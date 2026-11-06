/* <cadyam-viz> — embed a CadYam visualization in any page or slide.
 *
 *   <script src="cadyam-viz.js"></script>
 *   <cadyam-viz src="films.viz.html" state="loss-zone" aspect="16/10"></cadyam-viz>
 *
 * Attributes: src, state (animates when changed), theme (light|dark|auto),
 * aspect (w/h; or size the element with CSS). Methods: setState(id, {instant})
 * → Promise, setParams({name: value}), .states, .paramSpecs. Events
 * (bubbling): viz:ready {states, state, params}, viz:state {state, index},
 * and viz:<name> for whatever the module emits (e.g. viz:select). CSS: --viz-bg, --viz-font, --viz-ink, --viz-muted,
 * --viz-grid, --viz-accent, --viz-positive, --viz-negative and --viz-glow
 * (0..1) pass into the frame, so the chart wears the host page's theme.
 * Each visualization runs in its own frame, so any number can share a page.
 */
(function () {
  'use strict';
  if (window.customElements && customElements.get('cadyam-viz')) return;
  var NS = 'cadyam-viz';
  // The theme tokens a host page may set on (or above) the element; each
  // passes into the frame, where ctx.theme reads them.
  var TOKENS = ['--viz-bg', '--viz-font', '--viz-ink', '--viz-muted', '--viz-grid',
    '--viz-accent', '--viz-positive', '--viz-negative', '--viz-glow'];

  function CadyamViz() {
    return Reflect.construct(HTMLElement, [], CadyamViz);
  }
  CadyamViz.prototype = Object.create(HTMLElement.prototype);
  CadyamViz.prototype.constructor = CadyamViz;
  Object.setPrototypeOf(CadyamViz, HTMLElement);
  CadyamViz.observedAttributes = ['src', 'state', 'theme', 'aspect'];

  CadyamViz.prototype.connectedCallback = function () {
    var self = this;
    if (this._frame) return;
    this.style.display = this.style.display || 'block';
    this.style.position = this.style.position || 'relative';
    this._applyAspect();
    var f = this._frame = document.createElement('iframe');
    f.setAttribute('title', this.getAttribute('aria-label') || 'Visualization');
    f.setAttribute('loading', 'lazy');
    f.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;border:0;background:transparent';
    // A frame whose color-scheme differs from its element's is painted
    // opaque by the browser; matching them keeps the frame see-through.
    f.style.colorScheme = this._scheme();
    f.setAttribute('allowtransparency', 'true');
    this._ready = false;
    this._waiters = [];
    this._onMessage = function (e) {
      if (e.source !== f.contentWindow) return;
      var m = e.data;
      if (!m || m.ns !== NS) return;
      if (m.type === 'ready') {
        self._ready = true;
        self.states = m.states || [];
        self.paramSpecs = m.params || {};
        self._sendTheme();
        if (self._params) self._send({ type: 'params', values: self._params });
        var want = self.getAttribute('state');
        if (want && want !== m.state) self._send({ type: 'setState', state: want, instant: true });
        self.dispatchEvent(new CustomEvent('viz:ready', { bubbles: true, detail: { states: self.states, state: want || m.state } }));
      } else if (m.type === 'state') {
        self._state = m.state;
        self._waiters = self._waiters.filter(function (w) {
          if (w.state === m.state || w.state === m.index) { w.resolve(m); return false; }
          return true;
        });
        self.dispatchEvent(new CustomEvent('viz:state', { bubbles: true, detail: { state: m.state, index: m.index } }));
      } else if (m.type === 'event' && m.name) {
        self.dispatchEvent(new CustomEvent('viz:' + m.name, { bubbles: true, detail: m.detail }));
      }
    };
    window.addEventListener('message', this._onMessage);
    this._load();
    this.appendChild(f);
  };

  CadyamViz.prototype.disconnectedCallback = function () {
    window.removeEventListener('message', this._onMessage);
    if (this._frame) this._frame.remove();
    this._frame = null;
  };

  CadyamViz.prototype.attributeChangedCallback = function (name, old, val) {
    if (!this._frame || old === val) return;
    if (name === 'src') this._load();
    else if (name === 'state' && val && val !== this._state) this.setState(val);
    else if (name === 'theme') { this._frame.style.colorScheme = this._scheme(); this._sendTheme(); }
    else if (name === 'aspect') this._applyAspect();
  };

  CadyamViz.prototype._applyAspect = function () {
    var a = this.getAttribute('aspect');
    if (a && !this.style.height) this.style.aspectRatio = a.replace(':', '/');
  };

  CadyamViz.prototype._load = function () {
    var src = this.getAttribute('src') || '';
    var hash = [];
    if (this.getAttribute('state')) hash.push('state=' + encodeURIComponent(this.getAttribute('state')));
    hash.push('mode=' + encodeURIComponent(this._mode()));
    this._ready = false;
    this._frame.src = src + '#' + hash.join('&');
  };

  CadyamViz.prototype._mode = function () {
    var t = this.getAttribute('theme');
    return t === 'light' || t === 'dark' ? t : 'auto';
  };

  CadyamViz.prototype._scheme = function () {
    var m = this._mode();
    return m === 'auto' ? 'light dark' : m;
  };

  CadyamViz.prototype._send = function (m) {
    m.ns = NS;
    if (this._frame && this._frame.contentWindow) this._frame.contentWindow.postMessage(m, '*');
  };

  CadyamViz.prototype._sendTheme = function () {
    var cs = getComputedStyle(this), vars = {};
    TOKENS.forEach(function (k) {
      var v = cs.getPropertyValue(k).trim();
      if (v) vars[k] = v;
    });
    // Web fonts the page loaded don't reach into the frame on their own:
    // send the stylesheets (Google Fonts links, @font-face sheets) along.
    var fonts = [];
    document.querySelectorAll('link[rel="stylesheet"]').forEach(function (l) {
      if (/font/i.test(l.href)) fonts.push(l.href);
    });
    this._send({ type: 'theme', mode: this._mode(), vars: vars, fonts: fonts });
  };

  CadyamViz.prototype.setState = function (state, opts) {
    var self = this;
    return new Promise(function (resolve) {
      if (state === self._state) return resolve({ state: state });
      self._waiters.push({ state: state, resolve: resolve });
      var go = function () { self._send({ type: 'setState', state: state, instant: !!(opts && opts.instant) }); };
      if (self._ready) go();
      else self.addEventListener('viz:ready', go, { once: true });
    });
  };

  // Set the module's params (any subset): {year: 2024, minMag: 6}. Values
  // set before the frame is ready are sent when it is.
  CadyamViz.prototype.setParams = function (values) {
    this._params = Object.assign(this._params || {}, values || {});
    if (this._ready) this._send({ type: 'params', values: values || {} });
  };

  Object.defineProperty(CadyamViz.prototype, 'state', {
    get: function () { return this._state; },
  });

  customElements.define('cadyam-viz', CadyamViz);
})();

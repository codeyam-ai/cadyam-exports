#!/usr/bin/env python3
"""Generate thumbnails and rebuild index.html for all CadYam HTML exports in the repo root."""

import hashlib
import html
import json
import os
import re
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THUMB_DIR = ROOT / "thumbnails"
ASSETS_DIR = ROOT / "assets"
SITE_BASE_URL = os.environ.get(
    "CADYAM_EXPORTS_BASE_URL", "https://codeyam-ai.github.io/cadyam-exports"
).rstrip("/")
CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome",
    "chromium",
]


def find_chrome():
    for path in CHROME_PATHS:
        if os.path.exists(path):
            return path
    return None


def image_dimensions(path: Path) -> tuple[int, int]:
    try:
        header = path.read_bytes()[:24]
        if len(header) >= 24 and header[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", header[16:24])
            return int(w), int(h)
    except OSError:
        pass
    return 1600, 840


def short_file_hash(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()[:8]
    except OSError:
        return "1"


def extract_metadata(export_path: Path):
    content = export_path.read_text(encoding="utf-8", errors="replace")
    title_match = re.search(r"<title>(.*?)</title>", content, re.S)
    byline_match = re.search(r'<p class="byline">(.*?)</p>', content, re.S)
    title = html.unescape(title_match.group(1).strip()) if title_match else export_path.stem.replace("-", " ").title()
    raw_byline = re.sub(r"<button\b.*?</button>", "", byline_match.group(1), flags=re.S) if byline_match else "CadYam Export"
    byline = html.unescape(raw_byline.strip())
    if byline.startswith("CadYam · "):
        byline = byline[len("CadYam · "):]
    return title, byline


def build_social_meta(
    title: str,
    description: str,
    page_url: str,
    image_url: str,
    image_mime: str = "image/jpeg",
    width: int = 1600,
    height: int = 840,
) -> str:
    esc_title = html.escape(title, quote=True)
    esc_desc = html.escape(description, quote=True)
    esc_page = html.escape(page_url, quote=True)
    esc_img = html.escape(image_url, quote=True)
    return "\n".join(
        [
            "<!-- cadyam-social-meta:start -->",
            f'<meta name="description" content="{esc_desc}">',
            '<meta property="og:type" content="website">',
            '<meta property="og:site_name" content="CadYam Exports">',
            f'<meta property="og:title" content="{esc_title}">',
            f'<meta property="og:description" content="{esc_desc}">',
            f'<meta property="og:url" content="{esc_page}">',
            f'<meta property="og:image" content="{esc_img}">',
            f'<meta property="og:image:secure_url" content="{esc_img}">',
            f'<meta property="og:image:type" content="{image_mime}">',
            f'<meta property="og:image:width" content="{width}">',
            f'<meta property="og:image:height" content="{height}">',
            f'<meta property="og:image:alt" content="{esc_title} — 3D model preview">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{esc_title}">',
            f'<meta name="twitter:description" content="{esc_desc}">',
            f'<meta name="twitter:image" content="{esc_img}">',
            f'<meta name="twitter:image:alt" content="{esc_title} — 3D model preview">',
            "<!-- cadyam-social-meta:end -->",
        ]
    )


def externalize_heavy_payload(export_path: Path, content: str) -> str:
    """Move multi-megabyte inline #plan-view SVG and #drawing JSON into assets/<slug>-data.js.

    Keeping each HTML file ~85 KB ensures iMessage (LPMetadataProvider), Slack,
    Discord, and X/Twitter never abort metadata fetching due to their ~1 MB HTML
    response size limits, while a synchronous <script src="assets/<slug>-data.js">
    restores #plan-view and #drawing before the viewer script executes.
    """
    m_plan = re.search(
        r'(<div id="plan-view">)(<svg\b.*?</svg>\s*)(</div>\s*</section>)',
        content,
        re.S,
    )
    m_json = re.search(
        r'<script type="application/json" id="drawing">(.*?)</script>',
        content,
        re.S,
    )
    if not m_plan or not m_json:
        ASSETS_DIR.mkdir(exist_ok=True)
        root_data = ROOT / f"{export_path.stem}-data.js"
        asset_rel = f"assets/{export_path.stem}-data.js"
        asset_path = ROOT / asset_rel
        m_story = re.search(
            r'<script type="application/json" id="story-data">(.*?)</script>',
            content,
            re.S,
        )
        if m_story and len(m_story.group(1)) > 20_000:
            story_json = m_story.group(1).strip()
            asset_path.write_text(
                f"window.__VIZKIT_STORY__ = {story_json};\n", encoding="utf-8"
            )
            data_ver = short_file_hash(asset_path)
            content = (
                content[: m_story.start()]
                + f'<script src="{asset_rel}?v={data_ver}"></script>'
                + content[m_story.end() :]
            )
            return content
        if root_data.exists():
            shutil.move(str(root_data), str(asset_path))
        if asset_path.exists():
            data_ver = short_file_hash(asset_path)
            content = re.sub(
                rf'<script src="(?:assets/)?{re.escape(export_path.stem)}-data\.js(?:\?v=[^"]*)?"></script>',
                f'<script src="{asset_rel}?v={data_ver}"></script>',
                content,
            )
        return content

    svg_markup = m_plan.group(2)
    drawing_json = m_json.group(1).strip()
    if len(svg_markup) + len(drawing_json) < 20_000:
        return content

    ASSETS_DIR.mkdir(exist_ok=True)
    asset_rel = f"assets/{export_path.stem}-data.js"
    asset_path = ROOT / asset_rel
    js_payload = (
        "// Auto-extracted by scripts/update-exports.py so HTML stays lightweight for social/iMessage link previews.\n"
        "(function(){\n"
        "  var planHost = document.getElementById('plan-view');\n"
        "  if (planHost) planHost.innerHTML = " + json.dumps(svg_markup) + ";\n"
        "  var drawingEl = document.getElementById('drawing');\n"
        "  if (drawingEl) drawingEl.textContent = " + json.dumps(drawing_json) + ";\n"
        "})();\n"
    )
    asset_path.write_text(js_payload, encoding="utf-8")

    loader_tag = f'<script src="{asset_rel}"></script>'
    updated = (
        content[: m_plan.start(2)]
        + content[m_plan.end(2) : m_json.start(1)]
        + "{}"
        + content[m_json.end(1) :]
    )
    if loader_tag not in updated:
        updated = updated.replace(
            '<script type="application/json" id="drawing">{}</script>',
            '<script type="application/json" id="drawing">{}</script>\n' + loader_tag,
            1,
        )
    return updated


def upgrade_export_html(
    export_path: Path,
    title: str,
    byline: str,
    social_thumb_rel: str,
    image_mime: str,
    width: int,
    height: int,
):
    """Ensure the exported HTML opens in 3D mode by default, externalizes multi-MB data, and includes OG/Twitter meta tags."""
    content = export_path.read_text(encoding="utf-8", errors="replace")
    original = content

    # 1. Switch to 3D mode by default after 2D getBBox() + scaleLabels() initialization
    #    so opening the page starts in 3D view while preserving 2D framing when switching modes.
    default_3d_tail = '  inspect(null);\n  scaleLabels();\n  if (data.scene) setMode("3d");\n})();'
    if 'if (data.scene) setMode("3d");' not in content:
        content = content.replace(
            "  inspect(null);\n  scaleLabels();\n})();",
            default_3d_tail,
            1,
        )

    # 2. Externalize multi-megabyte inline #plan-view SVG and #drawing JSON into assets/<slug>-data.js
    #    so the HTML document is ~85 KB and unfurls reliably in iMessage & social media crawlers.
    content = externalize_heavy_payload(export_path, content)

    # 3. Inject or update Open Graph & Twitter Card meta tags in <head>.
    page_url = f"{SITE_BASE_URL}/{export_path.name}"
    image_url = f"{SITE_BASE_URL}/{social_thumb_rel}"
    description = f"Interactive 3D model & 2D plan — {byline}"
    meta_block = build_social_meta(
        title, description, page_url, image_url, image_mime, width, height
    )

    meta_pattern = re.compile(
        r"<!-- cadyam-social-meta:start -->.*?<!-- cadyam-social-meta:end -->",
        re.S,
    )
    if meta_pattern.search(content):
        content = meta_pattern.sub(meta_block, content, count=1)
    else:
        content = re.sub(
            r"(<title>.*?</title>)(?:\s*<meta\s+(?:name=\"(?:description|twitter:[^\"]*)\"|property=\"og:[^\"]*\")[^>]*>)*",
            r"\1\n" + meta_block,
            content,
            count=1,
            flags=re.S,
        )

    if content != original:
        export_path.write_text(content, encoding="utf-8")


def ensure_thumbnail(export_path: Path) -> str:
    THUMB_DIR.mkdir(exist_ok=True)
    thumb_rel = f"thumbnails/{export_path.stem}.png"
    thumb_path = ROOT / thumb_rel
    root_png = ROOT / f"{export_path.stem}.png"
    if root_png.exists() and not thumb_path.exists():
        shutil.move(str(root_png), str(thumb_path))
    if thumb_path.exists():
        jpg_path = ROOT / f"thumbnails/{export_path.stem}.jpg"
        if not jpg_path.exists() or thumb_path.stat().st_mtime > jpg_path.stat().st_mtime:
            subprocess.run(
                [
                    "sips",
                    "-s",
                    "format",
                    "jpeg",
                    "-s",
                    "formatOptions",
                    "88",
                    str(thumb_path),
                    "--out",
                    str(jpg_path),
                ],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        return thumb_rel

    chrome = find_chrome()
    if not chrome:
        return ""

    raw_html = export_path.read_text(encoding="utf-8", errors="replace")
    is_vizkit = 'content="CadYam vizkit"' in raw_html
    if is_vizkit:
        clean_html = raw_html
    else:
        clean_html = raw_html.replace(
            "</style>",
            "header, .tools, .zoom-controls, #inspector, #model-pins { display: none !important; }\n</style>",
            1,
        )
    clean_html = clean_html.replace(
        "<head>",
        f'<head>\n<base href="file://{ROOT}/">',
        1,
    )
    tmp_dir = tempfile.mkdtemp(prefix="cadyam-thumb-")
    tmp_path = os.path.join(tmp_dir, "export.html")
    with open(tmp_path, "w", encoding="utf-8") as tmp:
        tmp.write(clean_html)

    try:
        subprocess.run(
            [
                chrome,
                "--headless=new",
                f"--user-data-dir={os.path.join(tmp_dir, 'profile')}",
                "--window-size=1600,840" if is_vizkit else "--window-size=1920,1200",
                "--virtual-time-budget=3500",
                f"--screenshot={thumb_path}",
                f"file://{tmp_path}",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if thumb_path.exists():
            jpg_path = ROOT / f"thumbnails/{export_path.stem}.jpg"
            subprocess.run(
                [
                    "sips",
                    "-s",
                    "format",
                    "jpeg",
                    "-s",
                    "formatOptions",
                    "88",
                    str(thumb_path),
                    "--out",
                    str(jpg_path),
                ],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return thumb_rel


def build_index():
    exports = sorted(
        p for p in ROOT.glob("*.html") if p.name != "index.html"
    )
    items_html = []
    first_social_thumb = "thumbnails/farm-house.jpg"
    first_social_mime = "image/jpeg"
    first_dims = (1600, 840)
    for idx, exp in enumerate(exports):
        title, byline = extract_metadata(exp)
        png_rel = ensure_thumbnail(exp) or f"thumbnails/{exp.stem}.png"
        jpg_rel = f"thumbnails/{exp.stem}.jpg"
        w, h = image_dimensions(ROOT / png_rel)
        if (ROOT / jpg_rel).exists():
            ver = short_file_hash(ROOT / jpg_rel)
            social_thumb_rel = f"{jpg_rel}?v={ver}"
            social_mime = "image/jpeg"
            card_thumb_rel = f"{jpg_rel}?v={ver}"
        else:
            ver = short_file_hash(ROOT / png_rel)
            social_thumb_rel = f"{png_rel}?v={ver}"
            social_mime = "image/png"
            card_thumb_rel = f"{png_rel}?v={ver}"
        upgrade_export_html(exp, title, byline, social_thumb_rel, social_mime, w, h)
        if idx == 0:
            first_social_thumb = social_thumb_rel
            first_social_mime = social_mime
            first_dims = (w, h)
        thumb_markup = (
            f'<div class="export-thumb"><img src="{html.escape(card_thumb_rel)}" alt="{html.escape(title)} preview" loading="lazy"></div>'
            if (ROOT / png_rel).exists() or (ROOT / jpg_rel).exists()
            else ""
        )
        items_html.append(
            f"""    <li class="export-item">
      <a href="{html.escape(exp.name)}">
        {thumb_markup}
        <div class="export-body">
          <div class="export-info">
            <h3 class="export-title">{html.escape(title)}</h3>
            <p class="export-meta">{html.escape(byline)}</p>
          </div>
          <span class="export-action">Open export &rarr;</span>
        </div>
      </a>
    </li>"""
        )

    index_meta = build_social_meta(
        "CadYam Exports",
        "Interactive 3D models & 2D plans exported from CadYam",
        f"{SITE_BASE_URL}/",
        f"{SITE_BASE_URL}/{first_social_thumb}",
        first_social_mime,
        first_dims[0],
        first_dims[1],
    )

    index_content = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="CadYam">
<title>CadYam Exports</title>
{index_meta}
<style>
:root {{
  --ink: #1d1d1f;
  --muted: #6b6b76;
  --line: #e4e4ea;
  --line-strong: #cfcfd8;
  --accent: #1473e6;
  --accent-soft: #e8f1fc;
  --pick: #e8892b;
  --page: #f4f4f7;
  --panel: #fff;
  --canvas: #eaf0f6;
}}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; min-height: 100%; }}
body {{
  font: 14px/1.45 "Source Sans 3", "Source Sans Pro", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  color: var(--ink);
  background: var(--page);
  display: flex;
  flex-direction: column;
}}
header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 24px;
  background: var(--panel);
  border-bottom: 1px solid var(--line);
}}
.brand h1 {{
  font-size: 17px;
  font-weight: 600;
  margin: 0;
}}
.brand .byline {{
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--muted);
}}
main {{
  width: 100%;
  max-width: 960px;
  margin: 0 auto;
  padding: 32px 24px 64px;
  flex: 1;
}}
.section-header {{
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 14px;
}}
.section-header h2 {{
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--muted);
  margin: 0;
}}
.export-list {{
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 20px;
}}
.export-item a {{
  display: flex;
  flex-direction: column;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 12px;
  overflow: hidden;
  color: var(--ink);
  text-decoration: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease;
}}
.export-item a:hover,
.export-item a:focus-visible {{
  border-color: var(--accent);
  box-shadow: 0 8px 24px rgba(20, 115, 230, 0.12);
  transform: translateY(-1px);
  outline: none;
}}
.export-thumb {{
  width: 100%;
  aspect-ratio: 16 / 9;
  background: var(--canvas);
  border-bottom: 1px solid var(--line);
  overflow: hidden;
}}
.export-thumb img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}}
.export-body {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 20px;
}}
.export-info {{
  min-width: 0;
}}
.export-title {{
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px;
  color: var(--ink);
}}
.export-meta {{
  margin: 0;
  font-size: 13px;
  color: var(--muted);
}}
.export-action {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--accent);
  background: var(--accent-soft);
  padding: 6px 12px;
  border-radius: 6px;
  white-space: nowrap;
}}
.export-item a:hover .export-action {{
  background: var(--accent);
  color: #fff;
}}
@media (max-width: 520px) {{
  .export-list {{
    grid-template-columns: 1fr;
  }}
}}
</style>
</head>
<body>
<header>
  <div class="brand">
    <h1>CadYam Exports</h1>
    <p class="byline">Interactive 2D plans &amp; 3D models exported from CadYam</p>
  </div>
</header>
<main>
  <div class="section-header">
    <h2>Exports</h2>
  </div>
  <ul class="export-list">
{chr(10).join(items_html)}
  </ul>
</main>
</body>
</html>
"""
    (ROOT / "index.html").write_text(index_content, encoding="utf-8")


if __name__ == "__main__":
    build_index()

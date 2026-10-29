#!/usr/bin/env python3
"""Generate thumbnails and rebuild index.html for all CadYam HTML exports in the repo root."""

import html
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THUMB_DIR = ROOT / "thumbnails"
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


def extract_metadata(export_path: Path):
    content = export_path.read_text(encoding="utf-8", errors="replace")
    title_match = re.search(r"<title>(.*?)</title>", content, re.S)
    byline_match = re.search(r'<p class="byline">(.*?)</p>', content, re.S)
    title = html.unescape(title_match.group(1).strip()) if title_match else export_path.stem.replace("-", " ").title()
    byline = html.unescape(byline_match.group(1).strip()) if byline_match else "CadYam Export"
    if byline.startswith("CadYam · "):
        byline = byline[len("CadYam · "):]
    return title, byline


def ensure_thumbnail(export_path: Path) -> str:
    THUMB_DIR.mkdir(exist_ok=True)
    thumb_rel = f"thumbnails/{export_path.stem}.png"
    thumb_path = ROOT / thumb_rel
    if thumb_path.exists() and thumb_path.stat().st_mtime >= export_path.stat().st_mtime:
        return thumb_rel

    chrome = find_chrome()
    if not chrome:
        return thumb_rel if thumb_path.exists() else ""

    raw_html = export_path.read_text(encoding="utf-8", errors="replace")
    clean_html = raw_html.replace(
        "</style>",
        "header, .tools, #plan-view text { display: none !important; }\n</style>",
        1,
    )
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp:
        tmp.write(clean_html)
        tmp_path = tmp.name

    try:
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--window-size=1200,675",
                f"--screenshot={thumb_path}",
                f"file://{tmp_path}",
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return thumb_rel


def build_index():
    exports = sorted(
        p for p in ROOT.glob("*.html") if p.name != "index.html"
    )
    items_html = []
    for exp in exports:
        title, byline = extract_metadata(exp)
        thumb_rel = ensure_thumbnail(exp)
        thumb_markup = (
            f'<div class="export-thumb"><img src="{html.escape(thumb_rel)}" alt="{html.escape(title)} preview" loading="lazy"></div>'
            if thumb_rel
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

    index_content = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="CadYam">
<title>CadYam Exports</title>
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

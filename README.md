# CadYam Exports

Static site hosting interactive 2D + 3D HTML drawings exported from CadYam.

## Exports

- **[Farm House](farm-house.html)** — Landscape & Garden (Exported 29 October 2026)

## Adding a New Export

1. Copy the exported `.html` file into the repository root.
2. Run `python3 scripts/update-exports.py` to automatically render its 2D + 3D thumbnail into `thumbnails/` and update `index.html`.
3. Commit and push to `main`.

# CadYam Exports

Static site hosting interactive 2D + 3D HTML drawings exported from CadYam.

## Exports

- **[The 2.5× Rule](film-article.html)** — Data Stories (Exported 6 November 2026)
- **[Hillside Vineyard & Winery Estate](hillside-vineyard-estate.html)** — Landscape & Garden (Exported 5 November 2026)
- **[The Restless Year](quake-explorer.html)** — Data Stories (Exported 6 November 2026)
- **[Couture Botanical Evening Gown](couture-evening-gown.html)** — Fashion (Exported 5 November 2026)
- **[Twenty-Five Years of New Vaccines](vaccines-deck.html)** — Data Stories (Exported 6 November 2026)
- **[Farm House](farm-house.html)** — Landscape & Garden (Exported 5 November 2026)
- **[Chicago After Dark · Who Takes a Taxi](chicago-dashboard.html)** — Data Stories (Exported 6 November 2026)
- **[Heirloom Walnut & White Oak Craftsman Sideboard](heirloom-craftsman-sideboard.html)** — Woodworking & Furniture (Exported 5 November 2026)
- **[The Height Limit of Trees](trees-exhibit.html)** — Data Stories (Exported 6 November 2026)
- **[Luxury House Pond](luxuryhousepond.html)** — Landscape & Garden (Exported 5 November 2026)
- **[Grand Courtyard Residence & Loft Renovation](architectural-loft-renovation.html)** — Interior & Architecture (Exported 5 November 2026)
- **[Floral Dress](floral-dress.html)** — Fashion (Exported 5 November 2026)
- **[Twelve Junes of Bike Share](bikes-deck.html)** — Data Stories (Exported 6 November 2026)
- **[Town Center](town-center.html)** — Landscape & Garden (Exported 5 November 2026)
- **[The American Macro-Economy in 3D & Motion](american-economy-story.html)** — Data Stories (Exported 5 November 2026)

## Adding a New Export

1. Copy the exported `.html` file into the repository root.
2. Run `python3 scripts/update-exports.py` to automatically render its 2D + 3D thumbnail into `thumbnails/` and update `index.html`.
3. Commit and push to `main`.

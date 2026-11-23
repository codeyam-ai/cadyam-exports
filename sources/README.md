# Sources

The editable originals behind the gallery's examples, so any page can be
reopened in CadYam, improved and re-exported.

- **`.cadyam`** files open directly in CadYam (File › Open).
- **`gen_*.py`** scripts write a `.cadyam` file of CadYam command lines:
  `python3 gen_bookcase.py out.cadyam`. Most take an optional second
  argument (a species or material). Open the result in the app the script
  names, or run its lines through the command line.
- **`.txt`** files are command lines to run in order in a fresh drawing of
  the app they name.

| Page | Source |
|---|---|
| brass-zephyr-airship.html | `brass-zephyr-airship/` (drawing + generator) |
| aurora-bridal-set.html, aurora-pendant.html | `aurora/` (drawing + ring and necklace generators) |
| gull-rock-lighthouse.html | `gull-rock-lighthouse/` |
| loon-lake-cabin.html | `loon-lake-cabin/` (drawing; paintings in `art/`) |
| willow-creek-farm.html | `willow-creek-farm/` |
| walnut-bookcase.html | `walnut-bookcase/` |
| shaker-rocking-chair.html | `shaker-rocking-chair/gen_chair.py` (Woodworking) |
| staunton-chess-set.html | `staunton-chess-set/gen_chess.py` |
| shorai-an-tea-garden.html | `shorai-an-tea-garden/gen_tea.py` (Landscape) |
| meridian-pocket-watch.html | `meridian-pocket-watch/gen_watch.py` |
| camel-overcoat.html, tweed-sport-coat.html | `menswear/*.txt` (Fashion command lines) |
| architectural-loft-renovation.html (Grand Courtyard Residence) | `grand-courtyard-residence/` (drawing, generator, paintings in `art/`) |
| pecking-bird-automaton.html | `laser-automaton/` (assembled drawing; `gen_auto.py` writes the flat kit) |

Pages not listed here (the dresses and suit, the data stories and decks,
the vineyard, town centre, pond house, sideboard and coffee table) were made
before sources were kept. Their pages hold what they show, but not an
editable drawing.

## Art

The Loon Lake Cabin paintings in `loon-lake-cabin/art/` are public-domain
works from the Art Institute of Chicago (CC0): Winslow Homer, *North Woods
Club, Adirondacks* and *The Herring Net*; Vincent van Gogh, *The Bedroom*;
Pierre-Auguste Renoir, *Near the Lake*; Camille Corot, *Souvenir of the
Environs of Lake Nemi*; Henri-Joseph Harpignies, *Birches and Oaks*;
Utagawa Hiroshige, *Mishima: Morning Mist*.

The Grand Courtyard Residence paintings in `grand-courtyard-residence/art/`
are public-domain works from the Art Institute of Chicago (CC0): Claude
Monet, *Water Lilies*; Georges Seurat, *A Sunday on La Grande Jatte — 1884*;
Katsushika Hokusai, *Under the Wave off Kanagawa*; Utagawa Hiroshige,
*Hamamatsu* and *Arai* (Fifty-three Stations of the Tokaido); Mary Cassatt,
*The Child's Bath*; Gustave Caillebotte, *Paris Street; Rainy Day*; Vincent
van Gogh, *Self-Portrait*.

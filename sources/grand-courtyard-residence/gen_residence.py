#!/usr/bin/env python3
"""Grand Courtyard Residence: a furnished single-level house for CadYam
Interior Design, with public-domain paintings from the Art Institute of
Chicago on its walls.

Seven rooms on a 64' x 40' plan: a gallery foyer, a sunken living salon opened
to the kitchen through a wide cased opening framed by two brass columns, a
chef's kitchen, a dining conservatory, a glass courtyard atrium, a primary
bedroom and its bath.

Usage: python3 gen_residence.py out.cadyam [art-folder]
The art folder holds the paintings (default: ./art beside this script); their
paths are written into the picture lines, so run it where CadYam can read them.
Writes CadYam command lines, one per line.
"""
import os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "residence.cadyam"
ART = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "art"))
C = []


def add(*lines):
    C.extend(lines)


def art(where, name, big=False):
    kind = "large framed art" if big else "framed art"
    add(f'place {kind} {where} picture "{os.path.join(ART, name + ".jpg")}"')


add("units imperial")

# --- Shell: perimeter and the walls between rooms -------------------------
add("wall 0,0 64',0 64',40' 0,40' 0,0")
add("wall 14',0 14',20'")            # foyer | salon
add("wall 36',0 36',20'")            # salon | kitchen (the old load-bearing wall)
add("wall 0,20' 64',20'")            # front rooms | back rooms
add("wall 22',20' 22',40'")          # bedroom + bath | atrium
add("wall 0,32' 22',32'")            # bedroom | bath
add("wall 36',20' 36',40'")          # atrium | dining

# --- Openings, doors and windows ------------------------------------------
add("door 7',0 42\"")                       # front door
add("opening 14',10' 72\"")                 # foyer to salon
add("opening 36',10' 120\"")                # salon to kitchen: the opened-up wall
add("door 7',20'")                          # foyer to bedroom
add("opening 29',20' 96\"")                 # salon to atrium
add("opening 50',20' 96\"")                 # kitchen to dining
add("door 11',32'")                         # bedroom to bath
add("opening 36',30' 96\"")                 # atrium to dining
for x in (20, 30):
    add(f"window {x}',0 72\"")              # salon, south
for x in (44, 56):
    add(f"window {x}',0 48\"")              # kitchen, south
for y in (10, 30):
    add(f"window 64',{y}' 60\"")            # east
for x in (44, 56):
    add(f"window {x}',40' 72\"")            # dining conservatory, north
add("window 29',40' 120\"")                 # atrium glass wall
add("window 0,26' 60\"")                    # bedroom, west
add("window 11',40' 36\"")                  # bath, north
add("window 0,8' 36\"")                     # foyer, west

# --- Rooms ----------------------------------------------------------------
for pt, name in (("7',10'", "Gallery Foyer"), ("25',10'", "Sunken Living Salon"),
                 ("50',10'", "Chef Kitchen"), ("50',30'", "Dining Conservatory"),
                 ("29',30'", "Glass Courtyard Atrium"), ("11',26'", "Primary Bedroom"),
                 ("11',36'", "Primary Bath")):
    add(f"room {pt}", f"set last name {name}")

# --- Finishes -------------------------------------------------------------
add("finish floor oak everywhere",
    "finish floor marble in Gallery Foyer",
    "finish floor stone in Glass Courtyard Atrium",
    "finish floor white tile in Primary Bath",
    "finish walls ivory everywhere",
    "finish walls sage in Dining Conservatory",
    "finish walls navy in Primary Bedroom")

# --- Gallery Foyer: a console, a bench and a wall of Hiroshige prints ------
add("place console table in Gallery Foyer against east wall",
    "place bench in Gallery Foyer against west wall",
    "place olive tree 12',2'")
art("in Gallery Foyer on north wall", "hiroshige-hamamatsu")
art("above console table", "hokusai-great-wave", big=True)
art("in Gallery Foyer on west wall", "hiroshige-arai")

# --- Sunken Living Salon ---------------------------------------------------
add("place sectional with left chaise in Sunken Living Salon near 27',10' facing west",
    "place coffee table in Sunken Living Salon near 22',10'",
    "place rug in Sunken Living Salon centre",
    "place armchair in Sunken Living Salon near 19',4'",
    "place armchair in Sunken Living Salon near 31',4'",
    "place fireplace in Sunken Living Salon against west wall",
    "place floor lamp in Sunken Living Salon near 20',18'",
    "place side table in Sunken Living Salon near 34.5',2'",
    "place table lamp on side table",
    "place books on coffee table",
    "place olive tree 34',18'")
art("in Sunken Living Salon on north wall", "seurat-la-grande-jatte", big=True)
art("above fireplace", "monet-water-lilies", big=True)

# Twin brass columns where the load-bearing wall was opened up.
add('item define "brass column" 1\'x1\' height 8\'',
    "place brass column 36',4'6\"", "set last material brass shape cylinder",
    "place brass column 36',15'6\"", "set last material brass shape cylinder")

# --- Chef Kitchen ----------------------------------------------------------
add("place refrigerator in Chef Kitchen against east wall left",
    "place range in Chef Kitchen against south wall",
    "place kitchen sink in Chef Kitchen against south wall left",
    "place dishwasher in Chef Kitchen against south wall right",
    "place wall oven in Chef Kitchen against east wall right",
    "place island in Chef Kitchen centre",
    "place 3 bar stools around island",
    "place pantry in Chef Kitchen against north wall right")
for _ in range(4):
    add("place base cabinet in Chef Kitchen against south wall")
add("place base cabinet in Chef Kitchen against east wall",
    "place bowl on island")
art("in Chef Kitchen on north wall", "van-gogh-self-portrait")

# --- Dining Conservatory ---------------------------------------------------
add("place dining table in Dining Conservatory centre",
    "place dining chairs around dining table",
    "place sideboard in Dining Conservatory against east wall",
    "place chandelier 50',30'",
    "place olive tree 38',38'", "place olive tree 62',38'")
art("above sideboard", "caillebotte-paris-street-rainy-day", big=True)

# --- Glass Courtyard Atrium -------------------------------------------------
add("place round rug in Glass Courtyard Atrium centre",
    "place chaise lounge in Glass Courtyard Atrium near 25',27'",
    "place accent chair in Glass Courtyard Atrium near 32',30'",
    "place round coffee table in Glass Courtyard Atrium centre",
    "place olive tree 23',36'", "place olive tree 35',36'", "place olive tree 24',22'")

# --- Primary Bedroom ---------------------------------------------------------
add("place king bed in Primary Bedroom against east wall",
    "place nightstand in Primary Bedroom left of bed",
    "place nightstand in Primary Bedroom right of bed",
    "place table lamp on nightstand",
    "place dresser in Primary Bedroom against west wall",
    "place writing desk in Primary Bedroom against north wall",
    "place desk chair in Primary Bedroom at writing desk",
    "place rug in Primary Bedroom centre",
    "place floor lamp in Primary Bedroom near 3',22'")
art("above king bed", "cassatt-the-childs-bath", big=True)

# --- Primary Bath ------------------------------------------------------------
add("place bathtub in Primary Bath against north wall",
    "place double vanity in Primary Bath against west wall",
    "place shower in Primary Bath against east wall",
    "place toilet in Primary Bath against south wall left")

# --- Tour stops: each pin's Walk here stands a visitor in the room -------
for n, title, note, at in (
    (1, "Gallery Foyer", "Hokusai's Great Wave over the console, Hiroshige prints either side", "7',3',0"),
    (2, "Sunken Living Salon", "Seurat's La Grande Jatte and Monet's Water Lilies over the fireplace", "30',6',0"),
    (3, "The opened-up wall", "Twin brass columns where the load-bearing wall came out", "34',10',0"),
    (4, "Chef Kitchen", "Island seating for three; Van Gogh's self-portrait on the far wall", "50',14',0"),
    (5, "Dining Conservatory", "Caillebotte's Paris Street; Rainy Day above the sideboard", "40',30',0"),
    (6, "Primary Bedroom", "Mary Cassatt's The Child's Bath above the bed", "18',26',0")):
    add(f'pin {n} "{title}" at {at} note "{note}"')

with open(OUT, "w") as fh:
    fh.write("\n".join(C) + "\n")
print(f"wrote {OUT}: {len(C)} lines")

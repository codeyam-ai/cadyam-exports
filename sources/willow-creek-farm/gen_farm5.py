#!/usr/bin/env python3
"""Willow Creek Farm (estate edition): a large, lived-in working property for CadYam Landscape.

Feet; x east, y north, origin at the south-west corner of an 1100' x 760' property, with a
county road along the south edge. Organic shapes come from jittered outlines. Writes farm2.cadyam.
"""
import math, random, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "farm2.cadyam"
rnd = random.Random(19)
C = []


def ft(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return f"{s}'"


def pt(x, y):
    return f"{ft(x)},{ft(y)}"


def add(*lines):
    C.extend(l for l in lines if l)


def section(t):
    add(f"# === {t} ===")


def poly(pts):
    return " ".join(pt(x, y) for x, y in pts)


def blob(cx, cy, rx, ry, n=14, j=0.18, rot=0.0):
    """An organic closed outline: an ellipse with jittered radius."""
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        r = 1 + rnd.uniform(-j, j)
        x, y = rx * r * math.cos(a), ry * r * math.sin(a)
        c, s = math.cos(rot), math.sin(rot)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def wobble(pts, step=40, j=10):
    """A polygon with each edge broken into wavy segments."""
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        nx, ny = -(y1 - y0), x1 - x0
        L = math.hypot(nx, ny) or 1
        nx, ny = nx / L, ny / L
        for k in range(n):
            t = k / n
            d = rnd.uniform(-j, j) if k else 0
            out.append((x0 + (x1 - x0) * t + nx * d, y0 + (y1 - y0) * t + ny * d))
    return out


def track(pts, width, material, smooth=6):
    """A winding lane: the centre line through pts, smoothed, as a ribbon patio."""
    line = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        for k in range(smooth):
            t = k / smooth
            line.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    line.append(pts[-1])
    # Chaikin smoothing
    for _ in range(2):
        nl = [line[0]]
        for (a, b) in zip(line, line[1:]):
            nl += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        nl.append(line[-1])
        line = nl
    line = line[::2]
    left, right = [], []
    for i, (x, y) in enumerate(line):
        a, b = (line[i], line[i + 1]) if i + 1 < len(line) else (line[i - 1], line[i])
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L * width / 2, dx / L * width / 2
        left.append((x + nx, y + ny))
        right.append((x - nx, y - ny))
    add(f"patio {poly(left + right[::-1])} material {material}")
    return line


def trees(kinds, area, count, hmin, hmax, clear=()):
    xs = [p[0] for p in area]
    ys = [p[1] for p in area]
    placed = 0
    tries = 0
    while placed < count and tries < count * 20:
        tries += 1
        x, y = rnd.uniform(min(xs), max(xs)), rnd.uniform(min(ys), max(ys))
        if not inside(x, y, area) or any(math.hypot(x - cx, y - cy) < r for cx, cy, r in clear):
            continue
        add(f"place {rnd.choice(kinds)} {pt(x, y)} height {int(rnd.uniform(hmin, hmax))}'")
        placed += 1


def inside(x, y, poly_):
    c = False
    for (x0, y0), (x1, y1) in zip(poly_, poly_[1:] + poly_[:1]):
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            c = not c
    return c


def item(name, spec):
    add(f'item define "{name}" {spec}')


W, H = 1900, 760
add("app landscape", "units imperial")

section("Rolling ground: valley floor by the road, rising to wooded ridges")
add(f"grade {pt(0, 0)} +0' {pt(W, 0)} +3' {pt(W, H)} +34' {pt(0, H)} +28' close")
add(f"contour {pt(0, 300)} {pt(300, 340)} {pt(620, 300)} {pt(900, 360)} {pt(1300, 320)} {pt(1600, 380)} {pt(W, 340)} +12'")
add(f"contour {pt(0, 560)} {pt(260, 590)} {pt(560, 560)} {pt(840, 610)} {pt(1200, 600)} {pt(1500, 470)} {pt(1750, 590)} {pt(W, 570)} +22'")
add(f"grade {pt(1440, 500)} +38' {pt(1560, 540)} +40'")
add(f"grade {pt(160, 470)} +17' {pt(270, 520)} +21'")

section("County road along the south edge, with the farm stand")
add(f"patio {pt(0, 0)} {pt(W, 22)} material asphalt")
add(f"patio {pt(0, 10.5)} {pt(W, 11.5)} material #e8c547")
add("house 200',34' 222',48' storeys 1 height 9' siding #b5452e trim white roofing #e9e2cf pitch 5 overhang 3'")
item("Produce table", "8'x3' height 3' material cedar shape table")
for x in (196, 207, 218):
    add(f"place produce table {pt(x, 28)}")
item("Pumpkin", "1'6\"x1'6\" height 1'2\" material #e07a1f shape ellipsoid")
for _ in range(40):
    add(f"place pumpkin {pt(rnd.uniform(120, 185), rnd.uniform(34, 78))}")
item("Scarecrow post", "0'4\"x0'4\" height 6' material #8a6a44")
item("Scarecrow coat", "3'x1' height 2'6\" elevation 3'2\" material #5a6f3a shape ellipsoid")
item("Scarecrow hat", "1'8\"x1'8\" height 1'2\" elevation 6' material #c8a85a shape cone")
add(f"place scarecrow post {pt(152, 58)}", f"place scarecrow coat {pt(152, 58)}", f"place scarecrow hat {pt(152, 58)}")
add(f"place mailbox {pt(244, 26)}")

section("Main drive: a winding gravel lane from the road up to the farmyard")
drive = track([(250, 18), (270, 90), (330, 150), (360, 230), (420, 300), (470, 380), (500, 440)], 15, "gravel")
for k in range(4, len(drive) - 3, 6):
    x, y = drive[k]
    s = rnd.choice((1, -1))
    add(f"place red maple {pt(x + s * rnd.uniform(18, 26), y + rnd.uniform(-6, 6))} height {int(rnd.uniform(30, 44))}'")

section("Farm tracks: dirt lanes out to the cattle barn, the stable and the fields")
track([(500, 440), (600, 430), (720, 445), (820, 440)], 11, "dirt")
track([(470, 380), (380, 380), (320, 390)], 10, "dirt")
track([(360, 230), (420, 200), (560, 150), (700, 170), (860, 160), (980, 150)], 10, "dirt")
track([(330, 150), (220, 160), (120, 190)], 9, "dirt")

section("The farmyard: a big gravel apron between house, barn and sheds")
add(f"patio {poly(wobble([(470, 420), (640, 410), (650, 470), (480, 480)], 30, 5))} material gravel")

section("Farmhouse with a wraparound porch, a detached garage and a guest cottage")
add("house 480',490' 536',530' storeys 2 siding white trim #2f3b45 roofing #3d4650 chimney Stone pitch 9 overhang 1'6\"")
add("deck 474',482' 540',490' height 2'", "deck 536',490' 544',530' height 2'")
item("Porch roof", "70'x9' height 9' shape roof pitch 3/12 material #3d4650")
add(f"place porch roof {pt(507, 486)} elevation 9'")
add("house 440',470' 464',494' storeys 1 height 10' siding white trim #2f3b45 roofing #3d4650 pitch 7 garage_doors 2")
add("house 380',570' 408',592' storeys 1 height 10' siding #c9b28a trim white roofing #5b3a2a chimney Stone pitch 10")
add(f"place white oak {pt(468, 548)} height 62'", f"place white oak {pt(552, 552)} height 55'")
add(f"place swing set {pt(560, 520)}")
for x, y in ((476, 500), (476, 516), (500, 536), (520, 536)):
    add(f"place hydrangea {pt(x, y)}")

section("Kitchen garden and a glass greenhouse")
# Chickens in a picket run between the garage and the guest cottage, on
# their own random stream so every later placement stays where the audit
# left it.
import random as _r
hen = _r.Random(41)
add("fence 392',516' 428',516' 428',544' 392',544' close style picket height 3'")
for k in range(9):
    add(f"place chicken {pt(hen.uniform(396, 424), hen.uniform(520, 540))} facing {hen.randint(0, 359)}")
for i in range(4):
    for j in range(2):
        add(f"place raised bed {pt(560 + i * 11, 570 + j * 15)}", f"place tomato {pt(558 + i * 11, 570 + j * 15)}")
add("fence 550',560' 600',560' 600',596' 550',596' close style picket height 3'6\"")
item("Greenhouse", "30'x14' height 8' material glass shape block")
item("Greenhouse roof", "30'x14' height 4' elevation 8' material glass shape roof pitch 8/12")
add(f"place greenhouse {pt(630, 580)}", f"place greenhouse roof {pt(630, 580)}")

section("The treehouse: a great oak with a cabin, red roof and rope ladder")
add(f"place white oak {pt(330, 620)} height 70'")
item("Treehouse deck", "16'x13' height 1' elevation 18' material cedar shape slab")
item("Treehouse cabin", "9'x8' height 7' elevation 19' material #8a5a3c shape block")
item("Treehouse roof", "11'x10' height 1' elevation 26' material #b33a2a shape roof pitch 10/12")
add(f"place treehouse deck {pt(330, 614)}", f"place treehouse cabin {pt(328, 616)}", f"place treehouse roof {pt(328, 616)}")
item("Ladder rail", "0'3\"x0'3\" material #c8a87a shape beam")
add(f"place ladder rail from {pt(316.5, 612.5)} to {pt(321.8, 612.5)} rise 19'", f"place ladder rail from {pt(316.5, 615)} to {pt(321.8, 615)} rise 19'")
for k in range(1, 18):
    z = k * 1.05
    item(f"Ladder rung {k}", f"0'3\"x2'6\" height 0'2\" elevation {z:.2f}' material #c8a87a")
    add(f"place ladder rung {k} {pt(316.5 + 5.3 * z / 19, 613.75)}")
item("Swing rope", "0'2\"x0'2\" height 16' elevation 3'6\" material #c9b48a")
item("Tire swing", "3'x3' round height 0'10\" elevation 2' material #1d1d1d shape cylinder roll 90")
add(f"place swing rope {pt(346, 600)}", f"place tire swing {pt(346, 600)}")

section("Working yard: red bank barn, twin silos, machine shed and three grain bins")
add(f"place bank barn {pt(636, 483)} size 72'x46'")
for y in (472, 494):
    add(f"place concrete silo {pt(686, y)}")
add("house 560',380' 630',412' storeys 1 height 18' siding #9aa0a6 trim white roofing #8f979e pitch 3 garage_doors 3 garage_door_width 12' garage_door_height 12'")
for x in (660, 688, 716):
    add(f"place grain bin {pt(x, 392)}")

section("Cattle barn, feedlot and the big east pasture with a windmill")
add(f"place pole barn {pt(830, 468)} size 60'x36'")
add("fence 798',452' 762',452' 762',482' 798',482' style \"split rail\" height 4'6\"")
past = wobble([(760, 500), (1080, 470), (1086, 650), (900, 690), (760, 640)], 50, 14)
add(f"fence {poly(past)} close style \"split rail\" height 4'")
for k in range(22):
    for _ in range(30):
        x, y = rnd.uniform(770, 1070), rnd.uniform(480, 680)
        if inside(x, y, past):
            add(f"place cow {pt(x, y)} facing {rnd.randint(0, 359)}")
            break
for x, y in ((960, 600), (1010, 520), (850, 560)):
    add(f"place white oak {pt(x, y)} height {rnd.randint(48, 62)}'")
add(f"place windmill {pt(900, 640)}")
item("Water trough", "8'x3' height 2' material #8f979e shape tub")
add(f"place water trough {pt(905, 628)}")

section("Horse stable and a fenced riding arena")
add("house 260',380' 310',404' storeys 1 height 12' siding #e2d6bf trim #5b3a2a roofing #5b3a2a pitch 7 garage_doors 4 garage_door_width 6' garage_door_height 8'")
arena = blob(250, 300, 70, 38, 16, 0.04)
add(f"patio {poly(arena)} material #b49a6c")
add(f"fence {poly(arena)} close style \"split rail\" height 4'")
for x, y, f_ in ((230, 300, 40), (280, 290, 200)):
    add(f"place horse {pt(x, y)} facing {f_}")

section("Vineyard rows on the warm slope")
for k in range(16):
    x = 70 + k * 9
    add(f"bed {pt(x, 420)} {pt(x + 2.5, 540 + rnd.uniform(-8, 8))} mulch #3f6b2a edging None")
add(f"fence {pt(60, 412)} {pt(222, 412)} {pt(222, 552)} {pt(60, 552)} close style \"split rail\" height 3'6\"")

section("Old orchard with beehives along its edge")
for i in range(7):
    for j in range(5):
        if rnd.random() < 0.12:
            continue
        add(f"place dwarf apple {pt(70 + i * 24 + rnd.uniform(-4, 4), 590 + j * 22 + rnd.uniform(-4, 4))} height {int(rnd.uniform(9, 14))}'")
item("Beehive", "2'x2' height 3' material #f2efe6 shape block")
for k in range(5):
    add(f"place beehive {pt(240 + k * 5, 596)}")

section("Fields: wheat, corn and hay in irregular shapes, with round bales")
fields = [
    (wobble([(30, 40), (110, 100), (300, 200), (200, 260), (30, 250)], 40, 9), "#d9bb5f"),
    (wobble([(460, 40), (760, 34), (770, 140), (690, 160), (460, 140)], 40, 8), "#9cb558"),
    (wobble([(800, 40), (1080, 40), (1084, 330), (930, 360), (800, 290)], 45, 12), "#b8b25e"),
    (wobble([(520, 190), (720, 186), (740, 300), (600, 330), (520, 290)], 40, 8), "#6e4c2f"),
]
CROP = {"#d9bb5f": "Wheat", "#9cb558": "Corn", "#b8b25e": "Alfalfa", "#6e4c2f": "Ploughed"}
for outline, col in fields:
    add(f"field {poly(outline)} crop {CROP[col]}")
for _ in range(18):
    add(f"place round hay bale {pt(rnd.uniform(830, 1060), rnd.uniform(60, 300))} facing {rnd.randint(0, 179)}")

section("Willow Creek: a meandering creek into the big pond, with footbridges")
creek = [(1060, 740), (1010, 690), (940, 700), (870, 640), (760, 690), (700, 620), (722, 560), (748, 505), (752, 430), (742, 368), (650, 352), (600, 340), (560, 300), (470, 280)]
add("cut " + poly(creek) + " depth 2' width 9' profile round water")
add("cut " + poly([(390, 260), (360, 210), (380, 120), (330, 60), (300, 22)]) + " depth 2' width 8' profile round water")
pond = blob(420, 268, 62, 34, 18, 0.2, 0.3)
add(f"cut {poly(pond)} close depth 6' water")
isle = blob(428, 272, 13, 9, 10, 0.2)
add(f"level {poly(isle)} at +6'")
add(f"place paper birch {pt(428, 272)} height 32'")
add("cut " + poly(blob(980, 410, 28, 18, 12, 0.25)) + " close depth 4' water")
# Catalog footbridges laid square across the water, bank to bank (the third
# used to stand 24 ft beside the west brook; the warnings caught the decks
# floating with nothing under them).
for a, b in (((714.8, 554.1), (731.1, 561.8)), ((742.3, 443.6), (760.2, 444.5)), ((361.1, 163.4), (378.7, 167.3))):
    add(f"place footbridge from {pt(*a)} to {pt(*b)}")
item("Picnic table", "8'x5' height 2'6\" material cedar shape table")
add(f"place picnic table {pt(470, 230)}", f"place red oak {pt(480, 220)} height 52'")
add(f"deck 350',250' 372',258' height 1'")

section("The old shed and a rusting tractor at the hayfield's edge")
item("Old shed", "14'x10' height 9' material #6d5a48 shape block tilt 4")
item("Old shed roof", "16'x12' height 1' elevation 8'6\" material #7a3b2a shape roof pitch 6/12 tilt 5")
add(f"place old shed {pt(1040, 352)}", f"place old shed roof {pt(1040, 352)}")
add(f"place tractor {pt(1015, 340)} facing 200")

section("Stone walls, part tumbled, along old field boundaries")
for seg in (((30, 270), (140, 300), (260, 296)), ((780, 360), (790, 420)), ((640, 160), (780, 180))):
    add("gardenwall " + poly(seg) + " height 2'6\" thickness 2' material \"stone veneer\" cap none")

section("The east acreage: open hay meadows, a sunflower field, a sheep hill and the far woods")
# A dirt track runs on east from the fields, past the meadows, up to the hilltop oak.
track([(980, 150), (1120, 140), (1300, 170), (1480, 150), (1660, 190), (1800, 260)], 9, "dirt")
track([(1480, 150), (1470, 300), (1500, 430), (1490, 505)], 7, "dirt")
meadows = [
    (wobble([(1120, 40), (1440, 46), (1450, 130), (1300, 150), (1120, 120)], 45, 10), "#b9c46a", "#a5b257"),
    (wobble([(1130, 190), (1430, 180), (1440, 380), (1260, 400), (1140, 330)], 45, 12), "#c9b864", "#b5a350"),
    (wobble([(1530, 40), (1780, 50), (1790, 170), (1660, 200), (1530, 150)], 40, 9), "#e3c23a", "#6b5a2a"),
]
TURF = {"#b9c46a": "Hay", "#c9b864": "Meadow"}
for outline, col, row in meadows:
    if col in TURF:
        add(f"lawn {poly(outline)} turf {TURF[col]}")
    else:
        add(f"bed {poly(outline)} mulch {col} edging None")
for _ in range(26):
    add(f"place round hay bale {pt(rnd.uniform(1150, 1420), rnd.uniform(200, 360))} facing {rnd.randint(0, 179)}")
item("Sunflower stem", "0'2\"x0'2\" height 6' material #4f7a2a")
item("Sunflower head", "1'6\"x1'6\" round height 0'4\" elevation 6' material #f2b705 shape cylinder")
for _ in range(70):
    x, y = rnd.uniform(1545, 1775), rnd.uniform(60, 160)
    add(f"place sunflower stem {pt(x, y)}", f"place sunflower head {pt(x, y)}")
# Hedgerows of mixed trees between the meadows, gappy as old ones are.
for line in (((1100, 160), (1460, 165)), ((1470, 30), (1480, 400)), ((1520, 210), (1800, 230))):
    (x0, y0), (x1, y1) = line
    n = int(max(abs(x1 - x0), abs(y1 - y0)) / 26)
    for k in range(n):
        if rnd.random() < 0.3:
            continue
        t = k / max(n - 1, 1)
        add(f"place {rnd.choice(['red maple', 'black cherry', 'white oak', 'hydrangea'])} "
            f"{pt(x0 + (x1 - x0) * t + rnd.uniform(-5, 5), y0 + (y1 - y0) * t + rnd.uniform(-5, 5))} height {rnd.randint(14, 40)}'")

# Sheep on the hill behind a tumbled stone wall, with a little open shelter.
hill = wobble([(1150, 430), (1440, 420), (1460, 640), (1300, 680), (1160, 620)], 50, 14)
add("gardenwall " + poly(hill + hill[:1]) + " height 2'6\" thickness 2' material \"stone veneer\" cap none")
for k in range(34):
    for _ in range(30):
        x, y = rnd.uniform(1160, 1450), rnd.uniform(430, 670)
        if inside(x, y, hill):
            add(f"place sheep {pt(x, y)} facing {rnd.randint(0, 359)}")
            break
add("house 1330',600' 1354',614' storeys 1 height 8' siding #8a6a4a trim #5b3a2a roofing #5b3a2a pitch 4 overhang 2'")

# The hilltop: one great oak, a bench and a tire swing looking back over the farm.
add(f"place white oak {pt(1500, 520)} height 72'")
item("Hill bench", "6'x2' height 1'6\" material cedar shape slab")
add(f"place hill bench {pt(1488, 500)} facing 250")
add(f"place swing rope {pt(1512, 528)}", f"place tire swing {pt(1512, 528)}")

# A spring-fed pond in the east hollow, with willows and a rowboat.
epond = blob(1640, 360, 48, 30, 16, 0.22, 0.4)
add(f"cut {poly(epond)} close depth 5' water")
add("cut " + poly([(1640, 330), (1700, 300), (1760, 320), (1830, 300)]) + " depth 1'6\" width 5' profile round water")
for x, y in ((1600, 395), (1690, 392), (1675, 325)):
    add(f"place paper birch {pt(x, y)} height {rnd.randint(30, 40)}'")
item("Rowboat", "4'x12' height 1'6\" material #a8443a shape tub")
add(f"place rowboat {pt(1628, 352)} facing 70")

# The far east woods, with a hunting cabin in a clearing.
east = wobble([(1720, 420), (1800, 400), (W, 380), (W, 720), (1700, 700), (1660, 560)], 50, 16)
trees(["eastern white pine", "norway spruce", "red oak", "paper birch", "sugar maple"], east, 70, 36, 70, clear=((1790, 560, 26),))
add("house 1780',552' 1800',566' storeys 1 height 9' siding #5b4a3a trim #2b2826 roofing #3a4148 pitch 8 chimney Stone")
track([(1800, 260), (1820, 380), (1795, 545)], 5, "dirt")
for _ in range(16):
    x, y = rnd.uniform(1120, 1860), rnd.uniform(60, 640)
    kind, h = rnd.choice(['white oak', 'red maple', 'eastern redbud', 'black cherry']), rnd.randint(22, 55)
    if not any(inside(x, y, o) for o, _, _ in meadows):
        add(f"place {kind} {pt(x, y)} height {h}'")

section("Woods: a ridge forest along the north, a west woodlot and creek-side willows")
north = wobble([(0, 640), (300, 690), (520, 660), (760, 720), (1100, 700), (1400, 730), (1650, 690), (W, 710), (W, 760), (0, 760)], 60, 22)
trees(["white oak", "red oak", "eastern white pine", "norway spruce", "paper birch", "black cherry"], north, 150, 40, 72,
      clear=((330, 620, 30), (900, 640, 20)))
west = wobble([(0, 260), (60, 280), (40, 400), (0, 420)], 40, 10)
trees(["white oak", "black cherry", "paper birch", "eastern white pine"], west, 18, 34, 56)
for x, y in creek[1:-1:2]:
    add(f"place paper birch {pt(x + rnd.uniform(-20, 20), y + rnd.uniform(8, 20))} height {rnd.randint(30, 44)}'")
CROPLAND = [o for o, _ in fields] + [o for o, _, _ in meadows]
for _ in range(14):
    x, y = rnd.uniform(40, 1060), rnd.uniform(60, 640)
    kind, h = rnd.choice(['white oak', 'red maple', 'eastern redbud', 'dogwood']), rnd.randint(20, 50)
    if not any(inside(x, y, o) for o in CROPLAND):  # no stray trees in a planted field
        add(f"place {kind} {pt(x, y)} height {h}'")
track([(330, 640), (420, 690), (560, 700), (700, 735)], 5, "dirt")

# (Catalog animals have their own legs and heads; the stand-in leg/head pass is gone.)
open(OUT, "w").write("\n".join(C) + "\n")
print(f"wrote {OUT}: {len(C)} lines")

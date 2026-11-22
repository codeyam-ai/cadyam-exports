#!/usr/bin/env python3
"""Shōrai-an: a Japanese tea garden for CadYam Landscape.

A stroll garden on a gentle slope: a koi pond with an island and a red drum
bridge, a waterfall tumbling over boulders, a raked-gravel dry garden, a small
teahouse with its veranda, stone lanterns, a vermilion torii at the gate, a
stepping-stone path, a bamboo grove, Japanese maples, cloud-pruned pines,
flowering cherries and azaleas, moss, and koi in the water.

Feet. X east, Y north. Writes tea.cadyam.
"""
import math, random, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "tea.cadyam"
rnd = random.Random(7)
C = []


def f(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def pt(x, y):
    return f"{f(x)}',{f(y)}'"


def poly(pts):
    return " ".join(pt(x, y) for x, y in pts)


def add(*lines):
    C.extend(lines)


def section(t):
    add(f"# === {t} ===")


def blob(cx, cy, rx, ry, n=16, j=0.15, rot=0.0):
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        r = 1 + rnd.uniform(-j, j)
        x, y = rx * r * math.cos(a), ry * r * math.sin(a)
        c, s = math.cos(rot), math.sin(rot)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def item(name, spec):
    add(f'item define "{name}" {spec}')


W, H = 150, 110
add("app landscape", "units imperial")

section("The ground: a gentle rise to the north, moss everywhere")
add(f"grade {pt(0, 0)} +0' {pt(W, 0)} +0' {pt(W, H)} +7' {pt(0, H)} +6' close")
add(f"lawn {poly([(0, 0), (W, 0), (W, H), (0, H)])}")

section("Bamboo fence round the garden, a vermilion torii at the west gate")
item("Bamboo fence", "0'4\"x0'4\" height 6' material #8a9a52")
add(f"fence {pt(0, 0)} {pt(W, 0)} {pt(W, H)} {pt(0, H)} {pt(0, 64)} style \"horizontal slat\" height 6' material #9c8a4e")
add(f"fence {pt(0, 52)} {pt(0, 0)} style \"horizontal slat\" height 6' material #9c8a4e")
item("Torii post", "1'4\"x1'4\" round height 13' material #c8321e shape cylinder")
item("Torii kasagi", "2'x17' height 1'3\" elevation 13' material #222222 shape block")
item("Torii shimaki", "1'6\"x15' height 1' elevation 12' material #c8321e shape block")
item("Torii nuki", "1'x15' height 0'10\" elevation 10' material #c8321e shape block")
add(f"place torii post {pt(-1, 52)}", f"place torii post {pt(-1, 64)}",
    f"place torii kasagi {pt(-1, 58)}", f"place torii shimaki {pt(-1, 58)}", f"place torii nuki {pt(-1, 58)}")

section("The koi pond, with a pine-topped island")
pond = blob(62, 52, 30, 20, 20, 0.12, 0.2)
add(f"cut {poly(pond)} close depth 3'6\" water")
isle = blob(70, 47, 6, 4.5, 12, 0.15)
add(f"level {poly(isle)} at +2'")

section("A stream and waterfall down from the north")
stream = [(96, 104), (94, 92), (88, 84), (84, 76), (78, 70)]
add("cut " + poly(stream) + " depth 1'6\" width 4' profile round water")
item("Boulder", "4'x3' height 2'6\" material #7d7a72 shape ellipsoid")
item("Big boulder", "7'x5' height 4'6\" material #6f6c66 shape ellipsoid")
for (x, y) in ((92, 96), (99, 97), (95, 100), (90, 89), (97, 90), (86, 81), (91, 80), (81, 73)):
    add(f"place {'big boulder' if rnd.random() < 0.4 else 'boulder'} {pt(x + rnd.uniform(-1, 1), y)} facing {rnd.randint(0, 179)}")
for k in range(16):
    a = 2 * math.pi * k / 16
    if 0.3 < a < 2.0:
        continue
    x, y = 62 + 31.5 * math.cos(a) * (1 + 0.05 * math.sin(3 * a)), 52 + 21.5 * math.sin(a)
    add(f"place boulder {pt(x, y)} facing {rnd.randint(0, 179)}")

section("A red drum bridge to the island, and stepping stones on the far side")
item("Drum bridge", "18'x5' height 3'6\" material #b3261e shape bridge")
add(f"place drum bridge {pt(55, 47)} facing 80")
item("Stepping stone", "2'6\"x2' round height 0'6\" material #8a877f shape cylinder")
for k in range(5):
    add(f"place stepping stone {pt(78 + k * 3.2, 45 + rnd.uniform(-1, 1))} facing {rnd.randint(0, 90)}")

section("Water lilies")
item("Lily pad", "2'x2' round height 0'1\" material #3f7a3a shape cylinder")
item("Lily flower", "0'8\"x0'8\" round height 0'5\" elevation 0'1\" material #f4b6c8 shape ellipsoid")
placed = 0
while placed < 16:
    x, y = rnd.uniform(40, 84), rnd.uniform(40, 64)
    inside = (x - 62) ** 2 / 26.0 ** 2 + (y - 52) ** 2 / 16.0 ** 2 < 0.3
    clear = abs(y - 47) > 4 or abs(x - 55) > 4  # off the bridge
    off_isle = (x - 70) ** 2 / 64 + (y - 47) ** 2 / 36 > 1
    if not (inside and clear and off_isle):
        continue
    k = placed
    placed += 1
    add(f"place lily pad {pt(x, y)}")
    if k % 3 == 0:
        add(f"place lily flower {pt(x + 0.3, y + 0.2)}")

section("The teahouse: dark timber, a hipped roof and a veranda over the dry garden")
add("house 104',14' 128',30' storeys 1 height 9' siding #3b2a20 trim #e9e1cc roofing #4b4f55 roof Hip pitch 6 overhang 3'")
add("deck 100',10' 132',14' height 1'6\"")
add("deck 100',14' 104',30' height 1'6\"")

section("Karesansui: raked white gravel with three stones on moss islands")
add(f"patio {pt(104, 36)} {pt(140, 36)} {pt(140, 62)} {pt(104, 62)} material gravel")
for k in range(13):
    y = 37 + k * 2
    add(f"bed {pt(105, y)} {pt(139, y + 0.25)} mulch #f1eee6 edging None")
for (x, y, s) in ((112, 44, 1.0), (126, 54, 1.3), (133, 42, 0.8)):
    add(f"bed {poly(blob(x, y, 4 * s, 3 * s, 12, 0.18))} mulch #4f6b2c edging None")
    add(f"place big boulder {pt(x, y)} facing {rnd.randint(0, 179)}")
    for r in (6.0 * s, 8.0 * s):
        ring = blob(x, y, r, r * 0.8, 24, 0.0)
        for (a, b) in zip(ring, ring[1:] + ring[:1]):
            add(f"bed {pt(*a)} {pt(*b)} {pt(b[0] + 0.25, b[1] + 0.25)} {pt(a[0] + 0.25, a[1] + 0.25)} mulch #f6f4ee edging None")

section("Stone lanterns")
item("Lantern base", "2'x2' height 0'8\" material #9a978e shape block")
item("Lantern post", "0'10\"x0'10\" round height 2'6\" elevation 0'8\" material #9a978e shape cylinder")
item("Lantern light box", "1'8\"x1'8\" height 1'2\" elevation 3'2\" material #8f8c84 shape block")
item("Lantern glow", "1'x1' height 0'8\" elevation 3'5\" material #f6d27a shape block")
item("Lantern roof", "2'10\"x2'10\" height 0'4\" elevation 4'4\" material #85827a shape roof pitch 7/12")
item("Lantern finial", "0'6\"x0'6\" round height 0'8\" elevation 5'4\" material #85827a shape ellipsoid")
for (x, y) in ((24, 58), (46, 76), (98, 38), (88, 22)):
    for part in ("lantern base", "lantern post", "lantern light box", "lantern glow", "lantern roof", "lantern finial"):
        add(f"place {part} {pt(x, y)}")

section("The stepping-stone path from the torii to the teahouse")
path = [(4, 58), (14, 56), (22, 50), (28, 40), (34, 30), (44, 24), (56, 20), (70, 18), (84, 16), (98, 14)]
for (a, b) in zip(path, path[1:]):
    n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 3.2))
    for k in range(n):
        t = k / n
        add(f"place stepping stone {pt(a[0] + (b[0] - a[0]) * t + rnd.uniform(-0.5, 0.5), a[1] + (b[1] - a[1]) * t + rnd.uniform(-0.5, 0.5))} facing {rnd.randint(0, 179)}")

section("A bamboo grove along the east fence")
item("Bamboo cane", "0'4\"x0'4\" round height 26' material #7f9a3c shape cylinder")
item("Bamboo leaves", "4'x4' height 6' elevation 20' material #6c8f35 shape ellipsoid")
for k in range(90):
    x, y = rnd.uniform(136, 148), rnd.uniform(66, 108)
    add(f"place bamboo cane {pt(x, y)} height {rnd.randint(20, 30)}'")
    if k % 2 == 0:
        add(f"place bamboo leaves {pt(x, y)} elevation {rnd.randint(17, 24)}'")

section("Cloud-pruned pines")
item("Pine trunk", "1'x1' round height 9' material #5b4636 shape cylinder tilt 8")
item("Pine cloud", "5'x4' height 2' material #2f5a32 shape ellipsoid")
for (x, y) in ((70, 47), (30, 86), (116, 74), (18, 24)):
    add(f"place pine trunk {pt(x, y)}")
    # Side pads hug the trunk (each reaches it), so none floats beside it.
    for (dx, dy, z, s) in ((0, 0, 9, 1.0), (1.5, 0.6, 6.5, 0.8), (-1.4, -0.6, 5, 0.75), (0.6, -1.4, 7.5, 0.7)):
        add(f"place pine cloud {pt(x + dx, y + dy)} elevation {f(z)}' size {f(5 * s)}'x{f(4 * s)}'")

item("Azalea mound", "4'x3'4\" height 2'4\" material #c2386a shape ellipsoid")
section("Japanese maples in autumn crimson, flowering cherries and azaleas")
item("Maple trunk", "0'9\"x0'9\" round height 6' material #4a3427 shape cylinder tilt 6")
MAPLE_COLOURS = ("#b8231c", "#d4441f", "#e8752a", "#9e1a24")
for i, (x, y) in enumerate(((40, 92), (54, 98), (22, 74), (104, 56), (98, 80), (10, 42), (70, 88), (122, 80))):
    add(f"place maple trunk {pt(x, y)}")
    for k, (dx, dy, z, w) in enumerate(((0, 0, 6.5, 11), (3, 2, 5.5, 8), (-3, -1.5, 5, 8), (1, -3, 7.5, 7), (-1.5, 2.5, 8.5, 6))):
        col = MAPLE_COLOURS[(i + k) % 4]
        item(f"Maple crown {i}{k}", f"{f(w * 0.8)}'x{f(w * 0.75)}' height {f(w * 0.7)}' elevation {f(z - 1)}' material {col} shape ellipsoid")
        add(f"place maple crown {i}{k} {pt(x + dx, y + dy)}")
item("Cherry trunk", "1'x1' round height 7' material #4a3a30 shape cylinder tilt 5")
for i, (x, y) in enumerate(((16, 98), (30, 104), (112, 98), (126, 102))):
    add(f"place cherry trunk {pt(x, y)}")
    for k, (dx, dy, z, w) in enumerate(((0, 0, 7, 9), (2.4, 0.9, 6, 7), (-2.4, -0.6, 6, 7), (0.9, -2.2, 8.5, 6), (-1.3, 2, 9, 6), (0, 0, 10, 5))):
        col = ("#f6c9d6", "#f2b4c6", "#fbdde6")[(i + k) % 3]
        item(f"Blossom {i}{k}", f"{f(w * 0.85)}'x{f(w * 0.8)}' height {f(w * 0.75)}' elevation {f(z - 1)}' material {col} shape ellipsoid")
        add(f"place blossom {i}{k} {pt(x + dx, y + dy)}")
for k in range(30):
    a = rnd.uniform(0, 2 * math.pi)
    x, y = 62 + 34 * math.cos(a), 52 + 24 * math.sin(a)
    if 70 < x < 100 and y > 62:
        continue
    add(f"place azalea mound {pt(x, y)} facing {rnd.randint(0, 179)}")

open(OUT, "w").write("\n".join(C) + "\n")
print(f"wrote {OUT}: {len(C)} lines")

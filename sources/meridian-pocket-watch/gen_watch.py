#!/usr/bin/env python3
"""The Meridian: an open-backed pocket watch for CadYam Forms.

A 46 mm rose-gold case lying back-up on the table, its movement on show: a
silvered main plate, skeleton bridges, a gilt going train with cut teeth, a
screwed balance with a blued hairspring, ruby jewels in gold settings, blued
screws, and a cable chain with a T-bar running out from the bow.

Millimetres. X across, Y up the page (the crown at 12 o'clock is +Y), Z up off
the table. Writes watch.cadyam.
"""
import math, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "watch.cadyam"
SCREW = sys.argv[2] if len(sys.argv) > 2 else "blued_steel"
C = []


def f(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def p(x, y, z):
    return f"{f(x)},{f(y)},{f(z)}"


MAKERS = ("lathe ", "box ", "cylinder ", "torus ", "sphere ", "pipe ", "capsule ")
NOBJ = 0  # solids made so far: each is the next object number


def add(*lines):
    global NOBJ
    for l in lines:
        if l.startswith(MAKERS):
            NOBJ += 1
    C.extend(lines)


def section(t):
    add(f"# === {t} ===")


def mat(m):
    add(f"material last {m}")


CASE, PLATE, GILT, JEWEL, STEEL = "rose_gold", "brushed_aluminum", "yellow_gold", "ruby", "brushed_steel"
add("app forms", "units mm", "form detail fine", "material form plain")

# ------------------------------------------------------------------ case
R_CASE = 23.0
SEAT = 8.6  # the movement sits on this height
section("A rose-gold case, its back open on the movement")
prof = [(0, 0), (20.5, 0), (22.4, 0.8), (23.1, 2.6), (23.2, 5.5), (22.8, 8.4), (22.0, 10.1),
        (21.0, 10.6), (20.3, 10.6), (20.3, SEAT), (0, SEAT)]
add("lathe " + " ".join(f"{f(r)},{f(z)}" for r, z in prof) + " at 0,0,0 aim 0,0,1")
mat(CASE)
# a fine reeded band round the middle of the case
for k in range(96):
    a = 2 * math.pi * k / 96
    add(f"box {p(23.15 * math.cos(a), 23.15 * math.sin(a), 5.6)} 0.22,0.5,2.2 turn {f(math.degrees(a))},0,0")
    mat(CASE)

section("Pendant, knurled crown and the bow")
add(f"cylinder {p(0, 23.6, 5.6)} r 1.5 h 2.6 turn 0,0,90")
mat(CASE)
add(f"cylinder {p(0, 26.4, 5.6)} r 2.7 h 3.2 turn 0,0,90")
mat(CASE)
for k in range(28):
    a = 2 * math.pi * k / 28
    add(f"box {p(2.72 * math.cos(a), 26.4, 5.6 + 2.72 * math.sin(a))} 0.35,3.0,0.35 turn 0,{f(-math.degrees(a))},0")
    mat(CASE)
add(f"sphere {p(0, 28.1, 5.6)} r 1.4")
mat(CASE)
BOW_Y = 33.0
add(f"torus {p(0, BOW_Y, 1.0)} 5.2,0.85")
mat(CASE)

# ------------------------------------------------------------------ movement
TOP = SEAT + 0.8  # top of the main plate
section("Silvered main plate")
add(f"cylinder {p(0, 0, SEAT + 0.4)} r 20.1 h 0.8")
mat(PLATE)
# a sunk ring of circular graining round the plate's edge
add(f"torus {p(0, 0, TOP)} 19.4,0.18")
mat(PLATE)


def as_model(first):
    """Turn the solids made since `first` into one model, meshed at print detail:
    parts under half a millimetre thick keep their exact shape in exports."""
    add("form detail print", "model from " + " ".join(str(i) for i in range(first, NOBJ + 1)) + " replace",
        "form detail fine")


def gear(cx, cy, R, z, teeth, material, spokes=5, hub=1.3, club=False):
    """A wheel: a thin rim with spokes and a hub, its teeth cut round the edge."""
    first = NOBJ + 1
    th = 0.45
    # the rim: a revolved ring, so it meshes cleanly at any detail
    add(f"lathe {f(R - 1.1)},{f(-th / 2)} {f(R)},{f(-th / 2)} {f(R)},{f(th / 2)} {f(R - 1.1)},{f(th / 2)} at {p(cx, cy, z)} aim 0,0,1")
    mat(material)
    add(f"cylinder {p(cx, cy, z)} r {f(hub)} h {f(th + 0.15)}")
    mat(material)
    for k in range(spokes):
        a = 360 * k / spokes + 18
        ar = math.radians(a)
        mid = (R - 0.6 + hub) / 2
        add(f"box {p(cx + mid * math.cos(ar), cy + mid * math.sin(ar), z)} {f(R - 0.8 - hub)},0.55,{f(th)} turn {f(a)},0,0")
        mat(material)
    for k in range(teeth):
        a = 360 * k / teeth
        ar = math.radians(a)
        rr = R + 0.12
        if club:  # an escape wheel's raked club teeth
            add(f"box {p(cx + (R + 0.45) * math.cos(ar), cy + (R + 0.45) * math.sin(ar), z)} 1.1,0.32,{f(th)} turn {f(a + 28)},0,0")
        else:
            add(f"box {p(cx + rr * math.cos(ar), cy + rr * math.sin(ar), z)} 0.5,{f(min(0.5, 2 * math.pi * R / teeth * 0.55))},{f(th)} turn {f(a)},0,0")
        mat(material)


def jewel(cx, cy, z):
    """A ruby pivot jewel, domed, in a gold setting."""
    add(f"torus {p(cx, cy, z)} 0.95,0.28")
    mat(GILT)
    add(f"sphere {p(cx, cy, z - 0.1)} r 0.62")
    mat(JEWEL)


def screw(cx, cy, z, r=0.85, turn=30):
    """A blued screw head with its slot."""
    add(f"cylinder {p(cx, cy, z + 0.25)} r {f(r)} h 0.5")
    mat(SCREW)
    add(f"box {p(cx, cy, z + 0.52)} {f(1.9 * r)},0.26,0.06 turn {f(turn)},0,0")
    mat("#1a1e2c")


def bridge(x0, y0, x1, y1, z, w, end_r=None):
    """A skeleton bridge: a rounded bar from (x0,y0) to (x1,y1) with a round boss at its far end."""
    L = math.hypot(x1 - x0, y1 - y0)
    a = math.degrees(math.atan2(y1 - y0, x1 - x0))
    add(f"box {p((x0 + x1) / 2, (y0 + y1) / 2, z)} {f(L)},{f(w)},0.9 radius 0.4 turn {f(a)},0,0")
    mat(PLATE)
    add(f"cylinder {p(x1, y1, z)} r {f(end_r or w * 0.75)} h 0.9")
    mat(PLATE)


# The going train: barrel, centre, third, fourth and escape wheels.
GZ = TOP + 0.45  # wheel height
BAR = (-7.5, 7.0, 8.0)
CEN = (3.5, 5.0, 6.0)
THI = (10.0, -2.0, 4.6)
FOU = (6.5, -10.5, 4.2)
ESC = (-1.5, -14.0, 3.2)
BAL = (-10.0, -8.5, 6.3)

section("Mainspring barrel with its steel ratchet wheel and crown wheel")
gear(*BAR, GZ, 72, GILT, spokes=0, hub=7.0)
gear(BAR[0], BAR[1], 6.0, GZ + 1.6, 48, STEEL, spokes=0, hub=5.0)
gear(-2.5, 15.0, 3.0, GZ + 1.6, 24, STEEL, spokes=0, hub=2.2)
screw(BAR[0], BAR[1], GZ + 2.1, r=1.6)
screw(-2.5, 15.0, GZ + 2.1, r=1.0)

section("The going train: centre, third, fourth and escape wheels")
gear(*CEN, GZ, 60, GILT)
gear(*THI, GZ + 0.55, 48, GILT, spokes=4)
gear(*FOU, GZ, 44, GILT, spokes=4)
gear(*ESC, GZ + 0.55, 15, STEEL, spokes=3, hub=0.8, club=True)
add(f"box {p((ESC[0] + BAL[0]) / 2 + 0.5, (ESC[1] + BAL[1]) / 2, GZ + 0.9)} 7.5,0.6,0.4 turn {f(math.degrees(math.atan2(BAL[1] - ESC[1], BAL[0] - ESC[0])))},0,0")
mat(STEEL)  # the pallet lever

section("Skeleton bridges over the train, each pivot jewelled")
BZ = GZ + 1.35
for (gx, gy, _r) in (CEN, THI, FOU, ESC):
    a = math.atan2(gy, gx)
    ex, ey = 18.6 * math.cos(a), 18.6 * math.sin(a)
    bridge(ex, ey, gx, gy, BZ, 2.6)
    jewel(gx, gy, BZ + 0.5)
    screw(ex, ey, BZ + 0.45)
# the barrel bridge: a broad sweep across the top of the plate
bridge(-18.0, 4.0, BAR[0], BAR[1], BZ + 0.9, 4.2, end_r=3.4)
bridge(-6.0, 18.0, BAR[0], BAR[1], BZ + 0.9, 3.2, end_r=3.4)
jewel(BAR[0] + 3.0, BAR[1] - 2.2, BZ + 1.4)

section("Screwed balance with a blued hairspring, under its balance cock")
BR = BAL[2]
first_bal = NOBJ + 1
add(f"torus {p(BAL[0], BAL[1], GZ + 0.25)} {f(BR)},0.42")
mat(GILT)
for a in (25, 115):
    add(f"box {p(BAL[0], BAL[1], GZ + 0.25)} {f(2 * BR)},0.5,0.4 turn {a},0,0")
    mat(GILT)
for k in range(18):
    a = 2 * math.pi * k / 18
    add(f"sphere {p(BAL[0] + (BR + 0.35) * math.cos(a), BAL[1] + (BR + 0.35) * math.sin(a), GZ + 0.25)} r 0.34")
    mat(GILT)
pts = []
for i in range(361):
    t = i / 360
    a = t * 2 * math.pi * 10
    rr = 1.0 + 3.6 * t
    pts.append((BAL[0] + rr * math.cos(a), BAL[1] + rr * math.sin(a), GZ + 0.75))
add("pipe " + " ".join(p(*q) for q in pts) + " r 0.09")
mat(SCREW)

cock_end = (-19.0, -4.5)
bridge(cock_end[0], cock_end[1], BAL[0], BAL[1], BZ + 0.2, 3.4, end_r=2.8)
jewel(BAL[0], BAL[1], BZ + 0.7)
screw(cock_end[0], cock_end[1], BZ + 0.65)
# the regulator: a fine steel index arm over the cock
add(f"box {p(BAL[0] + 2.4, BAL[1] + 1.8, BZ + 0.75)} 6.0,0.35,0.2 turn 35,0,0")
mat(SCREW)

section("Plate screws round the edge")
for a in (60, 150, 245, 330):
    ar = math.radians(a)
    screw(19.2 * math.cos(ar), 19.2 * math.sin(ar), TOP, r=0.75, turn=a)

# ------------------------------------------------------------------ chain
section("A cable chain from the bow, curling across the table to a T-bar")
LR, LT = 1.15, 0.3
PITCH = 2 * (LR - LT) + 0.04
path = []
for i in range(401):
    t = i / 400
    a = math.radians(95 - 150 * t)
    rr = 30 + 4 * math.sin(t * math.pi)
    path.append((rr * math.cos(a) * 0.95 + 4.0 * t, rr * math.sin(a) * 0.9 + 3.0, LT + 0.05))
# start at the bow
path[0] = (0.0, BOW_Y + 5.0, LT + 0.05)
acc, need, k = 0.0, 0.0, 0
px, py, _ = path[0]
for (x, y, z) in path[1:]:
    seg = math.hypot(x - px, y - py)
    while seg and acc + seg >= need:
        t = (need - acc) / seg
        cx, cy = px + (x - px) * t, py + (y - py) * t
        th = math.degrees(math.atan2(y - py, x - px))
        if k % 2 == 0:
            add(f"torus {p(cx, cy, LT + 0.02)} {f(LR)},{f(LT)}")
        else:
            add(f"torus {p(cx, cy, LR + 0.02)} {f(LR)},{f(LT)} turn {f(th)},0,90")
        mat(CASE)
        k += 1
        need += PITCH
    acc += seg
    px, py = x, y
# the T-bar at the chain's end
ex, ey = px, py
add(f"capsule {p(ex + 2.5, ey - 2.0, 1.1)} r 1.0 length 14 turn 40,90,0")
mat(CASE)

open(OUT, "w").write("\n".join(C) + "\n")
print(f"wrote {OUT}: {len(C)} lines, {k} chain links")

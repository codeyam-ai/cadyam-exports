#!/usr/bin/env python3
"""Gull Rock Light: a lighthouse islet diorama for CadYam Forms.

Axes: +X east, +Y north, +Z up; z=0 is the underside of the sea base. About 180 mm across.
Writes command lines to lighthouse.cadyam.
"""
import math, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "lighthouse.cadyam"
C = []


def f(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def p(x, y, z):
    return f"{f(x)},{f(y)},{f(z)}"


def add(*lines):
    C.extend(lines)


def mat(m, ref="last"):
    add(f"material {ref} {m}")


def pipe(pts, r, extra=""):
    add("pipe " + " ".join(p(*q) for q in pts) + f" r {f(r)}" + (f" {extra}" if extra else ""))


def lathe(profile, x, y, z, m, aim="0,0,1"):
    add("lathe " + " ".join(f"{f(r)},{f(a)}" for r, a in profile) + f" at {p(x, y, z)} aim {aim}")
    mat(m)


def section(title):
    add(f"# === {title} ===")


STONE, SLATE, WHITE, RED, GLASS, COPPER, BLACK = "stone_veneer", "slate_tile", "white", "#b3261e", "glass", "copper", "charcoal"
WATER, CEDAR, PLASTER, GRASS, BRICK = "water", "cedar", "plaster", "lawn", "brick"
SEA = 6.0

add("app forms", "units mm", "form detail normal", "material form plain")

section("Calm sea: a water disc with wind ripples")
lathe([(0, 0), (88, 0), (90, 2), (90, SEA - 0.6), (89, SEA), (0, SEA)], 0, 0, 0, WATER)
add(f"relief noise fbm box {p(-90, -90, SEA - 1)} {p(90, 90, SEA + 1)} size 7mm depth 0.7mm seed 3")

section("The islet: stone masses blended into one rock, ridged and creased")
rocks = [((10, 5, -10), 46), ((-30, -14, -12), 34), ((36, -26, -20), 30), ((-8, 36, -25), 32),
         ((-46, 18, -14), 20), ((50, 18, -8), 14)]
for (x, y, z), r in rocks:
    add(f"sphere {p(x, y, z)} r {f(r)}")
add(f"box {p(0, 0, -50)} 220,220,100")
add("subtract last")
add("group " + " ".join(f"last-{i}" if i else "last" for i in range(len(rocks), -1, -1)) + " blend 7")
mat("#8a867d")
add(f"relief ridged sphere {p(5, 0, 20)} r 70 size 9mm depth 1.6mm seed 7 falloff 6")
add(f"relief cellular sphere {p(-30, -14, 15)} r 30 size 5mm depth 0.8mm seed 2")
add(f"sculpt crease {p(-8, -40, 12)} {p(10, -30, 22)} {p(28, -34, 14)} width 3 depth 1.4 sharp 0.6")
add(f"sculpt crease {p(30, 20, 26)} {p(46, 26, 12)} width 3 depth 1.2 sharp 0.5")
# grassy turf on the crown
section("The lighthouse: banded tower, spiral windows and a door")
TX, TY, TZ = 12, 6, 33.0
lathe([(0, 0), (17, 0), (17, 4), (15, 5), (0, 5)], TX, TY, TZ, STONE)
H = 66.0
bands = [(0, 0.2, WHITE), (0.2, 0.4, RED), (0.4, 0.6, WHITE), (0.6, 0.8, RED), (0.8, 1.0, WHITE)]
r0, r1 = 12.5, 8.5
for a, b, m in bands:
    za, zb = a * H, b * H
    ra, rb = r0 + (r1 - r0) * a, r0 + (r1 - r0) * b
    lathe([(0, za), (ra, za), (rb, zb), (0, zb)], TX, TY, TZ + 5, m)
for k in range(7):
    t = 0.12 + k * 0.11
    ang = math.radians(40 + k * 75)
    r = r0 + (r1 - r0) * t + 0.3
    x, y, z = TX + r * math.cos(ang), TY + r * math.sin(ang), TZ + 5 + t * H
    add(f"box {p(x, y, z)} 1.8,3,4.2 turn {f(math.degrees(ang))},0,0 chamfer 0.3")
    mat(BLACK)
add(f"box {p(TX + 12.2, TY, TZ + 9.5)} 2,6,9 chamfer 0.4")
mat("#2b3a4a")
add(f"lathe 0,0 3,0 3,1 0,1 at {p(TX + 12.6, TY, TZ + 14)} aim 1,0,0 angle 180")
mat(WHITE)

section("Gallery, railings, glazed lamp room and copper dome")
GZ = TZ + 5 + H
lathe([(0, 0), (12.5, 0), (12.5, 1.6), (0, 1.6)], TX, TY, GZ, BLACK)
lathe([(11.6, 6.0), (12.4, 6.0), (12.4, 6.8), (11.6, 6.8)], TX, TY, GZ, BLACK)
for k in range(20):
    a = math.radians(k * 18)
    pipe([(TX + 12 * math.cos(a), TY + 12 * math.sin(a), GZ + 1.0), (TX + 12 * math.cos(a), TY + 12 * math.sin(a), GZ + 6.4)], 0.35)
    mat(BLACK)
lathe([(0, 0), (7.6, 0), (7.6, 10), (0, 10)], TX, TY, GZ + 1.6, GLASS)
add(f"sphere {p(TX, TY, GZ + 6.6)} r 3.2")
mat("#ffd970")
for k in range(8):
    a = math.radians(k * 45)
    add(f"box {p(TX + 7.4 * math.cos(a), TY + 7.4 * math.sin(a), GZ + 6.6)} 0.8,0.8,10")
    mat(BLACK)
lathe([(0, 0), (8.6, 0), (8.2, 1.4), (6, 4.6), (3, 6.8), (0, 7.4)], TX, TY, GZ + 11.6, COPPER)
add(f"sphere {p(TX, TY, GZ + 20)} r 1.4")
mat(COPPER)
pipe([(TX, TY, GZ + 19), (TX, TY, GZ + 27)], 0.35)
mat(BLACK)
add(f"wedge {p(TX + 2.5, TY, GZ + 25.5)} 5,0.4,2.4 top 2,0.3 shift 1.5,0")
mat(BLACK)
pipe([(TX - 2.2, TY, GZ + 24), (TX + 2.2, TY, GZ + 24)], 0.25)
mat(BLACK)
pipe([(TX, TY - 2.2, GZ + 24), (TX, TY + 2.2, GZ + 24)], 0.25)
mat(BLACK)

section("Keeper's cottage: whitewashed walls, slate roof, brick chimney")
CX, CY, CZ = -30, -14, 18.0
add(f"box {p(CX, CY, CZ)} 26,16,8 chamfer 0.4")
add(f"box {p(CX, CY, CZ + 6.5)} 24,14,13 chamfer 0.4")
mat(PLASTER)
add(f"wedge {p(CX, CY, CZ + 17)} 28,18,6 top 28,1.5")
mat(SLATE)
add(f"box {p(CX - 9, CY + 3, CZ + 18)} 3.5,3.5,10 chamfer 0.3")
mat(BRICK)
for x in (-6, 0, 6):
    add(f"box {p(CX + x, CY - 7.1, CZ + 9)} 3.2,0.8,3.6 chamfer 0.2")
    mat("#2b3a4a")
    add(f"box {p(CX + x, CY - 7.3, CZ + 7)} 4,0.8,0.7")
    mat(WHITE)
add(f"box {p(CX + 12.1, CY, CZ + 7)} 0.8,4,7 chamfer 0.2")
mat(RED)

section("Stone steps down to a timber jetty, with a moored rowboat")
for k in range(7):
    add(f"box {p(32 + k * 4, -28 - k * 2.5, 20 - k * 2.2 - 1.6)} 5,4.4,4.8 chamfer 0.4")
    mat(STONE)
for s_ in (1, -1):
    add(f"box {p(75, -45 + s_ * 4.2, SEA + 1.0)} 34,1.2,1.4")
    mat(CEDAR)
for k in range(10):
    add(f"box {p(60 + k * 3.2, -45, SEA + 2.2)} 2.8,10,1 chamfer 0.2")
    mat(CEDAR)
for x in (60, 75, 89):
    for s in (1, -1):
        pipe([(x, -45 + s * 5.4, SEA - 2), (x, -45 + s * 5.4, SEA + 5)], 0.9)
        mat(CEDAR)
BX, BY = 76, -60
add(f"wedge {p(BX, BY, SEA + 1.6)} 18,6,3.6 top 22,8.5")
add(f"wedge {p(BX, BY, SEA + 2.4)} 16,5,3.2 top 20,6.8")
add("subtract last", "group last-1 last")
mat(RED)
add(f"box {p(BX + 11, BY, SEA + 2.4)} 4,4,2.6 turn 45,0,0")
add("subtract last", "group last-1 last")
for x in (BX - 3, BX + 3):
    add(f"box {p(x, BY, SEA + 3)} 1.4,7,0.6")
    mat(CEDAR)
pipe([(BX - 4, BY, SEA + 3.0), (BX + 6, BY + 3, SEA + 3.2)], 0.3)
mat(CEDAR)
pipe([(BX + 9, BY, SEA + 3), (BX + 14, BY + 6, SEA + 5), (89, -50.4, SEA + 4)], 0.2, "bend 2")
mat("#c8b68a")

section("Channel buoy, lobster pots, a lifebuoy and two gulls")
lathe([(0, 0), (3.2, 0), (3.6, 2), (3.6, 4), (0, 4)], -60, -50, SEA - 1, RED)
lathe([(0, 0), (3.6, 0), (2.6, 4), (1.4, 7), (0, 7.4)], -60, -50, SEA + 3, WHITE)
pipe([(-60, -50, SEA + 10), (-60, -50, SEA + 14)], 0.35)
mat(BLACK)
add(f"lamp {p(-60, -50, SEA + 14.6)} r 0.9")
mat("#ff6a3d")
for k, (x, y) in enumerate(((84, -42), (87, -47.5), (62, -48))):
    add(f"box {p(x, y, SEA + 3.95)} 3.6,3,2.6 chamfer 0.4")
    mat("#c49a5a" if k % 2 else "#7a5232")
    for d in (-1, 0, 1):
        add(f"box {p(x + d * 1.1, y, SEA + 3.95)} 0.3,3.2,2.8")
        mat("#3a2a18")
add(f"torus {p(TX + 13.3, TY - 7, TZ + 13)} 3,0.9 turn 0,90,0")
mat(RED)
add(f"torus {p(TX + 13.4, TY - 7, TZ + 13)} 3,0.95 turn 0,90,0 sweep 90" if False else f"box {p(TX + 13.5, TY - 7, TZ + 16)} 1.6,1,1.4")
mat(WHITE)
for (x, y, z, yaw) in ((40, 22, 22, 30), (-44, 16, 16, 200)):
    add(f"wedge {p(x, y, z)} 2.4,7,0.6 top 0.6,6 turn {yaw},0,0")
    mat(WHITE)
    add(f"sphere {p(x + 0.6, y, z + 0.6)} r 0.9")
    mat(WHITE)
    add(f"cone {p(x + 1.6, y, z + 0.6)} r 0.3,0 h 1")
    mat("#f2b33d")

section("Fence posts along the cliff path")
for k in range(6):
    x, y = -12 + k * 6, -22 - k * 1.2
    pipe([(x, y, 24 - k * 1.6), (x, y, 34 - k * 1.6)], 0.5)
    mat(CEDAR)

open(OUT, "w").write("\n".join(C) + "\n")
print(f"wrote {OUT}: {len(C)} lines")

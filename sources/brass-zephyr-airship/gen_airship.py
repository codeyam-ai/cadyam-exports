#!/usr/bin/env python3
"""The Brass Zephyr: a steampunk airship on a mooring-stand display base, for CadYam Forms.

Axes: +X toward the nose, +Y to port, +Z up; z=0 is the bottom of the display base.
About 200 mm long. Writes command lines (one per line) to airship.cadyam.
"""
import math, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "airship.cadyam"
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


def lathe_x(profile, x, y, z, m, aim="1,0,0"):
    """Revolve (radius, along) pairs about an axis through x,y,z."""
    add("lathe " + " ".join(f"{f(r)},{f(a)}" for r, a in profile) + f" at {p(x, y, z)} aim {aim}")
    mat(m)


def section(title):
    add(f"# === {title} ===")


BRASS, COPPER, WALNUT, STEEL, CANVAS, GLASS, LEATHER = (
    "brass", "copper", "walnut", "brushed_steel", "#d8ccb0", "glass", "leather")
RED = "#9b2b22"

# ------------------------------------------------------------------ envelope
EZ = 104.0  # envelope axis height
GZ = 54.0  # gondola deck height
ENV = [(-92, 0), (-86, 8), (-78, 15), (-66, 22), (-50, 28), (-30, 32), (-8, 34), (14, 34),
       (34, 32), (52, 27), (64, 21), (73, 14), (79, 8), (82, 0)]


def r_at(x):
    for (x0, r0), (x1, r1) in zip(ENV, ENV[1:]):
        if x0 <= x <= x1:
            return r0 + (r1 - r0) * (x - x0) / (x1 - x0)
    return 0.0


add("app forms", "units mm", "form detail normal", "material form plain")

section("Gasbag: a canvas envelope revolved from its side outline")
# lathe profile pairs are (radius, distance along the axis)
lathe_x([(0, -92)] + [(r, x) for x, r in ENV[1:-1]] + [(0, 82)], 0, 0, EZ, CANVAS)

add(f"relief noise fbm sphere {p(-5, 0, EZ)} r 95 size 9mm depth 0.5mm seed 11 falloff 4")
section("Brass girth bands and eight longitudinal straps")
for x in (-62, -36, -8, 22, 48):
    r = r_at(x)
    lathe_x([(r - 0.4, -1.6), (r + 1.0, -1.6), (r + 1.3, 0), (r + 1.0, 1.6), (r - 0.4, 1.6)], x, 0, EZ, BRASS)
# polar copies lose their material (a CadYam bug), so each strap is written out
for k in range(8):
    a = math.radians(k * 45)
    strap = [(x, -math.sin(a) * (r_at(x) + 0.5), EZ + math.cos(a) * (r_at(x) + 0.5)) for x in range(-84, 79, 6)]
    pipe(strap, 0.8, "bend 4")
    mat(BRASS)

section("Copper nose cap with a brass spike, and an observation blister")
lathe_x([(0, 0), (8.6, 0), (7.5, 4), (4.5, 7.5), (0, 9)], 75, 0, EZ, COPPER)
lathe_x([(0, 0), (1.6, 0), (0.3, 14), (0, 14)], 83, 0, EZ, BRASS)
add(f"sphere {p(40, 0, EZ - 32)} r 6")
mat(GLASS)
lathe_x([(5.6, -0.8), (7.2, -0.8), (7.2, 0.8), (5.6, 0.8)], 40, 0, EZ - 32, BRASS, aim="0,0,1")

section("Swept copper tail fins with brass leading edges")
for k in range(4):
    add("wedge -74,0,31 34,1.6,26 top 13,1 shift -12,0")
    mat(COPPER)
    pipe([(-57, 0, 19), (-77, 0, 44), (-88, 0, 44)], 0.9, "bend 2")
    mat(BRASS)
    add(f"group last-1 last at {p(0, 0, EZ)} turn 0,0,{k * 90}")

section("Tail pusher propeller with a copper spinner")
lathe_x([(0, 0), (5, 0), (4, 5), (0, 9)], -101, 0, EZ, COPPER, aim="-1,0,0")
add(f"pipe {p(-92, 0, EZ)} {p(-101, 0, EZ)} r 2.2")
mat(STEEL)
for k in range(4):
    a = k * 90 + 20
    add(f"box {p(-98, 0, EZ)} 1.4,4.5,26 turn 0,0,{a} chamfer 0.5")
    mat(WALNUT)

section("Crow's nest on the crown, with a telescope and pennant")
NX, NZ = 6, EZ + r_at(6)
lathe_x([(0, -1), (7, -1), (8, 0), (8, 1.4), (0, 1.4)], NX, 0, NZ, WALNUT, aim="0,0,1")
for k in range(10):
    a = math.radians(k * 36)
    pipe([(NX + 7.4 * math.cos(a), 7.4 * math.sin(a), NZ + 1.4), (NX + 7.4 * math.cos(a), 7.4 * math.sin(a), NZ + 6)], 0.3)
    mat(BRASS)
lathe_x([(7.0, 5.6), (7.8, 5.6), (7.8, 6.4), (7.0, 6.4)], NX, 0, NZ, BRASS, aim="0,0,1")
pipe([(NX - 3, 2, NZ + 5), (NX + 9, 5, NZ + 8)], 0.9)
mat(BRASS)
pipe([(NX + 8, 4.7, NZ + 7.7), (NX + 10.5, 5.4, NZ + 8.5)], 1.3, "cap open hollow 0.4")
mat(BRASS)
pipe([(NX - 4, -3, NZ + 1.4), (NX - 4, -3, NZ + 16)], 0.4)
mat(BRASS)
add(f"wedge {p(NX - 7.5, -3, NZ + 14)} 7,0.5,4 top 1,0.3 shift -3,0")
mat(RED)

section("Anchor on a chain below the gondola")
GZ = 54.0
for k in range(9):
    z = GZ - 16 - k * 2.2
    add(f"torus {p(-14, 0, z)} 1.1,0.35 turn " + ("90,90,0" if k % 2 else "0,90,0"))
    mat(STEEL)
AZ = GZ - 16 - 9 * 2.2
pipe([(-14, 0, AZ), (-14, 0, AZ - 9)], 0.7)
mat(STEEL)
pipe([(-19, 0, AZ - 5), (-17, 0, AZ - 9.5), (-14, 0, AZ - 10), (-11, 0, AZ - 9.5), (-9, 0, AZ - 5)], 0.7, "bend 2")
mat(STEEL)
pipe([(-17, 0, AZ - 1.5), (-11, 0, AZ - 1.5)], 0.5)
mat(STEEL)

section("Rigging: lines from the gasbag down to the gondola")
for x in (-26, -6, 14, 32):
    for s in (1, -1):
        top = (x, s * 14, EZ - r_at(x) * 0.93)
        pipe([top, (x * 0.85, s * 12, GZ + 1)], 0.35)
        mat(LEATHER)

section("Walnut gondola: hull, brass gunwale, deck and keel")
add(f"wedge {p(2, 0, GZ - 7)} 64,16,14 top 80,26 shift 0,0")
cut = [f"box {p(46, s * 16, GZ - 7)} 24,24,20 turn {45 * s},0,0" for s in (1, -1)]
cut += [f"box {p(-42, s * 16, GZ - 7)} 24,24,20 turn {-45 * s},0,0" for s in (1, -1)]
for c in cut:
    add(c)
add("subtract last-3 last-2 last-1 last", "group last-4 last-3 last-2 last-1 last")
mat(WALNUT)
for z in (GZ - 3, GZ - 9):
    add(f"rivets {p(-30, 13, z)} {p(30, 13, z)} spacing 4 r 0.5")
    add(f"rivets {p(-30, -13, z)} {p(30, -13, z)} spacing 4 r 0.5")
pipe([(-31, 0, GZ + 0.6), (-24, 12.6, GZ + 0.6), (32, 12.6, GZ + 0.6), (40, 0, GZ + 0.6),
      (32, -12.6, GZ + 0.6), (-24, -12.6, GZ + 0.6), (-31, 0, GZ + 0.6)], 0.9, "bend 3")
mat(BRASS)
pipe([(-36, 0, GZ - 14.5), (44, 0, GZ - 14.5)], 1.6)
mat(BRASS)
for k in range(-4, 5):
    add(f"box {p(k * 7, 0, GZ - 15.2)} 1.2,6,1.2")
    mat(BRASS)

section("Cabin with a copper roof and brass-rimmed portholes")
add(f"box {p(-4, 0, GZ + 6)} 40,20,12 chamfer 1")
mat(WALNUT)
add(f"wedge {p(-4, 0, GZ + 13.5)} 44,23,3 top 38,15")
mat(COPPER)
for x in (-18, -10, -2, 6, 14):
    for s in (1, -1):
        lathe_x([(1.9, 0), (2.9, 0), (2.9, 0.9), (1.9, 0.9)], x, s * 10, GZ + 6, BRASS, aim=f"0,{s},0")
        lathe_x([(0, 0), (2.0, 0), (2.0, 0.4), (0, 0.4)], x, s * 10, GZ + 6, GLASS, aim=f"0,{s},0")
add(f"box {p(16.2, 0, GZ + 5)} 0.8,7,10 chamfer 0.3")
mat("#3a2414")
add(f"lathe 0,0 0.9,0 0.9,1 0,1 at {p(16.5, -2.4, GZ + 5)} aim 1,0,0")
mat(BRASS)

section("Fore deck: ship's wheel, binnacle and bow lantern")
WX, WZ = 26, GZ + 8
lathe_x([(4.6, -0.5), (5.6, -0.5), (5.6, 0.5), (4.6, 0.5)], WX, 0, WZ, WALNUT)
for k in range(8):
    a = math.radians(k * 45)
    pipe([(WX, 0, WZ), (WX, 7.4 * math.cos(a), WZ + 7.4 * math.sin(a))], 0.4)
    mat(WALNUT)
add(f"sphere {p(WX, 0, WZ)} r 1.3")
mat(BRASS)
add(f"pipe {p(WX - 2, 0, GZ)} {p(WX - 2, 0, WZ)} r 1")
mat(BRASS)
add(f"cylinder {p(34, 0, GZ + 3)} r 2.2 h 6")
mat(BRASS)
add(f"sphere {p(34, 0, GZ + 7)} r 2.2")
mat(GLASS)
add(f"lamp {p(41, 0, GZ + 2)} r 1.6")
mat("#f2c14e")
for x in (22, 28, 34):
    for s in (1, -1):
        pipe([(x, s * 11.5, GZ), (x, s * 11.5, GZ + 5)], 0.4)
        mat(BRASS)
for s in (1, -1):
    pipe([(20, s * 11.5, GZ + 5), (34, s * 11.5, GZ + 5), (40, s * 4, GZ + 5)], 0.45, "bend 2")
    mat(BRASS)

section("Aft deck: riveted boiler, pressure gauges and smokestack")
BX = -26
lathe_x([(0, 0), (5.5, 0), (6, 1), (6, 15), (5.5, 16), (0, 16)], BX - 8, 0, GZ + 6.5, BRASS)
for x in (BX - 6, BX + 6):
    add(f"rivets {p(x, -6, GZ + 6.5)} {p(x, 6, GZ + 6.5)} spacing 2.4 r 0.45")
for s in (1, -1):
    add(f"lathe 0,0 1.8,0 1.8,1 0,1 at {p(BX, s * 6, GZ + 8)} aim 0,{s},0")
    mat(BRASS)
    add(f"lamp {p(BX, s * 7.1, GZ + 8)} r 1.2")
    mat("#f4ead2")
pipe([(BX - 4, 0, GZ + 12), (BX - 4, 0, GZ + 30)], 2.2)
mat(COPPER)
lathe_x([(2, 0), (3.4, 0), (3.6, 1.5), (2, 1.5)], BX - 4, 0, GZ + 30, COPPER, aim="0,0,1")

section("Twin engine nacelles on outriggers, with cooling rings and propellers")
for s in (1, -1):
    ny, nz = s * 33, GZ - 2
    lathe_x([(0, 0), (3, 0), (5, 3), (5.4, 10), (5, 18), (3.6, 22), (0, 22)], -12, ny, nz, BRASS)
    for x in (-8, -5, -2):
        lathe_x([(5.2, -0.5), (6.6, -0.5), (6.6, 0.5), (5.2, 0.5)], x, ny, nz, COPPER)
    pipe([(-2, s * 12, GZ - 3), (-2, ny - s * 4, nz)], 1.2)
    mat(STEEL)
    pipe([(-8, s * 12, GZ - 9), (-6, ny - s * 3, nz - 3)], 0.9)
    mat(STEEL)
    pipe([(BX + 2, s * 5, GZ + 9), (BX + 2, s * 12, GZ + 9), (-10, s * 14, GZ + 2), (-10, ny - s * 4, nz + 3)], 0.8, "bend 3")
    mat(COPPER)
    lathe_x([(0, 0), (2.6, 0), (2, 3), (0, 4.5)], -12, ny, nz, COPPER, aim="-1,0,0")
    for k in range(4):
        add(f"box {p(-14.5, ny, nz)} 1,3.6,19 turn 0,0,{20 + k * 90} chamfer 0.4")
        mat(WALNUT)

section("Pennant and port and starboard lamps")
pipe([(-34, 0, GZ), (-34, 0, GZ + 14)], 0.5)
mat(BRASS)
add(f"wedge {p(-38, 0, GZ + 12)} 8,0.6,5 top 1,0.4 shift -3.5,0")
mat(RED)
add(f"lamp {p(10, 13.5, GZ - 3)} r 1.1")
mat("#d23b2b")
add(f"lamp {p(10, -13.5, GZ - 3)} r 1.1")
mat("#2fa35a")

section("Display base: walnut plinth, brass mooring mast and nameplate")
lathe_x([(0, 0), (54, 0), (56, 2), (56, 6), (52, 9), (0, 9)], 0, 0, 0, WALNUT, aim="0,0,1")
lathe_x([(0, 0), (10, 0), (9, 2), (6, 4), (0, 4)], 0, 0, 9, BRASS, aim="0,0,1")
pipe([(0, 0, 12), (0, 0, GZ - 15)], 2.6)
mat(BRASS)
lathe_x([(0, 0), (4.5, 0), (4.5, 3), (2.8, 4.5), (0, 4.5)], 0, 0, GZ - 19, BRASS, aim="0,0,1")
pipe([(0, 0, GZ - 15), (0, 0, GZ - 13)], 2)
mat(BRASS)
add(f"box {p(0, -47, 5)} 30,3,6 chamfer 0.6 turn 0,0,0")
mat(BRASS)

open(OUT, "w").write("\n".join(C) + "\n")
print(f"wrote {OUT}: {len(C)} lines")

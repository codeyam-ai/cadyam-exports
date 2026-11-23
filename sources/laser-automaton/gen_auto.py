#!/usr/bin/env python3
"""The Pecking Bird: a laser-cut automaton for CadYam Laser & CNC Cutting.

A finger-jointed birch box is the frame. A crank turns a shaft through it; two
cams on the shaft lift two followers, one nodding the bird's head to peck and
one flapping its wing. Every part is a cut outline on 3 mm birch, with the
details engraved: the cam profiles, gear teeth, the bird's feathers and eye,
and the maker's plate on the box front.

Millimetres. Writes auto.cadyam.
"""
import math, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "auto.cadyam"
C = []


def f(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def add(*lines):
    C.extend(lines)


def section(t):
    add(f"# === {t} ===")


def poly(pts, name, op="cut"):
    add("polyline " + " ".join(f"{f(x)},{f(y)}" for x, y in pts) + " close", f"set last name {name}")
    if op != "cut":
        add(f"op {op} last")


def circle(x, y, r, name=None, op="cut"):
    add(f"circle {f(x)},{f(y)} r {f(r)}")
    if name:
        add(f"set last name {name}")
    if op != "cut":
        add(f"op {op} last")


add("app cutting", "units mm", "sheet birch_3mm", "kerf 0.15mm", "gap 3mm")

section("The frame: a finger-jointed open box the mechanism sits in")
add("box 120x70x80mm open at 0,0")

ox = 0.0  # parts are laid out to the right, then nested


def gear(cx, cy, R, teeth, name, hole=2.6):
    pts = []
    for k in range(teeth * 4):
        a = 2 * math.pi * k / (teeth * 4)
        phase = k % 4
        r = R + 1.6 if phase in (1, 2) else R - 1.2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    poly(pts, name)
    circle(cx, cy, hole)
    # spokes engraved for show
    for k in range(5):
        a = 2 * math.pi * k / 5
        add(f"line {f(cx + (hole + 1.5) * math.cos(a))},{f(cy + (hole + 1.5) * math.sin(a))} "
            f"{f(cx + (R - 4) * math.cos(a))},{f(cy + (R - 4) * math.sin(a))}", "op engrave last")


def cam(cx, cy, name, lobes=1, lift=9, base=12):
    pts = []
    for k in range(120):
        a = 2 * math.pi * k / 120
        bump = max(0.0, math.cos(lobes * a)) ** 2
        r = base + lift * bump
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    poly(pts, name)
    circle(cx, cy, 2.6)


section("Two cams for the shaft: a single lobe to peck, a double lobe to flap")
cam(200, 40, "Peck cam", 1)
cam(250, 40, "Flap cam", 2, lift=6)
section("Drive gears: crank gear and shaft gear")
gear(200, 100, 16, 24, "Crank gear")
gear(250, 100, 10, 15, "Shaft gear")

section("The crank: an arm and a turned handle")
poly([(185, 140), (225, 140), (228, 143), (225, 146), (185, 146), (182, 143)], "Crank arm")
circle(186, 143, 1.6)
circle(223, 143, 1.6)
circle(240, 143, 5, "Crank handle disc")
circle(240, 143, 1.6)

section("Followers: round-footed rods that ride the cams")
for i, (x, name) in enumerate(((290, "Peck follower"), (305, "Flap follower"))):
    poly([(x, 20), (x + 6, 20), (x + 6, 95), (x + 3, 99), (x, 95)], name)
    circle(x + 3, 26, 5, f"{name} foot")

section("The bird: body, nodding head and a flapping wing, feathers engraved")
body = []
for k in range(60):
    a = 2 * math.pi * k / 60
    body.append((380 + 34 * math.cos(a) * (1 + 0.15 * math.cos(a)), 60 + 18 * math.sin(a)))
poly(body, "Bird body")
circle(380, 60, 1.6)
head = []
for k in range(40):
    a = 2 * math.pi * k / 40
    head.append((440 + 14 * math.cos(a), 70 + 13 * math.sin(a)))
head = head[:5] + [(462, 66), (474, 62), (462, 60)] + head[5:]
poly(head, "Bird head and beak")
circle(436, 70, 1.6)
circle(445, 74, 2.2, "Eye", op="engrave")
wing = [(360, 110), (420, 104), (432, 112), (414, 120), (396, 126), (376, 126), (360, 118)]
poly(wing, "Wing")
for k in range(5):
    x = 372 + k * 10
    add(f"arc {f(x)},{f(118)} {f(x + 8)},{f(112)} {f(x + 16)},{f(118)}", "op engrave last")
for k in range(4):
    x = 360 + k * 12
    add(f"arc {f(x)},{f(64)} {f(x + 6)},{f(58)} {f(x + 12)},{f(64)}", "op engrave last")

section("Perch, shaft spacers and the maker's plate")
poly([(360, 150), (470, 150), (470, 158), (360, 158)], "Perch")
for k in range(6):
    circle(500 + (k % 3) * 14, 30 + (k // 3) * 14, 5, f"Spacer {k + 1}")
    circle(500 + (k % 3) * 14, 30 + (k // 3) * 14, 2.6)
add('text "THE PECKING BIRD" 60,-8 6mm align centre')

# nest overlaps small parts with box panels (see plan); laid out by hand instead
# Lay the mechanism's parts out on a band above the box's panels, which the
# box command spreads along y = 0..80.
import re as _re
DX, DY = -170.0, 120.0
def _shift(line):
    if not line.startswith(("polyline ", "circle ", "line ", "arc ", "text ")):
        return line
    return _re.sub(r"(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)",
                   lambda m: f"{f(float(m.group(1)) + DX)},{f(float(m.group(2)) + DY)}", line)
C[:] = [_shift(l) for l in C]
open(OUT, "w").write("\n".join(C) + "\n")
print(f"wrote {OUT}: {len(C)} lines")

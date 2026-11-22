#!/usr/bin/env python3
"""The Mount Lebanon Rocker: a Shaker ladder-back rocking chair for CadYam Woodworking.

Every part is drawn in the front view and the end (side) view with the same
part id, so the piece assembles in 3D and the cut list, stock and joints come
from the drawing: cherry posts, rails and rockers, three arched back slats,
mushroom-capped arms, and a woven tape seat.

Inches. Front view at x 0..21; end (side) view drawn at x 40.. (EX), depth
running front (left) to back (right). Writes chair.cadyam.
"""
import math, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "chair.cadyam"
SPECIES = sys.argv[2] if len(sys.argv) > 2 else "maple"
C = []
EX = 40.0  # where the end view starts


def f(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def add(*lines):
    C.extend(lines)


def section(t):
    add(f"# === {t} ===")


def board(x0, y0, x1, y1, pid, part, view, thick, species=None, extra=""):
    sp = species or SPECIES
    add(f"board {f(x0)},{f(y0)} {f(x1)},{f(y1)} stock Custom thickness {f(thick)} species {sp} "
        f"part {part} part_id {pid} view {view}" + (f" {extra}" if extra else ""))


def curved(pts, pid, part, view, thick, species=None):
    """A board cut to a curved outline: a closed polyline made into a board."""
    sp = species or SPECIES
    add("polyline " + " ".join(f"{f(x)},{f(y)}" for x, y in pts) + " close",
        "make board last",
        f"set last stock Custom thickness {f(thick)} species {sp} part {part} part_id {pid} view {view}")


def both(front, end, pid, part, thick, species=None, extra=""):
    """A straight part drawn in both views: front=(x0,y0,x1,y1), end=(d0,y0,d1,y1) in depth."""
    board(*front, pid, part, "Front", thick, species, extra)
    d0, ey0, d1, ey1 = end
    board(EX + d0, ey0, EX + d1, ey1, pid, part, "End", thick, species, extra)


W = 20.0       # outside width at the front posts
SEAT = 15.0    # seat height above the rocker tops
POST = 1.5     # post thickness
FRONT_D, BACK_D = 3.5, 19.0  # front and back post positions along the depth
LIFT = 3.0     # posts stand on the rockers' tops

add("units imperial")

section("Rockers: a long cherry arc under each side, the posts let into them")
R, L = 44.0, 32.0   # rocker radius and length
def rocker_outline():
    pts = []
    half = math.asin((L / 2) / R)
    for i in range(25):
        a = -half + 2 * half * i / 24
        pts.append((EX + 11.25 + R * math.sin(a), R - R * math.cos(a)))
    top = []
    for i in range(25):
        a = half - 2 * half * i / 24
        rr = R - 2.6 + 1.0 * (abs(a) / half) ** 4   # tapers smoothly toward the tips
        top.append((EX + 11.25 + rr * math.sin(a), R - rr * math.cos(a) + (R - rr) - 0.0))
    # a gentle swell under the posts, tapering to the tips
    out = pts + [(x, y + 0.1) for x, y in top]
    return out
for pid, part, x in (("RL", "Left Rocker", 0.75), ("RR", "Right Rocker", W - 1.75)):
    # The front view must be as tall as the curved outline: the 3D part is
    # where the two views agree, so a 3" board cut the arc's top off flat.
    top = max(y for _, y in rocker_outline())
    board(x, 0, x + 1.0, top, pid, part, "Front", 1.0)
    curved(rocker_outline(), pid, part, "End", 1.0)

section("Turned posts: two front posts to the arms, two tall back posts with finials")
for pid, part, x in (("FL", "Left Front Post", 0.5), ("FR", "Right Front Post", W - 2.0)):
    both((x, LIFT, x + POST, 25.5), (FRONT_D, LIFT, FRONT_D + POST, 25.5), pid, part, POST)
    # a mushroom cap where the arm meets the post
    both((x - 0.25, 25.5, x + POST + 0.25, 26.6), (FRONT_D - 0.25, 25.5, FRONT_D + POST + 0.25, 26.6),
         pid + "C", part.replace("Post", "Mushroom Cap"), POST + 0.5)
for pid, part, x in (("BL", "Left Back Post", 0.75), ("BR", "Right Back Post", W - 2.25)):
    both((x, LIFT, x + POST, 44.0), (BACK_D, LIFT, BACK_D + POST, 44.0), pid, part, POST)
    both((x + 0.1, 44.0, x + POST - 0.1, 46.2), (BACK_D + 0.1, 44.0, BACK_D + POST - 0.1, 46.2),
         pid + "F", part.replace("Back Post", "Finial"), POST - 0.2)

section("Arms from the front posts back to the back posts")
for pid, part, x in (("AL", "Left Arm", 0.25), ("AR", "Right Arm", W - 2.25)):
    both((x, 24.5, x + 2.0, 25.5), (FRONT_D - 0.5, 24.5, BACK_D + 0.5, 25.5), pid, part, 2.0)

section("Seat rails, and the woven tape seat over them")
both((POST + 0.5, SEAT - 1.0, W - POST - 0.5, SEAT), (FRONT_D, SEAT - 1.0, FRONT_D + POST, SEAT),
     "SF", "Front Seat Rail", 1.0, extra="joint Dado joint_depth 0.75")
both((POST + 0.75, SEAT - 1.0, W - POST - 0.75, SEAT), (BACK_D, SEAT - 1.0, BACK_D + POST, SEAT),
     "SB", "Back Seat Rail", 1.0, extra="joint Dado joint_depth 0.75")
for pid, part, x in (("SL", "Left Seat Rail", 0.75), ("SR", "Right Seat Rail", W - 1.75)):
    both((x, SEAT - 1.0, x + 1.0, SEAT), (FRONT_D + POST, SEAT - 1.0, BACK_D, SEAT), pid, part, 1.0,
         extra="joint Dado joint_depth 0.75")
both((1.25, SEAT, W - 1.25, SEAT + 0.4), (FRONT_D + 0.2, SEAT, BACK_D + 0.8, SEAT + 0.4),
     "TS", "Woven Tape Seat", 0.4, species="#3f5f7a")

section("Stretchers low between the posts")
both((POST + 0.5, 7.5, W - POST - 0.5, 8.25), (FRONT_D + 0.4, 7.5, FRONT_D + 1.1, 8.25), "XF", "Front Stretcher", 0.75)
for pid, part, x, y in (("XL", "Left Stretcher", 1.0, 6.0), ("XR", "Right Stretcher", W - 1.75, 6.0),
                        ("XL2", "Left Upper Stretcher", 1.0, 10.0), ("XR2", "Right Upper Stretcher", W - 1.75, 10.0)):
    both((x, y, x + 0.75, y + 0.75), (FRONT_D + POST, y, BACK_D, y + 0.75), pid, part, 0.75)
both((POST + 0.75, 7.0, W - POST - 0.75, 7.75), (BACK_D + 0.4, 7.0, BACK_D + 1.1, 7.75), "XB", "Back Stretcher", 0.75)

section("Three arched back slats, graduated, between the back posts")
for i, (y, h, rise) in enumerate(((29.0, 2.6, 0.5), (34.0, 2.9, 0.6), (39.0, 3.2, 0.7))):
    x0, x1 = POST + 0.75, W - POST - 0.75
    pts = []
    for k in range(17):
        t = k / 16
        pts.append((x0 + (x1 - x0) * t, y + rise * math.sin(math.pi * t)))
    for k in range(17):
        t = 1 - k / 16
        pts.append((x0 + (x1 - x0) * t, y + h + rise * math.sin(math.pi * t)))
    curved(pts, f"S{i + 1}", f"Back Slat {i + 1}", "Front", 0.375)
    board(EX + BACK_D + 0.55, y, EX + BACK_D + 0.925, y + h + rise, f"S{i + 1}", f"Back Slat {i + 1}", "End", 0.375)

open(OUT, "w").write("\n".join(C) + "\n")
print(f"wrote {OUT}: {len(C)} lines")

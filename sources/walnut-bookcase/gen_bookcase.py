#!/usr/bin/env python3
"""The Roycroft Bookcase: an Arts & Crafts oak bookcase for CadYam Woodworking.

Two thick oak sides with the shelves let into dados, a bottom shelf that runs
through the sides as tenons, a top that overhangs on three sides, a kick rail
under the bottom shelf, a top rail, and a back of narrow tongue-and-groove
boards in a rabbet. Every part is drawn in the front view and the end view with
the same part id, so it assembles in 3D with its cut list, stock and joints.

Inches. Front view at x 0..W; end view drawn at x EX.., depth running front
(left) to back (right). Writes bookcase.cadyam.
"""
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "bookcase.cadyam"
SP = sys.argv[2] if len(sys.argv) > 2 else "oak"
C = []
EX = 50.0

W, D, H = 36.0, 12.0, 54.0   # carcase width, depth, height (sides)
T = 0.875                    # side and shelf thickness
TOP_T, TOP_OVER = 1.0, 1.0   # top thickness and overhang


def f(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def board(x0, y0, x1, y1, pid, part, view, thick, extra=""):
    C.append(f"board {f(x0)},{f(y0)} {f(x1)},{f(y1)} stock Custom thickness {f(thick)} species {SP} "
             f"part {part} part_id {pid} view {view}" + (f" {extra}" if extra else ""))


def both(front, end, pid, part, thick, extra=""):
    board(*front, pid, part, "Front", thick, extra)
    d0, y0, d1, y1 = end
    board(EX + d0, y0, EX + d1, y1, pid, part, "End", thick, extra)


C.append("units imperial")

# Sides: full height, full depth, standing on the floor.
for pid, part, x in (("SL", "Left Side", 0.0), ("SR", "Right Side", W - T)):
    both((x, 0, x + T, H), (0, 0, D, H), pid, part, T)

# Shelves let into the sides in 3/8" dados; the bottom shelf tenons through.
inner0, inner1 = T, W - T
shelves = [(4.0, "B", "Bottom Shelf", "joint mortise joint_depth 0.875"),
           (16.5, "S1", "Lower Shelf", "joint Dado joint_depth 0.375"),
           (28.5, "S2", "Middle Shelf", "joint Dado joint_depth 0.375"),
           (40.5, "S3", "Upper Shelf", "joint Dado joint_depth 0.375")]
for y, pid, part, joint in shelves:
    both((inner0, y, inner1, y + T), (0.5, y, D - 0.25, y + T), pid, part, T, joint)

# Kick rail under the bottom shelf, set back 1/2", with a shallow arch cut
# out of its lower edge (the front view's outline; the end view stays full
# height so the 3D part keeps the arch).
import math
arch = [(inner0, 4.0), (inner1, 4.0), (inner1, 0.75)]
for i in range(1, 24):
    t = i / 24
    x = inner1 - t * (inner1 - inner0)
    arch.append((x, 0.75 + 1.75 * math.sin(math.pi * t)))
arch.append((inner0, 0.75))
C.append("polyline " + " ".join(f"{f(x)},{f(y)}" for x, y in arch) + " close")
C.append("make board last")
C.append(f"set last stock Custom thickness {f(T)} species {SP} part Kick Rail part_id K view Front joint mortise joint_depth 0.75")
board(EX + 0.5, 0.75, EX + 1.375, 4.0, "K", "Kick Rail", "End", T, "joint mortise joint_depth 0.75")

# Through-tenons: the bottom shelf's tenons stand 3/4" proud of each side,
# two per side, the Arts & Crafts tell.
for side, (x0, x1) in (("L", (-0.75, 0.0)), ("R", (W, W + 0.75))):
    for k, (d0, d1) in enumerate(((1.5, 4.0), (D - 4.0, D - 1.5))):
        both((x0, 4.0, x1, 4.0 + T), (d0, 4.0, d1, 4.0 + T), f"TN{side}{k}", f"Through Tenon {side}{k+1}", 0.75)

# Top rail under the top, across the front.
both((inner0, H - 2.5, inner1, H), (0.5, H - 2.5, 1.375, H), "TR", "Top Rail", T,
     "joint mortise joint_depth 0.75")

# Top: overhangs front and both ends, flush at the back, breadboarded ends.
both((-TOP_OVER, H, W + TOP_OVER, H + TOP_T), (-TOP_OVER, H, D, H + TOP_T), "TP", "Top", TOP_T,
     "joint Breadboard")

# Back: seven tongue-and-groove boards in a rabbet in the sides.
n = 7
bw = (W - 2 * T + 0.75) / n
for i in range(n):
    x0 = T - 0.375 + i * bw
    both((x0, 0.75, x0 + bw, H), (D - 0.25, 0.75, D, H), f"BK{i+1}", f"Back Board {i+1}", 0.5,
         "joint Rabbet joint_depth 0.375")

with open(OUT, "w") as fh:
    fh.write("\n".join(C) + "\n")
print(f"wrote {OUT}: {len(C)} lines")

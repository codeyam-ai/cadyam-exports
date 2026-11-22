#!/usr/bin/env python3
"""The Staunton Set: a printable chess set for CadYam Forms.

Six Staunton-pattern pieces (king, queen, bishop, rook, knight, pawn), each
turned from one profile, standing on a flat felt-sized base so it prints with
no supports: every overhang under 45 degrees, every feature at least 1 mm.
A full set is laid out on an inlaid board — walnut and maple — with white
pieces in maple PLA tones and black in walnut, and each piece type is also a
print part for the plate.

Millimetres. King height 64 mm (a "tournament" set at about 2/3 scale).
Writes chess.cadyam.
"""
import math, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "chess.cadyam"
C = []
NOBJ = 0
MAKERS = ("lathe ", "box ", "cylinder ", "torus ", "sphere ", "pipe ", "capsule ", "wedge ", "cone ", "group ")  # a group is a new object too


def f(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def p(x, y, z):
    return f"{f(x)},{f(y)},{f(z)}"


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


SQ = 30.0  # square size
BOARD_T = 8.0
LIGHT, DARK = "#e9d6b0", "#6b4226"   # maple and walnut squares
WHITE, BLACK = "#efe4cc", "#3a2418"  # boxwood and ebonised walnut pieces


def base(r, h=3.0):
    """A stepped Staunton base: a flat foot, a bevel, a bead, then a cove up to the stem."""
    return [(0, 0), (r, 0), (r, h * 0.55), (r - 0.9, h), (r - 1.4, h + 0.9), (r - 1.0, h + 1.8),
            (r - 2.2, h + 2.6)]


# Each profile runs from the axis at the foot (z = 0) up to the axis at the top.
# Overhangs: every step outward going up is at most 45 degrees.
def king():
    b = base(13)
    return b + [(6.0, 12), (4.4, 26), (4.2, 34), (7.4, 37), (7.6, 38.8), (4.6, 40), (4.2, 42),
                (6.6, 47), (7.0, 49.5), (5.8, 51), (3.6, 52), (0, 52)]


def queen():
    b = base(12.5)
    return b + [(5.8, 11.5), (4.2, 24), (4.0, 31), (7.0, 33.8), (7.2, 35.4), (4.4, 36.6), (4.0, 38.5),
                (6.8, 44), (7.2, 46.5), (5.6, 47.6), (3.0, 48.5), (2.6, 49.5), (2.9, 51.5), (0, 53)]


def bishop():
    b = base(11)
    return b + [(5.2, 10.5), (3.6, 20), (3.4, 25), (6.2, 27.2), (6.4, 28.6), (3.8, 29.6), (4.8, 31.5),
                (6.0, 35.5), (5.6, 39), (3.8, 42.5), (2.0, 44), (2.4, 45.2), (2.4, 46.6), (0, 47.4)]


def rook():
    b = base(12)
    return b + [(7.4, 11.5), (6.0, 20), (6.0, 24), (8.2, 27), (8.6, 29), (8.6, 34), (6.6, 34), (6.6, 32), (0, 32)]


def pawn():
    b = base(9.5, 2.6)
    return b + [(4.2, 8.5), (3.0, 14), (5.4, 16.2), (5.6, 17.4), (3.4, 18.4), (3.2, 19.4),
                (4.8, 21.5), (5.2, 24.0), (4.6, 26.5), (2.6, 28.4), (0, 28.9)]


def printable(prof):
    """Keep every outward step going up at 44 degrees or steeper (no overhang over 45):
    where a step widens faster than it rises, lift it and everything above it."""
    out = [prof[0]]
    lift = 0.0
    for (r0, z0), (r1, z1) in zip(prof, prof[1:]):
        dz, dr = z1 - z0, r1 - r0
        if dz > 0 and dr > 0 and dr > dz * 0.97:
            lift += dr / 0.97 - dz
        out.append((r1, z1 + lift))
    return out


def turned(prof, x, y, m):
    prof = printable(prof)
    add("lathe " + " ".join(f"{f(r)},{f(z)}" for r, z in prof) + f" at {p(x, y, BOARD_T)} aim 0,0,1")
    mat(m)


def king_cross(x, y, m):
    z = BOARD_T + 52
    add(f"box {p(x, y, z + 4.5)} 2.6,2.6,9 radius 0.4")
    mat(m)
    add(f"box {p(x, y, z + 5.4)} 8,2.6,2.6 radius 0.4")
    mat(m)


def queen_crown(x, y, m):
    z = BOARD_T + 46.5
    for k in range(8):
        a = 2 * math.pi * k / 8
        add(f"sphere {p(x + 6.0 * math.cos(a), y + 6.0 * math.sin(a), z + 0.6)} r 1.3")
        mat(m)
    add(f"sphere {p(x, y, BOARD_T + 54)} r 1.9")
    mat(m)


def bishop_mitre_cut(x, y, facing):
    """The bishop's slit: a 1.2 mm cut across the mitre, angled up."""
    add(f"box {p(x, y, BOARD_T + 40.5)} 14,1.4,3.2 turn {facing},0,35")
    add("subtract last")


def rook_crenels(x, y):
    for k in range(4):
        a = 45 * k
        add(f"box {p(x, y, BOARD_T + 33.5)} 20,2.4,3.4 turn {a},0,0")
        add("subtract last")


def knight(x, y, m, facing):
    """A Staunton knight built up from tapered blocks: neck, head, muzzle, ears and mane,
    all leaning forward under 45 degrees so it prints standing."""
    first = NOBJ + 1
    turned(base(12) + [(6.4, 11), (5.6, 12.5), (0, 12.5)], x, y, m)
    z0 = BOARD_T + 12.0
    a = math.radians(facing)
    fx, fy = math.cos(a), math.sin(a)

    def at(fw, up, side=0.0):
        return (x + fx * fw - fy * side, y + fy * fw + fx * side, z0 + up)

    # neck: a tall wedge leaning forward
    add(f"box {p(*at(-0.5, 9))} 10,8,18 radius 2 turn {facing},0,-14")
    mat(m)
    # head: rises and leans further forward
    add(f"box {p(*at(3.2, 20))} 9,7.6,10 radius 2.2 turn {facing},0,-32")
    mat(m)
    # muzzle reaching forward and down (bottom face slopes 40 degrees)
    add(f"box {p(*at(8.4, 19.2))} 9,6.6,6 radius 2 turn {facing},0,40")
    mat(m)
    # ears
    for s in (-1, 1):
        add(f"cone {p(*at(-0.4, 26.6, s * 2.0))} r 1.7,0.9 h 4.2")
        mat(m)
    # eyes: small domes, raised rather than cut
    for s_ in (-1, 1):
        add(f"sphere {p(*at(4.2, 22.4, s_ * 3.7))} r 0.8")
        mat(m)
    # mane: a ridge of beads down the back of the neck
    for k in range(7):
        t = k / 6
        add(f"sphere {p(*at(-5.2 + t * 2.0, 26 - t * 13))} r 1.6")
        mat(m)
    add("group " + " ".join(str(i) for i in range(first, NOBJ + 1)))
    mat(m)


PIECE = {"K": king, "Q": queen, "B": bishop, "R": rook, "P": pawn}


def piece(kind, col, row, colour):
    x, y = (col - 3.5) * SQ, (row - 3.5) * SQ
    facing = 90 if colour == WHITE else -90
    if kind == "N":
        knight(x, y, colour, facing)
        return
    first = NOBJ + 1
    turned(PIECE[kind](), x, y, colour)
    if kind == "K":
        king_cross(x, y, colour)
    elif kind == "Q":
        queen_crown(x, y, colour)
    elif kind == "B":
        # the mitre's slit as a raised band, not a cut: cuts leave walls too thin to print
        add(f"torus {p(x, y, BOARD_T + 38.2)} 5.6,0.6 turn 0,35,0")
        mat(colour)
    elif kind == "R":
        rook_crenels(x, y)
    if NOBJ > first:
        add("group " + " ".join(str(i) for i in range(first, NOBJ + 1)))
        mat(colour)


add("app forms", "units mm", "form detail fine", "material form plain")

if len(sys.argv) > 2 and sys.argv[2] == "plate":
    # One of each piece on the bed, for printing: no board, feet at z = 0.
    BOARD_T = 0.0
    section("One of each piece, standing on the print bed")
    for i, k in enumerate("KQBNRP"):
        x0 = (i - 2.5) * 32.0
        col, row = x0 / SQ + 3.5, 3.5
        piece(k, col, row, WHITE)
        add(f"part {k.lower()}piece last", f"part {k.lower()}piece orient upright")
    open(OUT, "w").write("\n".join(C) + "\n")
    print(f"wrote {OUT}: {len(C)} lines (print plate)")
    sys.exit(0)

section("An inlaid board: walnut and maple squares in a walnut frame with a boxwood line")
add(f"box {p(0, 0, BOARD_T / 2 - 0.5)} {f(8 * SQ + 26)},{f(8 * SQ + 26)},{f(BOARD_T - 1)} radius 2")
mat("walnut")
add(f"box {p(0, 0, BOARD_T - 0.7)} {f(8 * SQ + 6)},{f(8 * SQ + 6)},1.2")
mat("#d9c49a")
for r in range(8):
    for c in range(8):
        add(f"box {p((c - 3.5) * SQ, (r - 3.5) * SQ, BOARD_T - 0.35)} {f(SQ)},{f(SQ)},0.8")
        mat(LIGHT if (r + c) % 2 else DARK)

BACK = "RNBQKBNR"
section("White: boxwood")
for c, k in enumerate(BACK):
    piece(k, c, 0, WHITE)
for c in range(8):
    piece("P", c, 1, WHITE)
section("Black: ebonised walnut")
for c, k in enumerate(BACK):
    piece(k, c, 7, BLACK)
for c in range(8):
    piece("P", c, 6, BLACK)

open(OUT, "w").write("\n".join(C) + "\n")
print(f"wrote {OUT}: {len(C)} lines, {NOBJ} solids")

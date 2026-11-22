#!/usr/bin/env python3
"""The Aurora Pendant: a sapphire-and-diamond halo pendant on a fine platinum cable chain,
draped over a walnut display stand. For CadYam Forms.

Millimetres. X across, Z up; the pendant faces the viewer at -Y. Writes necklace.cadyam.
"""
import math, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "necklace.cadyam"
C = []


def f(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def p(x, y, z):
    return f"{f(x)},{f(y)},{f(z)}"


def add(*lines):
    C.extend(lines)


def section(t):
    add(f"# === {t} ===")


def mat(m):
    add(f"material last {m}")


def lathe(prof, at, aim, m):
    add("lathe " + " ".join(f"{f(r)},{f(a)}" for r, a in prof) + f" at {p(*at)} aim {aim}")
    mat(m)


PLAT, DIAMOND, WALNUT = "platinum", "diamond", "soft_touch"
add("app forms", "units mm", "form detail fine", "material form plain")

# ------------------------------------------------------------------ pendant
PZ = 0.0  # centre of the sapphire
CS = 7.0  # centre stone diameter
NM = 0


def brilliant(cx, gy, cz, d, gem):
    """A real round brilliant (57 flat facets) facing the viewer (-Y), its girdle at y = gy."""
    add(f"gem round {p(cx, gy, cz)} {f(d)} aim 0,-1,0")
    mat(gem)


section("Centre stone: a 7 mm round brilliant sapphire, facing the viewer")
brilliant(0, -0.95, PZ, CS, "sapphire")


def small_stone(cx, cz, d):
    brilliant(cx, -0.5, cz, d, DIAMOND)


section("Platinum basket and four claw prongs")
lathe([(2.6, 0), (3.75, 0), (3.75, 1.4), (3.35, 2.6), (2.6, 2.6)], (0, 1.9, PZ), "0,-1,0", PLAT)
for k in range(4):
    a = math.radians(45 + 90 * k)
    ca, sa = math.cos(a), math.sin(a)
    add("pipe " + " ".join(p(rr * ca, y, PZ + rr * sa) for rr, y in ((3.0, 1.6), (3.75, 0.2), (3.6, -1.0), (3.15, -1.45)))
        + " r 0.38 bend 0.8")
    mat(PLAT)
    add(f"sphere {p(3.12 * ca, -1.5, PZ + 3.12 * sa)} r 0.45")
    mat(PLAT)

section("Halo: eighteen pavé diamonds in a beaded platinum frame")
HR, HS = 5.15, 1.3
lathe([(HR - 0.95, 0), (HR + 0.95, 0), (HR + 0.9, 1.2), (HR - 0.9, 1.2)], (0, -0.3, PZ), "0,1,0", PLAT)
for k in range(18):
    a = math.radians(k * 20 + 10)
    small_stone(HR * math.cos(a), PZ + HR * math.sin(a), HS)
for k in range(18):
    a = math.radians(k * 20)
    add(f"sphere {p(HR * math.cos(a), -0.42, PZ + HR * math.sin(a))} r 0.3")
    mat(PLAT)
for rr in (HR - 0.95, HR + 0.95):
    n = int(2 * math.pi * rr / 0.6)
    for k in range(n):
        a = 2 * math.pi * k / n
        add(f"sphere {p(rr * math.cos(a), -0.36, PZ + rr * math.sin(a))} r 0.24")
        mat(PLAT)

section("Bail: a diamond-set loop the chain runs through")
BZ = PZ + HR + 0.95 + 2.6
add(f"torus {p(0, 0.5, BZ)} 2.2,0.6 turn 0,90,0")  # ring in the Y-Z plane, so the chain threads it
mat(PLAT)
lathe([(0.55, -0.8), (0.75, 0), (0.55, 0.8)], (0, 0.5, PZ + HR + 1.0), "0,0,1", PLAT)  # the neck joining bail and halo

# ------------------------------------------------------------------ stand
section("A walnut T-bar display stand")
SX, SZ = 18.0, 38.0  # half-span of the crossbar, its height above the pendant
FOOT = -16.0
add(f"cylinder {p(0, 9, FOOT - 1.5)} r 13 h 3")
mat(WALNUT)
add(f"cylinder {p(0, 9, (FOOT + SZ) / 2)} r 1.6 h {f(SZ - FOOT)}")
mat(WALNUT)
add(f"cylinder {p(0, 9, SZ)} r 1.8 h {f(2 * SX + 7)} turn 0,90,0")
mat(WALNUT)
for s in (-1, 1):
    add(f"sphere {p(s * (SX + 3.5), 9, SZ)} r 2.2")
    mat(WALNUT)

# ------------------------------------------------------------------ chain
section("Fine platinum cable chain: round links, each turned a quarter to the next")
LR, LT = 0.95, 0.24  # link ring radius, wire radius
PITCH = 2 * (LR - LT) + 0.02


def drape(x0, z0, x1, z1, sag, n=400):
    """A hanging curve from (x0,z0) to (x1,z1), sagging `sag` below the lower end."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        z = z0 + (z1 - z0) * t - sag * math.sin(math.pi * t) ** 1.15
        pts.append((x, z))
    return pts


def links_along(pts, y, start_flat=True, y_at=None):
    """Round links every PITCH along the polyline, alternating flat and upright."""
    out, acc, k = [], 0.0, 0
    (px, pz) = pts[0]
    need = 0.0
    for (x, z) in pts[1:]:
        seg = math.hypot(x - px, z - pz)
        while acc + seg >= need:
            t = (need - acc) / seg if seg else 0
            cx, cz = px + (x - px) * t, pz + (z - pz) * t
            th = math.degrees(math.atan2(z - pz, x - px))
            flat = (k % 2 == 0) == start_flat
            y = y_at(cz) if y_at else y
            if flat:  # ring containing the chain's direction and Y
                out.append(f"torus {p(cx, y, cz)} {f(LR)},{f(LT)} turn 0,{f(-th)},0")
            else:  # ring in the front plane
                out.append(f"torus {p(cx, y, cz)} {f(LR)},{f(LT)} turn 0,0,90")
            k += 1
            need += PITCH
        acc += seg
        px, pz = x, z
    return out


# Two strands from the bail up to rings looped round the crossbar near its
# ends: the bar is 9 mm behind the pendant, so each strand slopes back to it.
BY, BR = 9.0, 1.8  # the crossbar's y and radius
HANG_R = BR + 0.55  # a hanging ring just bigger than the bar
Y0, Z0 = 0.5, BZ + 1.2
for s in (-1, 1):
    hx = s * (SX - 1.0)
    # the ring round the bar, standing in the Y-Z plane
    add(f"torus {p(hx, BY, SZ)} {f(HANG_R)},{f(LT + 0.06)} turn 0,90,0")
    mat(PLAT)
    # the strand ends at the ring's lowest, front-most point
    ty, tz = BY - HANG_R * 0.7, SZ - HANG_R * 0.7
    pts = drape(0.0, Z0, hx, tz, 0.0)
    bowed = []
    for i, (x, z) in enumerate(pts):
        t = i / (len(pts) - 1)
        bowed.append((x + s * 3.0 * math.sin(math.pi * t) * (1 - t), z))
    y_at = lambda z, ty=ty, tz=tz: Y0 + (ty - Y0) * max(0.0, min(1.0, (z - Z0) / (tz - Z0)))
    for line in links_along(bowed, Y0, y_at=y_at):
        add(line)
        mat(PLAT)

open(OUT, "w").write("\n".join(l for l in C if l) + "\n")
print(f"wrote {OUT}: {len(C)} lines")

#!/usr/bin/env python3
"""The Aurora Bridal Set: a halo engagement ring and a matching pavé wedding band, for CadYam Forms.

Millimetres. The finger passes along the Y axis through the origin; Z is up, so the ring
stands upright with its centre stone at the top. Ring size is a parameter of the generator
(US size -> inner diameter = 11.63 + 0.8128 * size). Writes rings.cadyam.
"""
import math, sys

SIZE = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
OUT = sys.argv[1] if len(sys.argv) > 1 else "rings.cadyam"
R = (11.63 + 0.8128 * SIZE) / 2  # inner radius
C = []


def f(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def p(x, y, z):
    return f"{f(x)},{f(y)},{f(z)}"


def add(*lines):
    C.extend(lines)


def mat(m):
    add(f"material last {m}")


def section(t):
    add(f"# === {t} ===")


def lathe(prof, at, aim, m, extra=""):
    add("lathe " + " ".join(f"{f(r)},{f(a)}" for r, a in prof) + f" at {p(*at)} aim {aim}" + (f" {extra}" if extra else ""))
    mat(m)


def pipe(pts, r, m, extra=""):
    add("pipe " + " ".join(p(*q) for q in pts) + f" r {f(r)}" + (f" {extra}" if extra else ""))
    mat(m)


GOLD, PLAT, DIAMOND = "yellow_gold", "platinum", "diamond"
add("app forms", "units mm", "form detail fine", "material form plain")


NM = 0


def brilliant(cx, cy, cz, d, aim="0,0,1"):
    """A real round brilliant (57 flat facets) with its girdle at (cx, cy, cz), table facing `aim`."""
    add(f"gem round {p(cx, cy, cz)} {f(d)} aim {aim}")
    mat(DIAMOND)


# ------------------------------------------------------------------ engagement ring
section("Engagement ring: a comfort-fit yellow-gold band that tapers toward the head")
BW, BT = 2.1, 1.7  # band width along the finger, thickness
prof = [(R + 0.05, -BW / 2), (R + BT - 0.35, -BW / 2), (R + BT, -BW / 2 + 0.4), (R + BT + 0.05, 0),
        (R + BT, BW / 2 - 0.4), (R + BT - 0.35, BW / 2), (R + 0.05, BW / 2), (R - 0.08, 0.5), (R - 0.08, -0.5)]
lathe(prof, (0, 0, 0), "0,1,0", GOLD)

TOP = R + BT  # outer radius at the top of the band
CS = 6.5  # centre stone diameter (about 1 ct)
GZ = TOP + 4.6  # girdle height of the centre stone

section("Cathedral shoulders sweeping up to a platinum head")
for s in (1, -1):
    for side in (1, -1):
        a0, a1 = math.radians(40), math.radians(12)
        pts = []
        for k in range(7):
            t = k / 6
            a = a0 + (a1 - a0) * t
            rad = TOP - 0.55 + 3.4 * t ** 1.8
            pts.append((s * rad * math.sin(a), side * (0.42 + 0.12 * (1 - t)), rad * math.cos(a)))
        pts.append((s * 2.0, side * 0.4, GZ - 2.4))
        pipe(pts, 0.5, PLAT, "bend 1.5")

section("Basket gallery: two rails with pierced filigree between")
lathe([(2.2, 0), (2.9, 0), (2.9, 0.55), (2.2, 0.55)], (0, 0, GZ - 3.3), "0,0,1", PLAT)
lathe([(2.9, 0), (3.5, 0), (3.5, 0.5), (2.9, 0.5)], (0, 0, GZ - 1.7), "0,0,1", PLAT)
lathe([(2.45, 0), (3.05, 0), (3.25, 1.6), (2.65, 1.6)], (0, 0, GZ - 3.3), "0,0,1", PLAT)
for k in range(12):
    a = math.radians(k * 30 + 15)
    rr = 2.95
    add(f"sphere {p(rr * math.cos(a), rr * math.sin(a), GZ - 2.5)} r 0.42")
add("subtract " + " ".join(f"last-{i}" if i else "last" for i in range(11, -1, -1)))
add("group " + " ".join(f"last-{i}" if i else "last" for i in range(12, -1, -1)))
mat(PLAT)

section("Centre stone: a 6.5 mm round brilliant held by six claw prongs")
brilliant(0, 0, GZ, CS)
for k in range(6):
    a = math.radians(k * 60 + 30)
    ca, sa = math.cos(a), math.sin(a)
    pipe([(2.7 * ca, 2.7 * sa, GZ - 3.2), (3.35 * ca, 3.35 * sa, GZ - 0.4), (3.25 * ca, 3.25 * sa, GZ + 0.55),
          (2.85 * ca, 2.85 * sa, GZ + 0.95)], 0.36, PLAT, "bend 0.8")
    add(f"sphere {p(2.8 * ca, 2.8 * sa, GZ + 0.98)} r 0.42")
    mat(PLAT)

section("Halo: sixteen micro-pavé diamonds in a beaded platinum frame")
HR, HS = 4.55, 1.25  # halo radius to stone centres, halo stone diameter
HZ = GZ - 0.6
lathe([(HR - 0.85, -0.9), (HR + 0.85, -0.9), (HR + 0.95, 0.1), (HR - 0.95, 0.1)], (0, 0, HZ - 0.35), "0,0,1", PLAT)
for k in range(16):
    a = math.radians(k * 22.5)
    brilliant(HR * math.cos(a), HR * math.sin(a), HZ, HS)
for k in range(16):
    a = math.radians(k * 22.5 + 11.25)
    add(f"sphere {p(HR * math.cos(a), HR * math.sin(a), HZ + 0.05)} r 0.3")
    mat(PLAT)
for rr in (HR - 0.92, HR + 0.92):
    n = int(2 * math.pi * rr / 0.55)
    for k in range(n):
        a = 2 * math.pi * k / n
        add(f"sphere {p(rr * math.cos(a), rr * math.sin(a), HZ - 0.25)} r 0.22")
        mat(PLAT)

section("Pavé shoulders: seven diamonds down each side of the band")
for s in (1, -1):
    for k in range(7):
        a = math.radians(s * (22 + k * 7.5))
        rr = TOP + 0.05
        cx, cz = rr * math.sin(a), rr * math.cos(a)
        brilliant(cx, 0, cz, 1.05, aim=f"{f(math.sin(a))},0,{f(math.cos(a))}")
        for side in (1, -1):
            add(f"sphere {p((rr + 0.15) * math.sin(a + s * math.radians(3.6)), side * 0.62, (rr + 0.15) * math.cos(a + s * math.radians(3.6)))} r 0.2")
            mat(GOLD)

section("Milgrain beading along both edges of the band")
for side in (1, -1):
    for k in range(84):
        a = 2 * math.pi * k / 84
        if abs(math.degrees(a) - 0) < 80 or abs(math.degrees(a) - 360) < 80:
            continue
        rr = TOP - 0.25
        add(f"sphere {p(rr * math.sin(a), side * (BW / 2 + 0.02), rr * math.cos(a))} r 0.24")
        mat(GOLD)

# ------------------------------------------------------------------ wedding band
section("Matching wedding band: a curved pavé band that nests under the halo")
WY = BW / 2 + 0.25 + 1.0  # sits beside the engagement ring along the finger
WW, WT = 2.0, 1.5
wprof = [(R + 0.05, -WW / 2), (R + WT - 0.3, -WW / 2), (R + WT, -WW / 2 + 0.35), (R + WT, WW / 2 - 0.35),
         (R + WT - 0.3, WW / 2), (R + 0.05, WW / 2), (R - 0.08, 0.45), (R - 0.08, -0.45)]
lathe(wprof, (0, WY + WW / 2, 0), "0,1,0", GOLD)
for k in range(-6, 7):
    a = math.radians(k * 8.5)
    rr = R + WT + 0.02
    brilliant(rr * math.sin(a), WY + WW / 2, rr * math.cos(a), 1.15, aim=f"{f(math.sin(a))},0,{f(math.cos(a))}")
for side in (1, -1):
    for k in range(84):
        a = 2 * math.pi * k / 84
        rr = R + WT - 0.2
        add(f"sphere {p(rr * math.sin(a), WY + WW / 2 + side * (WW / 2 + 0.02), rr * math.cos(a))} r 0.23")
        mat(GOLD)

section("Engraving: Always, inside the wedding band")
add(f'engrave "Always" on {p(0, WY + WW / 2, -(R - 0.15))} along ring y size 0.9mm depth 0.15mm')
open(OUT, "w").write("\n".join(C) + "\n")
print(f"wrote {OUT}: {len(C)} lines (US size {SIZE:g}, inner diameter {2 * R:.2f} mm)")

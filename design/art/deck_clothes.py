"""Clothes deck (衣服): 20 cards, realistic and cartoon.

    python3 deck_clothes.py [id ...]   # writes app/assets/art/cards/clothes/<id>.svg and <id>_cartoon.svg

Children's clothes laid flat (shoes and boots standing), plain colours with small simple patterns,
no logos or words. Each item is one function drawing both styles from the same outlines:
realistic (flat=False): soft gradient light, folds (soft lines), a fine weave or knit texture,
stitching and a soft floor shadow; cartoon (flat=True): the same shapes in flat bright colours.
"""
import math
import random

from kit_bc import (P, begin, clipped, curve, dk, ellipse_d, ground, hatch, lg, line, lt, mix, n, poly, rg, rim, rpoly,
                    sline, specks, spot, spline, stitch, tube, write)

DECK = "clothes"


# ---------------------------------------------------------------- shared cloth painting
def fill_of(c, box, flat):
    if flat:
        return c
    x0, y0, x1, y1 = box
    return lg([(0, lt(c, .2)), (.55, c), (1, dk(c, .14))], x0, y0, x1, y1, user=True)


def weave(box, c, op=.07, ang=(90, 0), step=2.4):
    return "".join(hatch(box, step, a, dk(c, .55) if i == 0 else lt(c, .7), op * (1 if i == 0 else .9), .5) for i, a in enumerate(ang))


def knit(box, c, op=.22, sx=8, sy=7):
    """Rows of V stitches (a knitted look) as two zigzag paths per column."""
    x0, y0, x1, y1 = box
    rows = int((y1 - y0) / sy) + 1
    zig = " ".join(f"{n(sx * .38)},{n(sy / 2)} {n(-sx * .38)},{n(sy / 2)}" for _ in range(rows))
    zag = " ".join(f"{n(-sx * .38)},{n(sy / 2)} {n(sx * .38)},{n(sy / 2)}" for _ in range(rows))
    a, b = [], []
    x = x0
    while x < x1:
        a.append(f"M{n(x)},{n(y0)}l{zig}")
        b.append(f"M{n(x + sx * .76)},{n(y0)}l{zag}")
        x += sx
    return (f'<path d="{"".join(a)}" fill="none" stroke="{dk(c, .45)}" stroke-width=".9" stroke-opacity="{op}"/>'
            f'<path d="{"".join(b)}" fill="none" stroke="{lt(c, .45)}" stroke-width=".9" stroke-opacity="{op * .9}"/>')


def cloth(d, c, box, flat, inner="", tex="weave", rim_w=7, rim_op=.3, top=""):
    """A piece of cloth: fill, then (realistic only) folds/texture inside it and a soft rim."""
    if flat:
        return P(d, c) + (clipped(d, top) if top else "")
    t = weave(box, c) if tex == "weave" else (knit(box, c) if tex == "knit" else tex or "")
    return P(d, fill_of(c, box, False)) + clipped(d, inner + t + top) + rim(d, dk(c, .5), rim_w, rim_op)


def fold(d, c, w=10, op=.25, light=False):
    return sline(d, lt(c, .45) if light else dk(c, .3), w, op)


def shadow(cx, cy, rx, ry=7, op=.18):
    return ground(cx, cy, rx, ry, op)


def star_d(cx, cy, R, r=None, rot=-90):
    r = r or R * .45
    pts = []
    for i in range(10):
        a = math.radians(rot + i * 36)
        rr = R if i % 2 == 0 else r
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return poly(pts)


def heart_d(cx, cy, s):
    return (f"M{n(cx)},{n(cy + 9 * s)} C{n(cx - 12 * s)},{n(cy + 1 * s)} {n(cx - 11 * s)},{n(cy - 9 * s)} {n(cx - 5 * s)},{n(cy - 9 * s)} "
            f"C{n(cx - 2 * s)},{n(cy - 9 * s)} {n(cx)},{n(cy - 6 * s)} {n(cx)},{n(cy - 4.5 * s)} C{n(cx)},{n(cy - 6 * s)} {n(cx + 2 * s)},{n(cy - 9 * s)} "
            f"{n(cx + 5 * s)},{n(cy - 9 * s)} C{n(cx + 11 * s)},{n(cy - 9 * s)} {n(cx + 12 * s)},{n(cy + 1 * s)} {n(cx)},{n(cy + 9 * s)}Z")


def mirror(pts):
    return [(-p[0],) + tuple(p[1:]) for p in pts][::-1]


def button(cx, cy, r, c, flat):
    if flat:
        return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{c}"/>'
    return (f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{rg([(0, lt(c, .5)), (.7, c), (1, dk(c, .3))], .4, .35, .6)}"/>'
            f'<circle cx="{n(cx - r * .25)}" cy="{n(cy - r * .25)}" r="{n(r * .3)}" fill="#FFFFFF" fill-opacity=".6"/>')


# ================================================================ items
def tshirt(flat):
    c = "#FFC531" if flat else "#EFBF45"
    sh = ("M-24,-86 C-14,-75 14,-75 24,-86 C38,-84 50,-82 58,-79 C74,-71 90,-62 100,-52 C94,-38 88,-26 82,-14 "
          "C74,-18 66,-22 59,-26 C60,10 61,50 61,86 C21,92 -21,92 -61,86 C-61,50 -60,10 -59,-26 "
          "C-66,-22 -74,-18 -82,-14 C-88,-26 -94,-38 -100,-52 C-90,-62 -74,-71 -58,-79 C-50,-82 -38,-84 -24,-86Z")
    d1, d2, l1 = dk(c, .22), dk(c, .38), lt(c, .35)
    if flat:
        o = [P(sh, c), P("M-24,-86 C-12,-92 12,-92 24,-86 C14,-79 -14,-79 -24,-86Z", "#D9900B"),
             line("M-25,-86 C-14,-74 14,-74 25,-86", "#E8A317", 8),
             P("M-100,-52 L-94,-56 L-76,-16 L-82,-14Z", "#E8A317"), P("M100,-52 L94,-56 L76,-16 L82,-14Z", "#E8A317"),
             P("M-61,78 C-21,84 21,84 61,78 L61,86 C21,92 -21,92 -61,86Z", "#E8A317")]
        return "".join(o), (-104, -96, 104, 96)
    inner = [fold("M-56,-24 C-30,0 -20,30 -24,70", c, 9, .3), fold("M56,-24 C34,4 26,40 30,80", c, 8, .28),
             fold("M-40,-20 C-20,6 -10,36 -12,72", c, 12, .4, True), fold("M44,-18 C30,8 22,36 22,62", c, 9, .35, True),
             fold("M-96,-48 C-84,-40 -78,-30 -80,-18 M96,-48 C84,-40 78,-30 80,-18", c, 6, .3),
             fold("M-60,-30 C-48,-28 -40,-34 -36,-40 M60,-30 C48,-28 40,-34 36,-40", c, 5, .35),
             line("M-58,-79 C-56,-60 -58,-40 -59,-26 M58,-79 C56,-60 58,-40 59,-26", d1, 1.2, .6),
             stitch("M-92,-48 C-86,-36 -81,-26 -75,-16 M92,-48 C86,-36 81,-26 75,-16", d2, .9, .55),
             stitch("M-60,80 C-20,86 20,86 60,80", d2, .9, .55), stitch("M-60,77 C-20,83 20,83 60,77", d2, .9, .35)]
    o = [shadow(0, 94, 76, 6), cloth(sh, c, (-100, -88, 100, 92), False, "".join(inner), rim_w=6, rim_op=.3)]
    o.append(P("M-24,-86 C-12,-92 12,-92 24,-86 C14,-79 -14,-79 -24,-86Z", d2))
    o.append(line("M-25,-86 C-14,-74 14,-74 25,-86", d1, 7) + line("M-25,-86 C-14,-74 14,-74 25,-86", l1, 5, .7, dash="1 1.4"))
    o.append(line("M-27,-86 C-14,-93 14,-93 27,-86", d1, 2.2))
    return "".join(o), (-104, -96, 104, 100)


PANTS = [(-60, -124), (60, -124), (66, -60, 30), (70, 128, 4), (13, 131, 4), (0, -34, 4), (-13, 131, 4), (-70, 128, 4), (-66, -60, 30)]


def pants(flat):
    c = "#3D7DDB" if flat else "#5577A8"
    d = rpoly(PANTS, 4)
    band = rpoly([(-60, -124), (60, -124), (61.5, -106), (-61.5, -106)], 3)
    cuffs = [rpoly([(-70, 112), (-12, 114), (-13, 131), (-70, 128)], 3), rpoly([(70, 112), (12, 114), (13, 131), (70, 128)], 3)]
    if flat:
        o = [P(d, c), P(band, "#2A5FB0"), P(cuffs[0], "#6FA3F0"), P(cuffs[1], "#6FA3F0"),
             line("M8,-106 L8,-64 C8,-54 2,-48 -4,-46", "#2A5FB0", 4),
             line("M-34,-106 C-36,-86 -48,-74 -63,-72 M34,-106 C36,-86 48,-74 63,-72", "#2A5FB0", 4)]
        o += [f'<rect x="{x - 4}" y="-128" width="8" height="24" rx="3" fill="#2A5FB0"/>' for x in (-44, -14, 20, 44)]
        return "".join(o), (-74, -132, 74, 134)
    thread = "#D99A45"
    inner = [fold("M-40,-90 C-40,-20 -42,60 -42,126", c, 14, .35, True), fold("M40,-90 C40,-20 42,60 42,126", c, 12, .3, True),
             fold("M-64,30 C-50,36 -30,34 -16,40", c, 8, .35), fold("M-66,52 C-52,58 -34,56 -16,62", c, 6, .3),
             fold("M64,36 C50,42 30,40 16,46", c, 8, .32), fold("M-6,-60 L-2,-36", c, 8, .4),
             weave((-75, -130, 75, 135), c, .1, (45, -45), 2.2)]
    o = [shadow(0, 134, 74, 6), cloth(d, c, (-70, -124, 70, 132), False, "".join(inner), tex=None)]
    o.append(P(band, lg([(0, lt(c, .1)), (1, dk(c, .1))], 0, 0, 0, 1)) + rim(band, dk(c, .5), 3, .3))
    o.append(stitch("M-59,-109 L59,-109 M-59,-121 L59,-121", thread, 1, .85, "3 2"))
    for k, cd in enumerate(cuffs):
        o.append(P(cd, lt(c, .12)) + clipped(cd, fold("M-70,113 L70,113", c, 5, .4)))
    o.append(stitch("M-68,125 L-15,127 M68,125 L15,127", thread, 1, .8, "3 2"))
    o.append(line("M8,-106 L8,-64 C8,-54 2,-48 -4,-46", dk(c, .4), 1.4, .7) + stitch("M12,-106 L12,-62 C12,-50 4,-43 -4,-41", thread, 1, .85, "3 2"))
    o.append(line("M-34,-106 C-36,-86 -48,-74 -63,-72 M34,-106 C36,-86 48,-74 63,-72", dk(c, .45), 1.6, .7))
    o.append(stitch("M-38,-106 C-40,-84 -52,-70 -64,-68 M38,-106 C40,-84 52,-70 64,-68", thread, 1, .85, "3 2"))
    o.append(stitch("M-66,-60 L-70,124 M66,-60 L70,124", thread, .9, .6, "3 2"))
    for x in (-44, -14, 20, 44):
        lp = rpoly([(x - 4, -128), (x + 4, -128), (x + 4, -102), (x - 4, -102)], 2)
        o.append(P(lp, mix(c, "#FFFFFF", .05)) + rim(lp, dk(c, .5), 2, .4))
    o.append(button(0, -115, 5, "#B8A07A", False))
    return "".join(o), (-74, -132, 74, 140)


def skirt(flat):
    c = "#FF7FAA" if flat else "#EE8FAE"
    hem = [(112, 96), (90, 108), (62, 101), (32, 110), (0, 102), (-32, 110), (-62, 101), (-90, 108), (-112, 96)]
    d = "M-56,-92 L56,-92 L60,-72 L112,96" + curve(hem, closed=False, start=False) + " L-60,-72Z"
    band = rpoly([(-56, -94), (56, -94), (60, -72), (-60, -72)], 3)
    if flat:
        o = [P(d, c)] + [P(poly([(x * 10 - 3, -72), (x * 10 + 3, -72), (x * 22 + 8, 100), (x * 22 - 8, 100)]), "#FF9EC0") for x in (-4, -2, 0, 2, 4)]
        o.append(P(band, "#E0457A"))
        return "".join(o), (-116, -96, 116, 112)
    inner = []
    for k in range(-5, 6):
        x0, x1 = k * 11, k * 21.5
        inner.append(fold(f"M{x0},-72 L{x1},104", c, 10, .32) if k % 2 else fold(f"M{x0},-72 L{x1},104", c, 12, .45, True))
    inner.append(spot(-50, 30, 50, 70, lt(c, .4), .3))
    o = [shadow(0, 108, 104, 7), cloth(d, c, (-112, -92, 112, 110), False, "".join(inner))]
    o.append(P(band, lg([(0, lt(c, .15)), (1, dk(c, .1))], 0, 0, 0, 1)))
    gathers = "".join(f"M{x},-92 l{0.6 if i % 2 else -0.6},20" for i, x in enumerate(range(-54, 56, 4)))
    o.append(clipped(band, f'<path d="{gathers}" fill="none" stroke="{dk(c, .3)}" stroke-width="1.4" stroke-opacity=".5"/>') + rim(band, dk(c, .45), 3, .35))
    o.append(stitch("M-112,92 C-62,96 62,96 112,92", dk(c, .35), .9, .5))
    return "".join(o), (-116, -98, 116, 114)


JK_BODY = [(-28, -104), (28, -104), (64, -92), (66, 98), (-66, 98), (-64, -92)]
JK_SLEEVE = [(56, -96), (86, -82), (126, 70), (98, 82), (66, -24)]


def jacket(flat):
    c = "#F2544B" if flat else "#D25B4C"
    body = rpoly(JK_BODY, 7)
    sl = [rpoly(JK_SLEEVE, 8), rpoly(mirror(JK_SLEEVE), 8)]
    cuffs = [rpoly([(120, 50), (128, 72), (100, 84), (94, 62)], 4), rpoly([(-120, 50), (-128, 72), (-100, 84), (-94, 62)], 4)]
    hem = rpoly([(-66, 80), (66, 80), (66, 100), (-66, 100)], 5)
    collar = rpoly([(-32, -116, 8), (32, -116, 8), (34, -92, 4), (0, -86), (-34, -92, 4)], 6)
    zip_c = "#C9CDD2"
    if flat:
        o = [P(s, c) for s in sl] + [P(body, c)] + [P(cf, "#C93A33") for cf in cuffs] + [P(hem, "#C93A33"), P(collar, "#C93A33")]
        o.append(f'<rect x="-3" y="-90" width="6" height="186" fill="#FFFFFF"/><rect x="-6" y="-92" width="12" height="20" rx="4" fill="#FFFFFF"/>')
        o.append(line("M-52,4 L-36,50 M52,4 L36,50", "#C93A33", 5))
        return "".join(o), (-130, -120, 130, 104)
    o = [shadow(0, 104, 110, 7)]
    for s, sgn in zip(sl, (1, -1)):
        inner = fold(f"M{sgn * 74},-70 L{sgn * 108},60", c, 12, .4, True) + fold(f"M{sgn * 70},-20 C{sgn * 80},-10 {sgn * 92},-14 {sgn * 98},-4", c, 7, .35) \
            + fold(f"M{sgn * 82},20 C{sgn * 90},28 {sgn * 102},26 {sgn * 108},34", c, 7, .35)
        o.append(cloth(s, c, (-130, -100, 130, 90), False, inner))
    rib = lambda dd: clipped(dd, hatch((-130, 40, 130, 104), 3, 75, dk(c, .45), .4, 1))
    for cf, sgn in zip(cuffs, (1, -1)):
        o.append(P(cf, dk(c, .1)) + clipped(cf, hatch((-130, 40, 130, 90), 3.2, 90 - sgn * 20, dk(c, .45), .45, 1.1)) + rim(cf, dk(c, .5), 3, .3))
    inner = [fold("M-40,-80 C-36,-20 -40,40 -44,78", c, 14, .4, True), fold("M44,-70 C40,-10 42,40 46,78", c, 10, .28),
             fold("M-60,-60 C-50,-56 -40,-60 -34,-66", c, 6, .3)]
    o.append(cloth(body, c, (-66, -104, 66, 100), False, "".join(inner)))
    o.append(P(hem, dk(c, .1)) + clipped(hem, hatch((-70, 78, 70, 102), 3.2, 90, dk(c, .45), .45, 1.1)) + rim(hem, dk(c, .5), 3, .3))
    o.append(P(collar, lg([(0, lt(c, .1)), (1, dk(c, .15))], 0, 0, 0, 1)) + rim(collar, dk(c, .5), 3, .35))
    o.append(stitch("M-28,-110 L28,-110", dk(c, .4), .9, .6))
    # zipper
    o.append(f'<rect x="-4.5" y="-92" width="9" height="190" fill="{dk(c, .25)}"/>')
    o.append(line("M-2,-92 L-2,98", zip_c, 3, 1, "butt", "1.6 1.6") + line("M2,-91 L2,98", zip_c, 3, 1, "butt", "1.6 1.6"))
    pull = rpoly([(-5, -94), (5, -94), (6, -70), (-6, -70)], 4)
    o.append(P(pull, lg([(0, "#EEF1F4"), (1, "#9AA2AA")], 0, 0, 1, 1)) + f'<rect x="-2" y="-80" width="4" height="7" rx="2" fill="#7E868E"/>')
    for sgn in (-1, 1):
        o.append(line(f"M{sgn * 52},4 L{sgn * 36},50", dk(c, .5), 2.4, .8) + stitch(f"M{sgn * 56},4 L{sgn * 40},52", dk(c, .35), .9, .6))
    o.append(stitch("M-8,-88 L-8,80 M8,-88 L8,80", dk(c, .35), .9, .5))
    return "".join(o), (-130, -120, 130, 110)


SOCK = "M-30,-100 L24,-100 L24,8 C24,24 34,34 54,34 L74,34 C98,34 102,76 74,78 L-4,78 C-32,78 -36,52 -32,30Z"


def one_sock(c, c2, flat, shade=0.0):
    cuff = "M-30,-100 L24,-100 L24,-66 L-30.6,-66Z"
    heel = "M-32,32 C-36,56 -30,78 -4,78 L8,78 C0,64 -4,48 -30,28Z"
    toe = "M64,34 L74,34 C98,34 102,76 74,78 L62,78 C72,64 72,46 64,34Z"
    if shade:
        c, c2 = mix(c, "#5A6470", shade), mix(c2, "#2A3440", shade)
    if flat:
        o = [P(SOCK, c), P(heel, c2), P(toe, c2), P(cuff, lt(c, .35))]
        o += [f'<rect x="-30" y="{y}" width="54" height="7" fill="{c2}"/>' for y in (-92, -80)]
        return "".join(o)
    inner = [hatch((-40, -100, 110, 80), 3, 90, dk(c, .3), .25, .8), P(heel, c2), P(toe, c2), P(cuff, lt(c, .3)),
             hatch((-32, -100, 26, -66), 2.6, 90, dk(c, .3), .35, .9),
             f'<rect x="-32" y="-92" width="58" height="6" fill="{c2}"/><rect x="-32" y="-81" width="58" height="6" fill="{c2}"/>',
             fold("M-6,-60 L-6,20", c, 14, .4, True), fold("M10,10 C14,30 30,44 50,46", c, 10, .3), fold("M-30,-66 L24,-66", c, 5, .35),
             spot(30, 56, 40, 14, lt(c, .5), .45)]
    return P(SOCK, fill_of(c, (-36, -100, 100, 80), False)) + clipped(SOCK, "".join(inner)) + rim(SOCK, dk(c, .45), 6, .32)


def socks(flat):
    c, c2 = ("#9FD4FF", "#2F7FE0") if flat else ("#CFE0F0", "#4E7FC4")
    o = [] if flat else [shadow(10, 82, 104, 6)]
    o.append(f'<g transform="translate(36 -22) rotate(6)">{one_sock(c, c2, flat, .12 if not flat else 0)}</g>')
    if flat:
        o[-1] = o[-1].replace(c, "#7CC2FA")
    o.append(f'<g transform="translate(-22 4)">{one_sock(c, c2, flat)}</g>')
    return "".join(o), (-56, -124, 144, 86)


def one_shoe(c, flat, shade=0.0):
    sole_c, cap_c, strap_c = ("#E3E8EF", "#E3E8EF", lt(c, .3)) if flat else ("#F4F2EE", "#FBFAF7", lt(c, .25))
    if shade:
        c, sole_c, cap_c, strap_c = (mix(x, "#2A3440", shade) for x in (c, sole_c, cap_c, strap_c))
    upper = ("M-116,12 C-119,-8 -104,-20 -80,-24 C-60,-27 -44,-36 -30,-50 C-22,-58 -10,-64 4,-66 C24,-60 50,-60 70,-68 "
             "C82,-72 92,-66 94,-50 C98,-30 98,-6 96,12Z")
    sole = "M-120,8 L96,8 C101,8 104,12 104,17 L104,22 C104,27 100,30 94,30 L-108,30 C-117,30 -122,25 -122,18 C-122,12 -121,8 -120,8Z"
    opening = "M4,-66 C24,-75 56,-77 73,-68 C54,-61 26,-59 4,-66Z"
    cap = "M-115,10 C-118,-9 -103,-20 -82,-23 C-87,-10 -89,0 -87,10Z"
    straps = [rpoly([(-70, -28), (-52, -38), (-34, 6), (-54, 8)], 4), rpoly([(-44, -44), (-26, -56), (-8, 4), (-28, 8)], 4)]
    if flat:
        o = [P(upper, c), P(opening, dk(c, .45)), P(cap, cap_c), P(sole, sole_c)] + [P(s, strap_c) for s in straps]
        o.append('<rect x="-120" y="19" width="224" height="5" fill="#C9D1DC"/>')
        return "".join(o)
    o = [P(upper, fill_of(c, (-110, -74, 96, 6), False)),
         clipped(upper, spot(-40, -20, 60, 18, lt(c, .4), .4) + spot(60, -20, 30, 30, dk(c, .3), .3)
                 + hatch((-120, -80, 100, 10), 2.2, 30, dk(c, .4), .12, .6)) + rim(upper, dk(c, .5), 6, .35)]
    o.append(P(opening, lg([(0, dk(c, .6)), (1, dk(c, .35))], 0, 0, 0, 1)))
    o.append(line("M4,-66 C26,-58 54,-60 73,-68", lt(c, .3), 4, .9))
    o.append(P("M-4,-63 C-2,-76 12,-80 22,-72 C14,-66 6,-63 -4,-63Z", lt(c, .15)))
    o.append(P(cap, lg([(0, "#FFFFFF"), (1, "#D9D6D0")], 0, 0, 1, 1)) + rim(cap, "#9A968E", 3, .3))
    for s in straps:
        o.append(P(s, lg([(0, lt(strap_c, .2)), (1, strap_c)], 0, 0, 1, 1)) + clipped(s, hatch((-70, -64, 0, 2), 2, 60, dk(strap_c, .3), .25, .6))
                 + rim(s, dk(c, .45), 3, .4))
    o.append(stitch("M-108,2 C-108,-12 -96,-18 -80,-20", dk(c, .4), .9, .5) + stitch("M8,-61 C28,-55 52,-55 72,-63 C82,-66 88,-60 90,-48", dk(c, .4), .9, .5))
    o.append(P(sole, lg([(0, "#FFFFFF"), (.6, sole_c), (1, "#C9C6C0")], 0, 0, 0, 1)) + rim(sole, "#8E8A84", 3, .35))
    o.append(line("M-114,22 L98,22", "#C9CED6", 2.2, .9) + stitch("M-110,13 L96,13", "#B5B1AA", .9, .7))
    o.append(P(rpoly([(88, -62), (96, -64), (100, -46), (93, -44)], 3), dk(c, .35)))
    return "".join(o)


def shoes(flat):
    c = "#2F86F0" if flat else "#3E7CC4"
    o = [] if flat else [shadow(10, 32, 130, 7, .22)]
    o.append(f'<g transform="translate(34 -22) scale(.96)">{one_shoe(c, flat, .25 if not flat else 0)}</g>')
    if flat:
        o[-1] = o[-1].replace(c, "#1F6BD0", 1)
    o.append(one_shoe(c, flat))
    return "".join(o), (-126, -96, 138, 36)


def hat(flat):
    c = "#14B8A6" if flat else "#2A9D8F"
    crown = "M-74,22 C-78,-40 -40,-82 10,-82 C58,-82 90,-46 90,10 C90,16 88,22 86,24 C40,28 -30,28 -74,22Z"
    brim = "M-70,10 C-100,6 -136,12 -154,26 C-156,34 -146,42 -118,42 C-96,42 -76,38 -62,30Z"
    under = "M-154,26 C-156,34 -146,42 -118,42 C-96,42 -76,38 -62,30 L-64,26 C-90,30 -126,32 -154,26Z"
    if flat:
        o = [P(brim, "#0E8577"), P(crown, c), line("M10,-80 C-20,-70 -38,-30 -42,22 M10,-80 C34,-60 42,-20 40,26", "#0E8577", 4),
             '<ellipse cx="10" cy="-84" rx="10" ry="6" fill="#0E8577"/>', '<ellipse cx="-24" cy="-50" rx="3.5" ry="3" fill="#0E8577"/>']
        return "".join(o), (-156, -92, 94, 46)
    o = [shadow(-30, 40, 120, 7)]
    o.append(P(brim, lg([(0, lt(c, .15)), (1, dk(c, .2))], 0, 0, 0, 1)) + clipped(brim, P(under, dk(c, .4)) + weave((-156, 0, -50, 50), c, .1, (20, 110)))
             + rim(brim, dk(c, .5), 4, .35) + stitch("M-70,20 C-100,16 -130,20 -146,30", lt(c, .35), .9, .6))
    inner = [fold("M10,-80 C-20,-70 -38,-30 -42,22", c, 7, .35), fold("M10,-80 C34,-60 42,-20 40,26", c, 7, .3),
             fold("M10,-80 C56,-70 80,-30 84,18", c, 6, .3), spot(-30, -40, 40, 34, lt(c, .45), .45),
             spot(60, 0, 34, 30, dk(c, .3), .3), weave((-80, -90, 92, 30), c, .08)]
    o.append(cloth(crown, c, (-74, -82, 90, 26), False, "".join(inner), tex=None, rim_op=.38))
    o.append(stitch("M6,-78 C-24,-68 -42,-28 -46,22 M14,-78 C38,-58 46,-20 44,26", lt(c, .3), .9, .6))
    o.append(P("M-74,14 C-30,20 40,20 88,14 L86,24 C40,28 -30,28 -74,22Z", dk(c, .15), 'fill-opacity=".9"'))
    o.append(stitch("M-72,18 C-30,24 40,24 87,18", lt(c, .3), .9, .6))
    o.append(f'<ellipse cx="10" cy="-83" rx="10" ry="5.5" fill="{rg([(0, lt(c, .3)), (1, dk(c, .3))], .4, .3, .7)}"/>')
    for x, y in ((-24, -50), (38, -52)):
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="3.6" ry="3" fill="{dk(c, .45)}"/><ellipse cx="{x}" cy="{y}" rx="2" ry="1.6" fill="{dk(c, .7)}"/>')
    return "".join(o), (-156, -92, 94, 48)


GL_F = [((-36, -6), (-46, -58), 12), ((-14, -14), (-18, -88), 13), ((8, -16), (8, -94), 13), ((29, -10), (35, -82), 12.5)]


def one_glove(c, flat, shade=0.0):
    c2 = lt(c, .35)
    if shade:
        c, c2 = mix(c, "#2A2440", shade), mix(c2, "#2A2440", shade)
    fingers = [tube([(bx, by, w), ((bx + tx) / 2, (by + ty) / 2, w), (tx, ty, w * .96)]) for (bx, by), (tx, ty), w in GL_F]
    thumb = tube([(36, 34, 14), (54, 12, 13), (64, -10, 12)])
    palm = rpoly([(-50, -14), (44, -20), (54, 40), (46, 76), (-46, 76), (-54, 40)], 20)
    cuff = rpoly([(-48, 66), (46, 66), (50, 114), (-52, 114)], 8)
    if flat:
        o = [P(f, c) for f in fingers] + [P(thumb, c), P(palm, c), P(cuff, c2)]
        o += [f'<rect x="-52" y="{y}" width="102" height="6" fill="{c}"/>' for y in (82, 98)]
        return "".join(o)
    fill = fill_of(c, (-60, -100, 70, 110), False)
    o = []
    boxes = [(min(bx, tx) - w, ty - w, max(bx, tx) + w, by + 4) for (bx, by), (tx, ty), w in GL_F] + [(22, -24, 78, 48)]
    for f, bb in zip(fingers + [thumb], boxes):
        o.append(P(f, fill) + clipped(f, knit(bb, c, .3, 7, 6)) + rim(f, dk(c, .5), 4, .35))
    o.append(P(palm, fill) + clipped(palm, knit((-60, -30, 60, 80), c, .3, 7, 6) + spot(-16, 20, 34, 30, lt(c, .4), .35)) + rim(palm, dk(c, .5), 5, .35))
    o.append(P(cuff, fill_of(c2, (-50, 66, 50, 114), False)) + clipped(cuff, hatch((-56, 60, 56, 116), 4, 90, dk(c2, .4), .45, 1.4)
                                                                     + f'<rect x="-56" y="84" width="112" height="7" fill="{c}" fill-opacity=".85"/>')
             + rim(cuff, dk(c2, .5), 4, .35))
    return "".join(o)


def gloves(flat):
    c = "#A05BF0" if flat else "#9C7BD0"
    o = [] if flat else [shadow(10, 118, 104, 6)]
    o.append(f'<g transform="translate(44 -16) rotate(10) scale(-1 1)">{one_glove(c, flat, .2 if not flat else 0)}</g>')
    if flat:
        o[-1] = o[-1].replace(f'fill="{c}"', 'fill="#8840DE"')
    o.append(f'<g transform="translate(-26 6) rotate(-6)">{one_glove(c, flat)}</g>')
    return "".join(o), (-92, -112, 132, 124)


def scarf(flat):
    c, c2 = ("#FF4D4D", "#FFF1D6") if flat else ("#D84B4B", "#F2E6C8")
    mid = [(-104, -66, 24), (-50, -86, 25), (16, -76, 25), (58, -38, 24), (44, 8, 24), (-14, 30, 25), (-62, 58, 24), (-42, 98, 24), (30, 104, 24),
           (84, 92, 23)]
    C = spline(mid, 8)
    L, R = [], []
    for i, (x, y, w) in enumerate(C):
        a, b = C[max(0, i - 1)], C[min(len(C) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1
        L.append((x - dy / ln * w, y + dx / ln * w))
        R.append((x + dy / ln * w, y - dx / ln * w))
    d = poly(L + R[::-1])
    seg = []
    m = len(C)
    edges = [0] + [i for i in range(6, m - 6, 9)] + [m - 1]
    for k in range(len(edges) - 1):
        i0, i1 = edges[k], edges[k + 1]
        seg.append((poly(L[i0:i1 + 1] + R[i0:i1 + 1][::-1]), c if k % 2 == 0 else c2))
    fr = []
    for end, sgn in ((0, -1), (m - 1, 1)):
        a, b = C[end], C[end - sgn] if 0 <= end - sgn < m else C[end]
        dx, dy = (a[0] - b[0]), (a[1] - b[1])
        ln = math.hypot(dx, dy) or 1
        ux, uy = dx / ln, dy / ln
        for j in range(8):
            t = -1 + 2 * (j + .5) / 8
            px, py = a[0] - uy * a[2] * t * .92, a[1] + ux * a[2] * t * .92
            fr.append(f"M{n(px)},{n(py)} l{n(ux * 16 + (j % 3 - 1) * 1.5)},{n(uy * 16)}")
    if flat:
        o = [line("".join(fr), c, 4)] + [P(sd, col) for sd, col in seg]
        return "".join(o), (-140, -110, 120, 134)
    o = [shadow(-10, 128, 100, 6), line("".join(fr), dk(c, .1), 3.4)]
    tex = []
    for frac in (-.75, -.45, -.15, .15, .45, .75):
        tex.append("M" + " L".join(f"{n(x + (L[i][0] - x) * frac)},{n(y + (L[i][1] - y) * frac)}" for i, (x, y, w) in enumerate(C)))
    rib = f'<path d="{"".join(tex)}" fill="none" stroke="#5A1E1E" stroke-width="2.2" stroke-opacity=".16"/>'
    rib += f'<path d="{"".join(tex)}" fill="none" stroke="#FFFFFF" stroke-width="1" stroke-opacity=".18" transform="translate(-1.2 -1.2)"/>'
    for sd, col in seg:
        o.append(P(sd, col))
    shade = spot(30, -62, 30, 24, "#3A1010", .25) + spot(30, 22, 30, 20, "#3A1010", .25) + spot(-50, 74, 26, 20, "#3A1010", .25) \
        + spot(-60, -80, 40, 16, "#FFFFFF", .25) + spot(10, -10, 40, 18, "#FFFFFF", .15)
    o.append(clipped(d, rib + shade) + rim(d, "#4A1A1A", 6, .3))
    return "".join(o), (-140, -110, 120, 136)


PJ_BODY = [(-30, -108), (30, -108), (62, -96), (64, 48), (-64, 48), (-62, -96)]
PJ_SLEEVE = [(56, -100), (86, -86), (120, 30), (92, 42), (64, -30)]
PJ_PANTS = [(-56, 28), (56, 28), (62, 126, 4), (10, 128, 4), (0, 72, 4), (-10, 128, 4), (-62, 126, 4)]


def pattern(box, rng, c_star, c_moon, op=.9, flat=False):
    x0, y0, x1, y1 = box
    st, mo = [], []
    y, row = y0, 0
    while y < y1:
        x = x0 + (row % 2) * 14
        while x < x1:
            jx, jy = rng.uniform(-3, 3), rng.uniform(-3, 3)
            if (int(x / 28) + row) % 3 == 0:
                mo.append(f"M{n(x + jx + 3)},{n(y + jy - 5)} A5.5,5.5 0 1 0 {n(x + jx + 3)},{n(y + jy + 5)} A4,4 0 1 1 {n(x + jx + 3)},{n(y + jy - 5)}Z")
            else:
                st.append(star_d(x + jx, y + jy, 5, 2.3, -90 + rng.uniform(-15, 15)))
            x += 28
        y += 24
        row += 1
    return f'<path d="{"".join(st)}" fill="{c_star}" fill-opacity="{op}"/><path d="{"".join(mo)}" fill="{c_moon}" fill-opacity="{op}"/>'


def pajamas(flat):
    c = "#8F7BEA" if flat else "#A898DA"
    body = rpoly(PJ_BODY, 7)
    sl = [rpoly(PJ_SLEEVE, 8), rpoly(mirror(PJ_SLEEVE), 8)]
    pnts = rpoly(PJ_PANTS, 6)
    collar = ["M-30,-108 C-34,-90 -24,-76 -4,-80 L0,-100 C-10,-100 -22,-104 -30,-108Z", "M30,-108 C34,-90 24,-76 4,-80 L0,-100 C10,-100 22,-104 30,-108Z"]
    pat = lambda box: pattern(box, random.Random(4), "#FFFFFF", "#FFE58A", .85)
    pb, ps, pr = (-64, 26, 64, 132), (54, -104, 124, 46), (-64, -112, 64, 50)
    if flat:
        o = [P(pnts, dk(c, .1)), clipped(pnts, pat(pb))] + [P(s, c) + clipped(s, pat(ps if k == 0 else (-124, -104, -54, 46))) for k, s in enumerate(sl)]
        o += [P(body, c), clipped(body, pat(pr))]
        o += [P(cd, "#FFFFFF") for cd in collar]
        o += [line("M92,36 L118,24 M-92,36 L-118,24", "#FFFFFF", 6)]
        o += [f'<circle cx="0" cy="{y}" r="5.5" fill="#FFFFFF"/>' for y in (-70, -40, -10, 20)]
        return "".join(o), (-124, -112, 124, 132)
    o = [shadow(0, 132, 70, 6)]
    o.append(cloth(pnts, dk(c, .05), (-62, 28, 62, 128), False, fold("M-36,50 L-38,124", c, 12, .35, True) + fold("M30,60 L34,124", c, 10, .3)
                   + fold("M-60,90 C-48,94 -30,92 -14,96", c, 7, .35) + pat(pb)))
    o.append(stitch("M-60,116 L-12,118 M60,116 L12,118", lt(c, .5), .9, .7))
    for s, sgn in zip(sl, (1, -1)):
        o.append(cloth(s, c, (-124, -100, 124, 44), False, fold(f"M{sgn * 74},-76 L{sgn * 104},26", c, 12, .4, True)
                       + fold(f"M{sgn * 70},-30 C{sgn * 80},-20 {sgn * 90},-22 {sgn * 96},-12", c, 7, .35) + pat(ps if sgn > 0 else (-124, -104, -54, 46))))
        o.append(line(f"M{sgn * 94},36 L{sgn * 119},24", "#FFFFFF", 3.4, .95))
    o.append(cloth(body, c, (-64, -108, 64, 48), False, fold("M-40,-80 C-36,-20 -40,10 -44,44", c, 14, .4, True)
                   + fold("M44,-70 C40,-10 42,20 46,44", c, 10, .3) + fold("M-60,-60 C-50,-56 -40,-60 -34,-66", c, 6, .3) + pat(pr)))
    o.append(line("M-62,44 L62,44", "#FFFFFF", 3, .9) + line("M-5,-80 L-5,46", dk(c, .35), 1.2, .7))
    for cd in collar:
        o.append(P(cd, lg([(0, "#FFFFFF"), (1, "#E6E2F2")], 0, 0, 0, 1)) + rim(cd, "#8E86A8", 3, .3))
    for y in (-70, -40, -10, 20):
        o.append(button(0, y, 5, "#FFFFFF", False) + f'<circle cx="-1.4" cy="{y}" r=".9" fill="#A098B8"/><circle cx="1.4" cy="{y}" r=".9" fill="#A098B8"/>')
    return "".join(o), (-124, -112, 124, 136)


RC_BODY = [(-34, -96), (34, -96), (62, -84), (78, 120), (-78, 120), (-62, -84)]
RC_SLEEVE = [(56, -90), (86, -74), (124, 50), (96, 62), (68, -14)]
RC_HOOD = [(-48, -94), (-56, -124), (-32, -148), (0, -153), (32, -148), (56, -124), (48, -94), (0, -82)]


def raincoat(flat):
    c = "#FFC81A" if flat else "#F6C833"
    body = rpoly(RC_BODY, 8)
    sl = [rpoly(RC_SLEEVE, 8), rpoly(mirror(RC_SLEEVE), 8)]
    hood = curve(RC_HOOD)
    lining = curve([(-34, -98), (-38, -120), (-20, -136), (0, -139), (20, -136), (38, -120), (34, -98), (0, -88)])
    pockets = [rpoly([(-60, 40), (-22, 40), (-22, 56), (-60, 58)], 4), rpoly([(60, 40), (22, 40), (22, 56), (60, 58)], 4)]
    snaps = [(6, y) for y in (-64, -26, 12, 50, 88)]
    if flat:
        o = [P(s, c) for s in sl] + [P(hood, c), P(lining, "#E8A800"), P(body, c)]
        o += [P(pk, "#F0A800") for pk in pockets]
        o.append('<rect x="-3" y="-86" width="5" height="206" fill="#F0A800"/>')
        o += [f'<circle cx="{x}" cy="{y}" r="6.5" fill="#FFFFFF"/>' for x, y in snaps]
        o.append(line("M-46,-60 L-56,90", "#FFFFFF", 6) + line("M-96,-30 L-108,20", "#FFFFFF", 5))
        return "".join(o), (-128, -156, 128, 124)
    o = [shadow(0, 124, 104, 7)]
    gloss = lambda pts_d, w: sline(pts_d, "#FFFFFF", w, .5)
    for s, sgn in zip(sl, (1, -1)):
        o.append(cloth(s, c, (-128, -96, 128, 64), False, fold(f"M{sgn * 70},-30 C{sgn * 80},-22 {sgn * 92},-24 {sgn * 98},-14", c, 7, .35)
                       + gloss(f"M{sgn * 76},-66 L{sgn * 106},36", 7), tex=None, rim_op=.4))
        o.append(sline(f"M{sgn * 96},56 L{sgn * 121},44", dk(c, .35), 5, .4))
    o.append(cloth(hood, c, (-56, -153, 56, -82), False, gloss("M-36,-136 C-20,-146 10,-148 30,-140", 6), tex=None, rim_op=.4))
    o.append(P(lining, lg([(0, "#9A7A1C"), (.5, "#C9A23A"), (1, "#E2BC4E")], 0, 0, 0, 1)))
    o.append(cloth(body, c, (-78, -96, 78, 120), False, fold("M40,-70 C38,-10 42,60 50,116", c, 12, .3) + fold("M-20,0 C-24,40 -28,80 -30,116", c, 10, .25)
                   + gloss("M-46,-64 C-50,-10 -54,40 -58,100", 12) + gloss("M-34,-70 C-36,-40 -38,-20 -40,0", 4), tex=None, rim_op=.4))
    o.append(stitch("M-74,112 L74,112", dk(c, .35), .9, .6))
    o.append(P(rpoly([(-3, -86), (16, -86), (16, 120), (-3, 120)], 2), dk(c, .06)) + line("M-3,-86 L-3,120", dk(c, .35), 1.4, .8)
             + stitch("M12,-84 L12,118", dk(c, .35), .9, .5))
    for pk in pockets:
        o.append(P(pk, lg([(0, lt(c, .15)), (1, dk(c, .12))], 0, 0, 0, 1)) + rim(pk, dk(c, .45), 3, .4))
    o.append(stitch("M-58,44 L-24,44 M58,44 L24,44", dk(c, .35), .8, .55))
    for x, y in snaps + [(-41, 50), (41, 50)]:
        o.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{rg([(0, "#FFFFFF"), (.7, "#E3E6EA"), (1, "#A7ADB4")], .4, .35, .6)}"/>'
                 f'<circle cx="{x}" cy="{y}" r="2.4" fill="#B9BEC5"/>')
    return "".join(o), (-128, -156, 128, 128)


BOOT = "M-34,-112 L36,-112 C38,-60 38,-20 40,8 C44,24 60,30 82,32 C100,34 108,46 106,60 L106,66 L-48,66 L-48,60 C-50,30 -44,0 -40,-40Z"


def one_boot(c, flat, shade=0.0):
    cuff_c = lt(c, .2)
    sole_c = dk(c, .45)
    if shade:
        c, cuff_c, sole_c = (mix(x, "#2A1A18", shade) for x in (c, cuff_c, sole_c))
    sole = "M-50,52 L108,52 L108,62 C108,68 104,72 98,72 L-44,72 C-48,72 -50,68 -50,62Z"
    cuff = "M-34,-112 L36,-112 L36.4,-96 L-35.4,-96Z"
    tab = rpoly([(30, -112), (44, -112), (46, -88), (34, -90)], 4)
    if flat:
        return "".join([P(BOOT, c), P(cuff, cuff_c), P(sole, sole_c), P(tab, sole_c),
                        line("M-22,-80 L-24,30", "#FFFFFF", 7), line("M60,40 L84,40", "#FFFFFF", 5)])
    fill = lg([(0, lt(c, .25)), (.45, c), (1, dk(c, .3))], -50, 0, 110, 0, user=True)
    o = [P(BOOT, fill), clipped(BOOT, sline("M-22,-90 C-22,-40 -24,0 -26,40", "#FFFFFF", 12, .55) + sline("M-18,-90 C-18,-60 -19,-30 -20,-10", "#FFFFFF", 3, .7)
                                  + sline("M54,42 C66,38 80,38 94,42", "#FFFFFF", 6, .55) + spot(30, -40, 20, 70, dk(c, .4), .3)
                                  + spot(50, 30, 30, 18, dk(c, .3), .25)) + rim(BOOT, dk(c, .55), 7, .4)]
    o.append(P(cuff, lg([(0, lt(cuff_c, .2)), (1, cuff_c)], 0, 0, 0, 1)) + rim(cuff, dk(c, .5), 3, .3))
    o.append(P(tab, dk(c, .3)))
    o.append(P(sole, lg([(0, sole_c), (1, dk(sole_c, .4))], 0, 0, 0, 1)) + line("M-46,66 L104,66", dk(sole_c, .5), 1.4, .6, dash="6 4"))
    return "".join(o)


def rain_boots(flat):
    c = "#FF3B30" if flat else "#E0483B"
    o = [] if flat else [shadow(30, 74, 120, 7, .22)]
    o.append(f'<g transform="translate(54 -14) scale(.95)">{one_boot(c, flat, .25 if not flat else 0)}</g>')
    if flat:
        o[-1] = o[-1].replace(f'fill="{c}"', 'fill="#D92A20"')
    o.append(f'<g transform="translate(-20 6)">{one_boot(c, flat)}</g>')
    return "".join(o), (-72, -124, 162, 80)


def underwear(flat):
    c = "#5BB8F5" if flat else "#7FC4EA"
    d = "M-82,-56 L82,-56 L84,-36 C72,-6 44,28 24,56 L-24,56 C-44,28 -72,-6 -84,-36Z"
    band = "M-83,-60 L83,-60 L84,-40 L-84,-40Z"
    bow = ("M0,-30 C-6,-36 -14,-36 -14,-30 C-14,-24 -6,-24 0,-30Z M0,-30 C6,-36 14,-36 14,-30 C14,-24 6,-24 0,-30Z")
    if flat:
        return "".join([P(d, c), P(band, "#FFFFFF"), P(band, c, 'fill-opacity=".25"'), P(bow, "#FFFFFF"), '<circle cx="0" cy="-30" r="3" fill="#FFFFFF"/>',
                        line("M-82,-34 C-70,-6 -44,26 -26,52 M82,-34 C70,-6 44,26 26,52", "#3A9DE6", 5)]), (-88, -64, 88, 60)
    o = [shadow(0, 62, 74, 6)]
    inner = [fold("M-50,-30 C-40,0 -26,26 -14,50", c, 12, .4, True), fold("M40,-30 C34,0 24,26 14,50", c, 10, .3),
             sline("M-82,-34 C-70,-6 -44,26 -26,52", dk(c, .35), 6, .35), sline("M82,-34 C70,-6 44,26 26,52", dk(c, .35), 6, .35),
             line("M-30,20 C-10,30 10,30 30,20", dk(c, .3), 1, .5)]
    o.append(cloth(d, c, (-84, -56, 84, 56), False, "".join(inner)))
    o.append(stitch("M-79,-32 C-67,-4 -41,28 -24,50 M79,-32 C67,-4 41,28 24,50", dk(c, .35), .9, .55))
    o.append(P(band, lg([(0, "#FFFFFF"), (1, "#DCE7EF")], 0, 0, 0, 1)) + clipped(band, hatch((-86, -62, 86, -38), 3, 90, "#9AB3C6", .4, 1))
             + rim(band, "#7D96AA", 3, .35))
    o.append(P(bow, "#FFFFFF") + '<circle cx="0" cy="-30" r="3" fill="#E8EEF3"/>' + line("M-2,-27 L-6,-20 M2,-27 L6,-20", "#FFFFFF", 2))
    return "".join(o), (-90, -64, 90, 66)


TANK = "M-44,-112 L-24,-112 C-20,-84 20,-84 24,-112 L44,-112 C44,-74 54,-44 70,-32 L74,110 L-74,110 L-70,-32 C-54,-44 -44,-74 -44,-112Z"


def vest(flat):
    c = "#FF8A2A" if flat else "#F29A4A"
    trims = ["M-24,-112 C-20,-84 20,-84 24,-112", "M44,-112 C44,-74 54,-44 70,-32", "M-44,-112 C-44,-74 -54,-44 -70,-32"]
    if flat:
        o = [P(TANK, c)] + [line(t, "#E06A10", 7) for t in trims] + [P("M-74,98 L74,98 L74,110 L-74,110Z", "#E06A10")]
        return "".join(o), (-78, -116, 78, 112)
    inner = [fold("M-40,-60 C-34,0 -40,60 -44,106", c, 14, .4, True), fold("M36,-50 C32,10 34,60 40,106", c, 10, .28),
             fold("M-62,-20 C-50,-14 -40,-16 -34,-22", c, 6, .3), spot(0, 30, 50, 50, lt(c, .35), .3)]
    o = [shadow(0, 114, 72, 6), cloth(TANK, c, (-74, -112, 74, 110), False, "".join(inner))]
    for t in trims:
        o.append(clipped(TANK, line(t, dk(c, .15), 10) + line(t, lt(c, .2), 6, .8, dash="1 1.5")))
    o.append(stitch("M-72,102 L72,102", dk(c, .4), .9, .6))
    return "".join(o), (-78, -116, 78, 116)


def dress(flat):
    c = "#FF5C7A" if flat else "#E8607A"
    rng = random.Random(6)
    hem = "".join(f" Q{n(-116 + 38.7 * k + 19.3)},{n(128 + (4 if k % 2 else 0))} {n(-116 + 38.7 * (k + 1))},{116}" for k in range(6))
    d = "M-26,-112 L-46,-106 C-50,-96 -52,-84 -50,-74 L-44,-22 L-116,116" + hem + " L44,-22 L50,-74 C52,-84 50,-96 46,-106 L26,-112 C16,-100 -16,-100 -26,-112Z"
    sleeves = [f"M{s * 44},-108 C{s * 62},-118 {s * 82},-106 {s * 80},-86 C{s * 78},-74 {s * 66},-70 {s * 50},-72Z" for s in (-1, 1)]
    collar = ["M-26,-112 C-28,-94 -16,-86 -2,-92 L0,-101 C-10,-102 -20,-106 -26,-112Z", "M26,-112 C28,-94 16,-86 2,-92 L0,-101 C10,-102 20,-106 26,-112Z"]
    sash = rpoly([(-46, -34), (46, -34), (45, -20), (-45, -20)], 2)
    bow = "M0,-27 C-12,-40 -26,-36 -24,-27 C-26,-18 -12,-14 0,-27Z M0,-27 C12,-40 26,-36 24,-27 C26,-18 12,-14 0,-27Z"
    tails = "M-3,-24 L-12,4 L-6,1 L-2,6Z M3,-24 L12,4 L6,1 L2,6Z"
    dots = "".join(f"M{n(x - 4)},{n(y)}a4,4 0 1 0 8,0a4,4 0 1 0 -8,0" for y in range(-110, 130, 20) for x in range(-120 + (10 if (y // 20) % 2 else 0), 124, 20))
    dots_p = f'<path d="{dots}" fill="#FFFFFF" fill-opacity=".9"/>'
    if flat:
        o = [P(sl, c) + clipped(sl, dots_p) for sl in sleeves] + [P(d, c), clipped(d, dots_p)] + [P(cd, "#FFFFFF") for cd in collar]
        o += [P(sash, "#FFFFFF"), P(tails, "#FFD0DA"), P(bow, "#FFD0DA"), '<circle cx="0" cy="-27" r="5" fill="#FFFFFF"/>']
        return "".join(o), (-120, -122, 120, 134)
    o = [shadow(0, 128, 110, 7)]
    for sl in sleeves:
        o.append(cloth(sl, c, (-84, -118, 84, -70), False, dots_p, tex=None))
    inner = [fold("M-30,-10 C-50,40 -70,80 -80,118", c, 12, .4, True), fold("M-6,-10 C-10,40 -14,80 -16,124", c, 10, .3),
             fold("M18,-10 C26,40 36,80 44,122", c, 12, .35, True), fold("M36,-10 C56,40 76,80 90,118", c, 10, .3),
             spot(-20, -60, 30, 30, lt(c, .4), .4), dots_p, weave((-120, -115, 120, 130), c, .05)]
    o.append(cloth(d, c, (-116, -112, 116, 130), False, "".join(inner), tex=None))
    for cd in collar:
        o.append(P(cd, lg([(0, "#FFFFFF"), (1, "#EDE6E8")], 0, 0, 0, 1)) + rim(cd, "#A8949A", 3, .3))
    o.append(P(sash, lg([(0, "#FFFFFF"), (1, "#E8DEE1")], 0, 0, 0, 1)) + rim(sash, "#A8949A", 3, .3))
    o.append(P(tails, "#F7C4D0") + P(bow, lg([(0, "#FFE1E8"), (1, "#F2AFC0")], 0, 0, 0, 1)) + f'<circle cx="0" cy="-27" r="5" fill="{rg([(0, "#FFFFFF"), (1, "#E7C4CD")])}"/>')
    o.append(stitch("M-112,112 Q0,122 112,112", dk(c, .35), .9, .5))
    return "".join(o), (-120, -122, 120, 134)


SHORTS = [(-64, -70), (64, -70), (70, -30, 20), (78, 60, 4), (14, 66, 4), (0, 10, 4), (-14, 66, 4), (-78, 60, 4), (-70, -30, 20)]


def shorts(flat):
    c = "#5DBB63" if flat else "#6DAE6A"
    d = rpoly(SHORTS, 4)
    band = rpoly([(-64, -72), (64, -72), (65.5, -52), (-65.5, -52)], 3)
    cord = "M-6,-60 C-10,-44 -16,-30 -22,-18 M6,-60 C10,-44 16,-30 22,-18"
    if flat:
        o = [P(d, c), P(band, "#3E9A45"), line(cord, "#FFFFFF", 4), '<circle cx="-22" cy="-18" r="4" fill="#FFFFFF"/><circle cx="22" cy="-18" r="4" fill="#FFFFFF"/>',
             line("M-40,-52 C-44,-36 -56,-26 -70,-24 M40,-52 C44,-36 56,-26 70,-24", "#3E9A45", 4), P(rpoly([(-78, 48), (-13, 52), (-14, 66), (-78, 60)], 3), "#86D68B"),
             P(rpoly([(78, 48), (13, 52), (14, 66), (78, 60)], 3), "#86D68B")]
        return "".join(o), (-82, -76, 82, 70)
    inner = [fold("M-42,-40 C-42,0 -44,40 -46,62", c, 14, .4, True), fold("M42,-40 C42,0 44,40 46,62", c, 10, .3),
             fold("M-70,20 C-56,26 -36,24 -18,30", c, 7, .35), fold("M-4,-46 L0,-2", c, 8, .35)]
    o = [shadow(0, 70, 74, 6), cloth(d, c, (-78, -70, 78, 66), False, "".join(inner))]
    o.append(P(band, lg([(0, lt(c, .1)), (1, dk(c, .12))], 0, 0, 0, 1)))
    gathers = "".join(f"M{x},-72 l{0.6 if i % 2 else -0.6},20" for i, x in enumerate(range(-62, 64, 4)))
    o.append(clipped(band, f'<path d="{gathers}" fill="none" stroke="{dk(c, .35)}" stroke-width="1.4" stroke-opacity=".5"/>') + rim(band, dk(c, .45), 3, .35))
    o.append(line("M-40,-52 C-44,-36 -56,-26 -70,-24 M40,-52 C44,-36 56,-26 70,-24", dk(c, .45), 1.6, .7))
    o.append(stitch("M-76,52 L-15,56 M76,52 L15,56 M-66,-30 L-77,56 M66,-30 L77,56", dk(c, .4), .9, .55))
    o.append(line(cord, "#F4F1EA", 3) + line(cord, "#C9C2B4", 1, .5, dash="2 2"))
    o.append('<ellipse cx="-22" cy="-18" rx="3.4" ry="4.4" fill="#E9E4DA"/><ellipse cx="22" cy="-18" rx="3.4" ry="4.4" fill="#E9E4DA"/>')
    o.append('<circle cx="-6" cy="-62" r="2.6" fill="#E9E4DA"/><circle cx="6" cy="-62" r="2.6" fill="#E9E4DA"/>')
    return "".join(o), (-82, -76, 82, 74)


SW_BODY = [(-30, -104), (30, -104), (64, -92), (66, 94), (-66, 94), (-64, -92)]
SW_SLEEVE = [(56, -96), (86, -82), (124, 72), (96, 82), (66, -24)]


def sweater(flat):
    c, c2 = ("#3DAA4F", "#FFF1D6") if flat else ("#4F9A5B", "#F2E6C8")
    body = rpoly(SW_BODY, 7)
    sl = [rpoly(SW_SLEEVE, 8), rpoly(mirror(SW_SLEEVE), 8)]
    cuffs = [rpoly([(116, 46), (126, 72), (98, 84), (90, 60)], 4), rpoly([(-116, 46), (-126, 72), (-98, 84), (-90, 60)], 4)]
    hem = rpoly([(-66, 76), (66, 76), (66, 96), (-66, 96)], 5)
    neck = "M-31,-104 C-20,-86 20,-86 31,-104"
    band = '<rect x="-140" y="-46" width="280" height="22" fill="{0}"/><rect x="-140" y="-42" width="280" height="3" fill="{1}"/><rect x="-140" y="-31" width="280" height="3" fill="{1}"/>'
    if flat:
        o = [P(s, c) + clipped(s, band.format(c2, c)) for s in sl] + [P(body, c), clipped(body, band.format(c2, c))]
        o += [P(cf, "#2C8A3C") for cf in cuffs] + [P(hem, "#2C8A3C"), line(neck, "#2C8A3C", 10)]
        return "".join(o), (-130, -112, 130, 100)
    o = [shadow(0, 100, 110, 7)]
    for s, sgn in zip(sl, (1, -1)):
        kb = (54, -98, 128, 86) if sgn > 0 else (-128, -98, -54, 86)
        o.append(cloth(s, c, (-130, -100, 130, 90), False, band.format(c2, c) + fold(f"M{sgn * 74},-70 L{sgn * 108},60", c, 12, .35, True)
                       + fold(f"M{sgn * 70},-20 C{sgn * 80},-10 {sgn * 92},-14 {sgn * 98},-4", c, 7, .35), tex=None, top=knit(kb, c, .3)))
    for cf, sgn in zip(cuffs, (1, -1)):
        o.append(P(cf, dk(c, .1)) + clipped(cf, hatch((-130, 40, 130, 90), 3.4, 90 - sgn * 20, dk(c, .5), .5, 1.4)) + rim(cf, dk(c, .5), 3, .3))
    o.append(cloth(body, c, (-66, -104, 66, 96), False, band.format(c2, c) + fold("M-40,-80 C-36,-20 -40,40 -44,74", c, 14, .4, True)
                   + fold("M44,-70 C40,-10 42,40 46,74", c, 10, .3), tex=None, top=knit((-70, -110, 70, 96), c, .3)))
    o.append(P(hem, dk(c, .1)) + clipped(hem, hatch((-70, 74, 70, 98), 3.4, 90, dk(c, .5), .5, 1.4)) + rim(hem, dk(c, .5), 3, .3))
    o.append(line(neck, dk(c, .15), 10) + line(neck, dk(c, .4), 7, .5, dash="1.4 1.8") + line("M-33,-104 C-20,-94 20,-94 33,-104", dk(c, .45), 2.4, .6))
    return "".join(o), (-130, -112, 130, 104)


FLOP = [(0, -112), (28, -106), (44, -82), (46, -22), (40, 40), (36, 88), (20, 112), (-12, 114), (-30, 96), (-36, 40), (-40, -20), (-42, -80), (-26, -106)]


def one_flop(flat, shade=0.0):
    blue, white = ("#1E6FE0", "#DCE9F7") if flat else ("#2F6FC6", "#F4F3EE")
    if shade:
        blue, white = mix(blue, "#1A2030", shade), mix(white, "#5A6070", shade)
    outer = curve(FLOP)
    top = curve([(x * .9 + 2, y * .93 - 3) for x, y in FLOP])
    straps = [tube([(-8, -72, 5), (-22, -44, 7.5), (-36, -10, 7)]), tube([(-8, -72, 5), (14, -42, 7.5), (42, -16, 7)])]
    if flat:
        o = [f'<g transform="translate(2 6)">{P(outer, dk(blue, .25))}</g>', P(outer, blue), P(top, white)] + [P(s, blue) for s in straps]
        o.append(f'<circle cx="-8" cy="-72" r="6" fill="{blue}"/>')
        return "".join(o)
    o = [f'<g transform="translate(2 6)">{P(outer, dk(blue, .3))}</g>', P(outer, lg([(0, lt(blue, .2)), (1, dk(blue, .15))], 0, 0, 1, 1))]
    o.append(P(top, rg([(0, "#FFFFFF"), (.7, white), (1, mix(white, "#9AA6B4", .4))], .4, .4, .7)))
    o.append(clipped(top, hatch((-50, -120, 50, 120), 4, 60, "#8C98A8", .2, .7) + hatch((-50, -120, 50, 120), 4, -60, "#8C98A8", .2, .7)
                     + spot(-6, 50, 26, 40, "#7C8898", .18) + spot(4, -60, 28, 30, "#7C8898", .15)))
    for s in straps:
        o.append(P(s, lg([(0, lt(blue, .3)), (1, dk(blue, .2))], 0, 0, 1, 1)) + rim(s, dk(blue, .5), 3, .4))
    o.append(spot(-20, -8, 14, 6, "#2A3440", .25) + spot(40, -10, 14, 6, "#2A3440", .25))
    o.append(f'<circle cx="-8" cy="-72" r="6.5" fill="{rg([(0, lt(blue, .4)), (1, dk(blue, .3))], .4, .35, .6)}"/>')
    return "".join(o)


def slippers(flat):
    o = [] if flat else [shadow(0, 118, 110, 7)]
    o.append(f'<g transform="translate(-52 0) rotate(-4) scale(-1 1)">{one_flop(flat)}</g>')
    o.append(f'<g transform="translate(52 0) rotate(4)">{one_flop(flat)}</g>')
    return "".join(o), (-104, -118, 104, 124)


DIAPER = "M-92,-60 L92,-60 L94,-30 C86,0 60,30 42,58 C30,76 -30,76 -42,58 C-60,30 -86,0 -94,-30Z"


def diaper(flat):
    c = "#DDEBF8" if flat else "#F6F5F1"
    band = "M-92,-60 L92,-60 L93,-44 L-93,-44Z"
    tabs = [rpoly([(-104, -48), (-86, -50), (-86, -26), (-102, -24)], 5), rpoly([(104, -48), (86, -50), (86, -26), (102, -24)], 5)]
    motif = "".join(star_d(x, y, 6, 2.7) for x, y in ((-46, -18), (-6, -26), (36, -14), (-22, 12), (20, 18), (0, 44)))
    if flat:
        o = [P(DIAPER, c), P("M-94,-30 C-86,0 -60,30 -42,58 C-30,76 30,76 42,58 C60,30 86,0 94,-30 C84,0 56,40 30,56 C10,64 -10,64 -30,56 C-56,40 -84,0 -94,-30Z", "#B9D2EC"),
             P(band, "#7CC8F2")] + [P(t, "#FFD84A") for t in tabs] + [P(motif, "#FFD84A")]
        return "".join(o), (-106, -64, 106, 74)
    shade = "#B8C4D2"
    inner = [hatch((-100, -70, 100, 80), 12, 45, shade, .35, .7), hatch((-100, -70, 100, 80), 12, -45, shade, .35, .7),
             spot(-20, -10, 60, 40, "#FFFFFF", .7), spot(40, 30, 50, 30, shade, .35), spot(0, 66, 40, 12, shade, .4),
             sline("M-90,-28 C-80,0 -58,30 -40,56", shade, 10, .5), sline("M90,-28 C80,0 58,30 40,56", shade, 10, .5),
             P(motif, "#F6CF4A", 'fill-opacity=".9"')]
    o = [shadow(0, 76, 80, 6), P(DIAPER, rg([(0, "#FFFFFF"), (.6, c), (1, "#DCE2EA")], .42, .3, .8)), clipped(DIAPER, "".join(inner)), rim(DIAPER, "#8E9AAA", 6, .4)]
    o.append(line("M-88,-26 C-78,4 -56,32 -38,58 M88,-26 C78,4 56,32 38,58", "#FFFFFF", 4, .9) +
             line("M-86,-24 C-76,6 -54,34 -36,60 M86,-24 C76,6 54,34 36,60", "#C9D3DE", 1.2, .7, dash="2 2.5"))
    o.append(P(band, lg([(0, "#BFE3F7"), (1, "#8CC8EA")], 0, 0, 0, 1)) + clipped(band, hatch((-96, -62, 96, -42), 3, 90, "#5E9CC4", .45, 1))
             + rim(band, "#4E86AE", 3, .35))
    for t in tabs:
        o.append(P(t, lg([(0, "#FFE680"), (1, "#F2C230")], 0, 0, 0, 1)) + rim(t, "#B8901C", 3, .4))
    return "".join(o), (-106, -64, 106, 80)


def bib(flat):
    c = "#58D3B0" if flat else "#8FD3BE"
    outer = curve([(-30, -112), (-50, -114), (-80, -78), (-98, -20), (-90, 40), (-56, 90), (0, 108), (56, 90), (90, 40), (98, -20), (80, -78),
                   (50, -114), (30, -112)], closed=False)
    d = outer + " C30,-80 18,-56 0,-56 C-18,-56 -30,-80 -30,-112Z"
    if flat:
        o = [P(d, c), clipped(d, line(d, "#FFC94A", 14)), P(heart_d(0, 34, 2.4), "#FF6B81"), '<circle cx="-40" cy="-96" r="7" fill="#FFFFFF"/>']
        return "".join(o), (-102, -118, 102, 112)
    rng = random.Random(11)
    inner = [specks(rng, 500, (-100, -116, 100, 110), "#FFFFFF", .35, (.6, 1.3)), specks(rng, 350, (-100, -116, 100, 110), dk(c, .4), .25, (.5, 1.1)),
             fold("M-60,-40 C-40,0 -30,40 -20,80", c, 14, .3, True), fold("M50,-30 C40,10 30,50 20,86", c, 10, .25),
             line(d, "#F7D778", 16), line(d, "#FFF4CC", 1.6, .9, dash="3 2")]
    o = [shadow(0, 112, 80, 6), P(d, fill_of(c, (-98, -114, 98, 108), False)), clipped(d, "".join(inner)), rim(d, dk(c, .5), 5, .35)]
    o.append(P(heart_d(0, 34, 2.4), lg([(0, "#FF9AAA"), (1, "#E8607A")], 0, 0, 0, 1)) + stitch(heart_d(0, 34, 2.1), "#FFFFFF", .9, .8, "2.4 2"))
    o.append(f'<circle cx="-40" cy="-96" r="7.5" fill="{rg([(0, "#FFFFFF"), (.7, "#E6ECEA"), (1, "#A5B2AE")], .4, .35, .6)}"/><circle cx="-40" cy="-96" r="2.6" fill="#C2CCC9"/>')
    return "".join(o), (-102, -118, 102, 116)


ITEMS = {"tshirt": tshirt, "pants": pants, "skirt": skirt, "jacket": jacket, "socks": socks, "shoes": shoes, "hat": hat, "gloves": gloves,
         "scarf": scarf, "pajamas": pajamas, "raincoat": raincoat, "rain_boots": rain_boots, "underwear": underwear, "vest": vest,
         "dress": dress, "shorts": shorts, "sweater": sweater, "slippers": slippers, "diaper": diaper, "bib": bib}


def main(only=None):
    for cid, fn in ITEMS.items():
        if only and cid not in only:
            continue
        for flat in (False, True):
            begin()
            body, box = fn(flat)
            write(DECK, cid, body, box, cartoon=flat, fill=.84)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)

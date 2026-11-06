"""The fruits deck of 小卡認天下: 20 fruits, each in two styles.

    python3 deck_fruits.py               # writes app/assets/art/cards/fruits/<id>.svg and <id>_cartoon.svg
    python3 deck_fruits.py apple kiwi    # only these
    python3 deck_fruits.py sheet out.png # a contact sheet of the deck

Realistic drawings look like the fruit sold in Taiwan: a 椪柑-style mandarin for 橘子, 巨峰 grapes,
愛文 mango, 水蜜桃 peach, 珍珠芭樂 (pale green, bumpy, white flesh), 黑珍珠蓮霧 (deep red bells),
甜柿 (flat, orange, four-lobed calyx), a netted 哈密瓜 with orange flesh and a long 台農 papaya.
Fruits people know best cut open (kiwi, papaya, watermelon, melon, guava) also show a cut piece.
The apple and banana follow the approved mockups (docs/mockups/make_mockups.py), redrawn without
SVG filters (see kit_af.py). Cartoon fruits are flat shapes with a white shine and no faces, so
they stay easy to tell apart.
"""
import math
import random
import sys

import kit_af as K
from kit_af import (C, E, P, S, along, at, blob, circ, clipped, dk, ell, form, glow, ground, haze, inside, lg, line, lt,
                    rg, rim, rrect, softfill, speckles, strokes, tube)

REAL, CARTOON = {}, {}
n_ = K.n


def real(fn):
    REAL[fn.__name__] = fn
    return fn


def cartoon(name):
    def deco(fn):
        CARTOON[name] = fn
        return fn
    return deco


# ---------------------------------------------------------------- shared bits
def leaf(bx, by, tx, ty, w, c1="#5E9A34", c2="#3A6E24", veins=4, light="#BFE08A", flip=False):
    """A leaf from its base (bx, by) to its tip (tx, ty), half-width w: gradient, midrib, a few veins."""
    L = math.hypot(tx - bx, ty - by)
    a = math.atan2(ty - by, tx - bx)
    ca, sa = math.cos(a), math.sin(a)

    def p(u, v):
        return (bx + u * L * ca - v * sa, by + u * L * sa + v * ca)
    side = [(.22, .78), (.55, 1.0), (.85, .5)]
    pts = [p(0, 0)] + [p(u, -v * w) for u, v in side] + [p(1, 0)] + [p(u, v * w) for u, v in reversed(side)]
    d = blob(pts)
    s = -1 if flip else 1
    vein = "".join(f"M{n_(p(u, 0)[0])},{n_(p(u, 0)[1])}L{n_(p(u + .16, s * -.7 * w)[0])},{n_(p(u + .16, s * -.7 * w)[1])}"
                   f"M{n_(p(u, 0)[0])},{n_(p(u, 0)[1])}L{n_(p(u + .16, s * .7 * w)[0])},{n_(p(u + .16, s * .7 * w)[1])}"
                   for u in [.18 + i * .65 / veins for i in range(veins)])
    mid = f"M{n_(p(0, 0)[0])},{n_(p(0, 0)[1])}L{n_(p(.96, 0)[0])},{n_(p(.96, 0)[1])}"
    lx, ly = p(.45, -s * .4 * w)
    inner = (glow(lx, ly, L * .32, w * .5, light, .45, rot=math.degrees(a))
             + f'<path d="{mid}" stroke="{light}" stroke-width="1.6" fill="none" opacity=".8"/>'
             + f'<path d="{vein}" stroke="{light}" stroke-width=".9" fill="none" opacity=".55"/>')
    return form(d, lg([(0, c1), (.6, mix_(c1, c2, .4)), (1, c2)], 0, 0, 1, 1), inner, dark="#0E2A06", op=.3, w=3)


def mix_(a, b, t):
    return K.mix(a, b, t)


def stem(pts, c1="#7A5634", c2="#3F2814"):
    return form(tube(pts), lg([(0, c1), (1, c2)], 0, 0, 1, 0), "", dark="#1A0E06", op=.3, w=2)


def shine(cx, cy, rx, ry, rot=0, op=.85, big=.28):
    """A soft window highlight plus its bright core (glossy skins)."""
    return (glow(cx + rx * 1.2, cy + ry * 1.0, rx * 2.6, ry * 2.4, "#FFFFFF", big, rot=rot)
            + glow(cx, cy, rx, ry, "#FFFFFF", op, rot=rot, hard=.5))


def ball(cx, cy, r, c0, c1, c2, sh=.8, bloom=None, rimc="#1A0A10"):
    """A round glossy fruit (grape, cherry, blueberry)."""
    d = circ(cx, cy, r)
    inner = ""
    if bloom:
        inner += glow(cx, cy, r * 1.1, r * 1.1, bloom, .35, hard=.5)
    inner += glow(cx - r * .35, cy - r * .4, r * .22, r * .16, "#FFFFFF", sh, rot=-35, hard=.5)
    inner += glow(cx + r * .45, cy + r * .5, r * .4, r * .25, lt(c0, .3), .35, rot=-35)
    return form(d, rg([(0, c0), (.55, c1), (1, c2)], .38, .35, .7), inner, dark=rimc, op=.38, w=r * .22)


# ================================================================ apple (red, with a leaf)
APPLE = ("M0,-58 C14,-72 44,-80 68,-66 C92,-52 98,-18 92,12 C86,44 70,72 48,82 C34,88 20,86 10,82 "
         "C4,80 -4,80 -10,82 C-20,86 -34,88 -48,82 C-70,72 -86,44 -92,12 C-98,-18 -92,-52 -68,-66 C-44,-80 -14,-72 0,-58Z")


@real
def apple():
    rng = random.Random(7)
    inner = [glow(56, 34, 44, 46, "#EDA548", .3)]
    st = []
    for i in range(30):
        t = -1 + 2 * i / 29 + rng.uniform(-.03, .03)
        st.append((f'M{t * 18:.1f},-56 Q{t * 106:.1f},{-4 + abs(t) * 4:.1f} {t * 50:.1f},{86 - abs(t) * 12:.1f}',
                   "#F68560" if i % 2 else "#7A0F14", rng.uniform(2.5, 6.5), rng.uniform(.1, .22)))
    inner.append("".join(f'<path d="{d}" stroke="{c}" stroke-width="{w:.1f}" fill="none" stroke-opacity="{o:.2f}"/>' for d, c, w, o in st))
    inner.append(speckles(rng, 110, (-92, -62, 92, 86), "#FBDDB0", (.6, 1.2), .5, inside(APPLE)))
    inner.append(glow(0, -54, 30, 13, "#45080C", .6))
    inner.append(haze("M-34,-64 Q0,-44 34,-64", "#FF9478", 2.4, .4, 1.5))
    inner.append(glow(-48, -22, 26, 38, "#FFFFFF", .26, rot=18))
    inner.append(glow(-54, -34, 6, 12, "#FFFFFF", .85, rot=24, hard=.5))
    inner.append(haze("M-72,58 Q0,104 72,58", "#FF8D74", 7, .2, 4))
    o = [ground(0, 90, 76, 9, .16),
         form(APPLE, rg([(0, "#F25A45"), (.42, "#D02B25"), (.78, "#A0181B"), (1, "#6C0D12")], .38, .38, .7, .32, .3),
              "".join(inner), dark="#3A0608", op=.35, w=7)]
    o.append(stem([(0, -50, 3.2), (1, -68, 2.9), (4, -86, 2.5), (10, -99, 2.4)]))
    o.append('<ellipse cx="10" cy="-99" rx="2.6" ry="1.6" transform="rotate(-30 10 -99)" fill="#A88760"/>')
    o.append(leaf(6, -80, 66, -104, 13, "#5E9A34", "#3A6E24"))
    return "".join(o)


@cartoon("apple")
def apple_c():
    return (S("M2,-56 C2,-74 6,-88 12,-98", "#6B4424", 9)
            + P("M10,-84 C22,-106 52,-110 68,-98 C52,-80 28,-74 10,-84Z", "#2DAA5C")
            + P(APPLE, "#E8262E")
            + E(-50, -24, 10, 21, "#FFFFFF", 20))


# ================================================================ banana
MID = [(-100, -10, 3.5), (-80, 12, 12), (-46, 30, 19), (-6, 37, 21.5), (34, 30, 20.5), (66, 10, 16), (88, -14, 10), (96, -28, 6.5)]
STALK = [(94, -25, 5.2), (101, -38, 4.6), (108, -50, 5.4)]


@real
def banana():
    rng = random.Random(4)
    body = tube(MID)
    inner = [haze(along(MID, .55), "#C99418", 14, .7, 5),
             haze(along(MID, .95), "#A97A12", 6, .55, 3),
             haze(along(MID, -.45, .1, .9), "#FFF0A0", 9, .8, 4),
             haze(along(MID, -.4, .25, .7), "#FFFFFF", 2.6, .5, 1.5),
             f'<path d="{along(MID, .05, .06, .96)}" stroke="#D6A626" stroke-width="1.2" fill="none" opacity=".55"/>',
             f'<path d="{along(MID, -.62, .1, .94)}" stroke="#E2B530" stroke-width="1" fill="none" opacity=".5"/>',
             glow(86, -12, 28, 24, "#9DAA2E", .55),
             glow(-96, -8, 11, 11, "#6A4A1A", .8)]
    sp = []
    for _ in range(16):
        x, y, a, w = at(MID, rng.uniform(.15, .85))
        f = rng.uniform(-.7, .8)
        sp.append(E(x + math.cos(math.radians(a + 90)) * w * f, y + math.sin(math.radians(a + 90)) * w * f,
                    rng.uniform(.8, 1.8), rng.uniform(.6, 1.2), "#7A5420", extra=f' opacity="{rng.uniform(.25, .5):.2f}"'))
    inner += sp
    o = [ground(0, 56, 96, 8, .14),
         form(body, "#EFC93A", "".join(inner), dark="#5A3A06", op=.3, w=5),
         form(tube(STALK), lg([(0, "#8E9A3A"), (1, "#5E6A26")], 0, 0, 1, 0), "", dark="#1A1E06", op=.3, w=2),
         E(108, -51, 5.6, 3.8, "#7A6A3A", -30), E(108, -51, 3.6, 2.2, "#A99A64", -30),
         C(-101, -11, 3.4, "#3A2812")]
    return "".join(o)


@cartoon("banana")
def banana_c():
    return (P(tube(MID), "#FFD43B")
            + P(tube([(-80, 12, 4), (-46, 30, 7), (-6, 37, 8), (34, 30, 7), (66, 10, 5)]), "#F2B807")
            + P(tube(STALK), "#7DA83A") + C(-101, -11, 4, "#6B4424")
            + S(along(MID, -.5, .2, .7), "#FFFFFF", 5))


# ================================================================ orange (橘子: a Taiwan mandarin)
@real
def orange():
    rng = random.Random(17)
    body = blob([(0, -70), (40, -76), (78, -60), (98, -24), (98, 18), (80, 54), (40, 74), (0, 78), (-40, 74), (-80, 54),
                 (-98, 18), (-98, -24), (-78, -60), (-40, -76)])
    inner = [glow(40, 40, 70, 46, "#C8500A", .45),
             glow(-40, -30, 46, 38, "#FFC060", .5),
             speckles(rng, 380, (-98, -76, 98, 78), "#B8540A", (.7, 1.4), .45, inside(body)),
             speckles(rng, 240, (-98, -76, 98, 78), "#FFD08A", (.5, 1.0), .5, inside(body)),
             glow(-42, -34, 14, 10, "#FFFFFF", .7, rot=-30, hard=.4),
             glow(0, -64, 22, 8, "#A84A08", .5),
             haze("M-60,-58 C-30,-70 30,-70 60,-58", "#FFB050", 3, .35, 2)]
    o = [ground(0, 80, 80, 8, .16),
         form(body, rg([(0, "#FFAA3A"), (.5, "#F28A1C"), (.85, "#E06E10"), (1, "#C4580A")], .4, .38, .7), "".join(inner), dark="#5A2004", op=.35, w=7),
         form(ell(0, -68, 9, 4), lg([(0, "#7A8A3A"), (1, "#4A5A20")]), "", dark="#1A2006", op=.3, w=2),
         stem([(0, -70, 2.6), (2, -80, 2.2), (6, -88, 2)], "#6A7A30", "#3E4A1A"),
         leaf(4, -84, 70, -112, 15, "#4E8A2E", "#2E5E1A"),
         leaf(0, -84, -46, -110, 11, "#5E9A34", "#3A6E24", flip=True)]
    return "".join(o)


@cartoon("orange")
def orange_c():
    body = blob([(0, -70), (40, -76), (78, -60), (98, -24), (98, 18), (80, 54), (40, 74), (0, 78), (-40, 74), (-80, 54),
                 (-98, 18), (-98, -24), (-78, -60), (-40, -76)])
    return (P(body, "#FF9417") + C(0, -70, 8, "#6E8A2E")
            + P(blob([(4, -78), (30, -104), (66, -104), (40, -80)]), "#2DAA5C")
            + E(-50, -30, 10, 20, "#FFFFFF", 35) + C(-62, 4, 5, "#FFFFFF"))


# ================================================================ grapes (巨峰: big dark purple grapes with bloom)
GRAPES = [(-48, -56), (-12, -62), (24, -60), (58, -50), (-64, -22), (-28, -26), (8, -28), (44, -22), (-44, 8), (-8, 4), (28, 6),
          (60, 10), (-26, 38), (10, 36), (42, 40), (-8, 68), (26, 70), (8, 98)]


@real
def grapes():
    rng = random.Random(27)
    o = [ground(6, 122, 56, 7, .16)]
    o.append(stem([(6, -84, 4), (4, -100, 3.4), (12, -118, 3)], "#8A7A4A", "#4A3E22"))
    o.append(S("M4,-84 C-10,-70 -30,-64 -48,-60 M8,-84 C22,-70 40,-60 56,-52", "#6E5E36", 2.6))
    o.append(leaf(10, -100, 84, -120, 26, "#6AA03C", "#3A6E24", veins=5))
    order = sorted(GRAPES, key=lambda p: p[1])
    for x, y in order:
        jx, jy = rng.uniform(-3, 3), rng.uniform(-3, 3)
        o.append(ball(x + jx, y + jy, 22, "#7A4A8A", "#4A2456", "#22101E", .6, bloom="#B8B0D8", rimc="#0A0408"))
        o.append(C(x + jx, y + jy - 20, 1.6, "#8A7A5A", ' opacity=".7"'))
    return "".join(o)


@cartoon("grapes")
def grapes_c():
    o = [S("M6,-84 L10,-112", "#6B4424", 8), P(blob([(10, -100), (40, -126), (80, -118), (52, -96)]), "#2DAA5C")]
    for x, y in sorted(GRAPES, key=lambda p: p[1]):
        o.append(C(x, y, 22, "#8E44AD"))
        o.append(C(x - 8, y - 8, 5, "#C79BDD"))
    return "".join(o)


# ================================================================ strawberry
SB = ("M0,-62 C30,-70 70,-62 84,-36 C96,-12 80,26 58,56 C40,80 18,98 4,100 C-12,100 -36,80 -56,54 "
      "C-80,22 -96,-14 -84,-38 C-70,-64 -30,-70 0,-62Z")


@real
def strawberry():
    rng = random.Random(37)
    test = inside(SB)
    seeds = []
    for row in range(13):
        y = -52 + row * 12.5 + rng.uniform(-1, 1)
        for col in range(-8, 9):
            x = col * 13.5 + (row % 2) * 6.7 + rng.uniform(-2.5, 2.5)
            if test(x, y) and test(x, y + 6) and test(x + 5, y) and test(x - 5, y):
                k = max(.55, 1 - (abs(x) / 100) ** 2)
                seeds.append((x, y, k))
    pits = "".join(f"M{n_(x - 2.6 * k)},{n_(y)}a{n_(2.6 * k)},{n_(3.4 * k)} 0 1 0 {n_(5.2 * k)},0a{n_(2.6 * k)},{n_(3.4 * k)} 0 1 0 {n_(-5.2 * k)},0" for x, y, k in seeds)
    seedp = "".join(f"M{n_(x - .3)},{n_(y - 1.4)}l.6,1.8" for x, y, k in seeds)
    inner = [glow(40, 40, 60, 50, "#7A0A10", .45),
             glow(-40, -10, 40, 50, "#FF7A6A", .45),
             f'<path d="{pits}" fill="#8A0E16" opacity=".5"/>',
             f'<path d="{seedp}" stroke="#D8B050" stroke-width="3" stroke-linecap="round" fill="none"/>',
             f'<path d="{seedp}" stroke="#FFF0B0" stroke-width="1.1" stroke-linecap="round" fill="none" transform="translate(-.5 -.7)"/>',
             glow(-44, -24, 10, 22, "#FFFFFF", .55, rot=20, hard=.4),
             glow(0, -54, 70, 14, "#5A0608", .5)]
    o = [ground(4, 104, 52, 7, .16),
         form(SB, rg([(0, "#F04A3E"), (.5, "#D8222A"), (1, "#9A0E16")], .4, .35, .75), "".join(inner), dark="#3A0408", op=.4, w=7)]
    cal = []
    for a in (-160, -125, -90, -55, -20, 10, -180):
        r = math.radians(a)
        tx, ty = 52 * math.cos(r), -60 + 26 * math.sin(r) + 30
        cal.append(leaf(0, -64, tx, ty, 9, "#5E9A34", "#2E5E1A", veins=2))
    o += cal
    o.append(stem([(0, -66, 3.6), (2, -84, 3.2), (6, -98, 3)], "#6E9A3A", "#3E6A1A"))
    return "".join(o)


@cartoon("strawberry")
def strawberry_c():
    seeds = "".join(E(x, y, 2.6, 4, "#FFE36A") for x, y in ((-40, -30), (0, -34), (40, -30), (-56, 4), (-20, 0), (20, 0), (56, 4),
                                                             (-36, 34), (0, 32), (36, 34), (-14, 64), (16, 64)))
    return (P(SB, "#F0263A") + seeds
            + P(blob([(-70, -54), (-40, -78), (-10, -68), (0, -90), (10, -68), (40, -78), (70, -54), (30, -56), (0, -50), (-30, -56)]), "#2DAA5C")
            + S("M0,-74 L4,-100", "#2DAA5C", 7)
            + E(-50, -20, 8, 16, "#FFFFFF", 20))


# ================================================================ watermelon (a whole striped melon and a slice)
@real
def watermelon():
    rng = random.Random(47)
    o = [ground(0, 96, 120, 9, .16)]
    whole = ell(-34, -10, 92, 76, -8)
    stripes = []
    for k in range(-5, 6):
        x = -34 + k * 17
        pts = [(x * .2 - 34 * .8 + (x + 34) * math.cos(math.radians(t)) * .0, 0) for t in range(1)]
        wob = "".join(f" {n_(-34 + (x + 34) * math.sin(math.radians(t)) + rng.uniform(-3, 3))},{n_(-10 - 80 * math.cos(math.radians(t)))}" for t in range(10, 180, 14))
        stripes.append(f'<path d="M{n_(-34)},-90 L{wob[1:].replace(" ", " L")} L-34,70" stroke-width="{rng.uniform(7, 10):.1f}"/>')
    inner = [f'<g stroke="#1E4A1A" fill="none" stroke-linejoin="round" opacity=".85">{"".join(stripes)}</g>',
             glow(-70, -50, 40, 30, "#D8F0A0", .4), glow(10, 30, 70, 50, "#0E2A0A", .45),
             speckles(rng, 120, (-126, -86, 58, 66), "#C8E0A0", (.5, 1), .4)]
    o.append(f'<g transform="rotate(-8 -34 -10)">' + form(ell(-34, -10, 92, 76), rg([(0, "#8CC860"), (.6, "#5E9E3A"), (1, "#3A6E24")], .4, .35, .7),
                                                          "".join(inner).replace('rotate(-8 -34 -10)', ''), dark="#0E2A06", op=.4, w=7) + "</g>")
    o.append(E(-102, -40, 4, 3, "#6A5A2A"))
    # the slice: a half-moon, cut face toward us
    cx, cy, R = 40, 40, 82
    rind = f"M{cx - R},{cy} A{R},{R} 0 0 0 {cx + R},{cy} Z"
    white = f"M{cx - R + 7},{cy} A{R - 7},{R - 7} 0 0 0 {cx + R - 7},{cy} Z"
    flesh = f"M{cx - R + 14},{cy} A{R - 14},{R - 14} 0 0 0 {cx + R - 14},{cy} Z"
    seeds = []
    for r_, ang in ((44, 30), (44, 60), (44, 90), (44, 120), (44, 150), (24, 50), (24, 90), (24, 130), (58, 45), (58, 75), (58, 105), (58, 135)):
        a = math.radians(ang)
        x, y = cx + r_ * math.cos(a), cy + r_ * math.sin(a) * .95
        ex, ey = x + 4 * math.cos(a), y + 4 * math.sin(a)
        seeds.append(f'<path d="M{n_(x)},{n_(y)} q{n_(math.cos(a + 1.3) * 3)},{n_(math.sin(a + 1.3) * 3)} {n_(ex - x)},{n_(ey - y)} q{n_(math.cos(a - 1.3) * 3 - (ex - x) * .0)},{n_(math.sin(a - 1.3) * 3)} {n_(x - ex)},{n_(y - ey)}Z" fill="#1A1210"/>')
    sl = (form(rind, lg([(0, "#3A7A2A"), (1, "#1E4A16")]), "", dark="#0E2A06", op=.4, w=3)
          + P(white, "#E8F2C8")
          + form(flesh, rg([(0, "#FF6A6A"), (.7, "#E8333F"), (1, "#C21E30")], .5, .1, .9),
                 speckles(rng, 90, (cx - R, cy, cx + R, cy + R), "#FF9A9A", (.6, 1.2), .5) + "".join(seeds)
                 + glow(cx - 20, cy + 14, 30, 12, "#FFFFFF", .25), dark="#6A0A10", op=.3, w=4)
          + f'<path d="M{cx - R},{cy} L{cx + R},{cy}" stroke="#FFB0A8" stroke-width="2" opacity=".6"/>')
    o.append(f'<g transform="rotate(-12 {cx} {cy})">{sl}</g>')
    return "".join(o)


@cartoon("watermelon")
def watermelon_c():
    cx, cy, R = 0, -10, 110
    seeds = "".join(E(cx + r_ * math.cos(math.radians(a)), cy + r_ * math.sin(math.radians(a)) * .95, 4, 7, "#2B211C", a - 90)
                    for r_, a in ((50, 40), (50, 90), (50, 140), (78, 60), (78, 120), (28, 90), (80, 25), (80, 155)))
    return (P(f"M{cx - R},{cy} A{R},{R} 0 0 0 {cx + R},{cy} Z", "#2E9E48")
            + P(f"M{cx - R + 12},{cy} A{R - 12},{R - 12} 0 0 0 {cx + R - 12},{cy} Z", "#E9F7C8")
            + P(f"M{cx - R + 22},{cy} A{R - 22},{R - 22} 0 0 0 {cx + R - 22},{cy} Z", "#FF4D5E")
            + seeds)


# ================================================================ pineapple (金鑽鳳梨)
@real
def pineapple():
    rng = random.Random(57)
    body = blob([(0, -50), (40, -46), (62, -20), (68, 20), (62, 64), (40, 98), (0, 108), (-40, 98), (-62, 64), (-68, 20), (-62, -20), (-40, -46)])
    test = inside(body)
    eyes = []
    for row in range(14):
        y = -46 + row * 12
        for col in range(-6, 7):
            x = col * 13 + (row % 2) * 6.5
            if not test(x, y):
                continue
            k = max(.45, 1 - (abs(x) / 70) ** 2)
            hw, hh = 6.4 * k, 6.4
            d = f"M{n_(x)},{n_(y - hh)} L{n_(x + hw)},{n_(y)} L{n_(x)},{n_(y + hh)} L{n_(x - hw)},{n_(y)}Z"
            eyes.append(d)
    eyes_d = "".join(eyes)
    inner = [f'<path d="{eyes_d}" fill="#E8A030" opacity=".55"/>',
             f'<path d="{eyes_d}" fill="none" stroke="#8A5A12" stroke-width="1.6" opacity=".7" stroke-linejoin="round"/>',
             f'<path d="{eyes_d}" fill="none" stroke="#FFE08A" stroke-width=".9" opacity=".6" transform="translate(-.8 -1)"/>',
             speckles(rng, len(eyes), (-66, -48, 66, 104), "#5A3A0A", (1, 1.6), .6, test),
             glow(-24, 0, 26, 60, "#FFE6A0", .45), glow(40, 40, 40, 70, "#8A5A12", .4),
             glow(0, 96, 50, 14, "#6A7A2A", .45)]
    o = [ground(0, 110, 64, 8, .16),
         form(body, lg([(0, "#F6C24A"), (.5, "#E8A42E"), (1, "#B87A1E")], 0, 0, 1, 0), "".join(inner), dark="#3A2204", op=.38, w=6)]
    for a, L, w, c1, c2 in ((-158, 66, 13, "#5E8A4A", "#2E5A2A"), (-22, 66, 13, "#5E8A4A", "#2E5A2A"),
                            (-140, 84, 14, "#6E9A5A", "#3E6A36"), (-40, 84, 14, "#6E9A5A", "#3E6A36"),
                            (-122, 100, 14, "#7AA864", "#46743C"), (-58, 100, 14, "#7AA864", "#46743C"),
                            (-104, 112, 13, "#86B26E", "#4E7E42"), (-76, 112, 13, "#86B26E", "#4E7E42"), (-90, 118, 12, "#92BC78", "#5A8A4A")):
        r = math.radians(a)
        tx, ty = L * math.cos(r), -40 + L * math.sin(r)
        o.append(leaf(0, -40, tx, ty, w, c1, c2, veins=0, light="#C8E0B0"))
    return "".join(o)


@cartoon("pineapple")
def pineapple_c():
    body = blob([(0, -50), (40, -46), (62, -20), (68, 20), (62, 64), (40, 98), (0, 108), (-40, 98), (-62, 64), (-68, 20), (-62, -20), (-40, -46)])
    grid = "".join(f'<path d="M{x},-60 L{x + 160},100" stroke="#E89A14" stroke-width="5"/><path d="M{x + 160},-60 L{x},100" stroke="#E89A14" stroke-width="5"/>'
                   for x in range(-200, 120, 26))
    leaves = "".join(P(f"M-12,-40 Q{x * .5},{-70} {x},{y} Q{x * .5 + 10},{-70} 12,-40Z", c)
                     for x, y, c in ((-50, -110, "#1F9D55"), (50, -110, "#1F9D55"), (-26, -140, "#2DBA66"), (26, -140, "#2DBA66"), (0, -156, "#1F9D55")))
    return leaves + P(body, "#FFC629") + clipped(body, grid) + E(-36, 0, 8, 22, "#FFFFFF", 10, ' opacity=".8"')


# ================================================================ mango (愛文: red blush to yellow)
MANGO = blob([(-96, -30), (-70, -58), (-20, -66), (40, -58), (88, -32), (110, 0), (104, 30), (76, 52), (20, 64), (-40, 60), (-86, 36), (-104, 4)])


@real
def mango():
    rng = random.Random(67)
    inner = [glow(-50, -30, 90, 50, "#C8202A", .75),
             glow(60, 36, 70, 40, "#F2C232", .6),
             glow(40, -20, 40, 30, "#E86A20", .4),
             glow(-20, 50, 60, 20, "#9AB83A", .3),
             speckles(rng, 170, (-106, -68, 112, 66), "#FFE8B0", (.5, 1.1), .55, inside(MANGO)),
             glow(-50, -34, 30, 9, "#FFFFFF", .5, rot=-18, hard=.4)]
    o = [ground(0, 66, 100, 8, .16),
         form(MANGO, lg([(0, "#D8302A"), (.45, "#F07A2A"), (1, "#F4C83A")], 0, 0, 1, 1), "".join(inner), dark="#4A1004", op=.35, w=7),
         glow(-88, -40, 10, 6, "#5A3A10", .6),
         stem([(-90, -42, 3.4), (-100, -52, 3), (-104, -62, 2.8)], "#6E8A3A", "#4A5A20")]
    return "".join(o)


@cartoon("mango")
def mango_c():
    return (P(MANGO, "#FFB72B") + clipped(MANGO, P(blob([(-110, -70), (30, -84), (44, -50), (20, -16), (-30, 4), (-80, 14), (-120, 0)]), "#FF5A3C"))
            + S("M-90,-42 L-104,-62", "#6E8A2E", 7)
            + E(-44, -34, 24, 8, "#FFFFFF", -18))


# ================================================================ pear (yellow-green, with a leaf)
PEAR = ("M0,-86 C14,-86 22,-74 26,-56 C30,-36 44,-20 62,4 C82,32 80,72 56,92 C34,108 -34,108 -56,92 C-80,72 -82,32 -62,4 "
        "C-44,-20 -30,-36 -26,-56 C-22,-74 -14,-86 0,-86Z")


@real
def pear():
    rng = random.Random(77)
    inner = [glow(40, 50, 60, 50, "#9AA030", .5), glow(-30, 10, 36, 50, "#FFF6A0", .5),
             glow(30, -10, 50, 40, "#D8B840", .3),
             speckles(rng, 150, (-82, -86, 82, 106), "#8A6A2A", (.5, 1.1), .45, inside(PEAR)),
             glow(-34, 20, 10, 26, "#FFFFFF", .5, rot=15, hard=.4),
             glow(0, 100, 20, 8, "#6A5A20", .4)]
    o = [ground(0, 108, 66, 8, .16),
         form(PEAR, rg([(0, "#F2E07A"), (.6, "#D8CC4A"), (1, "#A8A030")], .4, .55, .7), "".join(inner), dark="#3A3004", op=.35, w=7),
         stem([(0, -82, 3.4), (4, -98, 3), (10, -110, 2.8)]),
         leaf(6, -98, 66, -116, 14, "#6AA03C", "#3A6E24")]
    return "".join(o)


@cartoon("pear")
def pear_c():
    return (S("M0,-82 C2,-96 6,-104 10,-110", "#6B4424", 8)
            + P(blob([(8, -100), (40, -126), (76, -116), (46, -94)]), "#2DAA5C")
            + P(PEAR, "#C9DB3A") + E(-36, 20, 9, 22, "#FFFFFF", 15))


# ================================================================ peach (水蜜桃)
PEACH = ("M0,-70 C10,-82 40,-84 64,-66 C90,-46 98,-6 88,30 C76,70 40,92 4,94 C-34,94 -74,70 -86,30 C-98,-8 -88,-48 -62,-68 "
         "C-38,-84 -10,-82 0,-70Z")


@real
def peach():
    rng = random.Random(87)
    inner = [glow(-30, -10, 80, 70, "#E8506A", .7), glow(-50, -40, 40, 30, "#C82A4A", .5),
             glow(60, 50, 50, 40, "#FFE6A0", .65),
             haze("M0,-70 C-12,-40 -16,10 -6,90", "#B83A50", 5, .35, 4),
             haze("M3,-70 C-8,-40 -11,10 -1,90", "#FFD0C0", 3, .35, 3),
             strokes(rng, 260, (-96, -84, 96, 94), lambda x, y: math.radians(rng.uniform(0, 360)), ["#FFFFFF", "#FFE0D8"], (1.5, 3), .5, .35, .3, inside(PEACH)),
             glow(-46, -36, 22, 16, "#FFFFFF", .3, rot=-30)]
    o = [ground(0, 94, 76, 8, .16),
         form(PEACH, rg([(0, "#FFC8A8"), (.6, "#F8A890"), (1, "#E0806E")], .55, .5, .7), "".join(inner), dark="#5A1020", op=.32, w=7),
         stem([(0, -70, 3), (-2, -80, 2.6)]),
         leaf(-2, -78, 70, -110, 15, "#5E9A34", "#3A6E24"),
         leaf(-2, -78, -60, -104, 12, "#6AA03C", "#3A6E24", flip=True)]
    return "".join(o)


@cartoon("peach")
def peach_c():
    return (P(blob([(-2, -76), (40, -112), (80, -104), (44, -78)]), "#2DAA5C")
            + P(PEACH, "#FFC2A0") + clipped(PEACH, P(blob([(-110, -90), (10, -90), (-6, -20), (0, 60), (-20, 110), (-110, 60)]), "#FF8A96"))
            + S("M0,-66 C-12,-36 -14,10 -6,84", "#E8607A", 5)
            + E(-50, -30, 8, 16, "#FFFFFF", 30))


# ================================================================ cherry (two on joined stems)
@real
def cherry():
    o = [ground(0, 104, 90, 8, .16)]
    o.append(S("M-44,40 C-36,-10 -6,-60 22,-96", "#5E6A2A", 4.6) + S("M46,52 C40,0 30,-60 22,-96", "#5E6A2A", 4.6))
    o.append(S("M-44,40 C-36,-10 -6,-60 22,-96", "#9AA45A", 1.4, ' opacity=".6"') + S("M46,52 C40,0 30,-60 22,-96", "#9AA45A", 1.4, ' opacity=".6"'))
    o.append(leaf(22, -96, 96, -118, 20, "#5E9A34", "#3A6E24"))
    for cx, cy, r in ((-44, 66, 44), (46, 78, 44)):
        d = blob([(cx, cy - r * .82), (cx + r * .7, cy - r * .9), (cx + r, cy - r * .2), (cx + r * .7, cy + r * .75), (cx, cy + r),
                  (cx - r * .7, cy + r * .75), (cx - r, cy - r * .2), (cx - r * .7, cy - r * .9)])
        inner = (glow(cx, cy - r * .8, r * .5, r * .22, "#2A0006", .7)
                 + glow(cx - r * .38, cy - r * .3, r * .16, r * .26, "#FFFFFF", .85, rot=25, hard=.5)
                 + glow(cx - r * .2, cy - r * .2, r * .6, r * .6, "#FFFFFF", .12)
                 + glow(cx + r * .5, cy + r * .5, r * .5, r * .4, "#E83A4A", .35))
        o.append(form(d, rg([(0, "#D8203A"), (.55, "#A00E22"), (1, "#5A0410")], .38, .35, .7), inner, dark="#1A0004", op=.4, w=7))
    return "".join(o)


@cartoon("cherry")
def cherry_c():
    return (S("M-44,40 C-36,-10 -6,-60 22,-96 M46,52 C40,0 30,-60 22,-96", "#5E8A2A", 7)
            + P(blob([(22, -96), (56, -126), (100, -118), (64, -94)]), "#2DAA5C")
            + C(-44, 66, 44, "#E8203A") + C(46, 78, 44, "#E8203A")
            + E(-60, 52, 8, 13, "#FFFFFF", 25) + E(30, 64, 8, 13, "#FFFFFF", 25))


# ================================================================ kiwi (a whole one and a cut half)
@real
def kiwi():
    rng = random.Random(97)
    o = [ground(0, 86, 116, 9, .16)]
    whole = ell(-44, -16, 76, 58, -20)
    fuzz = strokes(rng, 520, (-126, -86, 34, 54), lambda x, y: math.radians(rng.uniform(0, 360)), ["#C8A878", "#5A4228", "#A88658"], (1.5, 3), .7, .55, .3, inside(whole))
    o.append(form(whole, rg([(0, "#A88458"), (.6, "#8A6A42"), (1, "#5E4428")], .4, .35, .7),
                  fuzz + glow(-70, -40, 30, 20, "#D8B888", .4) + glow(-110, 0, 8, 7, "#4A3220", .7), dark="#1A0E04", op=.4, w=7))
    # the cut half, face toward us
    cx, cy = 42, 20
    face = ell(cx, cy, 70, 64)
    seeds = []
    for i in range(46):
        a = 2 * math.pi * i / 46 + rng.uniform(-.04, .04)
        r = rng.uniform(22, 30)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a) * .92
        seeds.append(E(x, y, 1.4, 3.2, "#120E08", math.degrees(a) + 90))
    rays = "".join(f"M{n_(cx + 16 * math.cos(a))},{n_(cy + 15 * math.sin(a))}L{n_(cx + 58 * math.cos(a))},{n_(cy + 54 * math.sin(a))}"
                   for a in [2 * math.pi * i / 60 for i in range(60)])
    inner = (glow(cx, cy, 64, 58, "#C8E070", .5)
             + f'<path d="{rays}" stroke="#E8F6B8" stroke-width="1" opacity=".55"/>'
             + glow(cx, cy, 30, 27, "#7AAE2A", .35)
             + "".join(seeds)
             + form(ell(cx, cy, 14, 12), rg([(0, "#FFFDE8"), (1, "#E8EEB0")]), "", dark="#6A7A20", op=.2, w=2)
             + glow(cx - 30, cy - 30, 20, 10, "#FFFFFF", .35, rot=-40))
    o.append(form(ell(cx + 4, cy + 3, 72, 66), lg([(0, "#8A6A42"), (1, "#4A3420")]), "", dark="#1A0E04", op=.4, w=4))
    o.append(form(face, rg([(0, "#B8D850"), (.55, "#8EC03A"), (.92, "#6EA028"), (1, "#C8D878")], .5, .5, .5), inner, dark="#2A4A06", op=.25, w=4))
    return "".join(o)


@cartoon("kiwi")
def kiwi_c():
    cx, cy = 30, 20
    seeds = "".join(E(cx + 30 * math.cos(math.radians(a)), cy + 28 * math.sin(math.radians(a)), 2.6, 5, "#2B211C", a + 90) for a in range(0, 360, 30))
    return (E(-50, -20, 74, 56, "#9A6E44", -20)
            + C(cx + 4, cy + 3, 72, "#7A5434")
            + C(cx, cy, 66, "#7CC63A") + C(cx, cy, 50, "#A8DE56") + seeds + C(cx, cy, 14, "#FFF8D8"))


# ================================================================ lemon
LEMON = ("M-96,6 C-100,0 -98,-8 -90,-12 C-80,-46 -40,-70 6,-70 C52,-70 84,-46 92,-12 C100,-8 102,0 96,6 "
         "C90,10 92,14 88,18 C78,52 44,70 4,70 C-38,70 -76,52 -86,18 C-90,14 -92,10 -96,6Z")


@real
def lemon():
    rng = random.Random(107)
    inner = [glow(30, 30, 70, 40, "#C8A010", .45), glow(-30, -30, 50, 30, "#FFF6A0", .55),
             speckles(rng, 420, (-100, -72, 100, 72), "#C8A010", (.6, 1.3), .45, inside(LEMON)),
             speckles(rng, 260, (-100, -72, 100, 72), "#FFF8C0", (.5, 1), .55, inside(LEMON)),
             glow(-40, -36, 20, 10, "#FFFFFF", .6, rot=-14, hard=.4),
             glow(-96, 4, 8, 7, "#8A8A20", .5), glow(96, 4, 8, 7, "#8A8A20", .5)]
    o = [ground(0, 74, 84, 7, .16),
         form(LEMON, rg([(0, "#FFF080"), (.55, "#F8DA2A"), (1, "#D8B010")], .4, .35, .7), "".join(inner), dark="#4A3A02", op=.32, w=6),
         leaf(-86, -14, -40, -96, 15, "#5E9A34", "#3A6E24", flip=True)]
    return "".join(o)


@cartoon("lemon")
def lemon_c():
    return (P(blob([(-86, -14), (-90, -60), (-56, -100), (-50, -60)]), "#2DAA5C")
            + P(LEMON, "#FFE01B") + E(-36, -30, 22, 9, "#FFFFFF", -14))


# ================================================================ papaya (台農: long, a whole one and a cut half)
@real
def papaya():
    rng = random.Random(117)
    o = [ground(10, 96, 116, 9, .16)]
    whole = blob([(-120, -60), (-100, -82), (-60, -86), (0, -70), (50, -50), (80, -26), (86, 0), (64, 14), (10, 6), (-50, -10), (-100, -30)])
    o.append(form(whole, lg([(0, "#E8B830"), (.5, "#F2A030"), (1, "#C8A030")], 0, 0, 1, 1),
                  glow(-90, -60, 36, 20, "#7AA03A", .6) + glow(40, -30, 50, 20, "#F07A20", .35)
                  + haze("M-110,-62 C-60,-74 0,-60 70,-20", "#9AB040", 3, .35, 3)
                  + speckles(rng, 60, (-120, -86, 86, 14), "#7A8A2A", (.6, 1.2), .35, inside(whole))
                  + glow(-30, -64, 40, 8, "#FFFFFF", .3, rot=8), dark="#3A2204", op=.38, w=6)
             + stem([(-118, -62, 4), (-128, -66, 3.6)], "#6E8A3A", "#4A5A20"))
    # the cut half, lying in front: an oval of orange flesh with a seed cavity full of black seeds
    half = blob([(-90, 30), (-60, 6), (0, 0), (60, 8), (96, 30), (100, 56), (70, 80), (0, 88), (-60, 80), (-96, 58)])
    cav = blob([(-50, 34), (-20, 22), (20, 22), (54, 32), (58, 50), (30, 62), (-14, 62), (-46, 52)])
    seeds = []
    for _ in range(70):
        x, y = rng.uniform(-50, 56), rng.uniform(22, 62)
        if inside(cav)(x, y):
            seeds.append((x, y, rng.uniform(3, 4.4)))
    seeds.sort(key=lambda p: p[1])
    sd = "".join(f'<circle cx="{n_(x)}" cy="{n_(y)}" r="{n_(r)}" fill="url(#seedg)"/>' for x, y, r in seeds)
    K.D.add("seedg", '<radialGradient id="seedg" cx=".38" cy=".32" r=".7"><stop offset="0" stop-color="#6A6058"/><stop offset=".45" stop-color="#1E1A16"/><stop offset="1" stop-color="#0A0806"/></radialGradient>')
    o.append(form(half, lg([(0, "#E8C040"), (1, "#C89A20")]), "", dark="#3A2204", op=.4, w=4))
    o.append(form(blob([(-84, 32), (-58, 12), (0, 6), (58, 14), (90, 32), (94, 54), (66, 76), (0, 82), (-58, 74), (-90, 56)]),
                  rg([(0, "#FFA040"), (.6, "#F27A2A"), (1, "#E0601A")], .5, .5, .6),
                  glow(-40, 20, 30, 10, "#FFFFFF", .3) + form(cav, rg([(0, "#E86A20"), (1, "#B8441A")]), sd + glow(-20, 30, 10, 4, "#FFFFFF", .4), dark="#5A1A04", op=.3, w=3),
                  dark="#7A2A04", op=.25, w=4))
    return "".join(o)


@cartoon("papaya")
def papaya_c():
    whole = blob([(-120, -60), (-100, -82), (-60, -86), (0, -70), (50, -50), (80, -26), (86, 0), (64, 14), (10, 6), (-50, -10), (-100, -30)])
    half = blob([(-90, 30), (-60, 6), (0, 0), (60, 8), (96, 30), (100, 56), (70, 80), (0, 88), (-60, 80), (-96, 58)])
    inner = blob([(-80, 34), (-56, 14), (0, 8), (56, 16), (86, 34), (88, 54), (62, 74), (0, 80), (-56, 72), (-84, 54)])
    seeds = "".join(C(x, y, 5, "#2B211C") for x, y in ((-36, 40), (-20, 34), (-4, 42), (12, 34), (28, 42), (42, 38), (-26, 52), (-8, 54), (10, 50), (28, 54)))
    return (P(whole, "#FFC233") + clipped(whole, E(-110, -70, 40, 30, "#8CC63F"))
            + P(half, "#FFD54A") + P(inner, "#FF8A2A")
            + P(blob([(-50, 34), (-20, 24), (20, 24), (54, 32), (56, 50), (30, 60), (-14, 60), (-46, 52)]), "#E86A1A") + seeds)


# ================================================================ guava (珍珠芭樂: pale green, bumpy, white flesh)
GUAVA = ("M0,-80 C30,-82 60,-66 76,-40 C92,-12 92,26 74,56 C56,84 26,96 0,96 C-26,96 -56,84 -74,56 C-92,26 -92,-12 -76,-40 "
         "C-60,-66 -30,-82 0,-80Z")


@real
def guava():
    rng = random.Random(127)
    test = inside(GUAVA)
    bumps = []
    for _ in range(70):
        x, y = rng.uniform(-86, 86), rng.uniform(-76, 92)
        if test(x, y):
            r = rng.uniform(8, 14)
            bumps.append(glow(x - r * .25, y - r * .3, r * .7, r * .6, "#E8F4B0", .5, hard=.1))
            bumps.append(glow(x + r * .3, y + r * .35, r * .7, r * .55, "#6A8A2A", .22, hard=.1))
    inner = ["".join(bumps), glow(40, 50, 60, 50, "#5A7A20", .4), glow(-36, -36, 40, 30, "#F0F8C0", .5),
             speckles(rng, 80, (-90, -80, 90, 96), "#8A9A3A", (.6, 1.2), .4, test)]
    o = [ground(-10, 98, 110, 9, .16),
         f'<g transform="translate(-40 -16) scale(.92)">'
         + form(GUAVA, rg([(0, "#D8EC90"), (.6, "#B4D266"), (1, "#86A840")], .42, .4, .7), "".join(inner), dark="#1E3006", op=.36, w=7)
         + form(ell(0, -78, 10, 4), lg([(0, "#8A9A4A"), (1, "#5A6A2A")]), "", dark="#1A2006", op=.3, w=2)
         + stem([(0, -80, 3), (2, -92, 2.6)], "#7A6A3A", "#4A3A1A")
         + leaf(2, -90, 76, -112, 16, "#5E9A34", "#2E5E1A") + "</g>"]
    # the cut half in front: white flesh, a pale green rind, the creamy seedy middle
    cx, cy = 48, 46
    seeds = "".join(f"M{n_(cx + r * math.cos(t))},{n_(cy + r * math.sin(t) * .9)}h.1"
                    for r, t in ((rng.uniform(6, 22), rng.uniform(0, 6.283)) for _ in range(46)))
    o.append(form(ell(cx + 4, cy + 4, 66, 60), lg([(0, "#A8C860"), (1, "#6A8A2A")]), "", dark="#1E3006", op=.4, w=4))
    o.append(form(ell(cx, cy, 64, 58), rg([(0, "#FFFFFF"), (.75, "#F6F6EA"), (.92, "#E8EED0"), (1, "#C8DC90")], .5, .5, .5),
                  glow(cx, cy, 32, 28, "#F2E8C0", .9, hard=.5)
                  + f'<path d="{seeds}" stroke="#D8C890" stroke-width="3.2" stroke-linecap="round" fill="none"/>'
                  + f'<path d="{seeds}" stroke="#FFF8E0" stroke-width="1.2" stroke-linecap="round" fill="none" transform="translate(-.5 -.6)"/>'
                  + glow(cx - 30, cy - 30, 20, 9, "#FFFFFF", .6, rot=-40),
                  dark="#4A5A2A", op=.22, w=4))
    return "".join(o)


@cartoon("guava")
def guava_c():
    seeds = "".join(C(48 + 18 * math.cos(math.radians(a)), 46 + 16 * math.sin(math.radians(a)), 3, "#E2C86A") for a in range(0, 360, 45))
    return (f'<g transform="translate(-40 -16) scale(.92)">' + S("M0,-80 L2,-96", "#6B4424", 7)
            + P(blob([(2, -92), (36, -118), (76, -110), (44, -88)]), "#2DAA5C")
            + P(GUAVA, "#A8DE5A") + E(-40, -30, 9, 20, "#FFFFFF", 25) + "</g>"
            + E(48, 46, 66, 60, "#7CC63A") + E(48, 46, 58, 52, "#FFFFFF") + E(48, 46, 30, 27, "#FFF2C0") + seeds)


# ================================================================ wax apple (蓮霧: deep red bells)
def wax_bell(cx, cy, s, tilt, rng):
    pts = [(0, -62), (14, -60), (24, -48), (36, -26), (54, 0), (66, 26), (66, 48), (54, 62), (30, 66), (12, 60), (0, 58), (-12, 60),
           (-30, 66), (-54, 62), (-66, 48), (-66, 26), (-54, 0), (-36, -26), (-24, -48), (-14, -60)]
    a = math.radians(tilt)
    P_ = [(cx + (x * math.cos(a) - y * math.sin(a)) * s, cy + (x * math.sin(a) + y * math.cos(a)) * s) for x, y in pts]
    d = blob(P_)

    def T(x, y):
        return (cx + (x * math.cos(a) - y * math.sin(a)) * s, cy + (x * math.sin(a) + y * math.cos(a)) * s)
    hx, hy = T(-26, -10)
    lx, ly = T(26, 40)
    bx, by = T(0, 58)
    tx, ty = T(0, -56)
    ridges = "".join(f'M{n_(T(x0, -50)[0])},{n_(T(x0, -50)[1])} Q{n_(T(x0 * 1.6, 10)[0])},{n_(T(x0 * 1.6, 10)[1])} {n_(T(x0 * 2.1, 60)[0])},{n_(T(x0 * 2.1, 60)[1])}' for x0 in (-20, -8, 8, 20))
    inner = (glow(lx, ly, 40 * s, 30 * s, "#5A0414", .5)
             + f'<path d="{ridges}" stroke="#4A0010" stroke-width="{3 * s:.1f}" fill="none" opacity=".14"/>'
             + glow(hx, hy, 9 * s, 24 * s, "#FFFFFF", .8, rot=tilt + 18, hard=.4)
             + glow(hx, hy, 22 * s, 40 * s, "#FFFFFF", .15, rot=tilt + 18)
             + glow(*T(30, 8), 6 * s, 14 * s, "#FFFFFF", .45, rot=tilt - 20, hard=.4)
             + glow(bx, by, 40 * s, 10 * s, "#C83A5A", .4)
             + glow(tx, ty, 14 * s, 8 * s, "#2A0006", .5))
    cr = "".join(f'<ellipse cx="{n_(T(x, 56)[0])}" cy="{n_(T(x, 56)[1])}" rx="{n_(4 * s)}" ry="{n_(3 * s)}" fill="#5A0414" opacity=".8"/>' for x in (-9, -3, 3, 9))
    inner += cr
    return form(d, lg([(0, "#E0304E"), (.45, "#B0102E"), (1, "#6A0418")], 0, 0, 1, 1), inner, dark="#1A0006", op=.4, w=7 * s)


@real
def wax_apple():
    rng = random.Random(137)
    o = [ground(0, 96, 110, 9, .16)]
    o.append(wax_bell(-46, 4, 1.05, -14, rng))
    o.append(wax_bell(44, 18, 1.0, 12, rng))
    o.append(stem([(-46, -58, 3), (-48, -70, 2.6)], "#7A6A3A", "#4A3A1A"))
    o.append(stem([(32, -40, 3), (30, -52, 2.6)], "#7A6A3A", "#4A3A1A"))
    return "".join(o)


@cartoon("wax_apple")
def wax_apple_c():
    bell = blob([(0, -62), (14, -60), (24, -48), (36, -26), (54, 0), (66, 26), (66, 48), (54, 62), (30, 66), (12, 60), (0, 58), (-12, 60),
                 (-30, 66), (-54, 62), (-66, 48), (-66, 26), (-54, 0), (-36, -26), (-24, -48), (-14, -60)])
    return (f'<g transform="translate(-46 4) rotate(-14)">{P(bell, "#E5263E")}{E(-22, -6, 7, 18, "#FFFFFF", 18)}{S("M0,-58 L0,-72", "#6B4424", 6)}</g>'
            f'<g transform="translate(44 18) rotate(12)">{P(bell, "#C8102E")}{E(-22, -6, 7, 18, "#FFFFFF", 18)}{S("M0,-58 L0,-72", "#6B4424", 6)}</g>')


# ================================================================ lychee (a bunch on the twig, one peeled)
@real
def lychee():
    rng = random.Random(147)
    o = [ground(0, 100, 104, 8, .16)]
    o.append(stem([(-10, -110, 3.6), (-6, -80, 3.2), (0, -50, 3)], "#8A6A3A", "#4A3A1A"))
    o.append(S("M-4,-70 C-30,-60 -50,-40 -56,-20 M0,-56 C20,-50 40,-30 50,-10 M-2,-60 C-4,-40 -4,-10 -2,10", "#6E5434", 2.8))
    o.append(leaf(-10, -100, -94, -124, 15, "#3E7A2A", "#1E4A16", flip=True))
    o.append(leaf(-8, -96, 70, -126, 15, "#4E8A2E", "#2E5E1A"))
    for (cx, cy, r) in ((-56, 0, 40), (50, 10, 40), (-2, 36, 42)):
        d = blob([(cx + r * math.cos(t) * (1 if math.sin(t) > 0 else .96), cy + r * math.sin(t) * (1.05 if math.sin(t) > 0 else .95))
                  for t in [2 * math.pi * i / 10 for i in range(10)]])
        tb = []
        for row in range(-6, 7):
            for col in range(-6, 7):
                x, y = cx + col * 7 + (row % 2) * 3.5, cy + row * 6.4
                if (x - cx) ** 2 + (y - cy) ** 2 < (r * .96) ** 2:
                    tb.append((x, y))
        tri = "".join(f"M{n_(x)},{n_(y - 2.6)}l2.6,4.2h-5.2z" for x, y in tb)
        inner = (f'<path d="{tri}" fill="#6A0A14" opacity=".35"/>'
                 + f'<path d="{tri}" fill="#FF9A8A" opacity=".3" transform="translate(-.8 -1)"/>'
                 + glow(cx + r * .4, cy + r * .4, r * .7, r * .6, "#4A0610", .45)
                 + glow(cx - r * .35, cy - r * .4, r * .3, r * .2, "#FFFFFF", .35, rot=-30)
                 + glow(cx, cy - r * .9, r * .3, r * .15, "#8A6A2A", .6))
        o.append(form(d, rg([(0, "#F25A5A"), (.6, "#D02A3A"), (1, "#8A1020")], .4, .35, .7), inner, dark="#2A0006", op=.4, w=6))
    # one peeled, in front: white translucent flesh in its open red shell
    cx, cy = 62, 76
    o.append(form(blob([(cx - 42, cy - 4), (cx - 30, cy + 22), (cx, cy + 30), (cx + 30, cy + 22), (cx + 42, cy - 4), (cx + 20, cy + 6), (cx - 20, cy + 6)]),
                  lg([(0, "#D02A3A"), (1, "#8A1020")]), "", dark="#2A0006", op=.4, w=3))
    o.append(form(ell(cx, cy - 18, 30, 30), rg([(0, "#FFFFFF"), (.5, "#F2F0E6"), (1, "#C8C6B4")], .4, .35, .7),
                  glow(cx - 10, cy - 30, 8, 12, "#FFFFFF", .9, rot=-20, hard=.4) + glow(cx + 10, cy - 6, 14, 10, "#A8A694", .35)
                  + '<path d="M{0},{1} q4,-14 0,-28" stroke="#D8D6C4" stroke-width="2" fill="none" opacity=".7"/>'.format(n_(cx + 6), n_(cy - 4)),
                  dark="#4A4834", op=.3, w=4))
    return "".join(o)


@cartoon("lychee")
def lychee_c():
    bumps = lambda cx, cy: "".join(C(cx + x, cy + y, 3.4, "#B8162E") for x, y in ((-18, -14), (0, -20), (18, -14), (-22, 4), (0, 0), (22, 4), (-12, 20), (12, 20)))
    return (S("M-10,-110 L0,-50 M-4,-70 C-30,-60 -50,-40 -56,-20 M0,-56 C20,-50 40,-30 50,-10", "#7A5434", 6)
            + P(blob([(-10, -100), (-50, -126), (-94, -122), (-56, -98)]), "#2DAA5C")
            + C(-56, 0, 40, "#E5263E") + bumps(-56, 0) + C(50, 10, 40, "#E5263E") + bumps(50, 10)
            + C(-2, 36, 42, "#F03A4E") + bumps(-2, 36)
            + P("M20,72 Q62,110 104,72 Q62,88 20,72Z", "#C8102E") + C(62, 58, 30, "#FFFDF0") + E(52, 46, 6, 10, "#FFFFFF", -20))


# ================================================================ persimmon (甜柿: flat, glossy orange, four-lobed calyx)
PERS = blob([(0, -58), (50, -60), (88, -40), (104, -4), (96, 34), (66, 62), (24, 74), (-24, 74), (-66, 62), (-96, 34), (-104, -4), (-88, -40), (-50, -60)])


@real
def persimmon():
    rng = random.Random(157)
    inner = [glow(40, 40, 70, 40, "#B83A06", .5), glow(-40, -20, 50, 34, "#FFB050", .45),
             haze("M-30,-54 C-50,-20 -54,20 -40,66", "#C84A08", 4, .14, 4),
             haze("M34,-54 C54,-20 56,20 42,66", "#C84A08", 4, .14, 4),
             speckles(rng, 70, (-100, -60, 100, 72), "#FFD8A0", (.5, 1), .4, inside(PERS)),
             glow(-50, -24, 10, 22, "#FFFFFF", .75, rot=30, hard=.4),
             glow(0, -52, 50, 12, "#8A2A04", .5)]
    o = [ground(0, 76, 88, 8, .16),
         form(PERS, rg([(0, "#FFA040"), (.55, "#F27A1A"), (1, "#C8500A")], .42, .38, .7), "".join(inner), dark="#4A1404", op=.36, w=7)]
    lobes = []
    for a in (-170, -100, -20, 60):
        r = math.radians(a)
        L = 50
        tx, ty = L * math.cos(r), -56 + L * .38 * math.sin(r)
        nx, ny = -math.sin(r), math.cos(r) * .38
        lobes.append(blob([(0, -58), (tx * .45 + nx * 17, ty * .45 - 58 * .55 + ny * 17), (tx * .92, ty), (tx * .45 - nx * 17, ty * .45 - 58 * .55 - ny * 17)]))
    for d in lobes:
        o.append(form(d, lg([(0, "#8E8A44"), (1, "#5A5222")], 0, 0, 1, 1),
                      '<path d="M0,-58 L0,-58" stroke="none"/>', dark="#1A1A06", op=.35, w=3))
    o.append(stem([(0, -60, 4.2), (2, -72, 3.6)], "#6A5A2A", "#3A2E14"))
    return "".join(o)


@cartoon("persimmon")
def persimmon_c():
    return (P(PERS, "#FF8A1E")
            + E(0, -66, 12, 8, "#55701F") + E(-28, -58, 26, 10, "#6E8A2E", -6) + E(28, -58, 26, 10, "#6E8A2E", 6)
            + E(0, -50, 12, 14, "#7E9A34") + C(0, -60, 9, "#55701F")
            + S("M0,-62 L2,-80", "#6B4424", 7)
            + E(-52, -18, 9, 20, "#FFFFFF", 30))


# ================================================================ melon (哈密瓜: netted, orange flesh)
@real
def melon():
    rng = random.Random(167)
    o = [ground(0, 96, 118, 9, .16)]
    cx, cy, R = -26, -10, 84
    body = ell(cx, cy, R, R * .94)
    pts = {}
    for i in range(-8, 9):
        for j in range(-8, 9):
            pts[(i, j)] = (cx + i * 13 + rng.uniform(-4, 4), cy + j * 13 + rng.uniform(-4, 4))
    net = "".join(f"M{n_(pts[(i, j)][0])},{n_(pts[(i, j)][1])}L{n_(pts[(i + 1, j)][0])},{n_(pts[(i + 1, j)][1])}"
                  f"M{n_(pts[(i, j)][0])},{n_(pts[(i, j)][1])}L{n_(pts[(i, j + 1)][0])},{n_(pts[(i, j + 1)][1])}"
                  for i in range(-8, 8) for j in range(-8, 8))
    inner = (glow(cx + 30, cy + 30, 70, 60, "#4A5A20", .4) + glow(cx - 30, cy - 30, 40, 34, "#F0F0C8", .4)
             + f'<path d="{net}" stroke="#7A7A4A" stroke-width="3.2" fill="none" opacity=".35"/>'
             + f'<path d="{net}" stroke="#F2EED6" stroke-width="1.6" fill="none" opacity=".75"/>')
    o.append(form(body, rg([(0, "#C8CC8A"), (.6, "#A8B070"), (1, "#7A8A4A")], .42, .4, .7), inner, dark="#1E2A06", op=.38, w=7))
    o.append(form("M-34,-92 L-18,-92 L-22,-104 L-6,-108 L-6,-114 L-46,-114 L-46,-108 L-30,-104Z", lg([(0, "#9AA060"), (1, "#5A6030")]), "", dark="#1A1A06", op=.3, w=2))
    # the slice, in front: a crescent wedge of orange flesh with a green rind
    sx, sy = 54, 52
    rind = f"M{sx - 76},{sy - 6} A80,64 0 0 0 {sx + 80},{sy - 10} L{sx + 72},{sy - 18} A72,54 0 0 1 {sx - 68},{sy - 14}Z"
    flesh = f"M{sx - 68},{sy - 14} A72,54 0 0 0 {sx + 72},{sy - 18} L{sx + 44},{sy - 30} C{sx + 10},{sy - 40} {sx - 30},{sy - 38} {sx - 60},{sy - 22}Z"
    o.append(form(rind, lg([(0, "#B8C890"), (1, "#7A8A4A")]), "", dark="#1E2A06", op=.38, w=3))
    o.append(form(flesh, lg([(0, "#FFB060"), (.5, "#F79A40"), (1, "#E8842E")], 0, 0, 0, 1),
                  glow(sx, sy - 30, 50, 8, "#FFE0A0", .7) + glow(sx - 20, sy - 4, 24, 8, "#FFFFFF", .25)
                  + f'<path d="M{sx - 66},{sy - 16} A70,52 0 0 0 {sx + 70},{sy - 20}" stroke="#D8E0A0" stroke-width="4" fill="none" opacity=".8"/>',
                  dark="#7A3A04", op=.25, w=3))
    return "".join(o)


@cartoon("melon")
def melon_c():
    cx, cy, R = -20, -10, 86
    net = "".join(f'<path d="M{x},-110 Q{x + 20},-10 {x},96" stroke="#F6F2D8" stroke-width="4" fill="none"/>' for x in range(-90, 70, 24))
    net += "".join(f'<path d="M-120,{y} Q-20,{y + 14} 80,{y}" stroke="#F6F2D8" stroke-width="4" fill="none"/>' for y in range(-80, 80, 26))
    body = ell(cx, cy, R, R * .94)
    sx, sy = 58, 58
    return (P(body, "#B8C46A") + clipped(body, net)
            + P(f"M{sx - 76},{sy - 6} A80,64 0 0 0 {sx + 80},{sy - 10} L{sx + 44},{sy - 30} C{sx + 10},{sy - 40} {sx - 30},{sy - 38} {sx - 60},{sy - 22}Z", "#FF9A3C")
            + P(f"M{sx - 76},{sy - 6} A80,64 0 0 0 {sx + 80},{sy - 10} L{sx + 72},{sy - 18} A72,54 0 0 1 {sx - 68},{sy - 14}Z", "#8CC63F")
            + S("M-28,-96 L-28,-110 M-44,-110 L-12,-110", "#6E8A2E", 7))


# ================================================================ blueberry (a small heap)
@real
def blueberry():
    rng = random.Random(177)
    o = [ground(0, 84, 110, 9, .16)]
    berries = [(-56, -34, 34), (8, -46, 36), (64, -20, 34), (-74, 26, 34), (-14, 12, 38), (48, 38, 36), (-38, 62, 34), (22, 70, 32)]
    for cx, cy, r in sorted(berries, key=lambda b: b[1]):
        o.append(ball(cx, cy, r, "#5A6EA8", "#3A4A86", "#1E2650", .55, bloom="#B8C4E0", rimc="#0A0E20"))
        a = math.radians(rng.uniform(-60, -20))
        kx, ky = cx + r * .2 * math.cos(a), cy + r * .2 * math.sin(a) - r * .15
        star = K.blob([(kx + (6 if i % 2 == 0 else 2.6) * math.cos(math.radians(i * 36)), ky + (6 if i % 2 == 0 else 2.6) * math.sin(math.radians(i * 36)) * .8) for i in range(10)])
        o.append(f'<path d="{star}" fill="#2A2E48"/>' + C(kx, ky, 2.2, "#14182A") + glow(kx - 2, ky - 3, 4, 2, "#C8D0E8", .5))
    return "".join(o)


@cartoon("blueberry")
def blueberry_c():
    berries = [(-56, -34, 34), (8, -46, 36), (64, -20, 34), (-74, 26, 34), (-14, 12, 38), (48, 38, 36), (-38, 62, 34), (22, 70, 32)]
    o = []
    for cx, cy, r in sorted(berries, key=lambda b: b[1]):
        o.append(C(cx, cy, r, "#4A6CD8") + C(cx + r * .1, cy - r * .2, 6, "#2E3E8A") + E(cx - r * .45, cy - r * .3, 5, 9, "#A8C0FF", 30))
    return "".join(o)


# ================================================================ main
if __name__ == "__main__":
    K.main("fruits", REAL, CARTOON, sys.argv[1:])

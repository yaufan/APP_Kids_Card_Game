"""The animals deck of 小卡認天下: 20 animals, each in two styles.

    python3 deck_animals.py               # writes app/assets/art/cards/animals/<id>.svg and <id>_cartoon.svg
    python3 deck_animals.py dog cat       # only these
    python3 deck_animals.py sheet out.png # a contact sheet of the deck

Realistic drawings are side views facing right (the easiest view to know an animal by), with real
eyes and noses only. The dog, cat, cow and duck follow the approved mockups
(docs/mockups/make_mockups.py), redrawn without SVG filters (see kit_af.py).
Cartoon drawings are flat shapes with a simple cute face, in the same colours as the real animal,
so the child sees the same animal when switching styles.
"""
import math
import random
import sys

import kit_af as K
from kit_af import (C, E, P, S, along, at, blob, blush, circ, clipped, dk, dot_eye, dot_eyes, ell, eye, form, glow, ground,
                    haze, inside, lg, line, lt, rg, rim, rrect, smile, softfill, speckles, strokes, tube)

REAL, CARTOON = {}, {}


def real(fn):
    REAL[fn.__name__] = fn
    return fn


def cartoon(name):
    def deco(fn):
        CARTOON[name] = fn
        return fn
    return deco


def legs_back(legs, fill, dark="#3A1E10", op=.45, w=5):
    return "".join(form(tube(leg), fill, dark=dark, op=op, w=w) for leg in legs)


# ================================================================ dog (Shiba Inu, standing, with a collar)
DOG = ("M122,-50 C122,-57 116,-61 109,-62 C103,-63 99,-65 96,-70 C94,-75 92,-80 90,-83 "
       "C89,-91 87,-99 85,-104 C84,-106 82,-106 81,-104 C78,-98 74,-92 69,-88 "
       "C64,-84 59,-77 56,-68 C52,-56 44,-44 32,-36 C24,-32 18,-31 10,-31 "
       "C-14,-31 -38,-30 -56,-28 C-68,-27 -77,-21 -80,-9 C-84,6 -83,24 -76,36 "
       "C-72,44 -71,52 -73,60 C-74,68 -73,78 -73,84 C-73,87 -71,88 -68,88 L-51,88 C-48,88 -47,85 -49,83 "
       "C-53,78 -54,70 -54,62 C-54,52 -50,42 -44,34 C-42,28 -38,24 -32,22 "
       "C-16,24 0,28 14,31 C22,33 27,36 30,40 C31,56 31,72 31,84 C31,87 33,88 36,88 L55,88 C58,88 59,85 57,83 "
       "C53,78 51,70 51,60 C51,50 52,40 55,30 C58,18 62,6 66,-4 C70,-14 76,-22 84,-28 "
       "C92,-33 100,-36 108,-38 C114,-40 119,-43 122,-50Z")
FUR, CREAM = "#CD7B38", "#F3E4CC"


@real
def dog():
    rng = random.Random(11)
    o = [ground(-10, 91, 104, 8, .2)]
    farf = [(42, 30, 8.5), (43, 58, 7.5), (45, 82, 7)]
    farh = [(-50, 18, 11), (-58, 44, 8.5), (-62, 62, 7), (-60, 83, 6.6)]
    legfill = lg([(0, "#9C5220"), (.55, "#B8743A"), (.75, "#D8C3A6"), (1, "#C9B394")])
    for leg, paw in ((farf, (50, 86)), (farh, (-54, 86))):
        o.append(form(tube(leg), legfill, op=.4, w=4))
        o.append(E(paw[0], paw[1], 9.5, 3.8, "#C2AC8C"))
    o.append('<path d="M72,-90 C73,-97 74,-103 75,-107 C71,-102 66,-96 61,-92Z" fill="#9A5220"/>')
    # tail (curled over the back)
    tl = [(-58, -27, 8.5), (-66, -42, 10), (-60, -59, 10.5), (-43, -63, 10), (-32, -52, 9), (-36, -40, 7.5), (-46, -36, 5.5)]
    tail_in = (haze(along(tl, .6, .15, .95), CREAM, 6, .9)
               + glow(-50, -48, 8, 7, "#7A3E14", .5)
               + strokes(random.Random(5), 150, (-80, -76, -20, -24), lambda x, y: math.atan2(y + 48, x + 50) + 1.7,
                         ["#F7CB96", "#8E4A1A", "#FFF1DD"], (4, 7), .8, .38))
    o.append(form(tube(tl), lg([(0, "#E9AE6E"), (.5, FUR), (1, "#A95E28")], 0, 0, 1, 1), tail_in, op=.4, w=4))
    inner = [haze("M-80,-22 C-40,-32 10,-34 40,-42 L66,-82", "#8E4A1A", 12, .45, 6),
             glow(-8, -4, 60, 18, "#F2B270", .45),
             haze("M28,-26 C38,-8 42,14 38,38", "#9A5222", 4, .35, 3),
             haze("M-42,-22 C-30,-6 -34,16 -46,28", "#9A5222", 5, .35, 3),
             glow(-62, 6, 20, 24, "#F0AE6C", .45)]
    cream = [blob([(128, -52), (110, -54), (99, -58), (90, -64), (80, -62), (72, -54), (66, -40), (62, -20), (58, 4), (54, 30),
                   (46, 40), (60, 60), (84, 20), (110, -20), (132, -34)]),
             blob([(38, 42), (28, 34), (6, 29), (-18, 24), (-32, 22), (-44, 34), (-46, 48), (-30, 40), (-6, 38), (24, 44)]),
             blob([(-54, 62), (-52, 92), (-76, 94), (-75, 72), (-64, 66)]),
             blob([(30, 64), (29, 92), (61, 94), (54, 64)])]
    inner += [softfill(c, CREAM, 1, 2.5) for c in cream]
    inner.append(glow(89, -81, 5, 3.5, "#F1D9B4", .9))
    inner.append(haze("M115,-60 C107,-60 100,-64 96,-70", "#B0612A", 4, .45, 2))
    inner.append(glow(76, -52, 14, 10, "#EFC998", .45))

    def flow(x, y):
        if y > 36:
            return math.radians(92)
        if x > 56:
            return math.radians(118 if y > -40 else 150)
        return math.radians(172 + (y + 10) * .5)
    inner.append(strokes(rng, 360, (-86, -40, 126, 92), flow, ["#F3BE84", "#8E4A1A", "#FFE2BC", "#B66A2E"], (4, 7), .85, .28))
    inner.append(strokes(rng, 100, (-86, 10, 60, 92), flow, ["#FFFFFF", "#D7C2A3"], (4, 6), .8, .3))
    # collar
    inner.append(haze("M44,-58 C52,-42 62,-30 78,-22", "#3A1E10", 8, .3, 1.5))
    inner.append(S("M45,-58 C53,-42 63,-31 79,-24", lg([(0, "#3F86B0"), (1, "#24597A")], 0, 0, 1, 1), 6.5, cap="butt"))
    inner.append(S("M46,-59.5 C54,-44 64,-33 79.6,-26", "#8CC2E0", 1.2, ' opacity=".7"'))
    o.append(form(DOG, lg([(0, "#B5652A"), (.3, FUR), (.62, "#DD9552"), (1, "#E8B47A")], 0, -30, 0, 90, user=True),
                  "".join(inner), op=.36, w=6))
    o.append('<circle cx="72" cy="-21" r="3.4" fill="none" stroke="#C9CDD2" stroke-width="1.4"/>'
             f'<circle cx="72.5" cy="-14.5" r="4.6" fill="{rg([(0, "#FFE9A0"), (1, "#C9962A")], .4, .35)}"/>')
    tufts = []
    for (x, y, a, c) in [(63, 2, 160, CREAM), (59, 14, 170, CREAM), (56, 26, 175, CREAM), (67, -8, 150, CREAM),
                         (-82, 6, 190, FUR), (-82, 18, 195, FUR), (-78, -16, 200, FUR)]:
        a = math.radians(a)
        tufts.append(f'<path d="M{x:.1f},{y:.1f} q{math.cos(a) * 3:.1f},{math.sin(a) * 3:.1f} {math.cos(a) * 4.5 + 2:.1f},{math.sin(a) * 4.5 + 1.5:.1f}" stroke="{c}"/>')
    o.append(f'<g fill="none" stroke-width="1.6" stroke-linecap="round" opacity=".8">{"".join(tufts)}</g>')
    # face: nose, mouth, eye, inner ear
    o.append('<path d="M122,-50 C121,-55.5 117,-58.5 113,-58.5 C111,-56 111,-51 113,-48 C116,-46 120,-46 122,-50Z" fill="#1C1714"/>'
             + glow(117, -55.5, 3.5, 2, "#FFFFFF", .55)
             + '<path d="M116,-46.5 C113,-43.5 107,-41.5 101,-41.5" stroke="#3A2516" stroke-width="1.2" fill="none" stroke-linecap="round" opacity=".85"/>'
             + '<path d="M101,-41.5 C99,-41.6 97.5,-42.4 96.5,-43.6" stroke="#3A2516" stroke-width=".9" fill="none" stroke-linecap="round" opacity=".55"/>'
             + eye(90, -73.5, 3.6, "#4A2E1A", rot=-14)
             + haze("M83,-101 L75,-90", "#7E3E14", 2.4, .5, 1.2)
             + '<g fill="#3A2516" opacity=".45"><circle cx="107" cy="-51" r=".7"/><circle cx="103" cy="-50" r=".7"/>'
               '<circle cx="105" cy="-48" r=".7"/><circle cx="109" cy="-49" r=".7"/></g>')
    return "".join(o)


@cartoon("dog")
def dog_c():
    c, d, cr = "#F0913A", "#D9762A", "#FFF1DA"
    return (S("M-58,-14 C-92,-34 -84,-78 -54,-62", c, 15)
            + "".join(f'<rect x="{x}" y="0" width="19" height="82" rx="9.5" fill="{d}"/>' for x in (-48, 42))
            + "".join(f'<rect x="{x}" y="0" width="19" height="84" rx="9.5" fill="{c}"/>' for x in (-66, 24))
            + rrect(-74, -34, 136, 64, 32).join(['<path d="', f'" fill="{c}"/>'])
            + E(-4, 10, 44, 16, cr)
            + P("M30,-74 L34,-118 L62,-90Z", d) + P("M98,-74 L96,-118 L66,-92Z", d)
            + P("M36,-80 L38,-106 L54,-90Z", "#F7C9A6") + P("M92,-80 L91,-106 L74,-90Z", "#F7C9A6")
            + C(64, -58, 38, c)
            + E(64, -40, 22, 17, cr)
            + E(64, -48, 7.5, 5.5, INK)
            + smile(64, -38, 12, 4, 3)
            + dot_eyes(48, -64, 80, -64, 5.5)
            + blush(40, -46, 7, 4.5) + blush(88, -46, 7, 4.5)
            + S("M44,-22 Q64,-14 84,-22", "#3F86B0", 6))


INK = K.INK


# ================================================================ cat (grey tabby, sitting)
CAT = ("M74,-53 C73,-58 71,-62 67,-66 C64,-70 62,-74 60,-78 C58,-86 55,-96 52,-106 C46,-99 40,-92 34,-86 "
       "C26,-82 20,-74 18,-64 C15,-52 6,-42 -6,-32 C-26,-16 -44,6 -52,30 C-58,46 -60,64 -56,76 "
       "C-53,84 -46,88 -38,88 L58,88 C62,88 63,83 59,81 C56,80 54,78 54,74 C53,56 52,30 52,10 "
       "C52,-4 50,-16 48,-26 C52,-32 58,-36 64,-38 C69,-40 73,-45 74,-49 C75,-51 75,-52 74,-53Z")


@real
def cat():
    rng = random.Random(21)
    base, light, stripe = "#9C958B", "#E4DFD5", "#4B4641"
    o = [ground(0, 92, 84, 7, .2)]
    o.append('<path d="M30,-84 C33,-92 36,-100 40,-108 C44,-100 46,-94 46,-88Z" fill="#6E6860"/>')
    inner = [softfill(blob([(80, -44), (66, -40), (56, -34), (50, -20), (48, 10), (50, 60), (62, 60), (66, 0), (82, -30)]), light, 1, 3),
             glow(66, -45, 11, 8, light),
             glow(-22, 48, 40, 42, "#6F6961", .35),
             glow(-30, 36, 26, 28, "#C9C3B9", .55),
             haze("M36,16 C38,40 38,64 38,86", "#55504A", 3, .4, 2.5)]
    st = []
    for i in range(7):
        t = i / 6
        x0, y0 = -2 - t * 46, -34 + t * 52
        st.append(f'<path d="M{x0:.1f},{y0:.1f} q{10 + t * 4:.1f},10 {6 + t * 10:.1f},{26 - t * 4:.1f} t4,16" stroke-width="{rng.uniform(4, 6):.1f}"/>')
    st += ['<path d="M36,-84 C38,-78 40,-74 40,-68" stroke-width="2.4"/>', '<path d="M43,-86 C44,-80 45,-76 46,-70" stroke-width="2.2"/>',
           '<path d="M29,-80 C31,-74 32,-70 32,-64" stroke-width="2.2"/>', '<path d="M50,-60 C42,-58 34,-56 26,-56" stroke-width="2"/>',
           '<path d="M48,-54 C42,-50 36,-48 28,-48" stroke-width="2"/>', '<path d="M14,-58 C8,-48 0,-40 -8,-34" stroke-width="4"/>',
           '<path d="M24,-62 C18,-50 12,-42 4,-36" stroke-width="3"/>']
    inner.append(f'<g stroke="{stripe}" fill="none" stroke-linecap="round" opacity=".5">{"".join(st)}</g>')
    inner.append(f'<g stroke="{stripe}" fill="none" stroke-linecap="round" opacity=".18">{"".join(st).replace("stroke-width=", "data-w=").replace("data-w=", "stroke-width=")}</g>')

    def flow(x, y):
        if x > 40 and y > -30:
            return math.radians(95)
        return math.radians(120 + (x + 60) * .2) if y > -40 else math.radians(160)
    inner.append(strokes(rng, 340, (-60, -100, 76, 90), flow, ["#D6D0C6", "#5C564F", "#FFFFFF", "#7A736A"], (3, 6), .7, .3))
    o.append(form(CAT, lg([(0, "#7F786F"), (.35, base), (1, "#B5AFA5")], 0, -100, 0, 90, user=True), "".join(inner),
                  dark="#1E1A16", op=.34, w=5))
    tl = [(-50, 70, 7), (-48, 84, 7.5), (-26, 89, 7.5), (6, 90, 7), (30, 87, 6.5), (42, 82, 6)]
    rings = "".join(f'<path d="M{x + math.cos(math.radians(a + 90)) * w * 1.2:.1f},{y + math.sin(math.radians(a + 90)) * w * 1.2:.1f} '
                    f'L{x - math.cos(math.radians(a + 90)) * w * 1.2:.1f},{y - math.sin(math.radians(a + 90)) * w * 1.2:.1f}"/>'
                    for x, y, a, w in (at(tl, t) for t in (.25, .42, .58, .74, .9)))
    o.append(form(tube(tl), lg([(0, "#ABA49A"), (1, "#7A736A")]),
                  f'<g stroke="{stripe}" stroke-width="3.6" opacity=".55">{rings}</g>' + glow(42, 82, 9, 9, "#3E3934", .8),
                  dark="#1E1A16", op=.34, w=3))
    o.append('<path d="M57,-84 C55,-92 53,-99 52,-104 C49,-98 47,-92 46,-86Z" fill="#D9A69C" opacity=".75"/>'
             '<g stroke="#FFFFFF" stroke-width="1" fill="none" opacity=".75" stroke-linecap="round">'
             '<path d="M54,-90 l-3,-3"/><path d="M52,-87 l-4,-2"/><path d="M53,-94 l-3,-4"/></g>')
    # eye: green-gold with a slit pupil
    o.append('<ellipse cx="57" cy="-64" rx="5.4" ry="4.2" transform="rotate(-8 57 -64)" fill="#2E2A24"/>'
             f'<ellipse cx="57.6" cy="-64" rx="4.4" ry="3.4" transform="rotate(-8 57 -64)" fill="{rg([(0, "#E3DC70"), (.7, "#B2B04A"), (1, "#7E8A34")])}"/>'
             '<ellipse cx="58.6" cy="-64" rx="1" ry="3.1" fill="#15120F"/>'
             '<circle cx="56.4" cy="-65.6" r="1" fill="#FFFFFF" opacity=".9"/>'
             '<path d="M51.4,-63.6 C54,-68.2 60,-68.8 62.6,-65.4" stroke="#2E2A24" stroke-width="1.2" fill="none"/>'
             '<path d="M74,-53 L70.4,-52.6 L72.2,-49.2Z" fill="#C98580"/>'
             '<path d="M72.4,-49.4 C72.6,-46.6 71.6,-44.6 69.6,-43.6 M72.4,-46.4 C70.4,-45 68.2,-45.2 66.6,-46.6" stroke="#4A3E38" stroke-width=".9" fill="none" opacity=".7"/>'
             '<g stroke="#FFFFFF" stroke-width=".8" fill="none" opacity=".85" stroke-linecap="round">'
             '<path d="M68,-47 Q84,-52 100,-50"/><path d="M68,-46 Q86,-47 100,-42"/><path d="M67,-45 Q82,-42 96,-34"/>'
             '<path d="M62,-70 Q70,-80 76,-84"/></g>'
             '<g fill="#5A524A" opacity=".5"><circle cx="69" cy="-47.5" r=".6"/><circle cx="67" cy="-46.5" r=".6"/><circle cx="68.5" cy="-45" r=".6"/></g>')
    return "".join(o)


# ================================================================ cow (Holstein, standing)
COW = ("M121,4 C122,-6 118,-20 110,-32 C106,-40 100,-46 94,-48 C86,-48 78,-44 68,-44 C50,-46 20,-48 -10,-47 "
       "C-40,-47 -70,-48 -88,-50 C-96,-51 -102,-48 -104,-42 C-108,-30 -108,-14 -106,0 C-104,14 -100,26 -96,36 "
       "C-95,44 -96,52 -96,60 L-95,82 L-96,88 L-82,88 L-83,82 C-84,70 -84,58 -82,48 C-80,36 -76,28 -70,24 "
       "C-40,32 0,32 32,28 L34,82 L33,88 L48,88 L48,82 L50,40 C54,26 60,14 66,8 C74,4 84,6 94,12 "
       "C102,16 110,20 116,18 C121,16 123,12 121,4Z")


@real
def cow():
    rng = random.Random(31)
    o = [ground(0, 91, 120, 8, .2)]
    for leg in ([(24, 18, 9), (25, 56, 7), (26, 84, 6.6)], [(-74, 22, 10), (-82, 52, 7), (-84, 84, 6.6)]):
        o.append(form(tube(leg), lg([(0, "#BDB8B0"), (1, "#A29C94")]), dark="#1E1A16", op=.4, w=4))
        x = leg[-1][0]
        o.append(f'<rect x="{x - 7}" y="80" width="14" height="9" rx="3" fill="#3A3634"/>')
    o.append(f'<path d="{tube([(-104, -42, 2.6), (-109, -26, 2.2), (-111, 10, 2), (-109, 44, 2)])}" fill="#D9D5CE"/>'
             f'<path d="{blob([(-109, 40), (-104, 50), (-106, 62), (-110, 64), (-114, 52)])}" fill="#2A2A2C"/>')
    blk = lg([(0, "#3A3A3C"), (1, "#141416")])
    patches = [blob([(64, -50), (96, -54), (120, -24), (126, 8), (110, 26), (84, 14), (64, 8), (56, -20)]),
               blob([(16, -52), (58, -50), (62, -22), (48, -2), (28, -8), (12, -26)]),
               blob([(-44, -52), (-2, -52), (6, -26), (-6, 2), (-30, 8), (-48, -14)]),
               blob([(-112, -48), (-76, -54), (-64, -32), (-78, -10), (-98, -12), (-112, -26)]),
               blob([(-22, 16), (2, 18), (6, 34), (-26, 34)])]
    inner = ["".join(f'<path d="{p}" fill="{blk}"/>' for p in patches),
             f'<path d="{blob([(100, -44), (108, -40), (116, -14), (119, 0), (112, 2), (106, -16), (98, -36)])}" fill="#F4F2EE"/>',
             glow(116, 8, 12, 14, "#C99C96", 1, hard=.6),
             glow(-14, -36, 80, 10, "#FFFFFF", .25),
             haze("M-70,30 C-40,36 0,36 32,30", "#8C867E", 8, .32, 5),
             haze("M-60,-40 C-56,-10 -64,14 -74,26", "#7C766E", 4, .28, 4),
             haze("M40,-30 C46,-6 46,14 42,30", "#7C766E", 3, .22, 3),
             strokes(rng, 220, (-108, -50, 124, 88), lambda x, y: math.radians(100 if y > 30 else 160), ["#FFFFFF", "#7A746C", "#5A5650"], (3, 5), .6, .2)]
    o.append(form(COW, lg([(0, "#FBFAF7"), (.6, "#EEEBE5"), (1, "#C9C4BC")], 0, -50, 0, 90, user=True), "".join(inner),
                  dark="#1E1A16", op=.32, w=6))
    o.append(f'<path d="M-62,26 C-64,38 -58,44 -50,44 C-42,44 -38,38 -40,26Z" fill="{lg([(0, "#E9B7AE"), (1, "#C98F86")])}"/>'
             '<path d="M-56,43 L-57,50 M-46,43 L-45,50" stroke="#D49C94" stroke-width="3" stroke-linecap="round"/>')
    o.append('<path d="M-96,82 L-82,82 L-81,89 L-97,89Z" fill="#3A3634"/><path d="M34,82 L48,82 L49,89 L33,89Z" fill="#3A3634"/>')
    o.append(f'<ellipse cx="80" cy="-40" rx="13" ry="5.5" transform="rotate(18 80 -40)" fill="{blk}"/>'
             '<ellipse cx="79" cy="-39" rx="8" ry="2.6" transform="rotate(18 79 -39)" fill="#B88A84"/>'
             f'<path d="{tube([(92, -48, 3.2), (94, -55, 2.4), (99, -61, 1.4)])}" fill="{lg([(0, "#EDE3C8"), (1, "#A89C7E")])}"/>'
             + eye(101, -26, 3, "#3A2A20", rot=-30)
             + '<ellipse cx="119" cy="4" rx="2" ry="3.2" transform="rotate(-20 119 4)" fill="#4A2E2A" opacity=".8"/>'
             '<path d="M118,14 C114,16 110,16 106,14" stroke="#5A3A36" stroke-width="1" fill="none" opacity=".6"/>')
    return "".join(o)


# ================================================================ duck (mallard drake, standing)
DUCK = ("M74,-54 C72,-70 56,-80 44,-74 C36,-70 32,-60 34,-48 C36,-36 34,-24 30,-14 "
        "C10,-14 -30,-12 -58,-10 L-78,-14 C-86,-16 -90,-10 -84,-4 L-70,6 C-60,30 -30,44 0,44 "
        "C34,44 52,26 52,8 C52,-6 48,-20 48,-30 C50,-36 58,-40 66,-40 Z")


@real
def duck():
    rng = random.Random(41)
    o = [ground(4, 74, 76, 6, .2)]
    for x, c in ((-8, "#C9701E"), (6, "#E8892E")):
        o.append(f'<path d="M{x},38 L{x + 1},62" stroke="{c}" stroke-width="5.5" stroke-linecap="round"/>'
                 f'<path d="M{x - 2},61 L{x + 18},67 L{x + 16},72 L{x - 3},71 Z" fill="{c}" stroke="{c}" stroke-width="2" stroke-linejoin="round"/>')
    inner = [f'<path d="{blob([(30, -40), (33, -56), (38, -72), (50, -82), (66, -80), (78, -60), (76, -42), (58, -36), (48, -30), (32, -34)])}" '
             f'fill="{lg([(0, "#2A6E86"), (.35, "#1F7A4C"), (.7, "#16603A"), (1, "#0F4A2C")], 0, 0, 1, 1)}"/>',
             glow(50, -68, 13, 8, "#6FD0A0", .45),
             f'<path d="{blob([(30, -28), (50, -28), (56, 8), (46, 32), (26, 40), (14, 14), (20, -10)])}" fill="{lg([(0, "#8A4A30"), (1, "#5E2E1E")])}"/>',
             '<path d="M30,-33 C38,-30 44,-28 50,-28" stroke="#FFFFFF" stroke-width="3.6" fill="none"/>',
             f'<path d="{blob([(-60, -12), (-74, -12), (-82, -6), (-70, 8), (-58, 6)])}" fill="#1A1A1C"/>',
             haze("M-70,30 C-40,46 0,48 40,36", "#6E6F6A", 8, .32, 5)]
    inner.append('<path d="' + "".join(f'M{n_(x)},{n_(y)}q3,-1.5 6,0t6,0' for x, y in ((rng.uniform(-60, 10), rng.uniform(-6, 40)) for _ in range(70)))
                 + '" stroke="#8A8C88" stroke-width=".6" fill="none" opacity=".35"/>')
    wing = blob([(28, -14), (0, -17), (-40, -15), (-66, -10), (-56, 4), (-30, 12), (0, 12), (22, 4)])
    win = ('<path d="' + "".join(f'M{x},{-14 + k * 7}q-8,6 -16,5' for k in range(4) for x in range(26 - k * 4, -60, -15))
           + '" stroke="#6E675C" stroke-width=".9" fill="none" opacity=".55"/>'
           + f'<path d="{blob([(-46, -1), (-28, 2), (-27, 8), (-45, 6)])}" fill="{lg([(0, "#4E62B0"), (1, "#30407E")])}" opacity=".9"/>'
           + '<path d="M-48,-2 L-26,1 M-46,7.5 L-25,9" stroke="#FFFFFF" stroke-width="1" opacity=".7"/>')
    inner.append(form(wing, lg([(0, "#B2AA9C"), (1, "#8C8476")]), win, dark="#1E1A16", op=.3, w=3))
    o.append(form(DUCK, lg([(0, "#D7D8D5"), (1, "#A9AAA6")]), "".join(inner), dark="#1E1A16", op=.32, w=5))
    o.append('<path d="M-66,-12 C-72,-24 -62,-28 -60,-21" stroke="#1A1A1C" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="{blob([(-80, -8), (-87, -11), (-90, -6), (-86, -1), (-80, -1)])}" fill="#D9D9D4"/>')
    bill = "M72,-55 C82,-53 92,-50 99,-46 C101,-44 100,-42 97,-41 C88,-40 78,-40 66,-41 C64,-46 66,-52 72,-55Z"
    o.append(form(bill, lg([(0, "#E8D460"), (1, "#B7A030")]), dark="#4A3A10", op=.3, w=2)
             + '<path d="M95,-45.5 C98,-45 100,-43.5 99,-42 C97,-41 95,-41.5 94.5,-43Z" fill="#2A2A22"/>'
             '<path d="M70,-46 C80,-45 90,-44 97,-43" stroke="#8A7A22" stroke-width=".8" fill="none" opacity=".7"/>'
             '<ellipse cx="79" cy="-50" rx="2.2" ry="1" fill="#5A5020"/>'
             + eye(56, -62, 2.6, "#2A1A0C"))
    return "".join(o)


def n_(v):
    return K.n(v)


def cloud(cx, cy, rx, ry, k=18, out=1.0, rot=0.0, jit=0.0, seed=1):
    """A woolly edge: arcs bulging out between points on an ellipse."""
    rng = random.Random(seed)
    a0 = math.radians(rot)
    pts = []
    for i in range(k):
        t = 2 * math.pi * i / k + rng.uniform(-jit, jit)
        pts.append((cx + rx * math.cos(t + a0), cy + ry * math.sin(t + a0)))
    d = f"M{n_(pts[0][0])},{n_(pts[0][1])}"
    for i in range(k):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % k]
        r = math.hypot(x1 - x0, y1 - y0) / 2 * out * rng.uniform(1.0, 1.15)
        d += f"A{n_(r)},{n_(r)} 0 0 1 {n_(x1)},{n_(y1)}"
    return d + "Z"


def hoof_leg(pts, fill, hoof="#3A3230", hw=None, dark="#2A1A10", op=.42):
    """A leg tube with a hoof at its foot."""
    x, y, w = pts[-1]
    hw = hw or w * 1.15
    h = f"M{n_(x - hw)},{n_(y - 6)} L{n_(x + hw)},{n_(y - 6)} L{n_(x + hw + 2)},{n_(y + 3)} L{n_(x - hw - 1)},{n_(y + 3)}Z"
    return form(tube(pts[:-1] + [(x, y - 4, w)]), fill, dark=dark, op=op, w=4) + form(h, lg([(0, lt(hoof, .2)), (1, hoof)]), dark="#000", op=.3, w=2)


# ================================================================ rabbit (brown, sitting)
@real
def rabbit():
    rng = random.Random(51)
    base, belly, back = "#B08560", "#EADBC6", "#7C5838"
    o = [ground(-8, 90, 96, 7, .2)]
    # far ear, then the body
    far = tube([(70, -74, 7), (68, -104, 10), (62, -136, 9), (56, -156, 4)])
    o.append(form(far, lg([(0, "#8A6444"), (1, "#6E4E32")]), glow(64, -110, 6, 26, "#D9A08C", .7), op=.4, w=3))
    body = blob([(-88, 70), (-92, 40), (-80, 6), (-56, -24), (-24, -40), (10, -44), (34, -50), (46, -66), (62, -80), (82, -80),
                 (98, -66), (106, -52), (104, -42), (94, -34), (80, -30), (68, -24), (62, -6), (64, 20), (68, 52), (72, 76),
                 (76, 86), (60, 90), (44, 88), (20, 84), (-10, 90), (-60, 90), (-82, 84)])
    def flow(x, y):
        if x > 40 and y < -20:
            return math.radians(200)
        return math.radians(150 + (y + 40) * .45)
    inner = [softfill(blob([(104, -44), (90, -36), (74, -30), (64, -16), (60, 20), (66, 60), (72, 86), (40, 88), (40, 40), (52, -10), (72, -40)]), belly, .95, 3),
             glow(-20, -24, 70, 20, back, .5),
             glow(-40, 40, 46, 44, "#8C6646", .35),
             glow(-46, 30, 30, 30, "#D2AE88", .4),
             haze("M-60,84 C-40,60 -4,58 20,80", "#6E4E32", 4, .45, 3),
             glow(84, -64, 16, 10, "#D7B48C", .5),
             strokes(rng, 330, (-96, -84, 108, 92), flow, ["#D9B790", "#6E4E32", "#F4E6D2", "#946C48"], (3, 6), .7, .32)]
    o.append(form(body, lg([(0, "#9C7350"), (.45, base), (1, "#C7A27C")], 0, -80, 0, 90, user=True), "".join(inner), op=.36, w=5))
    # hind foot, front paw
    foot = blob([(-64, 80), (-30, 78), (10, 82), (18, 88), (10, 92), (-60, 92)])
    o.append(form(foot, lg([(0, "#C9A57E"), (1, "#E4D2B8")]), op=.3, w=3))
    paw = tube([(62, 30, 7), (66, 60, 6.5), (72, 84, 6.5)])
    o.append(form(paw, lg([(0, "#D9C2A2"), (1, "#EADBC6")], 0, 0, 1, 0), op=.32, w=3))
    # tail
    o.append(form(circ(-88, 52, 14), rg([(0, "#FFFFFF"), (.7, "#F1ECE4"), (1, "#D9D0C4")], .4, .35, .6),
                  strokes(random.Random(3), 50, (-104, 36, -72, 68), lambda x, y: math.atan2(y - 52, x + 88), ["#FFFFFF", "#C9BFB2"], (2, 4), .6, .5),
                  dark="#3A2E20", op=.3, w=3))
    # near ear
    ear = tube([(58, -74, 8), (52, -106, 11), (42, -138, 10), (32, -160, 4)])
    o.append(form(ear, lg([(0, "#9C7350"), (.5, "#B08560"), (1, "#7C5838")], 0, 0, 1, 0),
                  softfill(tube([(56, -82, 3), (50, -106, 6), (42, -134, 5), (36, -150, 2)]), "#E2A99A", .75, 2)
                  + glow(34, -152, 10, 12, "#4A3020", .5)
                  + strokes(random.Random(8), 50, (26, -160, 66, -76), lambda x, y: math.radians(-100), ["#D9B790", "#6E4E32"], (3, 5), .6, .3),
                  op=.4, w=3))
    o.append(eye(80, -60, 5.4, "#3A2414", rot=-6, lidop=.5)
             + '<ellipse cx="80" cy="-60" rx="8.6" ry="7.2" fill="none" stroke="#E7D3BA" stroke-width="1.6" opacity=".55"/>'
             + f'<path d="M104,-48 C105,-45 103,-42 100,-43 C99,-46 101,-48 104,-48Z" fill="#9A6A62"/>'
             + '<path d="M101,-42 C100,-38 96,-36 92,-37" stroke="#6A4A3A" stroke-width="1" fill="none" opacity=".7"/>'
             + '<g stroke="#FFFFFF" stroke-width=".6" fill="none" opacity=".8" stroke-linecap="round">'
             '<path d="M98,-42 Q114,-46 128,-44"/><path d="M98,-41 Q114,-40 126,-34"/><path d="M97,-40 Q110,-34 120,-26"/></g>')
    return "".join(o)


@cartoon("rabbit")
def rabbit_c():
    c, d, cr, pk = "#C9A27A", "#B08760", "#FFF4E4", "#F7B6B0"
    return (C(-66, 46, 16, "#FFFFFF")
            + E(-6, 42, 60, 50, c)
            + E(4, 52, 34, 36, cr)
            + E(-50, 84, 26, 11, d) + E(34, 86, 22, 10, c) + E(-22, 88, 20, 9, c)
            + P(tube([(-22, -70, 13), (-30, -110, 14), (-32, -146, 11)]), c) + P(tube([(22, -70, 13), (30, -110, 14), (32, -146, 11)]), c)
            + P(tube([(-23, -82, 5), (-30, -112, 7), (-31, -140, 5)]), pk) + P(tube([(23, -82, 5), (30, -112, 7), (31, -140, 5)]), pk)
            + E(0, -44, 48, 42, c)
            + E(0, -26, 22, 16, cr)
            + P("M-6,-36 L6,-36 L0,-29Z", "#F08A8A")
            + S("M-9,-24 Q-4,-19 0,-27 Q4,-19 9,-24", INK, 3)
            + dot_eyes(-19, -52, 19, -52, 6.5)
            + blush(-30, -32, 7, 4.5) + blush(30, -32, 7, 4.5))


# ================================================================ pig (pink, standing)
@real
def pig():
    rng = random.Random(61)
    pink, lite, deep = "#F0B0A2", "#FBD6CB", "#C9867A"
    o = [ground(0, 91, 108, 7, .2)]
    legf = lg([(0, "#D99A8E"), (1, "#C4867A")])
    legn = lg([(0, pink), (1, "#E3A194")])
    o.append(hoof_leg([(40, 30, 11), (42, 62, 8.5), (43, 86, 8)], legf, "#7A5650", dark="#5A2A20"))
    o.append(hoof_leg([(-82, 30, 13), (-82, 62, 9), (-80, 86, 8)], legf, "#7A5650", dark="#5A2A20"))
    o.append(S("M-100,-12 C-112,-18 -120,-6 -112,-1 C-104,3 -106,-12 -114,-12 C-122,-12 -124,0 -118,6", "#E39C8E", 3.4))
    o.append(hoof_leg([(56, 30, 12.5), (58, 62, 9.5), (60, 86, 8.6)], legn, "#7A5650", dark="#5A2A20"))
    o.append(hoof_leg([(-62, 30, 14.5), (-64, 62, 10), (-64, 86, 9)], legn, "#7A5650", dark="#5A2A20"))
    body = blob([(-102, 0), (-98, -26), (-80, -46), (-48, -56), (-8, -58), (30, -54), (56, -48), (76, -44), (92, -38), (104, -28),
                 (110, -18), (110, 0), (102, 12), (88, 22), (74, 32), (58, 44), (30, 52), (-6, 56), (-44, 54), (-74, 46), (-94, 28)])
    inner = [glow(-10, 44, 96, 18, deep, .5),
             glow(-24, -44, 84, 16, "#FFE8E0", .75),
             glow(-70, -6, 30, 34, lite, .55),
             glow(52, -16, 26, 30, lite, .5),
             glow(90, 14, 22, 14, "#D8907F", .45),
             glow(84, -26, 20, 12, "#FFE0D6", .5),
             strokes(rng, 150, (-104, -58, 110, 56), lambda x, y: math.radians(170), ["#FFFFFF", "#C9867A"], (3, 5), .45, .3),
             speckles(rng, 50, (-100, -54, 106, 50), "#B8746A", (.4, .7), .3)]
    o.append(form(body, lg([(0, lite), (.45, pink), (1, "#DE988A")], 0, -58, 0, 56, user=True), "".join(inner), dark="#7A3028", op=.38, w=6))
    snout = blob([(96, -24), (114, -24), (124, -18), (126, -2), (122, 8), (108, 10), (96, 4)])
    o.append(form(snout, lg([(0, "#F6BFB2"), (1, "#E6A193")]), "", dark="#7A3028", op=.3, w=3))
    o.append(form(ell(123, -7, 5.5, 14), lg([(0, "#E8A698"), (1, "#C98477")], 0, 0, 1, 0), "", dark="#6A2820", op=.3, w=2)
             + '<ellipse cx="124.5" cy="-11" rx="1.6" ry="3.4" fill="#7A3A34"/><ellipse cx="124.5" cy="0" rx="1.6" ry="3.4" fill="#7A3A34"/>')
    o.append('<path d="M110,10 C104,15 96,16 88,12" stroke="#9A564C" stroke-width="1.5" fill="none" opacity=".6"/>')
    o.append(eye(86, -26, 3.3, "#3A2418", lidop=.6)
             + '<path d="M81,-30 l-2,-4 M84,-31 l-1,-4 M87,-31 l0,-4" stroke="#7A4A40" stroke-width=".8" opacity=".6"/>')
    ear = blob([(58, -46), (64, -68), (80, -84), (98, -84), (96, -68), (86, -52), (72, -42)])
    o.append(form(ear, lg([(0, "#F7C3B6"), (1, "#E09A8C")], 0, 0, 1, 1), glow(82, -68, 10, 12, "#D07E74", .5), dark="#7A3028", op=.4, w=3))
    return "".join(o)


@cartoon("pig")
def pig_c():
    c, d, sn = "#FFB3BF", "#F293A3", "#FF8FA3"
    return (S("M-92,-6 C-112,-14 -116,8 -102,8 C-90,8 -98,-12 -110,-6", d, 6)
            + "".join(f'<rect x="{x}" y="20" width="22" height="60" rx="10" fill="{d}"/>' for x in (-64, 34))
            + "".join(f'<rect x="{x}" y="20" width="22" height="62" rx="10" fill="{c}"/>' for x in (-82, 16))
            + P(rrect(-98, -40, 140, 82, 41), c)
            + P("M14,-90 L22,-124 L48,-102Z", d) + P("M86,-90 L78,-124 L52,-102Z", d)
            + E(50, -58, 46, 42, c)
            + E(50, -42, 22, 15, sn)
            + E(42, -42, 4.5, 6.5, "#C2566C") + E(58, -42, 4.5, 6.5, "#C2566C")
            + smile(50, -22, 12, 3, 3)
            + dot_eyes(32, -68, 68, -68, 6.5)
            + blush(20, -48, 7, 4.5) + blush(80, -48, 7, 4.5))


# ================================================================ sheep (woolly, dark face)
@real
def sheep():
    rng = random.Random(71)
    wool, face = "#EFE7D6", "#3E3632"
    o = [ground(-4, 91, 104, 7, .2)]
    legc = lg([(0, "#4A403A"), (1, "#2E2824")])
    for pts in ([(40, 30, 6.5), (42, 60, 5), (43, 86, 5)], [(-74, 30, 7), (-76, 60, 5.2), (-76, 86, 5)]):
        o.append(hoof_leg(pts, legc, "#1A1614", dark="#000", op=.3))
    for pts in ([(56, 30, 7), (58, 60, 5.4), (60, 86, 5.2)], [(-58, 30, 7.5), (-60, 60, 5.6), (-60, 86, 5.2)]):
        o.append(hoof_leg(pts, lg([(0, "#5A4E46"), (1, "#3A322C")]), "#1A1614", dark="#000", op=.3))
    body = cloud(-12, -8, 96, 58, 22, 1.0, jit=.05, seed=4)
    shade, hi = [], []
    for _ in range(90):
        x, y = rng.uniform(-104, 80), rng.uniform(-60, 44)
        if ((x + 12) / 90) ** 2 + ((y + 8) / 52) ** 2 > 1:
            continue
        r = rng.uniform(5, 8)
        shade.append(f"M{n_(x - r)},{n_(y)}a{n_(r)},{n_(r * .8)} 0 0 0 {n_(2 * r)},0")
        hi.append(f"M{n_(x - r * .5)},{n_(y - r * .45)}h{n_(r * .6)}")
    inner = [glow(-10, 30, 96, 30, "#B8A98E", .55),
             glow(-30, -44, 70, 20, "#FFFFFF", .8),
             f'<path d="{"".join(shade)}" stroke="#A8987C" stroke-width="2.4" fill="none" opacity=".28" stroke-linecap="round"/>',
             f'<path d="{"".join(shade)}" stroke="#A8987C" stroke-width="1" fill="none" opacity=".3" stroke-linecap="round"/>',
             f'<path d="{"".join(hi)}" stroke="#FFFFFF" stroke-width="3" fill="none" opacity=".7" stroke-linecap="round"/>']
    o.append(form(body, rg([(0, "#FBF7EE"), (.6, wool), (1, "#D8CCB4")], .4, .3, .75), "".join(inner), dark="#5A4A30", op=.4, w=7))
    # head: a long dark face, ears out sideways, a wool cap
    o.append(form(tube([(64, -34, 7), (72, -28, 6)]), "#2E2824", dark="#000", op=.3, w=2))
    headd = blob([(66, -46), (80, -60), (96, -60), (110, -44), (122, -22), (124, -10), (116, -4), (104, -8), (86, -18), (70, -26)])
    o.append(form(headd, lg([(0, "#5A4E48"), (.5, face), (1, "#2A2420")], 0, 0, 1, 1),
                  glow(96, -48, 16, 8, "#7A6C64", .5) + glow(118, -14, 8, 6, "#1A1412", .6)
                  + strokes(random.Random(9), 50, (66, -62, 124, -4), lambda x, y: math.radians(30), ["#6A5E56", "#1E1A18"], (2, 4), .5, .4),
                  dark="#000", op=.3, w=3))
    o.append(form(blob([(84, -50), (70, -60), (52, -60), (48, -52), (62, -46), (78, -44)]), lg([(0, "#4A403A"), (1, "#2A2420")]),
                  glow(62, -54, 8, 3, "#8A6A62", .6), dark="#000", op=.3, w=2))
    o.append(form(cloud(78, -58, 16, 12, 9, 1.0, seed=2), rg([(0, "#FBF7EE"), (1, "#D8CCB4")], .4, .3, .7), "", dark="#5A4A30", op=.3, w=3))
    o.append(eye(100, -42, 3, "#6A4A20", lid="#1A1412", lidop=.4)
             + '<path d="M120,-14 C118,-11 115,-10 112,-11" stroke="#120E0C" stroke-width="1.2" fill="none" opacity=".8"/>'
             + '<path d="M116,-6 C112,-6 108,-8 106,-10" stroke="#120E0C" stroke-width="1" fill="none" opacity=".5"/>')
    return "".join(o)


@cartoon("sheep")
def sheep_c():
    w, f = "#FFFFFF", "#3E3632"
    return ("".join(f'<rect x="{x}" y="20" width="16" height="64" rx="8" fill="#2E2824"/>' for x in (-62, 30))
            + "".join(f'<rect x="{x}" y="20" width="16" height="66" rx="8" fill="{f}"/>' for x in (-80, 12))
            + P(cloud(-30, 0, 84, 50, 14, 1.0, seed=3), "#E9E3D6")
            + P(cloud(-30, -4, 76, 44, 14, 1.0, seed=3), w)
            + E(20, -60, 22, 10, f, -20) + E(84, -60, 22, 10, f, 20)
            + E(52, -46, 34, 40, f)
            + P(cloud(52, -84, 26, 14, 8, 1.0, seed=5), w)
            + smile(52, -26, 12, 3, 3, "#FFFFFF")
            + dot_eyes(38, -52, 66, -52, 6.5, "#FFFFFF", shine=False)
            + C(39, -51, 3.2, INK) + C(67, -51, 3.2, INK)
            + blush(28, -34, 7, 4.5, .8) + blush(76, -34, 7, 4.5, .8))


# ================================================================ horse (bay, standing)
@real
def horse():
    rng = random.Random(81)
    coat, lite, black = "#8E522C", "#B87444", "#221A16"
    o = [ground(0, 91, 112, 7, .2)]

    def legfill(top, mid):
        return lg([(0, top), (.45, mid), (.62, black), (1, black)], 0, 0, 0, 90, user=True)
    o.append(hoof_leg([(44, 8, 11), (46, 36, 7.5), (46, 58, 5), (46, 76, 5.5), (47, 86, 6)], legfill("#6E3E20", "#5E3418"), "#2A2420"))
    o.append(hoof_leg([(-72, 0, 14), (-80, 28, 10), (-90, 50, 6), (-86, 70, 5), (-84, 86, 6)], legfill("#6E3E20", "#5E3418"), "#2A2420"))
    # tail
    tl = [(-98, -34, 6), (-112, -14, 9), (-116, 20, 11), (-112, 52, 10), (-104, 70, 5)]
    o.append(form(tube(tl), lg([(0, "#3A2C24"), (1, "#16110E")], 0, 0, 1, 0),
                  strokes(random.Random(4), 90, (-130, -36, -96, 74), lambda x, y: math.radians(100 + (x + 110) * 1.2), ["#5A4638", "#0A0807"], (8, 14), .8, .5, .05),
                  dark="#000", op=.3, w=4))
    o.append(hoof_leg([(58, 8, 12), (60, 36, 8), (60, 58, 5.2), (60, 76, 5.6), (61, 86, 6.2)], legfill(coat, "#7A4424"), "#2A2420"))
    o.append(hoof_leg([(-58, 0, 16), (-64, 28, 11), (-74, 50, 6.2), (-70, 70, 5.2), (-68, 86, 6.2)], legfill(coat, "#7A4424"), "#2A2420"))
    body = blob([(126, -64), (122, -56), (114, -52), (104, -58), (94, -64), (86, -66), (82, -56), (74, -36), (70, -12), (64, 12),
                 (40, 22), (0, 24), (-40, 20), (-72, 14), (-94, -4), (-100, -24), (-90, -42), (-60, -44), (-20, -38), (14, -42),
                 (34, -54), (52, -78), (70, -100), (86, -112), (100, -102), (114, -86), (124, -74)])

    def flow(x, y):
        if x > 50 and y < -40:
            return math.radians(60)
        return math.radians(175 + (y + 10) * .3)
    inner = [glow(-10, 14, 100, 16, "#4E2A14", .5),
             glow(-20, -30, 80, 16, "#C98450", .6),
             glow(-70, -18, 26, 28, lite, .5),
             glow(54, -6, 18, 26, lite, .4),
             haze("M70,-36 C60,-10 56,8 40,20", "#5A2E14", 4, .3, 4),
             haze("M-52,-38 C-64,-14 -60,6 -46,20", "#5A2E14", 4, .25, 4),
             glow(108, -84, 18, 10, "#C98450", .45),
             glow(120, -60, 9, 7, "#3A2416", .6),
             strokes(rng, 260, (-100, -112, 126, 24), flow, ["#C98450", "#5E3418", "#E0A070"], (4, 7), .7, .25, .05)]
    o.append(form(body, lg([(0, "#7A4424"), (.4, coat), (1, "#A9663A")], 0, -110, 0, 30, user=True), "".join(inner), dark="#2A1408", op=.4, w=6))
    # mane and forelock
    mane = blob([(86, -114), (70, -104), (52, -82), (36, -58), (22, -44), (30, -40), (46, -54), (62, -76), (78, -96), (92, -106)])
    o.append(form(mane, lg([(0, "#3A2C24"), (1, "#16110E")], 0, 0, 1, 1),
                  strokes(random.Random(6), 70, (20, -116, 96, -38), lambda x, y: math.radians(130), ["#5A4638", "#0A0807"], (8, 12), .8, .5, .05),
                  dark="#000", op=.3, w=3))
    o.append(P(blob([(92, -110), (104, -104), (108, -96), (98, -98), (90, -104)]), "#1E1612"))
    o.append(form(blob([(84, -110), (82, -124), (86, -132), (92, -122), (92, -110)]), lg([(0, coat), (1, "#5E3418")], 0, 0, 1, 0), "", dark="#2A1408", op=.4, w=2))
    o.append(eye(101, -86, 3.6, "#2A1A10", rot=20, lidop=.5)
             + '<path d="M118,-64 C121,-66 123,-62 121,-60" stroke="#1A1210" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
             + '<path d="M124,-54 C120,-52 116,-52 114,-53" stroke="#1A1210" stroke-width="1" fill="none" opacity=".6"/>')
    return "".join(o)


@cartoon("horse")
def horse_c():
    c, d, m = "#B8743E", "#9A5E30", "#3A2A20"
    return ("".join(f'<rect x="{x}" y="0" width="18" height="84" rx="9" fill="{d}"/>' for x in (-60, 34))
            + "".join(f'<rect x="{x}" y="0" width="18" height="86" rx="9" fill="{c}"/>' for x in (-78, 16))
            + "".join(f'<rect x="{x}" y="74" width="18" height="12" rx="4" fill="{m}"/>' for x in (-78, 16))
            + S("M-84,-26 C-112,-14 -114,30 -104,50", m, 16)
            + P(rrect(-92, -40, 136, 60, 30), c)
            + P(tube([(20, -20, 20), (44, -66, 17), (60, -96, 15)]), c)
            + P(tube([(44, -112, 4), (40, -126, 1)]), c)
            + P(tube([(60, -100, 22), (92, -70, 15)]), c)
            + E(96, -66, 16, 15, "#E8C9A8")
            + C(102, -68, 2.6, d)
            + P(blob([(38, -120), (56, -116), (40, -86), (24, -58), (10, -36), (6, -54), (22, -86)]), m)
            + P(tube([(48, -112, 7), (46, -128, 2)]), d)
            + dot_eye(66, -94, 6.5)
            + smile(92, -54, 10, 2, 3)
            + blush(74, -78, 7, 4.5))


# ================================================================ chicken (brown hen)
@real
def chicken():
    rng = random.Random(91)
    red, base = "#D8322A", "#A85A2C"
    o = [ground(4, 91, 70, 6, .22)]
    for x0 in (-6, 18):
        c = "#D9A43A" if x0 < 0 else "#EBB846"
        o.append(S(f"M{x0},34 L{x0 - 2},82", c, 6.5)
                 + S(f"M{x0 - 2},82 L{x0 + 16},86 M{x0 - 2},82 L{x0 + 8},90 M{x0 - 2},82 L{x0 - 14},86", c, 3.6))
    tail = [blob([(-50, -40), (-70, -74), (-84, -96), (-96, -92), (-92, -60), (-80, -30)]),
            blob([(-56, -36), (-82, -60), (-104, -72), (-110, -60), (-96, -36), (-76, -16)]),
            blob([(-60, -24), (-90, -40), (-112, -40), (-112, -28), (-92, -12), (-70, -4)])]
    for i, t in enumerate(tail):
        o.append(form(t, lg([(0, "#3A2A20"), (.6, "#24302A"), (1, "#151A16")], 0, 0, 1, 1),
                      glow(-80, -60 + i * 18, 14, 5, "#4E7A5A", .45, rot=-40), dark="#000", op=.3, w=3))
    body = blob([(74, -76), (70, -86), (58, -92), (44, -88), (36, -74), (32, -56), (14, -40), (-24, -36), (-56, -42), (-72, -36),
                 (-84, -12), (-74, 14), (-44, 36), (-4, 46), (34, 34), (58, 10), (66, -18), (66, -42), (70, -56), (76, -66)])

    def flow(x, y):
        if x > 30 and y < -40:
            return math.radians(120)
        return math.radians(170 + (y + 20) * .4)
    inner = [glow(-10, 30, 80, 20, "#5E2E14", .5),
             glow(30, -10, 30, 34, "#D08A50", .55),
             glow(54, -74, 18, 12, "#D08A50", .5),
             strokes(rng, 160, (-84, -92, 76, 46), flow, ["#D08A50", "#6E3416", "#E8A86A"], (4, 7), .9, .3, .25)]
    o.append(form(body, lg([(0, "#B8662E"), (.5, base), (1, "#8A4520")], 0, -90, 0, 46, user=True), "".join(inner), dark="#2A1206", op=.4, w=6))
    wing = blob([(30, -24), (0, -30), (-36, -26), (-62, -14), (-50, 6), (-20, 16), (12, 10), (30, -6)])
    feathers = "".join(f"M{x},{y}q-10,8 -22,8" for x, y in ((14, -16), (0, -14), (-14, -12), (-28, -8), (8, -2), (-6, 2), (-20, 6)))
    o.append(form(wing, lg([(0, "#9A4E24"), (1, "#7A3A18")], 0, 0, 1, 1),
                  f'<path d="{feathers}" stroke="#4E2410" stroke-width="1.6" fill="none" opacity=".5" stroke-linecap="round"/>'
                  + f'<path d="{feathers}" stroke="#E0A06A" stroke-width=".8" fill="none" opacity=".5" transform="translate(1 -1.6)"/>',
                  dark="#2A1206", op=.35, w=3))
    comb = blob([(42, -88), (44, -100), (50, -104), (54, -98), (58, -106), (64, -104), (66, -96), (72, -100), (76, -92), (72, -84), (56, -86)])
    o.append(form(comb, lg([(0, "#F04A3A"), (1, "#B01E1A")]), "", dark="#5A0A06", op=.35, w=3))
    o.append(form(blob([(70, -64), (78, -62), (80, -50), (76, -42), (70, -46), (68, -56)]), lg([(0, "#F04A3A"), (1, "#B01E1A")]), "", dark="#5A0A06", op=.35, w=2))
    o.append(form("M74,-80 C82,-80 90,-76 94,-71 C88,-68 82,-67 76,-67 C73,-71 72,-76 74,-80Z", lg([(0, "#F2D068"), (1, "#C99A30")]), "", dark="#5A4010", op=.3, w=2))
    o.append(glow(55, -64, 7, 6, "#E85040", .7) + eye(62, -78, 3.2, "#C98A20", rot=0, lidop=.5))
    return "".join(o)


@cartoon("chicken")
def chicken_c():
    c, d, r, y = "#C8743A", "#A65A2A", "#F2383A", "#FFC43A"
    return (S("M-8,40 L-10,76 M16,40 L16,76", y, 7)
            + S("M-10,76 L4,80 M-10,76 L-22,80 M16,76 L30,80 M16,76 L4,80", y, 5)
            + P(blob([(-50, -30), (-74, -76), (-90, -60), (-84, -20)]), "#4A3A30")
            + P(blob([(-56, -16), (-100, -46), (-104, -24), (-80, 4)]), "#3A2E26")
            + P(blob([(52, -84), (60, -100), (70, -92), (78, -102), (86, -86), (70, -76)]), r)
            + E(-6, 4, 74, 50, c)
            + C(54, -50, 36, c)
            + P(blob([(26, -10), (-30, -12), (-56, 4), (-28, 24), (16, 18)]), d)
            + P("M86,-60 L106,-52 L86,-42Z", y)
            + P(blob([(84, -40), (92, -38), (90, -24), (82, -30)]), r)
            + dot_eye(66, -58, 6.5) + blush(70, -38, 7, 4.5))


# ================================================================ fish (goldfish)
@real
def fish():
    rng = random.Random(101)
    org, lite, deep = "#F27A22", "#FFB45C", "#C94E14"
    o = []
    finf = lg([(0, "#FFB060", .9), (1, "#E8661C", .85)], 0, 0, 1, 0)
    rays = lambda pts: "".join(f"M{a},{b}L{c},{d}" for a, b, c, d in pts)
    tail = blob([(-54, -10), (-78, -30), (-108, -58), (-124, -54), (-114, -24), (-100, 0), (-114, 24), (-124, 52), (-108, 58), (-78, 32), (-54, 10)])
    o.append(form(tail, lg([(0, "#E8661C", .95), (.6, "#FF9A40", .85), (1, "#FFC27A", .7)], 1, 0, 0, 0),
                  f'<path d="{rays([(-58, -6, -116, -54), (-58, -3, -112, -36), (-58, 0, -104, -14), (-58, 0, -104, 14), (-58, 3, -112, 36), (-58, 6, -116, 54)])}" stroke="#B8460E" stroke-width="1.2" opacity=".45"/>',
                  dark="#7A2A06", op=.3, w=4))
    dorsal = blob([(34, -40), (10, -64), (-12, -76), (-26, -70), (-30, -36)])
    o.append(form(dorsal, finf, f'<path d="{rays([(28, -40, 8, -62), (16, -40, -6, -70), (2, -38, -18, -72), (-12, -36, -26, -66)])}" stroke="#B8460E" stroke-width="1.1" opacity=".45"/>', dark="#7A2A06", op=.3, w=3))
    o.append(form(blob([(20, 36), (6, 58), (-12, 62), (-14, 40)]), finf, "", dark="#7A2A06", op=.3, w=2))
    o.append(form(blob([(-24, 28), (-34, 46), (-50, 46), (-46, 20)]), finf, "", dark="#7A2A06", op=.3, w=2))
    body = blob([(114, -2), (110, -16), (94, -34), (64, -46), (24, -46), (-14, -36), (-42, -20), (-60, -10), (-60, 10), (-42, 18), (-14, 32), (24, 44), (64, 42), (94, 30), (110, 14)])
    sc = []
    for row in range(-4, 5):
        for col in range(9):
            x = 60 - col * 14 + (row % 2) * 7
            y = row * 10
            sc.append(f"M{x},{y - 6}a7,7 0 0 0 0,12")
    inner = [glow(20, -30, 90, 16, deep, .55),
             glow(20, 30, 80, 16, "#FFE2B8", .8),
             glow(30, 0, 70, 14, lite, .4),
             f'<path d="{"".join(sc)}" stroke="#A8400C" stroke-width="1.2" fill="none" opacity=".28"/>',
             f'<path d="{"".join(sc)}" stroke="#FFE0A8" stroke-width="1" fill="none" opacity=".35" transform="translate(-1.4 0)"/>',
             haze("M74,-34 C66,-14 66,12 76,32", "#B8460E", 3, .4, 2),
             f'<path d="M78,-30 C70,-12 70,10 80,28" stroke="#FFD9A0" stroke-width="1" fill="none" opacity=".6"/>',
             glow(96, -10, 18, 14, "#FFC890", .4),
             speckles(rng, 40, (-50, -40, 100, 40), "#FFF0D0", (.6, 1.2), .5)]
    o.append(form(body, lg([(0, deep), (.45, org), (1, "#FFC07A")], 0, -46, 0, 44, user=True), "".join(inner), dark="#6A2004", op=.38, w=6, light=.25))
    o.append(form(blob([(60, 10), (44, 22), (30, 34), (34, 38), (52, 30), (66, 18)]), finf, "", dark="#7A2A06", op=.3, w=2))
    o.append('<circle cx="92" cy="-10" r="9" fill="#E8B060"/>' + eye(92, -10, 7, "#1A1008", lid="#1A1008", lidop=0)
             + '<path d="M114,2 C111,4 108,4 106,3" stroke="#8A2E08" stroke-width="1.4" fill="none" stroke-linecap="round"/>')
    return "".join(o)


@cartoon("fish")
def fish_c():
    c, d, f = "#FF8A2A", "#E86A14", "#FFB55A"
    return (P(blob([(-50, -6), (-96, -54), (-108, -40), (-88, 0), (-108, 40), (-96, 54), (-50, 6)]), f)
            + P(blob([(30, -46), (0, -76), (-30, -62), (-30, -40)]), f)
            + P(blob([(10, 40), (0, 64), (-20, 56), (-16, 36)]), f)
            + E(20, 0, 86, 52, c)
            + P(blob([(50, 6), (28, 26), (36, 32), (58, 18)]), d)
            + dot_eye(70, -12, 9) + smile(94, 8, 12, 3, 3) + blush(72, 14, 8, 5)
            + C(-20, -14, 6, "#FFB55A") + C(-2, 4, 6, "#FFB55A") + C(-30, 12, 6, "#FFB55A"))


# ================================================================ bird (tree sparrow on a twig)
@real
def bird():
    rng = random.Random(111)
    o = []
    twig = tube([(-110, 66, 4.5), (-40, 60, 5.5), (30, 62, 5.5), (110, 54, 4)])
    o.append(form(twig, lg([(0, "#8A6A4A"), (1, "#5A402A")]), "", dark="#2A1A0A", op=.4, w=3))
    o.append(form(blob([(80, 56), (100, 36), (122, 28), (116, 46), (96, 56)]), lg([(0, "#7FAE5A"), (1, "#4E7E34")], 0, 0, 1, 1),
                  '<path d="M84,54 Q100,42 118,32" stroke="#C8E0A0" stroke-width="1" fill="none" opacity=".7"/>', dark="#1A3A0A", op=.3, w=2))
    tail = blob([(-50, 14), (-84, 30), (-112, 46), (-108, 56), (-78, 46), (-44, 34)])
    o.append(form(tail, lg([(0, "#7A5434"), (1, "#4A3220")]), '<path d="M-56,22 L-106,50 M-56,28 L-100,52" stroke="#2A1A10" stroke-width="1" opacity=".5"/>', dark="#1A0E06", op=.35, w=3))
    for x0 in (2, 22):
        o.append(S(f"M{x0},40 L{x0 + 2},58", "#B08070", 3) + S(f"M{x0 - 6},60 Q{x0 + 2},54 {x0 + 10},60", "#9A6A5A", 2.4))
    body = blob([(74, -36), (68, -54), (52, -66), (32, -66), (16, -56), (0, -40), (-24, -24), (-48, -2), (-56, 16), (-40, 34),
                 (-10, 46), (24, 44), (50, 28), (64, 6), (70, -16)])
    inner = [softfill(blob([(70, -10), (66, 10), (50, 30), (24, 44), (-10, 46), (-30, 36), (-10, 20), (20, 6), (46, -6)]), "#D9D2C6", 1, 3),
             softfill(blob([(16, -58), (32, -68), (52, -68), (68, -56), (70, -50), (56, -50), (40, -48), (22, -44)]), "#7A3E22", 1, 2),
             softfill(blob([(70, -50), (66, -34), (54, -26), (38, -30), (30, -40), (44, -46), (60, -48)]), "#F4F0E8", 1, 2),
             softfill(blob([(46, -38), (40, -32), (34, -36), (38, -40)]), "#1E1612", 1, 1),
             softfill(blob([(74, -38), (72, -28), (64, -20), (60, -26), (66, -34)]), "#1E1612", 1, 1.5),
             glow(10, 30, 50, 16, "#9A8E7E", .45),
             strokes(rng, 110, (-56, -70, 74, 46), lambda x, y: math.radians(160), ["#FFFFFF", "#8A7A6A"], (3, 5), .6, .3)]
    o.append(form(body, lg([(0, "#9A6A42"), (1, "#7A5232")], 0, 0, 1, 1), "".join(inner), dark="#1A0E06", op=.38, w=5))
    wing = blob([(30, -30), (6, -36), (-20, -26), (-52, 0), (-62, 18), (-40, 22), (-6, 14), (22, 0), (34, -14)])
    marks = "".join(f"M{x},{y}q-6,6 -14,6" for x, y in ((18, -20), (6, -18), (-6, -14), (-18, -8), (-30, 0), (10, -4), (-2, 0), (-14, 6)))
    o.append(form(wing, lg([(0, "#A8784A"), (1, "#6A4426")], 0, 0, 1, 1),
                  f'<path d="{marks}" stroke="#2A1A10" stroke-width="2.4" fill="none" opacity=".55" stroke-linecap="round"/>'
                  + '<path d="M22,-24 C10,-26 -4,-22 -14,-16" stroke="#F4ECDC" stroke-width="2.6" fill="none" opacity=".85" stroke-linecap="round"/>'
                  + '<path d="M14,-10 C2,-10 -12,-4 -22,4" stroke="#F4ECDC" stroke-width="2" fill="none" opacity=".7" stroke-linecap="round"/>',
                  dark="#1A0E06", op=.35, w=3))
    o.append(form("M72,-50 C78,-50 86,-46 88,-42 C84,-39 78,-38 72,-38 C70,-42 70,-47 72,-50Z", lg([(0, "#4A4038"), (1, "#1A1612")]), "", dark="#000", op=.3, w=1.5))
    o.append(eye(60, -48, 3.2, "#1A120C", lid="#1A120C", lidop=.3))
    return "".join(o)


@cartoon("bird")
def bird_c():
    b, d, w, cr = "#A8784A", "#7A4E2C", "#FFF7EC", "#8A4426"
    return (S("M-100,64 L100,56", "#8A6A4A", 10)
            + P(blob([(-40, 20), (-96, 44), (-90, 56), (-36, 38)]), d)
            + S("M0,40 L0,58 M24,40 L24,58", "#E39A6A", 5)
            + E(0, 6, 64, 46, b)
            + E(10, 22, 44, 26, "#EDE4D6")
            + C(42, -38, 36, b)
            + K.clipped(circ(42, -38, 36), E(42, -76, 40, 22, cr))
            + E(46, -26, 22, 14, w)
            + C(40, -24, 5, INK)
            + P(blob([(18, -6), (-30, -6), (-54, 18), (-20, 20)]), d)
            + P("M76,-46 L96,-38 L76,-30Z", "#3A3230")
            + dot_eye(56, -44, 6.5) + blush(62, -26, 6, 4))


# ================================================================ mouse (grey house mouse)
@real
def mouse():
    rng = random.Random(121)
    base = "#8E8882"
    o = [ground(0, 52, 96, 6, .2)]
    tl = [(-70, 14, 4.2), (-96, 32, 3.4), (-122, 22, 2.8), (-128, -10, 2.2), (-116, -40, 1.6), (-98, -52, 1)]
    o.append(form(tube(tl), lg([(0, "#C9A8A0"), (1, "#9A807A")], 0, 0, 1, 1), "", dark="#3A2420", op=.35, w=2))
    o.append(form(circ(64, -50, 15), rg([(0, "#E8B8B0"), (1, "#B08A84")]), "", dark="#3A2420", op=.4, w=3))
    for x in (-50, 52):
        o.append(S(f"M{x},36 L{x + 2},48", "#C9A098", 4) + S(f"M{x - 4},50 L{x + 10},50", "#D9B0A8", 3))
    body = blob([(106, 10), (100, 0), (86, -14), (68, -28), (48, -38), (16, -48), (-20, -50), (-52, -40), (-72, -18), (-74, 8),
                 (-62, 28), (-36, 40), (4, 44), (42, 40), (68, 30), (88, 22), (100, 18)])

    def flow(x, y):
        return math.radians(185 + (y + 10) * .35) if x < 60 else math.radians(200)
    inner = [softfill(blob([(100, 16), (80, 26), (50, 38), (10, 44), (-30, 40), (-20, 26), (30, 24), (70, 14)]), "#D8D0C8", .95, 3),
             glow(-10, -34, 70, 16, "#5E5852", .5),
             glow(-40, 0, 30, 30, "#B0AAA4", .45),
             glow(86, 0, 16, 10, "#B0AAA4", .5),
             strokes(rng, 260, (-76, -52, 106, 46), flow, ["#B8B2AC", "#5E5852", "#E0DAD4"], (3, 5), .6, .35)]
    o.append(form(body, lg([(0, "#7A746E"), (.5, base), (1, "#A8A29C")], 0, -50, 0, 44, user=True), "".join(inner), dark="#1E1A18", op=.38, w=5))
    o.append(form(circ(46, -46, 22), rg([(0, "#F0C4BC"), (.7, "#D9A39C"), (1, "#9A7A74")], .45, .45, .55),
                  glow(48, -44, 12, 14, "#C98880", .6) + glow(36, -58, 8, 6, "#FFFFFF", .5), dark="#3A2420", op=.4, w=4))
    for (x, y) in ((70, 34), (-40, 38)):
        o.append(form(ell(x, y + 10, 9, 4.5), "#E3B8B0", "", dark="#5A3430", op=.3, w=1.5))
    o.append(eye(80, -10, 5.4, "#120C0A", lid="#120C0A", lidop=.2)
             + glow(107, 10, 4.5, 4, "#D98A88", 1, hard=.6)
             + '<g stroke="#4A4440" stroke-width=".6" fill="none" opacity=".7" stroke-linecap="round">'
             '<path d="M98,8 Q112,0 126,-4"/><path d="M98,10 Q114,8 128,10"/><path d="M98,12 Q112,16 124,24"/><path d="M96,6 Q106,-6 116,-14"/></g>')
    return "".join(o)


@cartoon("mouse")
def mouse_c():
    g, d, pk, w = "#A9A4A0", "#8E8984", "#F7B6B0", "#EEEAE6"
    return (S("M-64,30 C-110,40 -120,-10 -96,-30", "#E3A8A4", 6)
            + E(-40, 50, 14, 8, d) + E(40, 50, 14, 8, g)
            + E(-8, 18, 66, 36, g)
            + E(-4, 30, 40, 20, w)
            + C(14, -58, 24, g) + C(86, -58, 24, g)
            + C(14, -58, 15, pk) + C(86, -58, 15, pk)
            + E(50, -22, 40, 34, g)
            + E(50, -8, 18, 12, w)
            + C(50, -14, 6, "#F08A9A")
            + smile(50, -3, 10, 2.5, 3)
            + dot_eyes(36, -30, 64, -30, 6)
            + blush(26, -12, 6, 4) + blush(74, -12, 6, 4)
            + S("M36,-12 L14,-16 M36,-8 L16,-4 M64,-12 L86,-16 M64,-8 L84,-4", "#FFFFFF", 2))


# ================================================================ cartoon cat, cow, duck
@cartoon("cat")
def cat_c():
    g, d, w, st = "#A39C93", "#8A837A", "#F2EDE5", "#6F685F"
    return (S("M-30,74 C-96,78 -100,10 -70,-6", g, 17)
            + E(-2, 36, 56, 54, g)
            + E(0, 50, 32, 36, w)
            + S("M-46,4 Q-36,0 -28,10 M-52,24 Q-42,20 -34,30", st, 6)
            + E(-34, 86, 20, 10, d) + E(30, 86, 20, 10, g)
            + P("M-40,-76 L-46,-128 L-6,-98Z", g) + P("M40,-76 L46,-128 L6,-98Z", g)
            + P("M-36,-86 L-39,-116 L-16,-98Z", "#F2B8B0") + P("M36,-86 L39,-116 L16,-98Z", "#F2B8B0")
            + E(0, -58, 52, 44, g)
            + S("M-10,-100 L-8,-86 M0,-102 L0,-88 M10,-100 L8,-86", st, 5)
            + E(0, -42, 18, 13, w)
            + P("M-5,-48 L5,-48 L0,-42Z", "#F08A8A")
            + S("M-8,-38 Q-4,-34 0,-39 Q4,-34 8,-38", INK, 3)
            + dot_eyes(-20, -62, 20, -62, 6.5)
            + blush(-32, -44, 7, 4.5) + blush(32, -44, 7, 4.5)
            + S("M-30,-44 L-58,-48 M-30,-39 L-56,-36 M30,-44 L58,-48 M30,-39 L56,-36", "#FFFFFF", 2.4))


@cartoon("cow")
def cow_c():
    w, b, pk, g = "#F5F2EC", "#2B2B2E", "#F7A8B4", "#E2DDD4"
    body = rrect(-100, -44, 150, 80, 38)
    return (S("M-96,-26 C-112,-6 -114,24 -108,44", g, 6) + E(-108, 50, 7, 10, b)
            + "".join(f'<rect x="{x}" y="10" width="22" height="74" rx="11" fill="{g}"/>' for x in (-70, 14))
            + "".join(f'<rect x="{x}" y="10" width="22" height="76" rx="11" fill="{w}"/>' for x in (-88, -4))
            + "".join(f'<rect x="{x}" y="74" width="22" height="12" rx="5" fill="{b}"/>' for x in (-88, -4, -70, 14))
            + P(body, w)
            + K.clipped(body, E(-62, -36, 28, 22, b) + E(-6, 30, 26, 18, b) + E(-24, -40, 14, 10, b) + E(-100, 10, 14, 26, b))
            + E(-34, 40, 13, 8, pk)
            + E(26, -100, 9, 5, "#E8DCC0", 30) + E(94, -100, 9, 5, "#E8DCC0", -30)
            + E(14, -80, 20, 10, b, 20) + E(106, -80, 20, 10, b, -20)
            + E(60, -66, 44, 42, w)
            + K.clipped(ell(60, -66, 44, 42), E(36, -94, 26, 22, b))
            + E(60, -36, 36, 22, pk)
            + E(47, -38, 4.5, 6.5, "#D9788A") + E(73, -38, 4.5, 6.5, "#D9788A")
            + smile(60, -24, 12, 2.5, 3)
            + dot_eyes(44, -72, 76, -72, 6.5)
            + blush(32, -52, 7, 4.5) + blush(88, -52, 7, 4.5))


@cartoon("duck")
def duck_c():
    o_ = "#FF9F1C"
    return (S("M-4,36 L-6,66 M18,36 L18,66", o_, 7)
            + P("M-22,70 Q-8,60 8,72 Z M2,70 Q18,60 34,72 Z", o_, f' stroke="{o_}" stroke-width="6" stroke-linejoin="round"')
            + P(blob([(-88, -30), (-62, -8), (-20, -12), (30, -12), (60, 2), (56, 30), (18, 50), (-36, 48), (-74, 22)]), "#D9D2C4")
            + P(blob([(-74, -8), (-24, -6), (22, 4), (4, 26), (-40, 26)]), "#A89E8E")
            + P(blob([(-50, 6), (-26, 8), (-26, 18), (-50, 16)]), "#3D5BC4")
            + P(blob([(24, -14), (48, -14), (62, 4), (56, 28), (32, 26), (20, 6)]), "#8A4A30")
            + P(blob([(20, -18), (30, -40), (44, -46), (52, -30), (50, -14)]), "#1F8A55")
            + C(46, -62, 32, "#1F8A55")
            + S("M24,-18 Q38,-12 52,-18", "#FFFFFF", 5)
            + P("M70,-70 Q100,-66 108,-56 Q104,-48 72,-50 Z", "#F5C518")
            + dot_eye(54, -70, 6.5) + blush(58, -52, 7, 4.5)
            + S("M76,-56 Q86,-52 96,-55", "#C99A10", 2.5))


# ================================================================ main
if __name__ == "__main__":
    K.main("animals", REAL, CARTOON, sys.argv[1:])

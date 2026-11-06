"""Body deck (身體): 20 cards, realistic and cartoon.

    python3 deck_body.py            # writes app/assets/art/cards/body/<id>.svg and <id>_cartoon.svg

A friendly generic young child (warm natural skin, dark brown hair, plain T-shirt and shorts)
shows each part, and the part has a soft pale-yellow glow ring around it. Close-ups (eye, teeth)
fade out softly at their edges; hand, finger and foot have a glow behind them.
All drawings use the child's own units: the face is about 150 wide with its middle at (0, 0);
the whole child stands about 720 tall (head about a quarter of that, like a 2-3 year old).
"""
import math
import random

from kit_bc import (P, along, at, begin, clipped, curve, ellipse_d, flat_disc, flat_ring, glow_path, glow_ring, ground,
                    halo, line, lit, lt, dk, mirror_pts, mix, n, rg, lg, rim, rot_pt, sline, spot, stitch, tube, write)

DECK = "body"

# ---------------------------------------------------------------- colours (realistic)
SKIN, SKIN_L, SKIN_D, SKIN_DD = "#EEC09E", "#F9DCC6", "#D9A07F", "#B97B5C"
CREASE = "#B07258"
LIP, LIP_D, LIP_L = "#DE8A80", "#B45E58", "#F2AFA4"
BLUSH = "#F3907F"
HAIR, HAIR_L, HAIR_D, HAIR_SHINE = "#2E2019", "#5E4333", "#140D0A", "#9B7C68"
IRIS, IRIS_D = "#6A4430", "#2C1A10"
TEE = {"blue": "#7FB2DE", "coral": "#F09A86", "mint": "#8CCBB4", "lilac": "#B8A6DC", "sun": "#F4C95A"}
SHORTS = "#3F5679"


def skin_fill(cx, cy, r, tone=0.0):
    """Skin with soft light from the upper left."""
    return rg([(0, mix(SKIN_L, SKIN, tone)), (.55, mix(SKIN, SKIN_D, tone * .5)), (1, mix(SKIN_D, SKIN_DD, .25 + tone * .3))],
              n(cx - r * .25), n(cy - r * .3), n(r), user=True)


def cloth_fill(c, x0, y0, x1, y1):
    return lg([(0, lt(c, .18)), (.6, c), (1, dk(c, .14))], x0, y0, x1, y1, user=True)


# ================================================================ realistic head (front)
FACE = [(0, -82), (38, -77), (61, -60), (72, -32), (74, -2), (72, 24), (64, 46), (48, 64), (26, 76), (0, 80),
        (-26, 76), (-48, 64), (-64, 46), (-72, 24), (-74, -2), (-72, -32), (-61, -60), (-38, -77)]
FACE_D = curve(FACE)
FRINGE = [(66, -2), (65, -24), (58, -33), (50, -30), (43, -39), (33, -33), (22, -42), (10, -35), (-2, -44), (-14, -35),
          (-25, -43), (-36, -34), (-46, -40), (-56, -31), (-65, -25), (-67, -2)]
BOY_OUT = [(-69, 8), (-76, -20), (-77, -48), (-67, -75), (-45, -94), (-14, -103), (17, -102), (45, -93), (67, -75), (78, -48),
           (77, -20), (70, 8)]
GIRL_OUT = [(-82, 66), (-90, 32), (-89, -8), (-84, -48), (-68, -80), (-40, -99), (0, -106), (40, -99), (68, -80), (84, -48),
            (89, -8), (90, 32), (82, 66), (72, 74)]
GIRL_IN_R = [(66, 56), (71, 24), (70, -4)]
GIRL_BACK = [(-90, -20), (-94, 30), (-90, 80), (-66, 98), (0, 102), (66, 98), (90, 80), (94, 30), (90, -20), (0, -60)]


def ear(side, scale=1.0):
    s = side
    pts = [(66, -16), (77, -22), (86, -14), (89, 2), (86, 18), (78, 30), (66, 31), (60, 8)]
    pts = [(s * x, y) for x, y in pts]
    d = curve(pts)
    o = [P(d, skin_fill(s * 70, -4, 40, .25))]
    o.append(clipped(d, spot(s * 79, 2, 8, 15, SKIN_DD, .45) + spot(s * 84, -10, 5, 8, SKIN_L, .5)
                     + line(f"M{s * 74},-14 C{s * 84},-14 {s * 86},6 {s * 79},20", SKIN_DD, 2.2, .45)))
    o.append(rim(d, SKIN_DD, 4, .35, -s * 1.5, 2.5))
    return "".join(o)


def eye(cx, cy, s=1.0, side=1, look=(0, 0), happy=0.0):
    """One eye, about 32 wide at s=1 (side=+1 for the eye on the viewer's right)."""
    def T(x, y):
        return cx + side * x * s, cy + y * s
    lid_up = [T(-15, 3), T(-9, -9 + happy * 3), T(4, -12 + happy * 3), T(15, -2)]
    lid_lo = [T(15, -2), T(8, 7 - happy * 4), T(-6, 9 - happy * 4), T(-15, 3)]
    shape = curve(lid_up + lid_lo[1:3], closed=True)
    ix, iy = cx + look[0] * s, cy + (-1.5 + look[1]) * s
    ir = 9.6 * s
    inner = [P(shape, lg([(0, "#E9DDD7"), (.35, "#FBF6F2"), (1, "#F4ECE6")], 0, 0, 0, 1)),
             f'<circle cx="{n(ix)}" cy="{n(iy)}" r="{n(ir)}" fill="{rg([(0, "#8A5A3C"), (.55, IRIS), (.85, IRIS_D), (1, "#1C110B")], .5, .55, .5)}"/>',
             f'<circle cx="{n(ix)}" cy="{n(iy)}" r="{n(ir * .45)}" fill="#120B08"/>',
             spot(ix + 2 * s, iy + 4 * s, ir * .5, ir * .35, "#C08A5E", .35),
             sline(curve(lid_up, closed=False), "#5A3A2C", 5 * s, .45)]
    o = [clipped(shape, "".join(inner))]
    # catchlights
    o.append(f'<circle cx="{n(ix - 3.4 * s * side)}" cy="{n(iy - 4 * s)}" r="{n(2.7 * s)}" fill="#FFFFFF" fill-opacity=".95"/>')
    o.append(f'<circle cx="{n(ix + 3.5 * s * side)}" cy="{n(iy + 3.6 * s)}" r="{n(1.1 * s)}" fill="#FFFFFF" fill-opacity=".8"/>')
    # lash line, lashes, crease, lower lid
    up = curve([T(-16, 3.5), T(-9, -9.5 + happy * 3), T(4, -12.6 + happy * 3), T(15.5, -2.4), T(18, -4)], closed=False)
    o.append(line(up, "#2A1A12", 2.4 * s))
    for k, (x, y, dx, dy) in enumerate([(4, -12.4, 1.5, -5), (8.5, -10.8, 3, -4.5), (12.3, -7.4, 4.2, -3.2), (15.4, -3, 5, -1.4)]):
        x2, y2 = T(x + dx, y + dy)
        x1, y1 = T(x, y + happy * 3)
        o.append(line(f"M{n(x1)},{n(y1)} Q{n(x1 + side * dx * s * .2)},{n(y2 + 1.2 * s)} {n(x2)},{n(y2 + happy * 3 * s)}", "#2A1A12", (1.3 - k * .12) * s))
    o.append(line(curve([T(-13, -10 + happy * 2), T(0, -17 + happy * 2), T(13, -12 + happy * 2)], closed=False), CREASE, 1.1 * s, .35))
    o.append(line(curve(lid_lo[:3] + [T(-14, 3.5)], closed=False), CREASE, .9 * s, .4))
    return "".join(o)


def brow(side, y=-21, raise_=0.0):
    pts = [(side * 46, y + 3 - raise_, 1.1), (side * 33, y - 2.5 - raise_ * 1.3, 2.3), (side * 18, y - raise_, 1.9), (side * 13, y + 1.5 - raise_, 1.2)]
    return P(tube(pts), "#5E412F", 'fill-opacity=".72"')


def nose(y=30, s=1.0):
    o = [sline(f"M-8,{y - 30} C-9,{y - 18} -10,{y - 10} -10,{y - 4}", SKIN_D, 7 * s, .18),
         sline(f"M9,{y - 30} C10,{y - 18} 11,{y - 10} 11,{y - 4}", SKIN_D, 8 * s, .26),
         spot(0, y - 6, 9 * s, 7 * s, SKIN_L, .55),
         spot(0, y + 3, 15 * s, 5 * s, SKIN_DD, .22),
         line(f"M-13,{y - 4} C-15,{y + 2} -11,{y + 5} -6,{y + 4}", CREASE, 1.3, .5),
         line(f"M13,{y - 4} C15,{y + 2} 11,{y + 5} 6,{y + 4}", CREASE, 1.3, .55)]
    for sd in (-1, 1):
        o.append(f'<ellipse cx="{n(sd * 4.8)}" cy="{n(y + 3.2)}" rx="2.9" ry="1.6" transform="rotate({sd * 18} {n(sd * 4.8)} {n(y + 3.2)})" fill="#8E4F40" fill-opacity=".72"/>')
    return "".join(o)


def mouth_smile(y=50):
    o = [P(f"M-17,{y - 2} C-8,{y + 2} 8,{y + 2} 17,{y - 2} C12,{y + 9} -12,{y + 9} -17,{y - 2}Z", LIP),
         P(f"M-12,{y + 2} C-6,{y + 9} 6,{y + 9} 12,{y + 2} C6,{y + 4} -6,{y + 4} -12,{y + 2}Z", LIP_L, 'fill-opacity=".6"'),
         P(f"M-16,{y - 3} C-10,{y - 6} -4,{y - 7} 0,{y - 5} C4,{y - 7} 10,{y - 6} 16,{y - 3} C8,{y - 1} -8,{y - 1} -16,{y - 3}Z", mix(LIP, SKIN_D, .3), 'fill-opacity=".85"'),
         line(f"M-19,{y - 4.5} C-9,{y + 2} 9,{y + 2} 19,{y - 4.5}", "#93473F", 1.8),
         line(f"M-21,{y - 7} C-19,{y - 4} -19,{y - 2} -20,{y}", CREASE, 1.1, .4),
         line(f"M21,{y - 7} C19,{y - 4} 19,{y - 2} 20,{y}", CREASE, 1.1, .4),
         spot(0, y + 15, 14, 5, SKIN_DD, .18)]
    return "".join(o)


def mouth_open_teeth(y=48, w=1.0):
    """Big happy smile with the top baby teeth showing."""
    W = 25 * w
    hole = f"M{-W},{y - 4} C{-W * .5},{y} {W * .5},{y} {W},{y - 4} C{W * .8},{y + 16} {W * .35},{y + 23} 0,{y + 23} C{-W * .35},{y + 23} {-W * .8},{y + 16} {-W},{y - 4}Z"
    inner = [P(hole, rg([(0, "#9A3C3C"), (1, "#5E1E22")], .5, .7, .7)),
             spot(0, y + 22, W * .7, 8, "#E77B80", .95, hard=.5)]
    teeth = []
    xs = [(-17, 5.2, 6.4), (-9.4, 6, 7.6), (-2.9, 6.4, 8.8), (2.9, 6.4, 8.8), (9.4, 6, 7.6), (17, 5.2, 6.4)]
    for x, tw, th in xs:
        x *= w
        top = y - 3 - abs(x) * .02
        teeth.append(P(f"M{n(x - tw / 2)},{n(top - 2)} L{n(x + tw / 2)},{n(top - 2)} L{n(x + tw / 2)},{n(top + th - 2)} "
                       f"Q{n(x)},{n(top + th + .6)} {n(x - tw / 2)},{n(top + th - 2)}Z", lg([(0, "#FFFFFF"), (.7, "#FBF6EC"), (1, "#E9DFD0")])))
    inner.append("".join(teeth))
    inner.append(sline(f"M{-W},{y - 3} C{-W * .5},{y + 1} {W * .5},{y + 1} {W},{y - 3}", "#C99A90", 3, .3))
    inner.append(spot(-W * .8, y + 4, 6, 10, "#3A1012", .4))
    inner.append(spot(W * .8, y + 4, 6, 10, "#3A1012", .4))
    o = [clipped(hole, "".join(inner))]
    # lips
    o.append(P(f"M{-W - 2},{y - 5} C{-W * .5},{y - 9} -4,{y - 10} 0,{y - 8} C4,{y - 10} {W * .5},{y - 9} {W + 2},{y - 5} "
               f"C{W * .5},{y - 2} {-W * .5},{y - 2} {-W - 2},{y - 5}Z", mix(LIP, SKIN_D, .25)))
    o.append(P(f"M{-W - 1},{y - 3} C{-W * .8},{y + 17} {-W * .35},{y + 24} 0,{y + 24} C{W * .35},{y + 24} {W * .8},{y + 17} {W + 1},{y - 3} "
               f"C{W * .85},{y + 20} {W * .4},{y + 29} 0,{y + 29} C{-W * .4},{y + 29} {-W * .85},{y + 20} {-W - 1},{y - 3}Z", LIP))
    o.append(spot(0, y + 26.5, 8, 1.6, "#FFFFFF", .4))
    o.append(line(f"M{-W - 5},{y - 9} C{-W - 3},{y - 5} {-W - 3},{y - 2} {-W - 4},{y + 1}", CREASE, 1.2, .45))
    o.append(line(f"M{W + 5},{y - 9} C{W + 3},{y - 5} {W + 3},{y - 2} {W + 4},{y + 1}", CREASE, 1.2, .45))
    return "".join(o)


def mouth_tongue(y=48):
    hole = f"M-15,{y} C-8,{y - 5} 8,{y - 5} 15,{y} C12,{y + 9} -12,{y + 9} -15,{y}Z"
    o = [P(hole, "#6A2428")]
    o.append(P(f"M-15,{y - 1} C-8,{y - 6} -3,{y - 7} 0,{y - 5} C3,{y - 7} 8,{y - 6} 15,{y - 1} C8,{y - 3} -8,{y - 3} -15,{y - 1}Z", mix(LIP, SKIN_D, .25)))
    o.append(P(f"M-16,{y + 1} C-12,{y + 9} 12,{y + 9} 16,{y + 1} C14,{y + 12} -14,{y + 12} -16,{y + 1}Z", LIP))
    tongue = f"M-11.5,{y + 1} C-13,{y + 14} -11,{y + 27} 0,{y + 28} C11,{y + 27} 13,{y + 14} 11.5,{y + 1}Z"
    o.append(P(tongue, lg([(0, "#D9636E"), (.35, "#F08890"), (1, "#E7747D")])))
    o.append(clipped(tongue, spot(-4, y + 15, 4, 8, "#FFFFFF", .35) + spot(0, y + 4, 12, 4, "#8E2E38", .5)
                     + line(f"M0,{y + 4} C-.5,{y + 12} 0,{y + 18} .5,{y + 22}", "#C24E5A", 1.4, .6)))
    o.append(line(f"M-17,{y - 3} C-19,{y - 1} -19,{y + 2} -17,{y + 4}", CREASE, 1.1, .4))
    o.append(line(f"M17,{y - 3} C19,{y - 1} 19,{y + 2} 17,{y + 4}", CREASE, 1.1, .4))
    return "".join(o)


def hair_strands(rng, outer, inner_pts, crown=(10, -96), count=70, cols=(HAIR_L, HAIR_D)):
    pts = inner_pts
    o = []
    for i in range(count):
        tx_, ty_ = pts[min(len(pts) - 1, int(rng.random() * len(pts)))]
        tx_ += rng.uniform(-4, 4)
        sx, sy = crown[0] + rng.uniform(-14, 14), crown[1] + rng.uniform(-4, 10)
        mx, my = (sx + tx_) / 2 + (tx_ - sx) * .25 + rng.uniform(-6, 6), (sy + ty_) / 2 - 18 + rng.uniform(-6, 6)
        o.append(f"M{n(sx)},{n(sy)} Q{n(mx)},{n(my)} {n(tx_)},{n(ty_)}")
    half = len(o) // 2
    return (f'<path d="{"".join(o[:half])}" fill="none" stroke="{cols[0]}" stroke-width="1.3" stroke-opacity=".45"/>'
            f'<path d="{"".join(o[half:])}" fill="none" stroke="{cols[1]}" stroke-width="1.6" stroke-opacity=".5"/>')


def hair_front(kind="boy", seed=5):
    rng = random.Random(seed)
    if kind == "boy":
        shape = curve(BOY_OUT + FRINGE)
        edge = FRINGE + BOY_OUT[:3] + BOY_OUT[-3:]
    else:
        inner_l = [(-x, y) for x, y in reversed(GIRL_IN_R)]
        shape = curve(GIRL_OUT + GIRL_IN_R + FRINGE[1:-1] + inner_l + [(-72, 74)])
        edge = FRINGE + GIRL_OUT[:3] + GIRL_OUT[-4:] + GIRL_IN_R
    fill = rg([(0, HAIR_L), (.45, HAIR), (1, HAIR_D)], -20, -80, 150, user=True)
    inner = [P(shape, fill), hair_strands(rng, shape, [(x, y + 2) for x, y in edge]),
             sline("M-52,-74 C-30,-92 26,-94 52,-76", HAIR_SHINE, 16, .42),
             sline("M-44,-72 C-24,-86 20,-88 44,-74", "#C9AE9A", 5, .35)]
    if kind == "girl":
        inner.append(sline("M-80,-30 C-84,0 -84,30 -78,60", HAIR_SHINE, 10, .3))
        inner.append(sline("M80,-30 C84,0 84,30 78,60", HAIR_D, 12, .45))
    inner.append(rim(shape, HAIR_D, 6, .5))
    return clipped(shape, "".join(inner[:-1])) + inner[-1]


def hair_back_girl():
    d = curve(GIRL_BACK)
    return P(d, rg([(0, HAIR), (1, HAIR_D)], 0, 20, 110, user=True)) + rim(d, HAIR_D, 8, .5)


def head_front(hair="boy", mouth="smile", happy=0.0, raise_=0.0, look=(0, 0)):
    o = []
    if hair == "girl":
        o.append(hair_back_girl())
    o.append(ear(-1) + ear(1))
    face = [P(FACE_D, skin_fill(0, -10, 115)),
            spot(-44, 30, 17, 12, BLUSH, .38), spot(44, 30, 17, 12, BLUSH, .38),
            spot(-24, -50, 26, 18, SKIN_L, .5),
            sline(curve([(x, y + 5) for x, y in FRINGE], closed=False), SKIN_DD, 12, .32),
            spot(0, 66, 26, 10, SKIN_L, .35)]
    o.append(clipped(FACE_D, "".join(face)))
    o.append(rim(FACE_D, SKIN_DD, 7, .38, 2.5, 3))
    o.append(brow(-1, raise_=raise_) + brow(1, raise_=raise_))
    o.append(eye(-29, 5, 1.0, -1, look, happy) + eye(29, 5, 1.0, 1, look, happy))
    o.append(nose(31))
    o.append({"smile": mouth_smile, "teeth": mouth_open_teeth, "tongue": mouth_tongue}[mouth]())
    o.append(hair_front(hair))
    if hair == "girl":
        o.append(hair_clip(50, -66))
    return "".join(o)


def hair_clip(x, y):
    d = f"M{x - 12},{y - 6} C{x - 4},{y - 12} {x + 6},{y - 4} {x + 13},{y - 10} L{x + 15},{y - 3} C{x + 7},{y + 3} {x - 3},{y - 4} {x - 10},{y + 2}Z"
    return P(d, lg([(0, "#F7A8BC"), (1, "#D9708C")])) + spot(x - 2, y - 6, 6, 2, "#FFFFFF", .6)


# ================================================================ realistic body (front and back)
NECK = "M-21,48 C-21,70 -22,88 -25,106 L25,106 C22,88 21,70 21,48Z"
SHIRT = [(-30, 94), (-56, 99), (-74, 110), (-80, 130), (-75, 154), (-79, 200), (-84, 250), (-81, 300), (-40, 305), (0, 307),
         (40, 305), (81, 300), (84, 250), (79, 200), (75, 154), (80, 130), (74, 110), (56, 99), (30, 94), (16, 106), (0, 110), (-16, 106)]
SHORTS_PTS = [(-79, 286), (79, 286), (83, 330), (88, 386), (48, 394), (7, 391), (0, 356), (-7, 391), (-48, 394), (-88, 386), (-83, 330)]
LEG = [(-39, 330, 31), (-38, 400, 27.5), (-36, 468, 21.5), (-36, 512, 23), (-34, 556, 15.5), (-33, 580, 13)]
ARMS = {
    "down": [(-68, 124, 18), (-82, 180, 16.5), (-90, 236, 14.5), (-93, 288, 13.5), (-94, 326, 11.8)],
    "hip": [(-68, 124, 18), (-94, 168, 16.5), (-116, 212, 14.5), (-102, 250, 14), (-80, 282, 12)],
    "belly": [(-68, 124, 18), (-88, 172, 16.5), (-96, 214, 14.5), (-76, 238, 14), (-50, 250, 12)],
}
HANDS = {"down": 92, "hip": 60, "belly": 4}


def limb(pts, base_tone=.25, light_side=1):
    d = tube(pts)
    x0 = min(p[0] for p in pts)
    o = P(d, lg([(0, SKIN_L), (.5, SKIN), (1, SKIN_D)], x0 - 20, 0, x0 + 60, 0, user=True) if light_side > 0 else
          lg([(0, SKIN_D), (.5, SKIN), (1, SKIN_L)], x0 - 20, 0, x0 + 60, 0, user=True))
    o += rim(d, SKIN_DD, 6, .3, 2, 2)
    return o, d


def hand_small(x, y, ang, side=1, curl=0.0):
    """A child's hand (back of the hand) at wrist (x, y), fingers pointing at angle ang (degrees)."""
    def T(px, py):
        return rot_pt(x + px, y + py * side, ang, x, y)
    palm = [T(-2, -11), T(14, -14), T(30, -13.5), T(41 - curl * 10, -10), T(47 - curl * 14, -2), T(45 - curl * 14, 7), T(34, 12), T(18, 13), T(2, 11)]
    d = curve(palm)
    thumb = [(*T(6, -10), 6.8), (*T(16, -19), 6), (*T(25, -22), 5.2)]
    td = tube(thumb)
    fill = skin_fill(x, y, 60, .1)
    o = [P(td, fill), rim(td, SKIN_DD, 3, .35, 1.5, 2), P(d, fill)]
    det = [line(curve([T(31 - curl * 6, k * 6.2 - 3), T(45 - curl * 14, k * 6.6 - 3.3)], closed=False), CREASE, .9, .5) for k in (-1, 0, 1)]
    det += [spot(*T(26, k * 6 - 3), 3, 2.4, SKIN_L, .6) for k in (-1, 0, 1, 2)]
    o.append(clipped(d, "".join(det) + spot(*T(44, 0), 6, 12, SKIN_DD, .25)))
    o.append(rim(d, SKIN_DD, 4, .35, 1.5, 2))
    return "".join(o)


def arm(pose, side, sleeve_c):
    pts = ARMS[pose]
    if side > 0:
        pts = mirror_pts(pts)
    a, d = limb(pts, light_side=-side)
    o = [a]
    # elbow dimple / crease
    ex, ey, ea, ew = at(pts, .5)
    o.append(clipped(d, spot(ex, ey, ew * .7, ew * .45, SKIN_DD, .22, ea)))
    wx, wy = pts[-1][0], pts[-1][1]
    _, _, wa, _ = at(pts, .97)
    o.append(hand_small(wx - math.cos(math.radians(wa)) * 3, wy - math.sin(math.radians(wa)) * 3, wa, side=-side if pose != "belly" else side,
                        curl=.25 if pose == "down" else 0))
    # short sleeve over the top of the arm
    sx, sy = pts[0][0], pts[0][1]
    ux, uy = pts[1][0] - sx, pts[1][1] - sy
    L = math.hypot(ux, uy)
    ux, uy = ux / L, uy / L
    end = (sx + ux * 46, sy + uy * 46)
    sl = [(sx - ux * 6, sy - uy * 6, 24), (sx + ux * 20, sy + uy * 20, 25), (end[0], end[1], 24)]
    sd = tube(sl, caps=(True, False))
    o.append(P(sd, cloth_fill(sleeve_c, sx - 30, 0, sx + 30, 0)))
    o.append(rim(sd, dk(sleeve_c, .35), 6, .3, 2 * -side, 3))
    nx, ny = -uy, ux
    o.append(stitch(f"M{n(end[0] - nx * 23 - ux * 4)},{n(end[1] - ny * 23 - uy * 4)} L{n(end[0] + nx * 23 - ux * 4)},{n(end[1] + ny * 23 - uy * 4)}", dk(sleeve_c, .4), 1, .5))
    o.append(sline(f"M{n(end[0] - nx * 22)},{n(end[1] - ny * 22)} L{n(end[0] + nx * 22)},{n(end[1] + ny * 22)}", dk(sleeve_c, .45), 3, .35, 2))
    return "".join(o)


def shirt_front(c, rng):
    d = curve(SHIRT)
    inner = [P(d, cloth_fill(c, -80, 100, 80, 300)),
             sline("M-50,160 C-42,200 -46,250 -52,296", dk(c, .25), 12, .25),
             sline("M48,170 C40,210 44,250 50,296", dk(c, .25), 10, .22),
             sline("M-26,140 C-18,180 -16,230 -20,290", lt(c, .4), 14, .3),
             spot(0, 250, 70, 40, lt(c, .35), .35),
             stitch("M-80,292 C-40,298 40,298 80,292", dk(c, .4), 1, .5)]
    o = [clipped(d, "".join(inner)), rim(d, dk(c, .45), 8, .32)]
    o.append(line("M-30,95 C-20,112 20,112 30,95", dk(c, .2), 8))
    o.append(line("M-30,95 C-20,112 20,112 30,95", lt(c, .25), 4, .8))
    return "".join(o)


def shorts(c, back=False):
    d = curve(SHORTS_PTS)
    inner = [P(d, cloth_fill(c, -80, 290, 80, 390)),
             sline("M0,300 L0,356", dk(c, .4), 6, .3),
             sline("M-60,330 C-56,350 -50,370 -48,392", lt(c, .3), 10, .25),
             stitch("M-87,380 C-60,388 -30,389 -8,386", lt(c, .3), 1, .6),
             stitch("M87,380 C60,388 30,389 8,386", lt(c, .3), 1, .6)]
    return clipped(d, "".join(inner)) + rim(d, dk(c, .5), 8, .35)


def leg(side, back=False):
    pts = LEG if side < 0 else mirror_pts(LEG)
    d = tube(pts, caps=(False, True))
    x0 = side * 36
    o = [P(d, lg([(0, SKIN_L if side < 0 else SKIN_D), (.5, SKIN), (1, SKIN_D if side < 0 else SKIN_L)], x0 - 32, 0, x0 + 32, 0, user=True))]
    det = [spot(x0 + side * 2, 466, 16, 12, SKIN_L if not back else SKIN_DD, .5 if not back else .25),
           spot(x0 - side * 4, 520, 10, 30, SKIN_L, .3)]
    if back:
        det.append(line(f"M{x0 - 14},{466} C{x0 - 5},{470} {x0 + 5},{470} {x0 + 14},{466}", CREASE, 1.2, .5))
    else:
        det.append(line(f"M{x0 - 12},{480} C{x0 - 4},{484} {x0 + 4},{484} {x0 + 12},{480}", CREASE, 1, .35))
        det.append(line(f"M{x0 - 10},{452} C{x0 - 4},{449} {x0 + 4},{449} {x0 + 10},{452}", CREASE, .9, .25))
    o.append(clipped(d, "".join(det)))
    o.append(rim(d, SKIN_DD, 6, .35, side * -2, 2))
    return "".join(o)


def foot_front(side):
    s = side
    pts = [(-47, 568), (-26, 568), (-19, 590), (-12, 606), (-17, 616), (-36, 619), (-55, 615), (-60, 605), (-55, 588)]
    pts = [(-x * -s if s < 0 else -x, y) for x, y in pts] if s > 0 else pts
    d = curve(pts)
    o = [P(d, skin_fill(s * 38, 580, 50, .15))]
    toes = [(-18, 610, 6.2, 5), (-28, 613, 4.6, 4.2), (-37, 614, 4.2, 3.8), (-45, 613, 3.8, 3.4), (-52, 610, 3.4, 3)]
    det = []
    for x, y, rx, ry in toes:
        x = x if s < 0 else -x
        det.append(spot(x, y - 1, rx, ry, SKIN_L, .6))
        det.append(line(f"M{n(x - rx)},{n(y + 1)} Q{n(x)},{n(y + ry + 2)} {n(x + rx)},{n(y + 1)}", CREASE, .8, .4))
    o.append(clipped(d, "".join(det) + spot(s * 34, 572, 16, 6, SKIN_DD, .25)))
    o.append(rim(d, SKIN_DD, 4, .35, -s * 1.5, 2))
    return "".join(o)


def body_front(pose="down", tee="blue", hair="boy", mouth="smile", ring=None, ring_under_arms=False, neck_up=0):
    """The whole child from the front. ring: SVG drawn over the body (under the arms if ring_under_arms)."""
    rng = random.Random(3)
    c = TEE[tee]
    o = [ground(0, 622, 110, 10, .16)]
    if hair == "girl":
        o.append(f'<g transform="translate(0 {-neck_up})">{hair_back_girl()}</g>')
    o.append(leg(-1) + leg(1))
    o.append(foot_front(-1) + foot_front(1))
    o.append(shorts(SHORTS))
    o.append(P(NECK if not neck_up else f"M-21,{48 - neck_up} C-21,70 -22,88 -25,106 L25,106 C22,88 21,70 21,{48 - neck_up}Z", skin_fill(0, 60, 60, .5)))
    o.append(clipped(NECK, spot(0, 58, 26, 16, SKIN_DD, .45)))
    o.append(shirt_front(c, rng))
    body_ring = ring if ring_under_arms else ""
    o.append(body_ring)
    o.append(arm(pose, -1, c) + arm(pose, 1, c))
    head = head_front(hair, mouth)
    if hair == "girl":
        head = head.replace(hair_back_girl(), "", 1)
    o.append(f'<g transform="translate(0 {-neck_up})">{head}</g>')
    if ring and not ring_under_arms:
        o.append(ring)
    return "".join(o)


# ================================================================ cards (realistic)
def r_head():
    return body_front("down", "blue") + glow_ring(0, -10, 104, 108, w=10), (-118, -130, 118, 210)


def r_face():
    return head_front("boy") + glow_ring(0, 2, 86, 92, w=8), (-98, -110, 98, 104)


def r_nose():
    return head_front("girl") + glow_ring(0, 25, 22, 20, w=6), (-96, -110, 96, 104)


def r_mouth():
    return head_front("boy") + glow_ring(0, 50, 31, 19, w=6), (-96, -110, 96, 104)


def r_tongue():
    return head_front("girl", "tongue", happy=.3, raise_=3) + glow_ring(0, 62, 22, 26, w=6), (-96, -110, 96, 104)


def r_hair():
    outline = curve([(x * 1.07, y * 1.05 + 2) for x, y in GIRL_OUT] + [(66, 80), (0, 96), (-66, 80)])
    return body_front("down", "coral", "girl") + glow_path(outline, 9), (-118, -130, 118, 210)


def r_neck():
    return body_front("down", "mint", neck_up=10) + glow_ring(0, 82, 40, 24, w=7), (-118, -130, 118, 210)


def r_shoulder():
    rings = glow_ring(-84, 118, 30, 26, -20, w=7) + glow_ring(84, 118, 30, 26, 20, w=7)
    return body_front("down", "coral", "girl", ring=rings), (-130, -125, 130, 245)


def r_elbow():
    return body_front("hip", "blue", ring=glow_ring(-118, 212, 26, 26, w=7)), (-150, -115, 150, 330)


def r_belly():
    return body_front("belly", "sun", "girl", ring=glow_ring(0, 238, 74, 54, w=8), ring_under_arms=True), (-150, -115, 150, 420)


def r_leg():
    return body_front("down", "mint", ring=glow_ring(-37, 468, 46, 140, w=8)), (-200, -112, 200, 632)


def r_knee():
    return body_front("down", "lilac", "girl", ring=glow_ring(-36, 468, 30, 30, w=7)), (-120, 280, 120, 630)


REAL = {"head": r_head, "face": r_face, "nose": r_nose, "mouth": r_mouth, "tongue": r_tongue, "hair": r_hair, "neck": r_neck,
        "shoulder": r_shoulder, "elbow": r_elbow, "belly": r_belly, "leg": r_leg, "knee": r_knee}
CARTOON = {}


def main(only=None):
    for cid, fn in REAL.items():
        if only and cid not in only:
            continue
        begin()
        body, box = fn()
        write(DECK, cid, body, box)
    for cid, fn in CARTOON.items():
        if only and cid not in only:
            continue
        begin()
        body, box = fn()
        write(DECK, cid, body, box, cartoon=True)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)

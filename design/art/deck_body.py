"""Body deck (身體): 20 cards, realistic and cartoon.

    python3 deck_body.py [id ...]     # writes app/assets/art/cards/body/<id>.svg and <id>_cartoon.svg

A friendly generic young child (warm natural skin, dark brown hair, plain T-shirt and shorts)
shows each part, and the part has a soft pale-yellow glow ring around it. Close-ups (eye, teeth)
fade out softly at their edges; hand, foot and toes are drawn big with a glow behind or around.
Units: the child's face is about 150 wide with its middle at (0, 0); the whole child stands about
720 tall (the head is about a quarter of that, like a 2-3 year old). The cartoon child has its own
units (round head of radius 80 at (0, 0), about 430 tall).
"""
import math
import random

from kit_bc import (P, at, begin, clipped, curve, ellipse_d, flat_disc, flat_ring, glow_path, glow_ring, ground, halo,
                    line, lt, dk, mirror_pts, mix, n, poly, rg, lg, rim, rot_pt, sline, spot, stitch, tube, write)

DECK = "body"

# ---------------------------------------------------------------- colours (realistic)
SKIN, SKIN_L, SKIN_D, SKIN_DD = "#EEC09E", "#F9DCC6", "#D9A07F", "#B97B5C"
CREASE = "#B07258"
LIP, LIP_L = "#DE8A80", "#F2AFA4"
BLUSH = "#F3907F"
HAIR, HAIR_L, HAIR_D, HAIR_SHINE = "#382619", "#6E4E3A", "#1A110C", "#A48370"
IRIS, IRIS_D = "#6A4430", "#2C1A10"
TEE = {"blue": "#7FB2DE", "coral": "#F09A86", "mint": "#8CCBB4", "lilac": "#B8A6DC", "sun": "#F4C95A"}
SHORTS = "#3F5679"


def skin_fill(cx, cy, r, tone=0.0):
    """Skin with soft light from the upper left."""
    return rg([(0, mix(SKIN_L, SKIN, tone)), (.55, mix(SKIN, SKIN_D, tone * .5)), (1, mix(SKIN_D, SKIN_DD, .25 + tone * .3))],
              n(cx - r * .25), n(cy - r * .3), n(r), user=True)


def cloth_fill(c, x0, y0, x1, y1):
    return lg([(0, lt(c, .18)), (.6, c), (1, dk(c, .14))], x0, y0, x1, y1, user=True)


def fade_piece(d, color, y0, y1, y2, xr=None, shade=SKIN_DD):
    """Where a close-up ends (wrist, ankle): skin that fades in over the cut edge (y0 to y1) and then
    out to nothing (y1 to y2), with a soft shade along the right side at xr."""
    o = P(d, lg([(0, color, 0), (.3, color), (.5, color, .85), (1, color, 0)], 0, y0, 0, y2, user=True))
    if xr is not None:
        o += spot(xr, (y1 + y2) / 2 - (y2 - y1) * .15, 9, abs(y2 - y1) * .5, shade, .35)
    return o


def _ext(p, q, y):
    """Point on the straight line from q through p at height y."""
    dx, dy = p[0] - q[0], p[1] - q[1]
    return (p[0] + dx * (y - p[1]) / dy, y)


def cut_outline(chain, y_cut):
    """Outline from an open chain of points (one side of the cut, around, to the other side), closed with
    straight sides down (or up) to y_cut, so a fade piece can continue those sides exactly."""
    a, b = _ext(chain[0], chain[1], y_cut), _ext(chain[-1], chain[-2], y_cut)
    return curve(chain, closed=False) + f" L{n(b[0])},{n(b[1])} L{n(a[0])},{n(a[1])}Z"


def cut_piece(chain, y0, y1):
    """The band between y0 and y1 along the straight sides of cut_outline(chain, ...)."""
    pts = [_ext(chain[0], chain[1], y0), _ext(chain[0], chain[1], y1), _ext(chain[-1], chain[-2], y1), _ext(chain[-1], chain[-2], y0)]
    return poly(pts)


# ================================================================ realistic head (front)
FACE = [(0, -82), (38, -77), (61, -60), (72, -32), (74, -2), (72, 24), (64, 46), (48, 64), (26, 76), (0, 80),
        (-26, 76), (-48, 64), (-64, 46), (-72, 24), (-74, -2), (-72, -32), (-61, -60), (-38, -77)]
FACE_D = curve(FACE)
FRINGE = [(66, -2), (65, -21), (60, -31), (52, -34), (43, -37), (33, -35), (23, -38), (12, -36), (1, -39), (-10, -36),
          (-21, -39), (-32, -36), (-43, -38), (-52, -34), (-60, -31), (-66, -21), (-67, -2)]
BOY_OUT = [(-69, 8), (-76, -20), (-77, -48), (-67, -75), (-45, -94), (-14, -103), (17, -102), (45, -93), (67, -75), (78, -48),
           (77, -20), (70, 8)]
GIRL_OUT = [(-74, 66), (-82, 46), (-87, 14), (-86, -22), (-79, -56), (-58, -86), (-26, -103), (8, -106), (40, -99), (66, -80),
            (82, -50), (88, -14), (88, 18), (84, 46), (80, 62), (73, 70), (70, 63), (65, 69)]
GIRL_IN_R = [(63, 56), (71, 26), (71, -4)]
GIRL_BACK = [(-88, -20), (-92, 30), (-88, 82), (-66, 100), (0, 104), (66, 100), (88, 82), (92, 30), (88, -20), (0, -60)]


def girl_hair_d():
    inner_l = [(-x, y) for x, y in reversed(GIRL_IN_R)]
    return curve(GIRL_OUT + GIRL_IN_R + FRINGE[1:-1] + inner_l + [(-69, 70), (-72, 62)])


def ear(side):
    s = side
    d = curve([(s * x, y) for x, y in [(66, -16), (77, -22), (86, -14), (89, 2), (86, 18), (78, 30), (66, 31), (60, 8)]])
    o = [P(d, skin_fill(s * 70, -4, 40, .25))]
    o.append(clipped(d, spot(s * 79, 2, 8, 15, SKIN_DD, .45) + spot(s * 84, -10, 5, 8, SKIN_L, .5)
                     + line(f"M{s * 74},-14 C{s * 84},-14 {s * 86},6 {s * 79},20", SKIN_DD, 2.2, .45)))
    o.append(rim(d, SKIN_DD, 4, .35, -s * 1.5, 2.5))
    return "".join(o)


def eye(cx, cy, s=1.0, side=1, look=(0, 0), happy=0.0, lashes=3):
    """One eye, about 32 wide at s=1 (side=+1 for the eye on the viewer's right)."""
    def T(x, y):
        return cx + side * x * s, cy + y * s
    h = happy * 3
    lid_up = [T(-15, 3), T(-9, -9 + h), T(4, -12 + h), T(15, -2)]
    lid_lo = [T(15, -2), T(8, 7 - happy * 4), T(-6, 9 - happy * 4), T(-15, 3)]
    shape = curve(lid_up + lid_lo[1:3], closed=True)
    ix, iy = cx + side * look[0] * s, cy + (-1.5 + look[1]) * s
    ir = 9.6 * s
    inner = [P(shape, lg([(0, "#E9DDD7"), (.35, "#FBF6F2"), (1, "#F4ECE6")])),
             f'<circle cx="{n(ix)}" cy="{n(iy)}" r="{n(ir)}" fill="{rg([(0, "#8A5A3C"), (.55, IRIS), (.85, IRIS_D), (1, "#1C110B")], .5, .55, .5)}"/>',
             f'<circle cx="{n(ix)}" cy="{n(iy)}" r="{n(ir * .45)}" fill="#120B08"/>',
             spot(ix + 2 * s * side, iy + 4 * s, ir * .5, ir * .35, "#C08A5E", .35),
             sline(curve(lid_up, closed=False), "#5A3A2C", 5 * s, .45)]
    o = [clipped(shape, "".join(inner))]
    o.append(f'<circle cx="{n(ix - 3.4 * s * side)}" cy="{n(iy - 4 * s)}" r="{n(2.7 * s)}" fill="#FFFFFF" fill-opacity=".95"/>')
    o.append(f'<circle cx="{n(ix + 3.5 * s * side)}" cy="{n(iy + 3.6 * s)}" r="{n(1.1 * s)}" fill="#FFFFFF" fill-opacity=".8"/>')
    up = curve([T(-16, 3.5), T(-9, -9.5 + h), T(4, -12.6 + h), T(15.5, -2.4), T(18, -4)], closed=False)
    o.append(line(up, "#2A1A12", 2.4 * s))
    lash = [(5, -12.3, 1.2, -4.6), (9.5, -10.4, 2.6, -4.2), (13, -7, 3.8, -3), (15.6, -3, 4.6, -1.2)][-lashes:]
    for k, (x, y, dx, dy) in enumerate(lash):
        x1, y1 = T(x, y + h)
        x2, y2 = T(x + dx, y + dy + h)
        o.append(line(f"M{n(x1)},{n(y1)} Q{n(x1 + side * dx * s * .2)},{n(y2 + 1.2 * s)} {n(x2)},{n(y2)}", "#2A1A12", (1.25 - k * .1) * s))
    o.append(line(curve([T(-13, -10 + h * .7), T(0, -17 + h * .7), T(13, -12 + h * .7)], closed=False), CREASE, 1.1 * s, .35))
    o.append(line(curve(lid_lo[:3] + [T(-14, 3.5)], closed=False), CREASE, .9 * s, .4))
    return "".join(o)


def brow(side, y=-21, raise_=0.0, s=1.0, cx=0.0):
    pts = [(cx + side * 46 * s, y + (3 - raise_) * s, 1.1 * s), (cx + side * 33 * s, y + (-2.5 - raise_ * 1.3) * s, 2.3 * s),
           (cx + side * 18 * s, y - raise_ * s, 1.9 * s), (cx + side * 13 * s, y + (1.5 - raise_) * s, 1.2 * s)]
    return P(tube(pts), "#5E412F", 'fill-opacity=".72"')


def nose(y=30, bridge=True):
    o = [sline(f"M-8,{y - 30} C-9,{y - 18} -10,{y - 10} -10,{y - 4}", SKIN_D, 7, .18),
         sline(f"M9,{y - 30} C10,{y - 18} 11,{y - 10} 11,{y - 4}", SKIN_D, 8, .26)] if bridge else []
    o += [spot(0, y - 6, 9, 7, SKIN_L, .55), spot(0, y + 3, 15, 5, SKIN_DD, .22),
         line(f"M-13,{y - 4} C-15,{y + 2} -11,{y + 5} -6,{y + 4}", CREASE, 1.3, .5),
         line(f"M13,{y - 4} C15,{y + 2} 11,{y + 5} 6,{y + 4}", CREASE, 1.3, .55)]
    for sd in (-1, 1):
        o.append(f'<ellipse cx="{n(sd * 4.8)}" cy="{n(y + 3.2)}" rx="2.9" ry="1.6" transform="rotate({sd * 18} {n(sd * 4.8)} {n(y + 3.2)})" fill="#8E4F40" fill-opacity=".72"/>')
    return "".join(o)


def mouth_smile(y=50):
    return "".join([
        P(f"M-17,{y - 2} C-8,{y + 2} 8,{y + 2} 17,{y - 2} C12,{y + 9} -12,{y + 9} -17,{y - 2}Z", LIP),
        P(f"M-12,{y + 2} C-6,{y + 9} 6,{y + 9} 12,{y + 2} C6,{y + 4} -6,{y + 4} -12,{y + 2}Z", LIP_L, 'fill-opacity=".6"'),
        P(f"M-16,{y - 3} C-10,{y - 6} -4,{y - 7} 0,{y - 5} C4,{y - 7} 10,{y - 6} 16,{y - 3} C8,{y - 1} -8,{y - 1} -16,{y - 3}Z", mix(LIP, SKIN_D, .3), 'fill-opacity=".85"'),
        line(f"M-19,{y - 4.5} C-9,{y + 2} 9,{y + 2} 19,{y - 4.5}", "#93473F", 1.8),
        line(f"M-21,{y - 7} C-19,{y - 4} -19,{y - 2} -20,{y}", CREASE, 1.1, .4),
        line(f"M21,{y - 7} C19,{y - 4} 19,{y - 2} 20,{y}", CREASE, 1.1, .4),
        spot(0, y + 15, 14, 5, SKIN_DD, .18)])


def mouth_teeth(y=48):
    """Big happy smile with the top baby teeth showing."""
    W = 25
    hole = f"M{-W},{y - 4} C{-W * .5},{y} {W * .5},{y} {W},{y - 4} C{W * .8},{y + 16} {W * .35},{y + 23} 0,{y + 23} C{-W * .35},{y + 23} {-W * .8},{y + 16} {-W},{y - 4}Z"
    inner = [P(hole, rg([(0, "#9A3C3C"), (1, "#5E1E22")], .5, .7, .7)), spot(0, y + 22, W * .7, 8, "#E77B80", .95, hard=.5)]
    tf = lg([(0, "#FFFFFF"), (.7, "#FBF6EC"), (1, "#E6DACB")])
    for x, tw, th in [(-17.5, 5.4, 6.2), (-10.2, 6.2, 7.6), (-3.3, 6.2, 8.8), (3.3, 6.2, 8.8), (10.2, 6.2, 7.6), (17.5, 5.4, 6.2)]:
        top = y - 5
        inner.append(P(f"M{n(x - tw / 2)},{n(top)} L{n(x + tw / 2)},{n(top)} L{n(x + tw / 2)},{n(top + th - 2.2)} "
                       f"Q{n(x + tw / 2)},{n(top + th)} {n(x)},{n(top + th)} Q{n(x - tw / 2)},{n(top + th)} {n(x - tw / 2)},{n(top + th - 2.2)}Z", tf))
    for x in (-6.5, 0, 6.5):
        inner.append(P(f"M{n(x - 2.8)},{y + 22} L{n(x - 2.8)},{y + 18.5} Q{n(x)},{y + 16.5} {n(x + 2.8)},{y + 18.5} L{n(x + 2.8)},{y + 22}Z", "#F4EEE4"))
    inner.append(sline(f"M{-W},{y - 3} C{-W * .5},{y + 1} {W * .5},{y + 1} {W},{y - 3}", "#C99A90", 3, .3))
    inner.append(spot(-W * .82, y + 4, 6, 10, "#3A1012", .45) + spot(W * .82, y + 4, 6, 10, "#3A1012", .45))
    o = [clipped(hole, "".join(inner))]
    o.append(P(f"M{-W - 2},{y - 5} C{-W * .5},{y - 9} -4,{y - 10} 0,{y - 8} C4,{y - 10} {W * .5},{y - 9} {W + 2},{y - 5} "
               f"C{W * .5},{y - 3} {-W * .5},{y - 3} {-W - 2},{y - 5}Z", mix(LIP, SKIN_D, .25)))
    o.append(P(f"M{-W - 1},{y - 3} C{-W * .8},{y + 17} {-W * .35},{y + 24} 0,{y + 24} C{W * .35},{y + 24} {W * .8},{y + 17} {W + 1},{y - 3} "
               f"C{W * .85},{y + 20} {W * .4},{y + 29} 0,{y + 29} C{-W * .4},{y + 29} {-W * .85},{y + 20} {-W - 1},{y - 3}Z", LIP))
    o.append(spot(0, y + 26.5, 8, 1.6, "#FFFFFF", .4))
    o.append(line(f"M{-W - 5},{y - 9} C{-W - 3},{y - 5} {-W - 3},{y - 2} {-W - 4},{y + 1}", CREASE, 1.2, .45))
    o.append(line(f"M{W + 5},{y - 9} C{W + 3},{y - 5} {W + 3},{y - 2} {W + 4},{y + 1}", CREASE, 1.2, .45))
    return "".join(o)


def mouth_tongue(y=48):
    o = [P(f"M-15,{y} C-8,{y - 5} 8,{y - 5} 15,{y} C12,{y + 9} -12,{y + 9} -15,{y}Z", "#6A2428"),
         P(f"M-15,{y - 1} C-8,{y - 6} -3,{y - 7} 0,{y - 5} C3,{y - 7} 8,{y - 6} 15,{y - 1} C8,{y - 3} -8,{y - 3} -15,{y - 1}Z", mix(LIP, SKIN_D, .25)),
         P(f"M-16,{y + 1} C-12,{y + 9} 12,{y + 9} 16,{y + 1} C14,{y + 12} -14,{y + 12} -16,{y + 1}Z", LIP)]
    tongue = f"M-11.5,{y + 1} C-13,{y + 14} -11,{y + 27} 0,{y + 28} C11,{y + 27} 13,{y + 14} 11.5,{y + 1}Z"
    o.append(P(tongue, lg([(0, "#D9636E"), (.35, "#F08890"), (1, "#E7747D")])))
    o.append(clipped(tongue, spot(-4, y + 15, 4, 8, "#FFFFFF", .35) + spot(0, y + 4, 12, 4, "#8E2E38", .5)
                     + line(f"M0,{y + 4} C-.5,{y + 12} 0,{y + 18} .5,{y + 22}", "#C24E5A", 1.4, .6)))
    o.append(line(f"M-17,{y - 3} C-19,{y - 1} -19,{y + 2} -17,{y + 4}", CREASE, 1.1, .4))
    o.append(line(f"M17,{y - 3} C19,{y - 1} 19,{y + 2} 17,{y + 4}", CREASE, 1.1, .4))
    return "".join(o)


def strands(rng, targets, crown, count, spread=14, bow=18):
    o = []
    for _ in range(count):
        tx_, ty_ = targets[int(rng.random() * len(targets))]
        tx_ += rng.uniform(-4, 4)
        sx, sy = crown[0] + rng.uniform(-spread, spread), crown[1] + rng.uniform(-4, 10)
        mx, my = (sx + tx_) / 2 + (tx_ - sx) * .25 + rng.uniform(-6, 6), (sy + ty_) / 2 - bow + rng.uniform(-6, 6)
        o.append(f"M{sx:.0f},{sy:.0f}Q{mx:.0f},{my:.0f} {tx_:.0f},{ty_:.0f}")
    h = len(o) // 2
    return (f'<path d="{"".join(o[:h])}" fill="none" stroke="{HAIR_L}" stroke-width="1.3" stroke-opacity=".5"/>'
            f'<path d="{"".join(o[h:])}" fill="none" stroke="{HAIR_D}" stroke-width="1.5" stroke-opacity=".55"/>')


def edge_pts(pts, k=3):
    out = []
    for a, b in zip(pts, pts[1:]):
        for j in range(k):
            out.append((a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k))
    return out


def hair_front(kind="boy", seed=5):
    rng = random.Random(seed)
    if kind == "boy":
        shape = curve(BOY_OUT + FRINGE)
        targets = edge_pts(FRINGE) + BOY_OUT[:3] + BOY_OUT[-3:]
    else:
        shape = girl_hair_d()
        targets = edge_pts(FRINGE) + [(x * .97, y) for x, y in GIRL_OUT[:5] + GIRL_OUT[-8:]]
    inner = [P(shape, rg([(0, HAIR_L), (.5, HAIR), (1, HAIR_D)], -20, -80, 160, user=True)), strands(rng, targets, (6, -98), 80),
             sline("M-54,-72 C-30,-92 26,-94 54,-74", HAIR_SHINE, 16, .42), sline("M-44,-72 C-24,-86 20,-88 44,-74", "#CDB2A0", 4, .4)]
    if kind == "girl":
        inner += [sline("M-80,-34 C-84,-4 -84,26 -76,56", HAIR_SHINE, 9, .32), sline("M82,-30 C86,0 86,30 80,56", HAIR_D, 12, .45),
                  line("M-76,40 C-74,52 -72,60 -70,66", HAIR_D, 1.2, .5), line("M78,40 C76,52 72,60 68,66", HAIR_D, 1.2, .5)]
    return clipped(shape, "".join(inner)) + rim(shape, HAIR_D, 6, .5)


def hair_back_girl():
    d = curve(GIRL_BACK)
    return P(d, rg([(0, HAIR), (1, HAIR_D)], 0, 20, 110, user=True))


def hair_clip(x, y):
    d = f"M{x - 12},{y - 6} C{x - 4},{y - 12} {x + 6},{y - 4} {x + 13},{y - 10} L{x + 15},{y - 3} C{x + 7},{y + 3} {x - 3},{y - 4} {x - 10},{y + 2}Z"
    return P(d, lg([(0, "#F7A8BC"), (1, "#D9708C")])) + spot(x - 2, y - 6, 6, 2, "#FFFFFF", .6)


def head_front(hair="boy", mouth="smile", happy=0.0, raise_=0.0, look=(0, 0), back_hair=True):
    o = []
    if hair == "girl" and back_hair:
        o.append(hair_back_girl())
    o.append(ear(-1) + ear(1))
    face = [P(FACE_D, skin_fill(0, -10, 115)), spot(-44, 30, 17, 12, BLUSH, .38), spot(44, 30, 17, 12, BLUSH, .38),
            spot(-24, -50, 26, 18, SKIN_L, .5), sline(curve([(x, y + 5) for x, y in FRINGE], closed=False), SKIN_DD, 12, .3),
            spot(0, 66, 26, 10, SKIN_L, .35)]
    o.append(clipped(FACE_D, "".join(face)))
    o.append(rim(FACE_D, SKIN_DD, 7, .36, 2.5, 3))
    o.append(brow(-1, raise_=raise_) + brow(1, raise_=raise_))
    o.append(eye(-29, 5, 1.0, -1, look, happy) + eye(29, 5, 1.0, 1, look, happy))
    o.append(nose(31))
    o.append({"smile": mouth_smile, "tongue": mouth_tongue}[mouth]() if mouth != "teeth" else
             f'<g transform="translate(0 47) scale(.84) translate(0 -47)">{mouth_teeth(47)}</g>')
    o.append(hair_front(hair))
    if hair == "girl":
        o.append(hair_clip(50, -70))
    return "".join(o)


# ================================================================ realistic hands
def finger_set(spread):
    """Four fingers and the thumb of a left hand seen from the back (fingers up, thumb on the right)."""
    F = []
    for bx, by, ang, ln, ws, rbx in [(-33, 14, -15, 50, (9.8, 9, 8), -28), (-14, 6, -6, 64, (10.8, 10, 8.8), -10),
                                     (4, 4, 0, 70, (11.2, 10.6, 9.4), 7.5), (22, 8, 9, 63, (10.8, 10.2, 9), 25)]:
        a = math.radians(ang * spread)
        bx = bx * spread + rbx * (1 - spread)
        ln = ln * (1 - .06 * (1 - spread))
        F.append([(bx + math.sin(a) * ln * t, by - math.cos(a) * ln * t, w) for t, w in zip((0, .5, 1), ws)])
    if spread > .5:
        thumb = [(34, 50, 13), (48, 30, 12), (59, 12, 10.6), (64, -4, 9.6)]
    else:
        thumb = [(32, 52, 12.6), (42, 32, 11.6), (48, 14, 10.4), (50, -2, 9.4)]
    return F, thumb


PALM = [(36, 90), (42, 62), (46, 36), (38, 13), (22, 3), (0, 1), (-26, 3), (-42, 12), (-46, 28), (-44, 56), (-37, 88)]
FIST = [(36, 90), (42, 62), (46, 36), (40, 16), (30, 8), (14, 6), (-4, 4), (-22, 4), (-36, 2), (-44, 14), (-47, 30), (-44, 56), (-37, 88)]


def hand_big(spread=1.0, detail=True, fold=None):
    """A child's left hand (back), fingers up; wrist at y about 100. fold: fingers folded into a fist (finger card)."""
    F, thumb = finger_set(spread)
    fill = rg([(0, SKIN_L), (.55, SKIN), (1, "#DCA27E")], -10, -20, 130, user=True)
    o = []
    nails, creases = [], []
    for i, f in enumerate(F):
        if fold and i in fold:
            continue
        d = tube(f)
        o.append(P(d, fill) + rim(d, SKIN_DD, 4.5, .4, 2, 2.5))
        if detail:
            for t, k in ((.52, 3), (.8, 2)):
                x, y, a, w = at(f, t)
                ra = math.radians(a + 90)
                for j in range(k):
                    off = (j - (k - 1) / 2) * 2.4
                    cx, cy = x + math.cos(math.radians(a)) * off, y + math.sin(math.radians(a)) * off
                    creases.append(f"M{cx + math.cos(ra) * w * .5:.1f},{cy + math.sin(ra) * w * .5:.1f}Q{cx + math.cos(math.radians(a)) * 1.6:.1f},"
                                   f"{cy + math.sin(math.radians(a)) * 1.6:.1f} {cx - math.cos(ra) * w * .5:.1f},{cy - math.sin(ra) * w * .5:.1f}")
            nails.append(nail(f))
    palm = cut_outline(PALM, 100)
    o.append(P(palm, fill))
    pd = []
    if fold:
        for x, y in ((-30, -2), (-14, -12), (4, -14)):
            pd.append(spot(x, y, 9, 7, SKIN_L, .7) + spot(x + 3, y + 12, 8, 4, SKIN_DD, .25))
        pd.append(line("M-36,10 C-28,2 -20,-2 -12,-4 M-21,0 C-12,-8 -2,-10 8,-8", CREASE, 1.1, .4))
    else:
        for f in F:
            x, y = f[0][0], f[0][1]
            pd.append(spot(x, y - 2, 7, 5, "#FBE3D2", .8) + spot(x + 1, y + 3, 3, 2.2, CREASE, .35))
    pd.append(spot(-14, 40, 30, 36, SKIN_L, .35) + sline("M-44,40 C-38,70 -34,96 -32,110", SKIN_DD, 10, .25))
    o.append(clipped(palm, "".join(pd)))
    o.append(clipped("M-60,-60 H70 V86 H-60Z", rim(palm, SKIN_DD, 5, .4, 2, 2.5)))
    td = tube(thumb)
    o.append(P(td, fill) + rim(td, SKIN_DD, 4.5, .4, 2, 2.5))
    if detail:
        x, y, a, w = at(thumb, .55)
        creases.append(f"M{x - 6:.1f},{y + 3:.1f}Q{x:.1f},{y + 5:.1f} {x + 6:.1f},{y - 3:.1f}")
        nails.append(nail(thumb))
        o.append(f'<path d="{"".join(creases)}" fill="none" stroke="#B87A58" stroke-width=".9" stroke-opacity=".45"/>')
        o.append("".join(nails))
    return "".join(o)


def nail(f, t=.86):
    x, y, a, w = at(f, t)
    nw, nl = w * .62, w * 1.2
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({a + 90:.1f})">'
            f'<rect x="{-nw:.1f}" y="{-nl * .6:.1f}" width="{2 * nw:.1f}" height="{nl * 1.25:.1f}" rx="{nw:.1f}" fill="#F3CDBF"/>'
            f'<rect x="{-nw * .86:.1f}" y="{-nl * .66:.1f}" width="{2 * nw * .86:.1f}" height="{nl * .3:.1f}" rx="{nw * .5:.1f}" fill="#FFF5EE" fill-opacity=".95"/>'
            f'<ellipse cx="{-nw * .3:.1f}" cy="{nl * .1:.1f}" rx="{nw * .25:.1f}" ry="{nl * .32:.1f}" fill="#FFFFFF" fill-opacity=".55"/></g>')


def hand_small(x, y, ang, s=.42, mirror=False, spread=0.0, palm_side=False):
    """The same hand, small (on the whole child): wrist at (x, y), fingers pointing at angle ang."""
    F, thumb = finger_set(spread)
    fill = skin_fill(0, 30, 120, .1)
    o = []
    for f in F:
        d = tube(f)
        o.append(P(d, fill) + rim(d, SKIN_DD, 4, .35, 2, 2.5))
    palm = cut_outline(PALM, 100)
    o.append(P(palm, fill) + rim(palm, SKIN_DD, 5, .35, 2, 2.5))
    td = tube(thumb)
    o.append(P(td, fill) + rim(td, SKIN_DD, 4, .35, 2, 2.5))
    o.append("".join(nail(f) for f in F + [thumb]) if not palm_side else "")
    sx = -s if mirror else s
    return f'<g transform="translate({n(x)} {n(y)}) rotate({n(ang - 90)}) scale({sx:.3f} {-s:.3f}) translate(0 -100)">{"".join(o)}</g>'


# ================================================================ realistic body (front and back)
NECK = "M-21,48 C-21,70 -22,88 -25,106 L25,106 C22,88 21,70 21,48Z"
SHIRT = [(-30, 94), (-56, 99), (-74, 110), (-80, 130), (-75, 154), (-79, 200), (-84, 250), (-81, 300), (-40, 305), (0, 307),
         (40, 305), (81, 300), (84, 250), (79, 200), (75, 154), (80, 130), (74, 110), (56, 99), (30, 94), (16, 106), (0, 110), (-16, 106)]
SHIRT_BACK = SHIRT[:19] + [(14, 97), (0, 99), (-14, 97)]
SLEEVE_CLIP = curve([(-32, 90), (-74, 106), (-100, 122), (-170, 160), (-170, 420), (170, 420), (170, 160), (100, 122), (74, 106), (32, 90), (0, 60)])
SHORTS_PTS = [(-79, 286), (79, 286), (83, 330), (88, 386), (48, 394), (7, 391), (0, 356), (-7, 391), (-48, 394), (-88, 386), (-83, 330)]
LEG = [(-39, 330, 31), (-38, 400, 27.5), (-36, 468, 21.5), (-36, 512, 23), (-34, 556, 15.5), (-33, 580, 13)]
ARMS = {
    "down": [(-68, 124, 18), (-82, 180, 16.5), (-90, 236, 14.5), (-93, 288, 13.5), (-94, 322, 11.8)],
    "belly": [(-68, 124, 18), (-88, 172, 16.5), (-97, 212, 14.5), (-80, 238, 14), (-56, 248, 12)],
    "wave": [(-68, 124, 18), (-96, 160, 16.5), (-119, 194, 15), (-127, 200, 14.6), (-133, 188, 14.2), (-138, 150, 13.4), (-140, 118, 12)],
}


def limb(pts, light=-1):
    d = tube(pts, k=2 if len(pts) > 5 else 1)
    x0 = sum(p[0] for p in pts) / len(pts)
    stops = [(0, SKIN_L), (.5, SKIN), (1, SKIN_D)]
    o = P(d, lg(stops if light < 0 else stops[::-1], x0 - 24, 0, x0 + 24, 0, user=True)) + rim(d, SKIN_DD, 6, .3, 2, 2)
    return o, d


def arm(pose, side, sleeve_c, back=False):
    pts = ARMS[pose]
    if side > 0:
        pts = mirror_pts(pts)
    a, d = limb(pts, side)
    o = [a]
    if pose == "wave":
        ex, ey = pts[3][0], pts[3][1]
        o.append(clipped(d, spot(ex + side * 3, ey + 4, 9, 7, SKIN_DD, .35) + line(f"M{n(ex + side * 10)},{n(ey - 8)} q{n(-side * 6)},{n(-4)} {n(-side * 12)},{n(-2)}", CREASE, 1, .45)))
    else:
        ex, ey, ea, ew = at(pts, .5)
        o.append(clipped(d, spot(ex, ey, ew * .7, ew * .45, SKIN_DD if back else SKIN_L, .3, ea)))
    wx, wy = pts[-1][0], pts[-1][1]
    _, _, wa, _ = at(pts, .97)
    if pose == "wave":
        o.append(hand_small(wx, wy + 4, -90 - side * 6, .5, mirror=side < 0, spread=1.0))
    elif pose == "belly":
        o.append(hand_small(wx - side * 4, wy, wa, .44, mirror=side > 0, spread=.15))
    else:
        o.append(hand_small(wx, wy - 4, wa, .42, mirror=(side < 0) != back, spread=0.0, palm_side=False))
    # short sleeve over the top of the arm, cut along the shoulder line
    sx, sy = pts[0][0], pts[0][1]
    ux, uy = pts[1][0] - sx, pts[1][1] - sy
    L = math.hypot(ux, uy)
    ux, uy = ux / L, uy / L
    end = (sx + ux * 48, sy + uy * 48)
    sd = tube([(sx - ux * 22, sy - uy * 22, 25), (sx + ux * 18, sy + uy * 18, 25.5), (end[0], end[1], 24)], caps=(False, False))
    nx, ny = -uy, ux
    sl = [P(sd, cloth_fill(sleeve_c, sx - 30, 0, sx + 30, 0)), rim(sd, dk(sleeve_c, .35), 6, .3, 2 * -side, 3),
          sline(f"M{n(end[0] - nx * 22)},{n(end[1] - ny * 22)} L{n(end[0] + nx * 22)},{n(end[1] + ny * 22)}", dk(sleeve_c, .45), 3, .35, 2),
          stitch(f"M{n(end[0] - nx * 23 - ux * 4)},{n(end[1] - ny * 23 - uy * 4)} L{n(end[0] + nx * 23 - ux * 4)},{n(end[1] + ny * 23 - uy * 4)}", dk(sleeve_c, .4), 1, .5)]
    o.append(clipped(SLEEVE_CLIP, "".join(sl)))
    return "".join(o)


def shirt(c, back=False):
    d = curve(SHIRT_BACK if back else SHIRT)
    inner = [P(d, cloth_fill(c, -80, 100, 80, 300)),
             sline("M-50,160 C-42,200 -46,250 -52,296", dk(c, .25), 12, .25),
             sline("M48,170 C40,210 44,250 50,296", dk(c, .25), 10, .22),
             sline("M-26,140 C-18,180 -16,230 -20,290", lt(c, .4), 14, .3),
             stitch("M-80,292 C-40,298 40,298 80,292", dk(c, .4), 1, .5)]
    if back:
        inner += [spot(-36, 150, 26, 22, lt(c, .35), .4), spot(36, 150, 26, 22, lt(c, .3), .35), sline("M0,110 L0,290", dk(c, .2), 10, .18)]
    else:
        inner.append(spot(0, 250, 70, 40, lt(c, .35), .35))
    o = [clipped(d, "".join(inner)), rim(d, dk(c, .45), 8, .32)]
    col = "M-30,95 C-20,104 20,104 30,95" if back else "M-30,95 C-20,112 20,112 30,95"
    o.append(line(col, dk(c, .2), 8) + line(col, lt(c, .25), 4, .8))
    return "".join(o)


def shorts(c, back=False):
    d = curve(SHORTS_PTS)
    inner = [P(d, cloth_fill(c, -80, 290, 80, 390)), sline("M0,300 L0,356", dk(c, .4), 6, .3),
             sline("M-60,330 C-56,350 -50,370 -48,392", lt(c, .3), 10, .25),
             stitch("M-87,380 C-60,388 -30,389 -8,386", lt(c, .3), 1, .6), stitch("M87,380 C60,388 30,389 8,386", lt(c, .3), 1, .6)]
    if back:
        inner.append(spot(-40, 340, 34, 30, lt(c, .25), .3) + spot(40, 340, 34, 30, lt(c, .2), .25))
    return clipped(d, "".join(inner)) + rim(d, dk(c, .5), 8, .35)


def leg(side, back=False):
    pts = LEG if side < 0 else mirror_pts(LEG)
    d = tube(pts, caps=(False, True))
    x0 = side * 36
    st = [(0, SKIN_L), (.5, SKIN), (1, SKIN_D)]
    o = [P(d, lg(st if side < 0 else st[::-1], x0 - 32, 0, x0 + 32, 0, user=True))]
    if back:
        det = [spot(x0, 470, 15, 9, SKIN_DD, .25), spot(x0 - side * 3, 515, 12, 30, SKIN_L, .35),
               line(f"M{x0 - 13},468 C{x0 - 5},472 {x0 + 5},472 {x0 + 13},468", CREASE, 1.2, .5)]
    else:
        det = [spot(x0 + side * 2, 464, 14, 12, SKIN_L, .6), spot(x0 + side * 2, 476, 12, 5, SKIN_DD, .22),
               spot(x0 - side * 4, 520, 10, 30, SKIN_L, .3),
               line(f"M{x0 - 11},481 C{x0 - 4},485 {x0 + 4},485 {x0 + 11},481", CREASE, .9, .35)]
    o.append(clipped(d, "".join(det)))
    o.append(rim(d, SKIN_DD, 6, .35, side * -2, 2))
    return "".join(o)


def foot_front(side):
    pts = [(-47, 568), (-26, 568), (-19, 590), (-12, 606), (-17, 616), (-36, 619), (-55, 615), (-60, 605), (-55, 588)]
    if side > 0:
        pts = mirror_pts(pts)
    d = curve(pts)
    o = [P(d, skin_fill(side * 38, 580, 50, .15))]
    det = []
    for x, y, rx, ry in [(-18, 610, 6.2, 5), (-28, 613, 4.6, 4.2), (-37, 614, 4.2, 3.8), (-45, 613, 3.8, 3.4), (-52, 610, 3.4, 3)]:
        x = x if side < 0 else -x
        det.append(spot(x, y - 1, rx, ry, SKIN_L, .6))
        det.append(line(f"M{n(x - rx)},{n(y + 1)} Q{n(x)},{n(y + ry + 2)} {n(x + rx)},{n(y + 1)}", CREASE, .8, .4))
    o.append(clipped(d, "".join(det) + spot(side * 34, 572, 16, 6, SKIN_DD, .25)))
    o.append(rim(d, SKIN_DD, 4, .35, -side * 1.5, 2))
    return "".join(o)


def heel_back(side):
    pts = [(-50, 566), (-24, 566), (-20, 590), (-24, 612), (-37, 618), (-50, 612), (-54, 590)]
    if side > 0:
        pts = mirror_pts(pts)
    d = curve(pts)
    return P(d, skin_fill(side * 37, 590, 40, .2)) + clipped(d, spot(side * 37, 606, 12, 8, SKIN_L, .5)) + rim(d, SKIN_DD, 4, .35, 0, 2)


def body_front(pose="down", tee="blue", hair="boy", mouth="smile", ring="", ring_under_arms=False, neck_up=0):
    c = TEE[tee]
    o = [ground(0, 622, 110, 10, .16)]
    if hair == "girl":
        o.append(f'<g transform="translate(0 {-neck_up})">{hair_back_girl()}</g>')
    o.append(leg(-1) + leg(1) + foot_front(-1) + foot_front(1) + shorts(SHORTS))
    nk = NECK if not neck_up else f"M-21,{48 - neck_up} C-21,70 -22,88 -25,106 L25,106 C22,88 21,70 21,{48 - neck_up}Z"
    o.append(P(nk, skin_fill(0, 60, 60, .5)) + clipped(nk, spot(0, 58 - neck_up, 26, 16, SKIN_DD, .45)))
    o.append(shirt(c))
    if ring_under_arms:
        o.append(ring)
    o.append(arm(pose, -1, c) + arm("down" if pose == "wave" else pose, 1, c))
    o.append(f'<g transform="translate(0 {-neck_up})">{head_front(hair, mouth, back_hair=False)}</g>')
    if not ring_under_arms:
        o.append(ring)
    return "".join(o)


def hair_back_boy(seed=8):
    rng = random.Random(seed)
    pts = [(-74, 12), (-78, -30), (-70, -70), (-44, -95), (0, -103), (44, -95), (70, -70), (78, -30), (74, 12), (66, 40), (50, 56),
           (36, 52), (24, 60), (10, 56), (-4, 62), (-18, 56), (-32, 60), (-48, 54), (-66, 40)]
    d = curve(pts)
    crown = (6, -58)
    tg = edge_pts(pts + pts[:1], 2)
    sw = []
    for i in range(46):
        a = i / 46 * math.tau
        r1, r2 = 4 + rng.uniform(0, 6), 30 + rng.uniform(0, 14)
        x1, y1 = crown[0] + math.cos(a) * r1, crown[1] + math.sin(a) * r1
        x2, y2 = crown[0] + math.cos(a + .9) * r2, crown[1] + math.sin(a + .9) * r2
        cx_, cy_ = crown[0] + math.cos(a + .45) * r2 * .8, crown[1] + math.sin(a + .45) * r2 * .8
        sw.append(f"M{x1:.0f},{y1:.0f}Q{cx_:.0f},{cy_:.0f} {x2:.0f},{y2:.0f}")
    inner = [P(d, rg([(0, HAIR_L), (.45, HAIR), (1, HAIR_D)], 0, -50, 150, user=True)),
             strands(rng, tg, crown, 70, spread=20, bow=-4),
             f'<path d="{"".join(sw)}" fill="none" stroke="{HAIR_D}" stroke-width="1.3" stroke-opacity=".45"/>',
             spot(crown[0], crown[1], 8, 7, HAIR_D, .5),
             sline("M-50,-76 C-26,-92 26,-92 50,-76", HAIR_SHINE, 16, .4)]
    return clipped(d, "".join(inner)) + rim(d, HAIR_D, 6, .5)


def body_back(tee="coral", ring=""):
    c = TEE[tee]
    o = [ground(0, 622, 110, 10, .16), leg(-1, True) + leg(1, True) + heel_back(-1) + heel_back(1) + shorts(SHORTS, True)]
    o.append(P(NECK, skin_fill(0, 60, 60, .3)) + clipped(NECK, spot(0, 56, 26, 14, SKIN_DD, .35)))
    o.append(shirt(c, back=True))
    o.append(ring)
    o.append(arm("down", -1, c, True) + arm("down", 1, c, True))
    o.append(P(FACE_D, skin_fill(0, -10, 115, .2)))
    o.append(ear(-1) + ear(1))
    o.append(hair_back_boy())
    return "".join(o)


# ================================================================ realistic close-ups
def skin_patch(cx, cy, rx, ry):
    """Skin that fades out softly at its edge (for close-ups)."""
    g = rg([(0, SKIN_L), (.42, SKIN), (.66, mix(SKIN, SKIN_D, .2), .95), (.84, SKIN, .5), (1, SKIN, 0)], .5, .5, .5, .46, .42)
    return f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="{g}"/>'


def r_eye():
    o = [skin_patch(0, 0, 190, 160), spot(-40, 70, 60, 30, BLUSH, .18), spot(0, 92, 70, 26, SKIN_D, .2)]
    o.append(P(tube([(-104, -66, 4), (-60, -88, 9), (0, -90, 8), (50, -74, 5), (78, -58, 2.5)]), "#5E412F", 'fill-opacity=".7"'))
    o.append(eye(0, 4, 4.6, 1, (0, 0), 0, 4))
    o.append(glow_ring(0, 2, 112, 76, w=12))
    return "".join(o), (-200, -170, 200, 170)


def r_teeth():
    head = head_front("boy", "teeth", happy=.5)
    return head + glow_ring(0, 55, 31, 23, w=6), (-98, -110, 98, 104)


WRIST = cut_piece(PALM, 80, 136)


def r_hand():
    o = [halo(0, 6, 128, 128), hand_big(1.0), fade_piece(WRIST, "#E4AE8B", 80, 96, 136, xr=26)]
    return "".join(o), (-80, -120, 90, 130)


def fist_big():
    """Left hand (back) making "one": index finger up, the other fingers folded, thumb tucked at the side."""
    F, _ = finger_set(1.0)
    fill = rg([(0, SKIN_L), (.55, SKIN), (1, "#DCA27E")], -10, -20, 130, user=True)
    o = []
    index = F[3]
    d = tube(index)
    o.append(P(d, fill) + rim(d, SKIN_DD, 4.5, .4, 2, 2.5))
    for x in (-31, -13, 5):
        ld = tube([(x, 10, 10.6), (x + .5, -8, 10.2), (x + 1, -16, 9.8)])
        o.append(P(ld, fill) + clipped(ld, spot(x - 2, -14, 7, 6, "#FBE3D2", .8) + spot(x + 5, 0, 5, 12, SKIN_DD, .25)) + rim(ld, SKIN_DD, 4, .4, 2, 2.5))
    palm = cut_outline(FIST, 100)
    o.append(P(palm, fill))
    pd = [spot(x, 6, 7, 4, CREASE, .3) for x in (-31, -13, 5, 22)]
    pd.append(spot(-14, 44, 30, 32, SKIN_L, .35) + sline("M-44,40 C-38,70 -34,96 -32,110", SKIN_DD, 10, .25))
    o.append(clipped(palm, "".join(pd)) + clipped("M-60,-60 H70 V86 H-60Z", rim(palm, SKIN_DD, 5, .4, 2, 2.5)))
    thumb = [(33, 56, 12.6), (44, 40, 11.6), (46, 26, 10.6), (40, 15, 9.8)]
    td = tube(thumb)
    o.append(P(td, fill) + rim(td, SKIN_DD, 4.5, .4, 2, 2.5) + nail(thumb, .84))
    cr = []
    for t_, k in ((.52, 3), (.8, 2)):
        x, y, a, w = at(index, t_)
        ra = math.radians(a + 90)
        for j in range(k):
            off = (j - (k - 1) / 2) * 2.4
            cx, cy = x + math.cos(math.radians(a)) * off, y + math.sin(math.radians(a)) * off
            cr.append(f"M{cx + math.cos(ra) * w * .5:.1f},{cy + math.sin(ra) * w * .5:.1f}Q{cx:.1f},{cy + 1.6:.1f} {cx - math.cos(ra) * w * .5:.1f},{cy - math.sin(ra) * w * .5:.1f}")
    o.append(f'<path d="{"".join(cr)}" fill="none" stroke="#B87A58" stroke-width=".9" stroke-opacity=".45"/>' + nail(index))
    return "".join(o)


def r_finger():
    F, _ = finger_set(1.0)
    x0, y0 = F[3][0][0], F[3][0][1]
    x1, y1 = F[3][2][0], F[3][2][1]
    o = [fist_big(), fade_piece(WRIST, "#E4AE8B", 80, 96, 136, xr=26), glow_ring((x0 + x1) / 2 + 1, (y0 + y1) / 2 - 7, 24, 47, 9, w=8)]
    return "".join(o), (-80, -110, 90, 130)


FOOT_SIDE = [(41, -46), (43, -24), (50, -4), (60, 14), (64, 32), (58, 52), (44, 62), (8, 64), (-30, 60), (-70, 64), (-104, 62), (-120, 58),
             (-122, 40), (-112, 28), (-94, 29), (-74, 22), (-50, 8), (-32, -10), (-20, -30), (-16, -46)]


def r_foot():
    d = cut_outline(FOOT_SIDE, -72)
    fill = rg([(0, SKIN_L), (.55, SKIN), (1, SKIN_D)], -40, -10, 150, user=True)
    o = [halo(-34, -6, 122, 108), ground(-28, 66, 110, 8, .22)]
    for x, y, r in [(-75, 20, 5.8), (-85, 21, 6.6), (-96, 23, 7.4), (-108, 26, 8.2)]:
        td = curve([(x - r, y + 6), (x - r * .9, y - r * .4), (x, y - r * .85), (x + r * .9, y - r * .4), (x + r, y + 6)])
        o.append(P(td, skin_fill(x, y, 16, .2)) + clipped(td, spot(x - 1, y - r * .4, r * .6, r * .4, SKIN_L, .7)) + rim(td, SKIN_DD, 2, .35, 1.5, 1.5))
        o.append(f'<ellipse cx="{n(x - r * .25)}" cy="{n(y - r * .55)}" rx="{n(r * .45)}" ry="{n(r * .25)}" fill="#F3CDBF"/>')
    o.append(P(d, fill))
    det = [spot(30, -8, 14, 12, SKIN_L, .55), spot(34, 0, 10, 8, SKIN_DD, .22),
           spot(-60, 34, 44, 18, SKIN_L, .45), spot(30, 40, 30, 16, SKIN_L, .35), spot(-40, 0, 26, 14, SKIN_L, .3),
           sline("M-96,60 C-60,52 -10,52 40,58", SKIN_DD, 14, .35),
           line("M-36,6 C-30,12 -26,18 -24,24", CREASE, 1, .3)]
    for x, y, r in [(-75, 20, 5.8), (-85, 21, 6.6), (-96, 23, 7.4)]:
        det.append(line(f"M{x - r + 1},{y + 7} Q{x},{y + 10} {x + r - 1},{y + 7}", CREASE, .9, .35))
    o.append(clipped(d, "".join(det)) + rim(d, SKIN_DD, 7, .4, 2, 3))
    big = curve([(-132, 48), (-128, 34), (-114, 27), (-100, 30), (-95, 42), (-101, 56), (-118, 60), (-129, 56)])
    o.append(P(big, skin_fill(-112, 40, 26, .1)) + clipped(big, spot(-116, 38, 10, 8, SKIN_L, .6)) + rim(big, SKIN_DD, 3, .4, 1.5, 2))
    o.append('<path d="M-128,36 C-126,31 -119,28 -112,29 C-112,35 -116,39 -122,40 C-126,40 -129,39 -128,36Z" fill="#F3CDBF"/>'
             '<path d="M-126,34 C-124,31 -120,30 -116,30" fill="none" stroke="#FFF5EE" stroke-width="1.6" stroke-linecap="round"/>')
    o.append(line("M-96,34 C-92,42 -93,50 -97,57", CREASE, 1.2, .45))
    o.append(fade_piece(cut_piece(FOOT_SIDE, -50, -128), "#ECBE9D", -50, -70, -128, xr=36))
    return "".join(o), (-140, -125, 72, 72)


TOES = [((30, -50), (31, -80), 15, 13), ((8, -58), (7, -86), 9.2, 8), ((-10, -56), (-12, -80), 8.6, 7.4), ((-26, -52), (-30, -72), 8, 6.8),
        ((-40, -46), (-45, -62), 7, 6)]
FOOT_TOP = [(41, 48), (47, -6), (48, -48), (37, -62), (8, -66), (-24, -60), (-45, -50), (-50, -26), (-48, 12), (-42, 52)]


def foot_top(cx, cy, mirror, ang):
    sx = -1 if mirror else 1
    d = cut_outline(FOOT_TOP, 84)
    fill = rg([(0, SKIN_L), (.6, SKIN), (1, SKIN_D)], 0, -20, 130, user=True)
    o = [P(d, fill), clipped(d, spot(0, -10, 34, 50, SKIN_L, .45) + spot(-30, -44, 14, 10, SKIN_DD, .15)), rim(d, SKIN_DD, 7, .35, 2.5 * sx, 3)]
    for (bx, by), (tx_, ty_), w0, w1 in TOES[::-1]:
        f = [(bx, by, w0), ((bx + tx_) / 2, (by + ty_) / 2, (w0 + w1) / 2), (tx_, ty_, w1)]
        td = tube(f)
        o.append(P(td, fill) + clipped(td, spot(tx_ - 2, ty_ + 4, w1 * .7, w1 * .9, SKIN_L, .6)) + rim(td, SKIN_DD, 3, .4, 1.5 * sx, 2.5))
        o.append(nail(f, .78))
        o.append(line(f"M{n(bx - w0 * .6)},{n(by + 2)} Q{n(bx)},{n(by + 5)} {n(bx + w0 * .6)},{n(by + 2)}", CREASE, .9, .35))
    o.append(fade_piece(cut_piece(FOOT_TOP, 62, 128), "#EAB996", 62, 80, 128, xr=30))
    return f'<g transform="translate({n(cx)} {n(cy)}) rotate({n(ang)}) scale({sx} 1)">{"".join(o)}</g>'


def r_toe():
    o = [foot_top(-62, 0, True, -5), foot_top(62, 0, False, 5)]
    o.append(glow_ring(-66, -72, 58, 34, 4, w=9))
    return "".join(o), (-125, -105, 125, 120)


# ---------------------------------------------------------------- side view of the head (ear card)
PROFILE = [(-58, -60), (-66, -30), (-68, -12), (-66, 0), (-70, 10), (-80, 22), (-78, 29), (-70, 31), (-68, 37), (-73, 43), (-69, 48),
           (-72, 54), (-64, 61), (-66, 69), (-56, 79), (-34, 82), (-10, 76), (14, 62), (40, 52), (64, 30), (78, -10), (70, -50),
           (46, -84), (8, -100), (-30, -92)]
HAIR_SIDE = [(-62, -30), (-60, -54), (-48, -80), (-24, -98), (8, -106), (44, -96), (72, -70), (86, -32), (86, 4), (78, 32), (62, 52),
             (48, 48), (44, 24), (42, -6), (34, -22), (20, -28), (8, -22), (0, -6), (-6, -22), (-26, -34), (-46, -36), (-56, -30)]
EAR_SIDE = [(12, -14), (20, -24), (32, -22), (40, -10), (41, 6), (36, 20), (30, 32), (21, 36), (14, 28), (10, 8)]


def r_ear():
    o = []
    neck = "M-30,64 C-30,90 -32,110 -36,130 L42,130 C38,110 34,80 34,48Z"
    o.append(P(neck, lg([(0, SKIN), (1, SKIN_D)], -30, 0, 40, 0, user=True)) + clipped(neck, spot(-6, 76, 40, 16, SKIN_DD, .45)))
    tee = "M-58,124 C-40,114 20,108 70,116 C90,120 98,136 100,150 L-70,150 C-70,140 -66,130 -58,124Z"
    o.append(P(tee, cloth_fill(TEE["mint"], -60, 110, 100, 150)) + line("M-36,122 C-10,116 20,114 40,116", dk(TEE["mint"], .2), 6))
    d = curve(PROFILE)
    o.append(P(d, skin_fill(-20, -10, 120)))
    det = [spot(-40, 30, 22, 16, BLUSH, .4), spot(-50, -40, 22, 16, SKIN_L, .45), spot(30, 30, 30, 26, SKIN_DD, .18),
           sline("M-74,26 C-72,30 -70,32 -66,31", CREASE, 3, .4)]
    o.append(clipped(d, "".join(det)))
    o.append(rim(d, SKIN_DD, 6, .35, 2, 3))
    # eye in profile, brow, nose, mouth
    eyed = "M-63,-3 C-59,-8 -53,-9 -48,-6 C-50,0 -55,3 -60,1Z"
    o.append(clipped(eyed, P(eyed, "#FBF6F2") + f'<ellipse cx="-59" cy="-3" rx="3.6" ry="5.4" fill="{IRIS_D}"/>'
                     + '<circle cx="-60" cy="-5" r="1.3" fill="#FFFFFF"/>'))
    o.append(line("M-64,-3 C-60,-9 -53,-10 -46,-7", "#2A1A12", 2))
    o.append(line("M-63,-6 l-4,-4 M-60,-8 l-3,-5 M-57,-9 l-1,-5", "#2A1A12", 1.1))
    o.append(line("M-60,-12 C-55,-15 -50,-15 -45,-12", CREASE, 1, .35))
    o.append(P(tube([(-66, -22, 1), (-58, -25, 2), (-46, -23, 1.6), (-40, -20, 1)]), "#5E412F", 'fill-opacity=".7"'))
    o.append(line("M-73,29 C-71,27 -69,27 -68,29", "#8E4F40", 1.6, .7))
    o.append(line("M-70,48 C-67,47 -64,48 -62,50", "#93473F", 1.6))
    o.append(P("M-73,43 C-70,41 -68,42 -66,44 C-67,46 -69,48 -70,48 C-71,46 -72,45 -73,43Z", LIP))
    o.append(P("M-71,50 C-69,49 -66,50 -64,51 C-66,55 -69,55 -71,53Z", LIP))
    # ear
    ed = curve(EAR_SIDE)
    o.append(P(ed, rg([(0, "#F6CDB0"), (.6, SKIN), (1, "#D49478")], .45, .45, .6)))
    ear_d = [P("M24,-12 C34,-12 36,4 32,14 C30,20 26,24 22,22 C26,14 28,6 26,0 C24,-4 20,-6 18,-6Z", SKIN_D, 'fill-opacity=".55"'),
             spot(26, 6, 9, 12, SKIN_DD, .55),
             line("M16,-14 C24,-20 34,-18 38,-8", SKIN_L, 2.4, .7),
             line("M18,-4 C22,-10 30,-10 32,-2 C34,6 30,14 26,18", CREASE, 1.3, .45),
             spot(20, 30, 6, 4, BLUSH, .4), spot(16, 6, 4, 6, SKIN_L, .5)]
    o.append(clipped(ed, "".join(ear_d)))
    o.append(rim(ed, SKIN_DD, 3.5, .45, -1, 2))
    hd = curve(HAIR_SIDE)
    rng = random.Random(9)
    o.append(clipped(hd, P(hd, rg([(0, HAIR_L), (.5, HAIR), (1, HAIR_D)], -10, -70, 170, user=True))
                     + strands(rng, edge_pts(HAIR_SIDE[:2] + HAIR_SIDE[9:], 3), (10, -100), 70, spread=26, bow=10)
                     + sline("M-40,-84 C-10,-102 40,-98 70,-70", HAIR_SHINE, 16, .4)) + rim(hd, HAIR_D, 6, .5))
    o.append(glow_ring(25, 6, 38, 46, w=8))
    return "".join(o), (-100, -112, 100, 140)


# ================================================================ realistic cards
REAL = {
    "head": lambda: (body_front("down", "blue") + glow_ring(0, -10, 104, 108, w=10), (-122, -130, 122, 212)),
    "face": lambda: (head_front("boy") + glow_ring(0, 2, 86, 92, w=8), (-98, -110, 98, 104)),
    "nose": lambda: (head_front("girl") + glow_ring(0, 25, 22, 20, w=6), (-98, -110, 98, 104)),
    "mouth": lambda: (head_front("boy") + glow_ring(0, 49, 31, 19, w=6), (-98, -110, 98, 104)),
    "tongue": lambda: (head_front("girl", "tongue", happy=.3, raise_=3) + glow_ring(0, 62, 22, 26, w=6), (-98, -110, 98, 104)),
    "hair": lambda: (body_front("down", "coral", "girl")
                     + glow_path(curve([(x * 1.07, y * 1.04 + 2) for x, y in GIRL_OUT[:-3]] + [(76, 82), (0, 100), (-76, 82)]), 9), (-122, -130, 122, 212)),
    "neck": lambda: (body_front("down", "mint", neck_up=10) + glow_ring(0, 80, 38, 22, w=7), (-122, -130, 122, 212)),
    "shoulder": lambda: (body_front("down", "coral", "girl", ring=glow_ring(-80, 116, 30, 26, -20, w=7) + glow_ring(80, 116, 30, 26, 20, w=7)), (-130, -125, 130, 248)),
    "elbow": lambda: (body_front("wave", "blue", ring=glow_ring(-126, 200, 30, 30, w=7)), (-165, -115, 135, 330)),
    "belly": lambda: (body_front("belly", "sun", "girl", ring=glow_ring(0, 236, 74, 52, w=8), ring_under_arms=True), (-150, -115, 150, 420)),
    "back": lambda: (body_back("coral", glow_ring(0, 186, 66, 70, w=9)), (-160, -115, 160, 420)),
    "leg": lambda: (body_front("down", "mint", ring=glow_ring(-37, 466, 50, 144, w=12)), (-200, -112, 200, 632)),
    "knee": lambda: (body_front("belly", "lilac", "girl", ring=glow_ring(-36, 466, 31, 31, w=7)), (-115, 340, 115, 628)),
    "eye": r_eye, "teeth": r_teeth, "hand": r_hand, "finger": r_finger, "foot": r_foot, "toe": r_toe, "ear": r_ear,
}


# ================================================================ cartoon: a cute simple child, flat colours
CSKIN, CSKIN_D, CCHEEK, CHAIR, CINK = "#FFCBA4", "#F4A57E", "#FF9C9C", "#5A3825", "#3A2A24"
CTEE = {"blue": "#3E9BF0", "coral": "#FF6F61", "mint": "#2EC4A0", "lilac": "#9B7BEA", "sun": "#FFB627"}
CSHORTS = "#2D4A8C"


def c_face(mouth="smile", hair="boy", ears=True, ear_big=False):
    o = []
    if hair == "girl":
        for s in (-1, 1):
            o.append(f'<ellipse cx="{s * 96}" cy="-6" rx="26" ry="34" fill="{CHAIR}" transform="rotate({s * -20} {s * 96} -6)"/>')
            o.append(f'<circle cx="{s * 78}" cy="-26" r="9" fill="#FF6FA5"/>')
    er = 22 if ear_big else 17
    if ears:
        for s in (-1, 1):
            o.append(f'<circle cx="{s * 80}" cy="10" r="{er}" fill="{CSKIN}"/><circle cx="{s * 82}" cy="10" r="{er * .52:.1f}" fill="{CSKIN_D}"/>')
    o.append(f'<circle cx="0" cy="0" r="80" fill="{CSKIN}"/>')
    if hair == "girl":
        o.append(f'<path d="M-82,10 C-86,-56 -46,-90 0,-90 C46,-90 86,-56 82,10 C76,-6 70,-20 60,-30 C40,-34 20,-40 4,-48 C-14,-36 -40,-30 -60,-30 C-70,-20 -78,-8 -82,10Z" fill="{CHAIR}"/>')
    else:
        o.append(f'<path d="M-80,4 C-84,-56 -44,-88 0,-88 C44,-88 84,-56 80,4 C76,-14 70,-26 62,-32 C52,-22 34,-24 26,-38 C14,-24 -12,-24 -20,-40 C-30,-26 -50,-24 -62,-32 C-70,-24 -76,-12 -80,4Z" fill="{CHAIR}"/>')
    for s in (-1, 1):
        o.append(f'<circle cx="{s * 30}" cy="10" r="8.5" fill="{CINK}"/><circle cx="{s * 30 - 2.6}" cy="7" r="2.8" fill="#FFFFFF"/>')
        o.append(f'<circle cx="{s * 50}" cy="32" r="12" fill="{CCHEEK}" fill-opacity=".8"/>')
    o.append(f'<ellipse cx="0" cy="25" rx="6.5" ry="4.5" fill="{CSKIN_D}"/>')
    if mouth == "smile":
        o.append(line("M-17,42 Q0,58 17,42", "#8B3A3A", 6))
    elif mouth == "tongue":
        o.append(f'<path d="M-14,42 Q0,50 14,42 Q0,56 -14,42Z" fill="#8B3A3A"/>')
        o.append(f'<path d="M-10,45 L10,45 L10,58 A10,10 0 0 1 -10,58Z" fill="#FF6B81"/><rect x="-1.2" y="47" width="2.4" height="10" rx="1.2" fill="#E84A66"/>')
    return "".join(o)


C_TORSO = "M-34,86 L34,86 C60,88 78,96 84,112 L78,206 C78,212 73,216 67,216 L-67,216 C-73,216 -78,212 -78,206 L-84,112 C-78,96 -60,88 -34,86Z"
C_SLEEVE_CLIP = "M-30,82 L-84,106 L-210,176 L-210,420 L210,420 L210,176 L84,106 L30,82Z"
C_ARMS = {"down": [(-86, 118), (-100, 184), (-104, 230)], "belly": [(-86, 118), (-106, 176), (-58, 194)],
          "wave": [(-86, 118), (-130, 166), (-138, 96)]}


def c_body(pose="down", tee="blue", hair="boy", mouth="smile", ring="", ring_under_arms=False, back=False, neck_up=0, arms=True):
    c = CTEE[tee]
    o = []
    for s in (-1, 1):
        o.append(f'<rect x="{-50 if s < 0 else 14}" y="200" width="36" height="128" rx="18" fill="{CSKIN}"/>')
        o.append(f'<ellipse cx="{s * 34}" cy="330" rx="24" ry="14" fill="{CSKIN if not back else CSKIN_D}"/>')
    o.append(f'<path d="M-76,200 L76,200 L82,262 C82,266 79,268 75,268 L12,268 L0,246 L-12,268 L-75,268 C-79,268 -82,266 -82,262Z" fill="{CSHORTS}"/>')
    o.append(f'<rect x="-18" y="{60 - neck_up}" width="36" height="{40 + neck_up}" rx="10" fill="{CSKIN_D}"/>')
    o.append(f'<path d="{C_TORSO}" fill="{c}"/>')
    o.append(f'<path d="M-26,86 Q0,{96 if back else 110} 26,86Z" fill="{CSKIN_D}"/>')
    if ring_under_arms:
        o.append(ring)
    sleeves = []
    for s in ((-1, 1) if arms else ()):
        pose_s = pose if (s < 0 or pose == "belly") else "down"
        pts = [(x * (-s if s > 0 else 1), y) for x, y in C_ARMS[pose_s]]
        o.append(line(f"M{pts[0][0]},{pts[0][1]} L{pts[1][0]},{pts[1][1]} L{pts[2][0]},{pts[2][1]}", CSKIN, 26))
        hx, hy = pts[2]
        if pose_s == "wave":
            o.append(c_hand_mini(hx, hy - 10))
        else:
            o.append(f'<circle cx="{hx}" cy="{hy + (4 if pose_s == "down" else 0)}" r="17" fill="{CSKIN}"/>')
        (ax, ay), (bx, by) = pts[0], pts[1]
        L = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / L, (by - ay) / L
        sleeves.append(line(f"M{n(ax - ux * 14)},{n(ay - uy * 14)} L{n(ax + ux * 26)},{n(ay + uy * 26)}", c, 42))
    o.append(clipped(C_SLEEVE_CLIP, "".join(sleeves)))
    face = c_face(mouth, hair) if not back else c_back_head()
    o.append(f'<g transform="translate(0 {-neck_up})">{face}</g>')
    if not ring_under_arms:
        o.append(ring)
    return "".join(o)


def c_hand_mini(x, y):
    o = [f'<circle cx="{x}" cy="{y}" r="18" fill="{CSKIN}"/>']
    for dx, dy, ang in [(-12, -16, -18), (-4, -20, -6), (5, -20, 6), (13, -16, 18)]:
        o.append(f'<rect x="{x + dx - 5}" y="{y + dy - 12}" width="10" height="22" rx="5" fill="{CSKIN}" transform="rotate({ang} {x + dx} {y + dy})"/>')
    o.append(f'<rect x="{x + 14}" y="{y - 4}" width="20" height="10" rx="5" fill="{CSKIN}" transform="rotate(-30 {x + 16} {y})"/>')
    return "".join(o)


def c_back_head():
    o = []
    for s in (-1, 1):
        o.append(f'<circle cx="{s * 80}" cy="10" r="17" fill="{CSKIN}"/>')
    o.append(f'<circle cx="0" cy="0" r="80" fill="{CSKIN}"/>')
    o.append(f'<path d="M-80,10 C-84,-56 -44,-88 0,-88 C44,-88 84,-56 80,10 C78,34 66,54 52,60 C30,54 -30,54 -52,60 C-66,54 -78,34 -80,10Z" fill="{CHAIR}"/>')
    o.append(f'<path d="M4,-40 C20,-40 22,-22 8,-22" fill="none" stroke="#7A5038" stroke-width="5" stroke-linecap="round"/>')
    return "".join(o)


C_NAIL = "#FFE6D8"


def c_finger(x, y, ang, ln, w):
    tf = f' transform="rotate({ang} {x} {y})"'
    return (f'<rect x="{x - w}" y="{y - ln}" width="{2 * w}" height="{ln + w}" rx="{w}" fill="{CSKIN}"{tf}/>'
            f'<rect x="{n(x - w * .6)}" y="{n(y - ln + w * .35)}" width="{n(w * 1.2)}" height="{n(w * 1.2)}" rx="{n(w * .6)}" fill="{C_NAIL}"{tf}/>')


def c_hand(fold=False):
    """Cartoon left hand (back), fingers up, coming out of a blue sleeve cuff."""
    o = [f'<rect x="-30" y="70" width="60" height="40" fill="{CSKIN}"/>']
    fingers = [(-33, 6, -12, 50, 11), (-12, 0, -4, 64, 12), (9, 0, 4, 68, 12), (30, 6, 12, 60, 11.5)]
    for i, (x, y, a, ln, w) in enumerate(fingers):
        if fold and i < 3:
            o.append(f'<rect x="{x - 11}" y="-14" width="22" height="40" rx="11" fill="{CSKIN}"/>')
        else:
            o.append(c_finger(x, y, a, ln, w))
    o.append(f'<rect x="-48" y="-6" width="96" height="96" rx="36" fill="{CSKIN}"/>')
    if fold:
        o.append(c_finger(40, 64, -14, 52, 12))
    else:
        o.append(c_finger(38, 62, 40, 54, 12))
    o.append(f'<rect x="-38" y="96" width="76" height="34" rx="8" fill="{CTEE["blue"]}"/><rect x="-38" y="96" width="76" height="9" rx="4" fill="#7CC0FA"/>')
    return "".join(o)


def c_foot():
    c = CSKIN
    o = []
    for x, y, r in [(-60, 12, 8), (-73, 13, 9), (-87, 15, 10)]:
        o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/><circle cx="{x - 2}" cy="{y - 3}" r="{r * .42:.1f}" fill="{C_NAIL}"/>')
    o.append(f'<path d="M-110,60 C-124,60 -126,30 -104,24 C-80,18 -54,10 -34,-8 C-22,-20 -16,-36 -14,-64 L44,-64 C42,-40 46,-16 58,6 '
             f'C70,28 66,60 40,60Z" fill="{c}"/>')
    o.append(f'<circle cx="-108" cy="40" r="20" fill="{c}"/><path d="M-124,32 C-122,24 -114,20 -106,22 C-106,30 -112,36 -120,36Z" fill="{C_NAIL}"/>')
    o.append(f'<circle cx="28" cy="-8" r="8" fill="{CSKIN_D}"/>')
    o.append(f'<rect x="-22" y="-104" width="74" height="44" rx="8" fill="#3E6FB8"/><rect x="-22" y="-74" width="74" height="12" rx="6" fill="#5A8BD4"/>')
    return "".join(o)


def c_foot_top(cx, cy, mirror, ang):
    sx = -1 if mirror else 1
    o = [f'<path d="M-46,-30 C-48,-58 44,-66 48,-36 C52,0 46,50 30,82 C20,100 -24,100 -34,80 C-46,50 -44,0 -46,-30Z" fill="{CSKIN}"/>']
    for (bx, by), (tx_, ty_), w0, w1 in TOES:
        r = w0 * 1.08
        o.append(f'<circle cx="{tx_}" cy="{n(ty_ + 3)}" r="{n(r)}" fill="{CSKIN}"/>')
        o.append(f'<rect x="{n(tx_ - r)}" y="{n(ty_ + 3)}" width="{n(2 * r)}" height="{n(by - ty_)}" fill="{CSKIN}"/>')
        o.append(f'<circle cx="{tx_}" cy="{n(ty_)}" r="{n(r * .5)}" fill="{C_NAIL}"/>')
    return f'<g transform="translate({n(cx)} {n(cy)}) rotate({n(ang)}) scale({sx} 1)">{"".join(o)}</g>'


def c_side_head():
    o = [f'<rect x="-28" y="60" width="56" height="70" rx="12" fill="{CSKIN_D}"/>',
         f'<path d="M-62,124 C-40,110 40,108 72,120 C90,128 96,140 96,150 L-70,150 C-70,138 -68,130 -62,124Z" fill="{CTEE["mint"]}"/>',
         f'<circle cx="0" cy="0" r="80" fill="{CSKIN}"/>',
         f'<ellipse cx="-80" cy="20" rx="12" ry="9" fill="{CSKIN}"/>',
         f'<path d="M-62,-36 C-60,-80 -20,-96 10,-96 C56,-96 86,-62 84,-10 C82,20 72,44 56,56 C46,40 46,10 40,-10 C30,-30 10,-30 0,-20 C-10,-34 -40,-40 -62,-36Z" fill="{CHAIR}"/>',
         f'<circle cx="-44" cy="6" r="8" fill="{CINK}"/><circle cx="-46.5" cy="3" r="2.6" fill="#FFFFFF"/>',
         f'<circle cx="-34" cy="32" r="12" fill="{CCHEEK}" fill-opacity=".8"/>',
         line("M-74,44 Q-64,50 -56,44", "#8B3A3A", 5),
         f'<ellipse cx="20" cy="6" rx="24" ry="30" fill="{CSKIN}"/><ellipse cx="22" cy="6" rx="13" ry="18" fill="{CSKIN_D}"/>']
    return "".join(o)


def c_eye():
    o = [f'<circle cx="0" cy="0" r="180" fill="{CSKIN}"/>',
         f'<path d="M-110,-92 Q-20,-140 90,-96" fill="none" stroke="{CHAIR}" stroke-width="20" stroke-linecap="round"/>',
         '<path d="M-118,6 C-80,-74 80,-80 118,0 C80,62 -80,64 -118,6Z" fill="#FFFFFF"/>',
         f'<circle cx="0" cy="-2" r="52" fill="#6B3E26"/><circle cx="0" cy="-2" r="28" fill="{CINK}"/>',
         '<circle cx="-18" cy="-20" r="13" fill="#FFFFFF"/><circle cx="16" cy="16" r="6" fill="#FFFFFF"/>',
         f'<path d="M-118,6 C-80,-74 80,-80 118,0" fill="none" stroke="{CINK}" stroke-width="10" stroke-linecap="round"/>']
    for x1, y1, x2, y2 in [(52, -54, 66, -84), (84, -38, 106, -62), (106, -18, 132, -32)]:
        o.append(line(f"M{x1},{y1} L{x2},{y2}", CINK, 9))
    o.append(f'<circle cx="-70" cy="84" r="28" fill="{CCHEEK}" fill-opacity=".6"/>')
    return "".join(o)


def c_teeth():
    o = [f'<circle cx="0" cy="0" r="180" fill="{CSKIN}"/>',
         f'<circle cx="-120" cy="-40" r="34" fill="{CCHEEK}" fill-opacity=".75"/><circle cx="120" cy="-40" r="34" fill="{CCHEEK}" fill-opacity=".75"/>',
         '<path d="M-110,-30 Q0,-14 110,-30 Q100,110 0,112 Q-100,110 -110,-30Z" fill="#9B2F3A"/>',
         '<ellipse cx="0" cy="84" rx="62" ry="28" fill="#FF6B81"/>']
    for x, w, h in [(-74, 26, 30), (-44, 28, 36), (-14, 28, 40), (14, 28, 40), (44, 28, 36), (74, 26, 30)]:
        o.append(f'<rect x="{x - w / 2}" y="-28" width="{w}" height="{h}" rx="9" fill="#FFFFFF"/>')
    return "".join(o)


CARTOON = {
    "head": lambda: (c_body("down", "blue") + flat_ring(0, -6, 106, 106, w=9), (-125, -125, 125, 225)),
    "face": lambda: (c_face() + flat_ring(0, 4, 90, 92, w=8), (-108, -108, 108, 108)),
    "nose": lambda: (c_face(hair="girl") + flat_ring(0, 25, 20, 18, w=6), (-125, -108, 125, 108)),
    "mouth": lambda: (c_face() + flat_ring(0, 48, 30, 18, w=6), (-108, -108, 108, 108)),
    "tongue": lambda: (c_face("tongue", "girl") + flat_ring(0, 52, 22, 20, w=6), (-125, -108, 125, 108)),
    "eye": lambda: (c_eye() + flat_ring(0, 0, 138, 96, w=12), (-185, -185, 185, 185)),
    "teeth": lambda: (c_teeth() + flat_ring(0, 34, 128, 92, w=12), (-185, -185, 185, 185)),
    "ear": lambda: (c_side_head() + flat_ring(21, 6, 36, 42, w=8), (-100, -110, 100, 150)),
    "hair": lambda: (c_body("down", "coral", "girl") + glow_c_hair(), (-130, -125, 130, 225)),
    "neck": lambda: (c_body("down", "mint", neck_up=12) + flat_ring(0, 80, 34, 20, w=7), (-125, -125, 125, 225)),
    "shoulder": lambda: (c_body("down", "coral", "girl", ring=flat_ring(-84, 106, 28, 26, -20, w=7) + flat_ring(84, 106, 28, 26, 20, w=7)), (-130, -125, 130, 240)),
    "elbow": lambda: (c_body("wave", "blue", ring=flat_ring(-131, 168, 28, 28, w=7)), (-170, -110, 130, 345)),
    "belly": lambda: (c_body("belly", "sun", "girl", ring=flat_ring(0, 176, 66, 40, w=8), ring_under_arms=True), (-170, -110, 170, 345)),
    "back": lambda: (c_body("down", "coral", back=True, ring=flat_ring(0, 150, 56, 52, w=8)), (-170, -110, 170, 345)),
    "leg": lambda: (c_body("down", "mint", ring=flat_ring(-32, 282, 38, 72, w=9)), (-180, -110, 180, 350)),
    "knee": lambda: (c_body("down", "lilac", "girl", ring=flat_ring(-32, 290, 25, 25, w=7), arms=False), (-90, 192, 90, 350)),
    "hand": lambda: (flat_disc(0, 22, 128, 128) + c_hand(), (-130, -108, 130, 150)),
    "finger": lambda: (c_hand(fold=True) + flat_ring(36, -34, 25, 50, 12, w=8), (-100, -100, 100, 132)),
    "foot": lambda: (flat_disc(-36, -16, 112, 104) + c_foot(), (-148, -120, 76, 88)),
    "toe": lambda: (c_foot_top(-62, 0, True, -5) + c_foot_top(62, 0, False, 5) + flat_ring(-66, -66, 56, 30, 4, w=7), (-125, -105, 125, 105)),
}


def glow_c_hair():
    return ('<path d="M-92,12 C-96,-64 -50,-102 0,-102 C50,-102 96,-64 92,12" fill="none" stroke="#FFF2A8" stroke-width="20" stroke-opacity=".75" stroke-linecap="round"/>'
            f'<path d="M-92,12 C-96,-64 -50,-102 0,-102 C50,-102 96,-64 92,12" fill="none" stroke="#FFD84A" stroke-width="9" stroke-linecap="round"/>')


def main(only=None):
    for table, cartoon in ((REAL, False), (CARTOON, True)):
        for cid, fn in table.items():
            if only and cid not in only:
                continue
            begin()
            body, box = fn()
            write(DECK, cid, body, box, cartoon=cartoon)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)

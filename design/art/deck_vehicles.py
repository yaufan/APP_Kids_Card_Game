"""交通工具 deck (20 cards): realistic <id>.svg and cartoon <id>_cartoon.svg.

    python3 deck_vehicles.py            # all cards
    python3 deck_vehicles.py bus taxi   # only these

Vehicles are seen from the side, front to the right, light from the top left.
Taiwan versions: a city bus, a yellow taxi, a step-through scooter, a generic metro and a
generic high-speed train, a yellow garbage truck, a white ambulance with a red cross and a
blue-and-white police car. No real company's logo, livery or lettering.
"""
import math
import random
import sys

from kit_vh import (C, D, E, L, P, R, band, blob, chrome, cheek, clip, dk, ell, eye, f1, glass, glow, ground, inside,
                    lg, lt, mix, poly, rg, rrect, shade, smile, specks, spline, tyre, wheel_flat, write_deck)


# ================================================================ realistic helpers
def paint(d, box, base, light=.35, dark=.45, ends=.28, tex=.08, seed=1, extra=""):
    """A painted metal panel: colour from light (top) to dark (bottom), darker ends, a little texture."""
    x0, y0, x1, y1 = box
    fill = lg([(0, lt(base, light)), (.3, base), (.7, dk(base, .12)), (1, dk(base, dark))], 0, y0, 0, y1, user=True)
    inner = [P(d, fill), extra, shade(box, "#000000", left=ends, right=ends, w=.12)]
    if tex:
        inner.append(specks(box, tex, seed))
    return inside(d, *inner)


def gloss(x0, x1, y, h, op=.45, color="#FFFFFF"):
    """Soft horizontal shine stripe (the light on a car's shoulder)."""
    return R(x0, y - h / 2, x1 - x0, h, lg(band(0, 0, 0, 1, color, op)))


def lamp(cx, cy, rx, ry, color, rot=0):
    """A small light (head-, tail- or warning light) with a bright middle."""
    t = f'transform="rotate({rot} {f1(cx)} {f1(cy)})"' if rot else ""
    return E(cx, cy, rx, ry, rg([(0, "#FFFFFF"), (.35, lt(color, .4)), (1, color)], cx=.4, cy=.4), t)


def rails(x0, x1, y, sleepers=True):
    o = []
    if sleepers:
        o.append("".join(R(x, y + 2, 14, 7, "#6B5A4A", 2) for x in range(int(x0), int(x1), 26)))
    o.append(R(x0, y - 3, x1 - x0, 6, lg([(0, "#D6DADF"), (.5, "#8C939B"), (1, "#5A6068")]), 2))
    return "".join(o)


def sedan_path(rear=-130, front=131, wr=-78, wf=80):
    return (f"M{rear},24 L{rear - 1},0 C{rear - 1},-10 {rear + 2},-16 {rear + 10},-18 L-88,-22 C-72,-46 -54,-58 -30,-60 "
            f"L24,-60 C42,-60 56,-52 76,-30 L{front - 20},-24 C{front - 8},-22 {front - 1},-14 {front},-4 L{front + 1},20 "
            f"C{front + 1},27 {front - 3},30 {front - 9},30 L{wf + 29},30 A29,29 0 0 0 {wf - 29},30 L{wr + 29},30 "
            f"A29,29 0 0 0 {wr - 29},30 L{rear + 6},30 C{rear + 2},30 {rear},28 {rear},24Z")


def sedan(base, roof="", lower=None, stripe=None, seed=3):
    """A four-door saloon (taxi, police car)."""
    body = sedan_path()
    box = (-132, -62, 133, 31)
    o = [ground(0, 60, 140, 9, .3)]
    extra = []
    if lower:
        extra.append(P("M-140,-6 C-40,-8 40,-9 140,-10 L140,40 L-140,40Z", lg([(0, lt(lower, .25)), (.5, lower), (1, dk(lower, .4))], 0, -10, 0, 31, user=True)))
    if stripe:
        extra.append(P("M-140,-10 C-40,-12 40,-13 140,-14 L140,-6 C40,-5 -40,-4 -140,-2Z", stripe))
    extra.append(gloss(-130, 130, -19, 9, .5))
    extra.append(R(-140, 8, 280, 24, lg([(0, "#000000", 0), (1, "#000000", .3)])))
    extra.append(L("M-126,-15 C-40,-18 40,-20 118,-22", dk(base, .35), 1.2, 'opacity=".55"'))
    extra.append(L("M-36,-60 L-38,28 M28,-58 C31,-30 35,-4 38,24", dk(base, .45), 1.3, 'opacity=".7"'))
    extra.append(L("M-87,-21 L-87,26", dk(base, .45), 1.1, 'opacity=".5"'))
    o.append(paint(body, box, base, extra="".join(extra), seed=seed))
    o.append(arch(-78, 30, 29) + arch(80, 30, 29))
    o.append(P("M-136,20 C-60,22 60,22 140,19 L140,33 L-136,33Z", "#24262B"))
    o.append(P("M-134,20 C-60,22 60,22 138,19", "none", 'stroke="#55585F" stroke-width="1.2"'))
    gl = "M-80,-24 C-66,-45 -50,-53 -28,-54 L24,-54 C38,-54 50,-46 66,-30 Z"
    o.append(glass(gl, (-80, -54, 66, -24)))
    o.append(inside(gl, R(-4, -56, 8, 34, "#1E2126")))
    o.append(L("M-80,-24 C-66,-45 -50,-53 -28,-54 L24,-54 C38,-54 50,-46 66,-30", "#1A1C20", 2, 'opacity=".5"'))
    o.append(P("M62,-32 C62,-40 68,-42 76,-41 L78,-32Z", lg([(0, lt(base, .1)), (1, dk(base, .45))])) + L("M64,-32 L78,-32", "#1B1D20", 2))
    o.append(R(-20, -19, 13, 4, chrome(), 2) + R(-76, -19, 12, 4, chrome(), 2))
    o.append(P("M112,-25 C121,-23 127,-18 129,-11 L114,-12 C110,-15 109,-21 112,-25Z", lg([(0, "#FFFFFF"), (.5, "#DDE6EC"), (1, "#97A6B1")], 0, 0, 1, 1)))
    o.append(P("M-131,-14 C-130,-17 -127,-18.5 -122,-19 L-121,-7 L-131.5,-6Z", lg([(0, "#FF7A5A"), (.5, "#D0221E"), (1, "#7E0A10")])))
    o.append(R(128, -2, 5, 3, "#FFB23A", 1.5))
    o.append(tyre(-78, 30, 25) + tyre(80, 30, 25))
    o.append(roof)
    return "".join(o)


def arch(cx, cy, r, color="#15161A"):
    return P(f"M{f1(cx - r)},{f1(cy + 2)} A{f1(r)},{f1(r)} 0 0 1 {f1(cx + r)},{f1(cy + 2)}Z", color)


# ================================================================ realistic vehicles
def car():
    """A small red hatchback (the approved mockup car, shaded with gradients only)."""
    body = ("M-118,26 L-120,4 C-121,-10 -117,-20 -108,-25 L-94,-30 C-80,-54 -66,-64 -40,-67 L18,-67 "
            "C38,-67 52,-60 70,-38 L100,-31 C113,-28 120,-20 121,-6 L122,20 C122,27 118,30 112,30 L101,30 "
            "A29,29 0 0 0 43,30 L-41,30 A29,29 0 0 0 -99,30 L-110,30 C-115,30 -118,29 -118,26Z")
    gl = "M-86,-31 C-74,-51 -62,-59 -40,-60 L16,-60 C32,-60 44,-54 60,-35 Z"
    o = [ground(0, 56, 132, 9, .3)]
    extra = [gloss(-118, 120, -21, 10, .45, "#FFB0A6"), gloss(-118, 120, -9, 8, .16),
             R(-124, 2, 248, 30, lg([(0, "#5A0A0E", 0), (1, "#5A0A0E", .45)])),
             L("M-114,-17 C-40,-20 40,-22 108,-24", "#7E1015", 1.2, 'opacity=".6"'),
             L("M-114,-15.5 C-40,-18.5 40,-20.5 108,-22.5", "#FF9A8E", 1, 'opacity=".5"'),
             L("M-38,-60 L-41,28 M28,-58 C30,-30 34,-4 38,22", "#6A0B10", 1.3, 'opacity=".7"'),
             L("M-36,-60 L-39,28 M30,-58 C32,-30 36,-4 40,22", "#FF8A7E", .8, 'opacity=".35"')]
    o.append(paint(body, (-121, -68, 123, 31), "#D42420", .3, .55, extra="".join(extra), seed=2))
    o.append(arch(-70, 30, 29) + arch(72, 30, 29))
    o.append(P("M-124,20 C-60,22 60,22 126,19 L126,34 L-124,34Z", "#2B2D31") + L("M-124,20 C-60,22 60,22 126,19", "#5A5D63", 1.2))
    o.append(R(108, 2, 16, 6, "#2B2D31", 3))
    o.append(glass(gl, (-86, -60, 60, -31)))
    o.append(inside(gl, R(-41, -64, 8, 36, "#1A1E23")))
    o.append(L("M-86,-31 C-74,-51 -62,-59 -40,-60 L16,-60 C32,-60 44,-54 60,-35", "#2A0406", 2.2, 'opacity=".55"'))
    o.append(P("M58,-38 C58,-46 64,-48 72,-47 L74,-38Z", lg([(0, "#E23A33"), (1, "#8A1015")])) + L("M60,-38 L74,-38", "#1B1D20", 2))
    o.append(R(-20, -20, 14, 4, chrome(), 2) + R(-82, -21, 13, 4, chrome(), 2))
    o.append(P("M104,-28 C112,-26 117,-21 119,-13 L106,-15 C102,-18 101,-24 104,-28Z", lg([(0, "#FFFFFF"), (.5, "#DDE6EC"), (1, "#9AA8B2")], 0, 0, 1, 1)))
    o.append(L("M106,-24 C110,-23 113,-20 115,-16", "#FFFFFF", 1.4, 'opacity=".9"'))
    o.append(P("M-119,-17 C-117,-22 -113,-24.5 -109,-25.5 L-107,-12 L-119.5,-10Z", lg([(0, "#FF7A5A"), (.5, "#D0221E"), (1, "#7E0A10")])))
    o.append(R(116, -3, 6, 3, "#FFB23A", 1.5))
    o.append(tyre(-70, 30, 25) + tyre(72, 30, 25))
    return "".join(o)


def taxi_sign():
    """The lit roof sign with T-A-X-I drawn as strokes (a generic word, no company)."""
    o = [P("M-30,-60 L-27,-66 L27,-66 L30,-60Z", "#2A2C30"),
         P(rrect(-30, -86, 60, 21, 5), lg([(0, "#FFFFFF"), (.6, "#F1EEE6"), (1, "#C9C3B4")])),
         R(-30, -86, 60, 21, lg(band(0, 0, 1, 0, "#000000", .12, .5, .5)), 5, 'opacity=".0"')]
    s = 2.6
    letters = ("M-21,-81 L-13,-81 M-17,-81 L-17,-70 "            # T
               "M-11,-70 L-7,-81 L-3,-70 M-9.5,-74 L-4.5,-74 "     # A
               "M0,-81 L7,-70 M7,-81 L0,-70 "                      # X
               "M12,-81 L18,-81 M15,-81 L15,-70 M12,-70 L18,-70")  # I
    o.append(L(letters, "#1F2226", s, cap="round"))
    return "".join(o)


def taxi():
    return sedan("#F6C21C", roof=taxi_sign(), seed=4)


def police_car():
    bar = (P("M-34,-60 L-30,-65 L30,-65 L34,-60Z", "#2A2C30")
           + P(rrect(-38, -76, 38, 12, 4), lg([(0, "#FF8A8A"), (.5, "#E21B23"), (1, "#8C0A10")]))
           + P(rrect(0, -76, 38, 12, 4), lg([(0, "#8AB8FF"), (.5, "#1B5BD6"), (1, "#0A2C78")]))
           + E(-24, -71, 9, 3, "#FFFFFF", 'opacity=".55"') + E(16, -71, 9, 3, "#FFFFFF", 'opacity=".55"'))
    return sedan("#F4F6F8", roof=bar, lower="#1F4FA8", stripe="#FFFFFF", seed=5)


def bus():
    """A Taiwanese low-floor city bus: big windows, front and middle doors, an amber LED sign."""
    body = ("M-166,22 L-166,-96 C-166,-104 -161,-108 -153,-108 L146,-108 C156,-108 162,-103 164,-94 "
            "L168,-40 L168,22 C168,27 165,30 160,30 L136,30 A27,27 0 0 0 82,30 L-62,30 A27,27 0 0 0 -116,30 "
            "L-160,30 C-164,30 -166,27 -166,22Z")
    box = (-166, -108, 168, 31)
    base = "#F3F5F6"
    extra = [P("M-170,-8 L172,-8 L172,40 L-170,40Z", lg([(0, "#2E9BD6"), (.6, "#1F7DBA"), (1, "#0E4B78")], 0, -8, 0, 31, user=True)),
             R(-170, -14, 342, 5, "#0E5E96"),
             gloss(-166, 168, -100, 8, .6),
             R(-170, 8, 342, 24, lg([(0, "#000000", 0), (1, "#000000", .3)]))]
    o = [ground(0, 59, 176, 9, .3)]
    o.append(paint(body, box, base, .2, .3, extra="".join(extra), seed=6))
    o.append(R(-150, -116, 120, 10, lg([(0, "#E9ECEE"), (1, "#AEB5BB")]), 4))   # roof air-conditioner
    o.append(arch(-89, 30, 28) + arch(109, 30, 28))
    # window band and pillars
    wb = "M-160,-92 L118,-92 L118,-26 L-160,-26Z"
    o.append(glass(wb, (-160, -92, 118, -26), "#33475A"))
    o.append("".join(R(x, -93, 5, 68, "#D5DADE") for x in (-112, -64, 42, 82)))
    # front windscreen (seen edge-on) and front door
    o.append(glass("M152,-92 L162,-92 L166,-40 L166,-4 L152,-4Z", (152, -92, 166, -4), "#33475A"))
    door = "M124,-94 L150,-94 L150,22 L124,22Z"
    o.append(P(door, "#C9D0D6") + glass("M127,-90 L147,-90 L147,18 L127,18Z", (127, -90, 147, 18), "#3B5163"))
    o.append(L("M137,-90 L137,18", "#AEB6BD", 2.2))
    # middle door
    o.append(P("M-16,-94 L36,-94 L36,22 L-16,22Z", "#C9D0D6") + glass("M-13,-90 L33,-90 L33,18 L-13,18Z", (-13, -90, 33, 18), "#3B5163"))
    o.append(L("M10,-90 L10,18", "#AEB6BD", 2.4) + L("M-10,-40 L-4,-40 M24,-40 L30,-40", "#E6EAED", 2))
    # LED destination sign above the windscreen
    o.append(R(146, -106, 18, 12, "#1A1B1E", 2) + R(148, -104, 14, 8, "#F7A21B", 1))
    o.append(R(60, -106, 52, 12, "#1A1B1E", 2))
    o.append("".join(R(63 + i * 4.4, -104 + (i * 7 % 3) * 2.3, 3.4, 3.4 + (i % 2) * 2.2, "#FFB33A") for i in range(11)))
    # lights, mirror, bumper
    o.append(lamp(165, -10, 3, 6, "#FFF4D0") + lamp(-165, -12, 2.4, 7, "#E0302A"))
    o.append(L("M166,-86 C176,-86 178,-80 177,-66", "#2A2C30", 3) + P(rrect(173, -70, 8, 18, 3), "#2A2C30"))
    o.append(P("M-168,16 L170,16 L170,30 L-168,30Z", "#2A2D33"))
    o.append(tyre(-89, 30, 24, hub="#BFC5CB") + tyre(109, 30, 24, hub="#BFC5CB"))
    return "".join(o)


def scooter():
    """A Taiwanese step-through scooter: small wheels, a flat floor, a broad front body, seat, mirrors."""
    base = "#2F7FC2"
    o = [ground(5, 74, 140, 9, .3)]
    o.append(tyre(-82, 40, 30, rim=.56, hub="#C4CAD0", spokes=6))
    o.append(tyre(98, 40, 30, rim=.56, hub="#C4CAD0", spokes=6))
    # engine / swing arm and muffler
    o.append(P("M-104,28 C-92,16 -40,14 -18,22 L-16,40 C-40,46 -84,48 -104,40Z", lg([(0, "#8D949B"), (1, "#3E4349")])))
    o.append(C(-82, 40, 9, "#2E3237"))
    o.append(P(rrect(-126, 22, 54, 15, 7.5), lg([(0, "#F2F4F6"), (.4, "#B8BFC6"), (.6, "#7F878F"), (1, "#C9CED3")])))
    o.append(P(rrect(-131, 25, 8, 9, 4), "#3A3E43"))
    # front fender
    fend = "M66,12 C72,0 104,-4 126,8 C130,11 130,15 126,15 C112,8 88,8 76,16Z"
    o.append(P(fend, lg([(0, lt(base, .3)), (1, dk(base, .4))])))
    # main body: rear cowl under the seat, floorboard, broad leg shield and front cover
    body = ("M-142,-8 C-146,-24 -136,-38 -112,-40 L-14,-42 C-2,-42 4,-34 2,-22 L0,6 L40,6 "
            "C44,-30 52,-62 60,-86 C62,-94 72,-98 80,-94 C92,-88 106,-66 106,-44 C106,-24 98,-8 88,4 "
            "C80,16 66,24 50,26 L-4,26 C-30,26 -48,20 -58,10 C-80,2 -112,6 -128,6 C-136,6 -140,0 -142,-8Z")
    box = (-146, -98, 106, 26)
    extra = [gloss(-146, 106, -34, 10, .45), R(-150, -2, 260, 30, lg([(0, "#000000", 0), (1, "#000000", .32)])),
             L("M-60,10 C-40,-2 -10,0 0,6", dk(base, .4), 1.4, 'opacity=".6"'),
             L("M40,6 C44,-30 52,-62 60,-86", dk(base, .35), 1.6, 'opacity=".6"'),
             L("M44,4 C48,-30 56,-60 64,-84", lt(base, .5), 2, 'opacity=".45"'),
             glow(84, -60, 16, 30, "#FFFFFF", .3)]
    o.append(paint(body, box, base, .35, .5, extra="".join(extra), seed=7))
    o.append(P("M-2,4 L42,4 L41,12 L-2,12Z", "#3B4046"))
    o.append(L("M90,-4 L98,40", "#9AA2AA", 8) + L("M90,-4 L98,40", "#E3E7EA", 2.6, 'opacity=".7"'))
    # seat
    seat = "M-138,-38 C-134,-54 -100,-58 -60,-57 L-16,-56 C-4,-56 2,-50 0,-42 L-138,-38Z"
    o.append(P(seat, lg([(0, "#55595F"), (.4, "#2C2F34"), (1, "#16181B")])))
    o.append(inside(seat, glow(-70, -58, 50, 5, "#FFFFFF", .25)))
    o.append(lamp(-142, -20, 4, 8, "#E0302A", 15))
    o.append(L("M-128,-42 C-134,-48 -126,-54 -110,-52", "#4A4E54", 5))
    # handlebar cover with headlight, grips, short mirror stalks
    hb = "M58,-108 C62,-118 92,-120 108,-112 C114,-108 112,-98 104,-94 L66,-90 C58,-92 55,-100 58,-108Z"
    o.append(P(hb, lg([(0, lt(base, .35)), (.5, base), (1, dk(base, .45))])))
    o.append(P("M100,-112 C110,-110 113,-102 106,-96 L98,-98 C100,-102 101,-107 100,-112Z", lg([(0, "#FFFFFF"), (1, "#B8C6D0")], 0, 0, 1, 1)))
    o.append(L("M60,-104 L40,-110", "#2A2C30", 8) + L("M58,-105 L44,-109", "#4A4E54", 3))
    o.append(L("M70,-114 L66,-126 M88,-116 L88,-128", "#3A3E43", 2.6))
    o.append(E(62, -131, 11, 7, "#2A2C30", 'transform="rotate(-15 62 -131)"') + E(88, -133, 11, 7, "#2A2C30", 'transform="rotate(10 88 -133)"'))
    o.append(lamp(102, -40, 3, 6, "#FFA11A", 12))
    return "".join(o)


def bicycle():
    """A city bicycle: diamond frame, spoked wheels, chain, saddle, bell."""
    frame = "#17908A"
    wr, wf, wy, R_ = -98, 98, 34, 60
    o = [ground(0, wy + R_ + 4, 165, 8, .25)]
    for cx in (wr, wf):
        o.append(C(cx, wy, R_, "none", 'stroke="#1E2024" stroke-width="9"'))
        o.append(C(cx, wy, R_ - 1, "none", 'stroke="#3A3D42" stroke-width="2" opacity=".7"'))
        o.append(C(cx, wy, R_ - 7, "none", f'stroke="{chrome()}" stroke-width="4"'))
        sp = []
        for i in range(32):
            a = math.radians(i * 360 / 32 + (4 if i % 2 else -4))
            b = math.radians(i * 360 / 32)
            sp.append(f"M{f1(cx + 5 * math.cos(a))},{f1(wy + 5 * math.sin(a))} L{f1(cx + (R_ - 8) * math.cos(b))},{f1(wy + (R_ - 8) * math.sin(b))}")
        o.append(L(" ".join(sp), "#A9B0B7", .9, cap="butt"))
        o.append(C(cx, wy, 6, rg([(0, "#FFFFFF"), (1, "#7E868E")], cx=.4, cy=.35)))
    bb = (-6, 44)
    seat = (-38, -64)
    head_t, head_b = (62, -70), (70, -40)
    o.append(L(f"M{bb[0]},{bb[1]} L{wr},{wy} L{seat[0] + 3},{seat[1] + 10}", dk(frame, .15), 6))     # stays
    o.append(L(f"M{bb[0]},{bb[1]} L{seat[0]},{seat[1]} M{seat[0] + 2},{seat[1] + 6} L{head_t[0]},{head_t[1] + 4} "
               f"M{bb[0]},{bb[1]} L{head_b[0]},{head_b[1]}", frame, 9))
    o.append(L(f"M{bb[0] + 2},{bb[1] - 4} L{seat[0] + 2},{seat[1] + 2} M{seat[0] + 4},{seat[1] + 3} L{head_t[0]},{head_t[1] + 1}",
               lt(frame, .45), 2.4, 'opacity=".8"'))
    o.append(L(f"M{head_t[0]},{head_t[1]} L{head_b[0]},{head_b[1]}", dk(frame, .2), 12))
    o.append(L(f"M{head_b[0]},{head_b[1]} C76,-12 86,10 {wf},{wy}", "#9AA2AA", 6) + L(f"M{head_b[0]},{head_b[1]} C75,-14 85,8 {wf - 1},{wy - 2}", "#E8ECEF", 1.8))
    # chain ring, chain, crank, pedals
    o.append(L(f"M{bb[0]},{bb[1] - 15} L{wr},{wy - 7} M{bb[0]},{bb[1] + 15} L{wr},{wy + 7}", "#4A4E54", 2.6))
    o.append(C(bb[0], bb[1], 16, chrome()) + C(bb[0], bb[1], 11, "#6E767E") + C(bb[0], bb[1], 6, chrome()))
    o.append(C(wr, wy, 8, "#4A4E54"))
    o.append(L(f"M{bb[0]},{bb[1]} L{bb[0] + 14},{bb[1] + 30}", "#5A6168", 6) + R(bb[0] + 4, bb[1] + 28, 22, 6, "#2A2C30", 2))
    o.append(L(f"M{bb[0]},{bb[1]} L{bb[0] - 12},{bb[1] - 30}", "#7E868E", 5) + R(bb[0] - 22, bb[1] - 34, 20, 6, "#3A3D42", 2))
    # seat post and saddle
    o.append(L(f"M{seat[0]},{seat[1]} L{seat[0] - 5},{seat[1] - 16}", "#B9C0C6", 5))
    sad = "M-74,-86 C-68,-92 -40,-90 -20,-84 C-14,-82 -16,-76 -22,-76 C-40,-76 -60,-74 -72,-78 C-77,-80 -77,-84 -74,-86Z"
    o.append(P(sad, lg([(0, "#55595F"), (.5, "#2A2C30"), (1, "#141518")])) + E(-48, -86, 18, 2.5, "#FFFFFF", 'opacity=".25"'))
    # stem and handlebar
    o.append(L(f"M{head_t[0]},{head_t[1]} L58,-92 C50,-96 40,-96 30,-92", "#9AA2AA", 5))
    o.append(L("M36,-93 L18,-90", "#2A2C30", 8))
    o.append(C(52, -100, 6, chrome()) + C(52, -100, 3, "#DDE2E6"))   # bell
    o.append(lamp(76, -64, 5, 6, "#FFF2C8"))
    return "".join(o)


def train():
    """A steam locomotive: boiler, chimney with steam, cab, big red wheels, on rails."""
    o = [ground(0, 64, 175, 8, .25), rails(-175, 175, 60)]
    # steam puffs
    rng = random.Random(4)
    for cx, cy, r, op in ((118, -120, 18, .9), (96, -146, 24, .85), (64, -164, 28, .75), (24, -172, 26, .6)):
        o.append(C(cx, cy, r, rg([(0, "#FFFFFF"), (.7, "#ECEFF2"), (1, "#C9D0D6")], cx=.38, cy=.35)))
        o.append(C(cx + r * .4, cy + r * .4, r * .55, "#B5BEC6", 'opacity=".35"'))
    # cab
    cab = "M-168,-126 L-86,-126 L-86,30 L-168,30Z"
    o.append(paint(cab, (-168, -126, -86, 30), "#1E5A3A", .25, .5, seed=8))
    o.append(P("M-176,-134 L-80,-134 C-78,-134 -78,-124 -80,-124 L-176,-124Z", lg([(0, "#3A3D42"), (1, "#141518")])))
    o.append(P(rrect(-154, -112, 50, 40, 6), lg([(0, "#E7EEF3"), (1, "#9FB1BE")])))
    o.append(P(rrect(-150, -108, 42, 32, 4), lg([(0, "#405565"), (1, "#1E2A34")])))
    o.append(R(-170, -64, 86, 6, "#C9A24A"))
    # boiler
    boil = "M-90,-92 L120,-92 C126,-92 128,-86 128,-66 C128,-46 126,-40 120,-40 L-90,-40Z"
    o.append(P(boil, lg([(0, "#3E8A62"), (.3, "#2A6E4A"), (.7, "#1A4A31"), (1, "#0D2A1B")], 0, -92, 0, -40, user=True)))
    o.append(inside(boil, gloss(-90, 128, -80, 8, .4), shade((-90, -92, 128, -40), right=.3, w=.1), specks((-90, -92, 128, -40), .08, 9)))
    o.append(R(30, -92, 7, 52, "#C9A24A") + R(-40, -92, 7, 52, "#C9A24A"))
    o.append(P("M104,-94 L128,-94 C134,-94 136,-86 136,-66 C136,-46 134,-38 128,-38 L104,-38Z", lg([(0, "#4A4E54"), (.4, "#2A2C30"), (1, "#101113")])))
    o.append(C(132, -66, 9, rg([(0, "#FFFFFF"), (.4, "#FFF0B0"), (1, "#C9A24A")])))
    # chimney and dome
    o.append(P("M106,-94 L108,-120 L102,-130 L130,-130 L124,-120 L126,-94Z", lg([(0, "#2E3136"), (.4, "#4E535A"), (1, "#16181B")], 0, 0, 1, 0)))
    o.append(P("M40,-92 C40,-112 72,-112 72,-92Z", lg([(0, "#E8C66A"), (.5, "#C9A24A"), (1, "#8A6A22")], 0, 0, 1, 0)))
    # running board and frame
    o.append(R(-94, -40, 236, 10, "#1F2124"))
    o.append(R(-170, 18, 330, 10, "#2A1A16"))
    # cow-catcher
    o.append(P("M138,0 L172,46 L128,46 L120,0Z", lg([(0, "#D9302A"), (1, "#7A1210")])))
    o.append(L("M130,6 L138,44 M138,6 L150,44 M146,6 L162,44", "#5A0C0A", 2))
    # cylinder
    o.append(P(rrect(84, -24, 52, 30, 6), lg([(0, "#3E4248"), (1, "#16181B")])))
    # wheels
    for cx, r in ((-128, 30), (-56, 34), (16, 34), (110, 18)):
        cy = 60 - r - 3
        o.append(C(cx, cy, r, rg([(0, "#E8433A"), (.75, "#B91E1A"), (.9, "#7A0E0C"), (1, "#2A2C30")])))
        sp = " ".join(f"M{cx},{cy} L{f1(cx + (r - 5) * math.cos(math.radians(a)))},{f1(cy + (r - 5) * math.sin(math.radians(a)))}" for a in range(0, 360, 30))
        o.append(L(sp, "#8A1410", 2.6))
        o.append(C(cx, cy, r * .28, rg([(0, "#FF7A6A"), (1, "#9A1410")])) + C(cx, cy, r * .1, "#2A2C30"))
        o.append(C(cx, cy, r, "none", 'stroke="#2A2C30" stroke-width="3"'))
    o.append(L("M-128,40 L16,36", chrome([(0, "#E6EAEE"), (1, "#8C949C")]), 6) + C(-128, 40, 4, "#4A4E54") + C(-56, 38, 4, "#4A4E54") + C(16, 36, 4, "#4A4E54"))
    o.append(L("M16,36 L100,-10", "#9AA2AA", 5))
    return "".join(o)


def mrt():
    """A generic metro car: silver body, blue stripe, double doors, big front windscreen."""
    body = ("M-172,-104 L132,-104 C150,-104 160,-98 164,-84 L170,-50 L172,8 C172,14 168,18 162,18 L-172,18Z")
    box = (-172, -104, 172, 18)
    extra = [R(-180, -30, 360, 14, lg([(0, "#3A8FD9"), (1, "#1A5FA8")])), R(-180, -14, 360, 3, "#123F70"),
             gloss(-172, 172, -96, 10, .55), R(-180, -4, 360, 24, lg([(0, "#000000", 0), (1, "#000000", .25)]))]
    o = [ground(0, 56, 178, 7, .25), rails(-176, 176, 50)]
    o.append(paint(body, box, "#D9DEE3", .5, .35, ends=.15, extra="".join(extra), seed=9))
    o.append(L("M-172,-102 L140,-102", "#FFFFFF", 2, 'opacity=".8"'))
    # front windscreen
    o.append(glass("M146,-94 C156,-94 160,-88 162,-80 L167,-42 L148,-42Z", (146, -94, 167, -42), "#2F4352"))
    o.append(R(150, -100, 14, 5, "#1A1B1E", 1.5) + R(151, -99, 12, 3, "#F7A21B", 1))
    o.append(lamp(168, -6, 2.6, 4.5, "#FFF4D0"))
    # windows and doors
    for x in (-160, -80, 10, 92):
        o.append(glass(rrect(x, -86, 34, 40, 4), (x, -86, x + 34, -46), "#33475A"))
    for x in (-118, -32, 52):
        o.append(P("M%d,-92 L%d,14 L%d,14 L%d,-92Z" % (x, x, x + 32, x + 32), lg([(0, "#C2C9CF"), (1, "#8D969E")])))
        o.append(glass(rrect(x + 3, -86, 12, 44, 3), (x + 3, -86, x + 15, -42), "#33475A"))
        o.append(glass(rrect(x + 17, -86, 12, 44, 3), (x + 17, -86, x + 29, -42), "#33475A"))
        o.append(L(f"M{x + 16},-92 L{x + 16},14", "#6E767E", 1.4))
    # under-frame and bogies
    o.append(R(-170, 18, 336, 12, "#2E3237"))
    for cx in (-120, 110):
        o.append(R(cx - 36, 22, 72, 14, "#3E4349", 4))
        for wx in (cx - 22, cx + 22):
            o.append(C(wx, 36, 12, rg([(0, "#6E767E"), (1, "#1A1B1E")])) + C(wx, 36, 4, "#9AA2AA"))
    return "".join(o)


def hsr():
    """A generic high-speed train: a long pointed nose, white body, a blue stripe."""
    body = ("M-176,-82 L20,-82 C60,-82 96,-70 130,-48 C152,-34 170,-18 178,-6 C181,0 178,8 168,10 "
            "L-176,10Z")
    box = (-176, -82, 181, 10)
    extra = [P("M-180,-22 L80,-22 C110,-22 140,-14 172,-2 L176,6 C140,-4 110,-12 80,-12 L-180,-12Z", lg([(0, "#3A8FD9"), (1, "#14508F")])),
             P("M-180,-10 L80,-10 C110,-10 140,-4 176,8 L176,12 L-180,12Z", lg([(0, "#9AA4AD"), (1, "#5E6870")])),
             gloss(-176, 100, -74, 10, .6),
             glow(150, -30, 40, 16, "#FFFFFF", .35, 30)]
    o = [ground(0, 46, 182, 7, .25), rails(-182, 182, 40)]
    o.append(paint(body, box, "#F4F6F8", .4, .28, ends=.12, extra="".join(extra), seed=10))
    # cockpit window on the nose
    cw = "M72,-70 C92,-66 110,-58 124,-48 L112,-44 C98,-52 84,-58 70,-60Z"
    o.append(glass(cw, (70, -70, 124, -44), "#24333F"))
    # passenger windows
    for x in range(-166, 50, 30):
        o.append(glass(rrect(x, -60, 20, 18, 5), (x, -60, x + 20, -42), "#2B3A47", sky=False))
    o.append(P("M-150,-70 L-136,-70 L-136,-14 L-150,-14Z", "#DCE1E5") + L("M-143,-70 L-143,-14", "#B4BCC3", 1.2))
    o.append(lamp(166, -8, 5, 2.4, "#FFF4D0", 25))
    # bogies
    o.append(R(-172, 10, 320, 10, "#3A3F45"))
    for cx in (-128, 92):
        for wx in (cx - 18, cx + 18):
            o.append(C(wx, 26, 10, rg([(0, "#6E767E"), (1, "#1A1B1E")])) + C(wx, 26, 3.5, "#9AA2AA"))
    # gap to the next car
    o.append(R(-182, -76, 4, 82, "#2A2C30"))
    return "".join(o)


def airplane():
    """A passenger jet seen from the side and a little below: wings, engines, tail fin, windows."""
    fus = ("M-150,-22 C-120,-30 60,-30 120,-28 C150,-27 172,-18 178,-6 C180,0 176,8 164,12 "
           "C120,20 -40,22 -110,18 C-130,16 -150,8 -168,-8 C-170,-14 -162,-20 -150,-22Z")
    o = []
    # far wing (behind the body)
    o.append(P("M20,-22 L-50,-76 L-34,-78 L50,-24Z", lg([(0, "#B9C2CA"), (1, "#8C96A0")])))
    o.append(P("M-148,-18 L-178,-34 L-170,-36 L-128,-20Z", "#9AA4AD"))
    # tail fin
    fin = "M-112,-24 L-160,-112 C-162,-118 -150,-120 -146,-114 L-80,-26Z"
    o.append(P(fin, lg([(0, "#3A8FD9"), (1, "#14508F")], 0, 0, 1, 1)))
    o.append(inside(fin, glow(-140, -90, 26, 10, "#FFFFFF", .3, -60)))
    # body
    o.append(P(fus, lg([(0, "#FFFFFF"), (.45, "#EEF1F4"), (.7, "#C9D1D8"), (1, "#8B96A0")], 0, -30, 0, 22, user=True)))
    o.append(inside(fus, gloss(-170, 180, -20, 8, .8), P("M-180,4 C-60,6 60,6 180,2 L180,30 L-180,30Z", "#A9B3BC", 'opacity=".55"'),
                    R(-180, 0, 360, 3, "#2E78C6"), specks((-170, -30, 180, 22), .06, 11), shade((-170, -30, 180, 22), left=.15, right=.12, w=.08)))
    # windows and door
    o.append("".join(E(x, -12, 3.2, 4, "#2B3A47") for x in range(-110, 120, 11)))
    o.append(P(rrect(126, -21, 14, 22, 3), "none", 'stroke="#9AA4AD" stroke-width="1.4"'))
    o.append(P("M148,-18 C156,-18 164,-14 170,-8 L152,-8 C150,-12 149,-15 148,-18Z", "#24333F"))
    o.append(P("M152,-16 L158,-15 L156,-10 L151,-10Z", "#FFFFFF", 'opacity=".3"'))
    # near wing (toward us) and engine
    wing = "M-10,8 L56,6 L74,10 L-30,74 L-58,78 C-62,78 -62,74 -58,70Z"
    o.append(P(wing, lg([(0, "#E4E9ED"), (.6, "#B4BEC7"), (1, "#7E8994")], 0, 0, 0, 1)))
    o.append(P("M-58,70 L-30,74 L-44,90 L-50,88Z", "#2E78C6"))
    o.append(inside(wing, L("M60,8 L-46,76", "#FFFFFF", 3, 'opacity=".6"')))
    eng = rrect(-4, 24, 58, 22, 11)
    o.append(P(eng, lg([(0, "#F4F6F8"), (.5, "#C2CAD1"), (1, "#7E8994")])))
    o.append(E(54, 35, 5, 11, lg([(0, "#5A6168"), (1, "#1E2124")])))
    o.append(E(-4, 35, 4, 8, "#3A3F45"))
    o.append(R(14, 18, 10, 8, "#B4BEC7"))
    # stabiliser near side
    o.append(P("M-140,-6 L-176,12 L-166,14 L-118,-2Z", lg([(0, "#D6DCE1"), (1, "#8C96A0")])))
    return "".join(o)


def helicopter():
    """A rescue-style helicopter: glass cabin, tail boom, rotors, skids."""
    base = "#D8262A"
    o = [ground(10, 92, 120, 7, .2)]
    # skids
    o.append(L("M-36,48 L-30,72 M50,48 L56,72", "#5A6168", 5))
    o.append(L("M-70,74 L96,74 C104,74 108,70 110,64", "#3A3F45", 6))
    # tail boom and fin
    boom = "M-40,-36 L-150,-24 L-150,-14 L-40,4Z"
    o.append(paint(boom, (-150, -36, -40, 4), base, .3, .5, ends=0, seed=12))
    fin = "M-140,-24 L-170,-80 L-156,-82 L-128,-20Z M-150,-14 L-168,8 L-156,8 L-138,-14Z"
    o.append(P(fin, lg([(0, lt(base, .2)), (1, dk(base, .4))])))
    o.append(C(-160, -30, 22, rg([(0, "#9AA4AD", .15), (.8, "#9AA4AD", .35), (1, "#9AA4AD", .1)])))
    o.append(L("M-160,-52 L-160,-8", "#2A2C30", 3.4) + C(-160, -30, 3.5, "#4A4E54"))
    # cabin
    cab = ("M-50,-52 C-40,-66 30,-70 60,-62 C96,-52 120,-28 124,0 C126,24 106,46 76,48 "
           "L-30,50 C-50,50 -58,36 -58,14 L-58,-30 C-58,-40 -56,-46 -50,-52Z")
    extra = [R(-70, 6, 200, 10, "#FFFFFF", 0, 'opacity=".95"'), gloss(-60, 124, -50, 10, .5),
             R(-70, 24, 200, 30, lg([(0, "#000000", 0), (1, "#000000", .3)]))]
    o.append(paint(cab, (-58, -70, 126, 50), base, .3, .5, extra="".join(extra), seed=13))
    win = "M46,-60 C80,-52 108,-30 118,-4 L66,-4 C60,-24 52,-44 46,-60Z"
    o.append(glass(win, (46, -60, 118, -4), "#2C4252"))
    o.append(glass(rrect(-6, -54, 40, 40, 8), (-6, -54, 34, -14), "#2C4252"))
    o.append(L("M-30,-40 L-30,38", dk(base, .4), 1.4, 'opacity=".6"'))
    o.append(R(-26, -6, 10, 4, chrome(), 2))
    # engine cover and rotor mast
    o.append(P("M-44,-56 C-40,-72 30,-76 44,-62Z", lg([(0, "#9AA4AD"), (1, "#5A6168")])))
    o.append(R(-2, -88, 8, 22, "#3A3F45") + E(2, -88, 14, 5, "#2A2C30"))
    # main rotor blades (thin, a little in perspective)
    o.append(P("M2,-91 L196,-96 L196,-89 L2,-85Z", lg([(0, "#3A3F45"), (1, "#1A1B1E")])))
    o.append(P("M2,-91 L-176,-84 L-176,-78 L2,-85Z", lg([(0, "#3A3F45"), (1, "#1A1B1E")])))
    o.append(lamp(122, 16, 3, 5, "#FFF4D0"))
    return "".join(o)


def boat():
    """A small passenger ship on the water: dark blue hull, white decks with windows, a funnel."""
    o = []
    # funnel and mast
    o.append(P("M8,-116 L40,-116 L36,-64 L4,-64Z", lg([(0, "#E8433A"), (.5, "#C91F1E"), (1, "#7E1015")], 0, 0, 1, 0)))
    o.append(R(6, -122, 36, 10, "#1F2226", 2))
    o.append(L("M-60,-60 L-60,-132", "#5A6168", 3) + L("M-74,-118 L-46,-118", "#5A6168", 2.4))
    # upper deck
    up = "M-90,-62 L60,-62 C70,-62 76,-56 78,-48 L82,-30 L-96,-30 L-96,-56 C-96,-60 -94,-62 -90,-62Z"
    o.append(paint(up, (-96, -62, 82, -30), "#F4F6F8", .3, .25, ends=.12, seed=14))
    o.append(glass("M56,-56 L74,-56 L78,-38 L56,-38Z", (56, -56, 78, -38), "#2C4252"))
    o.append("".join(glass(rrect(x, -54, 16, 14, 3), (x, -54, x + 16, -40), "#2C4252", sky=False) for x in range(-84, 50, 24)))
    # main deck
    md = "M-130,-30 L100,-30 C112,-30 118,-24 120,-14 L124,4 L-136,4 L-136,-24 C-136,-28 -134,-30 -130,-30Z"
    o.append(paint(md, (-136, -30, 124, 4), "#F4F6F8", .3, .3, ends=.12, seed=15))
    o.append("".join(C(x, -14, 6.5, lg([(0, "#4E6474"), (1, "#1E2A34")])) + C(x - 2, -16, 2.2, "#FFFFFF", 'opacity=".45"') for x in range(-120, 110, 22)))
    o.append(L("M-136,-31 L120,-31", "#B4BCC3", 2.4))
    # hull
    hull = "M-160,4 L176,4 C170,30 156,52 136,58 L-136,58 C-148,50 -156,30 -160,4Z"
    extra = [R(-170, 4, 350, 8, "#FFFFFF", 0, 'opacity=".9"'), R(-170, 44, 350, 20, "#C62A24")]
    o.append(paint(hull, (-160, 4, 176, 58), "#1E3F73", .25, .35, ends=.2, extra="".join(extra), seed=16))
    o.append(C(150, 20, 4, "#C9CED3"))
    # water
    water = "M-190,52 C-170,46 -150,58 -130,52 C-110,46 -90,58 -70,52 C-50,46 -30,58 -10,52 C10,46 30,58 50,52 C70,46 90,58 110,52 C130,46 150,58 170,52 C180,49 186,50 190,52 L190,86 L-190,86Z"
    o.append(P(water, lg([(0, "#5CB4E6"), (.5, "#2E8BC9"), (1, "#1C6CA8", .0)])))
    o.append(L("M-160,64 C-140,60 -120,66 -100,62 M-30,68 C-10,64 10,70 30,66 M90,64 C110,60 130,66 150,62", "#FFFFFF", 2.4, 'opacity=".55"'))
    return "".join(o)


def fire_truck():
    """A red fire engine: cab with windows, equipment lockers, a silver ladder, warning lights."""
    base = "#D3221E"
    o = [ground(0, 60, 178, 8, .3)]
    # ladder on top
    o.append(L("M-168,-98 L120,-112", "#B4BCC3", 5) + L("M-168,-86 L120,-100", "#8C949C", 5))
    o.append(L(" ".join(f"M{f1(x)},{f1(-98 - (x + 168) * 14 / 288)} L{f1(x)},{f1(-86 - (x + 168) * 14 / 288)}" for x in range(-160, 120, 16)), "#C9CED3", 3))
    o.append(R(-120, -88, 12, 14, "#5A6168") + R(40, -94, 12, 18, "#5A6168"))
    # body with lockers
    body = ("M-172,-78 L80,-78 L80,-110 C80,-116 84,-120 92,-120 L140,-120 C150,-120 156,-114 160,-104 "
            "L170,-60 L172,-40 L172,22 C172,27 168,30 162,30 L150,30 A28,28 0 0 0 94,30 L-48,30 A28,28 0 0 0 -104,30 "
            "L-108,30 A28,28 0 0 0 -164,30 L-168,30 C-171,30 -172,27 -172,22Z")
    box = (-172, -120, 172, 31)
    extra = [R(-180, -6, 360, 7, "#FFFFFF", 0, 'opacity=".95"'), R(-180, 1, 360, 3, "#F2C230"),
             gloss(-172, 172, -72, 8, .45), gloss(80, 172, -114, 7, .45),
             R(-180, 10, 360, 22, lg([(0, "#000000", 0), (1, "#000000", .3)]))]
    o.append(paint(body, box, base, .3, .55, extra="".join(extra), seed=17))
    for x in (-160, -110, -60, -10, 40):
        o.append(P(rrect(x, -70, 42, 56, 4), lg([(0, "#E4E8EB"), (1, "#9AA2AA")])))
        o.append(L(" ".join(f"M{x + 2},{y} L{x + 40},{y}" for y in range(-64, -16, 6)), "#8C949C", 1.2))
        o.append(R(x + 16, -22, 10, 4, "#4A4E54", 2))
    o.append(arch(-136, 30, 28) + arch(-76, 30, 28) + arch(122, 30, 28))
    # cab windows and door
    o.append(glass("M98,-110 L140,-110 C146,-110 150,-106 152,-100 L160,-62 L98,-62Z", (98, -110, 160, -62), "#2C4252"))
    o.append(L("M126,-110 L126,-62", dk(base, .4), 3))
    o.append(L("M92,-112 L92,24 M162,-60 L162,0", dk(base, .45), 1.4, 'opacity=".6"'))
    o.append(R(98, -48, 12, 4, chrome(), 2))
    # warning light bar
    o.append(P(rrect(94, -130, 56, 10, 4), lg([(0, "#FF9A9A"), (.5, "#F0262D"), (1, "#8C0A10")])))
    o.append(E(110, -126, 10, 2.5, "#FFFFFF", 'opacity=".6"') + E(134, -126, 10, 2.5, "#FFFFFF", 'opacity=".6"'))
    o.append(lamp(170, -20, 3, 7, "#FFF4D0") + lamp(-171, -40, 2.6, 7, "#FFB33A"))
    o.append(R(150, 14, 24, 16, "#C9CED3", 3) + R(-174, 16, 12, 14, "#2A2D33", 3))
    # hose reel at the back
    o.append(C(-150, -42, 16, "#3A3F45") + C(-150, -42, 10, "#F2C230") + C(-150, -42, 4, "#3A3F45"))
    o.append(tyre(-136, 30, 24) + tyre(-76, 30, 24) + tyre(122, 30, 24))
    return "".join(o)


def van(base, cross=False, stripe=None, bar=""):
    """A high-roof van (the ambulance)."""
    body = ("M-140,24 L-140,-84 C-140,-92 -135,-96 -127,-96 L72,-96 C82,-96 88,-92 92,-84 L114,-38 "
            "C118,-32 124,-30 132,-28 C138,-26 142,-20 142,-12 L143,22 C143,27 140,30 134,30 L120,30 "
            "A28,28 0 0 0 64,30 L-62,30 A28,28 0 0 0 -118,30 L-134,30 C-138,30 -140,28 -140,24Z")
    box = (-140, -96, 143, 31)
    extra = [gloss(-140, 143, -88, 10, .7), R(-150, 8, 300, 24, lg([(0, "#000000", 0), (1, "#000000", .22)]))]
    if stripe:
        extra.insert(0, R(-150, -34, 300, 14, stripe) + R(-150, -18, 300, 4, "#1F55B8"))
    o = [ground(0, 59, 150, 8, .3)]
    o.append(paint(body, box, base, .3, .32, ends=.15, extra="".join(extra), seed=18))
    o.append(arch(-90, 30, 28) + arch(92, 30, 28))
    o.append(glass("M76,-84 C82,-84 86,-82 88,-78 L106,-40 L76,-40Z", (76, -84, 106, -40), "#2C4252"))
    o.append(L("M70,-92 L70,24 M-4,-92 L-4,24 M-138,-92 L-138,24", "#9AA4AD", 1.4))
    o.append(R(54, -30, 12, 4, chrome(), 2))
    o.append(glass(rrect(18, -82, 40, 34, 4), (18, -82, 58, -48), "#2C4252"))
    if cross:
        o.append(P("M-86,-88 L-62,-88 L-62,-70 L-44,-70 L-44,-46 L-62,-46 L-62,-28 L-86,-28 L-86,-46 L-104,-46 L-104,-70 L-86,-70Z",
                   lg([(0, "#F0353A"), (1, "#B8141A")])))
    o.append(P("M-142,16 L144,16 L144,30 L-142,30Z", "#2A2D33"))
    o.append(lamp(140, -18, 3, 7, "#FFF4D0") + lamp(-139, -50, 2.4, 8, "#E0302A"))
    o.append(bar)
    o.append(tyre(-90, 30, 24) + tyre(92, 30, 24))
    return "".join(o)


def ambulance():
    bar = (P(rrect(30, -106, 56, 10, 4), lg([(0, "#FF9A9A"), (.5, "#F0262D"), (1, "#8C0A10")]))
           + P(rrect(-136, -104, 16, 8, 3), lg([(0, "#FF9A9A"), (1, "#B8141A")]))
           + E(46, -102, 10, 2.4, "#FFFFFF", 'opacity=".6"') + E(70, -102, 10, 2.4, "#FFFFFF", 'opacity=".6"'))
    return van("#F6F7F8", cross=True, stripe="#E3262B", bar=bar)


def bag(x, y, r, col):
    """A tied rubbish bag: a round sack with a knot on top."""
    return (P(blob([(x - r, y + r * .7), (x - r * 1.05, y - r * .2), (x - r * .5, y - r * .9), (x, y - r), (x + r * .5, y - r * .9),
                    (x + r * 1.05, y - r * .2), (x + r, y + r * .7), (x, y + r)]), col)
            + P(f"M{f1(x - r * .3)},{f1(y - r * .9)} L{f1(x - r * .45)},{f1(y - r * 1.45)} L{f1(x)},{f1(y - r * 1.15)} L{f1(x + r * .45)},{f1(y - r * 1.45)} L{f1(x + r * .3)},{f1(y - r * .9)}Z", col))


def bags_real():
    return [bag(-158, -10, 19, lg([(0, "#BFE3FA"), (.5, "#7FB8E0"), (1, "#3E7EB0")], 0, 0, 1, 1)),
            bag(-128, -6, 17, lg([(0, "#FFFFFF"), (.5, "#E2E6EA"), (1, "#9AA4AD")], 0, 0, 1, 1)),
            bag(-142, -38, 16, lg([(0, "#FFE9A0"), (.5, "#F2C84A"), (1, "#B88A10")], 0, 0, 1, 1))]


def garbage_truck():
    """A Taiwanese yellow garbage truck: cab, rounded compactor body, rear hopper."""
    base = "#F4C016"
    o = [ground(0, 60, 176, 8, .3)]
    # compactor body
    bd = "M-104,-100 C-104,-112 -96,-118 -84,-118 L70,-118 C80,-118 84,-112 84,-102 L84,14 L-104,14Z"
    extra = [gloss(-104, 84, -108, 9, .5), R(-110, -30, 200, 8, "#2E8B57"), R(-110, -22, 200, 3, "#FFFFFF", 0, 'opacity=".8"'),
             L(" ".join(f"M{x},-112 L{x},10" for x in range(-80, 80, 30)), dk(base, .2), 1.6, 'opacity=".55"')]
    o.append(paint(bd, (-104, -118, 84, 14), base, .3, .4, extra="".join(extra), seed=19))
    # rear loader: sloping tailgate with a wide open mouth full of rubbish bags
    hop = "M-100,-114 L-126,-114 C-148,-114 -164,-98 -170,-76 L-180,-30 L-180,10 C-180,16 -176,20 -170,20 L-100,20Z"
    o.append(paint(hop, (-180, -114, -100, 20), dk(base, .06), .25, .5, ends=.2, seed=20,
                   extra=L("M-104,-114 L-104,20", dk(base, .35), 2, 'opacity=".7"')))
    mouth = "M-176,-40 C-174,-56 -164,-64 -150,-64 L-116,-64 L-116,10 L-176,10Z"
    o.append(P(mouth, lg([(0, "#141518"), (1, "#3A3D42")])))
    o.append(inside(mouth, *bags_real()))
    o.append(L("M-160,-104 L-120,-70", "#B4BCC3", 6) + L("M-160,-104 L-120,-70", "#E8ECEF", 2))
    o.append(R(-184, 10, 70, 7, "#5A6168", 2))
    # chassis
    o.append(R(-140, 10, 312, 12, "#2A2D33"))
    # cab
    cab = ("M88,-100 C88,-108 94,-112 102,-112 L138,-112 C148,-112 154,-106 158,-96 L170,-56 L172,-40 "
           "L172,22 C172,27 168,30 162,30 L150,30 A28,28 0 0 0 94,30 L88,30Z")
    extra = [gloss(88, 172, -104, 8, .5), R(80, -30, 100, 8, "#2E8B57"), R(80, 10, 100, 22, lg([(0, "#000000", 0), (1, "#000000", .3)]))]
    o.append(paint(cab, (88, -112, 172, 31), base, .3, .45, extra="".join(extra), seed=21))
    o.append(glass("M100,-104 L136,-104 C144,-104 148,-100 150,-94 L160,-60 L100,-60Z", (100, -104, 160, -60), "#2C4252"))
    o.append(L("M94,-106 L94,24", dk(base, .4), 1.4, 'opacity=".6"') + R(100, -48, 12, 4, chrome(), 2))
    o.append(arch(122, 30, 28) + arch(-70, 30, 28))
    o.append(lamp(170, -20, 3, 7, "#FFF4D0") + R(150, 16, 24, 14, "#C9CED3", 3))
    o.append(P(rrect(108, -120, 30, 8, 3), lg([(0, "#FFD27A"), (1, "#E07A10")])))
    o.append(tyre(-70, 30, 24) + tyre(122, 30, 24))
    return "".join(o)


def truck():
    """A cargo truck: a flat-fronted blue cab and a big silver box."""
    base = "#1F5FB0"
    o = [ground(0, 60, 176, 8, .3)]
    o.append(R(-170, 8, 330, 14, "#2A2D33"))
    bx = rrect(-172, -124, 248, 128, 6)
    extra = [R(-180, -128, 260, 6, "#FFFFFF", 0, 'opacity=".5"'),
             L(" ".join(f"M{x},-122 L{x},2" for x in range(-150, 76, 22)), "#9AA2AA", 1.4, 'opacity=".6"'),
             R(-180, -20, 260, 26, lg([(0, "#000000", 0), (1, "#000000", .25)]))]
    o.append(paint(bx, (-172, -124, 76, 4), "#E6EAED", .3, .3, ends=.12, extra="".join(extra), seed=22))
    o.append(R(-172, -8, 248, 6, "#F2A31B"))
    cab = ("M84,-104 C84,-112 90,-116 98,-116 L158,-116 C166,-116 170,-112 171,-104 L174,-40 L174,22 "
           "C174,27 170,30 164,30 L152,30 A28,28 0 0 0 96,30 L84,30Z")
    extra = [gloss(84, 174, -108, 8, .5), R(80, 10, 100, 22, lg([(0, "#000000", 0), (1, "#000000", .3)])),
             L("M92,-112 L92,24", dk(base, .4), 1.4, 'opacity=".6"')]
    o.append(paint(cab, (84, -116, 174, 31), base, .3, .5, extra="".join(extra), seed=23))
    o.append(glass("M98,-106 L166,-106 L168,-62 L98,-62Z", (98, -106, 168, -62), "#2C4252"))
    o.append(R(98, -50, 12, 4, chrome(), 2) + R(162, -40, 12, 30, "#3A3F45", 2))
    o.append(L(" ".join(f"M164,{y} L172,{y}" for y in range(-36, -12, 5)), "#8C949C", 1.4))
    o.append(arch(124, 30, 28) + arch(-80, 30, 28) + arch(-136, 30, 28))
    o.append(lamp(172, 2, 3, 6, "#FFF4D0") + R(150, 16, 26, 14, "#C9CED3", 3))
    o.append(tyre(-136, 30, 24) + tyre(-80, 30, 24) + tyre(124, 30, 24))
    return "".join(o)


def excavator():
    """A yellow excavator: tracks, turning body with a glass cab, boom, arm and toothed bucket."""
    base = "#F2B705"
    o = [ground(-10, 84, 160, 8, .3)]
    # tracks
    tr = rrect(-150, 40, 220, 42, 21)
    o.append(P(tr, lg([(0, "#4A4E54"), (.5, "#2A2C30"), (1, "#141518")])))
    o.append(L(" ".join(f"M{x},42 L{x},80" for x in range(-140, 70, 10)), "#121315", 2.2, 'opacity=".7"'))
    o.append(P(rrect(-138, 48, 196, 26, 13), "#3A3F45"))
    o.append("".join(C(x, 61, 9, rg([(0, "#9AA2AA"), (1, "#4A4E54")])) for x in (-124, -94, -64, -34, -4, 26, 46)))
    o.append(R(-60, 30, 40, 12, "#2A2C30"))
    # house (upper body) and counterweight
    hs = "M-150,-14 C-150,-24 -144,-30 -132,-30 L44,-30 C52,-30 56,-24 56,-16 L56,30 L-150,30Z"
    extra = [gloss(-150, 56, -24, 8, .5), R(-160, 14, 230, 18, lg([(0, "#000000", 0), (1, "#000000", .3)])),
             L(" ".join(f"M{x},-24 L{x},-4" for x in range(-130, -80, 8)), "#2A2C30", 2.4, 'opacity=".5"')]
    o.append(paint(hs, (-150, -30, 56, 30), base, .3, .45, extra="".join(extra), seed=24))
    o.append(R(-150, 24, 206, 8, "#2A2C30"))
    # cab
    cab = "M-2,-118 L44,-118 C50,-118 54,-114 54,-108 L56,-30 L-6,-30 L-6,-110 C-6,-114 -4,-118 -2,-118Z"
    o.append(paint(cab, (-6, -118, 56, -30), base, .3, .4, seed=25))
    o.append(glass("M2,-110 L46,-110 L48,-38 L2,-38Z", (2, -110, 48, -38), "#2C4252"))
    o.append(L("M24,-110 L24,-38", dk(base, .35), 3))
    o.append(P(rrect(-8, -124, 66, 8, 3), "#2A2C30"))
    # boom
    boom = "M40,-10 C60,-50 90,-110 116,-142 C124,-152 140,-150 144,-138 C146,-130 142,-124 136,-118 C114,-88 84,-40 66,-2Z"
    o.append(paint(boom, (40, -152, 146, -2), base, .35, .4, ends=.15, seed=26))
    o.append(L("M36,-24 L104,-110", "#C9CED3", 7) + L("M36,-24 L80,-80", "#3A3F45", 9))
    # arm (stick) and bucket
    arm = "M128,-150 C140,-156 152,-148 152,-136 L166,-30 C167,-22 160,-16 152,-16 C146,-16 142,-20 141,-26 L124,-134 C123,-142 124,-147 128,-150Z"
    o.append(paint(arm, (123, -156, 167, -16), base, .3, .4, ends=.2, seed=27))
    o.append(L("M140,-150 L162,-60", "#C9CED3", 5) + L("M140,-150 L152,-100", "#3A3F45", 7))
    o.append(C(136, -138, 7, "#3A3F45") + C(136, -138, 3, "#9AA2AA"))
    buck = "M150,-30 C172,-38 194,-26 196,-4 L196,30 C196,38 190,42 182,40 L140,30 C150,20 158,4 150,-30Z"
    o.append(P(buck, lg([(0, "#5A6168"), (.5, "#3A3F45"), (1, "#1E2124")], 0, 0, 1, 1)))
    o.append(inside(buck, glow(180, -14, 18, 30, "#FFFFFF", .25)))
    o.append(P("M142,30 L148,40 L154,32 L160,42 L166,34 L172,44 L178,36 L184,44 L190,38 L182,40Z", "#8C949C"))
    o.append(C(158, -22, 6, "#2A2C30") + C(158, -22, 2.5, "#9AA2AA"))
    return "".join(o)


def hot_air_balloon():
    """A striped hot-air balloon with ropes and a wicker basket."""
    env = ("M0,-178 C70,-178 118,-128 118,-66 C118,-10 76,34 40,66 C30,76 24,86 22,98 L-22,98 "
           "C-24,86 -30,76 -40,66 C-76,34 -118,-10 -118,-66 C-118,-128 -70,-178 0,-178Z")
    cols = ["#E53935", "#FBC02D", "#1E88E5", "#43A047", "#FB8C00", "#8E24AA", "#E53935", "#FBC02D", "#1E88E5", "#43A047", "#FB8C00", "#8E24AA"]
    o = [ground(0, 186, 50, 5, .18)]
    gores = []
    n = 9
    for i in range(n):
        t0, t1 = -1 + 2 * i / n, -1 + 2 * (i + 1) / n

        def edge(t):
            return f"M{f1(t * 22)},98 C{f1(t * 80)},40 {f1(t * 150)},-40 {f1(t * 128)},-110 C{f1(t * 110)},-160 {f1(t * 40)},-180 0,-180"
        a = edge(t0)
        b = edge(t1)
        # region between two meridian curves
        d = (f"M{f1(t0 * 22)},98 C{f1(t0 * 80)},40 {f1(t0 * 150)},-40 {f1(t0 * 128)},-110 C{f1(t0 * 110)},-160 {f1(t0 * 40)},-180 0,-180 "
             f"C{f1(t1 * 40)},-180 {f1(t1 * 110)},-160 {f1(t1 * 128)},-110 C{f1(t1 * 150)},-40 {f1(t1 * 80)},40 {f1(t1 * 22)},98Z")
        gores.append(P(d, cols[i % len(cols)]))
    shade_ = [P(env, rg([(0, "#FFFFFF", .35), (.35, "#FFFFFF", 0), (.75, "#000000", .1), (1, "#000000", .45)], cx=.36, cy=.3, r=.75, fx=.32, fy=.24)),
              specks((-120, -180, 120, 100), .07, 28)]
    o.append(inside(env, *gores, *shade_))
    o.append(P("M-22,96 L22,96 L20,104 L-20,104Z", "#8A5A2A"))
    # ropes and burner
    o.append(L("M-21,103 L-26,140 M21,103 L26,140 M-8,104 L-10,140 M8,104 L10,140", "#5A4632", 1.6))
    o.append(R(-10, 108, 20, 10, "#6E767E", 2) + glow(0, 120, 10, 6, "#FFB33A", .6))
    # basket
    bk = "M-30,138 L30,138 L26,182 C26,186 22,188 18,188 L-18,188 C-22,188 -26,186 -26,182Z"
    o.append(P(bk, lg([(0, "#C68A4A"), (.5, "#A06A32"), (1, "#6E4520")])))
    weave = " ".join(f"M-30,{y} L30,{y}" for y in range(144, 188, 7)) + " " + " ".join(f"M{x},140 L{f1(x * .88)},188" for x in range(-24, 30, 8))
    o.append(inside(bk, L(weave, "#5A3818", 1.2, 'opacity=".5"'), shade((-30, 138, 30, 188), left=.3, right=.35, w=.25)))
    o.append(P(rrect(-33, 134, 66, 8, 4), "#7A4E24"))
    return "".join(o)


def rocket():
    """A rocket lifting off: white body, red nose and fins, round window, flame and smoke."""
    body = "M0,-188 C30,-160 44,-110 44,-50 L44,104 L-44,104 L-44,-50 C-44,-110 -30,-160 0,-188Z"
    o = []
    # smoke clouds and flame
    for cx, cy, r in ((-70, 176, 34), (70, 176, 34), (-34, 186, 30), (34, 186, 30), (0, 180, 28), (-110, 186, 22), (110, 186, 22)):
        o.append(C(cx, cy, r, rg([(0, "#FFFFFF"), (.7, "#E6E9EC"), (1, "#B8C0C8")], cx=.4, cy=.35)))
    flame = "M-30,112 C-28,140 -16,160 0,190 C16,160 28,140 30,112Z"
    o.append(P(flame, lg([(0, "#FFF6C8"), (.35, "#FFC23A"), (.75, "#FF7A1A"), (1, "#E0401A", .0)])))
    o.append(P("M-14,112 C-12,130 -6,144 0,160 C6,144 12,130 14,112Z", lg([(0, "#FFFFFF"), (1, "#FFE08A", .2)])))
    # nozzle
    o.append(P("M-30,100 L30,100 L36,120 L-36,120Z", lg([(0, "#5A6168"), (.5, "#9AA2AA"), (1, "#3A3F45")], 0, 0, 1, 0)))
    # fins
    fin = "M-44,40 C-70,60 -86,90 -88,128 L-44,104Z M44,40 C70,60 86,90 88,128 L44,104Z"
    o.append(P(fin, lg([(0, "#F04A3A"), (.5, "#C91F1E"), (1, "#7E1015")], 0, 0, 1, 0)))
    o.append(P("M-4,60 L4,60 L4,128 L-4,128Z", "#9A1410"))
    # body
    o.append(P(body, lg([(0, "#9AA4AD"), (.15, "#E6EAED"), (.38, "#FFFFFF"), (.7, "#D2D8DD"), (1, "#8A949D")], 0, 0, 1, 0)))
    nose = "M0,-188 C22,-168 34,-138 39,-110 L-39,-110 C-34,-138 -22,-168 0,-188Z"
    o.append(P(nose, lg([(0, "#8A1015"), (.25, "#E23A33"), (.45, "#F27A6A"), (.75, "#C91F1E"), (1, "#6E0C10")], 0, 0, 1, 0)))
    o.append(R(-44, 80, 88, 10, lg([(0, "#7E1015"), (.4, "#E23A33"), (1, "#6E0C10")], 0, 0, 1, 0)))
    o.append(R(-44, -110, 88, 4, "#B4BCC3", 0, 'opacity=".7"'))
    o.append(inside(body, specks((-44, -188, 44, 104), .06, 29)))
    # window
    o.append(C(0, -40, 22, lg([(0, "#E6EAED"), (1, "#8A949D")])) + C(0, -40, 16, rg([(0, "#7FC2EA"), (.6, "#2E78B6"), (1, "#163E66")], cx=.4, cy=.35)))
    o.append(E(-6, -46, 6, 4, "#FFFFFF", 'opacity=".6" transform="rotate(-35 -6 -46)"'))
    o.append(L("M-44,20 L44,20", "#B4BCC3", 1.4))
    return "".join(o)


def stroller():
    """A baby stroller: a soft hood, seat, push handle and four wheels."""
    base = "#2F7E86"
    o = [ground(0, 108, 130, 7, .25)]
    # frame
    o.append(L("M-100,-122 L-62,16 L-96,80 M-62,16 L80,86 M-62,16 L64,16", "#8C949C", 7))
    o.append(L("M-100,-122 L-62,16 M-60,14 L62,14", "#D6DBDF", 2))
    o.append(L("M-110,-128 L-90,-118", "#2A2C30", 10))
    # basket under the seat
    o.append(P("M-50,30 L56,30 L48,58 L-40,58Z", "#3A3F45", 'opacity=".85"'))
    o.append(L(" ".join(f"M{x},32 L{x - 4},56" for x in range(-40, 56, 10)), "#6E767E", 1.4))
    # seat body
    seat = "M-70,-36 C-60,-20 -40,-8 0,-6 L60,-8 C78,-8 88,0 88,10 C88,22 78,26 64,26 L-40,26 C-60,26 -72,10 -74,-12Z"
    o.append(paint(seat, (-74, -36, 88, 26), base, .3, .45, ends=.12, seed=30))
    o.append(P("M-40,-8 C-10,-10 30,-12 70,-4", "none", f'stroke="{lt(base, .4)}" stroke-width="2.4" opacity=".7"'))
    # hood (canopy) with folds
    hood = "M-82,-34 C-90,-80 -70,-120 -20,-128 C30,-132 66,-110 72,-70 C60,-74 40,-72 20,-60 C0,-48 -30,-38 -82,-34Z"
    o.append(paint(hood, (-90, -132, 72, -34), base, .35, .5, ends=.15, seed=31))
    o.append(inside(hood, L("M-70,-40 C-60,-90 -30,-120 -10,-126 M-40,-38 C-20,-80 10,-110 30,-120 M-8,-46 C16,-80 40,-100 60,-102", dk(base, .35), 3, 'opacity=".5"')))
    o.append(P("M72,-70 C60,-74 40,-72 20,-60 C0,-48 -30,-38 -82,-34 L-80,-28 C-30,-32 0,-42 22,-54 C42,-66 60,-66 72,-62Z", dk(base, .45)))
    # bumper bar
    o.append(L("M76,-6 C90,-20 96,-30 92,-40", "#3A3F45", 6))
    # wheels
    for cx, cy, r in ((-96, 80, 26), (80, 86, 20)):
        o.append(C(cx, cy, r, rg([(0, "#3A3D42"), (.8, "#24262A"), (1, "#0E0F11")])))
        o.append(C(cx, cy, r * .62, rg([(0, "#F4F6F8"), (.6, "#C2C8CE"), (1, "#7C848C")], cx=.4, cy=.35)))
        o.append(L(" ".join(f"M{cx},{cy} L{f1(cx + r * .6 * math.cos(math.radians(a)))},{f1(cy + r * .6 * math.sin(math.radians(a)))}" for a in range(0, 360, 45)), "#7C848C", 1.6))
        o.append(C(cx, cy, r * .18, "#5A6168"))
    return "".join(o)


REAL = {
    "car": (car, (-134, -72, 134, 66)),
    "bus": (bus, (-178, -118, 182, 68)),
    "taxi": (taxi, (-142, -88, 142, 70)),
    "scooter": (scooter, (-150, -144, 140, 84)),
    "bicycle": (bicycle, (-166, -102, 166, 104)),
    "train": (train, (-182, -200, 182, 72)),
    "mrt": (mrt, (-180, -106, 180, 62)),
    "hsr": (hsr, (-184, -84, 184, 52)),
    "airplane": (airplane, (-182, -122, 182, 92)),
    "helicopter": (helicopter, (-178, -100, 200, 100)),
    "boat": (boat, (-190, -134, 190, 86)),
    "fire_truck": (fire_truck, (-180, -132, 180, 68)),
    "ambulance": (ambulance, (-152, -108, 152, 68)),
    "police_car": (police_car, (-142, -78, 142, 70)),
    "garbage_truck": (garbage_truck, (-186, -124, 178, 68)),
    "truck": (truck, (-180, -126, 180, 68)),
    "excavator": (excavator, (-160, -160, 200, 92)),
    "hot_air_balloon": (hot_air_balloon, (-124, -184, 124, 194)),
    "rocket": (rocket, (-150, -194, 150, 220)),
    "stroller": (stroller, (-130, -136, 130, 116)),
}

# ================================================================ cartoon vehicles
# Flat bold shapes, bright colours, no outlines and no texture. Most get friendly eyes in the
# front window and a smile at the front. Colours follow the realistic card.
RED, YEL, BLUE, GREEN, ORANGE = "#F2353B", "#FFC62E", "#2F7DE1", "#27B26B", "#FF8A1F"
SKY, DARK, GREY, WHITE, SHADOW = "#BDE7FA", "#2B2B33", "#B8C2CC", "#FFFFFF", "#000000"


def floor(cx, cy, rx):
    return E(cx, cy, rx, 7, "#1E1E28", 'opacity=".12"')


def under(d, y, color, extra_h=200):
    """The lower part of a shape from y down, in another colour (flat two-tone)."""
    return inside(d, R(-400, y, 800, extra_h, color))


def shine(x, y, w, h=6):
    return R(x, y, w, h, WHITE, h / 2, 'opacity=".45"')


def c_car(color=RED, roof="", lower=None, sign_shift=0):
    o = [floor(0, 58, 128)]
    cabin = "M-70,-28 L-48,-68 Q-44,-76 -34,-76 L36,-76 Q46,-76 52,-68 L80,-28Z"
    body = rrect(-122, -32, 244, 64, 28)
    o.append(P(cabin, color) + P(body, color))
    if lower:
        o.append(under(body, 2, lower))
    o.append(shine(-96, -22, 70))
    o.append(P("M-56,-30 L-40,-62 Q-38,-66 -32,-66 L34,-66 Q40,-66 44,-62 L64,-30Z", SKY))
    o.append(R(-14, -68, 8, 40, color))
    o.append(eye(14, -46, 11, (.3, .05)) + eye(40, -46, 11, (.3, .05)))
    o.append(smile(100, 4, 22, 9, 4.5) + cheek(84, 14, 7))
    o.append(E(116, -14, 6, 9, "#FFE45C") + E(-118, -14, 5, 8, "#FF7A59"))
    o.append(wheel_flat(-70, 32, 27) + wheel_flat(72, 32, 27))
    o.append(roof)
    return "".join(o)


def c_taxi():
    sign = (P(rrect(-30, -100, 60, 24, 7), WHITE) + R(-24, -80, 48, 6, DARK, 2)
            + L("M-20,-95 L-12,-95 M-16,-95 L-16,-84 M-9,-84 L-5,-95 L-1,-84 M-7.5,-88 L-2.5,-88 "
                "M3,-95 L10,-84 M10,-95 L3,-84 M14,-95 L20,-95 M17,-95 L17,-84 M14,-84 L20,-84", DARK, 3))
    return c_car(YEL, sign)


def c_police():
    bar = (P(rrect(-34, -90, 34, 14, 6), RED) + P(rrect(0, -90, 34, 14, 6), BLUE) + R(-10, -78, 20, 4, DARK))
    return c_car("#F4F7FA", bar, lower="#1F5FC8")


def c_bus():
    o = [floor(0, 60, 168)]
    body = rrect(-160, -110, 320, 142, 30)
    o.append(P(body, "#F4F7FA") + under(body, -10, BLUE) + inside(body, R(-200, -16, 400, 6, "#1A4FA0")))
    o.append(shine(-140, -102, 120))
    o.append(P(rrect(-80, -122, 110, 14, 6), "#DCE3EA"))
    o.append(P(rrect(70, -106, 60, 12, 5), DARK) + "".join(R(76 + i * 9, -103, 6, 6, ORANGE, 1) for i in range(6)))
    for x in (-146, -100, -54):
        o.append(P(rrect(x, -88, 38, 44, 10), SKY))
    o.append(P(rrect(-6, -88, 40, 108, 10), "#DCE3EA") + P(rrect(0, -82, 13, 96, 5), SKY) + P(rrect(16, -82, 13, 96, 5), SKY))
    o.append(P(rrect(50, -88, 98, 52, 14), SKY))
    o.append(eye(84, -62, 13, (.3, .05)) + eye(118, -62, 13, (.3, .05)))
    o.append(smile(132, -8, 26, 9, 5) + cheek(110, 2, 8))
    o.append(E(152, 12, 6, 8, "#FFE45C") + E(-154, 10, 5, 8, "#FF7A59"))
    o.append(wheel_flat(-96, 32, 26) + wheel_flat(100, 32, 26))
    return "".join(o)


def c_scooter():
    base = "#3D8FE0"
    o = [floor(5, 76, 130)]
    o.append(wheel_flat(-82, 42, 32) + wheel_flat(98, 42, 32))
    o.append(P(rrect(-136, 22, 60, 16, 8), GREY))
    o.append(L("M90,-6 L98,42", GREY, 10))
    o.append(P("M64,14 C72,-2 108,-6 130,10 L130,16 C112,8 88,8 76,18Z", base))
    body = ("M-142,-8 C-146,-26 -134,-40 -110,-42 L-14,-42 C-2,-42 4,-34 2,-22 L0,6 L40,6 "
            "C44,-30 52,-62 60,-86 C62,-94 72,-98 80,-94 C92,-88 108,-66 108,-44 C108,-24 100,-8 90,4 "
            "C80,16 66,24 50,26 L-4,26 C-30,26 -48,20 -58,10 C-80,2 -112,6 -128,6 C-136,6 -140,0 -142,-8Z")
    o.append(P(body, base) + shine(-120, -34, 80) + P("M-2,6 L40,6 L40,14 L-2,14Z", DARK))
    o.append(P("M-140,-38 C-136,-56 -100,-60 -60,-58 L-16,-57 C-4,-57 2,-50 0,-42 L-140,-38Z", DARK))
    o.append(P("M56,-108 C62,-120 94,-122 110,-112 C116,-106 112,-96 104,-92 L64,-90 C56,-92 53,-100 56,-108Z", base))
    o.append(E(106, -104, 6, 9, "#FFE45C") + E(-142, -20, 5, 8, "#FF7A59"))
    o.append(L("M60,-104 L38,-110", DARK, 10))
    o.append(L("M72,-114 L68,-126 M90,-116 L90,-128", DARK, 4) + E(66, -131, 11, 7, DARK) + E(92, -133, 11, 7, DARK))
    return "".join(o)


def c_bicycle():
    frame = "#18A99E"
    o = [floor(0, 100, 160)]
    for cx in (-98, 98):
        o.append(C(cx, 34, 56, "none", f'stroke="{DARK}" stroke-width="14"'))
        o.append(L(" ".join(f"M{cx},34 L{f1(cx + 48 * math.cos(math.radians(a)))},{f1(34 + 48 * math.sin(math.radians(a)))}" for a in range(0, 360, 60)), GREY, 3))
        o.append(C(cx, 34, 8, GREY))
    o.append(L("M-6,44 L-98,34 L-36,-58 M-6,44 L-40,-64 M-38,-56 L62,-62 M-6,44 L70,-40", frame, 12))
    o.append(L("M62,-70 L70,-40 L98,34", frame, 12))
    o.append(C(-6, 44, 15, GREY) + L("M-6,44 L8,72", DARK, 7) + R(-4, 70, 24, 8, DARK, 4))
    o.append(L("M-40,-64 L-44,-80", GREY, 7) + P(rrect(-78, -94, 60, 16, 8), RED))
    o.append(L("M62,-70 L58,-92 L30,-92", DARK, 9) + C(48, -102, 7, YEL))
    return "".join(o)


def c_train():
    o = [floor(0, 68, 170), R(-176, 58, 352, 8, "#9A6B4A", 4)]
    for cx, cy, r in ((116, -122, 18), (92, -148, 24), (58, -164, 28)):
        o.append(C(cx, cy, r, "#E9EEF2"))
    o.append(P(rrect(-168, -126, 86, 158, 10), GREEN))
    o.append(P(rrect(-178, -138, 106, 16, 8), RED))
    o.append(P(rrect(-152, -110, 54, 46, 12), SKY))
    o.append(eye(-136, -88, 11, (.35, .05)) + eye(-112, -88, 11, (.35, .05)))
    o.append(P(rrect(-92, -92, 222, 56, 26), GREEN) + shine(-70, -84, 120))
    o.append(R(-30, -92, 10, 56, YEL) + R(40, -92, 10, 56, YEL))
    o.append(P("M104,-96 L106,-128 L128,-128 L130,-96Z", DARK) + P(rrect(98, -136, 38, 12, 6), DARK))
    o.append(P("M40,-92 C40,-114 72,-114 72,-92Z", YEL))
    o.append(C(128, -64, 12, "#FFE45C"))
    o.append(smile(116, -48, 18, 6, 4) if False else "")
    o.append(R(-100, -38, 238, 12, DARK, 4))
    o.append(P("M134,-6 L172,50 L124,50Z", RED))
    for cx, r in ((-128, 30), (-56, 34), (16, 34), (100, 20)):
        cy = 58 - r
        o.append(C(cx, cy, r, RED) + C(cx, cy, r * .4, "#FFD0C8") + C(cx, cy, r * .14, DARK))
    o.append(L("M-128,30 L16,26", GREY, 7))
    return "".join(o)


def c_mrt():
    o = [floor(0, 58, 170), R(-176, 50, 352, 8, "#9AA5B1", 4)]
    body = "M-170,-96 Q-170,-108 -158,-108 L130,-108 Q160,-108 166,-80 L172,-40 L172,14 Q172,24 162,24 L-158,24 Q-170,24 -170,12Z"
    o.append(P(body, "#E3E9EF") + inside(body, R(-200, -26, 400, 18, BLUE), R(-200, 10, 400, 20, "#C5CFD9")))
    o.append(shine(-150, -100, 140))
    for x in (-160, -76, 14):
        o.append(P(rrect(x, -88, 34, 40, 9), SKY))
    for x in (-118, -32):
        o.append(P(rrect(x, -94, 34, 112, 8), "#C5CFD9") + P(rrect(x + 4, -88, 12, 50, 5), SKY) + P(rrect(x + 18, -88, 12, 50, 5), SKY))
    o.append(P("M58,-92 L136,-92 Q156,-92 160,-76 L166,-40 L58,-40Z", SKY))
    o.append(eye(94, -66, 13, (.3, .05)) + eye(128, -66, 13, (.3, .05)))
    o.append(smile(150, 0, 22, 8, 4.5) + cheek(130, 6, 7))
    o.append(E(168, -24, 4, 7, "#FFE45C"))
    for cx in (-110, 100):
        o.append(wheel_flat(cx - 22, 36, 14) + wheel_flat(cx + 22, 36, 14))
    return "".join(o)


def c_hsr():
    o = [floor(0, 50, 176), R(-182, 42, 364, 8, "#9AA5B1", 4)]
    body = "M-176,-80 L20,-80 C64,-80 104,-66 140,-44 C160,-32 176,-16 180,-4 C182,4 178,12 168,12 L-176,12Z"
    o.append(P(body, "#F4F7FA") + inside(body, P("M-200,-26 L80,-26 C120,-26 150,-16 190,0 L190,10 C150,-4 120,-12 80,-12 L-200,-12Z", BLUE),
                                         R(-200, 0, 400, 20, "#C5CFD9")))
    o.append(shine(-160, -72, 160))
    for x in range(-166, 30, 34):
        o.append(P(rrect(x, -62, 24, 22, 8), SKY))
    o.append(P("M52,-72 C86,-68 112,-58 132,-44 L120,-34 C96,-46 74,-52 50,-54Z", SKY))
    o.append(eye(70, -60, 9, (.4, .1)) + eye(96, -54, 9, (.4, .1)))
    o.append(smile(158, -8, 18, 6, 4) + cheek(140, -6, 6))
    o.append(R(-182, -74, 6, 86, DARK, 3))
    for cx in (-128, 92):
        o.append(wheel_flat(cx - 18, 24, 11) + wheel_flat(cx + 18, 24, 11))
    return "".join(o)


def c_airplane():
    o = []
    o.append(P("M20,-22 L-44,-80 Q-36,-86 -26,-80 L52,-24Z", "#9FC2EA"))
    o.append(P("M-110,-22 L-150,-108 Q-148,-118 -136,-114 L-76,-24Z", BLUE))
    body = "M-160,-24 C-120,-36 60,-36 128,-32 C160,-30 180,-14 180,0 C180,14 160,20 128,20 L-120,20 C-150,18 -168,2 -172,-12 C-174,-20 -168,-22 -160,-24Z"
    o.append(P(body, "#F4F7FA") + inside(body, R(-200, 6, 400, 20, "#C5D9EE")))
    o.append(shine(-130, -28, 200))
    o.append("".join(C(x, -8, 6.5, SKY) for x in range(-110, 70, 22)))
    o.append(P("M118,-26 C140,-26 160,-20 170,-8 L118,-8Z", SKY))
    o.append(eye(132, -16, 8, (.4, .1)) + eye(154, -14, 8, (.4, .1)))
    o.append(smile(162, 6, 16, 5, 3.5))
    o.append(P("M-6,8 L58,8 L-30,82 Q-44,88 -54,80Z", "#DCE6F0"))
    o.append(P(rrect(-6, 26, 56, 22, 11), "#C5CFD9") + E(50, 37, 5, 11, DARK))
    o.append(P("M-142,-4 L-178,14 Q-176,20 -166,18 L-120,2Z", "#DCE6F0"))
    return "".join(o)


def c_helicopter():
    base = RED
    o = [floor(10, 92, 110)]
    o.append(L("M-36,48 L-30,72 M50,48 L56,72", GREY, 7) + L("M-72,74 L98,74 Q108,74 112,64", DARK, 8))
    o.append(P("M-40,-40 L-150,-26 L-150,-12 L-40,6Z", base))
    o.append(P("M-140,-24 L-168,-78 Q-160,-86 -150,-80 L-126,-22Z", base))
    o.append(C(-160, -28, 20, GREY, 'opacity=".5"') + L("M-160,-50 L-160,-6", DARK, 5))
    cab = "M-50,-52 C-40,-68 30,-72 60,-64 C98,-54 124,-28 126,2 C128,26 108,48 76,48 L-30,50 C-50,50 -60,36 -60,14 L-60,-30 C-60,-40 -56,-46 -50,-52Z"
    o.append(P(cab, base) + inside(cab, R(-80, 8, 220, 12, WHITE)))
    o.append(shine(-40, -56, 60))
    o.append(P("M30,-60 C78,-54 112,-30 120,-2 L30,-2Z", SKY))
    o.append(eye(58, -30, 13, (.35, .05)) + eye(92, -30, 13, (.35, .05)))
    o.append(smile(104, 28, 22, 8, 4.5) + cheek(84, 34, 7))
    o.append(R(-2, -90, 10, 26, DARK) + P(rrect(-176, -100, 372, 10, 5), DARK))
    return "".join(o)


def c_boat():
    o = []
    o.append(P("M8,-118 L40,-118 L36,-62 L4,-62Z", RED) + P(rrect(4, -128, 40, 14, 6), DARK))
    up = "M-90,-62 L58,-62 Q78,-62 82,-30 L-96,-30 L-96,-54 Q-96,-62 -90,-62Z"
    o.append(P(up, WHITE) + P(up, "#F4F7FA"))
    o.append(P("M50,-56 L70,-56 Q76,-56 78,-36 L50,-36Z", SKY))
    o.append(P("M-130,-30 L104,-30 Q120,-30 124,4 L-136,4 L-136,-24 Q-136,-30 -130,-30Z", "#F4F7FA"))
    o.append("".join(C(x, -13, 8, SKY) for x in range(-118, 40, 26)))
    o.append(P(rrect(-80, -54, 120, 18, 8), SKY))
    o.append(eye(70, -14, 11, (.35, .05)) + eye(98, -14, 11, (.35, .05)))
    hull = "M-160,4 L178,4 C170,32 154,52 134,58 L-136,58 C-150,50 -158,30 -160,4Z"
    o.append(P(hull, "#1F4F9A") + inside(hull, R(-200, 4, 400, 8, WHITE), R(-200, 44, 400, 20, RED)))
    o.append(smile(150, 24, 22, 8, 4.5, WHITE))
    o.append(P("M-190,54 C-170,46 -150,62 -130,54 C-110,46 -90,62 -70,54 C-50,46 -30,62 -10,54 C10,46 30,62 50,54 "
               "C70,46 90,62 110,54 C130,46 150,62 170,54 C180,50 186,52 190,54 L190,84 Q190,90 184,90 L-184,90 Q-190,90 -190,84Z", "#4FB3EA"))
    return "".join(o)


def c_fire_truck():
    o = [floor(0, 62, 172)]
    o.append(L("M-166,-96 L118,-110", GREY, 8) + L("M-166,-82 L118,-96", GREY, 8))
    o.append(L(" ".join(f"M{f1(x)},{f1(-96 - (x + 166) * 14 / 284)} L{f1(x)},{f1(-82 - (x + 166) * 14 / 284)}" for x in range(-156, 118, 20)), GREY, 5))
    body = ("M-172,-78 L80,-78 L80,-110 Q80,-120 92,-120 L140,-120 Q154,-120 160,-104 L170,-60 L172,-40 L172,18 Q172,30 160,30 L-160,30 Q-172,30 -172,18Z")
    o.append(R(-120, -90, 12, 14, GREY) + R(40, -96, 12, 20, GREY))
    o.append(P(body, RED) + inside(body, R(-200, -6, 400, 10, WHITE), R(-200, 4, 400, 4, YEL)))
    o.append(shine(-150, -72, 120))
    for x in (-160, -110, -60, -10, 40):
        o.append(P(rrect(x, -68, 42, 54, 8), "#FFB3B0"))
    o.append(P("M96,-110 L138,-110 Q148,-110 152,-100 L160,-62 L96,-62Z", SKY))
    o.append(eye(114, -86, 11, (.35, .05)) + eye(140, -86, 11, (.35, .05)))
    o.append(smile(148, -30, 22, 8, 4.5) + cheek(128, -22, 7))
    o.append(P(rrect(94, -132, 56, 14, 7), "#FF5A5F") + C(108, -125, 5, "#FFE45C") + C(136, -125, 5, "#FFE45C"))
    o.append(E(170, -18, 4, 8, "#FFE45C"))
    o.append(C(-150, -40, 16, DARK) + C(-150, -40, 9, YEL))
    o.append(wheel_flat(-136, 32, 26) + wheel_flat(-76, 32, 26) + wheel_flat(122, 32, 26))
    return "".join(o)


def c_ambulance():
    o = [floor(0, 60, 146)]
    body = ("M-140,-84 Q-140,-96 -128,-96 L72,-96 Q84,-96 90,-84 L112,-40 Q118,-30 132,-28 Q142,-26 142,-12 L142,18 Q142,30 130,30 "
            "L-128,30 Q-140,30 -140,18Z")
    o.append(P(body, "#F4F7FA") + inside(body, R(-200, -34, 400, 16, RED), R(-200, 10, 400, 30, "#DCE3EA")))
    o.append(shine(-120, -88, 120))
    o.append(P("M30,-84 L74,-84 Q84,-84 88,-76 L106,-40 L30,-40 Q22,-40 22,-48 L22,-76 Q22,-84 30,-84Z", SKY))
    o.append(eye(52, -62, 12, (.35, .05)) + eye(80, -62, 12, (.35, .05)))
    o.append(smile(126, -8, 22, 8, 4.5) + cheek(108, 0, 6))
    o.append(P("M-86,-90 L-62,-90 L-62,-72 L-44,-72 L-44,-48 L-62,-48 L-62,-30 L-86,-30 L-86,-48 L-104,-48 L-104,-72 L-86,-72Z", RED))
    o.append(P(rrect(28, -110, 56, 14, 7), "#FF5A5F") + C(42, -103, 5, "#FFE45C") + C(70, -103, 5, "#FFE45C"))
    o.append(E(140, -16, 4, 7, "#FFE45C"))
    o.append(wheel_flat(-90, 32, 27) + wheel_flat(92, 32, 27))
    return "".join(o)


def c_garbage_truck():
    o = [floor(0, 62, 172)]
    bd = "M-104,-100 Q-104,-118 -86,-118 L66,-118 Q84,-118 84,-100 L84,14 L-104,14Z"
    o.append(P(bd, YEL) + inside(bd, R(-200, -30, 400, 10, GREEN)))
    o.append(shine(-90, -110, 120))
    o.append(P("M-100,-114 L-126,-114 Q-162,-114 -170,-76 L-180,-30 L-180,10 Q-180,20 -170,20 L-100,20Z", "#F2B01E"))
    mouth = "M-176,-40 Q-174,-64 -150,-64 L-116,-64 L-116,10 L-176,10Z"
    o.append(P(mouth, DARK) + inside(mouth, bag(-158, -10, 19, "#7CC3F0"), bag(-128, -6, 17, WHITE), bag(-142, -38, 16, "#FFE066")))
    o.append(R(-140, 10, 312, 12, DARK, 4))
    cab = "M88,-100 Q88,-112 102,-112 L138,-112 Q152,-112 158,-96 L170,-56 L172,-40 L172,18 Q172,30 160,30 L88,30Z"
    o.append(P(cab, YEL) + inside(cab, R(80, -30, 100, 10, GREEN)))
    o.append(P("M98,-104 L136,-104 Q146,-104 150,-94 L160,-60 L98,-60Z", SKY))
    o.append(eye(114, -82, 11, (.35, .05)) + eye(140, -82, 11, (.35, .05)))
    o.append(smile(150, -6, 20, 7, 4) + cheek(132, 0, 6))
    o.append(P(rrect(106, -124, 34, 10, 5), ORANGE) + E(170, -18, 4, 8, "#FFE45C"))
    o.append(wheel_flat(-70, 32, 26) + wheel_flat(122, 32, 26))
    return "".join(o)


def c_truck():
    o = [floor(0, 62, 172)]
    o.append(R(-170, 8, 330, 14, DARK, 4))
    o.append(P(rrect(-172, -124, 248, 128, 14), "#EEF2F6") + R(-172, -12, 248, 10, ORANGE))
    o.append(shine(-150, -114, 140))
    cab = "M84,-104 Q84,-116 98,-116 L160,-116 Q172,-116 172,-104 L174,-40 L174,18 Q174,30 162,30 L84,30Z"
    o.append(P(cab, BLUE) + shine(98, -110, 50))
    o.append(P(rrect(96, -104, 72, 46, 12), SKY))
    o.append(eye(118, -80, 12, (.35, .05)) + eye(148, -80, 12, (.35, .05)))
    o.append(smile(150, -18, 22, 8, 4.5) + cheek(130, -10, 7))
    o.append(E(172, 4, 4, 8, "#FFE45C"))
    o.append(wheel_flat(-136, 32, 26) + wheel_flat(-80, 32, 26) + wheel_flat(124, 32, 26))
    return "".join(o)


def c_excavator():
    o = [floor(-10, 86, 150)]
    o.append(P(rrect(-150, 38, 220, 46, 23), DARK) + "".join(C(x, 61, 10, "#5A5F6A") for x in (-124, -90, -56, -22, 12, 44)))
    o.append(P(rrect(-152, -30, 210, 62, 14), YEL) + shine(-136, -22, 90))
    o.append(P(rrect(-8, -124, 70, 98, 12), YEL) + P(rrect(0, -114, 54, 74, 10), SKY))
    o.append(eye(15, -88, 10, (.35, .05)) + eye(40, -88, 10, (.35, .05)))
    o.append(smile(28, -64, 18, 6, 4) + cheek(8, -62, 5) + cheek(48, -62, 5))
    o.append(L("M48,-12 L120,-136", YEL, 30) + L("M120,-136 L156,-28", YEL, 22))
    o.append(C(120, -136, 8, "#E0A100"))
    o.append(P("M146,-34 Q178,-42 196,-14 L196,30 Q196,42 184,40 L140,30 Q156,8 146,-34Z", "#6B717C"))
    o.append(P("M142,30 L150,42 L158,32 L166,44 L174,34 L182,44 L190,36 L184,40Z", "#6B717C"))
    return "".join(o)


def c_balloon():
    env = ("M0,-178 C70,-178 118,-128 118,-66 C118,-10 76,34 40,66 C30,76 24,86 22,98 L-22,98 "
           "C-24,86 -30,76 -40,66 C-76,34 -118,-10 -118,-66 C-118,-128 -70,-178 0,-178Z")
    cols = [RED, YEL, BLUE, GREEN, ORANGE, "#9B4DDB", RED, YEL, BLUE]
    g = []
    n = 7
    for i in range(n):
        t0, t1 = -1 + 2 * i / n, -1 + 2 * (i + 1) / n
        g.append(P(f"M{f1(t0 * 22)},98 C{f1(t0 * 80)},40 {f1(t0 * 150)},-40 {f1(t0 * 128)},-110 C{f1(t0 * 110)},-160 {f1(t0 * 40)},-180 0,-180 "
                   f"C{f1(t1 * 40)},-180 {f1(t1 * 110)},-160 {f1(t1 * 128)},-110 C{f1(t1 * 150)},-40 {f1(t1 * 80)},40 {f1(t1 * 22)},98Z", cols[i]))
    o = [inside(env, *g), E(-62, -110, 12, 26, WHITE, 'opacity=".5" transform="rotate(25 -62 -110)"')]
    o.append(L("M-21,100 L-26,140 M21,100 L26,140", "#8A5A2A", 3))
    o.append(P("M-32,136 L32,136 L27,184 Q26,190 20,190 L-20,190 Q-26,190 -27,184Z", "#C98A4A") + P(rrect(-36, 132, 72, 12, 6), "#9A6430"))
    o.append(floor(0, 194, 46))
    return "".join(o)


def c_rocket():
    o = []
    for cx, cy, r in ((-66, 178, 32), (66, 178, 32), (-30, 188, 30), (30, 188, 30), (0, 182, 28)):
        o.append(C(cx, cy, r, "#E3E8EE"))
    o.append(P("M-30,110 C-28,140 -16,160 0,186 C16,160 28,140 30,110Z", ORANGE) + P("M-15,110 C-13,128 -6,142 0,156 C6,142 13,128 15,110Z", "#FFE45C"))
    o.append(P("M-30,100 L30,100 L36,118 L-36,118Z", "#6B717C"))
    o.append(P("M-44,40 C-72,60 -88,90 -90,128 Q-90,134 -84,132 L-44,104Z M44,40 C72,60 88,90 90,128 Q90,134 84,132 L44,104Z", RED))
    o.append(P("M0,-188 C30,-160 44,-110 44,-50 L44,104 L-44,104 L-44,-50 C-44,-110 -30,-160 0,-188Z", "#F4F7FA"))
    o.append(P("M0,-188 C22,-168 34,-138 39,-110 L-39,-110 C-34,-138 -22,-168 0,-188Z", RED))
    o.append(R(-44, 78, 88, 12, RED) + R(-30, -98, 10, 150, WHITE, 5, 'opacity=".0"'))
    o.append(R(-34, -96, 9, 150, "#DCE3EA", 4.5))
    o.append(C(0, -40, 23, "#9AA5B1") + C(0, -40, 16, "#5BB8F0") + E(-6, -46, 5, 3.4, WHITE, 'opacity=".8"'))
    return "".join(o)


def c_stroller():
    base = "#F06C9B"
    o = [floor(0, 110, 120)]
    o.append(L("M-100,-122 L-62,16 L-96,80 M-62,16 L80,86 M-62,16 L64,16", "#8C96A2", 9))
    o.append(L("M-114,-130 L-92,-118", DARK, 12))
    o.append(P("M-50,30 L56,30 L48,58 L-40,58Z", "#5A5F6A"))
    o.append(P("M-70,-36 C-60,-20 -40,-8 0,-6 L60,-8 C80,-8 90,0 90,10 C90,24 80,28 64,28 L-40,28 C-62,28 -74,10 -76,-12Z", base))
    o.append(P("M-82,-34 C-90,-80 -70,-120 -20,-128 C30,-132 66,-110 72,-70 C60,-74 40,-72 20,-60 C0,-48 -30,-38 -82,-34Z", base))
    o.append(L("M-60,-44 C-50,-90 -24,-116 -6,-122 M-26,-44 C-8,-84 18,-108 38,-114", "#D9507F", 5))
    o.append(E(-40, -108, 14, 6, WHITE, 'opacity=".45" transform="rotate(-30 -40 -108)"'))
    o.append(L("M78,-6 C92,-20 98,-30 94,-40", DARK, 8))
    o.append(wheel_flat(-96, 80, 27) + wheel_flat(80, 86, 21))
    return "".join(o)


CARTOON = {
    "car": (c_car, (-130, -80, 130, 66)),
    "bus": (c_bus, (-170, -126, 170, 68)),
    "taxi": (c_taxi, (-130, -104, 130, 66)),
    "scooter": (c_scooter, (-150, -144, 140, 84)),
    "bicycle": (c_bicycle, (-166, -108, 166, 108)),
    "train": (c_train, (-182, -194, 182, 76)),
    "mrt": (c_mrt, (-180, -110, 180, 66)),
    "hsr": (c_hsr, (-184, -84, 184, 58)),
    "airplane": (c_airplane, (-182, -120, 184, 90)),
    "helicopter": (c_helicopter, (-178, -104, 198, 100)),
    "boat": (c_boat, (-190, -132, 190, 92)),
    "fire_truck": (c_fire_truck, (-180, -134, 180, 70)),
    "ambulance": (c_ambulance, (-150, -112, 150, 68)),
    "police_car": (c_police, (-130, -94, 130, 66)),
    "garbage_truck": (c_garbage_truck, (-184, -126, 176, 70)),
    "truck": (c_truck, (-180, -128, 180, 70)),
    "excavator": (c_excavator, (-160, -150, 200, 94)),
    "hot_air_balloon": (c_balloon, (-124, -184, 124, 202)),
    "rocket": (c_rocket, (-150, -194, 150, 220)),
    "stroller": (c_stroller, (-130, -136, 130, 118)),
}

if __name__ == "__main__":
    only = set(sys.argv[1:]) or None
    write_deck("vehicles", REAL, CARTOON, only)

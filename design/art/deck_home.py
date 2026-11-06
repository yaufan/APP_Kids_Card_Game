"""家裡的東西 deck (20 cards): realistic <id>.svg and cartoon <id>_cartoon.svg.

    python3 deck_home.py              # all cards
    python3 deck_home.py cup bowl     # only these

Light from the top left. 電話 is a mobile phone, 筷子 a pair of chopsticks, 床 a child's bed.
"""
import math
import sys

from kit_vh import (C, E, L, P, R, Cam, band, blob, cheek, chrome, cuboid, dk, ell, extrude, eye, f1, face, glow, ground,
                    inside, lg, lt, number, pbox, poly, rg, round_rect_xz, rrect, scene, shade, smile, specks, write_deck)


def rot(svg, a, cx=0, cy=0):
    return f'<g transform="rotate({a} {cx} {cy})">{svg}</g>'


def hband(x0, x1, color, op, mid=.5, spread=.5):
    """Horizontal gradient stops: a soft vertical stripe of light (or dark)."""
    return lg(band(0, 0, 1, 0, color, op, mid, spread), x0, 0, x1, 0, user=True)


def handset(cx, cy, s, color, a=0):
    """The classic phone-receiver icon."""
    d = ("M-9,-8 C-7,-10 -4,-10 -3,-8 L-1,-4 C0,-2 -1,0 -2,1 L-3,2 C-2,5 1,8 4,9 L5,8 C6,7 8,6 10,7 L13,9 "
         "C15,10 15,13 13,15 L11,17 C8,19 2,17 -4,11 C-10,5 -12,-2 -9,-8Z")
    return f'<path transform="translate({f1(cx)} {f1(cy)}) rotate({a}) scale({s}) translate(-2 -4)" d="{d}" fill="{color}"/>'


# ================================================================ realistic
def cup(color="#4F8DB8"):
    """A ceramic mug (the approved mockup mug, gradients only)."""
    rx, ry, top, bot = 50, 11, -58, 58
    bodyd = f"M{-rx},{top} L{-rx + 3},{bot} A{rx - 3},{ry - 1} 0 0 0 {rx - 3},{bot} L{rx},{top} A{rx},{ry} 0 0 1 {-rx},{top}Z"
    o = [ground(14, bot + 9, 74, 9, .26)]
    handle = "M46,-34 C92,-42 94,30 44,30"
    o.append(L(handle, dk(color, .3), 15) + L(handle, color, 10, 'transform="translate(-1 -1.5)"'))
    o.append(L("M56,-35 C84,-36 86,14 68,22", lt(color, .5), 2.6, 'opacity=".7"'))
    inner = [P(bodyd, lg([(0, dk(color, .35)), (.1, dk(color, .1)), (.28, lt(color, .45)), (.4, lt(color, .2)), (.7, color), (.92, dk(color, .25)), (1, dk(color, .45))], 0, 0, 1, 0)),
             R(-38, top, 22, bot - top + 12, hband(-38, -16, "#FFFFFF", .45)),
             R(-60, top, 120, bot - top + 14, lg([(0, "#0E1E2A", 0), (.6, "#0E1E2A", 0), (1, "#0E1E2A", .35)])),
             R(28, top, 14, bot - top + 12, hband(28, 42, "#FFFFFF", .14)),
             specks((-50, top - 12, 50, bot + 12), .07, 41)]
    o.append(inside(bodyd, *inner))
    o.append(E(0, top, rx, ry, lt(color, .7)))
    ind = f"M{-rx + 4},{top + .6} A{rx - 4},{ry - 2.2} 0 0 1 {rx - 4},{top + .6} A{rx - 4},{ry - 2.2} 0 0 1 {-rx + 4},{top + .6}Z"
    o.append(P(ind, lg([(0, lt(color, .25)), (.5, color), (1, dk(color, .35))])))
    o.append(inside(ind, glow(0, top + 9, rx, 7, dk(color, .55), .6), glow(-26, top - 3, 18, 4, "#FFFFFF", .3)))
    o.append(L(f"M{-rx},{top} A{rx},{ry} 0 0 0 {rx},{top}", "#FFFFFF", 1.4, 'opacity=".85"'))
    return f'<g transform="translate(-16 0)">{"".join(o)}</g>'


def bowl():
    """A white porcelain rice bowl with a blue band, seen a little from above."""
    o = [ground(0, 76, 100, 12, .25)]
    rim = ell(0, -40, 130, 34)
    o.append(P(rim, rg([(0, "#E9EDF0"), (.55, "#D4DADF"), (.85, "#AEB6BD"), (1, "#8C949C")], cx=.5, cy=.78, r=.62)))
    o.append(inside(rim, glow(0, -62, 110, 22, "#FFFFFF", .55), glow(-60, -40, 40, 18, "#FFFFFF", .3)))
    body = ("M-130,-40 C-128,10 -92,46 -50,56 L-48,70 L48,70 L50,56 C92,46 128,10 130,-40 "
            "A130,34 0 0 1 -130,-40Z")
    o.append(P(body, lg([(0, "#9AA3AB"), (.12, "#D9DEE2"), (.32, "#FFFFFF"), (.55, "#F2F4F6"), (.85, "#C5CCD2"), (1, "#8C949C")], 0, 0, 1, 0)))
    blue = "#2A5DB0"
    deco = [P("M-140,-34 A140,40 0 0 0 140,-34 L140,-22 A140,40 0 0 1 -140,-22Z", blue, 'opacity=".9"'),
            P("M-140,-14 A140,40 0 0 0 140,-14 L140,-10 A140,40 0 0 1 -140,-10Z", blue, 'opacity=".8"')]
    for i in range(-5, 6):
        x = i * 22
        y = -40 + 34 * math.sqrt(max(0, 1 - (x / 130) ** 2)) + 30
        deco.append(E(x, y, 5.5 * math.sqrt(max(.2, 1 - (x / 130) ** 2)), 4, blue, 'opacity=".85"'))
    deco += [R(-140, 30, 280, 40, lg([(0, "#000000", 0), (1, "#000000", .18)])), specks((-130, -40, 130, 70), .05, 42)]
    o.append(inside(body, *deco))
    o.append(P("M-48,62 L48,62 L48,70 C30,74 -30,74 -48,70Z", lg([(0, "#B4BCC3"), (1, "#7C858E")])))
    o.append(L("M-130,-40 A130,34 0 0 0 130,-40", "#FFFFFF", 2.4))
    o.append(L("M-128,-44 A128,32 0 0 1 128,-44", "#C5CCD2", 1.6, 'opacity=".8"'))
    return "".join(o)


def spoon():
    """A stainless steel spoon, lying at a slant."""
    o = []
    hand = "M-170,-10 C-176,-10 -180,-5 -180,0 C-180,5 -176,10 -170,10 C-110,12 -40,8 0,4 C10,3 18,6 24,10 L24,-10 C18,-6 10,-3 0,-4 C-40,-8 -110,-12 -170,-10Z"
    bowl = ell(74, 0, 58, 36)
    o.append(P(hand, lg([(0, "#F4F6F8"), (.35, "#C2C8CE"), (.5, "#7E868E"), (.65, "#B4BBC2"), (1, "#E6EAED")])))
    o.append(inside(hand, R(-180, -12, 210, 5, "#FFFFFF", 0, 'opacity=".5"'), glow(-150, 0, 40, 9, "#FFFFFF", .4)))
    o.append(P("M14,-12 C22,-24 40,-34 70,-36 L60,36 C40,34 22,24 14,12Z", "#9AA2AA"))
    o.append(P(bowl, lg([(0, "#E9EDF0"), (.5, "#B4BBC2"), (1, "#6E767E")], 0, 0, 0, 1)))
    o.append(P(ell(76, 1, 50, 30), rg([(0, "#5E666E"), (.45, "#8C949C"), (.8, "#D2D7DC"), (1, "#F4F6F8")], cx=.6, cy=.62, r=.7)))
    o.append(inside(ell(76, 1, 50, 30), glow(98, 14, 22, 9, "#FFFFFF", .7, -15), glow(52, -14, 18, 6, "#3A4148", .5, -15)))
    o.append(L("M30,-20 A56,34 0 0 1 120,-20", "#FFFFFF", 2.2, 'opacity=".7"'))
    return ground(-14, 92, 150, 10, .2) + rot("".join(o), -28, 0, 0)


def chopsticks():
    """A pair of bamboo chopsticks with dark tops."""
    def stick(y_off, a):
        w0, w1 = 10, 3.4          # half-widths at the top and at the tip
        top = f"M-165,{-w0} L{165},{-w1} L165,0 L-165,0Z"
        side = f"M-165,0 L165,0 L165,{w1} L-165,{w0}Z"
        g = [P(top, lg([(0, "#F2D7A6"), (1, "#D9B27A")])), P(side, lg([(0, "#B98A4E"), (1, "#8F6532")])),
             P(f"M-165,{-w0} L-70,{-w0 + (w0 - w1) * 95 / 330:.2f} L-70,{w0 - (w0 - w1) * 95 / 330:.2f} L-165,{w0}Z", "#5A2E1A", 'opacity=".92"'),
             L("M-60,-3 L150,-1", "#B98A4E", .8, 'opacity=".5"'), L("M-160,-4 L-74,-3", "#8A5A3A", .8, 'opacity=".6"'),
             R(-70, -8, 4, 16, "#C9A24A")]
        return f'<g transform="translate(0 {y_off}) rotate({a})">{"".join(g)}</g>'
    o = [ground(-6, 70, 160, 9, .18)]
    o.append(stick(-16, -27) + stick(16, -23))
    return "".join(o)


def plate():
    """A round white plate with a blue rim line, seen from above at a slant."""
    o = [ground(0, 64, 158, 14, .25)]
    o.append(E(0, 10, 150, 66, lg([(0, "#C9D0D6"), (1, "#8C949C")])))
    o.append(E(0, 0, 150, 66, rg([(0, "#FFFFFF"), (.7, "#F4F6F8"), (1, "#D2D8DD")], cy=.6)))
    o.append(E(0, 0, 141, 61, "none", 'stroke="#2A5DB0" stroke-width="3" opacity=".85"'))
    o.append(E(0, 5, 102, 42, lg([(0, "#BCC4CB"), (.4, "#E3E7EA"), (1, "#FFFFFF")])))
    o.append(E(0, 7, 96, 39, rg([(0, "#FFFFFF"), (.75, "#F2F4F6"), (1, "#DCE1E5")], cy=.55)))
    o.append(E(0, 7, 96, 39, "none", 'stroke="#2A5DB0" stroke-width="1.6" opacity=".5"'))
    o.append(glow(-60, -26, 50, 12, "#FFFFFF", .8, -8) + glow(50, 30, 40, 9, "#FFFFFF", .5, -8))
    o.append(L("M-150,0 A150,66 0 0 0 150,0", "#FFFFFF", 1.6, 'opacity=".9"'))
    return "".join(o)


def toothbrush():
    """A child's toothbrush with a dab of toothpaste."""
    o = [ground(0, 54, 170, 8, .18)]
    g = []
    hand = ("M-176,4 C-178,-8 -170,-14 -150,-14 C-110,-14 -80,-10 -50,-8 C-20,-6 10,-4 30,-3 C50,-2 60,-4 70,-6 "
            "L70,8 C60,7 50,7 30,7 C10,8 -20,10 -50,12 C-80,14 -110,18 -150,18 C-170,18 -176,14 -176,4Z")
    g.append(P(hand, lg([(0, "#8CC8F5"), (.4, "#2D86D8"), (1, "#14508F")])))
    g.append(inside(hand, R(-176, -12, 250, 5, "#FFFFFF", 0, 'opacity=".45"'),
                    P("M-150,-16 C-120,-16 -100,-12 -80,-10 L-80,16 C-100,16 -120,20 -150,20Z", lg([(0, "#9BE07A"), (.5, "#4CB04A"), (1, "#2A7A2A")]))))
    head = rrect(66, -10, 84, 20, 10)
    g.append(P(head, lg([(0, "#8CC8F5"), (.4, "#2D86D8"), (1, "#14508F")])))
    tufts = []
    for i in range(9):
        x = 72 + i * 8.6
        col = "#FFFFFF" if i % 3 else "#5FD0E8"
        tufts.append(P(rrect(x, -40, 7, 32, 3), lg([(0, lt(col, .2)), (1, dk(col, .18))], 0, 0, 1, 0)))
    g.append("".join(tufts))
    paste = ("M64,-40 C60,-52 70,-58 82,-54 C92,-64 108,-62 114,-54 C124,-62 140,-58 142,-48 C150,-46 152,-40 146,-38 L66,-38 C62,-38 62,-40 64,-40Z")
    g.append(P(paste, lg([(0, "#FFFFFF"), (1, "#D9E2E8")])))
    g.append(inside(paste, L("M64,-46 C80,-52 100,-44 120,-52 C130,-56 140,-52 150,-48", "#3DB8D8", 5, 'opacity=".85"'),
                    glow(84, -54, 12, 5, "#FFFFFF", .9)))
    o.append(rot("".join(g), -22))
    return "".join(o)


def towel():
    """A striped bath towel folded over a chrome rail."""
    base = "#5FAEDB"
    o = []
    o.append(R(-150, -128, 300, 12, chrome([(0, "#F4F6F8"), (.5, "#B4BCC3"), (1, "#7E868E")]), 6))
    o.append(R(-160, -134, 16, 24, "#9AA2AA", 4) + R(144, -134, 16, 24, "#9AA2AA", 4))
    back = "M-100,-118 L108,-118 L112,140 C60,146 -40,146 -96,140Z"
    o.append(P(back, dk(base, .25)))
    front = "M-110,-124 C-108,-132 108,-132 110,-124 L114,124 C70,132 30,126 0,130 C-30,134 -70,128 -112,124Z"
    folds = "".join(R(x, -130, 26, 270, hband(x, x + 26, "#FFFFFF" if k % 2 else "#0A2A44", .16 if k % 2 else .14))
                    for k, x in enumerate(range(-116, 116, 26)))
    stripes = (R(-120, 70, 240, 12, "#FFFFFF", 0, 'opacity=".95"') + R(-120, 88, 240, 5, "#FFFFFF", 0, 'opacity=".95"')
               + R(-120, 104, 240, 30, lt(base, .1)))
    inner = [P(front, lg([(0, lt(base, .25)), (.1, base), (.8, dk(base, .08)), (1, dk(base, .2))])), folds, stripes,
             R(-120, -132, 240, 22, lg([(0, "#FFFFFF", .35), (1, "#FFFFFF", 0)])),
             specks((-120, -132, 120, 140), .22, 43, tile=24, n=40, r=(.6, 1.3)),
             shade((-114, -132, 116, 140), "#0A2A44", left=.25, right=.3, w=.1)]
    o.append(inside(front, *inner))
    o.append(R(-150, -128, 300, 5, "#FFFFFF", 2.5, 'opacity=".6"'))
    return "".join(o)


def soap():
    """A pink bar of soap with bubbles."""
    cam = Cam(yaw=18, pitch=40)
    base = "#F48FB1"
    outline = round_rect_xz(-110, -60, 110, 60, 46, 8)
    sides, top = extrude(cam, outline, 0, 44, base)
    o = [sides]
    o.append(inside(top, P(top, rg([(0, lt(base, .55)), (.6, lt(base, .25)), (1, base)], cx=.42, cy=.42, r=.65)),
                    specks(pbox(top), .08, 44)))
    eng = cam.poly([(x, 44, z) for x, z in round_rect_xz(-62, -28, 62, 28, 26, 6)])
    o.append(P(eng, "none", f'stroke="{dk(base, .2)}" stroke-width="3" opacity=".6"'))
    o.append(P(eng, "none", f'stroke="{lt(base, .6)}" stroke-width="1.4" opacity=".8" transform="translate(1.4 1.4)"'))
    bx = cam.box(0)
    gr = ground((bx[0] + bx[2]) / 2, bx[3] - 4, (bx[2] - bx[0]) * .55, 10, .25)
    # foam and bubbles
    foam = "".join(C(x, y, r, rg([(0, "#FFFFFF"), (.8, "#F3F6F8"), (1, "#C9D3DB")], cx=.4, cy=.35)) for x, y, r in
                   ((-70, -64, 18), (-48, -72, 16), (-86, -52, 14), (-56, -54, 15), (-30, -62, 12)))
    bub = []
    for x, y, r in ((40, -120, 26), (90, -96, 16), (-20, -128, 12), (120, -138, 10), (-100, -110, 14), (14, -82, 9)):
        bub.append(C(x, y, r, rg([(0, "#FFFFFF", 0), (.7, "#DDEFFF", .2), (.92, "#9FD3F5", .55), (1, "#C7B3F0", .8)])))
        bub.append(E(x - r * .35, y - r * .4, r * .32, r * .2, "#FFFFFF", f'opacity=".9" transform="rotate(-35 {f1(x - r * .35)} {f1(y - r * .4)})"'))
    o2 = gr + "".join(o) + foam + "".join(bub)
    xs = cam.xs + [-120, 140]
    ys = cam.ys + [-150]
    return o2, (min(xs) - 4, min(ys) - 4, max(xs) + 4, max(ys) + 14)


def comb():
    """A pink plastic comb: coarse teeth on one side, fine teeth on the other."""
    base = "#E05A92"
    spine = "M-160,-46 C-160,-58 -150,-62 -138,-62 L140,-62 C152,-62 160,-58 160,-46 L160,-22 L-160,-22Z"
    teeth = []
    x = -152
    while x < 150:
        w = 7 if x < 0 else 4.4
        gap = 5 if x < 0 else 3.4
        teeth.append(rrect(x, -26, w, 88, w / 2))
        x += w + gap
    t = " ".join(teeth)
    g = [ground(0, 76, 160, 8, .18)]
    g.append(P(t, lg([(0, base), (.6, lt(base, .15)), (1, lt(base, .35))])))
    g.append(inside(t, R(-160, -26, 320, 30, lg([(0, "#3A0A1E", .35), (1, "#3A0A1E", 0)]))))
    g.append(P(spine, lg([(0, lt(base, .5)), (.35, lt(base, .15)), (.7, base), (1, dk(base, .3))])))
    g.append(inside(spine, R(-160, -58, 320, 6, "#FFFFFF", 0, 'opacity=".55"'), specks((-160, -62, 160, -22), .07, 45)))
    return rot("".join(g), -8)


def chair():
    """A wooden chair seen from the front left, a little from above."""
    cam = Cam(yaw=-32, pitch=18)
    w = "#B9773C"
    S = 3
    lx0, lx1, lz0, lz1, t = -22 * S, 22 * S, -20 * S, 20 * S, 4 * S
    items = []
    for x in (lx0, lx1 - t):
        items.append((x, x + t, 0, 44 * S, lz0, lz0 + t, w))          # front legs
        items.append((x, x + t, 0, 92 * S, lz1 - t, lz1, w))          # back legs rising into the back
    items.append((lx0 + t, lx1 - t, 32 * S, 36 * S, lz0 + 1, lz0 + 3, dk(w, .1)))
    items.append((lx0 - 3, lx1 + 3, 44 * S, 48 * S, lz0 - 3, lz1, w))  # seat
    items.append((lx0 + t, lx1 - t, 80 * S, 90 * S, lz1 - t + 2, lz1 - 2, w))   # top rail
    items.append((lx0 + t, lx1 - t, 64 * S, 70 * S, lz1 - t + 3, lz1 - 3, w))   # middle rail
    body = scene(cam, items)
    bx = cam.box(0)
    gr = ground((bx[0] + bx[2]) / 2, bx[3] - 6, (bx[2] - bx[0]) * .6, 12, .25)
    return gr + body, cam.box(10)


def table():
    """A wooden table with four legs."""
    cam = Cam(yaw=-24, pitch=22)
    w = "#C48A4E"
    S = 2.2
    X, Z, H, t = 60 * S, 38 * S, 72 * S, 5 * S
    items = [(-X + 6, -X + 6 + t, 0, H - 4, -Z + 6, -Z + 6 + t, dk(w, .05)), (X - 6 - t, X - 6, 0, H - 4, -Z + 6, -Z + 6 + t, dk(w, .05)),
             (-X + 6, -X + 6 + t, 0, H - 4, Z - 6 - t, Z - 6, dk(w, .05)), (X - 6 - t, X - 6, 0, H - 4, Z - 6 - t, Z - 6, dk(w, .05))]
    items.append((-X + 6, X - 6, H - 14, H - 4, -Z + 7, -Z + 9, dk(w, .12)))
    legs = scene(cam, items[1:])
    top = cuboid(cam, -X, X, H - 4, H + 6, -Z, Z, w)
    tp = cam.poly([(-X, H + 6, -Z), (X, H + 6, -Z), (X, H + 6, Z), (-X, H + 6, Z)])
    grain = inside(tp, L(" ".join(f"M-400,{y} C-100,{y + 6} 100,{y - 6} 400,{y}" for y in range(-200, 100, 9)), dk(w, .2), 1, 'opacity=".25" transform="rotate(-12)"'),
                   glow(*cam.p(-X * .3, H + 6, -Z * .2), 120, 40, "#FFFFFF", .3, -10))
    bx = cam.box(0)
    gr = ground((bx[0] + bx[2]) / 2, bx[3] - 6, (bx[2] - bx[0]) * .58, 14, .25)
    front_leg = cuboid(cam, *items[0][:6], items[0][6])
    return gr + legs + top + grain + front_leg, cam.box(10)


def bed():
    """A child's wooden bed seen from the foot end: rounded headboard, pillow, blue blanket."""
    cam = Cam(yaw=26, pitch=26)
    wood = "#D9A66A"
    S = 2.0
    Lx, Wz, t = 150 * S, 80 * S, 6 * S
    o = []
    # headboard (far end) as an arched slab
    arch = ([(Wz, 0)] + [(Wz * (0.5 + 0.5 * math.cos(math.radians(a))), 70 * S + 26 * S * math.sin(math.radians(a))) for a in range(0, 181, 12)]
            + [(0, 0)])
    edge = [cam.poly([(0, y0, z0), (t, y0, z0), (t, y1, z1), (0, y1, z1)]) for (z0, y0), (z1, y1) in zip(arch, arch[1:])]
    o.append(P(" ".join(edge), cam.tone(wood, (0, 1, 0))))
    front = cam.poly([(t, y, z) for z, y in arch])
    o.append(P(front, lg([(0, lt(wood, .2)), (1, dk(wood, .15))])))
    o.append(inside(front, specks(pbox(front), .06, 55)))
    o.append(P(cam.poly([(t + .5, y, z) for z, y in [(Wz * (0.5 + 0.38 * math.cos(math.radians(a))), 72 * S + 14 * S * math.sin(math.radians(a))) for a in range(0, 181, 15)]]),
               "none", f'stroke="{dk(wood, .25)}" stroke-width="3" opacity=".5"'))
    # far side rail, mattress, near side rail
    o.append(cuboid(cam, t, Lx - t, 12 * S, 30 * S, Wz - 4 * S, Wz, wood))
    o.append(cuboid(cam, t, Lx - t, 26 * S, 44 * S, 3 * S, Wz - 3 * S, "#EEF2F5"))
    o.append(cuboid(cam, t, Lx - t, 12 * S, 30 * S, 0, 4 * S, wood))
    # pillow by the headboard
    pc = [cam.p(x, 50 * S, z) for x, z in ((10 * S, 10 * S), (44 * S, 8 * S), (46 * S, Wz - 8 * S), (12 * S, Wz - 10 * S))]
    mid = [((a[0] + b[0]) / 2 + dx, (a[1] + b[1]) / 2 + dy) for (a, b), (dx, dy) in zip(zip(pc, pc[1:] + pc[:1]), ((0, 8), (8, 0), (0, -12), (-8, 0)))]
    pil = blob([pc[0], mid[0], pc[1], mid[1], pc[2], mid[2], pc[3], mid[3]])
    o.append(P(pil, rg([(0, "#FFFFFF"), (.6, "#F2F5F8"), (1, "#AEB8C2")], cx=.45, cy=.4)))
    o.append(inside(pil, glow((pc[0][0] + pc[2][0]) / 2, (pc[0][1] + pc[2][1]) / 2 - 6, 44, 14, "#FFFFFF", .8)))
    # blanket over the foot half, hanging down the near side, with the sheet folded over its top edge
    blue = "#4F8FD6"
    x0b, x1b = 62 * S, Lx - t
    o.append(cuboid(cam, x0b, x1b, 44 * S, 48 * S, -1 * S, Wz + 1 * S, blue))
    o.append(cuboid(cam, x0b, x1b, 20 * S, 48 * S, -3 * S, -1 * S, blue))
    top = cam.poly([(x0b, 48 * S, -1 * S), (x1b, 48 * S, -1 * S), (x1b, 48 * S, Wz + S), (x0b, 48 * S, Wz + S)])
    o.append(inside(top, specks(pbox(top), .1, 47), glow(*cam.p(x0b + 40 * S, 48 * S, 30 * S), 90, 30, "#FFFFFF", .25)))
    fr = cam.poly([(x0b, 20 * S, -3 * S), (x1b, 20 * S, -3 * S), (x1b, 48 * S, -3 * S), (x0b, 48 * S, -3 * S)])
    o.append(inside(fr, specks(pbox(fr), .1, 48), R(-400, -400, 800, 800, lg([(0, "#000000", 0), (1, "#000000", .15)]))))
    o.append(cuboid(cam, x0b, x0b + 12 * S, 44 * S, 49 * S, -1 * S, Wz + 1 * S, "#F4F6F8"))
    o.append(cuboid(cam, x0b, x0b + 12 * S, 20 * S, 49 * S, -4 * S, -1 * S, "#F4F6F8"))
    # head-end leg and footboard (nearest)
    o.append(cuboid(cam, 0, t, 0, 30 * S, 0, 4 * S, dk(wood, .05)))
    o.append(cuboid(cam, Lx - t, Lx, 0, 54 * S, 0, Wz, wood, extra=lambda n, d: inside(d, specks(pbox(d), .06, 56)) if n[0] else ""))
    bx = cam.box(0)
    gr = ground((bx[0] + bx[2]) / 2, bx[3] - 10, (bx[2] - bx[0]) * .55, 18, .25)
    return gr + "".join(o), cam.box(10)


def pillow():
    """A soft pillow in a pale blue case."""
    base = "#BFD9F0"
    d = blob([(-150, -64), (-70, -76), (0, -70), (80, -84), (156, -80), (146, -10), (156, 60), (80, 66), (0, 72), (-80, 64), (-156, 74), (-146, 0)], 10)
    o = [ground(0, 86, 160, 12, .22)]
    inner = [P(d, rg([(0, lt(base, .75)), (.5, lt(base, .3)), (.85, base), (1, dk(base, .25))], cx=.45, cy=.42, r=.62)),
             glow(-40, -34, 70, 26, "#FFFFFF", .55, -6),
             L("M-150,-64 C-126,-50 -112,-40 -100,-34 M156,-80 C132,-64 120,-56 106,-50 M156,60 C130,48 118,40 104,34 M-156,74 C-132,60 -118,52 -104,44",
               dk(base, .25), 3, 'opacity=".45"'),
             specks((-160, -90, 160, 80), .07, 49),
             R(-160, 30, 320, 50, lg([(0, "#1C3A5A", 0), (1, "#1C3A5A", .22)]))]
    o.append(inside(d, *inner))
    o.append(P(d, "none", f'stroke="{lt(base, .55)}" stroke-width="3" opacity=".9"'))
    return "".join(o)


def clock():
    """A round wall clock with a wooden frame, numbers 1 to 12, hands at ten past ten."""
    o = [ground(0, 166, 110, 8, .14)]
    o.append(C(0, 0, 152, rg([(0, "#A86A3C"), (.85, "#8A5230"), (.93, "#6E3E22"), (1, "#4A2814")])))
    o.append(C(0, 0, 152, lg([(0, "#FFFFFF", .3), (.5, "#FFFFFF", 0), (1, "#000000", .2)])))
    o.append(C(0, 0, 132, lg([(0, "#5A3018"), (1, "#C08850")])))
    o.append(C(0, 0, 126, rg([(0, "#FFFFFF"), (.8, "#FAF8F4"), (1, "#E2DDD4")])))
    ticks = []
    for i in range(60):
        a = math.radians(i * 6)
        r0 = 108 if i % 5 else 100
        ticks.append(f"M{f1(math.sin(a) * r0)},{f1(-math.cos(a) * r0)} L{f1(math.sin(a) * 118)},{f1(-math.cos(a) * 118)}")
    o.append(L(" ".join(t for i, t in enumerate(ticks) if i % 5), "#5A5048", 1.4, cap="butt"))
    o.append(L(" ".join(t for i, t in enumerate(ticks) if not i % 5), "#2A2420", 4, cap="butt"))
    for h in range(1, 13):
        a = math.radians(h * 30)
        o.append(number(str(h), math.sin(a) * 80, -math.cos(a) * 80, 22, "#2A2420", 3.4))
    def hand(angle, ln, w, col, tail=14):
        a = math.radians(angle)
        sx, sy = math.sin(a), -math.cos(a)
        px, py = -sy, sx
        pts = [(-sx * tail + px * w * .6, -sy * tail + py * w * .6), (sx * ln + px * w * .25, sy * ln + py * w * .25), (sx * (ln + 6), sy * (ln + 6)),
               (sx * ln - px * w * .25, sy * ln - py * w * .25), (-sx * tail - px * w * .6, -sy * tail - py * w * .6)]
        return P(poly(pts), col)
    o.append(f'<g transform="translate(3 4)" opacity=".18">{hand(305, 62, 12, "#000")}{hand(60, 92, 9, "#000")}</g>')
    o.append(hand(305, 62, 12, "#1E1A18") + hand(60, 92, 9, "#1E1A18"))
    o.append(L("M-18,30 L52,-96", "#D32F2F", 2.2) + C(0, 0, 8, "#1E1A18") + C(0, 0, 4, "#D32F2F"))
    o.append(P("M-112,-30 C-104,-80 -60,-114 -10,-118 C-60,-104 -92,-74 -100,-26Z", "#FFFFFF", 'opacity=".45"'))
    return "".join(o)


def phone():
    """A smartphone with an incoming call: a picture of someone, a red and a green button."""
    o = [ground(10, 176, 90, 9, .2)]
    g = []
    g.append(P(rrect(-84, -168, 168, 336, 30), lg([(0, "#6E747C"), (.08, "#2A2D33"), (.9, "#1A1C20"), (1, "#4A4E55")], 0, 0, 1, 0)))
    g.append(R(84, -90, 4, 40, "#3A3D42", 2) + R(-88, -100, 4, 24, "#3A3D42", 2) + R(-88, -66, 4, 40, "#3A3D42", 2))
    scr = rrect(-76, -160, 152, 320, 24)
    g.append(P(scr, lg([(0, "#6AA8E8"), (.5, "#7B7FD8"), (1, "#3A4FA8")])))
    g.append(P(rrect(-22, -152, 44, 12, 6), "#0E0F12"))
    g.append(C(0, -70, 36, lg([(0, "#FFFFFF", .95), (1, "#E6ECF5", .95)])))
    g.append(C(0, -80, 13, "#9AA8C0") + P("M-24,-48 C-22,-64 -12,-66 0,-66 C12,-66 22,-64 24,-48 C14,-40 -14,-40 -24,-48Z", "#9AA8C0"))
    g.append(R(-40, -20, 80, 8, "#FFFFFF", 4, 'opacity=".9"') + R(-26, -4, 52, 6, "#FFFFFF", 3, 'opacity=".6"'))
    g.append(C(-40, 104, 24, rg([(0, "#FF7A70"), (1, "#E0302A")], cx=.4, cy=.35)) + handset(-40, 106, 1.25, "#FFFFFF", 135))
    g.append(C(40, 104, 24, rg([(0, "#7BE08A"), (1, "#2EAF4A")], cx=.4, cy=.35)) + handset(40, 104, 1.25, "#FFFFFF", 0))
    g.append(R(-30, 146, 60, 4, "#FFFFFF", 2, 'opacity=".8"'))
    g.append(inside(scr, P("M-80,-170 L20,-170 L-80,40Z", "#FFFFFF", 'opacity=".12"')))
    o.append(rot("".join(g), -8))
    return "".join(o)


def tv():
    """A flat-screen TV on a stand, showing a sunny hill."""
    o = [ground(0, 132, 130, 8, .22)]
    o.append(P("M-16,86 L16,86 L20,112 L-20,112Z", lg([(0, "#3A3D42"), (1, "#16181B")], 0, 0, 1, 0)))
    o.append(P("M-80,112 C-80,106 -74,104 -66,104 L66,104 C74,104 80,106 80,112 L80,118 L-80,118Z", lg([(0, "#55595F"), (1, "#1A1C20")])))
    o.append(P(rrect(-176, -118, 352, 210, 8), lg([(0, "#3A3D42"), (.1, "#1E2024"), (1, "#0E0F11")])))
    scr = "M-166,-108 L166,-108 L166,76 L-166,76Z"
    sc = [P(scr, lg([(0, "#3E8EDC"), (.6, "#8CC8F0"), (1, "#C8E8F8")])),
          C(110, -60, 26, rg([(0, "#FFF7C0"), (.6, "#FFD93A"), (1, "#FFB400")])), glow(110, -60, 56, 56, "#FFE680", .5),
          P("M-90,-62 C-90,-74 -70,-80 -60,-70 C-52,-86 -24,-84 -20,-66 C-8,-66 -4,-50 -18,-48 L-84,-48 C-96,-48 -98,-60 -90,-62Z", "#FFFFFF", 'opacity=".95"'),
          P("M-170,20 C-120,-20 -60,-10 -10,20 C40,-6 110,-30 170,10 L170,80 L-170,80Z", lg([(0, "#7DCB5A"), (1, "#3E8E2E")])),
          P("M-170,50 C-100,20 -20,30 40,56 C90,40 140,36 170,46 L170,80 L-170,80Z", lg([(0, "#5DB548"), (1, "#2A6E22")])),
          P("M-166,-108 L-40,-108 L-140,76 L-166,76Z", "#FFFFFF", 'opacity=".1"')]
    o.append(inside(scr, *sc))
    o.append(C(160, 84, 2, "#E04040"))
    return "".join(o)


def lamp():
    """A table lamp, switched on: a fabric shade glowing warm, a round ceramic base."""
    o = [glow(0, -20, 170, 150, "#FFE7A0", .45), ground(0, 168, 90, 9, .22)]
    o.append(P("M-66,150 C-66,140 -40,136 0,136 C40,136 66,140 66,150 L66,156 C66,162 40,166 0,166 C-40,166 -66,162 -66,156Z",
               lg([(0, "#8A6A48"), (1, "#4A3420")])))
    base = "M-12,136 C-56,132 -78,100 -76,68 C-74,36 -50,14 -22,8 L-14,-4 L14,-4 L22,8 C50,14 74,36 76,68 C78,100 56,132 12,136Z"
    o.append(P(base, lg([(0, "#4E7E78"), (.3, "#7FB3AC"), (.45, "#A8D3CC"), (.7, "#5E948C"), (1, "#2E5650")], 0, 0, 1, 0)))
    o.append(inside(base, glow(-30, 50, 16, 40, "#FFFFFF", .5), specks((-80, -10, 80, 140), .06, 50)))
    o.append(R(-5, -40, 10, 40, chrome([(0, "#E8C66A"), (.5, "#B8862A"), (1, "#E0B85A")])))
    o.append(glow(0, -36, 46, 20, "#FFFBE0", .95))
    shade_ = "M-56,-160 L56,-160 L104,-40 C104,-30 60,-24 0,-24 C-60,-24 -104,-30 -104,-40Z"
    o.append(P(shade_, lg([(0, "#E6D2AE"), (.2, "#FFF4DC"), (.45, "#FFF8E8"), (.8, "#F0DDB8"), (1, "#CDB48A")], 0, 0, 1, 0)))
    o.append(inside(shade_, R(-110, -80, 220, 60, lg([(0, "#FFE9A8", 0), (1, "#FFE9A8", .7)])), specks((-110, -160, 110, -20), .07, 51),
                    L(" ".join(f"M{x * .5},-160 L{x},-30" for x in range(-100, 101, 25)), "#C9B088", 1, 'opacity=".35"')))
    o.append(E(0, -160, 56, 8, lg([(0, "#D9C49C"), (1, "#FFF2D6")])))
    o.append(P("M-104,-40 C-104,-30 -60,-24 0,-24 C60,-24 104,-30 104,-40 C104,-34 60,-30 0,-30 C-60,-30 -104,-34 -104,-40Z", "#FFFBEA"))
    return "".join(o)


def door():
    """A wooden panel door in its frame, with a lever handle."""
    wood = "#9E5F33"
    o = [R(-124, -196, 248, 392, lg([(0, "#F4F1EC"), (1, "#D8D2C8")], 0, 0, 1, 0), 4)]
    o.append(R(-124, -196, 248, 392, "none", 4, 'stroke="#BFB7AA" stroke-width="2"'))
    leaf = "M-104,-180 L104,-180 L104,192 L-104,192Z"
    inner = [P(leaf, lg([(0, lt(wood, .12)), (.5, wood), (1, dk(wood, .18))], 0, 0, 1, 0)),
             L(" ".join(f"M{x},-180 C{x + 3},-60 {x - 3},60 {x},192" for x in range(-100, 104, 9)), dk(wood, .3), 1.1, 'opacity=".35"'),
             specks((-104, -180, 104, 192), .07, 52)]
    for x, y, w, h in ((-84, -160, 72, 120), (12, -160, 72, 120), (-84, -12, 72, 186), (12, -12, 72, 186)):
        inner.append(R(x, y, w, h, dk(wood, .25)))
        inner.append(P(f"M{x},{y} L{x + w},{y} L{x + w - 10},{y + 10} L{x + 10},{y + 10} L{x + 10},{y + h - 10} L{x},{y + h}Z", lt(wood, .22)))
        inner.append(P(f"M{x + w},{y} L{x + w},{y + h} L{x},{y + h} L{x + 10},{y + h - 10} L{x + w - 10},{y + h - 10} L{x + w - 10},{y + 10}Z", dk(wood, .35)))
        inner.append(R(x + 10, y + 10, w - 20, h - 20, lg([(0, lt(wood, .08)), (1, dk(wood, .1))], 0, 0, 1, 0)))
    o.append(inside(leaf, *inner))
    o.append(R(-110, -186, 6, 380, "#B8AFA2") + R(104, -186, 6, 380, "#B8AFA2"))
    for y in (-150, 130):
        o.append(R(-108, y, 8, 30, chrome([(0, "#E8C66A"), (1, "#9A7020")]), 2))
    o.append(P(rrect(70, -6, 16, 50, 8), chrome([(0, "#F2DA90"), (.5, "#C99A3A"), (1, "#8A6418")])))
    o.append(P("M78,6 C60,4 40,6 34,10 C30,13 32,18 38,18 C46,18 62,16 80,16Z", lg([(0, "#F6E2A0"), (.5, "#D2A440"), (1, "#8A6418")])))
    o.append(C(78, 11, 7, rg([(0, "#FFF0C0"), (1, "#A87A20")])))
    o.append(C(78, 32, 3.4, "#3A2A10") + R(76.6, 32, 2.8, 7, "#3A2A10"))
    o.append(R(-128, 190, 256, 10, lg([(0, "#C9C2B6"), (1, "#8E8678")]), 3))
    return "".join(o)


def window():
    """A window with a white frame, blue sky outside and curtains on both sides."""
    o = []
    o.append(R(-140, -142, 280, 250, "#E9E4DC", 4))
    pane = rrect(-122, -124, 244, 214, 2)
    sky = [P(pane, lg([(0, "#4D9BE0"), (.7, "#9ED0F2"), (1, "#D6EEFA")])),
           P("M-100,-60 C-104,-76 -84,-86 -72,-76 C-64,-94 -30,-92 -26,-70 C-12,-72 -6,-54 -20,-50 L-92,-50 C-104,-50 -106,-58 -100,-60Z", "#FFFFFF"),
           P("M30,-10 C28,-22 42,-28 52,-22 C58,-34 82,-32 84,-16 C94,-16 98,-4 88,-2 L36,-2 C28,-2 26,-8 30,-10Z", "#FFFFFF", 'opacity=".9"'),
           P("M-122,70 C-80,50 -30,56 10,72 C50,56 100,52 122,62 L122,92 L-122,92Z", "#7CC46A"),
           P("M-122,-124 L-40,-124 L-122,20Z", "#FFFFFF", 'opacity=".18"'), P("M10,-124 L40,-124 L-60,92 L-90,92Z", "#FFFFFF", 'opacity=".12"')]
    o.append(inside(pane, *sky))
    o.append(R(-6, -124, 12, 214, lg([(0, "#FFFFFF"), (1, "#D6D0C6")], 0, 0, 1, 0)) + R(-122, -20, 244, 10, lg([(0, "#FFFFFF"), (1, "#D6D0C6")])))
    o.append(R(-122, -124, 244, 214, "none", 0, 'stroke="#FFFFFF" stroke-width="8"'))
    o.append(P("M-156,106 L156,106 L148,124 L-148,124Z", lg([(0, "#FFFFFF"), (1, "#C9C2B6")])))
    o.append(R(-156, 104, 312, 6, "#FFFFFF"))
    # curtains
    cur = "#E27D60"
    for sgn in (-1, 1):
        d = (f"M{sgn * 176},-150 L{sgn * 104},-150 C{sgn * 98},-100 {sgn * 104},-40 {sgn * 120},10 "
             f"C{sgn * 132},40 {sgn * 130},90 {sgn * 120},140 L{sgn * 176},140Z")
        g = [P(d, lg([(0, lt(cur, .1)), (1, dk(cur, .2))]))]
        for k, x in enumerate(range(100, 180, 14)):
            g.append(R(sgn * x - (14 if sgn > 0 else 0), -150, 14, 290, hband(sgn * x - (14 if sgn > 0 else 0), sgn * x + (0 if sgn > 0 else 14), "#FFFFFF" if k % 2 else "#4A1A10", .22)))
        g.append(specks((-180, -150, 180, 140), .08, 53))
        o.append(inside(d, *g))
        o.append(L(f"M{sgn * 112},14 C{sgn * 130},10 {sgn * 160},12 {sgn * 176},16", "#B8462E", 6))
    o.append(R(-186, -158, 372, 10, lg([(0, "#E8C66A"), (1, "#8A6418")]), 5) + C(-188, -153, 9, "#B8862A") + C(188, -153, 9, "#B8862A"))
    return "".join(o)


def key():
    """A brass house key."""
    brass = lg([(0, "#F6DE8A"), (.35, "#E2B84A"), (.6, "#B8862A"), (1, "#7A5414")])
    g = [ground(0, 64, 150, 8, .18)]
    bow = "M-96,-56 C-60,-56 -40,-30 -40,0 C-40,30 -60,56 -96,56 C-132,56 -156,30 -156,0 C-156,-30 -132,-56 -96,-56Z M-114,0 C-114,10 -106,18 -96,18 C-86,18 -78,10 -78,0 C-78,-10 -86,-18 -96,-18 C-106,-18 -114,-10 -114,0Z"
    g.append(f'<path d="{bow}" fill="{brass}" fill-rule="evenodd"/>')
    g.append(P("M-44,-20 L-24,-20 L-24,20 L-44,20Z", brass))
    blade = ("M-26,-16 L130,-16 C138,-16 144,-12 146,-4 L148,4 L126,24 L118,16 L108,26 L98,16 L86,28 L74,16 L62,26 "
             "L50,16 L40,24 L30,16 L-26,16Z")
    g.append(P(blade, lg([(0, "#F6DE8A"), (.4, "#E2B84A"), (.7, "#B8862A"), (1, "#7A5414")])))
    g.append(L("M-20,-2 L132,-2", "#8A6418", 3, 'opacity=".55"') + L("M-20,1 L132,1", "#FFF0B0", 1.2, 'opacity=".6"'))
    g.append(inside(bow.split("Z")[0] + "Z", glow(-120, -26, 26, 12, "#FFFFFF", .55, -30), specks((-160, -60, -36, 60), .07, 54)))
    g.append(L("M-138,-30 C-124,-48 -104,-52 -86,-48", "#FFF4C0", 3, 'opacity=".7"'))
    return rot("".join(g), -18)


REAL = {
    "cup": (cup, (-96, -76, 92, 82)),
    "bowl": (bowl, (-140, -80, 140, 90)),
    "spoon": (spoon, (-170, -102, 140, 104)),
    "chopsticks": (chopsticks, (-156, -96, 156, 104)),
    "plate": (plate, (-160, -70, 160, 80)),
    "toothbrush": (toothbrush, (-166, -110, 160, 80)),
    "towel": (towel, (-162, -140, 162, 150)),
    "soap": (soap, None),
    "comb": (comb, (-166, -90, 166, 96)),
    "chair": (chair, None),
    "table": (table, None),
    "bed": (bed, None),
    "pillow": (pillow, (-162, -96, 162, 98)),
    "clock": (clock, (-156, -156, 156, 174)),
    "phone": (phone, (-112, -190, 112, 186)),
    "tv": (tv, (-180, -122, 180, 140)),
    "lamp": (lamp, (-140, -176, 140, 178)),
    "door": (door, (-130, -200, 130, 202)),
    "window": (window, (-198, -164, 198, 144)),
    "key": (key, (-166, -96, 166, 96)),
}

# ================================================================ cartoon
# Flat bold shapes, bright colours, no outlines, no texture. A few round things get a tiny face.
RED, YEL, BLUE, GREEN, ORANGE, PINK = "#F2353B", "#FFC62E", "#2F7DE1", "#27B26B", "#FF8A1F", "#F46A9B"
SKY, DARK, GREY, WHITE = "#BDE7FA", "#2B2B33", "#B8C2CC", "#FFFFFF"


def floor(cx, cy, rx, ry=7):
    return E(cx, cy, rx, ry, "#1E1E28", 'opacity=".12"')


def c_cup():
    o = [floor(-6, 70, 70)]
    o.append(L("M40,-30 C92,-36 92,32 40,28", BLUE, 18))
    o.append(P("M-58,-58 L58,-58 L52,52 Q50,64 38,64 L-38,64 Q-50,64 -52,52Z", BLUE))
    o.append(E(0, -58, 58, 13, "#7FB4F0") + E(0, -56, 50, 9, "#1C5CB8"))
    o.append(R(-44, -40, 12, 80, WHITE, 6, 'opacity=".35"'))
    o.append(face(4, 8, 1.15))
    return "".join(o)


def c_bowl():
    o = [floor(0, 78, 96)]
    o.append(E(0, -40, 132, 36, "#9CC3E8"))
    o.append(E(0, -34, 118, 26, "#C8DDF2"))
    body = "M-132,-40 C-130,12 -92,48 -50,56 L-48,70 L48,70 L50,56 C92,48 130,12 132,-40 A132,36 0 0 1 -132,-40Z"
    o.append(P(body, "#E8F2FB") + inside(body, P("M-140,-34 A140,40 0 0 0 140,-34 L140,-20 A140,40 0 0 1 -140,-20Z", BLUE)))
    o.append(R(-48, 60, 96, 10, "#9CC3E8", 4))
    o.append(face(0, 22, 1.1))
    return "".join(o)


def c_spoon():
    g = [P("M-176,-11 Q-186,0 -176,11 C-110,13 -40,9 6,5 L24,10 L24,-10 L6,-5 C-40,-9 -110,-13 -176,-11Z", "#A9B4BF"),
         E(74, 0, 60, 38, "#A9B4BF"), E(78, 2, 48, 28, "#D7DEE5"), E(96, 12, 16, 7, WHITE, 'opacity=".9"'),
         R(-170, -6, 130, 5, WHITE, 2.5, 'opacity=".5"')]
    return floor(-14, 92, 140, 9) + rot("".join(g), -28)


def c_chopsticks():
    def stick(y, a):
        return (f'<g transform="translate(0 {y}) rotate({a})">'
                + P("M-166,-11 L166,-4 Q170,0 166,4 L-166,11 Q-170,0 -166,-11Z", "#E8B567")
                + P("M-166,-11 L-66,-8.7 L-66,8.7 L-166,11 Q-170,0 -166,-11Z", "#B8452E") + R(-70, -10, 6, 20, YEL, 2) + "</g>")
    return floor(-6, 74, 140, 9) + stick(-16, -27) + stick(16, -23)


def c_plate():
    o = [floor(0, 70, 150, 10)]
    o.append(E(0, 10, 152, 66, "#9CC3E8"))
    o.append(E(0, 0, 152, 66, "#F4F8FC"))
    o.append(E(0, 0, 140, 60, "none", f'stroke="{BLUE}" stroke-width="7"'))
    o.append(E(0, 6, 100, 42, "#DCE8F4") + E(0, 9, 92, 37, "#F4F8FC"))
    o.append(E(-70, -26, 26, 7, WHITE, 'transform="rotate(-10 -70 -26)"'))
    return "".join(o)


def c_toothbrush():
    g = [P("M-176,4 Q-178,-14 -150,-15 C-110,-15 -50,-9 30,-4 L72,-7 L72,9 L30,8 C-50,12 -110,19 -150,19 Q-178,20 -176,4Z", BLUE),
         P("M-150,-15 C-130,-15 -100,-13 -84,-12 L-84,17 C-100,17 -130,19 -150,19Z", GREEN),
         P(rrect(66, -12, 88, 24, 12), BLUE), R(-140, -9, 150, 5, WHITE, 2.5, 'opacity=".4"')]
    g += [P(rrect(72 + i * 9, -44, 7.4, 34, 3.7), "#9FE3F5" if i % 3 else "#3FB8E0") for i in range(9)]
    g.append(P("M64,-44 C58,-58 72,-64 84,-58 C94,-70 112,-68 118,-58 C130,-68 148,-62 150,-50 C158,-48 160,-42 152,-40 L66,-40 Q60,-40 64,-44Z", "#7FD3F2"))
    g.append(L("M66,-48 C82,-56 100,-48 120,-56 C132,-60 142,-56 152,-50", WHITE, 6))
    return floor(0, 56, 150, 9) + rot("".join(g), -22)


def c_towel():
    base = "#4FA9E6"
    o = [R(-150, -128, 300, 14, GREY, 7), R(-162, -136, 18, 28, "#8C96A2", 6), R(144, -136, 18, 28, "#8C96A2", 6)]
    o.append(P("M-100,-118 L108,-118 L112,140 Q60,146 -96,140Z", "#2F82C2"))
    front = "M-110,-124 Q0,-136 110,-124 L114,124 Q70,132 0,130 Q-70,132 -112,124Z"
    o.append(P(front, base) + inside(front, R(-120, 66, 240, 16, WHITE), R(-120, 90, 240, 7, WHITE), R(-120, -130, 240, 18, "#8FCBF2"),
                                     R(-80, -100, 18, 150, WHITE, 9, 'opacity=".25"')))
    return "".join(o)


def c_soap():
    cam = Cam(yaw=18, pitch=40)
    base = PINK
    sides, top = extrude(cam, round_rect_xz(-110, -60, 110, 60, 46, 8), 0, 44, base, flat=True, top_fill=lt(base, .35))
    o = [sides]
    tx_, ty_ = cam.p(0, 44, 0)
    o.append(face(tx_, ty_ + 4, 1.4))
    bx = cam.box(0)
    gr = floor((bx[0] + bx[2]) / 2, bx[3] - 2, (bx[2] - bx[0]) * .5, 9)
    bub = []
    for x, y, r in ((40, -120, 26), (90, -96, 16), (-20, -128, 12), (120, -138, 10), (-100, -110, 14), (-60, -60, 18), (-36, -70, 13)):
        bub.append(C(x, y, r, "#BFE6FA") + C(x - r * .35, y - r * .38, r * .28, WHITE))
    xs, ys = cam.xs + [-120, 140], cam.ys + [-150]
    return gr + "".join(o) + "".join(bub), (min(xs) - 4, min(ys) - 4, max(xs) + 4, max(ys) + 14)


def c_comb():
    base = PINK
    teeth = []
    x = -152
    while x < 150:
        w = 8 if x < 0 else 5.4
        teeth.append(rrect(x, -26, w, 86, w / 2))
        x += w + (6 if x < 0 else 4)
    g = [floor(0, 78, 150, 9), P(" ".join(teeth), base),
         P("M-160,-44 Q-160,-62 -140,-62 L140,-62 Q160,-62 160,-44 L160,-20 L-160,-20Z", "#D9437E"),
         R(-140, -54, 240, 7, WHITE, 3.5, 'opacity=".45"')]
    return rot("".join(g), -8)


def c_chair():
    cam = Cam(yaw=-32, pitch=18)
    w = "#F0A04B"
    t = 12
    lx0, lx1, lz0, lz1 = -66, 66, -60, 60
    items = []
    for x in (lx0, lx1 - t):
        items.append((x, x + t, 0, 132, lz0, lz0 + t, w, True))
        items.append((x, x + t, 0, 276, lz1 - t, lz1, w, True))
    items.append((lx0 - 4, lx1 + 4, 132, 146, lz0 - 4, lz1, RED, True))
    items.append((lx0 + t, lx1 - t, 236, 268, lz1 - t + 2, lz1 - 2, w, True))
    items.append((lx0 + t, lx1 - t, 190, 206, lz1 - t + 3, lz1 - 3, w, True))
    body = scene(cam, items)
    bx = cam.box(0)
    return floor((bx[0] + bx[2]) / 2, bx[3] - 6, (bx[2] - bx[0]) * .55, 10) + body, cam.box(10)


def c_table():
    cam = Cam(yaw=-24, pitch=22)
    w = "#F0A04B"
    X, Z, H, t = 132, 84, 158, 14
    legs = [(-X + 8, -X + 8 + t, 0, H, -Z + 8, -Z + 8 + t), (X - 8 - t, X - 8, 0, H, -Z + 8, -Z + 8 + t),
            (-X + 8, -X + 8 + t, 0, H, Z - 8 - t, Z - 8), (X - 8 - t, X - 8, 0, H, Z - 8 - t, Z - 8)]
    back = scene(cam, [(*b, dk(w, .1), True) for b in legs[1:]])
    top = cuboid(cam, -X, X, H - 4, H + 12, -Z, Z, w, flat=True)
    front = cuboid(cam, *legs[0], dk(w, .1), flat=True)
    bx = cam.box(0)
    return floor((bx[0] + bx[2]) / 2, bx[3] - 6, (bx[2] - bx[0]) * .55, 12) + back + top + front, cam.box(10)


def c_bed():
    cam = Cam(yaw=26, pitch=26)
    wood = "#F0A04B"
    Lx, Wz, t = 300, 160, 14
    o = []
    arch = ([(Wz, 0)] + [(Wz * (0.5 + 0.5 * math.cos(math.radians(a))), 140 + 52 * math.sin(math.radians(a))) for a in range(0, 181, 12)] + [(0, 0)])
    o.append(P(" ".join(cam.poly([(0, y0, z0), (t, y0, z0), (t, y1, z1), (0, y1, z1)]) for (z0, y0), (z1, y1) in zip(arch, arch[1:])), dk(wood, .2)))
    o.append(P(cam.poly([(t, y, z) for z, y in arch]), wood))
    o.append(cuboid(cam, t, Lx - t, 24, 60, Wz - 8, Wz, wood, flat=True))
    o.append(cuboid(cam, t, Lx - t, 52, 88, 6, Wz - 6, "#D3E0EC", flat=True))
    o.append(cuboid(cam, t, Lx - t, 24, 60, 0, 8, wood, flat=True))
    pc = [cam.p(x, 100, z) for x, z in ((20, 20), (88, 16), (92, Wz - 16), (24, Wz - 20))]
    mid = [((a[0] + b[0]) / 2 + dx, (a[1] + b[1]) / 2 + dy) for (a, b), (dx, dy) in zip(zip(pc, pc[1:] + pc[:1]), ((0, 8), (8, 0), (0, -12), (-8, 0)))]
    o.append(P(blob([pc[0], mid[0], pc[1], mid[1], pc[2], mid[2], pc[3], mid[3]]), WHITE))
    x0b, x1b = 124, Lx - t
    o.append(cuboid(cam, x0b, x1b, 88, 96, -2, Wz + 2, BLUE, flat=True))
    o.append(cuboid(cam, x0b, x1b, 40, 96, -6, -2, BLUE, flat=True))
    tp = cam.poly([(x0b, 96, -2), (x1b, 96, -2), (x1b, 96, Wz + 2), (x0b, 96, Wz + 2)])
    stars = []
    for x, z in ((170, 40), (230, 110), (200, 80), (260, 30), (250, 140)):
        sx, sy = cam.p(x, 96, z)
        stars.append(C(sx, sy, 6, YEL))
    o.append(inside(tp, *stars))
    o.append(cuboid(cam, x0b, x0b + 24, 88, 98, -2, Wz + 2, "#F4F7FA", flat=True))
    o.append(cuboid(cam, x0b, x0b + 24, 40, 98, -8, -2, "#F4F7FA", flat=True))
    o.append(cuboid(cam, 0, t, 0, 60, 0, 8, dk(wood, .1), flat=True))
    o.append(cuboid(cam, Lx - t, Lx, 0, 108, 0, Wz, wood, flat=True))
    bx = cam.box(0)
    return floor((bx[0] + bx[2]) / 2, bx[3] - 8, (bx[2] - bx[0]) * .5, 12) + "".join(o), cam.box(10)


def c_pillow():
    d = blob([(-150, -64), (-70, -76), (0, -70), (80, -84), (156, -80), (146, -10), (156, 60), (80, 66), (0, 72), (-80, 64), (-156, 74), (-146, 0)], 10)
    o = [floor(0, 88, 150, 10), P(d, "#9CC9EE"),
         P(blob([(-120, -50), (-60, -60), (0, -56), (70, -66), (120, -60), (114, -10), (120, 40), (60, 46), (0, 50), (-70, 44), (-124, 50), (-114, 0)], 10), "#C4E0F7"),
         E(-70, -38, 30, 9, WHITE, 'opacity=".7" transform="rotate(-8 -70 -38)"')]
    o.append(eye(-22, 0, 10, blink=True) + eye(22, 0, 10, blink=True) + smile(0, 18, 14, 4, 3.4) + cheek(-40, 16, 8) + cheek(40, 16, 8))
    return "".join(o)


def c_clock():
    o = [C(0, 0, 150, RED), C(0, 0, 124, WHITE)]
    for i in range(12):
        a = math.radians(i * 30)
        if i % 3:
            o.append(C(math.sin(a) * 104, -math.cos(a) * 104, 6, "#5A5F6A"))
    for h, txt in ((0, "12"), (3, "3"), (6, "6"), (9, "9")):
        a = math.radians(h * 30)
        o.append(number(txt, math.sin(a) * 92, -math.cos(a) * 92, 30, DARK, 6))
    o.append(L("M0,0 L-44,-30", DARK, 14) + L("M0,0 L46,-64", DARK, 10) + C(0, 0, 12, YEL))
    return "".join(o)


def c_phone():
    g = [P(rrect(-84, -168, 168, 336, 32), "#2F3A56"), P(rrect(-72, -156, 144, 312, 22), "#8FC4F2"),
         P(rrect(-20, -148, 40, 12, 6), "#2F3A56"),
         C(0, -70, 36, WHITE), C(0, -80, 13, "#9AB0D0"), P("M-24,-48 C-22,-64 -12,-66 0,-66 C12,-66 22,-64 24,-48 C14,-40 -14,-40 -24,-48Z", "#9AB0D0"),
         R(-40, -20, 80, 9, WHITE, 4.5), R(-26, -4, 52, 7, WHITE, 3.5, 'opacity=".7"'),
         C(-40, 104, 25, RED), handset(-40, 106, 1.25, WHITE, 135), C(40, 104, 25, GREEN), handset(40, 104, 1.25, WHITE, 0)]
    return floor(10, 178, 84, 9) + rot("".join(g), -8)


def c_tv():
    o = [floor(0, 130, 120), R(-14, 86, 28, 24, DARK), P(rrect(-80, 104, 160, 14, 7), DARK)]
    o.append(P(rrect(-178, -120, 356, 214, 16), "#2F3A56"))
    scr = rrect(-162, -104, 324, 182, 8)
    o.append(inside(scr, R(-170, -110, 340, 200, "#6EC1F2"), C(108, -54, 28, YEL),
                    P("M-90,-60 C-90,-74 -70,-80 -60,-70 C-52,-86 -24,-84 -20,-66 C-8,-66 -4,-50 -18,-48 L-84,-48 C-96,-48 -98,-60 -90,-62Z", WHITE),
                    P("M-170,20 C-120,-20 -60,-10 -10,20 C40,-6 110,-30 170,10 L170,90 L-170,90Z", "#5BC25A"),
                    P("M-170,50 C-100,20 -20,30 40,56 C90,40 140,36 170,46 L170,90 L-170,90Z", GREEN)))
    o.append(C(160, 86, 3, RED))
    return "".join(o)


def c_lamp():
    o = [C(0, -40, 150, "#FFE680", 'opacity=".35"'), floor(0, 168, 84)]
    o.append(P(rrect(-66, 136, 132, 26, 13), "#B8743A"))
    o.append(P("M-12,136 C-56,132 -78,100 -76,68 C-74,36 -50,14 -22,8 L-14,-4 L14,-4 L22,8 C50,14 74,36 76,68 C78,100 56,132 12,136Z", "#2BB3A3"))
    o.append(E(-36, 56, 12, 30, WHITE, 'opacity=".35"'))
    o.append(R(-6, -40, 12, 40, "#C99A3A"))
    o.append(E(0, -32, 40, 14, "#FFF6C8"))
    o.append(P("M-56,-160 Q0,-166 56,-160 L104,-44 Q0,-26 -104,-44Z", YEL))
    o.append(P("M-104,-44 Q0,-26 104,-44 L104,-36 Q0,-18 -104,-36Z", ORANGE))
    o.append(R(-40, -150, 14, 96, WHITE, 7, 'opacity=".3" transform="rotate(-12 -33 -102)"'))
    return "".join(o)


def c_door():
    o = [P(rrect(-124, -196, 248, 396, 10), "#E9E2D6"), P(rrect(-104, -180, 208, 374, 6), "#B86A34")]
    for x, y, w, h in ((-84, -160, 72, 120), (12, -160, 72, 120), (-84, -14, 72, 186), (12, -14, 72, 186)):
        o.append(P(rrect(x, y, w, h, 8), "#D98A4E"))
    o.append(C(76, 12, 13, YEL) + C(76, 36, 4, DARK))
    o.append(R(-132, 190, 264, 12, "#C9C0B2", 6))
    return "".join(o)


def c_window():
    o = [P(rrect(-140, -142, 280, 252, 10), WHITE), P(rrect(-122, -124, 244, 216, 6), "#6EC1F2")]
    pane = rrect(-122, -124, 244, 216, 6)
    o.append(inside(pane, P("M-100,-60 C-104,-76 -84,-86 -72,-76 C-64,-94 -30,-92 -26,-70 C-12,-72 -6,-54 -20,-50 L-92,-50 C-104,-50 -106,-58 -100,-60Z", WHITE),
                    P("M30,-10 C28,-22 42,-28 52,-22 C58,-34 82,-32 84,-16 C94,-16 98,-4 88,-2 L36,-2 C28,-2 26,-8 30,-10Z", WHITE),
                    P("M-130,70 C-80,50 -30,56 10,72 C50,56 100,52 130,62 L130,100 L-130,100Z", GREEN)))
    o.append(R(-7, -124, 14, 216, WHITE) + R(-122, -22, 244, 12, WHITE))
    o.append(P(rrect(-160, 102, 320, 20, 8), "#E9E2D6"))
    for sgn in (-1, 1):
        o.append(P(f"M{sgn * 178},-150 L{sgn * 104},-150 C{sgn * 98},-100 {sgn * 104},-40 {sgn * 120},10 C{sgn * 132},40 {sgn * 130},90 {sgn * 120},140 L{sgn * 178},140Z", RED))
        o.append(R(sgn * 150 - 6, -146, 12, 140, "#C8202A", 6, 'opacity=".5"'))
        o.append(L(f"M{sgn * 112},12 L{sgn * 176},16", YEL, 8))
    o.append(P(rrect(-190, -160, 380, 14, 7), "#C99A3A"))
    return "".join(o)


def c_key():
    g = []
    g.append('<path d="M-96,-58 C-58,-58 -38,-32 -38,0 C-38,32 -58,58 -96,58 C-134,58 -158,32 -158,0 C-158,-32 -134,-58 -96,-58Z '
             f'M-114,0 C-114,10 -106,18 -96,18 C-86,18 -78,10 -78,0 C-78,-10 -86,-18 -96,-18 C-106,-18 -114,-10 -114,0Z" fill="{YEL}" fill-rule="evenodd"/>')
    g.append(P("M-44,-22 L-22,-22 L-22,22 L-44,22Z", YEL))
    g.append(P("M-26,-18 L132,-18 Q146,-18 148,-4 L150,4 L128,26 L118,16 L108,28 L98,16 L86,30 L74,16 L62,28 L50,16 L40,26 L30,16 L-26,16Z", YEL))
    g.append(R(-20, -4, 150, 6, "#E0A100", 3) + E(-122, -26, 14, 7, WHITE, 'opacity=".6" transform="rotate(-30 -122 -26)"'))
    return floor(0, 92, 130, 8) + rot("".join(g), -18)


CARTOON = {
    "cup": (c_cup, (-90, -78, 96, 82)),
    "bowl": (c_bowl, (-140, -80, 140, 90)),
    "spoon": (c_spoon, (-170, -102, 140, 104)),
    "chopsticks": (c_chopsticks, (-156, -96, 156, 104)),
    "plate": (c_plate, (-160, -70, 160, 84)),
    "toothbrush": (c_toothbrush, (-166, -110, 160, 80)),
    "towel": (c_towel, (-164, -140, 164, 150)),
    "soap": (c_soap, None),
    "comb": (c_comb, (-166, -90, 166, 96)),
    "chair": (c_chair, None),
    "table": (c_table, None),
    "bed": (c_bed, None),
    "pillow": (c_pillow, (-162, -96, 162, 100)),
    "clock": (c_clock, (-156, -156, 156, 156)),
    "phone": (c_phone, (-112, -190, 112, 188)),
    "tv": (c_tv, (-182, -124, 182, 140)),
    "lamp": (c_lamp, (-150, -190, 150, 176)),
    "door": (c_door, (-134, -200, 134, 204)),
    "window": (c_window, (-196, -164, 196, 144)),
    "key": (c_key, (-166, -96, 166, 96)),
}

if __name__ == "__main__":
    only = set(sys.argv[1:]) or None
    write_deck("home", REAL, CARTOON, only)

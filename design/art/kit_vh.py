"""Drawing kit for the 交通工具 (vehicles) and 家裡的東西 (home) card decks of 小卡認天下.

Every card is drawn twice, by code, as plain SVG that flutter_svg can show:
    <id>.svg          realistic: true shapes, colours and proportions, soft gradient shading,
                      a little speck texture, no outlines, no faces
    <id>_cartoon.svg  cartoon: flat bold shapes, bright colours, no outlines, no texture;
                      vehicles may get friendly eyes and a smile, objects a tiny face

flutter_svg rules kept here: no <filter>, <mask>, <style>, <text> or <foreignObject>;
soft light and shadow come from gradients that fade to transparent (glow, ground, shade);
texture is one small tile of specks repeated with <use> (at most 800 per file).
Everything is deterministic (fixed random seeds).

    python3 deck_vehicles.py           # writes app/assets/art/cards/vehicles/*.svg
    python3 deck_home.py               # writes app/assets/art/cards/home/*.svg
    python3 kit_vh.py sheet OUT.png    # contact sheet of both decks (needs Node + Playwright)
"""
import hashlib
import math
import pathlib
import random
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "app" / "assets" / "art" / "cards"
SIZE = 400
FILL = .85            # the subject's longer side covers this much of the card

# ---------------------------------------------------------------- colours
INK = "#2E2A2B"       # cartoon pupils and smiles


def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(x + (y - x) * t))) for x, y in zip(_rgb(a), _rgb(b)))


def lt(c, t):
    return mix(c, "#FFFFFF", t)


def dk(c, t):
    return mix(c, "#141018", t)


def f1(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


# ---------------------------------------------------------------- per-file defs
class Defs:
    def __init__(self):
        self.reset()

    def reset(self):
        self.d = {}
        self.uses = 0

    def add(self, key, svg):
        self.d.setdefault(key, svg)
        return key

    def svg(self):
        return "<defs>" + "".join(self.d.values()) + "</defs>" if self.d else ""


D = Defs()


def _h(*parts):
    return hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:6]


def _stops(stops):
    out = []
    for s in stops:
        op = f' stop-opacity="{s[2]}"' if len(s) > 2 and s[2] != 1 else ""
        out.append(f'<stop offset="{s[0]}" stop-color="{s[1]}"{op}/>')
    return "".join(out)


def lg(stops, x1=0, y1=0, x2=0, y2=1, user=False, tf=None):
    """Linear gradient; stops are (offset, colour[, opacity]). user=True: x/y in drawing units."""
    k = "l" + _h(stops, x1, y1, x2, y2, user, tf)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    t = f' gradientTransform="{tf}"' if tf else ""
    D.add(k, f'<linearGradient id="{k}" x1="{f1(x1)}" y1="{f1(y1)}" x2="{f1(x2)}" y2="{f1(y2)}"{u}{t}>{_stops(stops)}</linearGradient>')
    return f"url(#{k})"


def rg(stops, cx=.5, cy=.5, r=.5, fx=None, fy=None, user=False, tf=None):
    k = "r" + _h(stops, cx, cy, r, fx, fy, user, tf)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    f = f' fx="{f1(fx)}" fy="{f1(fy)}"' if fx is not None else ""
    t = f' gradientTransform="{tf}"' if tf else ""
    D.add(k, f'<radialGradient id="{k}" cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}"{f}{u}{t}>{_stops(stops)}</radialGradient>')
    return f"url(#{k})"


def clip(*shapes):
    """Clip path from path data strings (or ready-made SVG shapes starting with '<')."""
    body = "".join(s if s.startswith("<") else f'<path d="{s}"/>' for s in shapes)
    k = "c" + _h(body)
    D.add(k, f'<clipPath id="{k}">{body}</clipPath>')
    return f"url(#{k})"


def inside(d, *parts):
    """Group of parts clipped to path d."""
    return f'<g clip-path="{clip(d)}">{"".join(parts)}</g>'


# ---------------------------------------------------------------- shapes
def P(d, fill, extra=""):
    return f'<path d="{d}" fill="{fill}"{" " + extra if extra else ""}/>'


def E(cx, cy, rx, ry, fill, extra=""):
    return f'<ellipse cx="{f1(cx)}" cy="{f1(cy)}" rx="{f1(rx)}" ry="{f1(ry)}" fill="{fill}"{" " + extra if extra else ""}/>'


def C(cx, cy, r, fill, extra=""):
    return f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="{fill}"{" " + extra if extra else ""}/>'


def R(x, y, w, h, fill, rx=0, extra=""):
    r = f' rx="{f1(rx)}"' if rx else ""
    return f'<rect x="{f1(x)}" y="{f1(y)}" width="{f1(w)}" height="{f1(h)}"{r} fill="{fill}"{" " + extra if extra else ""}/>'


def L(d, color, w, extra="", cap="round"):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{f1(w)}" stroke-linecap="{cap}" stroke-linejoin="round"{" " + extra if extra else ""}/>'


def rrect(x, y, w, h, r):
    """Path data of a rounded rectangle."""
    r = min(r, w / 2, h / 2)
    return (f"M{f1(x + r)},{f1(y)} H{f1(x + w - r)} A{f1(r)},{f1(r)} 0 0 1 {f1(x + w)},{f1(y + r)} V{f1(y + h - r)} "
            f"A{f1(r)},{f1(r)} 0 0 1 {f1(x + w - r)},{f1(y + h)} H{f1(x + r)} A{f1(r)},{f1(r)} 0 0 1 {f1(x)},{f1(y + h - r)} "
            f"V{f1(y + r)} A{f1(r)},{f1(r)} 0 0 1 {f1(x + r)},{f1(y)}Z")


def ell(cx, cy, rx, ry):
    """Path data of an ellipse."""
    return (f"M{f1(cx - rx)},{f1(cy)} A{f1(rx)},{f1(ry)} 0 1 0 {f1(cx + rx)},{f1(cy)} "
            f"A{f1(rx)},{f1(ry)} 0 1 0 {f1(cx - rx)},{f1(cy)}Z")


def poly(pts, close=True):
    return "M" + " L".join(f"{f1(p[0])},{f1(p[1])}" for p in pts) + ("Z" if close else "")


def spline(pts, n=8, closed=False):
    """Catmull-Rom curve through pts."""
    P_ = list(pts)
    P_ = [P_[-1]] + P_ + [P_[0], P_[1]] if closed else [P_[0]] + P_ + [P_[-1]]
    out = []
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for j in range(n):
            t = j / n
            out.append(tuple(.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3)
                             for a, b, c, d in zip(p0, p1, p2, p3)))
    if not closed:
        out.append(tuple(P_[-2]))
    return out


def blob(pts, n=6):
    return poly(spline(pts, n, closed=True))


# ---------------------------------------------------------------- soft light without filters
def glow(cx, cy, rx, ry, color="#FFFFFF", op=.5, rot=0, core=0.0):
    """A soft spot of light (or dark): an ellipse whose colour fades out to its edge."""
    g = rg([(0, color, op), (core, color, op), (1, color, 0)] if core else [(0, color, op), (1, color, 0)])
    t = f' transform="rotate({f1(rot)} {f1(cx)} {f1(cy)})"' if rot else ""
    return E(cx, cy, rx, ry, g, t[1:] if t else "")


def ground(cx, cy, rx, ry, op=.22, color="#2B2F36"):
    """Soft shadow on the floor under a thing."""
    return E(cx, cy, rx, ry, rg([(0, color, op), (.55, color, op * .55), (1, color, 0)]))


def band(x0, y0, x1, y1, color, op, mid=.5, spread=.5):
    """Soft stripe across a box, strongest at `mid` (0..1 from (x0,y0) to (x1,y1)); fills the box."""
    a, b = max(0, mid - spread), min(1, mid + spread)
    st = [(0, color, 0)] if a > 0 else []
    st += [(round(a, 3), color, 0), (round(mid, 3), color, op), (round(b, 3), color, 0)]
    if b < 1:
        st.append((1, color, 0))
    return st


def shade(box, color="#000000", left=0.0, right=0.0, top=0.0, bottom=0.0, w=.22):
    """Darken (or lighten) the edges of a box: rectangles of gradient that fade inwards.
    Put it inside a clip of the shape to give it roundness."""
    x0, y0, x1, y1 = box
    o = []
    if left:
        o.append(R(x0, y0, (x1 - x0) * w, y1 - y0, lg([(0, color, left), (1, color, 0)], 0, 0, 1, 0)))
    if right:
        o.append(R(x1 - (x1 - x0) * w, y0, (x1 - x0) * w, y1 - y0, lg([(0, color, 0), (1, color, right)], 0, 0, 1, 0)))
    if top:
        o.append(R(x0, y0, x1 - x0, (y1 - y0) * w, lg([(0, color, top), (1, color, 0)])))
    if bottom:
        o.append(R(x0, y1 - (y1 - y0) * w, x1 - x0, (y1 - y0) * w, lg([(0, color, 0), (1, color, bottom)])))
    return "".join(o)


def specks(box, op=.10, seed=5, tile=40, n=26, light="#FFFFFF", dark="#000000", r=(.35, .8)):
    """A little print texture over box: one tile of tiny dots repeated with <use>."""
    k = "t" + _h(seed, tile, n, light, dark, r)
    if k not in D.d:
        rng = random.Random(seed)
        dots = []
        for i in range(n):
            col = light if i % 2 else dark
            dots.append(f'<circle cx="{rng.uniform(0, tile):.1f}" cy="{rng.uniform(0, tile):.1f}" r="{rng.uniform(*r):.2f}" fill="{col}"/>')
        D.add(k, f'<g id="{k}">{"".join(dots)}</g>')
    x0, y0, x1, y1 = box
    o = []
    y = y0
    while y < y1:
        x = x0
        while x < x1:
            o.append(f'<use xlink:href="#{k}" x="{f1(x)}" y="{f1(y)}"/>')
            D.uses += 1
            x += tile
        y += tile
    return f'<g opacity="{op}">{"".join(o)}</g>'


# ---------------------------------------------------------------- realistic parts
def tyre(cx, cy, r, rim=.62, hub="#C9CED4", spokes=5, deep=False):
    """Car or truck wheel seen from the side: rubber, a silver rim with spokes, a hub cap."""
    o = [C(cx, cy, r, rg([(0, "#3C3E43"), (.78, "#26282C"), (.93, "#18191C"), (1, "#0E0F11")])),
         C(cx, cy, r * .97, "none", f'stroke="#4A4D53" stroke-width="{f1(r * .03)}" opacity=".6"')]
    rr = r * rim
    o.append(C(cx, cy, rr, rg([(0, lt(hub, .6)), (.55, hub), (1, dk(hub, .45))], cx=.4, cy=.35, r=.75)))
    if spokes:
        o.append(C(cx, cy, rr * .86, dk(hub, .55)))
        sp = []
        for i in range(spokes):
            a = math.radians(-90 + i * 360 / spokes)
            w = math.radians(13)
            pts = [(cx + rr * .22 * math.cos(a - w * 2.2), cy + rr * .22 * math.sin(a - w * 2.2)),
                   (cx + rr * .9 * math.cos(a - w), cy + rr * .9 * math.sin(a - w)),
                   (cx + rr * .9 * math.cos(a + w), cy + rr * .9 * math.sin(a + w)),
                   (cx + rr * .22 * math.cos(a + w * 2.2), cy + rr * .22 * math.sin(a + w * 2.2))]
            sp.append(poly(pts))
        o.append(P(" ".join(sp), rg([(0, lt(hub, .7)), (.6, hub), (1, dk(hub, .3))], cx=.38, cy=.32, r=.7)))
    o.append(C(cx, cy, rr * .26, rg([(0, "#FFFFFF"), (1, dk(hub, .35))], cx=.4, cy=.35)))
    if deep:
        o.append(C(cx, cy, rr, "none", f'stroke="{dk(hub, .5)}" stroke-width="{f1(r * .05)}" opacity=".5"'))
    o.append(P(f"M{f1(cx - r * .82)},{f1(cy - r * .35)} A{f1(r * .9)},{f1(r * .9)} 0 0 1 {f1(cx + r * .1)},{f1(cy - r * .88)}",
               "none", f'stroke="#FFFFFF" stroke-width="{f1(r * .06)}" stroke-linecap="round" opacity=".18"'))
    return "".join(o)


def arch(cx, cy, r, color="#141518"):
    """Dark wheel arch behind a wheel (upper half circle + a bit)."""
    return P(f"M{f1(cx - r)},{f1(cy + 2)} A{f1(r)},{f1(r)} 0 0 1 {f1(cx + r)},{f1(cy + 2)}Z", color)


def glass(d, box, tint="#3A4C5C", sky=True):
    """Window glass: dark blue-grey with a pale sky reflection and two diagonal glints."""
    x0, y0, x1, y1 = box
    o = [P(d, lg([(0, lt(tint, .45)), (.45, tint), (1, dk(tint, .45))]))]
    w, h = x1 - x0, y1 - y0
    g = []
    if sky:
        g.append(R(x0, y0, w, h * .45, lg([(0, "#DDEBF5", .45), (1, "#DDEBF5", 0)])))
    sk = h * .9
    for fx, fw, op in ((.25, .16, .30), (.5, .06, .22)):
        gx = x0 + w * fx
        g.append(P(poly([(gx + sk * .5, y0 - 2), (gx + sk * .5 + w * fw, y0 - 2), (gx - sk * .5 + w * fw, y1 + 2), (gx - sk * .5, y1 + 2)]),
                   lg([(0, "#FFFFFF", op), (1, "#FFFFFF", op * .3)])))
    o.append(inside(d, *g))
    return "".join(o)


def chrome(stops=None):
    return lg(stops or [(0, "#F4F6F8"), (.45, "#C3C9CF"), (.55, "#8D959D"), (1, "#E0E4E8")])


# ---------------------------------------------------------------- cartoon parts
def eye(cx, cy, r, look=(.25, .1), blink=False):
    """A friendly cartoon eye: white, a big dark pupil looking a little forward, a shine."""
    if blink:
        return L(f"M{f1(cx - r * .8)},{f1(cy)} Q{f1(cx)},{f1(cy + r * .7)} {f1(cx + r * .8)},{f1(cy)}", INK, r * .32)
    px, py = cx + look[0] * r, cy + look[1] * r
    return (E(cx, cy, r * .9, r, "#FFFFFF") + C(px, py, r * .58, INK)
            + C(px - r * .2, py - r * .26, r * .2, "#FFFFFF"))


def smile(cx, cy, w, h=None, width=None, color=INK):
    h = w * .45 if h is None else h
    return L(f"M{f1(cx - w / 2)},{f1(cy)} Q{f1(cx)},{f1(cy + h * 2)} {f1(cx + w / 2)},{f1(cy)}", color, width or max(2.5, w * .14))


def cheek(cx, cy, r, color="#FF8FA0", op=.55):
    return E(cx, cy, r, r * .7, color, f'opacity="{op}"')


def face(cx, cy, s=1.0, cheeks=True):
    """A tiny face for an object: two dot eyes, a small smile, rosy cheeks."""
    o = [C(cx - 11 * s, cy, 4.2 * s, INK), C(cx + 11 * s, cy, 4.2 * s, INK),
         C(cx - 12.2 * s, cy - 1.4 * s, 1.4 * s, "#FFFFFF"), C(cx + 9.8 * s, cy - 1.4 * s, 1.4 * s, "#FFFFFF"),
         smile(cx, cy + 7 * s, 10 * s, 3.4 * s, 2.6 * s)]
    if cheeks:
        o += [cheek(cx - 20 * s, cy + 7 * s, 5 * s), cheek(cx + 20 * s, cy + 7 * s, 5 * s)]
    return "".join(o)


def wheel_flat(cx, cy, r, hub="#E6E6E6", tyre_c="#1F1F24"):
    return C(cx, cy, r, tyre_c) + C(cx, cy, r * .45, hub) + C(cx, cy, r * .16, mix(hub, tyre_c, .35))



# ---------------------------------------------------------------- simple 3D boxes (furniture, a bar of soap)
class Cam:
    """Orthographic view: turn by yaw (degrees) about the vertical axis, look down by pitch.
    World: x right, y up, z away from the viewer. Faces get flat tones from one light (top left front)."""

    def __init__(self, yaw=28, pitch=22, light=(-.55, .8, -.45)):
        a, b = math.radians(yaw), math.radians(pitch)
        self.ca, self.sa, self.cb, self.sb = math.cos(a), math.sin(a), math.cos(b), math.sin(b)
        n = math.sqrt(sum(v * v for v in light))
        self.L = [v / n for v in light]
        self.xs, self.ys = [], []

    def r(self, x, y, z):
        x1, z1 = x * self.ca + z * self.sa, -x * self.sa + z * self.ca
        return x1, y * self.cb + z1 * self.sb, -y * self.sb + z1 * self.cb

    def p(self, x, y, z):
        x1, y2, _ = self.r(x, y, z)
        self.xs.append(x1)
        self.ys.append(-y2)
        return x1, -y2

    def depth(self, x, y, z):
        return self.r(x, y, z)[2]

    def facing(self, n):
        return self.r(*n)[2] < -1e-6

    def tone(self, base, n, flat=False):
        k = sum(a * b for a, b in zip(n, self.L))
        if flat:
            return lt(base, .22) if k > .6 else (base if k > 0 else dk(base, .22))
        return lt(base, k * .3) if k >= 0 else dk(base, -k * .5)

    def box(self, pad=6):
        return (min(self.xs) - pad, min(self.ys) - pad, max(self.xs) + pad, max(self.ys) + pad)

    def poly(self, pts):
        return poly([self.p(*q) for q in pts])


def face_fill(cam, base, n, flat=False, grad=True):
    c = cam.tone(base, n, flat)
    if flat or not grad:
        return c
    return lg([(0, lt(c, .06)), (1, dk(c, .1))])


def cuboid(cam, x0, x1, y0, y1, z0, z1, base, flat=False, extra=None):
    """A box from (x0,y0,z0) to (x1,y1,z1): its visible faces. extra(n, d) can add details on a face."""
    F = [((0, 1, 0), [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]),
         ((0, -1, 0), [(x0, y0, z0), (x0, y0, z1), (x1, y0, z1), (x1, y0, z0)]),
         ((0, 0, -1), [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)]),
         ((0, 0, 1), [(x0, y0, z1), (x0, y1, z1), (x1, y1, z1), (x1, y0, z1)]),
         ((-1, 0, 0), [(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)]),
         ((1, 0, 0), [(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)])]
    o = []
    for n, q in F:
        if cam.facing(n):
            d = cam.poly(q)
            o.append(P(d, face_fill(cam, base, n, flat)))
            if extra:
                o.append(extra(n, d) or "")
    return "".join(o)


def solid_depth(cam, x0, x1, y0, y1, z0, z1):
    return cam.depth((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)


def scene(cam, items):
    """items: (x0, x1, y0, y1, z0, z1, colour[, extra]) boxes, drawn far to near."""
    out = []
    for it in sorted(items, key=lambda b: -solid_depth(cam, *b[:6])):
        out.append(cuboid(cam, *it[:7], flat=it[7] if len(it) > 7 else False, extra=it[8] if len(it) > 8 else None))
    return "".join(out)


def extrude(cam, outline, y0, y1, base, flat=False, top_fill=None):
    """A flat shape lying in the x-z plane (outline of (x, z) points, counter-clockwise seen from above),
    raised from height y0 to y1: its sides and top."""
    n = len(outline)
    cx = sum(p[0] for p in outline) / n
    cz = sum(p[1] for p in outline) / n
    sides = []
    for i in range(n):
        (ax, az), (bx, bz) = outline[i], outline[(i + 1) % n]
        nx, nz = bz - az, -(bx - ax)
        ln = math.hypot(nx, nz) or 1
        nx, nz = nx / ln, nz / ln
        if nx * ((ax + bx) / 2 - cx) + nz * ((az + bz) / 2 - cz) < 0:
            nx, nz = -nx, -nz
        nrm = (nx, 0, nz)
        if cam.facing(nrm):
            q = [(ax, y0, az), (bx, y0, bz), (bx, y1, bz), (ax, y1, az)]
            sides.append((-cam.depth((ax + bx) / 2, (y0 + y1) / 2, (az + bz) / 2), P(cam.poly(q), cam.tone(base, nrm, flat))))
    o = [s for _, s in sorted(sides)]
    top = cam.poly([(x, y1, z) for x, z in outline])
    o.append(P(top, top_fill or cam.tone(base, (0, 1, 0), flat)))
    return "".join(o), top


def round_rect_xz(x0, z0, x1, z1, r, n=6):
    """Counter-clockwise outline of a rounded rectangle in the x-z plane."""
    pts = []
    for cx, cz, a0 in ((x1 - r, z0 + r, -90), (x1 - r, z1 - r, 0), (x0 + r, z1 - r, 90), (x0 + r, z0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


# ---------------------------------------------------------------- digits drawn with strokes (clock faces)
DIGITS = {
    "0": "M3,0 C0.2,0 0,3 0,5 C0,7 0.2,10 3,10 C5.8,10 6,7 6,5 C6,3 5.8,0 3,0Z",
    "1": "M1.2,2 L3.6,0 L3.6,10",
    "2": "M0.3,2.6 C0.5,0.6 2,0 3.1,0 C4.8,0 6,1.2 6,2.8 C6,5 2,7 0,10 L6,10",
    "3": "M0.4,1.2 C1.2,0.3 2.2,0 3.1,0 C4.8,0 5.8,1.1 5.8,2.5 C5.8,4 4.4,4.9 2.6,4.9 C4.6,4.9 6,6 6,7.4 C6,9 4.6,10 3,10 C1.8,10 0.8,9.6 0,8.8",
    "4": "M4.6,10 L4.6,0 L0,7 L6.2,7",
    "5": "M5.6,0 L1.2,0 L0.6,4.6 C1.4,4 2.2,3.8 3,3.8 C4.8,3.8 6,5 6,6.9 C6,8.8 4.6,10 2.9,10 C1.8,10 0.8,9.6 0,8.9",
    "6": "M5.4,0.6 C4.8,0.2 4,0 3.3,0 C1.2,0 0,2.4 0,5.6 C0,8.6 1.3,10 3,10 C4.8,10 6,8.7 6,7 C6,5.2 4.8,4 3.1,4 C1.7,4 0.6,4.8 0.1,6",
    "7": "M0,0 L6,0 C4,3 2.6,6.4 2.2,10",
    "8": "M3,4.8 C1.4,4.8 0.4,3.8 0.4,2.4 C0.4,1 1.5,0 3,0 C4.5,0 5.6,1 5.6,2.4 C5.6,3.8 4.6,4.8 3,4.8 C1.2,4.8 0,5.9 0,7.4 C0,8.9 1.3,10 3,10 C4.7,10 6,8.9 6,7.4 C6,5.9 4.8,4.8 3,4.8Z",
    "9": "M5.9,4 C5.4,5.2 4.3,6 2.9,6 C1.2,6 0,4.8 0,3 C0,1.2 1.3,0 3,0 C4.9,0 6,1.6 6,4.2 C6,7.6 4.6,10 2.6,10 C1.8,10 1.1,9.7 0.6,9.3",
}


def number(s, cx, cy, h, color, w=None):
    """Draw a number centred at (cx, cy), h tall, with stroked digits."""
    k = h / 10
    adv = 7.4
    total = adv * len(s) - 1.4
    out = []
    for i, ch in enumerate(s):
        x = cx - total * k / 2 + i * adv * k
        out.append(f'<path transform="translate({f1(x)} {f1(cy - h / 2)}) scale({k:.3f})" d="{DIGITS[ch]}" fill="none" '
                   f'stroke="{color}" stroke-width="{f1((w or h * .14) / k)}" stroke-linecap="round" stroke-linejoin="round"/>')
    return "".join(out)


# ---------------------------------------------------------------- files
def svg_doc(body, box, fill=FILL):
    """Scale a drawing (in its own units, covering box) to the middle of the 400x400 card."""
    x0, y0, x1, y1 = box
    s = SIZE * fill / max(x1 - x0, y1 - y0)
    tx_, ty_ = SIZE / 2 - (x0 + x1) / 2 * s, SIZE / 2 - (y0 + y1) / 2 * s
    assert D.uses <= 800, D.uses
    return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" height="{SIZE}">{D.svg()}'
            f'<g transform="translate({tx_:.2f} {ty_:.2f}) scale({s:.4f})">{body}</g></svg>')


def write_deck(deck, real, cartoon, only=None):
    """real / cartoon: {id: (draw function, box)}. Writes OUT/deck/<id>.svg and <id>_cartoon.svg."""
    out = OUT / deck
    out.mkdir(parents=True, exist_ok=True)
    for table, suffix in ((real, ""), (cartoon, "_cartoon")):
        for cid, (fn, box) in table.items():
            if only and cid not in only:
                continue
            D.reset()
            body = fn()
            if isinstance(body, tuple):          # drawings that measure themselves (3D boxes)
                body, box = body
            text = svg_doc(body, box)
            for bad in ("<filter", "<mask", "<style", "<text", "<foreignObject", "<pattern"):
                assert bad not in text, (cid, bad)
            (out / f"{cid}{suffix}.svg").write_text(text)
            kb = len(text.encode()) / 1024
            if kb > 60:
                print(f"WARNING {deck}/{cid}{suffix}.svg is {kb:.0f} KB")
    print(f"wrote {deck}: {len(real)} realistic + {len(cartoon)} cartoon")


# ---------------------------------------------------------------- previews
RENDER_JS = """const { chromium } = require('playwright');
(async () => {
  const [inp, out, w, h] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
  await page.goto('file://' + inp);
  await page.waitForTimeout(300);
  await page.screenshot({ path: out, fullPage: true });
  await browser.close();
})();
"""


def sheet(out_png, decks=("vehicles", "home"), cols=5, big=170, small=120):
    """Contact sheet: per card the realistic and cartoon pictures side by side, big and at ~120 px."""
    import json
    cards = json.loads((ROOT / "design" / "cards.json").read_text())
    names = {c["id"]: c["zh"] for d in cards["decks"] for c in d["cards"]}
    cells = []
    for deck in decks:
        ids = [c["id"] for d in cards["decks"] if d["id"] == deck for c in d["cards"]]
        for cid in ids:
            a, b = OUT / deck / f"{cid}.svg", OUT / deck / f"{cid}_cartoon.svg"
            cells.append(f'<div class="c"><div class="row"><img src="file://{a}" width="{big}"><img src="file://{b}" width="{big}"></div>'
                         f'<div class="row"><img src="file://{a}" width="{small}"><img src="file://{b}" width="{small}"></div>'
                         f'<div class="n">{names.get(cid, "")} · {cid}</div></div>')
    cw = big * 2 + 30
    html = ("<!doctype html><html><head><meta charset='utf-8'></head><body style='margin:0;background:#E9E4DB;"
            f"font-family:sans-serif'><div style='display:grid;grid-template-columns:repeat({cols},{cw}px);gap:12px;padding:12px'>"
            + "".join(cells).replace('class="c"', f'style="background:#fff;border-radius:16px;padding:8px;text-align:center"')
            .replace('class="row"', 'style="display:flex;justify-content:center;gap:10px"')
            .replace('class="n"', 'style="font-size:16px;color:#444;margin-top:4px"')
            + "</div></body></html>")
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp)
        (p / "sheet.html").write_text(html)
        (p / "render.js").write_text(RENDER_JS)
        w = cols * (cw + 12) + 12
        subprocess.run(["node", str(p / "render.js"), str(p / "sheet.html"), str(out_png), str(w), "400"], check=True)
    print("sheet:", out_png)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "sheet":
        decks = tuple(sys.argv[3:]) or ("vehicles", "home")
        sheet(sys.argv[2], decks)

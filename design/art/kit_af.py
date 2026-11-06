"""Drawing kit for the animal and fruit card decks of 小卡認天下.

Two styles for every card:
  realistic  <id>.svg          picture-dictionary look: true shapes and colours, soft gradient
                                shading, a little texture (fur strokes, skin speckles), no outlines,
                                no cartoon faces.
  cartoon    <id>_cartoon.svg   flat, bold, bright shapes; animals get a simple cute face.

The approved mockups (docs/mockups/make_mockups.py) got their soft look from SVG filters
(blur, a lighting rim, grain). The app draws cards with flutter_svg, which draws no filters
and no masks, so this kit builds the same look only from paths, linear and radial gradients,
clip paths and opacity:
  glow()   a blurred ellipse  -> an ellipse filled with a radial gradient that fades to nothing
  haze()   a blurred stroke   -> a few stacked strokes, wider ones fainter
  rim()    the `vol` filter   -> inside a clip of the shape, its own outline stroked with a gradient
                                 that is dark only towards the bottom right (light from the top left)
  ground() the soft contact shadow under a subject

Every drawing is a function returning SVG in its own units (about -130..130). write_deck()
renders each one once in Chromium (Playwright) to find how far it really reaches, then writes
the card with a transform that centres it and makes it fill about 85% of the 400 x 400 square.
Everything is deterministic: random numbers always come from random.Random(fixed seed).
"""
import hashlib
import json
import math
import pathlib
import random
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CARDS = ROOT / "app" / "assets" / "art" / "cards"
SIZE = 400
FILL = 340          # the longer side of a subject, in px of the 400 px card
FILL_SQ = 318       # a compact (square-ish) subject a little smaller, so it does not look huge


# ---------------------------------------------------------------- colours
def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(x + (y - x) * t))) for x, y in zip(_rgb(a), _rgb(b)))


def lt(c, t):
    return mix(c, "#FFFFFF", t)


def dk(c, t):
    return mix(c, "#1E1A18", t)


# ---------------------------------------------------------------- numbers
def n(v):
    s = f"{v:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    return "0" if s == "-0" else s


# ---------------------------------------------------------------- defs (one registry per card)
class Defs:
    def __init__(self):
        self.d = {}

    def add(self, key, svg):
        self.d.setdefault(key, svg)
        return key

    def svg(self):
        return "<defs>" + "".join(self.d.values()) + "</defs>" if self.d else ""


D = Defs()


def begin():
    global D
    D = Defs()


def _h(*parts):
    return hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:8]


def _stops(stops):
    out = []
    for s in stops:
        o = f' stop-opacity="{s[2]:.3g}"' if len(s) > 2 and s[2] != 1 else ""
        out.append(f'<stop offset="{s[0]:.3g}" stop-color="{s[1]}"{o}/>')
    return "".join(out)


def lg(stops, x1=0, y1=0, x2=0, y2=1, user=False):
    """Linear gradient. stops: (offset, colour[, opacity]). user=True: x/y in the drawing's own units."""
    k = "l" + _h(stops, x1, y1, x2, y2, user)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    D.add(k, f'<linearGradient id="{k}" x1="{n(x1) if user else x1}" y1="{n(y1) if user else y1}" '
             f'x2="{n(x2) if user else x2}" y2="{n(y2) if user else y2}"{u}>{_stops(stops)}</linearGradient>')
    return f"url(#{k})"


def rg(stops, cx=.5, cy=.5, r=.5, fx=None, fy=None, user=False, tf=None):
    """Radial gradient (objectBoundingBox unless user=True). tf: a gradientTransform."""
    k = "r" + _h(stops, cx, cy, r, fx, fy, user, tf)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    f = f' fx="{fx}" fy="{fy}"' if fx is not None else ""
    t = f' gradientTransform="{tf}"' if tf else ""
    D.add(k, f'<radialGradient id="{k}" cx="{cx}" cy="{cy}" r="{r}"{f}{u}{t}>{_stops(stops)}</radialGradient>')
    return f"url(#{k})"


def clip(d):
    k = "c" + _h(d)
    D.add(k, f'<clipPath id="{k}"><path d="{d}"/></clipPath>')
    return f"url(#{k})"


def clipped(d, inner):
    return f'<g clip-path="{clip(d)}">{inner}</g>'


# ---------------------------------------------------------------- path geometry
_TOK = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
_NARGS = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7}


def path_points(d):
    """Every end and control point of a path (absolute), enough for a bounding box."""
    toks = _TOK.findall(d)
    i, cmd, x, y, sx, sy, pts = 0, None, 0.0, 0.0, 0.0, 0.0, []
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in "Zz":
                x, y = sx, sy
            continue
        C, rel = cmd.upper(), cmd.islower()
        k = _NARGS[C]
        a = [float(v) for v in toks[i:i + k]]
        i += k
        if C == "H":
            x = a[0] + (x if rel else 0)
            pts.append((x, y))
        elif C == "V":
            y = a[0] + (y if rel else 0)
            pts.append((x, y))
        elif C == "A":
            ex, ey = a[5] + (x if rel else 0), a[6] + (y if rel else 0)
            mx, my = (x + ex) / 2, (y + ey) / 2
            r = max(a[0], a[1])
            pts += [(ex, ey), (mx - r, my - r), (mx + r, my + r)]
            x, y = ex, ey
        else:
            for j in range(0, k, 2):
                px, py = a[j] + (x if rel else 0), a[j + 1] + (y if rel else 0)
                pts.append((px, py))
            x, y = pts[-1]
            if C == "M":
                sx, sy = x, y
                cmd = "l" if rel else "L"
    return pts


def bbox(d):
    p = path_points(d)
    xs, ys = [q[0] for q in p], [q[1] for q in p]
    return min(xs), min(ys), max(xs), max(ys)


def ell(cx, cy, rx, ry, rot=0.0):
    """An ellipse as a closed cubic path (rotation baked in), so it can be clipped to and rimmed."""
    k = .5523
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)

    def p(x, y):
        return f"{n(cx + x * ca - y * sa)},{n(cy + x * sa + y * ca)}"
    return (f"M{p(rx, 0)} C{p(rx, ry * k)} {p(rx * k, ry)} {p(0, ry)} C{p(-rx * k, ry)} {p(-rx, ry * k)} {p(-rx, 0)} "
            f"C{p(-rx, -ry * k)} {p(-rx * k, -ry)} {p(0, -ry)} C{p(rx * k, -ry)} {p(rx, -ry * k)} {p(rx, 0)}Z")


def circ(cx, cy, r):
    return ell(cx, cy, r, r)


def rrect(x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    return (f"M{n(x + r)},{n(y)} L{n(x + w - r)},{n(y)} A{n(r)},{n(r)} 0 0 1 {n(x + w)},{n(y + r)} L{n(x + w)},{n(y + h - r)} "
            f"A{n(r)},{n(r)} 0 0 1 {n(x + w - r)},{n(y + h)} L{n(x + r)},{n(y + h)} A{n(r)},{n(r)} 0 0 1 {n(x)},{n(y + h - r)} "
            f"L{n(x)},{n(y + r)} A{n(r)},{n(r)} 0 0 1 {n(x + r)},{n(y)}Z")


def spline(pts, k=10, closed=False):
    """Catmull-Rom curve through pts (tuples of any length: x, y[, width])."""
    P = list(pts)
    P = [P[-1]] + P + [P[0], P[1]] if closed else [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(k):
            t = j / k
            out.append(tuple(.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3)
                             for a, b, c, d in zip(p0, p1, p2, p3)))
    if not closed:
        out.append(tuple(P[-2]))
    return out


def poly(pts, close=True):
    return "M" + " L".join(f"{n(p[0])},{n(p[1])}" for p in pts) + ("Z" if close else "")


def _segs(P, closed=False):
    """Catmull-Rom through P written as cubic Bezier segments (no leading M)."""
    pts = [P[-1]] + list(P) + [P[0], P[1]] if closed else [P[0]] + list(P) + [P[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        out.append(f"C{n(p1[0] + (p2[0] - p0[0]) / 6)},{n(p1[1] + (p2[1] - p0[1]) / 6)} "
                   f"{n(p2[0] - (p3[0] - p1[0]) / 6)},{n(p2[1] - (p3[1] - p1[1]) / 6)} {n(p2[0])},{n(p2[1])}")
    return "".join(out)


def blob(pts, k=None):
    """Smooth closed shape through pts."""
    return f"M{n(pts[0][0])},{n(pts[0][1])}" + _segs([p[:2] for p in pts], True) + "Z"


def line(pts, k=None):
    """Smooth open curve through pts."""
    return f"M{n(pts[0][0])},{n(pts[0][1])}" + _segs([p[:2] for p in pts])


def _sides(pts, k=3):
    c = spline(pts, k)
    L, R, N = [], [], []
    for i, (x, y, w) in enumerate(c):
        a, b = c[max(0, i - 1)], c[min(len(c) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        N.append((nx, ny))
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    return c, L, R, N


def tube(pts, k=3, caps=(True, True)):
    """Outline of a limb, tail, neck...: pts are (x, y, half-width) along its middle."""
    c, L, R, _ = _sides(pts, k)
    w1, w0 = c[-1][2], c[0][2]
    d = f"M{n(L[0][0])},{n(L[0][1])}" + _segs(L)
    d += (f"A{n(w1)},{n(w1)} 0 0 0 {n(R[-1][0])},{n(R[-1][1])}" if caps[1] else f"L{n(R[-1][0])},{n(R[-1][1])}")
    d += _segs(R[::-1])
    d += (f"A{n(w0)},{n(w0)} 0 0 0 {n(L[0][0])},{n(L[0][1])}Z" if caps[0] else "Z")
    return d


def along(pts, frac, t0=0.0, t1=1.0, k=3):
    """A line inside a tube, at frac of the half-width from the middle (+ = the 'left' side)."""
    c, _, _, N = _sides(pts, k)
    i0, i1 = round(t0 * (len(c) - 1)), round(t1 * (len(c) - 1))
    return line([(c[i][0] + N[i][0] * c[i][2] * frac, c[i][1] + N[i][1] * c[i][2] * frac) for i in range(i0, i1 + 1)])


def at(pts, t, k=8):
    """Point, direction angle (degrees) and half-width at fraction t along a tube."""
    c = spline(pts, k)
    i = min(len(c) - 2, max(0, round(t * (len(c) - 1))))
    a, b = c[i], c[i + 1]
    return a[0], a[1], math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])), a[2]


def inside(d):
    """A point-in-shape test for a closed path (polygon of its points; fine for blob/tube/ell)."""
    pts = path_points(d)

    def test(x, y):
        c = False
        j = len(pts) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi:
                c = not c
            j = i
        return c
    return test


# ---------------------------------------------------------------- soft shading without filters
def glow(cx, cy, rx, ry, color, op=1.0, rot=0, hard=.35):
    """A soft-edged ellipse (what a blurred ellipse looked like): full colour to `hard`, then fading out."""
    f = rg([(0, color, op), (hard, color, op * .82), (.72, color, op * .32), (1, color, 0)])
    t = f' transform="rotate({n(rot)} {n(cx)} {n(cy)})"' if rot else ""
    return f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="{f}"{t}/>'


def haze(d, color, w, op=1.0, spread=None, cap="round"):
    """A soft stroke: three stacked strokes, the wider ones fainter."""
    s = spread if spread is not None else max(1.2, w * .6)
    lay = ((w + 2.2 * s, .28), (w + 1.0 * s, .34), (max(.4, w - .3 * s), .5))
    return (f'<g fill="none" stroke="{color}" stroke-linecap="{cap}" stroke-linejoin="round">'
            + "".join(f'<path d="{d}" stroke-width="{n(ww)}" stroke-opacity="{op * o:.3f}"/>' for ww, o in lay) + "</g>")


def softfill(d, color, op=1.0, edge=3.0):
    """A filled shape with a soft edge: a fading halo outside, flattened in a group so nothing doubles up."""
    return (f'<g opacity="{op:.3g}"><path d="{d}" fill="none" stroke="{color}" stroke-width="{n(edge * 2.4)}" stroke-opacity=".22" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{n(edge * 1.2)}" stroke-opacity=".4" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="{color}"/></g>')


def ref(d):
    """Put a path in defs once; returns its id (for <use href>)."""
    k = "p" + _h(d)
    D.add(k, f'<path id="{k}" d="{d}"/>')
    return k


def use(d, attrs):
    return f'<use href="#{ref(d)}" {attrs}/>'


def rim_strokes(d, dark="#3A1E10", op=.4, w=7.0, light=0.0, angle=50, lightc="#FFFFFF"):
    """The strokes of rim(), unclipped (to put inside a clip of d together with other details)."""
    x0, y0, x1, y1 = bbox(d)
    cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, math.hypot(x1 - x0, y1 - y0) / 2
    a = math.radians(angle)
    ax, ay, bx, by = cx - math.cos(a) * r, cy - math.sin(a) * r, cx + math.cos(a) * r, cy + math.sin(a) * r
    g = lg([(0, dark, 0), (.42, dark, 0), (.75, dark, .55), (1, dark, 1)], ax, ay, bx, by, user=True)
    out = [use(d, f'fill="none" stroke="{g}" stroke-width="{n(w * ww)}" stroke-opacity="{op * o:.3f}" stroke-linejoin="round"')
           for ww, o in ((2.6, .35), (1.5, .45), (.7, .6))]
    if light:
        gl = lg([(0, lightc, 1), (.3, lightc, .4), (.55, lightc, 0), (1, lightc, 0)], ax, ay, bx, by, user=True)
        out += [use(d, f'fill="none" stroke="{gl}" stroke-width="{n(w * ww)}" stroke-opacity="{light * o:.3f}" stroke-linejoin="round"')
                for ww, o in ((1.8, .4), (.8, .6))]
    return "".join(out)


def rim(d, dark="#3A1E10", op=.4, w=7.0, light=0.0, angle=50, lightc="#FFFFFF"):
    """The soft rounded edge of a form lit from the top left: inside the shape, a darker band along
    the edges that face down-right (and a faint light band top-left if light > 0)."""
    return clipped(d, rim_strokes(d, dark, op, w, light, angle, lightc))


def ground(cx, cy, rx, ry, op=.2, color="#2E3238"):
    return glow(cx, cy, rx, ry, color, op, hard=.2)


def form(d, fill, inner="", dark="#3A1E10", op=.38, w=7.0, light=0.0, angle=50):
    """A shaded form: the shape, its inside details (clipped to it) and the rim on top."""
    return use(d, f'fill="{fill}"') + clipped(d, inner + rim_strokes(d, dark, op, w, light, angle))


# ---------------------------------------------------------------- texture
def strokes(rng, count, box, angle, colors, length=(5, 9), width=1.0, op=.3, curve=.18, test=None):
    """Many short soft strokes (fur) inside box (and inside test(x, y) if given), grouped by colour.
    angle(x, y) gives their direction in radians."""
    x0, y0, x1, y1 = box
    by = {c: [] for c in colors}
    tries = 0
    made = 0
    while made < count and tries < count * 6:
        tries += 1
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        if test and not test(x, y):
            continue
        a = angle(x, y) + rng.uniform(-.28, .28)
        ln = rng.uniform(*length)
        ex, ey = x + math.cos(a) * ln, y + math.sin(a) * ln
        mx, my = (x + ex) / 2 + math.cos(a + 1.57) * ln * curve, (y + ey) / 2 + math.sin(a + 1.57) * ln * curve
        by[rng.choice(colors)].append(f"M{n(x)},{n(y)}q{n(mx - x)},{n(my - y)} {n(ex - x)},{n(ey - y)}")
        made += 1
    return (f'<g fill="none" stroke-width="{n(width)}" stroke-linecap="round" opacity="{op}">'
            + "".join(f'<path d="{"".join(v)}" stroke="{c}"/>' for c, v in by.items() if v) + "</g>")


def speckles(rng, count, box, color, r=(.6, 1.3), op=.5, test=None, squash=None):
    """Tiny round dots (skin pores, seeds, freckles): zero-length round-capped strokes, three sizes."""
    x0, y0, x1, y1 = box
    sizes = (r[0], (r[0] + r[1]) / 2, r[1])
    parts = {s_: [] for s_ in sizes}
    tries = made = 0
    while made < count and tries < count * 8:
        tries += 1
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        if test and not test(x, y):
            continue
        parts[rng.choice(sizes)].append(f"M{n(x)},{n(y)}h.1")
        made += 1
    return (f'<g fill="none" stroke="{color}" stroke-linecap="round" stroke-opacity="{op}">'
            + "".join(f'<path d="{"".join(v)}" stroke-width="{n(2 * s_)}"/>' for s_, v in parts.items() if v) + "</g>")


# ---------------------------------------------------------------- realistic details
def eye(cx, cy, r, iris="#3A2212", rot=0, lid="#2A1A10", shine=1.0, lidop=.7):
    """A real eye seen from the side: dark almond, iris, pupil, one catchlight, an upper lid line."""
    t = f' transform="rotate({n(rot)} {n(cx)} {n(cy)})"' if rot else ""
    return (f'<g{t}><ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(r * 1.25)}" ry="{n(r)}" fill="{lid}"/>'
            f'<ellipse cx="{n(cx + r * .1)}" cy="{n(cy)}" rx="{n(r * .9)}" ry="{n(r * .82)}" '
            f'fill="{rg([(0, lt(iris, .25)), (.7, iris), (1, dk(iris, .4))], .45, .4, .6)}"/>'
            f'<circle cx="{n(cx + r * .15)}" cy="{n(cy)}" r="{n(r * .45)}" fill="#0E0A08"/>'
            f'<circle cx="{n(cx + r * .45)}" cy="{n(cy - r * .38)}" r="{n(r * .26)}" fill="#FFFFFF" opacity="{.92 * shine:.2f}"/>'
            f'<path d="M{n(cx - r * 1.3)},{n(cy + r * .1)} C{n(cx - r * .7)},{n(cy - r * 1.25)} {n(cx + r * .7)},{n(cy - r * 1.3)} {n(cx + r * 1.3)},{n(cy - r * .3)}" '
            f'stroke="{lid}" stroke-width="{n(max(.8, r * .3))}" fill="none" stroke-linecap="round" opacity="{lidop}"/></g>')


# ---------------------------------------------------------------- cartoon helpers
BLUSH = "#FF8FA3"
INK = "#2B211C"


def dot_eyes(x1, y1, x2, y2, r=6.5, ink=INK, shine=True):
    o = [f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{ink}"/>' for x, y in ((x1, y1), (x2, y2))]
    if shine:
        o += [f'<circle cx="{n(x + r * .35)}" cy="{n(y - r * .4)}" r="{n(r * .36)}" fill="#FFFFFF"/>' for x, y in ((x1, y1), (x2, y2))]
    return "".join(o)


def dot_eye(x, y, r=6.5, ink=INK, shine=True):
    o = f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{ink}"/>'
    if shine:
        o += f'<circle cx="{n(x + r * .35)}" cy="{n(y - r * .4)}" r="{n(r * .36)}" fill="#FFFFFF"/>'
    return o


def smile(cx, cy, w=12, h=6, sw=3.4, ink=INK):
    return (f'<path d="M{n(cx - w / 2)},{n(cy)} Q{n(cx)},{n(cy + h * 1.6)} {n(cx + w / 2)},{n(cy)}" stroke="{ink}" '
            f'stroke-width="{n(sw)}" fill="none" stroke-linecap="round"/>')


def blush(cx, cy, rx=8, ry=5, op=.55, c=BLUSH):
    return f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="{c}" opacity="{op}"/>'


def P(d, fill, extra=""):
    return f'<path d="{d}" fill="{fill}"{extra}/>'


def C(cx, cy, r, fill, extra=""):
    return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{fill}"{extra}/>'


def E(cx, cy, rx, ry, fill, rot=0, extra=""):
    t = f' transform="rotate({n(rot)} {n(cx)} {n(cy)})"' if rot else ""
    return f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="{fill}"{t}{extra}/>'


def S(d, color, w, extra="", cap="round"):
    return f'<path d="{d}" stroke="{color}" stroke-width="{n(w)}" fill="none" stroke-linecap="{cap}" stroke-linejoin="round"{extra}/>'


# ================================================================ writing cards
_MEASURE_JS = r"""
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 1 });
  for (const j of jobs) {
    await page.setViewportSize({ width: j.w, height: j.h });
    await page.goto('file://' + j.svg);
    await page.screenshot({ path: j.png, omitBackground: true });
  }
  await browser.close();
})();
"""


def render_many(jobs):
    """jobs: [(svg_path, png_path, w, h)] rendered in one Chromium session."""
    with tempfile.TemporaryDirectory() as tmp:
        js = pathlib.Path(tmp) / "measure.js"
        js.write_text(_MEASURE_JS)
        lst = pathlib.Path(tmp) / "jobs.json"
        lst.write_text(json.dumps([{"svg": str(a), "png": str(b), "w": w, "h": h} for a, b, w, h in jobs]))
        subprocess.run(["node", str(js), str(lst)], check=True)


MB = 300   # measuring canvas: -MB..MB local units at 1 px per unit


def _measure(bodies):
    from PIL import Image
    import numpy as np
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        jobs = []
        for name, (defs, body) in bodies.items():
            p = pathlib.Path(tmp) / f"{name}.svg"
            p.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-MB} {-MB} {2 * MB} {2 * MB}" '
                         f'width="{2 * MB}" height="{2 * MB}">{defs}{body}</svg>')
            jobs.append((p, pathlib.Path(tmp) / f"{name}.png", 2 * MB, 2 * MB))
        render_many(jobs)
        for name in bodies:
            a = np.asarray(Image.open(pathlib.Path(tmp) / f"{name}.png").getchannel("A"))
            ys, xs = np.nonzero(a > 28)
            if len(xs) == 0:
                raise SystemExit(f"{name}: nothing drawn")
            if xs.min() <= 0 or ys.min() <= 0 or xs.max() >= 2 * MB - 1 or ys.max() >= 2 * MB - 1:
                print(f"warning: {name} reaches the edge of the measuring canvas")
            out[name] = (xs.min() - MB, ys.min() - MB, xs.max() + 1 - MB, ys.max() + 1 - MB)
    return out


FORBIDDEN = ("<filter", "<mask", "<style", "<foreignObject", "<image", "<text", "class=", "style=")


def check(name, svg):
    bad = [f for f in FORBIDDEN if f in svg]
    if bad:
        raise SystemExit(f"{name}: uses {bad} (flutter_svg cannot draw these)")
    if svg.count("<use") > 800:
        raise SystemExit(f"{name}: too many <use>")
    kb = len(svg.encode()) / 1024
    if kb > 60:
        print(f"warning: {name} is {kb:.0f} KB")
    return kb


def verify(path):
    """The file on disk is whole: not empty, ends with </svg>, parses as XML."""
    import xml.etree.ElementTree as ET
    text = pathlib.Path(path).read_text()
    if not text.rstrip().endswith("</svg>"):
        raise SystemExit(f"{path}: cut short")
    ET.fromstring(text)


def write_deck(deck, drawings, only=None):
    """drawings: {file_stem: function}. Draws each, measures it, writes app/assets/art/cards/<deck>/<stem>.svg."""
    outdir = CARDS / deck
    outdir.mkdir(parents=True, exist_ok=True)
    bodies = {}
    for stem, fn in drawings.items():
        if only and stem not in only and stem.replace("_cartoon", "") not in only:
            continue
        begin()
        body = fn()
        bodies[stem] = (D.svg(), body)
    boxes = _measure(bodies)
    sizes = {}
    for stem, (defs, body) in bodies.items():
        x0, y0, x1, y1 = boxes[stem]
        w, h = x1 - x0, y1 - y0
        s = min(FILL / max(w, h), FILL_SQ / math.sqrt(w * h))
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" height="{SIZE}">'
               f'{defs}<g transform="translate({SIZE / 2} {SIZE / 2}) scale({s:.4f}) translate({n(-cx)} {n(-cy)})">{body}</g></svg>\n')
        sizes[stem] = check(stem, svg)
        dest = outdir / f"{stem}.svg"
        dest.write_text(svg)
        verify(dest)
    print(f"{deck}: wrote {len(bodies)} cards, largest {max(sizes.values()):.1f} KB")
    return list(bodies)


# ================================================================ contact sheet
def sheet(decks, out, small=120):
    """Every card of the decks: realistic and cartoon side by side on white cards, then all of them small."""
    cells, smalls = [], []
    for deck in decks:
        for p in sorted((CARDS / deck).glob("*.svg")):
            if p.stem.endswith("_cartoon"):
                continue
            cart = p.with_name(p.stem + "_cartoon.svg")
            pair = "".join(f'<div class="c"><img src="file://{q}"></div>' for q in (p, cart) if q.exists())
            cells.append(f'<div class="pair">{pair}<div class="t">{deck}/{p.stem}</div></div>')
            smalls.append("".join(f'<div class="s"><img src="file://{q}"></div>' for q in (p, cart) if q.exists()))
    html = f"""<html><body style="margin:0;background:#E9E4DB;font:14px sans-serif">
<style>.g{{display:flex;flex-wrap:wrap;gap:14px;padding:14px}}.pair{{background:#DDD6CA;border-radius:16px;padding:8px}}
.c{{display:inline-block;width:220px;height:220px;background:#fff;border-radius:18px;margin:4px}}.c img{{width:220px;height:220px}}
.t{{text-align:center;color:#555}}.s{{display:inline-flex;gap:4px;margin:3px}}.s img{{width:{small}px;height:{small}px;background:#fff;border-radius:10px}}</style>
<div class="g">{''.join(cells)}</div><div class="g" style="gap:6px">{''.join(smalls)}</div></body></html>"""
    with tempfile.TemporaryDirectory() as tmp:
        hp = pathlib.Path(tmp) / "sheet.html"
        hp.write_text(html)
        js = pathlib.Path(tmp) / "sheet.js"
        js.write_text("""const { chromium } = require('playwright');
(async () => { const [inp, out] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1960, height: 800 }, deviceScaleFactor: 1 });
  await p.goto('file://' + inp); await p.waitForTimeout(300); await p.screenshot({ path: out, fullPage: true }); await b.close(); })();""")
        pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["node", str(js), str(hp), str(out)], check=True)
    print(out)


def main(deck, real, cartoon, argv):
    """python3 deck_x.py [ids...]          write all cards (or only these ids)
       python3 deck_x.py sheet out.png    contact sheet of this deck"""
    if argv and argv[0] == "sheet":
        sheet([deck], argv[1] if len(argv) > 1 else f"/tmp/{deck}.png")
        return
    drawings = dict(real)
    drawings.update({f"{k}_cartoon": v for k, v in cartoon.items()})
    write_deck(deck, drawings, set(argv) or None)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "sheet":
        sheet(sys.argv[3:] or ["animals", "fruits"], sys.argv[2])
    else:
        print(__doc__)

"""Drawing kit for the body and clothes decks (both styles).

    python3 kit_bc.py preview out.png      # contact sheet of body + clothes (needs Node.js + Playwright)

Every card is a square SVG (viewBox 0 0 400 400) with a see-through background. The app shows
it on a white card with flutter_svg, so the drawings use only what flutter_svg draws: paths,
gradients (with stop-opacity), clip paths and group opacity. No <filter>, no <mask>, no CSS.

Realistic style: the soft light and shade that the design mockups made with blur filters is made
here with gradients only:
  spot()   a soft round shade or light (an ellipse with a radial gradient fading to nothing)
  sline()  a soft line (a fold, a crease): a few stacked strokes, wide and faint to thin and stronger
  rim()    the darker rim inside a shape's lower-right edge (a soft line along the outline, shifted
           up-left and clipped to the shape), which makes flat shapes look round
  ground() a soft shadow on the floor
Cartoon style: flat colours only (one shape per colour, a white shine, no outlines).
"""
import hashlib
import math
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CARDS = ROOT / "app" / "assets" / "art" / "cards"
SIZE = 400


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


def n(v):
    """A number, short."""
    s = f"{v:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    return "0" if s == "-0" else s


# ---------------------------------------------------------------- defs of the card being drawn
_DEFS = {}


def begin():
    _DEFS.clear()


def _h(*parts):
    return hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:7]


def _stops(stops):
    return "".join(f'<stop offset="{s[0]}" stop-color="{s[1]}"' + (f' stop-opacity="{round(s[2], 3)}"' if len(s) > 2 and s[2] != 1 else "") + "/>"
                   for s in stops)


def lg(stops, x1=0, y1=0, x2=0, y2=1, user=False):
    """Linear gradient; stops are (offset, colour[, opacity]); user=True: x/y in drawing units."""
    k = "l" + _h(stops, x1, y1, x2, y2, user)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    _DEFS.setdefault(k, f'<linearGradient id="{k}" x1="{n(x1) if user else x1}" y1="{n(y1) if user else y1}" '
                        f'x2="{n(x2) if user else x2}" y2="{n(y2) if user else y2}"{u}>{_stops(stops)}</linearGradient>')
    return f"url(#{k})"


def rg(stops, cx=.5, cy=.5, r=.5, fx=None, fy=None, user=False, tf=None):
    k = "r" + _h(stops, cx, cy, r, fx, fy, user, tf)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    f = f' fx="{fx}" fy="{fy}"' if fx is not None else ""
    t = f' gradientTransform="{tf}"' if tf else ""
    _DEFS.setdefault(k, f'<radialGradient id="{k}" cx="{cx}" cy="{cy}" r="{r}"{f}{u}{t}>{_stops(stops)}</radialGradient>')
    return f"url(#{k})"


def clip(d):
    k = "c" + _h(d)
    inner = f'<use href="#{ref(d)}"/>' if len(d) > LONG else f'<path d="{d}"/>'
    _DEFS.setdefault(k, f'<clipPath id="{k}">{inner}</clipPath>')
    return f"url(#{k})"


def clipped(d, inner):
    """inner drawn only inside path d (same coordinates)."""
    return f'<g clip-path="{clip(d)}">{inner}</g>'


def doc(body):
    defs = "<defs>" + "".join(_DEFS.values()) + "</defs>" if _DEFS else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" height="{SIZE}">'
            f'{defs}{body}</svg>\n')


def fit(svg, box, fill=.86, dx=0, dy=0):
    """Scale and centre a drawing whose subject covers box (x0, y0, x1, y1) on the 400 card."""
    x0, y0, x1, y1 = box
    s = SIZE * fill / max(x1 - x0, y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return f'<g transform="translate({n(SIZE / 2 - cx * s + dx)} {n(SIZE / 2 - cy * s + dy)}) scale({s:.4f})">{svg}</g>'


def write(deck, cid, body, box, cartoon=False, fill=.86, dx=0, dy=0):
    """body: SVG drawn in its own units (call begin() before drawing it)."""
    out = CARDS / deck
    out.mkdir(parents=True, exist_ok=True)
    p = out / f"{cid}{'_cartoon' if cartoon else ''}.svg"
    text = doc(fit(body, box, fill, dx, dy))
    for bad in ("<filter", "<mask", "<style", "<foreignObject", "style="):
        assert bad not in text, (p.name, bad)
    uses = text.count("<use")
    assert uses <= 600, (p.name, uses)
    if len(text) > 60000:
        print(f"  warning: {p.name} is {len(text) // 1024} KB")
    p.write_text(text)
    return p


# ---------------------------------------------------------------- curves
def spline(pts, k=10, closed=False):
    """Catmull-Rom points through pts (tuples x, y[, width ...])."""
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


def curve(pts, closed=True, start=True):
    """Smooth path through pts as cubic Beziers (compact)."""
    P = [p[:2] for p in pts]
    m = len(P)
    if m < 2:
        return ""
    ext = [P[-1]] + P + [P[0], P[1]] if closed else [P[0]] + P + [P[-1]]
    d = (f"M{n(P[0][0])},{n(P[0][1])}" if start else "")
    segs = m if closed else m - 1
    for i in range(1, segs + 1):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{n(c1[0])},{n(c1[1])} {n(c2[0])},{n(c2[1])} {n(p2[0])},{n(p2[1])}"
    return d + ("Z" if closed else "")


def poly(pts, close=True):
    return "M" + " L".join(f"{n(p[0])},{n(p[1])}" for p in pts) + ("Z" if close else "")


def rpoly(pts, r=6.0):
    """Closed polygon with softly rounded corners; a point may carry its own radius (x, y, r)."""
    m = len(pts)
    d = ""
    for i in range(m):
        a, p, b = pts[i - 1], pts[i], pts[(i + 1) % m]
        rr = p[2] if len(p) > 2 else r
        la, lb = math.hypot(p[0] - a[0], p[1] - a[1]) or 1, math.hypot(b[0] - p[0], b[1] - p[1]) or 1
        ra, rb = min(rr, la / 2), min(rr, lb / 2)
        s = (p[0] - (p[0] - a[0]) * ra / la, p[1] - (p[1] - a[1]) * ra / la)
        e = (p[0] + (b[0] - p[0]) * rb / lb, p[1] + (b[1] - p[1]) * rb / lb)
        d += (f"M{n(s[0])},{n(s[1])}" if i == 0 else f" L{n(s[0])},{n(s[1])}") + f" Q{n(p[0])},{n(p[1])} {n(e[0])},{n(e[1])}"
    return d + "Z"


def _sides(pts, k=4):
    c = spline(pts, k)
    L, R, N = [], [], []
    for i, (x, y, w, *_) in enumerate(c):
        a, b = c[max(0, i - 1)], c[min(len(c) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        N.append((nx, ny))
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    return c, L, R, N


def tube(pts, caps=(True, True), k=1):
    """Outline of a limb, finger, strap...: pts are (x, y, half-width) along its middle."""
    c, L, R, _ = _sides(pts, k)
    d = curve(L, closed=False)
    w1, w0 = c[-1][2], c[0][2]
    d += (f" A{n(w1)},{n(w1)} 0 0 0 {n(R[-1][0])},{n(R[-1][1])}" if caps[1] else f" L{n(R[-1][0])},{n(R[-1][1])}")
    d += curve(list(reversed(R)), closed=False, start=False)
    d += (f" A{n(w0)},{n(w0)} 0 0 0 {n(L[0][0])},{n(L[0][1])}Z" if caps[0] else "Z")
    return d


def along(pts, frac, t0=0.0, t1=1.0, k=2):
    """A line inside a tube at frac of the half-width from the middle (+ = 'left' side)."""
    c, _, _, N = _sides(pts, k)
    i0, i1 = round(t0 * (len(c) - 1)), round(t1 * (len(c) - 1))
    return curve([(c[i][0] + N[i][0] * c[i][2] * frac, c[i][1] + N[i][1] * c[i][2] * frac) for i in range(i0, i1 + 1)], closed=False)


def at(pts, t, k=10):
    """Point, direction (degrees) and half-width at fraction t along a tube."""
    c = spline(pts, k)
    i = min(len(c) - 2, max(0, round(t * (len(c) - 1))))
    a, b = c[i], c[i + 1]
    return a[0], a[1], math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])), a[2]


def ellipse_d(cx, cy, rx, ry):
    return f"M{n(cx - rx)},{n(cy)} A{n(rx)},{n(ry)} 0 1 0 {n(cx + rx)},{n(cy)} A{n(rx)},{n(ry)} 0 1 0 {n(cx - rx)},{n(cy)}Z"


def rrect_d(x, y, w, h, r):
    return (f"M{n(x + r)},{n(y)} H{n(x + w - r)} A{n(r)},{n(r)} 0 0 1 {n(x + w)},{n(y + r)} V{n(y + h - r)} "
            f"A{n(r)},{n(r)} 0 0 1 {n(x + w - r)},{n(y + h)} H{n(x + r)} A{n(r)},{n(r)} 0 0 1 {n(x)},{n(y + h - r)} "
            f"V{n(y + r)} A{n(r)},{n(r)} 0 0 1 {n(x + r)},{n(y)}Z")


def mirror_pts(pts):
    return [(-p[0],) + tuple(p[1:]) for p in pts]


def rot_pt(x, y, deg, cx=0, cy=0):
    a = math.radians(deg)
    x, y = x - cx, y - cy
    return cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)


# ---------------------------------------------------------------- soft light and shade (realistic)
LONG = 120  # paths longer than this are stored once in <defs> and drawn with <use>


def ref(d):
    k = "p" + _h(d)
    _DEFS.setdefault(k, f'<path id="{k}" d="{d}"/>')
    return k


def shp(d, attrs):
    """A path with its paint attributes (all on the element itself, so <use> works the same in flutter_svg)."""
    if len(d) > LONG:
        return f'<use href="#{ref(d)}" {attrs}/>'
    return f'<path d="{d}" {attrs}/>'


def P(d, fill, extra=""):
    return shp(d, f'fill="{fill}"' + ((" " + extra) if extra else ""))


def spot(cx, cy, rx, ry, color, op, rot=0, hard=.0):
    """A soft round patch of colour fading to nothing at its edge (hard: how much stays solid)."""
    g = rg([(0, color, op), (round(.15 + hard * .5, 2), color, op * .9), (round(.5 + hard * .3, 2), color, op * .5), (.78, color, op * .16), (1, color, 0)])
    t = f' transform="rotate({n(rot)} {n(cx)} {n(cy)})"' if rot else ""
    return f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="{g}"{t}/>'


def sline(d, color, w, op, layers=4, cap="round"):
    """A soft line: stacked strokes, wide and faint outside, narrow in the middle."""
    a = 1 - (1 - min(op, .98)) ** (1 / layers)
    if len(d) > LONG:
        return "".join(shp(d, f'fill="none" stroke="{color}" stroke-linecap="{cap}" stroke-linejoin="round" stroke-opacity="{a:.3f}" '
                              f'stroke-width="{n(w * (1 - i / layers))}"') for i in range(layers))
    o = [f'<g fill="none" stroke="{color}" stroke-linecap="{cap}" stroke-linejoin="round" stroke-opacity="{a:.3f}">']
    for i in range(layers):
        o.append(f'<path d="{d}" stroke-width="{n(w * (1 - i / layers))}"/>')
    o.append("</g>")
    return "".join(o)


def rim(d, color, w, op, dx=2.5, dy=3.5, layers=2):
    """Darker rim just inside the lower-right edges of shape d (makes it look round)."""
    return clipped(d, f'<g transform="translate({n(-dx)} {n(-dy)})">{sline(d, color, w * 2, op, layers)}</g>')


def lit(d, color, w, op, dx=2.5, dy=3.5, layers=2):
    """Lighter rim inside the upper-left edges."""
    return rim(d, color, w, op, -dx, -dy, layers)


def ground(cx, cy, rx, ry, op=.18, color="#3A3530"):
    return spot(cx, cy, rx, ry, color, op, hard=.2)


def line(d, color, w, op=1.0, cap="round", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op != 1 else ""
    return shp(d, f'fill="none" stroke="{color}" stroke-width="{n(w)}" stroke-linecap="{cap}" stroke-linejoin="round"{o}{da}')


def hatch(box, step, angle, color, op, w=.6, jitter=None, rng=None, seg=None):
    """Parallel thin lines over box (a fabric weave) as one path; clip it to the cloth."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2
    a = math.radians(angle)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -uy, ux
    parts = []
    k = -R
    while k <= R:
        if seg and rng:
            t = -R
            while t < R:
                ln = rng.uniform(*seg)
                if rng.random() < .7:
                    sx, sy = cx + vx * k + ux * t, cy + vy * k + uy * t
                    parts.append(f"M{n(sx)},{n(sy)}l{n(ux * ln)},{n(uy * ln)}")
                t += ln * rng.uniform(1.2, 2.2)
        else:
            sx, sy = cx + vx * k - ux * R, cy + vy * k - uy * R
            parts.append(f"M{n(sx)},{n(sy)}l{n(2 * R * ux)},{n(2 * R * uy)}")
        k += step + (rng.uniform(-jitter, jitter) if jitter and rng else 0)
    return f'<path d="{"".join(parts)}" fill="none" stroke="{color}" stroke-width="{w}" stroke-opacity="{op}"/>'


def specks(rng, count, box, color, op, r=(.5, 1.1)):
    x0, y0, x1, y1 = box
    parts = []
    for _ in range(count):
        x, y, rr = rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(*r)
        parts.append(f"M{n(x - rr)},{n(y)}a{n(rr)},{n(rr)} 0 1 0 {n(2 * rr)},0a{n(rr)},{n(rr)} 0 1 0 {n(-2 * rr)},0")
    return f'<path d="{"".join(parts)}" fill="{color}" fill-opacity="{op}"/>'


def stitch(d, color, w=1.0, op=.6, dash="3 2.4"):
    return line(d, color, w, op, "butt", dash)


# ---------------------------------------------------------------- the highlight on body cards
GLOW = "#FFE36A"


def glow_ring(cx, cy, rx, ry, rot=0, w=11, op=1.0):
    """Soft pale-yellow glow ring around a body part (realistic cards)."""
    d = ellipse_d(cx, cy, rx, ry)
    t = f' transform="rotate({n(rot)} {n(cx)} {n(cy)})"' if rot else ""
    return (f'<g{t} opacity="{op}">' + sline(d, "#FFF1A6", w * 2.6, .45, 4) + sline(d, GLOW, w * 1.2, .7, 3)
            + line(d, "#FFF6C9", w * .38, .95) + "</g>")


def glow_path(d, w=11, op=1.0):
    """The same glow along any path (e.g. around the hair)."""
    return (f'<g opacity="{op}">' + sline(d, "#FFF1A6", w * 2.6, .45, 4) + sline(d, GLOW, w * 1.2, .7, 3)
            + line(d, "#FFF6C9", w * .38, .95) + "</g>")


def halo(cx, cy, rx, ry, op=1.0):
    """A soft pale-yellow glow behind a part that fills the card (hand, foot)."""
    g = rg([(0, "#FFF6C8", .0), (.5, "#FFF3B5", .35 * op), (.78, "#FFE57A", .75 * op), (.88, "#FFE98E", .45 * op), (1, "#FFF1A6", 0)])
    return f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="{g}"/>'


FLAT_GLOW = "#FFE45E"


def flat_ring(cx, cy, rx, ry, rot=0, w=10):
    """Cartoon highlight: a flat pale-yellow ring with a thin bright edge (no gradients)."""
    t = f' transform="rotate({n(rot)} {n(cx)} {n(cy)})"' if rot else ""
    return (f'<g{t}><ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="none" stroke="#FFF2A8" stroke-width="{n(w * 2)}" stroke-opacity=".75"/>'
            f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="none" stroke="{FLAT_GLOW}" stroke-width="{n(w)}"/></g>')


def flat_disc(cx, cy, rx, ry):
    return (f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" fill="#FFF2A8"/>'
            f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx * .86)}" ry="{n(ry * .86)}" fill="#FFE776"/>')


# ---------------------------------------------------------------- preview (contact sheet)
def preview(out, decks=("body", "clothes")):
    """All cards of decks: realistic and cartoon side by side, big and at phone size (120 px)."""
    import json
    cards = json.loads((ROOT / "design" / "cards.json").read_text())
    names = {c["id"]: c["zh"] for d in cards["decks"] for c in d["cards"]}
    order = [(d["id"], c["id"]) for d in cards["decks"] if d["id"] in decks for c in d["cards"]]
    font = ROOT.parent / "app_kids_paint_for_learning_writing" / "app" / "assets" / "fonts" / "jf-openhuninn-2.1.ttf"
    big, small = 190, 120

    def cell(deck, cid, s):
        src = CARDS / deck
        im = "".join(f'<div class="c" style="width:{s}px;height:{s}px"><img src="file://{src / (cid + suf)}.svg" width="{s}" height="{s}"></div>'
                     for suf in ("", "_cartoon"))
        return f'<div class="cell"><div class="pair">{im}</div><div class="t">{names[cid]} {cid}</div></div>'

    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>@font-face{{font-family:H;src:url("file://{font}")}}'
            '*{margin:0;padding:0}body{background:#ECE7DE;font:15px H,sans-serif;color:#3E4A55;padding:16px;width:2080px}'
            '.g{display:flex;flex-wrap:wrap;gap:14px;margin-bottom:22px}.cell{background:#F7F4EF;border-radius:12px;padding:8px}'
            '.pair{display:flex;gap:6px}.c{background:#fff;border-radius:10px}.t{text-align:center;margin-top:4px}'
            'h2{font-weight:normal;margin:6px 0 10px}</style></head><body>'
            + "".join(f'<h2>{dk_} (190 px)</h2><div class="g">' + "".join(cell(d, c, big) for d, c in order if d == dk_) + "</div>" for dk_ in decks)
            + '<h2>手機上的大小 120 px</h2><div class="g">' + "".join(cell(d, c, small) for d, c in order) + "</div></body></html>")
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp) / "sheet.html"
        p.write_text(html)
        js = pathlib.Path(tmp) / "shot.js"
        js.write_text("const { chromium } = require('playwright');(async () => {const [inp, out] = process.argv.slice(2);"
                      "const b = await chromium.launch();const pg = await b.newPage({viewport:{width:2112,height:800}});"
                      "await pg.goto('file://' + inp);await pg.evaluate(() => document.fonts.ready);await pg.waitForTimeout(400);"
                      "await pg.screenshot({path: out, fullPage: true});await b.close();})();")
        subprocess.run(["node", str(js), str(p), str(out)], check=True)
    print(out)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "preview":
        preview(sys.argv[2], tuple(sys.argv[3:]) or ("body", "clothes"))
    else:
        print(__doc__)

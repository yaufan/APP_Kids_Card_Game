"""Design-stage sketches for the picture-card game (name not decided yet).

    python3 make_mockups.py          # writes docs/mockups/*.png (needs Node.js and Playwright)
    python3 make_mockups.py items    # one big sheet of every drawing, to check them (written to /tmp)

Every picture is drawn here as SVG shapes by code (no outside pictures). render.js turns each
page into a PNG with Playwright's Chromium:

    0_畫風選擇.png     the same apple, dog, red car and cup in two styles
    1..7_*.png         seven phone screens (390x844, at 2x) in style A, realistic
    contact_sheet.png  the seven screens in one row

Style A ("寫實圖鑑風") draws things as they really look: true shapes and colours, soft
gradients, a soft rim shadow (the `vol` filter), a little grain, fur and skin details,
and no faces added to things. Style B ("簡單大色塊風") is flat shapes only.
The font is jf open-huninn from the sibling 字母寵物 checkout.
"""
import hashlib
import math
import pathlib
import random
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
FONT = HERE.parents[2] / "app_kids_paint_for_learning_writing" / "app" / "assets" / "fonts" / "jf-openhuninn-2.1.ttf"
W, H = 390, 844

# ---------------------------------------------------------------- colours (calm)
INK = "#3E4A55"        # slate for words
SOFT = "#8B959D"
BG = "#F3F0EA"         # warm paper white
BG2 = "#E9E4DB"
CARD = "#FFFFFF"
EDGE = "#E2DCD2"       # thin soft card border
TEAL = "#5E9E98"
BLUE = "#6F9CC3"
CORAL = "#E0917A"
SAND = "#E2BC72"
SAGE = "#8FB283"
LILAC = "#A496C6"
ROSE = "#DF98A6"
GOLD = "#F0B93E"


def _rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(x + (y - x) * t))) for x, y in zip(_rgb(a), _rgb(b)))


def lt(c, t):
    return mix(c, "#FFFFFF", t)


def dk(c, t):
    return mix(c, "#1E1A18", t)


# ---------------------------------------------------------------- defs registry
class Defs:
    def __init__(self):
        self.d = {}

    def add(self, key, svg):
        self.d.setdefault(key, svg)
        return key

    def svg(self):
        return "<defs>" + "".join(self.d.values()) + "</defs>"


D = Defs()


def _h(*parts):
    return hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()[:10]


def _stops(stops):
    return "".join(f'<stop offset="{s[0]}" stop-color="{s[1]}"' + (f' stop-opacity="{s[2]}"' if len(s) > 2 else "") + "/>" for s in stops)


def lg(stops, x1=0, y1=0, x2=0, y2=1, user=False):
    """Linear gradient. stops: (offset, colour[, opacity]). user=True: x/y in the drawing's own units."""
    k = "lg" + _h(stops, x1, y1, x2, y2, user)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    D.add(k, f'<linearGradient id="{k}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{u}>{_stops(stops)}</linearGradient>')
    return f"url(#{k})"


def rg(stops, cx=.5, cy=.5, r=.5, fx=None, fy=None, user=False):
    k = "rg" + _h(stops, cx, cy, r, fx, fy, user)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    f = f' fx="{fx}" fy="{fy}"' if fx is not None else ""
    D.add(k, f'<radialGradient id="{k}" cx="{cx}" cy="{cy}" r="{r}"{f}{u}>{_stops(stops)}</radialGradient>')
    return f"url(#{k})"


def clip(d):
    k = "cp" + _h(d)
    D.add(k, f'<clipPath id="{k}"><path d="{d}"/></clipPath>')
    return f"url(#{k})"


def blur(sd):
    k = "bl" + str(sd).replace(".", "_")
    D.add(k, f'<filter id="{k}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="{sd}"/></filter>')
    return f"url(#{k})"


def vol(r=6, op=.4, dx=2.5, dy=3.5, dark="#3A1E10", light=0.0):
    """Soft roundness for a whole drawing: a darker rim inside the edges facing down-right
    (and optionally a light rim top-left). Not puffy like clay: no bevel, no shine."""
    k = "vol" + _h(r, op, dx, dy, dark, light)
    lit = ""
    if light:
        lit = (f'<feOffset in="b" dx="{dx}" dy="{dy}" result="bo2"/>'
               '<feComposite in="SourceAlpha" in2="bo2" operator="arithmetic" k2="1.6" k3="-1.6" result="rim2"/>'
               f'<feFlood flood-color="#FFFFFF" flood-opacity="{light}"/><feComposite in2="rim2" operator="in" result="litc"/>')
    D.add(k, f'<filter id="{k}" x="-8%" y="-8%" width="116%" height="116%" color-interpolation-filters="sRGB">'
             f'<feGaussianBlur in="SourceAlpha" stdDeviation="{r}" result="b"/>'
             f'<feOffset in="b" dx="{-dx}" dy="{-dy}" result="bo"/>'
             '<feComposite in="SourceAlpha" in2="bo" operator="arithmetic" k2="1.6" k3="-1.6" result="rim"/>'
             f'<feFlood flood-color="{dark}" flood-opacity="{op}"/><feComposite in2="rim" operator="in" result="rimc"/>'
             f'{lit}<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="rimc"/>'
             + ('<feMergeNode in="litc"/>' if light else "") + '</feMerge></filter>')
    return f"url(#{k})"


def grain(s=.07, freq=.85, seed=3):
    """A little paper-print texture on a drawing (tiny light and dark specks)."""
    k = "gr" + _h(s, freq, seed)
    D.add(k, f'<filter id="{k}" x="-6%" y="-6%" width="112%" height="112%" color-interpolation-filters="sRGB">'
             f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="2" seed="{seed}" result="n"/>'
             '<feColorMatrix in="n" type="matrix" values=".33 .33 .33 0 0 .33 .33 .33 0 0 .33 .33 .33 0 0 0 0 0 0 1" result="g"/>'
             f'<feComposite in="SourceGraphic" in2="g" operator="arithmetic" k2="1" k3="{s}" k4="{-s / 2}" result="t"/>'
             '<feComposite in="t" in2="SourceAlpha" operator="in"/></filter>')
    return f"url(#{k})"


def card_shadow(op=.13, dy=6, sd=9):
    k = "cs" + _h(op, dy, sd)
    D.add(k, f'<filter id="{k}" x="-20%" y="-20%" width="140%" height="150%">'
             f'<feDropShadow dx="0" dy="{dy}" stdDeviation="{sd}" flood-color="#4A535C" flood-opacity="{op}"/></filter>')
    return f"url(#{k})"


# ---------------------------------------------------------------- curve helpers
def spline(pts, n=10, closed=False):
    """Catmull-Rom curve through pts (tuples of any length: x, y[, width])."""
    P = list(pts)
    P = [P[-1]] + P + [P[0], P[1]] if closed else [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(n):
            t = j / n
            out.append(tuple(.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3)
                             for a, b, c, d in zip(p0, p1, p2, p3)))
    if not closed:
        out.append(tuple(P[-2]))
    return out


def poly(pts, close=True):
    return "M" + " L".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts) + ("Z" if close else "")


def blob(pts, n=8):
    """Smooth closed shape through pts."""
    return poly(spline(pts, n, closed=True))


def _sides(pts, n=10):
    c = spline(pts, n)
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


def tube(pts, n=10, caps=(True, True)):
    """Outline of a limb, tail, finger...: pts are (x, y, half-width) along its middle."""
    c, L, R, _ = _sides(pts, n)
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in L)
    w1, w0 = c[-1][2], c[0][2]
    d += (f" A{w1:.1f},{w1:.1f} 0 0 0 {R[-1][0]:.1f},{R[-1][1]:.1f}" if caps[1] else f" L{R[-1][0]:.1f},{R[-1][1]:.1f}")
    d += " L" + " L".join(f"{x:.1f},{y:.1f}" for x, y in reversed(R))
    d += (f" A{w0:.1f},{w0:.1f} 0 0 0 {L[0][0]:.1f},{L[0][1]:.1f}Z" if caps[0] else "Z")
    return d


def along(pts, frac, t0=0.0, t1=1.0, n=10):
    """A line inside a tube, at frac of the half-width from the middle (+ = the 'left' side)."""
    c, _, _, N = _sides(pts, n)
    i0, i1 = round(t0 * (len(c) - 1)), round(t1 * (len(c) - 1))
    return poly([(c[i][0] + N[i][0] * c[i][2] * frac, c[i][1] + N[i][1] * c[i][2] * frac) for i in range(i0, i1 + 1)], close=False)


def at(pts, t, n=10):
    """Point, direction angle and half-width at fraction t along a tube."""
    c = spline(pts, n)
    i = min(len(c) - 2, max(0, round(t * (len(c) - 1))))
    a, b = c[i], c[i + 1]
    return a[0], a[1], math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])), a[2]


def strokes(rng, n, box, angle, colors, length=(5, 9), width=1.0, op=.3, curve=.18):
    """Many short soft strokes (fur, fabric) inside box; angle(x, y) gives their direction (radians)."""
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        a = angle(x, y) + rng.uniform(-.28, .28)
        ln = rng.uniform(*length)
        ex, ey = x + math.cos(a) * ln, y + math.sin(a) * ln
        mx, my = (x + ex) / 2 + math.cos(a + 1.57) * ln * curve, (y + ey) / 2 + math.sin(a + 1.57) * ln * curve
        out.append(f'<path d="M{x:.1f},{y:.1f} Q{mx:.1f},{my:.1f} {ex:.1f},{ey:.1f}" stroke="{rng.choice(colors)}"/>')
    return f'<g fill="none" stroke-width="{width}" stroke-linecap="round" opacity="{op}">{"".join(out)}</g>'


def ground(cx, cy, rx, ry, op=.2):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#2E3238" opacity="{op}" filter="{blur(round(ry * .7, 1))}"/>'


def soft(shape, sd, extra=""):
    """A blurred shading shape (inside a clipped group)."""
    return f'<g filter="{blur(sd)}" {extra}>{shape}</g>'


def star_path(R, r, n=5, cx=0, cy=0, rot=-90):
    pts = []
    for i in range(2 * n):
        a = math.radians(rot + i * 180 / n)
        rr = R if i % 2 == 0 else r
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return poly(pts)


def heart_path(s=1.0, cx=0, cy=0):
    return (f"M{cx},{cy + 26 * s} C{cx - 34 * s},{cy + 4 * s} {cx - 32 * s},{cy - 26 * s} {cx - 14 * s},{cy - 26 * s} "
            f"C{cx - 5 * s},{cy - 26 * s} {cx},{cy - 18 * s} {cx},{cy - 13 * s} C{cx},{cy - 18 * s} {cx + 5 * s},{cy - 26 * s} {cx + 14 * s},{cy - 26 * s} "
            f"C{cx + 32 * s},{cy - 26 * s} {cx + 34 * s},{cy + 4 * s} {cx},{cy + 26 * s}Z")


# ================================================================ style A: realistic drawings
# Each returns SVG in its own units; BOX[name] is the area it covers (x0, y0, x1, y1).
BOX = {}


def apple():
    body = ("M0,-58 C14,-72 44,-80 68,-66 C92,-52 98,-18 92,12 C86,44 70,72 48,82 C34,88 20,86 10,82 "
            "C4,80 -4,80 -10,82 C-20,86 -34,88 -48,82 C-70,72 -86,44 -92,12 C-98,-18 -92,-52 -68,-66 C-44,-80 -14,-72 0,-58Z")
    rng = random.Random(7)
    inner = [f'<path d="{body}" fill="{rg([(0, "#F25A45"), (.42, "#D02B25"), (.78, "#A0181B"), (1, "#6C0D12")], cx=.38, cy=.38, r=.7, fx=.32, fy=.3)}"/>',
             soft('<ellipse cx="56" cy="34" rx="36" ry="38" fill="#EDA548" opacity=".30"/>', 14)]
    st = []
    for i in range(30):
        t = -1 + 2 * i / 29 + rng.uniform(-.03, .03)
        st.append(f'<path d="M{t * 18:.1f},-56 Q{t * 106:.1f},{-4 + abs(t) * 4:.1f} {t * 50:.1f},{86 - abs(t) * 12:.1f}" '
                  f'stroke="{"#F68560" if i % 2 else "#7A0F14"}" stroke-width="{rng.uniform(2.5, 6.5):.1f}" opacity="{rng.uniform(.12, .28):.2f}"/>')
    inner.append(soft(f'<g fill="none">{"".join(st)}</g>', 1.6))
    inner.append('<g fill="#FBDDB0" opacity=".5">' + "".join(
        f'<ellipse cx="{rng.uniform(-92, 92):.1f}" cy="{rng.uniform(-62, 86):.1f}" rx="{rng.uniform(.6, 1.3):.1f}" ry="{rng.uniform(.5, 1):.1f}"/>' for _ in range(110)) + '</g>')
    inner.append(soft('<ellipse cx="0" cy="-54" rx="26" ry="11" fill="#45080C" opacity=".6"/>', 5))
    inner.append(soft('<path d="M-34,-64 Q0,-44 34,-64" stroke="#FF9478" stroke-width="3" fill="none" opacity=".45"/>', 1.5))
    inner.append(soft('<ellipse cx="-48" cy="-22" rx="20" ry="32" transform="rotate(18 -48 -22)" fill="#fff" opacity=".26"/>', 9))
    inner.append(soft('<ellipse cx="-54" cy="-34" rx="5" ry="10" transform="rotate(24 -54 -34)" fill="#fff" opacity=".8"/>', 1.6))
    inner.append(soft('<path d="M-72,58 Q0,104 72,58" stroke="#FF8D74" stroke-width="9" fill="none" opacity=".22"/>', 4))
    o = [ground(0, 88, 72, 8, .16),
         f'<g filter="{vol(7, .35)}"><g clip-path="{clip(body)}">{"".join(inner)}</g></g>']
    stem = [(0, -50, 3.2), (1, -68, 2.9), (4, -86, 2.5), (10, -99, 2.4)]
    o.append(f'<path d="{tube(stem)}" fill="{lg([(0, "#7A5634"), (1, "#3F2814")], 0, 0, 1, 0)}"/>')
    o.append(f'<ellipse cx="10" cy="-99" rx="2.6" ry="1.6" transform="rotate(-30 10 -99)" fill="#A88760"/>')
    leaf = "M6,-80 C14,-104 44,-114 66,-104 C54,-86 28,-74 6,-80Z"
    o.append(f'<path d="{leaf}" fill="{lg([(0, "#5E9A34"), (.6, "#4C8A2E"), (1, "#3A6E24")], 0, 0, 1, 1)}"/>')
    o.append(f'<g clip-path="{clip(leaf)}">' + soft('<ellipse cx="30" cy="-102" rx="26" ry="7" transform="rotate(-14 30 -102)" fill="#BFE08A" opacity=".45"/>', 4)
             + '<path d="M8,-80 Q36,-96 64,-104" stroke="#B9DB86" stroke-width="1.4" fill="none" opacity=".8"/>'
             + "".join(f'<path d="M{18 + 10 * i},{-85 - 4 * i} q{4 - i * .3},{-7} {9},{-11}" stroke="#A9CF78" stroke-width=".8" fill="none" opacity=".6"/>'
                       f'<path d="M{18 + 10 * i},{-85 - 4 * i} q{2},{5} {9},{6}" stroke="#A9CF78" stroke-width=".8" fill="none" opacity=".45"/>' for i in range(4))
             + '</g>')
    return f'<g filter="{grain(.06)}">{"".join(o)}</g>'


BOX["apple"] = (-100, -116, 100, 98)


def banana(shadow=False, color=None):
    """One ripe banana lying on its side. shadow=True: the same outline filled with one dark colour."""
    mid = [(-100, -10, 3.5), (-80, 12, 12), (-46, 30, 19), (-6, 37, 21.5), (34, 30, 20.5), (66, 10, 16), (88, -14, 10), (96, -28, 6.5)]
    stalk = [(94, -25, 5.2), (101, -38, 4.6), (108, -50, 5.4)]
    body = tube(mid)
    if shadow:
        c = color or "#38424D"
        return (f'<g><path d="{body}" fill="{c}"/><path d="{tube(stalk)}" fill="{c}"/>'
                f'<ellipse cx="108" cy="-51" rx="6" ry="4" transform="rotate(-30 108 -51)" fill="{c}"/></g>')
    rng = random.Random(4)
    inner = [f'<path d="{body}" fill="#EFC93A"/>',
             soft(f'<path d="{along(mid, .55)}" stroke="#C99418" stroke-width="16" fill="none" opacity=".75"/>', 5),
             soft(f'<path d="{along(mid, .95)}" stroke="#A97A12" stroke-width="7" fill="none" opacity=".6"/>', 3),
             soft(f'<path d="{along(mid, -.45, .1, .9)}" stroke="#FFF0A0" stroke-width="10" fill="none" opacity=".85"/>', 4),
             soft(f'<path d="{along(mid, -.4, .25, .7)}" stroke="#FFFFFF" stroke-width="3" fill="none" opacity=".55"/>', 1.5),
             f'<path d="{along(mid, .05, .06, .96)}" stroke="#D6A626" stroke-width="1.2" fill="none" opacity=".55"/>',
             f'<path d="{along(mid, -.62, .1, .94)}" stroke="#E2B530" stroke-width="1" fill="none" opacity=".5"/>',
             soft('<ellipse cx="86" cy="-12" rx="24" ry="20" fill="#9DAA2E" opacity=".55"/>', 8),
             soft('<ellipse cx="-96" cy="-8" rx="9" ry="9" fill="#6A4A1A" opacity=".8"/>', 3)]
    for _ in range(16):
        x, y, a, w = at(mid, rng.uniform(.15, .85))
        f = rng.uniform(-.7, .8)
        inner.append(f'<ellipse cx="{x + math.cos(math.radians(a + 90)) * w * f:.1f}" cy="{y + math.sin(math.radians(a + 90)) * w * f:.1f}" '
                     f'rx="{rng.uniform(.8, 1.8):.1f}" ry="{rng.uniform(.6, 1.2):.1f}" fill="#7A5420" opacity="{rng.uniform(.25, .5):.2f}"/>')
    o = [ground(0, 56, 92, 7, .14),
         f'<g filter="{vol(5, .3)}"><g clip-path="{clip(body)}">{"".join(inner)}</g>'
         f'<path d="{tube(stalk)}" fill="{lg([(0, "#8E9A3A"), (1, "#5E6A26")], 0, 0, 1, 0)}"/></g>',
         f'<ellipse cx="108" cy="-51" rx="5.6" ry="3.8" transform="rotate(-30 108 -51)" fill="#7A6A3A"/>',
         f'<ellipse cx="108" cy="-51" rx="3.6" ry="2.2" transform="rotate(-30 108 -51)" fill="#A99A64"/>',
         f'<circle cx="-101" cy="-11" r="3.4" fill="#3A2812"/>']
    return f'<g filter="{grain(.06)}">{"".join(o)}</g>'


BOX["banana"] = (-108, -60, 116, 64)


def car():
    """A small red hatchback seen from the side."""
    body = ("M-118,26 L-120,4 C-121,-10 -117,-20 -108,-25 L-94,-30 C-80,-54 -66,-64 -40,-67 L18,-67 "
            "C38,-67 52,-60 70,-38 L100,-31 C113,-28 120,-20 121,-6 L122,20 C122,27 118,30 112,30 L101,30 "
            "A29,29 0 0 0 43,30 L-41,30 A29,29 0 0 0 -99,30 L-110,30 C-115,30 -118,29 -118,26Z")
    glass = "M-86,-31 C-74,-51 -62,-59 -40,-60 L16,-60 C32,-60 44,-54 60,-35 Z"
    chrome = lg([(0, "#F2F2F2"), (1, "#9CA0A6")])
    o = [ground(0, 56, 128, 8, .28)]
    inner = [f'<path d="{body}" fill="{lg([(0, "#E8433A"), (.42, "#C91F1E"), (.7, "#A3161A"), (1, "#6E0C10")])}"/>',
             soft('<path d="M-112,-20 L102,-24" stroke="#FF8C80" stroke-width="7" fill="none" opacity=".55"/>', 3),
             soft('<rect x="-116" y="-14" width="236" height="10" fill="#FFFFFF" opacity=".18"/>', 3),
             soft('<path d="M-120,10 L122,8" stroke="#5A0A0E" stroke-width="12" fill="none" opacity=".35"/>', 5),
             '<path d="M-114,-17 C-40,-20 40,-22 108,-24" stroke="#7E1015" stroke-width="1.2" fill="none" opacity=".6"/>',
             '<path d="M-114,-15.5 C-40,-18.5 40,-20.5 108,-22.5" stroke="#FF9A8E" stroke-width="1" fill="none" opacity=".5"/>',
             '<path d="M-38,-60 L-41,28 M28,-58 C30,-30 34,-4 38,22" stroke="#6A0B10" stroke-width="1.3" fill="none" opacity=".7"/>',
             '<path d="M-36,-60 L-39,28 M30,-58 C32,-30 36,-4 40,22" stroke="#FF8A7E" stroke-width=".8" fill="none" opacity=".35"/>',
             '<path d="M-124,20 C-60,22 60,22 126,19 L126,34 L-124,34Z" fill="#2B2D31"/>',
             '<path d="M-124,20 C-60,22 60,22 126,19" stroke="#5A5D63" stroke-width="1.2" fill="none"/>',
             '<rect x="108" y="2" width="16" height="6" rx="3" fill="#2B2D31"/>']
    o.append(f'<g filter="{vol(6, .35, dark="#30060A")}"><g clip-path="{clip(body)}">{"".join(inner)}</g></g>')
    for wx in (-70, 72):
        o.append(f'<path d="M{wx - 29},30 A29,29 0 0 1 {wx + 29},30Z" fill="#1A1B1E"/>')
    o.append(f'<path d="{glass}" fill="{lg([(0, "#5F7385"), (.5, "#2F3E4C"), (1, "#1C252E")])}"/>')
    o.append(f'<g clip-path="{clip(glass)}">' + soft('<path d="M-30,-70 L-6,-70 L-36,-24 L-60,-24Z" fill="#E8F2F8" opacity=".35"/>', 3)
             + soft('<path d="M6,-70 L16,-70 L-12,-24 L-22,-24Z" fill="#E8F2F8" opacity=".25"/>', 2)
             + '<path d="M-41,-64 L-39,-28 L-31,-28 L-33,-64Z" fill="#1A1E23"/>'
             + '<path d="M-86,-31 L60,-35" stroke="#11171D" stroke-width="2"/></g>')
    o.append('<path d="M-86,-31 C-74,-51 -62,-59 -40,-60 L16,-60 C32,-60 44,-54 60,-35" stroke="#2A0406" stroke-width="2.2" fill="none" opacity=".55"/>')
    o.append(f'<path d="M58,-38 C58,-46 64,-48 72,-47 L74,-38Z" fill="{lg([(0, "#E23A33"), (1, "#8A1015")])}"/>')
    o.append('<path d="M60,-38 L74,-38" stroke="#1B1D20" stroke-width="2"/>')
    o.append(f'<rect x="-20" y="-20" width="14" height="4" rx="2" fill="{chrome}"/><rect x="-82" y="-21" width="13" height="4" rx="2" fill="{chrome}"/>')
    o.append(f'<path d="M104,-28 C112,-26 117,-21 119,-13 L106,-15 C102,-18 101,-24 104,-28Z" fill="{lg([(0, "#FFFFFF"), (.5, "#DDE6EC"), (1, "#9AA8B2")], 0, 0, 1, 1)}"/>')
    o.append('<path d="M106,-24 C110,-23 113,-20 115,-16" stroke="#FFFFFF" stroke-width="1.4" fill="none" opacity=".9"/>')
    o.append(f'<path d="M-119,-17 C-117,-22 -113,-24.5 -109,-25.5 L-107,-12 L-119.5,-10Z" fill="{lg([(0, "#FF7A5A"), (.5, "#D0221E"), (1, "#7E0A10")])}"/>')
    o.append('<path d="M-117,-18 L-110,-22" stroke="#FFD0C0" stroke-width="1" opacity=".7"/>')
    o.append('<rect x="116" y="-3" width="6" height="3" rx="1.5" fill="#FFB23A" opacity=".9"/>')
    for wx in (-70, 72):
        o.append(f'<circle cx="{wx}" cy="30" r="25" fill="{rg([(0, "#3A3C40"), (.8, "#24262A"), (1, "#111214")])}"/>')
        o.append(f'<circle cx="{wx}" cy="30" r="15.5" fill="{rg([(0, "#F4F6F8"), (.6, "#C2C8CE"), (1, "#7C848C")], cx=.4, cy=.35, r=.7)}"/>')
        sp = "".join(f'<path d="M{wx},30 L{wx + 14 * math.cos(math.radians(a - 8)):.1f},{30 + 14 * math.sin(math.radians(a - 8)):.1f} '
                     f'L{wx + 14 * math.cos(math.radians(a + 8)):.1f},{30 + 14 * math.sin(math.radians(a + 8)):.1f}Z"/>' for a in range(-90, 270, 72))
        o.append(f'<g fill="#5B636B" opacity=".55">{sp}</g>')
        o.append(f'<circle cx="{wx}" cy="30" r="4.5" fill="{rg([(0, "#FFFFFF"), (1, "#8C949C")], cx=.4, cy=.35)}"/>')
        o.append(f'<circle cx="{wx}" cy="30" r="15.5" fill="none" stroke="#5B636B" stroke-width="1.2"/>')
        o.append(soft(f'<path d="M{wx - 20},18 A23,23 0 0 1 {wx + 6},7" stroke="#FFFFFF" stroke-width="2" fill="none" opacity=".25"/>', .8))
    return f'<g filter="{grain(.05)}">{"".join(o)}</g>'


BOX["car"] = (-126, -72, 128, 66)


def cup(color="#5B93B5"):
    """A ceramic mug, seen a little from above."""
    rx, ry, top, bot = 50, 11, -58, 58
    bodyd = f"M{-rx},{top} L{-rx + 3},{bot} A{rx - 3},{ry - 1} 0 0 0 {rx - 3},{bot} L{rx},{top} A{rx},{ry} 0 0 1 {-rx},{top}Z"
    o = [ground(14, bot + 9, 70, 8, .2)]
    handle = "M46,-34 C92,-42 94,30 44,30"
    o.append(f'<path d="{handle}" stroke="{dk(color, .3)}" stroke-width="15" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="{handle}" stroke="{color}" stroke-width="10" fill="none" stroke-linecap="round" transform="translate(-1 -1.5)"/>')
    o.append(soft(f'<path d="M54,-35 C86,-38 88,16 66,24" stroke="{lt(color, .5)}" stroke-width="3" fill="none" opacity=".8"/>', 1.2))
    inner = [f'<path d="{bodyd}" fill="{lg([(0, dk(color, .35)), (.1, dk(color, .1)), (.28, lt(color, .45)), (.4, lt(color, .2)), (.7, color), (.92, dk(color, .25)), (1, dk(color, .45))], 0, 0, 1, 0)}"/>',
             soft(f'<rect x="-31" y="{top + 12}" width="8" height="{bot - top - 10}" fill="#FFFFFF" opacity=".45"/>', 3),
             f'<rect x="-60" y="{top}" width="120" height="{bot - top + 14}" fill="{lg([(0, "#0E1E2A", 0), (.6, "#0E1E2A", 0), (1, "#0E1E2A", .35)])}"/>',
             soft(f'<rect x="32" y="{top + 12}" width="5" height="{bot - top - 12}" fill="#FFFFFF" opacity=".12"/>', 3)]
    o.append(f'<g clip-path="{clip(bodyd)}">{"".join(inner)}</g>')
    o.append(f'<ellipse cx="0" cy="{top}" rx="{rx}" ry="{ry}" fill="{lt(color, .7)}"/>')
    ind = f"M{-rx + 4},{top + .6} A{rx - 4},{ry - 2.2} 0 0 1 {rx - 4},{top + .6} A{rx - 4},{ry - 2.2} 0 0 1 {-rx + 4},{top + .6}Z"
    o.append(f'<path d="{ind}" fill="{lg([(0, lt(color, .25)), (.5, color), (1, dk(color, .35))])}"/>')
    o.append(f'<g clip-path="{clip(ind)}">' + soft(f'<ellipse cx="0" cy="{top + 9}" rx="{rx}" ry="5" fill="{dk(color, .55)}" opacity=".55"/>', 2.5)
             + soft(f'<ellipse cx="-30" cy="{top - 3}" rx="16" ry="3" fill="#FFFFFF" opacity=".25"/>', 2) + '</g>')
    o.append(f'<path d="M{-rx},{top} A{rx},{ry} 0 0 0 {rx},{top}" stroke="#FFFFFF" stroke-width="1.4" fill="none" opacity=".85"/>')
    return f'<g transform="translate(-16 0)">{"".join(o)}</g>'


BOX["cup"] = (-74, -74, 84, 74)


# ---------------------------------------------------------------- dog (Shiba Inu, standing, side view, with a collar)
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


def dog():
    rng = random.Random(11)
    o = [ground(-10, 90, 100, 7, .22)]
    farf = [(42, 30, 8.5), (43, 58, 7.5), (45, 82, 7)]
    farh = [(-50, 18, 11), (-58, 44, 8.5), (-62, 62, 7), (-60, 83, 6.6)]
    back = []
    for leg, paw in ((farf, (50, 86)), (farh, (-54, 86))):
        back.append(f'<path d="{tube(leg)}" fill="{lg([(0, "#9C5220"), (.55, "#B8743A"), (.75, "#D8C3A6"), (1, "#C9B394")])}"/>')
        back.append(f'<ellipse cx="{paw[0]}" cy="{paw[1]}" rx="9.5" ry="3.8" fill="#C2AC8C"/>')
    o.append(f'<g filter="{vol(4, .45)}">{"".join(back)}</g>')
    inner = [f'<path d="{DOG}" fill="{lg([(0, "#B5652A"), (.3, FUR), (.62, "#DD9552"), (1, "#E8B47A")], 0, -30, 0, 90, user=True)}"/>',
             soft('<path d="M-80,-22 C-40,-32 10,-34 40,-42 L66,-82" stroke="#8E4A1A" stroke-width="16" fill="none" opacity=".5"/>', 7),
             soft('<ellipse cx="-8" cy="-4" rx="52" ry="15" fill="#F2B270" opacity=".45"/>', 10),
             soft('<path d="M28,-26 C38,-8 42,14 38,38" stroke="#9A5222" stroke-width="5" fill="none" opacity=".4"/>', 3.5),
             soft('<path d="M-42,-22 C-30,-6 -34,16 -46,28" stroke="#9A5222" stroke-width="6" fill="none" opacity=".38"/>', 4),
             soft('<ellipse cx="-62" cy="6" rx="16" ry="20" fill="#F0AE6C" opacity=".45"/>', 7)]
    cream = [blob([(128, -52), (110, -54), (99, -58), (90, -64), (80, -62), (72, -54), (66, -40), (62, -20), (58, 4), (54, 30),
                   (46, 40), (60, 60), (84, 20), (110, -20), (132, -34)]),
             blob([(38, 42), (28, 34), (6, 29), (-18, 24), (-32, 22), (-44, 34), (-46, 48), (-30, 40), (-6, 38), (24, 44)]),
             blob([(-54, 62), (-52, 92), (-76, 94), (-75, 72), (-64, 66)]),
             blob([(30, 64), (29, 92), (61, 94), (54, 64)])]
    inner.append(soft("".join(f'<path d="{c}" fill="{CREAM}"/>' for c in cream), 2.2))
    inner.append(soft('<ellipse cx="89" cy="-81" rx="4.5" ry="3" fill="#F1D9B4" opacity=".9"/>', 1.2))
    inner.append(soft('<path d="M115,-60 C107,-60 100,-64 96,-70" stroke="#B0612A" stroke-width="5" fill="none" opacity=".5"/>', 2.5))
    inner.append(soft('<ellipse cx="76" cy="-52" rx="12" ry="9" fill="#EFC998" opacity=".45"/>', 4))

    def flow(x, y):
        if y > 36:
            return math.radians(92)
        if x > 56:
            return math.radians(118 if y > -40 else 150)
        return math.radians(172 + (y + 10) * .5)
    inner.append(strokes(rng, 380, (-86, -40, 126, 92), flow, ["#F3BE84", "#8E4A1A", "#FFE2BC", "#B66A2E"], (4, 7), .85, .28))
    inner.append(strokes(rng, 110, (-86, 10, 60, 92), flow, ["#FFFFFF", "#D7C2A3"], (4, 6), .8, .3))
    # collar
    inner.append(soft('<path d="M44,-58 C52,-42 62,-30 78,-22" stroke="#3A1E10" stroke-width="9" fill="none" opacity=".35"/>', 1.5))
    inner.append(f'<path d="M45,-58 C53,-42 63,-31 79,-24" stroke="{lg([(0, "#3F86B0"), (1, "#24597A")], 0, 0, 1, 1)}" stroke-width="6.5" fill="none"/>')
    inner.append('<path d="M46,-59.5 C54,-44 64,-33 79.6,-26" stroke="#8CC2E0" stroke-width="1.2" fill="none" opacity=".7"/>')
    o.append(f'<g clip-path="{clip(DOG)}">{"".join(inner)}</g>')
    o.append(f'<circle cx="72" cy="-21" r="3.4" fill="none" stroke="#C9CDD2" stroke-width="1.4"/>'
             f'<circle cx="72.5" cy="-14.5" r="4.6" fill="{rg([(0, "#FFE9A0"), (1, "#C9962A")], cx=.4, cy=.35)}"/>')
    tufts = []
    for (x, y, a, c) in [(63, 2, 160, CREAM), (59, 14, 170, CREAM), (56, 26, 175, CREAM), (67, -8, 150, CREAM),
                         (-82, 6, 190, FUR), (-82, 18, 195, FUR), (-78, -16, 200, FUR)]:
        a = math.radians(a)
        tufts.append(f'<path d="M{x:.1f},{y:.1f} q{math.cos(a) * 3:.1f},{math.sin(a) * 3:.1f} {math.cos(a) * 4.5 + 2:.1f},{math.sin(a) * 4.5 + 1.5:.1f}" stroke="{c}"/>')
    o.append(f'<g fill="none" stroke-width="1.6" stroke-linecap="round" opacity=".8">{"".join(tufts)}</g>')
    body = f'<g filter="{vol(6, .38)}">{"".join(o[1:])}</g>'
    far_ear = '<path d="M72,-90 C73,-97 74,-103 75,-107 C71,-102 66,-96 61,-92Z" fill="#9A5220"/>'
    tl = [(-58, -27, 8.5), (-66, -42, 10), (-60, -59, 10.5), (-43, -63, 10), (-32, -52, 9), (-36, -40, 7.5), (-46, -36, 5.5)]
    tail = (f'<g filter="{vol(4, .4)}"><path d="{tube(tl)}" fill="{lg([(0, "#E9AE6E"), (.5, FUR), (1, "#A95E28")], 0, 0, 1, 1)}"/>'
            f'<g clip-path="{clip(tube(tl))}">'
            + soft(f'<path d="{along(tl, .6, .15, .95)}" stroke="{CREAM}" stroke-width="7" fill="none"/>', 2.5)
            + soft('<ellipse cx="-50" cy="-48" rx="6" ry="5" fill="#7A3E14" opacity=".55"/>', 2.5)
            + strokes(random.Random(5), 150, (-80, -76, -20, -24), lambda x, y: math.atan2(y + 48, x + 50) + 1.7, ["#F7CB96", "#8E4A1A", "#FFF1DD"], (4, 7), .8, .38)
            + '</g></g>')
    face = ('<path d="M122,-50 C121,-55.5 117,-58.5 113,-58.5 C111,-56 111,-51 113,-48 C116,-46 120,-46 122,-50Z" fill="#1C1714"/>'
            + soft('<ellipse cx="117" cy="-55.5" rx="3" ry="1.6" fill="#FFFFFF" opacity=".55"/>', .6)
            + '<path d="M116,-46.5 C113,-43.5 107,-41.5 101,-41.5" stroke="#3A2516" stroke-width="1.2" fill="none" stroke-linecap="round" opacity=".85"/>'
            + '<path d="M101,-41.5 C99,-41.6 97.5,-42.4 96.5,-43.6" stroke="#3A2516" stroke-width=".9" fill="none" stroke-linecap="round" opacity=".55"/>'
            + '<ellipse cx="90" cy="-73.5" rx="4.8" ry="3.6" transform="rotate(-14 90 -73.5)" fill="#2A1A10"/>'
            + '<ellipse cx="90.4" cy="-73.5" rx="3" ry="2.5" fill="#4A2E1A"/>'
            + '<circle cx="91.7" cy="-74.9" r="1" fill="#FFFFFF" opacity=".9"/>'
            + '<path d="M85.2,-73 C87,-76.8 92,-77.8 95.2,-75" stroke="#3A2212" stroke-width="1" fill="none" opacity=".7"/>'
            + soft('<path d="M83,-101 L75,-90" stroke="#7E3E14" stroke-width="3" opacity=".55"/>', 1.2)
            + '<g fill="#3A2516" opacity=".45"><circle cx="107" cy="-51" r=".7"/><circle cx="103" cy="-50" r=".7"/><circle cx="105" cy="-48" r=".7"/><circle cx="109" cy="-49" r=".7"/></g>')
    return f'<g filter="{grain(.06)}">{o[0]}{far_ear}{body}{tail}{face}</g>'


BOX["dog"] = (-90, -112, 130, 98)


# ---------------------------------------------------------------- cat (grey tabby, sitting, side view)
CAT = ("M74,-53 C73,-58 71,-62 67,-66 C64,-70 62,-74 60,-78 C58,-86 55,-96 52,-106 C46,-99 40,-92 34,-86 "
       "C26,-82 20,-74 18,-64 C15,-52 6,-42 -6,-32 C-26,-16 -44,6 -52,30 C-58,46 -60,64 -56,76 "
       "C-53,84 -46,88 -38,88 L58,88 C62,88 63,83 59,81 C56,80 54,78 54,74 C53,56 52,30 52,10 "
       "C52,-4 50,-16 48,-26 C52,-32 58,-36 64,-38 C69,-40 73,-45 74,-49 C75,-51 75,-52 74,-53Z")


def cat():
    rng = random.Random(21)
    base, light, stripe = "#9C958B", "#E4DFD5", "#4B4641"
    o = [ground(0, 92, 80, 6, .2)]
    o.append('<path d="M30,-84 C33,-92 36,-100 40,-108 C44,-100 46,-94 46,-88Z" fill="#6E6860"/>')
    inner = [f'<path d="{CAT}" fill="{lg([(0, "#7F786F"), (.35, base), (1, "#B5AFA5")], 0, -100, 0, 90, user=True)}"/>',
             soft(blob([(80, -44), (66, -40), (56, -34), (50, -20), (48, 10), (50, 60), (62, 60), (66, 0), (82, -30)]), 3, f'fill="{light}"'),
             soft(f'<ellipse cx="66" cy="-45" rx="9" ry="6" fill="{light}"/>', 2),
             soft('<ellipse cx="-22" cy="48" rx="32" ry="34" fill="#6F6961" opacity=".35"/>', 9),
             soft('<ellipse cx="-30" cy="36" rx="20" ry="22" fill="#C9C3B9" opacity=".55"/>', 9),
             soft('<path d="M36,16 C38,40 38,64 38,86" stroke="#55504A" stroke-width="4" fill="none" opacity=".45"/>', 2.5)]
    st = []
    for i in range(7):
        t = i / 6
        x0, y0 = -2 - t * 46, -34 + t * 52
        st.append(f'<path d="M{x0:.1f},{y0:.1f} q{10 + t * 4:.1f},{10:.1f} {6 + t * 10:.1f},{26 - t * 4:.1f} t{4:.1f},{16:.1f}" stroke-width="{rng.uniform(4, 6):.1f}"/>')
    st += ['<path d="M36,-84 C38,-78 40,-74 40,-68" stroke-width="2.4"/>', '<path d="M43,-86 C44,-80 45,-76 46,-70" stroke-width="2.2"/>',
           '<path d="M29,-80 C31,-74 32,-70 32,-64" stroke-width="2.2"/>', '<path d="M50,-60 C42,-58 34,-56 26,-56" stroke-width="2"/>',
           '<path d="M48,-54 C42,-50 36,-48 28,-48" stroke-width="2"/>', '<path d="M14,-58 C8,-48 0,-40 -8,-34" stroke-width="4"/>',
           '<path d="M24,-62 C18,-50 12,-42 4,-36" stroke-width="3"/>']
    inner.append(soft(f'<g stroke="{stripe}" fill="none" stroke-linecap="round" opacity=".55">{"".join(st)}</g>', 1.2))

    def flow(x, y):
        if x > 40 and y > -30:
            return math.radians(95)
        return math.radians(120 + (x + 60) * .2) if y > -40 else math.radians(160)
    inner.append(strokes(rng, 360, (-60, -100, 76, 90), flow, ["#D6D0C6", "#5C564F", "#FFFFFF", "#7A736A"], (3, 6), .7, .3))
    o.append(f'<g clip-path="{clip(CAT)}">{"".join(inner)}</g>')
    tl = [(-50, 70, 7), (-48, 84, 7.5), (-26, 89, 7.5), (6, 90, 7), (30, 87, 6.5), (42, 82, 6)]
    rings = "".join(f'<path d="M{x + math.cos(math.radians(a + 90)) * w * 1.2:.1f},{y + math.sin(math.radians(a + 90)) * w * 1.2:.1f} '
                    f'L{x - math.cos(math.radians(a + 90)) * w * 1.2:.1f},{y - math.sin(math.radians(a + 90)) * w * 1.2:.1f}" stroke-width="3.6"/>'
                    for x, y, a, w in (at(tl, t) for t in (.25, .42, .58, .74, .9)))
    o.append(f'<path d="{tube(tl)}" fill="{lg([(0, "#ABA49A"), (1, "#7A736A")])}"/>'
             f'<g clip-path="{clip(tube(tl))}"><g stroke="{stripe}" opacity=".6" filter="{blur(.8)}">{rings}</g>'
             f'<circle cx="42" cy="82" r="7" fill="#3E3934" opacity=".8" filter="{blur(1.5)}"/></g>')
    body = f'<g filter="{vol(5, .34, dark="#1E1A16")}">{"".join(o[1:])}</g>'
    face = ('<path d="M57,-84 C55,-92 53,-99 52,-104 C49,-98 47,-92 46,-86Z" fill="#D9A69C" opacity=".75"/>'
            '<g stroke="#FFFFFF" stroke-width="1" fill="none" opacity=".75" stroke-linecap="round">'
            '<path d="M54,-90 l-3,-3"/><path d="M52,-87 l-4,-2"/><path d="M53,-94 l-3,-4"/></g>'
            '<ellipse cx="57" cy="-64" rx="5.2" ry="4" transform="rotate(-8 57 -64)" fill="#2E2A24"/>'
            f'<ellipse cx="57.6" cy="-64" rx="4.2" ry="3.2" transform="rotate(-8 57 -64)" fill="{rg([(0, "#D9D46A"), (1, "#8E9A3A")])}"/>'
            '<ellipse cx="58.6" cy="-64" rx=".9" ry="3" fill="#15120F"/>'
            '<circle cx="56.6" cy="-65.4" r=".9" fill="#FFFFFF" opacity=".9"/>'
            '<path d="M51.6,-63.8 C54,-68 60,-68.6 62.4,-65.4" stroke="#2E2A24" stroke-width="1.1" fill="none"/>'
            '<path d="M74,-53 L70.6,-52.6 L72.2,-49.4Z" fill="#C98580"/>'
            '<path d="M72.4,-49.4 C72.6,-46.6 71.6,-44.6 69.6,-43.6 M72.4,-46.4 C70.4,-45 68.2,-45.2 66.6,-46.6" stroke="#4A3E38" stroke-width=".9" fill="none" opacity=".7"/>'
            '<g stroke="#FFFFFF" stroke-width=".7" fill="none" opacity=".85" stroke-linecap="round">'
            '<path d="M68,-47 Q84,-52 100,-50"/><path d="M68,-46 Q86,-47 100,-42"/><path d="M67,-45 Q82,-42 96,-34"/>'
            '<path d="M66,-46 Q54,-46 44,-44"/><path d="M62,-70 Q70,-80 76,-84"/></g>'
            '<g fill="#5A524A" opacity=".5"><circle cx="69" cy="-47.5" r=".6"/><circle cx="67" cy="-46.5" r=".6"/><circle cx="68.5" cy="-45" r=".6"/></g>')
    return f'<g filter="{grain(.06)}">{o[0]}{body}{face}</g>'


BOX["cat"] = (-64, -112, 102, 98)


# ---------------------------------------------------------------- cow (Holstein, standing, side view)
COW = ("M121,4 C122,-6 118,-20 110,-32 C106,-40 100,-46 94,-48 C86,-48 78,-44 68,-44 C50,-46 20,-48 -10,-47 "
       "C-40,-47 -70,-48 -88,-50 C-96,-51 -102,-48 -104,-42 C-108,-30 -108,-14 -106,0 C-104,14 -100,26 -96,36 "
       "C-95,44 -96,52 -96,60 L-95,82 L-96,88 L-82,88 L-83,82 C-84,70 -84,58 -82,48 C-80,36 -76,28 -70,24 "
       "C-40,32 0,32 32,28 L34,82 L33,88 L48,88 L48,82 L50,40 C54,26 60,14 66,8 C74,4 84,6 94,12 "
       "C102,16 110,20 116,18 C121,16 123,12 121,4Z")


def cow():
    rng = random.Random(31)
    o = [ground(0, 90, 116, 7, .22)]
    back = []
    for leg in ([(24, 18, 9), (25, 56, 7), (26, 84, 6.6)], [(-74, 22, 10), (-82, 52, 7), (-84, 84, 6.6)]):
        back.append(f'<path d="{tube(leg)}" fill="{lg([(0, "#BDB8B0"), (1, "#A29C94")])}"/>')
        x = leg[-1][0]
        back.append(f'<rect x="{x - 7}" y="80" width="14" height="9" rx="3" fill="#3A3634"/>')
    o.append(f'<g filter="{vol(4, .4, dark="#1E1A16")}">{"".join(back)}</g>')
    blk = lg([(0, "#3A3A3C"), (1, "#141416")])
    patches = [blob([(64, -50), (96, -54), (120, -24), (126, 8), (110, 26), (84, 14), (64, 8), (56, -20)]),
               blob([(16, -52), (58, -50), (62, -22), (48, -2), (28, -8), (12, -26)]),
               blob([(-44, -52), (-2, -52), (6, -26), (-6, 2), (-30, 8), (-48, -14)]),
               blob([(-112, -48), (-76, -54), (-64, -32), (-78, -10), (-98, -12), (-112, -26)]),
               blob([(-22, 16), (2, 18), (6, 34), (-26, 34)])]
    inner = [f'<path d="{COW}" fill="{lg([(0, "#FBFAF7"), (.6, "#EEEBE5"), (1, "#C9C4BC")], 0, -50, 0, 90, user=True)}"/>',
             "".join(f'<path d="{p}" fill="{blk}"/>' for p in patches),
             f'<path d="{blob([(100, -44), (108, -40), (116, -14), (119, 0), (112, 2), (106, -16), (98, -36)])}" fill="#F4F2EE"/>',
             soft('<ellipse cx="116" cy="8" rx="10" ry="12" fill="#C99C96"/>', 1.5),
             soft('<ellipse cx="-14" cy="-36" rx="70" ry="8" fill="#FFFFFF" opacity=".25"/>', 6),
             soft('<path d="M-70,30 C-40,36 0,36 32,30" stroke="#8C867E" stroke-width="10" fill="none" opacity=".35"/>', 5),
             soft('<path d="M-60,-40 C-56,-10 -64,14 -74,26" stroke="#7C766E" stroke-width="5" fill="none" opacity=".3"/>', 4),
             soft('<path d="M40,-30 C46,-6 46,14 42,30" stroke="#7C766E" stroke-width="4" fill="none" opacity=".25"/>', 3),
             strokes(rng, 260, (-108, -50, 124, 88), lambda x, y: math.radians(100 if y > 30 else 160), ["#FFFFFF", "#7A746C", "#5A5650"], (3, 5), .6, .2)]
    o.append(f'<g clip-path="{clip(COW)}">{"".join(inner)}</g>')
    o.append(f'<path d="M-62,26 C-64,38 -58,44 -50,44 C-42,44 -38,38 -40,26Z" fill="{lg([(0, "#E9B7AE"), (1, "#C98F86")])}"/>'
             '<path d="M-56,43 L-57,50 M-46,43 L-45,50" stroke="#D49C94" stroke-width="3" stroke-linecap="round"/>')
    o.append('<path d="M-96,82 L-82,82 L-81,89 L-97,89Z" fill="#3A3634"/><path d="M34,82 L48,82 L49,89 L33,89Z" fill="#3A3634"/>')
    body = f'<g filter="{vol(6, .32, dark="#1E1A16")}">{"".join(o[1:])}</g>'
    tail = (f'<path d="{tube([(-104, -42, 2.6), (-109, -26, 2.2), (-111, 10, 2), (-109, 44, 2)])}" fill="#D9D5CE"/>'
            f'<path d="{blob([(-109, 40), (-104, 50), (-106, 62), (-110, 64), (-114, 52)])}" fill="#2A2A2C"/>')
    head = (f'<ellipse cx="80" cy="-40" rx="13" ry="5.5" transform="rotate(18 80 -40)" fill="{blk}"/>'
            '<ellipse cx="79" cy="-39" rx="8" ry="2.6" transform="rotate(18 79 -39)" fill="#B88A84"/>'
            f'<path d="{tube([(92, -48, 3.2), (94, -55, 2.4), (99, -61, 1.4)])}" fill="{lg([(0, "#EDE3C8"), (1, "#A89C7E")])}"/>'
            '<ellipse cx="101" cy="-26" rx="3.6" ry="2.8" transform="rotate(-30 101 -26)" fill="#0E0D0C"/>'
            '<ellipse cx="101.5" cy="-26" rx="2.4" ry="1.8" transform="rotate(-30 101 -26)" fill="#3A2A20"/>'
            '<circle cx="102.4" cy="-27" r=".8" fill="#FFFFFF" opacity=".85"/>'
            '<ellipse cx="119" cy="4" rx="2" ry="3.2" transform="rotate(-20 119 4)" fill="#4A2E2A" opacity=".8"/>'
            '<path d="M118,14 C114,16 110,16 106,14" stroke="#5A3A36" stroke-width="1" fill="none" opacity=".6"/>')
    return f'<g filter="{grain(.05)}">{o[0]}{tail}{body}{head}</g>'


BOX["cow"] = (-118, -66, 128, 98)


# ---------------------------------------------------------------- duck (mallard drake, standing, side view)
DUCK = ("M74,-54 C72,-70 56,-80 44,-74 C36,-70 32,-60 34,-48 C36,-36 34,-24 30,-14 "
        "C10,-14 -30,-12 -58,-10 L-78,-14 C-86,-16 -90,-10 -84,-4 L-70,6 C-60,30 -30,44 0,44 "
        "C34,44 52,26 52,8 C52,-6 48,-20 48,-30 C50,-36 58,-40 66,-40 Z")


def duck():
    rng = random.Random(41)
    o = [ground(0, 74, 72, 5, .2)]
    for x, c in ((-8, "#C9701E"), (6, "#E8892E")):
        o.append(f'<path d="M{x},38 L{x + 1},62" stroke="{c}" stroke-width="5.5" stroke-linecap="round"/>'
                 f'<path d="M{x - 2},61 L{x + 18},67 L{x + 16},72 L{x - 3},71 Z" fill="{c}" stroke="{c}" stroke-width="2" stroke-linejoin="round"/>')
    inner = [f'<path d="{DUCK}" fill="{lg([(0, "#D7D8D5"), (1, "#A9AAA6")])}"/>',
             f'<path d="{blob([(30, -40), (33, -56), (38, -72), (50, -82), (66, -80), (78, -60), (76, -42), (58, -36), (48, -30), (32, -34)])}" '
             f'fill="{lg([(0, "#2A6E86"), (.35, "#1F7A4C"), (.7, "#16603A"), (1, "#0F4A2C")], 0, 0, 1, 1)}"/>',
             soft('<ellipse cx="50" cy="-68" rx="10" ry="6" fill="#6FD0A0" opacity=".45"/>', 3),
             f'<path d="{blob([(30, -28), (50, -28), (56, 8), (46, 32), (26, 40), (14, 14), (20, -10)])}" fill="{lg([(0, "#8A4A30"), (1, "#5E2E1E")])}"/>',
             '<path d="M30,-33 C38,-30 44,-28 50,-28" stroke="#FFFFFF" stroke-width="3.6" fill="none"/>',
             f'<path d="{blob([(-60, -12), (-74, -12), (-82, -6), (-70, 8), (-58, 6)])}" fill="#1A1A1C"/>',
             soft('<path d="M-70,30 C-40,46 0,48 40,36" stroke="#6E6F6A" stroke-width="10" fill="none" opacity=".35"/>', 5)]
    inner.append('<g stroke="#8A8C88" stroke-width=".6" fill="none" opacity=".35">' + "".join(
        f'<path d="M{x},{y} q3,-1.5 6,0 t6,0"/>' for x, y in ((rng.uniform(-60, 10), rng.uniform(-6, 40)) for _ in range(70))) + '</g>')
    o.append(f'<g clip-path="{clip(DUCK)}">{"".join(inner)}</g>')
    wing = blob([(28, -14), (0, -17), (-40, -15), (-66, -10), (-56, 4), (-30, 12), (0, 12), (22, 4)])
    o.append(f'<path d="{wing}" fill="{lg([(0, "#B2AA9C"), (1, "#8C8476")])}"/>')
    o.append(f'<g clip-path="{clip(wing)}">'
             + "".join(f'<path d="M{x},{-14 + k * 7} q-8,6 -16,5" stroke="#6E675C" stroke-width=".9" fill="none" opacity=".55"/>'
                       for k in range(4) for x in range(26 - k * 4, -60, -15))
             + f'<path d="{blob([(-46, -1), (-28, 2), (-27, 8), (-45, 6)])}" fill="{lg([(0, "#4E62B0"), (1, "#30407E")])}" opacity=".9"/>'
             + '<path d="M-48,-2 L-26,1 M-46,7.5 L-25,9" stroke="#FFFFFF" stroke-width="1" opacity=".7"/></g>')
    o.append('<path d="M-66,-12 C-72,-24 -62,-28 -60,-21" stroke="#1A1A1C" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="{blob([(-80, -8), (-87, -11), (-90, -6), (-86, -1), (-80, -1)])}" fill="#D9D9D4"/>')
    body = f'<g filter="{vol(5, .3, dark="#1E1A16")}">{"".join(o[1:])}</g>'
    bill = "M72,-55 C82,-53 92,-50 99,-46 C101,-44 100,-42 97,-41 C88,-40 78,-40 66,-41 C64,-46 66,-52 72,-55Z"
    head = (f'<path d="{bill}" fill="{lg([(0, "#E3CF5A"), (1, "#B7A030")])}"/>'
            '<path d="M95,-45.5 C98,-45 100,-43.5 99,-42 C97,-41 95,-41.5 94.5,-43Z" fill="#2A2A22"/>'
            '<path d="M70,-46 C80,-45 90,-44 97,-43" stroke="#8A7A22" stroke-width=".8" fill="none" opacity=".7"/>'
            '<ellipse cx="79" cy="-50" rx="2.2" ry="1" fill="#5A5020"/>'
            '<circle cx="56" cy="-62" r="2.8" fill="#1A120C"/><circle cx="56.8" cy="-62.8" r=".8" fill="#FFFFFF" opacity=".9"/>')
    return f'<g filter="{grain(.05)}">{o[0]}{body}{head}</g>'


BOX["duck"] = (-96, -86, 104, 80)


# ---------------------------------------------------------------- hand (back of a left hand)
SKIN, SKIN_L, SKIN_D = "#EBBB97", "#F5D3B6", "#C98C68"
FINGERS = [[(-33, 12, 8.6), (-42, -20, 7.8), (-48, -48, 6.8)],
           [(-15, 4, 9.6), (-19, -36, 8.8), (-22, -74, 7.6)],
           [(4, 2, 10), (4, -42, 9.4), (4, -86, 8.2)],
           [(22, 6, 9.6), (27, -34, 9), (31, -72, 7.8)]]
THUMB = [(32, 48, 12), (48, 26, 11), (61, 6, 9.6), (68, -12, 8.6)]


def hand():
    palm = blob([(-40, 8), (-24, 0), (0, -2), (22, 0), (36, 10), (44, 34), (40, 62), (32, 90), (30, 116), (-30, 116), (-34, 90), (-42, 54), (-44, 26)])
    shapes = [palm] + [tube(f) for f in FINGERS] + [tube(THUMB)]
    fill = rg([(0, SKIN_L), (.55, SKIN), (1, "#DCA27E")], 0, -10, 120, -20, -60, user=True)
    o = [f'<path d="{s}" fill="{fill}"/>' for s in shapes]
    # finger joints, nails, knuckles
    det = []
    for f in FINGERS + [THUMB]:
        for t, k in ((.5, 3), (.14, 2)) if f is not THUMB else ((.55, 2),):
            x, y, a, w = at(f, t)
            ra = math.radians(a + 90)
            for j in range(k):
                off = (j - (k - 1) / 2) * 2.2
                cx, cy = x + math.cos(math.radians(a)) * off, y + math.sin(math.radians(a)) * off
                det.append(f'<path d="M{cx + math.cos(ra) * w * .55:.1f},{cy + math.sin(ra) * w * .55:.1f} '
                           f'Q{cx + math.cos(math.radians(a)) * 1.6:.1f},{cy + math.sin(math.radians(a)) * 1.6:.1f} '
                           f'{cx - math.cos(ra) * w * .55:.1f},{cy - math.sin(ra) * w * .55:.1f}" stroke="#B87A58" stroke-width=".8" fill="none" opacity=".45"/>')
        x, y, a, w = at(f, .86)
        nw, nl = w * .62, w * 1.25
        det.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({a + 90:.1f})">'
                   f'<rect x="{-nw:.1f}" y="{-nl * .55:.1f}" width="{2 * nw:.1f}" height="{nl * 1.2:.1f}" rx="{nw:.1f}" fill="{lg([(0, "#F7DCCF"), (1, "#E7B4A2")])}" stroke="#C98C78" stroke-width=".5"/>'
                   f'<rect x="{-nw * .9:.1f}" y="{-nl * .6:.1f}" width="{2 * nw * .9:.1f}" height="{nl * .28:.1f}" rx="{nw * .5:.1f}" fill="#FFF4EC" opacity=".9"/>'
                   f'<ellipse cx="{-nw * .3:.1f}" cy="{nl * .05:.1f}" rx="{nw * .25:.1f}" ry="{nl * .35:.1f}" fill="#FFFFFF" opacity=".5"/></g>')
    for f in FINGERS:
        x, y = f[0][0], f[0][1]
        det.append(soft(f'<ellipse cx="{x}" cy="{y - 2}" rx="7" ry="5" fill="{SKIN_L}" opacity=".9"/>', 2.5))
        det.append(soft(f'<path d="M{x},{y + 6} L{x * .6:.1f},{y + 56}" stroke="#F8DCC4" stroke-width="3" fill="none" opacity=".45"/>', 2))
    det.append(soft('<path d="M-44,40 C-38,70 -34,100 -32,116" stroke="#B57A58" stroke-width="5" fill="none" opacity=".3"/>', 4))
    hand_g = f'<g filter="{vol(5, .5, dark="#7A3E22")}">{"".join(o)}{"".join(det)}</g>'
    D.add("handfade", '<linearGradient id="handfadeg" x1="0" y1="0" x2="0" y2="1"><stop offset=".78" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                      '<mask id="handfade" maskUnits="userSpaceOnUse" x="-80" y="-110" width="170" height="240"><rect x="-80" y="-110" width="170" height="232" fill="url(#handfadeg)"/></mask>')
    return f'<g filter="{grain(.05)}"><g mask="url(#handfade)">{hand_g}</g></g>'


BOX["hand"] = (-62, -98, 82, 120)


# ---------------------------------------------------------------- T-shirt (laid flat)
def tshirt(color="#EFBF45"):
    rng = random.Random(51)
    sh = ("M-24,-86 C-14,-75 14,-75 24,-86 C38,-84 50,-82 58,-79 C74,-71 90,-62 100,-52 C94,-38 88,-26 82,-14 "
          "C74,-18 66,-22 59,-26 C60,10 61,50 61,86 C21,92 -21,92 -61,86 C-61,50 -60,10 -59,-26 "
          "C-66,-22 -74,-18 -82,-14 C-88,-26 -94,-38 -100,-52 C-90,-62 -74,-71 -58,-79 C-50,-82 -38,-84 -24,-86Z")
    d1, d2, l1 = dk(color, .22), dk(color, .38), lt(color, .35)
    o = [ground(0, 94, 76, 6, .18)]
    inner = [f'<path d="{sh}" fill="{lg([(0, lt(color, .15)), (1, dk(color, .08))])}"/>',
             soft(f'<path d="M-56,-24 C-30,0 -20,30 -24,70" stroke="{d1}" stroke-width="7" fill="none" opacity=".45"/>', 6),
             soft(f'<path d="M56,-24 C34,4 26,40 30,80" stroke="{d1}" stroke-width="6" fill="none" opacity=".4"/>', 6),
             soft(f'<path d="M-40,-20 C-20,6 -10,36 -12,72" stroke="{l1}" stroke-width="8" fill="none" opacity=".6"/>', 6),
             soft(f'<path d="M44,-18 C30,8 22,36 22,62" stroke="{l1}" stroke-width="6" fill="none" opacity=".5"/>', 6),
             soft(f'<path d="M-96,-48 C-84,-40 -78,-30 -80,-18 M96,-48 C84,-40 78,-30 80,-18" stroke="{d1}" stroke-width="6" fill="none" opacity=".35"/>', 4),
             soft(f'<path d="M-60,-30 C-48,-28 -40,-34 -36,-40 M60,-30 C48,-28 40,-34 36,-40" stroke="{d1}" stroke-width="4" fill="none" opacity=".4"/>', 3),
             f'<path d="M-58,-79 C-56,-60 -58,-40 -59,-26 M58,-79 C56,-60 58,-40 59,-26" stroke="{d1}" stroke-width="1.2" fill="none" opacity=".6"/>',
             f'<path d="M-90,-30 L-81,-24 M90,-30 L81,-24" stroke="{d1}" stroke-width="1" fill="none" opacity=".0"/>',
             f'<g stroke="{d2}" stroke-width=".9" fill="none" stroke-dasharray="2.4 2" opacity=".55">'
             '<path d="M-97,-46 C-91,-34 -86,-24 -80,-14" transform="translate(5 -2)"/><path d="M97,-46 C91,-34 86,-24 80,-14" transform="translate(-5 -2)"/>'
             '<path d="M-60,80 C-20,86 20,86 60,80"/><path d="M-60,77 C-20,83 20,83 60,77" opacity=".6"/></g>',
             strokes(rng, 500, (-100, -88, 100, 92), lambda x, y: math.radians(90), [l1, d1], (2, 4), .6, .25, 0)]
    o.append(f'<g filter="{vol(5, .3, dark="#5A3A0A")}"><g clip-path="{clip(sh)}">{"".join(inner)}</g></g>')
    # collar: the inside of the back, then the rib band
    o.append(f'<path d="M-24,-86 C-12,-92 12,-92 24,-86 C14,-79 -14,-79 -24,-86Z" fill="{d2}"/>')
    o.append(f'<path d="M-25,-86 C-14,-74 14,-74 25,-86" stroke="{d1}" stroke-width="7" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="M-25,-86 C-14,-74 14,-74 25,-86" stroke="{l1}" stroke-width="5" fill="none" stroke-linecap="round" stroke-dasharray="1 1.4" opacity=".7"/>')
    o.append(f'<path d="M-27,-86 C-14,-93 14,-93 27,-86" stroke="{d1}" stroke-width="2.2" fill="none" stroke-linecap="round"/>')
    return f'<g filter="{grain(.08, 1.1)}">{"".join(o)}</g>'


BOX["tshirt"] = (-104, -96, 104, 100)


# ---------------------------------------------------------------- photo frame with a heart (the family deck)
def frame():
    o = [ground(0, 84, 66, 6, .2)]
    wood = lg([(0, "#D9A86C"), (.5, "#B98148"), (1, "#8E5C2E")], 0, 0, 1, 1)
    o.append(f'<rect x="-62" y="-78" width="124" height="156" rx="8" fill="{wood}"/>')
    grain_l = "".join(f'<path d="M-62,{y} C-20,{y + 3} 20,{y - 3} 62,{y + 1}" />' for y in range(-74, 78, 7))
    o.append(f'<g clip-path="{clip("M-62,-78 h124 v156 h-124Z")}"><g stroke="#7A4A20" stroke-width=".8" fill="none" opacity=".25">{grain_l}</g></g>')
    o.append('<rect x="-48" y="-64" width="96" height="128" rx="3" fill="#6E4520" opacity=".5"/>')
    o.append('<rect x="-46" y="-62" width="92" height="124" rx="2" fill="#FBF6EE"/>')
    o.append(f'<path d="{heart_path(1.25, 0, -2)}" fill="{rg([(0, "#F4A9B4"), (.7, "#E47F92"), (1, "#C9606F")], cx=.4, cy=.35)}"/>')
    o.append(soft('<ellipse cx="-14" cy="-22" rx="7" ry="5" transform="rotate(-30 -14 -22)" fill="#FFFFFF" opacity=".6"/>', 2))
    o.append(soft('<path d="M-46,-20 L-10,-62 L8,-62 L-46,0Z" fill="#FFFFFF" opacity=".22"/>', 2))
    return f'<g filter="{vol(4, .3)}">{"".join(o)}</g>'


BOX["frame"] = (-70, -84, 70, 92)




# ================================================================ style B: simple bold flat shapes (style sheet only)
APPLE = ("M0,-58 C14,-72 44,-80 68,-66 C92,-52 98,-18 92,12 C86,44 70,72 48,82 C34,88 20,86 10,82 "
         "C4,80 -4,80 -10,82 C-20,86 -34,88 -48,82 C-70,72 -86,44 -92,12 C-98,-18 -92,-52 -68,-66 C-44,-80 -14,-72 0,-58Z")


def flat_apple():
    return ('<path d="M2,-56 C2,-74 6,-88 12,-98" stroke="#5B3A1E" stroke-width="9" stroke-linecap="round" fill="none"/>'
            '<path d="M10,-84 C22,-106 52,-110 68,-98 C52,-80 28,-74 10,-84Z" fill="#1F9D55"/>'
            f'<path d="{APPLE}" fill="#E5262D"/>'
            '<ellipse cx="-50" cy="-24" rx="10" ry="21" transform="rotate(20 -50 -24)" fill="#FFFFFF"/>')


def flat_dog():
    c, cr = "#E8892E", "#FFF1DA"
    return (f'<path d="M-58,-14 C-92,-34 -84,-78 -54,-62" stroke="{c}" stroke-width="15" stroke-linecap="round" fill="none"/>'
            + "".join(f'<rect x="{x}" y="0" width="19" height="82" rx="9.5" fill="{c}"/>' for x in (-60, -36, 30, 52))
            + f'<rect x="-70" y="-34" width="146" height="62" rx="31" fill="{c}"/>'
            f'<path d="M56,-64 L62,-108 L90,-80Z" fill="#B85F18"/>'
            f'<circle cx="80" cy="-52" r="34" fill="{c}"/>'
            f'<rect x="88" y="-56" width="46" height="30" rx="15" fill="{cr}"/>'
            '<circle cx="86" cy="-62" r="5.5" fill="#1B1B1B"/><circle cx="131" cy="-44" r="8" fill="#1B1B1B"/>')


def flat_car():
    return ('<path d="M-116,24 L-116,-4 Q-116,-24 -96,-26 L-72,-28 L-48,-62 Q-44,-67 -36,-67 L34,-67 Q42,-67 48,-61 L80,-28 '
            'L102,-25 Q118,-22 118,-4 L118,24Z" fill="#E5262D"/>'
            '<path d="M-38,-56 L-6,-56 L-6,-30 L-60,-30Z M4,-56 L32,-56 L62,-30 L4,-30Z" fill="#BFE6F5"/>'
            '<circle cx="-66" cy="26" r="27" fill="#1B1B1B"/><circle cx="66" cy="26" r="27" fill="#1B1B1B"/>'
            '<circle cx="-66" cy="26" r="11" fill="#E6E6E6"/><circle cx="66" cy="26" r="11" fill="#E6E6E6"/>'
            '<rect x="104" y="-16" width="14" height="10" rx="5" fill="#FFD84A"/>')


def flat_cup():
    return ('<path d="M44,-30 C92,-34 92,34 44,30" stroke="#1D63D1" stroke-width="17" fill="none"/>'
            '<rect x="-54" y="-62" width="104" height="122" rx="16" fill="#1D63D1"/>'
            '<rect x="-54" y="-18" width="104" height="16" fill="#FFFFFF"/>')


THINGS_B = {"apple": (flat_apple, (-100, -112, 100, 92)), "dog": (flat_dog, (-100, -112, 140, 86)),
            "car": (flat_car, (-120, -70, 120, 56)), "cup": (flat_cup, (-56, -66, 94, 64))}


# ================================================================ page plumbing
def tx(x, y, s, size=16, color=INK, anchor="middle", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
            f'font-family="Huninn, \'WenQuanYi Zen Hei\', sans-serif" {extra}>{s}</text>')


def _fit(svg, box, cx, cy, w, h, maxs=99.0, flip=False):
    x0, y0, x1, y1 = box
    s = min(w / (x1 - x0), h / (y1 - y0), maxs)
    fx = -1 if flip else 1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    return f'<g transform="translate({cx - fx * mx * s:.2f} {cy - my * s:.2f}) scale({fx * s:.4f} {s:.4f})">{svg}</g>'


def place(name, cx, cy, w, h, maxs=99.0, flip=False, **kw):
    """Draw thing `name` (style A) scaled to fit a w x h box centred on (cx, cy)."""
    return _fit(THINGS[name](**kw), BOX[name], cx, cy, w, h, maxs, flip)


def place_b(name, cx, cy, w, h):
    f, box = THINGS_B[name]
    return _fit(f(), box, cx, cy, w, h)


def page(body, bg, w=W, h=H):
    css = (f"@font-face {{ font-family: Huninn; src: url('file://{FONT}'); }}"
           f"* {{ margin: 0; padding: 0; }} body {{ width: {w}px; height: {h}px; overflow: hidden; background: {bg}; }}")
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{D.svg()}{body}</svg>'
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{svg}</body></html>'


def render(html, out, w, h, scale):
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp) / "page.html"
        p.write_text(html)
        subprocess.run(["node", str(HERE / "render.js"), str(p), str(out), str(w), str(h), str(scale)], check=True)


THINGS = {"apple": apple, "banana": banana, "car": car, "cup": cup, "dog": dog, "cat": cat, "cow": cow,
          "duck": duck, "hand": hand, "tshirt": tshirt, "frame": frame}


# ---------------------------------------------------------------- small UI pieces (no outlines, soft shadows)
def card(x, y, w, h, rx=28, fill=CARD, border=EDGE, shadow=True, sw=1.5, extra=""):
    sh = f' filter="{card_shadow()}"' if shadow else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{border}" stroke-width="{sw}"{sh} {extra}/>'


def ic(inner, cx, cy, s=1.0):
    return f'<g transform="translate({cx} {cy}) scale({s})">{inner}</g>'


def i_speaker(c):
    return (f'<g transform="translate(-2 0)"><path d="M-12,-5 L-6,-5 L2,-12 L2,12 L-6,5 L-12,5Z" fill="{c}" stroke="{c}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="M7.5,-6 A9,9 0 0 1 7.5,6 M11.5,-11 A15,15 0 0 1 11.5,11" stroke="{c}" stroke-width="2.8" fill="none" stroke-linecap="round"/></g>')


def i_arrow(c, left=False, w=4):
    rot = ' transform="rotate(180)"' if left else ""
    return f'<path d="M-10,0 L9,0 M1,-9 L10,0 L1,9" stroke="{c}" stroke-width="{w}" fill="none" stroke-linecap="round" stroke-linejoin="round"{rot}/>'


def i_lock(c):
    return (f'<path d="M-5.5,-2 V-6 A5.5,5.5 0 0 1 5.5,-6 V-2" stroke="{c}" stroke-width="2.6" fill="none"/>'
            f'<rect x="-8.5" y="-2.5" width="17" height="13" rx="3" fill="{c}"/>')


def i_camera(c, hole):
    return (f'<path d="M-5,-8 L-3,-12 L3,-12 L5,-8Z" fill="{c}"/><rect x="-13" y="-8" width="26" height="19" rx="4.5" fill="{c}"/>'
            f'<circle cx="0" cy="1.5" r="6.5" fill="{hole}"/><circle cx="0" cy="1.5" r="3.8" fill="{c}"/>')


def i_mic(c):
    return (f'<rect x="-5" y="-14" width="10" height="17" rx="5" fill="{c}"/>'
            f'<path d="M-9,-2 A9,9 0 0 0 9,-2 M0,7 V12 M-5,12 H5" stroke="{c}" stroke-width="2.4" fill="none" stroke-linecap="round"/>')


def i_home(c, door="#FFFFFF"):
    return (f'<path d="M-11,-1 L0,-11 L11,-1 L11,11 L-11,11Z" fill="{c}" stroke="{c}" stroke-width="2.4" stroke-linejoin="round"/>'
            f'<rect x="-3.5" y="3" width="7" height="8.5" rx="1.5" fill="{door}"/>')


def i_play(c):
    return f'<path d="M-5,-8 L9,0 L-5,8Z" fill="{c}" stroke="{c}" stroke-width="2" stroke-linejoin="round"/>'


def i_back(c):
    return f'<path d="M5,-10 L-5,0 L5,10" stroke="{c}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'


def i_shield(c):
    return (f'<path d="M0,-11 L9,-7 C9,2 6,8 0,11 C-6,8 -9,2 -9,-7Z" fill="{c}"/>'
            '<path d="M-4,0 L-1,3 L5,-4" stroke="#FFFFFF" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')


def dots(cx, y, n, k, on=TEAL, off="#D8D2C7", r=5, gap=18):
    x0 = cx - (n - 1) * gap / 2
    return "".join(f'<circle cx="{x0 + i * gap}" cy="{y}" r="{r + (1.5 if i == k else 0)}" fill="{on if i <= k else off}"/>' for i in range(n))


def kid_bg():
    return f'<rect width="{W}" height="{H}" fill="{lg([(0, "#F7F4EF"), (1, "#ECE7DF")])}"/>'


def sparkle(cx, cy, r, c, op=1.0):
    return (f'<path d="M{cx},{cy - r} Q{cx},{cy} {cx + r},{cy} Q{cx},{cy} {cx},{cy + r} Q{cx},{cy} {cx - r},{cy} Q{cx},{cy} {cx},{cy - r}Z" '
            f'fill="{c}" opacity="{op}"/>')


def gold_star(cx, cy, R, rot=-90):
    return (f'<path d="{star_path(R, R * .48, 5, cx, cy, rot)}" fill="{rg([(0, "#FFE58A"), (1, "#F0B232")], cx=.45, cy=.4)}" '
            f'stroke="#F6C94E" stroke-width="{R * .18:.1f}" stroke-linejoin="round"/>')


def ripple(cx, cy, c=TEAL):
    return (f'<circle cx="{cx}" cy="{cy}" r="38" fill="none" stroke="{c}" stroke-width="2.5" opacity=".22"/>'
            f'<circle cx="{cx}" cy="{cy}" r="26" fill="none" stroke="{c}" stroke-width="3" opacity=".38"/>'
            f'<circle cx="{cx}" cy="{cy}" r="14" fill="{c}" opacity=".35"/>')


def bubble_path(x, y, w, h, r, tx_, tail=18):
    return (f"M{x + r},{y} H{x + w - r} A{r},{r} 0 0 1 {x + w},{y + r} V{y + h - r} A{r},{r} 0 0 1 {x + w - r},{y + h} "
            f"H{tx_ + 14} L{tx_ - 2},{y + h + tail} L{tx_ - 4},{y + h} H{x + r} A{r},{r} 0 0 1 {x},{y + h - r} V{y + r} A{r},{r} 0 0 1 {x + r},{y}Z")


# ---------------------------------------------------------------- 0 style sheet
def style_sheet():
    SW, SH = 1600, 900
    o = [f'<rect width="{SW}" height="{SH}" fill="#F3F0EA"/>',
         tx(SW / 2, 58, "畫風選擇", 40, INK),
         tx(SW / 2, 96, "同樣四張卡：蘋果、小狗、紅色汽車、杯子。兩種都不幫東西加臉，也和畫畫小鎮、字母寵物、動物小餐廳的畫風不一樣。", 20, SOFT)]
    words = [("apple", "蘋果"), ("dog", "小狗"), ("car", "汽車"), ("cup", "杯子")]
    bcol = {"apple": ("#FFD23F", INK), "dog": ("#2FA7A0", "#FFFFFF"), "car": ("#22335E", "#FFFFFF"), "cup": ("#FF9F1C", "#FFFFFF")}
    pw, top, ph = 750, 124, 700
    for k, (letter, name, desc, bg, accent) in enumerate([
            ("A", "寫實圖鑑風", "照真的樣子畫：形狀、顏色、比例都對，柔和的光影和一點紋理，白色圓角卡片。", "#E7EFEE", TEAL),
            ("B", "簡單大色塊風", "幾個簡單的平面色塊、對比很強，像寶寶閃卡；一樣不加臉。", "#F4EADB", CORAL)]):
        x0 = 40 + k * (pw + 30)
        o.append(f'<rect x="{x0}" y="{top}" width="{pw}" height="{ph}" rx="30" fill="{bg}"/>')
        o.append(f'<circle cx="{x0 + 52}" cy="{top + 50}" r="27" fill="{accent}"/>' + tx(x0 + 52, top + 61, letter, 30, "#FFFFFF"))
        o.append(tx(x0 + 94, top + 61, name, 32, INK, "start"))
        o.append(tx(x0 + 30, top + 110, desc, 18, SOFT, "start"))
        if letter == "A":
            o.append(f'<rect x="{x0 + pw - 120}" y="{top + 28}" width="90" height="44" rx="22" fill="#E0745A"/>' + tx(x0 + pw - 75, top + 58, "推薦", 23, "#FFFFFF"))
        for i, (n, word) in enumerate(words):
            cx0, cy0 = x0 + 30 + (i % 2) * (333 + 24), top + 134 + (i // 2) * (264 + 24)
            if letter == "A":
                o.append(card(cx0, cy0, 333, 264, 26))
                o.append(place(n, cx0 + 166, cy0 + 108, 262, 184))
                o.append(tx(cx0 + 166, cy0 + 240, word, 28, INK))
            else:
                fill, ink = bcol[n]
                o.append(f'<rect x="{cx0}" y="{cy0}" width="333" height="264" rx="26" fill="{fill}"/>')
                o.append(place_b(n, cx0 + 166, cy0 + 106, 240, 168))
                o.append(tx(cx0 + 166, cy0 + 240, word, 28, ink))
    o.append(tx(SW / 2, 866, "推薦 A：越像真的東西，小朋友越容易認得出生活裡的那一個。", 26, INK))
    return page("".join(o), "#F3F0EA", SW, SH)


# ---------------------------------------------------------------- 1 card boxes
def screen_decks():
    o = [kid_bg(), tx(30, 70, "卡片盒", 24, INK, "start")]
    o.append(f'<circle cx="352" cy="62" r="22" fill="#E3DED5"/>' + ic(i_lock("#8A939B"), 352, 60, .9))
    decks = [("dog", "動物", SAND), ("banana", "水果", SAGE), ("car", "交通工具", BLUE),
             ("hand", "身體", CORAL), ("cup", "家裡的東西", TEAL), ("tshirt", "衣服", LILAC)]
    r = 62
    for i, (n, label, col) in enumerate(decks):
        cx, cy = (108, 282)[i % 2], 172 + (i // 2) * 172
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#FFFFFF" filter="{card_shadow(.14, 5, 8)}"/>')
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{r - 3.5}" fill="none" stroke="{col}" stroke-width="7"/>')
        fw, fh = {"dog": (1.6, 1.36), "hand": (1.3, 1.5), "banana": (1.55, 1.2), "car": (1.6, 1.2), "cup": (1.3, 1.3), "tshirt": (1.36, 1.36)}[n]
        o.append(place(n, cx, cy + (5 if n in ("dog", "car") else 8 if n == "hand" else 0), r * fw, r * fh))
        o.append(tx(cx, cy + r + 30, label, 20, INK))
    cx, cy = 195, 702
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 10}" fill="{ROSE}" opacity=".16"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#FFFFFF" filter="{card_shadow(.14, 5, 8)}"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r - 3.5}" fill="none" stroke="{ROSE}" stroke-width="7"/>')
    o.append(place("frame", cx, cy + 2, r * 1.2, r * 1.3))
    o.append(tx(cx, cy + r + 32, "我的家人", 20, INK))
    return page("".join(o), BG)


# ---------------------------------------------------------------- 2 flip card
def card_back(x, y, w, h, rx=10):
    D.add("cbpat", '<pattern id="cbpat" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="4.5" cy="4.5" r="1.4" fill="#FFFFFF" opacity=".5"/></pattern>')
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{lg([(0, "#8DC0B8"), (1, "#6FA59D")], 0, 0, 1, 1)}" filter="{card_shadow(.12, 3, 4)}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#cbpat)"/>'
            f'<rect x="{x + 5}" y="{y + 5}" width="{w - 10}" height="{h - 10}" rx="{rx - 4}" fill="none" stroke="#FFFFFF" stroke-width="1.5" opacity=".75"/>'
            + sparkle(x + w / 2, y + h / 2, w * .2, "#FFFFFF", .9))


def screen_flip():
    o = [kid_bg()]
    o.append(f'<rect x="22" y="28" width="346" height="122" rx="22" fill="#FFFFFF" fill-opacity=".5" stroke="#D9D2C6" stroke-width="1.5" stroke-dasharray="6 5"/>')
    o.append(card_back(97, 40, 56, 76))
    o.append(card(237, 40, 56, 76, 10, shadow=True, sw=1))
    o.append(place("dog", 265, 70, 46, 36))
    o.append(tx(265, 106, "小狗", 10, INK))
    o.append('<path d="M166,92 Q195,60 224,92" stroke="#A7AFB5" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
             '<path d="M215,88 L225,94 L226,82" stroke="#A7AFB5" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(tx(195, 112, "點一下", 12, SOFT))
    o.append(tx(125, 138, "背面", 12, SOFT) + tx(265, 138, "翻過來", 12, SOFT))
    o.append(card(26, 166, 338, 546, 30))
    o.append(place("dog", 195, 340, 292, 236))
    o.append(tx(195, 556, "小狗", 66, INK))
    o.append(f'<rect x="118" y="584" width="154" height="54" rx="27" fill="#E1EEEB"/>')
    o.append(ic(i_speaker(TEAL), 152, 611, 1.05) + tx(212, 621, "汪汪", 26, dk(TEAL, .35)))
    o.append(tx(195, 684, "dog", 22, "#A3ABB2"))
    o.append(f'<circle cx="72" cy="782" r="36" fill="#FFFFFF" stroke="{EDGE}" stroke-width="1.5" filter="{card_shadow(.12, 4, 6)}"/>' + ic(i_arrow(INK, left=True), 72, 782, 1.1))
    o.append(f'<circle cx="318" cy="782" r="36" fill="{TEAL}" filter="{card_shadow(.16, 4, 6)}"/>' + ic(i_arrow("#FFFFFF"), 318, 782, 1.1))
    o.append(dots(195, 782, 6, 2))
    return page("".join(o), BG)


# ---------------------------------------------------------------- 3 find it
def screen_find():
    o = [kid_bg()]
    o.append('<g transform="translate(0 34)">')
    o.append(f'<path d="{bubble_path(24, 44, 342, 100, 30, 112)}" fill="#FFFFFF" stroke="{EDGE}" stroke-width="1.5" filter="{card_shadow()}"/>')
    o.append(f'<circle cx="78" cy="94" r="28" fill="{TEAL}"/>' + ic(i_speaker("#FFFFFF"), 78, 94, 1.05))
    o.append(tx(120, 106, "小狗在哪裡？", 31, INK, "start"))
    x1, x2, y, w, h = 22, 204, 214, 164, 318
    # the right one: glow, gold edge, stars
    o.append(f'<rect x="{x1 - 4}" y="{y - 4}" width="{w + 8}" height="{h + 8}" rx="32" fill="#FFE08A" opacity=".75" filter="{blur(9)}"/>')
    o.append(card(x1, y, w, h, 28, border=GOLD, sw=4))
    o.append(place("dog", x1 + w / 2, 362, 150, 200))
    o.append(card(x2, y, w, h, 28))
    o.append(place("cat", x2 + w / 2, 370, 136, 232, flip=True))
    o.append(ripple(104, 478))
    for (sx, sy, R, rot) in [(30, 212, 15, -80), (110, 194, 11, -100), (195, 262, 12, -70), (12, 336, 10, -95), (196, 446, 9, -85),
                             (16, 500, 13, -100), (176, 532, 14, -75), (92, 546, 9, -90)]:
        o.append(gold_star(sx, sy, R, rot))
    for (sx, sy, r) in [(66, 202, 6), (150, 200, 7), (8, 272, 6), (198, 362, 6), (8, 424, 7), (134, 548, 6), (54, 538, 5)]:
        o.append(sparkle(sx, sy, r, "#F2C14E"))
    o.append(f'<circle cx="176" cy="224" r="22" fill="{GOLD}" filter="{card_shadow(.18, 3, 4)}"/>'
             '<path d="M165,224 L173,232 L188,216" stroke="#FFFFFF" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(f'<rect x="96" y="600" width="198" height="46" rx="23" fill="#FFFFFF" fill-opacity=".75" stroke="{EDGE}"/>')
    o.append(ic(i_speaker(SOFT), 124, 623, .8) + tx(208, 631, "對了！是小狗", 20, INK))
    o.append('</g>')
    o.append(dots(195, 782, 5, 1))
    return page("".join(o), BG)


# ---------------------------------------------------------------- 4 who is calling
def screen_listen():
    o = [kid_bg()]
    cx, cy = 195, 150
    for r, op in ((118, .07), (98, .12), (80, .2)):
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{TEAL}" opacity="{op}"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="64" fill="{lg([(0, lt(TEAL, .12)), (1, dk(TEAL, .08))])}" filter="{card_shadow(.2, 5, 7)}"/>')
    o.append(ic(i_speaker("#FFFFFF"), cx, cy, 2.3))
    o.append(tx(cx, 304, "是誰在叫？", 30, INK))
    for i, (n, w, h) in enumerate((("cow", 230, 124), ("duck", 200, 124), ("dog", 200, 126))):
        y = 330 + i * 162
        o.append(card(26, y, 338, 148, 26))
        o.append(place(n, 195, y + 74, w, h))
    return page("".join(o), BG)


# ---------------------------------------------------------------- 5 shadow match
def screen_shadow():
    o = [kid_bg()]
    o.append('<g transform="translate(0 30)">')
    o.append(f'<circle cx="104" cy="62" r="20" fill="{TEAL}"/>' + ic(i_speaker("#FFFFFF"), 104, 62, .75))
    o.append(tx(136, 71, "影子是誰呢？", 24, INK, "start"))
    o.append(card(64, 100, 262, 226, 28, fill="#F7F8F9"))
    o.append(ground(195, 268, 92, 8, .14))
    o.append(place("banana", 195, 212, 206, 128, shadow=True, color="#3B4652"))
    o.append('<path d="M183,344 L195,356 L207,344 M183,360 L195,372 L207,360" stroke="#B9B2A6" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(card(22, 396, 164, 250, 28))
    o.append(place("banana", 104, 521, 150, 112))
    o.append(card(204, 396, 164, 250, 28))
    o.append(place("apple", 286, 521, 128, 128))
    o.append('</g>')
    o.append(dots(195, 782, 5, 3))
    return page("".join(o), BG)


# ---------------------------------------------------------------- 6 parent mode: my family cards
PBG, PINK, PACC, PLINE, PSOFT = "#EEF1F4", "#34404B", "#4F6D8C", "#D3D9DF", "#7C8792"


def person(kind, col="#BFC6CE", hair="#A4ADB7"):
    """A plain silhouette for a photo placeholder (no face drawn)."""
    o = []
    if kind == "mom":
        o.append(f'<path d="M-19,-6 C-22,-34 22,-34 19,-6 L22,18 L-22,18Z" fill="{hair}"/>')
    o.append(f'<path d="M-32,40 C-32,16 -18,10 0,10 C18,10 32,16 32,40Z" fill="{col}"/>')
    o.append(f'<circle cx="0" cy="-8" r="15" fill="{col}"/>')
    if kind == "dad":
        o.append(f'<path d="M-15.5,-11 C-15,-27 15,-27 15.5,-11 C8,-17 -8,-17 -15.5,-11Z" fill="{hair}"/>')
    if kind == "grandma":
        o.append(f'<circle cx="0" cy="-27" r="7.5" fill="{hair}"/>'
                 f'<path d="M-15.5,-10 C-15,-26 15,-26 15.5,-10 C8,-15 -8,-15 -15.5,-10Z" fill="{hair}"/>')
    if kind == "bottle":
        o = [f'<rect x="-8" y="-34" width="16" height="9" rx="3" fill="{hair}"/>',
             f'<rect x="-15" y="-26" width="30" height="62" rx="10" fill="{col}"/>',
             f'<rect x="-15" y="0" width="30" height="10" fill="{hair}"/>']
    return "".join(o)


def photo_ph(x, y, w, h, kind, rx=10):
    cp = clip(f"M{x + rx},{y} H{x + w - rx} A{rx},{rx} 0 0 1 {x + w},{y + rx} V{y + h - rx} A{rx},{rx} 0 0 1 {x + w - rx},{y + h} "
              f"H{x + rx} A{rx},{rx} 0 0 1 {x},{y + h - rx} V{y + rx} A{rx},{rx} 0 0 1 {x + rx},{y}Z")
    s = min(w, h) / 80
    dy = .62 if kind != "bottle" else .5
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="#E3E7EB"/>'
            f'<g clip-path="{cp}"><g transform="translate({x + w / 2} {y + h * dy}) scale({s:.3f})">{person(kind)}</g></g>')


def screen_family():
    o = [f'<rect width="{W}" height="{H}" fill="{PBG}"/>']
    o.append(ic(i_back(PINK), 30, 58))
    o.append(tx(195, 66, "我的家人卡", 21, PINK))
    o.append(f'<rect x="318" y="44" width="54" height="28" rx="14" fill="{PACC}"/>' + tx(345, 63, "家長", 14, "#FFFFFF"))
    # new card
    o.append(f'<rect x="16" y="92" width="358" height="420" rx="20" fill="#FFFFFF" stroke="{PLINE}"/>')
    o.append(tx(36, 124, "做一張新的卡", 16, PSOFT, "start"))
    o.append(f'<rect x="36" y="140" width="150" height="182" rx="14" fill="#FFFFFF" stroke="{PLINE}" stroke-width="1.5"/>')
    o.append(photo_ph(44, 148, 134, 134, "grandma"))
    o.append(tx(111, 308, "阿嬤", 15, PINK))
    o.append(f'<rect x="202" y="140" width="152" height="52" rx="14" fill="{PACC}"/>'
             + ic(i_camera("#FFFFFF", PACC), 232, 166, .95) + tx(290, 173, "拍照", 18, "#FFFFFF"))
    o.append(f'<rect x="202" y="204" width="152" height="52" rx="14" fill="#C9675B"/>'
             + ic(i_mic("#FFFFFF"), 228, 231, .95) + tx(292, 237, "錄下名字", 17, "#FFFFFF"))
    o.append(f'<rect x="202" y="266" width="152" height="56" rx="14" fill="#F6E9E6"/>')
    o.append(f'<circle cx="224" cy="294" r="13" fill="#FFFFFF"/>' + ic(i_play("#C9675B"), 223, 294, .7))
    bars = [6, 12, 20, 14, 26, 18, 30, 22, 12, 24, 16, 8, 14, 6]
    o.append("".join(f'<rect x="{244 + i * 6.4:.1f}" y="{294 - b / 2}" width="3.6" height="{b}" rx="1.8" fill="#C9675B" opacity="{.95 if i < 9 else .4}"/>' for i, b in enumerate(bars)))
    o.append(tx(346, 316, "0:02", 11, "#B07068", "end"))
    o.append(tx(36, 356, "名字", 15, PSOFT, "start"))
    o.append(f'<rect x="36" y="366" width="318" height="50" rx="12" fill="#FFFFFF" stroke="{PACC}" stroke-width="1.8"/>')
    o.append(tx(52, 399, "阿嬤", 21, PINK, "start") + f'<rect x="96" y="380" width="2" height="24" fill="{PACC}"/>')
    o.append(f'<rect x="36" y="436" width="318" height="54" rx="14" fill="{PACC}"/>' + tx(195, 470, "做好了，放進卡片盒", 18, "#FFFFFF"))
    # cards already made
    o.append(f'<rect x="16" y="528" width="358" height="226" rx="20" fill="#FFFFFF" stroke="{PLINE}"/>')
    o.append(tx(36, 560, "已經做好的卡（4）", 16, PSOFT, "start"))
    for i, (kind, name) in enumerate((("dad", "爸爸"), ("mom", "媽媽"), ("grandma", "阿嬤"), ("bottle", "我的水壺"))):
        x = 36 + i * 82
        o.append(f'<rect x="{x}" y="576" width="72" height="104" rx="12" fill="#FFFFFF" stroke="{PLINE}" stroke-width="1.5"/>')
        o.append(photo_ph(x + 6, 582, 60, 64, kind, 8))
        o.append(tx(x + 36, 668, name, 13, PINK))
        o.append(ic(i_speaker("#A6B0BA"), x + 36, 700, .55))
    o.append(tx(195, 736, "長按一張卡，可以改名字、重錄聲音或刪掉", 13, PSOFT))
    o.append(ic(i_shield("#8FA3B5"), 106, 790, .8) + tx(122, 795, "照片和聲音只存在這支手機裡", 13, PSOFT, "start"))
    return page("".join(o), PBG)


# ---------------------------------------------------------------- 7 rest
def screen_rest():
    o = [f'<rect width="{W}" height="{H}" fill="{lg([(0, "#E4E3EF"), (.55, "#EFEAEC"), (1, "#F5EEE6")])}"/>']
    x, y, w, h = 45, 64, 300, 300
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="30" fill="{lg([(0, "#2F3A66"), (1, "#5D6AA2")])}" filter="{card_shadow(.18, 6, 10)}"/>')
    cp = clip(f"M{x + 30},{y} H{x + w - 30} A30,30 0 0 1 {x + w},{y + 30} V{y + h - 30} A30,30 0 0 1 {x + w - 30},{y + h} H{x + 30} A30,30 0 0 1 {x},{y + h - 30} V{y + 30} A30,30 0 0 1 {x + 30},{y}Z")
    rng = random.Random(3)
    sky = []
    for _ in range(26):
        sx, sy = rng.uniform(x + 14, x + w - 14), rng.uniform(y + 14, y + h - 70)
        if math.hypot(sx - 200, sy - 206) < 90:
            continue
        sky.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{rng.uniform(.8, 1.8):.1f}" fill="#FFF6D8" opacity="{rng.uniform(.5, .95):.2f}"/>')
    for sx, sy, r in ((92, 104, 7), (96, 290, 6), (110, 214, 5), (300, 250, 7)):
        sky.append(sparkle(sx, sy, r, "#FFF1C2", .95))
    D.add("moonmask", f'<mask id="moonmask" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
                      f'<rect width="{W}" height="{H}" fill="#fff"/><circle cx="232" cy="186" r="58" fill="#000"/></mask>')
    moon = (f'<circle cx="200" cy="206" r="96" fill="#FFF0BE" opacity=".16" filter="{blur(16)}"/>'
            f'<g mask="url(#moonmask)"><circle cx="200" cy="206" r="64" fill="{rg([(0, "#FFF8DA"), (.7, "#F6E3A4"), (1, "#E8CC80")], cx=.38, cy=.42)}"/>'
            '<g fill="#D9BC70" opacity=".35"><circle cx="164" cy="214" r="8"/><circle cx="176" cy="246" r="5"/><circle cx="158" cy="184" r="4.5"/><circle cx="186" cy="262" r="3.5"/></g></g>')
    clouds = (f'<g fill="#FFFFFF" opacity=".9" filter="{blur(1.2)}">'
              '<path d="M58,380 L58,352 C56,330 82,322 96,332 C104,312 136,314 142,334 C160,330 176,342 172,358 L172,380Z"/>'
              '<path d="M224,380 L224,360 C224,342 246,336 258,344 C266,328 292,330 296,348 C312,346 326,356 322,368 L322,380Z" opacity=".75"/></g>')
    zz = (tx(268, 150, "z", 18, "#FFF1C2", extra='opacity=".8"') + tx(286, 128, "z", 24, "#FFF1C2", extra='opacity=".9"')
          + tx(308, 102, "z", 30, "#FFF1C2"))
    o.append(f'<g clip-path="{cp}">{"".join(sky)}{moon}{clouds}{zz}</g>')
    o.append(tx(195, 424, "眼睛休息一下，", 26, INK))
    o.append(tx(195, 464, "我們去找找家裡的杯子吧！", 26, INK))
    o.append(card(112, 500, 166, 176, 26))
    o.append(place("cup", 195, 590, 118, 118))
    o.append(f'<circle cx="122" cy="508" r="24" fill="{SAGE}" filter="{card_shadow(.16, 3, 4)}"/>' + ic(i_home("#FFFFFF", SAGE), 122, 508, 1.0))
    o.append(f'<rect x="276" y="776" width="92" height="42" rx="21" fill="#E2DDD6"/>' + ic(i_lock("#8A939B"), 300, 796, .72)
             + tx(336, 803, "家長", 17, "#7E878F"))
    return page("".join(o), BG)


SCREENS = {"1_卡片盒": screen_decks, "2_翻翻卡": screen_flip, "3_找找看": screen_find, "4_聽聲音": screen_listen,
           "5_影子配對": screen_shadow, "6_我的家人卡": screen_family, "7_休息一下": screen_rest}


def contact_sheet(names):
    cw_, ch_, gap, m = 250, 541, 18, 30
    w = len(names) * cw_ + (len(names) - 1) * gap + 2 * m
    h = ch_ + 96
    imgs = "".join(f'<div style="position:absolute;left:{m + i * (cw_ + gap)}px;top:30px;width:{cw_}px;text-align:center">'
                   f'<img src="file://{HERE / (n + ".png")}" style="width:{cw_}px;height:{ch_}px;border-radius:18px;box-shadow:0 6px 16px rgba(60,50,40,.18)">'
                   f'<div style="font:20px Huninn, sans-serif;color:{INK};margin-top:12px">{n.replace("_", " ")}</div></div>' for i, n in enumerate(names))
    css = f"@font-face {{ font-family: Huninn; src: url('file://{FONT}'); }} * {{ margin:0; padding:0 }} body {{ width:{w}px; height:{h}px; background:#F3F0EA; position:relative }}"
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{imgs}</body></html>', w, h


def items_sheet():
    names = list(THINGS)
    cols, cw, ch = 4, 420, 340
    rows = (len(names) + cols - 1) // cols
    o = []
    for i, n in enumerate(names):
        x, y = 20 + (i % cols) * (cw + 20), 20 + (i // cols) * (ch + 20)
        o.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="24" fill="#fff" stroke="{EDGE}"/>')
        o.append(place(n, x + cw / 2, y + ch / 2 - 10, cw - 60, ch - 80))
        o.append(tx(x + cw / 2, y + ch - 16, n, 18, SOFT))
    w, h = 20 + cols * (cw + 20), 20 + rows * (ch + 20)
    return page("".join(o), BG, w, h), w, h


def main(only=None):
    global D
    if only == "items":
        D = Defs()
        html, w, h = items_sheet()
        out = pathlib.Path(tempfile.gettempdir()) / "card_game_items.png"
        render(html, out, w, h, 1.5)
        print(out)
        return
    if only in (None, "0"):
        D = Defs()
        render(style_sheet(), HERE / "0_畫風選擇.png", 1600, 900, 1)
        print("0_畫風選擇")
    for name, make in SCREENS.items():
        if only not in (None, name[0]):
            continue
        D = Defs()
        render(make(), HERE / f"{name}.png", W, H, 2)
        print(name)
    if only in (None, "c"):
        html, w, h = contact_sheet(list(SCREENS))
        render(html, HERE / "contact_sheet.png", w, h, 1.5)
        print("contact_sheet")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)

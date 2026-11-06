"""小卡認天下's app icon: two picture cards, slightly fanned, on a soft teal background.
The front card shows the realistic dog of the animals deck, the card behind it the realistic apple.

    python3 icon.py preview out.png   # a sheet: round / squircle / square masks at 48, 96 and 192 px, and a big one
    python3 icon.py export            # writes the Android and iOS icons into app/

export writes
- Android, full square art: app/android/app/src/main/res/mipmap-{mdpi..xxxhdpi}/ic_launcher.png (48..192 px, opaque).
- Android adaptive icon (API 26+): mipmap-anydpi-v26/ic_launcher.xml, with
  drawable-{mdpi..xxxhdpi}/ic_launcher_foreground.png and ic_launcher_background.png
  (108 dp canvas; the cards stay inside the central 66 dp circle).
- iOS: every PNG listed in app/ios/Runner/Assets.xcassets/AppIcon.appiconset/Contents.json,
  at its size, opaque (no alpha).
Needs Node.js with Playwright (Chromium draws the SVGs; render_alpha.js) and Pillow.
"""
import json
import math
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw

import deck_animals
import deck_fruits
import kit_af as K

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
APP = ROOT / "app"
RES = APP / "android" / "app" / "src" / "main" / "res"
IOS = APP / "ios" / "Runner" / "Assets.xcassets" / "AppIcon.appiconset"
RENDER = HERE / "render_alpha.js"

C = 1024
DENSITIES = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
TEAL = ("#9AD3CA", "#6BB5AC", "#4A938B")

# the two drawings, measured once: (defs, body, bbox in their own units)
_ART = {}


def art(name):
    if name not in _ART:
        fn = {"dog": deck_animals.dog, "apple": deck_fruits.apple}[name]
        K.begin()
        body = fn()
        defs = K.D.svg()
        box = K._measure({name: (defs, body)})[name]
        _ART[name] = (defs, body, box)
    return _ART[name]


def picture(name, cx, cy, size):
    """The drawing centred at (cx, cy), its longer side `size`."""
    defs, body, (x0, y0, x1, y1) = art(name)
    s = size / max(x1 - x0, y1 - y0)
    return defs, (f'<g transform="translate({cx} {cy}) scale({s:.4f}) translate({-(x0 + x1) / 2:.1f} {-(y0 + y1) / 2:.1f})">'
                  f'{body}</g>')


def card(cx, cy, w, h, rot, inner):
    """A white rounded card with a soft shadow, turned by rot degrees."""
    r = w * .12
    return (f'<g transform="translate({cx} {cy}) rotate({rot})">'
            f'<rect x="{-w / 2 + 6}" y="{-h / 2 + 18}" width="{w}" height="{h}" rx="{r}" fill="#123A36" opacity=".28" filter="url(#sh)"/>'
            f'<rect x="{-w / 2}" y="{-h / 2}" width="{w}" height="{h}" rx="{r}" fill="#FFFFFF"/>'
            f'<rect x="{-w / 2 + 3}" y="{-h / 2 + 3}" width="{w - 6}" height="{h - 6}" rx="{r - 3}" fill="none" stroke="#E6EEEC" stroke-width="6"/>'
            f'{inner}</g>')


def subject_svg(px, radius):
    """The two cards, see-through around them, centred so the drawing reaches `radius` (in 1024ths) from the middle."""
    w, h = 480, 548
    d1, apple = picture("apple", -20, -30, 300)
    d2, dog = picture("dog", 0, 4, 420)
    back = card(-112, -36, w, h, -13, apple)
    front = card(90, 36, w, h, 8, dog)
    s = radius / 520 * FIT.get(radius, 1.0)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {C} {C}" width="{px}" height="{px}">'
            f'<defs><filter id="sh" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="22"/></filter></defs>'
            f'{d1}{d2}<g transform="translate({C / 2} {C / 2}) scale({s:.4f})">{back}{front}</g></svg>')


def background_svg(px):
    """Soft teal, a little lighter in the middle."""
    a, b, c = TEAL
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {C} {C}" width="{px}" height="{px}">'
            f'<defs><radialGradient id="bg" cx=".45" cy=".4" r=".8"><stop offset="0" stop-color="{a}"/>'
            f'<stop offset=".55" stop-color="{b}"/><stop offset="1" stop-color="{c}"/></radialGradient></defs>'
            f'<rect width="{C}" height="{C}" fill="url(#bg)"/>'
            f'<circle cx="{C * .5}" cy="{C * .5}" r="{C * .36}" fill="#FFFFFF" opacity=".08"/></svg>')


FULL_R = 0.44 * C                 # full square art (legacy Android, iOS)
SAFE_R = 33 / 108 * C * 0.97      # adaptive foreground: the central 66 dp circle of 108 dp
FIT = {}


# ---------------------------------------------------------------- rendering
def render(svg_text, px):
    with tempfile.TemporaryDirectory() as tmp:
        src, out = pathlib.Path(tmp) / "in.svg", pathlib.Path(tmp) / "out.png"
        src.write_text(svg_text)
        subprocess.run(["node", str(RENDER), str(src), str(out), str(px), str(px)], check=True)
        return Image.open(out).convert("RGBA").copy()


def reach(img):
    """How far from the middle the opaque part of the image reaches (ignoring the faint shadow)."""
    a = img.getchannel("A")
    w, h = img.size
    px = a.load()
    best = 0.0
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            if px[x, y] > 200:
                best = max(best, math.hypot(x + 0.5 - w / 2, y + 0.5 - h / 2))
    return best


def fit():
    for radius in (FULL_R, SAFE_R):
        FIT[radius] = 1.0
        got = reach(render(subject_svg(512, radius), 512)) * C / 512
        FIT[radius] = radius / got


def full_art():
    bg = render(background_svg(C), C)
    fg = render(subject_svg(C, FULL_R), C)
    return Image.alpha_composite(bg, fg).convert("RGB")


def adaptive_layers():
    return render(background_svg(C), C).convert("RGB"), render(subject_svg(C, SAFE_R), C)


def resized(img, px):
    return img.resize((px, px), Image.LANCZOS)


def mask(kind, px):
    m = Image.new("L", (px * 4, px * 4), 0)
    dr = ImageDraw.Draw(m)
    s = px * 4
    if kind == "round":
        dr.ellipse((0, 0, s - 1, s - 1), fill=255)
    elif kind == "squircle":
        pts = []
        for i in range(720):
            t = 2 * math.pi * i / 720
            c, si = math.cos(t), math.sin(t)
            pts.append((s / 2 + s / 2 * math.copysign(abs(c) ** (2 / 5), c), s / 2 + s / 2 * math.copysign(abs(si) ** (2 / 5), si)))
        dr.polygon(pts, fill=255)
    else:
        dr.rounded_rectangle((0, 0, s - 1, s - 1), radius=s * 0.08, fill=255)
    return m.resize((px, px), Image.LANCZOS)


def preview(out):
    fit()
    full = full_art()
    bg, fg = adaptive_layers()
    adaptive = Image.alpha_composite(bg.convert("RGBA"), fg).convert("RGB")
    k = C * 18 / 108          # a launcher shows the middle 72 dp of the 108 dp canvas
    adaptive_view = adaptive.crop((round(k), round(k), round(C - k), round(C - k)))
    sizes = (48, 96, 192)
    rows = [("round", adaptive_view), ("squircle", adaptive_view), ("square", full)]
    pad = 24
    W = pad + sum(s + pad for s in sizes) + 420 + pad
    H = pad + len(rows) * (192 + pad) + 120
    sheet = Image.new("RGB", (W, H), "#E9E4DE")
    sheet.paste(Image.new("RGB", (W, 120), "#2F2B33"), (0, H - 120))
    for r, (kind, art_) in enumerate(rows):
        x = pad
        y = pad + r * (192 + pad)
        for s in sizes:
            sheet.paste(resized(art_, s), (x, y + 192 - s), mask(kind, s))
            x += s + pad
    sheet.paste(resized(full, 420), (W - pad - 420, pad), mask("squircle", 420))
    x = pad
    for kind, art_ in rows:
        sheet.paste(resized(art_, 72), (x, H - 96), mask(kind, 72))
        x += 72 + pad
    sheet.save(out)
    print(out)


ADAPTIVE_XML = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
</adaptive-icon>
"""


def export():
    fit()
    full = full_art()
    bg, fg = adaptive_layers()
    written = []
    for name, k in DENSITIES.items():
        mip = RES / f"mipmap-{name}"
        mip.mkdir(parents=True, exist_ok=True)
        resized(full, round(48 * k)).save(mip / "ic_launcher.png")
        draw = RES / f"drawable-{name}"
        draw.mkdir(parents=True, exist_ok=True)
        resized(fg, round(108 * k)).save(draw / "ic_launcher_foreground.png")
        resized(bg, round(108 * k)).save(draw / "ic_launcher_background.png")
        written += [mip / "ic_launcher.png", draw / "ic_launcher_foreground.png", draw / "ic_launcher_background.png"]
    anydpi = RES / "mipmap-anydpi-v26"
    anydpi.mkdir(parents=True, exist_ok=True)
    (anydpi / "ic_launcher.xml").write_text(ADAPTIVE_XML)
    written.append(anydpi / "ic_launcher.xml")
    contents = json.loads((IOS / "Contents.json").read_text())
    for image in contents["images"]:
        if not image.get("filename"):
            continue
        size = float(image["size"].split("x")[0]) * float(image["scale"].rstrip("x"))
        resized(full, round(size)).convert("RGB").save(IOS / image["filename"])
        written.append(IOS / image["filename"])
    manifest = (APP / "android" / "app" / "src" / "main" / "AndroidManifest.xml").read_text()
    if 'android:icon="@mipmap/ic_launcher"' not in manifest:
        print("note: AndroidManifest.xml's android:icon is not @mipmap/ic_launcher")
    for p in written:
        print(p.relative_to(ROOT))


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "export":
        export()
    elif len(sys.argv) >= 3 and sys.argv[1] == "preview":
        preview(sys.argv[2])
    else:
        print(__doc__)

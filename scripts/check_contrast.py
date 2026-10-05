"""
Text-over-photograph contrast check.

check.py can assert that an image has alt text; it cannot know whether the
headline sitting on top of that image is readable. Once the generated plates
were replaced by photographs this stopped being theoretical: the section hero
label measured 2.9:1 over a snow field, having measured fine over a flat grey
plate the day before.

So this composites each photograph under the same scrim gradient the CSS
applies, samples the region the copy actually occupies, and reports the worst
contrast ratio found against every text colour used there.

Needs Pillow, like build_photos.py, and is therefore separate from check.py,
which stays dependency free.

    python scripts/check_contrast.py

Numbers are approximations of a browser paint, not a substitute for looking at
the page. They are, however, enough to catch a scrim that has stopped working.
"""

import json
import pathlib
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("check_contrast: needs Pillow.  python -m pip install Pillow")

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "docs" / "assets" / "img"

AA_BODY = 4.5
INK = (10, 11, 12)          # the scrim colour in index.css

# The text colours actually painted over each kind of photograph, read off the
# component blocks in index.css. Listing them per case rather than as one pool
# matters: the dimmest tone in the hero (.hero__field dt) does not appear on an
# index card, and the dimmest on a card does not appear in a hero.
HERO_TEXT = {
    "title": "#EDE9E1",       # .hero__title, .hero__field dd
    "lede": "#CFCAC0",        # .hero__lede
    "label": "#C9C4B8",       # .hero__label
    "field-dt": "#BFBAB1",    # .hero__field dt
}
CARD_TEXT = {
    "title": "#EDE9E1",       # .index-card__title, .index-card__stat b
    "blurb": "#C4BFB5",       # .index-card--media .index-card__blurb
    "detail": "#B3AEA5",      # .index-card--media .index-card__detail, __stat, __n
}

# name, slot, box, scrim stops, axis, copy region (x0, x1, y0, y1), colours
#
# The copy region is generous on purpose. A compact hero stacks a label, an h1,
# a lede and a four cell field list, so the block starts higher up the box than
# a glance at the page suggests.
CASES = [
    ("home hero", "hero-home", (1440, 860),
     [(0.00, 0.90), (0.42, 0.74), (1.00, 0.30)], "x", (0.06, 0.52, 0.30, 0.95), HERO_TEXT),
]
for section in ("ride", "navigate", "survive", "maintain", "market", "news", "workshop"):
    CASES.append((
        f"{section} hero", f"hero-{section}", (1440, 560),
        [(0.00, 0.48), (0.38, 0.82), (1.00, 0.93)], "y", (0.06, 0.52, 0.30, 0.95), HERO_TEXT,
    ))
# Equip reuses the index-equip photograph as a compact section hero under the
# same flat scrim, so it gets the hero treatment rather than only the card one.
CASES.append((
    "equip hero", "index-equip", (1440, 560),
    [(0.00, 0.48), (0.38, 0.82), (1.00, 0.93)], "y", (0.06, 0.52, 0.30, 0.95), HERO_TEXT,
))
for card in ("index-ride", "index-navigate", "index-equip"):
    CASES.append((
        f"{card} card", card, (620, 460),
        [(0.00, 0.45), (0.45, 0.80), (1.00, 0.94)], "y", (0.08, 0.92, 0.42, 0.94), CARD_TEXT,
    ))


def luminance(rgb):
    channels = []
    for value in rgb:
        value /= 255.0
        channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    high, low = max(la, lb), min(la, lb)
    return (high + 0.05) / (low + 0.05)


def to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def alpha_at(stops, position):
    for i in range(len(stops) - 1):
        (p0, a0), (p1, a1) = stops[i], stops[i + 1]
        if position <= p1:
            if p1 == p0:
                return a0
            return a0 + (a1 - a0) * ((position - p0) / (p1 - p0))
    return stops[-1][1]


def cover(slot_id, box):
    """object-fit: cover, the same crop the browser will make."""
    path = IMG / f"{slot_id}.jpg"
    if not path.exists():
        path = IMG / f"{slot_id}.svg"
        if path.exists():
            return None                       # artwork, not a photograph
        sys.exit(f"check_contrast: no file for {slot_id}")

    im = Image.open(path).convert("RGB")
    bw, bh = box
    scale = max(bw / im.width, bh / im.height)
    im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
    left, top = (im.width - bw) // 2, (im.height - bh) // 2
    return im.crop((left, top, left + bw, top + bh))


def measure(slot_id, box, stops, axis, region, colours):
    im = cover(slot_id, box)
    if im is None:
        return None

    bw, bh = box
    x0, x1 = int(bw * region[0]), int(bw * region[1])
    y0, y1 = int(bh * region[2]), int(bh * region[3])
    pixels = im.load()

    worst = {name: 99.0 for name in colours}
    for y in range(y0, y1, 2):
        row_alpha = alpha_at(stops, y / bh) if axis == "y" else None
        for x in range(x0, x1, 2):
            alpha = row_alpha if row_alpha is not None else alpha_at(stops, x / bw)
            r, g, b = pixels[x, y]
            backdrop = (
                r * (1 - alpha) + INK[0] * alpha,
                g * (1 - alpha) + INK[1] * alpha,
                b * (1 - alpha) + INK[2] * alpha,
            )
            for name, colour in colours.items():
                ratio = contrast(to_rgb(colour), backdrop)
                if ratio < worst[name]:
                    worst[name] = ratio
    return worst


def main():
    failures = []
    for label, slot_id, box, stops, axis, region, colours in CASES:
        worst = measure(slot_id, box, stops, axis, region, colours)
        if worst is None:
            print(f"{label:22} generated artwork, skipped")
            continue
        low = min(worst.values())
        cells = "  ".join(f"{n} {worst[n]:.2f}" for n in colours)
        mark = "" if low >= AA_BODY else "   UNDER 4.5:1"
        print(f"{label:22} {cells}   worst {low:5.2f}{mark}")
        if low < AA_BODY:
            failures.append((label, round(low, 2)))

    print()
    if failures:
        print(f"check_contrast: {len(failures)} case(s) below {AA_BODY}:1")
        for label, low in failures:
            print(f"  {label}: {low}")
        return 1

    print(f"check_contrast: every case clears {AA_BODY}:1")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
Frontier Moto photo pipeline.

Turns the source photographs in assets/photos/ into the derivatives the site
serves: an AVIF and a JPEG at each responsive width, cropped to the slot ratio
around a stated focal point, with all camera metadata stripped.

This is the one script in the project that needs a package (Pillow). It is an
asset step, not a build step: it runs when the photographs change, and its
output is committed. build.py and check.py stay dependency free, so anyone can
clone the repo and rebuild the site with a bare Python.

    python -m pip install Pillow
    python scripts/build_photos.py

Two rules the mapping below follows, both of them content rules rather than
technical ones:

  * Nothing is upscaled. Most sources are about 1170px wide, so the slot
    dimensions in content/images.json are whatever the photograph can honestly
    deliver after cropping. A soft hero is worse than a small one.
  * The focal point is set per photograph. A centre crop decapitates riders.
"""

import json
import pathlib
import sys

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("build_photos: needs Pillow.  python -m pip install Pillow")

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCES = ROOT / "assets" / "photos"
OUT = ROOT / "docs" / "assets" / "img"
CONTENT = ROOT / "content"

# Widths generated for each slot, largest first. Anything wider than the
# cropped source is dropped rather than upscaled.
WIDTHS = [2400, 1600, 1200, 800]
MIN_WIDTH = 640

# Ceiling per slot. Nothing benefits from a hero wider than the largest screen
# it fills, and an Open Graph card is read at exactly 1200x630 by every scraper
# that consumes it, so shipping a 5827px version of either is pure weight.
MAX_WIDTH = {"og-frontier": 1200}
DEFAULT_MAX = 2400

AVIF_QUALITY = 62
JPEG_QUALITY = 82

# slot id -> (source file, target ratio, focal x, focal y)
#
# The ratio is what the file is cropped to. Heroes and index cards are
# object-fit: cover in CSS, so their ratio only decides how much of the
# photograph is kept and how many bytes travel. The three feature slots share
# 3:2 because .feature__media and .article-card__media size themselves from the
# file, and a ragged grid would be the result of mixing ratios there.
PLAN = {
    "hero-home":          ("scrambler.jpg",           16 / 9,  0.50, 0.52),
    "hero-ride":          ("mountains-adv.avif",       2 / 1,  0.50, 0.55),
    "hero-navigate":      ("desert-mt-adv.avif",       2 / 1,  0.50, 0.55),
    "hero-survive":       ("wet-dirt-road.avif",       2 / 1,  0.50, 0.55),
    "hero-maintain":      ("spanenrs.avif",            2 / 1,  0.50, 0.50),
    "hero-market":        ("leather-jackets.avif",     2 / 1,  0.50, 0.50),
    "hero-news":          ("dash.avif",                2 / 1,  0.50, 0.50),
    "hero-workshop":      ("tool-wall.avif",           2 / 1,  0.50, 0.45),
    "hero-recovery":      ("desert-dirt-bike.avif",    2 / 1,  0.50, 0.62),

    "feature-escarpment": ("escarpemnt.avif",          3 / 2,  0.50, 0.50),
    "feature-chain":      ("motorcycle-computer.avif", 3 / 2,  0.50, 0.45),
    "feature-stage":      ("road-bike.avif",           3 / 2,  0.50, 0.55),

    "index-ride":         ("mtx-helmet.avif",          3 / 2,  0.50, 0.50),
    "index-navigate":     ("maps.avif",                3 / 4,  0.50, 0.66),
    "index-equip":        ("repair-shop.avif",         3 / 2,  0.50, 0.60),

    "market-gear":        ("helmets.avif",             4 / 3,  0.50, 0.35),
    "workshop-bay":       ("repair.avif",              3 / 4,  0.50, 0.50),
    "maintain-anatomy":   ("labelled-parts.png",    1572 / 1001, 0.50, 0.50),

    "og-frontier":        ("scrambler.jpg",         1200 / 630, 0.50, 0.50),
}

# Slots that stay as generated SVG artwork. maintain-diagram is a drawing whose
# six numbered callouts are keyed to content/technical.json, so a photograph
# cannot replace it.
KEEP_SVG = {"maintain-diagram"}


def crop_to(im, ratio, fx, fy):
    """Largest crop of the given ratio, positioned around the focal point."""
    w, h = im.size
    if w / h > ratio:
        cw, ch = int(round(h * ratio)), h
    else:
        cw, ch = w, int(round(w / ratio))

    left = min(max(int(round(w * fx - cw / 2)), 0), w - cw)
    top = min(max(int(round(h * fy - ch / 2)), 0), h - ch)
    return im.crop((left, top, left + cw, top + ch))


def widths_for(natural, ceiling):
    natural = min(natural, ceiling)
    picked = [w for w in WIDTHS if w <= natural and w >= MIN_WIDTH]
    if not picked or picked[0] != natural:
        picked.insert(0, natural)
    # Drop a width that is within 15 percent of the one above it; the extra
    # file would not change which one a browser picks.
    out = []
    for w in picked:
        if not out or w < out[-1] * 0.85:
            out.append(w)
    return out


def build_slot(slot_id, source, ratio, fx, fy):
    path = SOURCES / source
    if not path.exists():
        sys.exit(f"build_photos: missing source {path}")

    im = Image.open(path)
    im = ImageOps.exif_transpose(im).convert("RGB")   # also drops the EXIF block
    cropped = crop_to(im, ratio, fx, fy)
    ceiling = MAX_WIDTH.get(slot_id, DEFAULT_MAX)
    sizes = widths_for(cropped.width, ceiling)
    natural = sizes[0]

    made = []
    for w in sizes:
        h = int(round(w / (cropped.width / cropped.height)))
        frame = cropped if w == cropped.width else cropped.resize((w, h), Image.LANCZOS)
        suffix = "" if w == natural else f"-{w}"

        avif = OUT / f"{slot_id}{suffix}.avif"
        jpg = OUT / f"{slot_id}{suffix}.jpg"
        frame.save(avif, quality=AVIF_QUALITY)
        frame.save(jpg, quality=JPEG_QUALITY, optimize=True, progressive=True)
        made.append((w, h, avif.stat().st_size, jpg.stat().st_size))

    return {
        "w": made[0][0],
        "h": made[0][1],
        "source": source,
        "widths": [m[0] for m in made],
    }, made


def main():
    if not SOURCES.exists():
        sys.exit(f"build_photos: no source folder at {SOURCES}")

    OUT.mkdir(parents=True, exist_ok=True)
    images = json.loads((CONTENT / "images.json").read_text(encoding="utf-8"))
    slots = {s["id"]: s for s in images["slots"]}

    total_avif = total_jpg = 0
    print(f"build_photos: {len(PLAN)} slots from {SOURCES}\n")

    for slot_id, (source, ratio, fx, fy) in PLAN.items():
        if slot_id not in slots:
            sys.exit(f"build_photos: {slot_id} is not a slot in content/images.json")

        result, made = build_slot(slot_id, source, ratio, fx, fy)
        slots[slot_id].update(result)

        total_avif += sum(m[2] for m in made)
        total_jpg += sum(m[3] for m in made)
        widths = " ".join(str(m[0]) for m in made)
        print(f"  {slot_id:20} {source:26} {result['w']:5}x{result['h']:<5} [{widths}]")

        # The generated plate is no longer what this slot serves.
        stale = OUT / f"{slot_id}.svg"
        if stale.exists():
            stale.unlink()

    # Write the measured dimensions back so the markup and the files agree.
    (CONTENT / "images.json").write_text(
        json.dumps(images, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    write_manifest(images)

    kept = ", ".join(sorted(KEEP_SVG))
    print(f"\nbuild_photos: {total_avif / 1e6:.2f} MB avif, {total_jpg / 1e6:.2f} MB jpeg")
    print(f"build_photos: kept as generated artwork: {kept}")


def write_manifest(images):
    lines = [
        "# Image slots",
        "",
        "Generated by `scripts/build_photos.py` for photographs and",
        "`scripts/build_images.py` for the remaining artwork. Do not hand edit the",
        "files in this folder, they are overwritten.",
        "",
        "## Provenance",
        "",
        "The photographs are stock and reference imagery supplied for the build. They",
        "are not Frontier Moto field photographs, and none of them were taken in East",
        "Africa. Captions and alt text therefore describe what is in the frame and do",
        "not name a place. Confirm the licence for each file before treating the site",
        "as published work, and replace them as real field photography is shot.",
        "",
        "## Replacing a photograph",
        "",
        "1. Drop the new file into `assets/photos/`.",
        "2. Point the slot at it in the `PLAN` table in `scripts/build_photos.py`, with",
        "   a focal point if the subject is not centred.",
        "3. Run `python scripts/build_photos.py`, which rewrites the measured",
        "   dimensions in `content/images.json`, then `python scripts/build.py`.",
        "4. Update the caption and alt text in `content/images.json` so they still",
        "   describe the picture. Alt text is content and does not travel with a file.",
        "",
        "| Slot | File | Dimensions | Widths | Source | Alt text |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for slot in images["slots"]:
        sid = slot["id"]
        if sid in KEEP_SVG:
            lines.append(
                f"| `{sid}` | `{sid}.svg` | {slot['w']} x {slot['h']} | n/a | "
                f"generated artwork | {slot['alt']} |"
            )
            continue
        widths = " ".join(str(w) for w in slot.get("widths", [slot["w"]]))
        lines.append(
            f"| `{sid}` | `{sid}.avif` + `.jpg` | {slot['w']} x {slot['h']} | {widths} | "
            f"`{slot.get('source', 'n/a')}` | {slot['alt']} |"
        )

    (OUT / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

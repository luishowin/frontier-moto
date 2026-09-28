"""
Frontier Moto - image plate generator.

Every image slot in content/images.json becomes a deliberate SVG plate rather
than a grey box: brand palette, a faint technical grid, crop marks, a caption
and a slot reference, plus a composition drawn from the slot's `subject`. They
are meant to read as an editorial placeholder in the site's own language, so a
page looks finished before the photography exists.

Composition is deterministic. The seed comes from the slot id, so re-running
this produces byte identical files and never churns a diff.

Run:  python scripts/build_images.py
"""

import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUT = ROOT / "docs" / "assets" / "img"

# The plate palette is the site palette. Kept here rather than imported so the
# generator stays runnable on its own.
DARK = {
    "ground": "#16181A",
    "band": "#1E2124",
    "grid": "#2B2F33",
    "line": "#4A5054",
    "ink": "#8A8D8F",
    "bright": "#C9C4B8",
}
LIGHT = {
    "ground": "#E7E3DA",
    "band": "#DDD8CD",
    "grid": "#CFC9BC",
    "line": "#A9A294",
    "ink": "#6E6A62",
    "bright": "#2A2C2E",
}
SIGNAL = "#EED202"
MONO = "ui-monospace, 'Roboto Mono', 'DejaVu Sans Mono', 'Courier New', monospace"


class Seed:
    """A tiny deterministic generator. Same slot id, same picture, every run."""

    def __init__(self, key):
        self.state = int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:12], 16)

    def next(self):
        self.state = (self.state * 1103515245 + 12345) % (2 ** 31)
        return self.state / (2 ** 31)

    def between(self, lo, hi):
        return lo + (hi - lo) * self.next()


def esc(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ---------------------------------------------------------------------------
# Subjects. Each returns the inner markup for the picture area only; the frame,
# grid, crop marks and caption rail are added around it by plate().
# ---------------------------------------------------------------------------

def subject_highway(w, h, c, rnd):
    """Perspective road running to a vanishing point under a ridge line."""
    horizon = h * 0.60
    vp = w * rnd.between(0.44, 0.56)
    out = [ridge(w, h, horizon, c, rnd)]
    # Carriageway.
    out.append(
        f'<path d="M{w * -0.15:.0f} {h} L{vp - w * 0.02:.0f} {horizon:.0f} '
        f'L{vp + w * 0.02:.0f} {horizon:.0f} L{w * 1.15:.0f} {h} Z" '
        f'fill="{c["band"]}"/>'
    )
    out.append(
        f'<path d="M{w * -0.15:.0f} {h} L{vp - w * 0.02:.0f} {horizon:.0f}" '
        f'stroke="{c["line"]}" stroke-width="2" fill="none"/>'
    )
    out.append(
        f'<path d="M{w * 1.15:.0f} {h} L{vp + w * 0.02:.0f} {horizon:.0f}" '
        f'stroke="{c["line"]}" stroke-width="2" fill="none"/>'
    )
    # Centre line, foreshortened so the dashes shrink toward the vanishing point.
    t = 0.03
    while t < 0.94:
        y1 = horizon + (h - horizon) * (t ** 2.2)
        y2 = horizon + (h - horizon) * ((t + 0.05) ** 2.2)
        k1 = (y1 - horizon) / (h - horizon)
        x1 = vp + (w * 0.5 - vp) * k1
        x2 = vp + (w * 0.5 - vp) * ((y2 - horizon) / (h - horizon))
        out.append(
            f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{c["bright"]}" '
            f'stroke-width="{1 + 5 * k1:.1f}" opacity="0.55" fill="none"/>'
        )
        t += 0.09
    # The rider, small and well down the road. Safety yellow, the only accent.
    ry = horizon + (h - horizon) * 0.30
    rk = (ry - horizon) / (h - horizon)
    rx = vp + (w * 0.5 - vp) * rk + w * 0.035
    s = 6 + 26 * rk
    out.append(
        f'<rect x="{rx:.0f}" y="{ry - s:.0f}" width="{s * 0.5:.0f}" height="{s:.0f}" '
        f'rx="{s * 0.18:.0f}" fill="{SIGNAL}"/>'
    )
    return "\n".join(out)


def subject_descent(w, h, c, rnd):
    """Switchbacks falling away down a slope toward a valley floor."""
    horizon = h * 0.34
    out = [ridge(w, h, horizon, c, rnd)]
    out.append(f'<rect x="0" y="{horizon:.0f}" width="{w}" height="{h - horizon:.0f}" fill="{c["band"]}"/>')
    rows = 5
    for i in range(rows):
        y = horizon + (h - horizon) * (0.16 + 0.19 * i)
        inset = w * (0.06 + 0.05 * i)
        left = i % 2 == 0
        x1, x2 = (inset, w - inset) if left else (w - inset, inset)
        bend = w * 0.06 * (1 if left else -1)
        out.append(
            f'<path d="M{x1:.0f} {y:.0f} L{x2:.0f} {y:.0f} '
            f'q{bend:.0f} {(h - horizon) * 0.09:.0f} {bend * 0.2:.0f} {(h - horizon) * 0.19:.0f}" '
            f'stroke="{c["line"]}" stroke-width="{3 + i}" fill="none" stroke-linecap="round"/>'
        )
    # Rain front on the far ridge.
    for i in range(9):
        x = w * (0.52 + 0.045 * i)
        out.append(
            f'<path d="M{x:.0f} {horizon * 0.30:.0f} L{x - w * 0.02:.0f} {horizon * 0.92:.0f}" '
            f'stroke="{c["line"]}" stroke-width="1.5" opacity="0.5" fill="none"/>'
        )
    out.append(
        f'<circle cx="{w * 0.22:.0f}" cy="{horizon + (h - horizon) * 0.16:.0f}" r="{max(5, w * 0.008):.0f}" fill="{SIGNAL}"/>'
    )
    return "\n".join(out)


def subject_roadside(w, h, c, rnd):
    """A machine stopped well clear of the carriageway, marker back up the road."""
    horizon = h * 0.52
    out = [ridge(w, h, horizon, c, rnd)]
    out.append(f'<rect x="0" y="{horizon:.0f}" width="{w}" height="{h - horizon:.0f}" fill="{c["band"]}"/>')
    edge = horizon + (h - horizon) * 0.42
    out.append(f'<path d="M0 {edge:.0f} L{w} {edge - h * 0.04:.0f}" stroke="{c["line"]}" stroke-width="3" fill="none"/>')
    # Stopped machine, side on, off the carriageway.
    bx, by, bw = w * 0.60, edge + (h - edge) * 0.34, w * 0.13
    out.append(f'<circle cx="{bx:.0f}" cy="{by:.0f}" r="{bw * 0.22:.0f}" fill="none" stroke="{c["bright"]}" stroke-width="4"/>')
    out.append(f'<circle cx="{bx + bw:.0f}" cy="{by:.0f}" r="{bw * 0.22:.0f}" fill="none" stroke="{c["bright"]}" stroke-width="4"/>')
    out.append(
        f'<path d="M{bx:.0f} {by:.0f} L{bx + bw * 0.36:.0f} {by - bw * 0.30:.0f} '
        f'L{bx + bw * 0.78:.0f} {by - bw * 0.30:.0f} L{bx + bw:.0f} {by:.0f}" '
        f'stroke="{c["bright"]}" stroke-width="4" fill="none" stroke-linejoin="round"/>'
    )
    # Warning triangle, well back up the road, in the accent.
    tx, ty, ts = w * 0.22, edge + (h - edge) * 0.30, w * 0.035
    out.append(f'<path d="M{tx:.0f} {ty - ts:.0f} L{tx + ts * 0.86:.0f} {ty:.0f} L{tx - ts * 0.86:.0f} {ty:.0f} Z" fill="{SIGNAL}"/>')
    return "\n".join(out)


def subject_chain(w, h, c, rnd):
    """Drive chain running across the plate over a sprocket arc."""
    cy = h * 0.56
    out = [f'<rect x="0" y="{h * 0.30:.0f}" width="{w}" height="{h * 0.70:.0f}" fill="{c["band"]}"/>']
    r = h * 0.30
    cx = w * 0.74
    out.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" fill="none" stroke="{c["line"]}" stroke-width="6"/>')
    teeth = 22
    for i in range(teeth):
        import math
        a = (2 * math.pi / teeth) * i
        x1, y1 = cx + r * math.cos(a), cy + r * math.sin(a)
        x2, y2 = cx + (r + h * 0.035) * math.cos(a), cy + (r + h * 0.035) * math.sin(a)
        out.append(f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{c["line"]}" stroke-width="5"/>')
    # Chain run.
    pitch = w * 0.052
    x = w * 0.02
    idx = 0
    while x < w * 0.60:
        out.append(
            f'<rect x="{x:.0f}" y="{cy - r - h * 0.045:.0f}" width="{pitch * 0.78:.0f}" '
            f'height="{h * 0.09:.0f}" rx="{h * 0.045:.0f}" fill="none" '
            f'stroke="{SIGNAL if idx == 4 else c["bright"]}" stroke-width="4"/>'
        )
        x += pitch
        idx += 1
    return "\n".join(out)


def subject_gear(w, h, c, rnd):
    """Flat lay. Kit laid out in order, which is how it should be packed."""
    out = [f'<rect x="0" y="0" width="{w}" height="{h}" fill="{c["band"]}" opacity="0.5"/>']
    cols, rows = 4, 3
    pad = w * 0.045
    cw = (w - pad * (cols + 1)) / cols
    ch = (h - pad * (rows + 1)) / rows
    accent = int(rnd.between(0, cols * rows))
    for r in range(rows):
        for col in range(cols):
            i = r * cols + col
            x = pad + col * (cw + pad)
            y = pad + r * (ch + pad)
            hh = ch * rnd.between(0.42, 1.0)
            ww = cw * rnd.between(0.55, 1.0)
            stroke = SIGNAL if i == accent else c["line"]
            out.append(
                f'<rect x="{x:.0f}" y="{y + ch - hh:.0f}" width="{ww:.0f}" height="{hh:.0f}" '
                f'rx="{min(ww, hh) * 0.06:.0f}" fill="none" stroke="{stroke}" stroke-width="3"/>'
            )
    return "\n".join(out)


def subject_stage(w, h, c, rnd):
    """A row of machines standing at a stage, seen from across the road."""
    horizon = h * 0.56
    out = [ridge(w, h, horizon, c, rnd)]
    out.append(f'<rect x="0" y="{horizon:.0f}" width="{w}" height="{h - horizon:.0f}" fill="{c["band"]}"/>')
    n = 7
    accent = int(rnd.between(1, n - 1))
    for i in range(n):
        x = w * (0.06 + i * (0.88 / n))
        bh = (h - horizon) * rnd.between(0.34, 0.46)
        bw = w * 0.075
        y = horizon + (h - horizon) * 0.62
        col = SIGNAL if i == accent else c["bright"]
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{bw * 0.22:.0f}" fill="none" stroke="{col}" stroke-width="4"/>')
        out.append(f'<circle cx="{x + bw:.0f}" cy="{y:.0f}" r="{bw * 0.22:.0f}" fill="none" stroke="{col}" stroke-width="4"/>')
        out.append(
            f'<path d="M{x:.0f} {y:.0f} L{x + bw * 0.34:.0f} {y - bh * 0.42:.0f} '
            f'L{x + bw * 0.80:.0f} {y - bh * 0.42:.0f} L{x + bw:.0f} {y:.0f}" '
            f'stroke="{col}" stroke-width="4" fill="none" stroke-linejoin="round"/>'
        )
    return "\n".join(out)


def subject_workshop(w, h, c, rnd):
    """Bench, stand and tools laid out in order."""
    out = [f'<rect x="0" y="{h * 0.42:.0f}" width="{w}" height="{h * 0.58:.0f}" fill="{c["band"]}"/>']
    bench = h * 0.62
    out.append(f'<path d="M0 {bench:.0f} L{w} {bench:.0f}" stroke="{c["line"]}" stroke-width="5"/>')
    # Machine on a stand.
    bx, by, bw = w * 0.16, bench - h * 0.02, w * 0.34
    out.append(f'<circle cx="{bx:.0f}" cy="{by:.0f}" r="{bw * 0.16:.0f}" fill="none" stroke="{c["bright"]}" stroke-width="5"/>')
    out.append(f'<circle cx="{bx + bw:.0f}" cy="{by:.0f}" r="{bw * 0.16:.0f}" fill="none" stroke="{c["bright"]}" stroke-width="5"/>')
    out.append(
        f'<path d="M{bx:.0f} {by:.0f} L{bx + bw * 0.32:.0f} {by - bw * 0.26:.0f} '
        f'L{bx + bw * 0.74:.0f} {by - bw * 0.26:.0f} L{bx + bw:.0f} {by:.0f}" '
        f'stroke="{c["bright"]}" stroke-width="5" fill="none" stroke-linejoin="round"/>'
    )
    out.append(
        f'<path d="M{bx + bw * 0.52:.0f} {by:.0f} L{bx + bw * 0.40:.0f} {by + h * 0.10:.0f} '
        f'L{bx + bw * 0.70:.0f} {by + h * 0.10:.0f} Z" fill="{SIGNAL}"/>'
    )
    # Tools in a row on the bench.
    for i in range(6):
        x = w * (0.62 + i * 0.055)
        ln = h * rnd.between(0.10, 0.20)
        out.append(f'<path d="M{x:.0f} {bench - ln:.0f} L{x:.0f} {bench:.0f}" stroke="{c["line"]}" stroke-width="6" stroke-linecap="round"/>')
    return "\n".join(out)


def subject_diagram(w, h, c, rnd):
    """
    Schematic side view with numbered callouts. This one is not a stand-in for a
    photograph: it is the technical-manual illustration the Maintain feature
    calls for, so it stays as artwork even after real photography arrives.
    """
    out = []
    cy = h * 0.60
    wheel = h * 0.20
    front = w * 0.30
    rear = w * 0.72
    out.append(f'<circle cx="{front:.0f}" cy="{cy:.0f}" r="{wheel:.0f}" fill="none" stroke="{c["bright"]}" stroke-width="5"/>')
    out.append(f'<circle cx="{rear:.0f}" cy="{cy:.0f}" r="{wheel:.0f}" fill="none" stroke="{c["bright"]}" stroke-width="5"/>')
    out.append(f'<circle cx="{front:.0f}" cy="{cy:.0f}" r="{wheel * 0.34:.0f}" fill="none" stroke="{c["line"]}" stroke-width="3"/>')
    out.append(f'<circle cx="{rear:.0f}" cy="{cy:.0f}" r="{wheel * 0.42:.0f}" fill="none" stroke="{c["line"]}" stroke-width="3"/>')
    # Frame, forks, tank, seat.
    out.append(
        f'<path d="M{front:.0f} {cy:.0f} L{front + w * 0.045:.0f} {cy - h * 0.30:.0f} '
        f'L{w * 0.46:.0f} {cy - h * 0.26:.0f} L{rear:.0f} {cy:.0f} '
        f'M{w * 0.46:.0f} {cy - h * 0.26:.0f} L{w * 0.50:.0f} {cy:.0f} L{rear:.0f} {cy:.0f}" '
        f'stroke="{c["bright"]}" stroke-width="5" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
    )
    out.append(
        f'<path d="M{w * 0.40:.0f} {cy - h * 0.30:.0f} L{w * 0.58:.0f} {cy - h * 0.32:.0f} '
        f'L{w * 0.62:.0f} {cy - h * 0.24:.0f} L{w * 0.42:.0f} {cy - h * 0.23:.0f} Z" '
        f'stroke="{c["line"]}" stroke-width="4" fill="none" stroke-linejoin="round"/>'
    )
    # Chain run between the two wheel centres.
    out.append(
        f'<path d="M{front + wheel * 0.34:.0f} {cy + h * 0.02:.0f} L{rear - wheel * 0.42:.0f} {cy + h * 0.02:.0f}" '
        f'stroke="{SIGNAL}" stroke-width="4" stroke-dasharray="10 7" fill="none"/>'
    )
    # Six numbered callouts on leader lines.
    points = [
        (rear - wheel * 0.10, cy + h * 0.04, w * 0.86, h * 0.86, "01"),
        (w * 0.50, cy - h * 0.28, w * 0.56, h * 0.13, "02"),
        (front, cy + wheel * 0.72, w * 0.14, h * 0.88, "03"),
        (front, cy, w * 0.10, h * 0.34, "04"),
        (rear - w * 0.03, cy - h * 0.20, w * 0.88, h * 0.24, "05"),
        (w * 0.54, cy - h * 0.02, w * 0.50, h * 0.90, "06"),
    ]
    for x1, y1, x2, y2, n in points:
        out.append(f'<path d="M{x1:.0f} {y1:.0f} L{x2:.0f} {y2:.0f}" stroke="{c["line"]}" stroke-width="2"/>')
        out.append(f'<circle cx="{x2:.0f}" cy="{y2:.0f}" r="{h * 0.038:.0f}" fill="{c["ground"]}" stroke="{SIGNAL}" stroke-width="2.5"/>')
        out.append(
            f'<text x="{x2:.0f}" y="{y2 + h * 0.014:.0f}" text-anchor="middle" font-family="{MONO}" '
            f'font-size="{h * 0.038:.0f}" fill="{c["bright"]}" letter-spacing="1">{n}</text>'
        )
    return "\n".join(out)


def subject_og(w, h, c, rnd):
    out = [subject_highway(w, h, c, rnd)]
    out.append(f'<rect x="0" y="0" width="{w}" height="{h}" fill="{c["ground"]}" opacity="0.55"/>')
    for i, row in enumerate(["FRON", "TIER", "MOTO"]):
        out.append(
            f'<text x="{w * 0.07:.0f}" y="{h * (0.34 + 0.15 * i):.0f}" font-family="{MONO}" '
            f'font-size="{h * 0.115:.0f}" letter-spacing="{h * 0.052:.0f}" '
            f'fill="{c["bright"]}">{row}</text>'
        )
    return "\n".join(out)


SUBJECTS = {
    "highway": subject_highway,
    "descent": subject_descent,
    "roadside": subject_roadside,
    "chain": subject_chain,
    "gear": subject_gear,
    "stage": subject_stage,
    "workshop": subject_workshop,
    "diagram": subject_diagram,
    "og": subject_og,
}


def ridge(w, h, horizon, c, rnd):
    """A ridge line along the horizon. Every plate that has sky gets one."""
    pts = []
    x = 0.0
    y = horizon
    while x <= w:
        pts.append(f"{x:.0f} {y:.0f}")
        x += w / 14
        y = horizon - h * rnd.between(0.00, 0.09)
    body = " L".join(pts)
    return (
        f'<path d="M0 0 L{w} 0 L{w} {horizon:.0f} L0 {horizon:.0f} Z" fill="{c["ground"]}"/>'
        f'<path d="M{body} L{w} {horizon:.0f} L0 {horizon:.0f} Z" '
        f'fill="{c["band"]}" opacity="0.85"/>'
    )


# ---------------------------------------------------------------------------


def plate(slot):
    w, h = slot["w"], slot["h"]
    c = DARK if slot["tone"] == "dark" else LIGHT
    rnd = Seed(slot["id"])
    rail = max(34, int(h * 0.055))
    art_h = h - rail

    grid_step = max(40, int(w / 24))
    parts = [
        f'<rect width="{w}" height="{h}" fill="{c["ground"]}"/>',
        f'<g clip-path="url(#frame)">',
        SUBJECTS[slot["subject"]](w, art_h, c, rnd),
        "</g>",
        # Technical grid over the artwork, faint enough to read as texture.
        f'<g opacity="0.5">',
    ]
    x = grid_step
    while x < w:
        parts.append(f'<path d="M{x} 0 L{x} {art_h}" stroke="{c["grid"]}" stroke-width="1"/>')
        x += grid_step
    y = grid_step
    while y < art_h:
        parts.append(f'<path d="M0 {y} L{w} {y}" stroke="{c["grid"]}" stroke-width="1"/>')
        y += grid_step
    parts.append("</g>")

    # Crop marks, one per corner, sitting just inside the frame.
    m = max(16, int(w * 0.014))
    inset = max(12, int(w * 0.012))
    for cx, cy, dx, dy in (
        (inset, inset, 1, 1),
        (w - inset, inset, -1, 1),
        (inset, art_h - inset, 1, -1),
        (w - inset, art_h - inset, -1, -1),
    ):
        parts.append(
            f'<path d="M{cx} {cy + dy * m} L{cx} {cy} L{cx + dx * m} {cy}" '
            f'stroke="{c["bright"]}" stroke-width="2.5" fill="none" opacity="0.8"/>'
        )

    # Caption rail: what the photograph would show, and the slot reference.
    fs = max(13, int(rail * 0.40))
    parts.append(f'<rect x="0" y="{art_h}" width="{w}" height="{rail}" fill="{c["band"]}"/>')
    parts.append(f'<path d="M0 {art_h}.5 L{w} {art_h}.5" stroke="{c["line"]}" stroke-width="1"/>')
    parts.append(f'<rect x="0" y="{art_h}" width="{max(4, int(w * 0.004))}" height="{rail}" fill="{SIGNAL}"/>')
    parts.append(
        f'<text x="{inset + m}" y="{art_h + rail * 0.64:.0f}" font-family="{MONO}" font-size="{fs}" '
        f'letter-spacing="{fs * 0.14:.1f}" fill="{c["bright"]}">{esc(slot["caption"].upper())}</text>'
    )
    parts.append(
        f'<text x="{w - inset - m}" y="{art_h + rail * 0.64:.0f}" text-anchor="end" font-family="{MONO}" '
        f'font-size="{fs}" letter-spacing="{fs * 0.14:.1f}" fill="{c["ink"]}">'
        f'{esc(slot["id"].upper())} / {w}x{h} / PLATE</text>'
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'preserveAspectRatio="xMidYMid slice" role="img">'
        f'<defs><clipPath id="frame"><rect width="{w}" height="{art_h}"/></clipPath></defs>'
        + "".join(parts)
        + "</svg>"
    )


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def main():
    data = json.loads((CONTENT / "images.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)

    # Slots carrying a `source` are photographs built by build_photos.py. Drawing
    # a plate over one of those would quietly replace a picture with a grey box,
    # so this only renders the artwork slots that nothing else produces.
    artwork = [s for s in data["slots"] if not s.get("source")]
    photos = len(data["slots"]) - len(artwork)

    for slot in artwork:
        (OUT / f'{slot["id"]}.svg').write_text(plate(slot), encoding="utf-8")

    print(f"images: wrote {len(artwork)} plate(s) to docs/assets/img/")
    if photos:
        print(f"images: skipped {photos} photographic slot(s), see build_photos.py")
    print("images: MANIFEST.md is written by build_photos.py")


if __name__ == "__main__":
    main()

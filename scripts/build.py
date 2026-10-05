"""
Frontier Moto site build.

Renders content/*.json through the components and page modules into committed
static HTML under docs/. The published output is plain HTML with no runtime
dependency, which is the same arrangement beben.design uses for its generated
blog and tool pages. Nothing here runs in a browser.

Run:  python scripts/build.py
"""

import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "pages"))

import shell  # noqa: E402
import article as article_page  # noqa: E402
import home as home_page  # noqa: E402
import market as market_page  # noqa: E402
import recovery as recovery_page  # noqa: E402
import section as section_page  # noqa: E402
import shop as shop_page  # noqa: E402
import simple as simple_pages  # noqa: E402
import workshop as workshop_page  # noqa: E402

CONTENT = ROOT / "content"
DOCS = ROOT / "docs"


def load():
    names = ["site", "sections", "articles", "checklists", "technical", "market", "shop", "workshop", "images"]
    return {n: json.loads((CONTENT / f"{n}.json").read_text(encoding="utf-8")) for n in names}


def write(path, text):
    target = DOCS / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target


# ── Static support files ─────────────────────────────────────────────────────

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
<rect width="32" height="32" fill="#121212"/>
<rect x="4" y="6" width="24" height="3.5" fill="#F2EFE9"/>
<rect x="4" y="14.25" width="24" height="3.5" fill="#F2EFE9"/>
<rect x="4" y="22.5" width="24" height="3.5" fill="#EED202"/>
</svg>
"""


def favicon_ico():
    """
    A 32x32 .ico of the same three bar mark. Browsers that do not take an SVG
    icon request /favicon.ico by name, so without this every first page load
    logs a 404. Written by hand rather than with a library, since the whole
    project has no dependencies: a single uncompressed 32 bit BGRA image.
    """
    import struct

    size = 32
    ink, bone, signal = (0x12, 0x12, 0x12), (0xF2, 0xEF, 0xE9), (0xEE, 0xD2, 0x02)
    bars = [(6, 10, bone), (14, 18, bone), (22, 26, signal)]

    rows = []
    for y in range(size):
        row = bytearray()
        colour = ink
        for start, end, c in bars:
            if start <= y < end:
                colour = c
        for x in range(size):
            r, g, b = colour if (4 <= x < 28 and colour is not ink) else ink
            row += bytes((b, g, r, 255))          # BGRA
        rows.append(bytes(row))

    pixels = b"".join(reversed(rows))             # DIB rows run bottom up
    and_mask = b"\x00" * (size * 4)               # fully opaque

    header = struct.pack("<IiiHHIIiiII", 40, size, size * 2, 1, 32, 0,
                         len(pixels), 0, 0, 0, 0)
    image = header + pixels + and_mask

    return (
        struct.pack("<HHH", 0, 1, 1)
        + struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(image), 22)
        + image
    )


def manifest(site):
    # Paths are relative to the manifest, not absolute, so the site still works
    # when GitHub Pages serves it from a project sub-path rather than a domain
    # root. An absolute "/" start_url would leave the sub-path entirely.
    return json.dumps({
        "name": site["brand"]["name"],
        "short_name": "Frontier",
        "description": site["brand"]["tagline"],
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "background_color": "#F2EFE9",
        "theme_color": site["site"]["theme_color"],
        "icons": [
            {"src": "./favicon.svg", "sizes": "any", "type": "image/svg+xml"},
            {"src": "./favicon.ico", "sizes": "32x32", "type": "image/x-icon"},
        ],
    }, indent=2) + "\n"


def robots(site):
    base = site["site"]["base_url"].rstrip("/")
    return f"""User-agent: *
Allow: /

Sitemap: {base}/sitemap.xml
"""


def sitemap(site, pages):
    base = site["site"]["base_url"].rstrip("/")
    entries = []
    for page in pages:
        if page.get("noindex"):
            continue
        priority = "1.0" if page["href"] == "/" else "0.8"
        entries.append(
            "  <url>\n"
            f"    <loc>{base}{page['href']}</loc>\n"
            "    <lastmod>2026-08-24</lastmod>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )


def organization_schema(site):
    """
    Organization only. Not LocalBusiness, which would need a real street address,
    and not a service with hours or a telephone, because neither exists yet.
    """
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": site["brand"]["name"],
        "url": site["site"]["base_url"],
        "logo": site["site"]["base_url"].rstrip("/") + "/favicon.svg",
        "description": site["brand"]["mission"],
        "email": site["brand"]["email"],
        "areaServed": [
            {"@type": "Country", "name": n}
            for n in ["Kenya", "Uganda", "Tanzania", "Rwanda"]
        ],
        "knowsAbout": [
            "Motorcycle maintenance",
            "Motorcycle road safety",
            "Route planning",
            "Roadside repair",
            "Riding equipment",
        ],
    }


# ── Build ────────────────────────────────────────────────────────────────────

def main():
    data = load()
    site = data["site"]
    built = []

    # Home
    meta = dict(home_page.PAGE)
    meta["schema"] = organization_schema(site)
    body = home_page.build(data)
    write(meta["out"], shell.render(site, meta, meta["depth"], body))
    built.append(meta)

    # The shared section pages, except Market which has its own marketplace
    # builder. Survive keeps its generic section page even though it no longer
    # sits in the primary nav.
    for page in data["sections"]["pages"]:
        if page["slug"] == "market":
            continue
        meta = section_page.page_meta(page, site)
        body = section_page.build(page, data)
        write(meta["out"], shell.render(site, meta, meta["depth"], body))
        built.append(meta)

    # Market and Shop: dedicated commerce builders
    for module in (market_page, shop_page):
        meta = module.page_meta(site, data)
        body = module.build(data)
        write(meta["out"], shell.render(site, meta, meta["depth"], body))
        built.append(meta)

    # Workshop and Recovery
    for module, builder in ((workshop_page, workshop_page.build), (recovery_page, recovery_page.build)):
        meta = module.page_meta(site, data)
        body = builder(data)
        write(meta["out"], shell.render(site, meta, meta["depth"], body))
        built.append(meta)

    # Article detail pages
    for art in data["articles"]["articles"]:
        if not art.get("slug"):
            continue
        meta = article_page.page_meta(art, site)
        body = article_page.build(art, data)
        write(meta["out"], shell.render(site, meta, meta["depth"], body))
        built.append(meta)

    # Legal and 404
    meta = simple_pages.legal_meta(site)
    write(meta["out"], shell.render(site, meta, meta["depth"], simple_pages.legal(data)))
    built.append(meta)

    meta = simple_pages.not_found_meta(site)
    write(meta["out"], shell.render(site, meta, meta["depth"], simple_pages.not_found(data)))
    built.append(meta)

    # Support files
    write("favicon.svg", FAVICON)
    (DOCS / "favicon.ico").write_bytes(favicon_ico())
    write("site.webmanifest", manifest(site))
    write("robots.txt", robots(site))
    write("sitemap.xml", sitemap(site, built))

    indexed = [p for p in built if not p.get("noindex")]
    print(f"build: {len(built)} pages written to docs/ ({len(indexed)} in the sitemap)")
    for page in built:
        print(f"  {page['href']:<34} {page['out']}")


if __name__ == "__main__":
    main()

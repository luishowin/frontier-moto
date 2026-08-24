"""
Frontier Moto build check.

The project has no framework and therefore no framework to catch mistakes, so
this is the check. It walks every generated page and asserts the things that
actually break a static site: dead internal links, images without dimensions or
alt text, missing or duplicated metadata, malformed JSON-LD, skipped heading
levels, and the house copy rule against em dashes.

Exits non-zero on any failure, so it works as a pre-commit or CI step.

Run:  python scripts/check.py
"""

import html.parser
import json
import pathlib
import re
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
CONTENT = ROOT / "content"

FAILURES = []
CHECKED = {"pages": 0, "links": 0, "images": 0}


def fail(page, message):
    FAILURES.append(f"{page}: {message}")


class PageParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.images = []
        self.headings = []
        self.title = None
        self.meta = {}
        self.ld = []
        self.labelled = []
        self.ids = []
        self.forms = 0
        self.pictures = 0
        self.sources = 0
        self.bad_sources = []
        self._in_title = False
        self._in_ld = False
        self._ld_buf = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)

        if a.get("id"):
            self.ids.append(a["id"])

        if tag == "title":
            self._in_title = True
        elif tag == "a" and "href" in a:
            self.links.append(a["href"])
        elif tag == "link" and a.get("rel") in ("stylesheet", "icon", "manifest", "canonical", "preload"):
            self.links.append(a.get("href", ""))
            self.links.extend(candidates(a.get("imagesrcset", "")))
        elif tag == "source":
            self.sources += 1
            if not a.get("srcset"):
                self.bad_sources.append("<source> without a srcset")
            self.links.extend(candidates(a.get("srcset", "")))
        elif tag == "script" and a.get("src"):
            self.links.append(a["src"])
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld = True
            self._ld_buf = ""
        elif tag == "img":
            self.images.append(a)
            if a.get("src"):
                self.links.append(a["src"])
            self.links.extend(candidates(a.get("srcset", "")))
        elif tag == "picture":
            self.pictures += 1
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append(int(tag[1]))
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.meta[key] = a.get("content", "")
        elif tag == "form":
            self.forms += 1

        for key in ("aria-labelledby", "for"):
            if a.get(key):
                self.labelled.extend(a[key].split())

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_ld:
            self._in_ld = False
            self.ld.append(self._ld_buf)

    def handle_data(self, data):
        if self._in_title:
            self.title = (self.title or "") + data
        if self._in_ld:
            self._ld_buf += data


def candidates(srcset):
    """The URLs out of a srcset or imagesrcset, dropping the w descriptors."""
    out = []
    for part in srcset.split(","):
        part = part.strip()
        if part:
            out.append(part.split()[0])
    return out


def resolve(page_path, href):
    """Turn an href on a page into the file it should reach, or None if external."""
    if href.startswith(("http://", "https://", "mailto:", "tel:", "data:", "//")):
        return None
    href = href.split("#")[0].split("?")[0]
    if not href:
        return None

    target = (page_path.parent / href).resolve()
    if target.is_dir() or href.endswith("/"):
        target = target / "index.html"
    return target


def check_page(path, seen_titles, seen_descriptions):
    rel_name = path.relative_to(DOCS).as_posix()
    source = path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(source)
    CHECKED["pages"] += 1

    # ── Metadata ─────────────────────────────────────────────────────────────
    if not parser.title or not parser.title.strip():
        fail(rel_name, "no <title>")
    else:
        title = parser.title.strip()
        if title in seen_titles:
            fail(rel_name, f"duplicate title, also used by {seen_titles[title]}")
        seen_titles[title] = rel_name

    description = parser.meta.get("description", "").strip()
    if not description:
        fail(rel_name, "no meta description")
    elif len(description) > 300:
        fail(rel_name, f"meta description is {len(description)} characters, over 300")
    elif description in seen_descriptions:
        fail(rel_name, f"duplicate meta description, also used by {seen_descriptions[description]}")
    else:
        seen_descriptions[description] = rel_name

    for required in ("og:title", "og:description", "og:image", "og:url",
                     "twitter:card", "twitter:title", "twitter:image"):
        if not parser.meta.get(required):
            fail(rel_name, f"missing {required}")

    if 'rel="canonical"' not in source:
        fail(rel_name, "no canonical link")

    # ── JSON-LD ──────────────────────────────────────────────────────────────
    for i, blob in enumerate(parser.ld):
        try:
            json.loads(blob)
        except json.JSONDecodeError as err:
            fail(rel_name, f"JSON-LD block {i + 1} does not parse: {err}")

    # ── Headings ─────────────────────────────────────────────────────────────
    h1s = parser.headings.count(1)
    if h1s != 1:
        fail(rel_name, f"expected exactly one h1, found {h1s}")

    previous = 0
    for level in parser.headings:
        if previous and level > previous + 1:
            fail(rel_name, f"heading level jumps from h{previous} to h{level}")
            break
        previous = level

    # ── Images ───────────────────────────────────────────────────────────────
    for img in parser.images:
        CHECKED["images"] += 1
        src = img.get("src", "(no src)")
        if "alt" not in img:
            fail(rel_name, f"image without an alt attribute: {src}")
        elif not img["alt"].strip() and "decorative" not in img.get("class", ""):
            fail(rel_name, f"image with empty alt that is not marked decorative: {src}")
        if not img.get("width") or not img.get("height"):
            fail(rel_name, f"image without explicit width and height: {src}")

    # ── Responsive images ────────────────────────────────────────────────────
    # A <picture> with no <img> renders nothing at all in every browser, and a
    # <source> is only ever a fallback away from being invisible, so a missing
    # file behind a srcset never shows up as a broken image on the page.
    for problem in parser.bad_sources:
        fail(rel_name, problem)
    if parser.sources and not parser.pictures:
        fail(rel_name, f"{parser.sources} <source> element(s) outside any <picture>")
    if parser.pictures > len([i for i in parser.images if i.get("srcset")]):
        fail(rel_name, "a <picture> has no <img> fallback inside it")

    # ── Links ────────────────────────────────────────────────────────────────
    for href in parser.links:
        target = resolve(path, href)
        if target is None:
            continue
        CHECKED["links"] += 1
        if not target.exists():
            fail(rel_name, f"link goes nowhere: {href}")

    # ── In-page anchors ──────────────────────────────────────────────────────
    for href in parser.links:
        if not href.startswith("#") or href == "#":
            continue
        if href[1:] not in parser.ids:
            fail(rel_name, f"anchor has no matching id on this page: {href}")

    # ── Labelled regions and form controls ───────────────────────────────────
    for ident in set(parser.labelled):
        if ident not in parser.ids:
            fail(rel_name, f"aria-labelledby or label points at a missing id: {ident}")

    # ── Copy rule ────────────────────────────────────────────────────────────
    if "—" in source:
        fail(rel_name, "contains an em dash")

    return parser


def check_content_sources():
    for path in sorted(CONTENT.glob("*.json")):
        text = path.read_text(encoding="utf-8")
        if "—" in text:
            fail(f"content/{path.name}", "contains an em dash")
        try:
            json.loads(text)
        except json.JSONDecodeError as err:
            fail(f"content/{path.name}", f"does not parse: {err}")


def check_support_files():
    for name in ("robots.txt", "sitemap.xml", "site.webmanifest", "favicon.svg", "404.html"):
        if not (DOCS / name).exists():
            fail("docs/", f"missing {name}")

    # docs/ is the site root, but base_url may carry a project sub-path when the
    # site is served from GitHub Pages rather than a domain root. Strip that
    # prefix before mapping a sitemap URL back to a file.
    base_url = json.loads((CONTENT / "site.json").read_text(encoding="utf-8"))["site"]["base_url"]
    prefix = urllib.parse.urlparse(base_url).path.rstrip("/")

    sitemap = (DOCS / "sitemap.xml").read_text(encoding="utf-8")
    for loc in re.findall(r"<loc>(.*?)</loc>", sitemap):
        route = urllib.parse.urlparse(loc).path
        if prefix and not route.startswith(prefix + "/") and route != prefix:
            fail("sitemap.xml", f"URL is outside the site base path: {route}")
            continue
        route = route[len(prefix):] or "/"

        target = DOCS / route.lstrip("/")
        if route.endswith("/"):
            target = target / "index.html"
        if not target.exists():
            fail("sitemap.xml", f"lists a URL with no page behind it: {route}")

    manifest = json.loads((DOCS / "site.webmanifest").read_text(encoding="utf-8"))
    if not manifest.get("name"):
        fail("site.webmanifest", "has no name")


def check_recovery_honesty():
    """
    The one content assertion worth automating. Recovery must never imply a live
    dispatch service, and every form must carry its demonstration notice.
    """
    recovery = (DOCS / "recovery" / "index.html").read_text(encoding="utf-8")
    if "not live" not in recovery.lower() and "not an emergency service" not in recovery.lower():
        fail("recovery/index.html", "no statement that dispatch is not live")

    for path in sorted(DOCS.rglob("index.html")) + [DOCS / "404.html"]:
        source = path.read_text(encoding="utf-8")
        forms = source.count("<form")
        demos = source.count("data-demo-form")
        if forms != demos:
            fail(
                path.relative_to(DOCS).as_posix(),
                f"{forms} form(s) but {demos} marked as demonstrations",
            )


def main():
    if not DOCS.exists():
        print("check: docs/ does not exist, run build.py first")
        return 1

    pages = sorted(list(DOCS.rglob("*.html")))
    if not pages:
        print("check: no pages found in docs/")
        return 1

    seen_titles, seen_descriptions = {}, {}
    for path in pages:
        check_page(path, seen_titles, seen_descriptions)

    check_content_sources()
    check_support_files()
    check_recovery_honesty()

    print(
        f"check: {CHECKED['pages']} pages, {CHECKED['links']} internal links, "
        f"{CHECKED['images']} images"
    )

    if FAILURES:
        print(f"\n{len(FAILURES)} problem(s):\n")
        for line in FAILURES:
            print(f"  {line}")
        return 1

    print("check: all passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

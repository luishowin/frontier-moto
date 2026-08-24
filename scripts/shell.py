"""
The page shell: head, header, menu overlay and footer.

Every page is rendered through here, which is the reason this project generates
its HTML instead of hand-copying it. The house sites repeat the header and
footer markup in every file, and the nanyuki-holiday-home README already names
that as the maintenance problem it is. Generating the shell keeps the published
output identical in kind (plain static HTML, no runtime dependency) while there
is only one copy of the nav to edit.

Relative links are computed from page depth, so the site works unchanged from a
GitHub Pages project sub-path.
"""

import json

from components import esc, mono_label


def rel(href, depth):
    """Turn a root relative href into one relative to a page at `depth`."""
    if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
        return href
    up = "../" * depth
    if href == "/":
        return up if depth else "./"
    body = href.lstrip("/")
    if "#" in body and body.startswith("#"):
        return body
    return (up if depth else "") + body


# Bumped whenever index.css or index.js changes. GitHub Pages serves static
# assets with a long cache life and there is no build step to hash filenames,
# so without this a deploy can leave readers on the previous stylesheet. The
# house sites use the same query string approach.
ASSET_VERSION = "6"


BEACON = (
    '<svg class="recovery-action__beacon" width="13" height="13" viewBox="0 0 16 16" '
    'aria-hidden="true" focusable="false">'
    '<path d="M8 0.6 15.4 14H0.6L8 0.6Zm0 4.6L4.6 11.6h6.8L8 5.2Z"/>'
    '<path d="M7.1 6.9h1.8v2.4H7.1V6.9Zm0 3.1h1.8v1.1H7.1V10Z"/>'
    "</svg>"
)

SUN = (
    '<svg class="theme-toggle__sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.7" stroke-linecap="round" aria-hidden="true" focusable="false">'
    '<circle cx="12" cy="12" r="4.2"/><path d="M12 2v2.6M12 19.4V22M2 12h2.6M19.4 12H22'
    'M4.9 4.9l1.9 1.9M17.2 17.2l1.9 1.9M19.1 4.9l-1.9 1.9M6.8 17.2l-1.9 1.9"/></svg>'
)

MOON = (
    '<svg class="theme-toggle__moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" '
    'focusable="false"><path d="M20.5 14.6A8.6 8.6 0 0 1 9.4 3.5a8.6 8.6 0 1 0 11.1 11.1Z"/></svg>'
)

# Applied before first paint so the page never flashes the wrong palette.
THEME_BOOT = (
    "<script>(function(){try{var t=localStorage.getItem('frontier-theme');"
    "if(!t){t=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}"
    "document.documentElement.setAttribute('data-theme',t);}"
    "catch(e){document.documentElement.setAttribute('data-theme','light');}})();</script>"
)


def wordmark(site, depth, tag="a"):
    """FrontierWordmark. Three stacked four character rows."""
    rows = "".join(f"<span>{esc(r)}</span>" for r in site["brand"]["wordmark"])
    if tag == "a":
        return (
            f'<a class="wordmark" href="{rel("/", depth)}" '
            f'aria-label="{esc(site["brand"]["name"])}, home">{rows}</a>'
        )
    return f'<span class="wordmark" aria-hidden="true">{rows}</span>'


def recovery_action(site, depth, extra=""):
    """RecoveryAction. Present at every width, never inside the menu."""
    r = site["recovery"]
    cls = "recovery-action" + (f" {extra}" if extra else "")
    return (
        f'<a class="{cls}" href="{rel(r["href"], depth)}">'
        f"{BEACON}"
        f'<span class="recovery-action__text">{esc(r["short"])}</span>'
        f'<span class="recovery-action__short">{esc(r["label"])}</span>'
        "</a>"
    )


def head(site, page, depth):
    """
    Document head. Unique title and description, canonical, Open Graph,
    Twitter and JSON-LD on every page.
    """
    base = site["site"]["base_url"].rstrip("/")
    canonical = base + page["href"]
    og_image = base + site["site"]["og_image"]
    title = f'{page["title"]} | {site["brand"]["name"]}' if page["href"] != "/" else page["title"]

    schema = json.dumps(page["schema"], indent=2, ensure_ascii=False) if page.get("schema") else None

    parts = [
        '<!DOCTYPE html>',
        f'<html lang="{site["site"]["lang"]}">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        '<meta name="color-scheme" content="light dark">',
        f'<meta name="theme-color" content="{site["site"]["theme_color"]}">',
        "",
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(page["description"])}">',
        f'<link rel="canonical" href="{canonical}">',
        "",
        f'<meta property="og:type" content="{page.get("og_type", "website")}">',
        f'<meta property="og:site_name" content="{esc(site["brand"]["name"])}">',
        f'<meta property="og:locale" content="{site["site"]["locale"]}">',
        f'<meta property="og:url" content="{canonical}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(page["description"])}">',
        f'<meta property="og:image" content="{og_image}">',
        f'<meta property="og:image:alt" content="{esc(site["brand"]["name"])}">',
        "",
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:description" content="{esc(page["description"])}">',
        f'<meta name="twitter:image" content="{og_image}">',
        "",
        # Two families only. Archivo carries display and body, Roboto Mono carries
        # the wordmark, labels and every technical figure.
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        "family=Archivo:wght@400;500;600;700&family=Roboto+Mono:wght@400;500;700&display=swap\">",
        "",
        f'<link rel="stylesheet" href="{rel("/assets/css/index.css", depth)}?v={ASSET_VERSION}">',
        f'<link rel="icon" href="{rel("/favicon.ico", depth)}" sizes="32x32">',
        f'<link rel="icon" href="{rel("/favicon.svg", depth)}" type="image/svg+xml">',
        f'<link rel="manifest" href="{rel("/site.webmanifest", depth)}">',
    ]

    if page.get("noindex"):
        parts.append('<meta name="robots" content="noindex, follow">')

    if page.get("preload_image"):
        parts.append(
            f'<link rel="preload" as="image" href="{rel(page["preload_image"], depth)}" fetchpriority="high">'
        )

    if schema:
        parts += ["", f'<script type="application/ld+json">\n{schema}\n</script>']

    parts += ["", THEME_BOOT, "</head>"]
    return "\n".join(parts)


def header(site, page, depth):
    """SiteHeader with PrimaryNav and RecoveryAction."""
    over = ' data-over="dark"' if page.get("dark_hero") else ""

    links = []
    for item in site["nav"]:
        current = ' aria-current="page"' if item["slug"] == page.get("slug") else ""
        links.append(
            f'<li><a class="primary-nav__link" href="{rel(item["href"], depth)}"{current}>'
            f'{esc(item["label"])}</a></li>'
        )

    return f"""<a class="skip-link" href="#main">Skip to content</a>
<div id="header-sentinel" aria-hidden="true"></div>

<header class="site-header"{over}>
  <div class="site-header__inner">
    {wordmark(site, depth)}
    <nav class="primary-nav" aria-label="Primary">
      <ul class="primary-nav__list">{"".join(links)}</ul>
    </nav>
    <div class="header__actions">
      <button class="theme-toggle" id="theme-toggle" type="button" aria-pressed="false"
              aria-label="Switch to dark theme">{SUN}{MOON}</button>
      {recovery_action(site, depth)}
      <button class="menu-trigger" id="menu-trigger" type="button" aria-expanded="false"
              aria-controls="menu-overlay" aria-label="Open menu"><span></span></button>
    </div>
  </div>
</header>"""


def overlay(site, page, depth):
    """The mobile menu. Recovery is repeated here for reach, not for discovery."""
    items = []
    for i, item in enumerate(site["nav"], start=1):
        current = ' aria-current="page"' if item["slug"] == page.get("slug") else ""
        items.append(
            f'<li><a href="{rel(item["href"], depth)}"{current}>'
            f'<span class="menu-overlay__n">{i:02d}</span>{esc(item["label"])}</a></li>'
        )

    return f"""<div class="menu-overlay" id="menu-overlay" role="dialog" aria-modal="true"
     aria-label="Site navigation">
  <div class="menu-overlay__top">
    {wordmark(site, depth, tag="span")}
    <button class="menu-overlay__close" type="button" data-menu-close
            aria-label="Close menu">&#215;</button>
  </div>
  <nav class="menu-overlay__nav" aria-label="Site">
    <ul>{"".join(items)}</ul>
  </nav>
  <div class="menu-overlay__foot">
    {recovery_action(site, depth)}
    <p class="menu-overlay__note">{esc(site["recovery"]["note"])}. Recovery is not an
    emergency service. If anyone is hurt, contact local emergency services first.</p>
  </div>
</div>"""


def footer(site, depth):
    """SiteFooter."""
    f = site["footer"]

    cols = []
    for col in f["columns"]:
        links = "".join(
            f'<li><a href="{rel(l["href"], depth)}">{esc(l["label"])}</a></li>'
            for l in col["links"]
        )
        cols.append(
            f'<div><h2>{esc(col["title"])}</h2><ul class="site-footer__links">{links}</ul></div>'
        )

    legal = "".join(
        f'<a href="{rel(l["href"], depth)}">{esc(l["label"])}</a>' for l in f["legal"]
    )
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="site-footer__top">
      <div class="site-footer__brand">
        {wordmark(site, depth, tag="span")}
        <p class="site-footer__mission">{esc(site["brand"]["mission"])}</p>
      </div>
      {"".join(cols)}
      <div>
        <h2>Contact</h2>
        <p class="site-footer__contact">
          {esc(site["brand"]["region"])}<br>
          <a href="mailto:{esc(site["brand"]["email"])}">{esc(site["brand"]["email"])}</a>
        </p>
        <p class="site-footer__contact" style="margin-top:0.75rem">{esc(f["channels_note"])}</p>
        <div class="site-footer__cta">
          {recovery_action(site, depth)}
          <a class="btn btn--ghost-light" href="{rel("/workshop/", depth)}">
            <span class="btn__label">Workshop services</span></a>
        </div>
      </div>
    </div>
    <div class="site-footer__meta">
      <span>{esc(f["meta_left"])}</span>
      <nav class="site-footer__legal" aria-label="Legal">{legal}</nav>
      <span>{esc(f["meta_right"])}</span>
    </div>
  </div>
</footer>"""


def render(site, page, depth, body):
    """Assemble one complete document."""
    return "\n".join([
        head(site, page, depth),
        "<body>",
        header(site, page, depth),
        overlay(site, page, depth),
        '<main id="main">',
        body,
        "</main>",
        footer(site, depth),
        f'<script src="{rel("/assets/js/index.js", depth)}?v={ASSET_VERSION}" defer></script>',
        "</body>",
        "</html>",
        "",
    ])

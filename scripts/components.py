"""
Frontier Moto component library.

Each function here is one of the primitives the site is built from, and each
emits one canonical block of markup. Pages compose these; no page writes its
own version of a card, a spec list or a checklist.

Mapping to the component names used in the brief:

    SectionLabel        section_label
    EditorialHero       editorial_hero
    IndexCard           index_card
    FeatureStory        feature_story
    ArticleCard         article_card
    ArticleListRow      article_row
    TechnicalSpecList   spec_list
    Checklist           checklist  /  steps
    WorkshopCallout     workshop_callout
    RecoverSection      recover_section
    NewsletterForm      newsletter_form

    SiteHeader, FrontierWordmark, PrimaryNav, MarketAction, MoreMenu and
    SiteFooter live in shell.py, because they are part of every document rather
    than something a page chooses to place.
"""

import datetime
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMAGES = {
    slot["id"]: slot
    for slot in json.loads((ROOT / "content" / "images.json").read_text(encoding="utf-8"))["slots"]
}

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def esc(text):
    if text is None:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def fmt_date(iso):
    """2026-08-11 becomes 11 AUG 2026, which suits the mono label rail."""
    d = datetime.date.fromisoformat(iso)
    return f"{d.day:02d} {MONTHS[d.month - 1]} {d.year}"


def mono_label(text):
    return f'<span class="mono">{esc(text)}</span>'


def rel(href, depth):
    """Kept in step with shell.rel; duplicated to avoid a circular import."""
    if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
        return href
    up = "../" * depth
    if href == "/":
        return up if depth else "./"
    return (up if depth else "") + href.lstrip("/")


def srcset(slot, ext, depth):
    """
    A w-descriptor srcset across the widths build_photos.py actually produced.
    The widest file keeps the bare slot name so the fallback src is stable; the
    rest carry their width, which is also what makes them easy to spot on disk.
    """
    widths = slot.get("widths") or [slot["w"]]
    parts = []
    for w in widths:
        suffix = "" if w == widths[0] else "-%d" % w
        href = rel("/assets/img/%s%s.%s" % (slot["id"], suffix, ext), depth)
        parts.append("%s %dw" % (href, w))
    return ", ".join(parts)


def image(slot_id, depth, *, cls="", lazy=True, sizes=None, priority=False):
    """
    Every image carries real dimensions so nothing shifts as it loads, and the
    alt text comes from content/images.json rather than the page, because it
    describes the picture rather than the layout.

    Photographs ship as AVIF with a JPEG behind them. AVIF is roughly half the
    weight at the same quality, which is the difference that matters on a weak
    connection, and the JPEG in the <img> covers anything that cannot read it.
    Slots without a `source` are generated artwork and stay a single SVG.
    """
    slot = IMAGES[slot_id]
    attrs = [
        f'width="{slot["w"]}"',
        f'height="{slot["h"]}"',
        f'alt="{esc(slot["alt"])}"',
    ]
    if cls:
        attrs.append(f'class="{cls}"')
    if sizes:
        attrs.append(f'sizes="{sizes}"')
    if priority:
        attrs.append('fetchpriority="high"')
    attrs.append('decoding="async"')
    if lazy and not priority:
        attrs.append('loading="lazy"')

    if not slot.get("source"):
        src = rel("/assets/img/%s.svg" % slot_id, depth)
        return '<img src="%s" ' % src + " ".join(attrs) + ">"

    fallback = rel("/assets/img/%s.jpg" % slot_id, depth)
    img = (
        '<img src="%s" srcset="%s" ' % (fallback, srcset(slot, "jpg", depth))
        + " ".join(attrs) + ">"
    )
    sizes_attr = f' sizes="{sizes}"' if sizes else ""
    return (
        "<picture>"
        f'<source type="image/avif" srcset="{srcset(slot, "avif", depth)}"{sizes_attr}>'
        f"{img}</picture>"
    )


def preload_link(slot_id, depth, sizes="100vw"):
    """
    Preload the same AVIF candidate the <picture> will pick, not the JPEG, or
    the browser fetches the hero twice. A browser without AVIF ignores an
    unsupported type and simply loads the fallback in the normal course.
    """
    slot = IMAGES[slot_id]
    if not slot.get("source"):
        href = rel("/assets/img/%s.svg" % slot_id, depth)
        return '<link rel="preload" as="image" href="%s" fetchpriority="high">' % href
    return (
        '<link rel="preload" as="image" type="image/avif" '
        f'imagesrcset="{srcset(slot, "avif", depth)}" imagesizes="{sizes}" '
        'fetchpriority="high">'
    )


# ── SectionLabel ─────────────────────────────────────────────────────────────

def section_label(number, title, aside=None, heading_id=None):
    """
    This is the section's real heading, not a decorative rail. Rendering it as an
    h2 is what keeps the document from jumping straight from the page h1 to the
    h3 on every card, which is exactly what check.py caught when it was a <p>.
    """
    aside_html = f'<span class="section-label__aside">{esc(aside)}</span>' if aside else ""
    ident = f' id="{heading_id}"' if heading_id else ""
    return (
        f'<h2 class="section-label"{ident}>'
        f'<span class="section-label__n">{esc(number)}</span>'
        f'<span class="section-label__title">{esc(title)}</span>'
        f"{aside_html}</h2>"
    )


# ── EditorialHero ────────────────────────────────────────────────────────────

def editorial_hero(*, slot, depth, label=None, label_accent=None, title_lines, lede,
                   actions="", field=None, compact=False, flat=False):
    classes = "hero"
    if compact:
        classes += " hero--compact"
    if flat:
        classes += " hero--flat"

    lines = "".join(f"<span>{esc(l)}</span>" for l in title_lines)

    label_html = ""
    if label or label_accent:
        label_html = (
            '<p class="hero__label">'
            f"<b>{esc(label_accent)}</b> {esc(label)}</p>"
            if label_accent else
            f'<p class="hero__label">{esc(label)}</p>'
        )

    field_html = ""
    if field:
        cells = "".join(
            f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in field
        )
        field_html = f'<dl class="hero__field">{cells}</dl>'

    return f"""<section class="{classes}">
  <div class="hero__media">{image(slot, depth, priority=True, lazy=False, sizes="100vw")}</div>
  <div class="hero__scrim"></div>
  <div class="hero__inner">
    {label_html}
    <h1 class="hero__title">{lines}</h1>
    <p class="hero__lede">{esc(lede)}</p>
    {f'<div class="hero__actions btn-row">{actions}</div>' if actions else ""}
    {field_html}
  </div>
</section>"""


# ── IndexCard ────────────────────────────────────────────────────────────────

def index_card(entry, depth, href, i=0):
    """
    Deliberately not six identical cards. Size, media and treatment vary with
    the entry's own `size` field so the grid has a rhythm.
    """
    size = entry.get("size", "standard")
    classes = ["index-card"]
    if size == "wide":
        classes.append("index-card--wide")
    if size == "tall":
        classes.append("index-card--tall")
    if entry.get("image"):
        classes.append("index-card--media")
    if size == "signal":
        classes.append("index-card--signal")

    media = ""
    if entry.get("image"):
        media = f'<div class="index-card__media">{image(entry["image"], depth, sizes="(max-width: 720px) 100vw, 45vw")}</div>'

    stat = entry.get("stat")
    stat_html = ""
    if stat:
        stat_html = (
            f'<span class="index-card__stat">{esc(stat["k"])}<b>{esc(stat["v"])}</b></span>'
        )

    return f"""<article class="{" ".join(classes)}" data-reveal style="--i:{i}">
  {media}
  <p class="index-card__n">{esc(entry["number"])}</p>
  <h3 class="index-card__title"><a class="index-card__link" href="{rel(href, depth)}">{esc(entry["label"])}</a></h3>
  <p class="index-card__blurb">{esc(entry["blurb"])}</p>
  <p class="index-card__detail">{esc(entry["detail"])}</p>
  <div class="index-card__foot"><span>Open</span>{stat_html}</div>
</article>"""


# ── TechnicalSpecList ────────────────────────────────────────────────────────

def spec_list(pairs, single=False):
    cells = "".join(
        f'<div><dt>{esc(p["k"] if isinstance(p, dict) else p[0])}</dt>'
        f'<dd>{esc(p["v"] if isinstance(p, dict) else p[1])}</dd></div>'
        for p in pairs
    )
    cls = "spec-list spec-list--single" if single else "spec-list"
    return f'<dl class="{cls}">{cells}</dl>'


# ── FeatureStory ─────────────────────────────────────────────────────────────

def feature_story(article, depth, *, href):
    return f"""<article class="feature" data-reveal>
  <div class="feature__media">
    {image(article["image"], depth, sizes="(max-width: 960px) 100vw, 55vw")}
    <p class="feature__issue">{esc(article["issue"])}</p>
  </div>
  <div class="feature__body">
    <p class="feature__eyebrow">
      <span>{esc(article["category"])}</span>
      <span>{esc(article["location"])}</span>
      <span>{esc(fmt_date(article["date"]))}</span>
    </p>
    <h3 class="feature__title"><a href="{rel(href, depth)}">{esc(article["title"])}</a></h3>
    <p class="feature__dek">{esc(article["dek"])}</p>
    <p class="feature__note">{esc(article["excerpt"])}</p>
    {spec_list(article["specs"])}
    <p class="feature__actions">
      <span class="tlink">Read the story
        <span class="tlink__arrow" aria-hidden="true">&#8594;</span></span>
    </p>
  </div>
</article>"""


# ── ArticleCard and ArticleListRow ───────────────────────────────────────────

def _article_href(article, depth):
    if article.get("slug"):
        return rel(f'/field/{article["slug"]}/', depth)
    return None


def article_card(article, depth, i=0, with_media=True):
    href = _article_href(article, depth)
    media = ""
    if with_media and article.get("image"):
        media = f'<div class="article-card__media">{image(article["image"], depth, sizes="(max-width: 720px) 100vw, 30vw")}</div>'

    if href:
        title = f'<a href="{href}">{esc(article["title"])}</a>'
        tag = ""
    else:
        title = esc(article["title"])
        # The leading space matters: without it the title and the tag run
        # together when the markup is flattened to text or read aloud.
        tag = ' <span class="tag-upcoming">In preparation</span>'

    return f"""<article class="article-card" data-reveal style="--i:{i}">
  {media}
  <p class="article-card__meta">
    <span class="article-card__cat">{esc(article["category"])}</span>
    <span>{esc(fmt_date(article["date"]))}</span>
  </p>
  <h3 class="article-card__title">{title}{tag}</h3>
  <p class="article-card__excerpt">{esc(article["excerpt"])}</p>
  <p class="article-card__foot">{esc(article["read"])} read</p>
</article>"""


def article_row(article, depth, i=0):
    href = _article_href(article, depth)
    if href:
        title = f'<a href="{href}">{esc(article["title"])}</a>'
        tag = ""
    else:
        title = esc(article["title"])
        tag = ' <span class="tag-upcoming">In preparation</span>'

    return f"""<article class="article-row" data-reveal style="--i:{i}">
  <p class="article-row__cat">{esc(article["category"])}</p>
  <div>
    <h3 class="article-row__title">{title}{tag}</h3>
    <p class="article-row__excerpt">{esc(article["excerpt"])}</p>
  </div>
  <p class="article-row__meta">{esc(fmt_date(article["date"]))}<br>{esc(article["read"])}</p>
</article>"""


# ── Checklist and step sequence ──────────────────────────────────────────────

def checklist(data, i=0, href=None, depth=0):
    items = "".join(
        f'<li><span class="checklist__box" aria-hidden="true"></span>'
        f'<span><span class="checklist__label">{esc(item["label"])}</span>'
        f'<span class="checklist__detail">{esc(item["detail"])}</span></span></li>'
        for item in data["items"]
    )
    if href:
        title = (
            f'<a class="checklist__link" href="{rel(href, depth)}">'
            f'{esc(data["title"])}'
            '<span class="checklist__go" aria-hidden="true">&#8594;</span></a>'
        )
        cls = "checklist checklist--link"
    else:
        title = esc(data["title"])
        cls = "checklist"
    return f"""<section class="{cls}" data-reveal style="--i:{i}">
  <div class="checklist__head">
    <span class="checklist__n">{esc(data["number"])}</span>
    <h3 class="checklist__title">{title}</h3>
  </div>
  <p class="checklist__note">{esc(data["note"])}</p>
  <ul class="checklist__items">{items}</ul>
</section>"""


def steps(data):
    rows = "".join(
        f'<li class="step" data-reveal style="--i:{i}">'
        f'<span class="step__n">{esc(s["n"])}</span>'
        f'<div><h3 class="step__title">{esc(s["title"])}</h3>'
        f'<p class="step__detail">{esc(s["detail"])}</p></div></li>'
        for i, s in enumerate(data["steps"])
    )
    return f'<ol class="steps">{rows}</ol>'


# ── WorkshopCallout ──────────────────────────────────────────────────────────

def workshop_callout(*, depth, slot, caption_left, caption_right, callouts,
                     title, body, actions, intervals_note=None):
    items = "".join(
        f'<li><span class="callout-list__n">{esc(c["n"])}</span>'
        f'<span><span class="callout-list__part">{esc(c["part"])}</span>'
        f'<span class="callout-list__check">{esc(c["check"])}</span></span></li>'
        for c in callouts
    )
    note = f'<p class="checklist__note" style="margin-top:1rem">{esc(intervals_note)}</p>' if intervals_note else ""

    return f"""<div class="workshop-callout">
  <figure class="workshop-callout__figure" data-reveal>
    {image(slot, depth, sizes="(max-width: 960px) 100vw, 50vw")}
    <figcaption class="workshop-callout__figcaption">
      <span>{esc(caption_left)}</span><span>{esc(caption_right)}</span>
    </figcaption>
  </figure>
  <div data-reveal style="--i:1">
    <h3>{esc(title)}</h3>
    <p class="lede" style="margin-top:0.8rem">{esc(body)}</p>
    <ul class="callout-list">{items}</ul>
    {note}
    <div class="btn-row" style="margin-top:1.5rem">{actions}</div>
  </div>
</div>"""


# ── RecoverSection ───────────────────────────────────────────────────────────
#
# The sixth Index section on the homepage. It states what Frontier means by
# recovery, shows the information worth gathering, and keeps the honesty that
# dispatch is not live. The class names stay in the banner family so the
# visual system is untouched.

def recover_section(*, depth, ready, title="When the ride stops.",
                    body=None, heading_level=2, number="07"):
    body = body or (
        "Recovery at Frontier Moto means the order to work in when the machine "
        "will not move: people first, then position, then the machine. Frontier "
        "Moto is not an emergency service and no vehicle is dispatched from this "
        "website. What is live is the procedure."
    )
    items = "".join(
        f'<li><span class="ready-list__n">{esc(s["n"])}</span>'
        f'<span><span class="ready-list__label">{esc(s["title"])}</span>'
        f'<span class="ready-list__detail">{esc(s["detail"])}</span></span></li>'
        for s in ready
    )
    h = f"h{heading_level}"

    return f"""<section class="recovery-banner section" aria-labelledby="recovery-banner-title">
  <div class="container recovery-banner__inner">
    <div>
      <p class="recovery-banner__label">
        <span>{esc(number)}</span><span>Recover</span>
      </p>
      <{h} class="recovery-banner__title" id="recovery-banner-title">{esc(title)}</{h}>
      <p class="recovery-banner__body">{esc(body)}</p>
      <div class="recovery-banner__actions btn-row">
        <a class="btn btn--solid" href="{rel("/recovery/", depth)}">
          <span class="btn__label">Recovery guide</span></a>
        <a class="btn" href="{rel("/survive/", depth)}">
          <span class="btn__label">Roadside guidance</span></a>
      </div>
      <p class="disclaimer">
        <strong>Recovery dispatch is not live.</strong>
        Frontier Moto is not an emergency service and no vehicle is dispatched from
        this website. If anyone is injured, contact local emergency services first.
        The Recover page explains what we can and cannot do, and what to do instead
        where no service is available.
      </p>
    </div>
    <div>
      <p class="recovery-banner__label" style="border-bottom-color:rgba(18,18,18,0.35)">
        <span>Have this ready</span>
      </p>
      <ul class="ready-list" style="margin-top:1.2rem">{items}</ul>
    </div>
  </div>
</section>"""


# ── NewsletterForm ───────────────────────────────────────────────────────────

def newsletter_form(depth):
    return """<div class="newsletter">
  <div data-reveal>
    <h2 class="newsletter__title">Field notes for the ride ahead</h2>
    <p class="newsletter__body">
      Route notes, service intervals and what we got wrong last month. One email,
      sent when there is something worth sending, not on a schedule.
    </p>
  </div>
  <form class="newsletter__form" data-reveal style="--i:1" data-demo-form
        data-demo-message="This sign up is a front end demonstration. Your address was not stored, sent or added to any list."
        novalidate>
    <div class="newsletter__row">
      <div class="field">
        <label for="newsletter-email">Email address</label>
        <input id="newsletter-email" name="email" type="email" required
               autocomplete="email" placeholder="you@example.com">
        <p class="field__error" aria-live="polite"></p>
      </div>
      <button class="btn btn--solid" type="submit" style="margin-top:1.55rem">
        <span class="btn__label">Subscribe</span>
      </button>
    </div>
    <p class="field" style="margin-top:0.75rem">
      <span class="hint">No list exists yet. This form does not transmit anything.</span>
    </p>
    <p class="form-status" role="status" aria-live="polite"></p>
  </form>
</div>"""


# ── Static topic navigation ──────────────────────────────────────────────────

def topic_nav(topics):
    """
    Honest by construction. These are labels describing what the section covers,
    not filter controls, so they are rendered as text rather than as buttons
    that would appear to do something.
    """
    items = "".join(f"<span>{esc(t)}</span>" for t in topics)
    return f"""<div>
  <p class="mono" style="color:var(--text-muted);margin-bottom:0.6rem">Covered in this section</p>
  <div class="topic-nav">{items}</div>
</div>"""


# ── Market listing card (classified) ───────────────────────────────────────
#
# Market cards read as classifieds, not catalogue entries: reference and
# category first, condition and location before price, seller and inspection
# stated rather than implied. The anchor points at the detail block further
# down the same page, so no JavaScript is involved.

def listing_card(item, depth, i=0):
    return f"""<article class="listing-card" id="card-{esc(item["slug"])}" data-reveal style="--i:{i}">
  <p class="listing-card__top"><span>{esc(item["ref"])}</span><span>{esc(item["category_label"])}</span></p>
  <h3 class="listing-card__title"><a class="listing-card__link" href="#{esc(item["slug"])}">{esc(item["title"])}</a></h3>
  <p class="listing-card__meta">
    <span class="pill pill--used">Used</span>
    <span class="pill">{esc(item["inspection"])}</span>
  </p>
  <p class="listing-card__facts">{esc(item["condition"])} · {esc(item["location"])}</p>
  <p class="listing-card__detail">{esc(item["detail"])}</p>
  <p class="listing-card__price">{esc(item["price"])}</p>
  <p class="listing-card__foot"><span>View listing <span aria-hidden="true">&#8594;</span></span><span>{esc(item["status"])}</span></p>
</article>"""


def listing_detail(item, depth, i=0):
    specs = "".join(
        f'<li><span class="fact-list__k">{esc(s["k"])}</span><span>{esc(s["v"])}</span></li>'
        for s in item.get("specs", [])
    )
    return f"""<article class="listing-detail" id="{esc(item["slug"])}" data-reveal style="--i:{i}">
  <p class="listing-card__top"><span>{esc(item["ref"])}</span><span>{esc(item["category_label"])} · {esc(item["location"])}</span></p>
  <h3 class="listing-detail__title">{esc(item["title"])}</h3>
  <p class="listing-card__meta">
    <span class="pill pill--used">Used</span>
    <span class="pill">{esc(item["condition"])}</span>
    <span class="pill">{esc(item["inspection"])}</span>
  </p>
  <p class="listing-detail__price">{esc(item["price"])}<span>{esc(item["status"])} · Seller: {esc(item["seller"])}</span></p>
  <p class="listing-detail__body">{esc(item["description"])}</p>
  <ul class="fact-list" style="margin-top:1.25rem">{specs}</ul>
  <p class="listing-detail__faults"><strong>Known faults.</strong> {esc(item["faults"])}</p>
  <p class="listing-detail__contact">
    <span>Contact seller through Frontier Moto for now: no direct seller inbox exists on this site.</span>
    <a class="btn" href="mailto:field@frontiermoto.co.ke?subject={esc(item["ref"])}%20{esc(item["title"])}"><span class="btn__label">Enquire about {esc(item["ref"])}</span></a>
  </p>
  <p class="listing-detail__back"><a class="tlink" href="#listings">Back to all listings<span class="tlink__arrow" aria-hidden="true">&#8594;</span></a></p>
</article>"""


# ── Shop product card (catalogue) ────────────────────────────────────────────
#
# Shop cards read as new stock from Frontier: Frontier eyebrow, name, short
# descriptor, price and stock state. Same hairline cell system as the listing
# cards, different copy order and badges, so the two never look identical.

def product_card(item, depth, i=0):
    badge = f'<span class="pill pill--new">{esc(item["badge"])}</span>' if item.get("badge") else ""
    stock_cls = "product-card__stock--low" if item.get("stock") == "Low stock" else ""
    return f"""<article class="product-card" id="card-{esc(item["slug"])}" data-reveal style="--i:{i}">
  <p class="product-card__top"><span>Frontier</span><span>{esc(item["ref"])}</span></p>
  <h3 class="product-card__title"><a class="product-card__link" href="#{esc(item["slug"])}">{esc(item["title"])}</a></h3>
  <p class="product-card__blurb">{esc(item["blurb"])}</p>
  <p class="product-card__meta"><span>{esc(item["category_label"])}</span>{badge}</p>
  <p class="product-card__price">{esc(item["price"])}</p>
  <p class="product-card__foot"><span class="product-card__stock {stock_cls}">{esc(item["stock"])}</span><span>View product <span aria-hidden="true">&#8594;</span></span></p>
</article>"""


def product_detail(item, depth, i=0):
    badge = f'<span class="pill pill--new">{esc(item["badge"])}</span>' if item.get("badge") else ""
    specs = "".join(
        f'<li><span class="fact-list__k">{esc(s["k"])}</span><span>{esc(s["v"])}</span></li>'
        for s in item.get("specs", [])
    )
    return f"""<article class="product-detail" id="{esc(item["slug"])}" data-reveal style="--i:{i}">
  <p class="product-card__top"><span>Frontier · New</span><span>{esc(item["ref"])}</span></p>
  <h3 class="product-detail__title">{esc(item["title"])}</h3>
  <p class="product-card__meta"><span>{esc(item["category_label"])}</span>{badge}</p>
  <p class="product-detail__price">{esc(item["price"])}<span>{esc(item["stock"])} · Sold by Frontier Moto</span></p>
  <p class="product-detail__body">{esc(item["description"])}</p>
  <ul class="fact-list" style="margin-top:1.25rem">{specs}</ul>
  <p class="listing-detail__contact">
    <span>No checkout on this site yet. Ordering is by email with the product reference.</span>
    <a class="btn btn--solid" href="mailto:field@frontiermoto.co.ke?subject=Order%20{esc(item["ref"])}%20{esc(item["title"])}"><span class="btn__label">Order {esc(item["ref"])}</span></a>
  </p>
  <p class="listing-detail__back"><a class="tlink" href="#catalogue">Back to the catalogue<span class="tlink__arrow" aria-hidden="true">&#8594;</span></a></p>
</article>"""


def anchor_nav(items):
    """
    Category chips as same page anchors. Real links to section ids, so they
    work with no JavaScript and pass the anchor check.
    """
    links = "".join(
        f'<a href="#{esc(c["slug"])}">{esc(c["label"])}</a>' for c in items
    )
    return f"""<div>
  <p class="mono" style="color:var(--text-muted);margin-bottom:0.6rem">Browse by category</p>
  <div class="topic-nav">{links}</div>
</div>"""


def related_cards(entries, depth):
    cards = "".join(
        f'<article class="related-card">'
        f'<p class="related-card__n">{esc(e["number"])}</p>'
        f'<h3 class="related-card__title"><a href="{rel(e["href"], depth)}">{esc(e["title"])}</a></h3>'
        f'<p class="related-card__blurb">{esc(e["blurb"])}</p></article>'
        for e in entries
    )
    return f'<div class="related-grid" data-reveal>{cards}</div>'

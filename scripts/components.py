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
    RecoveryBanner      recovery_banner
    NewsletterForm      newsletter_form

    SiteHeader, FrontierWordmark, PrimaryNav, the primary header action and SiteFooter
    live in shell.py, because they are part of every document rather than
    something a page chooses to place.
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


# Shared button arrow. One copy so every guided button carries the same mark.
BTN_ARROW = (
    '<svg class="btn__arrow" width="12" height="12" viewBox="0 0 12 12" '
    'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round" aria-hidden="true" focusable="false">'
    '<path d="M4 2l4 4-4 4"/></svg>'
)


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

def author_badge(article):
    role = (article.get("author_role") or "staff").lower()
    label = {"staff": "Frontier", "pro": "Pro", "guest": "Guest"}.get(role, "Frontier")
    return f' <span class="tag-role tag-role--{esc(role)}">{esc(label)}</span>'


def index_card(entry, depth, href, i=0):
    """
    Deliberately not six identical cards. Size, media and treatment vary with
    the entry's own `size` field so the grid has a rhythm.
    Kept for compatibility. New home uses index_row vertical list.
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


def index_row(entry, depth, href, i=0):
    stat = entry.get("stat")
    stat_html = ""
    if stat:
        stat_html = (
            f'<span class="index-row__stat">{esc(stat["k"])}<b>{esc(stat["v"])}</b></span>'
        )
    return f"""<article class="index-row" data-reveal style="--i:{i}">
  <p class="index-row__n">{esc(entry["number"])}</p>
  <div class="index-row__body">
    <h3 class="index-row__title"><a class="index-row__link" href="{rel(href, depth)}">{esc(entry["label"])}</a></h3>
    <p class="index-row__blurb">{esc(entry["blurb"])}</p>
    <p class="index-row__detail">{esc(entry["detail"])}</p>
  </div>
  <div class="index-row__side">{stat_html}
    <a class="index-row__go" href="{rel(href, depth)}" aria-label="Open {esc(entry["label"])}"><span aria-hidden="true">&#8599;</span></a>
  </div>
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

    role_tag = author_badge(article)
    if href:
        title = f'<a href="{href}">{esc(article["title"])}</a>'
        prep_tag = ""
    else:
        title = esc(article["title"])
        prep_tag = '<span class="tag-upcoming">In preparation</span>'

    return f"""<article class="article-card" data-reveal style="--i:{i}">
  {media}
  <p class="article-card__meta">
    <span class="article-card__cat">{esc(article["category"])}</span>
    <span>{esc(fmt_date(article["date"]))}</span>
  </p>
  <h3 class="article-card__title">{title}</h3>
  <p class="article-card__excerpt">{esc(article["excerpt"])}</p>
  <p class="article-card__foot"><span>{esc(article["read"])} read</span><span class="card-tags">{role_tag}{prep_tag}</span></p>
</article>"""


def article_row(article, depth, i=0):
    href = _article_href(article, depth)
    role_tag = author_badge(article)
    if href:
        title = f'<a href="{href}">{esc(article["title"])}</a>'
        prep_tag = ""
    else:
        title = esc(article["title"])
        prep_tag = '<span class="tag-upcoming">In preparation</span>'

    return f"""<article class="article-row" data-reveal style="--i:{i}">
  <p class="article-row__cat">{esc(article["category"])}</p>
  <div>
    <h3 class="article-row__title">{title}</h3>
    <p class="article-row__excerpt">{esc(article["excerpt"])}</p>
    <p class="row-tags">{role_tag}{prep_tag}</p>
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


# ── EngineStudy ────────────────────────────────────────────────────────────

def engine_study(*, depth, slot, caption_left, caption_right,
                 title, body, actions, note=None, lede=None):
    """
    A photo-led workshop figure. Unlike workshop_callout this carries no
    service-point callout list: the annotated figure names its own parts.
    """
    note_html = (
        f'<p class="checklist__note" style="margin-top:1rem">{esc(note)}</p>'
        if note else ""
    )
    lede_html = (
        f'<p class="lede" style="margin-top:0.8rem">{esc(lede)}</p>'
        if lede else ""
    )

    return f"""<div class="workshop-callout">
  <figure class="workshop-callout__figure" data-reveal>
    {image(slot, depth, sizes="(max-width: 960px) 100vw, 50vw")}
    <figcaption class="workshop-callout__figcaption">
      <span>{esc(caption_left)}</span><span>{esc(caption_right)}</span>
    </figcaption>
  </figure>
  <div data-reveal style="--i:1">
    <h3>{esc(title)}</h3>
    {lede_html}
    <p class="lede" style="margin-top:0.8rem">{esc(body)}</p>
    {note_html}
    <div class="btn-row" style="margin-top:1.5rem">{actions}</div>
  </div>
</div>"""


# ── MarketCTA ──────────────────────────────────────────────────────────────

def market_cta(depth):
    """Homepage closer. Invites the reader to the market, not to a list."""
    return f"""<div class="split split--wide-left">
  <div data-reveal>
    <h3 class="newsletter__title">See what is on the stand</h3>
    <p class="newsletter__body">
      Used bikes, tools and gear from the local market, inspected in person
      and written up with notes on condition. New finds land there first.
    </p>
    <div class="btn-row" style="margin-top:1.5rem">
      <a class="btn btn--signal" href="{rel("/market/", depth)}">
        <span class="btn__label">Visit the market</span></a>
      <a class="btn" href="{rel("/market/#guides", depth)}">
        <span class="btn__label">Buying guidance</span></a>
    </div>
  </div>
  <div data-reveal style="--i:1">
    <ul class="fact-list">
      <li><span class="fact-list__k">Bikes</span><span>Used two wheelers, seen and started</span></li>
      <li><span class="fact-list__k">Tools</span><span>Used tools judged on wear, not packaging</span></li>
      <li><span class="fact-list__k">Gear</span><span>Rider and bike goods with condition notes</span></li>
    </ul>
  </div>
</div>"""


# ── RecoveryBanner ───────────────────────────────────────────────────────────

def recovery_banner(*, depth, ready, title="Workshop and recovery. Opening soon.",
                    body=None, heading_level=2, number="04"):
    body = body or (
        "Routine service, inspection and rider recovery dispatch at opening. "
        "Workshop line is a placeholder until then."
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
        <span>{esc(number)}</span><span>Workshop</span>
      </p>
      <{h} class="recovery-banner__title" id="recovery-banner-title">{esc(title)}</{h}>
      <p class="recovery-banner__body">{esc(body)}</p>
      <div class="recovery-banner__actions btn-row">
        <a class="btn btn--solid" href="{rel("/workshop/", depth)}">
          <span class="btn__label">Workshop, opening soon</span></a>
        <a class="btn" href="{rel("/ride/", depth)}">
          <span class="btn__label">Roadside guidance</span></a>
      </div>
      <p class="disclaimer">
        <strong>Workshop and recovery are opening soon.</strong>
        No service is bookable and no rider is dispatched from
        this website yet. If anyone is injured, contact local emergency services first.
        The Workshop page states the placeholder contact and what to do instead
        until opening.
      </p>
    </div>
    <div>
      <p class="recovery-banner__label" style="border-bottom-color:var(--line)">
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


# ── BikeAlertForm ──────────────────────────────────────────────────────────

def bike_alert_form(depth):
    """
    Market closer. A placeholder for a future match-and-notify feature:
    email plus bike specs or a named make, with email or WhatsApp delivery.
    Demonstration only, like every other form on the site.
    """
    return """<div class="newsletter">
  <div data-reveal>
    <h2 class="newsletter__title">Can&apos;t find what you&apos;re looking for?</h2>
    <p class="newsletter__body">
      Tell us the bike you are after and how to reach you. When a matching
      machine is inspected and listed, you get one email or WhatsApp message.
      Nothing else, and nothing until there is a match.
    </p>
    <p class="disclaimer" style="margin-top:1.25rem;max-width:44ch">
      <strong>Demonstration only.</strong>
      Matching and messaging are not built yet. This form transmits nothing
      and no alert is created.
    </p>
  </div>
  <form class="newsletter__form" data-reveal style="--i:1" data-demo-form
        data-demo-message="Demonstration only. No alert was created and nothing was stored or sent. Matching and messaging are not built yet."
        novalidate>
    <div class="form-grid">
      <div class="field field--full">
        <label for="alert-email">Email address</label>
        <input id="alert-email" name="email" type="email" required
               autocomplete="email" placeholder="you@example.com">
        <p class="field__error" aria-live="polite"></p>
      </div>
      <div class="field">
        <label for="alert-size">Engine size</label>
        <select id="alert-size" name="size" required>
          <option value="">Choose one</option>
          <option>Up to 125 cc</option>
          <option>125 to 250 cc</option>
          <option>250 to 400 cc</option>
          <option>Over 400 cc</option>
          <option>Not sure, advise me</option>
        </select>
        <p class="field__error" aria-live="polite"></p>
      </div>
      <div class="field">
        <label for="alert-type">Bike type</label>
        <select id="alert-type" name="type" required>
          <option value="">Choose one</option>
          <option>Commuter</option>
          <option>Dual sport</option>
          <option>Adventure</option>
          <option>Anything sound</option>
        </select>
        <p class="field__error" aria-live="polite"></p>
      </div>
      <div class="field field--full">
        <label for="alert-make">Make, model or bike name</label>
        <input id="alert-make" name="make" type="text"
               placeholder="A specific bike, or leave blank for any match">
        <p class="field__error" aria-live="polite"></p>
      </div>
      <div class="field field--full" data-channel-toggle="alert-phone-wrap">
        <span class="mono" id="alert-channel-label" style="display:block;margin-bottom:0.5rem">Notify me by</span>
        <div role="radiogroup" aria-labelledby="alert-channel-label">
          <label class="radio"><input type="radio" name="channel" value="email" checked> Email</label>
          <label class="radio"><input type="radio" name="channel" value="whatsapp"> WhatsApp</label>
        </div>
      </div>
      <div class="field field--full" id="alert-phone-wrap" hidden>
        <label for="alert-phone">WhatsApp number</label>
        <input id="alert-phone" name="phone" type="tel"
               autocomplete="tel" placeholder="+254 700 000 000">
        <p class="field__error" aria-live="polite"></p>
      </div>
    </div>
    <div class="btn-row" style="margin-top:1.5rem">
      <button class="btn btn--solid" type="submit">
        <span class="btn__label">Notify me</span>
      </button>
    </div>
    <p class="form-status" role="status" aria-live="polite"></p>
  </form>
</div>"""


# ── MarketBrowser ──────────────────────────────────────────────────────────

# Tiny inline stats icons. Decorative duplicates of adjacent text.
GEAR_SVG = (
    '<svg width="13" height="13" viewBox="0 0 16 16" fill="none" '
    'stroke="currentColor" stroke-width="1.6" aria-hidden="true" focusable="false">'
    '<circle cx="8" cy="8" r="2.2"/>'
    '<path d="M8 1.5v2M8 12.5v2M1.5 8h2M12.5 8h2M3.4 3.4l1.4 1.4M11.2 11.2l1.4 1.4'
    'M12.6 3.4l-1.4 1.4M4.8 11.2l-1.4 1.4"/></svg>'
)

TAG_SVG = (
    '<svg width="13" height="13" viewBox="0 0 16 16" fill="none" '
    'stroke="currentColor" stroke-width="1.6" aria-hidden="true" focusable="false">'
    '<path d="M2.5 2.5h5l6 6-5 5-6-6v-5Z"/><circle cx="6" cy="6" r="1.2"/></svg>'
)

def _listing_card(l, i):
    stat = l.get("gearbox") or l["category"]
    icon = GEAR_SVG if l.get("gearbox") else TAG_SVG
    chips = "".join(
        f'<span class="tag">{esc(t)}</span>'
        for t in [l["status"]] + l.get("tags", [])
    )
    price = l.get("price_guide")
    price_html = (
        f'<p class="listing-card__price">Guide price KSh {price:,}'
        f'<span>{esc(l["meta"])}</span></p>'
        if price else ""
    )
    search_text = " ".join([
        l["title"], l["detail"], l["ref"], l["meta"], l["category"],
        l["status"], l.get("make") or "", l.get("kind") or "",
        l.get("size") or "", l.get("gearbox") or "",
        " ".join(l.get("tags", [])),
    ])
    return f"""<article class="listing-card" data-reveal style="--i:{i}"
      data-category="{esc(l["category"])}"
      data-size="{esc(l.get("size") or "")}"
      data-status="{esc(l["status"])}"
      data-search="{esc(search_text)}">
      <div class="listing-card__media" aria-hidden="true"><span>{esc(l["ref"])}</span></div>
      <div class="listing-card__body">
        <h2 class="article-row__title">{esc(l["title"])}</h2>
        <p class="article-row__cat listing-card__stat">{icon} {esc(stat)}</p>
        <p class="article-row__excerpt">{esc(l["detail"])}</p>
        <p class="tag-row">{chips}</p>
        {price_html}
      </div>
    </article>"""


def market_browser(market, listings):
    """
    Motifiti style market browsing: search plus honest filters over a
    vertical stack of listing cards. The filters genuinely filter in the
    browser (see index.js); with JS off every listing is shown. Tools and
    gear carry no engine size, so they always pass the size filter.
    """
    rows = "".join(_listing_card(l, i) for i, l in enumerate(listings))

    return f"""<div class="market-filters" data-reveal data-market-filters>
  <div class="field">
    <label for="market-search">Search listings</label>
    <input id="market-search" name="search" type="search" autocomplete="off"
           placeholder="Try 150 cc, commuter or Nairobi">
  </div>
  <div class="field">
    <label for="market-category">Category</label>
    <select id="market-category" name="category">
      <option value="">All categories</option>
      <option>Used bike</option>
      <option>Used tool</option>
      <option>Used gear</option>
    </select>
  </div>
  <div class="field">
    <label for="market-size">Engine size</label>
    <select id="market-size" name="size">
      <option value="">Any size</option>
      <option>Up to 125 cc</option>
      <option>125 to 250 cc</option>
      <option>250 to 400 cc</option>
      <option>Over 400 cc</option>
    </select>
  </div>
  <div class="field">
    <label for="market-status">Condition</label>
    <select id="market-status" name="status">
      <option value="">Any condition</option>
      <option>Inspected</option>
      <option>Seen only</option>
      <option>Demo</option>
    </select>
  </div>
</div>
<p class="scroll-hint" data-market-count role="status" aria-live="polite">{len(listings)} listings</p>
<div class="row-list" data-market-list>{rows}</div>
<p class="lede" data-market-empty hidden style="margin-top:1.5rem;max-width:52ch">
  No listings match those filters. Clear them to see everything again, or join
  the waitlist below and we will message you when your bike lands.
</p>"""


# ── MarketSellerMenu ───────────────────────────────────────────────────────

def seller_menu(depth):
    """Market-local account menu. Every entry is a real placeholder page."""
    entries = [
        ("FAQ", "/faq/"),
        ("Contact us", "/contact/"),
        ("Log in", "/login/"),
        ("Sign up", "/join/"),
    ]
    items = "".join(
        f'<li><a href="{rel(href, depth)}">{esc(label)}</a></li>'
        for label, href in entries
    )
    return f'<nav class="seller-menu" aria-label="Market account"><ul>{items}</ul></nav>'


# ── MarketPagination ─────────────────────────────────────────────────────────

def market_pages_nav(page_num, total_pages, depth):
    """Static pagination. Real links to generated pages, not controls."""
    def href(n):
        return rel("/market/" if n == 1 else f"/market/page/{n}/", depth)

    nums = []
    for n in range(1, total_pages + 1):
        if n == 1 or n == total_pages or abs(n - page_num) <= 2:
            current = ' aria-current="page"' if n == page_num else ""
            nums.append(
                f'<a href="{href(n)}"{current}>{n}</a>'
            )
        elif not nums or not nums[-1].endswith("…</span>"):
            nums.append('<span aria-hidden="true">…</span>')

    prev = (
        f'<a href="{href(page_num - 1)}" aria-label="Previous page">&#8249; Prev</a>'
        if page_num > 1 else '<span aria-hidden="true">&#8249; Prev</span>'
    )
    nxt = (
        f'<a href="{href(page_num + 1)}" aria-label="Next page">Next &#8250;</a>'
        if page_num < total_pages else '<span aria-hidden="true">Next &#8250;</span>'
    )
    return (
        f'<nav class="pages-nav" aria-label="Market pages">'
        f"{prev}{''.join(nums)}{nxt}</nav>"
    )


# ── PopularSearches ──────────────────────────────────────────────────────────

def popular_searches(market):
    """
    Tag buttons with real counts computed from the listings. Clicking one
    fills the search box and filters the list, so the buttons genuinely work.
    Only values present in the data are rendered.
    """
    counts = {}
    order = []
    for l in market["listings"]:
        for term in [l.get("make"), l.get("kind"), l.get("size")]:
            if term and term not in counts:
                counts[term] = 0
                order.append(term)
            if term:
                counts[term] += 1

    buttons = "".join(
        f'<button type="button" data-search-tag="{esc(term)}">'
        f'<span>{esc(term)}</span><span>{counts[term]}</span></button>'
        for term in order
    )
    return f"""<div data-reveal>
  <div class="tag-cloud" data-search-tags>{buttons}</div>
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


def related_cards(entries, depth):
    cards = "".join(
        f'<article class="related-card">'
        f'<p class="related-card__n">{esc(e["number"])}</p>'
        f'<h3 class="related-card__title"><a href="{rel(e["href"], depth)}">{esc(e["title"])}</a></h3>'
        f'<p class="related-card__blurb">{esc(e["blurb"])}</p></article>'
        for e in entries
    )
    return f'<div class="related-grid" data-reveal>{cards}</div>'

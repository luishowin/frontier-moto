"""
Article detail.

Opens with the masthead rail rather than a photographic hero, because a reader
arriving here already chose the story and the headline should be the first thing
they see. The specification list sits beside the body on desktop and above it in
the reading sequence on narrow screens.
"""

from components import (
    article_card,
    esc,
    fmt_date,
    image,
    newsletter_form,
    rel,
    section_label,
    spec_list,
)

DEPTH = 2

SECTION_TITLES = {
    "ride": "Ride", "navigate": "Navigate", "survive": "Survive",
    "maintain": "Maintain", "market": "Market", "news": "News",
}


def _block(b):
    kind = b["type"]

    if kind == "p":
        return f'<p>{esc(b["text"])}</p>'

    if kind == "h2":
        return f'<h2>{esc(b["text"])}</h2>'

    if kind == "pull":
        return f'<p class="pull">{esc(b["text"])}</p>'

    if kind == "note":
        return (
            f'<aside class="note"><strong>{esc(b["title"])}</strong>'
            f'<span>{esc(b["text"])}</span></aside>'
        )

    if kind == "list":
        items = "".join(f"<li>{esc(i)}</li>" for i in b["items"])
        title = f'<p class="list-title">{esc(b["title"])}</p>' if b.get("title") else ""
        return f'<div>{title}<ul class="marked">{items}</ul></div>'

    raise ValueError(f"unknown block type: {kind}")


def build(article, data):
    articles = data["articles"]["articles"]
    section = article["section"]

    more = [
        a for a in articles
        if a is not article and (a["section"] == section or a.get("slug"))
    ][:3]

    body = "\n".join(_block(b) for b in article["body"])

    out = []

    # ── Masthead ─────────────────────────────────────────────────────────────
    out.append(f"""<article>
<header class="section section--tight page-top">
  <div class="container">
    <p class="feature__eyebrow" style="border-bottom:none;padding-bottom:0">
      <span>{esc(article["issue"])}</span>
      <span>{esc(article["category"])}</span>
      <a href="{rel(f"/{section}/", DEPTH)}">{esc(SECTION_TITLES[section])}</a>
    </p>
    <h1 style="margin-top:1rem;font-size:clamp(2.1rem,1.3rem+3.4vw,4rem);letter-spacing:-0.032em;max-width:20ch">
      {esc(article["title"])}
    </h1>
    <p class="lede" style="margin-top:1.1rem;max-width:56ch">{esc(article["dek"])}</p>
    <p class="feature__eyebrow" style="margin-top:1.75rem;border-bottom:none;padding-bottom:0">
      <span>{esc(article["author"])}</span>
      <span>{esc(article["location"])}</span>
      <span>
        <time datetime="{esc(article["date"])}">{esc(fmt_date(article["date"]))}</time>
      </span>
      <span>{esc(article["read"])} read</span>
    </p>
  </div>
</header>

<figure class="container" style="margin-bottom:clamp(2rem,1.5rem+2vw,3.5rem)">
  {image(article["image"], DEPTH, priority=True, lazy=False, sizes="(max-width: 1320px) 100vw, 1320px")}
  <figcaption class="workshop-callout__figcaption" style="border:1px solid var(--line);border-top:none">
    <span>{esc(article["image_alt"])}</span>
    <span>{esc(article["issue"])}</span>
  </figcaption>
</figure>

<div class="container section" style="padding-top:0">
  <div class="split split--wide-left">
    <div class="article-body" data-reveal>{body}</div>
    <aside class="article-aside" data-reveal style="--i:1" aria-label="Article data">
      <p class="mono" style="color:var(--text-muted);margin-bottom:0.5rem">At a glance</p>
      {spec_list(article["specs"], single=True)}
      <p class="checklist__note" style="margin-top:1.25rem">
        Figures are what we measured or timed ourselves. Where a number is an estimate
        it says so, and where conditions change it, the condition is named.
      </p>
      <div class="btn-row" style="margin-top:1.5rem">
        <a class="btn" href="{rel(f"/{section}/", DEPTH)}">
          <span class="btn__label">More in {esc(SECTION_TITLES[section])}</span></a>
      </div>
    </aside>
  </div>
</div>
</article>""")

    # ── More reading ─────────────────────────────────────────────────────────
    if more:
        cards = "".join(
            article_card(a, DEPTH, i, with_media=bool(a.get("image")))
            for i, a in enumerate(more)
        )
        out.append(f"""<section class="section section--soft" aria-labelledby="more-title">
  <div class="container">
    {section_label("Next", "Related guides", esc(SECTION_TITLES[section]), heading_id="more-title")}
    <div class="card-grid">{cards}</div>
  </div>
</section>""")

    out.append(f"""<section class="section" aria-labelledby="notes-title">
  <div class="container">
    {section_label("End", "Field notes", "One email, occasionally", heading_id="notes-title")}
    {newsletter_form(DEPTH)}
  </div>
</section>""")

    return "\n".join(out)


def page_meta(article, site):
    base = site["site"]["base_url"].rstrip("/")
    url = f'{base}/field/{article["slug"]}/'
    return {
        "href": f'/field/{article["slug"]}/',
        "out": f'field/{article["slug"]}/index.html',
        "depth": DEPTH,
        "slug": article["section"],
        "title": article["title"],
        "description": article["dek"],
        "dark_hero": False,
        "og_type": "article",
        "preload_image": article["image"],
        "preload_sizes": "(max-width: 1320px) 100vw, 1320px",
        "schema": {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": article["title"],
            "description": article["dek"],
            "url": url,
            "mainEntityOfPage": {"@type": "WebPage", "@id": url},
            "datePublished": article["date"],
            "dateModified": article["date"],
            "articleSection": SECTION_TITLES[article["section"]],
            "wordCount": sum(
                len(b.get("text", "").split()) + sum(len(i.split()) for i in b.get("items", []))
                for b in article["body"]
            ),
            "image": f'{base}/assets/img/{article["image"]}.svg',
            "author": {"@type": "Organization", "name": article["author"]},
            "publisher": {
                "@type": "Organization",
                "name": site["brand"]["name"],
                "url": site["site"]["base_url"],
            },
        },
    }

"""
The shared editorial page system.

Ride, Navigate, Survive, Maintain, Market and News are all the same page with
different content and a different practical data module. Workshop and Recovery
have their own stricter structures and live in their own modules.

Every section page carries: a masthead, a lead block, one data module that is
actually useful, the full listing for that section, cross-links to adjacent
sections, and the newsletter.
"""

from components import (
    article_card,
    article_row,
    checklist,
    editorial_hero,
    esc,
    feature_story,
    newsletter_form,
    related_cards,
    rel,
    section_label,
    spec_list,
    steps,
    topic_nav,
)

DEPTH = 1

SECTION_TITLES = {
    "ride": "Ride", "navigate": "Navigate", "survive": "Survive",
    "maintain": "Maintain", "market": "Market", "news": "News",
    "workshop": "Workshop", "recovery": "Recovery",
}

SECTION_BLURBS = {
    "ride": "Road safety, riding technique and awareness.",
    "navigate": "Routes, maps, fuel and terrain preparation.",
    "survive": "Breakdowns, preparedness and roadside resilience.",
    "maintain": "Service, diagnostics and workshop knowledge.",
    "market": "Gear, loadout and buying guidance.",
    "news": "Field reports and regional motorcycle news.",
    "workshop": "Service, inspection and repair.",
    "recovery": "Help when the ride stops.",
}


# ── Data modules ─────────────────────────────────────────────────────────────

def _module_checklist(page, data):
    keys = {
        "pre-ride": ["pre-ride", "weather", "contacts"],
    }.get(page["module_key"], [page["module_key"]])
    lists = "".join(checklist(data["checklists"]["checklists"][k], i)
                    for i, k in enumerate(keys))
    return "Ride ready", "Run before a long day", f'<div class="utility-grid">{lists}</div>'


def _module_steps(page, data):
    seq = data["checklists"]["steps"][page["module_key"]]
    return (
        seq["title"],
        seq["number"],
        f'<p class="lede" style="margin-bottom:1.5rem;max-width:62ch">{esc(seq["note"])}</p>'
        + steps(seq),
    )


def _module_routes(page, data):
    rows = "".join(
        f"""<tr>
      <td class="num">{esc(r["ref"])}</td>
      <th scope="row">{esc(r["name"])}<span class="note" style="display:block">{esc(r["note"])}</span></th>
      <td class="num">{esc(r["country"])}</td>
      <td class="num">{esc(r["distance"])}</td>
      <td class="num">{esc(r["time"])}</td>
      <td class="num">{esc(r["fuel_gap"])}</td>
      <td>{esc(r["surface"])}</td>
    </tr>"""
        for r in data["technical"]["routes"]
    )
    table = f"""<div class="table-wrap">
    <table class="data-table">
      <caption class="visually-hidden">Route notes with distance, riding time, longest fuel gap and surface</caption>
      <thead><tr>
        <th scope="col">Ref</th><th scope="col">Route</th><th scope="col">Country</th>
        <th scope="col">Distance</th><th scope="col">Time</th>
        <th scope="col">Fuel gap</th><th scope="col">Surface</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
  <p class="scroll-hint">Scroll the table sideways to see every column. Times are for a
  loaded machine at an unhurried pace, not a best case.</p>"""
    return "Route notes", "Six logged, more in progress", table


def _module_intervals(page, data):
    rows = "".join(
        f"""<tr>
      <th scope="row">{esc(r["item"])}</th>
      <td class="num">{esc(r["tarmac"])}</td>
      <td class="num">{esc(r["murram"])}</td>
      <td class="note">{esc(r["note"])}</td>
    </tr>"""
        for r in data["technical"]["intervals"]
    )
    table = f"""<div class="table-wrap">
    <table class="data-table">
      <caption class="visually-hidden">Service intervals compared between sealed and unsealed use</caption>
      <thead><tr>
        <th scope="col">Item</th><th scope="col">Tarmac</th>
        <th scope="col">Murram</th><th scope="col">Why it differs</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
  <p class="scroll-hint">Scroll the table sideways to see every column. These are working
  intervals for the region, not a substitute for the manufacturer schedule on a machine
  under warranty.</p>"""
    return "Service intervals", "Tarmac against murram", table


def _module_listings(page, data):
    market = data["market"]
    gear = "".join(
        f"""<article class="gear-item" data-reveal style="--i:{i}">
      <p class="gear-item__top"><span>{esc(g["ref"])}</span><span>{esc(g["category"])}</span></p>
      <h3 class="gear-item__name">{esc(g["name"])}</h3>
      <p class="gear-item__summary">{esc(g["summary"])}</p>
      {spec_list(g["spec"], single=True)}
      <p class="gear-item__top" style="margin-top:auto;padding-top:0.9rem">
        <span class="verdict verdict--{"tested" if g["verdict"] == "Field tested" else "untested"}">{esc(g["verdict"])}</span>
      </p>
    </article>"""
        for i, g in enumerate(market["gear"])
    )

    listings = "".join(
        f"""<article class="article-row" data-reveal style="--i:{i}">
      <p class="article-row__cat">{esc(l["ref"])}</p>
      <div>
        <h3 class="article-row__title">{esc(l["title"])}</h3>
        <p class="article-row__excerpt">{esc(l["detail"])}</p>
      </div>
      <p class="article-row__meta">{esc(l["meta"])}<br>{esc(l["status"])}</p>
    </article>"""
        for i, l in enumerate(market["listings"])
    )

    return "Equipment", "Six items, one untested", f"""<div class="gear-grid" id="inspect">{gear}</div>
  <h3 style="margin-top:3rem" id="price">Motorcycles seen</h3>
  <p class="lede" style="margin-top:0.6rem;margin-bottom:1.25rem;max-width:62ch">
    Machines we have inspected or, where marked, only seen. Frontier Moto does not
    broker sales and holds no stock. These are notes on condition, not offers.
  </p>
  <div class="row-list">{listings}</div>"""


MODULES = {
    "checklist": _module_checklist,
    "steps": _module_steps,
    "routes": _module_routes,
    "intervals": _module_intervals,
    "listings": _module_listings,
}


# ── Page ─────────────────────────────────────────────────────────────────────

def build(page, data):
    site = data["site"]
    articles = data["articles"]["articles"]
    mine = [a for a in articles if a["section"] == page["slug"]]
    mine.sort(key=lambda a: a["date"], reverse=True)

    lead = next((a for a in mine if a.get("slug")), None)
    rest = [a for a in mine if a is not lead]

    out = []
    n = page["number"]

    # Sub-numbers are handed out in order as blocks are appended. A page with no
    # lead article skips one block, and hardcoded numbering left a visible gap
    # in the sequence on exactly the pages that make a point of being numbered.
    counter = {"i": 0}

    def sub():
        counter["i"] += 1
        return f'{n}.{counter["i"]}'

    # ── Masthead ─────────────────────────────────────────────────────────────
    out.append(editorial_hero(
        slot=page["hero_image"],
        depth=DEPTH,
        label_accent=n,
        label="Frontier Index",
        title_lines=[page["title"]],
        lede=page["purpose"],
        compact=True,
        flat=True,
        field=[
            ("Section", f'{n} / {page["title"]}'),
            ("Guides", f"{len(mine)} listed"),
            ("Topics", str(len(page["topics"]))),
            ("Updated", "24 AUG 2026"),
        ],
    ))

    # ── Lead ─────────────────────────────────────────────────────────────────
    if lead:
        body = feature_story(lead, DEPTH, href=f'/field/{lead["slug"]}/')
    else:
        # No full article in this section yet, so the lead block is the section
        # statement and its topic list rather than a card pretending to be one.
        body = f"""<div class="split split--wide-left">
      <div data-reveal>
        <p class="lede" style="max-width:none;color:var(--text)">{esc(page["lede"])}</p>
        <div class="btn-row" style="margin-top:1.75rem">
          <a class="btn btn--solid" href="#guides"><span class="btn__label">Guides in this section</span></a>
          <a class="btn" href="#module"><span class="btn__label">Practical module</span></a>
        </div>
      </div>
      <div data-reveal style="--i:1">{topic_nav(page["topics"])}</div>
    </div>"""

    lead_aside = lead["issue"] if lead else f'{len(page["topics"])} topics'
    out.append(f"""<section class="section" aria-labelledby="lead-title">
  <div class="container">
    {section_label(sub(), "In this section", lead_aside, heading_id="lead-title")}
    {body}
  </div>
</section>""")

    if lead:
        out.append(f"""<section class="section section--tight section--soft" aria-labelledby="topics-title">
  <div class="container">
    {section_label(sub(), "Scope", "Static index, not a filter", heading_id="topics-title")}
    <div class="split">
      <p class="lede" style="max-width:none">{esc(page["lede"])}</p>
      {topic_nav(page["topics"])}
    </div>
  </div>
</section>""")

    # ── Data module ──────────────────────────────────────────────────────────
    if page["module"] != "none":
        title, aside, module_html = MODULES[page["module"]](page, data)
        soft = "" if lead else " section--soft"
        out.append(f"""<section class="section{soft}" id="module" aria-labelledby="module-title">
  <div class="container">
    {section_label(sub(), title, aside, heading_id="module-title")}
    {module_html}
  </div>
</section>""")

    # ── Listing ──────────────────────────────────────────────────────────────
    if rest:
        rows = "".join(article_row(a, DEPTH, i) for i, a in enumerate(rest))
        out.append(f"""<section class="section" id="guides" aria-labelledby="guides-title">
  <div class="container">
    {section_label(sub(), "Guides", f"{len(rest)} listed", heading_id="guides-title")}
    <div class="row-list">{rows}</div>
    <p class="scroll-hint" style="margin-top:1.25rem">
      Entries marked in preparation are planned and drafted but not published. They are
      listed so the scope of the section is honest rather than to imply a page exists.
    </p>
  </div>
</section>""")

    # ── Cross links ──────────────────────────────────────────────────────────
    related = [
        {
            "number": f"{i + 1:02d}",
            "title": SECTION_TITLES[slug],
            "blurb": SECTION_BLURBS[slug],
            "href": f"/{slug}/",
        }
        for i, slug in enumerate(page["related"] + ["workshop"])
    ]
    out.append(f"""<section class="section section--soft" aria-labelledby="related-title">
  <div class="container">
    {section_label(sub(), "Adjacent sections", "Where this leads", heading_id="related-title")}
    {related_cards(related, DEPTH)}
  </div>
</section>""")

    # ── Newsletter ───────────────────────────────────────────────────────────
    out.append(f"""<section class="section" aria-labelledby="notes-title">
  <div class="container">
    {section_label(sub(), "Field notes", "One email, occasionally", heading_id="notes-title")}
    {newsletter_form(DEPTH)}
  </div>
</section>""")

    return "\n".join(out)


def page_meta(page, site):
    return {
        "href": f'/{page["slug"]}/',
        "out": f'{page["slug"]}/index.html',
        "depth": DEPTH,
        "slug": page["slug"],
        "title": page["title"],
        "description": page["purpose"],
        "dark_hero": True,
        "preload_image": f'/assets/img/{page["hero_image"]}.svg',
        "schema": {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": f'{page["title"]} | {site["brand"]["name"]}',
            "description": page["purpose"],
            "url": site["site"]["base_url"].rstrip("/") + f'/{page["slug"]}/',
            "isPartOf": {
                "@type": "WebSite",
                "name": site["brand"]["name"],
                "url": site["site"]["base_url"],
            },
            "about": [{"@type": "Thing", "name": t} for t in page["topics"]],
        },
    }

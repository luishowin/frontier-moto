"""Homepage. Nine numbered blocks, in the order the brief sets out."""

from components import (
    article_card,
    checklist,
    editorial_hero,
    esc,
    feature_story,
    index_card,
    newsletter_form,
    recovery_banner,
    rel,
    section_label,
    workshop_callout,
)

DEPTH = 0


def build(data):
    site = data["site"]
    sections = data["sections"]
    articles = data["articles"]
    checklists = data["checklists"]["checklists"]
    technical = data["technical"]
    market = data["market"]

    by_slug = {a["slug"]: a for a in articles["articles"] if a.get("slug")}
    featured = by_slug[articles["featured_home"]]

    latest = sorted(
        [a for a in articles["articles"] if a["slug"] != featured["slug"]],
        key=lambda a: a["date"],
        reverse=True,
    )[:6]

    out = []

    # ── 01 Frontier ──────────────────────────────────────────────────────────
    out.append(editorial_hero(
        slot="hero-home",
        depth=DEPTH,
        label_accent="01",
        label="Frontier",
        title_lines=["Ride farther.", "Ride smarter.", "Get home."],
        lede=site["brand"]["tagline"],
        actions=(
            '<a class="btn btn--ghost-light" href="#index">'
            '<span class="btn__label">Explore Frontier</span></a>'
            f'<a class="btn btn--signal" href="{rel("/recovery/", DEPTH)}">'
            '<span class="btn__label">Get Recovery</span></a>'
        ),
        field=[
            ("Field log", "014 / Escarpment"),
            ("Season", "Long rains, closing"),
            ("Surface", "Tarmac, polished on descent"),
            ("Compiled", "Nanyuki, Kenya"),
        ],
    ))

    # ── 02 The Frontier Index ────────────────────────────────────────────────
    hrefs = {
        "ride": "/ride/", "navigate": "/navigate/", "survive": "/survive/",
        "maintain": "/maintain/", "market": "/market/", "recovery": "/recovery/",
    }
    cards = "".join(
        index_card(entry, DEPTH, hrefs[entry["slug"]], i)
        for i, entry in enumerate(sections["index"])
    )
    out.append(f"""<section class="section" id="index" aria-labelledby="index-title">
  <div class="container">
    {section_label("02", "The Frontier Index", "Six ways in", heading_id="index-title")}
    <p class="lede" style="margin-bottom:2rem;max-width:62ch">
      Everything on this site sits under one of six headings. They are ordered the way
      a ride is: what you do on the road, where you are going, what happens when it goes
      wrong, and how the machine is kept alive in between.
    </p>
    <div class="index-grid">{cards}</div>
  </div>
</section>""")

    # ── 03 Field story ───────────────────────────────────────────────────────
    out.append(f"""<section class="section section--soft" aria-labelledby="feature-title">
  <div class="container">
    {section_label("03", "Field story", featured["issue"], heading_id="feature-title")}
    {feature_story(featured, DEPTH, href=f'/field/{featured["slug"]}/')}
  </div>
</section>""")

    # ── 04 Ride ready ────────────────────────────────────────────────────────
    keys = ["pre-ride", "weather", "carry", "fuel", "contacts"]
    lists = "".join(checklist(checklists[k], i) for i, k in enumerate(keys))
    out.append(f"""<section class="section" aria-labelledby="ready-title">
  <div class="container">
    {section_label("04", "Ride ready", "Field guide, not a shop", heading_id="ready-title")}
    <p class="lede" style="margin-bottom:2rem;max-width:62ch">
      Five lists worth running before a long day. None of this is equipment you need to
      buy. Most of it is ten minutes and a decision made while you are still somewhere
      you can act on it.
    </p>
    <div class="utility-grid">{lists}</div>
    <p class="scroll-hint" style="margin-top:1.25rem">
      Boxes are printed marks, not controls. Nothing here is stored or tracked.
    </p>
  </div>
</section>""")

    # ── 05 Maintenance and workshop ──────────────────────────────────────────
    out.append(f"""<section class="section section--soft" aria-labelledby="maintain-title">
  <div class="container">
    {section_label("05", "Maintenance", "Service points, chain drive single", heading_id="maintain-title")}
    {workshop_callout(
        depth=DEPTH,
        slot="maintain-diagram",
        caption_left="Fig. 05.1 Service points",
        caption_right="Chain drive single",
        callouts=technical["callouts"],
        title="Six things that decide whether a bike finishes the route",
        body=(
            "Service books assume clean fuel, sealed roads and mild dust. Adjust the "
            "intervals for how the machine is actually used, or it will adjust them for "
            "you at the least convenient point on the route."
        ),
        intervals_note=(
            "Full intervals for tarmac and murram, with the reasoning for each, are in "
            "the Maintain section."
        ),
        actions=(
            f'<a class="btn btn--solid" href="{rel("/maintain/", DEPTH)}">'
            '<span class="btn__label">Maintenance guides</span></a>'
            f'<a class="btn" href="{rel("/workshop/", DEPTH)}">'
            '<span class="btn__label">Workshop services</span></a>'
        ),
    )}
  </div>
</section>""")

    # ── 06 Equipment and market ──────────────────────────────────────────────
    gear = "".join(
        f"""<article class="gear-item" data-reveal style="--i:{i}">
      <p class="gear-item__top"><span>{esc(g["ref"])}</span><span>{esc(g["category"])}</span></p>
      <h3 class="gear-item__name">{esc(g["name"])}</h3>
      <p class="gear-item__summary">{esc(g["summary"])}</p>
      <p class="gear-item__top" style="margin-top:1rem;padding-top:0.8rem;border-top:1px solid var(--line)">
        <span class="verdict verdict--{"tested" if g["verdict"] == "Field tested" else "untested"}">{esc(g["verdict"])}</span>
      </p>
    </article>"""
        for i, g in enumerate(market["gear"][:4])
    )

    guides = "".join(
        f'<li><a class="tlink" href="{rel(g["href"], DEPTH)}">{esc(g["title"])}'
        f'<span class="tlink__arrow" aria-hidden="true">&#8594;</span></a>'
        f'<span class="checklist__detail">{esc(g["detail"])}</span></li>'
        for g in market["guides"]
    )

    out.append(f"""<section class="section" aria-labelledby="equip-title">
  <div class="container">
    {section_label("06", "Equip and market", "Tested, not sponsored", heading_id="equip-title")}
    <div class="split split--wide-left" style="margin-bottom:2rem">
      <p class="lede" style="max-width:none">{esc(market["note"])}</p>
      <ul style="display:grid;gap:1rem">{guides}</ul>
    </div>
    <div class="gear-grid">{gear}</div>
    <div class="btn-row" style="margin-top:1.75rem">
      <a class="btn" href="{rel("/market/", DEPTH)}">
        <span class="btn__label">All equipment and listings</span></a>
    </div>
  </div>
</section>""")

    # ── 07 Recovery ──────────────────────────────────────────────────────────
    out.append(recovery_banner(
        depth=DEPTH,
        number="07",
        ready=data["checklists"]["steps"]["recovery"]["steps"][:5],
    ))

    # ── 08 Latest ────────────────────────────────────────────────────────────
    cards = "".join(article_card(a, DEPTH, i, with_media=bool(a.get("image")))
                    for i, a in enumerate(latest))
    out.append(f"""<section class="section" aria-labelledby="latest-title">
  <div class="container">
    {section_label("08", "Latest and field notes", "Updated 24 Aug 2026", heading_id="latest-title")}
    <div class="card-grid">{cards}</div>
    <div class="btn-row" style="margin-top:2rem">
      <a class="btn" href="{rel("/news/", DEPTH)}"><span class="btn__label">All news</span></a>
      <a class="btn" href="{rel("/ride/", DEPTH)}"><span class="btn__label">Riding guides</span></a>
    </div>
  </div>
</section>""")

    # ── 09 Newsletter ────────────────────────────────────────────────────────
    out.append(f"""<section class="section section--soft" aria-labelledby="notes-title">
  <div class="container">
    {section_label("09", "Field notes", "One email, occasionally", heading_id="notes-title")}
    {newsletter_form(DEPTH)}
  </div>
</section>""")

    return "\n".join(out)


PAGE = {
    "href": "/",
    "out": "index.html",
    "depth": DEPTH,
    "slug": None,
    "title": "Frontier Moto | Motorcycle knowledge and support for East Africa",
    "description": (
        "Riding skills, route notes, maintenance guides, equipment and workshop support "
        "for riders across Kenya, Uganda, Tanzania and Rwanda."
    ),
    "dark_hero": True,
    "preload_image": "/assets/img/hero-home.svg",
}

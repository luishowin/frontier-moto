"""Homepage. The hero plus eight numbered blocks: the Index, field knowledge,
readiness, maintenance, equipment, recovery, field notes and the newsletter."""

from components import (
    article_card,
    checklist,
    editorial_hero,
    esc,
    feature_story,
    index_card,
    newsletter_form,
    recover_section,
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
        title_lines=["Ride farther.", "Ride smarter.", "Get home."],
        lede=site["brand"]["tagline"],
        actions=(
            '<a class="btn btn--ghost-light" href="#index">'
            '<span class="btn__label">Explore Frontier</span></a>'
            f'<a class="btn btn--signal" href="{rel("/market/", DEPTH)}">'
            '<span class="btn__label">Browse the Market</span></a>'
        ),
    ))

    # ── 02 The Frontier Index ────────────────────────────────────────────────
    hrefs = {
        "ride": "/ride/", "navigate": "/navigate/", "survive": "/survive/",
        "maintain": "/maintain/", "equip": "/equip/", "recovery": "/recovery/",
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
    # Each list links to the section that carries it further. Same stretched
    # link pattern as the index and article cards: one real anchor per card.
    ready_hrefs = {
        "pre-ride": "/ride/",
        "weather": "/navigate/",
        "carry": "/survive/",
        "fuel": "/navigate/",
        "contacts": "/survive/",
    }
    keys = ["pre-ride", "weather", "carry", "fuel", "contacts"]
    lists = "".join(
        checklist(checklists[k], i, href=ready_hrefs[k], depth=DEPTH)
        for i, k in enumerate(keys)
    )
    out.append(f"""<section class="section" aria-labelledby="ready-title">
  <div class="container">
    {section_label("04", "Ride ready", "Before a long day", heading_id="ready-title")}
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

    # ── 06 Equip ─────────────────────────────────────────────────────────────
    # The knowledge layer: what to carry and why. Sourcing and availability
    # live on the Market page, linked from here rather than repeated.
    equip_page = next(p for p in sections["pages"] if p["slug"] == "equip")
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

    out.append(f"""<section class="section" aria-labelledby="equip-title">
  <div class="container">
    {section_label("06", "Equip", "Tested, not sponsored", heading_id="equip-title")}
    <p class="lede" style="margin-bottom:2rem;max-width:62ch">{esc(equip_page["purpose"])}</p>
    <div class="gear-grid">{gear}</div>
    <div class="btn-row" style="margin-top:1.75rem">
      <a class="btn btn--solid" href="{rel("/equip/", DEPTH)}">
        <span class="btn__label">Equipment guides</span></a>
      <a class="btn" href="{rel("/market/", DEPTH)}">
        <span class="btn__label">Second hand in the Market</span></a>
      <a class="btn" href="{rel("/shop/", DEPTH)}">
        <span class="btn__label">New stock in the Shop</span></a>
    </div>
  </div>
</section>""")

    # ── 07 Recover ─────────────────────────────────────────────────────────
    out.append(recover_section(
        depth=DEPTH,
        number="07",
        ready=data["checklists"]["steps"]["recovery"]["steps"][:5],
    ))

    # ── 08 Field Notes ───────────────────────────────────────────────────────
    cards = "".join(article_card(a, DEPTH, i, with_media=bool(a.get("image")))
                    for i, a in enumerate(latest))
    out.append(f"""<section class="section" aria-labelledby="latest-title">
  <div class="container">
    {section_label("08", "Field Notes", "Updated 24 Aug 2026", heading_id="latest-title")}
    <div class="card-grid">{cards}</div>
    <div class="btn-row" style="margin-top:2rem">
      <a class="btn" href="{rel("/news/", DEPTH)}"><span class="btn__label">All field notes</span></a>
      <a class="btn" href="{rel("/ride/", DEPTH)}"><span class="btn__label">Riding guides</span></a>
    </div>
  </div>
</section>""")

    # ── 09 Newsletter ────────────────────────────────────────────────────────
    out.append(f"""<section class="section section--soft" aria-labelledby="notes-title">
  <div class="container">
    {section_label("09", "Newsletter", "One email, occasionally", heading_id="notes-title")}
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
    "preload_image": "hero-home",
}

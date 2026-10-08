"""Homepage. Previews of the four navbar services."""

from components import (
    article_card,
    editorial_hero,
    esc,
    feature_story,
    index_row,
    newsletter_form,
    rel,
    section_label,
    workshop_callout,
)

DEPTH = 0


def build(data):
    site = data["site"]
    sections = data["sections"]
    articles = data["articles"]
    technical = data["technical"]
    market = data["market"]
    shop = data.get("shop", {"items": [], "note": ""})
    ws = data["workshop"]

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
            '<span class="btn__label">Market</span></a>'
        ),
    ))

    # ── 02 Index, vertical list ──────────────────────────────────────────────
    hrefs = {
        "ride": "/ride/", "market": "/market/",
        "shop": "/shop/", "workshop": "/workshop/",
    }
    rows = "".join(
        index_row(entry, DEPTH, hrefs[entry["slug"]], i)
        for i, entry in enumerate(sections["index"])
    )
    out.append(f"""<section class="section" id="index" aria-labelledby="index-title">
  <div class="container">
    {section_label("02", "Index", "Four ways in", heading_id="index-title")}
    <p class="lede" style="margin-bottom:2rem;max-width:62ch">
      Ride is the guides library. Market is used bikes, tools and gear.
      Shop is new spares, accessories, oils, kits, maps, navigation and audio.
      Workshop is service, inspection and rider recovery, opening soon.
    </p>
    <div class="index-list">{rows}</div>
  </div>
</section>""")

    # ── 03 Field story ───────────────────────────────────────────────────────
    out.append(f"""<section class="section section--soft" aria-labelledby="feature-title">
  <div class="container">
    {section_label("03", "Field story", featured["issue"], heading_id="feature-title")}
    {feature_story(featured, DEPTH, href=f'/field/{featured["slug"]}/')}
  </div>
</section>""")

    # ── 04 Ride preview ──────────────────────────────────────────────────────
    ride_articles = [a for a in articles["articles"] if a["section"] == "ride"][:3]
    ride_cards = "".join(article_card(a, DEPTH, i, with_media=bool(a.get("image")))
                         for i, a in enumerate(ride_articles))
    out.append(f"""<section class="section" aria-labelledby="ride-title">
  <div class="container">
    {section_label("04", "Ride", "Guides library preview", heading_id="ride-title")}
    <p class="lede" style="margin-bottom:2rem;max-width:62ch">
      Maintenance, repair, buying, PPE, tools, navigation, first aid, packing,
      terrain, weather, safety, sport and regional history, from us and from professionals.
    </p>
    <div class="card-grid">{ride_cards}</div>
    <div class="btn-row" style="margin-top:1.75rem">
      <a class="btn btn--solid" href="{rel("/ride/", DEPTH)}">
        <span class="btn__label">All ride guides</span></a>
    </div>
  </div>
</section>""")

    # ── 05 Market preview ────────────────────────────────────────────────────
    listings = "".join(
        f"""<article class="article-row" data-reveal style="--i:{i}">
      <p class="article-row__cat">{esc(l.get("category", "Used"))} {esc(l["ref"])}</p>
      <div>
        <h3 class="article-row__title">{esc(l["title"])}</h3>
        <p class="article-row__excerpt">{esc(l["detail"])}</p>
      </div>
      <p class="article-row__meta">{esc(l["meta"])}<br>{esc(l["status"])}</p>
    </article>"""
        for i, l in enumerate(market["listings"][:4])
    )
    out.append(f"""<section class="section section--soft" aria-labelledby="market-title">
  <div class="container">
    {section_label("05", "Market", "Used bikes, tools and gear", heading_id="market-title")}
    <p class="lede" style="margin-bottom:1.5rem;max-width:62ch">{esc(market["note"])}</p>
    <div class="row-list">{listings}</div>
    <div class="btn-row" style="margin-top:1.75rem">
      <a class="btn btn--solid" href="{rel("/market/", DEPTH)}">
        <span class="btn__label">All market listings</span></a>
    </div>
  </div>
</section>""")

    # ── 06 Shop preview ──────────────────────────────────────────────────────
    shop_items = "".join(
        f"""<article class="gear-item" data-reveal style="--i:{i}">
      <p class="gear-item__top"><span>{esc(g["ref"])}</span><span>{esc(g["category"])}</span></p>
      <h3 class="gear-item__name">{esc(g["name"])}</h3>
      <p class="gear-item__summary">{esc(g["summary"])}</p>
      <p class="gear-item__top" style="margin-top:1rem;padding-top:0.8rem;border-top:1px solid var(--line)">
        <span class="verdict verdict--untested">{esc(g["verdict"])}</span>
      </p>
    </article>"""
        for i, g in enumerate(shop["items"][:4])
    )
    out.append(f"""<section class="section" aria-labelledby="shop-title">
  <div class="container">
    {section_label("06", "Shop", "New goods, placeholder catalogue", heading_id="shop-title")}
    <p class="lede" style="margin-bottom:1.5rem;max-width:62ch">{esc(shop.get("note", ""))}</p>
    <div class="gear-grid">{shop_items}</div>
    <div class="btn-row" style="margin-top:1.75rem">
      <a class="btn btn--solid" href="{rel("/shop/", DEPTH)}">
        <span class="btn__label">All shop items</span></a>
    </div>
  </div>
</section>""")

    # ── 07 Workshop preview ──────────────────────────────────────────────────
    out.append(f"""<section class="section section--soft" aria-labelledby="workshop-title">
  <div class="container">
    {section_label("07", "Workshop", "Opening soon", heading_id="workshop-title")}
    <p class="lede" style="margin-bottom:2rem;max-width:64ch">{esc(ws["intro"])} {esc(ws.get("status_note", ""))}</p>
    {workshop_callout(
        depth=DEPTH,
        slot="maintain-diagram",
        caption_left="Fig. 07.1 Service points",
        caption_right="Chain drive single",
        callouts=technical["callouts"],
        title="Service, inspection and rider recovery at opening",
        body=(
            "Routine service, pre-route and pre-purchase inspection, diagnostics "
            "and suspension, plus rider recovery where a call dispatches the nearest rider. "
            "Placeholder contact " + site["brand"].get("phone", "") + ", not answered yet."
        ),
        intervals_note=(
            "Workshop and recovery are opening soon. Booking and dispatch forms are demonstrations."
        ),
        actions=(
            f'<a class="btn btn--solid" href="{rel("/workshop/", DEPTH)}">'
            '<span class="btn__label">Workshop, opening soon</span></a>'
            f'<a class="btn" href="{rel("/ride/", DEPTH)}">'
            '<span class="btn__label">Ride guides</span></a>'
        ),
    )}
  </div>
</section>""")

    # ── 08 Latest ────────────────────────────────────────────────────────────
    cards = "".join(article_card(a, DEPTH, i, with_media=bool(a.get("image")))
                    for i, a in enumerate(latest))
    out.append(f"""<section class="section" aria-labelledby="latest-title">
  <div class="container">
    {section_label("08", "Latest and field notes", "Updated 24 Aug 2026", heading_id="latest-title")}
    <div class="card-grid">{cards}</div>
    <div class="btn-row" style="margin-top:2rem">
      <a class="btn" href="{rel("/ride/", DEPTH)}"><span class="btn__label">All ride guides</span></a>
      <a class="btn" href="{rel("/market/", DEPTH)}"><span class="btn__label">Market</span></a>
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
        "Riding guides, used bikes and gear in the market, new spares and accessories in the shop, "
        "and workshop services opening soon across Kenya, Uganda, Tanzania and Rwanda."
    ),
    "dark_hero": True,
    "preload_image": "hero-home",
}

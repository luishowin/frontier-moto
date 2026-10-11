"""Homepage. Previews of the four navbar services."""

from components import (
    BTN_ARROW,
    article_card,
    editorial_hero,
    engine_study,
    esc,
    index_row,
    market_cta,
    rel,
    section_label,
)

DEPTH = 0


def build(data):
    site = data["site"]
    sections = data["sections"]
    articles = data["articles"]
    market = data["market"]
    shop = data.get("shop", {"items": [], "note": ""})
    ws = data["workshop"]

    by_slug = {a["slug"]: a for a in articles["articles"] if a.get("slug")}
    featured = by_slug[articles["featured_home"]]

    latest = sorted(
        [
            a for a in articles["articles"]
            if a["slug"] != featured["slug"]
            and a["title"] != "Nanyuki to Archers Post, surface report"
        ],
        key=lambda a: a["date"],
        reverse=True,
    )[:5]

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

    # ── 03 Ride preview ──────────────────────────────────────────────────────
    ride_articles = [a for a in articles["articles"] if a["section"] == "ride"][:3]
    ride_cards = "".join(article_card(a, DEPTH, i, with_media=bool(a.get("image")))
                         for i, a in enumerate(ride_articles))
    out.append(f"""<section class="section" aria-labelledby="ride-title">
  <div class="container">
    {section_label("03", "Ride", "Guides library preview", heading_id="ride-title")}
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

    # ── 04 Market preview ────────────────────────────────────────────────────
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
    {section_label("04", "Market", "Used bikes, tools and gear", heading_id="market-title")}
    <p class="lede" style="margin-bottom:1.5rem;max-width:62ch">{esc(market["note"])}</p>
    <div class="row-list">{listings}</div>
    <div class="btn-row" style="margin-top:1.75rem">
      <a class="btn btn--solid" href="{rel("/market/", DEPTH)}">
        <span class="btn__label">All market listings</span></a>
    </div>
  </div>
</section>""")

    # ── 05 Shop preview ──────────────────────────────────────────────────────
    shop_items = "".join(
        f"""<article class="article-card" data-reveal style="--i:{i}">
      <p class="article-card__meta">
        <span class="article-card__cat">{esc(g["category"])}</span>
        <span>{esc(g["ref"])}</span>
      </p>
      <h3 class="article-card__title">{esc(g["name"])}</h3>
      <p class="article-card__excerpt">{esc(g["summary"])}</p>
      <p class="article-card__foot"><span class="verdict verdict--{"tested" if g["verdict"] == "Field tested" else "untested"}">{esc(g["verdict"])}</span></p>
    </article>"""
        for i, g in enumerate(shop["items"][:5])
    )
    out.append(f"""<section class="section" aria-labelledby="shop-title">
  <div class="container">
    {section_label("05", "Shop", "New goods, placeholder catalogue", heading_id="shop-title")}
    <p class="lede" style="margin-bottom:1.5rem;max-width:62ch">{esc(shop.get("note", ""))}</p>
    <div class="card-grid">{shop_items}</div>
    <div class="btn-row" style="margin-top:1.75rem">
      <a class="btn btn--solid" href="{rel("/shop/", DEPTH)}">
        <span class="btn__label">Visit shop</span>{BTN_ARROW}</a>
    </div>
  </div>
</section>""")

    # ── 06 Workshop preview ──────────────────────────────────────────────────
    out.append(f"""<section class="section section--soft" aria-labelledby="workshop-title">
  <div class="container">
    {section_label("06", "Workshop", "Opening soon", heading_id="workshop-title")}
    {engine_study(
        depth=DEPTH,
        slot="maintain-engine",
        caption_left="Fig. 06.1 Single cylinder, annotated",
        caption_right="Nineteen parts named",
        title="Know the engine before you open it",
        lede=f'{ws["intro"]} {ws.get("status_note", "")}',
        body=(
            "A single cylinder four stroke with every part named, from camshaft "
            "chain and rocker arms through piston and cylinder block to clutch "
            "and kickstarter. Learn the names here and the service guides read "
            "twice as fast. " + site["brand"].get("phone", "") + " is still the "
            "placeholder contact, not answered yet."
        ),
        note=(
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

    # ── 07 Latest ────────────────────────────────────────────────────────────
    cards = "".join(article_card(a, DEPTH, i, with_media=bool(a.get("image")))
                    for i, a in enumerate(latest))
    out.append(f"""<section class="section" aria-labelledby="latest-title">
  <div class="container">
    {section_label("07", "Latest and field notes", "Updated 24 Aug 2026", heading_id="latest-title")}
    <div class="card-grid">{cards}</div>
    <div class="btn-row" style="margin-top:2rem">
      <a class="btn" href="{rel("/ride/", DEPTH)}"><span class="btn__label">All ride guides</span>{BTN_ARROW}</a>
    </div>
  </div>
</section>""")

    # ── 08 Market CTA ────────────────────────────────────────────────────────
    out.append(f"""<section class="section section--soft" aria-labelledby="notes-title">
  <div class="container">
    {section_label("08", "Visit the market", "Used bikes, tools and gear", heading_id="notes-title")}
    {market_cta(DEPTH)}
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

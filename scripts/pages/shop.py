"""
Shop.

Frontier Moto's own new product storefront: new parts, tools, riding gear,
accessories and Frontier goods sold directly by Frontier. Catalogue framing
throughout: Frontier eyebrow, price and stock state, ordering by email until
checkout exists. No cart, no payment, no fake checkout. One page, category
anchors, no runtime filtering.
"""

from components import (
    anchor_nav,
    editorial_hero,
    esc,
    newsletter_form,
    product_card,
    product_detail,
    related_cards,
    rel,
    section_label,
)

DEPTH = 1


def build(data):
    shop = data["shop"]
    products = shop["products"]
    categories = shop["categories"]
    by_ref = {p["ref"]: p for p in products}
    featured = [by_ref[r] for r in shop.get("featured", []) if r in by_ref]

    out = []

    out.append(editorial_hero(
        slot="hero-maintain",
        depth=DEPTH,
        label_accent="S",
        label="Frontier Store",
        title_lines=["Shop"],
        lede=(
            "New parts, tools, gear and accessories sold directly by Frontier "
            "Moto. Selected and stocked for riders who actually use their machines."
        ),
        compact=True,
        flat=True,
        actions=(
            '<a class="btn btn--signal" href="#catalogue">'
            '<span class="btn__label">Browse the catalogue</span></a>'
            '<a class="btn btn--ghost-light" href="#buying">'
            '<span class="btn__label">Buying guidance</span></a>'
        ),
        field=[
            ("Section", "S / Shop"),
            ("Products", f"{len(products)} in stock"),
            ("Categories", str(len(categories))),
            ("Checkout", "By email for now"),
        ],
    ))

    # ── S.1 In this shop ─────────────────────────────────────────────
    out.append(f"""<section class="section" aria-labelledby="lead-title">
  <div class="container">
    {section_label("S.1", "In this shop", "New stock, Frontier sold", heading_id="lead-title")}
    <div class="split split--wide-left">
      <div data-reveal>
        <p class="lede" style="max-width:none;color:var(--text)">
          Everything here is new and sold by Frontier Moto. Availability is stated
          on every product. There is no checkout on this site yet: ordering is by
          email with the product reference, and nothing is charged here.
        </p>
        <p class="disclaimer" style="margin-top:1.5rem">
          <strong>Opening catalogue.</strong>
          {esc(shop["note"])}
        </p>
      </div>
      <div data-reveal style="--i:1">{anchor_nav(categories)}</div>
    </div>
  </div>
</section>""")

    # ── S.2 Featured ─────────────────────────────────────────────────
    cards = "".join(product_card(p, DEPTH, i) for i, p in enumerate(featured))
    out.append(f"""<section class="section section--soft" aria-labelledby="featured-title">
  <div class="container">
    {section_label("S.2", "Featured", "Three worth a look", heading_id="featured-title")}
    <div class="product-grid">{cards}</div>
  </div>
</section>""")

    # ── S.3 Catalogue by category ────────────────────────────────────
    blocks = []
    for c in categories:
        items = [p for p in products if p.get("category") == c["slug"]]
        if not items:
            continue
        details = "".join(product_detail(p, DEPTH, i) for i, p in enumerate(items))
        blocks.append(f"""<h3 data-reveal id="{esc(c["slug"])}" style="margin:2.5rem 0 0.4rem">{esc(c["label"])}</h3>
    <p class="lede" data-reveal style="margin-bottom:1.25rem;max-width:62ch">{esc(c["blurb"])}</p>
    <div class="detail-list">{details}</div>""")
    out.append(f"""<section class="section" id="catalogue" aria-labelledby="catalogue-title">
  <div class="container">
    {section_label("S.3", "The catalogue", f"{len(products)} new products", heading_id="catalogue-title")}
    {"".join(blocks)}
  </div>
</section>""")

    # ── S.4 Buying guidance ──────────────────────────────────────────
    guides = "".join(
        f'<li><a class="tlink" href="{rel(g["href"], DEPTH)}">{esc(g["title"])}'
        f'<span class="tlink__arrow" aria-hidden="true">&#8594;</span></a>'
        f'<span class="checklist__detail">{esc(g["detail"])}</span></li>'
        for g in shop["guides"]
    )
    out.append(f"""<section class="section section--soft" id="buying" aria-labelledby="buying-title">
  <div class="container">
    {section_label("S.4", "Buying guidance", "From the people who stock it", heading_id="buying-title")}
    <div class="split split--wide-left">
      <p class="lede" data-reveal style="max-width:none">
        Short guidance from the workshop bench: what to measure before ordering,
        what fits what, and what stays home. Every product above links to the
        longer guide where one exists.
      </p>
      <ul data-reveal style="--i:1;display:grid;gap:1rem">{guides}</ul>
    </div>
    <div class="btn-row" style="margin-top:1.75rem">
      <a class="btn btn--solid" href="{rel("/market/", DEPTH)}">
        <span class="btn__label">Second hand in the Market</span></a>
      <a class="btn" href="{rel("/equip/", DEPTH)}">
        <span class="btn__label">Equipment evaluations</span></a>
    </div>
  </div>
</section>""")

    # ── Related ──────────────────────────────────────────────────────
    related = [
        {"number": "01", "title": "Market", "blurb": "Used machines, parts and tools sold by their owners.", "href": "/market/"},
        {"number": "02", "title": "Equip", "blurb": "Equipment judged against heat, dust, load and price.", "href": "/equip/"},
        {"number": "03", "title": "Workshop", "blurb": "Service, inspection and repair.", "href": "/workshop/"},
    ]
    out.append(f"""<section class="section" aria-labelledby="related-title">
  <div class="container">
    {section_label("S.5", "Adjacent sections", "Where this leads", heading_id="related-title")}
    {related_cards(related, DEPTH)}
  </div>
</section>""")

    out.append(f"""<section class="section section--soft" aria-labelledby="notes-title">
  <div class="container">
    {section_label("S.6", "Newsletter", "One email, occasionally", heading_id="notes-title")}
    {newsletter_form(DEPTH)}
  </div>
</section>""")

    return "\n".join(out)


def page_meta(site, data):
    shop = data["shop"]
    return {
        "href": "/shop/",
        "out": "shop/index.html",
        "depth": DEPTH,
        "slug": "shop",
        "title": "Shop",
        "description": (
            "New parts, tools, riding gear, accessories and Frontier goods sold "
            "directly by Frontier Moto. Stock stated plainly, ordering by email."
        ),
        "dark_hero": True,
        "preload_image": "hero-maintain",
        "schema": {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": f'Shop | {site["brand"]["name"]}',
            "description": "New products sold directly by Frontier Moto.",
            "url": site["site"]["base_url"].rstrip("/") + "/shop/",
            "isPartOf": {
                "@type": "WebSite",
                "name": site["brand"]["name"],
                "url": site["site"]["base_url"],
            },
            "about": [{"@type": "Thing", "name": c["label"]} for c in shop["categories"]],
        },
    }

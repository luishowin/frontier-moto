"""
Market.

The used and secondary marketplace: second hand motorcycles, used parts and
pre owned tools sold by their owners, not by Frontier Moto. Classified
framing throughout: condition and inspection before price, known faults
stated, contact by email until a seller inbox exists. No checkout, no cart,
no commission. One page, category anchors, no runtime filtering.
"""

from components import (
    anchor_nav,
    editorial_hero,
    esc,
    listing_card,
    listing_detail,
    newsletter_form,
    related_cards,
    rel,
    section_label,
    topic_nav,
)

DEPTH = 1


def build(data):
    market = data["market"]
    listings = market["listings"]
    categories = market.get("categories", [])
    supply = market["supply"]

    cats = []
    for c in categories:
        items = [l for l in listings if l.get("category") == c["slug"]]
        if items:
            cats.append((c, items))

    out = []

    out.append(editorial_hero(
        slot="hero-market",
        depth=DEPTH,
        label_accent="M",
        label="Used Market",
        title_lines=["Market"],
        lede=(
            "Used motorcycles, parts and tools from riders, mechanics and "
            "sellers. Every listing is second hand and sold by its owner, "
            "not by Frontier Moto."
        ),
        compact=True,
        flat=True,
        field=[
            ("Section", "M / Market"),
            ("Listings", f"{len(listings)} live"),
            ("Categories", str(len(cats))),
            ("Checkout", "None, contact seller"),
        ],
    ))

    # ── M.1 In this market ─────────────────────────────────────────────
    out.append(f"""<section class="section" aria-labelledby="lead-title">
  <div class="container">
    {section_label("M.1", "In this market", f"{len(listings)} second hand listings", heading_id="lead-title")}
    <div class="split split--wide-left">
      <div data-reveal>
        <p class="lede" style="max-width:none;color:var(--text)">
          A place to discover real used machines, components and workshop
          equipment. Condition is stated before price, known faults are listed,
          and anything we have only seen rather than inspected is marked as such.
        </p>
        <p class="disclaimer" style="margin-top:1.5rem">
          <strong>Sample listings, honest layout.</strong>
          Listings below use realistic sample prices to establish the layout.
          There is no checkout on this site. Frontier Moto takes no commission
          and holds no stock. Until seller contact exists, enquiries go through
          the email address in the footer with the listing reference.
        </p>
      </div>
      <div data-reveal style="--i:1">{anchor_nav(categories)}</div>
    </div>
  </div>
</section>""")

    # ── M.2 How this market works ──────────────────────────────────────
    standards = "".join(
        f'<li><span class="fact-list__mark">&#43;</span><span>{esc(s)}</span></li>'
        for s in supply["standards"]
    )
    out.append(f"""<section class="section section--soft" aria-labelledby="how-title">
  <div class="container">
    {section_label("M.2", "How this market works", "Used and secondary", heading_id="how-title")}
    <p class="lede" style="margin-bottom:2rem;max-width:64ch">{esc(supply["status"])}</p>
    <div class="split">
      <div data-reveal>
        <h3 style="margin-bottom:1rem">The standard</h3>
        <ul class="fact-list fact-list--marks">{standards}</ul>
      </div>
      <div data-reveal style="--i:1">
        <h3 style="margin-bottom:1rem">What a fair price looks like</h3>
        <p class="lede" style="max-width:none" id="price">{esc(supply["price_note"])}</p>
      </div>
    </div>
  </div>
</section>""")

    # ── M.3 Listings by category ───────────────────────────────────────
    blocks = []
    for c, items in cats:
        cards = "".join(listing_card(l, DEPTH, i) for i, l in enumerate(items))
        blocks.append(f"""<h3 data-reveal id="{esc(c["slug"])}" style="margin:2.5rem 0 0.4rem">{esc(c["label"])}</h3>
    <p class="lede" data-reveal style="margin-bottom:1.25rem;max-width:62ch">{esc(c["blurb"])}</p>
    <div class="listing-grid">{cards}</div>""")
    out.append(f"""<section class="section" id="listings" aria-labelledby="listings-title">
  <div class="container">
    {section_label("M.3", "Listings", f"{len(listings)} second hand", heading_id="listings-title")}
    {"".join(blocks)}
  </div>
</section>""")

    # ── M.4 Listing detail ─────────────────────────────────────────────
    details = "".join(listing_detail(l, DEPTH, i) for i, l in enumerate(listings))
    out.append(f"""<section class="section section--soft" id="inspect" aria-labelledby="detail-title">
  <div class="container">
    {section_label("M.4", "Listing detail", "Condition first", heading_id="detail-title")}
    <p class="lede" style="margin-bottom:2rem;max-width:64ch">
      Full notes on each listing: what it is today, what is known to be wrong,
      and how far the inspection went. Anything marked seen only deserves a full
      inspection before money moves.
    </p>
    <div class="detail-list">{details}</div>
    <div class="btn-row" style="margin-top:1.75rem">
      <a class="btn btn--solid" href="{rel("/shop/", DEPTH)}">
        <span class="btn__label">New stock in the Shop</span></a>
      <a class="btn" href="{rel("/workshop/", DEPTH)}">
        <span class="btn__label">Book a pre purchase inspection</span></a>
    </div>
  </div>
</section>""")

    # ── Related ────────────────────────────────────────────────────────
    related = [
        {"number": "01", "title": "Shop", "blurb": "New parts, tools and gear sold directly by Frontier Moto.", "href": "/shop/"},
        {"number": "02", "title": "Equip", "blurb": "Equipment judged against heat, dust, load and price.", "href": "/equip/"},
        {"number": "03", "title": "Workshop", "blurb": "Service, inspection and repair.", "href": "/workshop/"},
    ]
    out.append(f"""<section class="section" aria-labelledby="related-title">
  <div class="container">
    {section_label("M.5", "Adjacent sections", "Where this leads", heading_id="related-title")}
    {related_cards(related, DEPTH)}
  </div>
</section>""")

    out.append(f"""<section class="section section--soft" aria-labelledby="notes-title">
  <div class="container">
    {section_label("M.6", "Newsletter", "One email, occasionally", heading_id="notes-title")}
    {newsletter_form(DEPTH)}
  </div>
</section>""")

    return "\n".join(out)


def page_meta(site, data):
    market = data["market"]
    return {
        "href": "/market/",
        "out": "market/index.html",
        "depth": DEPTH,
        "slug": "market",
        "title": "Market",
        "description": (
            "Used motorcycles, second hand parts and pre owned tools from riders "
            "and sellers across East Africa. Condition and inspection stated "
            "plainly, priced by sellers, no checkout."
        ),
        "dark_hero": True,
        "preload_image": "hero-market",
        "schema": {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": f'Market | {site["brand"]["name"]}',
            "description": (
                "Second hand motorcycles, used parts and pre owned tools. "
                "Sold by owners, not by Frontier Moto."
            ),
            "url": site["site"]["base_url"].rstrip("/") + "/market/",
            "isPartOf": {
                "@type": "WebSite",
                "name": site["brand"]["name"],
                "url": site["site"]["base_url"],
            },
            "about": [{"@type": "Thing", "name": c["label"]} for c in market.get("categories", [])],
        },
    }

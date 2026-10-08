"""
Shop. Commerce layout: promos, pick by bike make, pick by category,
popular products, about plus guides. Placeholder catalogue, nothing for sale.

No product detail pages exist, so tiles and product cards are not links.
The only anchors point at sections on this page or at real site pages,
which keeps check.py link resolution green.
"""

from components import (
    article_card,
    editorial_hero,
    esc,
    image,
    newsletter_form,
    rel,
    section_label,
)

DEPTH = 1

CATEGORY_IMAGES = {
    "Spare parts": "feature-chain",
    "Rider accessories": "market-gear",
    "Bike accessories": "index-equip",
    "Oils": "hero-maintain",
    "Kits": "hero-maintain",
    "Maps": "index-navigate",
    "Navigation": "hero-news",
    "Audio": "index-ride",
}


def _promo_card(p, i, large=False):
    badge = f'<p class="promo__badge">{esc(p["badge"])}</p>' if p.get("badge") else ""
    cls = "promo promo--large" if large else "promo"
    return f"""<article class="{cls}" data-reveal style="--i:{i}">
  <div class="promo__text">
    {badge}
    <h3 class="promo__title">{esc(p["title"])}</h3>
    <p class="promo__detail">{esc(p["detail"])}</p>
    <p class="promo__price">{esc(p["price"])} <s>{esc(p.get("old_price", ""))}</s></p>
  </div>
  <div class="promo__media">{image(p["image"], DEPTH, sizes=p.get("sizes", "100vw"))}</div>
</article>"""


def build(data):
    site = data["site"]
    shop = data["shop"]
    articles = [a for a in data["articles"]["articles"] if a["section"] == "shop"][:2]

    out = []
    n = "03"

    out.append(editorial_hero(
        slot="hero-market",
        depth=DEPTH,
        label_accent=n,
        label="Shop",
        title_lines=["Shop"],
        lede=shop["note"],
        compact=True,
        flat=True,
        field=[
            ("Section", f"{n} / Shop"),
            ("Categories", f'{len(shop["categories"])} listed'),
            ("Status", "Placeholder"),
            ("Updated", "24 AUG 2026"),
        ],
    ))

    # ── Promos ─────────────────────────────────────────────────────────────
    promos = shop.get("promos", [])
    promo_html = ""
    if len(promos) >= 4:
        promo_html = (
            _promo_card(promos[0], 0, large=True)
            + _promo_card(promos[1], 1)
            + _promo_card(promos[2], 2)
            + _promo_card(promos[3], 3)
        )
    elif promos:
        promo_html = "".join(_promo_card(p, i) for i, p in enumerate(promos))
    out.append(f"""<section class="section" aria-labelledby="promo-title">
  <div class="container">
    {section_label(f"{n}.1", "Featured", "Placeholder prices", heading_id="promo-title")}
    <div class="promo-grid">{promo_html}</div>
    <p class="disclaimer" style="margin-top:1.5rem;max-width:none">
      <strong>Nothing for sale yet.</strong>
      Prices are placeholders in Kenya shillings. Cart controls below are
      demonstrations and place no order.
    </p>
  </div>
</section>""")

    # ── Pick by bike make ──────────────────────────────────────────────────
    groups = "".join(
        f'<div class="makes__group" data-reveal style="--i:{i}">'
        f'<p class="makes__letter">{esc(g["letter"])}</p>'
        f'<ul><li>' + "</li><li>".join(esc(m) for m in g["makes"]) + "</li></ul></div>"
        for i, g in enumerate(shop.get("brands", []))
    )
    out.append(f"""<section class="section section--soft" aria-labelledby="makes-title">
  <div class="container">
    {section_label(f"{n}.2", "Pick by bike make", f'{sum(len(g["makes"]) for g in shop.get("brands", []))} makes', heading_id="makes-title")}
    <div class="makes-grid">{groups}</div>
    <p class="scroll-hint" style="margin-top:1.25rem">Fitment lists per make arrive with opening stock. Makes above guide what the catalogue will cover first.</p>
  </div>
</section>""")

    # ── Pick by category ───────────────────────────────────────────────────
    counts = {}
    for item in shop.get("items", []):
        counts[item["category"]] = counts.get(item["category"], 0) + 1
    tiles = "".join(
        f"""<article class="cat-tile" data-reveal style="--i:{i}">
      <div class="cat-tile__text">
        <h3 class="cat-tile__title">{esc(c)}</h3>
        <p class="cat-tile__count">{counts.get(c, 0)} placeholder item(s)</p>
      </div>
      <div class="cat-tile__media">{image(CATEGORY_IMAGES.get(c, "hero-market"), DEPTH, sizes="(max-width: 960px) 50vw, 20vw")}</div>
    </article>"""
        for i, c in enumerate(shop.get("categories", []))
    )
    out.append(f"""<section class="section" id="categories" aria-labelledby="cats-title">
  <div class="container">
    {section_label(f"{n}.3", "Pick by category", f'{len(shop.get("categories", []))} categories', heading_id="cats-title")}
    <div class="cat-grid">{tiles}</div>
  </div>
</section>""")

    # ── Popular products ───────────────────────────────────────────────────
    products = "".join(
        f"""<article class="product" data-reveal style="--i:{i}">
      <p class="product__stock">{esc(g.get("stock", "Opening soon"))}</p>
      <div class="product__media">{image(g.get("image", "hero-market"), DEPTH, sizes="(max-width: 960px) 50vw, 22vw")}</div>
      <h3 class="product__name">{esc(g["name"])}</h3>
      <p class="product__cat">{esc(g["category"])} {esc(g["ref"])}</p>
      <p class="product__price">{esc(g.get("price", ""))} <s>{esc(g.get("old_price", ""))}</s></p>
      <button class="product__cart" type="button" disabled aria-label="{esc(g["name"])}, demo only, not for sale">
        <span aria-hidden="true">&#128722;</span>
      </button>
    </article>"""
        for i, g in enumerate(shop.get("items", [])[:4])
    )
    out.append(f"""<section class="section section--soft" id="popular" aria-labelledby="popular-title">
  <div class="container">
    {section_label(f"{n}.4", "Popular products", "Demo catalogue", heading_id="popular-title")}
    <div class="product-grid">{products}</div>
    <p class="scroll-hint" style="margin-top:1.25rem">Cart controls are disabled demonstrations. Nothing is added, stored or ordered.</p>
  </div>
</section>""")

    # ── About plus guides ──────────────────────────────────────────────────
    guides = "".join(article_card(a, DEPTH, i, with_media=False) for i, a in enumerate(articles))
    out.append(f"""<section class="section" aria-labelledby="about-title">
  <div class="container">
    {section_label(f"{n}.5", "About the shop", "What this becomes", heading_id="about-title")}
    <div class="split split--wide-left">
      <div data-reveal>
        <p class="lede" style="max-width:none;color:var(--text)">{esc(shop.get("about", shop["note"]))}</p>
        <div class="btn-row" style="margin-top:1.75rem">
          <a class="btn btn--solid" href="{rel("/market/", DEPTH)}"><span class="btn__label">Used market instead</span></a>
          <a class="btn" href="{rel("/workshop/", DEPTH)}"><span class="btn__label">Workshop, opening soon</span></a>
        </div>
      </div>
      <div class="card-grid" data-reveal style="--i:1">{guides}</div>
    </div>
  </div>
</section>""")

    out.append(f"""<section class="section section--soft" aria-labelledby="notes-title">
  <div class="container">
    {section_label(f"{n}.6", "Field notes", "One email, occasionally", heading_id="notes-title")}
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
        "description": shop["note"][:280],
        "dark_hero": True,
        "preload_image": "hero-market",
        "schema": {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": f'Shop | {site["brand"]["name"]}',
            "description": shop["note"],
            "url": site["site"]["base_url"].rstrip("/") + "/shop/",
            "isPartOf": {
                "@type": "WebSite",
                "name": site["brand"]["name"],
                "url": site["site"]["base_url"],
            },
        },
    }

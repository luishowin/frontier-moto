"""Legal single page. Minimal terms, privacy, credits. Short, honest, no filler."""

from components import esc, newsletter_form, rel, section_label

LEGAL_DEPTH = 1
NOTFOUND_DEPTH = 0


def legal(data):
    site = data["site"]
    brand = site["brand"]
    return f"""<section class="section page-top" aria-labelledby="legal-title">
  <div class="container">
    {section_label("10", "Legal", "In works, nothing for sale", heading_id="legal-title")}
    <h1>Terms, privacy and design credit</h1>
    <p class="lede" style="margin-top:1rem">
      The website is purely in the works. Nothing is selling. Market listings and shop
      items are design placeholders. Workshop and rider recovery are opening soon.
      All content is design work by {esc(brand.get("design_credit", "Luis Howin Maina."))}
    </p>

    <div class="prose" style="margin-top:2.5rem">
      <h2 id="terms">Terms of service</h2>
      <p>
        This site is a design in progress for a commercial platform selling used two
        wheelers, used tools and biking goods in the Market, and new spares, accessories,
        oils, kits, maps, navigation systems and audio in the Shop. No checkout exists
        and no sale, booking or dispatch happens through this site today.
      </p>
      <p>
        Guides in Ride describe what worked for us or for contributing professionals on
        specific machines in specific conditions. Riding, maintenance and roadside
        decisions remain yours. No guide can account for the state of your motorcycle
        or the road you are on. Where a procedure carries real risk we say so.
      </p>
      <p>
        Workshop service and rider recovery are opening soon. The phone
        {esc(brand.get("phone", "+254 700 000 000"))} is a placeholder and is not answered.
        Booking and recovery forms are front end demonstrations that transmit nothing.
        Frontier Moto is not an emergency service. If anyone is injured, contact local
        emergency services first.
      </p>

      <h2 id="privacy">Privacy policy</h2>
      <p>
        Minimal version. This site sets no cookies, runs no analytics and has no backend.
        The Workshop, newsletter and contact forms are demonstrations: entries stay in
        your browser and are discarded when you close the tab.
      </p>
      <p>
        Fonts are requested from Google Fonts, which means your browser contacts
        fonts.googleapis.com and fonts.gstatic.com when the page loads. Nothing else is
        requested from a third party. Email to {esc(brand["email"])} is the only contact
        that reaches anyone. A full notice will replace this text once a service actually
        collects anything.
      </p>

      <h2 id="credits">Credits</h2>
      <p>
        Design work and placeholder content by {esc(brand.get("design_credit", "Luis Howin Maina."))}
        Photographs on this site are reference imagery standing in for commissioned work.
        None of them were taken by Frontier Moto and none were taken in East Africa, so
        captions and alt text describe what is in the frame and do not name a place.
      </p>
      <p>
        The service point diagram on the Ride and home pages is drawn for this site.
        Every image slot is listed in the image manifest
        with its source, dimensions and description.
      </p>
      <p>
        Type is Archivo and Roboto Mono, both open licensed. The site is static HTML, CSS
        and a small amount of JavaScript, with no framework and no tracking.
      </p>

      <h2 id="contact">Contact</h2>
      <p>
        Placeholder phone <a href="tel:+254700000000">{esc(brand.get("phone", "+254 700 000 000"))}</a>
        ({esc(brand.get("phone_note", "not answered"))}). Planned hours {esc(brand.get("hours", ""))}.
        Base {esc(brand.get("base", ""))}.
        Corrections welcome, particularly on route notes and service intervals, which
        change. Write to
        <a href="mailto:{esc(brand["email"])}">{esc(brand["email"])}</a>.
      </p>
    </div>
  </div>
</section>

<section class="section section--soft" aria-labelledby="notes-title">
  <div class="container">
    {section_label("10.1", "Field notes", "One email, occasionally", heading_id="notes-title")}
    {newsletter_form(LEGAL_DEPTH)}
  </div>
</section>"""


def legal_meta(site):
    return {
        "href": "/legal/",
        "out": "legal/index.html",
        "depth": LEGAL_DEPTH,
        "slug": None,
        "title": "Terms, privacy and design credit",
        "description": (
            "Minimal terms and privacy for Frontier Moto: in works, nothing for sale, "
            "workshop opening soon, design by Luis Howin Maina."
        ),
        "dark_hero": False,
    }


def not_found(data):
    site = data["site"]
    nav = "".join(
        f'<li><a href="{rel(n["href"], NOTFOUND_DEPTH)}">{esc(n["label"])}</a></li>'
        for n in site["nav"]
    )
    return f"""<section class="section page-top" aria-labelledby="nf-title">
  <div class="container">
    {section_label("404", "Not found", "Wrong turn", heading_id="nf-title")}
    <h1>This page is not here</h1>
    <p class="lede" style="margin-top:1rem;max-width:52ch">
      The address does not match anything on the site. It may have moved, or it may
      never have existed. The sections below are the whole of it.
    </p>

    <div class="btn-row" style="margin-top:2rem">
      <a class="btn btn--solid" href="{rel("/", NOTFOUND_DEPTH)}">
        <span class="btn__label">Home</span></a>
      <a class="btn btn--signal" href="{rel("/market/", NOTFOUND_DEPTH)}">
        <span class="btn__label">Market</span></a>
    </div>

    <nav aria-label="All sections" style="margin-top:3rem">
      <p class="mono" style="color:var(--text-muted);margin-bottom:0.75rem">All sections</p>
      <ul class="topic-nav">{nav}</ul>
    </nav>
  </div>
</section>"""


def not_found_meta(site):
    return {
        "href": "/404.html",
        "out": "404.html",
        "depth": NOTFOUND_DEPTH,
        "slug": None,
        "title": "Page not found",
        "description": "The address does not match anything on Frontier Moto.",
        "dark_hero": False,
        "noindex": True,
    }

"""Legal placeholders and the not-found page. Short, honest, no filler."""

from components import esc, newsletter_form, rel, section_label

LEGAL_DEPTH = 1
NOTFOUND_DEPTH = 0


def legal(data):
    site = data["site"]
    return f"""<section class="section page-top" aria-labelledby="legal-title">
  <div class="container">
    {section_label("10", "Legal", "Placeholder text", heading_id="legal-title")}
    <h1>Legal, privacy and credits</h1>
    <p class="lede" style="margin-top:1rem">
      Frontier Moto is not yet trading as a registered business, so the pages that would
      normally carry company details carry placeholders instead. Everything below says
      what will go here rather than pretending it is already in force.
    </p>

    <div class="prose" style="margin-top:2.5rem">
      <h2 id="terms">Terms</h2>
      <p>
        Guides on this site describe what worked for us on specific machines in specific
        conditions. Riding, maintenance and roadside decisions remain yours. Where a
        procedure carries real risk we say so, but no guide can account for the state of
        your motorcycle or the road you are on.
      </p>
      <p>
        Recovery is not an operating service. Nothing on this site dispatches assistance,
        and the request form is a front end demonstration that transmits nothing.
      </p>

      <h2 id="privacy">Privacy</h2>
      <p>
        This site sets no cookies, runs no analytics and has no backend. The forms on the
        Recovery, Workshop and newsletter sections are demonstrations: entries stay in
        your browser and are discarded when you close the tab.
      </p>
      <p>
        Fonts are requested from Google Fonts, which means your browser contacts
        fonts.googleapis.com and fonts.gstatic.com when the page loads. Nothing else is
        requested from a third party. A full privacy notice will replace this text once
        there is a service that actually collects anything.
      </p>

      <h2 id="credits">Credits</h2>
      <p>
        Photographs on this site are reference imagery standing in for commissioned work.
        None of them were taken by Frontier Moto and none were taken in East Africa, so
        captions and alt text describe what is in the frame and do not name a place. Where
        a picture shows a machine, a tool or a road, read it as an illustration of the
        subject rather than a record of somewhere we have been.
      </p>
      <p>
        The one exception is the service point diagram on the Maintain and home pages,
        which is drawn for this site. Every image slot is listed in the image manifest
        with its source, dimensions and description.
      </p>
      <p>
        Type is Archivo and Roboto Mono, both open licensed. The site is static HTML, CSS
        and a small amount of JavaScript, with no framework and no tracking.
      </p>

      <h2 id="contact">Contact</h2>
      <p>
        Corrections are welcome, particularly on route notes and service intervals, which
        change. Write to
        <a href="mailto:{esc(site["brand"]["email"])}">{esc(site["brand"]["email"])}</a>.
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
        "title": "Legal, privacy and credits",
        "description": (
            "Terms, privacy and credits for Frontier Moto, including a plain statement "
            "that recovery dispatch is not an operating service."
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

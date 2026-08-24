"""
Workshop.

Scope first, then services, then how to prepare a machine, then how the work is
actually quoted and recorded, then the booking control. The practical detail is
the trust building, not adjectives about quality.
"""

from components import (
    image,
    checklist,
    esc,
    editorial_hero,
    newsletter_form,
    related_cards,
    rel,
    section_label,
)

DEPTH = 1


def build(data):
    site = data["site"]
    ws = data["workshop"]

    out = []

    out.append(editorial_hero(
        slot="hero-workshop",
        depth=DEPTH,
        label_accent="07",
        label="Workshop",
        title_lines=["Workshop"],
        lede=(
            "Service, inspection and diagnostics for the machines people actually ride "
            "here. Commuters and working bikes as readily as touring machines."
        ),
        compact=True,
        flat=True,
        actions=(
            '<a class="btn btn--ghost-light" href="#services">'
            '<span class="btn__label">Service categories</span></a>'
            '<a class="btn btn--signal" href="#booking">'
            '<span class="btn__label">Booking enquiry</span></a>'
        ),
        field=[
            ("Section", "07 / Workshop"),
            ("Services", f'{len(ws["services"])} categories'),
            ("Records", "Written, every job"),
            ("Updated", "24 AUG 2026"),
        ],
    ))

    # ── 07.1 Scope ───────────────────────────────────────────────────────────
    handles = "".join(
        f'<li><span class="fact-list__mark">&#43;</span><span>{esc(h)}</span></li>'
        for h in ws["handles"]
    )
    refers = "".join(
        f'<li><span class="fact-list__mark">&#8594;</span><span>{esc(h)}</span></li>'
        for h in ws["not_handled"]
    )

    out.append(f"""<section class="section" aria-labelledby="scope-title">
  <div class="container">
    {section_label("07.1", "What the workshop handles", "And what it does not", heading_id="scope-title")}
    <p class="lede" style="margin-bottom:2rem;max-width:64ch">{esc(ws["intro"])}</p>
    <div class="split">
      <div data-reveal>
        <h3 style="margin-bottom:1rem">Handled here</h3>
        <ul class="fact-list fact-list--marks">{handles}</ul>
      </div>
      <div data-reveal style="--i:1">
        <h3 style="margin-bottom:1rem">Referred out</h3>
        <ul class="fact-list fact-list--marks">{refers}</ul>
        <p class="checklist__note" style="margin-top:1rem">
          Saying this up front saves you a journey. Where we refer a job out, we will
          name someone who does it properly rather than leave you to find out.
        </p>
      </div>
    </div>
  </div>
</section>""")

    # ── 07.2 Services ────────────────────────────────────────────────────────
    services = "".join(
        f"""<article class="service" data-reveal style="--i:{i}">
      <p class="service__ref">{esc(s["ref"])}</p>
      <h3 class="service__name">{esc(s["name"])}</h3>
      <p class="service__summary">{esc(s["summary"])}</p>
      <ul class="fact-list" style="margin-top:auto;padding-top:1rem">
        <li><span class="fact-list__k">Time</span><span>{esc(s["time"])}</span></li>
        <li><span class="fact-list__k">You get</span><span>{esc(s["output"])}</span></li>
      </ul>
    </article>"""
        for i, s in enumerate(ws["services"])
    )

    out.append(f"""<section class="section section--soft" id="services" aria-labelledby="services-title">
  <div class="container">
    {section_label("07.2", "Service and inspection", f'{len(ws["services"])} categories', heading_id="services-title")}
    <div class="service-grid">{services}</div>
    <p class="scroll-hint" style="margin-top:1.25rem">
      Times are typical rather than promised, and depend on what the machine turns out
      to need. Prices are quoted per job after the bike is seen.
    </p>
  </div>
</section>""")

    # ── 07.3 Preparation ─────────────────────────────────────────────────────
    out.append(f"""<section class="section" aria-labelledby="prep-title">
  <div class="container">
    {section_label("07.3", "Preparing your motorcycle", "Five things, before you arrive", heading_id="prep-title")}
    <div class="split split--wide-left">
      <div data-reveal>{checklist(data["checklists"]["checklists"]["workshop-prep"], 0)}</div>
      <div data-reveal style="--i:1">
        <h3>Why the symptom matters more than the diagnosis</h3>
        <p style="margin-top:0.8rem;font-size:var(--t-small);color:var(--text-muted);max-width:52ch">
          A rider who says the bike is misfiring has already narrowed the search, often
          in the wrong direction. A rider who says it loses power above four thousand
          revolutions when the engine is hot, and only in the rain, has handed the
          workshop most of the answer.
        </p>
        <p style="margin-top:0.8rem;font-size:var(--t-small);color:var(--text-muted);max-width:52ch">
          Write it down before you set off. By the time you arrive you will have stopped
          noticing the detail that matters.
        </p>
        <div class="btn-row" style="margin-top:1.5rem">
          <a class="btn" href="{rel("/maintain/", DEPTH)}">
            <span class="btn__label">Maintenance guides</span></a>
        </div>
      </div>
    </div>
  </div>
</section>""")

    # ── 07.4 How we work ─────────────────────────────────────────────────────
    practical = "".join(
        f'<li><span class="fact-list__k">{esc(p["k"])}</span><span>{esc(p["v"])}</span></li>'
        for p in ws["practical"]
    )
    out.append(f"""<section class="section section--soft" aria-labelledby="how-title">
  <div class="container">
    {section_label("07.4", "How the work is quoted and recorded", "Practical detail", heading_id="how-title")}
    <div class="split split--wide-left">
      <ul class="fact-list" data-reveal>{practical}</ul>
      <figure data-reveal style="--i:1;margin:0">
        {image("workshop-bay", DEPTH, sizes="(max-width: 960px) 100vw, 40vw")}
        <figcaption class="workshop-callout__figcaption" style="border:1px solid var(--line);border-top:none">
          <span>Work in progress on the stand</span><span>Reference photograph</span>
        </figcaption>
      </figure>
    </div>
  </div>
</section>""")

    # ── 07.5 Booking ─────────────────────────────────────────────────────────
    options = "".join(f'<option>{esc(s["name"])}</option>' for s in ws["services"])

    out.append(f"""<section class="section" id="booking" aria-labelledby="booking-title">
  <div class="container">
    {section_label("07.5", "Booking enquiry", "Demonstration only", heading_id="booking-title")}
    <div class="split">
      <div data-reveal>
        <p class="lede" style="max-width:none">
          Tell us the machine and the symptom and we can usually say on the enquiry
          whether it is a morning job, a day job, or something we would refer out.
        </p>
        <p class="disclaimer" style="margin-top:1.5rem;max-width:none">
          <strong>This booking form is a front end demonstration.</strong>
          It is not connected to a calendar, an inbox or a booking system. Nothing you
          enter is stored or sent, and no appointment is created. Until a real endpoint
          is connected, use the email address in the footer.
        </p>
      </div>

      <form data-reveal style="--i:1" data-demo-form novalidate
            aria-labelledby="booking-form-title"
            data-demo-message="Demonstration only. No booking was created and nothing was sent. To reach the workshop for real, use the email address in the footer.">
        <h3 id="booking-form-title" style="margin-bottom:1.25rem">Enquiry details</h3>
        <div class="form-grid">
          <div class="field">
            <label for="bk-name">Name</label>
            <input id="bk-name" name="name" type="text" required autocomplete="name">
            <p class="field__error" aria-live="polite"></p>
          </div>
          <div class="field">
            <label for="bk-contact">How to reach you</label>
            <input id="bk-contact" name="contact" type="text" required
                   placeholder="Email or phone">
            <p class="field__error" aria-live="polite"></p>
          </div>
          <div class="field field--full">
            <label for="bk-service">Service</label>
            <select id="bk-service" name="service" required>
              <option value="">Choose one</option>
              {options}
              <option>Not sure, please advise</option>
            </select>
            <p class="field__error" aria-live="polite"></p>
          </div>
          <div class="field field--full">
            <label for="bk-machine">Motorcycle</label>
            <input id="bk-machine" name="machine" type="text" required
                   placeholder="Make, model, year, approximate mileage">
            <p class="field__error" aria-live="polite"></p>
          </div>
          <div class="field field--full">
            <label for="bk-notes">Symptom or reason for the visit</label>
            <textarea id="bk-notes" name="notes"
                      placeholder="When it happens, at what speed, hot or cold, and what changes it"></textarea>
            <span class="hint">Optional, but it is the most useful thing you can give us.</span>
          </div>
        </div>
        <div class="btn-row" style="margin-top:1.5rem">
          <button class="btn btn--solid" type="submit">
            <span class="btn__label">Send demonstration enquiry</span>
          </button>
        </div>
        <p class="form-status" role="status" aria-live="polite"></p>
      </form>
    </div>
  </div>
</section>""")

    related = [
        {"number": "01", "title": "Maintain", "blurb": "Intervals, diagnostics and what to check yourself.", "href": "/maintain/"},
        {"number": "02", "title": "Market", "blurb": "Buying guidance and pre-purchase inspection.", "href": "/market/"},
        {"number": "03", "title": "Recovery", "blurb": "What to do before the machine reaches a workshop.", "href": "/recovery/"},
    ]
    out.append(f"""<section class="section section--soft" aria-labelledby="related-title">
  <div class="container">
    {section_label("07.6", "Adjacent sections", "Where this leads", heading_id="related-title")}
    {related_cards(related, DEPTH)}
  </div>
</section>""")

    out.append(f"""<section class="section" aria-labelledby="notes-title">
  <div class="container">
    {section_label("07.7", "Field notes", "One email, occasionally", heading_id="notes-title")}
    {newsletter_form(DEPTH)}
  </div>
</section>""")

    return "\n".join(out)


def page_meta(site, data):
    ws = data["workshop"]
    return {
        "href": "/workshop/",
        "out": "workshop/index.html",
        "depth": DEPTH,
        "slug": "workshop",
        "title": "Workshop",
        "description": (
            "Routine service, pre-route and pre-purchase inspection, diagnostics and "
            "suspension setup, with the scope, preparation and quoting practice stated "
            "plainly."
        ),
        "dark_hero": True,
        "preload_image": "hero-workshop",
        "schema": {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": f'Workshop | {site["brand"]["name"]}',
            "url": site["site"]["base_url"].rstrip("/") + "/workshop/",
            "description": ws["intro"],
            "mainEntity": {
                "@type": "ItemList",
                "name": "Workshop service categories",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": i + 1,
                        "name": s["name"],
                        "description": s["summary"],
                    }
                    for i, s in enumerate(ws["services"])
                ],
            },
        },
    }

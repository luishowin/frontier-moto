"""
Recovery.

The one page on the site where speed of comprehension outranks composition. It
opens with the instruction rather than a photograph, because a rider reading it
is already stopped somewhere they would rather not be and may be on a poor
connection. Order: safety, then location and machine, then what this service
actually is and is not, then the request control, then what to do instead.

Nothing here dispatches anything. That is stated in the masthead, again beside
the form, and again in the form's own response.
"""

from components import (
    image,
    checklist,
    esc,
    newsletter_form,
    related_cards,
    rel,
    section_label,
    steps,
)

DEPTH = 1


def build(data):
    site = data["site"]
    seq = data["checklists"]["steps"]["recovery"]
    roadside = data["checklists"]["steps"]["roadside"]

    out = []

    # ── Masthead. Instruction first, above the fold, no large image. ─────────
    out.append(f"""<section class="alert-masthead">
  <div class="container">
    <p class="alert-masthead__label"><span>09</span><span>Recovery</span></p>
    <h1 class="alert-masthead__title">Stranded?<br>Start here.</h1>
    <p class="alert-masthead__purpose">
      Work down this page in order. The first three steps matter whether or not any
      recovery service is available to you.
    </p>

    <div class="alert-masthead__first">
      <h2>Before anything else</h2>
      <p><strong>If anyone is injured, contact local emergency services now.</strong>
      Frontier Moto is not an emergency service and cannot reach you.</p>
      <p>If nobody is hurt: get yourself and the machine fully clear of moving traffic,
      make yourself visible, and stand off the road on the uphill side. The motorcycle
      can wait. Read the six steps below before you contact anyone.</p>
    </div>

    <div class="alert-masthead__actions btn-row">
      <a class="btn btn--solid" href="#request"><span class="btn__label">Request form</span></a>
      <a class="btn" href="#coverage"><span class="btn__label">What this service is</span></a>
      <a class="btn" href="#alternatives"><span class="btn__label">If no service is available</span></a>
    </div>
  </div>
</section>""")

    # ── 09.1 Immediate steps ─────────────────────────────────────────────────
    out.append(f"""<section class="section" aria-labelledby="first-title">
  <div class="container">
    {section_label("09.1", roadside["title"], "Do this first", heading_id="first-title")}
    <p class="lede" style="margin-bottom:1.5rem;max-width:62ch">{esc(roadside["note"])}</p>
    {steps(roadside)}
  </div>
</section>""")

    # ── 09.2 Information checklist ───────────────────────────────────────────
    out.append(f"""<section class="section section--soft" aria-labelledby="ready-title">
  <div class="container">
    {section_label("09.2", "Have this ready", seq["number"], heading_id="ready-title")}
    <p class="lede" style="margin-bottom:1.5rem;max-width:62ch">{esc(seq["note"])}</p>
    {steps(seq)}
  </div>
</section>""")

    # ── 09.3 Coverage and process, stated plainly ────────────────────────────
    out.append(f"""<section class="section" id="coverage" aria-labelledby="coverage-title">
  <div class="container">
    {section_label("09.3", "What this service is", "Read before requesting", heading_id="coverage-title")}
    <div class="split">
      <div data-reveal>
        <p class="disclaimer" style="max-width:none">
          <strong>Recovery dispatch is not live.</strong>
          There is no vehicle on standby, no coverage map, no response time and no
          number that reaches a driver. The form on this page is a front end
          demonstration of how a request would work. It transmits nothing, and nobody
          is notified when you submit it.
        </p>
        <p style="margin-top:1.25rem;font-size:var(--t-small);color:var(--text-muted);max-width:60ch">
          We would rather show the process and say plainly that it is not running than
          publish a phone number that no one answers. When recovery does operate, the
          coverage area, hours and contact details will be stated here in full, and the
          form will say where a request has gone.
        </p>
      </div>
      <div data-reveal style="--i:1">
        <p class="mono" style="color:var(--text-muted);margin-bottom:0.75rem">
          How a request would be handled
        </p>
        <ul class="fact-list">
          <li><span class="fact-list__k">Step 1</span>
            <span>Request received with location, machine and fault.</span></li>
          <li><span class="fact-list__k">Step 2</span>
            <span>Call back to confirm position and safety status.</span></li>
          <li><span class="fact-list__k">Step 3</span>
            <span>Roadside fix attempted first where the fault allows it.</span></li>
          <li><span class="fact-list__k">Step 4</span>
            <span>Transport to a workshop where it does not.</span></li>
          <li><span class="fact-list__k">Step 5</span>
            <span>Cost agreed before anything is loaded, not after.</span></li>
          <li><span class="fact-list__k">Status</span>
            <span><strong>Not operating.</strong> This is a description, not an offer.</span></li>
        </ul>
      </div>
    </div>
  </div>
</section>""")

    # ── 09.4 The request control ─────────────────────────────────────────────
    out.append(f"""<section class="section section--soft" id="request" aria-labelledby="request-title">
  <div class="container">
    {section_label("09.4", "Recovery request", "Demonstration only", heading_id="request-title")}
    <div class="split">
      <div data-reveal>
        <p class="lede" style="max-width:none">
          Filling this in will not summon anyone. It is here so the request process is
          visible and so the fields tell you what information is worth gathering while
          you wait.
        </p>
        <p class="disclaimer" style="margin-top:1.5rem;max-width:none">
          <strong>This form does not send anything.</strong>
          There is no backend connected to it. Nothing you type is stored, transmitted
          or seen by anyone, and no recovery request is created.
        </p>
      </div>

      <form data-reveal style="--i:1" data-demo-form novalidate
            aria-labelledby="request-form-title"
            data-demo-message="Demonstration only. Nothing was sent, nothing was stored, and no recovery request exists. If you need help now, contact local emergency services or a workshop you can reach directly.">
        <h3 id="request-form-title" style="margin-bottom:1.25rem">Request details</h3>

        <div class="form-grid">
          <div class="field field--full">
            <label for="rq-location">Where are you</label>
            <input id="rq-location" name="location" type="text" required
                   placeholder="Road number, direction, last town passed">
            <span class="hint">A screenshot of your map position is worth more than a description.</span>
            <p class="field__error" aria-live="polite"></p>
          </div>

          <div class="field">
            <label for="rq-machine">Motorcycle</label>
            <input id="rq-machine" name="machine" type="text" required
                   placeholder="Make, model, approximate year">
            <p class="field__error" aria-live="polite"></p>
          </div>

          <div class="field">
            <label for="rq-rolls">Does the rear wheel turn</label>
            <select id="rq-rolls" name="rolls" required>
              <option value="">Choose one</option>
              <option>Yes, it can be rolled</option>
              <option>No, it must be lifted</option>
              <option>Not sure</option>
            </select>
            <p class="field__error" aria-live="polite"></p>
          </div>

          <div class="field field--full">
            <label for="rq-fault">What happened</label>
            <textarea id="rq-fault" name="fault" required
                      placeholder="What it was doing, at what speed, what it sounded like, what it does now"></textarea>
            <span class="hint">Describe the symptom rather than your diagnosis.</span>
            <p class="field__error" aria-live="polite"></p>
          </div>

          <div class="field field--full">
            <label for="rq-safety">Safety status</label>
            <select id="rq-safety" name="safety" required>
              <option value="">Choose one</option>
              <option>Safe, off the road, daylight</option>
              <option>Safe, off the road, getting dark</option>
              <option>Exposed position, close to traffic</option>
              <option>Someone is injured</option>
            </select>
            <span class="hint">If someone is injured, contact local emergency services rather than this form.</span>
            <p class="field__error" aria-live="polite"></p>
          </div>
        </div>

        <div class="btn-row" style="margin-top:1.5rem">
          <button class="btn btn--signal" type="submit">
            <span class="btn__label">Submit demonstration request</span>
          </button>
        </div>
        <p class="form-status" role="status" aria-live="polite"></p>
      </form>
    </div>
  </div>
</section>""")

    # ── 09.5 Alternatives ────────────────────────────────────────────────────
    out.append(f"""<section class="section" id="alternatives" aria-labelledby="alt-title">
  <div class="container">
    {section_label("09.5", "If no service is available", "Which is currently always", heading_id="alt-title")}
    <div class="split split--wide-left">
      <ul class="fact-list fact-list--marks" data-reveal>
        <li><span class="fact-list__mark">01</span>
          <span><strong>Ask at the nearest stage.</strong> Riders working a route every day
          know who repairs what, who has a pickup, and what a fair price for the lift is.
          It is the fastest route to help almost anywhere in the region.</span></li>
        <li><span class="fact-list__mark">02</span>
          <span><strong>Try the roadside fix first.</strong> A large share of stops are a
          puncture, a chain, a fuse or a loose connection. The Survive and Maintain
          sections cover each of those in the order worth checking them.</span></li>
        <li><span class="fact-list__mark">03</span>
          <span><strong>Call someone who knows your route.</strong> This is why the
          check in time is on the pre-ride list. Someone expecting you is the difference
          between being late and being missing.</span></li>
        <li><span class="fact-list__mark">04</span>
          <span><strong>Move the machine, not yourself.</strong> If the bike will limp,
          limp it to a town, a stage or a fuel station. Somewhere with people, light and
          space is a far better place to solve this than a shoulder.</span></li>
        <li><span class="fact-list__mark">05</span>
          <span><strong>If it is getting dark, stop trying to fix it.</strong> Secure the
          machine, get yourself somewhere safe, and return in daylight. Almost nothing
          mechanical is worth working on beside a road at night.</span></li>
      </ul>
      <div data-reveal style="--i:1">
        {checklist(data["checklists"]["checklists"]["contacts"], 0)}
      </div>
    </div>
    <figure data-reveal style="margin:2.5rem 0 0">
      {image("hero-recovery", DEPTH, sizes="(max-width: 1320px) 100vw, 1320px")}
      <figcaption class="workshop-callout__figcaption" style="border:1px solid var(--line);border-top:none">
        <span>Off the tarmac, no other vehicle in sight</span><span>Reference photograph</span>
      </figcaption>
    </figure>
  </div>
</section>""")

    # ── Cross links ──────────────────────────────────────────────────────────
    related = [
        {"number": "01", "title": "Survive", "blurb": "Breakdowns, preparedness and roadside resilience.", "href": "/survive/"},
        {"number": "02", "title": "Maintain", "blurb": "Diagnostics and the faults that stop a bike outright.", "href": "/maintain/"},
        {"number": "03", "title": "Workshop", "blurb": "Repair and inspection once the machine is off the road.", "href": "/workshop/"},
    ]
    out.append(f"""<section class="section section--soft" aria-labelledby="related-title">
  <div class="container">
    {section_label("09.6", "Adjacent sections", "Where this leads", heading_id="related-title")}
    {related_cards(related, DEPTH)}
  </div>
</section>""")

    out.append(f"""<section class="section" aria-labelledby="notes-title">
  <div class="container">
    {section_label("09.7", "Field notes", "One email, occasionally", heading_id="notes-title")}
    {newsletter_form(DEPTH)}
  </div>
</section>""")

    return "\n".join(out)


def page_meta(site, data):
    roadside = data["checklists"]["steps"]["roadside"]["steps"]
    return {
        "href": "/recovery/",
        "out": "recovery/index.html",
        "depth": DEPTH,
        "slug": "recovery",
        "title": "Recovery",
        "description": (
            "What to do when the ride stops: immediate safety steps, the information to "
            "gather, and an honest account of what recovery support does and does not "
            "currently cover."
        ),
        "dark_hero": False,
        "schema": {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": "What to do when a motorcycle breaks down on the road",
            "description": (
                "The order to work in after a motorcycle stops: clear the carriageway, "
                "become visible, check people before the machine, then gather location, "
                "machine and fault information."
            ),
            "step": [
                {"@type": "HowToStep", "position": i + 1, "name": s["title"], "text": s["detail"]}
                for i, s in enumerate(roadside)
            ],
        },
    }

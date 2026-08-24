# Frontier Moto

Source for Frontier Moto, an East African motorcycle competence, support and
culture brand. Riding skills, route notes, roadside survival, maintenance,
equipment, workshop services and recovery guidance for riders across Kenya,
Uganda, Tanzania and Rwanda.

**Live:** https://luishowin.github.io/frontier-moto/

Static HTML/CSS/JS, served by GitHub Pages from `docs/`. No framework, no npm
dependency, no runtime JavaScript for content. The HTML in `docs/` is generated
from `content/` and committed, so hosting, SEO and local preview work like any
hand written static site.

## Structure

```
docs/                       the published site (GitHub Pages serves from here)
  index.html                homepage
  ride/ navigate/ survive/ maintain/ market/ news/   section pages
  workshop/ recovery/       the two pages with their own structure
  field/<slug>/             article detail pages
  legal/ 404.html           support pages
  robots.txt sitemap.xml site.webmanifest favicon.svg favicon.ico
  assets/css/index.css      tokens, then components, in one file
  assets/js/index.js        theme, pinned header, menu, reveal, demo forms
  assets/img/               GENERATED image plates + MANIFEST.md

content/                    the SOURCE. Never edit docs/*.html by hand
  site.json                 brand, nav, footer, base URL
  sections.json             the six index entries and the six section pages
  articles.json             every article preview, plus full bodies for three
  checklists.json           checklists and numbered step sequences
  technical.json            routes, service intervals, component callouts
  market.json               equipment, listings, buying guides
  workshop.json             services, scope, quoting practice
  images.json               every image slot with dimensions and alt text

scripts/
  build.py                  content + components -> docs/*.html
  build_images.py           images.json -> SVG plates + MANIFEST.md
  check.py                  the verification pass
  shell.py                  head, header, menu overlay, footer
  components.py             the component library
  pages/                    one module per page kind
```

## Build

Python 3.11 or newer. No packages to install.

```bash
python scripts/build_images.py
python scripts/build.py
python scripts/check.py
```

Preview with `python -m http.server 8127 --directory docs`, or the `site`
configuration in `.claude/launch.json`.

`check.py` exits non-zero on any failure and asserts, across every page: internal
links resolve, images carry alt text and explicit dimensions, titles and
descriptions are unique and present, canonical and social metadata exist, JSON-LD
parses, heading levels never skip, `aria-labelledby` targets exist, every form is
marked as a demonstration, the Recovery page states that dispatch is not live,
and no em dash appears anywhere.

## Editing

Never hand edit `docs/*.html`; it is regenerated on every build. Change
`content/*.json` for copy and data, `scripts/` for structure and markup, and
`docs/assets/` for the stylesheet and script.

**After changing `index.css` or `index.js`, bump `ASSET_VERSION` in
`scripts/shell.py` and rebuild.** Pages serves static assets with a long cache
life and there is no build step hashing filenames, so without the bump a deploy
can leave readers on the previous stylesheet.

**To move to a real domain:** change `site.base_url` in `content/site.json`, add
a `CNAME` file in `docs/` containing the bare domain, rebuild, then point DNS at
GitHub Pages and set the domain under Settings, Pages. Canonicals, Open Graph
URLs and the sitemap all derive from that one value.

## Design system

- **Two families only.** Archivo carries display and body; Roboto Mono carries
  the wordmark, labels, specifications and every technical figure. A grotesque
  against a mono gives real contrast, one smaller font request, and less to
  download on a weak connection.
- **The wordmark is a monospace for a structural reason.** `FRON`, `TIER` and
  `MOTO` are all four characters, so a monospace makes the three stacked rows
  measure identically and the cube stays square at 48% tracking. Each row carries
  a negative right margin equal to the tracking, which removes the trailing space
  letter-spacing adds after the final character.
- **One accent.** Signal orange is for Recovery, focus rings and active state,
  and nothing else. It measures about 3:1 on bone, so it is never body text:
  `--signal-ink` is the darkened form for type, and orange fills always take
  ink-black labels at about 7.6:1. Recovery is also marked by a beacon glyph and
  border weight, so it never depends on colour alone.
- **The hairline rule is the structural device, not the card.** Content sits in
  cells divided by 1px lines. No shadows, no gradients other than the hero scrim,
  which is functional, and no corner radius above 2px.
- **One type scale.** Every size comes from the `--t-*` tokens. No ad hoc sizes.
- **Layout.** Full bleed sections, a 1320px `.container` inside. Soft sections
  alternate down the page.
- **Motion.** `[data-reveal]` with an `--i` stagger, one shared observer in
  `index.js`. Never add a per-page observer. Reduced motion shows everything
  immediately and constructs no observer at all.
- **Copy.** No em dashes. `check.py` enforces it.

## Components

Presentation lives in `scripts/components.py` and `scripts/shell.py`; content
lives in `content/`. Pages compose components and never write their own version
of a card, a spec list or a checklist.

| Component | Where |
| --- | --- |
| `SiteHeader`, `FrontierWordmark`, `PrimaryNav`, `RecoveryAction`, `SiteFooter` | `shell.py` |
| `SectionLabel` | `components.section_label` |
| `EditorialHero` | `components.editorial_hero` |
| `IndexCard` | `components.index_card` |
| `FeatureStory` | `components.feature_story` |
| `ArticleCard` | `components.article_card` |
| `ArticleListRow` | `components.article_row` |
| `TechnicalSpecList` | `components.spec_list` |
| `Checklist` | `components.checklist`, `components.steps` |
| `WorkshopCallout` | `components.workshop_callout` |
| `RecoveryBanner` | `components.recovery_banner` |
| `NewsletterForm` | `components.newsletter_form` |

The shell is generated rather than copied per page on purpose. The
`nanyuki-holiday-home` README names hand editing the nav in every file as a known
maintenance problem; there is one copy of it here.

## Images

Every slot in `content/images.json` is generated as an SVG plate by
`build_images.py`: brand palette, technical grid, crop marks, a caption and a
slot reference. They are placeholders that look deliberate, they weigh about 5 KB
each, and they sit inside real `<img>` markup with dimensions, lazy loading and
alt text. `docs/assets/img/MANIFEST.md` lists every slot with the ratio,
dimensions and alt text a photograph needs, so replacing one is a file swap.

`maintain-diagram` is artwork rather than a stand-in and should be kept.

## What is not real yet

Everything below needs business data or an integration before it means anything.
None of it is implied to work in the meantime.

- **Canonical domain.** `site.base_url` currently points at the GitHub Pages URL,
  which is where the site actually lives. Move it to the real domain when there
  is one, so canonicals do not advertise an address that does not resolve.
- **Recovery.** No dispatch, no coverage area, no response time, no phone number.
  The page says so three times and the request form transmits nothing.
- **Workshop booking.** No calendar, no inbox, no booking system.
- **Newsletter.** No list and no endpoint.
- **Photography.** All image slots are generated plates.
- **Social channels.** None open, so none are linked.
- **Schema.** Organization only. Not LocalBusiness, which needs a real street
  address, and no telephone, opening hours, ratings or reviews.

## Deploy

Already configured: Pages serves the `main` branch from `/docs`, so pushing a
rebuilt `docs/` publishes. Rebuild before you commit, or the published site will
not match `content/`.

All internal links are relative and the manifest uses relative paths, so the
site works unchanged from the project sub-path it is served from today and from
a domain root later.

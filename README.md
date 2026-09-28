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
  assets/img/               photographs as AVIF + JPEG, one SVG plate, MANIFEST.md

assets/photos/              SOURCE photographs, not published

content/                    the SOURCE. Never edit docs/*.html by hand
  site.json                 brand, nav, footer, base URL
  sections.json             the six index entries and the six section pages,
                            plus the optional reference plate some carry
  articles.json             every article preview, plus full bodies for three
  checklists.json           checklists and numbered step sequences
  technical.json            routes, service intervals, component callouts
  market.json               equipment, listings, buying guides
  workshop.json             services, scope, quoting practice
  images.json               every image slot: caption and alt text by hand,
                            dimensions and widths written by build_photos.py

scripts/
  build.py                  content + components -> docs/*.html
  build_photos.py           assets/photos/ -> AVIF + JPEG derivatives (Pillow)
  build_images.py           images.json -> the remaining SVG artwork
  check.py                  the verification pass
  check_contrast.py         text over photographs, measured (Pillow)
  shell.py                  head, header, menu overlay, footer
  components.py             the component library
  pages/                    one module per page kind
```

## Build

Python 3.11 or newer. Building the site needs no packages:

```bash
python scripts/build_images.py
python scripts/build.py
python scripts/check.py
```

The two image scripts need Pillow, and are an asset step rather than a build
step: they run when the photographs change and their output is committed, so a
clone can rebuild the whole site with a bare Python.

```bash
python -m pip install Pillow
python scripts/build_photos.py
python scripts/check_contrast.py
```

Preview with `python -m http.server 8127 --directory docs`, or the `site`
configuration in `.claude/launch.json`.

`check.py` exits non-zero on any failure and asserts, across every page: internal
links resolve, images carry alt text and explicit dimensions, titles and
descriptions are unique and present, canonical and social metadata exist, JSON-LD
parses, heading levels never skip, `aria-labelledby` targets exist, every form is
marked as a demonstration, the Recovery page states that dispatch is not live,
and no em dash appears anywhere. It also resolves every `srcset` candidate, so a
photograph that is referenced but missing fails the build rather than the page.

`check_contrast.py` is the other half of that. It composites each photograph
under the same scrim gradient the CSS applies, samples the region the copy
occupies, and reports the worst contrast ratio against every text colour painted
there. It is a separate script because it needs Pillow, and it exists because
swapping flat plates for photographs broke contrast on all eleven cases without
changing a line of markup. The worst was 1.09:1, on a hero label over a snow
field. None of it was visible as a broken page.

## Editing

Never hand edit `docs/*.html`; it is regenerated on every build. Change
`content/*.json` for copy and data, `scripts/` for structure and markup, and
`docs/assets/` for the stylesheet and script.

**After changing `index.css` or `index.js`, bump `ASSET_VERSION` in
`scripts/shell.py` and rebuild.** Pages serves static assets with a long cache
life and there is no build step hashing filenames, so without the bump a deploy
can leave readers on the previous stylesheet.

**To change a photograph,** drop the file into `assets/photos/`, point the slot
at it in the `PLAN` table in `scripts/build_photos.py`, then run
`build_photos.py`, `build.py` and `check_contrast.py`. Update the caption and
alt text in `content/images.json` afterwards: alt text is content and does not
travel with a file, so a swapped picture with the old alt text is a lie about
what is on the page.

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
- **One accent.** Safety yellow (`#EED202`) is for the primary market action,
  focus rings and active state, and nothing else. It measures about 1.3:1 on
  bone, so it is never body text: `--signal-ink` is the darkened form for type,
  and yellow fills always take ink-black labels at about 12.4:1. The header
  action is also marked by an arrow glyph and border weight, so it never
  depends on colour alone. On light surfaces the focus ring uses the darkened
  ink form, which clears 4.5:1 where the yellow cannot.
- **The hairline rule is the structural device, not the card.** Content sits in
  cells divided by 1px lines. No shadows, no corner radius above 2px, and no
  decorative gradient. The only gradients in the stylesheet are the two hero
  scrims, the index card scrim and the technical grid pattern, all four of which
  do a job.
- **Text over a photograph is measured, not judged by eye.** Every scrim value
  and every dim tone painted over a picture comes out of `check_contrast.py`,
  set to the lightest value that still clears 4.5:1 so the photograph stays as
  visible as legibility allows. Re-measure when the photographs change.
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
| Responsive image, `<picture>` and hero preload | `components.image`, `components.srcset`, `components.preload_link` |

The shell is generated rather than copied per page on purpose. The
`nanyuki-holiday-home` README names hand editing the nav in every file as a known
maintenance problem; there is one copy of it here.

## Photography

`assets/photos/` holds the source photographs. `build_photos.py` crops each one
to its slot ratio around a stated focal point, writes an AVIF and a JPEG at each
responsive width, strips camera metadata, and rewrites the measured dimensions
back into `content/images.json` so the markup and the files cannot disagree.
Pages emit a `<picture>`: AVIF first, JPEG behind it. The homepage hero costs
about 27 KB on a phone.

Two rules the mapping follows, both of them content rules rather than technical
ones:

- **Nothing is upscaled.** Most sources are about 1170px wide, so slot
  dimensions are whatever the photograph can honestly deliver after cropping.
  Workshop and Recovery draw on portrait sources and their heroes are 687px
  wide, which is soft on a large screen. A soft hero is worse than a small one,
  and both were the most apt pictures available for those pages.
- **The focal point is set per photograph.** A centre crop decapitates riders.

`maintain-diagram` stays a generated SVG. Its six numbered callouts are keyed to
`content/technical.json`, so no photograph can replace it. `build_images.py`
skips any slot a photograph now serves.

### Provenance

The photographs are stock and reference imagery supplied for the build. **They
are not Frontier Moto field photographs and none of them were taken in East
Africa.** Captions and alt text therefore describe what is in the frame and
never name a place: a picture of an Australian escarpment does not get captioned
as the Old Naivasha Road. Two of the supplied files were not brought into the
repository at all. `map-hero.avif` is a British tourist map with "The Isle of
Wight" and "Ventnor" legible in it, which cannot be presented as an East African
route, and `workshop.avif` was surplus once every slot was filled.

Confirm the licence for each file before treating the site as published work.
`docs/assets/img/MANIFEST.md` lists every slot with its source file, dimensions,
generated widths and alt text.

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
- **Photography.** Stock and reference imagery standing in for commissioned
  work. Not shot in East Africa, not licensed for this use as far as this repo
  knows, and captioned accordingly. See Provenance above.
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

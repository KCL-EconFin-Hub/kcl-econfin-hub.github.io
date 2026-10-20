# Developing the site

This file explains how the site is put together and why, for anyone changing
its structure or design. To update content only, see [README.md](README.md).

## Guiding principle

**Keep the design and the code as simple and elegant as possible.** Each
choice below follows from that. Before adding anything (a dependency, a build
step, a JavaScript feature, a new data file, a one-off style), check whether
the same result can come from the YAML, a template or the existing tokens.

The design follows a few widely used ideas:

- **Rules over instances** ([Every Layout](https://every-layout.dev/rudiments/axioms/)):
  a small set of rules applied everywhere, not page-by-page tweaks.
- **Fluid scales** ([Utopia](https://utopia.fyi/)): type and spacing grow
  smoothly with the screen instead of jumping at breakpoints.
- **Content first, do less** (GOV.UK's design principles): if something
  doesn't help a visitor, leave it out.
- **WCAG 2.2 AA accessibility.**

## Stack

- **Jekyll on GitHub Pages, built by GitHub.** Pushing to `main` publishes the
  site. There's no CI config, no Node, no bundler and no plugins beyond what
  the `github-pages` gem provides.
- **One stylesheet** ([assets/css/style.css](assets/css/style.css)): plain
  CSS, no Sass and no media queries.
- **One script** ([assets/js/calendar.js](assets/js/calendar.js)), used only
  for the "Add to calendar" button. The site works fully without JavaScript.
- **One font family:** Archivo (variable), loaded from Google Fonts.
- **Optional analytics:** Umami's tracker, on the live site only; see
  [Analytics](#analytics).

GitHub Pages pins **Jekyll 3.10** and an old Liquid. This rules out a few
newer idioms; see [Liquid gotchas](#liquid-gotchas).

## File map

```
_config.yml            site URL; the build settings
_data/site.yml         palette + every piece of text on the site
_data/people.yml       co-champions (shown in the sidebar)
_data/events.yml       events
_data/software.yml     software entries
_layouts/default.html  the page shell: top bar, banner, content + sidebar, footer
_includes/
  sidebar.html         co-champions, contact and related-links boxes
  person.html          one person: photo, linked name, job title
  section_head.html    an h2 (or h3) plus optional intro paragraph
  event_lists.html     splits events into `upcoming` and `past`
  event.html           one event
  software_item.html   one software card
favicon.ico            browser-tab icon (16, 32, 48 px)
apple-touch-icon.png   home-screen icon (180 px)
tools/
  fetch_kcl_people.py  scrapes the hub's people list from the KCL page into a
                       CSV plus photos (not part of the site; see its docstring)
index.html             overview  (/)
events.html            events    (/events/)
software.html          software  (/software/)
```

## Content lives in YAML, never in templates

The templates contain **no user-facing text**. Every heading, paragraph,
label and button caption comes from `_data/site.yml`. This lets
non-developers edit the site and keeps the wording in one place. When you
add a feature, put its text in `site.yml` too.

`site.yml` has one block per page (`home`, `events_page`, `software_page`),
plus shared `labels` and the `sidebar`. A page picks its block in front matter:

```yaml
---
layout: default
permalink: /events/
section: events_page
---
```

The layout reads `site.data.site[page.section]` (default `home`) for the
page's `page_title`, `heading` (default: the hub `title`), `tagline` and
`show_affiliation`. The page body then reads the rest of its block. The
banner, sidebar and footer belong to the layout, so every page gets them
automatically.

**Adding a page:** create `newpage.html` with a `permalink` and `section`, add
a matching block to `site.yml` and add an entry to `nav:`.

**Optional parts hide themselves.** For example, "Featured software" on the
overview disappears when nothing is `featured`, and a sidebar box disappears
when its list is empty. Prefer this to configuration flags. In Liquid an
empty list is still truthy, so test `list.size > 0`, not `list`.

## Design system

Everything visual comes from a handful of tokens. New styles should use
them, not new literal values.

### Colour: the palette in `site.yml`

Every colour is defined once, in `palette:` at the top of `_data/site.yml`.
The layout writes it out as CSS custom properties:

```html
<style>:root { --accent: #C8102E; --link: #1D3461; ... }</style>
```

**`style.css` must not contain colour literals.** Use `var(--name)` only. If
you need a new colour, add it to the palette with a comment saying where
it's used.

| Token | Role |
| --- | --- |
| `accent` | KCL red: rules, banner dots, badges, mail icons, focus ring |
| `accent-tint` | pale wash behind event badges |
| `link` | navy: links, names, buttons |
| `ink` | slate: top bar, banner, footer |
| `on-ink` | text on `ink`, `accent`, `link` and `kind-*` |
| `text` / `muted` | body text and headings / secondary text |
| `line` | borders, dividers, list bullets |
| `panel` | grey sidebar boxes, event date blocks |
| `background` | page, cards, title box |
| `kind-<name>` | one per software kind |

**Contrast:** every text/background pair in use passes 4.5:1 (WCAG AA). If
you change a colour, re-check it, for example with WebAIM's contrast checker.
The two pairs that fail, `accent` and `muted` on `ink`, are only used
decoratively (banner dots, a hairline). For that reason the focus ring
switches to `on-ink` inside the top bar and footer.

**Software kinds** are coloured through one variable. Each card sets
`style="--kind: var(--kind-<kind>, var(--accent))"`, and the card's top
border, badge and links use `var(--kind)`. To add a kind, add a label under
`software_page.kinds` and a `kind-<name>` palette entry. No CSS change is
needed.

### Type

- **Archivo in two cuts,** echoing KCL's pairing of a bold condensed
  grotesque for headings with a plainer grotesque for text. Headings, names
  and the wordmark use `font-stretch: var(--heading-stretch)` (80%) and
  weight 700. Body text uses `var(--text-stretch)` (95%) and weight 400. Both
  come from one variable-font request.
- **A fluid modular scale,** `--step--1` to `--step-5`. It runs from base
  16px with ratio 1.2 on a 360px screen to base 18px with ratio 1.25 on a
  1240px screen, generated with the [Utopia](https://utopia.fyi/type/calculator/)
  method. Every `font-size` uses a step.

### Space

A fluid space scale, `--space-3xs` to `--space-2xl` (multiples of the base
size), plus `--gutter` for the page edges. Every margin, padding and gap uses
one of these. To regenerate either scale, change the endpoints and
recompute with Utopia's calculator.

### Shape

- Square corners everywhere. The only round things are photos, mail icons
  and list bullets.
- **The red rule** (`--rule`, 4px) is the recurring accent: the active nav
  item, event date blocks, card tops, the footer.
- White content on the page, grey `panel` boxes in the sidebar.

## Visual identity

The site takes its structure from the
[KCL Finance Hub page](https://www.kcl.ac.uk/research/finance-hub-informatics):

- a banner with the page title in a white box
- condensed bold headings
- content beside a sidebar of grey boxes (people with round photos, contact
  addresses with red mail icons, related departments)
- research questions as a bulleted list
- navy links on a white page, with a slate top bar and footer

It must still read as the hub's own site, not an official King's page. One
line of small print in the footer (`footer_note` in `site.yml`) says so; the
design does the rest:

- **No KCL logo, crest, red logo block, mega-menu, audience links
  (Students/Staff/Alumni), institutional footer or social bar.** The hub has
  its own wordmark: the `mark` initials in a red square plus `short_title`.
- **The banner is a CSS dot-matrix pattern**, not a photo. It nods to the LED
  ticker on the KCL page without reusing it.
- **The affiliation appears only as plain text** (above the overview heading
  and in the footer).
- **Archivo stands in for KCL's own fonts.** KCL's Kings Bureau Grotesque is
  licensed to the university and must not be used here.

Keep these properties when changing the design.

### Icons

`favicon.ico` and `apple-touch-icon.png` are the wordmark's square: white
`EF` in Archivo (80% width, bold) on `accent` red. They're images, so they
don't follow the palette or `mark` automatically. If either changes,
regenerate them:

1. Render the mark at 512×512, e.g. a headless-Chrome screenshot of a page
   with `font-size: 370px` and the new colours.
2. Scale it to 180px for `apple-touch-icon.png`, and to 16, 32 and 48px PNGs
   packed into `favicon.ico`.

The layout links both, so browsers don't probe for other file names.

## Layout

```
┌ top bar: wordmark ··························· nav ┐
├ banner (dots) ┌ title box ┐ ─────────────────────┤
├ main ──────────────────────────┬ sidebar ────────┤
│ sections…                      │ panels…         │
├ footer ────────────────────────┴─────────────────┤
```

- One centred column (`.wrap`, max 75rem, `--gutter` padding) shared by the
  top bar, banner, page and footer.
- **No media queries.** Everything adapts on its own:
  - **Content and sidebar:** `.page` is a wrapping flex row. `main` has
    `flex: 999` and `min-inline-size: 60%`, and the sidebar has
    `flex-basis: 22rem`. The sidebar sits beside the content while the
    content keeps at least 60% of the width, and drops below it otherwise
    (Every Layout's "Sidebar"). `align-content: flex-start` stops wrapped
    rows from spreading out on tall screens.
  - **Cards:** `repeat(auto-fill, minmax(min(100%, 17rem), 1fr))`.
  - **Nav:** wraps below the wordmark when there's no room.
- `body` is a flex column and `.page` has `flex: 1`, so the footer sits at
  the bottom of short pages.

When testing narrow widths with headless Chrome, note that it won't lay out
below 500px whatever `--window-size` says. Load the page in a 390px-wide
`<iframe>` instead.

## Events

[`_includes/event_lists.html`](_includes/event_lists.html) defines `upcoming`
and `past`:

- **Upcoming:** events in progress (start date past, `end_date` today or
  later), then future events, then undated events.
- **Past:** finished events, most recent first.

**Dates may be quoted or not.** YAML reads `"2026-11-12"` as text but
`2026-11-12` as a Date, and Jekyll 3.10's `sort` crashes the whole build when
it meets both. So the include never sorts events directly:

1. It normalises each date with `| date: '%Y-%m-%d'`.
2. It builds a text key `"YYYY-MM-DD|position"` for each event (`undated`
   sorts after every date).
3. It sorts the keys as text and looks each event up again by its position.

**Times may be quoted or not.** YAML reads an unquoted `14:00` as the base-60
number 840. `event.html` spots a time that's just a number and turns it back
into `14:00`.

**"Today" means the build date.** GitHub Pages rebuilds only on a push, so
the split can lag by a few days in a quiet week. If that matters, add a
scheduled GitHub Action that rebuilds the site daily. That's the one extra
piece of infrastructure worth adding.

**Links come from a key list.** `event.html` loops over
`'url,registration_url,video_link,speaker_url,paper_url'` and labels each
link from `site.yml` → `labels`. To add a link type, extend the list and add
a label. `software_item.html` works the same way, and there **the first link
present is styled as the primary button** (`.card .link:first-child`), so the
order of that list sets priority.

**Calendar button:** event details travel in `data-` attributes, so quotes
and line breaks in titles cannot break the `onclick`. `calendar.js` writes:

- If `time` contains a clock time: a timed event in *floating* local time (no
  timezone; the audience is in London). It uses the first two `H:MM` times
  in the text, so "14:00 – 15:30 (UK time)" works. A start time on its own
  gets a one-hour slot.
- Otherwise (no time, or free text like "2pm–3pm"): an all-day event from
  `date` to `end_date`, with the exclusive `DTEND` that the iCalendar spec
  requires.

## Robustness

The content files are edited by hand, so the templates tolerate common
slips rather than breaking the build or the layout:

- **Escaping:** plain-text fields from `events.yml`, `software.yml`,
  `people.yml` and the sidebar lists are written with `| escape`, so
  "P<NP" or "R&D" shows as typed. Long fields (`description`, intros) go
  through `markdownify`. Short `site.yml` strings are output raw; they're
  maintained text, and that allows the odd bit of HTML.
- **Long words:** `overflow-wrap: anywhere` on `body` breaks long URLs and
  names instead of widening the page on phones.
- **Missing or odd fields:** a missing optional field drops out of the
  layout. An unknown software `kind` gets its raw name as the badge and the
  accent colour. A software entry with no `kind` gets no badge. A single
  string in `authors` or `tags` works as well as a list.

## People

`people.yml` has two lists:

- **`leads`** (the co-champions), rendered in the sidebar by `sidebar.html`.
- **`members`**, which together with `leads` makes up the **People** grid at
  the bottom of the overview.

Both places use the same `person.html` include. The CSS lays it out as a
small photo beside the text (`.panel .person`) or as a large centred card
(`.people-grid .person`).

The grid is sorted by surname with the same text-key technique as events.
Each person gets the key `surname name|position`, where the surname is the
last word of `name` unless `sort_as` is given. The keys are sorted, and each
person is looked up again by position. The co-champions are in the grid
automatically, so each person is listed once in the data.

Photos live in `assets/img/people/` as square images (320×320 is enough),
and CSS crops them to a circle. A person without a `photo` gets a grey
circle in its place, so the grid stays aligned.

## Liquid gotchas

These come from Jekyll 3.10 and the Liquid version GitHub Pages uses:

- **An empty data file is `false`, not `[]`.** Always read a list with a
  default: `site.data.events | default: empty_list`, where
  `empty_list = '' | split: ','`. The `[]` placeholder in the empty data
  files keeps them valid YAML.
- **An empty list is truthy,** so `{% if list %}` doesn't hide anything.
  Test `list.size > 0`.
- **No expressions in `include` parameters:** `{% include x.html
  config=home[group] %}` is a syntax error. Assign to a variable first.
- **`sort` can't compare a Date with a string**, and it fails the whole build
  rather than the one page. Normalise values with `date:` (or another filter)
  before comparing or sorting them.
- **`nil | date: …` is `nil`, not `""`.** Test the original field (`if
  event.end_date`), not the filtered value.
- Use `relative_url` for every internal link and asset. The site is
  currently served from the domain root (`baseurl: ""`), but this keeps a
  move to a project path a one-line change in `_config.yml`.

## Analytics

Visitor statistics come from [Umami](https://umami.is), which uses no
cookies and collects no personal data, so it needs no consent banner. It's
switched on by setting `analytics.umami_website_id` in `site.yml`. The layout
then adds Umami's script tag, with three safeguards:

- **Live site only:** the tag is included only when `jekyll.environment` is
  `production`. GitHub Pages builds in production mode; a local
  `jekyll build` or `serve` (including the test copy in [TEST.md](TEST.md))
  runs in development mode, so it's never tracked.
- **`data-domains`:** set from `url` in `_config.yml`, so a fork of the repo
  published elsewhere can't report into the hub's statistics. If the site
  moves to a custom domain, update `url`.
- **`data-do-not-track="true"`:** browsers that send Do Not Track aren't
  counted.

To check the tag locally, build with
`JEKYLL_ENV=production bundle exec jekyll build` and look for `umami` in
`_site/index.html`. If you serve that build, Umami still ignores it, because
of `data-domains`.

## Accessibility

- **Skip link:** the first Tab press reveals "Skip to content".
- **Focus:** a visible ring (`:focus-visible`, 3px). The top bar isn't
  sticky, so nothing can hide a focused element.
- **Target sizes:** nav links are 48px tall and the other controls are well
  above the 24px minimum.
- **Event dates:** the date block is `aria-hidden`. The same date is
  repeated in the text meta line that screen readers read.
- **Nav state:** the current page has `aria-current="page"`, which is also
  what the CSS uses to underline it.
- **Decorative images:** photos have empty `alt`, because the name next to
  each photo carries the meaning. The mail icons are `aria-hidden`.

## Deliberately left out

There's no dark mode, search, filtering, pagination, banner photos, cookies,
animation, JavaScript framework or CSS preprocessor. Each would
add moving parts for little benefit at this size. Reconsider only when the
content outgrows the simple version.

## Testing

[TEST.md](TEST.md) explains how to put a password-protected test copy on a
server. Before publishing a change to the design or templates, it's worth
repeating the checks used so far:

- **Messy data:** build a copy of the site with deliberately awkward data:
  unquoted dates and times, missing fields, `<`/`&` in titles, a URL with no
  spaces, unknown kinds.
- **No overflow:** check that no page scrolls sideways at 320px.
- **HTML validity:** run `npx html-validate` with `no-trailing-whitespace`
  off and `no-raw-characters` relaxed.
- **Links:** check that every internal link resolves, including in a build
  with `--baseurl /test`.

## Local development

```bash
bundle config set --local path vendor/bundle   # first time only
bundle install
bundle exec jekyll serve                        # http://localhost:4000
```

`vendor/`, `.bundle/`, `_site/` and `Gemfile.lock` are git-ignored.
GitHub Pages resolves gem versions itself.

# Economics and Finance Hub website

The website of the Economics and Finance Hub, served at
<https://kcl-econfin-hub.github.io>.

You can update everything on the site (text, events, software, people and
colours) by editing four plain-text files in the [`_data/`](_data/) folder. You
don't need to touch any HTML.

## How to make a change

1. On GitHub, open the file you want to change (see the table below) and click
   the pencil icon ("Edit this file").
2. Make your change, then click **Commit changes**.
3. The site rebuilds itself. Your change is live within a minute or two.

If something goes wrong, the site simply keeps showing the previous version.
Check the **Actions** tab on GitHub for a red cross, which usually points to a
typo in the file you edited (see [Common mistakes](#common-mistakes)).

## Where everything lives

| File | What it controls |
| --- | --- |
| [`_data/events.yml`](_data/events.yml) | Events: seminars, workshops, reading groups… |
| [`_data/software.yml`](_data/software.yml) | Software listed on the Software page |
| [`_data/people.yml`](_data/people.yml) | The hub co-champions, shown in the sidebar |
| [`_data/site.yml`](_data/site.yml) | All other text (the hub description, research questions, headings, button labels), the sidebar's contact addresses and related links, and the colour palette |

Each file starts with a comment listing every field it accepts. Longer text
fields (descriptions, intros) accept markdown: `[link text](https://…)`,
`**bold**`, `*italic*`, and a blank line to start a new paragraph.

## Adding an event

Add an entry to `_data/events.yml`:

```yaml
- title: "Strategic Behaviour in Decentralised Exchanges"
  type: "Seminar"                       # shown as a small label
  speaker: "Dr Jane Doe (University of Somewhere)"
  date: "2026-11-12"                    # YYYY-MM-DD, in quotes
  time: "14:00-15:00"
  location: "Bush House (N) 6.01"
  description: "We study how ..."
  registration_url: "https://..."       # optional "Register" link
```

Only `title` is required. For an event lasting several days, add
`end_date: "2026-11-13"`. Other optional links are `url` (event page),
`video_link` (Teams/Zoom), `speaker_url` and `paper_url`.

You don't need to sort anything. Events that haven't finished yet appear
under **Upcoming**, soonest first, and the rest under **Past**. The overview
page shows the next three. Each dated event gets an **Add to calendar** button.

> The upcoming/past split is worked out whenever the site rebuilds, which
> happens on every change. On a quiet week an event can stay under
> "Upcoming" for a day or two after it has happened. Any edit (even adding
> next week's talk) refreshes it.

## Adding software

Add an entry to `_data/software.yml`:

```yaml
- name: "Clearing Simulator"
  kind: web_app                 # web_app, local_app or repository
  summary: "Interactive simulation of clearing in financial networks."
  description: "Longer text, shown on the Software page only."   # optional
  authors:                                                       # optional
    - name: "Dr Jane Doe"
      url: "https://www.kcl.ac.uk/people/jane-doe"   # optional profile link
    - "John Smith"                                   # a plain name works too
  tags: ["Python", "systemic risk"]                               # optional
  app_url: "https://..."        # "Open app"
  repo_url: "https://..."       # "Code"
  featured: true                # also show it on the overview page
```

The other links are `download_url`, `docs_url` and `paper_url`. Include
whichever apply. The first one present is shown as a filled button. Each
`kind` has its own card colour and label.

Software appears in the order you list it.

## Changing people

`_data/people.yml` has two lists:

- `leads` holds the co-champions, who appear in the sidebar of every page.
- `members` holds everyone else.

The **People** section at the bottom of the overview shows both lists
together, sorted by last name, so list each person only once. Each person
has:

- `name`
- `job_title`
- `website` (the name links there)
- `photo`

To add a member, replace `members: []` with entries:

```yaml
members:
  - name: "Dr Jane Doe"
    photo: "jane-doe.jpg"
    job_title: "Lecturer in Computer Science"
    website: "https://www.kcl.ac.uk/people/jane-doe"
```

Sorting uses the last word of the name. If that isn't the surname, add e.g.
`sort_as: "Gonzalez Amador"`. To add a photo:

1. Upload a **square** image (around 320×320 pixels) to
   [`assets/img/people/`](assets/img/people/). On GitHub, use **Add file →
   Upload files** in that folder.
2. Set `photo:` to its file name, e.g. `photo: "jane-doe.jpg"`.

The photo is cropped to a circle automatically.

## Contact addresses and related links

The other sidebar boxes are set under `sidebar:` at the bottom of
`_data/site.yml`:

```yaml
sidebar:
  contacts:
    - "bart.de_keijzer@kcl.ac.uk"
  links:
    - title: "Department of Informatics"
      url: "https://www.kcl.ac.uk/informatics"
```

Remove every entry from a list to hide its box.

## Changing text

All the wording on the site is in `_data/site.yml`: the hub description,
the research questions, page headings and taglines, sidebar headings and
button labels. Find the text you want to change and edit it in place.

To rename the hub, change `title`, `short_title`, `mark` (the two letters
in the red square), the `page_title` of each page and the description text.

## Visitor statistics

The live site can count visitors with [Umami](https://umami.is), a
privacy-friendly service that uses no cookies. To turn it on:

1. Add the site in Umami. Its address is `kcl-econfin-hub.github.io`.
2. Copy the website ID from the site's **Edit** page, under "Tracking code".
   It looks like `a1b2c3d4-…`.
3. Paste it into `_data/site.yml`:

   ```yaml
   analytics:
     umami_website_id: "a1b2c3d4-..."
   ```

Statistics then appear in your Umami dashboard. Only the live site is
counted, never previews or the test copy. Set the ID back to `""` to turn
analytics off.

## Changing colours

The `palette:` block at the top of `_data/site.yml` sets every colour on the
site. Change a value, e.g. `accent: "#C8102E"`, and the whole site follows.
The comment beside each colour says where it is used. Software card colours
are the `kind-…` entries.

## Common mistakes

YAML is strict about a few things:

- **Indentation:** use spaces, never tabs, and line fields up under the
  first one, exactly as in the examples.
- **Quotes:** put text in double quotes, especially if it contains a colon
  (`:`) or starts with a special character. To include a double quote inside
  the text, use single quotes around it instead.
- **Dates and times:** write dates as `"YYYY-MM-DD"` and times as
  `"14:00-15:00"`. Quotes are recommended, but the site copes without them.
- **The `[]` line:** `events.yml` and `software.yml` start out with a line
  containing just `[]`, which means "empty list". Delete it when you add the
  first entry.

To check a file before committing, paste it into an online YAML validator.

## Previewing locally (optional)

If you have Ruby installed you can preview changes before publishing:

```bash
bundle config set --local path vendor/bundle   # first time only
bundle install                                 # first time only
bundle exec jekyll serve
```

Then open <http://localhost:4000>.

For how the site is built and how to change its design, see
[DEVELOP.md](DEVELOP.md).

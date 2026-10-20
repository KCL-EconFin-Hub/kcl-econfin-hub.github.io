"""Fetch the Finance Hub's people from its King's College London page.

Opens the page in Google Chrome, clicks "Show more people" until everyone is
listed, then writes people.csv (firstname, lastname, photofilename, jobtitle)
and saves each profile photo in photos/, both in the current directory.

Setup (once), from this folder:

    python3 -m venv .venv
    .venv/bin/pip install playwright

Run:

    .venv/bin/python fetch_kcl_people.py

Playwright drives the Google Chrome already installed on this machine, so no
separate browser download is needed.

Photos are requested at twice the size the page shows (320x320 px), with
KCL's crop. Where the original image is too small for that, KCL's image
service returns the original uncropped instead (between 160 and ~310 px, not
always square); the site crops every photo to a centred circle, so these
still display well.
"""

import csv
import mimetypes
import urllib.parse
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

PAGE_URL = "https://www.kcl.ac.uk/research/finance-hub-informatics"
CSV_FILE = Path("people.csv")
PHOTO_DIR = Path("photos")

# Photos are listed at 160x160 px; fetch them this many times larger.
PHOTO_SCALE = 2

HONORIFICS = {"dr", "professor", "prof", "mr", "mrs", "ms", "miss", "mx", "sir", "dame"}
# Surname particles: "Bart De Keijzer" -> first "Bart", last "De Keijzer".
PARTICLES = {"de", "van", "von", "der", "den", "da", "di", "du", "del", "della",
             "dos", "das", "le", "la", "ter", "ten", "bin", "al"}


def split_name(full_name):
    """Split "Dr Bart De Keijzer" into ("Bart", "De Keijzer")."""
    words = full_name.split()
    while words and words[0].rstrip(".").lower() in HONORIFICS:
        words = words[1:]
    if len(words) < 2:
        return " ".join(words), ""
    # The surname is the last word plus any particles directly before it.
    start = len(words) - 1
    while start > 1 and words[start - 1].lower() in PARTICLES:
        start -= 1
    return " ".join(words[:start]), " ".join(words[start:])


def larger_photo_url(src):
    """Scale the image service's size and crop parameters by PHOTO_SCALE,
    keeping the same crop, and drop the WebP conversion."""
    parts = urllib.parse.urlsplit(urllib.parse.urljoin(PAGE_URL, src))
    query = dict(urllib.parse.parse_qsl(parts.query))
    query.pop("f", None)
    for key in ("w", "h"):
        if key in query:
            query[key] = str(int(query[key]) * PHOTO_SCALE)
    if "crop" in query:
        query["crop"] = ",".join(str(int(n) * PHOTO_SCALE) for n in query["crop"].split(","))
    return urllib.parse.urlunsplit(parts._replace(query=urllib.parse.urlencode(query, safe=",")))


def download(url, stem):
    """Save url as photos/<stem>.<ext> and return the file name."""
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        content_type = response.headers.get_content_type()
        data = response.read()
    extension = {"image/jpeg": ".jpg"}.get(content_type) or mimetypes.guess_extension(content_type) or ".jpg"
    filename = stem + extension
    (PHOTO_DIR / filename).write_bytes(data)
    return filename


def scrape_people():
    """Return one dict per person card, after expanding the full list."""
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page()
        page.goto(PAGE_URL, wait_until="networkidle")

        # The cards that follow the "People" heading.
        section = page.get_by_role("heading", name="People", exact=True).locator("xpath=..")
        cards = section.locator('[data-test-id="list-item"]')
        more = page.get_by_role("button", name="Show more people")

        while more.count() and more.is_visible():
            shown = cards.count()
            more.click()
            page.wait_for_function(
                "([el, n]) => el.querySelectorAll('[data-test-id=\"list-item\"]').length > n",
                arg=[section.element_handle(), shown])

        people = []
        for card in cards.all():
            name_link = card.locator(".name a")
            image = card.locator("img")
            title = card.locator("p.title")
            people.append({
                "name": name_link.inner_text().strip(),
                "slug": name_link.get_attribute("href").rstrip("/").split("/")[-1],
                "photo_src": image.get_attribute("src") if image.count() else None,
                "jobtitle": title.inner_text().strip() if title.count() else "",
            })
        browser.close()
    return people


def main():
    people = scrape_people()
    PHOTO_DIR.mkdir(exist_ok=True)
    with CSV_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["firstname", "lastname", "photofilename", "jobtitle"])
        for person in people:
            firstname, lastname = split_name(person["name"])
            photo = download(larger_photo_url(person["photo_src"]), person["slug"]) if person["photo_src"] else ""
            writer.writerow([firstname, lastname, photo, person["jobtitle"]])
            print(f"{firstname} {lastname}: {photo or 'no photo'}")
    print(f"\n{len(people)} people written to {CSV_FILE}, photos in {PHOTO_DIR}/")

if __name__ == "__main__":
    main()

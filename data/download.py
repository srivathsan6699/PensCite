# /// script
# requires-python = ">=3.12"
# ///
from __future__ import annotations

import json
import re
import shutil
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib import error, request


# Params: edit these, then run `uv run data/download.py`
USER_AGENT = "Penscite data downloader"
OUTPUT_DIR = Path(__file__).resolve().parent / "downloads"
CLEAR_OUTPUT_DIR = True
REQUEST_DELAY_SECONDS = 0.15

# Pensions Tax Manual sections to crawl (top-level contents pages).
MANUAL_SECTIONS = {
    "PTM040000": "Contributions",
    "PTM050000": "Annual allowance",
    "PTM060000": "Member benefits",
    "PTM070000": "Death benefits",
    "PTM170001": "Lump sum allowance and lump sum and death benefit allowance",
}
# Max pages with body text to save per section; None crawls the whole section.
MAX_PAGES_PER_SECTION: int | None = 200

NEWSLETTER_COLLECTION = (
    "/government/collections/hm-revenue-and-customs-pension-schemes-newsletters"
)

GUIDANCE_PATHS = [
    "/workplace-pensions",
    "/workplace-pensions-employers",
    "/tax-on-your-private-pension",
]

GOVUK = "https://www.gov.uk"
MANUAL_PATH = "/hmrc-internal-manuals/pensions-tax-manual"
LICENCE = "Open Government Licence v3.0"


def get_content(base_path: str) -> dict:
    url = f"{GOVUK}/api/content{base_path}"
    req = request.Request(
        url, headers={"Accept": "application/json", "User-Agent": USER_AGENT}
    )
    for attempt in range(4):
        try:
            with request.urlopen(req, timeout=30) as response:
                content = json.loads(response.read().decode("utf-8"))
            time.sleep(REQUEST_DELAY_SECONDS)
            return content
        except error.HTTPError as exc:
            # GOV.UK rate-limits bursts; back off and retry on 429 and 5xx.
            if (exc.code != 429 and exc.code < 500) or attempt == 3:
                raise
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


def save(content: dict, source: str, reference: str, **extra: object) -> dict:
    local_path = OUTPUT_DIR / source / f"{content['base_path'].rsplit('/', 1)[-1]}.json"
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")
    return {
        "source": source,
        "reference": reference,
        "title": content["title"],
        "document_type": content["document_type"],
        "url": GOVUK + content["base_path"],
        "first_published_at": content.get("first_published_at"),
        "public_updated_at": content.get("public_updated_at"),
        "local_path": str(local_path.relative_to(OUTPUT_DIR)),
        **extra,
    }


def child_paths(content: dict) -> list[str]:
    return [
        child["base_path"]
        for group in content["details"].get("child_section_groups", [])
        for child in group["child_sections"]
    ]


def download_manual_section(section_id: str) -> list[dict]:
    entries = []
    # Depth-first with reversed children keeps pages in manual order.
    stack = [f"{MANUAL_PATH}/{section_id.lower()}"]
    while stack and (
        MAX_PAGES_PER_SECTION is None or len(entries) < MAX_PAGES_PER_SECTION
    ):
        content = get_content(stack.pop())
        stack.extend(reversed(child_paths(content)))

        # Contents pages have an empty body and archived pages keep only a
        # placeholder; neither belongs in the corpus.
        text = re.sub(r"<[^>]+>", "", content["details"].get("body", "")).strip()
        if text in ("", "This page has been archived."):
            continue
        entries.append(
            save(
                content,
                "pensions-tax-manual",
                content["details"]["section_id"],
                manual_section=section_id,
                breadcrumbs=[
                    crumb["section_id"] for crumb in content["details"]["breadcrumbs"]
                ],
            )
        )
    return entries


def download_newsletters() -> list[dict]:
    collection = get_content(NEWSLETTER_COLLECTION)
    entries = []
    for document in collection["links"]["documents"]:
        publication = get_content(document["base_path"])
        # The newsletter text lives in an HTML attachment, not the landing page.
        for attachment in publication["details"]["attachments"]:
            if attachment["attachment_type"] != "html":
                continue
            entries.append(
                save(
                    get_content(attachment["url"]),
                    "pension-schemes-newsletters",
                    publication["title"],
                    publication_url=GOVUK + publication["base_path"],
                )
            )
    return entries


def download_guidance() -> list[dict]:
    entries = []
    for path in GUIDANCE_PATHS:
        content = get_content(path)
        entries.append(
            save(
                content,
                "govuk-guidance",
                path.lstrip("/"),
                parts=[part["slug"] for part in content["details"].get("parts", [])],
            )
        )
    return entries


def download_corpus() -> dict:
    if CLEAR_OUTPUT_DIR and OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    documents = []
    for section_id, name in MANUAL_SECTIONS.items():
        print(f"Downloading Pensions Tax Manual: {name} ({section_id})...")
        documents.extend(download_manual_section(section_id))
    print("Downloading pension schemes newsletters...")
    documents.extend(download_newsletters())
    print("Downloading GOV.UK guidance...")
    documents.extend(download_guidance())

    manifest = {
        "source": "GOV.UK Content API",
        "licence": LICENCE,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "downloaded_count": len(documents),
        "documents": documents,
    }
    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    result = download_corpus()
    print(f"Downloaded {result['downloaded_count']} document(s) to {OUTPUT_DIR}")
    print(f"Manifest: {OUTPUT_DIR / 'manifest.json'}")

# Data

Local data artifacts for development live here.

- `downloads/` holds raw source pages fetched from the GOV.UK Content API (HMRC Pensions Tax Manual, HMRC pension schemes newsletters, GOV.UK guidance), plus a `manifest.json`.
- Downloaded payloads are gitignored because the corpus can get large.
- Fetch the corpus with `uv run data/download.py` (about 2 minutes). Edit the params at the top of the script to change which Pensions Tax Manual sections, newsletters and guidance pages are included.

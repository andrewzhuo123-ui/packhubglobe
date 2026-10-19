# Verified pouch reference import — 19 October 2026

Captured all product detail routes in the live source sitemaps: 540 UniquePouches and 615 StandPouchy pages. All 1,155 pages and main images returned successfully. Main images must decode and have at least 300 pixels on each axis.

605 unique product references were added to PackHubGlobe. 550 repeated references were merged using equivalent main-image content, including encoding variants (a 256-bit difference hash followed by mean/RMS pixel comparison). Source URLs remain attached to each retained reference. There were no equivalent images in the existing eight pouch products. Unused duplicate image files are omitted from the public assets.

`captures/` preserves captured text, specification fields, image source URLs and image hashes. `products.json` contains the curated public fields and per-product source provenance; `report.json` accounts for every candidate and duplicate. These source files remain private under the site's existing `/content/` access restriction.

Public pages use local images, PackHubGlobe references, MOQ 500 and the existing PackHubGlobe quote/WhatsApp routes. Material, film, closure, printing and dimensions are reference fields requiring project confirmation. Source-site prices, MOQ, timing and certification/environmental claims are not adopted. 97 individual source review notes identify unresolved material, closure or image/specification questions.

Rebuild with `python3 tools/build.py`; verify with `python3 tools/validate.py`, `python3 tools/validate-expansion.py` and `python3 tools/validate-pouch-import.py`. Re-running `tools/import_pouch_sources.py` refreshes missing cached image files from the recorded public sources.

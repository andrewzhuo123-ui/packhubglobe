# LuxoPack source reference import — 19 October 2026

Captured all 52 `/products/` routes discovered through the live sitemap, homepage and product directory. All pages and selected product images returned successfully. Original HTML (stored as `.html.gz`), page text, specification tables and source image URLs are preserved in `captures/` and `captures.json`.

49 individually reviewed product references are published: 39 rigid presentation boxes, four corrugated mailer/shipping boxes, two food packaging references, two folding cartons, one gable carry box and one paper carrier bag. The eco-packaging and jewelry overview pages are excluded as collections. The collapsible magnetic-box and shoulder/neck-box pages use an equivalent main image; one shoulder/neck reference retains both source URLs, with a note that the photograph does not establish a collapsible mechanism. No equivalent main images were found among the 1,461 prior catalog products (256-bit difference hash followed by RGB mean/RMS comparison).

All 49 main images and four approved additional design images decode successfully, have at least 300 pixels per axis, and are stored locally. Source logos remain intact. Additional images are labeled design references rather than fixed production specifications. `review.tsv` records the individual product name, format, primary collection, application and project-specific review notes used to generate public records.

Public pages retain PackHubGlobe contact routes and MOQ 500. Source MOQ, pricing, lead times, certifications, environmental and performance claims are not adopted. Food contact, material composition and final supplied components require confirmation for the actual order. Raw source material stays under the existing protected `/content/` directory.

Run `python3 tools/import_luxopack.py` to capture missing source files and regenerate the reviewed records. Unreviewed new source routes stop the import. Build with `python3 tools/build.py`; verify with `tools/validate.py`, `tools/validate-expansion.py`, `tools/validate-luxopack.py` and `tools/audit-catalog-consistency.py`.

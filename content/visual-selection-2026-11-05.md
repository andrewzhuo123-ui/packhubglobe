# Core page product image selection — 5 November 2026

Reselected existing catalog photos after reviewing contact sheets for product structure, application, composition and legibility. Selection is recorded in `content/visual-selection.json`; product links and alt text come from the selected catalog record.

- Homepage: 22 distinct product photos across hero, categories, industries and portfolio. Hero and category/portfolio sections use separate references.
- Six product families: distinct hero photos; comparison references exclude hero and format-card photos. Repeated format pictures are shown once; remaining formats keep their text links in the additional-formats list. Empty comparison sections are omitted.
- Fifteen industries: curated hero plus three other references, replacing keyword-first matching and repeated hero images.
- Corrected structure references for flat pouches, shopping bags and molded pulp inserts. Removed the die-cut handle mapping that showed a flat-bottom food pouch; the format link remains available with a clearly captioned family reference on its detail page.
- Image dimensions reflect each catalog record. Existing responsive variants and their compression are preserved. The preparation script now covers product and industry pages and retains existing variants.

Validation: `python3 tools/test-visual-selection.py` checks all 68 homepage/product/industry pages for missing assets, alt text and identical image bytes repeated on the same page, plus selection/record consistency. Browser results and reviewed desktop/mobile screenshots are under `qa/visual-selection/`. Summary-to-detail navigation and catalog product records may reuse an image across separate pages; this change avoids repeats within the reviewed pages and diversifies their prominent selections.

A Git push and the refreshed hosting package do not establish public deployment. Public image changes must be verified separately after hosting updates.

# PackHubGlobe detailed visual and content review — 2026-10-30

## Scope and evidence

- 2,246 public pages plus the 404 document; 1,824 catalog products. Product URLs preserved.
- All 2,247 documents rendered at actual 390 × 844 and 1440 × 1000 viewports: 4,494 checks, no invalid page, wrong viewport, horizontal overflow, flagged text/card overflow, broken visible image or visible empty paragraph.
- 128 representative routes additionally checked at 360, 428, 768 and 1024 px: 512 checks, no flagged issue.
- All 1,840 baseline raster images reviewed across 39 contact sheets; suspected mismatches enlarged against record evidence. Two newly used production photographs separately inspected. Final 1,842 raster files decode successfully.
- 213,749 rendered text blocks / 19,721 unique blocks scanned for unresolved text and repeated long sentences. This is automated coverage plus contextual editorial review, not a claim that each paragraph received individual manual proofreading.
- Ten purchasing guides analyzed separately. Heuristic results and contextual limitations saved under ignored `qa/deep-review/reports/`.

## Repairs

1. Corrected 17 image/title, application or construction classifications in the reviewed catalog overrides. The grain dispensing pouch no longer claims water-storage suitability; window cartons, folding mailers and rigid presentation boxes follow visible construction. Generic insert/accessory options are explicitly labeled as options.
2. Category recommendations now use explicit format membership; broad groups show a range of structures. Industry recommendations consider application. Removed unrelated card/tag, sticker, bag and material references.
3. Material pages show relevant packaging references. Service production images have specific captions distinguishing production context from inspection, export packing or sourcing evidence. Seven formats without a matching photo appear as honest text links.
4. Reference-card facts have readable labels; related-product cards use compact navigation without competing RFQ buttons. Removed redundant order-planning sentence and single-image duplicate thumbnails.
5. Mobile product images precede the main title/specification content. Home CTAs share one row; floating contact controls hide while the mobile menu is open. Product images retain their full proportions.
6. Reclassification reduces mailer pagination by one page. The removed `/catalog/mailer-shipping-boxes/page-13/` has a 301 to page 12; internal links and sitemap rebuilt. Total changes from 2,247 to 2,246 public pages; no product deleted.

## Deployment cache repair

Hostinger edge nodes returned different CSS revisions for the same query-versioned URL. Generated pages now reference a content-hashed CSS filename, preserving the source stylesheet and preventing old CSS from sharing the new public asset path.

## Validation and limitations

Whole-site route, asset, structured-data syntax, UI and catalog consistency checks passed. Product editorial depth and all ten guides retained. Enquiry client tests and the 29-case PHP WASM harness passed; no production enquiry was sent. Native PHP is unavailable locally; the harness uses PHP 8.4 WASM and mocked mail/CLI behavior.

The review establishes technical coverage and reviewed visual consistency, not universal subjective approval, a formal WCAG certification, manufacturing certification or conversion lift. GA4 remains unconnected because no Measurement ID exists. Field INP, indexing and actual email delivery are not claimed. Local QA evidence is excluded from the public site package.

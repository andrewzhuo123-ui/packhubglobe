# Finer Packaging catalog import

Complete collection: 33 groups inventoried, 2,259 distinct candidate products. 856 selected products with 856 local main images and complete original detail records. 1,177 category memberships share 856 product detail pages. Health care box is an empty source group.

## Selection and provenance

- Each category includes all products below 200, otherwise 200. Gift boxes: 200 of 207; cosmetic packaging: 200 of 1,603. All other categories include all listed products. See coverage.csv.
- Larger groups use title-derived application families and a seven-item source-position stride to spread the selection. This is a diversity heuristic, not a sales ranking, search-volume measure or Alibaba quality-score ranking.
- listings.json preserves original titles, source URLs, displayed price/MOQ and image URLs. details/ preserves original public metadata keywords, attributes, exposed variant options, store identity and UTC timestamps.
- Public keyword metadata often repeats the title; it is not a seller backend keyword export or proof of Google search volume.
- Public product names are concise source-based descriptions. Attributes and photos are references for custom specifications. Marketplace pricing, delivery promises and unsupported environmental/certification claims are not copied into product copy.
- Corporate entity names appear only on About / Factory pages. Original source records remain in content/, excluded from the deployment ZIP and blocked by .htaccess.
- Product inquiries include PHG references and use andrew@packhubglobe.com / WhatsApp +86 15105916426. The existing form prepares an email draft; it does not automatically send it.

## Build and validation

- python3 tools/catalog_verify.py checks category completion, selected counts, local assets, product identity, source store and attributes before HTML is written.
- python3 tools/build.py generates 1,100 public pages and one 404 document, including all original 100 routes.
- python3 tools/validate.py passed: 1,100 sitemap URLs, 70,167 internal links, all pages reachable, unique titles/descriptions, one H1 per page, local assets and JSON-LD.
- 79 representative routes tested at 320/390/768/1440 widths: 316 checks, no overflow. Exact-reference search, zero-result state, reset, pagination, mobile menu and quote prefill/email-draft recipient verified.
- python3 tools/package.py creates packhubglobe-hostinger-public_html.zip with 1,992 deployable files.
- Publication to GitHub and actual Hostinger deployment are separate states; see status.json.

## October 16 catalog expansion

- Owner-set catalog MOQ: 500 pieces for every product; original marketplace values remain unchanged in source records.
- Primary families: 771 paper boxes, 46 bags and pouches, 39 packaging accessories; all 856 original detail URLs preserved in item-paths.json.
- Cards and search results include captured attributes and a product-specific WhatsApp inquiry link.
- Every product has a relevant procurement guide, customization checklist, sample review and FAQs. All 10 Guides and the homepage have expanded editorial content.
- python3 tools/validate-expansion.py verifies MOQ, card facts, WhatsApp messages, original URLs, content sections and family coverage.
- Current responsive smoke test: 28 checks across homepage, catalog, three family hubs, product detail and Guide at 320/390/768/1440, no overflow.

## Coverage

| Source category | Candidates | Selected / complete details |
| --- | ---: | ---: |
| Hot Sale | 13 | 13 / 13 |
| $0.01 SAMPLE | 4 | 4 / 4 |
| Mailer Box & Shipping Box | 185 | 185 / 185 |
| Kraft Shipping Box | 19 | 19 / 19 |
| Colorful Shipping Box | 29 | 29 / 29 |
| Zipper Box | 2 | 2 / 2 |
| Fragile Shipping Box | 8 | 8 / 8 |
| Paper Bag | 26 | 26 / 26 |
| Shopping Bag | 9 | 9 / 9 |
| Mailer Bag | 17 | 17 / 17 |
| Gift Box | 207 | 200 / 200 |
| Magnetic Box | 191 | 191 / 191 |
| Drawer Box | 6 | 6 / 6 |
| Lid $ Base Box | 4 | 4 / 4 |
| Tube | 1 | 1 / 1 |
| Other | 4 | 4 / 4 |
| Clothing Packaging | 28 | 28 / 28 |
| Poly Bag | 10 | 10 / 10 |
| Zipper Bag | 7 | 7 / 7 |
| Mailer Bag | 3 | 3 / 3 |
| Underwear Box | 13 | 13 / 13 |
| Hang Tag & Strings | 5 | 5 / 5 |
| Cosmetic Packaging | 1603 | 200 / 200 |
| Food Packaging | 97 | 97 / 97 |
| Sushi Packaging Box | 27 | 27 / 27 |
| Cardboard Displays | 18 | 18 / 18 |
| Tea Packaging | 1 | 1 / 1 |
| Candle Packaging | 25 | 25 / 25 |
| Health care box | 0 | 0 / 0 |
| Paper Cards & Booklet | 11 | 11 / 11 |
| Sticker&Label | 4 | 4 / 4 |
| Pouches | 8 | 8 / 8 |
| Ungrouped | 2 | 2 / 2 |

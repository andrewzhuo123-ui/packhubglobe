# SEO, GEO and enquiry-flow update — 5 November 2026

Based on the owner's second proposal, `packhubglobe_seo_geo_frontend_optimization_plan.md`. The proposal supplies recommendations, not verified product prices, availability, credentials, factory measurements or business results. Work started from clean commit `47c540e85` and preserves its curated product imagery.

## Implementation and scope decisions

| Proposal area | Result |
| --- | --- |
| Homepage enquiry friction | Added one inline enquiry form after packaging categories. Packaging type, quantity and email are the core inputs; notes are optional and consent is required. The hero CTA leads to this section. The existing full brief and attachment route remains available. |
| Product enquiry drawer | Catalog products and detailed product-format pages include a native dialog. Main and mobile contextual quote links open it; normal links remain useful without JavaScript. Product title, reference and source path are carried to the existing PHP endpoint. Optional notes, visible submission state and failure preservation are included. No instant-price, response-time or free-dieline promise is made. |
| Submission contract | Both new forms use the existing fixed-recipient `/request-quote/send.php`. Empty optional notes become an explicit initial enquiry asking to confirm the remaining specification. Server validation, consent, honeypot and cooldown remain in force. No new backend, CRM ticket service or recipient is introduced. |
| Draft protection | Optional session-storage saving on the full form. It is off by default, saves text fields and relevant context only after visitor opt-in, and clears the saved copy on successful full-form submission or explicit clear. Attachment files and consent are never saved. Another product's context is protected from a mismatched draft. Privacy copy reflects the feature. |
| Guide semantics | All **19 actual guide articles**, not the guide index, have FAQPage data built from the same Q&A source as their visible FAQ. The quote checklist adds HowTo steps with matching visible anchors. Guide quick-answer asides include three topic-specific decisions from the existing approval checklist. Article modification dates and guide sitemap dates reflect this update. |
| Product offers | Existing evidence-bound Product descriptions remain. No example prices, fake zero-price offers, stock claims, price-validity dates, return policies or invented reviews were added. Price and availability data would need public, verified commercial terms before Offer markup could be added. No claim is made that the current products qualify for Google's merchant listings or product snippets. |
| Hub and spoke links | Five existing hubs (magnetic boxes, drawer boxes, mailers/shipping boxes, paper bags and stand-up pouches) now have tailored selection summaries, decision tables, guide links, industry links and design-concept links. The 15 existing industry routes connect to design concepts, and the concepts page links back to relevant industries. New duplicate industry/category aliases were not needed. |
| Companion components | Product pages link to relevant boxes, bags, inserts, cards or labels. The wording asks buyers to coordinate dimensions, materials and quantity; it does not assert verified compatibility from photos. |
| Entity evidence | About explains the addresses and carton-production scope shown in supplied ISO documents and links to complete documents. About and Factory JSON-LD identify the paper manufacturer, flexible-packaging company and separately named FSC trading company, without asserting a parent/subsidiary relationship or assigning their certificates to the PackHubGlobe brand. |
| Knowledge accuracy | Existing worked examples, comparison tables, public reference properties and procurement checks remain. The proposal's hypothetical unit costs, freight savings, test ratings and universal dimension formula were not converted into product specifications. Unsupported engineer biographies, LinkedIn profiles, equipment models, floor area, BSCI/Sedex and additional material-compliance claims were not added. |
| Asset delivery | One content-addressed CSS file and one deferred content-addressed JS file replace the separate shared resource requests. Their names are SHA-256-derived. Only these immutable bundles get one-year caching; HTML and mutable JSON remain revalidated. Apache compression is configured conditionally for Brotli or gzip according to installed modules and supported content types. One small cacheable stylesheet retains predictable first paint. |
| Navigation acceleration | Conservative same-origin HTML prefetch is enabled only on supported browsers and deliberate navigation links. It skips query URLs, assets and data-saving/slow connections. It does not prerender forms or execute future-page scripts. No zero-millisecond-navigation promise is made. |
| Measurement | Per the owner's explicit answer, **no GA4, GTM, Clarity, external collector or session recording is enabled**. Existing local event interfaces now include form-location, drawer open/close, field-completion names, documentation opens and brief downloads. Homepage form-view events require visibility; contact values, notes, attachments and query strings are excluded. |
| External promotion | No Reddit posts, directory submissions, guest posts, paid placements or outbound messages were sent. Those require a separate, concrete communication instruction and verified material. |

## Verification

Passed locally:

- Build: 2,255 public routes plus the 404 document. Existing canonical routes and page count preserved.
- Full validator: H1s, canonicals, sitemap, JSON-LD parsing, links and assets passed. All guide FAQ strings match the visible questions and answers; all HowTo steps resolve to visible sections.
- UI audit: 2,256 HTML documents, zero reported UI issues. Expanded product and guide content checks passed.
- Existing UX suite: 54 responsive layouts, 10 automated accessibility checks and three navigation/enquiry tasks passed. The navigation assertion was brought into line with the image-curation baseline; contextual quote navigation now verifies the drawer before continuing to the full form.
- New conversion suite: homepage submission, invalid-input blocking, product/source context, failure preservation, success payload, opt-in draft restore/clear/success lifecycle, analytics privacy, 20 additional layouts and eight additional automated accessibility checks passed. Browser console errors and warnings were empty.
- Catalog suite: basket persistence, three-item submission payload, URL/history filters, material filter, empty states, 16 layouts and automated accessibility checks passed.
- Existing enquiry-handler scenarios passed: controlled success, failure, network/HTML failures and attachment-limit validation.
- Apache 2.4.66 fixture using the actual `.htaccess`: clean HTML revalidation, filter `noindex`, one-year immutable bundle caching and gzip response bytes were checked. Source bytes and decoded compressed bytes matched. This is local server evidence; production CDN behavior requires its own check.
- Generated bundle hashes match their content. Rebuilds are deterministic. Only unused bundle files created during this task were removed; pre-existing assets were retained.
- Screenshots and machine-readable results: `qa/conversion-2026-11-05/`. No real email was sent.

Limitations: PHP CLI is absent in this environment. No backend PHP code was changed in this round. New enquiry payloads were verified with mocked transport, so actual email delivery and inbox receipt remain unverified. No claim is made about public Core Web Vitals, Lighthouse scores, conversion growth, rankings, indexing or AI citations.

## Source checks behind the adaptations

Google's [Product snippet documentation](https://developers.google.com/search/docs/appearance/structured-data/product-snippet) requires real price data for an Offer or AggregateOffer; example values from the proposal are not evidence. Google's [FAQ/HowTo announcement](https://developers.google.com/search/blog/2023/08/howto-faq-changes) restricts FAQ rich results and documents HowTo rich-result deprecation. Added semantic data is not a promise of a search-result feature. Chrome's [navigation speculation documentation](https://developer.chrome.com/docs/web-platform/prerender-pages) distinguishes prefetch from prerender; this implementation uses bounded HTML prefetch.

## Release

Commit and push are recorded in Git history. Public parity, response headers and key routes must be independently checked after the authorized push; repository state alone is not deployment evidence. The deployment ZIP is generated by `python3 tools/package.py` and excludes source and QA folders.

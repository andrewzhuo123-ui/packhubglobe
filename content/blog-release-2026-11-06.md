# Resources pillar and English blog release — 6 November 2026

The Resources entry at `/guides/` now helps a business buyer choose a question, enter a topic collection and read a complete independent article. The 19 existing guide routes remain available. New material focuses on decision workflows and approval records, while retained guides explain the underlying formats and terms.

Five collections cover sourcing/cost, shipping/protection, materials/sustainability, food pouches and design/sampling. Each contains two new English articles. An article archive and five category pages add 16 routes to the site, bringing the public inventory to 2,271 pages plus the 404 document.

Each article includes a question-led H1, short PAS opening, bold direct answer, transition, four question-led H2 sections, H3 analysis, a comparison table and a short conclusion. Source footnotes have working forward and return anchors. Each article uses three contextual internal links, two external source destinations and five images from the existing local library. The editorial voice expresses first-person buying judgments without invented customer cases, personal history or test results. AI concept images identify fictional brands; other captions explain the relevant specification decision.

The article text, excluding captions and source notes, ranges from 1,339 to 1,427 English words. All 40 deeper sections contain at least 200 words (216–256). PAS paragraphs are at most 30 words, answer paragraphs at most 50, and conclusions at most 30. Publication and modification metadata match the displayed 2026-11-06 date. Existing guide dates retain their earlier values.

The pillar and category maps are server-rendered HTML with ordinary links and native disclosures. The article template includes a table of contents, a related article, Article metadata, breadcrumbs, canonical URL, social metadata and sitemap entries. No FAQ rich-result or ranking outcome is promised. Table headings have scope attributes, readable contrast and keyboard-accessible overflow containers. Blog styling has a separate content-addressed bundle, so commercial page output does not change.

## Evidence and checks

- Build produces 2,271 public routes. The full validator checks all 2,272 HTML documents, sitemap parity, JSON-LD, assets, internal links and reachability with no errors.
- The expansion validator passes for retained catalog/guide content. The complete UI audit reports zero issues.
- `python3 tools/validate-blog.py` verifies all ten articles against the requested article contract, dates, footnotes, images, links and author metadata.
- The blog skill's Markdown scorer reports 90–94. Remaining generic warnings concern exact phrase density, absence of an added FAQ section and lack of an external author profile. The requested question-led structure is retained; no invented biography or repetitive keyword blocks were added to improve a score.
- `tools/test-blog.cjs` checks all 17 affected routes at 360, 768 and 1440 pixels: 51 layouts. Six representative WCAG automated checks and two reading flows pass. Screenshots were visually reviewed on desktop and mobile; an initial table-header contrast issue was corrected. Browser console errors are empty.
- Important external sources were researched. Direct requests returned access restrictions for Adobe and Reddit, while web research read the referenced content. The FTC summary URL was replaced with the current official eCFR Green Guides text after a direct 404; the Wipf link uses the verified canonical manufacturer destination. Access restrictions are not treated as proof that an article source is missing.
- The clean deployment ZIP includes all 16 new blog routes and excludes source, research and QA directories. Local checks do not establish live parity or search indexing.

The user-requested editorial research and future topic queue are retained privately outside this website Git repository. They distinguish actual Search Console observations, relative Google Trends indices, community questions and marketplace vocabulary. No platform sales or absolute keyword volumes were invented. No analytics collector, automation, outbound promotion or search-indexing submission was added.

Git history records the release commit. Public deployment and byte verification are recorded separately in the local research release status, because a successful push does not prove Hostinger has deployed the change.

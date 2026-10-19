# PackHubGlobe

Self-contained English B2B custom packaging website for **https://www.packhubglobe.com/**. All enquiries use **andrew@packhubglobe.com**. Company relationships are explained only on About and Factory pages.

## Website

- 2,247 public pages plus a branded `404.html`.
- 1,824 catalog products in three primary catalog families, 44 detailed product formats, 15 industry solutions, materials and services, ten buyer guides, company/contact and information pages.
- Local fonts and five original AI packaging images with fictional logos and slogans. No external runtime dependencies.
- Responsive navigation, category filters, native FAQ accordions, prefilled enquiry brief, email draft and text download.
- Unique titles, meta descriptions, H1s, canonical URLs, image alt text, semantic HTML, JSON-LD, sitemap and robots.

## Local preview

Run from the repository root:

```sh
python3 -m http.server 4174
```

Open http://localhost:4174/ . Directory URLs need an HTTP server; do not open files using `file://`.

## Rebuild and check

Python 3 and Node.js are needed only for local maintenance and checks, not on the hosting server.

```sh
python3 tools/build.py
python3 tools/validate.py
python3 tools/validate-expansion.py
node --check assets/app.js
python3 tools/package.py
```

Layout/content templates: `tools/build.py`, `tools/complete.py`. Product content: `content/products.py`. Industry, material, service and guide content: `content/collections.py`. Visual styles and behavior: `assets/style.css`, `assets/app.js`.

## Publishing

See **[DEPLOYMENT.md](DEPLOYMENT.md)**. The repository root already contains `index.html`, all public directories and `.htaccess`; no npm install or server build step is required. Private source directories are blocked by `.htaccess`. `tools/package.py` creates a clean `public_html` ZIP without sources, Git metadata or QA reports.

The owner deploys this GitHub repository to Hostinger. Git push is not proof of deployment, indexing, rankings or email receipt.

## Enquiries

The form prepares a complete brief in the visitor’s browser. The visitor can open a draft to **andrew@packhubglobe.com** and send it using their email client, or download the text and attach artwork manually. The site does not perform server-side mail delivery. It never reports an enquiry as sent automatically. A direct email link is also provided.

## Images and claims

Printed virtual brands and photorealistic scenes are original illustrative design references, not customer endorsements, manufactured-order evidence or certification claims. Provenance and full prompts: `content/image-provenance.md`. Fonts are distributed with their OFL licences in `assets/fonts/`.

Catalog products start at 500 pieces. Prices, production timing, materials, features and documents are confirmed for each project. The website does not promise Google rankings or AI citations.

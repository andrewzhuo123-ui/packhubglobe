"""Check every generated page for shared UI, accessible navigation and stale copy."""
from pathlib import Path
from html.parser import HTMLParser
import json
import re

ROOT = Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.headings = []
        self.ids = set()
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if attrs.get('id'): self.ids.add(attrs['id'])
        if re.fullmatch('h[1-6]', tag): self.headings.append(int(tag[1]))

shared_scripts = [attrs['src'] for tag, attrs in Page((ROOT / 'index.html').read_text()).tags if tag == 'script' and attrs.get('src')]
rows = []
for file in sorted(ROOT.rglob('*.html')):
    if any(part in ['qa', '.git'] for part in file.relative_to(ROOT).parts): continue
    text = file.read_text()
    page = Page(text)
    errors = []
    # Footer headings are independent of the page content outline.
    main = Page(text.split('<main', 1)[1].split('</main>', 1)[0])
    if any(b > a + 1 for a, b in zip(main.headings, main.headings[1:])):
        errors.append('Heading level skipped in main content')
    for tag, attrs in page.tags:
        if attrs.get('aria-controls') and attrs['aria-controls'] not in page.ids:
            errors.append('Missing controlled element: ' + attrs['aria-controls'])
        if 'catalog-layout' in attrs.get('class', '').split() and not attrs.get('data-catalog-scope'):
            errors.append('Catalog scope missing')
        if tag == 'img' and attrs.get('srcset'):
            for variant in attrs['srcset'].split(','):
                source = variant.strip().split()[0]
                if not (ROOT / source.lstrip('/')).is_file(): errors.append('Missing responsive image: ' + source)
            if not attrs.get('sizes'): errors.append('Responsive image missing sizes')
        if tag == 'label' and attrs.get('for') and attrs['for'] not in page.ids:
            errors.append('Missing labelled input: ' + str(attrs.get('for')))
        if tag == 'th' and attrs.get('scope') != 'col':
            errors.append('Table column heading missing scope')
        if 'tablewrap' in attrs.get('class', '').split() and (attrs.get('tabindex') != '0' or not attrs.get('aria-label')):
            errors.append('Scrollable table missing keyboard access or label')
    if re.search('Your draft is ready|Open email draft|Prepare an enquiry|when emailing the brief', text):
        errors.append('Outdated enquiry instructions')
    if [attrs['src'] for tag, attrs in page.tags if tag == 'script' and attrs.get('src')] != shared_scripts:
        errors.append('Shared interaction script version mismatch')
    rows.append({'path': str(file.relative_to(ROOT)), 'errors': errors})
report = {'pages': len(rows), 'failed': sum(bool(row['errors']) for row in rows), 'checks': rows}
(ROOT / 'qa').mkdir(exist_ok=True)
(ROOT / 'qa/ui-validation.json').write_text(json.dumps(report, indent=2))
print(json.dumps({'pages': report['pages'], 'failed': report['failed'], 'issues': [r for r in rows if r['errors']][:10]}, indent=2))
raise SystemExit(bool(report['failed']))

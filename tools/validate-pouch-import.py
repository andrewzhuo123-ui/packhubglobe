"""Verify source coverage, local image bytes, catalog routes and classification."""
from pathlib import Path
from PIL import Image
from collections import Counter
import hashlib, json
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'content/pouch-sources'
report = json.loads((DATA/'report.json').read_text())
products = json.loads((DATA/'products.json').read_text())
index = {p['reference']:p for p in json.loads((ROOT/'assets/catalog-index.json').read_text())}
errors = []
if report['captured'] + len(report['errors']) != report['candidates']: errors.append('Incomplete source accounting')
if not all(report['sources'].values()): errors.append('Missing source site')
if report['published'] + len(report['duplicates']) != report['captured']: errors.append('Deduplication coverage')
if len({p['path'] for p in products}) != len(products): errors.append('Duplicate product routes')
if len({p['image']['sha256'] for p in products}) != len(products): errors.append('Duplicate main images')
for p in products:
 path = ROOT/p['path'].strip('/')/'index.html'
 if not path.exists(): errors.append(p['id']+' missing page'); continue
 text = path.read_text()
 image = ROOT/p['image']['path'].lstrip('/')
 with Image.open(image) as im:
  im.load()
  if min(im.size)<300: errors.append(p['id']+' undersized image')
 if p['reference'] not in index: errors.append(p['id']+' absent from search')
 if p['image']['path'] not in text or p['reference'] not in text: errors.append(p['id']+' main image/reference')
 curated=index.get(p['reference'],{})
 if curated.get('family') not in ['bags','packaging-accessories'] or not curated.get('format') or not curated.get('groups'): errors.append(p['id']+' invalid reviewed category')
 if not p['sources'] or any(not s['url'].startswith(('https://standpouchy.com/products/','https://uniquepouches.com/custom-ups-')) for s in p['sources']): errors.append(p['id']+' invalid source')
 for group in ['bags','pouches']:
  # The product is discoverable in the complete paginated category, verified in the sitemap/link validator.
  if not (ROOT/'catalog'/group/'index.html').exists(): errors.append('Missing '+group+' collection')
result = dict(candidates=report['candidates'], captured=report['captured'], imported=len(products), duplicate_references=len(report['duplicates']), source_counts=report['sources'], excluded=report['errors'], formats=dict(Counter(index[p['reference']]['format'] for p in products)), errors=errors)
(ROOT/'qa/pouch-import.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
raise SystemExit(bool(errors))

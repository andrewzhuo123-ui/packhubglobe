"""Capture live product references and verified local images from the two source sites."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from io import BytesIO
from PIL import Image, ImageOps, ImageChops, ImageStat
from bs4 import BeautifulSoup
import hashlib, json, re, time

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'content/pouch-sources'
DATA.mkdir(exist_ok=True)
(DATA / 'captures').mkdir(exist_ok=True)
IMAGES = ROOT / 'assets/images/pouch-catalog'
IMAGES.mkdir(exist_ok=True)

def fetch(url):
 for attempt in range(3):
  try:
   with urlopen(Request(url, headers={'User-Agent': 'PackHubGlobe catalog reference capture'}), timeout=45) as response:
    if response.status != 200: raise ValueError('HTTP ' + str(response.status))
    return response.read()
  except Exception:
   if attempt == 2: raise
   time.sleep(attempt + 1)

def capture(pair):
 site, url = pair
 key = site + '-' + url.rstrip('/').split('/')[-1].removesuffix('.html')
 cache = DATA / 'captures' / (key + '.json')
 if cache.exists():
  cached = json.loads(cache.read_text())
  if (ROOT / cached['image']['path'].lstrip('/')).exists(): return cached
 soup = BeautifulSoup(fetch(url), 'html.parser')
 main = soup.find('main')
 if not main or not main.h1: raise ValueError('No product content')
 name = main.h1.get_text(' ', strip=True)
 image = main.select_one('.product-main-image img') or main.find('img')
 if not image: raise ValueError('No product main image')
 image_url = urljoin(url, image['src'])
 raw = fetch(image_url)
 im = ImageOps.exif_transpose(Image.open(BytesIO(raw))).convert('RGB')
 if min(im.size) < 300: raise ValueError('Main image too small: ' + str(im.size))
 im.load()
 pixel_hash = hashlib.sha256(str(im.size).encode() + im.tobytes()).hexdigest()
 file = IMAGES / (pixel_hash[:20] + '.webp')
 if not file.exists(): im.save(file, 'WEBP', quality=90, method=6)
 facts = []
 if site == 'up':
  table = main.select_one('table.selection-specs')
  if table:
   for row in table.select('tr'):
    cells = row.select('th,td')
    if len(cells) == 2: facts.append([c.get_text(' ', strip=True) for c in cells])
 else:
  dls = main.find_all('dl')
  dl = next((d for d in dls if any(dt.get_text(' ', strip=True) == 'Pouch format' for dt in d.find_all('dt'))), dls[0] if dls else None)
  if dl:
   for dt in dl.find_all('dt'):
    dd = dt.find_next_sibling('dd')
    if dd: facts.append([dt.get_text(' ', strip=True), dd.get_text(' ', strip=True)])
  # Original product pages also carry project parameters in a table.
  if not facts:
   table = main.find('table')
   if table:
    for row in table.select('tr'):
     cells = row.select('th,td')
     if len(cells) == 2: facts.append([c.get_text(' ', strip=True) for c in cells])
 if not facts: raise ValueError('No specification fields')
 record = dict(site=site, url=url, name=name, image_url=image_url,
               image=dict(path='/' + str(file.relative_to(ROOT)), width=im.width, height=im.height, sha256=pixel_hash),
               facts=facts, captured='2026-10-19', main_text=main.get_text(' ', strip=True))
 cache.write_text(json.dumps(record, ensure_ascii=False, indent=2))
 return record

urls = []
for site, host in [('up','uniquepouches.com'), ('sp','standpouchy.com')]:
 sitemap = fetch('https://' + host + '/sitemap.xml').decode()
 (DATA / (site + '-sitemap.xml')).write_text(sitemap)
 candidates = re.findall(r'<loc>(.*?)</loc>', sitemap)
 urls += [(site,u) for u in candidates if (site == 'up' and '/custom-ups-' in u) or (site == 'sp' and '/products/' in u and u.rstrip('/').split('/')[-1] != 'products')]
print('Candidates:', len(urls), flush=True)
records = []; errors = []
with ThreadPoolExecutor(max_workers=12) as pool:
 jobs = {pool.submit(capture, pair): pair for pair in urls}
 for job in as_completed(jobs):
  try: records.append(job.result())
  except Exception as error: errors.append(dict(source=jobs[job], error=str(error)))
  if (len(records)+len(errors)) % 100 == 0: print('Captured',len(records),'failed',len(errors),flush=True)
def review_note(record):
 notes = re.search(r'Reference details to resolve\s+(.*?)\s+SP\d+ specification record', record['main_text'])
 if not notes: return ''
 note = re.sub(r'^Clarify these points before selection\.\s*', '', notes.group(1))
 return note if len(note) < 1800 and not re.search(r'StandPouchy|Unique Packaging|https?://',note,re.I) else ''

records.sort(key=lambda r:(r['site'] == 'sp',r['url']))
seen = {}; products = []; duplicates = []; visual_seen = []
for record in records:
 digest = record['image']['sha256']
 with Image.open(ROOT / record['image']['path'].lstrip('/')) as source_image:
  thumb = source_image.convert('RGB').resize((96,96))
  gray = thumb.convert('L').resize((17,16))
  pixels = list(gray.getdata())
  signature = sum((pixels[y*17+x] > pixels[y*17+x+1]) << (y*16+x) for y in range(16) for x in range(16))
  ratio = source_image.width / source_image.height
 if digest not in seen:
  for previous_signature, previous_thumb, previous_ratio, previous_digest in visual_seen:
   if abs(ratio-previous_ratio) < 0.02 and (signature ^ previous_signature).bit_count() <= 12:
    difference = ImageStat.Stat(ImageChops.difference(thumb,previous_thumb))
    if sum(difference.mean)/3 < 6 and sum(difference.rms)/3 < 12:
     digest = previous_digest
     break
 if digest in seen:
  seen[digest]['sources'].append(dict(url=record['url'], image_url=record['image_url']))
  if review_note(record): seen[digest]['review_note'] = review_note(record)
  duplicates.append(dict(url=record['url'], retained=seen[digest]['sources'][0]['url']))
  continue
 ref = 'PC-' + hashlib.sha256(record['url'].encode()).hexdigest()[:10].upper()
 name = re.sub(r'\s*[·|]\s*SP\d+.*$', '', record['name'])
 name = re.sub(r'\b(?:StandPouchy|Unique Packaging|Premium|High[ -]Barrier|Leak[ -]?Proof|BPA[ -]?Free|Certified|Wholesale|High[ -]Quality|Sustainable|Recyclable|Compostable|Food[- ]Grade|Eco[- ]Friendly)\b', '', name, flags=re.I)
 name = re.sub(r'\s+', ' ', name).strip()
 facts = []
 mapping = {'Illustrated format':'Structure / closure','Intended project':'Application','Film / laminate reference':'Film / laminate', 'Material reference':'Material','Opening & closure':'Opening','Thickness reference':'Thickness reference', 'Finish references':'Finish reference', 'Handle reference':'Handle reference', 'Volume reference':'Volume reference', 'Fill-weight reference':'Fill-weight reference', 'Dimensions reference':'Dimensions reference', 'Print references':'Printing','Pouch format':'Structure / closure', 'Material direction':'Material', 'Closure & opening':'Opening', 'Print route':'Printing', 'Surface finish':'Finish reference', 'Construction':'Structure / closure','Listed gauge':'Thickness reference', 'Candidate material':'Material','Opening':'Opening','Print / surface reference':'Printing'}
 for label,value in record['facts']:
  if label not in mapping: continue
  label = mapping[label]
  if re.search(r'Not specified|to confirm|certif|compost|recycl|biodegrad|food.grade|sustainab|eco.friendly|https?://', value, re.I): continue
  if len(value)>240: continue
  if label not in [k for k,v in facts]: facts.append([label,value])
 for label,value in [('Size','Custom size; confirm with a filled sample'),('Artwork','Custom artwork subject to proof approval')]:
  facts.append([label,value])
 text = (name + ' ' + ' '.join(v for k,v in facts if k == 'Structure / closure')).lower()
 group = 'pouch-spout' if re.search(r'spout|refill',text) else 'pouch-flat-bottom' if re.search(r'flat[ -]?bottom|box.pouch',text) else 'pouch-side-gusset' if re.search(r'side[ -]gusset',text) else 'pouch-flat' if re.search(r'three.side|3.side|flat pouch|sachet',text) else 'pouch-stand-up' if re.search(r'stand.up|doypack',text) else 'pouch-specialty'
 product = dict(id=ref, name=name, reference='PHG-'+ref, path='/catalog/'+re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-')[:75]+'-'+ref.lower()+'/', facts=facts,
                profile='pouch', family='bags', groups=['919632767',group], image=record['image'], sources=[dict(url=record['url'],image_url=record['image_url'])], detail=dict(title=name), source=dict(groups=['919632767',group]))
 if review_note(record): product['review_note'] = review_note(record)
 seen[digest]=product;products.append(product)
 visual_seen.append((signature,thumb,ratio,digest))
(DATA/'products.json').write_text(json.dumps(products,ensure_ascii=False,indent=2))
report=dict(candidates=len(urls),captured=len(records),published=len(products),sources={s:sum(r['site']==s for r in records) for s in ['up','sp']},duplicates=duplicates,errors=errors)
(DATA/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='duplicates'},indent=2),flush=True)

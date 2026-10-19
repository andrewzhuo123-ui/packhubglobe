"""Capture source pages and images; curate public fields from the reviewed TSV."""
from pathlib import Path
from urllib.request import Request,urlopen,install_opener,build_opener
from urllib.parse import urljoin,urlparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from bs4 import BeautifulSoup
from PIL import Image,ImageOps
from io import BytesIO
import hashlib,json,re,time,gzip
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'content/luxopack-sources';OUT=ROOT/'assets/images/luxopack-catalog'
DATA.mkdir(parents=True,exist_ok=True);(DATA/'captures').mkdir(exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
install_opener(build_opener())
def fetch(url):
 for n in range(3):
  try:
   with urlopen(Request(url,headers={'User-Agent':'PackHubGlobe product reference capture'}),timeout=30) as r:return r.read()
  except Exception:
   if n==2:raise
   time.sleep(n+1)
sitemap=fetch('https://luxopack.com/sitemap.xml').decode();(DATA/'sitemap.xml').write_text(sitemap)
urls=set(re.findall(r'<loc>(https://luxopack.com/products/.*?)</loc>',sitemap))
for base in ['https://luxopack.com/','https://luxopack.com/products/']:
 s=BeautifulSoup(fetch(base),'html.parser')
 urls.update(urljoin(base,a['href']).split('#')[0].rstrip('/') for a in s.select('a[href]') if urlparse(urljoin(base,a['href'])).path.startswith('/products/'))
urls.discard('https://luxopack.com/products')
print('Candidates',len(urls),flush=True)
def capture(url):
 slug=url.rstrip('/').split('/')[-1];cache=DATA/'captures'/(slug+'.json')
 if cache.exists():
  cached=json.loads(cache.read_text())
  if all((ROOT/i['path'].lstrip('/')).exists() for i in cached['images']):return cached
 raw=fetch(url);s=BeautifulSoup(raw,'html.parser');m=s.find('main') or s.body;assert m and m.h1,'No main/H1'
 hero=m.select_one('.lp-hero-media img') or m.select_one('.hero img') or m.select_one('img[src*="/assets/images/products/"]')
 assert hero,'No product image'
 imgs=list(dict.fromkeys(urljoin(url,i.get('src','')) for i in [hero]+m.select('img[src]') if '/assets/images/products/' in i.get('src','') and not i.find_parent(class_=re.compile('related|recommend'))))
 images=[]
 for u in imgs:
  b=fetch(u);im=ImageOps.exif_transpose(Image.open(BytesIO(b))).convert('RGB');im.load()
  if min(im.size)<300:continue
  digest=hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest();p=OUT/(digest[:20]+'.webp')
  if not p.exists():im.save(p,'WEBP',quality=90,method=6)
  item=dict(url=u,path='/'+str(p.relative_to(ROOT)),width=im.width,height=im.height,sha256=digest)
  if not any(i['sha256']==digest for i in images):images.append(item)
 assert images,'No valid product images'
 tables=[]
 for t in m.select('table'):
  rows=[]
  for tr in t.select('tr'):
   cells=tr.select('th,td')
   if len(cells)>=2:rows.append([c.get_text(' ',strip=True) for c in cells])
  if rows:tables.append(rows)
 assert tables,'No specification table'
 r=dict(url=url,title=m.h1.get_text(' ',strip=True),images=images,tables=tables,sections=[dict(heading=h.get_text(' ',strip=True),text=h.parent.get_text(' ',strip=True)) for h in m.select('h2')],main_text=m.get_text(' ',strip=True),captured='2026-10-19')
 cache.write_text(json.dumps(r,ensure_ascii=False,indent=2));(DATA/'captures'/(slug+'.html.gz')).write_bytes(gzip.compress(raw,mtime=0))
 return r
records=[];errors=[]
with ThreadPoolExecutor(max_workers=6) as pool:
 jobs={pool.submit(capture,u):u for u in sorted(urls)}
 for f in as_completed(jobs):
  try:records.append(f.result())
  except Exception as e:errors.append(dict(url=jobs[f],error=str(e)))
  if (len(records)+len(errors))%10==0:print('Captured',len(records),'errors',len(errors),flush=True)
(DATA/'captures.json').write_text(json.dumps(sorted(records,key=lambda x:x['url']),ensure_ascii=False,indent=2))
(DATA/'capture-report.json').write_text(json.dumps(dict(candidates=len(urls),captured=len(records),errors=errors),indent=2))
print('Complete',len(records),len(errors),flush=True)

# Public fields are individually reviewed against the captured images and tables.
from PIL import ImageChops,ImageStat
from collections import Counter
captures={r['url'].split('/')[-1]:r for r in records}
def fingerprint(path):
 with Image.open(ROOT/path.lstrip('/')) as im:
  thumb=im.convert('RGB').resize((96,96));gray=list(thumb.convert('L').resize((17,16)).getdata())
  bits=sum((gray[y*17+x]>gray[y*17+x+1])<<(y*16+x) for y in range(16) for x in range(16))
  return bits,thumb,im.width/im.height
existing=[(r,*fingerprint(r['image'])) for r in json.loads((ROOT/'assets/catalog-index.json').read_text()) if not r['reference'].startswith('PHG-LX-')]
materials={'rigid':'Wrapped rigid board; board, wrap and insert grades to confirm','mailer':'Corrugated board; grade and flute to confirm','carton':'Folding paperboard; grade and thickness to confirm','carry-box':'Folding paperboard; handle and base construction to confirm','food-box':'Paperboard; coating and intended contact conditions to confirm','paper-bag':'Paper carrier construction; paper, handle and reinforcement to confirm'}
facets={'Apparel':'921840222','Candles':'920793609','Tea and coffee':'920803216','Cosmetics':'803708590','Perfume':'803708590','Chocolate':'810538305','Dates and chocolate':'810538305','Food service':'810538305'}
review_slugs={line.split('|')[0] for line in (DATA/'review.tsv').read_text().splitlines()}
assert set(captures)==review_slugs|{'collapsible-magnetic-gift-box-wholesale','eco-friendly-packaging','jewelry-boxes'},'Unreviewed source routes remain'
products=[];duplicates=[]
for line in (DATA/'review.tsv').read_text().splitlines():
 slug,name,kind,primary,application,note=line.split('|');r=captures[slug];im=r['images'][0]
 bits,thumb,ratio=fingerprint(im['path']);match=None
 for old,b,t,rat in existing:
  if abs(ratio-rat)<.025 and (bits^b).bit_count()<=12:
   stats=ImageStat.Stat(ImageChops.difference(thumb,t))
   if max(stats.mean)<5 and max(stats.rms)<12:match=old;break
 if match:
  duplicates.append(dict(url=r['url'],existing_reference=match['reference'],existing_path=match['path']));continue
 key='LX-'+hashlib.sha256(r['url'].encode()).hexdigest()[:10].upper()
 path='/catalog/'+re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-')+'-'+key.lower()+'/'
 sources=[dict(url=r['url'],title=r['title'])]
 if slug=='shoulder-neck-rigid-box':
  alias=captures['collapsible-magnetic-gift-box-wholesale'];sources.append(dict(url=alias['url'],title=alias['title']))
 gallery=r['images'][1:] if slug!='custom-magnetic-rigid-gift-box-manufacturer' else []
 products.append(dict(id=key,reference='PHG-'+key,name=name,path=path,format=kind,family='bags' if kind=='paper-bag' else 'paper-boxes',groups=list(dict.fromkeys([primary]+([facets[application]] if application in facets else []))),image=im,gallery=gallery,facts=[['Material',materials[kind]],['Size','Custom dimensions; confirm internal measurements with the packed product'],['Printing','Custom artwork; confirm print route and finishing with the approved proof'],['Application',application]],review_note=note,detail=dict(title=r['title'],attributes=[]),sources=sources))
for p in products:
 for image in [p['image']]+p['gallery']:image['file_sha256']=hashlib.sha256((ROOT/image['path'].lstrip('/')).read_bytes()).hexdigest()
(DATA/'products.json').write_text(json.dumps(products,ensure_ascii=False,indent=2))
report=dict(source='https://luxopack.com',source_routes=len(urls),captured=len(records),errors=errors,excluded_collections=['https://luxopack.com/products/eco-friendly-packaging','https://luxopack.com/products/jewelry-boxes'],merged_source=dict(url='https://luxopack.com/products/collapsible-magnetic-gift-box-wholesale',retained='https://luxopack.com/products/shoulder-neck-rigid-box',reason='Equivalent main image; collapsible mechanism not established by photograph'),existing_duplicates=duplicates,published=len(products),main_images=len({p['image']['sha256'] for p in products}),detail_images=sum(len(p['gallery']) for p in products),formats=dict(Counter(p['format'] for p in products)))
(DATA/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if errors:raise SystemExit('Capture errors remain')

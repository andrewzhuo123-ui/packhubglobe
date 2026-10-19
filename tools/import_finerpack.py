"""Capture the live FinerPack product cards, detail fields and main photographs."""
from pathlib import Path
from urllib.request import Request,urlopen,install_opener,build_opener
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor,as_completed
from bs4 import BeautifulSoup
from PIL import Image,ImageOps
from io import BytesIO
import json,re,hashlib,gzip,time
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'content/finerpack-sources';OUT=ROOT/'assets/images/box-reference-catalog'
DATA.mkdir(exist_ok=True);(DATA/'captures').mkdir(exist_ok=True);OUT.mkdir(exist_ok=True)
install_opener(build_opener())
def fetch(url):
 for n in range(3):
  try:
   with urlopen(Request(url,headers={'User-Agent':'PackHubGlobe catalog reference capture'}),timeout=35) as r:return r.read()
  except Exception:
   if n==2:raise
   time.sleep(n+1)
raw=fetch('https://www.finerpack.com/products');(DATA/'directory.html.gz').write_bytes(gzip.compress(raw,mtime=0));s=BeautifulSoup(raw,'html.parser')
cards=[]
for c in s.select('article.marketplace-product-card'):
 cards.append(dict(id=c.get('data-paper-box') or c.get('data-marketplace-product'),url=urljoin('https://www.finerpack.com',c.select_one('a')['href']),name=c.select_one('h3,h4').get_text(' ',strip=True),image_url=urljoin('https://www.finerpack.com',c.img['src']),paper=c.has_attr('data-paper-box')))
assert cards and len({c['url'] for c in cards})==len(cards)
(DATA/'cards.json').write_text(json.dumps(cards,ensure_ascii=False,indent=2));print('Cards',len(cards),flush=True)
def capture(card):
 cache=DATA/'captures'/(card['id']+'.json')
 if cache.exists():
  r=json.loads(cache.read_text())
  if (ROOT/r['image']['path'].lstrip('/')).exists():return r
 raw=fetch(card['url']);s=BeautifulSoup(raw,'html.parser');m=s.main;assert m and m.h1,'No product H1'
 image=m.select_one('.paper-box-main-photo img') or m.select_one('img');assert image,'No main image'
 u=urljoin(card['url'],image['src']);im=ImageOps.exif_transpose(Image.open(BytesIO(fetch(u)))).convert('RGB');im.load();assert min(im.size)>=300,'Small image'
 digest=hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest();file=OUT/(digest[:20]+'.webp')
 if not file.exists():im.save(file,'WEBP',quality=90,method=6)
 facts=[]
 for dt in m.select('dl dt'):
  dd=dt.find_next_sibling('dd')
  if dd:facts.append([dt.get_text(' ',strip=True),dd.get_text(' ',strip=True)])
 for tr in m.select('table tr'):
  cols=tr.select('th,td')
  if len(cols)==2:facts.append([c.get_text(' ',strip=True) for c in cols])
 assert facts,'Missing specification fields'
 article=m.select_one('article');classes=article.get('class',[]) if article else []
 family=next((v.removeprefix('paper-box-layout-') for v in classes if v.startswith('paper-box-layout-')),'cosmetic')
 intent=m.select_one('.paper-box-intent');decision=m.select_one('.paper-box-decision')
 r=dict(**card,title=m.h1.get_text(' ',strip=True),family=family,image=dict(url=u,path='/'+str(file.relative_to(ROOT)),width=im.width,height=im.height,sha256=digest,file_sha256=hashlib.sha256(file.read_bytes()).hexdigest()),facts=facts,brief=intent.get_text(' ',strip=True) if intent else '',decision=decision.get_text(' ',strip=True) if decision else '',main_text=m.get_text(' ',strip=True),captured='2026-10-19')
 cache.write_text(json.dumps(r,ensure_ascii=False,indent=2));(DATA/'captures'/(card['id']+'.html.gz')).write_bytes(gzip.compress(raw,mtime=0));return r
rows=[];errors=[]
with ThreadPoolExecutor(max_workers=6) as pool:
 jobs={pool.submit(capture,c):c for c in cards}
 for f in as_completed(jobs):
  try:rows.append(f.result())
  except Exception as e:errors.append(dict(url=jobs[f]['url'],error=str(e)))
  if (len(rows)+len(errors))%40==0:print('Captured',len(rows),'errors',len(errors),flush=True)
rows.sort(key=lambda r:r['url']);(DATA/'capture-report.json').write_text(json.dumps(dict(candidates=len(cards),captured=len(rows),errors=errors),indent=2));print('Complete',len(rows),errors,flush=True)
if errors:raise SystemExit(1)

# Reviewed product identities remain separate from the unmodified source snapshots.
from PIL import ImageChops,ImageStat
from collections import Counter
review=json.loads((DATA/'review.json').read_text());assert set(review)=={r['id'] for r in rows},'Unreviewed product routes remain'
by_id={r['id']:r for r in rows}
def fingerprint(path):
 with Image.open(ROOT/path.lstrip('/')) as im:
  thumb=im.convert('RGB').resize((96,96));g=list(thumb.convert('L').resize((17,16)).getdata());bits=sum((g[y*17+x]>g[y*17+x+1])<<(y*16+x) for y in range(16) for x in range(16));return bits,thumb,im.width/im.height
existing=[(r,*fingerprint(r['image'])) for r in json.loads((ROOT/'assets/catalog-index.json').read_text()) if not r['reference'].startswith('PHG-FP-')]
products=[];duplicates=[];new=[]
materials={'rigid':'Rigid board with a paper wrap; complete construction to confirm','mailer':'Corrugated board; flute, grade and finished construction to confirm','carton':'Folding paperboard; grade and thickness to confirm','carry-box':'Paperboard; handle, base and carrying construction to confirm','food-box':'Paperboard; coating and intended contact conditions to confirm','pulp-insert':'Paper pulp; composition, forming process and wall geometry to confirm'}
facets={'Cosmetics':'803708590','Perfume':'803708590','Soap':'803708590','Candles':'920793609','Food gifts':'810538305','Food service':'810538305'}
def attr(r,*names):
 return next((v for k,v in r['facts'] if k.lower() in [x.lower() for x in names] and v),'')
def safe(value):
 value=re.sub(r'\b(?:FSC(?:[- ]certified)?|certified|eco[- ]friendly|recycled|recyclable|sustainable|food[- ]grade|premium|high[- ]quality|biodegradable)\b','',value,flags=re.I)
 value=re.sub(r'\s+',' ',value).strip(' ,;/-')
 return '' if re.search(r'https?://|Finer|ISO\s*9001|\$|\bMOQ\b|\d+\s*(?:pcs|pieces|days)',value,re.I) else value
for card in cards:
 r=by_id[card['id']];cur=review[r['id']];bits,t,ratio=fingerprint(r['image']['path']);match=None
 for old,b,thumb,rat in existing+new:
  if abs(ratio-rat)<.025 and (bits^b).bit_count()<=12:
   st=ImageStat.Stat(ImageChops.difference(t,thumb))
   if max(st.mean)<5 and max(st.rms)<12:match=old;break
 source=dict(url=r['url'],title=r['title'],source_id=r['id'])
 if match:
  duplicates.append(dict(source=source,retained_reference=match['reference'],retained_path=match['path']))
  if match.get('sources') is not None:match['sources'].append(source)
  continue
 kind=cur['format'];key='FP-'+r['id'];name=cur['name'];path='/catalog/'+re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-')+'-'+key.lower()+'/'
 material=safe(attr(r,'Material','Paper Type','Material Type'))
 if kind in ['rigid','pulp-insert','carry-box','food-box'] or not material or kind=='mailer' and not re.search('corrugat',material,re.I) or kind=='carton' and re.search('corrugat|rigid|greyboard',material,re.I):material=materials[kind]
 facts=[['Material',material],['Size',safe(attr(r,'Size','Dimensions')) or 'Custom dimensions; measurement convention to confirm']]
 printing=safe(attr(r,'Printing Handling','Printing','Surface Handling','Surface Finish'))
 if printing:facts.append(['Print / finish',printing[:220]])
 else:facts.append(['Printing','Surface marking subject to material and sample review' if kind=='pulp-insert' else 'Artwork, print route and finish to confirm'])
 insert=safe(attr(r,'Liner type','Insert'))
 if insert and insert.lower() not in ['none','no insert','no']:facts.append(['Insert / accessories',insert[:180]])
 facts.append(['Application',cur['application']])
 groups=[cur['primary']];app=cur['application']
 if app in facets:groups.append(facets[app])
 elif re.search('skin|cosmetic|fragrance|lash|lip|nail|beauty',app,re.I):groups.append('803708590')
 elif re.search('apparel|clothing',app,re.I):groups.append('921840222')
 elif re.search('candle',app,re.I):groups.append('920793609')
 p=dict(id=key,reference='PHG-'+key,name=name,path=path,format=kind,family='packaging-accessories' if kind=='pulp-insert' else 'paper-boxes',groups=list(dict.fromkeys(groups)),image=r['image'],facts=facts,review_note=cur['review_note'],detail=dict(title=r['title'],attributes=[]),sources=[source])
 products.append(p);new.append((p,bits,t,ratio))
(DATA/'products.json').write_text(json.dumps(products,ensure_ascii=False,indent=2))
report=dict(source='https://www.finerpack.com/products',candidates=len(cards),captured=len(rows),errors=errors,published=len(products),main_images=len({p['image']['sha256'] for p in products}),duplicates=duplicates,formats=dict(Counter(p['format'] for p in products)),visual_reviewed=len(review))
(DATA/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('Published',len(products),'duplicates',len(duplicates),dict(Counter(p['format'] for p in products)),flush=True)

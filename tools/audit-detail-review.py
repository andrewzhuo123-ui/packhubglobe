"""Regression checks for image relevance, copy consistency and preserved routes."""
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
from collections import defaultdict,Counter
import json,re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/deep-review';OUT.mkdir(parents=True,exist_ok=True)
records=json.loads((ROOT/'assets/catalog-index.json').read_text());by_path={x['path']:x for x in records}
expected={'paper-bags':{'paper-bag','paper-mailer'},'plastic-bags':{'poly','poly-mailer'},'cards-tags':{'print'},'stickers-labels':{'label'}}
errors=[];image_uses=defaultdict(int);blocks=0;unique=set();pages=0
for file in sorted(ROOT.rglob('*.html')):
 if any(p in ['.git','qa'] for p in file.relative_to(ROOT).parts):continue
 pages+=1;path='/'+str(file.relative_to(ROOT)).removesuffix('index.html');s=BeautifulSoup(file.read_text(),'html.parser')
 for node in s.select('main p,main li,main dt,main dd,main summary,main h1,main h2,main h3'):
  text=node.get_text(' ',strip=True)
  if not text:continue
  blocks+=1;unique.add(text)
  if re.search(r'[\u4e00-\u9fff]|\b(?:undefined|null|lorem ipsum|NaN)\b',text,re.I):errors.append((path,'unresolved copy',text))
  sentences=[x.strip() for x in re.split(r'(?<=[.!?])\s+',text) if len(x.split())>8]
  if any(n>1 for n in Counter(sentences).values()):errors.append((path,'repeated sentence',text))
 for img in s.select('img[src^="/"]'):
  image_uses[img['src']]+=1
 for family,kinds in expected.items():
  if path=='/products/'+family+'/':
   links=s.select('.ux-grid .ux-photo[href]')
   if not links:errors.append((path,'empty reference group'))
   for link in links:
    item=by_path[link['href']]
    if item['format'] not in kinds:errors.append((path,'unrelated reference',item['reference']))
 if path.startswith('/catalog/') and path in by_path:
  if len(s.select('.related-products .catalog-actions')):errors.append((path,'competing related-card quote actions'))
  if any(len(d.select('summary'))!=1 for d in s.select('.ux-technical-details')):errors.append((path,'invalid technical disclosure'))
 if path=='/materials/barrier-films/':
  image=s.select_one('.ux-material-photo img')
  if not image or '/pouch' not in image['src'] and not any(x['image']==image['src'] and x['format'] in {'stand-up','flat-bottom','spout'} for x in records):errors.append((path,'film page uses unrelated warehouse photograph'))
for src in image_uses:
 if src.endswith('.svg'):continue
 try:
  with Image.open(ROOT/src.lstrip('/')) as im:im.verify()
 except Exception as error:errors.append((src,'unreadable image',str(error)))
redirects=json.loads((ROOT/'content/catalog-redirects.json').read_text());rules=(ROOT/'.htaccess').read_text()
for old,new in redirects.items():
 if not (ROOT/new.strip('/')/'index.html').is_file():errors.append((old,'redirect target absent'))
 if (ROOT/old.strip('/')/'index.html').exists():errors.append((old,'obsolete duplicate page'))
 if new not in rules:errors.append((old,'Apache redirect missing'))
report={'html_pages':pages,'text_blocks':blocks,'unique_text_blocks':len(unique),'unique_images':len(image_uses),'raster_images':sum(not s.endswith('.svg') for s in image_uses),'catalog_products':len(records),'redirects':len(redirects),'errors':errors}
(OUT/'content-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(bool(errors))

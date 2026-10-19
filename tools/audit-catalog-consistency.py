"""Audit every public catalog product, collection and format page after rendering."""
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import hashlib, json, re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/catalog-audit';OUT.mkdir(parents=True,exist_ok=True)
index=json.loads((ROOT/'assets/catalog-index.json').read_text())
by_path={r['path']:r for r in index}
errors=[];pages=[];paragraphs=0

def check(ok,path,message):
 if not ok:errors.append(path+': '+message)

def read(path):
 return BeautifulSoup((ROOT/path.strip('/')/'index.html').read_text(),'html.parser')

def blocks(soup):
 global paragraphs
 result=[]
 for node in soup.select('main p,main li,main summary,main dt,main dd'):
  text=node.get_text(' ',strip=True);paragraphs+=1
  result.append({'text':text,'sha256':hashlib.sha256(text.encode()).hexdigest()})
 return result

for r in index:
 path=r['path'];s=read(path);main=s.select_one('main')
 check(len(s.select('h1'))==1 and s.h1.get_text(strip=True)==r['name'],path,'H1/name')
 check(r['name'] in s.title.get_text() and r['reference'] in s.title.get_text(),path,'title/name/SKU')
 check(s.select_one('link[rel=canonical]')['href']=='https://www.packhubglobe.com'+path,path,'canonical')
 image=s.select_one('.catalog-product-image img')
 check(image and image['src']==r['image'] and image['alt']==r['name'],path,'hero image')
 schemas=[]
 for node in s.select('script[type="application/ld+json"]'):
  obj=json.loads(node.string)
  schemas.extend(obj if isinstance(obj,list) else obj.get('@graph',[obj]))
 product=next(x for x in schemas if x.get('@type')=='Product')
 for key,value in [('name',r['name']),('sku',r['reference']),('url','https://www.packhubglobe.com'+path),('image','https://www.packhubglobe.com'+r['image'])]:
  check(product.get(key)==value,path,'schema '+key)
 facts={d.dt.get_text(' ',strip=True):d.dd.get_text(' ',strip=True) for d in s.select('.product-details .spec-list > div')}
 check(facts.get('Minimum order quantity')=='500 pieces',path,'MOQ')
 check('Dimensions reference' in facts,path,'dimension reference')
 intro=s.select_one('#reference-specification p').get_text(' ',strip=True)
 for label in ['Material reference','Film reference','Dimensions reference','Printing options','Print / finish options']:
  if label in facts:check(facts[label] in intro,path,'intro contradicts '+label)
 message=parse_qs(urlparse(r['chat']).query)['text'][0]
 check(all(v in message for v in [r['name'],r['reference'],'https://www.packhubglobe.com'+path]),path,'search inquiry')
 for a in s.select('.detailcopy a[href*="request-quote"],.help-note a[href*="request-quote"]'):
  value=parse_qs(urlparse(a['href']).query).get('product',[''])[0]
  check(r['name'] in value and r['reference'] in value,path,'quote context')
 check(s.select_one('.detailcopy .eyebrow').get_text(strip=True)==r['groups'][0],path,'primary collection')
 related=[by_path[a['href']] for a in s.select('.related-products .catalog-photo')]
 check(len(related)==3 and len({x['path'] for x in related})==3,path,'related count/duplicates')
 same=sum(x['format']==r['format'] for x in index)-1
 check(sum(x['format']==r['format'] for x in related)==min(same,3),path,'related format')
 check(all(x['family']==r['family'] for x in related),path,'related family')
 if r['format'] in ['spout','drink-pouch','flat','side-gusset','flat-bottom','roll-bag','paper-mailer']:
  check('Keep the pouch standing' not in main.get_text(' ',strip=True),path,'incorrect standing assumption')
 check('856 products' not in main.get_text(),path,'obsolete catalog count')
 pages.append({'path':path,'reference':r['reference'],'format':r['format'],'blocks':blocks(s)})

# Every collection card is checked against its corresponding product page data.
collections=[];collection_members={}
for file in sorted((ROOT/'catalog').rglob('index.html')):
 path='/'+file.parent.relative_to(ROOT).as_posix()+'/'
 if path in by_path:continue
 s=read(path);base=re.sub(r'/page-\d+/$','/',path)
 collection_members.setdefault(base,[])
 cards=s.select('.catalog-grid:not(.related-products) .catalog-card')
 check(bool(cards),path,'empty collection')
 check(len(s.select('h1'))==1,path,'collection heading')
 for card in cards:
  a=card.select_one('.catalog-photo');r=by_path.get(a['href'])
  check(r is not None,path,'unknown product')
  if not r:continue
  collection_members[base].append(r['path'])
  if base not in ['/catalog/','/catalog/paper-boxes/','/catalog/bags/','/catalog/packaging-accessories/']:
   check(s.h1.get_text(strip=True).rstrip('.') in r['groups'],path,'group membership')
  check(card.select_one('h2,h3').get_text(' ',strip=True)==r['name'],path,'card name')
  check(a.img['src']==r['image'] and a.img['alt']==r['name'],path,'card image')
  check(card.select_one('.catalog-ref').get_text(strip=True)==r['reference'],path,'card reference')
  group=re.sub(r'/page-\d+/$','/',path).split('/')[-2]
  if group in ['paper-boxes','bags','packaging-accessories']:check(r['family']==group,path,'family membership')
 collections.append({'path':path,'cards':len(cards),'blocks':blocks(s)})

for base,members in collection_members.items():
 check(len(members)==len(set(members)),base,'duplicate across pagination')
 if base=='/catalog/':expected_members=set(by_path)
 else:
  title=read(base).h1.get_text(strip=True).rstrip('.')
  family=base.split('/')[-2]
  expected_members={r['path'] for r in index if (r['family']==family if family in ['paper-boxes','bags','packaging-accessories'] else title in r['groups'])}
 check(set(members)==expected_members,base,'incomplete paginated membership')

# Regressions found by visual review: these images must not revert to source labels.
expected={'PC-674101D769':'flat','PC-AB4E9973DC':'stand-up','PC-653374F80E':'container-reference','PC-34A0E94A43':'container-reference','PC-EA49A18AF7':'container-reference'}
for key,kind in expected.items():
 r=next(x for x in index if x['reference']=='PHG-'+key)
 check(r['format']==kind,r['path'],'visual regression '+kind)
for key,word in [('PC-674101D769','mask'),('PC-AB4E9973DC','litter'),('PC-B301EE847D','detergent')]:
 r=next(x for x in index if x['reference']=='PHG-'+key)
 check(word in r['name'].lower(),r['path'],'visual application regression')
formats=[]
for file in sorted((ROOT/'products').glob('*/*/index.html')):
 path='/'+file.parent.relative_to(ROOT).as_posix()+'/'
 s=read(path);check(len(s.select('h1'))==1,path,'format heading')
 check(bool(s.select('a[href^="/catalog/"]')),path,'format collection link')
 formats.append({'path':path,'blocks':blocks(s)})
old=json.loads((ROOT/'content/alibaba-catalog/item-paths.json').read_text())
old.update({p['id']:p['path'] for p in json.loads((ROOT/'content/pouch-sources/products.json').read_text())})
old.update({p['id']:p['path'] for p in json.loads((ROOT/'content/luxopack-sources/products.json').read_text())})
check(set(old.values())==set(by_path),'catalog','stable published product URLs')
report={'products':len(index),'collections_including_pagination':len(collections),'format_pages':len(formats),'text_blocks_checked':paragraphs,'formats':dict(Counter(r['format'] for r in index)),'visual_review_products':1461+len(json.loads((ROOT/'content/luxopack-sources/products.json').read_text())),'visual_corrections':len(json.loads((ROOT/'content/catalog-review.json').read_text())),'errors':errors}
(OUT/'summary.json').write_text(json.dumps(report,indent=2))
(OUT/'page-evidence.json').write_text(json.dumps({'products':pages,'collections':collections,'format_pages':formats},indent=2))
print(json.dumps(report,indent=2));raise SystemExit(bool(errors))

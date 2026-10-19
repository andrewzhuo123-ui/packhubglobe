"""Validate source coverage, curated pages, local assets and preserved existing products."""
from pathlib import Path
from PIL import Image
from bs4 import BeautifulSoup
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'content/finerpack-sources'
report=json.loads((DATA/'report.json').read_text());products=json.loads((DATA/'products.json').read_text());captures=[json.loads(p.read_text()) for p in sorted((DATA/'captures').glob('*.json'))];review=json.loads((DATA/'review.json').read_text())
index={p['reference']:p for p in json.loads((ROOT/'assets/catalog-index.json').read_text())};errors=[]
def check(ok,message):
 if not ok:errors.append(message)
check(not report['errors'] and report['candidates']==report['captured']==len(captures)==len(review),'Capture/review accounting')
check(len(products)+len(report['duplicates'])==len(captures),'Duplicate disposition accounting')
source_urls={r['url'] for r in captures};accounted={s['url'] for p in products for s in p['sources']}|{d['source']['url'] for d in report['duplicates']}
check(source_urls==accounted,'Incomplete provenance coverage')
check(len({p['path'] for p in products})==len(products),'Duplicate routes')
check(len({p['image']['sha256'] for p in products})==len(products),'Duplicate main images')
for p in products:
 key=p['reference'];r=index[key];s=BeautifulSoup((ROOT/p['path'].strip('/')/'index.html').read_text(),'html.parser')
 check(r['name']==p['name'] and r['family']==p['family'] and r['format']==p['format'],key+' curated identity')
 check(s.h1.get_text(strip=True)==p['name'] and p['review_note'] in s.get_text(' ',strip=True),key+' reviewed copy')
 image=ROOT/p['image']['path'].lstrip('/')
 with Image.open(image) as im:
  im.load();check(min(im.size)>=300 and im.size==(p['image']['width'],p['image']['height']),key+' decoded main image')
 check(hashlib.sha256(image.read_bytes()).hexdigest()==p['image']['file_sha256'],key+' image integrity')
 main=s.main.get_text(' ',strip=True)
 check(not any(v in main for v in ['Finer Pack','FinerPack','REFERENCE PRICE','1000 pieces','sales02@finer-packaging.com','FSC-certified','ISO 9001']),key+' source commercial terms')
for d in report['duplicates']:check(d['retained_reference'] in index and index[d['retained_reference']]['path']==d['retained_path'],'Missing deduplicated product')
old=json.loads(subprocess.check_output(['git','show','2afd4090:assets/catalog-index.json'],cwd=ROOT,text=True))
check(all(r==index.get(r['reference']) for r in old),'Existing catalog identity or attributes changed')
result=dict(captured=len(captures),published=len(products),duplicates=len(report['duplicates']),linked_existing=sum(not d['retained_reference'].startswith('PHG-FP-') for d in report['duplicates']),images=len(products),preserved_existing=len(old),errors=errors)
(ROOT/'qa/finerpack/validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));raise SystemExit(bool(errors))

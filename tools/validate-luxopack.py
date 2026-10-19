"""Check source accounting, asset integrity, classification and unchanged prior products."""
from pathlib import Path
from PIL import Image
from bs4 import BeautifulSoup
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'content/luxopack-sources'
report=json.loads((DATA/'report.json').read_text());products=json.loads((DATA/'products.json').read_text());captures=json.loads((DATA/'captures.json').read_text())
index={p['reference']:p for p in json.loads((ROOT/'assets/catalog-index.json').read_text())};errors=[]
def check(ok,message):
 if not ok:errors.append(message)
check(not report['errors'] and report['captured']==report['source_routes']==len(captures),'Source capture coverage')
check(report['published']+len(report['excluded_collections'])+1+len(report['existing_duplicates'])==report['captured'],'Source disposition accounting')
check(len({p['image']['sha256'] for p in products})==len(products),'Duplicate main images')
check(len({p['path'] for p in products})==len(products),'Duplicate product paths')
for p in products:
 key=p['reference'];s=BeautifulSoup((ROOT/p['path'].strip('/')/'index.html').read_text(),'html.parser');r=index[key]
 check(r['name']==p['name'] and r['format']==p['format'] and r['family']==p['family'],key+' classification')
 check(s.h1.get_text(strip=True)==p['name'] and p['review_note'] in s.get_text(' ',strip=True),key+' reviewed content')
 check(all(source['url'].startswith('https://luxopack.com/products/') for source in p['sources']),key+' provenance')
 for im in [p['image']]+p['gallery']:
  file=ROOT/im['path'].lstrip('/')
  with Image.open(file) as decoded:
   decoded.load();check(min(decoded.size)>=300 and decoded.size==(im['width'],im['height']),key+' valid dimensions')
  check(hashlib.sha256(file.read_bytes()).hexdigest()==im['file_sha256'],key+' image integrity')
  check(bool(s.select('img[src="'+im['path']+'"]')),key+' visible image reference')
 main=s.select_one('main').get_text(' ',strip=True)
 check(all(text not in main for text in ['LuxoPack','ISO 9001','FSC-certified','100 pcs','sales@luxopack.com','13352991594']),key+' source commercial terms')
old=json.loads(subprocess.check_output(['git','show','045cd0fd:assets/catalog-index.json'],cwd=ROOT,text=True))
check(all(p==index.get(p['reference']) for p in old),'Prior catalog records changed')
result=dict(captured=len(captures),published=len(products),main_images=report['main_images'],detail_images=report['detail_images'],retained_existing_products=len(old),errors=errors)
(ROOT/'qa/luxopack/validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));raise SystemExit(bool(errors))

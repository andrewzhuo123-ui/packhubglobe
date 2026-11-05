"""Core-page image regression: matching records, available assets and no repeat photos."""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
class Photos(HTMLParser):
 def __init__(self):super().__init__();self.images=[]
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='img' and not attrs.get('src','').endswith('.svg'):self.images.append(attrs)
records=json.loads((ROOT/'assets/catalog-index.json').read_text())
selection=json.loads((ROOT/'content/visual-selection.json').read_text())
by_ref={item['reference']:item for item in records}
selected=[*selection['home_hero'],*selection['home_categories'],*selection['home_portfolio'],*selection['home_industries'].values()]
assert len(selected)==len({by_ref[ref]['image'] for ref in selected}),'Homepage selections repeat'
errors=[];pages=[]
for file in [ROOT/'index.html',*sorted((ROOT/'products').rglob('index.html')),*sorted((ROOT/'industries').rglob('index.html'))]:
 photos=Photos();photos.feed(file.read_text());hashes=[]
 for photo in photos.images:
  asset=ROOT/photo['src'].lstrip('/')
  if not asset.is_file():errors.append(str(file.relative_to(ROOT))+': missing '+photo['src']);continue
  hashes.append(hashlib.sha256(asset.read_bytes()).hexdigest())
  if not photo.get('alt'):errors.append(str(file.relative_to(ROOT))+': missing alt')
 duplicates=[key for key,count in Counter(hashes).items() if count>1]
 if duplicates:errors.append(str(file.relative_to(ROOT))+': repeated image content')
 pages.append({'path':'/'+str(file.relative_to(ROOT)).removesuffix('index.html'),'images':len(photos.images),'duplicates':len(duplicates)})
for slug,refs in selection['industries'].items():
 assert len(refs)==4 and len({by_ref[ref]['image'] for ref in refs})==4,slug
for slug,reference in json.loads((ROOT/'content/format-references.json').read_text()).items():
 assert by_ref[reference['reference']]['image']==reference['image'],slug
report={'pages':pages,'errors':errors}
out=ROOT/'qa/visual-selection';out.mkdir(exist_ok=True);(out/'static.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'Checked {len(pages)} core pages; {len(errors)} image errors')
assert not errors,errors

"""Verify the requested catalog, inquiry and long-form content changes."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, parse_qs
import json, re

ROOT=Path(__file__).resolve().parents[1]
class Content(HTMLParser):
 def __init__(self,text,target):
  super().__init__();self.target=target;self.depth=0;self.words=[];self.feed(text)
 def handle_starttag(self,tag,attrs):
  if tag in ['img','input','br','hr','source','meta','link']:return
  if self.depth:self.depth+=1
  elif self.target in dict(attrs).get('class','').split() or self.target=='main' and tag=='main':self.depth=1
 def handle_endtag(self,tag):
  if self.depth:self.depth-=1
 def handle_data(self,value):
  if self.depth:self.words+=re.findall(r"\b[\w'-]+\b",value)

index=json.loads((ROOT/'assets/catalog-index.json').read_text());paths=json.loads((ROOT/'content/alibaba-catalog/item-paths.json').read_text())
errors=[];product_words=[];guide_words={}
for item in index:
 text=(ROOT/item['path'].strip('/')/'index.html').read_text()
 message=parse_qs(urlparse(item['chat']).query).get('text',[''])[0]
 if item['facts'][0]!=['MOQ','500 pieces'] or len(item['facts'])<4:errors.append(item['reference']+' card attributes')
 if urlparse(item['chat']).netloc!='wa.me' or '/8615105916426' not in item['chat']:errors.append(item['reference']+' WhatsApp number')
 if not all(s in message for s in [item['reference'],'Quantity: 500 pieces', 'https://www.packhubglobe.com'+item['path']]):errors.append(item['reference']+' inquiry message')
 count=len(Content(text,'tank-content').words);product_words.append(count)
 if count<900 or any('id="'+anchor+'"' not in text for anchor in ['reference-specification','customization','sample-review','order-planning','product-questions']):errors.append(item['reference']+' long-form sections')
 if item['path']!=paths[item['reference'].removeprefix('PHG-')]:errors.append(item['reference']+' changed URL')
for file in (ROOT/'guides').glob('*/index.html'):
 text=file.read_text();guide_words[file.parent.name]=len(Content(text,'guide-longform').words)
 if guide_words[file.parent.name]<700 or 'id="guide-faq"' not in text or '"@type": "Article"' not in text:errors.append(file.parent.name+' guide expansion')
families={key:sum(item['family']==key for item in index) for key in ['paper-boxes','bags','packaging-accessories']}
if sum(families.values())!=len(index) or not all(families.values()):errors.append('Family coverage')
home_words=len(Content((ROOT/'index.html').read_text(),'main').words)
if home_words<700:errors.append('Homepage expansion')
report={'products':len(index),'families':families,'product_longform_words_min':min(product_words),'product_longform_words_max':max(product_words),'guide_words':guide_words,'home_words':home_words,'errors':errors}
(ROOT/'qa/depth').mkdir(exist_ok=True);(ROOT/'qa/depth/acceptance.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));raise SystemExit(bool(errors))

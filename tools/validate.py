from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
from collections import deque,Counter
import json,re,csv,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1];ORIGIN='https://www.packhubglobe.com'
class Page(HTMLParser):
 def __init__(self,text):
  super().__init__();self.tags=[];self.ids=set();self.duplicate_ids=[];self.links=[];self.schema=[];self.buffer='';self.in_schema=False;self.h1=0;self.title='';self.in_title=False;self.text=[];self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);self.tags.append((tag,a))
  if tag=='h1':self.h1+=1
  if 'id' in a:
   if a['id'] in self.ids:self.duplicate_ids.append(a['id'])
   self.ids.add(a['id'])
  if tag=='a':self.links.append(a.get('href',''))
  if tag=='title':self.in_title=True
  if tag=='script' and a.get('type')=='application/ld+json':self.in_schema=True;self.buffer=''
 def handle_data(self,value):
  if self.in_schema:self.buffer+=value
  elif self.in_title:self.title+=value
  else:self.text.append(value)
 def handle_endtag(self,tag):
  if tag=='title':self.in_title=False
  if tag=='script' and self.in_schema:self.schema.append(json.loads(self.buffer));self.in_schema=False

pages={};errors=[];links_checked=0;assets=set();descriptions=[];graph={}
for file in ROOT.rglob('*.html'):
 if any(p in ['.git','qa'] for p in file.relative_to(ROOT).parts):continue
 path='/404.html' if file.name=='404.html' else '/'+str(file.relative_to(ROOT)).removesuffix('index.html')
 text=file.read_text();p=Page(text);pages[path]=p
 if p.duplicate_ids:errors.append(path+': duplicate IDs '+repr(p.duplicate_ids))
 if re.search(r'\b(?:Cutomized|Customezed|Offest|Carboard|Partone|Panton|Prinitng)\b',' '.join(p.text)):errors.append(path+': uncorrected source spelling')
 if p.h1!=1:errors.append(path+': H1 count '+str(p.h1))
 if not p.title:errors.append(path+': missing title')
 for tag in ['header','nav','main','footer']:
  if not any(t==tag for t,a in p.tags):errors.append(path+': missing '+tag)
 canon=[a.get('href') for t,a in p.tags if t=='link' and a.get('rel')=='canonical']
 if len(canon)!=1 or (path!='/404.html' and canon[0]!=ORIGIN+path):errors.append(path+': canonical mismatch')
 desc=[a.get('content') for t,a in p.tags if t=='meta' and a.get('name')=='description']
 if len(desc)!=1 or not desc[0]:errors.append(path+': missing description')
 elif path!='/404.html':descriptions.append(desc[0])
 robots=[a.get('content') for t,a in p.tags if t=='meta' and a.get('name')=='robots']
 if robots!=['noindex,follow' if path=='/404.html' else 'index,follow']:errors.append(path+': robots mismatch')
 if not p.schema:errors.append(path+': missing JSON-LD')
 if re.search(r'localhost|chatgpt\.site|Frontend design preview|Editorial concept|prototype|/planning/',text,re.I):errors.append(path+': preview content')
 if path not in ['/about/','/factory/'] and re.search(r'Xiamen|Finer Pack|Unique Packaging|uniquepouches|finerpack',text,re.I):errors.append(path+': company details outside About / Factory')
 for email in re.findall(r'mailto:([^?"\s]+)',text):
  if email!='andrew@packhubglobe.com':errors.append(path+': unexpected email')
 for tag,a in p.tags:
  if tag=='a' and a.get('target')=='_blank' and 'noopener' not in a.get('rel',''):errors.append(path+': external tab missing noopener')
  if tag=='main' and a.get('tabindex')!='-1':errors.append(path+': skip-link target is not focusable')
  if tag=='img':
   if not a.get('alt') or not a.get('width') or not a.get('height'):errors.append(path+': image missing alt or dimensions')
  if tag in ['video','source']:
   for key in ['src','poster','data-desktop','data-mobile']:
    value=a.get(key)
    if value and value.startswith('/'):
     assets.add(urlparse(value).path.lstrip('/'))
     if not (ROOT/urlparse(value).path.lstrip('/')).is_file():errors.append(path+': missing media '+value)
  resource=a.get('src') if tag in ['img','script'] else a.get('href') if tag=='link' and a.get('rel') in ['stylesheet','icon'] else None
  if resource:
   if resource.startswith('/'):
    target=ROOT/unquote(urlparse(resource).path.lstrip('/'));assets.add(str(target.relative_to(ROOT)))
    if not target.is_file():errors.append(path+': missing asset '+resource)
   else:errors.append(path+': external runtime resource '+resource)
for path,p in pages.items():
 for block in re.findall(r'<dl class="spec-list">(.*?)</dl>',(ROOT/path.strip('/')/'index.html').read_text() if path!='/404.html' else '',re.S):
  labels=re.findall(r'<dt>(.*?)</dt>',block)
  if len(labels)!=len(set(labels)):errors.append(path+': duplicate specification fields')
 graph[path]=[]
 for href in p.links:
  if not href or href in ['#','javascript:void(0)']:errors.append(path+': empty action');continue
  u=urlparse(href)
  if u.scheme or u.netloc:continue
  target=u.path or path
  if target.endswith('/') or target=='/404.html':
   if target not in pages:errors.append(path+': missing link '+href)
   else:
    graph[path].append(target)
    if u.fragment and unquote(u.fragment) not in pages[target].ids:errors.append(path+': missing anchor '+href)
  elif not (ROOT/unquote(target.lstrip('/'))).is_file():errors.append(path+': missing file '+href)
  links_checked+=1
for path in set(re.findall(r'url\([\'"]?([^\)\'\"]+)',(ROOT/'assets/style.css').read_text())):
 if path.startswith('/'):
  assets.add(path.lstrip('/'))
  if not (ROOT/path.lstrip('/')).is_file():errors.append('CSS missing asset '+path)
 elif not path.startswith('data:'):errors.append('Unexpected CSS resource '+path)
public=set(pages)-{'/404.html'}
planned={urlparse(r['url']).path for r in csv.DictReader((ROOT/'content/page-map.csv').open(encoding='utf-8-sig'))}
if public!=planned:errors.append('Planned-route mismatch: '+repr(public^planned))
tree=ET.parse(ROOT/'sitemap.xml');sitemap=[n.text for n in tree.findall('.//{*}loc')]
if set(sitemap)!={ORIGIN+p for p in public} or len(sitemap)!=len(public):errors.append('Sitemap mismatch')
seen={'/'};queue=deque(['/'])
while queue:
 for target in graph[queue.popleft()]:
  if target not in seen:seen.add(target);queue.append(target)
if public-seen:errors.append('Unreachable pages: '+repr(public-seen))
if len(set(p.title for path,p in pages.items() if path!='/404.html'))!=len(public):errors.append('Duplicate titles')
if len(set(descriptions))!=len(public):errors.append('Duplicate descriptions')
status={'status':'passed' if not errors else 'failed','public_pages':len(public),'html_files':len(pages),'planned_routes_covered':len(public&planned),'sitemap_urls':len(sitemap),'internal_links':links_checked,'referenced_assets':len(assets),'reachable_pages':len(seen&public),'jsonld_blocks':sum(len(p.schema) for p in pages.values()),'errors':errors}
(ROOT/'qa').mkdir(exist_ok=True);(ROOT/'qa/validation.json').write_text(json.dumps(status,indent=2));print(json.dumps(status,indent=2));raise SystemExit(bool(errors))

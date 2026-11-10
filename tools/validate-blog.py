"""Verify the owner's article contract against source and rendered HTML."""
from pathlib import Path
from collections import Counter
import argparse,json,re
from datetime import date
from hashlib import sha256
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
def words(text):return len(re.findall(r"\b[A-Za-z0-9]+(?:['’-][A-Za-z0-9]+)*\b",text))
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--batch-date',type=date.fromisoformat)
batch_date=parser.parse_args().batch_date
report=[];errors=[];categories=Counter();batch_count=0
image_owners={}
for source in sorted((ROOT/'content/blog').glob('*.md')):
 _,metadata,markdown=source.read_text().split('---',2)
 meta={k:json.loads(v) for line in metadata.strip().splitlines() for k,v in [line.split(': ',1)]}
 page=BeautifulSoup((ROOT/'blog'/source.stem/'index.html').read_text(),'html.parser')
 article=page.select_one('.blog-article');categories[meta['category']]+=1
 sections=article.select('section');depths=[words(d.get_text(' ',strip=True)) for d in article.select('.blog-depth')]
 own=[]
 body_text=' '.join(p.get_text(' ',strip=True) for p in article.select('p,h2,h3,th,td') if not p.find_parent('aside') and not p.find_parent('figcaption'))
 total=words(body_text)
 if total<1000:own.append('Article below 1000 words')
 if len(depths)!=4 or min(depths)<200:own.append('Dive deeper section below 200 words or missing')
 images=article.select('img')
 if len(images)!=5:own.append('Expected one hero and four section images')
 for slot,image in enumerate(images,1):
  src=image.get('src','')
  asset=ROOT/src.lstrip('/')
  if not src.startswith('/assets/') or not asset.is_file() or not image.get('alt','').strip():
   own.append(f'Missing local image or alt text in slot {slot}: {src}')
   continue
  digest=sha256(asset.read_bytes()).hexdigest()
  location=f'{source.stem} image {slot}'
  if digest in image_owners:
   own.append(f'Duplicate image in slot {slot}: {src} already used by {image_owners[digest]}')
  else:
   image_owners[digest]=location
 if images and (meta.get('image')!=images[0].get('src') or meta.get('imageAlt')!=images[0].get('alt')):
  own.append('Frontmatter cover image or alt text differs from the rendered cover')
 # The opening paragraphs are direct children; section paragraphs have the same contract.
 openings=[article.find_all('p',recursive=False)[:3]]+[s.find_all('p',recursive=False)[:2] for s in sections if s.get('id')!='conclusion']
 for i,opening in enumerate(openings):
  if len(opening)<2 or words(opening[0].get_text())>30 or words(opening[1].get_text())>50 or not opening[1].find('strong'):own.append('PAS/answer limit or bold answer failed at '+str(i))
 for p in article.select('p'):
  if words(p.get_text())>150:own.append('Paragraph above 150 words')
 for s in sections:
  if s.get('id')!='conclusion' and not s.h2.get_text().endswith('?'):own.append('Non-question H2')
 if words(article.select_one('#conclusion p').get_text())>30:own.append('Conclusion above 30 words')
 external={a['href'] for a in article.select('a[href^="https://"]')}
 internal={a['href'] for a in article.select('a[href^="/"]')}
 if len(external)!=2 or len(internal)!=3:own.append('Expected five contextual/source destinations')
 if len(article.select('.blog-sources li'))!=2:own.append('Expected two footnotes')
 published=date.fromisoformat(meta['publishedAt'])
 batch_count+=published==batch_date
 if page.select_one('time')['datetime']!=published.isoformat() or page.select_one('time').get_text()!=published.strftime('%-d %B %Y'):own.append('Publication date mismatch')
 graph=json.loads(page.select_one('script[type="application/ld+json"]').string)['@graph'];schema=next(n for n in graph if n['@type']=='Article')
 if schema['datePublished']!=meta['publishedAt'] or schema['author']['name']!=meta['author']:own.append('Article schema mismatch')
 if re.search(r'Leading paragraph:|featured paragraph:|Dive deeper paragraph:|\[图片占位符\]',article.get_text(),re.I):own.append('Visible writing instructions')
 report.append(dict(slug=source.stem,words=total,diveDeeperWords=depths,internalLinks=len(internal),externalLinks=len(external),images=len(article.select('img')),errors=own))
 errors.extend(source.stem+': '+e for e in own)
expected={c['slug'] for c in json.loads((ROOT/'content/blog-categories.json').read_text())}
if set(categories)!=expected:errors.append('Blog categories do not match the configured topics')
if batch_date and batch_count!=3:errors.append(f'Expected three posts dated {batch_date}, found {batch_count}')
result=dict(status='passed' if not errors else 'failed',articles=report,categories=dict(categories),uniqueArticleImages=len(image_owners),errors=errors)
out=ROOT/'qa'/('blog-'+(batch_date.isoformat() if batch_date else 'inventory'));out.mkdir(parents=True,exist_ok=True);(out/'content-gates.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2));raise SystemExit(bool(errors))

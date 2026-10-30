"""Resize homepage reference photos without cropping or altering the product."""
from pathlib import Path
from html.parser import HTMLParser
from PIL import Image
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
class Photos(HTMLParser):
 def __init__(self):super().__init__();self.paths=set()
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='img' and attrs.get('src','').startswith('/assets/') and not attrs['src'].endswith('.svg'):self.paths.add(attrs['src'])
photos=Photos();photos.feed((ROOT/'index.html').read_text())
folder=ROOT/'assets/responsive';folder.mkdir(exist_ok=True)
manifest={}
for source in sorted(photos.paths):
 with Image.open(ROOT/source.lstrip('/')) as image:
  image=image.convert('RGB');variants=[]
  for width in [320,640]:
   if image.width<=width:continue
   output=folder/(hashlib.sha256(source.encode()).hexdigest()[:16]+'-'+str(width)+'.webp')
   image.resize((width,round(image.height*width/image.width)),Image.Resampling.LANCZOS).save(output,'WEBP',quality=84,method=6)
   variants.append(['/'+str(output.relative_to(ROOT)),width])
  if variants:manifest[source]=variants+[[source,image.width]]
(folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Prepared responsive variants for',len(manifest),'reference images')

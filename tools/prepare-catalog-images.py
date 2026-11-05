"""Extend the existing responsive manifest with actual catalog image variants."""
from pathlib import Path
from PIL import Image
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'assets/responsive'
manifest=json.loads((folder/'manifest.json').read_text())
records=json.loads((ROOT/'assets/catalog-index.json').read_text())
for source in sorted({r['image'] for r in records}|{im for r in records for im in r.get('gallery',[])}):
 if source in manifest:continue
 with Image.open(ROOT/source.lstrip('/')) as image:
  image=image.convert('RGB');variants=[]
  for width in [320,640]:
   if image.width<=width:continue
   output=folder/(hashlib.sha256(source.encode()).hexdigest()[:16]+'-'+str(width)+'.webp')
   image.resize((width,round(image.height*width/image.width)),Image.Resampling.LANCZOS).save(output,'WEBP',quality=82,method=4)
   variants.append(['/'+str(output.relative_to(ROOT)),width])
  if variants:manifest[source]=variants+[[source,image.width]]
(folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Responsive manifest:',len(manifest),'images')

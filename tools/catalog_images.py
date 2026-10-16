"""Save merchant-owned catalog main images locally for static hosting."""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
import json
import urllib.request
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'content/alibaba-catalog'
OUT = ROOT / 'assets/catalog'
OUT.mkdir(parents=True, exist_ok=True)


def download(product):
    target = OUT / (product['id'] + '.webp')
    url = product['image']
    if url.startswith('//'):
        url = 'https:' + url
    try:
        if not target.exists():
            with urllib.request.urlopen(url, timeout=45) as response:
                image = ImageOps.exif_transpose(Image.open(BytesIO(response.read())))
                image = image.convert('RGB')
                image.thumbnail((1000, 1000))
                image.save(target, 'WEBP', quality=86)
        with Image.open(target) as image:
            width, height = image.size
            if min(width, height) < 300:
                raise ValueError('Main image below 300 px')
        return dict(id=product['id'], source=url, path='/assets/catalog/' + target.name,
                    width=width, height=height, bytes=target.stat().st_size)
    except Exception as error:
        return dict(id=product['id'], source=url, error=str(error))


if __name__ == '__main__':
    products = json.loads((DATA / 'detail-queue.json').read_text())
    results = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(download, products):
            results.append(result)
            (DATA / 'images.json').write_text(json.dumps(results, indent=2))
            if len(results) % 100 == 0:
                print(f'Images checked: {len(results)}/{len(products)}', flush=True)
    errors = [result for result in results if 'error' in result]
    print(json.dumps(dict(images=len(results), errors=errors), indent=2))
    raise SystemExit(bool(errors))

"""Check category coverage and product completeness before any pages are written."""
from pathlib import Path
import json


def verify_catalog(root):
    data = root / 'content/alibaba-catalog'
    inventory = json.loads((data / 'inventory.json').read_text())
    listings = json.loads((data / 'listings.json').read_text())
    selection = json.loads((data / 'selected.json').read_text())
    queue = json.loads((data / 'detail-queue.json').read_text())
    images = {p['id']: p for p in json.loads((data / 'images.json').read_text())}
    errors = []
    for group in inventory:
        group_id = group['id']
        if group['status'] not in ['list_complete', 'empty_verified']:
            errors.append('Incomplete category: ' + group_id)
        ids = selection[group_id]
        expected = min(200, len(listings[group_id]))
        if len(set(ids)) != len(ids) or len(ids) != expected:
            errors.append('Category selection count: ' + group_id)
    selected_ids = {id for ids in selection.values() for id in ids}
    if selected_ids != {p['id'] for p in queue}:
        errors.append('Selection/queue mismatch')
    missing_details = []
    for product in queue:
        product_id = product['id']
        detail_file = data / 'details' / (product_id + '.json')
        image = images.get(product_id, {})
        if 'error' in image or not (root / image.get('path', '').lstrip('/')).is_file():
            errors.append('Missing image: ' + product_id)
        if not detail_file.exists():
            missing_details.append(product_id)
            continue
        detail = json.loads(detail_file.read_text())
        if detail['id'] != product_id or len(detail.get('attributes', [])) < 5:
            errors.append('Incomplete product attributes: ' + product_id)
        if not any('finerpackaging.' in url for url in detail.get('supplier', [])):
            errors.append('Source store mismatch: ' + product_id)
    if missing_details:
        errors.append(f'Missing details: {len(missing_details)}/{len(queue)}')
    if errors:
        raise ValueError('Catalog publication blocked: ' + '; '.join(errors))
    return {'products': len(queue), 'groups': len(inventory), 'images': len(images)}


if __name__ == '__main__':
    print(json.dumps(verify_catalog(Path(__file__).resolve().parents[1]), indent=2))

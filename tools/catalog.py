"""Build the verified merchant catalog inside the existing static site."""
from urllib.parse import quote
from math import ceil

catalog_data = ROOT / 'content/alibaba-catalog'
catalog_queue = json.loads((catalog_data / 'detail-queue.json').read_text())
catalog_inventory = json.loads((catalog_data / 'inventory.json').read_text())
catalog_selection = json.loads((catalog_data / 'selected.json').read_text())
catalog_images = {p['id']: p for p in json.loads((catalog_data / 'images.json').read_text())}
catalog_item_paths=json.loads((catalog_data/'item-paths.json').read_text())
catalog_records = {}
catalog_missing = []
for source in catalog_queue:
 detail_file = catalog_data / 'details' / (source['id'] + '.json')
 image = catalog_images.get(source['id'], {})
 if not detail_file.exists() or 'error' in image:
  catalog_missing.append(source['id']);continue
 detail = json.loads(detail_file.read_text())
 if detail['id'] != source['id'] or not detail.get('attributes'):
  catalog_missing.append(source['id']);continue
 catalog_records[source['id']] = dict(source=source, detail=detail, image=image)
if catalog_missing:
 raise ValueError(f'Catalog publication blocked: {len(catalog_missing)} incomplete products')

def catalog_slug(text):
 return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

catalog_names = {
 '951346153': 'Featured packaging', '917683989': 'Sample packaging ideas',
 '920016676': 'Mailer & shipping boxes', '950338332': 'Kraft shipping boxes',
 '950338333': 'Printed shipping boxes', '951398518': 'Tear-strip boxes',
 '951662766': 'Protective shipping boxes', '919910675': 'Paper bags',
 '952968758': 'Paper shopping bags', '952857851': 'Paper mailing bags',
 '803631155': 'Gift boxes', '953980869': 'Magnetic boxes',
 '953294826': 'Drawer boxes', '954034112': 'Lid & base boxes',
 '952891404': 'Paper tubes', '954038904': 'Specialty gift boxes',
 '921840222': 'Clothing packaging', '953294833': 'Poly bags',
 '954067551': 'Zipper bags', '954072335': 'Poly mailing bags',
 '954038909': 'Underwear boxes', '952983140': 'Hang tags & strings',
 '803708590': 'Cosmetic packaging', '810538305': 'Food packaging',
 '920318966': 'Sushi packaging boxes', '953304411': 'Cardboard displays',
 '920803216': 'Tea packaging', '920793609': 'Candle packaging',
 '807897313': 'Cards & booklets', '803759676': 'Stickers & labels',
 '919632767': 'Pouches', '0': 'More packaging ideas'
}
catalog_groups = {g['id']: dict(g, public_name=catalog_names[g['id']],
 slug=catalog_slug(catalog_names[g['id']])) for g in catalog_inventory
 if catalog_selection[g['id']]}

def catalog_attr(record, *names):
 for name in names:
  values = [a['value'].strip() for a in record['detail']['attributes']
            if a.get('name', '').lower() == name.lower() and a.get('value')]
  if values:return values[0]
 return ''

def catalog_clean(text,label=''):
 text = re.sub(r'\b(?:FSC(?:[ -]Certified)?|Certified|Eco[ -]?Friendly|Sustainable|Recyclable|Recycl(?:e|ed)(?: Materials)?|Bio[ -]?degradable|Compostable|Food[ -]?Grade|High[ -]?Quality|Wholesale|Factory[ -]?Direct|Cheap|Hot Sale|Best[ -]?Seller|Luxury|Premium|Minimalist|Economically Priced)\b', '', text, flags=re.I)
 text = re.sub(r'\b(?:Finer(?: Packaging)?|Xiamen|China)\b', '', text, flags=re.I)
 text=re.sub(r'\b(?:Cutomized|Customezed|Customed)\b','Customized',text,flags=re.I)
 for pattern,value in [(r'\b(?:Panton|Partone)\b','Pantone'),(r'\b(?:Offest|Off-set)\b','Offset'),(r'\bCarboard\b','Cardboard'),(r'\bPrinitng\b','Printing'),(r'\bShap\b','Shape'),(r'\bVanishing\b','Varnishing'),(r'\bMatt\b','Matte'),(r'GlossyMatt','Gloss / matte')]:text=re.sub(pattern,value,text,flags=re.I)
 text=re.sub(r'\s+', ' ', text).strip(' ,-/')
 if not text:return ''
 if label=='Size' and not re.search(r'\d',text):return 'Custom size'
 if label=='Color' and re.search(r'custom|request',text,re.I):return 'Custom colors'
 if label=='Printing' and re.fullmatch(r"Customized|Customer Printing Requirement|Customers'?\s*requirements|Custom Printing Accept",text,re.I):return 'Custom printing'
 if label=='Structure / closure' and text.lower() in ['folders','others','custom','customized shape','custom shapes']:return 'Custom structure'
 if label=='Logo / branding' and re.search(r'custom|accept',text,re.I):return 'Custom logo'
 if label=='Insert / accessories' and text.lower()=='none':return 'No insert'
 if label=='Finish':text=re.sub(r'\bHot Galvanized\b,?\s*','',text,flags=re.I).strip(' ,')
 if ',' in text:text=', '.join(dict.fromkeys(part.strip() for part in text.split(',') if part.strip()))
 return text

def catalog_title(record):
 text=record['detail']['title'].lower()
 formats=[('Magnetic Vial Box',r'(?:vial|peptide).*magnetic|magnetic.*(?:vial|peptide)'),
 ('Magnetic Gift Box',r'magnetic'),('Drawer Gift Box',r'drawer|sliding|pull.out'),
 ('Lid & Base Gift Box',r'lid.{0,8}(?:base|bottom)|two.piece'),
 ('Paper Tube Box',r'paper tube|cylinder|cylindrical'),('Cardboard Display',r'pdq|counter.?display|display.?stand|floor.?display'),
 ('Paper Mailing Bag',r'(?=.*\bbags?\b).*(?:paper|kraft).*(?:mailer|mailing|postal)'),
 ('Paper Shopping Bag',r'paper.*bag|bag.*paper'),
 ('Zipper Bag',r'zip.?lock|zipper.*bag|bag.*zipper'),('Poly Mailing Bag',r'poly.*mailer|mailer.*poly'),
 ('Poly Bag',r'plastic.*bag|poly.*bag|garment.*bag'),('Packaging Pouch',r'pouch'),
 ('Hang Tag',r'hang.?tag'),('Printed Card',r'^(?!.*box).*\b(?:cards?|booklets?|brochures?)\b'),
 ('Printed Sticker',r'sticker'),('Product Label',r'^(?!.*box).*label'),
 ('Corrugated Mailer Box',r'corrugat|shipping|mailer|mailing'),
 ('Printed Carton',r'carton|folding|tuck|ste box|rte box'),('Gift Box',r'gift'),
 ('Product Packaging Box',r'box')]
 name=next((name for name,pattern in formats if re.search(pattern,text)),'Printed Packaging')
 applications=[('Serum',r'serum'),('Lipstick',r'lipstick'),('Lip Balm',r'lip balm'),
 ('Skincare',r'skin.?care|cream|lotion'),('Perfume',r'perfume|fragrance'),
 ('Essential Oils',r'essential oil|dropper'),('Soap',r'\bsoap\b'),
 ('Candles',r'candle'),('Jewelry',r'jewelry|jewellery'),('Apparel',r'clothing|apparel|garment|underwear|sock'),
 ('Bottles',r'bottle'),('Mugs',r'\bmug\b|coffee cup'),('Sushi',r'sushi'),
 ('Chocolate',r'chocolate'),('Tea',r'\btea\b'),('Bakery Products',r'cake|pastry|pastries|macaron')]
 application=next((name for name,pattern in applications if re.search(pattern,text)),'')
 material=catalog_attr(record,'Material Structure','Material','Paper Type').lower()
 prefix='Kraft' if 'kraft' in material and name in ['Corrugated Mailer Box','Paper Shopping Bag','Paper Mailing Bag'] else 'Custom'
 name=prefix+' '+name
 if application and application.lower() not in name.lower():name+=' for '+application
 return name

for product_id, record in catalog_records.items():
 record['name'] = catalog_title(record)
 record['reference'] = 'PHG-' + product_id
 record['path'] = '/catalog/' + catalog_slug(record['name'])[:90].rstrip('-') + '-' + product_id + '/'
 record['groups'] = [g for g in record['source']['groups'] if g in catalog_groups]
 if '953304411' in record['groups']:record['name']='Custom Cardboard Display'
 elif '952983140' in record['groups']:record['name']='Custom Printed Hang Tag'
 elif '807897313' in record['groups']:
  raw=record['detail']['title'].lower()
  if 'dust cover' in raw:record['name']='Custom Candle Dust Covers'
  elif 'table tent' in raw:record['name']='Custom Printed Table Tent'
  elif 'sleeve' in raw:record['name']='Custom Paper Packaging Sleeve'
 record['path']=catalog_item_paths[product_id]
 record['facts'] = []
 for label, names in [('Material', ('Material Structure','Material','Paper Type','Plastic Type')),
                       ('Size', ('Size',)), ('Printing' if catalog_attr(record,'Printing') else 'Print / finish', ('Printing','Printing Handling','Surface Handling'))]:
  value = catalog_clean(catalog_attr(record, *names),label)
  if label=='Material' and value.lower() in ['custom','others','other','cardboard box']:value=catalog_clean(catalog_attr(record,'Paper Type','Plastic Type'),label)
  if value and not re.search(r'Finer|Xiamen|https?://',value,re.I):
   record['facts'].append((label,value))
 for label,names in [('Structure / closure',('Box Type','Bag Type','Sealing & Handle','Shape')),('Finish',('Surface Finish','Surface Treatment')),('Insert / accessories',('Liner type','Accessories')),('Color',('Color','Colors')),('Logo / branding',('Logo','Logo printing'))]:
  value=catalog_clean(catalog_attr(record,*names),label)
  if label=='Finish' and not re.search(r'finish|laminat|varnish|foil|stamp|emboss|deboss|coating|gloss|matte|\bUV\b|print|textur|4C',value,re.I):continue
  if value and not re.search(r'Finer|Xiamen|https?://',value,re.I):record['facts'].append((label,value))
 record['family']='packaging-accessories' if product_profile(record) in ['label','print','display'] else 'bags' if product_profile(record) in ['bag','poly','pouch'] else 'paper-boxes'

# Verified source references join the existing catalog without changing its URLs.
pouch_data = ROOT / 'content/pouch-sources'
pouch_products = json.loads((pouch_data / 'products.json').read_text()) if (pouch_data / 'products.json').exists() else []
for group_id, label in [('pouch-stand-up','Stand-up pouches'), ('pouch-flat-bottom','Flat-bottom pouches'), ('pouch-side-gusset','Side-gusset pouches'), ('pouch-spout','Spout & refill pouches'), ('pouch-flat','Flat pouches & sachets'), ('pouch-specialty','Specialty flexible packaging')]:
 ids = [p['id'] for p in pouch_products if group_id in p['groups']]
 if ids:
  catalog_groups[group_id] = dict(id=group_id, public_name=label, slug=catalog_slug(label))
  catalog_selection[group_id] = ids
for record in pouch_products:
 catalog_records[record['id']] = record
 catalog_selection['919632767'].append(record['id'])

for record in json.loads((ROOT/'content/luxopack-sources/products.json').read_text()):
 catalog_records[record['id']]=record

exec(compile((ROOT/'tools/catalog_review.py').read_text(),str(ROOT/'tools/catalog_review.py'),'exec'))

FAMILIES={'paper-boxes':'Paper boxes','bags':'Bags & pouches','packaging-accessories':'Packaging accessories'}
def catalog_chat(record):
 return 'https://wa.me/8615105916426?text='+quote('Hello PackHubGlobe, I would like a quote for '+record['name']+' ('+record['reference']+').\nProduct: '+ORIGIN+record['path']+'\nQuantity: 500 pieces or more\nCustom size: \nLogo / printing: \nDelivery country: \nPlease advise the material, sample options and quotation.')

def family_nav(base):
 return '<nav class="family-nav" aria-label="Packaging families"><a href="/catalog/"'+(' aria-current="page"' if base=='/catalog/' else '')+'>All products</a>'+''.join('<a href="/catalog/'+slug+'/"'+(' aria-current="page"' if base=='/catalog/'+slug+'/' else '')+'>'+title+'</a>' for slug,title in FAMILIES.items())+'</nav>'

def catalog_fact_preview(value):
 parts=value.split(', ')
 if len(parts)>3:return ', '.join(parts[:3])+' +'+str(len(parts)-3)+' more'
 return value if len(value)<=95 else value[:95].rsplit(' ',1)[0]+'…'

def catalog_card(record,heading='h2'):
 image = record['image'];name = esc(record['name']);path = record['path']
 group = catalog_groups[record['groups'][0]]['public_name']
 facts = '<div class="moq-fact"><dt>MOQ</dt><dd>500 pieces</dd></div>'+''.join('<div><dt>'+label+'</dt><dd>'+esc(catalog_fact_preview(value))+'</dd></div>'
                 for label,value in record['facts'][:5])
 return '<article class="catalog-card"><a class="catalog-photo" href="'+path+'"><img src="'+image['path']+'" alt="'+esc(record['name'],quote=True)+'" width="'+str(image['width'])+'" height="'+str(image['height'])+'" loading="lazy"></a><div class="catalog-copy"><p class="eyebrow">'+esc(group)+'</p><'+heading+'><a href="'+path+'">'+name+'</a></'+heading+'><dl class="catalog-facts">'+facts+'</dl><p class="catalog-ref">'+record['reference']+'</p><div class="catalog-actions"><a class="textlink" href="'+path+'">View details ↗</a>'+button('Get a quote',qurl(record['name']+' · '+record['reference']))+'<a class="button chat-now" href="'+esc(catalog_chat(record),quote=True)+'" target="_blank" rel="noopener noreferrer">Chat now · WhatsApp</a></div></div></article>'

def catalog_pagination(base,page,total):
 if total<=1:return ''
 def url(n):return base if n==1 else base+'page-'+str(n)+'/'
 pages=sorted({1,total,*range(max(1,page-2),min(total,page+2)+1)})
 links=[]
 if page>1:links.append('<a rel="prev" href="'+url(page-1)+'">← Previous</a>')
 last=0
 for n in pages:
  if n>last+1:links.append('<span aria-hidden="true">…</span>')
  links.append('<a href="'+url(n)+'"'+(' aria-current="page"' if n==page else '')+'>'+str(n)+'</a>');last=n
 if page<total:links.append('<a rel="next" href="'+url(page+1)+'">Next →</a>')
 return '<nav class="catalog-pages" aria-label="Catalog pages">'+''.join(links)+'</nav>'

collection_copy=json.loads((ROOT/'content/catalog-collection-copy.json').read_text())

def catalog_listing(base,name,ids,all_products=False):
 total=ceil(len(ids)/24)
 for page in range(1,total+1):
  path=base if page==1 else base+'page-'+str(page)+'/'
  group_id=next((key for key,g in catalog_groups.items() if base=='/catalog/'+g['slug']+'/'),None)
  description=collection_copy.get(base,collection_copy.get(group_id,''))
  if not description:raise ValueError('Missing collection copy: '+base)
  if page>1:description+=' Page '+str(page)+'.'
  body=intro('Product collection',name+'.',description,'<a href="/catalog/">Product collection</a>'+(' / '+esc(name) if not all_products else ''))
  body+='<div class="wrap">'+family_nav(base)+'</div>'
  body+='<section class="wrap catalog-layout"><aside class="catalog-sidebar"><details'+(' open' if all_products else '')+'><summary>Browse packaging</summary><a href="/catalog/">All products</a>'+''.join('<a href="/catalog/'+g['slug']+'/"'+(' aria-current="page"' if base=='/catalog/'+g['slug']+'/' else '')+'>'+esc(g['public_name'])+' <span>'+str(len(catalog_selection[id]))+'</span></a>' for id,g in catalog_groups.items())+'</details><a class="textlink" href="/products/">Compare packaging formats ↗</a></aside><div class="catalog-results"><div class="catalog-toolbar"><p>'+str(len(ids))+' products · Page '+str(page)+' of '+str(total)+'</p><div class="catalog-search" hidden><label for="catalog-search">Search all products</label><input type="search" id="catalog-search" placeholder="Try a format, material or PHG reference" autocomplete="off"><button type="button" id="catalog-clear">Clear</button></div></div><p id="catalog-search-status" class="smallnote" role="status" aria-live="polite"></p><div class="catalog-grid" id="catalog-grid">'+''.join(catalog_card(catalog_records[id]) for id in ids[(page-1)*24:page*24])+'</div>'+catalog_pagination(base,page,total)+'</div></section>'+cta()
  listing_schema={'@type':'ItemList','name':name,'numberOfItems':len(ids),'itemListElement':[{'@type':'ListItem','position':(page-1)*24+i+1,'url':ORIGIN+catalog_records[id]['path']} for i,id in enumerate(ids[(page-1)*24:page*24])]}
  write(path,name+(' · Page '+str(page) if page>1 else '')+' | PackHubGlobe',description.split('. ',1)[0]+('. Page '+str(page)+'.' if page>1 else '.'),body,[listing_schema])

# Interleave source groups so the main collection opens with a varied range.
catalog_order=[]
catalog_pools=[list(ids) for id,ids in catalog_selection.items() if id in catalog_groups]
while any(catalog_pools):
 for pool in catalog_pools:
  if pool:
   id=pool.pop(0)
   if id not in catalog_order:catalog_order.append(id)
catalog_listing('/catalog/','Custom packaging collection',catalog_order,True)
for slug,title in FAMILIES.items():
 catalog_listing('/catalog/'+slug+'/',title,[id for id in catalog_order if catalog_records[id]['family']==slug])
for id,group in catalog_groups.items():
 catalog_listing('/catalog/'+group['slug']+'/',group['public_name'],catalog_selection[id])

for product_id, record in catalog_records.items():
 image=record['image'];reference=record['reference'];name=record['name']
 group=catalog_groups[record['groups'][0]]
 description=name+'. '+reference+'. Review material, size and printing options for a custom packaging quotation.'
 visual='<figure class="catalog-product-image"><a href="'+image['path']+'" target="_blank" rel="noopener noreferrer"><img src="'+image['path']+'" alt="'+esc(name,quote=True)+'" width="'+str(image['width'])+'" height="'+str(image['height'])+'" fetchpriority="high"></a></figure>'
 body=detailhero(group['public_name'],esc(name),reference+' · Compare the construction and artwork, then confirm your project specification.',visual,name+' · '+reference,'<a href="/catalog/">Product collection</a> / <a href="/catalog/'+group['slug']+'/">'+esc(group['public_name'])+'</a>')
 rows=[('Minimum order quantity','500 pieces')]+list(record['facts'])
 body+='<section class="section wrap product-details"><div><h2>Product details.</h2>'+specs(rows)+'<p class="smallnote">These are reference specifications. Confirm the material, dimensions, finish and sample for your order. MOQ: 500 pieces. Images show design references. Branded contents are not supplied; printed claims do not verify the order specification.</p></div><aside class="help-note"><h3>Make this packaging yours.</h3><p>Share your product dimensions, quantity per design, artwork and delivery country. Include reference '+reference+' in your enquiry.</p><div class="actions">'+button('Request a quote',qurl(name+' · '+reference))+'<a class="textlink" href="https://wa.me/8615105916426?text='+catalog_chat(record).split('?text=',1)[1]+'" target="_blank" rel="noopener noreferrer">Discuss on WhatsApp ↗</a></div><a class="textlink" href="/guides/packaging-quote-checklist/">Prepare your specification</a></aside></section>'
 if record.get('review_note'):
  body+='<section class="section wrap"><h2>Points to confirm for this reference.</h2><p>'+esc(record['review_note'])+'</p></section>'
 if record.get('gallery'):
  body+='<section class="section wrap"><h2>Additional design references.</h2><p>Compare these views with the main reference. Confirm the supplied components, dimensions and construction for your order.</p><div class="catalog-grid">'+''.join('<figure class="catalog-product-image"><a href="'+im['path']+'" target="_blank" rel="noopener noreferrer"><img src="'+im['path']+'" alt="'+esc(name+' · additional reference '+str(i+1),quote=True)+'" width="'+str(im['width'])+'" height="'+str(im['height'])+'" loading="lazy"></a><figcaption>'+esc(reference+' · additional design reference '+str(i+1))+'</figcaption></figure>' for i,im in enumerate(record['gallery']))+'</div></section>'
 body+=product_editorial(record,rows)
 related_pool=[r for id,r in catalog_records.items() if id!=product_id and r['format']==record['format']]
 if len(related_pool)<3:related_pool.extend(r for id,r in catalog_records.items() if id!=product_id and r['family']==record['family'] and r not in related_pool)
 application=next((v for k,v in record['facts'] if k=='Application'),'')
 related_items=sorted(related_pool,key=lambda r:(r['format']==record['format'],bool(application) and any(k=='Application' and v==application for k,v in r['facts']),len(set(r['groups'])&set(record['groups']))),reverse=True)[:3]
 body+='<section class="section wrap"><h2>Compare related product references.</h2><div class="catalog-grid related-products">'+''.join(catalog_card(r,'h3') for r in related_items)+'</div></section>'
 body+='<section class="section softbg"><div class="wrap"><h2>Explore related packaging.</h2><div class="related-links"><a href="/catalog/'+record['family']+'/">'+FAMILIES[record['family']]+'</a>'+''.join('<a href="/catalog/'+catalog_groups[g]['slug']+'/">'+esc(catalog_groups[g]['public_name'])+'</a>' for g in record['groups'])+'</div></div></section>'+cta()
 schema={'@type':'Product','name':name,'sku':reference,'url':ORIGIN+record['path'],'image':ORIGIN+image['path'],'description':description,'brand':{'@type':'Brand','name':'PackHubGlobe'},'additionalProperty':[{'@type':'PropertyValue','name':label,'value':value} for label,value in rows]}
 write(record['path'],name+' · '+reference+' | PackHubGlobe',description,body,[schema])
 file=ROOT/record['path'].strip('/')/'index.html'
 file.write_text(file.read_text().replace(ORIGIN+'/assets/images/print-collection.webp',ORIGIN+image['path']))

# Route inventory is generated from the same data, while preserving the original page plan.
map_file=ROOT/'content/page-map.csv'
with map_file.open(encoding='utf-8-sig',newline='') as stream:
 reader=csv.DictReader(stream);fields=reader.fieldnames;planned=[r for r in reader if '/catalog/' not in r['url']]
for path,title,description in PAGES:
 if path.startswith('/catalog/'):
  planned.append(dict(zip(fields,[ORIGIN+path,title,'/catalog/',title.split(' | ')[0],'P1','Catalog','implemented','Merchant product page captured 2026-10-16'])))
with map_file.open('w',encoding='utf-8-sig',newline='') as stream:
 writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(planned)

# Small search index uses only the curated public fields; original metadata remains in content/.
search=[{'name':r['name'],'reference':r['reference'],'path':r['path'],'image':r['image']['path'],'family':r['family'],'format':r['format'],'chat':catalog_chat(r),'searchText':' '.join(value for label,value in r['facts']),'facts':[['MOQ','500 pieces']]+[(label,catalog_fact_preview(value)) for label,value in r['facts'][:5]],'groups':[catalog_groups[g]['public_name'] for g in r['groups']]} for r in catalog_records.values()]
(ROOT/'assets/catalog-index.json').write_text(json.dumps(search,ensure_ascii=False))
(catalog_data/'publication.json').write_text(json.dumps({'products':len(catalog_records),'groups':{id:{'name':g['public_name'],'published':len(catalog_selection[id]),'candidates':len(json.loads((catalog_data/'listings.json').read_text()).get(id, catalog_selection[id]))} for id,g in catalog_groups.items()},'public_paths':[p[0] for p in PAGES if p[0].startswith('/catalog/')]},indent=2))

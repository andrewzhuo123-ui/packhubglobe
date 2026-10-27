"""Apply the 19 October product/image review while preserving public product URLs."""
review_overrides = json.loads((ROOT/'content/catalog-review.json').read_text())
# Format, public family, editorial profile and primary collection.
CATALOG_FORMATS = {
 'mailer':('paper-boxes','mailer','920016676','Mailer & shipping boxes'),
 'carton':('paper-boxes','carton','folding-cartons','Folding cartons'),
 'rigid':('paper-boxes','rigid','803631155','Gift boxes'),
 'carry-box':('paper-boxes','carry-box','handle-carry-boxes','Handle carry boxes'),
 'pillow':('paper-boxes','pillow','pillow-boxes','Pillow boxes'),
 'food-box':('paper-boxes','food-box','810538305','Food packaging'),
 'paper-bag':('bags','bag','952968758','Paper shopping bags'),
 'paper-mailer':('bags','paper-mailer','952857851','Paper mailing bags'),
 'poly':('bags','poly','953294833','Poly bags'),
 'poly-mailer':('bags','poly-mailer','954072335','Poly mailing bags'),
 'stand-up':('bags','pouch','pouch-stand-up','Stand-up pouches'),
 'flat-bottom':('bags','pouch-flat-bottom','pouch-flat-bottom','Flat-bottom pouches'),
 'side-gusset':('bags','pouch-side-gusset','pouch-side-gusset','Side-gusset pouches'),
 'spout':('bags','pouch-spout','pouch-spout','Spout & refill pouches'),
 'flat':('bags','pouch-flat','pouch-flat','Flat pouches & sachets'),
 'specialty':('bags','pouch-specialty','pouch-specialty','Specialty flexible packaging'),
 'drink-pouch':('bags','pouch-drink','beverage-straw-pouches','Beverage & straw pouches'),
 'carry-bag':('bags','carry-bag','gift-carry-bags','Gift & carry bags'),
 'roll-bag':('bags','roll-bag','roll-bags-liners','Roll bags & liners'),
 'bag-in-box':('bags','bag-in-box','bag-in-box','Bag-in-box references'),
 'container-reference':('packaging-accessories','reference','presentation-container-references','Presentation & container references'),
 'sleeve':('packaging-accessories','sleeve','packaging-sleeves','Packaging sleeves & wraps'),
 'pulp-insert':('packaging-accessories','insert','molded-pulp-inserts','Molded pulp inserts'),
 'dust-cover':('packaging-accessories','dust-cover','candle-dust-covers','Candle dust covers'),
 'print':('packaging-accessories','print','807897313','Cards & booklets'),
 'label':('packaging-accessories','label','803759676','Stickers & labels'),
 'display':('packaging-accessories','display','953304411','Cardboard displays'),
}

def reviewed_format(record):
 key=record['reference'].removeprefix('PHG-')
 if key.startswith(('LX-','FP-')):return record['format']
 if key in review_overrides:return review_overrides[key]['format']
 title=record['detail']['title'].lower();name=record['name'].lower();groups=set(record['groups'])
 if key.startswith('PC-'):
  return next((kind for kind in ['flat-bottom','side-gusset','spout','flat','stand-up','specialty'] if 'pouch-'+kind in groups),'specialty')
 bag_type=catalog_attr(record,'Bag Type').lower()
 box_type=catalog_attr(record,'Box Type').lower()
 material=' '.join(v for k,v in record['facts'] if k=='Material').lower()
 if 'table tent' in title or 'hang tag' in title or 'hangtag' in title:return 'print'
 if 'dust cover' in title or 'candle cover' in title:return 'dust-cover'
 if 'sleeve' in title and not re.search(r'\bbox(?:es)?\b|drawer',title):return 'sleeve'
 if '953304411' in groups or 'display' in name:return 'display'
 if '803759676' in groups:return 'label'
 if groups&{'807897313','952983140'}:return 'print'
 if re.search(r'stand\s*up|standup|side.gusset',bag_type) or '919632767' in groups:
  return 'side-gusset' if re.search(r'side.gusset',bag_type+' '+title) else 'flat-bottom' if re.search(r'flat.bottom',title) else 'stand-up'
 if '952857851' in groups or ('bag' in title and 'paper' in title and re.search(r'mail(?:ing|er)',title) and not re.search(r'\bbox(?:es)?\b',title)):return 'paper-mailer'
 if groups&{'953294833','954067551','954072335'}:
  return 'poly-mailer' if re.search(r'mail(?:ing|er)',title) else 'poly'
 if groups&{'919910675','952968758'} and not re.search(r'\bbox(?:es)?\b',title):return 'paper-bag'
 if any(s in title for s in ['magnetic','drawer','sliding','lid and base','lid & base','two piece','paper tube','cylinder']):return 'rigid'
 if 'rigid' in box_type and 'folding' not in box_type:return 'rigid'
 if re.search(r'corrugat|corruaged',material) or re.search(r'\bmail(?:er|ing)\b|\bshipping\b',title):return 'mailer'
 if 'pillow box' in title:return 'pillow'
 if '920318966' in groups or ('810538305' in groups and not 'chocolate' in title):return 'food-box'
 return 'carton'

FORMAT_NAMES={'mailer':'Custom Corrugated Mailer Box','carton':'Custom Folding Carton','rigid':'Custom Rigid Gift Box','carry-box':'Custom Carry Box','pillow':'Custom Pillow Box','food-box':'Custom Paper Food Box','paper-bag':'Custom Paper Shopping Bag','paper-mailer':'Custom Paper Mailing Bag','poly':'Custom Product Bag','poly-mailer':'Custom Poly Mailing Bag','stand-up':'Custom Stand-Up Pouch','flat-bottom':'Custom Flat-Bottom Pouch','side-gusset':'Custom Side-Gusset Bag','print':'Custom Printed Card','label':'Custom Printed Label','display':'Custom Cardboard Display','sleeve':'Custom Printed Packaging Sleeve','dust-cover':'Custom Candle Dust Cover'}
APPLICATION_GROUPS={'951346153','917683989','921840222','803708590','810538305','920803216','920793609','0'}
BOX_GROUPS={'920016676','950338332','950338333','951398518','951662766','803631155','953980869','953294826','954034112','952891404','954038904','954038909','920318966'}
PAPER_BAG_GROUPS={'919910675','952968758','952857851'}
POLY_GROUPS={'953294833','954067551','954072335'}
POUCH_FORMATS={'stand-up','flat-bottom','side-gusset','spout','flat','specialty','drink-pouch','bag-in-box'}
for record in catalog_records.values():
 key=record['reference'].removeprefix('PHG-');override=review_overrides.get(key,{})
 kind=reviewed_format(record);family,profile,primary,label=CATALOG_FORMATS[kind]
 name=override.get('name',record['name'])
 if key.startswith(('LX-','FP-')):
  primary=record['groups'][0]
 elif not key.startswith('PC-'):
  name=name.split(' for ',1)[0]
  compatible={'mailer':r'mailer','carton':r'carton','rigid':r'magnetic|drawer|lid & base|tube|rigid','paper-bag':r'shopping bag','paper-mailer':r'mailing bag','poly-mailer':r'poly mailing','stand-up':r'stand.up','side-gusset':r'side.gusset','flat-bottom':r'flat.bottom','sleeve':r'sleeve','dust-cover':r'dust cover','food-box':r'food box'}
  if not override and kind in compatible and not re.search(compatible[kind],name,re.I):name=FORMAT_NAMES[kind]
  if kind=='rigid':
   primary=next((group for word,group in [('magnetic','953980869'),('drawer','953294826'),('lid & base','954034112'),('tube','952891404')] if word in name.lower()),primary)
  if kind=='print' and '952983140' in record['groups'] and 'table tent' not in name.lower():primary='952983140'
 else:
  name=re.sub(r'\b(?:High Moisture Barrier|Moisture Barrier|Barrier|Lightweight|Organic|Mono-PE|Foil)\b','',name,flags=re.I)
  name=re.sub(r'\bMetali[sz]ed\b','Metallic-Look',name,flags=re.I)
  name=re.sub(r'\bMylar\b','Flexible Film',name,flags=re.I)
 name=re.sub(r'\s+',' ',name).strip(' -')
 record.update(name=name,format=kind,profile=profile,family=family)
 if primary not in catalog_groups:catalog_groups[primary]=dict(id=primary,public_name=label,slug=catalog_slug(label))
 allowed_boxes={'954038909','920318966'} if family=='paper-boxes' else set()
 if kind=='mailer':allowed_boxes|={'920016676','950338332','950338333','951398518','951662766'}
 if kind in {'rigid','carton','pillow','carry-box','food-box','mailer'}:allowed_boxes|={'803631155','954038904'}
 if kind=='rigid':allowed_boxes.add(primary)
 retained=[g for g in record['groups'] if g in APPLICATION_GROUPS or g in allowed_boxes or kind=='paper-bag' and g in PAPER_BAG_GROUPS-{'952857851'} or kind=='paper-mailer' and g in {'919910675','952857851'} or kind in {'poly','poly-mailer'} and g in POLY_GROUPS or kind in POUCH_FORMATS and g=='919632767']
 if kind=='print' and 'table tent' in name.lower():retained=[]
 record['groups']=list(dict.fromkeys([primary]+retained))
 facts=[]
 for field,value in record['facts']:
  value=catalog_clean(value,field)
  if not value or re.search(r'\b(?:AE|LTS)\b',value):continue
  if field in ['Structure / closure','Opening'] and override:continue
  if kind in {'container-reference','carry-bag','roll-bag'} and field in ['Material','Film / laminate','Thickness reference','Printing','Volume reference','Fill-weight reference']:continue
  if field=='Application' and override.get('application'):value=override['application']
  if field=='Color' and re.search(r'up to \d+',value,re.I):value='Colors to confirm with the print specification'
  if field=='Structure / closure' and (value in ['Slotted Boxes','Greeting cards'] or kind=='paper-mailer' and 'stand' in value.lower()):continue
  if field not in [k for k,v in facts]:facts.append([field,value])
 if override.get('application') and not any(k=='Application' for k,v in facts):facts.append(['Application',override['application']])
 structure={'mailer':'Folding mailer box; closure confirmed on the dieline','carton':'Folding carton; flap and base construction to confirm','carry-box':'Carry box with handle; attachment and load to confirm','pillow':'Curved-end folding pillow box','rigid':'Rigid presentation box; opening and insert to confirm','paper-bag':'Paper carrier bag; handle and base to confirm','poly':'Flexible product bag; opening and seams to confirm','poly-mailer':'Poly mailing bag; seam and adhesive flap to confirm','paper-mailer':'Paper mailing bag; seam and flap construction to confirm','stand-up':'Bottom-gusset pouch reference','flat-bottom':'Flat-bottom bag reference','side-gusset':'Side-gusset bag reference','spout':'Pouch with fitment; bore, cap and position to confirm','flat':'Flat bag / pouch; seal pattern to confirm','drink-pouch':'Beverage pouch with straw-opening reference','carry-bag':'Gift / carry bag; material and construction to confirm','roll-bag':'Bags supplied on rolls; perforation and bag count to confirm','bag-in-box':'Liner, dispensing fitment and outer box specified separately','container-reference':'Presentation reference; supplied component to confirm','sleeve':'Printed wrap-around sleeve','dust-cover':'Removable printed candle dust cover','pulp-insert':'Molded insert; cavities, support and wall geometry to confirm'}
 if kind in structure:facts=[[k,v] for k,v in facts if k!='Structure / closure'];facts.insert(0,['Structure / closure',structure[kind]])
 if kind in {'drink-pouch','spout','carry-bag','roll-bag','container-reference'}:
  facts=[[k,v] for k,v in facts if k!='Opening']
  if kind in {'drink-pouch','spout'}:facts.append(['Opening','Straw insertion and final top seal to confirm' if kind=='drink-pouch' else 'Spout / cap assembly to confirm'])
 if not any(k=='Size' for k,v in facts):facts.append(['Size','Custom dimensions; measurement convention to confirm'])
 if not any(k in ['Printing','Print / finish','Artwork'] for k,v in facts):facts.append(['Artwork','Custom artwork subject to proof approval'])
 # Remove duplicate base-film entries and make optional values read as references.
 material=next((v for k,v in facts if k=='Material'),'')
 if material:
  facts=[[k,v] for k,v in facts if k!='Film / laminate']
 labels={'Material':'Material reference','Film / laminate':'Other film reference' if material else 'Film reference','Size':'Dimensions reference','Printing':'Printing options','Print / finish':'Print / finish options','Structure / closure':'Format reference','Finish':'Finish options'}
 clean_facts=[]
 for field,value in facts:
  if field=='Insert / accessories' and value=='No insert':value='Insert requirement to confirm with the packed product'
  if field in {'Volume reference','Fill-weight reference'}:
   field='Fill quantity';value='Confirm for the actual contents and finished dimensions'
  if field in {'Material','Film / laminate'} and (value.count('/')>=6 or '; separate reference:' in value or len(value)>120):value='Several material options recorded; confirm one complete construction for the order'
  value=re.sub(r'\bcorruaged\b','corrugated',value,flags=re.I)
  field=labels.get(field,field)
  if field not in [k for k,v in clean_facts]:clean_facts.append([field,value])
 record['facts']=clean_facts
 if kind=='spout' and re.search(r'grain|rice|litter|dry grain',name,re.I):record['profile']='pouch-spout-dry'
 note=record.get('review_note','')
 if note and not key.startswith(('LX-','FP-')):
  if re.search(r'material field|unidentified component',note):
   record['review_note']='Confirm the complete layer construction, polymer identities and thickness. A film-name reference does not establish the finished laminate or its performance.'
  elif re.search(r'size field|volume and mass',note):
   record['review_note']='Specify fill mass or volume separately from package dimensions. Confirm finished width, height, any gusset and measurement units on the drawing and filled sample.'
  else:
   record['review_note']='Confirm the intended contents, complete construction and actual opening against a matching sample. Printed artwork illustrates a presentation direction; it does not qualify the material for a particular product or filling process.'
 if kind=='container-reference':record['review_note']='Identify the component you need: container, printed label, sleeve, wrap or presentation accessory. The photograph is a design reference and does not establish a flexible pouch or a fixed stock specification.'
 if kind=='bag-in-box':record['review_note']='Confirm whether the quotation covers the liner, dispensing fitment, printed outer box or the complete system. Approve fitment compatibility and the filled assembly together.'
 if key=='PC-3AE35E247D':record['review_note']='The image includes different fill examples. Select one intended product, opening and fitment configuration before confirming the structure and filling process.'
# Collections derive from the reviewed memberships, rather than supplier marketing buckets.
for group_id in catalog_groups:
 catalog_selection[group_id]=[key for key,r in catalog_records.items() if group_id in r['groups']]
catalog_groups={key:g for key,g in catalog_groups.items() if catalog_selection[key]}

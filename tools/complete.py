"""Build the complete static product, industry and resource page inventory."""
exec(compile((ROOT/'tools/editorial.py').read_text(),str(ROOT/'tools/editorial.py'),'exec'))
from products import PRODUCTS
from product_buying_guides import BUYING_GUIDES
import importlib.util
spec=importlib.util.spec_from_file_location('packhub_collections',ROOT/'content/collections.py')
collection=importlib.util.module_from_spec(spec);spec.loader.exec_module(collection)
INDUSTRIES=collection.INDUSTRIES;MATERIALS=collection.MATERIALS;SERVICES=collection.SERVICES;EXTRA_GUIDES=collection.EXTRA_GUIDES

def related(items):
 return '<div class="related-links">'+''.join('<a href="/products/'+p+'/">'+esc(next(row[1] for row in PRODUCTS[p.split('/')[0]] if row[0]==p.split('/')[1]))+'</a>' for p in items)+'</div>'

def scene(name,alt):
 file={'coffee':'print-coffee','beauty':'print-beauty','packing':'print-packing','general':'print-collection'}[name]
 width,height=(1254,1254) if name=='general' else (1536,1024)
 return '<figure class="scene"><img src="/assets/images/'+file+'.webp" alt="'+esc(alt,quote=True)+'" width="'+str(width)+'" height="'+str(height)+'" loading="lazy"><figcaption>Fictional-brand design reference</figcaption></figure>'

def sections(items):return ''.join('<section><h2>'+esc(title)+'</h2><p>'+esc(text)+'</p></section>' for title,text in items)
def specs(rows):return '<dl class="spec-list">'+''.join('<div><dt>'+esc(title)+'</dt><dd>'+esc(text)+'</dd></div>' for title,text in rows)+'</dl>'

format_references=json.loads((ROOT/'content/format-references.json').read_text())
def format_visual(slug,name,category):
 reference=format_references.get(slug)
 if not reference:
  return '<figure class="productvisual">'+art(category['art'])+'<figcaption>Packaging family reference; confirm the '+esc(name.lower())+' construction separately.</figcaption></figure>'
 return '<figure class="catalog-product-image"><a href="'+reference['path']+'"><img src="'+reference['image']+'" alt="Packaging reference for '+esc(name.lower(),quote=True)+'" width="'+str(reference['width'])+'" height="'+str(reference['height'])+'" fetchpriority="high"></a><figcaption>Related structure reference · <a href="'+reference['path']+'">'+reference['reference']+'</a>. Confirm your final dimensions, material and construction.</figcaption></figure>'

def format_collection(slug,family):
 return {'stand-up-pouches':'/catalog/stand-up-pouches/','flat-bottom-pouches':'/catalog/flat-bottom-pouches/','side-gusset-bags':'/catalog/side-gusset-pouches/','spout-pouches':'/catalog/spout-refill-pouches/','three-side-seal-pouches':'/catalog/flat-pouches-sachets/','sachets':'/catalog/flat-pouches-sachets/','folding-cartons':'/catalog/folding-cartons/','mailer-boxes':'/catalog/mailer-shipping-boxes/','magnetic-gift-boxes':'/catalog/magnetic-boxes/','drawer-boxes':'/catalog/drawer-boxes/','lid-and-base-boxes':'/catalog/lid-base-boxes/','tube-boxes':'/catalog/paper-tubes/','display-boxes':'/catalog/cardboard-displays/','packaging-sleeves':'/catalog/packaging-sleeves-wraps/','paper-mailing-bags':'/catalog/paper-mailing-bags/','poly-mailers':'/catalog/poly-mailing-bags/'}.get(slug,{'custom-boxes':'/catalog/paper-boxes/','paper-bags':'/catalog/paper-bags/','flexible-pouches':'/catalog/pouches/','plastic-bags':'/catalog/poly-bags/','cards-tags':'/catalog/cards-booklets/','stickers-labels':'/catalog/stickers-labels/'}[family])

for c in CATEGORIES:
 family=c['slug'];items=PRODUCTS[family]
 trail='<a href="/products/">Packaging</a> / '+c['name']
 body=detailhero('Custom packaging',c['name'],c['summary'],art(c['art']),c['name'],trail)
 used_images={ux_item(UX_VISUALS['family_heroes'][c['art']])['image']}
 shown_formats=set()
 body+='<section class="section wrap"><div class="sectionhead centered"><h2>Choose your format.</h2><p>'+c['intro']+'</p></div><div class="formats">'
 for slug,name,desc,options,check,use in items:
  if slug not in format_references:continue
  reference=format_references.get(slug)
  if reference['image'] in used_images:continue
  shown_formats.add(slug)
  photo=('<a class="format-photo" href="/products/'+family+'/'+slug+'/"><div class="art"><img src="'+reference['image']+'" alt="'+esc(name,quote=True)+' structure reference" width="'+str(reference['width'])+'" height="'+str(reference['height'])+'" loading="lazy"></div></a>') if reference else ''
  used_images.add(reference['image'])
  body+='<article class="format">'+photo+'<h3><a href="/products/'+family+'/'+slug+'/">'+name+'</a></h3><p>'+desc+'</p><a class="textlink" href="/products/'+family+'/'+slug+'/">View '+name.lower()+'</a></article>'
 body+='</div>'
 missing=[item for item in items if item[0] not in shown_formats]
 if missing:body+='<div class="ux-additional-formats"><h3>More formats to discuss</h3><p>Share your requirements for these structures. A matching reference and sample can be reviewed with your project.</p><div class="related-links">'+''.join('<a href="/products/'+family+'/'+item[0]+'/">'+esc(item[1])+'</a>' for item in missing)+'</div></div>'
 body+='<p class="catalog-browse-link"><a class="textlink" href="/catalog/">Browse product photos and specifications ↗</a></p></section><section class="section softbg"><div class="wrap split"><div><h2>Made around your product.</h2><p>Share the product, approximate size, quantity per design and delivery market. We can then review the material, print and sample you need.</p><a class="textlink" href="/guides/packaging-quote-checklist/">What to include in a quote request</a></div><div><h3>Explore the details</h3><div class="related-links vertical"><a href="/materials/">Materials & finishes</a><a href="/services/sampling/">Samples & approvals</a><a href="/services/artwork-preflight/">Artwork preparation</a></div></div></div></section>'+cta()
 comparisons=ux_references('/products/'+family+'/',exclude=used_images)
 body=body.removesuffix(cta())+('<section class="section wrap"><div class="sectionhead"><h2>Compare Product References</h2></div>'+ux_reference_cards(comparisons)+'</section>' if comparisons else '')+'<section class="section softbg"><div class="wrap faqwrap"><h2>Frequently Asked Questions</h2>'+ux_faq()+'</div></section>'+cta()
 write('/products/'+family+'/',c['name']+' with Custom Printing | PackHubGlobe',c['summary'],body)
 for slug,name,desc,options,check,use in items:
  path='/products/'+family+'/'+slug+'/'
  title='Custom '+name.lower()+' with Logo Printing'
  title=title[0].upper()+title[1:]
  buying_guide=BUYING_GUIDES.get(slug)
  if buying_guide:
   title=buying_guide['title'];desc=buying_guide['description']
  trail='<a href="/products/">Packaging</a> / <a href="/products/'+family+'/">'+c['name']+'</a> / '+name
  visual=format_visual(slug,name,c)
  body=detailhero(c['name'],buying_guide['heading'] if buying_guide else 'Custom '+name.lower(),desc,visual,name,trail,'',facts=[('Packaging style',name),('Structure & options',options),('Custom dimensions','Sized around your product; confirm measurement units'),('Printing & finishes','Review artwork, colors and selected finishes'),('Applications',use)])
  body+='<section class="section wrap product-details"><div><h2>Make it your own.</h2><p>Review these details with your product and artwork.</p>'+specs([('Structure & options',options),('Sample check',check),('For your quotation','Approximate dimensions or fill weight, quantity per size and design, artwork status and delivery country.')])+'</div><aside class="help-note"><h3>Not sure where to start?</h3><p>Send a product photo or reference with your enquiry. We’ll help you define the next step.</p><a class="textlink" href="/guides/packaging-sample-types/">Understand sample options</a><a class="textlink" href="/guides/packaging-print-proof/">Review print proofs</a><p class="smallnote">Catalog references start at 500 pieces. Confirm the final features, performance requirements and quantity split in the written quotation.</p></aside></section>'
  body+='<section class="section wrap"><h2>Compare product references.</h2><p>Browse images and specification starting points for this packaging direction.</p><a class="textlink" href="'+format_collection(slug,family)+'">Browse related product references ↗</a></section>'
  if buying_guide:body+=buying_guide['body']
  other=[family+'/'+r[0] for r in items if r[0]!=slug][:3]
  body+='<section class="section softbg"><div class="wrap"><h2>Other formats to explore.</h2>'+related(other)+'</div></section>'+cta()
  write(path,title+' | PackHubGlobe',desc,body,[{'@type':'Service','name':title,'description':desc,'serviceType':'Packaging specification and custom printing'}])

overview=intro('Industry solutions','Packaging for your industry.','Find a starting point for your product, from the retail pack to the delivery box.')+'<section class="wrap section" style="padding-top:0"><div class="industry-grid">'
for slug,name,desc,brief,approach,check,links,img in INDUSTRIES:
 industry_items=[ux_item(ref) for ref in UX_VISUALS['industries'][slug]]
 industry_image=('<div class="art">'+ux_photo(industry_items[0])+'</div>') if industry_items else ''
 overview+='<a class="industry-card" href="/industries/'+slug+'/">'+industry_image+'<h2>'+name+'</h2><p>'+desc+'</p><span class="cardlink">Explore packaging</span></a>'
 visual=('<figure class="catalog-product-image">'+ux_photo(industry_items[0],True)+'<figcaption>Related packaging reference; confirm suitability for your product.</figcaption></figure>') if industry_items else scene(img,'Illustrative '+name.lower()+' with branded printed packaging')
 body=detailhero('Industry packaging',name,desc,visual,name,'<a href="/industries/">Industries</a> / '+name)
 body+='<section class="section wrap"><div class="two"><section><h2>Build your packaging range.</h2><p>'+approach+'</p></section><section><h2>Check what matters.</h2><p>'+check+'</p></section></div><details class="technical"><summary>What to include in your enquiry</summary><p>'+brief+'</p><p>Include the quantity for each component and design, artwork status, delivery country and target arrival window.</p></details></section>'
 body+='<section class="section wrap"><h2>Product References for Your Project</h2>'+ux_reference_cards(industry_items[1:4])+'</section>'
 body+='<section class="section wrap"><h2>Coordinate the complete packaging set</h2><p><a class="textlink" href="/cases/">Compare coordinated design concepts ↗</a></p></section><section class="section softbg"><div class="wrap"><h2>Packaging to explore.</h2>'+related(links)+'</div></section>'+cta()
 write('/industries/'+slug+'/',name+' Solutions | PackHubGlobe',desc,body)
overview+='</div></section>'+cta()
write('/industries/','Custom Packaging by Industry | PackHubGlobe','Explore custom packaging for beauty, coffee, food, pet products, apparel, gifting, ecommerce and more.',overview)

for root,label,records in [('materials','Materials & finishes',MATERIALS),('services','Packaging services',SERVICES)]:
 overview=intro(label,label+'.','Explore the choices that shape your packaging, with practical guidance for your project.')+'<section class="section wrap" style="padding-top:0"><div class="formats">'
 for slug,name,desc,first,second,third,links in records:
  overview+='<article class="format"><h2><a href="/'+root+'/'+slug+'/">'+name+'</a></h2><p>'+desc+'</p><a class="textlink" href="/'+root+'/'+slug+'/">Learn more</a></article>'
  body=intro(label,name,desc,'<a href="/'+root+'/">'+label+'</a> / '+name)
  material_refs={'paperboard':'PHG-FP-1601095882863','corrugated-board':'PHG-1600659751763','kraft-paper':'PHG-60519970698','barrier-films':'PHG-PC-FE809D4EF8','recyclable-structures':'PHG-60519970698'}
  service_images={'structural-design':'company/sample-room','sampling':'company/sample-room','artwork-preflight':'process/plate-making','quality-control':'process/gluing','export-packing':'company/material-warehouse','multi-product-sourcing':'company/sample-room'}
  if root=='materials' and slug in material_refs:
   item=ux_item(material_refs[slug])
   body+='<figure class="wrap ux-material-photo ux-material-product">'+ux_photo(item,True)+'<figcaption>Related '+esc(name.lower())+' reference. <a href="'+item['path']+'">View the product specification</a>. Confirm the complete material and intended use for your project.</figcaption></figure>'
  else:
   image='process/lamination' if root=='materials' else service_images[slug]
   caption='Lamination equipment reference; review the selected surface finish on a physical sample.' if root=='materials' else {'structural-design':'Sample-room reference; dimensions and construction are developed around your product.','sampling':'Sample-room reference; agree the sample type and the decisions it needs to verify.','artwork-preflight':'Plate-making production reference; approve artwork and dieline revisions before print preparation.','quality-control':'Folding and gluing production reference; agree separate inspection points for the finished packaging.','export-packing':'Paper and board storage reference; export packing and freight are specified separately for your order.','multi-product-sourcing':'Packaging sample-room reference; coordinate each component in a single project brief.'}[slug]
   body+='<figure class="wrap ux-material-photo"><img src="/assets/'+image+'.webp" alt="'+esc(name,quote=True)+' production and project reference" width="1000" height="750" loading="lazy"><figcaption>'+caption+'</figcaption></figure>'
  body+='<article class="article wrap">'+sections([('Start with your product',first),('Review the options',second),('Confirm before approval',third)])+'</article><section class="section softbg"><div class="wrap"><h2>Related packaging.</h2>'+related(links)+'</div></section>'+cta()
  if root=='materials' and slug in ['paperboard','kraft-paper','recyclable-structures']:body=body.removesuffix(cta())+documentation_link('paper')+cta()
  if root=='services' and slug=='quality-control':body=body.removesuffix(cta())+documentation_link('quality')+cta()
  write('/'+root+'/'+slug+'/',name+' | PackHubGlobe',desc,body)
 overview+='</div></section>'+cta()
 write('/'+root+'/',label+' | PackHubGlobe','Explore '+label.lower()+' for custom boxes, bags, pouches, cards and labels.',overview)

from geo_guides import GUIDES as GEO_GUIDES
for guide in GEO_GUIDES:
 expanded_content.GUIDE_EXPANSIONS[guide['slug']]=guide
EXTRA_GUIDES=EXTRA_GUIDES+[(g['slug'],g['title'],g['description'],g['chapters']) for g in GEO_GUIDES]

allguides=[(g[0],g[2],g[3],g[4]) for g in GUIDES]+EXTRA_GUIDES
overview=intro('Buyer resources','Packaging buying guides for business buyers.','Compare packaging structures, materials, samples and artwork requirements before requesting a custom quotation.')
overview+='<section class="section wrap"><h2>What are you deciding?</h2><div class="related-links">'+''.join('<a href="/guides/'+slug+'/">'+TOPICS[slug][0]+'</a>' for slug in ['packaging-quote-checklist','folding-cartons-vs-rigid-boxes','packaging-materials-explained','custom-packaging-moq','prepare-packaging-dielines','choose-packaging-supplier-china'])+'</div></section><section class="section wrap" style="padding-top:0"><h2>Explore the buying guides</h2><div class="resourcegrid">'
for slug,title,desc,chapters in allguides:
 overview+='<article class="guidecard"><h2><a href="/guides/'+slug+'/">'+title+'</a></h2><p>'+desc+'</p><a class="textlink" href="/guides/'+slug+'/">Read guide</a></article>'
 body=intro('Buyer guide',title,desc,'<a href="/guides/">Guides</a> / '+title)
 updated='2026-11-05'
 guide_image=scene('beauty' if slug=='cosmetic-packaging-buyers-guide' else 'packing' if slug=='apparel-packaging-selection' else 'general','Illustrative packaging design concept; not a customer order') if slug in {g['slug'] for g in GEO_GUIDES} else ''
 body+='<article class="article wrap guide-longform"><p class="article-byline">By <a href="/about/">PackHubGlobe</a> · Updated <time datetime="'+updated+'">'+'5 November 2026'+'</time></p><nav class="article-toc" aria-label="Guide contents"><a href="#worked-example">Worked example</a><a href="#comparison">Comparison</a><a href="#approval-checklist">Checklist</a><a href="#guide-faq">FAQ</a></nav>'+'<aside class="guide-answer" aria-labelledby="quick-answer"><h2 id="quick-answer">Quick answer</h2><p>'+esc(expanded_content.GUIDE_EXPANSIONS[slug]['answer'])+'</p><ul>'+''.join('<li>'+esc(check)+'</li>' for check in expanded_content.GUIDE_EXPANSIONS[slug]['checks'][:3])+'</ul></aside>'+guide_image+(''.join('<section id="quote-step-'+str(i+1)+'"><h2>'+esc(name)+'</h2><p>'+esc(text)+'</p></section>' for i,(name,text) in enumerate(chapters)) if slug=='packaging-quote-checklist' else sections(chapters))+guide_extra(slug)+'<p class="article-note">For your own project, confirm the specification and sample requirements with us. <a href="/services/sampling/">Explore sampling</a> or <a href="/products/">browse packaging</a>.</p></article>'+cta()
 allowed=TOPICS[slug][1]
 candidates=[item for item in UX_INDEX if not allowed or item['format'] in allowed]
 terms={'cosmetic-packaging-buyers-guide':['skincare','cosmetic','serum','perfume'],'apparel-packaging-selection':['apparel','clothing','garment','hang tag']}.get(slug,[])
 if terms:candidates=[item for item in candidates if any(word in item['name'].lower() for word in terms)]
 examples=[];formats=set()
 for item in candidates:
  if item['format'] not in formats:examples.append(item);formats.add(item['format'])
 examples=(examples+[item for item in candidates if item not in examples])[:3]
 body=body.removesuffix(cta())+'<section class="section wrap" id="product-examples"><h2>Compare specification references</h2><p>Use these product images and reference specifications to apply the decisions in this guide. They are starting points for your quotation, and should be confirmed against your final specification.</p>'+ux_reference_cards(examples)+'</section>'+cta()
 write('/guides/'+slug+'/',title+' | PackHubGlobe',desc,body,guide_schemas(slug,title,chapters,updated))
overview+='</div></section>'+cta()
write('/guides/','Packaging Guides for B2B Buyers | PackHubGlobe','Compare packaging structures, dimensions, print proofs, sample types, label rolls and material choices.',overview,[{'@type':'ItemList','name':'Packaging buyer guides','numberOfItems':len(allguides),'itemListElement':[{'@type':'ListItem','position':i+1,'name':g[1],'url':ORIGIN+'/guides/'+g[0]+'/'} for i,g in enumerate(allguides)]}])

body=intro('Design references','Packaging ideas, brought together.','Explore fictional-brand concepts for coffee, beauty and ecommerce. These illustrate design directions, rather than completed customer orders.')+'<section class="section wrap" style="padding-top:0">'
for name,desc,links,img in [('Coffee range','Coordinate a printed pouch, retail bag, labels and insert card.',['flexible-pouches/flat-bottom-pouches','paper-bags/kraft-paper-bags','stickers-labels/roll-labels'],'coffee'),('Beauty presentation','Bring cartons, gift boxes and care cards into one range.',['custom-boxes/rigid-boxes','custom-boxes/folding-cartons','cards-tags/care-cards'],'beauty'),('Ecommerce unboxing','Connect a mailer, printed card and seal with your packing workflow.',['custom-boxes/mailer-boxes','cards-tags/insert-cards','stickers-labels/packaging-seals'],'packing')]:
 body+='<section class="project-example split">'+scene(img,name+' fictional-brand packaging concept')+'<div><h2>'+name+'</h2><p>'+desc+'</p>'+related(links)+'<a class="textlink" href="'+qurl(name)+'">Discuss a similar direction</a></div></section>'
body+='</section><section class="section wrap"><h2>Explore Product References</h2><p>Compare product images, material references and print options. These are specification starting points, not verified customer case studies.</p>'+ux_reference_cards([ux_item(ref) for ref in UX_FEATURES])+'</section>'+cta()
body=body.removesuffix(cta())+'<section class="section wrap"><h2>Explore the industry requirements</h2><div class="related-links"><a href="/industries/beauty-skincare/">Beauty and skincare</a><a href="/industries/coffee-tea/">Coffee packaging</a><a href="/industries/ecommerce/">Ecommerce packaging</a></div></section>'+cta()
write('/cases/','Packaging Project & Print Design References | PackHubGlobe','Explore original packaging design concepts for coffee, beauty and ecommerce, with product specifications to discuss.',body)

privacy=[('Your enquiry','Submitting the packaging form sends your details to our website server for email delivery to andrew@packhubglobe.com. A success message means the server accepted the enquiry for email delivery; it does not confirm inbox receipt. The download option creates a text brief locally in your browser. You can attach up to 5 artwork, image or reference files (5 MB per file, 10 MB total). Uploaded files are temporarily processed on the server and included as email attachments; the website does not publish them or keep a separate permanent upload copy.'),('Information you choose to provide','An email enquiry may include your name, business email, company, product requirements and files you attach. Provide only information needed to discuss the packaging project. Avoid sending unnecessary personal or sensitive data.'),('Purpose and contact','We use enquiry information to discuss specifications, provide quotations, arrange samples and handle the requested business relationship. Email and hosting providers may process information as part of delivering those services. Hosting may also record ordinary technical access logs.'),('Your choices','You can contact andrew@packhubglobe.com to ask about your enquiry information or request correction or deletion, subject to any applicable record-keeping requirements. Contact details and form input are not saved by default. If you opt in to keep an enquiry draft, its text fields are saved in session storage for this browser tab until you clear the saved draft, successfully submit the full form or close the tab. Files and consent are never saved. The clear control removes only the saved copy; you can still edit the current form. Product references selected in your quote basket are saved on this device until you remove them or clear the basket.'),('WhatsApp','WhatsApp links open an external chat service. Information you choose to share there is handled through WhatsApp and its own privacy terms. A link does not send a message automatically.'),('Website resources','Images, fonts, styles and scripts are hosted with this website. The site prepares event names and page paths in browser memory for a future analytics integration. No external analytics collector, advertising pixel or marketing-cookie system is connected. Enquiry text, contact details and file contents are not included in these events. External reference links have their own policies. The companies behind the brand are identified on the About page.')]
write('/privacy/','Privacy & Enquiry Information | PackHubGlobe','Read how PackHubGlobe handles email enquiries, form input and website resources.',intro('Privacy information','Privacy information.','Understand what this website does with the information you choose to share.')+'<article class="article wrap">'+sections(privacy)+'<p><a href="/about/">About PackHubGlobe</a> · <a href="mailto:'+EMAIL+'">Contact us about your information</a></p></article>')
terms=[('Information and quotations','This website introduces packaging formats and decisions to review. A product page or design reference is not a binding quotation. Price, minimum quantity, materials, features, samples, production, payment and delivery are confirmed in the written quotation and agreed order.'),('Specifications and artwork','Confirm dimensions, material, print, finish, quantity and artwork versions before production. The customer should approve product wording, claims, translations, barcodes and other content, and have the right to use any supplied artwork.'),('Samples and timing','Samples answer the decisions agreed for their sample type. A sample or illustration does not establish every aspect of final performance. Production and shipping dates require project-specific confirmation; delivery assumptions should be clear in the quotation.'),('Design references','Original virtual-brand images on this website illustrate printing and packaging directions. They do not represent endorsements, registered customer brands, test results or completed client orders. Requested finishes and features are subject to material and production review.'),('Responsible supply','The written quotation identifies the supplying company and the agreed commercial terms. Read About and Factory for the companies and areas of responsibility behind PackHubGlobe. Contact andrew@packhubglobe.com for a project-specific clarification.')]
write('/terms/','Quotation & Website Information | PackHubGlobe','Understand how packaging references, quotations, artwork, samples and order specifications are handled.',intro('Quotation information','Quotation & website terms.','The points below explain how website information relates to a packaging enquiry and an agreed order.')+'<article class="article wrap">'+sections(terms)+'<p><a href="/about/">About the brand</a> · <a href="/request-quote/">Prepare your enquiry</a></p></article>')
editorial=[('Purpose','The packaging notebook helps buyers ask clearer questions and prepare comparable specifications. Product, material and process guidance is framed around the actual application rather than a universal promise.'),('Claims and evidence','We do not publish invented prices, delivery guarantees, ratings, test results or certifications. Numerical performance and compliance claims need evidence for the relevant material, structure, intended use and conditions.'),('Imagery','Original fictional logos, slogans and photorealistic design references demonstrate graphic directions. They are labelled as concepts and are not used as proof of a factory, certificate or customer relationship.'),('Sources and revisions','Company information is linked to source profiles on the About and Factory pages. Guidance should be revised when a relevant specification or source changes. We do not change dates solely to imply freshness.'),('Corrections','Email andrew@packhubglobe.com with the page URL and the point that needs review. For a purchasing decision, request a written specification and suitable sample or evidence for your actual project.')]
write('/editorial-policy/','Editorial & Image Policy | PackHubGlobe','Read PackHubGlobe’s approach to procurement guidance, factual claims, original concept imagery and corrections.',intro('Editorial policy','Editorial & image policy.','How we present packaging guidance, design references and project information.')+'<article class="article wrap">'+sections(editorial)+'</article>')

exec(compile((ROOT/'tools/catalog.py').read_text(),str(ROOT/'tools/catalog.py'),'exec'))

errorbody=intro('Page not found','Let’s find the right package.','This address does not match a page on PackHubGlobe. Browse the packaging collection or start a brief.')+'<section class="wrap section" style="padding-top:0"><div class="actions">'+button('Explore packaging','/products/')+button('Contact PackHubGlobe','/request-quote/','light')+'</div></section>'
write('/404/','Page Not Found | PackHubGlobe','Find packaging products or contact PackHubGlobe.',errorbody)
error=(ROOT/'404/index.html').read_text().replace('content="index,follow"','content="noindex,follow"')
(ROOT/'404.html').write_text(error);(ROOT/'404/index.html').unlink();(ROOT/'404').rmdir();PAGES[:]=[p for p in PAGES if p[0]!='/404/']

exec(compile((ROOT/'tools/blog.py').read_text(),str(ROOT/'tools/blog.py'),'exec'))

from xml.sax.saxutils import escape as xesc
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('  <url><loc>'+xesc(ORIGIN+p[0])+'</loc>'+('<lastmod>2026-11-06</lastmod>' if p[0]=='/guides/' or p[0].startswith('/blog/') else '<lastmod>2026-11-05</lastmod>' if p[0].startswith('/guides/') else '')+'</url>\n' for p in sorted(PAGES))+'</urlset>\n')
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /tools/\nDisallow: /content/\nDisallow: /qa/\nDisallow: /.git/\n\n# Public search and retrieval crawlers use the same rules as all visitors.\n# Training policy is unchanged; no training-specific permission is required for search.\nSitemap: '+ORIGIN+'/sitemap.xml\n')
(ROOT/'llms.txt').write_text('# PackHubGlobe\n\nCustom packaging and printing for business buyers. Contact: '+EMAIL+'. Catalog MOQ is 500 pieces. Pricing, materials and production timing require a project-specific quotation. Original virtual-brand imagery is illustrative.\n\n'+''.join('- ['+title+']('+ORIGIN+path+'): '+desc+'\n' for path,title,desc in PAGES if path in ['/','/catalog/','/products/','/industries/','/materials/','/services/','/guides/','/about/','/factory/','/request-quote/'] or path.startswith(('/guides/','/blog/','/products/','/industries/','/materials/','/services/'))))
# Superseded pagination is redirected; it must not remain as an orphaned HTML page.
for old_path in json.loads((ROOT/'content/catalog-redirects.json').read_text()):
 stale=ROOT/old_path.strip('/')/'index.html'
 if stale.exists():stale.unlink()
(ROOT/'content/page-manifest.json').write_text(json.dumps(sorted(PAGES),indent=2))
print(f'Built {len(PAGES)} public pages plus a real 404 document for {ORIGIN}')

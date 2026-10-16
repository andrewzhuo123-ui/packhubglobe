"""Build the complete static product, industry and resource page inventory."""
import sys
sys.path.insert(0,str(ROOT/'content'))
from products import PRODUCTS
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

for c in CATEGORIES:
 family=c['slug'];items=PRODUCTS[family]
 trail='<a href="/products/">Packaging</a> / '+c['name']
 body=detailhero('Custom packaging',c['name'],c['summary'],art(c['art']),c['name'],trail)
 body+='<section class="section wrap"><div class="sectionhead centered"><h2>Choose your format.</h2><p>'+c['intro']+'</p></div><div class="formats">'
 for slug,name,desc,options,check,use in items:
  body+='<article class="format"><h3><a href="/products/'+family+'/'+slug+'/">'+name+'</a></h3><p>'+desc+'</p><a class="textlink" href="/products/'+family+'/'+slug+'/">View '+name.lower()+'</a></article>'
 body+='</div><p class="catalog-browse-link"><a class="textlink" href="/catalog/">Browse product photos and specifications ↗</a></p></section><section class="section softbg"><div class="wrap split"><div><h2>Made around your product.</h2><p>Share the product, approximate size, quantity per design and delivery market. We can then review the material, print and sample you need.</p><a class="textlink" href="/guides/packaging-quote-checklist/">What to include in a quote request</a></div><div><h3>Explore the details</h3><div class="related-links vertical"><a href="/materials/">Materials & finishes</a><a href="/services/sampling/">Samples & approvals</a><a href="/services/artwork-preflight/">Artwork preparation</a></div></div></div></section>'+cta()
 write('/products/'+family+'/',c['name']+' with Custom Printing | PackHubGlobe',c['summary'],body)
 for slug,name,desc,options,check,use in items:
  path='/products/'+family+'/'+slug+'/'
  title='Custom '+name.lower()+' with Logo Printing'
  title=title[0].upper()+title[1:]
  trail='<a href="/products/">Packaging</a> / <a href="/products/'+family+'/">'+c['name']+'</a> / '+name
  visual='<figure class="productvisual">'+art(c['art'])+'<figcaption>Packaging family design reference</figcaption></figure>'
  body=detailhero(c['name'],'Custom '+name.lower(),desc,visual,name,trail,use)
  body+='<section class="section wrap product-details"><div><h2>Make it your own.</h2><p>Review these details with your product and artwork.</p>'+specs([('Structure & options',options),('Sample check',check),('For your quotation','Approximate dimensions or fill weight, quantity per size and design, artwork status and delivery country.')])+'</div><aside class="help-note"><h3>Not sure where to start?</h3><p>Send a product photo or reference with your enquiry. We’ll help you define the next step.</p><a class="textlink" href="/guides/packaging-sample-types/">Understand sample options</a><a class="textlink" href="/guides/packaging-print-proof/">Review print proofs</a><p class="smallnote">Final features, MOQ and performance requirements are confirmed for the agreed specification.</p></aside></section>'
  other=[family+'/'+r[0] for r in items if r[0]!=slug][:3]
  body+='<section class="section softbg"><div class="wrap"><h2>Other formats to explore.</h2>'+related(other)+'</div></section>'+cta()
  write(path,title+' | PackHubGlobe',desc,body,[{'@type':'Service','name':title,'description':desc,'serviceType':'Packaging specification and custom printing'}])

overview=intro('Industry solutions','Packaging for your industry.','Find a starting point for your product, from the retail pack to the delivery box.')+'<section class="wrap section" style="padding-top:0"><div class="industry-grid">'
for slug,name,desc,brief,approach,check,links,img in INDUSTRIES:
 overview+='<a class="industry-card" href="/industries/'+slug+'/"><h2>'+name+'</h2><p>'+desc+'</p><span class="cardlink">Explore packaging</span></a>'
 visual=scene(img,'Illustrative '+name.lower()+' with branded printed packaging')
 body=detailhero('Industry packaging',name,desc,visual,name,'<a href="/industries/">Industries</a> / '+name)
 body+='<section class="section wrap"><div class="two"><section><h2>Build your packaging range.</h2><p>'+approach+'</p></section><section><h2>Check what matters.</h2><p>'+check+'</p></section></div><details class="technical"><summary>What to include in your enquiry</summary><p>'+brief+'</p><p>Include the quantity for each component and design, artwork status, delivery country and target arrival window.</p></details></section>'
 body+='<section class="section softbg"><div class="wrap"><h2>Packaging to explore.</h2>'+related(links)+'</div></section>'+cta()
 write('/industries/'+slug+'/',name+' Solutions | PackHubGlobe',desc,body)
overview+='</div></section>'+cta()
write('/industries/','Custom Packaging by Industry | PackHubGlobe','Explore custom packaging for beauty, coffee, food, pet products, apparel, gifting, ecommerce and more.',overview)

for root,label,records in [('materials','Materials & finishes',MATERIALS),('services','Packaging services',SERVICES)]:
 overview=intro(label,label+'.','Explore the choices that shape your packaging, with practical guidance for your project.')+'<section class="section wrap" style="padding-top:0"><div class="formats">'
 for slug,name,desc,first,second,third,links in records:
  overview+='<article class="format"><h2><a href="/'+root+'/'+slug+'/">'+name+'</a></h2><p>'+desc+'</p><a class="textlink" href="/'+root+'/'+slug+'/">Learn more</a></article>'
  body=intro(label,name,desc,'<a href="/'+root+'/">'+label+'</a> / '+name)
  body+='<article class="article wrap">'+sections([('Start with your product',first),('Review the options',second),('Confirm before approval',third)])+'</article><section class="section softbg"><div class="wrap"><h2>Related packaging.</h2>'+related(links)+'</div></section>'+cta()
  write('/'+root+'/'+slug+'/',name+' | PackHubGlobe',desc,body)
 overview+='</div></section>'+cta()
 write('/'+root+'/',label+' | PackHubGlobe','Explore '+label.lower()+' for custom boxes, bags, pouches, cards and labels.',overview)

allguides=[(g[0],g[2],g[3],g[4]) for g in GUIDES]+EXTRA_GUIDES
overview=intro('Buyer resources','Packaging guides.','Practical answers for choosing packaging, preparing artwork and planning your order.')+'<section class="section wrap" style="padding-top:0"><div class="resourcegrid">'
for slug,title,desc,chapters in allguides:
 overview+='<article class="guidecard"><h2><a href="/guides/'+slug+'/">'+title+'</a></h2><p>'+desc+'</p><a class="textlink" href="/guides/'+slug+'/">Read guide</a></article>'
 body=intro('Buyer guide',title,desc,'<a href="/guides/">Guides</a> / '+title)
 body+='<article class="article wrap">'+sections(chapters)+'<p class="article-note">For your own project, confirm the specification and sample requirements with us. <a href="/services/sampling/">Explore sampling</a> or <a href="/products/">browse packaging</a>.</p></article>'+cta()
 write('/guides/'+slug+'/',title+' | PackHubGlobe',desc,body)
overview+='</div></section>'+cta()
write('/guides/','Packaging Guides for B2B Buyers | PackHubGlobe','Compare packaging structures, dimensions, print proofs, sample types, label rolls and material choices.',overview)

body=intro('Design references','Packaging ideas, brought together.','Explore fictional-brand concepts for coffee, beauty and ecommerce. These illustrate design directions, rather than completed customer orders.')+'<section class="section wrap" style="padding-top:0">'
for name,desc,links,img in [('Coffee range','Coordinate a printed pouch, retail bag, labels and insert card.',['flexible-pouches/flat-bottom-pouches','paper-bags/kraft-paper-bags','stickers-labels/roll-labels'],'coffee'),('Beauty presentation','Bring cartons, gift boxes and care cards into one range.',['custom-boxes/rigid-boxes','custom-boxes/folding-cartons','cards-tags/care-cards'],'beauty'),('Ecommerce unboxing','Connect a mailer, printed card and seal with your packing workflow.',['custom-boxes/mailer-boxes','cards-tags/insert-cards','stickers-labels/packaging-seals'],'packing')]:
 body+='<section class="project-example split">'+scene(img,name+' fictional-brand packaging concept')+'<div><h2>'+name+'</h2><p>'+desc+'</p>'+related(links)+'<a class="textlink" href="'+qurl(name)+'">Discuss a similar direction</a></div></section>'
body+='</section>'+cta()
write('/cases/','Packaging Project & Print Design References | PackHubGlobe','Explore original packaging design concepts for coffee, beauty and ecommerce, with product specifications to discuss.',body)

privacy=[('Your enquiry','The packaging form prepares an email draft or a downloadable text brief in your browser. It does not automatically submit your details to a form server. Opening the draft passes the details to your chosen email application; sending that email delivers it to andrew@packhubglobe.com.'),('Information you choose to provide','An email enquiry may include your name, business email, company, product requirements and files you attach. Provide only information needed to discuss the packaging project. Avoid sending unnecessary personal or sensitive data.'),('Purpose and contact','We use enquiry information to discuss specifications, provide quotations, arrange samples and handle the requested business relationship. Email and hosting providers may process information as part of delivering those services. Hosting may also record ordinary technical access logs.'),('Your choices','You can contact andrew@packhubglobe.com to ask about your enquiry information or request correction or deletion, subject to any applicable record-keeping requirements. Form input is not intentionally saved to browser storage by this website.'),('WhatsApp','WhatsApp links open an external chat service. Information you choose to share there is handled through WhatsApp and its own privacy terms. A link does not send a message automatically.'),('Website resources','Images, fonts, styles and scripts are hosted with this website. No visitor analytics, advertising pixels or marketing-cookie system is installed in this version. External reference links have their own policies. The companies behind the brand are identified on the About page.')]
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

from xml.sax.saxutils import escape as xesc
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('  <url><loc>'+xesc(ORIGIN+p[0])+'</loc></url>\n' for p in sorted(PAGES))+'</urlset>\n')
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /tools/\nDisallow: /content/\n\nSitemap: '+ORIGIN+'/sitemap.xml\n')
(ROOT/'llms.txt').write_text('# PackHubGlobe\n\nCustom packaging and printing for business buyers. Contact: '+EMAIL+'. MOQ, pricing, materials and production timing require a project-specific quotation. Original virtual-brand imagery is illustrative.\n\n'+''.join('- ['+title+']('+ORIGIN+path+'): '+desc+'\n' for path,title,desc in PAGES if path in ['/','/catalog/','/products/','/industries/','/materials/','/services/','/guides/','/about/','/factory/','/request-quote/']))
(ROOT/'content/page-manifest.json').write_text(json.dumps(sorted(PAGES),indent=2))
print(f'Built {len(PAGES)} public pages plus a real 404 document for {ORIGIN}')

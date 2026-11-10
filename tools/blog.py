"""Build the Resources pillar, topic collections and question-led long-form posts."""
from datetime import date
from markdown_it import MarkdownIt

BLOG_CATEGORIES=json.loads((ROOT/'content/blog-categories.json').read_text())
BLOG_IMAGES=json.loads((ROOT/'content/blog-images.json').read_text())
BLOG_MARKDOWN=MarkdownIt('commonmark',{'html':True}).enable('table')
BLOG_POSTS=[]
for source in sorted((ROOT/'content/blog').glob('*.md')):
 _,metadata,markdown=source.read_text().split('---',2)
 post={key:json.loads(value) for line in metadata.strip().splitlines() for key,value in [line.split(': ',1)]};post.update(slug=source.stem,markdown=markdown.strip(),path='/blog/'+source.stem+'/')
 BLOG_POSTS.append(post)
BLOG_POSTS.sort(key=lambda post: post['publishedAt'],reverse=True)
BLOG_LASTMOD={post['path']:post['publishedAt'] for post in BLOG_POSTS}
BLOG_LASTMOD['/guides/']=BLOG_LASTMOD['/blog/']=BLOG_POSTS[0]['publishedAt']
for category in BLOG_CATEGORIES:
 BLOG_LASTMOD['/blog/category/'+category['slug']+'/']=max(post['publishedAt'] for post in BLOG_POSTS if post['category']==category['slug'])

def blog_date(value):
 return date.fromisoformat(value).strftime('%-d %B %Y')

def blog_figure(key,caption='',eager=False):
 image=BLOG_IMAGES[key]
 caption=caption or image.get('caption') or ('Illustrative AI design concept with fictional brands.' if image['reference'].startswith('Original AI') else 'Local image library reference; appearance does not establish material or performance.')
 return '<figure class="blog-figure"><img src="'+image['path']+'" alt="'+esc(image['alt'],quote=True)+'" width="'+str(image['width'])+'" height="'+str(image['height'])+'" '+('fetchpriority="high"' if eager else 'loading="lazy"')+'><figcaption>'+esc(caption)+'</figcaption></figure>'

def blog_cards(posts):
 body='<div class="resourcegrid blog-cards">'
 for post in posts:
  category=next(c for c in BLOG_CATEGORIES if c['slug']==post['category'])
  image=BLOG_IMAGES[post['hero']]
  body+='<article class="guidecard blog-card"><a class="blog-card-image" href="'+post['path']+'" tabindex="-1" aria-hidden="true"><img src="'+image['path']+'" alt="'+esc(image['alt'],quote=True)+'" width="'+str(image['width'])+'" height="'+str(image['height'])+'" loading="lazy"></a><div class="blog-card-copy"><p class="eyebrow">'+category['name']+'</p><h3><a href="'+post['path']+'">'+esc(post['title'])+'</a></h3><p>'+esc(post['description'])+'</p><p class="blog-meta"><time datetime="'+post['publishedAt']+'">'+blog_date(post['publishedAt'])+'</time> · '+str((len(post['markdown'].split())+219)//220)+' min read</p></div></article>'
 return body+'</div>'

def blog_list_schema(name,posts):
 return {'@type':'ItemList','name':name,'numberOfItems':len(posts),'itemListElement':[{'@type':'ListItem','position':i+1,'name':p['title'],'url':ORIGIN+p['path']} for i,p in enumerate(posts)]}

def blog_topic_nav(current=''):
 return '<nav class="blog-topics wrap" aria-label="Blog topics"><a href="/guides/"'+(' aria-current="page"' if current=='resources' else '')+'>All resources</a>'+''.join('<a href="/blog/category/'+c['slug']+'/"'+(' aria-current="page"' if current==c['slug'] else '')+'>'+c['name']+'</a>' for c in BLOG_CATEGORIES)+'</nav>'

for post in BLOG_POSTS:
 category=next(c for c in BLOG_CATEGORIES if c['slug']==post['category'])
 markdown=post['markdown'].split('\n',1)[1].strip()
 notes=re.findall(r'^\[\^(\d+)\]: (.+)$',markdown,re.M)
 markdown=re.sub(r'^\[\^\d+\]: .+$','',markdown,flags=re.M).strip()
 markdown=re.sub(r'\[\^(\d+)\]',lambda m:'<sup><a id="ref-'+m[1]+'" href="#note-'+m[1]+'" aria-label="Source '+m[1]+'">'+m[1]+'</a></sup>',markdown)
 preamble,*sections=markdown.split('\n## ')
 toc=[];content=BLOG_MARKDOWN.render(preamble)
 for i,section in enumerate(sections):
  heading,text=section.split('\n',1);anchor='conclusion' if heading=='Conclusion' else 'question-'+str(i+1)
  toc.append((anchor,heading));content+='<section id="'+anchor+'"><h2>'+esc(heading)+'</h2>'
  if heading=='Conclusion':content+=BLOG_MARKDOWN.render(text)
  else:
   opening,deep=text.split('\n### ',1)
   content+=BLOG_MARKDOWN.render(opening)+blog_figure(post['images'][i])+ '<div class="blog-depth">'+re.sub(r'<table>(.*?)</table>',r'<div class="blog-table" role="region" aria-label="Packaging decision comparison" tabindex="0"><table>\1</table></div>',BLOG_MARKDOWN.render('### '+deep),flags=re.S)+'</div>'
  content+='</section>'
 content=content.replace('<th>','<th scope="col">')
 content+='<aside class="blog-sources" aria-label="Sources and notes"><h2>Sources &amp; notes</h2><ol>'+''.join('<li id="note-'+n+'">'+BLOG_MARKDOWN.render(note)+'<a href="#ref-'+n+'" aria-label="Back to source '+n+' in the article">↩</a></li>' for n,note in notes)+'</ol></aside>'
 hero=post['hero']
 trail='<a href="/">Home</a> / <a href="/guides/">Resources</a> / <a href="/blog/category/'+category['slug']+'/">'+category['name']+'</a>'
 head='<header class="blog-heading wrap"><div class="breadcrumb">'+trail+'</div><p class="eyebrow">'+category['name']+'</p><h1>'+esc(post['title'])+'</h1><p class="blog-meta">By '+post['author']+' · <time datetime="'+post['publishedAt']+'">'+blog_date(post['publishedAt'])+'</time></p></header>'
 sidebar='<aside class="blog-sidebar"><nav aria-label="In this article"><p class="eyebrow">In this article</p><ol>'+''.join('<li><a href="#'+a+'">'+esc(h)+'</a></li>' for a,h in toc)+'</ol></nav><a class="textlink" href="/blog/category/'+category['slug']+'/">More in '+category['name']+' ↗</a></aside>'
 body=head+'<div class="wrap blog-layout"><article class="blog-article">'+blog_figure(hero,eager=True)+content+'</article>'+sidebar+'</div>'
 siblings=[p for p in BLOG_POSTS if p['category']==post['category'] and p!=post]
 body+='<section class="section wrap"><h2>Continue with a related question</h2>'+blog_cards(siblings)+'</section>'+cta()
 schema={'@type':'Article','@id':ORIGIN+post['path']+'#article','headline':post['title'],'description':post['description'],'datePublished':post['publishedAt'],'dateModified':post['publishedAt'],'author':{'@type':'Organization','name':post['author'],'url':ORIGIN+'/editorial-policy/'},'publisher':{'@id':ORIGIN+'/#brand'},'articleSection':category['name'],'inLanguage':'en','wordCount':len(post['markdown'].split()),'isPartOf':{'@id':ORIGIN+'/blog/#blog'}}
 write(post['path'],post['title']+' | PackHubGlobe',post['description'],body,[schema],breadcrumb=[('/guides/','Resources'),('/blog/category/'+category['slug']+'/',category['name']),(post['path'],post['title'])])

guide_map={g[0]:g for g in allguides}
# Every retained guide belongs to one topic; missing assignments are build errors.
assert set(guide_map)=={slug for c in BLOG_CATEGORIES for slug in c['guides']},'Update the resource topic map for the current guide inventory'
def blog_guide_links(category):
 return '<ul class="blog-guide-links">'+''.join('<li><a href="/guides/'+slug+'/">'+esc(guide_map[slug][1])+'</a></li>' for slug in category['guides'])+'</ul>'

for category in BLOG_CATEGORIES:
 posts=[p for p in BLOG_POSTS if p['category']==category['slug']]
 body=intro('Resource topic',category['name'],category['summary'],'<a href="/guides/">Resources</a> / '+category['name'])+blog_topic_nav(category['slug'])+'<section class="section wrap"><h2>'+category['question']+'</h2>'+blog_cards(posts)+'</section><section class="section softbg"><div class="wrap"><h2>Build the specification with these guides</h2>'+blog_guide_links(category)+'</div></section>'+cta()
 write('/blog/category/'+category['slug']+'/',category['name']+' Blog & Guides | PackHubGlobe',category['summary'],body,[blog_list_schema(category['name'],posts)],breadcrumb=[('/guides/','Resources'),('/blog/category/'+category['slug']+'/',category['name'])])

body=intro('Packaging blog','Practical answers for your next packaging order.','Long-form buying advice on packaging cost, shipping, materials, pouches, artwork and sample approval.','<a href="/guides/">Resources</a> / Blog')+blog_topic_nav()+'<section class="section wrap"><h2>Latest articles</h2>'+blog_cards(BLOG_POSTS)+'</section>'+cta()
write('/blog/','Packaging Blog for Business Buyers | PackHubGlobe','Read practical packaging articles on first-order costs, shipping protection, material claims, food pouches, print proofs and sample approvals.',body,[{'@type':'Blog','@id':ORIGIN+'/blog/#blog','name':'PackHubGlobe packaging blog','url':ORIGIN+'/blog/','publisher':{'@id':ORIGIN+'/#brand'}},blog_list_schema('Latest packaging articles',BLOG_POSTS)],breadcrumb=[('/guides/','Resources'),('/blog/','Blog')])

body='<section class="wrap blog-pillar-hero"><div><div class="breadcrumb"><a href="/">Home</a> / Resources</div><p class="eyebrow">The packaging notebook</p><h1>Better packaging starts with a better question.</h1><p>Build a clearer brief with practical blog articles and buying guides. Start with the decision that is holding up your order.</p><div class="actions">'+button('Choose a topic','#topics')+button('Browse all articles','/blog/','light')+'</div></div>'+blog_figure('collection',eager=True)+'</section>'+blog_topic_nav('resources')
body+='<section class="section softbg"><div class="wrap"><h2>What are you trying to solve?</h2><div class="blog-decisions">'+''.join('<a href="/blog/category/'+c['slug']+'/"><span>'+c['name']+'</span><strong>'+c['question']+'</strong></a>' for c in BLOG_CATEGORIES)+'</div></div></section>'
body+='<section class="section wrap" id="topics"><h2>Explore the topics</h2><p class="blog-intro">Each topic connects a practical decision with detailed articles and specification guides. Follow the evidence through your product, sample and written approval.</p>'
for category in BLOG_CATEGORIES:
 posts=[p for p in BLOG_POSTS if p['category']==category['slug']]
 body+='<section class="blog-topic-section"><div class="sectionhead"><div><p class="eyebrow">'+category['name']+'</p><h2>'+category['question']+'</h2><p>'+category['summary']+'</p></div><a class="textlink" href="/blog/category/'+category['slug']+'/">Explore topic ↗</a></div>'+blog_cards(posts)+'<details class="blog-guide-disclosure"><summary>Related buying guides ('+str(len(category['guides']))+')</summary>'+blog_guide_links(category)+'</details></section>'
body+='</section><section class="section softbg"><div class="wrap split"><div><h2>Turn reading into a reviewable brief.</h2><p>List your product, packed size or fill weight, quantity per design, artwork status and delivery market. Identify what the sample needs to prove.</p><a class="textlink" href="/guides/packaging-quote-checklist/">Prepare a packaging quote brief ↗</a></div><div><h2>Know what supports the advice.</h2><p>Articles separate practical judgment from documented claims. Source notes identify external references, and local library images illustrate formats without proving performance.</p><a class="textlink" href="/editorial-policy/">Read our editorial policy ↗</a></div></div></section>'+cta()
write('/guides/','Packaging Resources: Blog & Buying Guides | PackHubGlobe','Explore packaging blog topics and buying guides for sourcing costs, shipping protection, sustainable materials, food pouches, artwork and samples.',body,[blog_list_schema('Packaging resources',BLOG_POSTS)])

map_file=ROOT/'content/page-map.csv'
with map_file.open(encoding='utf-8-sig',newline='') as stream:
 reader=csv.DictReader(stream);fields=reader.fieldnames;rows=[r for r in reader if not r['url'].startswith(ORIGIN+'/blog/')]
for path,title,description in PAGES:
 if path.startswith('/blog/'):
  rows.append(dict(zip(fields,[ORIGIN+path,title,ORIGIN+'/guides/',title.split(' | ')[0],'P1','Resources','implemented','Researched blog content'])))
with map_file.open('w',encoding='utf-8-sig',newline='') as stream:
 writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(rows)

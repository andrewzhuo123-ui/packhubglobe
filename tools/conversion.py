"""Small enquiry forms that reuse the existing fixed-recipient PHP endpoint."""
def fast_quote_form(prefix,product='',reference='',source='/',image=''):
 hidden=''.join('<input type="hidden" name="'+k+'" value="'+esc(v,quote=True)+'">' for k,v in [('source_page',source),('product_reference',reference)])
 if product:
  field='<input type="hidden" name="product" value="'+esc(product,quote=True)+'"><div class="quick-context">'+('<img src="'+esc(image,quote=True)+'" alt="'+esc(product+' reference',quote=True)+'" width="72" height="72" loading="lazy">' if image else '')+'<p>'+esc(product)+'</p></div>'
 else:
  field='<div class="field"><label for="'+prefix+'-product">Packaging type</label><select id="'+prefix+'-product" name="product" required><option value="">Choose a packaging type</option>'+''.join('<option>'+v+'</option>' for v in ['Custom boxes','Paper bags','Flexible pouches','Plastic bags & mailers','Labels & stickers','Cards & hang tags','Help me choose'])+'</select></div>'
 return '<form class="fast-quote-form" data-fast-quote action="/request-quote/send.php" method="post">'+hidden+'<div hidden aria-hidden="true"><label for="'+prefix+'-website">Leave this field empty</label><input id="'+prefix+'-website" name="website" tabindex="-1" autocomplete="off"></div>'+field+'<div class="quick-fields"><div class="field"><label for="'+prefix+'-quantity">Estimated quantity per design</label><select id="'+prefix+'-quantity" name="quantity" required><option>500 pieces</option><option>1,000 pieces</option><option>3,000 pieces</option><option>5,000+ pieces</option><option>Help me confirm the quantity</option></select></div><div class="field"><label for="'+prefix+'-email">Work email</label><input id="'+prefix+'-email" name="email" type="email" autocomplete="email" maxlength="180" required></div></div><details class="optional-fields"><summary>Add project notes (optional)</summary><div class="field"><label for="'+prefix+'-details">Dimensions, artwork or delivery requirements</label><textarea id="'+prefix+'-details" name="details" rows="3" maxlength="6000"></textarea></div></details><label class="check"><input type="checkbox" name="consent" required><span>I agree to send these details to discuss my enquiry. <a href="/privacy/">Privacy</a></span></label><button class="button" type="submit">Send quote request</button><p class="fast-quote-status status" role="status" hidden></p><p class="smallnote">MOQ starts at 500 pieces per design. Price, specifications and timing are confirmed for your project.</p><noscript><p>Include project requirements in the notes before submitting, or <a href="/request-quote/">use the full enquiry form</a>.</p></noscript></form>'

def home_fast_quote():
 return '<section class="section softbg" id="fast-quote"><div class="wrap quick-home"><div><span class="eyebrow">Start with the essentials</span><h2>Tell us what you need to pack.</h2><p>Choose a packaging type, estimated quantity and email. Add project notes if you have them; we can discuss the remaining specification with you.</p><a class="textlink" href="/request-quote/">Have a detailed brief or artwork? Use the full form ↗</a></div>'+fast_quote_form('home')+'</div></section>'

def product_quote_drawer(body,path,extra):
 from html import unescape
 from urllib.parse import urlparse,parse_qs
 link=re.search(r'href="(/request-quote/\?product=[^"]+)"',body)
 if not link:return ''
 url=unescape(link[1]);product=parse_qs(urlparse(url).query).get('product',[''])[0]
 reference=next((v.get('sku','') for v in extra or [] if v.get('@type')=='Product'),'')
 image=re.search(r'<img\b[^>]*src="([^"]+)"',body)
 return '<dialog id="quick-quote-dialog" class="quick-quote-dialog" aria-labelledby="quick-quote-title"><div class="quick-dialog-head"><h2 id="quick-quote-title">Request a project quote</h2><button type="button" data-close-quick aria-label="Close quote request">Close</button></div>'+fast_quote_form('quick',product,reference,path,image[1] if image else '')+'<p><a class="textlink" href="'+esc(url,quote=True)+'">Full enquiry form &amp; artwork attachments ↗</a></p></dialog>'

def draft_controls():
 return '<div class="draft-controls"><label class="check"><input type="checkbox" id="save-enquiry-draft"><span>Keep a draft in this browser tab (optional)</span></label><button type="button" id="clear-enquiry-draft" class="textbutton">Clear saved draft</button><p id="draft-status" class="smallnote" role="status">Drafts are off. Files and consent are never saved.</p></div>'

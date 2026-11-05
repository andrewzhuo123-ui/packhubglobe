;(()=>{
// Public event data is restricted to event names and route paths.
globalThis.phgTrack=(event,properties={})=>{
 const data={event,page_path:location.pathname,...properties};
 document.dispatchEvent(new CustomEvent('packhubglobe:analytics',{detail:data}));
 // An installed analytics collector can consume this queue; no customer data is added.
 (globalThis.dataLayer??=[]).push(data);
};
const track=globalThis.phgTrack;
document.addEventListener('click',event=>{
 const link=event.target.closest('a');if(!link)return;
 if(link.pathname.startsWith('/assets/documents/')&&link.pathname.endsWith('.pdf'))track('documentation_open');
 if(link.pathname==='/request-quote/')track('quote_cta_click');
 if(link.closest('.ux-card,.productcard,.navpanel,.family-nav,.catalog-sidebar,.format')&&/^\/(products|catalog|industries)\//.test(link.pathname))track('category_select',{destination_path:link.pathname});
});
if(document.body.classList.contains('has-product-quote'))track('product_view');
const quoteForm=document.querySelector('#quote-form');
if(quoteForm){
 track('rfq_form_view');let started=false;
 quoteForm.addEventListener('focusout',event=>{const field=event.target;if(['name','email','company','product','quantity','country','size','material','whatsapp','timing','details'].includes(field.name)&&field.value)track('rfq_field_complete',{field_name:field.name})});
 quoteForm.addEventListener('input',()=>{if(!started){started=true;track('rfq_form_start')}});
 quoteForm.addEventListener('invalid',event=>{
  const input=event.target;
  let error=document.getElementById(input.id+'-error');
  if(!error){error=document.createElement('span');error.id=input.id+'-error';error.className='field-error';input.insertAdjacentElement('afterend',error);input.setAttribute('aria-describedby',[input.getAttribute('aria-describedby'),error.id].filter(Boolean).join(' '))}
  input.setAttribute('aria-invalid','true');error.textContent=input.validationMessage;
  track('rfq_form_error',{error_type:'validation'});
 },true);
 const clearError=event=>{const input=event.target;if(input.validity.valid){input.removeAttribute('aria-invalid');const error=document.getElementById(input.id+'-error');if(error)error.textContent=''}};
 quoteForm.addEventListener('input',clearError);quoteForm.addEventListener('change',clearError);
}
const navGroups=[...document.querySelectorAll('.navgroup')];
navGroups.forEach(group=>group.addEventListener('toggle',()=>{if(group.open)navGroups.forEach(other=>{if(other!==group)other.open=false})}));
document.addEventListener('click',event=>{if(!event.target.closest('.navlinks'))navGroups.forEach(group=>group.open=false)});
document.addEventListener('keydown',event=>{if(event.key==='Escape'){const active=navGroups.find(group=>group.open);navGroups.forEach(group=>group.open=false);active?.querySelector('summary').focus()}});
// Gallery controls retain full-size, crawlable image links without JavaScript.
document.querySelectorAll('.ux-thumbs a').forEach(link=>link.addEventListener('click',event=>{
 const main=link.closest('.detailhero').querySelector('.catalog-product-image img');
 if(main){event.preventDefault();main.src=link.getAttribute('href');main.alt=link.querySelector('img').alt;main.closest('a').href=link.getAttribute('href')}
}));

// Open a technical topic before following its on-page navigation link.
document.querySelectorAll('.tank-nav a').forEach(link=>link.addEventListener('click',()=>{const topic=document.querySelector(link.hash);const details=topic?.querySelector('.ux-technical-details');if(details)details.open=true}));
const linkedTopic=document.getElementById(location.hash.slice(1))?.querySelector('.ux-technical-details');if(linkedTopic)linkedTopic.open=true;

})();
;(()=>{
const menuButton=document.querySelector('.navbtn');
menuButton?.addEventListener('click',()=>{const open=menuButton.getAttribute('aria-expanded')!=='true';menuButton.setAttribute('aria-expanded',String(open));document.querySelector('.navlinks').classList.toggle('open',open)});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&menuButton?.getAttribute('aria-expanded')==='true'){menuButton.setAttribute('aria-expanded','false');document.querySelector('.navlinks').classList.remove('open');menuButton.focus()}});
const form=document.querySelector('#quote-form');
if(form){const params=new URLSearchParams(location.search);const product=params.get('product');if(product){const option=[...form.elements.product.options].find(o=>o.value===product);if(option)form.elements.product.value=product;else{form.elements.product.add(new Option(product,product,true,true))}}
if(form.elements.product_reference)form.elements.product_reference.value=product?.match(/\bPHG-[A-Za-z0-9-]+\b/)?.[0]||'';
if(form.elements.source_page&&/^\/(?:[A-Za-z0-9_-]+\/)*(?:index\.html|404\.html)?$/.test(params.get('source')||''))form.elements.source_page.value=params.get('source');
if(form.elements.source_page&&!form.elements.source_page.value&&document.referrer){try{const source=new URL(document.referrer);if(source.origin===location.origin&&source.pathname!==location.pathname)form.elements.source_page.value=source.pathname}catch{}}
const brief=()=>{const d=new FormData(form);return ['PACKHUBGLOBE — PACKAGING REQUEST',...['name','email','company','product','product_reference','quote_items','source_page','quantity','country','size','unit','material','whatsapp','timing','details'].map(k=>`${(k[0].toUpperCase()+k.slice(1)).replaceAll('_',' ')}: ${d.get(k)||'Not specified'}`),'','Please review format, material, artwork, sampling, MOQ and shipping options.'].join('\n')};
const attachments=document.querySelector('#attachments');
const validateAttachments=()=>{
 if(!attachments)return;
 const files=[...attachments.files];let message='';
 if(files.length>5)message='Please attach no more than 5 files.';
 else if(files.some(file=>!file.size||file.size>5*1024*1024))message='Each file must be non-empty and 5 MB or less.';
 else if(files.reduce((total,file)=>total+file.size,0)>10*1024*1024)message='Attachments must total 10 MB or less.';
 else if(files.some(file=>! /\.(jpe?g|png|webp|pdf|ai|psd|eps|zip)$/i.test(file.name)))message='Use JPG, PNG, WebP, PDF, AI, PSD, EPS or ZIP files.';
 attachments.setCustomValidity(message);
};
attachments?.addEventListener('change',()=>{validateAttachments();attachments.reportValidity()});
let sending=false;
form.addEventListener('submit',async e=>{
 e.preventDefault();validateAttachments();if(sending||!form.reportValidity())return;
 const button=form.querySelector('button[type="submit"]');const result=document.querySelector('#form-result');
 globalThis.phgTrack?.('rfq_form_submit');
 sending=true;button.disabled=true;button.textContent='Sending…';result.hidden=false;result.textContent='Sending your enquiry…';
 try{
  const response=await fetch('/request-quote/send.php',{method:'POST',body:new FormData(form),headers:{Accept:'application/json'}});
  const data=await response.json();
  if(!response.ok||data.ok!==true)throw new Error(data.message||'Your enquiry could not be sent. Please try again or email andrew@packhubglobe.com.');
  globalThis.phgTrack?.('rfq_form_success');
  if(attachments?.files.length)globalThis.phgTrack?.('file_upload_success',{file_count:attachments.files.length});
  result.textContent='Your enquiry and any attached files have been submitted for email delivery.';
 }catch(error){globalThis.phgTrack?.('rfq_form_error',{error_type:'submission'});result.textContent=(error instanceof SyntaxError||error.name==='TypeError')?'The enquiry service is unavailable. Please try again or email andrew@packhubglobe.com.':error.message||'Your enquiry could not be sent. Please try again or email andrew@packhubglobe.com.'}
 finally{sending=false;button.disabled=false;button.textContent='Send enquiry';result.scrollIntoView({block:'nearest',behavior:'smooth'})}
});
document.querySelector('#download-brief').addEventListener('click',()=>{if(!form.reportValidity())return;globalThis.phgTrack?.('rfq_brief_download');const blob=new Blob([brief()],{type:'text/plain;charset=utf-8'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='packhubglobe-packaging-brief.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)})}

document.querySelectorAll('.navlinks a').forEach(link=>link.addEventListener('click',()=>{menuButton?.setAttribute('aria-expanded','false');document.querySelector('.navlinks').classList.remove('open')}));

const heroVideo=document.querySelector('#hero-video');
if(heroVideo){
 const videoToggle=document.querySelector('#video-toggle');
 const videoMotion=matchMedia('(prefers-reduced-motion:reduce)');
 let resumeVideo=false;
 const startVideo=()=>{if(!heroVideo.getAttribute('src'))heroVideo.src=matchMedia('(max-width:600px)').matches?heroVideo.dataset.mobile:heroVideo.dataset.desktop;heroVideo.muted=true;heroVideo.play().catch(()=>{})};
 const updateVideoToggle=()=>{if(videoToggle)videoToggle.textContent=heroVideo.paused?'Play video':'Pause video'};
 if(videoToggle){videoToggle.hidden=false;videoToggle.addEventListener('click',()=>{if(heroVideo.paused)startVideo();else heroVideo.pause()})}
 heroVideo.addEventListener('play',updateVideoToggle);heroVideo.addEventListener('pause',updateVideoToggle);
 heroVideo.addEventListener('error',()=>{heroVideo.hidden=true;if(videoToggle)videoToggle.hidden=true});
 if(!videoMotion.matches&&!navigator.connection?.saveData)startVideo();
 videoMotion.addEventListener('change',()=>{if(videoMotion.matches){resumeVideo=false;heroVideo.pause()}});
 document.addEventListener('visibilitychange',()=>{if(document.hidden){resumeVideo=!heroVideo.paused;heroVideo.pause()}else if(resumeVideo){resumeVideo=false;startVideo()}});
 updateVideoToggle();
}

const catalogSearch=document.querySelector('#catalog-search');
if(catalogSearch){
 const browse=document.querySelector('.catalog-browse')||document.querySelector('.catalog-sidebar details');const mobileCatalog=matchMedia('(max-width:700px)');
 browse.open=!mobileCatalog.matches;mobileCatalog.addEventListener('change',event=>{browse.open=!event.matches});
 const scope=document.querySelector('[data-catalog-scope]')?.dataset.catalogScope||'all';
 const grid=document.querySelector('#catalog-grid');
 const original=grid.innerHTML;
 const formatFilter=document.querySelector('#format-filter');const materialFilter=document.querySelector('#material-filter');
 const industryFilter=document.querySelector('#industry-filter');
 const pagination=document.querySelector('.catalog-pages');
 const status=document.querySelector('#catalog-search-status');
 const listingCount=document.querySelector('.catalog-toolbar>p');
 let indexPromise;
 let searchTimer;let generation=0;
 const syncUrl=()=>{updateChips();const u=new URL(location.href);for(const [key,value] of [['q',catalogSearch.value.trim()],['structure',formatFilter?.value],['material',materialFilter?.value],['industry',industryFilter?.value]]){if(value)u.searchParams.set(key,value);else u.searchParams.delete(key)}if(u.href!==location.href)history.pushState(null,'',u)};
 const updateChips=()=>document.querySelectorAll('[data-structure-chip]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.structureChip===(formatFilter?.value||''))));
 const restore=()=>{const p=new URLSearchParams(location.search);catalogSearch.value=p.get('q')||'';for(const [filter,key] of [[formatFilter,'structure'],[materialFilter,'material'],[industryFilter,'industry']])if(filter)filter.value=p.get(key)||''};
 const clearSearch=(focus=true)=>{generation++;clearTimeout(searchTimer);catalogSearch.value='';if(formatFilter)formatFilter.value='';if(materialFilter)materialFilter.value='';if(industryFilter)industryFilter.value='';syncUrl();grid.innerHTML=original;if(pagination)pagination.hidden=false;listingCount.hidden=false;status.textContent='';if(focus)catalogSearch.focus()};
 const showResults=async()=>{const current=++generation;syncUrl();
  const query=catalogSearch.value.trim().toLowerCase();
  if(!query&&!formatFilter?.value&&!materialFilter?.value&&!industryFilter?.value){clearSearch(false);return}
  status.textContent='Searching the collection…';
  try{
   indexPromise??=globalThis.phgCatalogIndex??=fetch('/assets/catalog-index.json').then(response=>{if(!response.ok)throw new Error('Search unavailable');return response.json()}).catch(error=>{indexPromise=null;globalThis.phgCatalogIndex=null;throw error});
   const records=await indexPromise;
   if(current!==generation)return;
   const words=query.replace(/magnetic (closure|lid)/g,'magnetic').replace(/straight tuck end/g,'tuck').split(/\s+/);
   const synonyms={cartons:['carton','box'],carton:['carton','box'],boxes:['box'],bags:['bag'],labels:['label'],stickers:['sticker'],jewellery:['jewellery','jewelry'],jewelry:['jewelry','jewellery'],fashion:['apparel','garment'],apparel:['apparel','garment'],kraft:['kraft'],corrugated:['corrugated','mailer','shipping']};
   const applicationTerms={'Cosmetics & beauty':/cosmetic|beauty|skincare|serum|perfume|lipstick|soap/i,'Apparel & fashion':/apparel|garment|clothing|underwear|sock/i,'Food & beverage':/food|snack|coffee|tea|chocolate|bakery|sushi|beverage/i,'Jewelry & gifts':/jewel|gift|watch/i,'Electronics':/electronic|headphone|phone|charger/i};
   const matches=records.filter(record=>(scope==='all'||scope==='family:'+record.family||scope.startsWith('group:')&&record.groups.includes(scope.slice(6)))&&words.every(word=>(synonyms[word]||[word]).some(term=>(record.name+' '+record.reference+' '+record.groups.join(' ')+' '+record.searchText).toLowerCase().includes(term)))&&(!industryFilter?.value||applicationTerms[industryFilter.value]?.test(record.name+' '+record.searchText+' '+record.groups.join(' ')))&&(!formatFilter?.value||record.format===formatFilter.value)&&(!materialFilter?.value||record.facts.some(([key,value])=>/material|film/i.test(key)&&new RegExp('\\b'+materialFilter.value+'\\b','i').test(value))));
   grid.replaceChildren();
   for(const record of matches.slice(0,48)){
    const card=document.createElement('article');card.className='catalog-card compact-card';
    const photo=document.createElement('a');photo.className='catalog-photo';photo.href=record.path;
    const image=document.createElement('img');image.src=record.image;if(record.srcset){image.srcset=record.srcset;image.sizes='(max-width:600px) 44vw, (max-width:1100px) 30vw, 360px'}image.alt=record.name;image.width=record.imageWidth||1000;image.height=record.imageHeight||1000;image.loading='lazy';photo.append(image);
    const copy=document.createElement('div');copy.className='catalog-copy';
    const group=document.createElement('p');group.className='eyebrow';group.textContent=record.groups[0];
    const heading=document.createElement('h3');const link=document.createElement('a');link.href=record.path;link.textContent=record.name;heading.append(link);
    const minimum=document.createElement('p');minimum.className='compact-moq';minimum.textContent='From 500 pieces';
    const reference=document.createElement('p');reference.className='catalog-ref';reference.textContent=record.reference;
    const details=document.createElement('a');details.className='textlink';details.href=record.path;details.textContent='View details ↗';
    const add=document.createElement('button');add.type='button';add.className='quote-add';add.dataset.quoteRef=record.reference;add.setAttribute('aria-label','Add '+record.name+' '+record.reference+' to quote basket');add.setAttribute('aria-pressed','false');add.textContent='+ Quote';
    if(record.gallery?.length){const alternate=image.cloneNode();alternate.src=record.gallery[0];alternate.removeAttribute('srcset');alternate.className='catalog-alt';alternate.alt=record.name+' · alternate reference view';photo.append(alternate)}
    copy.append(group,heading,reference,minimum,details,add);card.append(photo,copy);grid.append(card);
   }
   if(!matches.length){const empty=document.createElement('div');empty.className='catalog-empty';const message=document.createElement('p');message.textContent='Need a different structure? Share a photo or artwork and your requirements.';const a=document.createElement('a');a.href='/request-quote/';a.textContent='Discuss a custom packaging project and attach a reference ↗';empty.append(message,a);grid.append(empty)}
   const suggestions=document.querySelector('#catalog-suggestions');if(query&&suggestions){suggestions.replaceChildren(...matches.slice(0,6).map(r=>new Option(r.name+' · '+r.reference,r.reference)))}
   if(pagination)pagination.hidden=true;listingCount.hidden=true;
   status.textContent=matches.length?`${matches.length} matching products${scope==='all'?' across all products':' in this category'}${matches.length>48?' · Showing the first 48; add another word to narrow your search.':'.'}`:'No matching products. Try a material, format or product reference.';
  }catch{if(catalogSearch.value.trim().toLowerCase()===query)status.textContent='Search is temporarily unavailable. Please use the packaging categories.'}
 };
 document.querySelector('.catalog-search').hidden=false;
 const filters=document.querySelector('.ux-filters');if(filters)filters.hidden=false;
 catalogSearch.addEventListener('input',()=>{clearTimeout(searchTimer);searchTimer=setTimeout(showResults,180)});
 document.querySelector('#catalog-clear').addEventListener('click',()=>clearSearch());
 [formatFilter,materialFilter,industryFilter].forEach(filter=>filter?.addEventListener('change',showResults));
 const popular=document.createElement('div');popular.className='catalog-popular';popular.setAttribute('aria-label','Popular packaging searches');for(const term of ['Corrugated mailer','Magnetic box','Stand-up pouch','Drawer box']){const b=document.createElement('button');b.type='button';b.textContent=term;b.onclick=()=>{catalogSearch.value=term;showResults()};popular.append(b)}filters?.after(popular);
 if(formatFilter){const chips=document.createElement('div');chips.className='catalog-popular';chips.setAttribute('aria-label','Quick structure filters');for(const [value,label] of [['','All structures'],['mailer','Corrugated mailers'],['rigid','Rigid gift boxes'],['carton','Folding cartons'],['stand-up','Stand-up pouches'],['paper-bag','Paper bags']]){if(value&&![...formatFilter.options].some(o=>o.value===value))continue;const b=document.createElement('button');b.type='button';b.dataset.structureChip=value;b.textContent=label;b.onclick=()=>{formatFilter.value=value;showResults()};chips.append(b)}filters.before(chips);updateChips()}
 window.addEventListener('popstate',()=>{restore();showResults()});restore();if(location.search)showResults();
}

})();
;(()=>{
// Persist only public product reference IDs; contact details stay in the form.
(()=>{
 const key='phg-quote-basket';let selected=[];let records;
 try{selected=JSON.parse(localStorage.getItem(key)||'[]');if(!Array.isArray(selected))selected=[];selected=[...new Set(selected.filter(v=>typeof v==='string'&&/^PHG-[A-Za-z0-9-]+$/.test(v)))].slice(0,50)}catch{}
 const load=()=>records??=globalThis.phgCatalogIndex??=fetch('/assets/catalog-index.json').then(r=>{if(!r.ok)throw Error('Catalog unavailable');return r.json()}).catch(e=>{records=null;globalThis.phgCatalogIndex=null;throw e});
 const bar=document.createElement('div');bar.className='quote-basket-bar';bar.hidden=true;
 const count=document.createElement('span');count.setAttribute('role','status');
 const review=document.createElement('button');review.type='button';review.textContent='Review quote basket';bar.append(count,review);document.body.append(bar);
 const dialog=document.createElement('dialog');dialog.className='quote-basket';dialog.setAttribute('aria-labelledby','basket-title');
 dialog.innerHTML='<header><h2 id="basket-title">Your packaging quote basket</h2><button type="button" data-close>Close</button></header><p>Select up to 50 references. Specify quantities and dimensions per item in the enquiry form. MOQ starts at 500 pieces per design.</p><ul></ul><p class="basket-status" role="status"></p><div class="actions"><a class="button" href="/request-quote/?basket=1">Continue to enquiry</a><button type="button" data-clear>Clear basket</button></div>';
 document.body.append(dialog);
 const update=()=>{bar.hidden=!selected.length;count.textContent=`${selected.length} reference${selected.length===1?'':'s'} selected`;document.querySelectorAll('[data-quote-ref]').forEach(b=>{const active=selected.includes(b.dataset.quoteRef);b.setAttribute('aria-pressed',String(active));b.textContent=active?'✓ In quote basket':'+ Quote'})};
 const save=()=>{try{localStorage.setItem(key,JSON.stringify(selected))}catch{dialog.querySelector('.basket-status').textContent='Browser storage is unavailable. Keep this tab open to preserve your selection.'}update()};
 const draw=async()=>{const list=dialog.querySelector('ul');list.replaceChildren();try{const data=await load();for(const ref of selected){const r=data.find(v=>v.reference===ref);if(!r)continue;const li=document.createElement('li');const img=document.createElement('img');img.src=r.image;img.alt='';img.width=64;img.height=64;const a=document.createElement('a');a.href=r.path;a.textContent=r.name;const small=document.createElement('small');small.textContent=ref;a.append(small);const remove=document.createElement('button');remove.type='button';remove.textContent='Remove';remove.setAttribute('aria-label','Remove '+ref);remove.onclick=()=>{selected=selected.filter(v=>v!==ref);save();draw();syncForm()};li.append(img,a,remove);list.append(li)}if(!selected.length)list.textContent='Your quote basket is empty.';dialog.querySelector('a.button').hidden=!selected.length}catch{dialog.querySelector('.basket-status').textContent='Could not load the references. Please try again.'}};
 review.onclick=()=>{dialog.showModal();draw()};dialog.querySelector('[data-close]').onclick=()=>dialog.close();dialog.querySelector('[data-clear]').onclick=()=>{selected=[];save();draw();syncForm()};
 document.addEventListener('click',e=>{const b=e.target.closest('[data-quote-ref]');if(!b)return;const ref=b.dataset.quoteRef;if(selected.includes(ref))selected=selected.filter(v=>v!==ref);else if(selected.length<50)selected.push(ref);else{dialog.showModal();dialog.querySelector('.basket-status').textContent='The basket holds up to 50 references. Remove an item to add another.';return}save();globalThis.phgTrack?.('quote_basket_update',{item_count:selected.length})});
 const form=document.querySelector('#quote-form');let hidden,summary;
 if(form){hidden=document.createElement('input');hidden.type='hidden';hidden.name='quote_items';form.append(hidden);summary=document.createElement('section');summary.className='quote-summary';summary.hidden=true;form.prepend(summary)}
 async function syncForm(){if(!form)return;hidden.value=selected.join('\n');summary.replaceChildren();summary.hidden=!selected.length;if(!selected.length)return;const heading=document.createElement('h2');heading.textContent='Selected packaging references';const list=document.createElement('ul');summary.append(heading,list);try{const data=await load();const items=data.filter(r=>selected.includes(r.reference));hidden.value=items.map(r=>`${r.reference} | ${r.name} | https://www.packhubglobe.com${r.path}`).join('\n');for(const r of items){const li=document.createElement('li');li.textContent=`${r.name} · ${r.reference}`;list.append(li)}const edit=document.createElement('button');edit.type='button';edit.className='quote-add';edit.textContent='Edit quote basket';edit.onclick=()=>{dialog.showModal();draw()};summary.append(edit);if(new URLSearchParams(location.search).has('basket')&&!form.elements.product.value){form.elements.product.add(new Option('Multi-item packaging enquiry','Multi-item packaging enquiry',true,true))}}catch{hidden.value=selected.join('\n');list.textContent=selected.join(', ')}}
 new MutationObserver(events=>{if(events.some(e=>[...e.addedNodes].some(n=>n.nodeType===1&&(n.matches('.catalog-card')||n.querySelector('.catalog-card')))))update()}).observe(document.querySelector('#catalog-grid')||document.createElement('div'),{childList:true,subtree:true});update();syncForm();
 window.addEventListener('storage',e=>{if(e.key===key){try{const values=JSON.parse(e.newValue||'[]');if(Array.isArray(values))selected=values.filter(v=>typeof v==='string'&&/^PHG-[A-Za-z0-9-]+$/.test(v)).slice(0,50)}catch{}update();syncForm()}});
 // Add only existing alternate views; never imply that a reference image is a dieline.
 if(document.querySelector('#catalog-grid'))load().then(data=>{document.querySelectorAll('.catalog-card').forEach(card=>{const photo=card.querySelector('.catalog-photo');const r=data.find(v=>v.path===photo?.getAttribute('href'));if(r?.gallery?.length){const image=document.createElement('img');image.className='catalog-alt';image.src=r.gallery[0];image.alt=r.name+' · alternate reference view';image.width=r.imageWidth;image.height=r.imageHeight;image.loading='lazy';photo.append(image)}})}).catch(()=>{});
})();

})();
;(()=>{
(()=>{
 const track=(name,form,extra={})=>globalThis.phgTrack?.(name,{form_location:form?.closest('dialog')?'product_drawer':'homepage',...extra});
 const drawer=document.querySelector('#quick-quote-dialog');
 if(drawer){
  drawer.querySelector('[data-close-quick]').onclick=()=>drawer.close();
  document.addEventListener('click',event=>{const a=event.target.closest('a[href^="/request-quote/?product="]');if(!a||event.button!==0||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey||!a.closest('.detailhero,.ux-mobile-quote,.cta'))return;event.preventDefault();drawer.showModal();track('rfq_drawer_open',drawer.querySelector('form'));track('rfq_form_view',drawer.querySelector('form'))});
  drawer.addEventListener('close',()=>track('rfq_drawer_close',drawer.querySelector('form')));
 }
 document.querySelectorAll('[data-fast-quote]').forEach(form=>{
  if(!form.closest('dialog')){const observer=new IntersectionObserver(entries=>{if(entries.some(entry=>entry.isIntersecting)){track('rfq_form_view',form);observer.disconnect()}},{threshold:0.2});observer.observe(form)}
  form.addEventListener('focusout',event=>{const field=event.target;if(['product','quantity','email','details'].includes(field.name)&&field.value)track('rfq_field_complete',form,{field_name:field.name})});
  let started=false;form.addEventListener('input',()=>{if(!started){started=true;track('rfq_form_start',form)}});
  form.addEventListener('invalid',()=>track('rfq_form_error',form,{error_type:'validation'}),true);
  form.addEventListener('submit',async event=>{
   event.preventDefault();const button=form.querySelector('[type=submit]');if(button.disabled||!form.reportValidity())return;
   const data=new FormData(form);if(!String(data.get('details')||'').trim())data.set('details','Initial packaging enquiry. Please review the selected packaging type and quantity with me. Dimensions, materials, artwork and delivery requirements are to be confirmed.');
   const status=form.querySelector('[role=status]');button.disabled=true;status.hidden=false;status.textContent='Sending your enquiry…';track('rfq_form_submit',form);
   try{const response=await fetch(form.action,{method:'POST',body:data,headers:{Accept:'application/json'}});const result=await response.json();if(!response.ok||result.ok!==true)throw Error(result.message||'The enquiry could not be submitted.');status.textContent='Your enquiry has been submitted for email delivery. You can add further specifications through the full enquiry form.';track('rfq_form_success',form)}
   catch(error){status.textContent=(error.name==='SyntaxError'||error.name==='TypeError'?'The enquiry service is unavailable.':error.message)+' Your input has been kept. Retry or email andrew@packhubglobe.com.';track('rfq_form_error',form,{error_type:'submission'})}
   finally{button.disabled=false}
  });
 });
 const form=document.querySelector('#quote-form');const save=document.querySelector('#save-enquiry-draft');
 if(form&&save){
  const key='phg-enquiry-tab-draft';const fields=['name','email','company','product','quantity','country','size','unit','material','whatsapp','timing','details'];const status=document.querySelector('#draft-status');
  const clear=()=>{try{sessionStorage.removeItem(key)}catch{}save.checked=false;status.textContent='Saved draft cleared. Your current form input is unchanged.'};
  const store=()=>{if(!save.checked)return;try{sessionStorage.setItem(key,JSON.stringify({fields:Object.fromEntries(fields.map(k=>[k,form.elements[k]?.value||''])),product_reference:form.elements.product_reference.value,source_page:form.elements.source_page.value}));status.textContent='Draft saved in this tab until you clear it or close the tab. Files and consent are not saved.'}catch{save.checked=false;status.textContent='Draft storage is unavailable. Keep this page open or download your brief.'}};
  try{const draft=JSON.parse(sessionStorage.getItem(key)||'null');if(draft?.fields){const current=form.elements.product.value;const compatible=!current||current===draft.fields.product;if(compatible){for(const k of fields){const input=form.elements[k];if(!input||typeof draft.fields[k]!=='string')continue;if(input.tagName==='SELECT'&&![...input.options].some(o=>o.value===draft.fields[k]))input.add(new Option(draft.fields[k],draft.fields[k]));input.value=draft.fields[k]}for(const k of ['product_reference','source_page'])if(typeof draft[k]==='string')form.elements[k].value=draft[k];save.checked=true;status.textContent='Your draft was restored. Reattach any files and confirm consent before submitting.'}else status.textContent='A draft for another product remains saved in this tab. This product’s context has been kept.'}}catch{}
  save.onchange=()=>save.checked?store():clear();form.addEventListener('input',store);form.addEventListener('change',store);document.querySelector('#clear-enquiry-draft').onclick=clear;
  document.addEventListener('packhubglobe:analytics',event=>{if(event.detail.event==='rfq_form_success'&&!event.detail.form_location)clear()});
 }
 // Prefetch only HTML for deliberate navigation; no prerendered forms or tracking.
 if(HTMLScriptElement.supports?.('speculationrules')&&!navigator.connection?.saveData&&!['slow-2g','2g'].includes(navigator.connection?.effectiveType)){
  const script=document.createElement('script');script.type='speculationrules';script.textContent=JSON.stringify({prefetch:[{source:'document',where:{and:[{href_matches:'/*'},{selector_matches:'.navpanel a, .catalog-photo, .ux-photo'},{not:{href_matches:'/*\\?*'}},{not:{href_matches:'/assets/*'}}]},eagerness:'conservative'}]});document.head.append(script);
 }
})();

})();
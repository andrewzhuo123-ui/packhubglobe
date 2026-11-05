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

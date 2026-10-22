const menuButton=document.querySelector('.navbtn');
menuButton?.addEventListener('click',()=>{const open=menuButton.getAttribute('aria-expanded')!=='true';menuButton.setAttribute('aria-expanded',String(open));document.querySelector('.navlinks').classList.toggle('open',open)});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&menuButton?.getAttribute('aria-expanded')==='true'){menuButton.setAttribute('aria-expanded','false');document.querySelector('.navlinks').classList.remove('open');menuButton.focus()}});
const form=document.querySelector('#quote-form');
if(form){const params=new URLSearchParams(location.search);const product=params.get('product');if(product){const option=[...form.elements.product.options].find(o=>o.value===product);if(option)form.elements.product.value=product;else{form.elements.product.add(new Option(product,product,true,true));form.elements.details.value=`Interested in: ${product}\n`}}
const brief=()=>{const d=new FormData(form);return ['PACKHUBGLOBE — PACKAGING REQUEST',...['name','email','company','product','quantity','country','size','unit','timing','details'].map(k=>`${k[0].toUpperCase()+k.slice(1)}: ${d.get(k)||'Not specified'}`),'','Please review format, material, artwork, sampling, MOQ and shipping options.'].join('\n')};
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
 sending=true;button.disabled=true;button.textContent='Sending…';result.hidden=false;result.textContent='Sending your enquiry…';
 try{
  const response=await fetch('/request-quote/send.php',{method:'POST',body:new FormData(form),headers:{Accept:'application/json'}});
  const data=await response.json();
  if(!response.ok||data.ok!==true)throw new Error(data.message||'Your enquiry could not be sent. Please try again or email andrew@packhubglobe.com.');
  result.textContent='Your enquiry and any attached files have been submitted for email delivery.';
 }catch(error){result.textContent=(error instanceof SyntaxError||error.name==='TypeError')?'The enquiry service is unavailable. Please try again or email andrew@packhubglobe.com.':error.message||'Your enquiry could not be sent. Please try again or email andrew@packhubglobe.com.'}
 finally{sending=false;button.disabled=false;button.textContent='Send enquiry';result.scrollIntoView({block:'nearest',behavior:'smooth'})}
});
document.querySelector('#download-brief').addEventListener('click',()=>{if(!form.reportValidity())return;const blob=new Blob([brief()],{type:'text/plain;charset=utf-8'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='packhubglobe-packaging-brief.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)})}

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
 const pagination=document.querySelector('.catalog-pages');
 const status=document.querySelector('#catalog-search-status');
 const listingCount=document.querySelector('.catalog-toolbar>p');
 let indexPromise;
 let searchTimer;
 const clearSearch=()=>{clearTimeout(searchTimer);catalogSearch.value='';grid.innerHTML=original;if(pagination)pagination.hidden=false;listingCount.hidden=false;status.textContent='';catalogSearch.focus()};
 const showResults=async()=>{
  const query=catalogSearch.value.trim().toLowerCase();
  if(!query){clearSearch();return}
  status.textContent='Searching the collection…';
  try{
   indexPromise??=fetch('/assets/catalog-index.json').then(response=>{if(!response.ok)throw new Error('Search unavailable');return response.json()}).catch(error=>{indexPromise=null;throw error});
   const records=await indexPromise;
   if(catalogSearch.value.trim().toLowerCase()!==query)return;
   const words=query.split(/\s+/);
   const matches=records.filter(record=>(scope==='all'||scope==='family:'+record.family||scope.startsWith('group:')&&record.groups.includes(scope.slice(6)))&&words.every(word=>(record.name+' '+record.reference+' '+record.groups.join(' ')+' '+record.searchText).toLowerCase().includes(word)));
   grid.replaceChildren();
   for(const record of matches.slice(0,48)){
    const card=document.createElement('article');card.className='catalog-card compact-card';
    const photo=document.createElement('a');photo.className='catalog-photo';photo.href=record.path;
    const image=document.createElement('img');image.src=record.image;image.alt=record.name;image.width=1000;image.height=1000;image.loading='lazy';photo.append(image);
    const copy=document.createElement('div');copy.className='catalog-copy';
    const group=document.createElement('p');group.className='eyebrow';group.textContent=record.groups[0];
    const heading=document.createElement('h2');const link=document.createElement('a');link.href=record.path;link.textContent=record.name;heading.append(link);
    const minimum=document.createElement('p');minimum.className='compact-moq';minimum.textContent='From 500 pieces';
    const reference=document.createElement('p');reference.className='catalog-ref';reference.textContent=record.reference;
    const details=document.createElement('a');details.className='textlink';details.href=record.path;details.textContent='View details ↗';
    copy.append(group,heading,reference,minimum,details);card.append(photo,copy);grid.append(card);
   }
   if(pagination)pagination.hidden=true;listingCount.hidden=true;
   status.textContent=matches.length?`${matches.length} matching products${scope==='all'?' across all products':' in this category'}${matches.length>48?' · Showing the first 48; add another word to narrow your search.':'.'}`:'No matching products. Try a material, format or product reference.';
  }catch{if(catalogSearch.value.trim().toLowerCase()===query)status.textContent='Search is temporarily unavailable. Please use the packaging categories.'}
 };
 document.querySelector('.catalog-search').hidden=false;
 catalogSearch.addEventListener('input',()=>{clearTimeout(searchTimer);searchTimer=setTimeout(showResults,180)});
 document.querySelector('#catalog-clear').addEventListener('click',clearSearch);
}

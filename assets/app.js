const menuButton=document.querySelector('.navbtn');
menuButton?.addEventListener('click',()=>{const open=menuButton.getAttribute('aria-expanded')!=='true';menuButton.setAttribute('aria-expanded',String(open));document.querySelector('.navlinks').classList.toggle('open',open)});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&menuButton?.getAttribute('aria-expanded')==='true'){menuButton.setAttribute('aria-expanded','false');document.querySelector('.navlinks').classList.remove('open');menuButton.focus()}});
const form=document.querySelector('#quote-form');
if(form){const params=new URLSearchParams(location.search);const product=params.get('product');if(product){const option=[...form.elements.product.options].find(o=>o.value===product);if(option)form.elements.product.value=product;else{form.elements.product.add(new Option(product,product,true,true));form.elements.details.value=`Interested in: ${product}\n`}}
const brief=()=>{const d=new FormData(form);return ['PACKHUBGLOBE — PACKAGING REQUEST',...['name','email','company','product','quantity','country','size','unit','timing','details'].map(k=>`${k[0].toUpperCase()+k.slice(1)}: ${d.get(k)||'Not specified'}`),'','Please review format, material, artwork, sampling, MOQ and shipping options.'].join('\n')};
form.addEventListener('submit',e=>{e.preventDefault();if(!form.reportValidity())return;const subject=`Packaging enquiry — ${form.elements.product.value}`;const link=document.querySelector('#email-draft');link.href=`mailto:andrew@packhubglobe.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(brief())}`;document.querySelector('#form-result').hidden=false;document.querySelector('#form-result').scrollIntoView({block:'nearest',behavior:'smooth'});link.focus()});
document.querySelector('#download-brief').addEventListener('click',()=>{if(!form.reportValidity())return;const blob=new Blob([brief()],{type:'text/plain;charset=utf-8'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='packhubglobe-packaging-brief.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)})}

document.querySelectorAll('.navlinks a').forEach(link=>link.addEventListener('click',()=>{menuButton?.setAttribute('aria-expanded','false');document.querySelector('.navlinks').classList.remove('open')}));

const heroVideo=document.querySelector('#hero-video');
if(heroVideo){
 const startVideo=()=>{if(!heroVideo.getAttribute('src'))heroVideo.src=matchMedia('(max-width:600px)').matches?heroVideo.dataset.mobile:heroVideo.dataset.desktop;heroVideo.muted=true;heroVideo.play().catch(()=>{})};
 heroVideo.addEventListener('error',()=>{heroVideo.hidden=true});
 if(!matchMedia('(prefers-reduced-motion:reduce)').matches&&!navigator.connection?.saveData)startVideo();
 document.addEventListener('visibilitychange',()=>{if(document.hidden)heroVideo.pause()});
}

const catalogSearch=document.querySelector('#catalog-search');
if(catalogSearch){
 const sidebar=document.querySelector('.catalog-sidebar details');const desktopOpen=sidebar.open;const smallCatalog=matchMedia('(max-width:700px)');
 if(smallCatalog.matches)sidebar.open=false;
 smallCatalog.addEventListener('change',event=>{sidebar.open=event.matches?false:desktopOpen});
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
   const matches=records.filter(record=>words.every(word=>(record.name+' '+record.reference+' '+record.groups.join(' ')+' '+record.searchText).toLowerCase().includes(word)));
   grid.replaceChildren();
   for(const record of matches.slice(0,48)){
    const card=document.createElement('article');card.className='catalog-card';
    const photo=document.createElement('a');photo.className='catalog-photo';photo.href=record.path;
    const image=document.createElement('img');image.src=record.image;image.alt=record.name;image.width=1000;image.height=1000;image.loading='lazy';photo.append(image);
    const copy=document.createElement('div');copy.className='catalog-copy';
    const group=document.createElement('p');group.className='eyebrow';group.textContent=record.groups[0];
    const heading=document.createElement('h2');const link=document.createElement('a');link.href=record.path;link.textContent=record.name;heading.append(link);
    const facts=document.createElement('dl');facts.className='catalog-facts';for(const [label,value] of record.facts){const row=document.createElement('div');if(label==='MOQ')row.className='moq-fact';const dt=document.createElement('dt');dt.textContent=label;const dd=document.createElement('dd');dd.textContent=value.length>95?value.slice(0,95)+'…':value;row.append(dt,dd);facts.append(row)}
    const reference=document.createElement('p');reference.className='catalog-ref';reference.textContent=record.reference;
    const actions=document.createElement('div');actions.className='catalog-actions';
    const details=document.createElement('a');details.className='textlink';details.href=record.path;details.textContent='View details ↗';
    const quote=document.createElement('a');quote.className='button';quote.href='/request-quote/?product='+encodeURIComponent(record.name+' · '+record.reference);quote.textContent='Get a quote';
    const chat=document.createElement('a');chat.className='button chat-now';chat.href=record.chat;chat.target='_blank';chat.rel='noopener noreferrer';chat.textContent='Chat now · WhatsApp';
    actions.append(details,quote,chat);copy.append(group,heading,facts,reference,actions);card.append(photo,copy);grid.append(card);
   }
   if(pagination)pagination.hidden=true;listingCount.hidden=true;
   status.textContent=matches.length?`${matches.length} matching products across the collection${matches.length>48?' · Showing the first 48; add another word to narrow your search.':'.'}`:'No matching products. Try a material, format or product reference.';
  }catch{if(catalogSearch.value.trim().toLowerCase()===query)status.textContent='Search is temporarily unavailable. Please use the packaging categories.'}
 };
 document.querySelector('.catalog-search').hidden=false;
 catalogSearch.addEventListener('input',()=>{clearTimeout(searchTimer);searchTimer=setTimeout(showResults,180)});
 document.querySelector('#catalog-clear').addEventListener('click',clearSearch);
}

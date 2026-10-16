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
const videoToggle=document.querySelector('#video-toggle');
if(heroVideo&&videoToggle){
 const updateVideoState=()=>{videoToggle.textContent=heroVideo.paused?'Play video':'Pause video';videoToggle.setAttribute('aria-label',heroVideo.paused?'Play factory video':'Pause factory video')};
 const startVideo=()=>{if(!heroVideo.getAttribute('src'))heroVideo.src=matchMedia('(max-width:600px)').matches?heroVideo.dataset.mobile:heroVideo.dataset.desktop;heroVideo.muted=true;heroVideo.play().catch(updateVideoState)};
 heroVideo.addEventListener('play',updateVideoState);
 heroVideo.addEventListener('pause',updateVideoState);
 heroVideo.addEventListener('error',()=>{heroVideo.hidden=true;videoToggle.hidden=true});
 videoToggle.addEventListener('click',()=>{if(heroVideo.paused)startVideo();else heroVideo.pause()});
 if(!matchMedia('(prefers-reduced-motion:reduce)').matches&&!navigator.connection?.saveData)startVideo();
 document.addEventListener('visibilitychange',()=>{if(document.hidden)heroVideo.pause()});
}

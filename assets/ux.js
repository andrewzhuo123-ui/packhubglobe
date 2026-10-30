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
 if(link.pathname==='/request-quote/')track('quote_cta_click');
 if(link.closest('.ux-card,.productcard,.navpanel,.family-nav,.catalog-sidebar,.format')&&/^\/(products|catalog|industries)\//.test(link.pathname))track('category_select',{destination_path:link.pathname});
});
if(document.body.classList.contains('has-product-quote'))track('product_view');
const quoteForm=document.querySelector('#quote-form');
if(quoteForm){
 track('rfq_form_view');let started=false;
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

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

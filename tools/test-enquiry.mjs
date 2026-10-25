// Run the actual browser submit handler with controlled server responses.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const source=readFileSync('assets/app.js','utf8');
for(const [referrer,expected] of [
 ['https://www.packhubglobe.com/catalog/example/?email=private@example.com','/catalog/example/'],
 ['https://example.com/private',''],
 ['', ''],
 ['https://www.packhubglobe.com/request-quote/?product=old','']
]){
 const elements={product:{options:[{value:'Custom Box · PHG-123'}],value:''},details:{value:''},source_page:{value:''},product_reference:{value:''}};
 const form={elements,addEventListener(){}};
 const document={referrer,querySelector:s=>s==='#quote-form'?form:s==='#download-brief'?{addEventListener(){}}:null,querySelectorAll:()=>[],addEventListener(){}};
 vm.runInNewContext(source,{document,location:{origin:'https://www.packhubglobe.com',pathname:'/request-quote/',search:'?product=Custom%20Box%20%C2%B7%20PHG-123'},URLSearchParams,URL});
 assert.equal(elements.source_page.value,expected);
 assert.equal(elements.product_reference.value,'PHG-123');
 assert.equal(elements.product.value,'Custom Box · PHG-123');
}
console.log('PASS context capture, query stripping, foreign and absent referrers');
for(const scenario of ['success','legacy form','failure','html','network','too many','large file','total size','bad extension']){
 const success=['success','legacy form'].includes(scenario);
 const result={hidden:true,textContent:'',scrollIntoView(){}};
 const button={disabled:false,textContent:'Send enquiry'};
 const input={value:'Keep this project'};
 const file={name:'sample.png',size:100};
 const attachments={files:[file,{name:'artwork.pdf',size:100}],validity:'',setCustomValidity(value){this.validity=value},addEventListener(){},reportValidity(){}};
 if(scenario==='too many')attachments.files=Array(6).fill(file);
 if(scenario==='large file')attachments.files=[{...file,size:5*1024*1024+1}];
 if(scenario==='total size')attachments.files=Array(3).fill({...file,size:4*1024*1024});
 if(scenario==='bad extension')attachments.files=[{...file,name:'script.php'}];
 let submit,finish,calls=0;
 const form={elements:{product:{options:[]},details:input,source_page:{value:''},product_reference:{value:''}},reportValidity:()=>!attachments.validity,querySelector:()=>button,addEventListener:(_,handler)=>{submit=handler}};
 if(scenario==='legacy form'){delete form.elements.source_page;delete form.elements.product_reference}
 const document={querySelector:selector=>({'#quote-form':form,'#attachments':attachments,'#form-result':result,'#download-brief':{addEventListener(){}}}[selector]??null),querySelectorAll:()=>[],addEventListener(){}};
 const fetch=()=>{calls++;return new Promise((resolve,reject)=>{finish=()=>{
  if(scenario==='network')return reject(new TypeError('Failed to fetch'));
  resolve({ok:success,json:async()=>{if(scenario==='html')throw new SyntaxError();return {ok:success,message:'Transport unavailable'}}});
 }})};
 vm.runInNewContext(source,{document,location:{search:''},URLSearchParams,FormData:class{},fetch,Error,SyntaxError});
 const pending=submit({preventDefault(){}});
 if(['too many','large file','total size','bad extension'].includes(scenario)){await pending;assert.equal(calls,0);assert.ok(attachments.validity);console.log('PASS',scenario);continue}
 assert.equal(button.disabled,true);
 await submit({preventDefault(){}});
 assert.equal(calls,1,'duplicate submit must be blocked');
 finish();await pending;
 assert.equal(button.disabled,false);
 assert.equal(input.value,'Keep this project');
 assert.equal(result.hidden,false);
 if(success)assert.match(result.textContent,/submitted for email delivery/);
 else assert.doesNotMatch(result.textContent,/submitted for email delivery/);
 console.log('PASS',scenario);
}

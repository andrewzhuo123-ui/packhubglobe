// Run the actual browser submit handler with controlled server responses.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const source=readFileSync('assets/app.js','utf8');
for(const scenario of ['success','failure','html','network']){
 const result={hidden:true,textContent:'',scrollIntoView(){}};
 const button={disabled:false,textContent:'Send enquiry'};
 const input={value:'Keep this project'};
 let submit,finish,calls=0;
 const form={elements:{product:{options:[]},details:input},reportValidity:()=>true,querySelector:()=>button,addEventListener:(_,handler)=>{submit=handler}};
 const document={querySelector:selector=>({'#quote-form':form,'#form-result':result,'#download-brief':{addEventListener(){}}}[selector]??null),querySelectorAll:()=>[],addEventListener(){}};
 const fetch=()=>{calls++;return new Promise((resolve,reject)=>{finish=()=>{
  if(scenario==='network')return reject(new TypeError('Failed to fetch'));
  resolve({ok:scenario==='success',json:async()=>{if(scenario==='html')throw new SyntaxError();return {ok:scenario==='success',message:'Transport unavailable'}}});
 }})};
 vm.runInNewContext(source,{document,location:{search:''},URLSearchParams,FormData:class{},fetch,Error,SyntaxError});
 const pending=submit({preventDefault(){}});
 assert.equal(button.disabled,true);
 await submit({preventDefault(){}});
 assert.equal(calls,1,'duplicate submit must be blocked');
 finish();await pending;
 assert.equal(button.disabled,false);
 assert.equal(input.value,'Keep this project');
 assert.equal(result.hidden,false);
 if(scenario==='success')assert.match(result.textContent,/submitted for email delivery/);
 else assert.doesNotMatch(result.textContent,/submitted for email delivery/);
 console.log('PASS',scenario);
}

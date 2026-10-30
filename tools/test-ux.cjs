// Browser acceptance: PLAYWRIGHT_MODULE points to an installed Playwright package.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const {default:AxeBuilder}=require(process.env.AXE_MODULE||'@axe-core/playwright');
const origin=process.env.TEST_ORIGIN||'http://127.0.0.1:4174';
const records=JSON.parse(fs.readFileSync('assets/catalog-index.json','utf8'));
const product=records.find(r=>r.reference==='PHG-FP-1600192691645');
const widths=[360,390,428,768,1024,1440];
const routes=['/','/products/','/products/custom-boxes/','/products/custom-boxes/magnetic-gift-boxes/',product.path,'/catalog/','/industries/apparel/','/materials/printing-finishes/','/request-quote/'];
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const context=await browser.newContext();const page=await context.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const report={layouts:[],accessibility:[],tasks:[],errors};
 fs.mkdirSync('qa/ux',{recursive:true});
 for(const width of widths){
  await page.setViewportSize({width,height:900});
  for(const route of routes){
   await page.goto(origin+route,{waitUntil:'networkidle'});
   const layout=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,h1:document.querySelectorAll('h1').length,unloaded:[...document.images].filter(i=>!i.loading&&i.complete&&!i.naturalWidth).map(i=>i.src)}));
   assert.equal(layout.overflow,false,`${width} ${route} overflows`);assert.equal(layout.h1,1);assert.deepEqual(layout.unloaded,[]);
   report.layouts.push({width,route,...layout});
  }
 }
 console.log('PASS 54 responsive page layouts');
 for(const width of [390,1440]){
  await page.setViewportSize({width,height:900});
  for(const route of ['/',product.path,'/catalog/','/request-quote/','/industries/apparel/']){
   await page.goto(origin+route,{waitUntil:'networkidle'});
   const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();
   report.accessibility.push({width,route,violations:result.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))});
  }
 }
 console.log('Completed WCAG automated checks');
 await page.setViewportSize({width:390,height:844});await page.goto(origin+'/');
 await page.getByRole('button',{name:'Menu',exact:true}).click();
 await page.locator('.navgroup summary').first().click();
 assert.ok(await page.getByRole('link',{name:'Custom boxes',exact:true}).isVisible());
 await page.keyboard.press('Escape');assert.equal(await page.locator('.navgroup[open]').count(),0);
 await page.getByRole('button',{name:'Menu',exact:true}).click();await page.locator('.navgroup summary').first().click();
 await page.getByRole('link',{name:'Custom boxes',exact:true}).click();await page.waitForURL('**/products/custom-boxes/');
 await page.getByRole('link',{name:'View magnetic gift boxes',exact:true}).click();await page.waitForURL('**/magnetic-gift-boxes/');
 assert.ok(await page.locator('.ux-mobile-quote').isVisible());
 await page.locator('.ux-mobile-quote a').click();await page.waitForURL('**/request-quote/**');
 assert.equal(await page.locator('#product').inputValue(),'Magnetic gift boxes');
 assert.equal(await page.locator('#details').inputValue(),'');
 assert.equal(await page.locator('[name=source_page]').inputValue(),'/products/custom-boxes/magnetic-gift-boxes/');
 report.tasks.push('Mobile menu → boxes → magnetic boxes → associated RFQ');
 await page.goto(origin+'/catalog/');
 await page.locator('#catalog-search').fill('magnetic closure boxes');
 await page.waitForFunction(()=>document.querySelector('#catalog-search-status').textContent.includes('matching products'));
 assert.ok(await page.locator('#catalog-grid .catalog-card').count()>0);
 await page.locator('#catalog-clear').click();assert.equal(await page.locator('#catalog-grid .catalog-card').count(),24);
 await page.locator('#format-filter').selectOption('rigid');
 await page.waitForFunction(()=>document.querySelector('#catalog-search-status').textContent.includes('matching products'));
 await page.locator('#catalog-clear').click();
 await page.locator('#catalog-search').fill('zz-no-such-product');await page.waitForFunction(()=>document.querySelector('#catalog-search-status').textContent.includes('No matching'));
 await page.goto(origin+'/catalog/paper-boxes/');
 assert.equal(await page.locator('[data-catalog-scope]').getAttribute('data-catalog-scope'),'family:paper-boxes');
 assert.equal(await page.locator('#catalog-grid>.catalog-card:visible').count(),12);
 await page.locator('.ux-more-products>summary').click();assert.equal(await page.locator('#catalog-grid .catalog-card:visible').count(),24);
 await page.locator('#catalog-search').fill('stand-up pouch');await page.waitForFunction(()=>document.querySelector('#catalog-search-status').textContent.includes('No matching'));
 report.tasks.push('Search synonyms, collection scope, structure filter, 12-item disclosure, empty state and reset');
 await page.goto(origin+'/request-quote/?product=Custom%20box&source=%2Fproducts%2Fcustom-boxes%2F');
 assert.equal(await page.locator('#name').getAttribute('required'),null);assert.equal(await page.locator('#country').getAttribute('required'),null);
 await page.locator('button[type=submit]').click();assert.ok(await page.locator('#email-error').isVisible());
 await page.locator('#email').fill('buyer@example.com');await page.locator('#details').fill('A custom printed carton for a new product.');
 await page.locator('[name=consent]').check();
 const inputBefore=await page.locator('#details').inputValue();
 let submits=0;
 await page.route('**/request-quote/send.php',async route=>{submits++;await route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({ok:false,message:'Test transport unavailable'})})});
 await page.locator('button[type=submit]').click();await page.waitForFunction(()=>document.querySelector('#form-result').textContent.includes('Test transport unavailable'));
 assert.equal(await page.locator('#details').inputValue(),inputBefore);assert.equal(submits,1);
 await page.unroute('**/request-quote/send.php');
 await page.locator('#attachments').setInputFiles({name:'reference.pdf',mimeType:'application/pdf',buffer:Buffer.from('%PDF-1.4 Test')});
 await page.route('**/request-quote/send.php',route=>route.fulfill({status:200,contentType:'application/json',body:'{"ok":true}'}));
 await page.locator('button[type=submit]').click();await page.waitForFunction(()=>document.querySelector('#form-result').textContent.includes('submitted for email delivery'));
 const events=await page.evaluate(()=>globalThis.dataLayer);
 for(const event of ['rfq_form_view','rfq_form_start','rfq_form_submit','rfq_form_success','rfq_form_error','file_upload_success'])assert.ok(events.some(e=>e.event===event),event);
 assert.ok(!JSON.stringify(events).includes('buyer@example.com'));assert.ok(!JSON.stringify(events).includes(inputBefore));
 report.tasks.push('Minimal brief, inline errors, transport failure preservation, attachment and success events (mocked transport; no email sent)');
 for(const [route,name,width] of [['/','home-desktop',1440],['/','home-mobile',390],[product.path,'product-mobile',390],['/products/custom-boxes/','category-desktop',1440]]){
  await page.setViewportSize({width,height:1000});await page.goto(origin+route,{waitUntil:'networkidle'});
  await page.evaluate(async()=>{document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager');await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))});
  await page.screenshot({path:`qa/ux/${name}.png`,fullPage:true});
 }
 const violations=report.accessibility.flatMap(r=>r.violations.map(v=>({width:r.width,route:r.route,...v})));
 fs.writeFileSync('qa/ux/acceptance.json',JSON.stringify(report,null,2));
 await browser.close();assert.deepEqual(errors,[]);assert.equal(violations.length,0,JSON.stringify(violations));console.log('PASS',JSON.stringify({layouts:report.layouts.length,accessibility:report.accessibility.length,tasks:report.tasks.length}));
})().catch(e=>{console.error(e);process.exit(1)});

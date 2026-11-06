// Render the pillar, all topic pages and every new article on desktop and mobile.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const {default:AxeBuilder}=require(process.env.AXE_MODULE||'@axe-core/playwright');
const origin=process.env.TEST_ORIGIN||'http://127.0.0.1:4174';
const routes=JSON.parse(fs.readFileSync('content/page-manifest.json','utf8')).map(p=>p[0]).filter(p=>p==='/guides/'||p.startsWith('/blog/'));
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const context=await browser.newContext();const page=await context.newPage();const report={layouts:[],accessibility:[],tasks:[],errors:[]};
 page.on('pageerror',e=>report.errors.push(e.message));fs.mkdirSync('qa/blog-2026-11-06',{recursive:true});
 for(const width of [360,768,1440]){
  await page.setViewportSize({width,height:900});
  for(const route of routes){
   const response=await page.goto(origin+route,{waitUntil:'networkidle'});assert.equal(response.status(),200);
   await page.locator('img').evaluateAll(images=>images.forEach(img=>img.loading='eager'));
   await page.waitForFunction(()=>[...document.images].every(i=>i.complete));
   const state=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,h1:document.querySelectorAll('h1').length,failedImages:[...document.images].filter(i=>!i.naturalWidth).map(i=>i.src),unresolvedNotes:[...document.querySelectorAll('a[href^="#note-"]')].filter(a=>!document.getElementById(a.hash.slice(1))).length}));
   assert.equal(state.overflow,false,`${width} ${route}`);assert.equal(state.h1,1);assert.deepEqual(state.failedImages,[]);assert.equal(state.unresolvedNotes,0);report.layouts.push({width,route,...state});
  }
 }
 for(const width of [390,1440]){
  await page.setViewportSize({width,height:900});
  for(const route of ['/guides/','/blog/category/design-sampling/','/blog/packaging-print-proof-approval-checklist/']){
   await page.goto(origin+route);const audit=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
   assert.deepEqual(audit.violations,[],JSON.stringify(audit.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))));report.accessibility.push({width,route,violations:0});
   await page.screenshot({path:`qa/blog-2026-11-06/${width}-${route==='/guides/'?'pillar':route.includes('/category/')?'category':'article'}.png`,fullPage:true});
   await page.screenshot({path:`qa/blog-2026-11-06/${width}-${route==='/guides/'?'pillar':route.includes('/category/')?'category':'article'}-viewport.png`});
  }
 }
 await page.goto(origin+'/guides/');await page.locator('.blog-guide-disclosure').first().locator('summary').click();assert(await page.locator('.blog-guide-disclosure').first().getAttribute('open')!==null);report.tasks.push('Retained guide disclosure opens');
 await page.locator('.blog-decisions a').last().click();assert(page.url().includes('/blog/category/design-sampling/'));await page.locator('.blog-card h3 a').first().click();assert(page.url().includes('/blog/packaging-print-proof-approval-checklist/'));
 await page.locator('a[href="#note-1"]').click();assert(page.url().endsWith('#note-1'));await page.locator('#note-1 a[href="#ref-1"]').click();assert(page.url().endsWith('#ref-1'));report.tasks.push('Pillar → category → independent article → footnote and return');
 assert.deepEqual(report.errors,[]);fs.writeFileSync('qa/blog-2026-11-06/browser-results.json',JSON.stringify(report,null,2));await browser.close();console.log(`PASS ${report.layouts.length} layouts, ${report.accessibility.length} accessibility checks and ${report.tasks.length} reading tasks`);
})().catch(e=>{console.error(e);process.exit(1)});

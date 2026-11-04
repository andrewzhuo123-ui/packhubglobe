// Verify new answers can be read without JS and their layouts remain usable.
const assert=require('node:assert/strict'),fs=require('node:fs');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const {default:AxeBuilder}=require(process.env.AXE_MODULE||'@axe-core/playwright');
const origin=process.env.TEST_ORIGIN||'http://127.0.0.1:4187';
const slugs=['straight-vs-reverse-tuck-end','packaging-materials-explained','custom-packaging-moq','foil-vs-spot-uv-vs-embossing','cosmetic-packaging-buyers-guide','apparel-packaging-selection','prepare-packaging-dielines','choose-packaging-supplier-china','custom-paper-bags-guide'];
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const context=await browser.newContext({javaScriptEnabled:false}),page=await context.newPage();
 const report={guides:[],layouts:[],accessibility:[]};fs.mkdirSync('qa/geo',{recursive:true});
 for(const slug of slugs){
  const route='/guides/'+slug+'/';assert.equal((await page.goto(origin+route)).status(),200);assert.equal(await page.locator('h1').count(),1);
  assert.equal(await page.locator('link[rel=canonical]').getAttribute('href'),'https://www.packhubglobe.com'+route);
  const graph=JSON.parse(await page.locator('script[type="application/ld+json"]').textContent())['@graph'],article=graph.find(n=>n['@type']==='Article');
  assert.equal(article.dateModified,await page.locator('.article-byline time').getAttribute('datetime'));assert.ok(graph.some(n=>n['@type']==='Organization'&&n['@id']===article.publisher['@id']));
  assert.equal(await page.locator('.guide-answer').count(),1);assert.ok((await page.locator('.guide-answer').textContent()).length>180);
  assert.ok(await page.locator('.guide-longform').evaluate(el=>!!(el.querySelector('.guide-answer').compareDocumentPosition(el.querySelector('section'))&Node.DOCUMENT_POSITION_FOLLOWING)));
  assert.ok(await page.locator('#guide-faq details').count()>=4);await page.locator('#guide-faq summary').first().click();assert.equal(await page.locator('#guide-faq details').first().getAttribute('open'),'');
  assert.ok(await page.locator('.article-toc a').evaluateAll(links=>links.every(a=>document.getElementById(a.hash.slice(1)))));
  assert.ok((await page.locator('#worked-example').textContent()).toLowerCase().includes('illustrative'));
  for(const width of [390,1440]){
   await page.setViewportSize({width,height:900});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,slug);
   const broken=await page.locator('img').evaluateAll(async images=>{await Promise.all(images.map(i=>{i.loading='eager';return i.decode().catch(()=>{})}));return images.filter(i=>!i.naturalWidth).map(i=>i.src)});assert.deepEqual(broken,[]);report.layouts.push({route,width});
  }
  report.guides.push({route,status:200,noJavaScript:true,canonical:true,article:true,answerFirst:true,faq:true});
 }
 await context.close();const rendered=await browser.newContext(),view=await rendered.newPage(),errors=[];view.on('pageerror',e=>errors.push(e.message));
 for(const width of [390,1440]){
  await view.setViewportSize({width,height:1000});await view.goto(origin+'/guides/prepare-packaging-dielines/',{waitUntil:'networkidle'});
  const result=await new AxeBuilder({page:view}).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze();assert.deepEqual(result.violations,[]);
  await view.locator('img').evaluateAll(async images=>{await Promise.all(images.map(i=>{i.loading='eager';return i.decode().catch(()=>{})}))});
  await view.screenshot({path:`qa/geo/dielines-${width}.png`,fullPage:true});report.accessibility.push({width,violations:0});
 }
 for(const route of ['/products/custom-boxes/','/products/paper-bags/','/industries/apparel/','/materials/']){await view.goto(origin+route);assert.ok(await view.getByRole('heading',{name:'Make your next packaging decision'}).count())}
 assert.deepEqual(errors,[]);fs.writeFileSync('qa/geo/acceptance.json',JSON.stringify(report,null,2));await browser.close();console.log('PASS',JSON.stringify({guides:report.guides.length,noJavaScript:true,layouts:report.layouts.length,accessibility:report.accessibility.length}));
})().catch(e=>{console.error(e);process.exit(1)});

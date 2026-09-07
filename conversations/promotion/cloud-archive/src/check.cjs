const {chromium}=require('playwright');
const fs=require('fs');
(async()=>{
  const slim=(await import('./browser/node_modules/@sparticuz/chromium/build/index.js')).default;
  const browser=await chromium.launch({headless:true,executablePath:'/workspace/scratch/d317e6067fb4/mindmap-qa/chrome-runtime/chromium',args:slim.args});
  const errors=[];
  for(const [width,theme] of [[768,'light'],[392,'light'],[392,'dark']]){
    const page=await browser.newPage({viewport:{width,height:1200},colorScheme:theme});
    page.on('pageerror',e=>errors.push(e.message));
    await page.goto('file:///workspace/scratch/d317e6067fb4/life-map-preview.html');
    const frame=page.frames()[1];
    await frame.waitForSelector('.lm-node');
    await page.waitForTimeout(160);
    const states=[['overview',null],['domains','domains'],['domain-d04','D04']];
    for(const [state,id] of states){
      if(id)await frame.locator('.lm-node[data-id="'+id+'"] button').click();
      await page.waitForTimeout(120);
      const metrics=await frame.evaluate(()=>{
        const root=document.getElementById('life-map-v4');
        const stage=root.querySelector('.lm-stage');
        const r=stage.getBoundingClientRect();
        const bad=[...root.querySelectorAll('.lm-node')].filter(el=>{
          const b=el.getBoundingClientRect();return b.left<r.left-.1||b.right>r.right+.1||el.scrollWidth>el.clientWidth+2;
        }).map(el=>el.dataset.id);
        return {width:r.width,height:root.scrollHeight,bad,documentWidth:document.documentElement.scrollWidth};
      });
      await page.locator('iframe').evaluate((el,h)=>el.style.height=h+'px',metrics.height+10);
      await page.setViewportSize({width,height:metrics.height+50});
      await page.screenshot({path:`/workspace/scratch/d317e6067fb4/mindmap-qa/${width}-${theme}-${state}.png`,fullPage:true});
      console.log(JSON.stringify({width,theme,state,...metrics}));
    }
    await frame.locator('.lm-crumbs button').first().click();
    await frame.locator('[data-id="knowledge"] button').click();
    await frame.locator('[data-id="methods"] button').click();
    await frame.locator('[data-id="M14"] button').click();
    await page.waitForTimeout(120);
    const h=await frame.locator('#life-map-v4').evaluate(el=>el.scrollHeight);
    await page.locator('iframe').evaluate((el,h)=>el.style.height=h+'px',h+10);
    await page.setViewportSize({width,height:h+50});
    await page.screenshot({path:`/workspace/scratch/d317e6067fb4/mindmap-qa/${width}-${theme}-m14.png`,fullPage:true});
    if(!await frame.locator('.lm-previews').last().innerText())throw Error('Module detail missing');
    await page.close();
  }
  console.log('JS_ERRORS',JSON.stringify(errors));
  await browser.close();
})();

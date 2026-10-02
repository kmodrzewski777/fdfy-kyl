const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:1000}});
const errs=[];p.on('pageerror',e=>errs.push('PAGEERR '+e.message));p.on('console',m=>{if(m.type()==='error')errs.push('CONSOLE '+m.text())});
await p.goto('file:///home/user/fdfy-kyl/insights-demo.html');await p.waitForTimeout(1500);
// scroll to render lazy sections
for(let y=0;y<40000;y+=800){await p.evaluate(y=>scrollTo(0,y),y);await p.waitForTimeout(60);}
await p.waitForTimeout(500);
const r=await p.evaluate(()=>{const K=scoreK();return {score:document.querySelector('.sc-num b')?.textContent,prev:scoreTot(K,'p'),cur:scoreTot(K,'c'),K:K.map(x=>[x.n,x.c,x.f(x.c)]),
 share30:flShare(30,0),share30p:flShare(30,30),share7:flShare(7,0),
 flkpi:document.querySelector('#fl-kpi').innerText.slice(0,400),flrs:document.querySelector('#fl-rs').innerText,
 inc:INC.tests.map(t=>[t.n,t.sig,Math.round(t.lift*100),t.pv.toFixed(4),Math.round(t.inc),Math.round(t.gr)]),
 iksum:document.querySelector('#ik-sum').innerText.slice(0,600),
 tiles:document.querySelector('#tiles').innerText.slice(0,500),cons:document.querySelector('#cons-tiles').innerText,
 churn:document.querySelector('#cz-head').innerText,nc:document.querySelector('#nc-k').innerText,app:document.querySelector('#app-top').innerText.slice(0,500),
 rev:document.querySelector('#d-rev')?.innerText, risk:document.querySelector('#cz-rv')?.innerText.slice(-200)}});
console.log(JSON.stringify(r,null,1));console.log(errs.join('\n'));
await p.screenshot({path:'shot_top.png'});
for(const id of ['flows','inkr','zgody','status','app']){const el=await p.$('#'+id);if(el){await el.scrollIntoViewIfNeeded();await p.waitForTimeout(300);await el.screenshot({path:'shot_'+id+'.png'});}}
await b.close();})();

const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:900}});const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
await p.goto('file:///home/user/fdfy-kyl/insights-demo.html');for(let y=0;y<70000;y+=800){await p.evaluate(y=>scrollTo(0,y),y);await p.waitForTimeout(25);}
const r=await p.evaluate(()=>{const K=scoreK(),t=document.querySelector('main').innerText;const nums=(t.match(/\d{1,3}(?:[  ]\d{3})+|\d{3,}/g)||[]).map(s=>s.replace(/[  ]/g,'')).filter(s=>+s>=100&&+s<5e6&&!/^20(25|26)$/.test(s));
 let rv=0,F=FLOWS,last=F.days-2;for(let i=last-29;i<=last;i++)for(const id in F.c)rv+=F.c[id].r[i];let tt=0;for(let i=last-29;i<=last;i++)tt+=F.tot[i];
 return {score:document.querySelector('.sc-num b').textContent,cur:scoreTot(K,'c'),prev:scoreTot(K,'p'),K:K.map(x=>[x.n,Math.round(x.c*10)/10,Math.round(x.f(x.c)*100)/100]),rv30:rv,share:rv/tt,
  inc:INC.tests.map(t=>[t.n.slice(0,22),t.days,t.live,t.sig,Math.round(t.lift*100),Math.round(t.inc)]),ok:INC.tests.filter(t=>t.sig).length,
  round:[...new Set(nums.filter(s=>/00$/.test(s)))].join(' '),nround:nums.filter(s=>/00$/.test(s)).length,n:nums.length,
  tiles:document.querySelector('#tiles').innerText.replace(/\n/g,' | ').slice(0,300),fl:document.querySelector('#fl-kpi').innerText.replace(/\n/g,' | ').slice(0,420)};});
console.log(JSON.stringify(r,null,1));console.log('ERR',errs);
for(const id of ['score','zgody','trendy','flows','inkr','leadflow','app']){const el=await p.$('#'+id);if(el){await el.scrollIntoViewIfNeeded();await p.waitForTimeout(250);await el.screenshot({path:'build/s_'+id+'.png'});}}
await b.close();})();

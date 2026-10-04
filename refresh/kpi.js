// Zapis dużych liczb z wyrenderowanego dashboardu do historii KPI (badge porównań). Użycie: node refresh/kpi.js
const {chromium}=require('playwright');const path=require('path'),fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:1000}});
await p.goto('file://'+path.resolve(__dirname,'../dashboard/foodify-retencja.html'));await p.waitForTimeout(2000);
const snap=JSON.parse(fs.readFileSync(path.resolve(__dirname,'snapshot.json')));
await p.evaluate(s=>{applyData(s);},snap);await p.waitForTimeout(800);
await p.evaluate(()=>{try{LZ.forEach(([fn])=>lzRun(fn));}catch(e){}try{renderMV();}catch(e){}});await p.waitForTimeout(800);
const o=await p.evaluate(()=>kpiCollect());const raw=JSON.parse(fs.readFileSync(path.resolve(__dirname,'raw.json')));
(raw.kpi_hist=raw.kpi_hist||{})[snap.asOf]=o;fs.writeFileSync(path.resolve(__dirname,'raw.json'),JSON.stringify(raw));
console.log('kpi',snap.asOf,Object.keys(o).length);await b.close();})();

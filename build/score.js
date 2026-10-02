const scLin=(v,lo,hi)=>Math.max(1,Math.min(10,1+9*(v-lo)/(hi-lo)));
function scoreK(){const S=SCORE,W=CHURN.wk,o=win(sr('2026-07-16',W.out2,7),30,'sum'),bk=win(sr('2026-07-16',W.back2,7),30,'sum'),
 r1=v=>(Math.round(v*10)/10).toFixed(1).replace('.',',')+'%',pc=v=>Math.round(v)+'%';
 return [
  {n:'Odnowienia przed końcem',u:'kończących się dostaw',w:25,c:S.renew[1],p:S.renew[0],f:v=>scLin(v,30,80),fmt:r1},
  {n:'Powroty stałych klientów',u:'na 100 odchodzących (2+ zamówień)',w:20,c:bk.c/o.c*100,p:o.p&&bk.p?bk.p/o.p*100:null,f:v=>scLin(v,40,100),fmt:v=>Math.round(v)},
  {n:'Drugi zakup',u:'klientów',w:15,c:S.second[1],p:S.second[0],f:v=>scLin(v,30,75),fmt:pc},
  {n:'Skuteczność automatyzacji',u:'kampanii z wygranym testem holdout',w:15,c:INC.tests.filter(t=>t.sig).length/INC.tests.length*100,p:66.7,f:v=>scLin(v,0,80),fmt:pc},
  {n:'Jedzący z aplikacją',u:'jedzących',w:15,c:S.app[1],p:S.app[0],f:v=>scLin(v,0,90),fmt:pc},
  {n:'Rabat w koszyku',u:'wartości zamówień',w:10,c:S.disc[1],p:S.disc[0],f:v=>scLin(25-v,0,21),fmt:r1}];}
function scoreTot(K,k){return K.reduce((a,x)=>a+x.w*x.f(k==='c'?x.c:(x.p??x.c)),0)/K.reduce((a,x)=>a+x.w,0);}
function renderScore(){const el=document.getElementById('sc-card');if(!el)return;
 const K=scoreK(),sc=scoreTot(K,'c'),sp=scoreTot(K,'p'),d=sc-sp,r1=v=>(Math.round(v*10)/10).toFixed(1).replace('.',',');
 const word=v=>v<2.5?'Krytycznie':v<4?'Słabo':v<5.5?'Przeciętnie':v<7?'Nieźle':v<8.5?'Dobrze':'Doskonale';
 const col=v=>v<4?'var(--crit)':v<5.5?'#ff9061':v<7?'#d9a400':'var(--good)';
 el.innerHTML=`<div class="sc-main"><span class="eyebrow">Scoring retencji</span><div class="sc-num"><b style="color:${col(sc)}">${r1(sc)}</b><span>/ 10</span></div><div class="sc-word" style="color:${col(sc)}">${word(sc)}</div>
  <span class="dlt ${d>0.05?'up':d<-0.05?'dn':'eq'}">${d>0.05?'▲':d<-0.05?'▼':'='} ${r1(Math.abs(d))} vs poprz. 30 dni (${r1(sp)})</span>
  <div class="sc-gauge"><i style="left:${(sc-1)/9*100}%"></i></div><div class="sc-ticks"><span>1 krytycznie</span><span>10 perfekcyjnie</span></div><button type="button" class="sc-hb" id="sc-hb"><span>?</span>Jak liczony jest scoring?</button></div>
  <div class="sc-chw"><span class="eyebrow">Scoring dzień po dniu</span><div id="ch-sc"></div></div><div class="sc-parts">${K.map(x=>{const v=x.f(x.c),pv=x.p!=null?x.f(x.p):null,dd=pv!=null?v-pv:0;return `<div class="sc-r"><div class="sc-l"><b>${x.n}</b><span>${x.fmt(x.c)} ${x.u}</span></div><i><em style="width:${(v-1)/9*100}%;background:${col(v)}"></em></i><b class="sc-v">${r1(v)}</b><span class="sc-d ${dd>0.05?'up':dd<-0.05?'dn':''}">${Math.abs(dd)>0.05?(dd>0?'▲':'▼')+r1(Math.abs(dd)):'='}</span></div>`;}).join('')}</div>`;}
function renderScoreTrend(){const el=document.getElementById('ch-sc');if(!el)return;
 const K=scoreK(),sc=scoreTot(K,'c'),sp=scoreTot(K,'p'),t0=Date.UTC(2026,7,7),N=56,out=[];let s=97;const R=()=>{s=(s*16807)%2147483647;return s/2147483647;};
 let w=0;for(let j=0;j<N;j++){const base=j<26?sp+.05*Math.sin(j/3.1)-.04:sp+(sc-sp)*Math.pow((j-25)/(N-26),.9);w=w*.6+(R()-.5)*.16;const dip=(j>=9&&j<=13)?-.18*Math.sin((j-9)/4*Math.PI):(j>=38&&j<=41)?-.11*Math.sin((j-38)/3*Math.PI):0;out.push(j===N-1?sc:base+w+dip);}
 const mn=Math.max(1,Math.floor(Math.min(...out)-0.5)),mx=Math.min(10,Math.ceil(Math.max(...out)+0.3));
 lines(el,[{n:'Scoring',agg:'mean',c:cssv('--magenta'),noscope:1,ax:v=>(Math.round(v*10)/10).toFixed(1).replace('.',','),fmt:v=>(Math.round(v*10)/10).toFixed(1).replace('.',','),d:out,date:i=>dfmt(new Date(t0+i*864e5))}],[],mn,mx,'Scoring retencji dziennie');}


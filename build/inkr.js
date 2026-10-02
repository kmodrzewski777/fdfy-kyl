// ---------- inkrementalność: testy holdout 70/30
const INC={tests:[
 // kampania, start, dni, [grupa z kampanią, % kupujących], [holdout, % kupujących]
 {id:'t1',from:'2026-07-02',days:74,m:[11836,.5212],h:[5071,.4719]},
 {id:'t3',from:'2026-08-11',days:45,m:[2517,.4093],h:[1083,.3362]},
 {id:'t2',from:'2026-09-03',days:28,m:[4412,.4387],h:[1889,.4061]},
 {id:'t5',from:'2026-07-21',days:52,m:[1846,.2671],h:[794,.1966]},
 {id:'w1',from:'2026-08-25',days:36,m:[1094,.2413],h:[471,.1741]},
 {id:'w2',from:'2026-06-30',days:60,m:[2731,.1817],h:[1169,.1323]},
 {id:'w3',from:'2026-06-16',days:90,m:[4903,.0838],h:[2098,.0591]},
 {id:'w6',from:'2026-07-07',days:66,m:[587,.3135],h:[249,.2088]},
 {id:'t6',from:'2026-08-18',days:38,m:[2204,.1488],h:[947,.1172]},
 {id:'w4',from:'2026-07-14',days:79,m:[2961,.0472],h:[1262,.0412]},
 {id:'t7',from:'2026-09-10',days:21,m:[3388,.4107],h:[1452,.4029]},
 {id:'w5',from:'2026-08-04',days:57,m:[18627,.0089],h:[7983,.0091]}]};
const ikCdf=x=>{const t=1/(1+.2316419*Math.abs(x)),y=.3989423*Math.exp(-x*x/2)*t*(.3193815+t*(-.3565638+t*(1.781478+t*(-1.821256+t*1.330274))));return x>0?1-y:y;};
INC.tests.forEach((T,ti)=>{const c=FLOWS.c[T.id],i0=Math.round((D0(T.from)-D0(FLOWS.start))/864e5);T.n=c.n;T.t=c.t;
 T.M={n:T.m[0],p:Math.round(T.m[0]*T.m[1])};T.H={n:T.h[0],p:Math.round(T.h[0]*T.h[1])};
 let gc=0,gr=0;for(let i=i0;i<i0+T.days;i++){gc+=c.c[i]||0;gr+=c.r[i]||0;}T.gc=gc;T.gr=gr;T.aov=gc?gr/gc:0;
 const pm=T.M.p/T.M.n,ph=T.H.p/T.H.n,se=Math.sqrt(pm*(1-pm)/T.M.n+ph*(1-ph)/T.H.n)||1;T.pm=pm;T.ph=ph;T.d=pm-ph;T.z=T.d/se;T.pv=2*(1-ikCdf(Math.abs(T.z)));T.sig=T.pv<.05&&T.d>0;
 T.to=D0(T.from)+(T.days-1)*864e5;T.live=T.to>=D0('2026-09-30');T.lift=ph?T.d/ph:0;T.extra=T.d*T.M.n;T.inc=T.extra*T.aov;
 let s=ti*131+7;const R=()=>{s=(s*16807)%2147483647;return s/2147483647;},tau=T.days/2.6,cu=k=>(1-Math.exp(-k/tau))/(1-Math.exp(-T.days/tau));
 T.lm=[];T.lh=[];for(let k=1;k<=T.days;k++){const w=cu(k);T.lm.push(pm*w*(1+(k<T.days?(R()-.5)*.03:0))*100);T.lh.push(ph*Math.pow(w,1.04)*(1+(k<T.days?(R()-.5)*.03:0))*100);}});
let IKP='all';try{IKP=localStorage.getItem('ik-p')||'all';if(IKP!=='all'&&!INC.tests.some(t=>t.id===IKP))IKP='all';}catch(e){}
function renderInkr(){const el=document.getElementById('ik-ch');if(!el)return;const TS=INC.tests,ok=TS.filter(t=>t.sig),mag=cssv('--magenta');
 const pct=x=>(x*100).toFixed(1).replace('.',',')+'%',nn=x=>Math.round(x).toLocaleString('pl-PL'),zlx=x=>(x<0?'−':'')+zl(Math.abs(x)),sg=x=>x>0?'+':x<0?'−':'';
 const incOk=ok.reduce((a,t)=>a+t.inc,0),grOk=ok.reduce((a,t)=>a+t.gr,0),avgLift=ok.reduce((a,t)=>a+t.lift,0)/ok.length,holdN=TS.reduce((a,t)=>a+t.H.n,0);
 const verdict=t=>t.sig?['good','Zarabia: wzrost potwierdzony']:t.d>0?['warn','Wynik niepewny']:['bad','Brak efektu'];
 document.getElementById('ik-sum').innerHTML=`<div class="ik-hero"><div class="ik-big"><span class="eyebrow">Kampanie z twardym dowodem skuteczności</span><b>${pf(ok.length,TS.length)}</b><p><b>${ok.length} z ${TS.length}</b> testowanych automatyzacji retencyjnych sprzedaje więcej niż grupa kontrolna bez komunikacji, z pewnością statystyczną powyżej 95%. To realny, dodatkowy przychód, a nie zakupy, które i tak by się wydarzyły.</p></div>
  <div class="fl-k ik-kk">${[['Testowane kampanie',TS.length,`${TS.filter(t=>t.live).length} w toku, ${TS.filter(t=>!t.live).length} zakończonych`],['Z istotnym wzrostem',ok.length,'p < 0,05'],['Śr. wzrost konwersji','+'+Math.round(avgLift*100)+'%','w kampaniach, które działają'],['Realny przychód',zl(incOk),'ponad grupę kontrolną'],['Realny / przypisany',pf(incOk,grOk),'przychodu z Goals to czysty zysk'],['Grupa kontrolna',nn(holdN),'osób bez komunikacji']].map(([l,v,s])=>`<div class="tile" data-noseg="1"><span class="eyebrow">${l}</span><span class="big">${v}</span><span class="tsub">${s}</span></div>`).join('')}</div></div>`;
 document.getElementById('ik-tab').innerHTML=`<div class="ikt-w"><table class="ikt"><thead><tr><th>Kampania</th><th>Test</th><th>Z kampanią</th><th>Holdout</th><th>Wzrost</th><th>Pewność</th><th>Realny przychód</th><th>Werdykt</th></tr></thead><tbody>${TS.slice().sort((a,b)=>b.sig-a.sig||b.inc-a.inc).map(t=>{const [c,l]=verdict(t);return `<tr data-ik="${t.id}" class="${IKP===t.id?'on':''}" tabindex="0"><td><b>${esc(t.n)}</b><small>${t.t}</small></td><td>${t.days} dni<small>${t.live?'w toku':'zakończony '+dfs(t.to)}</small></td><td>${pct(t.pm)}</td><td>${pct(t.ph)}</td><td class="${t.d>0?'up':'dn'}">${sg(t.lift)}${Math.abs(Math.round(t.lift*100))}%</td><td>${t.pv<.001?'> 99,9%':(Math.max(0,(1-t.pv)*100)).toFixed(1).replace('.',',')+'%'}</td><td>${t.sig?zl(t.inc):'—'}</td><td><span class="ikp ${c}">${l}</span></td></tr>`;}).join('')}</tbody></table></div><p class="foot-note">Kliknij kampanię, żeby zobaczyć jej test. Pewność = 1 − p (test różnicy dwóch proporcji). Realny przychód = różnica w % kupujących × liczba osób z kampanią × średnia wartość zamówienia.</p>`;
 document.querySelectorAll('[data-ikp]').forEach(x=>x.setAttribute('aria-pressed',x.dataset.ikp===IKP));
 const V=document.getElementById('ik-verdict'),KK=document.getElementById('ik-k'),CH=document.getElementById('ik-line'),LH=document.getElementById('ik-lh');
 if(IKP==='all'){const M={n:TS.reduce((a,t)=>a+t.M.n,0),p:TS.reduce((a,t)=>a+t.M.p,0)},H={n:holdN,p:TS.reduce((a,t)=>a+t.H.p,0)};
  V.innerHTML=`<div class="ik-v"><span class="eyebrow">Wszystkie testy razem · ${TS.length} kampanii</span><b class="good">${ok.length} z ${TS.length} kampanii zwiększa sprzedaż</b><p>Bez istotnej różnicy: ${TS.filter(t=>!t.sig).map(t=>esc(t.n)).join(', ')}. To kandydaci do zmiany bodźca albo ograniczenia wysyłek.</p></div>`;
  el.innerHTML='';KK.innerHTML='';
  LH.textContent='Wzrost % kupujących względem grupy kontrolnej';
  const mx=Math.max(...TS.map(t=>t.lift))*1.15,mn=Math.min(0,...TS.map(t=>t.lift));
  CH.innerHTML=`<div class="ik-lifts">${TS.slice().sort((a,b)=>b.lift-a.lift).map(t=>{const w=Math.abs(t.lift)/(mx-mn)*100,l=(Math.min(0,t.lift)-mn)/(mx-mn)*100;return `<div class="ik-lr" data-ik="${t.id}"><span class="nm">${esc(t.n)}</span><span class="tr"><i style="left:${l}%;width:${Math.max(.5,w)}%;background:${t.sig?mag:t.d>0?'var(--l1)':'var(--l2)'}"></i></span><b class="${t.sig?'g':''}">${sg(t.lift)}${Math.abs(Math.round(t.lift*100))}%</b></div>`;}).join('')}</div>`;
  document.getElementById('leg-ik').innerHTML=`<span><i style="background:${mag}"></i>wzrost potwierdzony</span><span><i style="background:var(--l1)"></i>niepewny</span><span><i style="background:var(--l2)"></i>brak efektu</span>`;return;}
 const T=TS.find(t=>t.id===IKP),M=T.M,H=T.H,pm=T.pm,ph=T.ph,[cls,head]=verdict(T);
 const txt=T.sig?`Osoby, które dostają kampanię, kupują częściej niż grupa bez komunikacji (${pct(pm)} vs ${pct(ph)}). Różnica jest statystycznie pewna: kampanię warto utrzymać i skalować.`:T.d>0?`Grupa z kampanią kupuje częściej (${pct(pm)} vs ${pct(ph)}), ale różnica może być przypadkowa. ${T.live?'Test trwa dalej.':'Test zakończony bez rozstrzygnięcia.'}`:`Grupa bez komunikacji kupuje tak samo często lub częściej (${pct(ph)} vs ${pct(pm)}). Przychód przypisany w Goals klienci wygenerowaliby sami.`;
 V.innerHTML=`<div class="ik-v"><span class="eyebrow">Test holdout ${dfs(D0(T.from))} – ${T.live?'trwa':dfs(T.to)} · ${T.days} dni · ${T.t}</span><b class="${cls==='warn'?'':cls}">${esc(T.n)}: ${head.toLowerCase()}</b><p>${txt}</p></div>`;
 const mx=Math.max(pm+1.96*Math.sqrt(pm*(1-pm)/M.n),ph+1.96*Math.sqrt(ph*(1-ph)/H.n),.001)*1.15,
  row=(nm,sub,g,p,col)=>{const s1=1.96*Math.sqrt(p*(1-p)/g.n);return `<div class="ik-row"><div class="nm">${nm}<small>${sub}</small></div><div class="ik-tr"><div class="ik-bar" style="width:${p/mx*100}%;background:${col}"></div><div class="ik-ci" style="left:${Math.max(0,p-s1)/mx*100}%;width:${2*s1/mx*100}%"></div></div><div class="val">${pct(p)}<small>${nn(g.p)} z ${nn(g.n)} kupiło</small></div></div>`;},
  tk=[0,.25,.5,.75,1].map(q=>`<span>${(mx*q*100).toFixed(1).replace('.',',')}%</span>`).join('');
 el.innerHTML=row('Dostają kampanię','70% grupy',M,pm,'var(--magenta)')+row('Holdout: bez kampanii','30% grupy',H,ph,'var(--l1)')+`<div class="ik-ax"><span></span><div>${tk}</div><span></span></div>`;
 const K=[['Wzrost',sg(T.lift)+Math.abs(T.lift*100).toFixed(1).replace('.',',')+'%'],['Różnica',sg(T.d)+Math.abs(T.d*100).toFixed(2).replace('.',',')+' pp'],['Pewność',T.sig?'Wysoka':'Niska'],['Przychód Goals',zl(T.gr)],['Realny przychód',T.d>0?zl(T.inc):'0 zł'],['Klienci netto',sg(T.extra)+nn(Math.abs(T.extra))]];
 KK.innerHTML=`<div class="fl-k">${K.map(([l,v])=>`<div class="tile" data-noseg="1"><span class="eyebrow">${l}</span><span class="big">${v}</span></div>`).join('')}</div>`;
 LH.textContent='% kupujących od startu testu';
 const t0=D0(T.from);lines(CH,[{n:'Dostają kampanię',noweek:1,noscope:1,pct:1,c:cssv('--magenta'),d:T.lm,date:i=>dfmt(new Date(t0+i*864e5))},{n:'Holdout',noscope:1,pct:1,c:cssv('--l1'),d:T.lh,date:i=>dfmt(new Date(t0+i*864e5))}],[],0,10,'% kupujących od startu testu',document.getElementById('leg-ik'));}
document.addEventListener('click',e=>{const b=e.target.closest('[data-ikp],[data-ik]');if(!b)return;const v=b.dataset.ikp||b.dataset.ik;IKP=IKP===v&&b.dataset.ik?'all':v;try{localStorage.setItem('ik-p',IKP)}catch(x){};renderInkr();if(b.dataset.ik)document.getElementById('ik-verdict').scrollIntoView({behavior:RM?'auto':'smooth',block:'center'});});
document.addEventListener('keydown',e=>{if(e.key!=='Enter')return;const r=e.target.closest&&e.target.closest('tr[data-ik]');if(r)r.click();});

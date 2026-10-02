// ---------- kampanie (dane demonstracyjne generowane deterministycznie)
const CAMPS=[
 // id, nazwa, typ, kanał, przychód w 30 dni (tys. zł), AOV, wysyłki dziennie, OR, CTOR, wypisy / dostarczone, start
 ['a1','Powitanie nowego leada','Activation','e-mail',78,820,260,.58,.19,.004],
 ['a2','Porzucony quiz dietetyczny','Activation','e-mail',64,940,95,.52,.24,.002],
 ['a3','Zestaw próbny 3 dni','Activation','e-mail',41,340,120,.47,.17,.003],
 ['a4','Lead bez zakupu 14 dni: kod startowy','Activation','e-mail',52,880,140,.44,.15,.004],
 ['a5','Sprawdził dostawę, nie kupił','Activation','e-mail',33,960,55,.55,.22,.002],
 ['a6','Onboarding przed startem dostawy','Activation','e-mail',18,420,45,.71,.26,.001],
 ['a7','Instalacja aplikacji po 1. zamówieniu','Activation','e-mail',14,1050,38,.63,.21,.001,'2026-05-12'],
 ['a8','Re-engagement leadów przed sunsetem','Activation','e-mail',20,900,210,.21,.09,.006],
 ['r1','Porzucony koszyk: e-mail po 1 h','Recovery','e-mail',168,1020,115,.54,.23,.002],
 ['r2','Porzucony koszyk: push w aplikacji','Recovery','push',96,990,140,.13,.52,0],
 ['r3','Porzucona płatność: przypomnienie po 1 h','Recovery','e-mail',112,1140,48,.63,.31,.001,'2026-06-02'],
 ['r4','Nieudana płatność: dokończ zamówienie','Recovery','SMS',41,1080,14,.72,.40,.001],
 ['r5','Porzucona konfiguracja diety','Recovery','e-mail',33,1010,52,.49,.20,.002],
 ['r6','Oglądał menu, nie zamówił','Recovery','push',20,980,160,.11,.36,0],
 ['t1','Odnowienie diety: 3 dni przed końcem','Retention','e-mail',520,1190,240,.61,.27,.001],
 ['t2','Odnowienie diety: dzień przed końcem','Retention','SMS + push',318,1120,210,.24,.45,.001],
 ['t3','Drugi zakup przed końcem 1. dostawy','Retention','e-mail',236,1060,70,.66,.29,.001],
 ['t4','Odnowienie zamówień 1–4-dniowych','Retention','e-mail',98,690,85,.57,.22,.002,'2026-07-15'],
 ['t5','Wypadli z rytmu (4+ zamówienia)','Retention','e-mail',152,1230,60,.58,.24,.002],
 ['t6','Upsell na dłuższy pakiet (20+ dni)','Retention','e-mail',128,1780,95,.52,.18,.002],
 ['t7','Ocena posiłków po 7 dniach','Retention','e-mail',46,1080,150,.64,.31,.001],
 ['t8','Program poleceń dla lojalnych','Retention','e-mail',84,1020,55,.59,.21,.001],
 ['t9','Podziękowanie po 5. i 10. zamówieniu','Retention','e-mail',58,1160,28,.74,.30,.001],
 ['t10','Menu na nowy tydzień','Retention','push',72,1050,630,.11,.41,0],
 ['t11','Urodziny klienta','Retention','e-mail',34,1140,30,.68,.33,.001],
 ['t12','Zmiana diety: rekomendacja','Retention','e-mail',54,1150,65,.55,.19,.002],
 ['w1','Bez dostawy 8–14 dni: wróć do diety','Win-back','e-mail',162,1080,45,.52,.21,.002],
 ['w2','Zagrożeni 15–30 dni: benefit kwotowy','Win-back','e-mail',176,1040,72,.48,.19,.003],
 ['w3','Reaktywacja 31–60 dni','Win-back','e-mail',118,990,80,.39,.16,.004],
 ['w4','Reaktywacja 61–90 dni','Win-back','e-mail',64,960,66,.33,.14,.005],
 ['w5','Utraceni 90+: ostatnia oferta','Win-back','e-mail',42,940,520,.19,.09,.008],
 ['w6','VIP win-back: Czempioni i Lojalni','Win-back','e-mail + SMS',74,1480,12,.66,.28,.001,'2026-06-20'],
 ['w7','Ankieta po odejściu + oferta','Win-back','e-mail',24,980,50,.41,.22,.003]];
const FLOWS=(()=>{const start='2026-04-08',days=178,t0=D0(start),last=days-2;
 const SEA={4:.97,5:.95,6:.9,7:.86,8:.89,9:1,10:1.02},WDF=[1.08,1,.97,1.01,.96,.9,1.08];
 const rng=s=>()=>{s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};
 const fac=i=>{const d=new Date(t0+i*864e5),m=d.getUTCMonth()+1;return SEA[m]*WDF[(d.getUTCDay()+6)%7]*(i===days-1?.42:1);};
 const c={};CAMPS.forEach(([id,n,t,ch,rv,aov,snd,or,ctor,un,from],ci)=>{const R=rng(ci*7919+17),f0=from?Math.round((D0(from)-t0)/864e5):0,push=/push|SMS/.test(ch)&&!/e-mail/.test(ch);
  const A=[[],[],[],[],[],[]],cv=[],r=[],cb=rv*1000/aov/30;
  for(let i=0;i<days;i++){if(i<f0){A.forEach(a=>a.push(0));cv.push(0);r.push(0);continue;}
   const g=(.86+.14*i/last)/.985,ramp=Math.min(1,(i-f0+1)/14),k=fac(i)*g*ramp,nz=()=>.88+.24*R();
   let s=snd*k*nz();if(id==='t10'){const wd=new Date(t0+i*864e5).getUTCDay();s=wd===0?snd*7*g*ramp*nz()*(i===days-1?.42:1):0;}
   const sent=Math.round(s),del=Math.round(sent*(push?.93+.03*R():.975+.015*R())),op=Math.round(del*or*(.94+.12*R())),cl=Math.round(op*ctor*(.9+.2*R()));
   const x=cb*k*nz(),cc=Math.floor(x+R());
   A[0].push(sent);A[1].push(del);A[2].push(op);A[3].push(cl);A[4].push(Math.floor(del*un+R()));A[5].push(Math.round(cc*(.72+.12*R())));cv.push(cc);r.push(Math.round(cc*aov*(.9+.2*R())));}
  c[id]={n,t,ch,st:'running',m:A,c:cv,r};});
 // przychód całej firmy: ~150 mln zł rocznie; automatyzacje dokładają ~26% w ostatnich 30 dniach
 const shape=Array.from({length:days},(_,i)=>fac(i)*(.97+.03*i/last));
 let cr=0,sh=0;for(let i=last-29;i<=last;i++){Object.values(c).forEach(x=>cr+=x.r[i]);sh+=shape[i];}
 const k=cr/.26/sh,tot=shape.map(v=>Math.round(v*k));
 return {start,days,c,tot};})();
let FLP=7,FLT='all',FLM='r';
const flShare=(n,off)=>{const F=FLOWS,last=F.days-2;let a=0,b=0;for(let i=last-off-n+1;i<=last-off;i++){if(i<0)continue;b+=F.tot[i];for(const id in F.c)a+=F.c[id].r[i];}return b?a/b*100:0;};
document.addEventListener('click',e=>{const t=e.target.closest('.fl-tc');if(t){FLT=FLT===t.dataset.t?'all':t.dataset.t;renderFlows();return;}
 const m=e.target.closest('.fl-ms .chip');if(m){FLM=m.dataset.m;renderFlows();}});
function renderFlows(){const el=document.getElementById('fl-kpi');if(!el)return;const F=FLOWS,C=F.c,ids=Object.keys(C).filter(id=>!FLHID.includes(id)),last=F.days-2,E=Math.max(0,last-Math.round(CUT));
 FLP=SCOPE?Math.min(SCOPE,E+1):E+1;
 const sw=(a,k,off)=>{let s=0;for(let i=E-off-k+1;i<=E-off;i++)if(i>=0)s+=a[i]||0;return s;};
 const st=(id,off)=>{const c=C[id];return {sent:sw(c.m[0],FLP,off),del:sw(c.m[1],FLP,off),op:sw(c.m[2],FLP,off),cl:sw(c.m[3],FLP,off),un:sw(c.m[4],FLP,off),ck:sw(c.m[5],FLP,off),cv:sw(c.c,FLP,off),rv:sw(c.r,FLP,off)};};
 const sum=(list,off)=>list.reduce((A,id)=>{const r=st(id,off);for(const k in r)A[k]+=(r[k]||0);return A;},{sent:0,del:0,op:0,cl:0,un:0,ck:0,cv:0,rv:0});
 const hasPrev=E-2*FLP+1>=0,P=(a,b)=>b?a/b*100:null,p1=v=>v==null?'—':(Math.round(v*10)/10).toFixed(1).replace('.',',')+'%';
 const sel=FLT==='all'?ids:ids.filter(id=>C[id].t===FLT),cur=sum(sel,0),prv=hasPrev?sum(sel,FLP):null,all=sum(ids,0),totRv=sw(F.tot,FLP,0),totPv=hasPrev?sw(F.tot,FLP,FLP):null;
 const shr=P(all.rv,totRv),shp=hasPrev?P(sum(ids,FLP).rv,totPv):null;
 const dlt=(v,pv,good)=>{if(pv==null||v==null)return '<span class="dlt eq">—</span>';const ch=pv?((v-pv)/pv*100):0,up=v>=pv;return `<span class="dlt ${Math.abs(ch)<0.5?'eq':(up===!!good?'up':'dn')}">${up?'▲':'▼'} ${Math.abs(Math.round(ch))}%</span>`;};
 const dpp=(v,pv)=>pv==null?'<span class="dlt eq">—</span>':`<span class="dlt ${Math.abs(v-pv)<0.05?'eq':v>pv?'up':'dn'}">${v>=pv?'▲':'▼'} ${Math.abs(v-pv).toFixed(1).replace('.',',')} pp</span>`;
 const K=[['Przychód',zl(cur.rv),dlt(cur.rv,prv&&prv.rv,1),1],['Udział w przychodzie',p1(shr),dpp(shr,shp),1],['Konwersje',f(cur.cv),dlt(cur.cv,prv&&prv.cv,1)],['Wysłane',f(cur.sent),dlt(cur.sent,prv&&prv.sent,1)],['Open rate',p1(P(cur.op,cur.del)),dlt(P(cur.op,cur.del),prv&&P(prv.op,prv.del),1)],['CTOR',p1(P(cur.cl,cur.op)),dlt(P(cur.cl,cur.op),prv&&P(prv.cl,prv.op),1)]];
 el.innerHTML=`<div class="fl-k">${K.map(([l,txt,d,qh])=>`<div class="tile"><span class="eyebrow">${l}${qh?'<button type="button" class="qh" data-h="flowrev">?</button>':''}</span><span class="big">${txt}</span>${d}</div>`).join('')}</div>
 <div class="fl-types">${['Activation','Recovery','Retention','Win-back'].map(t=>{const L=ids.filter(id=>C[id].t===t),a=sum(L,0),pv=hasPrev?sum(L,FLP):null;return `<button type="button" class="fl-tc ${FLT===t?'on':''} ${FLT!=='all'&&FLT!==t?'dim':''}" data-t="${t}" style="--c:${FLC[t]}"><span class="fl-tn"><i></i>${t}<em>${L.length} kamp.</em></span><b>${zl(a.rv)}</b><span class="fl-ts">${f(a.cv)} konwersji · ${pf(a.rv,totRv)} przychodu firmy</span>${dlt(a.rv,pv&&pv.rv,1)}</button>`;}).join('')}</div>`;
 const NN=Math.max(FLP,7),s0=D0(F.start)+(E-NN+1)*864e5,ser=id=>C[id][FLM].slice(E-NN+1,E+1);
 const series=FLT==='all'?['Activation','Recovery','Retention','Win-back'].map(t=>({n:t,c:FLC[t],noscope:1,fmt:FLM==='r'?zl:f,d:(()=>{const L=ids.filter(id=>C[id].t===t).map(ser);return Array.from({length:NN},(_,i)=>L.reduce((a,x)=>a+(x[i]||0),0));})(),date:i=>dfmt(new Date(s0+i*864e5))}))
  :sel.slice().sort((a,b)=>st(b,0).rv-st(a,0).rv).slice(0,6).map((id,k)=>({n:C[id].n,c:['#e1306c','#161616','#ff8a5b','#9a9a9a','#7b5cff','#2fbf71'][k],noscope:1,fmt:FLM==='r'?zl:f,d:ser(id),date:i=>dfmt(new Date(s0+i*864e5))}));
 const mx=Math.max(1,...series.flatMap(x=>x.d));
 $('#fl-cht').innerHTML=`<h3>${FLM==='r'?'Przychód':'Konwersje'} z kampanii dzień po dniu${FLT==='all'?'':' · '+FLT+' (top 6)'}</h3><div class="p8sw fl-ms"><button class="chip" data-m="r" aria-pressed="${FLM==='r'}">Przychód</button><button class="chip" data-m="c" aria-pressed="${FLM==='c'}">Konwersje</button></div>`;
 lines($('#ch-fl'),series,[],0,Math.ceil(mx*1.1),'Kampanie dziennie',$('#leg-fl'));
 const allRv=Math.max(1,...ids.map(id=>st(id,0).rv));
 const row=id=>{const r=st(id,0),c=C[id];return `<div class="fr" data-camp="${id}"><div class="fr-n"><span title="${esc(c.n)} · ${c.ch}">${esc(c.n)}</span><i class="fl-st live" title="Działa" style="background:#2fbf71"></i></div><div class="fr-rv"><b>${zl(r.rv)}</b><span class="fr-bar"><em style="width:${Math.max(2,r.rv/allRv*100)}%"></em></span></div><div class="fr-v"><b>${p1(P(r.rv,totRv))}</b></div><div class="fr-v">${f(r.cv)}</div><div class="fr-v">${p1(P(r.cv,r.del))}</div><div class="fr-v">${f(r.sent)}</div><div class="fr-v">${p1(P(r.op,r.del))}</div><div class="fr-v">${p1(P(r.cl,r.op))}</div><div class="fr-v">${f(r.un)}</div></div>`;};
 $('#fl-rs').innerHTML=`<span class="fl-sum">Automatyzacje łącznie: <b>${zl(all.rv)}</b> z ${zl(totRv)} przychodu firmy · <b class="fl-sh">${p1(shr)}</b></span>${FLHID.length?`<button type="button" class="fl-restore">Przywróć ukryte (${FLHID.length})</button>`:''}`;
 const head='<div class="fr fr-h"><div class="fr-n">Kampania</div><div class="fr-rv">Przychód</div><div class="fr-v" title="Udział kampanii w całym przychodzie firmy w wybranym okresie">% przychodu firmy</div><div class="fr-v" title="Zakupy przypisane przez cel (Goal)">Konwersje</div><div class="fr-v">CR</div><div class="fr-v">Wysłane</div><div class="fr-v">OR</div><div class="fr-v">CTOR</div><div class="fr-v">Wypisy</div></div>';
 $('#fl-tab').innerHTML=`<div class="fl-bar" role="img" aria-label="Udział automatyzacji w przychodzie firmy">${['Activation','Recovery','Retention','Win-back'].map(t=>{const v=sum(ids.filter(id=>C[id].t===t),0).rv;return `<i style="flex:${v};background:${FLC[t]}" title="${t}: ${zl(v)}"></i>`;}).join('')}<i style="flex:${Math.max(0,totRv-all.rv)};background:var(--surface-2)" title="Pozostały przychód: ${zl(totRv-all.rv)}"></i></div><div class="fl-bl"><span>${['Activation','Recovery','Retention','Win-back'].map(t=>`<em><i style="background:${FLC[t]}"></i>${t}</em>`).join('')}<em><i style="background:var(--surface-2)"></i>pozostała sprzedaż</em></span><b>${p1(shr)} przychodu firmy z ${ids.length} automatyzacji</b></div>`+['Activation','Recovery','Retention','Win-back'].filter(t=>FLT==='all'||FLT===t).map(t=>{const L=ids.filter(id=>C[id].t===t).sort((a,b)=>st(b,0).rv-st(a,0).rv),a=sum(L,0);if(!L.length)return '';
  return `<div class="fl-blk"><div class="fl-bh"><div class="fl-bt"><span class="eyebrow">${t}</span><b>${zl(a.rv)}</b></div><div class="fl-bs"><span><b>${p1(P(a.rv,totRv))}</b>przychodu firmy</span><span><b>${f(a.cv)}</b>konwersje</span><span><b>${p1(P(a.op,a.del))}</b>OR</span><span><b>${p1(P(a.cl,a.op))}</b>CTOR</span><span><b>${L.length}</b>${L.length===1?'kampania':L.length<5?'kampanie':'kampanii'}</span></div></div>${head}${L.map(row).join('')}</div>`;}).join('');}
let FLHID=[];try{FLHID=JSON.parse(localStorage.getItem('fl-hid-demo')||'[]')}catch(e){}
const flSave=()=>{try{localStorage.setItem('fl-hid-demo',JSON.stringify(FLHID))}catch(e){}};
const flHide=(id,h)=>{FLHID=h?[...new Set([...FLHID,id])]:FLHID.filter(x=>x!==id);flSave();renderFlows();};
document.addEventListener('click',e=>{const b=e.target.closest('.fl-restore');if(!b)return;const ov=document.getElementById('hp-ov');ov.querySelector('.sc-mh b').textContent='Ukryte kampanie';
 document.getElementById('hp-b').innerHTML=`<p>Zaznacz kampanie, które chcesz przywrócić do raportu.</p><div class="rs-l">${FLHID.map(id=>{const c=FLOWS.c[id];return c?`<label class="rs-i"><input type="checkbox" value="${id}"><span><b>${esc(c.n)}</b><small>${c.t}</small></span></label>`:'';}).join('')}</div><div class="rs-a"><button type="button" class="rs-all">Zaznacz wszystkie</button><button type="button" class="rs-ok">Przywróć zaznaczone</button></div>`;
 ov.hidden=false;requestAnimationFrame(()=>ov.classList.add('on'));
 ov.querySelector('.rs-all').onclick=()=>ov.querySelectorAll('.rs-i input').forEach(x=>x.checked=true);
 ov.querySelector('.rs-ok').onclick=()=>{const sel=[...ov.querySelectorAll('.rs-i input:checked')].map(x=>x.value);if(!sel.length)return;FLHID=FLHID.filter(x=>!sel.includes(x));flSave();renderFlows();ov.classList.remove('on');setTimeout(()=>ov.hidden=true,200);};});
const FLC={Retention:'#e1306c',Activation:'#ff8a5b','Win-back':'#161616',Recovery:'#9a9a9a'};
const FLREC={Retention:[['Push „Twoja dieta kończy się jutro” dla 14% bez zgody na push','Odnowienie dzień przed końcem dociera tylko SMS-em do osób bez zgody push; prompt zgody po 1. zamówieniu dołoży zasięgu.']],
Activation:[['Lead z aplikacją, bez zamówienia','16 tys. leadów ma aplikację; seria push z gotową propozycją diety i ceną.']],
'Win-back':[['Przebudowa reaktywacji 61–90 i 90+','Testy holdout nie pokazują wzrostu sprzedaży: zmienić bodziec albo ograniczyć wysyłki i koszt.']],
Recovery:[['Porzucony koszyk: SMS po 24 h','Trzeci krok dla koszyków powyżej 1 000 zł, gdy e-mail i push nie zadziałały.']]};

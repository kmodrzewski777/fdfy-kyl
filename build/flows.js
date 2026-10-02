// ---------- kampanie
const CAMPS=[
 // id, nazwa, typ, kanał, przychód w 30 dni (tys. zł), AOV, wysyłki dziennie, OR, CTOR, wypisy / dostarczone, start
 ['a1','Powitanie nowego leada','Activation','e-mail',78,820,260,.58,.19,.004,'2025-06-02'],
 ['a2','Porzucony quiz dietetyczny','Activation','e-mail',64,940,95,.52,.24,.002,'2025-09-08'],
 ['a3','Zestaw próbny 3 dni','Activation','e-mail',41,340,120,.47,.17,.003,'2025-11-17'],
 ['a4','Lead bez zakupu 14 dni: kod startowy','Activation','e-mail',52,880,140,.44,.15,.004,'2025-08-25'],
 ['a5','Sprawdził dostawę, nie kupił','Activation','e-mail',33,960,55,.55,.22,.002,'2026-01-12'],
 ['a6','Onboarding przed startem dostawy','Activation','e-mail',18,420,45,.71,.26,.001,'2025-12-01'],
 ['a7','Instalacja aplikacji po 1. zamówieniu','Activation','e-mail',14,1050,38,.63,.21,.001,'2026-05-12'],
 ['a8','Re-engagement leadów przed sunsetem','Activation','e-mail',20,900,210,.21,.09,.006,'2026-03-23'],
 ['r1','Porzucony koszyk: e-mail po 1 h','Recovery','e-mail',168,1020,115,.54,.23,.002,'2025-06-02'],
 ['r2','Porzucony koszyk: push w aplikacji','Recovery','push',96,990,140,.13,.52,0,'2025-12-15'],
 ['r3','Porzucona płatność: przypomnienie po 1 h','Recovery','e-mail',112,1140,48,.63,.31,.001,'2025-10-06'],
 ['r4','Nieudana płatność: dokończ zamówienie','Recovery','SMS',41,1080,14,.72,.40,.001,'2026-04-20'],
 ['r5','Porzucona konfiguracja diety','Recovery','e-mail',33,1010,52,.49,.20,.002,'2026-02-09'],
 ['r6','Oglądał menu, nie zamówił','Recovery','push',20,980,160,.11,.36,0,'2026-06-08'],
 ['t1','Odnowienie diety: 3 dni przed końcem','Retention','e-mail',520,1190,240,.61,.27,.001,'2025-06-16'],
 ['t2','Odnowienie diety: dzień przed końcem','Retention','SMS + push',318,1120,210,.24,.45,.001,'2025-09-22'],
 ['t3','Drugi zakup przed końcem 1. dostawy','Retention','e-mail',236,1060,70,.66,.29,.001,'2025-07-07'],
 ['t4','Odnowienie zamówień 1–4-dniowych','Retention','e-mail',98,690,85,.57,.22,.002,'2026-07-15'],
 ['t5','Wypadli z rytmu (4+ zamówienia)','Retention','e-mail',152,1230,60,.58,.24,.002,'2025-10-20'],
 ['t6','Upsell na dłuższy pakiet (20+ dni)','Retention','e-mail',128,1780,95,.52,.18,.002,'2026-01-26'],
 ['t7','Ocena posiłków po 7 dniach','Retention','e-mail',46,1080,150,.64,.31,.001,'2025-11-03'],
 ['t8','Program poleceń dla lojalnych','Retention','e-mail',84,1020,55,.59,.21,.001,'2026-02-23'],
 ['t9','Podziękowanie po 5. i 10. zamówieniu','Retention','e-mail',58,1160,28,.74,.30,.001,'2026-01-05'],
 ['t10','Menu na nowy tydzień','Retention','push',72,1050,630,.11,.41,0,'2025-12-08'],
 ['t11','Urodziny klienta','Retention','e-mail',34,1140,30,.68,.33,.001,'2026-04-06'],
 ['t12','Zmiana diety: rekomendacja','Retention','e-mail',54,1150,65,.55,.19,.002,'2026-03-02'],
 ['w1','Bez dostawy 8–14 dni: wróć do diety','Win-back','e-mail',162,1080,45,.52,.21,.002,'2025-09-29'],
 ['w2','Zagrożeni 15–30 dni: benefit kwotowy','Win-back','e-mail',176,1040,72,.48,.19,.003,'2025-07-21'],
 ['w3','Reaktywacja 31–60 dni','Win-back','e-mail',118,990,80,.39,.16,.004,'2025-07-21'],
 ['w4','Reaktywacja 61–90 dni','Win-back','e-mail',64,960,66,.33,.14,.005,'2025-10-13'],
 ['w5','Utraceni 90+: ostatnia oferta','Win-back','e-mail',42,940,520,.19,.09,.008,'2025-11-24'],
 ['w6','VIP win-back: Czempioni i Lojalni','Win-back','e-mail + SMS',74,1480,12,.66,.28,.001,'2026-02-16'],
 ['w7','Ankieta po odejściu + oferta','Win-back','e-mail',24,980,50,.41,.22,.003]];
const FLOWS=(()=>{const start='2025-06-02',days=488,t0=D0(start),last=days-2;
 const SEA={1:1.06,2:1.04,3:1.01,4:.97,5:.95,6:.9,7:.86,8:.88,9:1,10:1.02,11:.97,12:.86},WDF=[1.09,1,.97,1.01,.95,.88,1.1];
 // dni ze świętami / przerwami i skala biznesu (start marki: czerwiec 2025)
 const OFF={'2025-12-24':.35,'2025-12-25':.2,'2025-12-26':.4,'2025-12-31':.55,'2026-01-01':.45,'2026-04-05':.4,'2026-04-06':.55,'2026-05-01':.7,'2026-05-03':.7,'2025-08-15':.7,'2026-08-15':.72,'2025-11-11':.75};
 const biz=i=>.36+.64*Math.min(1,Math.pow(i/last,.82));
 const rng=s=>()=>{s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};
 const sea=d=>{const m=d.getUTCMonth()+1,x=(d.getUTCDate()-15)/30,n=x>=0?m%12+1:(m+10)%12+1,w=Math.abs(x);return SEA[m]*(1-w)+SEA[n]*w;};
 const fac=i=>{const d=new Date(t0+i*864e5),k=d.toISOString().slice(0,10);return sea(d)*WDF[(d.getUTCDay()+6)%7]*(OFF[k]||1)*(i===days-1?.42:1);};
 const c={};CAMPS.forEach(([id,n,t,ch,rv,aov,snd,or,ctor,un,from],ci)=>{const R=rng(ci*7919+17),f0=from?Math.round((D0(from)-t0)/864e5):0,push=/push|SMS/.test(ch)&&!/e-mail/.test(ch);
  const A=[[],[],[],[],[],[]],cv=[],r=[],cb=rv*1000/aov/30,gap=R()<.25?Math.floor(f0+30+R()*(last-f0-60)):-99,gl=2+Math.floor(R()*4);
  for(let i=0;i<days;i++){if(i<f0){A.forEach(a=>a.push(0));cv.push(0);r.push(0);continue;}
   const g=biz(i)/biz(last-15),ramp=Math.min(1,Math.pow((i-f0+1)/56,.7)),stop=i>=gap&&i<gap+gl?.08:1,k=fac(i)*g*ramp*stop,nz=()=>.8+.4*R();
   let s=snd*k*nz();if(id==='t10'){const wd=new Date(t0+i*864e5).getUTCDay();s=wd===0?snd*7*g*ramp*nz()*(i===days-1?.42:1):0;}
   const lift=(.9+.16*R())*(1+.06*Math.sin(i/9.3+ci));
   const sent=Math.round(s),del=Math.round(sent*(push?.93+.03*R():.975+.015*R())),op=Math.round(del*or*(.94+.12*R())),cl=Math.round(op*ctor*(.9+.2*R()));
   const x=cb*k*nz()*lift,cc=Math.floor(x+R());
   A[0].push(sent);A[1].push(del);A[2].push(op);A[3].push(cl);A[4].push(Math.floor(del*un+R()));A[5].push((()=>{let q=0;for(let j=0;j<cc;j++)if(R()<.77)q++;return q;})());cv.push(cc);r.push(Math.round(cc*aov*(.9+.2*R())));}
  c[id]={n,t,ch,st:'running',m:A,c:cv,r};});
  const shape=Array.from({length:days},(_,i)=>fac(i)*biz(i));
 let cr=0,sh=0;for(let i=last-29;i<=last;i++){Object.values(c).forEach(x=>cr+=x.r[i]);sh+=shape[i];}
 const k=cr/.2617/sh,tot=shape.map(v=>Math.round(v*k));
 return {start,days,c,tot};})();
let FLP=7,FLT='all',FLM='r';
document.addEventListener('click',e=>{const t=e.target.closest('.fl-tc');if(t){FLT=FLT===t.dataset.t?'all':t.dataset.t;renderFlows();return;}
 const m=e.target.closest('.fl-ms .chip');if(m){FLM=m.dataset.m;renderFlows();}});
function renderFlows(){const el=document.getElementById('fl-kpi');if(!el)return;const F=FLOWS,C=F.c,ids=Object.keys(C).filter(id=>!FLHID.includes(id)),last=F.days-2,E=Math.max(0,last-Math.round(CUT));
 FLP=SCOPE?Math.min(SCOPE,E+1):E+1;
 const sw=(a,k,off)=>{let s=0;for(let i=E-off-k+1;i<=E-off;i++)if(i>=0)s+=a[i]||0;return s;};
 const st=(id,off)=>{const c=C[id];return {sent:sw(c.m[0],FLP,off),del:sw(c.m[1],FLP,off),op:sw(c.m[2],FLP,off),cl:sw(c.m[3],FLP,off),un:sw(c.m[4],FLP,off),ck:sw(c.m[5],FLP,off),cv:sw(c.c,FLP,off),rv:sw(c.r,FLP,off)};};
 const sum=(list,off)=>list.reduce((A,id)=>{const r=st(id,off);for(const k in r)A[k]+=(r[k]||0);return A;},{sent:0,del:0,op:0,cl:0,un:0,ck:0,cv:0,rv:0});
 const hasPrev=E-2*FLP+1>=0,P=(a,b)=>b?a/b*100:null,p1=v=>v==null?'—':(Math.round(v*10)/10).toFixed(1).replace('.',',')+'%';
 const sel=FLT==='all'?ids:ids.filter(id=>C[id].t===FLT),cur=sum(sel,0),prv=hasPrev?sum(sel,FLP):null,all=sum(ids,0);
 const dlt=(v,pv,good)=>{if(pv==null||v==null)return '<span class="dlt eq">—</span>';const ch=pv?((v-pv)/pv*100):0,up=v>=pv;return `<span class="dlt ${Math.abs(ch)<0.5?'eq':(up===!!good?'up':'dn')}">${up?'▲':'▼'} ${Math.abs(Math.round(ch))}%</span>`;};
 const K=[['Przychód',zl(cur.rv),dlt(cur.rv,prv&&prv.rv,1),1],['Śr. wartość zamówienia',f(cur.cv?cur.rv/cur.cv:0)+' zł',dlt(cur.cv?cur.rv/cur.cv:0,prv&&prv.cv?prv.rv/prv.cv:null,1)],['Konwersje',f(cur.cv),dlt(cur.cv,prv&&prv.cv,1)],['Wysłane',f(cur.sent),dlt(cur.sent,prv&&prv.sent,1)],['Open rate',p1(P(cur.op,cur.del)),dlt(P(cur.op,cur.del),prv&&P(prv.op,prv.del),1)],['CTOR',p1(P(cur.cl,cur.op)),dlt(P(cur.cl,cur.op),prv&&P(prv.cl,prv.op),1)]];
 el.innerHTML=`<div class="fl-k">${K.map(([l,txt,d,qh])=>`<div class="tile"><span class="eyebrow">${l}${qh?'<button type="button" class="qh" data-h="flowrev">?</button>':''}</span><span class="big">${txt}</span>${d}</div>`).join('')}</div>
 <div class="fl-types">${['Activation','Recovery','Retention','Win-back'].map(t=>{const L=ids.filter(id=>C[id].t===t),a=sum(L,0),pv=hasPrev?sum(L,FLP):null;return `<button type="button" class="fl-tc ${FLT===t?'on':''} ${FLT!=='all'&&FLT!==t?'dim':''}" data-t="${t}" style="--c:${FLC[t]}"><span class="fl-tn"><i></i>${t}<em>${L.length} kamp.</em></span><b>${zl(a.rv)}</b><span class="fl-ts">${f(a.cv)} konwersji · ${pf(a.rv,all.rv)} przychodu z kampanii</span>${dlt(a.rv,pv&&pv.rv,1)}</button>`;}).join('')}</div>`;
 const NN=Math.max(FLP,7),s0=D0(F.start)+(E-NN+1)*864e5,ser=id=>C[id][FLM].slice(E-NN+1,E+1);
 const series=FLT==='all'?['Activation','Recovery','Retention','Win-back'].map(t=>({n:t,c:FLC[t],noscope:1,fmt:FLM==='r'?zl:f,d:(()=>{const L=ids.filter(id=>C[id].t===t).map(ser);return Array.from({length:NN},(_,i)=>L.reduce((a,x)=>a+(x[i]||0),0));})(),date:i=>dfmt(new Date(s0+i*864e5))}))
  :sel.slice().sort((a,b)=>st(b,0).rv-st(a,0).rv).slice(0,6).map((id,k)=>({n:C[id].n,c:['#e1306c','#161616','#ff8a5b','#9a9a9a','#7b5cff','#2fbf71'][k],noscope:1,fmt:FLM==='r'?zl:f,d:ser(id),date:i=>dfmt(new Date(s0+i*864e5))}));
 const mx=Math.max(1,...series.flatMap(x=>x.d));
 $('#fl-cht').innerHTML=`<h3>${FLM==='r'?'Przychód':'Konwersje'} z kampanii dzień po dniu${FLT==='all'?'':' · '+FLT+' (top 6)'}</h3><div class="p8sw fl-ms"><button class="chip" data-m="r" aria-pressed="${FLM==='r'}">Przychód</button><button class="chip" data-m="c" aria-pressed="${FLM==='c'}">Konwersje</button></div>`;
 lines($('#ch-fl'),series,[],0,Math.ceil(mx*1.1),'Kampanie dziennie',$('#leg-fl'));
 const allRv=Math.max(1,...ids.map(id=>st(id,0).rv));
 const row=id=>{const r=st(id,0),c=C[id];return `<div class="fr" data-camp="${id}"><div class="fr-n"><span title="${esc(c.n)} · ${c.ch}">${esc(c.n)}</span><i class="fl-st live" title="Działa" style="background:#2fbf71"></i></div><div class="fr-rv"><b>${zl(r.rv)}</b><span class="fr-bar"><em style="width:${Math.max(2,r.rv/allRv*100)}%"></em></span></div><div class="fr-v">${f(r.ck)}</div><div class="fr-v">${f(r.cv)}</div><div class="fr-v">${p1(P(r.cv,r.del))}</div><div class="fr-v">${f(r.sent)}</div><div class="fr-v">${p1(P(r.op,r.del))}</div><div class="fr-v">${p1(P(r.cl,r.op))}</div><div class="fr-v">${f(r.un)}</div></div>`;};
 $('#fl-rs').innerHTML=`${FLHID.length?`<button type="button" class="fl-restore">Przywróć ukryte (${FLHID.length})</button>`:''}`;
 const head='<div class="fr fr-h"><div class="fr-n">Kampania</div><div class="fr-rv">Przychód</div><div class="fr-v" title="Konwersje według definicji ustawionej w samej kampanii">Konwersje kampanii</div><div class="fr-v" title="Zakupy przypisane przez cel (Goal)">Konwersje Goals</div><div class="fr-v">CR</div><div class="fr-v">Wysłane</div><div class="fr-v">OR</div><div class="fr-v">CTOR</div><div class="fr-v">Wypisy</div></div>';
 $('#fl-tab').innerHTML=['Activation','Recovery','Retention','Win-back'].filter(t=>FLT==='all'||FLT===t).map(t=>{const L=ids.filter(id=>C[id].t===t).sort((a,b)=>st(b,0).rv-st(a,0).rv),a=sum(L,0);if(!L.length)return '';
  return `<div class="fl-blk"><div class="fl-bh"><div class="fl-bt"><span class="eyebrow">${t}</span><b>${zl(a.rv)}</b></div><div class="fl-bs"><span><b>${f(a.cv)}</b>konwersje</span><span><b>${p1(P(a.op,a.del))}</b>OR</span><span><b>${p1(P(a.cl,a.op))}</b>CTOR</span><span><b>${L.length}</b>${L.length===1?'kampania':L.length<5?'kampanie':'kampanii'}</span></div></div>${head}${L.map(row).join('')}</div>`;}).join('');}
let FLHID=[];try{FLHID=JSON.parse(localStorage.getItem('fl-hid')||'[]')}catch(e){}
const flSave=()=>{try{localStorage.setItem('fl-hid',JSON.stringify(FLHID))}catch(e){}};
const flHide=(id,h)=>{FLHID=h?[...new Set([...FLHID,id])]:FLHID.filter(x=>x!==id);flSave();renderFlows();};
document.addEventListener('click',e=>{const b=e.target.closest('.fl-restore');if(!b)return;const ov=document.getElementById('hp-ov');ov.querySelector('.sc-mh b').textContent='Ukryte kampanie';
 document.getElementById('hp-b').innerHTML=`<p>Zaznacz kampanie, które chcesz przywrócić do raportu.</p><div class="rs-l">${FLHID.map(id=>{const c=FLOWS.c[id];return c?`<label class="rs-i"><input type="checkbox" value="${id}"><span><b>${esc(c.n)}</b><small>${c.t}</small></span></label>`:'';}).join('')}</div><div class="rs-a"><button type="button" class="rs-all">Zaznacz wszystkie</button><button type="button" class="rs-ok">Przywróć zaznaczone</button></div>`;
 ov.hidden=false;requestAnimationFrame(()=>ov.classList.add('on'));
 ov.querySelector('.rs-all').onclick=()=>ov.querySelectorAll('.rs-i input').forEach(x=>x.checked=true);
 ov.querySelector('.rs-ok').onclick=()=>{const sel=[...ov.querySelectorAll('.rs-i input:checked')].map(x=>x.value);if(!sel.length)return;FLHID=FLHID.filter(x=>!sel.includes(x));flSave();renderFlows();ov.classList.remove('on');setTimeout(()=>ov.hidden=true,200);};});
const FLC={Retention:'#e1306c',Activation:'#ff8a5b','Win-back':'#161616',Recovery:'#9a9a9a'};

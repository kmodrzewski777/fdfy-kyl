const aiHtml=()=>{const K=scoreK(),sc=scoreTot(K,'c'),sp=scoreTot(K,'p'),r1=v=>(Math.round(v*10)/10).toFixed(1).replace('.',','),F=FLOWS,last=F.days-2;
 let rv=0;for(let i=last-29;i<=last;i++)for(const id in F.c)rv+=F.c[id].r[i];
 const T=INC.tests,ok=T.filter(t=>t.sig),lift=ok.reduce((a,t)=>a+t.lift,0)/ok.length,L=STATIC.ladder,W=CHURN.wk,n=W.out.length,s4=(a,o)=>a.slice(n-4-o,n-o).reduce((x,y)=>x+y,0);
 const D=CHURN.day,b0=D[0]/BASE(Date.UTC(2026,7,7))*100,b1=D[D.length-1]/BASE(Date.UTC(2026,7,7)+(D.length-1)*864e5)*100,C=APP.cmp,lm=[150,650,2000,4500,8000,16500],av=b=>b.reduce((a,v,i)=>a+v*lm[i],0)/b.reduce((a,v)=>a+v,0);
 const r30=c=>c.r.slice(last-29,last+1).reduce((x,y)=>x+y,0),tr=Object.values(F.c).sort((a,b)=>r30(b)-r30(a)).slice(0,3).map(c=>c.n.split(':')[0].toLowerCase());
 return `<div class="ai-kpi"><div><b>${r1(sc)} / 10</b><span>scoring retencji, ${sc>=sp?'+':'−'}${r1(Math.abs(sc-sp))} m/m</span></div><div><b>${zl(rv)}</b><span>z automatyzacji w 30 dni</span></div><div><b>${ok.length} z ${T.length}</b><span>kampanii z wygranym testem holdout</span></div><div><b>${pf(APP.eat,APP.eat+APP.eatNoApp)}</b><span>jedzących dziś ma aplikację</span></div></div>
<h4>Gdzie jesteśmy mocni</h4>
<ul>
<li><b>Automatyzacje to filar sprzedaży.</b> ${Object.keys(F.c).length} kampanii automatycznych przyniosło w ostatnich 30 dniach ${zl(rv)}. Najwięcej dają: ${tr.join(', ')}.</li>
<li><b>Kampanie mają twardy dowód skuteczności.</b> W ${ok.length} z ${T.length} testów holdout grupa z kampanią kupuje istotnie częściej niż grupa kontrolna. Średni wzrost konwersji w działających kampaniach to ok. +${Math.round(lift*100)}%.</li>
<li><b>Drugi zakup powyżej średniej rynku.</b> ${pf(L[1].v,L[0].v)} klientów wraca po drugie zamówienie, a ${pf(L[6].v,L[5].v)} klientów z 6+ zamówieniami dochodzi do 10.</li>
<li><b>Stali klienci wracają.</b> Na 100 klientów z 2+ zamówieniami, którzy przekroczyli 30 dni bez dostawy, wraca ${Math.round(s4(W.back2,0)/s4(W.out2,0)*100)} (miesiąc wcześniej ${Math.round(s4(W.back2,4)/s4(W.out2,4)*100)}). W całej bazie, razem z jednorazowymi klientami, to ${Math.round(s4(W.back,0)/s4(W.out,0)*100)} na 100.</li>
<li><b>Aplikacja jako kanał retencji.</b> ${f(APP.users)} użytkowników, a klient z aplikacją ma ${r1(av(C.ltvB[0])/av(C.ltvB[1]))}× wyższe LTV niż klient bez niej.</li>
<li><b>Zdyscyplinowane rabaty.</b> Rabat to ${r1(SCORE.disc[1])}% wartości koszyka, a stali klienci (4+ zamówień) kupują z kodem rzadziej niż nowi.</li>
</ul>
<h4>Gdzie są rezerwy</h4>
<ul>
<li><b>Zgoda na push.</b> Ma ją ${pf(APP.pushCons,APP.users)} użytkowników aplikacji (${f(APP.pushCons)} osób). Każdy kolejny punkt procentowy to zasięg dla odnowień i porzuconych koszyków bez kosztu SMS.</li>
<li><b>Kampanie bez efektu w testach.</b> ${T.filter(t=>!t.sig).map(t=>t.n).join(', ')}: przychód przypisany w Goals klienci wygenerowaliby w dużej części sami.</li>
<li><b>Leady z aplikacją.</b> ${f(LEAD.app)} leadów ma aplikację, ale nie złożyło zamówienia. Brakuje dla nich osobnej ścieżki push.</li>
</ul>
<h4>Rekomendacje</h4>
<ul>
<li><b>Skalować to, co ma dowód.</b> Odnowienia, drugi zakup, wypadli z rytmu i VIP win-back: dołożyć kanał push i wariant SMS dla osób bez zgody push.</li>
<li><b>Przebudować reaktywację 61+ dni.</b> Zmienić bodziec (np. darmowy dzień próbny zamiast rabatu) i ograniczyć wysyłki do osób, które otwierały w 90 dni.</li>
<li><b>Prompt zgody push po 1. udanym zamówieniu</b>, z obietnicą przypomnienia o końcu diety.</li>
<li><b>Ocena posiłków bez celu sprzedażowego.</b> Zostawić ją jako źródło NPS i wiedzy o menu, bez kodu rabatowego.</li>
</ul>
<h4>Co tydzień patrzeć tylko na to</h4>
<ul><li>scoring retencji i jego składowe</li><li>przychód z automatyzacji tydzień do tygodnia</li><li>ilu stałych klientów wraca na 100 odchodzących</li><li>przejście 1. → 2. zamówienie</li><li>zgoda na push wśród użytkowników aplikacji</li><li>wyniki testów holdout</li></ul>`;};
(()=>{const btn=$('#ai-btn'),pan=$('#ai-pan'),x=$('#ai-x');if(!btn||!pan)return;
 const open=o=>{if(o){$('#ai-body').innerHTML=aiHtml();pan.hidden=false;requestAnimationFrame(()=>pan.classList.add('open'));}else{pan.classList.remove('open');setTimeout(()=>pan.hidden=true,260);}btn.setAttribute('aria-expanded',o);};
 btn.onclick=e=>{e.stopPropagation();open(pan.hidden);};x.onclick=()=>open(false);document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!pan.hidden)open(false);});
 document.addEventListener('click',e=>{if(!pan.hidden&&!e.target.closest('#ai-pan,#ai-btn,.sc-ov'))open(false);});})();

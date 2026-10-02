let AI={html:`
<div class="ai-kpi"><div><b>9,3 / 10</b><span>scoring retencji, +0,4 m/m</span></div><div><b>26%</b><span>przychodu firmy z automatyzacji</span></div><div><b>9 z 12</b><span>kampanii z dowodem w teście holdout</span></div><div><b>86%</b><span>jedzących dziś ma aplikację</span></div></div>
<h4>Gdzie jesteśmy mocni</h4>
<ul>
<li><b>Automatyzacje to filar sprzedaży.</b> 33 kampanie automatyczne przynoszą ok. 26% całego przychodu, czyli ok. 3,3 mln zł miesięcznie. Najwięcej dają odnowienia diety (3 dni i dzień przed końcem) oraz drugi zakup przed końcem 1. dostawy.</li>
<li><b>Kampanie mają twardy dowód skuteczności.</b> W 9 z 12 testów holdout (75%) grupa z kampanią kupuje istotnie częściej niż grupa kontrolna. Średni wzrost konwersji w działających kampaniach to ok. +30%.</li>
<li><b>Drugi zakup na poziomie liderów rynku.</b> 71% klientów wraca po drugie zamówienie, a 63% klientów z 6+ zamówieniami dochodzi do 10.</li>
<li><b>Bilans odpływu prawie zamknięty.</b> Na 100 osób, które przestają jeść, wraca 96 (miesiąc wcześniej ok. 90). Odsetek nieaktywnych w bazie spada z 88,6% do 86,0%.</li>
<li><b>Aplikacja jako kanał retencji.</b> 61 947 użytkowników, 86% jedzących dziś korzysta z aplikacji, a klient z aplikacją ma ok. 2,9× wyższe LTV niż klient bez niej.</li>
<li><b>Zdyscyplinowane rabaty.</b> Rabat to tylko 6,1% wartości koszyka, a stali klienci (4+ zamówień) kupują z kodem dwa razy rzadziej niż nowi.</li>
</ul>
<h4>Gdzie są rezerwy</h4>
<ul>
<li><b>Zgoda na push.</b> Ma ją 47,6% użytkowników aplikacji (29 492 osoby). Każdy kolejny punkt procentowy to zasięg dla odnowień i porzuconych koszyków bez kosztu SMS.</li>
<li><b>Reaktywacja głębokich nieaktywnych.</b> Kampanie dla 61–90 dni i 90+ nie pokazują wzrostu sprzedaży w teście holdout. Przychód przypisany w Goals klienci wygenerowaliby sami.</li>
<li><b>Leady z aplikacją.</b> 16 410 leadów ma aplikację, ale nie złożyło zamówienia. Brakuje dla nich osobnej ścieżki push.</li>
</ul>
<h4>Rekomendacje</h4>
<ul>
<li><b>Skalować to, co ma dowód.</b> Odnowienia, drugi zakup, wypadli z rytmu i VIP win-back: dołożyć kanał push i wariant SMS dla osób bez zgody push.</li>
<li><b>Przebudować reaktywację 61+ dni.</b> Zmienić bodziec (np. darmowy dzień próbny zamiast rabatu) i ograniczyć wysyłki do osób, które otwierały w 90 dni.</li>
<li><b>Prompt zgody push po 1. udanym zamówieniu</b>, z obietnicą przypomnienia o końcu diety.</li>
<li><b>Ocena posiłków bez celu sprzedażowego.</b> Kampania nie podnosi sprzedaży: zostawić ją jako źródło NPS i wiedzy o menu, bez kodu rabatowego.</li>
</ul>
<h4>Co tydzień patrzeć tylko na to</h4>
<ul><li>scoring retencji i jego składowe</li><li>udział automatyzacji w przychodzie firmy</li><li>ilu wraca na 100 odchodzących</li><li>przejście 1. → 2. zamówienie</li><li>zgoda na push wśród użytkowników aplikacji</li><li>wyniki testów holdout</li></ul>`};
(()=>{const btn=$('#ai-btn'),pan=$('#ai-pan'),x=$('#ai-x');if(!btn||!pan)return;
 const open=o=>{if(o){$('#ai-body').innerHTML=AI.html;pan.hidden=false;requestAnimationFrame(()=>pan.classList.add('open'));}else{pan.classList.remove('open');setTimeout(()=>pan.hidden=true,260);}btn.setAttribute('aria-expanded',o);};
 btn.onclick=e=>{e.stopPropagation();open(pan.hidden);};x.onclick=()=>open(false);document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!pan.hidden)open(false);});
 document.addEventListener('click',e=>{if(!pan.hidden&&!e.target.closest('#ai-pan,#ai-btn,.sc-ov'))open(false);});})();

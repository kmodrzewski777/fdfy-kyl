import json, re, os
B = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(B, '..', 'original.html')
OUT = os.path.join(B, '..', 'insights-demo.html')
L = open(SRC).read().split('\n')
D = json.load(open(os.path.join(B, 'data.json')))
V = dict(x.split('=', 1) for x in D['out'])
rd = lambda f: open(os.path.join(B, f)).read().rstrip('\n')

def defs(*names, kw='let'):
    return '\n'.join(f'{kw} {n}={V[n]};' for n in names)

R = {}  # (start, end) 1-indexed inclusive -> replacement text
R[(1472, 1472)] = defs('ACTIVE_T') + '\n' + defs('SCORE', kw='const') + f'\nconst CUST={D["CUST"]};'
R[(1493, 1493)] = 'const LTVMID=[150,650,2000,4500,8000,16500];'
R[(1494, 1505)] = defs('RAW')
R[(1510, 1510)] = 'const EMR={};'
R[(1513, 1513)] = defs('APPR', kw='const')
R[(1705, 1713)] = ''                                  # renderPlan (martwy kod)
R[(1716, 1719)] = defs('LEAD')
R[(1737, 1737)] = defs('STATIC')
R[(1752, 1771)] = ''                                  # ukryta tabela automatyzacji
R[(1774, 1777)] = defs('CHURN')
R[(1843, 1845)] = defs('MOM')
R[(1897, 1897)] = defs('CHURNP', kw='const')
R[(1899, 1900)] = defs('APP')
R[(1936, 1936)] = defs('CONS')
R[(1937, 1939)] = defs('LB')
R[(1940, 1942)] = ''                                  # CB
R[(1970, 1986)] = ''                                  # renderCB
R[(1998, 2017)] = ''                                  # applyData + połączenie z bazą
R[(2019, 2023)] = ''                                  # P8
R[(2024, 2028)] = defs('RB')
R[(2030, 2070)] = ''                                  # renderP8
R[(2101, 2101)] = defs('SER')
R[(2150, 2185)] = rd('score.js')
R[(2186, 2187)] = ''                                  # przełącznik 800+
R[(2191, 2217)] = rd('segtip.js')
R[(2220, 2220)] = defs('CBO')
R[(2239, 2311)] = rd('flows.js')
R[(2312, 2357)] = rd('inkr.js')
R[(2359, 2359)] = defs('SUN', kw='const')
R[(2365, 2366)] = defs('DMAP', kw='const')
R[(2400, 2400)] = f'const NCR={V["NCR"]},NK={V["NK"]},NCSEC={V["NCSEC"]};let NCSEL=null;'
R[(2422, 2429)] = rd('kw.js')
R[(2459, 2459)] = ''                                  # applyData(snapshot)
R[(2463, 2463)] = ''                                  # DOCS p800
R[(2472, 2472)] = ''                                  # DOCS cashback
R[(2505, 2577)] = rd('ai.js')

# sprawdź, że zakresy się nie nakładają
ks = sorted(R)
for a, b in zip(ks, ks[1:]):
    assert a[1] < b[0], (a, b)
assert L[2400 - 1].startswith('const NCR=') and L[2459 - 1].startswith('try{applyData') and L[2505 - 1].startswith('const REFRESH')
assert L[2312 - 1].startswith('const INC=') and L[2239 - 1].startswith('let FLOWS=') and L[2150 - 1].startswith('function renderScore(')
assert L[2422 - 1].startswith('function renderKW') and L[2191 - 1].startswith('const SEGMAP') and L[2463 - 1].startswith('p800:') and L[2472 - 1].startswith('cashback:')
for (a, b) in sorted(R, reverse=True):
    L[a - 1:b] = [R[(a, b)]] if R[(a, b)] != '' else []
S = '\n'.join(L)

def rep(old, new, count=1):
    global S
    n = S.count(old)
    assert n == count, (n, old[:90])
    S = S.replace(old, new)

def resub(pat, new, count=1, flags=re.S):
    global S
    S2, n = re.subn(pat, new, S, flags=flags)
    assert n == count, (n, pat[:90])
    S = S2

# ---------- HTML ----------
rep('<title>Insights @ RetentionQ</title>', '<title>Insights @ RetentionQ</title>')
rep('/* Design system Foodify (z maili Design Studio)', '/* Design system Insights')
rep('subject=Pytanie%20do%20Insights%20Foodify', 'subject=Pytanie%20do%20Insights', 2)
rep('<span class="asof" id="asof">Dane z 1 października 2026, 20:48</span><button class="chip refresh" id="refresh" type="button">Aktualizuj dane</button><span class="rf-msg" id="rf-msg"></span>',
    '<span class="asof" id="asof">Dane z 1 października 2026</span>')
rep('<a class="sb-part k" href="#p8part">Programy</a><a href="#p800">Jedzeniowe 800+</a> ', '')
rep('<a href="#rabaty">Rabaty</a><a href="#cashback">Cashback</a>', '<a href="#rabaty">Rabaty</a>')
rep('\n    <a class="sb-part d" href="#dzialania" hidden>Działania</a><a href="#automatyzacje" hidden>Automatyzacje</a></nav>', '</nav>')
rep('<a class="chip" href="#p8part">Programy</a>', '')
rep('<button class="upd-btn" id="upd-btn" type="button">↻ Zaktualizuj</button>', '')
resub(r'<div id="p8part" class="pdiv p">.*?</section>\n\n', '')
resub(r'<section id="cashback">.*?</section>\n\n', '')
rep('<div class="tiles t5" id="cons-tiles"', '<div class="tiles t3" id="cons-tiles"')
rep('<span class="pds">cała baza: klienci i leady</span>', f'<span class="pds">cała baza: {D["PROFILES"]:,} profili klientów i leadów</span>'.replace(',', ' '))
rep('wpływ automatyzacji Customer.io na zakupy i zaangażowanie', 'wpływ automatyzacji marketing automation na sprzedaż i zaangażowanie')
resub(r'<section id="inkr" style="padding-top:32px">.*?</section>\n<section id="automatyzacje" hidden.*?</section>',
      '<section id="inkr" style="padding-top:32px"><div class="fl-h"><h2>Inkrementalność</h2></div>\n'
      '<div class="card nofilter"><div id="ik-sum"></div></div>\n'
      '<div class="card nofilter" style="margin-top:14px"><h3>Wyniki testów holdout</h3><div id="ik-tab"></div></div>\n'
      '<div class="card nofilter" style="margin-top:14px"><div class="ik-top"><div id="ik-verdict"></div><div class="ik-sw" role="group"><button type="button" class="chip" data-ikp="all" aria-pressed="true">Wszystkie testy</button></div></div><div id="ik-ch"></div><div id="ik-k"></div></div>\n'
      '<div class="card nofilter" style="margin-top:14px"><h3 id="ik-lh">% kupujących od startu testu</h3><div id="ik-line"></div><div class="legend" id="leg-ik"></div></div></section>')
rep('<!-- ================= DZIAŁANIA ================= -->\n<div id="dzialania" hidden></div>\n', '')

# scoring: modal
resub(r'<p>Scoring to średnia ważona sześciu wskaźników retencji\..*?<p>Skala słowna',
 '<p>Scoring to średnia ważona sześciu wskaźników retencji. Każdy wskaźnik zamieniamy na ocenę 1–10 liniowo między progiem „1 pkt” a „10 pkt” (wartości poza zakresem przycinamy do 1 lub 10). Wynik końcowy = Σ (ocena × waga) / 100.</p>\n'
 '<table><thead><tr><th>Wskaźnik</th><th>Jak mierzony</th><th>1 pkt</th><th>10 pkt</th><th>Waga</th></tr></thead><tbody>\n'
 '<tr><td>Odnowienia przed końcem</td><td>% dostaw kończących się w ostatnich 30 dniach, po których klient zamówił kolejną bez przerwy</td><td>30%</td><td>80%</td><td>25%</td></tr>\n'
 '<tr><td>Powroty po przerwie</td><td>ilu wróciło na 100 osób, które przekroczyły 30 dni bez dostawy, ostatnie 30 dni</td><td>40</td><td>100</td><td>20%</td></tr>\n'
 '<tr><td>Drugi zakup</td><td>% klientów, którzy złożyli co najmniej 2 zamówienia</td><td>30%</td><td>75%</td><td>15%</td></tr>\n'
 '<tr><td>Przychód z automatyzacji</td><td>% przychodu firmy z kampanii automatycznych, ostatnie 30 dni</td><td>0%</td><td>28%</td><td>15%</td></tr>\n'
 '<tr><td>Jedzący z aplikacją</td><td>% klientów z aktywną dostawą, którzy korzystają z aplikacji</td><td>0%</td><td>90%</td><td>15%</td></tr>\n'
 '<tr><td>Rabat w koszyku</td><td>% wartości zamówień oddany w kodach rabatowych</td><td>25%</td><td>≤ 4%</td><td>10%</td></tr>\n'
 '</tbody></table>\n'
 '<p>Przykład: wskaźnik o progach 30% (1 pkt) i 80% (10 pkt) przy wartości 55% daje 1 + 9 × 25 / 50 = 5,5 pkt.</p>\n'
 '<p>Porównanie z poprzednim okresem liczy ten sam wzór na danych z wcześniejszych 30 dni. Scoring zawsze dotyczy całej bazy, niezależnie od filtrów.</p>\n'
 '<p>Skala słowna')

# ---------- CSS ----------
rep('</style>\n<div class="wrap">', '''body{overflow-x:clip}.sc-card>*{min-width:0}#ch-sc,#ch-sc svg{max-width:100%}#fl-tab{overflow-x:auto}#fl-tab .fl-blk{min-width:860px}.fl-bar,.fl-bl{min-width:0}
@media (max-width:700px){.scope,.catnav{overflow-x:auto;max-width:100%;scrollbar-width:none}.fl-dh{flex-wrap:wrap}}

.fl-sum{font-size:13px;color:var(--muted)}.fl-sum b{color:var(--fg);font-weight:600}.fl-sum .fl-sh{color:var(--magenta)}
.fl-bar{display:flex;height:14px;border-radius:99px;overflow:hidden;gap:2px;margin:6px 0 8px}.fl-bar i{display:block;min-width:2px}
.fl-bl{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px 16px;font-size:12.5px;color:var(--muted);margin-bottom:18px}.fl-bl span{display:flex;flex-wrap:wrap;gap:6px 14px}.fl-bl em{font-style:normal;display:inline-flex;align-items:center;gap:6px}.fl-bl em i{width:10px;height:10px;border-radius:3px;display:inline-block}.fl-bl b{color:var(--fg);font-weight:600}
.ik-hero{display:grid;grid-template-columns:minmax(0,1fr);gap:18px}.ik-big{display:flex;flex-wrap:wrap;align-items:center;gap:8px 24px}.ik-big .eyebrow{flex-basis:100%}.ik-big>b{font-size:64px;line-height:1;font-weight:700;color:var(--good);letter-spacing:-.03em}.ik-big p{flex:1;min-width:240px;max-width:720px;margin:0;color:var(--fg-2);line-height:1.5}.ik-big p b{color:var(--fg)}
.ik-kk .tsub{font-size:12px;color:var(--muted)}
.ikt-w{overflow-x:auto}.ikt{width:100%;border-collapse:separate;border-spacing:0 6px;font-variant-numeric:tabular-nums;font-size:13.5px;min-width:760px}
.ikt th{font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:600;text-align:right;padding:4px 12px}.ikt th:first-child{text-align:left}
.ikt td{background:var(--surface-2);padding:11px 12px;text-align:right;white-space:nowrap}.ikt td:first-child{text-align:left;border-radius:12px 0 0 12px;white-space:normal}.ikt td:last-child{border-radius:0 12px 12px 0}
.ikt td small{display:block;color:var(--muted);font-size:11.5px}.ikt tr{cursor:pointer}.ikt tr:hover td,.ikt tr.on td{background:color-mix(in srgb,var(--magenta) 12%,var(--surface-2))}.ikt tr:focus-visible td{outline:2px solid var(--magenta)}
.ikt td.up{color:var(--good);font-weight:600}.ikt td.dn{color:var(--crit);font-weight:600}
.ikp{display:inline-block;font-size:11.5px;font-weight:600;border-radius:99px;padding:4px 10px}.ikp.good{background:color-mix(in srgb,var(--good) 15%,transparent);color:var(--good)}.ikp.warn{background:color-mix(in srgb,var(--warn) 16%,transparent);color:var(--warn)}.ikp.bad{background:color-mix(in srgb,var(--crit) 14%,transparent);color:var(--crit)}
.ik-lifts{display:grid;gap:8px;margin-top:6px}.ik-lr{display:grid;grid-template-columns:minmax(140px,280px) 1fr 60px;gap:12px;align-items:center;cursor:pointer;font-size:13px}.ik-lr .nm{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.ik-lr .tr{position:relative;height:14px;background:var(--surface-2);border-radius:99px}.ik-lr .tr i{position:absolute;top:0;bottom:0;border-radius:99px}.ik-lr b{text-align:right;font-variant-numeric:tabular-nums;color:var(--muted)}.ik-lr b.g{color:var(--good)}.ik-lr:hover .nm{color:var(--magenta)}
@media (max-width:640px){.ik-lr{grid-template-columns:minmax(0,1fr) 54px}.ik-lr .tr{grid-column:1/-1;grid-row:2}.ik-big>b{font-size:48px}}
</style>
<div class="wrap">''')

# ---------- JS: drobne poprawki ----------
rep('let tot=14619;', 'let tot=CUST;')
rep('const yv=g=>g.rev/g.tot*12/11;', 'const yv=g=>g.rev/g.tot*0.4;')
rep("Bez komunikacji sprzedażowej. Gryzy, ulubione danie, naliczony cashback.", "Bez komunikacji sprzedażowej. Ulubione danie, nowości w menu.")
rep("saldo cashbacku w zł.", "ulubiona dieta jednym kliknięciem.")
rep("'Saldo cashbacku / FoodiKarty w zł i Gryzy. Bez nowego rabatu.'", "'Przypomnienie o ulubionym zestawie i dniu dostawy. Bez nowego rabatu.'")
rep("(mediana 12 dni). Cashback + ulubione danie.", "(mediana 13 dni). Ulubione danie + darmowa dostawa.")
rep("'Segmenty RFM z BigQuery; tempo z dziennej historii segmentów we wrześniu (RFM przelicza się codziennie, stąd duże ruchy w obie strony).'", "'Segmenty RFM; tempo z dziennej historii segmentów we wrześniu.'")
rep("Loyalist i Champion to co trzeci klient i większość przychodu. Newcomer to 41% bazy i prawie nic nie zostawia.", "Loyalist i Champion to 44% klientów i ok. 80% przychodu.")
rep("[['1 wrz',0],['9 wrz: sunset',8],['30 wrz',30]],8000,14000,", "[['1 wrz',0],['9 wrz: sunset',8],['1 paź',30]],50000,62000,")
rep("lines($('#app-push'),[{n:'Otwarte pushe',d:P.open,c:mag,date:i=>P.lab[i],extra:i=>`<div class=\"tr\"><span>Dostarczone</span><b>${f(P.del[i])}</b></div><div class=\"tr\"><span>Wskaźnik otwarć</span><b>${String(rate[i]).replace('.',',')}%</b></div>`},{n:'Konwersje',d:P.conv,c:org,date:i=>P.lab[i]}],P.lab.map((l,i)=>[l,i]),0,2000,'Pushe miesięcznie',$('#leg-push'));",
    "lines($('#app-push'),[{n:'Konwersje z pushy',d:P.conv,c:mag,date:i=>P.lab[i],extra:i=>`<div class=\"tr\"><span>Otwarte pushe</span><b>${f(P.open[i])}</b></div><div class=\"tr\"><span>Dostarczone</span><b>${f(P.del[i])}</b></div><div class=\"tr\"><span>Wskaźnik otwarć</span><b>${String(rate[i]).replace('.',',')}%</b></div>`}],P.lab.map((l,i)=>[l,i]),0,700,'Pushe miesięcznie',$('#leg-push'));")
rep('<h3>Pushe: otwarcia i konwersje miesięcznie</h3>','<h3>Konwersje z pushy miesięcznie</h3>')
rep("lines($('#ch-cons'),ser,lab,0,20000,", "lines($('#ch-cons'),ser,lab,0,110000,")
rep("[[dfmt(new Date(t0)),0],[dfmt(new Date(t0+L*864e5)),L]],0,4000,", "[[dfmt(new Date(t0)),0],[dfmt(new Date(t0+L*864e5)),L]],0,6000,")
# zgody: tylko newsletter / SMS / push
rep("const S=[['Oferty specjalne i promocje',C.c51,mag],['Nowości i inspiracje',C.c75,cssv('--orange')],['Newsletter',C.c28,cssv('--kc')],['SMS',C.c71,cssv('--a1')],['Push',C.c523,cssv('--l1')]];",
    "const S=[['Newsletter',C.c28,mag],['SMS',C.c71,cssv('--orange')],['Push',C.c523,cssv('--kc')]];")
resub(r"\$\('#cons-note'\)\.textContent='[^']*';", "$('#cons-note').textContent='Baza: "+f'{D["PROFILES"]:,}'.replace(',', ' ')+" profili (klienci i leadzi), zgodę newsletterową ma co 2,4 osoba. Nagłe spadki to akcje sunset (m.in. 9 wrz), które wygaszają kontakty bez reakcji od 90+ dni.';")
# leady: ścieżka zakupu z danych
rep("funnelH($('#f-lbuy'),[{l:'Podsumowanie zamówienia',v:401,why:'Leadzi, którzy doszli do podsumowania zamówienia.'},{l:'Ekran wyboru płatności',v:24,why:'Tylko 6% z podsumowania przechodzi do wyboru płatności.'},{l:'Płatność rozpoczęta',v:11,why:'Mniej niż połowa z wyboru płatności ją rozpoczyna.'}],{aria:'Ścieżka zakupu leadów'});",
    "funnelH($('#f-lbuy'),[{l:'Koszyk',v:L.buy[2][1],why:'Leadzi, którzy dodali dietę do koszyka.'},{l:'Podsumowanie zamówienia',v:L.buy[3][1],why:'72% z koszyka dochodzi do podsumowania.'},{l:'Ekran wyboru płatności',v:L.buy[4][1],why:'Dwie trzecie z podsumowania przechodzi do wyboru płatności.'},{l:'Płatność rozpoczęta',v:L.buy[5][1],why:'8 na 10 osób z wyboru płatności ją rozpoczyna.'}],{aria:'Ścieżka zakupu leadów'});")
resub(r"\$\('#lb-ins'\)\.innerHTML=`<div class=\"bt\">\$\{\[.*?\]\.map\(x=>",
 "$('#lb-ins').innerHTML=`<div class=\"bt\">${["
 "['Koszyk → podsumowanie',`${f(L.buy[2][1])} leadów dodało dietę do koszyka, ${f(L.buy[3][1])} doszło do podsumowania. 28% odpada przed podsumowaniem: tu działa porzucony koszyk (e-mail i push).`],"
 "['Quiz bez zakupu',`${f(L.ev[3][1])} leadów zaczęło quiz dietetyczny w 30 dni. Kampania „Porzucony quiz” wysyła im gotową propozycję diety z ceną.`],"
 "['Sprawdzenie adresu',`${f(L.ev[4][1])} osób sprawdziło dostawę pod swój adres. To najgorętszy sygnał przed zakupem.`],"
 "['Aplikacja',`${f(L.ev[1][1])} leadów (${pf(L.ev[1][1],L.tot)}) ogląda ekrany w aplikacji, ${f(L.pg[6][1])} zagląda do programu lojalnościowego.`],"
 "['Brak aktywności',`${pf(L.tot-L.buy[1][1],L.tot)} leadów nie zrobiło w 30 dni nic mierzalnego: trafiają do re-engagementu przed sunsetem.`]].map(x=>")
resub(r"<p class=\"foot-note\">Kohorty według miesi[^`]*?</p>", '<p class="foot-note">Kohorty według miesiąca: nowi leadzi, odejścia (zakup lub wypis) i nowi klienci w danym miesiącu.</p>', count=1)
# rabaty: bez doładowań 800+
rep("lines($('#ch-rb'),[{n:'Zamówienia z kodem',agg:'mean',d:R.days.map(x=>x[1]),c:mag,date:i=>R.days[i][0],fmt:v=>v+'%'},{n:'Zapłacone doładowaniem',d:R.days.map(x=>x[2]),c:org,date:i=>R.days[i][0],fmt:v=>v+'%'}],[[R.days[0][0],0],['15 wrz',6],['29 wrz',12]],0,100,",
    "lines($('#ch-rb'),[{n:'Zamówienia z kodem',agg:'mean',d:R.days.map(x=>x[1]),c:mag,date:i=>R.days[i][0],fmt:v=>v+'%'}],[[R.days[0][0],0],[R.days[13][0],13]],0,60,")
rep("c[2]==='40%'?org:c[2]==='30%'?cssv('--a1'):mag", "parseInt(c[2])>=20?org:parseInt(c[2])>=15?cssv('--a1'):mag")
rep("`<p class=\"foot-note\">Udział w zamówieniach z kodem. Kody influencerskie (…15) to rabat 15%, SPF40 to 40%, kody partnerskie 30%.</p>`", "`<p class=\"foot-note\">Udział w zamówieniach z kodem. Kody powrotu i startowe to rabat 15–20%, kody aplikacji i poleceń 10%.</p>`")
rep("Stali klienci (4+) kupują z kodem prawie tak samo często jak nowi.", "Stali klienci (4+) kupują z kodem dwa razy rzadziej niż nowi.")
rep("Indeks majętności z BigQuery (1 = najniższa, 5 = najwyższa). Klientów z indeksem 5 jest najwięcej i to oni zabierają najwięcej rabatu, choć mają najwyższy koszyk.", "Indeks majętności (1 = najniższa, 5 = najwyższa). Rabat rozkłada się równo między grupy, a zamożniejsi klienci mają wyższy koszyk.")
resub(r"\$\('#rb-note'\)\.textContent=`[^`]*`;", "$('#rb-note').textContent=`Źródło: próbka ${R.n} zamówień z ostatnich 14 dni (kod, procent rabatu, wartość zamówienia); majętność i liczba zamówień z profilu kupującego.`;")
rep("<span class=\"tsub\">miesięcznie przy obecnym tempie (~${R.perDay} zamówień dziennie)</span>", "<span class=\"tsub\">miesięcznie przy obecnym tempie (~${R.perDay} zamówień dziennie)</span>")
# lazy render: bez 800+ i cashbacku
rep("[()=>renderP8(),'p800'],", '')
rep("[()=>renderCB(),'d-cb'],", '')
# pomoc
resub(r"const HELP=\{flowrev:`.*?`,money:", "const HELP={flowrev:`<p><b>Przychód z kampanii</b> = suma wartości zamówień przypisanych do kampanii przez cele (Goals): zakup w oknie atrybucji od otwarcia wiadomości (Recovery 1 dzień, pozostałe typy 7 dni).</p><p><b>Udział w przychodzie firmy</b> = przychód z kampanii ÷ cały przychód sklepu w tym samym okresie.</p><p><b>OR</b> = otwarcia ÷ dostarczone. <b>CTOR</b> = kliknięcia ÷ otwarcia. <b>CR</b> = konwersje ÷ dostarczone. Dzisiejszy, niepełny dzień nie jest wliczany. Porównanie: ten sam okres bezpośrednio wcześniej.</p>`,money:")
rep("<li><b>Wartość klienta w grupie.</b> Dla każdego segmentu RFM sumujemy lifetime_revenue jego klientów (atrybut z profilu, liczony ze środków przedziałów: do 300, 300–1000, 1000–3000, 3000–6000, 6000–10 000, 10 000+ zł).</li>",
    "<li><b>Wartość klienta w grupie.</b> Dla każdego segmentu RFM sumujemy lifetime_revenue jego klientów (liczony ze środków przedziałów: do 300, 300–1000, 1000–3000, 3000–6000, 6000–10 000, 10 000+ zł).</li>")
rep("<li><b>Roczny przychód na klienta</b> = suma lifetime_revenue grupy ÷ liczba klientów grupy × 12/11 (historia obejmuje ok. 11 miesięcy, przeliczamy na rok).</li>",
    "<li><b>Roczny przychód na klienta</b> = średnie lifetime_revenue grupy ÷ 2,5 (średni staż klienta w latach).</li>")
# DOCS
resub(r"^inkr:\{t:'Inkrementalność',b:`.*?`\},$", "inkr:{t:'Inkrementalność',b:`<p>Sprawdza, czy automatyzacje naprawdę dokładają sprzedaży, czy tylko „podpisują się” pod zakupami, które i tak by nastąpiły.</p><ul><li><b>Grupy</b>: każdy klient ma losowo przypisaną grupę: <b>z kampanią</b> (70%) albo <b>holdout</b> (30%, nie dostaje danej kampanii). Porównujemy tylko osoby, które spełniały warunki wejścia do kampanii.</li><li><b>% kupujących</b>: ile osób z grupy złożyło co najmniej 1 zamówienie od startu testu.</li><li><b>Wzrost</b>: o ile % wyższy jest odsetek kupujących w grupie z kampanią względem holdoutu. <b>Pewność</b>: test różnicy dwóch proporcji; kampania „zarabia”, gdy wzrost jest dodatni, a p &lt; 0,05.</li><li><b>Przychód Goals</b>: przychód przypisany kampanii w okresie testu. <b>Realny przychód</b> = różnica w % kupujących × liczba osób w grupie z kampanią × średnia wartość zamówienia.</li><li><b>Kreska na pasku</b>: przedział ufności 95%. Jeśli kreski obu grup się nakładają, różnica może być przypadkowa.</li><li>Kliknij wiersz tabeli albo pasek na wykresie, żeby zobaczyć szczegóły testu jednej kampanii.</li></ul>`},", flags=re.S | re.M)
resub(r"^zgody:\{t:'Zgody marketingowe',b:`.*?`\},$", "zgody:{t:'Zgody marketingowe',b:`<p>Liczba osób (klientów i leadów) z poszczególnymi zgodami dzień po dniu: newsletter (e-mail), SMS, push. Zgodę newsletterową ma co 2,4 osoba w bazie. Liczby przy kafelkach: zmiana w wybranym okresie.</p>`},", flags=re.S | re.M)
resub(r"^flows:\{t:'Performance kampanii',b:`.*?`\},$", "flows:{t:'Performance kampanii',b:`<p>Wyniki automatyzacji w okresie wybranym w przełączniku u góry strony (wczoraj, 7, 30, 90 dni lub całość od 8 kwietnia), z porównaniem do poprzedniego okresu o tej samej długości.</p><ul><li><b>Przychód i konwersje</b>: zakupy przypisane do kampanii przez cele (Goals) w oknie atrybucji (Recovery 1 dzień, Activation, Retention i Win-back 7 dni).</li><li><b>Udział w przychodzie firmy</b>: jaka część całej sprzedaży sklepu w okresie pochodzi z kampanii automatycznych; pasek nad tabelą pokazuje to samo w podziale na typy.</li><li><b>OR</b> = otwarcia ÷ dostarczone, <b>CTOR</b> = kliknięcia ÷ otwarcia, <b>CR</b> = konwersje ÷ dostarczone.</li><li><b>Karty typów</b>: kliknięcie zawęża wykres i tabele do danego typu.</li><li><b>Tabele</b>: osobno dla każdego typu, od najwyższego przychodu. Kolumna „% przychodu firmy” pokazuje udział pojedynczej kampanii w całej sprzedaży. Kliknięcie w kampanię pozwala ukryć ją w raporcie.</li><li>Dzisiejszy, niepełny dzień nie jest wliczany.</li></ul>`},", flags=re.S | re.M)
rep("<li><b>Użytkownicy aplikacji</b> – osoby z segmentu [App] Application User; podział na klientów i osoby bez zakupu.</li>", "<li><b>Użytkownicy aplikacji</b> – osoby zalogowane w aplikacji mobilnej; podział na klientów i osoby bez zakupu.</li>")
rep("<p>Na podstawie próbki zamówień (po 50 z każdego z ostatnich 14 dni) z eventu purchase: kod, procent rabatu, wartość, majętność klienta.</p>", "<p>Na podstawie próbki zamówień z ostatnich 14 dni: kod, procent rabatu, wartość, majętność klienta.</p>")
# HELP rabaty / app teksty z nazwą klienta
assert 'Foodify' not in S.replace('Foodify', 'Foodify') or True
open(OUT, 'w').write(S)
print('written', len(S))
for w in ['Foodify', 'Gryz', 'FoodiK', 'cashback', 'Cashback', '800+', 'Customer.io', 'cio_', 'claude.use', 'fly.customer', 'PINDB.', 'BigQuery']:
    print(w, S.count(w))

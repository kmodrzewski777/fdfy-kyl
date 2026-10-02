"""Generator spójnych danych demonstracyjnych dla dashboardu Insights (wersja demo).

Model bazy (wszystko się z niego wyprowadza):
  profile łącznie 235 858 = 98 274 zgód newsletter x 2,4
  klienci 54 820, leadzi (zgoda e-mail, bez zakupu) 58 762
  jedzący dziennie ~5,2 tys. x ~80 zł/dzień = ~150 mln zł przychodu rocznie
"""
import json, math, random
from datetime import date, timedelta

R = random.Random(20261001)
def J(x): return json.dumps(x, ensure_ascii=False, separators=(',', ':'))

ASOF = date(2026, 10, 1)
CUST = 54820
NEWS, SMS, PUSH = 98274, 68318, 29492
PROFILES = round(NEWS * 2.4)          # 235 858
LEADS = 58762
APP_USERS = 61947

def noise(a): return 1 + R.uniform(-a, a)
def season(d):
    # sezonowość branży: lato słabsze, wrzesień mocny (powrót do formy)
    m = {1: 1.08, 2: 1.04, 3: 1.03, 4: 0.98, 5: 0.97, 6: 0.93, 7: 0.88, 8: 0.9, 9: 1.0, 10: 1.02, 11: 0.98, 12: 0.85}
    return m[d.month]
WD = [1.06, 1.0, 0.98, 1.01, 0.97, 0.95, 1.03]  # pn..nd

# ---------------- segmenty RFM / lojalność ----------------
# r = [e03,e47,teraz,d07,d814,d1530,d3160,d6190,d90,email,sms,push,app]
RFM = [
 dict(k='R1', n='Czempioni', d='RFM 14–15', c='--c-r1', tot=4900, st=[640,530,2950,300,200,290,420,230,510], ch=[4060,4250,3450,4560], ltv=[0,0,120,700,1380,2700]),
 dict(k='R2', n='Lojalni', d='RFM 11–13', c='--c-r2', tot=8700, st=[340,290,1560,260,200,360,760,560,5000], ch=[6960,7310,4950,7570], ltv=[0,150,1200,2500,2650,2200]),
 dict(k='R3', n='Obiecujący', d='RFM 8–10', c='--c-r3', tot=11600, st=[140,110,580,170,150,330,700,640,9030], ch=[8820,9050,5110,9280], ltv=[100,1300,3900,3700,1800,800]),
 dict(k='R4', n='Okazjonalni', d='RFM 5–7', c='--c-r4', tot=15900, st=[25,20,90,40,50,120,420,470,14710], ch=[11130,11920,5230,11450], ltv=[1600,5600,6000,2000,520,180]),
 dict(k='R5', n='Utraceni', d='RFM 3–4', c='--c-r5', tot=13720, st=[0,0,0,0,0,0,0,0,13720], ch=[8542,9340,2900,8370], ltv=[4800,7000,1780,140,0,0]),
]
LOY = [
 dict(k='NEW', n='Newcomer', d='1 zamówienie', c='--c-new', tot=15900, st=[110,90,480,70,70,120,410,340,14410], ch=[10292,11070,4090,9680], ltv=[5600,7900,2200,200,0,0], extra=dict(**{'in': 39, 'out': 28})),
 dict(k='POT', n='Potential Loyalist', d='2–3 zamówienia', c='--c-pot', tot=14600, st=[150,130,640,150,130,260,610,560,12250], ch=[10370,11000,5050,10700], ltv=[600,5200,6800,1800,200,0], extra={'in': 28}),
 dict(k='LOY', n='Loyalist', d='4–9 zamówień', c='--c-loy', tot=14200, st=[345,280,1560,250,200,380,760,620,10430], ch=[10650,11200,6400,11500], ltv=[0,300,3900,5600,3300,1100], extra={}),
 dict(k='CHA', n='Champion', d='10+ zamówień', c='--c-cha', tot=10120, st=[540,450,2500,300,200,340,520,380,5880], ch=[8200,8600,6100,9350], ltv=[0,0,300,2100,3470,4250], extra={}),
]
for grp in (RFM, LOY):
    for g in grp:
        s = g['st']
        assert s[2] + sum(s[3:9]) == g['tot'], g['k']
        assert sum(g['ltv']) == g['tot'], g['k']
    for j in range(9):
        pass
for j in range(9):
    assert sum(g['st'][j] for g in RFM) == sum(g['st'][j] for g in LOY), j
for j in range(4):
    assert sum(g['ch'][j] for g in RFM) == sum(g['ch'][j] for g in LOY), j
assert sum(g['tot'] for g in RFM) == CUST
EAT = sum(g['st'][2] for g in RFM)          # 5180
CH_TOT = [sum(g['ch'][j] for g in RFM) for j in range(4)]  # email, sms, push, app

# historia RFM we wrześniu (30 dni)
starts = {'R1': 4690, 'R2': 8480, 'R3': 11420, 'R4': 15620, 'R5': 13407}
ein = {'R1': 64, 'R2': 118, 'R3': 236, 'R4': 312, 'R5': 152}
for g in RFM:
    a, b = starts[g['k']], g['tot']
    hist = []
    for i in range(30):
        v = a + (b - a) * i / 29 + (R.uniform(-0.0025, 0.0025) * b if 0 < i < 29 else 0)
        hist.append(round(v))
    g['hist'] = hist
    net = (b - a) / 29
    e = [max(1, round(ein[g['k']] * noise(0.18))) for _ in range(30)]
    g['e'] = e
    g['l'] = [max(0, round(x - net + R.uniform(-4, 4))) for x in e]

def seg_js(g):
    o = dict(k=g['k'], n=g['n'], d=g['d'], c=g['c'], tot=g['tot'], r=g['st'] + g['ch'], ltv=g['ltv'])
    if 'hist' in g: o.update(hist=g['hist'], e=g['e'], l=g['l'])
    if g.get('extra'): o.update(g['extra'])
    return o
RAW = dict(loy=[seg_js(g) for g in LOY], rfm=[seg_js(g) for g in RFM])

# podział na aplikację (IPF: wiersze = segment app, kolumny = stany)
def ipf(groups):
    st_ratio = [0.875, 0.87, 0.86, 0.82, 0.8, 0.78, 0.76, 0.75, 0.728]
    out = {}
    for g in groups:
        m = [g['st'][j] * st_ratio[j] for j in range(9)]
        out[g['k']] = m
    target_col = [sum(g['st'][j] for g in groups) * st_ratio[j] for j in range(9)]
    for _ in range(60):
        for g in groups:
            row = out[g['k']]; s = row[2] + sum(row[3:9]); f = g['ch'][3] / s if s else 0
            out[g['k']] = [v * f for v in row]
        for j in range(9):
            s = sum(out[g['k']][j] for g in groups); f = target_col[j] / s if s else 0
            for g in groups: out[g['k']][j] *= f
    res = {}
    for g in groups:
        row = [min(round(v), g['st'][j]) for j, v in enumerate(out[g['k']])]
        row[0] = min(row[0], row[2]); row[1] = min(row[1], row[2] - row[0])
        tot = row[2] + sum(row[3:9]); row[8] += g['ch'][3] - tot
        res[g['k']] = [g['ch'][3]] + row
    return res
APPR = {**ipf(LOY), **ipf(RFM)}
APP_EAT = sum(APPR[g['k']][3] for g in RFM)
APP_INACT = sum(sum(APPR[g['k']][7:10]) for g in RFM)

# ---------------- dzienne serie ----------------
def days(a, b):
    d = a
    while d <= b:
        yield d; d += timedelta(1)

# nowi klienci od 1 lipca do 1 października
newc = []
for d in days(date(2026, 7, 1), ASOF):
    base = 33 + (d - date(2026, 7, 1)).days * 0.07
    newc.append(max(10, round(base * season(d) / 0.92 * WD[d.weekday()] * noise(0.16))))
# korekta: ostatnie 30 dni ~1168
s30 = sum(newc[-30:]); newc = newc[:-30] + [round(v * 1168 / s30) for v in newc[-30:]]
newc_dates = list(days(date(2026, 7, 1), ASOF))

def base_at(d):
    tot = CUST
    for dd, v in zip(newc_dates, newc):
        if dd > d: tot -= v
    return tot

# jedzący dziennie 6.07 → 1.10 (88 dni); śr. wrzesień ~5150
ACTIVE_T = []
for d in days(date(2026, 7, 6), ASOF):
    lvl = 4700 * season(d) / 0.9 if d.month < 9 else 5000 + (d.day) * 6.5
    if d.month == 8: lvl = 4650 + d.day * 4
    if d.month == 7: lvl = 4590 - d.day * 1.5
    if d.month == 10: lvl = 5180
    ACTIVE_T.append(round(lvl * (1 + 0.012 * math.sin(d.toordinal() / 1.1)) * noise(0.006)))
ACTIVE_T[-1] = EAT

# nieaktywni dziennie od 7.08 (56 dni)
inact = []
v = 46707
for i, d in enumerate(days(date(2026, 8, 7), ASOF)):
    inact.append(round(v + R.uniform(-6, 6)))
    v += 13 if d < date(2026, 9, 3) else 4
inact[-1] = sum(sum(g['st'][6:9]) for g in RFM)
# rozciągnij liniowo, żeby trafić w 47 170
k0 = inact[0]; kN = inact[-1]

WK = dict(lab=['16 lip','23 lip','30 lip','6 sie','13 sie','20 sie','27 sie','3 wrz','10 wrz','17 wrz','24 wrz'],
          out=[520,535,548,510,506,497,503,492,478,501,470],
          back=[446,452,470,451,455,447,460,470,462,481,452])

LADDER = [54820, 38920, 30820, 24320, 19720, 16120, 10120]
CBO = dict(lab=['1','2','3','4','5','6–9','10+'], tot=[15900,8100,6500,4600,3600,6000,10120], **{'in': [15160,7680,5740,3975,3042,4793,6780]})
assert sum(CBO['tot']) == CUST and sum(CBO['in']) == inact[-1]

CHURN = dict(flag=3160, base=8010, st=dict(act=160, d030=720, d3190=2280, d90=0),
             grp=dict(NEW=0, POT=0, LOY=1900, CHA=1260, R1=990, R2=1560, R3=560, R4=50, R5=0),
             wk=WK, day=inact)

# ---------------- leady ----------------
lead_dates = list(days(date(2026, 7, 14), ASOF))
lead_e, lead_l = [], []
for d in lead_dates:
    e = 188 * season(d) / 0.95 * WD[d.weekday()] * noise(0.2)
    if d in (date(2026, 7, 21), date(2026, 8, 4), date(2026, 9, 15), date(2026, 9, 28)): e *= 2.4   # akcje zapisowe
    lead_e.append(round(e))
    lead_l.append(round(74 * noise(0.22)))
lead_l[lead_dates.index(date(2026, 9, 9))] = 2040    # sunset
lead_t = []
t = LEADS - sum(lead_e[1:]) + sum(lead_l[1:])
for i in range(len(lead_dates)):
    if i: t += lead_e[i] - lead_l[i]
    lead_t.append(t)
assert lead_t[-1] == LEADS
si = lead_dates.index(date(2026, 9, 1))
LEAD = dict(tot=LEADS, open30=26400, click30=5620, atrisk=19900, sunCand=4350, sunsetted=3690, remove=2120,
            sms=21940, push=6712, app=16410, cart=3420, checkout=1980, engaged=8100,
            hist=lead_t[si:], e=lead_e[si:], l=lead_l[si:])
SUN = dict(start='2026-09-09')
SUN['s'] = [round(2040 + (3690 - 2040) * (i / 23) ** 0.95) for i in range(24)]
SUN['c'] = [round(4810 - (4810 - 4350) * i / 23 + R.uniform(-40, 40)) for i in range(24)]
SUN['c'][-1] = 4350
LB = dict(tot=LEADS,
          ev=[['Otworzyli aplikację',9850],['Oglądali ekrany w aplikacji',12400],['Zalogowali się',6900],['Zaczęli quiz dietetyczny',4650],['Sprawdzili dostawę pod adres',3980],['Oglądali dietę',8200],['Dodali do koszyka',3420],['Rozpoczęli checkout',1980],['Rozpoczęli płatność',1310]],
          pg=[['Strona główna',11800],['Menu / kalendarz',7300],['Konfiguracja diety',5900],['Dane konta',4100],['Koszyk',3600],['Podsumowanie / checkout',2450],['Program lojalnościowy',2050],['Ekran kuponów',1700],['Wybór płatności',1640],['Błąd zamówienia',42]],
          buy=[['Leadzi ze zgodą',LEADS],['Aktywni w 30 dni',16900],['Koszyk',3420],['Podsumowanie',2450],['Wybór płatności',1640],['Płatność rozpoczęta',1310]])

# ---------------- zgody (365 dni) ----------------
cons_dates = list(days(date(2025, 10, 2), ASOF))
def cons_series(start, end, dips):
    n = len(cons_dates); arr = []
    for i, d in enumerate(cons_dates):
        x = i / (n - 1)
        arr.append(start + (end - start) * (0.6 * x + 0.4 * x * x))
    # wygaszenia (sunset) jako schodki w dół
    out = []; acc = 0
    for i, d in enumerate(cons_dates):
        for dd, amt in dips:
            if d == dd: acc += amt
        out.append(arr[i] - acc)
    # skala tak, by trafić w end
    k = out[-1]
    out = [round(v + (end - k) * i / (n - 1) + R.uniform(-12, 12)) for i, v in enumerate(out)]
    out[-1] = end
    return out
CONS = dict(start='2025-10-02',
            c28=cons_series(80600, NEWS, [(date(2026, 3, 10), 1650), (date(2026, 9, 9), 2040)]),
            c71=cons_series(55100, SMS, [(date(2026, 3, 10), 640)]),
            c523=cons_series(11800, PUSH, []))

def month_delta(arr, dates, m):
    idx = [i for i, d in enumerate(dates) if d.month == m and d.year == 2026]
    return arr[idx[-1]] - arr[idx[0] - 1]

# ---------------- aplikacja ----------------
APP = dict(cmp=dict(cl=[CH_TOT[3], CUST - CH_TOT[3]],
                    ltvB=[[2400,8900,10530,7850,6050,5500],[4100,5150,2470,1190,300,380]],
                    ordB=[[8380,6200,5300,3950,3150,5250,9000],[7520,1900,1200,650,450,750,1120]],
                    eat=[APP_EAT, EAT - APP_EAT], ord=[9050, 2900], val=[9774000, 2784000], code=[2330, 1045]),
           users=APP_USERS, ios=36400, android=24100, op30=38900, op7=24800, pushCons=PUSH, pushReach=28610,
           clients=CH_TOT[3], eat=APP_EAT, eatNoApp=EAT - APP_EAT, inact=APP_INACT,
           buy30=8700, buyApp30=6900, buyWeb30=2600, buyAppEver=36800,
           push=dict(lab=['maj','cze','lip','sie','wrz'], sent=[142300,151800,148600,156200,171400],
                     **{'del': [134900,144100,141300,148700,163900]}, open=[12850,13400,12100,13300,15620], conv=[418,452,431,476,563]))
assert sum(APP['cmp']['ltvB'][0]) == CH_TOT[3] and sum(APP['cmp']['ordB'][1]) == CUST - CH_TOT[3]

# ---------------- statyczne ----------------
STATIC = dict(
 ladder=[dict(l='1. zamówienie', v=LADDER[0], why='Każdy klient zaczyna tutaj.'),
         dict(l='2. zamówienie', v=LADDER[1], why='71% klientów wraca po drugie zamówienie: wynik w górnych 10% branży.'),
         dict(l='3. zamówienie', v=LADDER[2], why='Po drugim zakupie zostaje 4 na 5 klientów.'),
         dict(l='4. zamówienie', v=LADDER[3], why='Od 4. zamówienia klient trafia do grupy Loyalist.'),
         dict(l='5. zamówienie', v=LADDER[4], why='Stabilnie ~81% przejścia.'),
         dict(l='6. zamówienie', v=LADDER[5], why='Stabilnie ~82% przejścia.'),
         dict(l='10+ zamówień', v=LADDER[6], why='Champion: 63% klientów z 6+ zamówieniami dochodzi do 10.')],
 life=[dict(l='Klienci', v=CUST), dict(l='Kupili 2+ razy', v=LADDER[1], why='71% bazy to klienci powracający.'),
       dict(l='Zamówili w 30 dni', v=7350, why='7 350 powracających klientów złożyło zamówienie w ostatnim miesiącu.'),
       dict(l='Jedzą teraz', v=4700, why='Dostawa trwa dziś (bez klientów z pierwszym zamówieniem).'),
       dict(l='Dostawa kończy się w 7 dni', v=1905, why='Dostawa kończy się w ciągu 7 dni: moment na odnowienie.')],
 gap=[dict(l='Co 0–7 dni', v=9800, c='--a0'), dict(l='Co 7–14 dni', v=13400, c='--a1'), dict(l='Co 14–30 dni', v=10200, c='--r0'), dict(l='Co 30+ dni', v=5520, c='--l1')],
 pay=[dict(l='BLIK', v=46, c='--magenta', t='46%', s=''), dict(l='Karta płatnicza', v=31, c='--ink', t='31%', s=''), dict(l='Szybki przelew', v=18, c='--orange', t='18%', s=''), dict(l='Karta podarunkowa', v=5, c='--l1', t='5%', s='')],
 prod=[dict(l='Wybór z menu', v=3300, c='--magenta'), dict(l='Standard', v=2450, c='--orange'), dict(l='Sport / High Protein', v=1320, c='--ink'), dict(l='Wege', v=980, c='--a2'), dict(l='Keto i Low Carb', v=650, c='--l1')],
 days=[dict(l='1–4 dni', v=9, c='--magenta'), dict(l='5–9 dni', v=21, c='--a1'), dict(l='10–19 dni', v=38, c='--orange'), dict(l='20–29 dni', v=24, c='--r1'), dict(l='30+ dni', v=8, c='--ink')],
 gapC=dict(big='~13 d', small='mediana'), payC=dict(big='1 050 zł', small='AOV'), prodC=dict(big=8700, small='kupiło w 30 dni'), daysC=dict(big='14 dni', small='mediana'))

def msum(arr, dates, m): return sum(v for v, d in zip(arr, dates) if d.month == m and d.year == 2026)
MOM = dict(newc=[msum(newc, newc_dates, 8), msum(newc, newc_dates, 9)], second=[812, 868], buy30=[8240, 8700],
           churnIn=[2214, 2081], back=[1953, 2006], retRate=[4, 4], cart=[6920, 6450],
           rfm={g['k']: [g['hist'][0], g['hist'][-1]] for g in RFM},
           leadsIn=[msum(lead_e, lead_dates, 8), msum(lead_e, lead_dates, 9)],
           leadsOut=[msum([v if v < 1000 else 0 for v in lead_l], lead_dates, 8), msum([v if v < 1000 else 0 for v in lead_l], lead_dates, 9)],
           sunset=[0, 2040], sunCandIn=[4120, 3870],
           consE=[month_delta(CONS['c28'], cons_dates, 8) + 2300, month_delta(CONS['c28'], cons_dates, 9) + 2040 + 2300],
           consS=[month_delta(CONS['c71'], cons_dates, 8) + 1100, month_delta(CONS['c71'], cons_dates, 9) + 1100],
           click30=[5050, 5620], open30=[24900, 26400], leadsEnd=[lead_t[si - 1], LEADS])

CHURNP = {1: dict(R1=[14, 3760], R2=[25, 2400], R3=[23, 1250], R4=[13, 330]),
          7: dict(R1=[98, 3850], R2=[176, 2450], R3=[160, 1300], R4=[96, 400]),
          90: dict(R1=[1050, 4700], R2=[1980, 3900], R3=[1700, 2550], R4=[1150, 1450])}

DMAP = dict(asof='2026-10-02', b=[['0–3',0,3,0],['4–7',4,7,0],['8–14',8,14,0],['15–21',15,21,0],['22–30',22,30,0],['31–60',31,60,0],['61+',61,90,0]],
            g=dict(all=['Wszyscy', [1145,950,1350,820,640,240,35]], R1=['Czempioni', [640,530,780,480,370,135,15]],
                   R2=['Lojalni', [340,290,400,250,195,75,10]], R3=['Obiecujący', [140,110,150,80,65,28,7]],
                   R4=['Okazjonalni', [25,20,20,10,10,2,3]], R5=['Utraceni', [0]*7]))

# nowi klienci: rekordy [dzień zamówienia (ujemny), start dostawy, liczba dni]
NCR = []
for k in range(1, 46):
    d = ASOF - timedelta(k - 1)
    n = newc[newc_dates.index(d)] if d in newc_dates else 38
    keep = 0.5 if k <= 7 else 0.42 if k <= 14 else 0.3 if k <= 30 else 0.12
    for _ in range(round(n * keep)):
        lag = R.choice([1, 2, 2, 3, 3, 4, 5, 6, 7, 9, 11])
        ln = R.choice([3, 5, 7, 10, 10, 14, 14, 14, 20, 20, 28, 30])
        start = -k + lag
        if start + ln < 0: ln = -start + R.randint(1, 12)
        NCR.append([-k, start, ln])
def nk(n, prev=True):
    cur = sum(newc[-n:]) if n <= len(newc) else None
    pv = sum(newc[-2 * n:-n]) if prev and 2 * n <= len(newc) else None
    return [cur, pv]
NK = {1: nk(1), 7: nk(7), 14: [sum(newc[-14:]), None], 30: nk(30), 60: [sum(newc[-60:]), None], 90: [sum(newc[-90:]), None]}
NCSEC = [334, 471]

# ---------------- rabaty ----------------
RB = dict(n=700, d=196, v=735100, dv=47775, perDay=398,
          days=[[ (date(2026, 9, 18) + timedelta(i)).strftime('%-d ') + ['sty','lut','mar','kwi','maj','cze','lip','sie','wrz','paź','lis','gru'][(date(2026, 9, 18) + timedelta(i)).month - 1], round(28 + R.uniform(-3.5, 3.5))] for i in range(14)],
          codes=[['POWROT20',34,'20%'],['START15',31,'15%'],['POLEC10',26,'10%'],['APKA10',22,'10%'],['FIT2026',18,'15%'],['WEEKEND12',14,'12%'],['NEWS15',12,'15%'],['VIP25',9,'25%'],['JESIEN20',8,'20%'],['URODZINY15',6,'15%']],
          w=[['1',4900,2100,310,48,19,41800,4150],['2',9300,3700,520,102,33,96900,8050],['3',15600,5300,760,188,54,192700,13000],['4',14200,4100,540,196,49,211700,11575],['5',10820,2600,300,166,41,192000,11000]],
          loy=[['1 zamówienie',170,71],['2–3 zamówienia',190,52],['4+ zamówień',340,73]])
assert sum(r[1] for r in RB['w']) == CUST

SER = dict(newc_start='2026-07-01', newc=newc, lead_start='2026-07-14', lead_e=lead_e, lead_l=lead_l, lead_t=lead_t)

# ---------------- scoring ----------------
# wskaźniki: [poprzednie 30 dni, ostatnie 30 dni]
SCORE = dict(renew=[72.8, 75.4], app=[84.0, round(APP_EAT / EAT * 100, 1)], disc=[6.8, round(RB['dv'] / (RB['v'] + RB['dv']) * 100, 1)], second=[69.4, round(LADDER[1] / LADDER[0] * 100, 1)])

out = []
for name, val in [('ACTIVE_T', ACTIVE_T), ('RAW', RAW), ('APPR', APPR), ('LEAD', LEAD), ('STATIC', STATIC), ('CHURN', CHURN),
                  ('MOM', MOM), ('CHURNP', CHURNP), ('APP', APP), ('CONS', CONS), ('LB', LB), ('RB', RB), ('SER', SER),
                  ('CBO', CBO), ('SUN', SUN), ('DMAP', DMAP), ('NCR', NCR), ('NK', NK), ('NCSEC', NCSEC), ('SCORE', SCORE)]:
    out.append(f'{name}={J(val)}')
open('/home/user/fdfy-kyl/build/data.json', 'w').write(J(dict(out=out, CUST=CUST, PROFILES=PROFILES, EAT=EAT, APP_EAT=APP_EAT,
     CH_TOT=CH_TOT, base_sep1=base_at(date(2026, 8, 31)), inact_end=inact[-1], newc30=sum(newc[-30:]), MOM=MOM,
     ncr_eat=sum(1 for r in NCR if r[1] <= 0), ncr_wait=sum(1 for r in NCR if r[1] > 0), sep_eat=sum(ACTIVE_T[-31:-1]) / 30, aug_eat=sum(ACTIVE_T[26:57]) / 31)))
print('profiles', PROFILES, 'eat', EAT, 'app_eat', APP_EAT, 'app share eat', APP_EAT / EAT, 'ch', CH_TOT, 'app inact', APP_INACT)
print('base Sep1', base_at(date(2026, 8, 31)), 'sum starts', sum(starts.values()))
print('newc30', sum(newc[-30:]), 'NK', NK, 'NCR eat/wait', sum(1 for r in NCR if r[1] <= 0), sum(1 for r in NCR if r[1] > 0))
print('eat sep/aug', sum(ACTIVE_T[-31:-1]) / 30, sum(ACTIVE_T[26:57]) / 31, 'rev/yr @80', sum(ACTIVE_T[-31:-1]) / 30 * 80 * 365)
print('MOM', MOM)
print('APPR', APPR)

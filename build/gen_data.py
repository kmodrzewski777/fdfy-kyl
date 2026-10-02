"""Generator danych dashboardu Insights.

Model bazy: profile 235 858 = 98 274 zgód newsletter x 2,4; ok. 54,8 tys. klientów; 58 762 leadów;
ok. 5,1 tys. jedzących dziennie x ~80 zł/dzień ~ 150 mln zł przychodu rocznie.
Wszystkie wartości dostają szum, a serie dzienne mają wahania (weekendy, wakacje, sunsety, wypisy).
"""
import json, math, random
from datetime import date, timedelta

R = random.Random(7310)
def J(x): return json.dumps(x, ensure_ascii=False, separators=(',', ':'))
def nz(a): return 1 + R.uniform(-a, a)
def rough(x, pct=0.035):
    """Szum procentowy + brak zer na końcu dla liczb >= 100."""
    if x == 0: return 0
    v = round(x * nz(pct))
    if v >= 100:
        while v % 10 == 0: v += R.choice([-3, -2, -1, 1, 2, 3, 4, 6, 7])
    return max(0, v)
def fix_sum(vals, target, idx=None):
    """Dopasuj sumę listy do target, korygując największy element (lub idx)."""
    i = idx if idx is not None else max(range(len(vals)), key=lambda k: vals[k])
    vals[i] += target - sum(vals)
    return vals
def days(a, b):
    d = a
    while d <= b:
        yield d; d += timedelta(1)
MON = ['sty','lut','mar','kwi','maj','cze','lip','sie','wrz','paź','lis','gru']
def lab(d): return f'{d.day} {MON[d.month - 1]}'

ASOF = date(2026, 10, 1)
NEWS, SMS, PUSH = 98274, 68318, 29492
PROFILES = round(NEWS * 2.4)
LEADS = 58762
APP_USERS = 61947

# ---------------- segmenty: stany [e03,e47,teraz,d07,d814,d1530,d3160,d6190,d90]
RFM0 = [
 ('R1','Czempioni','RFM 14–15','--c-r1',[640,530,2950,300,200,290,420,230,510],[4060,4250,3450,4560],[0,30,380,1450,1700,1340]),
 ('R2','Lojalni','RFM 11–13','--c-r2',[340,290,1560,260,200,360,760,560,5000],[6960,7310,4950,7570],[20,600,2900,3100,1500,580]),
 ('R3','Obiecujący','RFM 8–10','--c-r3',[140,110,580,170,150,330,700,640,9030],[8820,9050,5110,9280],[600,3600,4600,2000,600,200]),
 ('R4','Okazjonalni','RFM 5–7','--c-r4',[25,20,90,40,50,120,420,470,14710],[11130,11920,5230,11450],[3600,7400,3900,850,120,30]),
 ('R5','Utraceni','RFM 3–4','--c-r5',[0,0,0,0,0,0,3,11,13720],[8542,9340,2900,8370],[6900,5800,920,100,0,0]),
]
LOY0 = [
 ('NEW','Newcomer','1 zamówienie','--c-new',[205,170,900,70,70,120,410,340,14410],[10292,11070,4090,9680],[8400,6600,850,50,0,0]),
 ('POT','Potential Loyalist','2–3 zamówienia','--c-pot',[150,130,640,150,130,260,610,560,12250],[10370,11000,5050,10700],[1500,7200,5000,800,100,0]),
 ('LOY','Loyalist','4–9 zamówień','--c-loy',[305,250,1390,250,200,380,760,620,10430],[10650,11200,6400,11500],[0,1400,6900,4600,1100,200]),
 ('CHA','Champion','10+ zamówień','--c-cha',[490,405,2250,300,200,340,520,380,5880],[8200,8600,6100,9350],[0,100,1900,4500,2600,1020]),
]
def mk(rows):
    out = []
    for k, n, d, c, st, ch, ltv in rows:
        s = [rough(v, .05) if v >= 20 else v for v in st]
        s[0] = min(s[0], s[2]); s[1] = min(s[1], s[2] - s[0])
        out.append(dict(k=k, n=n, d=d, c=c, st=s, ch=[rough(v, .03) for v in ch], ltv=[rough(v, .05) for v in ltv]))
    return out
RFM, LOY = mk(RFM0), mk(LOY0)
# kolumny stanów LOY = RFM
for j in [2, 3, 4, 5, 6, 7, 8, 0, 1]:
    diff = sum(g['st'][j] for g in RFM) - sum(g['st'][j] for g in LOY)
    tgt = max(LOY, key=lambda g: g['st'][j]); tgt['st'][j] += diff
for grp in (RFM, LOY):
    for g in grp:
        s = g['st']; g['tot'] = s[2] + sum(s[3:9])
CUST = sum(g['tot'] for g in RFM)
assert CUST == sum(g['tot'] for g in LOY)
EAT = sum(g['st'][2] for g in RFM)
CH_T = [NEWS - LEADS, 41853, 21617, 41186]          # e-mail, SMS, push, aplikacja wśród klientów
for grp in (RFM, LOY):
    for j in range(4):
        col = [g['ch'][j] for g in grp]
        fix_sum(col, CH_T[j])
        for g, v in zip(grp, col): g['ch'][j] = min(v, g['tot'])
        assert sum(g['ch'][j] for g in grp) == CH_T[j]
    for g in grp:
        fix_sum(g['ltv'], g['tot'])

# historia RFM we wrześniu: przeliczenia dzienne dają ruchy w obie strony
newc = []
newc_dates = list(days(date(2026, 7, 1), ASOF))
WDN = [1.12, 1.04, 0.98, 1.0, 0.93, 0.82, 1.1]
for d in newc_dates:
    base = 89 + (d - newc_dates[0]).days * 0.11
    if date(2026, 8, 8) <= d <= date(2026, 8, 18): base *= 0.82     # długi weekend sierpniowy
    newc.append(max(9, round(base * WDN[d.weekday()] * nz(0.24))))
def base_at(d):
    return CUST - sum(v for dd, v in zip(newc_dates, newc) if dd > d)
sep1 = base_at(date(2026, 8, 31))
growth = {'R1': 211, 'R2': 384, 'R3': 597, 'R4': 846, 'R5': 0}
starts = {g['k']: g['tot'] - growth[g['k']] for g in RFM}
starts['R5'] = sep1 - sum(v for k, v in starts.items() if k != 'R5')
for g in RFM:
    a, b = starts[g['k']], g['tot']
    h, v = [], a
    step = (b - a) / 29
    for i in range(30):
        h.append(round(v))
        v += step + R.gauss(0, max(6, b * 0.0028)) + (R.choice([-1, 1]) * b * 0.006 if R.random() < 0.08 else 0)
    h[-1] = b
    g['hist'] = h
    ein = max(8, b * 0.012)
    g['e'] = [max(1, round(ein * nz(0.3))) for _ in range(30)]
    g['l'] = [max(0, round(g['e'][i] - (h[i] - h[i - 1] if i else step))) for i in range(30)]

def seg_js(g, extra=None):
    o = dict(k=g['k'], n=g['n'], d=g['d'], c=g['c'], tot=g['tot'], r=g['st'] + g['ch'], ltv=g['ltv'])
    if 'hist' in g: o.update(hist=g['hist'], e=g['e'], l=g['l'])
    if extra: o.update(extra)
    return o
NC30 = sum(newc[-30:])
RAW = dict(loy=[seg_js(g, {'in': round(NC30 / 30, 1), 'out': 66.3} if g['k'] == 'NEW' else {'in': 66.3} if g['k'] == 'POT' else None) for g in LOY],
           rfm=[seg_js(g) for g in RFM])

def ipf(groups):
    ratio = [0.875, 0.87, 0.86, 0.82, 0.8, 0.78, 0.76, 0.75, 0.728]
    out = {g['k']: [g['st'][j] * ratio[j] for j in range(9)] for g in groups}
    tcol = [sum(g['st'][j] for g in groups) * ratio[j] for j in range(9)]
    for _ in range(60):
        for g in groups:
            row = out[g['k']]; s = row[2] + sum(row[3:9]); f = g['ch'][3] / s if s else 0
            out[g['k']] = [v * f for v in row]
        for j in range(9):
            s = sum(out[g['k']][j] for g in groups); f = tcol[j] / s if s else 0
            for g in groups: out[g['k']][j] *= f
    res = {}
    for g in groups:
        row = [min(round(v), g['st'][j]) for j, v in enumerate(out[g['k']])]
        row[0] = min(row[0], row[2]); row[1] = min(row[1], row[2] - row[0])
        row[8] += g['ch'][3] - (row[2] + sum(row[3:9]))
        res[g['k']] = [g['ch'][3]] + row
    return res
APPR = {**ipf(LOY), **ipf(RFM)}
APP_EAT = sum(APPR[g['k']][3] for g in RFM)
APP_INACT = sum(sum(APPR[g['k']][7:10]) for g in RFM)
L = {g['k']: g for g in LOY}

# ---------------- jedzący dziennie (6.07 → 1.10): weekendy, wakacje, wrzesień w górę
ACTIVE_T = []
lvl = 4880.0
for d in days(date(2026, 7, 6), ASOF):
    drift = {7: -6.5, 8: -1.5, 9: 10.5, 10: 0}[d.month]
    if date(2026, 8, 10) <= d <= date(2026, 8, 17): drift = -14
    if date(2026, 8, 18) <= d <= date(2026, 8, 24): drift = 9
    lvl += drift + R.gauss(0, 11)
    wk = {5: R.uniform(.955, .985), 6: R.uniform(.93, .97)}.get(d.weekday(), 1.0)
    if d == date(2026, 8, 15): wk *= 0.88
    ACTIVE_T.append(round(lvl * wk * nz(0.014)))
n_ = len(ACTIVE_T); wl = {5: 0.935, 6: 0.905}.get(ASOF.weekday(), 1.0); dlt = EAT - ACTIVE_T[-1]
ACTIVE_T = [round(v + dlt * (i / (n_ - 1)) ** 1.3) for i, v in enumerate(ACTIVE_T)]
ACTIVE_T[-1] = EAT

# ---------------- churn
INACT = sum(sum(g['st'][6:9]) for g in RFM)
WK = dict(lab=['16 lip','23 lip','30 lip','6 sie','13 sie','20 sie','27 sie','3 wrz','10 wrz','17 wrz','24 wrz'],
          out=[1027, 1061, 1094, 1012, 1138, 1047, 979, 1003, 968, 1021, 947],
          back=[398, 412, 431, 387, 404, 428, 419, 446, 423, 468, 419],
          out2=[531, 547, 566, 522, 589, 538, 512, 517, 498, 526, 489],
          back2=[449, 461, 488, 437, 476, 459, 446, 471, 452, 479, 444])
dts = list(days(date(2026, 8, 7), ASOF))
steps = []
for d in dts[1:]:
    wi = min(10, max(0, (d - date(2026, 7, 16)).days // 7))
    steps.append((WK['out'][wi] - WK['back'][wi]) / 7 + R.gauss(0, 38) + (55 if d.weekday() == 0 else -14 if d.weekday() == 6 else 0))
inact = [INACT - sum(steps)]
for st_ in steps: inact.append(inact[-1] + st_)
inact = [round(x) for x in inact]; inact[-1] = INACT
st4 = [L['LOY'], L['CHA']]
base4 = sum(g['st'][2] + sum(g['st'][3:8]) for g in st4)
d3190 = sum(g['st'][6] + g['st'][7] for g in st4)
d030 = round(sum(sum(g['st'][3:6]) for g in st4) * 0.437)
act = round(sum(g['st'][2] for g in st4) * 0.0387)
flag = act + d030 + d3190
loyf = round(flag * 0.6017)
rw = [0.3134, 0.4927, 0.1771, 0.0168]
rf = [round(flag * w) for w in rw]; rf[1] += flag - sum(rf)
CHURN = dict(flag=flag, base=base4, st=dict(act=act, d030=d030, d3190=d3190, d90=0),
             grp=dict(NEW=0, POT=0, LOY=loyf, CHA=flag - loyf, R1=rf[0], R2=rf[1], R3=rf[2], R4=rf[3], R5=0), wk=WK, day=inact)

# bariera / drabina
p2 = round(L['POT']['tot'] * 0.5548)
t4, t5 = round(L['LOY']['tot'] * 0.3237), round(L['LOY']['tot'] * 0.2531)
tot_b = [L['NEW']['tot'], p2, L['POT']['tot'] - p2, t4, t5, L['LOY']['tot'] - t4 - t5, L['CHA']['tot']]
ina = {g['k']: sum(g['st'][6:9]) for g in LOY}
i2 = round(p2 * 0.926); i4 = round(t4 * 0.8641); i5 = round(t5 * 0.8457)
in_b = [ina['NEW'], i2, ina['POT'] - i2, i4, i5, ina['LOY'] - i4 - i5, ina['CHA']]
CBO = dict(lab=['1','2','3','4','5','6–9','10+'], tot=tot_b, **{'in': in_b})
assert sum(in_b) == INACT
LAD = [CUST]
for t in tot_b[:5]: LAD.append(LAD[-1] - t)
LADDER = LAD[:6] + [tot_b[6]]

# ---------------- leady
lead_dates = list(days(date(2026, 7, 14), ASOF))
lead_e, lead_l = [], []
SEND = {0, 3}                 # dni newsletterów: więcej zapisów i więcej wypisów
for d in lead_dates:
    e = 297 * {7: 0.93, 8: 0.86, 9: 1.08, 10: 1.1}[d.month] * WDN[d.weekday()] * nz(0.28)
    if d in (date(2026, 7, 21), date(2026, 8, 4), date(2026, 9, 15), date(2026, 9, 28)): e *= R.uniform(2.1, 2.7)
    l = 168 * nz(0.3) + (R.uniform(45, 130) if d.weekday() in SEND else 0)
    if d in (date(2026, 8, 5), date(2026, 9, 16)): l += R.uniform(150, 260)   # porządki po kampaniach
    lead_e.append(round(e)); lead_l.append(round(l))
SUNSET = 2037
lead_l[lead_dates.index(date(2026, 9, 9))] = SUNSET
lead_t, t = [], LEADS - sum(lead_e[1:]) + sum(lead_l[1:])
for i in range(len(lead_dates)):
    if i: t += lead_e[i] - lead_l[i]
    lead_t.append(t)
si = lead_dates.index(date(2026, 9, 1))
SUN = dict(start='2026-09-09')
s, c = [], []
sv, cv = SUNSET + 143, 4917
for i in range(24):
    s.append(round(sv)); c.append(round(cv))
    sv += R.uniform(35, 110) - (R.uniform(40, 160) if R.random() < 0.18 else 0)     # wygaszeni minus przywróceni
    cv += R.gauss(-18, 62) + (R.uniform(120, 260) if R.random() < 0.12 else 0)
SUN.update(s=s, c=c)
LB_ev = [['Otworzyli aplikację',9857],['Oglądali ekrany w aplikacji',12431],['Zalogowali się',6893],['Zaczęli quiz dietetyczny',4662],['Sprawdzili dostawę pod adres',3974],['Oglądali dietę',8216],['Dodali do koszyka',3418],['Rozpoczęli checkout',1977],['Rozpoczęli płatność',1306]]
LB_pg = [['Strona główna',11823],['Menu / kalendarz',7286],['Konfiguracja diety',5914],['Dane konta',4097],['Koszyk',3612],['Podsumowanie / checkout',2461],['Program lojalnościowy',2052],['Ekran kuponów',1693],['Wybór płatności',1647],['Błąd zamówienia',43]]
LB = dict(tot=LEADS, ev=LB_ev, pg=LB_pg,
          buy=[['Leadzi ze zgodą',LEADS],['Aktywni w 30 dni',16874],['Koszyk',LB_ev[6][1]],['Podsumowanie',LB_pg[5][1]],['Wybór płatności',LB_pg[8][1]],['Płatność rozpoczęta',LB_ev[8][1]]])
OTH = dict(sms=4519, push=1163, app=4307)
LEAD = dict(tot=LEADS, open30=26384, click30=5617, atrisk=19871, sunCand=c[-1], sunsetted=s[-1], remove=2113,
            sms=SMS - CH_T[1] - OTH['sms'], push=PUSH - CH_T[2] - OTH['push'], app=APP_USERS - CH_T[3] - OTH['app'],
            cart=LB_ev[6][1], checkout=LB_ev[7][1], engaged=8093, hist=lead_t[si:], e=lead_e[si:], l=lead_l[si:])

# ---------------- zgody: dzienne przyrosty i wypisy, sunsety, sezon
cons_dates = list(days(date(2025, 6, 2), ASOF))
SEAC = {6: 1.9, 7: 1.5, 8: 1.3, 10: 1.0, 11: 1.15, 12: 0.7, 1: 1.45, 2: 1.1, 3: 1.05, 4: 0.95, 5: 0.9, 6: 0.75, 7: 0.6, 8: 0.62, 9: 1.2}
def cons_series(start, end, gross, unsub, dips, shocks=(), launch=None):
    inc, out = [], []
    for d in cons_dates:
        if launch and d < launch: inc.append(0); out.append(0); continue
        boost = 3.2 if launch and (d - launch).days < 21 else 1
        age = (d - (launch or cons_dates[0])).days
        inc.append(gross * SEAC[d.month] * WDN[d.weekday()] * nz(0.35) * boost * (1.55 - 0.75 * min(1, age / 420)))
        o = unsub * nz(0.4) * (0.3 + min(1, age / 200)) + (unsub * R.uniform(1.5, 3.5) if d.weekday() in SEND else 0)
        for dd, amt in list(dips) + list(shocks):
            if d == dd: o += amt
        out.append(o)
    f = (end - start + sum(out)) / sum(inc)
    arr, v = [], float(start)
    for a, b in zip(inc, out):
        v += a * f - b; arr.append(round(v))
    arr[-1] = end
    return arr
CONS = dict(start='2025-06-02',
            c28=cons_series(3912, NEWS, 118, 31, [(date(2026, 3, 10), 1651), (date(2026, 9, 9), SUNSET)]),
            c71=cons_series(2147, SMS, 71, 18, [(date(2026, 3, 10), 643)], [(date(2026, 6, 2), 388)]),
            c523=cons_series(0, PUSH, 63, 9, [], [(date(2026, 2, 17), 412), (date(2026, 7, 22), 297)], launch=date(2025, 9, 15)))   # wylogowania po aktualizacjach aplikacji

# ---------------- aplikacja
lb_tot = [sum(g['ltv'][j] for g in RFM) for j in range(6)]
la = [round(t * r) for t, r in zip(lb_tot, [0.369, 0.633, 0.81, 0.868, 0.953, 0.935])]; fix_sum(la, CH_T[3], 2)
ob = [round(t * r) for t, r in zip(tot_b, [0.527, 0.765, 0.815, 0.859, 0.875, 0.875, 0.889])]; fix_sum(ob, CH_T[3], 0)
BUY30 = 10243
both = 806; bapp = round(BUY30 * 0.7934)
APP = dict(cmp=dict(cl=[CH_T[3], CUST - CH_T[3]], ltvB=[la, [t - a for t, a in zip(lb_tot, la)]], ordB=[ob, [t - a for t, a in zip(tot_b, ob)]],
                    eat=[APP_EAT, EAT - APP_EAT], ord=[9047, 2918], val=[9765331, 2806187], code=[2319, 1061]),
           users=APP_USERS, ios=36412, android=24089, op30=38861, op7=24773, pushCons=PUSH, pushReach=28587,
           clients=CH_T[3], eat=APP_EAT, eatNoApp=EAT - APP_EAT, inact=APP_INACT,
           buy30=BUY30, buyApp30=bapp, buyWeb30=BUY30 - bapp + both, buyAppEver=36817,
           push=dict(lab=['maj','cze','lip','sie','wrz'], sent=[142318,151764,131593,138207,171442],
                     **{'del': [134871,144212,124385,130917,163569]}, open=[12863,13391,10427,11208,15634], conv=[418,452,371,389,563]))

# ---------------- statyczne
gap = [round((CUST - L['NEW']['tot']) * r) for r in [0.2519, 0.3442, 0.2621]]; gap.append(CUST - L['NEW']['tot'] - sum(gap))
prod = [round(BUY30 * r) for r in [0.3794, 0.2817, 0.1523, 0.1127]]; prod.append(BUY30 - sum(prod))
ret30 = BUY30 - NC30
eat_old = EAT - L['NEW']['st'][2]
end7 = sum(g['st'][0] + g['st'][1] for g in RFM) - (L['NEW']['st'][0] + L['NEW']['st'][1])
pc = lambda a, b: round(100 * a / b)
STATIC = dict(
 ladder=[dict(l='1. zamówienie', v=LADDER[0], why='Każdy klient zaczyna tutaj.'),
         dict(l='2. zamówienie', v=LADDER[1], why=f'{pc(LADDER[1], LADDER[0])}% klientów wraca po drugie zamówienie.'),
         dict(l='3. zamówienie', v=LADDER[2], why=f'Po drugim zakupie zostaje {pc(LADDER[2], LADDER[1])}% klientów.'),
         dict(l='4. zamówienie', v=LADDER[3], why='Od 4. zamówienia klient trafia do grupy Loyalist.'),
         dict(l='5. zamówienie', v=LADDER[4], why=f'{pc(LADDER[4], LADDER[3])}% przejścia.'),
         dict(l='6. zamówienie', v=LADDER[5], why=f'{pc(LADDER[5], LADDER[4])}% przejścia.'),
         dict(l='10+ zamówień', v=LADDER[6], why=f'Champion: {pc(LADDER[6], LADDER[5])}% klientów z 6+ zamówieniami dochodzi do 10.')],
 life=[dict(l='Klienci', v=CUST), dict(l='Kupili 2+ razy', v=LADDER[1], why=f'{pc(LADDER[1], CUST)}% bazy to klienci powracający.'),
       dict(l='Zamówili w 30 dni', v=ret30, why='Powracający klienci, którzy złożyli zamówienie w ostatnim miesiącu.'),
       dict(l='Jedzą teraz', v=eat_old, why='Dostawa trwa dziś (bez klientów z pierwszym zamówieniem).'),
       dict(l='Dostawa kończy się w 7 dni', v=end7, why='Dostawa kończy się w ciągu 7 dni: moment na odnowienie.')],
 gap=[dict(l='Co 0–7 dni', v=gap[0], c='--a0'), dict(l='Co 7–14 dni', v=gap[1], c='--a1'), dict(l='Co 14–30 dni', v=gap[2], c='--r0'), dict(l='Co 30+ dni', v=gap[3], c='--l1')],
 pay=[dict(l='BLIK', v=46.3, c='--magenta', t='46%', s=''), dict(l='Karta płatnicza', v=30.8, c='--ink', t='31%', s=''), dict(l='Szybki przelew', v=17.6, c='--orange', t='18%', s=''), dict(l='Karta podarunkowa', v=5.3, c='--l1', t='5%', s='')],
 prod=[dict(l='Wybór z menu', v=prod[0], c='--magenta'), dict(l='Standard', v=prod[1], c='--orange'), dict(l='Sport / High Protein', v=prod[2], c='--ink'), dict(l='Wege', v=prod[3], c='--a2'), dict(l='Keto i Low Carb', v=prod[4], c='--l1')],
 days=[dict(l='1–4 dni', v=1083, c='--magenta'), dict(l='5–9 dni', v=2467, c='--a1'), dict(l='10–19 dni', v=4431, c='--orange'), dict(l='20–29 dni', v=2861, c='--r1'), dict(l='30+ dni', v=917, c='--ink')],
 gapC=dict(big='~13 d', small='mediana'), payC=dict(big='1 047 zł', small='AOV'), prodC=dict(big=BUY30, small='kupiło w 30 dni'), daysC=dict(big='14 dni', small='mediana'))

def msum(arr, dts, m, cap=None): return sum((0 if cap and v > cap else v) for v, d in zip(arr, dts) if d.month == m and d.year == 2026)
def month_delta(arr, m):
    idx = [i for i, d in enumerate(cons_dates) if d.month == m and d.year == 2026]
    return arr[idx[-1]] - arr[idx[0] - 1]
MOM = dict(newc=[msum(newc, newc_dates, 8), msum(newc, newc_dates, 9)], second=[1893, 2011], buy30=[9786, BUY30],
           churnIn=[2214, 2081], back=[1953, 2006], retRate=[4, 4], cart=[6917, 6452],
           rfm={g['k']: [g['hist'][0], g['hist'][-1]] for g in RFM},
           leadsIn=[msum(lead_e, lead_dates, 8), msum(lead_e, lead_dates, 9)],
           leadsOut=[msum(lead_l, lead_dates, 8, 1000), msum(lead_l, lead_dates, 9, 1000)],
           sunset=[0, SUNSET], sunCandIn=[4117, 3869],
           consE=[month_delta(CONS['c28'], 8) + 2311, month_delta(CONS['c28'], 9) + SUNSET + 2311],
           consS=[month_delta(CONS['c71'], 8) + 1093, month_delta(CONS['c71'], 9) + 1093],
           click30=[5046, LEAD['click30']], open30=[24873, LEAD['open30']], leadsEnd=[lead_t[si - 1], LEADS])
CHURNP = {1: dict(R1=[14, 3761], R2=[27, 2406], R3=[23, 1247], R4=[13, 331]),
          7: dict(R1=[97, 3846], R2=[178, 2453], R3=[161, 1302], R4=[94, 403]),
          90: dict(R1=[1047, 4706], R2=[1983, 3891], R3=[1706, 2543], R4=[1153, 1446])}

# kiedy kończy się dostawa (jedzący teraz)
DR = [0.437, 0.271, 0.207, 0.077, 0.008]
dm = {}
for g in RFM:
    rest = g['st'][2] - g['st'][0] - g['st'][1]
    v = [round(rest * r * nz(0.12)) for r in DR]; fix_sum(v, rest, 0)
    dm[g['k']] = [g['st'][0], g['st'][1]] + v
dm_all = [sum(dm[k][i] for k in dm) for i in range(7)]
DMAP = dict(asof='2026-10-02', b=[['0–3',0,3,0],['4–7',4,7,0],['8–14',8,14,0],['15–21',15,21,0],['22–30',22,30,0],['31–60',31,60,0],['61+',61,90,0]],
            g=dict(all=['Wszyscy', dm_all], R1=['Czempioni', dm['R1']], R2=['Lojalni', dm['R2']], R3=['Obiecujący', dm['R3']], R4=['Okazjonalni', dm['R4']], R5=['Utraceni', dm['R5']]))

NCR = []
for kk in range(1, 46):
    d = ASOF - timedelta(kk - 1)
    n = newc[newc_dates.index(d)]
    keep = 0.5 if kk <= 7 else 0.42 if kk <= 14 else 0.3 if kk <= 30 else 0.12
    for _ in range(round(n * keep * nz(0.2))):
        lag = R.choice([1, 2, 2, 3, 3, 4, 5, 6, 7, 9, 11])
        ln = R.choice([3, 5, 7, 10, 10, 14, 14, 14, 20, 20, 28, 30])
        st_ = -kk + lag
        if st_ + ln < 0: ln = -st_ + R.randint(1, 12)
        NCR.append([-kk, st_, ln])
def nk(n): return [sum(newc[-n:]), sum(newc[-2 * n:-n]) if 2 * n <= len(newc) else None]
NK = {1: nk(1), 7: nk(7), 14: [sum(newc[-14:]), None], 30: nk(30), 60: [sum(newc[-60:]), None], 90: [sum(newc[-90:]), None]}
NCSEC = [836, 1177]

# ---------------- rabaty
w0 = [[4900,2100,310,48,19,41800,3610],[9300,3700,520,102,33,96900,7010],[15600,5300,760,188,54,192700,11320],[14200,4100,540,196,49,211700,10080],[10820,2600,300,166,41,192000,9580]]
W = [[rough(v, .04) if v >= 20 else v for v in r] for r in w0]
cl = [r[0] for r in W]; fix_sum(cl, CUST)
for r, v in zip(W, cl): r[0] = v
RBw = [[str(i + 1)] + r for i, r in enumerate(W)]
n_ = sum(r[3] for r in W); d_ = sum(r[4] for r in W); v_ = sum(r[5] for r in W); dv_ = sum(r[6] for r in W)
loy_n = [round(n_ * .243), round(n_ * .271)]; loy_n.append(n_ - sum(loy_n))
loy_d = [round(loy_n[0] * .418), round(loy_n[1] * .274)]; loy_d.append(d_ - sum(loy_d))
RB = dict(n=n_, d=d_, v=v_, dv=dv_, perDay=397,
          days=[[lab(date(2026, 9, 18) + timedelta(i)), round(28 + R.uniform(-4.5, 4.5) + (3 if (date(2026, 9, 18) + timedelta(i)).weekday() == 0 else 0))] for i in range(14)],
          codes=[['POWROT20',33,'20%'],['START15',31,'15%'],['POLEC10',27,'10%'],['APKA10',21,'10%'],['FIT2026',17,'15%'],['WEEKEND12',14,'12%'],['NEWS15',11,'15%'],['VIP25',9,'25%'],['JESIEN20',8,'20%'],['URODZINY15',6,'15%']],
          w=RBw, loy=[['1 zamówienie', loy_n[0], loy_d[0]], ['2–3 zamówienia', loy_n[1], loy_d[1]], ['4+ zamówień', loy_n[2], loy_d[2]]])
SER = dict(newc_start='2026-07-01', newc=newc, lead_start='2026-07-14', lead_e=lead_e, lead_l=lead_l, lead_t=lead_t)
SCORE = dict(renew=[74.9, 78.6], app=[84.3, round(APP_EAT / EAT * 100, 1)], disc=[6.8, round(dv_ / (v_ + dv_) * 100, 1)], second=[68.1, round(LADDER[1] / LADDER[0] * 100, 1)])

out = []
for name, val in [('ACTIVE_T', ACTIVE_T), ('RAW', RAW), ('APPR', APPR), ('LEAD', LEAD), ('STATIC', STATIC), ('CHURN', CHURN),
                  ('MOM', MOM), ('CHURNP', CHURNP), ('APP', APP), ('CONS', CONS), ('LB', LB), ('RB', RB), ('SER', SER),
                  ('CBO', CBO), ('SUN', SUN), ('DMAP', DMAP), ('NCR', NCR), ('NK', NK), ('NCSEC', NCSEC), ('SCORE', SCORE)]:
    out.append(f'{name}={J(val)}')
json.dump(dict(out=out, CUST=CUST, PROFILES=PROFILES), open('/home/user/fdfy-kyl/build/data.json', 'w'), ensure_ascii=False)
print('CUST', CUST, 'EAT', EAT, 'APP_EAT', APP_EAT, round(APP_EAT / EAT * 100, 1), 'INACT', INACT, round(INACT / CUST * 100, 1))
print('ladder', LADDER, 'CBO in%', [round(100 * a / b, 1) for a, b in zip(in_b, tot_b)])
print('eat sep', sum(ACTIVE_T[-31:-1]) / 30, 'aug', sum(ACTIVE_T[26:57]) / 31, 'jul', sum(ACTIVE_T[:26]) / 26)
print('SCORE', SCORE, 'CHURN', flag, base4, 'RB', n_, d_, v_, dv_, 'LEAD sms/push/app', LEAD['sms'], LEAD['push'], LEAD['app'])
print('cons ends', CONS['c28'][-31], CONS['c71'][-31], CONS['c523'][-31])

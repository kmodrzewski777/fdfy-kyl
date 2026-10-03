#!/usr/bin/env python3
"""raw.json (surowe wyniki Customer.io) -> snapshot.json (jeden dokument do bazy artefaktu). HTML się nie zmienia.
Cała logika prezentacji jest tutaj. LLM nic nie liczy ręcznie:
  python3 refresh/plan.py --reset   -> wykonaj wypisane wywołania, zapisuj put.py
  python3 refresh/build.py          -> przelicza WSZYSTKO
"""
import json, re, collections, statistics, os, sys, math, time, datetime as dt
D = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(os.path.join(D, 'raw.json')))
s = json.load(open(os.path.join(D, 'snapshot.json')))  # szablon: pola nieliczone tu (MOM, konfiguracja) zostają bez zmian
C = raw['counts']
D0 = dt.date.fromisoformat(raw['asof'])
MON = ['sty', 'lut', 'mar', 'kwi', 'maj', 'cze', 'lip', 'sie', 'wrz', 'paź', 'lis', 'gru']
lab = lambda d: '%d %s' % (d.day, MON[d.month - 1])
day = lambda x: dt.date.fromisoformat(x)

# ---------- walidacja kompletności ----------
err = []
err += ['counts:' + k for k, _ in json.load(open(os.path.join(D, 'queries.json'))) if k not in C]
MEMB = ['528', '28', '51', '71', '75', '523', '488', '551', '636', '639', '531', '143', '145', '146', '147', '149', '655']
err += ['membership:' + m for m in MEMB if m not in raw.get('membership', {})]
if '531' not in raw.get('membership_weeks', {}): err.append('membership_weeks:531')
for k in ('active_pages', 'sec_pages'):
    if not raw.get(k): err.append(k)
smp = raw['sample']
last14 = [str(D0 - dt.timedelta(i)) for i in range(14, 0, -1)]
err += ['sample:' + d for d in last14 if d not in smp]
if err: sys.exit('Brak danych w raw.json (uruchom plan.py):\n  ' + '\n  '.join(err))

def mem(seg, start=None, end=None):
    """Seria dzienna segmentu jako dict data->(entered,left,total); brak danych = 0."""
    m = raw['membership'][str(seg)]; st = day(m['start'])
    n = max(len(m['e']), len(m['l']), len(m['t']))
    g = lambda a, i: (a[i] if i < len(a) and a[i] is not None else 0)
    return collections.defaultdict(lambda: (0, 0, 0), {st + dt.timedelta(i): (g(m['e'], i), g(m['l'], i), g(m['t'], i)) for i in range(n)})
def series(seg, start, idx):
    m = mem(seg); st = day(start)
    return [m[st + dt.timedelta(i)][idx] for i in range((D0 - st).days + 1)]

rows = [smp[d] for d in last14]

# ---------- RB (Rabaty) ----------
RB = s['RB']
for k in ('n', 'd', 'v', 'dv'): RB[k] = sum(r[k] for r in rows)
cc = collections.Counter()
for r in rows:
    for k, n in r['codes']: cc[k] += n
def pct(k):
    m = re.search(r'(\d+)$', k)
    return m.group(1) + '%' if m and m.group(1) in ('10', '15', '20', '25', '30', '40', '50') else '—'
RB['codes'] = [[k, n, pct(k)] for k, n in cc.most_common(10)]
lo = collections.defaultdict(lambda: [0, 0])
for r in rows:
    for k, n, d in r['o']: lo[k][0] += n; lo[k][1] += d
RB['loy'] = [['1 zamówienie', *lo['1']], ['2–3 zamówienia', *lo['2-3']], ['4+ zamówień', *lo['4+']]]
W = collections.defaultdict(lambda: [0, 0, 0, 0])
for r in rows:
    for k, n, d, v, dv in r['w']:
        for i, x in enumerate((n, d, v, dv)): W[k][i] += x
for k, w in enumerate(RB['w'], 1):
    w[1:4] = [C['rb.w%d.%d' % (k, j)] for j in (1, 2, 3)]
    w[4:8] = W[w[0]]
RB['perDay'] = raw['purchases_yesterday']
# serie dzienne RB.days / CB.days: dni z próbki (pola dn/rc/sws) + historia sprzed zmiany próbki
dl = dict(raw.get('days_legacy', {}))
for d, r in smp.items():
    if 'dn' in r and r['n']:
        dl[d] = {'rb': [round(100 * r['dn'] / r['n']), round(100 * r['t'] / r['n'])], 'cb': [r['rc'], r['sws'], r['n']]}
dk = sorted(x for x in dl if x < str(D0))
RB['days'] = [[lab(day(x)), *dl[x]['rb']] for x in dk if 'rb' in dl[x]]

# ---------- CB (Cashback) ----------
CB = s['CB']; l6 = rows[-6:]
CB['n'] = sum(r['n'] for r in l6); CB['nu'] = sum(r['nu'] for r in l6); CB['perDay'] = raw['purchases_yesterday']
for i, b in enumerate(CB['buckets']): b[1] = C['cb.b%d' % i]
CB['never'] = [C['cb.never%d' % j] for j in range(5)]
CB['inact'] = [C['cb.inact%d' % j] for j in range(5)]
for i, x in enumerate(CB['lvl']): x[1] = C['cb.lvl%d' % i]
for k in ('used', 'neverUsed', 'sp30', 'sp7'): CB[k] = C['cb.' + k]
CB['days'] = [[lab(day(x)), *dl[x]['cb']] for x in dk if 'cb' in dl[x]]

# ---------- RAW (grupy, statusy, LTV, historia RFM) ----------
SEGG = {'R1': 143, 'R2': 145, 'R3': 146, 'R4': 147, 'R5': 149}
for g in s['RAW']['rfm'] + s['RAW']['loy']:
    k = g['k']; old = g['tot'] or 1; g['tot'] = C['raw.%s.tot' % k]
    g['r'][0:9] = [C['raw.%s.%d' % (k, j)] for j in range(9)]
    g['r'][9:13] = [round(v * g['tot'] / old) for v in g['r'][9:13]]
    g['ltv'] = [C['ltv.%s.%d' % (k, x)] for x in (662, 663, 664, 682, 683, 684)]
    if k in SEGG:
        m = mem(SEGG[k]); ds = [D0 - dt.timedelta(i) for i in range(29, -1, -1)]
        g['hist'] = [m[d][2] for d in ds]; g['e'] = [m[d][0] for d in ds]; g['l'] = [m[d][1] for d in ds]

# ---------- CHURN ----------
CH = s['CHURN']
CH['base'] = C['churn.base']; CH['flag'] = C['churn.flag']
CH['st'] = {k: C['churn.st.' + k] for k in ('act', 'd030', 'd3190', 'd90')}
CH['grp'] = {**{k: C['churn.grp.' + k] for k in ('CHA', 'LOY', 'R1', 'R2', 'R3', 'R4', 'R5')}, 'POT': 0, 'NEW': 0}
m655 = mem(655); CH['lost30'] = sum(m655[D0 - dt.timedelta(i)][0] for i in range(30))
CH['day'] = series(531, '2026-08-07', 2)
# tygodnie (resolution=weeks, tygodnie od czwartku); pierwszy kubełek bywa niepełny -> pomijany, bieżący niepełny tydzień też
mw = raw['membership_weeks']['531']; w0 = day(mw['start']); wk = {'lab': [], 'out': [], 'back': []}
for i in range(1, len(mw['e'])):
    ws = w0 + dt.timedelta(7 * i)
    if ws + dt.timedelta(6) >= D0: break
    wk['lab'].append(lab(ws)); wk['out'].append(mw['e'][i]); wk['back'].append(mw['l'][i])
CH['wk'] = wk

# ---------- serie dzienne ----------
s['ACTIVE_T'] = series(528, '2026-07-06', 2)
for sg in (28, 51, 71, 75, 523): s['CONS']['c%d' % sg] = series(sg, s['CONS']['start'], 2)
SE = s['SER']
SE['newc'] = series(488, SE['newc_start'], 0)
SE['lead_e'], SE['lead_l'], SE['lead_t'] = (series(551, SE['lead_start'], i) for i in (0, 1, 2))
SE['p800_e'] = series(636, SE['p800_start'], 0); SE['p800_buy'] = series(639, SE['p800_start'], 0)

# ---------- LEAD / LB ----------
L = s['LEAD']
for k in ('open30', 'click30', 'atrisk', 'sunCand', 'sunsetted', 'remove', 'sms', 'push', 'app', 'cart', 'checkout', 'engaged'):
    L[k] = C['lead.' + k]
m551 = mem(551); ds = [D0 - dt.timedelta(i) for i in range(30, -1, -1)]
L['e'] = [m551[d][0] for d in ds]; L['l'] = [m551[d][1] for d in ds]; L['hist'] = [m551[d][2] for d in ds]
L['tot'] = C['lb.tot']
LB = s['LB']; LB['tot'] = C['lb.tot']
for i, x in enumerate(LB['ev']): x[1] = C['lb.ev%d' % i]
for i, x in enumerate(LB['pg']): x[1] = C['lb.pg%d' % i]
for i, x in enumerate(LB['buy']): x[1] = C['lb.buy%d' % i]

# ---------- STATIC ----------
S = s['STATIC']
ten = C['app.ordA.648'] + C['app.ordN.648']
for x, v in zip(S['ladder'], [C['lad.2'], C['lad.3'], C['lad.4'], C['lad.5'], C['lad.6'], C['lad.ge6'], ten]): x['v'] = v
for x, v in zip(S['life'], [C['lad.2'], C['lad.3'], C['app.buy30'], C['seg.act'], C['seg.end7']]): x['v'] = v
for x, k in zip(S['gap'], (658, 659, 660, 661)): x['v'] = C['seg.%d' % k]
for x, k in zip(S['prod'], (671, 672, 675, 673, 674)): x['v'] = C['seg.%d' % k]
S['prodC']['big'] = C['app.buy30']
dd = [x for r in rows for x in r['dd']]
b = [sum(1 for x in dd if x == 1), sum(1 for x in dd if 2 <= x <= 4), sum(1 for x in dd if 5 <= x <= 9),
     sum(1 for x in dd if 10 <= x <= 19), sum(1 for x in dd if x >= 20)]
for x, v in zip(S['days'], b): x['v'] = v
med = int(statistics.median(dd)); S['daysC']['big'] = '1 dzień' if med == 1 else '%d dni' % med
ex, cb, tu = (sum(r[k] for r in rows) for k in ('ex', 'cb', 'tu')); T = ex + cb + tu
for x, v in zip(S['pay'], (ex, cb, tu)): x['v'] = round(100 * v / T, 1); x['t'] = '%d%%' % round(100 * v / T)
S['payC']['big'] = '%d zł' % round(RB['v'] / RB['n'])

# ---------- P8 (800+) ----------
P = s['P8']
for k in ('members', 'enr', 'susp', 'buy', 'buy2', 'buy3', 'eatNoBuy', 'disc', 'w13', 'w45'): P[k] = C['p8.' + k]
P['st'] = {k: C['p8.st.' + k] for k in ('eat', 'r030', 'l30')}
P['who'] = {k: C['p8.who.' + k] for k in ('lead', 'o1', 'o23', 'o4')}
P['whoBuy'] = {k: C['p8.whoBuy.' + k] for k in ('lead', 'o1', 'o23', 'o4')}
P['rfm'] = {'tot': C['p8.enr'], 'r': [C['p8.rfm.' + g] for g in ('R1', 'R2', 'R3', 'R4', 'R5')]}
st8 = day('2026-09-28'); n8 = (D0 - st8).days + 1
P['day'] = {'e': series(636, '2026-09-28', 0), 'b': series(639, '2026-09-28', 0),
            'lab': [lab(st8 + dt.timedelta(i)) for i in range(n8)]}
cm = raw['camp']; P['camp'][0][2:6] = cm['157']['email']; P['camp'][1][2:6] = cm['158']['push']


# =================== stałe HTML ===================
LTV = (662, 663, 664, 682, 683, 684); ORD = (642, 643, 644, 645, 646, 647, 648)
sa = collections.defaultdict(lambda: [0, 0, 0])
for r in l6:
    for k, n, v, d in r['src']: sa[k][0] += n; sa[k][1] += v; sa[k][2] += d
pm = raw['push_monthly']
APP = dict(
    cmp=dict(cl=[C['app.clients'], C['app.clNo']],
             ltvB=[[C['app.ltvA.%d' % x] for x in LTV], [C['app.ltvN.%d' % x] for x in LTV]],
             ordB=[[C['app.ordA.%d' % x] for x in ORD], [C['app.ordN.%d' % x] for x in ORD]],
             eat=[C['app.eat'], C['app.eatNoApp']],
             ord=[sa['app'][0], sa['web'][0]], val=[sa['app'][1], sa['web'][1]], code=[sa['app'][2], sa['web'][2]]),
    **{k: C['app.' + k] for k in ('users', 'ios', 'android', 'op30', 'op7', 'pushCons', 'pushReach', 'clients', 'o4',
                                  'eat', 'eatNoApp', 'inact', 'buy30', 'buyApp30', 'buyWeb30', 'buyAppEver')},
    push=dict(lab=pm['lab'], sent=pm['s'], **{'del': pm['d']}, open=pm['o'], conv=pm['cv']))
# Osiągalni pushem = zgoda na push × realny odsetek dostarczeń pushy w ostatnim pełnym miesiącu
# (segment 198 zawyża: tokeny wygasłe / odinstalowana aplikacja; broadcast 357: 3324 wysł. → 1242 dostarcz.)
APP['pushRate'] = round(pm['d'][-1] / pm['s'][-1], 4) if pm['s'][-1] else None
APP['pushReach'] = round(C['app.pushCons'] * APP['pushRate']) if APP['pushRate'] else C['app.pushReach']
EMR = {g: C['emr.' + g] for g in ('R1', 'R2', 'R3', 'R4', 'R5')}
APPR = {g: [C['appr.%s.%d' % (g, j)] for j in range(10)] for g in ('CHA', 'LOY', 'POT', 'NEW', 'R1', 'R2', 'R3', 'R4', 'R5')}

# NK: pierwsze zamówienia w oknach k dni
Nk = {d: C['nk.p1.%d' % d] + C['nk.p2.%d' % d] for d in (1, 2, 7, 14, 30, 60, 90, 180)}
NK = {1: [Nk[1], Nk[2] - Nk[1]], 7: [Nk[7], Nk[14] - Nk[7]], 14: [Nk[14], None], 30: [Nk[30], Nk[60] - Nk[30]], 60: [Nk[60], None], 90: [Nk[90], None]}
# DMAP: dni dostaw do końca
DX = (650, 651, 814, 815, 816, 817, 818)
dm = {'all': [C['dmap.all.%d' % x] for x in DX]}
for g in ('R1', 'R2', 'R3', 'R4', 'R5'): dm[g] = [C['raw.%s.0' % g], C['raw.%s.1' % g]] + [C['dmap.%s.%d' % (g, x)] for x in DX[2:]]
# CHURNP
CHURNP = {p: {g: [C['churnp.%s.%d' % (g, a)], C['churnp.%s.%d' % (g, a + 1)]] for g in ('R1', 'R2', 'R3', 'R4')}
          for p, a in ((1, 831), (7, 833), (90, 835))}
# WT + NCR z listy aktywnych klientów (649)
WT = collections.Counter(); NCR = []
for p in raw['active_pages'].values():
    for g, n in p['w']: WT[g] += n
    NCR += p['n']
WT = {'R%d' % (g + 1): WT.get(g, 0) for g in range(5)}
# Czekający: ile dni do startu pierwszej dostawy (strony 649, pole wait_days: [grupa, dni do startu])
WAITB = None
if raw.get('wait_days'):
    WB = collections.defaultdict(lambda: [0, 0, 0])
    for p in raw['wait_days'].values():
        for g, d in p:
            if g > 4: continue
            WB['R%d' % (g + 1)][0 if d <= 3 else 1 if d <= 7 else 2] += 1
    WAITB = {k: WB[k] for k in ('R1', 'R2', 'R3', 'R4', 'R5')}
    WT = {k: sum(v) for k, v in WAITB.items()}
NCR.sort(key=lambda r: (-r[0], r[1]))
# NCSEC: 2. zamówienie w trakcie diety z 1. zamówienia (klienci 643, 1. zamówienie w 30 dni)
den = sum(p[0] for p in raw['sec_pages'].values()); dur = sum(p[1] for p in raw['sec_pages'].values())
NCSEC = [dur, den]
# FLOWS
FL = raw['flows']; fst = day(FL['start']); nd = (D0 - fst).days + 1
FC = {}
for cid, mt in FL['meta'].items():
    c = {'n': mt['n'], 't': mt['t'], 'st': mt['st']}
    mm = FL['metrics'].get(cid) if mt['m'] else None
    if mm:
        c['m'] = [([0] * (nd - len(a)) + a)[-nd:] for a in mm['d']]
    else: c['m'] = None
    gs = [FL['goals'].get(str(fst + dt.timedelta(i)), {}).get(cid, [0, 0]) for i in range(nd)]
    c['c'] = [g[0] for g in gs]; c['r'] = [g[1] for g in gs]
    c['mw'] = mm['w'] if mm else None; c['mm'] = mm['m'] if mm else None
    FC[cid] = c
FLOWS = {'start': FL['start'], 'days': nd, 'c': FC}
NAMES = {'all': 'Wszyscy', 'R1': 'Czempioni', 'R2': 'Lojalni', 'R3': 'Obiecujący', 'R4': 'Okazjonalni', 'R5': 'Niska wartość'}
DMAP_B = [['0–3', 0, 3, 650], ['4–7', 4, 7, 651], ['8–14', 8, 14, 814], ['15–21', 15, 21, 815], ['22–30', 22, 30, 816], ['31–60', 31, 60, 817], ['61+', 61, 90, 818]]

# Wszystko trafia do jednego dokumentu w bazie (snapshot/current). HTML NIE jest zmieniany —
# strona przy otwarciu czyta dane z bazy (applyData: klucze snapshotu + s['H']) i sama się przelicza/renderuje.
s['APP'] = APP
# WKD: weekend. o = zamówienia per dzień (ostatnie 8 pełnych tygodni do wczoraj), d = dostawy w najbliższe 2 weekendy
# z harmonogramów (najnowsze zdarzenie diet_delivery_schedule per dieta, logi ~30 dni wstecz).
OD = raw.get('orders_day', {}); od = sorted(k for k in OD if k < raw['asof'])[-56:]
ep = lambda d: (d - dt.date(1970, 1, 1)).days
WS = D0 - dt.timedelta(1) if D0.weekday() == 6 else D0 + dt.timedelta((5 - D0.weekday()) % 7)
wkd = []
for k in range(2):
    sa = WS + dt.timedelta(7 * k); a, b = ep(sa), ep(sa) + 1
    sat = [v for v in raw.get('wk_sched', {}).values() if a in v[1]]; sun = [v for v in raw.get('wk_sched', {}).values() if b in v[1]]
    anyd = [v for v in raw.get('wk_sched', {}).values() if a in v[1] or b in v[1]]
    both = {v[0] for v in sat} & {v[0] for v in sun}
    wkd.append({'sat': str(sa), 'd': [len(sat), len(sun), len(anyd)], 'p': [len({v[0] for v in sat}), len({v[0] for v in sun}), len({v[0] for v in anyd}), len(both)]})
WKD = {'o': {'dates': od, 'n': [OD[k][0] for k in od], 'v': [OD[k][1] for k in od]}, 'd': wkd}
# Historia kafli segmentów (Czekają / Aktywni / Zagrożeni / Nieaktywni) — dopisywana przy każdym przeliczeniu.
# Customer.io nie trzyma wstecznej historii segmentów statusów (powstały 1 paź), więc zbieramy ją sami od 2026-10-03.
HG = ('R1', 'R2', 'R3', 'R4', 'R5', 'CHA', 'LOY', 'POT', 'NEW')
row = {g: [WT.get(g), C['raw.%s.2' % g], sum(C['raw.%s.%d' % (g, j)] for j in (3, 4, 5)), sum(C['raw.%s.%d' % (g, j)] for j in (6, 7, 8))] for g in HG}
row['all'] = [sum(row[g][k] or 0 for g in ('R1', 'R2', 'R3', 'R4', 'R5')) for k in range(4)]
hist = raw.setdefault('seg_hist', {}); hist[raw['asof']] = row
WKD['act'] = row['all'][1]  # aktywni (jedzą teraz) jako mianownik udziału
json.dump(raw, open(os.path.join(D, 'raw.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
SEGH = {'dates': sorted(hist)[-90:]}
SEGH['v'] = {g: [hist[d].get(g) for d in SEGH['dates']] for g in list(HG) + ['all']}
s['H'] = {'WKD': WKD, 'SEGH': SEGH, 'WAITB': WAITB, 'EMR': EMR, 'APPR': APPR, 'CHURNP': CHURNP, 'WT': WT, 'NCR': NCR, 'NK': NK, 'NCSEC': NCSEC, 'FLOWS': FLOWS,
          'DMAP': {'asof': raw['asof'], 'b': DMAP_B, 'g': {g: [NAMES[g], dm[g]] for g in NAMES}}}
s['asOf'] = raw['asof']; s['updatedAt'] = int(time.time() * 1000); s['v'] = 1
json.dump(s, open(os.path.join(D, 'snapshot.json'), 'w'), ensure_ascii=False)
print('OK', raw['asof'], '| RB.n', RB['n'], '| LEAD.tot', L['tot'], '| NCR', len(NCR), '| WT', WT, '| NCSEC', NCSEC, '| FLOWS.days', nd,
      '| rozmiar dokumentu %.0f KB' % (len(json.dumps(s, ensure_ascii=False).encode()) / 1024))

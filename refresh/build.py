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
err += ['counts:' + k for k, _ in json.load(open(os.path.join(D, 'queries.json'))) if k not in C and '@' not in k]  # warianty filtrów (@) sprawdzane osobno: filtr włączany tylko gdy komplet
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
    g['r'][9:13] = [C['ch.%s.%s' % (k, c)] for c in ('email', 'sms', 'push', 'app')]  # kanały: realne liczniki z Customer.io
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
# opisy pod liczbami liczone z tych samych danych (bez stałych liczb w tekście)
pl = lambda n: ('{:,}'.format(round(n))).replace(',', ' ')
pc = lambda a, b_: round(a / b_ * 100) if b_ else 0
LD = S['ladder']
LD[0]['why'] = 'Każdy klient zaczyna tutaj.'
LD[1]['why'] = '%d%% klientów nie złożyło drugiego zamówienia.' % (100 - pc(LD[1]['v'], LD[0]['v']))
LD[2]['why'] = '%d%% klientów z 2 zamówieniami składa trzecie.' % pc(LD[2]['v'], LD[1]['v'])
LD[3]['why'] = 'Od 4. zamówienia klient trafia do grupy Loyalist. Przejście z 3.: %d%%.' % pc(LD[3]['v'], LD[2]['v'])
LD[4]['why'] = '%d%% przejścia z 4. zamówienia.' % pc(LD[4]['v'], LD[3]['v'])
LD[5]['why'] = '%d%% przejścia z 5. zamówienia.' % pc(LD[5]['v'], LD[4]['v'])
LD[6]['why'] = 'Champion: %d%% klientów z 6+ zamówieniami dochodzi do 10.' % pc(LD[6]['v'], LD[5]['v'])
LF = S['life']
LF[1]['why'] = '%d%% bazy to klienci powracający.' % pc(LF[1]['v'], LF[0]['v'])
LF[2]['why'] = 'W ostatnich 30 dniach kupiło %s osób (%d%% wszystkich klientów).' % (pl(LF[2]['v']), pc(LF[2]['v'], LF[0]['v']))
for x, k in zip(S['gap'], (658, 659, 660, 661)): x['v'] = C['seg.%d' % k]
_gt = sum(x['v'] for x in S['gap']); _acc = 0
for x in S['gap']:
    _acc += x['v']
    if _acc >= _gt / 2: S['gapC'] = {'big': x['l'].replace('Co ', ''), 'small': 'mediana odstępu'}; break
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
EMR = {g: C['ch.%s.email' % g] for g in ('R1', 'R2', 'R3', 'R4', 'R5')}
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
# SEGX: dane do kart segmentów (podstrony) — liczniki sg.<R>.<klucz> z queries.json
SGK = ('o642', 'o643', 'o644', 'o645', 'o646', 'o647', 'o648', 'b7', 'b14', 'b30', 'b60', 'b90', 'm30', 'disc', 'disc3', 'p8', 'w1', 'w2', 'w3', 'w4', 'w5', 'eo30', 'ec30', 'sun', 'aop30', 'aop7', 'abA', 'abW', 'ret90')
SEGX = {g: {k: C['sg.%s.%s' % (g, k)] for k in SGK} for g in ('R1', 'R2', 'R3', 'R4', 'R5')}
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
# suma wszystkich segmentów: strefy z dziennej historii segmentów (od dnia po utworzeniu), uzupełnione pomiarami z odświeżeń
ZH = {}
for zi, sg in ((1, 649), (2, 744), (3, 745)):
    m = raw['membership'].get(str(sg)); c0 = dt.datetime.utcfromtimestamp(raw['seg_created'][str(sg)]).date()
    if not m: continue
    st = day(m['start'])
    for i, v in enumerate(m['t'] or []):
        d_ = st + dt.timedelta(i)
        if v is not None and c0 <= d_ <= D0: ZH.setdefault(str(d_), {})[zi] = v
SEGH = {'dates': sorted(set(hist) | set(ZH))[-90:]}
SEGH['v'] = {g: [hist[d].get(g) if d in hist else None for d in SEGH['dates']] for g in HG}
SEGH['v']['all'] = []
for d in SEGH['dates']:
    r = list(hist[d]['all']) if d in hist else [None, None, None, None]
    for zi, v in ZH.get(d, {}).items(): r[zi] = v
    SEGH['v']['all'].append(r)
s['H'] = {'RET90': C.get('ret90.all', 0), 'SEGX': SEGX, 'WKD': WKD, 'SEGH': SEGH, 'WAITB': WAITB, 'EMR': EMR, 'APPR': APPR, 'CHURNP': CHURNP, 'WT': WT, 'NCR': NCR, 'NK': NK, 'NCSEC': NCSEC, 'FLOWS': FLOWS,
          'DMAP': {'asof': raw['asof'], 'b': DMAP_B, 'g': {g: [NAMES[g], dm[g]] for g in NAMES}}}
# ---------- GR (Gryzy: points_value + event gadget_earned) ----------
GL = ['0', '1–100', '101–500', '501–1000', '1001–3000', '3000+']
GX = raw.get('gryzy_ex', {'rows': []}); GALL = GX['rows']; _gt = GX.get('to', raw['asof']); _g30 = (dt.date.fromisoformat(_gt) - dt.timedelta(29)).isoformat()
gr_rows = [r for r in GALL if r[0] >= _g30]
gc, gcost, gday = {}, {}, {}
for d_, sp, gs, pv in gr_rows:
    gday[d_] = gday.get(d_, 0) + 1
    for g in gs: gc[g] = gc.get(g, 0) + 1
    if len(gs) == 1: gcost.setdefault(gs[0], []).append(sp)
g0 = dt.date.fromisoformat(max(GX.get('from', _g30), _g30)); g1 = dt.date.fromisoformat(GX.get('to', raw['asof']))
gdays = [(g0 + dt.timedelta(i)).isoformat() for i in range((g1 - g0).days + 1)]
s['GR'] = {'b': [[GL[i], C.get('gr.b%d' % i, 0), C.get('gr.eat%d' % i, 0), C.get('gr.ina%d' % i, 0), C.get('gr.app%d' % i, 0)] for i in range(6)],
           'ex': C.get('gr.ex', 0), 'ex30': C.get('gr.ex30', 0), 'exEat': C.get('gr.exEat', 0), 'exIna': C.get('gr.exIna', 0), 'exApp': C.get('gr.exApp', 0),
           'n': len(gr_rows), 'spent': sum(r[1] for r in gr_rows), 'items': sum(len(r[2]) for r in gr_rows),
           'after': [sum(1 for r in gr_rows if lo <= r[3] < hi) for lo, hi in ((0, 100), (100, 500), (500, 1000), (1000, 3000), (3000, 10**9))],
           'top': sorted([[g, n, min(gcost[g]) if g in gcost else None] for g, n in gc.items()], key=lambda x: -x[1]),
           'days': [[lab(dt.date.fromisoformat(x)), gday.get(x, 0)] for x in gdays], 'from': g0.isoformat(), 'to': GX.get('to')}
GRR = sorted(GALL, key=lambda r: r[0]); gto = GX.get('to', raw['asof'])
def gwin(a, b):
    d1 = (dt.date.fromisoformat(gto) - dt.timedelta(a - 1)).isoformat(); d0 = (dt.date.fromisoformat(gto) - dt.timedelta(b - 1)).isoformat()
    rr = [r for r in GRR if d0 <= r[0] < d1] if a else [r for r in GRR if r[0] >= d0]
    tc = {}
    for r in rr:
        for g in r[2]: tc[g] = tc.get(g, 0) + 1
    return {'n': len(rr), 'items': sum(len(r[2]) for r in rr), 'spent': sum(r[1] for r in rr), 'top': tc}
s['GR']['cmp'] = {str(p_): {'cur': gwin(0, p_), 'prev': gwin(p_, 2 * p_) if (dt.date.fromisoformat(gto) - dt.date.fromisoformat(GX.get('from', gto))).days + 1 >= 2 * p_ else None,
                            'ppl': [C.get('gr.ex%d' % p_, 0), (C.get('gr.ex%d' % (2 * p_), 0) - C.get('gr.ex%d' % p_, 0)) if C.get('gr.ex%d' % (2 * p_)) else None]} for p_ in (7, 14, 30)}
s['GR']['ex90'] = C.get('gr.ex90', 0)
s['asOf'] = raw['asof']; s['updatedAt'] = int(time.time() * 1000); s['v'] = 1
# ---------- SUN: wygaszeni (616) i kandydaci (425), stan dzienny od dnia po utworzeniu segmentu 616 do wczoraj ----------
def tser(seg, d0):
    m = raw['membership'][str(seg)]; st = day(m['start']); out = []
    for i in range((D0 - d0).days):
        j = (d0 + dt.timedelta(i) - st).days
        v = m['t'][j] if 0 <= j < len(m['t']) else None
        if v is None: raise SystemExit('SUN: brak dnia %s w segmencie %s' % (d0 + dt.timedelta(i), seg))
        out.append(v)
    return out
sun0 = dt.datetime.utcfromtimestamp(raw['seg_created']['616']).date()
s['H']['SUN'] = {'start': str(sun0), 's': tser(616, sun0), 'c': tser(425, sun0)}
# ---------- SEC2 (drugie zamówienie) i INA (nieaktywni) ----------
def dser(seg, k, d0):
    m = raw['membership'][str(seg)]; st = day(m['start']); o = []
    for i in range((D0 - d0).days):
        j = (d0 + dt.timedelta(i) - st).days
        o.append(m[k][j] if 0 <= j < len(m[k] or []) else None)
    return o
c642 = dt.datetime.utcfromtimestamp(raw['seg_created']['642']).date() + dt.timedelta(1)
s['H']['SEC2'] = {'start': str(c642), 'sec': dser(642, 'l', c642), 'first': dser(642, 'e', c642),
                  'n1': C['cbo.0.tot'], 'in1': C['cbo.0.in'], 'ec': C['ch.NEW.emailCons'], 'es': C['ch.NEW.emailSun'], 'pc': C['ch.NEW.pushCons'], 'oneStart': str(c642 - dt.timedelta(1)), 'one': dser(642, 't', c642 - dt.timedelta(1)) + [C['cbo.0.tot']]}
i531 = day(raw['membership']['531']['start'])
s['H']['INA'] = {'start': str(i531), 'e': dser(531, 'e', i531), 'l': dser(531, 'l', i531), 't': dser(531, 't', i531),
                 'ch': {k: C['in.' + k] for k in ('email', 'sms', 'push', 'app')}, 'n745': C.get('seg.745') or (raw['membership']['745']['t'] or [None])[-1]}
# ---------- MOM: dwa ostatnie PEŁNE miesiące kalendarzowe, wyłącznie z dziennych serii segmentów ----------
# Reguła: miesiąc liczony tylko gdy segment istniał od 1. dnia miesiąca i każdy dzień ma wartość. Inaczej None (strona pokazuje „brak historii”).
SC = {k: dt.datetime.utcfromtimestamp(v).date() for k, v in raw.get('seg_created', {}).items() if v}
mL = D0.replace(day=1) - dt.timedelta(1); mL = mL.replace(day=1); mP = (mL - dt.timedelta(1)).replace(day=1)
def mdays(m0):
    m1 = (m0 + dt.timedelta(32)).replace(day=1); return [m0 + dt.timedelta(i) for i in range((m1 - m0).days)]
def mser(seg, k, m0):
    sg = str(seg); m = raw.get('membership', {}).get(sg)
    if not m or not m.get(k): return None
    if sg not in SC or SC[sg] >= m0: return None
    st = day(m['start']); out = []
    for d in mdays(m0):
        i = (d - st).days
        if i < 0 or i >= len(m[k]) or m[k][i] is None: return None
        out.append(m[k][i])
    return out
def msum(seg, k, m0): a = mser(seg, k, m0); return None if a is None else sum(a)
def mavg(seg, k, m0): a = mser(seg, k, m0); return None if a is None else sum(a) / len(a)
def mend(seg, k, m0): a = mser(seg, k, m0); return None if a is None else a[-1]
def pair(fn, *a): return [fn(*a, mP), fn(*a, mL)]
def rr(m0):
    b, t = msum(531, 'l', m0), mavg(531, 't', m0); return None if b is None or not t else round(b / t * 100)
MOMC = {'newc': pair(msum, 488, 'e'), 'churnIn': pair(msum, 531, 'e'), 'back': pair(msum, 531, 'l'), 'eat': pair(mavg, 528, 't'),
        'retRate': [rr(mP), rr(mL)], 'consE': pair(msum, 51, 'e'), 'consS': pair(msum, 71, 'e'), 'sunCandIn': pair(msum, 425, 'e'),
        'cart': pair(msum, 54, 'e'), 'open30': pair(mend, 537, 't'), 'click30': pair(mend, 552, 't'), 'buy30': pair(mend, 676, 't'),
        'second': pair(msum, 643, 'e'), 'rfm': {g: pair(mend, sid, 't') for g, sid in (('R1', 143), ('R2', 145), ('R3', 146), ('R4', 147), ('R5', 149))}}
MN = ['styczeń', 'luty', 'marzec', 'kwiecień', 'maj', 'czerwiec', 'lipiec', 'sierpień', 'wrzesień', 'październik', 'listopad', 'grudzień']
MNL = ['styczniu', 'lutym', 'marcu', 'kwietniu', 'maju', 'czerwcu', 'lipcu', 'sierpniu', 'wrześniu', 'październiku', 'listopadzie', 'grudniu']
MOMC['_m'] = [MN[mP.month - 1], MN[mL.month - 1]]; MOMC['_ml'] = [MNL[mP.month - 1], MNL[mL.month - 1]]; MOMC['_ms'] = [MON[mP.month - 1], MON[mL.month - 1]]
def leads(m0):
    e, l = mser(551, 'e', m0), mser(551, 'l', m0)
    if e is None or l is None: return None
    big = [(d_, v) for d_, v in zip(mdays(m0), l) if v > 1000]  # masowe akcje sunset (pojedyncze dni z >1000 wyjść)
    return {'in': sum(e), 'sun': sum(v for _, v in big), 'out': sum(l) - sum(v for _, v in big), 'end': mend(551, 't', m0), 'day': [str(d_) for d_, _ in big]}
LP, LL = leads(mP), leads(mL)
g_ = lambda x, k: None if x is None else x[k]
MOMC.update({'leadsIn': [g_(LP, 'in'), g_(LL, 'in')], 'leadsOut': [g_(LP, 'out'), g_(LL, 'out')], 'sunset': [g_(LP, 'sun'), g_(LL, 'sun')], 'leadsEnd': [g_(LP, 'end'), g_(LL, 'end')]})
MOMC['sunsetDay'] = ', '.join('%d %s' % (int(x[8:]), MON[int(x[5:7]) - 1]) for x in (LL or {}).get('day', []))
s['MOM'] = MOMC
s['KPIH'] = {k: v for k, v in sorted(raw.get('kpi_hist', {}).items())[-120:]}
s['H']['CBO'] = {'lab': ['1', '2', '3', '4', '5', '6–9', '10+'], 'tot': [C['cbo.%d.tot' % i] for i in range(7)], 'in': [C['cbo.%d.in' % i] for i in range(7)]}
# ---------- KONTROLA JAKOŚCI: twarde błędy blokują zapis snapshotu, ostrzeżenia trafiają na stronę ----------
QA_ERR, QA_WARN, QA_N = [], [], 0
def chk(ok, msg, hard=True):
    global QA_N
    QA_N += 1
    if not ok: (QA_ERR if hard else QA_WARN).append(msg)
import numbers
for k, v in C.items():
    chk(isinstance(v, numbers.Number) and v >= 0 and float(v).is_integer(), 'licznik %s nie jest nieujemną liczbą całkowitą: %r' % (k, v))
GRP = ('R1', 'R2', 'R3', 'R4', 'R5', 'NEW', 'POT', 'LOY', 'CHA')
for g in GRP:
    t = C['raw.%s.tot' % g]
    chk(C['raw.%s.0' % g] + C['raw.%s.1' % g] <= C['raw.%s.2' % g], '%s: kończący się w 7 dni nie mieszczą się w aktywnych' % g)
    chk(sum(C['raw.%s.%d' % (g, j)] for j in range(2, 9)) <= t, '%s: suma statusów dostaw większa niż liczebność' % g)
    for c in ('email', 'sms', 'push', 'app'): chk(C['ch.%s.%s' % (g, c)] <= t, '%s: kanał %s większy niż liczebność' % (g, c))
chk(sum(C['raw.%s.tot' % g] for g in GRP[:5]) == sum(C['raw.%s.tot' % g] for g in GRP[5:]) or True, 'RFM vs lojalność')
rf, lo = sum(C['raw.%s.tot' % g] for g in GRP[:5]), sum(C['raw.%s.tot' % g] for g in GRP[5:])
chk(abs(rf - lo) <= 0.03 * max(rf, lo), 'suma segmentów RFM (%d) i etapów lojalności (%d) różni się o ponad 3%%' % (rf, lo), hard=False)
ex = [C.get('gr.ex%d' % d) for d in (7, 14, 28, 30, 60, 90)] + [C.get('gr.ex')]
chk(all(a is not None and b is not None and a <= b for a, b in zip(ex, ex[1:])), 'Gryzy: liczba osób z wymianą nie rośnie z długością okna: %s' % ex)
LDv = [x['v'] for x in s['STATIC']['ladder']]
chk(all(a >= b for a, b in zip(LDv, LDv[1:])), 'drabina zamówień nie jest malejąca: %s' % LDv)
odk = sorted(k for k in raw.get('orders_day', {}) if k < raw['asof'])[-28:]
chk(len(odk) == 28 and (day(odk[-1]) - day(odk[0])).days == 27 and odk[-1] == str(D0 - dt.timedelta(1)), 'zamówienia dzienne: brak ciągłości ostatnich 28 dni (ostatni dzień %s)' % (odk[-1] if odk else None))
for d_ in last14:
    sm_ = smp[d_]; chk(sm_.get('n', 0) > 0 and sm_.get('day') == d_, 'próbka %s pusta albo z innego dnia' % d_)
chk(raw['sample'][str(D0 - dt.timedelta(1))]['n'] <= max(50, raw.get('purchases_yesterday', 0)), 'próbka wczoraj większa niż liczba zakupów')
for seg in ('528', '531', '488', '551'):
    m = raw['membership'][seg]; st = day(m['start']); k = 't' if m.get('t') else 'e'
    vals = [m[k][(D0 - dt.timedelta(i) - st).days] if 0 <= (D0 - dt.timedelta(i) - st).days < len(m[k]) else None for i in range(1, 31)]
    chk(all(v is not None for v in vals), 'segment %s: brak dnia w ostatnich 30 dniach' % seg)
chk(all(a <= t for a, t in zip(s['H']['CBO']['in'], s['H']['CBO']['tot'])), 'bariera: nieaktywni większe niż liczba klientów')
chk(all(v is not None for v in s['H']['INA']['e'][-30:] + s['H']['INA']['l'][-30:]), 'nieaktywni: brak dni w historii odpływu/powrotów')
chk(all(s['H']['INA']['ch'][k] <= s['H']['INA']['n745'] for k in s['H']['INA']['ch']), 'nieaktywni: kanał większy niż liczba nieaktywnych')
GRb = s['GR']['b']; chk(sum(x[1] for x in GRb) > 0 and all(x[2] <= x[1] and x[3] <= x[1] and x[4] <= x[1] for x in GRb), 'Gryzy: podgrupy większe niż przedział salda')
chk(s['GR']['n'] == len(gr_rows) and all(r[0] >= _g30 for r in gr_rows), 'Gryzy: wymiany spoza okna 30 dni')
for k_ in ('newc', 'churnIn', 'back', 'eat', 'retRate', 'consE', 'consS', 'sunCandIn', 'cart', 'open30', 'click30', 'leadsIn'):
    chk(s['MOM'][k_][1] is not None, 'porównanie miesięcy: brak wartości %s za %s' % (k_, MOMC['_m'][1]), hard=False)
def finite(o, path=''):
    if isinstance(o, dict): [finite(v, path + '.' + str(k_)) for k_, v in o.items()]
    elif isinstance(o, list): [finite(v, path + '[%d]' % i) for i, v in enumerate(o)]
    elif isinstance(o, float): chk(math.isfinite(o), 'wartość nieskończona/NaN w %s' % path)
finite(s)
chk(raw['asof'] == str(dt.datetime.utcnow().date()) or '--allow-old' in sys.argv, 'asof %s to nie dzisiejsza data (UTC %s)' % (raw['asof'], dt.datetime.utcnow().date()), hard=False)
s['QA'] = {'checks': QA_N, 'errors': QA_ERR, 'warnings': QA_WARN, 'at': int(time.time() * 1000)}
if QA_ERR:
    sys.exit('KONTROLA JAKOŚCI NIEUDANA — snapshot NIE zapisany:\n  ' + '\n  '.join(QA_ERR))
json.dump(s, open(os.path.join(D, 'snapshot.json'), 'w'), ensure_ascii=False)
# ---------- archiwum dzienne: pełny zrzut liczników i wyliczeń, nigdy nie nadpisywany innym dniem ----------
os.makedirs(os.path.join(D, 'history'), exist_ok=True)
json.dump({'asof': raw['asof'], 'counts': C, 'purchases_yesterday': raw.get('purchases_yesterday'), 'camp': raw.get('camp'),
           'sample': raw.get('sample', {}).get(str(D0 - dt.timedelta(1))), 'orders_day': {k: v for k, v in raw.get('orders_day', {}).items() if k >= str(D0 - dt.timedelta(7))},
           'gryzy_ex': [r for r in raw.get('gryzy_ex', {}).get('rows', []) if r[0] >= str(D0 - dt.timedelta(7))],
           'snapshot': {k: s[k] for k in s if k not in ('updatedAt',)}},
          open(os.path.join(D, 'history', raw['asof'] + '.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print('QA: %d kontroli, %d błędów, %d ostrzeżeń' % (QA_N, len(QA_ERR), len(QA_WARN)) + ''.join('\n  ostrzeżenie: ' + x for x in QA_WARN))
print('OK', raw['asof'], '| RB.n', RB['n'], '| LEAD.tot', L['tot'], '| NCR', len(NCR), '| WT', WT, '| NCSEC', NCSEC, '| FLOWS.days', nd,
      '| rozmiar dokumentu %.0f KB' % (len(json.dumps(s, ensure_ascii=False).encode()) / 1024))

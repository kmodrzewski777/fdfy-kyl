#!/usr/bin/env python3
"""raw.json (surowe wyniki Customer.io) -> snapshot.json + dashboard HTML.
Cała logika prezentacji jest tutaj. LLM przy odświeżaniu NIE liczy niczego ręcznie:
wypełnia raw.json wg queries.json i docs/AKTUALIZACJA_DANYCH.md, potem: python3 refresh/build.py
"""
import json, re, collections, statistics, os, sys
D = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(D, '..', 'dashboard', 'foodify-retencja.html')
raw = json.load(open(os.path.join(D, 'raw.json')))
s = json.load(open(os.path.join(D, 'snapshot.json')))  # szablon: pola nieliczone tu zostają bez zmian
C = raw['counts']
rows = sorted(raw['sample'], key=lambda x: x['day'])
miss = [k for k, _ in json.load(open(os.path.join(D, 'queries.json'))) if k not in C]
if miss: sys.exit('Brak liczników w raw.json: %s' % miss)

# ---------- RB (Rabaty) z próbki zamówień ----------
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
for w in RB['w']: w[4:8] = W[w[0]]
RB['perDay'] = raw['purchases_yesterday']

# ---------- CB (Cashback): ostatnie 6 dni próbki ----------
CB = s['CB']; l6 = rows[-6:]
CB['n'] = sum(r['n'] for r in l6); CB['nu'] = sum(r['nu'] for r in l6); CB['perDay'] = raw['purchases_yesterday']

# ---------- LEAD ----------
L = s['LEAD']
for k in ('open30', 'click30', 'atrisk', 'sunCand', 'sunsetted', 'remove', 'sms', 'push', 'app', 'cart', 'checkout', 'engaged'):
    L[k] = C['lead.' + k]
L.update(raw['lead_series']); L['tot'] = L['hist'][-1]

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
P = s['P8']; P['disc'] = C['p8.disc']; P['w13'] = C['p8.w13']; P['w45'] = C['p8.w45']
cm = raw['camp']
P['camp'][0][2:6] = cm['157']['email']; P['camp'][1][2:6] = cm['158']['push']

# ---------- RAW ltv per grupa ----------
for g in s['RAW']['rfm'] + s['RAW']['loy']:
    g['ltv'] = [C['ltv.%s.%d' % (g['k'], x)] for x in (662, 663, 664, 682, 683, 684)]

s['asOf'] = raw['asof']
json.dump(s, open(os.path.join(D, 'snapshot.json'), 'w'), ensure_ascii=False)

# ---------- stałe HTML ----------
LTV = (662, 663, 664, 682, 683, 684); ORD = (642, 643, 644, 645, 646, 647, 648)
src = {x[0]: x for r in l6 for x in []}
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
EMR = {g: C['emr.' + g] for g in ('R1', 'R2', 'R3', 'R4', 'R5')}
APPR = {g: [C['appr.%s.%d' % (g, j)] for j in range(10)] for g in ('CHA', 'LOY', 'POT', 'NEW', 'R1', 'R2', 'R3', 'R4', 'R5')}

h = open(HTML).read()
def js(o): return json.dumps(o, ensure_ascii=False, separators=(',', ':'))
def sub(pat, rep):
    global h
    h, n = re.subn(pat, lambda m: rep, h, count=1, flags=re.S)
    if n != 1: sys.exit('Nie znaleziono w HTML: ' + pat)
sub(r'let APP=\{.*?\}\};\n', 'let APP=' + js(APP) + ';\n')
sub(r'EMR=\{[^}]*\}', 'EMR=' + js(EMR))
sub(r'APPR=\{.*?\};', 'APPR=' + js(APPR) + ';')
i = h.index('try{applyData({') + len('try{applyData(')
j = i; depth = 0
while True:  # dopasuj klamry osadzonego snapshotu
    c = h[j]
    if c == '{': depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0: break
    elif c == '"':
        j += 1
        while h[j] != '"': j += 2 if h[j] == '\\' else 1
    j += 1
h = h[:i] + js(s) + h[j + 1:]
open(HTML, 'w').write(h)
print('OK', raw['asof'], 'RB.n', RB['n'], 'LEAD.tot', L['tot'], 'APP.users', APP['users'])

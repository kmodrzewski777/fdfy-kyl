#!/usr/bin/env python3
"""Wypisuje DOKŁADNIE wywołania cio_read_api potrzebne do odświeżenia. Użycie: python3 plan.py [YYYY-MM-DD] [--reset]
--reset czyści liczniki i strony klientów (pełne odświeżenie dnia). Wynik każdego wywołania zapisz put.py (ścieżka podana w linii)."""
import json, sys, os, base64, math, datetime as dt
D = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(D, 'raw.json')
raw = json.load(open(F)); args = [a for a in sys.argv[1:] if not a.startswith('--')]
D0 = dt.date.fromisoformat(args[0]) if args else dt.date.today()
ts = lambda d: int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp())
if '--reset' in sys.argv:
    for k in ('counts', 'active_pages', 'sec_pages', 'wait_days'): raw[k] = {}  # historia (membership, sample, flows) zostaje
    raw['asof'] = str(D0); json.dump(raw, open(F, 'w'), ensure_ascii=False, separators=(',', ':'))
E = 'path=/v1/environments/190673'
print('# 1. LICZNIKI  ->  put.py counts \'{"klucz":n,...}\'   (jq .meta.pagination.total, limit 1)')
for k, f in json.load(open(os.path.join(D, 'queries.json'))):
    if k not in raw.get('counts', {}):
        print('C', k, base64.b64encode(json.dumps(f, separators=(',', ':')).encode()).decode())
# segment: (od kiedy potrzebna historia, potrzebne pola). raw.membership trzyma całą historię — pobieraj tylko brakujące dni + ostatnie 8.
NEED = {528: ('2026-07-06', 't'), 488: ('2026-07-01', 'e'), 551: ('2026-07-14', 'elt'), 636: ('2026-09-28', 'e'), 639: ('2026-09-28', 'e'),
        531: ('2026-07-16', 'elt')}
for g in (28, 75, 523): NEED[g] = ('2025-10-01', 't')
for g in (51, 71): NEED[g] = ('2025-10-01', 'et')
# miesięczne porównanie (MOM): segmenty z historią dzienną od 1. dnia dwóch miesięcy wstecz
M0 = (D0.replace(day=1) - dt.timedelta(1)).replace(day=1); M0 = (M0 - dt.timedelta(1)).replace(day=1)
for g, fl in ((54, 'e'), (425, 'elt'), (616, 'elt'), (643, 'e'), (537, 't'), (552, 't'), (676, 't')): NEED[g] = (str(M0), fl)
for g in (143, 145, 146, 147, 149): NEED[g] = (str(min(D0 - dt.timedelta(29), M0)), 'elt')
for g in (649, 744, 745): NEED[g] = ('2026-10-01', 't')
NEED[642] = ('2026-10-01', 'elt')
NEED[655] = (str(D0 - dt.timedelta(29)), 'e')
print('\n# 1b. DATY UTWORZENIA SEGMENTÓW  path=/v1/environments/190673/segments jq=[.segments[]|[(.id|tostring),(.created_at//.created)]]|map({(.[0]):.[1]})|add|tojson  ->  put.py seg_created \'<wynik>\'  (dni przed utworzeniem segmentu = brak danych, nie zero)')
print('\n# 2. CZŁONKOSTWO  path=/v1/environments/{environment_id}/metrics/segment_membership  params={environment_id:190673,segment_id,resolution:"days",start,end}')
print('#    jq: .membership_metric|[<pola>]|tojson  gdzie pole: e=.entered l=.left t=.total, brak pola = []  (np. pola "t" -> [[],[],.total])')
print('#    ->  put.py membership/<seg> \'{"start":"<data startu>","v":<wynik>}\'   (scalanie po datach, historia zostaje)')
for sg, (need, fl) in NEED.items():
    m = raw.get('membership', {}).get(str(sg))
    st = str(D0 - dt.timedelta(7))
    if m:
        ok = all(m.get(k) for k in fl) and m['start'] <= need and all(x is not None for k in fl for x in m[k][(dt.date.fromisoformat(need) - dt.date.fromisoformat(m['start'])).days:])
        last = dt.date.fromisoformat(m['start']) + dt.timedelta(len(m[fl[0]]) - 1)
        if not ok: st = need
        elif str(last - dt.timedelta(1)) < st: st = str(last - dt.timedelta(1))
    else: st = need
    jq = '[' + ','.join('.entered' if 'e' in fl else '[]' for _ in [0]) + ',' + ('.left' if 'l' in fl else '[]') + ',' + ('.total' if 't' in fl else '[]') + ']'
    print('M', sg, st, ts(dt.date.fromisoformat(st)), ts(D0 + dt.timedelta(1)), 'jq=.membership_metric|%s|tojson' % jq)
print('W 531 tygodnie: params={environment_id:190673,segment_id:531,resolution:"weeks",start:%d,end:%d} jq=.membership_metric|[.entered,.left]|tojson -> put.py membership_weeks/531 \'{"start":"2026-07-09","e":<[0]>,"l":<[1]>}\'' % (ts(dt.date(2026, 7, 9)), ts(D0 + dt.timedelta(1))))
print('\n# 3. PRÓBKA ZAMÓWIEŃ  %s/logs params={type:"event",name:"purchase",limit:50,from:"<D>T00:00:00Z",to:"<D>T23:59:59Z"} jq=refresh/sample.jq' % E)
print('#    1 strona / dzień; sprawdź że timestampy są z dnia D  ->  put.py sample/<D> \'<wynik + "day":"<D>">\'')
for i in range(14, 0, -1):
    d = str(D0 - dt.timedelta(i))
    if d not in raw.get('sample', {}) or ('dn' not in raw['sample'][d] and d not in raw.get('days_legacy', {})) or i == 1: print('S', d)
print('#    purchases_yesterday: wszystkie strony logów z %s (continuation), jq .logs|map(select(.timestamp>=%d and .timestamp<%d))|length, suma -> put.py purchases_yesterday N'
      % (D0 - dt.timedelta(1), ts(D0 - dt.timedelta(1)), ts(D0)))
# Weekend: zamówienia per dzień (doba warszawska, UTC+2) i harmonogramy dostaw z wczoraj
print('\n# 3b. WEEKEND')
for i in range(7, 0, -1):
    d = D0 - dt.timedelta(i); S = ts(d) - 7200
    if str(d) not in raw.get('orders_day', {}):
        print('O %s purchase: %s/logs params={type:"event",name:"purchase",limit:50,from:"%sT22:00:00Z",to:"%sT21:59:59Z"} wszystkie strony (continuation), '
              'jq=(.logs|map(select(.timestamp>=%d and .timestamp<=%d))) as $l|[($l|length),([$l[].attrs.value//0|tonumber]|add//0|floor),(.logs[-1].timestamp//0),.meta.continuation]|tojson'
              '  koniec gdy timestamp < %d; zsumuj n,v -> put.py orders_day/%s \'[n,v]\'' % (d, E, d - dt.timedelta(1), d, S, S + 86399, S, d))
yd = D0 - dt.timedelta(1); Y0 = ts(yd)
print(('D %s diet_delivery_schedule: %s/logs params={type:"event",name:"diet_delivery_schedule",limit:50,from:"%sT00:00:00Z",to:"%sT23:59:59Z"} wszystkie strony (continuation, koniec gdy timestamp < %d), '
       'jq=[(.logs|map(select(.timestamp>=%d and .timestamp<=%d))|map("\\(.customer_id|tostring|.[-5:])\\(.attrs.client_diet_uuid|tostring|.[-6:]):\\([(.attrs.days//[])[]|select(.>=%d)|(./86400|floor)|select(((.+4)%%7)==6 or ((.+4)%%7)==0)]|map(tostring)|join("."))")|join(",")),(.logs[-1].timestamp//0),.meta.continuation]|tojson'
       '  -> KAŻDĄ stronę po kolei (od najnowszej): put.py wk_sched/%s \'<[0]>\'') % (yd, E, yd, yd, Y0, Y0, Y0 + 86399, ts(D0), yd))
print('\n# 4. STRONY KLIENTÓW  %s/customers params={filters:<b64>,limit:50,page:p}' % E)
B, M0, T30 = int(dt.datetime.now().timestamp()), ts(D0), ts(D0) - 30 * 86400
JA = ('def d(x): ((x-%d)/86400|floor); [.customers[]|.attributes|((.active_diets//"[]"|fromjson? // []|map(.start_date|tonumber)|min)//0) as $s|'
      '{g:(((.rfm_total_score|tonumber?)//0)|if .>=14 then 0 elif .>=11 then 1 elif .>=8 then 2 elif .>=5 then 3 elif .>=3 then 4 else 5 end),w:($s>%d),'
      'o:((.lifetime_orders|tonumber?)//0),s:d($s),n:[d((.first_order_at|tonumber?)//0),d(if $s>0 then $s else %d end),((.total_days_count|tonumber?)//0)]}] as $a|'
      '{w:([$a[]|select(.w)|.g]|group_by(.)|map([.[0],length])),wd:[$a[]|select(.w)|[.g,.s]],n:[$a[]|select(.o==1)|.n]}|tojson') % (M0, B, M0)
JS = ('[.customers[]|.attributes|select(((.first_order_at|tonumber?)//0)>=%d)|((.last_order_at|tonumber?)//0) as $lo|'
      '(.active_diets//"[]"|fromjson? // [])|any(.[];(.start_date|tonumber)<$lo and $lo<=((.end_date|tonumber)+86400))]|[length,(map(select(.))|length)]|tojson') % T30
for key, seg, jq in (('active_pages', {"segment": {"id": 649}}, JA), ('sec_pages', {"and": [{"segment": {"id": 643}}, {"segment": {"id": 820}}]}, JS)):
    f = base64.b64encode(json.dumps(seg, separators=(',', ':')).encode()).decode()
    print('P %s seg=%s filters=%s  strony 1..ceil(total/50) (total = pierwsza strona .meta.pagination.total)  ->  put.py %s/<p> \'<wynik>\'' % (key, json.dumps(seg), f, key))
    print('  jq:', jq)
print('P wait_days seg=649 te same strony co active_pages, jq: [.customers[]|.attributes|((.active_diets//"[]"|fromjson? // []|map(.start_date|tonumber)|min)//0) as $s|select($s>%d)|[(((.rfm_total_score|tonumber?)//0)|if .>=14 then 0 elif .>=11 then 1 elif .>=8 then 2 elif .>=5 then 3 elif .>=3 then 4 else 5 end),(($s-%d)/86400|floor)]]|tojson  ->  put.py wait_days \'{"<p>":<wynik>}\'' % (B, M0))
print('\n# 5. KAMPANIE (FLOWS)')
st = dt.date.fromisoformat(raw['flows']['start']); nd = (D0 - st).days + 1
for cid, m in raw['flows']['meta'].items():
    if m['m']:
        for per, steps, k in (('days', min(nd, 8), 'd'), ('weeks', 12, 'w'), ('months', 13, 'm')):
            print('K %s/campaigns/%s/metrics params={period:"%s",steps:%d} jq=.campaign_metrics.email as $e|[["sent","delivered","human_opened","human_clicked","unsubscribed","converted"][]|($e[.]//[])[-%d:]]|tojson  ->  put.py flows/metrics/%s/%s %s'
                  % (E, cid, per, steps, steps, cid, k, ('\'{"end":"%s","v":<wynik>}\'' % D0) if k == 'd' else "'<wynik>'"))
gd = sorted(raw['flows']['goals']); last = dt.date.fromisoformat(gd[-1]) if gd else st
d = min(last, D0 - dt.timedelta(3))
while d < D0:
    print('G %s goals 2,7,10,11: %s/goals/<g>/goal_refresh params={start:%d,end:%d} jq={p:.refresh_in_progress,g:[.goal_refresh[]|select(.campaign_id!=null)|[.campaign_id,.goal_count,.revenue]]}|tojson'
          % (d, E, ts(d), ts(d) + 86399))
    print('   p=true -> ponów. Zsumuj 4 cele per campaign_id ->  put.py flows/goals/%s \'{"<cid>":[liczba,przychód],...}\'' % d)
    d += dt.timedelta(1)
print('\n# 6. PUSH / KAMPANIE 800+')
print('X %s/metrics/all_deliveries params={version:2,res:"months"} filtr type=="push", pełne miesiące -> put.py push_monthly \'{"lab":[..],"s":[..],"d":[..],"o":[..],"cv":[..]}\'' % E)
print('X %s/campaigns/157/channel_metrics, /158/channel_metrics params={period:"days"} suma od 2026-09-28 -> put.py camp \'{"157":{"email":[d,o,cl,cv]},"158":{"push":[d,o,null,cv]}}\'' % E)
print('\n# 6b. GRYZY  path=/v1/environments/190673/logs params={type:"event",name:"gadget_earned",limit:100,from:"<D-30>T00:00:00Z",to:"<D-1>T23:59:59Z"} (+continuation)')
print('#    jq [.logs[]|[(.timestamp|strftime("%Y-%m-%d")),(.attrs.spent/100|floor),(.attrs.gadget|split(", ")),(.attrs.points_value|floor)]]')
print('#    sklej fragmenty nazw rozbite przecinkiem ("w zapinanej na suwak walizce", "duoball i piłka") -> DOPISZ do raw["gryzy_ex"]["rows"] tylko dni nowsze niż obecne "to" (starszych NIE usuwaj — budują historię do porównań 30 dni), zaktualizuj "to"; "from" zostaje najstarszą datą')
print('\n# 7. python3 refresh/build.py')

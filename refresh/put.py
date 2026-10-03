#!/usr/bin/env python3
"""Zapis do raw.json bez ręcznej edycji pliku.
  python3 put.py PATH 'JSON'      PATH rozdzielany '/', np. counts | membership/528 | sample/2026-10-02 | active_pages/3
Słownik + słownik = scalenie, w innym wypadku nadpisanie. Wartość może być stringiem z MCP (JSON w JSON) — zostanie rozpakowana."""
import json, sys, os
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw.json')
raw = json.load(open(F))
path, val = sys.argv[1].split('/'), json.loads(sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read())
while isinstance(val, str):
    try: val = json.loads(val)
    except ValueError: break
if isinstance(val, dict) and set(val) == {'data'}: val = json.loads(val['data']) if isinstance(val['data'], str) else val['data']
if path[0] == 'membership':  # scalanie po datach: {"start":"YYYY-MM-DD","v":[entered,left,total]} (pusta lista = brak)
    import datetime as dt
    m = raw.setdefault('membership', {}).setdefault(path[1], {'start': val['start'], 'e': [], 'l': [], 't': []})
    st0, st1 = dt.date.fromisoformat(m['start']), dt.date.fromisoformat(val['start'])
    if st1 < st0:
        pad = (st0 - st1).days
        for k in 'elt': m[k] = [None] * pad + m[k] if m[k] else m[k]
        m['start'] = val['start']; st0 = st1
    off = (st1 - st0).days
    for k, arr in zip('elt', val['v']):
        if not arr: continue
        cur = m[k] or []
        n = max(len(cur), off + len(arr)); cur = cur + [None] * (n - len(cur))
        cur[off:off + len(arr)] = arr; m[k] = cur
    json.dump(raw, open(F, 'w'), ensure_ascii=False, separators=(',', ':'))
    print('ok membership', path[1], m['start'], len(m['t'] or m['e'])); sys.exit()
if path[:2] == ['flows', 'metrics'] and len(path) == 4 and path[3] == 'd' and isinstance(val, dict):
    # ogon metryk dziennych: {"end":"YYYY-MM-DD","v":[6 tablic]} wyrównany do daty końca; historia zostaje
    import datetime as dt
    m = raw['flows']['metrics'].setdefault(path[2], {'d': [[] for _ in range(6)], 'w': None, 'm': None})
    st = dt.date.fromisoformat(raw['flows']['start']); end = dt.date.fromisoformat(val['end'])
    for k, arr in enumerate(val['v']):
        cur = m['d'][k]; i0 = (end - st).days + 1 - len(arr)
        cur += [0] * max(0, i0 + len(arr) - len(cur)); cur[i0:i0 + len(arr)] = arr
    json.dump(raw, open(F, 'w'), ensure_ascii=False, separators=(',', ':'))
    print('ok', '/'.join(path), val['end']); sys.exit()
o = raw
for p in path[:-1]: o = o.setdefault(p, {})
k = path[-1]
if isinstance(o.get(k), dict) and isinstance(val, dict): o[k].update(val)
else: o[k] = val
json.dump(raw, open(F, 'w'), ensure_ascii=False, separators=(',', ':'))
print('ok', '/'.join(path), len(val) if hasattr(val, '__len__') else val)

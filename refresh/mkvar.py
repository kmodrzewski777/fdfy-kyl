import json,base64,sys
# python3 mkvar.py key1 key2 ... -> dopisuje warianty @email/@sms/@push/@app/@d_web do queries.json, wypisuje brakujące do vq.txt
q=json.load(open('queries.json'));Q=dict((k,v) for k,v in q);ks=set(Q);c=json.load(open('raw.json'))['counts']
V={'email':{"and":[{"segment":{"id":51}},{"not":{"segment":{"id":616}}}]},'sms':{"segment":{"id":71}},'push':{"segment":{"id":198}},'app':{"segment":{"id":157}},'d_web':{"not":{"segment":{"id":157}}}}
out=[]
for k in sys.argv[1:]:
  for v,f in V.items():
    kk=k+'@'+v;fl={"and":[Q[k],f]}
    if kk not in ks:q.append([kk,fl]);ks.add(kk)
    if kk not in c: out.append(kk+' '+base64.b64encode(json.dumps(fl,separators=(',',':')).encode()).decode())
json.dump(q,open('queries.json','w'),ensure_ascii=False)
open('/tmp/claude-0/-home-user-fdfy-kyl/f0217bd4-5a78-5add-bba6-6736e7072891/scratchpad/vq.txt','w').write('\n'.join(out));print(len(out))

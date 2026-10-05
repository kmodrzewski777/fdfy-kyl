import json,time
p='../dashboard/foodify-retencja.html';s=open(p).read();snap=json.load(open('snapshot.json'))
m='try{applyData({"';i=s.index(m)+len(m)-2;_,n=json.JSONDecoder().raw_decode(s,i)
s=s[:i]+json.dumps(snap,ensure_ascii=False,separators=(',',':'))+s[n:]
import re;s=re.sub(r'window\.__EMB_UPD=\d+',f'window.__EMB_UPD={int(time.time()*1000)}',s,1)
open(p,'w').write(s);print('embedded',len(s))

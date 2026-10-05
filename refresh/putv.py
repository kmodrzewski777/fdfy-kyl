import json,subprocess,sys
# python3 putv.py START v1 v2 ... -> zapisuje wartości dla linii vq.txt od START (1-indexed)
L=[l.split()[0] for l in open('/tmp/claude-0/-home-user-fdfy-kyl/f0217bd4-5a78-5add-bba6-6736e7072891/scratchpad/vq.txt')]
s=int(sys.argv[1])-1;v=[int(x) for x in sys.argv[2:]]
subprocess.run(['python3','put.py','counts',json.dumps(dict(zip(L[s:s+len(v)],v)))])

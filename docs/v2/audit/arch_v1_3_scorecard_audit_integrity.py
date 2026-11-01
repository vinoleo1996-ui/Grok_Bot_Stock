import json,hashlib,os,datetime as dt
def sha(p):
    h=hashlib.sha256();f=open(p,'rb')
    for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
m=json.load(open('output/strategy_optimizer/core_x2/v1_3_RUN_MANIFEST.json'))
okt=dt.datetime(2026,10,18,0,46,19).timestamp()
bad=0;early=[]
for sec in ['outputs','inputs','code','gates']:
  for p,v in m[sec].items():
    if not os.path.exists(p): print('MISSING',sec,p);bad+=1;continue
    s=sha(p)
    if s!=v['sha256']: print('MISMATCH',sec,p);bad+=1
    if sec=='outputs' and os.path.getmtime(p)<okt: early.append(p)
print('mismatch/missing',bad,'early_outputs',early)
for p,v in m['code'].items(): print('code',p,dt.datetime.fromtimestamp(os.path.getmtime(p)))
# baseline
n=0;b=0
for line in open('docs/v2/audit/CORE_WEIGHTS_SHA256_20261018.txt'):
  t=line.split()
  if len(t)<2 or len(t[0])!=64: continue
  n+=1;p=t[-1].lstrip('*')
  if not os.path.exists(p): print('BL missing',p);b+=1
  elif sha(p)!=t[0]: print('BL changed',p);b+=1
print('baseline',n,'bad',b)

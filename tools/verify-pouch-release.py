"""Compare every changed public file with normal and cache-busted production bytes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request,urlopen
import hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
files=subprocess.check_output(['git','diff-tree','--no-commit-id','--name-only','-r',sha],cwd=ROOT,text=True).splitlines()
files=[p for p in files if (p.endswith('.html') or p.startswith('assets/') or p in ['sitemap.xml','robots.txt','llms.txt']) and (ROOT/p).is_file()]
def verify(path):
 route='/' + path.removesuffix('index.html') if path.endswith('index.html') else '/'+path
 expected=hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
 results=[]
 for suffix in ['', '?release='+sha[:12]]:
  url='https://www.packhubglobe.com'+route+suffix
  error=''
  for attempt in range(3):
   try:
    with urlopen(Request(url,headers={'User-Agent':'PackHubGlobe release verification','Cache-Control':'no-cache'}),timeout=45) as response:
     actual=hashlib.sha256(response.read()).hexdigest();status=response.status
    if status==200 and actual==expected: error='';break
    error='HTTP '+str(status)+' byte mismatch'
   except Exception as exc:error=str(exc)
   if attempt<2:time.sleep(2)
  results.append(dict(url=url,match=not error,error=error))
 return dict(path=path,checks=results)
checks=[]
with ThreadPoolExecutor(max_workers=16) as pool:
 jobs=[pool.submit(verify,path) for path in files]
 for i,job in enumerate(as_completed(jobs),1):
  checks.append(job.result())
  if i%200==0:print('Verified',i,'/',len(files),flush=True)
failed=[r for r in checks if not all(c['match'] for c in r['checks'])]
report=dict(commit=sha,files=len(files),checks=2*len(files),matched=sum(c['match'] for r in checks for c in r['checks']),failed=failed)
(ROOT/'qa/pouch-release.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='failed'},indent=2));print('Failures:',len(failed),flush=True)
raise SystemExit(bool(failed))

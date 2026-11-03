"""복사용 입력의 Bash 구문만 검사한다. 입력을 실행하지 않는다."""
from pathlib import Path
import json, subprocess

ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'examples/rev02/input-index.json').read_text('utf8'))
bash=Path('C:/Program Files/Git/bin/bash.exe')
errors=[];checked=[]
for r in rows:
    if not r['id'].startswith('C') or 'PowerShell' in r['where']:continue
    p=subprocess.run([str(bash),'--noprofile','--norc','-n'],input=r['text']+'\n',text=True,encoding='utf8',capture_output=True)
    checked.append(r['id'])
    if p.returncode:errors.append({'id':r['id'],'stderr':p.stderr})
report={'checked':len(checked),'errors':errors,'scope':'Bash parse only; no commands executed','ids':checked}
(ROOT/'editorial/REV02/bash-syntax.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({k:v for k,v in report.items() if k!='ids'},ensure_ascii=False))
raise SystemExit(bool(errors))

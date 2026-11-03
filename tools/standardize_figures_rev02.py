"""REV02 도식 값과 화면의 표시 범위를 통일한다. 실제 화면 픽셀은 변경하지 않는다."""
from pathlib import Path
import json, shutil, hashlib
from diagrams_rev02 import Figure
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets/illustrations/rev02';ASSETS.mkdir(exist_ok=True)
GENERATED=Path('C:/Users/Student/.codex/generated_images/01a1a06d-6f6f-74a2-bced-1ac61dec819b')
selected={
 'assets/illustrations/diversity/v1-c07-file.png':('exec-8e38a7a0-c510-4eee-8c64-68051c5ee8c9.png','webshell.png'),
 'assets/illustrations/diversity/v1-c09-fim.png':('exec-03029c94-697e-4bfd-a12f-86bad2254c31.png','fim.png'),
 'assets/illustrations/diversity/v1-c10-process.png':('exec-9d3132e0-3103-4c4b-9586-ef445d6a8225.png','ports.png'),
}
for source,name in selected.values():shutil.copy2(GENERATED/source,ASSETS/name)
# 개념 도식은 원본 생성 방식으로 REV02 자산에 다시 작성한다.
f=Figure(1120)
f.text((30,10,1470,100),'Windows PC · VMware Workstation',54)
f.box((35,115,1465,245),'Windows 브라우저\n웹 HTTP :80 · Wazuh HTTPS :5601',0,42)
f.box((35,340,710,825),'kt66 VM\nUbuntu 22.04\n192.168.0.107\n웹 서비스 · Wazuh · 호스트 센서',1,42)
f.box((790,340,1465,825),'공격자 VM\nUbuntu 22.04 Live Server\n192.168.0.108\n공격 도구',2,42)
f.text((35,255,1465,330),'공격 요청: 192.168.0.108 → 192.168.0.107',42)
f.arrow((370,835),(370,945));f.arrow((1120,835),(1120,945))
f.box((35,955,1465,1085),'Bridged · 실습망 192.168.0.0/24 · DHCP 주소 예약',0,42)
f.save('environment')
f=Figure(500)
f.box((35,30,1465,155),'https://192.168.0.107:5601/',0,64)
f.text((35,170,1465,270),'HTTPS: 통신 방식    192.168.0.107: VM 주소    5601: 포트',43)
f.box((35,320,670,460),'HTTP · 80 → kt66 웹',1,52)
f.box((775,320,1465,460),'HTTPS · 5601 → Wazuh',2,49);f.save('ports')
f=Figure(400)
f.box((35,35,510,200),'dvwa.ccc.com\n이름',0,48);f.box((990,35,1465,200),'192.168.0.107\n접속할 주소',1,48)
f.arrow((525,115),(975,115));f.text((530,20,970,100),'Windows hosts',43)
f.box((35,260,1465,365),'HTTP Host: dvwa.ccc.com → Apache가 DVWA 사이트 선택',2,43);f.save('name-and-host')

crops={
 'assets/screens/chapter05/browser/normal-headers.png':[0,0,900,274],
 'assets/screens/chapter05/browser/sqli-headers.png':[0,0,900,306],
 'assets/screens/chapter06/brute-success-headers.png':[0,0,900,306],
 'assets/screens/chapter06/login-failed-headers.png':[0,0,900,242],
 'assets/screens/chapter06/login-success-headers.png':[0,0,900,242],
 'assets/screens/chapter06/method-headers.png':[0,0,900,242],
 'assets/screens/chapter06/scan-data.png':[0,0,1060,171],
 'assets/screens/chapter07/shell-rules.png':[0,0,405,181],
 'assets/screens/chapter07/ok-status.png':[205,0,375,116],
}
record=[]
for src in sorted((ROOT/'manuscript/REV02').glob('*.json')):
 d=json.loads(src.read_text('utf8'));port_scene=None
 for pg in d['pages']:
  for b in pg['blocks'][:]:
   path=b.get('path','')
   if path in selected:
    b['path']='assets/illustrations/rev02/'+selected[path][1]
    if path.endswith('v1-c07-file.png'):
     b['caption']='삽화. 서버 담당은 파일 생성 경보를 확인한 뒤 같은 파일에 웹 요청을 보낸다. 파일 존재와 요청 기록까지 확인됐지만, PHP 실행 여부는 응답과 실행 위치를 더 조사해야 한다.'
    if path.endswith('v1-c09-fim.png'):
     b['caption']='삽화 9-1. 파일을 바꿔도 경보가 없자 시스템 담당이 감시 설정을 조회한다. 수집 대상 경로를 확인한 뒤에야 규칙의 탐지 여부를 시험할 수 있다.'
    if path.endswith('v1-c10-process.png'):
     b['caption']='삽화. 한 사람은 실습용 리스너를 종료하고 다른 사람은 포트 목록을 다시 조회한다. 포트가 닫힌 뒤에도 과거 경보는 남으므로 보고서에 발생 시각과 조회 시각을 구분해 적는다.'
     port_scene=b;pg['blocks'].remove(b)
   if path.endswith('v1-c10-sensor.png'):
    pg['blocks'].remove(b);record.append({'action':'remove redundant illustration','path':path})
   if path in crops:
    b['crop_px']=crops[path];record.append({'action':'Word crop; original pixel values unchanged','path':path,'rectangle':crops[path]})
    if path.endswith('ok-status.png'):
     b['width_mm']=54;b['caption']='화면 7-12. 의심 URL 요청의 HTTP 200 응답'
   if path in ['assets/figures/chapter01/environment.png','assets/figures/chapter01/ports.png','assets/figures/chapter05/name-and-host.png']:
    b['path']='assets/figures/rev02/'+Path(path).name
   if path=='assets/screens/chapter07/log4-raw.png':
    pg['blocks'].remove(b);record.append({'action':'omit raw screenshot with historical payload destination; preserve source in editorial','path':path})
   if path=='assets/screens/chapter07/shell-raw.png':
    idx=pg['blocks'].index(b)
    pg['blocks'][idx]={'type':'code','text':'"GET /cgi-bin/test.cgi HTTP/1.1" 200 10436\n"-" "() { :; }; /bin/bash -c \\"id\\""\n\n"GET /cgi-bin/status HTTP/1.1" 403 438\n"() { :; }; /bin/bash -c \\"cat /etc/passwd\\""\n"curl/7.81.0"'}
    record.append({'action':'transcribe request/status/header portions; no address substitution','path':path})
   if b['type']=='code' and b.get('text','').startswith('192.168.0.202 - - [01/Nov/2026:21:32:00 +0900]'):
    b['text']=b['text'].split('\n',1)[1]
   if b['type']=='p':
    s=b['text']
    s=s.replace(' 원본 기록에 보이는 .202는 본문 예시의 .108과 역할이 같은 주소이다.','')
    s=s.replace('rule.id 31101은 4xx 응답을 분류한다. full_log의 요청 줄 뒤에는 403이 있고 끝부분의 User-Agent에는 조회 문자열이 남아 있다. URL의 인코딩된 값과 헤더의 평문 값을 서로 대응시킨다.','rule.id 31101은 4xx 응답을 분류한다. 요청 기록의 full_log를 열고 요청 줄 뒤의 응답 코드와 마지막 User-Agent 값을 확인한다. URL의 인코딩된 조회 문자열을 디코딩해 헤더의 평문 값과 대조한다.')
    s=s.replace('출발지는 .202이며 원문 시각은 17:20:55 +0900이다.','원문 시각은 17:20:55 +0900이다. 아래 접속 로그의 요청·응답·헤더 항목을 대조한다.')
    s=s.replace('기존 경보에서 확인한 값은 .202, 200, 31106이다.','경보의 응답 코드는 200이고 적용 규칙은 31106이다.')
    b['text']=s
 if port_scene:next(pg for pg in d['pages'] if pg['title'].startswith('10.8 '))['blocks'].append(port_scene)
 src.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
(ROOT/'editorial/REV02/figure-standardization.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
print('3 concept figures; 3 replacement illustrations; 1 redundant illustration removed; 9 Word crops')

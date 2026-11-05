"""REV01 5장 도식: 학습 순서, 입력의 도달 지점과 확인할 기록."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import diagrams_chapter01 as base
base.OUT=base.ROOT/'assets/figures/chapter05';base.OUT.mkdir(parents=True,exist_ok=True)
Figure=base.Figure

# 학습 순서: 준비 → 기준 → 공격 → 판단.
f=Figure(930)
cols=[('준비',['5.1\n요청의 경로','5.2\nDVWA 준비','5.3\n요청 읽기']),('기준',['5.4\n정상 요청']),
      ('공격',['5.5\nSQL 인젝션','5.6\nWAF 근거','5.7\nXSS','5.8\n경로 조작']),('판단',['5.9\n도달 지점 판정','5.10\n결과가 다를 때','5.11\n원상복구','5.12\ncurl(선택)'])]
W,G,X0=318,74,15
for col,(label,items) in enumerate(cols):
 x=X0+col*(W+G)
 f.label((x,15,x+W,95),label,50)
 for row,title in enumerate(items):
  y=110+row*180;f.box((x,y,x+W,y+160),title,col%3,36)
 if col<3:f.arrow((x+W+8,280),(x+W+G-8,280))
f.label((15,830,1485,915),'실행 위치: Windows 브라우저 · kt66 VM 터미널 · 공격자 VM(선택)',40)
f.save('rev01-roadmap')

# 입력이 어디까지 갔는가: 지점마다 확인할 기록.
f=Figure(940)
f.label((35,10,700,85),'입력이 도달한 지점',42);f.label((800,10,1465,85),'확인할 기록',42)
rows=[('1  브라우저가 보냈다','Network · Request URL·Payload'),
      ('2  웹 서버에 도착했다','dvwa_access.log · data.url'),
      ('3  WAF가 판정했다','modsec_audit.log · intercepted'),
      ('4  애플리케이션이 처리했다','응답 코드와 본문'),
      ('5  결과가 생겼다','DB 자료 · 스크립트 실행 · 파일 내용')]
for i,(stage,ev) in enumerate(rows):
 y=100+i*155
 f.box((35,y,700,y+120),stage,i%3,38);f.box((800,y,1465,y+120),ev,(i+1)%3,34)
 f.arrow((707,y+60),(793,y+60))
 if i<4:f.arrow((367,y+124),(367,y+150))
f.label((35,855,1465,930),'이 장의 네 공격 요청은 3에서 차단되었다',40)
f.save('rev01-reach')
print('2 chapter 5 REV01 diagrams')

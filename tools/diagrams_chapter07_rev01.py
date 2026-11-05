"""REV01 7장 도식: 학습 순서, 실행 판정의 네 단계와 Wazuh 기록."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import diagrams_chapter01 as base
base.OUT=base.ROOT/'assets/figures/chapter07';base.OUT.mkdir(parents=True,exist_ok=True)
Figure=base.Figure

# 학습 순서: 틀 → 여섯 사례 → 교차 분석 → 마무리.
f=Figure(1110)
cols=[('틀',['7.1\n실행 판정\n네 단계']),('사례',['7.2\n웹셸','7.3\nLog4Shell','7.4\nShellshock','7.5\n명령 삽입','7.6\n200·500 응답']),
      ('사례·분석',['7.7\n반복 오류','7.8\n교차 분석']),('마무리',['7.9\n원본·정의','7.10\n원상복구','7.11\ncurl(선택)'])]
W,G,X0=318,74,15
for col,(label,items) in enumerate(cols):
 x=X0+col*(W+G)
 f.label((x,15,x+W,95),label,46)
 for row,title in enumerate(items):
  y=110+row*180;f.box((x,y,x+W,y+160),title,col%3,34)
 if col<3:f.arrow((x+W+8,190),(x+W+G-8,190))
f.label((15,1020,1485,1100),'결과 화면은 강의 자료(2026-10-31)의 기록 · 입력은 직접 보내 비교한다',38)
f.save('rev01-roadmap')

# 실행 판정의 네 단계와 각 단계의 기록.
f=Figure(830)
f.label((35,10,700,80),'판정 단계',42);f.label((800,10,1465,80),'Wazuh·서버에서 찾을 기록',42)
rows=[('1  입력 흔적\n요청에 공격 문자열','접속 로그 URL·헤더 · WAF 감사\n(31101·31103·31166 등)'),
      ('2  처리 흔적\n서버가 응답했다','data.id · 응답 본문\n(31106·31168: 2xx·3xx 조건)'),
      ('3  서버 변화\n파일·명령·검사','FIM 554·550·553 · cmdlog 100260\n· ClamAV 52502'),
      ('4  실행 결과\n출력·조회·반환','응답의 명령 출력 · 외부 통신\n· DB·파일 내용')]
for i,(stage,ev) in enumerate(rows):
 y=95+i*170
 f.box((35,y,700,y+140),stage,i%3,36);f.box((800,y,1465,y+140),ev,(i+1)%3,32)
 f.arrow((707,y+70),(793,y+70))
 if i<3:f.arrow((367,y+144),(367,y+166))
f.label((35,760,1465,822),'실행 판정에는 3·4단계 기록이 필요하다',38)
f.save('rev01-ladder')
print('2 chapter 7 REV01 diagrams')

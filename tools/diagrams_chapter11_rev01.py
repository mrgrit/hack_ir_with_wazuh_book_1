"""REV01 11장 도식: 학습 순서, 세 사례의 경계, 기록에서 결론까지의 층."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import diagrams_chapter01 as base
base.OUT=base.ROOT/'assets/figures/chapter11';base.OUT.mkdir(parents=True,exist_ok=True)
Figure=base.Figure

# 학습 순서.
f=Figure(580)
cols=[('두 기록',['11.1\n공격 일지와\n조사 기록']),('증거',['11.2\n시각과\n식별값','11.3\n사본과 해시']),
      ('재구성',['11.4\n세 사례\n시간표','11.5\n대응 판단']),('정리',['11.6\n탐지 공백','11.7\n보고서'])]
W,G,X0=318,74,15
for col,(label,items) in enumerate(cols):
 x=X0+col*(W+G)
 f.label((x,15,x+W,95),label,46)
 for row,title in enumerate(items):
  y=110+row*180;f.box((x,y,x+W,y+160),title,col%3,34)
 if col<3:f.arrow((x+W+8,190),(x+W+G-8,190))
f.label((15,485,1485,565),'기록이 말하는 범위까지만 쓰고, 모르는 것은 모른다고 쓴다',38)
f.save('rev01-roadmap')

# 세 사례의 경계.
f=Figure(770)
for x0,x1,t in [(15,330,'사례'),(350,800,'때 · 대상'),(820,1485,'답할 질문')]:f.label((x0,5,x1,70),t,36)
rows=[('A\nSSH 인증','11-02 20:25~21:00\nbastion(컨테이너)','실패 뒤 성공한 연결은\n어느 것인가'),
      ('B\n공개 키','11-03 07:45~08:05\nbastion(컨테이너)','등록한 키로\n실제 로그인했는가'),
      ('C\n포트·키 상태','11-03 08:35~09:30\nkt66-host(VM)','무엇이 언제부터\n언제까지 있었나')]
for i,(a,b,c) in enumerate(rows):
 y=85+i*200
 f.box((15,y,330,y+170),a,i,34);f.box((350,y,800,y+170),b,i,30);f.box((820,y,1485,y+170),c,i,30)
f.label((15,690,1485,755),'같은 주소·계정이 나와도 사례를 하나로 합치지 않는다',32)
f.save('rev01-cases')

# 기록에서 결론까지의 층.
f=Figure(840)
steps=[('관찰 사실','경보·원문에 그대로 있는 것\n예: 07:50:25 Accepted publickey for ccc',0),
       ('근거 있는 판단','둘 이상의 기록이 같은 결론을 가리킬 때\n예: 지문이 diff로 더해진 키와 같다',1),
       ('미확인','기록 범위 밖 · 수집 공백\n예: 접속 뒤 파일을 읽었는가',2),
       ('다음 행동','미확인을 줄일 수집·확인\n예: 그 세션의 명령 기록과 통신 기록',0)]
for i,(a,b,c) in enumerate(steps):
 y=20+i*205
 f.box((15,y,400,y+160),a,c,38);f.box((430,y,1485,y+160),b,c,30)
 if i<3:f.arrow((207,y+166),(207,y+198))
f.save('rev01-levels')
print('3 chapter 11 REV01 diagrams')

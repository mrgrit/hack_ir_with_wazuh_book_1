"""REV01 9장 도식: 학습 순서, 변경을 보는 기록, 기록의 변경 타임라인."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import diagrams_chapter01 as base
base.OUT=base.ROOT/'assets/figures/chapter09';base.OUT.mkdir(parents=True,exist_ok=True)
Figure=base.Figure

# 학습 순서.
f=Figure(940)
cols=[('준비',['9.1\n감시 범위\n확인']),('남겨 둔 것',['9.2\nsudo 규칙\n파일','9.3\nSSH\n공개 키','9.4\n예약 작업']),
      ('실행·변경',['9.5\n외부 연결','9.6\n내려받아\n실행','9.7\n실행 파일','9.8\n로그 삭제']),('분석·마무리',['9.9\n교차 분석','9.10\n정의 확인','9.11\n원상복구'])]
W,G,X0=318,74,15
for col,(label,items) in enumerate(cols):
 x=X0+col*(W+G)
 f.label((x,15,x+W,95),label,46)
 for row,title in enumerate(items):
  y=110+row*180;f.box((x,y,x+W,y+160),title,col%3,34)
 if col<3:f.arrow((x+W+8,190),(x+W+G-8,190))
f.label((15,840,1485,920),'변경을 만들며 일지에 적고, 기록 세 가지로 다시 묶는다',38)
f.save('rev01-roadmap')

# 변경을 보는 기록: 어디서 무엇을 보는가.
f=Figure(820)
for x0,x1,t in [(15,330,'바뀐 것'),(370,900,'Wazuh 기록'),(940,1485,'답하는 질문')]:f.label((x0,5,x1,70),t,36)
rows=[('파일\nsudoers.d·키·cron','FIM(syscheck)\n554 추가 · 550 변경 · 553 삭제','무엇이 언제 바뀌었나\n(diff: 무엇이 더해졌나)'),
      ('로그인','auth.log\n5715 · sudo 5402','누가 그때 들어와\n어떤 명령을 요청했나'),
      ('호스트 명령','auditd(audit_command)\n80792 · auid · 인자','어떤 프로그램을\n어떤 인자로 실행했나')]
for i,(a,b,c) in enumerate(rows):
 y=85+i*210
 f.box((15,y,330,y+180),a,0,32);f.box((370,y,900,y+180),b,1,30);f.box((940,y,1485,y+180),c,2,30)
 f.arrow((338,y+90),(362,y+90));f.arrow((908,y+90),(932,y+90))
f.label((15,730,1485,800),'한 기록으로 답하지 못하는 질문은 시각으로 다른 기록에 넘긴다',34)
f.save('rev01-sources')

# 기록의 변경 타임라인(세로).
rows=[('07:49:34~43','sudoers.d 실습 파일\n추가·수정·삭제','',''),
      ('07:50:21','authorized_keys\n키 한 줄 추가(550)','',''),
      ('07:50:25','키 제거(550)\n07:50:25.985','공개 키 로그인\n원문 07:50:25',''),
      ('07:51:42','cron.d 실습 파일\n추가(554)','',''),
      ('07:52:26','','','nc 실행\n인자 주소·4444'),
      ('07:52:27','cron.d 삭제(553)','',''),
      ('07:53:20','web /usr/bin/yes\n7바이트 추가(550)','','curl → sh\nid · hostname'),
      ('07:53:25','yes 복구(550)','',''),
      ('07:53:26~36','로그 사본 추가·\n비우기·삭제','','')]
H,GAP,Y0=104,10,95
f=Figure(Y0+len(rows)*(H+GAP)+80)
cols=[(15,265),(280,680),(695,1075),(1090,1485)]
for (x0,x1),t in zip(cols,['시각(KST)','FIM(bastion·web)','인증(bastion)','명령(kt66-host)']):f.label((x0,10,x1,80),t,34)
for i,row in enumerate(rows):
 y=Y0+i*(H+GAP)
 f.label((cols[0][0],y,cols[0][1],y+H),row[0],30)
 for j,t in enumerate(row[1:],start=1):
  if t:f.box((cols[j][0],y,cols[j][1],y+H),t,j-1,29)
f.label((15,Y0+len(rows)*(H+GAP)+5,1485,Y0+len(rows)*(H+GAP)+70),'2026-11-03 기록 · 시각은 경보 timestamp(인증은 원문 시각 병기)',30)
f.save('rev01-timeline')
print('3 chapter 9 REV01 diagrams')

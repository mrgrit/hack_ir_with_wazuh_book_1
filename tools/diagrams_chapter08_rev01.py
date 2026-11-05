"""REV01 8장 도식: 학습 순서, SSH·로그 경로, 기록 타임라인, 세션 묶기, 권한 지도."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import diagrams_chapter01 as base
base.OUT=base.ROOT/'assets/figures/chapter08';base.OUT.mkdir(parents=True,exist_ok=True)
Figure=base.Figure

# 학습 순서.
f=Figure(940)
cols=[('준비',['8.1\n경로와\n기준 상태']),('공격·관찰',['8.2\n암호 대입','8.3\n자동 차단','8.4\n없는 계정','8.5\n실패 뒤 성공']),
      ('권한',['8.6\nroot 로그인','8.7\nsudo·docker','8.8\n계정 변경']),('분석·마무리',['8.9\n경보만으로\n재구성','8.10\n원본·정의','8.11\n원상복구'])]
W,G,X0=318,74,15
for col,(label,items) in enumerate(cols):
 x=X0+col*(W+G)
 f.label((x,15,x+W,95),label,46)
 for row,title in enumerate(items):
  y=110+row*180;f.box((x,y,x+W,y+160),title,col%3,34)
 if col<3:f.arrow((x+W+8,190),(x+W+G-8,190))
f.label((15,840,1485,920),'공격 일지에 적으며 만들고, 일지를 덮고 경보만으로 다시 답한다',38)
f.save('rev01-roadmap')

# SSH 접속 경로와 로그·대응 경로.
f=Figure(700)
top=[('공격자 VM\n192.168.0.202',0),('kt66 VM\n포트 2204',1),('bastion sshd\n10.20.30.201:22',2)]
for i,(t,c) in enumerate(top):
 x=15+i*520;f.box((x,40,x+430,200),t,c,38)
 if i<2:f.arrow((x+438,120),(x+512,120))
f.label((520,205,1000,255),'Docker가 전달 · 출발지 유지',30)
f.arrow((1270,208),(1270,300))
bottom=[('/var/log/\nauth.log',2),('Wazuh\n에이전트',1),('Manager\n디코더·규칙',0),('Discover\n검색',1)]
xs=[1130,780,430,40]
for (t,c),x in zip(bottom,xs):f.box((x,305,x+330,465),t,c,36)
for a,b in zip(xs[:-1],xs[1:]):f.arrow((a-8,385),(b+338,385))
f.box((430,520,1460,660),'5712·5763이 붙으면 bastion에서 firewall-drop\n출발지 주소를 180초 차단(iptables DROP)',2,32)
f.arrow((595,470),(595,512))
f.save('rev01-path')

# 기록의 타임라인(세로). 열: 시각 · 실패·차단 · 성공 · 권한·계정
rows=[('20:28:13','','ccc 로그인\n포트 51380',''),
      ('20:29:35\n~20:30:23','ccc 실패 · 한 연결씩\n연결당 6회에서 끊김','',''),
      ('20:31:33\n~20:31:37','ccc 실패 · 네 연결\n5763(수준 10)','',''),
      ('20:31:37\n~20:34:38','출발지 차단 180초\nfirewall-drop','',''),
      ('20:36:11\n~20:36:15','없는 계정 3개\n5710 8건','',''),
      ('20:37:03\n~20:37:13','ccc 실패 3회\n같은 연결','ccc 로그인\n포트 42688',''),
      ('20:38:05','','root 로그인\n포트 46726','root 암호 변경\n5555'),
      ('20:38:07','root 실패\n복구 뒤 확인','',''),
      ('20:38:35','','ccc 로그인','sudo -i id\nshadow 읽기'),
      ('20:38:37\n~20:38:39','','ccc 로그인 4회','계정 생성·sudo\n그룹 추가·삭제')]
H,GAP,Y0=104,10,95
f=Figure(Y0+len(rows)*(H+GAP)+80)
cols=[(15,265),(280,680),(695,1075),(1090,1485)]
for (x0,x1),t in zip(cols,['시각(KST)','실패·차단','로그인 성공','권한·계정']):f.label((x0,10,x1,80),t,36)
for i,row in enumerate(rows):
 y=Y0+i*(H+GAP)
 f.label((cols[0][0],y,cols[0][1],y+H),row[0],30)
 for j,t in enumerate(row[1:],start=1):
  if t:f.box((cols[j][0],y,cols[j][1],y+H),t,j-1,30)
f.label((15,Y0+len(rows)*(H+GAP)+5,1485,Y0+len(rows)*(H+GAP)+70),'출발지는 모두 192.168.0.108(공격자 VM)',32)
f.save('rev01-timeline')

# 세션 묶기: 어떤 필드로 같은 연결·세션을 잇는가.
f=Figure(760)
f.label((15,5,1485,70),'sshd[2537] 한 연결의 기록 (20:37:03~13)',36)
items=[('5503 PAM 실패\nrhost=…108',2),('5760 Failed\n포트 42688',0),('5760 반복 요약\n포트·출발지 없음',0),('5715 Accepted\n포트 42688',1),('5501·5502\n세션 열림·닫힘',1)]
for i,(t,c) in enumerate(items):
 x=15+i*296;f.box((x,90,x+276,250),t,c,30)
f.box((15,280,1457,360),'sshd[2537] 프로세스 번호: 여섯 건 모두',2,32)
f.box((311,385,1161,465),'출발지 포트 42688: 두 건',0,32)
f.label((15,500,1485,560),'다른 세션의 sudo 줄에는 sshd 번호가 없다',34)
f.box((15,580,520,730),'sshd[2651]\n20:38:35.459 열림',1,30)
f.box((540,580,960,730),'sudo 2건\nsrcuser ccc',2,30)
f.box((980,580,1485,730),'sshd[2651]\n20:38:35.544 닫힘',1,30)
f.arrow((523,655),(535,655));f.arrow((963,655),(975,655))
f.save('rev01-session')

# 권한 지도: 로그인한 계정으로 할 수 있었던 일.
f=Figure(900)
for x0,x1,t in [(15,290,'출발지'),(330,700,'계정'),(740,1100,'권한'),(1140,1485,'할 수 있는 일')]:f.label((x0,5,x1,60),t,36)
f.box((15,75,290,575),'192.168.0.202\n공격자 VM',0,32)
f.box((330,75,700,395),'ccc\n암호 인증',1,34)
f.box((330,455,700,575),'root 직접 로그인\n(임시 허용 때)',1,28)
f.box((740,75,1100,215),'sudo\nNOPASSWD: ALL',2,32)
f.box((740,255,1100,395),'docker 그룹\nDocker 소켓',2,32)
f.box((1140,75,1485,215),'root로\n모든 명령',0,32)
f.box((1140,255,1485,395),'호스트 Docker\n컨테이너 조작',0,30)
f.box((1140,455,1485,575),'root로\n모든 명령',0,32)
f.arrow((298,235),(322,235));f.arrow((298,515),(322,515))
f.arrow((708,145),(732,145));f.arrow((708,325),(732,325))
f.arrow((1108,145),(1132,145));f.arrow((1108,325),(1132,325));f.arrow((708,515),(1132,515))
f.box((330,640,700,780),'book08-user\n암호 잠김(L)',1,32)
f.box((740,640,1100,780),'sudo 그룹\n(ALL : ALL) ALL',2,30)
f.box((1140,640,1485,780),'자기 암호 필요\n지금은 못 씀',0,30)
f.arrow((708,710),(732,710));f.arrow((1108,710),(1132,710))
f.label((15,800,1485,880),'로그인한 계정의 권한이 그 출발지가 할 수 있었던 일이다',36)
f.save('rev01-reach')
print('5 chapter 8 REV01 diagrams')

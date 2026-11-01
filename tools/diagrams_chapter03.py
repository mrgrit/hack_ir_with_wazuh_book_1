"""3장: 검색 조건과 경보 필드의 관계."""
import diagrams_chapter01 as drawing
drawing.OUT=drawing.ROOT/'assets/figures/chapter03';drawing.OUT.mkdir(parents=True,exist_ok=True)
Figure=drawing.Figure
f=Figure(660)
for i,(a,b) in enumerate([('검색 대상','wazuh-alerts-*'),('시간 범위','최근 24시간'),('검색 조건','agent.name: "kt66-host"')]):
 y=30+i*210;f.box((35,y,490,y+155),a,i,53);f.arrow((510,y+77),(605,y+77));f.box((630,y,1465,y+155),b,i,48)
f.save('search-scope')
f=Figure(530)
f.box((35,35,655,235),'접속 출발지\n10.20.30.254',0,52)
f.box((845,35,1465,235),'SSH 서버 · bastion\n10.20.30.201',1,48)
f.arrow((665,135),(835,135))
f.label((35,270,655,400),'data.srcip\n서버가 기록한 출발지',47)
f.label((845,270,1465,400),'agent.ip\n수집 에이전트의 주소',47)
f.label((35,425,1465,510),'같은 경보에 접속 출발지와 수집 장비의 주소가 함께 들어간다.',43)
f.save('address-fields')
print('2 chapter 3 diagrams')

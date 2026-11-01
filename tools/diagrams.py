from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parents[1]
# Vector pixel-office diagrams: crisp blocks, consistent palette, live text labels.
def draw(name,title,labels,notes,accent='#287f78'):
 s=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 330"><rect width="900" height="330" fill="#f4ebdd"/><text x="28" y="38" font-family="Noto Sans CJK KR,sans-serif" font-size="23" fill="#263449">{escape(title)}</text>'
 for i,(label,note) in enumerate(zip(labels,notes)):
  x=35+i*292
  s+=f'<g shape-rendering="crispEdges"><rect x="{x+12}" y="82" width="180" height="118" fill="#263449"/><rect x="{x+22}" y="92" width="160" height="96" fill="#fffdf8"/><rect x="{x+87}" y="200" width="32" height="16" fill="#263449"/><rect x="{x+64}" y="216" width="78" height="10" fill="#263449"/><rect x="{x}" y="230" width="210" height="12" fill="#b96c24"/><rect x="{x+12}" y="242" width="12" height="30" fill="#263449"/><rect x="{x+186}" y="242" width="12" height="30" fill="#263449"/>'
  for j,w in enumerate([100,70,115]):s+=f'<rect x="{x+38}" y="{111+j*22}" width="{w}" height="8" fill="{accent}"/>'
  s+='</g>'
  s+=f'<text x="{x+103}" y="74" text-anchor="middle" font-family="Noto Sans CJK KR,sans-serif" font-size="23" font-weight="bold" fill="#263449">{escape(label)}</text><text x="{x+103}" y="305" text-anchor="middle" font-family="Noto Sans CJK KR,sans-serif" font-size="20" fill="#263449">{escape(note)}</text>'
  if i<2:s+=f'<path d="M{x+225} 150h45m-14-14 14 14-14 14" fill="none" stroke="{accent}" stroke-width="7"/>'
 s+='</svg>';(ROOT/f'assets/diagrams/{name}.svg').write_text(s)
draw('overview','직접 실행하고, 기록을 찾고, 근거를 읽는다',['학습자','실습 서버','Wazuh'],['명령 한 개 실행','요청·상태 변화 기록','클릭·검색·문서 펼치기'])
draw('sqli','요청의 흐름과 관찰 지점',['공격 문자열','WAF','웹 애플리케이션'],['입력값을 변형','차단 또는 통과','처리 결과는 별도 확인'],'#b54445')
draw('ssh','같은 출발지·계정의 시간 순서를 읽는다',['인증 실패','인증 실패','인증 성공'],['첫 번째 시도','두 번째 시도','이후 행위 조사'],'#426b9b')
draw('osquery','상태 비교에서 검색 화면까지',['상태 변화','osqueryd','Wazuh'],['포트·인증 키 추가','예약 쿼리·차이 기록','added 행을 찾아 읽기'])

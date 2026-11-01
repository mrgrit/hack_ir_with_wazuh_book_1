"""Compose generated concept art with typeset labels. Never draw lab screenshots."""
from pathlib import Path
from html import escape
from base64 import b64encode
ROOT=Path(__file__).resolve().parents[1]
def draw(name,title,labels,notes,accent='#287f78'):
    s=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 900 430"><title>{escape(title)}</title><desc>옛 PC 게임풍 개념 삽화. 공격자는 뒷모습, 방어자는 앞모습입니다. 실제 실행 화면이나 네트워크 배치도가 아닙니다.</desc><rect width="900" height="430" fill="#fffdf8"/><text x="14" y="30" font-family="Noto Sans CJK KR,sans-serif" font-size="24" font-weight="bold" fill="#263449">{escape(title)}</text>'
    art=b64encode((ROOT/f'assets/illustrations/{name}.png').read_bytes()).decode('ascii')
    s+=f'<image x="0" y="46" width="900" height="300" xlink:href="data:image/png;base64,{art}"/>'
    for i,(label,note) in enumerate(zip(labels,notes)):
        x=150+i*300
        s+=f'<rect x="{x-128}" y="358" width="256" height="3" fill="{accent}"/><text x="{x}" y="388" text-anchor="middle" font-family="Noto Sans CJK KR,sans-serif" font-size="24" font-weight="bold" fill="#263449">{escape(label)}</text><text x="{x}" y="418" text-anchor="middle" font-family="Noto Sans CJK KR,sans-serif" font-size="22" fill="#263449">{escape(note)}</text>'
        if i<2:s+=f'<path d="M{x+139} 382h22m-7-7 7 7-7 7" fill="none" stroke="{accent}" stroke-width="3"/>'
    (ROOT/f'assets/diagrams/{name}.svg').write_text(s+'</svg>')
draw('overview','직접 실행하고, 기록을 찾고, 근거를 읽는다',['공격 실습','대상 시스템','방어·분석'],['명령 한 개 실행','요청·상태 변화 기록','Wazuh에서 근거 확인'])
draw('sqli','공격 요청에서 기록 분석까지',['공격 요청','WAF·웹 서버','Wazuh 분석'],['변형한 입력값 전송','검사·처리 결과 기록','요청과 기록 연결'],'#b54445')
draw('ssh','같은 출발지·계정의 시간 순서를 읽는다',['인증 시도','SSH 대상 서버','방어·분석'],['같은 출발지·계정','실패 2회 후 성공 1회','정상 접속 여부 확인'],'#426b9b')
draw('osquery','호스트의 변화가 분석 화면에 나타나기까지',['호스트 변경 실습','osqueryd 예약 조회','Wazuh 분석'],['포트·인증 키 추가','이전 결과와 비교','추가된 항목 확인'])

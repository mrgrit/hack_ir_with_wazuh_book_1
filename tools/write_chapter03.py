"""3장: Discover에서 검색하고 경보의 원문을 확인한다."""
import json
from pathlib import Path
from write_chapter01 import p,h,tab,img,code
ROOT=Path(__file__).resolve().parents[1]
pages=[];queries=[]
def page(title,*blocks):pages.append({'title':title,'kind':'body','blocks':list(blocks)})
def q(text,why,result):
 b={'type':'query','id':f'Q03-{len(queries)+1:02d}','text':text,'why':why,'result':result,'where':'Windows · Discover 검색창'};queries.append(b);return b
def screen(name,caption,width=127):return img(f'assets/screens/chapter03/{name}.png',caption,width)
page('3장  Wazuh 기본 운용',
 h('3.1  경보 검색 준비'),
 p('이 장에서는 kt66-host의 경보를 검색하고, 한 건을 열어 발생 시각·탐지 규칙·원문을 읽는다. 2장의 SSH 실패 사례로 검색 조건을 좁히는 방법도 확인한다.'),
 tab(['항목','준비·확인'],[['실행 위치','Windows PC의 웹 브라우저'],['선행 조건','kt66 기동, Wazuh 로그인, kt66-host 연결'],['사용 도구','kt66이 구성한 Wazuh Dashboard의 Discover'],['완료 기준','경보 한 건의 시각·agent.name·rule.id·full_log를 기록한다.'],['검색 오류','3.8의 순서로 검색 범위와 수집 상태를 확인한다.'],['마무리','검색창·필터를 비우고 기간을 Last 24 hours로 되돌린다.']],[30,97]),
 p('Discover는 저장된 기록을 검색하고 항목별로 읽는 화면이다. 검색 대상, 시간 범위, 검색 조건을 정하면 세 조건을 모두 만족하는 기록이 나온다. [1]'),
 img('assets/figures/chapter03/search-scope.png','도식 3-1. 경보 검색 범위.'))
page('3.2  Discover 열기',
 p('1. Wazuh 화면 왼쪽 위의 가로줄 세 개 버튼을 누른다.'),
 p('2. Explore를 펼치고 Discover를 누른다.'),
 screen('menu','화면 3-1. Discover 메뉴.',90),
 p('Discover가 열리면 왼쪽에 필드 목록, 위쪽에 기간과 검색창, 아래쪽에 검색 결과가 보인다. 결과 한 행은 경보 한 건이다.'))
page('3.3  검색 대상 선택',
 p('인덱스는 검색할 기록을 저장하는 단위이다. 인덱스 패턴은 이름이 일치하는 인덱스를 묶어 선택한다. wazuh-alerts-*의 *는 뒤에 붙는 여러 이름을 포함한다.'),
 p('1. 왼쪽 위의 인덱스 패턴 목록을 연다.'),
 p('2. wazuh-alerts-*를 선택한다. 이 장에서는 탐지 결과가 저장된 경보 인덱스를 조회한다.'),
 screen('index-pattern','화면 3-2. 경보 인덱스 패턴.',110),
 p('예를 들어 wazuh-alerts-4.x-2026.11.01은 이 패턴에 포함된다. 날짜가 다른 경보 인덱스도 같은 패턴으로 검색한다.'),
 p('목록에 wazuh-alerts-*가 없으면 Wazuh 로그인 계정과 1.9의 서비스·센서 상태를 확인한다.'))
page('3.4  최근 24시간 선택',
 p('시간 범위는 경보의 timestamp를 기준으로 정한다. Last 24 hours는 조회 시점에서 거슬러 올라간 24시간이다. 오래된 사례를 찾을 때는 시작·종료 시각을 직접 지정한다.'),
 p('1. 화면 위쪽의 달력 옆 아래쪽 화살표를 누른다.'),
 p('2. Commonly used에서 Last 24 hours를 누른다.'),
 screen('time-range','화면 3-3. 상대 시간 범위.',108),
 p('선택 후 검색 결과가 갱신된다. Refresh는 같은 검색 조건으로 다시 조회하는 버튼이다. 시간이 지나면 눌러 새 경보를 확인한다.'))
page('3.5  에이전트 이름으로 검색',
 p('검색창 오른쪽의 언어 표시가 DQL인지 확인한다. DQL은 필드와 값을 지정해 기록을 거르는 검색식이다. SQL의 SELECT 문과는 구문이 다르다. [2]'),
 q('agent.name: "kt66-host"',
 '기본 구문은 필드명: 값이다. 콜론(:) 뒤에 찾을 값을 적고, 큰따옴표로 값을 감싼다. agent.name은 경보를 보낸 에이전트의 이름이다. 입력 후 Enter를 누른다.',
 '결과에 kt66-host의 경보가 나온다. hits는 검색된 기록의 건수이다.'),
 screen('query','화면 3-4. 에이전트 이름 검색.'),
 h('결과가 없을 때'),
 p('검색창을 비우고 Enter를 누른다. 기록이 나오면 agent.name 값을 확인해 검색식을 고친다. 여전히 결과가 없으면 기간을 Last 7 days로 넓힌 뒤 3.8을 확인한다.'),
 p('검색식 복사용 파일은 examples/chapter03/Q03-01.txt에 있다. 이후 Q03 번호도 같은 폴더의 파일과 대응한다.'))
page('3.6  결과 열과 상세 기록',
 p('1. 왼쪽 Search field names에 agent.name을 입력한다. 해당 필드에 마우스를 올리고 + 버튼을 누른다.'),
 p('2. 같은 방법으로 rule.id와 rule.description을 추가한다. 필드 검색창을 비우면 선택한 필드가 Selected fields에 모인다.'),
 screen('fields','화면 3-5. 결과 표에 표시할 필드.',104),
 tab(['열','확인할 내용'],[['Time','경보 시각'],['agent.name','기록을 보낸 에이전트'],['rule.id','탐지 규칙 번호'],['rule.description','규칙 설명']],[45,82]),
 p('3. 결과 한 행의 왼쪽 화살표를 눌러 상세 기록을 펼친다. Table은 필드와 값을 표로, JSON은 같은 기록을 중괄호와 키·값으로 표시한다.'),
 p('Table에서 timestamp와 full_log를 찾는다. timestamp는 경보 시각이고, full_log는 분석한 원문이다. 원문 시각·대상·동작·결과를 읽고 규칙 설명과 대조한다.'))
page('3.7  SSH 실패 사례 좁혀 찾기',
 p('다음 화면은 2장에서 제공한 기존 kt66의 SSH 실패 기록을 조회한 것이다. 자신의 환경에서는 3.6에서 선택한 경보의 시각과 필드값을 사용한다.'),
 h('시작·종료 시각 지정'),
 p('1. 기간 표시에서 Show dates를 누른다. 날짜가 이미 보이면 시작 시각을 누른다. Absolute 탭을 선택한다.'),
 p('2. Start date에 시작 시각을 입력한다. 사례의 시작은 Nov 1, 2026 @ 14:20:00.000이다.'),
 screen('absolute-time','화면 3-6. 시작 시각 지정.',103),
 p('3. 팝업 밖을 눌러 닫고 종료 시각을 누른다. Absolute의 End date에 Nov 1, 2026 @ 14:25:00.000을 입력한다. 팝업을 닫고 Update를 누른다.'),
 p('화면의 시각은 브라우저 시간대가 한국 표준시인 경우이다. 경보 timestamp의 UTC 시각에는 9시간을 더해 대조한다.'))
page('3.7  SSH 실패 사례 · 검색 조건',
 q('agent.name: "bastion" AND rule.id: "5710"',
 'AND는 양쪽 조건을 모두 만족하는 기록을 찾는다. bastion의 경보 중 규칙 번호가 5710인 기록을 선택한다.',
 '사례의 5분 구간에서는 두 건이 나왔다. 각 행의 에이전트 이름과 규칙 번호를 확인한다.'),
 screen('results','화면 3-7. bastion의 규칙 5710 검색 결과.'),
 q('agent.name: "bastion" AND rule.id: "5710"\nAND data.srcip: "10.20.30.254"',
 'data.srcip은 원문에서 추출한 접속 출발지 IP이다. 같은 출발지의 기록만 남기도록 조건을 추가한다. 두 줄을 함께 입력한다.',
 '이 사례에서는 두 건이 모두 남는다. 원문의 출발지도 10.20.30.254인지 확인한다.'),
 p('조건을 추가할 때는 한 번에 한 항목씩 바꾸고 결과 건수를 확인한다. 결과가 사라지면 마지막에 추가한 조건부터 제거한다.'))
page('3.7  SSH 실패 사례 · 원문 대조',
 p('14:22:36.778의 행을 펼친다. Table에서 수집 에이전트와 접속 출발지를 구분한다.'),
 screen('detail','화면 3-8. 수집 에이전트와 접속 출발지.'),
 img('assets/figures/chapter03/address-fields.png','도식 3-2. SSH 사례의 두 IP 필드.'),
 p('agent.ip은 수집 에이전트의 주소이고, data.srcip은 이 SSH 기록에서 접속을 시작한 주소이다. 같은 경보 안에서도 두 값이 가리키는 장비가 다르다.'),
 h('full_log에서 확인할 내용'),
 p('계정 book03_probe, 출발지 10.20.30.254, 결과 Failed password를 찾는다. rule.id 5710의 설명과 함께 읽으면 존재하지 않는 계정으로 시도한 인증 실패임을 확인할 수 있다.'),
 p('현재 선택한 경보에 full_log가 없으면 다른 행을 열어 확인한다. 필드는 로그 종류와 분석 결과에 따라 달라진다.'))
page('3.8  검색 결과가 없을 때',
 tab(['순서','확인·조치'],[['1. 대상','인덱스 패턴이 wazuh-alerts-*인지 확인한다.'],['2. 기간','Last 24 hours에서 Last 7 days로 넓힌다. 과거 사례는 Absolute로 지정한다.'],['3. 조건','검색창을 비우고 Enter를 누른다. 검색창 아래 필터가 있으면 각 필터의 ×로 제거한다.'],['4. 이름','나온 경보의 agent.name 값을 확인해 검색식에 넣는다.'],['5. 수집','기록이 계속 없으면 1.9에서 에이전트 연결을 확인한다. 이어 원본 로그 생성과 수집 설정을 확인한다.']],[30,97]),
 p('검색 조건을 바꾼 뒤 Refresh를 눌러 결과를 다시 읽는다. 해당 기간에 저장된 경보가 있는지부터 확인한다.'),
 {'type':'image','path':'assets/illustrations/chapter03/time.png','caption':'삽화. 조사 시각 확인.','width_mm':55,'align':'right'},
 h('검색 상태 되돌리기'),
 p('검색창과 필터를 비우고 기간을 Last 24 hours로 바꾼다. 추가한 열은 왼쪽 Selected fields에서 해당 필드에 마우스를 올려 − 버튼으로 제거한다. 이 작업은 화면의 조회 조건과 표시 열을 바꾼다.'))
page('3.9  검색한 경보 기록',
 p('자신의 환경에서 확인한 경보 한 건을 다음 양식으로 정리한다. 필드가 없으면 “없음”을 적고 원문에서 확인한 값을 따로 남긴다.'),
 tab(['항목','적을 내용'],[['검색 범위','인덱스 패턴, 시작·종료 시각, 시간대'],['검색 조건','사용한 DQL과 화면 필터'],['기록 식별','상세 기록 JSON의 _index와 _id'],['발생 대상','agent.name, agent.ip'],['탐지 결과','rule.id, rule.description'],['원문','full_log, location'],['확인한 사실','원문에서 확인한 동작과 결과'],['추가 조사','같은 출발지의 후속 로그인 등 다음에 찾을 기록']],[32,95]),
 p('JSON에서 _id는 저장된 기록의 식별자이고, _index는 그 기록을 담은 인덱스 이름이다. 두 값을 함께 적으면 조사 중인 기록을 구분할 수 있다.'),
 p('양식 파일은 examples/chapter03/investigation.txt에 있다. 4장에서는 원본 로그가 수집되고 탐지 규칙에 적용되는 과정을 확인한다.'))
page('3장 참고 자료',
 h('[1] Discover 사용'),
 {'type':'link','text':'OpenSearch 2.16 · Discover','url':'https://docs.opensearch.org/2.16/dashboards/discover/index-discover/'},
 h('[2] DQL 검색 구문'),
 {'type':'link','text':'OpenSearch 2.16 · Dashboards Query Language','url':'https://docs.opensearch.org/2.16/dashboards/dql/'},
 h('실습 환경과 사례'),
 {'type':'link','text':'kt66 · 기준 커밋 63d4180','url':'https://github.com/mrgrit/kt66/tree/63d4180b1d6866de986ef263a3bd831d6082b5d5'},
 p('화면은 Wazuh 4.10.0의 기존 kt66에서 촬영했다. SSH 사례의 원본은 examples/chapter02/case-ssh.json에 있다. 조회 기간은 2026년 11월 1일 14:20~14:25(KST)이다.'))
if __name__=='__main__':
 data={'title':'Wazuh 기본 운용','series':'해킹·침해대응 실무 with Wazuh · 시스템 침투와 SIEM 분석','pages':pages}
 (ROOT/'manuscript/volume01-chapter03.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 out=ROOT/'examples/chapter03';out.mkdir(parents=True,exist_ok=True)
 for b in queries:(out/(b['id']+'.txt')).write_text(b['text']+'\n')
 (out/'manifest.json').write_text('[]\n')
 (out/'queries.json').write_text(json.dumps(queries,ensure_ascii=False,indent=2)+'\n')
 (out/'investigation.txt').write_text('검색 범위:\n시작·종료 시각과 시간대:\nDQL:\n화면 필터:\n_index:\n_id:\nagent.name:\nagent.ip:\nrule.id:\nrule.description:\nfull_log:\nlocation:\n확인한 사실:\n추가 조사:\n')
 print(len(pages),'pages',len(queries),'queries')

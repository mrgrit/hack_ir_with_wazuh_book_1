"""REV01 · 3장 Wazuh 기본 운용. 저자용이며 검색을 실행하지 않는다.

2026-11-02 개정 기준
- 조사 질문: 원하는 기록을 어떻게 찾는가. 검색 대상·기간·조건 세 가지와 0건의 의미를 중심으로 쓴다.
- 3.6은 기존 kt66 화면(2.1 사례), 3.7은 2.2에서 독자가 남긴 book02_probe 기록을 찾는다.
- DQL 문법은 OpenSearch Dashboards 2.16 문서와 대조했다.
- 한 번의 접속이 여러 5710 경보를 만드는 점, message repeated 기록에 data.srcip가 없는 점은
  2026-11-02 실제 kt66 경보(editorial/evidence/chapter08/2026-11-02/authentication-alerts.json)로 확인했다.
"""
import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript/REV01'
EX=ROOT/'examples/rev01/chapter03'
COMMIT='63d4180b1d6866de986ef263a3bd831d6082b5d5'
pages=[];queries=[]

def p(t): return {'type':'p','text':t}
def h(t): return {'type':'h','text':t}
def ul(*items): return {'type':'list','items':list(items)}
def ol(*items): return {'type':'list','style':'number','items':list(items)}
def tab(head,rows,widths=None,keep=False):
    b={'type':'table','head':head,'rows':rows,'widths':widths}
    if keep:b['keep']=True
    return b
def img(path,caption,width=127): return {'type':'image','path':path,'caption':caption,'width_mm':width}
def screen(name,caption,width=127): return img(f'assets/screens/chapter03/{name}.png',caption,width)
def box(kind,*text,items=None):
    b={'type':'box','kind':kind,'text':list(text)}
    if items:b['items']=items
    return b
def code(t): return {'type':'code','text':t}
def link(text,url): return {'type':'link','text':text,'url':url}
def q(text,purpose,syntax,result):
    b={'type':'query','id':f'Q03-{len(queries)+1:02d}','where':'Windows · Discover 검색창','purpose':purpose,'text':text,'syntax':syntax,'result':result}
    queries.append(b);return b
def page(title,*blocks,brk=True,level='page'):
    pg={'title':title,'kind':'body','blocks':list(blocks)}
    if not brk:pg['break']=False
    if level!='page':pg['level']=level
    pages.append(pg)
def section(title,*blocks):page(title,*blocks,brk=False,level='section')
FIG='assets/figures/chapter03/'

# ── 장 도입 ───────────────────────────────────────────────────
page('3장  Wazuh 기본 운용',
    p('2.2에서 남긴 로그인 실패는 Wazuh에 도착했을까? 경보 인덱스에는 kt66의 여러 서버가 보낸 기록이 계속 쌓인다. 그중 한 건을 찾으려면 어디에서, 언제, 무엇을 찾을지 세 가지를 정해야 한다. 셋 중 하나만 기록과 어긋나도 결과는 0건이다. 0건을 “기록이 없다”로 읽기 전에 세 조건부터 점검한다.'),
    h('학습 목표'),
    ul('Discover에서 검색 대상·시간 범위·검색 조건을 정해 경보를 찾고, 결과 건수가 무엇을 센 값인지 설명한다.',
       'DQL의 필드 검색, AND·OR·NOT, 괄호로 조건을 한 단계씩 더해 검색 범위를 좁힌다.',
       '경보 한 건의 상세 기록을 열어 시각·규칙·원문과 _index·_id를 조사 기록에 옮긴다.'),
    img(FIG+'rev01-roadmap.png','도식 3-1. 3장 학습 순서.',120),
    h('준비와 완료 기준'),
    tab(['항목','내용'],[
        ['실행 위치','Windows PC의 웹 브라우저 · Wazuh Dashboard의 Discover'],
        ['선행 조건','kt66 기동, Wazuh 로그인(1.6), 사건 노트에 적은 2.2의 실행 시각'],
        ['완료 기준','2.2에서 남긴 기록을 찾아 한 건의 시각·agent.name·rule.id·full_log·_index·_id를 조사 기록에 옮긴다.'],
        ['결과가 다를 때','3.8의 순서로 검색 범위와 수집 상태를 확인한다.'],
        ['원상복구','검색창과 필터를 비우고 기간을 Last 24 hours로 되돌린다(3.8).']],[32,95],keep=True))

# ── 3.1 ──────────────────────────────────────────────────────
section('3.1  검색의 세 조건',
    p('Discover는 Indexer에 저장된 기록을 검색하고 항목별로 읽는 Wazuh Dashboard의 화면이다. 검색할 때는 다음 세 조건을 정한다. 결과는 세 조건을 모두 만족하는 기록이다. [1]'),
    tab(['조건','화면 위치','정하는 것'],[
        ['검색 대상','왼쪽 위 인덱스 패턴 목록','어떤 종류의 기록을 찾을지(경보, 전체 기록)'],
        ['시간 범위','위쪽 달력 버튼','기록의 timestamp가 들어갈 기간'],
        ['검색 조건','위쪽 검색창(DQL)','필드와 값의 조건']],[26,45,56],keep=True),
    img(FIG+'search-scope.png','도식 3-2. 검색 대상·시간 범위·검색 조건.'),
    p('결과 0건은 기록이 없다는 뜻일 수도 있지만, 세 조건 중 하나가 기록과 맞지 않는다는 뜻일 수도 있다. 두 경우를 구분하는 순서는 3.8에서 정리한다.'))

# ── 3.2 ──────────────────────────────────────────────────────
section('3.2  Discover 열고 대상 고르기',
    ol('Wazuh 화면 왼쪽 위의 가로줄 세 개 버튼을 누른다.',
       '**Explore**를 펼치고 **Discover**를 누른다.'),
    screen('menu','화면 3-1. Discover 메뉴.',90),
    p('Discover가 열리면 왼쪽에 필드 목록, 위쪽에 기간과 검색창, 가운데에 검색 결과가 보인다. 결과 한 행은 저장된 기록 한 건이다.'),
    p('인덱스는 Indexer가 기록을 저장하는 단위이다. Wazuh는 경보를 날짜별 인덱스에 나누어 저장한다. 인덱스 패턴은 이름이 일치하는 여러 인덱스를 묶어 한 번에 검색하게 한다. wazuh-alerts-*의 *는 뒤에 붙는 어떤 문자열과도 일치한다. 예를 들어 wazuh-alerts-4.x-2026.11.01은 이 패턴에 포함된다.'),
    ol('왼쪽 위의 인덱스 패턴 목록을 연다.',
       '**wazuh-alerts-***를 선택한다.'),
    screen('index-pattern','화면 3-2. 인덱스 패턴 목록.',110),
    tab(['인덱스 패턴','저장하는 기록'],[
        ['wazuh-alerts-*','탐지 규칙에 일치해 경보가 된 기록. 기본 설정에서 수준 3 이상(2.3)'],
        ['wazuh-archives-*','에이전트가 보낸 모든 기록. 규칙 일치와 관계없다. kt66이 켜 둔다(2.3).'],
        ['wazuh-monitoring-* 등','에이전트 연결 상태, 매니저 통계, 취약점 상태']],[40,87]),
    p('경보를 검색할 때는 wazuh-alerts-*를, 경보가 되지 않은 원본 기록까지 찾을 때는 wazuh-archives-*를 고른다. 목록에 두 패턴이 없으면 Wazuh 로그인 계정과 1.7의 수집기·서비스 상태를 확인한다.'))

# ── 3.3 ──────────────────────────────────────────────────────
section('3.3  기간 정하기',
    p('시간 범위는 기록의 timestamp를 기준으로 고른다. Last 24 hours 같은 상대 범위는 조회하는 순간부터 거슬러 올라간 기간이고, Absolute는 시작·종료 시각을 직접 지정한 기간이다.'),
    h('상대 범위'),
    ol('화면 위쪽 달력 버튼 옆의 아래쪽 화살표를 누른다.',
       '**Commonly used**에서 **Last 24 hours**를 누른다.'),
    screen('time-range','화면 3-3. 상대 시간 범위.',100),
    p('상대 범위는 조회할 때마다 끝 시각이 현재로 바뀐다. **Refresh**는 같은 조건으로 다시 조회하는 버튼이다. 새 기록을 기다릴 때 누른다.'),
    h('시작·종료 시각 지정'),
    ol('기간 표시에서 **Show dates**를 누른다. 날짜가 이미 보이면 시작 시각을 누른다.',
       '**Absolute** 탭을 선택하고 **Start date**에 시작 시각을 입력한다.',
       '팝업 밖을 눌러 닫고 종료 시각을 누른다. **Absolute**의 **End date**에 종료 시각을 입력한다.',
       '팝업을 닫고 **Update**를 누른다.'),
    screen('absolute-time','화면 3-4. 시작 시각 지정.',100),
    box('caution','화면의 시각은 브라우저가 실행되는 Windows의 시간대로 표시된다. Windows가 한국 표준시이면 KST로 보인다. 상세 기록의 JSON에 있는 timestamp는 UTC이므로 9시간을 더해 화면 시각과 대조한다(2.4).'),
    p('특정 사건을 찾을 때는 사건 노트에 적은 시각의 앞뒤 5분 정도를 Absolute로 지정한다. 기록 시각과 처리 시각의 차이(2.4)도 이 범위에 들어간다.'))

# ── 3.4 ──────────────────────────────────────────────────────
section('3.4  DQL로 조건 적기',
    p('검색창 오른쪽의 언어 표시가 DQL인지 확인한다. DQL(Dashboards Query Language)은 필드와 값으로 기록을 거르는 검색식이다. 데이터베이스의 SQL과 달리 결과에 보일 열이나 집계를 정하지 않고, 조건에 맞는 기록만 고른다. [2]'),
    q('agent.name: "kt66-host"',
      'kt66 VM 자신의 에이전트가 보낸 경보만 고른다.',
      '기본 구문은 필드명: 값이다. 콜론(:) 앞이 필드, 뒤가 찾을 값이다. 큰따옴표로 감싼 값은 하나의 구문으로 찾는다. kt66-host는 1.7에서 확인한 kt66 VM의 수집기 이름이다. 입력 후 Enter를 누른다.',
      '결과에 kt66-host의 경보만 나온다. 결과 위의 hits는 세 조건을 만족한 기록의 건수이다.'),
    screen('query','화면 3-5. 에이전트 이름 검색.'),
    p('조건을 더할 때는 다음 연산자를 쓴다. DQL은 연산자의 대소문자를 구분하지 않는다. 이 책에서는 눈에 띄도록 대문자로 쓴다.'),
    tab(['형식','예','뜻'],[
        ['필드: 값','rule.id: "5710"','필드의 값이 일치하는 기록'],
        ['AND','A AND B','두 조건을 모두 만족'],
        ['OR','rule.id: "5710" OR rule.id: "5760"','하나 이상 만족'],
        ['NOT','NOT rule.id: "5710"','조건을 만족하지 않는 기록'],
        ['( )','A AND (B OR C)','괄호 안을 먼저 계산'],
        ['필드: *','data.srcip: *','그 필드가 있는 기록'],
        ['>=, <=, >, <','rule.level >= 10','숫자 필드의 범위']],[24,56,47],keep=True),
    p('연산자는 NOT, AND, OR 순서로 계산된다. A AND B OR C는 (A AND B) OR C로 계산되므로, AND와 OR를 함께 쓸 때는 의도한 묶음을 괄호로 적는다. [2]'),
    box('blind','필드 조건은 그 필드가 있는 기록만 고른다. 같은 사건의 기록이라도 디코더가 값을 꺼내지 못한 줄에는 그 필드가 없다. 예를 들어 rsyslog가 같은 줄의 반복을 message repeated 5 times처럼 묶어 쓴 기록에는 data.srcip가 없어서, data.srcip 조건을 붙이면 결과에서 빠진다. 조건을 더해 건수가 줄었을 때는 빠진 기록이 무엇인지 조건을 빼고 확인한다.'))

# ── 3.5 ──────────────────────────────────────────────────────
section('3.5  결과 열과 상세 기록',
    p('결과 표에는 처음에 시각과 기록 요약만 보인다. 조사에 필요한 필드를 열로 추가한다.'),
    ol('왼쪽 **Search field names**에 agent.name을 입력한다. 해당 필드에 마우스를 올리고 + 버튼을 누른다.',
       '같은 방법으로 rule.id와 rule.description을 추가한다. 필드 검색창을 비우면 추가한 필드가 **Selected fields**에 모인다.'),
    screen('fields','화면 3-6. 결과 표에 추가한 필드.',100),
    tab(['열','확인할 내용'],[
        ['Time','기록의 timestamp. 브라우저 시간대로 표시'],
        ['agent.name','기록을 보낸 에이전트'],
        ['rule.id','일치한 탐지 규칙 번호'],
        ['rule.description','규칙 설명']],[34,93]),
    ol('결과 한 행의 왼쪽 화살표를 눌러 상세 기록을 펼친다.',
       '**Table**에서 timestamp와 full_log를 찾는다. **JSON**은 같은 기록을 중괄호와 키·값으로 보여 준다.'),
    p('full_log는 분석에 쓴 원문이다. 원문의 시각·대상·동작·결과를 읽고 rule.description과 대조한다. JSON 맨 위의 _index와 _id는 이 기록이 저장된 인덱스와 그 안의 식별자이다. 조사 기록에 함께 적으면 같은 기록을 다시 찾을 수 있다(2.7).'))

# ── 3.6 ──────────────────────────────────────────────────────
section('3.6  사례 좁혀 찾기',
    p('2.1의 사례를 검색한 기존 kt66의 화면으로 조건을 좁히는 순서를 익힌다. 자신의 환경에는 이 사례가 없으므로 같은 순서를 3.7에서 직접 남긴 기록에 적용한다.'),
    p('기간은 Absolute로 Nov 1, 2026 @ 14:20:00.000부터 Nov 1, 2026 @ 14:25:00.000까지 지정했다. 조건은 한 번에 하나씩 더하고, 더할 때마다 건수를 본다.'),
    img(FIG+'rev01-narrowing.png','도식 3-3. 조건을 하나씩 더하는 검색.'),
    q('agent.name: "bastion" AND rule.id: "5710"',
      'bastion의 경보 중 없는 계정 로그인 시도(5710)만 고른다.',
      'AND는 양쪽 조건을 모두 만족하는 기록을 찾는다. 규칙 번호도 문자열로 저장되므로 큰따옴표로 감싼다.',
      '사례의 5분 구간에서는 두 건이 나왔다.'),
    screen('results','화면 3-7. bastion의 규칙 5710 검색 결과.'),
    box('predict','두 건이 나왔다. 로그인 시도가 두 번이었을까? 두 행을 펼쳐 full_log를 비교하기 전에 예측을 적는다.'),
    p('경보 건수는 시도 횟수가 아니다. sshd는 한 번의 접속에서 없는 계정으로 접속을 시작한 줄(Invalid user …), 암호 인증이 실패한 줄(Failed password for invalid user …), 연결을 끊은 줄을 따로 남긴다. 규칙 5710은 invalid user가 들어간 줄마다 일치하므로 한 번의 접속이 여러 경보가 된다. 접속은 full_log의 출발지 포트와 sshd 프로세스 번호(sshd[…])로 구분하고, 암호 시도는 Failed password 줄로 센다.'),
    q('agent.name: "bastion" AND rule.id: "5710"\nAND data.srcip: "10.20.30.254"',
      '같은 출발지의 기록만 남긴다.',
      'data.srcip는 디코더가 원문에서 꺼낸 접속 출발지이다. 앞의 검색식 뒤에 줄을 바꿔 조건을 더한다. 두 줄을 함께 입력한다.',
      '사례에서는 두 건이 모두 남았다. 건수가 줄면 빠진 기록에 data.srcip가 있는지 확인한다(3.4).'),
    screen('detail','화면 3-8. 상세 기록의 에이전트와 출발지 필드.'),
    p('agent.ip(10.20.30.201)는 기록을 보낸 bastion의 주소이고 data.srcip(10.20.30.254)는 bastion에 접속한 쪽의 주소이다. 2.2에서 확인했듯 10.20.30.254는 kt66 VM의 ext망 주소이다.'))

# ── 3.7 ──────────────────────────────────────────────────────
section('3.7  직접 남긴 기록 찾기',
    p('2.2에서 남긴 book02_probe의 로그인 실패를 찾는다. 인덱스 패턴은 wazuh-alerts-*, 기간은 사건 노트에 적은 실행 시각의 앞뒤 5분을 Absolute로 지정한다.'),
    q('data.srcuser: "book02_probe"',
      '디코더가 계정 이름을 book02_probe로 꺼낸 경보를 찾는다.',
      'data.srcuser는 없는 계정으로 시도한 경우 디코더가 원문에서 꺼낸 계정 이름이다(2.3).',
      'agent.name은 bastion, rule.id는 5710, data.srcip는 10.20.30.254인 경보가 나온다. 각 행을 펼쳐 full_log가 어느 줄인지 확인한다.'),
    q('agent.name: "bastion" AND full_log: "book02_probe"',
      '계정 이름이 원문에 들어간 기록을 필드 추출과 관계없이 찾는다.',
      'full_log는 원문 전체이다. 원문 안의 단어를 찾으므로 data.srcuser가 없는 기록도 고른다.',
      '건수를 Q03-04와 비교한다. 늘어난 행은 계정 이름이 data.srcuser로 추출되지 않은 기록이다. Ctrl+C로 끊은 연결의 기록(Connection closed by invalid user …)이 이런 경우일 수 있다.'),
    q('agent.name: "bastion" AND\ndata.srcip: "10.20.30.254" AND\n(rule.id: "5710" OR rule.id: "5760" OR rule.id: "5715")',
      '같은 출발지의 인증 실패와 성공을 함께 확인한다.',
      '괄호 안의 OR로 세 규칙 중 하나에 해당하는 기록을 고르고, 바깥의 AND로 에이전트와 출발지를 제한한다. 5760은 있는 계정의 실패, 5715는 로그인 성공이다(2.5).',
      'kt66 VM에서 다른 SSH 접속을 하지 않았다면 5710만 나오고 5715는 없다. 5715가 있으면 그 행의 시각과 계정을 사건 노트의 자신의 행동과 대조한다.'),
    box('field','결과가 없으면 인덱스 패턴을 wazuh-archives-*로 바꾸고 agent.name: "bastion"과 시간 범위만으로 검색한다. 아카이브에서 원문이 보이면 기록은 수집되었지만 경보가 되지 않은 것이고, 아카이브에도 없으면 수집 단계부터 확인한다(3.8).'),
    p('찾은 경보 한 건을 3.9의 양식으로 정리하고 사건 노트의 조사 기록에 한 줄을 더한다.'))

# ── 3.8 ──────────────────────────────────────────────────────
section('3.8  검색 결과가 없을 때',
    p('0건이면 조건을 넓히는 쪽에서 좁히는 쪽으로 다음 순서로 확인한다.'),
    tab(['순서','확인·조치'],[
        ['1. 대상','인덱스 패턴이 wazuh-alerts-*인지 확인한다.'],
        ['2. 기간','Last 24 hours를 Last 7 days로 넓힌다. 과거 사례는 Absolute 시각과 시간대를 확인한다.'],
        ['3. 조건','마지막에 더한 조건부터 뺀다. 그래도 없으면 검색창을 비우고, 검색창 아래 필터는 각 필터의 ×로 지운다.'],
        ['4. 이름','결과에 나온 agent.name의 실제 값을 확인해 검색식에 넣는다.'],
        ['5. 아카이브','wazuh-archives-*에서 에이전트와 시간만으로 원문을 찾는다. 있으면 규칙과 저장 기준을 확인한다(2.3).'],
        ['6. 수집','아카이브에도 없으면 에이전트 연결(1.7)과 원본 로그(2.2), 수집 설정(4장)을 확인한다.']],[24,103],keep=True),
    p('조건을 바꾼 뒤에는 **Refresh**를 눌러 결과를 다시 읽는다.'),
    {'type':'image','path':'assets/illustrations/chapter03/time.png','caption':'삽화. 조사 시각 확인.','width_mm':45,'align':'right'},
    h('검색 상태 원상복구'),
    p('검색창과 필터를 비우고 기간을 Last 24 hours로 바꾼다. 추가한 열은 왼쪽 **Selected fields**에서 해당 필드에 마우스를 올리고 − 버튼으로 제거한다. 인덱스 패턴을 바꿨다면 wazuh-alerts-*로 되돌린다. 이 작업은 화면의 조회 조건과 표시 열만 바꾸며 저장된 기록은 바뀌지 않는다.'))

# ── 3.9 ──────────────────────────────────────────────────────
section('3.9  검색한 경보 기록',
    p('3.7에서 찾은 경보 한 건을 다음 양식으로 정리한다. 필드가 없으면 “없음”을 적고 원문에서 확인한 값을 따로 남긴다.'),
    tab(['항목','적을 내용'],[
        ['검색 범위','인덱스 패턴, 시작·종료 시각, 시간대'],
        ['검색 조건','사용한 DQL과 화면 필터'],
        ['기록 식별','상세 기록 JSON의 _index와 _id'],
        ['발생 대상','agent.name, agent.ip'],
        ['탐지 결과','rule.id, rule.description'],
        ['원문','full_log, location'],
        ['확인한 사실','원문에서 확인한 동작과 결과'],
        ['추가 조사','같은 출발지의 다른 계정 시도, 로그인 성공 등 다음에 찾을 기록']],[30,97],keep=True),
    p('검색 범위와 조건을 함께 적으면 다른 사람이 같은 결과를 다시 얻을 수 있고, 0건이었을 때 무엇을 확인했는지도 남는다. 양식 파일은 examples/rev01/chapter03/investigation.txt에 있다. 4장에서는 원본 로그가 수집되고 탐지 규칙에 적용되는 과정을 직접 확인한다.'))

# ── 장 끝 ─────────────────────────────────────────────────────
page('3장 정리',
    h('핵심 정리'),
    ul('검색 결과는 검색 대상(인덱스 패턴), 시간 범위, 검색 조건(DQL)을 모두 만족하는 기록이다. 0건이면 세 조건부터 점검한다.',
       'wazuh-alerts-*에는 경보가 된 기록만 있다. kt66은 모든 기록을 wazuh-archives-*에도 저장하므로 경보가 없을 때 원문을 다시 찾을 수 있다.',
       '조건은 하나씩 더하고 건수를 본다. 필드 조건은 그 필드가 없는 기록을 빼므로, 건수가 줄면 빠진 기록을 확인한다.',
       '경보 건수는 시도 횟수가 아니다. 한 번의 접속도 여러 줄의 원문과 여러 경보를 남긴다.'),
    h('확인 문제'),
    ol('경보 검색 결과가 0건이다. 기록이 없다고 판단하기 전에 확인할 세 가지는 무엇인가?',
       'rule.id: "5710" OR rule.id: "5715" AND data.srcip: "10.20.30.254"는 어떻게 계산되는가? 두 규칙 모두 출발지를 제한하려면 어떻게 고치는가?',
       'agent.name: "bastion" AND rule.id: "5710"은 3건, 여기에 AND data.srcip: "10.20.30.254"를 더하면 2건이다. 빠진 1건은 무엇일 수 있는가?',
       '5710 경보가 4건이다. 없는 계정으로 4번 시도했다고 쓸 수 있는가?',
       'wazuh-alerts-*에는 없고 wazuh-archives-*에는 원문이 있다. 무엇을 뜻하는가?'),
    h('확인 문제 해설'),
    ol('검색 대상(인덱스 패턴), 시간 범위, 검색 조건이다. 이어서 아카이브와 수집 상태를 확인한다(3.8).',
       'AND가 먼저 계산되어 rule.id: "5710" OR (rule.id: "5715" AND data.srcip: "10.20.30.254")가 된다. (rule.id: "5710" OR rule.id: "5715") AND data.srcip: "10.20.30.254"로 고친다.',
       'data.srcip가 추출되지 않은 기록이다. data.srcip 조건을 빼고 그 행의 full_log를 읽어 확인한다.',
       '쓸 수 없다. 한 접속이 Invalid user 줄, Failed password 줄, 연결 종료 줄을 따로 남길 수 있다. full_log의 출발지 포트와 sshd 프로세스 번호로 접속을 구분하고, 암호 시도는 Failed password 줄로 센다.',
       '기록은 수집되었지만 경보가 되지 않았다. 일치하는 규칙이 없거나 규칙 수준이 저장 기준보다 낮다(2.3).'),
    h('더 읽을거리'),
    p('OpenSearch Dashboards의 DQL 문서이다. 3.4의 연산자 외에 와일드카드, 날짜 범위, 중첩 필드 검색 예가 있다.'),
    link('OpenSearch 2.16 · Dashboards Query Language','https://docs.opensearch.org/2.16/dashboards/dql/'),
    p('Wazuh 4.10 공식 문서의 이벤트 기록 설명이다. 경보 파일과 아카이브 파일의 차이, 아카이브를 wazuh-archives-* 인덱스로 검색하는 설정을 3.2와 대조해 읽는다.'),
    link('Wazuh 4.10 · Event logging','https://documentation.wazuh.com/4.10/user-manual/manager/event-logging.html'))

section('3장 참고 자료',
    h('[1] Discover 사용'),
    link('OpenSearch 2.16 · Discover','https://docs.opensearch.org/2.16/dashboards/discover/index-discover/'),
    h('[2] DQL 검색 구문'),
    link('OpenSearch 2.16 · Dashboards Query Language','https://docs.opensearch.org/2.16/dashboards/dql/'),
    h('실습 환경과 사례'),
    link('kt66 · 기준 커밋 63d4180','https://github.com/mrgrit/kt66/tree/'+COMMIT),
    p('3.6의 화면은 Wazuh 4.10.0의 기존 kt66에서 2.1의 사례를 조회한 것이다. 조회 기간은 2026년 11월 1일 14:20~14:25(KST)이다. 사례 원본은 examples/rev01/chapter02/case-ssh.json에 있다.'))

INVESTIGATION='''검색한 경보 기록

검색 범위(인덱스 패턴·시작~종료·시간대):
검색 조건(DQL·필터):
기록 식별(_index·_id):
발생 대상(agent.name·agent.ip):
탐지 결과(rule.id·rule.description):
원문(full_log·location):
확인한 사실:
추가 조사:
'''
README='''3장 REV01 검색식

Q03-01~06 : 검색식 블록 번호와 같은 파일. Windows 브라우저의 Discover 검색창에 입력한다.
queries.json : 검색식 목록과 설명
investigation.txt : 검색한 경보 기록 양식

여러 줄 검색식은 줄바꿈을 포함해 그대로 붙여 넣는다.
'''

if __name__=='__main__':
    data={'title':'Wazuh 기본 운용','series':'해킹·침해대응 실무 with Wazuh · 시스템 침투와 SIEM 분석','baseline':COMMIT,'revision':'REV01',
          'comments':'REV01 원고. DQL은 OpenSearch Dashboards 2.16 문서와 대조. 3.6 화면은 기존 kt66에서 촬영. 3.7 직접 검색은 새 VM에서 실행 검증 전.','pages':pages}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'volume01-chapter03.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    EX.mkdir(parents=True,exist_ok=True)
    for old in EX.glob('Q03-*.txt'):old.unlink()
    for b in queries:(EX/(b['id']+'.txt')).write_text(b['text']+'\n')
    (EX/'queries.json').write_text(json.dumps(queries,ensure_ascii=False,indent=2)+'\n')
    (EX/'investigation.txt').write_text(INVESTIGATION)
    (EX/'README.txt').write_text(README)
    print(len(pages),'pages',len(queries),'queries')

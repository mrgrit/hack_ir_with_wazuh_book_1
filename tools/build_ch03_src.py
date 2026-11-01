#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1권 3장 'Wazuh 기본 운용' 원고(JSON) 생성기. 저자용, kt66 미접속.
문체: 문어체 평서형(한다체). 실제 컨테이너 이름·경로·필드로 서술한다.
근거: kt66 커밋 63d4180 의 docker-compose.yaml·deployment, Wazuh 4.10 표준 경로."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "manuscript" / "volume01-chapter03.json"
WHERE_H = "kt66 호스트 터미널 · ~/work/kt66"

def P(t): return {"type": "p", "text": t}
def H(t): return {"type": "h", "text": t}
def NOTE(t): return {"type": "note", "text": t}
def TAB(head, rows, widths=None):
    b = {"type": "table", "head": head, "rows": rows}
    if widths: b["widths"] = widths
    return b
def CMD(cid, text, why, result, where=WHERE_H):
    return {"type": "cmd", "id": cid, "where": where, "text": text, "why": why, "result": result}
def CODE(label, text): return {"type": "code", "label": label, "text": text}
def SHOT(sid, title, memo, height=48): return {"type": "shot", "id": sid, "title": title, "text": memo, "height_mm": height}
def IMG(path, caption, width=127): return {"type": "image", "path": path, "caption": caption, "width_mm": width}
def SRC(text, url): return {"type": "source", "text": text, "url": url}
def FLOW(title, nodes): return {"type": "flow", "title": title, "nodes": nodes}
def page(title, subtitle, blocks): return {"kind": "body", "title": title, "subtitle": subtitle, "blocks": blocks}

pages = []

# ============================== 3장 도입 ==============================
pages.append(page("3장  Wazuh 기본 운용", "3.1  네 구성요소와 실행 위치", [
    P("1장에서 kt66을 설치하고 Wazuh 로그인까지 확인했다. 2장에서 로그·이벤트·경보와 Decoder·Rule을 개념으로 "
      "정리했다. 이 장에서는 그 개념이 kt66에서 실제로 어디에 있는지 확인한다. 구성요소가 각각 어느 위치에서 "
      "동작하는지, 설정과 로그 파일이 어디에 있는지, 그리고 Dashboard의 Discover와 Dev Tools로 기록을 조회하는 "
      "방법을 다룬다. 규칙을 직접 작성·시험하는 작업은 4장에서 이어서 다룬다."),
    P("2장에서 Wazuh는 Agent, Manager, Indexer, Dashboard의 네 구성요소로 이루어진다고 했다. kt66에서는 이 중 "
      "Agent가 호스트(Ubuntu 가상머신)에 설치되고, 나머지 셋은 각각 컨테이너로 동작한다. 실행 위치가 다르므로 "
      "확인하는 명령과 경로도 다르다."),
    IMG("assets/figures/ch03/components.png",
        "그림 3-1. 네 구성요소와 실행 위치. Agent는 호스트에, Manager·Indexer·Dashboard는 컨테이너에서 동작한다.", 127),
    CMD("01", "docker compose -f docker-compose.yaml ps",
        "실행 중인 컨테이너와 상태를 출력한다. 1장에서 사용한 명령으로, Wazuh 컨테이너가 모두 동작하는지 먼저 확인한다.",
        "wazuh-indexer·siem·wazuh-dashboard 가 Up 상태로 보인다. 아래 명령은 이들이 동작하는 상태에서 실행한다."),
    NOTE("컨테이너 이름과 서비스 이름은 다르다. Compose 파일에서 서비스 이름은 siem·wazuh-indexer·wazuh-dashboard 이고, "
         "실제 컨테이너 이름은 kt66-siem·kt66-wazuh-indexer·kt66-wazuh-dashboard 이다. docker exec 에는 컨테이너 이름을 쓴다."),
]))

# ============================== 3.2 디렉터리 ==============================
pages.append(page("호스트와 컨테이너의 디렉터리", "3.2  두 위치를 구분한다", [
    P("Wazuh 파일은 두 위치에 나뉘어 있다. 호스트의 저장소(~/work/kt66)에는 설치·기동에 쓰는 스크립트와 Compose "
      "파일, 인덱서·대시보드 설정이 있다. 반면 Manager의 설정과 로그, 규칙은 kt66-siem 컨테이너 내부의 /var/ossec "
      "아래에 있다. 이 둘은 서로 다른 위치이므로, 호스트에서 바로 보이지 않는 파일은 컨테이너 안으로 들어가 확인한다."),
    IMG("assets/figures/ch03/dirs.png",
        "그림 3-2. 호스트의 저장소 파일과 컨테이너 내부 /var/ossec 은 다른 위치다. docker exec 로 컨테이너 안을 조회한다.", 127),
    P("docker exec 는 실행 중인 컨테이너 안에서 명령을 실행한다. 형식은 docker exec ⟨컨테이너 이름⟩ ⟨명령⟩ 이다. "
      "아래에서는 kt66-siem 컨테이너 안의 파일 목록을 조회한다."),
    CMD("02", "docker exec kt66-siem ls /var/ossec/etc",
        "kt66-siem 컨테이너 안의 /var/ossec/etc 디렉터리 내용을 출력한다. Manager의 설정이 있는 위치이다.",
        "ossec.conf, rules, decoders 등이 보인다. 이 파일들은 호스트의 저장소가 아니라 컨테이너 안에 있다."),
    CMD("03", "docker exec kt66-siem /var/ossec/bin/wazuh-control status",
        "Manager 내부의 각 데몬(프로세스) 상태를 출력한다. wazuh-control 은 Wazuh 서비스를 제어·조회하는 명령이다.",
        "wazuh-analysisd·wazuh-remoted 등 여러 데몬이 is running 으로 보인다. 일부만 떠 있으면 로그를 확인한다."),
    NOTE("이 장에서는 설정 파일을 읽기만 하고 수정하지 않는다. 규칙·디코더를 편집하고 wazuh-logtest 로 시험하는 작업은 "
         "4장에서 다룬다. 지금 수정하면 이후 실습의 기준이 흔들린다."),
]))

# ============================== 3.3 설정·로그 ==============================
pages.append(page("주요 설정과 로그 파일", "3.3  무엇이 어디에 기록되는가", [
    TAB(["경로", "내용"], [
        ["etc/ossec.conf", "Manager의 주 설정. 수집 대상·모듈·연동을 정의"],
        ["etc/rules/local_rules.xml", "직접 추가하는 로컬 규칙(4장에서 작성)"],
        ["logs/ossec.log", "Manager 자체의 동작·오류 로그"],
        ["logs/alerts/alerts.json", "생성된 경보가 JSON 한 줄씩 쌓이는 파일"],
        ["bin/wazuh-control", "서비스 상태 조회·재시작 명령"],
    ], [3.1, 5.5]),
    P("설정 파일은 길다. 전체를 한 번에 출력하기보다 필요한 부분만 확인한다. head 는 파일의 앞부분만, tail 은 "
      "끝부분만 출력하는 명령이다. -n 뒤의 숫자가 줄 수이다."),
    CMD("04", "docker exec kt66-siem head -n 20 /var/ossec/etc/ossec.conf",
        "ossec.conf 의 앞 20줄을 출력한다. 설정이 XML 형식으로 되어 있음을 확인한다.",
        "<ossec_config> 로 시작하는 XML 설정의 앞부분이 보인다."),
    CMD("05", "docker exec kt66-siem tail -n 5 /var/ossec/logs/ossec.log",
        "Manager 동작 로그의 마지막 5줄을 출력한다. 기동·오류 메시지가 여기에 남는다.",
        "시각과 함께 INFO·WARNING 등의 로그 줄이 보인다. ERROR 가 반복되면 그 메시지를 조사한다."),
    CMD("06", "docker exec kt66-siem tail -n 2 /var/ossec/logs/alerts/alerts.json",
        "최근 경보 2건을 JSON 형태로 출력한다. 경보 한 건이 하나의 JSON 객체로 저장된다.",
        "rule·agent·timestamp 등을 담은 JSON 이 보인다. 아직 공격을 만들지 않았다면 경보가 적거나 없을 수 있다."),
    NOTE("1장에서 공격을 생성하지 않았으므로 alerts.json 은 비어 있거나 설치 과정의 기록만 담을 수 있다. 경보가 없다는 "
         "것이 오류는 아니다. 5장에서 공격을 재현하면 이 파일과 Discover에 기록이 쌓인다."),
]))

# ============================== 3.4 서비스 상태 ==============================
pages.append(page("서비스 상태 확인", "3.4  어느 층이 멈췄는지 가른다", [
    P("문제가 생기면 네 구성요소 중 어디가 멈췄는지부터 가른다. 호스트의 Agent는 systemctl 로, 컨테이너의 세 "
      "구성요소는 docker compose 와 wazuh-control 로 확인한다."),
    CMD("07", "systemctl is-active wazuh-agent",
        "호스트에 설치된 Wazuh Agent 서비스의 실행 여부를 확인한다. 1장에서도 사용했다.",
        "active 이면 호스트 센서가 동작 중이다."),
    CMD("08", "docker compose -f docker-compose.yaml logs --tail 20 siem",
        "Manager(siem) 컨테이너의 최근 로그 20줄을 출력한다. 컨테이너가 반복 재시작하거나 응답이 없을 때 확인한다.",
        "기동 메시지가 보이고 오류 반복이 없으면 정상이다."),
    TAB(["확인 대상", "명령과 정상 신호"], [
        ["Agent (호스트)", "systemctl is-active wazuh-agent → active"],
        ["컨테이너 상태", "docker compose ps → Up"],
        ["Manager 데몬", "wazuh-control status → is running"],
        ["Dashboard 접속", "브라우저 https://⟨IP⟩:5601 로그인"],
    ], [2.4, 6.2]),
    P("한 층이 멈추면 그 위층의 결과가 비어 보인다. Agent가 멈추면 수집이, Manager가 멈추면 경보 생성이, Indexer가 "
      "멈추면 검색이, Dashboard가 멈추면 화면이 동작하지 않는다. 증상이 나타난 층이 아니라, 그 아래층부터 확인한다."),
]))

# ============================== 3.5 Discover ==============================
pages.append(page("Discover와 시간 범위", "3.5  기록을 화면에서 조회한다", [
    P("Dashboard에서 기록을 조회하는 기본 화면이 Discover 이다. 브라우저로 Wazuh에 로그인한 뒤 왼쪽 메뉴에서 "
      "Discover 를 연다. 메뉴 위치는 버전에 따라 다를 수 있다. Discover 는 저장된 이벤트와 경보를 시간순으로 "
      "보여 주고, 검색과 필드 선택을 지원한다."),
    IMG("assets/figures/ch03/discover.png",
        "그림 3-3. Discover 화면의 구성. ① 검색창 ② 시간 범위 ③ 필드 목록 ④ 문서 표 ⑤ 문서 펼치기.", 127),
    P("Discover 는 색인 패턴을 기준으로 데이터를 읽는다. Wazuh의 경보는 보통 wazuh-alerts-* 패턴, 시간 필드는 "
      "timestamp 이다. 화면 왼쪽 위에서 현재 패턴이 wazuh-alerts-* 인지 확인한다."),
    P("가장 흔한 실수는 시간 범위이다. 오른쪽 위의 시간 범위가 좁으면(예: Last 15 minutes) 방금 전 기록만 보이고 "
      "그 전 기록은 보이지 않는다. 기록이 없어 보이면 먼저 시간 범위를 Last 24 hours 나 Last 7 days 로 넓힌다. "
      "데이터가 없는 것과, 범위 밖이라 보이지 않는 것을 혼동하지 않는다."),
    SHOT("01", "Discover 열기와 시간 범위", "왼쪽 메뉴에서 Discover 선택, 색인 패턴 wazuh-alerts-*, 오른쪽 시간 범위 설정 화면. 두 장으로 분할.", 50),
]))

# ============================== 3.6 DQL ==============================
pages.append(page("DQL과 필드", "3.6  검색어로 범위를 좁힌다", [
    P("Discover의 검색창에는 DQL(Dashboards Query Language)을 입력한다. DQL은 필드와 값으로 조건을 적는 간단한 "
      "검색 언어이다. 기본 형식은 필드:값 이며, 비교와 결합을 함께 쓴다. 필드 이름은 왼쪽 필드 목록에서 확인한다."),
    TAB(["DQL 예", "의미"], [
        ["rule.level >= 7", "규칙 수준이 7 이상인 경보"],
        ["agent.name: \"kt66-host\"", "호스트 에이전트가 수집한 기록"],
        ["data.srcip: \"203.0.113.10\"", "특정 출발지 IP"],
        ["rule.level >= 7 and data.srcip: \"203.0.113.10\"", "두 조건을 모두 만족"],
        ["rule.description: *admin*", "설명에 admin 이 포함된 경보"],
    ], [4.6, 4.0]),
    P("문자열 값은 큰따옴표로 감싼다. and·or 로 조건을 결합하고, 별표(*)는 임의의 문자를 대신하는 와일드카드이다. "
      "조건을 입력한 뒤 Enter 를 누르면 문서 표가 갱신된다. 필드 목록에서 필드 이름을 클릭하면 표의 열로 추가할 수 "
      "있다."),
    TAB(["자주 쓰는 필드", "내용"], [
        ["timestamp", "발생 시각(시간 범위의 기준)"],
        ["agent.name", "수집한 대상 이름(예: kt66-host)"],
        ["rule.level · rule.id", "규칙 수준과 번호"],
        ["rule.description", "규칙이 붙인 설명"],
        ["data.srcip · data.url", "해석으로 뽑은 출발지·경로 등"],
    ], [2.8, 5.8]),
    SHOT("02", "DQL 검색과 열 추가", "검색창에 DQL 입력 후 문서 표가 좁혀진 화면과, 필드를 열로 추가한 화면. 글자가 읽히도록 확대.", 50),
]))

# ============================== 3.7 Dev Tools ==============================
pages.append(page("Dev Tools의 JSON", "3.7  같은 질의를 JSON으로", [
    P("Discover의 DQL은 내부적으로 Indexer에 보내는 JSON 질의로 바뀐다. Dashboard의 Dev Tools 콘솔에서는 이 JSON "
      "질의를 직접 작성해 실행할 수 있다. 메뉴에서 Dev Tools 를 열면 왼쪽에 질의를, 오른쪽에 응답을 표시한다. DQL이 "
      "다루기 번거로운 집계나 세밀한 조건을 다룰 때 사용하며, 10장의 집계 조회에서 본격적으로 쓴다."),
    CODE("예시 · 최근 경보 조회 (왼쪽 질의 입력)",
         'GET wazuh-alerts-*/_search\n{\n  "size": 5,\n  "sort": [{ "timestamp": "desc" }]\n}'),
    P("GET 은 조회를, wazuh-alerts-* 는 대상 색인을, _search 는 검색을 뜻한다. size 는 가져올 문서 수, sort 는 정렬 "
      "기준이다. 위 질의는 가장 최근 경보 5건을 가져온다. 삼각형 실행 버튼을 누르면 오른쪽에 JSON 응답이 나온다."),
    CODE("예시 · 조건을 넣은 조회",
         'GET wazuh-alerts-*/_search\n{\n  "query": {\n    "range": { "rule.level": { "gte": 7 } }\n  }\n}'),
    P("query 안의 range 는 범위 조건으로, 위 질의는 rule.level 이 7 이상인 경보를 가져온다. 이는 Discover에서 "
      "rule.level >= 7 을 입력한 것과 같은 결과를 조회한다. DQL과 JSON은 표현만 다를 뿐 같은 데이터를 조회한다."),
    SHOT("03", "Dev Tools 콘솔", "Dev Tools에서 왼쪽 질의와 오른쪽 JSON 응답. hits 안의 _source 필드가 보이도록 확대.", 50),
]))

# ============================== 읽기 실습 ==============================
pages.append(page("읽기 실습", "3.8  경보 한 건을 펼쳐 필드 읽기", [
    P("Discover에서 기록 한 건을 펼쳐 필드를 직접 읽는다. 아직 공격을 만들지 않았다면 설치 과정에서 생성된 기록 "
      "중 하나를 사용한다. 절차는 다음과 같다."),
    TAB(["단계", "조작"], [
        ["1", "시간 범위를 Last 7 days 로 넓힌다"],
        ["2", "검색창을 비우거나 rule.level >= 3 을 입력한다"],
        ["3", "문서 표에서 한 줄의 펼치기(>)를 누른다"],
        ["4", "timestamp·agent.name·rule.description·rule.level 값을 읽는다"],
    ], [1.2, 7.4]),
    P("읽은 값을 2장의 방식대로 세 문장으로 정리한다. 확인한 사실(어느 시각에 어느 대상에서 어떤 규칙이 몇 수준으로 "
      "기록되었는가), 아직 가설인 부분, 추가로 확인할 대상을 나눈다. 이 한 건이 공격인지 아닌지를 지금 단정하지 "
      "않는다. 5장부터 직접 생성한 공격 기록으로 같은 절차를 반복한다."),
    NOTE("Discover에서 읽은 필드 이름(rule.level, data.srcip 등)은 Dev Tools의 JSON 응답에서 _source 아래의 같은 "
         "이름으로 나타난다. 화면의 표와 JSON은 같은 기록을 다르게 보여 줄 뿐이다."),
]))

# ============================== 참고 ==============================
pages.append(page("3장 참고 자료", "경로와 조회에 사용한 자료", [
    P("이 장의 컨테이너 이름과 경로는 kt66 커밋 63d4180 의 docker-compose.yaml·deployment 와, Wazuh 4.10 표준 "
      "디렉터리를 대조해 서술했다. 설정 편집과 규칙 작성은 4장에서 다룬다."),
    SRC("kt66 docker-compose.yaml (컨테이너 이름·볼륨)", "https://github.com/mrgrit/kt66/blob/main/docker-compose.yaml"),
    SRC("Wazuh 문서 — 디렉터리 구조", "https://documentation.wazuh.com/current/user-manual/reference/directories.html"),
    SRC("Wazuh 문서 — wazuh-control", "https://documentation.wazuh.com/current/user-manual/reference/tools/wazuh-control.html"),
    SRC("Wazuh 문서 — Discover와 질의", "https://documentation.wazuh.com/current/user-manual/wazuh-dashboard/queries.html"),
    P("출판 전 확인: 실제 kt66에서 docker exec 결과, Discover 색인 패턴 이름, 시간 범위 동작, Dev Tools 응답의 "
      "_source 필드를 촬영하며 대조한다."),
]))

OUT_DATA = {
    "title": "시스템 침투와 SIEM 분석",
    "series": "해킹·침해대응 실무 with Wazuh",
    "chapter": 3,
    "document_label": "3장",
    "verification_note": "컨테이너 이름·경로는 kt66 커밋 63d4180 의 compose·deployment 와 Wazuh 4.10 표준 경로로 대조. "
                         "UI 화면과 실제 출력은 저자 촬영으로 검증.",
    "pages": pages,
}

if __name__ == "__main__":
    OUT.write_text(json.dumps(OUT_DATA, ensure_ascii=False, indent=2))
    print("wrote", OUT, "pages:", len(pages))

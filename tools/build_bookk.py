#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""부크크 B5 서식 기반 DOCX 조판 — 저자용. kt66/Wazuh 에 접속하지 않는다.

템플릿(tools/assets/bookk-B5-template.docx)을 base 로 열어 그 페이지 크기·여백·테마를
그대로 쓰고, 부크크 명조/고딕 글꼴·검정 본문·단순 표로 원고 JSON 을 조판한다.
섹션마다 페이지를 강제로 나누지 않고 연속으로 흐르게 한다(장·앞부속만 새 쪽)."""
import argparse, json
from pathlib import Path
from docx import Document
from docx.shared import Mm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ROW_HEIGHT_RULE, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "tools/assets/bookk-B5-template.docx"
TW = 127.0  # 본문 가로(mm)

MYUNGJO = "부크크 명조 Light"   # 본문
GOTHIK  = "부크크 고딕 Light"   # 제목·강조
MONO    = "Consolas"            # 명령/코드 (Office 기본 탑재)
BLACK = "000000"; GRAY = "595959"; BOX = "F4F4F4"; HEAD = "EDEDED"; LINE = "BFBFBF"

# ---------- 저수준 ----------
def _set_font(run, name, size=None, bold=False, color=BLACK):
    run.font.name = name
    if size is not None: run.font.size = Pt(size)
    run.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)
    rpr = run._r.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None: rf = OxmlElement('w:rFonts'); rpr.insert(0, rf)
    for k in ('ascii', 'hAnsi', 'eastAsia', 'cs'): rf.set(qn('w:' + k), name)

def _spacing(p, after=4, line=1.5, before=0):
    pf = p.paragraph_format
    pf.space_after = Pt(after); pf.space_before = Pt(before)
    pf.line_spacing = line
    pf.widow_control = True

def _borders(el_pr, which=('top','left','bottom','right'), sz=6, color=LINE, space=0):
    """el_pr: pPr(문단) 또는 tcPr(셀). 테두리 추가."""
    is_p = el_pr.tag == qn('w:pPr')
    tag = 'w:pBdr' if is_p else 'w:tcBorders'
    # 스키마상 테두리 요소보다 뒤에 와야 하는 형제들(이들 앞에 삽입)
    succ = (('w:shd','w:tabs','w:suppressAutoHyphens','w:kinsoku','w:spacing','w:ind',
             'w:jc','w:textAlignment','w:rPr') if is_p else
            ('w:shd','w:noWrap','w:tcMar','w:textDirection','w:tcFit','w:vAlign','w:hideMark'))
    bd = el_pr.find(qn(tag))
    if bd is None:
        bd = OxmlElement(tag)
        ref = None
        for t in succ:
            el = el_pr.find(qn(t))
            if el is not None: ref = el; break
        (ref.addprevious(bd) if ref is not None else el_pr.append(bd))
    for side in which:
        e = OxmlElement('w:' + side)
        e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), str(sz))
        e.set(qn('w:space'), str(space)); e.set(qn('w:color'), color)
        bd.append(e)

def _shade(pr, fill):
    for old in pr.findall(qn('w:shd')): pr.remove(old)
    sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), fill)
    ref = None
    for t in ('w:noWrap','w:tcMar','w:textDirection','w:tcFit','w:vAlign','w:hideMark',
              'w:tabs','w:spacing','w:ind','w:jc','w:textAlignment','w:rPr'):
        el = pr.find(qn(t))
        if el is not None: ref = el; break
    (ref.addprevious(sh) if ref is not None else pr.append(sh))

def _cell_margins(cell, l=1.6, r=1.6, t=0.8, b=0.8):
    tcPr = cell._tc.get_or_add_tcPr()
    for old in tcPr.findall(qn('w:tcMar')): tcPr.remove(old)
    m = OxmlElement('w:tcMar')
    for k, v in (('top', t), ('left', l), ('bottom', b), ('right', r)):
        e = OxmlElement('w:' + k); e.set(qn('w:w'), str(int(v*56.7))); e.set(qn('w:type'), 'dxa'); m.append(e)
    ref = None
    for tag in ('w:textDirection', 'w:tcFit', 'w:vAlign', 'w:hideMark'):
        el = tcPr.find(qn(tag))
        if el is not None: ref = el; break
    (ref.addprevious(m) if ref is not None else tcPr.append(m))

def _no_split(row):
    x = OxmlElement('w:cantSplit'); row._tr.get_or_add_trPr().append(x)

# ---------- 문단/표 ----------
def add_p(doc, text, font=MYUNGJO, size=10, bold=False, align='both', color=BLACK,
          after=4, line=1.5, before=0, indent=0, keep_next=False):
    p = doc.add_paragraph()
    p.alignment = {'both': WD_ALIGN_PARAGRAPH.JUSTIFY, 'left': WD_ALIGN_PARAGRAPH.LEFT,
                   'center': WD_ALIGN_PARAGRAPH.CENTER, 'right': WD_ALIGN_PARAGRAPH.RIGHT}[align]
    _spacing(p, after=after, line=line, before=before)
    if indent: p.paragraph_format.left_indent = Mm(indent)
    if keep_next: p.paragraph_format.keep_with_next = True
    if text:
        r = p.add_run(text); _set_font(r, font, size, bold, color)
    return p

def runs_p(doc, parts, align='both', after=4, line=1.5, before=0, keep_next=False):
    """parts: [(text, font, size, bold, color), ...]"""
    p = doc.add_paragraph()
    p.alignment = {'both': WD_ALIGN_PARAGRAPH.JUSTIFY, 'left': WD_ALIGN_PARAGRAPH.LEFT}[align]
    _spacing(p, after=after, line=line, before=before)
    if keep_next: p.paragraph_format.keep_with_next = True
    for (t, f, s, b, c) in parts:
        r = p.add_run(t); _set_font(r, f, s, b, c)
    return p

def box_para(doc, text, font=MONO, size=9.5, fill=BOX, color=BLACK, after=5, keep_next=False, indent=0):
    p = add_p(doc, '', font=font, size=size, align='left', after=after, line=1.3, keep_next=keep_next)
    if indent: p.paragraph_format.left_indent = Mm(indent); p.paragraph_format.right_indent = Mm(indent)
    pPr = p._p.get_or_add_pPr()
    if fill: _shade(pPr, fill)
    _borders(pPr, sz=6, color=LINE, space=4)
    r = p.add_run(text); _set_font(r, font, size, False, color)
    return p

def placeholder(doc, caption, body_lines, memo, fill, height_mm, cap_tag):
    add_p(doc, caption, font=GOTHIK, size=9.5, bold=True, align='left', color=GRAY, after=2, keep_next=True)
    t = doc.add_table(rows=1, cols=1); t.autofit = False; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.columns[0].width = Mm(TW)
    row = t.rows[0]; row.height = Mm(height_mm); row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST; _no_split(row)
    c = t.cell(0, 0); c.width = Mm(TW); c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    _shade(c._tc.get_or_add_tcPr(), fill); _borders(c._tc.get_or_add_tcPr(), color=LINE, sz=6)
    first = True
    for ln, bold in body_lines:
        p = c.paragraphs[0] if first else c.add_paragraph(); first = False
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER; _spacing(p, after=2, line=1.2)
        r = p.add_run(ln); _set_font(r, GOTHIK, 9, bold, GRAY)
    pm = c.add_paragraph(); pm.alignment = WD_ALIGN_PARAGRAPH.CENTER; _spacing(pm, after=0, line=1.15)
    rm = pm.add_run(memo); _set_font(rm, MYUNGJO, 8, False, GRAY)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def simple_table(doc, head, rows, widths=None):
    n = len(head)
    if not widths:
        widths = [TW*0.32] + [TW*0.68/(n-1)]*(n-1) if n > 1 else [TW]
    # 폭 합을 TW 로 정규화
    s = sum(widths); widths = [w*TW/s for w in widths]
    t = doc.add_table(rows=1, cols=n); t.autofit = False; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = 'Normal Table'
    for col, w in zip(t.columns, widths): col.width = Mm(w)
    # 헤더
    for i, v in enumerate(head):
        cell = t.rows[0].cells[i]; cell.width = Mm(widths[i]); cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        _shade(cell._tc.get_or_add_tcPr(), HEAD); _borders(cell._tc.get_or_add_tcPr(), color=LINE, sz=6); _cell_margins(cell)
        p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER; _spacing(p, after=0, line=1.25)
        r = p.add_run(v); _set_font(r, GOTHIK, 9.5, True, BLACK)
    hdr = OxmlElement('w:tblHeader'); t.rows[0]._tr.get_or_add_trPr().append(hdr)
    for row_vals in rows:
        rr = t.add_row(); _no_split(rr)
        for i, v in enumerate(row_vals):
            cell = rr.cells[i]; cell.width = Mm(widths[i]); cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            _borders(cell._tc.get_or_add_tcPr(), color=LINE, sz=6); _cell_margins(cell)
            p = cell.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.LEFT; _spacing(p, after=0, line=1.25)
            r = p.add_run(v); _set_font(r, MYUNGJO, 9.5, False, BLACK)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def hyperlink(doc, text, url):
    p = doc.add_paragraph(); _spacing(p, after=2, line=1.3)
    h = OxmlElement('w:hyperlink'); h.set(qn('r:id'), p.part.relate_to(url, RT.HYPERLINK, is_external=True))
    r = OxmlElement('w:r'); rpr = OxmlElement('w:rPr')
    rf = OxmlElement('w:rFonts')
    for k in ('ascii','hAnsi','eastAsia','cs'): rf.set(qn('w:'+k), MYUNGJO)
    rpr.append(rf)
    col = OxmlElement('w:color'); col.set(qn('w:val'), '0000FF'); rpr.append(col)
    u = OxmlElement('w:u'); u.set(qn('w:val'), 'single'); rpr.append(u)
    sz = OxmlElement('w:sz'); sz.set(qn('w:val'), '18'); rpr.append(sz)
    r.append(rpr); tt = OxmlElement('w:t'); tt.text = text; r.append(tt); h.append(r); p._p.append(h)

def page_break(doc):
    p = doc.add_paragraph(); r = p.add_run(); br = OxmlElement('w:br'); br.set(qn('w:type'), 'page'); r._r.append(br)

# ---------- 본문 조립 ----------
def clear_body(doc):
    body = doc.element.body
    for ch in list(body):
        if ch.tag != qn('w:sectPr'):
            body.remove(ch)

def render_blocks(doc, blocks, chapter):
    for b in blocks:
        typ = b['type']
        if typ == 'p':
            add_p(doc, b['text'])
        elif typ == 'h':
            add_p(doc, b['text'], font=GOTHIK, size=10.5, bold=True, align='left', after=3, before=6, keep_next=True)
        elif typ == 'note':
            p = add_p(doc, b['text'], font=MYUNGJO, size=9.5, align='both', after=5, line=1.4, indent=3)
            _borders(p._p.get_or_add_pPr(), which=('left',), sz=18, color=GRAY, space=6)
        elif typ == 'table':
            simple_table(doc, b['head'], b['rows'], b.get('widths'))
        elif typ == 'cmd':
            add_p(doc, f"C{chapter:02}-{b['id']}  ·  {b['where']}", font=GOTHIK, size=8.5, bold=True,
                  align='left', color=GRAY, after=1, keep_next=True)
            box_para(doc, b['text'], font=MONO, size=10, fill=BOX, keep_next=True)
            add_p(doc, b['why'], after=2)
            runs_p(doc, [("확인  ", GOTHIK, 10, True, BLACK), (b['result'], MYUNGJO, 10, False, BLACK)], after=6)
        elif typ == 'code':
            add_p(doc, b['label'], font=GOTHIK, size=8.5, bold=True, align='left', color=GRAY, after=1, keep_next=True)
            box_para(doc, b['text'], font=MONO, size=10, fill=BOX)
        elif typ == 'shot':
            placeholder(doc, f"그림 {chapter}-{b['id']}  {b['title']}",
                        [("[실제 화면 자리]", True), ("촬영 후 이 안내를 지우고 화면을 넣습니다.", False)],
                        "촬영 메모 · " + b['text'], fill="FFFFFF", height_mm=b.get('height_mm', 46), cap_tag='화면')
        elif typ == 'art':
            placeholder(doc, f"그림 {chapter}-{b['id']} · 삽화  {b['title']}",
                        [("[레트로 픽셀오피스 삽화 자리]", True), ("같은 화풍으로 생성해 넣습니다. 실제 화면과 구분합니다.", False)],
                        "연출 지시 · " + b['text'], fill="F2F4FA", height_mm=b.get('height_mm', 44), cap_tag='삽화')
        elif typ == 'image':
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; _spacing(p, after=2, line=1.0); p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(str(ROOT / b['path']), width=Mm(b.get('width_mm', TW)))
            add_p(doc, b['caption'], font=MYUNGJO, size=8.5, align='center', color=GRAY, after=6)
        elif typ == 'source':
            hyperlink(doc, "• " + b['text'], b['url'])
        elif typ == 'flow':
            add_p(doc, b['title'], font=GOTHIK, size=9.5, bold=True, align='left', color=GRAY, after=1, keep_next=True)
            chain = "   →   ".join(f"{t}({d})" for t, d in b['nodes'])
            box_para(doc, chain, font=GOTHIK, size=9.5, fill=BOX)
        else:
            raise ValueError(typ)

# 새 쪽에서 시작할 '주요' 제목
import re as _re
_CHAP = _re.compile(r'^\d+장')

def wants_break(title, seen):
    t = title.strip()
    if _CHAP.match(t): return True
    if t == "이 책을 읽는 방법": return True
    if t in ("목차", "머리말"):
        if t in seen: return False
        return True
    return False

def build(source, target):
    data = json.loads(source.read_text())
    chapter = data.get('chapter', 1)
    doc = Document(str(TEMPLATE))
    clear_body(doc)
    seen = set()
    for n, pg in enumerate(data['pages']):
        if pg['kind'] == 'cover':
            # 표지
            for ln in pg['title'].split("\n"):
                add_p(doc, ln, font=GOTHIK, size=26, bold=True, align='center', after=4, line=1.1, before=(60 if ln == pg['title'].split("\n")[0] else 0))
            add_p(doc, pg['subtitle'], font=GOTHIK, size=13, bold=False, align='center', color=GRAY, after=20)
            for bl in pg['blocks']:
                if bl['type'] == 'note':
                    p = add_p(doc, bl['text'], font=MYUNGJO, size=9, align='both', after=5, line=1.4, indent=3)
                    _borders(p._p.get_or_add_pPr(), which=('left',), sz=18, color=GRAY, space=6)
                elif bl['type'] == 'p':
                    add_p(doc, bl['text'], font=MYUNGJO, size=9.5, align='center', color=GRAY, after=4)
            page_break(doc)
            continue
        title = pg['title']
        if wants_break(title, seen) and n != 0:
            page_break(doc)
        seen.add(title.strip())
        # 제목 조판
        if _CHAP.match(title.strip()):
            add_p(doc, title, font=GOTHIK, size=18, bold=True, align='center', after=4, before=20)
            if pg['subtitle']:
                add_p(doc, pg['subtitle'], font=GOTHIK, size=11, bold=True, align='center', color=GRAY, after=10)
        else:
            add_p(doc, title, font=GOTHIK, size=13, bold=True, align='left', after=2, before=10, keep_next=True)
            if pg['subtitle']:
                add_p(doc, pg['subtitle'], font=GOTHIK, size=9.5, bold=False, align='left', color=GRAY, after=6, keep_next=True)
        render_blocks(doc, pg['blocks'], chapter)
    # 문서 속성
    cp = doc.core_properties
    cp.title = data['title']; cp.subject = data['series']; cp.author = "집필팀"; cp.language = "ko-KR"
    cp.comments = data.get('verification_note', '')
    target.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(target))
    print("wrote", target)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, default=ROOT / 'manuscript/volume01-opening.json')
    ap.add_argument('--output', type=Path, default=ROOT / 'manuscript/volume01-opening.docx')
    a = ap.parse_args()
    build(a.source, a.output)

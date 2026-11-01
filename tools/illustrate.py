#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""개념 도식 생성기 — 레트로 픽셀 팔레트의 PNG 삽화를 코드로 생성한다(저자용).
AI 장면 삽화(assets/illustrations/*.png)와 구분한다. 한글 라벨은 선명하게,
그래픽은 제한 색면·굵은 남색 윤곽·점무늬 음영의 옛 PC 게임풍으로 그린다."""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = "/home/ccc/hack_ir_with_wazuh_book_1/assets/figures"
NANUM = "/usr/share/fonts/truetype/nanum"
GB = NANUM + "/NanumGothicBold.ttf"
GR = NANUM + "/NanumGothic.ttf"
GC = NANUM + "/NanumGothicCoding.ttf"

# 팔레트 (overview.png 계열의 레트로 색면)
PAPER = (245, 242, 234)
NAVY  = (28, 42, 66)
INK   = (33, 54, 76)
TEAL  = (46, 136, 142)
TEALF = (205, 230, 230)
BLUE  = (92, 142, 206)
BLUEF = (210, 224, 246)
PINK  = (223, 120, 150)
PINKF = (247, 220, 228)
AMBER = (232, 176, 78)
AMBERF= (250, 236, 206)
CREAM = (238, 230, 210)
RED   = (176, 58, 64)
REDF  = (238, 206, 206)
GREEN = (74, 150, 110)
GREENF= (214, 236, 222)
WHITE = (252, 251, 248)
GREY  = (150, 160, 172)

def font(path, size): return ImageFont.truetype(path, size)

def dither(d, box, color, step=6):
    """점무늬 음영 — 레트로 느낌."""
    x0, y0, x1, y1 = box
    for y in range(int(y0), int(y1), step):
        for x in range(int(x0) + (y // step % 2) * (step // 2), int(x1), step):
            d.ellipse([x, y, x + 2, y + 2], fill=color)

def rrect(d, box, fill, outline=NAVY, w=6, r=22):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=w)

def ctext(d, cx, cy, text, f, fill=INK, line=1.25):
    lines = text.split("\n")
    hs = [d.textbbox((0, 0), ln, font=f)[3] for ln in lines]
    lh = max(hs) * line
    total = lh * len(lines)
    y = cy - total / 2
    for ln in lines:
        w = d.textbbox((0, 0), ln, font=f)[2]
        d.text((cx - w / 2, y), ln, font=f, fill=fill)
        y += lh

def arrow(d, x1, y1, x2, y2, color=NAVY, w=7, head=16):
    d.line([x1, y1, x2, y2], fill=color, width=w)
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    for s in (+1, -1):
        d.line([x2, y2, x2 - head * math.cos(a - s * 0.5), y2 - head * math.sin(a - s * 0.5)], fill=color, width=w)

def canvas(w, h):
    im = Image.new("RGB", (w, h), PAPER)
    return im, ImageDraw.Draw(im, "RGBA")

def save(im, name):
    os.makedirs(os.path.dirname(os.path.join(OUT, name)), exist_ok=True)
    p = os.path.join(OUT, name); im.save(p); print(p, im.size); return p


# ───────────────────────── 2장 ─────────────────────────
def fig_risk():
    """자산·취약점·위협·위험 (세 겹 + 중앙)."""
    W, H = 1600, 1120
    im, d = canvas(W, H)
    fL = font(GB, 60); fS = font(GR, 42); fC = font(GB, 72)
    rrect(d, [40, 34, W - 40, 162], CREAM, NAVY, 7, 18)
    ctext(d, W // 2, 98, "셋이 겹치는 곳에 위험이 커진다", font(GB, 56), INK)
    cx, r = W // 2, 250
    centers = {"자산": (cx, 440), "취약점": (cx - 215, 720), "위협": (cx + 215, 720)}
    fills = {"자산": (92, 142, 206, 115), "취약점": (46, 136, 142, 115), "위협": (223, 120, 150, 115)}
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    for k, (x, y) in centers.items():
        ld.ellipse([x - r, y - r, x + r, y + r], fill=fills[k])
    im = Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")
    d = ImageDraw.Draw(im, "RGBA")
    for k, (x, y) in centers.items():
        d.ellipse([x - r, y - r, x + r, y + r], outline=NAVY, width=6)
    # 라벨 — 각 원의 겹치지 않는 바깥 영역
    ctext(d, cx, 326, "자산", fL, INK);        ctext(d, cx, 388, "지켜야 할 것", fS, (70, 86, 104))
    ctext(d, cx - 305, 824, "취약점", fL, INK); ctext(d, cx - 305, 886, "약점", fS, (70, 86, 104))
    ctext(d, cx + 305, 824, "위협", fL, INK);   ctext(d, cx + 305, 886, "해를 끼칠 주체", fS, (70, 86, 104))
    ctext(d, cx, 664, "위험", fC, RED)
    ctext(d, W // 2, 1066, "가치 있는 자산에 취약점이 있고 위협이 활동할 때 위험이 커진다", fS, (70, 86, 104))
    save(im, "ch02/risk.png")


def stage_box(d, box, title, sub, fill, tf=None, sf=None):
    rrect(d, box, fill, NAVY, 6, 20)
    x0, y0, x1, y1 = box
    dither(d, [x0 + 10, y1 - 60, x1 - 10, y1 - 14], (255, 255, 255, 90), 7)
    ctext(d, (x0 + x1) / 2, y0 + 58, title, tf, INK)
    if sub:
        ctext(d, (x0 + x1) / 2, y0 + 128, sub, sf, (70, 86, 104))

def fig_log_pipeline():
    """로그 → 이벤트 → 경보 (Decoder/Rule). 큼직한 글자."""
    W, H = 1720, 1020
    im, d = canvas(W, H)
    fT = font(GB, 64); fS = font(GR, 40); fMono = font(GC, 42); fChip = font(GC, 40); fLbl = font(GB, 46)
    rrect(d, [40, 34, W - 40, 158], CREAM, NAVY, 7, 18)
    ctext(d, W // 2, 96, "원본 로그가 이벤트와 경보가 되는 과정", font(GB, 56), INK)
    bw, bh, y0 = 490, 540, 270
    xs = [70, 615, 1160]
    cols = [BLUEF, TEALF, PINKF]
    titles = ["로그", "이벤트", "경보"]
    subs = ["원본 한 줄", "해석 · 필드", "규칙 평가"]
    for i, x in enumerate(xs):
        rrect(d, [x, y0, x + bw, y0 + bh], cols[i], NAVY, 7, 22)
        ctext(d, x + bw / 2, y0 + 70, titles[i], fT, INK)
        ctext(d, x + bw / 2, y0 + 150, subs[i], fS, (70, 86, 104))
    # 로그 한 줄 샘플
    d.rounded_rectangle([xs[0] + 30, y0 + 210, xs[0] + bw - 30, y0 + bh - 40], radius=12, fill=WHITE, outline=GREY, width=4)
    ctext(d, xs[0] + bw / 2, y0 + 210 + (bh - 40 - 210) / 2, "203.0.113.10\nGET /admin\n403", fMono, (60, 72, 92), 1.5)
    # 이벤트 필드 (큰 칩 2개 + 하나 더)
    fields = ["srcip 203.0.113.10", "url /admin", "status 403"]
    for j, t in enumerate(fields):
        yy = y0 + 220 + j * 92
        d.rounded_rectangle([xs[1] + 30, yy, xs[1] + bw - 30, yy + 74], radius=12, fill=WHITE, outline=TEAL, width=4)
        ctext(d, xs[1] + bw / 2, yy + 37, t, fChip, (46, 92, 100))
    # 경보 태그
    d.rounded_rectangle([xs[2] + 30, y0 + 220, xs[2] + bw - 30, y0 + 320], radius=14, fill=AMBERF, outline=AMBER, width=5)
    ctext(d, xs[2] + bw / 2, y0 + 270, "rule.level 5\n관리경로 접근", font(GB, 42), (120, 80, 20), 1.35)
    d.rounded_rectangle([xs[2] + 30, y0 + 346, xs[2] + bw - 30, y0 + 432], radius=12, fill=WHITE, outline=GREY, width=4)
    ctext(d, xs[2] + bw / 2, y0 + 389, "설명과 그룹이\n함께 기록", font(GR, 36), (90, 100, 112), 1.3)
    # 화살표 + Decoder/Rule
    ay = y0 + bh / 2
    arrow(d, xs[0] + bw + 6, ay, xs[1] - 6, ay, w=9, head=22)
    arrow(d, xs[1] + bw + 6, ay, xs[2] - 6, ay, w=9, head=22)
    ctext(d, (xs[0] + bw + xs[1]) / 2, ay - 64, "Decoder", fLbl, TEAL)
    ctext(d, (xs[1] + bw + xs[2]) / 2, ay - 64, "Rule", fLbl, PINK)
    ctext(d, W // 2, 900, "모든 로그가 경보가 되지는 않는다. 대부분은 이벤트로만 남는다.", font(GR, 40), (70, 86, 104))
    save(im, "ch02/log_pipeline.png")


def fig_fpfn():
    """오탐·미탐 2×2."""
    W, H = 1520, 1060
    im, d = canvas(W, H)
    fAx = font(GB, 48); fC = font(GB, 66); fS = font(GR, 40)
    rrect(d, [40, 34, W - 40, 150], CREAM, NAVY, 7, 18)
    ctext(d, W // 2, 92, "공격 성공과 탐지 성공은 다른 사건이다", font(GB, 52), INK)
    gx, gy, cw, ch, gap = 380, 310, 490, 300, 26
    cells = [
        (0, 0, "정탐", "실제 공격 · 탐지됨\n→ 조사 대상", GREENF, GREEN),
        (1, 0, "미탐", "실제 공격 · 탐지 안 됨\n→ 가장 위험", REDF, RED),
        (0, 1, "오탐", "정상 · 탐지됨\n→ 규칙 조정", AMBERF, AMBER),
        (1, 1, "정상", "정상 · 탐지 안 됨", WHITE, GREY),
    ]
    for col, row, title, sub, fill, oc in cells:
        x = gx + col * (cw + gap); y = gy + row * (ch + gap)
        rrect(d, [x, y, x + cw, y + ch], fill, NAVY, 6, 18)
        if title == "미탐":
            dither(d, [x + 12, y + 12, x + cw - 12, y + ch - 12], (176, 58, 64, 60), 9)
        ctext(d, x + cw / 2, y + 70, title, fC, oc if title in ("미탐",) else INK)
        ctext(d, x + cw / 2, y + 180, sub, fS, (60, 74, 92), 1.3)
    # 축 라벨
    ctext(d, gx + cw / 2, gy - 46, "탐지됨", fAx, TEAL)
    ctext(d, gx + cw + gap + cw / 2, gy - 46, "탐지 안 됨", fAx, TEAL)
    # 세로축 (회전)
    for row, lab in [(0, "실제 공격"), (1, "정상 행위")]:
        txt = Image.new("RGBA", (340, 86), (0, 0, 0, 0)); td = ImageDraw.Draw(txt)
        w = td.textbbox((0, 0), lab, font=fAx)[2]; td.text(((340 - w) / 2, 10), lab, font=fAx, fill=PINK)
        txt = txt.rotate(90, expand=True)
        im.paste(txt, (gx - 330, int(gy + row * (ch + gap) + ch / 2 - txt.size[1] / 2)), txt)
    save(im, "ch02/fpfn.png")


if __name__ == "__main__":
    fig_risk()
    fig_log_pipeline()
    fig_fpfn()
    print("done")

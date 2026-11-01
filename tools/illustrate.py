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
    W, H = 1600, 1080
    im, d = canvas(W, H)
    fL = font(GB, 48); fS = font(GR, 30); fC = font(GB, 54)
    rrect(d, [40, 36, W - 40, 150], CREAM, NAVY, 6, 18)
    ctext(d, W // 2, 93, "셋이 겹치는 곳에 위험이 커진다", font(GB, 48), INK)
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
    ctext(d, cx, 318, "자산", fL, INK);        ctext(d, cx, 372, "지켜야 할 것", fS, (70, 86, 104))
    ctext(d, cx - 300, 820, "취약점", fL, INK); ctext(d, cx - 300, 874, "약점", fS, (70, 86, 104))
    ctext(d, cx + 300, 820, "위협", fL, INK);   ctext(d, cx + 300, 874, "해를 끼칠 주체", fS, (70, 86, 104))
    ctext(d, cx, 662, "위험", fC, RED)
    ctext(d, W // 2, 1020, "가치 있는 자산에 취약점이 있고 위협이 활동할 때 위험이 커진다", fS, (70, 86, 104))
    save(im, "ch02/risk.png")


def stage_box(d, box, title, sub, fill, tf=None, sf=None):
    rrect(d, box, fill, NAVY, 6, 20)
    x0, y0, x1, y1 = box
    dither(d, [x0 + 10, y1 - 60, x1 - 10, y1 - 14], (255, 255, 255, 90), 7)
    ctext(d, (x0 + x1) / 2, y0 + 58, title, tf, INK)
    if sub:
        ctext(d, (x0 + x1) / 2, y0 + 128, sub, sf, (70, 86, 104))

def fig_log_pipeline():
    """로그 → 이벤트 → 경보 (Decoder/Rule)."""
    W, H = 1600, 820
    im, d = canvas(W, H)
    fT = font(GB, 46); fS = font(GR, 28); fMono = font(GC, 26); fTag = font(GB, 30)
    rrect(d, [40, 36, W - 40, 140], CREAM, NAVY, 6, 18)
    ctext(d, W // 2, 88, "원본 로그가 이벤트와 경보가 되는 과정", font(GB, 48), INK)
    bw, bh, y0 = 420, 300, 240
    xs = [70, 590, 1110]
    cols = [BLUEF, TEALF, PINKF]
    titles = ["로그", "이벤트", "경보"]
    subs = ["원본 한 줄", "해석 · 필드", "규칙 평가 결과"]
    for i, x in enumerate(xs):
        stage_box(d, [x, y0, x + bw, y0 + bh], titles[i], subs[i], cols[i], fT, fS)
    # 로그 한 줄 샘플
    d.rounded_rectangle([xs[0] + 26, y0 + 176, xs[0] + bw - 26, y0 + bh - 26], radius=10, fill=WHITE, outline=GREY, width=3)
    ctext(d, xs[0] + bw / 2, y0 + 176 + (bh - 26 - 176) / 2, "203.0.113.10\nGET /admin\n403", fMono, (60, 72, 92), 1.3)
    # 이벤트 필드
    fields = ["srcip = 203.0.113.10", "url = /admin", "status = 403"]
    for j, t in enumerate(fields):
        yy = y0 + 170 + j * 44
        d.rounded_rectangle([xs[1] + 26, yy, xs[1] + bw - 26, yy + 36], radius=8, fill=WHITE, outline=TEAL, width=3)
        d.text((xs[1] + 40, yy + 3), t, font=font(GC, 24), fill=(50, 70, 80))
    # 경보 태그
    d.rounded_rectangle([xs[2] + 30, y0 + 176, xs[2] + bw - 30, y0 + 236], radius=10, fill=AMBERF, outline=AMBER, width=4)
    ctext(d, xs[2] + bw / 2, y0 + 206, "rule.level 5  ·  관리경로 접근", fTag, (120, 80, 20))
    d.rounded_rectangle([xs[2] + 30, y0 + 250, xs[2] + bw - 30, y0 + 288], radius=8, fill=WHITE, outline=GREY, width=3)
    ctext(d, xs[2] + bw / 2, y0 + 269, "rule.description", font(GR, 24), (90, 100, 112))
    # 화살표 + Decoder/Rule
    arrow(d, xs[0] + bw + 8, y0 + bh / 2, xs[1] - 8, y0 + bh / 2)
    arrow(d, xs[1] + bw + 8, y0 + bh / 2, xs[2] - 8, y0 + bh / 2)
    ctext(d, (xs[0] + bw + xs[1]) / 2, y0 + bh / 2 - 46, "Decoder", font(GB, 30), TEAL)
    ctext(d, (xs[1] + bw + xs[2]) / 2, y0 + bh / 2 - 46, "Rule", font(GB, 30), PINK)
    ctext(d, W // 2, 700, "모든 로그가 경보가 되지는 않는다. 대부분은 이벤트로만 남는다.", font(GR, 30), (70, 86, 104))
    save(im, "ch02/log_pipeline.png")


def fig_fpfn():
    """오탐·미탐 2×2."""
    W, H = 1500, 1040
    im, d = canvas(W, H)
    fAx = font(GB, 34); fC = font(GB, 44); fS = font(GR, 28)
    rrect(d, [40, 36, W - 40, 140], CREAM, NAVY, 6, 18)
    ctext(d, W // 2, 88, "공격 성공과 탐지 성공은 다른 사건이다", font(GB, 46), INK)
    gx, gy, cw, ch, gap = 360, 300, 480, 300, 24
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
        txt = Image.new("RGBA", (260, 60), (0, 0, 0, 0)); td = ImageDraw.Draw(txt)
        w = td.textbbox((0, 0), lab, font=fAx)[2]; td.text(((260 - w) / 2, 6), lab, font=fAx, fill=PINK)
        txt = txt.rotate(90, expand=True)
        im.paste(txt, (gx - 300, int(gy + row * (ch + gap) + ch / 2 - txt.size[1] / 2)), txt)
    save(im, "ch02/fpfn.png")


if __name__ == "__main__":
    fig_risk()
    fig_log_pipeline()
    fig_fpfn()
    print("done")

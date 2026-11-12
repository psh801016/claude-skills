#!/usr/bin/env python
"""photo_grid.py — 사진·도면 이미지에 픽셀 격자 + 표식을 얹어 AI 가 좌표를 '격자 숫자'로 읽게 한다.

배경(2026-11-09): 무카 CAD(cowsdelete.com/cad) 의 '사진 → 3D' 절차를 분석해 들여옴.
AI 는 자가 없어서 이미지 위치를 눈대중으로 재면 틀린다(INWEPF 실패 원인). 격자 숫자를 읽으면
확대·축소된 화면이라도 원본 픽셀 좌표가 그대로 나온다. 중요한 점은 먼저 --mark 로 찍어 맞는지
확인한 뒤 쓴다. 치수 1개(--measure + --mm)로 mm/px 를 계산한다.

사용:
  python photo_grid.py 사진.jpg -o grid.png                       # 전체, 굵은 선 간격 자동(약 14칸)
  python photo_grid.py 사진.jpg -o grid.png --crop 300 800 900 1400 --step 50
  python photo_grid.py 사진.jpg -o grid.png --mark 412,1180,A --mark 980,1176,B
  python photo_grid.py 사진.jpg --measure 412,1180 980,1176 --mm 500   # → mm_per_px 출력(그림 없이)
출력: 마지막 줄 JSON {size, crop, step, image_scale, mm_per_px?}. 빨간 숫자 = x(px), 파란 숫자 = y(px, 아래로 증가).
"""
import argparse, json, math, sys
from PIL import Image, ImageDraw, ImageFont


def nice_step(span, n=14):
    raw = span / n
    p = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if m * p >= raw:
            return m * p
    return 10 * p


def grid_image(img, crop=None, step=None, marks=(), max_px=1400, max_zoom=6):
    W0, H0 = img.size
    x0, y0, x1, y1 = crop if crop else (0, 0, W0, H0)
    x0 = max(0, min(x0, W0 - 2)); y0 = max(0, min(y0, H0 - 2))
    x1 = max(x0 + 2, min(x1, W0)); y1 = max(y0 + 2, min(y1, H0))
    cw, ch = x1 - x0, y1 - y0
    k = min(max_px / max(cw, ch), max_zoom)
    W, H = round(cw * k), round(ch * k)
    out = img.crop((x0, y0, x1, y1)).convert("RGB").resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(out, "RGBA")
    step = step if step and step > 0 else nice_step(max(cw, ch))
    minor = step / 2
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except OSError:
        font = ImageFont.load_default()

    def label(t, X, Y, col):
        tw = d.textlength(t, font=font) + 6
        d.rectangle([X, Y, X + tw, Y + 17], fill=(255, 255, 255, 220))
        d.text((X + 3, Y + 2), t, fill=col, font=font)

    for st, col in ((minor, (80, 190, 255, 140)), (step, (255, 40, 40, 220))):
        x = math.ceil(x0 / st) * st
        while x <= x1:
            X = round((x - x0) * k); d.line([(X, 0), (X, H)], fill=col, width=1); x += st
        y = math.ceil(y0 / st) * st
        while y <= y1:
            Y = round((y - y0) * k); d.line([(0, Y), (W, Y)], fill=col, width=1); y += st
    x = math.ceil(x0 / step) * step
    while x <= x1:
        X = round((x - x0) * k)
        for Y in (2, H // 2, H - 20):
            label(str(round(x)), X + 2, Y, (200, 0, 0))
        x += step
    y = math.ceil(y0 / step) * step
    while y <= y1:
        Y = round((y - y0) * k)
        for X in (2, W // 2):
            label(str(round(y)), X, Y + 2, (0, 71, 179))
        y += step
    for mx, my, name in marks[:60]:
        X, Y = (mx - x0) * k, (my - y0) * k
        d.line([(X - 12, Y), (X + 12, Y)], fill=(255, 230, 0, 255), width=3)
        d.line([(X, Y - 12), (X, Y + 12)], fill=(255, 230, 0, 255), width=3)
        d.ellipse([X - 5, Y - 5, X + 5, Y + 5], outline=(0, 0, 0, 255), width=1)
        if name:
            label(str(name), X + 8, Y + 6, (0, 0, 0))
    info = {"size": [W0, H0], "crop": [round(x0), round(y0), round(x1), round(y1)], "step": step,
            "image_scale": round(k, 3),
            "note": "위치는 반드시 격자 숫자(원본 px)로 읽는다. 빨강=x, 파랑=y(아래로 증가). 노란 + = 지정한 점"}
    return out, info


def parse_pt(s):
    p = s.split(",")
    return float(p[0]), float(p[1]), (p[2] if len(p) > 2 else "")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("-o", "--out")
    ap.add_argument("--crop", nargs=4, type=float, metavar=("X0", "Y0", "X1", "Y1"))
    ap.add_argument("--step", type=float, help="굵은 선 간격(px). 생략하면 약 14칸으로 자동")
    ap.add_argument("--mark", action="append", default=[], help="x,y[,이름] — 여러 번")
    ap.add_argument("--measure", nargs=2, metavar=("P1", "P2"), help="x,y 두 점 — 기준 치수 양 끝")
    ap.add_argument("--mm", type=float, help="--measure 두 점 사이 실제 길이(mm)")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # 한글 note 가 cp949 콘솔에서 깨지지 않게 (test 가 utf-8 로 읽음)
    except Exception:
        pass
    img = Image.open(a.image)
    info = {"size": list(img.size)}
    if a.measure:
        (ax, ay, _), (bx, by, _) = parse_pt(a.measure[0]), parse_pt(a.measure[1])
        px = math.hypot(bx - ax, by - ay)
        info["px_dist"] = round(px, 2)
        if a.mm:
            info["mm_per_px"] = round(a.mm / px, 5)
    if a.out:
        out, gi = grid_image(img, a.crop, a.step, [parse_pt(m) for m in a.mark])
        out.save(a.out)
        info.update(gi); info["out"] = a.out
    print(json.dumps(info, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

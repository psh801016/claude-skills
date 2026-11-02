"""족자봉 상·하단 여유 검사 — 판마다 글자·그림(뚜렷한 경계)이 판 위·아래 끝에서 몇 mm 떨어져 시작하는지 잰다.
족자봉 봉·마감에 가려지지 않게 위·아래 70mm 이상 여유가 필요하다 (동료 요청 2026-10-22: "상/하단 약 7cm 이상씩 여유").
배경 그라데이션은 경계가 약해 무시하고, 글자·아이콘·선처럼 밝기 차가 큰 경계만 '내용'으로 본다.
사용: python check_margin.py [결과폴더]  → C:/jjb/margin_<key>.png (빨간 선 = 70mm) + 표 출력"""
import json, subprocess, sys
import fitz, numpy as np
from PIL import Image, ImageDraw
K = 72 / 25.4; M, TITLE, LABEL, GAP = 40, 30, 50, 30
SAFE, PXMM = 70, 2   # 70mm, 1mm = 2px
folder = sys.argv[1] if len(sys.argv) > 1 else "C:/jjb/out"
jobs = json.loads(subprocess.run(["node", "-e", "const fs=require('fs');eval(fs.readFileSync('C:/jjb/jsx/jobs.js','utf8').replace(/^\\uFEFF/,''));console.log(JSON.stringify(JOBS))"],
                                 capture_output=True, text=True, encoding="utf-8").stdout)

def margins(img):
    g = np.asarray(img.convert("L"), float)
    e = np.maximum(np.abs(np.diff(g, axis=1))[:-1, :], np.abs(np.diff(g, axis=0))[:, :-1])
    rows = (e > 60).mean(axis=1)                      # 줄마다 뚜렷한 경계 비율
    hit = np.where(rows > 0.004)[0]
    if not len(hit): return None, None
    return hit[0] / PXMM, (len(rows) - 1 - hit[-1]) / PXMM

tight = []
for job in jobs:
    if job.get("hold"): continue
    p = fitz.open(f"{folder}/{job['key']}.ai", filetype="pdf")[0]
    x = M; tiles = []
    for pc in job["pieces"]:
        w, h = pc["W"] / 10, pc["H"] / 10
        r = fitz.Rect(x * K, (M + TITLE + LABEL) * K, (x + w) * K, (M + TITLE + LABEL + h) * K)
        z = pc["W"] * PXMM / r.width
        pix = p.get_pixmap(matrix=fitz.Matrix(z, z), clip=r, alpha=False)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        top, bot = margins(im)
        flag = (top is not None and top < SAFE) or (bot is not None and bot < SAFE)
        if flag: tight.append((job["title"], pc["pos"], top, bot))
        d = ImageDraw.Draw(im)
        for yy in (SAFE * PXMM, im.height - SAFE * PXMM): d.line([(0, yy), (im.width, yy)], fill=(255, 0, 0), width=4)
        tiles.append((pc["pos"], top, bot, im))
        print(f"{job['title']:14s} {pc['pos']:7s} 위 {top if top is not None else '-':>5}mm  아래 {bot if bot is not None else '-':>5}mm  {'★7cm 미만' if flag else ''}")
        x += w + GAP
    # 업체별 확인 그림 (판을 같은 높이로 나란히)
    H = 500; row = [t[3].resize((round(t[3].width * H / t[3].height), H)) for t in tiles]
    sheet = Image.new("RGB", (sum(r.width for r in row) + 20 * (len(row) + 1), H + 50), "#777"); dd = ImageDraw.Draw(sheet); cx = 20
    for (pos, top, bot, _), r in zip(tiles, row):
        sheet.paste(r, (cx, 40)); dd.text((cx, 8), f"{pos}  위 {top}mm / 아래 {bot}mm", fill="white"); cx += r.width + 20
    sheet.save(f"C:/jjb/margin_{job['key']}.png")
print(f"7cm 미만 {len(tight)}판")

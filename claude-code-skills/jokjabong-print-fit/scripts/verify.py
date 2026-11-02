"""족자봉 출력 시트 검증: 시트의 각 판을 원본 같은 영역과 나란히 렌더하고 형태 상관계수를 잰다.
레이아웃 상수는 build.jsx 와 같아야 한다(M=40, TITLE=30, LABEL=32, GAP=30, 시트 1/10)."""
import json, re, subprocess, sys, fitz, numpy as np
from PIL import Image, ImageDraw, ImageFont
# 색 프로필 변환: CMYK 원본은 끄고 비교한다 — 원본(Japan Color 태그)과 결과(새 문서 프로필) 태그가 달라 화면 변환만으로 색이 달라 보였다, CMYK 숫자는 같음 (2026-10-27 굿모닝 측면 verify 오탐).
# RGB 원본(소만사·우리)은 CMYK 로 색맞춤 변환했으니 켜야 비교가 된다. 원본 색모드는 probe.txt 에서 읽는다.
K = 72 / 25.4; M, TITLE, LABEL, GAP = 40, 30, 50, 30
jobs = json.loads(subprocess.run(["node", "-e", "const fs=require('fs');eval(fs.readFileSync('C:/jjb/jsx/jobs.js','utf8').replace(/^\uFEFF/,''));console.log(JSON.stringify(JOBS))"], capture_output=True, text=True, encoding="utf-8").stdout)
ab = {}; cur = None; RGB_SRC = set()
for line in open("C:/jjb/probe.txt", encoding="utf-8"):
    m = re.match(r"== (\S+)", line)
    if m: cur = m.group(1); ab[cur] = []
    if m and "RGB" in line: RGB_SRC.add(cur)
    m = re.search(r"AB\d+ .* W=([\d.]+) H=([\d.]+)", line)
    if m and cur: ab[cur].append((float(m.group(1)), float(m.group(2))))
font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 14)

def render(path, page, clip_mm, width):
    d = fitz.open(path, filetype="pdf"); p = d[page]
    r = fitz.Rect(clip_mm[0] * K, clip_mm[1] * K, (clip_mm[0] + clip_mm[2]) * K, (clip_mm[1] + clip_mm[3]) * K)
    z = width / r.width; pix = p.get_pixmap(matrix=fitz.Matrix(z, z), clip=r)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

def src_region(part):
    s = part["src"]; f = "C:/jjb/src/" + s
    if s.endswith(".eps"): return None
    page = part.get("page", part.get("ab", 1)) - 1
    pr = fitz.open(f, filetype="pdf")[page].rect
    pw, ph = pr.width / K, pr.height / K
    aw, ah = (pw, ph) if s.endswith(".pdf") else ab[s][page]
    ox, oy = (pw - aw) / 2, (ph - ah) / 2
    r = part.get("rect") or ([(aw - part["center"][0]) / 2, (ah - part["center"][1]) / 2, *part["center"]] if part.get("center") else [0, 0, aw, ah])
    return f, page, [ox + r[0], oy + r[1], r[2], r[3]]

ok = True
for job in jobs:
    if job.get("hold"): continue   # 보류 업체(사이즈 확인 대기 등)는 결과물이 없다
    out = f"C:/jjb/out/{job['key']}.ai"
    x = M; tiles = []
    for pc in job["pieces"]:
        w, h = pc["W"] / 10, pc["H"] / 10
        got = render(out, 0, [x, M + TITLE + LABEL, w, h], 240)
        ref, score = None, "visual"
        part = pc["parts"][0]
        if len(pc["parts"]) == 1 and not part.get("pick") and not part.get("img") and not part.get("pre") and not pc.get("safe"):   # 여백맞춤으로 줄인 판도 원본과 일부러 다르다   # 글줄을 옮긴 판은 원본과 일부러 다르다 → 눈으로
            sr = src_region(part)
            if sr and abs(sr[2][2] / sr[2][3] - pc["W"] / pc["H"]) < 0.01:   # 비율이 같은 판만 수치 비교
                fitz.TOOLS.set_icc(part["src"] in RGB_SRC); got = render(out, 0, [x, M + TITLE + LABEL, w, h], 240)
                ref = render(sr[0], sr[1], sr[2], 240).resize(got.size)
                sm = (48, round(48 * got.height / got.width))   # 잔무늬(입자·망점)를 지우고 배치만 비교
                a = np.asarray(ref.convert("L").resize(sm, Image.BOX), float).ravel(); b = np.asarray(got.convert("L").resize(sm, Image.BOX), float).ravel()
                corr = np.corrcoef(a, b)[0, 1]   # 색 변환(RGB→CMYK·혼합 공간) 차이는 무시하고 형태가 같은지만 본다
                mae = np.abs(a - b).mean()
                score = f"corr {corr:.3f} mae {mae:.1f}"
                bad = corr < 0.95 and mae > 6   # 거의 단색 판은 상관계수가 불안정해 밝기 차이로도 통과시킨다
                if bad: ok = False; score += " ✗"
        tiles.append((pc["pos"], score, ref, got))
        x += w + GAP
        print(f"{job['key']:12s} {pc['pos']:6s} {pc['W']}x{pc['H']}  {score}")
    H = max(t[3].height for t in tiles) * 2 + 60; W = sum(t[3].width + 20 for t in tiles) + 20
    sheet = Image.new("RGB", (W, H), "#888"); dr = ImageDraw.Draw(sheet); cx = 20
    for pos, score, ref, got in tiles:
        dr.text((cx, 4), f"{pos} {score}", fill="white", font=font)
        if ref: sheet.paste(ref, (cx, 24))
        sheet.paste(got, (cx, 24 + got.height + 12)); cx += got.width + 20
    sheet.save(f"C:/jjb/check_{job['key']}.png")
print("ALL_OK" if ok else "CHECK_FAILED")
sys.exit(0 if ok else 1)

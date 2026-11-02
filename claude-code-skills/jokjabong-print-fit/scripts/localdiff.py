"""원본 대비 '국소 색 차이' 검사 — 칸(판을 30×40 등분)마다 평균색을 원본과 비교해, 일부 영역만 색이 달라진 곳(반투명이 빠져 진해진 그림 등)을 잡는다.
계기: 2026-10-23 프라이빗 정면 가운데 그림의 반투명이 빠져 파랗게 눌렸는데, 전체 형태 비교(verify.py)는 통과했다 (ASURA님 지적).
사용: python localdiff.py <결과폴더> <라벨칸mm>   (판 배치는 build.jsx 와 같아야 함)"""
import fitz, numpy as np, json, subprocess, re, sys
from PIL import Image
# 색 프로필 변환: CMYK 원본은 끄고 비교한다 — 원본(Japan Color 태그)과 결과(새 문서 프로필) 태그가 달라 화면 변환만으로 색이 달라 보였다, CMYK 숫자는 같음 (2026-10-27 굿모닝 측면 verify 오탐).
# RGB 원본(소만사·우리)은 CMYK 로 색맞춤 변환했으니 켜야 비교가 된다. 원본 색모드는 probe.txt 에서 읽는다.
K = 72 / 25.4; M, TITLE, GAP = 40, 30, 30
folder = sys.argv[1]; LABEL = float(sys.argv[2])
jobs = json.loads(subprocess.run(["node", "-e", "const fs=require('fs');eval(fs.readFileSync('C:/jjb/jsx/jobs.js','utf8').replace(/^\uFEFF/,''));console.log(JSON.stringify(JOBS))"], capture_output=True, text=True, encoding="utf-8").stdout)
ab = {}; cur = None; RGB_SRC = set()
for line in open("C:/jjb/probe.txt", encoding="utf-8"):
    m = re.match(r"== (\S+)", line)
    if m: cur = m.group(1); ab[cur] = []
    if m and "RGB" in line: RGB_SRC.add(cur)
    m = re.search(r"AB\d+ .* W=([\d.]+) H=([\d.]+)", line)
    if m and cur: ab[cur].append((float(m.group(1)), float(m.group(2))))
def rend(path, page, clip, w):
    p = fitz.open(path, filetype="pdf")[page]; z = w / clip.width; pix = p.get_pixmap(matrix=fitz.Matrix(z, z), clip=clip, alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
src_map = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
INCLUDE_SAFE = len(sys.argv) > 4 and sys.argv[4] == "all"   # 여백맞춤 전 결과물(out_prev)을 볼 때만
rows = []
for j in jobs:
    if j.get("hold"): continue
    try: fitz.open(f"{folder}/{j['key']}.ai", filetype="pdf")
    except Exception: continue
    x = M
    for pc in j["pieces"]:
        w, h = pc["W"] / 10, pc["H"] / 10; part = pc["parts"][0]
        if len(pc["parts"]) == 1 and part.get("src") and not part.get("pick") and not part["src"].endswith(".eps") and (INCLUDE_SAFE or not pc.get("safe")) and not part.get("pre"):
            s = part["src"]; f = src_map.get(s, "C:/jjb/src/" + s); page = part.get("page", part.get("ab", 1)) - 1
            pr = fitz.open(f, filetype="pdf")[page].rect; pw, ph = pr.width / K, pr.height / K
            aw, ah = (pw, ph) if s.endswith(".pdf") else ab[s][page]
            rr = part.get("rect") or [0, 0, aw, ah]; ox, oy = (pw - aw) / 2, (ph - ah) / 2
            if abs(rr[2] / rr[3] - pc["W"] / pc["H"]) < 0.01:
                fitz.TOOLS.set_icc(s in RGB_SRC)
                A = rend(f, page, fitz.Rect((ox + rr[0]) * K, (oy + rr[1]) * K, (ox + rr[0] + rr[2]) * K, (oy + rr[1] + rr[3]) * K), 600)
                B = rend(f"{folder}/{j['key']}.ai", 0, fitz.Rect(x * K, (M + TITLE + LABEL) * K, (x + w) * K, (M + TITLE + LABEL + h) * K), 600).resize(A.size)
                g = (A.width // 30, A.height // 30)
                a = np.asarray(A.resize(g, Image.BOX), float); b = np.asarray(B.resize(g, Image.BOX), float)
                d = np.abs(a - b).max(2); base = np.median(d); bad = d > base + 25
                rows.append((d.max() - base, j["key"], pc["pos"], int(bad.sum()), d.size))
                if bad.sum() >= 1: Image.fromarray(np.hstack([np.asarray(A), np.asarray(B)]).astype(np.uint8)).save(f"C:/jjb/localdiff_{j['key']}_{pc['pos'].replace(' ', '')}.png")
        x += w + GAP
for worst, k, pos, bad, n in sorted(rows, reverse=True):
    print(f"{k:12s} {pos:7s} 칸 평균색 차이 최대 {worst:5.1f}  어긋난 칸 {bad:3d}/{n}")
print("LOCAL_OK" if not any(r[3] >= 2 for r in rows) else f"LOCAL_DIFF {sum(1 for r in rows if r[3] >= 2)}판")

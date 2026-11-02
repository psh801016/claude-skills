"""족자봉 시트의 판마다 바탕이 빈(투명) 곳이 있는지 잰다. 판 위치는 build.jsx 레이아웃(M=40, TITLE=30, LABEL=32, GAP=30, 1/10)과 같다.
사용: python check_bg.py [폴더(기본 C:/jjb/out)]  → 빈 곳이 0.1% 넘는 판이 있으면 exit 1
계기: 2026-10-22 스패로우 정면 원본이 판의 30% 를 비워 둬서 ASURA님이 "바탕 없이 있는 건 안 된다" 지적."""
import json, subprocess, sys
import fitz, numpy as np
K = 72 / 25.4; M, TITLE, LABEL, GAP = 40, 30, 50, 30
folder = sys.argv[1] if len(sys.argv) > 1 else "C:/jjb/out"
jobs = json.loads(subprocess.run(["node", "-e", "const fs=require('fs');eval(fs.readFileSync('C:/jjb/jsx/jobs.js','utf8').replace(/^\\uFEFF/,''));console.log(JSON.stringify(JOBS))"],
                                 capture_output=True, text=True, encoding="utf-8").stdout)
bad = 0
for job in jobs:
    if job.get("hold"): continue   # 보류 업체(사이즈 확인 대기 등)는 결과물이 없다
    try: p = fitz.open(f"{folder}/{job['key']}.ai", filetype="pdf")[0]
    except Exception: continue
    x = M; res = []
    for pc in job["pieces"]:
        w, h = pc["W"] / 10, pc["H"] / 10
        r = fitz.Rect(x * K, (M + TITLE + LABEL) * K, (x + w) * K, (M + TITLE + LABEL + h) * K)
        z = 300 / r.width
        pix = p.get_pixmap(matrix=fitz.Matrix(z, z), clip=r, alpha=True)
        a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 4)[1:-1, 1:-1, 3]   # 가장자리 1px 은 안티에일리어스라 뺀다
        empty = (a < 250).mean() * 100
        if empty > 0.1: bad += 1
        res.append(f"{pc['pos']} {empty:.1f}%")
        x += w + GAP
    print(f"{job['key']:12s} 빈 곳: " + " · ".join(res))
print("BG_OK" if not bad else f"BG_EMPTY {bad}판")
sys.exit(1 if bad else 0)

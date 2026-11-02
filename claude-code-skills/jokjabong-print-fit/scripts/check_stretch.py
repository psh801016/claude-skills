"""여백맞춤 '가장자리 늘림' 검사 — 늘린 띠에 무늬·그라데이션이 있으면 줄무늬로 번진다.
계기: 2026-10-28 ASURA님 "니가 임의로 늘린겨? 이렇게 하면 안된다, 이게 안되면 파일을 달라고 해야한다"
(제이콥 우측 판 좌우 가장자리·앤앤에스피·우리아이티·시큐어레터 우측2 에서 줄무늬). 단색 띠만 허용, 나머지는 업체에 파일 요청.
판 가장자리에서 안쪽으로 '첫 줄과 같은 줄'이 1mm 이상 이어지면 늘린 구역으로 보고, 그 띠의 색 편차(%)를 잰다.
사용: python check_stretch.py [결과폴더=out]   → STRETCH_OK / STRETCH_BAD(편차 2% 넘는 판 목록)"""
import fitz, json, subprocess, sys
import numpy as np

fitz.TOOLS.set_icc(False)
K = 72 / 25.4; M, TITLE, LABEL, GAP = 40, 30, 50, 30; PX = 8; LIMIT = 2.0
folder = sys.argv[1] if len(sys.argv) > 1 else "C:/jjb/out"
jobs = json.loads(subprocess.run(["node", "-e", "const fs=require('fs');eval(fs.readFileSync('C:/jjb/jsx/jobs.js','utf8').replace(/^\uFEFF/,''));console.log(JSON.stringify(JOBS))"], capture_output=True, text=True, encoding="utf-8").stdout)
bad = []
for j in jobs:
    if j.get("hold"): continue
    try: p = fitz.open(f"{folder}/{j['key']}.ai", filetype="pdf")[0]
    except Exception: continue
    x = M
    for pc in j["pieces"]:
        w, h = pc["W"] / 10, pc["H"] / 10
        if pc.get("safe"):
            c = fitz.Rect(x * K, (M + TITLE + LABEL) * K, (x + w) * K, (M + TITLE + LABEL + h) * K)
            pm = p.get_pixmap(matrix=fitz.Matrix(PX * 25.4 / 72, PX * 25.4 / 72), clip=c, colorspace=fitz.csCMYK, alpha=False)
            a = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, 4).astype(int)
            for side, arr in (("위", a), ("아래", a[::-1]), ("왼쪽", a.transpose(1, 0, 2)), ("오른쪽", a.transpose(1, 0, 2)[::-1])):
                n = 0
                while n + 1 < arr.shape[0] and np.abs(arr[n + 1] - arr[0]).max() <= 6: n += 1
                if n < PX: continue
                var = np.abs(arr[0] - np.median(arr[0], axis=0)).mean() / 2.55
                if var > LIMIT: bad.append(f"{j['key']} {pc['pos']} {side} {n / PX * 10:.0f}mm 늘림, 줄무늬 {var:.1f}%")
        x += w + GAP
print("\n".join(bad))
print(f"STRETCH_BAD {len(bad)}곳 — 늘리지 말고 업체에 파일 요청" if bad else "STRETCH_OK")
sys.exit(1 if bad else 0)

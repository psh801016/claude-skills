# restore_graphics.py 회귀 테스트 — 2026-11-06 Kofpi 부스2 "팔 어디 감 / 부스에 허리 걸리잖아".
# 사람 마스크 없이(사람 분할이 놓친 상황) 돌려도: ① 스태프 뻗은 손(x 1000~1050, y 830~870)은 생성 사진 그대로
# ② 안쪽 남성 머리(x 1560~1620, y 760~800) 그대로 ③ 앞 카운터 로고(x 920~1130, y 1030~1080)는 원본 렌더에 가깝다.
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, cv2
from PIL import Image
HERE = Path(__file__).parent
K = Path(r"G:\내 드라이브\AI-작업기록\Claude").joinpath("2026-11-06_Kofpi-부스배경2")
src, cand, alpha, g = K / "01_부스_흰배경_2560.png", K / "50_magR_A_2560.png", K / "01_부스_알파.png", K / "54_그래픽마스크.png"
ppl = K / "57_사람마스크_박스.png"
# 2026-11-06 개정: 인쇄물마다 따로 위치 맞춤(글자 두 겹·상판 물결 사고) + 사람 마스크는 빠짐없이 넘긴다(안쪽 남성 덮임 사고)
if not all(p.exists() for p in (src, cand, alpha, g, ppl)):
    print("SKIP 실제 파일 없음"); sys.exit(0)
with tempfile.TemporaryDirectory() as t:
    out = Path(t) / "o.png"
    r = subprocess.run([sys.executable, str(HERE / "restore_graphics.py"), "--src", str(src), "--cand", str(cand), "--alpha", str(alpha),
                        "--gmask", str(g), "--people", str(ppl), "--out", str(out)], capture_output=True, text=True, encoding="utf-8",
                       env={"PYTHONIOENCODING": "utf-8", **__import__("os").environ})
    assert "GRAPHICS_OK" in r.stdout, r.stdout + r.stderr
    o = np.asarray(Image.open(out).convert("RGB")).astype(int); c = np.asarray(Image.open(cand).convert("RGB")).astype(int)
    s_ = np.asarray(Image.open(src).convert("RGB")).astype(int)
    man = np.abs(o[760:1000, 1540:1700] - c[760:1000, 1540:1700]).mean(); assert man < 15, f"안쪽 남성이 덮임 {man:.1f}"
    face = np.abs(o[760:820, 1050:1110] - c[760:820, 1050:1110]).mean(); assert face < 15, f"스태프가 덮임 {face:.1f}"
    # 로고는 생성본의 카운터 자리에 맞춰 몇 px 옮겨 붙으므로 픽셀 차이 대신 ±12px 안에서 원본 로고와의 최대 상관으로 본다
    import cv2
    tpl = cv2.cvtColor(s_[1030:1080, 920:1130].astype(np.uint8), cv2.COLOR_RGB2GRAY)
    win = lambda A: cv2.cvtColor(A[1018:1092, 908:1142].astype(np.uint8), cv2.COLOR_RGB2GRAY)
    mo = cv2.matchTemplate(win(o), tpl, cv2.TM_CCOEFF_NORMED).max(); mc = cv2.matchTemplate(win(c), tpl, cv2.TM_CCOEFF_NORMED).max()
    assert mo > 0.8 and mo > mc, f"카운터 로고가 원본과 다름 {mo:.2f} vs 생성본 {mc:.2f}"
print("TEST_OK")

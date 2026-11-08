# rescale_people.py 회귀 테스트 — 2026-11-06 Kofpi 부스2 "사람 너무 커, 750 한 칸이라니까 키가 거의 2미터".
# 지키는 것: ① 큰 사람 5명을 줄인다(scaled ≥ 4) ② 옛 큰 회색 정장 남성 머리 자리(줄인 뒤 비는 곳)가 사람 없는 판과 같다(복사본·유령 없음).
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np
from PIL import Image
HERE = Path(__file__).parent
K = Path(r"G:\내 드라이브\AI-작업기록\Claude").joinpath("2026-11-06_Kofpi-부스배경2")
img, base, ppl, lock = K / "25_최종.png", K / "22_배경.png", K / "24_사람레이어" / "people_mask.png", K / "01_부스_알파.png"
if not all(p.exists() for p in (img, base, ppl, lock)):
    print("SKIP 실제 파일 없음"); sys.exit(0)
with tempfile.TemporaryDirectory() as t:
    out = Path(t) / "o.png"
    r = subprocess.run([sys.executable, str(HERE / "rescale_people.py"), "--img", str(img), "--base", str(base), "--people", str(ppl),
                        "--lock", str(lock), "--k", "0.90338", "--yh", "720.9", "--out", str(out), "--feet", "2000-2200:1222"],
                       capture_output=True, text=True, encoding="utf-8", env={"PYTHONIOENCODING": "utf-8", **__import__("os").environ})
    assert "RESCALE_OK" in r.stdout, r.stdout + r.stderr
    n = int(r.stdout.split("scaled=")[1].split()[0]); assert n >= 4, r.stdout
    o = np.asarray(Image.open(out).convert("L")).astype(int); b = np.asarray(Image.open(base).convert("L")).astype(int)
    d = np.abs(o[700:735, 1205:1255] - b[700:735, 1205:1255]).mean()   # 옛 큰 남성 머리 꼭대기 자리
    assert d < 12, f"옛 큰 사람 흔적 {d:.1f}"
print("TEST_OK")

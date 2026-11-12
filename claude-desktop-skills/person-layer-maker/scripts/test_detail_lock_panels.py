"""detail_lock_panels 회귀 테스트.
사고 배경(2026-11-11 Kofpi 히어로 컷): 부스를 렌더 픽셀로 통째 덮어 "합성티 / 색감도 안 맞고" — 렌더가 AI 사진보다 밝고 차가웠다.
지킬 것: ① 판 안 색(저주파)은 AI 사진 것 ② 글자(고주파)는 렌더 것 ③ 판 밖은 AI 사진 그대로.
"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, cv2
from PIL import Image

HERE = Path(__file__).parent


def main():
    W, H = 640, 360
    rng = np.random.default_rng(0)
    tex = (rng.random((H, W)) * 255).astype(np.uint8)
    tex = cv2.GaussianBlur(tex, (0, 0), 1.0)
    render = np.dstack([tex] * 3).copy()
    render[100:260, 200:440] = (60, 160, 60)                         # 초록 판
    cv2.putText(render, "TEXT", (230, 200), cv2.FONT_HERSHEY_SIMPLEX, 2.2, (255, 255, 255), 6)   # 원본 글자
    cand = render.astype(np.float32) * np.array([1.0, 0.92, 0.75]) * 0.9   # AI: 더 어둡고 따뜻함
    cand = np.clip(cand, 0, 255).astype(np.uint8)
    cand[100:260, 200:440] = np.clip(np.array([60, 160, 60]) * np.array([1.0, 0.92, 0.75]) * 0.9, 0, 255)  # AI 는 글자를 지움
    alpha = np.zeros((H, W), np.uint8); alpha[90:270, 190:450] = 255
    cand[120:250, 400:430] = 15                                       # 판 앞 사람(어두운 정장) — 2026-11-11 검은 번짐 사고
    ppl = np.zeros((H, W), np.uint8); ppl[120:250, 400:430] = 255
    with tempfile.TemporaryDirectory() as td:
        for n, x in (("r", render), ("c", cand), ("a", alpha), ("p", ppl)):
            Image.fromarray(x).save(f"{td}/{n}.png")
        out = subprocess.run([sys.executable, str(HERE / "detail_lock_panels.py"), "--src", f"{td}/r.png", "--alpha", f"{td}/a.png",
                              "--cand", f"{td}/c.png", "--people", f"{td}/p.png", "--panels", "p:200,100,440,260", "--out", f"{td}/o.png"],
                             capture_output=True, text=True, encoding="utf-8")
        assert "DETAIL_LOCK_OK" in out.stdout, out.stdout + out.stderr
        o = np.asarray(Image.open(f"{td}/o.png").convert("RGB")).astype(float)
    g = lambda x: cv2.cvtColor(x.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(float)
    hp = lambda x: g(x) - cv2.GaussianBlur(g(x), (0, 0), 8)
    corr = np.corrcoef(hp(o)[120:240, 220:420].ravel(), hp(render)[120:240, 220:420].ravel())[0, 1]
    assert corr > 0.8, f"글자 디테일이 렌더와 다름 corr={corr:.2f}"
    lab = lambda x: cv2.cvtColor(x.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(float)[110:250, 210:430].reshape(-1, 3).mean(0)
    assert abs(lab(o)[2] - lab(cand)[2]) < 3, (lab(o), lab(cand))     # 색(노란기)은 AI 사진
    assert np.abs(o[0:60, 0:150] - cand[0:60, 0:150]).max() <= 1      # 판 밖은 AI 그대로
    near = o[150:220, 380:392].mean(); far = o[150:220, 300:312].mean()
    assert near > far - 12, f"사람 옆 판이 어두워짐(검은 번짐) near={near:.0f} far={far:.0f}"
    print("TEST_OK test_detail_lock_panels")


if __name__ == "__main__":
    main()

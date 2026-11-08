# compose_keep_design.py 회귀 테스트 — 2026-11-06 Kofpi 부스 "왜 이따구로 나오는데 / 합성티 안 나게 사진처럼".
# 오려 붙이기 방식에서 난 세 사고를 지킨다: ① 스태프 뻗은 손이 박스 경계에서 잘림 ② 카펫 위 그림자가 타원 얼룩
# ③ 여성 발밑 반사가 각진 짙은 덩어리. 그리고 디자인물(앞 카운터 인쇄면)은 원본 그대로. 실제 파일로 돌고, 없으면 SKIP.
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np
from PIL import Image
HERE = Path(__file__).parent
K = Path(r"G:\내 드라이브\AI-작업기록\Claude").joinpath("2026-11-06_Kofpi-부스배경")
base, cand, lock, ppl = K / "14_배경최종.png", K / "16_magA.png", K / "01_부스_알파.png", K / "18_사람레이어" / "people_mask.png"
if not all(p.exists() for p in (base, cand, lock, ppl)):
    print("SKIP 실제 파일 없음"); sys.exit(0)
with tempfile.TemporaryDirectory() as t:
    out = Path(t) / "o.png"
    r = subprocess.run([sys.executable, str(HERE / "compose_keep_design.py"), "--base", str(base), "--cand", str(cand), "--lock", str(lock),
                        "--people", str(ppl), "--out", str(out)], capture_output=True, text=True, encoding="utf-8",
                       env={"PYTHONIOENCODING": "utf-8", **__import__("os").environ})
    assert "COMPOSE_OK" in r.stdout, r.stdout + r.stderr
    o = np.asarray(Image.open(out).convert("RGB")).astype(int); b = np.asarray(Image.open(base).convert("RGB")).astype(int)
    hand = o[825:860, 1065:1120]; assert (hand[..., 0] - hand[..., 2]).mean() > 15, "스태프 손(살색)이 없음 — 잘림"
    face = np.abs(o[1020:1180, 1240:1420] - b[1020:1180, 1240:1420]).mean(); assert face < 12, f"카운터 인쇄면이 바뀜 {face:.1f}"
    refl = o[1260:1330, 880:1050].mean(2); col = refl.mean(0)
    assert np.abs(np.diff(col)).max() < 12, f"발밑 반사 경계가 각짐 {np.abs(np.diff(col)).max():.1f}"
# ④ "사람 손 뭐여": 걸어오는 남성 손(x 2190~2240, y 900~960)이 후보만큼 선명(반사 흐림이 손을 덮지 않음)
# ⑤ "저 얼룩은 또 뭐고": 안쪽 남성 옆 그래픽 벽(x 1712~1760, y 700~880)이 원본 벽과 같다(정장 번짐 없음)
# ⑥ 사람 둘레 흰 벽 띠 없음: 스태프 오른쪽 패널 흰 면(x 1290~1330, y 760~900)이 원본과 같다
with tempfile.TemporaryDirectory() as t:
    out = Path(t) / "o.png"
    subprocess.run([sys.executable, str(HERE / "compose_keep_design.py"), "--base", str(base), "--cand", str(cand), "--lock", str(lock),
                    "--people", str(ppl), "--out", str(out)], capture_output=True, text=True, encoding="utf-8",
                   env={"PYTHONIOENCODING": "utf-8", **__import__("os").environ})
    import cv2
    o = np.asarray(Image.open(out).convert("L")).astype(np.float32)
    c = cv2.resize(np.asarray(Image.open(cand).convert("L")), (o.shape[1], o.shape[0])).astype(np.float32)
    sharp = lambda g: float(cv2.Laplacian(g, cv2.CV_32F).var())
    so, sc = sharp(o[900:960, 2190:2240]), sharp(c[900:960, 2190:2240])
    assert so > 0.5 * sc, f"손이 뭉개짐 sharp {so:.0f} vs 후보 {sc:.0f}"
    bL = np.asarray(Image.open(base).convert("L")).astype(np.float32)
    pmk = np.asarray(Image.open(ppl).convert("L")) > 20
    def bandd(y0, y1, x0, x1):
        m = ~pmk[y0:y1, x0:x1]; return float(np.abs(o[y0:y1, x0:x1] - bL[y0:y1, x0:x1])[m].mean())
    # 옛 결과(19)는 벽 9.2 / 스태프 둘레 7.6 / 안쪽 남성 둘레 16.2, 고친 뒤(20)는 0.4 / 1.4 / 2.7
    assert bandd(700, 880, 1712, 1760) < 4, f"그래픽 벽 얼룩 {bandd(700, 880, 1712, 1760):.1f}"
    assert bandd(780, 1000, 1240, 1290) < 4, f"스태프 둘레 띠 {bandd(780, 1000, 1240, 1290):.1f}"
    assert bandd(700, 1000, 1801, 1925) < 6, f"안쪽 남성 둘레 띠 {bandd(700, 1000, 1801, 1925):.1f}"
# ⑦ 2026-11-06 부스2 "걸어오는 남성 손·다리": 사람 마스크가 엉덩이에서 잘린 사람(아랫단이 어깨만큼 넓음)은 반사 흐림을 걸지 않는다.
K2 = K.parent / "2026-11-06_Kofpi-부스배경2"
b2, c2, l2, p2 = K2 / "22_배경.png", K2 / "23_magB.png", K2 / "01_부스_알파.png", K2 / "24_사람레이어" / "people_mask.png"
if all(x.exists() for x in (b2, c2, l2, p2)):
    with tempfile.TemporaryDirectory() as t:
        out = Path(t) / "o.png"
        r = subprocess.run([sys.executable, str(HERE / "compose_keep_design.py"), "--base", str(b2), "--cand", str(c2), "--lock", str(l2),
                            "--people", str(p2), "--out", str(out)], capture_output=True, text=True, encoding="utf-8",
                           env={"PYTHONIOENCODING": "utf-8", **__import__("os").environ})
        assert "COMPOSE_OK" in r.stdout, r.stdout + r.stderr
        import cv2
        o2 = np.asarray(Image.open(out).convert("L")).astype(np.float32)
        cc2 = cv2.resize(np.asarray(Image.open(c2).convert("L")), (o2.shape[1], o2.shape[0])).astype(np.float32)
        dl = float(np.abs(o2[950:1220, 2010:2200] - cc2[950:1220, 2010:2200]).mean())
        assert dl < 4, f"걸어오는 남성 다리가 흐려짐 {dl:.1f}"
print("TEST_OK")

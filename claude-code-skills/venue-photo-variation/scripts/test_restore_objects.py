# restore_objects.py 회귀 테스트 — 2026-11-05 KOBC 로비 등록데스크(배경 교체 후보가 데스크 글자를 깨뜨림).
# 합성: 원본 = 무늬 배경 + 글자 있는 물건, 후보 = 전혀 다른 배경 + 물건 글자 뭉갬. 결과의 물건은 원본, 배경은 후보여야 한다. 임시 폴더만 쓴다.
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np, cv2
from PIL import Image
HERE = Path(__file__).parent
rng = np.random.default_rng(0)
with tempfile.TemporaryDirectory() as t:
    d = Path(t); W, H = 640, 360
    src = np.full((H, W, 3), 200, np.uint8); src[:] = rng.integers(150, 220, (H, W, 3))
    obj = np.zeros((H, W), np.uint8); cv2.rectangle(obj, (150, 100), (500, 300), 255, -1)
    src[obj > 0] = (30, 60, 160)
    for i in range(40):  # 특징점용 글자·무늬
        cv2.putText(src, "BMFW", (160 + (i % 5) * 68, 130 + (i // 5) * 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cand = rng.integers(40, 90, (H, W, 3)).astype(np.uint8)
    cand[obj > 0] = cv2.GaussianBlur(src, (0, 0), 1.2)[obj > 0]
    a = np.dstack([src, obj])
    Image.fromarray(src).save(d / "s.png"); Image.fromarray(cand).save(d / "c.png"); Image.fromarray(a, "RGBA").save(d / "m.png")
    r = subprocess.run([sys.executable, str(HERE / "restore_objects.py"), "--src", str(d / "s.png"), "--cand", str(d / "c.png"),
                        "--obj-mask", str(d / "m.png"), "--out", str(d / "o.png"), "--size", f"{W}x{H}"], capture_output=True, text=True, encoding="utf-8")
    assert "OBJ_RESTORE_OK" in r.stdout, r.stdout + r.stderr
    o = np.asarray(Image.open(d / "o.png")).astype(int)
    inner = cv2.erode(obj, np.ones((9, 9), np.uint8)) > 0
    assert np.abs(o - src.astype(int))[inner].mean() < 6, "물건이 원본 픽셀이 아님"
    outer = cv2.dilate(obj, np.ones((9, 9), np.uint8)) == 0
    assert np.abs(o - cand.astype(int))[outer].mean() < 2, "배경이 후보가 아님"
# 2026-11-06 Kofpi 부스 "하단에 겹치는 저거 뭐냐": 밑선 메우기는 바닥 밑선에만, 공중 보 아랫면은 그대로.
import subprocess, tempfile
from pathlib import Path as _P
K = _P(r"G:\내 드라이브\AI-작업기록\Claude").joinpath("2026-11-06_Kofpi-부스배경")
if (K / "02_후보C.png").exists():
    import numpy as _np
    from PIL import Image as _I
    with tempfile.TemporaryDirectory() as t:
        o1, o0 = _P(t) / "on.png", _P(t) / "off.png"
        for o, fe in ((o1, "0.012"), (o0, "0")):
            r = subprocess.run([sys.executable, str(_P(__file__).parent / "restore_objects.py"), "--src", str(K / "01_부스_흰배경.png"),
                                "--cand", str(K / "02_후보C.png"), "--obj-mask", str(K / "01_부스_알파.png"), "--out", str(o), "--floor-edge", fe],
                               capture_output=True, text=True, encoding="utf-8", env={"PYTHONIOENCODING": "utf-8", **__import__("os").environ})
            assert "OBJ_RESTORE_OK" in r.stdout, r.stdout + r.stderr
        a, b = _np.asarray(_I.open(o1).convert("L")).astype(int), _np.asarray(_I.open(o0).convert("L")).astype(int)
        d = _np.abs(a - b) > 12
        assert d[:1000].sum() == 0, f"공중 보·간판 아래가 바뀜 {d[:1000].sum()}px"
        assert d[1050:1280].sum() > 5000, "바닥 밑선 띠가 안 메워짐"
print("TEST_OK")

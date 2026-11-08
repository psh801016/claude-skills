# audit_light_rules.py 회귀 테스트 — 2026-11-05 KOBC 6차 반려(실루엣·굴곡 추종·고보·빔 굵기·수렴·가상 광원·객석 수광)를 다시 잡는지.
# 합성 그림으로 '반려본 특징'은 FAIL, '수정본 특징'은 PASS 여야 한다. 임시 폴더만 쓴다.
import json, subprocess, sys, tempfile
from pathlib import Path
import numpy as np, cv2
from PIL import Image

HERE = Path(__file__).parent
W, H = 400, 300
RNG = np.random.default_rng(3)
TEX = cv2.GaussianBlur(RNG.random((H, W)).astype(np.float32), (0, 0), 1.5)  # 테이블보 주름 흉내


def run(d, face_light, gobo_blur, beam_w, ledger, audience_lit=True, follow_shading=True):
    src = np.full((H, W, 3), 30, np.uint8)
    cv2.circle(src, (60, 20), 6, (200, 200, 210), -1); cv2.circle(src, (340, 20), 6, (200, 200, 210), -1)  # 기구 렌즈
    top = (90 + 60 * TEX[150:160, 50:350])[..., None] * np.array([1.0, 1.04, 1.12])
    src[150:160, 50:350] = np.clip(top, 0, 255).astype(np.uint8)                       # 회청 테이블 윗면(주름)
    src[160:220, 50:350] = (np.clip(10 + 25 * TEX[160:220, 50:350], 0, 255)[..., None] * np.array([1, 1, 3.2])).astype(np.uint8)
    obj = np.zeros((H, W), np.uint8); obj[150:220, 50:350] = 255
    plate = np.zeros((H, W, 3), np.float32)
    if audience_lit:
        lum = cv2.cvtColor(src, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
        if follow_shading:
            plate[150:220, 50:350] = (160 * np.clip((lum - 0.07) / 0.33, 0, 1) ** 1.6)[150:220, 50:350, None]
        else:
            plate[150:220, 50:350] = 120   # 가구 전체에 평평한 띠(v6 반려 특징)
        plate[170:220, 50:350] = np.maximum(plate[170:220, 50:350], face_light)
        plate = cv2.GaussianBlur(plate, (0, 0), 1.2)
    plate = plate.astype(np.uint8)
    gobo = np.zeros((H, W), np.uint8); cv2.circle(gobo, (80, 60), 40, 200, -1)
    if gobo_blur:
        gobo = cv2.GaussianBlur(gobo, (0, 0), gobo_blur)
    beams = np.zeros((H, W), np.uint8); cv2.line(beams, (200, 0), (260, 140), 200, beam_w)
    for n, a in (("src", src), ("obj", obj), ("plate", plate), ("gobo", gobo), ("beams", beams)):
        Image.fromarray(a).save(d / f"{n}.png")
    (d / "ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
    r = subprocess.run([sys.executable, str(HERE / "audit_light_rules.py"), "--plate", str(d / "plate.png"),
                        "--obj-mask", str(d / "obj.png"), "--src", str(d / "src.png"), "--ledger", str(d / "ledger.json"),
                        "--gobo", str(d / "gobo.png"), "--beams", str(d / "beams.png")],
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout


GOOD = {"led": [[150, 40, 250, 120]], "deck_y": [120, 130], "deck_w": 300,
        "beams": [{"S": [60, 20], "L": [100, 125]}, {"S": [340, 20], "L": [300, 125]}, {"S": [60, 20], "L": [200, 125]}],
        "audience": []}
BAD = {"led": [[150, 40, 250, 120]], "deck_y": [120, 130], "deck_w": 300,
       "beams": [{"S": [60, 20], "L": [190, 125]}, {"S": [340, 20], "L": [200, 125]}, {"S": [100, 20], "L": [210, 125]},
                 {"S": [200, -30], "L": [200, 125]}, {"S": [200, 5], "L": [200, 125]}],   # 수렴 + 가상 광원 + 평평한 천장 출발
       "audience": []}

with tempfile.TemporaryDirectory() as t:
    d = Path(t)
    code, out = run(d, face_light=110, gobo_blur=0, beam_w=5, ledger=BAD, follow_shading=False)
    for key in ("실루엣", "날카로움", "가늘다", "수렴", "가상 광원", "평평"):
        assert key in out, (key, out)
    assert code == 1
    code, out = run(d, face_light=0, gobo_blur=4, beam_w=26, ledger=GOOD, follow_shading=False)   # v6 반려: 평평한 띠
    assert code == 1 and "굴곡을 안 따라감" in out, out
    code, out = run(d, face_light=5, gobo_blur=30, beam_w=26, ledger=GOOD)
    assert code == 1 and "뭉개짐" in out, out
    code, out = run(d, face_light=5, gobo_blur=0, beam_w=26, ledger=GOOD, audience_lit=False)
    assert code == 1 and "객석에 빛이 안 묻음" in out, out
    code, out = run(d, face_light=0, gobo_blur=4, beam_w=26, ledger=GOOD)
    assert code == 0 and out.startswith("AUDIT_PASS"), out
print("TEST_OK")

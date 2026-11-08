# replace_floor.py 회귀 테스트 — 2026-11-05 KOBC 포토존 "바닥 패턴 왜 바뀌어"(물건 자리에 GPT 바닥이 남음·꽃이 바닥에 덮임).
# 합성: 위는 벽, 아래는 AI 무늬 바닥, 가운데 물건(keep). 결과: 벽·물건 픽셀 그대로, 바닥은 카펫 결로 바뀜, 큰 밝기는 유지.
import numpy as np, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from replace_floor import replace

rng = np.random.default_rng(1)
H, W = 300, 500
img = np.zeros((H, W, 3), np.uint8); img[:120] = (180, 150, 110)                    # 벽
img[120:] = (90, 100, 120) + rng.integers(-40, 40, (H - 120, W, 1)).astype(np.uint8) * 0  # 바닥
img[120:] = np.clip(img[120:].astype(int) + (np.sin(np.arange(W) / 3) * 30).astype(int)[None, :, None], 0, 255)  # AI 무늬
keep = np.zeros((H, W), bool); keep[150:260, 200:300] = True; img[keep] = (20, 30, 120)  # 테이블
carpet = rng.integers(60, 140, (200, 400, 3)).astype(np.uint8)                       # 카펫 사진
out, fl = replace(img, carpet, [0, 0, 400, 200], [0, 120, W, 120], keep)
assert np.array_equal(out[:110], img[:110]), "벽이 바뀜"
inner = np.zeros_like(keep); inner[160:250, 210:290] = True
assert np.abs(out[inner].astype(int) - img[inner].astype(int)).max() == 0, "물건이 바닥으로 덮임"
row = out[280, 10:190].astype(int).mean(1); src = img[280, 10:190].astype(int).mean(1)
assert np.corrcoef(row, src)[0, 1] < 0.6, "바닥 무늬가 그대로 남음"
assert abs(out[fl].mean() - img[fl].mean()) < 8, "바닥 밝기가 크게 바뀜"
print("TEST_OK")

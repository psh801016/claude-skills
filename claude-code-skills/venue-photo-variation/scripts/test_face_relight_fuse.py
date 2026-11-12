# 회귀: ①조명은 다시조명판을 따른다 ②원본의 강한 이목구비 결은 남는다 ③약한 중간 대역 무늬(지렁이)는 줄어든다.
# 배경: 2026-11-12 내 얼굴 실사 — 통째 복원은 원래 조명이 남고, GPT 피부 무늬가 보여 반려.
import os, sys
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
from face_relight_fuse import fuse

S = 256
yy, xx = np.mgrid[:S, :S]
src = np.full((S, S), 150, np.float32)
src[120:124, 90:166] = 60                                     # 강한 결(입술선 같은 4px 어두운 획)
src += 2.5 * np.sin(xx / 2.2) * np.sin(yy / 2.6)              # 약한 중간 대역 무늬(지렁이 흉내)
relit = src * 0.0 + 90                                        # 다시 조명: 전체가 더 어두움
relit[120:124, 90:166] = 40
a = cv2.cvtColor(np.clip(src, 0, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
h = cv2.cvtColor(np.clip(relit, 0, 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
o, _ = fuse(a, h, (128, 128, 90, 90), sigma=12, core=3)
g = cv2.cvtColor(o, cv2.COLOR_BGR2GRAY).astype(np.float32)
patch = g[60:100, 100:156]
assert abs(patch.mean() - 90) < 12, ("조명이 다시조명판을 안 따름", patch.mean())
stroke = g[140:150, 100:156].mean() - g[120:124, 100:156].mean()
assert stroke > 25, ("강한 결이 사라짐", stroke)
src_tex = src[60:100, 100:156].std()
assert patch.std() < src_tex * 0.5, ("약한 무늬가 줄지 않음", patch.std(), src_tex)
print("TEST_OK")

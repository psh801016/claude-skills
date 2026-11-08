# 부스 카메라(렌더 실측)로 로비 기하를 직접 투영한 밑그림 — 생성 모델이 소실점을 못 지켜서(GPT 2.24°, Magnific 4.6°).
# 카메라: 오른쪽 소실점 (3326,776), 왼쪽 (-1394,~776) → f=2339, 주점 (1280,776)(세로선 평행 = 기울기 0, 렌즈 시프트), 눈높이 0.835m.
# 기준: 왼쪽 기둥 앞 모서리 바닥점 (780,1096) = 2m 기둥, 기둥 깊이 0.5m.
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

D = Path(__file__).parent
W, H = 2560, 1440
f, cx, cy = 2339.0, 1280.0, 776.0
hc = 0.835
d1 = np.array([2046.0, 0, 2339.0]); d1 /= np.linalg.norm(d1)      # 부스 정면·벽 방향(오른쪽 깊이)
d2 = np.array([-2674.0, 0, 2339.0]); d2 /= np.linalg.norm(d2)     # 벽 쪽(뒤·왼쪽)
up = np.array([0, -1.0, 0])
P0 = np.array([-500.0, 320.0, f]) * (hc / 320.0)                  # 기둥 앞 모서리 바닥점
WALL_GAP = 2.2  # 2026-11-06 반려 "의자 뒤에 공간이 있어야 사람이 앉지, 지금 벽에 붙어 있어": 0.55 → 2.2m(카운터 0.6 + 직원·통로 1.6)
WALL0 = P0 + WALL_GAP * d2                                        # 벽면 기준점(바닥)
CEIL = 3.4                                                         # 천장 높이(m)


def proj(p):
    return (cx + f * p[0] / p[2], cy + f * p[1] / p[2])


def wall_pt(s, h):
    return WALL0 + s * d1 + h * up


def floor_pt(s, t):
    return WALL0 + s * d1 - t * d2


def ceil_pt(s, t, h=CEIL):
    return WALL0 + s * d1 - t * d2 + h * up


def quad(dr, pts, fill, outline=None, width=1):
    if min(p[2] for p in pts) < 0.4:
        return
    dr.polygon([proj(p) for p in pts], fill=fill, outline=outline, width=width)


def line(dr, a, b, fill, width=2):
    if min(a[2], b[2]) < 0.4:
        return
    dr.line([proj(a), proj(b)], fill=fill, width=width)


img = Image.new("RGB", (W, H), (240, 240, 238))
dr = ImageDraw.Draw(img)
S_MIN, S_MAX = -7.0, 40.0
# 1) 천장(흰색) + 벽 상단 띠(벌크헤드) + 코브 조명 줄
for s in np.arange(S_MIN, S_MAX, 0.5):
    for tt in np.arange(0, 12, 0.3):
        quad(dr, [ceil_pt(s, tt), ceil_pt(s + 0.5, tt), ceil_pt(s + 0.5, tt + 0.3), ceil_pt(s, tt + 0.3)], (246, 246, 244))
for t in (1.2, 3.6, 6.0):  # 벽과 평행한 코브 슬롯(밝은 선)
    for s in np.arange(S_MIN, S_MAX, 0.5):
        quad(dr, [ceil_pt(s, t), ceil_pt(s + 0.5, t), ceil_pt(s + 0.5, t + 0.12), ceil_pt(s, t + 0.12)], (255, 255, 255), None)
        line(dr, ceil_pt(s, t - 0.02), ceil_pt(s + 0.5, t - 0.02), (200, 200, 200), 2)
# 2) 벽: 아이보리 석재 타일(1200x300, 반장 엇갈림) + 회색 줄눈, 상단 3.0~3.4m 흰 띠
for s in np.arange(S_MIN, S_MAX, 0.5):
    quad(dr, [wall_pt(s, 0), wall_pt(s + 0.5, 0), wall_pt(s + 0.5, 3.0), wall_pt(s, 3.0)], (226, 218, 204))
    quad(dr, [wall_pt(s, 3.0), wall_pt(s + 0.5, 3.0), wall_pt(s + 0.5, CEIL), wall_pt(s, CEIL)], (238, 238, 236))
for k in range(0, 11):  # 가로 줄눈
    h = 0.3 * k
    line(dr, wall_pt(S_MIN, h), wall_pt(S_MAX, h), (165, 160, 152), 2)
for k in range(0, 10):  # 세로 줄눈(엇갈림)
    h0 = 0.3 * k
    off = 0.6 if k % 2 else 0.0
    for s in np.arange(S_MIN + off, S_MAX, 1.2):
        line(dr, wall_pt(s, h0), wall_pt(s, h0 + 0.3), (165, 160, 152), 2)
line(dr, wall_pt(S_MIN, 3.0), wall_pt(S_MAX, 3.0), (150, 150, 150), 3)
# 3) 왼쪽 검정 프레임 유리 포털(벽면과 같은 면, 기둥 왼쪽 1.0~4.5m), 안쪽은 어두운 실내
for s in np.arange(-3.4, 0.0, 0.25):  # 벽을 뒤로 뺀 뒤 화면 밖으로 밀려나 데스크 바로 왼쪽으로 당김
    quad(dr, [wall_pt(s, 0), wall_pt(s + 0.25, 0), wall_pt(s + 0.25, 3.0), wall_pt(s, 3.0)], (58, 54, 50))
for a, b in [((-3.4, 0), (-3.4, 3.0)), ((0.0, 0), (0.0, 3.0)), ((-3.4, 3.0), (0.0, 3.0))]:
    line(dr, wall_pt(*a), wall_pt(*b), (10, 10, 10), 10)
# 4) 바닥: 따뜻한 연회색 석재 1200x600, 줄눈
for s in np.arange(S_MIN, S_MAX, 0.5):  # 가까운 쪽 조각이 카메라 뒤로 넘어가 통째로 빠지지 않게 t 도 잘게
    for tt in np.arange(0, 12, 0.3):
        quad(dr, [floor_pt(s, tt), floor_pt(s + 0.5, tt), floor_pt(s + 0.5, tt + 0.3), floor_pt(s, tt + 0.3)], (190, 184, 178))
for k in range(0, 21):
    line(dr, floor_pt(S_MIN, 0.6 * k), floor_pt(S_MAX, 0.6 * k), (160, 154, 148), 2)
for s in np.arange(S_MIN, S_MAX, 1.2):
    for tt in np.arange(0, 12, 0.3):
        line(dr, floor_pt(s, tt), floor_pt(s, tt + 0.3), (160, 154, 148), 2)
line(dr, floor_pt(S_MIN, 0), floor_pt(S_MAX, 0), (120, 118, 114), 3)  # 벽 밑선

# 5) 부스(렌더 원본)를 얹는다
r = Image.open(D / "11_렌더2_흰배경.png").convert("RGB")
m = Image.open(D / "11_물건마스크.png").convert("L")
img.paste(r, (0, 0), m)
img.save(D / "19_공간밑그림.png")
print("UNDERLAY_OK", proj(wall_pt(0, 0)), proj(d1 * 1e6 + WALL0))

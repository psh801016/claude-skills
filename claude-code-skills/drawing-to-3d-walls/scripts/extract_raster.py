# extract_raster.py — 래스터 평면도(스샷/이미지)에서 벽선 자동 추출 → walls.json + overlay.png
# 실행: python extract_raster.py <이미지> <작업폴더> [건물폭m]
#   건물폭m = 추출된 벽 bbox 가로의 실치수(축척 근거). 모르면 제원 홀폭으로 역산:
#            건물폭m = 홀폭m × (bbox_px_width / 홀_px_width)  (없으면 100 가정 — 반드시 교정)
# 클린 파이프라인: 색아이콘 제거 → 솔리드 블롭 제거 → Canny → 밴드화(이중선 병합) →
#   작은 노이즈 제거 → skeletonize(단일 중심선) → 그래프 추적(연결 폴리라인) → 단순화.
# ★ overlay.png(원본 위 빨간선=검출벽)를 반드시 눈으로 검증한 뒤 build_walls.py로.
# 의존: opencv-python-headless, scikit-image, numpy
import cv2, numpy as np, json, os, sys
from skimage.morphology import skeletonize

IMG = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else "."
BUILDING_W = float(sys.argv[3]) if len(sys.argv) > 3 else 100.0
os.makedirs(OUT, exist_ok=True)
img = cv2.imread(IMG)
if img is None: raise SystemExit(f"이미지 못읽음: {IMG}")
H, W = img.shape[:2]

# 1. 색 아이콘 제거(안티앨리어싱 halo까지 팽창) → 흰색
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
colored = cv2.dilate((hsv[:, :, 1] > 40).astype(np.uint8), np.ones((13, 13), np.uint8))
img2 = img.copy(); img2[colored > 0] = (255, 255, 255)
gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

# 2. 솔리드 덩어리(빔프로젝터·글자)만 제거 — ★ '꽉 찬(fill_ratio 높은)' 것만.
#    벽선은 검정이어도 얇은 네트워크(fill_ratio 낮음)라 보존된다. (CAD 검정벽 도면 대응)
dark = (gray < 95).astype(np.uint8)
n, lab, stats, _ = cv2.connectedComponentsWithStats(dark, 8)
blob = colored.copy() * 255
for i in range(1, n):
    a = stats[i, cv2.CC_STAT_AREA]
    w_, h_ = stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]
    fill = a / max(1, w_ * h_)
    if a > 40 and a < 9000 and fill > 0.35:   # 작고 꽉 찬 = 아이콘/글자만
        blob[lab == i] = 255
blob = cv2.dilate(blob, np.ones((7, 7), np.uint8))

# 3. Canny → 밴드(이중엣지 병합+갭연결) → 작은 노이즈 제거 → skeletonize
edges = cv2.Canny(gray, 25, 90); edges[blob > 0] = 0
band = cv2.dilate(edges, np.ones((5, 5), np.uint8))
band = cv2.morphologyEx(band, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
n2, lab2, st2, _ = cv2.connectedComponentsWithStats((band > 0).astype(np.uint8), 8)
keep = np.zeros_like(band)
for i in range(1, n2):
    if st2[i, cv2.CC_STAT_AREA] > 500: keep[lab2 == i] = 255
sk = skeletonize(keep > 0)

# 4. 스켈레톤 그래프 추적 → 연결 폴리라인 (곡선·연속성 보존, 단일 중심선)
pts = set(map(tuple, np.column_stack(np.where(sk)[::-1]).tolist()))
def nbrs(p):
    x, y = p
    return [(x+dx, y+dy) for dx in (-1,0,1) for dy in (-1,0,1)
            if (dx or dy) and (x+dx, y+dy) in pts]
deg = {p: len(nbrs(p)) for p in pts}
nodes = {p for p in pts if deg[p] != 2}
used = set(); polys = []
for s in nodes:
    for nb in nbrs(s):
        if (s, nb) in used: continue
        path = [s]; prev, cur = s, nb
        while True:
            path.append(cur); used.add((prev, cur)); used.add((cur, prev))
            if cur in nodes: break
            nxt = [q for q in nbrs(cur) if q != prev]
            if not nxt: break
            prev, cur = cur, nxt[0]
        if len(path) >= 2: polys.append(path)
for s in pts:  # 순수 루프(노드 없는 닫힌 방)
    if deg[s] == 2 and all((s, q) not in used for q in nbrs(s)):
        path = [s]; prev, cur = s, nbrs(s)[0]
        while cur != s:
            path.append(cur); used.add((prev, cur)); used.add((cur, prev))
            nxt = [q for q in nbrs(cur) if q != prev]
            if not nxt: break
            prev, cur = cur, nxt[0]
        path.append(s)
        if len(path) >= 4: polys.append(path)

# 5. 단순화 + 짧은 노이즈 폴리라인 제거
def plen(pl): return sum(np.hypot(pl[i+1][0]-pl[i][0], pl[i+1][1]-pl[i][1]) for i in range(len(pl)-1))
segs_px = []
for path in polys:
    if plen(path) < 18: continue
    # eps=8: 저해상 래스터의 잔물결(울퉁불퉁) 제거 → 곧은 직선벽. 연결은 폴리라인이라 유지됨.
    # 더 반듯하게: 값↑ / 곡선 살리려면 값↓.
    ap = cv2.approxPolyDP(np.array(path, np.int32).reshape(-1, 1, 2), 8.0, False).reshape(-1, 2)
    for a, b in zip(ap[:-1], ap[1:]):
        segs_px.append((int(a[0]), int(a[1]), int(b[0]), int(b[1])))
if not segs_px: raise SystemExit("벽선 미검출 — Canny/노이즈 파라미터 조정 필요")

# ── X 표시(빈공간/void) 제외 ── 건축 도면 규칙: 사각형 안 대각선 X = 오픈/빈공간(open to below), 벽 아님.
# 판정: 두 세그먼트가 서로 중앙부(20~80%)에서 교차 + 각도차 큼 = X 대각선쌍 → 그 bbox 안 세그먼트 전부 제거.
import math as _m
def _len(s): return _m.hypot(s[2]-s[0], s[3]-s[1])
def _cross(a, b):  # 두 선분이 각자 중앙부에서 교차하나
    d = (a[2]-a[0])*(b[3]-b[1]) - (a[3]-a[1])*(b[2]-b[0])
    if abs(d) < 1e-6: return False
    t = ((b[0]-a[0])*(b[3]-b[1]) - (b[1]-a[1])*(b[2]-b[0])) / d
    u = ((b[0]-a[0])*(a[3]-a[1]) - (b[1]-a[1])*(a[2]-a[0])) / d
    return 0.3 < t < 0.7 and 0.3 < u < 0.7
def _adiff(a, b):
    d = abs(_m.atan2(a[3]-a[1], a[2]-a[0]) - _m.atan2(b[3]-b[1], b[2]-b[0])) % _m.pi
    return min(d, _m.pi - d)
# ★ 원본 엣지에서 전체 대각선 확보(skeleton은 X를 분기로 쪼갬) → 중앙교차하는 대각선쌍 = X
_hl = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=45, minLineLength=45, maxLineGap=12)
_raw = [tuple(map(int, l[0])) for l in _hl] if _hl is not None else []
voids = []
for i in range(len(_raw)):
    for j in range(i+1, len(_raw)):
        a, b = _raw[i], _raw[j]
        if _adiff(a, b) > _m.radians(45) and _cross(a, b) and 0.55 < _len(a)/max(1, _len(b)) < 1.8:
            xs = [a[0], a[2], b[0], b[2]]; ys = [a[1], a[3], b[1], b[3]]
            voids.append((min(xs), min(ys), max(xs), max(ys)))
def _in(p, v, mg=8): return v[0]-mg <= p[0] <= v[2]+mg and v[1]-mg <= p[1] <= v[3]+mg
if voids:
    before = len(segs_px)
    segs_px = [s for s in segs_px if not any(_in(((s[0]+s[2])/2, (s[1]+s[3])/2), v) for v in voids)]
    print(f"X 빈공간(void) {len(voids)}곳 감지 → 세그 {before}→{len(segs_px)} (벽 제외)")

# 검증 오버레이
ov = cv2.addWeighted(img, 0.35, np.full_like(img, 255), 0.65, 0)
for x0, y0, x1, y1 in segs_px: cv2.line(ov, (x0, y0), (x1, y1), (0, 0, 255), 2)
cv2.imwrite(os.path.join(OUT, "overlay.png"), ov)

# 축척: 벽 bbox 가로 = BUILDING_W (m)
xs = [c for s in segs_px for c in (s[0], s[2])]; ys = [c for s in segs_px for c in (s[1], s[3])]
minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
SCALE = BUILDING_W / (maxx - minx)
out = [[round((x0-minx)*SCALE, 3), round((maxy-y0)*SCALE, 3),
        round((x1-minx)*SCALE, 3), round((maxy-y1)*SCALE, 3), 0.2] for x0, y0, x1, y1 in segs_px]
json.dump({"unit": "m", "wall_height": 3.5, "count": len(out), "segments": out},
          open(os.path.join(OUT, "walls.json"), "w"))
print(f"폴리라인 {len(polys)} → 세그 {len(segs_px)}, 건물 {BUILDING_W:.1f}x{(maxy-miny)*SCALE:.1f}m")
print(f"-> {OUT}\\walls.json + overlay.png  (★ overlay.png 검증 후 build_walls.py)")

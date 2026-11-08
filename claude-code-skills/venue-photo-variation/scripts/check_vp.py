# 물건(부스·데스크)과 배경의 깊이 소실점이 같은지 잰다 — rebg 납품 관문.
# 사고 배경(2026-11-06 성과보고회 로비): GPT 가 참고 사진의 광각 시점을 따라 천장·벽 깊이선을 그려
#   부스 소실점 (3301,777) vs 배경 (2360,713) — 사용자 "천장에서 공간깊이에 각을 봐 지금 부스랑 틀리잖아".
# 방법: 물건 알파 윤곽의 기울어진 직선 → 물건 소실점. 배경(물건 밖)의 같은 쪽으로 기울어진 직선 각각이
#   물건 소실점을 얼마나 빗나가는지(점-직선 거리 → 각도) 중앙값을 낸다.
# 사용: python check_vp.py --img 최종.png --obj-mask 물건.png [--max-deg 1.0]
# 성공 토큰: VP_OK   실패: VP_FAIL (exit 1)
import argparse, sys
import numpy as np, cv2
from PIL import Image


def seg_lines(gray, excl=None, minlen=150, thr=90):
    e = cv2.Canny(gray, 50, 150)
    if excl is not None:
        e[excl] = 0
    L = cv2.HoughLinesP(e, 1, np.pi / 720, thr, minLineLength=minlen, maxLineGap=8)
    if L is None:
        return []
    return [l for l in L[:, 0] if 2 < abs(np.degrees(np.arctan2(l[3] - l[1], l[2] - l[0]))) < 40]


def vanish(ls):
    A, b = [], []
    for x1, y1, x2, y2 in ls:
        n = np.array([y2 - y1, -(x2 - x1)], float); n /= np.linalg.norm(n)
        A.append(n); b.append(n @ [x1, y1])
    return np.linalg.lstsq(np.array(A), np.array(b), rcond=None)[0]


def miss_deg(l, v):
    """선분 방향과, 선분 중점→소실점 방향 사이 각도."""
    x1, y1, x2, y2 = map(float, l)
    d1 = np.array([x2 - x1, y2 - y1]); m = np.array([(x1 + x2) / 2, (y1 + y2) / 2]); d2 = v - m
    c = abs(d1 @ d2) / (np.linalg.norm(d1) * np.linalg.norm(d2))
    return float(np.degrees(np.arccos(np.clip(c, -1, 1))))


def ransac_vps(lines, k=2, tol=1.0, iters=3000, seed=0):
    """긴 직선들에서 소실점을 최대 k 개 찾는다. 후보 = 두 선의 교점, 점수 = tol(°) 안에 드는 선 길이 합.
    2026-11-06: 정면선·측면선을 한 무리로 최소제곱하면 소실점이 치우쳤다(로비 3326 → 실제 약 3500, 배경 2.2° 어긋남)."""
    rng = np.random.default_rng(seed)
    L = [np.array(l, float) for l in lines]; vps = []
    for _ in range(k):
        if len(L) < 2: break
        w = np.array([np.hypot(l[2] - l[0], l[3] - l[1]) for l in L]); best = None
        for _ in range(iters):
            a, b = rng.choice(len(L), 2, replace=False, p=w / w.sum())
            v = vanish([L[a], L[b]])
            if not np.all(np.isfinite(v)): continue
            inl = np.array([miss_deg(l, v) < tol for l in L])
            sc = w[inl].sum()
            if inl.sum() >= 2 and (best is None or sc > best[0]): best = (sc, inl)
        if best is None: break
        inl = best[1]; v = vanish([l for l, ok in zip(L, inl) if ok])
        vps.append((v, int(inl.sum())))
        L = [l for l, ok in zip(L, inl) if not ok]
    return vps


def object_lines(img, obj):
    """물건 알파 윤곽 + 물건 안 긴 직선(패널 이음·상판). 그래픽 글자 잡음은 길이 120px 로 거른다."""
    a = seg_lines((obj * 255).astype(np.uint8), None, 120, 80)
    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    inner = cv2.erode(obj.astype(np.uint8), np.ones((5, 5), np.uint8)) == 0
    b = seg_lines(g, inner, 200, 120)
    return a + b


def measure(img, obj, src=None):
    obj_l = object_lines(src if src is not None else img, obj)
    vs = [v for v, n in ransac_vps(obj_l) if n >= 3]
    if not vs:
        vs = [vanish(obj_l)]
    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    excl = cv2.dilate(obj.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
    bg = seg_lines(g, excl, 150, 90)
    # 물건 소실점 쪽으로 향하는 배경선만(반대편 소실점·사선 잡음 제외): 선 방향이 소실점 방향과 15° 이내
    near = [l for l in bg if min(miss_deg(l, u) for u in vs) < 15]
    errs = [min(miss_deg(l, u) for u in vs) for l in near]
    return vs, len(obj_l), len(near), (float(np.median(errs)) if errs else None), (vanish(near) if len(near) >= 3 else None)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", required=True); ap.add_argument("--obj-mask", required=True)
    ap.add_argument("--max-deg", type=float, default=1.0)
    a = ap.parse_args()
    img = np.asarray(Image.open(a.img).convert("RGB"))
    obj = np.asarray(Image.open(a.obj_mask).convert("L").resize(img.shape[1::-1])) > 127
    vs, n_obj, n_bg, med, vb = measure(img, obj)
    info = f"obj_vp={[(int(u[0]), int(u[1])) for u in vs]} obj_lines={n_obj} bg_lines={n_bg} median_miss={med if med is None else round(med, 2)}deg bg_vp={None if vb is None else (int(vb[0]), int(vb[1]))}"
    if n_obj < 4 or n_bg < 5 or med is None:
        print("VP_FAIL 직선 부족 — 육안 판정 필요 " + info); sys.exit(1)
    if med > a.max_deg:
        print(f"VP_FAIL 배경 깊이선이 물건 소실점을 빗나감(중앙값 {med:.2f}° > {a.max_deg}°) " + info); sys.exit(1)
    print("VP_OK " + info)


if __name__ == "__main__":
    main()

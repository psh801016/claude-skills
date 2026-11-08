# 실사화 뒤 글자·로고·인쇄 패널만 원본 렌더로 되돌린다 — 앞에 선 사람·팔·서류는 절대 덮지 않는다.
# 배경: 2026-11-06 Kofpi 부스2 "부스에 허리 걸리잖아" → "팔 어디 감" → "일부러 이러는 거여? 원인 찾아서 확실히 고쳐".
#   원인: 되돌릴 영역에서 '사람 분할 모델이 잡은 사람'만 뺐다. 모델이 카운터 뒤 스태프·패널 앞 남성을 놓치면 그 몸·팔이 패널로 덮였다.
#   고정 판정: 위치를 맞춘 생성 사진과 원본 렌더의 '굵은 큰 차이'(11px 열기에서 살아남고 300px 넘는 덩어리) 중 초록 잉크색이 아닌 것
#   = 가리는 물체(사람·팔·머리·옷·서류). 글자가 바뀐 차이는 가는 획이라 열기에서 사라지고, 로고·패널 초록은 잉크색이라 남지 않는다.
# 사용: python restore_graphics.py --src 원본렌더.png --cand 실사화.png --alpha 부스알파.png --gmask 그래픽마스크.png --out 결과.png [--people 사람마스크.png]
# 성공 토큰: GRAPHICS_OK <경로> occluder_px=<n> restored_px=<n>
import argparse, subprocess, sys, tempfile
from pathlib import Path
import numpy as np, cv2
from PIL import Image


def load(p, mode="RGB"):
    return np.asarray(Image.open(p).convert(mode))


def occluders(cand, orig, alpha):
    orb = cv2.ORB_create(8000); fm = cv2.dilate(alpha.astype(np.uint8) * 255, np.ones((15, 15), np.uint8))
    k1, d1 = orb.detectAndCompute(cv2.cvtColor(cand, cv2.COLOR_RGB2GRAY), fm); k2, d2 = orb.detectAndCompute(cv2.cvtColor(orig, cv2.COLOR_RGB2GRAY), fm)
    ms = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d1, d2), key=lambda x: x.distance)[:2000]
    p1 = np.float32([k1[m.queryIdx].pt for m in ms]); p2 = np.float32([k2[m.trainIdx].pt for m in ms])
    A, _ = cv2.estimateAffinePartial2D(p1, p2, method=cv2.RANSAC, ransacReprojThreshold=3.0)
    h, w = orig.shape[:2]
    cw = cv2.warpAffine(cand, A, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    d = np.abs(cv2.GaussianBlur(cw.astype(np.float32), (0, 0), 2) - cv2.GaussianBlur(orig.astype(np.float32), (0, 0), 2)).max(2) > 55
    hsv = cv2.cvtColor(cw, cv2.COLOR_RGB2HSV)
    ink = (hsv[..., 0] > 35) & (hsv[..., 0] < 95) & (hsv[..., 1] > 40)
    occ = cv2.morphologyEx((d & ~ink).astype(np.uint8), cv2.MORPH_OPEN, np.ones((11, 11), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(occ); keep = np.zeros_like(occ)
    for j in range(1, n):
        if st[j][4] > 300: keep[lab == j] = 1
    return cv2.dilate(keep, np.ones((13, 13), np.uint8)) > 0, cw   # 13px — 25px 는 사람 옆 글자 띠가 생성본으로 남았고, 사람에 붙은 덩어리 판정(--people)으로 서류는 따로 지킨다


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    for n in ("--src", "--cand", "--alpha", "--gmask", "--out"): ap.add_argument(n, required=True)
    ap.add_argument("--people")
    a = ap.parse_args()
    orig = load(a.src); h, w = orig.shape[:2]
    cand = cv2.resize(load(a.cand), (w, h), interpolation=cv2.INTER_LANCZOS4)
    alpha = cv2.resize(load(a.alpha, "L"), (w, h)) > 127
    g = cv2.resize(load(a.gmask, "L"), (w, h), interpolation=cv2.INTER_NEAREST) > 127
    occ, cw = occluders(cand, orig, alpha)
    if a.people:
        # 사람이 주어지면 사람에 붙은 덩어리만 가림 물체로 — 생성 모델이 인쇄 내용을 바꿔 그린 자리(사람과 떨어진 큰 차이)까지
        #   가림으로 보면 그 글자가 원본으로 안 돌아왔다(2026-11-06 부스1 앞 카운터 "연구재를 상재들 헌시")
        pp = cv2.resize(load(a.people, "L"), (w, h)) > 127
        near = cv2.dilate(pp.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
        n, lab, st, _ = cv2.connectedComponentsWithStats(occ.astype(np.uint8)); keep = np.zeros((h, w), bool)
        for j in range(1, n):
            c = lab == j
            if (c & near).any(): keep |= c & near   # 사람 근처 부분만
        # 주의: '어두운 덩어리=사람' 같은 추측 규칙은 진한 초록 글자까지 잡아 글자를 깨뜨렸다(2026-11-06) — 사람 마스크(--people)를 빠짐없이 만들어 넘긴다
        occ = keep | pp
    g = g & alpha & ~occ
    # 인쇄물마다 따로 위치를 맞춰 또렷하게 붙인다 — 그림 전체 한 번 맞춤 + 넓은 흐림 섞기는 생성 모델이 카운터를 몇 px 다른 자리에
    #   그린 곳에서 글자 두 겹·상판 물결·유리처럼 비침을 만들었다(2026-11-06 부스1 "하... 진짜 / 뭐냐고").
    out = Path(a.out); res = cw.astype(np.float32).copy(); srcf = orig.astype(np.float32)
    grad = lambda x: cv2.magnitude(cv2.Sobel(x, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(x, cv2.CV_32F, 0, 1, ksize=3))
    gs, gc = cv2.cvtColor(orig, cv2.COLOR_RGB2GRAY).astype(np.float32), cv2.cvtColor(cw, cv2.COLOR_RGB2GRAY).astype(np.float32)
    n, lab, st, _ = cv2.connectedComponentsWithStats(g.astype(np.uint8)); moved = []
    for j in range(1, n):
        x, y, bw, bh, ar = st[j]
        if ar < 300: continue
        m = 60; X0, Y0, X1, Y1 = max(0, x - m), max(0, y - m), min(w, x + bw + m), min(h, y + bh + m)
        T, I = grad(gc[Y0:Y1, X0:X1]), grad(gs[Y0:Y1, X0:X1])
        # 원근(호모그래피)으로 맞춘다 — 생성 모델은 카운터를 원본보다 넓게·기울게 그려, 위치만 맞추면 바깥에 생성본 상판·테두리가
        #   한 겹 더 남았다(2026-11-06 "너 장난치냐"). ECC 호모그래피(그라디언트) → 개선 없으면 항등.
        ncc = lambda A, B: float(((A - A.mean()) * (B - B.mean())).mean() / (A.std() * B.std() + 1e-6))
        Hm = np.eye(3, dtype=np.float32); before = ncc(T, I); best = before
        for motion, init in ((cv2.MOTION_AFFINE, np.eye(2, 3, dtype=np.float32)), (cv2.MOTION_HOMOGRAPHY, np.eye(3, dtype=np.float32))):
            try:
                _, W2 = cv2.findTransformECC(cv2.GaussianBlur(T, (0, 0), 2), cv2.GaussianBlur(I, (0, 0), 2), init, motion,
                                             (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-6), None, 5)
                H3 = np.vstack([W2, [0, 0, 1]]).astype(np.float32) if W2.shape[0] == 2 else W2
                sc = np.linalg.det(H3[:2, :2])
                if not (0.8 < sc < 1.25) or abs(H3[0, 2]) > 40 or abs(H3[1, 2]) > 40: continue
                a2 = ncc(T, cv2.warpPerspective(I, H3, (X1 - X0, Y1 - Y0), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP))
                if a2 > best: best, Hm = a2, H3
            except cv2.error:
                pass
        moved.append(float(np.hypot(Hm[0, 2], Hm[1, 2])))
        wp = lambda A, fl=cv2.INTER_LINEAR: cv2.warpPerspective(A, Hm, (X1 - X0, Y1 - Y0), flags=fl + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
        sp = wp(srcf[Y0:Y1, X0:X1]); mk = wp((lab[Y0:Y1, X0:X1] == j).astype(np.float32))
        mk = mk * (~occ[Y0:Y1, X0:X1]).astype(np.float32)
        # 조명: 후보의 넓은 밝기비(인쇄물 안에서만)
        lm = (mk > 0.5).astype(np.float32)
        lb = lambda A: cv2.GaussianBlur(A.mean(2) * lm, (0, 0), 20) / (cv2.GaussianBlur(lm, (0, 0), 20) + 1e-3) + 6
        ratio = np.clip(lb(res[Y0:Y1, X0:X1]) / lb(sp), 0.75, 1.15)[..., None]
        sp = sp * ratio
        sp = cv2.addWeighted(sp, 1.5, cv2.GaussianBlur(sp, (0, 0), 1.0), -0.5, 0)       # 확대된 렌더의 무름 보정
        al = cv2.GaussianBlur(cv2.erode((mk > 0.5).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 0.8)[..., None]
        res[Y0:Y1, X0:X1] = sp * al + res[Y0:Y1, X0:X1] * (1 - al)
    if out.exists(): out.unlink()
    Image.fromarray(np.clip(res, 0, 255).astype(np.uint8)).save(out)
    print(f"  인쇄물 {len(moved)}개 개별 맞춤, 이동 최대 {max(moved) if moved else 0:.1f}px")
    ov = out.with_name(out.stem + "_overlay50.png")
    if ov.exists(): ov.unlink()
    # 납품 전 전체 검수 시트 — 부분 확대만 보고 냈다가 '블럭마다 회색 네모 얼룩'을 놓쳤다(2026-11-06). 부스 영역을 6칸으로 100% 확대.
    ys, xs = np.where(alpha); bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
    tw, th = (bx1 - bx0) // 3 + 1, (by1 - by0) // 2 + 1
    sheet = Image.new("RGB", (tw * 3 + 20, th * 2 + 10), "black"); rimg = Image.open(out).convert("RGB")
    for i in range(6):
        cx, cy = bx0 + (i % 3) * tw, by0 + (i // 3) * th
        sheet.paste(rimg.crop((cx, cy, cx + tw, cy + th)), ((i % 3) * (tw + 10), (i // 3) * (th + 10)))
    sheet.save(out.with_name(out.stem + "_review.jpg"), quality=88)
    print(f"GRAPHICS_OK {a.out} occluder_px={int((occ & alpha).sum())} restored_px={int(g.sum())} review={out.with_name(out.stem + '_review.jpg').name}")


if __name__ == "__main__":
    main()

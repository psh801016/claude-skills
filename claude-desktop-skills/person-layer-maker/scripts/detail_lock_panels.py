# 부스 실사화 마무리 — AI 사진을 그대로 바탕으로 쓰고, 그래픽 판(글자·로고·일러스트)만 원본 렌더 '디테일'로 되돌린다.
# 사고 배경(2026-11-11 Kofpi 히어로 컷): lock_booth.py 로 부스 전체를 렌더 픽셀로 덮었더니 "합성티 너무 나 / 구도도 안 맞고 / 색감도 안 맞고".
#   원인: 렌더 부스가 AI 사진보다 밝기 +13, 노란기(LAB b) −14 → 부스만 차갑게 떴고, AI 가 그린 바닥 반사·사람·의자와 렌더 집기가 서로 어긋났다.
# 방법: 판마다 렌더→AI 호모그래피(ORB)로 위치를 맞추고, LAB 각 채널 = AI 저주파(σ8, 빛·색) + 렌더 고주파(글자·선). 사람 마스크는 제외.
# 사용: python detail_lock_panels.py --src 렌더(흰배경).png --alpha 부스알파.png --cand AI사진.png --people 사람마스크.png
#           --panels "이름:x0,y0,x1,y1;..." --out 결과.png [--sigma 8]
#   판 박스 = 렌더 좌표, 글자·그래픽이 있는 판만(흰 패널·집기는 넣지 않는다 — AI 것이 더 사실적).
# 성공 토큰: DETAIL_LOCK_OK <경로> panels=<n> min_inliers=<n>
import argparse, sys
import numpy as np, cv2
from PIL import Image


def load(p, mode="RGB"):
    return np.asarray(Image.open(p).convert(mode))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    for n in ("--src", "--alpha", "--cand", "--out", "--panels"):
        ap.add_argument(n, required=True)
    ap.add_argument("--people"); ap.add_argument("--sigma", type=float, default=8.0)
    ap.add_argument("--max-shift", type=float, default=6.0, help="판 모서리가 이보다 많이 움직이면 정렬 안 함(렌더 자리)")
    a = ap.parse_args()
    c = load(a.cand); H, W = c.shape[:2]
    r = cv2.resize(load(a.src), (W, H), interpolation=cv2.INTER_AREA)
    alpha = (cv2.resize(load(a.alpha, "L"), (W, H)) > 127).astype(np.uint8)
    ppl = (cv2.resize(load(a.people, "L"), (W, H)) > 127).astype(np.uint8) if a.people else np.zeros((H, W), np.uint8)
    gr, gc = cv2.cvtColor(r, cv2.COLOR_RGB2GRAY), cv2.cvtColor(c, cv2.COLOR_RGB2GRAY)
    labc = cv2.cvtColor(c, cv2.COLOR_RGB2LAB).astype(np.float32)
    lp = lambda x: cv2.GaussianBlur(x, (0, 0), a.sigma)
    # 2026-11-11 Kofpi 2차: 저주파에 판 앞 사람(어두운 정장)이 섞여 사람 둘레 판에 검은 번짐이 생겼다 → 사람 뺀 정규화 블러
    wp = 1.0 - cv2.dilate(ppl, np.ones((9, 9), np.uint8)).astype(np.float32)
    den = np.maximum(lp(wp), 1e-3)
    base = np.dstack([lp(labc[..., i] * wp) / den for i in range(3)])
    orb = cv2.ORB_create(4000); bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    acc = np.zeros_like(labc); wsum = np.zeros((H, W), np.float32); inls = []
    for item in a.panels.split(";"):
        name, box = item.split(":"); x0, y0, x1, y1 = map(int, box.split(","))
        mr = np.zeros((H, W), np.uint8); mr[y0:y1, x0:x1] = 255; mr &= alpha * 255
        mc = np.zeros((H, W), np.uint8); mc[max(0, y0 - 30):y1 + 30, max(0, x0 - 30):x1 + 30] = 255
        k1, d1 = orb.detectAndCompute(gr, mr); k2, d2 = orb.detectAndCompute(gc, mc)
        Hm, ni = np.eye(3), 0
        if d1 is not None and d2 is not None:
            mt = bf.match(d1, d2)
            if len(mt) >= 8:
                h, inl = cv2.findHomography(np.float32([k1[m.queryIdx].pt for m in mt]), np.float32([k2[m.trainIdx].pt for m in mt]), cv2.RANSAC, 3)
                if h is not None and inl is not None and inl.sum() >= 8:
                    Hm, ni = h, int(inl.sum())
        # 2026-11-11 Kofpi 2차: AI 가 카운터를 다른 모양으로 그리면 호모그래피가 판을 비틀고 늘렸다(글자 기울고 뭉개짐).
        #   모서리 이동이 max-shift(px) 넘으면 렌더 자리 그대로(전체 정렬은 이미 ±2px) — 판 모양을 AI 에 맞추지 않는다.
        cn = np.float32([[x0, y0], [x1, y0], [x1, y1], [x0, y1]]).reshape(-1, 1, 2)
        mv = np.abs(cv2.perspectiveTransform(cn, Hm) - cn).max()
        if mv > a.max_shift:
            print(f"{name}: 모서리 이동 {mv:.0f}px > {a.max_shift} → 렌더 자리 그대로"); Hm, ni = np.eye(3), -1
        inls.append(ni)
        rw = cv2.warpPerspective(r, Hm, (W, H), flags=cv2.INTER_CUBIC)
        mw = cv2.warpPerspective(mr, Hm, (W, H)).astype(np.float32) / 255
        mw = cv2.erode(mw, np.ones((3, 3), np.uint8)) * (1 - cv2.dilate(ppl, np.ones((5, 5), np.uint8)))
        mw = cv2.GaussianBlur(mw, (0, 0), 1.5)
        lr = cv2.cvtColor(rw, cv2.COLOR_RGB2LAB).astype(np.float32)
        det = lr - np.dstack([lp(lr[..., i]) for i in range(3)])
        acc += (base + det) * mw[..., None]; wsum += mw
        print(f"{name}: inliers={ni}")
    w = np.clip(wsum, 0, 1)[..., None]
    pan = cv2.cvtColor(np.clip(acc / np.maximum(wsum, 1e-4)[..., None], 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32)
    res = pan * w + c.astype(np.float32) * (1 - w)          # 판 밖은 AI 원본 픽셀 그대로(LAB 왕복 오차 없음)
    Image.fromarray(np.clip(res + 0.5, 0, 255).astype(np.uint8)).save(a.out)
    print(f"DETAIL_LOCK_OK {a.out} panels={len(inls)} min_inliers={min(inls)}")


if __name__ == "__main__":
    main()

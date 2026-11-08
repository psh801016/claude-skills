# 사람 합성 최종 단계(권장) — 생성 사진을 통째로 바탕으로 쓰고, 디자인물(부스·데스크·포토월)만 원본으로 덮는다.
# 배경: 2026-11-06 Kofpi 부스 "야 너 문제가 뭐냐 도대체 왜 이따구로 나오는데 / 합성티 안 나게 사진처럼".
#   사람을 오려 원본에 붙이고 그림자·반사를 짐작으로 다시 그리던 방식은 경계(손 잘림)·그림자 얼룩·반사 네모가 매번 새로 생겼다.
#   생성 모델은 사람·그림자·반사를 한 번에 맞게 그리므로 그 사진을 살리고, 고쳐야 할 것(디자인 글자·블럭)만 원본으로 되돌린다.
# 사용:
#   python compose_keep_design.py --base 승인배경.png --cand 사람후보.png --lock 디자인물알파.png --people 사람마스크.png --out 결과.png
#   --people = extract_people.py 가 만든 people_mask.png(사람이 선 자리는 디자인물이어도 후보 그대로).
#   디자인물 안: 원본 × 후보의 넓은 밝기비(조명). 디자인물 중 바닥(카펫)처럼 생긴 곳은 좁은 밝기비까지 옮겨 사람 그림자를 살린다.
# 성공 토큰: COMPOSE_OK <경로> rms=<px> hall_diff=<디자인물·사람 밖 평균차>
import argparse, sys
import numpy as np, cv2
from PIL import Image


def load(p, mode="RGB"):
    return np.asarray(Image.open(p).convert(mode))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True); ap.add_argument("--cand", required=True)
    ap.add_argument("--lock", required=True); ap.add_argument("--people", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--refl-soft", type=float, default=0.65, help="발밑 바닥 반사 세기(0~1). 생성 모델이 짙은 네모로 그린 반사를 흐리게 푼다. 1=그대로")
    a = ap.parse_args()
    base = load(a.base); h, w = base.shape[:2]
    cand = cv2.resize(load(a.cand), (w, h), interpolation=cv2.INTER_CUBIC)
    g1, g2 = cv2.cvtColor(cand, cv2.COLOR_RGB2GRAY), cv2.cvtColor(base, cv2.COLOR_RGB2GRAY)
    orb = cv2.ORB_create(10000)
    k1, d1 = orb.detectAndCompute(g1, None); k2, d2 = orb.detectAndCompute(g2, None)
    ms = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d1, d2), key=lambda x: x.distance)[:3000]
    p1 = np.float32([k1[x.queryIdx].pt for x in ms]); p2 = np.float32([k2[x.trainIdx].pt for x in ms])
    A, inl = cv2.estimateAffinePartial2D(p1, p2, method=cv2.RANSAC, ransacReprojThreshold=3.0); inl = inl.ravel().astype(bool)
    rms = float(np.sqrt(np.mean(np.sum((cv2.transform(p1[inl][None], A)[0] - p2[inl]) ** 2, 1))))
    cw = cv2.warpAffine(cand, A, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
    lock = cv2.resize(load(a.lock, "L"), (w, h), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
    ppl = cv2.resize(load(a.people, "L"), (w, h), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
    ppl = cv2.GaussianBlur(cv2.dilate(ppl, np.ones((5, 5), np.uint8)), (0, 0), 1.5)
    bf = base.astype(np.float32)
    lum = lambda x: x.mean(2) + 6
    # 사람 = 가로로 겹치는 마스크 덩어리 묶음(손·허리에서 끊긴 상·하반신을 한 사람으로). 발 = 묶음의 가장 아래.
    #   2026-11-06 "사람 손 뭐여": 끊긴 상반신의 아랫끝을 발로 보고 그 아래에 반사 흐림을 걸어 손이 뭉개졌다.
    pb = (ppl > 0.5).astype(np.uint8); n, lab, st, _ = cv2.connectedComponentsWithStats(pb)
    comps = [list(map(int, st[j][:4])) for j in range(1, n) if st[j][4] >= 300]
    persons = []
    for x0, y0, bw, bh in sorted(comps, key=lambda c: c[0]):
        for P in persons:
            # 위아래로 끊긴 한 사람의 조각만 묶는다(가로 겹침 40%↑ + 세로 겹침이 작은 쪽 키의 30%↓).
            #   나란히 선 두 사람은 세로 범위가 거의 같아 묶지 않는다 — 묶으면 남의 발 기준으로 줄어 얼굴에 띠가 생겼다(2026-11-06 부스1 스태프)
            xo = min(P[2], x0 + bw) - max(P[0], x0); yo = min(P[3], y0 + bh) - max(P[1], y0)
            if xo > 0.4 * min(P[2] - P[0], bw) and yo < 0.3 * min(P[3] - P[1], bh):
                P[:] = [min(P[0], x0), min(P[1], y0), max(P[2], x0 + bw), max(P[3], y0 + bh)]; break
        else:
            persons.append([x0, y0, x0 + bw, y0 + bh])
    persons = [P for P in persons if P[3] - P[1] >= 80]
    near_feet = np.zeros((h, w), np.float32); below_feet = np.zeros((h, w), np.float32)
    for x0, y0, x1, f in persons:
        hh = f - y0
        # 아랫단이 어깨만큼 넓으면 발이 아니라 몸이 잘린 것(짙은 바지가 짙은 바닥에 묻혀 분할이 다리를 못 잡음) → 반사 흐림 안 함
        rows = pb[max(y0, f - max(3, int(hh * .04))):f, x0:x1].sum(1); wmax = pb[y0:f, x0:x1].sum(1).max()
        if wmax and rows.size and rows.mean() > 0.7 * wmax:
            print(f"  person x={x0}-{x1} 아랫단 잘림(폭 {rows.mean() / wmax:.2f}) → 반사 흐림 생략"); continue
        near_feet[max(0, f - int(hh * .04)):min(h, f + int(hh * .10)), max(0, x0 - int(hh * .2)):min(w, x1 + int(hh * .2))] = 1
        below_feet[max(0, f - int(hh * .02)):min(h, f + int(hh * .7)), max(0, x0 - int(hh * .15)):min(w, x1 + int(hh * .15))] = 1
    # 넓은 밝기비(조명) — 디자인물 전체
    # 사람 픽셀은 빼고 평균 — 넣으면 짙은 옷 때문에 사람 둘레 흰 벽이 30~60px 띠로 어두워진다(2026-11-06 전체 점검에서 발견)
    nm0 = 1 - np.clip(cv2.dilate(ppl, np.ones((9, 9), np.uint8)) * 1.5, 0, 1)
    mb30 = lambda x: cv2.GaussianBlur(x * nm0, (0, 0), 30) / (cv2.GaussianBlur(nm0, (0, 0), 30) + 1e-3)
    wide = np.clip(np.nan_to_num((mb30(lum(cw)) + 1) / (mb30(lum(bf)) + 1), nan=1.0), 0.8, 1.15)
    # 좁은 밝기비(사람 그림자) — 디자인물 중 바닥처럼 생긴 곳(채도 낮고 잔무늬 있는 면 = 카펫)만
    hsv = cv2.cvtColor(base, cv2.COLOR_RGB2HSV).astype(np.float32)
    g = lum(bf); tex = np.sqrt(cv2.GaussianBlur((g - cv2.GaussianBlur(g, (0, 0), 1.5)) ** 2, (0, 0), 4))
    floorish = ((hsv[..., 1] < 40) & (tex > 3.0) & (lock > 0.5)).astype(np.float32)
    floorish = cv2.morphologyEx(floorish, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    # 발 근처만 — 그래픽 벽 흰 점무늬도 '카펫처럼' 보여 벽에 정장 번짐이 묻었다(2026-11-06 "저 얼룩은 또 뭐고")
    floorish = cv2.GaussianBlur(floorish * near_feet, (0, 0), 3)
    nm = 1 - np.clip(ppl * 1.5, 0, 1)        # 사람 픽셀은 밝기비 계산에서 뺀다(짙은 옷이 주변으로 번지는 것 방지)
    mblur = lambda x: cv2.GaussianBlur(x * nm, (0, 0), 4) / (cv2.GaussianBlur(nm, (0, 0), 4) + 1e-3)
    narrow = np.clip(np.nan_to_num((mblur(lum(cw)) + 1) / (mblur(lum(bf)) + 1), nan=1.0), 0.45, 1.1)
    ratio = wide * (1 - floorish) + narrow * floorish
    design = bf * ratio[..., None]
    keep = np.clip(lock * (1 - ppl), 0, 1)[..., None]          # 디자인물이면서 사람 아닌 곳 = 원본
    # 발밑 반사 풀기 — 2026-11-06 "여성 발 아래 검은 덩어리": 모델이 반사를 각진 짙은 덩어리로 그렸다. 사람 발 아래(키 70%·좌우 키 15%)
    #   디자인물 밖에서 '후보 − 원본' 차이를 흐리게(σ 키 1%) 하고 세기를 줄여 원본 바닥에 얹는다(사람 몸은 건드리지 않음).
    if a.refl_soft < 1:
        zone = cv2.GaussianBlur(below_feet, (0, 0), 12) * (1 - lock) * (1 - np.clip(ppl * 1.5, 0, 1))
        # 선명한 곳 보호 — 바닥 반사는 원래 흐릿하고 손·다리·구두는 선명하다. 사람 찾기가 몸 일부를 빠뜨려도
        #   (2026-11-06 부스2 걸어오는 남성: 상반신만 잡혀 손·다리에 흐림이 걸림, 같은 흠 두 번째) 선명한 디테일은 흐리지 않는다.
        gc = cw.mean(2); hf = cv2.GaussianBlur(np.abs(gc - cv2.GaussianBlur(gc, (0, 0), 1.5)), (0, 0), 3)
        protect = cv2.dilate(np.clip((hf - 2.5) / 3.0, 0, 1), np.ones((9, 9), np.uint8))
        zone = zone * (1 - protect)
        dif = cv2.GaussianBlur(cw - bf, (0, 0), 5)
        soft = bf + a.refl_soft * dif
        cw = cw * (1 - zone[..., None]) + soft * zone[..., None]
    out = design * keep + cw * (1 - keep)
    out = np.clip(out, 0, 255).astype(np.uint8)
    Image.fromarray(out).save(a.out)
    hall = (lock < 0.02) & (ppl < 0.02)
    hd = float(np.abs(cw - bf).mean(2)[hall].mean())
    print(f"COMPOSE_OK {a.out} rms={rms:.2f} hall_diff={hd:.1f}")


if __name__ == "__main__":
    main()

# 납품 전 자동 검사 — QA_OK 가 없으면 납품하지 않는다.
# 배경: 2026-11-06 Kofpi 부스 하루 반려 30여 건("얼룩/모서리 두 겹/글자 두 겹/잔상/사람 너무 커"). 매번 눈으로 부분만 보고 냈다가 놓쳤다.
# 검사 3가지:
#  ① 부스 무결성: 부스 알파 안·사람 밖에서 결과와 렌더의 '고주파 차이'(조명 저주파는 빼고) — AI 흔적·이음매·두 겹·얼룩은 고주파 차이로 남는다.
#     차이 큰 픽셀 비율 ≤ 0.5% 이고 300px 넘는 덩어리가 없어야 한다(덩어리 위치를 출력).
#  ② 사람 키: --k --yh 가 있으면 사람 전용 분할로 발 보이는 사람마다 비율 1±0.07.
#  ③ 검수 시트: 부스 6칸 100% + 문제 덩어리 빨간 상자 표시(<out>_qa.jpg) — 납품 전 반드시 열어 본다.
# 사용: python qa_booth.py --img 결과.png --render 렌더.png --alpha 부스알파.png --people 사람마스크.png [--k 0.9 --yh 715]
import argparse, sys
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw


def load(p, mode="RGB"):
    return np.asarray(Image.open(p).convert(mode))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    for n in ("--img", "--render", "--alpha", "--people"): ap.add_argument(n, required=True)
    ap.add_argument("--k", type=float); ap.add_argument("--yh", type=float)
    ap.add_argument("--cand", help="AI 사진(사람 있는 판). 주면 '사람 보존' 검사: 생성본의 사람이 결과에서 렌더로 덮였는지")
    ap.add_argument("--plate", help="같은 AI 사진에서 사람만 지운 판. --cand 와 함께 주면 사람 위치를 판 차이로 정확히 잡는다")
    ap.add_argument("--frac", type=float, default=0.005); ap.add_argument("--blob", type=int, default=300)
    ap.add_argument("--removed", help="일부러 지운 사람 자리 마스크 — ④ 사람 덮임 검사에서 뺀다(2026-11-06 집기에 걸린 사람을 빼기로 한 경우)")
    ap.add_argument("--occluder", help="사람보다 앞에 있는 집기 마스크 — 이 안은 사람 마스크여도 렌더와 같아야 한다(⑤ 앞뒤 순서)")
    a = ap.parse_args()
    img = load(a.img).astype(np.float32); h, w = img.shape[:2]
    ren = cv2.resize(load(a.render), (w, h), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    al = cv2.resize(load(a.alpha, "L"), (w, h)) > 127
    pp = cv2.dilate((cv2.resize(load(a.people, "L"), (w, h)) > 127).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    zone = cv2.erode(al.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & ~pp
    # 전역 위치 맞춤(렌더 → 결과, 부분 아핀) — 결과가 렌더 좌표가 아닐 수도 있으니
    gi, gr = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2GRAY), cv2.cvtColor(ren.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    orb = cv2.ORB_create(8000); fm = al.astype(np.uint8) * 255
    k1, d1 = orb.detectAndCompute(gr, fm); k2, d2 = orb.detectAndCompute(gi, fm)
    ms = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d1, d2), key=lambda x: x.distance)[:2000]
    A_, _ = cv2.estimateAffinePartial2D(np.float32([k1[m.queryIdx].pt for m in ms]), np.float32([k2[m.trainIdx].pt for m in ms]), method=cv2.RANSAC)
    ren = cv2.warpAffine(ren, A_, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    # 조명(저주파) 빼고 비교
    lum = lambda X: X.mean(2)
    zf = zone.astype(np.float32)
    lb = lambda X: cv2.GaussianBlur(lum(X) * zf, (0, 0), 14) / (cv2.GaussianBlur(zf, (0, 0), 14) + 1e-3) + 6
    rr = ren * np.clip(lb(img) / lb(ren), 0.4, 1.6)[..., None]
    d = np.abs(cv2.GaussianBlur(img, (0, 0), 1.2) - cv2.GaussianBlur(rr, (0, 0), 1.2)).max(2)
    bad = ((d > 38) & zone).astype(np.uint8)
    bad = cv2.morphologyEx(bad, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(bad, np.ones((7, 7), np.uint8)))
    blobs = [list(map(int, st[j])) for j in range(1, n) if st[j][4] > a.blob]
    frac = float(bad.sum()) / max(1, zone.sum())
    fails = []
    if frac > a.frac or blobs: fails.append(f"부스무결성 frac={frac:.4f} blobs={[b[:4] for b in blobs[:8]]}")
    # ② 키
    ratios = []
    if a.k and a.yh is not None:
        from rembg import remove, new_session
        hm = (np.asarray(remove(Image.fromarray(img.astype(np.uint8)), session=new_session("u2net_human_seg"), only_mask=True)) > 100).astype(np.uint8)
        nn, ll, ss, _ = cv2.connectedComponentsWithStats(hm)
        for j in range(1, nn):
            x, y, bw, bh, ar = ss[j]
            if ar < 2500 or bh < 120: continue
            f = y + bh
            # 사람 전용 분할이 다리를 놓치면(엉덩이에서 끊김) 넘겨받은 사람 마스크로 아래를 이어 붙인다 — 0.82 오측정(2026-11-06 안쪽 남성)
            pmask = cv2.resize(load(a.people, "L"), (w, h)) > 127
            while f < h - 1 and pmask[f, x:x + bw].sum() >= max(4, 0.12 * bw): f += 1
            rows = ((ll[max(y, f - 12):f, x:x + bw] == j) | pmask[max(y, f - 12):f, x:x + bw]).sum(1)
            wmax = ((ll[y:f, x:x + bw] == j) | pmask[y:f, x:x + bw]).sum(1).max()
            if rows.mean() > 0.6 * wmax: continue
            bh = f - y
            ratios.append(round(float(bh / (a.k * (f - a.yh))), 2))
        if any(abs(r - 1) > 0.07 for r in ratios): fails.append(f"사람키 {ratios}")
    # ④ 사람 보존 — 렌더가 사람을 덮으면 ①은 '렌더와 같다'고 통과시킨다(2026-11-06 스태프 다리·안쪽 남성 다리 사라짐을 놓침).
    #   생성본 사람 자리(판 차이 ∩ 분할)에서 결과가 생성본과 다르면 실패.
    if a.cand and a.plate:
        cd = cv2.resize(load(a.cand), (w, h), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
        pl = cv2.resize(load(a.plate), (w, h), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
        pl = pl + cv2.GaussianBlur(cd - pl, (0, 0), 30)
        pd = np.abs(cv2.GaussianBlur(cd, (0, 0), 1.5) - cv2.GaussianBlur(pl, (0, 0), 1.5)).max(2) > 35
        pd = cv2.morphologyEx(pd.astype(np.uint8), cv2.MORPH_OPEN, np.ones((7, 7), np.uint8)).astype(bool) & al
        lost = pd & (np.abs(img - cd).max(2) > 45)
        if a.removed:
            lost &= ~(cv2.dilate((cv2.resize(load(a.removed, "L"), (w, h), interpolation=cv2.INTER_NEAREST) > 127).astype(np.uint8), np.ones((15, 15), np.uint8)) > 0)
        if a.occluder:   # 집기 뒤 사람이 집기에 가려진 것은 결함이 아니다(⑤가 따로 본다)
            lost &= ~(cv2.resize(load(a.occluder, "L"), (w, h), interpolation=cv2.INTER_NEAREST) > 127)
        lost = cv2.morphologyEx(lost.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        nl, ll2, sl, _ = cv2.connectedComponentsWithStats(lost)
        lb_ = [list(map(int, sl[j])) for j in range(1, nl) if sl[j][4] > 250]
        if lb_: fails.append(f"사람덮임 {[b[:4] for b in lb_[:8]]}"); blobs += lb_
    # ⑤ 앞뒤 순서 — '사람보다 앞에 있는 집기' 마스크 안은 사람 마스크여도 결과가 렌더여야 한다.
    #   (2026-11-06 "부스 잘리잖아": AI 가 카운터를 좁게 그려 남성을 카운터 옆에 세움 → 렌더 카운터가 다리 모양으로 잘림.
    #    'AI≈판' 자동 판정은 25px 만 잡았다 — 두 그림이 공간을 다르게 그린 곳이라 자동으로 못 가른다. 집기 마스크를 직접 준다.)
    if a.occluder:
        occm = cv2.resize(load(a.occluder, "L"), (w, h), interpolation=cv2.INTER_NEAREST) > 127
        # 집기 가장자리에 걸친 다리는 폭 10~40px 띠라 5px 침식·200px 문턱이면 사라진다(2026-11-06 86 "부스 잘리잖아" 놓침) → 1px·120px
        region = cv2.erode((occm & al).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        dz = np.abs(cv2.GaussianBlur(img, (0, 0), 1.2) - cv2.GaussianBlur(rr, (0, 0), 1.2)).max(2)
        wrong = cv2.morphologyEx(((dz > 38) & region).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n_w, l_w, s_w, _ = cv2.connectedComponentsWithStats(wrong)
        wb = [list(map(int, s_w[j])) for j in range(1, n_w) if s_w[j][4] > 120]
        if wb: fails.append(f"앞뒤순서(집기가 사람 모양으로 잘림) {[b[:4] for b in wb[:8]]}"); blobs += wb
    # ⑥ 흰 면 얼룩 — 렌더에서 흰 무지(블럭·벽)인 곳의 밝기가 넓은 주변 대비 12 이상 튀는 비율 ≤ 10%.
    #   (2026-11-06 "부스에 얼룩은 뭐냐": 조명 비율을 좁게 재서 그래픽 모양 얼룩이 흰 벽에 찍힘 — 얼룩 판 15%, 정상 8%)
    rh = cv2.cvtColor(ren.astype(np.uint8), cv2.COLOR_RGB2HSV)
    white = cv2.erode(((rh[..., 1] < 15) & (rh[..., 2] > 225) & zone).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    if white.sum() > 5000:
        lbw = cv2.GaussianBlur(img.mean(2), (0, 0), 8)
        refw = cv2.GaussianBlur(np.where(white, lbw, 0), (0, 0), 80) / (cv2.GaussianBlur(white.astype(np.float32), (0, 0), 80) + 1e-3)
        stain = float((np.abs(lbw - refw)[white] > 12).mean())
        if stain > 0.10: fails.append(f"흰면얼룩 {stain:.3f}")
    # ③ 검수 시트
    R = Image.fromarray(img.astype(np.uint8)); D = ImageDraw.Draw(R)
    for x, y, bw, bh, _ in blobs: D.rectangle([x - 6, y - 6, x + bw + 6, y + bh + 6], outline=(255, 0, 0), width=4)
    ys, xs = np.where(al); bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
    tw, th = (bx1 - bx0) // 3 + 1, (by1 - by0) // 2 + 1
    sh = Image.new("RGB", (tw * 3 + 20, th * 2 + 10))
    for i in range(6):
        cx, cy = bx0 + (i % 3) * tw, by0 + (i // 3) * th
        sh.paste(R.crop((cx, cy, cx + tw, cy + th)), ((i % 3) * (tw + 10), (i // 3) * (th + 10)))
    qp = Path(a.img).with_name(Path(a.img).stem + "_qa.jpg"); sh.save(qp, quality=88)
    tok = "QA_FAIL" if fails else "QA_OK"
    print(f"{tok} frac={frac:.4f} blobs={len(blobs)} heights={ratios} sheet={qp.name}" + ("" if not fails else " | " + " ; ".join(fails)))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

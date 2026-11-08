# 생성본의 사람(무리)을 원본 사진 위 '정해진 자리·정해진 크기'로 옮겨 붙인다 — 배경·디자인물은 원본 픽셀 그대로.
# 사고 배경(2026-11-06 성과보고회 포토존): 막대를 줘도 Magnific 이 커플을 판 오른쪽에 세우고 크게 그렸다 →
#   "가운데가 아니잖아 / 매번 틀려 / 막대가 아직도 크다". 자리·크기를 생성 모델에 맡기지 않고 기하로 맞춘다.
# 사용:
#   python place_people.py --base 원본.png --cand 정합된_생성본.png --mask 사람마스크.png --box x0,y0,x1,y1
#       --target-feet X,Y --target-height PX --out 결과.png [--shadow-h 60]
#   --box: 옮길 사람(무리)만 감싸는 박스. 박스 밖 사람은 버린다(예: 카메라 앞으로 튀어나온 행인)
#   --target-feet: 무리 발 중심이 갈 화면 좌표(포토존 = 판 실제 3D 중심 C_floor 바로 앞)
#   --target-height: 무리에서 가장 큰 사람의 화면 키(px). 비율로 줄이면 나머지도 같은 비율
# 성공 토큰: PLACE_OK <out> scale=… feet=(x,y) height=…
import argparse, sys
import numpy as np, cv2
from PIL import Image


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    for n in ("--base", "--cand", "--mask", "--box", "--out"): ap.add_argument(n, required=True)
    ap.add_argument("--target-feet", default=""); ap.add_argument("--target-height", type=float, default=0)
    ap.add_argument("--keep", action="store_true", help="자리·크기 그대로(이미 기준보다 작을 때) — 사람·접지 그림자만 붙인다")
    ap.add_argument("--shadow-h", type=int, default=60)
    ap.add_argument("--reflect", type=float, default=0, help="광택 바닥 반사 세기(석재 반광 0.25~0.35, 카펫·무광 0)")
    ap.add_argument("--reflect-len", type=float, default=0.35, help="반사 길이 = 키 × 이 값")
    a = ap.parse_args()
    base = np.asarray(Image.open(a.base).convert("RGB")).astype(np.float32)
    H, W = base.shape[:2]
    cand = np.asarray(Image.open(a.cand).convert("RGB").resize((W, H))).astype(np.float32)
    m = (np.asarray(Image.open(a.mask).convert("L").resize((W, H))) > 127).astype(np.uint8)
    x0, y0, x1, y1 = map(int, a.box.split(","))
    box = np.zeros_like(m); box[y0:y1, x0:x1] = 1
    m = m * box
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    keep = [i for i in range(1, n) if st[i, 4] > 400]
    if not keep:
        print("PLACE_FAIL 박스 안에 사람이 없다"); sys.exit(1)
    m = np.isin(lab, keep).astype(np.uint8)
    ys, xs = np.where(m)
    top, bot = ys.min(), ys.max()
    # 발 중심: 아래 3% 띠의 x 평균
    band = ys > bot - (bot - top) * 0.03
    fx, fy = float(xs[band].mean()), float(bot)
    # 사람별 키: 열 덩어리로 나눠 가장 큰 사람
    cols = np.where(m.any(0))[0]
    hmax = max(int(np.where(m[:, c])[0].max() - np.where(m[:, c])[0].min()) for c in cols)
    if a.keep:
        s, tx, ty = 1.0, fx, fy
    else:
        s = a.target_height / hmax
        tx, ty = map(float, a.target_feet.split(","))
    # 발 중심 기준 축소 + 이동
    A = np.array([[s, 0, tx - s * fx], [0, s, ty - s * fy]], np.float32)
    # 접지 그림자: 생성본/원본 밝기비(사람 밖, 발밑) ÷ 그 사람 주변 바닥의 밝기비(기준)
    # 2026-11-06 포토존 "사진 찍는 사람 다리 그림자 이상해": 생성본 바닥이 원래 35% 어두워(비 0.65) 그 차이까지
    #   타원째 옮겨져 발 주변에 둥근 얼룩, 블러 6px 로 밑창 접지선은 뭉개져 떠 보였다 → 주변 기준으로 나누고 블러 2px.
    blur = lambda x: cv2.GaussianBlur(x, (0, 0), 2)
    ratio = blur(cand).mean(2) / np.maximum(blur(base).mean(2), 1)
    sh1 = np.ones((H, W), np.float32)
    for i in keep:  # 사람(덩어리)마다 자기 발밑에 접지 그림자 — 무리 전체 발 하나로 잡으면 뒤 사람은 그림자가 없다(2026-11-06 로비)
        yi, xi = np.where(lab == i)
        hi = yi.max() - yi.min()
        bi = yi > yi.max() - hi * 0.03
        zi = np.zeros((H, W), np.float32)
        ctr, ax = (int(xi[bi].mean()), int(yi.max())), (int((xi[bi].max() - xi[bi].min()) * 0.65 + 20), max(a.shadow_h // 2, int(hi * 0.05)))
        cv2.ellipse(zi, ctr, ax, 0, 0, 360, 1, -1)
        ring = np.zeros((H, W), np.uint8)
        cv2.ellipse(ring, ctr, (ax[0] * 2, ax[1] * 2), 0, 0, 360, 1, -1)
        ring = (ring > 0) & (zi == 0) & (m == 0)
        ref = float(np.median(ratio[ring])) if ring.sum() > 50 else 1.0
        zi = cv2.GaussianBlur(zi * (1 - m), (0, 0), max(3, ax[1] / 4))
        rel = np.clip(ratio / max(ref, 1e-3), 0.35, 1.0)   # 어두워지기만
        sh1 = np.minimum(sh1, 1 + (rel - 1) * zi)
    sh = np.repeat(sh1[..., None], 3, 2)
    # 광택 바닥 반사: 사람을 밑창선 기준으로 뒤집어 아래로, 멀어질수록 흐리고 옅게.
    # 2026-11-06 포토존 "반사가 신발만 되냐고 끊어져 보이잖아" — 생성본 반사를 발밑 타원만큼만 옮겨 신발에서 끊겼다.
    rnum = np.zeros_like(cand); rden = np.zeros((H, W), np.float32)
    if a.reflect > 0:
        for i in keep:
            yi, xi = np.where(lab == i)
            yb, hi = int(yi.max()), int(yi.max() - yi.min())
            n = min(int(hi * a.reflect_len), yb + 1, H - 1 - yb)
            x0, x1 = xi.min(), xi.max() + 1
            comp = (lab[yb + 1 - n:yb + 1, x0:x1] == i)[::-1].astype(np.float32)
            fade = ((1 - np.arange(n) / n) ** 1.5)[:, None] * a.reflect
            al = comp * fade
            rnum[yb + 1:yb + 1 + n, x0:x1] += cand[yb + 1 - n:yb + 1, x0:x1][::-1] * al[..., None]
            rden[yb + 1:yb + 1 + n, x0:x1] += al
        rs = max(2.0, hmax * 0.006)
        rnum = cv2.GaussianBlur(rnum, (0, 0), sigmaX=rs, sigmaY=rs * 2.5)   # 반광 바닥: 세로로 더 번진다
        rden = cv2.GaussianBlur(rden, (0, 0), sigmaX=rs, sigmaY=rs * 2.5)
    rcol = cv2.warpAffine(rnum / np.maximum(rden, 1e-4)[..., None], A, (W, H), flags=cv2.INTER_LINEAR)
    ral = cv2.warpAffine(np.clip(rden, 0, 1), A, (W, H), flags=cv2.INTER_LINEAR)[..., None]
    sh_w = cv2.warpAffine(sh, A, (W, H), flags=cv2.INTER_LINEAR, borderValue=(1, 1, 1))
    ppl = cv2.warpAffine(cand, A, (W, H), flags=cv2.INTER_AREA)
    mw = cv2.warpAffine(m.astype(np.float32), A, (W, H), flags=cv2.INTER_LINEAR)
    mw = cv2.GaussianBlur(mw, (0, 0), 0.8)[..., None]
    out = base * sh_w
    out = rcol * ral + out * (1 - ral)
    out = ppl * mw + out * (1 - mw)
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(a.out)
    Image.fromarray((mw[..., 0] * 255).astype(np.uint8)).save(a.out.replace(".png", "_mask.png"))
    print(f"PLACE_OK {a.out} scale={s:.3f} feet=({tx:.0f},{ty:.0f}) height={hmax * s:.0f} from_feet=({fx:.0f},{fy:.0f}) from_height={hmax}")


if __name__ == "__main__":
    main()

# rebg(배경 교체) 후보에서 '배경은 후보, 3D 물건은 원본 렌더 픽셀'로 되돌린다 — restore_zone_a.py 의 반대 방향.
# 배경: 2026-11-05 KOBC 로비 등록데스크 — 렌더(가짜 석재 배경)를 실제 로비로 바꾸라는 요청("배경을 경로 참고해서 합성하라니").
#       GPT 는 배경과 함께 데스크 글자·로고도 다시 그려 깨뜨리므로, 물건 마스크 안은 원본 렌더 픽셀 × 후보의 저주파 밝기(조명)만 쓴다.
# 사용:
#   python restore_objects.py --src 합성본.png --cand 후보.png --obj-mask 물건알파.png --out 최종.png [--size 2560x1440]
#   --obj-mask = 물건만 렌더한 알파 PNG(또는 흰색 마스크), 합성본과 같은 카메라.
# 정합은 물건 영역의 특징점으로만 한다(배경은 통째로 바뀌므로).
# 성공 토큰: OBJ_RESTORE_OK <경로> inliers=<n> rms=<px> obj_diff=<평균차>   실패: OBJ_RESTORE_FAIL <사유> (exit 1)
import argparse, sys
from pathlib import Path
import numpy as np, cv2
from PIL import Image


def load(p, mode="RGB"):
    return np.asarray(Image.open(p).convert(mode))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True); ap.add_argument("--cand", required=True)
    ap.add_argument("--obj-mask", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--size", default="2560x1440")
    ap.add_argument("--floor-edge", type=float, default=0.012, help="물건 밑선 바로 아래 띠(높이 비율)를 그 아래 바닥으로 메운다. 0=끄기")
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        print(f"OBJ_RESTORE_FAIL 출력이 이미 있음(덮어쓰기 금지): {out}"); sys.exit(1)
    src = load(a.src); h, w = src.shape[:2]
    cand = cv2.resize(load(a.cand), (w, h), interpolation=cv2.INTER_CUBIC)
    mr = load(a.obj_mask, "RGBA")
    m = (mr[:, :, 3] if mr[:, :, 3].min() < 255 else mr[:, :, :3].max(2))
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_NEAREST) > 127

    # 1) 물건 영역 특징점으로만 후보 → 원본 정합
    fm = cv2.dilate(m.astype(np.uint8) * 255, np.ones((15, 15), np.uint8))
    g1, g2 = cv2.cvtColor(cand, cv2.COLOR_RGB2GRAY), cv2.cvtColor(src, cv2.COLOR_RGB2GRAY)
    orb = cv2.ORB_create(8000)
    k1, d1 = orb.detectAndCompute(g1, fm); k2, d2 = orb.detectAndCompute(g2, fm)
    if d1 is None or d2 is None:
        print("OBJ_RESTORE_FAIL 특징점 없음"); sys.exit(1)
    ms = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d1, d2), key=lambda x: x.distance)[:2000]
    if len(ms) < 50:
        print(f"OBJ_RESTORE_FAIL 정합 특징점 부족({len(ms)})"); sys.exit(1)
    p1 = np.float32([k1[x.queryIdx].pt for x in ms]); p2 = np.float32([k2[x.trainIdx].pt for x in ms])
    # 회전·확대·이동만(부분 아핀). 호모그래피는 물건 특징점만으로 풀면 배경을 원근 왜곡해 세로선이 1~2° 기운다
    # (2026-11-05 반려 "좌측 문이 기운 거 같은데" — GPT 원본은 0°, 복원 후 −1.9°/+1.2°, 실행마다 RANSAC 로 달라짐).
    A, inl = cv2.estimateAffinePartial2D(p1, p2, method=cv2.RANSAC, ransacReprojThreshold=3.0); inl = inl.ravel().astype(bool)
    rms = float(np.sqrt(np.mean(np.sum((cv2.transform(p1[inl][None], A)[0] - p2[inl]) ** 2, 1))))
    warped = cv2.warpAffine(cand, A, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # 2) 물건 안 = 원본 × 후보 저주파 밝기 비(조명만 옮김, 0.75~1.15 로 제한), 경계 2px 페더
    sf, wf = src.astype(np.float32), warped.astype(np.float32)
    mi = m.astype(np.float32)
    ls = cv2.GaussianBlur(sf.mean(2) * mi, (0, 0), 35) / (cv2.GaussianBlur(mi, (0, 0), 35) + 1e-3) + 8
    lc = cv2.GaussianBlur(wf.mean(2) * mi, (0, 0), 35) / (cv2.GaussianBlur(mi, (0, 0), 35) + 1e-3) + 8
    ratio = np.clip(lc / ls, 0.75, 1.15)[..., None]
    obj = np.clip(sf * ratio, 0, 255)
    alpha = cv2.GaussianBlur(cv2.erode(mi, np.ones((3, 3), np.uint8)), (0, 0), 1.0)[..., None]
    # 3) 밑선 겹침 제거 — 2026-11-06 Kofpi 부스 "하단에 겹치는 저거 뭐냐": GPT 가 배경을 바꾸며 물건 밑에 자기 몰딩·바닥판 모서리를
    #    조금 아래에 다시 그려, 원본 밑선(흰 바닥판 옆면) 아래로 GPT 몰딩이 한 겹 더 보였다. 물건 밑선 바로 아래 띠(높이 1.2%)를
    #    그보다 아래 바닥(반사 포함)을 위로 끌어와 메우고, 밑선에 얇은 접촉 그림자를 넣는다(띠만 지우면 물건이 뜬다).
    bg = wf
    N = int(round(h * a.floor_edge))
    if N > 0:
        mu = m.astype(np.uint8)
        # 세로줄마다 '가장 아래 밑선'(바닥에 닿는 선)에만 — 공중 보·간판 아랫면에도 하면 위쪽 픽셀을 끌어와 판이 하나 더 생긴다(같은 날 실측)
        has = m.any(0); last = (h - 1 - np.argmax(m[::-1], axis=0)).astype(np.int32)
        yy = np.arange(h)[:, None]
        band = has[None, :] & (yy > last[None, :]) & (yy <= last[None, :] + 2 * N)   # 몰딩 + 그 반사 줄
        edge = has[None, :] & (yy > last[None, :]) & (yy <= last[None, :] + 3)
        src_floor = np.roll(wf, -(2 * N + 3), axis=0)   # 몰딩의 바닥 반사 줄까지 건너뛴다
        bf = cv2.GaussianBlur(band.astype(np.float32), (0, 0), 1.2)[..., None]
        bg = src_floor * bf + wf * (1 - bf)
        sh = cv2.GaussianBlur(edge.astype(np.float32), (0, 0), 1.5) * 0.35
        bg = bg * (1 - sh)[..., None]
    res = obj * alpha + bg * (1 - alpha)
    W, Hh = map(int, a.size.lower().split("x"))
    res = cv2.resize(res.astype(np.uint8), (W, Hh), interpolation=cv2.INTER_CUBIC if W > w else cv2.INTER_AREA)
    Image.fromarray(res).save(out)
    ov = (0.5 * src + 0.5 * cv2.resize(res, (w, h))).astype(np.uint8)
    Image.fromarray(ov).save(out.with_name(out.stem + "_overlay50.png"))
    od = float(np.abs(cv2.resize(res, (w, h)).astype(int) - src.astype(int)).mean(2)[cv2.erode(m.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0].mean())
    print(f"OBJ_RESTORE_OK {out} inliers={int(inl.sum())} rms={rms:.2f} obj_diff={od:.1f} ratio={float(ratio.min()):.2f}..{float(ratio.max()):.2f}")


if __name__ == "__main__":
    main()

# GPT 한 장 사진(최종 바탕) 위에 디자인 면(앞판·백월 등)의 글자·로고만 '면별 호모그래피'로 정확히 얹는다.
# 배경: 2026-11-05 KOBC 로비 등록데스크 — 사람만 떼어 3D 렌더 데스크 위에 붙이면 "합성티 팍팍, 사진 같지 않어"(3회 반려).
#       원인은 사람이 아니라 렌더 픽셀 그대로인 데스크·배경(인쇄 질감 없음·칼날 모서리). 그래서 GPT 가 찍은 장면을 최종 바탕으로 두고
#       글자만 되돌린다. GPT 는 카운터 상판을 30~50px 낮게 그리는 등 면마다 다르게 움직이므로 전체 호모그래피 하나로는 안 맞는다 → 면별로 맞춘다.
# 사용:
#   python restore_faces.py --src 원본(렌더 합성).png --cand GPT후보.png --face 앞판마스크.png --face 백월마스크.png \
#       [--people 후보좌표_사람마스크.png] --out 최종.png [--size 2560x1440]
#   --face = 원본(src) 좌표의 면 마스크(흰색). --people = 후보(출력) 좌표의 사람 마스크 — 면 앞에 선 사람은 후보 픽셀을 지킨다.
# 성공 토큰: FACES_OK <경로> face1=inliers/rms ...   (면 하나라도 rms > 2px 면 FACES_FAIL, exit 1)
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
    ap.add_argument("--face", action="append", required=True); ap.add_argument("--people")
    ap.add_argument("--out", required=True); ap.add_argument("--size", default="2560x1440")
    a = ap.parse_args()
    W, H = map(int, a.size.lower().split("x"))
    src = cv2.resize(load(a.src), (W, H), interpolation=cv2.INTER_AREA)
    cand = cv2.resize(load(a.cand), (W, H), interpolation=cv2.INTER_LANCZOS4)
    people = (cv2.resize(load(a.people, "L"), (W, H)) > 127) if a.people else np.zeros((H, W), bool)
    out = cand.astype(np.float32)
    g_s, g_c = cv2.cvtColor(src, cv2.COLOR_RGB2GRAY), cv2.cvtColor(cand, cv2.COLOR_RGB2GRAY)
    orb = cv2.ORB_create(12000); rep = []; bad = False
    for fp in a.face:
        fm = cv2.resize(load(fp, "L"), (W, H), interpolation=cv2.INTER_NEAREST) > 127
        k1, d1 = orb.detectAndCompute(g_s, cv2.erode(fm.astype(np.uint8) * 255, np.ones((7, 7), np.uint8)))
        k2, d2 = orb.detectAndCompute(g_c, cv2.dilate(fm.astype(np.uint8) * 255, np.ones((121, 121), np.uint8)))
        ms = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d1, d2), key=lambda x: x.distance)[:2500]
        if len(ms) < 40:
            rep.append(f"{Path(fp).name}=matches{len(ms)}"); bad = True; continue
        p1 = np.float32([k1[m.queryIdx].pt for m in ms]); p2 = np.float32([k2[m.trainIdx].pt for m in ms])
        Hm, inl = cv2.findHomography(p1, p2, cv2.RANSAC, 2.5); inl = inl.ravel().astype(bool)
        rms = float(np.sqrt(np.mean(np.sum((cv2.perspectiveTransform(p1[inl][None], Hm)[0] - p2[inl]) ** 2, 1))))
        rep.append(f"{Path(fp).name}={int(inl.sum())}/{rms:.2f}")
        if rms > 2.0: bad = True
        sw = cv2.warpPerspective(src, Hm, (W, H), flags=cv2.INTER_CUBIC).astype(np.float32)
        mw = cv2.warpPerspective(fm.astype(np.float32), Hm, (W, H), flags=cv2.INTER_LINEAR)
        mw = cv2.erode((mw > 0.5).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)  # 면 가장자리 2px 안쪽만(모서리는 GPT 재질)
        mw[people] = 0
        # 원본 글자 × 후보의 저주파 밝기(빛 번짐·인쇄 재질 명암) — 면 안에서만 평균
        ls = cv2.GaussianBlur(sw.mean(2) * mw, (0, 0), 25) / (cv2.GaussianBlur(mw, (0, 0), 25) + 1e-3) + 6
        lc = cv2.GaussianBlur(out.mean(2) * mw, (0, 0), 25) / (cv2.GaussianBlur(mw, (0, 0), 25) + 1e-3) + 6
        obj = sw * np.clip(lc / ls, 0.7, 1.2)[..., None]
        # 후보의 미세 질감(인쇄면 결·노이즈)을 살짝 되살린다
        hp = out - cv2.GaussianBlur(out, (0, 0), 1.5)
        obj = obj + 0.6 * hp
        al = cv2.GaussianBlur(mw, (0, 0), 1.2)[..., None]
        out = obj * al + out * (1 - al)
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(a.out)
    print(("FACES_FAIL " if bad else "FACES_OK ") + f"{a.out} " + " ".join(rep))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

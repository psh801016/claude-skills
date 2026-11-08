# 형태를 잠근 3D 물건(데스크·백월)에 '사진으로 찍힌 질감'만 입힌다 — 형태·위치·글자 픽셀 배치는 그대로.
# 배경: 2026-11-05 KOBC 로비 등록데스크 — "합성티 너무 나, 사진처럼 안 되냐" + "형태를 바꾸면 어떡해".
#       GPT 데스크를 쓰면 사진 같지만 형태가 바뀌고(상판 50px 낮아짐), 렌더 데스크를 쓰면 형태는 맞지만 CG 티가 난다.
#       렌더 데스크의 CG 티 = ① 빛 명암 없음 ② 접지 그림자 없음(떠 보임) ③ 칼날 모서리 ④ 노이즈 없음.
#       → GPT 사진의 저주파 빛 명암만 면별 호모그래피로 옮기고, 접지 AO·모서리 0.7px·화면 전체 같은 그레인·비네팅을 더한다.
# 사용:
#   python photo_finish_objects.py --img 합성본.png --obj-mask 물건알파.png --gpt GPT후보.png --face 앞판.png --face 백월.png \
#       [--gpt-people GPT좌표_사람마스크.png] [--keep 사람마스크.png] --out 최종.png
#   --keep = 마감에서 제외할 영역(이미 사진인 사람 등, 그레인만 공통). 결과 크기 = --img 크기.
# 성공 토큰: OBJ_PHOTO_OK <경로> faces=<inliers/rms ...> shape_diff=<물건 외곽 IoU>
import argparse, sys
from pathlib import Path
import numpy as np, cv2
from PIL import Image


def load(p, mode="RGB"):
    return np.asarray(Image.open(p).convert(mode))


def masked_blur(x, m, s):
    return cv2.GaussianBlur(x * m, (0, 0), s) / (cv2.GaussianBlur(m, (0, 0), s) + 1e-4)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", required=True); ap.add_argument("--obj-mask", required=True); ap.add_argument("--gpt", required=True)
    ap.add_argument("--face", action="append", required=True); ap.add_argument("--gpt-people"); ap.add_argument("--keep")
    ap.add_argument("--out", required=True); ap.add_argument("--grain", type=float, default=2.2)
    a = ap.parse_args()
    img = load(a.img).astype(np.float32); H, W = img.shape[:2]
    om = load(a.obj_mask, "RGBA"); obj = cv2.resize(om[:, :, 3] if om[:, :, 3].min() < 255 else om[:, :, :3].max(2), (W, H)) > 127
    gpt = cv2.resize(load(a.gpt), (W, H), interpolation=cv2.INTER_LANCZOS4)
    gp = (cv2.resize(load(a.gpt_people, "L"), (W, H)) > 127) if a.gpt_people else np.zeros((H, W), bool)
    keep = (cv2.resize(load(a.keep, "L"), (W, H)) > 127) if a.keep else np.zeros((H, W), bool)
    g_i, g_g = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2GRAY), cv2.cvtColor(gpt, cv2.COLOR_RGB2GRAY)
    orb = cv2.ORB_create(12000); rep = []
    out = img.copy()
    # ① 면별 빛 명암: GPT 면을 원본 형태로 되돌려 놓고, 저주파 밝기 비만 곱한다
    for fp in a.face:
        fm = cv2.resize(load(fp, "L"), (W, H), interpolation=cv2.INTER_NEAREST) > 127
        k1, d1 = orb.detectAndCompute(g_i, cv2.erode(fm.astype(np.uint8) * 255, np.ones((7, 7), np.uint8)))
        k2, d2 = orb.detectAndCompute(g_g, cv2.dilate(fm.astype(np.uint8) * 255, np.ones((121, 121), np.uint8)))
        ms = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d1, d2), key=lambda x: x.distance)[:2500]
        p1 = np.float32([k1[m.queryIdx].pt for m in ms]); p2 = np.float32([k2[m.trainIdx].pt for m in ms])
        Hm, inl = cv2.findHomography(p2, p1, cv2.RANSAC, 2.5); inl = inl.ravel().astype(bool)   # GPT → 원본 형태
        rms = float(np.sqrt(np.mean(np.sum((cv2.perspectiveTransform(p2[inl][None], Hm)[0] - p1[inl]) ** 2, 1))))
        rep.append(f"{Path(fp).name}={int(inl.sum())}/{rms:.2f}")
        gw = cv2.warpPerspective(gpt, Hm, (W, H), flags=cv2.INTER_LINEAR).astype(np.float32)
        valid = cv2.warpPerspective((~gp).astype(np.float32), Hm, (W, H)) > 0.5   # GPT 쪽 사람이 가린 곳은 빼고 평균
        m = (fm & valid & ~keep).astype(np.float32)
        lg = masked_blur(gw.mean(2), m, 30); li = masked_blur(out.mean(2), m, 30)
        ratio = np.clip((lg + 6) / (li + 6), 0.72, 1.12)
        fmf = cv2.GaussianBlur(fm.astype(np.float32), (0, 0), 1.0) * (~keep)
        out = out * (1 + (ratio[..., None] - 1) * fmf[..., None])
    # ② 접지 AO: 물건 아래 외곽선 바로 밑 바닥을 어둡게(진한 접점 + 부드러운 꼬리)
    below = np.zeros((H, W), np.float32)
    cols = np.where(obj.any(0))[0]
    for x in cols:
        y = np.where(obj[:, x])[0].max()
        if y < H - 2: below[y + 1:min(H, y + 4), x] = 1.0
    ao = np.maximum(cv2.GaussianBlur(below, (0, 0), 2.0) * 0.55, cv2.GaussianBlur(cv2.dilate(below, np.ones((15, 3), np.uint8)), (0, 0), 14) * 0.30)
    ao *= (~obj) * (~keep)
    out *= (1 - np.clip(ao, 0, 0.5))[..., None]
    # ③ 모서리: 물건 외곽 띠만 0.7px 흐림(렌더 칼날 모서리 제거)
    edge = cv2.morphologyEx(obj.astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)).astype(bool) & ~keep
    soft = cv2.GaussianBlur(out, (0, 0), 0.7)
    out[edge] = soft[edge]
    # ④ 물건 면 미세 흐림 0.45px(사진 렌즈 해상) + 화면 전체 같은 단색 그레인 + 약한 비네팅
    objm = (obj & ~keep)[..., None].astype(np.float32)
    out = cv2.GaussianBlur(out, (0, 0), 0.45) * objm + out * (1 - objm)
    rng = np.random.default_rng(7)
    out += rng.normal(0, a.grain, (H, W)).astype(np.float32)[..., None]
    yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    out *= (1 - 0.07 * np.clip(r - 0.55, 0, None) ** 1.5)[..., None]
    res = np.clip(out, 0, 255).astype(np.uint8)
    Image.fromarray(res).save(a.out)
    print(f"OBJ_PHOTO_OK {a.out} faces={' '.join(rep)} size={W}x{H}")


if __name__ == "__main__":
    main()

# 바닥 교체 — GPT 가 그린 바닥(지렁이 같은 AI 무늬)을 실제 현장 사진의 카펫으로 바꾼다. 빛·그림자(큰 명암)는 지금 이미지에서 옮긴다.
# 배경: 2026-11-05 KOBC 로비 포토존 — "바닥에 GPT 특유의 패턴 생겨", "바닥 패턴 왜 바뀌어"(군데군데 사각형으로 GPT 바닥이 남음).
#       함정 3개: ① 바닥 마스크를 색으로 잡으면 꽃·테이블이 바닥으로 덮인다 → '벽 밑선 아래 − 물건 마스크' 로 만든다
#       ② 카펫 사진에 벽·콘솔이 들어 있으면 같이 깔린다 → --carpet-rect 로 카펫만 있는 영역을 고른다
#       ③ 물건 자리를 사각형으로 빼면 그 안에 GPT 바닥이 남아 짜깁기처럼 보인다 → 물건 마스크는 분할 윤곽(BiRefNet 등)
# 사용:
#   python replace_floor.py --img 이미지.png --carpet 현장사진.jpg --carpet-rect x0,y0,x1,y1 \
#       --wall-line x0,y0,x1,y1 --keep 물건1.png [--keep 물건2.png ...] --out 결과.png
#   --wall-line = 이미지에서 벽과 바닥이 만나는 직선 두 점(이 아래가 바닥). --keep = 바닥이 아닌 것(흰색) — 테이블·꽃·포토월·사람.
# 성공 토큰: FLOOR_OK <경로> floor_px=<n>
import argparse, sys
import numpy as np, cv2
from PIL import Image


def load(p, mode="RGB"):
    return np.asarray(Image.open(p).convert(mode))


def floor_mask(h, w, wall_line, keep):
    x0, y0, x1, y1 = wall_line
    yy, xx = np.mgrid[0:h, 0:w]
    yl = y0 + (xx - x0) * (y1 - y0) / max(1e-6, (x1 - x0))
    m = yy > yl + 4
    if keep is not None:
        m &= ~(cv2.dilate(keep.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0)
    return m, yl


def replace(img, carpet, rect, wall_line, keep):
    h, w = img.shape[:2]
    fl, yl = floor_mask(h, w, wall_line, keep)
    cx0, cy0, cx1, cy1 = rect
    srcq = np.float32([[cx0, cy0], [cx1, cy0], [cx1, cy1], [cx0, cy1]])
    dstq = np.float32([[0, yl[0, 0] - 15], [w, yl[0, -1] - 15], [w, h], [0, h]])
    tex = cv2.warpPerspective(carpet.astype(np.float32), cv2.getPerspectiveTransform(srcq, dstq), (w, h), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REFLECT)
    tl = cv2.GaussianBlur(tex.mean(2), (0, 0), 40); tex = tex / (tl[..., None] + 1) * tl.mean()   # 카펫 사진 자체의 큰 얼룩 제거
    imf = img.astype(np.float32)
    for c in range(3):
        t, g = tex[..., c][fl], imf[..., c][fl]
        tex[..., c] = (tex[..., c] - t.mean()) / (t.std() + 1e-3) * g.std() * 0.8 + g.mean()
    fm = fl.astype(np.float32)
    mb = lambda x, s: cv2.GaussianBlur(x * fm, (0, 0), s) / (cv2.GaussianBlur(fm, (0, 0), s) + 1e-4)
    tex = tex * np.clip((mb(imf.mean(2), 30) + 4) / (mb(tex.mean(2), 30) + 4), 0.6, 1.3)[..., None]   # 지금 이미지의 빛·그림자
    # 물건 밑 접지 AO(벽 밑선은 제외)
    nf = (~fl).astype(np.uint8); edge = (cv2.dilate(nf, np.ones((3, 3), np.uint8)) > 0) & fl
    ys, xs = np.where(edge); keep_e = (nf[np.clip(ys - 3, 0, h - 1), xs] > 0) & (ys > yl[ys, xs] + 12)
    seed = np.zeros((h, w), np.float32); seed[ys[keep_e], xs[keep_e]] = 1
    ao = np.clip(np.maximum(cv2.GaussianBlur(seed, (0, 0), 2.5) * 1.2, cv2.GaussianBlur(cv2.dilate(seed, np.ones((9, 3), np.uint8)), (0, 0), 12) * 0.5), 0, 0.45) * fm
    tex *= (1 - ao)[..., None]
    al = cv2.GaussianBlur(cv2.erode(fl.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 1.5)[..., None]
    return np.clip(tex * al + imf * (1 - al), 0, 255).astype(np.uint8), fl


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", required=True); ap.add_argument("--carpet", required=True)
    ap.add_argument("--carpet-rect", required=True); ap.add_argument("--wall-line", required=True)
    ap.add_argument("--keep", action="append", default=[]); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    img = load(a.img); h, w = img.shape[:2]
    keep = np.zeros((h, w), bool)
    for k in a.keep:
        keep |= cv2.resize(load(k, "L"), (w, h), interpolation=cv2.INTER_NEAREST) > 127
    out, fl = replace(img, load(a.carpet), [int(v) for v in a.carpet_rect.split(",")], [float(v) for v in a.wall_line.split(",")], keep)
    Image.fromarray(out).save(a.out)
    print(f"FLOOR_OK {a.out} floor_px={int(fl.sum())}")


if __name__ == "__main__":
    main()

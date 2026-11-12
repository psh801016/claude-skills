# 전시홀 밑그림 — 부스 렌더(알파) 카메라의 두 소실점으로 천장 트러스 격자·펜던트 조명 점·바닥 줄눈을 투영한다.
# 사고 배경(2026-11-11 Kofpi 히어로 컷): AI 가 홀 천장을 화면 안 한 점으로 모이는 다른 투시로 그렸다 —
#   "천장에 소실점 각도와 부스 소실점 안 맞는다고 / 전체 공간 소실점이 기본 아니냐". space_underlay.py 는 방(벽돌벽)용이라 열린 홀에 안 맞았다.
#   이 밑그림을 GPT 2.6 에 GEOMETRY LOCK 으로 넣으니 check_vp median 0.15°(VP_OK).
# 사용: python hall_underlay.py --render 부스.png(RGBA) --vp-left X,Y --vp-right X,Y --f 2502 --anchor X,YBOT --hc 1.44 --out 밑그림.png
#   --vp-* / --f / --hc 는 space_underlay.py 출력(UNDERLAY_OK f=… hc=…) 또는 check_vp 의 obj_vp 를 쓴다. --anchor = 부스 앞 모서리 바닥점.
#   [--ceil 10 --truss 6 --lights 3 --floor-grid 4] (m)
# 성공 토큰: HALL_UNDERLAY_OK <경로> cx=<주점 x>
import argparse, sys
import numpy as np, cv2
from PIL import Image


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    for n in ("--render", "--vp-left", "--vp-right", "--anchor", "--out"):
        ap.add_argument(n, required=True)
    ap.add_argument("--f", type=float, required=True); ap.add_argument("--hc", type=float, default=1.5)
    ap.add_argument("--ceil", type=float, default=12.0); ap.add_argument("--truss", type=float, default=9.0)  # 2026-11-11 "천장은 어설프다": 3m 촘촘 조명 → 6m 듬성
    ap.add_argument("--lights", type=float, default=6.0); ap.add_argument("--floor-grid", type=float, default=4.0)
    a = ap.parse_args()
    rgba = Image.open(a.render).convert("RGBA"); W, H = rgba.size
    vL = np.array(list(map(float, a.vp_left.split(",")))); vR = np.array(list(map(float, a.vp_right.split(","))))
    cy = (vL[1] + vR[1]) / 2; f = a.f
    # 두 수평 소실점이 직교: (vL-p)·(vR-p) = -f² → 주점 x (화면 가운데에 가까운 해)
    b = -(vL[0] + vR[0]); c = vL[0] * vR[0] + f * f; d = b * b - 4 * c
    if d < 0:
        print("HALL_UNDERLAY_FAIL 소실점·f 가 직교 조건을 못 맞춘다(f 확인)"); sys.exit(1)
    cx = min(((-b + np.sqrt(d)) / 2, (-b - np.sqrt(d)) / 2), key=lambda x: abs(x - W / 2))
    dL = np.array([vL[0] - cx, 0, f]); dL /= np.linalg.norm(dL)
    dR = np.array([vR[0] - cx, 0, f]); dR /= np.linalg.norm(dR)
    ax, ay = map(float, a.anchor.split(","))
    O = np.array([(ax - cx) / f, (ay - cy) / f, 1.0]) * (f * a.hc / (ay - cy))   # 앞 모서리 바닥점(카메라 좌표, y 아래)

    img = np.zeros((H, W, 3), np.uint8); img[:int(cy)] = (35, 35, 40); img[int(cy):] = (55, 55, 58)

    def proj(P):
        P = np.atleast_2d(P); ok = P[:, 2] > 0.3
        return np.c_[cx + f * P[:, 0] / np.where(ok, P[:, 2], 1), cy + f * P[:, 1] / np.where(ok, P[:, 2], 1)], ok

    def seg(A, B, col, th):
        P = A[None] + (B - A)[None] * np.linspace(0, 1, 400)[:, None]; uv, ok = proj(P)
        pts = uv[ok].astype(np.int32)
        if len(pts) > 1:
            cv2.polylines(img, [pts], False, col, th, cv2.LINE_AA)

    R = 60.0
    ceil = O + np.array([0, -a.ceil, 0])
    for k in np.arange(-R, R + 1, a.truss):
        seg(ceil + dL * k - dR * R, ceil + dL * k + dR * R, (150, 150, 155), 5)
        seg(ceil + dR * k - dL * R, ceil + dR * k + dL * R, (150, 150, 155), 5)
    for i in np.arange(-R, R + 1, a.lights):
        for j in np.arange(-R, R + 1, a.lights):
            P = ceil + np.array([0, 1.2, 0]) + dL * i + dR * j; uv, ok = proj(P)
            if ok[0] and 0 <= uv[0, 0] < W and 0 <= uv[0, 1] < cy:
                cv2.circle(img, tuple(uv[0].astype(int)), max(2, int(260 / np.linalg.norm(P))), (255, 250, 225), -1, cv2.LINE_AA)
    for k in np.arange(-R, R + 1, a.floor_grid):
        seg(O + dL * k - dR * R, O + dL * k + dR * R, (95, 95, 100), 2)
        seg(O + dR * k - dL * R, O + dR * k + dL * R, (95, 95, 100), 2)
    out = Image.fromarray(img); out.paste(rgba, mask=rgba.split()[3]); out.save(a.out)
    print(f"HALL_UNDERLAY_OK {a.out} cx={cx:.1f}")


if __name__ == "__main__":
    main()

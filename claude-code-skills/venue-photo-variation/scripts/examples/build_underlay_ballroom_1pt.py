# 연회장 1점 투시 밑그림 — 정면 무대 렌더(알파) 카메라의 소실점 하나로 천장 레일·다운라이트·트러스·벽 필라스터를 투영한다.
# 사고 배경(2026-11-11 HUF 2026 연회장 재작업): 무대 구조·카메라가 바뀐 렌더를 기존 완성본처럼 실사화.
#   정면 무대는 깊이 소실점이 하나(가로선은 화면과 평행)라 hall_underlay.py(2점)를 못 쓴다. 점검표 14·15 — 공간을 AI 에 맡기지 않는다.
# 소실점은 테이블 열(같은 열 테이블 중심을 이은 선) 2쌍 이상의 교점으로 잰다(그래픽 직선 RANSAC 은 화면 글자에 끌려 틀렸다).
# 사용: python build_underlay_ballroom_1pt.py --render 렌더.png(RGBA) --vp X,Y --f 2500 --hc 4.3 --out 밑그림.png
#   [--back 30 --half 13 --ceil 7.5 --truss 6.3]  (m, 카메라 기준: 뒷벽 깊이, 벽 반폭, 천고, 트러스 높이)
# 성공 토큰: UNDERLAY_1PT_OK <경로>
import argparse, sys
import numpy as np, cv2
from PIL import Image


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", required=True); ap.add_argument("--vp", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--f", type=float, default=2500); ap.add_argument("--hc", type=float, default=4.3)
    ap.add_argument("--back", type=float, default=30); ap.add_argument("--half", type=float, default=13)
    ap.add_argument("--ceil", type=float, default=7.5); ap.add_argument("--truss", type=float, default=6.3)
    a = ap.parse_args()
    rgba = Image.open(a.render).convert("RGBA"); W, H = rgba.size
    cx, cy = map(float, a.vp.split(",")); f, hc = a.f, a.hc
    img = np.zeros((H, W, 3), np.uint8); img[:] = (28, 30, 38)

    def P(X, Yup, Z):  # 월드(X 오른쪽, Yup 바닥 기준 높이, Z 깊이) → 화면
        return np.array([cx + f * X / Z, cy - f * (Yup - hc) / Z])

    def seg(A, B, col, th, n=200):
        pts = np.array([P(*(np.array(A) + (np.array(B) - np.array(A)) * t)) for t in np.linspace(0, 1, n)])
        cv2.polylines(img, [pts.astype(np.int32)], False, col, th, cv2.LINE_AA)

    def quad(pts3, col):
        cv2.fillPoly(img, [np.array([P(*p) for p in pts3]).astype(np.int32)], col, cv2.LINE_AA)

    Z0, Zb, hw, C = 3.0, a.back, a.half, a.ceil
    quad([(-hw, 0, Z0), (-hw, 0, Zb), (hw, 0, Zb), (hw, 0, Z0)], (40, 52, 110))          # 카펫
    quad([(-hw, 0, Zb), (hw, 0, Zb), (hw, C, Zb), (-hw, C, Zb)], (52, 38, 30))           # 뒷벽(어두운 목재)
    for s in (-1, 1):
        quad([(s * hw, 0, Z0), (s * hw, 0, Zb), (s * hw, C, Zb), (s * hw, C, Z0)], (46, 34, 27))  # 옆벽
    quad([(-hw, C, Z0), (-hw, C, Zb), (hw, C, Zb), (hw, C, Z0)], (18, 18, 22))            # 천장
    for s in (-1, 1):                                                                       # 벽 모서리선(깊이)
        seg((s * hw, 0, Z0), (s * hw, 0, Zb), (90, 80, 70), 3); seg((s * hw, C, Z0), (s * hw, C, Zb), (90, 80, 70), 3)
        for z in np.arange(Z0 + 1.5, Zb, 3.0):                                              # 옆벽 필라스터(세로 빛줄)
            seg((s * hw, 0.2, z), (s * hw, C - 0.4, z), (215, 175, 120), 4, 20)
    for x in np.arange(-hw + 1.6, hw - 1.5, 3.2):                                          # 뒷벽 필라스터
        seg((x, 0.2, Zb), (x, C - 0.4, Zb), (215, 175, 120), 3, 20)
    for x in np.arange(-hw + 2, hw - 1, 2.2):                                              # 천장 세로 레일(깊이선) + 다운라이트
        seg((x, C, Z0), (x, C, Zb), (70, 70, 78), 6)
        for z in np.arange(Z0 + 1.0, Zb, 2.4):
            u = P(x + 1.1, C, z)
            if 0 <= u[0] < W and 0 <= u[1] < H:
                cv2.circle(img, tuple(u.astype(int)), max(3, int(90 / z)), (255, 245, 220), -1, cv2.LINE_AA)
    for z in (Zb - 15, Zb - 9, Zb - 3):                                                    # 가로 트러스 + 무빙라이트(뒷벽 앞 3·9·15m)
        seg((-hw, a.truss, z), (hw, a.truss, z), (120, 120, 128), max(3, int(150 / z)))
        for x in np.arange(-hw + 1.5, hw - 1, 2.6):
            u = P(x, a.truss - 0.35, z)
            if 0 <= u[0] < W and 0 <= u[1] < H:
                cv2.circle(img, tuple(u.astype(int)), max(4, int(180 / z)), (140, 190, 255), -1, cv2.LINE_AA)
    out = Image.fromarray(img); out.paste(rgba, mask=rgba.split()[3]); out.save(a.out)
    print(f"UNDERLAY_1PT_OK {a.out}")


if __name__ == "__main__":
    main()

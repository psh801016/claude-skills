# 얼굴 합성 티 제거: 빛·색은 다시 조명한 판(GPT/Gemini), 이목구비 디테일은 원본, GPT 피부 지렁이 무늬는 코어링으로 제거.
# 배경: 2026-11-12 내 얼굴 실사 — 원본 얼굴 픽셀 통째 복원은 원래 조명이 남아 합성 티,
#   GPT 판 피부 결은 지렁이 무늬(σ5 땐 남고 σ12 에서 사라짐), 원본 자체의 무늬는 중간 대역 코어링 t=3 으로 제거(t=5 는 플라스틱).
# 사용: python face_relight_fuse.py 원본.png 다시조명판.png 출력.png --ellipse cx,cy,rx,ry [--sigma 12] [--core 3]
#   ellipse 는 원본 좌표(이마~턱·귀 포함). 다시조명판 해상도로 자동 배율, 템플릿 매칭으로 위치 보정.
import argparse, cv2, numpy as np


def fuse(a, h, ell, sigma=12, core=3):
    k = h.shape[1] / a.shape[1]
    a = cv2.resize(a, (h.shape[1], h.shape[0]), interpolation=cv2.INTER_LANCZOS4)
    cx, cy, rx, ry = [v * k for v in ell]
    x0, y0, x1, y1 = int(cx - rx * .85), int(cy - ry * .8), int(cx + rx * .85), int(cy + ry * .9)
    r = cv2.matchTemplate(h, a[y0:y1, x0:x1], cv2.TM_CCOEFF_NORMED); _, sc, _, loc = cv2.minMaxLoc(r)
    dx, dy = loc[0] - x0, loc[1] - y0
    a = cv2.warpAffine(a, np.float32([[1, 0, dx], [0, 1, dy]]), (a.shape[1], a.shape[0]), borderMode=cv2.BORDER_REFLECT)
    la = cv2.cvtColor(a, cv2.COLOR_BGR2LAB).astype(np.float32)
    lh = cv2.cvtColor(h, cv2.COLOR_BGR2LAB).astype(np.float32)
    s = sigma * k
    L = cv2.GaussianBlur(lh[..., 0], (0, 0), s) + (la[..., 0] - cv2.GaussianBlur(la[..., 0], (0, 0), s))
    if core > 0:                                              # 중간 대역의 약한 결(지렁이 무늬)만 깎음
        band = cv2.GaussianBlur(L, (0, 0), 0.8 * k) - cv2.GaussianBlur(L, (0, 0), 4 * k)
        L = L + (np.sign(band) * np.maximum(np.abs(band) - core, 0) - band)
    m = np.zeros(a.shape[:2], np.float32)
    cv2.ellipse(m, (int(cx) + dx, int(cy) + dy), (int(rx), int(ry)), 0, 0, 360, 1, -1)
    m = cv2.GaussianBlur(m, (0, 0), 10 * k)
    o = lh.copy(); o[..., 0] = L * m + lh[..., 0] * (1 - m)
    return cv2.cvtColor(np.clip(o, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR), sc


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("relit"); ap.add_argument("out")
    ap.add_argument("--ellipse", required=True, help="cx,cy,rx,ry (원본 좌표)")
    ap.add_argument("--sigma", type=float, default=12); ap.add_argument("--core", type=float, default=3)
    p = ap.parse_args()
    o, sc = fuse(cv2.imread(p.src), cv2.imread(p.relit), [float(v) for v in p.ellipse.split(",")], p.sigma, p.core)
    cv2.imwrite(p.out, o)
    print("FACE_FUSE_OK", p.out, "match", round(sc, 3))

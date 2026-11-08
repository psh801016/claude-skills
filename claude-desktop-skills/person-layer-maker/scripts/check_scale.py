# 3단계 2번 — 생성 후보의 사람 키를 원근 기준(k·y_horizon, 1.7m)과 비교해 통과/반려를 낸다.
# 배경: 2026-11-06 Kofpi "사람 너무 커, 750 한 칸이라니까 키가 거의 2미터". Magnific 은 막대를 무시하고 10~15% 크게 그린다 → 후보마다 재서 고른다.
# 사용: python check_scale.py --img 후보.png --k 0.899 --yh 715.2 [--tol 0.05] [--canvas 2560x1440]
#   사람 분할(u2net_human_seg)로 발이 보이는 사람만 잰다(아랫단이 몸통처럼 넓으면 '가려짐'으로 제외).
# 출력: 사람별 비율, 마지막 줄 SCALE_OK mean=.. max=.. / SCALE_FAIL ...
import argparse, sys
import numpy as np, cv2
from PIL import Image


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", required=True); ap.add_argument("--k", type=float, required=True); ap.add_argument("--yh", type=float, required=True)
    ap.add_argument("--tol", type=float, default=0.05); ap.add_argument("--canvas", default="2560x1440")
    a = ap.parse_args()
    W, H = map(int, a.canvas.split("x"))
    im = Image.open(a.img).convert("RGB").resize((W, H), Image.LANCZOS)
    from rembg import remove, new_session
    m = (np.asarray(remove(im, session=new_session("u2net_human_seg"), only_mask=True)) > 100).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    rs = []
    for j in range(1, n):
        x, y, w, h, ar = st[j]
        if ar < 2500 or h < 120: continue
        f = y + h; rows = (lab[max(y, f - 12):f, x:x + w] == j).sum(1); wmax = (lab[y:f, x:x + w] == j).sum(1).max()
        if rows.mean() > 0.6 * wmax:
            print(f"  x={x}-{x + w}: 발 가려짐 — 제외"); continue
        r = h / (a.k * (f - a.yh)); rs.append(r); print(f"  x={x}-{x + w} 키={h}px 기대={a.k * (f - a.yh):.0f}px 비율={r:.2f}")
    if not rs:
        print("SCALE_FAIL 잴 사람 없음"); sys.exit(1)
    bad = [r for r in rs if abs(r - 1) > a.tol]
    tok = "SCALE_FAIL" if bad else "SCALE_OK"
    print(f"{tok} n={len(rs)} mean={np.mean(rs):.2f} max={max(rs):.2f} min={min(rs):.2f}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

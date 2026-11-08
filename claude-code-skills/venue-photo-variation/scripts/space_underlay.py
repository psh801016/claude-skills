# 렌더(물건만, 흰 배경) 카메라를 두 소실점으로 풀고, 그 카메라로 공간(벽·바닥·천장·포털) 밑그림을 투영한다.
# 사고 배경(2026-11-06 성과보고회 로비): GPT·Magnific 이 rebg 배경을 참고 사진 시점으로 그려 부스와 소실점이 달랐다
#   (2.2~4.6° 어긋남, 사용자 "공간 각도가 부스랑 안 맞아"). 기하를 직접 투영한 밑그림을 rebg 에 넣으면 0.4° 로 맞았다.
# 사용:
#   python space_underlay.py --render 렌더_흰배경.png --mask 물건.png --vp-left X,Y --vp-right X,Y
#       --anchor X,YTOP,YBOT --anchor-m 2.0 --wall-dir left|right --wall-gap 1.0 --out 밑그림.png
#   [--soffit 2.9,1.8] [--ceil 4.0] [--portal S0,S1,H] [--tile ashlar|bond]
#   --anchor: 물건 앞 모서리 세로선(x, 위 y, 바닥 y), --anchor-m: 그 실제 높이(m)
#   --wall-dir: 벽(=물건 정면)이 어느 소실점으로 달리는지. 다른 쪽이 '뒤(벽 쪽)' 방향
#   --wall-gap: 앞 모서리에서 벽면까지 거리(m). 사람이 뒤에 앉는 데스크는 2m 이상(점검표 11)
# 성공 토큰: UNDERLAY_OK f=… hc=… Z=…
import argparse, sys
import numpy as np
from PIL import Image, ImageDraw


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", required=True); ap.add_argument("--mask", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--vp-left", default=""); ap.add_argument("--vp-right", default="")  # 비우면 렌더에서 자동(RANSAC)
    ap.add_argument("--anchor", default="auto"); ap.add_argument("--anchor-m", type=float, required=True)
    ap.add_argument("--wall-dir", choices=["left", "right", "auto"], default="auto")
    ap.add_argument("--wall-gap", type=float, required=True)
    ap.add_argument("--soffit", default="", help="낮은 천장 띠: 높이,벽에서 폭(m). 없으면 평천장")
    ap.add_argument("--ceil", type=float, default=3.4)
    ap.add_argument("--portal", default="", help="벽면 개구부: s0,s1,높이(m) — s 는 벽 기준점에서 벽 방향 거리")
    ap.add_argument("--tile", choices=["ashlar", "bond"], default="bond")
    a = ap.parse_args()

    ren = Image.open(a.render).convert("RGB"); W, H = ren.size
    if a.vp_left and a.vp_right:
        vl = np.array(list(map(float, a.vp_left.split(",")))); vr = np.array(list(map(float, a.vp_right.split(","))))
        wl = wr = 1
    else:  # 자동: 물건 직선 RANSAC 소실점 2개(2026-11-06 업그레이드 — 손 측정·최소제곱 혼합이 2° 틀렸다)
        sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
        import check_vp
        msk = np.asarray(Image.open(a.mask).convert("L")) > 127
        vps = [(v, n) for v, n in check_vp.ransac_vps(check_vp.object_lines(np.asarray(ren), msk)) if n >= 3]
        if len(vps) < 2:
            print("UNDERLAY_FAIL 소실점 2개를 못 찾음 — --vp-left/--vp-right 를 직접 주라"); sys.exit(1)
        (va, na), (vb, nb) = vps[:2]
        (vl, wl), (vr, wr) = sorted([(va, na), (vb, nb)], key=lambda q: q[0][0])
    cx = W / 2
    cy = (vl[1] * wl + vr[1] * wr) / (wl + wr)   # 세로선 평행 = 기울기 0, 주점 높이 = 눈높이선(선 많은 쪽 가중)
    f2 = -(vl[0] - cx) * (vr[0] - cx)
    if f2 <= 0:
        print("UNDERLAY_FAIL 두 소실점이 주점 같은 쪽 — 직교 2점 투시가 아님"); sys.exit(1)
    f = float(np.sqrt(f2))
    dL = np.array([vl[0] - cx, 0, f]); dL /= np.linalg.norm(dL)
    dR = np.array([vr[0] - cx, 0, f]); dR /= np.linalg.norm(dR)
    wd = a.wall_dir if a.wall_dir != "auto" else ("left" if wl >= wr else "right")  # 직선 많은 소실점 = 물건 정면 = 벽 방향
    d1, d2 = (dL, dR) if wd == "left" else (dR, dL)   # d1 = 벽 방향, d2 = 뒤(벽 쪽)
    if a.anchor == "auto":  # 가장 긴 세로 기둥 = 카메라에 가장 가까운 앞 모서리. 바닥 카펫(채도 높은 빨강)은 밑에서 걷어낸다
        msk = np.asarray(Image.open(a.mask).convert("L")) > 127; rgb = np.asarray(ren).astype(int)
        carpet = (rgb[..., 0] > 50) & (rgb[..., 0] > 2 * rgb[..., 1]) & (rgb[..., 0] > 2 * rgb[..., 2])  # 그늘진 카펫 가장자리까지(밝기 무관, 빨강 우세)
        best = None
        for x in range(0, W, 2):
            ys = np.where(msk[:, x] & ~carpet[:, x])[0]
            if len(ys) < 50: continue
            gap = np.where(np.diff(ys) > 3)[0]   # 위에서부터 끊김 없는 구간만(카펫 밑 경계 픽셀 제외)
            if len(gap): ys = ys[: gap[0] + 1]
            run = ys[-1] - ys[0]
            if best is None or run > best[0]: best = (run, x, ys[0], ys[-1])
        _, ax, yt, yb = map(float, best)
        print(f"anchor auto x={ax:.0f} y={yt:.0f}..{yb:.0f}")
    else:
        ax, yt, yb = map(float, a.anchor.split(","))
    Z = f * a.anchor_m / (yb - yt); hc = (yb - cy) * Z / f
    P0 = np.array([(ax - cx) * Z / f, hc, Z])
    up = np.array([0, -1.0, 0])
    WALL0 = P0 + a.wall_gap * d2

    def proj(p): return (cx + f * p[0] / p[2], cy + f * p[1] / p[2])
    wall_pt = lambda s, h: WALL0 + s * d1 + h * up
    floor_pt = lambda s, t: WALL0 + s * d1 - t * d2
    ceil_pt = lambda s, t, h: WALL0 + s * d1 - t * d2 + h * up

    img = Image.new("RGB", (W, H), (240, 240, 238)); dr = ImageDraw.Draw(img)

    def quad(pts, fill):
        if min(p[2] for p in pts) < 0.4: return
        dr.polygon([proj(p) for p in pts], fill=fill)

    def line(p, q, fill, width=2, n=None):
        # 긴 선은 0.5m 조각으로 — 한쪽 끝이 카메라 뒤(Z<0.4)면 선 전체가 버려져 벽 가로 줄눈이 빠졌다(2026-11-06)
        n = n or max(1, int(np.linalg.norm(q - p) / 0.5))
        for i in range(n):
            a0, a1 = p + (q - p) * i / n, p + (q - p) * (i + 1) / n
            if min(a0[2], a1[2]) >= 0.4:
                dr.line([proj(a0), proj(a1)], fill=fill, width=width)

    S0, S1 = -40.0, 40.0
    sof = list(map(float, a.soffit.split(","))) if a.soffit else None
    wall_top = sof[0] if sof else a.ceil
    # 천장
    for s in np.arange(S0, S1, 0.5):
        for t in np.arange(0, 14, 0.3):
            h = sof[0] if (sof and t < sof[1]) else a.ceil
            quad([ceil_pt(s, t, h), ceil_pt(s + 0.5, t, h), ceil_pt(s + 0.5, t + 0.3, h), ceil_pt(s, t + 0.3, h)], (246, 246, 244))
    if sof:  # 낮은 띠 끝면(세로) + 코브 밝은 선 + 다운라이트 줄
        for s in np.arange(S0, S1, 0.5):
            quad([ceil_pt(s, sof[1], sof[0]), ceil_pt(s + 0.5, sof[1], sof[0]), ceil_pt(s + 0.5, sof[1], a.ceil), ceil_pt(s, sof[1], a.ceil)], (232, 232, 230))
        line(ceil_pt(S0, sof[1] + 0.05, a.ceil), ceil_pt(S1, sof[1] + 0.05, a.ceil), (255, 255, 255), 6)
        for s in np.arange(S0, S1, 1.8):
            c = ceil_pt(s, sof[1] / 2, sof[0])
            if c[2] > 0.5:
                u, v = proj(c); r = max(2, 2600 / c[2] * 0.012)
                dr.ellipse([u - r * 2, v - r, u + r * 2, v + r], fill=(255, 255, 250))
    # 벽 + 타일
    for s in np.arange(S0, S1, 0.5):
        quad([wall_pt(s, 0), wall_pt(s + 0.5, 0), wall_pt(s + 0.5, wall_top), wall_pt(s, wall_top)], (228, 222, 210))
    rng = np.random.default_rng(3)
    for k in range(int(wall_top / 0.3) + 1):
        h0 = 0.3 * k
        line(wall_pt(S0, h0), wall_pt(S1, h0), (170, 165, 158), 2)
        s = S0 + (0.6 if (k % 2 and a.tile == "bond") else rng.uniform(0, 0.6))
        while s < S1:
            line(wall_pt(s, h0), wall_pt(s, min(h0 + 0.3, wall_top)), (170, 165, 158), 2)
            s += 1.2 if a.tile == "bond" else rng.choice([0.6, 0.9, 1.2])
    if a.portal:
        p0, p1, ph = map(float, a.portal.split(","))
        for s in np.arange(p0, p1, 0.25):
            quad([wall_pt(s, 0), wall_pt(min(s + 0.25, p1), 0), wall_pt(min(s + 0.25, p1), ph), wall_pt(s, ph)], (58, 54, 50))
        for p, q in [((p0, 0), (p0, ph)), ((p1, 0), (p1, ph)), ((p0, ph), (p1, ph))]:
            line(wall_pt(*p), wall_pt(*q), (10, 10, 10), 10)
    # 바닥
    for s in np.arange(S0, S1, 0.5):
        for t in np.arange(0, 14, 0.3):
            quad([floor_pt(s, t), floor_pt(s + 0.5, t), floor_pt(s + 0.5, t + 0.3), floor_pt(s, t + 0.3)], (190, 184, 178))
    for k in range(24):
        line(floor_pt(S0, 0.6 * k), floor_pt(S1, 0.6 * k), (160, 154, 148), 2)
    for s in np.arange(S0, S1, 1.2):
        for t in np.arange(0, 14, 0.3):
            line(floor_pt(s, t), floor_pt(s, t + 0.3), (160, 154, 148), 2)
    line(floor_pt(S0, 0), floor_pt(S1, 0), (120, 118, 114), 3)
    img.paste(ren, (0, 0), Image.open(a.mask).convert("L"))
    img.save(a.out)
    print(f"UNDERLAY_OK wall_dir={wd} f={f:.0f} hc={hc:.2f}m Z={Z:.2f}m wall_gap={a.wall_gap}m vpL={tuple(vl.astype(int))} vpR={tuple(vr.astype(int))}")


if __name__ == "__main__":
    main()

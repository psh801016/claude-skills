# 부스 통째 고정 — AI 사진(사람·홀)은 그대로, 부스 면은 원본 렌더를 AI 가 그린 부스 모양에 촘촘히(광흐름) 휘어 맞춰 한 덩어리로 붙인다.
# 배경: 2026-11-06 Kofpi "하나 고치면 하나 지랄 나고 / 얼룩은 또 뭐여". 인쇄물 조각만 붙이면 조각 경계마다 AI 와 렌더의 모양 차이가
#   계단·얼룩으로 드러났다. 경계를 부스 외곽선과 사람 윤곽선으로만 두면 면 중간 이음매가 생기지 않는다.
# 조명: AI 사진의 저주파 밝기비(부스 안, 사람 제외) × 렌더 + AI 와 같은 크기의 센서 노이즈.
# 사용: python lock_booth.py --src 렌더(흰배경,캔버스크기).png --alpha 부스알파.png --cand AI사진.png --people 사람마스크.png --out 결과.png
# 성공 토큰: LOCK_OK <경로> flow_p95=<px>
import argparse, sys
from pathlib import Path
import numpy as np, cv2
from PIL import Image


def load(p, mode="RGB"):
    return np.asarray(Image.open(p).convert(mode))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    for n in ("--src", "--alpha", "--cand", "--people", "--out"): ap.add_argument(n, required=True)
    ap.add_argument("--light-sigma", type=float, default=120.0, help="조명 비율을 재는 범위(px). 좁으면(14) AI 가 다르게 그린 그래픽을 조명으로 착각해 흰 면에 얼룩이 찍힌다(2026-11-06). 넓게(120)")
    ap.add_argument("--plate", help="같은 AI 사진에서 사람만 지운 판(정합본). 집기 뒤 사람 자동 판정(약함) — --occluder 가 정답")
    ap.add_argument("--occluder", help="사람보다 앞에 있는 집기 마스크(흰색, 렌더 좌표). 이 안은 사람이 있어도 무조건 렌더. 카운터 뒤에 선 사람(발이 집기 바닥선보다 위)의 집기를 넣는다 — 2026-11-06 '부스 잘리잖아'의 정답")
    ap.add_argument("--flow", action="store_true", help="광흐름 촘촘한 정렬(실험) — 2026-11-06 기둥이 물결처럼 휘어 반려, 기본 꺼짐")
    a = ap.parse_args()
    src = load(a.src); h, w = src.shape[:2]
    cand = cv2.resize(load(a.cand), (w, h), interpolation=cv2.INTER_LANCZOS4)
    al = cv2.resize(load(a.alpha, "L"), (w, h), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
    ppl = cv2.resize(load(a.people, "L"), (w, h)) > 127
    # 1) 전역 정렬(부분 아핀, 부스 특징점) — AI → 렌더 좌표
    orb = cv2.ORB_create(10000); fm = cv2.dilate((al > 0.5).astype(np.uint8) * 255, np.ones((15, 15), np.uint8))
    k1, d1 = orb.detectAndCompute(cv2.cvtColor(cand, cv2.COLOR_RGB2GRAY), fm); k2, d2 = orb.detectAndCompute(cv2.cvtColor(src, cv2.COLOR_RGB2GRAY), fm)
    ms = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d1, d2), key=lambda x: x.distance)[:3000]
    p1 = np.float32([k1[m.queryIdx].pt for m in ms]); p2 = np.float32([k2[m.trainIdx].pt for m in ms])
    A, _ = cv2.estimateAffinePartial2D(p1, p2, method=cv2.RANSAC, ransacReprojThreshold=3.0)
    cw = cv2.warpAffine(cand, A, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    pw = cv2.warpAffine(ppl.astype(np.uint8), A, (w, h), flags=cv2.INTER_NEAREST) > 0
    # 2) 촘촘한 정렬: 렌더 → AI 광흐름(그라디언트 기반, 사람 자리는 주변으로 메워 무시), 강하게 매끈하게
    gs = cv2.cvtColor(src, cv2.COLOR_RGB2GRAY); gc = cv2.cvtColor(cw, cv2.COLOR_RGB2GRAY)
    gc_f = gc.copy(); gc_f[pw] = cv2.inpaint(gc, pw.astype(np.uint8), 15, cv2.INPAINT_TELEA)[pw]
    # 배경(부스 밖)은 렌더가 흰색이라 흐름이 튄다 → 부스 안만 쓰고 밖은 0
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    flow = dis.calc(gc_f, gs, None)                       # 각 렌더 픽셀이 AI 의 어디에 해당하는지가 아니라: gc(x+flow) ≈ gs(x)
    inside = cv2.erode((al > 0.5).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
    for c in range(2):
        f = flow[..., c] * inside
        flow[..., c] = cv2.GaussianBlur(f, (0, 0), 25) / (cv2.GaussianBlur(inside, (0, 0), 25) + 1e-3)
    flow = np.clip(flow, -12, 12)
    if not a.flow: flow[:] = 0          # 기본: 부스는 렌더 그대로(전역 정렬만) — 면 안 이음매·휨 없음
    mag = np.hypot(flow[..., 0], flow[..., 1])
    # 렌더를 AI 모양으로: 출력 위치 y 의 값 = 렌더(y - flow(y)) — flow 는 렌더→AI 이동이므로 역으로 근사
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    mx, my = xx - flow[..., 0], yy - flow[..., 1]
    sw = cv2.remap(src.astype(np.float32), mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    aw = cv2.remap(al, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    # 3) 조명: AI 저주파 밝기 / 렌더 저주파 밝기 (부스 안·사람 밖)
    m = ((aw > 0.5) & ~pw).astype(np.float32)
    lb = lambda X: cv2.GaussianBlur(X.mean(2) * m, (0, 0), a.light_sigma) / (cv2.GaussianBlur(m, (0, 0), a.light_sigma) + 1e-3) + 6
    ratio = np.clip(lb(cw.astype(np.float32)) / lb(sw), 0.55, 1.25)[..., None]
    booth = sw * ratio
    # 4) 노이즈: AI 의 평평한 곳 수준
    hp = lambda g: g - cv2.GaussianBlur(g, (0, 0), 1.0)
    gcf = gc.astype(np.float32); nz = float(np.percentile(np.abs(hp(gcf))[m > 0], 50)) * 1.25
    rng = np.random.default_rng(7); booth = booth + rng.normal(0, nz, (h, w))[..., None]
    # 5) 앞뒤 순서 — 2026-11-06 "부스 잘리잖아 / 모서리 두 겹 / 글자 찌그러짐" 의 진짜 원인: 카운터 뒤에 선 사람의 다리까지 '사람 자리'로
    #    남겨 카운터가 다리 모양대로 잘렸다. 판정: 사람 마스크 픽셀 중 'AI 사진이 사람 없는 판과 같은 곳'(= AI 도 거기에 집기를 그림)은
    #    집기가 앞 → 렌더가 덮는다. 판이 없으면 사람 자리 전부를 사람으로 둔다(옛 동작).
    person_front = pw.copy()
    if a.plate:
        pl = cv2.resize(load(a.plate), (w, h), interpolation=cv2.INTER_LANCZOS4)
        pl = cv2.warpAffine(pl, A, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
        cwf = cw.astype(np.float32); pl = pl + cv2.GaussianBlur(cwf - pl, (0, 0), 30)
        same = np.abs(cv2.GaussianBlur(cwf, (0, 0), 1.5) - cv2.GaussianBlur(pl, (0, 0), 1.5)).max(2) < 14
        same = cv2.morphologyEx(same.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)).astype(bool)
        occl = pw & same & (aw > 0.5)                      # 사람 마스크인데 AI 에서도 집기인 곳 = 집기가 앞
        occl = cv2.morphologyEx(occl.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        # 집기와 이어진 덩어리만 — 사람 몸 안에 고립된 작은 조각(옷 색이 우연히 판과 같음)은 집기가 아니다(2026-11-06 스태프 몸 흰 점)
        outside = cv2.dilate(((aw > 0.5) & ~pw).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        n_o, l_o, s_o, _ = cv2.connectedComponentsWithStats(occl); keep_o = np.zeros_like(occl)
        for j in range(1, n_o):
            c = l_o == j
            if s_o[j][4] >= 300 and (c & outside).any(): keep_o[c] = 1
        occl = keep_o.astype(bool)
        person_front = pw & ~occl
        print(f"  집기 뒤 사람 픽셀 {int(occl.sum())} → 렌더가 앞")
    if a.occluder:
        occm = cv2.resize(load(a.occluder, "L"), (w, h), interpolation=cv2.INTER_NEAREST) > 127
        print(f"  --occluder: 사람 마스크 중 집기 앞 {int((pw & occm).sum())}px 를 렌더로")
        person_front = person_front & ~occm
    k = cv2.GaussianBlur((aw * (1 - cv2.dilate(person_front.astype(np.uint8), np.ones((3, 3), np.uint8)))).astype(np.float32), (0, 0), 0.8)[..., None]
    # 외곽 띠 정리: AI 가 부스를 몇 px 크게 그린 곳은 렌더 외곽 밖에 AI 부스 조각(흰·초록 띠)이 남는다 → 바깥 홀로 메움
    ring = (cv2.dilate((aw > 0.5).astype(np.uint8), np.ones((19, 19), np.uint8)) > 0) & (aw < 0.5) & ~pw
    hallref = cv2.medianBlur(cw, 21).astype(np.float32)
    brighter = (cw.astype(np.float32).mean(2) - hallref.mean(2)) > 18
    sl = (ring & brighter).astype(np.uint8)
    if sl.any():
        cwi = cv2.inpaint(cw, cv2.dilate(sl, np.ones((3, 3), np.uint8)), 7, cv2.INPAINT_TELEA)
        cw = np.where(cv2.dilate(sl, np.ones((3, 3), np.uint8))[..., None] > 0, cwi, cw)
    out = booth * k + cw.astype(np.float32) * (1 - k)
    out = np.clip(out, 0, 255).astype(np.uint8)
    o = Path(a.out); Image.fromarray(out).save(o)
    # 검수 시트(부스 6칸 100%)
    ys, xs = np.where(aw > 0.5); bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
    tw, th = (bx1 - bx0) // 3 + 1, (by1 - by0) // 2 + 1
    sh = Image.new("RGB", (tw * 3 + 20, th * 2 + 10)); R = Image.fromarray(out)
    for i in range(6):
        cx, cy = bx0 + (i % 3) * tw, by0 + (i // 3) * th
        sh.paste(R.crop((cx, cy, cx + tw, cy + th)), ((i % 3) * (tw + 10), (i // 3) * (th + 10)))
    sh.save(o.with_name(o.stem + "_review.jpg"), quality=88)
    print(f"LOCK_OK {o} flow_p95={float(np.percentile(mag[al > 0.5], 95)):.1f}px noise={nz:.1f}")


if __name__ == "__main__":
    main()

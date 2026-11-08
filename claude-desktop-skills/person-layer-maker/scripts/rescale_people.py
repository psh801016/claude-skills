# 사람 키를 원근 기준(키 막대 k·y_horizon)에 맞춰 발 위치 기준으로 줄인다 — 그림자·반사까지 같이.
# 배경: 2026-11-06 Kofpi 부스1·2 "사람 너무 큰 거 아녀, 750 한 칸이라니까 지금 키가 거의 2미터여".
#   Magnific(NB 2.1)은 막대 길이를 거의 무시한다 — 막대를 0.88배로 줘도 기준보다 8~14% 크게 그렸다(실측 4장).
#   그래서 크기는 생성 뒤 기하로 맞춘다. 이음매는 다음 단계의 전체 실사화(GPT realize)가 녹인다.
# 사용:
#   python rescale_people.py --img 사람있는합성.png --base 사람없는판.png --people people_mask.png --lock 디자인물알파.png \
#       --k 0.903 --yh 720.9 --out 결과.png [--feet x0-x1:y ...]
#   --feet = 마스크가 엉덩이에서 잘린 사람의 발 y(가로 범위로 지정). 카운터 뒤처럼 발이 가려진 사람은 건너뛴다.
# 성공 토큰: RESCALE_OK <경로> scaled=<n> skipped=<n>
import argparse, sys
import numpy as np, cv2
from PIL import Image


def load(p, mode="RGB"):
    return np.asarray(Image.open(p).convert(mode))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    for n in ("--img", "--base", "--people", "--lock", "--out"): ap.add_argument(n, required=True)
    ap.add_argument("--k", type=float, required=True); ap.add_argument("--yh", type=float, required=True)
    ap.add_argument("--feet", action="append", default=[]); ap.add_argument("--tol", type=float, default=0.04)
    ap.add_argument("--ids", help="extract_people.py 의 people_ids.png(사람별 번호). 주면 덩어리 대신 사람 번호로 나눈다")
    ap.add_argument("--behind", action="append", default=[], help="x0-x1:바닥y — 카운터 뒤처럼 발이 가려진 사람. 다른 사람들의 비율 중앙값으로, 자기 바닥점 기준으로 줄이고 원래 가림선 아래는 안 붙인다(2026-11-06 스태프: 옆 사람과 묶여 남의 발 기준으로 줄이자 80px 내려앉아 '상판에 상반신이 걸림')")
    a = ap.parse_args()
    img = load(a.img).astype(np.float32); h, w = img.shape[:2]
    base = cv2.resize(load(a.base), (w, h)).astype(np.float32)
    pm = cv2.resize(load(a.people, "L"), (w, h)) > 127
    lock = cv2.resize(load(a.lock, "L"), (w, h), interpolation=cv2.INTER_NEAREST) > 127
    over = []
    for f in a.feet:
        r, y = f.split(":"); x0, x1 = map(int, r.split("-")); over.append((x0, x1, int(y)))
    behind = []
    for b in a.behind:
        r, y = b.split(":"); x0, x1 = map(int, r.split("-")); behind.append((x0, x1, int(y)))
    pm_all = pm.copy()
    for x0, x1, _ in behind: pm[:, x0:x1 + 1] &= False                 # 가려진 사람은 묶기에서 뺀다(옆 사람과 한 덩어리 방지)
    pb = pm.astype(np.uint8); n, lab, st, _ = cv2.connectedComponentsWithStats(pb)
    comps = [list(map(int, st[j][:4])) for j in range(1, n) if st[j][4] >= 300]
    idm = cv2.resize(load(a.ids, "L"), (w, h), interpolation=cv2.INTER_NEAREST) if a.ids else None
    if idm is not None:   # 사람 번호가 있으면 번호마다 한 사람
        comps = []
        for v in np.unique(idm):
            if v == 0: continue
            ys_, xs_ = np.where((idm == v) & pm)
            if len(ys_) >= 300: comps.append([int(xs_.min()), int(ys_.min()), int(xs_.max() - xs_.min() + 1), int(ys_.max() - ys_.min() + 1), int(v)])
    persons = []
    for cc in sorted(comps, key=lambda c: c[0]):
        x0, y0, bw, bh = cc[:4]
        if idm is not None:
            persons.append([x0, y0, x0 + bw, y0 + bh, cc[4]]); continue
        for P in persons:
            # 위아래로 끊긴 한 사람의 조각만 묶는다(가로 겹침 40%↑ + 세로 겹침이 작은 쪽 키의 30%↓).
            #   나란히 선 두 사람은 세로 범위가 거의 같아 묶지 않는다 — 묶으면 남의 발 기준으로 줄어 얼굴에 띠가 생겼다(2026-11-06 부스1 스태프)
            xo = min(P[2], x0 + bw) - max(P[0], x0); yo = min(P[3], y0 + bh) - max(P[1], y0)
            if xo > 0.4 * min(P[2] - P[0], bw) and yo < 0.3 * min(P[3] - P[1], bh):
                P[:] = [min(P[0], x0), min(P[1], y0), max(P[2], x0 + bw), max(P[3], y0 + bh)]; break
        else:
            persons.append([x0, y0, x0 + bw, y0 + bh])
    diff = np.abs(cv2.GaussianBlur(img, (0, 0), 1.5) - cv2.GaussianBlur(base, (0, 0), 1.5)).max(2)
    # 판 톤 맞추기 — 사람 없는 판은 따로 생성된 사진이라 밝기·색이 미세하게 달라, 큰 사람을 지운 테두리에 잔상이 남았다
    #   (2026-11-06 부스1 "사람 주변 잔상 같은 건?"). 사람 밖(넉넉히 뺀 곳)에서 잰 저주파 차이를 판 전체에 더한다.
    far = (~(cv2.dilate(pm.astype(np.uint8), np.ones((61, 61), np.uint8)) > 0)).astype(np.float32)
    nb = lambda x, sg: cv2.GaussianBlur(x * far[..., None], (0, 0), sg) / (cv2.GaussianBlur(far, (0, 0), sg)[..., None] + 1e-3)
    base = base + nb(img - base, 18)
    jobs = []; done = skipped = 0
    for P in sorted(persons, key=lambda P: P[3]):                       # 뒤(위) 사람부터
        x0, y0, x1, f = P[:4]; pid = P[4] if len(P) > 4 else None
        hh = f - y0
        if hh < 80: continue
        ov = [o for o in over if o[0] <= (x0 + x1) // 2 <= o[1]]
        pbo = ((idm == pid) & pm).astype(np.uint8) if pid is not None else pb
        rows = pbo[max(y0, f - 12):f, x0:x1].sum(1); wmax = pbo[y0:f, x0:x1].sum(1).max()
        truncated = rows.mean() > 0.7 * wmax
        below_lock = lock[min(h - 1, f + 4), (x0 + x1) // 2] and not lock[max(0, f - 4), (x0 + x1) // 2]
        if ov: f = ov[0][2]; hh = f - y0
        elif truncated or below_lock:
            print(f"  skip x={x0}-{x1}: 발이 안 보임({'잘린 마스크' if truncated else '물건 뒤'}) — --feet 로 지정"); skipped += 1; continue
        ratio = hh / (a.k * (f - a.yh))
        if ratio <= 1 + a.tol:
            # 크기가 맞는 사람도 원래 크기(s=1)로 다시 붙인다 — 옆 사람을 지운 영역이 이 사람 몸까지 넘어가 흐린 띠가 생겼다(2026-11-06 부스1 스태프)
            own = (idm == pid) if pid is not None else np.zeros((h, w), bool)
            if pid is None: own[y0:f + 1, x0:x1 + 1] = True
            k1 = (pm & own).astype(np.uint8)
            A1 = cv2.GaussianBlur(cv2.dilate(k1, np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0), 1.5)
            jobs.append((A1, np.zeros((h, w), np.uint8), 1.0, (x0 + x1) / 2, f)); print(f"  ok   x={x0}-{x1}: 키 비율 {ratio:.2f} (그대로 다시 붙임)"); continue
        s = float(np.clip(1 / ratio, 0.75, 1.0)); fx = (x0 + x1) / 2
        X0, X1 = max(0, int(x0 - hh * .25)), min(w, int(x1 + hh * .25)); Y0, Y1 = max(0, y0 - 10), min(h, int(f + hh * .7))
        reg = np.zeros((h, w), np.uint8); reg[Y0:Y1, X0:X1] = 1
        own = (idm == pid) if pid is not None else np.zeros((h, w), bool)
        if pid is None: own[y0:f + 1, x0:x1 + 1] = True
        al = (pm & own).astype(np.uint8)                                  # 이 사람 몸만
        # 몸만 옮긴다 — 발 위치는 그대로이므로 발밑 그림자·반사는 원래 사진 것을 둔다. 그림자를 '판과 다른 곳'으로 같이 옮기면
        #   판이 다르게 그린 카운터 모서리 조각이 딸려 와 엉뚱한 선이 생겼다(2026-11-06 부스1 여성 다리 옆).
        keep = al.copy()
        A = cv2.GaussianBlur(cv2.dilate(keep, np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0), 2)
        # 지울 자리는 넉넉히 — 사람 마스크가 놓친 머리카락·어깨 끝이 유령으로 남았다(2026-11-06 첫 시도)
        Ebig = cv2.dilate(keep, np.ones((13, 13), np.uint8)) & reg & ~(pm & ~own).astype(np.uint8)
        jobs.append((A, Ebig, s, fx, f)); print(f"  scale x={x0}-{x1}: 키 비율 {ratio:.2f} → x{s:.3f}"); done += 1
    ratios = [1 / j[2] for j in jobs if j[2] < 1.0] or [1 / j[2] for j in jobs]
    for x0, x1, fy in behind:                                            # 가려진 사람: 중앙 비율, 자기 바닥점 기준
        own = np.zeros((h, w), bool); own[:, x0:x1 + 1] = True
        keep = (pm_all & own).astype(np.uint8)
        if not keep.any() or not ratios: continue
        ys, xs = np.where(keep); cut = ys.max()                          # 원래 가림선(카운터 상판)
        s = float(np.clip(1 / np.median(ratios), 0.75, 1.0)); fx = (xs.min() + xs.max()) / 2
        A = cv2.GaussianBlur(cv2.dilate(keep, np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0), 1.5)
        A_paste = A.copy()
        Eb = cv2.dilate(keep, np.ones((25, 25), np.uint8)) * (np.arange(h)[:, None] < cut + 3)
        jobs.insert(0, (A_paste, Eb, s, fx, fy, cut)); print(f"  behind x={x0}-{x1}: 중앙 비율 {1 / s:.2f} → x{s:.3f}, 바닥 y={fy}, 가림선 y={cut}"); done += 1
    # 1) 줄일 사람들을 한꺼번에 지운다(사람 없는 판) 2) 줄인 사람을 뒤 → 앞 순서로 붙인다
    #    한 명씩 지우고 붙이면 앞사람을 지울 때 이미 붙인 뒷사람이 같이 지워졌다.
    E = np.zeros((h, w), np.float32)
    for jb in jobs: E = np.maximum(E, jb[1].astype(np.float32))
    E = cv2.GaussianBlur(E, (0, 0), 3)[..., None]
    out = base * E + img * (1 - E)
    placed = np.zeros((h, w), np.float32)                               # 최종 위치의 사람 마스크(다음 단계 restore_graphics --people 용)
    for jb in sorted(jobs, key=lambda j: j[4]):                          # 뒤(발이 위) → 앞 순서
        A, Eb, s, fx, f = jb[:5]; cut = jb[5] if len(jb) > 5 else None
        T = np.float32([[s, 0, fx * (1 - s)], [0, s, f * (1 - s)]])
        As = cv2.warpAffine(A, T, (w, h), flags=cv2.INTER_LINEAR)
        if cut is not None: As *= (np.arange(h)[:, None] < cut)          # 가림선 아래는 카운터가 가린다
        Is = cv2.warpAffine(img, T, (w, h), flags=cv2.INTER_CUBIC)
        out = Is * As[..., None] + out * (1 - As[..., None])
        placed = np.maximum(placed, As)
    # 디자인물은 사람 없는 판에서(줄어든 사람이 비운 자리 포함), 단 줄인 사람이 앞에 선 곳은 사람
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(a.out)
    # 사람 분할 모델은 사람을 놓친다(카운터 뒤 스태프·패널 앞 남성) — 붙인 위치를 그대로 저장해 글자 복원이 사람을 덮지 않게(2026-11-06)
    from pathlib import Path as _P
    Image.fromarray((np.clip(placed, 0, 1) * 255).astype(np.uint8)).save(str(_P(a.out).with_name(_P(a.out).stem + "_people.png")))
    print(f"RESCALE_OK {a.out} scaled={done} skipped={skipped}")


if __name__ == "__main__":
    main()

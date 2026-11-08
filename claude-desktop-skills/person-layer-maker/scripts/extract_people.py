# 경로 C 자동화 — 장면에 사람을 넣은 GPT 후보에서 '사람 + 접지 그림자'만 레이어로 떼어 원본 위에 얹는다.
# 배경: 2026-11-05 KOBC 로비 등록데스크 — "사람이 항상 좀 인위적이고 어색해". 사람은 장면 안에서 생성해야 빛·원근이 맞고,
#       GPT 는 화면 전체를 다시 그리므로(카운터 그래픽·카펫까지 변형) 사람 밖은 반드시 원본 픽셀이어야 한다.
#       같은 날 실측 함정: ① GPT 가 카운터 그래픽을 다시 그려 차이 영역이 사람들과 한 덩어리로 붙는다 → 사람 박스를 받는다
#       ② 사람 분할을 화면 전체에 돌리면 작은·먼 사람을 놓친다 → 박스마다 크롭해서 돌린다
#       ③ GPT 는 사람을 18% 작게 그렸다(키 1.4m) → --k/--yh 를 주면 사람마다 원근식 키와 비교해 ±5% 넘으면 FAIL.
# 사람 실루엣 = 분할 모델(rembg birefnet-general — 손에 든 물건 포함, Select Subject 대응) ∩ 원본과 달라진 곳(넓게). 뒤에 선 사람은 가림막 영역 제외.
# 사용:
#   python extract_people.py --base 원본.png --cand 후보.png --out-dir 폴더 \
#       --box "x1,y1,x2,y2" --box "x1,y1,x2,y2:behind" ... [--occluder 가림마스크.png] [--k 1.414 --yh 725.7]
#   박스 = 원본 픽셀 기준 사람 하나(발끝 포함). ':behind' = 카운터 뒤(발이 안 보임, 키 검사 생략), ':behind:dy=-38' = 위로 38px 이동
#   (GPT 가 카운터 상판을 낮게 그려 손·태블릿이 원본 상판에 묻힐 때 — 2026-11-05 "안내원 몸통 짤려"), ':edge' = 프레임 끝 흐린 행인.
# 출력: people_layer.png(RGBA), shadow_layer.png(곱하기 계수, 흰=변화 없음), people_mask.png, people_final.png
# 확인 시트: check_feet.jpg(사람별 아랫단 확대) — 공중부양·다리 잘림은 수치로 못 잡아 눈으로 본다
# 성공 토큰: PEOPLE_OK … / 키 오차 ±5% 초과 사람이 있으면 PEOPLE_SCALE_FAIL (exit 2, 파일은 남김)
import argparse, sys
from pathlib import Path
import numpy as np, cv2
from PIL import Image


def load(p, mode="RGB"):
    return np.asarray(Image.open(p).convert(mode))


def photo_finish(lay, al, bg, hh, front, feet, fx, gal=None, lock=None):
    """사진 마감 — 2026-11-05 "지금 사진 같지 않어": AI 인물은 배경보다 선명·깨끗하고, 주변 색이 안 묻고, 윤곽이 오려 붙인 듯하다.
    ① (자동 흐림 없음) ② 배경의 평평한 곳과 같은 센서 노이즈(상한 3) ③ 주변 색 묻힘(ab 25%) ④ 라이트랩(윤곽 2~3px 에 배경 빛 번짐) ⑤ 발밑 접지 AO.
    lay/bg float32 RGB(전체 캔버스), al 0~1. 반환: (lay, bg)"""
    body = (al > 0.5).astype(np.uint8)
    if not body.any():
        return lay, bg
    r = max(6, int(hh * 0.12))
    ring = cv2.dilate(body, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))).astype(bool) & ~cv2.dilate(body, np.ones((7, 7), np.uint8)).astype(bool)
    inner = cv2.erode(body, np.ones((5, 5), np.uint8)).astype(bool)
    if ring.sum() < 200 or inner.sum() < 200:
        return lay, bg
    gb, gl = cv2.cvtColor(np.clip(bg, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32), cv2.cvtColor(np.clip(lay, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    # ① 선명도 자동 흐림은 쓰지 않는다 — 주변이 매끈한 인쇄면이면 사람을 과하게 뭉갠다(2026-11-05 실측: 회색 재킷 여성 뿌옇게).
    # ② 노이즈: 주변에서 '가장 평평한' 곳(국소 표준편차 하위 20%)의 센서 노이즈에 맞춘다 — 카펫 무늬를 노이즈로 읽지 않게. 상한 3.
    hp = lambda g: g - cv2.GaussianBlur(g, (0, 0), 1.0)
    gl = cv2.cvtColor(np.clip(lay, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    def flat_noise(g, m):
        loc = np.sqrt(cv2.GaussianBlur(hp(g) ** 2, (0, 0), 3))
        v = loc[m]; return float(np.percentile(v, 20)) if v.size else 0.0
    nb, nl = flat_noise(gb, ring), flat_noise(gl, inner)
    add = min(3.0, np.sqrt(max(0.0, nb * nb - nl * nl)))
    if add > 0.3:
        rng = np.random.default_rng(int(fx) * 7 + int(feet))
        lay = lay + rng.normal(0, add, lay.shape[:2]).astype(np.float32)[..., None]
    # ③ 주변 색 묻힘: Lab a·b 평균을 주변 쪽으로 25%
    lab_l = cv2.cvtColor(np.clip(lay, 0, 255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    lab_b = cv2.cvtColor(np.clip(bg, 0, 255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
    for c in (1, 2):
        lab_l[..., c] += 0.25 * (lab_b[..., c][ring].mean() - lab_l[..., c][inner].mean())
    lay = cv2.cvtColor(np.clip(lab_l, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32)
    # ④ 라이트랩: 윤곽 안쪽 띠에 흐린 배경 빛을 섞는다
    band = np.clip(al - cv2.erode(al, np.ones((5, 5), np.uint8)), 0, 1)
    wrap = cv2.GaussianBlur(band, (0, 0), 1.2)[..., None] * 0.35
    lay = lay * (1 - wrap) + cv2.GaussianBlur(bg, (0, 0), 6) * wrap
    # ⑤ 접지 그림자 두 겹 — 2026-11-06 "카펫에 사람이 붕 뜨는 거 같아": 한 겹(30%)은 카펫에서 안 보였다.
    #   ⓐ 접촉: 신발 바로 밑, 발 아랫단 폭, 높이 1.2% 키, 55% ⓑ 주변: 사람 폭 0.7배, 높이 4% 키, 25%(위에서 오는 부스 조명)
    #   사람 한 명(덩어리)씩 판정 — 박스 하나에 두 사람이 서면 '발'을 낮은 사람 것으로 잡아 다른 사람은 그림자가 없었다(2026-11-06 스태프).
    #   잠금 구역(카펫·부스 바닥)에 선 사람은 항상, 유광 바닥 사람은 후보 반사·그림자를 옮긴 게 약할 때만.
    if front:
        n, lab, st, _ = cv2.connectedComponentsWithStats(body)
        ao = np.zeros(al.shape, np.float32)
        for j in range(1, n):
            x0, y0, bw, bh, area = st[j]
            if area < 400 or bh < 40: continue
            comp = lab == j; f = int(y0 + bh - 1); ph = float(bh)
            fxs = np.where(comp[max(0, int(f - ph * 0.05)):f + 1].any(0))[0]
            if not len(fxs): continue
            cx = int((fxs.min() + fxs.max()) / 2)
            on_lock = lock is not None and lock[min(lock.shape[0] - 1, f + 3), min(lock.shape[1] - 1, cx)]
            g = gal[max(0, f - 6):f + 10, max(0, cx - 40):cx + 40] if gal is not None else np.zeros(1)
            if not on_lock and g.size and g.mean() >= 0.25: continue
            c = np.zeros(al.shape, np.float32); o = np.zeros(al.shape, np.float32)
            cv2.ellipse(c, (cx, f), (max(4, int((fxs.max() - fxs.min()) * 0.6)), max(2, int(ph * 0.012))), 0, 0, 360, 1.0, -1)
            cv2.ellipse(o, (cx, int(f + ph * 0.005)), (max(6, int(bw * 0.7)), max(3, int(ph * 0.04))), 0, 0, 360, 1.0, -1)
            c = cv2.GaussianBlur(c, (0, 0), max(1.5, ph * 0.006)); o = cv2.GaussianBlur(o, (0, 0), max(3, ph * 0.02))
            # 발밑 바닥과 같은 색 면에만 — 옆 카운터 인쇄면·기둥에 그림자가 번지면 디자인물이 더럽혀진다(2026-11-06 스태프 옆 카운터)
            yb0, yb1 = min(bg.shape[0] - 1, f + 2), min(bg.shape[0], f + 2 + max(4, int(ph * 0.02)))
            xb0, xb1 = max(0, int(fxs.min() - bw * 0.3)), min(bg.shape[1], int(fxs.max() + bw * 0.3))
            patch = bg[yb0:yb1, xb0:xb1][~(al[yb0:yb1, xb0:xb1] > 0.3)]
            if patch.size:
                gcol = np.median(patch.reshape(-1, 3), 0)
                sim = np.exp(-((np.linalg.norm(cv2.GaussianBlur(bg, (0, 0), 2) - gcol, axis=2) / 28.0) ** 2))
            else:
                sim = 1.0
            ao = np.maximum(ao, (0.55 * c + 0.25 * o) * sim)
        bg = bg * (1 - np.clip(ao, 0, 0.65) * (1 - al))[..., None]
    return lay, bg


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True); ap.add_argument("--cand", required=True); ap.add_argument("--out-dir", required=True)
    ap.add_argument("--box", action="append", default=[])
    ap.add_argument("--auto-boxes", action="store_true", help="새로 생긴 사람을 자동으로 찾아 박스를 만든다(가림막에 발이 걸치면 자동 behind). 찾은 박스를 출력하니 고칠 때 --box 로 다시 준다")
    ap.add_argument("--strict-scale", action="store_true", help="키 오차 ±5%% 를 FAIL 로 본다(기본은 경고만 — 2026-11-05 '사람 너무 커')")
    ap.add_argument("--occluder"); ap.add_argument("--diff-thr", type=float, default=12)
    ap.add_argument("--k", type=float); ap.add_argument("--yh", type=float)
    ap.add_argument("--no-finish", dest="finish", action="store_false", help="사진 마감(선명도·노이즈·색 묻힘·라이트랩·접지 AO) 끄기")
    ap.add_argument("--seg-model", default="birefnet-general", help="사람+손에 든 물건을 한 덩어리로 따는 분할 모델. u2net_human_seg 는 태블릿·폰·서류를 빼먹는다(2026-11-05 \"사람 빵구났다\")")
    ap.add_argument("--lock", help="디자인물 잠금 마스크(흰색=부스·데스크·포토월). 발밑 그림자·반사는 이 안에서 접지띠(키 6%%)까지만 옮긴다")
    ap.add_argument("--no-ground", dest="ground", action="store_false", help="후보의 발밑 그림자·바닥 반사 옮기기 끄기(옛 방식: 어둡게만)")
    ap.add_argument("--fix-scale", action="store_true", help="앞에 선 사람의 키 오차를 발 위치 기준 확대·축소로 보정(가림막 뒤 사람은 보정 불가 → 재생성)")
    a = ap.parse_args()
    od = Path(a.out_dir); od.mkdir(parents=True, exist_ok=True)
    base = load(a.base); h, w = base.shape[:2]
    cand = cv2.resize(load(a.cand), (w, h), interpolation=cv2.INTER_CUBIC)

    g1, g2 = cv2.cvtColor(cand, cv2.COLOR_RGB2GRAY), cv2.cvtColor(base, cv2.COLOR_RGB2GRAY)
    orb = cv2.ORB_create(10000)
    k1, d1 = orb.detectAndCompute(g1, None); k2, d2 = orb.detectAndCompute(g2, None)
    ms = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(d1, d2), key=lambda x: x.distance)[:3000]
    p1 = np.float32([k1[x.queryIdx].pt for x in ms]); p2 = np.float32([k2[x.trainIdx].pt for x in ms])
    A, inl = cv2.estimateAffinePartial2D(p1, p2, method=cv2.RANSAC, ransacReprojThreshold=3.0); inl = inl.ravel().astype(bool)
    rms = float(np.sqrt(np.mean(np.sum((cv2.transform(p1[inl][None], A)[0] - p2[inl]) ** 2, 1))))
    cw = cv2.warpAffine(cand, A, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    from rembg import new_session, remove
    sess = new_session(a.seg_model)
    diff = np.abs(cv2.GaussianBlur(cw, (0, 0), 1.5).astype(int) - cv2.GaussianBlur(base, (0, 0), 1.5).astype(int)).max(2)
    dmask = cv2.dilate((diff > a.diff_thr).astype(np.uint8), np.ones((9, 9), np.uint8))
    # 위치 허용 차이: GPT 가 카운터 상판·백월 모서리를 몇 px 다르게 그린 것은 물건이 아니다(2026-11-05: 상판 조각이 사람에 딸려와 이음매)
    # → 원본을 반경 5px 로 팽창/침식한 범위 밖으로 벗어난 색만 '달라짐'으로 본다.
    kk = np.ones((11, 11), np.uint8); cb = cv2.GaussianBlur(cw, (0, 0), 1.5).astype(int)
    bmax = cv2.dilate(base, kk).astype(int); bmin = cv2.erode(base, kk).astype(int)
    diff_strong = (np.maximum(cb - bmax, 0) + np.maximum(bmin - cb, 0)).max(2) > 30
    occ = cv2.resize(load(a.occluder, "L"), (w, h), interpolation=cv2.INTER_NEAREST) > 127 if a.occluder else None

    if a.auto_boxes:
        # 화면 전체 사람 분할은 작은·먼 사람을 놓친다(u2net 2026-11-05 실측: 연사·뒤 여자 누락) → 손에 든 물건까지 잡는 분할(sess)을 쓴다
        segf = np.asarray(remove(Image.fromarray(cw), session=sess, only_mask=True)) > 110
        # 사람 덩어리 전체를 박스로 잡고, '달라진 곳'은 덩어리가 새 사람인지 판정에만 쓴다(픽셀 AND 금지 —
        # 회색 바지·검은 구두가 어두운 카펫과 같다고 봐서 박스가 구두 위에서 끝남, 2026-11-05 "다리 잘렸다")
        # 위치는 '분할 ∩ 새로 생긴 곳' 덩어리로 찾는다(분할 덩어리 통째로 쓰면 부스에 붙어 선 사람이 부스와 한 덩어리가 돼 빠짐
        #   — 2026-11-06 Kofpi 부스 5명 중 4명 누락). 어두운 구두가 '새로 생긴 곳'에서 빠져도 괜찮다: 박스 아래 여유 + 박스별
        #   덩어리 선택(아래)이 발까지 통째로 가져온다(2026-11-05 "다리 잘렸다").
        ds = cv2.dilate(diff_strong.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
        new = (segf & ds).astype(np.uint8)
        # 얇은 가로 띠(배경 밑선·몰딩 차이)를 먼저 깎는다 — 사람과 이어지면 한 덩어리가 돼 가로 덩어리 조건에 사람까지 빠졌다(2026-11-06)
        new = cv2.morphologyEx(new, cv2.MORPH_OPEN, np.ones((max(25, h // 30), 1), np.uint8))
        new = cv2.morphologyEx(new, cv2.MORPH_CLOSE, np.ones((25, 7), np.uint8))
        n0, lab0, st0, _ = cv2.connectedComponentsWithStats(new)
        for j in range(1, n0):
            x, y, bw, bh, area = st0[j]
            if area < max(2500, h * w * 0.0007) or bh < 60: continue
            if bh < bw * 0.6: continue
            if bw < bh * 0.15: continue   # 세로로 가는 띠 = 기둥 모서리(2026-11-06 "왜 자꾸 블럭을 틀어버려": 생성 모델이 다시 그린 블럭 기둥 옆면을 사람으로 붙임)   # 가로로 긴 덩어리 = 사람이 아님(2026-11-06: 배경 밑선 수정 뒤 후보와 달라진 부스 밑단 띠를 사람으로 잡음)
            mx, my = int(bw * 0.06) + 4, int(bh * 0.03) + 8
            bx1, by1, bx2, by2 = max(0, x - mx), max(0, y - my), min(w, x + bw + mx), min(h, y + bh + my + int(bh * 0.06))
            spec = f"{bx1},{by1},{bx2},{by2}"
            if occ is not None:
                band = occ[max(by1, by2 - max(6, int(bh * 0.05))):by2, bx1:bx2]
                if band.size and band.mean() > 0.35: spec += ":behind"
            a.box.append(spec); print("AUTO_BOX " + spec)
    if not a.box:
        print("PEOPLE_FAIL 박스 없음(--box 또는 --auto-boxes)"); sys.exit(1)
    people = np.zeros((h, w), np.float32); zones = np.zeros((h, w), np.uint8); shadow_z = np.zeros((h, w), np.uint8); ground_z = []
    ids = np.zeros((h, w), np.uint8)   # 사람별 번호 지도 — 붙어 선 사람을 한 덩어리로 다루지 않게(2026-11-06 부스1 스태프+남성)
    lockm = cv2.resize(load(a.lock, "L"), (w, h), interpolation=cv2.INTER_NEAREST) > 127 if a.lock else None
    report, bad, persons, holes, floats, sheet_boxes = [], [], [], [], [], []
    for i, spec in enumerate(a.box, 1):
        coords, *flags = spec.split(":")
        x1, y1, x2, y2 = [int(v) for v in coords.split(",")]
        behind = "behind" in flags; edge = "edge" in flags   # edge = 프레임 끝 근경 행인(키·그림자 검사 생략)
        dy = next((int(f[3:]) for f in flags if f.startswith("dy=")), 0)
        dx = next((int(f[3:]) for f in flags if f.startswith("dx=")), 0)
        s_box = next((float(f[2:]) for f in flags if f.startswith("s=")), None)  # 박스별 배율(발 고정) — 손을 상판 높이에 맞출 때만 소폭  # 가림막 끝 밖으로 몸이 나가 잘릴 때 안쪽으로  # 가림막 뒤 사람 세로 이동(px, 위로 = 음수)
        px = int((x2 - x1) * 0.6); py = int((y2 - y1) * 0.06)   # 옆 여유 0.6 — 0.25 는 뻗은 손을 잘랐다(2026-11-06 스태프 손)
        # 아래로 키 60% 더 본다(잠금 구역 밖만) — 어두운 다리가 '새로 생긴 곳'에서 빠져 상반신만 박스가 잡혔다(2026-11-06 부스2 걸어오는 남성)
        ext = 0 if behind else int((y2 - y1) * 0.6)
        X1, Y1, X2, Y2 = max(0, x1 - px), max(0, y1 - py), min(w, x2 + px), min(h, y2 + py + ext)
        seg = np.asarray(remove(Image.fromarray(cw[Y1:Y2, X1:X2]), session=sess, only_mask=True, post_process_mask=True)).astype(np.float32) / 255
        # ':nodiff' = 옷 색이 뒤 배경과 비슷해 '원본과 달라진 곳' 조건이 몸을 잘라먹을 때(2026-11-05 남색 정장 연설자 다리 사라짐)
        # 덩어리 단위 선택: 박스 안에 반 이상 들어오고(이웃 사람 제외) 원본과 달라진 비율이 있는(원본에 있던 사람 제외) 분할 덩어리만.
        # 픽셀 단위 'seg × 달라진 곳' 과 박스 테두리 흐림은 금지 — 옷·구두가 배경과 비슷하면 다리·발이 잘린다(2026-11-05 두 번 반려).
        box = np.zeros_like(seg); box[y1 - Y1:y2 - Y1, x1 - X1:x2 - X1] = 1
        if ext:
            ex = np.zeros_like(seg); ex[y2 - Y1:, x1 - X1:x2 - X1] = 1
            if lockm is not None: ex *= ~lockm[Y1:Y2, X1:X2]
            box = np.maximum(box, ex)
        dm = dmask[Y1:Y2, X1:X2] > 0
        nseg, lseg, _, _ = cv2.connectedComponentsWithStats((seg > 0.5).astype(np.uint8))
        keep = np.zeros_like(seg, dtype=np.uint8)
        bx_core = np.zeros_like(seg, dtype=bool); bx_core[y1 - Y1:y2 - Y1, x1 - X1:x2 - X1] = True
        for j in range(1, nseg):
            c = lseg == j
            if not ('nodiff' in flags or dm[c].mean() > 0.15): continue
            if box[c].mean() > 0.5: keep[c] = 1
            elif (c & bx_core).sum() > 0.25 * bx_core.sum():
                # 붙어 선 두 사람이 한 덩어리로 분할되면 큰 쪽 박스만 가져가 다른 사람이 통째로 빠졌다(2026-11-06 부스1 스태프)
                #   → 덩어리가 이 박스를 크게 덮으면 이 박스 범위만큼 잘라 이 사람 것으로
                keep[c & bx_core] = 1
        m = seg * cv2.dilate(keep, np.ones((7, 7), np.uint8))
        if edge:  # 초점 나간 근경 행인은 분할 모델이 못 잡는다(2026-11-05 실측 0px) → 원본과 달라진 덩어리를 메워 부드럽게
            dz = diff_strong[Y1:Y2, X1:X2].astype(np.uint8) * (box > 0)
            dz = cv2.morphologyEx(dz, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
            n3, lab3, st3, _ = cv2.connectedComponentsWithStats(dz)
            if n3 > 1:
                big = 1 + int(np.argmax(st3[1:, 4])); dz = (lab3 == big).astype(np.uint8)
                cnts, _ = cv2.findContours(dz, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); cv2.drawContours(dz, cnts, -1, 1, -1)
                m = cv2.GaussianBlur(cv2.erode(dz, np.ones((7, 7), np.uint8)).astype(np.float32), (0, 0), 4)
        if behind and occ is not None and not dy:  # dy 로 옮길 사람은 옮긴 뒤 합성 단계에서 가린다(먼저 자르면 손·태블릿이 잘림)
            m[occ[Y1:Y2, X1:X2]] = 0
        mb = (m > 0.5).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(mb)
        if n > 1:  # 부스러기만 버린다 — '가장 큰 덩어리만'은 한 박스에 선 두 번째 사람을 지웠다(2026-11-06 Kofpi 스태프 누락)
            big = st[1:, 4].max(); keep = np.isin(lab, [j for j in range(1, n) if st[j, 4] >= max(800, big * 0.08)]).astype(np.uint8)
            m *= cv2.dilate(keep, np.ones((7, 7), np.uint8))
        people[Y1:Y2, X1:X2] = np.maximum(people[Y1:Y2, X1:X2], m)
        sub = ids[Y1:Y2, X1:X2]; sub[(m > 0.5) & (sub == 0)] = i
        zones[Y1:Y2, X1:X2] = 1
        ys, xs = np.where(m > 0.5)
        top, feet = (int(Y1 + ys.min()), int(Y1 + ys.max())) if len(ys) else (y1, y2)
        line = f"#{i} box={x1},{y1},{x2},{y2} top={top} feet={feet} px={len(ys)}"
        # 구멍 검사: 사람 윤곽 안쪽 작은 오목부(닫힘 반경 4% 키)인데 원본과 크게 달라졌는데 마스크에 없는 픽셀 = 빠진 손·물건.
        #   볼록 껍질로 재면 팔과 몸 사이·다리 사이(진짜 배경)까지 잡혀 오탐 — 2026-11-05 실측.
        mb2 = (m > 0.5).astype(np.uint8)
        if mb2.any():
            r2 = max(3, int((y2 - y1) * 0.04))
            closed = cv2.morphologyEx(mb2, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r2 + 1, 2 * r2 + 1)))
            miss = closed.astype(bool) & diff_strong[Y1:Y2, X1:X2] & (mb2 == 0)
            if behind and occ is not None: miss &= ~occ[Y1:Y2, X1:X2]
            miss = cv2.morphologyEx(miss.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
            hole = int(miss.sum()); line += f" hole={hole}"
            if hole > 0.015 * mb2.sum(): holes.append(i)
        if not behind and not edge:
            hh = feet - top
            shadow_z[max(0, feet - int(hh * .06)):min(h, feet + int(hh * .07)), max(0, x1 - int(hh * .12)):min(w, x2 + int(hh * .12))] = 1
            ground_z.append((feet, hh, x1, x2))
            if a.k and a.yh is not None:
                exp = a.k * (feet - a.yh); err = hh / exp - 1
                line += f" height={hh} expected={exp:.0f} err={err:+.1%}"
                if abs(err) > 0.05 and a.strict_scale: bad.append(i)
                elif abs(err) > 0.05: line += ' (scale_warn)'
        else:
            line += " (behind" + (f", dy={dy}" if dy else "") + ")" if behind else " (edge)"
        s_fix = s_box if s_box else 1.0
        if not behind and not edge and a.k and a.yh is not None and a.fix_scale and len(ys):
            s_fix = a.k * (feet - a.yh) / max(1, feet - top); line += f" -> scaled x{s_fix:.3f}"
            if i in bad: bad.remove(i)
        persons.append((feet, behind, X1 + dx, Y1 + dy, cw[Y1:Y2, X1:X2].copy(), m.copy(), s_fix, (x1 + x2) / 2 + dx, edge, i))
        report.append(line)

    lb = cv2.GaussianBlur(base.astype(np.float32).mean(2), (0, 0), 6) + 4
    lc = cv2.GaussianBlur(cw.astype(np.float32).mean(2), (0, 0), 6) + 4
    sz = cv2.GaussianBlur(shadow_z.astype(np.float32), (0, 0), 12)
    shade = 1 - (1 - np.clip(lc / lb, 0.45, 1.0)) * sz * (1 - people)
    res = base.astype(np.float32) * shade[..., None]
    gal = np.zeros((h, w), np.float32)
    lock_m = cv2.resize(load(a.lock, "L"), (w, h), interpolation=cv2.INTER_NEAREST) > 127 if a.lock else None
    if a.ground and ground_z and a.fix_scale is False:
        # 2026-11-06 "왜 매번 사람이 붕 떠 있어, 잘라 붙인 거 같아": 생성 모델이 그린 접지 그림자·유광 바닥 반사를 버리고
        #   사람 윤곽만 붙여서 반사 바닥 위 사람만 반사가 없었다 → 발밑 구역(아래로 키 60%, 좌우 키 15%)에서 후보와 원본의
        #   차이(흐림 3px, 6~28 사이 부드럽게)만큼 후보 픽셀을 그대로 옮긴다. 무광 카펫은 차이가 그림자뿐이라 자동으로 그림자만 온다.
        #   잠금 마스크(--lock) 안은 접지띠(발 ±6%)만. 키 보정(--fix-scale)과는 같이 못 쓴다(사람만 옮겨지고 반사는 제자리).
        zone = np.zeros((h, w), np.float32)
        lock = lock_m if lock_m is not None else np.zeros((h, w), bool)
        for feet, hh, x1, x2 in ground_z:
            zx1, zx2 = max(0, x1 - int(hh * .15)), min(w, x2 + int(hh * .15))
            z = np.zeros((h, w), np.float32); z[max(0, feet - int(hh * .06)):min(h, feet + int(hh * .6)), zx1:zx2] = 1
            band = np.zeros((h, w), np.float32); band[max(0, feet - int(hh * .06)):min(h, feet + int(hh * .06)), zx1:zx2] = 1
            # 잠금 구역(부스 카펫) 위에 선 사람은 발밑 띠만 — 카펫 밖 홀 바닥까지 옮기면 옛 배경으로 만든 후보의 몰딩·반사가
            #   다시 들어와 부스 바닥판이 비뚤어 보였다(2026-11-06 "왜 자꾸 블럭을 틀어버려", 스태프 발밑).
            fxc = min(w - 1, max(0, (x1 + x2) // 2)); on_lock = lock[min(h - 1, feet + 3), fxc]
            zone = np.maximum(zone, band * lock if on_lock else np.where(lock, band, z))   # 띠도 카펫 안으로만
        zone = cv2.GaussianBlur(zone, (0, 0), 10)
        dg = np.abs(cv2.GaussianBlur(cw.astype(np.float32), (0, 0), 3) - cv2.GaussianBlur(base.astype(np.float32), (0, 0), 3)).max(2)
        gal = np.clip((dg - 6) / 22, 0, 1) * zone
        gal = cv2.GaussianBlur(gal, (0, 0), 2)
        res = cw.astype(np.float32) * gal[..., None] + base.astype(np.float32) * (1 - gal[..., None])
        zones |= (gal > 0.02).astype(np.uint8)
    # 사람별로 합성(뒤 → 앞). --fix-scale 이면 발끝 점을 고정하고 확대
    acc_rgb = np.zeros((h, w, 3), np.float32); acc_a = np.zeros((h, w), np.float32)
    for feet, behind, X1, Y1, crop, m, sf, fx, edge, pid in sorted(persons, key=lambda t: (not t[1], t[0])):
        T = np.float32([[sf, 0, X1 * sf + fx * (1 - sf)], [0, sf, Y1 * sf + feet * (1 - sf)]])
        lay = cv2.warpAffine(crop.astype(np.float32), T, (w, h), flags=cv2.INTER_CUBIC)
        al = cv2.GaussianBlur(cv2.warpAffine(m, T, (w, h), flags=cv2.INTER_LINEAR), (0, 0), 0.8)
        if behind and occ is not None: al[occ] = 0
        # 공중부양은 수치로 못 잡았다(2026-11-05: 꽃·테이블이 옷단을 가려 '지지'로 보임, 실측 5건 중 2건 놓침) → 사람별 아랫단 확대 시트를 남겨 눈으로 본다
        v = al > 0.5
        if v.any():
            ys_, xs_ = np.where(v); hb = ys_.max() - ys_.min()
            sheet_boxes.append((pid, max(0, xs_.min() - 40), max(0, ys_.max() - int(hb * 0.45)), min(w, xs_.max() + 40), min(h, ys_.max() + 60)))
        if a.finish:
            # 후보 그림자를 이미 옮긴 사람(유광 바닥)은 합성 그림자를 빼고, 발밑에 옮겨진 게 약한 사람(카펫·잠금 구역)은 넣는다 — 사람마다 판정
            lay, res = photo_finish(lay, al, res, (feet - Y1) * sf if not behind else 400, not behind and not edge, feet, fx, gal, lock_m)
        res = lay * al[..., None] + res * (1 - al[..., None])
        acc_rgb = lay * al[..., None] + acc_rgb * (1 - al[..., None]); acc_a = al + acc_a * (1 - al)
        zones |= cv2.dilate((al > 0.02).astype(np.uint8), np.ones((5, 5), np.uint8))
    res = np.clip(res, 0, 255).astype(np.uint8)
    rgb = np.where(acc_a[..., None] > 1e-3, acc_rgb / np.maximum(acc_a[..., None], 1e-3), 0)
    alpha = acc_a[..., None]; cw = np.clip(rgb, 0, 255).astype(np.uint8); people = acc_a
    outside = (cv2.dilate(zones, np.ones((25, 25), np.uint8)) == 0) & (shade > 0.999)
    od_v = float(np.abs(res.astype(int) - base.astype(int)).mean(2)[outside].mean())
    Image.fromarray(np.dstack([cw, (alpha[..., 0] * 255).astype(np.uint8)]), "RGBA").save(od / "people_layer.png")
    Image.fromarray((shade * 255).astype(np.uint8)).save(od / "shadow_layer.png")
    Image.fromarray((people * 255).astype(np.uint8)).save(od / "people_mask.png")
    Image.fromarray(ids).save(od / "people_ids.png")
    Image.fromarray(res).save(od / "people_final.png")
    # 확인 시트: 사람마다 아랫단(발·옷단·가림막 경계) 확대 — 공중부양·다리 잘림은 이것으로 본다(납품 전 필수)
    tiles = []
    for pid, x0, y0, x1, y1 in sheet_boxes:
        t = Image.fromarray(res[y0:y1, x0:x1]); t.thumbnail((360, 360)); tiles.append((pid, t))
    if tiles:
        from PIL import ImageDraw
        sw = sum(t.width for _, t in tiles) + 10 * len(tiles); sh = max(t.height for _, t in tiles) + 24
        sheet = Image.new("RGB", (sw, sh), "black"); d = ImageDraw.Draw(sheet); x = 0
        for pid, t in tiles:
            sheet.paste(t, (x, 24)); d.text((x + 4, 4), f"#{pid}", fill=(255, 255, 0)); x += t.width + 10
        sheet.save(od / "check_feet.jpg", quality=88)
    print("\n".join(report))
    tok = "PEOPLE_HOLE_FAIL" if holes else ("PEOPLE_FLOAT_FAIL" if floats else ("PEOPLE_SCALE_FAIL" if bad else "PEOPLE_OK"))
    print(f"{tok} inliers={int(inl.sum())} rms={rms:.2f} outside_diff={od_v:.3f}" + (f" scale_bad={bad}" if bad else "") + (f" holes={holes}" if holes else "") + (f" floats={sorted(set(floats))}" if floats else ""))
    sys.exit(3 if holes else (4 if floats else (2 if bad else 0)))


if __name__ == "__main__":
    main()

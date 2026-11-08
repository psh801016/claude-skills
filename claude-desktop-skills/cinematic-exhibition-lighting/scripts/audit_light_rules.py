# 사용자 반려 규칙을 저장된 조명판·빔 장부에서 자동으로 잡는다 — 통과 못 하면 납품 금지.
# 배경: 2026-11-05 KOBC 컨퍼런스 조명이 하루에 5번 반려됐다. 규칙은 SKILL.md 에 있었는데 즉석 코드가 지키지 않았다.
#   ① "무대만 빔이 가냐" / "객석에 조명이 묻어야"  → 객석(물건 마스크) 수광 비율이 낮으면 실패
#   ② "무대 조명 이상해"(한 점 수렴·X자 교차)       → 장부의 착지점이 겹치거나, 빔끼리 LED·무대 중앙에서 교차하면 실패
#   ③ "실 조명에 맞게"(사진에 없는 기구에서 출발)   → 장부의 광원 좌표 주변이 평평한 천장·벽이면 실패
#   ④ "굴곡에 맞게 꺾이고 실루엣"                   → 의자 뒷면(카메라 쪽 면)이 테이블 윗면만큼 밝으면 실패
#   ⑤ "고보 딱 떨어져 인위적" ↔ "너무 뭉갰어"      → 고보 가장자리 기울기가 띠(0.075~0.16) 밖이면 실패
#   ⑥ "빛줄기가 너무 얄상해"                       → 빔 능선 두께 12px 미만이면 실패
# 사용: python audit_light_rules.py --plate 조명판.png --obj-mask 물건.png --src 원본.png --ledger ledger.json
#          [--gobo L6.png] [--beams L4.png] [--floor-y 812]
# 성공 토큰: AUDIT_PASS   실패: AUDIT_FAIL <사유들> (exit 1)
import argparse, json, sys
from pathlib import Path
import numpy as np, cv2
from PIL import Image


def gray(p, size=None):
    im = Image.open(p).convert("RGB")
    if size and im.size != size:
        im = im.resize(size)
    return np.asarray(im).max(2).astype(np.float32)


def seg_cross(a, b, c, d):
    """선분 ab, cd 교점(없으면 None)."""
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = a, b, c, d
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-6:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den
    if 0.02 < t < 0.98 and 0.02 < u < 0.98:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--plate", required=True)
    ap.add_argument("--obj-mask", required=True)
    ap.add_argument("--src", help="원본(베이스 전) 사진 — 테이블 윗면·기구 판별용")
    ap.add_argument("--ledger", help="빔 장부 json: beams[{S,L}], audience[{S,L}], led[[x1,y1,x2,y2]], deck_y")
    ap.add_argument("--gobo")
    ap.add_argument("--beams")
    ap.add_argument("--floor-y", type=int, default=0)
    a = ap.parse_args()
    # 기준값은 thresholds.json 에서 읽는다(현장마다 보정 기록을 남긴다). 없으면 KOBC 2026-11-05 값.
    TH = {"audience_lit": 0.12, "landing_dist": 60, "deck_span": 0.35, "source_std": 12, "face_top": 0.35,
          "sticker_edge": 0.12, "shading_corr": 0.70, "gobo_max": 0.16, "gobo_min": 0.075, "beam_width": 12}
    tp = Path(__file__).with_name("thresholds.json")
    if tp.exists():
        TH.update({k: v for k, v in json.loads(tp.read_text(encoding="utf-8")).items() if not k.startswith("_")})
    plate = gray(a.plate); H, W = plate.shape
    obj = gray(a.obj_mask, (W, H)) > 127
    obj[: a.floor_y] = False
    fails, info = [], []
    srcg = cv2.cvtColor(np.asarray(Image.open(a.src).convert("RGB").resize((W, H))), cv2.COLOR_RGB2GRAY).astype(np.float32) if a.src else None

    # ① 객석 수광: 물건(테이블·의자) 픽셀 중 빛을 받는 비율
    if obj.any():
        frac = float((plate[obj] > 6).mean())
        info.append(f"audience lit={frac:.2f}")
        if frac < TH['audience_lit']:
            fails.append(f"객석에 빛이 안 묻음(수광 비율 {frac:.2f} < 0.12) — 바깥 무빙→객석 풀, LED 번짐을 뒤 줄까지")

    # ② 수렴·교차 / ③ 실제 기구 출발 — 빔 장부
    if a.ledger:
        led = json.loads(open(a.ledger, encoding="utf-8").read())
        beams = led.get("beams", []); rects = led.get("led", []); dy = led.get("deck_y", [0, 0])
        L = [tuple(b["L"]) for b in beams]
        for i in range(len(L)):
            for j in range(i + 1, len(L)):
                if np.hypot(L[i][0] - L[j][0], L[i][1] - L[j][1]) < TH['landing_dist']:
                    fails.append(f"착지점 수렴: 빔{i}·빔{j} 착지 거리 {np.hypot(L[i][0]-L[j][0], L[i][1]-L[j][1]):.0f}px < 60 — 착지를 흩는다"); break
        xs = []
        for i in range(len(beams)):
            for j in range(i + 1, len(beams)):
                if abs(beams[i]["S"][1] - beams[j]["S"][1]) > 60:
                    continue  # 다른 바(천장 무빙 vs 무대 파이프)끼리 화면 앞에서 지나치는 건 실제 리그에서 흔하다
                p = seg_cross(beams[i]["S"], beams[i]["L"], beams[j]["S"], beams[j]["L"])
                if p is None:
                    continue
                if any(x1 <= p[0] <= x2 and y1 <= p[1] <= y2 for x1, y1, x2, y2 in rects):
                    xs.append((i, j, p))
        if xs:
            i, j, p = xs[0]
            fails.append(f"같은 바 빔끼리 LED 화면 앞 X자 교차: 빔{i}×빔{j} at ({p[0]:.0f},{p[1]:.0f}) — 화면 앞에서 교차 금지")
        deck = [b for b in beams if abs(b["L"][1] - dy[1]) <= 12]
        if len(deck) >= 3:
            span = max(b["L"][0] for b in deck) - min(b["L"][0] for b in deck)
            deck_w = led.get("deck_w", W * 0.55)
            info.append(f"deck span={span/deck_w:.2f}")
            if span < TH['deck_span'] * deck_w:
                fails.append(f"빔 {len(deck)}개가 무대 한 구역에 수렴(착지 폭 {span:.0f}px < 데크의 35%) — 좌·중·우로 흩는다")
        off = [i for i, b in enumerate(beams) if b["S"][1] < 0 and not b.get("evidence")]
        if off:
            fails.append(f"화면 밖 가상 광원 빔 {off} — 사진에 근거(evidence) 없는 앞트러스 키라이트 금지(2026-11-05 '회색 기둥' 반려)")
        if srcg is not None:
            flat = []
            for i, b in enumerate(beams + led.get("audience", [])):
                sx, sy = b["S"]
                if sy < 0:
                    continue  # 화면 밖 광원(E)은 검사 불가
                win = srcg[max(0, sy - 12): sy + 13, max(0, sx - 12): sx + 13]
                c = float(win.std())
                if c < TH['source_std']:
                    flat.append(f"({sx},{sy}) std={c:.1f}")
            info.append(f"sources={len(beams)+len(led.get('audience', []))}")
            if flat:
                fails.append("광원이 사진 속 기구 위에 없음(주변이 평평): " + ", ".join(flat[:3]) + " — 렌즈 좌표를 실측해 S 로")

    # ④ 가구 실루엣: 테이블 윗면 대비 카메라 쪽 면(의자 뒷면·드레이프)의 빛 비율
    if srcg is not None:
        hsv = cv2.cvtColor(np.asarray(Image.open(a.src).convert("RGB").resize((W, H))), cv2.COLOR_RGB2HSV)
        tabletop = obj & (hsv[..., 1] < 95) & (hsv[..., 2] > 55)
        seat = obj & ~tabletop
        face = seat & ~(seat & ~np.roll(seat, 10, axis=0))
        lit_top = tabletop & (plate > 3)
        if lit_top.sum() > 500:
            zone = cv2.dilate(lit_top.astype(np.uint8), np.ones((61, 61), np.uint8)) > 0
            r = plate[face & zone].mean() / max(plate[lit_top].mean(), 0.1)
            info.append(f"face/top={r:.2f}")
            if r > TH['face_top']:
                fails.append(f"가구 실루엣 없음(의자 뒷면/테이블 윗면 {r:.2f} > 0.35) — 윗면·윗선만 받고 카메라 쪽 면은 그늘")
            # 경계 계단(v7 보정): 원본에 모서리가 없는 평평한 곳에 빛의 급한 경계가 있으면 '스티커'.
            #   실제 물체 모서리(테이블 끝·의자 윗선)에서 빛이 끊기는 건 정상이므로 원본 기울기가 큰 곳은 제외한다.
            gn = plate / max(float(plate[lit_top].max()), 1.0)
            pm = np.hypot(cv2.Sobel(gn, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(gn, cv2.CV_32F, 0, 1, ksize=3)) / 8
            sg = cv2.GaussianBlur(srcg, (0, 0), 1.0) / 255
            sm = np.hypot(cv2.Sobel(sg, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(sg, cv2.CV_32F, 0, 1, ksize=3)) / 8
            near = cv2.dilate(lit_top.astype(np.uint8), np.ones((15, 15), np.uint8)).astype(bool) & obj
            flat = near & (sm < 0.02)
            if flat.sum() > 1000:
                q = float(np.quantile(pm[flat], 0.995))
                info.append(f"sticker edge={q:.3f}")
                if q > TH['sticker_edge']:
                    fails.append(f"객석 빛이 원본 굴곡과 무관한 경계를 가짐(평평한 면 위 빛 경계 {q:.3f} > 0.12) — 색 마스크 띠 금지, 원본 명암을 따라가게")

    # ④-2 굴곡 추종(v7, "아직도 실루엣 안 맞아" = 평평한 띠): 빛을 받은 가구 안에서 빛의 세부 변화가 원본 명암과 같이 움직여야 한다
    if srcg is not None:
        lit_obj = obj & (plate > 6)
        if lit_obj.sum() > 2000:
            hp = lambda x: x - cv2.GaussianBlur(x, (0, 0), 12)
            a_, b_ = hp(plate)[lit_obj], hp(srcg)[lit_obj]
            corr = float(np.corrcoef(a_, b_)[0, 1]) if a_.std() > 1e-3 and b_.std() > 1e-3 else 0.0
            info.append(f"shading corr={corr:.2f}")
            # 기준 0.70: 실측 2026-11-05 KOBC v6(색 마스크 띠, 반려)=0.61 / v7(명암 추종, 통과)=0.77 / v4=-0.03
            if corr < TH['shading_corr']:
                fails.append(f"객석 빛이 원본 굴곡을 안 따라감(세부 명암 상관 {corr:.2f} < 0.70) — 색 마스크 띠 금지, 원본 명암(위를 향한 면)을 곱한다")

    # ⑤ 고보 경계 띠: 너무 또렷(v4 0.18 반려) ↔ 너무 뭉갬(v5 0.067 반려)
    if a.gobo:
        g = gray(a.gobo, (W, H)); m = g.max()
        if m > 0:
            gn = g / m
            mag = np.hypot(cv2.Sobel(gn, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(gn, cv2.CV_32F, 0, 1, ksize=3)) / 8
            q = float(np.quantile(mag[g > 0], 0.995))
            info.append(f"gobo edge={q:.3f}")
            if q > TH['gobo_max']:
                fails.append(f"고보 경계가 너무 날카로움({q:.3f} > 0.16) — 블러 4~5px·핫스팟 감쇠·얼룩")
            elif q < TH['gobo_min']:
                fails.append(f"고보가 너무 뭉개짐({q:.3f} < 0.075) — 블러를 4~5px 로")

    # ⑥ 빔 굵기: 밝은 빔 영역의 능선(거리변환 극대) 평균 두께
    if a.beams:
        bb = gray(a.beams, (W, H))
        if (bb > 0).any():
            thr = max(6.0, float(bb.max()) * 0.25)
            bm = (bb > thr).astype(np.uint8)
            dist = cv2.distanceTransform(bm, cv2.DIST_L2, 5)
            ridge = (dist > 1.5) & (dist >= cv2.dilate(dist, np.ones((5, 5), np.uint8)) - 1e-3)
            if ridge.any():
                width = 2 * float(dist[ridge].mean())
                info.append(f"beam width={width:.1f}px")
                if width < TH['beam_width']:
                    fails.append(f"빔이 너무 가늘다(능선 두께 {width:.1f}px < 12) — 폭 ×1.8 + 헤이즈 외피")

    if fails:
        print("AUDIT_FAIL " + " | ".join(fails) + "  [" + ", ".join(info) + "]"); sys.exit(1)
    print("AUDIT_PASS " + ", ".join(info))


if __name__ == "__main__":
    main()

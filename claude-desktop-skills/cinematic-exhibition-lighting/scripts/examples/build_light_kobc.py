# 예제(2026-11-05 KOBC v7, 반려 점검표 통과본, AUDIT_PASS). 새 장면: SRC/_obj_mask 경로, LED 좌표, BEAMS·AUD·SPOTS 의 기구 렌즈 좌표(사진 실측), 고보 글자·벽 사다리꼴만 바꾼다.
# KOBC 컨퍼런스 조명 — cinematic-exhibition-lighting 계약대로 '보존 레이어'에서 합성본·조명판을 같이 만든다.
# 좌표는 2560x1440 실사본(05_실사_최종.png) 기준. 블렌드 = screen (b + (255-b)*p//255).
import hashlib, json
from pathlib import Path
import numpy as np, cv2
from PIL import Image

D = Path(__file__).parent
SRC = D.parent / "05_실사_최종.png"
src = np.asarray(Image.open(SRC).convert("RGB")).astype(np.float32)
H, W = src.shape[:2]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(7)

LED = [(968, 390, 1592, 786), (655, 430, 945, 790), (1617, 430, 1905, 790)]
led = np.zeros((H, W), np.float32)
for x1, y1, x2, y2 in LED:
    led[y1:y2, x1:x2] = 1

# 1) 베이스: 객석 조도만 0.62, LED 면은 원본 그대로
f = 0.68 + 0.32 * cv2.GaussianBlur(led, (0, 0), 1.5)  # 키노트 전 객석 디밍(리서치)
base = np.clip(src * f[..., None], 0, 255).astype(np.uint8)

def noise(scale, seed):
    n = np.random.default_rng(seed).random((H // scale + 2, W // scale + 2)).astype(np.float32)
    return cv2.resize(cv2.GaussianBlur(n, (0, 0), 1.2), (W, H), interpolation=cv2.INTER_CUBIC)

def u8(rgb_float):
    return np.clip(rgb_float, 0, 255).astype(np.uint8)

COOL = np.array([236, 243, 255], np.float32)
BLUE = np.array([70, 130, 255], np.float32)
VIOLET = np.array([190, 120, 255], np.float32)
AMBER = np.array([255, 168, 88], np.float32)

# 2) 빔 장부 — 2026-11-05 반려("무대만 빔이 가냐") 뒤 재설계: 천장바 무빙 4(교차) + 카메라 뒤 앞트러스 키 1
#    S=렌즈 중심(실측), L=착지 중심, 폭은 화면 픽셀(원근 포함), kind=deck(무대 데크)|floor(통로 카펫)
objm = np.asarray(Image.open(D.parent / "_obj_mask.png").convert("L").resize((W, H))) > 127
deck = ((yy >= 786) & (yy <= 799) & (xx >= 575) & (xx <= 1985)).astype(np.float32)
lip = ((yy > 799) & (yy <= 812) & (xx >= 575) & (xx <= 1985)).astype(np.float32)
aisle = cv2.GaussianBlur(((~objm) & (yy > 820)).astype(np.float32), (0, 0), 3)
chair = objm & (yy > 812)
rim = chair & ~np.roll(chair, 4, axis=0)  # 의자·테이블 윗선만
# v5(4차 반려 "굴곡에 맞게 빛이 꺾이고 실루엣이 나와야"): 수광면 지도
_hsv = cv2.cvtColor(src.astype(np.uint8), cv2.COLOR_RGB2HSV)
tabletop = objm & (_hsv[..., 1] < 95) & (_hsv[..., 2] > 55) & (yy > 820)   # 테이블 윗면
seat = objm & (yy > 812) & ~tabletop
seattop = seat & ~np.roll(seat, 10, axis=0)                                 # 등받이·드레이프 윗선
castshadow = (~objm) & np.roll(objm, 16, axis=0)                            # 빛이 무대 쪽에서 오므로 그림자는 카메라 쪽(아래)
carpet_lit = cv2.GaussianBlur(((~objm) & (yy > 820) & ~castshadow).astype(np.float32), (0, 0), 1.5)
def soft(m, open_k=3, sigma=2.5):  # v6: 문턱값 마스크의 톱니·점을 지우고 가장자리를 푼다(5차 반려 "의자 실루엣 이상")
    u = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((open_k, open_k), np.uint8))
    u = cv2.morphologyEx(u, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.GaussianBlur(u.astype(np.float32), (0, 0), sigma)
lum0 = cv2.cvtColor(src.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
shade = 0.45 + 1.4 * np.clip(lum0, 0, 0.6)   # 빛이 원본 명암(주름·굴곡)을 따라간다 — 평평한 스티커 금지
up = np.clip((lum0 - 0.07) / 0.33, 0, 1) ** 1.6                 # 원본에서 위 조명을 받아 밝은 면 = 위를 향한 면
RECV = soft(objm & (yy > 812), 3, 1.5) * up * 1.15 + carpet_lit * 0.32  # v7: 평평한 띠 금지, 굴곡 추종
# v4(2026-11-05 3차 반려 "실 조명에 맞게 은은하면서 멋지게"): 사진에 실제로 있는 기구만 쓴다.
#   FOH = 천장 조명바 흰 무빙(y127) → 데크 좌·중·우 분산(교차 없음), 은은한 쿨화이트
#   BACK = LED 위 무대 파이프 검정 기구(y370~385) → 데크로 짧게, 보라(사용자 레퍼런스), LED 앞은 55%
PALE = np.array([235, 238, 255], np.float32)
LAV = np.array([175, 145, 235], np.float32)  # Gemini 권고 톤다운 청보라
BEAMS = [  # S, L, 시작폭, 끝폭, 세기, 색
    ((455, 127), (1000, 793), 6, 52, 0.40, PALE),
    ((830, 127), (1215, 793), 6, 50, 0.55, PALE),
    ((2120, 127), (1590, 793), 6, 52, 0.45, PALE),
    ((790, 385), (695, 793), 5, 40, 0.50, LAV),
    ((955, 378), (1075, 793), 5, 42, 0.60, LAV),
    ((1615, 372), (1490, 793), 5, 42, 0.50, LAV),
    ((1805, 376), (1915, 793), 5, 40, 0.42, LAV),
]
shafts = np.zeros((H, W, 3), np.float32)
land = np.zeros((H, W, 3), np.float32)
for i, ((sx, sy), (lx, ly), w0, w1, k, col) in enumerate(BEAMS):
    v = np.array([lx - sx, ly - sy], np.float32); L = np.hypot(*v); v /= L
    t = ((xx - sx) * v[0] + (yy - sy) * v[1]) / L
    d = np.abs((xx - sx) * v[1] - (yy - sy) * v[0])
    w = 1.8 * (w0 + (w1 - w0) * np.clip(t, 0, 1))
    inside = (t >= 0) & (t <= 1)
    along = (1 - 0.55 * t) * np.clip(t / 0.02, 0, 1)
    prof = np.exp(-2.0 * (d / w) ** 2) * (0.6 + 0.4 * np.exp(-7 * (d / w) ** 2)) + 0.35 * np.exp(-0.5 * (d / (2.2 * w)) ** 2) * np.clip(1 - d / (3.5 * w), 0, 1)
    dens = np.where(inside, along, 0) * prof * (0.65 + 0.7 * noise(60, 11 + i))
    dens = np.where(led > 0, dens * 0.55, dens)  # 밝은 LED 앞에서는 산란광 대비가 준다
    shafts += dens[..., None] * col * 0.55 * k
    glow = np.exp(-((xx - sx) ** 2 + (yy - sy) ** 2) / (2 * 7 ** 2))
    shafts += glow[..., None] * col * 0.9 * k
    e = np.exp(-(((xx - lx) / (w1 * 1.1)) ** 2) * 1.6)
    land += (e * deck * 0.42 + e * lip * np.exp(-np.maximum(yy - 799, 0) / 4) * 0.10)[..., None] * col * k

# 무대 키 워시(빔 없음): 가운데 강연 구역 중심 가우시안
wash = np.exp(-((xx - 1280) / 420) ** 2)
land += (cv2.GaussianBlur(deck, (0, 0), 2) * wash * 0.26)[..., None] * np.array([255, 244, 228], np.float32)

# 벽 스캘럽: 벽 쪽 천장 트랙 스팟(실측) 아래로 떨어지는 따뜻한 빛 자국, 은은하게
SPOTS = [(255, 215), (365, 262), (435, 288), (2310, 212), (2195, 258), (2130, 284)]
scal = np.zeros((H, W), np.float32)
for sx, sy in SPOTS:
    dy = yy - (sy + 8)
    wx = 8 + 0.32 * np.maximum(dy, 0)
    scal += np.where(dy > 0, np.exp(-((xx - sx) / wx) ** 2 * 1.5) * np.exp(-dy / 210) * np.clip(dy / 40, 0, 1), 0)
scal_l = (np.clip(scal, 0, 1) * 0.20)[..., None] * np.array([255, 222, 186], np.float32)


# 객석에 묻는 빛(사용자 "객석쪽에서 조명이 묻어서"): 천장바 바깥 무빙 2대가 객석으로 은은한 풀 + LED 번짐을 뒤쪽 줄까지
AUD = [  # S, 풀 중심, rx, ry, 세기, 색
    ((275, 127), (560, 1040), 260, 70, 0.55, LAV),
    ((2295, 127), (2010, 990), 240, 62, 0.45, LAV),
    ((655, 128), (930, 1290), 300, 90, 0.35, PALE),
]
aud = np.zeros((H, W, 3), np.float32)
for i, ((sx, sy), (lx, ly), rx, ry, k, col) in enumerate(AUD):
    v = np.array([lx - sx, ly - sy], np.float32); L = np.hypot(*v); v /= L
    t = ((xx - sx) * v[0] + (yy - sy) * v[1]) / L
    d = np.abs((xx - sx) * v[1] - (yy - sy) * v[0])
    w = 10 + (rx * 0.75 - 10) * np.clip(t, 0, 1)
    dens = np.where((t >= 0) & (t <= 1), (1 - 0.75 * t) * np.clip(t / 0.02, 0, 1) * np.clip((1.0 - t) / 0.3, 0, 1), 0) * np.exp(-2.0 * (d / w) ** 2)
    dens = dens * (0.65 + 0.7 * noise(60, 31 + i)) + 0.35 * np.where((t >= 0) & (t <= 1), 1 - 0.75 * t, 0) * np.exp(-0.5 * (d / (2.2 * w)) ** 2) * np.clip(1 - d / (3.5 * w), 0, 1)
    dens *= 1 - 0.75 * soft(seat & ~seattop, 3, 3.0) * np.clip((t - 0.65) / 0.2, 0, 1)  # 착지 근처는 의자가 빛줄기를 가린다(경사)
    aud += dens[..., None] * col * 0.60 * k
    aud += np.exp(-((xx - sx) ** 2 + (yy - sy) ** 2) / (2 * 7 ** 2))[..., None] * col * 0.9 * k
    e = np.exp(-((xx - lx) / rx) ** 2 - ((yy - ly) / ry) ** 2)
    e = np.clip((e - 0.03) / 0.97, 0, 1)  # 긴 꼬리 제거(빛 풀은 경계가 있다)
    recv = RECV * (0.75 + 0.5 * noise(25, 41 + i))  # 수광면 지도 + 무빙 렌즈 브레이크업
    aud += (e * recv * 1.25 * k)[..., None] * col

# 2-1) 객석 위 공기 헤이즈(중간) — 바닥 가까이·천장 모서리로 갈수록 0
vy = np.clip((yy - 110) / 240, 0, 1) * np.clip((1000 - yy) / 260, 0, 1)
hx = 0.55 + 0.45 * np.exp(-((xx - 1280) / 900) ** 2)
haze = (0.07 * vy * hx * (0.55 + 0.9 * noise(90, 3)))[..., None] * np.array([205, 214, 235], np.float32)


# 2-2) 좌우 벽 고보 "KOBC 2026"(사용자 레퍼런스: 앰버 원형 고보, 글자 밝게) — 화면 밖 앞트러스 투사, 벽 원근(소실점 1280,650)에 맞춰 붙임
from PIL import ImageDraw, ImageFont
_r = np.hypot(*np.mgrid[-300:300, -300:300]) / 300
radial = np.clip(1.0 - 0.45 * _r ** 2, 0, 1) + 0.12 * np.exp(-((_r - 1.0) / 0.12) ** 2)  # 핫스팟→가장자리 감쇠 + 렌즈 후광
def gobo_sheet(n=600):
    g = Image.new("L", (n, n), 0); dr = ImageDraw.Draw(g)
    dr.ellipse((40, 40, n - 40, n - 40), fill=60)
    f = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 150)
    for txt, y in (("KOBC", 120), ("2026", 300)):
        w = dr.textlength(txt, font=f); dr.text(((n - w) / 2, y), txt, font=f, fill=255)
    hole = Image.new("L", (n, n), 0); ImageDraw.Draw(hole).ellipse((40, 40, n - 40, n - 40), fill=255)
    g = Image.fromarray((np.asarray(g).astype(np.float32) * (np.asarray(hole) / 255)).astype(np.uint8))  # v7: 고보 구멍 밖 글자 금지
    return np.asarray(g.filter(__import__("PIL.ImageFilter", fromlist=["x"]).GaussianBlur(4.5))).astype(np.float32) / 255 * radial  # v6: 9→4.5 (v5 '너무 뭉개짐' 반려)
VP = (1280, 650)
def wall_quad(xn, xf, yt, yb):
    k = (VP[0] - xf) / (VP[0] - xn)
    return [(xn, yt), (xf, VP[1] + (yt - VP[1]) * k), (xf, VP[1] + (yb - VP[1]) * k), (xn, yb)]
sheet = gobo_sheet()
gobo = np.zeros((H, W), np.float32)
for xn, xf in ((80, 330), (2480, 2230)):
    q = wall_quad(xn, xf, 370, 790)
    src_q = np.float32([(0, 0), (600, 0), (600, 600), (0, 600)])
    if xn > xf:
        src_q = np.float32([(600, 0), (0, 0), (0, 600), (600, 600)])
    M = cv2.getPerspectiveTransform(src_q, np.float32(q))
    gobo = np.maximum(gobo, cv2.warpPerspective(sheet, M, (W, H)))
lum = cv2.cvtColor(src.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
alb = cv2.GaussianBlur(lum, (0, 0), 30); alb = np.clip(alb / max(float(alb[300:900, 0:400].mean()), 1e-3), 0.7, 1.3)  # 패널 단위 반사차, 나무결 없음
gobo_l = (gobo * 1.0 * alb * (0.85 + 0.3 * noise(35, 51)))[..., None] * AMBER

# 3) LED 짧은 번짐: 무대 데크·화면 사이 벽·앞줄 의자 윗선·무대 앞 카펫
dist = cv2.distanceTransform((1 - led).astype(np.uint8), cv2.DIST_L2, 5)
outside = 1 - led
ledcol = cv2.GaussianBlur(src * led[..., None], (0, 0), 25) / np.maximum(cv2.GaussianBlur(led, (0, 0), 25), 1e-3)[..., None]
halo = (np.exp(-dist / 16) * outside * 0.10)[..., None] * ledcol          # LED 앞 공기 헤이즈
wall = (np.exp(-dist / 22) * outside * (yy < 786) * 0.12)[..., None] * BLUE  # 화면 옆 벽·커튼
deckspill = ((deck * 0.20 + lip * np.exp(-np.maximum(yy - 799, 0) / 8) * 0.18) * ((xx > 640) & (xx < 1925)))[..., None] * BLUE

cx = np.exp(-((xx - 1280) / 700) ** 2)
chairs = (RECV * 0.40 * np.exp(-np.maximum(yy - 820, 0) / 130) * cx)[..., None] * BLUE
carpet_exposed = cv2.GaussianBlur(((~objm) & (yy > 870)).astype(np.float32), (0, 0), 6)
carpet = (carpet_exposed * np.exp(-np.maximum(yy - 870, 0) / 45) * 0.10 * np.exp(-((xx - 1280) / 260) ** 2))[..., None] * BLUE

layers = {
    "L1_led_spill_surfaces.png": u8(wall + deckspill + chairs + carpet),
    "L2_stage_landings.png": u8(land),
    "L3_led_foreground_haze.png": u8(halo),
    "L5_room_haze.png": u8(haze),
    "L6_wall_gobo_KOBC2026.png": u8(gobo_l),
    "L7_wall_scallops.png": u8(scal_l),
    "L8_audience_spill.png": u8(aud),
    "L4_beam_shafts.png": u8(shafts),
}
def screen(b, p):
    b = b.astype(np.int32); p = p.astype(np.int32)
    return (b + (255 - b) * p // 255)
plate = np.zeros((H, W, 3), np.int32)
for n, a in layers.items():
    Image.fromarray(a).save(D / n); plate = screen(plate, a)
plate = plate.astype(np.uint8)
comp = screen(base, plate).astype(np.uint8)
Image.fromarray(base).save(D / "base_dimmed.png")
Image.fromarray(plate).save(D / "KOBC_조명판.png")
Image.fromarray(comp).save(D / "KOBC_조명합성.png")

# 4) 판정 마스크(계획에서 독립 지정)
def save_mask(n, m):
    Image.fromarray((m.astype(np.uint8)) * 255).save(D / n)
core = np.zeros((H, W), bool)
for (sx, sy), (lx, ly), *_ in BEAMS:
    for t in np.linspace(0.12, 0.5, 80):
        y = int(sy + (ly - sy) * t); x = int(sx + (lx - sx) * t)
        if 0 <= y < H: core[y, x] = True
save_mask("m_beam_core.png", core)
lm = np.zeros((H, W), bool)
for _, (lx, ly), _, w1, *_ in BEAMS:
    lm[790:796, int(lx - w1 * 0.3):int(lx + w1 * 0.3)] = True
lm &= ~(objm & (yy > 812))
save_mask("m_stage_landing.png", lm)
ring = (dist >= 2) & (dist <= 6) & (yy < 780) & (yy > 440)
save_mask("m_led_haze.png", ring)
gm = cv2.erode((gobo > 0.9).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
save_mask("m_gobo_text.png", gm)
unlit = np.zeros((H, W), bool); unlit[0:50, 0:350] = True; unlit[0:50, 2210:] = True; unlit[1300:, 0:250] = True
save_mask("m_unlit.png", unlit)

sha = lambda n: hashlib.sha256((D / n).read_bytes()).hexdigest()
names = ["base_dimmed.png", *layers, "m_beam_core.png", "m_stage_landing.png", "m_led_haze.png", "m_gobo_text.png", "m_unlit.png"]
man = {"canvas": [W, H], "mode": "screen", "base": "base_dimmed.png", "composite": "KOBC_조명합성.png",
       "plate": "KOBC_조명판.png", "source_layers": list(layers), "sha256": {n: sha(n) for n in names},
       "required_effects": [{"name": "beam shafts", "mask": "m_beam_core.png", "min_value": 12},
                            {"name": "stage and aisle landings", "mask": "m_stage_landing.png", "min_value": 15},
                            {"name": "LED foreground haze", "mask": "m_led_haze.png", "min_value": 6},
                            {"name": "wall gobo KOBC 2026", "mask": "m_gobo_text.png", "min_value": 40}],
       "unlit_mask": "m_unlit.png"}
(D / "pair.json").write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
# 빔 장부(ledger) — audit_light_rules.py 가 수렴·X교차·실제 기구 출발·객석 수광을 검사한다
ledger = {"led": LED, "deck_y": [786, 799], "floor_y": 812,
          "beams": [{"S": [int(sx), int(sy)], "L": [int(lx), int(ly)], "w1": int(w1), "k": float(k)} for (sx, sy), (lx, ly), w0, w1, k, col in BEAMS],
          "audience": [{"S": [int(sx), int(sy)], "L": [int(lx), int(ly)], "rx": int(rx), "k": float(k)} for (sx, sy), (lx, ly), rx, ry, k, col in AUD]}
(D / "ledger.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=1), encoding="utf-8")
print("BUILD_OK", W, H)

# 레이더 워크숍 연회장(호텔 볼룸, 원형 테이블) 조명 — 2026-11-09 사용자 "이대로 확정". 연회장 기본 출발 예제.
# 좌표 = Downloads 레이더워크숍_연회장_실사화.png(2560x1440) 실측. 2026-11-09 사용자 "조명스킬사용 / 이미지 만들라고".
import hashlib, json
from pathlib import Path
import numpy as np, cv2
from PIL import Image

D = Path(__file__).parent
src8 = np.asarray(Image.open(D / "src.png").convert("RGB"))
H, W = src8.shape[:2]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

src = src8.astype(np.float32)  # 실사화 완료본(2560 원본) 그대로


def noise(scale, seed):
    n = np.random.default_rng(seed).random((H // scale + 2, W // scale + 2)).astype(np.float32)
    return cv2.resize(cv2.GaussianBlur(n, (0, 0), 1.2), (W, H), interpolation=cv2.INTER_CUBIC)


def u8(a):
    return np.clip(a, 0, 255).astype(np.uint8)


def soft(m, open_k=3, sigma=2.5):
    u = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((open_k, open_k), np.uint8))
    u = cv2.morphologyEx(u, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.GaussianBlur(u.astype(np.float32), (0, 0), sigma)


LED = [(864, 499, 1692, 911)]
BANNER = [(305, 612, 623, 954), (630, 554, 858, 926), (1699, 554, 1924, 926), (1933, 614, 2249, 954)]  # 인쇄 배너(발광 아님)
ban = np.zeros((H, W), np.float32)
for x1, y1, x2, y2 in BANNER:
    ban[y1:y2, x1:x2] = 1
led = np.zeros((H, W), np.float32)
for x1, y1, x2, y2 in LED:
    led[y1:y2, x1:x2] = 1
DECK_Y = (922, 946)
deck = ((yy >= DECK_Y[0]) & (yy <= DECK_Y[1]) & (xx >= 565) & (xx <= 1990)).astype(np.float32) * (1 - led) * (1 - ban)  # 배너 글자에 스팟을 얹지 않는다
lip = ((yy > DECK_Y[1]) & (yy <= 1016) & (xx >= 565) & (xx <= 1990)).astype(np.float32)  # 무대 앞 검정 단 앞면
lum0 = cv2.cvtColor(src.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
hsv = cv2.cvtColor(src.astype(np.uint8), cv2.COLOR_RGB2HSV)
objm = (yy > 950) & (hsv[..., 1] > 110)  # 객석 남색 테이블보·의자 커버
up = np.clip((lum0 - 0.07) / 0.33, 0, 1) ** 1.6  # 어두운 남색 천 = KOBC 식(윗면만 밝아 굴곡을 따름)
RECV = soft(objm, 3, 1.5) * up
alb = np.clip(cv2.GaussianBlur(lum0, (0, 0), 0.8) / 0.6, 0.25, 1.3)  # 5차: 반사광은 표면 밝기(반사율)를 따른다 — 그릴·틈은 어둡게
RECV = cv2.GaussianBlur((yy > 950).astype(np.float32), (0, 0), 30) * up * alb  # 5차: 벽 밑단 가로 경계선 → 넓게 풀기  # 객석 전체 × 윗면 × 반사율(카펫·천)

# 1) 베이스: 객석·벽 0.66(행사 직전 디밍 — 0.80 은 빛이 묻혀 안 보였다, 2026-11-06 1차), 무대 구역·LED 는 그대로
#    2차: 0.66 도 데크(밝기 244)가 하얗게 떠 스팟 원이 안 보였다 → 객석·벽 0.58, 데크·앞벽 0.72, LED 만 1.0
stage_zone = cv2.GaussianBlur(((yy > 900) & (yy < 1020) & (xx > 560) & (xx < 1995)).astype(np.float32), (0, 0), 12)
f = 0.40 + 0.08 * stage_zone  # 3차 레퍼런스(어두운 홀·파란 무대): 주변 0.40
f = np.maximum(f, 0.62 * np.clip((300 - yy) / 140, 0, 1))  # 천장 라이트 패널은 살린다(레퍼런스의 천장 간접광)  # 3차: 데크 0.72 도 밝아 스팟 원이 묻힘 → 0.62
f = np.maximum(f, cv2.GaussianBlur(led, (0, 0), 2))
f = np.maximum(f, 0.85 * cv2.GaussianBlur(ban, (0, 0), 2))  # 인쇄 배너는 객석보다 덜 낮춘다(글자 대비 유지)
base = u8(src * f[..., None])

# 레퍼런스 없음 → 은은한 컨퍼런스 기본: 스팟 = 중성 쿨화이트, 무빙 = 옅은 청백(LED 파랑 계열에 맞춤)
WARM = np.array([120, 175, 255], np.float32)  # (이름 유지) 트러스 스팟 = 레퍼런스의 파란 렌즈
COOL = np.array([215, 225, 255], np.float32)  # 옆벽 그레이징 = 중성 백색
BLUE = np.array([70, 125, 255], np.float32)


led_soft = np.clip(cv2.GaussianBlur(np.maximum(led, ban), (0, 0), 45) * 1.6, 0, 1)


def beam(S, L, w0, w1, k, col, seed, led_att=0.55, fade_end=0.0, reach=1.0):
    sx, sy = S
    lx, ly = L
    v = np.array([lx - sx, ly - sy], np.float32)
    Ln = np.hypot(*v)
    v /= Ln
    t = ((xx - sx) * v[0] + (yy - sy) * v[1]) / Ln
    d = np.abs((xx - sx) * v[1] - (yy - sy) * v[0])
    w = 1.8 * (w0 + (w1 - w0) * np.clip(t, 0, 1))
    along = (1 - 0.55 * t) * np.clip(t / 0.02, 0, 1)
    if fade_end:
        along = along * np.clip((1 - t) / fade_end, 0, 1)
    if reach < 1:  # 4차 "무대로 내려 꽂는 조명 이상해": 렌즈 아래 짧게만 보이고 공기 속으로 사라짐
        along = along * np.clip((reach - t) / (0.7 * reach), 0, 1)
    prof = np.exp(-2.0 * (d / w) ** 2) * (0.6 + 0.4 * np.exp(-7 * (d / w) ** 2)) + 0.35 * np.exp(-0.5 * (d / (2.2 * w)) ** 2) * np.clip(1 - d / (2.6 * w), 0, 1)  # 3차: 넓힌 빔 외피가 천장 구석까지 번짐 → 외피 끝 2.6w
    dens = np.where((t >= 0) & (t <= 1), along, 0) * prof * (0.65 + 0.7 * noise(60, seed))
    dens = dens * (1 - (1 - led_att) * led_soft)  # LED 경계에서 빔이 뚝 끊기지 않게(점검: 화면 경계에서 잘린 빛)
    out = dens[..., None] * col * 0.55 * k
    out += np.exp(-((xx - sx) ** 2 + (yy - sy) ** 2) / (2 * 9 ** 2))[..., None] * col * 1.4 * k  # 렌즈 글로우(레퍼런스처럼 또렷)
    return out


# 2) 배튼 스팟 → 데크(실측 렌즈, 11개 중 6개, 좌우 비대칭). LED 앞을 지나므로 감쇄
# 앞 트러스 실측 렌즈(10대 중 5대, 좌우 비대칭): 데크 착지. LED·배너 앞을 지나므로 감쇄
# 2차(사용자 "빛줄기가 너무 얇아 퍼짐이 더"): 폭 w0 4→9, w1 34→72
# 트러스 기구 전부(실측 렌즈 9대): 파란 렌즈 + 무대로 짧게 떨어지는 부드러운 빛(수직이라 교차 없음), 세기 제각각
BATTEN = []  # 5차 사용자 "절대 무대로 내려 꽂듯 조명 주지 말고" — 무대 다운라이트 없음
shafts = np.zeros((H, W, 3), np.float32)
land = np.zeros((H, W, 3), np.float32)
deck_s = cv2.GaussianBlur(deck, (0, 0), 1.5)
for i, (S, L, w0, w1, k) in enumerate(BATTEN):
    shafts += beam(S, L, w0, w1, k * 1.6, WARM, 11 + i, led_att=0.45, reach=0.22)
    e = np.exp(-((xx - L[0]) / (w1 * 1.3)) ** 2 * 1.6)
    land += ((e * deck_s * 0.90 + e * lip * np.exp(-np.maximum(yy - DECK_Y[1], 0) / 6) * 0.10) * alb)[..., None] * WARM * k

# 3) 무빙 4대(렌즈가 객석을 향함): 바깥 2 → 앞줄 객석 풀, 안쪽 2 → 객석 위 공중(끝에서 소산). 교차 없음
# 천장 프로파일 스팟 2대(실측 렌즈) → 앞 좌·우 테이블 윗면 넓은 풀(객석에 묻는 빛). 서로 교차 없음
# 2차(사용자 "조명 위치와 빛 나가는 게 안 맞아"): 렌즈가 카메라 쪽을 보는 중앙 무빙 → 앞 가운데 테이블 풀
# 5차 "무대에서 테이블 쪽으로 퍼져 나가는 멋진 걸로": 트러스 기구(렌즈가 객석을 향함) → 테이블 윗면.
#   왼쪽 기구는 왼쪽, 오른쪽 기구는 오른쪽(착지 x 가 광원 순서대로) → 교차 없음. 세기·폭 비대칭.
MOV_AUD = [((830, 376), (330, 1000), 230, 80, 0.60), ((1150, 352), (900, 1090), 260, 90, 0.75),
           ((1290, 448), (1290, 1095), 300, 90, 0.85), ((1433, 352), (1690, 1090), 260, 90, 0.70),
           ((1740, 380), (2240, 1000), 230, 80, 0.55)]
# 천장 프로파일 2대: 몸통→렌즈 축 실측 (595,60)→(515,150) / (1985,55)→(2065,155). 축을 따라 옆벽으로 착지
PROFILE = [((515, 150), (90, 690), 14, 260, 0.45), ((2065, 155), (2470, 665), 14, 260, 0.42)]  # 4차 "벽이 타는 것 같다": 1.1 → 0.45
# 트러스 무빙 2대(실측) → 객석 위 공중, 끝에서 소산. 중앙 X 교차 없음(왼쪽은 왼쪽, 오른쪽은 오른쪽)
# 무빙 옆 스팟 2대: 렌즈가 카메라 쪽 아래를 본다 → 앞쪽 아래로 넓게 퍼지며 객석 위에서 소산
MOV_AIR = []
aud = np.zeros((H, W, 3), np.float32)
occl = soft(objm, 3, 3.0) * np.clip((yy - 950) / 20, 0, 1)  # 8차: 무대 앞 양옆 객석 상관 0.56 → 의자선에서 바로 차광  # 4차: 굴곡 상관 0.59 → 의자가 빔을 더 가림
for i, (S, L, rx, ry, k) in enumerate(MOV_AUD):
    b = beam(S, L, 12, 190, k * 1.7, WARM, 31 + i, fade_end=0.55)  # 객석 쪽으로 넓게 퍼지며 착지 전 소산  # 0.55 는 무대 끝에 뿌연 덩어리
    aud += b * (1 - 0.97 * occl)[..., None]  # 착지 근처는 의자가 가린다
    e = np.clip((np.exp(-((xx - L[0]) / rx) ** 2 - ((yy - L[1]) / ry) ** 2) - 0.03) / 0.97, 0, 1)
    aud += (e * RECV * 1.3 * k)[..., None] * WARM  # 5차: 25px 잡음이 굴곡 상관을 깎아 제거
for i, (S, L, w0, w1, k) in enumerate(MOV_AIR):
    shafts += beam(S, L, w0, w1, k, COOL, 51 + i, fade_end=0.55)
wallm = cv2.GaussianBlur((((xx < 250) | (xx > 2310)) & (yy < 940)).astype(np.float32), (0, 0), 6)
for i, (S, L, w0, w1, k) in enumerate(PROFILE):
    shafts += beam(S, L, w0, w1, k, COOL, 61 + i, fade_end=0.25, reach=0.75)
    e = np.clip((np.exp(-((xx - L[0]) / 260) ** 2 - ((yy - L[1]) / 330) ** 2) - 0.03) / 0.97, 0, 1)
    land += (e * wallm * alb * 0.30 * k)[..., None] * COOL  # 4차: 벽 수광 0.75 → 0.30(×k 0.45)

# 4) LED 번짐: 데크·무대 앞벽·커튼 안쪽·벽·앞줄 의자 윗선
dist = cv2.distanceTransform((1 - led).astype(np.uint8), cv2.DIST_L2, 5)
outside = 1 - led
ledcol = cv2.GaussianBlur(src * led[..., None], (0, 0), 25) / np.maximum(cv2.GaussianBlur(led, (0, 0), 25), 1e-3)[..., None]
halo = (np.exp(-dist / 16) * outside * 0.10)[..., None] * ledcol
wallspill = (np.exp(-dist / 40) * outside * (1 - ban) * (yy < DECK_Y[0]) * (yy > 420) * 0.16)[..., None] * BLUE
deckspill = ((deck_s * 0.55 + lip * np.exp(-np.maximum(yy - DECK_Y[1], 0) / 40) * 0.40) * alb)[..., None] * BLUE  # 3차: 무대 파란 번짐 진하게
cx = np.clip((np.exp(-((xx - 1280) / 1100) ** 2) - 0.04) / 0.96, 0, 1)  # 11차: 긴 꼬리가 비조명 구석까지 닿음 → 0 에서 끊는다
chairs = (RECV * 1.0 * np.exp(-np.maximum(yy - 955, 0) / 420) * cx)[..., None] * BLUE
chairs += (cv2.GaussianBlur((yy > 950).astype(np.float32), (0, 0), 30) * (1 - soft(objm, 3, 2)) * 0.10 * np.exp(-np.maximum(yy - 955, 0) / 220) * cx)[..., None] * BLUE  # 통로 카펫 파란 번짐

# 5) 객석 위 공기 헤이즈(천장·바닥 쪽 0)
vy = np.clip((yy - 350) / 220, 0, 1) * np.clip((1000 - yy) / 160, 0, 1)  # 객석 위를 평평하게 덮지 않게
hx = 0.5 + 0.5 * np.exp(-((xx - 1280) / 800) ** 2)
hx = hx * (1 - 0.7 * led_soft)  # LED·배너 앞 헤이즈 30%  # 13차: LED 앞 헤이즈가 글자 대비를 깎아 뭉개 보임 → 30%
haze = (0.12 * vy * hx * (0.55 + 0.9 * noise(90, 3)))[..., None] * np.array([150, 185, 245], np.float32)  # 3차: 푸른 헤이즈 조금 더

layers = {"L1_led_spill_surfaces.png": u8(wallspill + deckspill + chairs), "L2_stage_landings.png": u8(land),
          "L3_led_foreground_haze.png": u8(halo), "L5_room_haze.png": u8(haze),
          "L8_audience_spill.png": u8(aud), "L4_beam_shafts.png": u8(shafts)}


def screen(b, p):
    b = b.astype(np.int32)
    p = p.astype(np.int32)
    return b + (255 - b) * p // 255


plate = np.zeros((H, W, 3), np.int32)
for n, a in layers.items():
    Image.fromarray(a).save(D / n)
    plate = screen(plate, a)
plate = plate.astype(np.uint8)
comp = screen(base, plate).astype(np.uint8)
Image.fromarray(base).save(D / "base_dimmed.png")
Image.fromarray(plate).save(D / "조명판.png")
Image.fromarray(comp).save(D / "조명합성.png")
Image.fromarray(objm.astype(np.uint8) * 255).save(D / "_obj_mask.png")


# 6) 판정 마스크(계획에서 독립 지정)
def save_mask(n, m):
    Image.fromarray(m.astype(np.uint8) * 255).save(D / n)


core = np.zeros((H, W), bool)
for (sx, sy), (lx, ly), *_ in BATTEN + MOV_AIR + PROFILE + MOV_AUD:
    for t in np.linspace(0.03, 0.12, 40):  # 4차: 빔을 렌즈 아래 짧게 → 판정 지원 영역도 렌즈 가까이
        y = int(sy + (ly - sy) * t)
        x = int(sx + (lx - sx) * t)
        if 0 <= y < H and led[y, x] == 0:
            core[y, x] = True
save_mask("m_beam_core.png", core)
lm = np.zeros((H, W), bool)
lm[928:940, 1000:1600] = True  # 5차: 무대 수광 = LED 파란 번짐(데크 가운데)
lm &= (led == 0) & (ban == 0)
save_mask("m_stage_landing.png", lm)
save_mask("m_led_haze.png", (dist >= 2) & (dist <= 6) & (yy < 900) & (yy > 520) & (ban == 0))
unlit = np.zeros((H, W), bool)
unlit[0:30, 0:200] = True
unlit[0:30, 2360:] = True  # 천장 위 구석(헤이즈·번짐이 닿지 않는 곳)
save_mask("m_unlit.png", unlit)


def sha(n):
    return hashlib.sha256((D / n).read_bytes()).hexdigest()


names = ["base_dimmed.png", *layers, "m_beam_core.png", "m_stage_landing.png", "m_led_haze.png", "m_unlit.png"]
man = {"canvas": [W, H], "mode": "screen", "base": "base_dimmed.png", "composite": "조명합성.png", "plate": "조명판.png",
       "source_layers": list(layers), "sha256": {n: sha(n) for n in names},
       "required_effects": [{"name": "beam shafts", "mask": "m_beam_core.png", "min_value": 10},
                            {"name": "stage landings", "mask": "m_stage_landing.png", "min_value": 15},
                            {"name": "LED foreground haze", "mask": "m_led_haze.png", "min_value": 6}],
       "unlit_mask": "m_unlit.png"}
(D / "pair.json").write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
ledger = {"led": LED + BANNER, "deck_y": list(DECK_Y), "floor_y": 950,
          "beams": [{"S": list(S), "L": list(L), "w1": int(w1), "k": float(k)} for S, L, w0, w1, k in BATTEN + PROFILE + MOV_AIR],
          "audience": [{"S": list(S), "L": list(L), "rx": int(rx), "k": float(k)} for S, L, rx, ry, k in MOV_AUD]}
(D / "ledger.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=1), encoding="utf-8")
print("BUILD_OK", W, H)

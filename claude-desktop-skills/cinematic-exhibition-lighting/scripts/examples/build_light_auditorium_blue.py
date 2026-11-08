# 오디토리움 "2026 공공보건의료 성과보고회" 조명 — cinematic-exhibition-lighting 계약(보존 레이어 → 합성본·조명판, screen).
# 출발: build_light_kobc.py 예제. 좌표 = 2560x1440 작업본(21_합성본_2560.png) 실측.
# 2026-11-06 사용자 "뭉게지는데 조명스킬사용해서 만들어": GPT 후보(1672px) 대신 고해상도 배경판+3D 원본에서 시작.
import hashlib, json
from pathlib import Path
import numpy as np, cv2
from PIL import Image

D = Path(__file__).parent
src8 = np.asarray(Image.open(D.parent / "21_합성본_2560.png").convert("RGB"))
addm = np.asarray(Image.open(D.parent / "21_추가물마스크.png").convert("L")).astype(np.float32) / 255
H, W = src8.shape[:2]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

# 0) 뭉개짐: 2000px 합성본에서 1.28배 키운 3D·그래픽 부분만 약한 언샤프(배경판은 이미 5120 업스케일)
s = src8.astype(np.float32)
sharp = s + 0.7 * (s - cv2.GaussianBlur(s, (0, 0), 1.1))
src = np.clip(s * (1 - addm[..., None]) + sharp * addm[..., None], 0, 255)
Image.fromarray(src.astype(np.uint8)).save(D / "src_sharp.png")


def noise(scale, seed):
    n = np.random.default_rng(seed).random((H // scale + 2, W // scale + 2)).astype(np.float32)
    return cv2.resize(cv2.GaussianBlur(n, (0, 0), 1.2), (W, H), interpolation=cv2.INTER_CUBIC)


def u8(a):
    return np.clip(a, 0, 255).astype(np.uint8)


def soft(m, open_k=3, sigma=2.5):
    u = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((open_k, open_k), np.uint8))
    u = cv2.morphologyEx(u, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.GaussianBlur(u.astype(np.float32), (0, 0), sigma)


LED = [(903, 568, 1650, 858), (735, 660, 905, 875), (1652, 660, 1825, 875)]
led = np.zeros((H, W), np.float32)
for x1, y1, x2, y2 in LED:
    led[y1:y2, x1:x2] = 1
DECK_Y = (858, 895)
deck = ((yy >= DECK_Y[0]) & (yy <= DECK_Y[1]) & (xx >= 720) & (xx <= 1850)).astype(np.float32) * (1 - led)
deck = deck * (1 - np.clip(addm * 1.5, 0, 1))  # 12차: 데크 위 사인·장비는 바닥 수광에서 뺀다(사인 글자가 스팟에 씻김)
lip = ((yy > DECK_Y[1]) & (yy <= 990) & (xx >= 740) & (xx <= 1830)).astype(np.float32)  # 무대 앞 흰 벽면
lum0 = cv2.cvtColor(src.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
hsv = cv2.cvtColor(src.astype(np.uint8), cv2.COLOR_RGB2HSV)
objm = (yy > 935) & (hsv[..., 2] > 70)  # 객석 의자(나무 등받이·팔걸이)
up = np.clip(lum0 / 0.95, 0, 1) ** 1.5  # 6차: 밝은 원목 의자(밝기 0.6~0.8)에서 KOBC 식은 1 로 포화 → 평평한 띠. 포화 없는 식
RECV = soft(objm, 3, 1.5) * up
alb = np.clip(cv2.GaussianBlur(lum0, (0, 0), 0.8) / 0.6, 0.25, 1.3)  # 5차: 반사광은 표면 밝기(반사율)를 따른다 — 그릴·틈은 어둡게
RECV = cv2.GaussianBlur((yy > 935).astype(np.float32), (0, 0), 3) * up * alb  # 9차: 쿠션을 뺀 마스크 경계가 인위적 → 객석 전체 + 반사율(쿠션은 어두워 덜 반사)

# 1) 베이스: 객석·벽 0.66(행사 직전 디밍 — 0.80 은 빛이 묻혀 안 보였다, 2026-11-06 1차), 무대 구역·LED 는 그대로
#    2차: 0.66 도 데크(밝기 244)가 하얗게 떠 스팟 원이 안 보였다 → 객석·벽 0.58, 데크·앞벽 0.72, LED 만 1.0
stage_zone = cv2.GaussianBlur(((yy > 840) & (yy < 1000) & (xx > 700) & (xx < 1870)).astype(np.float32), (0, 0), 12)
f = 0.58 + 0.04 * stage_zone  # 3차: 데크 0.72 도 밝아 스팟 원이 묻힘 → 0.62
f = np.maximum(f, cv2.GaussianBlur(led, (0, 0), 2))
base = u8(src * f[..., None])

# 2026-11-06 사용자 "조명 푸른빛 계열로": 배튼 = 옅은 청백, 무빙 = 파랑 (한 계열 안에서 명도만 다르게)
WARM = np.array([170, 205, 255], np.float32)  # (이름 유지) 배튼 스팟 청백
COOL = np.array([95, 155, 255], np.float32)   # 무빙 빔 파랑
BLUE = np.array([70, 125, 255], np.float32)


def beam(S, L, w0, w1, k, col, seed, led_att=0.55, fade_end=0.0):
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
    prof = np.exp(-2.0 * (d / w) ** 2) * (0.6 + 0.4 * np.exp(-7 * (d / w) ** 2)) + 0.35 * np.exp(-0.5 * (d / (2.2 * w)) ** 2) * np.clip(1 - d / (3.5 * w), 0, 1)
    dens = np.where((t >= 0) & (t <= 1), along, 0) * prof * (0.65 + 0.7 * noise(60, seed))
    dens = np.where(led > 0, dens * led_att, dens)
    out = dens[..., None] * col * 0.55 * k
    out += np.exp(-((xx - sx) ** 2 + (yy - sy) ** 2) / (2 * 6 ** 2))[..., None] * col * 0.9 * k  # 렌즈 글로우
    return out


# 2) 배튼 스팟 → 데크(실측 렌즈, 11개 중 6개, 좌우 비대칭). LED 앞을 지나므로 감쇄
BATTEN = [((1040, 503), (1010, 884), 4, 34, 0.50), ((1138, 508), (1150, 888), 4, 34, 0.40),
          ((1286, 475), (1300, 886), 4, 36, 0.55), ((1408, 503), (1440, 888), 4, 34, 0.45),
          ((1498, 503), (1560, 884), 4, 34, 0.40), ((972, 475), (880, 880), 4, 32, 0.35)]
shafts = np.zeros((H, W, 3), np.float32)
land = np.zeros((H, W, 3), np.float32)
deck_s = cv2.GaussianBlur(deck, (0, 0), 1.5)
for i, (S, L, w0, w1, k) in enumerate(BATTEN):
    shafts += beam(S, L, w0, w1, k * 1.6, WARM, 11 + i, led_att=0.45)
    e = np.exp(-((xx - L[0]) / (w1 * 1.3)) ** 2 * 1.6)
    land += ((e * deck_s * 0.90 + e * lip * np.exp(-np.maximum(yy - DECK_Y[1], 0) / 6) * 0.10) * alb)[..., None] * WARM * k

# 3) 무빙 4대(렌즈가 객석을 향함): 바깥 2 → 앞줄 객석 풀, 안쪽 2 → 객석 위 공중(끝에서 소산). 교차 없음
MOV_AUD = [((828, 867), (520, 1060), 210, 95, 1.05), ((1718, 867), (2040, 1050), 210, 95, 0.95)]  # 10차: ry 44 는 풀 경계가 의자 명암과 무관한 세부가 됨
MOV_AIR = [((978, 874), (760, 330), 5, 45, 1.15), ((1568, 875), (1830, 320), 5, 45, 1.05)]
aud = np.zeros((H, W, 3), np.float32)
occl = soft(objm, 3, 3.0) * np.clip((yy - 935) / 20, 0, 1)  # 8차: 무대 앞 양옆 객석 상관 0.56 → 의자선에서 바로 차광  # 4차: 굴곡 상관 0.59 → 의자가 빔을 더 가림
for i, (S, L, rx, ry, k) in enumerate(MOV_AUD):
    b = beam(S, L, 5, 57, k, COOL, 31 + i, fade_end=0.7)  # 0.55 는 무대 끝에 뿌연 덩어리
    aud += b * (1 - 0.97 * occl)[..., None]  # 착지 근처는 의자가 가린다
    e = np.clip((np.exp(-((xx - L[0]) / rx) ** 2 - ((yy - L[1]) / ry) ** 2) - 0.03) / 0.97, 0, 1)
    aud += (e * RECV * 1.2 * k)[..., None] * COOL  # 5차: 25px 잡음이 굴곡 상관을 깎아 제거
for i, (S, L, w0, w1, k) in enumerate(MOV_AIR):
    shafts += beam(S, L, w0, w1, k, COOL, 51 + i, fade_end=0.45)

# 4) LED 번짐: 데크·무대 앞벽·커튼 안쪽·벽·앞줄 의자 윗선
dist = cv2.distanceTransform((1 - led).astype(np.uint8), cv2.DIST_L2, 5)
outside = 1 - led
ledcol = cv2.GaussianBlur(src * led[..., None], (0, 0), 25) / np.maximum(cv2.GaussianBlur(led, (0, 0), 25), 1e-3)[..., None]
halo = (np.exp(-dist / 16) * outside * 0.10)[..., None] * ledcol
wallspill = (np.exp(-dist / 40) * outside * (yy < DECK_Y[0]) * (yy > 440) * 0.16)[..., None] * BLUE
deckspill = ((deck_s * 0.24 + lip * np.exp(-np.maximum(yy - DECK_Y[1], 0) / 30) * 0.16) * alb)[..., None] * BLUE
cx = np.clip((np.exp(-((xx - 1280) / 750) ** 2) - 0.06) / 0.94, 0, 1)  # 11차: 긴 꼬리가 비조명 구석까지 닿음 → 0 에서 끊는다
chairs = (RECV * 0.42 * np.exp(-np.maximum(yy - 940, 0) / 200) * cx)[..., None] * BLUE

# 5) 객석 위 공기 헤이즈(천장·바닥 쪽 0)
vy = np.clip((yy - 330) / 220, 0, 1) * np.clip((960 - yy) / 160, 0, 1)  # 객석 위를 평평하게 덮지 않게
hx = 0.5 + 0.5 * np.exp(-((xx - 1280) / 800) ** 2)
hx = hx * (1 - 0.7 * cv2.GaussianBlur(led, (0, 0), 6))  # 13차: LED 앞 헤이즈가 글자 대비를 깎아 뭉개 보임 → 30%
haze = (0.08 * vy * hx * (0.55 + 0.9 * noise(90, 3)))[..., None] * np.array([205, 214, 235], np.float32)

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
for (sx, sy), (lx, ly), *_ in BATTEN + MOV_AIR:
    for t in np.linspace(0.12, 0.45, 80):
        y = int(sy + (ly - sy) * t)
        x = int(sx + (lx - sx) * t)
        if 0 <= y < H and led[y, x] == 0:
            core[y, x] = True
save_mask("m_beam_core.png", core)
lm = np.zeros((H, W), bool)
for _, (lx, ly), _, w1, _ in BATTEN:
    lm[868:880, int(lx - w1 * 0.3):int(lx + w1 * 0.3)] = True
lm &= led == 0
save_mask("m_stage_landing.png", lm)
save_mask("m_led_haze.png", (dist >= 2) & (dist <= 6) & (yy < 850) & (yy > 580))
unlit = np.zeros((H, W), bool)
unlit[0:40, 0:300] = True
unlit[0:40, 2260:] = True
unlit[1380:, 0:200] = True
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
ledger = {"led": LED, "deck_y": list(DECK_Y), "floor_y": 935,
          "beams": [{"S": list(S), "L": list(L), "w1": int(w1), "k": float(k)} for S, L, w0, w1, k in BATTEN],
          "audience": [{"S": list(S), "L": list(L), "rx": int(rx), "k": float(k)} for S, L, rx, ry, k in MOV_AUD]}
(D / "ledger.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=1), encoding="utf-8")
print("BUILD_OK", W, H)

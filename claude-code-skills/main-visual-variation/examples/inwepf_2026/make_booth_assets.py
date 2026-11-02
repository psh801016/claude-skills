r"""INWEPF 2026 부스 간판·날개·켈지 배경 재료 (일러 없이) — 실물 150ppi CMYK TIFF.
- 간판 2930x500 / 1940x500, 켈지 950x200: 디자인팀 가로 배경(02 소스\INWEPF소스_01 사본 3.png, 8000x4500 배경만)에서
  산 능선~논 띠를 판 비율로 잘라 쓴다(위 = 하늘·산 → 작은 행사명 띠, 아래 = 논). 1940·켈지는 같은 띠의 가운데를 판 비율로.
- 날개 450x2480: ASURA님이 만든 3D 맵 '하단백월날개.png'(398x2382)의 가장자리 색 흐름(남색 → 청록)을 그대로 따서 매끈한 세로 그라데이션.
원본 파일은 읽기만 한다. 결과: C:\mvv\src\inwepf_booth\*.tif
"""
import sys
from pathlib import Path
from PIL import Image, ImageFilter
sys.path.insert(0, r"C:\Users\PSH\.agents\skills\jokjabong-print-fit\scripts\color")
from colorize import to_cmyk, ICC_BYTES

Image.MAX_IMAGE_PIXELS = None
EV = r"X:\[11.11~11.13] 2026년 제21차 INWEPF 운영위원회 개최"
BG = EV + r"\02 소스\INWEPF소스_01 사본 3.png"
WING = EV + r"\08 3D\map\하단백월날개.png"
OUT = Path(r"C:\mvv\src\inwepf_booth"); OUT.mkdir(parents=True, exist_ok=True)
PPI = 150


def px(mm):
    return round(mm / 25.4 * PPI)


def save(im_rgb, name, flat_top=40):
    c, _ = to_cmyk(im_rgb, flat_top=flat_top)   # 그라데이션은 0 — 줄마다 같은 색이라 '넓은 단색 덮어쓰기'가 걸려 가로 띠가 생긴다(1차 날개)
    c.save(OUT / name, compression="tiff_adobe_deflate", icc_profile=ICC_BYTES, dpi=(PPI, PPI))
    im_rgb.resize((max(1, im_rgb.width // 8), max(1, im_rgb.height // 8))).save(OUT / (name[:-4] + "_view.jpg"), quality=85)
    print(name, c.size)


src = Image.open(BG).convert("RGB")          # 8000 x 4500
W, H = src.size
Y_MID = 2600                                 # 띠 가운데 = 산 능선 — 위는 별 하늘(작은 행사명이 잘 보이게), 아래는 산·논 (3250 은 너무 밝았다)

def band(wmm, hmm, name, wfrac=1.0):
    cw = round(W * wfrac); ch = round(cw * hmm / wmm)
    x0 = (W - cw) // 2; y0 = max(0, min(H - ch, Y_MID - ch // 2))
    save(src.crop((x0, y0, x0 + cw, y0 + ch)).resize((px(wmm), px(hmm)), Image.LANCZOS), name)

band(2930, 500, "sign_2930_bg.tif")
band(1940, 500, "sign_1940_bg.tif", wfrac=1940 / 2930)
band(950, 200, "kelji_bg.tif", wfrac=0.45)   # 켈지도 같은 띠 (2026-10-26 켈지는 950x950 데스크 현수막으로 바뀜 — 남겨 둠)

# 데스크 앞판 950x750 (켈지 대신, ASURA님 2026-10-26 "950*950 현수막 상하단 바미싱, 메인비주얼로" → "높이가 750 이다"):
# 디자인팀 가로 메인비주얼(02 소스\INWEPF소스_01 사본.png = 원 안에 제목·국기·곡선 슬로건, 로고·날짜 없음)을 원 중심 기준 950:750 으로.
# 6080x4800px / 950mm = 약 162ppi (현수막 출력 충분). 하늘 그라데이션 띠 방지로 flat_top=0
import numpy as np
mv = Image.open(EV + r"\02 소스\INWEPF소스_01 사본.png").convert("RGB")
CX = 4000                                    # 원 중심 x (8000 폭 가운데)
PAD = 300                                    # 원 윗선이 판 끝에 붙으면 상단 바미싱에 먹힌다(950x950 1차) → 하늘을 위로 300px(약 60mm) 늘림: 하늘만 있는 판의 맨 위 띠를 뒤집어 이어 붙임
DH = 4500 + PAD; DW = round(DH * 950 / 750)
dk = Image.new("RGB", (DW, DH))
sky = Image.open(EV + r"\02 소스\INWEPF소스_01 사본 4.png").convert("RGB")   # 하늘만 있는 판(맨 윗줄 색이 사본과 같다). 사본 자체를 뒤집으면 원 윗부분이 거울처럼 비쳤다(2차)
dk.paste(sky.crop((CX - DW // 2, 0, CX + DW // 2, PAD)).transpose(Image.FLIP_TOP_BOTTOM), (0, 0))
dk.paste(mv.crop((CX - DW // 2, 0, CX + DW // 2, 4500)), (0, PAD))
# 남색 하늘을 메인비주얼 CMYK 값으로: 소스 PNG 하늘(0,12,104)은 그대로 바꾸면 C100 M100 Y55 K7(보라 기운)이라 메인 CMYK 하늘 C100 M91 Y32 K53 과 다르다
# ("남색으로 맞춰", 2026-10-26). RGB 를 바꿔서는 M100·Y60 아래로 안 내려가서 CMYK 에서 직접 고친다. 남색만(R 낮고 B 어두운 곳) — 원 안 보라·풍경은 그대로
c, _ = to_cmyk(dk, flat_top=0)
a = np.asarray(c).astype(np.float32); r = np.asarray(dk).astype(np.float32)
w = np.clip((140 - r[..., 2]) / 36, 0, 1) * np.clip((40 - r[..., 0]) / 20, 0, 1)   # B 104 이하 = 1, 140 이상 = 0 / R 20 이하만
for ch, tgt in ((1, 91), (2, 32), (3, 53)):
    t = tgt * 2.55
    a[..., ch] = a[..., ch] + (t - a[..., ch]) * w if ch == 3 else np.where(a[..., ch] > t, a[..., ch] + (t - a[..., ch]) * w, a[..., ch])
Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "CMYK").save(OUT / "desk_950_bg.tif", compression="tiff_adobe_deflate", icc_profile=ICC_BYTES, dpi=(PPI, PPI))
dk.resize((DW // 8, DH // 8)).save(OUT / "desk_950_bg_view.jpg", quality=85)
print("desk_950_bg.tif", (DW, DH), "하늘 맨 위 CMYK", [round(v / 2.55) for v in a[5, DW // 6]])

# 날개 그라데이션: 하단백월날개.png 왼쪽 가장자리 세로 한 줄(글자 없는 곳) → 부드럽게 → 450x2480 실물
w = Image.open(WING).convert("RGB")
col = w.crop((4, 0, 12, w.height)).resize((1, w.height), Image.BOX).filter(ImageFilter.GaussianBlur(6))
save(col.resize((px(450), px(2480)), Image.BICUBIC), "wing_grad.tif", flat_top=0)

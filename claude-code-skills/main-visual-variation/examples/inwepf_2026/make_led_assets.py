r"""INWEPF 2026 LED 재료 (RGB — LED 는 화면이라 RGB 문서로 만든다). 원본은 전부 읽기만.
  bg_rgb.tif      디자인팀 가로 배경(02 소스\INWEPF소스_01 사본 3.png)을 10:4 로 아래 맞춰 자름
  led_pattern.png 참고 LED(지식재산대전 무대LED.ai)의 RGB 픽셀 줄무늬(1597x900) — 일러에서 Overlay 50% 로 얹는다
  imag_win.png    연사 카메라 화면 창: 연사 뒤 LED(기본 판 렌더)를 흐리게 + 연사 상반신·포디움 클로즈업 + 하늘색 테두리
                  (연사는 LED 가운데 앞에 실제로 서고, 좌우 창에 그 카메라 화면을 띄운다 — ASURA님 2026-10-23)
실행: python make_led_assets.py   (LED_기본.jpg 가 먼저 있어야 창 배경을 만든다)
"""
import fitz
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

Image.MAX_IMAGE_PIXELS = None
EV = r"X:\[11.11~11.13] 2026년 제21차 INWEPF 운영위원회 개최"
OUT = r"C:\mvv\src\inwepf"
REF = r"X:\[09.22. 10시] 2026 대한민국 지식재산대전\제안\01 3D\map\무대LED.ai"

# 1) 배경
im = Image.open(EV + r"\02 소스\INWEPF소스_01 사본 3.png").convert("RGB")
W, H = im.size
im.crop((0, H - round(W * 0.4), W, H)).save(OUT + r"\bg_rgb.tif", compression="tiff_lzw")

# 2) 픽셀 줄무늬 — 참고 파일에서 1597x900 그림을 찾아 꺼낸다
d = fitz.open(REF)
pat = None
for pg in d:
    for info in pg.get_image_info(xrefs=True):
        if info.get("width") == 1597 and info.get("height") == 900 and info.get("xref"):
            pat = fitz.Pixmap(d, info["xref"]); break
    if pat: break
if pat.n - pat.alpha != 3:
    pat = fitz.Pixmap(fitz.csRGB, pat)
pat.save(OUT + r"\led_pattern.png")

# 3) 연사 카메라 화면 창 (2200 x 3500mm 창 → 1100 x 1750px)
WW, WH = 1100, 1750
led = Image.open(EV + r"\08 3D\map\LED_기본.jpg").convert("RGB")          # 6000x2400 (10x4m)
lx = led.width // 2; cw = round(led.height * 0.92 * WW / WH)
back = led.crop((lx - cw // 2, round(led.height * 0.04), lx + cw // 2, round(led.height * 0.96))).resize((WW, WH), Image.LANCZOS)
back = ImageEnhance.Brightness(back.filter(ImageFilter.GaussianBlur(28))).enhance(0.72)
spk = Image.open(OUT + r"\speaker_inwepf.png").convert("RGBA")             # 1504x2776, 포디움판 INWEPF
crop = spk.crop((200, 40, 200 + 1200, 40 + round(1200 * WH / WW)))        # 머리~포디움판 아래, 포디움 글자(INWEPF)가 보이게 (창 비율)
crop = crop.resize((WW, WH), Image.LANCZOS)
win = back.copy(); win.paste(crop, (0, 0), crop)
dr = ImageDraw.Draw(win); b = 10
dr.rectangle((0, 0, WW - 1, WH - 1), outline=(120, 220, 255), width=b)     # 하늘색 테두리
win.save(OUT + r"\imag_win.png")
win.resize((WW // 3, WH // 3)).save(OUT + r"\imag_win_view.jpg", quality=85)
print("bg", (W, round(W * 0.4)), "pattern", (pat.width, pat.height), "win", win.size)

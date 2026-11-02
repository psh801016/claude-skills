r"""INWEPF 2026 LED(10m x 4m) 배경 — 디자인팀 가로 원본(02 소스\INWEPF소스_01 사본 3.png, 8000x4500 배경만)을 10:4 로 아래 맞춰 자르고 CMYK TIFF 로.
연사판 가운데 칸(25%~75%)도 같은 자리에서 잘라 따로 저장 — 연사 사진이 넘치는 부분을 덮는다. 원본은 읽기만."""
import sys
from PIL import Image
sys.path.insert(0, r"C:\Users\PSH\.agents\skills\jokjabong-print-fit\scripts\color")
from colorize import to_cmyk, ICC_BYTES
Image.MAX_IMAGE_PIXELS = None
SRC = r"X:\[11.11~11.13] 2026년 제21차 INWEPF 운영위원회 개최\02 소스\INWEPF소스_01 사본 3.png"
OUT = r"C:\mvv\src\inwepf"
im = Image.open(SRC).convert("RGB")
W, H = im.size                      # 8000 x 4500
h = round(W * 4 / 10)               # 3200
bg = im.crop((0, H - h, W, H))      # 아래(풍경) 기준
c, _ = to_cmyk(bg); c.save(OUT + r"\led_bg.tif", compression="tiff_lzw", icc_profile=ICC_BYTES)
mid = c.crop((W // 4, 0, W * 3 // 4, h)); mid.save(OUT + r"\led_bg_mid.tif", compression="tiff_lzw", icc_profile=ICC_BYTES)
bg.resize((2000, 800)).save(OUT + r"\led_bg_view.jpg", quality=85)
print(c.size, mid.size)
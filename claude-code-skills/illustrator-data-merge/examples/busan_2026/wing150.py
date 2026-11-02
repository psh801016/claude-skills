# 날개 한 면을 실물 150ppi CMYK 로 두 장: 아래(그대로), 위(미리 180도 돌림). 일러에서 돌리지 않아 이음매가 안 생긴다.
import fitz
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
ICC = open(r"C:\Windows\System32\spool\drivers\color\JapanColor2001Coated.icc", "rb").read()
OUT = r"G:\내 드라이브\AI-작업기록\claude\2026-10-15_부산사이버보안_부스간판\출력그림" + "\\"
pg = fitz.open(r"X:\[11.04-05] 2026 부산 사이버보안 콘퍼런스\3 3D\발주\원본\B구역부스.ai")[0]
px = round(450 / 25.4 * 150); z = px / pg.rect.width
pix = pg.get_pixmap(matrix=fitz.Matrix(z, z), colorspace=fitz.csCMYK, alpha=False)
im = Image.frombytes("CMYK", (pix.width, pix.height), pix.samples)
kw = dict(compression="tiff_adobe_deflate", icc_profile=ICC, dpi=(1500, 1500))
im.save(OUT + "날개_아래_150.tif", **kw)
im.rotate(180).save(OUT + "날개_위_150.tif", **kw)
print(im.size, "→ 실물", round(im.size[0] / 150 * 25.4), "x", round(im.size[1] / 150 * 25.4), "mm")

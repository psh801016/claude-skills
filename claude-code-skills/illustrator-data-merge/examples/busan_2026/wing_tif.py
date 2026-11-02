import fitz
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
ICC = r"C:\Windows\System32\spool\drivers\color\JapanColor2001Coated.icc"
OUT = r"G:\내 드라이브\AI-작업기록\claude\2026-10-15_부산사이버보안_부스간판\로고\날개_한면_cmyk.tif"
pg = fitz.open(r"X:\[11.04-05] 2026 부산 사이버보안 콘퍼런스\3 3D\발주\원본\B구역부스.ai")[0]
r = pg.rect; print("대지", round(r.width * 25.4 / 72, 1), "x", round(r.height * 25.4 / 72, 1), "mm (1/10)")
px_w = round(450 / 25.4 * 120)                      # 실물 450mm @120dpi
z = px_w / r.width
pix = pg.get_pixmap(matrix=fitz.Matrix(z, z), colorspace=fitz.csCMYK, alpha=False)
im = Image.frombytes("CMYK", (pix.width, pix.height), pix.samples)
im.save(OUT, compression="tiff_lzw", icc_profile=open(ICC, "rb").read(), dpi=(1200, 1200))
print(im.size, "→ 실물 dpi", round(pix.width / (450 / 25.4)))
prev = pg.get_pixmap(matrix=fitz.Matrix(1200 / r.height, 1200 / r.height), alpha=False); prev.save("wing_face_prev.png")

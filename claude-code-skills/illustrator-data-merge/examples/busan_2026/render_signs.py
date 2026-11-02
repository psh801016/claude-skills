"""출력 2단계: 원본 부스간판.ai 에서 간판 32장을 실물 150ppi CMYK TIFF 로 뽑는다 (일러 없이, pymupdf).

간판위치.tsv(out_prep.jsx 가 기록) = 대지 기준 pt 의 간판 테두리(클리핑) 상자. 그 상자만 그린다 → 위 검정 번호 라벨·옆 간판은 안 들어간다.
1/10 축척: 293mm 상자 = 실물 2930mm → 150ppi 면 17,303px. dpi 메타데이터는 1500(=150×10) 이라 1/10 문서에 넣으면 제 크기.
"""
from pathlib import Path

import fitz
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
SRC = r"X:\[11.04-05] 2026 부산 사이버보안 콘퍼런스\3 3D\발주\원본\부스간판.ai"
OUT = Path(r"G:\내 드라이브\AI-작업기록\claude\2026-10-15_부산사이버보안_부스간판\출력그림")
ICC = open(r"C:\Windows\System32\spool\drivers\color\JapanColor2001Coated.icc", "rb").read()
PPI, SCALE, MM = 150, 10, 72 / 25.4

rows = [l.split("\t") for l in (OUT / "간판위치.tsv").read_text(encoding="utf-8").splitlines()]
ab = rows[0]
pg = fitz.open(SRC)[0]
assert abs(pg.rect.width - float(ab[1])) < 1 and abs(pg.rect.height - float(ab[2])) < 1, (pg.rect, ab)
dl = pg.get_displaylist()                                   # 한 번만 해석하고 32번 그린다
for r in rows[1:]:
    rid, num, name = r[0], r[1], r[2]          # S0~S31 간판, O0~ 데스크 띠지 같은 다른 출력물
    x0, y0, x1, y1 = map(float, r[3:7])
    real_w = (x1 - x0) / MM * SCALE
    px = round(real_w / 25.4 * PPI)
    z = px / (x1 - x0)
    pix = dl.get_pixmap(matrix=fitz.Matrix(z, z), clip=fitz.Rect(x0, y0, x1, y1), colorspace=fitz.csCMYK, alpha=False)
    im = Image.frombytes("CMYK", (pix.width, pix.height), pix.samples)
    dst = OUT / f"그림_{rid}.tif"
    im.save(dst, compression="tiff_adobe_deflate", icc_profile=ICC, dpi=(PPI * SCALE, PPI * SCALE))
    print(f"{rid} {num} {name} 실물 {round(real_w)}x{round((y1 - y0) / MM * SCALE)}mm → {im.size[0]}x{im.size[1]}px {dst.stat().st_size // 2**20}MB", flush=True)
    del pix, im

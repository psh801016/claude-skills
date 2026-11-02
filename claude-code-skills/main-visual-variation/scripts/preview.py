"""결과 시트 미리보기 — 일러 없이 pymupdf 로 C:/mvv/out/<key>.ai 를 흰 바탕 jpg 로 그린다 (긴 변 3000px).
일러 PNG 내보내기는 투명 배경이라 겹침·흰 글자가 안 보이므로 이걸로 본다 (간판 스킬 7절과 같은 이유).
실행: python preview.py [key ...]   (없으면 전부)  → C:/mvv/out/<key>.jpg
"""
import sys
from pathlib import Path

import fitz
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
OUT = Path("C:/mvv/out")


def render(ai: Path, long_px: int = 3000) -> Path:
    pg = fitz.open(ai)[0]
    z = long_px / max(pg.rect.width, pg.rect.height)
    pix = pg.get_pixmap(matrix=fitz.Matrix(z, z), colorspace=fitz.csRGB, alpha=False)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    dst = ai.with_suffix(".jpg")
    im.save(dst, quality=85)
    return dst


if __name__ == "__main__":
    keys = sys.argv[1:]
    files = [OUT / f"{k}.ai" for k in keys] if keys else sorted(OUT.glob("*.ai"))
    for f in files:
        print(render(f))

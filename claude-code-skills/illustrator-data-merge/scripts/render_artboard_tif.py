"""다른 .ai 파일의 대지 한 장 → 실물 해상도 CMYK TIFF (일러 없이, pymupdf).

왜: 다른 파일의 디자인(날개 등)을 일러 스크립트로 벡터 복제하면 반투명 그림·스크린 겹침이 빠졌다
(2026-10-21 부산 기업부스날개, 3회). pymupdf 렌더는 대지 그대로(대지 밖은 잘림) 나온다.
dpi 메타데이터를 `dpi × 축척`으로 적어 두면, 1/10 축척 문서에 넣었을 때 문서 크기에 그대로 맞는다.

예) py -3 render_artboard_tif.py "B구역부스.ai" --page 1 --real-width 450 --dpi 120 --scale 10 -o 날개_한면_cmyk.tif
"""
import argparse
from pathlib import Path

import fitz
from PIL import Image

ICC = r"C:\Windows\System32\spool\drivers\color\JapanColor2001Coated.icc"


def render(src, page, real_width_mm, dpi, scale, out):
    pg = fitz.open(src)[page - 1]
    px_w = round(real_width_mm / 25.4 * dpi)
    z = px_w / pg.rect.width
    pix = pg.get_pixmap(matrix=fitz.Matrix(z, z), colorspace=fitz.csCMYK, alpha=False)
    im = Image.frombytes("CMYK", (pix.width, pix.height), pix.samples)
    icc = Path(ICC).read_bytes() if Path(ICC).exists() else None
    kw = {"compression": "tiff_lzw", "dpi": (dpi * scale, dpi * scale)}
    if icc:
        kw["icc_profile"] = icc
    im.save(out, **kw)
    return im.size, round(pg.rect.width * 25.4 / 72, 1), round(pg.rect.height * 25.4 / 72, 1)


def main():
    a = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    a.add_argument("src"); a.add_argument("-o", "--out", required=True)
    a.add_argument("--page", type=int, default=1, help="대지 번호(1부터)")
    a.add_argument("--real-width", type=float, required=True, help="실물 폭 mm (예: 날개 450)")
    a.add_argument("--dpi", type=int, default=120, help="실물 기준 dpi (현수막 100~120)")
    a.add_argument("--scale", type=int, default=10, help="문서 축척 (1/10 이면 10)")
    o = a.parse_args()
    size, w, h = render(o.src, o.page, o.real_width, o.dpi, o.scale, o.out)
    print(f"대지 {w}x{h}mm → {size[0]}x{size[1]}px CMYK, 실물 {o.dpi}dpi → {o.out}")


if __name__ == "__main__":
    main()

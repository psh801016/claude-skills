"""세로 메인비주얼 → 가로로 긴 판(LED·가로 백월)용 배경 이미지. 일러 없이.

세로 포스터를 그대로 늘리면 풍경 사진이 찌그러지거나 너무 커진다. 그래서
  ① 하늘: 포스터 글자 레이어를 끄고 렌더해 좌우 가장자리(사진·원 밖) 색을 줄마다 읽어 위→아래 그라데이션을 만든다
  ② 풍경: 포스터 안의 가장 큰 사진(풍경)을 원래 비율 그대로 판 폭에 맞춰 아래에 깔고, 윗부분을 하늘로 서서히 녹인다
  ③ 결과는 CMYK TIFF (Japan Color 2001 Coated, 족자봉 색 맞춤 도구) — 일러 빌더가 bg 로 깐다
충남 2026 은 배경이 단색 그라데이션이라 필요 없었고, INWEPF 2026 LED(10x4m) 에서 처음 씀.

실행: python wide_bg.py <main.ai> <out.tif> --w 6000 --h 2400 --land-top 0.42 --fade 0.18 [--off "레이어 2"] [--crop x0,x1]
  land-top = 풍경 사진 윗변 위치(판 높이 비율), fade = 녹이는 높이(판 높이 비율), off = 끌 PDF 레이어 이름(글자 레이어)
  crop = 결과에서 가로 일부만 따로 저장(연사판 가운데 칸용, 비율 0~1) → <out>_crop.tif
"""
import argparse
import io
import sys

import fitz
import numpy as np
from PIL import Image, ImageCms

sys.path.insert(0, r"C:\Users\PSH\.agents\skills\jokjabong-print-fit\scripts\color")
from colorize import to_cmyk, ICC_BYTES   # noqa: E402

Image.MAX_IMAGE_PIXELS = None
SRGB = ImageCms.createProfile("sRGB")
JC = ImageCms.ImageCmsProfile(io.BytesIO(ICC_BYTES))


def sky_profile(page, off_xrefs, rows):
    """글자 레이어를 끈 렌더에서 좌우 가장자리 3% 의 줄별 중앙값 색 → (rows,3)"""
    doc = page.parent
    # doc.set_layer(-1, off=…) 는 렌더에 반영되지 않는다 — UI 설정으로 끈다 (map_png.py 테스트로 확인, 2026-10-23)
    names = {o["name"] for x, o in doc.get_ocgs().items() if x in off_xrefs}
    for u in doc.layer_ui_configs():
        if u["text"] in names and u["on"]:
            doc.set_layer_ui_config(u["number"], action=2)
    z = 600 / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(z, z), alpha=False)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(float)
    e = max(2, pix.width * 3 // 100)
    edge = np.concatenate([a[:, :e], a[:, -e:]], axis=1)
    prof = np.median(edge, axis=1)                       # (H,3)
    xs = np.linspace(0, len(prof) - 1, rows)
    return np.stack([np.interp(xs, np.arange(len(prof)), prof[:, c]) for c in range(3)], 1)


def biggest_photo(doc, page):
    best = None
    for im in page.get_image_info(xrefs=True):
        if im.get("xref") and (best is None or im["width"] * im["height"] > best["width"] * best["height"]):
            best = im
    pix = fitz.Pixmap(doc, best["xref"])
    if pix.n - pix.alpha == 4:
        img = Image.frombytes("CMYK", (pix.width, pix.height), pix.samples if not pix.alpha else fitz.Pixmap(pix, 0).samples)
        return ImageCms.profileToProfile(img, JC, SRGB, outputMode="RGB")
    if pix.n - pix.alpha != 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def build(main, W, H, land_top, fade, off_names, sky_rows_frac=0.55):
    doc = fitz.open(main); page = doc[0]
    off = [x for x, o in doc.get_ocgs().items() if o["name"] in off_names]
    # 하늘은 포스터 위쪽(사진 위) 만 쓴다 — 포스터 높이의 sky_rows_frac 까지를 판 전체 높이로 늘린다
    prof = sky_profile(page, off, int(H / sky_rows_frac))[:H]
    sky = np.repeat(prof[:, None, :], W, axis=1)
    photo = biggest_photo(doc, page)
    ph = round(photo.height * W / photo.width)
    photo = np.asarray(photo.resize((W, ph), Image.LANCZOS)).astype(float)
    top = int(H * land_top)
    out = sky.copy()
    n = min(ph, H - top)
    fh = max(1, int(H * fade))
    alpha = np.clip(np.arange(n) / fh, 0, 1)[:, None, None]
    out[top:top + n] = sky[top:top + n] * (1 - alpha) + photo[:n] * alpha
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def test():
    # 풍경 녹이기: 윗변은 하늘색 그대로, fade 아래는 사진 그대로
    sky = np.zeros((10, 4, 3)); ph = np.full((10, 4, 3), 200.0)
    alpha = np.clip(np.arange(10) / 4, 0, 1)[:, None, None]
    o = sky * (1 - alpha) + ph * alpha
    assert o[0, 0, 0] == 0 and o[5, 0, 0] == 200
    print("OK wide_bg blend")


if __name__ == "__main__":
    if sys.argv[1:] == ["test"]:
        test(); sys.exit()
    ap = argparse.ArgumentParser()
    ap.add_argument("main"); ap.add_argument("out")
    ap.add_argument("--w", type=int, default=6000); ap.add_argument("--h", type=int, default=2400)
    ap.add_argument("--land-top", type=float, default=0.42); ap.add_argument("--fade", type=float, default=0.18)
    ap.add_argument("--off", default="레이어 2"); ap.add_argument("--crop", default="")
    a = ap.parse_args()
    rgb = build(a.main, a.w, a.h, a.land_top, a.fade, [s.strip() for s in a.off.split(",") if s.strip()])
    rgb.save(a.out.rsplit(".", 1)[0] + "_rgb.jpg", quality=90)
    cm, _ = to_cmyk(rgb)
    cm.save(a.out, compression="tiff_lzw", icc_profile=ICC_BYTES)
    print(a.out, rgb.size)
    if a.crop:
        x0, x1 = (float(v) for v in a.crop.split(","))
        c = cm.crop((round(a.w * x0), 0, round(a.w * x1), a.h))
        p = a.out.rsplit(".", 1)[0] + "_crop.tif"; c.save(p, compression="tiff_lzw", icc_profile=ICC_BYTES); print(p, c.size)

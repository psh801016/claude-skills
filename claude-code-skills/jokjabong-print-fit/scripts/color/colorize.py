"""족자봉 RGB 원본 색 맞춤 — colormatch.jsx 와 짝.
  python colorize.py map <KEY>            : <KEY>_colors.txt → 최적 CMYK 색표 + <KEY>_r*.png → CMYK TIFF → <KEY>_map.js
  python colorize.py pdf <pdf> <page> <W> <H> <dpi> <out.tif> : PDF 한 쪽을 실치수 W×H(mm)·dpi 로 렌더해 CMYK TIFF (단색 면은 최적값)
  python colorize.py img <in> <W> <H> <dpi> <out.tif>          : 그림(RGB) → 실치수 크기 CMYK TIFF
기준 프로파일 Japan Color 2001 Coated, 그림은 상대색도+BPC, 단색은 match.best() (원본 RGB 와 ΔE2000 최소)"""
import io, sys, pathlib, json
import numpy as np
from PIL import Image, ImageCms
from match import best, std, de2000, lab_rgb, lab_cmyk, T_RGB_CMYK, ICC
Image.MAX_IMAGE_PIXELS = None
D = pathlib.Path("C:/jjb/color")
ICC_BYTES = open(ICC, "rb").read()

def to_cmyk(rgb_img, flat_top=40):
    """그림 전체는 표준 변환, 면적이 큰 단색(정확히 같은 RGB)은 최적값으로 덮어쓴다"""
    rgb_img = rgb_img.convert("RGB")
    cmyk = np.asarray(ImageCms.applyTransform(rgb_img, T_RGB_CMYK)).copy()
    a = np.asarray(rgb_img); flat = a.reshape(-1, 3)
    keys, counts = np.unique(flat[:: max(1, flat.shape[0] // 400000)], axis=0, return_counts=True)
    report = []
    for idx in np.argsort(-counts)[:flat_top]:
        rgb = tuple(int(v) for v in keys[idx])
        c, s = best(rgb)
        m = np.all(a == keys[idx], axis=-1)
        if m.sum() < 500: continue
        cmyk[m] = np.round(np.array(c) * 2.55).astype(np.uint8)
        report.append((rgb, c, round(s, 1), int(m.sum())))
    return Image.fromarray(cmyk, "CMYK"), report

def save_tif(img, out, dpi):
    img.save(out, compression="tiff_lzw", dpi=(dpi, dpi), icc_profile=ICC_BYTES)

def cmd_map(key):
    lines = [l.strip() for l in open(D / f"{key}_colors.txt", encoding="utf-8") if l.strip()]
    rows = []
    for l in lines:
        rgb = tuple(int(v) for v in l.split(","))
        c, s = best(rgb); rows.append(list(rgb) + list(c))
        print(f"  {rgb} → {c}  ΔE {s:.1f}  (표준 {std(rgb)} ΔE {de2000(lab_rgb(rgb), lab_cmyk(std(rgb))):.1f})")
    ras = {}   # "가로x세로" → tif (같은 그림이 판마다 복제돼 있어 픽셀 크기로 짝짓는다)
    man = D / f"{key}_rasters.txt"
    for l in (open(man, encoding="utf-8").read().split("\n") if man.exists() else []):
        if not l.strip(): continue
        px, py, _tr = l.split("|"); dim = f"{px}x{py}"
        im = Image.open(D / f"{key}_{dim}.png").convert("RGB").resize((int(px), int(py)), Image.LANCZOS)
        c, rep = to_cmyk(im)   # 그림 전체는 표준 변환, 넓은 단색 면은 최적값
        name = f"{key}_{dim}.tif"; save_tif(c, D / name, 72); ras[dim] = name
        print(f"  그림 {dim}: 단색 {[(r[0], r[1], r[2]) for r in rep[:3]]}")
    js = "var CMAP = " + str(rows) + ";\nvar RAS = " + json.dumps(ras) + ";\n"
    (D / f"{key}_map.js").write_text(js, encoding="utf-8")
    print(f"{key}: 색 {len(rows)}개, 그림 {len(ras)}개 → {key}_map.js")

def cmd_pdf(pdf, page, W, H, dpi, out):
    import fitz
    p = fitz.open(pdf)[int(page) - 1]
    px = round(float(W) / 25.4 * int(dpi)); py = round(float(H) / 25.4 * int(dpi))
    pix = p.get_pixmap(matrix=fitz.Matrix(px / p.rect.width, py / p.rect.height), alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).resize((px, py), Image.LANCZOS)
    c, rep = to_cmyk(img); save_tif(c, out, int(dpi))
    print(f"{out}: {px}x{py}px CMYK, 단색 {len(rep)}개 최적화")
    for r in rep[:12]: print("   ", r)

def cmd_img(src, W, H, dpi, out):
    img = Image.open(src)
    px = round(float(W) / 25.4 * int(dpi)); py = round(float(H) / 25.4 * int(dpi))
    c, rep = to_cmyk(img.convert("RGB").resize((px, py), Image.LANCZOS)); save_tif(c, out, int(dpi))
    print(f"{out}: {px}x{py}px CMYK, 단색 {len(rep)}개 최적화")

if __name__ == "__main__":
    {"map": cmd_map, "pdf": cmd_pdf, "img": cmd_img}[sys.argv[1]](*sys.argv[2:])

"""회사 폴더의 .ai 원본 로고 → 고해상도 CMYK TIFF (2026-10-16, 일러 없이 pymupdf 로).

저해상도 PNG(굿모닝아이텍 190px 등)를 바꾸려고 만든다. .ai 를 PDF 로 열어 CMYK 그대로 그린다.
페이지에 로고가 여러 개면(78리서치랩 CI 안내 페이지, 소만사 흰색/파란색) CROP 으로 그 로고 자리만 고른다(단위 pt).
흰 여백은 저해상도로 먼저 재서 잘라 내고, 로고 폭이 TARGET_PX 가 되게 다시 그린다.
"""
import zipfile
from pathlib import Path

import fitz
from PIL import Image

HERE = Path(__file__).parent
BASE = Path(r"Z:\01. 진행중인작업\▶ 06. 2Group_1Part\[11.04-05] 2026 부산 사이버보안 콘퍼런스\01. 실행\04. 전시\02. 전시기업 자료")
AIDIR = HERE / "로고_ai원본"
OUT = HERE / "로고"
ICC = r"C:\Windows\System32\spool\drivers\color\JapanColor2001Coated.icc"
TARGET_PX = 6000

# 연번 → (.ai 경로, 고를 영역 pt [x0, y0, x1, y1] 또는 None = 페이지 전체)
SRC = {
    16: (AIDIR / "굿모닝아이텍로고.ai", None),            # zip 안의 .ai 를 꺼내 둔 것
    1: (BASE / "03. (주)78리서치랩" / "78ResearchLab_최종cs.ai", (430, 80, 670, 155)),   # CI 안내 페이지의 첫 로고(흰 바탕용)
    17: (BASE / "08. 넥스원소프트(주)" / "01 CI_Normal_Blue.ai", None),
    11: (BASE / "16. 위드네트웍스" / "AI_로고_위드네트웍스 (작은 글씨 X).ai", None),
    18: (BASE / "13. 스패로우" / "Sparrow_CI_Color.ai", None),
    5: (BASE / "10. 소만사" / "소만사 신규로고_흰색 파란색.ai", (80, 250, 515, 375)),     # 파란색 로고만 (흰색 판은 흰 간판에 안 보임)
    4: (BASE / "06. 비테크놀로지" / "비테크놀로지-로고CI.ai", None),
    12: (BASE / "18. 윈스테크넷" / "WINSTECHNET_발주용.ai", None),
    # 2026-10-19 김태영님 전달: NNSP·우리아이티 .ai. 10번은 2025 처럼 좌 시스코 | 우 우리아이티 (2사 틀)
    9: (BASE / "17. NNSP" / "NNSP_CI1 (1).ai", None),
    "10_1": (BASE / "23. (주)우리아이티" / "시스코 로고_cisco logo (1).ai", (440, 70, 760, 250)),   # 오른쪽 위 하늘색 (2025 간판과 같은 색)
    "10_2": (BASE / "23. (주)우리아이티" / "우리아이티 로고1.ai", (170, 1230, 620, 1590)),       # 맨 아래 큰 WIT 심볼 (2025 간판과 같은 판)
}


def ink_box(pix):
    """저해상도 RGB 렌더에서 흰색 아닌 부분의 상자(픽셀)."""
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    px = im.load(); xs, ys = [], []
    for y in range(pix.height):
        for x in range(pix.width):
            if min(px[x, y]) < 240:
                xs.append(x); ys.append(y)
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def render(no, path, crop):
    page = fitz.open(path)[0]
    area = fitz.Rect(crop) if crop else page.rect
    z0 = 1200 / area.width
    low = page.get_pixmap(matrix=fitz.Matrix(z0, z0), clip=area, alpha=False)
    x0, y0, x1, y1 = ink_box(low)
    ink = fitz.Rect(area.x0 + x0 / z0, area.y0 + y0 / z0, area.x0 + x1 / z0, area.y0 + y1 / z0)
    pad = ink.width * 0.01
    ink = fitz.Rect(ink.x0 - pad, ink.y0 - pad, ink.x1 + pad, ink.y1 + pad) & page.rect
    z = TARGET_PX / ink.width
    pix = page.get_pixmap(matrix=fitz.Matrix(z, z), clip=ink, colorspace=fitz.csCMYK, alpha=False)
    im = Image.frombytes("CMYK", (pix.width, pix.height), pix.samples)
    tag = f"{no:02d}_1" if isinstance(no, int) else no
    dst = OUT / f"{tag}_ai_cmyk.tif"
    im.save(dst, compression="tiff_lzw", icc_profile=open(ICC, "rb").read(), dpi=(300, 300))
    prev = page.get_pixmap(matrix=fitz.Matrix(800 / ink.width, 800 / ink.width), clip=ink, alpha=False)
    prev.save(str(Path(r"C:\Users\PSH\AppData\Local\Temp\bsg\aiprev") / f"cut_{tag}.png"))
    return dst, im.size


def main():
    AIDIR.mkdir(exist_ok=True)
    z = zipfile.ZipFile(BASE / "02. 굿모닝아이텍" / "로고_굿모닝아이텍(ai,png).zip")
    for i in z.infolist():
        if i.filename.lower().endswith(".ai"):
            (AIDIR / "굿모닝아이텍로고.ai").write_bytes(z.read(i))
    for no, (path, crop) in SRC.items():
        dst, size = render(no, path, crop)
        print(f"{no} {path.name} → {dst.name} {size[0]}x{size[1]}px CMYK")


if __name__ == "__main__":
    main()

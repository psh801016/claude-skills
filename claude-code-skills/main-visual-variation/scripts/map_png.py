"""3D 맵 PNG — 빌드 결과(C:/mvv/out/<key>.ai)의 맵 대지(2번째 대지 = 판 크기)를 <맵 이름>.png 로 map 폴더에 뽑는다. 일러 없이 pymupdf.

사내 관행 (INWEPF 2026 08 3D/map, ASURA님이 직접 뽑아 둔 것 실측 2026-10-23):
  품목 대지 1개 = PNG 1장 · 이름 = 품목 이름 · 1/10 시트를 144ppi(일러 내보내기 200%) · 투명 배경(RGBA) · 여유 포함 판 전체
시트 회색 바탕('시트 바탕')·여유 표시 ㄱ·ㄴ('여유 표시') 레이어는 끄고 뽑는다 — 3D 텍스처에 섞이면 안 된다.
같은 이름 PNG 가 이미 있으면 건너뛴다(--force 일 때만 덮어씀) — ASURA님이 손으로 뽑아 둔 파일을 지우지 않게.

실행: python map_png.py <map 폴더> <key> [<key> ...] [--force]
"""
import sys
from pathlib import Path

import fitz
from PIL import Image

OUT = Path("C:/mvv/out")
HIDE = ("시트 바탕", "여유 표시")
PPI = 144


def hide_layers(doc, names):
    """PDF 레이어 끄기 — doc.set_layer(-1, off=…) 는 렌더에 반영되지 않았다(2026-10-23 test 에서 회색 바탕이 남음). UI 설정으로 끈다."""
    for u in doc.layer_ui_configs():
        if u["text"] in names and u["on"]:
            doc.set_layer_ui_config(u["number"], action=2)


def render(ai: Path):
    doc = fitz.open(ai)
    hide_layers(doc, HIDE)
    pg = doc[1] if len(doc) > 1 else doc[0]       # 2번째 대지 = 맵 대지
    z = PPI / 72
    pix = pg.get_pixmap(matrix=fitz.Matrix(z, z), alpha=True)
    return Image.frombytes("RGBA", (pix.width, pix.height), pix.samples), pg.rect


def main(map_dir, keys, force):
    d = Path(map_dir)
    for k in keys:
        ai = OUT / f"{k}.ai"; mt = OUT / f"{k}.map.txt"
        if not mt.exists():
            print(f"SKIP {k}: 맵 이름 없음(빌드에 map 대지가 없음)"); continue
        name = mt.read_text(encoding="utf-8").strip()
        dst = d / f"{name}.png"
        if dst.exists() and not force:
            print(f"SKIP {dst.name}: 이미 있음 (--force 로 덮어쓰기)"); continue
        im, r = render(ai)
        im.save(dst, dpi=(PPI, PPI))
        print(f"{dst.name}: {im.size[0]}x{im.size[1]}px (대지 {r.width * 25.4 / 72:.1f}x{r.height * 25.4 / 72:.1f}mm, {PPI}ppi)")


def test():
    # 2쪽 PDF: 1쪽 = 시트(회색 바탕 레이어), 2쪽 = 맵 대지 → 2쪽을 144ppi 로, 숨김 레이어 빼고
    import tempfile
    p = Path(tempfile.mkdtemp()) / "t.ai"
    doc = fitz.open()
    ocg = doc.add_ocg("시트 바탕", on=True)
    a = doc.new_page(width=200, height=100)
    b = doc.new_page(width=72, height=144)            # 25.4 x 50.8 mm
    b.draw_rect(b.rect, color=None, fill=(0.5, 0.5, 0.5), oc=ocg)
    doc.save(p)
    im, _ = render(p)
    assert im.size == (144, 288), im.size              # 72pt → 144px
    assert im.getpixel((10, 10))[3] == 0, "시트 바탕 레이어가 꺼지지 않음"
    print("OK map_png")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["test"]:
        test(); sys.exit()
    force = "--force" in a
    a = [x for x in a if x != "--force"]
    main(a[0], a[1:], force)

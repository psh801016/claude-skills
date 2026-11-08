"""KOBC·BMFW 2026 발주 PPTX — 사내 양식(부산 사이버보안_(공감발주).pptx) 그대로: 16:9, 표지 1장 + 그룹마다 그림 1장.
그림 = kobc_order.jsx 가 만든 흰 바탕 그룹 시트 jpg(그룹 이름 크게 + 판마다 이름/재질/WxHmm/수량 라벨).
  python make_pptx.py <out.pptx>
"""
import sys
from pptx import Presentation
from pptx.util import Pt, Emu
from pptx.enum.text import PP_ALIGN
from PIL import Image

OUT = sys.argv[1]
GROUPS = ["메인무대", "포토존1", "포토존2", "등록데스크", "로비LED"]
prs = Presentation()
prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)       # 16:9 (참고본 960x540pt)
blank = prs.slide_layouts[6]


def tbox(slide, text, top, size, bold=False, color=(0, 0, 0)):
    tb = slide.shapes.add_textbox(0, top, prs.slide_width, Pt(size * 1.6))
    p = tb.text_frame.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = text; r.font.size = Pt(size); r.font.bold = bold
    from pptx.dml.color import RGBColor
    r.font.color.rgb = RGBColor(*color); r.font.name = "맑은 고딕"


s = prs.slides.add_slide(blank)
tbox(s, "KOBC BADA · BMFW 2026", Pt(150), 48, bold=True)
tbox(s, "2026. 11. 03.(화) 발주   —   전 품목 목공 (불칼질, 상하좌우 100mm 포함)", Pt(235), 20)
tbox(s, "담당자 : (                                   )", Pt(268), 16, color=(120, 120, 120))

M = Emu(300000)
for g in GROUPS:
    img = f"C:/mvv/out/{g}_발주.jpg"
    w, h = Image.open(img).size
    s = prs.slides.add_slide(blank)
    bw, bh = prs.slide_width - 2 * M, prs.slide_height - 2 * M
    k = min(bw / w, bh / h)
    pw, ph = int(w * k), int(h * k)
    s.shapes.add_picture(img, int((prs.slide_width - pw) / 2), int((prs.slide_height - ph) / 2), pw, ph)
prs.save(OUT)
print("PPTX_OK", OUT, len(prs.slides._sldIdLst), "장")

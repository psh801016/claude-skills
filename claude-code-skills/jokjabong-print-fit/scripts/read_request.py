"""요청서 PPTX → 기업·재질·사이즈·수량 표와 슬라이드별 경로·메모를 텍스트로 뽑는다.
사용: python -X utf8 read_request.py "<요청서.pptx>" > request.txt  (콘솔은 한글이 깨지니 파일로 받는다)"""
import sys
from pptx import Presentation
from pptx.util import Emu
p = Presentation(sys.argv[1])
print("slide size mm", p.slide_width/36000, p.slide_height/36000)
for i,s in enumerate(p.slides,1):
    print(f"\n===== SLIDE {i}")
    for sh in s.shapes:
        t = sh.shape_type
        if sh.has_text_frame and sh.text_frame.text.strip():
            print(f"[text] {sh.text_frame.text.strip()!r}")
        if getattr(sh,'has_table',False) and sh.has_table:
            for r in sh.table.rows:
                print("[row] " + " | ".join(c.text.strip().replace('\n','/') for c in r.cells))
        if t == 13:
            print(f"[pic] {sh.name} {sh.image.filename} {sh.image.size}")
        if t == 6:
            for g in sh.shapes:
                if g.has_text_frame and g.text_frame.text.strip(): print(f"  [gtext] {g.text_frame.text.strip()!r}")

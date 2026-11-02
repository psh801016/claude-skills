"""요청서 PPTX → 슬라이드별 글·표·그림(해시) 덤프. 차수가 바뀌면(1021→1022) 두 판을 덤프해 diff 로 비교한다.
1022 판부터 요청서가 '새 작업 필요 / 수정 필요 / 확인 완료' 구분 슬라이드로 나뉜다 — 수정 슬라이드의 메모 그림(업체 메일 캡처)까지 꺼내 읽는다.
사용: python -X utf8 diff_request.py <요청서.pptx> > req_<차수>.txt"""
import sys, hashlib
from pptx import Presentation
p = Presentation(sys.argv[1])
def walk(shs):
    for s in shs:
        if s.shape_type == 6: yield from walk(s.shapes)
        else: yield s
for i, s in enumerate(p.slides, 1):
    print(f"===== SLIDE {i}")
    for sh in walk(s.shapes):
        if getattr(sh, "has_table", False) and sh.has_table:
            for r in sh.table.rows: print("[row] " + " | ".join(c.text.strip().replace("\n", "/") for c in r.cells))
        elif sh.has_text_frame and sh.text_frame.text.strip():
            print("[text] " + sh.text_frame.text.strip().replace("\x0b", " ").replace("\n", " / "))
        elif sh.shape_type == 13:
            print(f"[pic] {hashlib.md5(sh.image.blob).hexdigest()[:8]} {sh.image.size}")

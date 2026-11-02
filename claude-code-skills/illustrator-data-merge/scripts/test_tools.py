"""일러 없이 도는 회귀 테스트 — 2026-10-21 부산 부스간판 32장 작업에서 터진 것들.

사고 배경:
- 한 줄 코드 중간에 `//` 주석을 넣어 그 뒤 `}` 까지 주석이 됐고, 일러에서 'catch/finally without try' 로
  스크립트가 아예 안 돌았다(fix_wing.jsx). 일러를 띄우기 전에 잡았어야 했다 → 모든 .jsx 문법 검사.
- ExtendScript 에 없는 `Array.indexOf` 를 써서 reorder.jsx 가 'is not a function' 으로 멈췄다 → 배열 indexOf 금지 검사.
- 다른 파일 날개 디자인을 벡터 복제하면 반투명·겹침이 빠져서 대지를 CMYK TIFF 로 뽑기로 했다
  → render_artboard_tif.py 가 실물 픽셀 수·CMYK·축척 dpi 를 맞게 쓰는지.
실행: py -3 test_tools.py   (node 필요 — 없으면 문법 검사만 건너뛰고 알린다)
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import fitz
from PIL import Image

HERE = Path(__file__).resolve().parent
JSX = sorted(list(HERE.glob("*.jsx")) + list((HERE.parent / "examples").rglob("*.jsx")))


def test_jsx_syntax():
    node = shutil.which("node")
    if not node:
        print("SKIP 문법 검사: node 없음")
        return
    bad = []
    for f in JSX:
        src = f.read_text(encoding="utf-8-sig")
        r = subprocess.run([node, "-e", "new Function(require('fs').readFileSync(process.argv[1],'utf8').replace(/^\\uFEFF/,''))", str(f)],
                           capture_output=True, text=True, encoding="utf-8")
        if r.returncode:
            bad.append(f"{f.name}: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else r.returncode}")
    assert not bad, "문법 오류:\n" + "\n".join(bad)
    print(f"OK 문법 {len(JSX)}개")


def test_no_array_indexof():
    # 문자열 indexOf 는 ES3 에도 있다. 배열에 쓰던 꼴(tops.indexOf / arr.indexOf(숫자변수))만 막는다.
    pat = re.compile(r"\b(tops|arr|list|names|seen)\.indexOf\(")
    hits = [f"{f.name}:{i}" for f in JSX for i, line in enumerate(f.read_text(encoding="utf-8-sig").splitlines(), 1)
            if pat.search(line) and "//" not in line.split("indexOf")[0]]
    assert not hits, "배열 indexOf (ExtendScript 에 없음): " + ", ".join(hits)
    print("OK 배열 indexOf 없음")


def test_render_artboard_tif():
    sys.path.insert(0, str(HERE))
    import render_artboard_tif as rt
    d = Path(tempfile.mkdtemp())
    pdf = d / "face.pdf"
    doc = fitz.open()
    pg = doc.new_page(width=45 * 72 / 25.4, height=323 * 72 / 25.4)       # 1/10 축척 날개 한 면 45x323mm
    pg.draw_rect(pg.rect, color=None, fill=(0.0, 0.3, 0.7))
    pg.insert_text((20, 400), "2026", fontsize=40, color=(1, 1, 1))
    doc.save(pdf)
    out = d / "face.tif"
    size, w, h = rt.render(str(pdf), 1, 450, 120, 10, str(out))
    im = Image.open(out)
    assert im.mode == "CMYK", im.mode
    assert abs(im.size[0] - round(450 / 25.4 * 120)) <= 1, im.size
    assert abs(im.size[1] / im.size[0] - 323 / 45) < 0.01, im.size
    assert round(im.info["dpi"][0]) == 1200, im.info.get("dpi")             # 1/10 문서에 넣으면 45mm 로 들어간다
    assert abs(im.size[0] / im.info["dpi"][0] * 25.4 - 45) < 0.2
    print(f"OK 대지 TIFF {im.size} CMYK dpi {float(im.info['dpi'][0]):.0f}")


if __name__ == "__main__":
    test_jsx_syntax()
    test_no_array_indexof()
    test_render_artboard_tif()
    print("전부 통과")

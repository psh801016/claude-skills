"""illustrator-data-merge 회귀 테스트.

배경(2026-10-15): 디자이너맘 영상의 사원증 자동배치를 스킬로 옮기면서 깨지기 쉬운 곳 세 군데를 박아 둔다.
  - '@사진' 머리글: 엑셀에서 손으로 치면 @ 가 수식으로 먹혀 작은따옴표가 필요했다. CSV 를 직접 쓰므로
    머리글이 정확히 '@사진' 인지 본다.
  - 한글 경로·인코딩: 한글 파일명 사진 경로가 일러에서 깨지지 않아야 한다.
  - 사진 누락: 명단에 있는데 사진이 없으면 조용히 빈 카드가 나오지 않게 exit 1.
--ai 를 주면 켜진 일러스트레이터(COM)로 실제 import → 배치까지 돌리고 결과 PNG 를 남긴다.
테스트 데이터는 임시 폴더에만 만든다(작업 파일·명단 오염 없음).

  py -3 test_merge.py          # CSV 단위 검사
  py -3 test_merge.py --ai     # + 일러스트레이터 실구동
"""
import csv
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_csv  # noqa: E402

PEOPLE = [("디자인팀", "이은영", (300, 400)), ("마케팅팀", "이재훈", (400, 300)),
          ("개발팀", "박정은", (300, 300)), ("재무팀", "최현우", (200, 500))]


def make_fixture(root):
    img = root / "img"
    img.mkdir()
    for i, (_, name, size) in enumerate(PEOPLE):
        Image.new("RGB", size, (60 * i, 120, 200 - 40 * i)).save(img / f"{name}.jpg")
    lst = root / "명단.csv"
    with open(lst, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows([["부서", "이름"]] + [[d, n] for d, n, _ in PEOPLE])
    return img, lst


def run_cli(*args):
    return subprocess.run([sys.executable, str(HERE / "make_csv.py"), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8",
                          env={**os.environ, "PYTHONIOENCODING": "utf-8"})   # 실행 셸 콘솔 인코딩과 무관하게


def test_csv(root):
    img, lst = make_fixture(root)
    out = root / "list_ai.csv"
    r = run_cli(img, "--list", lst, "-o", out)
    assert r.returncode == 0, r.stderr
    assert "비율이 다른 사진 3장" in r.stderr and "이은영" not in r.stderr, r.stderr
    rows = list(csv.reader(out.read_text(encoding="utf-8-sig").splitlines()))
    assert rows[0] == ["부서", "이름", "@사진"], rows[0]
    assert len(rows) == 1 + len(PEOPLE)
    for row in rows[1:]:
        p = Path(row[2])
        assert p.is_absolute() and p.exists() and p.stem == row[1], row

    (img / "최현우.jpg").unlink()                   # 누락 → exit 1, 이름이 찍혀야 함
    r = run_cli(img, "--list", lst, "-o", root / "miss.csv")
    assert r.returncode == 1 and "최현우" in r.stderr, (r.returncode, r.stderr)

    r = run_cli(img, "-o", root / "auto.csv")       # 명단 없이 폴더만
    rows = list(csv.reader((root / "auto.csv").read_text(encoding="utf-8-sig").splitlines()))
    assert rows[0] == ["이름", "@사진"] and len(rows) == len(PEOPLE), rows
    print("CSV 검사 통과")


HARNESS = r"""
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var R = {};
var doc = app.documents.add(DocumentColorSpace.CMYK, 400, 500);
try {
    var g = doc.groupItems.add();
    var clip = g.groupItems.add();
    var ph = clip.placedItems.add(); ph.file = File(%(first)s);
    ph.width = 150; ph.height = 200; ph.position = [100, -60];
    var frame = clip.pathItems.rectangle(-60, 100, 150, 200);
    frame.move(clip, ElementPlacement.PLACEATBEGINNING);
    clip.clipped = true;
    var t1 = g.textFrames.add(); t1.contents = "부서"; t1.position = [100, -280];
    var t2 = g.textFrames.add(); t2.contents = "이름"; t2.position = [100, -310];
    var v1 = doc.variables.add(); v1.kind = VariableKind.TEXTUAL; v1.name = "부서"; t1.contentVariable = v1;
    var v2 = doc.variables.add(); v2.kind = VariableKind.TEXTUAL; v2.name = "이름"; t2.contentVariable = v2;
    var v3 = doc.variables.add(); v3.kind = VariableKind.IMAGE; v3.name = "사진"; ph.contentVariable = v3;

    doc.importVariables(File(%(csv)s));
    R.vars = []; for (var i = 0; i < doc.variables.length; i++) R.vars.push(doc.variables[i].name);
    R.sets = doc.dataSets.length;

    $.global.DM_NO_MAIN = true;
    $.evalFile(File(%(layout)s));
    R.laid = layoutDatasets(doc, g);

    R.cards = [];
    for (var k = 0; k < doc.groupItems.length; k++) {
        var it = doc.groupItems[k];
        if (it.parent !== doc.activeLayer) continue;
        var c = { texts: [] };
        for (var t = 0; t < it.textFrames.length; t++) c.texts.push(it.textFrames[t].contents);
        var p = it.groupItems[0].placedItems[0];
        c.photo = decodeURI(p.file.name); c.pw = p.width; c.ph = p.height;
        c.bound = !!p.contentVariable;
        R.cards.push(c);
    }
    var opt = new ExportOptionsPNG24(); opt.artBoardClipping = false;
    doc.exportFile(File(%(png)s), ExportType.PNG24, opt);
} catch (e) { R.error = e.message + " (line " + e.line + ")"; }
doc.close(SaveOptions.DONOTSAVECHANGES);
function js(o) {  // ExtendScript 에 JSON 이 없어 최소 직렬화
    if (o instanceof Array) { var a = []; for (var i = 0; i < o.length; i++) a.push(js(o[i])); return "[" + a.join(",") + "]"; }
    if (typeof o === "object") { var s = []; for (var k in o) s.push(js(k) + ":" + js(o[k])); return "{" + s.join(",") + "}"; }
    if (typeof o === "string") return '"' + o.replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"';
    return String(o);
}
var f = File(%(out)s); f.encoding = "UTF-8"; f.open("w"); f.write(js(R)); f.close();
"""


def test_ai(root, keep):
    img, lst = make_fixture(root)
    csv_path = root / "list_ai.csv"
    assert run_cli(img, "--list", lst, "-o", csv_path).returncode == 0
    out, png = root / "result.txt", keep / "layout_result.png"
    js = HARNESS % {k: json.dumps(str(v).replace("\\", "/")) for k, v in dict(
        first=img / "이은영.jpg", csv=csv_path, layout=HERE / "layout_datasets.jsx",
        png=png, out=out).items()}
    jsx = root / "harness.jsx"
    jsx.write_text(js, encoding="utf-8-sig")
    ps = f"$ai = New-Object -ComObject Illustrator.Application; $ai.DoJavaScriptFile('{jsx}') | Out-Null"
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True, timeout=300)
    raw = out.read_text(encoding="utf-8-sig")
    print(raw)
    R = json.loads(raw)
    assert "error" not in R, R["error"]
    assert sorted(R["vars"]) == sorted(["부서", "이름", "사진"]), R["vars"]  # BOM 이 이름에 붙으면 여기서 깨짐
    assert R["sets"] == len(PEOPLE) and R["laid"] == len(PEOPLE), R
    assert len(R["cards"]) == len(PEOPLE), R["cards"]
    want = {n: d for d, n, _ in PEOPLE}
    assert sorted(c["photo"] for c in R["cards"]) == sorted(n + ".jpg" for n in want)
    for c in R["cards"]:
        name = c["photo"][:-4]                         # 사진·이름·부서가 같은 카드에 있어야 함
        assert sorted(c["texts"]) == sorted([name, want[name]]), c
    assert sum(c["bound"] for c in R["cards"]) == 1, "복제본은 변수 연결이 끊겨야 함"
    print(f"일러스트레이터 실구동 통과: 결과 그림: {png}")


# ── fill_template.jsx (부스간판 방식) ─────────────────────────────────────────────
# 배경(2026-10-15): 탄소중립 컨퍼런스 부스간판 30장을 손으로 복붙하다 2줄 첫 두 장 위 라벨이
# 'A1' 로 남고 박스는 'A7' 인 불일치가 실제 발주 원본에 들어 있었다. 또 첫 구현에서 머리글 루프 변수가
# 카드 높이를 덮어써 줄 간격이 반으로 줄었다. 아래는 그 둘 + 수백 장·엑셀 기본(CP949) CSV 를 잡는다.
# 주의: 일러 오류(캔버스 밖 대지 등)는 '그 스크립트 실행' 안의 변경을 통째로 되돌린다(2026-10-15 실측).
# 실제 사용처럼 단계마다 따로 실행해야 앞 단계 결과가 같이 사라지지 않는다.
JS_PRELUDE = r"""
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, R = {};
function js(o) {
    if (o === null) return "null";
    if (o instanceof Array) { var a = []; for (var i = 0; i < o.length; i++) a.push(js(o[i])); return "[" + a.join(",") + "]"; }
    if (typeof o === "object") { var s = []; for (var k in o) s.push(js(k) + ":" + js(o[k])); return "{" + s.join(",") + "}"; }
    if (typeof o === "string") return '"' + o.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\r/g, "\\r").replace(/\n/g, "\\n") + '"';
    return String(o);
}
function done() { var f = File(%(out)s); f.encoding = "UTF-8"; f.open("w"); f.write(js(R)); f.close(); }
"""
JS_BUILD = r"""
var doc = app.documents.add(DocumentColorSpace.CMYK, 2200 * MM, 900 * MM);
var L = doc.layers[0], tpl = L.groupItems.add(); tpl.name = "틀";
var top = 800 * MM, left = 50 * MM;
tpl.pathItems.rectangle(top, left, 194 * MM, 75 * MM);
var area = tpl.pathItems.rectangle(top - 16 * MM, left + 76.5 * MM, 102 * MM, 42 * MM);
area.filled = area.stroked = false; area.name = "영역";
function tf(name, txt, x, y, size, parent) { var t = parent.textFrames.add(); t.contents = txt; t.name = name;
    t.textRange.characterAttributes.size = size; t.textRange.paragraphAttributes.justification = Justification.CENTER;
    t.position = [x - t.width / 2, y]; return t; }
tf("국문", "국문샘플", left + 127.5 * MM, top - 25 * MM, 29.7, tpl);
tf("영문", "SAMPLE", left + 127.5 * MM, top - 40 * MM, 25.4, tpl);
tf("부스번호", "B1", left + 171 * MM, top - 5 * MM, 17.9, tpl);
tf("부스번호", "B1", left + 171 * MM, top + 10 * MM, 17.9, L).move(tpl, ElementPlacement.PLACEATEND);
doc.saveAs(File(%(ai)s)); doc.close(); done();
"""
JS_FILL = r"""
var doc = app.open(File(%(ai)s));
$.global.FT_NO_MAIN = true; $.evalFile(File(%(script)s));
try { R.n = fillTemplate(doc, File(%(csv)s)); doc.save(); } catch (e) { R.err = e.message; }
doc.close(SaveOptions.DONOTSAVECHANGES); done();
"""
JS_COLLECT = r"""
var doc = app.open(File(%(ai)s));
$.global.FT_NO_MAIN = true; $.evalFile(File(%(script)s));
var cv = canvasBounds(doc), ab = doc.artboards[0].artboardRect;
function mm4(a) { return [a[0] / MM, a[1] / MM, a[2] / MM, a[3] / MM]; }
R.canvas = mm4(cv); R.ab = mm4(ab);
var L = doc.layers[0], outs = 0; for (var i = 0; i < L.groupItems.length; i++) if (L.groupItems[i].name == "자동생성") outs++;
R.outs = outs; R.tplHidden = doc.pageItems.getByName("틀").hidden; R.area = 102; R.cards = [];
var res = doc.pageItems.getByName("자동생성");
for (var c = 0; c < res.groupItems.length; c++) { var g = res.groupItems[c]; if (g.parent !== res) continue;
    var vb = g.visibleBounds, o = { b: mm4(vb), x: Math.round(vb[0] / MM), y: Math.round(vb[1] / MM), h: (vb[1] - vb[3]) / MM, box: [] };
    for (var t = 0; t < g.textFrames.length; t++) { var it = g.textFrames[t], b = it.visibleBounds;
        var e = { s: it.contents, w: (b[2] - b[0]) / MM };
        if (it.parent === g && /^B\d+$/.test(it.contents) && b[3] > vb[1] - 9 * MM) o.label = e.s; else o.box.push(e); }
    R.cards.push(o); }
doc.close(SaveOptions.DONOTSAVECHANGES); done();
"""


def ai_run(root, body, **paths):
    out = root / "r.txt"
    if out.exists():
        out.unlink()
    js = (JS_PRELUDE + body) % {k: json.dumps(str(v).replace("\\", "/")) for k, v in dict(paths, out=out).items()}
    jsx = root / "step.jsx"
    jsx.write_text(js, encoding="utf-8-sig")
    ps = f"$ai = New-Object -ComObject Illustrator.Application; $ai.DoJavaScriptFile('{jsx}') | Out-Null"
    p = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, timeout=600)
    if p.returncode:
        err = p.stderr.decode("cp949", "replace").split("+ ")[0].strip()   # 일러 JS 오류 원문
        raise AssertionError(f"일러 스크립트 오류: {err}")
    return json.loads(out.read_text(encoding="utf-8-sig"))


def test_fill(root):
    long_en = 'International "Hydrogen" Fuel Cell Innovation Consortium Co., Ltd.'
    rows = [["부스번호", "국문", "영문", "수량"]]
    for i in range(1, 41):
        en = long_en if i % 8 == 0 else ("Two\nLines Inc." if i == 5 else f"COMPANY {i}")
        rows.append([f"B{i}", f"㈜테스트{i}" + ("국제수소연료전지혁신컨소시엄" if i % 7 == 0 else ""), en, "10"])
    csv_path, big = root / "signs.csv", root / "big.csv"
    with open(csv_path, "w", encoding="cp949", newline="") as f:   # 엑셀 기본 저장 형식
        csv.writer(f).writerows(rows)
    with open(big, "w", encoding="utf-8-sig", newline="") as f:     # 40줄 × 20장 = 800장 → 캔버스 초과
        csv.writer(f).writerows([rows[0]] + [r[:3] + ["20"] for r in rows[1:]])
    ai = root / "tpl.ai"
    p = dict(ai=ai, script=HERE / "fill_template.jsx")
    ai_run(root, JS_BUILD, ai=ai)
    r1 = ai_run(root, JS_FILL, csv=csv_path, **p)
    assert "err" not in r1 and r1["n"] == 400, r1
    r2 = ai_run(root, JS_FILL, csv=csv_path, **p)                   # 다시 돌려도 결과는 한 벌
    assert "err" not in r2 and r2["n"] == 400, r2
    r3 = ai_run(root, JS_FILL, csv=big, **p)
    assert "최대" in r3.get("err", "") and "800" in r3["err"], r3     # 넘치면 몇 장까지인지 알리고 멈춤
    R = ai_run(root, JS_COLLECT, **p)
    assert len(R["cards"]) == 400, len(R["cards"])                    # 멈춘 실행이 이전 결과를 지우지 않음
    cv, ab = R["canvas"], R["ab"]
    for c in R["cards"]:                                              # 전부 캔버스 안 + 대지 안
        b = c["b"]
        assert cv[0] <= b[0] and b[2] <= cv[2] and cv[3] <= b[3] and b[1] <= cv[1], (b, cv)
        assert ab[0] <= b[0] + 0.1 and b[2] <= ab[2] + 0.1 and ab[3] <= b[3] + 0.1 and b[1] <= ab[1] + 0.1, (b, ab)
    assert R["outs"] == 1 and R["tplHidden"], R
    xs = sorted({c["x"] for c in R["cards"]})
    assert len(xs) == 20, f"10열 × 2블록이어야 함: {xs}"           # 캔버스 아래가 차면 오른쪽 새 블록
    rows_y = sorted({c["y"] for c in R["cards"]}, reverse=True)
    gap = (rows_y[0] - rows_y[1]) - R["cards"][0]["h"]          # 줄 간격 버그(높이 덮어쓰기) 재발 감시
    assert abs(gap - 69) <= 1, (rows_y[:3], gap)
    per_row = {}
    for c in R["cards"]:
        per_row[(c["y"], c["x"] > xs[9])] = per_row.get((c["y"], c["x"] > xs[9]), 0) + 1
    assert max(per_row.values()) == 10, "한 줄 10장 초과 금지(출력 한계)"
    for c in R["cards"]:
        nos = [b["s"] for b in c["box"] if b["s"].startswith("B") and b["s"][1:].isdigit()]
        assert c.get("label") and nos == [c["label"]], c           # 라벨 = 박스 번호
        for b in c["box"]:
            assert b["w"] <= R["area"] + 0.5, c                     # 영역 폭 안
    two = [b["s"] for c in R["cards"] for b in c["box"] if "\r" in b["s"]]
    assert any(s.startswith("International") for s in two), "긴 영문은 두 줄로"
    assert any(s == "Two\rLines Inc." for s in two), "엑셀 칸 안 줄바꿈 유지"
    assert any('"Hydrogen"' in b["s"] for c in R["cards"] for b in c["box"]), "따옴표·쉼표 CSV 파싱"
    print("부스간판 채우기 400장 통과 (800장은 용량 초과 안내)")


# 크기가 다른 틀(틀_2940x750) + 로고 틀(틀_로고) 섞어 쓰기 (2026-10-15 ASURA님: 간판 크기·로고가 다른 것도 있다)
JS_BUILD_MULTI = r"""
var doc = app.documents.add(DocumentColorSpace.CMYK, 2200 * MM, 900 * MM), L = doc.layers[0];
function tf(name, txt, x, y, size, parent) { var t = parent.textFrames.add(); t.contents = txt; t.name = name;
    t.textRange.characterAttributes.size = size; t.textRange.paragraphAttributes.justification = Justification.CENTER;
    t.position = [x - t.width / 2, y]; return t; }
function mk(name, wmm, top, logo) {
    var g = L.groupItems.add(); g.name = name; var left = 50 * MM;
    g.pathItems.rectangle(top, left, wmm * MM, 75 * MM);
    var a = g.pathItems.rectangle(top - 16 * MM, left + (wmm - 102) * MM / 2 + (logo ? 25 * MM : 0), 102 * MM, 42 * MM);
    a.filled = a.stroked = false; a.name = "영역";
    if (logo) { var b = g.pathItems.rectangle(top - 10 * MM, left + 10 * MM, 40 * MM, 40 * MM); b.filled = b.stroked = false; b.name = "로고"; }
    var cx = left + wmm * MM / 2 + (logo ? 25 * MM : 0);
    tf("국문", "국문샘플", cx, top - 25 * MM, 29.7, g); tf("영문", "SAMPLE", cx, top - 40 * MM, 25.4, g);
    tf("부스번호", "B1", left + (wmm - 23) * MM, top - 5 * MM, 17.9, g);
}
mk("틀", 194, 800 * MM, false); mk("틀_2940x750", 294, 650 * MM, false); mk("틀_로고", 194, 500 * MM, true);
doc.saveAs(File(%(ai)s)); doc.close(); done();
"""
JS_COLLECT_MULTI = r"""
var doc = app.open(File(%(ai)s)), res = doc.pageItems.getByName("자동생성");
R.hidden = []; var names = ["틀", "틀_2940x750", "틀_로고"];
for (var i = 0; i < names.length; i++) R.hidden.push(doc.pageItems.getByName(names[i]).hidden);
R.cards = [];
for (var c = 0; c < res.groupItems.length; c++) { var g = res.groupItems[c]; if (g.parent !== res) continue;
    var vb = g.geometricBounds, o = { x: vb[0] / MM, y: Math.round(vb[1] / MM), w: Math.round((vb[2] - vb[0]) / MM), texts: [], logo: null };
    for (var t = 0; t < g.textFrames.length; t++) o.texts.push(g.textFrames[t].contents);
    if (g.rasterItems.length) { var rb = g.rasterItems[0].geometricBounds; o.logo = [(rb[0] - vb[0]) / MM, (vb[1] - rb[1]) / MM, (rb[2] - rb[0]) / MM, (rb[1] - rb[3]) / MM]; }
    R.cards.push(o); }
doc.close(SaveOptions.DONOTSAVECHANGES); done();
"""


def test_fill_multi(root):
    for n, size in (("wide.png", (400, 100)), ("tall.png", (100, 300))):
        Image.new("RGB", size, (200, 30, 30)).save(root / n)
    rows = [["부스번호", "국문", "영문", "틀", "로고", "수량"],
            ["A1", "㈜가", "AAA", "", "", "2"],
            ["A2", "㈜나", "BBB", "2940x750", "", "3"],
            ["A3", "㈜다", "CCC", "", "wide.png", "1"],                 # 로고 있음 → 틀_로고, 상대경로
            ["A4", "㈜라", "DDD", "", str(root / "tall.png"), "12"],  # 절대경로, 10장 넘음 → 두 줄
            ["A5", "㈜마", "EEE", "", "", "1"]]
    csv_path = root / "multi.csv"
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(rows)
    ai = root / "multi.ai"
    p = dict(ai=ai, script=HERE / "fill_template.jsx")
    ai_run(root, JS_BUILD_MULTI, ai=ai)
    r1 = ai_run(root, JS_FILL, csv=csv_path, **p)
    assert "err" not in r1 and r1["n"] == 19, r1
    R = ai_run(root, JS_COLLECT_MULTI, ai=ai)
    assert R["hidden"] == [True, True, True], R["hidden"]
    cards = R["cards"]
    by = lambda pred: [c for c in cards if pred(c)]
    assert len(by(lambda c: c["w"] == 294)) == 3, "2940 틀 3장"
    logo_cards = by(lambda c: c["logo"])
    assert len(logo_cards) == 13, len(logo_cards)                      # A3 1장 + A4 12장
    for c in logo_cards:                                               # 로고 상자(10,10,40x40) 안 · 비율 유지
        x, y, w, h = c["logo"]
        assert 9.9 <= x and x + w <= 50.1 and 9.9 <= y and y + h <= 50.1, c
        assert abs(max(w, h) - 40) < 0.2, c
        assert abs(w / h - (4 if "CCC" in c["texts"] else 1 / 3)) < 0.02, c
    rows_by_y = {}
    for c in cards:
        rows_by_y.setdefault((c["y"], round(c["x"] // 3000)), []).append(c)
    for row in rows_by_y.values():                                     # 한 줄에 크기만 안 섞임, 10장 이하
        assert len(row) <= 10 and len({c["w"] for c in row}) == 1, row
    counts = sorted(len(r) for r in rows_by_y.values())
    # 같은 크기(194)는 틀이 달라도 엑셀 순서대로 이어 붙인다: A1×2, A3, A4×12, A5 = 16장 → 10 + 6 / 2940 3장
    # (2026-10-15 부산: 틀별로 줄을 나눠 06·14 가 맨 아래 한 장씩 떨어졌다 — ASURA님 "10개 붙여서 두라 했는데")
    assert counts == [3, 6, 10], counts
    first = sorted(by(lambda c: c["w"] == 194), key=lambda c: (-c["y"], c["x"]))
    names = [next(t for t in c["texts"] if t in "AAA BBB CCC DDD EEE".split()) for c in first]
    assert names == ["AAA", "AAA", "CCC"] + ["DDD"] * 12 + ["EEE"], names
    print("여러 틀·로고 채우기 통과")


# 부산 사이버보안 부스간판(2026-10-15) 실파일에서 터진 두 가지:
#  ① 틀이 '클리핑 그룹'(배경 이미지가 간판 밖으로 넘침)이라 visibleBounds 로 재면 간판 폭이 368mm(실제 293)로 잡힘
#  ② .ai 로고를 place→embed 하면 그림이 깨지고(심볼 조각·글자 두 겹) 흰 대지 여백 때문에 작아짐 → 열어서 PNG 로 뽑아 넣는다
#  ③ 간판 위 검정 번호 라벨(출력소 확인용)이 빠짐 → 클리핑 간판 + 라벨을 묶음 그룹 '틀'로. 간격은 여전히 클리핑 폭
JS_BUILD_CLIP = r"""
var lg = app.documents.add(DocumentColorSpace.CMYK, 200 * MM, 100 * MM), ab = lg.artboards[0].artboardRect;
var bg = lg.pathItems.rectangle(ab[1], ab[0], 200 * MM, 100 * MM); var w = new CMYKColor(); bg.fillColor = w; bg.stroked = false;
var red = lg.pathItems.rectangle(ab[1] - 40 * MM, ab[0] + 50 * MM, 100 * MM, 20 * MM); var rc = new CMYKColor(); rc.magenta = 100; rc.yellow = 100; red.fillColor = rc;
lg.saveAs(File(%(logo)s)); lg.close();
var doc = app.documents.add(DocumentColorSpace.CMYK, 1000 * MM, 300 * MM), L = doc.layers[0];
var wrapG = L.groupItems.add(); wrapG.name = "틀";           // 묶음: 클리핑 간판 + 간판 위 검정 번호 라벨
var g = wrapG.groupItems.add();
var top = 250 * MM, left = 50 * MM;
var lb = wrapG.textFrames.add(); lb.contents = "B1"; lb.name = "부스번호"; lb.position = [left + 170 * MM, top + 10 * MM];
var over = g.pathItems.rectangle(top + 20 * MM, left - 30 * MM, 254 * MM, 115 * MM); over.fillColor = rc;   // 간판 밖으로 넘치는 장식
var bx = g.pathItems.rectangle(top - 10 * MM, left + 10 * MM, 40 * MM, 40 * MM); bx.filled = bx.stroked = false; bx.name = "로고";
var t = g.textFrames.add(); t.contents = "B1"; t.name = "부스번호"; t.position = [left + 150 * MM, top - 5 * MM];
var clip = g.pathItems.rectangle(top, left, 194 * MM, 75 * MM); clip.move(g, ElementPlacement.PLACEATBEGINNING);
g.clipped = true;
doc.saveAs(File(%(ai)s)); doc.close(); done();
"""
JS_COLLECT_CLIP = r"""
var doc = app.open(File(%(ai)s)), res = doc.pageItems.getByName("자동생성"); R.cards = [];
function rasters(x, a) { for (var i = 0; i < x.pageItems.length; i++) { var it = x.pageItems[i]; if (it.parent !== x) continue;
    if (it.typename == "RasterItem") a.push(it); else if (it.typename == "GroupItem") rasters(it, a); } return a; }
function texts(x, a) { for (var i = 0; i < x.pageItems.length; i++) { var it = x.pageItems[i]; if (it.parent !== x) continue;
    if (it.typename == "TextFrame") a.push(it.contents); else if (it.typename == "GroupItem") texts(it, a); } return a; }
function clipOf(x) {                       // 묶음 그룹(간판 + 라벨)이면 클리핑 사각형은 한 단계 안쪽에 있다
    if (x.clipped) { for (var i = 0; i < x.pathItems.length; i++) if (x.pathItems[i].clipping) return x.pathItems[i].geometricBounds; }
    for (var j = 0; j < x.groupItems.length; j++) if (x.groupItems[j].parent === x) { var b = clipOf(x.groupItems[j]); if (b) return b; }
    return null; }
for (var c = 0; c < res.groupItems.length; c++) { var g = res.groupItems[c]; if (g.parent !== res) continue;
    var cb = clipOf(g);
    var rs = rasters(g, []), o = { x: cb[0] / MM, w: (cb[2] - cb[0]) / MM, n: rs.length, t: texts(g, []) };
    if (rs.length) { var rb = rs[0].geometricBounds; o.logo = [(rb[0] - cb[0]) / MM, (cb[1] - rb[1]) / MM, (rb[2] - rb[0]) / MM, (rb[1] - rb[3]) / MM]; }
    R.cards.push(o); }
R.open = app.documents.length;
doc.close(SaveOptions.DONOTSAVECHANGES); done();
"""


def test_clip_and_vector_logo(root):
    ai, logo, csv_path = root / "clip.ai", root / "logo.ai", root / "c.csv"
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows([["부스번호", "로고", "수량"], ["B1", "logo.ai", "3"]])
    ai_run(root, JS_BUILD_CLIP, ai=ai, logo=logo)
    r1 = ai_run(root, JS_FILL, csv=csv_path, ai=ai, script=HERE / "fill_template.jsx")
    assert "err" not in r1 and r1["n"] == 3, r1
    R = ai_run(root, JS_COLLECT_CLIP, ai=ai)
    assert R["open"] == 1, "로고 원본 문서가 열린 채 남음"
    xs = sorted(c["x"] for c in R["cards"])
    assert all(abs((b - a) - 194) < 0.5 for a, b in zip(xs, xs[1:])), xs        # ① 간판 간격 = 클리핑 폭
    for c in R["cards"]:
        x, y, w, h = c["logo"]
        assert c["n"] == 1 and abs(w - 40) < 0.5 and abs(w / h - 5) < 0.3, c    # ② 흰 바탕 빼고 100x20 비율(바탕 남으면 2)
        assert c["t"] == ["B1", "B1"], c                                         # ③ 간판 안 배지 + 간판 위 라벨 둘 다 채움
        assert 9.5 <= x and x + w <= 50.5 and 9.5 <= y and y + h <= 50.5, c
    print("클리핑 틀·벡터 로고 통과")


def test_excel(root):
    """2026-10-15 받은 '홍보부스 참가기업 LIST' 모양: 제목 줄 + 2줄 병합 머리글 + 백월디자인·컨펌 칸."""
    from openpyxl import Workbook
    import excel_to_csv
    wb = Workbook(); ws = wb.active
    ws.append(["제10회 탄소중립 국제 컨퍼런스 홍보부스 참가기업 LIST"])
    ws.append(["NO", "기관명", None, "백월 디자인", "컨펌"])
    ws.append([None, "국문", "영문", None, None])
    ws.merge_cells("A2:A3"); ws.merge_cells("B2:C2"); ws.merge_cells("D2:D3"); ws.merge_cells("E2:E3")
    ws.append(["A1", "㈜한국중부발전", "KOMIPO", "요청완료", None])
    ws.append(["A2", "리벨리온㈜", "Rebellions", "○", "확정"])
    ws.append(["A12", "충남산학융합원", "Chungnam Institute Of\nIndustry-University Convergence", "○", "통보"])
    ws.append([None, None, None, None, None])
    ws.append(["A20", " ㈜비전이노베이션 ", "Vision Innovation Co., Ltd", "요청완료", None])
    src = root / "list.xlsx"; wb.save(src)
    head, rows, notes = excel_to_csv.convert(src, qty={"A1": 2, "A20": 3})   # 부스 2칸·3칸 = 간판 2·3장
    assert head == ["부스번호", "국문", "영문", "수량"], head
    assert rows == [["A1", "㈜한국중부발전", "KOMIPO", "2"], ["A2", "리벨리온㈜", "Rebellions", "1"],
                    ["A12", "충남산학융합원", "Chungnam Institute Of Industry-University Convergence", "1"],
                    ["A20", "㈜비전이노베이션", "Vision Innovation Co., Ltd", "3"]], rows
    assert not notes, notes

    # 크기 다른 간판(사이즈 칸) + 부스수 칸 + 로고 폴더 (2026-10-15 ASURA님: 크기·로고가 다른 간판도 있다)
    ws.cell(2, 6, "사이즈"); ws.cell(2, 7, "부스수")
    ws.cell(4, 6, "1940x750"); ws.cell(4, 7, 2); ws.cell(8, 6, "2940 x 750")
    wb.save(src)
    logos = root / "logos"; logos.mkdir()
    for n in ("KOMIPO.png", "(주)비전이노베이션.ai", "readme.txt"):
        (logos / n).write_bytes(b"x")
    head, rows, notes = excel_to_csv.convert(src, logos=logos)
    assert head == ["부스번호", "국문", "영문", "틀", "로고", "수량"], head
    assert [r[3] for r in rows] == ["1940x750", "", "", "2940 x 750"], rows
    assert [r[-1] for r in rows] == ["2", "1", "1", "1"], rows
    assert Path(rows[0][4]).name == "KOMIPO.png" and Path(rows[3][4]).name == "(주)비전이노베이션.ai", rows
    assert rows[1][4] == "" and any("A2" in n and "로고 없음" in n for n in notes), notes
    print("엑셀 변환 검사 통과")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        test_csv(Path(d))
    with tempfile.TemporaryDirectory() as d:
        test_excel(Path(d))
    if "--ai" in sys.argv:
        with tempfile.TemporaryDirectory() as d:
            test_ai(Path(d), Path(tempfile.gettempdir()))
        with tempfile.TemporaryDirectory() as d:
            test_fill(Path(d))
        with tempfile.TemporaryDirectory() as d:
            test_fill_multi(Path(d))
        with tempfile.TemporaryDirectory() as d:
            test_clip_and_vector_logo(Path(d))

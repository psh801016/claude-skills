// 2026-10-21 김태영님 요청: 12번(시스코 | 우리아이티) 간판 "로고 2개 사이에 막대기 말고 x 자 표시로".
// 두 회사형 틀의 가운데 세로 구분선(폭 ~0, 높이 ~27mm, 간판 가운데)을 지우고 같은 중심에 X(선 두 개)를 그린다.
// 다른 간판은 손대지 않는다(전후 대조). X 크기·굵기·색은 구분선에 맞춤: 8mm, 1.5pt, K60.
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, out = [];
var RESULT = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/원본/부스간판.ai";
var SK = "C:/Users/PSH/.agents/skills/illustrator-data-merge/scripts/";
var TARGET = "시스코", XSIZE = 8, XSTROKE = 1.5, XGRAY = 60;
$.global.FT_NO_MAIN = true;
$.evalFile(File(SK + "fill_template.jsx"));
$.evalFile(File(SK + "sign_tools.jsx"));

var busy = false;
for (var d = 0; d < app.documents.length; d++) if (/^부스간판\.ai$/.test(app.documents[d].name)) busy = true;
if (busy) out.push("부스간판.ai 가 열려 있음 — 중단");
else {
    var doc = app.open(File(RESULT));
    try {
        var res = doc.pageItems.getByName("자동생성"), cards = kids(res), before = [], hit = [];
        for (var c = 0; c < cards.length; c++) { var r = stInfo(cards[c]); before.push(r.key); if (r.name == TARGET) hit.push(c); }
        if (hit.length != 1) throw new Error("'" + TARGET + "' 간판이 " + hit.length + "장");
        var card = cards[hit[0]], cb = stClipOf(card).geometricBounds, cx = (cb[0] + cb[2]) / 2, lines = [];
        stWalk(card, function (it) {
            if (it.typename != "PathItem" || !it.stroked || it.filled) return;
            var b = it.geometricBounds, w = (b[2] - b[0]) / MM, h = (b[1] - b[3]) / MM, mx = (b[0] + b[2]) / 2;
            if (w < 1 && h > 20 && h < 32 && Math.abs(mx - cx) < 3 * MM) lines.push(it);
        });
        if (lines.length != 1) throw new Error("가운데 구분선 " + lines.length + "개");
        var lb = lines[0].geometricBounds, mx = (lb[0] + lb[2]) / 2, my = (lb[1] + lb[3]) / 2, par = lines[0].parent;
        lines[0].remove();
        var k = new CMYKColor(); k.black = XGRAY;
        var s = XSIZE / 2 * MM, pts = [[[mx - s, my + s], [mx + s, my - s]], [[mx - s, my - s], [mx + s, my + s]]];
        for (var i = 0; i < 2; i++) {
            var p = par.pathItems.add(); p.setEntirePath(pts[i]);
            p.filled = false; p.stroked = true; p.strokeWidth = XSTROKE; p.strokeColor = k; p.strokeCap = StrokeCap.ROUNDENDCAP;
        }
        out.push("구분선 지움 → X " + XSIZE + "mm (간판 " + (hit[0] + 1) + "번째, 번호 " + stInfo(card).num + ")");
        var after = kids(res), changed = 0;
        for (c = 0; c < after.length; c++) if (stInfo(after[c]).key != before[c]) changed++;
        out.push("간판 " + after.length + "장 / 내용 바뀐 간판 " + changed);
        if (after.length == 32 && changed == 0) { doc.save(); out.push("saved"); } else out.push("검사 불통과 — 저장 안 함");
    } catch (e) { out.push("ERROR " + e.message + " line " + e.line); }
    doc.close(SaveOptions.DONOTSAVECHANGES);
}
var g = File(Folder.temp.fsName + "/bsg_x.txt"); g.encoding = "UTF-8"; g.open("w"); g.write(out.join("\n")); g.close();

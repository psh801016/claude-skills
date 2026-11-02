// 드림시큐리티 로고만 키운다 (2026-10-18, ASURA님 "드림시큐리티 로고는 네가 키워").
// 세로로 긴 로고라 높이 26mm 상자에 막혀 작았다 → 가운데는 그대로, 높이 34mm(글자 영역 높이)까지 비율 유지 확대. 다른 간판은 손대지 않는다.
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, out = [], H = 34;
var RESULT = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/원본/부스간판.ai";
function kids(g) { var a = []; for (var i = 0; i < g.pageItems.length; i++) if (g.pageItems[i].parent === g) a.push(g.pageItems[i]); return a; }
function walk(g, fn) { var k = kids(g); for (var i = 0; i < k.length; i++) { fn(k[i]); if (k[i].typename == "GroupItem") walk(k[i], fn); } }
function mm(b) { return [Math.round(b[0] / MM * 10) / 10, Math.round(b[1] / MM * 10) / 10, Math.round((b[2] - b[0]) / MM * 10) / 10, Math.round((b[1] - b[3]) / MM * 10) / 10]; }
function logosAll(doc) {
    var cards = kids(doc.pageItems.getByName("자동생성")), res = [];
    for (var c = 0; c < cards.length; c++) {
        var name = "", logos = [];
        walk(cards[c], function (it) {
            if (it.typename == "TextFrame" && /[가-힣]/.test(it.contents) && !/AI시대|콘퍼런스/.test(it.contents) && !name) name = it.contents;
            if (it.typename == "RasterItem" && it.geometricBounds[2] - it.geometricBounds[0] < 200 * MM) logos.push(it);
        });
        res.push({ name: name, logos: logos });
    }
    return res;
}
var already = false;
for (var d = 0; d < app.documents.length; d++) if (app.documents[d].name == "부스간판.ai") already = true;
if (already) out.push("결과 파일이 열려 있음 — 중단");
else {
    var doc = app.open(File(RESULT));
    try {
        var before = logosAll(doc), done = 0;
        for (var c = 0; c < before.length; c++) out.push("전 " + (c + 1) + " " + before[c].name + " " + before[c].logos.length + " " + (before[c].logos.length ? mm(before[c].logos[0].geometricBounds).join(",") : "-"));
        for (c = 0; c < before.length; c++) {
            if (before[c].name != "(주)드림시큐리티") continue;
            if (before[c].logos.length != 1) { out.push("로고 " + before[c].logos.length + "개 — 중단"); break; }
            var it = before[c].logos[0], b = it.geometricBounds, k = H * MM / (b[1] - b[3]) * 100;
            it.resize(k, k, true, true, true, true, k, Transformation.CENTER);
            out.push("확대 " + Math.round(k) + "% → " + mm(it.geometricBounds).join(","));
            done++;
        }
        var after = logosAll(doc);
        for (c = 0; c < after.length; c++) out.push("후 " + (c + 1) + " " + after[c].name + " " + after[c].logos.length + " " + (after[c].logos.length ? mm(after[c].logos[0].geometricBounds).join(",") : "-"));
        var o = new ExportOptionsPNG24(); o.horizontalScale = o.verticalScale = 150; o.artBoardClipping = true;
        doc.exportFile(File(Folder.temp.fsName + "/bsg/full.png"), ExportType.PNG24, o);
        o.horizontalScale = o.verticalScale = 60;
        doc.exportFile(File("G:/내 드라이브/AI-작업기록/claude/2026-10-15_부산사이버보안_부스간판/부스간판_자동생성_미리보기.png"), ExportType.PNG24, o);
        if (done == 1) { doc.save(); out.push("saved"); } else out.push("드림 못 찾음 — 저장 안 함");
    } catch (e) { out.push("ERROR " + e.message + " line " + e.line); }
    doc.close(SaveOptions.DONOTSAVECHANGES);
}
var g = File(Folder.temp.fsName + "/bsg_dream.txt"); g.encoding = "UTF-8"; g.open("w"); g.write(out.join("\n")); g.close();

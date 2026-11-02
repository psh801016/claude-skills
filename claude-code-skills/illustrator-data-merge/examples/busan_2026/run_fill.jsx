// 부산 사이버보안 부스간판 22장 채우기 + 검증 덤프 + 미리보기 (2026-10-15)
// 결과는 매번 틀 파일에서 새로 만든다 → 이전 실행 결과가 남아 중복되는 일이 없다 (ASURA님 "중복 되어 있잖아").
// 저장 전 틀(숨김)을 지워 결과 파일엔 간판 22장 + 위 번호 라벨만 남긴다.
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, out = [];
var DIR = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/원본/";
var WORK = "G:/내 드라이브/AI-작업기록/claude/2026-10-15_부산사이버보안_부스간판/";
var doc = app.open(File(WORK + "부스간판_틀.ai"));
doc.saveAs(File(DIR + "부스간판.ai"));
$.global.FT_NO_MAIN = true;
$.evalFile(File("C:/Users/PSH/.agents/skills/illustrator-data-merge/scripts/fill_template.jsx"));
try {
    var t0 = new Date();
    out.push("n=" + fillTemplate(doc, File(WORK + "부스간판_목록.csv")) + " sec=" + (new Date() - t0) / 1000);
    var L = doc.layers.getByName("Layer 1"), top = kids(L);
    for (var i = 0; i < top.length; i++) if (/^틀/.test(top[i].name)) top[i].remove();     // 틀 정리
    top = kids(L);
    out.push("Layer 1 top items=" + top.length + " (" + top[0].name + ")");
    var res = doc.pageItems.getByName("자동생성"), cards = kids(res);
    for (var c = 0; c < cards.length; c++) {
        var g = cards[c], cb = bounds(g), s = [], tfs = [], imgs = [];
        (function walk(x) { var k = kids(x); for (var i = 0; i < k.length; i++) {
            if (k[i].typename == "GroupItem") walk(k[i]);
            else if (k[i].typename == "TextFrame") tfs.push(k[i]);
            else if (k[i].typename == "RasterItem" && (k[i].geometricBounds[2] - k[i].geometricBounds[0]) < 200 * MM) imgs.push(k[i]); } })(g);
        for (var t = 0; t < tfs.length; t++) {
            var txt = tfs[t].contents.replace(/\r/g, "/");
            if (!/AI시대|콘퍼런스/.test(txt)) s.push(txt);
        }
        var cs = []; for (var m = 0; m < imgs.length; m++) cs.push(String(imgs[m].imageColorSpace).replace("ImageColorSpace.", ""));
        out.push((c + 1) + ") x" + Math.round(cb[0] / MM) + " y" + Math.round(cb[1] / MM) + " | " + s.join(" | ") + " | img" + imgs.length + " " + cs.join(","));
    }
    var o = new ExportOptionsPNG24(); o.horizontalScale = o.verticalScale = 60; o.artBoardClipping = true;
    doc.exportFile(File(WORK + "부스간판_자동생성_미리보기.png"), ExportType.PNG24, o);
    o.horizontalScale = o.verticalScale = 150;
    doc.exportFile(File(Folder.temp.fsName + "/bsg/full.png"), ExportType.PNG24, o);
    var cc = { RGB: 0, CMYK: 0, other: 0 };
    for (var q = 0; q < doc.rasterItems.length; q++) { var sp = String(doc.rasterItems[q].imageColorSpace); if (/CMYK/.test(sp)) cc.CMYK++; else if (/RGB/.test(sp)) cc.RGB++; else cc.other++; }
    out.push("문서 " + doc.documentColorSpace + " | 그림 전체 RGB " + cc.RGB + " / CMYK " + cc.CMYK + " / 기타 " + cc.other);
    var r = doc.artboards[0].artboardRect;
    out.push("artboard " + doc.artboards.length + " x" + Math.round(r[0] / MM) + " y" + Math.round(r[1] / MM) + " " + Math.round((r[2] - r[0]) / MM) + "x" + Math.round((r[1] - r[3]) / MM));
    doc.save();
    out.push("saved");
} catch (e) { out.push("ERROR " + e.message + " line " + e.line); }
doc.close(SaveOptions.DONOTSAVECHANGES);
var f = File(Folder.temp.fsName + "/bsg_fill.txt"); f.encoding = "UTF-8"; f.open("w"); f.write(out.join("\n")); f.close();

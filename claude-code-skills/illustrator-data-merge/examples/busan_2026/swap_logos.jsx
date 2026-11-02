// 결과 파일에서 로고 그림만 바꿔 끼운다 (2026-10-16). ASURA님이 손으로 고친 부분(드림시큐리티 크기 등)은 그대로 둔다.
// 회사 국문 이름으로 간판을 찾고, 그 간판의 로고 그림(배경보다 작은 RasterItem)을 새 CMYK TIFF 로 바꾼다.
// 새 로고는 기존 로고 자리(상자) 안에 비율 유지·가운데. 전후로 모든 간판의 위치·로고 상자를 기록해 대조한다.
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, out = [];
var RESULT = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/원본/부스간판.ai";
var LOGO = "G:/내 드라이브/AI-작업기록/claude/2026-10-15_부산사이버보안_부스간판/로고/";
var SWAP = {
    "(주)78리서치랩": "01_1_ai_cmyk.tif", "(주)비테크놀로지": "04_1_ai_cmyk.tif", "(주)소만사": "05_1_ai_cmyk.tif",
    "(주)위드네트웍스": "11_1_ai_cmyk.tif", "(주)윈스테크넷": "12_1_ai_cmyk.tif", "굿모닝아이텍(주)": "16_1_ai_cmyk.tif",
    "넥스원소프트(주)": "17_1_ai_cmyk.tif", "스패로우": "18_1_ai_cmyk.tif"
};
function kids(g) { var a = []; for (var i = 0; i < g.pageItems.length; i++) if (g.pageItems[i].parent === g) a.push(g.pageItems[i]); return a; }
function walk(g, fn) { var k = kids(g); for (var i = 0; i < k.length; i++) { fn(k[i]); if (k[i].typename == "GroupItem") walk(k[i], fn); } }
function mm(b) { return [Math.round(b[0] / MM * 10) / 10, Math.round(b[1] / MM * 10) / 10, Math.round((b[2] - b[0]) / MM * 10) / 10, Math.round((b[1] - b[3]) / MM * 10) / 10]; }
function snapshot(doc) {   // 간판마다 [이름, 로고 상자들]
    var res = doc.pageItems.getByName("자동생성"), cards = kids(res), snap = [];
    for (var c = 0; c < cards.length; c++) {
        var name = "", logos = [];
        walk(cards[c], function (it) {
            if (it.typename == "TextFrame" && /[가-힣]/.test(it.contents) && !/AI시대|콘퍼런스/.test(it.contents) && !name) name = it.contents;
            if (it.typename == "RasterItem" && it.geometricBounds[2] - it.geometricBounds[0] < 200 * MM) logos.push(it);
        });
        snap.push({ card: cards[c], name: name, logos: logos });
    }
    return snap;
}
var doc = app.open(File(RESULT));
try {
    var before = snapshot(doc), done = 0;
    for (var c = 0; c < before.length; c++) out.push("전 " + (c + 1) + " " + before[c].name + " " + (before[c].logos.length ? mm(before[c].logos[0].geometricBounds).join(",") : "-"));
    for (c = 0; c < before.length; c++) {
        var s = before[c], f = SWAP[s.name];
        if (!f) continue;
        if (s.logos.length != 1) { out.push("건너뜀(로고 " + s.logos.length + "개): " + s.name); continue; }
        var old = s.logos[0], ob = old.geometricBounds, parent = old.parent, pre = kids(parent);
        var p = parent.placedItems.add(); p.file = File(LOGO + f);
        p.move(old, ElementPlacement.PLACEBEFORE);
        p.embed();
        var post = kids(parent), nu = null;
        for (var i = 0; i < post.length && !nu; i++) { var isNew = true; for (var j = 0; j < pre.length; j++) if (post[i] === pre[j]) isNew = false; if (isNew) nu = post[i]; }
        var nb = nu.geometricBounds, k = Math.min((ob[2] - ob[0]) / (nb[2] - nb[0]), (ob[1] - ob[3]) / (nb[1] - nb[3])) * 100;
        nu.resize(k, k, true, true, true, true, k, Transformation.CENTER);
        nb = nu.geometricBounds;
        nu.translate((ob[0] + ob[2]) / 2 - (nb[0] + nb[2]) / 2, (ob[1] + ob[3]) / 2 - (nb[1] + nb[3]) / 2);
        old.remove();
        done++;
        out.push("교체 " + s.name + " ← " + f + " | 새 " + mm(nu.geometricBounds).join(",") + " " + nu.imageColorSpace);
    }
    var after = snapshot(doc);
    for (c = 0; c < after.length; c++) out.push("후 " + (c + 1) + " " + after[c].name + " " + (after[c].logos.length ? mm(after[c].logos[0].geometricBounds).join(",") + " " + after[c].logos[0].imageColorSpace : "-"));
    out.push("교체 " + done + "개");
    var o = new ExportOptionsPNG24(); o.horizontalScale = o.verticalScale = 150; o.artBoardClipping = true;
    doc.exportFile(File(Folder.temp.fsName + "/bsg/full.png"), ExportType.PNG24, o);
    o.horizontalScale = o.verticalScale = 60;
    doc.exportFile(File("G:/내 드라이브/AI-작업기록/claude/2026-10-15_부산사이버보안_부스간판/부스간판_자동생성_미리보기.png"), ExportType.PNG24, o);
    if (done == 8) { doc.save(); out.push("saved"); } else out.push("8개가 아니라 저장 안 함");
} catch (e) { out.push("ERROR " + e.message + " line " + e.line); }
doc.close(SaveOptions.DONOTSAVECHANGES);
var g = File(Folder.temp.fsName + "/bsg_swap.txt"); g.encoding = "UTF-8"; g.open("w"); g.write(out.join("\n")); g.close();

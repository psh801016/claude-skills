// 2026-10-21 기업부스날개를 그림(TIFF)으로 다시 넣기.
// 벡터 복제로는 B구역부스.ai 날개의 물결(50% 투명 그림)·입자(스크린 겹침)가 빠졌다(3회 시도).
// → B구역부스.ai 1번 대지(날개 한 면 450x3230)를 pymupdf 로 실물 120dpi CMYK TIFF 로 뽑아(wing_tif.py) 넣는다.
//   아래 = 그대로, 위 = 180도 돌림 → 450x6460 (둥글게 양면). 간판 32장·제목은 손대지 않는다.
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, out = [];
var RESULT = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/원본/부스간판.ai";
var WORK = "G:/내 드라이브/AI-작업기록/claude/2026-10-15_부산사이버보안_부스간판/";
var TIF = WORK + "로고/날개_한면_cmyk.tif";
$.global.FT_NO_MAIN = true;
$.evalFile(File("C:/Users/PSH/.agents/skills/illustrator-data-merge/scripts/fill_template.jsx"));   // kids·bounds

function mmw(b) { return Math.round((b[2] - b[0]) / MM * 10) / 10; }
function mmh(b) { return Math.round((b[1] - b[3]) / MM * 10) / 10; }
function walk(g, fn) { var k = kids(g); for (var i = 0; i < k.length; i++) { fn(k[i]); if (k[i].typename == "GroupItem") walk(k[i], fn); } }
function key(card) {
    var t = [];
    walk(card, function (it) { if (it.typename == "TextFrame" && !/AI시대|콘퍼런스/.test(it.contents)) t.push(it.contents); });
    var b = bounds(card); return t.join(";") + "|" + Math.round(b[0]) + "," + Math.round(b[1]);
}
function placeTif(parent) {                       // 넣고 파일에 포함 → 새로 생긴 그림을 돌려준다
    var pre = kids(parent), p = parent.placedItems.add(); p.file = File(TIF); p.embed();
    var post = kids(parent);
    for (var i = 0; i < post.length; i++) { var isNew = true; for (var j = 0; j < pre.length; j++) if (post[i] === pre[j]) isNew = false; if (isNew) return post[i]; }
}

var busy = false;
for (var d = 0; d < app.documents.length; d++) if (/^부스간판\.ai$/.test(app.documents[d].name)) busy = true;
if (busy) out.push("부스간판.ai 가 열려 있음 — 중단");
else {
    var doc = app.open(File(RESULT));
    try {
        var res = doc.pageItems.getByName("자동생성"), L = res.layer, cards = kids(res), before = [];
        for (var c = 0; c < cards.length; c++) before.push(key(cards[c]));
        var old = null, top = kids(L);
        for (var i = 0; i < top.length; i++) if (top[i].name == "기업부스날개") old = top[i];
        if (!old) throw new Error("기존 기업부스날개 없음");
        var ob = bounds(old), X = ob[0], Y = ob[1];
        old.remove();

        var wing = L.groupItems.add(); wing.name = "기업부스날개";
        var lower = placeTif(wing), upper = placeTif(wing);
        var fit = function (it) {                  // 45x323mm 로
            var b = it.geometricBounds, k = 45 * MM / (b[2] - b[0]) * 100;
            it.resize(k, k, true, true, true, true, k, Transformation.TOPLEFT);
        };
        fit(lower); fit(upper); upper.rotate(180);
        var ub = upper.geometricBounds; upper.translate(X - ub[0], Y - ub[1]); ub = upper.geometricBounds;
        var lb = lower.geometricBounds; lower.translate(X - lb[0], ub[3] - lb[1]);
        var wb = bounds(wing);
        var rs = 0; walk(wing, function (it) { if (it.typename == "RasterItem" && it.imageColorSpace == ImageColorSpace.CMYK) rs++; });   // embed 가 그룹으로 감쌀 수 있다
        out.push("날개 " + mmw(wb) + "x" + mmh(wb) + "mm / CMYK 그림 " + rs + "개");

        var after = kids(res), changed = 0;
        for (c = 0; c < after.length; c++) if (key(after[c]) != before[c]) changed++;
        out.push("간판 " + after.length + "장 / 바뀐 간판 " + changed);
        var ok = after.length == 32 && changed == 0 && Math.abs(mmw(wb) - 45) < 1 && Math.abs(mmh(wb) - 646) < 2 && rs == 2;
        if (ok) { doc.save(); out.push("saved"); } else out.push("검사 불통과 — 저장 안 함");
    } catch (e) { out.push("ERROR " + e.message + " line " + e.line); }
    doc.close(SaveOptions.DONOTSAVECHANGES);
}
var g = File(Folder.temp.fsName + "/bsg_wtif.txt"); g.encoding = "UTF-8"; g.open("w"); g.write(out.join("\n")); g.close();

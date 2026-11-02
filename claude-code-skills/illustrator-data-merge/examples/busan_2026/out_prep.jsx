// 2026-10-23 출력 준비 1단계 (원본 부스간판.ai).
//  ① 기업부스날개를 150ppi 두 장으로 교체: 아래 = 그대로, 위 = 파이썬에서 미리 180도 돌린 그림 → 일러에서 돌리지 않으니 이음매가 없다.
//     두 장을 45x323mm 로 똑같이 맞추고 0.05mm(실물 0.5mm) 겹친다.
//  ② 간판 32장(+ 데스크 띠지 같은 다른 출력물)의 테두리(클리핑) 위치를 대지 기준 pt 로 기록 → 파이썬이 그 영역만 150ppi 로 뽑는다.
// 간판은 '자동생성' 묶음 이름이 아니라 모양으로 찾는다(ASURA님이 묶음을 풀고 레이어 이름을 바꿈, 10-23). 간판 내용은 손대지 않는다(전후 대조).
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, out = [];
var RESULT = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/원본/부스간판.ai";
var WORK = "G:/내 드라이브/AI-작업기록/claude/2026-10-15_부산사이버보안_부스간판/";
var SK = "C:/Users/PSH/.agents/skills/illustrator-data-merge/scripts/";
$.global.FT_NO_MAIN = true;
$.evalFile(File(SK + "fill_template.jsx"));
$.evalFile(File(SK + "sign_tools.jsx"));
function r1(v) { return Math.round(v / MM * 10) / 10; }

var busy = false;
for (var d = 0; d < app.documents.length; d++) if (/^부스간판(_출)?\.ai$/.test(app.documents[d].name)) busy = true;
if (busy) out.push("부스간판.ai 가 열려 있음 — 중단");
else {
    var doc = app.open(File(RESULT));
    try {
        var found = stFindSigns(doc), cards = found.signs, others = found.others, before = [], c, i;
        if (cards.length != 32) throw new Error("간판 " + cards.length + "장 (예상 32)");
        for (c = 0; c < cards.length; c++) before.push(stInfo(cards[c]).key);

        // ① 날개
        var old = doc.groupItems.getByName("기업부스날개"), L = old.layer, ob = bounds(old), X = ob[0], Y = ob[1];
        old.remove();
        var wing = L.groupItems.add(); wing.name = "기업부스날개";
        var up = stEmbed(wing, File(WORK + "출력그림/날개_위_150.tif"));
        var lo = stEmbed(wing, File(WORK + "출력그림/날개_아래_150.tif"));
        var parts = [up, lo];
        for (i = 0; i < 2; i++) { parts[i].width = 45 * MM; parts[i].height = 323 * MM; }
        up.left = X; up.top = Y;
        lo.left = X; lo.top = Y - 323 * MM + 0.05 * MM;
        var wb = bounds(wing);
        out.push("날개 " + r1(wb[2] - wb[0]) + "x" + r1(wb[1] - wb[3]) + "mm");

        // ② 위치 기록 (대지 기준 pt, 위→아래 +)
        var ab = doc.artboards[0].artboardRect, rows = ["AB\t" + (ab[2] - ab[0]) + "\t" + (ab[1] - ab[3])];
        for (c = 0; c < cards.length; c++) {
            var r = stInfo(cards[c]), cb = stClipOf(cards[c]).geometricBounds;
            rows.push(["S" + c, r.num, r.name, cb[0] - ab[0], ab[1] - cb[1], cb[2] - ab[0], ab[1] - cb[3], r.w].join("\t"));
        }
        for (c = 0; c < others.length; c++) {
            var pb = stClipPathOf(others[c]).geometricBounds;
            rows.push(["O" + c, "", others[c].name, pb[0] - ab[0], ab[1] - pb[1], pb[2] - ab[0], ab[1] - pb[3], r1(pb[2] - pb[0])].join("\t"));
            out.push("다른 출력물 " + c + ": " + r1(pb[2] - pb[0]) + "x" + r1(pb[1] - pb[3]) + "mm");
        }
        var f = File(WORK + "출력그림/간판위치.tsv"); f.encoding = "UTF-8"; f.open("w"); f.write(rows.join("\n")); f.close();

        var after = stFindSigns(doc).signs, changed = 0;
        for (c = 0; c < after.length; c++) if (stInfo(after[c]).key != before[c]) changed++;
        out.push("간판 " + after.length + "장 / 다른 출력물 " + others.length + " / 바뀐 간판 " + changed + " / 위치 " + (rows.length - 1) + "줄");
        if (after.length == 32 && changed == 0 && Math.abs((wb[1] - wb[3]) / MM - 645.95) < 0.5) { doc.save(); out.push("saved"); }
        else out.push("검사 불통과 — 저장 안 함");
    } catch (e) { out.push("ERROR " + e.message + " line " + e.line); }
    doc.close(SaveOptions.DONOTSAVECHANGES);
}
var g = File(Folder.temp.fsName + "/bsg_prep.txt"); g.encoding = "UTF-8"; g.open("w"); g.write(out.join("\n")); g.close();

// 2026-10-21 간판을 번호순으로 다시 놓기 (번호는 파란 배치도 그대로 — ASURA님 "파란배치도 따라서 하라고").
// 정면 24장: 01→22 (08 안랩 2장 나란히), 공공협력존 04 국제식물검역인증원은 맨 끝. 10장씩 줄.
// 옆간판 8장: 번호순, 공공 04 맨 끝. 자리만 옮기고 내용은 그대로(전후 대조).
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, out = [];
var RESULT = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/원본/부스간판.ai";
$.global.FT_NO_MAIN = true;
$.evalFile(File("C:/Users/PSH/.agents/skills/illustrator-data-merge/scripts/fill_template.jsx"));   // kids·bounds

function walk(g, fn) { var k = kids(g); for (var i = 0; i < k.length; i++) { fn(k[i]); if (k[i].typename == "GroupItem") walk(k[i], fn); } }
function info(card) {
    var r = { card: card, name: "", num: "", txt: [] };
    walk(card, function (it) {
        if (it.typename != "TextFrame" || /AI시대|콘퍼런스/.test(it.contents)) return;
        if (/^\d+$/.test(it.contents)) r.num = it.contents;
        else { r.txt.push(it.contents); if (/[가-힣]/.test(it.contents) && !r.name) r.name = it.contents; }
    });
    r.b = bounds(card); r.w = Math.round((r.b[2] - r.b[0]) / MM * 10) / 10;
    r.key = r.num + "|" + r.txt.join(";");
    r.sort = (r.name == "국제식물검역인증원" ? 100 : 0) + parseInt(r.num, 10);   // 공공협력존은 맨 끝
    return r;
}

var busy = false;
for (var d = 0; d < app.documents.length; d++) if (/^부스간판\.ai$/.test(app.documents[d].name)) busy = true;
if (busy) out.push("부스간판.ai 가 열려 있음 — 중단");
else {
    var doc = app.open(File(RESULT));
    try {
        var res = doc.pageItems.getByName("자동생성"), cards = kids(res), F = [], S = [];
        for (var c = 0; c < cards.length; c++) { var r = info(cards[c]); (Math.abs(r.w - 293) < 1 ? F : S).push(r); }
        if (F.length != 24 || S.length != 8) throw new Error("정면 " + F.length + " / 옆 " + S.length);
        // 지금 칸 자리 (왼쪽 위 기준): 정면은 줄 위쪽 값 3개, 옆은 한 줄
        var X0 = 1e9, PITCH = 293 * MM, tops = [], SX0 = 1e9, STOP = null, SW = 243.5 * MM;
        for (c = 0; c < F.length; c++) { X0 = Math.min(X0, F[c].b[0]); var t = Math.round(F[c].b[1]), seen = false; for (var q = 0; q < tops.length; q++) if (tops[q] == t) seen = true; if (!seen) tops.push(t); }   // ExtendScript 에는 indexOf 가 없다
        tops.sort(function (a, b) { return b - a; });
        for (c = 0; c < S.length; c++) { SX0 = Math.min(SX0, S[c].b[0]); STOP = S[c].b[1]; }
        if (tops.length != 3) throw new Error("정면 줄이 " + tops.length + "개");
        var before = {}; for (c = 0; c < cards.length; c++) { var k0 = info(cards[c]).key; before[k0] = (before[k0] || 0) + 1; }

        function byNum(a, b) { return a.sort - b.sort; }
        F.sort(byNum); S.sort(byNum);
        for (c = 0; c < F.length; c++) F[c].card.translate(X0 + (c % 10) * PITCH - F[c].b[0], tops[Math.floor(c / 10)] - F[c].b[1]);
        for (c = 0; c < S.length; c++) S[c].card.translate(SX0 + c * SW - S[c].b[0], STOP - S[c].b[1]);

        // 검사: 내용 그대로 + 줄마다 왼→오 번호순
        var after = kids(res), now = {}, rows = {}, errs = [];
        for (c = 0; c < after.length; c++) {
            var a = info(after[c]); now[a.key] = (now[a.key] || 0) + 1;
            var rk = (Math.abs(a.w - 293) < 1 ? "F" : "S") + Math.round(a.b[1]);
            (rows[rk] = rows[rk] || []).push(a);
        }
        for (var k in before) if (before[k] != now[k]) errs.push("내용 달라짐: " + k);
        var order = [];
        for (k in rows) {
            rows[k].sort(function (a, b) { return a.b[0] - b.b[0]; });
            var line = []; for (c = 0; c < rows[k].length; c++) { line.push((rows[k][c].name == "국제식물검역인증원" ? "공" : "") + rows[k][c].num); if (c && rows[k][c].sort < rows[k][c - 1].sort) errs.push(k + " 순서 틀림"); }
            order.push(k.charAt(0) + " " + line.join(" "));
        }
        out.push(order.join("\n"));
        out.push("문제 " + errs.length); for (c = 0; c < errs.length; c++) out.push("  ! " + errs[c]);
        if (!errs.length) { doc.save(); out.push("saved"); } else out.push("검사 불통과 — 저장 안 함");
    } catch (e) { out.push("ERROR " + e.message + " line " + e.line); }
    doc.close(SaveOptions.DONOTSAVECHANGES);
}
var g = File(Folder.temp.fsName + "/bsg_reorder.txt"); g.encoding = "UTF-8"; g.open("w"); g.write(out.join("\n")); g.close();

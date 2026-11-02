// 2026-10-21 발주 정리판처럼 묶음 제목 + 기업부스날개 넣기. ASURA님 "타이틀 명칭·사이즈 넣고, 참고 파일 날개 디자인 그대로 넣고".
//  - 제목 3개: 조립부스간판 / 기본부스간판 옆날개 / 기업부스날개 (2025 참고판 이름). 크기·재질·수량 줄 포함.
//  - 날개: B구역부스.ai 의 450x6460 (현수막 둥글게 양면 = 한 장을 반 접어 기둥 하나 감쌈) 디자인을 그대로 복제, 1개 + 수량 29EA.
//    29 = 3D 기준 24 (01~03 4 · 04~11 10 · 섬 서 5 · 섬 동 5) + 아래 줄(04공공·14·13·12) 5 — ASURA님 확정.
//  - 옆간판 줄은 제목 자리만큼 아래로 내린다. 간판 내용은 손대지 않는다(전후 덤프로 확인).
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, out = [];
var RESULT = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/원본/부스간판.ai";
var BZONE = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/원본/B구역부스.ai";
var WORK = "G:/내 드라이브/AI-작업기록/claude/2026-10-15_부산사이버보안_부스간판/";
var WINGS = 29, SIDE_DROP = 70;      // 옆간판 줄을 70mm 더 내려 제목 자리 확보
$.global.FT_NO_MAIN = true;
$.evalFile(File("C:/Users/PSH/.agents/skills/illustrator-data-merge/scripts/fill_template.jsx"));   // kids·bounds

function walk(g, fn) { var k = kids(g); for (var i = 0; i < k.length; i++) { fn(k[i]); if (k[i].typename == "GroupItem") walk(k[i], fn); } }
function key(card) {
    var t = [], l = [];
    walk(card, function (it) {
        if (it.typename == "TextFrame" && !/AI시대|콘퍼런스/.test(it.contents)) t.push(it.contents.replace(/\r/g, "/"));
        if (it.typename == "RasterItem" && it.geometricBounds[2] - it.geometricBounds[0] < 200 * MM) {
            var b = it.geometricBounds; l.push(Math.round((b[2] - b[0]) / MM * 10) / 10 + "x" + Math.round((b[1] - b[3]) / MM * 10) / 10);
        }
    });
    return t.join(" ; ") + " | " + l.join(" ; ");
}
function mmw(b) { return Math.round((b[2] - b[0]) / MM * 10) / 10; }
function mmh(b) { return Math.round((b[1] - b[3]) / MM * 10) / 10; }
function addText(layer, s, size, font, x, top) {
    var t = layer.textFrames.add(); t.contents = s;
    t.textRange.characterAttributes.textFont = font;
    t.textRange.characterAttributes.size = size;
    var k = new CMYKColor(); k.black = 100; t.textRange.characterAttributes.fillColor = k;
    var b = t.visibleBounds; t.translate(x - b[0], top - b[1]);
    return t;
}
function title(layer, name, lines, x, bottom, font) {    // 제목 묶음: 맨 아래가 bottom 에 오게
    var g = layer.groupItems.add(); g.name = "제목_" + name;
    var y = 0, items = [addText(g, name, 60, font, x, 0)];
    for (var i = 0; i < lines.length; i++) items.push(addText(g, lines[i], 26, font, x, 0));
    for (i = 0; i < items.length; i++) { var b = items[i].visibleBounds; items[i].translate(0, y - b[1]); y -= (b[1] - b[3]) + (i == 0 ? 4 : 2) * MM; }
    var gb = g.visibleBounds; g.translate(0, bottom - gb[3]);
    return g;
}

var busy = false;
for (var d = 0; d < app.documents.length; d++) if (/^(부스간판|B구역부스)\.ai$/.test(app.documents[d].name)) busy = true;
if (busy) out.push("부스간판.ai 또는 B구역부스.ai 가 열려 있음 — 중단 (ASURA님 창은 건드리지 않는다)");
else {
    var bdoc = app.open(File(BZONE)), doc = null;
    try {
        // 대지 위 객체 선택은 앞에 떠 있는 문서에만 먹는다 → B구역부스를 연 직후, 결과 파일을 열기 전에 찾는다
        bdoc.activate();
        for (var l = 0; l < bdoc.layers.length; l++) { bdoc.layers[l].locked = false; bdoc.layers[l].visible = true; }   // 저장 안 함
        // 날개 원본 찾기: 폭 45mm·높이 646mm 안팎 (1/10 축척 450x6460).
        // ★ bdoc.pageItems 전체를 하나씩 재면 조각이 수만 개라 일러가 멈췄다(2026-10-21, 26GB·응답 없음 → 강제 종료).
        //   대지마다 '대지 위 객체 선택'으로 맨 위 묶음만 받아 잰다.
        var cand = [];
        for (var a = 0; a < bdoc.artboards.length && !cand.length; a++) {
            bdoc.artboards.setActiveArtboardIndex(a);
            bdoc.selection = null;
            bdoc.selectObjectsOnActiveArtboard();
            var sel = bdoc.selection;
            for (var i = 0; i < sel.length; i++) {
                var b = sel[i].geometricBounds;
                if (Math.abs(mmw(b) - 45) < 3 && Math.abs(mmh(b) - 646) < 15) cand.push(sel[i]);
            }
            out.push("대지 " + (a + 1) + ": 맨 위 객체 " + sel.length + "개");
        }
        // 정리판 대지(체험부스 간판·날개 450x6460)에는 날개가 묶음 없이 조각으로 흩어져 있다(2026-10-21 실측 2,504개).
        // 세로 300mm 넘는 가는 조각으로 날개 기둥 범위를 잡고, 그 안에 든 조각만 모아 한 묶음으로 만든다(B구역부스.ai 는 저장 안 함).
        if (!cand.length) {
            var best = -1, most = 0;
            for (a = 0; a < bdoc.artboards.length; a++) {
                bdoc.artboards.setActiveArtboardIndex(a); bdoc.selection = null; bdoc.selectObjectsOnActiveArtboard();
                if (bdoc.selection.length > most) { most = bdoc.selection.length; best = a; }
            }
            bdoc.artboards.setActiveArtboardIndex(best); bdoc.selection = null; bdoc.selectObjectsOnActiveArtboard();
            var sel2 = [], U = null;
            for (i = 0; i < bdoc.selection.length; i++) sel2.push(bdoc.selection[i]);
            bdoc.selection = null;
            for (i = 0; i < sel2.length; i++) {
                var gb = sel2[i].geometricBounds;
                if (mmh(gb) > 300 && mmw(gb) < 50) U = U ? [Math.min(U[0], gb[0]), Math.max(U[1], gb[1]), Math.max(U[2], gb[2]), Math.min(U[3], gb[3])] : gb;
            }
            if (!U) throw new Error("정리판 대지에서 세로로 긴 날개 조각을 못 찾음");
            out.push("날개 기둥 범위 " + mmw(U) + "x" + mmh(U) + "mm");
            var tol = 1 * MM, pick = [];
            for (i = 0; i < sel2.length; i++) {
                var pb = sel2[i].geometricBounds;
                if (pb[0] >= U[0] - tol && pb[2] <= U[2] + tol && pb[1] <= U[1] + tol && pb[3] >= U[3] - tol) pick.push(sel2[i]);
            }
            var wg = sel2[0].layer.groupItems.add(); wg.name = "날개_모음";
            for (i = pick.length - 1; i >= 0; i--) pick[i].move(wg, ElementPlacement.PLACEATBEGINNING);   // 쌓임 순서 유지
            out.push("날개 조각 " + pick.length + "개를 한 묶음으로 → " + mmw(wg.geometricBounds) + "x" + mmh(wg.geometricBounds) + "mm");
            if (Math.abs(mmw(wg.geometricBounds) - 45) < 3 && Math.abs(mmh(wg.geometricBounds) - 646) < 15) cand.push(wg);
        }
        bdoc.selection = null;
        out.push("날개 후보 " + cand.length + "개" + (cand.length ? " (" + mmw(cand[0].geometricBounds) + "x" + mmh(cand[0].geometricBounds) + " " + cand[0].typename + ")" : ""));
        if (!cand.length) throw new Error("B구역부스.ai 에서 450x6460 날개를 못 찾음");
        doc = app.open(File(RESULT));

        var res = doc.pageItems.getByName("자동생성"), L = res.layer, cards = kids(res), before = [];
        for (var c = 0; c < cards.length; c++) before.push(key(cards[c]));
        if (cards.length != 32) throw new Error("간판 " + cards.length + "장 (예상 32)");
        var b0 = bounds(cards[0]), X0 = b0[0], Y0 = b0[1];
        var font = null;
        walk(cards[0], function (t) { if (!font && t.typename == "TextFrame" && /^\d+$/.test(t.contents)) font = t.textRange.characterAttributes.textFont; });

        // 옆간판 줄 내리기
        for (c = 24; c < 32; c++) cards[c].translate(0, -SIDE_DROP * MM);
        var sideTop = bounds(cards[24])[1], frontRight = bounds(cards[9])[2];

        title(L, "조립부스간판", ["2930x750mm / 현수막 / 상하단 바미싱", "각 1EA · 총 24EA (08 안랩 통합부스 2EA)"], X0, Y0 + 12 * MM, font);
        title(L, "기본부스간판 옆날개", ["2435x750mm / 현수막 / 상하단 바미싱", "각 1EA · 총 8EA"], X0, sideTop + 12 * MM, font);

        // 날개: 정면 간판 오른쪽 300mm, 첫 줄 높이에 맞춰
        var w = cand[0].duplicate(L, ElementPlacement.PLACEATEND), wb = w.geometricBounds;
        w.translate(frontRight + 300 * MM - wb[0], Y0 - wb[1]); w.name = "기업부스날개";
        title(L, "기업부스날개", ["450x6460mm", "현수막 / 둥글게 양면", WINGS + "EA"], frontRight + 300 * MM, Y0 + 12 * MM, font);

        // 검사: 간판 32장 내용 그대로
        var after = kids(res), changed = 0;
        for (c = 0; c < after.length; c++) if (key(after[c]) != before[c]) changed++;
        var tb = L.groupItems.getByName("제목_기업부스날개").visibleBounds, wb2 = w.geometricBounds;
        out.push("간판 " + after.length + "장 / 내용 바뀐 간판 " + changed + " / 날개 " + mmw(wb2) + "x" + mmh(wb2) + " / 글꼴 " + (font ? font.name : "없음"));
        var ok = after.length == 32 && changed == 0 && Math.abs(mmh(wb2) - 646) < 15;

        // 대지: 전부 + 여백
        var u = null, all = kids(L);
        for (c = 0; c < all.length; c++) { if (all[c].hidden) continue; var q = all[c].visibleBounds; u = u ? [Math.min(u[0], q[0]), Math.max(u[1], q[1]), Math.max(u[2], q[2]), Math.min(u[3], q[3])] : q; }
        var m = 30 * MM; doc.artboards[0].artboardRect = [u[0] - m, u[1] + m, u[2] + m, u[3] - m];
        var o = new ExportOptionsPNG24(); o.horizontalScale = o.verticalScale = 100; o.artBoardClipping = true;
        doc.exportFile(File(Folder.temp.fsName + "/bsg/full.png"), ExportType.PNG24, o);
        if (ok) {
            o.horizontalScale = o.verticalScale = 50;
            doc.exportFile(File(WORK + "부스간판_미리보기.png"), ExportType.PNG24, o);
            doc.save(); out.push("saved");
        } else out.push("검사 불통과 — 저장 안 함");
    } catch (e) { out.push("ERROR " + e.message + " line " + e.line); }
    if (doc) doc.close(SaveOptions.DONOTSAVECHANGES);
    bdoc.close(SaveOptions.DONOTSAVECHANGES);
}
var g = File(Folder.temp.fsName + "/bsg_title.txt"); g.encoding = "UTF-8"; g.open("w"); g.write(out.join("\n")); g.close();

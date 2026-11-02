// 2026-10-23 원본 부스간판.ai 수정 (ASURA님 "2번 스샷 것도 간판에 추가시키고 수정해라", 김용만님 "띠지 켈지로").
//  ① 데스크 띠지 설명 '현수막' → '켈지' (크기·수량 그대로)
//  ② B구역부스.ai 2·3번 대지(체험부스 간판 2930x750: 부산광역시 / 부산정보산업진흥원 AI·디지털체험)를 살아 있는 오브젝트로 복사.
//     대지마다 맨 위 객체를 한 묶음으로 → 대지 크기 클리핑(대지 밖 배경 잘림) → 원본의 옆간판 줄 아래 새 줄 + 제목 '체험부스 간판'.
//     클리핑된 맨 위 묶음이라 출력 단계(stFindSigns)에서 '다른 출력물'로 잡혀 150ppi 그림이 된다.
// B구역부스.ai 는 저장하지 않는다. 기존 간판 32장은 손대지 않는다(전후 대조).
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, out = [];
var RESULT = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/원본/부스간판.ai";
var BZONE = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/원본/B구역부스.ai";
var SK = "C:/Users/PSH/.agents/skills/illustrator-data-merge/scripts/";
$.global.FT_NO_MAIN = true;
$.evalFile(File(SK + "fill_template.jsx"));
$.evalFile(File(SK + "sign_tools.jsx"));
function r1(v) { return Math.round(v / MM * 10) / 10; }

var busy = false;
for (var d = 0; d < app.documents.length; d++) if (/^(부스간판|부스간판_출|B구역부스)\.ai$/.test(app.documents[d].name)) busy = true;
if (busy) out.push("부스간판.ai 또는 B구역부스.ai 가 열려 있음 — 중단");
else {
    var bdoc = app.open(File(BZONE)), doc = null;
    try {
        // B구역: 대지 2·3 의 맨 위 객체를 묶고 대지 크기로 클리핑 (선택 명령은 앞 문서에만 먹는다 → 먼저)
        bdoc.activate();
        for (var l = 0; l < bdoc.layers.length; l++) { bdoc.layers[l].locked = false; bdoc.layers[l].visible = true; }
        app.executeMenuCommand("unlockAll"); app.executeMenuCommand("showAll");
        var faces = [];
        for (var a = 1; a <= 2; a++) {
            bdoc.artboards.setActiveArtboardIndex(a); bdoc.selection = null; bdoc.selectObjectsOnActiveArtboard();
            var sel = []; for (var i = 0; i < bdoc.selection.length; i++) sel.push(bdoc.selection[i]);
            bdoc.selection = null;
            var g = sel[0].layer.groupItems.add();
            for (i = sel.length - 1; i >= 0; i--) sel[i].move(g, ElementPlacement.PLACEATBEGINNING);
            var ar = bdoc.artboards[a].artboardRect;
            var cp = g.pathItems.rectangle(ar[1], ar[0], ar[2] - ar[0], ar[1] - ar[3]);
            cp.move(g, ElementPlacement.PLACEATBEGINNING); cp.filled = false; cp.stroked = false; g.clipped = true;
            var cb = stClipPathOf(g).geometricBounds;
            out.push("B구역 대지 " + (a + 1) + ": 객체 " + sel.length + "개 → " + r1(cb[2] - cb[0]) + "x" + r1(cb[1] - cb[3]) + "mm");
            if (Math.abs(r1(cb[2] - cb[0]) - 293) > 1 || Math.abs(r1(cb[1] - cb[3]) - 75) > 1) throw new Error("체험부스 간판 크기가 293x75 가 아님");
            faces.push(g);
        }

        doc = app.open(File(RESULT));
        var found = stFindSigns(doc), cards = found.signs, before = [], c;
        if (cards.length != 32) throw new Error("간판 " + cards.length + "장");
        for (c = 0; c < cards.length; c++) before.push(stInfo(cards[c]).key);
        var L = cards[0].layer;

        // ① 띠지 '현수막' → '켈지' : 레이어 직속 글자 중 정확히 '현수막' 인 것 (날개 제목의 '현수막 / 둥글게 양면' 은 묶음 안이라 안 걸림)
        var mat = [];
        for (i = 0; i < L.textFrames.length; i++) { var t = L.textFrames[i]; if (t.parent === L && t.contents == "현수막") mat.push(t); }
        if (mat.length != 1) throw new Error("띠지 '현수막' 글자 " + mat.length + "개");
        var mb = mat[0].visibleBounds; mat[0].contents = "켈지";
        var nb = mat[0].visibleBounds; mat[0].translate(mb[0] - nb[0], mb[1] - nb[1]);
        out.push("띠지 재질 → 켈지");

        // ② 체험부스 간판: 옆간판 줄 아래에 제목 + 2장
        var X0 = 1e9, bottom = 1e9, font = null;
        for (c = 0; c < cards.length; c++) { var b = bounds(cards[c]); X0 = Math.min(X0, b[0]); bottom = Math.min(bottom, b[3]); }
        stWalk(cards[0], function (it) { if (!font && it.typename == "TextFrame" && /^\d+$/.test(it.contents)) font = it.textRange.characterAttributes.textFont; });
        var title = stTitle(L, "체험부스 간판", ["2930x750mm / 현수막 / 상하단 바미싱", "2EA (부산광역시 · 부산정보산업진흥원 AI·디지털체험)"], X0, bottom - 70 * MM, font);
        var tb = title.visibleBounds, x = X0;
        for (i = 0; i < faces.length; i++) {
            var nw = faces[i].duplicate(L, ElementPlacement.PLACEATEND);
            nw.name = "체험부스간판_" + (i + 1);
            var wb = stClipPathOf(nw).geometricBounds;
            nw.translate(x - wb[0], tb[3] - 12 * MM - wb[1]);
            x += wb[2] - wb[0];
        }

        // 검사
        var f2 = stFindSigns(doc), changed = 0, exp = 0;
        for (c = 0; c < f2.signs.length; c++) if (stInfo(f2.signs[c]).key != before[c]) changed++;
        for (c = 0; c < f2.others.length; c++) if (/^체험부스간판_/.test(f2.others[c].name)) exp++;
        out.push("간판 " + f2.signs.length + "장 / 바뀐 간판 " + changed + " / 체험부스 " + exp + " / 다른 출력물 전체 " + f2.others.length);
        if (f2.signs.length == 32 && changed == 0 && exp == 2) {
            var u = null, all = kids(L);                          // 대지를 새 줄까지 늘린다 (마스크 크기로 잰다)
            for (c = 0; c < all.length; c++) { var q = (all[c].typename == "GroupItem") ? bounds(all[c]) : all[c].visibleBounds; u = u ? [Math.min(u[0], q[0]), Math.max(u[1], q[1]), Math.max(u[2], q[2]), Math.min(u[3], q[3])] : q; }
            var m = 30 * MM; doc.artboards[0].artboardRect = [u[0] - m, u[1] + m, u[2] + m, u[3] - m];
            doc.save(); out.push("saved");
        } else out.push("검사 불통과 — 저장 안 함");
    } catch (e) { out.push("ERROR " + e.message + " line " + e.line); }
    if (doc) doc.close(SaveOptions.DONOTSAVECHANGES);
    bdoc.close(SaveOptions.DONOTSAVECHANGES);
}
var gf = File(Folder.temp.fsName + "/bsg_exp.txt"); gf.encoding = "UTF-8"; gf.open("w"); gf.write(out.join("\n")); gf.close();

// 옆간판 틀 만들기 (2026-10-21). 정면 2930x750 → 옆 2435x750 (1/10 문서: 293 → 243.5mm). ASURA님 최신 옥타 메모 "옆간판 2435mm x 750mm".
// 늘이거나 줄이지(scale) 않고 '잘라 당기기': 92mm·238mm 두 곳을 기준으로 가운데 구간은 24.75, 오른쪽 구간은 49.5 왼쪽으로.
//   - 제목 아래 홈(115~185)은 가운데 구간에 통째로 있어 모양 그대로, 새 폭의 가운데로 온다. 'AI시대' 글자(24~74)·왼쪽 장식은 그대로.
//   - 테두리처럼 구간을 가로지르는 선은 꼭짓점만 옮겨 폭만 줄어든다(모서리 모양 유지). 배경 그림은 클리핑으로 잘린다.
//   - 로고·글자 칸은 비율대로 다시 잡는다: 로고 39.5~112.5, 글자 126.7~203.5 (정면 39.5~134.5 / 153~253).
// '틀' → '틀_옆', '틀_연두' → '틀_옆_연두'. 다시 돌리면 이전 옆 틀을 지우고 새로 만든다. 끝에 견본 2장을 그림으로 뽑고 견본은 저장하지 않는다.
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, out = [];
var WORK = "G:/내 드라이브/AI-작업기록/claude/2026-10-15_부산사이버보안_부스간판/";
var CUT1 = 92, CUT2 = 238, D = (293 - 243.5) / 2;            // mm (간판 왼쪽 끝 기준)
var LOGO = [39.5, 112.5], AREA = [126.7, 203.5];
$.global.FT_NO_MAIN = true;
$.evalFile(File("C:/Users/PSH/.agents/skills/illustrator-data-merge/scripts/fill_template.jsx"));   // setText·placeImage·collect·kids·center·bounds

function clipOf(g) { var k = kids(g); for (var i = 0; i < k.length; i++) if (k[i].typename == "GroupItem" && k[i].clipped) for (var j = 0; j < k[i].pathItems.length; j++) if (k[i].pathItems[j].clipping) return k[i].pathItems[j]; }
// ExtendScript 안쪽 함수가 바깥 지역변수(x0)를 제대로 못 읽었다(실측: -38mm 를 오른쪽 구간으로 판정) → 도우미는 전부 바깥에 두고 값을 넘긴다.
function zoneOf(x, x0) {                       // 겹친 ?: 식이 -37.5 를 2 로 판정했다(ExtendScript 실측) → if 로
    var m = (x - x0) / MM;
    if (m <= CUT1) return 0;
    if (m <= CUT2) return 1;
    return 2;
}
function shiftOf(x, x0) { return -zoneOf(x, x0) * D * MM; }
function movePts(p, x0) {
    var n = 0;
    for (var i = 0; i < p.pathPoints.length; i++) {
        var q = p.pathPoints[i], s = shiftOf(q.anchor[0], x0);
        if (!s) continue;
        q.anchor = [q.anchor[0] + s, q.anchor[1]];
        q.leftDirection = [q.leftDirection[0] + s, q.leftDirection[1]];
        q.rightDirection = [q.rightDirection[0] + s, q.rightDirection[1]];
        n++;
    }
    return n;
}
function sq(it, x0, holder) {
    if (it.name == "__holder__") return 0;
    var b = it.geometricBounds, n = 0;
    if (zoneOf(b[0], x0) == zoneOf(b[2], x0)) { var s = shiftOf(b[0], x0); if (s) it.translate(s, 0); return 0; }
    if (it.typename == "GroupItem") { var k = kids(it); for (var i = 0; i < k.length; i++) n += sq(k[i], x0); }
    else if (it.typename == "PathItem") n += movePts(it, x0);
    else if (it.typename == "CompoundPathItem") for (var j = 0; j < it.pathItems.length; j++) n += movePts(it.pathItems[j], x0);
    else if (it.typename == "RasterItem") {}                    // 배경 그림: 클리핑이 잘라 준다
    else it.translate(shiftOf((b[0] + b[2]) / 2, x0), 0);
    return n;
}
function squeezeTpl(w) {
    var x0 = clipOf(w).geometricBounds[0], moved = 0;
    var all = collect(w, []), area = null, logo = null;          // 이름 붙은 칸은 그룹 깊이 들어 있어 getByName 이 안 된다
    for (var i = 0; i < all.length; i++) { if (all[i].name == "영역") area = all[i]; if (all[i].name == "로고") logo = all[i]; }
    var holder = area.parent; holder.name = "__holder__";        // 로고·글자 칸 묶음은 따로 다시 잡는다 (=== 비교가 안 돼서 이름표로 건너뜀)
    var k = kids(w);
    for (i = 0; i < k.length; i++) moved += sq(k[i], x0);
    holder.name = "";
    // 제목이 24.75 왼쪽으로 오면서 'AI시대…' 문구 끝(74mm)에 붙는다 → 문구만 왼쪽 끝 기준 75% (제목 크기는 그대로)
    for (i = 0; i < all.length; i++) if (all[i].typename == "TextFrame" && /^AI시대/.test(all[i].contents))
        all[i].resize(75, 75, true, true, true, true, 75, Transformation.LEFT);
    var tg = null, hk = kids(holder);
    for (i = 0; i < hk.length; i++) if (hk[i].typename == "GroupItem") tg = hk[i];
    logo.width = (LOGO[1] - LOGO[0]) * MM; logo.left = x0 + LOGO[0] * MM;
    area.width = (AREA[1] - AREA[0]) * MM; area.left = x0 + AREA[0] * MM;
    var tb = tg.visibleBounds; tg.translate(x0 + (AREA[0] + AREA[1]) / 2 * MM - (tb[0] + tb[2]) / 2, 0);
    return moved;
}
function rel(b, x0, y0) { return [Math.round((b[0] - x0) / MM * 10) / 10, Math.round((b[2] - x0) / MM * 10) / 10]; }

var busy = false;
for (var d = 0; d < app.documents.length; d++) if (/부스간판_(자동생성|틀)\.ai$/.test(app.documents[d].name)) busy = true;
if (busy) out.push("열려 있음 — 중단");
else {
    var doc = app.open(File(WORK + "부스간판_틀.ai"));
    try {
        var L = doc.layers.getByName("Layer 1"), PAIRS = [["틀", "틀_옆", -800], ["틀_연두", "틀_옆_연두", -950]];
        for (var p = 0; p < PAIRS.length; p++) {
            try { doc.groupItems.getByName(PAIRS[p][1]).remove(); } catch (e) {}
            var src = doc.groupItems.getByName(PAIRS[p][0]), w = src.duplicate(L, ElementPlacement.PLACEATBEGINNING);
            w.name = PAIRS[p][1]; w.hidden = false;
            var sb = bounds(src); w.translate(0, PAIRS[p][2] * MM - (bounds(w)[1] - sb[1]) + (sb[1] - bounds(w)[1]) * 0);
            var n = squeezeTpl(w), cb = clipOf(w).geometricBounds;
            out.push(PAIRS[p][1] + ": 꼭짓점 " + n + "개 이동, 간판 폭 " + Math.round((cb[2] - cb[0]) / MM * 10) / 10 + "mm, 묶음 " + rel(bounds(w), cb[0]).join("~"));
        }
        var okW = true; for (p = 0; p < PAIRS.length; p++) { var c2 = clipOf(doc.groupItems.getByName(PAIRS[p][1])).geometricBounds; if (Math.abs((c2[2] - c2[0]) / MM - 243.5) > 0.2) okW = false; }
        if (!okW) throw new Error("옆 틀 폭이 243.5mm 가 아님 — 저장 안 함");
        doc.save(); out.push("틀 저장");

        // 견본 2장 (저장 안 함)
        var SAMPLE = [["틀_옆", { "부스번호": "03", "국문": "스패로우", "영문": "SPARROW" }, "18_1_ai_cmyk.tif"],
                      ["틀_옆_연두", { "부스번호": "04", "국문": "국제식물검역인증원", "영문": "IPAB" }, "add1_1_cmyk.tif"]];
        for (var s = 0; s < SAMPLE.length; s++) {
            var t = doc.groupItems.getByName(SAMPLE[s][0]), sm = t.duplicate(L, ElementPlacement.PLACEATBEGINNING);
            sm.translate(0, -400 * MM);
            var ci = collect(sm, []), areas = [];
            for (var i = 0; i < ci.length; i++) if (ci[i].name == "영역") areas.push(ci[i].visibleBounds);
            for (i = 0; i < ci.length; i++) {
                var it = ci[i];
                if (it.typename == "TextFrame" && it.name in SAMPLE[s][1]) {
                    var cc = center(it.visibleBounds), area = null;
                    for (var a = 0; a < areas.length && !area; a++) if (cc[0] > areas[a][0] && cc[0] < areas[a][2] && cc[1] < areas[a][1] && cc[1] > areas[a][3]) area = areas[a];
                    setText(it, SAMPLE[s][1][it.name], area);
                } else if (it.typename == "PathItem" && it.name == "로고") placeImage(it, File(WORK + "로고/" + SAMPLE[s][2]));
            }
            var bb = bounds(sm), m = 5 * MM;
            var ab = doc.artboards.add([bb[0] - m, bb[1] + m, bb[2] + m, bb[3] - m]);
            doc.artboards.setActiveArtboardIndex(doc.artboards.length - 1);
            var o = new ExportOptionsPNG24(); o.horizontalScale = o.verticalScale = 400; o.artBoardClipping = true;
            doc.exportFile(File(Folder.temp.fsName + "/bsg/side_sample" + (s + 1) + ".png"), ExportType.PNG24, o);
            out.push("견본 " + (s + 1) + " " + SAMPLE[s][1]["국문"]);
        }
        // 비교용 정면 틀 견본도 같은 배율로
    } catch (e) { out.push("ERROR " + e.message + " line " + e.line); }
    doc.close(SaveOptions.DONOTSAVECHANGES);
}
var g = File(Folder.temp.fsName + "/bsg_side.txt"); g.encoding = "UTF-8"; g.open("w"); g.write(out.join("\n")); g.close();

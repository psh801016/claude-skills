// 2026-10-21 부스간판 32장: 정면 24 (08 안랩 통합부스 2장) + 옆간판 8 (2435x750, 파란 배치도 빨간 선 = 오픈된 쪽).
// 기존 23장은 손대지 않고(손 수정 보존) 08 만 복제해 옆에 붙이고 뒤 간판을 한 칸씩 민다 → 10·10·4 줄.
// 옆간판은 틀 파일 '틀_옆'/'틀_옆_연두' 를 복제해, 같은 번호 정면 간판의 국문·영문 글자와 로고 그림을 그대로 가져와 채운다. 맨 아래 한 줄.
// 전후 덤프: 기존 23장 내용(글자·번호·로고 크기) 그대로, 정면 24·옆 8, 로고 전부 CMYK 일 때만 저장.
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, out = [];
var RESULT = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/원본/부스간판.ai";
var WORK = "G:/내 드라이브/AI-작업기록/claude/2026-10-15_부산사이버보안_부스간판/";
var SIDE = [["01", "(주)이글루코퍼레이션", "틀_옆"], ["03", "스패로우", "틀_옆"], ["04", "(주)소만사", "틀_옆"], ["04", "국제식물검역인증원", "틀_옆_연두"],
            ["15", "워터월시스템즈(주)", "틀_옆"], ["18", "넥스원소프트(주)", "틀_옆"], ["19", "(주)앤앤에스피", "틀_옆"], ["22", "굿모닝아이텍(주)", "틀_옆"]];
$.global.FT_NO_MAIN = true;
$.evalFile(File("C:/Users/PSH/.agents/skills/illustrator-data-merge/scripts/fill_template.jsx"));   // setText·collect·kids·center·bounds

function walk(g, fn) { var k = kids(g); for (var i = 0; i < k.length; i++) { fn(k[i]); if (k[i].typename == "GroupItem") walk(k[i], fn); } }
function mm(b) { return [Math.round(b[0] / MM * 10) / 10, Math.round(b[1] / MM * 10) / 10, Math.round((b[2] - b[0]) / MM * 10) / 10, Math.round((b[1] - b[3]) / MM * 10) / 10]; }
function info(card) {
    var r = { card: card, name: "", nums: [], txt: [], logos: [], big: null, small: null };
    walk(card, function (it) {
        if (it.typename == "TextFrame" && !/AI시대|콘퍼런스/.test(it.contents)) {
            if (/^\d+$/.test(it.contents)) r.nums.push(it.contents);
            else {
                r.txt.push(it.contents.replace(/\r/g, "/"));
                if (/[가-힣]/.test(it.contents) && !r.name) r.name = it.contents.replace(/\r/g, " ");
                var sz = it.textRange.characterAttributes.size;
                if (!r.big || sz > r.big.textRange.characterAttributes.size) { r.small = r.big; r.big = it; }
                else if (!r.small || sz > r.small.textRange.characterAttributes.size) r.small = it;
            }
        }
        if (it.typename == "RasterItem" && it.geometricBounds[2] - it.geometricBounds[0] < 200 * MM) r.logos.push(it);
    });
    var lb = [], cs = 0;
    for (var i = 0; i < r.logos.length; i++) {
        var b = r.logos[i].geometricBounds;
        lb.push(Math.round((b[2] - b[0]) / MM * 10) / 10 + "x" + Math.round((b[1] - b[3]) / MM * 10) / 10);
        if (r.logos[i].imageColorSpace != ImageColorSpace.CMYK) cs++;
    }
    r.nv = r.nums.join("/"); r.rgb = cs; r.b = bounds(card);
    r.key = r.nv + " | " + r.txt.join(" ; ") + " | " + lb.join(" ; ");
    r.w = Math.round((r.b[2] - r.b[0]) / MM * 10) / 10;
    return r;
}
function snap(doc) { var c = kids(doc.pageItems.getByName("자동생성")), s = []; for (var i = 0; i < c.length; i++) s.push(info(c[i])); return s; }

var busy = false;
for (var d = 0; d < app.documents.length; d++) if (/^부스간판(_틀)?\.ai$/.test(app.documents[d].name)) busy = true;
if (busy) out.push("결과/틀 파일이 열려 있음 — 중단");
else {
    var tdoc = app.open(File(WORK + "부스간판_틀.ai"));
    var doc = app.open(File(RESULT));
    try {
        var before = snap(doc), res = doc.pageItems.getByName("자동생성");
        if (before.length != 23) throw new Error("간판 " + before.length + "장 (예상 23)");
        for (var c = 0; c < before.length; c++) out.push("전 " + (c + 1) + " " + before[c].key);
        var X0 = before[0].b[0], PITCH = before[1].b[0] - before[0].b[0];
        var Y = [before[0].b[1], before[10].b[1], before[20].b[1]], ROWH = Y[0] - Y[1];
        Y.push(Y[2] - ROWH);

        // 1) 08 안랩 한 장 더 (바로 뒤)
        var i8 = -1;
        for (c = 0; c < before.length; c++) if (before[c].name == "(주)안랩") i8 = c;
        if (i8 < 0) throw new Error("안랩 못 찾음");
        before[i8].card.duplicate(before[i8].card, ElementPlacement.PLACEAFTER);
        var fronts = kids(res);
        if (fronts.length != 24) throw new Error("08 복제 뒤 " + fronts.length + "장");
        for (c = 0; c < fronts.length; c++) {                        // 10장씩 3줄로 다시 놓기 (순서 그대로)
            var fb = bounds(fronts[c]);
            fronts[c].translate(X0 + (c % 10) * PITCH - fb[0], Y[Math.floor(c / 10)] - fb[1]);
        }

        // 2) 옆간판 8장
        var fs = snap(doc), x = X0;
        for (var s = 0; s < SIDE.length; s++) {
            var src = null;
            for (c = 0; c < fs.length; c++) if (fs[c].name == SIDE[s][1] && fs[c].nv == SIDE[s][0] + "/" + SIDE[s][0]) src = fs[c];
            if (!src) throw new Error("정면 간판 못 찾음: " + SIDE[s].join(" "));
            if (src.logos.length != 1) throw new Error(SIDE[s][1] + " 로고 " + src.logos.length + "개");
            var w = tdoc.groupItems.getByName(SIDE[s][2]).duplicate(res.layer, ElementPlacement.PLACEATEND);   // 다른 문서 → 레이어로 복제 후 이동 (PARM 함정)
            w.move(res, ElementPlacement.PLACEATEND); w.name = ""; w.hidden = false;
            var ci = collect(w, []), area = null, box = null;
            for (var i = 0; i < ci.length; i++) { if (ci[i].name == "영역") area = ci[i].visibleBounds; if (ci[i].name == "로고") box = ci[i]; }
            var val = { "국문": src.big.contents, "영문": src.small.contents, "부스번호": SIDE[s][0] };
            for (i = 0; i < ci.length; i++) {
                var it = ci[i];
                if (it.typename == "TextFrame" && it.name in val) {
                    var cc = center(it.visibleBounds);
                    var inA = cc[0] > area[0] && cc[0] < area[2] && cc[1] < area[1] && cc[1] > area[3];
                    setText(it, val[it.name], inA ? area : null);
                }
            }
            var lg = src.logos[0].duplicate(box, ElementPlacement.PLACEBEFORE);   // 정면 간판에 들어간 로고 그림 그대로
            var bb = box.geometricBounds, lb = lg.geometricBounds;
            var k = Math.min((bb[2] - bb[0]) / (lb[2] - lb[0]), (bb[1] - bb[3]) / (lb[1] - lb[3])) * 100;
            lg.resize(k, k, true, true, true, true, k, Transformation.CENTER);
            lb = lg.geometricBounds;
            lg.translate((bb[0] + bb[2]) / 2 - (lb[0] + lb[2]) / 2, (bb[1] + bb[3]) / 2 - (lb[1] + lb[3]) / 2);
            for (i = 0; i < ci.length; i++) if (ci[i].name) ci[i].name = "";
            var wb = bounds(w);
            w.translate(x - wb[0], Y[3] - wb[1]);
            x += wb[2] - wb[0];
        }

        // 3) 검사
        var after = snap(doc), fronts2 = 0, sides = 0, rgb = 0, n08 = 0, errs = [], used = {};
        for (c = 0; c < after.length; c++) {
            var a = after[c]; rgb += a.rgb;
            out.push("후 " + (c + 1) + " [" + a.w + "] " + mm(a.b).slice(0, 2).join(",") + " " + a.key);
            if (Math.abs(a.w - 293) < 1) fronts2++; else if (Math.abs(a.w - 243.5) < 1) sides++; else errs.push((c + 1) + "번째 폭 " + a.w);
            if (a.name == "(주)안랩" && Math.abs(a.w - 293) < 1) n08++;
        }
        for (c = 0; c < before.length; c++) {                         // 기존 23장 내용 그대로인지 (자리만 바뀜)
            var hit = false;
            for (var j = 0; j < after.length && !hit; j++)
                if (!used[j] && after[j].key == before[c].key && Math.abs(after[j].w - 293) < 1) { used[j] = 1; hit = true; }
            if (!hit) errs.push("기존 " + (c + 1) + " " + before[c].name + " 내용이 달라짐");
        }
        for (s = 0; s < SIDE.length; s++) {
            var sc = after[24 + s];
            if (!sc || sc.nv != SIDE[s][0] + "/" + SIDE[s][0] || sc.name != SIDE[s][1] || sc.logos.length != 1)
                errs.push("옆 " + (s + 1) + " " + SIDE[s][1] + " 확인 실패 (" + (sc ? sc.name + " [" + sc.nv + "]" : "없음") + ")");
        }
        if (fronts2 != 24 || sides != 8 || n08 != 2 || rgb) errs.push("정면 " + fronts2 + " / 옆 " + sides + " / 08 " + n08 + " / RGB " + rgb);
        out.push("정면 " + fronts2 + " / 옆 " + sides + " / 08 안랩 " + n08 + " / RGB 로고 " + rgb + " / 문제 " + errs.length);
        for (c = 0; c < errs.length; c++) out.push("  ! " + errs[c]);

        // 대지: 전체 간판 + 여백 20
        var u = null;
        for (c = 0; c < after.length; c++) { var q = after[c].b; u = u ? [Math.min(u[0], q[0]), Math.max(u[1], q[1]), Math.max(u[2], q[2]), Math.min(u[3], q[3])] : q; }
        var m = 20 * MM; doc.artboards[0].artboardRect = [u[0] - m, u[1] + m, u[2] + m, u[3] - m];
        var o = new ExportOptionsPNG24(); o.horizontalScale = o.verticalScale = 150; o.artBoardClipping = true;
        doc.exportFile(File(Folder.temp.fsName + "/bsg/full.png"), ExportType.PNG24, o);
        if (!errs.length) {
            o.horizontalScale = o.verticalScale = 60;
            doc.exportFile(File(WORK + "부스간판_자동생성_미리보기.png"), ExportType.PNG24, o);
            doc.save(); out.push("saved");
        } else out.push("검사 불통과 — 저장 안 함");
    } catch (e) { out.push("ERROR " + e.message + " line " + e.line); }
    doc.close(SaveOptions.DONOTSAVECHANGES);
    tdoc.close(SaveOptions.DONOTSAVECHANGES);
}
var g = File(Folder.temp.fsName + "/bsg_32.txt"); g.encoding = "UTF-8"; g.open("w"); g.write(out.join("\n")); g.close();

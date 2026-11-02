// 2026-10-19 김태영님 요청: 화질 깨지던 2개 기업 .ai 로고 반영.
//  - 10번 우리아이티: 2025 처럼 두 회사형(좌 시스코 Cisco | 우 (주)우리아이티 WOORIIT). 틀 파일의 '틀_2사' 를 복제해 그 자리에 바꿔 끼운다.
//  - 9번 앤앤에스피: 로고 그림만 .ai 원본 TIFF 로 교체(swap_logos 와 같은 방식).
// 나머지 21장(ASURA님 손 수정 포함)은 건드리지 않는다. 전후 덤프로 바뀐 간판이 9·10 두 장뿐일 때만 저장.
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, out = [];
var RESULT = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/원본/부스간판.ai";
var WORK = "G:/내 드라이브/AI-작업기록/claude/2026-10-15_부산사이버보안_부스간판/";
var LOGO = WORK + "로고/";
var TEXT = { "국문": "시스코", "영문": "Cisco", "국문2": "(주)우리아이티", "영문2": "WOORIIT", "부스번호": "10" };
var IMG = { "로고": "10_1_ai_cmyk.tif", "로고2": "10_2_ai_cmyk.tif" };
var LOGO_H = 30;   // 틀 로고 상자 22mm 는 세로형 WIT 가 작게 들어간다(드림 때와 같은 문제) → 가운데 기준 30mm 로 키워서 넣는다
$.global.FT_NO_MAIN = true;
$.evalFile(File("C:/Users/PSH/.agents/skills/illustrator-data-merge/scripts/fill_template.jsx"));   // setText·placeImage·collect·bounds·kids

function walk(g, fn) { var k = kids(g); for (var i = 0; i < k.length; i++) { fn(k[i]); if (k[i].typename == "GroupItem") walk(k[i], fn); } }
function mm(b) { return [Math.round(b[0] / MM * 10) / 10, Math.round(b[1] / MM * 10) / 10, Math.round((b[2] - b[0]) / MM * 10) / 10, Math.round((b[1] - b[3]) / MM * 10) / 10]; }
function info(card) {
    var name = "", texts = [], logos = [];
    walk(card, function (it) {
        if (it.typename == "TextFrame" && !/AI시대|콘퍼런스/.test(it.contents)) {
            texts.push(it.contents.replace(/\r/g, "/"));
            if (/[가-힣]/.test(it.contents) && !name) name = it.contents;
        }
        if (it.typename == "RasterItem" && it.geometricBounds[2] - it.geometricBounds[0] < 200 * MM) logos.push(it);
    });
    var lb = []; for (var i = 0; i < logos.length; i++) lb.push(mm(logos[i].geometricBounds).join(",") + " " + String(logos[i].imageColorSpace).replace("ImageColorSpace.", ""));
    return { card: card, name: name, logos: logos, key: mm(bounds(card)).join(",") + " | " + texts.join(" ; ") + " | " + lb.join(" ; ") };
}
function snap(doc) { var c = kids(doc.pageItems.getByName("자동생성")), s = []; for (var i = 0; i < c.length; i++) s.push(info(c[i])); return s; }
function find(s, name) { for (var i = 0; i < s.length; i++) if (s[i].name == name) return i; return -1; }

var busy = false;
for (var d = 0; d < app.documents.length; d++) if (/^부스간판(_틀)?\.ai$/.test(app.documents[d].name)) busy = true;
if (busy) out.push("결과/틀 파일이 열려 있음 — 중단");
else {
    var tdoc = app.open(File(WORK + "부스간판_틀.ai"));
    var tpl = tdoc.groupItems.getByName("틀_2사");
    var doc = app.open(File(RESULT));
    try {
        var before = snap(doc), i10 = find(before, "(주)우리아이티"), i9 = find(before, "(주)앤앤에스피");
        if (i10 < 0 || i9 < 0) throw new Error("간판 못 찾음 10=" + i10 + " 9=" + i9);
        for (var c = 0; c < before.length; c++) out.push("전 " + (c + 1) + " " + before[c].key);

        // 10번: 두 회사형으로 바꿔 끼우기
        var old = before[i10].card, nu = tpl.duplicate(old.layer, ElementPlacement.PLACEATEND);   // 다른 문서의 간판 바로 앞으로는 복제가 안 된다(PARM) → 레이어로 복제 후 이동
        nu.move(old, ElementPlacement.PLACEBEFORE);
        nu.name = ""; nu.hidden = false;
        var ci = collect(nu, []), areas = [];
        for (var i = 0; i < ci.length; i++) if (ci[i].name == "영역") areas.push(ci[i].visibleBounds);
        for (i = 0; i < ci.length; i++) {
            var it = ci[i];
            if (it.typename == "TextFrame" && it.name in TEXT) {
                var cc = center(it.visibleBounds), area = null;
                for (var a = 0; a < areas.length && !area; a++)
                    if (cc[0] > areas[a][0] && cc[0] < areas[a][2] && cc[1] < areas[a][1] && cc[1] > areas[a][3]) area = areas[a];
                setText(it, TEXT[it.name], area); it.name = "";
            } else if (it.typename == "PathItem" && it.name in IMG) {
                var b0 = center(it.geometricBounds);
                it.height = LOGO_H * MM;
                var b1 = center(it.geometricBounds); it.translate(b0[0] - b1[0], b0[1] - b1[1]);
                placeImage(it, File(LOGO + IMG[it.name])); it.name = "";
            } else if (it.name == "영역") it.name = "";
        }
        var ob = bounds(old), nb = bounds(nu);
        nu.translate(ob[0] - nb[0], ob[1] - nb[1]);
        old.remove();
        out.push("10번 두 회사형 → " + mm(bounds(nu)).join(","));

        // 9번: 로고만 교체
        var s9 = snap(doc)[i9];
        if (s9.logos.length != 1) throw new Error("9번 로고 " + s9.logos.length + "개");
        var ol = s9.logos[0], ol0 = ol.name, ob9 = ol.geometricBounds, par = ol.parent, pre = kids(par);
        var p = par.placedItems.add(); p.file = File(LOGO + "09_1_ai_cmyk.tif");
        p.move(ol, ElementPlacement.PLACEBEFORE); p.embed();
        var post = kids(par), nl = null;
        for (i = 0; i < post.length && !nl; i++) { var isNew = true; for (var j = 0; j < pre.length; j++) if (post[i] === pre[j]) isNew = false; if (isNew) nl = post[i]; }
        var lb = nl.geometricBounds, k = Math.min((ob9[2] - ob9[0]) / (lb[2] - lb[0]), (ob9[1] - ob9[3]) / (lb[1] - lb[3])) * 100;
        nl.resize(k, k, true, true, true, true, k, Transformation.CENTER);
        lb = nl.geometricBounds;
        nl.translate((ob9[0] + ob9[2]) / 2 - (lb[0] + lb[2]) / 2, (ob9[1] + ob9[3]) / 2 - (lb[1] + lb[3]) / 2);
        ol.remove();
        // embed 결과가 그룹으로 감싸여 nl 은 GroupItem 일 수 있다(실측). 남은 로고 그림 이름이 새 파일명인지로 확인한다.
        var a9 = snap(doc)[i9].logos, swapped9 = a9.length == 1 && a9[0].name.indexOf("09_1_ai_cmyk") == 0 && ol0 != a9[0].name;   // 같은 상자에 맞추므로 위치·크기는 그대로다 → 그림이 새것인지로 확인

        // 검사: 장수 같고, 바뀐 간판은 9·10 뿐, 10번 로고 2개, 모든 로고 CMYK
        var after = snap(doc), changed = [], rgb = 0;
        for (c = 0; c < after.length; c++) {
            out.push("후 " + (c + 1) + " " + after[c].key);
            if (c < before.length && after[c].key != before[c].key) changed.push(c + 1);
            for (i = 0; i < after[c].logos.length; i++) if (after[c].logos[i].imageColorSpace != ImageColorSpace.CMYK) rgb++;
        }
        var ok = after.length == before.length && changed.join(",") == String(i10 + 1) && swapped9 && after[i10].logos.length == 2 && rgb == 0;
        out.push("장수 " + before.length + "→" + after.length + " / 바뀐 간판 " + changed.join(",") + " / 9번 교체 " + swapped9 + " / 10번 로고 " + after[i10].logos.length + " / RGB 로고 " + rgb);
        var o = new ExportOptionsPNG24(); o.horizontalScale = o.verticalScale = 150; o.artBoardClipping = true;
        doc.exportFile(File(Folder.temp.fsName + "/bsg/full.png"), ExportType.PNG24, o);
        if (ok) {
            o.horizontalScale = o.verticalScale = 60;
            doc.exportFile(File(WORK + "부스간판_자동생성_미리보기.png"), ExportType.PNG24, o);
            doc.save(); out.push("saved");
        } else out.push("검사 불통과 — 저장 안 함");
    } catch (e) { out.push("ERROR " + e.message + " line " + e.line); }
    doc.close(SaveOptions.DONOTSAVECHANGES);
    tdoc.close(SaveOptions.DONOTSAVECHANGES);
}
var g = File(Folder.temp.fsName + "/bsg_fix.txt"); g.encoding = "UTF-8"; g.open("w"); g.write(out.join("\n")); g.close();

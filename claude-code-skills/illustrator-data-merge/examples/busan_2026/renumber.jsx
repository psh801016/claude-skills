// 2026-10-21 배치도(밝은 판) 기준으로 부스번호 맞추기. ASURA님 "밝은 배치도 기준으로 맞춰".
// 간판 순서는 그대로, 번호(배지 + 위 검정 라벨)만 바꾼다. 밝은 배치도엔 08(안랩)이 비어 있다 → DROP_AHNLAB 이면 안랩 간판을 빼고 뒤 간판을 한 칸씩 당긴다.
// 순서·이름·현재 번호를 전부 확인한 뒤에만 바꾸고, 전후 덤프로 번호 외에는 바뀐 게 없을 때만 저장.
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var DROP_AHNLAB = $.global.DROP_AHNLAB === true;
var MM = 72 / 25.4, out = [];
var RESULT = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/원본/부스간판.ai";
var WORK = "G:/내 드라이브/AI-작업기록/claude/2026-10-15_부산사이버보안_부스간판/";
$.global.FT_NO_MAIN = true;
$.evalFile(File("C:/Users/PSH/.agents/skills/illustrator-data-merge/scripts/fill_template.jsx"));   // bounds·kids·center
// [현재 순서의 첫 한글 글자(없으면 ""), 지금 번호, 배치도 번호]
var MAP = [
    ["(주)78리서치랩", "01", "06"], ["(주)넷코아테크", "02", "11"], ["(주)드림시큐리티", "03", "14"], ["(주)비테크놀로지", "04", "05"],
    ["(주)소만사", "05", "04"], ["", "06", "20"], ["(주)아이시큐", "07", "02"], ["(주)안랩", "08", "08"],
    ["(주)앤앤에스피", "09", "19"], ["시스코", "10", "12"], ["(주)위드네트웍스", "11", "09"], ["(주)윈스테크넷", "12", "21"],
    ["(주)이글루코퍼레이션", "13", "01"], ["(주)제이콥시스템", "14", "07"], ["(주)퓨쳐시스템", "15", "10"], ["굿모닝아이텍(주)", "16", "22"],
    ["넥스원소프트(주)", "17", "18"], ["스패로우", "18", "03"], ["시큐어레터(주)", "19", "13"], ["워터월시스템즈(주)", "20", "15"],
    ["팔로알토 네트웍스", "21", "16"], ["프라이빗에이아이(주)", "22", "17"], ["국제식물검역인증원", "04", "04"]
];
function walk(g, fn) { var k = kids(g); for (var i = 0; i < k.length; i++) { fn(k[i]); if (k[i].typename == "GroupItem") walk(k[i], fn); } }
function mm(b) { return [Math.round(b[0] / MM * 10) / 10, Math.round(b[1] / MM * 10) / 10, Math.round((b[2] - b[0]) / MM * 10) / 10, Math.round((b[1] - b[3]) / MM * 10) / 10]; }
function info(card) {
    var name = "", nums = [], other = [], logos = [];
    walk(card, function (it) {
        if (it.typename == "TextFrame" && !/AI시대|콘퍼런스/.test(it.contents)) {
            if (/^\d+$/.test(it.contents)) nums.push(it);
            else { other.push(it.contents.replace(/\r/g, "/")); if (/[가-힣]/.test(it.contents) && !name) name = it.contents.replace(/\r/g, " "); }
        }
        if (it.typename == "RasterItem" && it.geometricBounds[2] - it.geometricBounds[0] < 200 * MM) logos.push(mm(it.geometricBounds).join(","));
    });
    var nv = []; for (var i = 0; i < nums.length; i++) nv.push(nums[i].contents);
    return { card: card, name: name, nums: nums, nv: nv.join("/"), key: other.join(" ; ") + " | " + logos.join(" ; "), b: bounds(card) };
}
function snap(doc) { var c = kids(doc.pageItems.getByName("자동생성")), s = []; for (var i = 0; i < c.length; i++) s.push(info(c[i])); return s; }

var busy = false;
for (var d = 0; d < app.documents.length; d++) if (/^부스간판\.ai$/.test(app.documents[d].name)) busy = true;
if (busy) out.push("결과 파일이 열려 있음 — 중단");
else {
    var doc = app.open(File(RESULT));
    try {
        var s = snap(doc), errs = [];
        if (s.length != MAP.length) errs.push("간판 " + s.length + "장 (예상 " + MAP.length + ")");
        for (var i = 0; i < s.length && i < MAP.length; i++) {
            out.push("전 " + (i + 1) + " " + s[i].name + " [" + s[i].nv + "] " + mm(s[i].b).join(","));
            if (s[i].name != MAP[i][0]) errs.push((i + 1) + "번째 이름 '" + s[i].name + "' ≠ '" + MAP[i][0] + "'");
            if (s[i].nv != MAP[i][1] + "/" + MAP[i][1]) errs.push((i + 1) + "번째 번호 [" + s[i].nv + "] ≠ " + MAP[i][1] + " 2개");
        }
        if (errs.length) throw new Error(errs.join(" / "));

        var pos = []; for (i = 0; i < s.length; i++) pos.push(s[i].b);
        var expect = [];
        for (i = 0; i < s.length; i++) {
            if (DROP_AHNLAB && MAP[i][0] == "(주)안랩") { s[i].card.remove(); continue; }
            for (var k = 0; k < s[i].nums.length; k++) {           // 배지 숫자는 가운데, 위 라벨은 오른쪽 맞춤이라 내용만 바꾸고 중심/오른쪽 끝을 되돌린다
                var tf = s[i].nums[k], b0 = tf.visibleBounds, c0 = center(b0);
                tf.contents = MAP[i][2];
                var b1 = tf.visibleBounds, c1 = center(b1);
                if (tf.textRange.paragraphAttributes.justification == Justification.RIGHT) tf.translate(b0[2] - b1[2], c0[1] - c1[1]);
                else tf.translate(c0[0] - c1[0], c0[1] - c1[1]);
            }
            expect.push([MAP[i][0], MAP[i][2], s[i].key]);
        }
        if (DROP_AHNLAB) {                                         // 빈 칸 메우기: 뒤 간판을 앞 간판 자리로 한 칸씩
            var c = kids(doc.pageItems.getByName("자동생성")), j = 0;
            for (i = 0; i < pos.length; i++) {
                if (MAP[i][0] == "(주)안랩") continue;
                var nb = bounds(c[j]), target = pos[j];
                c[j].translate(target[0] - nb[0], target[1] - nb[1]); j++;
            }
        }
        var a = snap(doc), ok = a.length == expect.length;
        for (i = 0; i < a.length; i++) {
            out.push("후 " + (i + 1) + " " + a[i].name + " [" + a[i].nv + "] " + mm(a[i].b).join(","));
            if (!ok || a[i].name != expect[i][0] || a[i].nv != expect[i][1] + "/" + expect[i][1] || a[i].key.replace(/\| .*/, "") != expect[i][2].replace(/\| .*/, "")) { ok = false; out.push("  ↑ 예상과 다름"); }
            if (Math.abs(a[i].b[0] - pos[i][0]) > 1 || Math.abs(a[i].b[1] - pos[i][1]) > 1) { ok = false; out.push("  ↑ 자리 어긋남"); }
        }
        out.push("장수 " + s.length + "→" + a.length + " / 안랩 " + (DROP_AHNLAB ? "뺌" : "유지(08)") + " / 검사 " + ok);
        var o = new ExportOptionsPNG24(); o.horizontalScale = o.verticalScale = 150; o.artBoardClipping = true;
        doc.exportFile(File(Folder.temp.fsName + "/bsg/full.png"), ExportType.PNG24, o);
        if (ok) {
            o.horizontalScale = o.verticalScale = 60;
            doc.exportFile(File(WORK + "부스간판_자동생성_미리보기.png"), ExportType.PNG24, o);
            doc.save(); out.push("saved");
        } else out.push("검사 불통과 — 저장 안 함");
    } catch (e) { out.push("ERROR " + e.message + " line " + e.line); }
    doc.close(SaveOptions.DONOTSAVECHANGES);
}
var g = File(Folder.temp.fsName + "/bsg_renum.txt"); g.encoding = "UTF-8"; g.open("w"); g.write(out.join("\n")); g.close();

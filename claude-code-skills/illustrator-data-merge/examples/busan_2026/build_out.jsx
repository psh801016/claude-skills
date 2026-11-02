// 출력 3단계: 원본 부스간판.ai → 출력/부스간판_출.ai (원본은 그대로).
// 간판 32장은 테두리 안을, 데스크 띠지 같은 다른 출력물은 그 클리핑 안을 render_signs.py 가 뽑은 150ppi CMYK 그림으로 바꾼다(같은 자리·같은 크기).
// 위 검정 번호 라벨(설치하는 분 확인용)·묶음 제목·띠지 설명 글자는 글자깨기(선으로)만. 날개는 이미 150ppi 그림. 미리보기 _출.jpg 도 만든다.
// 출력 폴더 기존 파일 규칙(콘솔가림막_출·카페테리아_출 실측): 대지는 원본과 같은 1/10, 그림은 실물 150ppi, 글자 0개.
// 간판은 모양으로 찾는다(stFindSigns) — '자동생성' 묶음이 풀려 있어도 된다.
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, out = [];
var SRC = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/원본/부스간판.ai";
var DST = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/출력/부스간판_출.ai";
var JPG = "X:/[11.04-05] 2026 부산 사이버보안 콘퍼런스/3 3D/발주/출력/부스간판_출.jpg";
var WORK = "G:/내 드라이브/AI-작업기록/claude/2026-10-15_부산사이버보안_부스간판/";
var SK = "C:/Users/PSH/.agents/skills/illustrator-data-merge/scripts/";
$.global.FT_NO_MAIN = true;
$.evalFile(File(SK + "fill_template.jsx"));
$.evalFile(File(SK + "sign_tools.jsx"));
function img(id) { return File(WORK + "출력그림/그림_" + id + ".tif"); }
function fit(it, b) { it.width = b[2] - b[0]; it.height = b[1] - b[3]; it.left = b[0]; it.top = b[1]; }

var busy = false;
for (var d = 0; d < app.documents.length; d++) if (/^부스간판(_출)?\.ai$/.test(app.documents[d].name)) busy = true;
if (busy) out.push("부스간판.ai 또는 부스간판_출.ai 가 열려 있음 — 중단");
else {
    var doc = app.open(File(SRC));
    try {
        // 위치표와 같은 간판·같은 순서인지 먼저 확인 (원본은 아직 안 바뀐 상태)
        var tf = File(WORK + "출력그림/간판위치.tsv"); tf.encoding = "UTF-8"; tf.open("r"); var rows = tf.read().split("\n"); tf.close();
        var found = stFindSigns(doc), cards = found.signs, others = found.others, meta = [], c, i;
        if (cards.length != 32 || cards.length + others.length != rows.length - 1) throw new Error("간판 " + cards.length + " + 기타 " + others.length + " / 위치표 " + (rows.length - 1));
        for (c = 0; c < cards.length; c++) {
            var r = stInfo(cards[c]), cols = rows[c + 1].split("\t");
            if (cols[0] != "S" + c || cols[1] != r.num || cols[2] != r.name) throw new Error((c + 1) + "번째가 다름: " + r.num + " " + r.name + " ≠ " + cols.slice(0, 3).join(" "));
            if (!img("S" + c).exists) throw new Error("그림 없음 S" + c);
            meta.push(r.w);
        }
        for (c = 0; c < others.length; c++) if (!img("O" + c).exists) throw new Error("그림 없음 O" + c);

        doc.saveAs(File(DST));                                     // 여기부터는 출력 파일만 고친다

        for (c = 0; c < cards.length; c++) {                       // 간판 테두리 안 → 그림 (라벨은 그대로)
            var clip = stClipOf(cards[c]), sign = clip.parent, cb = clip.geometricBounds;
            fit(stEmbed(cards[c], img("S" + c)), cb);
            sign.remove();
        }
        var rowItems = []; for (c = 0; c < cards.length; c++) rowItems.push(cards[c]);
        for (c = 0; c < others.length; c++) {                      // 데스크 켈지 등 → 같은 자리 그림
            var ob = stClipPathOf(others[c]).geometricBounds;
            var oimg = stEmbed(others[c].parent, img("O" + c)); fit(oimg, ob);
            if ((ob[2] - ob[0]) / MM > 200) rowItems.push(oimg);      // 간판 크기(체험부스 등)는 줄 그룹에 넣고, 켈지(95mm)는 뺀다
            others[c].remove();
        }
        var tfs = [];                                              // 글자깨기 (라벨·제목·설명 전부)
        for (i = 0; i < doc.textFrames.length; i++) tfs.push(doc.textFrames[i]);
        for (i = 0; i < tfs.length; i++) tfs[i].createOutline();

        // 검사 — 바꾼 뒤에는 클리핑 그룹이 없어 stFindSigns 로는 간판을 못 센다(1차 실행 0/32 오판) → 처음 찾은 간판 묶음을 그대로 본다
        var after = stFindSigns(doc), bad = [], big = 0, rgb = 0, allR = 0;
        for (c = 0; c < cards.length; c++) {
            var rs = [];
            stWalk(cards[c], function (it) { if (it.typename == "RasterItem") rs.push(it); });
            if (rs.length != 1) { bad.push((c + 1) + "번째 그림 " + rs.length + "개"); continue; }
            var ib = rs[0].geometricBounds;
            if (Math.abs((ib[2] - ib[0]) / MM - meta[c]) > 0.2) bad.push((c + 1) + "번째 폭 " + Math.round((ib[2] - ib[0]) / MM * 10) / 10);
            else big++;
        }
        for (i = 0; i < doc.rasterItems.length; i++) { allR++; if (doc.rasterItems[i].imageColorSpace != ImageColorSpace.CMYK) rgb++; }
        out.push("간판 그림 " + big + "/32 · 남은 클리핑 출력물 " + after.others.length + " · 그림 전체 " + allR + " · RGB " + rgb + " · 남은 글자 " + doc.textFrames.length + " · 문제 " + bad.length);
        for (c = 0; c < bad.length; c++) out.push("  ! " + bad[c]);
        if (big == 32 && after.signs.length == 0 && after.others.length == 0 && allR == 32 + others.length + 2 && rgb == 0 && doc.textFrames.length == 0 && !bad.length) {
            var nRows = stGroupRows(rowItems, "줄");                 // 한 줄(최대 10장)씩 한 그룹 (ASURA님 10-23)
            doc.saveAs(File(DST), stCS6Options()); out.push("saved CS6 " + DST + " / 줄 그룹 " + nRows);   // 인쇄업체용 CS6
            var o = new ExportOptionsJPEG(); o.artBoardClipping = true; o.qualitySetting = 80; o.horizontalScale = o.verticalScale = 100;
            doc.exportFile(File(JPG), ExportType.JPEG, o); out.push("jpg " + JPG);
        } else out.push("검사 불통과 — 저장 안 함 (saveAs 로 생긴 출력 파일은 원본 사본 상태로 남음)");
    } catch (e) { out.push("ERROR " + e.message + " line " + e.line); }
    doc.close(SaveOptions.DONOTSAVECHANGES);
}
var g = File(Folder.temp.fsName + "/bsg_out.txt"); g.encoding = "UTF-8"; g.open("w"); g.write(out.join("\n")); g.close();

// order_label.jsx — 아트보드 치수 라벨 + 발주값 검증 + CSV 내보내기
//
// 기존 artboard_size_label.jsx(치수만 찍음)의 확장판이다. 하던 대로 한 번 실행하면
//   1) 치수 라벨을 찍고 (기존 기능 그대로)
//   2) 그 치수가 옥타 발주표의 정규값인지 판정해 아니면 ⚠ 와 가까운 정규값을 같이 찍고
//   3) 같은 폴더에 <문서명>_발주표.csv 를 떨궈 order_check.py 가 그대로 받는다.
//
// 규칙 정본: AUSURA wiki/reference/octanorm-booth-order-specs.md
// 설치: Illustrator > 파일 > 스크립트 > 기타 스크립트… 로 이 파일 실행
//       (자주 쓰면 Presets\<언어>\Scripts 에 복사해두면 메뉴에 뜬다)

// ── 설정 ──────────────────────────────────────────────────────────
var SCALE = 10;          // 작업 축척. 1/10 로 그리면 10, 실치수로 그리면 1
var LABEL_FONT = "GmarketSansMedium";
var LABEL_SIZE = 50;
var WRITE_CSV = true;

// 옥타 발주 정규값 (가로). 2.5m 초과 높이일 때 값이 갈리는 폭은 둘 다 넣는다.
var OCTA_W = [450, 950, 1445, 1940, 1950, 2435, 2930, 2940, 3920, 3930, 4910, 4920];
var OCTA_LABEL = {
    450: "0.5m", 950: "1m", 1445: "1.5m",
    1940: "2m", 1950: "2m(+10)", 2435: "2.5m",
    2930: "3m", 2940: "3m(+10)", 3920: "4m", 3930: "4m(+10)",
    4910: "5m", 4920: "5m(+10)"
};
var TOL = 3;             // ±3mm 안이면 그 정규값으로 본다 (반올림 오차 흡수)

// ── 유틸 ──────────────────────────────────────────────────────────
function ptToMm(pt) { return Math.round(pt * 0.352778) * SCALE; }

function nearestOcta(w) {
    var best = null, bestD = 1e9;
    for (var i = 0; i < OCTA_W.length; i++) {
        var d = Math.abs(OCTA_W[i] - w);
        if (d < bestD) { bestD = d; best = OCTA_W[i]; }
    }
    return { value: best, diff: bestD };
}

function csvCell(s) {
    s = String(s);
    return (s.indexOf(",") >= 0 || s.indexOf('"') >= 0)
        ? '"' + s.replace(/"/g, '""') + '"' : s;
}

// ── 본체 ──────────────────────────────────────────────────────────
var doc = app.activeDocument;
var rows = [];
var warned = 0;

for (var i = 0; i < doc.artboards.length; i++) {
    var ab = doc.artboards[i];
    var rect = ab.artboardRect;                 // [left, top, right, bottom]
    var w = ptToMm(rect[2] - rect[0]);
    var h = ptToMm(rect[1] - rect[3]);

    var near = nearestOcta(w);
    var ok = (near.diff <= TOL);
    var text = w + " x " + h + " mm";
    var note = "";

    if (ok) {
        note = OCTA_LABEL[near.value];
        text += "  [" + note + "]";
    } else {
        warned++;
        note = "옥타 정규값 아님 (가까운 값 " + near.value + ")";
        text += "  ⚠ " + near.value + "?";
    }

    var lbl = doc.textFrames.add();
    lbl.contents = text;
    var attr = lbl.textRange.characterAttributes;
    attr.size = LABEL_SIZE;
    try { attr.textFont = app.textFonts.getByName(LABEL_FONT); } catch (e) {}
    var c = new RGBColor();
    if (ok) { c.red = 0; c.green = 0; c.blue = 0; }
    else    { c.red = 220; c.green = 30; c.blue = 30; }   // 정규값 아니면 빨강
    attr.fillColor = c;
    lbl.left = rect[0];
    lbl.top = rect[1] + 75;

    rows.push([ab.name, w, h, ok ? OCTA_LABEL[near.value] : "", "", "", w, h, note]);
}

// ── CSV ───────────────────────────────────────────────────────────
var msg = "아트보드 " + doc.artboards.length + "개 라벨 완료.\n";
msg += warned ? ("⚠ 옥타 정규값이 아닌 아트보드 " + warned + "개 — 빨간 라벨 확인\n")
              : "전부 옥타 정규값입니다.\n";

if (WRITE_CSV) {
    try {
        var out = new File(doc.path + "/" + doc.name.replace(/\.[^.]+$/, "") + "_발주표.csv");
        out.encoding = "UTF-8";
        out.open("w");
        out.writeln("﻿구역,폭,세로,마감,수량,양면,적힌가로,적힌세로,비고");
        for (var r = 0; r < rows.length; r++) {
            var line = [];
            for (var k = 0; k < rows[r].length; k++) line.push(csvCell(rows[r][k]));
            out.writeln(line.join(","));
        }
        out.close();
        msg += "\nCSV 저장: " + out.fsName + "\n";
        msg += "→ 마감·수량 칸을 채운 뒤\n   python order_check.py sizes \"<csv>\" 로 검산하세요.";
    } catch (e) {
        msg += "\nCSV 저장 실패(문서를 먼저 저장했는지 확인): " + e;
    }
}

alert(msg);

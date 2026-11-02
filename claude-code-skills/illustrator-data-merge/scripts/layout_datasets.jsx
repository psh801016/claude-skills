// layout_datasets.jsx — 변수 패널의 데이터셋을 한 장씩 복제해 격자로 깔아 준다.
//
// 영상(디자이너맘)에서 '샘플 폴더의 스크립트'가 하던 일을 대신한다.
// 준비: 변수 패널에 CSV 를 불러온 뒤, 카드 전체를 Ctrl+G 로 묶고 그 그룹 하나만 선택.
// 실행: 파일 > 스크립트 > 기타 스크립트… 로 이 파일.
// 결과: 원본 그룹 = 1번 데이터, 오른쪽·아래로 2번부터 복제본. 열 수는 √개수 올림(12개면 4열).
//       복제본은 변수 연결이 끊긴 일반 오브젝트라 따로 고쳐도 된다.

var GAP_MM = 10;   // 카드 사이 간격

function layoutDatasets(doc, tpl) {
    var sets = doc.dataSets;
    if (sets.length === 0) throw new Error("데이터셋이 없습니다. 변수 패널에서 CSV 를 먼저 불러오세요.");
    var gap = GAP_MM * 72 / 25.4;
    var b = tpl.visibleBounds;                       // [left, top, right, bottom]
    var w = b[2] - b[0], h = b[1] - b[3];
    var cols = Math.ceil(Math.sqrt(sets.length));
    for (var i = 1; i < sets.length; i++) {
        sets[i].display();
        var dup = tpl.duplicate();
        dup.translate((i % cols) * (w + gap), -Math.floor(i / cols) * (h + gap));
    }
    sets[0].display();
    return sets.length;
}

if (!$.global.DM_NO_MAIN) {
    try {
        var doc = app.activeDocument;
        if (doc.selection.length !== 1) throw new Error("Ctrl+G 로 묶은 카드 그룹 하나만 선택하고 실행하세요.");
        alert(layoutDatasets(doc, doc.selection[0]) + "장 배치 완료");
    } catch (e) {
        alert(e.message);
    }
}

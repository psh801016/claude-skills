// 시트 바탕을 연회색으로 — 흰 바탕 판이 흰 시트와 구분 안 되는 문제 (ASURA님 지적 2026-10-23).
// 대지 전체 크기의 회색 사각형을 맨 아래 '시트 바탕' 레이어에 깐다. 판(흰판 포함)은 건드리지 않는다. 두 번 돌려도 하나만.
#target illustrator
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var LOG = [];
for (var j = 0; j < KEYS.length; j++) {
  var f = new File("C:/jjb/out/" + KEYS[j] + ".ai"), doc = app.open(f), L = null;
  for (var i = 0; i < doc.layers.length; i++) if (doc.layers[i].name == "시트 바탕") L = doc.layers[i];
  if (!L) {
    L = doc.layers.add(); L.name = "시트 바탕"; L.move(doc, ElementPlacement.PLACEATEND);
    var r = doc.artboards[0].artboardRect, c = new CMYKColor(); c.cyan = 0; c.magenta = 0; c.yellow = 0; c.black = 25;
    var p = L.pathItems.rectangle(r[1], r[0], r[2] - r[0], r[1] - r[3]);
    p.stroked = false; p.filled = true; p.fillColor = c; p.name = "시트 바탕";
    L.locked = true;
    var so = new IllustratorSaveOptions(); so.pdfCompatible = true; so.embedLinkedFiles = true; so.compressed = true;
    doc.saveAs(f, so);
    LOG.push(KEYS[j] + " 회색 바탕 추가");
  } else LOG.push(KEYS[j] + " 이미 있음");
  doc.close(SaveOptions.DONOTSAVECHANGES);
}
var lf = new File("C:/jjb/sheetbg_log.txt"); lf.encoding = "UTF-8"; lf.open("w"); lf.write(LOG.join("\n")); lf.close();

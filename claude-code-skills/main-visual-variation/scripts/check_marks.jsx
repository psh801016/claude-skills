// 발주 시트 ㄱㄴ(여유 표시) 검산+교정. 배경: 2026-11-04 KOBC — 사용자가 판을 옮기면 ㄱㄴ이 따라가지 않아 4판이 어긋났다("목공 표시 ㄱㄴ 잘못된곳있어 고쳐").
// 규칙: 각 판 클리핑 외곽에서 안쪽 10mm(1/10 시트 = 실물 100) 사각형의 왼쪽 위 ㄱ / 오른쪽 아래 ㄴ. 가장 가까운 판에 맞춰 평행이동하고 dx·dy를 기록한다.
// 입력: C:/mvv/out/check_marks.txt  1줄 = 시트 사본 폴더(안의 *.ai 전부), 2줄 = jpg 내보내기 배율(기본 150). 원본이 아니라 사본에서 돌리고, 검증 뒤 백업하고 덮어쓴다.
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var cf = new File("C:/mvv/out/check_marks.txt"); cf.encoding = "UTF-8"; cf.open("r"); var cfg = cf.read().replace(/\r/g, "").split("\n"); cf.close();
var dir = cfg[0], scale = parseInt(cfg[1] || "150", 10), MM = 72/25.4, out = [], files = new Folder(dir).getFiles("*.ai"), names = [];
for (var q = 0; q < files.length; q++) names.push(decodeURI(files[q].name).replace(/\.ai$/i, ""));
for (var n = 0; n < names.length; n++) {
  var d = app.open(new File(dir + "/" + names[n] + ".ai")), L = d.layers[0], panels = [], marks = [];
  for (var i = 0; i < L.pageItems.length; i++) {
    var it = L.pageItems[i];
    if (it.typename == "GroupItem" && it.clipped) { for (var k = 0; k < it.pageItems.length; k++) if (it.pageItems[k].typename == "PathItem" && it.pageItems[k].clipping) { var c = it.pageItems[k].geometricBounds; panels.push({n: it.name, L: c[0]+10*MM, T: c[1]-10*MM, R: c[2]-10*MM, B: c[3]+10*MM}); break; } }
    else if (it.name.indexOf("여유") >= 0) marks.push(it);
  }
  for (var m = 0; m < marks.length; m++) {
    var b = marks[m].geometricBounds, cx = (b[0]+b[2])/2, cy = (b[1]+b[3])/2, best = null, bd = 1e9;
    for (var p = 0; p < panels.length; p++) { var px = (panels[p].L+panels[p].R)/2, py = (panels[p].T+panels[p].B)/2, dd = Math.abs(px-cx)+Math.abs(py-cy); if (dd < bd) { bd = dd; best = panels[p]; } }
    var dx = best.L - b[0], dy = best.T - b[1];
    var sizeOk = Math.abs((b[2]-b[0]) - (best.R-best.L)) < 0.5 && Math.abs((b[1]-b[3]) - (best.T-best.B)) < 0.5;
    if (Math.abs(dx) > 0.1 || Math.abs(dy) > 0.1) marks[m].translate(dx, dy);
    out.push(names[n] + " " + best.n + " dx=" + (dx/MM).toFixed(1) + " dy=" + (dy/MM).toFixed(1) + " size" + (sizeOk ? "OK" : "MISMATCH"));
  }
  d.save();
  var o = new ExportOptionsJPEG(); o.qualitySetting = 80; o.horizontalScale = scale; o.verticalScale = scale; o.artBoardClipping = true; o.antiAliasing = true;
  d.exportFile(new File(dir + "/" + names[n] + "_발주.jpg"), ExportType.JPEG, o);
  d.close(SaveOptions.DONOTSAVECHANGES);
}
var f = new File(dir + "/_marks.txt"); f.encoding = "UTF-8"; f.open("w"); f.write(out.join("\n")); f.close();

// 사용자가 고친 그룹 발주 시트(.ai 사본)에서 판마다 맥스 맵 PNG 를 뽑는다.
// 배경: 2026-11-03 KOBC — 사용자가 포토존 시트를 직접 고친 뒤 "맵으로 뽑아줘". 원본 문서는 열지 않고 사본만 연다.
// 입력: C:/mvv/out/sheet_maps.txt  1줄 = 사본 .ai 경로, 2줄 = 결과 폴더. 판 = 이름 있는 클리핑 그룹, 보이는 면 = 클리핑 외곽 - 여유 10mm(1/10 시트 = 실물 100).
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var cf = new File("C:/mvv/out/sheet_maps.txt"); cf.encoding = "UTF-8"; cf.open("r");
var cfg = cf.read().replace(/\r/g, "").split("\n"); cf.close();
var d = app.open(new File(cfg[0])), MM = 72 / 25.4, B = 10 * MM, done = [];
try { d.layers.getByName("시트 바탕").visible = false; } catch (e) {}
var dst = new Folder(cfg[1]); if (!dst.exists) dst.create();
var L = d.layers[0], panels = [];
for (var i = 0; i < L.pageItems.length; i++) {
  var it = L.pageItems[i];
  if (it.typename == "GroupItem" && it.clipped && it.name) panels.push(it); else it.hidden = true;  // 라벨·여유 표시 숨김
}
for (var n = 0; n < panels.length; n++) {
  var g = panels[n], cb = null;
  for (var k = 0; k < g.pageItems.length; k++) if (g.pageItems[k].typename == "PathItem" && g.pageItems[k].clipping) { cb = g.pageItems[k].geometricBounds; break; }
  if (!cb) continue;
  var ab = d.artboards.add([cb[0] + B, cb[1] - B, cb[2] - B, cb[3] + B]); ab.name = g.name;
  var op = new ExportForScreensOptionsPNG24(); op.transparentBackground = true; op.antiAliasing = AntiAliasingMethod.ARTOPTIMIZED;
  op.scaleType = ExportForScreensScaleType.SCALEBYFACTOR; op.scaleTypeValue = 2;
  var ex = new ExportForScreensItemToExport(); ex.artboards = String(d.artboards.length); ex.document = false;
  d.exportForScreens(dst, ExportForScreensType.SE_PNG24, op, ex, "");
  done.push(g.name);
}
d.close(SaveOptions.DONOTSAVECHANGES);
var f = new File(cfg[1] + "/_done.txt"); f.encoding = "UTF-8"; f.open("w"); f.write("OK " + done.join("|")); f.close();

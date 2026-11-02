// 원본 사본(C:/mvv/src/*.ai)의 조각 지도를 뽑는다 → C:/mvv/probe.txt. PIECES 영역을 정할 때 본다. 저장하지 않는다.
// 대지 기준 mm(x,y 좌상단, 아래로 +). 묶음은 2단까지 안으로 들어가 본다. 대지 밖(x<0 또는 x>W)에 놓인 옛 조각도 그대로 적는다 — 고르지 않기 위해 알아야 한다.
#target illustrator
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4;
var out = new File("C:/mvv/probe.txt"); out.encoding = "UTF-8"; out.open("w");
function f1(v) { return (Math.round(v * 10) / 10).toString(); }
function dump(items, ox, oy, depth, pre) {
  for (var i = 0; i < items.length; i++) {
    var p = items[i], b = p.geometricBounds, extra = "";
    if (p.typename == "TextFrame") extra = " '" + p.contents.replace(/[\r\n]+/g, " / ").substr(0, 40) + "'";
    if (p.typename == "GroupItem") extra = " sub=" + p.pageItems.length + (p.clipped ? " CLIP" : "") + (p.opacity != 100 ? " op" + p.opacity : "");
    if (p.typename == "RasterItem") extra = " " + p.imageColorSpace;
    out.writeln(pre + p.typename + (p.name ? " '" + p.name + "'" : "") + (p.hidden ? " HID" : "") + " x=" + f1((b[0] - ox) / MM) + " y=" + f1((oy - b[1]) / MM) + " w=" + f1((b[2] - b[0]) / MM) + " h=" + f1((b[1] - b[3]) / MM) + extra);
    if (p.typename == "GroupItem" && depth < 2) dump(p.pageItems, ox, oy, depth + 1, pre + "    ");
  }
}
var files = new Folder("C:/mvv/src").getFiles("*.ai");
for (var f = 0; f < files.length; f++) {
  var d = app.open(files[f]);
  for (var a = 0; a < d.artboards.length; a++) {
    var r = d.artboards[a].artboardRect;
    out.writeln("== " + files[f].name + " AB" + (a + 1) + " " + f1((r[2] - r[0]) / MM) + "x" + f1((r[1] - r[3]) / MM) + "mm color=" + d.documentColorSpace);
    for (var l = 0; l < d.layers.length; l++) {
      var L = d.layers[l];
      out.writeln("  LAYER '" + L.name + "' vis=" + L.visible + " lock=" + L.locked + " items=" + L.pageItems.length);
      dump(L.pageItems, r[0], r[1], 0, "    ");
    }
  }
  d.close(SaveOptions.DONOTSAVECHANGES);
}
out.close();

// RGB 원본 색 맞춤 — 결과 시트(out/<KEY>.ai)의 RGB 유래 색을 '원본 RGB 에 가장 가까운 CMYK' 로 바꾼다.
// MODE="export": 원본 RGB 색 목록 + 시트 안 RGB 그림을 PNG(원래 픽셀 수)로 뽑는다 → python colorize.py 가 변환
// MODE="apply" : <KEY>_map.js 의 색표로 벡터 색·그라데이션 정지점을 바꾸고, RGB 그림을 변환된 CMYK TIFF 로 갈아 끼운다
// 원본·시트 외 문서는 건드리지 않는다 (C:/jjb 아래만 열고 닫음)
#target illustrator
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var DIR = "C:/jjb/color/", OUT = "C:/jjb/out/" + KEY + ".ai", LOG = [], TEMPS = [];
function w(path, text) { var f = new File(path); f.encoding = "UTF-8"; f.open("w"); f.write(text); f.close(); }
function rgbKey(c) { return Math.round(c.red) + "," + Math.round(c.green) + "," + Math.round(c.blue); }

function eachPath(items, fn) {
  for (var i = 0; i < items.length; i++) {
    var p = items[i];
    if (p.typename == "GroupItem") eachPath(p.pageItems, fn);
    else if (p.typename == "CompoundPathItem") { for (var k = 0; k < p.pathItems.length; k++) fn(p.pathItems[k]); }
    else if (p.typename == "PathItem") fn(p);
  }
}
function eachLayerPath(doc, fn) {
  function L(layers) { for (var i = 0; i < layers.length; i++) { eachPath(layers[i].pageItems, fn); L(layers[i].layers); } }
  L(doc.layers);
}

function doExport() {
  var seen = {}, list = [];
  function add(c) { if (c && c.typename == "RGBColor") { var k = rgbKey(c); if (!seen[k]) { seen[k] = 1; list.push(k); } } }
  // 그림은 '원본'(RGB 문서)에서 뽑는다 — 결과 시트(CMYK)는 저장할 때 일러가 이미 미국 기준 CMYK 로 바꿔 버린다.
  // 같은 그림이 판마다 복제되므로 픽셀 크기(가로x세로)로 한 번씩만 뽑고, apply 때 같은 크기 그림을 갈아 끼운다.
  var man = [], done = {};
  var pre = new DocumentPreset(); pre.colorMode = DocumentColorSpace.RGB; pre.width = 500; pre.height = 500;
  for (var s = 0; s < SRCS.length; s++) {
    if (SRCS[s][1]) app.preferences.PDFFileOptions.pageToOpen = SRCS[s][1];
    var d = app.open(new File("C:/jjb/src/" + SRCS[s][0]));
    eachLayerPath(d, function (p) { if (p.filled) add(p.fillColor); if (p.stroked) add(p.strokeColor); });
    for (var g = 0; g < d.gradients.length; g++) { var st = d.gradients[g].gradientStops; for (var j = 0; j < st.length; j++) add(st[j].color); }
    var ras = [];
    for (var i = 0; i < d.rasterItems.length; i++) if (d.rasterItems[i].imageColorSpace == ImageColorSpace.RGB) ras.push(d.rasterItems[i]);
    for (var n = 0; n < ras.length; n++) exportRaster(ras[n]);
    d.close(SaveOptions.DONOTSAVECHANGES);
  }
  if (list.length) w(DIR + KEY + "_colors.txt", list.join("\n"));
  w(DIR + KEY + "_rasters.txt", man.join("\n"));
  LOG.push(KEY + " export colors=" + list.length + " rasters=" + man.length);

  function exportRaster(r) {
    var px = r.boundingBox[2], py = r.boundingBox[1], dim = px + "x" + py;
    if (done[dim]) return; done[dim] = 1;
    var tmp = app.documents.addDocument("", pre), ab = tmp.artboards[0].artboardRect;
    TEMPS.push(tmp);
    var dup = r.duplicate(tmp.layers[0], ElementPlacement.PLACEATBEGINNING);
    var b = dup.geometricBounds;   // 1px = 1pt 로 맞춰 100% 로 내보내면 원래 픽셀 수 그대로
    dup.resize(px / (b[2] - b[0]) * 100, py / (b[1] - b[3]) * 100, true, true, true, true, 100, Transformation.TOPLEFT);
    b = dup.geometricBounds; dup.translate(ab[0] - b[0], ab[1] - b[1]); b = dup.geometricBounds;
    tmp.artboards[0].artboardRect = b;
    var o = new ExportOptionsPNG24(); o.artBoardClipping = true; o.horizontalScale = o.verticalScale = 100; o.transparency = r.transparent; o.antiAliasing = false;
    tmp.exportFile(new File(DIR + KEY + "_" + dim + ".png"), ExportType.PNG24, o);
    tmp.close(SaveOptions.DONOTSAVECHANGES);
    man.push(px + "|" + py + "|" + r.transparent);
  }
}

function doApply() {
  $.evalFile(DIR + KEY + "_map.js");   // CMAP = [[r,g,b, c,m,y,k], ...], RAS = [tif 파일명, ...] (export 순서)
  var doc = app.open(new File(OUT)), lay = doc.layers[0];
  // 일러가 이 문서에서 해당 RGB 를 어떤 CMYK 로 바꿨는지 직접 재서 열쇠로 쓴다
  var keys = [];
  for (var i = 0; i < CMAP.length; i++) {
    var t = lay.pathItems.rectangle(0, 0, 1, 1), c = new RGBColor(); c.red = CMAP[i][0]; c.green = CMAP[i][1]; c.blue = CMAP[i][2];
    t.fillColor = c; var m = t.fillColor; keys.push([m.cyan, m.magenta, m.yellow, m.black]); t.remove();
  }
  function target(col) {
    if (!col || col.typename != "CMYKColor") return null;
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      if (Math.abs(k[0] - col.cyan) < 0.3 && Math.abs(k[1] - col.magenta) < 0.3 && Math.abs(k[2] - col.yellow) < 0.3 && Math.abs(k[3] - col.black) < 0.3) {
        var n = new CMYKColor(); n.cyan = CMAP[i][3]; n.magenta = CMAP[i][4]; n.yellow = CMAP[i][5]; n.black = CMAP[i][6]; return n;
      }
    }
    return null;
  }
  var nf = 0, ns = 0, ng = 0;
  eachLayerPath(doc, function (p) {
    if (p.filled) { var a = target(p.fillColor); if (a) { p.fillColor = a; nf++; } }
    if (p.stroked) { var b = target(p.strokeColor); if (b) { p.strokeColor = b; ns++; } }
  });
  for (var g = 0; g < doc.gradients.length; g++) {
    var st = doc.gradients[g].gradientStops;
    for (var j = 0; j < st.length; j++) { var q = target(st[j].color); if (q) { st[j].color = q; ng++; } }
  }
  // 그림 교체 — 픽셀 크기가 같은 그림을 색 맞춤 TIFF 로 (RAS = {"가로x세로": tif})
  var olds = [], miss = 0;
  for (var r = 0; r < doc.rasterItems.length; r++) {
    var R = doc.rasterItems[r], dim = R.boundingBox[2] + "x" + R.boundingBox[1];
    if (RAS[dim]) olds.push([R, RAS[dim]]); else miss++;
  }
  for (var z = 0; z < olds.length; z++) {
    var old = olds[z][0], ob = old.geometricBounds;
    var pi = lay.placedItems.add(); pi.file = new File(DIR + olds[z][1]); pi.embed();
    var it = lay.pageItems[0], nb = it.geometricBounds;
    it.resize((ob[2] - ob[0]) / (nb[2] - nb[0]) * 100, (ob[1] - ob[3]) / (nb[1] - nb[3]) * 100, true, true, true, true, 100, Transformation.TOPLEFT);
    nb = it.geometricBounds; it.translate(ob[0] - nb[0], ob[1] - nb[1]);
    it.move(old, ElementPlacement.PLACEBEFORE);
    old.remove();
  }
  var left = 0; for (var e = 0; e < doc.rasterItems.length; e++) if (doc.rasterItems[e].imageColorSpace == ImageColorSpace.RGB) left++;
  var so = new IllustratorSaveOptions(); so.pdfCompatible = true; so.embedLinkedFiles = true; so.compressed = true;
  doc.saveAs(new File(OUT), so); doc.close(SaveOptions.DONOTSAVECHANGES);
  LOG.push(KEY + " apply fills=" + nf + " strokes=" + ns + " gradStops=" + ng + " rasters_replaced=" + olds.length + " rasters_unmatched=" + miss + " rgb_left=" + left);
}

try { if (MODE == "export") doExport(); else doApply(); }
catch (err) {
  LOG.push(KEY + " ERROR " + err + " line " + err.line);
  for (var i = app.documents.length - 1; i >= 0; i--) { var p = ""; try { p = app.documents[i].fullName.fsName; } catch (e) { p = app.documents[i].name; }
    if (p.toLowerCase().indexOf("c:\\jjb\\") == 0) app.documents[i].close(SaveOptions.DONOTSAVECHANGES); }
  for (var t = 0; t < TEMPS.length; t++) { try { TEMPS[t].close(SaveOptions.DONOTSAVECHANGES); } catch (e) {} }   // 내가 만든 임시 문서만
}
var lf = new File(DIR + "log.txt"); lf.encoding = "UTF-8"; lf.open("a"); lf.writeln(LOG.join("\n")); lf.close();

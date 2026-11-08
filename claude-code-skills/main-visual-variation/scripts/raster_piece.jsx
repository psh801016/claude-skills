// BMFW CMYK.ai 의 도시·크레인·항로 조각만 투명 PNG 로 — 1/10 시트에 벡터로 넣으면 7,695개 가는 선이 내보내기에서 사라졌다(2026-11-03).
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var src = app.open(new File("C:/mvv/src/bmfw.ai"));
for (var l = 0; l < src.layers.length; l++) { src.layers[l].locked = false; src.layers[l].visible = true; }
var pre = new DocumentPreset(); pre.colorMode = DocumentColorSpace.CMYK; pre.width = 800; pre.height = 600;
var d = app.documents.addDocument("", pre);
d.rasterEffectSettings.resolution = 300;
var C = [[1, 4], [1, 3], [1, 2], [1, 1]];
for (var i = C.length - 1; i >= 0; i--) { src.activate(); src.layers[C[i][0]].pageItems[C[i][1]].duplicate(d.layers[0], ElementPlacement.PLACEATBEGINNING); }
d.activate();
// 스크린·컬러닷지 빛기둥은 투명 배경에 굳히면 회색 얼룩이 된다("도시건물 배 얼룩지는건 뭐여") → 합성 모드가 걸린 조각은 빼고 굳힌다
function dropBlend(c) { for (var i = c.pageItems.length - 1; i >= 0; i--) { var it = c.pageItems[i];
  var bm = BlendModes.NORMAL; try { bm = it.blendingMode; } catch (e) {}
  if (bm != BlendModes.NORMAL) { it.remove(); continue; }
  if (it.typename == "GroupItem") dropBlend(it); } }
dropBlend(d.layers[0]);
var L = 1e9, T = -1e9, R = -1e9, B = 1e9;
for (var k = 0; k < d.pageItems.length; k++) { var b = d.pageItems[k].visibleBounds; L = Math.min(L, b[0]); T = Math.max(T, b[1]); R = Math.max(R, b[2]); B = Math.min(B, b[3]); }
d.artboards[0].artboardRect = [L, T, R, B];
var o = new ExportOptionsPNG24(); o.artBoardClipping = true; o.transparency = true; o.antiAliasing = true;
o.horizontalScale = o.verticalScale = 600;
d.exportFile(new File("C:/mvv/src/photos/city_cmyk.png"), ExportType.PNG24, o);
d.close(SaveOptions.DONOTSAVECHANGES);
src.close(SaveOptions.DONOTSAVECHANGES);
var f = new File("C:/mvv/kobc/city_bounds.txt"); f.open("w"); f.write(((R - L) / 72 * 25.4) + "x" + ((T - B) / 72 * 25.4)); f.close();

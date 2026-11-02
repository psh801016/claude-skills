// 3D(맥스) 맵 PNG — 일러 '스크린용 내보내기'(Export for Screens)로 각 품목의 맵 대지(2번째 대지)를 PNG 로 뽑는다.
// ASURA님 2026-10-26 "맥스 맵으로 사용할꺼니깐 스크린인가 그걸로 각각 뽑아서 맵폴더에 넣으란소리야" — 사내 방식 = 일러 스크린용 내보내기 2x·투명 배경.
// 입력: C:/mvv/out/map_keys.txt (한 줄에 key 하나). 결과: C:/mvv/out/screens/<맵 대지 이름>.png (하위 폴더가 생기면 run 쪽에서 찾아 옮긴다)
if (app.documents.length) throw new Error("열린 문서가 있어 멈춤 — 사용자 문서를 건드리지 않는다");
var kf = new File("C:/mvv/out/map_keys.txt"); kf.encoding = "UTF-8"; kf.open("r");
var keys = kf.read().replace(/\r/g, "").split("\n"); kf.close();
var dst = new Folder("C:/mvv/out/screens"); if (!dst.exists) dst.create();
var done = [];
for (var i = 0; i < keys.length; i++) {
  if (!keys[i]) continue;
  var doc = app.open(new File("C:/mvv/out/" + keys[i] + ".ai"));
  for (var l = 0; l < doc.layers.length; l++) if (doc.layers[l].name == "시트 바탕" || doc.layers[l].name == "여유 표시") doc.layers[l].visible = false;
  var op = new ExportForScreensOptionsPNG24();
  op.transparentBackground = true; op.antiAliasing = AntiAliasingMethod.ARTOPTIMIZED;
  op.scaleType = ExportForScreensScaleType.SCALEBYFACTOR; op.scaleTypeValue = 2;   // 1/10 시트 2x = 144ppi (ASURA님 PNG 실측과 같음)
  var it = new ExportForScreensItemToExport(); it.artboards = "2"; it.document = false;
  doc.exportForScreens(dst, ExportForScreensType.SE_PNG24, op, it, "");
  done.push(doc.artboards[1].name);
  doc.close(SaveOptions.DONOTSAVECHANGES);
}
"OK " + done.join("|");

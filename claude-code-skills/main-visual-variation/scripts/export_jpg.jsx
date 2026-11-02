// 대지별 JPG 내보내기 (3D 맵 텍스처용, 150ppi). main-visual-variation.
// 사고 배경(2026-10-28): 교통문화 map 폴더의 텍스처가 jpg 였다. 글자만 고친 뒤 같은 이름·같은 픽셀로 다시 뽑아야
// 3ds Max 가 재질을 그대로 다시 읽는다. 일러 출력은 기존보다 1px 다를 수 있어 scripts/map_jpg.py 로 기존 크기에 맞춘다.
//
// 쓰는 법: C:/mvv/jsx/export_cfg.js 에
//   var EXPORT = { outDir: "C:/mvv/gt/map", ppi: 150, quality: 90, log: "C:/mvv/gt/export.txt",
//                  jobs: [["C:/mvv/gt/out_desk.ai", [[0, "등록데스크_01"], [1, "등록데스크_02"]]], ...] };  // [파일, [[대지번호, 이름]…]]
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
$.evalFile("C:/mvv/jsx/export_cfg.js");
var ppi = EXPORT.ppi || 150, q = EXPORT.quality || 90, out = [];
new Folder(EXPORT.outDir).create();
for (var i = 0; i < EXPORT.jobs.length; i++) {
  var d = app.open(new File(EXPORT.jobs[i][0])), list = EXPORT.jobs[i][1];
  for (var e = 0; e < list.length; e++) {
    d.artboards.setActiveArtboardIndex(list[e][0]);
    var o = new ExportOptionsJPEG();
    o.artBoardClipping = true; o.antiAliasing = true; o.qualitySetting = q;
    o.horizontalScale = ppi / 72 * 100; o.verticalScale = ppi / 72 * 100;
    d.exportFile(new File(EXPORT.outDir + "/" + list[e][1] + ".jpg"), ExportType.JPEG, o);
    out.push("exp " + list[e][1]);
  }
  d.close(SaveOptions.DONOTSAVECHANGES);
}
var lf = new File(EXPORT.log); lf.encoding = "UTF-8"; lf.open("w"); lf.write(out.join("\n")); lf.close();

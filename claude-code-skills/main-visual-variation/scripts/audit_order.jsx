// 발주 원본(.ai) 반려 점검표 자동 검사. 배경: 2026-11-05 "스킬에 적힌 대로 안 나오고 매번 몇십 번 반복" — 글자 잘림·판 밖 글자·작은 글자·날개 흐림·72ppi 가 사람 눈에만 맡겨져 있었다.
// 입력: C:/mvv/out/audit_order.txt  1줄 = 검사할 폴더(안의 *.ai 전부). 저장하지 않는다. 결과 C:/mvv/out/_audit.txt (줄마다 FAIL/PASS, 마지막 줄 AUDIT_PASS/AUDIT_FAIL)
// 검사: ① 클리핑 판 안 글자가 판 경계 밖으로 나감(잘림) ② 대지 밖 글자 ③ 글자 높이 < 3.0mm(1/10 시트 → 실물 30mm, "한 줄 33mm 는 작다")
//       ④ 이름에 '날개' 든 묶음 불투명도 < 80 ⑤ 래스터효과 < 300ppi ⑥ 문서 색공간 ≠ CMYK ⑦ 숨은 글자 없음
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var cf = new File("C:/mvv/out/audit_order.txt"); cf.encoding = "UTF-8"; cf.open("r"); var dir = cf.read().replace(/\r/g, "").split("\n")[0]; cf.close();
var MM = 72 / 25.4, out = [], nfail = 0, files = new Folder(dir).getFiles("*.ai");
function inside(b, c, tol) { return b[0] >= c[0] - tol && b[2] <= c[2] + tol && b[1] <= c[1] + tol && b[3] >= c[3] - tol; }
function walkText(items, acc) {
  for (var i = 0; i < items.length; i++) {
    var p = items[i];
    if (p.typename == "TextFrame") acc.push(p);
    else if (p.typename == "GroupItem") walkText(p.pageItems, acc);
  }
  return acc;
}
for (var f = 0; f < files.length; f++) {
  var d = app.open(files[f]), name = decodeURI(files[f].name), fl = [];
  try {
    if (d.documentColorSpace != DocumentColorSpace.CMYK) fl.push("색공간 " + d.documentColorSpace + " ≠ CMYK");
    if (d.rasterEffectSettings.resolution < 300) fl.push("래스터효과 " + d.rasterEffectSettings.resolution + "ppi < 300");
    var ab = d.artboards[0].artboardRect;
    for (var l = 0; l < d.layers.length; l++) {
      var L = d.layers[l];
      for (var i = 0; i < L.pageItems.length; i++) {
        var it = L.pageItems[i];
        if (it.typename == "GroupItem" && it.clipped) {
          var clip = null;
          for (var k = 0; k < it.pageItems.length; k++) if (it.pageItems[k].typename == "PathItem" && it.pageItems[k].clipping) { clip = it.pageItems[k].geometricBounds; break; }
          var tf = walkText(it.pageItems, []);
          for (var t = 0; t < tf.length; t++) {
            var b = tf[t].geometricBounds, txt = tf[t].contents.replace(/[\r\n]+/g, " ").substr(0, 24);
            if (clip && !inside(b, clip, 0.5)) fl.push("'" + (it.name || "판" + i) + "' 글자 잘림: '" + txt + "'");
            if ((b[1] - b[3]) / MM < 3.0 && tf[t].contents.replace(/\s/g, "").length) fl.push("'" + (it.name || "판" + i) + "' 글자 높이 " + ((b[1] - b[3]) / MM).toFixed(1) + "mm < 3.0: '" + txt + "'");
            if (tf[t].hidden) fl.push("숨은 글자: '" + txt + "'");
          }
          if (it.name.indexOf("날개") >= 0 && it.opacity < 80) fl.push("'" + it.name + "' 불투명도 " + it.opacity + " < 80");
        } else if (it.typename == "TextFrame") {
          var bb = it.geometricBounds;
          if (!inside(bb, ab, 0.5)) fl.push("대지 밖 글자: '" + it.contents.substr(0, 24) + "'");
        }
      }
    }
  } catch (e) { fl.push("검사 오류 " + e); }
  if (fl.length) { nfail++; out.push("FAIL " + name + " :: " + fl.join(" | ")); } else out.push("PASS " + name);
  d.close(SaveOptions.DONOTSAVECHANGES);
}
out.push(nfail ? "AUDIT_FAIL " + nfail + "/" + files.length : "AUDIT_PASS " + files.length);
var o = new File("C:/mvv/out/_audit.txt"); o.encoding = "UTF-8"; o.open("w"); o.write(out.join("\n")); o.close();

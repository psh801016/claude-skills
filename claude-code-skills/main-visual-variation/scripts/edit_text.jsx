// 글자만 고치는 수정 — 라이브 텍스트의 문구를 바꾸되 글상자 중심은 그대로 둔다 (main-visual-variation).
// 사고 배경(2026-10-28 교통문화발전대회 "행사명 다 붙여서"): 띄어쓰기 한 칸을 지우면 글상자 폭이 줄어
// 가운데 맞춤이 어긋난다. 지우기 전 geometricBounds 중심을 재고 지운 뒤 translate 로 되돌린다.
// 세로 날개(rotate 90) 글자도 같은 식으로 맞다.
//
// 쓰는 법: run.ps1 -Jsx 로 돌리기 전에 C:/mvv/jsx/edit_cfg.js 에 EDIT 를 쓴다.
//   var EDIT = {
//     files: [["C:/mvv/gt/desk.ai", "C:/mvv/gt/out_desk.ai"], ...],   // [열 파일, 저장할 파일]
//     find: "교통문화 발전대회", replace: "교통문화발전대회",             // find 가 들어간 글상자마다 적용
//     log: "C:/mvv/gt/fix.txt"
//   };
// replace 가 find 에서 글자만 빠진 꼴이면 그 글자만 remove() 해서 서식이 그대로 남는다.
// 그 밖(글자 추가·교체)은 find 전체를 지우고 insertionPoint 에 넣는다 — 서식은 앞 글자를 따른다, 결과를 꼭 렌더로 본다.
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
$.evalFile("C:/mvv/jsx/edit_cfg.js");

function removedOnly(a, b) {           // b 가 a 에서 글자 몇 개만 뺀 것이면 뺄 위치 목록, 아니면 null
  var out = [], j = 0;
  for (var i = 0; i < a.length; i++) {
    if (j < b.length && a.charAt(i) == b.charAt(j)) { j++; } else { out.push(i); }
  }
  if (j != b.length) { return null; }
  return out;
}

var out = [], drop = removedOnly(EDIT.find, EDIT.replace);
for (var f = 0; f < EDIT.files.length; f++) {
  var d = app.open(new File(EDIT.files[f][0])), n = 0;
  for (var t = 0; t < d.textFrames.length; t++) {
    var tf = d.textFrames[t], k = tf.contents.indexOf(EDIT.find);
    if (k < 0) { continue; }
    var b = tf.geometricBounds, cx = (b[0] + b[2]) / 2, cy = (b[1] + b[3]) / 2;
    if (drop) {
      for (var i = drop.length - 1; i >= 0; i--) { tf.textRange.characters[k + drop[i]].remove(); }
    } else {
      for (var i2 = EDIT.find.length - 1; i2 >= 0; i2--) { tf.textRange.characters[k + i2].remove(); }
      tf.textRange.insertionPoints[k].characters.add(EDIT.replace);
    }
    var a = tf.geometricBounds;
    tf.translate(cx - (a[0] + a[2]) / 2, cy - (a[1] + a[3]) / 2);
    n++; out.push(EDIT.files[f][1] + " #" + t + " -> " + tf.contents);
  }
  var so = new IllustratorSaveOptions(); so.pdfCompatible = true; so.embedICCProfile = true;
  d.saveAs(new File(EDIT.files[f][1]), so);
  d.close(SaveOptions.DONOTSAVECHANGES);
  out.push(EDIT.files[f][1] + " fixed=" + n);
}
var lf = new File(EDIT.log); lf.encoding = "UTF-8"; lf.open("w"); lf.write(out.join("\n")); lf.close();

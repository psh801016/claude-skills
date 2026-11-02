// 판(클리핑 그룹)마다 마스크 밖에 숨은 내용을 잰다: 가장 멀리 뻗은 거리(실치수 mm)와 통째로 바깥에 있는 객체 수.
// 계기: 2026-10-22 제이콥 정면 띠를 만들 때 원본 전체가 7.5배 늘어난 채 마스크 밑에 숨어 있었다 (ASURA님 지적).
#target illustrator
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, LOG = [];
function walk(items, cb) {
  for (var i = 0; i < items.length; i++) {
    var p = items[i];
    if (p.typename == "GroupItem") walk(p.pageItems, cb);
    else if (!(p.typename == "PathItem" && p.clipping)) cb(p);
  }
}
for (var j = 0; j < KEYS.length; j++) {
  var doc = app.open(new File(DIR + KEYS[j] + ".ai")), lay = doc.layers[0], res = [];
  for (var g = 0; g < lay.groupItems.length; g++) {
    var G = lay.groupItems[g];
    if (!G.clipped) continue;
    var c = G.pageItems[0].geometricBounds, far = 0, out = 0, n = 0;
    walk(G.pageItems, function (p) {
      var b = p.geometricBounds; n++;
      var d = Math.max(c[0] - b[0], b[2] - c[2], b[1] - c[1], c[3] - b[3]);
      if (d > far) far = d;
      if (b[2] < c[0] || b[0] > c[2] || b[3] > c[1] || b[1] < c[3]) out++;
    });
    res.push(Math.round(far / MM * 10) + "mm/" + out + "개");
  }
  LOG.push(KEYS[j] + " : " + res.join(" · "));
  doc.close(SaveOptions.DONOTSAVECHANGES);
}
var f = new File("C:/jjb/t_hidden.txt"); f.encoding = "UTF-8"; f.open("w"); f.write(LOG.join("\n")); f.close();

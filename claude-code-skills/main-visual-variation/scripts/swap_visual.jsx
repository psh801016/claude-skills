// 예전 바레이션 파일 안에서 메인비주얼 요소만 새 메인 조각으로 바꿔 끼운다 (판 배치·사진·문구는 그대로).
// 환황해 포럼 2026 첫 실전 (ASURA님 2026-10-27 "2·3번을 베리에이션 해주는데 메인 새로 나온걸로 바꿔줘").
// 입력: C:/mvv/hw/main.ai (새 메인 사본), CFG = { files:[...], photozone8m:{file, ab:"포토존", w:790} } — 전부 C:/mvv/hw 사본만 열고 저장
// 찾는 규칙 (예전 파일 실측):
//   소용돌이 = 불투명도 < 100, 자식 2개, 첫 자식 = 묶음 1개 → 그 안 묶음 19개(지도 조각)  → 새 원(붓터치+지도)을 같은 중심·높이·불투명도로
//   제목     = 자식 2개: [글자 묶음('제11회'+'Pan-Yellow Sea Forum')] + [복합 패스(붓글씨)]      → 새 제목 묶음을 같은 폭·중심으로
//   슬로건   = '함께 여는 대전환 시대' 글상자의 부모 묶음 (안에 '하는 환황해,' 포함)               → 새 슬로건을 같은 폭·중심으로
// 새 메인 조각 순번(probe 2026-10-27, 레이어1): [0]슬로건 [2]제목(안 [1]제11회·Pan [2]붓글씨) [3]~[13] 붓터치 원 [14] 가운데 지도
#target illustrator
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, LOG = [];
function log(s) { LOG.push(s); }
function f1(v) { return Math.round(v * 10) / 10; }
function center(b) { return [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2]; }
function fit(it, tb, by) {   // tb 와 같은 중심, by = "h"(높이) | "w"(폭) | "in"(둘 다 안에 들어가게)
  var b = it.geometricBounds, sw = (tb[2] - tb[0]) / (b[2] - b[0]), sh = (tb[1] - tb[3]) / (b[1] - b[3]);
  var s = by == "w" ? sw : by == "h" ? sh : Math.min(sw, sh);
  it.resize(s * 100, s * 100, true, true, true, true, s * 100, Transformation.CENTER);
  b = it.geometricBounds; var c0 = center(b), c1 = center(tb);
  it.translate(c1[0] - c0[0], c1[1] - c0[1]);
}
function allGroups(d) { var a = []; for (var i = 0; i < d.groupItems.length; i++) a.push(d.groupItems[i]); return a; }
function isSwirl(g) {
  if (g.opacity >= 100 || g.pageItems.length != 2) return false;
  var c = g.pageItems[0];
  // 첫 자식 묶음의 첫 조각이 지도(조각 19개) — 지도 옆에 조각이 더 붙은 변형도 있다(양쪽LED2, 2026-10-27 1차에서 빠짐)
  return c.typename == "GroupItem" && c.pageItems.length >= 1 && c.pageItems[0].typename == "GroupItem" && c.pageItems[0].pageItems.length == 19;
}
// 제목 = 글자가 '제11회'·'Pan-Yellow' 뿐이고 붓글씨 복합패스가 든 작은 묶음(가로형). 큰 제목 G2(G2(T,T),C) 말고도
// 현수막 G3(P,G2(T,T),C)·데스크 G2(G1(T),C)·포토존 G2(T,G2(G1(T),C)) 이 있다 — 1차 때 큰 것만 잡아 "그대로" 반려(2026-10-27).
// 세로 제목(높이>폭)은 새 메인에 세로판이 없어 건드리지 않는다.
function leaves(g, a) {   // 묶음 안 모든 조각(재귀) — 묶음의 textFrames 등이 안쪽까지 세는지 믿지 않는다
  for (var i = 0; i < g.pageItems.length; i++) { var p = g.pageItems[i]; if (p.typename == "GroupItem") leaves(p, a); else a.push(p); }
  return a;
}
function isTitle(g) {
  if (g.clipped || g.pageItems.length > 3) return false;
  var L = leaves(g, []), has = false, cp = false;
  if (L.length > 8) return false;
  for (var i = 0; i < L.length; i++) {
    if (L[i].typename == "CompoundPathItem") { cp = true; continue; }
    if (L[i].typename != "TextFrame") continue;
    var s = L[i].contents;
    if (s.indexOf("제11회") >= 0) has = true; else if (s.indexOf("Pan-Yellow") < 0) return false;
  }
  if (!cp) return false;
  var b = g.geometricBounds;
  return has && (b[2] - b[0]) > (b[1] - b[3]);
}
function outerTitles(list) {   // 바깥 묶음만 (안쪽 묶음도 isTitle 이면 같이 걸린다)
  var a = [];
  for (var i = 0; i < list.length; i++) { var p = list[i].parent; if (!(p.typename == "GroupItem" && isTitle(p))) a.push(list[i]); }
  return a;
}
function sloganGroups(d) {
  var a = [];
  for (var i = 0; i < d.textFrames.length; i++) {
    var t = d.textFrames[i];
    if (t.contents.replace(/\s+$/, "") != "함께 여는 대전환 시대") continue;
    var p = t.parent;
    if (p.typename != "GroupItem") continue;
    var ok = false;
    for (var k = 0; k < p.textFrames.length; k++) if (p.textFrames[k].contents.indexOf("하는 환황해") >= 0) ok = true;
    if (ok) a.push(p);
  }
  return a;
}
// 소용돌이: 예전 묶음 경계는 판 밖까지 퍼져 있어 그 높이에 맞추면 새 원이 판 밖으로 커진다(1차 반려, 2026-10-27).
// 예전 지도 조각(첫 자식)의 높이·중심에 새 원의 지도 조각(첫 자식 = 새 메인 [1,3])을 맞춘다.
function replaceSwirl(src, old) {
  var d = old.layer.parent;
  var c = src.duplicate(d.layers[0], ElementPlacement.PLACEATBEGINNING);
  var ob = old.pageItems[0].pageItems[0].geometricBounds, nb = c.pageItems[0].geometricBounds;   // 예전 지도 조각 ↔ 새 지도 조각
  var s = (ob[1] - ob[3]) / (nb[1] - nb[3]);
  c.resize(s * 100, s * 100, true, true, true, true, s * 100, Transformation.CENTER);
  nb = c.pageItems[0].geometricBounds; var c0 = center(nb), c1 = center(ob);
  c.translate(c1[0] - c0[0], c1[1] - c0[1]);
  // 예전 원은 10~30% 로 흐려 바뀐 게 안 보였다 — "원도 메인처럼 진하게" (2026-10-27) → CFG.swirlOpacity (없으면 예전 값)
  c.move(old, ElementPlacement.PLACEBEFORE); c.opacity = CFG.swirlOpacity || old.opacity; old.remove(); return c;
}
function aspect(b) { return (b[1] - b[3]) / (b[2] - b[0]); }
function replaceWith(src, old, by, keepOp) {
  var d = old.layer.parent;   // 문서
  while (d.typename != "Document") d = d.parent;
  var c = src.duplicate(d.layers[0], ElementPlacement.PLACEATBEGINNING);
  fit(c, old.geometricBounds, by);
  c.move(old, ElementPlacement.PLACEBEFORE);
  for (var i = old.pageItems.length - 1; i >= 0; i--) if (old.pageItems[i].typename == "PathItem") old.pageItems[i].move(c, ElementPlacement.PLACEAFTER);   // 제목 밑줄 등은 남긴다
  if (keepOp) c.opacity = old.opacity;
  old.remove();
  return c;
}

// 8m 포토존: 4m 대지(393)를 790 으로 넓힌 새 대지 — 바탕·물결 클립은 가로로 늘리고, 소용돌이·제목은 가운데로, 로고는 양끝 유지
function photozone8m(d, cfg) {
  var ai = -1;
  for (var a = 0; a < d.artboards.length; a++) if (d.artboards[a].name == cfg.ab) ai = a;
  if (ai < 0) { log("  8m: 대지 '" + cfg.ab + "' 없음"); return; }
  var r = d.artboards[ai].artboardRect, W0 = (r[2] - r[0]) / MM, H0 = (r[1] - r[3]) / MM, add = (cfg.w - W0) * MM;
  var low = 1e9; for (var q = 0; q < d.artboards.length; q++) low = Math.min(low, d.artboards[q].artboardRect[3]);
  var dy = cfg.inPlace ? 0 : (low - 150 * MM) - r[1];
  var items = [], L = d.layers[0];
  // 제자리(맨 위 '포토존' 구역)에 펼친다 — 아래로 내리면 다른 판과 겹쳤다("여기 위에 있잖아 포토존 여기다가 정리해", 2026-10-27).
  // 오른쪽 옆에 있던 두 번째 4m 사본(대지 없음)은 8m 한 장으로 대신하므로 지운다. 그 옆 날개(간격 띄운 세로판)는 남긴다.
  if (cfg.inPlace) {
    var old2 = 0;
    for (var o = L.pageItems.length - 1; o >= 0; o--) { var oc = center(L.pageItems[o].geometricBounds);
      if (oc[0] > r[2] && oc[0] < r[2] + add && oc[1] <= r[1] && oc[1] >= r[3]) { L.pageItems[o].remove(); old2++; } }
    log("  옆 4m 사본 " + old2 + "개 지움");
  }
  for (var i = 0; i < L.pageItems.length; i++) {   // 이 대지 안에 중심이 있는 맨 위 객체
    var c = center(L.pageItems[i].geometricBounds);
    if (c[0] >= r[0] && c[0] <= r[2] && c[1] <= r[1] && c[1] >= r[3]) items.push(L.pageItems[i]);
  }
  var cx = (r[0] + r[2]) / 2;
  for (var j = 0; j < items.length; j++) {
    var it = items[j].duplicate(L, ElementPlacement.PLACEATEND); it.translate(0, dy);
    if (it.typename == "GroupItem" && it.clipped) {
      for (var k = 0; k < it.pageItems.length; k++) {
        var p = it.pageItems[k], pb = p.geometricBounds;
        if (isSwirl(p)) { p.translate(add / 2, 0); continue; }
        var sx = ((pb[2] - pb[0]) + add) / (pb[2] - pb[0]) * 100;   // 바탕·클립·물결: 같은 왼쪽에서 가로로 늘림
        p.resize(sx, 100, true, true, true, true, 100, Transformation.LEFT);
      }
    } else if (it.typename == "GroupItem" && it.pageItems.length == 2 && !isTitle(it) && (it.geometricBounds[2] - it.geometricBounds[0]) > 0.6 * (r[2] - r[0])) {
      for (var m = 0; m < it.pageItems.length; m++) if (center(it.pageItems[m].geometricBounds)[0] > cx) it.pageItems[m].translate(add, 0);   // 로고 줄: 오른쪽 것만 끝으로
    } else it.translate(add / 2, 0);
  }
  // 발주는 옥타 4m 판 두 개다 — 이어진 그림 한 장을 판 폭대로 대지 두 개로 나눈다 ("포토존은 2개에 옥타로 4미터 두개라고", 2026-10-27)
  var n = cfg.split || 1, pw = (r[2] + add - r[0]) / n;
  for (var s = 0; s < n; s++) { var nab = d.artboards.add([r[0] + s * pw, r[1] + dy, r[0] + (s + 1) * pw, r[3] + dy]); nab.name = n > 1 ? cfg.ab + (s + 1) : cfg.ab; }
  for (var z = items.length - 1; z >= 0; z--) items[z].remove();
  d.artboards[ai].remove();
  log("  8m 포토존: " + f1(W0) + "x" + f1(H0) + " → " + cfg.w + "x" + f1(H0) + " (객체 " + items.length + "개)");
}

// 발주 사이즈 라벨: 대지마다 위에 '이름 / W x H mm'(1/10 시트라 x10) — "발주 사이즈 넣고 하는거 왜 안해" (2026-10-27)
// 대지 밖이라 출력에 안 나간다. 모음 대지('아트보드 1' 등)는 뺀다. CFG.labels = { rename:{ "Artboard 2":"현수막_타이틀" } }
function sizeLabels(d) {
  var L; try { L = d.layers.getByName("발주 사이즈"); L.remove(); } catch (e) {}
  L = d.layers.add(); L.name = "발주 사이즈"; LB = [];
  var f; try { f = app.textFonts.getByName("Pretendard-Regular"); } catch (e) { f = app.textFonts.getByName("MalgunGothic"); }
  var k = new CMYKColor(); k.black = 100;
  // 양식 = 판 왼쪽 위 4줄 '이름 / 마감 / WxHmm / 수량' (부산 메인무대게이트.jpg · INWEPF order_sheet 와 같음). 2줄·오른쪽은 반려(2026-10-27)
  var C = CFG.labels, rn = C.rename || {}, n = 0, LH = 12.5 * MM;
  for (var a = 0; a < d.artboards.length; a++) {
    var ab = d.artboards[a], nm = rn[ab.name] || ab.name;
    if (/^(아트보드|Artboard) \d+$/.test(nm) || (C.skip && C.skip.test(nm))) continue;   // 모음 대지·LED(발주 아님)
    var r = ab.artboardRect, W = Math.round((r[2] - r[0]) / MM) * 10, H = Math.round((r[1] - r[3]) / MM) * 10;
    var lines = [nm, (C.finish && C.finish[nm]) || C.finishDefault || "", W + "x" + H + "mm", (C.qty && C.qty[nm]) || "1ea"];
    // 좁은 판(현수막 1000)은 32pt 면 옆 라벨과 겹쳤다 — 가장 긴 줄이 판 폭 안에 들도록 줄인다(최소 18pt)
    var tf = [], mw = 0;
    for (var l = 0; l < lines.length; l++) {
      var t = L.textFrames.add(); t.contents = lines[l];
      var c = t.textRange.characterAttributes; c.textFont = f; c.size = 32; c.fillColor = k;
      tf.push(t); if (t.width > mw) mw = t.width;
    }
    var pt = Math.max(18, Math.min(32, 32 * ((r[2] - r[0]) - 3 * MM) / mw)), lh = LH * pt / 32;
    for (var l2 = 0; l2 < tf.length; l2++) { tf[l2].textRange.characterAttributes.size = pt; tf[l2].left = r[0]; tf[l2].top = r[1] + (tf.length - l2) * lh + 3 * MM; }
    LB.push(ub(tf));
    n++;
  }
  // 라벨이 구역 제목('비전월' 등 큰 글자)과 겹치면 구역 제목을 라벨 왼쪽으로 비킨다
  var mv = 0;
  for (var h = 0; h < d.textFrames.length; h++) {
    var hd = d.textFrames[h]; if (hd.layer == L || hd.textRange.characterAttributes.size < 60) continue;
    for (var b = 0; b < LB.length; b++) if (hit(hd.geometricBounds, LB[b])) { hd.translate((LB[b][0] - 8 * MM) - hd.geometricBounds[2], 0); mv++; }   // 왼쪽으로 비킨다 — 위로 올리면 윗줄 판(포토존)을 덮었다
  }
  log("  발주 사이즈 라벨 " + n + "개 (구역 제목 " + mv + "개 위로)");
}
var LB = [];
function ub(a) { var b = a[0].geometricBounds.concat(); for (var i = 1; i < a.length; i++) { var q = a[i].geometricBounds; b[0] = Math.min(b[0], q[0]); b[1] = Math.max(b[1], q[1]); b[2] = Math.max(b[2], q[2]); b[3] = Math.min(b[3], q[3]); } return b; }
function hit(a, b) { return a[0] < b[2] && a[2] > b[0] && a[3] < b[1] && a[1] > b[3]; }
function inR(it, r) { var c = center(it.geometricBounds); return c[0] >= r[0] && c[0] <= r[2] && c[1] <= r[1] && c[1] >= r[3]; }
function abRect(d, nm) { for (var a = 0; a < d.artboards.length; a++) if (d.artboards[a].name == nm) return d.artboards[a].artboardRect; return null; }
function ring(c) { var a = []; for (var i = 0; i < c.pageItems.length - 1; i++) a.push(c.pageItems[i]); return ub(a); }   // 마지막 조각 = 지도(번짐 경계가 커서 뺀다)

// 통일성 (2026-10-27 "메인비주얼 배경이 흰색 아니야? 통일성 좀 주고, 지도 색이 너무 강해 비전월 같은 건 텍스트가 묻혀")
// ⑤ 바탕 흰색: 판을 덮는 흰→크림 그라데이션 패스는 흰색(C0M0Y0K0)으로, 판을 덮는 반투명 질감 이미지는 숨긴다(사진은 100% 라 안 건드림)
// 모음 대지 = 다른 대지 2개 이상을 품은 대지 (이름이 "Artboard 2" 인 실제 판도 있어 이름으로 가리면 빠졌다)
function isSheet(d, a) { var r = d.artboards[a].artboardRect, n = 0; for (var k = 0; k < d.artboards.length; k++) { if (k == a) continue; var q = d.artboards[k].artboardRect; if (q[0] >= r[0] && q[2] <= r[2] && q[1] <= r[1] && q[3] >= r[3]) n++; } return n >= 2; }
function whiteBg(d) {
  var W = new CMYKColor(); W.cyan = W.magenta = W.yellow = W.black = 0;
  var np = 0, nr = 0;
  for (var a = 0; a < d.artboards.length; a++) {
    if (isSheet(d, a)) continue;
    var r = d.artboards[a].artboardRect, A = (r[2] - r[0]) * (r[1] - r[3]);
    var cov = function (b) { var iw = Math.min(b[2], r[2]) - Math.max(b[0], r[0]), ih = Math.min(b[1], r[1]) - Math.max(b[3], r[3]); return iw > 0 && ih > 0 ? iw * ih / A : 0; };
    for (var i = 0; i < d.pathItems.length; i++) { var p = d.pathItems[i];
      if (p.clipping || !p.filled || p.fillColor.typename != "GradientColor" || cov(p.geometricBounds) < 0.95) continue;
      var g = p.fillColor.gradient, light = true;
      for (var s = 0; s < g.gradientStops.length; s++) { var c = g.gradientStops[s].color; if (c.typename != "CMYKColor" || c.cyan > 5 || c.magenta > 8 || c.yellow > 30 || c.black > 3) light = false; }
      if (light) { p.fillColor = W; np++; } }
    for (var j = 0; j < d.rasterItems.length; j++) { var ri = d.rasterItems[j]; if (ri.opacity < 100 && cov(ri.geometricBounds) > 0.95 && !ri.hidden) { ri.hidden = true; nr++; } }
  }
  log("  바탕 흰색: 그라데이션 " + np + " · 질감 이미지 숨김 " + nr);
}
// ⑥ 글자 뒤 원은 50% — 원(고리) 영역에 글자·붓글씨 제목이 들어오면 그 원만 옅게. 안 겹치는 원은 메인처럼 100%
var SOFT = 50;   // 35% 는 너무 흐렸다 — ASURA님이 직접 만든 등록데스크의 50% 와 맞춰 통일
function isUnder(it, g) { var p = it.parent; while (p && p.typename != "Layer" && p.typename != "Document") { if (p == g) return true; p = p.parent; } return false; }
function softenBehindText(d, swirls) {
  var n = 0, abs = [];
  for (var a = 0; a < d.artboards.length; a++) if (!isSheet(d, a)) abs.push(d.artboards[a].artboardRect);
  var marks = [];
  for (var t = 0; t < d.textFrames.length; t++) if (d.textFrames[t].layer.name != "발주 사이즈" && d.textFrames[t].contents.replace(/\s/g, "").length) marks.push(d.textFrames[t]);
  for (var c = 0; c < d.compoundPathItems.length; c++) marks.push(d.compoundPathItems[c]);
  for (var w = 0; w < swirls.length; w++) {
    var g = swirls[w], rb = g.pageItems.length > 2 ? ring(g) : g.geometricBounds, hitT = false;
    for (var a2 = 0; a2 < abs.length && !hitT; a2++) { var r = abs[a2]; if (!inR(g, r) && !hit(rb, r)) continue;
      var vis = [Math.max(rb[0], r[0]), Math.min(rb[1], r[1]), Math.min(rb[2], r[2]), Math.max(rb[3], r[3])];   // 판 안에 보이는 고리 부분
      for (var m = 0; m < marks.length && !hitT; m++) { var mk = marks[m], mb = mk.geometricBounds;
        if ((mb[2] - mb[0]) * (mb[1] - mb[3]) > 0.5 * (r[2] - r[0]) * (r[1] - r[3]) || isUnder(mk, g) || !hit(mb, r)) continue;
        if (hit(mb, vis)) hitT = true; } }
    g.opacity = hitT ? SOFT : 100; if (hitT) n++;
  }
  log("  글자 뒤 원 " + SOFT + "%: " + n + "/" + swirls.length);
}

// ⑦ 판 크기 바꾸기: 예전 파일 대지가 실제 발주 치수와 다를 때(현수막_타이틀 1000x4000 → 450x2480, "이거 사이즈 450x2480 이야" 2026-10-27).
//    왼쪽 위 기준 새 대지. 판을 덮는 바탕·클립·물결은 새 판에 맞춰 늘리고, 나머지(제목·로고·원)는 폭 비율로 줄여 세로 위치는 판 높이 비율대로 다시 펼친다.
function resizeBoard(d, nm, wmm, hmm) {
  var ai = -1; for (var a = 0; a < d.artboards.length; a++) if (d.artboards[a].name == nm) ai = a;
  if (ai < 0) return;
  var r = d.artboards[ai].artboardRect, W0 = r[2] - r[0], H0 = r[1] - r[3], W1 = wmm * MM, H1 = hmm * MM, s = W1 / W0 * 100;
  var items = [];
  for (var l = 0; l < d.layers.length; l++) { var L = d.layers[l]; if (L.name == "발주 사이즈") continue;
    for (var i = 0; i < L.pageItems.length; i++) if (inR(L.pageItems[i], r)) items.push(L.pageItems[i]); }
  function place(p) {
    var b = p.geometricBounds, bw = b[2] - b[0], bh = b[1] - b[3];
    if (bw >= 0.8 * W0 && bh >= 0.5 * H0) {   // 바탕·클립·물결: 새 판에 맞춰 늘림, 판 왼쪽 위에서의 거리도 같은 비율
      var ox = (b[0] - r[0]) * W1 / W0, oy = (r[1] - b[1]) * H1 / H0;
      p.resize(W1 / W0 * 100, H1 / H0 * 100, true, true, true, true, 100, Transformation.TOPLEFT);
      b = p.geometricBounds; p.translate(r[0] + ox - b[0], (r[1] - oy) - b[1]); return;
    }
    var c = center(b), rx = (c[0] - r[0]) / W0, ry = (r[1] - c[1]) / H0;
    p.resize(s, s, true, true, true, true, s, Transformation.CENTER);
    var c2 = center(p.geometricBounds); p.translate(r[0] + rx * W1 - c2[0], (r[1] - ry * H1) - c2[1]);
  }
  for (var j = 0; j < items.length; j++) {
    var it = items[j];
    if (it.typename == "GroupItem" && it.clipped) { for (var k = 0; k < it.pageItems.length; k++) place(it.pageItems[k]); }
    else place(it);
  }
  d.artboards[ai].artboardRect = [r[0], r[1], r[0] + W1, r[1] - H1];
  log("  판 크기: " + nm + " " + Math.round(W0 / MM * 10) + "x" + Math.round(H0 / MM * 10) + " → " + wmm * 10 + "x" + hmm * 10 + "mm (조각 " + items.length + ")");
}

// 디자인 다듬기 (references/design-quality.md) — 2026-10-27 "글씨 안짤리게 그리고 좀 멋지게"
function polish(d, SWN, TIN, SLN) {
  if (CFG.resize) for (var rz in CFG.resize) resizeBoard(d, rz, CFG.resize[rz][0], CFG.resize[rz][1]);
  var P = CFG.photozone8m;
  // ① 옥타 두 판 포토존: 판 사이 프레임이 글자를 가르지 않게 — 제목은 왼판 가운데 위(머리 위), 원은 오른판 가운데
  var r1 = P && abRect(d, P.ab + "1"), r2 = P && abRect(d, P.ab + "2");
  // 2차("디자인 이게 최선이냐"): 왼판 제목·오른판 원은 휑했다 → 큰 원을 이음매 가운데에 세워 사람이 그 안에 서는 프레임으로,
  // 제목은 왼판 위·슬로건은 오른판 위(둘 다 아랫변이 바닥에서 1.8m 위 = 머리 위), 그래픽만 이음매를 건너고 글자는 안 건넌다.
  if (r1 && r2) {
    var U = [r1[0], r1[1], r2[2], r2[3]], pw = r1[2] - r1[0], H = U[1] - U[3], seam = r1[2], head = U[3] + H * (1800 / 2480);
    for (var j = 0; j < SWN.length; j++) if (inR(SWN[j], U)) {
      var c = SWN[j], rb = ring(c), s = 0.9 * H / (rb[1] - rb[3]) * 100;
      c.resize(s, s, true, true, true, true, s, Transformation.CENTER);
      rb = ring(c); c.translate(seam - (rb[0] + rb[2]) / 2, (U[3] + 0.02 * H) - rb[3]);
    }
    var RB = null; for (var j2 = 0; j2 < SWN.length; j2++) if (inR(SWN[j2], U)) RB = ring(SWN[j2]);
    var mg = 0.06 * H, topY = U[1] - mg, maxH = topY - head;   // 글자 높이 한도: 위 여백 ~ 머리선
    for (var i = 0; i < TIN.length; i++) if (inR(TIN[i], U)) {
      var t = TIN[i], b = t.geometricBounds, room = (RB ? RB[0] : seam) - 0.04 * pw - (r1[0] + 0.16 * pw);
      var st = Math.min(maxH / (b[1] - b[3]), room / (b[2] - b[0])) * 100;
      t.resize(st, st, true, true, true, true, st, Transformation.CENTER);
      b = t.geometricBounds; t.translate((r1[0] + 0.16 * pw + (RB ? RB[0] : seam) - 0.04 * pw) / 2 - (b[0] + b[2]) / 2, topY - b[1]);
    }
    var sg = NEWS.duplicate(TIN.length ? TIN[0].parent : d.layers[0], ElementPlacement.PLACEATBEGINNING), sb = sg.geometricBounds;
    var room2 = (r2[2] - 0.16 * pw) - ((RB ? RB[2] : seam) + 0.04 * pw), ss = Math.min(0.8 * maxH / (sb[1] - sb[3]), room2 / (sb[2] - sb[0])) * 100;
    sg.resize(ss, ss, true, true, true, true, ss, Transformation.CENTER);
    sb = sg.geometricBounds; sg.translate(((RB ? RB[2] : seam) + 0.04 * pw + r2[2] - 0.16 * pw) / 2 - (sb[0] + sb[2]) / 2, (topY - 0.03 * H) - sb[1]);
    log("  포토존 디자인: 원 이음매 가운데(높이 90%), 제목 " + P.ab + "1 위, 슬로건 " + P.ab + "2 위");
  }
  // ② 글자 밑 진한 원 비키기: 원을 글자 덩어리 왼쪽으로 민다. 판 왼끝을 넘어야 비켜지면 그 자리에서 40% 로
  var CT = CFG.clearText || {};
  for (var nm in CT) {
    var r = abRect(d, nm); if (!r) continue;
    var tx = []; for (var a = 0; a < TIN.length; a++) if (inR(TIN[a], r)) tx.push(TIN[a]);
    for (var a2 = 0; a2 < SLN.length; a2++) if (inR(SLN[a2], r)) tx.push(SLN[a2]);
    if (!tx.length) for (var a3 = 0; a3 < d.textFrames.length; a3++) if (inR(d.textFrames[a3], r)) tx.push(d.textFrames[a3]);   // 바꾸지 않은 문구(양쪽LED1 슬로건 등)
    log("  " + nm + ": 글자 " + tx.length + "개"); if (!tx.length) continue;
    var TB = ub(tx), W = r[2] - r[0];
    for (var k2 = 0; k2 < SWN.length; k2++) if (inR(SWN[k2], r)) {
      var rb2 = ring(SWN[k2]), dx = (TB[0] - 0.03 * W) - rb2[2], cx = (rb2[0] + rb2[2]) / 2 + dx;
      if (cx >= r[0]) { SWN[k2].translate(dx, 0); log("  " + nm + ": 원을 글자 왼쪽으로"); }
      else { SWN[k2].translate(r[0] - (rb2[0] + rb2[2]) / 2, 0); log("  " + nm + ": 원 왼끝"); }
    }
  }
  // ④ 바탕 밖으로 튀어나온 원은 클리핑 마스크로 가둔다 — 대지 없는 6m 띠에서 원이 띠 위아래로 삐져나왔다(2026-10-27 "클리핑 마스크를 하던가").
  //    이미 클립 안에 있으면 둔다. 바탕 = 같은 묶음 안에서 원 중심을 품는 가장 작은 닫힌 패스/클립 묶음(원 고리 면적의 30% 이상)
  var nc = 0;
  for (var w = 0; w < SWN.length; w++) {
    var c2 = SWN[w], an = c2.parent, inClip = false;
    while (an && an.typename == "GroupItem") { if (an.clipped) inClip = true; an = an.parent; }
    if (inClip) continue;
    var rr = ring(c2), cc = [(rr[0] + rr[2]) / 2, (rr[1] + rr[3]) / 2], ra2 = (rr[2] - rr[0]) * (rr[1] - rr[3]), best = null, bestA = 1e20;
    var sib = c2.parent.pageItems;
    for (var v = 0; v < sib.length; v++) { var hs = sib[v]; if (hs == c2) continue;
      var shape = null;
      if (hs.typename == "PathItem" && hs.closed) shape = hs;
      else if (hs.typename == "GroupItem" && hs.clipped) for (var u = 0; u < hs.pathItems.length; u++) if (hs.pathItems[u].clipping) { shape = hs.pathItems[u]; break; }
      if (!shape) continue;
      var hb = shape.geometricBounds, ha = (hb[2] - hb[0]) * (hb[1] - hb[3]);
      if (cc[0] < hb[0] || cc[0] > hb[2] || cc[1] > hb[1] || cc[1] < hb[3] || ha < 0.3 * ra2) continue;
      if (rr[0] >= hb[0] && rr[2] <= hb[2] && rr[1] <= hb[1] && rr[3] >= hb[3]) { shape = null; break; }   // 이미 안에 있다
      if (ha < bestA) { bestA = ha; best = shape; }
    }
    if (!best) continue;
    var cg = c2.parent.groupItems.add(); cg.move(c2, ElementPlacement.PLACEBEFORE);
    c2.move(cg, ElementPlacement.PLACEATEND);
    var mk = best.duplicate(cg, ElementPlacement.PLACEATBEGINNING); mk.filled = false; mk.stroked = false;
    cg.clipped = true; nc++;
  }
  if (nc) log("  튀어나온 원 클리핑 " + nc + "개");
  // ③ 판 밖으로 잘린 제목: 제목만 윗변 기준으로 줄여 아랫변을 판 안(3%)에 넣는다.
  //    카드·인물 사진까지 같이 줄이면 카드 밑에 가려 있던 사진(연단 '제40대')이 드러났다(2026-10-27 시도 → 폐기)
  for (var q = 0; q < TIN.length; q++) {
    var ab = null; for (var z = 0; z < d.artboards.length; z++) if (!/^(아트보드|Artboard) \d+$/.test(d.artboards[z].name) && inR(TIN[q], d.artboards[z].artboardRect)) ab = d.artboards[z].artboardRect;   // 모음 대지는 모든 판을 덮어 빼야 한다
    var tb = TIN[q].geometricBounds; if (!ab || tb[3] >= ab[3]) continue;
    var H = ab[1] - ab[3], s2 = ((tb[1] - (ab[3] + 0.03 * H)) / (tb[1] - tb[3])) * 100;
    TIN[q].resize(s2, s2, true, true, true, true, s2, Transformation.TOP);
    log("  잘린 제목 판 안으로: " + Math.round(s2) + "%");
  }
}

var main = app.open(new File("C:/mvv/hw/main.ai")), ML = main.layers[1];
// [14] = 가운데 지도(주황 원 + 한반도, 번짐 때문에 경계 238x311) — 빠뜨려 원 안이 비었다(2026-10-27 2차에서 발견)
var NEWC = ML.groupItems.add(); for (var i = 14; i >= 3; i--) ML.pageItems[i + 1].duplicate(NEWC, ElementPlacement.PLACEATBEGINNING);   // +1: 방금 만든 묶음이 맨 앞
var NEWT = ML.groupItems.add();   // 제목 묶음 = 원래 [1,2] (묶음 2개를 더 만들어 순번 +2)
var T;
T = ML.pageItems[4]; T.pageItems[2].duplicate(NEWT, ElementPlacement.PLACEATEND); T.pageItems[1].duplicate(NEWT, ElementPlacement.PLACEATBEGINNING);
var NEWS = ML.pageItems[2];   // 슬로건 = 원래 [1,0] (+2)
log("새 원 " + f1((NEWC.geometricBounds[2] - NEWC.geometricBounds[0]) / MM) + "x" + f1((NEWC.geometricBounds[1] - NEWC.geometricBounds[3]) / MM) + " / 제목 " + NEWT.pageItems.length + " / 슬로건 '" + NEWS.textFrames[0].contents + "'");

for (var f = 0; f < CFG.files.length; f++) {
  var fname = CFG.files[f], d = app.open(new File("C:/mvv/hw/" + fname + ".ai"));   // "name" 은 ExtendScript 전역과 겹쳐 경로가 깨졌다 (2026-10-27)
  for (var l = 0; l < d.layers.length; l++) { d.layers[l].locked = false; d.layers[l].visible = true; }
  log("== " + fname);
  if (CFG.photozone8m && CFG.photozone8m.file == fname) photozone8m(d, CFG.photozone8m);
  if (CFG.labelOnly && CFG.labelOnly[fname]) {   // 이미 새 원(조각 12개 묶음, 50%)이 든 파일 — 진하기만 올리고 라벨
    // ASURA님이 만든 파일의 원 진하기는 그대로 둔다(무대백월 100% 는 "너무 쌔다, 왼쪽(50%)이 좋은데" 2026-10-27)
    var dk = 0, SWO = [];
    for (var q = 0; q < d.groupItems.length; q++) { var gq = d.groupItems[q]; if (gq.opacity < 100 && gq.pageItems.length == 12) { SWO.push(gq); dk++; } }
    whiteBg(d);
    log("  (이미 새 메인 — 원 진하게 " + dk + " · 라벨만)"); sizeLabels(d); saveOut(d, fname); continue;
  }
  var g = allGroups(d), sw = [], ti = [];
  for (var k = 0; k < g.length; k++) { if (isSwirl(g[k])) sw.push(g[k]); else if (isTitle(g[k])) ti.push(g[k]); }
  var sl = sloganGroups(d);
  var SWN = [], TIN = [], SLN = [];
  for (var a1 = 0; a1 < sw.length; a1++) SWN.push(replaceSwirl(NEWC, sw[a1]));
  ti = outerTitles(ti);
  for (var a2 = 0; a2 < ti.length; a2++) TIN.push(replaceWith(NEWT, ti[a2], "in", false));
  // 슬로건은 모양(두 줄 비율)이 새 것과 비슷할 때만 — 한 줄 슬로건 자리에 두 줄을 넣으면 제목과 겹쳤다(1차 반려, 데스크·비전월2)
  var ns = aspect(NEWS.geometricBounds), done = 0;
  for (var a3 = 0; a3 < sl.length; a3++) { var ra = aspect(sl[a3].geometricBounds) / ns; if (ra > 0.6 && ra < 1.6) { SLN.push(replaceWith(NEWS, sl[a3], "w", false)); done++; } }
  log("  소용돌이 " + sw.length + " · 제목 " + ti.length + " · 슬로건 " + done + "/" + sl.length + " 교체 (한 줄 슬로건은 그대로)");
  polish(d, SWN, TIN, SLN);
  whiteBg(d); softenBehindText(d, SWN);
  if (CFG.labels) sizeLabels(d);
  saveOut(d, fname);
}
function saveOut(d, fname) {
  var names = []; for (var n = 0; n < d.artboards.length; n++) names.push(d.artboards[n].name);
  var nf = new File("C:/mvv/hw/" + fname + "_artboards.txt"); nf.encoding = "UTF-8"; nf.open("w"); nf.write(names.join("\n")); nf.close();
  var so = new IllustratorSaveOptions(); so.pdfCompatible = true; so.embedLinkedFiles = true; so.compressed = true;
  d.saveAs(new File("C:/mvv/hw/out_" + fname + ".ai"), so); d.close(SaveOptions.DONOTSAVECHANGES);
}
main.close(SaveOptions.DONOTSAVECHANGES);
var lf = new File("C:/mvv/hw/swap_log.txt"); lf.encoding = "UTF-8"; lf.open("w"); lf.write(LOG.join("\n")); lf.close();

// 메인비주얼 → 사이즈 바레이션 빌더. jobs.js 의 JOBS 를 읽어 항목마다 1/10 축척 발주 원본 시트(CMYK)를 C:/mvv/out/<key>.ai 로 만든다.
// 원본(C:/mvv/src/*.ai = 디자인팀 메인비주얼의 '사본')은 읽기만 한다 — 조각을 복제해 오고 저장 없이 닫는다.
// 디자인팀 폴더(02 메인비주얼)는 절대 열지 않는다. 사본은 run.ps1 이 C:/mvv/src 로 복사한다.
#target illustrator
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, SHEET = 0.1, U = SHEET * MM, EPS = 0.3 * MM;
var LOG = [];
function log(s) { LOG.push(s); }
function f1(v) { return (Math.round(v * 10) / 10).toString(); }
function cmyk(c, m, y, k) { var o = new CMYKColor(); o.cyan = c; o.magenta = m; o.yellow = y; o.black = k; return o; }
function unlockAll(layer) { try { layer.locked = false; layer.visible = true; } catch (e) {} for (var i = 0; i < layer.layers.length; i++) unlockAll(layer.layers[i]); }
function inside(b, L, T, R, B) { return b[0] >= L - EPS && b[2] <= R + EPS && b[1] <= T + EPS && b[3] >= B - EPS; }
function overlaps(b, L, T, R, B) { return b[0] < R - EPS && b[2] > L + EPS && b[1] > B + EPS && b[3] < T - EPS; }
function clipPathOf(g) {
  for (var k = 0; k < g.pageItems.length; k++) {
    var q = g.pageItems[k];
    if (q.typename == "PathItem" && q.clipping) return q;
    if (q.typename == "CompoundPathItem" && q.pathItems.length && q.pathItems[0].clipping) return q;
  }
  return null;
}

// ── 조각 고르기: 영역(원본 대지 기준 mm) 안에 '통째로' 드는 객체. 걸치는 평범한 묶음은 안으로 들어가 본다.
// 메인비주얼은 보통 배경·별자리·인물·꽃이 한 묶음(대지보다 큼)이라 안으로 들어가야 조각이 갈라진다. (2026-10-23 충남 실측: 레이어1 #1 263x328mm 묶음)
function pickInside(items, L, T, R, B, out) {
  for (var i = 0; i < items.length; i++) {
    var p = items[i];
    if (p.hidden) continue;
    if (p.typename == "PathItem" && (p.guides || p.clipping)) continue;
    var b = p.geometricBounds;
    if (inside(b, L, T, R, B)) { out.push(p); continue; }
    if (p.typename != "GroupItem" || !overlaps(b, L, T, R, B)) continue;
    if (p.clipped) { var cp = clipPathOf(p); if (!cp || !inside([L, T, R, B], cp.geometricBounds[0], cp.geometricBounds[1], cp.geometricBounds[2], cp.geometricBounds[3])) continue; }
    if (p.opacity != 100 || p.blendingMode != BlendModes.NORMAL) continue;
    pickInside(p.pageItems, L, T, R, B, out);
  }
}
function pickLayers(layers, L, T, R, B, out) {
  for (var i = 0; i < layers.length; i++) { if (!layers[i].visible) continue; pickInside(layers[i].pageItems, L, T, R, B, out); pickLayers(layers[i].layers, L, T, R, B, out); }
}

var SRC = {};   // 열어 둔 원본 사본 (이름 → 문서)
function srcDoc(name) {
  if (SRC[name]) return SRC[name];
  var d = app.open(new File("C:/mvv/src/" + name + ".ai"));
  for (var l = 0; l < d.layers.length; l++) unlockAll(d.layers[l]);
  // RGB 원본(3D map 백월 등)은 사본을 CMYK 문서로 바꾼 뒤 조각을 가져온다 — 그대로 복제하면 사진이 RGB 로 남았다 (2026-10-23 entry 사진 5장).
  // 사본이라 저장하지 않는다. 변환은 일러 기본 프로파일 기준이니 보고에 적는다(족자봉 스킬 '색 맞춤' 참고).
  if (d.documentColorSpace == DocumentColorSpace.RGB) { d.activate(); app.executeMenuCommand("doc-color-cmyk"); log("    " + name + " 사본 RGB → CMYK 문서 변환"); }
  SRC[name] = d;
  return d;
}
function closeSrc() { for (var k in SRC) { try { SRC[k].close(SaveOptions.DONOTSAVECHANGES); } catch (e) {} } SRC = {}; }

// 조각 하나를 출력 문서 레이어에 복제해 묶음으로 돌려준다. 원본 문서에는 임시 묶음을 만들었다가 지운다(저장 안 함).
// pc = PIECES[name] = { src:"main", region:[x,y,w,h] (원본 대지 mm), scale: 원본 1mm = 실물 scale mm (기본 1; 1/10 시트 원본이면 10), back:true 면 맨 뒤 하나만 }
function fetchPiece(name, outLayer) {
  var pc = PIECES[name];
  if (!pc) throw new Error("PIECES 에 없음: " + name);
  var d = srcDoc(pc.src || "main");
  d.activate();
  var sel = [];
  if (pc.items) {
    // items = [[레이어, 순번, 순번…], …] — probe.txt 순서(0 = 맨 위). 클리핑 묶음 안 조각도 잘리지 않고 통째로 집힌다.
    // 영역으로 고르면 대지 끝에 걸친 인물이 조각나서 이걸 기본으로 쓴다 (2026-10-23 충남 메인 실측)
    for (var t = 0; t < pc.items.length; t++) {
      var path = pc.items[t], it = d.layers[path[0]];
      for (var u = 1; u < path.length; u++) it = it.pageItems[path[u]];
      sel.push(it);
    }
  } else {
    var ab = d.artboards[(pc.ab || 1) - 1].artboardRect, g = pc.region;
    var L = ab[0] + g[0] * MM, T = ab[1] - g[1] * MM, R = L + g[2] * MM, B = T - g[3] * MM;
    pickLayers(d.layers, L, T, R, B, sel);
  }
  if (pc.minW) { var keep = []; for (var k = 0; k < sel.length; k++) { var kb = sel[k].geometricBounds; if ((kb[2] - kb[0]) / MM >= pc.minW) keep.push(sel[k]); } sel = keep; }
  if (pc.back) sel = [sel[sel.length - 1]];
  if (!sel.length) throw new Error("조각 '" + name + "' 에 고를 것이 없음");
  var G = d.layers[0].groupItems.add();
  for (var i = 0; i < sel.length; i++) { try { sel[i].locked = false; } catch (e) {} sel[i].duplicate(G, ElementPlacement.PLACEATEND); }
  var D = G.duplicate(outLayer, ElementPlacement.PLACEATBEGINNING);
  G.remove();
  D.name = name;
  var b = D.geometricBounds;
  log("    조각 " + name + " n=" + sel.length + " " + f1((b[2] - b[0]) / MM) + "x" + f1((b[1] - b[3]) / MM) + "mm(원본)");
  return { item: D, k: (pc.scale || 1) };
}

// ── 배치: 실물 mm 좌표(보이는 면 좌상단 = 0,0, 아래로 +) → 시트(1/10) 위치. 크기는 w 또는 h 하나로 비율 유지, 둘 다 주면 늘림(배경).
// step = { piece | pieces:[...], mode:"row"|"col", gap, at:[x,y], anchor:"tl|tc|tr|cl|c|cr|bl|bc|br", cx, cy, w, h, op, rot, flip }
// 그림 칸: photos.py 가 만든 CMYK TIFF 를 실물 mm 자리·크기에 넣는다. step = { img:"C:/mvv/src/photos/x.tif", at:[x,y], w, h }
function placeImg(lay, step, ox, oy) {
  var pi = lay.placedItems.add();
  pi.file = new File(step.img);
  pi.embed();
  var it = lay.pageItems[0], b = it.geometricBounds;
  it.resize(step.w * U / (b[2] - b[0]) * 100, step.h * U / (b[1] - b[3]) * 100, true, true, true, true, 100, Transformation.TOPLEFT);
  b = it.geometricBounds;
  it.translate(ox + step.at[0] * U - b[0], oy - step.at[1] * U - b[1]);
  it.name = step.name || step.img.replace(/^.*\//, "");
  // LED 픽셀 줄무늬 같은 효과 레이어: blend = "OVERLAY" 등 BlendModes 이름, op = 불투명도 (참고: 지식재산대전 무대LED.ai = Overlay 50%)
  if (step.blend) it.blendingMode = BlendModes[step.blend];
  if (step.op != undefined) it.opacity = step.op;
  return it;
}

function placeStep(doc, lay, step, ox, oy, face) {
  if (step.img) return placeImg(lay, step, ox, oy);
  var names = step.pieces || [step.piece], parts = [], i;
  for (i = 0; i < names.length; i++) parts.push(fetchPiece(names[i], lay));
  doc.activate();
  var G;
  if (parts.length == 1) G = parts[0].item;
  else {
    // 줄(row)·단(col)로 붙인다: 각 조각을 같은 축척으로 맞춘 뒤 gap(원본 mm — 묶음 전체가 함께 커지므로) 만큼 띄워 나란히
    G = lay.groupItems.add();
    var cur = 0, gap = (step.gap || 0) * MM;
    for (i = 0; i < parts.length; i++) {
      var it = parts[i].item, b = it.geometricBounds, sc = parts[i].k / parts[0].k * 100;
      it.resize(sc, sc, true, true, true, true, sc, Transformation.TOPLEFT);
      b = it.geometricBounds;
      if (step.mode == "col") { it.translate(-b[0], -b[1] - cur); cur += (b[1] - b[3]) + gap; }
      else { it.translate(-b[0] + cur, -b[1]); cur += (b[2] - b[0]) + gap; }
      it.move(G, ElementPlacement.PLACEATEND);
    }
    if (step.mode == "row" && step.align != "top") {   // 줄은 세로 가운데 맞춤
      var hb = G.geometricBounds, mid = (hb[1] + hb[3]) / 2;
      for (i = 0; i < G.pageItems.length; i++) { var pb = G.pageItems[i].geometricBounds; G.pageItems[i].translate(0, mid - (pb[1] + pb[3]) / 2); }
    }
  }
  var k = parts[0].k;                       // 원본 1mm = 실물 k mm
  // 글자 바꾸기: 원본 글상자의 글꼴·색을 그대로 쓰고 내용만 바꾼다 (text, 줄바꿈은 \n). ptScale = 글자 크기 배율
  if (step.text != undefined) {
    var tf = G.typename == "TextFrame" ? G : G.textFrames[0];
    var sz = tf.textRange.characterAttributes.size;
    tf.contents = step.text.replace(/\n/g, "\r");
    // 글자를 줄이면 줄 간격도 자동으로 — 원본 큰 글자의 줄 간격이 남아 둘째 줄이 날짜에 붙었다 (2026-10-23 입구백월 v4 1차)
    if (step.ptScale) { tf.textRange.characterAttributes.size = sz * step.ptScale; tf.textRange.characterAttributes.autoLeading = true; }
  }
  if (step.flip) G.resize(-100, 100, true, true, true, true, 100, Transformation.CENTER);
  if (step.rot) G.rotate(step.rot, true, true, true, true, Transformation.CENTER);
  var b0 = G.geometricBounds, w0 = (b0[2] - b0[0]) / MM * k, h0 = (b0[1] - b0[3]) / MM * k;   // 지금 실물 크기
  var sx, sy;
  if (step.w && step.h) { sx = step.w / w0; sy = step.h / h0; }
  else if (step.w) { sx = sy = step.w / w0; }
  else if (step.h) { sx = sy = step.h / h0; }
  else { sx = sy = 1; }
  sx = sx * k * SHEET * 100; sy = sy * k * SHEET * 100;   // 원본 단위 → 시트(1/10 실물) 단위
  G.resize(sx, sy, true, true, true, true, (sx + sy) / 2, Transformation.TOPLEFT);
  var b = G.geometricBounds, w = b[2] - b[0], h = b[1] - b[3];
  if (step.maxW && w > step.maxW * U) {     // 칸 폭을 넘는 글줄은 같은 비율로 줄인다
    var f = step.maxW * U / w * 100;
    G.resize(f, f, true, true, true, true, f, Transformation.TOPLEFT);
    b = G.geometricBounds; w = b[2] - b[0]; h = b[1] - b[3];
  }
  var x, y;
  if (step.at) { x = step.at[0]; y = step.at[1]; } else { x = step.cx; y = step.cy; }
  var a = step.anchor || (step.at ? "tl" : "c");
  var ax = a.charAt(1) == "l" ? 0 : (a.charAt(1) == "r" ? 1 : 0.5), ay = a.charAt(0) == "t" ? 0 : (a.charAt(0) == "b" ? 1 : 0.5);
  if (a == "c") { ax = 0.5; ay = 0.5; }
  var tx = ox + x * U - ax * w, ty = oy - y * U + ay * h;
  G.translate(tx - b[0], ty - b[1]);
  if (step.op != undefined) G.opacity = step.op;
  G.name = (step.name || names.join("+"));
  log("    배치 " + G.name + " → " + f1(w / U) + "x" + f1(h / U) + "mm at " + f1((b[0] + (tx - b[0]) - ox) / U) + "," + f1((oy - (b[1] + (ty - b[1]))) / U) + (step.op != undefined ? " op" + step.op : "") + (step.rot ? " rot" + step.rot : ""));
  return G;
}

// 라벨은 줄마다 글상자 하나 — 한 글상자 안 문단 범위를 고치면 좁은 판(측면 700)에서 'illegal text range' 로 멈췄다 (2026-10-23 center_wing·entry_wing)
function textLine(lay, font, s, size, color) {
  var tf = lay.textFrames.add();
  tf.contents = s;
  var ca = tf.textRange.characterAttributes;
  ca.size = size; ca.textFont = font; ca.fillColor = color;
  return tf;
}
// 라벨 3줄은 판 왼쪽 끝에 맞추고 크기 차이를 줄인다 — 60pt/16pt 가운데 정렬은 둘째·셋째 줄이 안 읽혔다 (ASURA님 2026-10-23 "텍스트 이상하잖아 보기 불편하고")
// 1줄 재질 36pt(현수막 빨강 / 패트·켈지 파랑) · 2줄 치수·수량 30pt 검정 · 3줄 위치·보이는 면 20pt 회색
var LABEL_SIZES = [36, 30, 20];
function addLabel(lay, font, lines, left, bottomY) {
  var col = cmyk(0, 0, 0, 100);
  if (lines[0].indexOf("현수막") >= 0) col = cmyk(0, 100, 100, 0);
  else if (lines[0].indexOf("페트") >= 0 || lines[0].indexOf("패트") >= 0 || lines[0].indexOf("켈지") >= 0) col = cmyk(100, 60, 0, 0);
  var colors = [col, cmyk(0, 0, 0, 100), cmyk(0, 0, 0, 70)], y = bottomY, tf = null;
  for (var i = lines.length - 1; i >= 0; i--) {
    tf = textLine(lay, font, lines[i], LABEL_SIZES[i], colors[i]);
    tf.left = left; tf.top = y + tf.height; y += tf.height + 1.5 * MM;
  }
  return tf;
}
function comma(n) { var s = String(Math.round(n)); return s.replace(/\B(?=(\d{3})+(?!\d))/g, ","); }
function pickFont() {
  var names = ["Pretendard-Bold", "Pretendard-SemiBold", "MalgunGothicBold", "MalgunGothic-Bold", "MalgunGothic"];
  for (var i = 0; i < names.length; i++) { try { return app.textFonts.getByName(names[i]); } catch (e) {} }
  return app.textFonts[0];
}

// job = { key, title, W, H (발주 치수 mm), bleed (보이는 면 바깥 여유, 불칼질 100), mat, pos, qty, shape:"circle", sheet:false(라벨·시트 없이 = 3D 텍스처용), layout:[step...] }
function build(job) {
  log("== " + job.key + " " + job.title + " " + job.W + "x" + job.H);
  var pre = new DocumentPreset();
  // LED 같은 화면물은 RGB 문서 (job.rgb) — 발주물은 CMYK
  pre.colorMode = job.rgb ? DocumentColorSpace.RGB : DocumentColorSpace.CMYK; pre.units = RulerUnits.Millimeters;
  pre.width = 1400 * MM; pre.height = 900 * MM;
  var doc = app.documents.addDocument("", pre);
  // 새 문서 기본 래스터효과 72ppi 면 1/10 시트의 글로우가 실물 7ppi 로 굳어 _출(pymupdf 렌더)·맵 PNG 에 그대로 간다. 300 과 1500 은 결과가 같았다 (2026-10-27 LED 원 둘레 실측)
  doc.rasterEffectSettings.resolution = 300;
  doc.saveAs(new File("C:/mvv/out/" + job.key + ".ai"));   // 경로를 먼저 줘야 오류 때 내 문서만 골라 닫을 수 있다
  var lay = doc.layers[0], font = pickFont();
  var M = job.sheet === false ? 0 : 40 * MM, LABEL = job.sheet === false ? 0 : 50 * MM, TITLE = job.sheet === false ? 0 : 30 * MM;
  var a0 = doc.artboards[0].artboardRect;
  var px = a0[0] + M, py = a0[1] - M - TITLE - LABEL;
  var w = job.W * U, h = job.H * U, bleed = job.bleed || 0;
  var ox = px + bleed * U, oy = py - bleed * U;             // 보이는 면 원점
  var face = { W: job.W - 2 * bleed, H: job.H - 2 * bleed };

  var PG = lay.groupItems.add(); PG.name = job.key;
  var base = lay.pathItems.rectangle(py, px, w, h);           // 흰판: 판 크기 — 바탕 없는 판 금지
  base.name = "흰판"; base.stroked = false; base.filled = true; base.fillColor = cmyk(0, 0, 0, 0);
  base.move(PG, ElementPlacement.PLACEATEND);
  for (var s = 0; s < job.layout.length; s++) {
    var st = job.layout[s];
    // 다각형 (간판의 흰 이름 판·테두리 꺾쇠 등): { poly:[[x,y]…] (보이는 면 실물 mm), open:true(열린 선), fill:[c,m,y,k], stroke:[c,m,y,k], sw(실물 mm) }
    // 모양 원본: 부산 2026 메인무대게이트.ai 간판 흰 판 = 모서리 45° 따기 + 위 가운데 홈 (INWEPF 2026 부스 간판. 둥근 판은 반려됨)
    if (st.poly) {
      var pts = [];
      for (var pi = 0; pi < st.poly.length; pi++) pts.push([ox + st.poly[pi][0] * U, oy - st.poly[pi][1] * U]);
      var pp = lay.pathItems.add(); pp.setEntirePath(pts); pp.closed = !st.open;
      pp.filled = !!st.fill; if (st.fill) pp.fillColor = cmyk(st.fill[0], st.fill[1], st.fill[2], st.fill[3]);
      pp.stroked = !!st.stroke; if (st.stroke) { pp.strokeColor = cmyk(st.stroke[0], st.stroke[1], st.stroke[2], st.stroke[3]); pp.strokeWidth = st.sw * U; }
      pp.name = st.name || "다각형";
      pp.move(PG, ElementPlacement.PLACEATBEGINNING); continue;
    }
    // 새 글자 (메인에 없는 문구 — 'COMPANY NAME' 자리 등): { newText, font:[글꼴 후보…], color:[c,m,y,k], cx, cy, h(글상자 높이 실물 mm), maxW }
    // 살아 있는 글자로 둔다(원본은 수정용). 글꼴 후보가 없으면 시트 글꼴.
    if (st.newText != undefined) {
      var nt = lay.textFrames.add(); nt.contents = st.newText;
      var nca = nt.textRange.characterAttributes, nf = null;
      for (var fi = 0; st.font && fi < st.font.length && !nf; fi++) { try { nf = app.textFonts.getByName(st.font[fi]); } catch (e) {} }
      nca.textFont = nf || font; nca.fillColor = cmyk(st.color[0], st.color[1], st.color[2], st.color[3]); nca.size = 100;
      var nb = nt.visibleBounds, nsz = 100 * (st.h * U) / (nb[1] - nb[3]);
      if (st.maxW && (nb[2] - nb[0]) * nsz / 100 > st.maxW * U) nsz = 100 * (st.maxW * U) / (nb[2] - nb[0]);
      nca.size = nsz;
      nb = nt.visibleBounds;
      nt.translate(ox + st.cx * U - (nb[0] + nb[2]) / 2, oy - st.cy * U - (nb[1] + nb[3]) / 2);
      nt.name = st.name || st.newText;
      log("    새 글자 " + st.newText + " " + f1(nsz) + "pt 글꼴 " + (nf ? nf.name : font.name));
      nt.move(PG, ElementPlacement.PLACEATBEGINNING); continue;
    }
    if (st.fill) {   // 단색 사각형 (실물 mm, 보이는 면 기준)
      var rr = lay.pathItems.rectangle(oy - st.at[1] * U, ox + st.at[0] * U, st.w * U, st.h * U);
      rr.stroked = false; rr.filled = true; rr.fillColor = cmyk(st.fill[0], st.fill[1], st.fill[2], st.fill[3]);
      rr.move(PG, ElementPlacement.PLACEATBEGINNING); continue;
    }
    if (st.bg) { st.at = [-bleed, -bleed]; st.w = job.W; st.h = job.H; }   // 배경은 여유까지 늘려 덮는다
    var G = placeStep(doc, lay, st, ox, oy, face);
    G.move(PG, ElementPlacement.PLACEATBEGINNING);
  }
  closeSrc();
  doc.activate();
  var outer = job.shape == "circle" ? lay.pathItems.ellipse(py, px, w, h) : lay.pathItems.rectangle(py, px, w, h);
  outer.move(PG, ElementPlacement.PLACEATBEGINNING);
  PG.clipped = true;
  // 여유 표시 = 보이는 면 네 모서리에 안쪽으로 꺾인 ㄱ·ㄴ (점선 사각형 아님). 사내 관행: 부산 2026 무대목공백월.ai —
  // 연회색 극세선, 한 변 실물 약 240mm, 출력(_출) 파일에도 남긴다 (ASURA님 2026-10-23 "모서리만 ㄱ ㄴ 이런식으로")
  // 별도 레이어 '여유 표시' — 3D 맵 PNG 를 뽑을 때 이 레이어를 끈다 (map_png.py)
  if (bleed) {
    var ML = doc.layers.add(); ML.name = "여유 표시";
    var CM = ML.groupItems.add(); CM.name = "여유 표시(모서리)";
    var leg = Math.min(240, 0.2 * Math.min(face.W, face.H)) * U, fx = ox + face.W * U, fy = oy - face.H * U;
    var corners = [[[ox + leg, oy], [ox, oy], [ox, oy - leg]], [[fx - leg, oy], [fx, oy], [fx, oy - leg]],
                   [[ox + leg, fy], [ox, fy], [ox, fy + leg]], [[fx - leg, fy], [fx, fy], [fx, fy + leg]]];
    for (var c = 0; c < 4; c++) {
      var cp = CM.pathItems.add(); cp.setEntirePath(corners[c]);
      cp.filled = false; cp.stroked = true; cp.strokeColor = cmyk(0, 0, 0, 40); cp.strokeWidth = 0.25;
    }
  }

  if (job.sheet !== false) {
    var t = lay.textFrames.add();
    t.contents = (job.event || "") + " — " + job.title;
    t.textRange.characterAttributes.size = 48; t.textRange.characterAttributes.textFont = font; t.textRange.characterAttributes.fillColor = cmyk(0, 0, 0, 100);
    t.left = px; t.top = a0[1] - M + 4 * MM;
    var l3 = job.pos;
    if (bleed) l3 += "   |   보이는 면 " + comma(face.W) + " x " + comma(face.H) + " + 사방 여유 " + bleed;
    addLabel(lay, font, [job.mat, comma(job.W) + " x " + comma(job.H) + " mm   ·   " + (job.qty || 1) + "EA", l3], px, py + 6 * MM);
    var BG = doc.layers.add(); BG.name = "시트 바탕"; BG.move(doc, ElementPlacement.PLACEATEND);
  }
  // 대지 폭 = 판·제목·라벨 중 가장 긴 것 + 여백 — 작은 판(원형 1150)에서 시트 제목이 대지 밖으로 잘렸다 (2026-10-23)
  var right = px + w;
  for (var r = 0; r < lay.textFrames.length; r++) right = Math.max(right, lay.textFrames[r].geometricBounds[2]);
  doc.artboards[0].artboardRect = [a0[0], a0[1], right + M, py - h - M];
  if (job.sheet !== false) {
    var ar = doc.artboards[0].artboardRect, gp = BG.pathItems.rectangle(ar[1], ar[0], ar[2] - ar[0], ar[1] - ar[3]);
    gp.stroked = false; gp.filled = true; gp.fillColor = cmyk(0, 0, 0, 25); gp.name = "시트 바탕"; BG.locked = true;
  }
  // 3D 맵용 대지 — 판(여유 포함) 크기 그대로, 이름 = 맵 이름. map_png.py 가 이 대지(PDF 2쪽)를 <맵 이름>.png 로 뽑는다
  // 사내 관행: 품목 대지 1개 = PNG 1장, 1/10 시트를 144ppi(일러 내보내기 200%)·투명 배경 (INWEPF 2026 map, ASURA님 2026-10-23 "map 폴더에 png로 각 해당 이름으로")
  var mapName = job.map === false ? "" : (job.map || job.file || job.key);
  if (mapName) {
    var mab = doc.artboards.add([px, py, px + w, py - h]); mab.name = mapName;
    var mf = new File("C:/mvv/out/" + job.key + ".map.txt"); mf.encoding = "UTF-8"; mf.open("w"); mf.write(mapName); mf.close();
    log("  맵 대지 " + mapName + " " + job.W + "x" + job.H);
  }
  var rgb = 0;
  for (var g = 0; g < doc.rasterItems.length; g++) if (doc.rasterItems[g].imageColorSpace == ImageColorSpace.RGB) rgb++;
  var txt = [];
  for (var q = 0; q < doc.textFrames.length; q++) txt.push(doc.textFrames[q].contents.replace(/[\r\n]+/g, " / "));
  log("  raster=" + doc.rasterItems.length + " rgb_raster=" + rgb + " text=" + doc.textFrames.length);
  log("  글자: " + txt.join(" | "));
  var so = new IllustratorSaveOptions(); so.pdfCompatible = true; so.embedLinkedFiles = true; so.compressed = true;
  doc.saveAs(new File("C:/mvv/out/" + job.key + ".ai"), so);
  doc.close(SaveOptions.DONOTSAVECHANGES);
  log("  saved C:/mvv/out/" + job.key + ".ai");
}

function closeMine() {   // 사용자가 같은 일러에서 작업 중일 수 있다 — C:/mvv 아래 문서(내가 연 것)만 닫는다
  for (var i = app.documents.length - 1; i >= 0; i--) {
    var d = app.documents[i], p = "";
    try { p = d.fullName.fsName; } catch (e) { continue; }
    if (p.toLowerCase().indexOf("c:\\mvv\\") == 0) d.close(SaveOptions.DONOTSAVECHANGES);
  }
}

var oldScale = app.preferences.getBooleanPreference("scaleLineWeight");
app.preferences.setBooleanPreference("scaleLineWeight", true);
var userDoc = null;
try { userDoc = app.activeDocument.name; } catch (e) {}
$.evalFile("C:/mvv/jsx/jobs.js");
for (var j = 0; j < JOBS.length; j++) {
  if (typeof ONLY != "undefined" && ONLY != "all" && JOBS[j].key != ONLY) continue;
  if (JOBS[j].hold && ONLY != JOBS[j].key) { log("== " + JOBS[j].key + " 보류(" + JOBS[j].hold + ")"); continue; }
  try { build(JOBS[j]); } catch (err) { log("  ERROR " + JOBS[j].key + ": " + err + " (line " + err.line + ")"); SRC = {}; closeMine(); }
}
app.preferences.setBooleanPreference("scaleLineWeight", oldScale);
if (userDoc) { try { app.documents.getByName(userDoc).activate(); } catch (e) {} }
var lf = new File("C:/mvv/build_log.txt"); lf.encoding = "UTF-8"; lf.open("a"); lf.writeln(LOG.join("\n")); lf.close();

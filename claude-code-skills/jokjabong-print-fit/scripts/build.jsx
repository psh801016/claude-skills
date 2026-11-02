// 족자봉 출력 시트 빌더 — JOBS(jobs.js) 중 ONLY 키 하나를 만든다.
// 원본은 읽기만 한다(작업 뒤 저장하지 않고 닫음). 결과는 1/10 축척 시트 1장.
#target illustrator
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72 / 25.4, SHEET = 0.1, EPS = 0.5 * MM;
var LOG = [];
function log(s) { LOG.push(s); }
function f1(v) { return (Math.round(v * 10) / 10).toString(); }

function cmyk(c, m, y, k) { var o = new CMYKColor(); o.cyan = c; o.magenta = m; o.yellow = y; o.black = k; return o; }

function unlockAll(layer) {
  try { layer.locked = false; } catch (e) {}
  for (var i = 0; i < layer.layers.length; i++) unlockAll(layer.layers[i]);
}

function overlaps(b, L, T, R, B) {
  return b[0] < R - EPS && b[2] > L + EPS && b[1] > B + EPS && b[3] < T - EPS;
}

// 레이어(하위 레이어 포함)의 최상위 객체 중 영역과 겹치는 것, 위→아래 순
// 영역에 걸친 '큰 묶음'은 통째로 가져오지 않고 안으로 들어가 영역에 닿는 것만 가져온다 — 통째로 가져오면
// 마스크 밖에 원본 전체가 숨어 들어가고, 비균등 확대 때는 그 숨은 원본이 길게 늘어난다 (2026-10-22 제이콥 띠, ASURA님 지적).
// 묶음에 투명도·합성 모드가 걸려 있거나 클리핑 묶음이면 풀면 모양이 바뀌므로 통째로 둔다.
function inside(b, L, T, R, B) { return b[0] >= L - EPS && b[2] <= R + EPS && b[1] <= T + EPS && b[3] >= B - EPS; }
function collectItems(items, L, T, R, B, out) {
  for (var i = 0; i < items.length; i++) {
    var p = items[i];
    if (p.hidden) continue;
    if (p.typename == "PathItem" && (p.guides || p.clipping)) continue;   // 마스크 경로는 묶음 안으로 들어갔을 때만 만나며, 가져오지 않는다
    if (p.typename == "CompoundPathItem" && p.pathItems.length && p.pathItems[0].clipping) continue;
    var b = p.geometricBounds;
    if (!overlaps(b, L, T, R, B)) continue;
    var plain = p.typename == "GroupItem" && p.opacity == 100 && p.blendingMode == BlendModes.NORMAL;
    if (plain && p.clipped) {   // 마스크가 판 영역을 다 덮으면 판 안에선 마스크가 하는 일이 없다 → 안으로 들어간다
      var cp = clipPathOf(p);
      plain = cp && inside([L, T, R, B], cp.geometricBounds[0], cp.geometricBounds[1], cp.geometricBounds[2], cp.geometricBounds[3]);
    }
    if (plain && !inside(b, L, T, R, B)) collectItems(p.pageItems, L, T, R, B, out);
    else out.push(p);
  }
}
function clipPathOf(g) {
  for (var k = 0; k < g.pageItems.length; k++) {
    var q = g.pageItems[k];
    if (q.typename == "PathItem" && q.clipping) return q;
    if (q.typename == "CompoundPathItem" && q.pathItems.length && q.pathItems[0].clipping) return q;
  }
  return null;
}
function collect(layer, L, T, R, B, out) {
  if (!layer.visible) return;
  collectItems(layer.pageItems, L, T, R, B, out);
  for (var j = 0; j < layer.layers.length; j++) collect(layer.layers[j], L, T, R, B, out);
}

// 프레임 크기(mm)와 같은 클리핑 그룹을 찾아 좌상단을 기준점으로 쓴다 (신화 EPS)
function findFrame(doc, w, h) {
  var stack = [];
  for (var i = 0; i < doc.layers[0].pageItems.length; i++) stack.push([doc.layers[0].pageItems[i], 0]);
  while (stack.length) {
    var s = stack.shift(), p = s[0];
    if (p.typename == "GroupItem") {
      var b = p.geometricBounds;
      if (p.clipped && Math.abs((b[2] - b[0]) / MM - w) < 1 && Math.abs((b[1] - b[3]) / MM - h) < 1) return [b[0], b[1]];
      if (s[1] < 2) for (var k = 0; k < p.pageItems.length; k++) stack.push([p.pageItems[k], s[1] + 1]);
    }
  }
  throw new Error("frame " + w + "x" + h + " not found");
}

// ── 자르기 전 원본 손보기 (판 경계에 걸리는 글줄 다시 배치) ─────────────────
// op = { region:[x,y,w,h] (원점 기준 mm, y 아래로 +), move:[dx,dy] | scale:s | hide:true, minW:mm }
// region 안에 '통째로' 들어오는 객체만 고른다. 걸치는 그룹은 안으로 들어가 본다. 마스크 경로는 건드리지 않는다.
function pickInside(items, L, T, R, B, out) {
  for (var i = 0; i < items.length; i++) {
    var p = items[i];
    if (p.hidden) continue;
    if (p.typename == "PathItem" && (p.guides || p.clipping)) continue;
    var b = p.geometricBounds;
    if (b[0] >= L - EPS && b[2] <= R + EPS && b[1] <= T + EPS && b[3] >= B - EPS) out.push(p);
    else if (p.typename == "GroupItem" && overlaps(b, L, T, R, B)) pickInside(p.pageItems, L, T, R, B, out);
  }
}
function pickLayers(layers, L, T, R, B, out) {
  for (var i = 0; i < layers.length; i++) {
    if (!layers[i].visible) continue;
    pickInside(layers[i].pageItems, L, T, R, B, out);
    pickLayers(layers[i].layers, L, T, R, B, out);
  }
}
function applyOp(src, op, ox, oy) {
  var g = op.region, L = ox + g[0] * MM, T = oy - g[1] * MM, R = L + g[2] * MM, B = T - g[3] * MM;
  var sel = [];
  pickLayers(src.layers, L, T, R, B, sel);
  if (op.minW) { var keep = []; for (var k = 0; k < sel.length; k++) { var kb = sel[k].geometricBounds; if ((kb[2] - kb[0]) / MM >= op.minW) keep.push(sel[k]); } sel = keep; }
  if (!sel.length) throw new Error("op 영역에 고를 것이 없음: " + g.join(","));
  var U = [1e9, -1e9, -1e9, 1e9];
  for (var i = 0; i < sel.length; i++) { var b = sel[i].geometricBounds; U = [Math.min(U[0], b[0]), Math.max(U[1], b[1]), Math.max(U[2], b[2]), Math.min(U[3], b[3])]; }
  for (var j = 0; j < sel.length; j++) {
    var p = sel[j];
    try { p.locked = false; } catch (e) {}
    if (op.hide) p.hidden = true;
    if (op.move) p.translate(op.move[0] * MM, -op.move[1] * MM);
    if (op.scale) {
      var pb = p.geometricBounds, s = op.scale;
      var tl = U[0] + s * (pb[0] - U[0]), tt = U[1] - s * (U[1] - pb[1]);
      p.resize(s * 100, s * 100, true, true, true, true, s * 100, Transformation.TOPLEFT);
      var nb = p.geometricBounds;
      p.translate(tl - nb[0], tt - nb[1]);
    }
  }
  var what = "scale " + op.scale;   // 겹친 삼항식은 ExtendScript 가 틀리게 계산한다 → if 로
  if (op.move) what = "move " + op.move.join(",");
  if (op.hide) what = "hide";
  log("      op " + what + " n=" + sel.length +
      " 범위 x" + f1((U[0] - ox) / MM) + "-" + f1((U[2] - ox) / MM) + " y" + f1((oy - U[1]) / MM) + "-" + f1((oy - U[3]) / MM));
}

// 같은 원본에서 조각을 연달아 뜰 때(후렉스 가장자리 띠 등) 다시 열지 않는다 — 큰 파일 반복 열기는 느리고 일러가 죽은 적이 있다.
// pre(원본 손보기)가 있는 조각은 원본을 바꾸므로 따로 열고 바로 닫는다.
var CACHE = null;
function closeCache() { if (CACHE) { try { CACHE.doc.close(SaveOptions.DONOTSAVECHANGES); } catch (e) {} CACHE = null; } }
function releaseSrc(part, src) { if (part.pre || part.page) src.close(SaveOptions.DONOTSAVECHANGES); }
function openSrc(part) {
  var f = new File("C:/jjb/src/" + part.src);
  if (!part.pre && !part.page && CACHE && CACHE.path == f.fsName) return CACHE.doc;
  closeCache();
  if (part.page) { app.preferences.PDFFileOptions.pageToOpen = part.page; app.preferences.PDFFileOptions.pDFCropToBox = PDFBoxType.PDFMEDIABOX; }
  var d = app.open(f);
  if (!part.pre && !part.page) CACHE = { path: f.fsName, doc: d };
  return d;
}

// 원본 영역을 잘라 1/10 로 줄인 클리핑 그룹을 출력 문서에 복제해 넣는다
function cutPart(part, outLayer, px, py) {
  var src = openSrc(part);
  src.activate();
  for (var l = 0; l < src.layers.length; l++) unlockAll(src.layers[l]);
  var ab = src.artboards[(part.ab || 1) - 1].artboardRect;
  var ox = ab[0], oy = ab[1];
  var abW = (ab[2] - ab[0]) / MM, abH = (ab[1] - ab[3]) / MM;
  if (part.frame) { var fr = findFrame(src, part.frame[0], part.frame[1]); ox = fr[0]; oy = fr[1]; abW = part.frame[0]; abH = part.frame[1]; }
  var r = part.rect;
  if (!r && part.center) r = [(abW - part.center[0]) / 2, (abH - part.center[1]) / 2, part.center[0], part.center[1]];
  if (!r) r = [0, 0, abW, abH];
  var L = ox + r[0] * MM, T = oy - r[1] * MM, R = L + r[2] * MM, B = T - r[3] * MM;
  for (var o = 0; o < (part.pre || []).length; o++) applyOp(src, part.pre[o], ox, oy);

  var items = [];
  for (var i = 0; i < src.layers.length; i++) collect(src.layers[i], L, T, R, B, items);
  if (part.pick == "back") {
    while (items.length == 1 && items[0].typename == "GroupItem" && !items[0].clipped) {
      var inner = [];
      for (var q = 0; q < items[0].pageItems.length; q++) if (overlaps(items[0].pageItems[q].geometricBounds, L, T, R, B)) inner.push(items[0].pageItems[q]);
      items = inner;
    }
    items = [items[items.length - 1]];
  }
  if (!items.length) throw new Error("no items in " + part.src + " rect " + r.join(","));

  // 원본은 건드리지 않게 같은 문서 안에서 복제본으로 작업
  var host = src.layers[0];
  host.visible = true;
  var G = host.groupItems.add();
  for (var n = 0; n < items.length; n++) {
    try { items[n].locked = false; } catch (e) {}
    items[n].duplicate(G, ElementPlacement.PLACEATEND);
  }
  var clip = host.pathItems.rectangle(T, L, R - L, B < T ? T - B : B - T);
  clip.move(G, ElementPlacement.PLACEATBEGINNING);
  G.clipped = true;

  var dw = part.dst[2] * SHEET * MM;
  var sx = dw / (R - L) * 100;
  var sy = part.dst[3] ? part.dst[3] * SHEET * MM / (T - B) * 100 : sx;
  G.resize(sx, sy, true, true, true, true, (sx + sy) / 2, Transformation.TOPLEFT);
  var cb = G.pageItems[0].geometricBounds;
  var a1 = src.artboards[0].artboardRect;
  G.translate(a1[0] - cb[0], a1[1] - cb[1]);

  var D = G.duplicate(outLayer, ElementPlacement.PLACEATBEGINNING);
  G.remove();
  releaseSrc(part, src);

  var db = D.pageItems[0].geometricBounds;
  D.translate(px + part.dst[0] * SHEET * MM - db[0], py - part.dst[1] * SHEET * MM - db[1]);
  log("    part " + part.src + (part.ab ? " ab" + part.ab : "") + (part.page ? " p" + part.page : "") + " rect=" + f1(r[2]) + "x" + f1(r[3]) + " items=" + items.length + " scale=" + f1(sx) + (sy != sx ? "/" + f1(sy) : "") + "%");
  return D;
}

// 그림 파일(링크 깨진 원본에서 뽑은 CMYK TIFF 등)을 넣고 dst 크기로 맞춘다
function placeImg(part, outLayer, px, py) {
  var pi = outLayer.placedItems.add();
  pi.file = new File("C:/jjb/src/" + part.img);
  pi.embed();
  var it = outLayer.pageItems[0];
  var b = it.geometricBounds;
  var w = part.dst[2] * SHEET * MM, h = part.dst[3] * SHEET * MM;
  it.resize(w / (b[2] - b[0]) * 100, h / (b[1] - b[3]) * 100, true, true, true, true, 100, Transformation.TOPLEFT);
  b = it.geometricBounds;
  it.translate(px + part.dst[0] * SHEET * MM - b[0], py - part.dst[1] * SHEET * MM - b[1]);
  log("    img " + part.img + " " + it.typename);
  return it;
}

// ── 족자봉 안전 여백: 위·아래 SAFE mm 안쪽에 내용이 오도록 판 내용을 같은 비율로 줄이고, 남는 가장자리는 배경으로 채운다 ──
// pc.safe = [원래 위 여백, 원래 아래 여백] (mm, check_margin.py 실측). 동료 요청 2026-10-22 "상/하단 7cm 이상 여유".
// 가장자리 채움은 축소된 그림의 끝 2mm 띠를 '그림으로 바꿔(rasterize)' 늘린다 — 벡터 사본을 늘려 숨겨 두지 않는다.
var SAFE = 72, EDGE = 2;
function safeFit(doc, lay, PG, pc, px, py) {
  doc.activate();
  var W = pc.W, H = pc.H, tm = pc.safe[0], bm = pc.safe[1], span = H - tm - bm;
  var s = Math.min(1, (H - 2 * SAFE) / span);
  var cx = W / 2, cy = tm + span / 2;
  var ny = Math.max(SAFE + s * span / 2, Math.min(H - SAFE - s * span / 2, cy)), dy = ny - cy;
  var U = SHEET * MM;
  // 흰판을 뺀 판 내용을 한 묶음으로
  var CG = lay.groupItems.add(), list = [];
  for (var i = 0; i < PG.pageItems.length; i++) if (PG.pageItems[i].name != "흰판") list.push(PG.pageItems[i]);
  for (var k = 0; k < list.length; k++) list[k].move(CG, ElementPlacement.PLACEATEND);
  var mk = lay.pathItems.rectangle(py, px, 1, 1); mk.move(CG, ElementPlacement.PLACEATEND);   // 판 좌상단 표시점 — 축소 뒤 위치 보정용
  CG.resize(s * 100, s * 100, true, true, true, true, s * 100, Transformation.TOPLEFT);
  var ex = px + cx * U + s * (px - (px + cx * U)), ey = (py - cy * U) + s * (py - (py - cy * U)) - dy * U;
  var mb = mk.geometricBounds; CG.translate(ex - mb[0], ey - mb[1]); mk.remove();
  CG.move(PG, ElementPlacement.PLACEATBEGINNING);
  var x0 = cx - s * cx, x1 = W - x0, y0 = cy - s * cy + dy, y1 = cy + s * (H - cy) + dy, e = EDGE;
  var fills = [[x0, y0, x1 - x0, e, x0, 0, x1 - x0, y0], [x0, y1 - e, x1 - x0, e, x0, y1, x1 - x0, H - y1],
               [x0, y0, e, y1 - y0, 0, y0, x0, y1 - y0], [x1 - e, y0, e, y1 - y0, x1, y0, W - x1, y1 - y0],
               [x0, y0, e, e, 0, 0, x0, y0], [x1 - e, y0, e, e, x1, 0, W - x1, y0], [x0, y1 - e, e, e, 0, y1, x0, H - y1], [x1 - e, y1 - e, e, e, x1, y1, W - x1, H - y1]];
  var n = 0;
  for (var f = 0; f < fills.length; f++) {
    var q = fills[f];
    if (q[6] < 0.05 || q[7] < 0.05) continue;
    // 띠는 그림 끝에서 0.5mm 안쪽에서 뜬다 — rasterize 가 픽셀 격자에 맞추며 끝에 흰 조각을 붙이는데, 늘리면 흰 줄이 된다
    // (2026-10-23 앤앤에스피·제이콥 판 아래 흰 줄 실측). 채움은 판 바깥쪽으로 1mm 더 내보내 끝 실선도 막는다.
    var d = 0.5, sx0 = q[0] + d, sy0 = q[1] + d, sw = q[2] - 2 * d, sh = q[3] - 2 * d;
    var tx0 = q[4], ty0 = q[5], tw = q[6], th = q[7];
    if (tx0 < 0.01) { tx0 -= 1; tw += 1; } if (ty0 < 0.01) { ty0 -= 1; th += 1; }
    if (tx0 + tw > W - 0.01) tw += 1; if (ty0 + th > H - 0.01) th += 1;
    var D = CG.duplicate(lay, ElementPlacement.PLACEATBEGINNING);
    var L = px + sx0 * U, T = py - sy0 * U;
    var o = new RasterizeOptions(); o.resolution = 1500; o.transparency = false; o.antiAliasingMethod = AntiAliasingMethod.ARTOPTIMIZED;
    var R = doc.rasterize(D, [L, T, L + sw * U, T - sh * U], o);
    var rb = R.geometricBounds;
    R.resize(tw * U / (rb[2] - rb[0]) * 100, th * U / (rb[1] - rb[3]) * 100, true, true, true, true, 100, Transformation.TOPLEFT);
    rb = R.geometricBounds; R.translate(px + tx0 * U - rb[0], py - ty0 * U - rb[1]);
    R.move(PG, ElementPlacement.PLACEATEND);   // 흰판 바로 위가 되도록 맨 아래로 보낸 뒤 흰판을 다시 맨 아래로
    n++;
  }
  for (var b = 0; b < PG.pageItems.length; b++) if (PG.pageItems[b].name == "흰판") { PG.pageItems[b].move(PG, ElementPlacement.PLACEATEND); break; }
  log("    여백맞춤 축소 " + f1(s * 100) + "% 위아래 " + f1(ny - s * span / 2) + "/" + f1(H - ny - s * span / 2) + "mm 가장자리채움 " + n);
}

function addLabel(doc, layer, font, lines, cx, bottomY, maxW, s0, s1) {
  // 큰 첫 줄과 아래 줄을 한 글상자에 넣으면 아래 줄이 큰 글자에 붙어 보였다 (2026-10-26 안랩 켈지 "깔끔하게 정리")
  // → 두 글상자로 나눠 첫 줄 크기 비례로 띄운다. (한 상자 안 줄간격 조정은 일러가 'illegal text range' 로 거부)
  function frame(txt, size) {
    var tf = layer.textFrames.add(); tf.contents = txt;
    var ca = tf.textRange.characterAttributes; ca.size = size; ca.textFont = font; ca.fillColor = cmyk(0, 0, 0, 100);
    for (var i = 0; i < tf.paragraphs.length; i++) tf.paragraphs[i].paragraphAttributes.justification = Justification.CENTER;
    return tf;
  }
  // 재질을 60pt·색 구분(현수막 빨강, 페트지 파랑)으로 크게 쓰는 건 2026 부산 행사 동료 요청(10-22·23)이라 행사 옵션이다.
  // 기본은 24pt 검정 (ASURA님 2026-10-26 "글씨 너무 커, 지금 행사는 특별히 저렇게 한 거"). 켜려면 jobs.js 에 var BIG_MAT = true;
  var bigMat = typeof BIG_MAT != "undefined" && BIG_MAT;
  var big = frame(lines[0], s0 || (bigMat ? 60 : 24));
  var p0 = big.textRange.characterAttributes;
  if (bigMat && lines[0].indexOf("현수막") >= 0) p0.fillColor = cmyk(0, 100, 100, 0);
  else if (bigMat && lines[0].indexOf("페트") >= 0) p0.fillColor = cmyk(100, 60, 0, 0);
  // 판 폭(+간격 일부)을 넘으면 큰 첫 줄을 줄여 이웃 라벨과 겹치지 않게
  for (var t = 0; t < 8 && big.width > maxW; t++) p0.size = Math.max(20, p0.size * maxW / big.width * 0.98);
  var rest = [];
  for (var k = 1; k < lines.length; k++) if (lines[k] !== "") rest.push(lines[k]);
  var y = bottomY;
  if (rest.length) {
    var small = frame(rest.join(String.fromCharCode(13)), s1 || 16);
    small.left = cx - small.width / 2; small.top = y + small.height;
    y = small.top + p0.size * 0.15;
  }
  big.left = cx - big.width / 2; big.top = y + big.height;
  return big;
}

function pickFont() {
  // 글꼴 목록 조회가 가끔 실패하면 예전엔 목록 첫 글꼴(AcadEref, 가는 CAD 글꼴)로 조용히 넘어갔다 (2026-10-26 안랩 켈지 라벨이 가늘게 나옴)
  // → 이름으로 못 찾으면 '맑은 고딕 Bold' 를 목록에서 다시 찾고, 그래도 없으면 멈춘다
  // getByName 은 설치 안 된 글꼴도 '찾음'으로 돌려주고 대체 글꼴(가는 글씨)로 찍힌다 (2026-10-28 이글루 라벨, Pretendard 미설치) → 설치 목록에 있는 이름만 쓴다
  var names = ["Pretendard-Bold", "Pretendard-SemiBold", "MalgunGothicBold", "MalgunGothic-Bold"], have = {};
  for (var h = 0; h < app.textFonts.length; h++) have[app.textFonts[h].name] = app.textFonts[h];
  for (var i = 0; i < names.length; i++) if (have[names[i]]) return have[names[i]];
  for (var k = 0; k < app.textFonts.length; k++) { var f = app.textFonts[k]; if (f.name.indexOf("MalgunGothic") == 0 && f.style.indexOf("Bold") >= 0) return f; }
  throw new Error("굵은 글꼴(Pretendard/맑은 고딕 Bold)을 못 찾음 — 라벨을 가는 글꼴로 만들지 않으려고 멈춤");
}

function build(job) {
  log("== " + job.key + " " + job.title);
  var pre = new DocumentPreset();
  pre.colorMode = DocumentColorSpace.CMYK; pre.units = RulerUnits.Millimeters;
  pre.width = 1200 * MM; pre.height = 800 * MM;
  var doc = app.documents.addDocument("", pre);
  // 새 문서 기본 래스터효과 해상도 72ppi 로 두면 업체 원본(대부분 300) 의 글로우·블러가 1/10 시트에서 실물 7ppi 로 굳는다 (2026-10-27 굿모닝 해상도 점검에서 발견)
  doc.rasterEffectSettings.resolution = 300;
  doc.saveAs(new File("C:/jjb/out/" + job.key + ".ai"));  // 경로를 먼저 줘야 오류 때 내 문서만 골라 닫을 수 있다
  var lay = doc.layers[0];
  var font = pickFont();
  log("  글꼴 " + font.name);
  var M = 40 * MM, GAP = 30 * MM, LABEL = 50 * MM, TITLE = 30 * MM;
  var a0 = doc.artboards[0].artboardRect;
  var x = a0[0] + M, top = a0[1] - M - TITLE - LABEL, maxH = 0;

  var t = lay.textFrames.add();
  t.contents = job.title + " — " + (job.sub || "족자봉");
  t.textRange.characterAttributes.size = 48; t.textRange.characterAttributes.textFont = font;
  t.textRange.characterAttributes.fillColor = cmyk(0, 0, 0, 100);
  t.left = a0[0] + M; t.top = a0[1] - M + 4 * MM;

  for (var i = 0; i < job.pieces.length; i++) {
    var pc = job.pieces[i];
    var w = pc.W * SHEET * MM, h = pc.H * SHEET * MM;
    log("  [" + pc.pos + "] " + pc.W + "x" + pc.H);
    var PG = lay.groupItems.add();
    // 흰판: 판 크기와 같은 흰 사각형을 맨 아래에 — 바탕이 빈 원본도 판 크기가 정해지게 (ASURA님 지시 2026-10-22)
    var base = lay.pathItems.rectangle(top, x, w, h);
    base.name = "흰판"; base.stroked = false; base.filled = true; base.fillColor = cmyk(0, 0, 0, 0);
    base.move(PG, ElementPlacement.PLACEATEND);
    for (var f = 0; f < (pc.fills || []).length; f++) {
      var fl = pc.fills[f];
      var rr = lay.pathItems.rectangle(top - fl[1] * SHEET * MM, x + fl[0] * SHEET * MM, fl[2] * SHEET * MM, fl[3] * SHEET * MM);
      rr.stroked = false; rr.filled = true; rr.fillColor = cmyk(fl[4], fl[5], fl[6], fl[7]);
      rr.move(PG, ElementPlacement.PLACEATBEGINNING);
    }
    var parts = pc.parts;
    for (var p = 0; p < parts.length; p++) {
      var D = parts[p].img ? placeImg(parts[p], lay, x, top) : cutPart(parts[p], lay, x, top);
      D.move(PG, ElementPlacement.PLACEATBEGINNING);
    }
    if (pc.safe) safeFit(doc, lay, PG, pc, x, top);
    var outer = lay.pathItems.rectangle(top, x, w, h);
    outer.move(PG, ElementPlacement.PLACEATBEGINNING);
    PG.clipped = true;
    closeCache();
    if (job.oneMat) addLabel(doc, lay, font, [pc.pos, pc.W + " x " + pc.H + "mm  /  " + (pc.qty || 1) + "EA"], x + w / 2, top + 6 * MM, w + GAP * 0.8, 34, 22);   // 재질이 제목에 있는 시트: 판 이름 + 치수·수량 두 줄, 제목(48)보다 작게
    else addLabel(doc, lay, font, [pc.l1 || pc.mat, (pc.l1 ? "" : "족자봉 ") + pc.W + "mm x " + pc.H + "mm", pc.pos + " / " + (pc.qty || 1) + "EA"], x + w / 2, top + 6 * MM, w + GAP * 0.8);   // 첫 줄 = 재질만 크게
    x += w + GAP;
    if (h > maxH) maxH = h;
  }
  doc.artboards[0].artboardRect = [a0[0], a0[1], x - GAP + M, top - maxH - M];
  // 시트 바탕 연회색 — 흰 바탕 판이 흰 시트와 구분되게 (ASURA님 지적 2026-10-23). 맨 아래 잠긴 레이어, 판은 건드리지 않는다
  var BG = doc.layers.add(); BG.name = "시트 바탕"; BG.move(doc, ElementPlacement.PLACEATEND);
  var ar = doc.artboards[0].artboardRect, gp = BG.pathItems.rectangle(ar[1], ar[0], ar[2] - ar[0], ar[1] - ar[3]);
  gp.stroked = false; gp.filled = true; gp.fillColor = cmyk(0, 0, 0, 25); gp.name = "시트 바탕"; BG.locked = true;

  // 출력 전 정리: 글자깨기, 링크 그림 포함, RGB 그림 수
  var nText = doc.textFrames.length;
  for (var k = doc.textFrames.length - 1; k >= 0; k--) doc.textFrames[k].createOutline();
  var nPlaced = doc.placedItems.length;
  for (var e = doc.placedItems.length - 1; e >= 0; e--) { try { doc.placedItems[e].embed(); } catch (er) { log("  embed fail " + er); } }
  var rgb = 0;
  for (var g = 0; g < doc.rasterItems.length; g++) if (doc.rasterItems[g].imageColorSpace == ImageColorSpace.RGB) rgb++;
  log("  text_outlined=" + nText + " placed_embedded=" + nPlaced + " raster=" + doc.rasterItems.length + " rgb_raster=" + rgb + " left_text=" + doc.textFrames.length);

  var so = new IllustratorSaveOptions();
  so.pdfCompatible = true; so.embedLinkedFiles = true; so.compressed = true;
  doc.saveAs(new File("C:/jjb/out/" + job.key + ".ai"), so);
  doc.close(SaveOptions.DONOTSAVECHANGES);
  log("  saved C:/jjb/out/" + job.key + ".ai");
}

// 사용자가 같은 일러에서 작업 중일 수 있다 — C:/jjb 아래 문서(내가 연 것)만 닫는다
function closeMine() {
  for (var i = app.documents.length - 1; i >= 0; i--) {
    var d = app.documents[i], p = "";
    try { p = d.fullName.fsName; } catch (e) { continue; }
    if (p.toLowerCase().indexOf("c:\\jjb\\") == 0) d.close(SaveOptions.DONOTSAVECHANGES);
  }
}

var oldScale = app.preferences.getBooleanPreference("scaleLineWeight");
app.preferences.setBooleanPreference("scaleLineWeight", true);
var userDoc = null;
try { userDoc = app.activeDocument.name; } catch (e) {}
$.evalFile("C:/jjb/jsx/jobs.js");
for (var j = 0; j < JOBS.length; j++) {
  if (typeof ONLY != "undefined" && ONLY != "all" && JOBS[j].key != ONLY) continue;
  if (JOBS[j].hold && ONLY != JOBS[j].key) { log("== " + JOBS[j].key + " 보류(" + JOBS[j].hold + ")"); continue; }
  try { build(JOBS[j]); } catch (err) { log("  ERROR " + JOBS[j].key + ": " + err + " (line " + err.line + ")"); closeMine(); }
}
app.preferences.setBooleanPreference("scaleLineWeight", oldScale);
if (userDoc) { try { app.documents.getByName(userDoc).activate(); } catch (e) {} }
var lf = new File("C:/jjb/build_log.txt"); lf.encoding = "UTF-8"; lf.open("a"); lf.writeln(LOG.join("\n")); lf.close();

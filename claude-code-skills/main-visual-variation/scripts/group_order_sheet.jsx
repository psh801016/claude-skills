// KOBC·BMFW 2026 발주 시트 — 그룹(등록데스크·포토존1·포토존2·메인무대·로비LED)마다 품목 판(C:/mvv/out/<key>.ai)을 한 장(1/10)에 모은다.
// 사용자 2026-11-03 "이렇게 다 따로가 아니라 등록데스크면 등록데스크 전부로 묶어 포토존이면 포토존 다 묶어서". 바탕 examples/inwepf_2026/order_sheet.jsx.
// 판 위 4줄 라벨(이름 / 마감 / WxHmm / 수량) + 모서리 여유 표시(ㄱ·ㄴ)도 같이 옮긴다. 결과 C:/mvv/out/<그룹>_발주.ai·jpg
var MM = 72 / 25.4;
var MAT = "목공 (불칼질)";
// 좌·우 날개가 같은 디자인이면 한 번만 놓고 수량 2ea(사용자 "날개가 동일하면 갯수만 늘리면 되잖아 따로 놓지말고")
// 1일차·2일차 한 판에 같이(사용자 정정 2026-11-03 밤 "1일차 2일차 하나로 같이 들어가는거다"), 날개 500 통일, 같은 디자인 날개는 한 번·총수량
var GROUPS = [
  { name: "메인무대", rows: [[["메인무대_목공", "무대 좌우목공", 4200, 2200, 2], ["메인무대_LED하단띠", "LED 하단 띠", 9200, 900, 1]]] },
  { name: "포토존", light: true, rows: [[["날개_BMFW_3000", "BMFW 날개 (포토존1·로비LED)", 700, 3200, 4], ["포토존1", "포토존1 본판", 8200, 3200, 1], ["날개_KOBC_3000", "KOBC 날개", 700, 3200, 2], ["포토존2", "포토존2 본판", 6400, 3200, 1]]] },
  { name: "등록데스크", rows: [
    [["날개_BMFW_2440", "백월 날개", 700, 2640, 2], ["등록데스크_백월", "등록데스크 백월", 7200, 2640, 1]],
    [["등록데스크_앞판", "등록데스크 앞판", 7200, 1250, 1], ["등록데스크_옆가림막", "옆 가림막", 1200, 1250, 2]] ] },
  { name: "로비LED", rows: [[["로비LED목공", "LED 좌우목공", 2640, 3200, 2]]] }
];
var M = 25, GAP = 45, LAB = 74, TOP = 50, LH = 15.5, PT = 40, MINW = 195, NAMEW = 80, ROWGAP = 45, RT = 34;   // RT = 줄 제목(1일차/2일차) 칸   // 시트 mm. 라벨 = 부산 발주본 꼴(왼쪽 이름 2줄 / 오른쪽 재질·마감·사이즈·수량), 40pt

function font(names) { for (var i = 0; i < names.length; i++) { try { return app.textFonts.getByName(names[i]); } catch (e) {} } return app.textFonts[0]; }
function k(v) { var c = new CMYKColor(); c.black = v; return c; }
function text(lay, s, f, pt, x, y) { var t = lay.textFrames.add(); t.contents = s; var a = t.textRange.characterAttributes; a.textFont = f; a.size = pt; a.fillColor = k(100); t.left = x * MM; t.top = -y * MM; return t; }
function comma(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ","); }

if (app.documents.length) throw new Error("열린 문서가 있어 멈춤 — 사용자 문서를 건드리지 않는다");
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var done = [];
for (var gi = 0; gi < GROUPS.length; gi++) {
  var G = GROUPS[gi];
  var pre = new DocumentPreset(); pre.colorMode = DocumentColorSpace.CMYK; pre.units = RulerUnits.Millimeters; pre.width = 1000 * MM; pre.height = 500 * MM;
  var doc = app.documents.addDocument("", pre), lay = doc.layers[0];
  doc.rasterEffectSettings.resolution = 300;
  var fB = font(["GmarketSansTTFBold", "GmarketSansBold", "Pretendard-Bold", "MalgunGothicBold"]), fR = font(["GmarketSansTTFMedium", "GmarketSansMedium", "Pretendard-Regular", "MalgunGothic"]);
  var ab = doc.artboards[0].artboardRect, X0 = ab[0] / MM, Y0 = -ab[1] / MM;
  // 시트 제목 = 가운데 큰 굵은 한 줄, 공통 정보(재질·마감)를 여기에 몰아 쓴다(참고본 "(레이더) X배너 / 패트지 / 600x1800mm / 사방펀칭")
  var tt = text(lay, "(KOBC·BMFW) " + G.name + " / 목공 / 불칼질 상하좌우 100mm", fB, 84, X0 + M, Y0 + M - 6);   // 사내 발주 PPTX 양식: 그룹 이름만 크게(부산 사이버보안_(공감발주).pptx)
  var y = M + TOP, maxRight = (tt.geometricBounds[2] - ab[0]) / MM;   // 좁은 판 한 장(로비LED)이면 큰 제목이 대지 밖으로 잘렸다
  for (var ri = 0; ri < G.rows.length; ri++) {
    var row = G.rows[ri], x = M, rowH = 0;
    if (row.title) { text(lay, row.title, fB, 56, X0 + M, Y0 + y); y += RT; row = row.items; }
    for (var i = 0; i < row.length; i++) {
      var it = row[i], src = app.open(new File("C:/mvv/out/" + it[0] + ".ai"));
      // 다른 문서로 복제하면 눈금자 원점이 달라 원본 좌표로 이동량을 재면 판이 밀린다(1차: 아래·왼쪽으로 잘림) → 판과 모서리 표시의 '상대 위치'만 원본에서 재고, 위치는 복제 뒤 대상 문서에서 잰다
      var pg = src.groupItems.getByName(it[0]), b0 = pg.geometricBounds, cmSrc = null, off = null;
      // ㄱㄴ 오프셋도 클리핑 패스(판 외곽) 기준 — 묶음 bounds 로 재면 판 밖으로 나간 도시·그래픽만큼 ㄱㄴ이 밀렸다(2026-11-04 앞판 85mm·옆가림막 20mm, 사용자 "ㄱㄴ 잘못된곳있어")
      for (var qq = 0; qq < pg.pageItems.length; qq++) { var pq = pg.pageItems[qq]; if (pq.typename == "PathItem" && pq.clipping) { b0 = pq.geometricBounds; break; } }
      try { cmSrc = src.layers.getByName("여유 표시").groupItems[0]; var cb = cmSrc.geometricBounds; off = [cb[0] - b0[0], cb[1] - b0[1]]; } catch (e) { cmSrc = null; }
      var d = pg.duplicate(lay, ElementPlacement.PLACEATEND), cm = cmSrc ? cmSrc.duplicate(lay, ElementPlacement.PLACEATBEGINNING) : null;
      src.close(SaveOptions.DONOTSAVECHANGES);
      app.activeDocument = doc;
      // 판 위치는 클리핑 패스(판 외곽)로 잰다 — 묶음 bounds 는 판 밖으로 나간 지도·그래픽까지 잡혀 판이 아래로 밀렸다
      var db = d.geometricBounds;
      for (var q = 0; q < d.pageItems.length; q++) { var pi = d.pageItems[q]; if (pi.typename == "PathItem" && pi.clipping) { db = pi.geometricBounds; break; } }
      var top = y + LAB, tx = (X0 + x) * MM, ty = -(Y0 + top) * MM;
      d.translate(tx - db[0], ty - db[1]);
      if (cm) { var cb2 = cm.geometricBounds; cm.translate(tx + off[0] - cb2[0], ty + off[1] - cb2[1]); }
      // 라벨 = 굵은 2줄, 판 위 가운데(사용자 참고본 '범부처 950x2480' 시트 — "이거 얼마나 깔끔하게 보기 좋아"): 이름 / WxHmm · 목공 불칼질 · N ea
      var bw = it[2] / 10, L1 = it[1], L2 = it[2] + "x" + it[3] + "mm   " + it[4] + "ea";   // 판 위엔 이름 + 사이즈·수량만(공통 재질은 제목에)
      var a1 = text(lay, L1, fB, PT, 0, Y0 + y + 8), a2 = text(lay, L2, fB, PT * 1.15, 0, Y0 + y + 8 + LH * 1.2);
      var labW = Math.max(a1.width, a2.width) / MM, slot = Math.max(bw, labW), cxm = X0 + x + slot / 2;
      a1.left = (cxm - a1.width / MM / 2) * MM; a2.left = (cxm - a2.width / MM / 2) * MM;
      d.translate((slot - bw) / 2 * MM, 0); if (cm) cm.translate((slot - bw) / 2 * MM, 0);   // 판도 칸 가운데로
      x += slot + GAP;   // 다음 판은 판 폭·라벨 폭 중 큰 쪽 뒤에
      rowH = Math.max(rowH, LAB + it[3] / 10);
    }
    maxRight = Math.max(maxRight, x - GAP);
    y += rowH + ROWGAP;
  }
  doc.artboards[0].artboardRect = [ab[0], ab[1], ab[0] + (maxRight + M) * MM, ab[1] - (y - ROWGAP + M) * MM];
  tt.left = ab[0] + ((maxRight + M) * MM - tt.width) / 2;   // 제목 가운데
  // 시트 바탕: 판이 흰색(밝은 하늘·흰 날개)이면 회색(K25), 아니면 양식대로 흰 바탕 — 사용자 "바레이션이 흰색이면 바탕은 회색이여 이거 이미 가르쳐줬잖아"
  if (G.light) {
    var BG = doc.layers.add(); BG.name = "시트 바탕"; BG.move(doc, ElementPlacement.PLACEATEND);
    var ar = doc.artboards[0].artboardRect, gp = BG.pathItems.rectangle(ar[1], ar[0], ar[2] - ar[0], ar[1] - ar[3]);
    gp.stroked = false; gp.filled = true; gp.fillColor = k(25); BG.locked = true;
  }
  var so = new IllustratorSaveOptions(); so.pdfCompatible = true; so.compressed = true;
  doc.saveAs(new File("C:/mvv/out/" + G.name + "_발주.ai"), so);
  var jo = new ExportOptionsJPEG(); jo.qualitySetting = 90; jo.artBoardClipping = true; jo.horizontalScale = jo.verticalScale = 150;   // 300% 는 포토존 시트(판 12장)에서 1.8만 px 라 일러가 오래 '응답 없음'이 됐다
  doc.exportFile(new File("C:/mvv/out/" + G.name + "_발주.jpg"), ExportType.JPEG, jo);
  doc.close(SaveOptions.DONOTSAVECHANGES);
  done.push(G.name);
}
"OK " + done.join("|");

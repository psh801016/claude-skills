// INWEPF 2026 전시부스 발주 시트 — 품목 4개(C:/mvv/out/<key>.ai 의 판 묶음)를 한 장(1/10)에 모으고 판마다 위에 이름·마감·사이즈·수량 라벨
// 양식 원본: 부산 2026 3 3D\발주\원본\메인무대게이트.jpg (흰 바탕, 큰 제목, 판 위 4줄 라벨 '현수막 / 상하단 바미싱 / 3920x750mm / 2ea')
// ASURA님 2026-10-26 "발주용으로 네임 사이즈 해서 만들어서 검토 받아". 결과 C:/mvv/out/전시부스_발주.ai (긴 한글 경로 saveAs 오류 → 납품 때 복사)
var MM = 72 / 25.4, U = MM / 10;   // 1/10 시트: 실물 1mm = 0.1mm
var TITLE = "전시부스";
var ITEMS = [   // key, 라벨 4줄, 시트 위 x(mm, 1/10 시트), W·H 실물 mm
  { key: "booth_2930", lines: ["부스 간판 (3m 부스)", "현수막 상하단 바미싱", "2930x500mm", "2ea"], W: 2930, H: 500 },
  { key: "booth_1940", lines: ["부스 간판 (2m 부스)", "현수막 상하단 바미싱", "1940x500mm", "2ea"], W: 1940, H: 500 },
  { key: "desk_kelji", lines: ["데스크 켈지", "켈지", "950x200mm", "4ea"], W: 950, H: 200 },
  { key: "booth_wing", lines: ["부스 날개", "현수막 상하단 바미싱", "450x2480mm", "3ea"], W: 450, H: 2480 }
];
var M = 25, GAP = 35, LAB = 62, TOP = 50, LH = 12.5, PT = 32, MINW = 125;   // 라벨 32pt·줄 12.5mm = 참고본 비율 (13pt 는 너무 작았다). 단위 = 시트 mm

function font(names) { for (var i = 0; i < names.length; i++) { try { return app.textFonts.getByName(names[i]); } catch (e) {} } return app.textFonts[0]; }
function k100() { var c = new CMYKColor(); c.black = 100; return c; }
function text(lay, s, f, pt, x, y) {   // x·y = 시트 좌상단 기준 mm, 글상자 위
  var t = lay.textFrames.add(); t.contents = s;
  var a = t.textRange.characterAttributes; a.textFont = f; a.size = pt; a.fillColor = k100();
  t.left = x * MM; t.top = -y * MM; return t;
}

if (app.documents.length) throw new Error("열린 문서가 있어 멈춤 — 사용자 문서를 건드리지 않는다");
var pre = new DocumentPreset(); pre.colorMode = DocumentColorSpace.CMYK; pre.units = RulerUnits.Millimeters;
pre.width = 1000 * MM; pre.height = 500 * MM;
var doc = app.documents.addDocument("", pre), lay = doc.layers[0];
doc.rasterEffectSettings.resolution = 300;   // 기본 72 면 판의 글로우가 실물 7ppi 로 굳는다 (build.jsx 와 같은 값)
var fB = font(["Pretendard-Bold", "MalgunGothicBold", "MalgunGothic"]), fR = font(["Pretendard-Regular", "Pretendard-Medium", "MalgunGothic"]);
var ab = doc.artboards[0].artboardRect, X0 = ab[0] / MM, Y0 = -ab[1] / MM;   // 대지 좌상단 (mm)
text(lay, TITLE, fB, 72, X0 + M, Y0 + M - 6);

var x = M, maxBottom = 0;
for (var i = 0; i < ITEMS.length; i++) {
  var it = ITEMS[i], src = app.open(new File("C:/mvv/out/" + it.key + ".ai"));
  var g = src.groupItems.getByName(it.key);
  var d = g.duplicate(lay, ElementPlacement.PLACEATEND);
  src.close(SaveOptions.DONOTSAVECHANGES);
  app.activeDocument = doc;
  var top = M + TOP + LAB;
  d.left = (X0 + x) * MM; d.top = -(Y0 + top) * MM;
  for (var l = 0; l < it.lines.length; l++) text(lay, it.lines[l], fR, PT, X0 + x, Y0 + M + TOP + l * LH);
  var w = it.W / 10, h = it.H / 10;
  x += Math.max(w, MINW) + GAP;   // 좁은 판(날개·켈지)도 라벨 폭만큼 자리
  if (top + h > maxBottom) maxBottom = top + h;
}
doc.artboards[0].artboardRect = [ab[0], ab[1], ab[0] + (x - GAP + M) * MM, ab[1] - (maxBottom + M) * MM];
doc.saveAs(new File("C:/mvv/out/전시부스_발주.ai"));
var jo = new ExportOptionsJPEG(); jo.qualitySetting = 90; jo.artBoardClipping = true; jo.horizontalScale = jo.verticalScale = 400;
doc.exportFile(new File("C:/mvv/out/전시부스_발주.jpg"), ExportType.JPEG, jo);
doc.close(SaveOptions.DONOTSAVECHANGES);
"OK " + ITEMS.length;

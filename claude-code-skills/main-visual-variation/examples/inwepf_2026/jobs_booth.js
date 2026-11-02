// INWEPF 2026 전시부스 — 부스 간판 2종·부스 날개·데스크 켈지 (ASURA님 2026-10-26)
// 스타일 = 부산 사이버보안 2026 메인무대게이트 간판(위 가운데 홈에 행사명 + 모서리 딴 흰 판·청록 테두리·꺾쇠 안에 이름). 둥근 판은 반려(2026-10-26). 기관명 2026-10-26 확정(영문).
// 배치: 오픈형 3m 2칸(간판 2930 각 1, 날개 3: 양 끝·가운데) + 2m 1칸(간판 1940 x1) / 데스크 3 → 켈지 3 (2026-10-26 확정. 처음 3D 는 2m 2칸·데스크 4 였다)
// 재료: make_booth_assets.py → C:/mvv/src/inwepf_booth/ (배경 띠·날개 그라데이션, 실물 150ppi CMYK)
// 조각 순번 (probe 2026-10-23): 레이어0 [5] 제목 묶음 = [0] INWEPF(벡터) [1] 'Steering Meeting & Symposium'(글자) [2] 21ST(벡터)
var PIECES = {
  "21ST": { src: "main", items: [[0, 5, 2]] },
  "INWEPF": { src: "main", items: [[0, 5, 0]] },
  "Steering": { src: "main", items: [[0, 5, 1]] }
};
var A = "C:/mvv/src/inwepf_booth/", EV = "INWEPF 2026";
var NAVY = [100, 90, 10, 20], CYAN = [70, 0, 15, 0], WHITE = [0, 0, 0, 0], BLACK = [0, 0, 0, 100], GRAY = [0, 0, 0, 20];
var FONT = ["Poppins-Bold", "Poppins-SemiBold", "Paperlogy-7Bold", "SUIT-Bold", "GmarketSansBold"];

// 위 띠 한 줄 '21ST INWEPF Steering Meeting & Symposium'. x0 = 줄 왼쪽, top = 줄 위, k = 크기 배율. 줄 폭 = 1307.4k
function titleLine(x0, top, k) {
  return [
    { piece: "21ST", at: [x0, top], h: 55 * k },
    { piece: "INWEPF", at: [x0 + 113.7 * k, top], h: 55 * k },
    { piece: "Steering", at: [x0 + 413.4 * k, top + 27.5 * k], anchor: "cl", h: 86 * k }   // 글상자 86 = 글자 높이가 INWEPF 의 약 3/4 (50 은 너무 작았다)
  ];
}
// 이름 판 = 부산 2026 메인무대게이트.ai 간판의 흰 판 모양 (실측 3920x750: 판 y193~620·좌우 여백 328·모서리 따기 70·위 가운데 홈 깊이 32, 홈 위에 행사명)
// m 좌우 여백, T·B 판 위·아래, c 모서리 따기, nw 홈 반폭(0 = 홈 없음), d 홈 깊이. 흰 판 + 청록 테두리 + 바깥 회색 꺾쇠(좌우 끝만)
function nameBoard(W, m, T, B, c, nw, d, sw) {
  var cx = W / 2, R = W - m, o = sw * 2.2, q = 0.414 * o, L = c + 80;
  var top = nw ? [[cx - nw, T], [cx - nw + d, T + d], [cx + nw - d, T + d], [cx + nw, T]] : [];
  var board = [[m + c, T]].concat(top).concat([[R - c, T], [R, T + c], [R, B - c], [R - c, B], [m + c, B], [m, B - c], [m, T + c]]);
  var mid = (T + B) / 2, gap = (B - T) * 0.12;
  function br(sx, x) {   // sx = +1 왼쪽, -1 오른쪽. 위·아래 꺾쇠 두 토막
    return [{ poly: [[x + sx * L, T - o], [x + sx * (c - q), T - o], [x - sx * o, T + c - q], [x - sx * o, mid - gap]], open: true, stroke: GRAY, sw: sw * 0.4, name: "꺾쇠" },
            { poly: [[x - sx * o, mid + gap], [x - sx * o, B - c + q], [x + sx * (c - q), B + o], [x + sx * L, B + o]], open: true, stroke: GRAY, sw: sw * 0.4, name: "꺾쇠" }];
  }
  return [{ poly: board, fill: WHITE, stroke: CYAN, sw: sw, name: "이름 판" }].concat(br(1, m)).concat(br(-1, R));
}
function sign(key, file, W, qty, pos, k, m, name) {   // name = 기관명 (확정 전 COMPANY NAME)
  var cx = W / 2, T = 129, B = 413, d = 22, nw = 653.7 * k + 100;
  return { key: key, file: file, event: EV, title: "부스 간판 " + W + "x500", W: W, H: 500, mat: "현수막 상하단 바미싱", qty: qty, pos: pos,
    layout: [{ img: A + "sign_" + W + "_bg.tif", at: [0, 0], w: W, h: 500, name: "배경" }]
      .concat(nameBoard(W, m, T, B, 47, nw, d, 9))
      .concat(titleLine(cx - 653.7 * k, T + d - 33 - 55 * k, k))   // 행사명은 홈 위, 홈 선과 33 띄움 (참고본 비율. 8 은 g 꼬리가 선에 닿았다)
      .concat([{ newText: name, font: FONT, color: BLACK, cx: cx, cy: (T + d + B) / 2 + 15, h: 175, maxW: W - 2 * m - 160, name: "기관명" }]) };   // 긴 영문 기관명은 폭에 맞춰 줄어든다
}

var JOBS = [
  // 부스명 확정 (김시운님 2026-10-26): 오픈형 3m 2개·2m 1개 = 3부스. ①② 3m, ③ 2m ("2미터짜리에 어느게?" → "3번이요")
  sign("booth_2930_1", "부스간판_2930x500_1", 2930, 1, "① 3m 부스 정면 간판", 1, 200, "Korea Rural Community Corporation(KRC)"),   // 검산: 옥타 3 500 바미싱 = 2930x500
  sign("booth_2930_2", "부스간판_2930x500_2", 2930, 1, "② 3m 부스 정면 간판", 1, 200, "KRC Water Resources Management System"),   // 검산: 옥타 3 500 바미싱 = 2930x500
  sign("booth_1940", "부스간판_1940x500", 1940, 1, "③ 2m 부스 정면 간판", 0.85, 150, "Rural Research Institute(RRI), KRC"),   // 검산: 옥타 2 500 바미싱 = 1940x500
  // 날개: 참고본(부산 2026 메인무대게이트 날개)처럼 글자를 진하게(1차 45% 는 흐리다고 반려), 가운데. 3D 맵 '하단백월날개.png' 와 같은 디자인 — 남색→청록 그라데이션 + 행사명 세로쓰기(위→아래, rot -90), 반투명. 로고 없음
  { key: "booth_wing", file: "부스날개_450x2480", event: EV, title: "부스 날개 450x2480", W: 450, H: 2480, mat: "현수막 상하단 바미싱", qty: 3,   // 검산: 옥타 0.5 2480 바미싱 = 450x2480
    pos: "3m 부스 기둥(왼쪽 끝·가운데·오른쪽 끝)",
    layout: [
      { img: A + "wing_grad.tif", at: [0, 0], w: 450, h: 2480, name: "배경" },
      { pieces: ["21ST", "INWEPF"], mode: "row", gap: 4, rot: -90, cx: 285, cy: 1240, h: 1000, op: 85, name: "행사명" },
      { piece: "Steering", rot: -90, cx: 160, cy: 1240, h: 980, op: 80, name: "부제" }
    ] },
  // 데스크 앞판 950x750: 켈지(950x200) 대신 (ASURA님 2026-10-26 "켈지가 없어지고 950*950 현수막 상하단 바미싱, 메인비주얼로" → "높이가 750 이다").
  // 그림 = 디자인팀 가로 메인비주얼(원 안 제목·국기·곡선 슬로건)을 원 중심 950:750 으로, 남색 하늘은 메인 CMYK(C100 M91 Y32 K53)로 보정 — make_booth_assets.py. 로고·날짜 없음
  { key: "desk_950", file: "데스크_950x750", event: EV, title: "데스크 앞판 950x750", W: 950, H: 750, mat: "현수막 상하단 바미싱", qty: 3,   // 검산: 옥타 1 750 바미싱 = 950x750
    pos: "인포데스크 앞판(부스마다 1, 3부스)",
    layout: [
      { img: A + "desk_950_bg.tif", at: [0, 0], w: 950, h: 750, name: "메인비주얼" }
    ] }
];

// 충청남도 청년정책 대토론회 (2026-11-02) — 메인비주얼 사이즈 바레이션 발주 목록. 우리 몫 = 01 3D 의 백월·LED 만.
// 원형판켈지·X배너·폼보드·DID·명패는 04 현장설치물·03 DID·07 폴더 = 디자인팀 몫 → 이 스킬 대상 아님 (ASURA님 2026-10-23)
// 메인 = 02 메인비주얼\(청년정책)메인비주얼_CMYK.ai (A4, 디자인팀 파일 — run.ps1 이 C:\mvv\src\main.ai 로 복사해 읽기만).
// 조각 = probe.txt 순번 (레이어 0 = '레이어 2', 1 = '레이어 1'; 순번 0 = 맨 위). 2026-10-23 실측:
//   레이어2: [0] 제목 묶음(선·날짜·대토론회·충청남도·청년정책) [1] 말풍선 묶음 [2] 로고 / [3~6] 대지 왼쪽 밖 옛 조각(안 씀)
//   레이어1: [0] 클리핑 묶음 = [2]확성기 남 [3]망원경 남 [4]큐브 [5]흰셔츠 [6]노랑 여 [7]폴더·별 [8]말풍선 아이콘 [9]태블릿 여 [10]꽃(op25) [11]별자리 [12]배경 그라데이션
//            [1~6] 대지 밖 옛 문구(청년이 모이는 충남·15:00~17:00·4F) — 안 씀
var PIECES = {
  "배경":    { src: "main", items: [[1, 0, 12]] },
  "별자리":  { src: "main", items: [[1, 0, 11]] },
  "꽃":      { src: "main", items: [[1, 0, 10]] },
  "인물좌":  { src: "main", items: [[1, 0, 3], [1, 0, 4], [1, 0, 8], [1, 0, 9]] },
  "인물우":  { src: "main", items: [[1, 0, 2], [1, 0, 5], [1, 0, 6], [1, 0, 7]] },
  "제목1":   { src: "main", items: [[0, 0, 3]] },     // 충청남도
  "제목2":   { src: "main", items: [[0, 0, 4]] },     // 청년정책
  "제목3":   { src: "main", items: [[0, 0, 2]] },     // 대토론회
  "구분선":  { src: "main", items: [[0, 0, 0]] },
  "날짜":    { src: "main", items: [[0, 0, 1]] },     // 2026. 11. 2.(월) 15:30 ㅣ 충청남도청 대회의실
  "말풍선1": { src: "main", items: [[0, 1, 1], [0, 1, 2], [0, 1, 3]] },   // 청년이 말하면
  "말풍선2": { src: "main", items: [[0, 1, 0], [0, 1, 4], [0, 1, 5]] },   // 충남이 바뀐다
  "로고":    { src: "main", items: [[0, 2]] },
  // 입구백월 전용 — 기존 01 3D\map\입구백월.ai(1/10, 옛 메인)의 사진 타임라인·캘리만 (scale 10 = 그 문서 1mm 가 실물 10mm)
  "단계제목": { src: "entry", scale: 10, items: [[0, 15]] },   // 기존 입구백월 단계 제목 글상자(글꼴·색만 빌려 쓰고 내용은 v4 로 바꾼다)
  "단계날짜": { src: "entry", scale: 10, items: [[0, 14]] },
  "캘리":     { src: "entry", scale: 10, items: [[0, 7]] }    // 함께 만든 / 청년정책의 여정 (v4 표기로 바꿈)
};
var EV = "충남 청년정책 대토론회", BAN = "현수막 불칼질";
// 발주 여유: 상하좌우 각 200 — 제작물 디자인요청서 5쪽 "상하좌우 20씩" = 20cm (ASURA님 2026-10-23 "상하 좌우 200 이다"). 20mm·100 은 반려됨. 슬로프 없음
var BL = 200;
function titleRow(cx, cy, w) { return { pieces: ["제목1", "제목2", "제목3"], mode: "row", gap: 9, cx: cx, cy: cy, w: w, name: "제목" }; }

// 무대 백월 (보이는 면 W x H, 실물 mm). 인물 양끝, 꽃은 가운데 뒤, 글자 요소는 머리 위 한 줄.
// 머리 위 규칙은 무대 백월·포토존에만 (ASURA님 2026-10-23 "포토존이랑 무대 백월만 그렇다고")
// 로고 A = 좌상단 / B = 우상단 — 이 행사는 B(우상단)로 확정 (ASURA님 2026-10-23 "우상단이 좋은듯")
function stageWall(W, H, logoMode) {
  var cx = W / 2, BAND = H - 1800, L = [
    { piece: "배경", bg: true, name: "배경" },
    { piece: "별자리", at: [-200, -200], w: 3800 },
    { piece: "별자리", at: [W + 200, -200], anchor: "tr", w: 3800, flip: true, name: "별자리R" },
    { piece: "꽃", cx: cx, cy: H * 0.66, w: 2700 },
    // 인물은 불칼질 여유(아래) 끝까지 내린다 — 보이는 면 끝에 맞추면 여유 쪽에 빈 띠가 생긴다 (center_a 1차 미리보기)
    { piece: "인물좌", at: [0, H + BL], anchor: "bl", h: H * 0.78 },
    { piece: "인물우", at: [W + 20, H + BL], anchor: "br", h: H * 0.78 },
    // 날짜·구분선은 바레이션에 넣지 않는다 (ASURA님 2026-10-23 "베리에이션에선 날짜 빼라")
    // 글자 요소는 사람 머리 위 — 바닥에서 1,800 이상 = 위쪽 H-1800 띠 안 (단체촬영 때 서 있는 사람 기준, 포토존과 같은 원칙. ASURA님 2026-10-23)
    // 그래서 말풍선·제목·말풍선을 위쪽 한 줄로 (포디움 폼보드와 같은 꼴)
    titleRow(cx, BAND / 2 + 40, 4800),
    { piece: "말풍선1", cx: cx - 3160, cy: BAND / 2 + 40, w: 1250 },
    { piece: "말풍선2", cx: cx + 3160, cy: BAND / 2 + 40, w: 1250 }
  ];
  // 로고 A = 좌상단 / B = 우상단. 처음 안(중앙 하단)은 사람에 가려 뺐다
  if (logoMode == "A") L.push({ piece: "로고", at: [200, 90], w: 620 });
  else L.push({ piece: "로고", at: [W - 200, 90], anchor: "tr", w: 620 });
  return L;
}
// 일반 가로형 (무대 백월·포토존 아닌 것 — LED 등): 메인처럼 가운데에 제목, 그 아래 말풍선 2개, 로고 중앙 하단
function plainWall(W, H) {
  var cx = W / 2;
  return [
    { piece: "배경", bg: true, name: "배경" },
    { piece: "별자리", at: [-200, -200], w: 3800 },
    { piece: "별자리", at: [W + 200, -200], anchor: "tr", w: 3800, flip: true, name: "별자리R" },
    { piece: "꽃", cx: cx, cy: H * 0.66, w: 2700 },
    { piece: "인물좌", at: [0, H], anchor: "bl", h: H * 0.78 },
    { piece: "인물우", at: [W + 60, H], anchor: "br", h: H * 0.78 },
    titleRow(cx, H * 0.35, Math.min(5400, W * 0.56)),
    { pieces: ["말풍선1", "말풍선2"], mode: "row", gap: 6, cx: cx, cy: H * 0.62, w: 3300, name: "말풍선" },
    { piece: "로고", cx: cx, cy: H - 220, w: 760 }
  ];
}
// 측면 날개(500 폭): 제목 한 줄을 시계방향 90도 돌려 위→아래로 읽게
function wing(W, H) {
  return [{ piece: "배경", bg: true, name: "배경" }, { pieces: ["제목1", "제목2", "제목3"], mode: "row", gap: 9, cx: W / 2, cy: H / 2, h: 1900, rot: -90, name: "제목세로" }];
}

// 입구백월 v4 — 4단계 타임라인 (보이는 면 7320 x 2440, 실물 mm)
var STEPS = [
  { t: "청년 참여단 공개 모집", d: "청년참여단은 공개모집을 통해 청년 창업가,\n청년농부, 학생 등 50명의 충남 청년들로 구성", day: "2026. 8. 19." },
  { t: "시군별 청년\n아이디어 발굴 회의", d: "15개 시군 청년들이 모여\n정책 아이디어 제시", day: "2026. 8. 21. ~ 9. 4." },
  { t: "청년 축제 현장 내 정책\n아이디어 접수", d: "청년 축제 현장에서\n정책 아이디어 접수", day: "2026. 9. 12." },
  { t: "청년 참여단 회의", d: "청년정책 아이디어 정리 및 분야별 방안 마련\n온·오프라인 회의 운영", day: "2026. 9. 21. / 10. 6." }
];
function entryLayout() {
  $.evalFile("C:/mvv/src/photos/photos.js");
  var X0 = 2080, CW = 1190, GAP = 120, L = [
    { piece: "배경", bg: true, name: "배경" },
    { piece: "별자리", at: [7320 + 200, -200], anchor: "tr", w: 3400, flip: true },
    { piece: "꽃", at: [-350, 2440 + 250], anchor: "bl", w: 2400 },
    titleRow(3660, 400, 4200),
    { piece: "말풍선1", cx: 820, cy: 400, w: 1050 },
    { piece: "말풍선2", cx: 6500, cy: 400, w: 1050 },
    { piece: "캘리", text: "함께 만든\n청년정책의 여정", cx: 1000, cy: 1380, w: 1650 }
  ];
  for (var i = 0; i < STEPS.length; i++) {
    var x = X0 + i * (CW + GAP), s = STEPS[i];
    L.push({ piece: "단계제목", text: s.t, at: [x, 930], anchor: "bl", maxW: CW, name: "단계" + (i + 1) + " 제목" });
    L.push({ piece: "단계제목", text: s.d, ptScale: 0.62, at: [x, 1680], maxW: CW, name: "단계" + (i + 1) + " 설명" });
    L.push({ piece: "단계날짜", text: s.day, at: [x, 1870], maxW: CW, name: "단계" + (i + 1) + " 날짜" });
  }
  for (var p = 0; p < PHOTOS.length; p++) L.push(PHOTOS[p]);
  L.push({ piece: "로고", cx: 3660, cy: 2200, w: 700 });
  return L;
}

var JOBS = [
  // 검산: 목공200 9760 2440 = 10160x2840
  { key: "center", event: EV, title: "중앙백월 정면", file: "중앙백월_정면", W: 10160, H: 2840, bleed: BL, mat: BAN, pos: "무대 중앙백월 정면", qty: 1, layout: stageWall(9760, 2440, "B") },
  // 검산: 목공200 500 2440 = 900x2840  — 중앙·입구 측면 날개는 같은 디자인이라 한 파일, 수량 합침 (ASURA님 2026-10-23 "불칼질 날개는 같은거 아녀?")
  { key: "wing", event: EV, title: "백월 측면 날개", file: "백월_측면날개", W: 900, H: 2840, bleed: BL, mat: BAN, pos: "중앙백월 좌·우 2 + 입구백월 좌·우 2", qty: 4, layout: wing(500, 2440) },
  // 검산: 목공200 7320 2440 = 7720x2840
  // 입구백월 타임라인 = Z: 행사폴더 2. 디자인/백월요청서/입구백월 구성 수정안/토론회 준비 과정 조형물 내용(안)_v4.hwpx (ASURA님 2026-10-23 "v4 로 바꿔서")
  //   4단계·설명 문구·Z: 고화질 사진. 사진 자리는 photos.json 한 곳에만 — photos.py 가 C:/mvv/src/photos/photos.js(PHOTOS) 로 쓴다
  //   세로 배치는 기존 입구백월처럼 제목 바로 아래부터 (ASURA님 "너무 아래로 쏠렸어"): 단계제목 ~930 / 사진 965~1645 / 설명 1680~ / 날짜 1870~ / 로고 2200
  { key: "entry", event: EV, title: "입구백월 정면", file: "입구백월_정면", W: 7720, H: 2840, bleed: BL, mat: BAN, pos: "입구백월 정면", qty: 1, layout: entryLayout() },
  // 원형판 켈지 Ø1150 정사이즈 — ASURA님이 발주\원본 에 직접 넣고 "이것도 고쳐" (2026-10-23). 원래 04 현장설치물 사본(옛 메인)
  //   새 메인: 제목 3줄 세로 + 말풍선 2개 아래, 꽃 엠블럼 아래쪽, 별자리 위쪽. 캘리(통하는 충남)·날짜 없음
  { key: "round", event: EV, title: "원형판 켈지", file: "(청년정책)원형판켈지", W: 1150, H: 1150, mat: "켈지", pos: "무대 원형판 (지름 1,150 원형 재단)", qty: 1, shape: "circle", layout: [
    { piece: "배경", bg: true, name: "배경" },
    { piece: "별자리", at: [-80, -60], w: 820 },
    { piece: "별자리", at: [1150 + 80, -60], anchor: "tr", w: 620, flip: true, name: "별자리R" },
    { piece: "꽃", cx: 575, cy: 990, w: 820 },
    // 말풍선은 제목 위 (ASURA님 2026-10-23 "말풍선이 위로 가야할듯")
    { pieces: ["말풍선1", "말풍선2"], mode: "row", gap: 6, cx: 575, cy: 220, w: 620, name: "말풍선" },
    { pieces: ["제목1", "제목2", "제목3"], mode: "col", gap: 3, cx: 575, cy: 590, w: 630, name: "제목" }
  ] },
  // LED 는 3D 텍스처용 — 발주 아님, 시트·라벨 없이 (ASURA님 2026-10-23). 결과 jpg 를 01 3D\map\led.jpg 로
  { key: "led", event: EV, title: "LED (3D 텍스처)", file: "led_새메인", dest: "map", W: 8500, H: 2740, sheet: false, mat: "LED", pos: "무대 LED", layout: plainWall(8500, 2740) }
];

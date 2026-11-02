// INWEPF 2026 (제21차 INWEPF 운영위원회 및 심포지엄, 호텔스퀘어안산) — 무대 LED 10m x 4m, 3D 맵용 (발주 아님, 시트·라벨 없음, RGB 문서)
// 요청서: Z: 행사폴더 02. 실행/03. 디자인/※ 디자인 요청서/3D 요청서(10.18).pptx 1쪽 "LED : 10M*4M"
// 참고: 지식재산대전 2026 제안/01 3D/map/무대LED.ai — ① 전체 비주얼 ② 연사 화면 + 픽셀 줄무늬 Overlay 50%
// 재료(make_led_assets.py): bg_rgb.tif(디자인팀 가로 배경) / led_pattern.png(픽셀 줄무늬) / imag_win.png(연사 카메라 화면 창)
// 연사 = 실제 연사는 LED 가운데 앞에 서고, 좌우 창에 그 카메라 화면을 띄운다 (ASURA님 2026-10-23 "지금은 그냥 led가 하나에 판같잖아")
// 조각 순번 (2026-10-23 probe): 레이어0 '레이어 2' = [0]국기 줄 [1]상단 로고 줄(안 [0]Organizer [1]Host) [4]휘어진 슬로건 [5]제목 [6]날짜(안 씀)
//   레이어1 = [3]물결선 [5]빛나는 고리 [25]점 지구본 [26]태극 원
var PIECES = {
  "원": { src: "main", items: [[0, 0], [0, 4], [0, 5], [1, 3], [1, 5], [1, 25], [1, 26]] },   // 포스터 속 원+제목+국기+슬로건 한 덩어리
  "Host": { src: "main", items: [[0, 1, 1]] },
  "Organizer": { src: "main", items: [[0, 1, 0]] }
};
var A = "C:/mvv/src/inwepf/", W = 10000, H = 4000, LOGO = 31.8;   // 로고 배율: Host 59.8mm → 1,900mm
// 픽셀 줄무늬 — 참고 파일처럼 7.29m 폭 타일을 이어 판 전체를 덮는다
var PATTERN = [
  { img: A + "led_pattern.png", at: [-1290, -54], w: 7290, h: 4108, blend: "OVERLAY", op: 50, name: "LED 픽셀 효과 1" },
  { img: A + "led_pattern.png", at: [6000, -54], w: 7290, h: 4108, blend: "OVERLAY", op: 50, name: "LED 픽셀 효과 2" }
];
var JOBS = [
  // ① 기본: 화면 전체 비주얼
  { key: "led_main", title: "LED 기본", file: "LED_기본", W: W, H: H, rgb: true, sheet: false, mat: "LED", pos: "무대 LED 10x4m", layout: [
    { img: A + "bg_rgb.tif", at: [0, 0], w: W, h: H, name: "배경" },
    { piece: "원", cx: W / 2, cy: 2080, h: 3650 },
    { piece: "Host", at: [300, 230], w: 59.8 * LOGO },
    { piece: "Organizer", at: [W - 300, 230], anchor: "tr", w: 74.6 * LOGO }
  ].concat(PATTERN) },
  // ② 연사: 비주얼은 판 전체 그대로, 좌우에 테두리 있는 카메라 화면 창(2.2 x 3.5m)
  { key: "led_speaker", title: "LED 연사", file: "LED_연사", W: W, H: H, rgb: true, sheet: false, mat: "LED", pos: "무대 LED 10x4m", layout: [
    { img: A + "bg_rgb.tif", at: [0, 0], w: W, h: H, name: "배경" },
    { piece: "원", cx: W / 2, cy: 2080, h: 3500 },
    { piece: "Host", at: [2650, 230], w: 59.8 * 20 },
    { piece: "Organizer", at: [W - 2650, 230], anchor: "tr", w: 74.6 * 20 },
    { img: A + "imag_win.png", at: [180, 250], w: 2200, h: 3500, name: "연사 화면 좌" },
    { img: A + "imag_win.png", at: [W - 180 - 2200, 250], w: 2200, h: 3500, name: "연사 화면 우" }
  ].concat(PATTERN) }
];

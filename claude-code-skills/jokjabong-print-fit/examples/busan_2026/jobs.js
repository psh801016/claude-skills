// 족자봉 발주 목록 — 2026 부산 사이버보안 콘퍼런스 (요청서 1021 + 김태영님 확인 반영)
// 조각: pos/mat/W/H, parts = 원본 영역(rect: 대지 좌상단 기준 mm) → dst [x,y,폭(,높이)] 실치수 mm
function P(pos, mat, W, H, parts, fills) { return { pos: pos, mat: mat, W: W, H: H, parts: parts, fills: fills || [] }; }
function A(src, ab, W) { return [{ src: src, ab: ab, dst: [0, 0, W] }]; }
function R(src, rect, W, extra) { var o = { src: src, rect: rect, dst: [0, 0, W] }; if (extra) for (var k in extra) o[k] = extra[k]; return [o]; }
var PET = "페트지", BAN = "현수막", F = [6500, 2350];
var K = 900 / 1853.2;
// 제이콥 정면 판 위 띠: 원본 띠 색 그대로 (남색 490 높이 → 100, 초록 20 → 4 로 비율 유지). 원본을 늘려 쓰지 않는다
var JC_BAND = [[0, 0, 900, 100, 100, 88, 53, 22], [0, 100, 900, 4, 70, 0, 80, 0]];
// 판 경계(900)에 걸리는 글줄 다시 배치 — 원본 좌표(mm, 원점 기준, y 아래로 +)
// 위드 왼쪽 대지(1800): '무선 보안을 하나의 체계로'(109-1381)를 두 줄로 → 문구 3줄을 0.88 로 줄여 좌측1 안에 좌우 여백을 맞춘다
var WITH_TEXT = [{ region: [700, 730, 700, 130], move: [-603, 130] }, { region: [90, 600, 820, 400], scale: 0.88 }];
// 좌측1 에는 기기 그림·후광(1407 폭 그룹)이 잘려 들어오므로 숨긴다 — 기기는 좌측2 에 온전히 남는다
var WITH_L1 = WITH_TEXT.concat([{ region: [600, -100, 1500, 1000], hide: true, minW: 1000 }]);
// 신화 왼쪽 날개: 'Contain the / Breach', 부제 'AI-enhanced breach containment / without complexity or risk' 두 줄, 불릿을 그만큼 내림
var SHIN_L = [{ region: [100, 560, 600, 180], move: [0, 137] }, { region: [655, 430, 420, 60], move: [-522, 137] },
              { region: [120, 430, 545, 60], move: [0, 95] }, { region: [730, 300, 370, 110], move: [-605, 95] }];
// 신화 오른쪽 날개: 잘리진 않지만 'Illumio Insights' 가 판 끝 12mm 까지 붙어 왼쪽과 같게 'Illumio / Insights' 두 줄로
var SHIN_R = [{ region: [4800, 405, 800, 360], move: [0, 95] }, { region: [5200, 300, 410, 130], move: [-375, 95] }];


// 후렉스: 사내 규칙 한 면당 20mm 확장(프레임에 감기는 부분). 원본에 재단 여유가 없으면 앞면은 그대로 두고
// 가장자리 2mm 띠를 20mm 로 늘려 채운다 — 감기는 면이라 앞에서는 안 보인다. (W,H = 원본 정사이즈)
function FLEX(src, W, H) {
  var e = 20, s = 2, P2 = [{ src: src, ab: 1, rect: [0, 0, W, H], dst: [e, e, W] }];
  var strips = [[0, 0, s, H, 0, e, e, H], [W - s, 0, s, H, W + e, e, e, H], [0, 0, W, s, e, 0, W, e], [0, H - s, W, s, e, H + e, W, e],
                [0, 0, s, s, 0, 0, e, e], [W - s, 0, s, s, W + e, 0, e, e], [0, H - s, s, s, 0, H + e, e, e], [W - s, H - s, s, s, W + e, H + e, e, e]];
  for (var i = 0; i < strips.length; i++) { var t = strips[i]; P2.push({ src: src, ab: 1, rect: [t[0], t[1], t[2], t[3]], dst: [t[4], t[5], t[6], t[7]] }); }
  return P2;
}
var BIG_MAT = true;   // 이 행사만: 재질 라벨 60pt + 현수막 빨강/페트지 파랑 (동료 요청 2026-10-22·23)
var JOBS = [
 { key: "ahnlab", title: "안랩", pieces: [P("정면 1", BAN, 2900, 2350, A("ahnlab.ai", 1, 2900)), P("정면 2", BAN, 2900, 2350, A("ahnlab.ai", 2, 2900))] },
 // 1024 요청: 안랩 기본부스 인포데스크 앞면 전체 켈지 — 행사명 켈지 대신 자사 로고. 사이즈 950x650 (ASURA님 확인 2026-10-26, 업체 1/10 대지 95x65 와 같음)
 { key: "ahnlab_kelji", title: "안랩 인포데스크", sub: "그레이켈지", oneMat: true, pieces: [   // 같은 디자인은 한 장 + 2EA, 재질 그레이켈지 (ASURA님 2026-10-26)
   { pos: "AhnLab", mat: "그레이켈지", l1: "그레이켈지", W: 950, H: 650, qty: 2, parts: A("ahnlab.ai", 3, 950), fills: [] },
   { pos: "AhnLab AI+", mat: "그레이켈지", l1: "그레이켈지", W: 950, H: 650, qty: 2, parts: A("ahnlab.ai", 4, 950), fills: [] }] },
 { key: "sparrow", title: "스패로우", pieces: [P("좌측 1", PET, 900, 1200, A("sparrow_s1.ai", 1, 900)), P("좌측 2", PET, 900, 1200, A("sparrow_s2.ai", 1, 900)), P("정면", PET, 2900, 1200, A("sparrow_main.ai", 1, 2900))] },
// 프라이빗·이글루: 원본에 반투명·합성 모드(곱하기·스크린·색상 닷지 등)가 많아 1/10 로 줄이면 효과가 빠진다 (2026-10-23 프라이빗 유리 타워가 파랗게 눌림, ASURA님 지적)
//   → 원본 모습 그대로 CMYK 이미지로 렌더(pymupdf, 프라이빗 100dpi·이글루 150dpi)해 쓴다
 { key: "pribit", title: "프라이빗에이아이", pieces: [P("정면", PET, 2900, 2350, [{ img: "pribit_cmyk.tif", dst: [0, 0, 2900, 2350] }])] },
 { key: "with", title: "위드네트웍스", pieces: [
   P("좌측 1", PET, 900, 1200, R("with.ai", [0, 0, 900, 1200], 900, { ab: 1, pre: WITH_L1 })), P("좌측 2", PET, 900, 1200, R("with.ai", [900, 0, 900, 1200], 900, { ab: 1, pre: WITH_TEXT })),
   P("정면", PET, 2900, 2350, A("with.ai", 4, 2900)), P("우측 1", PET, 900, 1200, A("with.ai", 2, 900)), P("우측 2", PET, 900, 1200, A("with.ai", 3, 900))] },
 // 워터월 원본: 2026-10-23 14:33 `…부스 그래픽_최종 1.ai` (김태영님 교체 요청 — "온프레미스/클라우드" 띄어쓰기 수정본)
 { key: "waterwall", title: "워터월시스템즈", pieces: [P("정면", PET, 2900, 1200, A("waterwall.ai", 1, 2900))] },
 { key: "somansa", title: "소만사", pieces: [P("좌측", BAN, 900, 1200, A("somansa.ai", 1, 900)), P("정면", BAN, 900, 1200, A("somansa.ai", 3, 900)), P("우측", BAN, 900, 1200, A("somansa.ai", 2, 900))] },
 // 우리아이티: PDF 의 그림 ~290개가 일러에서 손댈 수 없는 객체로 들어와 색 맞춤을 못 한다 → PDF 를 색 맞춤 CMYK TIFF(200dpi)로 렌더해 쓴다 (color/colorize.py pdf)
 { key: "woori", title: "우리아이티", pieces: [P("좌측", PET, 900, 1200, [{ img: "woori_p1_cmyk.tif", dst: [0, 0, 900, 1200] }]), P("정면", PET, 900, 1200, [{ img: "woori_p2_cmyk.tif", dst: [0, 0, 900, 1200] }]), P("우측", PET, 900, 1200, [{ img: "woori_p3_cmyk.tif", dst: [0, 0, 900, 1200] }])] },
 { key: "nnsp", title: "앤앤에스피", pieces: [P("좌측", BAN, 900, 1200, A("nnsp.ai", 1, 900)), P("정면", BAN, 900, 1200, A("nnsp.ai", 2, 900)), P("우측", BAN, 900, 1200, A("nnsp.ai", 3, 900))] },
 { key: "wins", title: "윈스테크넷", pieces: [P("좌측 1", PET, 900, 1200, A("wins_s1.ai", 1, 900)), P("좌측 2", PET, 900, 1200, A("wins_s2.ai", 1, 900)), P("정면", PET, 2900, 2350, A("wins_front.ai", 1, 2900)), P("우측 1", PET, 900, 1200, A("wins_s3.ai", 1, 900)), P("우측 2", PET, 900, 1200, A("wins_s4.ai", 1, 900))] },
 { key: "jcorp", title: "제이콥시스템·정원엔시스", pieces: [
   P("좌측", PET, 900, 1200, [{ src: "jcorp_left_1029.ai", dst: [0, 0, 900] }]),
   P("정면 1", PET, 900, 1200, [{ src: "jcorp_qr.ai", pick: "back", dst: [0, 0, 900, 1200] }, { src: "jcorp_qr.ai", dst: [0, 0, 900] }]),
   P("정면 2", PET, 900, 1200, [{ src: "jcorp_front.ai", rect: [85, 601.4, 1853.2, 1853.2], dst: [0, 130, 900] }, { src: "jcorp_front.ai", rect: [1580, 2460, 730, 90], dst: [(900 - 730 * K) / 2, 1045, 730 * K] }], JC_BAND),
   P("정면 3", PET, 900, 1200, [{ src: "jcorp_front.ai", rect: [1940, 600, 1853.2, 1853.2], dst: [0, 130, 900] }, { src: "jcorp_front.ai", rect: [1580, 2460, 730, 90], dst: [(900 - 730 * K) / 2, 1045, 730 * K] }], JC_BAND),
   P("우측", PET, 900, 1200, [{ src: "jcorp_right_1029.ai", dst: [0, 0, 900] }])] },
 { key: "dream", title: "드림시큐리티", pieces: [P("정면", PET, 2900, 2350, A("dream.ai", 1, 2900))] },   // 1022 새 작업 — 원본 1/2 축척(1450x1175)
 // 1027 업체 재전달(백월 이미지 10.27일 수령…_발주파일.ai): 세 대지 모두 장식 점 배치만 바뀜. 1026 측면 900x1200 2장 추가 (김태영 전달, 업체 '좌우여백_최종' 파일 대지 2·3 — 배경만, 좌우 구분 없음 → 대지 순서대로 측면 1·2). 정면 대지 1은 이전 파일과 픽셀 동일
 { key: "goodmorning", title: "굿모닝아이텍", pieces: [P("정면", PET, 2900, 2350, A("goodmorning_1027.ai", 1, 2900)), P("측면 1", PET, 900, 1200, A("goodmorning_1027.ai", 2, 900)), P("측면 2", PET, 900, 1200, A("goodmorning_1027.ai", 3, 900))] },
 { key: "secure", title: "시큐어레터", pieces: [P("좌측 1", PET, 900, 1200, A("secure_side.ai", 1, 900)), P("좌측 2", PET, 900, 1200, A("secure_side.ai", 2, 900)), P("정면", PET, 2900, 2350, A("secure_front.ai", 1, 2900)), P("우측 1", PET, 900, 1200, A("secure_side.ai", 3, 900)), P("우측 2", PET, 900, 1200, A("secure_side.ai", 4, 900))] },
 { key: "igloo", title: "이글루코퍼레이션", pieces: [P("좌측", BAN, 900, 1200, [{ img: "igloo1_cmyk.tif", dst: [0, 0, 900, 1200] }]), P("정면", BAN, 900, 1200, [{ img: "igloo2_cmyk.tif", dst: [0, 0, 900, 1200] }]), P("우측", BAN, 900, 1200, [{ img: "igloo3_cmyk.tif", dst: [0, 0, 900, 1200] }])] },
 { key: "shinhwa", title: "신화씨엔에스", pieces: [
   P("좌측 1", PET, 900, 1200, R("shinhwa_fix.eps", [0, 0, 900, 1200], 900, { frame: F, pre: SHIN_L })), P("좌측 2", PET, 900, 1200, R("shinhwa_fix.eps", [900, 0, 900, 1200], 900, { frame: F, pre: SHIN_L })),
   P("정면", PET, 2900, 2350, R("shinhwa_fix.eps", [1800, 0, 2900, 2350], 2900, { frame: F })),
   P("우측 1", PET, 900, 1200, R("shinhwa_fix.eps", [4700, 0, 900, 1200], 900, { frame: F, pre: SHIN_R })), P("우측 2", PET, 900, 1200, R("shinhwa_fix.eps", [5600, 0, 900, 1200], 900, { frame: F, pre: SHIN_R }))] },
 { key: "itwin", hold: "사이즈 확인 대기", title: "아이티윈 외 4사", sub: "후렉스·켈지 (독립부스)", pieces: [
   { pos: "B-1 왼쪽벽", mat: "후렉스", l1: "후렉스 (사방 20 확장)", W: 2040, H: 1540, parts: FLEX("itwin_b1.ai", 2000, 1500), fills: [] },
   { pos: "B-2 왼쪽벽", mat: "후렉스", l1: "후렉스 (사방 20 확장)", W: 2040, H: 1540, parts: FLEX("itwin_b2.ai", 2000, 1500), fills: [] },
   { pos: "A-1 오른쪽벽", mat: "켈지", l1: "켈지", W: 1500, H: 2250, parts: A("itwin_a1.ai", 1, 1500), fills: [] },
   { pos: "A-3 오른쪽벽", mat: "켈지", l1: "켈지", W: 1500, H: 2250, parts: A("itwin_a3.ai", 1, 1500), fills: [] }] }
];

// 족자봉 상·하단 70mm 여유가 모자란 판 — 원래 위·아래 여백(mm, check_margin.py 실측 2026-10-23). build.jsx 가 내용을 줄여 72mm 안쪽으로 넣는다
var SAFE_M = {"sparrow|좌측 1": [27.5, 195.0], "sparrow|좌측 2": [27.5, 151.5], "with|정면": [66.0, 1411.5], "waterwall|정면": [37.0, 26.5], "woori|좌측": [19.5, 29.0], "woori|정면": [19.5, 85.5], "woori|우측": [19.5, 41.5], "nnsp|좌측": [48.0, 57.0], "nnsp|정면": [56.0, 57.0], "nnsp|우측": [48.0, 53.5], "goodmorning|정면": [69.5, 154.0], "secure|좌측 2": [24.0, 175.0], "secure|우측 2": [24.0, 175.0], "igloo|좌측": [59.5, 68.0], "igloo|우측": [59.5, 68.0]};
for (var si = 0; si < JOBS.length; si++) for (var sj = 0; sj < JOBS[si].pieces.length; sj++) { var sk = JOBS[si].key + "|" + JOBS[si].pieces[sj].pos; if (SAFE_M[sk]) JOBS[si].pieces[sj].safe = SAFE_M[sk]; }

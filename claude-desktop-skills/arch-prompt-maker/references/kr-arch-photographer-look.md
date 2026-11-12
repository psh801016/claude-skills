# 한국 건축사진가 실사 기준 — 건물 합성·실사화의 "진짜 사진" 정본

출처: 2026-11-11 ASURA님 지정 레퍼런스 `threads.com/@hanskim_studio`(건축사진가 김현수, 준공 건축 포트폴리오).
분석 대상: 청라문화센터(주간 3/4·정면·디테일), 충남스포츠센터(주간 지상·드론 황혼), 아크로 여의도 더원(타워 정면),
기념 조형물 노을 컷, 촬영 현장 사진(삼각대 + 시프트 카메라, 노트북 현장 보정). ASURA님: "건물 합성 실사화는 이걸 보고 업그레이드, 이게 실사 사진이야".

건물 렌더를 실사로 바꾸거나 현장 사진에 건물을 합성할 때 **목표 사진은 '분위기 컷'이 아니라 '준공 기록 건축사진'**이다.
아래 8가지가 그 사진의 문법이다. 프롬프트와 검수 모두 이 기준으로 한다.

## 1. 수직선은 완전 수직 (가장 큰 차이)
- 시프트 렌즈·현장 보정으로 **세로선 기울기 0°**. 2점 투시라도 수직 소실은 없다(3점 투시 금지). 타워 정면도 위로 좁아지지 않는다.
- 카메라는 사람 눈높이(삼각대 1.5~1.7m), 수평선은 화면 40~55% 근처. 건물을 올려다보며 수직이 모이는 각도는 쓰지 않는다 — 대신 렌즈를 올려(shift) 하늘을 위에 많이 남긴다.
- 프롬프트: `perspective-corrected architectural photograph taken with a shift lens from eye level on a tripod, all vertical lines perfectly vertical and parallel, two-point perspective with no vertical convergence`
- 검수: `scripts/check_verticals.py --img 결과.png` → `VERT_OK`(세로선 중앙 |기울기| ≤0.3°). 합성본이 이걸 못 넘으면 납품하지 않는다.

## 2. 맑은 날 측면 직사광 — 형태를 그림자로 읽게
- 기본 조건은 **청명한 맑은 날**, 해는 측면·약간 뒤(오전/늦가을 오후), 고도 낮~중간. 매스마다 밝은 면/그늘 면이 분명하고, 캔틸레버 밑·발코니 밑에 진한 그림자가 떨어진다.
- 흐린 날의 평평한 빛·CG 의 사방 균일 GI 가 렌더 티의 1순위다. 그림자 방향은 화면 전체에서 하나.
- 그늘은 검게 뭉개지지 않고 디테일이 남는다(브라케팅 합성 수준의 열린 그늘) — 하지만 HDR 후광·회색 평탄화는 없다.

## 3. 하늘 — 진한 편광 파랑, 위로 갈수록 짙게
- 편광 필터를 쓴 듯 **깊은 코발트 블루**, 꼭대기가 가장 짙고 수평선 쪽이 옅은 부드러운 그라데이션. 구름은 없거나 얇은 새털구름 몇 줄.
- 하늘이 화면의 30~50% 를 차지해도 된다(시프트로 건물을 아래에 둔 결과). 하늘에 노이즈·밴딩 없음.
- 유리 커튼월은 이 파란 하늘과 주변 건물을 **왜곡 없이 반사**한다(청록 유리 + 하늘색). 유리가 투명한 내부 렌더처럼 보이면 실패.

## 4. 노출·색 — 깨끗한 흰색, 중립~약간 차가운 화이트밸런스
- 흰 금속패널·화이트 벽돌이 **순백에 가깝게** 밝지만 날아가지 않는다(하이라이트 디테일 유지). 전체 톤은 중립~약간 차갑다.
- 채도: 하늘 파랑만 진하고, 재료색(벽돌·목재·잔디)은 실제 그대로. 렌더의 과포화 녹색·주황 노을 그레이딩 금지.
- 미세 대비(마이크로 콘트라스트)가 높고 **화면 가장자리까지 선명**(조리개 조인 팬포커스). 비네팅·보케·필름 그레인 연출 없음 — 고화소 디지털 원본의 깨끗한 질감.

## 5. 재료가 '시공된' 디테일
- 벽돌은 줄눈 한 장 한 장, 금속패널은 판 이음선과 미세한 평활도 차이(빛 반사가 판마다 조금씩 다름), 유리는 멀리언·스팬드럴·내부 블라인드가 보인다.
- 난간 유리·스틸 난간, 외부 조명기구·CCTV·배수구·점검구 같은 **실제 설비 소품**이 붙어 있다. 렌더에서 매끈한 단일면이면 이음과 설비를 더한다(형태는 바꾸지 않음).

## 6. 대지는 '막 준공한' 상태
- 바닥은 새 보도블럭·화강석 판석(줄눈 선명, 약간의 얼룩), 조경은 **막 심은 나무**(지주목·가는 줄기·성긴 잎), 잔디 경사면, 경계석, 관목 열.
- 주변 맥락을 지우지 않는다: 뒤 고층 아파트·이웃 건물·전신주·주차 차량·공사 펜스가 그대로 화면에 남는다(현실감의 근거). 사람은 거의 없거나 아주 작게.
- 전경에 나무 가지·화단을 걸어 깊이를 만든다(3/4 뷰 대표 구도).

## 7. 컷 구성 — 한 건물을 4종으로
| 컷 | 구도 | 비고 |
|---|---|---|
| 대표 3/4 | 모서리 기준 2점 투시, 눈높이, 전경 조경 | 포트폴리오 첫 장 |
| 정면 입면 | 정면 1점, 좌우 대칭 가까움, 수평선 중간 | 매스 구성 읽기 |
| 디테일 | 망원 압축, 재료·창 하나·캔틸레버 밑면 | 하늘 일부만 |
| 드론/황혼 | 블루아워·노을, 실내외 조명 켜짐, 도시 맥락 넓게 | 수평 유지, 하늘 분홍→청색 |

황혼 컷: 하늘은 마젠타·분홍→짙은 파랑, 건물 조명·조형물 업라이트가 켜지고, 물면·바닥에 반사. 해 진 직후 실외 밝기와 실내 조명이 비슷한 '매직아워' 노출.

## 8. 합성(현장 사진 + 건물)일 때 추가 규칙
- 배경 사진의 해 방향·그림자 길이·하늘 색을 **먼저 읽고** 건물 빛을 그쪽에 맞춘다(건물만 다른 시간대면 즉시 합성티).
- 건물 밑선은 지면과 접지 그림자·AO 로 붙이고, 유리에는 **배경 사진의 실제 하늘과 이웃 건물**이 비친다.
- 배경 사진이 시프트 보정이 안 돼 수직이 모이면, 배경을 먼저 수직 보정(키스톤)하고 건물을 얹는다 — 건물만 수직이면 둘이 어긋난다.
- 검수: ① `check_verticals.py` VERT_OK ② 그림자 방향 하나(건물·나무·차) ③ 유리 반사가 배경 하늘색과 같은 계열 ④ 원본 50% 오버레이로 매스·개구부 위치 그대로.

## GPT 경로 프롬프트 블록 (긍정형, 13단계 PROMPT 의 12단계에 넣는다)
`Photograph it like a professional Korean architectural photographer documenting a newly completed building: perspective-corrected shift-lens photograph from eye level on a tripod, all verticals perfectly vertical; a clear sunny day with crisp directional side sunlight giving every mass a bright face and a shaded face with sharp cast shadows under cantilevers and balconies; a deep polarized cobalt-blue sky darkening toward the top; clean bright whites with retained highlight detail, neutral slightly cool white balance, natural material colors; edge-to-edge sharpness with high micro-contrast and deep depth of field; brick joints, panel seams, mullions and real building fixtures visible; newly paved stone ground, freshly planted young trees with support stakes, real surrounding buildings and context kept in frame.`

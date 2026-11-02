# 디자인 검수 규칙 (바레이션·발주 원본 공통)

환황해 포럼 2026-10-27 반려("글씨 안짤리게 그리고 좀 멋지게")와 웹 자료를 묶은 것. 납품 전에 렌더(대지 밖까지, 일러 JPEG `artBoardClipping=false`)를 보고 하나씩 대조한다.

## 1. 글자는 절대 안 잘린다
- **판 이음매**: 옥타 판 여러 장으로 세우는 큰 그림(포토존 4m×2 등)은 판 사이 프레임이 지나간다. 글자·로고는 이음매를 넘지 않게 한 판 안에 둔다. 원·물결 같은 그래픽만 이어지게 한다. 대형 백드롭 인쇄 업체들도 "판이 만나는 선에서 글자·로고를 떼라"고 한다(4OVER4).
  - 환황해 포토존: 제목은 왼판 가운데 위(머리 위), 원은 오른판 가운데. `polish()` ①
- **판 끝**: 제목·문구가 대지 밖으로 나가면 잘린다. 예전 파일에 원래 잘려 있던 것(양쪽LED2 아래 제목)도 고친다. 제목만 윗변 기준으로 줄여 판 안 3%에 넣는다. `polish()` ③
  - 카드·인물 사진까지 같이 줄이면 카드에 가려 있던 사진 부분(연단 글씨)이 드러났다. 그래서 제목만 줄인다.
- **안전 여백**: 중요한 글자는 판 끝에서 3~5% 안쪽에 둔다. 가장자리는 프레임·여유에 먹힌다(live area, 4OVER4·롤업 업체 가이드).

## 2. 글자는 깨끗한 바탕 위에
- 진한 원·지도·사진 위에 글자를 얹지 않는다. 바탕과 글자의 대비가 높아야 읽힌다(이벤트 배너 가이드 다수).
- 원을 진하게(메인처럼 100%) 쓰라는 지시와 부딪히면 이 순서로 한다.
  - 먼저 원을 글자 덩어리 옆으로 비킨다.
  - 그래도 판 안에서 못 비키면 원을 판 왼끝에 둔다. 글자와 겹치는 원은 `softenBehindText`가 50%로 낮춘다. `polish()` ②, `CFG.clearText`
- 글자 수는 적게 한다. 한눈에 읽히는 건 5~7단어 정도다(banners.com).

## 2-1. 통일성 — 바탕은 메인비주얼과 같은 색(환황해 = 흰색), 원 진하기 규칙(100% / 글자 뒤 50%)은 모든 판·모든 파일에 같게. 판마다 제각각이면 "통일성이 없어졌다" 반려(2026-10-27).

## 3. 글자 크기는 보는 거리로 정한다
- 3m(10ft)마다 글자 높이 2.5cm(1in)가 최소다(banners.com 등 업계 공통). 무대 LED처럼 15~20m 밖에서 보는 판은 제목 높이 15cm 이상이 기준이다.
- 무대 LED는 굵고 단순한 글꼴을 쓴다. 가는 선·옅은 그라데이션은 조명에 묻힌다(LED 콘텐츠 가이드).

## 4. 발주 라벨
- 판 왼쪽 위에 네 줄로 쓴다: `이름 / 마감(현수막 상하단 바미싱) / WxHmm / 수량ea`.
- 좁은 판은 가장 긴 줄이 판 폭 안에 들도록 글자를 줄인다(최소 18pt). 구역 제목과 겹치면 구역 제목을 라벨 왼쪽으로 비킨다(위로 올리면 윗줄 판을 덮었다).
- LED 화면은 발주가 아니라 라벨을 달지 않는다.

## 5. 색 역할·크기 대비 (전체 디자인 감각)
- 색은 3개로 역할을 정한다: 바탕(넓게) / 주색(제목·원) / 강조색(한 단어·빛, 작게 한 곳에만). 메인비주얼에서 뽑아 모든 판에 같은 역할로.
- 제목은 아주 크게, 보조 글은 아주 작게 — 중간 크기를 늘어놓지 않는다. 보조 글은 여백 쪽에 짧게 모은다.
- 상세·예시 HEX: AUSURA `wiki/playbooks/design-color-sense.md`

## 출처
- 4OVER4, 대형 배너의 이음매와 live area: https://mapp.4over4.com/faqs/signs-banners/what-should-i-know-about-seams-and-live-areas-when-designing-large-banners
- banners.com, 거리별 글자 크기: https://banners.com/c/how-far-away-can-someone-read-a-banner-complete-banner-font-size-guide
- banners.com, 이벤트 배너 디자인 팁: https://www.banners.com/c/event-banner-design-tips
- NMR Events, LED 콘텐츠 원칙: https://nmrevents.com/post/led-content-best-practices
- printsimple, 롤업 안전영역: https://www.printsimple.eu/en/help/design-guidelines-roll-up-banners

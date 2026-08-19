# Vox 스타일 프롬프트 템플릿 (한국어판)

Phase 1과 Phase 3에 들어가는 재료. 모든 프롬프트의 목표는 하나다 —
**모션 디자인된 에디토리얼 콜라주**, 즉 Vox 영상의 시각 문법. 촬영된 장면이
절대 아니다.

> **프롬프트는 영어로 쓴다.** 이미지·영상 모델의 영어 이해도가 압도적으로
> 높다. 한국어 프롬프트는 스타일 준수율이 눈에 띄게 떨어진다. 한국어는
> 나레이션과 자막에만 쓴다.

## 시각 어휘

아래 장치들에서 장면을 뽑는다. 모든 블록은 이 중 두세 개를 조합하되, 그
블록의 나레이션을 문자 그대로 그리도록 고른다.

- **아카이브 컷아웃** — 사람·건물·사물의 사진을 거친 흰 종이 테두리로
  오려낸 것. 플랫한 배경 위를 떠다니거나 탁 하고 제자리에 붙는다. 사진은
  콜라주 *안의* 요소로 존재하고, 프레임 전체가 실사인 적은 없다.
- **플랫 컬러 필드** — 볼드한 에디토리얼 배경: 따뜻한 노랑, 오프화이트 종이,
  딥 네이비, 코랄 레드. 블록당 지배색 하나, 영상 전체에 일관된 액센트 팔레트.
- **종이·인쇄 질감** — 그레인, 하프톤 도트, 신문지, 찢긴 가장자리, 테이프
  조각, "오려 붙인" 느낌을 파는 은은한 드롭섀도.
- **손그림 주석** — 컷아웃 주위로 스스로 그려지는 마커 동그라미, 쓸고 들어오는
  밑줄, 요소를 잇는 화살표, 휘갈긴 강조 획. (추상 획만 — 글자·단어 절대 금지.)
- **추상 데이터 그래픽** — 자라나는 막대, 스스로 그려져 올라가는 선그래프,
  갈라지는 파이 조각. 라벨 없이 — 순수한 형태와 움직임, 숫자 없음, 축 텍스트
  없음.
- **지도** — 애니메이션 경로가 있는 플랫한 스타일라이즈드 지도, 맥동하는 위치
  점, 색으로 채워지는 지역.
- **먹칠·하이라이트 블록** — 영역 위로 미끄러지는 단색 바, 컷아웃 하나만
  남기고 나머지를 어둡게 하는 스포트라이트 비네트.
- **스케일 비교** — 사물 하나가 줄지어 증식, 작은 컷아웃 옆에 우뚝 선 큰 것,
  쌓여 올라가는 더미.

### 한국 소재를 다룰 때

- 한글 간판·현판·문서가 들어가는 장면은 **글자가 깨진다.** 한국적 소재는
  글자 없는 요소로 표현한다: 기와 지붕 실루엣, 한반도 지도 형태, 전통 문양의
  기하학적 추상화, 아파트 단지 실루엣.
- 특정 기업 로고·브랜드 간판은 넣지 않는다(저작권 + 렌더링 품질 양쪽 문제).
- 실존 정치인·공인 얼굴은 피하고, 필요하면 검열바·하프톤으로 처리한다.

## 모션 어휘

Vox 모션은 스냅하고 의도적이다: 빠른 이즈아웃 등장, 살짝 오버슛하며 미끄러져
들어오거나 팝 하고 붙는 요소들, "이거 들어보세요" 비트에서의 느리고 의도적인
카메라 푸시인, 아이디어 사이의 휩팬이나 페이지 넘김, 콜라주 레이어 간 패럴랙스
드리프트. 항상 뭔가 움직이되, **한 번에 하나만 시끄러워야** 한다.

## STYLE KEY 프롬프트 (16:9 기본 경로)

`generate_image`, 모델 `nano_banana_pro`, `aspect_ratio: "16:9"`로 사용:

```
Editorial mixed-media collage style swatch, Vox-documentary motion graphics
aesthetic: flat warm yellow and off-white paper background with halftone dot
texture, archival photo cutouts with rough white paper borders, torn paper
edges and tape strips, hand-drawn black marker circles and arrows, bold flat
color blocks in navy and coral, subtle paper grain and drop shadows.
Abstract composition only — no characters, no objects with faces, no
letters, no words, no numbers, no Korean characters, no Hangul.
Non-photorealistic, no live-action, no realism, no 3D render.
```

9:16 요청 시에는 이 프롬프트 대신 프리셋
`80e4dd7b-cd65-42d4-b191-b58d62558602`을 `resolve_explainer_preset`으로
해석해 쓴다(무료).

## STYLE 토큰 (모든 블록 프롬프트의 STYLE REFERENCE 줄에 들어감)

```
editorial mixed-media collage, archival photo cutouts with white paper
borders, flat bold color fields, halftone and paper grain textures,
hand-drawn marker annotations, snappy motion-graphics animation,
non-photorealistic, no live-action
```

## 블록 프롬프트 템플릿

블록당 하나, 라벨 붙이고, 타임코드 없이:

```
Block {N}
STYLE REFERENCE: Match the attached style key EXACTLY — {STYLE 토큰}.
SCENE: {이 블록의 나레이션을 그리는 콜라주 구성: 어떤 컷아웃, 어떤 컬러 필드,
어떤 주석/차트/지도}. Composition: keep the lower ~17% of the frame visually
quiet — background texture only, no key subject in that band.
MOTION: {등장 안무 + 카메라 무브 + 샷 동안 무엇이 애니메이트되는지}.
AUDIO: {앰비언스 베드 + 종이/휘익/틱 SFX 한두 개 — 목소리 없음, 나레이션 없음}.
NEGATIVE: readable text, letters, words, numbers, Korean characters, Hangul,
Chinese characters, Japanese kana, garbled lettering, captions, subtitles,
watermark, logo, signage, storefront signs, document text, newspaper headlines,
photorealism, live-action footage, 3D render, lip-sync, talking characters,
color drift.
```

NEGATIVE 줄은 고정이다 — 모든 블록에 그대로 복사한다. 원본 영어판보다 항목이
길어진 이유는 한글·한자·가나 렌더링과 간판·문서 텍스트를 명시적으로 막기
위해서다. SCENE은 나레이션이 말하는 *아이디어*를 시각화해야지, 누가 그걸
말하는 장면을 그리면 안 된다.

## 작업 예시

나레이션 (블록 1): *"사람들은 매일 이십억 명을 먹일 수 있는 음식을 버립니다.
그리고 그 대부분은 식탁에 오르지도 못합니다."*

```
Block 1
STYLE REFERENCE: Match the attached style key EXACTLY — editorial mixed-media
collage, archival photo cutouts with white paper borders, flat bold color
fields, halftone and paper grain textures, hand-drawn marker annotations,
snappy motion-graphics animation, non-photorealistic, no live-action.
SCENE: A warm yellow paper background with halftone texture. Photo cutouts of
apples, bread loaves and a full dinner plate snap into a neat grid in the upper
two-thirds, then one by one flip over and tumble downward into a torn-paper
"bin" shape. A thick black marker circle draws itself around the last remaining
plate. Composition: keep the lower ~17% of the frame visually quiet —
background paper texture only, no cutouts or strokes in that band.
MOTION: Cutouts pop in with slight overshoot in quick succession; slow camera
push-in as they begin tumbling; the marker circle draws in one confident
stroke at the end.
AUDIO: Soft paper rustles and quick whoosh ticks as cutouts flip and fall,
low minimal ambient pulse underneath — no voice, no narration.
NEGATIVE: readable text, letters, words, numbers, Korean characters, Hangul,
Chinese characters, Japanese kana, garbled lettering, captions, subtitles,
watermark, logo, signage, storefront signs, document text, newspaper headlines,
photorealism, live-action footage, 3D render, lip-sync, talking characters,
color drift.
```

나레이션 (중반 근거 블록): *"천구백칠십 년에는 컨테이너 하나를 바다 건너
보내는 데 지금의 열 배가 들었습니다. 그다음 이 상자가 세상을 먹었죠."*

```
Block 4
STYLE REFERENCE: Match the attached style key EXACTLY — editorial mixed-media
collage, archival photo cutouts with white paper borders, flat bold color
fields, halftone and paper grain textures, hand-drawn marker annotations,
snappy motion-graphics animation, non-photorealistic, no live-action.
SCENE: Deep navy background. A stylized flat world map slides up into the
upper half; a coral dotted route draws itself across the ocean between two
pulsing dots. An archival photo cutout of a cargo ship rides along the route
while an abstract bar chart on the right shrinks step by step, its tallest bar
collapsing to a stub. Torn-paper container shapes multiply into a growing
stack at mid-frame. Composition: keep the lower ~17% of the frame visually
quiet — flat navy only, no map edge, no bars, no stack in that band.
MOTION: Map slides in with ease-out; route line draws left to right; camera
drifts laterally following the ship; bars shrink with snappy steps; container
stack builds with rhythmic pops.
AUDIO: Low ambient hum, soft tick per bar step, gentle ocean-paper whoosh —
no voice, no narration.
NEGATIVE: readable text, letters, words, numbers, Korean characters, Hangul,
Chinese characters, Japanese kana, garbled lettering, captions, subtitles,
watermark, logo, signage, storefront signs, document text, newspaper headlines,
photorealism, live-action footage, 3D render, lip-sync, talking characters,
color drift.
```

## 대본 예시 (구조 참고, 6블록 = 1분)

주제: "음식물 쓰레기는 사실 물류 이야기다"

```
Block 1  사람들은 매일 이십억 명을 먹일 수 있는 음식을 버립니다. 그리고 그
         대부분은 식탁에 오르지도 못합니다.
Block 2  우리는 입 짧은 사람과 꽉 찬 냉장고를 탓하죠. 그런데 가장 큰 손실은
         음식이 우리 눈에 보이기 한참 전에 일어납니다.
Block 3  가난한 나라에서는 폐기의 사십 퍼센트 가까이가 농장에서 발생합니다.
         오지 않는 트럭을 기다리다 작물이 썩는 겁니다.
Block 4  부유한 나라는 문제를 뒤집었습니다. 음식은 운송을 버텨내고, 대신
         완벽한 겉모습을 좇는 마트 진열대에서 죽습니다.
Block 5  그런데 진짜는 따로 있습니다. 트럭과 냉장 설비를 고치는 편이 모든
         가정 캠페인을 합친 것보다 폐기를 더 줄입니다.
Block 6  그러니까 음식물 쓰레기와의 싸움은 여러분 부엌에 있지 않습니다.
         저녁거리를 세계로 실어 나르는, 그 지루한 기계 장치 안에 있습니다.
```

형태를 보라: 콜드오픈 통계 → 판돈 → 근거 두 비트 → 전환 → 블록 1을 다시
정의하는 킬러. 각 줄은 아이디어 하나, **40~50 음절**, 숫자는 읽는 대로,
군더더기 없음.

### 한국어 분량 감각

위 예시 블록들의 음절 수를 세어보면 대략 45~55음절이다. 한국어 다큐
나레이션은 초당 약 5음절이 대략의 감이지만, **TTS 실측 전까지 믿지 않는다.**
첫 블록을 뽑아 `durationSec`을 읽고 실제 음절/초를 계산한 뒤 나머지를 보정한다.

주의할 페이싱 함정:
- 마침표가 많을수록 길어진다. 위 블록 2는 문장이 둘이라 블록 6보다 길게
  나올 수 있다.
- 쉼표로 이은 한 문장이 가장 예측 가능하다.
- 숫자·약어는 읽는 대로 적는다: `40%` → `사십 퍼센트`, `1970년` →
  `천구백칠십 년`.

# 조명 레이어 세트 (LIGHT LAYER / 4분리) — 포토샵 개별 컨트롤용

> 2026-07-27 SKILL.md 재작성 때 누락된 절을 복원(원본: 2026-07-13본).
> `person-layer-maker`의 「조명 샌드위치」(L1 빔·L2 헤이즈는 인물 위, L3 스팟 풀·L4 컬러 워시는 인물 아래)가
> 이 문서의 L1~L4를 그대로 참조한다 — 둘은 같이 움직인다.
> SKILL.md 본문의 「빛 전용 플레이트 절대 출력 계약」은 단일 플레이트 규격이고,
> 이 문서는 그 플레이트를 4성분으로 쪼개 각각 따로 생성할 때만 적용한다.

## 조명 레이어 프롬프트 (포토샵 합성용)

### 개념

순수 블랙 배경 위에 **빛 효과만** 렌더링한 이미지를 생성한다.
포토샵에서 원본 이미지 위에 올리고 블렌딩 모드를 적용하면 조명을 독립적으로 제어할 수 있다.

```
포토샵 합성 방법:
레이어 순서: [조명 레이어] → 블렌딩 모드: Screen 또는 Linear Dodge(Add)
             [원본 이미지]
→ 불투명도로 조명 강도 조절
→ 레이어 마스크로 원하는 영역만 적용
→ 색조/채도로 조명 색상 독립 보정
```

### LIGHT LAYER PROMPT 작성 원칙

조명 레이어는 메인 변환 프롬프트와 달리 **공간 구조를 묘사하지 않는다.**
오직 아래 5가지 빛 요소만 묘사한다:

1. **볼류메트릭 빔** — 천장/측면에서 내려오는 빛줄기 형태와 방향
2. **헤이즈·먼지 입자** — 빔 안에 떠다니는 미세 입자
3. **스파클·글린트** — 공중에 흩어진 빛 반짝임
4. **앰비언트 글로우** — 빔 주변의 부드러운 후광
5. **색온도** — 빔과 글로우의 색상

공간·재료·가구·텍스트·사람 묘사는 일절 하지 않는다.

### LIGHT LAYER PROMPT 작성 순서

아래 6개 블록을 순서대로 이어 붙여 하나의 연속된 영어 단락을 만든다.
괄호 설명은 작성 가이드이며 출력에 포함하지 않는다.

**① 블랙 배경 선언 (항상 고정)**
> `"Pure solid black background. Complete darkness as the base. No room, no architecture, no surfaces, no objects, no floor, no ceiling, no walls — only pure black void."`

**② 비율 — 생성 설정으로 지정 (프롬프트 문장이 아니라 파라미터로)**
조명 레이어는 txt2img라 Image 1이 엔진에 첨부되지 않는다 — 프롬프트로 "Image 1과 같은 비율"을 요구해도 수행 불가. **생성 파라미터(사이즈/종횡비)를 합성 대상 원본과 동일하게 설정하라고 사용자에게 1줄 안내**하고, 프롬프트에는 Image 1 참조를 넣지 않는다. Image 1 자체가 없는 실행(조명 레이어 단독 요청)이면 사용자가 원하는 출력 크기(Width/Height)를 직접 지정하도록 안내한다. (합성 시 정렬은 포토샵에서 캔버스 크기로 맞춘다.)

**③ 빔 묘사 — Image 2 패턴 반영**
Image 2의 빔 패턴·광원 위치 읽은 뒤 묘사. 아래 색온도별 템플릿 참조.

**④ 입자·헤이즈 (항상 고정)**
> `"Subtle floating dust particles and atmospheric haze suspended within and around the light beams, creating depth and three-dimensional volumetric presence."`

**⑤ 스파클·글린트 (항상 고정)**
> `"Refined sparkling light particles and soft glinting highlights scattered within the illuminated beam zones, delicate and organic without overexposure or neon quality."`

**⑥ 기술 선언 (항상 고정)**
> `"Pure light art, photorealistic light physics, high dynamic range, deep pure black surrounding areas with no grey or noise, bright luminous beams with natural falloff and soft edge gradients. No room, no architecture, no objects, no text, no watermark, no people. Compositing-ready light layer on pure black background."`

### 색온도별 빔·글로우 묘사

**Cool Blue 레이어:**
> `"Multiple dramatic volumetric light beams in deep cool blue and crisp cold white, radiating downward and crossing from upper positions. Icy blue atmospheric glow surrounding the beam edges. Silver-white beam cores with blue-tinted penumbra and cool cyan ambient scatter."`

**Warm Amber 레이어:**
> `"Multiple dramatic volumetric light beams in rich warm amber and deep gold, radiating downward and crossing from upper positions. Golden atmospheric glow surrounding the beam edges. Bright warm white beam cores with amber-tinted penumbra and golden ambient scatter."`

**Mixed 레이어:**
> `"Multiple dramatic volumetric light beams — dominant cool blue and cold white primary beams from upper center, with warm amber and gold secondary accent beams from side angles. Blue-silver atmospheric glow on primary beams, warm golden glow on accent beams, creating layered mixed-temperature light atmosphere."`

**Neutral Cinematic 레이어:**
> `"Multiple dramatic volumetric light beams in neutral cool white with subtle silver undertones, radiating from upper positions. Refined neutral atmospheric glow surrounding beam edges. Clean white beam cores with slightly cool-toned penumbra and minimal ambient scatter."`

### LIGHT LAYER NEGATIVE (항상 동일)

```
LIGHT LAYER NEGATIVE (SD/MJ/ComfyUI 전용 — GPT image·Magnific/nanobanana에는 입력하지 않음)
room, architecture, walls, ceiling, floor, furniture, objects, people, faces,
background elements, interior space, outdoor scene, any solid surface,
grey background, white background, colored background, gradient background,
noise in dark areas, grain in shadows, visible texture in black areas,
text, watermark, logo, signage, labels, readable letters,
neon lights, LED strips, lens flares, chromatic aberration, lens artifacts,
overexposed blown areas, clipped highlights, flat even glow, studio light look,
illustration, cartoon, painted look, digital art style, fantasy glow, magical sparkles,
colored smoke, fog machine look, dry ice effect, unrealistic physics
```

**Image 2 없는 경우 (레퍼런스 없이 조명 레이어만 요청):**
빔 패턴은 Neutral Cinematic 기본값으로 — 천장 중앙 3-5개 수직 다운라이트 빔,
좌우 사이드에서 약한 교차 보조 빔, 전체 Neutral Cool White 색온도.
프롬프트에 "the reference image" 같은 참조 문구를 넣지 않는다(txt2img에는 레퍼런스가 첨부되지 않음 — 유령 참조 금지). 빔 형태를 직접 묘사한다.

**GPT image 경로 분기:** LIGHT LAYER NEGATIVE를 출력은 하되 입력에 사용하지 않고, 블록 ①·⑥의 부정문(`No room, no architecture...`)을 긍정형으로 바꾼다 —
- ① 대체: `"The entire frame is a pure black void in which volumetric light beams are the only visible content."`
- ⑥ 대체: `"Pure light art on a pure black background, photorealistic light physics, high dynamic range, deep pure black surroundings, bright luminous beams with natural falloff and soft edge gradients — a compositing-ready light layer."`

---

## 조명 레이어 세트 (LAYER SET — 포토샵 개별 컨트롤용 4분리) ★

### 개념
조명 레이어 1장은 빔·헤이즈·스팟·워시가 한 덩어리라 "빔만 줄이고 헤이즈만 키우기"가 불가능하다. **레이어 세트 모드는 조명을 4개 성분으로 분리 생성**해 포토샵에서 각각 불투명도·색조·마스크로 따로 컨트롤한다 — 한 번에 나온 결과를 수정 못 해 버리는 일을 없앤다.

> **오픈소스 대안 — IC-Light**: 베이스 조명(전역 조명감·색광·방향)은 IC-Light(무료·MIT, SD 기반 relight)로 재조명 보정하고, 포토샵 레이어(L1~L4)는 빔·하이라이트 **미세보정만** 맡기면 레이어 수를 크게 줄일 수 있다. 이 스킬의 조명 레이어 분리 합성과 **같은 광원 중첩(독립성) 물리 직관에서 출발하지만 구현은 다르다** — IC-Light는 신경망 추론이라 결과가 편집 가능한 조명 레이어가 아니라 **구워진 재조명 이미지**로 나온다. 디테일 그림자 마스킹도 불완전하므로 베이스 조명 전용 — 완전 대체가 아니다.

각 레이어는 위 "LIGHT LAYER PROMPT 작성 순서"의 블록 ①(블랙 배경)·②(비율=생성 파라미터)·④·⑤·⑥ 규칙을 그대로 상속하고, **③(빔 묘사) 자리만 아래 성분별 묘사로 바꾼다.** 색온도는 판단표의 모드를 4장 모두 동일하게 적용(혼합 모드면 빔=주색, 워시=보조색 배분 가능).

### 4분리 성분 (각각 별도 생성 = 별도 프롬프트 출력)

| # | 레이어 | ③ 자리 묘사 | 블렌드/불투명도 시작값 |
|---|---|---|---|
| L1 | **빔 (BEAM)** | `"only sharp well-defined volumetric light beams with natural falloff and non-clipping brightness, crisp edges, minimal ambient glow around them"` (빔 코어를 순백으로 만들지 않는다) | Screen 또는 Linear Dodge(Add), **40~70%** — 하이라이트가 날아가면 하향 |
| L2 | **헤이즈 (HAZE)** | `"only soft atmospheric haze glow filling the beam paths and upper air, with light haze / medium haze / heavy haze density, without any defined beam edges"` (농도 1개 선택) | Screen, 30~60% |
| L3 | **스팟 풀 (SPOT POOL)** | `"only soft elliptical light pools on the floor and subject positions where the spotlights land, gentle hotspot centers with natural falloff, without visible beams in the air"` | Screen, 50~80% |
| L4 | **컬러 워시 (COLOR WASH)** | `"only a broad smooth color wash gradient as if colored stage light washing across walls and surfaces, soft and even, without beams, pools, or particles"` | **블랙 배경 규격이면 Screen 20~40%.** Soft Light/Color는 레이어를 50% 그레이 기반으로 만들었을 때만 20~50% (블랙 배경에 Soft Light를 걸면 검정 영역이 화면을 어둡게 만든다) |

> 모든 블렌드 값은 **시작값**이다 — 결과를 보고 레이어별 불투명도로 조정하는 것이 이 모드의 존재 이유다.

### 출력 형식 (레이어 세트 요청 시)
```
LIGHT LAYER SET — 생성 파라미터: 사이즈/종횡비를 합성 대상 원본과 동일하게 설정
L1 BEAM PROMPT
[연속 영어 단락]
L2 HAZE PROMPT
[연속 영어 단락]
L3 SPOT POOL PROMPT
[연속 영어 단락]
L4 COLOR WASH PROMPT
[연속 영어 단락]
블렌드 가이드(시작값): L1 Screen/Linear Dodge 40~70% · L2 Screen 30~60% · L3 Screen 50~80% · L4 Screen 20~40%(50% 그레이 기반 제작 시 Soft Light 20~50%) — 각 레이어 불투명도로 조절
```
- LIGHT LAYER NEGATIVE는 4장 공통으로 1회만 출력(기존 "항상 동일" 블록). GPT 경로면 생략+긍정형 전환(위 분기 규칙 동일).
- 필요 없는 성분은 생성하지 않아도 된다(예: 워시 없는 조명이면 L4 생략) — 어떤 성분을 쓸지는 Image 2 분석으로 판단해 명시한다.

### 인물·레이어 합성 파이프라인 연계 (조명 샌드위치)
사람을 넣으려면 **person-layer-maker** 스킬로 인물을 별도 레이어로 생성하고, 조명은 인물을 사이에 두고 나눠 얹는다 — **바닥·벽에 깔리는 빛(L3 스팟 풀·L4 워시)은 인물 아래, 공기 중의 빛(L1 빔·L2 헤이즈)은 인물 위**. 인물이 빔을 자연스럽게 가로막아 입체감이 생기고 인물 발광을 막는다. 표준 레이어 순서: 베이스 → 반사 → L3·L4 → 인물 그림자 → 인물(+클리핑 색보정) → L1 빔 → L2 헤이즈 → 통합 그레인(맨 위 1회).

---


### 조명 레이어 예시 — Mixed (Cool Blue + Warm Amber) / 컨퍼런스홀 기준

포토샵 합성용. 이 이미지를 원본 위에 올리고 **Screen** 또는 **Linear Dodge(Add)** 모드 적용.
생성 시 **사이즈/종횡비 파라미터를 Image 1과 동일하게 설정**한다 (프롬프트가 아니라 생성 설정에서).

```
LIGHT LAYER PROMPT
Pure solid black background. Complete darkness as the base. No room, no architecture, no surfaces, no objects, no floor, no ceiling, no walls — only pure black void. Multiple dramatic volumetric light beams radiating downward and crossing in a wide symmetrical fan pattern from upper center positions. Primary beams descend from the top-center area spreading outward in a symmetrical fan formation, with secondary crossing diagonal beams from upper-left and upper-right angles meeting near the center-lower zone. Subtle floating dust particles and atmospheric haze suspended within and around the light beams, creating depth and three-dimensional volumetric presence. Refined sparkling light particles and soft glinting highlights scattered within the illuminated beam zones, delicate and organic without overexposure or neon quality. Dominant cool blue and cold white primary beams from upper center, with warm amber and deep gold secondary accent beams from side angles. Blue-silver atmospheric glow surrounding the primary beam edges, warm golden glow around accent beams, creating layered mixed-temperature light atmosphere. Pure light art, photorealistic light physics, high dynamic range, deep pure black surrounding areas with no grey or noise, bright luminous beams with natural falloff and soft edge gradients. No room, no architecture, no objects, no text, no watermark, no people. Compositing-ready light layer on pure black background.

LIGHT LAYER NEGATIVE (SD/MJ/ComfyUI 전용 — GPT image·Magnific/nanobanana에는 입력하지 않음)
room, architecture, walls, ceiling, floor, furniture, objects, people, faces, background elements, interior space, outdoor scene, any solid surface, grey background, white background, colored background, gradient background, noise in dark areas, grain in shadows, visible texture in black areas, text, watermark, logo, signage, labels, readable letters, neon lights, LED strips, lens flares, chromatic aberration, lens artifacts, overexposed blown areas, clipped highlights, flat even glow, studio light look, illustration, cartoon, painted look, digital art style, fantasy glow, magical sparkles, colored smoke, fog machine look, dry ice effect, unrealistic physics
```

---


---
name: magnific-compositing-prep
description: "포토샵 3D 오브젝트 합성을 위해 실내 배경 이미지를 Magnific nanobanana 업스케일 전처리용 프롬프트로 변환하는 스킬. 수직/수평 왜곡 최소화, 소실점 정확도 유지, 합성 친화적 배경이 핵심. '마그네픽 프롬프트', '합성 배경', '3D 합성용', '합성할 배경', '수직 수평 맞게', '합성용 업스케일' — 이 중 하나라도 나오면 반드시 이 스킬을 사용한다. '나노바나나'·'업스케일 프롬프트'는 단독으로는 발동하지 않는다 — 합성/업스케일 전처리 문맥이 함께 있을 때만 이 스킬이다(나노바나나 단독 이미지 생성 요청, 실사화 결과물의 단순 업스케일 설정 문의는 해당 스킬이 담당: 심리스 텍스처 목적이면 texture-prompt-maker, 실사화 업스케일 설정은 interior/arch 스킬의 엔진 선택 절). 이미지가 없어도 공간 설명만으로 실행 가능. interior-prompt-maker(CGI→실사화)·cinematic-exhibition-lighting(조명 전환)과 목적이 다르다 — 이 스킬은 합성 배경의 기하학 정확도 확보가 목적이다."
---

# Magnific Compositing Prep 프롬프트 메이커

포토샵 3D 합성 배경을 Magnific nanobanana 4x로 업스케일하기 위한 전처리 프롬프트 생성.
수직/수평 라인과 소실점 보존이 최우선이며, 새로운 왜곡·오브젝트 추가를 원천 차단한다.

> 용어: 여기서 "nanobanana"는 **Magnific 업스케일러의 nanobanana 엔진 프리셋**을 뜻한다(원래 nano-banana는 Google Gemini 계열 이미지 모델의 별칭 — 공식명 Gemini Flash Image). SETTINGS(Creativity/Resemblance/Detail/HDR)는 Magnific UI 슬라이더 값이며 Google Gemini API 파라미터가 아니다.

## 처리 순서

1. **소스 판별** — 실사진 / CGI 렌더 구분
2. **고유 요소 추출** — 브랜드·로고 / 특징 재료·패턴 / 핵심 구조물
3. **공간 유형 파악** — 아래 목록에서 매칭
4. **PROMPT + SETTINGS + NEGATIVE(SD 대체 경로 전용) 세 섹션을 항상 이 구성으로 출력** — 설명·분석·체크리스트 없음. NEGATIVE 섹션 제목은 반드시 `NEGATIVE (SD/ComfyUI 대체 경로 전용 — Magnific/nanobanana에는 입력하지 않음)`으로 표기해 사용처 혼동을 차단한다

**절대 금지:** 카메라 브랜드(Sony, Canon, Nikon, Hasselblad 등) / MJ 파라미터(`--v`, `--ar` 등) / 절대 초점거리 mm 숫자

**NEGATIVE 사용처 (결정 규칙):** Magnific/nanobanana 실행 시 입력하는 것은 **PROMPT + SETTINGS 뿐**이다. NEGATIVE를 프롬프트에 이어붙이지 않는다 — 의미기반 엔진(nanobanana)은 부정 나열을 장면 묘사로 읽어 역효과를 내고, Magnific UI에는 NEGATIVE 전용 필드가 없다. PROMPT의 긍정형 기하학 잠금(`perfect rectilinear perspective, straight parallel lines` 등)이 억제를 대신한다. NEGATIVE 섹션은 **SD/ComfyUI 계열로 대체 실행할 때만** 그 negative 필드에 넣는 참고용이며, 출력 시 섹션 제목에 이를 명기한다.

---

## 소스 판별

**사용자가 직접 말하면** → 우선 적용
("실사야", "CGI야", "D5", "Lumion", "SketchUp", "렌더야" 등)

**CGI 렌더 소프트웨어 키워드 감지 → 즉시 CGI 처리:**
D5 Render, Lumion, SketchUp, Rhino, Revit, ArchiCAD, 3ds Max, Blender, Enscape,
V-Ray, Corona Renderer, Twinmotion, KeyShot, Cinema 4D

**이미지/설명에서 판단:**

| 실사진 신호 | CGI 렌더 신호 |
|---|---|
| 자연 노이즈·그레인 | 노이즈 없는 완벽한 텍스처 |
| 불균일한 조명·그림자 | 균일하고 이상적인 조명 |
| 소재 노화·먼지·지문 | 플라스틱처럼 매끈한 표면 |
| 생활 오브젝트·사람 | 렌더 아티팩트·ambient occlusion banding |

판단 불가 → CGI 렌더로 처리 (안전한 기본값)

---

## A. 실사진용

**목표:** 기존 기하학·텍스처를 100% 보존. 새로운 grain·aging·object 추가를 원천 차단.
4x 업스케일에서 Magnific이 빈 공간에 오브젝트를 hallucinate하지 않도록 NEGATIVE가 핵심.

### PROMPT

```
real interior photograph upscale, perfect rectilinear perspective,
plumb vertical walls, level horizontal ceiling and floor planes,
accurate vanishing points preserved, straight parallel lines throughout,
compositing-ready background plate, enhance sharpness and material clarity only,
no structural or spatial alteration, preserve all existing surfaces as-is
```

고유 요소 추가 (PROMPT 끝, 개수 제한 없음):
`preserve [위치 포함 구체 설명] exactly as in the original`

### NEGATIVE

```
barrel distortion, pincushion distortion, fisheye, curved walls, warped geometry,
bent vertical lines, tilted horizon, perspective warp, lens aberration,
added film grain, artificial noise, vignette, hallucinated texture,
artificial aging, new stains or marks, changed room geometry,
new furniture added, objects moved or removed, hallucinated objects,
new architectural elements, reframed composition, style change,
dreamlike, painterly, illustration
```

### SETTINGS (nanobanana 4x 기준)

```
Creativity : 0.1
Resemblance: 0.95
Detail     : 0.35
HDR        : 0.1
```

**Detail 조정:** 거친 재료(벽돌·콘크리트·카펫) → 0.45 / 매끈한 재료(대리석·도장벽) → 0.25
**Resemblance 조정:** 로고·사이니지 등 정밀 보존 필요 시 → 1.0

---

## B. CGI 렌더용

**목표:** CGI의 플라스틱 같은 완벽함을 실사 소재감으로 전환하되 기하학은 절대 유지.
소재 전환(Creativity ↑)을 허용하면서도 수직·수평 라인이 흔들리지 않게 기하학 키워드를 먼저 배치.

### PROMPT

```
convert CGI render to photorealistic interior photograph,
strict rectilinear geometry lock — plumb verticals, level horizontals,
accurate vanishing points unchanged, no perspective shift,
photorealistic material quality, realistic surface micro-texture,
subtle material imperfection and aging, photographic light response on surfaces,
compositing-ready photorealistic background, professional architectural photography
```

공간 유형 키워드 추가 (아래 섹션에서 선택)

고유 요소 추가 (PROMPT 끝):
`preserve [위치 포함 구체 설명] exactly as in the original`

### NEGATIVE

```
CGI look, plastic material, uniform synthetic texture, oversaturated colors,
perfectly clean non-aging surfaces, barrel distortion, pincushion distortion,
fisheye, curved walls, warped geometry, bent vertical lines,
perspective shift, lens aberration, render artifact, ambient occlusion banding,
new furniture added, objects moved, hallucinated objects,
new architectural elements, toon shading, illustration, cartoon, added film grain
```

### SETTINGS (nanobanana 4x 기준)

```
Creativity : 0.3
Resemblance: 0.80
Detail     : 0.5
HDR        : 0.2
```

**Creativity 조정:**
- 텍스처가 단순한 공간(흰 벽 오피스, 미니멀 로비) → 0.2
- 복잡한 소재가 많은 공간(연회장, 카페, 레스토랑) → 0.4 (최대)
- Creativity > 0.4는 기하학 변형 위험 — 절대 초과하지 않는다

**Detail 조정:**
- 거친 재료(카펫·벽돌·콘크리트) → 0.6
- 매끈한 재료(대리석·유리·도장면) → 0.4

---

## 공간별 재료 키워드 (CGI 렌더 전용)

PROMPT 핵심 구성 뒤에 해당 공간 블록을 이어 붙인다.

### 호텔 연회장 / 이벤트홀 / 컨퍼런스홀
```
patterned carpet pile variation and weave texture,
dark upholstered chair fabric tension and fold,
acoustic wall panel micro-texture and mounting depth,
warm LED track spotlight falloff and shadow definition,
projection screen matte surface, polished stage floor reflection gradient
```

### 오피스 / 회의실
```
acoustic ceiling tile depth and grid shadow,
carpet tile seam and wear variation,
glass partition fingerprint and reflection depth,
desk surface material weight, diffuse task lighting softness
```

### 호텔 로비 / 고급 상업 공간
```
large format stone floor mineral variation and joint depth,
marble polished reflection gradient,
metal trim anisotropic specular, reception desk material weight,
lobby glazing system depth and mullion shadow
```

### 상업 쇼룸 / 전시 공간
```
polished or honed floor surface reflectivity,
display shelf and case material edge detail,
neutral wall matte surface, focused spotlight circle definition,
product surface micro-texture contrast
```

### 주거 거실 / 침실
```
wood flooring grain variation and plank seam,
upholstered sofa fabric compression and weave,
matte painted wall subtle surface variation,
curtain fabric translucency and fold
```

### 카페 / 레스토랑
```
table surface material scratch and variation,
upholstery weave and seam detail,
ceramic or stone tile grout line depth,
warm pendant light glow falloff, bar counter edge and material weight
```

### 전시관 / 갤러리
```
polished concrete or hardwood reflectivity and seam,
white plaster wall micro-texture, track light directional definition,
artwork frame edge and glass reflection, neutral ambient balance
```

### 의료 / 교육 공간
```
vinyl or terrazzo floor pattern and seam,
acoustic panel perforation depth, diffuse ceiling panel even glow,
matte wall paint subtle variation, handrail metal surface detail
```

### 전시부스 / 전시홀 (3종: 목공 · 블럭 · 옥타놈)
```
anodized aluminum post and beam edge specular highlight, panel-to-panel seam depth,
matte white melamine or PVC infill panel surface, fascia header band flatness,
grey needle-punch exhibition carpet pile, aluminum base rail edge,
overhead truss and spotlight specular, straight vertical frame lines preserved
```
유형별 추가(원본이 어느 부스인지에 맞춰 한 줄 선택):
- 목공부스: `smooth continuous painted or vinyl-wrapped wall surface, sharp clean flush corner, solid built wall`
- 블럭부스: `standardized rectangular box modules, fine consistent seams between modules, flat even matte panel faces` (발광은 원본 그래픽면에 있을 때만 국소적으로, 벽 전체 발광 금지)
- 그래픽 재료(원본에 보이는 1~2종만): `flat tight self-adhesive vinyl film (kelji) wrapped on wall, taut smooth SEG tension fabric matte surface, satin PVC flex banner, matte foam PVC board`
> 3종 공통으로 수직/수평 직선 보존이 생명이다. CGI 소스면 Creativity를 더 낮게(0.1~0.2) 잡아 격자·모서리 왜곡을 막는다. 옥타놈은 포스트가 패널보다 볼록 돌출된 seam을, 블럭부스는 균일한 박스 모듈 접합 그리드를, 목공은 이음매 없는 매끈면을 유지시킨다. 발광·광택 토큰을 여럿 겹치면 전면발광·bloom이 나므로 주 재료 1개에만 적용한다.

### 목록에 없는 공간 (fallback)
위 목록에 없는 공간(체육관, 종교시설, 공장 내부, 지하주차장 등)은 키워드 블록을 생략하거나 임의 창작하지 말고, **가장 유사한 블록을 선택**하거나 그 공간의 **바닥·벽·천장·조명 4요소**를 같은 형식(재료명 + micro-texture/seam/falloff 패턴)으로 직접 작성한다.

---

## 고유 요소 보존

이미지 설명에서 아래 요소가 감지되면 반드시 PROMPT 끝에 추가한다.
**위치를 구체적으로 명시**해야 Magnific이 어디를 건드리지 말아야 하는지 인식한다.

| 요소 유형 | 작성 예시 |
|---|---|
| 브랜드 로고 | `preserve the Fairmont logo on the rear LED screen exactly` |
| 카펫·타일 패턴 | `preserve the floral patterned carpet color and repeat design exactly` |
| 포인트 컬러 구조물 | `preserve the blue accent wall on the left side exactly` |
| 유리·파티션 | `preserve the glass partition transparency and surface reflection exactly` |
| 특수 천장 구조 | `preserve the arched ceiling form and height exactly` |
| 사이니지·간판 | `preserve the signage text, color, and position on the wall exactly` |
| 주요 가구 배치 | `preserve the long conference table position and surface geometry exactly` |

---

## 출력 예시

### 예시 1 — 호텔 연회장 실사진

```
[SOURCE: 실사진]

PROMPT
real interior photograph upscale, perfect rectilinear perspective, plumb vertical walls, level horizontal ceiling and floor planes, accurate vanishing points preserved, straight parallel lines throughout, compositing-ready background plate, enhance sharpness and material clarity only, no structural or spatial alteration, preserve all existing surfaces as-is, preserve the Fairmont logo on the rear LED screen exactly, preserve the floral patterned carpet color and repeat design exactly

NEGATIVE (SD/ComfyUI 대체 경로 전용 — Magnific/nanobanana에는 입력하지 않음)
barrel distortion, pincushion distortion, fisheye, curved walls, warped geometry, bent vertical lines, tilted horizon, perspective warp, lens aberration, added film grain, artificial noise, vignette, hallucinated texture, artificial aging, new stains or marks, changed room geometry, new furniture added, objects moved or removed, hallucinated objects, new architectural elements, reframed composition, style change, dreamlike, painterly, illustration

SETTINGS
Creativity : 0.1
Resemblance: 0.95
Detail     : 0.35
HDR        : 0.1
```

### 예시 2 — 오피스 회의실 CGI 렌더

```
[SOURCE: CGI 렌더]

PROMPT
convert CGI render to photorealistic interior photograph, strict rectilinear geometry lock — plumb verticals, level horizontals, accurate vanishing points unchanged, no perspective shift, photorealistic material quality, realistic surface micro-texture, subtle material imperfection and aging, photographic light response on surfaces, compositing-ready photorealistic background, professional architectural photography, acoustic ceiling tile depth and grid shadow, carpet tile seam and wear variation, glass partition fingerprint and reflection depth, desk surface material weight, diffuse task lighting softness, preserve the glass partition transparency and surface reflection exactly, preserve the acoustic ceiling tile grid layout and panel depth exactly, preserve the long conference table position and surface geometry exactly

NEGATIVE (SD/ComfyUI 대체 경로 전용 — Magnific/nanobanana에는 입력하지 않음)
CGI look, plastic material, uniform synthetic texture, oversaturated colors, perfectly clean non-aging surfaces, barrel distortion, pincushion distortion, fisheye, curved walls, warped geometry, bent vertical lines, perspective shift, lens aberration, render artifact, ambient occlusion banding, new furniture added, objects moved, hallucinated objects, new architectural elements, toon shading, illustration, cartoon, added film grain

SETTINGS
Creativity : 0.3
Resemblance: 0.80
Detail     : 0.5
HDR        : 0.2
```

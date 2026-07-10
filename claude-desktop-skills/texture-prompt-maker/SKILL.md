---
name: texture-prompt-maker
description: "마감재 · 표면 · 재질 사진을 3D 소프트웨어(3DS Max · Blender · SketchUp · D5 · Lumion · Enscape) 용 심리스(seamless) 타일링 알베도/PBR 텍스처를 생성하는 image 프롬프트로 변환하는 전문 스킬. 사용자가 마감재·표면·재질 이미지와 함께 '텍스처 만들어줘', '심리스 텍스처', '타일링 텍스처', '알베도 텍스처', '재질 텍스처', '마감재 텍스처', '3D 텍스처', 'PBR 텍스처', '스샷 텍스처', '이 재질로 텍스처', 'seamless texture', '3DS Max 텍스처', '노멀맵/러프니스맵' 같은 말을 하면 반드시 이 스킬을 사용한다. 두 가지 입력 모드를 자동 판단한다: - 모드 A: 마감재·표면 클로즈업 1장 → 그 표면 전체를 텍스처로 - 모드 B: 공간·장면 이미지 1장 + 재질 지정(예: '파란 카펫', '벽돌 벽') → 해당 재질 영역만 추출 출력은 텍스처 생성용 PROMPT + NEGATIVE. 나노바나나 · Gemini 이미지 · Stable Diffusion 등에 그대로 사용. 공간 전체를 실사화하는 것은 interior-prompt-maker / arch-prompt-maker, 포토샵 합성 배경 준비는 magnific-compositing-prep 를 사용한다."
---

# 심리스 텍스처(알베도/PBR) 프롬프트 메이커

마감재·표면 사진을, 3D 소프트웨어에 바로 import 할 수 있는 **평탄하고(de-lit, 탈조명), 이음새 없이 타일링되는(seamless) 알베도(albedo/diffuse) 텍스처**를 만드는 image 프롬프트로 변환한다.

**출력 타입 2종 (먼저 결정):**
- **MATERIAL_TILE (기본):** 1:1 정사각, 상하좌우 4방향 심리스 — 단일 재질 면.
- **WALL_SECTION:** 여러 구역으로 구성된 벽(투톤·웨인스코트·띠 구성) — 그 면의 비율 보존, **가로만** 심리스, 세로 구성은 한 섹션 유지 (아래 "통합 원칙" 참조). 1:1을 강제하지 않는다.

## 핵심 원칙

**임무 = 사진 속 재질을 "순수 베이스 컬러 + 무한 반복 가능한 평면"으로 추출하는 것.**
재질의 색·패턴은 그대로 보존하고, 거기 박혀 있던 조명·그림자·원근만 걷어낸다. 새로운 디자인·색·아트 효과를 더하는 일이 아니다.

### ⭐ 0순위 원칙 — 원본 변환(img2img)이지 새 창작이 아니다 (실전 검증됨)

가장 흔한 실패: 생성기가 **원본을 안 보고 글만 보고 새 텍스처를 창작** → 패널 배치·비율·색이 매번 달라짐. 막는 법은 두 가지를 항상 함께 지키는 것:

1. **프롬프트를 "첨부 이미지 변환" 명령으로 작성한다.** 첫 문장은 반드시:
   > `"Use the ATTACHED reference image as the exact source and transform THAT SAME surface — do not invent, redesign, or re-imagine. Preserve precisely as in the source: [패널 배치/모듈 크기·위치/색/결/줄눈]. Change ONLY: (1) DELIGHT, (2) RECTIFY to orthographic, (3) make edges seamlessly tileable."`
   - (3)의 심리스 문구는 출력 타입에 따라 분기: **MATERIAL_TILE** = `"make all four edges seamlessly tileable"` / **WALL_SECTION** = `"make it horizontally seamless left-to-right only; preserve the top and bottom boundaries; not vertically tileable"`
   - 변하는 건 **조명·원근·이음새 3가지뿐.** 배치·비율·색·재질은 원본 고정.
   - 불필요 요소(글자·사이니지·배너·가구 등)는 "remove ... so only the [면] remains" 로 제거 지시.
2. **사용자에게 실행법을 반드시 안내한다:** ⓐ **원본 사진 첨부 필수**(텍스트만 ❌) ⓑ **img2img / 이미지 편집 모드**로 실행 ⓒ 엔진별 설정 — **Magnific이면 Creativity 0.1~0.2 / Resemblance 0.8~0.9 (0~1 스케일)**, **SD 계열(A1111/ComfyUI img2img)이면 denoising strength 0.3~0.45 낮게**, 나노바나나·Gemini면 "이 이미지를 편집" 형태 ⓓ **모드 B(장면+재질 지정)는 장면 전체를 첨부하지 말고 대상 재질 영역을 먼저 크롭한 이미지를 첨부 원본으로 쓴다(사전 크롭 필수)** — 고정 유사도 img2img는 장면 전체(가구·벽·천장)를 그대로 재현하므로 프롬프트의 isolate 문구만으로는 영역 추출이 안 된다. 크롭이 불가하면 편집형 생성기(나노바나나/Gemini) 경로로 안내 ⓔ 생성기가 출력 비율을 강제(1:1 등)하면 프롬프트로 비율을 요구하지 말고 **원본을 대상 면 비율로 크롭해 첨부**한다.

> 패널 크기가 제각각인 벽(불규칙 구성)은 **격자를 새로 규칙화하지 말고 원본 배치를 그대로 보존**한다 — 규칙화는 균일 그리드 재질에만.

이 세 가지가 빠지면 3D에서 못 쓰는 텍스처가 된다. 그래서 프롬프트의 뼈대도 이 셋이다:

1. **Delighting(탈조명)** — 그림자·하이라이트·반사·방향성 조명을 0%로. 가상 라이트에만 반응하는 평평한 색 데이터만 남긴다.
2. **Orthographic(정면 평탄화)** — 원근·렌즈 왜곡을 제거해 카메라를 표면 정면에 수직으로 둔 듯한 정사 투영 평면으로.
3. **Seamless + Stochastic(무봉제 + 비반복)** — 상하좌우 가장자리가 완벽히 맞물리고, 타일링 티가 나는 "튀는 특징"(별 모양 자국, 고립된 얼룩, 눈에 띄는 한 점)은 분산·제거한다.

> ⚠️ **비반복(stochastic)은 "표면 질감"에만 적용한다. "구조(그리드·줄눈·모듈)"에는 절대 적용하지 않는다.**
> 패널·타일·벽돌처럼 **규칙적 모듈** 재질에서 stochastic을 구조에까지 걸면, 모델이 줄눈을 일부러 어긋나게 만들어 격자가 깨진다(실제 실패 사례 있음). 그래서 두 층을 분리해 지시한다:
> - **구조 층 = 완벽 규칙 고정:** `"keep the panel/tile grid perfectly regular and uniform — evenly sized modules, crisp straight continuous aligned joint lines, identical spacing; do NOT randomize, offset, stagger, break, shift, or distort the grid."`
> - **표면 층 = 미세 변화만:** `"apply subtle natural variation ONLY within the surface texture (fiber/grain/weave), never in the joint grid."`
> 콘크리트·석재·흙처럼 **모듈이 없는 유기적 재질**일 때만 stochastic을 표면 전체에 자유롭게 적용한다.

## 빠른 흐름

1. **모드 판단**: 클로즈업 1장 → 모드 A / 장면 + 재질 지정 → 모드 B
2. **재질 파악**: 종류(콘크리트·벽돌·목재·패브릭·석재·금속·타일 등), 색, 패턴 스케일
3. **PROMPT + NEGATIVE 작성** (아래 순서)
4. **PROMPT + NEGATIVE 두 섹션만** 출력 — 설명·분석·주석 없음 (단, 두 섹션이 끝난 **뒤에** 실행법 안내를 덧붙이는 것은 허용·필수)

카메라 브랜드(Sony, Canon 등) 절대 명시하지 않는다 — 텍스처에는 카메라 자체가 없어야 한다.
MJ 파라미터(`--v`, `--ar` 등) 포함하지 않는다.

## 출력 원칙

- **PROMPT와 NEGATIVE 두 섹션만** 출력 — 두 섹션 앞·사이에는 설명을 넣지 않으며, 실행법 안내(원본 첨부·img2img 모드·설정값)는 두 섹션이 모두 끝난 **이후에만** 덧붙인다
- 단, 사용자가 "프롬프트만 줘"라고 엄격 출력을 요구하면 실행법 안내를 생략한다 — **사용자의 출력 계약이 우선**
- **NEGATIVE 사용처:** NEGATIVE 섹션은 **항상 출력**(조건부 생략 금지)하되, 제목을 `NEGATIVE (SD/ComfyUI 디퓨전 전용 — gpt-image·나노바나나에는 입력하지 않음)`으로 표기한다. gpt-image·나노바나나(Gemini) 등 negative 입력 필드가 없는 의미기반 생성기 대상이면 이 섹션은 입력하지 않고, 핵심 억제 항목을 긍정형으로 PROMPT에 흡수한다(예: baked shadows 억제 → `"perfectly even shadowless lighting"`, seams 억제 → `"perfectly continuous edges"`)
- PROMPT는 **하나의 연속된 영어 단락**, NEGATIVE도 **하나의 연속된 영어 단락**
- 사용자가 PBR 맵(노멀/러프니스/AO)을 요청하면 그때만 추가 섹션을 붙인다 (아래 "PBR 맵 확장")

---

## 모드 판단

**모드 A — 마감재/표면 클로즈업 1장:** 그 이미지의 표면 전체가 타겟 재질. 화면을 꽉 채운 콘크리트·벽돌·러그 등.

**모드 B — 공간/장면 이미지 1장 + 재질 지정:** 이미지 안에서 사용자가 말한 재질 영역(예: "파란 카펫", "왼쪽 벽돌 벽")만 식별해 그 부분으로 텍스처를 만든다. 반드시 어느 재질인지 사용자에게 확인된 상태에서 진행한다.

### 통합 원칙 ★ (한 재질 = 한 장)

사용자가 **하나의 대상("벽체", "바닥", "이 벽")** 을 지정하면, 그 안에 색·톤·구역이 여러 개여도 **절대 여러 장으로 쪼개지 않는다.** 항상 **한 장의 텍스처로 합쳐서** 출력한다 — 3D에서 한 번에 매핑해 쓰는 게 목적이기 때문이다.

- **단일 톤 면:** 그대로 사방 심리스 정사각 텍스처.
- **여러 구역으로 구성된 면(예: 상단 베이지 + 중간 띠 + 하단 그레이, 웨인스코트, 투톤 벽):** 그 면의 **세로 구성(composition)을 그대로 보존한 "벽 섹션 텍스처" 한 장**으로 만든다.
  - **가로(좌우) 방향만 심리스 타일링** — 긴 벽을 감싸도록.
  - **세로 구성은 전체 높이 한 섹션으로 유지** — 세로로는 타일링하지 않는다.
  - 1:1 강제하지 말고 **그 면의 비율(wall-section aspect)을 보존**한다.
  - 첫 문장에 `"capture the entire [면] as a single unified wall-section texture that can be applied at once, preserving its full vertical composition — [상단 구역], [중간 띠/구분 요소], [하단 구역]"` 를 명시한다.
  - Seamless 4단계는 `"horizontally seamless and tileable left-to-right ... keep the vertical composition intact as one full wall-height section"` 로 바꿔 쓴다.

여러 재질을 **각각 따로** 원하실 때만(사용자가 명시적으로 "따로", "각각", "분리해서" 라고 할 때) 분할 출력한다.

---

## PROMPT 작성 순서

### 1. 출력물 성격 선언 (첫 문장) ★★★

**기본(권장) — img2img 변환 프레이밍** (위 ⭐0순위 원칙): 원본 첨부 + 이미지 편집으로 쓸 때.
> `"Use the ATTACHED reference image as the exact source and transform THAT SAME [면/재질] into a flat orthographic seamless tileable PBR albedo texture — do not invent, redesign, or re-imagine. Preserve precisely as in the source: [배치/모듈/색/결/줄눈]."`

**대안 — 설명 프레이밍** (텍스트 전용 생성기에서만): 원본을 못 첨부할 때.
> `"A flat orthographic seamless tileable PBR albedo (base color / diffuse) texture map of [재질 구체적 묘사 — 색상값·패턴 스케일·모듈 치수까지 직접 서술] for direct use in 3D software."`

> ⚠️ **텍스트 전용 경로에서는 "extracted faithfully from the reference image" 같은 참조 문구를 절대 넣지 않는다** — 첨부되지 않은 이미지를 참조시키면 환각을 유발한다(아래 예시들의 해당 구문도 텍스트 전용으로 복사할 때는 제거하고 Claude가 원본 분석에서 뽑은 구체 묘사로 대체한다).

**모드 B는 영역 한정을 추가:**
> `"...isolate only the [지정 재질, 예: blue low-pile carpet] region from the scene and generate its texture, ignoring all other surfaces."`

예:
- `"A flat orthographic seamless tileable PBR albedo texture map of weathered exposed concrete with fine aggregate grain, extracted faithfully from the reference image for direct use in 3D software."`
- `"A flat orthographic seamless tileable PBR albedo texture map of red clay running-bond brick wall with mortar joints, extracted faithfully from the reference image for 3D use."`

### 2. Delighting(탈조명) — 가장 중요 ★★★

조명 정보를 완전히 제거한다고 강하게 명시한다. 이게 약하면 3D에서 그림자가 두 번 생긴다.

> `"Completely delit: neutralize all direct and indirect lighting to zero, erase every cast shadow, self-shadow, specular highlight, glare, hotspot, and lighting gradient. Leave only the pure even base-color albedo data that will react solely to virtual lights in 3D software. Uniform neutral studio illumination, perfectly flat and dry color."`

### 3. Orthographic(정면 평탄화)

> `"Perfectly flattened straight-on orthographic front view as if photographed exactly perpendicular to the surface; correct all perspective, foreshortening, and lens distortion while strictly preserving the material's inherent structural forms (brick coursing, plank layout, weave direction, tile grid) without warping."`

### 4. Seamless + Stochastic(무봉제 + 비반복)

**유기적 재질(콘크리트·석재·흙 등, 모듈 없음):**
> `"Perfectly seamless and tileable across all four edges with no visible seam lines; ensure natural continuity and stochastic non-repeating variation so the texture never looks artificially repeated when tiled over a large surface; disperse or remove any distinct landmark feature — isolated stains, standout marks, single eye-catching spots — that would reveal the repetition."`

**규칙적 모듈 재질(패널·타일·벽돌 등) — 구조/표면 분리 필수 ★:**
> `"CRITICAL — keep the [panel/tile] grid perfectly regular and uniform: evenly sized modules with crisp, straight, continuous, consistently aligned joint lines and identical spacing across the entire texture; do NOT randomize, offset, stagger, break, shift, or distort the grid. Perfectly seamless and tileable across all four edges with no visible seam lines; apply subtle natural variation ONLY within the surface texture (fiber/grain/weave) so it does not look mechanically cloned, but NEVER vary, offset, or break the joint grid; remove any isolated stain, hardware fitting, or standout mark."`

### 5. 재질 충실도 + 사양

재질 고유의 색과 미세 디테일은 살린다.

> `"Strictly photorealistic and faithful to the original material — preserve exact base-color values and micro-detail (pores, grain, fiber, micro-scratches, surface roughness texture). 4K ultra-high resolution (3840px or higher), 1:1 square aspect ratio, no watermark, no text. No artistic photography effects."`
>
> ※ 비율 분기: 위 `1:1 square aspect ratio`는 일반 타일링 텍스처 기본값이다. **통합 모드(WALL_SECTION)에서는 1:1을 강제하지 않고** `preserve the wall-section aspect proportion`으로 대체한다(예시 참조).

재질별 디테일 키워드는 아래 "재질별 키워드" 참고.

---

## NEGATIVE 작성

카테고리 순서대로, 하나의 영어 단락으로:

**탈조명 실패 억제 (최우선):**
```
baked shadows, cast shadows, self-shadows, drop shadows, specular highlights, glare, hotspots,
directional lighting, lighting gradient, baked ambient occlusion, uneven illumination, shiny reflections
```

**원근/왜곡 억제:**
```
perspective distortion, lens distortion, vanishing point, angled view, tilted surface,
foreshortening, warped structure, skewed pattern
```

**타일링 실패 억제:**
```
visible seams, seam lines, tiling seams, obvious repeating pattern, repetition artifacts,
mirrored edges, distinct landmark features, isolated stains, standout marks, single eye-catching spot
```

**그리드 붕괴 억제 (모듈/패널/타일/벽돌 재질 필수 — 재질별 취사 규칙 준수):**
```
irregular grid, broken grid, misaligned joints, shifted rows, randomized layout,
distorted grid, warped joints, wavy seam lines,
inconsistent module size, discontinuity band, mismatched rows
```
- **정렬형 그리드 재질에만 추가**(타일·패널·커튼월 등 줄눈이 상하좌우 일직선인 경우): `staggered joints, offset panels, running-bond offset`
- **어긋쌓기가 정상 패턴인 재질에는 위 3개 토큰 금지**(벽돌 running bond, 헤링본 등) — PROMPT의 `running-bond coursing`과 충돌해 정상 패턴 자체를 억제한다. 대신 `inconsistent coursing, uneven course height`를 쓴다.

**재질 정체성 상실 억제 (원본 재질을 다른 재질로 바꾸지 않게):**
```
lost original texture, flat smooth stone, ceramic tile look, plain concrete, polished surface,
smeared texture, wrong material, generic surface
```

**아트 효과/스타일화 억제:**
```
artistic effects, photo filters, vignetting, chromatic aberration, color grading, HDR,
oversaturation, stylized, illustration, painterly, bokeh, depth of field, blur
```

**색·재질 오염 억제:**
```
color shift, recolored, altered material color, inaccurate base color, fake material,
plastic look, procedural look, AI texture artifacts
```

**품질 억제:**
```
low resolution, blurry, soft focus, noise, jpeg artifacts, watermark, text, logo, border, frame
```

---

## 재질별 키워드 (PROMPT 5단계에 섞어 사용)

- **콘크리트:** `fine aggregate grain, subtle tonal mottling, form-tie marks, micro-pores, matte cement surface, hairline variation`
- **벽돌:** `clay brick texture, mortar joint depth, slight color variation per brick, surface pitting, running-bond coursing`
- **목재:** `natural wood grain, pore texture, plank seams, knots, directional fiber, low-sheen satin grain`
- **패브릭/카펫:** `woven fiber texture, visible weave, pile direction, thread variation, soft matte absorption`
- **석재/대리석:** `mineral veining, stone porosity, soft vein transition, micro roughness, honed surface`
- **금속:** `brushed metal grain, micro scratches, subtle anisotropic direction, matte metallic base color`
- **타일:** `ceramic surface, grout line grid, slight glaze variation, edge bevel, uniform module`

---

## PBR 맵 확장 (옵션 — 요청 시에만)

사용자가 "노멀맵", "러프니스맵", "AO맵", "PBR 풀세트"를 요청하면, 같은 재질에 대해 추가 섹션을 출력한다. 각 맵은 albedo와 동일한 구도·타일링을 공유해야 한다.

> ⚠️ 이미지 생성기로 만든 노멀/러프니스/AO는 **물리 측정 기반 PBR이 아니라 시각적 추정 맵**이다. 3D에 바로 넣지 말고 Substance/Materialize/렌더러 프리뷰에서 검수·보정 후 사용하도록 안내를 덧붙인다.

- **NORMAL MAP PROMPT:** `"Tangent-space normal map of the same [재질] texture, same seamless tiling and alignment as the albedo, dominant blue/purple palette, encoding surface height as RGB normals, no color/albedo information, no lighting."`
- **ROUGHNESS MAP PROMPT:** `"Grayscale roughness map of the same [재질] texture, same tiling, white = rough and black = smooth, representing micro-surface variation only, no color, no lighting."`
- **AO MAP PROMPT:** `"Grayscale ambient occlusion map of the same [재질] texture, same tiling, soft contact shadows in crevices and joints only, white = exposed, dark = occluded, no albedo color."`

---

## 예시

### 모드 A — 풍화된 노출 콘크리트 클로즈업 1장

```
PROMPT
A flat orthographic seamless tileable PBR albedo (base color / diffuse) texture map of weathered exposed concrete with fine aggregate grain and subtle tonal mottling, extracted faithfully from the reference image for direct use in 3D software. Completely delit: neutralize all direct and indirect lighting to zero, erase every cast shadow, self-shadow, specular highlight, glare, hotspot, and lighting gradient, leaving only the pure even base-color albedo data that will react solely to virtual lights in 3D software, uniform neutral studio illumination, perfectly flat and dry color. Perfectly flattened straight-on orthographic front view as if photographed exactly perpendicular to the surface, correct all perspective, foreshortening, and lens distortion while strictly preserving the concrete's inherent surface forms without warping. Perfectly seamless and tileable across all four edges with no visible seam lines, natural continuity and stochastic non-repeating variation so the texture never looks artificially repeated when tiled over a large wall, disperse or remove any distinct landmark feature, isolated stains, standout marks, or single eye-catching spots that would reveal the repetition. Strictly photorealistic and faithful to the original material, preserve exact base-color values and micro-detail including fine aggregate grain, form-tie marks, micro-pores, and hairline variation, matte cement surface. 4K ultra-high resolution, 1:1 square aspect ratio, no watermark, no text, no artistic photography effects.

NEGATIVE (SD/ComfyUI 디퓨전 전용 — gpt-image·나노바나나에는 입력하지 않음)
baked shadows, cast shadows, self-shadows, drop shadows, specular highlights, glare, hotspots, directional lighting, lighting gradient, baked ambient occlusion, uneven illumination, shiny reflections, perspective distortion, lens distortion, vanishing point, angled view, tilted surface, foreshortening, warped structure, skewed pattern, visible seams, seam lines, tiling seams, obvious repeating pattern, repetition artifacts, mirrored edges, distinct landmark features, isolated stains, standout marks, single eye-catching spot, artistic effects, photo filters, vignetting, chromatic aberration, color grading, HDR, oversaturation, stylized, illustration, painterly, bokeh, depth of field, blur, color shift, recolored, altered material color, inaccurate base color, fake material, plastic look, procedural look, AI texture artifacts, low resolution, blurry, soft focus, noise, jpeg artifacts, watermark, text, logo, border, frame
```

### 모드 B — 회의실 장면 이미지 + "파란 카펫" 지정

```
PROMPT
A flat orthographic seamless tileable PBR albedo (base color / diffuse) texture map of blue low-pile commercial loop carpet, extracted faithfully from the reference image for direct use in 3D software; isolate only the blue carpet floor region from the scene and generate its texture, ignoring all other surfaces, furniture, and walls. Completely delit: neutralize all direct and indirect lighting to zero, erase every cast shadow, self-shadow, specular highlight, glare, hotspot, and lighting gradient, leaving only the pure even base-color albedo data that will react solely to virtual lights in 3D software, uniform neutral studio illumination, perfectly flat and dry color. Perfectly flattened straight-on orthographic top-down view as if photographed exactly perpendicular to the floor, correct all perspective and foreshortening while preserving the carpet's weave direction and fiber pattern without warping. Perfectly seamless and tileable across all four edges with no visible seam lines, natural continuity and stochastic non-repeating variation so the carpet never looks artificially repeated when tiled over a large floor, disperse or remove any distinct landmark feature, isolated stains, or standout marks that would reveal the repetition. Strictly photorealistic and faithful to the original material, preserve exact blue base-color value and micro-detail including woven fiber texture, visible loop weave, pile direction, and thread variation, soft matte absorption. 4K ultra-high resolution, 1:1 square aspect ratio, no watermark, no text, no artistic photography effects.

NEGATIVE (SD/ComfyUI 디퓨전 전용 — gpt-image·나노바나나에는 입력하지 않음)
baked shadows, cast shadows, self-shadows, drop shadows, specular highlights, glare, hotspots, directional lighting, lighting gradient, baked ambient occlusion, uneven illumination, shiny reflections, furniture, walls, ceiling, other surfaces, scene objects, perspective distortion, lens distortion, vanishing point, angled view, tilted surface, foreshortening, warped structure, skewed pattern, visible seams, seam lines, tiling seams, obvious repeating pattern, repetition artifacts, mirrored edges, distinct landmark features, isolated stains, standout marks, single eye-catching spot, artistic effects, photo filters, vignetting, chromatic aberration, color grading, HDR, oversaturation, stylized, illustration, painterly, bokeh, depth of field, blur, color shift, recolored, altered material color, inaccurate base color, fake material, plastic look, procedural look, AI texture artifacts, low resolution, blurry, soft focus, noise, jpeg artifacts, watermark, text, logo, border, frame
```

### 통합 모드 — 회의실 장면 + "벽체" 지정 (여러 구역 → 한 장)

상단 베이지 패널 + 중간 흰색 타공 띠 + 하단 베이지 타공 패널처럼 한 벽이 여러 구역으로 나뉘어도, **쪼개지 않고 세로 구성을 보존한 한 장의 벽 섹션 텍스처**로 만든다.

```
PROMPT
A flat orthographic seamless tileable PBR albedo (base color / diffuse) texture map of the complete warm beige acoustic wall finish, extracted faithfully from the reference image; capture the entire wall as a single unified wall-section texture that can be applied at once, preserving its full vertical composition — an upper large-format warm-beige fabric-wrapped acoustic panel zone, a horizontal white micro-perforated acoustic accent band at mid-height, and a lower warm-beige micro-perforated acoustic panel zone with subtle panel seam rhythm. Isolate only the wall material and ignore the ceiling, signage, equipment, furniture, and floor. Completely delit: neutralize all direct and indirect lighting to zero, erase every cast shadow, self-shadow, specular highlight, glare, hotspot, and lighting gradient, leaving only the pure even base-color albedo data that will react solely to virtual lights in 3D software, uniform neutral studio illumination, perfectly flat and dry color. Perfectly flattened straight-on orthographic front view as if photographed exactly perpendicular to the wall, correct all perspective, foreshortening, and lens distortion while strictly preserving the acoustic panel module proportions, seam rhythm, divider band position, and micro-perforation grid without warping. Horizontally seamless and tileable left-to-right with no visible vertical seam so it wraps a long wall, keep the vertical composition intact as one full wall-height section, and apply stochastic non-repeating variation so the wall never looks artificially repeated, dispersing any distinct landmark feature, scuff mark, or isolated stain that would reveal the repetition. Strictly photorealistic and faithful to the original material, preserve exact warm beige base-color values and micro-detail including fine acoustic perforation dots, subtle panel weave grain, panel joint lines, and slight tonal variation, matte sound-absorbing finish. 4K ultra-high resolution, preserve the wall-section aspect proportion, no watermark, no text, no artistic photography effects.

NEGATIVE (SD/ComfyUI 디퓨전 전용 — gpt-image·나노바나나에는 입력하지 않음)
ceiling, ceiling grid, downlights, downlight glow, banner, signage, text banner, LED panel, blue glow, loudspeakers, microphone stand, tripod, wall sconce, wall clock, stage, podium, tables, desks, chairs, carpet, floor, people, baked shadows, cast shadows, self-shadows, specular highlights, glare, hotspots, directional lighting, lighting gradient, baked ambient occlusion, uneven illumination, shiny reflections, perspective distortion, lens distortion, vanishing point, angled view, tilted surface, foreshortening, warped structure, skewed pattern, visible vertical seam, tiling seams, obvious repeating pattern, repetition artifacts, mirrored edges, distinct landmark features, isolated stains, scuff marks, standout marks, artistic effects, photo filters, vignetting, chromatic aberration, color grading, HDR, oversaturation, stylized, illustration, painterly, bokeh, depth of field, blur, color shift, recolored, altered material color, inaccurate base color, fake material, plastic look, procedural look, AI texture artifacts, low resolution, blurry, soft focus, noise, jpeg artifacts, watermark, text, logo, border, frame
```

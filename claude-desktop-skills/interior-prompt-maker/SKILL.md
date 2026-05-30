---
name: interior-prompt-maker
description: >
  인테리어 · 실내 공간 CGI · 렌더 이미지를 Stable Diffusion / Midjourney / ComfyUI
  image-to-image용 사실적 실내 사진 프롬프트로 변환하는 전문 스킬.
  이미지 1장(원본 실사화)과 2장(구조 보존 + 스타일 리모델링) 두 가지 모드를 자동 판단한다.

  사용자가 실내 이미지와 함께 "프롬프트 만들어줘", "실사화해줘",
  "리모델링 프롬프트 써줘", "i2i 프롬프트 뽑아줘", "SD/MJ 프롬프트",
  "사진처럼 만들어줘", "CGI 느낌 없애줘", "인테리어 프롬프트" 같은 말을
  하면 반드시 이 스킬을 사용한다.

  입력 유형: SketchUp · Rhino · Revit · Lumion · Enscape · D5 실내 렌더,
  화이트 모델, 클레이 모델 — 모든 실내 CGI.

  지원 공간: 거실 · 주방 · 침실 · 욕실 · 오피스 · 카페 · 레스토랑 ·
  호텔 로비 · 병원 · 교육 공간 · 공공 서비스홀.

  건물 외관 프롬프트는 arch-prompt-maker를 사용한다.
---

# 인테리어 Image-to-Image 프롬프트 메이커

인테리어 CGI/렌더/모델 이미지를 실제 건축 인테리어 사진과 구분 불가능한 수준의 프롬프트로 변환한다.

## 핵심 원칙

**임무 = CGI 표면 퀄리티 → 사진 퀄리티 변환. 색상·재료·공간 재설계가 아니다.**

## 빠른 흐름

1. **모드 판단**: 이미지 1장 → 단일 모드 / 이미지 2장 → 리모델링 모드
2. **이미지 분석**: 공간 유형, 색상 팔레트, 주요 건축 요소 파악
3. **9단계 PROMPT + NEGATIVE** 작성
4. **PROMPT + NEGATIVE 두 섹션만** 출력 — 설명 없음

카메라 브랜드 (Sony, Canon, Hasselblad 등) 절대 명시하지 않는다.
MJ 파라미터 (`--v`, `--iw`, `--ar` 등) 절대 포함하지 않는다.

## 출력 원칙

- **PROMPT와 NEGATIVE 두 섹션만** 출력
- 설명, 분석, 주석 없음
- PROMPT는 **하나의 연속된 영어 단락**
- NEGATIVE는 **하나의 연속된 영어 단락**

---

## 모드 판단

**이미지 1장 → 단일 모드:** 원본 공간을 실사 사진으로 변환
**이미지 2장 → 리모델링 모드:** 이미지1 구조·색상 유지 + 이미지2 스타일만 적용

---

## PROMPT 작성 순서 (9단계, 엄격히 준수)

### 1. 이미지 역할 선언 (첫 문장) ★★★

**출력물 성격을 먼저 선언. 카메라+공간 보존을 한 문장에 통합.**

**단일 모드:**
> `"Ultra photorealistic architectural interior photography of [공간유형] converted from a CGI architectural render while preserving the exact original camera position, eye-level perspective, composition, [이 공간 전용 요소 구체적 나열], and spatial hierarchy."`

**반드시 포함할 요소 (공간에서 눈에 보이는 것을 구체적으로):**
- 카메라: `camera position, eye-level perspective, lens perspective, focal length feel, framing, crop, composition, horizon line`
- 천장: `ceiling geometry / ceiling layout / suspended ceiling baffle layout`
- 바닥: `floor level, floor plan geometry`
- 벽/구조: `wall positions, partitions, architectural boundaries`
- 주요 가구·카운터: `counter placement, furniture arrangement, shelving configuration`
- 동선: `circulation layout, openings`

**예시:**
- `"Ultra photorealistic architectural interior photography of a modern Korean public facility reception lobby converted from a CGI architectural render while preserving the exact original camera position, eye-level perspective, composition, room proportions, ceiling layout, circulation, counter placement, furniture arrangement, shelving geometry, and spatial hierarchy."`
- `"Ultra photorealistic architectural interior photography of a contemporary Korean public library lounge transformed from a CGI render into a believable real built environment while preserving the exact original camera angle, eye-level viewpoint, lens perspective, composition, ceiling geometry, circulation layout, furniture placement, shelving arrangement, and architectural proportions."`

**리모델링 모드:**
> `"Use Image 1 as the immutable architectural structure, room geometry, camera, composition, and spatial reference, and use Image 2 only as the remodeling style, material, furniture, lighting, and atmosphere reference."`

---

### 2. 전환 선언 + 공간 정체성

이미지 역할 선언 직후. 두 가지 중 선택:

**옵션 A — 전면 변환:**
> `"Transform the space into a believable built interior with realistic materiality and architectural detailing."`

**옵션 B — 요소별 보존 (권장):**
> `"Maintain the existing [천장/카운터/가구 등 핵심 요소] exactly as shown while upgrading all materials into realistic architectural finishes."`

예: `"Maintain the existing curved reception desk configuration and suspended wood slat ceiling exactly as shown while upgrading all materials into realistic architectural finishes."`

---

### 3. 컬러 팔레트 잠금 ★ (재료 묘사 전 필수)

**가장 자주 실패하는 지점. 반드시 포함.**

먼저 선언:
> `"Preserve exactly the original design color palette without any change, reinterpretation, or color shift. The task is to convert CGI surface quality to photographic realism only — do NOT redesign, recolor, or replace any material or color."`

그 다음 이미지에서 확인된 모든 색상을 요소별로 명시:

```
[색상명] — [해당 요소]
예시:
mustard yellow / warm golden ochre — counter front panels, shelving units, ceiling soffit band
dusty rose / mauve — all wall surfaces
cobalt blue — chair shells
teal / cyan — accent panel insets
dark walnut brown — ceiling slat baffles
light natural oak — table surface
gray — large-format floor tiles
white matte — ceiling panels, gate frame, counter top
```

---

### 4. 재료 변환 ★★★ (핵심 섹션)

**두 가지 패턴을 섞어서 사용:**

**패턴 A — 요소 보존형 (특정 건축 요소가 뚜렷할 때):**
> `"Preserve the [요소] exactly as shown, but render them with [현실적 물성]..."`

예:
- `"Preserve the suspended linear wood ceiling baffles exactly as shown, but render them with authentic walnut wood texture, natural variation, slight construction irregularities, and realistic recessed lighting trim depth."`
- `"Preserve the U-shaped reception counter configuration exactly as shown, but render the front panels with realistic woven acoustic fabric tension, visible weave texture, and matte surface absorption."`

**패턴 B — 색상+재료 묘사형 (전체 공간 재질화):**
> `"The [색상] [재료명] features [현실적 물성]..."`

예:
- `"The warm natural oak veneer slatted panels feature subtle edge wear, realistic wood grain variation, and believable construction tolerances."`
- `"The blue upholstered chairs show detailed woven fabric texture, slight wrinkles, soft seat deformation, matte powder-coated metal legs, and naturally worn contact areas."`

**재료별 핵심 물성 키워드:**

**목재:**
`natural wood grain variation, subtle pore texture, realistic plank/panel seams, low-sheen finish, directional wood reflection, organic tonal inconsistency, slight edge wear`

**패브릭/업홀스터리:**
`woven textile texture, visible fabric weave, realistic fabric tension, natural folds, cushion compression, soft diffuse absorption, slight seat deformation, naturally worn contact surfaces`

**석재/타일:**
`subtle mineral variation, realistic stone porosity, soft vein transitions, natural surface depth, micro roughness, honed finish, diffuse reflections, grout line variation, stone expansion joints`

**금속:**
`brushed finish, controlled specular highlights, softened reflections, realistic metallic roughness, anodized finish depth, directional reflection response, subtle micro scratches, joint tolerances, sealant detailing`

**유리:**
`realistic glass transparency, layered reflections, subtle glazing depth, physically accurate refraction, soft reflectivity, glazing thickness, mullion detailing, edge reflections`

**도장 벽:**
`matte painted plaster, subtle wall texture, realistic paint absorption, soft plaster variation, shadow gaps, corner detailing, edge transitions`

**천장:**
`matte ceiling finish, subtle ceiling shadowing, realistic recessed lighting trims, HVAC diffuser detailing, soft ceiling bounce, mounting hardware depth`

---

### 5. 표면 디테일 + 실생활 소품

> `"Include subtle construction tolerances, realistic seams, edge conditions, material thickness, shadow gaps, cabinet joints, silicone lines, grout lines, baseboards, mullions, recessed lighting trims, curtain rails, door frames, ventilation diffusers, HVAC diffusers, electrical outlets, signage mounting details, reception accessories, slight clutter, and realistic interior imperfections. Add subtle dust, fingerprints, fabric wrinkles, edge wear, soft scratches, and believable surface aging."`

공공·업무 공간 추가:
> `"Realistic institutional accessories: document trays, monitors with cable management, signage holders, pen holders, reception accessories at proper scale."`

주거 공간 추가:
> `"Realistic Korean residential objects: books, remote controls, tea cups, lifestyle clutter at believable scale."`

---

### 6. 가구 + 오브젝트 사실성

> `"Physically believable furniture scale, realistic upholstery tension, natural fabric folds, proper cushion compression, believable object placement, and subtle everyday residential or institutional clutter."`

---

### 7. 조명

순서: 광원 유형 → 색온도 → 그림자 → 반사 → 노출 밸런스 → 센서 그레인

**자연광만:**
```
soft natural daylight entering through windows with physically believable interior exposure balance,
controlled dynamic range between exterior daylight and interior luminance,
soft shadow gradients, natural penumbra, realistic ambient falloff, subtle photographic sensor grain
```

**인공조명만 (기관·상업):**
```
warm institutional recessed ceiling downlights with realistic localized illumination pools and trim ring depth,
soft linear LED strips with believable luminance falloff, diffuse ambient bounce,
controlled [2700K–3000K 주거 / 3000K–4000K 기관] lighting balance,
soft shadow gradients, subtle photographic sensor grain
```

**혼합 (자연 + 인공) — 가장 현실적:**
```
balanced mixed lighting with soft natural daylight and warm recessed architectural lighting,
realistic interplay between cool daylight and warm interior practical lighting,
controlled exposure balance between bright exterior daylight and warm interior illumination,
architectural photography dynamic range with realistic window highlight retention,
subtle warm-cool lighting contrast, subtle photographic sensor grain
```

**창문 노출 원칙:** 창문 > 실내 밝기 = 현실적. 항상 포함:
`"controlled exposure balance between bright exterior windows and interior shadow detail"`

---

### 8. 인물 (조건부)

원본에 인물이 있거나 요청 시에만:

> `"[동작 묘사] realistic Korean [남/녀] — [복장], [방향/자세], candid posture, realistic clothing fabric drape and tension, natural hair, visible hair strands, authentic body proportions, realistic skin texture, and believable interaction with the space."`

예:
- `"Replace the CGI figure with a realistic casually dressed Korean woman captured candidly from behind with natural body proportions, realistic hair strands, natural clothing folds, authentic skin texture, and believable posture."`
- `"One naturally posed Korean woman walking toward the service counter — brown knit top, dark blue jeans — back to camera, candid mid-stride posture, realistic clothing drape, natural hair."`

---

### 9. 최종 선언 + 카메라 + anti-CGI

**세 부분을 이어서 작성:**

**사진 리얼리즘:**
> `"The final result must feel like a professionally photographed real built interior space, not a CGI render or architectural visualization. Ultra high detail, natural color science, realistic dynamic range, subtle photographic sensor grain, editorial architectural photography quality."`

**카메라 선언 (마지막에 위치):**
> `"Captured as a professional full-frame architectural interior photograph using a [24mm 광각/35mm 표준] lens, indistinguishable from a real built environment."`

**anti-CGI 강화:**
> `"No render look, no archviz appearance, no plastic materials, no fake reflections, no Unreal Engine look, no SketchUp appearance, no clay-render feeling, no synthetic atmosphere, no artificial lighting. Completely believable real-world interior photograph."`

---

## NEGATIVE 작성 (14카테고리, 순서 엄수)

### 1. 스타일화 억제
```
cartoon, anime, illustration, sketch, watercolor, concept art, matte painting, stylized, painterly
```

### 2. 렌더 엔진/CGI 억제
```
CGI, archviz look, render look, Unreal Engine look, Blender render look, game-engine look,
SketchUp look, Rhino viewport look, Revit model look, Enscape look, D5 Render look,
Lumion look, Twinmotion look, V-Ray render look, Corona render look,
clay render, white model, obvious 3D render, artificial rendering, synthetic lighting,
fake global illumination, plastic rendering, showroom CGI materials
```

### 3. 카메라 오염 억제
```
changed camera angle, changed viewpoint, changed perspective, changed framing, changed crop,
changed composition, changed lens perspective, zoomed-in composition, zoomed-out composition,
reframed shot, perspective reinterpretation, altered focal length feel, distorted wide-angle view
```

### 4. 컬러 오염 억제 ★
```
changed color palette, recolored surfaces, altered material colors, color shift,
changed accent color, changed wall color, changed upholstery color, changed floor color,
material redesign, redesigned material identity, replaced materials, color reinterpretation,
desaturated colors, oversaturated colors
```

### 5. 기하학 오염 억제
```
changed room geometry, changed room proportions, changed ceiling height, changed ceiling shape,
changed wall positions, changed floor level, changed window placement, changed door positions,
wrong scale, redesigned architecture, distorted room, enlarged room, shrunken room,
stretched room, warped walls, melted architecture, unrealistic proportions
```

### 6. 구조 수정 억제
```
deleted architectural elements, moved walls, moved windows, moved doors,
random added structural elements, fake openings, extra columns, altered circulation path,
missing ceiling elements, floating architectural elements, impossible architecture,
missing architectural details
```

### 7. 재료 사실성 억제
```
plastic materials, fake wood, fake stone, fake glass, flat painted surfaces, unrealistic textures,
fake reflections, oversmoothed surfaces, texture repetition, procedural textures,
unrealistic roughness, glossy plastic wood, glossy plastic surfaces, artificial textures,
incorrect material scale, showroom CGI materials, empty sterile space, unrealistic wood texture
```

### 8. 유리/반사 억제
```
mirror glass, flat glazing, unrealistic glass, impossible reflections,
floating reflections, opaque glass, incorrect transparency, fake window reflections
```

### 9. 가구/오브젝트 물성 억제
```
floating furniture, toy-like furniture, repeated objects, repeated assets, cloned objects,
unrealistic furniture scale, impossible object placement, levitating decor,
warped furniture, warped shelves, melted furniture, deformed chairs, deformed furniture,
noisy geometry, blurry edges
```

### 10. 인물 해부학 억제
```
mannequin people, render people, entourage people, cutout people, CGI humans, 3D humans,
cloned people, stock-photo models, fashion models, perfect skin, plastic skin, wax skin,
AI beauty face, fake crowd, distorted faces, blurry faces, broken hands, bad anatomy,
extra limbs, oversized people, tiny people, unrealistic anatomy
```

### 11. 조명/렌더 아티팩트 억제
```
fantasy lighting, excessive bloom, artificial glow, fake ambient occlusion, extreme HDR, overexposure,
oversharpening, glowing corners, halo effects, unrealistic shadow gradients,
artificial bounce light, fake global illumination, fake ambient lighting,
surreal lighting, synthetic atmosphere, unrealistic ceiling lighting,
incorrect lighting direction, noisy render artifacts
```

### 12. 텍스트/로고/워터마크 억제
```
random text, logo, watermark, fake typography, distorted letters, readable fake signage
```

### 13. 공간별 조건부 억제

거실: `showroom perfection, luxury showroom look, staged catalog appearance, empty sterile space`
주방: `fake marble veining, impossible appliance reflections, oversized kitchen island, floating cabinetry`
침실: `perfectly smooth bedding, floating blankets, unrealistic fabric tension`
욕실: `mirror distortion, fake wet reflections, impossible tile alignment, unrealistic water behavior`
오피스: `fake monitor glow, repeated office chairs, cloned desks, unrealistic workstation spacing`
로비/공공: `impossible scale, fake luxury materials, sci-fi architecture, empty sterile space`
레스토랑: `fake food, impossible occupancy density, cloned diners, unrealistic hospitality lighting`
공통 품질: `low resolution, noisy geometry, blurry materials, missing architectural details, synthetic textures`

### 14. 리모델링 보호 (2장 모드에만)
```
copied geometry from the second reference image, copied room structure from the second reference image,
replaced architecture from the second image, structural transfer from reference image
```

---

## 공간 유형별 접근

### 거실
재료: 오크/월넛 바닥, 패브릭 소파, 린넨 커튼, 텍스처 러그, 매트 스톤 테이블
디테일: 쿠션 압축, 패브릭 주름, 러그 변형, TV 반사, 일상 소품
조명: 간접 자연광 + 소프트 앰비언트. 상업 조명 금지
카메라: 24–35mm 광각, 눈높이

### 주방
재료: 쿼츠 카운터탑, 세라믹 타일, 스테인리스 가전, 캐비닛 엣지
디테일: 카운터탑 반사, 물 자국, 가전 이음새, 싱크 깊이감
조명: 자연광 + 태스크 + 언더캐비닛 LED
카메라: 24–35mm

### 침실
재료: 레이어드 패브릭, 소프트 침구, 매트 도장면, 따뜻한 목재
디테일: 베개 변형, 이불 주름, 커튼 반투명성
조명: 소프트 저대비, 간접광, 따뜻한 스탠드
카메라: 24–35mm

### 욕실 (반사 억제 최강)
재료: 세라믹 타일 줄눈, 자연석 다공성, 브러시드 니켈
디테일: 거울 깊이감, 물 자국, 실리콘 이음새, 배수구
조명: 디퓨즈드 미러 조명, 컨트롤된 하이라이트
카메라: 24mm 광각 또는 24–28mm

### 오피스/작업공간
재료: 어쿠스틱 패널, 매트 데스크, 상업용 카펫, 금속 프레임
디테일: 케이블 관리, 모니터 글로우, 의자 마모
조명: 기능적 확산 조명, 자연광 균형, 3000–4000K
카메라: 24–35mm 광각

### 공공 로비/서비스홀
재료: 라지 포맷 스톤/타일, 어쿠스틱 패브릭 패널, 금속 트림
디테일: HVAC 디퓨저, 사이니지 마운팅, 카운터 엣지, 출입 게이트
조명: 3000K–4000K 기관 조명, 계층적 건축 조명
카메라: 24mm 광각

### 레스토랑/카페
재료: 텍스처드 우드, 스톤 테이블탑, 세라믹, 따뜻한 금속, 업홀스터리
디테일: 테이블 세팅, 의자 어긋남, 유리잔 반사, 서비스 흔적
조명: 카페=소프트 자연광 / 레스토랑=낮은 조도, 로컬 조명 풀
카메라: 24–35mm

---

## 예시

### 단일 모드 — 한국 공공 도서관 서비스홀

```
PROMPT
Ultra photorealistic architectural interior photography of a modern Korean public library service center converted from a CGI architectural render while preserving the exact original camera position, eye-level perspective, composition, room proportions, ceiling layout, U-shaped service counter placement, modular shelving wall configuration, long table and chair arrangement, circulation, and spatial hierarchy. Transform the space into a believable built interior with realistic materiality and architectural detailing. Preserve exactly the original design color palette without any change, reinterpretation, or color shift — convert CGI surface quality to photographic realism only, do NOT redesign or recolor any material. mustard yellow and warm golden ochre — counter front panels, shelving units, ceiling soffit band; dusty rose and mauve — all wall surfaces; cobalt blue — all chair shells; teal and cyan — shelving accent panel insets; dark walnut brown — suspended ceiling slat baffles; light natural oak — long table surface; gray — large-format floor tiles; white matte — ceiling panels, gate frame, and countertop. Preserve the suspended dark walnut wood ceiling baffles exactly as shown, but render them with authentic walnut grain variation, slight tonal inconsistencies, micro scratches, realistic recessed lighting trim depth, and believable mounting hardware. Preserve the mustard yellow modular shelving wall exactly as shown, but render with realistic acoustic fabric surface tension on counter panels, visible weave texture, panel seams, and matte surface absorption. The cobalt blue polypropylene chairs feature realistic plastic surface with soft specular highlights on curves, slight seat deformation, thin black metal legs with natural wear. The light natural oak long table shows authentic wood grain, subtle pore texture, low-sheen satin finish, and believable edge detailing. Large-format gray porcelain floor tiles with realistic grout line variation, subtle tonal differences between tiles, slight wear near circulation zones. Dusty rose matte plaster walls with soft surface texture, realistic paint absorption, shadow at corners. Include HVAC diffusers, electrical outlets, signage mounting details, ceiling mounting hardware, counter edge profiles, shelf hardware, realistic monitor stands with cables, reception accessories, and minimal institutional clutter. Physically believable furniture scale, realistic object placement, and subtle everyday institutional presence. Warm institutional recessed ceiling downlights with realistic localized illumination pools and trim ring depth, soft linear LED strips with believable luminance falloff, controlled 3000K–4000K institutional lighting, soft shadow gradients, controlled exposure balance between bright exterior windows and interior shadow detail, subtle photographic sensor grain. Replace the CGI figure with a realistic casually dressed Korean woman captured candidly from behind with natural body proportions, realistic hair strands, natural clothing folds, authentic skin texture, and believable posture. The final result must feel like a professionally photographed real built interior space. Ultra high detail, natural color science, realistic dynamic range, editorial architectural photography quality. Captured as a professional full-frame architectural interior photograph using a 24mm lens, indistinguishable from a real built environment. No render look, no archviz appearance, no plastic materials, no fake reflections, no synthetic atmosphere. Completely believable real-world interior photograph.

NEGATIVE
cartoon, anime, illustration, sketch, watercolor, concept art, matte painting, stylized, painterly, CGI, archviz look, render look, Unreal Engine look, Blender render look, game-engine look, SketchUp look, Rhino viewport look, Revit model look, Enscape look, D5 Render look, Lumion look, Twinmotion look, V-Ray render look, Corona render look, clay render, white model, artificial rendering, synthetic lighting, fake global illumination, plastic rendering, showroom CGI materials, changed camera angle, changed viewpoint, changed perspective, changed framing, changed crop, reframed shot, perspective reinterpretation, altered focal length feel, changed color palette, recolored surfaces, altered material colors, color shift, changed accent color, changed wall color, changed upholstery color, material redesign, replaced materials, color reinterpretation, desaturated colors, changed room geometry, changed ceiling height, changed ceiling shape, changed wall positions, changed floor level, wrong scale, unrealistic proportions, redesigned architecture, distorted room, enlarged room, warped walls, deleted architectural elements, moved walls, moved shelving, moved counter, missing ceiling elements, floating architectural elements, missing architectural details, plastic materials, fake wood, fake stone, fake glass, flat painted surfaces, unrealistic textures, fake reflections, oversmoothed surfaces, texture repetition, procedural textures, glossy plastic wood, glossy plastic surfaces, artificial textures, incorrect material scale, unrealistic wood texture, mirror glass, flat glazing, impossible reflections, floating furniture, toy-like furniture, repeated objects, cloned objects, unrealistic furniture scale, warped furniture, warped shelves, deformed chairs, noisy geometry, blurry edges, mannequin people, render people, entourage people, cutout people, CGI humans, 3D humans, cloned people, stock-photo models, fashion models, perfect skin, plastic skin, wax skin, AI beauty face, distorted faces, blurry faces, broken hands, bad anatomy, extra limbs, oversized people, tiny people, fantasy lighting, excessive bloom, artificial glow, fake ambient occlusion, extreme HDR, overexposure, oversharpening, glowing corners, halo effects, fake global illumination, surreal lighting, synthetic atmosphere, unrealistic ceiling lighting, incorrect lighting direction, noisy render artifacts, random text, logo, watermark, impossible scale, fake luxury materials, sci-fi architecture, empty sterile space, low resolution, blurry materials
```

### 리모델링 모드 — 이미지1(화이트모델 주방) + 이미지2(미드센추리 모던)

```
PROMPT
Use Image 1 as the immutable architectural structure, room geometry, camera, composition, and spatial reference, and use Image 2 only as the remodeling style, material, furniture, lighting, and atmosphere reference. Ultra photorealistic architectural interior photography of a contemporary Korean apartment kitchen applying mid-century modern design language from Image 2 while preserving the exact original camera position, eye-level perspective, lens perspective, composition, room proportions, ceiling height, wall positions, window placement, and all architectural structure from Image 1. Transform the space into a believable built interior with realistic materiality and architectural detailing. Preserve exactly the original design color palette without any change — convert CGI surface quality to photographic realism only, do NOT redesign or recolor any material. Warm walnut flat-front cabinetry with realistic wood grain variation, subtle panel seams, believable edge banding, and shadow gaps. Preserve the countertop position exactly as shown, but render with quartz surface showing natural stone veining, diffuse reflections, realistic edge detailing, and subtle surface imperfections. Ceramic tile backsplash with realistic grout lines and subtle surface variation. Brushed brass hardware and faucet with controlled specular highlights and directional metallic texture. Include subtle countertop reflections, realistic appliance tolerances, believable cabinet joints, HVAC diffusers, outlet positions, and edge conditions. Realistic kitchen objects: fruit bowl, dish towels, cutting board, small appliances at proper scale. Balanced natural daylight with realistic task lighting, under-cabinet LED warm glow, controlled exposure balance between bright exterior window and interior luminance, subtle photographic sensor grain. The final result must feel like a professionally photographed real built interior space. Ultra high detail, natural color science, realistic dynamic range, editorial architectural photography quality. Captured as a professional full-frame architectural interior photograph using a 24mm lens, indistinguishable from a real built environment. No render look, no archviz appearance, completely believable real-world interior photograph.

NEGATIVE
cartoon, anime, illustration, sketch, watercolor, concept art, matte painting, stylized, CGI, archviz look, render look, Unreal Engine look, Blender render look, game-engine look, SketchUp look, Enscape look, D5 Render look, Lumion look, Twinmotion look, V-Ray render look, Corona render look, clay render, plastic rendering, showroom CGI materials, changed camera angle, changed viewpoint, changed perspective, changed framing, reframed shot, changed color palette, recolored surfaces, altered material colors, color shift, material redesign, replaced materials, changed room geometry, changed ceiling height, changed wall positions, changed window placement, wrong scale, unrealistic proportions, redesigned architecture, distorted room, warped walls, deleted architectural elements, moved walls, moved windows, missing architectural details, plastic materials, fake wood, fake stone, fake glass, flat painted surfaces, fake reflections, oversmoothed surfaces, texture repetition, procedural textures, glossy plastic wood, glossy plastic surfaces, artificial textures, incorrect material scale, showroom CGI materials, mirror glass, flat glazing, impossible reflections, floating furniture, toy-like furniture, repeated objects, cloned objects, unrealistic furniture scale, warped furniture, deformed chairs, mannequin people, render people, entourage people, cutout people, CGI humans, 3D humans, fashion models, perfect skin, plastic skin, wax skin, AI beauty face, distorted faces, blurry faces, broken hands, bad anatomy, fantasy lighting, excessive bloom, artificial glow, fake ambient occlusion, extreme HDR, glowing corners, fake global illumination, surreal lighting, synthetic atmosphere, incorrect lighting direction, random text, logo, watermark, fake marble veining, impossible appliance reflections, oversized kitchen island, floating cabinetry, low resolution, noisy geometry, blurry materials, copied geometry from the second reference image, copied room structure from the second reference image, structural transfer from reference image
```

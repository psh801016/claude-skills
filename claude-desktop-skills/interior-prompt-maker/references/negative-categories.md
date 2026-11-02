# NEGATIVE 14카테고리 토큰 (interior-prompt-maker, SD/ComfyUI 전용)

SKILL.md 'NEGATIVE 작성' 절의 토큰 판정 규칙·중복 제거 규칙이 이 문서 전체에 적용된다. 카테고리 순서를 바꾸지 않고 한 단락에 잇는다.

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

### 3. 카메라 오염 억제 (★ SD/MJ/ComfyUI 디퓨전 전용 — GPT image에는 NEGATIVE 자체를 넣지 않는다)
```
changed camera angle, changed viewpoint, changed perspective, changed framing, changed crop,
changed composition, changed lens perspective, reframed shot, perspective reinterpretation,
altered focal length feel
```
**주의:** `wider angle of view`, `expanded field of view`, `added side columns`, `letterboxed`, `zoomed-in composition`, `distorted wide-angle view` 같이 **결과 장면을 직접 묘사·호명하는 토큰은 넣지 않는다** — 의미기반 모델에서 오히려 그 장면을 그리게 만든다. 판별 기준: '변형 행위'를 명명하는 토큰(`changed/altered X`)은 허용, '결과 장면'을 묘사하는 토큰은 금지. SD에서도 이 카테고리는 위 추상 항목 수준으로만 유지한다.

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
incorrect material scale, unrealistic wood texture
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
artificial bounce light, fake ambient lighting,
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
전시부스/전시장 (★SD/MJ 디퓨전 전용 · GPT엔 미사용 · 증상 직접호명 배제, 추상 명사만): `seamless drywall booth without visible panel seams, single flat featureless wall, dissolved modular grid, readable fascia text, fake company logo, legible signage typography, light source without a fixture, non-geometric aluminum, wrong module proportions, oversized booth`
> 주의: `melting / warped / bent / garbled / floating / melted / tangled` 같은 동사형 증상 토큰은 넣지 않는다 — 의미기반 모델에서 오히려 그 증상을 그린다. 위처럼 '정상상태의 부재 / 비정상 명사'로만 억제한다.
공통 품질: `low resolution, noisy geometry, blurry materials, missing architectural details, synthetic textures`

### 14. 리모델링 보호 (2장 모드에만)
```
copied geometry from the second reference image, copied room structure from the second reference image,
replaced architecture from the second image, structural transfer from reference image
```

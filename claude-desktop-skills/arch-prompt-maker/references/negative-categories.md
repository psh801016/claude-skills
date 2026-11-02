# NEGATIVE 15카테고리 토큰 (arch-prompt-maker, SD/MJ/ComfyUI 전용)

SKILL.md 'NEGATIVE 작성' 절의 토큰 판정 규칙·중복 제거 규칙이 이 문서 전체에 적용된다. 카테고리 순서를 바꾸지 않고 한 단락에 잇는다.

### A. 카메라 실패 (항상 첫 번째)
```
changed camera angle, changed viewpoint, changed camera position, changed camera height,
changed tilt, changed yaw, changed framing, changed crop, changed horizon, changed perspective,
changed lens feel, orbit camera, zoom change, reframed composition, recropped image,
tilted architecture, distorted perspective lines, warped verticals
```

### B. 구도 실패
```
altered composition, shifted focal hierarchy, unstable horizon, exaggerated perspective,
changed foreground/background relationship, changed vertical alignment
```

### C. 기하학 실패 (핵심)
```
changed building shape, changed massing, changed facade design, changed silhouette,
changed proportions, changed floor count, changed roofline, changed terrace shape,
changed balcony shape, changed railing geometry, changed opening sizes, changed window proportions,
changed glazing divisions, changed mullion spacing, changed structural edges, changed slab edges,
changed column positions, changed road alignment, changed site levels,
changed retaining wall position, changed landscape boundary,
changed fence layout, changed gate geometry, changed loading dock position
```

### D. 컬러 오염 억제 ★
```
changed color palette, recolored facade, changed material colors, altered facade colors,
color reinterpretation, material color redesign, changed accent color, changed glazing tint,
desaturated colors, oversaturated colors, unexpected color introduction, color shift, material redesign
```

### E. 건축 재설계 실패
```
redesigned architecture, distorted geometry, deformed building, deleted architectural elements,
added random architectural elements, simplified architecture, missing architectural details,
altered facade rhythm, random balconies, random skylights, asymmetrical facade mutation,
fantasy architecture, warped facade
```

### F. 스케일 실패
```
wrong scale, wrong human scale, oversized people, tiny people, giant trees,
oversized furniture, miniature vehicles, toy-like objects, inaccurate scale
```

### G. CGI/렌더 스타일 억제 (항상 포함)
```
CGI, archviz look, render look, SketchUp look, Rhino viewport look, Revit model look,
clay render look, white model look, Lumion look, Enscape look, D5 render look,
Twinmotion look, V-Ray render look, Corona render look, Unreal render look, Blender render look,
game-engine look, concept art, illustration, cartoon, anime style,
AI-generated aesthetic, showroom rendering, polished visualization, synthetic environment, fake realism
```

### H. 재료 실패
```
plastic materials, fake reflections, muddy textures, unrealistic concrete, fake stone,
fake wood, flat painted surfaces, repeated texture, noisy material,
over-clean materials, perfect surfaces, procedural stone texture, procedural texture,
oversaturated wood grain, metallic plasticity, texture stretching, low-detail facade
```

### I. 유리/반사 실패 (H와 분리)
```
mirror glass, flat glass, black mirror glass, black void windows, empty glazing, textureless glazing,
overreflective curtain wall, impossible reflections, glowing windows,
inconsistent reflections, fake transparency, infinite mirror effect, flat blank glazing
```

### J. 조경 실패
```
repeated trees, cloned trees, procedural vegetation, rendering-library trees,
identical canopies, repeated shrubs, synthetic grass, fake planting,
plastic leaves, artificial grass, floating vegetation,
tropical vegetation mismatch, floating landscape, impossible terrain
```

### K. 인물 실패
```
repeated people, cloned figures, mannequin people, CGI humans, floating people,
deformed people, broken hands, distorted faces, unrealistic skin,
fashion pose, fashion-model posing, exaggerated gestures,
giant pedestrians, crowd duplication, extra limbs, melted anatomy
```

### L. 차량/대지 실패
```
fake cars, toy-like cars, unrealistic road texture, floating vehicles,
impossible parking, distorted lane markings, unrealistic sidewalks, broken curb geometry,
clean showroom streets, perfect paving, spotless sidewalks, no urban wear,
fake asphalt texture, procedural pavement, unrealistic curb geometry
```

### M. 조명 실패
```
fantasy lighting, excessive bloom, fake ambient occlusion, extreme HDR,
overexposed highlights, oversharpening, halo artifacts,
cinematic teal-orange grading, dramatic sci-fi atmosphere,
neon reflections, heavy fog, volumetric effects, unreal lighting,
fake sunset glow, neon glow, unrealistic night lighting,
overdramatic shadows, fake god rays, cinematic haze
```

### N. 이미지 품질 실패
```
blurry materials, noisy image, smeared texture, low-detail facade,
compression artifacts, watercolor texture, painterly surface,
painterly effect, cartoon effect, stylized illustration, surrealism
```

### O. 텍스트/오염 (항상 마지막)
```
random text, readable fake signage, logo, watermark, UI overlay,
subtitle text, fake branding, QR codes, poster graphics, graphic overlay
```

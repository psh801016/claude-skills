---
name: cinematic-exhibition-lighting
description: >
  인테리어·건축·행사 공간 이미지(Image 1)에 레퍼런스 이미지(Image 2)의 시네마틱 전시 조명을
  이식하는 전문 스킬. 구조·카메라·재료·가구·오브젝트는 Image 1 기준으로 4중 완전 잠금,
  조명·색온도·분위기·볼류메트릭 효과만 Image 2에서 추출하여 적용한다.

  이 스킬은 아래 상황에서 반드시 사용한다:
  - "조명 바꿔줘", "이 조명으로 바꿔줘", "레퍼런스 조명 적용해줘", "조명 이식"
  - "분위기 바꿔줘", "드라마틱하게", "시네마틱 조명", "전시 느낌으로"
  - "갤러리 분위기로", "뮤지엄 조명", "공연장 느낌", "행사장 조명"
  - "CGI 렌더에 조명 입혀줘", "이미지에 이 조명 써줘"
  - "lighting transfer", "exhibition lighting", "stage lighting apply"
  - 이미지 2장과 함께 조명·분위기 변환 요청이 들어오는 모든 경우

  지원 공간: 거실·침실·주방·오피스·카페·호텔 로비·컨퍼런스홀·이벤트홀·
  전시관·갤러리·공연장·행사장·의료공간·상업공간 — 모든 실내외 공간.

  입력: Image 1 (원본 공간) + Image 2 (조명 레퍼런스, 선택) + 색온도 키워드 (선택)
  출력 — 메인 변환: PROMPT + NEGATIVE
         조명 레이어: LIGHT LAYER PROMPT + LIGHT LAYER NEGATIVE (txt2img, 포토샵 합성용)
         익스트림 다크: EXTREME DARK PROMPT + NEGATIVE + MAGNIFIC SETTINGS (Magnific img2img 전용)
         둘 다 요청 시: 두 세트 순서대로 출력

  건물 외관 실사화는 arch-prompt-maker, 조명 변환 없는 일반 실사화는 interior-prompt-maker 사용.
---

# 시네마틱 전시 조명 마스터

인테리어·건축·행사 공간에 시네마틱 전시 조명을 이식한다.
구조는 4중 완전 잠금 — 오직 조명·분위기만 변환.

## 출력 모드

| 모드 | 트리거 | 출력 |
|---|---|---|
| **메인 변환** | 기본 (조명 변환 요청) | PROMPT + NEGATIVE |
| **조명 레이어** | "레이어만", "빛만", "포토샵 합성용", "블랙 배경 조명", "조명 레이어" | LIGHT LAYER PROMPT + LIGHT LAYER NEGATIVE |
| **익스트림 다크** | "극단적으로 어둡게", "실루엣만", "빛만 살려", "나머지 다 블랙", "어둡게 눌러", "다크 실루엣", "Magnific 다크" | EXTREME DARK PROMPT + NEGATIVE |
| **둘 다** | "둘 다", "레이어도", "합성도 같이" | 두 세트 모두 출력 |

## 빠른 흐름

1. **출력 모드 판단** (위 표 참조)
2. **입력 확인**: Image 1 (원본) + Image 2 (조명 레퍼런스) + 색온도 키워드 (선택)
3. **Image 2 조명 분석** (아래 "조명 추출 가이드" 참조)
4. **색온도 판단** (아래 색온도 판단표 참조)
5. **메인 변환** → 4중 잠금 + PROMPT + NEGATIVE
6. **조명 레이어** → LIGHT LAYER PROMPT + LIGHT LAYER NEGATIVE
7. **익스트림 다크** → EXTREME DARK PROMPT + NEGATIVE + Magnific 설정값

카메라 브랜드(Sony, Canon, Hasselblad 등) 절대 명시하지 않는다.
MJ 파라미터(`--v`, `--iw`, `--ar` 등) 절대 포함하지 않는다.

## 출력 원칙

설명·분석·주석·이미지 생성 없음. 프롬프트 섹션만 출력.
모든 PROMPT·LIGHT LAYER PROMPT는 **하나의 연속된 영어 단락**.

**메인 변환 출력 형식:**
```
PROMPT
[연속 영어 단락]

NEGATIVE
[연속 영어 단락]
```

**조명 레이어 출력 형식:**
```
LIGHT LAYER PROMPT
[연속 영어 단락]

LIGHT LAYER NEGATIVE
[연속 영어 단락]
```

**둘 다 출력 시:** 메인 변환 세트 → 빈 줄 → 조명 레이어 세트 순서로.

---

## Image 2 조명 추출 가이드

Image 2에서 아래 5가지 요소만 읽는다. 구조·재료·가구·텍스트·로고는 무시한다.
Image 2에 워터마크나 텍스트가 있어도 조명 특성 추출에만 집중하고 NEGATIVE에서 텍스트 억제.

| 추출 요소 | 읽는 내용 |
|---|---|
| **빔 패턴** | 방사형·교차형·수직형·사이드형 등 빛줄기 방향과 배열 |
| **광원 위치** | 천장 트러스·사이드·무대 앞·측면 등 주 광원 위치 |
| **색온도 비율** | 쿨/웜 비율, 주조명 색 vs 보조 색 |
| **대비 레벨** | 주변 암부 깊이, 빛/어둠 대비 강도 |
| **분위기 밀도** | 헤이즈/먼지 밀도, 볼류메트릭 강도 |

---

## 색온도 판단표

| 사용자 키워드 | 적용 모드 |
|---|---|
| Cold Blue, 차분한 푸른빛, 쿨톤, 블루, 차갑게 | Cool Blue |
| Warm Amber, 따뜻한 앰버빛, 웜톤, 금빛, 황금, 따뜻하게 | Warm Amber |
| 혼합, 블루+골드, 쿨+웜, Mixed | Mixed |
| 미지정 + Image 2 있음 | Image 2 색온도 분석 후 위 3가지 중 가장 가까운 모드 선택 |
| 미지정 + Image 2 없음 | Neutral Cinematic (기본값) |

---

## PROMPT 작성 순서 (10단계, 엄격히 준수)

### 1. 이미지 역할 선언 (첫 문장)

> `"Use Image 1 as the immutable architectural structure, room geometry, camera position, composition, original materials, surface finishes, furniture layout, and all spatial elements. Extract ONLY the lighting direction, beam pattern, color temperature, contrast ratio, volumetric quality, and atmospheric mood from Image 2 — do not transfer any structural, material, spatial, stylistic, or textual content from Image 2."`

---

### 2. 카메라 잠금

> `"Preserve exactly the original camera position, camera height, viewing angle, lens perspective, focal length feel, framing, crop, composition, horizon line, tilt, yaw, and perspective alignment from Image 1. No camera change, no reframing, no recropping, no zoom change, no perspective reinterpretation."`

광각 이미지인 경우 추가:
> `"Preserve the original wide-angle interior lens feel without altering spatial perspective."`

---

### 3. 방 기하학 잠금

```
Preserve exactly the original room proportions and spatial hierarchy from Image 1.
Preserve the original ceiling height, ceiling shape, soffits, bulkheads, recessed areas, and architectural ceiling structure.
Preserve all wall positions, partitions, corners, and architectural boundaries.
Maintain the original floor height and level transitions.
Preserve window placement, door positions, openings, and circulation paths.
Preserve all columns, stairs, built-in architectural elements, fixed cabinetry, and structural lines.
Do not move, scale, rotate, deform, simplify, delete, or reinterpret any architectural element.
```

**행사장·무대 공간 추가:**
```
Preserve the original stage platform, stage steps, and stage-floor level transitions.
Preserve all LED screen positions, screen sizes, and screen frame structures exactly.
Preserve all side panel positions and branded display panel placements.
```

---

### 4. 재료 + 가구 + 오브젝트 잠금 (핵심)

> `"Preserve the original materials, surface finishes, textures, and color palette of all architectural and decorative elements exactly as they appear in Image 1. Preserve the original furniture layout, furniture design, seating arrangement, object placement, and all fixtures. Do not substitute, replace, upgrade, recolor, or alter any material, finish, furniture piece, seating unit, or object. The lighting transformation must reveal and enhance the existing surfaces — not change them."`

**LED 스크린·디지털 디스플레이가 있는 경우 추가:**
> `"Preserve the LED screen and display panel structures and frame positions. Screen content and display imagery may be atmospherically adapted to the new lighting mood while maintaining screen placement and scale."`

---

### 5. 공간 정체성 선언

공간 유형을 파악하여 한 문장으로 선언:

**주거 공간:**
- `"Dark cinematic exhibition rendering of the original residential living room with all original elements preserved"`
- `"Cinematic dramatic lighting applied to the original bedroom interior with full material and furniture fidelity"`

**상업·업무 공간:**
- `"Exhibition-quality dramatic lighting transformation of the original office workspace, all materials and furniture unchanged"`
- `"Cinematic museum-grade lighting applied to the original hotel lobby interior with full architectural fidelity"`
- `"Dramatic stage lighting applied to the original café interior with all original furnishings and surfaces preserved"`

**행사·전시 공간:**
- `"Cinematic event-grade lighting transformation of the original conference hall with all seating, screens, and architectural structure preserved"`
- `"Dramatic exhibition lighting applied to the original convention hall interior with stage, LED screens, and seating unchanged"`
- `"Cinematic concert-grade lighting atmosphere applied to the original event hall with full architectural and equipment fidelity"`

---

### 6. 볼류메트릭 전시 조명 (항상 포함)

Image 2에서 추출한 빔 패턴·광원 위치를 반영하여 작성:

> `"Apply dramatic exhibition-grade lighting with strong volumetric light beams visible in the air, using directional spotlights from ceiling and side angles referencing the [빔 패턴 묘사] lighting composition of Image 2. Include subtle haze and dust particles floating within the light rays to enhance depth and atmospheric realism. Add refined sparkling highlights on reflective surfaces and secondary light elements, generating soft shimmering glints without overexposure or neon effects. Ensure controlled glossy reflections and premium stage-grade lighting quality. Maintain high contrast between deep surrounding darkness and focused light pools. No fantasy or illustration style — cinematic professional event hall mood only."`

빔 패턴 묘사 예시:
- 방사형: `"fan-radiating beam pattern from overhead ceiling truss"`
- 교차형: `"crossing diagonal beam spotlights from left and right ceiling positions"`
- 수직 집중: `"tight vertical spotlights from ceiling grid focused on stage area"`
- 사이드 플러드: `"side-wash beams from left and right wall positions"`

---

### 7. 색온도 적용 (4모드 중 1개 선택)

**Cool Blue 모드:**
> `"Apply deep cool blue color temperature throughout the dramatic spotlights and ambient atmosphere. Use deep blues, crisp silvers, and cold white light for the volumetric beams and spotlight illumination. Cool-toned shadows with icy ambient fill and sophisticated blue-silver atmospheric depth."`

**Warm Amber 모드:**
> `"Apply warm amber color temperature throughout the dramatic spotlights and ambient atmosphere. Use rich warm ambers, deep golds, and brown-toned darkness for the volumetric beams and spotlight illumination. Warm-toned shadows with golden ambient fill and luxurious amber-gold atmospheric depth."`

**Mixed 모드 (쿨+웜 혼합):**
> `"Apply a cinematic mixed color temperature with dominant cool blue primary spotlights and warm amber secondary accent lights. Deep blue volumetric main beams from ceiling, warm gold side accent illumination at lower positions, creating layered depth and premium event-lighting atmosphere. Cool-dominated overall mood with warm accent counterpoints."`

**Neutral Cinematic 모드 (기본값):**
> `"Apply sophisticated neutral-to-cool cinematic color temperature. Museum-grade neutral white spotlights with subtle cool undertones, controlled neutral ambient fill, and refined cinematic atmospheric depth."`

---

### 8. 표면 디테일 보존

> `"Maintain all original surface micro-details from Image 1 including material grain variation, seams, joint lines, edge conditions, construction tolerances, shadow gaps, and believable surface aging. The dramatic lighting must reveal and enhance these existing architectural details — not flatten or override them."`

---

### 9. 사진 리얼리즘 선언

> `"The final result must feel like a professionally photographed cinematic event space — ultra-realistic photo quality with exhibition-grade lighting and atmosphere. True photographic realism, not a CGI render or digital composite. The space must feel physically real and architecturally believable."`

---

### 10. 최종 anti-CGI + 오염 방지 (마지막 문장)

> `"No render look, no archviz appearance, no plastic materials, no fake reflections, no Unreal Engine look, no SketchUp appearance, no clay-render feeling, no illustration style, no fantasy elements. Completely believable real-world cinematic photograph. No material changes from Image 1, no structural changes from Image 1, no furniture or seating changes from Image 1, no screen content fully replaced from Image 2."`

---

## NEGATIVE 작성 순서 (15카테고리, 순서 엄수)

### 1. 스타일화 억제
```
cartoon, anime, illustration, sketch, watercolor, concept art, matte painting,
stylized, painterly, fantasy, sci-fi, surreal
```

### 2. 렌더/CGI 억제
```
CGI, archviz look, render look, Unreal Engine look, Blender render look,
game-engine look, SketchUp look, Rhino viewport look, clay render, white model,
obvious 3D render, artificial rendering, synthetic lighting, fake global illumination, plastic rendering
```

### 3. 카메라 오염 억제
```
changed camera angle, changed viewpoint, changed perspective, changed framing, changed crop,
changed composition, reframed shot, perspective reinterpretation, altered focal length feel,
distorted wide-angle view, zoomed-in composition, zoomed-out composition
```

### 4. 기하학 오염 억제
```
changed room geometry, changed room proportions, changed ceiling height, changed ceiling shape,
changed wall positions, changed floor level, changed window placement, changed door positions,
distorted room, enlarged room, shrunken room, warped walls, melted architecture
```

### 5. 구조 수정 억제
```
deleted architectural elements, moved walls, moved windows, moved doors,
added structural elements, fake openings, extra columns, altered circulation path,
missing ceiling elements, floating architectural elements
```

### 6. 재료 오염 억제 (핵심)
```
changed materials, replaced materials, upgraded materials, substituted surface finishes,
recolored surfaces, material transfer from Image 2, style transfer from Image 2,
changed floor finish, changed wall material, changed ceiling material,
new material applied, different texture applied
```

### 7. 가구·오브젝트·좌석 오염 억제 (핵심)
```
moved furniture, repositioned objects, changed furniture design, new furniture added,
replaced furniture, removed furniture, upgraded furniture, added decorative objects,
removed original objects, exhibition pedestals added, display props added,
furniture from Image 2 transferred, changed seating arrangement, removed seating rows,
added audience seating, rearranged chairs
```

### 8. 행사장·무대 장비 오염 억제
```
added stage equipment, speaker towers added, truss structures added,
lighting rigs added, scaffolding added, added PA system, added stage monitors,
moved stage position, changed stage size, added concert equipment,
changed LED screen content entirely, replaced screen imagery, modified display content
```

### 9. 과도한 광원 억제
```
neon lights, LED strip overexposure, excessive bloom, overexposed spotlights,
blown highlights, halo effects, fake lens flares, glowing corners,
unrealistic ambient occlusion, flat fill lighting, equally lit entire space
```

### 10. 유리·반사 오염 억제
```
mirror glass, impossible reflections, floating reflections, fake reflections,
unrealistic glass, opaque glass, incorrect transparency
```

### 11. 원본 조명 잔류 억제
```
bright daylight, natural daylight, window sunlight, residential warm lighting,
studio photography lighting, flat even lighting, overhead fluorescent lighting,
original lighting unchanged, daytime interior look
```

### 12. 텍스트·로고·워터마크 억제
```
random text, readable signage, logo, watermark, fake typography,
exhibition labels, gallery placard text, distorted letters,
watermark from reference image, stock photo watermark
```

### 13. 인물 억제 (원본에 인물 없는 경우)
```
mannequin people, cloned people, distorted faces, broken hands, bad anatomy,
exhibition visitors, gallery viewers, added audience, added people, added presenters
```

### 14. 판타지·비현실 억제
```
fantasy elements, magical atmosphere, surreal lighting, ethereal glow,
impossible physics, holographic elements, sci-fi architecture, dreamlike atmosphere
```

### 15. Image 2 구조 전이 억제
```
copied geometry from Image 2, copied room structure from Image 2,
structural content from reference image, spatial layout from reference image,
architectural transfer from reference image, furniture from reference image,
stage layout from reference image, ceiling structure from reference image
```

---

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

**② 비율 선언 — Image 1과 동일하게 (항상 포함)**
> `"Match the exact aspect ratio and frame dimensions of Image 1 so this layer aligns perfectly for compositing."`

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
LIGHT LAYER NEGATIVE
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

---

## 예시

### Warm Amber — 거실 공간

```
PROMPT
Use Image 1 as the immutable architectural structure, room geometry, camera position, composition, original materials, surface finishes, furniture layout, and all spatial elements. Extract ONLY the lighting direction, beam pattern, color temperature, contrast ratio, volumetric quality, and atmospheric mood from Image 2 — do not transfer any structural, material, spatial, stylistic, or textual content from Image 2. Preserve exactly the original camera position, camera height, viewing angle, lens perspective, focal length feel, framing, crop, composition, horizon line, and perspective alignment from Image 1. No camera change, no reframing, no recropping, no zoom change, no perspective reinterpretation. Preserve exactly the original room proportions and spatial hierarchy from Image 1. Preserve the original ceiling height, ceiling shape, and architectural ceiling structure. Preserve all wall positions, partitions, and architectural boundaries. Preserve window placement, door positions, and circulation paths. Do not move, scale, rotate, deform, or reinterpret any architectural element. Preserve the original materials, surface finishes, textures, and color palette of all elements exactly as they appear in Image 1. Preserve the original furniture layout, furniture design, and object placement. Do not substitute, replace, or alter any material, finish, furniture piece, or object. Dark cinematic exhibition rendering of the original residential living room with all original elements preserved. Apply dramatic exhibition-grade lighting with strong volumetric light beams visible in the air, using directional spotlights from ceiling and side angles referencing the lighting composition of Image 2. Include subtle dust particles floating within the light rays to enhance depth and atmospheric realism. Add refined sparkling highlights on reflective surfaces, generating soft shimmering glints without overexposure or neon effects. Controlled glossy reflections and premium museum-grade lighting quality. High contrast between deep surrounding darkness and focused light pools. No fantasy or illustration style. Apply warm amber color temperature throughout the dramatic spotlights and ambient atmosphere. Use rich warm ambers, deep golds, and brown-toned darkness for volumetric beams and spotlight illumination. Warm-toned shadows with golden ambient fill and luxurious amber-gold atmospheric depth. Maintain all original surface micro-details from Image 1 including material grain, seams, joint lines, and edge conditions. The final result must feel like a professionally photographed cinematic event space — ultra-realistic photo quality. True photographic realism. No render look, no archviz appearance, completely believable real-world cinematic photograph. No material changes from Image 1, no structural changes from Image 1, no furniture or object changes from Image 1.

NEGATIVE
cartoon, anime, illustration, sketch, watercolor, concept art, matte painting, stylized, painterly, fantasy, sci-fi, surreal, CGI, archviz look, render look, Unreal Engine look, Blender render look, SketchUp look, clay render, plastic rendering, fake global illumination, changed camera angle, changed viewpoint, changed perspective, changed framing, reframed shot, changed room geometry, changed ceiling height, changed wall positions, changed window placement, distorted room, warped walls, deleted architectural elements, moved walls, changed materials, replaced materials, material transfer from Image 2, style transfer from Image 2, changed floor finish, changed wall material, new furniture added, replaced furniture, moved furniture, repositioned objects, neon lights, excessive bloom, overexposed spotlights, blown highlights, halo effects, fake lens flares, flat fill lighting, bright daylight, natural daylight, original lighting unchanged, mirror glass, impossible reflections, fake reflections, random text, logo, watermark, watermark from reference image, fantasy elements, magical atmosphere, impossible physics, copied geometry from Image 2, structural content from reference image
```

### Cool Blue — 오피스 공간

```
PROMPT
Use Image 1 as the immutable architectural structure, room geometry, camera position, composition, original materials, surface finishes, furniture layout, and all spatial elements. Extract ONLY the lighting direction, beam pattern, color temperature, contrast ratio, volumetric quality, and atmospheric mood from Image 2 — do not transfer any structural, material, spatial, stylistic, or textual content from Image 2. Preserve exactly the original camera position, camera height, viewing angle, lens perspective, focal length feel, framing, crop, composition, horizon line, and perspective alignment from Image 1. No camera change, no reframing, no recropping, no zoom change. Preserve exactly the original room proportions and spatial hierarchy from Image 1. Preserve the original ceiling height, ceiling shape, and architectural ceiling structure. Preserve all wall positions, partitions, and architectural boundaries. Preserve window placement, door positions, and circulation paths. Do not move, scale, rotate, deform, or reinterpret any architectural element. Preserve the original materials, surface finishes, textures, and color palette of all elements exactly as they appear in Image 1. Preserve the original furniture layout, furniture design, and object placement. Do not substitute, replace, or alter any material, finish, furniture piece, or object. Exhibition-quality dramatic lighting transformation of the original office workspace, all materials and furniture unchanged. Apply dramatic exhibition-grade lighting with strong volumetric light beams visible in the air, using directional spotlights from ceiling and side angles referencing the lighting composition of Image 2. Include subtle dust particles floating within the light rays to enhance depth and atmospheric realism. Add refined sparkling highlights on reflective surfaces, generating soft shimmering glints without overexposure or neon effects. Controlled glossy reflections and premium stage-grade lighting quality. High contrast between deep surrounding darkness and focused light pools. No fantasy or illustration style. Apply deep cool blue color temperature throughout the dramatic spotlights and ambient atmosphere. Use deep blues, crisp silvers, and cold white light for volumetric beams and spotlight illumination. Cool-toned shadows with icy ambient fill and sophisticated blue-silver atmospheric depth. Maintain all original surface micro-details from Image 1 including material grain, seams, joint lines, and edge conditions. The final result must feel like a professionally photographed cinematic event space — ultra-realistic photo quality. True photographic realism. No render look, no archviz appearance, completely believable real-world cinematic photograph. No material changes from Image 1, no structural changes from Image 1, no furniture or object changes from Image 1.

NEGATIVE
cartoon, anime, illustration, sketch, watercolor, concept art, matte painting, stylized, painterly, fantasy, sci-fi, surreal, CGI, archviz look, render look, Unreal Engine look, Blender render look, SketchUp look, clay render, plastic rendering, fake global illumination, changed camera angle, changed viewpoint, changed perspective, changed framing, reframed shot, changed room geometry, changed ceiling height, changed wall positions, changed window placement, distorted room, warped walls, deleted architectural elements, moved walls, changed materials, replaced materials, material transfer from Image 2, style transfer from Image 2, changed floor finish, changed wall material, new furniture added, replaced furniture, moved furniture, repositioned objects, neon lights, excessive bloom, overexposed spotlights, blown highlights, halo effects, fake lens flares, flat fill lighting, bright daylight, natural daylight, original lighting unchanged, mirror glass, impossible reflections, fake reflections, random text, logo, watermark, watermark from reference image, fantasy elements, magical atmosphere, impossible physics, copied geometry from Image 2, structural content from reference image
```

### Mixed (Cool Blue + Warm Amber) — 컨퍼런스홀 (검증된 예시)

```
PROMPT
Use Image 1 as the immutable architectural structure, room geometry, camera position, composition, original materials, surface finishes, furniture layout, and all spatial elements. Extract ONLY the lighting direction, beam pattern, color temperature, contrast ratio, volumetric quality, and atmospheric mood from Image 2 — do not transfer any structural, material, spatial, stylistic, or textual content from Image 2. Preserve exactly the original camera position, camera height, wide-angle viewing angle, lens perspective, focal length feel, framing, crop, composition, horizon line, and perspective alignment from Image 1. No camera change, no reframing, no recropping, no zoom change, no perspective reinterpretation. Preserve the original wide-angle interior lens feel without altering spatial perspective. Preserve exactly the original room proportions and spatial hierarchy from Image 1. Preserve the original ceiling height, white geometric coffered grid ceiling structure, soffits, recessed lighting strips, and all architectural ceiling elements. Preserve all wall positions, side wall panels, and architectural boundaries. Maintain the original floor level and light oak flooring. Preserve the elevated stage platform with steps, center LED main screen, two side LED branded panels, all seating rows, and center-hung projector. Preserve all LED screen and display panel structures and frame positions. Do not move, scale, rotate, deform, simplify, delete, or reinterpret any architectural or spatial element. Preserve the original materials, surface finishes, and color palette of all elements exactly as they appear in Image 1 — white coffered ceiling, beige textured wall panels, light oak floor, deep blue fabric chair upholstery, LED screen surfaces. Preserve the original seating arrangement and all object placement. Do not substitute, replace, or alter any material, finish, seating unit, or object. Cinematic event-grade lighting transformation of the original conference hall with all seating, screens, and architectural structure preserved. Apply dramatic exhibition-grade lighting with strong volumetric light beams visible in the air, using multiple directional crossing spotlights radiating from the ceiling truss referencing the fan-beam radiating pattern of Image 2. Include subtle haze and dust particles floating within the light rays to enhance depth and atmospheric realism. Add refined sparkling highlights on the LED screen surfaces, metallic trim elements, and reflective floor, generating soft shimmering glints without overexposure or neon effects. Ensure controlled glossy reflections on the polished floor surface and premium stage lighting quality. Maintain high contrast between the deep surrounding darkness and focused light pools illuminating the stage and seating areas. No fantasy or illustration style — cinematic professional conference event hall mood only. Apply a cinematic mixed color temperature with dominant cool blue primary spotlights and warm amber secondary accent lights. Deep blue volumetric main beams from ceiling, warm gold side accent illumination at lower positions, creating layered depth and premium event-lighting atmosphere. Cool-dominated overall mood with warm accent counterpoints. Maintain all original surface micro-details from Image 1 including ceiling panel joints, seat row spacing, stage edge detailing, floor seam lines, and wall panel texture. The final result must feel like a professionally photographed cinematic conference event space — ultra-realistic photo quality with dramatic stage-grade lighting and atmosphere. True photographic realism, not a CGI render or digital composite. No render look, no archviz appearance, no plastic materials, no fake reflections, no Unreal Engine look. Completely believable real-world cinematic photograph. No material changes from Image 1, no structural changes from Image 1, no seating changes from Image 1.

NEGATIVE
cartoon, anime, illustration, sketch, watercolor, concept art, matte painting, stylized, painterly, fantasy, sci-fi, surreal, CGI, archviz look, render look, Unreal Engine look, Blender render look, game-engine look, SketchUp look, Rhino viewport look, clay render, white model, obvious 3D render, artificial rendering, synthetic lighting, fake global illumination, plastic rendering, changed camera angle, changed viewpoint, changed perspective, changed framing, changed crop, changed composition, reframed shot, perspective reinterpretation, altered focal length feel, zoomed-in composition, zoomed-out composition, changed room geometry, changed room proportions, changed ceiling height, changed white coffered ceiling structure, changed wall positions, changed floor level, changed stage position, changed screen placement, distorted room, enlarged room, warped walls, melted architecture, deleted architectural elements, moved walls, moved stage, added structural elements, missing ceiling elements, changed materials, replaced materials, upgraded materials, recolored surfaces, material transfer from Image 2, style transfer from Image 2, changed floor finish, changed wall material, changed ceiling material, changed seat color, changed upholstery, new furniture added, replaced furniture, moved seating rows, repositioned objects, removed LED panels, added stage equipment, speaker towers added, truss structures added, lighting rigs added, scaffolding added, added concert equipment, neon lights, LED strip overexposure, excessive bloom, overexposed spotlights, blown highlights, halo effects, fake lens flares, glowing corners, flat fill lighting, equally lit entire space, bright daylight, natural daylight, original white ceiling lighting preserved, original fluorescent even lighting, mirror glass, impossible reflections, floating reflections, fake reflections, random text, logo added, watermark, watermark from reference image, stock photo watermark, exhibition labels, fantasy elements, magical atmosphere, surreal lighting, impossible physics, holographic elements, copied geometry from Image 2, structural content from reference image, spatial layout from reference image, concert stage equipment added
```

---

### 조명 레이어 예시 — Mixed (Cool Blue + Warm Amber) / 컨퍼런스홀 기준

포토샵 합성용. 이 이미지를 원본 위에 올리고 **Screen** 또는 **Linear Dodge(Add)** 모드 적용.

```
LIGHT LAYER PROMPT
Pure solid black background. Complete darkness as the base. No room, no architecture, no surfaces, no objects, no floor, no ceiling, no walls — only pure black void. Match the exact aspect ratio and frame dimensions of Image 1 so this layer aligns perfectly for compositing. Multiple dramatic volumetric light beams radiating downward and crossing in a wide fan pattern from upper center positions, referencing the radiating beam composition of the reference image. Primary beams descend from the top-center area spreading outward in a symmetrical fan formation, with secondary crossing diagonal beams from upper-left and upper-right angles meeting near the center-lower zone. Subtle floating dust particles and atmospheric haze suspended within and around the light beams, creating depth and three-dimensional volumetric presence. Refined sparkling light particles and soft glinting highlights scattered within the illuminated beam zones, delicate and organic without overexposure or neon quality. Dominant cool blue and cold white primary beams from upper center, with warm amber and deep gold secondary accent beams from side angles. Blue-silver atmospheric glow surrounding the primary beam edges, warm golden glow around accent beams, creating layered mixed-temperature light atmosphere. Pure light art, photorealistic light physics, high dynamic range, deep pure black surrounding areas with no grey or noise, bright luminous beams with natural falloff and soft edge gradients. No room, no architecture, no objects, no text, no watermark, no people. Compositing-ready light layer on pure black background.

LIGHT LAYER NEGATIVE
room, architecture, walls, ceiling, floor, furniture, objects, people, faces, background elements, interior space, outdoor scene, any solid surface, grey background, white background, colored background, gradient background, noise in dark areas, grain in shadows, visible texture in black areas, text, watermark, logo, signage, labels, readable letters, neon lights, LED strips, lens flares, chromatic aberration, lens artifacts, overexposed blown areas, clipped highlights, flat even glow, studio light look, illustration, cartoon, painted look, digital art style, fantasy glow, magical sparkles, colored smoke, fog machine look, dry ice effect, unrealistic physics
```

---

## 익스트림 다크 모드 (Magnific img2img 전용)

### 개념

**공간 구조는 어두운 실루엣으로 유지**하되, 스포트라이트 빔만 극단적으로 지배적으로 만드는 모드.
순수 블랙이 아니라 — 테이블·의자·천장이 거의 보이지 않는 짙은 실루엣으로 남고, 빛줄기가 압도적인 주인공이 된다.
Magnific nanobanana img2img에 최적화된 프롬프트.

### EXTREME DARK PROMPT 작성 원칙

Image 1 (시네마틱 변환 결과물)을 Magnific에 올리고 아래 프롬프트를 입력한다.
Image 2 레퍼런스 없음. 단독 img2img 변환.

**출력 형식:**
```
EXTREME DARK PROMPT
[연속 영어 단락]

EXTREME DARK NEGATIVE
[연속 영어 단락]

MAGNIFIC SETTINGS
Creativity: [값]
Resemblance: [값]
```

### EXTREME DARK PROMPT 내용 (항상 이 구조로)

**① 극단적 어둠 선언**
> `"Extreme darkness transformation. Push all ambient light to near-black. Maximum contrast between deep shadow and spotlight beams."`

**② 공간 요소 실루엣화**
> `"All walls, ceiling, floor, stage platform crushed into near-black deep shadow. All furniture — tables, chairs — become barely visible dark silhouettes against black. All screens and panels fall into darkness. Only the faintest silhouette outlines remain, no surface detail, no color, no texture visible."`

**③ 빔 지배 선언**
> `"Only the crossing spotlight beams remain as the dominant light source. The volumetric beam rays are the sole illumination — intense, sharp, and high contrast against the surrounding blackness. Haze and atmospheric particles within the beam paths are visible and glowing."`

**④ 색온도 (앞서 분석한 모드 그대로 적용)**
- Cool Blue: `"Cool blue and cold white spotlight beams cutting through black darkness."`
- Warm Amber: `"Warm amber and gold spotlight beams cutting through black darkness."`
- Mixed: `"Dominant cool blue primary beams and warm amber accent beams cutting through black darkness."`

**⑤ 사진 리얼리즘**
> `"Photorealistic dramatic concert event lighting. Real photograph quality. Not CGI, not illustration."`

### EXTREME DARK NEGATIVE (항상 동일)

```
bright ambient lighting, evenly lit room, visible wall textures, visible ceiling detail, visible floor surface, colorful surfaces, bright backgrounds, cheerful lighting, daylight, studio lighting, flat lighting, fully visible furniture, fully visible architecture, neon effects, overexposed bloom, fake lens flares, illustration, cartoon, CGI render look, Unreal Engine look, text, watermark, logo
```

### Magnific 설정값 (항상 이 값)

```
Creativity: 0.75
Resemblance: 0.35
```

### 익스트림 다크 예시 — Cool Blue / 컨퍼런스홀

```
EXTREME DARK PROMPT
Extreme darkness transformation. Push all ambient light to near-black. Maximum contrast between deep shadow and spotlight beams. All walls, ceiling, floor, stage platform crushed into near-black deep shadow. All furniture — tables, chairs — become barely visible dark silhouettes against black. All screens and panels fall into darkness. Only the faintest silhouette outlines remain, no surface detail, no color, no texture visible. Only the crossing spotlight beams remain as the dominant light source. The volumetric beam rays are the sole illumination — intense, sharp, and high contrast against the surrounding blackness. Haze and atmospheric particles within the beam paths are visible and glowing. Cool blue and cold white spotlight beams cutting through black darkness. Photorealistic dramatic concert event lighting. Real photograph quality. Not CGI, not illustration.

EXTREME DARK NEGATIVE
bright ambient lighting, evenly lit room, visible wall textures, visible ceiling detail, visible floor surface, colorful surfaces, bright backgrounds, cheerful lighting, daylight, studio lighting, flat lighting, fully visible furniture, fully visible architecture, neon effects, overexposed bloom, fake lens flares, illustration, cartoon, CGI render look, Unreal Engine look, text, watermark, logo

MAGNIFIC SETTINGS
Creativity: 0.75
Resemblance: 0.35
```

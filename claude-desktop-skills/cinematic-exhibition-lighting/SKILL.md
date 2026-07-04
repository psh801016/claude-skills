---
name: cinematic-exhibition-lighting
description: "인테리어·건축·행사 공간 이미지(Image 1)에 레퍼런스 이미지(Image 2)의 시네마틱 전시 조명을 이식하는 전문 스킬. 구조·카메라·재료·가구·오브젝트는 Image 1 기준으로 4중 완전 잠금, 조명·색온도·분위기·볼류메트릭 효과만 Image 2에서 추출하여 적용한다. 이 스킬은 아래 상황에서 반드시 사용한다: - '조명 바꿔줘', '이 조명으로 바꿔줘', '레퍼런스 조명 적용해줘', '조명 이식' - '분위기 바꿔줘', '드라마틱하게', '시네마틱 조명', '전시 느낌으로' - '갤러리 분위기로', '뮤지엄 조명', '공연장 느낌', '행사장 조명' - 'CGI 렌더에 조명 입혀줘', '이미지에 이 조명 써줘' - 'lighting transfer', 'exhibition lighting', 'stage lighting apply' - 이미지 2장과 함께 조명·분위기 변환 요청이 들어오는 모든 경우 지원 공간: 거실·침실·주방·오피스·카페·호텔 로비·컨퍼런스홀·이벤트홀· 전시관·갤러리·공연장·행사장·의료공간·상업공간 — 모든 실내외 공간. 입력: Image 1 (원본 공간) + Image 2 (조명 레퍼런스, 선택) + 색온도 키워드 (선택) 출력 — 메인 변환: PROMPT + NEGATIVE 조명 레이어: LIGHT LAYER PROMPT + LIGHT LAYER NEGATIVE (txt2img, 포토샵 합성용) 조명 레이어 세트('레이어 세트', '조명 나눠서', '따로 컨트롤'): 빔/헤이즈/스팟 풀/컬러 워시 4분리 프롬프트 + 블렌드 가이드 익스트림 다크: EXTREME DARK PROMPT + MAGNIFIC SETTINGS(Magnific img2img 전용) + NEGATIVE(SD 대체 경로 전용 — Magnific/nanobanana에는 입력하지 않음) 둘 다 요청 시: 두 세트 순서대로 출력 사람을 별도 레이어로 합성하려면 person-layer-maker 사용(조명 레이어는 인물 위·아래로 나눠 쌓는다 — 공기 중 빔/헤이즈는 인물 위, 바닥·벽 스팟풀/컬러워시는 인물 아래) 건물 외관 실사화는 arch-prompt-maker, 조명 변환 없는 일반 실사화는 interior-prompt-maker 사용. 이 스킬은 레퍼런스 조명(Image 2)이나 '조명·분위기만' 바꾸는 요청 전용 — 단순 야간/황금시간대/날씨 전환은 외관이면 arch, 재료·가구·마감까지 바꾸는 스타일 리모델링은 interior 2장 모드가 담당한다."
---

# 시네마틱 전시 조명 마스터

인테리어·건축·행사 공간에 시네마틱 전시 조명을 이식한다.
구조는 4중 완전 잠금 — 오직 조명·분위기만 변환.

> **용어·엔진 정리:** 이 문서의 "nanobanana"는 **Magnific 업스케일러의 nanobanana 엔진 프리셋**을 뜻한다(원래 nano-banana는 Google Gemini 계열 이미지 모델의 별칭 — 공식명 Gemini Flash Image). MAGNIFIC SETTINGS(Creativity/Resemblance)는 Magnific UI 슬라이더 값이다. **NEGATIVE 처리는 엔진 계열로 갈린다** — Magnific·Gemini/nano-banana·GPT image 등 **의미기반 모델 경로에는 NEGATIVE를 넣지 않고**(부정 나열을 장면 묘사로 읽어 역효과), 부정문을 긍정형으로 흡수한다. NEGATIVE 블록은 **SD/ComfyUI 디퓨전 대체 경로 전용**이다. 본문에서 "GPT image 경로"라 적힌 규칙은 Gemini/nano-banana 등 다른 의미기반 모델에도 동일하게 적용된다.

## ★ 구도 보존 최우선 원칙 (실패 1순위 방지)

이 스킬은 카메라·기하학을 4중 잠금하지만, i2i 엔진 자체가 구도(화각·종횡비)를 틀 수 있다. 근본 원인은 **종횡비 불일치**다.

1. **★ 실행 전 원본을 대상 엔진이 지원하는 비율로 사전 크롭** — 엔진의 출력 비율 제약을 먼저 확인한다: **gpt-image-1 계열은 1:1 / 3:2 / 2:3 고정**이므로 원본을 미리 그 비율로 크롭해 넣고, **임의 해상도를 지원하는 엔진/모델(사용 전 사양 확인)**이면 원본 비율을 그대로 유지한다(불필요한 크롭 금지). 크롭으로 잘리는 면적이 15%를 넘으면 사용자에게 경고 후 진행하고(비율 맞춤 크롭에만 적용), 크롭은 목표 비율·방향을 1~2줄로 안내하거나 이미지 파일 접근이 가능하면 직접 크롭 후 진행한다. 모델이 엣지에서 공간을 발명할 여지를 없애는 유일한 구조적 해결책이다.
2. **절대 초점거리 숫자 금지** — PROMPT에 mm 숫자를 쓰지 않는다(이 스킬은 이미 미사용). "원본과 동일한 화각" 긍정형만 쓴다.
3. **GPT image 경로에서는 NEGATIVE를 넣지 않고, 본문·예시의 모든 부정문을 긍정형으로 바꾼다 (2·3·6·9·10단계 포함)** — 의미기반 모델은 부정 단락을 장면 묘사로 읽어 억제어를 오히려 그린다. 카메라/기하학 잠금의 부정문(`No camera change`, `no reframing` 등)은 긍정형(`preserve the exact same camera position, framing, field of view, and aspect ratio as Image 1, with every element occupying the same fraction of the frame, all four frame edges aligning with Image 1, and the vanishing points in the same screen positions`)으로, 6단계의 `No fantasy or illustration style`·9단계의 `not a CGI render`·10단계의 부정문 나열은 긍정형 대체문(`"a professionally photographed real-world cinematic event space, with the material fidelity and lighting physics of documentary stage photography, every material, structure, furniture piece, and screen exactly as in Image 1"`)으로 바꿔 쓴다. PROMPT만 사용하고, 부정문 잠금·NEGATIVE는 SD/MJ/ComfyUI 디퓨전 경로 전용. (긍정형 변환 대상은 **이미지 생성 PROMPT 텍스트 안의 부정 표현뿐** — 이 스킬 문서의 절차·규칙 문장은 변환 대상이 아니다.)
4. **엔진 선택·검증** — 구도 보존 최우선이면 ControlNet 기반 SD i2i 또는 Magnific 업스케일러(0~1 스케일 기준 Creativity 0.1~0.3 낮게 / Resemblance 0.85~1.0 높게 — 익스트림 다크 모드의 0.75/0.35와 스케일 동일, 용도만 다름)를 쓰고, 결과 위에 원본 50% 오버레이로 소실점·모서리 일치를 확인한다.

## 출력 모드

| 모드 | 트리거 | 출력 |
|---|---|---|
| **메인 변환** | 기본 (조명 변환 요청) | PROMPT + NEGATIVE |
| **조명 레이어** | "레이어만", "빛만 레이어", "빛만 뽑아", "포토샵 합성용", "블랙 배경 조명", "조명 레이어" | LIGHT LAYER PROMPT + LIGHT LAYER NEGATIVE |
| **조명 레이어 세트** ★ | "레이어 세트", "조명 나눠서", "레이어 분리", "따로따로 컨트롤" | 4분리 레이어 프롬프트 (빔/헤이즈/스팟 풀/컬러 워시) + 블렌드 가이드 |
| **익스트림 다크** | "극단적으로 어둡게", "실루엣만", "빛만 살려", "빛만 눌러", "나머지 다 블랙", "어둡게 눌러", "다크 실루엣", "Magnific 다크" | EXTREME DARK PROMPT + NEGATIVE(SD 대체 경로 전용) + MAGNIFIC SETTINGS |
> 트리거 우선순위: "빛만 살려/눌러" 계열은 **익스트림 다크** 우선, "빛만 레이어/뽑아"는 **조명 레이어**로 판정한다.
| **둘 다** | "둘 다", "레이어도", "합성도 같이" | 두 세트 모두 출력 |

## 빠른 흐름

1. **출력 모드 판단** (위 표 참조)
2. **입력 확인**: Image 1 (원본) + Image 2 (조명 레퍼런스, 선택) + 색온도 키워드 (선택) — **메인 변환·익스트림 다크에서 Image 1이 없으면 프롬프트를 지어내지 말고 원본 이미지를 요청한다** (조명 레이어 모드만 이미지 없이 가능)
2-1. **(구도 보존 중요 시) 사전 크롭 안내**: 대상 엔진 비율 확인 후 크롭 안내 또는 직접 크롭 — 위 "구도 보존 최우선 원칙" 1
3. **Image 2 조명 분석** (아래 "조명 추출 가이드" 참조) — **Image 2가 없으면** 조명 분석을 생략하고 색온도 판단표의 기본값(Neutral Cinematic)으로 진행하며, 1단계·6단계 문장에서 Image 2 참조를 제거한 대체 문장을 쓴다(아래 각 단계 참조)
4. **색온도 판단** (아래 색온도 판단표 참조)
5. **메인 변환** → 4중 잠금 + PROMPT + NEGATIVE
6. **조명 레이어** → LIGHT LAYER PROMPT + LIGHT LAYER NEGATIVE
7. **익스트림 다크** → EXTREME DARK PROMPT + NEGATIVE + Magnific 설정값

> 5~7은 순차 실행이 아니다 — 1단계에서 판정된 모드에 해당하는 것만 실행한다("둘 다"면 해당 세트 모두 순서대로).

카메라 브랜드(Sony, Canon, Hasselblad 등) 절대 명시하지 않는다.
MJ 파라미터(`--v`, `--iw`, `--ar` 등) 절대 포함하지 않는다.

## 출력 원칙

설명·분석·주석·이미지 생성 없음. 프롬프트 섹션만 출력.
단, 예외 2가지: (a) 사전 크롭이 필요한 경우 크롭 안내(목표 비율·방향) 1~2줄 허용, (b) 필수 입력(Image 1)이 없으면 프롬프트를 지어내지 말고 이미지를 요청.
모든 PROMPT·LIGHT LAYER PROMPT는 **하나의 연속된 영어 단락**.

**메인 변환 출력 형식 (GPT image 경로에서는 NEGATIVE 섹션 생략 — PROMPT만):**
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

**Image 2 없는 경우 대체 문장 (존재하지 않는 이미지를 참조하지 않는다):**
> `"Use Image 1 as the immutable architectural structure, room geometry, camera position, composition, original materials, surface finishes, furniture layout, and all spatial elements. Transform only the lighting, color temperature, and atmospheric mood."`

---

### 2. 카메라 잠금

> **★ GPT image 경로에서는 이 카메라 잠금과 아래 "3. 방 기하학 잠금"의 부정문(`No camera change`, `no reframing`, `Do not move...` 등)을 모두 긍정형으로 바꾼다 — 위 "구도 보존 최우선 원칙" 3 참조. 부정문 LOCK은 SD/MJ/ComfyUI 디퓨전 경로 전용.**

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
> `"Preserve the LED screen and display panel structures, frame positions, placement, and scale. The existing screen content may receive only brightness and color-temperature grading to match the new lighting mood — keep the same imagery, no semantic replacement of screen content."`

**색 보존과 조명 색온도의 관계 (문자 충돌 방지):** 색온도 조명은 표면의 '보이는 색'을 바꾼다. 잠금의 의미는 **재료의 고유 색(intrinsic base color)** 보존이며, 조명에 의한 지각 색 변화는 허용이다. 필요 시 PROMPT에 `"preserve the intrinsic material base colors; only the perceived illumination color may shift due to the new lighting"`을 덧붙인다.

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

**Image 2 없는 경우:** `referencing the [빔 패턴 묘사] lighting composition of Image 2` 부분을 빼고, 조명 레이어 섹션의 기본값처럼 빔을 직접 묘사한다 — `"using three to five vertical downlight beams from the ceiling center and soft crossing secondary beams from the sides"`. (GPT 경로에서는 마지막 문장 `No fantasy...`를 긍정형 `cinematic professional event hall mood, grounded in real stage-lighting physics`로 바꾼다.)

빔 패턴 묘사 예시:
- 방사형: `"fan-radiating beam pattern from overhead ceiling truss"`
- 교차형: `"crossing diagonal beam spotlights from left and right ceiling positions"`
- 수직 집중: `"tight vertical spotlights from ceiling grid focused on stage area"`
- 사이드 플러드: `"side-wash beams from left and right wall positions"`

**무대 조명 효과 어휘 (Image 2 분석·요청에 맞춰 선택 — 겹치는 발광 토큰 최소화):**
- 빔/워시/스팟 구분: `sharp defined beam` (빔) / `broad soft color wash across the wall` (워시) / `focused light pool on the floor or subject` (스팟)
- 백라이트·림: `strong backlight from behind the stage creating rim highlights on subject edges`
- LED 월 글로우: `soft screen-glow spill from the LED wall onto nearby floor and subjects` (스크린 콘텐츠 자체는 잠금 유지)
- 고보 패턴(레퍼런스에 있을 때만): `patterned gobo light texture projected on the floor`
- 객석 스필: `dim warm light spill over the audience area, far dimmer than the stage`
- 헤이즈 농도 3단계: `light haze` (빔 윤곽만) / `medium haze` (기본) / `heavy haze` (공기 자체가 발광, 대비 저하 감수)
- 무빙헤드 등 조명 기구 자체는 원본(Image 1)에 있을 때만 유지 — 새 기구를 만들어 넣지 않는다 (physically mounted fixtures 원칙)

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
프롬프트에 "the reference image" 같은 참조 문구를 넣지 않는다(txt2img에는 레퍼런스가 첨부되지 않음 — 유령 참조 금지). 빔 형태를 직접 묘사한다.

**GPT image 경로 분기:** LIGHT LAYER NEGATIVE를 생략하고, 블록 ①·⑥의 부정문(`No room, no architecture...`)을 긍정형으로 바꾼다 —
- ① 대체: `"The entire frame is a pure black void in which volumetric light beams are the only visible content."`
- ⑥ 대체: `"Pure light art on a pure black background, photorealistic light physics, high dynamic range, deep pure black surroundings, bright luminous beams with natural falloff and soft edge gradients — a compositing-ready light layer."`

---

## 조명 레이어 세트 (LAYER SET — 포토샵 개별 컨트롤용 4분리) ★

### 개념
조명 레이어 1장은 빔·헤이즈·스팟·워시가 한 덩어리라 "빔만 줄이고 헤이즈만 키우기"가 불가능하다. **레이어 세트 모드는 조명을 4개 성분으로 분리 생성**해 포토샵에서 각각 불투명도·색조·마스크로 따로 컨트롤한다 — 한 번에 나온 결과를 수정 못 해 버리는 일을 없앤다.

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

## 예시

> **※ 아래 메인 변환 예시들은 SD/디퓨전 경로용(부정문 카메라 잠금·NEGATIVE 포함). GPT image 경로에서는 NEGATIVE를 빼고 PROMPT만 쓰며, 본문의 부정문 카메라/기하학 잠금(`No camera change`, `no reframing` 등)을 긍정형으로 바꾼다 — 위 "구도 보존 최우선 원칙" 3 참조.**

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
생성 시 **사이즈/종횡비 파라미터를 Image 1과 동일하게 설정**한다 (프롬프트가 아니라 생성 설정에서).

```
LIGHT LAYER PROMPT
Pure solid black background. Complete darkness as the base. No room, no architecture, no surfaces, no objects, no floor, no ceiling, no walls — only pure black void. Multiple dramatic volumetric light beams radiating downward and crossing in a wide symmetrical fan pattern from upper center positions. Primary beams descend from the top-center area spreading outward in a symmetrical fan formation, with secondary crossing diagonal beams from upper-left and upper-right angles meeting near the center-lower zone. Subtle floating dust particles and atmospheric haze suspended within and around the light beams, creating depth and three-dimensional volumetric presence. Refined sparkling light particles and soft glinting highlights scattered within the illuminated beam zones, delicate and organic without overexposure or neon quality. Dominant cool blue and cold white primary beams from upper center, with warm amber and deep gold secondary accent beams from side angles. Blue-silver atmospheric glow surrounding the primary beam edges, warm golden glow around accent beams, creating layered mixed-temperature light atmosphere. Pure light art, photorealistic light physics, high dynamic range, deep pure black surrounding areas with no grey or noise, bright luminous beams with natural falloff and soft edge gradients. No room, no architecture, no objects, no text, no watermark, no people. Compositing-ready light layer on pure black background.

LIGHT LAYER NEGATIVE
room, architecture, walls, ceiling, floor, furniture, objects, people, faces, background elements, interior space, outdoor scene, any solid surface, grey background, white background, colored background, gradient background, noise in dark areas, grain in shadows, visible texture in black areas, text, watermark, logo, signage, labels, readable letters, neon lights, LED strips, lens flares, chromatic aberration, lens artifacts, overexposed blown areas, clipped highlights, flat even glow, studio light look, illustration, cartoon, painted look, digital art style, fantasy glow, magical sparkles, colored smoke, fog machine look, dry ice effect, unrealistic physics
```

---

## 익스트림 다크 모드 (Magnific img2img 전용)

### 개념

**공간 구조는 어두운 실루엣으로 유지**하되, 스포트라이트 빔만 극단적으로 지배적으로 만드는 모드.
순수 블랙이 아니라 — 테이블·의자·천장이 거의 보이지 않는 짙은 실루엣으로 남고, 빛줄기가 압도적인 주인공이 된다.
Magnific nanobanana img2img에 최적화된 프롬프트.

> **★ 이 모드는 '4중 잠금' 모드가 아니다 — 무드 강화 후처리 모드다.** 높은 Creativity(0.75)/낮은 Resemblance(0.35)는 **구도·배치 수준만 대략 유지**하고 표면 디테일·색감·텍스처를 대폭 변형한다. 픽셀 수준 구조 보존이 필요한 결과물에는 쓰지 않는다. 사용자에게 "원본 색감·디테일이 크게 변합니다" 경고를 한 줄 덧붙인다.

### EXTREME DARK PROMPT 작성 원칙

Image 1 (시네마틱 변환 결과물)을 Magnific에 올리고 아래 프롬프트를 입력한다.
Image 2 레퍼런스 없음. 단독 img2img 변환.

**출력 형식 (항상 이 구성 — Magnific/nanobanana에 입력하는 것은 PROMPT와 SETTINGS 뿐):**
```
EXTREME DARK PROMPT
[연속 영어 단락]

EXTREME DARK NEGATIVE (SD 계열 대체 경로 전용 — Magnific/nanobanana에는 입력하지 않음)
[연속 영어 단락]

MAGNIFIC SETTINGS
Creativity: [값]
Resemblance: [값]
Detail: [값]
HDR: [값]
```

### EXTREME DARK PROMPT 내용 (항상 이 구조로)

**① 극단적 어둠 선언**
> `"Extreme darkness transformation. Push all ambient light to near-black. Maximum contrast between deep shadow and spotlight beams."`

**② 공간 요소 실루엣화**
> `"All walls, ceiling, floor, stage platform crushed into near-black deep shadow. All furniture — tables, chairs — become barely visible dark silhouettes against black. All screens and panels fall into darkness. Only the faintest silhouette outlines remain, no surface detail, no color, no texture visible."`

**③ 빔 지배 선언**
> `"Only the crossing spotlight beams remain as the dominant light source. The volumetric beam rays are the sole illumination — intense, sharp, and high contrast against the surrounding blackness. Haze and atmospheric particles within the beam paths are visible and glowing."`

**④ 색온도 (앞서 분석한 모드 그대로 적용)**
- Neutral Cinematic (기본값 — 색온도 키워드·Image 2 없을 때): `"Neutral cool-white spotlight beams with subtle silver undertones cutting through black darkness."`
- Cool Blue: `"Cool blue and cold white spotlight beams cutting through black darkness."`
- Warm Amber: `"Warm amber and gold spotlight beams cutting through black darkness."`
- Mixed: `"Dominant cool blue primary beams and warm amber accent beams cutting through black darkness."`

**⑤ 사진 리얼리즘**
> `"Photorealistic dramatic concert event lighting. Real photograph quality. Not CGI, not illustration."`

### EXTREME DARK NEGATIVE (SD 계열 img2img 대체 경로 전용)

> **주의:** Magnific 업스케일러와 nanobanana(Gemini 계열 의미기반 모델)에는 별도 NEGATIVE 입력 필드가 없고, 의미기반 모델에 부정 나열을 이어붙이면 억제어를 오히려 그린다(구도 보존 원칙 3과 동일 논리). **Magnific/nanobanana 경로에서는 이 NEGATIVE를 생략**하고 ②의 긍정형 어둠 묘사(`crushed into near-black deep shadow` 등)로 흡수한다. 아래 블록은 SD 계열 img2img로 대체 실행할 때만 NEGATIVE 필드에 넣는다.

```
bright ambient lighting, evenly lit room, visible wall textures, visible ceiling detail, visible floor surface, colorful surfaces, bright backgrounds, cheerful lighting, daylight, studio lighting, flat lighting, fully visible furniture, fully visible architecture, neon effects, overexposed bloom, fake lens flares, illustration, cartoon, CGI render look, Unreal Engine look, text, watermark, logo
```

### Magnific 설정값 (항상 이 값 — 0~1 스케일)

```
Creativity: 0.75
Resemblance: 0.35
Detail: 0.4
HDR: 0.1
```
(구도 보존용 기본값 0.1~0.3 / 0.85~1.0과 정반대인 것은 의도 — 이 모드는 변형 허용 모드다. 위 개념의 경고 참조.)
**Detail/HDR:** 다크 플레이트는 **HDR 낮게(~0.1)** — HDR을 올리면 눌러둔 암부가 다시 살아나 실루엣이 풀린다. Detail은 빔·헤이즈 입자감 확보용 **0.4 전후**, 노이즈가 과하면 0.3으로 낮춘다.

### 익스트림 다크 예시 — Cool Blue / 컨퍼런스홀

```
EXTREME DARK PROMPT
Extreme darkness transformation. Push all ambient light to near-black. Maximum contrast between deep shadow and spotlight beams. All walls, ceiling, floor, stage platform crushed into near-black deep shadow. All furniture — tables, chairs — become barely visible dark silhouettes against black. All screens and panels fall into darkness. Only the faintest silhouette outlines remain, no surface detail, no color, no texture visible. Only the crossing spotlight beams remain as the dominant light source. The volumetric beam rays are the sole illumination — intense, sharp, and high contrast against the surrounding blackness. Haze and atmospheric particles within the beam paths are visible and glowing. Cool blue and cold white spotlight beams cutting through black darkness. Photorealistic dramatic concert event lighting. Real photograph quality. Not CGI, not illustration.

EXTREME DARK NEGATIVE (SD 계열 대체 경로 전용 — Magnific/nanobanana에는 입력하지 않음)
bright ambient lighting, evenly lit room, visible wall textures, visible ceiling detail, visible floor surface, colorful surfaces, bright backgrounds, cheerful lighting, daylight, studio lighting, flat lighting, fully visible furniture, fully visible architecture, neon effects, overexposed bloom, fake lens flares, illustration, cartoon, CGI render look, Unreal Engine look, text, watermark, logo

MAGNIFIC SETTINGS
Creativity: 0.75
Resemblance: 0.35
Detail: 0.4
HDR: 0.1
```

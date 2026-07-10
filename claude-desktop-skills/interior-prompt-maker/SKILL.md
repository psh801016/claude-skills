---
name: interior-prompt-maker
description: "인테리어 · 실내 공간 CGI · 렌더 이미지를 Stable Diffusion / Midjourney / ComfyUI image-to-image용 사실적 실내 사진 프롬프트로 변환하는 전문 스킬. 이미지 1장(원본 실사화)과 2장(구조 보존 + 스타일 리모델링) 두 가지 모드를 자동 판단한다. 사용자가 실내 이미지와 함께 '프롬프트 만들어줘', '실사화해줘', '리모델링 프롬프트 써줘', 'i2i 프롬프트 뽑아줘', 'SD/MJ 프롬프트', '사진처럼 만들어줘', 'CGI 느낌 없애줘', '인테리어 프롬프트' 같은 말을 하면 반드시 이 스킬을 사용한다. 입력 유형: SketchUp · Rhino · Revit · Lumion · Enscape · D5 실내 렌더, 화이트 모델, 클레이 모델 — 모든 실내 CGI. 지원 공간: 거실 · 주방 · 침실 · 욕실 · 오피스 · 카페 · 레스토랑 · 호텔 로비 · 병원 · 교육 공간 · 공공 서비스홀. 건물 외관 프롬프트는 arch-prompt-maker, 재질·텍스처 추출은 texture-prompt-maker, 포토샵 합성용 업스케일 전처리는 magnific-compositing-prep, 구조·재료는 그대로 두고 조명·분위기만 이식할 때는 cinematic-exhibition-lighting을 사용한다. 주 피사체 기준: 파사드·매스·외부 공간이 화면 주체면 arch, 실내 공간(전시부스 실내 포함)이 주체면 이 스킬 — 둘 다 크게 보이면 사용자에게 확인. 사람을 별도 레이어로 합성해 넣는 요청은 person-layer-maker가 담당한다(원본 렌더에 이미 있는 인물의 실사 변환은 이 스킬 8단계). 이미지가 없으면 원본 이미지 첨부와 실내/외 여부를 먼저 확인한다."
---

# 인테리어 Image-to-Image 프롬프트 메이커

인테리어 CGI/렌더/모델 이미지를 실제 건축 인테리어 사진과 구분 불가능한 수준의 프롬프트로 변환한다.

## 핵심 원칙

**임무 = CGI 표면 퀄리티 → 사진 퀄리티 변환. 색상·재료·공간 재설계가 아니다.**

## ★ 구도 보존 최우선 원칙 (실패 1순위 방지)

i2i 변환의 가장 흔한 실패 = **구도(화각·줌·시점·종횡비) 틀어짐**. 근본 원인은 문구가 아니라 **종횡비 불일치**다 — 16:9 원본을 모델이 다른 비율로 강제하면, 모자란 부분을 "프레임 밖 공간을 발명"해 채우며 줌아웃·측벽 추가가 생긴다. 따라서 문구보다 1·2가 먼저다.

1. **★ 실행 전 원본을 출력 합법 비율로 사전 크롭 (진짜 해결책)** — 모델이 엣지에서 방을 발명할 여지를 구조적으로 없앤다. 엔진의 출력 비율 제약을 먼저 확인한다: **gpt-image-1 계열은 1:1 / 3:2 / 2:3 고정**이므로 원본 16:9를 미리 3:2(가로형)로 크롭해 넣고, **gpt-image-2는 제약 내 임의 해상도를 지원**하므로 원본 비율을 그대로 유지한다(불필요한 크롭 금지). 크롭으로 잘리는 면적이 15%를 넘으면 중요 요소 절단 위험을 사용자에게 경고 후 진행한다(이 경고는 출력 비율 맞춤 크롭에만 적용 — 영역 추출 목적의 의도적 크롭은 대상 아님). "넓히지 마"(강제 불가)를 "넓힐 여지 없음"(구조 보장)으로 바꾸는 유일한 단계다.
2. **종횡비 원본 일치** — 사전 크롭한 비율과 출력 비율을 동일하게 둔다.
3. **절대 초점거리 숫자 금지** — 프롬프트에 `24mm`·`35mm` 등 숫자 초점거리를 절대 쓰지 않는다. 모델이 원본 화각을 무시하고 그 렌즈로 재해석해 광각화·줌아웃을 일으킨다. 오직 "원본과 동일한 화각·시점·프레이밍" **긍정형** 상대 표현만 쓴다.
4. **부정문("do not widen / zoom out") 금지** — 의미기반 모델에선 "분홍 코끼리" 효과로 오히려 그 변형을 유발한다. 항상 "원본과 동일하게 / 프레임 점유율 동일 / 네 모서리 정렬 / 소실점 동일 위치" 같은 **긍정 대응**으로 쓴다.
5. **GPT image 경로에서는 NEGATIVE를 넣지 않는다** — gpt-image는 부정 단락을 장면 묘사로 읽어 억제어를 오히려 그린다. PROMPT(긍정형)만 사용한다. NEGATIVE는 SD/MJ/ComfyUI 디퓨전 경로에서만 쓴다.
6. **엔진 선택 규칙** — 구도 픽셀 보존이 최우선이면 **GPT 엔진을 쓰지 않는다.** ControlNet(depth+lineart) 기반 SD i2i, 또는 Magnific 업스케일러(**0~1 스케일 기준 Creativity 0.1~0.3 낮게 / Resemblance 0.85~1.0 높게** 에서 시작, 이미지별 튜닝)를 쓴다. **FLUX 파이프라인이면 FLUX-native 컨트롤 모델(FLUX.1 Depth-dev 또는 Canny-dev 중 택일, 동시 사용은 ComfyUI 스태킹으로 별도 검증)** 을 쓴다 — SD/SDXL 계열 ControlNet·LoRA는 구조가 달라 **로드 자체가 불가**하니 FLUX 전용으로 교체. 주의: dev 계열은 비상업 라이선스(상업 프로젝트는 라이선스 확인), BFL API 신규 통합에서는 deprecated 표시(로컬 ComfyUI open-weight 경로는 사용 가능, 2026-07 기준).
7. **검증** — 결과 위에 원본을 50% 투명도로 겹쳐 수평선·소실점·네 모서리가 일치하는지 확인하고, 어긋나면 크롭으로 정렬한다.

## 빠른 흐름

0. **(구도 보존 중요 시) 사전 크롭**: 실행 전 원본을 출력 엔진의 합법 비율로 사전 크롭한다(위 원칙 1). 사용자에게 목표 비율·크롭 방향을 1~2줄로 안내하거나, 이미지 파일 접근이 가능하면 직접 크롭 후 진행한다.
1. **대상 엔진 판별**: 사용자가 명시하지 않으면 SD/MJ/ComfyUI 디퓨전 기본. GPT image 경로면 NEGATIVE 없이 긍정형 PROMPT만(원칙 5).
2. **모드 판단**: 이미지 1장 → 단일 모드 / 이미지 2장 → 리모델링 모드 (아래 "모드 판단"의 엣지케이스 규칙 참조)
3. **이미지 분석**: 공간 유형, 색상 팔레트, 주요 건축 요소 파악
4. **9단계 PROMPT + NEGATIVE** 작성
5. **PROMPT + NEGATIVE 두 섹션을 항상 함께** 출력 — NEGATIVE 제목에는 사용처 라벨(출력 원칙 참조). GPT image 경로에서는 NEGATIVE를 출력은 하되 입력에 사용하지 않는다(원칙 5)

카메라 브랜드 (Sony, Canon, Hasselblad 등) 절대 명시하지 않는다.
MJ 파라미터 (`--v`, `--iw`, `--ar` 등) 절대 포함하지 않는다.

## 출력 원칙

- **PROMPT와 NEGATIVE 두 섹션을 항상 함께** 출력(조건부 생략 금지). NEGATIVE 제목에는 사용처 라벨을 붙인다: `NEGATIVE (SD/MJ/ComfyUI 전용 — GPT image·Magnific/nanobanana에는 입력하지 않음)`. GPT image 경로에서는 이 섹션을 **출력은 하되 입력에 사용하지 않는다** — 부정 억제는 9단계 GPT 긍정형 대체 문장이 대신한다
- 설명, 분석, 주석 없음 — 단, 사전 크롭이 필요한 경우 PROMPT 출력 전에 크롭 안내(목표 비율·방향) 1~2줄은 허용
- PROMPT는 **하나의 연속된 영어 단락**
- NEGATIVE는 **하나의 연속된 영어 단락**

---

## 모드 판단

**이미지 1장 → 단일 모드:** 원본 공간을 실사 사진으로 변환
**이미지 2장 → 리모델링 모드:** 이미지1 구조·색상 유지 + 이미지2 스타일만 적용
**이미지 2장 + 부분 지정("소파만", "이 벽만", "콕 집어", "빨간 영역만") → 정밀 재료 교체(PICK) 모드** (아래 블록)

**엣지케이스:**
- 이미지 0장 → 원본 이미지 첨부를 요청한다 (텍스트만으로 지어내지 않는다)
- 이미지 2장이 같은 공간의 다른 앵글이라 리모델링 의도가 불명확하면 → 각각 단일 모드로 처리할지 사용자에게 확인 (다중 앵글 일괄 실사화 케이스 빈발)
- 이미지 3장 이상 → 어느 것이 구조 원본(Image 1)이고 어느 것이 스타일 레퍼런스인지 확인 후 진행 ("Image 1 = 구조 고정" 가정은 PROMPT 첫 문장의 역할 선언으로 표현된다 — 별도 설명 출력 금지)

---

## 정밀 재료 교체(PICK) 모드 — 부분만 콕 집어 교체 (2026-07-06 신규)

리모델링 모드가 "공간 전체 스타일"을 바꾼다면, 이 모드는 **지정된 부분의 표면 재료만** 바꾼다. 행위/기준/전이 3행 규격:

- **행위:** 표면 재료만 바꾼다 (형태 재설계 금지)
- **기준(보존):** 형상 · 구도 · 객체 경계 · 카메라 — 대상의 실루엣과 나머지 공간 전부
- **전이:** 질감 · 색 · 거칠기 · 반사도 — Image 2(레퍼런스)의 재료 속성만

**프롬프트 구성:**
1. 첫 문장 역할 선언: "Image 1 = BASE(보존), Image 2 = 재료 소스(REFERENCE)"
2. 대상 지정: 자연어("the fabric sofa", "the upper wall band around the skylight") 또는 **빨간 마스크 규약** — Image 1의 빨간 하이라이트 영역 = 변경 대상. **⚠ 소스(Image 2) 쪽은 빨간 채움 금지** — 모델이 읽을 소스 색·질감이 오염된다. 소스 패치는 **크롭해 깨끗한 이미지로 전달**하고, 표시가 불가피하면 채움 없는 윤곽선만 사용
3. 교체 문장: "Replace ONLY the surface material of [대상] with the material of the REFERENCE — transfer its texture, color, roughness and reflectance. Keep the shape, boundaries, composition and camera exactly unchanged."
4. 마스크를 썼다면 제거 지시 필수: "Remove every red annotation line, hatch or highlight from the final output."
5. 물리 정합 앵커로 마무리: "physically correct scale, contact shadows and lighting on the new material."

**주의:** ① 구도 보존 최우선 원칙(위 ★ 블록) 그대로 적용 ② GPT 경로 = NEGATIVE 없이 긍정형 잠금(기존 규칙) ③ 새 재료의 반사도가 조명과 충돌하면(광택 재료 ← 무광 장면) 조명 방향을 명시해 하이라이트 위치를 고정한다.

**엣지케이스:**
- 이미지 0장 → 원본 이미지 첨부를 요청한다 (텍스트만으로 지어내지 않는다)
- 이미지 2장이 같은 공간의 다른 앵글이라 리모델링 의도가 불명확하면 → 각각 단일 모드로 처리할지 사용자에게 확인 (다중 앵글 일괄 실사화 케이스 빈발)
- 이미지 3장 이상 → 어느 것이 구조 원본(Image 1)이고 어느 것이 스타일 레퍼런스인지 확인 후 진행 ("Image 1 = 구조 고정" 가정은 PROMPT 첫 문장의 역할 선언으로 표현된다 — 별도 설명 출력 금지)

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

**색상 적용 기준(리모델링 모드):** 구조·고정 요소(벽 골조, 천장 형태, 창호 프레임 등 Image 1의 건축 구조)의 색은 **Image 1을 보존**하고, 마감재·가구·스타일 요소의 색상은 **Image 2를 적용**한다. 아래 "컬러 팔레트 잠금"의 원본 색 보존 규칙은 **단일 모드에서는 이미지 전체에**, **리모델링 모드에서는 구조·고정 요소에만** 적용된다.

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

먼저 선언 (단일 모드):
> `"Preserve exactly the original design color palette without any change, reinterpretation, or color shift. The task is to convert CGI surface quality to photographic realism only — do NOT redesign, recolor, or replace any material or color."`

**리모델링 모드 전용 잠금 문구 (위 문장 대신 사용 — 무스코프 잠금과 Image 2 재료 지정이 충돌하지 않도록):**
> `"Preserve exactly the architectural structure and fixed-element colors from Image 1, while applying the material and furniture palette of Image 2. The task is to convert CGI surface quality to photographic realism — do NOT alter Image 1's architecture and do NOT invent elements absent from both images."`

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

**카메라 선언 (마지막에 위치) — ★ 절대 초점거리(24mm/35mm 등)를 숫자로 박지 않는다. 부정문("do not …") 대신 원본 화각을 그대로 따르는 긍정형으로 쓴다:**
> `"Captured with the exact same camera position, camera height, focal length, field of view, angle of view, and aspect ratio as the source image, so that every wall and ceiling element occupies the same fraction of the frame as in the original, all four frame edges align with the same points of the original scene, and the vanishing points land in the same screen positions. Match the original framing one-to-one, as a professional full-frame architectural interior photograph indistinguishable from a real built environment."`

**왜 이렇게:** ① `24mm`·`35mm` 등 절대 초점거리를 쓰면 모델이 원본 화각을 무시하고 그 렌즈로 재해석 → 광각화·줌아웃. ② `do not widen / do not zoom out` 같은 부정문은 의미기반 모델(GPT image 등)에서 "분홍 코끼리" 효과로 오히려 그 변형을 유발한다. 그래서 위처럼 "프레임 점유율 동일·네 모서리 정렬·소실점 동일 위치" 긍정 대응 표현만 쓴다.

**anti-CGI 강화 (SD/MJ/ComfyUI 디퓨전 경로 전용):**
> `"No render look, no archviz appearance, no plastic materials, no fake reflections, no Unreal Engine look, no SketchUp appearance, no clay-render feeling, no synthetic atmosphere, no artificial-looking lighting. Completely believable real-world interior photograph."`

(※ `artificial lighting`이 아니라 `artificial-looking lighting` — 7단계의 인공조명(다운라이트·LED) 처방과 충돌 방지)

**GPT image 경로 긍정형 대체 (부정문 블록 대신 PROMPT 말미에 사용):**
> `"Rendered with the material fidelity, lighting behavior, and natural color science of documentary architectural interior photography — a completely believable real-world interior photograph."`

---

## NEGATIVE 작성 (14카테고리, 순서 엄수)

**토큰 판정 규칙(전 카테고리 공통):** 토큰이 **억제하려는 결함·실패 상태**를 부르면 유지(예: `warped walls`, `bad anatomy` — SD 부정 임베딩의 정상 메커니즘), **원하는 결과 장면·구도**를 이름으로 부르면 금지(예: `zoomed-in composition`, `wider angle of view` — 의미기반 모델에서 그 장면을 그리게 만든다). 판별이 애매하면 '변형 행위 명명형'(`changed/altered X`)으로 쓴다. (카테고리 3 주의문·13 전시부스 주의문은 이 규칙의 카테고리별 강화판이다.)

> 최종 출력 전 NEGATIVE에서 **중복 토큰을 제거**한다 — 같은 토큰이 두 카테고리에 있으면 한 번만 남긴다 (CLIP 청크 토큰 예산 희석 방지).

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

---

## 공간 유형별 접근

> **★ 아래 각 항목의 "카메라: 24–35mm" 등 mm 숫자는 촬영 화각 감각을 잡기 위한 참조용일 뿐이다. PROMPT에는 절대 mm 숫자를 쓰지 않는다 — "원본과 동일한 화각" 긍정형 표현만 사용한다 (위 "구도 보존 최우선 원칙" 참조).**

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

### 전시부스 / 전시장 (3종: 목공 · 블럭 · 옥타놈 + 전시홀) ★

> **왜 별도 블록인가:** 전시부스는 규칙적인 알루미늄 직선 격자(포스트·빔·fascia)로 이뤄져 AI가 가장 잘 무너뜨리는 대상이다. 프레임을 "녹이거나" 벽을 매끈한 단일면으로 뭉개고, 간판 글자를 깨뜨린다. 아래 어휘·성공문장·엔진 규칙으로 이를 막는다. (검수 반영: NEGATIVE 증상토큰 배제·mm 숫자 배제·fascia 텍스트 생성 금지)

**★★ 먼저 3종 중 무엇인지 판별 (한국 전시업계 실무 기준 — 셋은 외형이 다르다. 섞지 않는다):**
| 유형 | 골조·시공 | 외형 식별자 |
|---|---|---|
| **목공부스** (독립/맞춤) | 각재+합판+퍼티+도장/시트 | **이음매 없는 매끈한 벽면(seamless), 날카롭고 깔끔한 모서리, 프레임 안 보임** |
| **블럭부스** (렌탈 모듈) | 규격 박스 모듈 조립 | **규격 박스 모듈이 격자로 조립된 벽면, 모듈 사이 일정한 미세 접합선, 평평하고 균일한 패널면** (발광은 그래픽면 한정 옵션 — 아래 참조) |
| **옥타놈/옥타늄** (기본/시스템) | 알루미늄 폴+바+패널 | **은색 알루미늄 프레임 격자가 노출, 그 사이 백색 인필 패널** |
> 원본 이미지에서 위 셋 중 하나를 먼저 판정해 해당 모드만 적용한다. (업체마다 목공/블럭을 묶어 부르기도 하나, 실사화는 위 외형 식별자로 구분한다.)
> ★블럭부스 = "규격 모듈 조립"이 핵심 정의다. 내부 LED 발광은 일부 고급형의 옵션일 뿐 정의가 아니다 — 비발광 블럭부스가 오히려 다수다. 발광을 식별자로 강제하면 벽 전체가 라이트박스처럼 전면발광하는 실패가 난다(3중 검수 만장일치 BLOCKER).

**★ 옥타놈 성공 문장 (옥타놈일 때 반드시 한 문장으로 고정 삽입):**
> `"The booth must read as a modular shell-scheme system, not a seamless drywall room: every wall bay shows visible panel-to-panel seams, slim silver anodized aluminum vertical uprights standing proud of the flat white infill panels, horizontal top beams, and slightly raised aluminum base rails."`

**모드 A — 옥타놈 / 시스템 기본부스 (프레임 노출 격자형):**
- 구조: `Octanorm-style modular exhibition shell scheme, slim silver anodized aluminum post-and-beam frame, narrow vertical posts proud of the flat white infill panels, crisp specular highlights along the post edges, standard 3x3m booth, eye-level wall height`
- 재료: `flat matte white melamine or PVC foam infill panels, non-reflective panel surface`; 그래픽은 원본에 있을 때만 `printed graphic panel inserts`
- 사인: `fascia header band above the booth, kept as a blank or simple placeholder signage area without legible text` (실제 상호는 후처리 합성 — 글자 생성은 깨짐 유발)
- 조명/바닥: `clip-on spotlight arms mounted on the fascia, track spotlights washing the panels, physically mounted fixtures, grey needle-punch exhibition carpet, brushed aluminum base rails seating the booth on the floor`

**모드 B — 목공 독립부스 (매끈한 면 볼륨형):**
- 구조: `custom-built exhibition booth with smooth continuous plastered and painted wall surfaces, sharp clean flush corners, solid built walls`
- 재료/디테일: `matte painted walls or adhesive vinyl-wrapped walls, laminate finish, branded feature walls`; 로고 사인은 원본에 있을 때만 `edge-lit acrylic logo` (한 면에만)
- ★대조 앵커(한 문장 삽입): `"…a solid custom-built wall, not a modular framed system and not an exposed aluminum grid."`

**모드 C — 블럭부스 / 규격 박스 모듈 조립 (modular block assembly):**
- 구조: `modular block-panel booth assembled from standardized rectangular box modules, fine consistent seams between modules, clean rectilinear module grid, flat even matte panel faces`
- 발광은 옵션(국소 게이팅): 원본에 발광 그래픽 벽이 있을 때만 → `only the graphic panel is softly lit from behind, while the surrounding module structure, floor and ceiling are lit by ambient hall light` (벽 전체를 발광시키지 않는다)
- ★대조 앵커(한 문장 삽입): `"…a modular box-panel assembly, not a seamless custom-built wall and not an exposed aluminum post-and-beam grid."`

**★ 그래픽·마감 실재료 서브블록 (★원본에 실제 보이는 재료 1~2종만 골라 주입 — 6종 나열 금지(material soup). 없는 텍스트/로고 생성 금지):**
- 현수막(플렉스): `PVC flex banner graphic, slight surface undulation, satin sheen`
- 켈지(점착 실사출력): `matte (or gloss) self-adhesive vinyl film, tightly wrapped flat to the wall, crisp saturated color`; 백켈지=`opaque solid backing` / 투명켈지=`translucent vinyl on glass`
- 커팅시트: `cut vinyl lettering and solid-color film logos, sharp die-cut edges`
- SEG 텐션패브릭: `SEG silicone-edge tension fabric graphic, taut smooth flat matte fabric, edge sitting flush in a slim aluminum channel`
- 포맥스/폼보드: `rigid foam PVC board (Foamex), matte smooth surface, UV-printed sharp graphics`; 입체글자=`raised cut-out lettering`
- 아크릴: `glossy acrylic panel, transparent or frosted`
- ★발광·광택 단일화: `backlit / edge-lit / strong specular / high-gloss` 토큰을 한 프롬프트에 여럿 겹치지 않는다 — bloom·전면발광·플라스틱화 유발. 발광/광택은 **주 피사체 재료 1개에만** 적용하고, 나머지 면은 `matte, non-emissive`로 눌러 명시한다.

**★ 인물·현장 서브블록 (★조건부 — 원본 이미지에 실제로 인물이 있을 때만 켠다):**
> Lineart/Canny primary 파이프라인에서는 컨트롤 소스(부스 렌더/도면)에 인물 엣지가 없다. 컨트롤에 없는 인물을 프롬프트로만 주입하면 얼굴·손 붕괴·반투명 고스팅·구조 경합이 난다(3중 검수 BLOCKER). 원본에 인물이 없으면 이 서브블록을 통째로 생략한다.
- 원본 근경에 인물이 있을 때만: `Korean booth staff in a business suit or a plain branded uniform, natural working posture` (텍스트 없는 복장)
- 배경 군중: `a few small out-of-focus figures in the far background of the aisle` (원거리·아웃포커스 한정, 밀집 금지)
- ★텍스트 발생 소품은 넣지 않거나 blank로: 명찰은 `a plain lanyard with a blank card`까지만, 브로슈어·명함함·브랜드백은 글자 깨짐을 부르므로 생략하거나 `unbranded, no legible text`로. (fascia 텍스트 금지 원칙과 동일 — 글자는 후처리 합성)
- ★원본에 인물이 없는데 사람을 넣고 싶다면 → 이 스킬로 굽지 말고 **person-layer-maker**로 인물을 별도 레이어 생성해 포토샵 합성한다(위치·인원·교체 수정 가능).

**전시장 배경 (부스가 홀 안에 놓인 광각 샷일 때만):**
- 배경: `exposed high-ceiling truss grid, fire sprinkler pipes, suspended rigging banners overhead, rows of neighboring booths, trade-fair aisle, grey aisle carpet`
- 오브젝트: `neighboring booth edges, brochure stands, cable covers, small product displays, aisle stanchions`
- 조명: `cool neutral exhibition hall lighting from metal-halide and fluorescent fixtures, slight fluorescent green bias only in ambient shadows, mixed with warm booth spotlights` (4000K대는 중성백색이지 녹색이 아니다 — 녹색끼는 그림자에만 미세하게)
- 촬영: `deep-focus architectural trade-show photography` (얕은 심도 금지 — 구조 보존 약화)

**★ 엔진 규칙 (전시부스는 반드시):** 규칙적 직선격자라 i2i 시 ControlNet 병행이 사실상 필수다. 우선순위 — **Lineart(또는 Lineart-realistic) 또는 Canny를 primary 구조 컨트롤**(포스트·패널·모서리 윤곽 보존), **MLSD는 긴 직선·소실점 보조로 optional**, **Depth는 부스 볼륨·통로 전후관계 보조로만** (특히 블럭부스는 Depth로 박스 모듈 입체감 보존). MLSD 단독은 짧은 포스트 두께·패널 seam·조명 암을 날려 부족하다. GPT 단독 경로보다 SD+ControlNet을 권장한다. **FLUX 파이프라인이면 FLUX-native 컨트롤(Canny-dev 또는 Depth-dev 택일, 동시 사용은 ComfyUI 스태킹 검증 필요)로 구성한다 — SD/SDXL 계열 CN은 로드 불가.** 참조용 커뮤니티 파이프라인: PH's Archviz x AI(civitai, SDXL→FLUX 단계식 — 2026-07 조회 기준, dev 계열 비상업 라이선스 주의).

**★ GPT-image 경로 긍정형 잠금문 (NEGATIVE 대신 PROMPT에 이어붙임):**
> `"straight rigid booth structure, crisp orthogonal module grid, clean panel seams, physically mounted spotlights, blank or deliberately simple signage, the booth reads as a real exhibition stand photographed on a trade-show floor."`

---

## 예시

> **※ 아래 예시는 SD/디퓨전 경로용(NEGATIVE 포함).** GPT image 경로에서는 NEGATIVE 섹션을 입력에 사용하지 않고 PROMPT만 넣으며, PROMPT 말미의 부정문 블록(`No render look...`)을 9단계의 GPT 긍정형 대체 문장으로 바꾼다.

### 단일 모드 — 한국 공공 도서관 서비스홀

```
PROMPT
Ultra photorealistic architectural interior photography of a modern Korean public library service center converted from a CGI architectural render while preserving the exact original camera position, eye-level perspective, composition, room proportions, ceiling layout, U-shaped service counter placement, modular shelving wall configuration, long table and chair arrangement, circulation, and spatial hierarchy. Transform the space into a believable built interior with realistic materiality and architectural detailing. Preserve exactly the original design color palette without any change, reinterpretation, or color shift — convert CGI surface quality to photographic realism only, do NOT redesign or recolor any material. mustard yellow and warm golden ochre — counter front panels, shelving units, ceiling soffit band; dusty rose and mauve — all wall surfaces; cobalt blue — all chair shells; teal and cyan — shelving accent panel insets; dark walnut brown — suspended ceiling slat baffles; light natural oak — long table surface; gray — large-format floor tiles; white matte — ceiling panels, gate frame, and countertop. Preserve the suspended dark walnut wood ceiling baffles exactly as shown, but render them with authentic walnut grain variation, slight tonal inconsistencies, micro scratches, realistic recessed lighting trim depth, and believable mounting hardware. Preserve the mustard yellow modular shelving wall exactly as shown, but render with realistic acoustic fabric surface tension on counter panels, visible weave texture, panel seams, and matte surface absorption. The cobalt blue polypropylene chairs feature realistic plastic surface with soft specular highlights on curves, slight seat deformation, thin black metal legs with natural wear. The light natural oak long table shows authentic wood grain, subtle pore texture, low-sheen satin finish, and believable edge detailing. Large-format gray porcelain floor tiles with realistic grout line variation, subtle tonal differences between tiles, slight wear near circulation zones. Dusty rose matte plaster walls with soft surface texture, realistic paint absorption, shadow at corners. Include HVAC diffusers, electrical outlets, signage mounting details, ceiling mounting hardware, counter edge profiles, shelf hardware, realistic monitor stands with cables, reception accessories, and minimal institutional clutter. Physically believable furniture scale, realistic object placement, and subtle everyday institutional presence. Warm institutional recessed ceiling downlights with realistic localized illumination pools and trim ring depth, soft linear LED strips with believable luminance falloff, controlled 3000K–4000K institutional lighting, soft shadow gradients, controlled exposure balance between bright exterior windows and interior shadow detail, subtle photographic sensor grain. Replace the CGI figure with a realistic casually dressed Korean woman captured candidly from behind with natural body proportions, realistic hair strands, natural clothing folds, authentic skin texture, and believable posture. The final result must feel like a professionally photographed real built interior space. Ultra high detail, natural color science, realistic dynamic range, editorial architectural photography quality. Captured with the exact same camera position, camera height, focal length, field of view, angle of view, and aspect ratio as the original image, with every wall and ceiling element occupying the same fraction of the frame as in the original, all four frame edges aligning with the same points of the original scene, and the vanishing points landing in the same screen positions. Match the original framing one-to-one, as a professional full-frame architectural interior photograph indistinguishable from a real built environment. No render look, no archviz appearance, no plastic materials, no fake reflections, no synthetic atmosphere. Completely believable real-world interior photograph.

NEGATIVE (SD/MJ/ComfyUI 전용 — GPT image·Magnific/nanobanana에는 입력하지 않음)
cartoon, anime, illustration, sketch, watercolor, concept art, matte painting, stylized, painterly, CGI, archviz look, render look, Unreal Engine look, Blender render look, game-engine look, SketchUp look, Rhino viewport look, Revit model look, Enscape look, D5 Render look, Lumion look, Twinmotion look, V-Ray render look, Corona render look, clay render, white model, artificial rendering, synthetic lighting, fake global illumination, plastic rendering, showroom CGI materials, changed camera angle, changed viewpoint, changed perspective, changed framing, changed crop, reframed shot, perspective reinterpretation, altered focal length feel, changed color palette, recolored surfaces, altered material colors, color shift, changed accent color, changed wall color, changed upholstery color, material redesign, replaced materials, color reinterpretation, desaturated colors, changed room geometry, changed ceiling height, changed ceiling shape, changed wall positions, changed floor level, wrong scale, unrealistic proportions, redesigned architecture, distorted room, enlarged room, warped walls, deleted architectural elements, moved walls, moved shelving, moved counter, missing ceiling elements, floating architectural elements, missing architectural details, plastic materials, fake wood, fake stone, fake glass, flat painted surfaces, unrealistic textures, fake reflections, oversmoothed surfaces, texture repetition, procedural textures, glossy plastic wood, glossy plastic surfaces, artificial textures, incorrect material scale, unrealistic wood texture, mirror glass, flat glazing, impossible reflections, floating furniture, toy-like furniture, repeated objects, cloned objects, unrealistic furniture scale, warped furniture, warped shelves, deformed chairs, noisy geometry, blurry edges, mannequin people, render people, entourage people, cutout people, CGI humans, 3D humans, cloned people, stock-photo models, fashion models, perfect skin, plastic skin, wax skin, AI beauty face, distorted faces, blurry faces, broken hands, bad anatomy, extra limbs, oversized people, tiny people, fantasy lighting, excessive bloom, artificial glow, fake ambient occlusion, extreme HDR, overexposure, oversharpening, glowing corners, halo effects, surreal lighting, synthetic atmosphere, unrealistic ceiling lighting, incorrect lighting direction, noisy render artifacts, random text, logo, watermark, impossible scale, fake luxury materials, sci-fi architecture, empty sterile space, low resolution, blurry materials
```

### 리모델링 모드 — 이미지1(화이트모델 주방) + 이미지2(미드센추리 모던)

```
PROMPT
Use Image 1 as the immutable architectural structure, room geometry, camera, composition, and spatial reference, and use Image 2 only as the remodeling style, material, furniture, lighting, and atmosphere reference. Ultra photorealistic architectural interior photography of a contemporary Korean apartment kitchen applying mid-century modern design language from Image 2 while preserving the exact original camera position, eye-level perspective, lens perspective, composition, room proportions, ceiling height, wall positions, window placement, and all architectural structure from Image 1. Transform the space into a believable built interior with realistic materiality and architectural detailing. Preserve exactly the architectural structure and fixed-element colors from Image 1, while applying the material and furniture palette of Image 2 — convert CGI surface quality to photographic realism only, and do NOT invent elements absent from both images. Warm walnut flat-front cabinetry with realistic wood grain variation, subtle panel seams, believable edge banding, and shadow gaps. Preserve the countertop position exactly as shown, but render with quartz surface showing natural stone veining, diffuse reflections, realistic edge detailing, and subtle surface imperfections. Ceramic tile backsplash with realistic grout lines and subtle surface variation. Brushed brass hardware and faucet with controlled specular highlights and directional metallic texture. Include subtle countertop reflections, realistic appliance tolerances, believable cabinet joints, HVAC diffusers, outlet positions, and edge conditions. Realistic kitchen objects: fruit bowl, dish towels, cutting board, small appliances at proper scale. Balanced natural daylight with realistic task lighting, under-cabinet LED warm glow, controlled exposure balance between bright exterior window and interior luminance, subtle photographic sensor grain. The final result must feel like a professionally photographed real built interior space. Ultra high detail, natural color science, realistic dynamic range, editorial architectural photography quality. Captured with the exact same camera position, camera height, focal length, field of view, angle of view, and aspect ratio as the original image, with every wall and ceiling element occupying the same fraction of the frame as in the original, all four frame edges aligning with the same points of the original scene, and the vanishing points landing in the same screen positions. Match the original framing one-to-one, as a professional full-frame architectural interior photograph indistinguishable from a real built environment. No render look, no archviz appearance, completely believable real-world interior photograph.

NEGATIVE (SD/MJ/ComfyUI 전용 — GPT image·Magnific/nanobanana에는 입력하지 않음)
cartoon, anime, illustration, sketch, watercolor, concept art, matte painting, stylized, CGI, archviz look, render look, Unreal Engine look, Blender render look, game-engine look, SketchUp look, Enscape look, D5 Render look, Lumion look, Twinmotion look, V-Ray render look, Corona render look, clay render, plastic rendering, showroom CGI materials, changed camera angle, changed viewpoint, changed perspective, changed framing, reframed shot, changed color palette, recolored surfaces, altered material colors, color shift, material redesign, replaced materials, changed room geometry, changed ceiling height, changed wall positions, changed window placement, wrong scale, unrealistic proportions, redesigned architecture, distorted room, warped walls, deleted architectural elements, moved walls, moved windows, missing architectural details, plastic materials, fake wood, fake stone, fake glass, flat painted surfaces, fake reflections, oversmoothed surfaces, texture repetition, procedural textures, glossy plastic wood, glossy plastic surfaces, artificial textures, incorrect material scale, mirror glass, flat glazing, impossible reflections, floating furniture, toy-like furniture, repeated objects, cloned objects, unrealistic furniture scale, warped furniture, deformed chairs, mannequin people, render people, entourage people, cutout people, CGI humans, 3D humans, fashion models, perfect skin, plastic skin, wax skin, AI beauty face, distorted faces, blurry faces, broken hands, bad anatomy, fantasy lighting, excessive bloom, artificial glow, fake ambient occlusion, extreme HDR, glowing corners, fake global illumination, surreal lighting, synthetic atmosphere, incorrect lighting direction, random text, logo, watermark, fake marble veining, impossible appliance reflections, oversized kitchen island, floating cabinetry, low resolution, noisy geometry, blurry materials, copied geometry from the second reference image, copied room structure from the second reference image, structural transfer from reference image
```

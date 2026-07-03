---
name: arch-prompt-maker
description: "건축 외관 CGI · 렌더 · 모델 이미지를 Stable Diffusion / Midjourney / ComfyUI image-to-image용 사실적 건축 사진 프롬프트로 변환하는 전문 스킬. 사용자가 건물 외관 이미지와 함께 '프롬프트 만들어줘', '실사화해줘', 'SD 프롬프트', 'MJ 프롬프트', 'i2i 프롬프트 써줘', '프롬프트 뽑아줘', '사실적으로 만들어줘', '렌더 느낌 없애줘', '사진처럼 만들어줘' 같은 말을 하면 반드시 이 스킬을 사용한다. 입력 유형: SketchUp · Rhino · Revit · Lumion · Enscape · D5 · V-Ray · Corona · Twinmotion · Blender 렌더, archviz, 클레이 모델, AI 렌더 — 모든 건축 외관 CGI. 지원 건물: 아파트 · 공장 · 오피스 타워 · 상업 · 공공 · 교육 · 의료 건물. 지원 작업: 실사화, 야간 전환, 황금시간대, 날씨 변경, 파사드 재료 교체, 사이니지 수정, 조경 업그레이드, 인물 추가. 인테리어 · 실내 공간(전시부스 실내 포함) 프롬프트는 interior-prompt-maker를 사용한다. 레퍼런스 이미지의 조명을 이식하는 요청은 cinematic-exhibition-lighting을 쓰고, 단순 야간/황금시간대/날씨 전환은 외관이면 이 스킬이 담당한다. 주 피사체 기준: 파사드·매스·외부 공간이 화면 주체면 이 스킬, 실내 공간이 주체면 interior — 둘 다 크게 보이면 사용자에게 확인. 이미지가 없으면 원본 이미지 첨부와 실내/외 여부를 먼저 확인한다."
---

# 건축 외관 Image-to-Image 프롬프트 메이커

건축 CGI/렌더/모델 외관 이미지를 실제 건축 사진과 구분 불가능한 수준의 프롬프트로 변환한다.

## ★ 구도 보존 최우선 원칙 (실패 1순위 방지)

i2i 변환의 가장 흔한 실패 = **구도(화각·줌·시점·종횡비) 틀어짐**. 근본 원인은 문구가 아니라 **종횡비 불일치**다 — 원본을 모델이 다른 비율로 강제하면 모자란 부분을 "프레임 밖을 발명"해 채우며 줌아웃·요소 추가가 생긴다. 따라서 문구보다 1·2가 먼저다.

1. **★ 실행 전 원본을 출력 합법 비율로 사전 크롭 (진짜 해결책)** — 모델이 엣지에서 장면을 발명할 여지를 구조적으로 없앤다. 엔진의 출력 비율 제약을 먼저 확인한다: **gpt-image-1 계열은 1:1 / 3:2 / 2:3 고정**이므로 원본을 미리 그 비율로 크롭해 넣고, **gpt-image-2는 제약 내 임의 해상도를 지원**하므로 원본 비율을 그대로 유지한다(불필요한 크롭 금지). 크롭으로 잘리는 면적이 15%를 넘으면 중요 요소 절단 위험을 사용자에게 경고 후 진행한다(이 경고는 출력 비율 맞춤 크롭에만 적용). 크롭은 사용자에게 목표 비율·방향을 1~2줄로 안내하거나, 이미지 파일 접근이 가능하면 직접 크롭 후 진행한다.
2. **종횡비 원본 일치** — 사전 크롭한 비율과 출력 비율을 동일하게 둔다.
3. **절대 초점거리 숫자 금지** — PROMPT에 `24mm`·`50mm` 등 숫자 초점거리를 쓰지 않는다(아래 "렌즈/카메라 선택 원칙" 표는 화각 감각 참조용일 뿐). 모델이 원본 화각을 무시하고 그 렌즈로 재해석해 광각화·줌아웃을 일으킨다.
4. **GPT image 경로 주의 — PROMPT 전체에서 부정문 금지** — gpt-image는 부정문(`No zoom change`, `no reframing`)을 "분홍 코끼리"로 오히려 유발하고, NEGATIVE 단락도 장면 묘사로 읽는다. GPT로 돌릴 땐 **본문의 모든 부정문 블록(카메라 잠금·기하학 잠금·컬러 잠금·재료 Avoid 문구·최종 선언의 "not an enhanced render" 포함)을 긍정형으로 바꿔 쓰고, NEGATIVE는 넣지 않는다**(PROMPT만 사용). 긍정형 대체 예 —
   - 카메라: `"preserve the exact same camera position, camera height, framing, field of view, and aspect ratio as the input, with every element occupying the same fraction of the frame, all four frame edges aligning with the original, and the vanishing points in the same screen positions"`
   - 기하학: `"keep every architectural element in its exact original position, scale, form, and proportion, reproducing the input massing, rooflines, openings, and site composition one-to-one"`
   - 컬러: `"reproduce the exact original color palette of every facade element one-to-one"`
   - 최종 선언: `"a newly completed real building photographed on-site in Korea, with the material fidelity and lighting behavior of documentary architectural photography"`
   부정문 LOCK과 NEGATIVE는 SD/MJ/ComfyUI 디퓨전 경로 전용이다. (긍정형 변환 대상은 **이미지 생성 PROMPT 텍스트 안의 부정 표현뿐** — 이 스킬 문서의 절차·규칙 문장은 변환 대상이 아니다.)
5. **엔진 선택** — 구도 픽셀 보존이 최우선이면 GPT 엔진 대신 ControlNet(depth+lineart) 기반 SD i2i, 또는 Magnific 업스케일러(0~1 스케일 기준 Creativity 0.1~0.3 낮게 / Resemblance 0.85~1.0 높게 시작)를 쓴다.
6. **검증** — 결과 위에 원본을 50% 투명도로 겹쳐 수평선·소실점·네 모서리 일치를 확인하고, 어긋나면 크롭으로 정렬한다.

## 빠른 흐름

0. **(구도 보존 중요 시) 실행 전 원본을 출력 합법 비율로 사전 크롭** — 위 "구도 보존 최우선 원칙" 참조
1. 입력 이미지에서 **건물 유형** 파악 (공장/아파트/오피스/상업/공공/교육/의료)
2. 사용자 요청에서 **변경 사항** 추출 (야간 전환, 황금시간대, 재료 교체 등)
3. 뷰 변경 없으면 **ABSOLUTE CAMERA LOCK** 적용, 변경 요청 시 새 뷰로 교체
4. 13단계 PROMPT + 15카테고리 NEGATIVE 작성
5. **PROMPT + NEGATIVE 두 섹션만** 출력 — 설명 없음. **단 GPT image 경로에서는 NEGATIVE를 생략하고 PROMPT만 출력하며, ABSOLUTE CAMERA LOCK을 부정문 대신 긍정형으로 쓴다(구도 보존 원칙 4 참조).**

카메라 브랜드 (Sony, Canon, Nikon 등) 절대 명시하지 않는다.
MJ 파라미터 (`--v`, `--iw`, `--ar` 등) 절대 포함하지 않는다.

## 출력 원칙

- **PROMPT와 NEGATIVE 두 섹션만** 출력한다 (단, **GPT image 경로에서는 NEGATIVE를 생략하고 PROMPT만** — 구도 보존 원칙 4)
- 설명, 분석, 주석, 이미지 생성 일절 없음 — 단, 사전 크롭이 필요한 경우 PROMPT 출력 전에 크롭 안내(목표 비율·방향) 1~2줄은 허용
- PROMPT는 **하나의 연속된 영어 단락**으로 작성
- NEGATIVE는 **하나의 연속된 영어 단락**으로 작성

```
PROMPT
[연속 영어 단락]

NEGATIVE
[연속 영어 단락]
```

---

## PROMPT 작성 순서 (엄격히 준수)

아래 13단계를 반드시 이 순서로 작성한다.

### 1. 입력 이미지 레퍼런스 및 변환 의도
항상 첫 번째. 업로드된 이미지가 불변의 기준임을 선언.

포함 내용:
- 이미지가 불변(immutable) 기준임을 명시
- color를 포함한 4가지 참조 차원 선언: camera / composition / color / architectural reference
- 소스 유형 명시 (SketchUp 모델, 클레이 렌더, CGI archviz, AI 렌더 등)
- 변환 목표: 실제 촬영된 건축 사진으로 변환

기본 구문 (이미지 입력 시):
> `"Use the input image as an immutable camera, composition, color, and architectural reference."`

이어서 변환 목표 선언:
> `"Convert the existing [CGI render / SketchUp-like massing model / archviz visualization] into a highly realistic real-world architectural photograph of [건물유형] in [지역], Korea. Replace all synthetic rendering artifacts, visualization materials, and archviz shortcuts with physically plausible real-world construction materials and authentic site conditions."`

---

### 2. 카메라 잠금 / 뷰 지시
항상 두 번째.

**뷰 변경 없을 때 (기본값) — ABSOLUTE CAMERA LOCK:**
```
ABSOLUTE CAMERA LOCK: preserve exactly the original camera position, camera height,
camera tilt, camera yaw, lens perspective, focal length feel, framing, crop, horizon line,
vertical alignment, foreground/background relationship, viewing angle, and overall composition.
The camera must not shift in any way. No angle change, no viewpoint change, no orbit,
no zoom change, no reframing, no recropping, and no perspective reinterpretation.
```

**조감도(드론뷰) 시 추가:**
```
ABSOLUTE CAMERA LOCK: preserve exactly the original aerial camera position, bird's-eye
perspective, drone height, camera tilt, camera yaw, horizon logic, framing, crop,
lens perspective, focal length feel, viewing direction, and overall composition.
No angle change, no orbit, no zoom shift, no reframing, and no perspective reinterpretation.
```

**뷰 변경 요청 시:**
- 카메라 잠금 대신 새로운 뷰 지시로 교체
- aerial / street-level / eye-level / frontal elevation / diagonal perspective / detail shot 등 명시

---

### 3. 기하학 잠금 / 건축 보존
카메라 잠금 직후. 가장 중요한 섹션.

항상 포함:
```
ABSOLUTE GEOMETRY LOCK: preserve exactly the original building form and site composition
with zero design change. Strictly preserve the exact massing, proportions, rooflines,
facade rhythm, openings, glazing divisions, [이미지 특정 요소들 나열], slab edges,
column positions, structural edges, road alignment, landscape boundaries, retaining walls,
site levels, and spatial hierarchy exactly as shown in the input image.
Do not move, scale, rotate, redesign, delete, extend, simplify, reinterpret, or deform
any architectural element.
```

**[이미지 특정 요소들 나열] 예시:**
- 공장: `loading dock position, entrance canopy geometry, panel divisions`
- 학교: `fence position, gate design, perimeter wall layout`
- 아파트: `balcony geometry, railing pattern, window rhythm`
- 오피스: `curtain wall system, mullion spacing, podium proportions`

---

### 4. 컬러 팔레트 잠금 ★ (항상 포함)
기하학 잠금 직후, 재료 묘사 이전. 색상 드리프트 방지의 핵심.

선언 문구:
> `"Preserve exactly the original building color palette without any change, reinterpretation, or color shift. The task is to convert CGI surface quality to photographic realism only — do NOT redesign, recolor, or replace any material color or facade color."`

이어서 이미지에 보이는 모든 색상을 요소별로 명시:

패턴: `"[색상 설명] — [건물 요소]"`

| 요소 | 예시 |
|---|---|
| 파사드 주색상 | `white / light gray — insulated metal panel facade` |
| 보조 파사드 | `beige granite — podium cladding`, `warm sand — exterior concrete` |
| 악센트 | `red — entrance canopy`, `blue — loading dock canopy` |
| 유리 톤 | `dark-tinted low-e glazing — curtain wall`, `silver aluminum — mullion system` |
| 지붕/구조 | `dark gray — roofline parapet`, `silver — aluminum trim and flashing` |
| 바닥/대지 | `dark asphalt — site circulation`, `light gray — concrete sidewalk` |

---

### 5. 사용자 요청 수정 블록 (조건부)
컬러 잠금 직후. **명시적으로 요청된 변경사항만** 포함.

가능한 변경 예시:
- 재료 교체, 야간 전환, 날씨 변경, 파사드 업데이트
- 사람 추가, 조경 업그레이드, 계절 변환, 사이니지

**중요:** 요청된 요소만 변경. 나머지는 모두 보존.

**★ 잠금 스코프 규칙 (무조건 잠금과 요청 변경의 충돌 방지):** 요청으로 변경되는 요소는 컬러/기하학 잠금 문구에서 제외하고 `"...except the requested [요소] change"` 형태로 한정한다. NEGATIVE에서도 해당 변경과 충돌하는 항목을 뺀다 — 예: 재료 교체 요청 시 D의 `material redesign`·`changed material colors` 중 해당 요소 관련 토큰 제외, 뷰 변경 요청 시 A(카메라 실패) 전체 제외.

---

### 6. 건축 정체성 및 공간 묘사
이미지에 실제 존재하는 것을 묘사.

외관 장면 요소:
- 건물 매싱, 파사드 시스템, 유리, 멀리언, 포디움
- 테라스, 발코니, 도로, 연석, 보도, 옹벽
- 인접 건물, 스카이라인, 지형

---

### 7. 재료 사실성 변환 (요소별 색상 명시)
건축 묘사 직후. 합성 재료 → 실제 건축 재료. **요소별로 색상과 함께 작성.**

작성 패턴: `"The [색상] [재료명] should [사실적 물성 묘사]..."`

**유리/커튼월:**
`realistic architectural glazing with subtle reflectivity, layered environmental reflections, realistic interior visibility variation, glazing depth, mullion shadowing, edge reflections, and slight optical imperfections. Avoid perfectly black glass or mirror-like rendering reflections.`

**금속 멀리언/트림:**
`realistic metallic behavior with subtle fabrication irregularities, reflectance variation, anodized finish depth, weather exposure, joint tolerances, sealant detailing, and nuanced daylight response.`

**콘크리트/석재:**
`authentic installed stone/concrete with geological grain variation, subtle color shifts, panel joints, edge wear, realistic seam tolerances, anchoring logic, accumulated urban dust, and authentic surface transitions.`

**금속 패널 (산업/물류):**
`insulated metal sandwich panels with subtle joint depth, slight tonal variation, precise panel seams, realistic fastening logic, clean surface reflections, and real-world facade thickness.`

**도장면/벽돌:**
`painted exterior panels with realistic paint absorption, subtle surface texture, crack-free but non-perfect finish, weathering hints, and believable construction tolerances.`

---

### 8. 도로 및 대지 사실성
재료 다음.

포함 내용:
`realistic asphalt texture, subtle tire wear, drainage slopes, utility covers, patch repairs, curb staining, expansion joints, maintenance traces, road paint wear, realistic concrete coloration, and slight urban grime accumulation. No perfect rendering surfaces.`

한국 맥락 (기본값):
`Korean urban paving with accurate asphalt texture, curb detailing, drainage lines, paving joints, slight imperfections, and realistic slope transitions. Korean road markings and lane geometry.`

---

### 9. 조경 사실성
도로 다음.

포함 내용:
`botanically believable Korean urban planting with varied tree species, asymmetrical canopies, authentic pruning patterns, leaf translucency, seasonal realism, slight wind response, age variation, irregular branch structure, and naturally maintained planting beds. Avoid cloned trees, procedural landscaping, or rendering-library vegetation.`

---

### 10. 차량 및 도시 맥락

포함 내용:
`realistic contemporary Korean vehicles with physically accurate paint reflections, glazing, tire detail, and natural traffic positioning. Korean urban density, utility poles if appropriate, restrained signage, and believable street infrastructure.`

---

### 11. 인물 사실성 (조건부)
다음 경우에만 포함:
- 소스 이미지에 인물이 있을 때 / 사용자 요청 시 / 스케일 참조가 유용할 때

포함 내용:
`candid Korean pedestrians with natural posture, proper architectural scale, authentic movement, realistic skin texture, subtle clothing folds, casual contemporary attire, and documentary-style behavior.`

---

### 12. 조명 및 사진적 동작
**차량/인물 이후** — 이 순서 엄수.

포함 내용:
- 물리적으로 근거 있는 자연광 동작
- 노출, 대기 부드러움, 그림자 전환
- 현실적 하늘 반사 동작
- 미세한 사진 센서 그레인
- CGI 글로벌 일루미네이션 제거

예시 구문:
> `"Lighting should behave like real architectural photography. Use physically grounded daylight with balanced exposure, realistic atmospheric softness, natural shadow transitions, subtle haze depth, realistic sky reflection behavior, restrained highlights, accurate white balance, realistic shadow density, and fine photographic sensor grain. Eliminate all CGI global illumination look, fake HDR, excessive contrast, bloom, artificial glow, and oversaturated rendering colors."`

**시간대/날씨별 키워드 (아래 섹션 참조)**

---

### 13. 준공 상태 + 최종 선언
PROMPT 마지막.

**신축 완공:**
> `"The final image should feel like a high-end professional architectural photograph — realistic, grounded, urban, observational, and physically believable rather than stylized or cinematic. The result must look like a newly completed real building photographed on-site in Korea, not an enhanced render."`

**노후 건물 시:**
> `"The final image should feel like a documentary architectural photograph of an existing building — subtle wear, believable patina, natural weathering, honest materiality, and authentic urban aging rather than CGI stylization."`

---

## 렌즈 / 카메라 선택 원칙

**카메라 브랜드는 절대 명시하지 않는다** (Sony, Canon, Leica 등).
대신 **화각과 원근 동작**을 묘사한다.

> **★ 아래 표의 mm 범위는 화각 감각 참조용일 뿐, PROMPT에는 mm 숫자를 쓰지 않는다 — 키워드(화각·원근 동작)만 사용한다. (위 "구도 보존 최우선 원칙" 참조)**

| 장면 유형 | 화각 범위 | 키워드 |
|---|---|---|
| 넓은 가로 뷰 | 24–28mm | `restrained wide-angle architectural photography, natural street-level field of view, corrected architectural verticals` |
| 정면 입면 | 50–85mm | `compressed perspective, balanced facade compression, corrected vertical geometry` |
| 조감/항공 | 28–50mm | `realistic aerial architectural photography, believable urban scale, drone-height perspective` |
| 파사드 클로즈업 | 70–100mm | `compressed architectural detail photography, material-focused framing` |

---

## 시간대 / 날씨 처리

소스 이미지에서 자동 감지 후 사용자 요청 없으면 보존.

### 황금시간대
```
warm low-angle sunlight, soft golden-hour illumination, long natural shadows, warm facade highlights,
atmospheric warmth, subtle amber reflections, soft directional light, controlled highlight rolloff,
realistic sunset exposure, natural sky glow, realistic dusk atmosphere
```

### 흐린 날 (Overcast)
```
diffuse overcast daylight, soft ambient illumination, cloud-filtered light, shadowless soft lighting,
balanced neutral exposure, subtle atmospheric softness, muted sky luminance, realistic cloudy-day contrast,
restrained reflections, physically believable diffuse lighting
```

### 정오 직사광
```
bright midday sunlight, crisp architectural shadows, high sun angle, strong natural daylight,
realistic solar contrast, sharp shadow edges on facade articulation, true daylight color temperature
```

### 야간
```
realistic architectural night photography, controlled interior illumination, warm lobby glow,
believable urban night lighting, subtle facade reflections, physically plausible luminance,
realistic street lighting, balanced nighttime exposure, soft illuminated glazing,
restrained contrast, realistic mixed color temperatures
```

### 비/젖은 날
```
wet pavement reflections, rain-darkened concrete, soft rainy-day atmosphere, overcast rainy lighting,
reflective asphalt texture, damp material surfaces, subtle atmospheric haze,
diffused rainy daylight, softened shadow contrast
```

---

## 건물 유형별 접근

### 산업/공장
**특화 기하학:** loading dock position, entrance canopy geometry, service yard, roof equipment
**재료:** 단열 금속 패널, 아연도금 강재, 프리캐스트 콘크리트, 산업용 조인트
**대지:** 트럭 타이어 자국, 배수 채널, 산업 인프라, 아스팔트 마모
**조명:** 흐린 날 기본값. 드라마틱 석양 금지
**차량:** 배달 트럭, 지게차, PPE 작업자

### 주거 아파트
**특화 기하학:** balcony geometry, railing pattern, window rhythm, curtain wall repetition
**재료:** 따뜻한 주거 스케일 마감, 발코니 난간 깊이감
**대지:** 놀이터, 보행 동선, 식재 중정, 자전거 주차
**조명:** 황금시간대·저녁 온기 선호. 창문 조명 다양화 (동일 글로우 금지)
**인물:** 가족, 입주자, 유모차, 자전거

### 상업/리테일
**특화 기하학:** storefront layout, canopy positions, entrance sequences, signage zones
**재료:** 더 깔끔한 유리, 세련된 금속 트림, 광택 포장
**대지:** 야외 좌석, 보행자 밀도, 배달 구역
**조명:** 레이어드, 저녁 친화적. 과조명 금지
**인물:** 쇼퍼, 카페 활동, 배달 밴, 활발한 보행

### 오피스 타워
**특화 기하학:** curtain wall system, mullion spacing, podium proportions, tower crown
**재료:** 유리 깊이감, 멀리언 두께, 석재 포디움 디테일
**대지:** 플라자 디자인, 드롭오프 존, 비즈니스 지구 맥락
**조명:** 현실적 오피스 점유, 층별 조명 변화 (동일 글로우 금지)
**인물:** 오피스 워커, 비즈니스 복장, 택시, 통근 동선

### 공공/시민 건축
**특화 기하학:** public plaza, civic entrance sequences, colonnade, atrium
**재료:** 석재·노출 콘크리트·시민 목재, 내구성·기념비적
**대지:** 모임 공간, 시민 조경, 공공 좌석, 램프
**조명:** 침착, 품위 있음. 자연광 선호. 리테일 과밝기 금지
**인물:** 방문자, 학생, 가족, 관광객

### 교육 시설 (학교/대학교)
**특화 기하학:** fence position, gate design, classroom window rhythm, campus landscape boundary
**재료:** 노출 콘크리트, 벽돌, 알루미늄 커튼월, 루버 시스템
**대지:** 캠퍼스 잔디, 자전거 거치대, 한국 학교 철망 펜스
**조명:** 맑은 자연광 또는 흐린 날. 드라마틱 조명 금지
**인물:** 학생 그룹, 배낭, 자전거

### 의료 시설 (병원/클리닉)
**특화 기하학:** emergency entrance, accessible ramps, porte-cochere, helipad (대형)
**재료:** 알루미늄 커튼월, 도장 콘크리트 패널, 스테인리스 트림
**대지:** 구급차 동선, 장애인 주차, 명확한 출입구 표시
**조명:** 중립적 자연광. 따뜻한 황금시간대보다 냉정한 의료 환경감
**인물:** 환자, 보호자, 의료진, 구급차

---

## NEGATIVE 작성 순서 (15카테고리, 순서 엄수)

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

---

## 적용 예시

**입력:** 서울 오피스 타워 CGI — 35층, 다크 틴티드 유리 커튼월, 실버 알루미늄 멀리언, 베이지 화강석 포디움, 1층 리테일, 밝은 낮 시간

> **※ 아래는 SD/디퓨전 경로 예시(NEGATIVE 포함). GPT image 경로에서는 NEGATIVE를 빼고 PROMPT만 쓰며, 모든 부정문 잠금을 긍정형으로 바꾼다 — 위 "구도 보존 최우선 원칙" 4 참조. 예시 NEGATIVE는 15카테고리 템플릿의 축약형이다 — 실제 출력에서는 A~O 순서의 전체 템플릿을 기준으로 하되 중복 토큰은 제거한다.**

```
PROMPT
Use the input image as an immutable camera, composition, color, and architectural reference. Convert the existing CGI office tower rendering into a highly realistic real-world architectural photograph of a contemporary 35-story office tower in Seoul's modern urban business district. Replace all synthetic rendering artifacts, visualization materials, and archviz shortcuts with physically plausible real-world construction materials and authentic site conditions. ABSOLUTE CAMERA LOCK: preserve exactly the original camera position, camera height, camera tilt, camera yaw, lens perspective, focal length feel, framing, crop, horizon line, vertical alignment, foreground/background relationship, viewing angle, and overall composition. The camera must not shift in any way. No angle change, no viewpoint change, no orbit, no zoom change, no reframing, no recropping, and no perspective reinterpretation. ABSOLUTE GEOMETRY LOCK: preserve exactly the original building form and site composition with zero design change. Strictly preserve the exact 35-floor massing, proportions, facade rhythm, curtain wall system, mullion spacing, podium proportions, storefront layout, roofline, slab edges, entrances, setbacks, glazing divisions, structural grid, and spatial hierarchy exactly as shown in the input image. Do not move, scale, rotate, redesign, delete, extend, simplify, reinterpret, or deform any architectural element. Preserve exactly the original building color palette without any change, reinterpretation, or color shift. dark-tinted low-e glazing — tower curtain wall facade, silver — aluminum mullion system, beige granite — podium cladding, clear glazing — ground-floor retail storefronts, dark gray — roofline parapet, light gray — concrete sidewalk and plaza. The dark-tinted tower glazing should read as real architectural glass with subtle reflectivity, layered environmental reflections, realistic interior visibility variation, mullion shadowing, edge reflections, dust accumulation, and slight optical imperfections — avoid perfectly black glass or mirror-like rendering reflections. Silver aluminum mullions should exhibit realistic metallic behavior with subtle fabrication irregularities, reflectance variation, anodized finish depth, joint tolerances, and sealant detailing. The beige granite podium should appear as authentic installed natural stone with geological grain variation, panel joints, edge wear, accumulated urban dust, slight staining near pedestrian zones, and realistic seam tolerances. Ground-floor retail storefront glazing should feel physically built with realistic interior lighting, shallow depth, and believable occupancy. Realistic asphalt texture, subtle tire wear, drainage slopes, utility covers, patch repairs, curb staining, expansion joints, maintenance traces, road paint wear, and slight urban grime accumulation. No perfect rendering surfaces. Botanically believable Korean urban planting with varied tree species, asymmetrical canopies, authentic pruning patterns, leaf translucency, seasonal realism, and irregular branch structure. Avoid procedural landscaping or rendering-library trees. Realistic contemporary Korean vehicles with physically accurate paint reflections, glazing, tire detail, and natural traffic positioning. Candid Korean pedestrians in business attire with natural posture, proper scale, authentic movement, realistic skin texture, and documentary-style behavior. Lighting should behave like real architectural photography captured on a bright slightly humid Seoul daytime. Use physically grounded daylight with balanced exposure, realistic atmospheric softness, natural shadow transitions, subtle haze depth, realistic sky reflection behavior, restrained highlights, accurate white balance, realistic shadow density, and fine photographic sensor grain. Eliminate all CGI global illumination look, fake HDR, excessive contrast, bloom, artificial glow, and oversaturated rendering colors. The final image should feel like a high-end professional architectural photograph — realistic, grounded, urban, observational, and physically believable rather than stylized or cinematic. The result must look like a newly completed real building photographed on-site in Seoul, not an enhanced render.

NEGATIVE
changed camera angle, changed viewpoint, changed camera position, changed camera height, changed tilt, changed yaw, changed framing, changed crop, changed horizon, changed perspective, changed lens feel, orbit camera, zoom change, reframed composition, recropped image, tilted architecture, altered composition, changed building shape, changed massing, changed facade design, changed silhouette, changed proportions, changed floor count, changed roofline, changed curtain wall pattern, changed mullion spacing, changed podium design, changed storefront layout, altered slab edges, altered structural grid, altered proportions, modified architecture, simplified geometry, missing architectural details, added random buildings, fantasy architecture, warped facade, changed color palette, recolored facade, changed material colors, altered facade colors, color reinterpretation, changed accent color, changed glazing tint, color shift, material redesign, redesigned architecture, distorted geometry, deformed building, deleted architectural elements, wrong scale, oversized people, tiny people, CGI, archviz look, render look, SketchUp look, Rhino viewport look, Revit model look, clay render look, Lumion look, Enscape look, D5 render look, Twinmotion look, V-Ray render look, Corona render look, Unreal render look, Blender render look, game-engine look, AI-generated aesthetic, showroom rendering, polished visualization, synthetic environment, fake realism, concept art, illustration, cartoon, anime style, plastic materials, fake reflections, muddy textures, flat painted surfaces, repeated texture, over-clean materials, perfect surfaces, procedural stone texture, texture stretching, mirror glass, flat glass, black mirror glass, black void windows, empty glazing, textureless glazing, impossible reflections, glowing windows, repeated trees, cloned trees, procedural vegetation, rendering-library trees, identical canopies, synthetic grass, fake planting, fake people, mannequin humans, CGI humans, duplicated pedestrians, floating people, distorted anatomy, deformed faces, unrealistic skin, fashion-model posing, oversized people, tiny people, fake cars, toy-like cars, unrealistic road texture, clean showroom streets, perfect paving, spotless sidewalks, no urban wear, extreme HDR, bloom, glowing edges, artificial ambient occlusion, overexposed highlights, crushed shadows, excessive sharpness, halo artifacts, cinematic teal-orange grading, dramatic sci-fi atmosphere, neon reflections, heavy fog, volumetric effects, blurry materials, noisy image, low-detail facade, watercolor texture, surrealism, random text, readable fake signage, logo, watermark, graphic overlay
```

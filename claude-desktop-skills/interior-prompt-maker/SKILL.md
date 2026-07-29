---
name: interior-prompt-maker
description: "실내 CGI·렌더를 Magnific, Gemini/Nano Banana, SD·ComfyUI image-to-image용 사실적 사진 프롬프트로 변환한다. 이미지 1장 실사화와 2장 구조보존 리모델링을 구분하고, 한국 전시부스의 목공·블럭·옥타늄·맥시마 시공을 구조 증거로 구역별 판별한다. 사용자가 실내 이미지와 함께 '프롬프트 만들어줘', '실사화해줘', '실사화 스킬', '리모델링 프롬프트', 'i2i 프롬프트', '사진처럼', 'CGI 느낌 제거'라고 하면 사용한다. 프롬프트·스킬 요청은 이미지 생성 권한이 아니며 사용자가 생성·제작을 명시한 경우에만 생성 도구를 호출한다. 엔진 미지정 시 Magnific / Gemini / SD·ComfyUI 중 하나를 확인하고 엔진별 출력을 섞지 않는다. 건물 외관은 arch-prompt-maker, 재질 추출은 texture-prompt-maker, 조명만 이식할 때는 cinematic-exhibition-lighting, 사람 별도 합성은 person-layer-maker를 사용한다."
---

# 인테리어 Image-to-Image 프롬프트 메이커

인테리어 CGI/렌더/모델 이미지를 실제 건축 인테리어 사진과 구분 불가능한 수준의 프롬프트로 변환한다.

## 핵심 원칙

**임무 = CGI 표면 퀄리티 → 사진 퀄리티 변환. 색상·재료·공간 재설계가 아니다.**

**프롬프트 요청 = 프롬프트 텍스트만 출력.** 매 사용자 턴마다 산출물 의도를 새로 판정한다. 해당 턴이 `프롬프트 만들어`, `프롬프트 줘`, `프롬프트 작성`, `prompt for an image`, `실사화 스킬`처럼 프롬프트 텍스트 작성만 요구하고 `이미지 생성해`, `이미지 만들어`, `렌더링해`, `그려줘`, `generate an image` 같은 명시적 시각 결과물 지시를 포함하지 않으면 PROMPT_ONLY다. 한 턴에 프롬프트 작성과 명시적 이미지 생성 지시가 모두 있으면 이미지 생성이 허용된 복합 요청으로 처리하고 사용한 프롬프트도 함께 제공한다. `만들어줘`, `보여줘`, `적용해줘`처럼 산출물 종류가 모호하면 이미지 도구를 호출하지 않고 텍스트 프롬프트와 이미지 생성 중 무엇인지 확인한다. PROMPT_ONLY에서는 생성·편집·렌더링·마스킹·생성용 업로드·크레딧 소비 도구를 호출하지 않는다.

**규칙 우선순위:** ① 도구 권한·PROMPT_ONLY ② 사용자가 선언한 실제 시공 사실과 구조 원본의 카메라·형상·배치 ③ 구역별 시공 분류 ④ 유형별 재료·디테일 규칙 ⑤ 레퍼런스에서 추출한 일반 시공감. 같은 단계에서 충돌하면 원본에서 보이는 상태를 보존하고 불명확한 디테일을 추가하지 않는다.

## ★ 구도 보존 최우선 원칙 (실패 1순위 방지)

i2i 변환의 가장 흔한 실패 = **구도(화각·줌·시점·종횡비) 틀어짐**. 근본 원인은 문구가 아니라 **종횡비 불일치**다 — 16:9 원본을 모델이 다른 비율로 강제하면, 모자란 부분을 "프레임 밖 공간을 발명"해 채우며 줌아웃·측벽 추가가 생긴다. 따라서 문구보다 1·2가 먼저다.

1. **★ 실행 전 원본을 출력 합법 비율로 사전 크롭 (진짜 해결책)** — 모델이 엣지에서 방을 발명할 여지를 구조적으로 없앤다. 엔진의 출력 비율 제약을 먼저 확인한다: **gpt-image-1 계열은 1:1 / 3:2 / 2:3 고정**이므로 원본 16:9를 미리 3:2(가로형)로 크롭해 넣고, **gpt-image-2는 제약 내 임의 해상도를 지원**하므로 원본 비율을 그대로 유지한다(불필요한 크롭 금지). 크롭으로 잘리는 면적이 15%를 넘으면 중요 요소 절단 위험을 사용자에게 경고 후 진행한다(이 경고는 출력 비율 맞춤 크롭에만 적용 — 영역 추출 목적의 의도적 크롭은 대상 아님). "넓히지 마"(강제 불가)를 "넓힐 여지 없음"(구조 보장)으로 바꾸는 유일한 단계다.
2. **종횡비 원본 일치** — 사전 크롭한 비율과 출력 비율을 동일하게 둔다.
3. **절대 초점거리 숫자 금지** — 프롬프트에 `24mm`·`35mm` 등 숫자 초점거리를 절대 쓰지 않는다. 모델이 원본 화각을 무시하고 그 렌즈로 재해석해 광각화·줌아웃을 일으킨다. 오직 "원본과 동일한 화각·시점·프레이밍" **긍정형** 상대 표현만 쓴다.
4. **부정문("do not widen / zoom out") 금지** — 의미기반 모델에선 "분홍 코끼리" 효과로 오히려 그 변형을 유발한다. 항상 "원본과 동일하게 / 프레임 점유율 동일 / 네 모서리 정렬 / 소실점 동일 위치" 같은 **긍정 대응**으로 쓴다.
5. **GPT image 경로에서는 NEGATIVE를 넣지 않는다** — gpt-image는 부정 단락을 장면 묘사로 읽어 억제어를 오히려 그린다. PROMPT(긍정형)만 사용한다. NEGATIVE는 SD/MJ/ComfyUI 디퓨전 경로에서만 쓴다.
6. **엔진 선택 규칙** — 사용자가 엔진을 지정하지 않으면 추측해 SD 기본값을 고르지 말고 **Magnific / Gemini·Nano Banana / SD·ComfyUI 중 하나를 확인**한다. 서로 다른 엔진의 PROMPT·NEGATIVE를 한 답변에 섞지 않는다. 구도 픽셀 보존이 최우선이면 **GPT 엔진을 쓰지 않는다.** ControlNet(depth+lineart) 기반 SD i2i 또는 Magnific를 쓴다. Magnific는 두 모드를 분리한다: 원본과 이미 완성된 조명을 거의 그대로 키우는 **보존 업스케일**은 Creativity 0.1~0.3 / Resemblance 0.85~1.0에서 시작하고, CGI 표면을 실제 재질·빛 반응으로 바꾸는 **실사화(Materialization)** 는 Creativity 0.50 / Resemblance 0.55에서 시작한다. 실사화 샘플에서 ZONE B 변화가 약할 때만 Creativity를 0.05씩 올려 최대 0.60까지 시험하며, 그래픽·구조가 흔들리면 전체 프레임 값을 더 올리지 않고 ZONE B 크롭/마스크 경로로 전환한다. **FLUX 파이프라인이면 FLUX-native 컨트롤 모델(FLUX.1 Depth-dev 또는 Canny-dev 중 택일, 동시 사용은 ComfyUI 스태킹으로 별도 검증)** 을 쓴다 — SD/SDXL 계열 ControlNet·LoRA는 구조가 달라 **로드 자체가 불가**하니 FLUX 전용으로 교체. 주의: dev 계열은 비상업 라이선스(상업 프로젝트는 라이선스 확인), BFL API 신규 통합에서는 deprecated 표시(로컬 ComfyUI open-weight 경로는 사용 가능, 2026-07 기준).
7. **이중 검증** — (A) 결과 위에 원본을 50% 투명도로 겹쳐 수평선·소실점·네 모서리·그래픽·직선 프레임·카펫 외곽이 일치하는지 확인한다. (B) 벽·천장·바닥·금속·유리·조명·접촉 그림자는 실제 사진의 표면 반응과 빛 감쇠로 분명히 바뀌었는지 확인한다. A가 틀리거나 B가 원본 렌더와 거의 같으면 모두 실패다.

## ★ 재질·시공 사실 잠금 (단일 실사화의 최상위 규칙)

**실사화는 원본에 보이는 재질을 더 현실적으로 읽히게 할 뿐, 재질의 종류·무늬·마감 등급·시공 방식을 새로 설계하거나 강화하는 작업이 아니다.** 이 잠금은 **단일 실사화 모드의 최상위 규칙**이다. 리모델링 모드에서는 사용자가 명시한 Image 2 기반 재질 교체 범위만 예외이며, 카메라·건축 구조·대상 경계·비지정 요소는 계속 잠근다.

1. **재질 원본성:** 목재결의 방향·대비·반복·절·색 농도, 석재 맥·타일 패턴·줄눈, 금속 광택, 벽체의 미세 텍스처, 바닥 반사 강도는 원본에서 보이는 수준과 분포를 유지한다. 매끈하거나 약한 무늬목을 진한 월넛·러프 쏜우드·강한 절무늬로 재해석하지 않는다.
2. **제조·시공 사실:** 원본에 실제로 보이지 않는 아일렛/타공/펀칭 홀, 피스·볼트·리벳, 봉제선, 프레임, 몰딩, 패널 줄눈, 고정 브래킷, 케이블, 장식, 소품은 추가하지 않는다. 원본에 없는 결함·마모·먼지·지문·주름·스크래치도 "현실감"을 이유로 발명하지 않는다.
3. **현수막·그래픽면:** 원본에서 구멍이나 고정 하드웨어가 확인되지 않으면, 현수막은 **연속된 불투명 PVC 플렉스 그래픽면**으로 유지한다. 원본 그래픽·텍스트·로고는 픽셀 아트워크를 최상단 오버레이로 복원하며, AI가 새 글자·구멍·봉제선·주름·접힘·광택 패턴을 만들게 두지 않는다.
4. **원본 우선:** "ultra detail", "authentic grain", "construction tolerances", "imperfections", "realistic accessories" 같은 일반 묘사는 원본에서 확인되는 대상에만 제한적으로 쓴다. 확신할 수 없으면 해당 디테일을 추가하지 않는다.

**가구·인물 권한:** 가구 교체는 사용자가 명시적으로 요청한 리모델링 모드에서만 허용한다. 인물 추가는 사용자가 명시적으로 요청했을 때 `person-layer-maker`의 별도 레이어 절차로 처리하며, 이 실사화 프롬프트가 임의로 사람을 굽지 않는다.

## ★ 2영역 실사화 균형 (보존이 실사화를 죽이지 않게)

전시·행사 이미지에는 반드시 영역을 두 가지로 나누어 프롬프트를 작성한다. **전체 이미지를 픽셀 고정하지 않는다.**

- **ZONE A — 픽셀 고정:** 카메라·구도·건축 형상·객체 위치·그래픽 판넬 경계·텍스트·로고·아트워크·직선 프레임·카펫 외곽. 생성 모델이 ZONE A를 정확히 복원한다고 약속하지 않는다. 최종 상업 납품본에서는 원본 아트워크/선형 구조 마스크를 후보 이미지 위에 최상단으로 복원한다.
- **ZONE B — 조건부 적극 실사화:** 입력에 실제 존재하는 벽·천장·바닥·금속·유리·기존 가구 표면, 기존 조명의 광학 반응, 반사 감쇠, 접촉 그림자, 간접광, 노출과 색 반응. 입력이 CGI/렌더이고 해당 표면에 합성 흔적이 보일 때만 적극 변환한다. 재료의 **종류·색·무늬 방향·무늬 강도·패널 구획은 유지**하되 균일한 CGI 셰이딩을 실제 촬영 표면 반응으로 바꾼다. 입력이 이미 실사이거나 해당 요소가 없으면 변화를 강제하지 않는다.

**균형 원칙:** `preserve material identity`는 `preserve CGI pixels`가 아니다. 원본보다 과장된 나뭇결·새 타공·새 하드웨어는 실패다. CGI 흔적이 확인된 ZONE B에서 조명·접지감·미세 거칠기·반사·표면 흡수가 그대로 남는 것도 실패다. 이미 실사인 입력은 보존 통과가 가능하다.

**마스크 소유권·합성 순서:** ① 원본에서 ZONE A 마스크를 만든다. ② ZONE A를 보호하거나 제외한 상태로 ZONE B 후보를 생성한다. ③ 원본 ZONE A를 후보 위 최상단에 100% 복원한다. ④ ZONE A 경계를 넘어 새 반사·그림자·광학 효과를 그리지 않는다. ⑤ 원본 50% 오버레이와 OCR/로고 육안 대조로 ZONE A를 확인한다. 마스크 합성이 불가능한 경로의 전체 이미지 생성 결과는 **재질·조명 후보**일 뿐, 텍스트·로고·그래픽이 있는 상업 최종본으로 승인하지 않는다.

**Gemini/Nano Banana용 2영역 핵심 문장(첫 보존 문장 뒤에 반드시 삽입, 긍정형만 사용):**
> `"Apply a strict two-zone transformation to the CGI characteristics visible in Image 1. ZONE A remains aligned one-to-one: the camera, geometry, object placement, graphic boundaries, typography, logos, source artwork, straight frame edges, carpet perimeter, and continuous opaque banner faces retain their exact source identity. ZONE B contains only the existing walls, ceiling, floor, metal, glass, furniture surfaces, lighting, reflections, indirect bounce, contact shadows and exposure response; actively convert their synthetic CGI shading into physically believable photographed material behavior. Preserve each material's identity, base color, grain direction, grain strength, pattern scale, visible seams, visible joints and construction method while expressing real-world micro-roughness, light absorption, highlight roll-off, reflection falloff and grounded shadows. Existing accessories and fabrication details remain exactly the observed set. The completed scene reads as an on-location architectural photograph while ZONE A stays registered to Image 1."`

**Magnific용 2영역 핵심 문장(전체 프레임 실사화의 시작 문장, 긍정형만 사용):**
> `"Materialize only the CGI-looking surfaces in Image 1 into a believable on-location architectural photograph. Keep the camera, room geometry, object placement, screen frames, straight edges, graphic boundaries, typography, logos and source artwork registered to the source. Actively re-render the existing ZONE B surfaces — walls, ceiling, floor, metal, glass, seating and stage surfaces — with physically specific material response: micro-roughness, fabric tension, light absorption, highlight roll-off, reflection falloff, localized indirect bounce and grounded contact shadows. Treat every active LED display as an emissive surface while retaining its source artwork: its existing screen colors cast controlled, localized light onto only the immediately adjacent source surfaces, with physically plausible falloff. The result must visibly change the synthetic shading in ZONE B; a mere sharpened or enlarged CGI render is insufficient."

## 빠른 흐름

0. **(구도 보존 중요 시) 사전 크롭**: 실행 전 원본을 출력 엔진의 합법 비율로 사전 크롭한다(위 원칙 1). 사용자에게 목표 비율·크롭 방향을 1~2줄로 안내하거나, 이미지 파일 접근이 가능하면 직접 크롭 후 진행한다.
1. **대상 엔진 판별**: 사용자가 명시하지 않으면 먼저 Magnific / Gemini·Nano Banana / SD·ComfyUI 중 실행 엔진을 묻는다. Magnific가 명시되면 Magnific 블록만, Gemini·Nano Banana가 명시되면 긍정형 Gemini 블록만, SD·ComfyUI가 명시되면 PROMPT+NEGATIVE만 만든다.
2. **모드 판단**: 이미지 1장 → 단일 모드 / 이미지 2장 → 리모델링 모드 (아래 "모드 판단"의 엣지케이스 규칙 참조)
3. **이미지 분석**: 공간 유형, 색상 팔레트, 주요 건축 요소 파악
4. **엔진별 실행 PROMPT 작성**: Magnific는 실사화(Materialization) 또는 보존 업스케일 중 하나를 선택해 설정값까지 작성한다. Gemini·Nano Banana는 긍정형 PROMPT만, SD·ComfyUI는 PROMPT+NEGATIVE를 작성한다.
5. **선택한 엔진 블록만 출력**: 사용자가 다른 엔진용 블록을 잘못 복사할 여지를 만들지 않는다.

카메라 브랜드 (Sony, Canon, Hasselblad 등) 절대 명시하지 않는다.
MJ 파라미터 (`--v`, `--iw`, `--ar` 등) 절대 포함하지 않는다.

## 출력 원칙

- **Magnific 지정 시** 정확히 두 섹션만 출력: `MAGNIFIC PROMPT`(연속 영어 단락)와 `MAGNIFIC SETTINGS`(Materialization 또는 Preservation, Creativity, Resemblance). NEGATIVE와 다른 엔진용 섹션을 절대 출력하지 않는다.
- **Gemini/Nano Banana 지정 시** `PROMPT` 한 섹션만 출력한다. NEGATIVE와 SD·ComfyUI·Magnific용 섹션을 절대 출력하지 않는다.
- **SD·ComfyUI 지정 시** `PROMPT`와 `NEGATIVE (SD/ComfyUI 전용)` 두 섹션을 출력한다. Midjourney는 별도 네거티브 필드를 공유하지 않으므로 SD·ComfyUI NEGATIVE를 Midjourney용으로 표기하거나 섞지 않는다.
- 설명, 분석, 주석 없음 — 단, 사전 크롭이 필요한 경우 PROMPT 출력 전에 크롭 안내(목표 비율·방향) 1~2줄은 허용
- PROMPT는 **하나의 연속된 영어 단락**
- NEGATIVE는 **하나의 연속된 영어 단락**

---

## 모드 판단

**이미지 1장 → 단일 모드:** 원본 공간을 실사 사진으로 변환
**이미지 2장 → 리모델링 모드:** 이미지1 카메라·건축 구조·비지정 요소 유지 + 사용자가 지정한 Image 2 스타일/재질 범위만 적용
**이미지 2장 + 부분 지정("소파만", "이 벽만", "콕 집어", "빨간 영역만") → 정밀 재료 교체(PICK) 모드** (아래 블록)

**리모델링 권한 분리:** 기본은 `재질/스타일 교체`이며 기존 가구의 형상·수량·위치는 유지한다. 사용자가 가구 교체까지 명시한 경우에만 `가구 교체 리모델링`으로 전환하고, 대상 가구·수량·점유 영역·동선 간섭 범위를 별도로 잠근다.

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

**리모델링 모드(기본: 가구 형상 유지):**
> `"Use Image 1 as the immutable architectural structure, room geometry, camera, composition, furniture geometry and spatial reference. Apply from Image 2 only the user-specified remodeling style, surface materials, lighting and atmosphere within the declared target areas."`

**가구 교체 리모델링(사용자가 명시한 경우만):**
> `"Use Image 1 as the immutable architecture, camera and circulation reference. Replace only the explicitly named furniture using Image 2, while preserving the declared furniture count, occupied footprint, clearances and circulation paths."`

**색상 적용 기준(리모델링 모드):** 구조·고정 요소(벽 골조, 천장 형태, 창호 프레임 등 Image 1의 건축 구조)의 색은 **Image 1을 보존**하고, 마감재·가구·스타일 요소의 색상은 **Image 2를 적용**한다. 아래 "컬러 팔레트 잠금"의 원본 색 보존 규칙은 **단일 모드에서는 이미지 전체에**, **리모델링 모드에서는 구조·고정 요소에만** 적용된다.

---

### 2. 전환 선언 + 공간 정체성

이미지 역할 선언 직후. 두 가지 중 선택:

**옵션 A — 전면 변환:**
> `"Transform the existing CGI surface and lighting response into a believable photographed built interior while retaining every observed material identity and architectural detail."`

**옵션 B — 요소별 보존 (권장):**
> `"Maintain the exact shape, placement, color, and material identity of the existing [천장/카운터/가구 등 핵심 요소], while actively replacing their CGI shading with physically believable photographed surface response, micro-roughness, highlight roll-off, reflection falloff, and grounded contact shadows."`

예: `"Maintain the existing curved reception desk configuration and suspended wood slat ceiling exactly as shown while actively re-rendering their existing materials with real photographed surface response and physically grounded lighting."`

---

### 3. 컬러 팔레트 잠금 ★ (재료 묘사 전 필수)

**가장 자주 실패하는 지점. 반드시 포함.**

먼저 선언 (단일 모드):
> `"Preserve exactly the original design color palette without any change, reinterpretation, or color shift. The task is to convert CGI surface quality to photographic realism only — do NOT redesign, recolor, or replace any material or color."`

**리모델링 모드 전용 잠금 문구 (위 문장 대신 사용):**
> `"Image 1 retains the complete architecture, fixed-element colors, camera, circulation and every non-target element. The declared target surfaces receive only the specified material palette from Image 2, expressed with photographed material behavior. Existing furniture geometry remains registered to Image 1 unless the user explicitly selected furniture-replacement remodeling."`

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
- `"Preserve the suspended linear wood ceiling baffles exactly as shown, retaining their observed wood species, color, grain direction and grain strength while expressing real photographed low-sheen response and existing recessed-light trim depth."`
- `"Preserve the U-shaped reception counter configuration exactly as shown, but render the front panels with realistic woven acoustic fabric tension, visible weave texture, and matte surface absorption."`

**패턴 B — 색상+재료 묘사형 (전체 공간 재질화):**
> `"The [색상] [재료명] features [현실적 물성]..."`

예:
- `"The warm natural oak veneer slatted panels feature subtle edge wear, realistic wood grain variation, and believable construction tolerances."`
- `"The blue upholstered chairs show detailed woven fabric texture, slight wrinkles, soft seat deformation, matte powder-coated metal legs, and naturally worn contact areas."`

**재료별 핵심 물성 키워드:** 아래 속성 중 **원본에서 확인되는 것만 선택**한다. `edge wear`, `scratches`, `seams`, `joints`, `mounting hardware`는 원본에 보일 때만 사용한다.

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

> `"Preserve only the construction details, seams, edge conditions, material thickness, shadow gaps, joints, trims, fixtures, accessories, and surface age that are visibly present in Image 1. Render those existing details with physically believable scale and light response. Do not invent construction hardware, mounting details, clutter, dust, fingerprints, wrinkles, wear, scratches, seams, or surface aging that Image 1 does not show."`

공공·업무 공간 추가(원본에 실제 보이는 항목만 선택):
> `"Preserve the institutional accessories already visible in Image 1 at their exact positions and scale, and integrate them with realistic contact shadows and material response. Add no new accessories."`

주거 공간 추가(원본에 실제 보이는 항목만 선택):
> `"Preserve only the residential objects already visible in Image 1 at their exact positions and scale, with realistic contact shadows and material response. Add no new lifestyle clutter."`

---

### 6. 가구 + 오브젝트 사실성

> `"Preserve the exact furniture and objects already visible in Image 1, with physically believable scale, grounded contact shadows, realistic upholstery tension and material response. Introduce no new furniture, props, clutter, people, cables, or decorations."`

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
> `"Where CGI characteristics are visible in the existing environment surfaces and lighting, transform them into a professionally photographed real built interior through physically grounded junctions, material-specific micro-roughness and absorption, natural highlight roll-off, distance-based reflection falloff, localized illumination pools, believable indirect bounce, realistic dynamic range and documentary architectural color science. If those identified CGI characteristics remain nearly identical, reject the result as insufficient photorealization."`

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

### 전시부스 / 전시장 (목공 · 블럭 · 옥타놈 · 맥시마 혼합 + 전시홀) ★

> **왜 별도 블록인가:** 전시부스는 규칙적인 알루미늄 직선 격자(포스트·빔·fascia)로 이뤄져 AI가 가장 잘 무너뜨리는 대상이다. 프레임을 "녹이거나" 벽을 매끈한 단일면으로 뭉개고, 간판 글자를 깨뜨린다. 아래 어휘·성공문장·엔진 규칙으로 이를 막는다. (검수 반영: NEGATIVE 증상토큰 배제·mm 숫자 배제·fascia 텍스트 생성 금지)
>
> **필수 분류 참조:** 전시부스가 한 구역이라도 보이면 프롬프트를 쓰기 전에 [`references/exhibition-booth-classification.md`](references/exhibition-booth-classification.md)를 **끝까지 읽고**, 그 문서의 판정 순서·공법별 표현 한계·그래픽/바닥 분리 게이트를 적용한다. 내부적으로 `zone_id | source_region | 부모 면 | 경계 근거 | Image 1 분류 증거 | 판정 | 허용 앵커 | 금지 앵커 | 확신도` 원장을 먼저 만든다. 사용자가 요구하지 않으면 원장은 출력하지 않고 최종 프롬프트에만 반영한다.
> **바미싱 현수막 필수 참조:** 사용자가 `바미싱`, `상하단 바미싱`, `프레임 안 보이는 현수막`, `프레임 없는 플렉스`를 선언하거나 구조 원본에서 그래픽면 둘레의 상·하·측면 프레임이 보이지 않으면 [`references/bar-missing-flex-banners.md`](references/bar-missing-flex-banners.md)를 끝까지 읽는다. 이 그래픽면은 옥타 인필·블럭 패널·목공벽이 아니라 독립 `bar-missing PVC flex banner face`로 처리하며, 같은 면에 옥타 포스트·레일·베이스레일·은색 외곽 프레임을 넣지 않는다.

**★★ 먼저 시공 유형을 판별 (한국 전시업계 실무 기준 — 외형과 시공 논리가 다르다):**
| 유형 | 골조·시공 | 외형 식별자 |
|---|---|---|
| **목공부스** (독립/맞춤) | 각재+합판+퍼티+도장/시트 | **이음매 없는 매끈한 벽면(seamless), 날카롭고 깔끔한 모서리, 프레임 안 보임** |
| **블럭부스** (렌탈 모듈) | 규격 블럭·탈착 패널 반복 조립 | **원본의 벽 또는 카운터에 실제 패널 두께와 좁지만 명확히 보이는 반복 조인트가 이어지는 구조**. 캐노피·곡면·체결점은 원본에 있을 때 분류를 보강할 뿐 필수 조건이 아님 |
| **옥타놈/옥타늄** (기본/시스템) | 알루미늄 폴+바+패널 | **은색 알루미늄 프레임 격자가 노출, 그 사이 백색 인필 패널** |
| **맥시마** (시스템 압출 골조) | 40/80/120 계열을 포함하는 알루미늄 압출 골격 | **개구부·포털·파시아·상부를 잇는 구조 스팬과 관찰 가능한 압출 접합**. 노출·패널 피복·패브릭 피복은 원본에 보이는 상태만 유지하며, 부재 굵기·색·발광만으로 판정하지 않음 |
| **바미싱 플렉스 현수막** (그래픽면) | 상·하단 장력 방식이 숨겨진 연속 PVC 플렉스 면 | **그래픽면의 상·하·측면에 바·레일·외곽 프레임이 보이지 않는 넓고 평평한 현수막 면**. 보이는 세로 맥시마 빔은 별도 골격 구역으로만 판정 |
> **분류 권한:** 사용자가 실제 시공 유형을 선언하면 원본 CGI의 애매한 표현보다 그 시공 사실을 최우선으로 사용한다. 사용자 선언은 해당 선언이 가리키는 구역에만 적용하며, 원본 CGI와 외형이 달라도 선언을 임의로 강등하지 않는다. 같은 구역에 서로 충돌하는 사용자 선언이 둘 이상 있으면 그 구역만 확인 전까지 `construction=undetermined`로 둔다. 사용자 선언이 없을 때만 구조 원본에서 판정하고 레퍼런스 이미지로 유형을 결정하지 않는다.
> **구역별 판정:** 실제 부스가 혼합이면 전체를 하나로 덮지 않고 `주벽`, `상부/캐노피`, `카운터·독립 가구`, `전면 강조빔`, `측·후면 골조`를 각각 판정해 해당 영역에만 시공 문구를 적용한다.
> **혼합의 정의:** `혼합`은 별도의 다섯 번째 재료가 아니라 서로 다른 구역이 서로 다른 공법으로 확정된 상태다. 같은 구역에 옥타·맥시마·블럭 표현을 섞지 않는다. 맥시마 전면 포털 + 옥타늄 측·후면처럼 각 구역을 따로 명명한다.
> **불명확 폴백:** 가림·저해상도·상충 증거로 판정이 불충분한 영역은 `construction=undetermined`로 두고 보이는 구조만 보존한다. 블럭·옥타늄·목공에 해당하지 않는 텐션패브릭·트러스·맞춤 철제 등은 `construction=other`로 두고 유형 문구를 강제하지 않는다. 이 영역에 새 조인트·체결점·프레임 격자·캐노피 하부·지지대·내부조명을 추가하지 않는다.
> **레퍼런스 격리:** 공법 판정이 확정되기 전에는 레퍼런스에서 어떤 시공 속성도 가져오지 않는다. `classification_evidence`에는 구조 원본 Image 1의 위치와 관찰만 기록한다. 공법이 확정된 뒤에만 **같은 공법의** 레퍼런스에서 패널 두께감, 조인트 성격, 일반 체결 방식, 표면 마감 범주(`matte / low-sheen / semi-gloss / gloss`)와 일반 재료 범주, 일반 조명 장착 방식을 `reference_finish_notes`로 별도 기록할 수 있다. 이 값은 원본에서 확인된 구조 범위 안의 사실감을 보정할 뿐 패널 치수·조인트 수·폭·깊이·반복·프레임 단면·배치를 새로 만들거나 공법 판정을 바꾸지 않는다. 레퍼런스의 특정 색·팔레트·브랜드 그래픽·평면·입면 구성·모듈 수·배치·곡선 위치·곡률·캐노피·카운터·진열대 형상·개구부·가구·사인·아트워크·조명 위치·수량·카메라를 원본에 복제하거나 변형 적용하지 않는다.
> ★블럭부스 = "규격 모듈 조립"이 핵심 정의다. 내부 LED 발광은 일부 고급형의 옵션일 뿐 정의가 아니다 — 비발광 블럭부스가 오히려 다수다. 발광을 식별자로 강제하면 벽 전체가 라이트박스처럼 전면발광하는 실패가 난다(3중 검수 만장일치 BLOCKER).

**★ 옥타놈 성공 문장 (옥타놈으로 확정된 구역에만 한 문장으로 고정 삽입):**
> `"Each source-confirmed Octanorm zone must read as a modular shell-scheme system: every visible wall bay in that zone retains its slim anodized aluminum vertical uprights standing proud of the separate infill panels, its horizontal rails and its source-visible base rails."`

**모드 A — 옥타놈 / 시스템 기본부스 (프레임 노출 격자형):**
- 구조: `Octanorm-style modular exhibition shell scheme, slim silver anodized aluminum post-and-beam frame, narrow vertical posts proud of the flat white infill panels, crisp specular highlights along the post edges, standard 3x3m booth, eye-level wall height`
- 재료: `flat matte white melamine or PVC foam infill panels, non-reflective panel surface`; 그래픽은 원본에 있을 때만 `printed graphic panel inserts`
- 사인: `fascia header band above the booth, kept as a blank or simple placeholder signage area without legible text` (실제 상호는 후처리 합성 — 글자 생성은 깨짐 유발)
- 조명/바닥: `clip-on spotlight arms mounted on the fascia, track spotlights washing the panels, physically mounted fixtures, grey needle-punch exhibition carpet, brushed aluminum base rails seating the booth on the floor`

**모드 A2 — 맥시마 또는 맥시마/옥타늄 혼합부스 (사용자가 맥시마 시공을 선언하거나 원본에서 개구부·파시아를 잇는 압출 골격과 접합 증거가 보일 때):**
- 맥시마 구조 앵커: `the target-visible zone retains its source-confirmed Maxima extrusion structure at the exact source openings, fascia or portal, preserving only the observed exposed, panel-clad, or fabric-clad condition and the observed beam depth, spacing and joints`
- 옥타늄 혼합이 함께 확정된 경우에만: `a neutral matte-silver Octanorm base shell with thicker Maxima box-section beams only at the exact front-facade positions already visible in target Image 1`
- 기존 파란 맥시마 빔: target Image 1에서 실제 발광할 때만 `the target-visible blue Maxima members retain their exact geometry and read as internally illuminated architectural blue channel members matching Image 1, with a controlled electric-blue core and short-range diffuse spill limited to the immediately adjoining banner edge, upright edge and floor directly below`
- 나머지 골조: target Image 1 또는 사용자의 실제 시공 선언이 해당 측·후면 구역을 옥타늄으로 확인할 때만 기본값 `side and rear Octanorm posts, rails and base members remain neutral silver, matte and non-emissive`를 적용한다. 다른 구조이거나 불명확하면 이 문구를 적용하지 않고 원본에서 보이는 상태를 보존한다. 사용자가 해당 구역의 발광 시공을 별도로 선언한 경우에만 그 구역을 독립적으로 예외 처리한다.
- 그래픽: 백색 또는 컬러 인쇄면은 원본 시공 선언에 따라 `continuous opaque tensioned PVC flex banner graphic with subtle tarpaulin microtexture and exact source artwork preserved`
- ★대조 앵커: `"…a physically assembled hybrid exhibition system with facade-only Maxima treatment, not an all-blue glowing frame and not a seamless built wall."`

**모드 B — 목공 독립부스 (매끈한 면 볼륨형):**
- 구조: `custom-built exhibition booth with smooth continuous plastered and painted wall surfaces, sharp clean flush corners, solid built walls`
- 재료/디테일: `matte painted walls or adhesive vinyl-wrapped walls, laminate finish, branded feature walls`; 로고 사인은 원본에 있을 때만 `edge-lit acrylic logo` (한 면에만)
- ★대조 앵커(한 문장 삽입): `"…a solid custom-built wall, not a modular framed system and not an exposed aluminum grid."`

**모드 C — 블럭부스 / 규격 블럭·탈착 패널 조립 (modular block-panel assembly):**
- **범위 게이트:** 아래 문구는 사용자 선언 또는 구조 원본 Image 1의 시각 판정으로 `construction=block`이 확정된 구역에만 적용한다. 목공·옥타늄·맥시마·기타·불명확 구역에는 블럭 조인트·패널 두께·체결점·곡면 세그먼트·캐노피·내부발광 문구를 적용하지 않는다.
- **레퍼런스 사용법:** 실제 블럭부스 사진은 디자인 복제본이 아니다. 원본 렌더의 카메라·형상·높이·개구부·색·곡면 유무·캐노피 유무·가구·브랜드를 유지하고, 사진에서는 패널 두께감·반복 조인트·일반 체결 방식·표면 반사·일반 조명 장착 방식만 추출한다.
- **식별:** 원본에 실제 패널 두께와 좁지만 카메라 거리에서 명확히 읽히는 반복 함몰 조인트가 이어지고, 연속 노출 옥타늄 포스트-인필 격자가 없을 때 블럭 영역으로 판정한다. 벽·캐노피·기둥·카운터는 서로 독립 판정하며 원본이 같은 시스템임을 보여줄 때만 같은 모듈 언어를 공유한다. 공식 모듈 수치는 판별 참고일 뿐 프롬프트에 절대·상대·비교 수치로 넣지 않고 원본에서 보이는 패널 비례와 조인트 간격만 보존한다.
- 기본 구조 문장: `a reusable modular block-panel exhibition construction assembled from standardized rigid modules, preserving the target source silhouette, openings, proportions, visible panel-size pattern, narrow but clearly visible recessed joints and target-visible panel thickness`
- 직선 영역에만 조건부 추가: `rectangular panel modules aligned consistently along the source-visible straight runs`
- 곡면 영역에만 조건부 추가: 원본에서 곡면과 세그먼트 경계가 모두 보일 때 `discrete curved-profile modules following the target's apparent curved contour, arc span and only the visibly observable segment seams`; 매끈하거나 가려진 곡면에는 새 세그먼트 선을 추가하지 않는다.
- 체결점 조건부 추가: 원본 해상도에서 독립 하드웨어로 식별되는 체결점의 **보이는 종류·수량·대략적 위치만** 묘사한다. 관찰된 단일 체결점 하나를 근거로 보이지 않는 위치까지 전체 부스에 외삽하지 않는다. 체결점이 없거나 불확실하면 관련 문구를 생략한다.
- 캐노피 조건부 추가: 원본에 상부 캐노피·포털이 있을 때 원본과 같은 카메라에서 보이는 외곽·측면·하부 범위만 보존한다. 하부 조인트, 등기구, 브래킷, 현수부, 기둥, 벽체 캔틸레버는 각각 실제로 보이는 항목만 그 수량·위치에 맞춰 별도로 추가하며, 원본에서 가려진 하부·지지 구조는 계속 가려진 상태로 유지한다.
- 표면: `rigid removable composite or laminate-skinned panel faces with source-matched low-sheen or semi-gloss response, crisp color-film or printed-graphic application, visible shallow edge reveals and no plaster-like continuity`
- 카운터·진열대가 같은 시스템일 때만: `the source-visible counters and display plinths repeat the same observed modular panel-size pattern, recessed-joint cadence, thickness and finish language at their exact source positions`
- 발광은 옵션(독립 게이트): 그래픽의 밝은 색·반사·홀 조명 핫스폿만으로 내부발광을 추정하지 않는다. 같은 주변광 아래 인접 불투명 패널보다 뚜렷한 자체 휘도 차이를 보이는 백라이트 그래픽, 경계가 분명한 발광 패널 면 또는 내부 광원이 원본에서 확인될 때만 `the observed panel bay is the sole self-luminous surface in that module; its illumination falls off rapidly as a faint soft reflection on only the immediately adjacent panel edges and floor, while neighboring modules remain opaque and non-self-luminous`
- 원본에 발광 근거가 없거나 해상도가 불충분하면 모든 블럭은 `opaque, non-emissive, lit only by the observed hall and source-visible booth fixtures`
- ★대조 앵커: `"Only the source-confirmed block zones read as reusable modular block-panel construction with clearly visible repeated recessed joints and real panel thickness; do not reinterpret those same block-zone surfaces as seamless carpentry, a slim exposed Octanorm post-and-infill grid, or an open Maxima box-beam frame."`

**★ 그래픽·마감 실재료 서브블록 (★원본에 실제 보이는 재료 1~2종만 골라 주입 — 6종 나열 금지(material soup). 없는 텍스트/로고 생성 금지):**
- 현수막(플렉스): `continuous opaque PVC flex banner graphic, exact original artwork preserved, only the original level of surface flatness and sheen, no added holes, grommets, screws, rivets, stitching, folds, or wrinkles`
- 바미싱 플렉스 현수막(사용자 선언 또는 원본 확인 시): `a continuous full-bleed opaque PVC flex banner face held by a concealed top-and-bottom bar-missing tension system, with no visible top bar, bottom bar, side rail, silver perimeter frame, exposed post, base rail, panel joint or border around the graphic face; exact original artwork preserved`
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

**★ 행사형 전시홀 서브블록 (2026-07-13 신규 · 3중검수 반영 — 적용 조건: 부스존/무대·중앙 설치물/관객석/휴게존 중 **2개 이상의 존이 한 프레임에 뚜렷이 구분되어 공존**하는 와이드샷일 때만. 부스 안에 의자 몇 개 보이는 수준엔 적용 금지):**
> 성격이 다른 존을 뭉뚱그리면 모델이 공간 위계를 재배치한다. 대응: **1단계 첫 문장의 보존 나열에 존을 열거**한다 — 단일 모드는 보존 나열에, 리모델링 모드는 `Use Image 1 as the immutable ...` 목록 안에 삽입: `booth positions, central [stage / media volume / feature installation — 원본에 실제 있는 것] geometry, carpet zone boundary, seating rows, circulation`. **컬러 팔레트 잠금(3단계)도 존별로 끊어** 명시한다.
> ⚠ 한계 명시: 존 경계 토큰은 **약한 바이어스**일 뿐 공간 락이 아니다 — 실제 영역 유지는 i2i의 낮은 denoise/높은 structure strength(또는 ControlNet)가 담당한다. 높은 denoise에서는 토큰이 있어도 존이 번질 수 있다.
- 휴게존 인조잔디 카펫(★원본에서 인조잔디로 확인될 때만, 색도 원본 채도 그대로): `[원본 색] artificial turf carpet with realistic fiber pile texture, directional sheen, seam tape lines[, slight flattening along walking paths — 원본에 통행 자국이 보일 때만]` + 강채도 녹색이면 바운스 게이팅 1줄: `saturated green confined to the turf zone, only a subtle green bounce on immediately adjacent surfaces, neutral white balance across the rest of the hall` (발광 게이팅과 동일 원리 — 대면적 강채도는 diffuse bounce로 홀 전체를 물들인다).
- 행사 관객석(★원본의 의자 유형·재질 그대로 — 플라스틱으로 단정 금지): `audience seating matching the original chair type, material and arrangement, identical chairs repeated in rows but each with slightly different scuff marks and a few degrees of rotation variation` — per-instance 미세 변주가 복제 어셋 티를 막는 **긍정형 1차 수단**(관객석은 동일 제품 반복이 정답이므로 형태·색 변주를 유발하는 표현 금지). SD 경로 NEGATIVE의 `cloned objects`는 보조.
- 무대/백드롭: 백드롭 그래픽은 fascia 텍스트 금지 원칙과 동일 — `the backdrop graphic kept as the same overall composition and colors, with no new legible text`.
- 착석 인물이 원본에 있으면 인물·현장 서브블록(위) 규칙 그대로(원경 실루엣 유지·텍스트 소품 금지), 없으면 person-layer-maker로.

**★ LED 미디어아트 발광 볼륨 서브블록 (적용 조건: 원본에 **입체 미디어 볼륨**(깊이·측면이 보이는 독립 구조물)이 있을 때만 — 평면 LED월·프로젝션 스크린·플러시 그래픽 패널에는 구조 문구를 적용하지 않는다(없는 입체 매스 발명 유발)):**
- 구조(★재료·색은 원본 확인 후 기입): `a vertical slatted structural volume matching the original material, color and geometry, carrying a large-format fine-pitch LED media surface` — 프레임 격자는 부스 격자와 동일하게 구조 보존 대상.
- 발광 게이팅(핵심): `only the media surface is emissive, emitting [원본 콘텐츠 색] light streaks with believable local bloom and slightly blown highlights at the brightest streaks, the fine LED pitch reading as a soft continuous glow with individual pixels blurred by lens diffraction, screen light spilling only onto surfaces immediately adjacent to the volume, which receive the colored light but are themselves matte and non-emissive, neutral white balance across the rest of the hall` — 발광은 미디어 표면 1개에만(발광 단일화 규칙의 적용례), 스필은 인접면 한정, **선명한 픽셀 격자·모아레를 그리지 않게 soft glow로 명시**(실촬영에서 격자는 회절·블룸으로 뭉개진다).
- 스필 ↔ 팔레트 잠금 충돌 방지(3단계에 예외 1줄 추가): `colored illumination from the media surface may tint the light and shadows on nearby surfaces without replacing or recoloring their underlying materials.`
- 미디어 콘텐츠는 **gestalt만 약속**: 3단계 팔레트 잠금에 콘텐츠 색을 명시(`[콘텐츠 색] — glowing media-art light streaks on the media surface only`)하고 `preserving the overall streak layout and color family of the source content` — 정확한 스트릭 형태는 i2i가 재렌더한다(허용). "동일 구성 복제"를 약속하는 표현은 쓰지 않는다.
- 광택 바닥이 원본에 있으면: `soft reflection of the media surface on the polished floor` 1줄(반사는 2차 발광이 아니므로 단일화 규칙과 충돌 없음).
- 조명(7단계)과의 정합: 혼합 조명 문구에 `colored screen light from the media volume` 1회만 언급 — 발광 토큰 중복 금지.

**★ 평면 LED월 + 무대 데크 발광 서브블록 (적용 조건: 원본에 켜진 평면 LED월과 바로 앞 무대 데크가 함께 보일 때만):**
> 평면 LED월은 미디어아트 발광 볼륨이 아니다. 입체 매스·측면 구조를 발명하지 않으며, 그래픽·텍스트·로고는 최종 합성에서 원본 아트워크로 복원한다. Magnific에서는 이 블록을 생략하면 LED를 단순한 인쇄 그래픽으로 보존해 무대 반사와 스필이 빠질 수 있다.
- 화면/광원 분리 문장: `the existing flat LED wall retains its exact frame, position and source artwork while reading as an active emissive display surface, with authentic luminance falloff rather than a printed backdrop`
- 무대 반사 문장(원본 무대 데크가 반사 가능한 마감일 때만): `the existing [dark semi-gloss / polished — 원본 관찰값] stage deck directly below the LED wall carries a controlled [원본 화면 색] horizontal specular reflection band, brightest at the screen base and naturally fading toward the audience, while retaining the deck's exact geometry, edge profile and base material identity`
- 국소 스필 문장: `a faint localized [원본 화면 색] bounce light reaches only the stage edge and the immediately adjacent original surfaces; the rest of the hall retains its original material colors and stays non-emissive`
- **Magnific 필수 규칙:** 위 세 문장은 행사장·컨퍼런스홀 Magnific 실사화 PROMPT에서 원본 조건이 충족되면 반드시 포함한다. `soft screen glow`처럼 포괄적으로만 쓰지 않는다. 첫 샘플에서 반사 밴드·국소 스필·객석 패브릭의 빛 흡수가 동시에 보이지 않으면 단순 업스케일로 판정하고, Creativity를 0.05 올린 한 번의 재시도까지만 허용한다. 이후 그래픽·구조가 흔들리면 전체 프레임 재시도를 중단하고 무대/데크 ZONE B 크롭으로 전환한다.

**전시장 배경 (부스가 홀 안에 놓인 광각 샷일 때만):**
- 배경: `exposed high-ceiling truss grid, fire sprinkler pipes, suspended rigging banners overhead, rows of neighboring booths, trade-fair aisle, grey aisle carpet`
- 오브젝트: `neighboring booth edges, brochure stands, cable covers, small product displays, aisle stanchions`
- 조명: `cool neutral exhibition hall lighting from metal-halide and fluorescent fixtures, slight fluorescent green bias only in ambient shadows, mixed with warm booth spotlights` (4000K대는 중성백색이지 녹색이 아니다 — 녹색끼는 그림자에만 미세하게)
- 촬영: `deep-focus architectural trade-show photography` (얕은 심도 금지 — 구조 보존 약화)

**★ 엔진 규칙 (전시부스는 반드시):** 규칙적 직선격자라 i2i 시 ControlNet 병행이 사실상 필수다. 우선순위 — **Lineart(또는 Lineart-realistic) 또는 Canny를 primary 구조 컨트롤**(포스트·패널·모서리 윤곽 보존), **MLSD는 긴 직선·소실점 보조로 optional**, **Depth는 부스 볼륨·통로 전후관계 보조로만** (특히 블럭부스는 Depth로 박스 모듈 입체감 보존). MLSD 단독은 짧은 포스트 두께·패널 seam·조명 암을 날려 부족하다. GPT 단독 경로보다 SD+ControlNet을 권장한다. **FLUX 파이프라인이면 FLUX-native 컨트롤(Canny-dev 또는 Depth-dev 택일, 동시 사용은 ComfyUI 스태킹 검증 필요)로 구성한다 — SD/SDXL 계열 CN은 로드 불가.** 참조용 커뮤니티 파이프라인: PH's Archviz x AI(civitai, SDXL→FLUX 단계식 — 2026-07 조회 기준, dev 계열 비상업 라이선스 주의).

**★ GPT-image 경로 긍정형 잠금문 (NEGATIVE 대신 PROMPT에 이어붙임):**
> `"Keep the straight rigid booth structure, original panel boundaries, observed fixture set, printed artwork, typography, logos and carpet outline aligned one-to-one with Image 1. Actively transform only the existing wall, ceiling, floor, metal, glass, lighting, reflections and contact shadows into physically believable photographed surfaces. The completed installation reads as a real exhibition stand photographed on location, with intact continuous opaque graphic faces and exactly the observed frame and signage set."`

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

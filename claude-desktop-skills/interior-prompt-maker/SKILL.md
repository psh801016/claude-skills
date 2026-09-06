---
name: interior-prompt-maker
description: "실내 CGI·렌더를 Magnific / Gemini·Nano Banana / SD·ComfyUI image-to-image용 사실적 사진 프롬프트로 변환한다. 실내 이미지와 함께 '프롬프트 만들어줘', '실사화해줘', '실사화 스킬', '리모델링 프롬프트', 'i2i 프롬프트', '사진처럼', 'CGI 느낌 제거'라고 하면 사용한다. 1장 실사화와 2장 구조보존 리모델링을 구분하고, 한국 전시부스 시공(목공·블럭·옥타늄·맥시마)을 구조 증거로 구역별 판별한다."
---

# 인테리어 Image-to-Image 프롬프트 메이커

인테리어 CGI/렌더/모델 이미지를 실제 건축 인테리어 사진과 구분 불가능한 수준의 프롬프트로 변환한다.

## 발동 범위와 라우팅

- **엔진을 먼저 확정한다.** 미지정이면 Magnific / Gemini / SD·ComfyUI 중 무엇인지 확인하고,
  엔진별 출력을 섞지 않는다.
- 프롬프트·스킬 요청은 **이미지 생성 권한이 아니다.** 사용자가 생성·제작을 명시했을 때만
  생성 도구를 호출한다.
- 건물 외관은 `arch-prompt-maker`, 재질 추출은 `texture-prompt-maker`,
  조명만 이식할 때는 `cinematic-exhibition-lighting`, 사람 별도 합성은 `person-layer-maker`.

### 전시·행사 조명 인계

- 전시·무대·컨퍼런스 공간의 조명만 바꾸거나 조명 참고이미지가 있으면, 이 스킬은 별도 조명 프롬프트나 결과를 만들지 않고 `cinematic-exhibition-lighting`에 인계한다. 참고사진에서는 빛의 물리적 특성만 분석하고, 구조·스크린·그래픽을 옮겨오지 않는다.
- 실사화와 행사 조명을 함께 요청하면 이 스킬은 재질·노출·원본 구조 보존까지의 베이스를 맡고, 조명의 광원·빛줄기·간접광·합성본과 라이트 플레이트는 조명 스킬이 단일 책임으로 만든다.
- 사용자가 이미지 생성을 명시한 조명 작업은 조명 스킬이 합성본과 같은 구도의 라이트 플레이트를 각각 낸다. 이 스킬은 그 뒤 선택된 합성본을 다시 중성화·재조명하지 않는다.

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

→ **`references/space-types.md` 에 있다.** 대상 공간 유형(거실·주방·욕실·오피스·로비·전시부스 등)이 정해지면 해당 항목만 읽는다.
해당 상황이면 넘기지 말고 그 파일을 반드시 읽는다.

## 실제 시공 기준 표현

→ **`references/as-built-reality.md` 에 있다.** 전시부스·행사장·무대·백월이면 `exhibition-booth-classification.md`
와 **함께** 반드시 읽는다. 공법 판정은 저 문서, "시공하면 실제로 어떻게 보이는가"(포스트 돌출·파시아 2단·
통로 원바닥·백월 하단 업라이트 감쇠·현수막/후렉스/패트지 재질 구분·컨벤션센터 마감천장)는 이 문서가 정본이다.

## 예시

→ **`references/examples.md` 에 있다.** 작성 형식이 헷갈리거나 완성본 참고가 필요할 때 읽는다.
해당 상황이면 넘기지 말고 그 파일을 반드시 읽는다.


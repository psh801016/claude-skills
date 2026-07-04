---
name: person-layer-maker
description: "이미 실사화된 공간 사진(전시부스·행사장·인테리어·건물)에 사람을 **별도 레이어로 합성**하기 위한 인물 생성 프롬프트 + 포토샵 합성 가이드를 만드는 스킬. 인물을 장면에 직접 그려넣지 않고(bake 금지), 필요한 사람을 **컷당 2~3명으로 묶어 최소 컷 수로 일괄 생성**해 **배경에서 사람만 분리**하고(간격 배치로 인물별 분할 가능) 그림자·반사·색보정까지 전부 분리 레이어로 쌓아 위치·크기·인원·조명을 언제든 수정할 수 있게 한다. 사용자가 '사람 합성', '인물 합성', '사람 넣어줘', '인물 넣어줘', '사람 레이어', '인물 레이어', '스태프 넣어줘', '관람객 넣어줘', '사람 추가 프롬프트' 같은 말을 하면 반드시 이 스킬을 사용한다. 주 도구: Higgsfield(Nano Banana Pro) 생성 + Magnific 업스케일 + 포토샵 레이어 합성. 공간 자체의 실사화는 interior/arch-prompt-maker, 원본 렌더에 이미 있는 인물의 실사 변환은 interior 8단계, 조명 레이어는 cinematic-exhibition-lighting이 담당한다."
---

# 인물 레이어 메이커 (사람 별도 합성)

**목표 = 수정 가능한 실사 인물 합성.** 인물을 장면 안에 한 번에 생성하면(통짜 인페인트) 위치·인원·포즈를 못 고치고, 한 명이 깨져도 전체를 재생성해야 한다. 그래서 이 스킬은 **사람을 장면과 분리해 생성하고, 배경에서 사람만 떼어 레이어로 얹는다** — 그림자·반사·색보정도 각각 분리 레이어. 마음에 안 드는 인물만 교체하고, 위치·크기는 자유 변형으로 조정한다.

## 0순위 원칙

1. **장면 전체에 인물을 직접 굽지(bake) 않는다.** 전체 장면 인페인트는 사용자가 명시적으로 요구할 때만("수정 불가" 경고 1줄과 함께).
2. **기본은 일괄 생성 → 사람만 분리.** 필요한 인물을 **컷당 2~3명 상한으로 묶어**(단색 배경, 서로 간격을 두고) 만들고, 배경에서 사람만 분리한다 — 같은 컷에서 나온 인물들은 조명·색·스타일이 자동으로 일치한다. 4명 이상이면 여러 컷으로 나누되(컷 분할 규칙은 아래 참조) 같은 조명 문구 + 첫 컷 레퍼런스 재투입으로 컷 간 일관성을 유지한다. 분리 후 필요하면 인물별로 레이어를 쪼갠다(간격 덕에 개별 선택 가능). **한 명씩 개별 생성은 교체·추가용 보조 수단**이다.
3. **장면 매칭이 실사감의 전부다.** 생성 전에 반드시 Image 1(합성 대상 장면)을 분석해 주입한다: ①카메라 높이/앵글 ②렌즈(광각 여부) ③조명 방향 ④색온도 ⑤대비 ⑥바닥 재질 ⑦장면의 그레인/선명도 ⑧기존 인물 유무.
4. **텍스트 소품 금지** — 명찰은 `a plain lanyard with a blank card`까지만, 의류·가방은 `unbranded, no legible text`. 글자는 후처리 합성(전시부스 fascia 규칙과 동일).
5. 카메라 브랜드 금지, 절대 초점거리 mm 숫자 금지, MJ 파라미터 금지 (하우스 공통 규칙).

## 생성 경로 (2경로 A·B + 보조 A-보조 — 먼저 선택)

| 경로 | 방법 | 장점 | 단점 | 언제 |
|---|---|---|---|---|
| **A. 스튜디오 일괄 생성 (기본)** | 필요한 인물을 **컷당 2~3명씩**(단색 배경, 간격 배치) 생성 → 배경에서 **사람만 분리** → 필요 시 인물별 레이어 분할 | 인물 간 조명·색·스타일 자동 일치, 적은 컷 수로 끝, 완전한 수정 컨트롤 | 조명·원근을 프롬프트로 근사(±오차) | 기본값 — 인물 다수, 근·중경 |
| **A-보조. 개별 재생성** | 특정 인물 1명만 같은 조명 문구로 재생성 → 교체 | 한 명만 갈아끼움, 픽셀 전부를 한 명에 할당 | 색 일치 재확인 필요(일괄 생성분을 레퍼런스로 재투입) | 교체·인원 추가 + **주인공급 근경 인물, 얼굴·손 디테일이 중요한 인물, 원근 차가 큰 인물** |
| **B. 컨텍스트 추출 (조명 정밀)** | 장면의 인물 배치 영역만 **크롭** → 그 크롭에 nanobanana 편집으로 인물 인페인트 → 개체 선택으로 **인물만 추출**해 레이어화 → 크롭 원본과 diff 확인 후 배경은 원본 사용 | 조명·원근·색이 장면에서 자동 일치(광각 왜곡 포함) | 추출 매팅 품질 의존, 생성이 배경을 살짝 물들일 수 있음(원본 배경으로 덮어 해결) | 조명이 복잡한 근경 1~2명, 경로 A가 계속 뜰 때 |

두 경로 모두 **최종 산출물은 분리 레이어** — 수정 컨트롤은 동일하게 확보된다.

## 빠른 흐름

1. **장면 분석**: SCENE MATCH 8항목 추출. 이미지가 없으면 합성 대상 장면을 먼저 요청한다.
2. **기존 인물 분기**: 베이스에 이미 사람이 있으면 — 유지(기존 인물의 조명·색을 신규 인물의 **매칭 앵커**로 사용) / 제거(인페인트로 지우고 바닥 재구성 후 진행) 중 확인.
3. **인물 구성 확인**: 몇 명, 역할, 근/중/원경, **포즈 분류(서기/앉기/기대기)** — 미지정이면 장면에 맞는 기본 구성을 제안하고 확인.
4. **컷 분할 계획 → GROUP PROMPT 출력** (경로 A 기본. NB Pro는 의미기반 — NEGATIVE 없음, 긍정형만). 컷 수 = 인원을 **컷당 2~3명 상한**으로 나누되, **같은 거리대(근/중/원경)·상호작용 무리 단위로 묶는다**(분할 규칙은 GROUP PROMPT 템플릿 절 참조). 각 컷마다 GROUP PROMPT 1개를 출력하고, 컷이 여럿이면 같은 조명 문구 + 첫 컷 레퍼런스 재투입으로 일관성을 유지한다.
5. **REPLACE PROMPT 템플릿 + PHOTOSHOP STEPS + SCALE ANCHOR + 품질 게이트 출력** (출력 형식의 구성 그대로)

## 출력 형식 (항상 이 구성)

```
[SCENE MATCH] — 8항목 분석 요약 + 기존 인물 분기
GROUP PROMPT × 컷 수 (컷당 2~3명 일괄 — 인물별 역할·포즈·간격 배치 명세 포함)
(인원 4명↑ / 거리대·무리 분리 시) GROUP PROMPT 2, 3 … — 컷별 별도
REPLACE PROMPT 템플릿 — 특정 인물 1명 교체용
PHOTOSHOP STEPS — 사람만 분리→인물별 분할→레이어 순서·블렌드·오클루전
SCALE ANCHOR — 크기 정렬 기준
QUALITY GATE — 재생성 판정 기준
```

---

## SCENE MATCH 분석 (프롬프트 주입값)

| 항목 | Image 1에서 읽는 것 | 주입/처리 |
|---|---|---|
| 카메라 | 눈높이/하이앵글 | `photographed at standing eye level` 등 원본과 동일 표현 |
| 렌즈 | 광각 여부(가장자리 수직선 기울기) | 광각이면 **인물을 프레임 중앙~중간 영역에 배치**(가장자리 회피). 가장자리 배치가 불가피하면 주변 수직선 기울기에 맞춰 인물을 미세 기울임 + Edit > Transform > Distort(또는 Adaptive Wide Angle)로 왜곡을 맞춘다 — 경로 B가 더 안전 |
| 조명 방향 | 주광 좌/우/상/후면 | `key light from the upper left, soft fill from the right` 식 명시 |
| 색온도 | 웜 스팟/중성백색/혼합 | `warm spotlight tone` / `cool neutral exhibition hall light` / `mixed warm-cool` |
| 대비 | 그림자 깊이·하이라이트 | `soft low-contrast lighting` ~ `crisp directional lighting with defined shadows` |
| 바닥 | 카펫·목재(무반사)/에폭시·폴리시드(반사) | 그림자·반사 레이어 설계에 사용 |
| 그레인·선명도 | 베이스 노이즈 레벨 | 통합 그레인 강도 결정(아래) |
| 기존 인물 | 있음/없음 | 있으면 색·조명·스케일의 **매칭 앵커**로 사용 |

## GROUP PROMPT 템플릿 (경로 A — Higgsfield Nano Banana Pro, 전원 일괄 생성)

**공통 골격 (사람만 분리 친화 — 단색 배경·간격 배치·접지):**
> `"Ultra photorealistic group photograph of [N] people arranged side by side with clear gaps between each figure, on a clean bare seamless [배경색] studio floor with only minimal soft contact shadows, against a plain solid empty [배경색] background, clean separable silhouettes, every figure fully visible from head to shoes inside the frame. From left to right: (1) [성별·연령·복장·역할·포즈], (2) [성별·연령·복장·역할·포즈], (3) [...]. Lighting matched to the destination scene: [조명 방향+색온도+대비], a single clear directional key light shared by all figures. Natural body proportions, candid unposed everyday stances, distinct faces and outfits for each person, realistic skin texture, individual hair strands, natural fabric drape and wrinkles, [카메라 높이 표현]. Documentary candid style, each person looking [시선 방향]."`

**★ 골격 변형 2종 (공통 골격은 "서기·간격·전신" 라인업 전제 — 아래 컷 유형이면 해당 절만 바꿔 쓴다):**
- **클러스터 컷 (상담 그룹 등 상호작용 무리):** `arranged side by side with clear gaps between each figure` → `standing close together in natural conversational spacing, bodies angled toward each other, the group reading as one connected cluster with a clean outer silhouette` — 클러스터는 1레이어 유지라 내부 간격이 필요 없다. 클러스터+단독 인물이 한 컷이면 **클러스터와 단독 인물 사이에만** 간격을 명시한다.
- **착석 컷 (앉은 인물):** `every figure fully visible from head to shoes` → `each figure seated on a simple gray box at the same height as the destination chair or desk, the entire seated figure and box fully visible in the frame`, `candid unposed everyday stances` → `natural seated posture, upper body upright` — 포즈군 통일 원칙에 따라 착석 인물은 어차피 별도 컷이다.

- **좌→우 슬롯 명세**: 인물마다 번호 슬롯으로 성별·나이·복장·포즈를 따로 박는다 — 안 그러면 비슷한 얼굴·복장이 반복된다(`distinct faces and outfits` 포함).
- **★플랫 라인업 규격**: 일괄 컷은 장면의 광각을 흉내내지 않고 **왜곡 없는 정면 라인업**으로 생성한다 — 골격에 `"rendered with a flat distortion-free perspective, as if photographed from a distance with a narrow field of view, all figures at the same camera distance"`를 포함. 컷 좌우 끝 인물에 광각 왜곡이 박히면 재배치가 불가능해진다. 장면의 원근은 배치·스케일(±15~20%)로만 대응하고, 그 이상은 거리대별 컷 분리.
- **포즈군 통일**: 같은 컷은 같은 포즈군(전원 서기 등)만 — 단일 프롬프트에 서기/앉기를 섞으면 모델이 포즈를 뒤섞는다. **앉은 인물·기댄 인물은 별도 컷 또는 개별 생성**(의자 귀속 문제도 함께 해결).
- **배경색은 컷당 1색**: 일괄 컷은 배경을 하나만 쓸 수 있다 — 슬롯들의 의상 명도와 겹치지 않는 **중성 미디엄 그레이 1색을 기본**으로 하고(아래 "배경색 동적 선택" 규칙을 따른다), 흰 옷과 검은 옷이 섞이면 미디엄 그레이로 고정한다(극단 명도 의상은 슬롯 명세에서 조정).
- **REPLACE(교체) 생성도 같은 플랫 정면 규격**으로 만든다 — 교체 인물만 다른 원근이면 오히려 티가 난다.

- **간격 배치가 핵심**: 인물 사이에 뚜렷한 틈(`clear gaps between each figure`)이 있어야 배경 제거 후 인물별로 쉽게 쪼갤 수 있다. **상호작용 무리(상담 그룹 등)만 붙여서** 하나의 클러스터로 두고, 클러스터 사이는 간격을 띄운다.
- **★한 컷 인원 상한 = 2~3명(1클러스터 포함).** 다인물을 한 컷에 몰수록 얼굴·손 디테일이 뭉개진다 — 4명 이상 필요하면 GROUP PROMPT를 **여러 컷으로 나누고**(무리별·거리대별), 컷 간 일관성은 같은 조명 문구 + 첫 컷 결과물을 레퍼런스로 재투입해 유지한다.
- **같은 컷 = 같은 거리대**: 한 컷의 인물들은 장면에서 비슷한 거리(근경군/중경군/원경군)에 배치될 사람들로 묶는다 — 같은 컷은 같은 카메라 거리로 생성되므로, 근경용과 원경용을 섞으면 확대·축소 시 원근감이 어긋난다. **같은 컷에서 나온 인물의 스케일 조정은 ±15~20%까지만** — 그 이상 차이 나는 배치는 거리대별 별도 컷으로 생성한다(원경 컷은 저디테일·약한 대비·소프트 에지의 원경 프리셋 사용).
- **상호작용 클러스터는 쪼개지 않는다**: 서로 닿거나 가린 무리는 가려진 신체 부위가 애초에 존재하지 않아 분할하면 잘린 팔·빈 어깨가 드러난다. 클러스터 = 1레이어로 유지하고, 개별 이동이 필요한 인물은 처음부터 간격을 두고 생성한다.
- **REPLACE PROMPT(교체용)**: 위 골격에서 인물 목록을 교체 대상 1명으로 줄이고, 일괄 생성 결과물을 **레퍼런스 이미지로 재투입**해 조명·색을 일치시킨다.
- 생성 도구가 **투명 배경(알파)이나 배경 제거 마스크 출력**을 지원하면 그 경로를 우선한다 — 단색 배경 컷아웃은 차선책이다.

- **배경색 동적 선택(매팅 품질)**: 기본 **중성 미디엄 그레이**. 의상이 밝으면(흰 셔츠·베이지) **미디엄~다크 그레이**로, 의상이 어두우면(검정·네이비) **라이트 그레이**로 바꿔 명도 대비를 확보한다 — 배경과 의상의 명도가 비슷하면 컷아웃이 실패한다. 그린 배경은 스필 오염 때문에 쓰지 않는다.
- **포즈 분류 반영**: 서기=`standing, entire body including shoes` / **앉기**=`seated on a simple gray box at the same height as the destination chair/desk`(의자 높이 근사 — 합성 시 가구로 가림) / 기대기=`leaning posture with clear contact side`.
- 조명은 스튜디오라도 **방향·색온도를 장면과 동일하게** 지정 — 몸의 3D 음영(코 밑·턱 밑·옷 주름)은 생성 단계에서만 만들 수 있고 포토샵 2D 보정으로는 재현 불가(플랫 무지향 생성 금지).

**역할 프리셋 (한국 전시장 기본값 — 장면·클라이언트 맥락에 맞춰 인종·복장은 조정한다):**
- 부스 스태프: `a Korean booth staff member in a neat business suit (or a plain single-color branded-style uniform without any lettering), a plain lanyard with a blank white card, welcoming posture or mid-explanation gesture`
- 비즈니스 관람객: `a Korean business visitor in smart casual attire, plain lanyard with a blank card, holding an unbranded tote bag or tablet, walking or pausing to look`
- 캐주얼 관람객: `a casually dressed Korean visitor, unbranded shopping bag, relaxed browsing posture`
- 상담 그룹(밀착 2~3인 = 1레이어 허용): `a Korean booth staff member explaining to two visitors, natural conversational spacing, candid mid-gesture`
- 앉은 접수 직원: `a Korean receptionist seated at counter height on a simple gray box, upper body upright, hands at desk level`
- 원경 통행인(배경용): `small distant figures walking along a trade-fair aisle, slightly out of focus, soft edges` — 원경만 아웃포커스 허용, 근·중경은 딥포커스

**다인물 일관성**: 일괄 생성(같은 컷)이면 조명·색·스타일 일관성이 **자동으로 확보**된다 — 이것이 기본 모드인 이유. 개별 재생성(교체·추가)할 때만 일괄 생성분을 **레퍼런스 이미지로 재투입**하고, 완성 후 그 인물의 색온도·그림자 방향이 나머지와 맞는지 확인한다. 레퍼런스 재투입도 얼굴·체형·의상이 어긋날(drift) 수 있다 — 같은 인물 유지가 필요하면 의상·체형을 프롬프트에 고정 명시하고 결과를 비교해 고른다.

**시선·포즈 규칙**: 카메라 정면 응시 금지(긍정형 `looking toward the booth display / toward each other`). 근경 1명 이상은 뒷모습·측면이 합성 티가 덜 난다.

## PHOTOSHOP STEPS (전부 분리 레이어 — 이 순서로 쌓는다)

```
[맨 위] 통합 그레인 (Add Noise·Monochromatic 체크, Overlay — 베이스 노이즈에 맞춰 0.5~3%) ← 마지막 1회
        헤이즈 레이어 (cinematic L2, Screen 30~60%)
        빔 레이어 (cinematic L1, Screen/Linear Dodge 40~70% — 하이라이트 클리핑 시 하향)
        [인물 클리핑] L3·L4 약화 복제 (인물에 클리핑, 불투명도 원본의 30~50%) ← 인물 하반신도 바닥 빛을 받게
        인물별 색보정 (Match Color→Camera Raw→Curves, 클리핑 마스크)
        인물 레이어 N ... (겹치면 앞사람이 위, 구조물 뒤면 구조물 마스크로 가림)
        인물 레이어 1 (컷아웃, 에지 1px 페더+디컨타미네이트)
        인물 그림자 레이어 (Multiply 20~60% — 몸 음영 방향 기준)
        스팟 풀 (L3)·컬러 워시 (L4) — 바닥·벽에 깔리는 빛은 인물 아래 (Screen 기본)
        바닥 반사 레이어 (광택 바닥만: 수직 반전 10~20%; 카펫·목재·무광은 생략)
[맨 아래] 베이스 플레이트 (실사화+Magnific 업스케일 완료본)
```
> **조명 샌드위치 + 이중 배치(핵심):** 바닥·벽에 깔리는 빛(L3·L4)은 인물 **아래**(인물이 빛 위에 서게), 공기 중의 빛(L1 빔·L2 헤이즈)은 인물 **위**(인물이 빔을 가로막게). 단, 인물 아래에만 두면 인물 몸은 그 빛을 못 받아 떠 보인다 — **L3·L4를 인물에 클리핑한 약화 복제본(30~50%)으로 이중 배치**해 하반신·몸통에도 같은 빛을 입힌다.

1. **사람만 분리 → 인물별 분할 (비파괴)**: 일괄 생성 컷의 **원본 레이어는 보존**하고, 인물(또는 클러스터)마다 **레이어 복제 + 마스크**로 분리한다(Layer Via Cut 단독 금지 — 파괴적이라 경계 복구가 안 된다). 간격 덕에 개별 선택이 쉽다. 머리카락은 '가장자리 다듬기', 마스크 손상 시 원본에서 다시 딴다. 밝은 의상 에지에 프린지가 남으면 배경색을 바꿔 재생성(위 배경색 규칙). **레이어명 규칙**: `P1_스태프_근경` 식으로 슬롯·역할·거리대를 박아 교체·재생성 추적을 쉽게 한다.
2. **오클루전(Z-순서)**: 인물이 카운터·집기 **뒤**에 서면 베이스에서 그 구조물을 선택해 인물 레이어 마스크로 하반신을 가린다. 인물끼리 겹치면 앞사람 레이어를 위로. 앉은 인물은 의자·데스크로 가려지는 부분을 같은 방식으로 마스킹.
3. **그림자 (별도 레이어)**: 인물 실루엣 복제 → **장면의 실제 그림자 색을 스포이드로 샘플링해 채움(순검정 금지)** → 자유 변형으로 바닥에 눕힘 → 2단 블러(접점 콘택트 AO는 진하고 선명하게·멀어지는 캐스트는 소프트하게) → Multiply 20~60% 시작(장면 조명이 강할수록 진하게 — 모든 수치는 시작값이며 장면 샘플링으로 조정). **방향은 프롬프트가 아니라 생성된 인물의 몸 음영을 기준으로** 잡는다. 기존 인물이 있으면 그들의 그림자 농도·방향에 맞춘다.
4. **색 매칭**: ① Image > Adjustments > **Match Color**(소스=베이스) ② Camera Raw(색온도·틴트) ③ Curves — 단 **최암/최명 '픽셀'에 맞추지 말 것**(노이즈·LED·금속 반짝임일 수 있다). 베이스의 대표 어두운/밝은 **면(패치)**을 샘플로 맞춘다. 기존 인물이 있으면 그 인물의 피부·의상 톤이 1차 기준. 그래도 '스티커'처럼 뜨면 감마가 다른 것 — 재생성이 빠르다.
5. **통합 그레인 맨 마지막 1회**: Add Noise(**Monochromatic 필수**), 강도는 베이스 노이즈에 맞춰 0.5~3%(깨끗한 베이스=0.5~1%, 행사장 고감도 사진=2~3%). 필요 시 인물에만 0.3~0.5px 블러.
6. **수정 컨트롤**: 인물 교체=해당 레이어만 재생성 / 위치·크기=자유 변형(SCALE ANCHOR) / 인원=레이어 on/off / 조명=조명 레이어만 교체.

## SCALE ANCHOR (크기 정렬 — 합성 티의 1순위 원인)

- **0단계 = 평면 판정**: 인물이 설 자리가 카메라와 **같은 바닥 평면인지 먼저 판정**한다(단상·경사·단차·데스크 안쪽이면 그 평면 기준으로 이후 규칙을 적용).
- **1순위 = 접점(contact point)**: 서기=발이 닿는 **그 바닥 평면**, **앉기=엉덩이가 닿는 좌면 + 머리 높이 이중 앵커**(발 접점 무의미), 기대기=접촉면. 접점이 틀리면 뜨거나 박혀 보인다.
- **2순위 = 눈높이 보정**: 평지+눈높이 샷이면 **서 있는 성인의 눈은 거리 무관 수평선 근처 정렬**. 접점을 잡은 뒤 눈 높이로 크기를 보정한다. 하이앵글이면 이 규칙은 쓰지 않는다(접점+원근만).
- 보조 앵커: 옥타놈 벽(약 2.5m)=성인 키의 140~150%, 데스크·의자·출입문 등 알려진 치수 요소, **기존 인물이 있으면 그 키가 최우선 스케일 기준**.

## QUALITY GATE (재생성 판정 — 보정으로 살리려 하지 말 것)

- 몸 음영의 키라이트 방향이 장면과 **±30° 이상** 어긋남 → 좌우 반전(Flip) 시도, 반전으로 안 되는 상하 불일치·소품 거울상 발생 시 **재생성**.
- Match Color 후에도 피부톤이 뜸(감마 불일치) → 재생성.
- 다인물 중 한 명만 색온도가 튐 → 그 인물만 재생성 또는 일괄 색보정.
- 광각 가장자리 배치에서 주변 수직선과 인물 축이 안 맞음 → 중앙 쪽으로 재배치 또는 경로 B로 전환.
- 전신 세로 프레이밍은 얼굴·손 디테일이 약해질 수 있다 → 생성 직후와 업스케일 후 **얼굴·손 QC 필수**(일괄 생성 컷은 인물마다 확인).
- **2단계 게이트**: ① 배치 게이트(컷 단위) — 인물이 겹치거나 간격이 없거나 라인업이 부자연스러우면 컷 재생성(간격 문구 강조), 반복 실패 시 인원을 줄여(2명) 재시도. ② 인물 게이트(분할 후 개별) — **1~2명만 불합격이면 컷을 버리지 말고 REPLACE PROMPT로 그 인물만 교체**, 절반 이상 불합격이거나 간격 붕괴면 컷 전체 재생성.

**최종 100% 확대 QC 체크리스트 (내보내기 전):** ①헤어 에지 프린지 ②발/엉덩이 접지 ③그림자 방향=몸 음영 ④인물 대비가 베이스와 동일 ⑤피부 채도 ⑥그레인 크기 균일 ⑦조명 레이어가 인물·벽·바닥을 잘못 덮는 곳 없음.

## Higgsfield · Magnific 운용 규칙

- 생성: **Higgsfield Nano Banana Pro**(웹 — 2026-07 기준 무료 UNLIMITED, 제품 정책은 변동 가능) 세로 프레이밍, 3~4 변형 중 선택. 같은 인물 재사용은 **레퍼런스 이미지 재투입**으로 캐릭터 일관성 유지. SD 계열로 인물을 생성하는 경우에만 negative 사용 가능(이 스킬의 기본 경로 NB Pro는 긍정형만).
- 업스케일: 베이스가 Magnific 업스케일본이면 인물도 해상도를 맞춰 합성 — **인물은 Creativity 0.1 / Resemblance 0.95**(얼굴 변형 방지, 0~1 스케일).
- Magnific **Relight**: 컷아웃 인물에 베이스를 광원 레퍼런스로 걸어 색광을 자동 일치 — **순서: 컷아웃 직후 Relight 먼저 시도 → 부족하면 PHOTOSHOP STEPS 4의 수동 색 매칭(Match Color→Camera Raw→Curves)으로 보완**. 두 절차는 경쟁이 아니라 지름길→정밀 순의 한 파이프라인이다.
- **NB Pro(기본 경로)에서는 NEGATIVE를 출력하지 않는다** — 의미기반이라 부정 나열이 역효과. 억제는 긍정형으로만. SD 계열로 대체 생성할 때만 negative를 쓴다(위 생성 규칙).

## 대안·고급 경로 (요청 시 안내)

- **전체 장면 인페인트 한방 합성**: 빠르지만 수정 불가 — 기본 금지, 명시 요청 시 경고와 함께.
- **Generative Fill을 그림자에만**: 인물은 레이어, 접지 그림자만 Generative Fill로 — 그림자도 별도 레이어로 유지.
- **3D 프록시 프리비즈**(고급): 장면 카메라를 근사한 Blender 마네킹으로 원근·스케일·그림자 방향을 수학적으로 확정한 뒤 그 렌더를 가이드로 생성 — 다인물·광각·오클루전이 복잡할 때 최상 정확도.

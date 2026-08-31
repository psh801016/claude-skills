<!-- person-layer-maker/SKILL.md 에서 분리. 원문 그대로이며 내용 변경 없음. -->

## GROUP PROMPT 템플릿 (경로 A — Higgsfield Nano Banana Pro, 전원 일괄 생성)

**공통 골격 (사람만 분리 친화 — 단색 배경·간격 배치·접지):**
> `"Ultra photorealistic group photograph of [N] people arranged side by side with clear gaps between each figure, on a clean bare seamless [배경색] studio floor with only minimal soft contact shadows, against a plain solid empty [배경색] background, clean separable silhouettes, every figure fully visible from head to shoes inside the frame. From left to right: (1) [성별·연령·복장·역할·포즈], (2) [성별·연령·복장·역할·포즈], (3) [...]. Lighting matched to the destination scene: [조명 방향+색온도+대비], a single clear directional key light shared by all figures. Natural body proportions, candid unposed everyday stances, distinct faces and outfits for each person, realistic skin texture, individual hair strands, natural fabric drape and wrinkles, [카메라 높이 표현]. Documentary candid style, each person looking [시선 방향]."`

- **좌→우 슬롯 명세**: 인물마다 번호 슬롯으로 성별·나이·복장·포즈를 따로 박는다 — 안 그러면 비슷한 얼굴·복장이 반복된다(`distinct faces and outfits` 포함).
- **★플랫 라인업 규격**: 일괄 컷은 장면의 광각을 흉내내지 않고 **왜곡 없는 정면 라인업**으로 생성한다 — 골격에 `"rendered with a flat distortion-free perspective, as if photographed from a distance with a narrow field of view, all figures at the same camera distance"`를 포함. 컷 좌우 끝 인물에 광각 왜곡이 박히면 재배치가 불가능해진다. 장면의 원근은 배치·스케일(±15~20%)로만 대응하고, 그 이상은 거리대별 컷 분리.
- **포즈군 통일**: 같은 컷은 같은 포즈군(전원 서기 등)만 — 단일 프롬프트에 서기/앉기를 섞으면 모델이 포즈를 뒤섞는다. **앉은 인물·기댄 인물은 별도 컷 또는 개별 생성**(의자 귀속 문제도 함께 해결).
- **배경색은 컷당 1색**: 일괄 컷은 배경을 하나만 쓸 수 있다 — 슬롯들의 의상 명도와 겹치지 않는 **중성 그레이 1색**을 고르고, 흰 옷과 검은 옷이 섞이면 미디엄 그레이로 고정한다(극단 명도 의상은 슬롯 명세에서 조정).
- **REPLACE(교체) 생성도 같은 플랫 정면 규격**으로 만든다 — 교체 인물만 다른 원근이면 오히려 티가 난다.

- **간격 배치가 핵심**: 인물 사이에 뚜렷한 틈(`clear gaps between each figure`)이 있어야 배경 제거 후 인물별로 쉽게 쪼갤 수 있다. **상호작용 무리(상담 그룹 등)만 붙여서** 하나의 클러스터로 두고, 클러스터 사이는 간격을 띄운다.
- **★한 컷 인원 상한 = 2~3명(1클러스터 포함).** 다인물을 한 컷에 몰수록 얼굴·손 디테일이 뭉개진다 — 4명 이상 필요하면 GROUP PROMPT를 **여러 컷으로 나누고**(무리별·거리대별), 컷 간 일관성은 같은 조명 문구 + 첫 컷 결과물을 레퍼런스로 재투입해 유지한다.
- **같은 컷 = 같은 거리대**: 한 컷의 인물들은 장면에서 비슷한 거리(근경군/중경군/원경군)에 배치될 사람들로 묶는다 — 같은 컷은 같은 카메라 거리로 생성되므로, 근경용과 원경용을 섞으면 확대·축소 시 원근감이 어긋난다. **같은 컷에서 나온 인물의 스케일 조정은 ±15~20%까지만** — 그 이상 차이 나는 배치는 거리대별 별도 컷으로 생성한다(원경 컷은 저디테일·약한 대비·소프트 에지의 원경 프리셋 사용).
- **상호작용 클러스터는 쪼개지 않는다**: 서로 닿거나 가린 무리는 가려진 신체 부위가 애초에 존재하지 않아 분할하면 잘린 팔·빈 어깨가 드러난다. 클러스터 = 1레이어로 유지하고, 개별 이동이 필요한 인물은 처음부터 간격을 두고 생성한다.
- **REPLACE PROMPT(교체용)**: 위 골격에서 인물 목록을 교체 대상 1명으로 줄이고, 일괄 생성 결과물을 **레퍼런스 이미지로 재투입**해 조명·색을 일치시킨다.
- 생성 도구가 **투명 배경(알파)이나 배경 제거 마스크 출력**을 지원하면 그 경로를 우선한다 — 단색 배경 컷아웃은 차선책이다.

- **배경색 동적 선택(매팅 품질)**: 기본 라이트 그레이. 의상이 밝으면(흰 셔츠·베이지) **미디엄~다크 그레이**로 바꿔 명도 대비를 확보한다 — 배경과 의상의 명도가 비슷하면 컷아웃이 실패한다. 그린 배경은 스필 오염 때문에 쓰지 않는다.
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

**시선·포즈 규칙**: 일반 전시·부스 장면은 카메라 정면 응시를 피하고 `looking toward the booth display / toward each other`처럼 장면 안의 목적지를 지정한다. 단, **포토존·옥타판은 위 ‘포토존·옥타판 구역 및 포즈 판정’이 우선**한다. 포토존 주인공 2명은 사용자 수정본 또는 대상 판의 실제 3D 평면에서 유도한 `n_front`를 따른다. 화면 좌우나 카메라 방향으로 환산하지 않는다. 머리·눈만 돌리고 몸통·골반·발이 다른 방향에 남으면 불합격이다. 주변 참석자만 일반 전시 장면의 시선·대화·보행 규칙을 따른다.

---
name: person-layer-maker
description: "이미 실사화된 공간 사진(전시부스·행사장·인테리어·건물)에 사람을 별도 레이어로 합성하기 위한 인물 생성 프롬프트 + 포토샵 합성 가이드를 만든다. '사람 합성', '인물 합성', '사람 넣어줘', '인물 넣어줘', '배경에 맞게 사람 배치', '장면에 사람 넣어', '사람 레이어', '인물 레이어', '스태프·관람객 넣어줘'라고 하면 사용한다. 그림자·빛·색보정까지 분리 레이어로 쌓아 위치·인원·조명을 나중에 고칠 수 있게 한다."
---

# 인물 레이어 메이커 (사람 별도 합성)

**목표 = 수정 가능한 실사 인물 합성.** 인물을 장면 안에 한 번에 생성하면(통짜 인페인트) 위치·인원·포즈를 못 고치고, 한 명이 깨져도 전체를 재생성해야 한다. 그래서 이 스킬은 **사람을 장면과 분리해 생성하고, 배경에서 사람만 떼어 레이어로 얹는다** — 그림자·반사·색보정도 각각 분리 레이어. 마음에 안 드는 인물만 교체하고, 위치·크기는 자유 변형으로 조정한다.

주 도구는 Higgsfield(Nano Banana Pro) 생성 + Magnific 업스케일 + 포토샵 레이어 합성이다.
공간 자체의 실사화는 `interior-prompt-maker` / `arch-prompt-maker`,
원본 렌더에 **이미 있는** 인물의 실사 변환은 `interior-prompt-maker` 8단계,
조명 레이어는 `cinematic-exhibition-lighting`이 담당한다.
아이소메트릭·탑다운 렌더는 `isometric-person-compositor`.

## 최우선 출력 계약 — 프롬프트만 먼저

이 절은 아래의 모든 상세 경로·합성 절보다 우선한다.

1. 사용자가 **"이미지 생성해"·"이미지 만들어"처럼 생성 자체를 명시**하기 전에는 이미지 생성 도구, Higgsfield 웹 UI, 이미지 편집 도구를 절대 실행하지 않는다. 이미지 첨부·"사람스킬"·"새로 만들어"·"다시 해"는 **새 프롬프트 요청**으로 해석한다.
2. 기본 응답은 설명·표·워크플로·레이어 가이드 없이 **복사 가능한 영문 프롬프트 1개만** 낸다. 사용자가 설명, 레이어, 포토샵, diff, QC를 요청할 때만 해당 절을 덧붙인다.
3. 원본 빈 공간에 사람을 새로 넣는 요청은 이전 생성본을 수정하지 않는다. **원본 빈 이미지 하나만 베이스**로 하여, 모든 사람을 한 프롬프트에서 새로 구성한다. 단, 사용자가 포토샵으로 위치·스케일·방향을 잡은 합성본을 정답 예시로 주면 그 합성본이 **배치 마스터**다. 이때 빈 원본과 합성본을 함께 넣어 모델이 어느 쪽을 베이스로 고르게 하지 말고, 깨끗하게 내보낸 합성본 한 장만 사용해 인물 실루엣 영역을 국소 교체한다.
4. 사람이 한 명만 이상하면 전체 이미지를 다시 편집하지 않는다. 해당 인물과 접지 그림자에 필요한 최소 영역만 마스크 편집한다. 다른 인물의 보존을 장황한 다중 이미지 지시로 해결하지 않는다. 위치·스케일·방향이 이미 맞는 포토샵 합성본은 인물 기하를 다시 생성하지 않고 색·조명·접지만 보정한다.
5. 프롬프트는 AI가 바로 실행할 수 있게 `base image → exact people and zones → lighting/perspective → immutable elements` 순서로 쓴다. 인원·성별·역할·위치를 짧고 명확하게 지정하며, 성별 표현이 필요한 경우 `clearly Korean woman/man`과 헤어·의상·포즈를 함께 쓴다.

### 기본 영문 프롬프트 뼈대

```text
Using the original empty [scene] image as the only base, add exactly [N] realistic Korean [event] attendees. Return the exact original pixel dimensions, aspect ratio and crop. Do not redraw, resample, blur, denoise or soften the existing background. Preserve every original background pixel outside the new people and their immediate physically required shadows/reflections. Do not change any existing architecture, text, logos, screens, graphics, lighting or camera angle.

Place: [one concise numbered list of people, role, gender, outfit and physical zone]. Keep people away from all signage and screen content.

Match correct perspective, scale, grounded feet, scene lighting, contact shadows, and only the floor reflections supported by the floor material. Render the people with crisp high-resolution facial, hand, hair and fabric detail at their final placed size. Natural candid business-event posture, no direct eye contact, no readable text on clothing or props. Change only the people and their immediate shadows/reflections.
```

## 해상도·원본 픽셀 보존 (포토존 포함 전 경로 필수)

- **최종 캔버스는 입력 원본과 픽셀 치수·종횡비·크롭이 완전히 같아야 한다.** 축소본, 임의 업스케일본, 리사이즈·재크롭본은 결과 후보로도 통과시키지 않는다.
- AI 전체 화면 편집 결과는 사람·접지 그림자·인접 반사 추출용 소스일 뿐이다. **최종본의 사람 마스크 밖 모든 배경 픽셀은 손대지 않은 원본에서 복원**한다. 건축, 옥타판, 글자, 로고, 그래픽, 천장, 바닥은 생성 결과의 재렌더 픽셀을 남기지 않는다.
- 전체 화면을 반복 생성·업스케일·디노이즈하지 않는다. 한 번의 전체 화면 후보에서 방향·위치·해상도가 틀리면 즉시 인물 전용 국소 마스크 또는 별도 인물 레이어로 전환한다. 반복 편집으로 생긴 글자 번짐·벽면 뭉개짐·바닥 질감 손실은 보정 대상이 아니라 반려 사유다.
- 인물 디테일이 부족하면 전체 장면을 확대하지 않는다. **인물 영역만 최종 배치 크기보다 충분히 큰 고해상도 소스로 다시 생성**한 뒤 한 번만 축소해 합성한다. 얼굴·손·머리카락·의상 가장자리를 100% 확대에서 확인한다.
- 최종 QC에서 원본과 결과를 100% 확대 Difference 비교한다. 허용 차이는 `인물 실루엣 + 접지 그림자 + 물리적으로 필요한 인접 반사/스필` 안쪽뿐이다. 그 밖의 차이는 모두 원본 픽셀로 되돌린다.

## 0순위 원칙

1. **장면 전체에 인물을 직접 구운(bake) 이미지를 최종본으로 내지 않는다.** 단 bake 결과를 **'소스'로 쓰는 것은 허용** — 경로 C는 장면에 직접 배치 생성한 뒤 원본과의 차분으로 사람·빛·그림자만 레이어로 떼어 수정 컨트롤을 회수한다. bake 결과를 그대로 최종본으로 쓰는 건 사용자가 명시적으로 요구할 때만("수정 불가" 경고 1줄과 함께).
2. **기본은 일괄 생성 → 사람만 분리.** 필요한 인물 **전원을 한 번의 생성으로** 같은 컷 안에(단색 배경, 서로 간격을 두고) 만들고, 배경에서 사람만 분리한다 — 같은 컷에서 나온 인물들은 조명·색·스타일이 자동으로 일치한다. 분리 후 필요하면 인물별로 레이어를 쪼갠다(간격 덕에 개별 선택 가능). **한 명씩 개별 생성은 교체·추가용 보조 수단**이다.
3. **장면 매칭이 실사감의 전부다.** 생성 전에 반드시 Image 1(합성 대상 장면)을 분석해 주입한다: ①카메라 높이/앵글 ②렌즈(광각 여부) ③조명 방향 ④색온도 ⑤대비 ⑥바닥 재질 ⑦장면의 그레인/선명도 ⑧기존 인물 유무.
4. **텍스트 소품 금지** — 명찰은 `a plain lanyard with a blank card`까지만, 의류·가방은 `unbranded, no legible text`. 글자는 후처리 합성(전시부스 fascia 규칙과 동일).
5. 카메라 브랜드 금지, 절대 초점거리 mm 숫자 금지, MJ 파라미터 금지 (하우스 공통 규칙).

## 생성 경로 3가지 (먼저 선택)

| 경로 | 방법 | 장점 | 단점 | 언제 |
|---|---|---|---|---|
| **C. 씬베이크 디프 추출 (배경 정합 기본)** | 장면 전체를 NB Pro Edit에 넣고 **인물을 장면 안에 직접 배치 생성**(SCENE PLACEMENT PROMPT) → 포토샵에서 원본과 **차분(diff)** 을 떠 '사람+사람에 묻은 빛+그림자'만 레이어로 추출 | 원근·스케일·조명·색·오클루전이 **장면에서 자동 정합**(합성 티 최소), 광각·컬러 스필도 자동 | 인물 개별 재배치는 제한적(교체는 부분 재생성), 전역 드리프트 시 diff 정리 필요 | **"배경에 맞게 넣어줘" 요청의 기본값** — 다인물·깊은 원근·복잡 조명 장면 |
| **A. 스튜디오 일괄 생성** | 필요한 인물 **전원을 한 컷에**(단색 배경, 간격 배치) 생성 → 배경에서 **사람만 분리** → 필요 시 인물별 레이어 분할 | 인물 간 조명·색·스타일 자동 일치, **위치·크기·인원 완전 자유** | 조명·원근을 프롬프트로 근사(±오차) — 장면 정합은 수동 | 인물 위치를 자유롭게 옮겨야 할 때, 소스 라이브러리 구축 |
| **A-보조. 개별 재생성** | 특정 인물 1명만 같은 조명 문구로 재생성 → 교체 | 한 명만 갈아끼움, 픽셀 전부를 한 명에 할당 | 색 일치 재확인 필요(일괄 생성분을 레퍼런스로 재투입) | 교체·인원 추가 + **주인공급 근경 인물, 얼굴·손 디테일이 중요한 인물, 원근 차가 큰 인물** |
| **B. 컨텍스트 추출 (조명 정밀·국소)** | 장면의 인물 배치 영역만 **크롭** → 그 크롭에 nanobanana 편집으로 인물 인페인트 → 개체 선택으로 **인물만 추출**해 레이어화 → 크롭 원본과 diff 확인 후 배경은 원본 사용 | 조명·원근·색이 장면에서 자동 일치(광각 왜곡 포함), 드리프트 범위가 크롭 안으로 격리 | 추출 매팅 품질 의존, 생성이 배경을 살짝 물들일 수 있음(원본 배경으로 덮어 해결) | 조명이 복잡한 근경 1~2명, 경로 C의 전역 드리프트가 심할 때 |

**경로 선택 기준:** 사용자가 "배경에 어울리게/맞게 넣어줘"라고 하면 **C가 기본** — 스튜디오 컷(A)을 먼저 내밀면 "이게 뭐냐"가 된다(2026-07-13 실사용 피드백). A는 인물 위치·인원을 사후에 자유 조정해야 하는 요구가 명확할 때만. 모든 경로의 **최종 산출물은 분리 레이어** — 수정 컨트롤은 동일하게 확보된다.

## 빠른 흐름

1. **출력 계약 판정**: 생성 명시가 없으면 영문 단일 프롬프트만 출력한다. 생성 명시가 있을 때만 해당 경로의 실행 절차를 사용한다.
2. **경로 판정**: "배경에 맞게/어울리게 넣어줘" 또는 배경 정합 우선 → **경로 C**. 위치·인원 사후 자유 조정이 명시 요구 → 경로 A.
3. **장면 분석**: SCENE MATCH 8항목 추출. 이미지가 없으면 합성 대상 장면을 먼저 요청한다.
4. **기존 인물 분기**: 베이스에 이미 사람이 있으면 — 유지(기존 인물의 조명·색을 신규 인물의 **매칭 앵커**로 사용) / 제거(인페인트로 지우고 바닥 재구성 후 진행) 중 확인.
5. **인물 구성 확인**: 몇 명, 역할, 근/중/원경, **포즈 분류(서기/앉기/기대기)** — 미지정이면 장면에 맞는 기본 구성을 제안하고 확인.
6. **프롬프트 출력**: 경로 C = SCENE PLACEMENT PROMPT 1개 / 경로 A = GROUP PROMPT(상호작용 무리·거리대별로 나눠 2~3개까지). NB Pro는 의미기반 — NEGATIVE 없음, 긍정형만.
7. **추출/합성 가이드 출력**: 경로 C = DIFF EXTRACT STEPS / 경로 A = PHOTOSHOP STEPS. + SCALE ANCHOR + 품질 게이트.

## 출력 형식 (판정된 경로 것만 출력 — 두 경로를 다 내밀지 않는다)

생성 명시가 없으면 이 형식을 사용하지 말고, 위의 **기본 영문 프롬프트 뼈대에 맞춘 프롬프트 1개만** 출력한다.

```
[SCENE MATCH] — 8항목 분석 요약 + 기존 인물 분기 + 경로 판정(C/A/B와 근거 1줄)
(경로 C면) SCENE PLACEMENT PROMPT + DIFF EXTRACT STEPS — 인물/효과 레이어 분리
(경로 A면) GROUP PROMPT (+필요 시 GROUP PROMPT 2) + PHOTOSHOP STEPS
REPLACE PROMPT 템플릿 — 특정 인물 1명 교체용
SCALE ANCHOR — 크기 정렬 기준
QUALITY GATE — 재생성 판정 기준
+ 미선택 경로는 마지막에 1줄 안내("위치를 자유롭게 옮기려면 경로 A로" 등)
```

---

## 경로 C — 씬베이크 디프 추출 (2026-07-13 신규 · 실사용 1건 검증 + 3중 적대검수 반영)

**아이디어:** 배경 정합(원근·조명·오클루전·컬러 스필)은 모델이 장면 안에서 생성할 때 가장 정확하다. 그래서 **장면에 직접 배치 생성**하되, 결과를 그대로 쓰지 않고 원본과 비교해 "사람 + 사람이 만든 효과(빛·그림자)"만 레이어로 떼어 원본 위에 얹는다 — 정합은 자동, 수정 컨트롤은 레이어로 회수.

**★마스크 역할 정의(핵심):** 인물 실루엣의 1차 소스는 **Select Subject(개체 선택)+수동 보정**이다. 픽셀 diff는 인물 마스크가 아니라 **"효과(그림자·스필) 후보 영역"을 제한하는 보조 마스크**로만 쓴다 — NB Pro는 전 프레임을 재렌더하므로 diff에는 그레인·압축 노이즈가 항상 섞여 있어 최종 마스크 자격이 없다(3중검수 만장일치).

### C-1. SCENE PLACEMENT PROMPT 골격 (NB Pro Edit — 베이스 이미지 첨부)

> `"Add realistic [인종/국적] people into this existing [장면 유형] photograph. Protected and unchanged: the camera, composition, framing, resolution, aspect ratio and crop (return the image at the identical resolution, pixel-aligned with the input), and every existing structure, surface, color and text — [장면 고유 요소 나열]. Allowed changes only: the newly added people themselves, their contact shadows on the floor and furniture, and subtle light spill on surfaces immediately adjacent to them. Place them naturally into the real depth of the scene: [구역별 배치 명세 — 구역마다 '위치 + 인원 + 역할·복장 + 포즈·시선 + 앞뒤 관계(예: partially occluded behind the front counter)' 한 줄]. Match every person to the scene: correct perspective and size for their exact floor position and distance, feet and hips properly contacting the floor and chairs, lit by the scene's key light from [SCENE MATCH에서 읽은 광원 방향·경도·색온도], color temperature matching the surrounding light[, with 장면 고유 컬러 스필 문구], realistic soft contact shadows beneath each person on the [바닥 재질], all shadows falling in the same direction as existing shadows in the scene. Natural candid postures, distinct faces and outfits, realistic skin and hair, unbranded clothing with no text, [photo-zone or scene-matched eye-direction instruction]. Photorealistic documentary photograph, people fully integrated into the space, not pasted on top."`

- **보호/허용 분리가 잠금의 핵심**: "아무것도 바꾸지 마 + 그림자는 그려"는 자기모순이라 모델이 잠금을 느슨히 해석하며 전역 드리프트로 샌다. 위처럼 **Protected(구조·색·해상도) / Allowed(신규 인물·접지 그림자·인접 스필)** 를 명시 분리한다.
- **해상도·픽셀 그리드 락 필수**: diff 공정 전체가 두 이미지의 동일 픽셀 그리드를 전제한다 — 락 문구가 없으면 NB Pro가 크롭·리사이즈해 공정이 시작부터 무너진다.
- **오클루전 명시**: 전경 구조물 뒤에 설 인물은 반드시 `partially occluded behind [구조물]`로 앞뒤 관계를 지정 — 틀린 오클루전은 레이어로도 수정 불가(부분 재생성이 유일한 출구).
- 구역별 배치는 **장면의 실제 구조물 이름으로** 지정(`on the green grass carpet at the round wooden café tables` 식), 원경은 `smaller and softer as they are farther away`. 텍스트 소품 금지·시선 규칙은 공통 원칙 그대로.

### 포토존·옥타판 구역 및 포즈 판정 (필수)

- **대상 옥타판을 먼저 특정한다.** 판의 색은 기준이 아니다. 긴 옥타 구조가 여러 칸이면 전체 벽을 포토존으로 취급하지 않는다. 사용자가 지정한 옥타판 1칸 또는 행사명·키비주얼이 크게 배치된 히어로 판 1칸만 대상 포토존이다. 일정표·이슈 목록·안내 화면이 있는 다른 판은 제외한다.
- **화면 좌표보다 실제 판의 3D 면을 먼저 읽는다.** 대상 판의 두 세로 프레임, 하단 베이스라인, 상단선의 원근으로 판 평면 `P`를 잡는다. 그래픽이 인쇄된 표시 앞면에서 관람객이 설 수 있는 열린 공간으로 나오는 수직 방향을 `n_front`로 정의한다. 카메라, 화면 중앙, 화면 좌우·상하, 판의 색, 카펫 색·화살표·그래픽 방향으로 `n_front`를 정하지 않는다.
- **판의 앞뒤가 불명확하면 추측하지 않는다.** 앞면과 열린 공간을 이미지에서 확정할 수 없으면 사용자 표시 또는 배치 마스터를 요청한다. 카메라를 향하는 쪽을 임의로 판 앞면으로 간주하지 않는다.
- 포토존의 좌우 경계는 대상 판 1칸을 감싸는 **두 개의 세로 프레임/기둥**이다. 두 프레임의 바닥 접점 중점을 `C_floor`로 정의한다. 주인공 2명의 위치는 화면 중앙이 아니라 이 프레임 사이의 **실제 3D 바닥 중심 `C_floor`**다.
- 두 사람을 하나의 그룹으로 보고 **두 사람 발 접지점의 그룹 중점이 `C_floor`와 일치**하게 한다. 두 사람 사이의 빈 간격 중심도 판의 세로 중앙선에 맞춘다. 판 중앙, 카펫 중앙, 화면 중앙이 서로 다르면 항상 **대상 판의 `C_floor`**가 우선이다.
- 두 발의 베이스라인은 판 하단 베이스라인과 평행하고 바로 앞에 있어야 한다. 사람을 카펫 앞쪽·대리석 쪽·카메라 쪽으로 당기거나 포토존 칸 바깥으로 옮기지 않는다.
- 포토존 주인공은 **정확히 2명 전신**이다. 두 사람은 판과 평행한 같은 베이스라인에 서며, 발뒤꿈치와 등이 판에 거의 닿아 보일 정도로 가깝게 배치한다.
- **사용자 수정본이 배치 정본이다.** 사용자가 포토샵으로 사람 위치·스케일·방향을 잡은 이미지를 주면 그 픽셀 배치를 다시 추정하거나 계산하지 않는다. 머리·어깨·골반·무릎·발 접지점과 몸 방향을 그대로 보존한다.
- **방향은 하나의 3D 관계로만 판정한다.** 공간 관계는 `대상 옥타판 P → 사람의 등 → 사람의 가슴·얼굴·시선 → n_front 방향의 열린 공간`이다. 판은 두 사람의 등 뒤에 있어야 한다. 얼굴·코·가슴·골반·무릎·발끝·시선은 판 앞쪽 열린 반공간을 향해야 한다. 사람은 판을 바라보지 않으며, 머리나 눈만 다른 방향으로 돌면 불합격이다.
- **화면 투영은 결과 확인용일 뿐 지시 기준이 아니다.** 프롬프트에 `lower-left/right of the frame`, `screen left/right`, `toward the camera/viewer`, `front-facing`, `outward`를 방향 지시로 쓰지 않는다. 같은 3D 방향도 카메라 위치에 따라 화면에서 정면·측면·3/4로 보일 수 있으므로, 판 평면에서 유도한 `n_front`만 유지한다.
- 프롬프트에는 다음 관계를 한 덩어리로 쓴다: `standing immediately in front of the target Octanorm panel with the panel directly behind their backs; their chests, feet, faces and gaze all extend perpendicularly away from the panel into the open space in front of that panel; derive this direction from the physical panel plane, never from the render camera or screen coordinates`.
- **정확한 방향이 중요한 경우 텍스트 단독 생성을 금지한다.** 포토샵 수정본 또는 포즈 가이드가 있으면 그것을 한 장의 배치 마스터로 사용하고 주인공 2명 실루엣만 국소 교체한다. 가이드 없이 빈 원본에 텍스트만 써서 방향을 재현한 결과는 후보일 뿐 최종본으로 통과시키지 않는다.
- 두 사람은 하나의 포즈 그룹이다. 서로를 바라보거나 대화·이동·관람하는 장면이 아니라 같은 `n_front` 방향으로 나란히 선다. 짝다리·가벼운 몸 틀기·편안한 표정·비대칭 손 자세는 허용하되, 가슴·골반·발끝의 주방향이 판 앞쪽 열린 반공간을 벗어나면 안 된다.
- 사용자가 참조 이미지처럼 붐비는 행사 분위기를 요구하면, 주인공 2명과 별도로 주변 참석자를 포토존 핵심 구역 밖에 자연스럽게 배치한다. 주변 참석자는 소그룹 대화·대기·이동이 가능하지만 주인공 2명이나 대상 옥타판을 가리지 않는다.
- 빈 원본에 모든 인물을 새로 구성할 때는 주변 참석자까지 같은 프롬프트에 명시한다. 빈 원본에 `preserve existing people`라고 쓰지 않는다. 기존 사람이 있는 배치 마스터를 수정할 때만 보존 문구를 사용한다.
- **반복 실패 차단:** 방향, `C_floor` 중심, 판과의 거리, 입력 해상도 중 하나라도 한 번 틀리면 문구만 바꿔 전체 화면을 다시 생성하지 않는다. 원본 구조·그래픽·배경 픽셀을 잠그고, 배치 마스터+인물 전용 국소 마스크 또는 별도 고해상도 인물 레이어 합성으로 즉시 전환한다.
- 이 절은 일반 전시·부스의 시선 규칙, 화면 중앙, 카펫 장축, 카메라 정면 기반 추정보다 우선한다.

### C-2. DIFF EXTRACT STEPS (포토샵 — 인물/효과 분리, 기본 2레이어)

```
[위] C_인물   = R 복제 + [인물 실루엣 마스크(1~2px 확장)]                  (Normal)
     C_효과   = R 복제 + [(diff 후보 ∩ 인물 주변) − 인물] 마스크            (Normal) ← 그림자+스필 합본
[아래] 베이스(원본) = 손대지 않은 실사화 완료본
```

0. **픽셀 검증**: 베이스와 배치결과 R의 픽셀 치수가 동일한지 먼저 확인. 다르면 R을 베이스에 맞춰 리샘플하지 말고 **재생성**(락 문구 강화). 1~2px 수준 미세 어긋남만 Auto-Align 허용 — Auto-Align은 재렌더 이미지를 오히려 워프시킬 수 있으니 크게 어긋나면 정렬 대신 재생성.
1. **그레인 평탄화 후 diff(순서 중요)**: 베이스·R 각각 **사본**에 약한 Median(1~2px) 또는 Surface Blur를 걸어 그레인을 죽인 뒤, 그 사본끼리 Difference로 diff를 뜬다 — 원본끼리 바로 diff하면 서로 다른 그레인 난수 필드가 화면 전체 노이즈로 뜨고, Levels 임계로 이걸 죽이면 소프트 그림자 꼬리·은은한 스필(경로 C의 존재 이유)까지 같이 죽는다. 통합 그레인은 공통 규칙대로 맨 마지막 1회만.
2. **diff 후보 마스크**: 평탄화 diff 스탬프에 Levels로 잔노이즈만 가볍게 컷 → 채널 Ctrl+클릭으로 선택 로드 → **인물·그림자 주변만 러프 라쏘로 교집합 제한**(인물과 무관한 구역의 diff = 드리프트이므로 버리고 원본 노출).
3. **인물 마스크(1차 소스)**: R에 Select Subject 실행 → 잔머리·경계 수동 보정 → **기존 인물·포스터 속 인물·반사 인물이 있으면 차집합으로 제외** → 마스크를 1~2px **확장** + 디컨타미네이트(경계 반투명 픽셀·헤어가 효과 레이어로 새면 인물 윤곽에 halo가 남는다). = `C_인물`.
4. **효과 레이어(그림자+스필 합본)**: (diff 후보 − 인물 확장 마스크) = `C_효과`, 블렌드 Normal. **Darken/Lighten으로 그림자/빛을 더 쪼개는 것은 선택 사항** — Darken/Lighten은 채널별 min/max라 **채색 스필(예: 붉은 옷이 벽에 만든 빛)은 한 픽셀에서 두 레이어로 찢어진다**. 무채색에 가까운 장면에서만 쪼개고, 컬러 스필이 있는 장면은 합본 1레이어를 유지한 채 부분 마스크로 강도 조절한다.
5. **인물별 분할(선택)**: `C_인물` 마스크를 인물 단위로 쪼개 복제 — 개별 on/off·부분 교체용. 단 경로 C 인물은 장면 원근에 구워져 있어 **이동은 소폭만**(재배치 필요 시 그 인물만 지우고 부분 재생성 후 해당 영역 diff 재추출 — 기존 C 레이어와의 이음 경계는 새 diff가 이긴다).
6. **드리프트 대응(폴백)**: 인물 배치 구역 **밖**에서 diff가 유의미하게 뜨거나 배경 구조·글자·색이 눈에 띄게 변형 → 보존 잠금 강화 후 재생성, 2회 실패 시 **경로 B(크롭 부분편집)로 전환**(드리프트가 크롭 안으로 격리).
7. **광택 바닥 예외**: 반사 바닥이면 인물이 만드는 것은 그림자가 아니라 **밝고 채색된 반사** — 효과 레이어에서 반사 영역만 별도 마스크로 떼어 불투명도를 독립 조절한다.

### C-3. 경로 C QUALITY GATE

- **분해 무손실 자가검증**: `C_인물`+`C_효과`+베이스 합성 결과 위에 R을 Difference로 올려 인물·그림자 영역이 검게 나오는지 확인 — 어긋난 곳 = 마스크가 놓친 픽셀.
- **해상도·배경 선명도 게이트**: 결과의 픽셀 치수·종횡비가 원본과 정확히 같은지 확인한다. 인물·효과 마스크 밖에서 원본과 결과의 Difference가 뜨거나 글자·로고·판 그래픽·바닥 질감이 조금이라도 부드러워졌으면 결과를 반려하고 해당 구역을 원본 픽셀로 복원한다.
- **드리프트 판정은 면적%가 아니라 구역 기준**: 인물을 배치하지 않은 배경 구역의 diff 잔량으로 판정(다인물 장면은 정상 배치도 화면 대부분을 덮을 수 있다 — 절대 면적 임계 금지). 부스 로고·글자·구조물 변형은 면적과 무관하게 즉시 재생성 사유.
- 특정 인물만 불합격(얼굴·손 붕괴) → 그 인물 영역만 크롭해 REPLACE 부분 재생성(경로 B 절차) 후 diff 재추출.
- 접지·스케일은 장면 생성이라 대체로 자동 합격 — 그래도 발 접점·그림자 방향(기존 그림자와 동일 방향)·인물 윤곽 halo는 100% 확대 QC.

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
- **포토존 구역·방향 게이트**: ①선택된 대상이 사용자가 지정한 옥타판 1칸인가 ②두 세로 프레임·하단 베이스라인으로 실제 판 평면 `P`, 판 앞쪽 열린 방향 `n_front`, 두 프레임 바닥 접점의 중점 `C_floor`를 잡았는가 ③두 사람 발 접지점의 그룹 중점과 두 사람 사이 간격 중심이 `C_floor`에 일치하는가 ④두 발이 지정 바닥 안쪽이고 판 하단 바로 앞에 접지하며 등과 판 사이가 거의 붙어 보이는가 ⑤사용자 수정본이 있으면 머리·어깨·골반·무릎·발 접지점·스케일이 오버레이에서 일치하는가 ⑥판이 사람 등 뒤에 있고 얼굴·코·가슴·골반·무릎·발끝·시선이 모두 `n_front` 쪽 열린 반공간을 향하는가 ⑦카메라·화면 좌우·화면 정면이 방향 기준으로 쓰이지 않았는가 ⑧두 사람이 하나의 포즈 그룹으로 같은 물리 방향을 향하는가 ⑨주변 참석자가 주인공이나 대상 판을 가리지 않는가 ⑩최종 캔버스가 원본과 동일한 픽셀 치수이며 인물·효과 마스크 밖 배경이 원본 픽셀과 일치하는가를 확인한다. 하나라도 어기면 전체 화면 재생성을 반복하지 말고 배치 마스터+국소 마스크 또는 별도 고해상도 인물 레이어 합성으로 전환한다.

**최종 100% 확대 QC 체크리스트 (내보내기 전):** ①원본과 동일한 픽셀 치수·종횡비·크롭 ②인물·효과 마스크 밖 배경 픽셀 원본 일치 ③글자·로고·판 그래픽·바닥 질감 선명도 유지 ④헤어 에지 프린지 ⑤얼굴·손 디테일 ⑥발/엉덩이 접지 ⑦그림자 방향=몸 음영 ⑧인물 대비가 베이스와 동일 ⑨피부 채도 ⑩그레인 크기 균일 ⑪조명 레이어가 인물·벽·바닥을 잘못 덮는 곳 없음.

## Higgsfield · Magnific 운용 규칙

- 생성: **Higgsfield Nano Banana Pro**(웹 — 2026-07 기준 무료 UNLIMITED, 제품 정책은 변동 가능) 세로 프레이밍, 3~4 변형 중 선택. 같은 인물 재사용은 **레퍼런스 이미지 재투입**으로 캐릭터 일관성 유지. SD 계열로 인물을 생성하는 경우에만 negative 사용 가능(이 스킬의 기본 경로 NB Pro는 긍정형만). SD 경로 negative는 표준 인물 항목만 간단히: `mannequin look, waxy skin, plastic skin, distorted face, bad anatomy, broken hands, extra limbs, cutout edge halo` — 별도 섹션으로 출력하지 않고 사용자가 SD 사용을 밝힌 경우에만 인라인으로 안내한다.
- 업스케일: 베이스가 Magnific 업스케일본이면 인물도 해상도를 맞춰 합성 — **인물은 Creativity 0.1 / Resemblance 0.95**(얼굴 변형 방지, 0~1 스케일).
- Magnific **Relight**: 컷아웃 인물에 베이스를 광원 레퍼런스로 걸어 색광을 자동 일치 — 수동 색매칭 전에 시도할 가치가 있는 지름길. 무료 대안으로 **IC-Light**(오픈소스·MIT)의 배경조건(fbc) 모델이 같은 일(컷아웃 인물을 배경 조명에 자동 매칭)을 한다 — 단 결과는 구워진 이미지이고 디테일 그림자는 불완전하므로 매칭 후 포토샵 미세보정(동봉 배경제거기 BRIA RMBG는 비상업 라이선스 주의).
- NEGATIVE는 출력하지 않는다 — NB Pro는 의미기반(부정 나열 역효과). 억제는 긍정형으로만.

## 대안·고급 경로 (요청 시 안내)

- **전체 장면 인페인트 한방 합성(레이어 추출 없이)**: 빠르지만 수정 불가 — 기본 금지, 명시 요청 시 경고와 함께. 같은 생성을 하되 diff 추출까지 하면 경로 C가 된다 — 한방 합성 요청이 와도 경로 C를 먼저 권한다.
- **Generative Fill을 그림자에만**: 인물은 레이어, 접지 그림자만 Generative Fill로 — 그림자도 별도 레이어로 유지.
- **3D 프록시 프리비즈**(고급): 장면 카메라를 근사한 Blender 마네킹으로 원근·스케일·그림자 방향을 수학적으로 확정한 뒤 그 렌더를 가이드로 생성 — 다인물·광각·오클루전이 복잡할 때 최상 정확도.
- **ComfyUI 실행엔진 대안 — PH's Archviz x AI**(civitai 커뮤니티 워크플로, 2026-07 조회 기준 — FLUX dev 계열이라 상업 사용 시 라이선스 확인): FLUX 기반 archviz 파이프라인에 MaskEditor 인물 삽입·기존 3D 인물 자동 개선이 노드로 통합돼 있다. 단 인물 삽입은 proof-of-concept 단계이고 장면에 구워지는 방식이라, **수정 가능 레이어가 필요하면 이 스킬의 분리 레이어 방식이 우위** — 참조·비교용으로만.

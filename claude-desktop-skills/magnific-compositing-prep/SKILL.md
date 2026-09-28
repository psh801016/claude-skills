---
name: magnific-compositing-prep
description: "포토샵 3D 오브젝트 합성을 위해 실내 배경 이미지를 Magnific nanobanana 업스케일 전처리용 프롬프트로 변환한다 — 수직·수평 왜곡 최소화와 소실점 보존이 목적. '마그네픽 프롬프트', '합성 배경', '3D 합성용', '합성할 배경', '수직 수평 맞게', '합성용 업스케일' 중 하나라도 나오면 사용한다. 이미지 없이 공간 설명만으로도 실행 가능."
---

# Magnific Compositing Prep 프롬프트 메이커

포토샵 3D 합성 배경을 Magnific nanobanana 4x로 업스케일하기 위한 전처리 프롬프트 생성.
수직/수평 라인과 소실점 보존이 최우선이며, 새로운 왜곡·오브젝트 추가를 원천 차단한다.

## 발동 경계

"나노바나나"·"업스케일 프롬프트"는 **단독으로는 이 스킬을 발동시키지 않는다.**
합성·업스케일 전처리 문맥이 함께 있을 때만 이 스킬이다.

- 나노바나나 단독 이미지 생성 요청 → 이 스킬 아님
- 심리스 텍스처 목적 → `texture-prompt-maker`
- 실사화 결과물의 업스케일 설정 문의 → `interior-prompt-maker` / `arch-prompt-maker`의 엔진 선택 절
- CGI→실사화(`interior-prompt-maker`) · 조명 전환(`cinematic-exhibition-lighting`)과는
  목적이 다르다 — 이 스킬은 **합성 배경의 기하학 정확도 확보**가 목적이다.

## 전시 조명 보존 인계

- 행사·전시 조명 참고사진, 조명 설계, 합성본, 라이트 플레이트는 먼저 `cinematic-exhibition-lighting`에서 확정한다. 이 스킬은 선택된 합성본의 구조·재질·선명도 보정만 맡으며 광원 배치나 색을 다시 설계하지 않는다.
- 라이트 플레이트는 원본과 동일한 구도·픽셀 치수의 검정 바탕 효과 레이어다. Magnific 업스케일·재질 보정에 넣지 않고, 별도 레이어로 그대로 보존한다.
- 화이트·블루 등 확정된 행사 조명 톤을 중성화하거나, 빛줄기·간접광·테이블 반응을 제거하는 보정은 금지한다.

> 용어: 여기서 "nanobanana"는 **Magnific 업스케일러의 nanobanana 엔진 프리셋**을 뜻한다(원래 nano-banana는 Google Gemini 계열 이미지 모델의 별칭 — 공식명 Gemini Flash Image). SETTINGS(Creativity/Resemblance/Detail/HDR)는 Magnific UI 슬라이더 값이며 Google Gemini API 파라미터가 아니다.

## ★ as-built 실사 규칙 — 전시·행사 장면이면 필수 (2026-09-21 배선)

배경이 **전시부스·행사장·등록데스크·게이트·포토존·백월**이면 프롬프트를 쓰기 전에 읽는다:

```
C:\Users\PSH\.agents\skills\interior-prompt-maker\references\as-built-reality.md
```

**사본을 만들지 않는다 — 이 경로 하나만 본다.**

업스케일 전처리에서 특히 걸리는 것 — **업스케일러는 "지저분한 것"을 지우려 든다. 그게 실사 단서다.**

1. **폴 이음선·프로파일 띠·나사 자국·체결 자국을 보존한다.** 매끈하게 지우면 부스가 단일 벽이 된다.
2. **현수막 인필의 세로 주름과 미세 파형을 보존한다.** 특히 등록데스크 백월은 아래로 갈수록
   주름이 는다 — 완전 평면으로 펴면 실사감이 죽는다.
3. **발광 부재는 균일 발광면 그대로 둔다.** 디테일을 올린다고 프레임 안에 없던 조명기구·
   라인조명 구조를 만들어 넣지 않는다. 블룸도 원본 수준까지만.
4. **스필로 물든 바닥·천장 색을 중성화하지 않는다.** 보라빛 레드카펫, 청보라 천장 타일은
   색 보정 오류가 아니라 실제 조명 반응이다.
5. **백스테이지 가벽의 퍼티 자국·얼룩·긁힘을 새 도장면으로 되돌리지 않는다.**

## 처리 순서

1. **소스 판별** — 실사진 / CGI 렌더 구분
2. **고유 요소 추출** — 브랜드·로고 / 특징 재료·패턴 / 핵심 구조물
3. **공간 유형 파악** — 아래 목록에서 매칭
4. **PROMPT + SETTINGS + NEGATIVE(SD 대체 경로 전용) 세 섹션을 항상 이 구성으로 출력** — 설명·분석·체크리스트 없음. NEGATIVE 섹션 제목은 반드시 `NEGATIVE (SD/ComfyUI 대체 경로 전용 — Magnific/nanobanana에는 입력하지 않음)`으로 표기해 사용처 혼동을 차단한다

**절대 금지:** 카메라 브랜드(Sony, Canon, Nikon, Hasselblad 등) / MJ 파라미터(`--v`, `--ar` 등) / 절대 초점거리 mm 숫자

**NEGATIVE 사용처 (결정 규칙):** Magnific/nanobanana 실행 시 입력하는 것은 **PROMPT + SETTINGS 뿐**이다. NEGATIVE를 프롬프트에 이어붙이지 않는다 — 의미기반 엔진(nanobanana)은 부정 나열을 장면 묘사로 읽어 역효과를 내고, Magnific UI에는 NEGATIVE 전용 필드가 없다. PROMPT의 긍정형 기하학 잠금(`perfect rectilinear perspective, straight parallel lines` 등)이 억제를 대신한다. NEGATIVE 섹션은 **SD/ComfyUI 계열로 대체 실행할 때만** 그 negative 필드에 넣는 참고용이며, 출력 시 섹션 제목에 이를 명기한다.

---

## 소스 판별

**사용자가 직접 말하면** → 우선 적용
("실사야", "CGI야", "D5", "Lumion", "SketchUp", "렌더야" 등)

**CGI 렌더 소프트웨어 키워드 감지 → 즉시 CGI 처리:**
D5 Render, Lumion, SketchUp, Rhino, Revit, ArchiCAD, 3ds Max, Blender, Enscape,
V-Ray, Corona Renderer, Twinmotion, KeyShot, Cinema 4D

**이미지/설명에서 판단:**

| 실사진 신호 | CGI 렌더 신호 |
|---|---|
| 자연 노이즈·그레인 | 노이즈 없는 완벽한 텍스처 |
| 불균일한 조명·그림자 | 균일하고 이상적인 조명 |
| 소재 노화·먼지·지문 | 플라스틱처럼 매끈한 표면 |
| 생활 오브젝트·사람 | 렌더 아티팩트·ambient occlusion banding |

판단 불가 → CGI 렌더로 처리 (안전한 기본값)

---

## A. 실사진용

**목표:** 기존 기하학·텍스처를 100% 보존. 새로운 grain·aging·object 추가를 원천 차단.
4x 업스케일에서 Magnific이 빈 공간에 오브젝트를 hallucinate하지 않도록 NEGATIVE가 핵심.

### PROMPT

```
real interior photograph upscale, perfect rectilinear perspective,
plumb vertical walls, level horizontal ceiling and floor planes,
accurate vanishing points preserved, straight parallel lines throughout,
compositing-ready background plate, enhance sharpness and material clarity only,
no structural or spatial alteration, preserve all existing surfaces as-is
```

고유 요소 추가 (PROMPT 끝, 개수 제한 없음):
`preserve [위치 포함 구체 설명] exactly as in the original`

### NEGATIVE

```
barrel distortion, pincushion distortion, fisheye, curved walls, warped geometry,
bent vertical lines, tilted horizon, perspective warp, lens aberration,
added film grain, artificial noise, vignette, hallucinated texture,
artificial aging, new stains or marks, changed room geometry,
new furniture added, objects moved or removed, hallucinated objects,
new architectural elements, reframed composition, style change,
dreamlike, painterly, illustration
```

### SETTINGS (nanobanana 4x 기준)

```
Creativity : 0.1
Resemblance: 0.95
Detail     : 0.35
HDR        : 0.1
```

**Detail 조정:** 거친 재료(벽돌·콘크리트·카펫) → 0.45 / 매끈한 재료(대리석·도장벽) → 0.25
**Resemblance 조정:** 로고·사이니지 등 정밀 보존 필요 시 → 1.0

---

## B. CGI 렌더용

**목표:** CGI의 플라스틱 같은 완벽함을 실사 소재감으로 전환하되 기하학은 절대 유지.
소재 전환(Creativity ↑)을 허용하면서도 수직·수평 라인이 흔들리지 않게 기하학 키워드를 먼저 배치.

### PROMPT

```
convert CGI render to photorealistic interior photograph,
strict rectilinear geometry lock — plumb verticals, level horizontals,
accurate vanishing points unchanged, no perspective shift,
photorealistic material quality, realistic surface micro-texture,
subtle material imperfection and aging, photographic light response on surfaces,
compositing-ready photorealistic background, professional architectural photography
```

공간 유형 키워드 추가 (아래 섹션에서 선택)

고유 요소 추가 (PROMPT 끝):
`preserve [위치 포함 구체 설명] exactly as in the original`

### NEGATIVE

```
CGI look, plastic material, uniform synthetic texture, oversaturated colors,
perfectly clean non-aging surfaces, barrel distortion, pincushion distortion,
fisheye, curved walls, warped geometry, bent vertical lines,
perspective shift, lens aberration, render artifact, ambient occlusion banding,
new furniture added, objects moved, hallucinated objects,
new architectural elements, toon shading, illustration, cartoon, added film grain
```

### SETTINGS (nanobanana 4x 기준)

```
Creativity : 0.3
Resemblance: 0.80
Detail     : 0.5
HDR        : 0.2
```

**Creativity 조정:**
- 텍스처가 단순한 공간(흰 벽 오피스, 미니멀 로비) → 0.2
- 복잡한 소재가 많은 공간(연회장, 카페, 레스토랑) → 0.4 (최대)
- Creativity > 0.4는 기하학 변형 위험 — 절대 초과하지 않는다

**Detail 조정:**
- 거친 재료(카펫·벽돌·콘크리트) → 0.6
- 매끈한 재료(대리석·유리·도장면) → 0.4

---

## 공간별 재료 키워드 (CGI 렌더 전용)

→ **`references/material-keywords.md` 에 있다.** 대상 공간이 정해지면 해당 공간 항목만 읽는다.
해당 상황이면 넘기지 말고 그 파일을 반드시 읽는다.

## 고유 요소 보존

이미지 설명에서 아래 요소가 감지되면 반드시 PROMPT 끝에 추가한다.
**위치를 구체적으로 명시**해야 Magnific이 어디를 건드리지 말아야 하는지 인식한다.

| 요소 유형 | 작성 예시 |
|---|---|
| 브랜드 로고 | `preserve the Fairmont logo on the rear LED screen exactly` |
| 카펫·타일 패턴 | `preserve the floral patterned carpet color and repeat design exactly` |
| 포인트 컬러 구조물 | `preserve the blue accent wall on the left side exactly` |
| 유리·파티션 | `preserve the glass partition transparency and surface reflection exactly` |
| 특수 천장 구조 | `preserve the arched ceiling form and height exactly` |
| 사이니지·간판 | `preserve the signage text, color, and position on the wall exactly` |
| 주요 가구 배치 | `preserve the long conference table position and surface geometry exactly` |

---

## 출력 예시

→ **`references/examples.md` 에 있다.** 작성 형식이 헷갈릴 때 읽는다.
해당 상황이면 넘기지 말고 그 파일을 반드시 읽는다.


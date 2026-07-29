---
name: cinematic-exhibition-lighting
description: "Image 1의 구조·카메라·재질·그래픽을 잠그고 Image 2에서 실제로 보이는 빔 개수·광원 위치·진행 방향·팬 형태·원근 확장·색·헤이즈를 그대로 분석해 이식한다. 조명 이식, 공연장·행사장 조명, 분위기 변경, lighting transfer, exhibition lighting에 사용한다. 고보는 사용자가 현재 요청에서 명시할 때만 포함한다. 빛 전용 플레이트 요청 시 LED·구조·그래픽을 완전히 제외하고 순수 검정 위에 빔·헤이즈·고보 투사광과 빛이 실제 표면에 만든 조명 성분만 출력한다."
---

# 시네마틱 전시 조명 마스터

인테리어·건축·행사 공간에 시네마틱 전시 조명을 이식한다.
구조는 4중 완전 잠금 — 오직 조명·분위기만 변환.

## ★ 구도 보존 최우선 원칙 (실패 1순위 방지)

이 스킬은 카메라·기하학을 4중 잠금하지만, i2i 엔진 자체가 구도(화각·종횡비)를 틀 수 있다. 근본 원인은 **종횡비 불일치**다.

1. **★ 실행 전 원본을 대상 엔진이 지원하는 비율로 사전 크롭** — 엔진의 출력 비율 제약을 먼저 확인한다: **gpt-image-1 계열은 1:1 / 3:2 / 2:3 고정**이므로 원본을 미리 그 비율로 크롭해 넣고, **gpt-image-2는 제약 내 임의 해상도를 지원**하므로 원본 비율을 그대로 유지한다(불필요한 크롭 금지). 크롭으로 잘리는 면적이 15%를 넘으면 사용자에게 경고 후 진행하고(비율 맞춤 크롭에만 적용), 크롭은 목표 비율·방향을 1~2줄로 안내하거나 이미지 파일 접근이 가능하면 직접 크롭 후 진행한다. 모델이 엣지에서 공간을 발명할 여지를 없애는 유일한 구조적 해결책이다.
2. **절대 초점거리 숫자 금지** — PROMPT에 mm 숫자를 쓰지 않는다(이 스킬은 이미 미사용). "원본과 동일한 화각" 긍정형만 쓴다.
3. **Gemini·Nano Banana·Magnific 경로에서는 NEGATIVE를 넣지 않고, 본문·예시의 모든 부정문을 긍정형으로 바꾼다 (2·3·6·9·10단계 포함)** — 의미기반 모델은 부정 단락을 장면 묘사로 읽어 억제어를 오히려 그린다. 카메라/기하학 잠금의 부정문(`No camera change`, `no reframing` 등)은 긍정형(`preserve the exact same camera position, framing, field of view, and aspect ratio as Image 1, with every element occupying the same fraction of the frame, all four frame edges aligning with Image 1, and the vanishing points in the same screen positions`)으로, 6단계의 `No fantasy or illustration style`·9단계의 `not a CGI render`·10단계의 부정문 나열은 긍정형 대체문(`"a professionally photographed real-world cinematic event space, with the material fidelity and lighting physics of documentary stage photography, every material, structure, furniture piece, and screen exactly as in Image 1"`)으로 바꿔 쓴다. 이 엔진들은 PROMPT만 사용하고, 부정문 잠금·NEGATIVE는 SD/ComfyUI 디퓨전 경로 전용이다. (긍정형 변환 대상은 **이미지 생성 PROMPT 텍스트 안의 부정 표현뿐** — 이 스킬 문서의 절차·규칙 문장은 변환 대상이 아니다.)
4. **엔진 선택·검증** — 사용자가 엔진을 지정하지 않으면 Magnific / Gemini·Nano Banana / SD·ComfyUI 중 실행 엔진을 확인한다. Magnific가 지정되면 Magnific 블록만 출력한다. 조명 이식의 Magnific 기본은 Creativity 0.50 / Resemblance 0.55이며, 조명 변화가 약할 때만 Creativity를 0.05 올려 최대 0.60까지 한 번씩 시험한다. 그래픽·구조가 흔들리면 전체 프레임 값을 더 올리지 않고 조명 대상 ZONE B 크롭/마스크로 전환한다. 결과 위에 원본 50% 오버레이로 소실점·모서리 일치를 확인한다.

## 출력 모드

| 모드 | 트리거 | 출력 |
|---|---|---|
| **메인 변환** | 기본 (조명 변환 요청) | 선택 엔진 전용 완성 장면 PROMPT. Magnific는 입력 원본을 보존하는 경로이므로 완성 장면만 출력한다. 빛 분리 플레이트는 검정 빈 캔버스를 직접 입력할 수 있는 별도 생성 경로에서만 출력 |
| **빛 전용 플레이트** | "빛만", "빛줄기만", "빛 따로", "조명 패스", "light-only" | 순수 검정 바탕 위에 빔·헤이즈·입자·조사된 표면 광량만 남긴 독립 PROMPT. LED·스크린·글자·로고·기본 구조는 0. 고보는 현재 요청에 명시됐을 때 투사 콘과 투사광까지 포함 |
| **조명 레이어 세트(4분리)** | "레이어 세트", "조명 나눠서", "따로 컨트롤", "L1", "L2", "L3", "L4" | `references/lighting-layer-set.md` 규격으로 L1 빔 / L2 헤이즈 / L3 스팟 풀 / L4 컬러 워시를 각각 별도 PROMPT로 출력 + 블렌드 가이드. `person-layer-maker`의 조명 샌드위치가 이 L1~L4를 참조한다 |
| **익스트림 다크** | "극단적으로 어둡게", "실루엣만", "빛만 살려", "나머지 다 블랙", "어둡게 눌러", "다크 실루엣", "Magnific 다크" | EXTREME DARK PROMPT + NEGATIVE + MAGNIFIC SETTINGS |

**출력 범위:** 기본 산출물은 빛이 무대·바닥·객석·벽·테이블에 맺히는 반사·굴곡·스팟 풀·림라이트·색광 스필을 포함한 완성 장면이다. 빛 전용 플레이트는 별도의 독립 출력이며 Image 1을 위치·원근·표면 수광 마스크로만 사용한다. 프레임 전체의 기본값은 순수 검정이고 조명 에너지에 해당하는 픽셀만 남긴다. 엔진이 원본 구조나 LED 콘텐츠를 남기면 실패로 판정하고 검정 캔버스·원본 마스크·레이어 합성 경로로 다시 만든다. 결과는 후처리에서 Screen 또는 Linear Dodge(Add)로 합성한다.

## ★ 빛 전용 플레이트 절대 출력 계약

이 절은 빛 전용 요청에서 메인 변환·LED 보존·재질 보존 문장보다 우선한다.

1. **검정 기본값:** 프레임 전체를 균일한 순수 검정 RGB 0,0,0으로 만든다.
2. **LED 완전 제외:** 중앙·측면 LED 패널, 화면 콘텐츠, 행사명, 한글·영문 글자, 로고, 그래픽, 패널 발광, 화면 잔광과 화면 반사를 모두 출력 성분에서 제거한다. LED 위치는 빔 정렬을 위한 내부 좌표로만 사용하고 결과 픽셀에는 나타내지 않는다.
3. **공중 조명 성분:** Image 2에서 읽은 빔 전체 경로, 발광 코어, 헤이즈, 미세 입자, 자연스러운 감쇠를 원래 위치와 원근으로 남긴다.
4. **표면 조명 성분:** 빔이 실제로 때린 부분의 광량만 남긴다. 의자 상단·외곽의 림라이트, 패브릭에 흡수된 색광, 테이블보의 국소 반사, 중앙 통로·카펫·바닥·무대 데크의 스필·스팟 풀·길게 늘어진 반사, 벽면의 조사광을 포함한다. 빛이 닿지 않은 물체의 기본색·윤곽·재질·그림자는 순수 검정으로 사라진다.
5. **연결성:** 각 공중 빔과 그 아래 실제 수광 흔적을 하나의 물리적으로 연결된 조명 사건으로 표현한다. 빔만 공중에 떠 있고 의자·바닥의 조사광이 없는 결과는 실패다.
6. **고보 옵트인:** 사용자가 현재 요청에서 고보를 명시하면 고보 투사광뿐 아니라 실제 프로파일 광원에서 벽까지 이어지는 희미한 체적 투사 콘도 남긴다. 고보 필드·문자·문양은 반투명 광량으로만 보이고 그 밖의 벽은 순수 검정이다. 고보가 명시되지 않으면 관련 광량은 0이다.
7. **합성 안전:** 기본 공간, 사람, 가구, 천장, 벽, 스크린을 재현하는 미용 이미지를 만들지 않는다. 오직 가산 합성 가능한 조명 성분만 출력한다.

빛 전용 의미기반 모델용 핵심 문장:
> `"Create a pure additive lighting pass on uniform RGB 0,0,0 black. The only visible pixels are the complete volumetric beams, illuminated haze and particles, optional requested gobo projection cones and projected gobo light, plus the physically aligned light contribution deposited on chair edges, fabric table covers, carpet, aisle, floor, stage deck and wall surfaces. The central and side LED screens, screen artwork, event title, typography, logos, panel glow and screen reflections contribute zero visible pixels."`

**★ 고보 완전 옵트인:** 고보 조명은 이 스킬의 기본 조명 구성에 포함하지 않는다. 사용자가 **현재 요청에서** `고보`, `gobo`, `문양 투사`, `행사명 투사`처럼 고보 사용을 명시한 경우에만 추가한다. 이전 요청이나 이전 결과에 고보가 있었더라도 다음 요청으로 자동 승계하지 않고 매 요청마다 고보 상태를 OFF로 초기화한다. 사용자가 고보를 명시하지 않은 기본 조명 프롬프트와 빛 전용 플레이트에는 원형 고보, 패턴 고보, 텍스트 고보, 로고 고보를 모두 넣지 않는다.

## ★ Image 2 빔 형태 충실 이식 (최우선 규칙)

이 절은 아래의 범용 빔 예시·색온도 예시보다 우선한다. Image 2가 있으면 임의의 `3~5개 수직빔`, 중앙 하향빔, 교차빔, 사이드 워시를 기본값으로 섞지 않는다. **Image 2에서 실제로 관찰되는 빔 서명만 이식한다.**

1. **역할 고정:** Image 1은 최종 장면의 유일한 카메라·구조·재질·가구·그래픽·고보 정본이다. Image 2는 빔 조명 전용 레퍼런스이며 구조·스크린·텍스트·로고·가구를 가져오지 않는다.
2. **빔 서명 추출:** 프롬프트를 쓰기 전에 Image 2에서 다음을 하나의 세트로 읽는다: `빔 개수`, `실제 광원/트러스 위치`, `카메라 기준 진행 방향`, `도착점 또는 프레임 이탈점`, `팬·교차·수직·사이드 배열`, `좌우 대칭`, `색 분포`, `코어 밝기`, `가장자리 부드러움`, `헤이즈 밀도`, `원근에 따른 폭 변화`.
3. **방향을 화면상 모양으로 명시:**
   - **전방 방사형 / 카메라 방향:** 무대 뒤·상부 트러스에서 좁게 시작하고 객석·카메라 쪽으로 진행하면서 넓어지며, 화면의 상단 또는 좌우 바깥으로 이어진다. 빔 끝을 무대 바닥·LED·백월에 닫지 않는다.
   - **하향형:** 천장 광원에서 무대·바닥의 실제 스팟 풀까지 이어진다.
   - **교차형·사이드형:** Image 2의 실제 시작점과 교차점 또는 벽면 도착점을 그대로 기술한다.
4. **형태 우선:** 사용자가 밝기·어둠·색 강도를 조정해도 빔 개수·출발점·진행 방향·팬 형태·원근 확장은 Image 2와 동일하게 유지한다. 밝기 조정 때문에 빔 전체가 사라지지 않도록 `"keep every complete beam path visible from its source to its frame exit or physical landing point"`를 함께 쓴다.
5. **물리 광원 매핑:** Image 1에 실제로 보이는 기존 무빙헤드·프로파일 조명·트러스 위치 중 Image 2의 빔 서명을 가장 자연스럽게 재현하는 위치에 매핑한다. 사용자가 장비 추가를 요구하지 않은 상태에서는 새 바닥 조명기구·새 트러스·새 스피커 타워를 발명하지 않는다.
6. **참조 우선 문장:** Image 2가 있을 때 메인 프롬프트에 아래 의미를 짧고 강하게 넣는다.
   > `"Use Image 2 solely as the beam-lighting reference. Transfer its complete beam signature onto Image 1: the observed beam count, source positions, camera-relative travel direction, fan geometry, frame exits or landing points, colors, perspective expansion, luminous intensity, haze density and edge softness."`
7. **실패 방지:** `preserve the beams`처럼 추상적으로만 쓰지 않는다. Image 2가 전방 방사형인데 `aim toward the stage/backwall`처럼 반대 방향을 쓰지 않는다. 여러 조명 레이아웃을 동시에 제안하지 않는다.

## ★ 사용자가 승인한 광학 품질 기준

- `assets/forward-beam-quality-reference.png`는 사용자가 승인한 **광학적 완성도 참고**다. 조명 배치 템플릿이 아니다.
- 전방 방사형 빔이 포함된 작업에서는 `references/forward-beam-quality-reference.md`를 읽어 빔 깊이감, 원근 확장, 헤이즈 질감, 시인성 및 홀 노출 균형을 맞춘다.
- 매 작업의 빔 개수·광원 위치·방향·팬 형태·색·끝점은 승인 이미지가 아니라 **현재 Image 2**에서 새로 추출한다.
- Image 2가 다른 빛 형태를 보여주면 그 형태를 유지하며 승인 이미지 수준의 물리적 빛 표현만 적용한다.
- 고보는 승인 이미지나 참고 문서에 보이더라도 자동 포함하지 않는다. 사용자가 현재 요청에서 명시한 경우에만 아래 고보 분기를 활성화한다.

## ★ 고보 요청 시 처리

고보가 현재 요청에서 명시된 경우에만 아래 분기를 사용한다.

- **Image 1의 기존 고보 유지 요청:** Image 1을 고보의 유일한 정본으로 사용한다. 위치·크기·원형/타원형 필드·색·밝기·내용·부드러움·벽 질감 반응을 그대로 잠근다. 원본 고보 글자가 이미 보이면 프롬프트에 행사명을 다시 타이핑하지 않는다. 행사명을 재기입하면 모델이 고보 대신 대형 벽면 사인·슬로건을 만들 수 있다.
- **새 고보 생성 요청:** 기존 천장 프로파일 조명에서 벽으로 이어지는 희미한 투사 콘, 내부가 채워진 낮은 대비의 원형/타원형 광 필드, 반투명 글자, 장거리 초점 흐림, 불균일한 광량, 벽 타공·이음·질감이 글자를 통과해 보이는 상태를 기술한다. 모든 글자는 투사 필드 내부에만 배치한다.
- **고보가 Image 2에만 보이는 경우:** 사용자가 현재 요청에서 고보를 명시하지 않았다면 이식하지 않는다.
- **고보와 빔 분리:** 고보의 밝기·초점·내용을 조정해도 Image 2 빔 서명은 바꾸지 않는다. 빔과 고보를 각각 독립 잠금한다.

## ★ 프롬프트 간결성 및 복사 형식

- 한 번의 프롬프트에는 사용자가 요청한 변화와 필요한 잠금만 넣는다. 같은 텍스트·로고·실패 금지어를 반복해 모델의 재생성 주의를 높이지 않는다.
- 프롬프트는 의미상 하나의 영어 지시문으로 유지하되, 사용자가 내용을 읽고 복사할 수 있도록 문장 단위 줄바꿈을 허용한다.
- 완성 장면과 빛 전용 플레이트를 함께 요청하면 **서로 분리된 두 개의 코드 블록**으로 출력한다. 각 블록은 독립적으로 복사해 사용할 수 있어야 한다.
- 빛 전용 플레이트는 완성 장면 프롬프트와 한 블록에 섞지 않는다. Image 1은 위치·원근·수광 마스크로만 참조하고 출력은 순수 검정 위 조명 성분으로 제한한다.
- 사용자가 UI에 존재한다고 확인하지 않은 Creativity·Resemblance 같은 설정값은 출력하지 않는다.

## 빠른 흐름

1. **출력 모드 판단** (위 표 참조)
2. **입력 확인**: Image 1 (원본) + Image 2 (조명 레퍼런스, 선택) + 색온도 키워드 (선택) — Image 1이 없으면 프롬프트를 지어내지 말고 원본 이미지를 요청한다.
2-1. **(구도 보존 중요 시) 사전 크롭 안내**: 대상 엔진 비율 확인 후 크롭 안내 또는 직접 크롭 — 위 "구도 보존 최우선 원칙" 1
3. **실행 엔진 확인**: 엔진 미지정 시 먼저 묻는다. Magnific 지정 시 Magnific 블록만, Gemini·Nano Banana 지정 시 PROMPT만, SD·ComfyUI 지정 시 PROMPT+NEGATIVE만 만든다.
4. **Image 2 조명 분석** (아래 "조명 추출 가이드" 참조) — **Image 2가 없으면** 조명 분석을 생략하고 색온도 판단표의 기본값(Neutral Cinematic)으로 진행하며, 1단계·6단계 문장에서 Image 2 참조를 제거한 대체 문장을 쓴다(아래 각 단계 참조)
5. **색온도 판단** (아래 색온도 판단표 참조)
6. **메인 변환** → 엔진 전용 완성 장면 조명 PROMPT 작성. 빛 전용 요청이면 별도 `LIGHT-ONLY PLATE PROMPT`를 작성하며 위 절대 출력 계약을 적용한다.
7. **익스트림 다크** → EXTREME DARK PROMPT + NEGATIVE + Magnific 설정값

카메라 브랜드(Sony, Canon, Hasselblad 등) 절대 명시하지 않는다.
MJ 파라미터(`--v`, `--iw`, `--ar` 등) 절대 포함하지 않는다.

## 출력 원칙

설명·분석·주석·이미지 생성 없음. 프롬프트 섹션만 출력.
단, 예외 2가지: (a) 사전 크롭이 필요한 경우 크롭 안내(목표 비율·방향) 1~2줄 허용, (b) 필수 입력(Image 1)이 없으면 프롬프트를 지어내지 말고 이미지를 요청.
모든 PROMPT는 의미상 **하나의 연속된 영어 지시문**으로 작성한다. 사용자가 읽고 복사하기 쉽도록 문장 단위 줄바꿈을 허용하며, 서로 다른 프롬프트는 반드시 별도 코드 블록으로 분리한다.

**Magnific 메인 변환 출력 형식 — 이 블록만 출력:**
```
MAGNIFIC PROMPT
[영어 프롬프트, 긍정형만 사용, 문장 단위 줄바꿈 허용]
```
사용자가 빛 전용 플레이트도 요청했으면 `LIGHT-ONLY PLATE PROMPT`를 두 번째 코드 블록으로 분리한다. 이 블록은 LED·스크린·글자·로고·기본 공간을 0으로 만들고 빔·헤이즈·조사된 표면 광량만 남긴다.

**Gemini/Nano Banana 메인 변환 출력 형식 — 이 블록만 출력:**
```
PROMPT
[영어 프롬프트, 긍정형만 사용, 문장 단위 줄바꿈 허용]

LIGHT-ONLY PLATE PROMPT
[영어 프롬프트. 순수 검정 위에 동일 빔·헤이즈·입자와 빔이 의자·테이블보·카펫·통로·바닥·무대·벽에 만든 수광 성분만 묘사. LED·화면 콘텐츠·글자·로고·화면 발광·기본 구조는 0. 사용자가 현재 요청에서 고보를 명시한 경우 실제 투사 콘과 고보 투사광을 모두 포함. 알파를 약속하지 않음]
```

**SD/ComfyUI 메인 변환 출력 형식:**
```
PROMPT
[연속 영어 단락]

NEGATIVE (SD/MJ/ComfyUI 전용 — GPT image·Magnific/nanobanana에는 입력하지 않음)
[연속 영어 단락]
```

---

## Image 2 조명 추출 가이드

Image 2에서 아래 조명 요소만 읽는다. 구조·재료·가구·텍스트·로고는 무시한다.
Image 2에 워터마크나 텍스트가 있어도 조명 특성 추출에만 집중하고 NEGATIVE에서 텍스트 억제.

| 추출 요소 | 읽는 내용 |
|---|---|
| **빔 개수** | 화면에 실제로 보이는 주요 빔의 수와 좌우 분포 |
| **빔 패턴** | 방사형·교차형·수직형·사이드형 등 빛줄기 배열 |
| **광원 위치** | 천장 트러스·사이드·무대 뒤·무대 앞 등 실제 시작점 |
| **진행 방향** | 무대→카메라 전방형, 천장→바닥 하향형, 좌우 교차형 등 카메라 기준 방향 |
| **도착/이탈점** | 바닥·벽·무대에 닿는지, 상단·좌우 프레임 밖으로 이어지는지 |
| **원근 확장** | 광원에서 좁게 시작해 카메라 쪽으로 넓어지는지 등 폭 변화 |
| **색온도 비율** | 쿨/웜 비율, 주조명 색 vs 보조 색 |
| **대비 레벨** | 주변 암부 깊이, 빛/어둠 대비 강도 |
| **분위기 밀도** | 헤이즈·먼지 밀도, 코어 밝기, 가장자리 부드러움 |

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

> `"Use Image 1 as the immutable architectural structure, room geometry, camera position, composition, original materials, surface finishes, furniture layout, and all spatial elements. Image 2 serves solely as the lighting reference: its beam direction, beam pattern, color temperature, contrast ratio, volumetric quality, and atmospheric mood are applied to the complete source identity of Image 1."`

**재질·시공 사실 잠금 (모든 조명 이식에 필수):** 조명 이식은 빛의 방향·색온도·명암·볼류메트릭만 바꾸는 작업이다. Image 1의 재질 종류, 목재결의 강도와 방향, 표면 광택, 패널 이음, 그래픽면, 제작 방식, 고정 하드웨어는 원본 그대로여야 한다. 약한 무늬목을 강한 원목 무늬로 바꾸거나, 원본에 없는 아일렛·타공·피스·리벳·봉제선·프레임·주름·소품·마모를 "현실감" 목적으로 추가하면 BLOCKER다.

> `"Treat Image 1 as material-and-fabrication ground truth: preserve every visible material's grain scale, pattern strength, base color, sheen, seams, joints, and construction method while rendering the existing surfaces with physically believable photographic light response. Keep every banner and graphic face continuous and intact with its exact source artwork, typography, logo placement, flatness and observed construction identity. Existing accessories and fabrication details remain the observed set."`

전시 그래픽·현수막은 AI가 다시 그리는 재질이 아니라 원본 아트워크를 최상단 마스크/오버레이로 복원하는 대상이다. 원본에 타공 또는 고정 하드웨어가 명백히 보일 때에만 그 위치·개수·크기를 동일하게 유지한다.

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

> `"Preserve the original materials, surface finishes, textures, intrinsic color palette, furniture layout, furniture design, seating arrangement, object placement, and observed fixture set exactly as they appear in Image 1. The lighting transformation reveals those existing surfaces through physically believable light absorption, highlight roll-off, reflection falloff, localized indirect bounce and grounded contact shadows."`

**LED 스크린·디지털 디스플레이가 있는 경우 추가:**
> `"Preserve the LED screen and display panel structures, frame positions, placement, scale, source artwork, typography and logos. Render each active source screen as an emissive display surface whose existing colors create controlled local illumination on only the immediately adjacent source surfaces, with natural luminance falloff and no change to the source content."`

**평면 LED월 + 무대 데크(원본에 둘 다 있을 때 필수):** LED가 단순 인쇄 그래픽처럼 남지 않게, 아래 문장을 메인 조명 PROMPT에 반드시 추가한다.
> `"The active central flat LED wall casts a controlled [source screen color] horizontal specular reflection band across the existing [source-confirmed semi-gloss or polished] stage deck directly below it, brightest at the screen base and naturally fading toward the audience. A faint localized colored bounce reaches only the stage edge and immediately adjacent first-row surfaces while the rest of the hall retains its intrinsic material colors."`

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

Image 2가 있으면 위 `Image 2 빔 형태 충실 이식`에서 추출한 **전체 빔 서명**을 반영하여 작성한다. `dramatic`, `strong`, `multiple` 같은 추상어만으로 대체하지 않는다.

> `"Use Image 2 solely as the beam-lighting reference and transfer its complete observed beam signature onto Image 1: [실제 빔 개수와 좌우 분포], originating from [실제 광원 위치], travelling [카메라 기준 진행 방향], reaching [실제 도착점 또는 프레임 이탈점], arranged as [실제 팬·교차·수직·사이드 형태], with [실제 색 분포], [실제 원근 폭 변화], [실제 코어 밝기와 가장자리 부드러움], and [실제 헤이즈 밀도]. Keep every complete beam path visible from its source to its frame exit or physical landing point while preserving the complete source identity of Image 1."`

**Image 2 없는 경우:** 사용자가 구체적인 빔 형태를 말했으면 그 형태만 사용한다. 사용자가 형태를 지정하지 않았으면 공간에 실제로 보이는 기존 조명기구를 기준으로 절제된 Neutral Cinematic 조명을 작성하고, 임의의 전방 방사형·중앙 수직빔·다수 교차빔을 자동 추가하지 않는다.

빔 패턴 묘사 예시:
- 방사형: `"fan-radiating beam pattern from overhead ceiling truss"`
- 교차형: `"crossing diagonal beam spotlights from left and right ceiling positions"`
- 수직 집중: `"tight vertical spotlights from ceiling grid focused on stage area"`
- 사이드 플러드: `"side-wash beams from left and right wall positions"`

**무대 조명 효과 어휘 (Image 2 분석·요청에 맞춰 선택 — 겹치는 발광 토큰 최소화):**
- 빔/워시/스팟 구분: `sharp defined beam` (빔) / `broad soft color wash across the wall` (워시) / `focused light pool on the floor or subject` (스팟)
- 백라이트·림: `strong backlight from behind the stage creating rim highlights on subject edges`
- LED 월 글로우: `soft screen-glow spill from the LED wall onto nearby floor and subjects` (스크린 콘텐츠 자체는 잠금 유지)
- 고보 패턴(현재 사용자 요청에서 명시했을 때만): `patterned gobo light texture projected on the floor` — Image 2에 고보가 보여도 사용자가 현재 요청에서 고보를 요구하지 않았으면 추출·이식하지 않는다.
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
changed composition, reframed shot, perspective reinterpretation, altered focal length feel
```
**주의:** `zoomed-in composition`, `distorted wide-angle view`처럼 **결과 장면을 직접 묘사·호명하는 토큰은 넣지 않는다** — 의미기반 모델에서 오히려 그 장면을 그리게 만든다. '변형 행위'를 명명하는 토큰(`changed/altered X`)만 사용한다(판별 기준은 interior-prompt-maker 카메라 카테고리와 동일).

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

## 예시

아래 예시는 문장 구조와 잠금 범위만 참고한다. 예시 안의 `multiple directional crossing spotlights`, 색온도, 빔 개수·방향을 새 작업에 복사하지 않는다. 새 작업의 빔 형태는 항상 사용자의 현재 지시와 `Image 2 빔 형태 충실 이식` 절에서 새로 추출한다.

> **※ 아래 메인 변환 예시들은 SD/디퓨전 경로용(부정문 카메라 잠금·NEGATIVE 포함). GPT image 경로에서는 NEGATIVE를 빼고 PROMPT만 쓰며, 본문의 부정문 카메라/기하학 잠금(`No camera change`, `no reframing` 등)을 긍정형으로 바꾼다 — 위 "구도 보존 최우선 원칙" 3 참조.**

### Warm Amber — 거실 공간

```
PROMPT
Use Image 1 as the immutable architectural structure, room geometry, camera position, composition, original materials, surface finishes, furniture layout, and all spatial elements. Extract ONLY the lighting direction, beam pattern, color temperature, contrast ratio, volumetric quality, and atmospheric mood from Image 2 — do not transfer any structural, material, spatial, stylistic, or textual content from Image 2. Preserve exactly the original camera position, camera height, viewing angle, lens perspective, focal length feel, framing, crop, composition, horizon line, and perspective alignment from Image 1. No camera change, no reframing, no recropping, no zoom change, no perspective reinterpretation. Preserve exactly the original room proportions and spatial hierarchy from Image 1. Preserve the original ceiling height, ceiling shape, and architectural ceiling structure. Preserve all wall positions, partitions, and architectural boundaries. Preserve window placement, door positions, and circulation paths. Do not move, scale, rotate, deform, or reinterpret any architectural element. Preserve the original materials, surface finishes, textures, and color palette of all elements exactly as they appear in Image 1. Preserve the original furniture layout, furniture design, and object placement. Do not substitute, replace, or alter any material, finish, furniture piece, or object. Dark cinematic exhibition rendering of the original residential living room with all original elements preserved. Apply dramatic exhibition-grade lighting with strong volumetric light beams visible in the air, using directional spotlights from ceiling and side angles referencing the lighting composition of Image 2. Include subtle dust particles floating within the light rays to enhance depth and atmospheric realism. Add refined sparkling highlights on reflective surfaces, generating soft shimmering glints without overexposure or neon effects. Controlled glossy reflections and premium museum-grade lighting quality. High contrast between deep surrounding darkness and focused light pools. No fantasy or illustration style. Apply warm amber color temperature throughout the dramatic spotlights and ambient atmosphere. Use rich warm ambers, deep golds, and brown-toned darkness for volumetric beams and spotlight illumination. Warm-toned shadows with golden ambient fill and luxurious amber-gold atmospheric depth. Maintain all original surface micro-details from Image 1 including material grain, seams, joint lines, and edge conditions. The final result must feel like a professionally photographed cinematic event space — ultra-realistic photo quality. True photographic realism. No render look, no archviz appearance, completely believable real-world cinematic photograph. No material changes from Image 1, no structural changes from Image 1, no furniture or object changes from Image 1.

NEGATIVE (SD/MJ/ComfyUI 전용 — GPT image·Magnific/nanobanana에는 입력하지 않음)
cartoon, anime, illustration, sketch, watercolor, concept art, matte painting, stylized, painterly, fantasy, sci-fi, surreal, CGI, archviz look, render look, Unreal Engine look, Blender render look, SketchUp look, clay render, plastic rendering, fake global illumination, changed camera angle, changed viewpoint, changed perspective, changed framing, reframed shot, changed room geometry, changed ceiling height, changed wall positions, changed window placement, distorted room, warped walls, deleted architectural elements, moved walls, changed materials, replaced materials, material transfer from Image 2, style transfer from Image 2, changed floor finish, changed wall material, new furniture added, replaced furniture, moved furniture, repositioned objects, neon lights, excessive bloom, overexposed spotlights, blown highlights, halo effects, fake lens flares, flat fill lighting, bright daylight, natural daylight, original lighting unchanged, mirror glass, impossible reflections, fake reflections, random text, logo, watermark, watermark from reference image, fantasy elements, magical atmosphere, impossible physics, copied geometry from Image 2, structural content from reference image
```

### Cool Blue — 오피스 공간

```
PROMPT
Use Image 1 as the immutable architectural structure, room geometry, camera position, composition, original materials, surface finishes, furniture layout, and all spatial elements. Extract ONLY the lighting direction, beam pattern, color temperature, contrast ratio, volumetric quality, and atmospheric mood from Image 2 — do not transfer any structural, material, spatial, stylistic, or textual content from Image 2. Preserve exactly the original camera position, camera height, viewing angle, lens perspective, focal length feel, framing, crop, composition, horizon line, and perspective alignment from Image 1. No camera change, no reframing, no recropping, no zoom change. Preserve exactly the original room proportions and spatial hierarchy from Image 1. Preserve the original ceiling height, ceiling shape, and architectural ceiling structure. Preserve all wall positions, partitions, and architectural boundaries. Preserve window placement, door positions, and circulation paths. Do not move, scale, rotate, deform, or reinterpret any architectural element. Preserve the original materials, surface finishes, textures, and color palette of all elements exactly as they appear in Image 1. Preserve the original furniture layout, furniture design, and object placement. Do not substitute, replace, or alter any material, finish, furniture piece, or object. Exhibition-quality dramatic lighting transformation of the original office workspace, all materials and furniture unchanged. Apply dramatic exhibition-grade lighting with strong volumetric light beams visible in the air, using directional spotlights from ceiling and side angles referencing the lighting composition of Image 2. Include subtle dust particles floating within the light rays to enhance depth and atmospheric realism. Add refined sparkling highlights on reflective surfaces, generating soft shimmering glints without overexposure or neon effects. Controlled glossy reflections and premium stage-grade lighting quality. High contrast between deep surrounding darkness and focused light pools. No fantasy or illustration style. Apply deep cool blue color temperature throughout the dramatic spotlights and ambient atmosphere. Use deep blues, crisp silvers, and cold white light for volumetric beams and spotlight illumination. Cool-toned shadows with icy ambient fill and sophisticated blue-silver atmospheric depth. Maintain all original surface micro-details from Image 1 including material grain, seams, joint lines, and edge conditions. The final result must feel like a professionally photographed cinematic event space — ultra-realistic photo quality. True photographic realism. No render look, no archviz appearance, completely believable real-world cinematic photograph. No material changes from Image 1, no structural changes from Image 1, no furniture or object changes from Image 1.

NEGATIVE (SD/MJ/ComfyUI 전용 — GPT image·Magnific/nanobanana에는 입력하지 않음)
cartoon, anime, illustration, sketch, watercolor, concept art, matte painting, stylized, painterly, fantasy, sci-fi, surreal, CGI, archviz look, render look, Unreal Engine look, Blender render look, SketchUp look, clay render, plastic rendering, fake global illumination, changed camera angle, changed viewpoint, changed perspective, changed framing, reframed shot, changed room geometry, changed ceiling height, changed wall positions, changed window placement, distorted room, warped walls, deleted architectural elements, moved walls, changed materials, replaced materials, material transfer from Image 2, style transfer from Image 2, changed floor finish, changed wall material, new furniture added, replaced furniture, moved furniture, repositioned objects, neon lights, excessive bloom, overexposed spotlights, blown highlights, halo effects, fake lens flares, flat fill lighting, bright daylight, natural daylight, original lighting unchanged, mirror glass, impossible reflections, fake reflections, random text, logo, watermark, watermark from reference image, fantasy elements, magical atmosphere, impossible physics, copied geometry from Image 2, structural content from reference image
```

### Mixed (Cool Blue + Warm Amber) — 컨퍼런스홀 (검증된 예시)

```
PROMPT
Use Image 1 as the immutable architectural structure, room geometry, camera position, composition, original materials, surface finishes, furniture layout, and all spatial elements. Extract ONLY the lighting direction, beam pattern, color temperature, contrast ratio, volumetric quality, and atmospheric mood from Image 2 — do not transfer any structural, material, spatial, stylistic, or textual content from Image 2. Preserve exactly the original camera position, camera height, wide-angle viewing angle, lens perspective, focal length feel, framing, crop, composition, horizon line, and perspective alignment from Image 1. No camera change, no reframing, no recropping, no zoom change, no perspective reinterpretation. Preserve the original wide-angle interior lens feel without altering spatial perspective. Preserve exactly the original room proportions and spatial hierarchy from Image 1. Preserve the original ceiling height, white geometric coffered grid ceiling structure, soffits, recessed lighting strips, and all architectural ceiling elements. Preserve all wall positions, side wall panels, and architectural boundaries. Maintain the original floor level and light oak flooring. Preserve the elevated stage platform with steps, center LED main screen, two side LED branded panels, all seating rows, and center-hung projector. Preserve all LED screen and display panel structures and frame positions. Do not move, scale, rotate, deform, simplify, delete, or reinterpret any architectural or spatial element. Preserve the original materials, surface finishes, and color palette of all elements exactly as they appear in Image 1 — white coffered ceiling, beige textured wall panels, light oak floor, deep blue fabric chair upholstery, LED screen surfaces. Preserve the original seating arrangement and all object placement. Do not substitute, replace, or alter any material, finish, seating unit, or object. Cinematic event-grade lighting transformation of the original conference hall with all seating, screens, and architectural structure preserved. Apply dramatic exhibition-grade lighting with strong volumetric light beams visible in the air, using multiple directional crossing spotlights radiating from the ceiling truss referencing the fan-beam radiating pattern of Image 2. Include subtle haze and dust particles floating within the light rays to enhance depth and atmospheric realism. Add refined sparkling highlights on the LED screen surfaces, metallic trim elements, and reflective floor, generating soft shimmering glints without overexposure or neon effects. Ensure controlled glossy reflections on the polished floor surface and premium stage lighting quality. Maintain high contrast between the deep surrounding darkness and focused light pools illuminating the stage and seating areas. No fantasy or illustration style — cinematic professional conference event hall mood only. Apply a cinematic mixed color temperature with dominant cool blue primary spotlights and warm amber secondary accent lights. Deep blue volumetric main beams from ceiling, warm gold side accent illumination at lower positions, creating layered depth and premium event-lighting atmosphere. Cool-dominated overall mood with warm accent counterpoints. Maintain all original surface micro-details from Image 1 including ceiling panel joints, seat row spacing, stage edge detailing, floor seam lines, and wall panel texture. The final result must feel like a professionally photographed cinematic conference event space — ultra-realistic photo quality with dramatic stage-grade lighting and atmosphere. True photographic realism, not a CGI render or digital composite. No render look, no archviz appearance, no plastic materials, no fake reflections, no Unreal Engine look. Completely believable real-world cinematic photograph. No material changes from Image 1, no structural changes from Image 1, no seating changes from Image 1.

NEGATIVE (SD/MJ/ComfyUI 전용 — GPT image·Magnific/nanobanana에는 입력하지 않음)
cartoon, anime, illustration, sketch, watercolor, concept art, matte painting, stylized, painterly, fantasy, sci-fi, surreal, CGI, archviz look, render look, Unreal Engine look, Blender render look, game-engine look, SketchUp look, Rhino viewport look, clay render, white model, obvious 3D render, artificial rendering, synthetic lighting, fake global illumination, plastic rendering, changed camera angle, changed viewpoint, changed perspective, changed framing, changed crop, changed composition, reframed shot, perspective reinterpretation, altered focal length feel, zoomed-in composition, zoomed-out composition, changed room geometry, changed room proportions, changed ceiling height, changed white coffered ceiling structure, changed wall positions, changed floor level, changed stage position, changed screen placement, distorted room, enlarged room, warped walls, melted architecture, deleted architectural elements, moved walls, moved stage, added structural elements, missing ceiling elements, changed materials, replaced materials, upgraded materials, recolored surfaces, material transfer from Image 2, style transfer from Image 2, changed floor finish, changed wall material, changed ceiling material, changed seat color, changed upholstery, new furniture added, replaced furniture, moved seating rows, repositioned objects, removed LED panels, added stage equipment, speaker towers added, truss structures added, lighting rigs added, scaffolding added, added concert equipment, neon lights, LED strip overexposure, excessive bloom, overexposed spotlights, blown highlights, halo effects, fake lens flares, glowing corners, flat fill lighting, equally lit entire space, bright daylight, natural daylight, original white ceiling lighting preserved, original fluorescent even lighting, mirror glass, impossible reflections, floating reflections, fake reflections, random text, logo added, watermark, watermark from reference image, stock photo watermark, exhibition labels, fantasy elements, magical atmosphere, surreal lighting, impossible physics, holographic elements, copied geometry from Image 2, structural content from reference image, spatial layout from reference image, concert stage equipment added
```

---

## 익스트림 다크 모드 (Magnific img2img 전용)

### 개념

**빛이 닿는 곳은 살리고, 빛이 안 닿는 곳만 어둠에 잠기는 모드.** 스포트라이트 빔이 압도적 주인공이지만 — **빔이 무대 데크·의자·벽·바닥에 만드는 빛효과(스팟풀·표면 반사·림라이트·색광 스필)는 반드시 살아있어야 한다.** Magnific nanobanana / Nano Banana Pro img2img에 최적화.

> **★★ 가장 흔한 실패 = "빛만 남기고 다 블랙"을 완전 실루엣 blackout으로 오해하는 것 (2026-07-13 ASURA 반복 질책).** "빛만 남긴다"의 진짜 의미: **빛 안 닿는 곳만 어둠, 빛이 물체에 묻는 효과는 살린다.** 아래 2가지 모두 반려된 실패다 —
> - ❌ 순수 블랙 배경에 빔만 떠있는 결과 → 물체 상호작용이 없어 "죽은 그림".
> - ❌ 공간을 완전 실루엣으로 눌러 `no surface detail, no color, no texture` → 빛 묻음까지 죽여 반려.
> - ✅ **원본을 넣는 img2img** — 빔 + 빛이 닿는 표면의 스팟풀·반사·림·색광 스필은 재질별로 살아있고, 빛 안 닿는 곳만 딥 섀도(faint form 유지, 완전 컷아웃 금지).

> **★ 이 모드는 '4중 잠금' 모드가 아니다 — 무드 강화 img2img다.** Resemblance를 낮추면 표면 디테일·색감이 변한다. **물체·구조를 유지하려면 Resemblance 0.5~0.55**(아래 설정값 참조). 색감·디테일이 크게 변할 수 있음을 사용자에게 한 줄 경고한다.

### ★★ 입력 판별 최우선 — 조명 보존 모드 vs 조명 생성 모드 (2026-07-13 ASURA 반복 질책)

**가장 큰 실패 = 이미 조명이 입혀진 입력의 조명을 익스트림 다크가 재발명해 원본과 틀어지는 것.** 익스트림 다크는 입력 이미지에 따라 두 모드로 갈린다 — 실행 전 Image 1을 보고 반드시 판별한다:

| 모드 | 진입 조건 (★호출 시점 결정론 — 이미지 추론 금지) | 조명 처리 |
|---|---|---|
| **B. 조명 보존 (★기본 — 메인 변환 다음 단계)** | **이 스킬의 메인 변환(①) 결과물을 이어받아 다크로 굽는 단계면 무조건 B** (=직전 조명 작업의 산출물이라는 provenance로 결정) | **기존 빔의 위치·방향·각도·색·개수·부채꼴 패턴을 그대로 보존**하고 주변 암부만 더 눌러 어둠 강화. 빔 재발명·재배치·재색·재패턴 금지 |
| **A. 조명 생성** | 조명이 아직 안 입혀진 밝고 균등한 원본(CGI 실사화 등)에 처음 조명을 넣으며 다크로 만드는 경우 | 아래 ①~⑤ 기본 흐름대로 빔을 새로 묘사·생성 |

> **★ 판별은 이미지 내용 추론이 아니라 호출 맥락으로 결정한다(3중 검수 BLOCKER B2).** "Image 1에 빔이 보이면 B" 같은 자연어 추론은 창문 반사광·밝은 벽 그라데이션·약한 앰비언트를 빔으로 오판해 잘못된 프리셋을 걸어 실패 #1을 재발시킨다. **직전에 조명을 입힌 결과물을 이어받는 작업이면 = 무조건 모드 B**로 못박는다. ASURA 표준 워크플로우(메인 변환 ① → 익스트림 다크 ②)의 ②는 항상 이 경우 = **B가 기본값**. 맥락이 불명확하면 A/B를 추측하지 말고 ASURA에게 "①을 이어받는 다크입니까"를 확인한다.

### EXTREME DARK PROMPT 작성 원칙

Image 1 (시네마틱 변환 결과물)을 Magnific에 올리고 아래 프롬프트를 입력한다.
Image 2 레퍼런스 없음. 단독 img2img 변환.
**아래 ①~⑤는 조명 생성 모드(A) 기준이다. 조명 보존 모드(B)면 ①·③·④ 대신 "조명 보존 모드 프롬프트"(바로 아래) 를 쓴다.**

### 조명 보존 모드(B) 프롬프트 — ★기본, 이미 조명 입힌 입력용

**★ 긍정 단언형으로 쓴다(3중 검수 MAJOR M2).** 부정 열거(`do not move/recolor/re-pattern`)는 의미기반 모델에서 그 변형 대상의 salience를 오히려 올리고, 실제 강제자는 텍스트가 아니라 **Resemblance 슬라이더**다. "지키고 싶은 상태를 긍정으로 단언 + 슬라이더로 강제"가 부정문 나열보다 강하다. 한 단락으로:
> `"Preserve the existing spotlight beams exactly as they already appear in Image 1 — their positions, directions, angles, colors, spread and fan pattern remain as visible, byte-for-byte the same lighting. Beam geometry and hue stay unchanged; beam brightness may soften only through the global exposure reduction. The single change is a global reduction of ambient and shadow exposure around those beams: everything outside the beams settles into rich clean near-black while keeping faint volumetric form and depth. Every surface the beams already illuminate keeps its existing light [원본에 있는 재질별 빛 반응 — ③-a에서 골라 삽입], staying as in Image 1 with only the surrounding non-beam area darkened."`

- 그 뒤에 **켜진 LED/디스플레이 처리**(있으면 — ③-b), 카메라 보존, HDR 마무리를 이어 붙인다(아래 ⑤ 뒤 공통 블록 참조).
- 색온도는 **새로 지정하지 않는다** — 이미 입혀진 색을 보존한다(④ 생략).
- **★ 어둠은 Magnific 프롬프트가 만들지 못한다(3중 검수 MAJOR M1).** Magnific/nanobanana는 보존·업스케일 중심이라 낮은 Creativity에서 전역 노출을 거의 안 낮춘다. **다크닝은 투입 전 선행 단계에서 완성**한다 — 원본(① 결과물)을 포토샵 Curves/노출 다운으로 먼저 어둡게 만든 뒤 Magnific에 넣거나, 아예 형태 100% 보존 레이어 경로(아래)를 쓴다. Magnific 값은 **조명 보존 프리셋**(아래 설정값)으로 형태·조명 재발명 여지를 최소화하는 용도지, 어둡게 만드는 용도가 아니다.

**출력 형식:**
```
EXTREME DARK PROMPT
[연속 영어 단락]

EXTREME DARK NEGATIVE (SD 계열 대체 경로 전용 — Magnific/nanobanana에는 입력하지 않음)
[연속 영어 단락]

MAGNIFIC SETTINGS
Creativity: [값]
Resemblance: [값]
```

**★ i2i 성공 기준(BLOCKER):** 결과 위에 원본 50% 오버레이로 의자 행·카펫 경계·패널 위치를 대조한다. 틀어졌거나 원본에 없던 재질 무늬·타공·아일렛·피스·봉제선·주름·소품이 생기면 즉시 반려하고 다시 생성한다.

### EXTREME DARK PROMPT 내용 (항상 이 구조로)

**① 극단적 어둠 선언 (★ 전면 near-black 금지 — 빔 안 닿는 곳만 한정)**
> `"Extreme darkness transformation: push everything the beams do NOT reach toward near-black, while every surface the beams strike stays fully lit and alive. Strong contrast between the bright beam-lit pools and the surrounding darkness, while the shadowed areas keep faint volumetric form and depth rather than crushing to pure black."`

(`maximum contrast`는 쓰지 않는다 — i2i에서 블랙 클리핑을 밀어붙여 실루엣 blackout(반려된 실패)을 재유발한다. `strong contrast` + faint form 유지 앵커를 한 문장에 붙인다.)

**② 빛이 안 닿는 곳만 어둠 (완전 실루엣 금지 — faint form 유지)**
> `"Everything the beams do NOT reach falls into deep rich shadow — the ceiling void, the back of the hall, the far rows, the deep corners sink toward near-black while keeping faint volumetric form and depth in the shadows."`

(의미기반 모델에 들어가는 PROMPT이므로 `never a flat dead cutout` 같은 실패-명사구를 넣지 않는다 — 약한 모델이 그 명사구를 오히려 렌더한다. 긍정형 `keeping faint form`만 쓴다.)

**③ 빔 + 빛-물체 상호작용 살림 (★핵심 — 이 문장이 빠지면 죽은 그림이 된다)**
> `"The crossing spotlight beams are the dominant light source — intense sharp volumetric rays with glowing haze and drifting dust particles inside them — but every surface the light lands on stays fully alive: bright elliptical spotlight pools spilling across the surfaces the beams touch, soft light washing down edges, colored light grazing the walls where side beams strike, and gentle rim highlights skimming the tops of objects in the light. Render realistic light spill, sheen, and colored illumination sitting on the real materials."`

**③-a 재질별 빛 반응 (원본에 있는 재질만 골라 명시하면 고도화됨):**
> 패브릭 의자/천 = `"cool light raking across velvety fabric is absorbed as matte diffuse glow with brighter rim highlights feathering along the top edges, the beam color mixing physically with the fabric's own hue as accurate colored reflection"` · 무대 데크(매트) = `"crisp elliptical spotlight pools with soft penumbra and a faint low sheen"` · 광택 타일 바닥 = `"brighter wet-looking specular pools and elongated beam reflections stretching toward the camera"` · 거친 벽/기둥 = `"warm side beams graze the rough plaster as a soft warm wash fading with distance, warming the surface tone"` · 꺼진 블랙 LED/유리 = `"stays the darkest anchor with only a faint edge sheen, no emission"`. 색광이 물체 고유색과 **물리적으로 섞이는(mixing/absorption)** 것을 명시한다 — 채도·명도 결과값을 강제하지 말고 물리 반사 동사로만 제어한다(예: 파란빔이 파란의자에 physically mixing, 골드빔이 크림벽에 warming). 결과값(saturation↑ 등) 강제는 컬러 노이즈·디테일 붕괴를 유발한다.

**③-b 켜진 LED 스크린·디스플레이 처리 (★있으면 필수 — 2026-07-13 ASURA 반복 질책 + 3중 검수 반영):** 원본에 **켜져서 콘텐츠가 표시된 LED 스크린**을 다크에서 어떻게 둘지 3상태 중 하나를 명시적으로 고른다(3중 검수 BLOCKER — 기존 메인 변환의 재료잠금 `keep the same screen imagery`와 충돌하므로 상태를 분기해야 한다):

| LED 상태 | 언제 | 처리 |
|---|---|---|
| `LED_CONTENT_PRESERVE` | 스크린을 켠 채 두고 싶을 때 | 메인 변환의 재료잠금 그대로(밝기·색온도만 그레이딩). 아래 OFF 문구 미사용 |
| `LED_DIM` | 켜되 아주 어둡게 | 권장 안 함 — 잔상 위험. 꼭 필요하면 콘텐츠를 유지하되 노출만 크게 낮춤 |
| `LED_POWERED_OFF` (★ASURA 기본) | 완전히 꺼서 블랙 패널로 | 아래 긍정 단언 문구. **이 상태에서는 재료잠금의 `keep the same imagery`류 문구를 절대 함께 넣지 않는다**(직접 충돌) |

`LED_POWERED_OFF` 문구 — **긍정 목표상태를 앞세우고, 부정 열거는 짧은 보강 1개로만**(3중 검수 M2: `no purple content`처럼 두려운 산출물을 세세히 호명하면 오히려 salience가 올라 잔상 확률↑):
> `"The [central LED screen / display panels] are a single flat uniform matte-black powered-off display surface with zero emitted light, the darkest black in the whole frame; the panel frame, position and geometry stay exactly as in Image 1 while only the emissive content is gone. These OFF panels are the sole exception to the volumetric shadow — pure black with zero glow and no screen spill or color bounce onto any surrounding surface."`
- 발광 콘텐츠만 제거하고 **프레임·패널 기하·위치는 유지**한다고 분리해서 쓴다(패널 자체를 뭉개지 않게).
- `dimmed`·`barely legible`·`faint content`는 쓰지 않는다 — 의미기반 모델이 그 잔상을 렌더한다.
- **★ img2img로는 켠 LED가 확실히 안 꺼질 수 있다.** 형태 100% 보존 레이어 경로에서는 프롬프트가 아니라 **LED 영역을 마스크로 잡아 검정으로 채우는 수동/세그 단계**가 확실하다(아래 형태 보존 블록 B1 참조).
- SD 대체 경로 NEGATIVE에는 잔상 억제 토큰을 넣는다: `glowing LED screen, visible screen content, residual screen glow, faint screen text, legible logo on screen`.

**④ 색온도 (앞서 분석한 모드 그대로 적용 — 빔뿐 아니라 그 빛이 표면에 묻는 색까지 물듦)**
- Cool Blue: `"Cool blue and cold white spotlight beams cutting through the darkness, their blue light pooling and spilling onto the surfaces they touch."`
- Warm Amber: `"Warm amber and gold spotlight beams cutting through the darkness, their warm light pooling and spilling onto the surfaces they touch."`
- Mixed: `"Dominant cool blue primary beams and warm amber accent beams cutting through the darkness, both colors pooling and mixing onto the surfaces they land on."`

**⑤ 사진 리얼리즘**
> `"Photorealistic dramatic concert event lighting. Real photograph quality. Not CGI, not illustration."`

### EXTREME DARK NEGATIVE (SD 계열 img2img 대체 경로 전용)

> **주의:** Magnific 업스케일러와 nanobanana(Gemini 계열 의미기반 모델)에는 별도 NEGATIVE 입력 필드가 없고, 의미기반 모델에 부정 나열을 이어붙이면 억제어를 오히려 그린다(구도 보존 원칙 3과 동일 논리). **Magnific/nanobanana 경로에서는 이 NEGATIVE를 입력하지 않고**(섹션 출력은 유지) ②의 긍정형 어둠 묘사(`sink toward near-black while keeping faint volumetric form` 등)로 흡수한다. 아래 블록은 SD 계열 img2img로 대체 실행할 때만 NEGATIVE 필드에 넣는다.
> **★ 표면-빛 효과를 죽이는 토큰은 넣지 않는다** — `visible wall/floor/ceiling surface`, `fully visible furniture/architecture`, 무조건적 `colorful surfaces`는 빔이 닿는 표면까지 억제해 죽은 그림(실패모드 b)을 재현한다. 색 억제는 "고르게 밝은 색"으로만 한정한다(`colorful evenly-lit surfaces`, `flat daylight color`). 표면 보존은 긍정형 PROMPT의 ③·③-a가 담당한다.

```
bright ambient lighting, evenly lit room, colorful evenly-lit surfaces, flat daylight color, cheerful lighting, daylight, studio lighting, flat fill lighting, grey washed shadows, noise in dark areas, neon effects, overexposed bloom, blown highlights, fake lens flares, illustration, cartoon, CGI render look, Unreal Engine look, text, watermark, logo
```
(`bright backgrounds`는 넣지 않는다 — 빔이 뒷벽을 때리는 밝은 표면까지 억제한다.)

### Magnific 설정값 (0~1 스케일 — 3프리셋)

> **★ 대전제(3중 검수 MAJOR M1): Magnific은 어둡게 만드는 도구가 아니다.** 보존·업스케일 중심이라 낮은 Creativity에서 전역 노출을 거의 안 낮춘다. **다크닝은 Magnific 투입 전에 완성한다** — 원본을 포토샵 Curves/노출 다운으로 먼저 어둡게 만든 뒤 Magnific에 넣거나, 형태 100% 보존 레이어 경로를 쓴다. 아래 값은 "어둡게"가 아니라 "형태·조명 보존"용이다. 값은 실측 튜닝 시작 범위지 보증값이 아니다.

**★ 조명 보존 모드(B) — 이미 조명 입힌 입력 (권장 기본, ASURA 워크플로우):** 조명·형태 재발명 여지를 최소화해 ① 결과물의 빔을 그대로 유지한다.
```
Creativity: 0.2 ~ 0.35
Resemblance: 0.8 ~ 0.95
```
(조명 생성 모드보다 Creativity를 낮추고 Resemblance를 높인다 — 기존 조명·구도를 충실히 유지. **어둠이 부족하면 Creativity를 올리지 말고**(구조 재해석 위험) 선행 다크닝을 강화하거나 Curves/Multiply 레이어 합성으로 어둠을 만든다. 최소 3장 샘플에서 형태 diff·LED 잔상으로 검증.)

**조명 생성 모드(A) 기본(물체·구조 유지 우선):** 빛-물체 상호작용을 살리려면 물체가 유지돼야 한다.
```
Creativity: 0.5
Resemblance: 0.55
```
**그림자 비중 강화(단, 표면 빛은 유지 — 원본이 너무 밝을 때만):**
```
Creativity: 0.6
Resemblance: 0.48   ← 허용 하한. 0.48 미만 금지
```
(원본에 잔여 앰비언트가 강해 어둠이 안 먹을 때만 Resemblance를 하한 0.48까지 낮춘다. **0.48 미만으로 내리면** Magnific이 실제 재질을 환각·대량 변형해 ③이 의존하는 "real materials"와 빛 묻음이 사라진다 — 실루엣 blackout(반려된 실패)이 되므로 금지. 0.48은 실측 튜닝 시작점이지 보증값이 아니다 — 원본 앰비언트가 아주 강하면 0.48에서도 재질 변형이 날 수 있으니 결과에서 재질·빛 묻음 유지를 확인하고 필요하면 0.5 쪽으로 되올린다. 구도 보존용 기본값 0.1~0.3 / 0.85~1.0보다 변형 허용이 크다.)

### 익스트림 다크 예시 — Mixed / 무대 행사장 (빛-물체 상호작용 살림, 검증 사례)

> **★ 예시의 재질·색 묘사(dark matte stage deck, royal blue fabric chairs, beige walls, matte-black LED wall 등)는 이 검증 사례의 원본에 실제로 있던 것들이다. 템플릿으로 쓸 때는 반드시 사용자의 원본 이미지에 실제로 보이는 재질·색으로 교체한다** — 원본에 없는 재질을 그대로 복사하면 재질 환각을 유도한다(③-a "원본에 있는 재질만" 원칙과 동일).

```
EXTREME DARK PROMPT
Transform Image 1 into an extreme-dark cinematic stage scene lit primarily by overhead spotlight beams, with clearly visible side accent beams also lighting the nearby surfaces, keeping every surface the light actually touches fully alive while everything the light misses sinks into deep shadow. Crossing volumetric spotlight beams radiate in a wide symmetrical fan from the ceiling truss — dominant cool blue and cold white beams down the center, warm amber and gold accent beams from the outer sides — each ray a solid three-dimensional shaft with a bright luminous core, soft feathered edges, and visible glowing haze and drifting dust particles inside it. Render the light-on-material physics precisely: on the dark matte stage deck, crisp elliptical spotlight pools with soft penumbra and a faint low sheen; on the polished tiled floor and aisle, brighter wet-looking specular pools and elongated beam reflections stretching toward the camera; on the royal blue fabric chairs, cool light raking the velvety covers is absorbed as matte diffuse glow with brighter rim highlights feathering along the top edges of the front rows, the blue beam color mixing physically with the chairs' own blue as accurate colored reflection; on the beige walls and columns, warm side beams graze the rough plaster as a soft warm wash fading with distance; the powered-off matte-black central LED wall stays the darkest anchor with only a faint edge sheen and no emission. Everything the beams do not reach — the ceiling void, the back of the hall, the far rows, the deep corners — falls into rich clean near-black shadow while keeping faint volumetric form and depth. Preserve the exact same camera position, wide-angle framing, composition, and every element's placement as Image 1. High dynamic range with brilliant beam cores, natural falloff, deep noise-free shadows with no grey wash, strong contrast between the glowing illuminated pools and the surrounding darkness, correct color mixing between the colored beams and each material's own base color. Photorealistic dramatic concert-grade stage lighting on a real built hall, true photograph quality, physically believable light-on-surface behavior — not CGI, not illustration.

EXTREME DARK NEGATIVE (SD 계열 대체 경로 전용 — Magnific/nanobanana에는 입력하지 않음)
bright ambient lighting, evenly lit room, colorful evenly-lit surfaces, flat daylight color, daylight, studio lighting, flat fill lighting, cheerful lighting, grey washed shadows, noise in dark areas, neon effects, overexposed bloom, blown highlights, fake lens flares, illustration, cartoon, CGI render look, Unreal Engine look, changed camera angle, changed framing, text, watermark, logo

MAGNIFIC SETTINGS
Creativity: 0.5
Resemblance: 0.55
```

### 익스트림 다크 예시 — 조명 보존 모드(B) / 컨퍼런스홀 (★기본, 켜진 LED OFF 처리 포함, 2026-07-13 검증 사례)

메인 변환(①)으로 조명을 입힌 결과물을 Image 1으로 올린다. 빔을 새로 그리지 않고 보존하며, 원본의 켜진 보라 LED 스크린은 완전 OFF 블랙으로 끈다.

```
EXTREME DARK PROMPT
Preserve the existing spotlight beams exactly as they already appear in Image 1 — their positions, directions, angles, colors, spread and wide symmetrical fan pattern remain as visible, byte-for-byte the same lighting. Beam geometry and hue stay unchanged; beam brightness may soften only through the global exposure reduction. The single change is a global reduction of ambient and shadow exposure around those beams: everything outside the beams — the ceiling void above the baffles, the back of the hall, the far rows, the deep corners — settles into rich clean near-black while keeping faint volumetric form and depth. Every surface the beams already illuminate keeps its existing light: the elliptical spotlight pools on the matte stage deck, the cool beam light pooling on the navy contour-patterned carpet catching the pale contour lines and pile sheen, the beam light on the dark charcoal fabric chair covers as matte diffuse glow with brighter rim highlights on the rows already lit, and the warm amber side light on the dark walnut wall paneling — all staying as in Image 1 with only the surrounding non-beam area darkened. The wide central LED screen and the two vertical LED banner screens are a single flat uniform matte-black powered-off display surface with zero emitted light, the darkest black in the whole frame; the panel frames, positions and geometry stay exactly as in Image 1 while only the emissive content is gone, and these OFF panels are the sole exception to the volumetric shadow with zero glow and no screen spill onto surrounding surfaces. Preserve the exact same camera position, wide-angle central-aisle framing, composition, and every element's placement as Image 1. High dynamic range with the existing beam cores kept, natural falloff, deep noise-free shadows with no grey wash, stronger contrast between the already-lit beam pools and the deepened surroundings. Photorealistic dramatic concert-grade stage lighting on a real built hall, true photograph quality — a believable real-world interior photograph.

EXTREME DARK NEGATIVE (SD 계열 대체 경로 전용 — Magnific/nanobanana에는 입력하지 않음)
new light beams, added spotlights, re-patterned beams, moved beams, changed beam directions, changed beam colors, different lighting layout, relit scene, reinvented lighting, extra beams, fan pattern changed, glowing LED screen, bright emissive screen, screen casting light, visible screen content, purple screen imagery, faint screen text, residual screen glow, legible logo on screen, bright ambient lighting, evenly lit room, flat daylight color, daylight, studio lighting, flat fill lighting, grey washed shadows, noise in dark areas, neon effects, overexposed bloom, blown highlights, fake lens flares, illustration, cartoon, CGI render look, changed camera angle, changed framing, text, watermark, logo

MAGNIFIC SETTINGS  (형태·조명 보존용 — 어둠은 투입 전 Curves로 선행 완성)
Creativity: 0.2 ~ 0.35
Resemblance: 0.8 ~ 0.95
```


**★ 익스트림 다크 성공 기준 체크리스트 (3중 검수 반영 — 결과를 이걸로 검증):**
- [ ] LED 패널 내부에 텍스트·로고·보라 잔광이 전혀 없음(순수 검정)
- [ ] 빔 개수·주요 방향·부채꼴 패턴이 기준 이미지(①)와 일치
- [ ] 화면 프레임·객석 행·카펫 경계의 위치가 원본과 동일(오버레이 대조)
- [ ] 카메라 크롭·종횡비가 원본과 동일
- [ ] 위 중 하나라도 실패 시 원샷 i2i를 버리고 레이어 합성 경로로 전환

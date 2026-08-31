<!-- interior-prompt-maker/SKILL.md 에서 분리. 원문 그대로이며 내용 변경 없음. -->

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
- 이 사용자의 맥시마 빔: `each source-visible Maxima beam remains the exact original internally illuminated structural member, consisting only of its opaque deep-cobalt low-sheen aluminum casing and the single narrow flush translucent opal diffuser core already visible in Image 1; preserve the exact source casing-to-core ratio, luminous-pixel footprint, beam silhouette and junctions while materializing only the casing roughness, diffuser translucency, highlight roll-off and localized light response`
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
- 바미싱 플렉스 현수막(사용자 선언 또는 원본 확인 시): `a continuous full-bleed opaque PVC flex banner face tensioned by concealed sewn pole pockets at the top and bottom, with the internal rods fully hidden inside the rod-pocket sleeves; the visible face remains flat and uninterrupted at the source-defined silhouette, with exact original artwork preserved`
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

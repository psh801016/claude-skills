# AI 에이전트 3D 모델링 플레이북 — 웹 학습 정리 (2026-11-04)

plan2max · drawing-to-3d-walls · 3dsmax-mcp-dev · led-immersive-camera 가 공통으로 따른다.
배경: katalee95(블렌더 archviz + 크몽 + 클로드코드 감독) 계정 분석 뒤 "저렇게 스스로 할 수 있게 학습" 지시.
논문 4편(3DCodeBench·BlenderGym·LL3M·CodeGen-3D)·오픈소스 4종(booth-image-to-model·blender-agent-studio·blender-mcp·Blender Architect)·
archviz 후보정 가이드(ArchiGen 4-pass)·Blender 5.0 API 변경표·Kling/Seedance 비교를 읽고 **우리 파이프라인에 없는 것만** 규칙으로 뽑았다.
원문 출처는 맨 아래.

## 0. 먼저 — 무엇이 되고 무엇이 안 되나 (근거 있는 한계)
- 코딩 하네스(실행→트레이스백→재시도)는 **실행 성공률을 0.70→0.97** 로 올리지만 **형상 정확도는 거의 안 오른다**(3DCodeBench). 즉 "돌아간다 ≠맞다". 형상은 도면 겹침·치수 대조로만 확인된다 — plan2max 의 overlay·wallnet·wall_quality 가 그 역할.
- VLM 자기비평(렌더 보고 스스로 고치기)은 **이미지→3D 에서 오히려 점수를 떨어뜨렸다**(3DCodeBench D.2). 공간 결함(손잡이 안 붙음)을 VLM 이 못 본다(LL3M). → 렌더 눈대중 수정은 보조, 수치 검사가 정본. 사용자 눈이 최종 백스톱.
- 작업 시간을 2~3시간으로 늘려도 정확도는 안 올랐다(2026-11-03 유튜브 실험). 늘릴 것은 시간이 아니라 **지시의 구체성**(밑그림·좌표·대조표).
- 3DCodeBench 인간 선호 Elo 에서 Claude 는 같은 비용대 Gemini 보다 낮았다. 형상 코드 생성 레그를 교차검증할 땐 gemini 프록시를 끼운다(cross-review).
- 결론: "3D 프로그램 안 켜고 다 된다"는 **저가·저요구(크몽 투시도, 박스 매스 + AI 배경)** 조건에서만 성립. 부스 구조물·시공 치수가 얽힌 모델은 규칙 코드 + 수치 검사 + 사용자 검수가 여전히 필요.

## 1. 스펙 우선 — JSON 한 장이 정본, 코드는 그걸 컴파일만 한다
- 입력(도면·사진·말) → **중간 스펙 JSON**(단위 m, 부재 그룹별 배열, 모든 추정값에 `assumed`/`inferred` 표식) → 빌더가 새 프로세스에서 세움 → **다시 열어 검증**(reopen). booth-image-to-model · LL3M · Blender Agent Studio 전부 같은 구조. 우리 `solids.json` 이 그 스펙이다.
- 스펙에 **출처 필드**를 둔다: `brief`(사용자 말) / `drawing`(도면 선) / `prior`(관행값) / `assumed`. 보고는 `assumed` 목록을 반드시 적는다(이미 plan2max '가정한 높이' 규칙 → 모든 항목으로 확장).
- 부스(전시) 스펙 그룹 — booth-spec-v2 를 참고해 우리 kind 에 맞춤: `floor · wall · fascia(간판띠) · portal(출입 아치) · counter · furn · screen(LED/DID) · light · graphic(패널)`. 부스 유형 `inline/corner/peninsula/island` + `open_sides`(열린 면)·`cutaway_sides`(보여주려고 뺀 면, 개구부 아님) 를 적는다. 열린 면의 벽은 버리고 컷어웨이 면의 벽은 남긴다.
- 사진 1장에서 잰 치수는 **추정**이다. "실측·CAD·시공 치수"라 부르지 않는다.

## 2. 실행 루프 — 가장 수익률 높은 한 가지
- `코드 실행 → 트레이스백 전문 → 같은 코드에 국소 수정 → 재실행`. 트레이스백 없이 새 코드로 갈아엎지 않는다(LL3M: 공유 컨텍스트 없이 재생성하면 다른 모델이 나온다).
- 에러 난 줄을 **지워서** 통과시키는 것 금지(LL3M 관찰: RAG 없을 때 에이전트가 문제 줄을 삭제해 품질 하락). 고칠 수 없으면 `[확인]` 으로 보고.
- 실패 원인의 약 90% 가 **Blender 5.0 API 변경**(3DCodeBench). → §6 변경표를 먼저 본다. 우리 Blender 는 5.1.
- temperature 0.7 근처, 생각 예산은 모델 등급에 맞춤(프론티어 모델은 일찍 포화). 레퍼런스 뷰는 1~4장 늘려도 이득 없음 — **좋은 한 장 + 치수**가 낫다.

## 3. 회색 상자 먼저, 재질은 나중
- 순서: 매스(graybox) → 사용자 검토 → 개구부·틀 → 재질 → 조명 → 카메라. Blender Agent Studio·substack 사례 공통. 재질 넣은 뒤 벽 위치를 고치면 두 배 든다.
- 평면 이미지 입력은 **밑그림 깔고 따라 그리기**(plan2max 규칙) — 눈대중 좌표로 상자 놓기 금지(INWEPF 실패).
- 코드는 **편집 가능하게**: 치수·개수·색은 파일 맨 위 파라미터, 부재 이름은 의미(`30_벽_북측`), 부모-자식·컬렉션은 공정 번호(plan2max 레이어 표). 한 줄 수정 요청은 "최신 스펙 복사 → 그 항목만 변경 → 재컴파일 → 바뀐 것만 보고".

## 4. 검증 게이트 — 수치 먼저, 렌더는 증거
1. **구조 검사(코드)**: 비매니폴드 모서리 0 · 떠 있는 조각 0 · 지면 아래 0 · 같은 종류 상자 겹침 0 · 외곽 크기 = 도면 — `C:\Users\PSH\dev\plan2max\blender_qa.py`(아래) + wallnet + contact_check(Max MCP).
2. **도면 겹침**: solids 를 원본 위에 50% 로 얹어 실루엣·개구부 개수·슬래브 선 대조(overlay.png). 통과 못 하면 렌더로 안 넘어간다.
3. **고정 뷰 렌더 세트**: 히어로 1 + 정면·배면·좌·우·평면 5(수정 중엔 2장만). 카메라를 매번 바꾸지 않는다 — 같은 뷰라야 전후 비교가 된다. 3D 빌드의 뷰포트 캡처·와이어·GLB 는 "검증된 모델"이 아니다(booth 규칙).
4. **재열기 검증**: 저장한 .blend/.max 를 **별도 프로세스**로 열어 객체 수·레이어·크기 재확인(build_log 의 size 대조). 메모리 안 장면은 증거가 아니다.
5. 사용자 검수 — 렌더 시트 + 가정 목록. VLM 비평은 참고만.

## 5. 렌더 → AI 후보정 (katalee 방식의 정석화 = ArchiGen 4-pass)
원칙: **대상 건물·부스는 풀 렌더로 고정, AI 는 배경·빛·식생만.** 한 번에 다 시키면 파사드를 다시 설계해 버린다.
- 준비 패스: 고정 카메라에서 beauty + **depth + 정리한 edge(실루엣·개구부·슬래브·멀리언만)** + 마스크(유리·식생·하늘·특수 재질). 3D 에서 뽑을 수 있으면 추정 depth 를 쓰지 않는다.
- Pass 1 구조 고정: depth+edge 컨트롤, 낮은 denoise, 프롬프트는 건물 유형·재료·시간대·"geometry 유지"만. 식생·안개·반사 금지. **반려 기준**: 실루엣·개구부 개수·슬래브 선·난간·계단이 움직이면 반려. 시드 5개 컨택시트에서 개구부 패턴이 같은 것만 채택.
- Pass 2 빛·재질 관계: 더 낮은 denoise, 물리 관계로 서술(태양 방향·그림자 부드러움·유리 반사율). 창 깊이·베이·멀리언 간격·FFL·카메라 금지. 모델 그림자와 모순되는 하이라이트면 반려.
- Pass 3 영역별 인페인트: 유리 → 식생·지면 → 사람·디테일 순, 마스크 하나씩. 유리에 엉뚱한 건물이 비치거나 나무가 코너를 가리면 반려.
- Pass 4 업스케일: 마지막에, denoise 는 앞 단계보다 낮게, depth/edge 다시 붙임. 타일은 메모리가 필요할 때만, 직선·재질면을 가로지르는 이음새 없도록 overlap 충분히(USDU 기준 타일 512~768, mask blur 12~16, denoise 0.15~0.2 최소변경/0.35 강화). 미세 텍스처 과다·재해석이면 반려. 승인한 저해상 프레임·시드·프롬프트·모델 버전을 프로젝트에 남긴다.
- katalee 의 "저해상 배경 1장 → 20개 타일 → 재합성"은 Pass 4 의 타일 업스케일과 같다. 우리 쪽 도구는 `interior-prompt-maker/references/exhibition-pixel-preservation.md`(원본 그래픽·프레임 마스크 되돌리기 + 50% 오버레이 대조) 가 이미 Pass 1·4 반려 규칙을 갖고 있다 — 조감도에도 그대로 적용.
- Nano Banana(Gemini 이미지) 편집 문장 규격: `Using the provided image, change only <배경/식생/하늘>. Keep the building architecture, proportions, window mullions and camera exactly the same.` 80% 맞으면 재생성 말고 그 변경만 요청. 참조 이미지는 "Image 1/2"로 번호 지칭, 최대 14장(고충실 6장). POV 내리기(눈높이)는 약하고 수직 이동은 잘 됨.
- Photoshop 생성형 채우기는 알파 채널 선택을 그대로 쓰므로 건물 마스크가 정확할 때 가장 안전한 배경 교체 도구.

## 6. Blender 5.x API — 실패의 90% (우리 설치: 5.1)
- `grease_pencils_v3`→`annotations`, `Scene.node_tree`→`compositing_node_group`, `Scene.grease_pencil` 제거, `use_hdr_view`→`is_hdr`.
- Cycles: `feature_set` 제거, `homogeneous_volume`(Material/World) 제거, 오브젝트 `dicing_rate`·`use_adaptive_subdivision` 제거 → Subsurf 모디파이어 `use_adaptive_subdivision` 로 이동.
- EEVEE: `SceneEEVEE.use_gtao/gtao_distance/gtao_quality` 제거(→ `ViewLayerEEVEE.ambient_occlusion_distance`), 엔진 식별자는 `BLENDER_EEVEE`(NEXT 아님). `bpy.context.scene['cycles']` 딕셔너리 접근 불가 — 반드시 `scene.cycles.xxx`.
- 베이크: `RenderSettings.bake_*` 전부 제거 → `BakeSettings`.
- 메시: `MeshPolygon/MeshEdge.use_freestyle_mark` 제거, `MeshUVLoop.select` 제거. `Image.bindcode` 제거(→`gpu.texture.from_image`).
- 지오메트리 노드 다수 `mode` 속성 제거(Transform·FillCurve·MergeByDistance·Triangulate `quad_method/ngon_method` 등).
- 컴포지터 노드 속성 대거 제거(Blur size_x/y, Glare, ColorBalance 대부분) — 컴포지팅은 코드로 만지지 말고 포토샵/후보정 단계로.
- Sky Texture: `dust_density`→`aerosol_density`, 5.0 부터 **Multiple Scattering** 모드(정확, HDRI 없이 중립 색감). 기본 밝기가 높으니 Color Management Exposure 를 내린다. 512×256 프리컴퓨트 텍스처라 태양을 다른 노드로 못 돌린다. 'Single Scattering'(구 Nishita)은 레거시 — 누런 색감 원인.
- 재질 노드는 **이름이 아니라 type 으로** 찾는다(현지화): `next(n for n in nt.nodes if n.type=="BSDF_PRINCIPLED")`. enum 은 하드코딩 말고 `bl_rna.properties[...].enum_items` 로 읽는다. 렌더 엔진 대입은 try/except TypeError 로(메시지에 유효 목록).
- 전체 표: https://docs.blender.org/api/5.0/change_log.html

## 7. 3ds Max 쪽 — MCP 로 모델링할 때 (3dsmax-mcp-dev 에 이미 있는 규칙 외)
- 선택·모드 가정 금지: 스크립트가 "현재 선택"을 전제로 하면 엉뚱한 객체를 고친다. 항상 이름/핸들로 지정.
- 짧은 이름 중복(`Box001`)은 AMBIGUOUS → 먼저 공정 이름으로 rename.
- 모디파이어 스택·인스턴스 관계 보존: collapse·copy 변환은 요청 때만. 부모 스케일이 자식에 번지는지 확인.
- 체크포인트(hold/save-as)를 먼저 찍고 수정, 수정 뒤 `query_scene(delta)` + 고정 뷰 캡처 + `contact_check`.
- 배치 생성(부스 모듈·옥타 프레임·트러스)은 RailClone/스크립트 반복이 맞고, 손으로 한 칸씩 MCP 호출은 금지(undo 트랜잭션 섞임).

## 8. 영상(키컷 → i2v) — katalee 실험 + 비교 글
- **키컷(스틸) 품질이 영상 품질을 정한다.** 렌더 → §5 후보정으로 키컷을 먼저 확정하고 나서 영상.
- 모델: 건물 피사체·핸드헬드 흔들림 없는 드론샷은 **Kling 3.0**(자체 실험 + 비교 글 일치). Seedance 2.0 은 21:9·다중 참조 입력(12장)에 강하나 가챠가 심함 → 720p mini 로 테스트컷 안정화 후 1080p 최종.
- 프롬프트 층 순서: 장면(건물·시간대) → 카메라 **한 가지 움직임 + 속도**("slow drone push-in, stable motion, realistic perspective") → 빛·분위기. 움직임 1~2개로 제한. 멀티샷은 Kling 이 "Shot 1 4s / Shot 2 8s" 식 절대 지정 가능.
- 비용 기준: 1분 FHD 최소 10만원, 수정 왕복 포함 1분 30초 프로젝트 50만원까지 — 견적에 **수정 2회 한도**를 넣는다.

## 9. 평면 이미지·PDF → 벽 추출, 외부 도구 결론
- 딥러닝(CubiCasa5K ResNet-UNet·DeepLabV3+)은 주거 스캔 도면 전용으로 학습돼 전시 배치도·연회장 I-FIN 에 그대로 안 맞는다. 우리 경로(벡터 PDF→DXF→규칙, 사진→경로 C)가 맞고, LLM 비전은 `drawing-to-3d-walls` 경로 C 의 판독 프롬프트처럼 **JSON 스키마 강제 + 치수 두 개로 축척** 이 정석(Planova·floor-plan-3d 도 같은 구조).
- Archipack 은 Blender 5.0 에서 깨짐(bl_i18n_utils 오류, 2025-12~2026-07 이슈 미해결), Building Tools 는 4.0 까지·2025-01 이후 방치. **외부 건축 애드온에 기대지 않고 bmesh 직접 생성**(현 build_blender.py 방식)이 맞다.
- 이미지→3D(TRELLIS/Hunyuan3D/Meshy)는 건물 매스는 비슷하게 뽑지만 **부위 경계 없는 단일 메시**라 수정 불가 → 소품·조경 오브젝트에만. 건물·부스 본체엔 쓰지 않는다.
- 부스 사진 1장 → 파라메트릭 스펙은 `ocrevo/booth-image-to-model`(Apache-2.0, Claude Code 스킬 형태, 코너 8~10점 + 축척 앵커로 카메라 피팅, LOO 잔차로 자기검사). 사진만 있고 도면이 없는 경쟁사 부스 역설계에 쓸 수 있다 — 도입 전 cross-review.

## 10. 크몽식 상품화에 필요한 자동화 조각 (분석만, 미실행)
- 견적 규칙(평형·컷수·단가·납기·수정 횟수)을 봇이 계산 → 작업 지시서(JSON 스펙) 자동 생성 → 빌드·렌더·후보정 → 리모트컨트롤로 수정 대화. 우리 쪽은 slack-claude-bridge/Hermes 가 CS 봇 자리, plan2max/max_shots 가 빌드·초안 렌더 자리. 빠진 것은 견적 규칙과 후보정 자동 패스(§5) 뿐.

## 11. 무카 CAD(cowsdelete.com/cad) 에서 배운 검증 규칙 (2026-11-09 전수 분석)
브라우저 2D 캐드 + MCP 로 AI 가 JSON 명령으로 그리는 도구. 3D 는 **기계 부품 2·3면도 전용** 규칙 엔진(회전체·2면 교차·단면 쌓기)이라 건축 벽체엔 안 쓰지만, 검증 설계는 우리와 같은 결론을 더 수치화했다. 분석 정본 `AUSURA/AI-Sessions/wiki/reference/mucca-cad-cowsdelete-analysis-2026-11-09.md`.
- **핵심 치수 ≫ 모양**: "전체 크기·플랜지 외경·PCD·구멍·고정 홀만 맞으면 3D 로 쓸 수 있다". 건축으로 옮기면 **외곽 크기·개구부 개수와 폭·층고·기둥 간격**이 key. 보고 첫 표는 key 항목의 도면 값/모델 값/차이 — 선 일치율·렌더 인상은 그 다음.
- **2D 대조를 숫자로**: 3D 를 도면 방향으로 재투상해 재현(도면 선 중 모델에 있는 비율)·정확(모델 선 중 도면에 있는 비율) 97% 통과, 빠진 선 빨강·남는 선 파랑. → **구현: `C:/Users/PSH/dev/plan2max/plan_recall.py`**(재현 = 도면 벽 선이 모델 벽 안에, 정확 = 모델 외곽이 도면 선 위에, 기본 0.90). 첫 판의 '도면 선이 모델 외곽 위' 재현은 벽 띠 안쪽 두 줄 도면에서 55% 오판 → 덮임 기준으로 바꿈. 도면 위생은 `drawing_check.py`(무카 AUDIT·가공 전 점검 차용). 97% 가 어려운 도면(로고·곡면)도 key 는 반드시 통과.
- **5면 자가검사**: 겹침 = 작은 부품 부피의 5% 이상(그 미만은 '살짝 박힘', 볼트·용접처럼 일부러일 수 있음) · 떠 있음 = 어느 부품과도 안 닿음 · 부피 0. `blender_qa.py`(비매니폴드·떠 있음·지면 아래·같은 종류 겹침) 와 같은 자리 — 겹침 판정에 5% 부피 기준을 쓴다.
- **규칙 엔진 먼저, AI 코드 나중**: 무료·결정론 결과가 통과하면 끝. 우리 plan_model → 사람 표(doors_px) → AI 는 마지막.
- **독립 판정 AI**: 만든 과정을 모르는 새 대화에 "그리지 말고 판정만" → 불합격 사유로 1회 고치기. = cross-review 의 "만든 사람이 검수하지 않는다".
- **저장 전 게이트**: 대조 미달 3D 는 STEP 저장 전에 한 번 막는다(자동 실행은 경고만 기록). = `WALLNET_FAIL`·`inventory_check` 미통과면 납품 금지.
- **부품 하나씩**: 몸체 먼저 → 부품 몇 개씩 더하고 더한 것만 바로 점검. = 회색 상자 → 개구부 → 틀 순서(§3).
- **사진→3D 절차**: 격자(crop·mark) → 치수 1개로 mm/px → 부품 목록(그룹 기호+번호) → 코드 → 투영 겹침 **최소 2회** → 5면 → 도면. 좌표계·뷰 이름(right/left/front/rear/top)을 먼저 선언하고, 원근 사진은 위·아래 모서리의 가운데를 쓴다. 우리 도구: `drawing-to-3d-walls/scripts/photo_grid.py`.
- 안 가져온 것: replicad DSL·3D 규칙 엔진 코드(기계 전용)·블록 라이브러리.

## 12. 휴플로우 스튜디오(교육) 방법 비교 — 2026-11-09 사이트·블로그 10편 전수 분석
20년 차 공간설계자가 ChatGPT(Codex)+MCP 로 도면→SketchUp→렌더→제안서→물량→영상을 가르친다. 코드 공개 없음(리습 2개·베타 2개). 분석 정본 `AUSURA/AI-Sessions/wiki/reference/hueflow-studio-analysis-2026-11-09.md`.
- **갈림길을 먼저 선언**: 구조·동선 설명용 그림 → 평면도 1장 i2i(1~2분) / 정확한 각도·치수·여러 뷰 → 3D 에서 세운다. **i2i 는 시점·각도 변경에 약하다**(뒤쪽 뷰 요청 → 배치부터 틀어짐). 우리 plan2max·build3d 의 자리 = 후자.
- **요청 틀 `[절대 유지]/[변경]/[톤]` + 개수 숫자 + 새 대화 재투입** — interior-prompt-maker 8항. 반복 수정으로 흐려진 이미지를 '복구'하기보다 원본을 새 대화에 다시 넣는다.
- **속도 기준은 입력 난도와 함께 적는다**: 치수 없는 부동산 평면도 1장 기준 CAD 5분 46초·SketchUp 2분 51초. 연회장 I-FIN·도면 세트와 비교 불가. 사용자에게 소요 시간을 말할 때 입력 종류를 같이 말한다.
- **스킬 = 반려 축적**: "틀린 데를 짚어주고 어느 정도 되면 '지금까지 기준을 스킬로 만들어 줘'". 우리 반려 점검표 방식과 같다 — 새 사무소 도면마다 RULES 를 덧붙이는 이유.
- **현장사진 입력 기준**: 창이 잘리지 않는 수평 정면·짐 적은 사진. 사진에 안 보이는 것은 AI 가 지어낸다 → 지킬 것이 다 보이게 찍거나 3D 렌더를 준다(venue-photo-variation 와 일치).
- **모델 등급**: 디자인·도면 업무는 medium 이면 충분(그들 Q&A) — 비용 게이트와 같은 결론.
- 채택 안 함: SketchUp MCP 경로, Computer Use 로 AutoCAD 화면 출력(accoreconsole 스크립트가 안정), 베타 도구.

## 출처
- 3DCodeBench (arXiv 2606.01057) · BlenderGym (CVPR 2025) · LL3M (arXiv 2508.08228) · CodeGen-3D (IEEE Access 2026) · EZBlender (arXiv 2601.07143)
- github.com/ocrevo/booth-image-to-model (SKILL.md v3.1.0-rc7) · github.com/ifBars/blender-agent-studio · github.com/ahujasid/blender-mcp · mcpmarket Blender Architect skill · Impertio Bonsai skill package
- archigenai.com 4-pass enhancement / AI post-production stack (2026) · Coyote-A Ultimate SD Upscale FAQ · dev.to/googleai Nano Banana Pro prompting guide
- docs.blender.org/api/5.0/change_log · Blender 5.0 release notes(Sky Multiple Scattering) · blenderartists Multiple Scattering thread
- fal.ai Seedance 2.0 vs Kling 3.0 · liromfilms 150-generation test · magichour Kling 3.0 reference
- s-leger/archipack issues #436/#443 · ranjian0/building_tools releases · Yytsi/floorplan-to-3d · XUranus/planova · Omrigotlieb/floor-plan-3d
- designwithai.substack "walkable 3D house with Claude Code and Blender" (179 prompts·7일) · vagon.io Claude vs Codex for 3D
- 분석 노트: `G:\내 드라이브\AUSURA\AI-Sessions\wiki\sources\katalee95-archviz-ai-kmong-analysis-2026-11-04.md`

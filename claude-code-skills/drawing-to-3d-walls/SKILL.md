---
name: drawing-to-3d-walls
description: >-
  건축 도면(평면도)을 3D 벽체 모델로 변환한다 — PDF·DWG/DXF·래스터 이미지(스샷/사진) 모두 입력 가능.
  Blender headless로 벽을 압출해 아이소 렌더 PNG + .blend 파일을 만든다. ASURA의 CGI→AI 실사화
  워크플로우 입력 자산 생성용. 다음 상황이면 반드시 이 스킬을 사용하라: 사용자가 평면도/도면 이미지·PDF·DWG와 함께
  "3D 벽체 만들어", "벽체 세워줘", "도면 3D로", "이 평면도 3D로 뽑아", "층 도면 입체로",
  "floor plan to 3D", "walls from drawing", "제원 보고 만들어", 또는 홀/방 치수표(가로×세로×높이)를
  주며 방을 세우라고 할 때. 입력이 벡터 PDF든 DWG든 단순 스샷이든 상관없이 이 스킬로 처리한다.
---

# 도면 → 3D 벽체

2D 건축 도면에서 3D 벽체를 만든다. 엔진 = Python(추출) + **Blender 5.1 headless**(압출/렌더).
ASURA의 **CGI→AI 실사화** 파이프라인 입력 자산을 만드는 핵심·반복 작업이다.

## 원본 파이프라인 위치
스크립트 원본과 학습 노트는 `C:\Users\PSH\dev\drawing-to-3d-walls`. 이 스킬의 `scripts/`는 그것을
파라미터화·통합한 재사용판이다. 실증 성공 사례: 2026 세계 토양의 날 4층 도면(PDF), 컨벤션센터 3홀(래스터+제원).

## ★ 가장 먼저 — 입력 유형을 판별하라 (품질이 여기서 갈린다)

도면은 "그림"이 아니라 **표준 규칙으로 분류된 구조화 정보**다. 입력 포맷에 따라 얻을 수 있는 정보량이 다르다.
자세한 도면 문법(선 종류·레이어 표준·기호)은 `references/건축도면_이해_체계.md` 참고.

```
입력이 무엇인가?
├─ DWG / DXF        → 경로 A (최정밀). 레이어가 살아있어 벽/문/창을 결정적으로 구분.
├─ 벡터 PDF          → 경로 B (양호). 벡터선을 추출해 평행선쌍→중심선 병합.
└─ 래스터(스샷/사진/이미지) → 경로 C. 벡터선이 없다 → 눈으로 트레이스 + 제원표로 축척.
```

**게이트 — PDF/래스터가 들어오면 진행 전에 원본 DWG/DXF가 있는지 먼저 1회 확인한다.**
PDF는 레이어 평탄화로 벽/문/창 분류 정보가 이미 지워진 상태고 래스터는 더하다 — 원본 DWG가 있으면
경로 A가 항상 우선이다. 사용자가 "없다/모른다"면 그때 경로 B/C로 진행한다. (무인·자동화 맥락이면
질문 대신 주어진 입력으로 진행하되 보고에 "원본 DWG 미확인" 명시.)

**조용한 킬러 = 축척(스케일).** 틀려도 결과가 그럴듯해서 놓치기 쉽다.
- DWG/PDF: 도면 자체 좌표(mm)로 실치수 확보.
- 래스터: **스케일 근거가 없다.** 반드시 (1) 제원표(홀/방 가로×세로×높이) 또는 (2) 사용자가 아는 기준선 2점
  중 하나로 실치수를 잡아라. 근거 없이 픽셀로 추정하지 마라.

---

## 경로 A — DWG / DXF (최정밀)

레이어명이 요소의 정체다(A-WALL=벽, A-GLAZ=창…). ezdxf로 레이어별 추출.

```bash
python scripts/extract_dwg.py <도면.dxf> <작업폴더>
# → <작업폴더>/walls.json  (segments: [x0,y0,x1,y1,두께], 단위 m)
```
`.dwg`만 있으면 먼저 DXF로 변환 필요(ODA File Converter 등). 산출 walls.json으로 **경로 D(빌드)** 진행.
※ ezdxf 미설치 시 `pip install ezdxf`. explode된 조각·Layer 0 쓰레기 DWG 주의.
※ **단위 가정 주의**: extract_dwg.py는 mm→m(×0.001) 고정 가정이다. 도면 단위가 mm가 아니면
($INSUNITS 확인) 축척이 통째로 틀린 채 그럴듯하게 나온다 — 산출 로그의 건물 전체 치수(m)를
상식선(수십 m대)과 반드시 대조하고, 어긋나면 스크립트 SF를 도면 단위에 맞게 수정.

## 경로 B — 벡터 PDF

pdfplumber로 검정 벡터선 추출 → 수평/수직/사선 분류 → 평행선쌍 매칭으로 중심선+실두께 →
networkx로 고립 잡선 제거.

```bash
python scripts/extract_pdf.py <도면.pdf> <작업폴더> [건물폭m] [사선컷비율]
# 건물폭m 생략 시 50m 가정(임의 축척). 실치수를 알면 반드시 넣어라 — 축척의 유일한 근거다.
# 사선컷비율(0~1, 선택): 이 비율(상단 기준) 아래의 사선 제거 — 주차 램프 빗금 등이 벽으로 잡힐 때만.
#   기본은 사선 유지(무조건 제거하면 다른 도면의 하단 사선 벽이 조용히 소실된다).
#   ★ 2026-07-10 이전 버전은 0.45 컷이 하드코딩돼 있었다 — 과거 결과 재현이 필요하면 0.45를 명시하라.
#   (호출자 감사 2026-07-10: 이 스크립트를 무인자 호출하는 자동화는 없음 — 이 SKILL 수동 경로가 유일)
# → <작업폴더>/walls.json + <작업폴더>/preview.png (추출 검증용 2단 비교)
```
※ 의존성: `pip install pdfplumber networkx matplotlib`
**preview.png를 먼저 눈으로 확인**하라 — 벽선이 제대로 잡혔는지, 잡선이 남았는지. 그 다음 **경로 D**.

## 경로 C — 래스터 이미지 (스샷 / 사진)

벡터선이 없으니 픽셀에서 벽선을 **자동 추출**한다. 두 방법 — **C-1 자동추출(우선)** / C-2 수기 rooms(대안).

### ★ 붙여넣은 이미지를 파일로: transcript에서 추출
사용자가 채팅에 붙여넣은 이미지는 파일 경로가 없다. 세션 기록(jsonl)에 base64로 저장돼 있으니 꺼낸다:
```python
# 세션 transcript 경로: ~/.claude/projects/<프로젝트>/<session-id>.jsonl
# json 각 줄을 순회하며 {"type":"image","source":{"type":"base64","data":..}} 블록을 base64 디코드→.png 저장
```
(전용 스크립트는 없다 — 위 주석 패턴대로 즉석 작성한다. session-id는 scratchpad 경로에 들어있다.)

### C-1 자동추출 (OpenCV+skimage) — 우선
색아이콘 제거 → 솔리드 블롭(빔프로젝터·글자) 제거 → Canny → 밴드화(이중선 병합) → 노이즈 제거 →
**skeletonize(단일 중심선)** → 그래프 추적(연결 폴리라인, 곡선 보존) → 단순화. **이중선 없는 깔끔한 벽.**
```bash
python scripts/extract_raster.py <이미지.png> <작업폴더> [건물폭m]
# 건물폭m = 벽 bbox 가로 실치수. 제원 홀폭으로 역산: 건물폭m = 홀폭m × (bbox_px / 홀_px)
# → <작업폴더>/walls.json + overlay.png
```
**overlay.png(원본 위 빨간선=검출벽)를 반드시 눈으로 검증**하라 — 벽이 잘 잡혔는지/노이즈 없는지.
아이콘 스크리블이 남으면 색마스크 팽창↑, 갭이 크면 Canny 하한↓·maxLineGap↑. 그 다음 **경로 D**.
※ 미설치 시 `pip install opencv-python-headless scikit-image numpy` — 경로 C 필수 3종(skeletonize는 scikit-image 소속). 실증: 라한 경주 B1F(붙여넣기 도면).
※ extract_raster.py는 walls.json에 `wall_height: 3.5`를 기록한다(실증 당시 값 — 경로 B의 3.0과 다름). 다른 층고가 필요하면 빌드 전에 walls.json의 wall_height를 수정.

### C-2 수기 rooms (대안 — 도면이 색블록/단순 홀 위주일 때)
방/벽을 **직접 읽어서** `rooms.json`으로 구성한다. 축척은 **제원표**가 준다. (작성 예시: `examples/convention-center-rooms.json` — 컨벤션홀 8개 방 구성)

1. 평면도를 보고 방들의 상대 배치·복도 흐름·코어(화장실/EV/계단) 위치를 파악.
2. 제원표에서 각 홀/방의 **실치수(가로 w × 세로 d × 높이 h, m)** 를 읽는다.
3. `rooms.json`을 작성한다 (아래 포맷). 방은 제원대로 정확히, 배치는 평면도를 따라.

```json
{
  "rooms": [
    {"name":"컨벤션홀","cx":24,"cy":34,"w":48,"d":30.6,"h":7.1,"t":0.30,"rot":0,"door":["S",8]},
    {"name":"베가홀","cx":14,"cy":3,"w":15.5,"d":24.4,"h":6.3,"t":0.30,"door":["N",4]},
    {"name":"화장실","cx":52,"cy":44,"w":6,"d":5,"h":3,"t":0.15}
  ],
  "polylines": [
    {"pts":[[48,30],[62,27],[76,20]],"t":0.2,"h":3.0}
  ]
}
```
- `cx,cy` = 방 중심(m), `w,d` = 가로·세로(m), `h` = 천장높이(m), `t` = 벽두께(기본 0.3, 칸막이 0.15).
- `rot` = 회전각(도, 선택), `door` = `[변, 개구부폭]` 변은 `N/S/E/W`(선택, 없으면 4벽 막힘).
- `polylines` = 복도/자유벽. `pts` 정점들을 두께 `t`·높이 `h`로 압출.
- 그 다음 **경로 D**로 빌드.

**정직 원칙(중요):** 래스터는 "**홀은 제원대로 정확, 배치·복도는 눈대중 재구성**"이다. 결과 보고 시 이 구분을
반드시 명시하라. 픽셀 정밀이 필요하면 원본 DWG/PDF를 요청하라. ASURA는 근사/대체물에 민감하다 —
근사한 부분을 정확한 척 넘기지 마라.

---

## 경로 D — Blender 빌드 (모든 경로 공통)

`walls.json`(경로 A/B) 또는 `rooms.json`(경로 C) → 벽 박스 압출 → 아이소 렌더 + .blend 저장.

```bash
"/c/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background \
  --python scripts/build_walls.py -- <작업폴더> <walls.json 또는 rooms.json>
# → <작업폴더>/render.png (아이소 뷰) + <작업폴더>/model.blend
```
- 두 JSON 포맷을 자동 감지한다(`rooms`/`polylines` 키 있으면 경로 C, `segments` 키면 A/B).
- 세그먼트 파일은 전체를 `wall_height`(기본 3.0m) 단일 높이로, rooms는 방별 `h`로 압출.
- Blender 경로가 다르면 실제 설치 버전으로 교체(`ls "/c/Program Files/Blender Foundation/"`).

**빌드 후 반드시 render.png를 눈으로 확인**하고 사용자에게 보여줘라. 벽이 엉키거나 축척이 이상하면 JSON을 고쳐 재실행.

## 산출물 규약
작업폴더에 `walls.json`/`rooms.json`(소스) · `render.png`(렌더) · `model.blend`(편집용). 사용자가 Blender에서
바로 열 수 있게 `.blend`를 전달하라.

## 남은 과제 (개선 여지)
- 문/창 개구부 자동검출(현재 벽 통짜 or 수동 door). 문=arc, 창=반복 평행선, YOLOv8 심볼.
- 래스터 축척 자동화: 치수 OCR(PaddleOCR) → 기준선 2점 클릭 fallback.
- 스캔 도면: 전처리→CubiCasa5K/DeepFloorplan 딥러닝 벽분할→벡터화→같은 walls.json 합류.

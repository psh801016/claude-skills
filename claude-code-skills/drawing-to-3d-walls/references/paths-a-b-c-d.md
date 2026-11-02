# 경로 A·B·C·D — 보조 경로 상세 (drawing-to-3d-walls)

SKILL.md 의 '입력 유형 판별'에서 A·B·C 로 갈렸을 때 읽는다. 경로 E·F(★주력)는 SKILL.md 본문에 있다.

## 경로 A — DWG / DXF 원본 (좌표가 실재하는 최정밀)

레이어명이 요소의 정체다(A-WALL=벽, A-GLAZ=창…). ezdxf로 레이어별 추출.

```bash
python scripts/extract_dwg.py <도면.dxf> <작업폴더>
# → <작업폴더>/walls.json  (segments: [x0,y0,x1,y1,두께], 단위 m)
```
`.dwg`만 있으면 먼저 DXF로 변환(ODA File Converter 등). 산출 walls.json으로 **경로 D** 진행.

**이 스크립트의 알려진 결함 3가지 — 쓰기 전에 확인하라:**
1. **`$INSUNITS`를 안 읽는다.** `SF=0.001`(mm→m) 고정이다. 도면 단위가 mm가 아니면 축척이
   통째로 틀린 채 그럴듯하게 나온다. 로그의 건물 전체 치수(m)를 상식선과 **반드시 대조**하라.
2. **Layer 0을 전부 벽으로 본다** (`if name == "0": return "WALL"`). 실무 DWG에서 Layer 0은
   잡동사니가 모이는 곳이라 쓰레기가 벽이 된다.
3. **문/창을 분류만 하고 쓰지 않는다.** `cat_layers['DOOR']`를 만들어놓고 참조하지 않아
   벽이 통짜로 나온다. 개구부가 필요하면 경로 E로 가거나 직접 잘라라.

※ `pip install ezdxf`. explode된 조각 주의.
※ 경로 A에는 시각 검증 산출물이 없다(B는 preview.png, C는 overlay.png가 있다). 로그 숫자로 대조하라.

## 경로 B — 치수 없는 벡터 PDF

pdfplumber로 검정 벡터선 추출 → 수평/수직/사선 분류 → 평행선쌍 매칭으로 중심선+실두께 →
networkx로 고립 잡선 제거.

```bash
python scripts/extract_pdf.py <도면.pdf> <작업폴더> [건물폭m] [사선컷비율]
# 건물폭m 생략 시 50m 가정(임의 축척). 실치수를 알면 반드시 넣어라 — 축척의 유일한 근거다.
# 사선컷비율(0~1, 선택): 그 비율(상단 기준) 아래의 사선 제거 — 주차 램프 빗금이 벽으로 잡힐 때만.
#   기본은 사선 유지(무조건 제거하면 다른 도면의 하단 사선 벽이 조용히 소실된다).
#   ★ 2026-07-10 이전 버전은 0.45 컷이 하드코딩돼 있었다 — 과거 결과 재현이 필요하면 0.45를 명시.
# → <작업폴더>/walls.json + preview.png (추출 검증용 2단 비교)
```
※ `pip install pdfplumber networkx matplotlib`
**preview.png를 먼저 눈으로 확인**하라 — 벽선이 제대로 잡혔는지, 잡선이 남았는지.

## 경로 C — 치수 없는 래스터 (스샷 / 사진)

### 붙여넣은 이미지를 파일로: transcript에서 추출
채팅에 붙여넣은 이미지는 파일 경로가 없다. 세션 기록(jsonl)에 base64로 있으니 꺼낸다:
```python
# ~/.claude/projects/<프로젝트>/<session-id>.jsonl 각 줄을 순회하며
# {"type":"image","source":{"type":"base64","data":..}} 를 디코드 → .png 저장
```
(전용 스크립트는 없다 — 위 패턴대로 즉석 작성. session-id는 scratchpad 경로에 있다.)

### C-1 자동추출 (OpenCV+skimage)
색아이콘 제거 → 솔리드 블롭 제거 → Canny → 밴드화 → 노이즈 제거 → **skeletonize** →
그래프 추적 → 단순화.
```bash
python scripts/extract_raster.py <이미지.png> <작업폴더> [건물폭m]
# 건물폭m = 벽 bbox 가로 실치수. 제원 홀폭으로 역산: 홀폭m × (bbox_px / 홀_px)
# → walls.json + overlay.png
```
**overlay.png(원본 위 빨간선=검출벽)를 반드시 눈으로 검증**하라. 아이콘 스크리블이 남으면
색마스크 팽창↑, 갭이 크면 Canny 하한↓·maxLineGap↑.
※ `pip install opencv-python-headless scikit-image numpy`
※ walls.json에 `wall_height: 3.5`가 박힌다(실증 당시 값). 다른 층고면 빌드 전에 고친다.
※ **선만 나오고 "이건 문, 저긴 안방"은 모른다.** 실명·개구부가 필요하면 경로 E가 낫다.

### C-2 수기 rooms (도면이 색블록/단순 홀 위주일 때)
제원표가 축척을 준다. 예시: `examples/convention-center-rooms.json`.
```json
{
  "rooms": [{"name":"컨벤션홀","cx":24,"cy":34,"w":48,"d":30.6,"h":7.1,"t":0.30,"rot":0,"door":["S",8]}],
  "polylines": [{"pts":[[48,30],[62,27],[76,20]],"t":0.2,"h":3.0}]
}
```
`cx,cy`=중심(m), `w,d`=가로·세로, `h`=천장고, `t`=벽두께(기본 0.3/칸막이 0.15),
`rot`=회전각(도), `door`=`[N|S|E|W, 개구부폭]`.

**정직 원칙:** 래스터는 "**홀은 제원대로 정확, 배치·복도는 눈대중 재구성**"이다. 보고 시 이 구분을
반드시 명시하라. ASURA는 근사물을 정확한 척 넘기는 것에 민감하다.

## 경로 D — 매스 빌드 (A·B·C 공통, 빠른 검토용)

```bash
"/c/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background \
  --python scripts/build_walls.py -- <작업폴더> <walls.json 또는 rooms.json>
# → render.png + model.blend
```
- 두 포맷 자동 감지(`rooms`/`polylines` → C, `segments` → A/B).
- 세그먼트는 `wall_height` 단일 높이. **세그먼트별 높이 `s[5]`도 지원한다**(문서에 없던 기능) —
  층고가 실마다 다르면 `[x0,y0,x1,y1,t,h]` 6번째에 m 단위로 넣어라.
- **한계: 벽만 선다.** 바닥·개구부·가구·재질이 없어 매스 덩어리로 나온다. 납품물이면 경로 F를 써라.
- 카메라가 `lens=40`·고정거리라 **가로로 긴 건물은 프레임 밖으로 나간다.** 잘리면 정사영으로 바꿔라.

`plan.json`을 이 경로로 쓰고 싶으면 `scripts/to_walls_json.py`가 변환한다(개구부를 잘라주고
세그먼트별 높이를 채운다).

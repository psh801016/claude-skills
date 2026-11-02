---
name: led-immersive-camera
description: "3ds Max + V-Ray 에서 곡면·다면 LED 월 몰입형 전시룸을 현장 사진처럼 보이게 카메라 3종(코너 사선·벽 정면 근접·세로 9:16)을 MaxScript 로 자동 배치하고 LED 광원·유광 바닥·VFB 포스트까지 세팅한다. 'LED 룸 카메라', '몰입형 전시 뷰 잡아줘', '카메라 잡아줘', '실감나게 뷰', '레퍼런스처럼 렌더', 'LED 월 렌더 세팅', '미디어아트 룸 카메라'라고 하면 사용한다. 평면도에서 모델을 세우는 일은 plan2max, MCP 도구 사용법 자체는 3dsmax-mcp-dev, 렌더 이미지의 조명 프롬프트 변환은 cinematic-exhibition-lighting."
---

# LED 몰입형 전시룸 카메라 연출

LED 월 전시 공간이 이미 모델링된 3ds Max 씬에서 "실감나게 보이는" 카메라 3개를 만들고, 그 카메라가 사진처럼 보이게 하는 광원·재질·포스트 값을 맞춘다. 단위는 mm. 렌더러는 V-Ray(CPU), 재질은 VRayMtl/VRayLightMtl 이 기본이다.

## 시작 전 확인 질문 (모호하면 1개만)

- 관람객이 들어오는 **열린 쪽**이 -Y(front) 인지 +Y(back) 인지 모르면 먼저 묻는다. 씬에서 판단되면 묻지 않는다.

## 1. 판단 기준 — 레퍼런스가 좋아 보이는 이유

1. 관람객 눈높이 1,400~1,600mm, 벽에 가깝다.
2. 비대칭 구도: 한 벽은 정면, 한 벽은 사선, 소실점은 프레임 밖.
3. 검은 유광 바닥 반사로 깊이가 두 배로 보인다.
4. LED 월이 유일한 광원이라 바닥·사람·천장에 같은 색이 묻는다.

금지: 룸 정중앙 + 세 벽 대칭 + 높이 2m 이상 + 28mm 이상 → 도면처럼 보인다.

## 2. 카메라 프리셋

| 프리셋 | 위치 | 높이 | Target 높이 | 초점거리 |
|---|---|---|---|---|
| A 코너 사선 (메인) | 안쪽 모서리, 두 벽에서 1.8m 안쪽, 대각선 방향 | 1,500 | 1,400 | 20mm (18~24) |
| B 벽 정면 근접 | 목표 벽에서 3m, 벽 좌우 1/3 지점을 향함 | 1,500 | 1,450 | 18mm (16~20) |
| C 세로 9:16 | 룸 중앙에서 열린 쪽으로 15% 물러남, 위로 3~5° | 1,200 | 1,450 | 20mm |

공통: VRayPhysicalCamera, Film gate 36mm, Specify FOV OFF, DOF OFF(f/8), 수직 틸트 보정 ON. C 는 Output Size 1080×1920.

## 3. 실행 — 스크립트는 `scripts/led_cams.ms` 하나가 정본

코드를 본문에 다시 쓰지 않는다. 수치를 바꿀 때는 `led_cams.ms` 만 고치고 테스트를 다시 돌린다.

1. 사용자에게 LED 월 오브젝트를 선택해 두게 하거나, 이름으로 골라 배열을 만든다.
2. 실행 경로를 고른다.
   - **3ds Max MCP 연결됨(로컬 Claude)**: `mcp__3dsmax-mcp__execute_maxscript` 로 아래 두 줄을 보낸다.
   - **MCP 없음·웹**: `led_cams.ms` 전체와 아래 마지막 줄을 MAXScript Listener 붙여넣기용으로 준다.

```maxscript
fileIn @"C:\Users\PSH\.agents\skills\led-immersive-camera\scripts\led_cams.ms"
buildLEDCams (selection as array) openSide:"front"
```

3. 성공 토큰 `LEDCAM_OK A B C` 가 리스너에 찍혀야 성공이다. 없으면 실패로 보고한다.
4. 같은 이름 카메라는 지우고 다시 만들므로 여러 번 돌려도 카메라는 3개뿐이다.
5. 생성 뒤 `mcp__3dsmax-mcp__capture_viewport` 로 세 카메라 뷰를 확인하고, 곡면·열린 방향 때문에 어긋난 컷은 그 카메라의 pos/target 만 조정한다. 벽이 X축 방향으로 서 있으면 x/y 를 바꿔 적용한다.

코드 블록 안에는 한국어 주석을 넣지 않는다(Listener 인코딩 깨짐).

## 4. 광원·재질 체크리스트 — 카메라보다 중요

- **LED 월**: `VRayLightMtl`, 콘텐츠 프레임 텍스처, Multiplier 8~15, Direct illumination ON, Emit back side OFF. 픽셀 피치는 Composite 맵에 LED 그리드 Multiply. 패널 UV 는 Planar 로 통일(가로 스캔라인 노이즈 = UV 깨짐).
- **바닥**: `VRayMtl` Diffuse (10,10,10), Reflect 흰색, Glossiness 0.75~0.85, Fresnel IOR 1.6.
- **천장·상단 벽**: 무광 (40,40,40). 완전 검정 금지.
- **라이트**: 환경광 0, 다른 라이트 OFF, LED 월만 광원. GI Brute Force + Light Cache.
- **인물**: 실루엣 2~4명(벽 앞 1명 손 들기, 뒤 2명 관람). 사진 인물 합성은 person-layer-maker.
- **VFB 포스트**: Bloom/Glare Size 20~30, Intensity 0.3~0.5, Exposure -0.5~-1.0 EV, 섀도 살짝 리프트.

## 5. 작업 순서

1. 카메라 3개 생성 → LEDCam_A 저해상 테스트 렌더로 광원·바닥 확인.
2. 콘텐츠별(네온 스트라이프 / 별 파티클 / 수묵 / 블루 수중) 텍스처만 교체해 같은 카메라로 렌더.
3. 애니메이션: 돌리 0.3~0.5 m/s 사선 전진, 핸드헬드 Noise Position 5mm / Rotation 0.2°.

## 6. 출력 규격 (항상 이 순서)

1. 생성한 카메라 3개 이름과 위치·초점거리 표
2. 성공 토큰 확인 결과(`LEDCAM_OK` 유무)
3. 광원·재질 체크리스트 중 씬과 다른 항목
4. 못 한 것·조정이 필요한 컷

## 7. 검증

- 회귀 테스트: `scripts/test_led_cams.ms` — 사용자 열린 씬이 아니라 별도 배치 프로세스로 돌린다. 성공 토큰 `LEDCAM_TEST_OK`.

```bash
"/c/Program Files/Autodesk/3ds Max 2025/3dsmaxbatch.exe" "C:\Users\PSH\.agents\skills\led-immersive-camera\scripts\test_led_cams.ms" -listenerlog out.txt
```

- 연혁·레퍼런스·함정: `references/lessons.md`

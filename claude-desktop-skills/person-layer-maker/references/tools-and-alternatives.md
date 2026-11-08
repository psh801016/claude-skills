# 생성 도구 운용·대안 경로 (SKILL.md 에서 이동, 2026-11-05)

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

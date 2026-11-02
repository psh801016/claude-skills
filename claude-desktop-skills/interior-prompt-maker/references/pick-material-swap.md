# 정밀 재료 교체(PICK) 모드 — 부분만 콕 집어 교체 (interior-prompt-maker)

SKILL.md 의 '구도 보존 최우선 원칙' ★ 블록과 모드 판단 규칙이 그대로 적용된다.

## 정밀 재료 교체(PICK) 모드 — 부분만 콕 집어 교체

리모델링 모드가 "공간 전체 스타일"을 바꾼다면, 이 모드는 **지정된 부분의 표면 재료만** 바꾼다. 행위/기준/전이 3행 규격:

- **행위:** 표면 재료만 바꾼다 (형태 재설계 금지)
- **기준(보존):** 형상 · 구도 · 객체 경계 · 카메라 — 대상의 실루엣과 나머지 공간 전부
- **전이:** 질감 · 색 · 거칠기 · 반사도 — Image 2(레퍼런스)의 재료 속성만

**프롬프트 구성:**
1. 첫 문장 역할 선언: "Image 1 = BASE(보존), Image 2 = 재료 소스(REFERENCE)"
2. 대상 지정: 자연어("the fabric sofa", "the upper wall band around the skylight") 또는 **빨간 마스크 규약** — Image 1의 빨간 하이라이트 영역 = 변경 대상. **⚠ 소스(Image 2) 쪽은 빨간 채움 금지** — 모델이 읽을 소스 색·질감이 오염된다. 소스 패치는 **크롭해 깨끗한 이미지로 전달**하고, 표시가 불가피하면 채움 없는 윤곽선만 사용
3. 교체 문장: "Replace ONLY the surface material of [대상] with the material of the REFERENCE — transfer its texture, color, roughness and reflectance. Keep the shape, boundaries, composition and camera exactly unchanged."
4. 마스크를 썼다면 제거 지시 필수: "Remove every red annotation line, hatch or highlight from the final output."
5. 물리 정합 앵커로 마무리: "physically correct scale, contact shadows and lighting on the new material."

**주의:** ① 구도 보존 최우선 원칙(위 ★ 블록) 그대로 적용 ② GPT 경로 = NEGATIVE 없이 긍정형 잠금(기존 규칙) ③ 새 재료의 반사도가 조명과 충돌하면(광택 재료 ← 무광 장면) 조명 방향을 명시해 하이라이트 위치를 고정한다.

**엣지케이스:**
- 이미지 0장 → 원본 이미지 첨부를 요청한다 (텍스트만으로 지어내지 않는다)
- 이미지 2장이 같은 공간의 다른 앵글이라 리모델링 의도가 불명확하면 → 각각 단일 모드로 처리할지 사용자에게 확인 (다중 앵글 일괄 실사화 케이스 빈발)
- 이미지 3장 이상 → 어느 것이 구조 원본(Image 1)이고 어느 것이 스타일 레퍼런스인지 확인 후 진행 ("Image 1 = 구조 고정" 가정은 PROMPT 첫 문장의 역할 선언으로 표현된다 — 별도 설명 출력 금지)

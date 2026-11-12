# 무카 CAD(cowsdelete.com/cad)에서 가져온 것 (2026-11-09)

설치·연결하지 않는다(사용자 지시). 이 도구는 기계 부품 2·3면도→3D 용이며 **건축 평면도의 벽체 3D 는 못 만든다**(실측 확인). 아래 기능만 우리 코드·규칙으로 옮겼다.

- 좌표 격자 읽기 → `scripts/photo_grid.py` (사진→3D 절차의 격자+표식+mm/px)
- 입면 전개도·면적표 → `scripts/plan2elev.py` (휴플로우 리습과 함께)
- 검증 규칙 → `../plan2max/references/ai-modeling-playbook.md` §11 (핵심 치수 우선 · 2D 재투상 대조 · 5면 겹침 5% · 독립 판정 · 저장 전 차단)
- 도면 위생 검사(AUDIT·가공 전 점검) → `C:/Users/PSH/dev/plan2max/drawing_check.py`
- 모델↔도면 2D 대조(재현·정확) → `C:/Users/PSH/dev/plan2max/plan_recall.py` (+`test_plan_recall.py`). plan_model.py 가 meta 에 `origin_mm`·`wall_layers`·`frame_mm` 을 남긴다

분석 정본 `AUSURA/AI-Sessions/wiki/reference/mucca-cad-cowsdelete-analysis-2026-11-09.md`.

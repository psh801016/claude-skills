# 부산 사이버보안 콘퍼런스 2026 부스간판 세트 — 실제 작업 스크립트 (2026-10-15~21)

결과: `X:\[11.04-05] 2026 부산 사이버보안 콘퍼런스\3 3D\발주\원본\부스간판.ai`
(정면 2930x750 24장 · 옆간판 2435x750 8장 · 기업부스날개 450x6460 29EA · 묶음 제목 3개, 파란 배치도 번호순).
로고 정리본·틀·백업: `G:\내 드라이브\AI-작업기록\claude\2026-10-15_부산사이버보안_부스간판\`.
다음 행사에서는 경로·로고 표·번호 표만 바꿔 쓴다. 공용 기능은 `scripts/sign_tools.jsx`·`render_artboard_tif.py` 로 올라갔다.

| 순서 | 파일 | 하는 일 | 일러 |
|---|---|---|---|
| 1 | make_list.py | 요청서 엑셀 → CSV, 회사별 로고 표, 오타 표, CMYK TIFF | 아니오 |
| 1 | ai_logos.py | 나중에 온 .ai 로고 → CMYK 6000px TIFF (CROP 으로 한 개만) | 아니오 |
| 2 | make_template.jsx | 예시안 → 틀 4종(`틀`·`틀_로고2`·`틀_2사`·`틀_연두`) + 위 검정 번호 라벨 | 예 |
| 3 | run_fill.jsx | 틀 → 결과 파일 채우기 → 틀 지우기 → 덤프 → 미리보기 | 예 |
| 4 | swap_logos.jsx · enlarge_dream.jsx · fix_wit_nnsp.jsx · divider_to_x.jsx | 손 수정 뒤 로고만 교체 / 로고 키우기 / 한 장을 두 회사형으로 / 구분 막대 → X | 예 |
| 5 | renumber.jsx | 확정 배치도 번호로 배지·라벨 바꾸기 | 예 |
| 6 | make_side.jsx | 정면 틀 → 옆간판 틀(`틀_옆`·`틀_옆_연두`) 잘라 당기기 + 견본 2장 | 예 |
| 7 | build32.jsx | 08 통합부스 1장 추가 + 옆간판 8장 (정면 로고·글자 복제) | 예 |
| 8 | reorder.jsx | 번호순 다시 놓기 (공공 04 맨 끝) | 예 |
| 9 | add_titles_wing.jsx · wing_tif.py · wing_tif.jsx | 묶음 제목 3개 + 날개(B구역부스 1번 대지 → CMYK TIFF → 한 면 + 180도) | 예 |

.jsx 는 UTF-8 BOM 으로 저장해 `$ai.DoJavaScriptFile()` 로 돌린다. 돌리기 전에 ASURA님께 묻는다.
| 10 | out_prep.jsx · wing150.py · render_signs.py · build_out.jsx · run_jsx.ps1 | 출력 파일: 날개 150ppi 위·아래, 간판·띠지 테두리 안 → 실물 150ppi CMYK 그림, 글자깨기 → `출력/부스간판_출.ai` + `_출.jpg` | 일부 |

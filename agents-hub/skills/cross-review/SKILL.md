---
name: cross-review
description: 결과물(코드·설계·문서)을 여러 모델로 적대적 교차검증한다. "교차검증", "검수해줘", "cross-review", 만들거나 고친 산출물을 머지·배포 전 확인할 때 사용. Claude Code·Codex 양쪽에서 동일하게 동작.
---

# cross-review — 적대적 3중 교차검증

만들거나 고친 결과물을 혼자 판단하지 않고, 독립 모델들에게 **기본적으로 결함을 가정**하고 반박하게 한다.

## 절차

1. 검수 대상과 핵심 질문을 1200자 이내로 정리한다(파일 경로·구조·구체 질문 포함).
2. 세 관점을 병렬로 호출한다 — 누구 하나 빼지 않는다.
   - `gemini` — 다른 관점 / UI·UX 대안
   - `opus` — 설계 · 로직 · 엣지케이스
   - `codex`(또는 `gpt`) — 실제 코드 버그 · 타입 안전성
3. 호출은 적대적으로 강제한다(검수자가 "잘 봐주지" 않도록):

   ```powershell
   cd C:\Users\PSH\dev\multi-model
   .\consult.ps1 -Provider codex  -Review -Prompt "이 코드 검수: <질문>" -File "<경로>"
   .\consult.ps1 -Provider opus   -Review -Prompt "이 설계 검수: <질문>"
   .\consult.ps1 -Provider gemini -Review -Prompt "이 관점 검수: <질문>"
   ```
   - Codex 사용자는 `consult.ps1`을 `shell`로 실행하면 동일하게 동작한다.
4. 세 결과를 대조해 BLOCKER/MAJOR/MINOR로 분류하고, 이견이 갈리면 가장 보수적·안전한 쪽을 채택한다.
5. **실제 실행 검증**(build / HTTP 200 / test)으로 재확인한 뒤에만 "통과"라고 보고한다.
6. 배운 교훈은 `~/.agents/knowledge/` 또는 `C:\Users\PSH\MultiAgent\_shared\learnings.md`에 누적한다.

## 출력 형식

- **BLOCKER** — 머지/배포 차단. 근거·재현 시나리오 포함.
- **MAJOR** — 주요 결함. 구체적 수정안.
- **MINOR** — 개선 권장.
- **통과 가능 여부** — 위를 고쳤을 때만 통과인지 조건 명시.

근거 없는 통과 선언은 검수 실패로 간주한다.

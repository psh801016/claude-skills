# claude-skills — 세션 규율

## ★ 모든 턴의 0번 단계: 모델·effort 라우팅 선언 (생략 금지)

**비단순 요청을 받으면, 작업을 시작하기 전에 먼저** 추천 provider/model/effort를 선언한다.
사용자가 묻기를 기다리지 않는다. 이것은 선택이 아니라 **선행 조건**이다.

### 절차

```bash
cd claude-desktop-skills/adaptive-model-effort-advisor/scripts

# 1) 전례 조회 — 휴리스틱보다 먼저
python3 registry.py query "<작업>" --axes "verifiable=...,failcost=...,volume=...,depth=..."

# 2) 현재 모델명 해석 — 릴리스 번호를 절대 손으로 쓰지 않는다
python3 recommend.py "<작업>" --provider claude --axes "verifiable=...,failcost=...,volume=...,depth=..."
```

### 4축 분류

| 축 | 값 |
|---|---|
| `verifiable` | `yes` / `partial` / `no` |
| `failcost` | `low` / `mid` / `high` |
| `volume` | `high` / `low` |
| `depth` | `shallow` / `mid` / `deep` |

### 출력 형식 (5요소 전부)

1. 해석된 route (`model` + `effort` + `source` + `catalog_checked_at`)
2. 4축 판정 근거
3. 검증 체크 1개 — 기계적 또는 사람 확인
4. 승급 경로 **정확히 1개**
5. registry 조회 결과 (`matched` 건수)

### 생략 가능한 경우

단순 번역, 짧은 조회, 한 단계로 끝나는 요청 — 라우팅의 실익이 없을 때만.
**"급해 보여서" 는 생략 사유가 아니다.** 조사·구현·설계·문서 작업은 예외 없이 선언한다.

### 왜 이 파일이 필요한가

`adaptive-model-effort-advisor`는 `claude-desktop-skills/` 에 있어 **Claude Desktop에서만 자동 로드된다.**
Claude Code(CLI·웹) 세션에는 그 스킬이 노출되지 않아 2026-08-04 이전까지 이 루틴이 발동하지 않았다.
이 CLAUDE.md가 Code 세션에서의 강제 장치다. 스킬 본문은 위 경로의 `SKILL.md`를 정본으로 읽는다.

---

## 저장소 성격

Claude 스킬 백업 전용이다.

| 경로 | 런타임 |
|---|---|
| `claude-code-skills/` | Claude Code (CLI·웹) |
| `claude-desktop-skills/` | Claude Desktop |
| `tools/` | 진단·운영 스크립트 |

- 정본은 로컬 `~/.agents` 이며 주간 `sync.ps1` 로 이곳에 백업된다.
- 이 저장소를 직접 고친 뒤 로컬로 되돌리려면 드리프트에 주의한다 — 정본은 항상 `~/.agents/rules.md` 쪽이다.

## 작업 규율

- **fail-loud**: 실패·미확인을 조용히 넘기지 않는다. 애매하면 "미확인"으로 명시한다.
- **사실과 추정 분리**: 관측된 것과 추론한 것을 문서에서 절대 섞지 않는다.
- **원본 우선**: 로그·원문을 인용하고, 요약본을 근거로 결론내지 않는다.

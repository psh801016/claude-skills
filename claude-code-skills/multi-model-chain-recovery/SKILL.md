---
name: multi-model-chain-recovery
description: Codex·Claude·Gemini 3중 체인(자비스 자동 루틴·cross-review)이 통째로 실패할 때 원인을 지문으로 특정하고 복구한다. "3중 체인 전부 실패", "MODEL_ERROR", "OAuth session expired", "helper_unknown_error", "setup refresh had errors", "folder is not trusted", "지혜 승격 실패", "루틴이 조용히 죽었다" 같은 말이 나오면 사용. Windows 로컬 CLI 환경·인증 문제 전담 — 모델 선택은 adaptive-model-effort-advisor, 검수 절차 자체는 cross-review가 담당.
---

# multi-model-chain-recovery — 3중 체인 복구

Codex·Claude·Gemini 세 레그가 **동시에** 죽으면 모델 문제가 아니다. 거의 항상 **무인(headless) 실행 환경**의 문제다 — 세 CLI 모두 "사람이 앞에 있다"고 가정한 폴백(브라우저 로그인·신뢰 확인 프롬프트·샌드박스 승인)을 갖고 있고, Slack 자비스 브리지/스케줄러에서 돌면 그 폴백이 전부 실패로 떨어진다.

## 1. 30초 지문 판별

로그에서 아래 문자열을 찾는다. 레그마다 원인이 완전히 다르므로 **한 번에 하나씩 고치려 하지 말고 세 개를 병렬로 판정**한다.

| 로그 지문 | 레그 | 진짜 원인 | 즉시 조치 |
|---|---|---|---|
| `windows sandbox: helper_unknown_error` / `setup refresh had errors` | Codex | 작업 폴더 **NTFS 소유권**이 `BUILTIN\Administrators` 또는 `CodexSandboxOnline/Offline` → 샌드박스가 ACL을 못 고침(`SetNamedSecurityInfoW failed: 5`) | §2.1 소유권 회수 |
| `Failed to authenticate: OAuth session expired and could not be refreshed` | Claude | 헤드리스에서 OAuth 액세스 토큰이 **자동 갱신되지 않음**(알려진 버그) | §2.2 장수명 토큰 |
| `Approval mode overridden to "default" because the current folder is not trusted` + `Error authenticating` | Gemini | 폴더 미신뢰 → safe mode → **프로젝트 `.env`·워크스페이스 설정 무시** → `GEMINI_API_KEY` 미주입 → 인증 실패 | §2.3 폴더 신뢰 + 키 위치 이동 |

> Gemini의 두 줄은 별개 사고가 아니라 **인과**다. 신뢰 경고를 "경고니까 무시"로 넘기면 바로 아래 인증 실패의 원인을 놓친다.

## 2. 레그별 복구

### 2.0 자동 복구 (권장)

2.1~2.3을 한 번에 처리한다. **일반 PowerShell에서 실행해도 된다** — 관리자 권한이 필요하면 스스로 UAC 승격 창을 띄운다.

```powershell
.\scripts\fix-chain.ps1 -WorkDir "C:\Users\PSH\MultiAgent"
```

한 번 실행으로 끝나는 순서:

1. 관리자 권한 자동 승격(UAC [예] 클릭)
2. 작업 폴더 소유권·ACL 회수 — 폴더가 없으면 `MultiAgent` 를 자동 탐색한다
3. `trustedFolders.json` 에 신뢰 항목 기록(대화형 `/permissions` 대체, 기존 항목 병합 + `.bak` 백업)
4. `claude setup-token` 을 직접 실행 → 브라우저 로그인 → 출력된 토큰을 붙여넣으면 환경변수 등록
5. `GEMINI_API_KEY` 붙여넣기(선택) → 환경변수 등록
6. `preflight-chain.ps1` 로 검증까지 이어서 실행

사람이 해야 하는 건 **UAC 승인 · 브라우저 로그인 · 토큰 붙여넣기** 세 가지뿐이다.
값을 미리 알고 있으면 프롬프트 없이 넘길 수도 있다:

```powershell
.\scripts\fix-chain.ps1 -ClaudeToken "<토큰>" -GeminiApiKey "<키>"
.\scripts\fix-chain.ps1 -NonInteractive   # 스케줄러에서 무인 실행 — 프롬프트 대신 TODO 로 보고
```

아래 2.1~2.3은 수동 절차와 그 원리다.

### 2.1 Codex — 샌드박스 셋업 실패

관리자 PowerShell에서 작업 폴더 소유권을 실사용자로 되돌린다.

```powershell
takeown /F "C:\Users\PSH\MultiAgent" /R /D Y
icacls  "C:\Users\PSH\MultiAgent" /grant "${env:USERDOMAIN}\${env:USERNAME}:(OI)(CI)(F)" /T
```

> `"$env:USERNAME:(OI)..."` 처럼 쓰면 PowerShell이 콜론까지 변수 이름으로 먹어 사용자명이 빈 값이 되고
> `매개 변수가 잘못되었습니다`로 실패한다(실측 2026-08-02). 반드시 `${env:USERNAME}`으로 경계를 닫는다.

- 확인: `(Get-Acl "C:\Users\PSH\MultiAgent").Owner` 가 `PSH` 계정이면 정상. `CodexSandboxOnline`·`BUILTIN\Administrators`면 아직 원인이 남아 있다.
- 샌드박스가 실패한 뒤 폴더 소유자가 샌드박스 계정으로 **바뀌어 있는 경우**가 있다 — 실패할 때마다 소유자를 다시 확인한다.
- 그래도 안 되면 최후수단으로 격리를 낮춘다(권한 축소 손실을 감수하는 선택이므로 **작업 폴더 한정**으로만):
  `codex exec --sandbox danger-full-access ...` 또는 `~/.codex/config.toml`의 `[windows] sandbox = "elevated"`.

### 2.2 Claude — OAuth 세션 만료

무인 실행에서는 브라우저 재로그인 폴백이 존재하지 않는다. 1년짜리 토큰을 한 번 발급해 **서비스 환경변수**로 고정한다.

```powershell
claude setup-token                      # 대화형으로 1회만 — 장수명 OAuth 토큰 출력
[Environment]::SetEnvironmentVariable('CLAUDE_CODE_OAUTH_TOKEN', '<발급된 토큰>', 'User')
```

- 봇을 서비스/스케줄러로 돌린다면 **그 프로세스가 상속하는** 환경에 넣어야 한다. 대화형 셸에만 넣으면 자비스 루틴에는 안 잡힌다. 등록 후 봇 프로세스를 재시작해야 반영된다.
- `ANTHROPIC_API_KEY`가 설정돼 있으면 Claude Code가 그쪽을 먼저 쓴다 — 구독이 아니라 **API 종량과금**으로 청구되니 의도한 경우에만 둔다.
- 토큰도 1년 뒤 만료된다. 발급일을 `learnings.md`에 남겨 둔다.

### 2.3 Gemini — 폴더 미신뢰 → 인증 실패

```
gemini
> /permissions        # → Trust folder (또는 Trust parent folder)
```

- 신뢰 상태는 `~/.gemini/trustedFolders.json`(경로 → `TRUST_FOLDER` | `TRUST_PARENT` | `DO_NOT_TRUST`)에 저장된다. **손으로 편집하지 않는다** — 부모의 `TRUST_FOLDER`가 자식의 `DO_NOT_TRUST`를 덮는 알려진 버그가 있어 의도와 다르게 굳는다. `/permissions` 또는 `fix-chain.ps1`(작업 폴더 경로에 정확히 `TRUST_FOLDER`만 병합하고 `.bak` 백업을 남긴다)을 쓴다.
- **API 키를 프로젝트 `.env`에 두지 않는다.** 미신뢰 폴더에서는 `.env`가 통째로 무시되므로, 신뢰가 풀리는 순간 키까지 같이 사라져 인증 실패로 번진다. `GEMINI_API_KEY`는 사용자/머신 환경변수에 둔다.
- `fix-chain.ps1`은 `AIza...` ASCII 형식이 아닌 값을 API 키로 인정하지 않는다. 잘못된 저장값 때문에 CLI가 깨지면 키 인증 선택을 해제하고 올바른 키 교체를 TODO로 남긴다.
- Gemini CLI OAuth가 429·지원종료로 실패해도 실제 멀티모델 체계의 Antigravity Gemini가 `PONG`이면 프리플라이트의 Gemini 레그는 그 실경로로 통과한다.
- 신뢰 프롬프트 자체를 무인 환경에서 없애려면 `~/.gemini/settings.json`에 `{"security":{"folderTrust":{"enabled":false}}}` — 안전장치를 끄는 선택이므로 개인 머신에 한정한다.

## 3. 무인 실행 3원칙 (재발 방지)

1. **대화형 폴백에 의존하지 않는다** — 세 CLI 모두 키/토큰을 환경변수로 미리 주입. 브라우저 로그인·신뢰 확인·승인 프롬프트가 뜨는 경로는 무인 실행에서 전부 실패다.
2. **키는 프로젝트 밖에 둔다** — 프로젝트 `.env`는 신뢰·샌드박스 상태에 따라 무시된다. 사용자/머신 환경변수가 유일하게 안정적이다.
3. **루틴 시작 전에 프리플라이트를 돌린다** — §4. 세 레그가 다 죽은 뒤 로그를 읽는 것보다 30초 먼저 아는 편이 싸다.

## 4. 스크립트

| 스크립트 | 용도 |
|---|---|
| `scripts/fix-chain.ps1` | 복구. 소유권·신뢰·환경변수를 자동 처리하고 끝에서 검증한다(§2.0) |
| `scripts/preflight-chain.ps1` | 점검. 루틴 시작 직전에 실행한다. **종료 코드 = 실패한 레그 수** |
| `scripts/guardian-run.ps1` | 자가 점검 1회분 — 점검 → 무인 복구 → 재점검 → 로그 |
| `scripts/install-guardian.ps1` | 위를 Windows 예약 작업으로 상주시킨다(로그온 시 + 60분마다) |

**상주 등록은 옵트인이다** — `fix-chain.ps1 -InstallGuardian` 을 줘야 등록한다. 기본으로 켜면
사용자 화면에 주기적으로 창이 뜨는 부작용이 있어 기본값에서 뺐다. 등록하면 예약 작업이
최고 권한으로 **창 없이**(wscript 창스타일 0) 돌면서 소유권 회수·폴더 신뢰처럼
무인으로 가능한 복구는 스스로 끝내고, 브라우저 로그인이 필요한 토큰 재발급 같은 잔여 항목만 로그에 남긴다.
VBS는 PowerShell 종료까지 기다린 뒤 `WScript.Quit`로 실제 실패 레그 수를 예약 작업에 전달한다.
예약 작업은 기존 작업을 먼저 삭제하지 않고 `-Force`로 갱신하며, `IgnoreNew`·30분 실행 제한·10년 반복 기간을 사용한다.

가디언에는 폭주 방지 장치가 둘 있다.
- `fix-chain` 호출 시 **`-SkipGuardian` 필수** — 빼면 fix-chain 이 예약 작업을 재등록·즉시 실행해서
  guardian → fix-chain → guardian 무한 재기동이 된다(실측 2026-08-03, 약 2분 주기로 창이 떴다).
- **고칠 수 있는 증상일 때만** 복구하고, 같은 증상에는 쿨다운(기본 6시간)을 둔다.
  인증 만료·쿼터 소진에 소유권 회수와 신뢰 파일 수정을 매시간 반복하면 무의미한 변경만 쌓인다.

```powershell
.\scripts\install-guardian.ps1 -WorkDir "C:\Users\PSH\MultiAgent"   # 등록(+즉시 1회 실행)
.\scripts\install-guardian.ps1 -Uninstall                            # 해제
Get-Content "C:\Users\PSH\MultiAgent\_shared\chain-guardian.log" -Tail 20   # 이력
```

> **CLI 는 호출 연산자(`&`)로 실행한다.** npm 전역 설치는 같은 이름으로 `.cmd`·`.ps1` 을 함께 깔고,
> 어느 쪽이 잡히는지는 환경마다 다르다. `Start-Process` 는 `.ps1` 을 실행하지 못해
> `%1은(는) 올바른 Win32 응용 프로그램이 아닙니다` 로 죽는다(실측 2026-08-02). 타임아웃이 필요하면
> 별도 `powershell.exe`에서 호출 연산자로 실행하고 타임아웃이면 **그 PID 트리만** `taskkill /PID /T`로 종료한다.
> 이름 기반 종료는 사용자의 대화형 Codex·Claude·Gemini 세션까지 죽일 수 있어 금지한다.

> **JSON 은 BOM 없이 쓰고, 읽을 때는 인코딩을 명시한다.** `Get-Content` 는 PS 5.1 에서 BOM 없는 UTF-8 을
> 시스템 코드페이지(cp949)로 읽어 한글 경로를 깨뜨리고, 깨진 바이트가 JSON 이스케이프 오류로 이어진다
> (실측 2026-08-03 — `G:\내 드라이브\AUSURA` 가 `G:\????뱛볼????\AUSURA` 로 저장됐다).
> `[System.IO.File]::ReadAllText($p, [System.Text.Encoding]::UTF8)` 으로 읽고,
> 파싱에 실패하면 `.broken` 으로 보존한 뒤 새로 쓴다 — 깨진 파일을 붙들면 단계 전체가 죽는다.

> **상위 경로의 `DO_NOT_TRUST` 를 먼저 확인한다.** 하위 폴더를 아무리 신뢰시켜도 상위가 불신이면
> safe mode 로 떨어진다(실측 2026-08-03 — `"g:/": "DO_NOT_TRUST"` 가 볼트 전체를 막고 있었다).
> `fix-chain.ps1` 은 신뢰 대상의 상위에 걸린 불신 항목을 자동으로 걷어낸다.

> **두 스크립트는 UTF-8 BOM 으로 저장한다.** Windows PowerShell 5.1은 BOM 없는 파일을 시스템 코드페이지(cp949)로
> 읽어 한글이 깨지고, 깨진 바이트 때문에 `"<토큰>"` 의 `<` 가 리다이렉션 연산자로 파싱돼 스크립트 전체가
> `ParserError` 로 죽는다(실측 2026-08-02). 편집 도구가 BOM을 떼지 않는지 확인할 것.
> 같은 이유로 `trustedFolders.json` 은 반대로 **BOM 없이** 써야 한다 — gemini-cli 가 `JSON.parse` 로 읽는다.

```powershell
pwsh -File "<이 스킬>\scripts\preflight-chain.ps1" -WorkDir "C:\Users\PSH\MultiAgent"
```

- 각 레그에 `PONG` 스모크를 던지고, §1의 지문을 출력에서 직접 찾는다.
- CLI를 부르기 전에 정적 점검부터 한다: 작업 폴더 소유자, `CLAUDE_CODE_OAUTH_TOKEN`/`ANTHROPIC_API_KEY` 유무, `trustedFolders.json`의 신뢰 항목, `GEMINI_API_KEY` 유무.
- **exit 0이어도 지문이 잡히면 실패로 판정한다** — Gemini는 신뢰 경고를 뱉으면서도 성공 코드로 끝나는 경우가 있어, 코드만 보면 조용한 실패를 통과시킨다.

## 5. 보고 규칙

- 레그가 죽으면 **어느 레그가 어떤 지문으로 죽었는지** 보고에 명시한다. 2중을 3중이라고 보고하면 그 자체가 실패다(cross-review §4와 동일).
- "3중 전부 실패"는 모델 장애가 아니라 **환경 장애 신호**다. 모델을 바꾸거나 재시도를 늘리는 대응은 원인을 못 짚은 것이다 — §1로 돌아간다.
- 복구에 쓴 조치와 발급일자는 `C:\Users\PSH\MultiAgent\_shared\learnings.md`에 누적한다.

## 출처

- Codex Windows 샌드박스 소유권/ACL: [openai/codex#31414](https://github.com/openai/codex/issues/31414), [#29797](https://github.com/openai/codex/issues/29797), [#29867](https://github.com/openai/codex/issues/29867)
- Claude Code 헤드리스 OAuth 갱신 실패: [anthropics/claude-code#28827](https://github.com/anthropics/claude-code/issues/28827), [#50743](https://github.com/anthropics/claude-code/issues/50743)
- Gemini CLI 폴더 신뢰(safe mode에서 `.env`·워크스페이스 설정 무시): [Trusted Folders 문서](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/trusted-folders.md), 부모 신뢰 우선 버그 [google-gemini/gemini-cli#13125](https://github.com/google-gemini/gemini-cli/issues/13125)

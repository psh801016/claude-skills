# claude-skills — 동기화 가이드 (꼭 먼저 읽기)

이 저장소는 **Claude 스킬(skill) 파일들의 백업·동기화 본부**입니다.
핸드폰·웹·데스크탑 어디서 봐도 똑같이 보이게 하는 **단 하나의 원본(원천, single source of truth)** 이 바로 이 GitHub 저장소입니다.

---

## 1. 가장 중요한 개념 (이것만 이해하면 안 헷갈림)

```
[내 실제 데스크탑 PC]            [GitHub 저장소]                [핸드폰 / 웹 / 클라우드 세션]
  Claude 데스크탑 앱 스킬           ← push(올리기) →               화면에 보이는 내용
  Claude Code 스킬                                                = "GitHub에 올라간 것"만 보임
  (내 컴퓨터에만 있음)            ★ 모두가 보는 원본 ★
```

- **핸드폰 화면과 웹/클라우드 화면은 서로 다른 기기가 아니라, "GitHub에 올라간 같은 원본"을 보는 창입니다.**
- 그래서 **데스크탑 PC에서 작업해도, GitHub에 push 하기 전까지는 핸드폰·웹 어디에도 안 보입니다.**
- 안 보이는 게 고장이 아니라, **"아직 안 올린 것"** 입니다.

## 2. 자주 헷갈리는 상황과 답

| 증상 | 진짜 원인 | 해결 |
|------|-----------|------|
| "컴퓨터로 하던 게 핸드폰에 안 보여요" | 데스크탑에서 GitHub로 push 안 함 | 데스크탑에서 `sync-skills.sh` 실행 |
| "핸드폰이랑 데스크탑 화면이 달라요" | 한쪽이 옛날 버전(새로고침 안 됨) 또는 다른 브랜치를 봄 | 둘 다 같은 브랜치 보고 새로고침 |
| "자동 동기화라더니 안 됐어요" | 자동 장치가 원래 없었음(이름만 auto) | 작업 후 매번 sync 스크립트 직접 실행 |

> ⚠️ **자동(auto) 동기화는 없습니다.** 내 PC의 파일을 GitHub로 자동으로 올리는 건
> 내 PC 안에서 도는 프로그램만 할 수 있습니다(클라우드는 내 PC에 손을 못 댐).
> 그래서 "작업 끝 → sync 스크립트 한 번 실행"이 정식 흐름입니다.

## 3. 폴더 구조

```
claude-skills/
├── claude-code-skills/      # Claude Code(CLI/웹)용 스킬 (.md)
│   ├── attendance.md
│   └── instagram-analyze.md
└── claude-desktop-skills/   # Claude 데스크탑 앱용 스킬 (각 폴더에 SKILL.md)
    ├── arch-prompt-maker/
    ├── cinematic-exhibition-lighting/
    ├── interior-prompt-maker/
    ├── magnific-compositing-prep/
    ├── notion-bokhameham-auto-limit/
    ├── notion-calendar-sync/
    ├── notion-diary-upload/
    └── texture-prompt-maker/
```

## 4. 동기화 흐름 (정식 절차)

### A. 데스크탑에서 작업한 걸 핸드폰/웹에 보이게 하기 (올리기)
1. 데스크탑에서 스킬 작업/수정
2. **PowerShell** 을 열고 이 저장소 폴더로 이동 (`cd` 로 이동)
3. `.\sync-skills.ps1 "무엇을 바꿨는지 메모"` 실행  ← **윈도우는 이거**
   - (Mac/Git Bash 라면 `./sync-skills.sh "메모"`)
4. → 자동으로 GitHub에 올라감 → 핸드폰·웹 새로고침하면 보임

> 윈도우에서 처음 한 번만: PowerShell에서
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` 실행(스크립트 허용).

### B. 어디서든 최신 상태 받기 (내려받기)
- 데스크탑: `git pull origin (현재 브랜치)`
- 핸드폰/웹: 세션을 새로 열거나 새로고침 (항상 최신 GitHub를 봄)

### 윈도우 스킬 원본 위치 (참고)
- 데스크탑 앱 스킬: `%APPDATA%\Claude\skills`
- Claude Code 스킬: `%USERPROFILE%\.claude\skills`
- 위치가 다르면 `sync-skills.ps1` 위쪽의 경로 변수를 고치면 됩니다.

## 5. 한눈 점검 (헷갈릴 때)
```bash
git status        # 안 올린 변경사항이 있는지
git log -1        # 마지막으로 올라간 게 언제인지
git branch        # 지금 어느 브랜치를 보는지
```
이 세 줄이 "지금 내가 보는 게 최신인지"를 알려줍니다.

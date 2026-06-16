# sync-skills.ps1  (윈도우용)
#
# 내 윈도우 PC의 Claude 스킬을 이 저장소로 모아서 GitHub에 올립니다.
# 이걸 실행해야 핸드폰/웹에서도 같은 내용이 보입니다.
#
# 사용법 (PowerShell 에서):
#   처음 한 번만 허용 설정:
#     Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
#   실행:
#     .\sync-skills.ps1 "무엇을 바꿨는지 한 줄 메모"
#   (메모를 안 적으면 날짜로 자동 기록)

param(
  [string]$Message = ("Sync skills " + (Get-Date -Format "yyyy-MM-dd HH:mm"))
)

$ErrorActionPreference = "Stop"

# ── 1. 내 윈도우 PC의 스킬 원본 위치 (※ 다르면 여기 수정) ──────────────────
#   Claude 데스크탑 앱 스킬: 보통 %APPDATA%\Claude\skills
#   Claude Code 스킬:        보통 %USERPROFILE%\.claude\skills
$SrcDesktopSkills = if ($env:SRC_DESKTOP_SKILLS) { $env:SRC_DESKTOP_SKILLS } else { Join-Path $env:APPDATA "Claude\skills" }
$SrcCodeSkills    = if ($env:SRC_CODE_SKILLS)    { $env:SRC_CODE_SKILLS }    else { Join-Path $env:USERPROFILE ".claude\skills" }

# ── 2. 이 저장소 안의 대상 폴더 (수정 불필요) ─────────────────────────────
$RepoDir     = Split-Path -Parent $MyInvocation.MyCommand.Path
$DstDesktop  = Join-Path $RepoDir "claude-desktop-skills"
$DstCode     = Join-Path $RepoDir "claude-code-skills"

Set-Location $RepoDir
$Branch = (git rev-parse --abbrev-ref HEAD).Trim()
Write-Host "▶ 저장소: $RepoDir (브랜치: $Branch)"

function Copy-IfExists($Src, $Dst, $Label) {
  if (Test-Path $Src) {
    Write-Host "  ✔ $Label 복사: $Src → $Dst"
    New-Item -ItemType Directory -Force -Path $Dst | Out-Null
    # robocopy 로 원본을 저장소에 복사 (저장소에만 있는 파일은 지우지 않음)
    robocopy $Src $Dst /E /XF "*.DS_Store" /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy 실패 ($Label), 코드 $LASTEXITCODE" }
    $global:LASTEXITCODE = 0   # robocopy 는 성공해도 0이 아님 → 초기화
  } else {
    Write-Host "  ⚠ $Label 원본 폴더 없음 → 건너뜀: $Src"
    Write-Host "    (경로가 다르면 스크립트 위쪽 SrcDesktopSkills/SrcCodeSkills 를 고치세요)"
  }
}

Write-Host "▶ 윈도우 PC의 스킬을 저장소로 모으는 중..."
Copy-IfExists $SrcDesktopSkills $DstDesktop "데스크탑 앱 스킬"
Copy-IfExists $SrcCodeSkills    $DstCode    "Claude Code 스킬"

Write-Host "▶ 변경 사항 확인..."
$changes = git status --porcelain
if ([string]::IsNullOrWhiteSpace($changes)) {
  Write-Host "✅ 바뀐 게 없습니다. 이미 GitHub와 같은 상태예요. (올릴 것 없음)"
  exit 0
}

git add -A
git status --short

Write-Host "▶ GitHub에 올리는 중..."
git commit -m "$Message"

# push 실패 시(네트워크 문제) 지수 백오프로 최대 4회 재시도
foreach ($delay in 0,2,4,8) {
  if ($delay -gt 0) { Write-Host "  …$delay초 후 재시도"; Start-Sleep -Seconds $delay }
  git push -u origin $Branch
  if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 완료! 이제 핸드폰/웹을 새로고침하면 같은 내용이 보입니다."
    exit 0
  }
}

Write-Host "❌ push 실패. 인터넷 연결을 확인하고 다시 실행하세요."
exit 1

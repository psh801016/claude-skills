# sync-skills.ps1  (Windows)
# 내 PC의 Claude 스킬을 모아서 GitHub에 올립니다.
# 사용법: .\sync-skills.ps1 "메모"

param(
  [string]$Message = ("Sync skills " + (Get-Date -Format "yyyy-MM-dd HH:mm"))
)

$ErrorActionPreference = "Stop"

# 내 PC 스킬 원본 위치 (다르면 여기 수정)
$SrcDesktopSkills = if ($env:SRC_DESKTOP_SKILLS) { $env:SRC_DESKTOP_SKILLS } else { Join-Path $env:APPDATA "Claude\skills" }
$SrcCodeSkills    = if ($env:SRC_CODE_SKILLS)    { $env:SRC_CODE_SKILLS }    else { Join-Path $env:USERPROFILE ".claude\skills" }

$RepoDir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$DstDesktop = Join-Path $RepoDir "claude-desktop-skills"
$DstCode    = Join-Path $RepoDir "claude-code-skills"

Set-Location $RepoDir
$Branch = (git rev-parse --abbrev-ref HEAD).Trim()
Write-Host "[sync] 저장소: $RepoDir (브랜치: $Branch)"

function Copy-IfExists($Src, $Dst, $Label) {
  if (Test-Path $Src) {
    Write-Host "  [OK] $Label 복사: $Src -> $Dst"
    New-Item -ItemType Directory -Force -Path $Dst | Out-Null
    robocopy $Src $Dst /E /XF ".DS_Store" /NFL /NDL /NJH /NJS /NP | Out-Null
    $global:LASTEXITCODE = 0
  } else {
    Write-Host "  [건너뜀] 원본 폴더 없음: $Src"
  }
}

Write-Host "[sync] 스킬 수집 중..."
Copy-IfExists $SrcDesktopSkills $DstDesktop "Claude 데스크탑 앱 스킬"
Copy-IfExists $SrcCodeSkills    $DstCode    "Claude Code 스킬"

Write-Host "[sync] 변경 사항 확인..."
$changes = git status --porcelain
if ([string]::IsNullOrWhiteSpace($changes)) {
  Write-Host "[완료] 바뀐 게 없습니다. GitHub와 이미 같은 상태."
  exit 0
}

git add -A
git status --short

Write-Host "[sync] GitHub에 올리는 중..."
git commit -m $Message

$delays = @(0, 2, 4, 8)
foreach ($delay in $delays) {
  if ($delay -gt 0) {
    Write-Host "  재시도 대기 ${delay}초..."
    Start-Sleep -Seconds $delay
  }
  git push -u origin $Branch
  if ($LASTEXITCODE -eq 0) {
    Write-Host "[완료] GitHub 업로드 성공! 핸드폰/웹을 새로고침하면 같은 내용이 보입니다."
    exit 0
  }
}

Write-Host "[오류] push 실패. 인터넷 연결을 확인하고 다시 실행하세요."
exit 1

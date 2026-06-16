# sync-skills.ps1 (Windows - 완전 자동)
param(
  [string]$Message = ("Sync skills " + (Get-Date -Format "yyyy-MM-dd HH:mm"))
)

$ErrorActionPreference = "Stop"
$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoDir

# 1) git 사용자 자동 설정
git config --global user.email "park801016@gmail.com"
git config --global user.name "PSH"

# 2) 스스로 최신 버전으로 업데이트
git fetch origin claude/local-network-device-sync-ddhiac 2>$null
git pull origin claude/local-network-device-sync-ddhiac 2>$null

# 3) 스킬 원본 위치
$SrcCode    = Join-Path $env:USERPROFILE ".claude\skills"
$SrcDesktop = Join-Path $env:APPDATA "Claude\skills"
$DstCode    = Join-Path $RepoDir "claude-code-skills"
$DstDesktop = Join-Path $RepoDir "claude-desktop-skills"

function Copy-IfExists($Src, $Dst) {
  if (Test-Path $Src) {
    New-Item -ItemType Directory -Force -Path $Dst | Out-Null
    robocopy $Src $Dst /E /XF ".DS_Store" /NFL /NDL /NJH /NJS /NP | Out-Null
    $global:LASTEXITCODE = 0
    Write-Host "[OK] 복사 완료: $Src"
  }
}

Copy-IfExists $SrcCode    $DstCode
Copy-IfExists $SrcDesktop $DstDesktop

# 4) 변경 없으면 종료
$changes = git status --porcelain
if ([string]::IsNullOrWhiteSpace($changes)) {
  Write-Host "[완료] 변경 없음. 이미 최신 상태."
  exit 0
}

# 5) commit + push
git add -A
git commit -m $Message

$delays = @(0, 2, 4, 8)
foreach ($d in $delays) {
  if ($d -gt 0) { Start-Sleep -Seconds $d }
  git push -u origin claude/local-network-device-sync-ddhiac
  if ($LASTEXITCODE -eq 0) {
    Write-Host "[완료] GitHub 업로드 성공!"
    exit 0
  }
}

Write-Host "[오류] push 실패. 인터넷 확인 후 재시도하세요."
exit 1

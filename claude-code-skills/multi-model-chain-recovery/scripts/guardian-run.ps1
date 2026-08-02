<#
.SYNOPSIS
    3중 체인 자가 점검·자가 복구 1회분. 예약 작업이 주기적으로 이걸 부른다.

.DESCRIPTION
    사람이 개입하지 않는 것을 전제로 한다.

      1. preflight-chain.ps1 실행
      2. 실패가 있으면 fix-chain.ps1 -NonInteractive 로 복구 시도
         (소유권 회수·폴더 신뢰 기록처럼 무인으로 가능한 것만 처리한다)
      3. 재점검 후 결과를 로그에 append
      4. 사람이 반드시 개입해야 하는 잔여 항목(토큰 재발급 등)만 따로 표시

    종료 코드 = 최종 실패 레그 수. 0 이면 3중 체인 정상.
#>
[CmdletBinding()]
param(
    [string]$WorkDir = 'C:\Users\PSH\MultiAgent',
    [string]$LogPath,
    [int]$TimeoutSec = 90
)

$ErrorActionPreference = 'Continue'
$here = $PSScriptRoot
$preflight = Join-Path $here 'preflight-chain.ps1'
$fix = Join-Path $here 'fix-chain.ps1'

if (-not $LogPath) {
    $LogPath = Join-Path $WorkDir '_shared\chain-guardian.log'
}

function Write-Log {
    param([string]$Text)
    $line = "[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Text
    Write-Output $line
    try {
        $dir = Split-Path -Parent $LogPath
        if ($dir -and -not (Test-Path -LiteralPath $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
        Add-Content -LiteralPath $LogPath -Value $line -Encoding utf8
    }
    catch { }   # 로그를 못 써도 점검 자체는 계속한다
}

function Invoke-Preflight {
    $out = & $preflight -WorkDir $WorkDir -TimeoutSec $TimeoutSec 2>&1 | Out-String
    return [pscustomobject]@{ Code = $LASTEXITCODE; Text = $out }
}

if (-not (Test-Path -LiteralPath $preflight)) {
    Write-Log "guardian: preflight-chain.ps1 을 찾지 못했다 ($preflight)"
    exit 99
}

$first = Invoke-Preflight
if ($first.Code -eq 0) {
    Write-Log 'guardian: 정상 — 3중 체인 이상 없음'
    exit 0
}

Write-Log "guardian: 실패 레그 $($first.Code)개 감지 — 자동 복구 시도"
foreach ($line in ($first.Text -split "`r?`n" | Where-Object { $_ -match '^\[' })) {
    Write-Log "  before: $line"
}

if (Test-Path -LiteralPath $fix) {
    $fixOut = & $fix -WorkDir $WorkDir -NonInteractive -NoElevate -SkipVerify 2>&1 | Out-String
    foreach ($line in ($fixOut -split "`r?`n" | Where-Object { $_ -match '^\[|^남은 작업' })) {
        Write-Log "  fix: $line"
    }
}
else {
    Write-Log "  fix: fix-chain.ps1 을 찾지 못했다 — 재점검만 수행"
}

$second = Invoke-Preflight
if ($second.Code -eq 0) {
    Write-Log 'guardian: 자동 복구 성공 — 3중 체인 정상'
    exit 0
}

Write-Log "guardian: 자동 복구 후에도 실패 레그 $($second.Code)개 — 사람 개입 필요"
foreach ($line in ($second.Text -split "`r?`n" | Where-Object { $_ -match '^\[' })) {
    Write-Log "  after: $line"
}

# 무인으로 못 고치는 대표 사례를 명시한다.
if ($second.Text -match 'OAuth 만료') {
    Write-Log '  → Claude 토큰은 브라우저 로그인이 필요하다: claude setup-token 후 fix-chain.ps1 -ClaudeToken "<토큰>"'
}
if ($second.Text -match '소유권|ACL') {
    Write-Log '  → 소유권 회수는 관리자 권한이 필요하다: 관리자 PowerShell 에서 fix-chain.ps1 재실행'
}

exit $second.Code

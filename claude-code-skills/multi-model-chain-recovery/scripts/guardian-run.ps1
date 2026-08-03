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
    [int]$TimeoutSec = 90,
    [int]$RepairCooldownHours = 6
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

Write-Log "guardian: 실패 레그 $($first.Code)개 감지"
foreach ($line in ($first.Text -split "`r?`n" | Where-Object { $_ -match '^\[' })) {
    Write-Log "  before: $line"
}

# 복구를 언제나 돌리지 않는다 — fix-chain 이 실제로 고칠 수 있는 증상일 때만 손을 댄다.
# (인증 만료·쿼터 소진에 소유권 회수와 신뢰 파일 수정을 매시간 반복하면 무의미한 변경만 쌓인다.)
$needOwnership = $first.Text -match '소유권|ACL|샌드박스'
$needTrust     = $first.Text -match '미신뢰|not trusted'
$repairable    = $needOwnership -or $needTrust

# 같은 증상으로 계속 실패할 때 매시간 같은 수정을 반복하지 않도록 쿨다운을 둔다.
$statePath = Join-Path (Split-Path -Parent $LogPath) 'chain-guardian.state'
$lastRepair = try {
    if (Test-Path -LiteralPath $statePath) { [datetime](Get-Content -LiteralPath $statePath -Raw).Trim() } else { $null }
} catch { $null }
$cooledDown = (-not $lastRepair) -or ((Get-Date) - $lastRepair).TotalHours -ge $RepairCooldownHours

if (-not $repairable) {
    Write-Log '  복구 생략 — fix-chain 이 고칠 수 있는 증상이 아니다(인증·쿼터·타임아웃은 사람 또는 재시도 영역)'
}
elseif (-not $cooledDown) {
    Write-Log "  복구 생략 — 마지막 복구 시도 이후 $RepairCooldownHours 시간이 지나지 않았다 ($lastRepair)"
}
elseif (-not (Test-Path -LiteralPath $fix)) {
    Write-Log '  fix-chain.ps1 을 찾지 못했다 — 재점검만 수행'
}
else {
    Write-Log '  자동 복구 시도'
    # -SkipGuardian 필수: fix-chain 의 마지막 단계가 예약 작업을 재등록하고 즉시 실행하므로,
    # 빼면 guardian → fix-chain → guardian 무한 재기동이 된다(실측 2026-08-03, 약 2분 주기로 창이 떴다).
    # 배열 splat 은 위치 인수로 넘어간다 — 이름 있는 스위치를 넘기려면 해시테이블이어야 한다.
    $fixArgs = @{
        WorkDir        = $WorkDir
        NonInteractive = $true
        NoElevate      = $true
        SkipVerify     = $true
        SkipGuardian   = $true
    }
    if (-not $needOwnership) { $fixArgs['SkipOwnership'] = $true }

    $fixOut = & $fix @fixArgs 2>&1 | Out-String
    foreach ($line in ($fixOut -split "`r?`n" | Where-Object { $_ -match '^\[|^남은 작업' })) {
        Write-Log "  fix: $line"
    }
    try { Set-Content -LiteralPath $statePath -Value (Get-Date).ToString('o') -Encoding utf8 } catch { }
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

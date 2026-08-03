<#
.SYNOPSIS
    3중 체인 자가 점검·자가 복구를 Windows 예약 작업으로 상주시킨다.

.DESCRIPTION
    한 번 등록해 두면 사람이 다시 명령을 칠 일이 없다.
    등록된 작업은 guardian-run.ps1 을 주기적으로 실행해서
    점검 → 실패 시 무인 복구 → 재점검 → 로그 기록까지 스스로 한다.

    - 로그온 직후 1회, 이후 지정 간격(기본 60분)마다 실행
    - 최고 권한으로 실행(소유권 회수에 관리자 권한이 필요하다)
    - 창을 띄우지 않는다

.EXAMPLE
    # 관리자 PowerShell — 등록
    .\install-guardian.ps1 -WorkDir "C:\Users\PSH\MultiAgent"

.EXAMPLE
    # 해제
    .\install-guardian.ps1 -Uninstall
#>
[CmdletBinding()]
param(
    [string]$WorkDir = 'C:\Users\PSH\MultiAgent',
    [string]$TaskName = 'multi-model-chain-guardian',
    [int]$IntervalMinutes = 60,
    [switch]$Uninstall
)

$ErrorActionPreference = 'Stop'
$isWin = ($null -eq $IsWindows) -or $IsWindows

if (-not $isWin) {
    Write-Output '이 스크립트는 Windows 예약 작업 전용입니다.'
    exit 0
}

if (-not (Get-Command Register-ScheduledTask -ErrorAction SilentlyContinue)) {
    Write-Output 'ScheduledTasks 모듈이 없습니다 — schtasks.exe 로 직접 등록해 주세요.'
    exit 1
}

if ($Uninstall) {
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Output "예약 작업 '$TaskName' 을 해제했습니다."
    }
    catch { Write-Output "해제할 작업이 없습니다: $TaskName" }
    exit 0
}

$runner = Join-Path $PSScriptRoot 'guardian-run.ps1'
if (-not (Test-Path -LiteralPath $runner)) {
    Write-Error "guardian-run.ps1 을 찾지 못했습니다: $runner"
    exit 99
}

# Windows PowerShell 5.1 을 명시적으로 쓴다 — pwsh 가 없는 환경에서도 동작해야 한다.
$psExe = Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe'
if (-not (Test-Path -LiteralPath $psExe)) { $psExe = 'powershell.exe' }

# powershell.exe 는 콘솔 앱이라 예약 작업이 직접 띄우면 -WindowStyle Hidden 을 줘도
# 검은 창이 깜빡인다(실측 2026-08-02 — 사용자 화면에 매시간 터미널이 떴다).
# wscript 로 창 스타일 0(숨김) 으로 감싸서 완전히 조용하게 만든다.
$launchDir = Join-Path $env:LOCALAPPDATA 'multi-model-chain-guardian'
if (-not (Test-Path -LiteralPath $launchDir)) {
    New-Item -ItemType Directory -Path $launchDir -Force | Out-Null
}
$vbsPath = Join-Path $launchDir 'guardian-launch.vbs'

$psCommand = '{0} -NoProfile -ExecutionPolicy Bypass -File "{1}" -WorkDir "{2}"' -f $psExe, $runner, $WorkDir
$vbsBody = 'CreateObject("WScript.Shell").Run "{0}", 0, False' -f ($psCommand -replace '"', '""')
[System.IO.File]::WriteAllText($vbsPath, $vbsBody, (New-Object System.Text.ASCIIEncoding))

$wscript = Join-Path $env:WINDIR 'System32\wscript.exe'
if (-not (Test-Path -LiteralPath $wscript)) { $wscript = 'wscript.exe' }

$action = New-ScheduledTaskAction -Execute $wscript -Argument ('"{0}"' -f $vbsPath) -WorkingDirectory $launchDir

$triggers = @(
    New-ScheduledTaskTrigger -AtLogOn
    New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(2) `
        -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes)
)

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 15) `
    -MultipleInstances IgnoreNew

$principal = New-ScheduledTaskPrincipal -UserId ("{0}\{1}" -f $env:USERDOMAIN, $env:USERNAME) `
    -LogonType Interactive -RunLevel Highest

try {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $triggers `
        -Settings $settings -Principal $principal `
        -Description '3중 체인(Codex/Claude/Gemini) 자가 점검 및 무인 복구' | Out-Null

    Write-Output "예약 작업 '$TaskName' 등록 완료 — 로그온 시 + $IntervalMinutes 분마다 자동 점검합니다."
    Write-Output "로그: $(Join-Path $WorkDir '_shared\chain-guardian.log')"
    Write-Output '지금 즉시 1회 실행합니다...'
    Start-ScheduledTask -TaskName $TaskName
    exit 0
}
catch {
    Write-Error "등록 실패: $($_.Exception.Message)"
    exit 1
}

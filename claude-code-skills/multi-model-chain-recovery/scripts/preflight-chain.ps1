<#
.SYNOPSIS
    Codex / Claude / Gemini 3중 체인 프리플라이트.

.DESCRIPTION
    자동 루틴(지혜 승격·cross-review 등)을 시작하기 전에 세 레그가 실제로 살아 있는지 확인한다.
    레그마다 (1) CLI를 부르지 않는 정적 점검, (2) PONG 스모크 호출을 수행하고,
    출력에서 알려진 실패 지문을 직접 찾는다. 종료 코드는 실패한 레그 수.

    exit 0 이어도 지문이 잡히면 실패로 판정한다 — Gemini는 신뢰 경고를 뱉으면서
    성공 코드로 끝나는 경우가 있어, 종료 코드만 믿으면 조용한 실패를 통과시킨다.

.EXAMPLE
    pwsh -File preflight-chain.ps1 -WorkDir "C:\Users\PSH\MultiAgent"
#>
[CmdletBinding()]
param(
    [string]$WorkDir = (Get-Location).Path,
    [int]$TimeoutSec = 90,
    [ValidateSet('codex', 'claude', 'gemini')]
    [string[]]$Only
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $WorkDir)) {
    Write-Error "작업 폴더가 없다: $WorkDir"
    exit 99
}
$WorkDir = (Resolve-Path -LiteralPath $WorkDir).Path

# 알려진 실패 지문 — SKILL.md §1 과 같은 목록을 유지한다.
$Fingerprints = @(
    @{ Pattern = 'helper_unknown_error|setup refresh had errors|SetNamedSecurityInfoW'
       Cause   = 'Codex 샌드박스 셋업 실패 — 작업 폴더 소유권/ACL'
       Fix     = 'takeown /F "<WorkDir>" /R /D Y  (SKILL.md 2.1)' }
    @{ Pattern = 'OAuth session expired|could not be refreshed|Failed to authenticate'
       Cause   = 'Claude OAuth 만료 — 헤드리스에서 자동 갱신 안 됨'
       Fix     = 'claude setup-token → CLAUDE_CODE_OAUTH_TOKEN 등록 (SKILL.md 2.2)' }
    @{ Pattern = 'is not trusted|folder trust'
       Cause   = 'Gemini 폴더 미신뢰 → safe mode(.env·워크스페이스 설정 무시)'
       Fix     = 'gemini 안에서 /permissions → Trust folder (SKILL.md 2.3)' }
    @{ Pattern = 'Error authenticating|RESOURCE_EXHAUSTED|Invalid API key|401 Unauthorized'
       Cause   = '인증 실패 또는 쿼터 소진'
       Fix     = 'API 키를 사용자/머신 환경변수로 이동 후 프로세스 재시작' }
)

function Find-Fingerprint {
    param([string]$Text)
    if ([string]::IsNullOrWhiteSpace($Text)) { return $null }
    foreach ($fp in $Fingerprints) {
        if ($Text -match $fp.Pattern) { return $fp }
    }
    return $null
}

function Format-CliArg {
    param([string]$Value)
    if ($Value -match '[\s"]') { '"' + ($Value -replace '"', '\"') + '"' } else { $Value }
}

function Resolve-CliTarget {
    <#
      npm 전역 설치는 같은 이름으로 .ps1 / .cmd / 확장자 없는 셸 스크립트를 함께 깐다.
      PowerShell 의 Get-Command 는 .ps1 을 먼저 집는데, Start-Process 는 .ps1 을 실행하지 못하고
      "%1은(는) 올바른 Win32 응용 프로그램이 아닙니다" 로 죽는다(실측 2026-08-02).
      실행 가능한 형태를 골라 필요한 인터프리터를 앞에 붙여서 돌려준다.
    #>
    param([string]$Exe)

    $all = @(Get-Command $Exe -All -ErrorAction SilentlyContinue)
    if ($all.Count -eq 0) { return $null }

    $exe = $all | Where-Object { $_.Source -match '\.exe$' } | Select-Object -First 1
    if ($exe) { return @{ File = $exe.Source; Pre = @() } }

    $shim = $all | Where-Object { $_.Source -match '\.(cmd|bat)$' } | Select-Object -First 1
    if ($shim) { return @{ File = $env:ComSpec; Pre = @('/c', (Format-CliArg $shim.Source)) } }

    $ps1 = $all | Where-Object { $_.Source -match '\.ps1$' } | Select-Object -First 1
    if ($ps1) {
        $psExe = try { (Get-Process -Id $PID).Path } catch { 'powershell.exe' }
        return @{ File = $psExe
                  Pre  = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', (Format-CliArg $ps1.Source)) }
    }

    $any = $all | Where-Object { $_.Source } | Select-Object -First 1
    if ($any) { return @{ File = $any.Source; Pre = @() } }
    return $null
}

function Invoke-Smoke {
    param(
        [string]$Exe,
        [string[]]$CliArgs,
        [int]$TimeoutSeconds,
        [string]$Cwd
    )

    $target = Resolve-CliTarget -Exe $Exe
    if (-not $target) {
        return [pscustomobject]@{ Found = $false; Code = -1; Output = ''; TimedOut = $false }
    }

    # Start-Process 는 -ArgumentList 원소를 그대로 이어 붙인다 — 공백이 든 인자는 직접 감싸야
    # 프롬프트가 여러 인자로 쪼개지지 않는다.
    $file = $target.File
    $argv = @($target.Pre) + @($CliArgs | ForEach-Object { Format-CliArg $_ })

    $outFile = [System.IO.Path]::GetTempFileName()
    $errFile = [System.IO.Path]::GetTempFileName()
    $timedOut = $false
    try {
        $proc = Start-Process -FilePath $file -ArgumentList $argv `
            -WorkingDirectory $Cwd -NoNewWindow -PassThru `
            -RedirectStandardOutput $outFile -RedirectStandardError $errFile

        if ($proc.WaitForExit($TimeoutSeconds * 1000)) {
            # 타임아웃 있는 WaitForExit 는 리다이렉트 스트림 flush 를 기다리지 않는다.
            # 인자 없는 WaitForExit 를 한 번 더 불러야 출력 파일이 완성된다.
            $proc.WaitForExit()
        }
        else {
            $timedOut = $true
            try { $proc.Kill($true) } catch { try { $proc.Kill() } catch { } }
            $proc.WaitForExit(5000) | Out-Null
        }
        $code = if ($timedOut) { -2 } else { $proc.ExitCode }

        # flush 가 늦는 경우가 있어 짧게 재확인한다(빈 출력을 오탐하지 않기 위해).
        $text = ''
        foreach ($attempt in 1..10) {
            $text = ((Get-Content -LiteralPath $outFile -Raw -ErrorAction SilentlyContinue) + "`n" +
                     (Get-Content -LiteralPath $errFile -Raw -ErrorAction SilentlyContinue))
            if (-not [string]::IsNullOrWhiteSpace($text)) { break }
            Start-Sleep -Milliseconds 100
        }
        return [pscustomobject]@{ Found = $true; Code = $code; Output = $text; TimedOut = $timedOut }
    }
    finally {
        Remove-Item -LiteralPath $outFile, $errFile -Force -ErrorAction SilentlyContinue
    }
}

function New-Result {
    param([string]$Leg, [string]$Status, [string]$Detail, [string]$Fix = '')
    [pscustomobject]@{ Leg = $Leg; Status = $Status; Detail = $Detail; Fix = $Fix }
}

function Test-Leg {
    param([string]$Leg, [string]$Exe, [string[]]$CliArgs, [string[]]$StaticWarnings)

    $smoke = Invoke-Smoke -Exe $Exe -CliArgs $CliArgs -TimeoutSeconds $TimeoutSec -Cwd $WorkDir
    if (-not $smoke.Found) {
        return New-Result $Leg 'FAIL' "$Exe 을(를) PATH에서 찾을 수 없다" '설치 또는 PATH 확인'
    }

    $fp = Find-Fingerprint -Text $smoke.Output
    if ($fp) {
        return New-Result $Leg 'FAIL' $fp.Cause ($fp.Fix -replace '<WorkDir>', $WorkDir)
    }
    if ($smoke.TimedOut) {
        return New-Result $Leg 'FAIL' "스모크 타임아웃(${TimeoutSec}s)" '프록시/네트워크 확인 후 -TimeoutSec 상향'
    }
    if ($smoke.Code -ne 0) {
        $tail = ($smoke.Output -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 1)
        return New-Result $Leg 'FAIL' "종료 코드 $($smoke.Code): $tail" '위 출력으로 SKILL.md 1절 지문 대조'
    }
    if ($smoke.Output -notmatch 'PONG') {
        return New-Result $Leg 'FAIL' 'PONG 미응답(빈 응답)' 'CLI 버전↔기본 모델 불일치 의심 — CLI 업그레이드'
    }

    if ($StaticWarnings.Count -gt 0) {
        return New-Result $Leg 'WARN' ($StaticWarnings -join ' / ') '지금은 통과하나 무인 실행에서 깨진다'
    }
    return New-Result $Leg 'OK' 'PONG 응답 확인' ''
}

# ── 정적 점검 ────────────────────────────────────────────────────────────────

function Get-CodexWarnings {
    $warn = @()
    # 소유권/ACL 은 Windows 샌드박스 전용 문제다 — 다른 OS 에서는 점검 대상이 아니다.
    $isWin = ($null -eq $IsWindows) -or $IsWindows   # PS 5.1 에는 $IsWindows 가 없다
    if (-not $isWin) { return $warn }
    try {
        $owner = (Get-Acl -LiteralPath $WorkDir).Owner
        if ($owner -match 'CodexSandbox|BUILTIN\\Administrators|S-1-5-32-544') {
            $warn += "작업 폴더 소유자가 '$owner' — 샌드박스가 ACL을 못 고친다"
        }
    }
    catch {
        $warn += "소유권 확인 실패: $($_.Exception.Message)"
    }
    return $warn
}

function Get-ClaudeWarnings {
    $warn = @()
    if (-not $env:CLAUDE_CODE_OAUTH_TOKEN -and -not $env:ANTHROPIC_API_KEY) {
        $warn += 'CLAUDE_CODE_OAUTH_TOKEN·ANTHROPIC_API_KEY 둘 다 없음 — 세션 만료 시 무인 복구 불가'
    }
    return $warn
}

function Get-GeminiWarnings {
    $warn = @()
    if (-not $env:GEMINI_API_KEY -and -not $env:GOOGLE_API_KEY) {
        $warn += 'GEMINI_API_KEY 가 프로세스 환경에 없음 — 프로젝트 .env 의존이면 미신뢰 시 인증 실패'
    }

    $trustPath = if ($env:GEMINI_CLI_TRUSTED_FOLDERS_PATH) {
        $env:GEMINI_CLI_TRUSTED_FOLDERS_PATH
    } else {
        Join-Path $HOME '.gemini/trustedFolders.json'
    }

    if (-not (Test-Path -LiteralPath $trustPath)) {
        $warn += "trustedFolders.json 없음 ($trustPath) — 신뢰 결정이 저장된 적 없다"
        return $warn
    }

    try {
        $trust = Get-Content -LiteralPath $trustPath -Raw | ConvertFrom-Json

        # 정상 스키마는 경로 → TRUST_FOLDER|TRUST_PARENT|DO_NOT_TRUST 맵이지만,
        # 경로 배열로 저장된 버전도 있어 둘 다 받는다.
        # ConvertFrom-Json 은 배열을 파이프라인으로 풀어 놓으므로 @() 로 다시 묶어서 판별한다.
        $items = @($trust)
        $entries = if ($items.Count -gt 0 -and $items[0] -is [string]) {
            $items | ForEach-Object { [pscustomobject]@{ Name = $_; Value = 'TRUST_FOLDER' } }
        } else {
            $items | ForEach-Object { $_.PSObject.Properties } |
                ForEach-Object { [pscustomobject]@{ Name = $_.Name; Value = $_.Value } }
        }

        $trusted = $false
        $decided = $false
        foreach ($entry in $entries) {
            $p = try { (Resolve-Path -LiteralPath $entry.Name -ErrorAction Stop).Path } catch { $entry.Name }
            $isSelf = $p.TrimEnd('\', '/') -ieq $WorkDir.TrimEnd('\', '/')
            $isAncestor = $WorkDir.StartsWith($p.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)
            if ($isSelf -and $entry.Value -in @('TRUST_FOLDER', 'TRUST_PARENT')) { $trusted = $true }
            if ($isAncestor -and $entry.Value -eq 'TRUST_PARENT') { $trusted = $true }
            if ($isSelf -and $entry.Value -eq 'DO_NOT_TRUST') {
                $warn += "작업 폴더가 DO_NOT_TRUST 로 저장돼 있다 — /permissions 로 변경"
                $decided = $true
            }
        }
        if (-not $trusted -and -not $decided) {
            $warn += "작업 폴더에 대한 신뢰 항목 없음 — safe mode 진입 가능"
        }
    }
    catch {
        $warn += "trustedFolders.json 파싱 실패: $($_.Exception.Message)"
    }
    return $warn
}

# ── 실행 ────────────────────────────────────────────────────────────────────

$targets = if ($Only) { $Only } else { @('codex', 'claude', 'gemini') }
$prompt = 'Reply with exactly one word: PONG'
$results = @()

Write-Output "3중 체인 프리플라이트 — WorkDir: $WorkDir (timeout ${TimeoutSec}s)`n"

if ($targets -contains 'codex') {
    $results += Test-Leg -Leg 'Codex' -Exe 'codex' -CliArgs @('exec', $prompt) -StaticWarnings (Get-CodexWarnings)
}
if ($targets -contains 'claude') {
    $results += Test-Leg -Leg 'Claude' -Exe 'claude' -CliArgs @('-p', $prompt) -StaticWarnings (Get-ClaudeWarnings)
}
if ($targets -contains 'gemini') {
    $results += Test-Leg -Leg 'Gemini' -Exe 'gemini' -CliArgs @('-p', $prompt) -StaticWarnings (Get-GeminiWarnings)
}

# Format-Table 은 출력이 파이프/파일로 리다이렉트되면(=봇이 캡처하는 그 상황) 폭을 못 잡아
# 빈 표를 뱉는다. 무인 실행이 주 용도이므로 직접 조립해서 Write-Output 으로 낸다.
foreach ($r in $results) {
    Write-Output ("[{0,-6}] {1,-6} {2}" -f $r.Leg, $r.Status, $r.Detail)
    if ($r.Fix) { Write-Output ("{0,-16}→ {1}" -f '', $r.Fix) }
}
Write-Output ''

$failed = @($results | Where-Object { $_.Status -eq 'FAIL' })
if ($failed.Count -gt 0) {
    Write-Output "실패 레그 $($failed.Count)개 ($(($failed.Leg) -join ', ')) — 루틴을 시작하지 말고 SKILL.md 2절 순서로 복구한다."
}
elseif (@($results | Where-Object { $_.Status -eq 'WARN' }).Count -gt 0) {
    Write-Output '지금은 통과하나 무인 실행에서 깨질 구성이 있다 — SKILL.md 3절 확인.'
}
else {
    Write-Output '3중 체인 정상.'
}

exit $failed.Count

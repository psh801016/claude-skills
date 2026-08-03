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

function Get-CliDiag {
    <#
      Get-Command 가 이 이름으로 무엇을 찾았는지 사람이 읽을 수 있게 요약한다.
      실행 자체는 Invoke-Smoke 가 호출 연산자로 하므로, 이 값은 진단용이다.
    #>
    param([string]$Exe)

    $all = @(Get-Command $Exe -All -ErrorAction SilentlyContinue)
    if ($all.Count -eq 0) { return 'Get-Command 결과 없음' }
    $resolved = foreach ($c in $all) {
        if ($c.CommandType -eq 'Alias' -and $c.ResolvedCommand) { $c.ResolvedCommand } else { $c }
    }
    return (($resolved | ForEach-Object { "$($_.CommandType):$($_.Source)" }) -join ', ')
}

function Invoke-Smoke {
    <#
      별도 powershell.exe에서 호출 연산자(&)로 CLI를 실행한다. 타임아웃이면 이번
      스모크가 만든 정확한 PID 트리만 종료한다. 이름 기반 종료는 사용자의 대화형
      Codex/Claude/Gemini 세션까지 죽일 수 있으므로 사용하지 않는다.
    #>
    param(
        [string]$Exe,
        [string[]]$CliArgs,
        [int]$TimeoutSeconds,
        [string]$Cwd
    )

    if (-not (Get-Command $Exe -ErrorAction SilentlyContinue)) {
        return [pscustomobject]@{ Found = $false; Code = -1; Output = ''
                                  TimedOut = $false; Diag = (Get-CliDiag $Exe) }
    }

    $payload = [ordered]@{ Exe = $Exe; Args = @($CliArgs); Cwd = $Cwd } |
        ConvertTo-Json -Depth 5 -Compress
    $payloadB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($payload))
    $bootstrap = @"
`$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = New-Object Text.UTF8Encoding(`$false)
`$json = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('$payloadB64'))
`$payload = `$json | ConvertFrom-Json
Set-Location -LiteralPath `$payload.Cwd
`$cliArgs = @(`$payload.Args)
& `$payload.Exe @cliArgs 2>&1 | Out-String | Write-Output
exit `$LASTEXITCODE
"@
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($bootstrap))
    $psExe = Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe'
    if (-not (Test-Path -LiteralPath $psExe)) { $psExe = 'powershell.exe' }
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $psExe
    $psi.Arguments = "-NoProfile -NonInteractive -ExecutionPolicy Bypass -EncodedCommand $encoded"
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.StandardOutputEncoding = New-Object Text.UTF8Encoding($false)
    $psi.StandardErrorEncoding = New-Object Text.UTF8Encoding($false)
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    try {
        if (-not $process.Start()) { throw "프로세스 시작 실패: $Exe" }
        $stdoutTask = $process.StandardOutput.ReadToEndAsync()
        $stderrTask = $process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
            try { & taskkill.exe /PID $process.Id /T /F 2>&1 | Out-Null }
            catch { try { $process.Kill() } catch { } }
            [void]$process.WaitForExit(5000)
            return [pscustomobject]@{ Found = $true; Code = -2
                                      Output = ([string]$stdoutTask.Result + [string]$stderrTask.Result)
                                      TimedOut = $true; Diag = "pid=$($process.Id) tree terminated" }
        }
        $process.WaitForExit()
        $text = [string]$stdoutTask.Result + [string]$stderrTask.Result
        return [pscustomobject]@{ Found = $true; Code = $process.ExitCode; Output = $text
                                  TimedOut = $false; Diag = '' }
    }
    catch {
        return [pscustomobject]@{ Found = $true; Code = -3; Output = $_.Exception.Message
                                  TimedOut = $false; Diag = '' }
    }
    finally {
        $process.Dispose()
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
        return New-Result $Leg 'FAIL' "$Exe 실행 파일을 찾지 못했다 — $($smoke.Diag)" '설치 또는 PATH 확인'
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
        # PS 5.1 의 Get-Content 는 BOM 없는 UTF-8 을 cp949 로 읽어 한글 경로를 깨뜨린다 —
        # 인코딩을 명시해서 읽는다(실측 2026-08-03).
        $trustRaw = [System.IO.File]::ReadAllText($trustPath, [System.Text.Encoding]::UTF8)
        $trust = $trustRaw | ConvertFrom-Json

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

        # 신뢰 파일에는 "g:/" 처럼 슬래시로 저장된 항목이 섞인다 — 구분자를 맞춰서 비교한다.
        $normWork = $WorkDir.Replace('/', '\').TrimEnd('\')

        $trusted = $false
        $decided = $false
        foreach ($entry in $entries) {
            $p = try { (Resolve-Path -LiteralPath $entry.Name -ErrorAction Stop).Path } catch { $entry.Name }
            $normP = $p.Replace('/', '\').TrimEnd('\')

            $isSelf = $normP -ieq $normWork
            $isAncestor = $normWork.StartsWith($normP + '\', [StringComparison]::OrdinalIgnoreCase)

            if ($isSelf -and $entry.Value -in @('TRUST_FOLDER', 'TRUST_PARENT')) { $trusted = $true }
            if ($isAncestor -and $entry.Value -eq 'TRUST_PARENT') { $trusted = $true }
            if ($isSelf -and $entry.Value -eq 'DO_NOT_TRUST') {
                $warn += '작업 폴더가 DO_NOT_TRUST 로 저장돼 있다 — /permissions 로 변경'
                $decided = $true
            }
            # 상위 경로의 DO_NOT_TRUST 는 하위 신뢰를 무력화한다(실측: "g:/" 가 볼트 전체를 막았다).
            if ($isAncestor -and $entry.Value -eq 'DO_NOT_TRUST') {
                $warn += "상위 경로 '$($entry.Name)' 가 DO_NOT_TRUST — 하위를 신뢰시켜도 safe mode 로 떨어진다"
                $decided = $true
            }
        }
        if (-not $trusted -and -not $decided) {
            $warn += '작업 폴더에 대한 신뢰 항목 없음 — safe mode 진입 가능'
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
    # --skip-git-repo-check: codex exec 는 git 저장소 밖이면 실행을 거부한다
    # ("Not inside a trusted directory and --skip-git-repo-check was not specified", 실측 2026-08-03).
    # 스모크는 어느 폴더에서든 떠야 하므로 항상 붙인다.
    $results += Test-Leg -Leg 'Codex' -Exe 'codex' `
        -CliArgs @('exec', '--skip-git-repo-check', $prompt) -StaticWarnings (Get-CodexWarnings)
}
if ($targets -contains 'claude') {
    $results += Test-Leg -Leg 'Claude' -Exe 'claude' -CliArgs @('-p', $prompt) -StaticWarnings (Get-ClaudeWarnings)
}
if ($targets -contains 'gemini') {
    $geminiResult = Test-Leg -Leg 'Gemini' -Exe 'gemini' -CliArgs @('-p', $prompt) -StaticWarnings (Get-GeminiWarnings)
    if ($geminiResult.Status -eq 'FAIL') {
        # Gemini CLI OAuth/free tier가 429 또는 지원종료여도 실제 멀티모델 체계는
        # Antigravity consult 경로를 사용한다. 그 실경로를 2차 스모크한다.
        $consult = 'C:\Users\PSH\dev\multi-model\consult.ps1'
        if (Test-Path -LiteralPath $consult) {
            $fallback = Test-Leg -Leg 'Gemini' -Exe 'powershell.exe' `
                -CliArgs @(
                    '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $consult,
                    '-Provider', 'gemini', '-Retries', '1',
                    '-TimeoutMs', ([string]($TimeoutSec * 1000)), '-Prompt', $prompt
                ) -StaticWarnings @()
            if ($fallback.Status -eq 'OK') {
                $fallback.Detail = 'PONG 응답 확인 (Antigravity Gemini 폴백)'
                $geminiResult = $fallback
            }
        }
    }
    $results += $geminiResult
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

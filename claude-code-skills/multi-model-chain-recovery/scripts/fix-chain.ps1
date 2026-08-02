<#
.SYNOPSIS
    Codex / Claude / Gemini 3중 체인 자동 복구.

.DESCRIPTION
    SKILL.md 2절의 복구 절차를 자동화한다. 자동화할 수 있는 것은 전부 자동으로 하고,
    사람이 반드시 해야 하는 것(브라우저 로그인)만 남겨서 안내한다.

      1. Codex — 작업 폴더 소유권/ACL 회수 (관리자 권한 필요)
      2. Gemini — trustedFolders.json 에 신뢰 항목을 직접 기록 (/permissions 대화형 대체)
      3. Claude — 발급받은 장수명 토큰을 사용자 환경변수로 등록
      4. Gemini API 키를 사용자 환경변수로 이동 (프로젝트 .env 의존 제거)
      5. preflight-chain.ps1 로 결과 검증

.EXAMPLE
    # 관리자 PowerShell — 토큰 없이 먼저 돌리면 1·2번을 처리하고 3번 안내를 띄운다
    .\fix-chain.ps1

.EXAMPLE
    # claude setup-token 으로 받은 토큰을 넣어 마무리
    .\fix-chain.ps1 -ClaudeToken 'sk-ant-oat01-...' -GeminiApiKey 'AIza...'
#>
[CmdletBinding()]
param(
    [string]$WorkDir = 'C:\Users\PSH\MultiAgent',
    [string]$ClaudeToken,
    [string]$GeminiApiKey,
    [switch]$SkipOwnership,
    [switch]$SkipVerify,
    [switch]$NonInteractive,
    [switch]$NoElevate
)

$ErrorActionPreference = 'Stop'
$steps = @()

function Add-Step {
    param([string]$Name, [string]$Status, [string]$Detail)
    $script:steps += [pscustomobject]@{ Step = $Name; Status = $Status; Detail = $Detail }
    Write-Output ("[{0,-6}] {1} — {2}" -f $Status, $Name, $Detail)
}

function Test-Admin {
    try {
        $id = [Security.Principal.WindowsIdentity]::GetCurrent()
        return ([Security.Principal.WindowsPrincipal]$id).IsInRole(
            [Security.Principal.WindowsBuiltInRole]::Administrator)
    }
    catch { return $false }
}

$isWin = ($null -eq $IsWindows) -or $IsWindows
$canPrompt = -not $NonInteractive -and [Environment]::UserInteractive

# ── 0. 관리자 권한 자동 승격 ─────────────────────────────────────────────────
# 소유권 회수에 관리자 권한이 필요하다. 일반 창에서 실행됐으면 스스로 승격 창을 띄운다.

if ($isWin -and -not $NoElevate -and -not $SkipOwnership -and -not (Test-Admin)) {
    $psExe = try { (Get-Process -Id $PID).Path } catch { 'powershell.exe' }
    $fwd = @('-NoExit', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $PSCommandPath, '-NoElevate')
    foreach ($p in $PSBoundParameters.GetEnumerator()) {
        if ($p.Key -eq 'NoElevate') { continue }
        if ($p.Value -is [switch]) {
            if ($p.Value.IsPresent) { $fwd += "-$($p.Key)" }
        }
        else { $fwd += @("-$($p.Key)", [string]$p.Value) }
    }
    if (-not $PSBoundParameters.ContainsKey('WorkDir')) { $fwd += @('-WorkDir', $WorkDir) }

    Write-Output '관리자 권한이 필요합니다. 승격 창을 띄웁니다 — UAC 창에서 [예]를 눌러 주세요.'
    try {
        Start-Process -FilePath $psExe -ArgumentList $fwd -Verb RunAs | Out-Null
        Write-Output '새로 열린 관리자 창에서 계속 진행됩니다. 이 창은 닫으셔도 됩니다.'
        exit 0
    }
    catch {
        Write-Output "승격 실패($($_.Exception.Message)) — 관리자 권한 없이 가능한 단계만 진행합니다."
    }
}

# ── 작업 폴더 확정 ───────────────────────────────────────────────────────────

if (-not (Test-Path -LiteralPath $WorkDir)) {
    $found = $null
    foreach ($root in @($env:USERPROFILE, 'C:\', 'D:\')) {
        if (-not $root -or -not (Test-Path -LiteralPath $root)) { continue }
        $found = Get-ChildItem -LiteralPath $root -Directory -Filter 'MultiAgent' -Recurse -Depth 3 `
            -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) { break }
    }
    if ($found) {
        Write-Output "지정된 작업 폴더가 없어 자동 탐색했습니다: $($found.FullName)"
        $WorkDir = $found.FullName
    }
    else {
        Write-Error "작업 폴더를 찾지 못했습니다: $WorkDir  (-WorkDir 로 자비스 실제 작업 폴더를 지정해 주세요)"
        exit 99
    }
}
$WorkDir = (Resolve-Path -LiteralPath $WorkDir).Path

Write-Output "3중 체인 복구 — WorkDir: $WorkDir`n"

# ── 1. Codex: 소유권/ACL ─────────────────────────────────────────────────────

if ($SkipOwnership) {
    Add-Step 'Codex 소유권' 'SKIP' '-SkipOwnership 지정'
}
elseif (-not $isWin) {
    Add-Step 'Codex 소유권' 'SKIP' 'Windows 전용 단계'
}
elseif (-not (Test-Admin)) {
    Add-Step 'Codex 소유권' 'FAIL' '관리자 권한 PowerShell 에서 다시 실행해 주세요'
}
else {
    # takeown 은 이미 성공했더라도 다시 돌려서 문제 없다(멱등).
    & takeown.exe /F $WorkDir /R /D Y 2>&1 | Out-Null

    # 주의: "$env:USERNAME:(OI)" 처럼 쓰면 PowerShell 이 콜론까지 변수 이름으로 먹는다.
    # 반드시 ${} 로 경계를 닫을 것.
    $principal = "${env:USERDOMAIN}\${env:USERNAME}"
    $grant = "${principal}:(OI)(CI)(F)"
    $out = & icacls.exe $WorkDir /grant $grant /T /C 2>&1
    if ($LASTEXITCODE -eq 0) {
        Add-Step 'Codex 소유권' 'OK' "$principal 에게 전체 권한 부여 완료"
    }
    else {
        Add-Step 'Codex 소유권' 'FAIL' (($out | Select-Object -Last 1) -join ' ')
    }

    $owner = try { (Get-Acl -LiteralPath $WorkDir).Owner } catch { '확인 실패' }
    if ($owner -match 'CodexSandbox|BUILTIN\\Administrators') {
        Add-Step 'Codex 소유자' 'FAIL' "여전히 '$owner' — 샌드박스가 ACL 을 못 고친다"
    }
    else {
        Add-Step 'Codex 소유자' 'OK' $owner
    }
}

# ── 2. Gemini: 폴더 신뢰 ─────────────────────────────────────────────────────

$trustPath = if ($env:GEMINI_CLI_TRUSTED_FOLDERS_PATH) {
    $env:GEMINI_CLI_TRUSTED_FOLDERS_PATH
} else {
    Join-Path $HOME '.gemini/trustedFolders.json'
}

try {
    $trustDir = Split-Path -Parent $trustPath
    if (-not (Test-Path -LiteralPath $trustDir)) {
        New-Item -ItemType Directory -Path $trustDir -Force | Out-Null
    }

    $map = [ordered]@{}
    if (Test-Path -LiteralPath $trustPath) {
        Copy-Item -LiteralPath $trustPath -Destination "$trustPath.bak" -Force
        $existing = @(Get-Content -LiteralPath $trustPath -Raw | ConvertFrom-Json)
        if ($existing.Count -gt 0 -and $existing[0] -is [string]) {
            # 경로 배열 스키마 → 맵으로 승격
            foreach ($p in $existing) { $map[$p] = 'TRUST_FOLDER' }
        }
        else {
            foreach ($o in $existing) {
                foreach ($prop in $o.PSObject.Properties) { $map[$prop.Name] = $prop.Value }
            }
        }
    }

    $before = $map[$WorkDir]
    $map[$WorkDir] = 'TRUST_FOLDER'

    # Windows PowerShell 5.1 의 `-Encoding utf8` 은 BOM 을 붙인다.
    # gemini-cli 는 이 파일을 JSON.parse 로 읽으므로 BOM 이 있으면 파싱이 깨진다 — BOM 없이 쓴다.
    $json = $map | ConvertTo-Json -Depth 5
    [System.IO.File]::WriteAllText($trustPath, $json, (New-Object System.Text.UTF8Encoding($false)))

    $note = if ($before -eq 'TRUST_FOLDER') { '이미 신뢰됨(변경 없음)' } else { "$trustPath 기록" }
    Add-Step 'Gemini 신뢰' 'OK' $note
}
catch {
    Add-Step 'Gemini 신뢰' 'FAIL' "$($_.Exception.Message) — gemini 안에서 /permissions 로 수동 설정"
}

# ── 3·4. 환경변수 등록 ───────────────────────────────────────────────────────

function Set-UserEnv {
    param([string]$Name, [string]$Value)
    [Environment]::SetEnvironmentVariable($Name, $Value, 'User')
    Set-Item -Path "env:$Name" -Value $Value      # 현재 세션에도 즉시 반영
}

if ($ClaudeToken) {
    Set-UserEnv -Name 'CLAUDE_CODE_OAUTH_TOKEN' -Value $ClaudeToken
    Add-Step 'Claude 토큰' 'OK' 'CLAUDE_CODE_OAUTH_TOKEN 사용자 환경변수 등록'
}
elseif ($env:CLAUDE_CODE_OAUTH_TOKEN) {
    Add-Step 'Claude 토큰' 'OK' '이미 등록돼 있음'
}
elseif ($env:ANTHROPIC_API_KEY) {
    Add-Step 'Claude 토큰' 'WARN' 'ANTHROPIC_API_KEY 로 동작 중 — 구독이 아니라 API 종량과금'
}
elseif ($canPrompt -and (Get-Command claude -ErrorAction SilentlyContinue)) {
    # setup-token 은 브라우저 로그인이 필요한 대화형 명령이라 출력을 가로채면 화면이 깨진다.
    # 콘솔을 그대로 물려주고 실행한 뒤, 마지막에 출력되는 토큰만 받아 등록한다.
    Write-Output ''
    Write-Output '─ Claude 토큰 발급 ─ 브라우저가 열리면 로그인해 주세요. (건너뛰려면 Ctrl+C)'
    try { & claude setup-token } catch { Write-Output "setup-token 실행 실패: $($_.Exception.Message)" }

    $pasted = (Read-Host '위에 출력된 토큰을 붙여넣고 Enter (건너뛰려면 그냥 Enter)').Trim()
    if ($pasted) {
        Set-UserEnv -Name 'CLAUDE_CODE_OAUTH_TOKEN' -Value $pasted
        Add-Step 'Claude 토큰' 'OK' 'CLAUDE_CODE_OAUTH_TOKEN 사용자 환경변수 등록'
    }
    else {
        Add-Step 'Claude 토큰' 'TODO' 'claude setup-token 후 -ClaudeToken "<토큰>" 으로 재실행해 주세요'
    }
}
else {
    Add-Step 'Claude 토큰' 'TODO' 'claude setup-token 실행 후 -ClaudeToken "<토큰>" 으로 재실행해 주세요'
}

if ($GeminiApiKey) {
    Set-UserEnv -Name 'GEMINI_API_KEY' -Value $GeminiApiKey
    Add-Step 'Gemini 키' 'OK' 'GEMINI_API_KEY 사용자 환경변수 등록'
}
elseif ($env:GEMINI_API_KEY -or $env:GOOGLE_API_KEY) {
    Add-Step 'Gemini 키' 'OK' '이미 프로세스 환경에 있음'
}
elseif ($canPrompt) {
    $pasted = (Read-Host 'GEMINI_API_KEY 를 붙여넣고 Enter (프로젝트 .env 에만 있으면 신뢰 해제 시 또 깨집니다 / 건너뛰려면 그냥 Enter)').Trim()
    if ($pasted) {
        Set-UserEnv -Name 'GEMINI_API_KEY' -Value $pasted
        Add-Step 'Gemini 키' 'OK' 'GEMINI_API_KEY 사용자 환경변수 등록'
    }
    else {
        Add-Step 'Gemini 키' 'TODO' '-GeminiApiKey "<키>" 로 재실행해 주세요'
    }
}
else {
    Add-Step 'Gemini 키' 'TODO' '-GeminiApiKey "<키>" 로 재실행 (프로젝트 .env 의존이면 신뢰 해제 시 또 깨진다)'
}

# ── 5. 검증 ─────────────────────────────────────────────────────────────────

Write-Output ''
$todo = @($steps | Where-Object { $_.Status -in @('FAIL', 'TODO') })
if ($todo.Count -gt 0) {
    Write-Output "남은 작업 $($todo.Count)건:"
    $todo | ForEach-Object { Write-Output ("  - {0}: {1}" -f $_.Step, $_.Detail) }
}
else {
    Write-Output '자동 복구 단계 전부 완료.'
}

Write-Output ''
Write-Output '환경변수를 새로 등록했다면 자비스 봇 프로세스를 재시작해야 반영됩니다.'

if (-not $SkipVerify) {
    $preflight = Join-Path $PSScriptRoot 'preflight-chain.ps1'
    if (Test-Path -LiteralPath $preflight) {
        Write-Output "`n--- 검증 ---"
        & $preflight -WorkDir $WorkDir
        exit $LASTEXITCODE
    }
}

exit $todo.Count

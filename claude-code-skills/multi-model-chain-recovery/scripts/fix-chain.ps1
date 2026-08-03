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
    [string[]]$TrustDirs,
    [string]$ClaudeToken,
    [string]$GeminiApiKey,
    [switch]$DisableFolderTrust,
    [switch]$SkipOwnership,
    [switch]$SkipVerify,
    [switch]$NonInteractive,
    [switch]$NoElevate,
    [switch]$InstallGuardian,
    [switch]$SkipGuardian   # 하위 호환용 — 상주 등록은 이제 기본값이 아니라 -InstallGuardian 옵트인이다
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
        elseif ($p.Value -is [array]) {
            # 배열을 [string] 으로 캐스팅하면 공백으로 이어붙어 한 값이 된다 —
            # 콤마로 넘겨야 승격된 쪽에서 다시 배열로 바인딩된다.
            $fwd += @("-$($p.Key)", (($p.Value | ForEach-Object { $_ }) -join ','))
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
    $broken = $false
    if (Test-Path -LiteralPath $trustPath) {
        Copy-Item -LiteralPath $trustPath -Destination "$trustPath.bak" -Force
        try {
            # Get-Content 는 PS 5.1 에서 BOM 없는 UTF-8 을 시스템 코드페이지(cp949)로 읽어
            # 한글 경로를 깨뜨리고, 깨진 바이트가 JSON 이스케이프 오류로 이어진다(실측 2026-08-03).
            # 인코딩을 명시해서 읽는다.
            $raw = [System.IO.File]::ReadAllText($trustPath, [System.Text.Encoding]::UTF8)
            $existing = @($raw | ConvertFrom-Json)
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
        catch {
            # 이미 깨진 파일이면 붙들고 있지 않는다 — 보존해 두고 새로 쓴다.
            Copy-Item -LiteralPath $trustPath -Destination "$trustPath.broken" -Force
            $map = [ordered]@{}
            $broken = $true
        }
    }

    # 루틴이 어느 폴더에서 gemini 를 부르는지는 작업 폴더와 다를 수 있다(예: 볼트 경로).
    # 작업 폴더 + 그 부모 + 사용자가 지정한 폴더까지 한꺼번에 신뢰한다.
    $targets = New-Object System.Collections.Generic.List[string]
    $targets.Add($WorkDir)
    $parent = Split-Path -Parent $WorkDir
    if ($parent) {
        # 비교는 해석된 경로끼리 해야 한다 — 대소문자·후행 구분자 때문에 원본끼리 비교하면 어긋난다.
        $parent = try { (Resolve-Path -LiteralPath $parent -ErrorAction Stop).Path } catch { $parent }
        $targets.Add($parent)
    }
    # 콤마로 넘어온 값(승격 시 전달 형식)도 풀어서 받는다.
    foreach ($d in @($TrustDirs)) {
        foreach ($one in ("$d" -split ',')) {
            $one = $one.Trim()
            if ($one) { $targets.Add($one) }
        }
    }

    $added = @()
    $resolvedTargets = @()
    foreach ($t in $targets) {
        $key = try { (Resolve-Path -LiteralPath $t -ErrorAction Stop).Path } catch { $t }
        $resolvedTargets += $key
        $value = if ($key -eq $parent) { 'TRUST_PARENT' } else { 'TRUST_FOLDER' }
        if ($map[$key] -ne $value) { $added += $key }
        $map[$key] = $value
    }

    # 상위 경로에 DO_NOT_TRUST 가 걸려 있으면 하위를 아무리 신뢰시켜도 safe mode 로 떨어진다.
    # (실측 2026-08-03: "g:/" 가 DO_NOT_TRUST 라 볼트 전체가 미신뢰였다.)
    $cleared = @()
    foreach ($k in @($map.Keys)) {
        if ($map[$k] -ne 'DO_NOT_TRUST') { continue }
        $norm = $k.Replace('/', '\').TrimEnd('\')
        foreach ($t in $resolvedTargets) {
            $tn = $t.Replace('/', '\').TrimEnd('\')
            if ($tn -eq $norm -or $tn.StartsWith($norm + '\', [StringComparison]::OrdinalIgnoreCase)) {
                $map.Remove($k)
                $cleared += $k
                break
            }
        }
    }

    # Windows PowerShell 5.1 의 `-Encoding utf8` 은 BOM 을 붙인다.
    # gemini-cli 는 이 파일을 JSON.parse 로 읽으므로 BOM 이 있으면 파싱이 깨진다 — BOM 없이 쓴다.
    $json = $map | ConvertTo-Json -Depth 5
    [System.IO.File]::WriteAllText($trustPath, $json, (New-Object System.Text.UTF8Encoding($false)))

    $parts = @()
    if ($broken) { $parts += '기존 파일이 깨져 있어 .broken 으로 보존하고 새로 씀' }
    if ($added.Count -gt 0) { $parts += "$($added.Count)개 폴더 신뢰 기록" }
    if ($cleared.Count -gt 0) { $parts += "상위 DO_NOT_TRUST 해제 — $($cleared -join ', ')" }
    if ($parts.Count -eq 0) { $parts += "이미 신뢰됨 (항목 $($map.Count)개)" }
    Add-Step 'Gemini 신뢰' 'OK' ($parts -join ' / ')
}
catch {
    Add-Step 'Gemini 신뢰' 'FAIL' "$($_.Exception.Message) — gemini 안에서 /permissions 로 수동 설정"
}

# 폴더별 신뢰로는 루틴이 실행되는 모든 경로를 못 덮는 경우가 있다.
# 그때는 신뢰 기능 자체를 끈다 — 개인 머신 한정 선택이라 기본값이 아니라 명시 옵션이다.
if ($DisableFolderTrust) {
    try {
        $settingsPath = Join-Path $HOME '.gemini/settings.json'
        $settings = [pscustomobject]@{}
        if (Test-Path -LiteralPath $settingsPath) {
            Copy-Item -LiteralPath $settingsPath -Destination "$settingsPath.bak" -Force
            try {
                # trustedFolders.json 과 같은 이유로 인코딩을 명시해서 읽는다(cp949 오독 방지).
                $sRaw = [System.IO.File]::ReadAllText($settingsPath, [System.Text.Encoding]::UTF8)
                if ($sRaw.Trim()) { $settings = $sRaw | ConvertFrom-Json }
            }
            catch {
                # 깨진 설정을 붙들면 전체 단계가 죽는다 — 보존하고 새로 쓴다.
                Copy-Item -LiteralPath $settingsPath -Destination "$settingsPath.broken" -Force
                $settings = [pscustomobject]@{}
            }
        }

        $security = if ($settings.PSObject.Properties['security']) { $settings.security } else { [pscustomobject]@{} }
        $folderTrust = if ($security.PSObject.Properties['folderTrust']) { $security.folderTrust } else { [pscustomobject]@{} }

        $folderTrust | Add-Member -NotePropertyName 'enabled' -NotePropertyValue $false -Force
        $security    | Add-Member -NotePropertyName 'folderTrust' -NotePropertyValue $folderTrust -Force
        $settings    | Add-Member -NotePropertyName 'security' -NotePropertyValue $security -Force

        $sJson = $settings | ConvertTo-Json -Depth 10
        [System.IO.File]::WriteAllText($settingsPath, $sJson, (New-Object System.Text.UTF8Encoding($false)))
        Add-Step 'Gemini 신뢰검사' 'OK' "security.folderTrust.enabled=false 기록 ($settingsPath) — 되돌리려면 .bak 복원"
    }
    catch {
        Add-Step 'Gemini 신뢰검사' 'FAIL' $_.Exception.Message
    }
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

# ── 4.5 환경변수를 못 받은 봇 프로세스 탐지 ──────────────────────────────────
# 환경변수는 "새로 뜨는 프로세스"에만 상속된다. 자비스가 이미 떠 있으면 등록 전 환경을
# 그대로 들고 있어서, 토큰을 아무리 넣어도 같은 OAuth 만료 오류가 계속 난다.

if ($isWin) {
    try {
        $stale = @(Get-CimInstance Win32_Process -ErrorAction Stop |
            Where-Object {
                $_.CommandLine -and
                $_.CommandLine -match '(?i)hermes|jarvis|자비스|discord|bot\.py|bot\.js' -and
                $_.Name -match '(?i)^(node|python|pythonw|pwsh|powershell)'
            })

        if ($stale.Count -eq 0) {
            Add-Step '봇 프로세스' 'OK' '이 이름으로 실행 중인 봇 프로세스를 찾지 못함 — 다음 기동 시 새 환경을 받는다'
        }
        else {
            foreach ($p in $stale) {
                $started = try { $p.CreationDate } catch { $null }
                $when = if ($started) { (Get-Date $started -Format 'MM-dd HH:mm') } else { '시각 미상' }
                Add-Step '봇 프로세스' 'TODO' "PID $($p.ProcessId) ($($p.Name), $when 기동) — 재시작해야 새 토큰을 받는다"
            }
        }
    }
    catch {
        Add-Step '봇 프로세스' 'SKIP' "프로세스 조회 실패: $($_.Exception.Message)"
    }
}

# ── 5. 자가 점검 상주 등록 ───────────────────────────────────────────────────
# 한 번 등록해 두면 이후로는 사람이 명령을 칠 일이 없다 — 예약 작업이 점검·복구를 대신한다.

if (-not $InstallGuardian -or $SkipGuardian -or -not $isWin) {
    Add-Step '자가 점검' 'SKIP' $(if ($isWin) { '상주 등록 안 함 (-InstallGuardian 으로 켤 수 있다)' } else { 'Windows 전용 단계' })
}
else {
    $installer = Join-Path $PSScriptRoot 'install-guardian.ps1'
    if (Test-Path -LiteralPath $installer) {
        try {
            $gOut = & $installer -WorkDir $WorkDir 2>&1 | Out-String
            if ($LASTEXITCODE -eq 0 -or $gOut -match '등록 완료') {
                Add-Step '자가 점검' 'OK' '예약 작업 등록 — 로그온 시 + 60분마다 자동 점검·복구'
            }
            else {
                Add-Step '자가 점검' 'WARN' (($gOut -split "`r?`n" | Where-Object { $_.Trim() } | Select-Object -Last 1))
            }
        }
        catch {
            Add-Step '자가 점검' 'WARN' "등록 실패: $($_.Exception.Message)"
        }
    }
    else {
        Add-Step '자가 점검' 'SKIP' 'install-guardian.ps1 없음'
    }
}

# ── 6. 검증 ─────────────────────────────────────────────────────────────────

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

<#
.SYNOPSIS
    ARCOVA "켜면 자꾸 꺼진다" 원인 실측 스크립트 (읽기 전용).

.DESCRIPTION
    ARCOVA-진단-20260804.md 의 §3 점검 항목을 한 번에 수행한다.
    이 스크립트는 아무것도 고치거나 종료하지 않는다. 오직 읽고 출력만 한다.

    판정 결과:
      후보 A = 브리지/워치독 다중 인스턴스
      후보 B = Windows cp949 인코딩
      후보 C = 워치독이 사망 원인을 기록하지 않음

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\arcova-triage.ps1
    powershell -ExecutionPolicy Bypass -File .\arcova-triage.ps1 -OutFile arcova-triage.txt
#>

[CmdletBinding()]
param(
    # 결과를 파일로도 저장할 경로. 생략하면 화면 출력만 한다.
    [string]$OutFile,

    # 브리지 관련 프로세스를 식별할 커맨드라인 키워드.
    [string[]]$Keyword = @('jarvis', 'bridge', 'hermes', 'arcova', 'server.py', 'skill-server'),

    # 점유 여부를 확인할 포트. 3747=skill-server, 49691=운영 콘솔(/ops).
    [int[]]$Port = @(3747, 49691)
)

$ErrorActionPreference = 'Continue'
$findings = [System.Collections.Generic.List[string]]::new()

function Write-Section {
    param([string]$Title)
    Write-Host ''
    Write-Host ('=' * 70) -ForegroundColor DarkGray
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host ('=' * 70) -ForegroundColor DarkGray
}

function Add-Finding {
    param([string]$Code, [string]$Message)
    $findings.Add("[$Code] $Message")
    Write-Host "  >> $Code : $Message" -ForegroundColor Yellow
}

if ($OutFile) { Start-Transcript -Path $OutFile -Force | Out-Null }

Write-Host ''
Write-Host 'ARCOVA 진단 — 읽기 전용 실측' -ForegroundColor Green
Write-Host ("실행 시각: {0}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
Write-Host ("호스트   : {0}" -f $env:COMPUTERNAME)

# ---------------------------------------------------------------------------
# 1. 중복 프로세스  (후보 A)
# ---------------------------------------------------------------------------
Write-Section '1. 브리지/서버 프로세스 — 중복 실행 여부 (후보 A)'

$procs = Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='pythonw.exe' OR Name='node.exe'" -ErrorAction SilentlyContinue |
    Where-Object {
        $cmd = $_.CommandLine
        $cmd -and ($Keyword | Where-Object { $cmd -match [regex]::Escape($_) })
    }

if (-not $procs) {
    Write-Host '  관련 프로세스가 하나도 실행 중이 아닙니다. (ARCOVA가 지금 꺼져 있는 상태)' -ForegroundColor DarkYellow
} else {
    $procs | Select-Object ProcessId, CreationDate, CommandLine | Format-List | Out-String | Write-Host

    # 같은 스크립트 경로가 2번 이상 뜬 경우를 잡는다.
    $bySignature = $procs | Group-Object {
        # 커맨드라인에서 스크립트 파일명만 뽑아 서명으로 삼는다.
        if ($_.CommandLine -match '([^\\/ "]+\.(py|ps1|js))') { $Matches[1] } else { $_.Name }
    }

    foreach ($g in $bySignature) {
        if ($g.Count -gt 1) {
            $pids = ($g.Group.ProcessId -join ', ')
            Add-Finding 'A' "'$($g.Name)' 이(가) $($g.Count)개 동시 실행 중입니다 (PID: $pids). 중복 인스턴스입니다."
        }
    }
    if (-not ($bySignature | Where-Object Count -gt 1)) {
        Write-Host '  중복 없음 — 각 스크립트가 1개씩만 실행 중입니다.' -ForegroundColor Green
    }
}

# ---------------------------------------------------------------------------
# 2. 워치독 예약작업  (후보 A)
# ---------------------------------------------------------------------------
Write-Section '2. 워치독 예약작업 — 중복 등록 여부 (후보 A)'

$tasks = Get-ScheduledTask -ErrorAction SilentlyContinue |
    Where-Object { $_.TaskName -match 'Hermes|Watchdog|ARCOVA|Bridge|Jarvis' }

if (-not $tasks) {
    Write-Host '  일치하는 예약작업이 없습니다.' -ForegroundColor DarkYellow
} else {
    $tasks | Select-Object TaskName, State, TaskPath | Format-Table -AutoSize | Out-String | Write-Host

    $watchdogs = $tasks | Where-Object { $_.TaskName -match 'Watchdog' }
    if ($watchdogs.Count -gt 1) {
        Add-Finding 'A' "워치독 예약작업이 $($watchdogs.Count)개 등록되어 있습니다. 서로 상대의 프로세스를 재시작하며 충돌합니다."
    }

    # 자동 시작 항목도 함께 본다 (부팅 시 중복 기동원).
    $runKeys = @(
        'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run',
        'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run'
    )
    foreach ($k in $runKeys) {
        $item = Get-ItemProperty -Path $k -ErrorAction SilentlyContinue
        if ($item) {
            $hits = $item.PSObject.Properties | Where-Object {
                $v = $_.Value
                $v -is [string] -and ($Keyword | Where-Object { $v -match [regex]::Escape($_) })
            }
            foreach ($h in $hits) {
                Write-Host "  [자동시작] $k -> $($h.Name) = $($h.Value)" -ForegroundColor DarkCyan
                Add-Finding 'A' "레지스트리 Run 키에도 기동 항목이 있습니다 ($($h.Name)). 예약작업과 겹치면 이중 기동합니다."
            }
        }
    }
}

# ---------------------------------------------------------------------------
# 3. 포트 점유  (후보 A)
# ---------------------------------------------------------------------------
Write-Section '3. 포트 점유 현황 (후보 A)'

foreach ($p in $Port) {
    $conns = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
    if (-not $conns) {
        Write-Host "  :$p  — 아무도 듣고 있지 않습니다." -ForegroundColor DarkYellow
    } else {
        foreach ($c in $conns) {
            $owner = Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue
            Write-Host ("  :{0}  — PID {1} ({2})" -f $p, $c.OwningProcess, $owner.ProcessName) -ForegroundColor Green
        }
        if ($conns.Count -gt 1) {
            Add-Finding 'A' ":$p 를 여러 소켓이 점유하고 있습니다. bind 충돌로 후발 인스턴스가 즉사할 수 있습니다."
        }
    }
}

# ---------------------------------------------------------------------------
# 4. 인코딩  (후보 B)
# ---------------------------------------------------------------------------
Write-Section '4. 인코딩 설정 — 한글 깨짐 원인 (후보 B)'

$cp = (chcp) 2>$null
Write-Host "  콘솔 코드페이지 : $cp"
if ("$cp" -match '949') {
    Add-Finding 'B' '콘솔 코드페이지가 949(cp949)입니다. 한글 출력 시 UnicodeEncodeError로 프로세스가 죽을 수 있습니다.'
}

$pyEnc = & python -c "import sys,locale;print(sys.stdout.encoding,'|',sys.getdefaultencoding(),'|',locale.getpreferredencoding())" 2>$null
if ($pyEnc) {
    Write-Host "  python (stdout | default | locale) : $pyEnc"
    if ($pyEnc -match '(?i)cp949|euc-kr|ms949') {
        Add-Finding 'B' "Python이 cp949 계열 인코딩을 사용합니다 ($pyEnc). 이것이 '?' 치환의 직접 원인일 가능성이 높습니다."
    }
} else {
    Write-Host '  python 실행 실패 — PATH에 없거나 다른 이름일 수 있습니다.' -ForegroundColor DarkYellow
}

foreach ($var in 'PYTHONUTF8', 'PYTHONIOENCODING') {
    $u = [Environment]::GetEnvironmentVariable($var, 'User')
    $m = [Environment]::GetEnvironmentVariable($var, 'Machine')
    Write-Host ("  {0,-18} User='{1}' Machine='{2}'" -f $var, $u, $m)
    if (-not $u -and -not $m) {
        Add-Finding 'B' "$var 가 설정되어 있지 않습니다. Windows 기본값(cp949)이 적용됩니다."
    }
}

# ---------------------------------------------------------------------------
# 5. 사망 흔적  (후보 C)
# ---------------------------------------------------------------------------
Write-Section '5. 최근 3일 비정상 종료 흔적 (후보 C)'

$since = (Get-Date).AddDays(-3)

$evts = Get-WinEvent -FilterHashtable @{
    LogName   = 'Application'
    StartTime = $since
} -ErrorAction SilentlyContinue |
    Where-Object {
        $_.LevelDisplayName -in 'Error', 'Critical' -and
        ($_.Message -match 'python|node|Application Error|\.NET|Faulting' )
    } |
    Select-Object -First 15

if (-not $evts) {
    Write-Host '  이벤트 로그에 관련 오류가 없습니다.' -ForegroundColor Green
    Add-Finding 'C' '프로세스가 죽는데 이벤트 로그에 아무 흔적이 없습니다 = 정상 종료 경로로 조용히 exit 하고 있습니다. 워치독에 종료코드/stderr 기록을 추가해야 원인 특정이 가능합니다.'
} else {
    $evts | Select-Object TimeCreated, ProviderName, Id,
        @{n = 'Message'; e = { ($_.Message -split "`n")[0] } } |
        Format-Table -AutoSize -Wrap | Out-String | Write-Host
}

Write-Section '6. 최근 수정된 로그 파일 (수동 확인용)'

$logs = Get-ChildItem $env:USERPROFILE -Recurse -Include *.log, *.err, *.out -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -gt $since } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 20 FullName, LastWriteTime, Length

if ($logs) {
    $logs | Format-Table -AutoSize | Out-String | Write-Host
    Write-Host '  ↑ 워치독 재시작 시각과 겹치는 파일의 끝부분을 확인하세요:' -ForegroundColor DarkCyan
    Write-Host '     Get-Content <경로> -Tail 50' -ForegroundColor DarkCyan
} else {
    Write-Host '  최근 3일 내 수정된 로그 파일이 없습니다.' -ForegroundColor DarkYellow
}

# ---------------------------------------------------------------------------
# 종합
# ---------------------------------------------------------------------------
Write-Section '종합 판정'

if ($findings.Count -eq 0) {
    Write-Host '  탐지된 문제 없음. 이 시점에는 중복 실행도 cp949도 관측되지 않았습니다.' -ForegroundColor Green
    Write-Host '  간헐적 증상이므로, 다음 사망 직후에 다시 실행해 보세요.' -ForegroundColor DarkYellow
} else {
    Write-Host ''
    foreach ($f in $findings) { Write-Host "  $f" -ForegroundColor Yellow }
    Write-Host ''
    Write-Host '  대응: ARCOVA-진단-20260804.md 의 §4를 참고하세요.' -ForegroundColor Cyan
    Write-Host '        A -> §4-1 단일 인스턴스 강제 / B -> §4-2 UTF-8 고정 / C -> §4-3 워치독 fail-loud' -ForegroundColor Cyan
}

Write-Host ''
if ($OutFile) {
    Stop-Transcript | Out-Null
    Write-Host "결과를 저장했습니다: $OutFile" -ForegroundColor Green
}

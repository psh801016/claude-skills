# 일러 자동 작업 실행기 (main-visual-variation). 사용자 문서가 하나라도 열려 있으면 돌리지 않는다 — 2026-10-22 일러 강제 종료로 저장 안 한 문서가 날아간 사고.
# 사용:  run.ps1 -Main "<메인비주얼.ai>" -Jobs "<jobs.js>" [-Only key|all] [-Probe] [-Extra @{entry='X:\...\입구백월.ai'}]
#        run.ps1 -Jsx "<임의.jsx>"   : 그 jsx 만 같은 가드(사용자 문서 열림 → ABORT)로 돌린다. edit_text.jsx·export_jpg.jsx 용. BOM 으로 다시 저장해 준다.
#   -Probe : 조각 지도만 뽑는다 (C:\mvv\probe.txt)
#   아니면 : C:\mvv\out\<key>.ai 생성, 로그 C:\mvv\build_log.txt
# 디자인팀 메인비주얼 원본은 C:\mvv\src\main.ai 로 '복사'만 한다. 원본 폴더에는 아무것도 쓰지 않는다.
param(
  [string]$Main = "",
  [string]$Jsx = "",
  [string]$Jobs = "",
  [string]$Only = "all",
  [switch]$Probe,
  [hashtable]$Extra = @{}
)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
foreach ($d in "C:\mvv\src", "C:\mvv\jsx", "C:\mvv\out") { New-Item -ItemType Directory -Force $d | Out-Null }
if (-not $Main -and -not $Jsx) { "-Main 또는 -Jsx 가 필요합니다"; exit 1 }
if ($Main) { Copy-Item -LiteralPath $Main -Destination "C:\mvv\src\main.ai" -Force }
foreach ($k in $Extra.Keys) { Copy-Item -LiteralPath $Extra[$k] -Destination ("C:\mvv\src\" + $k + ".ai") -Force }

$ai = New-Object -ComObject Illustrator.Application
$others = @()
foreach ($d in @($ai.Documents)) {
  $p = ''; try { $p = $d.FullName } catch { $p = $d.Name }
  if ($p -notlike 'C:\mvv\*') { $others += "$p (저장됨=$($d.Saved))" }
}
if ($others.Count) { "ABORT 사용자 문서가 열려 있음: " + ($others -join '; '); exit 2 }

if ($Jsx) {
  $jsx = $Jsx
  $src = [IO.File]::ReadAllText($jsx); [IO.File]::WriteAllText($jsx, $src, (New-Object System.Text.UTF8Encoding $true))
} elseif ($Probe) {
  $jsx = "C:\mvv\jsx\probe.jsx"
  Copy-Item -LiteralPath (Join-Path $here "probe_pieces.jsx") -Destination $jsx -Force
} else {
  if (-not $Jobs) { "jobs.js 경로가 필요합니다"; exit 1 }
  Copy-Item -LiteralPath $Jobs -Destination "C:\mvv\jsx\jobs.js" -Force
  Copy-Item -LiteralPath (Join-Path $here "build.jsx") -Destination "C:\mvv\jsx\build.jsx" -Force
  $jsx = "C:\mvv\jsx\run.jsx"
  # 한글 경로·문자열이 든 jsx 는 UTF-8 BOM 으로 저장해야 깨지지 않는다
  [IO.File]::WriteAllText($jsx, ('var ONLY="' + $Only + '"; $.evalFile("C:/mvv/jsx/build.jsx");'), (New-Object System.Text.UTF8Encoding $true))
}
$t = Get-Date
try { $ai.DoJavaScriptFile($jsx) | Out-Null } catch { "AI_ERROR " + $_.Exception.Message; exit 3 }
"OK {0:N0}s" -f ((Get-Date) - $t).TotalSeconds
if ($Jsx) { } elseif ($Probe) { Get-Content "C:\mvv\probe.txt" -Encoding UTF8 } else { Get-Content "C:\mvv\build_log.txt" -Encoding UTF8 | Select-Object -Last 60 }

# 일러 자동 작업 실행기 — 사용자 문서가 열려 있으면 돌리지 않는다.
# 계기: 2026-10-22 13:26 색 작업 중 일러가 강제 종료돼 사용자의 저장 안 한 Untitled 문서가 날아감.
# -AllowSaved: ASURA님이 "열린 문서는 다 저장돼 있다"고 허락한 경우에만 — 저장 안 된 문서가 하나라도 있으면 그래도 멈춘다.
param([Parameter(Mandatory)][string]$Jsx, [switch]$AllowSaved)
$ai = New-Object -ComObject Illustrator.Application
$others = @(); $unsaved = @()
foreach ($d in @($ai.Documents)) {
  $p = ''; try { $p = $d.FullName } catch { $p = $d.Name }
  if ($p -notlike 'C:\jjb\*') { $others += "$p (저장됨=$($d.Saved))"; if (-not $d.Saved) { $unsaved += $p } }
}
if ($unsaved.Count) { "ABORT 저장 안 된 사용자 문서가 있음: " + ($unsaved -join '; '); exit 2 }
if ($others.Count -and -not $AllowSaved) { "ABORT 사용자 문서가 열려 있음: " + ($others -join '; '); exit 2 }
$t = Get-Date
try { $ai.DoJavaScriptFile($Jsx) | Out-Null } catch { "AI_ERROR " + $_.Exception.Message; exit 3 }
"OK {0:N0}s" -f ((Get-Date) - $t).TotalSeconds

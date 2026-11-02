# RGB 원본에서 온 조각의 색을 '원본 RGB 에 맞춘 CMYK'(Japan Color 2001 Coated)로 바꾼다 — 발주는 CMYK, 일러 기본 변환(미국 SWOP)에 맡기지 않는다.
# ASURA님 지시 2026-10-23: "발주는 cmyk로 작업해야해 알지비 색상을 cmyk로 맞춰서 해야해".
# 도구는 족자봉 스킬(jokjabong-print-fit/scripts/color)을 그대로 쓴다 — 실행할 때 C:\mvv\color 로 가져와 작업 경로(C:/jjb → C:/mvv)만 바꾼다. 복사본을 스킬에 두지 않는다.
# 사용: color_match.ps1 -Key entry -Src entry.ai      (Src = C:\mvv\src 아래 RGB 원본 사본, 결과 = C:\mvv\out\<Key>.ai 를 고쳐 저장)
param([Parameter(Mandatory)][string]$Key, [Parameter(Mandatory)][string]$Src)
$ErrorActionPreference = "Stop"
$cm = "C:\Users\PSH\.agents\skills\jokjabong-print-fit\scripts\color"
$dir = "C:\mvv\color"; New-Item -ItemType Directory -Force $dir | Out-Null
$enc = New-Object System.Text.UTF8Encoding $true
foreach ($f in "colormatch.jsx", "colorize.py", "match.py") {
  $t = [IO.File]::ReadAllText((Join-Path $cm $f)) -replace 'C:/jjb', 'C:/mvv' -replace 'C:\\\\jjb', 'C:\\mvv' -replace 'c:\\\\\\\\jjb', 'c:\\\\mvv'
  [IO.File]::WriteAllText((Join-Path $dir $f), $t, $enc)
}
$ai = New-Object -ComObject Illustrator.Application
foreach ($d in @($ai.Documents)) { $p = ''; try { $p = $d.FullName } catch { $p = $d.Name }; if ($p -notlike 'C:\mvv\*') { "ABORT 사용자 문서가 열려 있음: $p"; exit 2 } }
Remove-Item "$dir\log.txt" -ErrorAction SilentlyContinue
foreach ($mode in "export", "apply") {
  if ($mode -eq "apply") { Push-Location $dir; python -X utf8 colorize.py map $Key; $rc = $LASTEXITCODE; Pop-Location; if ($rc) { "COLORIZE_FAIL"; exit 4 } }
  $run = "$dir\run_$mode.jsx"
  [IO.File]::WriteAllText($run, ('var KEY="' + $Key + '", MODE="' + $mode + '", SRCS=[["' + $Src + '", 0]]; $.evalFile("C:/mvv/color/colormatch.jsx");'), $enc)
  try { $ai.DoJavaScriptFile($run) | Out-Null } catch { "AI_ERROR $mode " + $_.Exception.Message; exit 3 }
}
Get-Content "$dir\log.txt" -Encoding UTF8

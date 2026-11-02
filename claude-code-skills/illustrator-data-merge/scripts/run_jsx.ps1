param($f)
$src = Join-Path $PSScriptRoot $f
$dst = Join-Path $env:TEMP ("bsg_" + $f)
$t = [IO.File]::ReadAllText($src, [Text.Encoding]::UTF8)
[IO.File]::WriteAllText($dst, $t, (New-Object Text.UTF8Encoding $true))
$ai = New-Object -ComObject Illustrator.Application
$ai.DoJavaScriptFile($dst) | Out-Null

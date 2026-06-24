#requires -version 5.1
<#
  sync.ps1 — 스킬·규칙을 Claude Code / Codex 양쪽에 동일 적용 (단일 물리본 = junction)
  목표: 어느 런타임에서 고쳐도 양쪽 반영, 업로드도 한 번에 최신.

  설계(실측·적대검증 반영):
   - 8개 기존 스킬의 원본은 Desktop 경로(AppData\Claude\skills)에 그대로 둔다(주간 GitHub 백업이 이미 이 경로를 푸시 → 업로드 자동 일원화).
   - Claude Code는 이 8종을 Desktop 브리지('anthropic-skills' 네임스페이스)로 이미 본다 → ~/.claude/skills에는 중복 junction 안 함(이름충돌 방지, codex MAJOR).
   - Codex(~/.codex/skills)에는 8종 + ~/.agents 스킬을 junction → Codex도 동일 사용.
   - junction(mklink /J): 관리자 권한 불필요(실증). 같은 물리 파일이라 양방향 자동 동기화.
   - rules.md(단일정본) → ~/.codex/AGENTS.md 자동생성(수기중복 금지, M-1).
   - no-clobber: 대상에 '실폴더'가 있으면 절대 안 덮음. frontmatter(name+description) 검증.
  사용: powershell -ExecutionPolicy Bypass -File "$HOME\.agents\sync.ps1" [-Copy] [-WhatIf]
#>
param([switch]$Copy, [switch]$WhatIf)
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$AgentsHome    = Join-Path $HOME ".agents"
$AgentsSkills  = Join-Path $AgentsHome "skills"
$DesktopSkills = Join-Path $env:APPDATA "Claude\skills"   # 기존 8스킬 원본

# 타깃별 소스 규칙
$Plan = @(
  @{ Name=".codex";  Target=(Join-Path $HOME ".codex\skills");  Sources=@($DesktopSkills, $AgentsSkills) },
  @{ Name=".claude"; Target=(Join-Path $HOME ".claude\skills"); Sources=@($AgentsSkills) }
)

$report = [System.Collections.Generic.List[string]]::new()

function Test-Frontmatter([string]$md) {
  $raw = Get-Content -LiteralPath $md -Raw -Encoding UTF8
  return (($raw -match '(?m)^\s*name\s*:') -and ($raw -match '(?m)^\s*description\s*:'))
}
function Get-LinkTarget([string]$path) {
  try { $it = Get-Item -LiteralPath $path -Force -ErrorAction Stop } catch { return $null }
  if ($it.LinkType) { return ($it.Target | Select-Object -First 1) }
  return $null   # 실폴더(링크 아님)
}
function Link-Skill($skillDir, $target, $rt) {
  $name = $skillDir.Name
  $md = Join-Path $skillDir.FullName "SKILL.md"
  if (-not (Test-Path -LiteralPath $md)) { $report.Add("SKIP  [$rt] ${name}: SKILL.md 없음"); return }
  if (-not (Test-Frontmatter $md))       { $report.Add("SKIP  [$rt] ${name}: name/description 없음"); return }
  if (-not (Test-Path -LiteralPath $target)) { if (-not $WhatIf) { New-Item -ItemType Directory -Path $target -Force | Out-Null } }
  $linkPath = Join-Path $target $name

  if (Test-Path -LiteralPath $linkPath) {
    $tgt = Get-LinkTarget $linkPath
    if ($null -eq $tgt) { $report.Add("WARN  [$rt] ${name}: 실폴더 존재 → 안 덮음(수동확인)"); return }
    if ($tgt.TrimEnd('\') -ieq $skillDir.FullName.TrimEnd('\')) { $report.Add("OK    [$rt] ${name}: 이미 연결됨"); return }
    if (-not $WhatIf) { (Get-Item -LiteralPath $linkPath -Force).Delete() }
    $report.Add("RELNK [$rt] ${name}: 대상 변경 → 재연결")
  }
  if ($WhatIf) { $report.Add("PLAN  [$rt] ${name}: " + $(if($Copy){"복사"}else{"junction"})); return }
  if ($Copy) {
    Copy-Item -LiteralPath $skillDir.FullName -Destination $linkPath -Recurse -Force
    $report.Add("COPY  [$rt] ${name}")
  } else {
    $null = cmd /c mklink /J "`"$linkPath`"" "`"$($skillDir.FullName)`"" 2>&1
    if (Test-Path -LiteralPath $linkPath) { $report.Add("LINK  [$rt] ${name}") }
    else { $report.Add("FAIL  [$rt] ${name}: junction 실패 → -Copy 권장") }
  }
}

Write-Host "== 스킬 동기화 (Claude + Codex) ==" -ForegroundColor Cyan
if ($WhatIf) { Write-Host "(WhatIf: 계획만)" -ForegroundColor Yellow }

foreach ($p in $Plan) {
  foreach ($src in $p.Sources) {
    if (-not (Test-Path -LiteralPath $src)) { $report.Add("MISS  소스 없음: $src"); continue }
    Get-ChildItem -LiteralPath $src -Directory -ErrorAction SilentlyContinue | ForEach-Object {
      Link-Skill $_ $p.Target $p.Name
    }
  }
}

# rules.md → ~/.codex/AGENTS.md 자동생성
$rules = Join-Path $AgentsHome "rules.md"
if (Test-Path -LiteralPath $rules) {
  $agentsMd = Join-Path $HOME ".codex\AGENTS.md"
  $hdr = "<!-- AUTO-GENERATED from ~/.agents/rules.md by sync.ps1 - 직접 수정 금지. 원본을 고치세요. -->`n`n"
  if (-not $WhatIf) {
    New-Item -ItemType Directory -Path (Split-Path $agentsMd -Parent) -Force | Out-Null
    Set-Content -LiteralPath $agentsMd -Value ($hdr + (Get-Content -LiteralPath $rules -Raw -Encoding UTF8)) -Encoding UTF8
  }
  $report.Add("GEN   ~/.codex/AGENTS.md <- rules.md")
}

Write-Host ""
$report | ForEach-Object {
  $c = switch -Regex ($_) { '^(FAIL|WARN|MISS)' {'Yellow'} '^(LINK|COPY|GEN|RELNK)' {'Green'} default {'Gray'} }
  Write-Host $_ -ForegroundColor $c
}
Write-Host "`n== 완료 ==" -ForegroundColor Cyan
Write-Host "검증: Codex 재시작 후 스킬 목록 / Claude는 새 세션." -ForegroundColor DarkGray

#!/usr/bin/env bash
#
# sync-skills.sh
# 내 데스크탑 PC의 Claude 스킬을 이 저장소로 모아서 GitHub에 올립니다.
# 이걸 실행해야 핸드폰/웹에서도 같은 내용이 보입니다.
#
# 사용법:
#   ./sync-skills.sh "무엇을 바꿨는지 한 줄 메모"
#   (메모를 안 적으면 날짜로 자동 기록)
#
# 처음 한 번: 아래 두 경로(SRC_*)가 내 컴퓨터의 실제 스킬 폴더와 맞는지 확인하세요.

set -euo pipefail

# ── 1. 내 데스크탑의 스킬 원본 위치 (※ 본인 환경에 맞게 수정) ───────────────
#   아래는 macOS 기준 흔한 위치입니다. 폴더가 없으면 자동으로 건너뜁니다.
SRC_DESKTOP_SKILLS="${SRC_DESKTOP_SKILLS:-$HOME/Library/Application Support/Claude/skills}"
SRC_CODE_SKILLS="${SRC_CODE_SKILLS:-$HOME/.claude/skills}"

# ── 2. 이 저장소 안의 대상 폴더 (수정 불필요) ─────────────────────────────
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DST_DESKTOP="$REPO_DIR/claude-desktop-skills"
DST_CODE="$REPO_DIR/claude-code-skills"

BRANCH="$(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD)"
MSG="${1:-Sync skills $(date '+%Y-%m-%d %H:%M')}"

echo "▶ 저장소: $REPO_DIR (브랜치: $BRANCH)"

copy_if_exists () {
  local src="$1" dst="$2" label="$3"
  if [ -d "$src" ]; then
    echo "  ✔ $label 복사: $src → $dst"
    mkdir -p "$dst"
    # 원본에 있는 스킬을 저장소로 복사 (저장소에만 있는 파일은 건드리지 않음)
    rsync -a --exclude '.DS_Store' "$src"/ "$dst"/
  else
    echo "  ⚠ $label 원본 폴더 없음 → 건너뜀: $src"
    echo "    (경로가 다르면 스크립트 위쪽 SRC_* 값을 고치세요)"
  fi
}

echo "▶ 데스크탑 PC의 스킬을 저장소로 모으는 중..."
copy_if_exists "$SRC_DESKTOP_SKILLS" "$DST_DESKTOP" "데스크탑 앱 스킬"
copy_if_exists "$SRC_CODE_SKILLS"    "$DST_CODE"    "Claude Code 스킬"

echo "▶ 변경 사항 확인..."
cd "$REPO_DIR"
if git diff --quiet && git diff --cached --quiet; then
  echo "✅ 바뀐 게 없습니다. 이미 GitHub와 같은 상태예요. (올릴 것 없음)"
  exit 0
fi

git add -A
git status --short

echo "▶ GitHub에 올리는 중..."
git commit -m "$MSG"

# push 실패 시 (네트워크 문제) 지수 백오프로 최대 4회 재시도
for delay in 0 2 4 8; do
  [ "$delay" -gt 0 ] && { echo "  …$delay초 후 재시도"; sleep "$delay"; }
  if git push -u origin "$BRANCH"; then
    echo "✅ 완료! 이제 핸드폰/웹을 새로고침하면 같은 내용이 보입니다."
    exit 0
  fi
done

echo "❌ push 실패. 인터넷 연결을 확인하고 다시 실행하세요."
exit 1

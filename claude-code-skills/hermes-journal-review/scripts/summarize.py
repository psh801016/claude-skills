#!/usr/bin/env python3
"""에이전트 저널을 집계해 한 화면 요약으로 만든다.

저널 원본(compaction.jsonl)을 통째로 읽으면 토큰만 먹는다. 판단에 필요한
숫자와 이상징후만 뽑아 주고, 해석·제안은 읽는 쪽(HERMES)이 한다.

경로는 실행 위치에 따라 다르다:
  - 도커 HERMES 안: /opt/data/agent-journal/
  - 윈도우 호스트  : ~/.hermes/agent-journal/
둘 다 같은 폴더의 두 얼굴이라 존재하는 쪽을 자동으로 고른다.

읽기 전용. 아무것도 고치지 않는다.
"""
import json
import os
import sys
from collections import Counter, defaultdict

# Windows legacy consoles may use CP949, which cannot print the em dash in the
# normal "저널 없음" status line. Keep this read-only reporter runnable there.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CANDIDATES = ["/opt/data/agent-journal", os.path.join(os.path.expanduser("~"), ".hermes", "agent-journal")]


def journal_path():
    for d in CANDIDATES:
        p = os.path.join(d, "compaction.jsonl")
        if os.path.exists(p):
            return p
    return None


def load(path, days=None):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                rows.append({"_broken": line[:120]})
    if days:
        cut = f"{days}"
        rows = [r for r in rows if r.get("ts", "") >= cut]
    return rows


def summarize(rows):
    out = []
    add = out.append
    add(f"# 에이전트 저널 요약 — {len(rows)}건")

    broken = [r for r in rows if "_broken" in r or "parse_error" in r]
    runtimes = Counter(r.get("runtime", "?") for r in rows if "_broken" not in r)
    events = Counter(r.get("event", "?") for r in rows if "_broken" not in r)

    add("")
    add("## 런타임별")
    for k, v in runtimes.most_common():
        add(f"- {k}: {v}건")
    add("")
    add("## 이벤트별")
    for k, v in events.most_common():
        add(f"- {k}: {v}건")

    # 압축 관련 — Claude/Codex
    comp = [r for r in rows if r.get("event") == "PreCompact"]
    if comp:
        trig = Counter(r.get("trigger", "?") for r in comp)
        add("")
        add("## 압축")
        add(f"- 총 {len(comp)}회 (자동 {trig.get('auto', 0)} / 수동 {trig.get('manual', 0)})")
        # 같은 세션이 3회 넘게 압축되면 복사본의 복사본이라 신뢰도가 떨어진다.
        per = Counter(r.get("session", "?") for r in comp)
        heavy = [(s, n) for s, n in per.most_common() if n >= 3]
        if heavy:
            add("- ⚠ 3회 이상 압축된 세션(맥락 열화 의심):")
            for s, n in heavy[:5]:
                add(f"    {s}: {n}회")
        cwds = Counter(r.get("cwd", "?") for r in comp)
        add("- 압축이 잦은 작업폴더:")
        for c, n in cwds.most_common(5):
            add(f"    {n}회  {c}")
        wants = [r.get("user_instructions", "") for r in comp if r.get("user_instructions")]
        if wants:
            add(f"- 사용자가 직접 준 압축 지시 {len(wants)}건:")
            for w in wants[:5]:
                add(f"    \"{w[:80]}\"")

    # Antigravity Stop
    stops = [r for r in rows if r.get("event") == "Stop"]
    if stops:
        add("")
        add("## Antigravity 작업 종료")
        add(f"- 총 {len(stops)}회")
        for label, key in (("모델", "model"), ("종료사유", "reason")):
            c = Counter(r.get(key, "") for r in stops if r.get(key))
            if c:
                add(f"- {label}: " + ", ".join(f"{k} {v}회" for k, v in c.most_common(5)))
        errs = [r for r in stops if r.get("error")]
        if errs:
            add(f"- ⚠ 오류로 끝난 작업 {len(errs)}건:")
            for e in errs[:5]:
                add(f"    {e.get('session', '?')}: {e['error'][:100]}")
        ws = Counter(r.get("workspace", "") for r in stops if r.get("workspace"))
        if ws:
            add("- 작업 위치:")
            for w, n in ws.most_common(5):
                add(f"    {n}회  {w}")
        add("- 최근 transcript(원인 파악이 필요할 때만 열 것):")
        for r in stops[-3:]:
            if r.get("transcript"):
                add(f"    {r.get('session', '?')}  {r['transcript']}")

    if broken:
        add("")
        add(f"## ⚠ 깨진 기록 {len(broken)}건 — 훅 계약이 바뀌었을 수 있음")
        for b in broken[:3]:
            add(f"- {b.get('parse_error') or b.get('_broken')}")

    return "\n".join(out)


def main():
    p = journal_path()
    if not p:
        print("저널 없음 — 아직 한 건도 기록되지 않았습니다.")
        print("찾아본 경로: " + ", ".join(CANDIDATES))
        return 0
    rows = load(p, days=sys.argv[1] if len(sys.argv) > 1 and sys.argv[1][:2] == "20" else None)
    if not rows:
        print(f"저널은 있으나 비어 있습니다: {p}")
        return 0
    print(summarize(rows))
    print("")
    print(f"(원본: {p})")
    return 0


def demo():
    """자체 점검 — 합성 데이터로 집계가 맞는지, 빈 파일에도 안 죽는지."""
    import tempfile
    rows = [
        {"ts": "2026-08-13T01:00:00+00:00", "event": "PreCompact", "runtime": "claude",
         "trigger": "auto", "session": "aaa11111", "cwd": r"C:\p1", "user_instructions": ""},
        {"ts": "2026-08-13T02:00:00+00:00", "event": "PreCompact", "runtime": "claude",
         "trigger": "auto", "session": "aaa11111", "cwd": r"C:\p1", "user_instructions": ""},
        {"ts": "2026-08-13T03:00:00+00:00", "event": "PreCompact", "runtime": "codex",
         "trigger": "manual", "session": "aaa11111", "cwd": r"C:\p1",
         "user_instructions": "디자인 결정만"},
        {"ts": "2026-08-13T04:00:00+00:00", "event": "Stop", "runtime": "antigravity",
         "session": "bbb22222", "model": "gemini-3.1-flash-lite", "reason": "NO_TOOL_CALL",
         "workspace": r"C:\w1", "transcript": "C:/t.jsonl", "error": "boom"},
    ]
    fd, tmp = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    with open(tmp, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        fh.write("깨진줄{{{\n")

    txt = summarize(load(tmp))
    assert "claude: 2건" in txt, txt
    assert "codex: 1건" in txt, txt
    assert "antigravity: 1건" in txt, txt
    assert "자동 2 / 수동 1" in txt, txt
    assert "aaa11111: 3회" in txt, "3회 이상 압축 경고 누락"
    assert "디자인 결정만" in txt, "사용자 압축 지시 누락"
    assert "boom" in txt, "오류 종료 누락"
    assert "깨진 기록 1건" in txt, "깨진 줄 경고 누락"
    os.remove(tmp)

    # 빈 파일에도 안 죽어야 한다.
    fd, tmp2 = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    assert summarize(load(tmp2)).startswith("# 에이전트 저널 요약 — 0건")
    os.remove(tmp2)
    print("OK  집계 4종 + 경고 3종 + 빈파일 통과")


if __name__ == "__main__":
    if "--check" in sys.argv:
        demo()
    else:
        sys.exit(main())

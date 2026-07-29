#!/usr/bin/env python3
"""Shared append-only outcome registry for Codex and Gemini routing."""
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

STATE = Path.home() / ".agents" / "state" / "model-effort-registry.jsonl"
WORDS = re.compile(r"[a-z0-9\u3131-\uD79D]+", re.I)


def load():
    if not STATE.exists():
        return []
    rows = []
    for line in STATE.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            rows.append(json.loads(line))
        except (ValueError, TypeError):
            pass
    return rows


def tokens(value):
    return set(WORDS.findall((value or "").lower()))


def axes(value):
    return {item.strip().lower() for item in (value or "").split(",") if item.strip()}


def record(args):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": datetime.now().isoformat(timespec="seconds"), "task": args.task,
        "axes": args.axes, "provider": args.provider, "model": args.model,
        "effort": args.effort, "outcome": args.outcome, "reason": args.reason,
        "cost": args.cost, "minutes": args.minutes,
    }
    with STATE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({"recorded": row}, ensure_ascii=False))


def query(args):
    wanted_tokens, wanted_axes = tokens(args.task), axes(args.axes)
    matches = []
    for row in load():
        row_tokens = tokens(row.get("task"))
        keyword = len(wanted_tokens & row_tokens) / (len(wanted_tokens | row_tokens) or 1)
        axis_score = len(wanted_axes & axes(row.get("axes"))) / 4 if wanted_axes else 0
        score = keyword * 0.6 + axis_score * 0.4
        if score > 0.08:
            matches.append((score, row))
    matches.sort(key=lambda item: item[0], reverse=True)
    top = [row for _, row in matches[:8]]
    print(json.dumps({
        "matched": len(top),
        "successes": [row for row in top if row.get("outcome") == "success"][:4],
        "avoid": [row for row in top if row.get("outcome") == "fail"][:4],
    }, ensure_ascii=False, indent=2))


def stats(_args):
    rows = load()
    summary = {}
    for row in rows:
        key = f"{row.get('provider')}:{row.get('model')}:{row.get('effort')}"
        bucket = summary.setdefault(key, {"success": 0, "fail": 0, "partial": 0})
        bucket[row.get("outcome", "partial")] += 1
    print(json.dumps({"total": len(rows), "by_combo": summary}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    q = sub.add_parser("query")
    q.add_argument("task")
    q.add_argument("--axes", default="")
    q.set_defaults(run=query)
    r = sub.add_parser("record")
    r.add_argument("--task", required=True)
    r.add_argument("--axes", default="")
    r.add_argument("--provider", required=True, choices=["codex", "gemini", "claude"])
    r.add_argument("--model", required=True)
    r.add_argument("--effort", default="")
    r.add_argument("--outcome", required=True, choices=["success", "fail", "partial"])
    r.add_argument("--reason", default="")
    r.add_argument("--cost", type=float)
    r.add_argument("--minutes", type=float)
    r.set_defaults(run=record)
    s = sub.add_parser("stats")
    s.set_defaults(run=stats)
    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()

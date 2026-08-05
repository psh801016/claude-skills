---
name: adaptive-model-effort-advisor
description: Recommend the cheapest reliable Codex, Gemini, or Claude model and reasoning effort for a task, with one escalation step. Use when the user asks which model to use, asks to cut cost or latency, compares models or effort levels, reports poor results from a model, routes through C:\Users\PSH\dev\multi-model, or wants prior recommendations re-evaluated after a model upgrade.
---

# Adaptive Model Effort Advisor

Choose model capacity and reasoning time independently. Start cheaply, verify, and escalate only at the observed failure point. Never treat the newest or largest model as automatically best.

## When to run

Run this when the user raises model choice, cost, or latency — or when a route has already failed and needs escalating.

**Do not run it on every request, and do not announce a route before ordinary work.** That announcement was written when models could not plan their own approach; current models do, so a forced preamble on every task costs tokens and adds nothing. If the user has not raised model choice and the default route is working, skip this skill entirely.

(2026-08-05: always-on invocation removed. Rationale in `DECISIONS.md` → ADR 2026-08-05.)

## Workflow

1. Classify the task as `verifiable=yes|partial|no`, `failcost=low|mid|high`, `volume=high|low`, and `depth=shallow|mid|deep`.
2. Query prior outcomes before using heuristics:
   `python scripts/registry.py query "<task>" --axes "verifiable=...,failcost=...,volume=...,depth=..."`
3. Resolve the current model name immediately before recommending:
   `python scripts/recommend.py "<task>" --provider codex|gemini|claude --axes "verifiable=...,failcost=...,volume=...,depth=..."`
   Never emit a current release number from this table. Use the script's `model`, `effort`, and `source` fields.
4. Pick the lowest-cost starting route that can meet the Definition of Done.
5. State one mechanical or human verification check and exactly one next escalation.
6. Record the measured outcome with `scripts/registry.py record`; do not record an unverified success.

## Cold-start routes

| Task | Codex | Gemini harness | Claude Code |
|---|---|---|---|
| Formal, repeatable, mechanically verifiable | Luna + Medium | `gemini-low` | `opus --effort low` |
| Judgment, analysis, ordinary implementation | Terra + High | `gemini` | `opus --effort medium` |
| Complex build with tests or render checks | Terra + Max | `gemini-pro` | `opus --effort high` |
| Deep knowledge, architecture, security, high failure cost | Sol + High | `gemini-pro` plus independent verification | `opus --effort xhigh`, then Max only on failure |

For Codex, `scripts/recommend.py` reads the current `models_cache.json` and selects the newest tier-compatible slug; do not hard-code a release number. For Gemini on this machine, do not use the blocked Gemini CLI OAuth path; use `C:\Users\PSH\dev\multi-model\consult.ps1`. Its provider strategies resolve current proxy models at call time and retain fixed fallbacks.

For Claude Code, use the official `opus` alias so upgrades automatically follow the latest available Opus. Vary `--effort` by task instead of changing to Sonnet; the user's policy reserves Opus for planning and implementation. Do not select Fable automatically until usage-credit authorization is explicitly re-confirmed. The Antigravity `opus-ag` route resolves the latest exposed Opus thinking model at call time.

Inspect Gemini resolution without spending a model call:

```powershell
& C:\Users\PSH\dev\multi-model\consult.ps1 -Provider gemini-pro -Prompt ignored -ResolveOnly
```

## Escalation rules

- Shallow or wrong at low effort: raise effort one step on the same tier.
- Still wrong at High: raise model capacity, not effort.
- Literal benchmark gaming or endless polishing: lower effort, tighten the acceptance test, and add a stop condition.
- Use Ultra only when the task has independent subproblems worth parallelizing. Most tasks do not need it.
- After any provider upgrade, rerun one familiar task per task class and record success, failure, duration, and cost. Personal measurements override this table.

## Output

Return: recommendation, four-axis reason, verification check, escalation, and resolved/current route before starting the work. Keep it concise unless the user requests a comparison report.

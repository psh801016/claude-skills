---
name: adaptive-model-effort-advisor
description: Recommend the cheapest reliable Codex, Gemini, or Claude model and reasoning effort for a task, with one escalation step. Apply proactively before any non-trivial work — state the route without waiting to be asked. Also use when the user asks which model to use, asks to cut cost or latency, compares models or effort levels, reports poor results, routes through C:\Users\PSH\dev\multi-model, or wants prior recommendations re-evaluated after a model upgrade.
---

# Adaptive Model Effort Advisor

Choose model capacity and reasoning time independently. Start cheaply, verify, and escalate only at the observed failure point. Never treat the newest or largest model as automatically best.

Apply this proactively to every non-trivial user request. Do not wait for the user to ask which model to use. Before executing substantial analysis, coding, design, research, or document work, state the resolved provider/model/effort and one escalation path. Skip the announcement only for trivial one-step requests where routing has no practical benefit.

> 2026-08-06: 상시 발동을 해제하자는 제안(ADR 2026-08-05)이 있었으나 **ASURA님이 기각**했다.
> 2026-07-19 사용자 지시로 못박힌 규칙이라 유지한다. description만 압축했다.
> 이 절을 다시 지우자는 제안이 나오면 이 줄을 먼저 읽는다.

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

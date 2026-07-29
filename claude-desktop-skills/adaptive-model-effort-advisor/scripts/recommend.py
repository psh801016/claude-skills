#!/usr/bin/env python3
"""Resolve current provider model recommendations without hard-coded release numbers."""
import argparse
import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def parse_axes(value):
    result = {}
    for item in (value or "").split(","):
        if "=" in item:
            key, val = item.split("=", 1)
            result[key.strip().lower()] = val.strip().lower()
    return result


def effort_for(axes):
    if axes.get("depth") == "deep" or axes.get("failcost") == "high":
        return "xhigh"
    if axes.get("depth") == "mid" or axes.get("failcost") == "mid":
        return "high"
    if axes.get("volume") == "high" or axes.get("depth") == "shallow":
        return "low"
    return "medium"


def codex_model(axes):
    cache = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "models_cache.json"
    rows = []
    try:
        data = json.loads(cache.read_text(encoding="utf-8"))
        rows = data.get("models", []) if isinstance(data, dict) else []
    except (OSError, ValueError, TypeError):
        pass
    tiers = {"luna": [], "terra": [], "sol": []}
    pattern = re.compile(r"^gpt-(\d+)\.(\d+)-(luna|terra|sol)$", re.I)
    for row in rows:
        match = pattern.match(str(row.get("slug", "")))
        if match:
            tiers[match.group(3).lower()].append((int(match.group(1)), int(match.group(2)), row["slug"]))
    tier = "sol" if axes.get("depth") == "deep" or axes.get("failcost") == "high" else "terra"
    if axes.get("volume") == "high" and tier != "sol":
        tier = "luna"
    candidates = sorted(tiers[tier], reverse=True)
    return (candidates[0][2] if candidates else f"latest-codex-{tier}"), "codex-models-cache" if candidates else "codex-alias-fallback"


def gemini_models(url):
    request = urllib.request.Request(url.rstrip("/") + "/v1/models", headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=3) as response:
        data = json.load(response)
    return data.get("data", []) if isinstance(data, dict) else []


def gemini_model(axes, proxy_url):
    try:
        models = gemini_models(proxy_url)
    except Exception:
        models = []
    def version(item):
        match = re.search(r"(\d+)(?:\.(\d+))?", str(item.get("id", "")) + " " + str(item.get("description", "")))
        return (int(match.group(1)), int(match.group(2) or 0)) if match else (0, 0)
    def choose(predicate, prefer_quality=False):
        found = [item for item in models if predicate(item)]
        def rank(item):
            text = (str(item.get("id", "")) + " " + str(item.get("description", ""))).lower()
            quality = 0
            if prefer_quality:
                if "high" in text or "agent" in text:
                    quality += 3
                if "low" in text or "lite" in text:
                    quality -= 2
            return quality, version(item)
        return sorted(found, key=rank, reverse=True)[0].get("id") if found else None
    if axes.get("depth") == "deep" or axes.get("failcost") == "high":
        model = choose(lambda x: "pro" in (str(x.get("id", "")) + str(x.get("description", ""))).lower(), True)
        return model or "latest-pro", "gemini-live-catalog" if model else "gemini-alias-fallback"
    if axes.get("volume") == "high":
        model = choose(lambda x: "lite" in (str(x.get("id", "")) + str(x.get("description", ""))).lower())
        return model or "latest-lite", "gemini-live-catalog" if model else "gemini-alias-fallback"
    model = choose(lambda x: "flash" in (str(x.get("id", "")) + str(x.get("description", ""))).lower() and "lite" not in str(x.get("id", "")).lower(), True)
    return model or "latest-flash", "gemini-live-catalog" if model else "gemini-alias-fallback"


def recommend(args):
    axes = parse_axes(args.axes)
    provider = args.provider
    if provider == "auto":
        provider = "codex"
    if provider == "codex":
        model, source = codex_model(axes)
        effort = effort_for(axes)
    elif provider == "gemini":
        model, source = gemini_model(axes, args.proxy_url)
        effort = effort_for(axes)
    elif provider == "claude":
        model, source, effort = "opus", "claude-official-alias", effort_for(axes)
    else:
        raise ValueError(provider)
    escalation = "raise effort one step, then move to the next capacity tier after a failed verification"
    print(json.dumps({"task": args.task, "provider": provider, "model": model, "effort": effort,
                      "escalation": escalation, "source": source,
                      "catalog_checked_at": datetime.now(timezone.utc).isoformat()}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task")
    parser.add_argument("--provider", choices=["auto", "codex", "gemini", "claude"], default="auto")
    parser.add_argument("--axes", default="")
    parser.add_argument("--proxy-url", default="http://localhost:8080")
    args = parser.parse_args()
    recommend(args)


if __name__ == "__main__":
    main()

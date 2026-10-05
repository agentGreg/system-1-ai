"""Shared helpers for experiment 06: item sets reused from experiments 03/04/05, item variants (facts block, rule moved
into the state), hardware, JSONL, Wilson intervals, OpenRouter calls with a hard budget.

The OpenRouter API key is read from the macOS keychain at start-up and kept in memory only; it is never printed,
logged or written. Every paid call's usage.cost is appended to costs.jsonl; `check_budget()` stops a script before a
call once the cumulative cost of this experiment reaches BUDGET_USD.
"""
import json
import math
import platform
import re
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
E03 = EXP / "03-extended-set"
E04 = EXP / "04-multi-domain"
E05 = EXP / "05-rule-decomposition"
CAT03 = {"R": "reklamacja", "D": "routing", "E": "eskalacja", "K": "kompletnosc", "S": "irytacja", "P": "phishing"}
COSTS = HERE / "costs.jsonl"
BUDGET_USD = 1.0
SAFETY_USD = 0.05
CLIENT = "Poland, residential connection"


def read_jsonl(path):
    p = Path(path)
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def write_jsonl(path, rows):
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def split_rule(question):
    """'Czy ...? Reguła: ...' -> ('Czy ...?', 'Reguła: ...'); (question, None) when there is no 'Reguła:'."""
    k = question.find(" Reguła:")
    if k < 0:
        return question, None
    return question[:k].strip(), question[k + 1:].strip()


def load_set(name):
    """Items of one set, each with id, type, state, question, options, gold, category (+ set-specific fields)."""
    if name == "e03":
        items = read_jsonl(E03 / "decisions.jsonl")
        for it in items:
            it["category"] = CAT03[it["id"][0]]
        return items
    if name == "e04":
        items = read_jsonl(E04 / "decisions.jsonl")
        for it in items:
            it["category"] = it["domain"]
        return items
    if name == "rules99":  # the 99 rule items of experiment 05 (60 exp-04 rule_based + 39 clean exp-03 completeness)
        items = read_jsonl(E05 / "items.jsonl")
        for it in items:
            it["category"] = it["block"]
        return items
    if name in ("rc_orig", "rc_changed"):  # rule-change test (rule_change_items.jsonl, gold written before any run)
        v = name[3:]
        out = []
        for r in read_jsonl(HERE / "rule_change_items.jsonl"):
            out.append({"id": f'{r["id"]}@{v}', "base_id": r["id"], "version": v, "type": r["type"],
                        "category": r["kind"], "block": r["block"], "state": r["state"],
                        "question": r[f"question_{v}"], "options": r["options"], "gold": r[f"gold_{v}"],
                        "clause": r[f"clause_{v}"], "keys": ["true", "false"]})
        return out
    raise ValueError(name)


def variant(it, facts=False, rule_in_state=False, inject=None):
    """Return (state, question) for an item under a variant.
    rule_in_state: the 'Reguła: ...' part of the question is appended to the state as its last paragraph and the
    question keeps only its first sentence (items without 'Reguła:' are unchanged).
    facts: basal's facts.inject() on the (possibly extended) state, exactly what basal-serve does for "facts": "auto"."""
    state, question = it["state"], it["question"]
    if rule_in_state:
        head, rule = split_rule(question)
        if rule:
            state, question = state + "\n\n" + rule, head
    if facts:
        state = inject(state)
    return state, question


def hardware():
    def sysctl(k):
        return subprocess.run(["sysctl", "-n", k], capture_output=True, text=True).stdout.strip()
    return {"chip": sysctl("machdep.cpu.brand_string"), "ram_gb": int(sysctl("hw.memsize")) // 2**30,
            "macos": platform.mac_ver()[0], "python": platform.python_version()}


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def spent():
    return sum(r.get("cost") or 0.0 for r in read_jsonl(COSTS))


class BudgetExceeded(RuntimeError):
    pass


def check_budget(next_estimate=0.0):
    s = spent()
    if s + next_estimate >= BUDGET_USD - SAFETY_USD:
        raise BudgetExceeded(f"spent ${s:.4f}; cap ${BUDGET_USD} (safety ${SAFETY_USD})")
    return s


def log_cost(label, model, item_id, cost, served=None, extra=None):
    with COSTS.open("a") as fh:
        fh.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "label": label, "model_requested": model,
                             "model_served": served, "id": item_id, "cost": cost, **(extra or {})}) + "\n")


def api_key():
    return subprocess.run(["security", "find-generic-password", "-s", "openrouter-api-key", "-w"],
                          capture_output=True, text=True, check=True).stdout.strip()


def post(key, url, body, timeout=180, retries=3, headers=None):
    """POST JSON; retries only transport errors, 429 and 5xx. Returns (data, status, latency_ms, attempts)."""
    attempts = []
    h = {"Content-Type": "application/json"}
    if key:
        h.update({"Authorization": f"Bearer {key}", "HTTP-Referer": "https://github.com/agentGreg/system-1-ai",
                  "X-Title": "system-1-ai experiment 06"})
    for attempt in range(retries):
        req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST", headers=h)
        t = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data, status = json.loads(r.read()), r.status
        except urllib.error.HTTPError as e:
            body_txt = re.sub(r"(user_id\\?\"\s*:\s*\\?\")[^\"\\]*", r"\1<redacted>", e.read().decode(errors="replace"))
            data, status = {"error": {"http": e.code, "body": body_txt[:2000]}}, e.code
        except Exception as e:  # timeouts, connection errors
            data, status = {"error": {"exception": repr(e)[:500]}}, None
        lat = (time.perf_counter() - t) * 1000
        attempts.append({"status": status, "latency_ms": lat, "error": data.get("error")})
        if "error" not in data or not (status is None or status == 429 or (status or 0) >= 500):
            break
        time.sleep(2 * (attempt + 1))
    return data, status, lat, attempts

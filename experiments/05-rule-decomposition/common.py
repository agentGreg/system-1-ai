"""Shared helpers for experiment 05: test set, hardware, JSONL, OpenRouter calls with a hard budget.

The OpenRouter API key is read from the macOS keychain at start-up and kept in memory only; it is never printed,
logged or written. Every paid call's usage.cost is appended to costs.jsonl; `check_budget()` stops a script before a
call once the cumulative cost of this experiment reaches BUDGET_USD.
"""
import json
import re
import platform
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
COSTS = HERE / "costs.jsonl"
BUDGET_USD = 3.0
SAFETY_USD = 0.10  # stop this far below the hard cap
CLIENT = "Poland, residential connection"


def hardware():
    def sysctl(k):
        return subprocess.run(["sysctl", "-n", k], capture_output=True, text=True).stdout.strip()
    return {"chip": sysctl("machdep.cpu.brand_string"), "ram_gb": int(sysctl("hw.memsize")) // 2**30,
            "macos": platform.mac_ver()[0], "python": platform.python_version()}


def write_jsonl(path, rows):
    Path(path).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def read_jsonl(path):
    p = Path(path)
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


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


def post(key, url, body, timeout=180, retries=3):
    """POST JSON; retries only transport errors, 429 and 5xx. Returns (data, status, latency_ms, attempts)."""
    attempts = []
    for attempt in range(retries):
        req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                              "HTTP-Referer": "https://github.com/agentGreg/system-1-ai",
                                              "X-Title": "system-1-ai experiment 05"})
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

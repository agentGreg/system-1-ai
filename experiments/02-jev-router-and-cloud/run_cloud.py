"""Cloud LLMs via OpenRouter on the same 30 decisions as experiment 01 (same prompt, same option lettering).

The prompt (SYSTEM / USER), the option lettering (A, B, C ... in the original order) and the answer parser are
copied verbatim from ../01-basal-vs-thinking/run_llm.py (the Qwen runs), so the numbers are comparable.
Calls are sequential, one decision per call, non-streaming. Latency is wall clock from just before the HTTPS request
to the full response, measured on the client (Poland), so it includes network and OpenRouter/provider queueing.

The API key is read from the macOS keychain at start-up and kept in memory only. It is never printed or written.
Every call's exact cost (usage.cost, via "usage": {"include": true}) is appended to costs.jsonl and the script stops
before a call if the cumulative cost of the whole experiment reaches --budget.

usage: python run_cloud.py --model typesafe/jev-router --label jev-router --out raw_jev-router.jsonl
       python run_cloud.py --model openai/gpt-6.1-sol --reasoning '{"effort":"medium"}' --label ... --out ...
       add --limit 2 for a smoke test
"""
import argparse
import json
import re
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP01 = HERE.parent / "01-basal-vs-thinking"
CATEGORY = {"R": "reklamacja", "D": "routing", "E": "eskalacja", "K": "kompletnosc"}
URL = "https://openrouter.ai/api/v1/chat/completions"
COSTS = HERE / "costs.jsonl"

# --- verbatim from ../01-basal-vs-thinking/run_llm.py ---
LETTERS = "ABCDEFGHIJ"
SYSTEM = "Jesteś asystentem działu obsługi klienta. Oceniasz sprawę i wybierasz dokładnie jedną z podanych opcji."
USER = ("Wiadomość / zgłoszenie:\n{state}\n\nPytanie: {q}\nOpcje:\n{opts}\n\n"
        "Odpowiedz wyłącznie literą wybranej opcji (np. A).")


def parse_letter(text, k):
    ans = text.split("</think>")[-1]
    m = re.findall(rf"\b([{LETTERS[:k]}])\b", ans)
    return LETTERS.index(m[0]) if m else None
# --- end verbatim ---


def load_items():
    items = [json.loads(l) for l in (EXP01 / "decisions.jsonl").read_text().splitlines() if l.strip()]
    for it in items:
        it["category"] = CATEGORY[it["id"][0]]
    return items


def spent():
    if not COSTS.exists():
        return 0.0
    return sum(json.loads(l).get("cost") or 0.0 for l in COSTS.read_text().splitlines() if l.strip())


def api_key():
    return subprocess.run(["security", "find-generic-password", "-s", "openrouter-api-key", "-w"],
                          capture_output=True, text=True, check=True).stdout.strip()


def call(key, body, timeout):
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                                          "HTTP-Referer": "https://github.com/agentGreg/system-1-ai",
                                          "X-Title": "system-1-ai experiment 02"})
    t = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
            status = r.status
    except urllib.error.HTTPError as e:
        data, status = {"error": {"http": e.code, "body": e.read().decode(errors="replace")[:2000]}}, e.code
    except Exception as e:  # timeouts, connection errors
        data, status = {"error": {"exception": repr(e)[:500]}}, None
    return data, status, (time.perf_counter() - t) * 1000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--reasoning", default=None, help='JSON for the OpenRouter "reasoning" field, or omit')
    ap.add_argument("--max-tokens", type=int, default=8192)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--budget", type=float, default=4.5)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    reasoning = json.loads(a.reasoning) if a.reasoning else None
    key = api_key()
    items = load_items()[: a.limit] if a.limit else load_items()
    rows = []
    for it in items:
        if spent() >= a.budget:
            print(f"BUDGET STOP: spent ${spent():.4f} >= ${a.budget}", flush=True)
            break
        k = len(it["options"])
        opts = "\n".join(f"{LETTERS[i]}. {o}" for i, o in enumerate(it["options"]))
        body = {"model": a.model, "max_tokens": a.max_tokens, "usage": {"include": True},
                "messages": [{"role": "system", "content": SYSTEM},
                             {"role": "user", "content": USER.format(state=it["state"], q=it["question"],
                                                                     opts=opts)}]}
        if reasoning is not None:
            body["reasoning"] = reasoning
        attempts = []
        for attempt in range(3):  # retry only transport / 429 / 5xx errors
            data, status, lat = call(key, body, a.timeout)
            attempts.append({"status": status, "latency_ms": lat, "error": data.get("error")})
            if "error" not in data or not (status is None or status == 429 or (status or 0) >= 500):
                break
            time.sleep(2 * (attempt + 1))
        usage = data.get("usage") or {}
        cost = usage.get("cost")
        with COSTS.open("a") as fh:
            fh.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "label": a.label,
                                 "model_requested": a.model, "model_served": data.get("model"),
                                 "id": it["id"], "cost": cost, "attempts": len(attempts)}) + "\n")
        choice = (data.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        content = msg.get("content") or ""
        pred = parse_letter(content, k) if content else None
        ctd = usage.get("completion_tokens_details") or {}
        row = {"id": it["id"], "category": it["category"], "type": it["type"], "tricky": it["tricky"],
               "gold": it["gold"], "pred": pred, "correct": pred == it["gold"],
               "latency_ms": attempts[-1]["latency_ms"], "attempts": attempts,
               "http_status": attempts[-1]["status"], "error": data.get("error"),
               "model_requested": a.model, "model_served": data.get("model"), "provider": data.get("provider"),
               "finish_reason": choice.get("finish_reason"), "native_finish_reason": choice.get("native_finish_reason"),
               "input_tokens": usage.get("prompt_tokens"), "output_tokens": usage.get("completion_tokens"),
               "reasoning_tokens": ctd.get("reasoning_tokens"), "cost": cost, "usage": usage,
               "answer_text": content.strip(), "reasoning_text": msg.get("reasoning"),
               "extra_keys": sorted(set(data) - {"id", "model", "provider", "choices", "usage", "object",
                                                 "created", "system_fingerprint"}),
               "response_id": data.get("id")}
        # keep any non-standard top-level fields the router may add (routing metadata etc.)
        for x in row["extra_keys"]:
            row["x_" + x] = data[x]
        rows.append(row)
        print(f'{it["id"]} gold={it["gold"]} pred={pred} served={data.get("model")} '
              f'out={usage.get("completion_tokens")} reas={ctd.get("reasoning_tokens")} '
              f'{attempts[-1]["latency_ms"]/1000:.2f}s ${cost} err={bool(data.get("error"))}', flush=True)
    out = HERE / a.out
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    meta = {"system": a.label, "model_requested": a.model, "reasoning": reasoning, "max_tokens": a.max_tokens,
            "temperature": "provider default (not sent)", "date_utc": datetime.now(timezone.utc).isoformat(),
            "endpoint": URL, "client_location": "Poland, residential connection",
            "n": len(rows), "calls_sequential": True, "streaming": False}
    out.with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    n_ok = sum(r["correct"] for r in rows)
    print(f"acc {n_ok}/{len(rows)}  run cost ${sum(r['cost'] or 0 for r in rows):.5f}  total spent ${spent():.5f}")


if __name__ == "__main__":
    main()

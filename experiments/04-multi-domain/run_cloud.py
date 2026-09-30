"""Reference chat LLMs via OpenRouter on the experiment 04 decisions (same prompt and lettering as experiments 01-03).

USER and parse_letter are copied verbatim from ../01-basal-vs-thinking/run_llm.py, as in experiments 02 and 03. The
system prompt drops "customer service department" (12 domains here) and says "an assistant working in a company or
institution"; nothing else changed. Original option order only. Calls are sequential, one decision per call, non-streaming; latency is
wall clock on the client (Poland) from just before the HTTPS request to the full response, so it includes network
and provider queueing. usage.cost of every call goes to costs.jsonl and the budget cap is enforced.

usage: python run_cloud.py --model google/gemini-3.8-flash --reasoning '{"effort":"medium"}' --label ... --out ...
"""
import argparse
import json
import re
from datetime import datetime, timezone

from common import (CLIENT, HERE, BudgetExceeded, api_key, check_budget, load_items, log_cost, post, spent,
                    write_jsonl)

URL = "https://openrouter.ai/api/v1/chat/completions"

# --- from ../01-basal-vs-thinking/run_llm.py (system prompt generalised, see docstring) ---
LETTERS = "ABCDEFGHIJ"
SYSTEM = ("Jesteś asystentem pracującym w firmie lub instytucji. Oceniasz sprawę i wybierasz dokładnie jedną z "
          "podanych opcji.")
USER = ("Wiadomość / zgłoszenie:\n{state}\n\nPytanie: {q}\nOpcje:\n{opts}\n\n"
        "Odpowiedz wyłącznie literą wybranej opcji (np. A).")


def parse_letter(text, k):
    ans = text.split("</think>")[-1]
    m = re.findall(rf"\b([{LETTERS[:k]}])\b", ans)
    return LETTERS.index(m[0]) if m else None
# --- end ---


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--reasoning", default=None, help='JSON for the OpenRouter "reasoning" field, or omit')
    ap.add_argument("--max-tokens", type=int, default=8192)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    reasoning = json.loads(a.reasoning) if a.reasoning else None
    key = api_key()
    items = load_items()[: a.limit] if a.limit else load_items()
    rows = []
    try:
        for it in items:
            check_budget(0.02)
            k = len(it["options"])
            opts = "\n".join(f"{LETTERS[i]}. {o}" for i, o in enumerate(it["options"]))
            body = {"model": a.model, "max_tokens": a.max_tokens, "usage": {"include": True},
                    "messages": [{"role": "system", "content": SYSTEM},
                                 {"role": "user", "content": USER.format(state=it["state"], q=it["question"],
                                                                         opts=opts)}]}
            if reasoning is not None:
                body["reasoning"] = reasoning
            data, status, lat, attempts = post(key, URL, body, timeout=180)
            usage = data.get("usage") or {}
            cost = usage.get("cost")
            log_cost(a.label, a.model, it["id"], cost, data.get("model"))
            choice = (data.get("choices") or [{}])[0]
            msg = choice.get("message") or {}
            content = msg.get("content") or ""
            pred = parse_letter(content, k) if content else None
            ctd = usage.get("completion_tokens_details") or {}
            rows.append({"id": it["id"], "category": it["category"], "domain": it["domain"], "type": it["type"],
                         "rule_based": it["rule_based"], "tricky": it["tricky"],
                         "gold": it["gold"], "pred": pred, "correct": pred == it["gold"],
                         "latency_ms": lat, "attempts": attempts, "http_status": status, "error": data.get("error"),
                         "model_requested": a.model, "model_served": data.get("model"),
                         "provider": data.get("provider"), "finish_reason": choice.get("finish_reason"),
                         "input_tokens": usage.get("prompt_tokens"), "output_tokens": usage.get("completion_tokens"),
                         "reasoning_tokens": ctd.get("reasoning_tokens"), "cost": cost, "usage": usage,
                         "answer_text": content.strip(), "reasoning_text": msg.get("reasoning"),
                         "response_id": data.get("id")})
            print(f'{it["id"]} gold={it["gold"]} pred={pred} served={data.get("model")} '
                  f'out={usage.get("completion_tokens")} reas={ctd.get("reasoning_tokens")} {lat/1000:.2f}s ${cost}',
                  flush=True)
    except BudgetExceeded as e:
        print("BUDGET STOP:", e, flush=True)
    write_jsonl(HERE / a.out, rows)
    meta = {"system": a.label, "model_requested": a.model, "reasoning": reasoning, "max_tokens": a.max_tokens,
            "models_served": sorted({r["model_served"] or "" for r in rows}),
            "providers": sorted({r["provider"] or "" for r in rows}),
            "temperature": "provider default (not sent)", "date_utc": datetime.now(timezone.utc).isoformat(),
            "endpoint": URL, "client": CLIENT, "n": len(rows), "calls_sequential": True, "streaming": False}
    (HERE / a.out).with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print(f"acc {sum(r['correct'] for r in rows)}/{len(rows)}  run cost ${sum(r['cost'] or 0 for r in rows):.5f}  "
          f"total spent ${spent():.5f}")


if __name__ == "__main__":
    main()

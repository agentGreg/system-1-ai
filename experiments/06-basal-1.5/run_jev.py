"""Raw Jev (typesafe/jev-1.13) via OpenRouter's alpha System One endpoint on the rule-change items, both option orders.

Protocol of ../04-multi-domain/run_jev.py (noul only here): POST https://openrouter.ai/api/alpha/decisions with
{"model", "state", "questions": {"q": {"type": "noul", "instructions": question, "criteria": {"true": yes-text,
"false": no-text}}}}; order 2 sends the criteria in reversed insertion order. Two-order prediction = argmax of the
averaged [P(yes), 1-P(yes)]; single-order = order 1. Sequential calls, client in Poland, wall-clock latency.
The API key is read from the macOS keychain (never printed or stored); spend is capped at common.BUDGET_USD.

usage: python run_jev.py --set rc_orig --out raw_jev-1.13_rc_orig.jsonl
"""
import argparse
import json
from datetime import datetime, timezone

from common import (CLIENT, HERE, BudgetExceeded, api_key, check_budget, hardware, load_set, log_cost, post, spent,
                    write_jsonl)

URL = "https://openrouter.ai/api/alpha/decisions"
MODEL = "typesafe/jev-1.13"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    key = api_key()
    items = load_set(a.set)[: a.limit] if a.limit else load_set(a.set)
    rows = []
    try:
        for it in items:
            assert it["type"] == "noul"
            per = []
            for rev in (False, True):
                check_budget(0.001)
                crit = {"true": it["options"][0], "false": it["options"][1]}
                if rev:
                    crit = {"false": it["options"][1], "true": it["options"][0]}
                body = {"model": MODEL, "state": it["state"],
                        "questions": {"q": {"type": "noul", "instructions": it["question"], "criteria": crit}}}
                data, status, lat, attempts = post(key, URL, body, timeout=60)
                usage = data.get("usage") or {}
                log_cost("jev-1.13", MODEL, it["id"], usage.get("cost"), data.get("model"), {"order": 2 if rev else 1})
                ans = (data.get("answers") or {}).get("q")
                p = ans.get("noul") if ans else None
                per.append({"order": 2 if rev else 1, "probs": [float(p), 1 - float(p)] if p is not None else None,
                            "raw_answer": ans, "latency_ms": lat, "http_status": status, "attempts": attempts,
                            "error": data.get("error"), "model_served": data.get("model"),
                            "provider": data.get("provider"), "usage": usage, "cost": usage.get("cost"),
                            "response_id": data.get("id")})
            ok = [p for p in per if p["probs"] is not None]
            avg = [sum(x) / len(ok) for x in zip(*[p["probs"] for p in ok])] if ok else None
            pred = max(range(2), key=avg.__getitem__) if avg else None
            o1 = per[0]["probs"]
            pred1 = max(range(2), key=o1.__getitem__) if o1 else None
            rows.append({"id": it["id"], "category": it["category"], "type": it["type"], "gold": it["gold"],
                         "pred": pred, "correct": pred == it["gold"], "p_pred": avg[pred] if avg else None,
                         "probs": avg, "pred_order1_only": pred1, "conf_order1": max(o1) if o1 else None,
                         "probs_per_order": [p["probs"] for p in per], "n_orders_ok": len(ok),
                         "latency_ms": per[0]["latency_ms"], "latency_ms_order2": per[1]["latency_ms"],
                         "cost": sum(p["cost"] or 0 for p in per), "calls": per})
            print(f'{it["id"]} gold={it["gold"]} pred={pred} p={avg[pred] if avg else None} '
                  f'{per[0]["latency_ms"]:.0f}ms served={per[0]["model_served"]}', flush=True)
    except BudgetExceeded as e:
        print("BUDGET STOP:", e, flush=True)
    write_jsonl(HERE / a.out, rows)
    meta = {"system": "Jev 1.13 (raw System One endpoint)", "model_requested": MODEL,
            "models_served": sorted({c["model_served"] or "" for r in rows for c in r["calls"]}),
            "endpoint": URL, "orders": 2, "set": a.set, "date_utc": datetime.now(timezone.utc).isoformat(),
            "client": CLIENT, "calls_sequential": True, "n": len(rows), "hardware_client": hardware()}
    (HERE / a.out).with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print(f"acc {sum(r['correct'] for r in rows)}/{len(rows)}  run cost ${sum(r['cost'] for r in rows):.5f}  "
          f"total spent ${spent():.5f}")


if __name__ == "__main__":
    main()

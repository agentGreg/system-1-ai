"""Raw Jev (typesafe/jev-1.13) via OpenRouter's alpha System One endpoint, both option orders.

POST https://openrouter.ai/api/alpha/decisions with {"model", "state", "questions": {"q": {...}}}.
  noul   -> {"type": "noul", "instructions": question, "criteria": {"true": yes-text, "false": no-text}}
  choice -> {"type": "choice", "instructions": question, "criteria": {slug: option text, ...}}
Order 1 sends the criteria in the canonical order, order 2 reversed (same keys, reversed insertion order). The answer
is mapped back to canonical option indices: noul -> [P(yes), 1-P(yes)], choice -> probabilities by key.
Two-order prediction = argmax of the averaged distribution (as basal does); single-order = order 1 only.
Calls are sequential, one decision per call. Latency is wall clock on the client (Poland), network included.

usage: python run_jev.py --out raw_jev-1.13.jsonl [--limit 2]
"""
import argparse
import json
from datetime import datetime, timezone

from common import (CLIENT, HERE, BudgetExceeded, check_budget, hardware, load_items, log_cost, post, spent,
                    write_jsonl, api_key)

URL = "https://openrouter.ai/api/alpha/decisions"
MODEL = "typesafe/jev-1.13"
KEYS = {"routing": ["reklamacje", "faktury_platnosci", "dostawa", "wsparcie_techniczne", "sprzedaz"],
        "irytacja": ["spokojny", "lekko_zirytowany", "bardzo_zirytowany"]}


def question(it, reverse):
    k = len(it["options"])
    idx = list(range(k))[::-1] if reverse else list(range(k))
    if it["type"] == "noul":
        keys = ["true", "false"]
    else:
        keys = KEYS[it["category"]]
    crit = {keys[i]: it["options"][i] for i in idx}
    return {"type": it["type"], "instructions": it["question"], "criteria": crit}, keys


def parse(it, ans, keys):
    """Canonical probability vector and the reported confidence (None if absent)."""
    if not ans:
        return None, None
    if it["type"] == "noul":
        p = ans.get("noul")
        if p is None:
            return None, None
        return [float(p), 1.0 - float(p)], ans.get("confidence")
    pr = ans.get("probabilities") or {}
    v = [float(pr.get(k, 0.0)) for k in keys]
    s = sum(v)
    if s <= 0:
        if ans.get("choice") in keys:
            v = [1.0 if k == ans["choice"] else 0.0 for k in keys]
        else:
            return None, None
    else:
        v = [x / s for x in v]
    return v, ans.get("confidence")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    key = api_key()
    items = load_items()[: a.limit] if a.limit else load_items()
    rows = []
    try:
        for it in items:
            per = []
            for rev in (False, True):
                check_budget(0.001)
                q, keys = question(it, rev)
                body = {"model": MODEL, "state": it["state"], "questions": {"q": q}}
                data, status, lat, attempts = post(key, URL, body, timeout=60)
                usage = data.get("usage") or {}
                log_cost("jev-1.13", MODEL, it["id"], usage.get("cost"), data.get("model"), {"order": 2 if rev else 1})
                ans = (data.get("answers") or {}).get("q")
                probs, conf = parse(it, ans, keys)
                per.append({"order": 2 if rev else 1, "probs": probs, "reported_confidence": conf, "raw_answer": ans,
                            "latency_ms": lat, "http_status": status, "attempts": attempts, "error": data.get("error"),
                            "model_served": data.get("model"), "provider": data.get("provider"), "usage": usage,
                            "cost": usage.get("cost"), "response_id": data.get("id")})
            o1, o2 = per
            ok = [p for p in per if p["probs"] is not None]
            if ok:
                avg = [sum(x) / len(ok) for x in zip(*[p["probs"] for p in ok])]
                pred = max(range(len(avg)), key=avg.__getitem__)
            else:
                avg, pred = None, None
            pred1 = max(range(len(o1["probs"])), key=o1["probs"].__getitem__) if o1["probs"] else None
            conf1 = o1["reported_confidence"] if o1["reported_confidence"] is not None else (
                max(o1["probs"]) if o1["probs"] else None)
            rows.append({"id": it["id"], "category": it["category"], "type": it["type"], "tricky": it["tricky"],
                         "gold": it["gold"], "pred": pred, "correct": pred == it["gold"],
                         "p_pred": avg[pred] if avg else None, "probs": avg,
                         "pred_order1_only": pred1, "correct_order1": pred1 == it["gold"],
                         "conf_order1": conf1, "probs_per_order": [p["probs"] for p in per],
                         "n_orders_ok": len(ok),
                         "latency_ms": o1["latency_ms"], "latency_ms_order2": o2["latency_ms"],
                         "cost": sum(p["cost"] or 0 for p in per), "calls": per, "output_tokens": None})
            print(f'{it["id"]} gold={it["gold"]} pred={pred} p={avg[pred] if avg else None} '
                  f'o1={pred1} {o1["latency_ms"]:.0f}/{o2["latency_ms"]:.0f}ms served={o1["model_served"]}', flush=True)
    except BudgetExceeded as e:
        print("BUDGET STOP:", e, flush=True)
    write_jsonl(HERE / a.out, rows)
    meta = {"system": "Jev 1.13 (raw System One endpoint)", "model_requested": MODEL,
            "models_served": sorted({c["model_served"] or "" for r in rows for c in r["calls"]}),
            "endpoint": URL, "orders": 2, "date_utc": datetime.now(timezone.utc).isoformat(), "client": CLIENT,
            "calls_sequential": True, "n": len(rows), "hardware_client": hardware(),
            "choice_keys": KEYS, "noul_criteria_keys": ["true", "false"]}
    (HERE / a.out).with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    n = sum(r["correct"] for r in rows)
    print(f"acc {n}/{len(rows)}  run cost ${sum(r['cost'] for r in rows):.5f}  total spent ${spent():.5f}")


if __name__ == "__main__":
    main()

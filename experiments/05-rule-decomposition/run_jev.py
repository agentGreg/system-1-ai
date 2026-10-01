"""Raw Jev (typesafe/jev-1.13) on the decomposed sub-questions via OpenRouter's alpha System One endpoint.

POST https://openrouter.ai/api/alpha/decisions with {"model", "state", "questions": {sid: q, ...}}: all sub-questions
a variant sends for one item go in ONE call (a questions dict), each
  {"type": "noul", "instructions": sub-question, "criteria": {"true": "Tak", "false": "Nie"}}.
Order 1 sends the criteria as true, false; order 2 reversed (false, true), same keys, as in experiments 03/04. Answer
noul = P(yes); the two orders are averaged per sub-question.

Per item: variant A call (all sub-questions) x 2 orders, then variant B call (read sub-questions only) x 2 orders.
Items without an arith sub-question have identical A and B requests, so the B call is skipped and A's answers and
latency are reused (marked "b_reuses_a"). Latency = client wall clock of the order-1 call (Poland, residential
connection, network included), i.e. the total for all the item's sub-questions in that variant.

usage: python run_jev.py --out raw_jev-1.13.jsonl [--limit 2]
"""
import argparse
import json
from datetime import datetime, timezone

from common import CLIENT, HERE, BudgetExceeded, api_key, check_budget, hardware, log_cost, post, spent, write_jsonl
from decomp import load, load_items, sids

URL = "https://openrouter.ai/api/alpha/decisions"
MODEL = "typesafe/jev-1.13"


def call(key, it, d, ss, rev, label):
    qs = {}
    for q in d["subquestions"]:
        if q["sid"] in ss:
            crit = {"false": "Nie", "true": "Tak"} if rev else {"true": "Tak", "false": "Nie"}
            qs[q["sid"]] = {"type": "noul", "instructions": q["text"], "criteria": crit}
    check_budget(0.002)
    body = {"model": MODEL, "state": it["state"], "questions": qs}
    data, status, lat, attempts = post(key, URL, body, timeout=90)
    usage = data.get("usage") or {}
    log_cost(label, MODEL, it["id"], usage.get("cost"), data.get("model"), {"order": 2 if rev else 1, "n_q": len(qs)})
    answers = data.get("answers") or {}
    p = {}
    for s in ss:
        a = answers.get(s) or {}
        p[s] = float(a["noul"]) if a.get("noul") is not None else None
    return {"order": 2 if rev else 1, "p_yes": p, "raw_answers": answers, "latency_ms": lat, "http_status": status,
            "attempts": attempts, "error": data.get("error"), "model_served": data.get("model"),
            "provider": data.get("provider"), "usage": usage, "cost": usage.get("cost"), "response_id": data.get("id")}


def variant(key, it, d, ss, label):
    per = [call(key, it, d, ss, rev, label) for rev in (False, True)]
    avg = {}
    for s in ss:
        v = [c["p_yes"][s] for c in per if c["p_yes"].get(s) is not None]
        avg[s] = sum(v) / len(v) if v else None
    return {"sids": ss, "p_yes": avg, "latency_ms": per[0]["latency_ms"], "latency_ms_order2": per[1]["latency_ms"],
            "cost": sum(c["cost"] or 0 for c in per), "calls": per}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    key = api_key()
    items, decs = load_items(), load()
    items = items[: a.limit] if a.limit else items
    rows = []
    try:
        for it in items:
            d = decs[it["id"]]
            A = variant(key, it, d, sids(d), "jev-1.13 A")
            reads = sids(d, "read")
            if len(reads) == len(sids(d)):
                B, reuse = A, True
            elif reads:
                B, reuse = variant(key, it, d, reads, "jev-1.13 B"), False
            else:
                B, reuse = {"sids": [], "p_yes": {}, "latency_ms": 0.0, "latency_ms_order2": 0.0, "cost": 0.0,
                            "calls": []}, False
            rows.append({"id": it["id"], "block": it["block"], "type": it["type"], "gold": it["gold"],
                         "A": A, "B": B, "b_reuses_a": reuse})
            print(it["id"], " ".join(f'{s}={v:.2f}' if v is not None else f"{s}=None" for s, v in A["p_yes"].items()),
                  f'A {A["latency_ms"]:.0f}ms B {B["latency_ms"]:.0f}ms served={A["calls"][0]["model_served"]}',
                  flush=True)
    except BudgetExceeded as e:
        print("BUDGET STOP:", e, flush=True)
    write_jsonl(HERE / a.out, rows)
    served = sorted({c["model_served"] or "" for r in rows for v in ("A", "B") for c in r[v]["calls"]})
    meta = {"system": "Jev 1.13 (raw System One endpoint)", "model_requested": MODEL, "models_served": served,
            "endpoint": URL, "orders": 2, "date_utc": datetime.now(timezone.utc).isoformat(), "client": CLIENT,
            "calls_sequential": True, "n": len(rows), "hardware_client": hardware(),
            "noul_criteria": {"true": "Tak", "false": "Nie"}, "one_call_per_item_variant_order": True}
    (HERE / a.out).with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    cost = sum(r["A"]["cost"] + (0 if r["b_reuses_a"] else r["B"]["cost"]) for r in rows)
    print(f"{len(rows)} items  run cost ${cost:.5f}  total spent ${spent():.5f}")


if __name__ == "__main__":
    main()

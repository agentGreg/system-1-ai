"""Raw Jev (TypeSafe System One model) via OpenRouter's decisions endpoint, on the same 30 decisions.

Endpoint: POST https://openrouter.ai/api/alpha/decisions, model typesafe/jev-1.13 (pinned; the returned "model" is
recorded). Request format = System One (as in basal): {"model", "state", "questions": {"q": {...}}}.

Mapping (matches how basal was asked in experiment 01, i.e. basal/run.py "simple" items):
  * noul items  -> {"type": "noul", "instructions": question, "criteria": {"true": yes-text, "false": no-text}};
                   answer "noul" = P(yes). Reversed order = the same criteria with the dict order false, true
                   (whether the server honours key order is part of what we observe).
  * choice items -> {"type": "choice", "instructions": question, "criteria": {"A": text0, ..., "E": text4}}; keys
                   are stable (attached to the option), reversed order = reversed dict order.
  * --noul-as-choice: send noul items as 2-option choice {"A": yes-text, "B": no-text} (supplementary run).
Per item: prediction, probabilities, vendor confidence, correctness, wall-clock latency, tokens, cost.
Budget guard shared with run_cloud.py via costs.jsonl. The key is read from the keychain and never printed.

usage: python run_jev.py --order original --out raw_jev-1.13_orig.jsonl
       python run_jev.py --order reversed --out raw_jev-1.13_rev.jsonl
       python run_jev.py --multi   # one multi-question call per category state, not scored
"""
import argparse
import json
import time
from datetime import datetime, timezone

from run_cloud import COSTS, HERE, api_key, load_items, spent
import urllib.error
import urllib.request

URL = "https://openrouter.ai/api/alpha/decisions"
MODEL = "typesafe/jev-1.13"
KEYS = "ABCDEFGHIJ"


def post(key, body, timeout=60):
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    t = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data, status = json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        data, status = {"error": {"http": e.code, "body": e.read().decode(errors="replace")[:2000]}}, e.code
    except Exception as e:
        data, status = {"error": {"exception": repr(e)[:500]}}, None
    return data, status, (time.perf_counter() - t) * 1000


def question(it, reversed_, noul_as_choice):
    opts = it["options"]
    if it["type"] == "noul" and not noul_as_choice:
        crit = [("true", opts[0]), ("false", opts[1])]
        keys = ["true", "false"]
        t = "noul"
    else:
        crit = [(KEYS[i], o) for i, o in enumerate(opts)]
        keys = [KEYS[i] for i in range(len(opts))]
        t = "choice"
    if reversed_:
        crit = crit[::-1]
    return {"type": t, "instructions": it["question"], "criteria": dict(crit)}, keys


def canon_probs(ans, keys):
    """Probabilities in canonical option order (index = option index in decisions.jsonl)."""
    if ans.get("type") == "noul" and not ans.get("probabilities"):
        return [ans["noul"], 1 - ans["noul"]]
    p = ans["probabilities"]
    return [p.get(k) for k in keys]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--order", choices=["original", "reversed"], default="original")
    ap.add_argument("--noul-as-choice", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--budget", type=float, default=4.5)
    ap.add_argument("--multi", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    key = api_key()
    items = load_items()[: a.limit] if a.limit else load_items()
    if a.multi:  # demo: all four question families about one state (the first item of each category)
        rows = []
        for it in [x for x in items if x["id"] in ("R03", "D07", "E01", "K03")]:
            qs = {}
            for other in [x for x in items if x["id"] in ("R01", "D01", "E01", "K01")]:
                qs[other["category"]], _ = question(other, False, False)
            data, status, lat = post(key, {"model": MODEL, "state": it["state"], "questions": qs})
            _log(a, "jev multi", it["id"], data)
            rows.append({"state_of": it["id"], "latency_ms": lat, "status": status, "response": data})
            print(it["id"], round(lat), json.dumps(data.get("answers"), ensure_ascii=False)[:300], data.get("usage"))
        (HERE / "raw_jev-1.13_multi.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
        return
    rows = []
    for it in items:
        if spent() >= a.budget:
            print("BUDGET STOP")
            break
        q, keys = question(it, a.order == "reversed", a.noul_as_choice)
        data, status, lat = post(key, {"model": MODEL, "state": it["state"], "questions": {"q": q}})
        _log(a, f"jev {a.order}{' noul-as-choice' if a.noul_as_choice else ''}", it["id"], data)
        ans = (data.get("answers") or {}).get("q")
        probs = canon_probs(ans, keys) if ans else None
        pred = max(range(len(probs)), key=probs.__getitem__) if probs else None
        usage = data.get("usage") or {}
        rows.append({"id": it["id"], "category": it["category"], "type": it["type"], "tricky": it["tricky"],
                     "gold": it["gold"], "pred": pred, "correct": pred == it["gold"], "probs": probs,
                     "p_pred": probs[pred] if probs else None, "confidence": (ans or {}).get("confidence"),
                     "answer": ans, "latency_ms": lat, "http_status": status, "error": data.get("error"),
                     "model_requested": MODEL, "model_served": data.get("model"), "provider": data.get("provider"),
                     "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
                     "cost": usage.get("cost"), "usage": usage, "request_question": q})
        print(f'{it["id"]} gold={it["gold"]} pred={pred} p={rows[-1]["p_pred"]} {lat:.0f}ms ${usage.get("cost")}',
              flush=True)
    out = HERE / a.out
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    out.with_suffix(".meta.json").write_text(json.dumps(
        {"system": "Jev raw", "model_requested": MODEL, "endpoint": URL, "order": a.order,
         "noul_as_choice": a.noul_as_choice, "date_utc": datetime.now(timezone.utc).isoformat(),
         "client_location": "Poland, residential connection", "n": len(rows)}, indent=1))
    print(f"acc {sum(r['correct'] for r in rows)}/{len(rows)}  total spent ${spent():.5f}")


def _log(a, label, id_, data):
    with COSTS.open("a") as fh:
        fh.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "label": label, "model_requested": MODEL,
                             "model_served": data.get("model"), "id": id_,
                             "cost": (data.get("usage") or {}).get("cost"), "attempts": 1}) + "\n")


if __name__ == "__main__":
    main()

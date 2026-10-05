"""Client for a local `basal-serve` (basal v1.5.0): latency of the engine's own Mac paths, SOAM and evidence spans.

Start a server first (see run_serve.sh), then:
  latency  every item of a set as one request (one question, both option orders, calibrated), sent one at a time;
           records the server's usage.latency_ms and the client wall clock (localhost HTTP), the probabilities and
           the prediction. Requests are built with basal.run.to_request (what basal-run sends for a simple item).
  soam     12 experiment-03 states x 5 (and 3) of experiment 03's questions: one request with all questions vs one
           request per question, each pattern repeated --reps times (median); answers compared
  evidence the rule-change items (original and changed rule), rule moved into the state (evidence spans point only
           into the state), "evidence": true; overlap of the returned spans with the rule clause that was changed

usage: <basal-env>/bin/python run_serve.py latency --set e03 --out raw_serve_mlx_basal-1.5-4.5B_e03.jsonl --label ...
       <basal-env>/bin/python run_serve.py soam --out raw_soam_mlx_basal-1.5-4.5B.json --label ...
       <basal-env>/bin/python run_serve.py evidence --out raw_evidence_basal-1.5-4.5B.jsonl --label ...
"""
import argparse
import json
import os
import statistics as st
import time

import httpx
from basal.run import to_request

from common import HERE, hardware, load_set, read_jsonl, split_rule, write_jsonl

URL = f"http://127.0.0.1:{os.environ.get('PORT', '8000')}/v1/systemone"
SOAM_IDS = ["R05", "R14", "R22", "D03", "D12", "D25", "E04", "E15", "E30", "S02", "S09", "S16"]
SOAM_Q = ["reklamacja", "routing", "eskalacja", "irytacja", "phishing"]


def post(cli, body):
    t = time.perf_counter()
    r = cli.post(URL, json=body)
    wall = (time.perf_counter() - t) * 1000
    return r.json(), r.status_code, wall


def canon_probs(it, ans):
    keys = ["true", "false"] if ans["type"] == "noul" else [str(k) for k in range(len(it["options"]))]
    return [ans["probabilities"][k] for k in keys]


def latency(cli, a, info):
    items = load_set(a.set)
    for it in items[:3]:  # warm-up (not timed)
        post(cli, to_request(it))
    rows = []
    for it in items:
        resp, status, wall = post(cli, to_request(it))
        ans = resp["answers"]["q"]
        probs = canon_probs(it, ans)
        pred = max(range(len(probs)), key=probs.__getitem__)
        rows.append({"id": it["id"], "category": it["category"], "type": it["type"], "gold": it["gold"],
                     "pred": pred, "correct": pred == it["gold"], "p_pred": probs[pred], "probs": probs,
                     "latency_ms": wall, "server_latency_ms": resp["usage"]["latency_ms"],
                     "input_tokens": resp["usage"]["input_tokens"], "http_status": status})
        print(f'{it["id"]} gold={it["gold"]} pred={pred} p={probs[pred]:.3f} {wall:.0f}ms', flush=True)
    return rows


def soam_body(state, qs):
    return {"state": state, "questions": {c: to_request({**q, "state": state})["questions"]["q"] for c, q in qs.items()}}


def soam(cli, a, info):
    e03 = {it["id"]: it for it in load_set("e03")}
    tmpl = {}
    for it in e03.values():
        tmpl.setdefault(it["category"], it)
    out = {"states": SOAM_IDS, "reps": a.reps, "patterns": {}}
    for nq in (5, 3):
        cats = SOAM_Q[:nq]
        qs = {c: {"type": tmpl[c]["type"], "question": tmpl[c]["question"], "options": tmpl[c]["options"]}
              for c in cats}
        for sid in SOAM_IDS[:2]:  # warm-up
            post(cli, soam_body(e03[sid]["state"], qs))
        per_state = []
        for sid in SOAM_IDS:
            state = e03[sid]["state"]
            one_wall, one_srv, sep_wall, sep_srv = [], [], [], []
            for _ in range(a.reps):
                resp, _, wall = post(cli, soam_body(state, qs))
                one_wall.append(wall)
                one_srv.append(resp["usage"]["latency_ms"])
                one = {c: canon_probs(qs[c], resp["answers"][c]) for c in cats}
                w_tot, s_tot, sep = 0.0, 0.0, {}
                for c in cats:
                    r2, _, w2 = post(cli, soam_body(state, {c: qs[c]}))
                    w_tot += w2
                    s_tot += r2["usage"]["latency_ms"]
                    sep[c] = canon_probs(qs[c], r2["answers"][c])
                sep_wall.append(w_tot)
                sep_srv.append(s_tot)
            diff = max(abs(x - y) for c in cats for x, y in zip(one[c], sep[c]))
            same = all(max(range(len(one[c])), key=one[c].__getitem__) == max(range(len(sep[c])), key=sep[c].__getitem__)
                       for c in cats)
            per_state.append({"id": sid, "one_request_wall_ms": st.median(one_wall),
                              "one_request_server_ms": st.median(one_srv),
                              "separate_requests_wall_ms": st.median(sep_wall),
                              "separate_requests_server_ms": st.median(sep_srv),
                              "max_abs_prob_diff": diff, "same_answers": same, "answers_one_request": one,
                              "answers_separate": sep})
            print(f"{nq}q {sid}: one {st.median(one_wall):.0f} ms vs separate {st.median(sep_wall):.0f} ms, "
                  f"max diff {diff:.2e}, same={same}", flush=True)
        out["patterns"][f"{nq}q"] = {"questions": cats, "per_state": per_state}
    return out


def evidence(cli, a, info):
    rows = []
    for v in ("orig", "changed"):
        items = load_set(f"rc_{v}")
        for it in items:
            head, rule = split_rule(it["question"])
            state = it["state"] + "\n\n" + rule if rule else it["state"]
            body = to_request({**it, "state": state, "question": head})
            body["questions"]["q"]["evidence"] = True
            resp, status, wall = post(cli, body)
            if "answers" not in resp:
                rows.append({"id": it["id"], "error": resp, "http_status": status})
                print(it["id"], "ERROR", resp, flush=True)
                continue
            ans = resp["answers"]["q"]
            probs = canon_probs(it, ans)
            pred = max(range(len(probs)), key=probs.__getitem__)
            cs = state.find(it["clause"])
            ce = cs + len(it["clause"]) if cs >= 0 else -1
            ev = ans.get("evidence") or []
            ov = [max(0, min(e["end"], ce) - max(e["start"], cs)) if cs >= 0 else 0 for e in ev]
            rows.append({"id": it["id"], "base_id": it["base_id"], "version": v, "gold": it["gold"], "pred": pred,
                         "correct": pred == it["gold"], "p_pred": probs[pred], "probs": probs,
                         "clause": it["clause"], "clause_span": [cs, ce], "evidence": ev,
                         "rule_paragraph_start": len(it["state"]) + 2 if rule else None,
                         "evidence_overlap_chars": ov,
                         "top_span_overlaps_clause": bool(ov and ov[0] > 0),
                         "any_span_overlaps_clause": any(o > 0 for o in ov),
                         "latency_ms": wall, "server_latency_ms": resp["usage"]["latency_ms"]})
            print(f'{it["id"]} gold={it["gold"]} pred={pred} p={probs[pred]:.3f} top_overlap={bool(ov and ov[0] > 0)}',
                  flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["latency", "soam", "evidence"])
    ap.add_argument("--set", default="e03")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--label", required=True, help="e.g. 'basal-1.5-4.5B MLX-8bit (basal-serve --mode mlx)'")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    with httpx.Client(timeout=300) as cli:
        info = cli.get(URL.replace("/systemone", "/models")).json()
        res = {"latency": latency, "soam": soam, "evidence": evidence}[a.what](cli, a, info)
    meta = {"label": a.label, "what": a.what, "set": a.set, "server_models": info, "url": "localhost",
            "hardware": hardware()}
    if isinstance(res, list):
        write_jsonl(HERE / a.out, res)
        (HERE / a.out).with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
        ok = [r for r in res if "correct" in r]
        print(f"n {len(res)} acc {sum(r['correct'] for r in ok) / max(len(ok), 1):.3f} "
              f"median {st.median(r['latency_ms'] for r in ok):.0f} ms")
    else:
        res["meta"] = meta
        (HERE / a.out).write_text(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

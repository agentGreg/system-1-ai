"""Validate decompositions.jsonl; with --truth, check that true sub-answers reproduce the gold labels.

Structure check (always): every item of items.jsonl has exactly one decomposition, sids unique, kinds valid, arith
sub-questions have a calc, combiner and calc expressions evaluate for every assignment of sub-answers and the combiner
returns a valid option index.

--truth truth_check.jsonl: rows {"id", "answers": {sid: true/false}} with the TRUE answer to every sub-question,
written by a separate checker blind to the gold labels. Reports items where
  (A) combiner(true answers) != gold                          -> the decomposition itself is wrong
  (B) calc(values, true read answers) != true arith answer    -> the variant-B arithmetic or a transcribed value is wrong
  (B) combiner(true reads + calc) != gold

usage: python check_decomp.py [--truth truth_check.jsonl] [--only ID,ID]
"""
import argparse
import itertools
import json
import sys

from decomp import HERE, arith_answers, load, load_items, outcome, sids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=str(HERE / "decompositions.jsonl"))
    ap.add_argument("--truth")
    ap.add_argument("--only")
    a = ap.parse_args()
    items = load_items()
    if a.only:
        items = [it for it in items if it["id"] in a.only.split(",")]
    decs = load(a.file)
    errs = 0
    for it in items:
        d = decs.get(it["id"])
        if d is None:
            print(it["id"], "MISSING"); errs += 1; continue
        qs = d["subquestions"]
        ss = [q["sid"] for q in qs]
        if len(set(ss)) != len(ss) or not ss:
            print(it["id"], "bad sids", ss); errs += 1; continue
        for q in qs:
            if q["kind"] not in ("read", "arith") or (q["kind"] == "arith" and not q.get("calc")):
                print(it["id"], q["sid"], "bad kind/calc"); errs += 1
        k = len(it["options"])
        try:
            for bits in itertools.product((True, False), repeat=len(ss)):
                o = outcome(d, dict(zip(ss, bits)))
                assert 0 <= o < k, f"outcome {o} out of range"
            rs = sids(d, "read")
            for bits in itertools.product((True, False), repeat=len(rs)):
                ans = dict(zip(rs, bits))
                o = outcome(d, {**ans, **arith_answers(d, ans)})
                assert 0 <= o < k, f"B outcome {o} out of range"
        except Exception as e:
            print(it["id"], "EVAL ERROR", repr(e)); errs += 1
    print(f"structure: {len(items)} items, {errs} problems")
    if not a.truth:
        sys.exit(1 if errs else 0)

    truth = {r["id"]: r["answers"] for r in (json.loads(l) for l in open(a.truth) if l.strip())}
    bad_a, bad_b = [], []
    for it in items:
        d, t = decs.get(it["id"]), truth.get(it["id"])
        if d is None:
            continue
        if t is None or set(t) != set(sids(d)):
            print(it["id"], "truth missing or sids differ", None if t is None else sorted(t)); bad_a.append(it["id"])
            continue
        oa = outcome(d, t)
        if oa != it["gold"]:
            bad_a.append(it["id"]); print(f"{it['id']} A: combiner(true answers)={oa} gold={it['gold']}")
        reads = {s: t[s] for s in sids(d, "read")}
        try:
            ar = arith_answers(d, reads)
        except Exception as e:
            bad_b.append(it["id"]); print(it["id"], "B calc error", repr(e)); continue
        diff = [s for s in ar if ar[s] != t[s]]
        ob = outcome(d, {**reads, **ar})
        if diff or ob != it["gold"]:
            bad_b.append(it["id"])
            print(f"{it['id']} B: calc differs from truth on {diff}; combiner={ob} gold={it['gold']}")
    print(f"truth check: A wrong {len(bad_a)} {bad_a}; B wrong {len(bad_b)} {bad_b}")


if __name__ == "__main__":
    main()

"""Experiment 05 analysis: compound baseline (reused from experiments 03/04) vs decomposition variant A (all
sub-questions to the model) vs variant B (read sub-questions to the model, arithmetic in Python), per block.

Reads items.jsonl, decompositions.jsonl, truth_check.jsonl (true sub-answers from the blind checker, used only to
say which sub-question a wrong item failed on), raw_*.jsonl of this experiment and the baseline raw outputs of
experiments 03/04. Writes results.csv (one row per system, condition and item) and prints the markdown tables used in
results.md.

usage: python analyze.py
"""
import csv
import json
import math
import statistics
from pathlib import Path

from decomp import HERE, arith_answers, decide, load, load_items, sids

E03, E04 = HERE.parent / "03-extended-set", HERE.parent / "04-multi-domain"
THR = 0.9133519967189886  # basal CALIBRATION.json v1.0.1, target 1% error
BLOCKS = [("exp04_rules", "exp 04 rules (60)"), ("exp03_completeness", "exp 03 completeness (39)"),
          ("all", "both blocks (99)")]
SYSTEMS = [("basal-4.5B", "raw_basal-4.5B.jsonl", "basal"), ("basal-1.5B", "raw_basal-1.5B.jsonl", "basal"),
           ("Jev 1.13", "raw_jev-1.13.jsonl", "jev")]
GEMINI = "raw_gemini-3.8-flash_medium.jsonl"


def rows(p):
    p = Path(p)
    return {r["id"]: r for r in (json.loads(l) for l in p.read_text().splitlines() if l.strip())} if p.exists() else {}


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def acc(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {100*k/n:.1f}% [{100*lo:.0f}-{100*hi:.0f}]" if n else "n/a"


def med(v):
    v = [x for x in v if x is not None]
    return f"{statistics.median(v):.0f}" if v else "n/a"


def main():
    items = load_items()
    byid = {it["id"]: it for it in items}
    decs = load()
    truth = {r["id"]: r["answers"] for r in rows(HERE / "truth_check.jsonl").values()}
    blk = {b: [it["id"] for it in items if b == "all" or it["block"] == b] for b, _ in BLOCKS}

    def base(fname):
        out = {}
        for e, b in ((E04, "exp04_rules"), (E03, "exp03_completeness")):
            r = rows(e / fname)
            for i in blk[b]:
                if i in r:
                    x = r[i]
                    out[i] = {"pred": x["pred"], "correct": x["pred"] == byid[i]["gold"], "conf": x.get("p_pred"),
                              "latency_ms": x.get("latency_ms")}
        return out

    res = {}  # (system, condition) -> {id: row}
    sub_stats = {}
    for name, fname, kind in SYSTEMS:
        res[(name, "compound")] = base(fname)
        raw = rows(HERE / fname)
        if not raw:
            continue
        for var in ("A", "B"):
            out = {}
            for i, r in raw.items():
                d = decs[i]
                if kind == "basal":
                    p = {s["sid"]: s["p_yes"] for s in r["subanswers"]}
                    lat = {s["sid"]: s["latency_ms"] for s in r["subanswers"]}
                    asked = sids(d) if var == "A" else sids(d, "read")
                    latency = sum(lat[s] for s in asked)
                    p = {s: p[s] for s in asked}
                else:
                    v = r[var]
                    p, latency = v["p_yes"], v["latency_ms"]
                if any(x is None for x in p.values()):
                    out[i] = {"pred": None, "correct": False, "conf": None, "latency_ms": latency, "failed": []}
                    continue
                pred, conf, _ = decide(d, p, var)
                failed = []
                t = truth.get(i)
                if t:
                    ans = {s: p[s] >= 0.5 for s in p}
                    if var == "B":
                        ans = {**ans, **arith_answers(d, ans)}
                    failed = [s for s in sids(d) if s in ans and ans[s] != t[s] and (var == "A" or s in p)]
                out[i] = {"pred": pred, "correct": pred == byid[i]["gold"], "conf": conf, "latency_ms": latency,
                          "failed": failed}
            res[(name, var)] = out
        # sub-question accuracy against the checker's true answers (variant A asks every sub-question)
        if truth:
            st = {"read": [0, 0], "arith": [0, 0]}
            for i, r in raw.items():
                p = ({s["sid"]: s["p_yes"] for s in r["subanswers"]} if kind == "basal" else r["A"]["p_yes"])
                for q in decs[i]["subquestions"]:
                    if p.get(q["sid"]) is None or i not in truth:
                        continue
                    st[q["kind"]][1] += 1
                    st[q["kind"]][0] += (p[q["sid"]] >= 0.5) == truth[i][q["sid"]]
            sub_stats[name] = st
    res[("Gemini 3.8 Flash (medium)", "compound")] = base(GEMINI)

    # ---------------- decomposition stats ----------------
    print("## Decomposition stats\n")
    print("| block | items | sub-questions per item (min / mean / max) | total sub-questions | read | arith | "
          "items with >= 1 arith |\n|---|---|---|---|---|---|---|")
    for b, label in BLOCKS:
        n = [len(decs[i]["subquestions"]) for i in blk[b]]
        na = [len(sids(decs[i], "arith")) for i in blk[b]]
        print(f"| {label} | {len(n)} | {min(n)} / {statistics.mean(n):.2f} / {max(n)} | {sum(n)} | "
              f"{sum(n)-sum(na)} | {sum(na)} | {sum(x > 0 for x in na)} |")

    # ---------------- accuracy ----------------
    print("\n## Accuracy (95% Wilson intervals)\n")
    print("| system | condition | " + " | ".join(l for _, l in BLOCKS) + " |\n|---|---|" + "---|" * len(BLOCKS))
    for (name, cond), out in res.items():
        if not out:
            continue
        cells = []
        for b, _ in BLOCKS:
            ids = [i for i in blk[b] if i in out]
            cells.append(acc(sum(out[i]["correct"] for i in ids), len(ids)) if ids else "n/a")
        label = {"compound": "compound question (baseline, exp 03/04 run)", "A": "A: pure decomposition",
                 "B": "B: decomposition + Python arithmetic"}[cond]
        print(f"| {name} | {label} | " + " | ".join(cells) + " |")

    # ---------------- latency ----------------
    print("\n## Latency per item, median ms (basal: sum of sequential forwards on the Mac; Jev: wall clock of the "
          "order-1 call from Poland, all sub-questions in one call)\n")
    print("| system | condition | " + " | ".join(l for _, l in BLOCKS) + " |\n|---|---|" + "---|" * len(BLOCKS))
    for (name, cond), out in res.items():
        if not out or name.startswith("Gemini"):
            continue
        print(f"| {name} | {cond} | " + " | ".join(med([out[i]["latency_ms"] for i in blk[b] if i in out])
                                                for b, _ in BLOCKS) + " |")
    g = res[("Gemini 3.8 Flash (medium)", "compound")]
    print(f"| Gemini 3.8 Flash (medium) | compound | " + " | ".join(
        med([g[i]["latency_ms"] for i in blk[b] if i in g]) for b, _ in BLOCKS) + " |")

    # ---------------- coverage ----------------
    print(f"\n## Coverage at confidence >= 0.913 (both blocks, 99 items)\n")
    print("Baseline confidence = top-option probability of the compound decision; decomposed confidence = probability "
          "of the predicted outcome under independent sub-answers (exact enumeration; for a pure AND rule with a "
          "'yes' outcome this is the product of the sub-answer probabilities).\n")
    print("| system | condition | accepted | errors among accepted | wrong items accepted |\n|---|---|---|---|---|")
    for (name, cond), out in res.items():
        if not out or name.startswith("Gemini"):
            continue
        acc_ids = [i for i in blk["all"] if i in out and out[i]["conf"] is not None and out[i]["conf"] >= THR]
        errs = [i for i in acc_ids if not out[i]["correct"]]
        print(f"| {name} | {cond} | {len(acc_ids)}/{len(out)} | {len(errs)} | {', '.join(errs) or '-'} |")

    # ---------------- sub-question accuracy ----------------
    if sub_stats:
        print("\n## Sub-question accuracy against the checker's true answers (all sub-questions, as in variant A)\n")
        print("| system | read | arith |\n|---|---|---|")
        for name, st in sub_stats.items():
            print(f"| {name} | {acc(*st['read'])} | {acc(*st['arith'])} |")

    # ---------------- remaining errors ----------------
    print("\n## Items still wrong after decomposition\n")
    for name, _, _ in SYSTEMS:
        for var in ("A", "B"):
            out = res.get((name, var))
            if not out:
                continue
            errs = [i for i in blk["all"] if i in out and not out[i]["correct"]]
            base_ok = res[(name, "compound")]
            txt = []
            for i in errs:
                f = out[i]["failed"]
                kinds = [next(q["kind"] for q in decs[i]["subquestions"] if q["sid"] == s) for s in f]
                was = "baseline ok" if base_ok.get(i, {}).get("correct") else "baseline wrong"
                txt.append(f"{i} ({was}; wrong sub-answers: " +
                           (", ".join(f"{s}/{k}" for s, k in zip(f, kinds)) or "none, combiner") + ")")
            fixed = [i for i in blk["all"] if i in out and out[i]["correct"] and not base_ok.get(i, {}).get("correct")]
            broke = [i for i in blk["all"] if i in out and not out[i]["correct"] and base_ok.get(i, {}).get("correct")]
            print(f"- **{name} {var}**: {len(errs)} wrong; fixed vs baseline {len(fixed)}, newly wrong {len(broke)}. "
                  + "; ".join(txt))

    # ---------------- csv ----------------
    with (HERE / "results.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["system", "condition", "id", "block", "gold", "pred", "correct", "confidence", "latency_ms",
                    "wrong_subquestions"])
        for (name, cond), out in res.items():
            for i in blk["all"]:
                if i in out:
                    r = out[i]
                    w.writerow([name, cond, i, byid[i]["block"], byid[i]["gold"], r["pred"], int(r["correct"]),
                                "" if r["conf"] is None else f"{r['conf']:.4f}",
                                "" if r["latency_ms"] is None else f"{r['latency_ms']:.1f}",
                                " ".join(r.get("failed") or [])])


if __name__ == "__main__":
    main()

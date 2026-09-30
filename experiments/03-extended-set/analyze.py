"""Experiment 03 analysis: annotation agreement, clean set, per-system accuracy with Wilson CIs, latency, cost,
coverage at basal's frozen confidence thresholds, calibration (reliability bins, ECE), original-30 continuity.

Writes results.csv (one row per system and item) and disputed.md; prints markdown tables used in results.md.
usage: python analyze.py
"""
import csv
import json
import math
import statistics as st
from collections import Counter

from common import CATS, HERE, load_items, read_jsonl

LET = "ABCDEFGHIJ"
ANN = [("Claude Opus 5.5", "ann_opus-5.5.jsonl"), ("GPT-6.1 Sol", "ann_gpt-6.1-sol.jsonl")]
THR = [("0.913", 0.9133519967189886), ("0.744", 0.7439389485170212)]  # basal CALIBRATION.json v1.0.1


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def fmt_acc(k, n):
    if n == 0:
        return "n/a"
    lo, hi = wilson(k, n)
    return f"{100*k/n:.1f}% ({k}/{n}) [{100*lo:.0f}-{100*hi:.0f}]"


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def pct(xs, q):
    xs = sorted(xs)
    i = (len(xs) - 1) * q
    lo, hi = int(i), min(int(i) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)


def load_system(f):
    return {r["id"]: r for r in read_jsonl(HERE / f)}


def main():
    items = load_items()
    byid = {it["id"]: it for it in items}
    ann = [(name, load_system(f)) for name, f in ANN]
    ids = [it["id"] for it in items]

    # ---------------- annotation agreement ----------------
    lab = {"author": [f'{byid[i]["category"]}:{byid[i]["gold"]}' for i in ids]}
    for name, rows in ann:
        lab[name] = [f'{byid[i]["category"]}:{rows[i]["pred"]}' if i in rows else f"{byid[i]['category']}:None"
                     for i in ids]
    names = ["author"] + [n for n, _ in ann]
    print("## Annotation agreement (all 200 items)\n")
    print("| pair | agreement | Cohen's kappa |\n|---|---|---|")
    for i in range(3):
        for j in range(i + 1, 3):
            a, b = lab[names[i]], lab[names[j]]
            ag = sum(x == y for x, y in zip(a, b))
            print(f"| {names[i]} vs {names[j]} | {ag}/{len(a)} ({100*ag/len(a):.1f}%) | {kappa(a, b):.3f} |")
    clean = {i for k, i in enumerate(ids) if lab["author"][k] == lab[names[1]][k] == lab[names[2]][k]}
    print(f"\n3-way agreement (clean set): {len(clean)}/{len(ids)} ({100*len(clean)/len(ids):.1f}%)")
    ann_agree_vs_author = sum(1 for k, i in enumerate(ids) if lab[names[1]][k] == lab[names[2]][k]
                              and lab[names[1]][k] != lab["author"][k])
    print(f"both annotators agree with each other but not with the author: {ann_agree_vs_author}")
    print("\n| category | n | 3-way agree | author-A1 kappa | author-A2 kappa | A1-A2 kappa |\n|---|---|---|---|---|---|")
    for c in CATS:
        ks = [k for k, i in enumerate(ids) if byid[i]["category"] == c]
        g = lambda nm: [lab[nm][k] for k in ks]
        print(f"| {c} | {len(ks)} | {sum(ids[k] in clean for k in ks)} | {kappa(g('author'), g(names[1])):.2f} | "
              f"{kappa(g('author'), g(names[2])):.2f} | {kappa(g(names[1]), g(names[2])):.2f} |")
    tr = [i for i in ids if byid[i]["tricky"]]
    print(f"\ntricky items in clean set: {sum(i in clean for i in tr)}/{len(tr)}; "
          f"non-tricky: {sum(i in clean for i in ids if not byid[i]['tricky'])}/{len(ids)-len(tr)}")
    print(f"exp01 items in clean set: {sum(i in clean for i in ids if byid[i]['subset']=='exp01')}/30")

    # disputed.md
    out = ["# Disputed items (experiment 03)\n",
           "Items where the author label and the two LLM annotators do not all agree. They are kept out of the "
           "headline numbers (the clean set) and wait for human adjudication by Greg. No author label was changed.\n",
           f"{len(ids) - len(clean)} items. Annotators: {', '.join(n for n, _ in ann)} (reasoning on, blind to the "
           "author label and to each other).\n",
           "Adjudication: fill in the `Decision` line of each item (A/B/... or `drop` if genuinely ambiguous).\n"]
    for i in ids:
        if i in clean:
            continue
        it = byid[i]
        out.append(f"\n## {i} ({it['category']}{', tricky' if it['tricky'] else ''})\n")
        out.append("```\n" + it["state"] + "\n```\n")
        out.append(f"**Question:** {it['question']}\n")
        out.append("**Options:** " + "; ".join(f"{LET[k]}. {o}" for k, o in enumerate(it["options"])) + "\n")
        out.append(f"- **Author:** {LET[it['gold']]} ({it['options'][it['gold']]})")
        for name, rows in ann:
            r = rows.get(i, {})
            p = r.get("pred")
            po = f"{LET[p]} ({it['options'][p]})" if p is not None else "(no answer)"
            out.append(f"- **{name}:** {po}. {r.get('justification', '')}")
        out.append("- **Decision:** _pending_\n")
    (HERE / "disputed.md").write_text("\n".join(out) + "\n")

    # ---------------- systems ----------------
    systems = []

    def add(name, f, kind, pred_key="pred", conf_key="p_pred", cost_key="cost", lat_key="latency_ms"):
        rows = load_system(f)
        if rows:
            systems.append(dict(name=name, rows=rows, kind=kind, pred_key=pred_key, conf_key=conf_key,
                                cost_key=cost_key, lat_key=lat_key, file=f))

    add("basal-1.0-4.5B (local, 2 orders)", "raw_basal-4.5B.jsonl", "basal")
    add("basal-1.0-1.5B (local, 2 orders)", "raw_basal-1.5B.jsonl", "basal")
    add("Jev 1.13 raw (2 orders avg)", "raw_jev-1.13.jsonl", "jev2")
    add("Jev 1.13 raw (order 1 only)", "raw_jev-1.13.jsonl", "jev1", pred_key="pred_order1_only",
        conf_key="conf_order1")
    add("Gemini 3.8 Flash (thinking medium)", "raw_gemini-3.8-flash_medium.jsonl", "llm")
    add("Mistral Medium 3.1 (no reasoning)", "raw_mistral-medium-3.1.jsonl", "llm")
    add("Qwen3-14B thinking (local MLX 4-bit)", "raw_qwen3-14b_think.jsonl", "llm")

    def pred(s, r):
        return r.get(s["pred_key"])

    def correct(s, i):
        r = s["rows"].get(i)
        return r is not None and pred(s, r) == byid[i]["gold"]

    def latency(s, r):
        if s["kind"] == "jev2":
            return r["latency_ms"] + r["latency_ms_order2"]  # two sequential calls
        return r[s["lat_key"]]

    def cost(s, r):
        if s["kind"] == "jev1":
            return r["calls"][0]["cost"] or 0.0
        return r.get("cost") or 0.0

    sets = {"clean": [i for i in ids if i in clean], "all": ids,
            "exp01": [i for i in ids if byid[i]["subset"] == "exp01"],
            "exp01_clean": [i for i in ids if byid[i]["subset"] == "exp01" and i in clean]}

    for setname in ("clean", "all"):
        S = sets[setname]
        print(f"\n## Accuracy on the {setname} set (n={len(S)}), Wilson 95% CI\n")
        print("| system | n run | overall | " + " | ".join(CATS) + " | tricky | median ms | p90 ms | $ / 1,000 |")
        print("|---" * (len(CATS) + 7) + "|")
        for s in systems:
            run = [i for i in S if i in s["rows"]]
            k = sum(correct(s, i) for i in run)
            cells = []
            for c in CATS:
                cs = [i for i in run if byid[i]["category"] == c]
                kc = sum(correct(s, i) for i in cs)
                lo, hi = wilson(kc, len(cs)) if cs else (float("nan"),) * 2
                cells.append(f"{kc}/{len(cs)} [{100*lo:.0f}-{100*hi:.0f}]" if cs else "n/a")
            trs = [i for i in run if byid[i]["tricky"]]
            lat = [latency(s, s["rows"][i]) for i in run]
            cst = [cost(s, s["rows"][i]) for i in run]
            dollars = f"{1000*st.mean(cst):.3f}" if s["kind"] not in ("basal",) and "Qwen" not in s["name"] else "0 (local)"
            print(f"| {s['name']} | {len(run)} | {fmt_acc(k, len(run))} | " + " | ".join(cells) +
                  f" | {sum(correct(s, i) for i in trs)}/{len(trs)} | {st.median(lat):.0f} | {pct(lat, .9):.0f} | {dollars} |")

    print("\n## Original 30 items of experiment 01 (author labels = exp 01 gold)\n")
    print("| system | all 30 | clean subset of the 30 |\n|---|---|---|")
    for s in systems:
        a30 = sets["exp01"]
        c30 = sets["exp01_clean"]
        print(f"| {s['name']} | {sum(correct(s, i) for i in a30)}/{len(a30)} | "
              f"{sum(correct(s, i) for i in c30)}/{len(c30)} |")

    # annotators as "systems" vs author on all items (for reference only)
    print("\n## Annotators scored against the author label (all 200)\n")
    for name, rows in ann:
        k = sum(rows[i]["pred"] == byid[i]["gold"] for i in ids if i in rows)
        print(f"- {name}: {fmt_acc(k, len(ids))}; cost ${sum(r['cost'] or 0 for r in rows.values()):.3f}; "
              f"median reasoning tokens {st.median(r['reasoning_tokens'] or 0 for r in rows.values()):.0f}, "
              f"items with >0 reasoning tokens {sum((r['reasoning_tokens'] or 0) > 0 for r in rows.values())}")

    # ---------------- coverage at threshold ----------------
    print("\n## Coverage at basal's frozen thresholds (clean set)\n")
    print("| system | threshold | decided alone | share | wrong among decided | error rate [95% CI] | "
          "to a human | errors caught |\n|---|---|---|---|---|---|---|---|")
    for s in systems:
        if s["kind"] not in ("basal", "jev2", "jev1"):
            continue
        run = [i for i in sets["clean"] if i in s["rows"]]
        errs = [i for i in run if not correct(s, i)]
        for tname, t in THR:
            auto = [i for i in run if (s["rows"][i].get(s["conf_key"]) or 0) >= t]
            w = sum(not correct(s, i) for i in auto)
            lo, hi = wilson(w, len(auto)) if auto else (float("nan"),) * 2
            caught = sum(1 for i in errs if i not in auto)
            print(f"| {s['name']} | {tname} | {len(auto)}/{len(run)} | {100*len(auto)/len(run):.1f}% | {w} | "
                  f"{100*w/max(len(auto),1):.1f}% [{max(0,100*lo):.1f}-{100*hi:.1f}] | {len(run)-len(auto)} | "
                  f"{caught}/{len(errs)} |")

    # ---------------- calibration ----------------
    print("\n## Calibration on the clean set: reliability bins of the top-option probability\n")
    edges = [0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0001]
    for s in systems:
        if s["kind"] not in ("basal", "jev2", "jev1"):
            continue
        run = [i for i in sets["clean"] if i in s["rows"] and s["rows"][i].get(s["conf_key"]) is not None]
        confs = [(float(s["rows"][i][s["conf_key"]]), correct(s, i)) for i in run]
        n = len(confs)
        ece = 0.0
        cells = []
        for lo, hi in zip(edges, edges[1:]):
            b = [(c, y) for c, y in confs if lo <= c < hi]
            if not b:
                cells.append(f"[{lo:.2f},{min(hi,1):.2f}): 0")
                continue
            mc = st.mean(c for c, _ in b)
            acc = st.mean(1.0 if y else 0.0 for _, y in b)
            ece += len(b) / n * abs(acc - mc)
            cells.append(f"[{lo:.2f},{min(hi,1):.2f}): n={len(b)} conf={mc:.3f} acc={acc:.3f}")
        brier = st.mean((c - (1.0 if y else 0.0)) ** 2 for c, y in confs)
        mean_conf = st.mean(c for c, _ in confs)
        acc_all = st.mean(1.0 if y else 0.0 for _, y in confs)
        print(f"**{s['name']}** n={n}: mean confidence {mean_conf:.3f}, accuracy {acc_all:.3f}, "
              f"ECE {ece:.3f}, Brier(top) {brier:.3f}")
        for c in cells:
            print("  - " + c)

    # ---------------- order sensitivity ----------------
    print("\n## Order sensitivity (all 200)\n")
    for s in systems:
        if s["kind"] not in ("basal", "jev2"):
            continue
        flips = []
        for i, r in s["rows"].items():
            pp = r["probs_per_order"]
            if any(p is None for p in pp):
                continue
            a1 = max(range(len(pp[0])), key=pp[0].__getitem__)
            a2 = max(range(len(pp[1])), key=pp[1].__getitem__)
            if a1 != a2:
                flips.append(i)
        o1 = sum(r["pred_order1_only"] == byid[i]["gold"] for i, r in s["rows"].items() if i in clean)
        print(f"- {s['name']}: orders disagree on {len(flips)} items {flips}; order-1-only accuracy on clean "
              f"{o1}/{len(clean)}")

    # ---------------- errors ----------------
    print("\n## Errors on the clean set\n")
    for s in systems:
        errs = [i for i in sets["clean"] if i in s["rows"] and not correct(s, i)]
        parts = []
        for i in errs:
            r = s["rows"][i]
            p = pred(s, r)
            c = r.get(s["conf_key"]) if s["kind"] != "llm" else None
            parts.append(f"{i}(gold {LET[byid[i]['gold']]}, pred {LET[p] if p is not None else '-'}"
                         + (f", p={c:.2f}" if c is not None else "") + ")")
        print(f"- **{s['name']}** ({len(errs)}): " + ", ".join(parts))
    err_count = Counter(i for s in systems if s["kind"] != "jev1"
                        for i in sets["clean"] if i in s["rows"] and not correct(s, i))
    print("\nclean items missed by most systems:", err_count.most_common(15))

    # ---------------- results.csv ----------------
    rows_csv = []
    for s in systems:
        for i in ids:
            r = s["rows"].get(i)
            if r is None:
                continue
            it = byid[i]
            p = pred(s, r)
            rows_csv.append({"system": s["name"], "id": i, "category": it["category"], "subset": it["subset"],
                             "tricky": it["tricky"], "clean": i in clean, "gold": it["gold"],
                             "gold_option": it["options"][it["gold"]], "pred": p,
                             "pred_option": it["options"][p] if p is not None else "",
                             "correct": p == it["gold"],
                             "confidence": round(r[s["conf_key"]], 4) if s["kind"] != "llm" and r.get(s["conf_key"]) is not None else "",
                             "latency_ms": round(latency(s, r), 1), "cost_usd": cost(s, r),
                             "output_tokens": r.get("output_tokens") if r.get("output_tokens") is not None else ""})
    for name, rows in ann:
        for i in ids:
            r = rows.get(i)
            it = byid[i]
            p = r["pred"] if r else None
            rows_csv.append({"system": f"annotator: {name}", "id": i, "category": it["category"],
                             "subset": it["subset"], "tricky": it["tricky"], "clean": i in clean,
                             "gold": it["gold"], "gold_option": it["options"][it["gold"]], "pred": p,
                             "pred_option": it["options"][p] if p is not None else "", "correct": p == it["gold"],
                             "confidence": "", "latency_ms": round(r["latency_ms"], 1) if r else "",
                             "cost_usd": r.get("cost") if r else "", "output_tokens": r.get("output_tokens") if r else ""})
    with open(HERE / "results.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows_csv[0]))
        w.writeheader()
        w.writerows(rows_csv)

    costs = read_jsonl(HERE / "costs.jsonl")
    by = Counter()
    for c in costs:
        by[c["label"]] += c.get("cost") or 0.0
    print("\n## Spend (usage.cost, all calls incl. smoke tests)\n")
    for k, v in by.most_common():
        print(f"- {k}: ${v:.4f}")
    print(f"- **total: ${sum(by.values()):.4f}**")


if __name__ == "__main__":
    main()

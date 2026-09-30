"""Experiment 04 analysis: dataset stats, annotation agreement, clean set, accuracy with Wilson CIs (overall, per
domain, per type, rule-based vs not, tricky), score MAE, latency, cost, coverage at basal's frozen confidence
thresholds, calibration (reliability bins, ECE, Brier), order sensitivity, errors.

Same computations as ../03-extended-set/analyze.py, extended with domains, the score type and the rule_based flag.
Writes results.csv (one row per system and item) and disputed.md; prints the markdown used in results.md.
usage: python analyze.py > analysis_out.txt
"""
import csv
import math
import statistics as st
from collections import Counter

from common import DOMAINS, HERE, TYPES, load_items, read_jsonl

LET = "ABCDEFGHIJ"
ANN = [("Claude Opus 5.5", "ann_opus-5.5.jsonl"), ("GPT-6.1 Sol", "ann_gpt-6.1-sol.jsonl")]
THR = [("0.913", 0.9133519967189886), ("0.744", 0.7439389485170212)]  # basal-4.5B CALIBRATION.json v1.0.1


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
    return f"{100*k/n:.1f}% ({k}/{n}) [{100*lo:.1f}-{100*hi:.1f}]"


def cell(k, n):
    if n == 0:
        return "n/a"
    lo, hi = wilson(k, n)
    return f"{k}/{n} [{100*lo:.0f}-{100*hi:.0f}]"


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
    ids = [it["id"] for it in items]
    ann = [(name, load_system(f)) for name, f in ANN]

    # ---------------- dataset ----------------
    print(f"## Dataset (n={len(items)})\n")
    print("| domain | n | noul | choice | score | rule-based | tricky | noul yes/no |\n|---|---|---|---|---|---|---|---|")
    for d in DOMAINS + ["total"]:
        ds = items if d == "total" else [it for it in items if it["domain"] == d]
        ty = Counter(it["type"] for it in ds)
        nb = Counter(it["gold"] for it in ds if it["type"] == "noul")
        print(f"| {d} | {len(ds)} | {ty['noul']} | {ty['choice']} | {ty['score']} | "
              f"{sum(it['rule_based'] for it in ds)} | {sum(it['tricky'] for it in ds)} | {nb[0]}/{nb[1]} |")
    for t in ("choice", "score"):
        g = Counter((len(it["options"]), it["gold"]) for it in items if it["type"] == t)
        print(f"\n{t} gold by (n options, gold index): {dict(sorted(g.items()))}")

    # ---------------- annotation agreement ----------------
    def lab_of(i, p):
        return f'{byid[i]["domain"]}:{byid[i]["type"]}:{p}'

    lab = {"author": [lab_of(i, byid[i]["gold"]) for i in ids]}
    for name, rows in ann:
        lab[name] = [lab_of(i, rows[i]["pred"] if i in rows else None) for i in ids]
    names = ["author"] + [n for n, _ in ann]
    print(f"\n## Annotation agreement (all {len(ids)} items)\n")
    print("| pair | agreement | Cohen's kappa |\n|---|---|---|")
    for i in range(3):
        for j in range(i + 1, 3):
            a, b = lab[names[i]], lab[names[j]]
            ag = sum(x == y for x, y in zip(a, b))
            print(f"| {names[i]} vs {names[j]} | {ag}/{len(a)} ({100*ag/len(a):.1f}%) | {kappa(a, b):.3f} |")
    clean = {i for k, i in enumerate(ids) if lab["author"][k] == lab[names[1]][k] == lab[names[2]][k]}
    print(f"\n3-way agreement (clean set): {len(clean)}/{len(ids)} ({100*len(clean)/len(ids):.1f}%)")
    both_vs_author = [i for k, i in enumerate(ids) if lab[names[1]][k] == lab[names[2]][k] != lab["author"][k]]
    print(f"both annotators agree with each other but not with the author: {len(both_vs_author)} {both_vs_author}")
    unparsed = {name: [i for i in ids if rows.get(i, {}).get("pred") is None] for name, rows in ann}
    print(f"unparsed annotator answers: {unparsed}")

    def agree_table(key, values):
        print(f"\n| {key} | n | 3-way agree | author-A1 kappa | author-A2 kappa | A1-A2 kappa |\n|---|---|---|---|---|---|")
        for v in values:
            ks = [k for k, i in enumerate(ids) if byid[i][key] == v]
            if not ks:
                continue
            g = lambda nm: [lab[nm][k] for k in ks]
            print(f"| {v} | {len(ks)} | {sum(ids[k] in clean for k in ks)} | {kappa(g('author'), g(names[1])):.2f} | "
                  f"{kappa(g('author'), g(names[2])):.2f} | {kappa(g(names[1]), g(names[2])):.2f} |")

    agree_table("domain", DOMAINS)
    agree_table("type", TYPES)
    agree_table("rule_based", [True, False])
    agree_table("tricky", [True, False])

    # disputed.md
    out = ["# Disputed items (experiment 04)\n",
           "Items where the author label and the two LLM annotators do not all agree. They are kept out of the "
           "headline numbers (the clean set) and wait for human adjudication by Greg. No author label was changed.\n",
           f"{len(ids) - len(clean)} items. Annotators: {', '.join(n for n, _ in ann)} (reasoning on, blind to the "
           "author label and to each other).\n",
           "Adjudication: fill in the `Decision` line of each item (A/B/... or `drop` if genuinely ambiguous).\n"]
    for i in ids:
        if i in clean:
            continue
        it = byid[i]
        flags = ", ".join(x for x, on in (("rule-based", it["rule_based"]), ("tricky", it["tricky"])) if on)
        out.append(f"\n## {i} ({it['domain']}, {it['type']}{', ' + flags if flags else ''})\n")
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

    def add(name, short, f, kind, pred_key="pred", conf_key="p_pred"):
        rows = load_system(f)
        if rows:
            systems.append(dict(name=name, short=short, rows=rows, kind=kind, pred_key=pred_key,
                                conf_key=conf_key, file=f))

    add("basal-1.0-4.5B (local, 2 orders)", "basal-4.5B", "raw_basal-4.5B.jsonl", "basal")
    add("basal-1.0-1.5B (local, 2 orders)", "basal-1.5B", "raw_basal-1.5B.jsonl", "basal")
    add("Jev 1.13 raw (2 orders avg)", "Jev 2-ord", "raw_jev-1.13.jsonl", "jev2")
    add("Jev 1.13 raw (order 1 only)", "Jev 1-ord", "raw_jev-1.13.jsonl", "jev1", pred_key="pred_order1_only",
        conf_key="conf_order1")
    add("Gemini 3.8 Flash (thinking medium)", "Gemini", "raw_gemini-3.8-flash_medium.jsonl", "llm")
    add("Mistral Medium 3.1 (no reasoning)", "Mistral", "raw_mistral-medium-3.1.jsonl", "llm")
    add("Qwen3-14B thinking (local MLX 4-bit)", "Qwen3-14B", "raw_qwen3-14b_think.jsonl", "local_llm")

    def pred(s, r):
        return r.get(s["pred_key"])

    def correct(s, i):
        r = s["rows"].get(i)
        return r is not None and pred(s, r) == byid[i]["gold"]

    def latency(s, r):
        if s["kind"] == "jev2":
            return r["latency_ms"] + r["latency_ms_order2"]  # two sequential calls
        return r["latency_ms"]

    def cost(s, r):
        if s["kind"] == "jev1":
            return r["calls"][0]["cost"] or 0.0
        return r.get("cost") or 0.0

    def conf(s, r):
        c = r.get(s["conf_key"])
        return float(c) if c is not None else None

    local = lambda s: s["kind"] in ("basal", "local_llm")
    C = [i for i in ids if i in clean]

    def acc_row(s, S):
        run = [i for i in S if i in s["rows"]]
        return sum(correct(s, i) for i in run), len(run)

    for setname, S in (("clean", C), ("all", ids)):
        print(f"\n## Main table, {setname} set (n={len(S)}), Wilson 95% CI\n")
        print("| system | n run | overall | noul | choice | score | rule-based | not rule-based | tricky | "
              "median ms | p90 ms | $ / 1,000 |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
        for s in systems:
            run = [i for i in S if i in s["rows"]]
            k = sum(correct(s, i) for i in run)
            sub = lambda f: cell(sum(correct(s, i) for i in run if f(byid[i])), sum(1 for i in run if f(byid[i])))
            lat = [latency(s, s["rows"][i]) for i in run]
            cst = [cost(s, s["rows"][i]) for i in run]
            dollars = "0 (local)" if local(s) else f"{1000*st.mean(cst):.3f}"
            print(f"| {s['name']} | {len(run)} | {fmt_acc(k, len(run))} | {sub(lambda x: x['type']=='noul')} | "
                  f"{sub(lambda x: x['type']=='choice')} | {sub(lambda x: x['type']=='score')} | "
                  f"{sub(lambda x: x['rule_based'])} | {sub(lambda x: not x['rule_based'])} | "
                  f"{sub(lambda x: x['tricky'])} | {st.median(lat):.0f} | {pct(lat, .9):.0f} | {dollars} |")

    print("\n## Per-domain accuracy, clean set (correct/n, Wilson 95% CI in %)\n")
    print("| domain | n clean | " + " | ".join(s["short"] for s in systems) + " |")
    print("|---" * (len(systems) + 2) + "|")
    for d in DOMAINS:
        S = [i for i in C if byid[i]["domain"] == d]
        print(f"| {d} | {len(S)} | " + " | ".join(cell(*acc_row(s, S)) for s in systems) + " |")

    print("\n## Per type x rule-based, clean set\n")
    print("| slice | n | " + " | ".join(s["short"] for s in systems) + " |")
    print("|---" * (len(systems) + 2) + "|")
    for t in TYPES:
        for rb in (True, False):
            S = [i for i in C if byid[i]["type"] == t and byid[i]["rule_based"] == rb]
            if S:
                print(f"| {t}, {'rule-based' if rb else 'not rule-based'} | {len(S)} | "
                      + " | ".join(cell(*acc_row(s, S)) for s in systems) + " |")

    print("\n## Score items, clean set: exact accuracy and mean absolute error in levels\n")
    print("| system | n | exact | MAE (argmax) | MAE (expected level) | off by >= 2 levels |\n|---|---|---|---|---|---|")
    SC = [i for i in C if byid[i]["type"] == "score"]
    for s in systems:
        run = [i for i in SC if i in s["rows"] and pred(s, s["rows"][i]) is not None]
        if not run:
            continue
        err = [abs(pred(s, s["rows"][i]) - byid[i]["gold"]) for i in run]
        k = sum(e == 0 for e in err)
        ev = ""
        if s["kind"] in ("basal", "jev2"):
            ev = f"{st.mean(abs(s['rows'][i]['expected_level'] - byid[i]['gold']) for i in run):.3f}"
        print(f"| {s['name']} | {len(run)} | {fmt_acc(k, len(run))} | {st.mean(err):.3f} | {ev or '-'} | "
              f"{sum(e >= 2 for e in err)} |")

    # annotators vs author (reference only)
    print(f"\n## Annotators scored against the author label (all {len(ids)})\n")
    for name, rows in ann:
        k = sum(rows[i]["pred"] == byid[i]["gold"] for i in ids if i in rows)
        rt = [r.get("reasoning_tokens") or 0 for r in rows.values()]
        print(f"- {name}: {fmt_acc(k, len(ids))}; cost ${sum(r['cost'] or 0 for r in rows.values()):.3f} "
              f"(${1000*sum(r['cost'] or 0 for r in rows.values())/len(rows):.2f} / 1,000); median reasoning tokens "
              f"{st.median(rt):.0f}, items with >0 reasoning tokens {sum(x > 0 for x in rt)}")

    # ---------------- coverage at threshold ----------------
    print("\n## Coverage at basal's frozen thresholds (clean set)\n")
    print("| system | threshold | decided alone | share | wrong among decided | error rate [95% CI] | "
          "to a human | errors caught |\n|---|---|---|---|---|---|---|---|")
    for s in systems:
        if s["kind"] not in ("basal", "jev2", "jev1"):
            continue
        run = [i for i in C if i in s["rows"]]
        errs = [i for i in run if not correct(s, i)]
        for tname, t in THR:
            auto = [i for i in run if (conf(s, s["rows"][i]) or 0) >= t]
            w = sum(not correct(s, i) for i in auto)
            lo, hi = wilson(w, len(auto)) if auto else (float("nan"),) * 2
            caught = sum(1 for i in errs if i not in auto)
            print(f"| {s['name']} | {tname} | {len(auto)}/{len(run)} | {100*len(auto)/len(run):.1f}% | {w} | "
                  f"{100*w/max(len(auto),1):.1f}% [{max(0,100*lo):.1f}-{100*hi:.1f}] | {len(run)-len(auto)} | "
                  f"{caught}/{len(errs)} |")
    print("\nCoverage by rule-based (strict threshold 0.913, clean set):\n")
    for s in systems:
        if s["kind"] not in ("basal", "jev2"):
            continue
        for rb in (True, False):
            run = [i for i in C if i in s["rows"] and byid[i]["rule_based"] == rb]
            auto = [i for i in run if (conf(s, s["rows"][i]) or 0) >= THR[0][1]]
            w = sum(not correct(s, i) for i in auto)
            print(f"- {s['name']}, {'rule-based' if rb else 'not rule-based'}: decided {len(auto)}/{len(run)}, "
                  f"wrong {w}")

    # ---------------- calibration ----------------
    print("\n## Calibration on the clean set: reliability bins of the top-option probability\n")
    edges = [0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0001]
    for s in systems:
        if s["kind"] not in ("basal", "jev2", "jev1"):
            continue
        run = [i for i in C if i in s["rows"] and conf(s, s["rows"][i]) is not None]
        confs = [(conf(s, s["rows"][i]), correct(s, i)) for i in run]
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
        print(f"**{s['name']}** n={n}: mean confidence {st.mean(c for c, _ in confs):.3f}, accuracy "
              f"{st.mean(1.0 if y else 0.0 for _, y in confs):.3f}, ECE {ece:.3f}, Brier(top) {brier:.3f}")
        for c in cells:
            print("  - " + c)

    # ---------------- order sensitivity ----------------
    print(f"\n## Order sensitivity (all {len(ids)})\n")
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
        both = sum(correct(s, i) for i in C if i in s["rows"])
        print(f"- {s['name']}: orders disagree on {len(flips)} items {flips}; clean accuracy order 1 only {o1}, "
              f"2-order average {both} (of {len(C)})")

    # ---------------- errors ----------------
    print("\n## Errors on the clean set\n")
    for s in systems:
        errs = [i for i in C if i in s["rows"] and not correct(s, i)]
        parts = []
        for i in errs:
            r = s["rows"][i]
            p = pred(s, r)
            c = conf(s, r) if s["kind"] in ("basal", "jev1", "jev2") else None
            parts.append(f"{i}(gold {LET[byid[i]['gold']]}, pred {LET[p] if p is not None else '-'}"
                         + (f", p={c:.2f}" if c is not None else "") + ")")
        print(f"- **{s['name']}** ({len(errs)}): " + ", ".join(parts))
    err_count = Counter(i for s in systems if s["kind"] != "jev1"
                        for i in C if i in s["rows"] and not correct(s, i))
    print("\nclean items missed by most systems:", err_count.most_common(20))

    # ---------------- run health ----------------
    print("\n## Run health\n")
    for s in systems:
        rows = s["rows"].values()
        none = sum(pred(s, r) is None for r in rows)
        extra = ""
        if s["kind"] in ("llm", "local_llm"):
            fr = Counter(r.get("finish_reason") for r in rows)
            extra = f"; finish reasons {dict(fr)}"
            if s["kind"] == "llm":
                extra += f"; served {sorted({r.get('model_served') or '' for r in rows})}"
                extra += f"; http errors {sum(1 for r in rows if r.get('error'))}"
                extra += f"; median output tokens {st.median(r.get('output_tokens') or 0 for r in rows):.0f}"
        if s["kind"] == "jev2":
            extra = (f"; served {sorted({c['model_served'] or '' for r in rows for c in r['calls']})}; "
                     f"items with a failed order {sum(r['n_orders_ok'] < 2 for r in rows)}; retried calls "
                     f"{sum(len(c['attempts']) > 1 for r in rows for c in r['calls'])}; median slower-of-two ms "
                     f"{st.median(max(r['latency_ms'], r['latency_ms_order2']) for r in rows):.0f}")
        print(f"- {s['name']}: rows {len(s['rows'])}, no prediction {none}{extra}")

    # ---------------- results.csv ----------------
    rows_csv = []
    for s in systems:
        for i in ids:
            r = s["rows"].get(i)
            if r is None:
                continue
            it = byid[i]
            p = pred(s, r)
            c = conf(s, r) if s["kind"] in ("basal", "jev1", "jev2") else None
            rows_csv.append({"system": s["name"], "id": i, "domain": it["domain"], "type": it["type"],
                             "rule_based": it["rule_based"], "tricky": it["tricky"], "clean": i in clean,
                             "gold": it["gold"], "gold_option": it["options"][it["gold"]], "pred": p,
                             "pred_option": it["options"][p] if p is not None else "", "correct": p == it["gold"],
                             "confidence": round(c, 4) if c is not None else "",
                             "latency_ms": round(latency(s, r), 1), "cost_usd": cost(s, r),
                             "output_tokens": r.get("output_tokens") if r.get("output_tokens") is not None else ""})
    for name, rows in ann:
        for i in ids:
            r = rows.get(i)
            it = byid[i]
            p = r["pred"] if r else None
            rows_csv.append({"system": f"annotator: {name}", "id": i, "domain": it["domain"], "type": it["type"],
                             "rule_based": it["rule_based"], "tricky": it["tricky"], "clean": i in clean,
                             "gold": it["gold"], "gold_option": it["options"][it["gold"]], "pred": p,
                             "pred_option": it["options"][p] if p is not None else "", "correct": p == it["gold"],
                             "confidence": "", "latency_ms": round(r["latency_ms"], 1) if r else "",
                             "cost_usd": r.get("cost") if r else "",
                             "output_tokens": r.get("output_tokens") if r else ""})
    if rows_csv:
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

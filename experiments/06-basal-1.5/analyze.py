"""Experiment 06 analysis: basal-1.5 family vs basal-1.0, Jev 1.13 and Gemini 3.8 Flash on the experiment 03/04 sets
(accuracy with Wilson CIs, per category / domain, rules, coverage at thresholds, calibration, latency on both Mac
paths), facts:auto on the 99 rule items vs experiment 05, SOAM timing, rule-change flip rates and evidence spans.

Earlier systems are read from the raw files of experiments 03/04/05 (not rerun). Prints markdown tables
(analysis_out.txt) and writes results.csv (one row per system, set, condition and item).
usage: python analyze.py > analysis_out.txt
"""
import csv
import json
import statistics as st
from collections import Counter

from basal_facts import inject
from common import E03, E04, E05, HERE, load_set, read_jsonl, variant, wilson

LET = "ABCDEFGHIJ"
THR10 = [("0.913", 0.9133519967189886), ("0.744", 0.7439389485170212)]  # basal-1.0 CALIBRATION.json (v1.0.1)
NEW = [("basal-1.5-mini", "basal-1.5-mini"), ("basal-1.5 (4.5B)", "basal-1.5-4.5B"), ("basal-1.5-max", "basal-1.5-max")]
CSV_ROWS = []


def rows_of(path):
    return {r["id"]: r for r in read_jsonl(path)}


def meta_of(path):
    p = path.with_suffix(".meta.json")
    return json.loads(p.read_text()) if p.exists() else {}


def pct(xs, q):
    xs = sorted(xs)
    i = (len(xs) - 1) * q
    lo, hi = int(i), min(int(i) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)


def acc(k, n):
    if n == 0:
        return "n/a"
    lo, hi = wilson(k, n)
    return f"{100*k/n:.1f}% ({k}/{n}) [{100*lo:.0f}-{100*hi:.0f}]"


def cell(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n} [{100*lo:.0f}-{100*hi:.0f}]"


class Sys:
    def __init__(self, name, rows, kind, pred_key="pred", conf_key="p_pred", meta=None):
        self.name, self.rows, self.kind, self.pk, self.ck, self.meta = name, rows, kind, pred_key, conf_key, meta or {}

    def pred(self, i):
        r = self.rows.get(i)
        return None if r is None else r.get(self.pk)

    def conf(self, i):
        r = self.rows.get(i)
        return None if r is None or self.kind == "llm" else r.get(self.ck)

    def lat(self, i):
        r = self.rows[i]
        if self.kind == "jev2":
            return r["latency_ms"] + r["latency_ms_order2"]
        return r["latency_ms"]

    def ok(self, i, gold):
        return self.pred(i) == gold


def main():
    sets = {"e03": {it["id"]: it for it in load_set("e03")}, "e04": {it["id"]: it for it in load_set("e04")}}
    clean03 = {r["id"] for r in csv.DictReader(open(E03 / "results.csv")) if r["clean"] == "True"}
    ids = {"e03": [i for i in sets["e03"] if i in clean03], "e04": list(sets["e04"])}
    old = {"e03": E03, "e04": E04}

    def systems(s):
        d = old[s]
        out = [Sys("basal-1.0-4.5B", rows_of(d / "raw_basal-4.5B.jsonl"), "basal", meta=meta_of(d / "raw_basal-4.5B.jsonl")),
               Sys("basal-1.0-1.5B", rows_of(d / "raw_basal-1.5B.jsonl"), "basal", meta=meta_of(d / "raw_basal-1.5B.jsonl"))]
        for name, tag in NEW:
            p = HERE / f"raw_{tag}_{s}.jsonl"
            if p.exists():
                out.append(Sys(name, rows_of(p), "basal", meta=meta_of(p)))
        out += [Sys("Jev 1.13, 2 orders", rows_of(d / "raw_jev-1.13.jsonl"), "jev2"),
                Sys("Jev 1.13, order 1", rows_of(d / "raw_jev-1.13.jsonl"), "jev1", "pred_order1_only", "conf_order1"),
                Sys("Gemini 3.8 Flash (medium)", rows_of(d / "raw_gemini-3.8-flash_medium.jsonl"), "llm")]
        return out

    SYS = {s: systems(s) for s in sets}

    def own_thr(sy):
        th = sy.meta.get("thresholds")
        if isinstance(th, dict) and "0.01" in th:
            return [("own 1%", th["0.01"]), ("own 5%", th["0.05"])]
        return []

    # ---------------- main accuracy ----------------
    print("## Accuracy (exp 03 clean n=198, exp 04 n=204, both = 402), Wilson 95% CI\n")
    print("| system | exp 03 | exp 04 | exp 04 rules (60) | exp 04 non-rule (144) | both sets |\n|---|---|---|---|---|---|")
    for k in range(len(SYS["e03"])):
        a, b = SYS["e03"][k], SYS["e04"][k]
        k3 = sum(a.ok(i, sets["e03"][i]["gold"]) for i in ids["e03"])
        k4 = sum(b.ok(i, sets["e04"][i]["gold"]) for i in ids["e04"])
        rl = [i for i in ids["e04"] if sets["e04"][i]["rule_based"]]
        nr = [i for i in ids["e04"] if not sets["e04"][i]["rule_based"]]
        kr = sum(b.ok(i, sets["e04"][i]["gold"]) for i in rl)
        kn = sum(b.ok(i, sets["e04"][i]["gold"]) for i in nr)
        print(f"| {a.name} | {acc(k3, len(ids['e03']))} | {acc(k4, len(ids['e04']))} | {cell(kr, len(rl))} | "
              f"{cell(kn, len(nr))} | {acc(k3 + k4, len(ids['e03']) + len(ids['e04']))} |")

    for s, key in (("e03", "category"), ("e04", "domain"), ("e04", "type")):
        cats = list(dict.fromkeys(sets[s][i][key] for i in ids[s]))
        print(f"\n## {s} by {key}\n")
        print("| system | " + " | ".join(cats) + " |\n|---" * 1 + "|---" * len(cats) + "|")
        for sy in SYS[s]:
            cells = []
            for c in cats:
                cs = [i for i in ids[s] if sets[s][i][key] == c]
                cells.append(f"{sum(sy.ok(i, sets[s][i]['gold']) for i in cs)}/{len(cs)}")
            print(f"| {sy.name} | " + " | ".join(cells) + " |")
    print("\n## exp 03 tricky (clean)\n")
    tr = [i for i in ids["e03"] if sets["e03"][i]["tricky"]]
    for sy in SYS["e03"]:
        print(f"- {sy.name}: {sum(sy.ok(i, sets['e03'][i]['gold']) for i in tr)}/{len(tr)}")

    # paired comparison basal-1.5 vs basal-1.0 (same items)
    print("\n## Paired: items fixed / broken vs basal-1.0-4.5B (both sets, 402)\n")
    for s_new in [n for n, _ in NEW]:
        fixed = broken = 0
        for s in sets:
            base = next(x for x in SYS[s] if x.name == "basal-1.0-4.5B")
            new = next((x for x in SYS[s] if x.name == s_new), None)
            if new is None:
                continue
            for i in ids[s]:
                g = sets[s][i]["gold"]
                fixed += (not base.ok(i, g)) and new.ok(i, g)
                broken += base.ok(i, g) and not new.ok(i, g)
        print(f"- {s_new}: fixes {fixed}, breaks {broken} (net {fixed - broken:+d})")

    # ---------------- coverage ----------------
    print("\n## Coverage at confidence thresholds (both sets pooled, 402; and per set)\n")
    print("| system | threshold | exp 03 decided / errors | exp 04 decided / errors | both: decided | errors among "
          "decided [95% CI] | wrong items accepted (both) |\n|---|---|---|---|---|---|---|")
    for k in range(len(SYS["e03"])):
        a = SYS["e03"][k]
        if a.kind == "llm":
            continue
        for tn, t in THR10 + own_thr(a):
            parts, D, W, wrong = [], 0, 0, []
            for s in ("e03", "e04"):
                sy = SYS[s][k]
                auto = [i for i in ids[s] if (sy.conf(i) or 0) >= t]
                w = [i for i in auto if not sy.ok(i, sets[s][i]["gold"])]
                parts.append(f"{len(auto)}/{len(ids[s])} / {len(w)}")
                D += len(auto)
                W += len(w)
                wrong += w
            lo, hi = wilson(W, D)
            tlabel = tn if not tn.startswith("own") else f"{tn} ({t:.3f})"
            print(f"| {a.name} | {tlabel} | {parts[0]} | {parts[1]} | {D}/402 ({100*D/402:.1f}%) | "
                  f"{W} ({100*W/max(D,1):.1f}%) [{max(0.0, 100*lo):.1f}-{100*hi:.1f}] | {', '.join(wrong) if wrong else '-'} |")

    # ---------------- calibration ----------------
    print("\n## Calibration (top-option probability; both sets pooled, 402)\n")
    edges = [0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0001]
    print("| system | mean confidence | accuracy | ECE (8 bins) | Brier (top) |\n|---|---|---|---|---|")
    bins_out = []
    for k in range(len(SYS["e03"])):
        if SYS["e03"][k].kind == "llm":
            continue
        confs = []
        for s in ("e03", "e04"):
            sy = SYS[s][k]
            confs += [(float(sy.conf(i)), sy.ok(i, sets[s][i]["gold"])) for i in ids[s] if sy.conf(i) is not None]
        n = len(confs)
        ece, cells = 0.0, []
        for lo, hi in zip(edges, edges[1:]):
            b = [(c, y) for c, y in confs if lo <= c < hi]
            if b:
                mc, ac = st.mean(c for c, _ in b), st.mean(1.0 if y else 0.0 for _, y in b)
                ece += len(b) / n * abs(ac - mc)
                cells.append(f"[{lo:.2f},{min(hi,1):.2f}): n={len(b)} conf={mc:.3f} acc={ac:.3f}")
        brier = st.mean((c - (1.0 if y else 0.0)) ** 2 for c, y in confs)
        print(f"| {SYS['e03'][k].name} | {st.mean(c for c, _ in confs):.3f} | "
              f"{st.mean(1.0 if y else 0.0 for _, y in confs):.3f} | {ece:.3f} | {brier:.3f} |")
        bins_out.append((SYS["e03"][k].name, cells))
    for name, cells in bins_out:
        print(f"\n**{name}** reliability bins:")
        for c in cells:
            print("  - " + c)

    # ---------------- latency ----------------
    print("\n## Latency per decision on the Mac (median / p90 ms; one question, both option orders, batch 1)\n")
    print("| system | path | exp 03 median | exp 03 p90 | exp 04 median | exp 04 p90 | agreement with PyTorch bf16 "
          "(both sets) | accuracy both sets |\n|---|---|---|---|---|---|---|---|")
    lat_rows = []
    for k in range(len(SYS["e03"])):
        a, b = SYS["e03"][k], SYS["e04"][k]
        if a.kind != "basal":
            continue
        l3 = [a.lat(i) for i in ids["e03"]]
        l4 = [b.lat(i) for i in ids["e04"]]
        ka = sum(a.ok(i, sets["e03"][i]["gold"]) for i in ids["e03"]) + sum(b.ok(i, sets["e04"][i]["gold"]) for i in ids["e04"])
        label = "PyTorch MPS bf16, plain forward (run_basal.py; basal-1.0 numbers from exp 03/04)"
        tag = dict(NEW).get(a.name)
        if tag:  # latency from the final latency pass (run_latency_pass.sh), predictions must be identical
            p3 = rows_of(HERE / f"lat_{tag}_e03.jsonl")
            p4 = rows_of(HERE / f"lat_{tag}_e04.jsonl")
            if p3 and p4:
                same = sum(p3[i]["pred"] == a.pred(i) and abs(p3[i]["p_pred"] - a.conf(i)) < 1e-6 for i in ids["e03"]) + \
                    sum(p4[i]["pred"] == b.pred(i) and abs(p4[i]["p_pred"] - b.conf(i)) < 1e-6 for i in ids["e04"])
                l3 = [p3[i]["latency_ms"] for i in ids["e03"]]
                l4 = [p4[i]["latency_ms"] for i in ids["e04"]]
                label += f"; latency pass rerun, identical outputs on {same}/402"
        lat_rows.append((a.name, label, l3, l4, "reference", ka))
    for name, tag in NEW:
        for mode, label in (("mlx", "basal-serve --mode mlx, -MLX-8bit port (HTTP localhost)"),
                            ("mps", "basal-serve --mode mps, bf16 (HTTP localhost)")):
            r3 = rows_of(HERE / f"raw_serve_{mode}_{tag}_e03.jsonl")
            r4 = rows_of(HERE / f"raw_serve_{mode}_{tag}_e04.jsonl")
            if not r3 or not r4:
                continue
            ref = {s: next(x for x in SYS[s] if x.name == name) for s in sets}
            agree = sum(r3[i]["pred"] == ref["e03"].pred(i) for i in ids["e03"]) + \
                sum(r4[i]["pred"] == ref["e04"].pred(i) for i in ids["e04"])
            ka = sum(r3[i]["correct"] for i in ids["e03"]) + sum(r4[i]["correct"] for i in ids["e04"])
            lat_rows.append((name, label, [r3[i]["latency_ms"] for i in ids["e03"]],
                             [r4[i]["latency_ms"] for i in ids["e04"]], f"{agree}/402", ka))
            for s, rr in (("e03", r3), ("e04", r4)):
                for i in ids[s]:
                    r = rr[i]
                    CSV_ROWS.append({"system": f"{name} [{mode}]", "set": s, "condition": f"basal-serve {mode}",
                                     "id": i, "category": sets[s][i]["category"], "gold": r["gold"],
                                     "pred": r["pred"], "correct": r["correct"], "confidence": round(r["p_pred"], 4),
                                     "latency_ms": round(r["latency_ms"], 1)})
    for name, label, l3, l4, ag, ka in lat_rows:
        print(f"| {name} | {label} | {st.median(l3):.0f} | {pct(l3, .9):.0f} | {st.median(l4):.0f} | {pct(l4, .9):.0f} | "
              f"{ag} | {acc(ka, 402)} |")
    for s in sets:
        for sy in SYS[s]:
            if sy.kind != "basal":
                continue
            print(f"\nload / meta {s} {sy.name}: revision {sy.meta.get('hf_revision', '')[:7]}, temps "
                  f"{sy.meta.get('temperatures')}, thresholds {sy.meta.get('thresholds')}, load {sy.meta.get('load_s', 0):.1f}s")

    # ---------------- errors ----------------
    print("\n## Errors (both sets)\n")
    for k in range(len(SYS["e03"])):
        parts = []
        for s in ("e03", "e04"):
            sy = SYS[s][k]
            for i in ids[s]:
                if not sy.ok(i, sets[s][i]["gold"]):
                    c = sy.conf(i)
                    parts.append(f"{i}({LET[sets[s][i]['gold']]}->{LET[sy.pred(i)] if sy.pred(i) is not None else '-'}"
                                 + (f", {c:.2f}" if c is not None else "") + ")")
        print(f"- **{SYS['e03'][k].name}** ({len(parts)}): " + ", ".join(parts))

    # csv rows for main sets
    for s in sets:
        for sy in SYS[s]:
            for i in ids[s]:
                r = sy.rows.get(i)
                if r is None:
                    continue
                c = sy.conf(i)
                CSV_ROWS.append({"system": sy.name, "set": s, "condition": "compound (exp 03/04 protocol)", "id": i,
                                 "category": sets[s][i]["category"], "gold": sets[s][i]["gold"], "pred": sy.pred(i),
                                 "correct": sy.ok(i, sets[s][i]["gold"]),
                                 "confidence": round(c, 4) if c is not None else "",
                                 "latency_ms": round(sy.lat(i), 1)})

    facts_section(sets, SYS)
    soam_section()
    rule_change_section()

    with open(HERE / "results.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["system", "set", "condition", "id", "category", "gold", "pred", "correct",
                                           "confidence", "latency_ms"])
        w.writeheader()
        w.writerows(CSV_ROWS)
    costs = read_jsonl(HERE / "costs.jsonl")
    print(f"\n## Spend\n\n- Jev calls: {len(costs)}, total usage.cost ${sum(c.get('cost') or 0 for c in costs):.5f}")


def facts_section(sets, SYS):
    items = {it["id"]: it for it in load_set("rules99")}
    blocks = [("exp04_rules", "exp 04 rules (60)"), ("exp03_completeness", "exp 03 completeness (39)")]
    print("\n## facts:auto on the 99 rule items (compound question), Wilson 95% CI\n")
    print("Conditions: compound = the exp 03/04 item as is (rule in the question); +facts = \"facts\": \"auto\" "
          "(basal.facts.inject on the state); rule in state = the 'Reguła:' text moved to the end of the state; "
          "rule in state +facts = moved, then inject (durations in the rule become visible to the facts code).\n")
    print("| system | condition | exp 04 rules (60) | exp 03 completeness (39) | both (99) | accepted at 0.913 "
          "(errors) | facts block added (items) |\n|---|---|---|---|---|---|---|")
    exp05 = list(csv.DictReader(open(E05 / "results.csv")))
    models = [("basal-1.0-4.5B", "basal-1.0-4.5B")] + NEW
    for name, tag in models:
        conds = []
        comp = {}
        for s in ("e03", "e04"):
            sy = next((x for x in SYS[s] if x.name == name), None)
            if sy:
                comp.update({i: {"pred": sy.pred(i), "p_pred": sy.conf(i), "state_modified": False}
                             for i in sy.rows if i in items})
        if comp:
            conds.append(("compound", comp))
        for cond, suf in (("+facts", "facts"), ("rule in state", "ris"), ("rule in state +facts", "ris_facts")):
            p = HERE / f"raw_{tag}_rules99_{suf}.jsonl"
            if p.exists():
                conds.append((cond, rows_of(p)))
        for cond, rows in conds:
            cells, tot = [], 0
            for b, _ in blocks:
                bi = [i for i in items if items[i]["block"] == b]
                k = sum(rows[i]["pred"] == items[i]["gold"] for i in bi if i in rows)
                tot += k
                cells.append(cell(k, len(bi)))
            auto = [i for i in items if i in rows and (rows[i]["p_pred"] or 0) >= 0.913]
            w = sum(rows[i]["pred"] != items[i]["gold"] for i in auto)
            ris = cond.startswith("rule in state")
            mod = sum(variant(items[i], True, ris, inject)[0] != variant(items[i], False, ris, inject)[0] for i in items)
            print(f"| {name} | {cond} | {cells[0]} | {cells[1]} | {acc(tot, 99)} | {len(auto)} ({w}) | "
                  f"{mod if 'facts' in cond else '-'} |")
            if cond != "compound":
                for i in items:
                    if i in rows:
                        r = rows[i]
                        CSV_ROWS.append({"system": name, "set": "rules99", "condition": cond, "id": i,
                                         "category": items[i]["block"], "gold": items[i]["gold"], "pred": r["pred"],
                                         "correct": r["pred"] == items[i]["gold"], "confidence": round(r["p_pred"], 4),
                                         "latency_ms": round(r["latency_ms"], 1)})
    print("| *experiment 05 reference* | | | | | | |")
    for sysname, label in (("basal-4.5B", "basal-1.0-4.5B"), ("basal-1.5B", "basal-1.0-1.5B"), ("Jev 1.13", "Jev 1.13"),
                           ("Gemini 3.8 Flash (medium)", "Gemini 3.8 Flash (medium)")):
        for cond in ("compound", "A", "B"):
            rr = [r for r in exp05 if r["system"] == sysname and r["condition"] == cond]
            if not rr:
                continue
            cells = []
            for b, _ in blocks:
                bb = [r for r in rr if r["block"] == b]
                cells.append(cell(sum(r["correct"] == "1" for r in bb), len(bb)))
            k = sum(r["correct"] == "1" for r in rr)
            cname = {"compound": "compound (exp 05 table)", "A": "A: split, model does arithmetic",
                     "B": "B: split + Python arithmetic"}[cond]
            print(f"| {label} | {cname} | {cells[0]} | {cells[1]} | {acc(k, len(rr))} | | |")

    # where facts helped / hurt (4.5B)
    for name, tag in NEW:
        p = HERE / f"raw_{tag}_rules99_facts.jsonl"
        sy = {s: next((x for x in SYS[s] if x.name == name), None) for s in ("e03", "e04")}
        if not p.exists() or not sy["e04"]:
            continue
        f = rows_of(p)
        fixed = [i for i in items if items[i]["block"] == "exp04_rules" and f[i]["pred"] == items[i]["gold"]
                 and sy["e04"].pred(i) != items[i]["gold"]]
        broke = [i for i in items if items[i]["block"] == "exp04_rules" and f[i]["pred"] != items[i]["gold"]
                 and sy["e04"].pred(i) == items[i]["gold"]]
        print(f"\n- {name}, +facts vs compound on exp 04 rules: fixed {fixed}, broke {broke}")


def soam_section():
    print("\n## SOAM: one request with all questions vs one request per question (basal-serve, localhost)\n")
    print("| model / path | questions | states | one request (median of per-state medians, ms) | separate requests "
          "(sum, ms) | speed-up | same argmax | max abs prob diff |\n|---|---|---|---|---|---|---|---|")
    for p in sorted(HERE.glob("raw_soam_*.json")):
        d = json.loads(p.read_text())
        for nq, pat in d["patterns"].items():
            ps = pat["per_state"]
            one = st.median(x["one_request_wall_ms"] for x in ps)
            sep = st.median(x["separate_requests_wall_ms"] for x in ps)
            same = sum(x["same_answers"] for x in ps)
            diff = max(x["max_abs_prob_diff"] for x in ps)
            print(f"| {d['meta']['label']} | {nq} | {len(ps)} | {one:.0f} | {sep:.0f} | {sep/one:.2f}x | "
                  f"{same}/{len(ps)} | {diff:.1e} |")


def rule_change_section():
    rc = read_jsonl(HERE / "rule_change_items.jsonl")
    if not rc:
        return
    print("\n## Rule change: same message, changed rule (20 items, gold written before any run)\n")
    print("| system | condition | original right | changed right | flipped correctly (both right) | answer changed "
          "| changed right among items right originally |\n|---|---|---|---|---|---|---|")
    systems = [("basal-1.0-4.5B", "basal-1.0-4.5B", "plain")] + [(n, t, "plain") for n, t in NEW] + \
        [(n, t, "ris") for n, t in NEW] + [(n, t, "risf") for n, t in NEW] + [("Jev 1.13, 2 orders", "jev-1.13", "plain"),
                                           ("Jev 1.13, order 1", "jev-1.13", "o1")]
    per_item, moves, by_block = {}, {}, []
    for name, tag, cond in systems:
        suf = {"ris": "_ris", "risf": "_ris_facts"}.get(cond, "")
        o = rows_of(HERE / f"raw_{tag}_rc_orig{suf}.jsonl")
        c = rows_of(HERE / f"raw_{tag}_rc_changed{suf}.jsonl")
        if not o or not c:
            continue
        pk = "pred_order1_only" if cond == "o1" else "pred"
        orr = {r["id"]: o[f'{r["id"]}@orig'][pk] == r["gold_orig"] for r in rc}
        chr_ = {r["id"]: c[f'{r["id"]}@changed'][pk] == r["gold_changed"] for r in rc}
        both = [i for i in orr if orr[i] and chr_[i]]
        changed = sum(o[f"{i}@orig"][pk] != c[f"{i}@changed"][pk] for i in orr)
        among = [i for i in orr if orr[i]]
        cname = {"plain": "rule in question (as in exp 03/04)", "ris": "rule moved into the state",
                 "risf": "rule moved into the state + facts:auto", "o1": "rule in question"}[cond]
        print(f"| {name} | {cname} | {sum(orr.values())}/20 | {sum(chr_.values())}/20 | {len(both)}/20 | {changed}/20 | "
              f"{sum(chr_[i] for i in among)}/{len(among)} |")
        key = name + {"ris": " [rule in state]", "risf": " [rule in state + facts]"}.get(cond, "")
        per_item[key] = {i: ("o" if orr[i] else "x") + ("o" if chr_[i] else "x") for i in orr}
        # movement of P(yes) from the original to the changed rule, signed towards the new gold
        mv = []
        for r in rc:
            pkey = (lambda x: x["probs_per_order"][0][0]) if cond == "o1" else (lambda x: x["probs"][0])
            po = pkey(o[f'{r["id"]}@orig'])
            pc = pkey(c[f'{r["id"]}@changed'])
            mv.append((pc - po) * (1 if r["gold_changed"] == 0 else -1))
        moves[key] = (st.mean(mv), st.median(abs(x) for x in mv), sum(x > 0 for x in mv))
        blk = []
        for b, bl in (("exp03_completeness", "reading rules, exp 03 completeness (8)"),
                      ("exp04_rules", "number rules, exp 04 deadlines/amounts/eligibility (12)")):
            its = [r for r in rc if r["block"] == b]
            fl = sum(orr[r["id"]] and chr_[r["id"]] for r in its)
            same = sum(o[f'{r["id"]}@orig'][pk] == c[f'{r["id"]}@changed'][pk] for r in its)
            blk.append(f"{bl}: flipped correctly {fl}/{len(its)}, same answer under both rules {same}/{len(its)}")
        by_block.append(f"- {name}, {cname}: " + "; ".join(blk))
        if cond != "o1":
            for v, rows in (("orig", o), ("changed", c)):
                for r in rc:
                    x = rows[f'{r["id"]}@{v}']
                    CSV_ROWS.append({"system": name, "set": f"rule_change_{v}", "condition": cname,
                                     "id": r["id"], "category": r["kind"], "gold": r[f"gold_{v}"], "pred": x["pred"],
                                     "correct": x["pred"] == r[f"gold_{v}"],
                                     "confidence": round(x["p_pred"], 4) if x.get("p_pred") is not None else "",
                                     "latency_ms": round(x["latency_ms"], 1)})
    print("\nBy block:\n")
    print("\n".join(by_block))
    print("\nPer item (o = right, x = wrong; first letter original rule, second changed rule):\n")
    ids_ = [r["id"] for r in rc]
    print("| item | kind | change | " + " | ".join(per_item) + " |\n|---|---|---|" + "---|" * len(per_item))
    for r in rc:
        print(f"| {r['id']} | {r['kind']} | {r['change']} | " + " | ".join(per_item[k][r['id']] for k in per_item) + " |")
    for kind in sorted({r["kind"] for r in rc}):
        ks = [r["id"] for r in rc if r["kind"] == kind]
        print(f"- {kind} ({len(ks)}): " + "; ".join(
            f"{k} {sum(per_item[k][i] == 'oo' for i in ks)}" for k in per_item))
    _ = ids_
    print("\nMovement of P(yes) from original to changed rule, signed so that positive = towards the new correct "
          "answer:\n")
    print("| system | mean signed move | median absolute move | items moved towards the new answer |\n|---|---|---|---|")
    for k, (m, med, n) in moves.items():
        print(f"| {k} | {m:+.3f} | {med:.3f} | {n}/20 |")

    for p in sorted(HERE.glob("raw_evidence_*.jsonl")):
        ev = read_jsonl(p)
        ok = [r for r in ev if "correct" in r and r["clause_span"][0] >= 0]
        print(f"\n## Evidence spans ({p.name}; rule moved into the state, \"evidence\": true)\n")
        print(f"Items whose rule has no 'Reguła:' prefix keep the rule in the question and are left out here: "
              f"{sorted({r['base_id'] for r in ev if r['clause_span'][0] < 0})}; n = {len(ok) // 2} per version.\n")
        for v in ("orig", "changed"):
            vv = [r for r in ok if r["version"] == v]
            print(f"- {v}: right {sum(r['correct'] for r in vv)}/{len(vv)}; top span overlaps the rule clause that is "
                  f"changed: {sum(r['top_span_overlaps_clause'] for r in vv)}/{len(vv)}; any of the (up to 3) spans "
                  f"overlaps: {sum(r['any_span_overlaps_clause'] for r in vv)}/{len(vv)}; no span returned: "
                  f"{sum(not r['evidence'] for r in vv)}; median latency {st.median(r['latency_ms'] for r in vv):.0f} ms")
        ch = [r for r in ok if r["version"] == "changed"]
        cr = [r for r in ch if r["correct"]]
        print(f"- changed rule, answered right: top span on the changed clause {sum(r['top_span_overlaps_clause'] for r in cr)}/{len(cr)}; "
              f"answered wrong: {sum(r['top_span_overlaps_clause'] for r in ch if not r['correct'])}/{len(ch) - len(cr)}")
        for v in ("orig", "changed"):
            where = Counter()
            for r in ok:
                if r["version"] == v and r["evidence"]:
                    top = r["evidence"][0]
                    where["rule paragraph" if top["start"] >= r["rule_paragraph_start"] else "message"] += 1
            print(f"- {v}: top span located in the rule paragraph {where['rule paragraph']}, in the message "
                  f"{where['message']}")
        blk = {r["id"]: r["block"] for r in rc}
        for b in ("exp03_completeness", "exp04_rules"):
            bb = [r for r in ch if blk[r["base_id"]] == b]
            print(f"- changed rule, {b}: top span overlaps the changed clause {sum(r['top_span_overlaps_clause'] for r in bb)}"
                  f"/{len(bb)}; median top-span length {st.median(len(r['evidence'][0]['text']) for r in bb):.0f} chars, "
                  f"median top-span probability {st.median(r['evidence'][0]['probability'] for r in bb):.2f}")
        print("- examples (changed rule): " + " || ".join(
            f"{r['base_id']}: \"{r['evidence'][0]['text'][:90]}\"" for r in ch[:6] if r["evidence"]))


if __name__ == "__main__":
    main()

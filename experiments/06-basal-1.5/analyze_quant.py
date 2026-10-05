"""Analysis of QUANT_PLAN.md v2: MLX ports of basal-1.5-mini vs the PyTorch bf16 reference.

Reads the raw readouts written by run_quant.sh and prints quant_results tables (markdown) to stdout.
  floors        dtype floor (torch-fp32 vs torch-bf16), engine floor (mlx-bf16 vs torch-bf16)
  per port      agreement, flips with the reference margin, discordant split, accuracy (Wilson 95%), |dp|, score
                level shift, paired log-loss difference (bootstrap 95%), threshold coverage counts, decision rule
  categories    flips per category, e03 + e04
  temperature   Remek's label-free paired fit: per type, the factor t on the bf16 temperature that minimises
                KL(reference || port at T_bf16 * t), with a bootstrap 95% interval; score not refit
  extras        agreement and |dp| on the label-free paired readouts (rules99 facts / rule-in-state, rule change)

usage: python analyze_quant.py > quant_results_tables.md
"""
import csv
import glob
import json
import math
import random
from pathlib import Path

from common import EXP, HERE, read_jsonl, wilson

PORTS = ["bf16", "8bit", "6bit", "fp4", "mixed-4-6", "4bit-g32", "4bit"]
MAIN = ["e03", "e04"]
EXTRAS = ["rules99_facts", "rules99_ris", "rc_orig", "rc_changed"]
MARGIN = 0.2
B = 1000
rng = random.Random(0)


def ref_path(s):
    return HERE / f"raw_basal-1.5-mini_{s}.jsonl"


def port_path(p, s):
    return HERE / f"raw_mlx-{p}_mini_{s}.jsonl"


def load(path):
    rows = read_jsonl(path)
    return {r["id"]: r for r in rows}


def clean_e03():
    rows = list(csv.DictReader(open(EXP / "03-extended-set/results.csv")))
    first = rows[0]["system"]
    return {r["id"] for r in rows if r["system"] == first and r["clean"] == "True"}


def margin(r):
    p = sorted(r["probs"], reverse=True)
    return p[0] - p[1]


def raw_avg(r):
    return [sum(x) / len(r["probs_per_order"]) for x in zip(*r["probs_per_order"])]


def scale(p, T):
    lg = [math.log(max(x, 1e-12)) / T for x in p]
    m = max(lg)
    e = [math.exp(x - m) for x in lg]
    s = sum(e)
    return [x / s for x in e]


def kl(p, q):
    return sum(a * (math.log(max(a, 1e-12)) - math.log(max(b, 1e-12))) for a, b in zip(p, q))


def compare(ref, port, ids):
    n = len(ids)
    agree = sum(ref[i]["pred"] == port[i]["pred"] for i in ids)
    flips = [i for i in ids if ref[i]["pred"] != port[i]["pred"]]
    big = [i for i in flips if margin(ref[i]) >= MARGIN]
    dps = [max(abs(a - b) for a, b in zip(ref[i]["probs"], port[i]["probs"])) for i in ids]
    return n, agree, flips, big, dps


def boot_mean(xs):
    if not xs:
        return float("nan"), float("nan"), float("nan")
    ms = sorted(sum(rng.choice(xs) for _ in xs) / len(xs) for _ in range(B))
    return sum(xs) / len(xs), ms[int(0.025 * B)], ms[int(0.975 * B)]


def fit_t(pairs):
    """pairs: (reference probs, port raw averaged probs, bf16 T). Grid search of t minimising mean KL."""
    grid = [0.5 + 0.005 * k for k in range(301)]
    def loss(t, ps):
        return sum(kl(r, scale(q, T * t)) for r, q, T in ps) / len(ps)
    def best(ps):
        return min(grid, key=lambda t: loss(t, ps))
    t = best(pairs)
    bs = sorted(best([rng.choice(pairs) for _ in pairs]) for _ in range(200))
    return t, bs[5], bs[194], loss(1.0, pairs), loss(t, pairs)


def main():
    clean = clean_e03()
    ref = {s: load(ref_path(s)) for s in MAIN + EXTRAS}
    bf16_T = json.loads((HERE / "raw_basal-1.5-mini_e03.meta.json").read_text())["temperatures"]
    thr = json.loads((HERE / "raw_basal-1.5-mini_e03.meta.json").read_text())["thresholds"]
    ports = {p: {s: load(port_path(p, s)) for s in MAIN + EXTRAS if port_path(p, s).exists()} for p in PORTS}

    print("## Floors\n")
    print("| comparison | set | n | agreement | flips (ref margin >= 0.2) | mean / max abs dp |")
    print("|---|---|---|---|---|---|")
    for name, other in [("torch-fp32 vs torch-bf16", {s: load(HERE / f"raw_torch-fp32_mini_{s}.jsonl") for s in MAIN}),
                        ("mlx-bf16 vs torch-bf16", ports["bf16"])]:
        for s in MAIN:
            n, ag, fl, big, dps = compare(ref[s], other[s], list(ref[s]))
            print(f"| {name} | {s} | {n} | {ag / n:.3f} | {len(fl)} ({len(big)}) | {sum(dps) / n:.4f} / {max(dps):.3f} |")
    rep = HERE / "raw_mlx-6bit_mini_e04_repeat.jsonl"
    if rep.exists():
        a, b = ports["6bit"]["e04"], load(rep)
        print(f"\nDeterminism (mlx-6bit e04 run twice): identical probabilities on "
              f"{sum(a[i]['probs'] == b[i]['probs'] for i in a)}/{len(a)} items.")

    print("\n## Ports vs torch-bf16 (e03 + e04 pooled; e03 clean set in brackets)\n")
    print("| port | GB | agreement | flips | flips with ref margin >= 0.2 | port right / ref right | accuracy (95% CI) "
          "| ref accuracy | mean / max abs dp | log-loss diff (95% CI) | rule |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    ref_acc = sum(ref[s][i]["correct"] for s in MAIN for i in ref[s])
    N = sum(len(ref[s]) for s in MAIN)
    sizes = {}
    for p in PORTS:
        loc = Path.home() / f"models/basal-mlx/basal-1.5-mini-MLX-{p}"
        if not loc.exists():
            g = glob.glob(str(Path.home() / f".cache/huggingface/hub/models--Remek--basal-1.5-mini-MLX-{p}/snapshots/*"))
            loc = Path(g[0]) if g else None
        sizes[p] = sum(f.stat().st_size for f in loc.glob("*.safetensors")) / 1e9 if loc else float("nan")
    verdict = {}
    for p in PORTS:
        if not all(s in ports[p] for s in MAIN):
            continue
        n = agree = 0
        flips, big, dps, ll, pr, rr, acc = [], [], [], [], 0, 0, 0
        for s in MAIN:
            ids = list(ref[s])
            n_, ag, fl, bg, dp = compare(ref[s], ports[p][s], ids)
            n += n_; agree += ag; flips += [(s, i) for i in fl]; big += [(s, i) for i in bg]; dps += dp
            for i in ids:
                R, P = ref[s][i], ports[p][s][i]
                acc += P["correct"]
                ll.append(-math.log(max(P["p_gold"], 1e-12)) + math.log(max(R["p_gold"], 1e-12)))
                if R["pred"] != P["pred"]:
                    pr += P["correct"]; rr += R["correct"]
        cl = [i for i in clean]
        n_c, ag_c, fl_c, bg_c, _ = compare(ref["e03"], ports[p]["e03"], cl)
        lo, hi = wilson(acc, n)
        m, llo, lhi = boot_mean(ll)
        ok = agree / n >= 0.98 and not big
        verdict[p] = ok
        print(f"| {p} | {sizes[p]:.2f} | {agree / n:.3f} [{ag_c / n_c:.3f}] | {len(flips)} | {len(big)} | {pr} / {rr} "
              f"| {acc / n:.3f} ({lo:.3f}-{hi:.3f}) | {ref_acc / N:.3f} | {sum(dps) / n:.4f} / {max(dps):.3f} "
              f"| {m:+.4f} ({llo:+.4f}, {lhi:+.4f}) | {'equivalent' if ok else 'measurably different'} |")

    print("\n## Per set\n")
    print("| port | set | agreement | flips (ref margin >= 0.2) | accuracy | ref accuracy |")
    print("|---|---|---|---|---|---|")
    for p in PORTS:
        for s in MAIN:
            if s not in ports[p]:
                continue
            n, ag, fl, big, _ = compare(ref[s], ports[p][s], list(ref[s]))
            a = sum(r["correct"] for r in ports[p][s].values()) / n
            ra = sum(r["correct"] for r in ref[s].values()) / n
            print(f"| {p} | {s} | {ag / n:.3f} | {len(fl)} ({len(big)}) | {a:.3f} | {ra:.3f} |")

    print("\n## Flips per category (e03 + e04; flips with ref margin >= 0.2 in brackets)\n")
    cats = {}
    for s in MAIN:
        for i, r in ref[s].items():
            cats.setdefault((s, r["category"]), []).append(i)
    show = [p for p in PORTS if all(s in ports[p] for s in MAIN)]
    print("| set | category | n | ref acc | " + " | ".join(show) + " |")
    print("|---|---|---|---|" + "---|" * len(show))
    for (s, c), ids in sorted(cats.items()):
        cells = []
        for p in show:
            _, _, fl, big, _ = compare(ref[s], ports[p][s], ids)
            cells.append(f"{len(fl)} ({len(big)})" if fl else "0")
        if any(x != "0" for x in cells):
            ra = sum(ref[s][i]["correct"] for i in ids) / len(ids)
            print(f"| {s} | {c} | {len(ids)} | {ra:.2f} | " + " | ".join(cells) + " |")

    print("\n## Per type (e03 + e04)\n")
    print("| port | type | n | agreement | flips (ref margin >= 0.2) | score: mean abs shift of expected level |")
    print("|---|---|---|---|---|---|")
    for p in show:
        for t in ["noul", "choice", "score"]:
            n = ag = nf = nb = 0
            shift = []
            for s in MAIN:
                ids = [i for i, r in ref[s].items() if r["type"] == t]
                if not ids:
                    continue
                n_, a_, fl, big, _ = compare(ref[s], ports[p][s], ids)
                n += n_; ag += a_; nf += len(fl); nb += len(big)
                if t == "score":
                    shift += [abs(ports[p][s][i]["expected_level"] - ref[s][i]["expected_level"]) for i in ids]
            if n:
                sh = f"{sum(shift) / len(shift):.3f}" if shift else ""
                print(f"| {p} | {t} | {n} | {ag / n:.3f} | {nf} ({nb}) | {sh} |")

    print("\n## Temperature: label-free paired fit (t multiplies the bf16 temperature)\n")
    print("| port | type | n | t (95% CI), e03 + e04 + extras | KL at t=1 | KL at t | shipped t |")
    print("|---|---|---|---|---|---|---|")
    for p in show:
        meta = json.loads(port_path(p, "e03").with_suffix(".meta.json").read_text())
        for t in ["noul", "choice"]:
            pairs = [(ref[s][i]["probs"], raw_avg(ports[p][s][i]), bf16_T[t])
                     for s in MAIN + EXTRAS if s in ports[p] for i in ref[s]
                     if ref[s][i]["type"] == t and i in ports[p][s]]
            tt, lo, hi, k1, kt = fit_t(pairs)
            shipped = meta["temperatures"][t] / bf16_T[t]
            print(f"| {p} | {t} | {len(pairs)} | {tt:.3f} ({lo:.3f}-{hi:.3f}) | {k1:.4f} | {kt:.4f} | {shipped:.3f} |")

    print("\n## Confidence thresholds (bf16 tiers; covered items / covered errors, e03 + e04)\n")
    print("| system | tier 0.01 (conf >= %.3f) | tier 0.05 (conf >= %.3f) |" % (thr["0.01"], thr["0.05"]))
    print("|---|---|---|")
    def cov(rows):
        out = []
        for k in ["0.01", "0.05"]:
            c = [r for r in rows if r["p_pred"] >= thr[k]]
            out.append(f"{len(c)} / {sum(not r['correct'] for r in c)}")
        return out
    allref = [r for s in MAIN for r in ref[s].values()]
    print(f"| torch-bf16 (reference) | " + " | ".join(cov(allref)) + " |")
    for p in show:
        print(f"| {p} | " + " | ".join(cov([r for s in MAIN for r in ports[p][s].values()])) + " |")

    print("\n## Extras (label-free, paired with the bf16 reference)\n")
    print("| port | " + " | ".join(EXTRAS) + " |")
    print("|---|" + "---|" * len(EXTRAS))
    for p in show:
        cells = []
        for s in EXTRAS:
            if s not in ports[p]:
                cells.append("")
                continue
            ids = [i for i in ref[s] if i in ports[p][s]]
            n, ag, fl, big, dps = compare(ref[s], ports[p][s], ids)
            cells.append(f"{ag / n:.3f}, {len(fl)} ({len(big)}) flips, mean dp {sum(dps) / n:.3f}")
        print(f"| {p} | " + " | ".join(cells) + " |")

    json.dump(verdict, open(HERE / "quant_verdict.json", "w"), indent=1)


if __name__ == "__main__":
    main()

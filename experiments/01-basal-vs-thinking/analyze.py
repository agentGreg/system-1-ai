"""Aggregate raw_*.jsonl into results.csv and print summary tables (markdown) for results.md."""
import csv
import json
import statistics as st

from common import HERE, load_items

SYSTEMS = [("basal-1.0-4.5B", "raw_basal-4.5B.jsonl"), ("basal-1.0-1.5B", "raw_basal-1.5B.jsonl"),
           ("Qwen3-14B thinking ON", "raw_qwen3-14b_think.jsonl"),
           ("Qwen3-14B thinking OFF", "raw_qwen3-14b_nothink.jsonl")]
CATS = ["reklamacja", "routing", "eskalacja", "kompletnosc"]


def pct(xs, q):
    xs = sorted(xs)
    i = (len(xs) - 1) * q
    lo, hi = int(i), min(int(i) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)


def main():
    items = {it["id"]: it for it in load_items()}
    csv_rows, summary = [], []
    for name, f in SYSTEMS:
        p = HERE / f
        if not p.exists():
            continue
        rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
        meta = json.loads(p.with_suffix(".meta.json").read_text())
        lat = [r["latency_ms"] for r in rows]
        line = {"system": name, "n": len(rows), "acc": sum(r["correct"] for r in rows),
                "by_cat": {c: (sum(r["correct"] for r in rows if r["category"] == c),
                               sum(1 for r in rows if r["category"] == c)) for c in CATS},
                "tricky": (sum(r["correct"] for r in rows if r["tricky"]), sum(1 for r in rows if r["tricky"])),
                "lat_med": st.median(lat), "lat_p90": pct(lat, 0.9), "lat_total_s": sum(lat) / 1000,
                "tok_med": st.median(r["output_tokens"] for r in rows),
                "tok_max": max(r["output_tokens"] for r in rows), "load_s": meta["load_s"]}
        if "pred_order1_only" in rows[0]:
            line["acc_order1"] = sum(r["pred_order1_only"] == r["gold"] for r in rows)
            line["order_flips"] = [r["id"] for r in rows
                                   if max(range(len(r["probs"])), key=r["probs_per_order"][1].__getitem__)
                                   != r["pred_order1_only"]]
            # frozen thresholds shipped in CALIBRATION.json (target error 1% -> conf >= 0.913, 5% -> conf >= 0.744)
            for tag, thr in (("thr_0.01", 0.9133519967189886), ("thr_0.05", 0.7439389485170212)):
                acc_ = [r for r in rows if r["p_pred"] >= thr]
                line[tag] = {"auto": len(acc_), "auto_wrong": sum(not r["correct"] for r in acc_),
                             "to_human": [r["id"] for r in rows if r["p_pred"] < thr]}
        summary.append(line)
        for r in rows:
            it = items[r["id"]]
            csv_rows.append({"system": name, "id": r["id"], "category": r["category"], "tricky": r["tricky"],
                             "gold": r["gold"], "gold_option": it["options"][r["gold"]], "pred": r["pred"],
                             "pred_option": it["options"][r["pred"]] if r["pred"] is not None else "",
                             "correct": r["correct"], "p_pred": round(r.get("p_pred", float("nan")), 4),
                             "latency_ms": round(r["latency_ms"], 1), "output_tokens": r["output_tokens"],
                             "answer_text": r.get("answer_text", "")})
        errs = [r for r in rows if not r["correct"]]
        print(f"\n## {name}: errors")
        for r in errs:
            it = items[r["id"]]
            extra = f" p={r['p_pred']:.3f}" if "p_pred" in r else f" out_tok={r['output_tokens']}"
            po = it["options"][r["pred"]] if r["pred"] is not None else "(no parsable answer)"
            print(f"- {r['id']}: gold={it['options'][r['gold']]!r} pred={po!r}{extra}")
    with open(HERE / "results.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(csv_rows[0]))
        w.writeheader()
        w.writerows(csv_rows)
    print("\n| system | acc | " + " | ".join(CATS) + " | tricky | median ms | p90 ms | median out tok | load s |")
    print("|---" * (len(CATS) + 7) + "|")
    for s in summary:
        cats = " | ".join(f"{a}/{n}" for a, n in s["by_cat"].values())
        print(f"| {s['system']} | {s['acc']}/{s['n']} | {cats} | {s['tricky'][0]}/{s['tricky'][1]} | "
              f"{s['lat_med']:.0f} | {s['lat_p90']:.0f} | {s['tok_med']:.0f} | {s['load_s']:.1f} |")
    for s in summary:
        print(s["system"], {k: v for k, v in s.items()
                            if k in ("acc_order1", "order_flips", "lat_total_s", "tok_max", "thr_0.01", "thr_0.05")})


if __name__ == "__main__":
    main()

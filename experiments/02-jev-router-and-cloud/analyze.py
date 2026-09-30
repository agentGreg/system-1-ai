"""Aggregate raw_*.jsonl of experiment 02 into results.csv and print markdown tables for results.md."""
import csv
import json
import statistics as st
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP01 = HERE.parent / "01-basal-vs-thinking"
CATS = ["reklamacja", "routing", "eskalacja", "kompletnosc"]
SYSTEMS = [  # (label, raw file)
    ("Jev Router (typesafe/jev-router)", "raw_jev-router.jsonl"),
    ("GPT-6 Luna direct (default reasoning)", "raw_gpt-6-luna.jsonl"),
    ("DeepSeek V4.1 Flash direct (default reasoning)", "raw_deepseek-v4.1-flash.jsonl"),
    ("Claude Sonnet 5.5, effort medium", "raw_sonnet-5.5_medium.jsonl"),
    ("Claude Sonnet 5.5, effort minimal", "raw_sonnet-5.5_minimal.jsonl"),
    ("GPT-6.1 Sol, effort medium", "raw_gpt-6.1-sol_medium.jsonl"),
    ("GPT-6.1 Sol, effort minimal", "raw_gpt-6.1-sol_minimal.jsonl"),
    ("GPT-6.1 Sol, effort high", "raw_gpt-6.1-sol_high.jsonl"),
    ("Gemini 3.8 Flash, effort medium", "raw_gemini-3.8-flash_medium.jsonl"),
]


def pct(xs, q):
    xs = sorted(xs)
    i = (len(xs) - 1) * q
    lo, hi = int(i), min(int(i) + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)


def load(f):
    return [json.loads(l) for l in (HERE / f).read_text().splitlines() if l.strip()]


def main():
    items = {json.loads(l)["id"]: json.loads(l) for l in (EXP01 / "decisions.jsonl").read_text().splitlines() if l}
    csv_rows, summary = [], []
    for name, f in SYSTEMS:
        if not (HERE / f).exists():
            continue
        rows = load(f)
        ok = [r for r in rows if not r["error"]]
        lat = [r["latency_ms"] for r in ok]
        cost = sum(r["cost"] or 0 for r in rows)
        s = {"system": name, "file": f, "n": len(rows), "acc": sum(r["correct"] for r in rows),
             "by_cat": {c: (sum(r["correct"] for r in rows if r["category"] == c),
                            sum(1 for r in rows if r["category"] == c)) for c in CATS},
             "tricky": (sum(r["correct"] for r in rows if r["tricky"]), sum(1 for r in rows if r["tricky"])),
             "lat_med": st.median(lat), "lat_p90": pct(lat, 0.9), "lat_min": min(lat), "lat_max": max(lat),
             "out_med": st.median(r["output_tokens"] for r in ok),
             "reas_med": st.median(r["reasoning_tokens"] or 0 for r in ok),
             "reas_max": max(r["reasoning_tokens"] or 0 for r in ok),
             "in_med": st.median(r["input_tokens"] for r in ok),
             "cost": cost, "per_1k": cost / len(rows) * 1000,
             "errors": [r["id"] for r in rows if not r["correct"]],
             "api_errors": [(r["id"], r["error"]) for r in rows if r["error"]],
             "retries": [r["id"] for r in rows if len(r["attempts"]) > 1],
             "served": Counter(r["model_served"] for r in rows),
             "providers": Counter((r["model_served"], r["provider"]) for r in rows)}
        summary.append(s)
        for r in rows:
            it = items[r["id"]]
            csv_rows.append({"system": name, "id": r["id"], "category": r["category"], "tricky": r["tricky"],
                             "gold": r["gold"], "gold_option": it["options"][r["gold"]], "pred": r["pred"],
                             "pred_option": it["options"][r["pred"]] if r["pred"] is not None else "",
                             "correct": r["correct"], "model_served": r["model_served"], "provider": r["provider"],
                             "latency_ms": round(r["latency_ms"], 1), "input_tokens": r["input_tokens"],
                             "output_tokens": r["output_tokens"], "reasoning_tokens": r["reasoning_tokens"],
                             "cost_usd": r["cost"], "answer_text": r["answer_text"]})
    with open(HERE / "results.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(csv_rows[0]))
        w.writeheader()
        w.writerows(csv_rows)

    print("| system | acc | " + " | ".join(CATS) + " | tricky | median ms | p90 ms | median out tok | "
          "median reasoning tok | max reasoning tok | total $ (30) | $ / 1,000 |")
    print("|---" * (len(CATS) + 10) + "|")
    for s in summary:
        cats = " | ".join(f"{a}/{n}" for a, n in s["by_cat"].values())
        print(f"| {s['system']} | {s['acc']}/{s['n']} | {cats} | {s['tricky'][0]}/{s['tricky'][1]} | "
              f"{s['lat_med']:,.0f} | {s['lat_p90']:,.0f} | {s['out_med']:.0f} | {s['reas_med']:.0f} | "
              f"{s['reas_max']} | {s['cost']:.5f} | {s['per_1k']:.3f} |")
    print()
    for s in summary:
        print(s["system"], "errors:", s["errors"], "api_errors:", s["api_errors"], "retries:", s["retries"],
              "lat range:", round(s["lat_min"]), round(s["lat_max"]), "in_med:", s["in_med"])
        print("   served:", dict(s["served"]), "providers:", dict(s["providers"]))
    # jev-router routing detail
    jr = load("raw_jev-router.jsonl")
    print("\n## jev-router routing per category")
    for c in CATS:
        print(c, dict(Counter(r["model_served"] for r in jr if r["category"] == c)))
    for m in sorted({r["model_served"] for r in jr}):
        rs = [r for r in jr if r["model_served"] == m]
        print(m, "n", len(rs), "acc", sum(r["correct"] for r in rs), "med ms", round(st.median(r["latency_ms"] for r in rs)),
              "med reas", st.median(r["reasoning_tokens"] or 0 for r in rs),
              "with reasoning>0", [r["id"] for r in rs if (r["reasoning_tokens"] or 0) > 0],
              "gold", Counter(r["gold"] for r in rs), "cost", round(sum(r["cost"] for r in rs), 6))
    total = sum(json.loads(l).get("cost") or 0 for l in (HERE / "costs.jsonl").read_text().splitlines() if l)
    print(f"\nTotal spend incl. smoke tests (costs.jsonl): ${total:.5f}")


if __name__ == "__main__":
    main()

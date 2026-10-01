"""Collect the experiment 05 items into items.jsonl (copies, no edits).

Block "exp04_rules": the 60 rule_based items of ../04-multi-domain/decisions.jsonl (all 204 items there are in the
clean set: author and both annotators agree).
Block "exp03_completeness": the completeness-rule items (category kompletnosc, ids K01-K40) of
../03-extended-set/decisions.jsonl that are in experiment 03's clean set (author label == both annotators' labels);
K39 is disputed there and is left out.

usage: python build_items.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
E03 = HERE.parent / "03-extended-set"
E04 = HERE.parent / "04-multi-domain"


def rows(p):
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]


def main():
    out = []
    for it in rows(E04 / "decisions.jsonl"):
        if it["rule_based"]:
            out.append({**it, "block": "exp04_rules"})
    e03 = rows(E03 / "decisions.jsonl")
    ann = [{r["id"]: r["pred"] for r in rows(E03 / f)} for f in ("ann_opus-5.5.jsonl", "ann_gpt-6.1-sol.jsonl")]
    for it in e03:
        if not it["id"].startswith("K"):
            continue
        if all(a.get(it["id"]) == it["gold"] for a in ann):
            out.append({**it, "domain": "kompletnosc", "rule_based": True, "keys": ["true", "false"],
                        "block": "exp03_completeness"})
        else:
            print("not in exp 03 clean set:", it["id"])
    (HERE / "items.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))
    print(len(out), "items:", sum(r["block"] == "exp04_rules" for r in out), "exp04_rules,",
          sum(r["block"] == "exp03_completeness" for r in out), "exp03_completeness")


if __name__ == "__main__":
    main()

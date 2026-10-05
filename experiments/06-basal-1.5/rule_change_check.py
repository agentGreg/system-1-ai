"""Sanity checks for rule_change_items.jsonl (exp 06, changed-rule test set).

Each item must keep the source state/options/question/gold from exp 05 and differ
only by one verbatim clause swap in the rule text, with the gold flipped.
Run: python3 rule_change_check.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "05-rule-decomposition" / "items.jsonl"
ITEMS = HERE / "rule_change_items.jsonl"

src = {}
for line in SRC.read_text(encoding="utf-8").splitlines():
    if line.strip():
        j = json.loads(line)
        src[j["id"]] = j

items = [json.loads(l) for l in ITEMS.read_text(encoding="utf-8").splitlines() if l.strip()]
KINDS = {"deadline", "amount", "eligibility", "required_field", "conditional"}

assert len(items) == 20, len(items)
assert len({it["id"] for it in items}) == len(items), "duplicate ids"
for it in items:
    i, s = it["id"], src[it["id"]]
    assert it["type"] == "noul" == s["type"], i
    assert it["block"] == s["block"], i
    assert it["kind"] in KINDS, i
    assert it["state"] == s["state"], f"{i}: state differs"
    assert it["options"] == s["options"], f"{i}: options differ"
    assert it["question_orig"] == s["question"], f"{i}: question_orig differs"
    assert it["gold_orig"] == s["gold"], f"{i}: gold_orig differs"
    assert it["clause_orig"] in it["question_orig"], f"{i}: clause_orig not in question_orig"
    assert it["clause_changed"] in it["question_changed"], f"{i}: clause_changed not in question_changed"
    assert it["question_orig"].count(it["clause_orig"]) == 1, f"{i}: clause_orig not unique"
    assert it["gold_changed"] == 1 - it["gold_orig"], f"{i}: gold not flipped"
    assert it["question_orig"].replace(it["clause_orig"], it["clause_changed"]) == it["question_changed"], \
        f"{i}: question_changed is not a single clause swap"
    assert it["question_changed"] != it["question_orig"], i

flips = sum(it["gold_orig"] == 0 for it in items)
print(f"OK: {len(items)} items, {flips} yes->no, {len(items) - flips} no->yes")

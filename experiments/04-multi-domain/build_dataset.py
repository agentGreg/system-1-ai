"""Build decisions.jsonl for experiment 04: ~200 Polish business decisions across 12 domains.

Every item was written by hand for this experiment (sources in dataset_src/<domain>.py). `gold` is the author's label,
fixed there before any model (annotator or system) saw the item. All people, companies, addresses and identifiers are
fictional (identifiers use obviously invalid patterns such as 00000000000 or 00 0000 ...).

Item fields: id, domain, type (noul | choice | score), rule_based, tricky, state, question, options, keys (ASCII keys
of the options, used for the Jev criteria), gold (index into options). For noul, options = [yes-text, no-text] and
gold 0 = yes. For score, options are ordered levels from lowest to highest.

usage: python build_dataset.py            (validate all domains, write decisions.jsonl, print stats)
       python build_dataset.py --check hr (validate one domain only, write nothing)
"""
import argparse
import importlib
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOMAINS = ["administracja", "kancelaria", "hr", "przychodnia", "ubezpieczenia", "bank_aml", "logistyka",
           "it_security", "produkcja", "uczelnia", "wspolnota", "moderacja"]
FIELDS = {"id", "type", "rule_based", "tricky", "state", "question", "options", "gold"}
KEY_RE = re.compile(r"^[a-z][a-z0-9_]{0,31}$")


def load_domain(d):
    mod = importlib.import_module(f"dataset_src.{d}")
    items = []
    for raw in mod.ITEMS:
        it = dict(raw)
        missing = FIELDS - set(it)
        assert not missing, f"{it.get('id')}: missing {missing}"
        t, opts = it["type"], it["options"]
        assert t in ("noul", "choice", "score"), f"{it['id']}: bad type {t}"
        assert isinstance(it["gold"], int) and 0 <= it["gold"] < len(opts), f"{it['id']}: bad gold"
        assert isinstance(it["rule_based"], bool) and isinstance(it["tricky"], bool), f"{it['id']}: flags"
        if t == "noul":
            assert len(opts) == 2, f"{it['id']}: noul needs [yes, no]"
            it["keys"] = ["true", "false"]
        else:
            assert 3 <= len(opts) <= 6, f"{it['id']}: {t} needs 3-6 options"
            keys = it.get("keys")
            assert keys and len(keys) == len(opts) and len(set(keys)) == len(keys), f"{it['id']}: keys"
            assert all(KEY_RE.match(k) for k in keys), f"{it['id']}: keys must be ascii slugs"
        assert len(set(opts)) == len(opts), f"{it['id']}: duplicate options"
        assert it["state"].strip() and it["question"].strip(), f"{it['id']}: empty text"
        it["domain"] = d
        it["author_gold"] = it["gold"]
        items.append(it)
    return items


def stats(items):
    print(f"n={len(items)}")
    for d in sorted({it["domain"] for it in items}, key=DOMAINS.index):
        ds = [it for it in items if it["domain"] == d]
        ty = Counter(it["type"] for it in ds)
        nb = Counter(it["gold"] for it in ds if it["type"] == "noul")
        print(f"{d:14s} n={len(ds):2d} noul={ty['noul']:2d} (yes {nb[0]} / no {nb[1]}) choice={ty['choice']:2d} "
              f"score={ty['score']:2d} rule={sum(it['rule_based'] for it in ds):2d} "
              f"tricky={sum(it['tricky'] for it in ds):2d}")
    ty = Counter(it["type"] for it in items)
    print("types:", dict(ty), "rule_based:", sum(it["rule_based"] for it in items),
          "tricky:", sum(it["tricky"] for it in items))
    for t in ("choice", "score"):
        g = Counter((len(it["options"]), it["gold"]) for it in items if it["type"] == t)
        print(f"{t} gold by (n_options, index):", dict(sorted(g.items())))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", default=None)
    a = ap.parse_args()
    doms = [a.check] if a.check else DOMAINS
    items = [it for d in doms for it in load_domain(d)]
    ids = [it["id"] for it in items]
    dup = [k for k, v in Counter(ids).items() if v > 1]
    assert not dup, f"duplicate ids {dup}"
    stats(items)
    if a.check:
        return
    order = ["id", "domain", "type", "rule_based", "tricky", "state", "question", "options", "keys", "gold",
             "author_gold"]
    rows = [{k: it[k] for k in order} for it in items]
    (HERE / "decisions.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    print("wrote decisions.jsonl")


if __name__ == "__main__":
    main()

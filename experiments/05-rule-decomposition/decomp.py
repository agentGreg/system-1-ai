"""Decomposition helpers for experiment 05: loading, the boolean combiner, variant-B arithmetic, item confidence.

decompositions.jsonl, one row per item:
  id            item id (items.jsonl)
  subquestions  list of {"sid": "q1", "text": yes/no question in Polish, "kind": "read" | "arith", "calc": str|null}
                "read"  : reading the state (is X present, is the client a natural person, ...). Always sent to the model.
                "arith" : a date / deadline / amount / count comparison. Variant A sends it to the model as a yes/no
                          question like any other; variant B does not send it and evaluates "calc" in Python instead.
  values        dict of literal values stated in the state (dates "YYYY-MM-DD", months "YYYY-MM", numbers), copied
                by the experimenter; used only by the "calc" expressions of variant B (V["name"]).
  combiner      Python expression over the sids (True = "yes" to that sub-question). For noul items it returns a bool
                (True -> option 0, the "yes" option); for choice items it returns the option index.
  note          free text: how the rule maps to the combiner.

"calc" expressions may use V (the values), the read sub-answers by sid, the helpers below and plain arithmetic.
"""
import calendar
import itertools
import json
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent


def D(s):
    """date from 'YYYY-MM-DD' (or a date)"""
    return s if isinstance(s, date) else date.fromisoformat(s)


def days(a, b):
    """D(b) - D(a) in days"""
    return (D(b) - D(a)).days


def add_days(d, n):
    return D(d) + timedelta(days=n)


def add_months(d, n):
    d = D(d)
    m = d.month - 1 + n
    y, m = d.year + m // 12, m % 12 + 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def wd(d):
    """weekday, 0 = Monday ... 6 = Sunday"""
    return D(d).weekday()


def next_workday(d, holidays=(), saturday_free=True):
    """d itself if it is a working day, else the next working day (Sundays and `holidays` are never working days)."""
    d, hol = D(d), {D(h) for h in holidays}
    while d.weekday() == 6 or (saturday_free and d.weekday() == 5) or d in hol:
        d += timedelta(days=1)
    return d


def months_incl(a, b):
    """number of calendar months from month a to month b inclusive ('YYYY-MM'); '2019-09'..'2021-08' -> 24"""
    ya, ma = map(int, a.split("-")[:2])
    yb, mb = map(int, b.split("-")[:2])
    return (yb - ya) * 12 + mb - ma + 1


HELPERS = {"D": D, "days": days, "add_days": add_days, "add_months": add_months, "wd": wd,
           "next_workday": next_workday, "months_incl": months_incl, "min": min, "max": max, "abs": abs,
           "round": round, "sum": sum, "len": len, "any": any, "all": all, "int": int, "float": float}


def ev(expr, names):
    # eval of expressions written by the experimenter in decompositions.jsonl (combiners, calc); no builtins, no
    # untrusted input.
    return eval(expr, {"__builtins__": {}}, {**HELPERS, **names})


def load(path=HERE / "decompositions.jsonl"):
    return {r["id"]: r for r in (json.loads(l) for l in Path(path).read_text().splitlines() if l.strip())}


def load_items(path=HERE / "items.jsonl"):
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def sids(dec, kind=None):
    return [q["sid"] for q in dec["subquestions"] if kind is None or q["kind"] == kind]


def outcome(dec, answers):
    """Combiner result mapped to an option index."""
    r = ev(dec["combiner"], answers)
    if isinstance(r, bool):
        return 0 if r else 1
    return int(r)


def arith_answers(dec, read_answers):
    """Variant B: arith sub-answers computed from V and the read sub-answers."""
    names = {**read_answers, "V": dec.get("values") or {}}
    out = {}
    for q in dec["subquestions"]:
        if q["kind"] == "arith":
            out[q["sid"]] = bool(ev(q["calc"], {**names, **out}))
    return out


def decide(dec, p_yes, variant):
    """Item decision from sub-question probabilities.

    p_yes: {sid: P(yes)} for the sids the variant sends to the model (A: all, B: read only).
    Returns (pred, conf, dist): pred = combiner over argmax sub-answers; dist = distribution over option indices
    assuming independent sub-answers (exact enumeration); conf = dist[pred].
    """
    asked = sids(dec) if variant == "A" else sids(dec, "read")
    arg = {s: p_yes[s] >= 0.5 for s in asked}

    def full(ans):
        return {**ans, **arith_answers(dec, ans)} if variant == "B" else ans

    pred = outcome(dec, full(arg))
    dist = {}
    for bits in itertools.product((True, False), repeat=len(asked)):
        ans = dict(zip(asked, bits))
        pr = 1.0
        for s, b in ans.items():
            pr *= p_yes[s] if b else 1.0 - p_yes[s]
        o = outcome(dec, full(ans))
        dist[o] = dist.get(o, 0.0) + pr
    return pred, dist.get(pred, 0.0), dist

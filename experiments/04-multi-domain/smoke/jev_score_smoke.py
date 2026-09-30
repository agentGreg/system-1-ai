"""Smoke test: how the raw Jev System One endpoint answers `score` questions (list vs keyed criteria)."""
import json, sys
sys.path.insert(0, "..")
from common import HERE, api_key, check_budget, log_cost, post
URL = "https://openrouter.ai/api/alpha/decisions"
key = api_key()
state = "Zgłoszenie od mieszkańca: od rana w całym budynku nie ma ciepłej wody, zimna leci normalnie."
q = "Jak pilne jest to zgłoszenie?"
variants = {
  "list": {"type": "score", "instructions": q, "criteria": ["1 - niska", "2 - średnia", "3 - wysoka", "4 - krytyczna"]},
  "dict": {"type": "score", "instructions": q, "criteria": {"niska": "1 - niska", "srednia": "2 - średnia", "wysoka": "3 - wysoka", "krytyczna": "4 - krytyczna"}},
  "choice6": {"type": "choice", "instructions": q, "criteria": {f"k{i}": f"opcja {i}" for i in range(6)}},
}
out = {}
for name, qq in variants.items():
    check_budget(0.001)
    data, status, lat, att = post(key, URL, {"model": "typesafe/jev-1.13", "state": state, "questions": {"q": qq}}, timeout=60)
    u = data.get("usage") or {}
    log_cost("smoke-jev", "typesafe/jev-1.13", f"smoke-{name}", u.get("cost"), data.get("model"))
    out[name] = {"status": status, "latency_ms": lat, "answers": data.get("answers"), "error": data.get("error"), "model": data.get("model"), "usage": u}
(HERE / "smoke" / "jev_score_smoke.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps(out, ensure_ascii=False, indent=1)[:3000])

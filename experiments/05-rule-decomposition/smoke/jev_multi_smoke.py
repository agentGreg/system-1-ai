"""Smoke test (not an experiment item): does the decisions endpoint accept several noul questions in one call?"""
import json, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
from common import HERE, api_key, log_cost, post

key = api_key()
state = "Wiadomość od klienta: Dzień dobry, zamówienie nr TEST-0001 nie dotarło. Proszę o zwrot pieniędzy."
qs = {f"q{i}": {"type": "noul", "instructions": t, "criteria": {"true": "Tak", "false": "Nie"}} for i, t in enumerate(
    ["Czy wiadomość zawiera numer zamówienia?", "Czy klient żąda zwrotu pieniędzy?", "Czy podano numer rachunku bankowego?"], 1)}
data, status, lat, att = post(key, "https://openrouter.ai/api/alpha/decisions",
                              {"model": "typesafe/jev-1.13", "state": state, "questions": qs}, timeout=60)
u = data.get("usage") or {}
log_cost("smoke multi-question", "typesafe/jev-1.13", "SMOKE", u.get("cost"), data.get("model"), {"n_q": 3})
out = {"status": status, "latency_ms": lat, "model": data.get("model"), "answers": data.get("answers"), "usage": u,
       "error": data.get("error")}
(HERE / "smoke" / "jev_multi_smoke.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps(out, ensure_ascii=False))

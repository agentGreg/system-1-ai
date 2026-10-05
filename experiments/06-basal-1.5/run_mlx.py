"""basal letter readout with MLX (mlx_lm), the same decision logic and output rows as run_basal.py (PyTorch MPS).

Per decision: same prompt (basal_prompt.render), two option orders (one forward each, no padding), softmax over the
option letters' next-token logits in float32, mapped back to canonical order and averaged, then the per-type
temperature from the model's calibration file: CALIBRATION.mlx.json when the repo ships one (what basal-serve --mode
mlx loads, basal/server.py), else CALIBRATION.json. Variants --facts auto and --rule-in-state as in run_basal.py.

usage: python run_mlx.py --model ~/models/basal-mlx/basal-1.5-mini-MLX-4bit --set e03 --out raw_mlx-4bit_mini_e03.jsonl
       --model also takes a hub id (e.g. Remek/basal-1.5-mini-MLX-8bit)
"""
import argparse
import json
import time
from pathlib import Path

import mlx.core as mx
from huggingface_hub import snapshot_download
from mlx_lm import load

from basal_facts import inject
from basal_prompt import lang_of, letter_ids, render
from common import HERE, hardware, load_set, variant, write_jsonl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--orders", type=int, default=2)
    ap.add_argument("--set", required=True)
    ap.add_argument("--facts", default="off", choices=["off", "auto"])
    ap.add_argument("--rule-in-state", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    p = Path(a.model).expanduser()
    md = p if p.exists() else Path(snapshot_download(a.model))
    cal_path = md / "CALIBRATION.mlx.json" if (md / "CALIBRATION.mlx.json").exists() else md / "CALIBRATION.json"
    cal = json.loads(cal_path.read_text()) if cal_path.exists() else {}
    temps = cal.get("temperature_per_prim", {})

    t0 = time.perf_counter()
    model, wrapper = load(str(md))
    tok = wrapper._tokenizer
    load_s = time.perf_counter() - t0

    def decide(it):
        state, question = variant(it, facts=a.facts == "auto", rule_in_state=a.rule_in_state, inject=inject)
        opts = it["options"]
        k = len(opts)
        lang = lang_of(state + question)
        perms = [list(range(k)), list(range(k))[::-1]][: a.orders]
        prompts = [render(tok, state, question, [opts[c] for c in pm], lang) for pm in perms]
        ids = letter_ids(tok, prompts[0], k)
        assert ids is not None, "option letters are not single tokens"
        canon, n_in = [], 0
        for perm, prompt in zip(perms, prompts):
            enc = tok(prompt, add_special_tokens=False).input_ids
            n_in = max(n_in, len(enc))
            logits = model(mx.array([enc]))[0, -1, :].astype(mx.float32)
            pp = mx.softmax(logits[mx.array(ids)], axis=-1).tolist()
            c = [0.0] * k
            for pos, j in enumerate(perm):
                c[j] = pp[pos]
            canon.append(c)
        pr = mx.array([sum(x) / len(canon) for x in zip(*canon)])
        T = temps.get(it["type"], 1.0)
        if T != 1.0:
            pr = mx.softmax(mx.log(mx.maximum(pr, 1e-12)) / T, axis=-1)
        return pr.tolist(), canon, n_in, T, state != it["state"]

    items = load_set(a.set)
    if a.limit:
        items = items[: a.limit]
    for it in items[:2]:  # warm-up (not timed)
        decide(it)
    rows = []
    for it in items:
        t = time.perf_counter()
        probs, canon, n_in, T, changed = decide(it)
        lat = (time.perf_counter() - t) * 1000
        pred = max(range(len(probs)), key=probs.__getitem__)
        pred_o1 = max(range(len(probs)), key=canon[0].__getitem__)
        rows.append({"id": it["id"], "category": it["category"], "type": it["type"],
                     "gold": it["gold"], "pred": pred, "correct": pred == it["gold"],
                     "p_pred": probs[pred], "p_gold": probs[it["gold"]], "probs": probs,
                     "pred_order1_only": pred_o1, "probs_per_order": canon, "temperature": T,
                     "expected_level": sum(j * v for j, v in enumerate(probs)) if it["type"] == "score" else None,
                     "state_modified": changed, "latency_ms": lat, "input_tokens_padded_per_row": n_in,
                     "output_tokens": 0})
        print(f'{it["id"]} gold={it["gold"]} pred={pred} p={probs[pred]:.3f} {lat:.0f}ms', flush=True)
    cfg = json.loads((md / "config.json").read_text())
    meta = {"system": a.model, "path": str(md).replace(str(Path.home()), "~"), "quantization": cfg.get("quantization"), "engine": "mlx_lm",
            "orders": a.orders, "set": a.set, "facts": a.facts, "rule_in_state": a.rule_in_state,
            "calibration_file": cal_path.name, "temperatures": temps,
            "thresholds": {k: v.get("confidence") for k, v in cal.get("thresholds", {}).items()}
            if isinstance(cal.get("thresholds"), dict) else cal.get("thresholds"),
            "load_s": load_s, "mlx": mx.__version__, "hardware": hardware()}
    write_jsonl(HERE / a.out, rows)
    (HERE / a.out).with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    acc = sum(r["correct"] for r in rows) / len(rows)
    print(f"load {load_s:.1f}s  acc {acc:.3f}")


if __name__ == "__main__":
    main()

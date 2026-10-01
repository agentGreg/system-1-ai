"""basal-1.0 on the decomposed sub-questions (Apple Silicon, PyTorch MPS), same decision logic as experiments 01/03/04.

Every sub-question of every item in decompositions.jsonl is one noul decision: the item's state, the sub-question as
the question, options ["Tak", "Nie"] (yes first, as the noul items of experiments 03/04), basal.prompt.render
(vendored as basal_prompt.py), both option orders (original + reversed) batched in one forward, softmax over the
option letters, mapped back and averaged, then CALIBRATION.json's noul temperature. No text is generated.

Sub-questions are run one after another (one forward with 2 rows each); the per-item latency reported in results.md is
the sum over the sub-questions a variant sends to the model (variant A: all, variant B: read only). Variant B's read
answers are the same forward passes as variant A's (the model is deterministic and answers each sub-question
independently), so one run serves both variants.

usage: python run_basal.py --model Remek/basal-1.0-4.5B --out raw_basal-4.5B.jsonl
"""
import argparse
import json
import time
from pathlib import Path

import torch
from huggingface_hub import snapshot_download
from transformers import AutoModelForCausalLM, AutoTokenizer

from basal_prompt import lang_of, letter_ids, render
from common import HERE, hardware, write_jsonl
from decomp import load, load_items

OPTS = ["Tak", "Nie"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Remek/basal-1.0-4.5B")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    md = Path(snapshot_download(a.model))
    cal_path = md / "CALIBRATION.json"
    cal = json.loads(cal_path.read_text()) if cal_path.exists() else {}
    temps = cal.get("temperature_per_prim", {})
    T = temps.get("noul", 1.0)

    t0 = time.perf_counter()
    tok = AutoTokenizer.from_pretrained(md)
    tok.padding_side = "left"
    tok.pad_token = tok.pad_token or tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(md, dtype=getattr(torch, a.dtype)).to("mps").eval()
    torch.mps.synchronize()
    load_s = time.perf_counter() - t0

    @torch.no_grad()
    def decide(state, question):
        lang = lang_of(state + question)
        perms = [[0, 1], [1, 0]]
        prompts = [render(tok, state, question, [OPTS[c] for c in p], lang) for p in perms]
        ids = letter_ids(tok, prompts[0], 2)
        assert ids is not None, "option letters are not single tokens"
        enc = tok(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to("mps")
        logits = model(**enc, logits_to_keep=1).logits[:, -1, :].float()
        lp = torch.log_softmax(logits, -1)
        per_order = [torch.softmax(lp[b, ids], -1).tolist() for b in range(2)]
        canon = []
        for perm, pp in zip(perms, per_order):
            c = [0.0, 0.0]
            for pos, j in enumerate(perm):
                c[j] = pp[pos]
            canon.append(c)
        p = torch.tensor([sum(x) / 2 for x in zip(*canon)])
        if T != 1.0:
            p = torch.softmax(torch.log(p.clamp_min(1e-12)) / T, -1)
        torch.mps.synchronize()
        return p.tolist(), canon, int(enc.input_ids.shape[1])

    items, decs = load_items(), load()
    for it in items[:2]:  # warm-up (not timed)
        decide(it["state"], decs[it["id"]]["subquestions"][0]["text"])
    rows = []
    for it in items:
        d = decs[it["id"]]
        subs = []
        for q in d["subquestions"]:
            t = time.perf_counter()
            probs, canon, n_in = decide(it["state"], q["text"])
            lat = (time.perf_counter() - t) * 1000
            subs.append({"sid": q["sid"], "kind": q["kind"], "p_yes": probs[0], "probs": probs,
                         "probs_per_order": canon, "latency_ms": lat, "input_tokens_padded_per_row": n_in})
        rows.append({"id": it["id"], "block": it["block"], "type": it["type"], "gold": it["gold"],
                     "temperature": T, "subanswers": subs})
        print(it["id"], " ".join(f'{s["sid"]}={s["p_yes"]:.2f}' for s in subs), flush=True)
    meta = {"system": a.model, "hf_revision": md.name, "dtype": a.dtype, "device": "mps", "orders": 2,
            "options": OPTS, "temperature_noul": T, "calibration_keys": list(cal), "load_s": load_s,
            "torch": torch.__version__, "hardware": hardware(),
            "n_items": len(rows), "n_subquestions": sum(len(r["subanswers"]) for r in rows)}
    write_jsonl(HERE / a.out, rows)
    (HERE / a.out).with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print(f"load {load_s:.1f}s  {meta['n_subquestions']} sub-questions")


if __name__ == "__main__":
    main()

"""basal-1.0 letter readout on Apple Silicon (PyTorch MPS), reproducing the basal server's decision logic.

Per decision (what `basal-serve` does by default):
  * options as in basal/run.py "simple" items: noul -> [yes-text, no-text], choice -> option texts (option_keys="hide")
  * prompt = basal.prompt.render(...) (vendored unchanged as basal_prompt.py): fixed system prompt, state, question,
    lettered options, chat template with enable_thinking=False, assistant turn prefilled with {"answer": "
  * two option orders (original + reversed), one forward each (batched together, left padding), softmax over the option
    letters' next-token logits only, mapped back to canonical order and averaged
  * per-type temperature from CALIBRATION.json applied to the averaged distribution
No text is generated: one forward pass per option order.

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
from common import HERE, hardware, load_items, write_jsonl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Remek/basal-1.0-4.5B")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--orders", type=int, default=2)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    md = Path(snapshot_download(a.model))
    rev = md.name
    cal_path = md / "CALIBRATION.json"
    cal = json.loads(cal_path.read_text()) if cal_path.exists() else {}
    temps = cal.get("temperature_per_prim", {})
    basal_json = json.loads((md / "basal.json").read_text()) if (md / "basal.json").exists() else {}

    t0 = time.perf_counter()
    tok = AutoTokenizer.from_pretrained(md)
    tok.padding_side = "left"
    tok.pad_token = tok.pad_token or tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(md, dtype=getattr(torch, a.dtype)).to("mps").eval()
    torch.mps.synchronize()
    load_s = time.perf_counter() - t0

    @torch.no_grad()
    def decide(it):
        opts = it["options"]
        k = len(opts)
        lang = lang_of(it["state"] + it["question"])
        perms = [list(range(k)), list(range(k))[::-1]][: a.orders]
        prompts = [render(tok, it["state"], it["question"], [opts[c] for c in p], lang) for p in perms]
        ids = letter_ids(tok, prompts[0], k)
        assert ids is not None, "option letters are not single tokens"
        enc = tok(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to("mps")
        logits = model(**enc, logits_to_keep=1).logits[:, -1, :].float()
        lp = torch.log_softmax(logits, -1)
        per_order = [torch.softmax(lp[b, ids], -1).tolist() for b in range(len(perms))]
        canon = []
        for perm, pp in zip(perms, per_order):
            c = [0.0] * k
            for pos, j in enumerate(perm):
                c[j] = pp[pos]
            canon.append(c)
        p = torch.tensor([sum(x) / len(canon) for x in zip(*canon)])
        T = temps.get(it["type"], 1.0)
        if T != 1.0:
            p = torch.softmax(torch.log(p.clamp_min(1e-12)) / T, -1)
        return p.tolist(), canon, int(enc.input_ids.shape[1]), T

    items = load_items()
    for it in items[:2]:  # warm-up (not timed)
        decide(it)
    rows = []
    for it in items:
        t = time.perf_counter()
        probs, canon, n_in, T = decide(it)
        lat = (time.perf_counter() - t) * 1000
        pred = max(range(len(probs)), key=probs.__getitem__)
        pred_o1 = max(range(len(probs)), key=canon[0].__getitem__)
        rows.append({"id": it["id"], "category": it["category"], "type": it["type"], "tricky": it["tricky"],
                     "gold": it["gold"], "pred": pred, "correct": pred == it["gold"],
                     "p_pred": probs[pred], "p_gold": probs[it["gold"]], "probs": probs,
                     "pred_order1_only": pred_o1, "probs_per_order": canon, "temperature": T,
                     "latency_ms": lat, "input_tokens_padded_per_row": n_in, "output_tokens": 0})
        print(f'{it["id"]} gold={it["gold"]} pred={pred} p={probs[pred]:.3f} {lat:.0f}ms', flush=True)
    meta = {"system": a.model, "hf_revision": rev, "dtype": a.dtype, "device": "mps", "orders": a.orders,
            "temperatures": temps, "calibration_keys": list(cal), "basal_json": basal_json,
            "load_s": load_s, "torch": torch.__version__, "hardware": hardware()}
    write_jsonl(HERE / a.out, rows)
    (HERE / a.out).with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    acc = sum(r["correct"] for r in rows) / len(rows)
    print(f"load {load_s:.1f}s  acc {acc:.3f}")


if __name__ == "__main__":
    main()

"""Generative LLM baseline (Qwen3 via mlx-lm) on the same 30 decisions, with thinking on or off.

The model gets the same state / question / lettered options (original order only) and is asked to reply with the
option letter. With --thinking the chat template's enable_thinking=True is used and the model writes its reasoning in
<think>...</think> before answering; the answer letter is parsed from the text after </think>.
Sampling follows Qwen3's published recommendations (thinking: T=0.6, top_p=0.95, top_k=20; non-thinking: T=0.7,
top_p=0.8, top_k=20), fixed seed.

Copied unchanged from ../01-basal-vs-thinking/run_llm.py (only this docstring differs).

usage: python run_llm.py --model <mlx dir> --thinking --out raw_qwen3-14b_think.jsonl
"""
import argparse
import json
import re
import time
from pathlib import Path

import mlx.core as mx
from mlx_lm import load, stream_generate
from mlx_lm.sample_utils import make_sampler

from common import HERE, hardware, load_items, write_jsonl

LETTERS = "ABCDEFGHIJ"
SYSTEM = "Jesteś asystentem działu obsługi klienta. Oceniasz sprawę i wybierasz dokładnie jedną z podanych opcji."
USER = ("Wiadomość / zgłoszenie:\n{state}\n\nPytanie: {q}\nOpcje:\n{opts}\n\n"
        "Odpowiedz wyłącznie literą wybranej opcji (np. A).")


def parse_letter(text, k):
    ans = text.split("</think>")[-1]
    m = re.findall(rf"\b([{LETTERS[:k]}])\b", ans)
    return LETTERS.index(m[0]) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--thinking", action="store_true")
    ap.add_argument("--max-tokens", type=int, default=8192)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    t0 = time.perf_counter()
    model, tok = load(a.model)
    load_s = time.perf_counter() - t0
    sampler = (make_sampler(temp=0.6, top_p=0.95, top_k=20) if a.thinking
               else make_sampler(temp=0.7, top_p=0.8, top_k=20))

    def ask(it):
        opts = "\n".join(f"{LETTERS[i]}. {o}" for i, o in enumerate(it["options"]))
        msgs = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": USER.format(state=it["state"], q=it["question"], opts=opts)}]
        prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                         enable_thinking=a.thinking)
        text, last, t_first = "", None, None
        t = time.perf_counter()
        for r in stream_generate(model, tok, prompt, max_tokens=a.max_tokens, sampler=sampler):
            if t_first is None:
                t_first = time.perf_counter() - t
            text += r.text
            last = r
        lat = (time.perf_counter() - t) * 1000
        return text, last, lat, t_first * 1000

    items = load_items()
    mx.random.seed(a.seed)
    for it in items[:2]:  # warm-up (not timed)
        ask(it)
    mx.random.seed(a.seed)
    rows = []
    for it in items:
        text, r, lat, ttft = ask(it)
        k = len(it["options"])
        pred = parse_letter(text, k)
        think = text.split("</think>")[0] if "</think>" in text else ""
        rows.append({"id": it["id"], "category": it["category"], "type": it["type"], "tricky": it["tricky"],
                     "gold": it["gold"], "pred": pred, "correct": pred == it["gold"],
                     "latency_ms": lat, "ttft_ms": ttft, "input_tokens": r.prompt_tokens,
                     "output_tokens": r.generation_tokens, "finish_reason": r.finish_reason,
                     "gen_tps": r.generation_tps, "thinking_chars": len(think),
                     "answer_text": text.split("</think>")[-1].strip(), "full_text": text})
        print(f'{it["id"]} gold={it["gold"]} pred={pred} out_tok={r.generation_tokens} {lat/1000:.1f}s', flush=True)
    meta = {"system": a.label, "model_path": a.model, "thinking": a.thinking, "load_s": load_s,
            "max_tokens": a.max_tokens, "seed": a.seed, "hardware": hardware()}
    write_jsonl(HERE / a.out, rows)
    (HERE / a.out).with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    acc = sum(r["correct"] for r in rows) / len(rows)
    print(f"load {load_s:.1f}s  acc {acc:.3f}")


if __name__ == "__main__":
    main()

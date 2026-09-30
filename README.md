# system-1-ai

Small, reproducible experiments comparing "System 1" decision models (one forward pass, calibrated probabilities over
typed options, no text generation) with generative "thinking" LLMs on everyday business decisions.

## Experiments

- `experiments/01-basal-vs-thinking/`: 30 Polish customer-service / back-office decisions (is it a complaint, which
  department, escalate to a human, is the form complete). basal-1.0 (4.5B and 1.5B, letter readout, both option orders
  averaged, calibrated) vs Qwen3-14B with thinking on and off, all run locally on an Apple Silicon Mac.
  See `results.md` there.

## Running

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python torch "transformers==5.17.0" huggingface_hub accelerate safetensors mlx-lm
cd experiments/01-basal-vs-thinking
../../.venv/bin/python run_basal.py --model Remek/basal-1.0-4.5B --out raw_basal-4.5B.jsonl
../../.venv/bin/python -m mlx_lm convert --hf-path Qwen/Qwen3-14B --mlx-path <dir> -q --q-bits 4
../../.venv/bin/python run_llm.py --model <dir> --label "Qwen3-14B thinking" --thinking --out raw_qwen3-14b_think.jsonl
../../.venv/bin/python analyze.py
```

`basal_prompt.py` is a verbatim copy of `basal/prompt.py` from https://github.com/rkinas/basal (Apache-2.0).

## License

Code is MIT (see `LICENSE`), except `basal_prompt.py`, which stays Apache-2.0 as in the original. The test set (`decisions.jsonl`) and results are CC BY 4.0: reuse them freely with attribution.

Write-up: [Your AI thinks too long: System 1 AI explained](https://agentgreg.ai/research/system-one-ai/) ([PL](https://agentgreg.ai/pl/research/system-one-ai/)).

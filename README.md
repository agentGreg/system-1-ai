# system-1-ai

Small, reproducible experiments comparing "System 1" decision models (one forward pass, calibrated probabilities over
typed options, no text generation) with generative "thinking" LLMs on everyday business decisions.

## Experiments

- `experiments/01-basal-vs-thinking/`: 30 Polish customer-service / back-office decisions (is it a complaint, which
  department, escalate to a human, is the form complete). basal-1.0 (4.5B and 1.5B, letter readout, both option orders
  averaged, calibrated) vs Qwen3-14B with thinking on and off, all run locally on an Apple Silicon Mac.
  See `results.md` there.
- `experiments/02-jev-router-and-cloud/`: the same 30 decisions and the same prompt sent through OpenRouter to
  TypeSafe's Jev Router (`typesafe/jev-router`, which picks another model and effort per request), the two models it
  picked called directly (GPT-6 Luna, DeepSeek V4.1 Flash), and cloud reasoning models (Claude Sonnet 5.5, GPT-6.1 Sol,
  Gemini 3.8 Flash). Accuracy, end-to-end latency from Poland, tokens and exact cost per call. See `results.md` there.
- `experiments/03-extended-set/`: 200 Polish decisions (the 30 above plus 170 new, six categories including
  irritation level and phishing), labels checked blind by two LLM annotators from different vendors (198/200 agreed,
  2 disputed items left for human adjudication). basal-1.0 (local), raw Jev 1.13 via the System One endpoint (both
  option orders), Gemini 3.8 Flash, Mistral Medium 3.1 and local Qwen3-14B: accuracy with 95% intervals, latency,
  cost, coverage at confidence thresholds and calibration. See `results.md` there.

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

Experiment 02 needs only Python 3 (standard library) and an OpenRouter key in the macOS keychain
(`security add-generic-password -s openrouter-api-key -w`); see `run_all_chat.sh` there.

Experiment 03: `python build_dataset.py`, then `annotate.py`, `run_basal.py`, `run_jev.py`, `run_cloud.py`,
`run_llm.py` and `analyze.py` (commands in the docstrings; the API scripts use the same keychain entry).

`basal_prompt.py` is a verbatim copy of `basal/prompt.py` from https://github.com/rkinas/basal (Apache-2.0).

## Use of model outputs

Raw model outputs in this repo are published for evaluation only. Do not use them to train, fine-tune or distill
models. Jev results come from the alpha endpoint https://openrouter.ai/api/alpha/decisions (typesafe/jev-1.13) and are
a snapshot as of 2026-09-30; this repo is independent and not affiliated with or endorsed by TypeSafe AI, OpenRouter
or any other model provider.

## License

Code is MIT (see `LICENSE`), except `basal_prompt.py`, which stays Apache-2.0 as in the original. The test set (`decisions.jsonl`) and results are CC BY 4.0: reuse them freely with attribution.

Write-up: [Your AI thinks too long: System 1 AI explained](https://agentgreg.ai/research/system-one-ai/) ([PL](https://agentgreg.ai/pl/research/system-one-ai/)).

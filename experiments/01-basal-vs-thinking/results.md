# Experiment 01: basal-1.0 (System 1) vs Qwen3-14B with and without thinking

Date: 2026-09-30. 30 Polish customer-service / back-office decisions, all run locally on one Mac.

## Setup

**Hardware.** Apple M5 Max, 128 GB unified memory, macOS 26.6.2. Python 3.12, PyTorch 2.14.0 (MPS),
transformers 5.17.0, mlx-lm 0.31.3. Nothing else heavy was running on the GPU during timed runs (a network download
was running in the background during the Qwen runs and the first basal-4.5B run).

**Test set** (`decisions.jsonl`, written by us for this experiment, gold labels fixed before any model was run):

| category | type | n | question |
|---|---|---|---|
| reklamacja | noul (yes/no) | 10 | Is this message a complaint (defect / non-conformity + a demand)? |
| routing | choice (5 options) | 10 | Which department: complaints, invoices/payments, delivery, tech support, sales |
| eskalacja | noul | 5 | Hand over to a human now? (legal threat, very angry, vulnerable person) |
| kompletnosc | noul | 5 | Is the complaint form complete under a stated 4-part rule? |

8 items are marked `tricky` (sarcasm, a polite complaint, praise plus a sales question, statutory withdrawal that is
not a complaint, a sales question that mentions a past delivery, a joking password question, a refund request with
no bank account).

**Systems**

| system | weights | how it answers |
|---|---|---|
| basal-1.0-4.5B | `Remek/basal-1.0-4.5B` rev `b952880`, bf16, PyTorch MPS, eager (no compile, no graphs) | one forward pass per option order, letter readout, no generation |
| basal-1.0-1.5B | `Remek/basal-1.0-1.5B` rev `81a74ac`, same setup | same |
| Qwen3-14B thinking ON | `Qwen/Qwen3-14B` rev `40c0698`, converted to MLX 4-bit (group 64, 4.5 bits/weight) | generates `<think>...</think>` then a letter |
| Qwen3-14B thinking OFF | same weights, `enable_thinking=False` | generates a letter directly |

**basal details.** `run_basal.py` reimplements the basal server's logic on MPS: prompts come from `basal_prompt.py`,
a verbatim copy of `basal/prompt.py` (fixed system prompt, `enable_thinking=False`, `{"answer": "` prefill,
single-token letter check). Options follow basal's `run.py` "simple" format (noul = [yes-text, no-text]; choice =
option texts with `option_keys="hide"`). Each decision is asked in the **original and reversed option order**
(both in one batch of 2), the two distributions are mapped back to canonical order and **averaged**, then the
per-type temperature from `CALIBRATION.json` v1.0.1 is applied (noul T=1.477, choice T=1.075). This is what
`basal-serve` does by default. `probs_per_order` in the raw files holds both orders before averaging.

**Qwen details.** `run_llm.py`, same state / question / lettered options (original order only, no averaging),
Polish instruction "answer only with the option letter". Sampling as recommended by Qwen (thinking: T=0.6,
top_p=0.95, top_k=20; non-thinking: T=0.7, top_p=0.8, top_k=20), seed 0, max 8192 new tokens. The answer is the
first capital option letter after `</think>`. Every generation ended with a normal stop (no truncation).
Seed check: seeds 1 and 2 gave exactly the same errors in both modes (`raw_seedcheck_*.jsonl`).

**Latency.** Wall clock per decision, batch size 1, measured after 2 untimed warm-up decisions, includes tokenization.
For basal it covers both option orders. For Qwen it is the full generation (thinking included).

## Results

| system | accuracy | reklamacja | routing | eskalacja | kompletnosc | tricky | median latency | p90 latency | median output tokens | max output tokens |
|---|---|---|---|---|---|---|---|---|---|---|
| basal-1.0-4.5B | **27/30** | 10/10 | 9/10 | 5/5 | 3/5 | 7/8 | **118 ms** | 139 ms | 0 | 0 |
| basal-1.0-1.5B | **27/30** | 9/10 | 10/10 | 5/5 | 3/5 | 6/8 | **50 ms** | 53 ms | 0 | 0 |
| Qwen3-14B thinking ON | **29/30** | 10/10 | 9/10 | 5/5 | 5/5 | 8/8 | **3,939 ms** | 5,152 ms | 224 | 374 |
| Qwen3-14B thinking OFF | **28/30** | 10/10 | 9/10 | 5/5 | 4/5 | 8/8 | **289 ms** | 481 ms | 2 | 16 |

Totals for all 30 decisions: basal-4.5B 3.9 s, basal-1.5B 1.5 s, Qwen thinking ON 125.6 s, Qwen thinking OFF 10.0 s.
A second basal-4.5B run gave median 132 ms and the same predictions. Qwen generated about 61 tokens/s with thinking.
Input size: about 190 to 255 tokens per prompt for all systems.

Load time (weights already in the OS file cache, so these are warm-cache numbers): basal-4.5B 1.9 s and 3.0 s
(two runs), basal-1.5B 0.7 s. The MLX load time (0.5 to 1.0 s) is not comparable: MLX loads lazily and part of the
real loading happens in the untimed warm-up calls.

**Order averaging matters for basal.** Using only the original option order, basal-4.5B would score 28/30 (it gets
D07 right in that order) and basal-1.5B 27/30. Averaging exposes the order sensitivity on exactly those items instead
of hiding it.

**Confidence thresholds (basal only).** `CALIBRATION.json` ships frozen thresholds: confidence >= 0.913 (target 1%
error) and >= 0.744 (target 5% error). On our 30 items:

| system | threshold | decided automatically | wrong among automatic | sent to a human |
|---|---|---|---|---|
| basal-4.5B | 0.913 | 23 | 0 | D07, E01, E04, K01, K02, K03, K04 |
| basal-4.5B | 0.744 | 28 | 2 (K02, K03) | D07, K01 |
| basal-1.5B | 0.913 | 14 | 0 | 16 items |
| basal-1.5B | 0.744 | 21 | 0 | 9 items (incl. all 3 errors) |

At the strict threshold, every basal-4.5B error lands in the "ask a human" bucket and none of the 23 automatic
decisions is wrong. Qwen gives no comparable confidence number with this setup.

## Errors

### basal-1.0-4.5B (3)
- **D07** "Czy router, który macie w ofercie za 299 zł, obsługuje Wi-Fi 7? Zastanawiam się nad zakupem dwóch sztuk."
  Gold: Sprzedaż. Predicted: Wsparcie techniczne, p=0.547. Original order: Sprzedaż 0.81. Reversed order:
  Techniczne 0.92. The two orders disagree, the average is near a coin flip.
- **K02** Refund request with bank account but **no order number**. Gold: incomplete. Predicted: complete, p=0.839.
- **K03** "Zamówienie 60871. Ekspres do kawy przecieka... Proszę o zwrot pieniędzy." Refund requested, **no bank
  account**. Gold: incomplete. Predicted: complete, p=0.757.

On the completeness rule basal-4.5B leans "complete" for 4 of 5 forms (0.72 to 0.90); only K05 (no demand at all)
got "incomplete". It does not seem to check the four conditions one by one.

### basal-1.0-1.5B (3)
- **R03** Polite complaint ("bardzo lubię Państwa sklep... sweter ma rozpruty szew... byłabym wdzięczna, gdyby udało
  się przysłać nowy egzemplarz"). Gold: complaint. Predicted: not a complaint, p=0.540. The two orders disagree.
- **K02**, **K03**: same as 4.5B (p=0.636, 0.586).

### Qwen3-14B thinking ON (1)
- **D07** Predicted: Wsparcie techniczne (374 output tokens, the longest reasoning in the set). The reasoning
  noticed "they mention considering buying two units" and then decided "the core of the query is technical".

### Qwen3-14B thinking OFF (2)
- **D07** Predicted: Wsparcie techniczne.
- **K01** "Zamówienie nr 55123. Słuchawki... lewa słuchawka nie ładuje się od pierwszego dnia. Proszę o wymianę na
  nowe." Complete (exchange, so no bank account needed). Predicted: incomplete. Same answer on seeds 0, 1, 2.

With thinking on, Qwen got all 5 completeness checks right; its reasoning lists the four conditions and checks each
(for K03 it explicitly notes the missing account number).

## Caveats

- **n=30.** One error is 3.3 points. The differences in accuracy here (27 vs 28 vs 29) are not statistically
  meaningful. The latency differences (50 ms vs 4 s) are large and stable.
- **We wrote the test set and the gold labels.** They are clear to us, but no second annotator checked them.
  In hindsight **D07 is debatable**: a pre-purchase question about a product specification could go to sales or to
  tech support. Three of the four systems (basal-4.5B and both Qwen runs) chose tech support; basal-1.5B chose
  sales (p 0.957). So it may be our label, not the models. Without D07: basal-4.5B 27/29, basal-1.5B 26/29,
  Qwen thinking 29/29, Qwen no-think 28/29. We did not change any label after seeing results.
- **Mac, not a datacenter GPU.** basal ran as plain eager PyTorch on MPS in bf16, with none of the engine's
  optimisations (CUDA graphs, torch.compile, shared prefix for the two orders). The basal README reports 12.5 ms per
  two-order decision on an H100. Our 118 ms is what a laptop does with a naive port.
- **Unequal footing on speed.** Qwen ran through MLX with 4-bit weights (Apple's fast path); basal ran through PyTorch
  MPS in bf16. A 4-bit or MLX port of basal would likely be faster than what we measured. Qwen is also 3x larger than
  basal-4.5B.
- **Unequal footing on method.** basal averages two option orders and is calibrated; Qwen answered once in the
  original order. Qwen's thinking was in English although the prompt was Polish.
- **Single-question prompts.** basal can score many questions against one state; Qwen would need one call per
  question (or a combined prompt) in production. Not tested here.
- **No throughput test.** All numbers are batch size 1. Batching would favour basal (one forward pass, no decoding).
- **One run** per system for the main numbers (plus seed checks for Qwen and one basal repeat).

## Files

- `decisions.jsonl`: the 30 items (id, type, state, question, options, gold, tricky)
- `run_basal.py`, `basal_prompt.py`, `run_llm.py`, `common.py`, `analyze.py`: scripts
- `raw_*.jsonl` + `raw_*.meta.json`: per-item raw outputs (basal: both per-order distributions; Qwen: full text
  including thinking) and run metadata
- `results.csv`: one row per system and item
- `log_*.txt`: console logs of the Qwen runs

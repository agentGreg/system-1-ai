Independent evaluation; not affiliated with or endorsed by any model provider. Jev results are a snapshot of the alpha endpoint.

# Experiment 06: basal-1.5 (mini, 4.5B, max) on our Polish decision sets

Date: 2026-10-05, the day basal-1.5 was released. Goal: rerun the protocol of experiments 03/04/05 with the three new
basal models, and test four things the release adds or claims: better accuracy and calibration, the Mac engines
(MLX), `"facts": "auto"` for rules with dates and amounts, SOAM (one state, many questions). A fifth test answers a
question from a LinkedIn thread: when a procedure or price changes, does the model follow the new rule without
retraining?

**Short answer.**
- basal-1.5-max (11B) is the first open basal model in the range of Jev 1.13 on our sets: 98.0% on experiment 03
  (Jev 98.5%), 91.7% on experiment 04 (Jev 94.6%), 94.8% on both (Jev 96.5%, Gemini 100%), intervals overlap. It is
  also the best calibrated basal so far (ECE 0.023). basal-1.5 (4.5B) gains 4.5 points over basal-1.0-4.5B (88.8% vs
  84.3% on both sets). basal-1.5-mini is level with basal-1.0-4.5B (85.1% vs 84.3%) at less than half its latency (47 vs 116 ms).
- Rules with numbers stay the weak spot: 45/60 for max, 39/60 for 4.5B, 37/60 for mini on the experiment 04 rules,
  against 49 for Jev and 60 for Gemini.
- `facts: auto` does not close that gap. As sent (rule in the question) it is net zero for 4.5B and max (39 -> 39,
  45 -> 45 of 60; a few items fixed, as many broken) and costs mini 4 of the 60. With the rule moved into the state so the facts code also sees the
  durations, max reaches 50/60 and 4.5B 41/60. Experiment 05's hand-written split + Python arithmetic gave
  basal-1.0-4.5B 59/60.
- SOAM works on the Mac: one request with 5 questions is 2.0 to 2.5 times faster than 5 requests, with the same
  answers (probabilities differ by up to 0.04 in bf16 / 8-bit, the argmax never did).
- Rule change: with the rule edited so that the correct answer flips (message unchanged), basal often follows reading
  changes (a required field added or dropped: max 7/8, 4.5B 4/8, basal-1.0-4.5B 6/8; Jev 8/8) but mostly ignores number
  changes (deadline 14 -> 7 days, threshold 500 -> 600 zł): the answer stays the same on 9 to 11 of 12 such items
  (Jev: 5 of 12). Moving the rule into the state and adding `facts: auto` lifts max to 6/12 there (Jev 7/12).
- On an M5 Max the plain PyTorch MPS forward is faster than the MLX 8-bit ports for mini and 4.5B (4.5B: 114 ms vs
  151 ms median per decision on experiment 03; max: MLX is faster, 245 vs 268 ms); for mini and 4.5B
  `basal-serve --mode mps` is the fastest path (4.5B: 98 ms).

## Setup

**Hardware.** Apple M5 Max, 128 GB unified memory, macOS 26.6.2. Plain PyTorch path: Python 3.12.8, PyTorch 2.14.0
(MPS), transformers 5.17.0 (the repo's `.venv`, as in experiments 01/03/04/05). Engine path: basal v1.5.0 installed
with `uv pip install "basal[mlx] @ https://github.com/rkinas/basal/archive/refs/tags/v1.5.0.tar.gz"` into a separate
environment (PyTorch 2.14.1, transformers 5.17.0, mlx 0.32.3, mlx-lm 0.32.0). Runs between 10:46 and 11:18 UTC.

**Models**

| system | exact id (Hugging Face revision) | used for |
|---|---|---|
| basal-1.5-mini (1.5B) | `Remek/basal-1.5-mini` rev `1978d07`; `Remek/basal-1.5-mini-MLX-8bit` rev `6ea29c4` | all tests; MLX latency |
| basal-1.5 (4.5B) | `Remek/basal-1.5-4.5B` rev `784a683`; `Remek/basal-1.5-4.5B-MLX-8bit` rev `79f5a7c` | all tests; MLX latency; evidence |
| basal-1.5-max (11B) | `Remek/basal-1.5-max` rev `be1b5ee`; `Remek/basal-1.5-max-MLX-8bit` rev `fafde24` | all tests; MLX latency |
| basal-1.0-4.5B, basal-1.0-1.5B | as in experiments 03/04 (rev `b952880`, `81a74ac`) | numbers reused; 1.0-4.5B rerun on the facts and rule-change items |
| Jev 1.13 raw | requested `typesafe/jev-1.13`, served `typesafe/jev-1.13-20260917` | 03/04/05 numbers reused (2026-09-30 / 10-01); rule-change items run today |
| Gemini 3.8 Flash (medium) | as in experiments 03/04 | numbers reused |

**Decision logic (accuracy runs).** `run_basal.py` is the script of experiments 01/03/04 with the v1.5.0 prompt file:
state + question + lettered options, the fixed basal prompt and chat template, assistant turn prefilled with
`{"answer": "`, one forward per option order (original and reversed, batched), softmax over the option letters,
averaged, then each model's own `CALIBRATION.json` temperature for the question type. Simple items are sent with the
option texts only (`option_keys: "hide"`), as `basal-run` does. **Prompt-format changes: none.** basal v1.5.0's
`basal/prompt.py` is byte-identical to the v1.0 file except for its docstring ("the models were trained with", not
"basal-1.0"), and `basal.json` of every 1.5 model says "basal-1.0 (unchanged prompt contract)". The script reproduces
experiment 03's basal-1.0-4.5B probabilities exactly (max difference 0.0 on a 10-item check, `smoke/`).

Per-type temperatures in the 1.5 files: mini noul 1.394 / choice 1.139 / score 1.542; 4.5B 1.782 / 1.278 / 1.756; max
1.542 / 1.498 / 2.059. Shipped confidence thresholds (1% / 5% error targets): mini 0.955 / 0.763, 4.5B 0.962 /
0.765, max 0.947 / 0.729. basal-1.0's were 0.913 / 0.744.

**Item sets** (not changed): experiment 03, 198 clean items (K39 and S14 are disputed there and left out);
experiment 04, 204 items, 60 with explicit rules; experiment 05's 99 rule items (the 60 + the 39 clean completeness
items of experiment 03).

## Main table (both option orders averaged, Wilson 95% intervals)

| system | exp 03 (198) | exp 04 (204) | exp 04 rules (60) | both sets (402) | decided at >= 0.913 / errors | at >= 0.744 / errors | ECE | median ms per decision, Mac (exp 03 / exp 04) |
|---|---|---|---|---|---|---|---|---|
| Gemini 3.8 Flash (medium) | 100.0% [98-100] | 100.0% [98-100] | 60/60 | 100.0% [99-100] | - | - | - | 4,225 / 2,969 (API from Poland, exp 03/04) |
| Jev 1.13, 2 orders | 98.5% [96-99] | 94.6% [91-97] | 49/60 | 96.5% [94-98] | 316 (78.6%) / 0 | 370 (92.0%) / 2 | 0.035 | 584 / 603 (two sequential API calls from Poland, exp 03/04) |
| Jev 1.13, order 1 | 98.0% [95-99] | 94.6% [91-97] | 50/60 | 96.3% [94-98] | 309 (76.9%) / 0 | 369 (91.8%) / 3 | 0.039 | 288 / 295 (API from Poland, exp 03/04) |
| **basal-1.5-max** (11B) | **98.0%** [95-99] | **91.7%** [87-95] | **45/60** | **94.8%** [92-97] | 341 (84.8%) / 5 | 376 (93.5%) / 8 | **0.023** | 268 / 354 (PyTorch); 245 / 291 (MLX 8-bit) |
| **basal-1.5** (4.5B) | 91.9% [87-95] | 85.8% [80-90] | 39/60 | 88.8% [85-92] | 292 (72.6%) / 10 | 359 (89.3%) / 26 | 0.039 | 114 / 152 (PyTorch); 151 / 165 (MLX 8-bit); 98 / 123 (`basal-serve --mode mps`) |
| **basal-1.5-mini** (1.5B) | 88.9% [84-93] | 81.4% [75-86] | 37/60 | 85.1% [81-88] | 232 (57.7%) / 8 | 317 (78.9%) / 33 | 0.054 | 47 / 57 (PyTorch); 52 / 60 (MLX 8-bit); 41 / 49 (`--mode mps`) |
| basal-1.0-4.5B | 86.9% [81-91] | 81.9% [76-87] | 38/60 | 84.3% [80-88] | 251 (62.4%) / 6 | 335 (83.3%) / 35 | 0.059 | 116 / 142 (PyTorch, exp 03/04) |
| basal-1.0-1.5B | 79.3% [73-84] | 77.5% [71-83] | 38/60 | 78.4% [74-82] | 156 (38.8%) / 7 | 252 (62.7%) / 25 | 0.039 | 46 / 57 (PyTorch, exp 03/04) |

0.913 and 0.744 are basal-1.0's frozen thresholds, kept as a common yardstick (they were not fitted for Jev or for
the 1.5 models). With each 1.5 model's own 1% threshold: max decides 313/402 (77.9%) with 3 errors (1.0%, 95%
interval 0.3-2.8), 4.5B 242 (60.2%) with 4 errors (1.7%), mini 184 (45.8%) with 2 errors (1.1%). The release
reports 51.0% / 62.2% / 46.5% coverage at 0.55% / 0.58% / 0.90% error on its own test set.

**What changed from basal-1.0 to 1.5 (paired, same 402 items).** basal-1.5 (4.5B) fixes 29 items basal-1.0-4.5B got
wrong and breaks 11 (net +18). max fixes 50 and breaks 8 (net +42). mini fixes 29 and breaks 26 (net +3, so a
different error profile at the same level).

**Per category (experiment 03).**

| system | reklamacja | routing | eskalacja | kompletnosc | irytacja | phishing | tricky (63) |
|---|---|---|---|---|---|---|---|
| basal-1.0-4.5B | 39/40 | 36/40 | 37/40 | 33/39 | 13/19 | 14/20 | 44 |
| basal-1.5-mini | 38/40 | 39/40 | 37/40 | 27/39 | 17/19 | 18/20 | 46 |
| basal-1.5 (4.5B) | 40/40 | 39/40 | 37/40 | 33/39 | 16/19 | 17/20 | 49 |
| basal-1.5-max | 40/40 | 40/40 | 39/40 | 37/39 | 18/19 | 20/20 | 62 |
| Jev 1.13, 2 orders | 40/40 | 39/40 | 40/40 | 38/39 | 19/19 | 19/20 | 60 |

The two categories that were new in experiment 03 (irritation, phishing) are where 1.5 gains most, together with
routing for the 4.5B model (+3 items each): basal-1.0-4.5B
sent all five of its "slightly irritated" errors to "very irritated"; 1.5-max gets 18/19. Completeness rules do not move for
the 4.5B model (33/39 in both versions); mini gets 27/39, below basal-1.0-4.5B (33) but above basal-1.0-1.5B (23).

**Per domain and type (experiment 04).** max: 17/17 in HR, clinic and logistics, its weakest domain is IT security
(13/17, same as mini). 4.5B: 12/17 in IT security, 13/17 in moderation, 14-16 elsewhere. By type, max scores 82/96
yes/no, 63/65 choice and 42/43 score; 4.5B 73/96, 62/65, 40/43. The yes/no questions are where the rules are, so
that is where the gap to Jev (85/96) and Gemini (96/96) sits. The items max gets wrong with confidence >= 0.913:
ADM03, LAW01, ITS02, ECM04 (all rule items) and K02 (a completeness rule in experiment 03).

**Calibration.** Reliability bins (`analysis_out.txt`): for max, the >= 0.99 bin holds 223 decisions at 100%
accuracy and the 0.95-0.99 bin 87 at 96.6% (mean confidence 0.976). For basal-1.5 (4.5B) the 0.90-0.95 bin is overconfident (41 decisions at
conf 0.930, accuracy 0.805), which accounts for 5 of the 10 errors its 0.913 threshold lets through (the other 5 are at >= 0.95: E34, P15, P18,
ITS02, ITS03). Brier (top option): max 0.037,
4.5B 0.083, mini 0.112, basal-1.0-4.5B 0.107, Jev 0.025.

## Latency on the Mac (median / p90 ms per decision, one question, both option orders, batch size 1)

| model | path | exp 03 | exp 04 | same decision as PyTorch bf16 | accuracy (402) |
|---|---|---|---|---|---|
| basal-1.5-mini | plain PyTorch MPS bf16 (`run_basal.py`) | 47 / 52 | 57 / 65 | reference | 85.1% |
| basal-1.5-mini | `basal-serve --mode mlx`, `-MLX-8bit` | 52 / 54 | 60 / 67 | 402/402 | 85.1% |
| basal-1.5-mini | `basal-serve --mode mps`, bf16 | 41 / 45 | 49 / 57 | 402/402 | 85.1% |
| basal-1.5 (4.5B) | plain PyTorch MPS bf16 | 114 / 131 | 152 / 187 | reference | 88.8% |
| basal-1.5 (4.5B) | `basal-serve --mode mlx`, `-MLX-8bit` | 151 / 159 | 165 / 179 | 398/402 | 88.8% |
| basal-1.5 (4.5B) | `basal-serve --mode mps`, bf16 | 98 / 103 | 123 / 138 | 400/402 | 88.8% |
| basal-1.5-max | plain PyTorch MPS bf16 | 268 / 315 | 354 / 430 | reference | 94.8% |
| basal-1.5-max | `basal-serve --mode mlx`, `-MLX-8bit` | 245 / 255 | 291 / 336 | 400/402 | 94.8% |

- The plain PyTorch numbers are what experiments 01/03/04 measured for basal-1.0 (in-process, no HTTP, two option
  orders batched in one forward). The `basal-serve` numbers are client wall clock over HTTP on localhost, so they
  include the server's JSON handling. The latency pass (`run_latency_pass.sh`) reran the PyTorch runs and got
  identical outputs on 402/402 items per model.
- The 8-bit MLX ports change 0 (mini), 4 (4.5B) and 2 (max) decisions of 402, with the same accuracy. The MLX path is
  the README's recommended Mac engine; on this M5 Max it is not faster than PyTorch for mini and 4.5B. The release
  measured 196 / 587 / 1,360 ms (mini / 4.5B / max, MLX 8-bit) on an M4 Pro.
- basal-1.5-max in bf16 was not too slow: the 402 decisions of experiments 03 + 04 took 2 min 18 s of wall clock
  including model load (11B in bf16 is about 22 GB of the 128 GB).

## facts:auto on the 99 rule items

`"facts": "auto"` makes basal-serve append a block of computed facts to a Polish state (weekdays and days off of the
dates, gaps between dates, date + durations mentioned in the text, VAT and money sums, comparisons as symbols).
`run_basal.py --facts auto` calls the same function (`basal/facts.py` v1.5.0, vendored as `basal_facts.py`) on the
state, which is exactly what the server does with the request. The function reads only the state. In our items the
rule, and with it every duration ("14 dni", "30 dni"), is in the question, so we also ran the rule moved to the end of
the state. 12 of the 99 items stay as they are under "rule in state": HR01-HR04 and INS04 phrase the rule inside the
question without "Reguła", and MFG04, EDU01, ECM01-ECM05 use "Reguła z umowy:", "Reguła regulaminu:" or "Reguła
Ochrony Kupującego:", which our split (on " Reguła:") does not match; for those 7, "rule in state + facts" equals
"+ facts".

| system | condition | exp 04 rules (60) | exp 03 completeness (39) | both (99) | accepted at 0.913 (errors) |
|---|---|---|---|---|---|
| basal-1.5-max | compound (as in exp 03/04) | 45/60 [63-84] | 37/39 | 82.8% [74-89] | 65 (5) |
| basal-1.5-max | + facts:auto | 45/60 [63-84] | 37/39 | 82.8% [74-89] | 63 (3) |
| basal-1.5-max | rule in state | 46/60 [65-86] | 37/39 | 83.8% [75-90] | 62 (4) |
| basal-1.5-max | rule in state + facts:auto | **50/60** [72-91] | 37/39 | **87.9%** [80-93] | 66 (4) |
| basal-1.5 (4.5B) | compound | 39/60 [52-76] | 33/39 | 72.7% [63-81] | 50 (6) |
| basal-1.5 (4.5B) | + facts:auto | 39/60 [52-76] | 33/39 | 72.7% [63-81] | 48 (5) |
| basal-1.5 (4.5B) | rule in state | 37/60 [49-73] | 33/39 | 70.7% [61-79] | 45 (5) |
| basal-1.5 (4.5B) | rule in state + facts:auto | 41/60 [56-79] | 33/39 | 74.7% [65-82] | 45 (2) |
| basal-1.5-mini | compound | 37/60 [49-73] | 27/39 | 64.6% [55-73] | 28 (4) |
| basal-1.5-mini | + facts:auto | 33/60 [42-67] | 28/39 | 61.6% [52-71] | 29 (4) |
| basal-1.5-mini | rule in state | 39/60 [52-76] | 24/39 | 63.6% [54-72] | 26 (4) |
| basal-1.5-mini | rule in state + facts:auto | 35/60 [46-70] | 23/39 | 58.6% [49-68] | 26 (3) |
| basal-1.0-4.5B (control, not trained with facts) | + facts:auto | 39/60 | 33/39 | 72.7% | 20 (1) |
| basal-1.0-4.5B (control) | rule in state + facts:auto | 43/60 | 29/39 | 72.7% | 20 (1) |
| *exp 05:* basal-1.0-4.5B | split into sub-questions, model does arithmetic (A) | 40/60 | 36/39 | 76.8% | 36 (0) |
| *exp 05:* basal-1.0-4.5B | split + Python arithmetic (B) | 59/60 | 36/39 | 96.0% | 74 (0) |
| *exp 05:* Jev 1.13 | compound / B | 49/60 / 60/60 | 38/39 / 39/39 | 87.9% / 100% | 55 (0) / 71 (0) |
| *exp 03/04:* Gemini 3.8 Flash | compound | 60/60 | 39/39 | 100% | - |

The facts block was added to 53 of the 99 states as sent (44 of the 60 experiment-04 items) and to 56 with the rule
in the state. For basal-1.5 (4.5B), facts on the compound question fixed MED02, MED03, BNK05, ECM03 and broke INS01,
BNK03, LOG02, MFG04 (net 0). With the rule in the state the facts block adds 4 items of 60 for max and 4.5B against
the rule-in-state baseline, and costs mini 4 (39 -> 35) but stays far from the hand-built decomposition with code: the block lists
"date + 14 dni = ...", yet the model still has to apply the weekend/holiday shift, pick the right date and compare,
and that is where it fails. **Answer to the key question: no, the built-in facts block does not close the rules gap
without hand-written decompositions;** with the rule in the state it adds 5 items of 60 for max and 2 for 4.5B over the
compound question, net zero when the rule stays in the question, and it costs mini a few items. On the completeness
rules (no arithmetic) facts change nothing for 4.5B and max, as expected.

## SOAM: one request with several questions about one state

12 experiment-03 states (R05, R14, R22, D03, D12, D25, E04, E15, E30, S02, S09, S16), each asked experiment 03's
questions (complaint?, department?, escalate?, irritation?, phishing?) either in one request (5 or 3 questions) or
one request per question; each pattern 5 times, median per state, then median over states. Client wall clock on
localhost.

| model / path | questions | one request | separate requests (sum) | speed-up | same argmax (states) | max abs probability difference |
|---|---|---|---|---|---|---|
| basal-1.5-mini, MLX 8-bit | 5 | 123 ms | 302 ms | 2.46x | 12/12 | 0.041 |
| basal-1.5-mini, MLX 8-bit | 3 | 91 ms | 180 ms | 1.99x | 12/12 | 0.021 |
| basal-1.5 (4.5B), MLX 8-bit | 5 | 367 ms | 785 ms | 2.14x | 12/12 | 0.042 |
| basal-1.5 (4.5B), MLX 8-bit | 3 | 252 ms | 463 ms | 1.84x | 12/12 | 0.025 |
| basal-1.5-mini, `--mode mps` bf16 | 5 | 89 ms | 196 ms | 2.21x | 12/12 | 0.016 |
| basal-1.5-mini, `--mode mps` bf16 | 3 | 62 ms | 120 ms | 1.92x | 12/12 | 0.012 |
| basal-1.5 (4.5B), `--mode mps` bf16 | 5 | 237 ms | 478 ms | 2.02x | 12/12 | 0.023 |
| basal-1.5 (4.5B), `--mode mps` bf16 | 3 | 169 ms | 297 ms | 1.76x | 12/12 | 0.013 |

Every question of every state got the same answer both ways. The probabilities are not bit-identical in bf16 and
8-bit (the release says exact in fp32; we did not run fp32). The release reports 3.0x at 5 questions on an H100; on
the Mac we see 2.0-2.5x.

## Rule change: does the model follow a changed rule without retraining?

20 rule items (8 completeness items of experiment 03, one from each rule template plus one more; 12 experiment-04
rules, one per domain). For each, the rule text in the question was edited so that the correct answer flips (for
example "14 dni" -> "7 dni", "500 zł" -> "600 zł", a required field added or dropped, a conditional made
unconditional); the customer message is byte-identical. 10 flips go yes -> no and 10 no -> yes. The changed versions
and their gold labels were written, checked (`rule_change_check.py`) and blind-verified by a second pass that
recomputed every date and sum (20/20 orig and 20/20 changed agree, `rule_change_truth_check.jsonl`), then committed
in `7d6ef19` before any model saw them. Items were chosen by content without looking at any model output.

| system | condition | original right | changed right | flipped correctly | same answer under both rules |
|---|---|---|---|---|---|
| Jev 1.13, 2 orders | rule in question | 17/20 | 18/20 | **15/20** | 5/20 |
| Jev 1.13, order 1 | rule in question | 17/20 | 17/20 | 14/20 | 6/20 |
| basal-1.5-max | rule in question | 17/20 | 13/20 | 10/20 | 10/20 |
| basal-1.5-max | rule in state | 17/20 | 13/20 | 10/20 | 10/20 |
| basal-1.5-max | rule in state + facts:auto | 19/20 | 14/20 | **13/20** | 7/20 |
| basal-1.5 (4.5B) | rule in question | 12/20 | 13/20 | 5/20 | 15/20 |
| basal-1.5 (4.5B) | rule in state + facts:auto | 14/20 | 14/20 | 8/20 | 12/20 |
| basal-1.5-mini | rule in question | 13/20 | 12/20 | 5/20 | 15/20 |
| basal-1.5-mini | rule in state + facts:auto | 13/20 | 13/20 | 7/20 | 12/20 |
| basal-1.0-4.5B | rule in question | 12/20 | 15/20 | 7/20 | 13/20 |

"Flipped correctly" = right under the original rule and right under the changed rule. "Same answer" = the model gave
the same answer to both versions, i.e. it did not react to the change at all (for basal "rule in state" without facts
see `analysis_out.txt`: 4.5B 6/20, mini 7/20 flipped).

| system | reading rules: completeness (8), flipped / unchanged | number rules: deadline, amount, eligibility (12), flipped / unchanged |
|---|---|---|
| Jev 1.13, 2 orders | 8 / 0 | 7 / 5 |
| basal-1.5-max | 7 / 1 | 3 / 9 |
| basal-1.5-max, rule in state + facts | 7 / 1 | 6 / 6 |
| basal-1.5 (4.5B) | 4 / 4 | 1 / 11 |
| basal-1.5 (4.5B), rule in state + facts | 5 / 3 | 3 / 9 |
| basal-1.5-mini | 4 / 4 | 1 / 11 |
| basal-1.0-4.5B | 6 / 2 | 1 / 11 |

Mean movement of P(yes) towards the new correct answer when the rule changes: Jev +0.62 (all 20 items move the right
way), basal-1.5-max +0.45 (18/20), +0.55 with rule in state + facts (19/20), basal-1.5 (4.5B) +0.28 (median absolute
move 0.10), mini +0.12 (median 0.05). Five number items are hard for everyone: BNK03 (tenure 6 -> 9 months) and ECM04 (dispute window 30 -> 45
days) flip for no system and condition; LOG01 (2nd -> 1st working day) only for mini with rule in state + facts,
EDU03 (income limit) only for mini with rule in state, RE05 (objection deadline 30 -> 21 days) only for max with rule
in state + facts. Jev misses all five, three of them already under the original rule.

**Reading of the LinkedIn question ("what does retraining cost when procedures or prices change?").** For these
models the rule is an input, so a changed rule costs nothing to deploy: edit the text. Whether the decision follows
it is a separate question, and the answer depends on the kind of change. When the change is which fields or
documents are required, basal-1.5-max follows it on 7 of 8 items and Jev on 8 of 8. When the change is a number in a
deadline or threshold, the smaller basal models keep their old answer on 11 of 12 items: they read the case facts
and largely ignore the number in the rule. max with the rule in the state and facts:auto follows 6 of 12, Jev 7 of
12. Number rules belong in code (experiment 05: 59/60 with Python arithmetic), and then a price change is a config
change, not a model question.

**Evidence spans** (basal-1.5 4.5B, `basal-serve --mode mps`, `"evidence": true`, rule moved into the state because
spans point only into the state; HR01 and ECM04 have no "Reguła:" prefix and are left out, n = 18). Under the changed
rule the top span overlaps the changed clause on 8/18 items, and some returned span (up to 3) on 17/18. By kind:
completeness 7/8 for the top span, but these spans are long (median 224 characters) and usually cover most of the
rule list; number rules 1/10: there the top span points at the case facts (dates, amounts) in the message, on 8/10;
BNK03's top span is another clause of the rule, and only EDU03's covers the changed number. Top-span probabilities are low (median 0.13 and 0.05). On the items answered
wrong under the changed rule, the top span was never on the changed clause (0/5). Median request time with evidence was 199 ms
(the same server answered experiment 03's shorter states in 98 ms without evidence; not a like-for-like comparison).

## Caveats

- **Our sets are written cases with model-checked labels.** All items were written by us (experiment 03) or by Claude
  agents following a spec (experiment 04, the rule-change edits), and labels were checked by LLM annotators and agent
  passes, not by humans. Frontier models find most items easy (Gemini 100%); the sets separate small and fast
  systems better than large ones.
- **Not Werdykt.** Remigiusz Kinas's own Werdykt numbers (basal-1.5-max 0.773, basal-1.5 0.721, mini 0.607, Jev
  1.13 0.816, rules category about 0.34 for all basal models) come from a hidden, harder, different set (long
  documents, contracts, RAG, English, abstain) on an H100. Our numbers are higher and not comparable with his.
- **Small n.** 198 + 204 items, 60 rule items, 20 rule-change items. Differences of 1-7 items between max and Jev
  (exp 03: 194 vs 195; both sets: 381 vs 388) are inside the intervals. The rule-change and evidence counts are anecdotes with numbers, not estimates.
- **Thresholds.** 0.913 / 0.744 are basal-1.0's and were not fitted for the 1.5 models or Jev; the 1.5 thresholds
  were certified by the author on descriptions-only prompts and yes/no questions with the bf16 engine. Our noul items
  carry option texts ("Tak, w terminie" / "Nie, po terminie"), not the default yes/no, so the validated case is only
  approximately ours.
- **Reused numbers.** Jev and Gemini on experiments 03/04/05 are the 2026-09-30 / 10-01 runs, not rerun; basal-1.0 is
  deterministic and reproduced exactly. The Jev rule-change runs are from today (served `typesafe/jev-1.13-20260917`).
- **Latency.** Batch size 1, one request at a time, Mac only; no H100. During the first pass another process used the
  GPU, so every latency number reported here comes from a separate pass (`run_latency_pass.sh`) with a watcher that
  logged other model processes every 2 s (`log_gpu_watch.txt`: one 2-second Python import at 11:07:51 UTC, no model
  run). Accuracy runs are deterministic and unaffected.
- **facts:auto variants.** "Rule in state" is our move, not the original item format; for the 12 rule items
  listed in the facts section (and HR01, ECM04 among the rule-change items) it changes nothing.
- **Evidence** is marked experimental by the author; we ran it on one model and 18 items.

## Spend

$0.00175 of usage.cost for 82 Jev calls (80 rule-change calls + 2 in a smoke test; `costs.jsonl`). Budget cap $1.
Everything else ran locally.

## Files

- `run_basal.py` (plain PyTorch MPS readout, `--facts auto`, `--rule-in-state`), `basal_prompt.py` and
  `basal_facts.py` (verbatim copies of `basal/prompt.py` and `basal/facts.py` from basal v1.5.0, Apache-2.0),
  `common.py`, `run_local.sh`, `run_rc.sh`
- `run_serve.py` + `run_serve.sh` (latency, SOAM and evidence against a local `basal-serve`), `run_latency_pass.sh`
- `run_jev.py` (raw Jev on the rule-change items)
- `rule_change_items.jsonl` (20 items, original and changed rule, gold, the changed clause, the computation),
  `rule_change_check.py`, `rule_change_truth_check.jsonl` (blind second pass)
- `raw_<model>_<set>[_condition].jsonl` + `.meta.json`: accuracy runs (`e03`, `e04`, `rules99_facts`, `rules99_ris`,
  `rules99_ris_facts`, `rc_orig`, `rc_changed`, `_ris`, `_ris_facts`); `lat_*.jsonl`: latency pass of the PyTorch
  runs; `raw_serve_<mode>_<model>_<set>.jsonl`: basal-serve runs; `raw_soam_*.json`; `raw_evidence_*.jsonl`;
  `raw_jev-1.13_rc_*.jsonl`
- `analyze.py`, `analysis_out.txt` (every table above and more: reliability bins, per-item errors, per-item
  rule-change table), `results.csv` (one row per system, set, condition and item), `log_*.txt`, `costs.jsonl`,
  `smoke/`

```bash
bash run_local.sh mini 4.5B max 1.0-4.5B      # accuracy + facts runs (repo .venv)
bash run_rc.sh 1.0-4.5B mini 4.5B max         # rule-change runs
python run_jev.py --set rc_orig --out raw_jev-1.13_rc_orig.jsonl
python run_jev.py --set rc_changed --out raw_jev-1.13_rc_changed.jsonl
BASAL_ENV=<basal v1.5.0 env> bash run_latency_pass.sh
python analyze.py > analysis_out.txt
```

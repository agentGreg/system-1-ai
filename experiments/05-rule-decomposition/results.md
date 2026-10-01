Independent evaluation; not affiliated with or endorsed by any model provider. Jev results are a snapshot of the alpha endpoint on 2026-10-01.

# Experiment 05: does splitting a compound rule into simple yes/no questions help fast decision models?

The basal README recommends: compute numbers in code and split composite rules into simple questions. This experiment
tests that on the rule-based items of experiments 03 and 04, for basal-1.0-4.5B, basal-1.0-1.5B and raw Jev 1.13.

**Short answer.** Splitting alone helps a little and not reliably (A). Splitting plus doing the date and amount
arithmetic in Python (B) closes most of the gap: basal-4.5B goes from 71.7% to 96.0% on the 99 items, basal-1.5B from
61.6% to 84.8%, Jev 1.13 from 87.9% to 99/99. B is "fast model + deterministic calculation", not the model alone, and
on 15 of the 60 experiment-04 items B makes no model call at all (every condition there is arithmetic).

## Setup

- **Items.** Block 1: the 60 `rule_based` items of `../04-multi-domain/decisions.jsonl` (12 domains, 56 noul + 4
  choice; all 204 items there are in the clean set). Block 2: the completeness-rule items of
  `../03-extended-set/decisions.jsonl` (category kompletnosc, 7 rule templates A-G) that are in experiment 03's clean
  set: 39 of 40 (K39 is disputed there and left out). `build_items.py` writes `items.jsonl`.
- **Decompositions** (`decompositions.jsonl`, brief in `AUTHORING_BRIEF.txt`). Each rule is split into atomic yes/no
  sub-questions about the state, in the rule's own wording and without item-specific facts, plus a fixed combiner in
  code (AND / OR / IF-THEN / option precedence for the 4 choice items). Each sub-question is marked `read` (is X in the
  text, is the client a natural person, ...) or `arith` (date difference, deadline, weekday/holiday shift, amount
  threshold, count, per-person division, months of experience). Arith sub-questions also carry a Python `calc`
  expression over values copied literally from the state (`values`). Written by the experimenter's side (three
  authoring passes by Claude agents, one per part, from the rule text, without access to any model output) and
  committed and pushed in 4a5a8a3 before any model was run on them.
- **Independent check.** A separate pass (two fresh Claude agents, blind: they saw only the state and the
  sub-question texts, not the gold label, the combiner, the calc or any model output) answered every one of the 394
  sub-questions. `check_decomp.py --truth truth_check.jsonl`: with the true sub-answers, the combiner reproduces the
  gold label on 99/99 items in variant A, and the variant-B calc agrees with the true answer on every arith
  sub-question and reproduces gold on 99/99. No decomposition needed fixing. The checkers flagged one wording point:
  in the deadline-shift pattern ("q1 = posted by day N; q2 = day N falls on a Saturday/Sunday/holiday; q3 = posted by
  the first working day after day N"; combiner `q1 or (q2 and q3)`), q3 read literally is true for ADM03 and EDU01
  even though day N is a normal working day. They answered it literally (as the calc does); the combiner only uses q3
  when q2 is true, so the item label does not change. The true answers are also used below to say which sub-question
  a wrong item failed on.
- **Variant A (pure decomposition):** every sub-question, including the arithmetic ones, goes to the model as a yes/no
  question. **Variant B (decomposition + deterministic arithmetic):** only `read` sub-questions go to the model; arith
  sub-answers are computed in Python from the copied values (and, where a calc needs it, from read sub-answers).
- **Systems.** basal-1.0-4.5B (rev b9528804) and basal-1.0-1.5B (rev 81a74acc), local on an Apple M5 Max (128 GB,
  PyTorch MPS, bf16), same decision logic as experiments 01/03/04 (`run_basal.py`): state + one sub-question, options
  "Tak"/"Nie", both option orders averaged, CALIBRATION.json noul temperature (1.477), no generation. Raw Jev
  `typesafe/jev-1.13` (served `typesafe/jev-1.13-20260917` on every call) via POST
  https://openrouter.ai/api/alpha/decisions, type noul, criteria `{"true": "Tak", "false": "Nie"}`, both orders
  (criteria reversed), all sub-questions of one item and variant in one call (questions dict), client in Poland,
  residential connection, sequential calls (`run_jev.py`). For items without arith sub-questions (all of block 2,
  7 items of block 1) the B request equals the A request and A's call is reused.
- **Baselines** are the compound-question runs of experiments 04 and 03 for the same items (not rerun). Gemini 3.8
  Flash (medium reasoning) on the compound items is the experiment 03/04 reference.
- **Item decision** = combiner over the argmax sub-answers. **Item confidence** = probability of that outcome under
  independent sub-answers, by exact enumeration of all sub-answer combinations (for a pure AND with a "yes" outcome
  this is the product of the sub-answer probabilities); in B, Python-computed sub-answers have probability 1.
- **Spend:** $0.0064 for the whole experiment (Jev 1.13 runs and one multi-question smoke test; `costs.jsonl`).
  Budget cap was $3.

## Decomposition stats

| block | items | sub-questions per item (min / mean / max) | total sub-questions | read | arith | items with >= 1 arith |
|---|---|---|---|---|---|---|
| exp 04 rules | 60 | 1 / 3.65 / 7 | 219 | 112 | 107 | 53 |
| exp 03 completeness | 39 | 2 / 4.49 / 6 | 175 | 175 | 0 | 0 |
| both blocks | 99 | 1 / 3.98 / 7 | 394 | 287 | 107 | 53 |

15 of the 60 block-1 items have only arith sub-questions (ADM01, ADM03, LAW01, HR03, INS01, INS04, LOG01, MFG01,
MFG04, MFG05, EDU01, EDU03, RE01, RE02, RE05): in variant B they are decided by Python alone, with no model call.
Block 2 has no arithmetic, so A and B are the same there.

## Accuracy (95% Wilson intervals)

| system | condition | exp 04 rules (60) | exp 03 completeness (39) | both blocks (99) |
|---|---|---|---|---|
| basal-4.5B | compound question (baseline) | 38/60 = 63.3% [51-74] | 33/39 = 84.6% [70-93] | 71/99 = 71.7% [62-80] |
| basal-4.5B | A: pure decomposition | 40/60 = 66.7% [54-77] | 36/39 = 92.3% [80-97] | 76/99 = 76.8% [68-84] |
| basal-4.5B | B: decomposition + Python arithmetic | 59/60 = 98.3% [91-100] | 36/39 = 92.3% [80-97] | 95/99 = 96.0% [90-98] |
| basal-1.5B | compound question (baseline) | 38/60 = 63.3% [51-74] | 23/39 = 59.0% [43-73] | 61/99 = 61.6% [52-71] |
| basal-1.5B | A: pure decomposition | 34/60 = 56.7% [44-68] | 30/39 = 76.9% [62-87] | 64/99 = 64.6% [55-73] |
| basal-1.5B | B: decomposition + Python arithmetic | 54/60 = 90.0% [80-95] | 30/39 = 76.9% [62-87] | 84/99 = 84.8% [76-91] |
| Jev 1.13 | compound question (baseline) | 49/60 = 81.7% [70-89] | 38/39 = 97.4% [87-100] | 87/99 = 87.9% [80-93] |
| Jev 1.13 | A: pure decomposition | 51/60 = 85.0% [74-92] | 39/39 = 100.0% [91-100] | 90/99 = 90.9% [84-95] |
| Jev 1.13 | B: decomposition + Python arithmetic | 60/60 = 100.0% [94-100] | 39/39 = 100.0% [91-100] | 99/99 = 100.0% [96-100] |
| Gemini 3.8 Flash (medium), reference | compound question (exp 03/04) | 60/60 = 100.0% [94-100] | 39/39 = 100.0% [91-100] | 99/99 = 100.0% [96-100] |

Block 1 without the 15 pure-Python items (45 items where B still needs the model): basal-4.5B 31/45 compound vs 44/45
B; basal-1.5B 29/45 vs 39/45; Jev 1.13 38/45 vs 45/45.

What the arithmetic offloading adds, by sub-question type (every sub-question compared with the blind checker's true
answer, all asked as in variant A):

| system | read sub-questions | arith sub-questions |
|---|---|---|
| basal-4.5B | 279/287 = 97.2% [95-99] | 75/107 = 70.1% [61-78] |
| basal-1.5B | 248/287 = 86.4% [82-90] | 70/107 = 65.4% [56-74] |
| Jev 1.13 | 284/287 = 99.0% [97-100] | 88/107 = 82.2% [74-88] |

The models read the state well; they compare dates and amounts badly. Splitting the rule does not fix the arithmetic,
and a rule with 3-4 arithmetic conditions now has 3-4 chances to fail, which is why A barely moves block 1 (and
basal-1.5B gets worse there, 38 -> 34). Moving those comparisons into code is where the gain comes from. On block 2
(pure reading rules) splitting alone helps: basal-4.5B 33 -> 36/39, basal-1.5B 23 -> 30/39, Jev 38 -> 39/39.

## Latency per item (median ms)

basal: sum of the sequential forwards of the sub-questions the variant sends (each forward = both option orders in
one batch of 2) on the Mac. Jev: wall clock of the order-1 call from Poland, all sub-questions of the item in that
one call. Pure-Python items count as 0 ms model time in B.

| system | condition | exp 04 rules | exp 03 completeness | both blocks |
|---|---|---|---|---|
| basal-4.5B | compound | 143 | 127 | 136 |
| basal-4.5B | A | 425 | 493 | 470 |
| basal-4.5B | B | 179 | 493 | 350 |
| basal-1.5B | compound | 58 | 51 | 55 |
| basal-1.5B | A | 171 | 192 | 185 |
| basal-1.5B | B | 71 | 192 | 135 |
| Jev 1.13 | compound | 298 | 283 | 288 |
| Jev 1.13 | A | 300 | 287 | 294 |
| Jev 1.13 | B | 283 | 287 | 285 |
| Gemini 3.8 Flash (medium) | compound | 3435 | 3529 | 3496 |

For basal the cost is linear in the number of sub-questions because they run one after another; batching all
sub-questions of an item into one forward would cut this, but was not measured. For Jev the questions dict keeps one
round trip per item, and latency stays at the compound level.

## Coverage at confidence >= 0.913 (both blocks, 99 items)

0.913 is basal's frozen CALIBRATION.json threshold for a 1% target error, applied unchanged to all systems.

| system | condition | accepted | errors among accepted | wrong items accepted |
|---|---|---|---|---|
| basal-4.5B | compound | 19/99 | 1 | HR04 |
| basal-4.5B | A | 36/99 | 0 | - |
| basal-4.5B | B | 74/99 (15 of them pure Python) | 0 | - |
| basal-1.5B | compound | 4/99 | 2 | HR04, MFG05 |
| basal-1.5B | A | 22/99 | 4 | HR03, ECM01, K29, K37 |
| basal-1.5B | B | 54/99 (15 pure Python) | 2 | K29, K37 |
| Jev 1.13 | compound | 55/99 | 0 | - |
| Jev 1.13 | A | 39/99 | 0 | - |
| Jev 1.13 | B | 71/99 (15 pure Python) | 0 | - |

For Jev, decomposition A lowers coverage (55 -> 39): multiplying several sub-answer probabilities that are each
below 1 pushes many correct items below 0.913. B recovers it because the arithmetic sub-answers have probability 1. For
basal-1.5B, confident wrong items remain (K29, K37: two read sub-questions misread with high confidence).

## Items that remain wrong

- **basal-4.5B B (4):** RE03 (misreads q1, read), K18 (q2, read), K21 (q4, read), K38 (q4, read). Three of them were
  right as compound questions; all four failures are misreadings of the state, not arithmetic.
- **basal-1.5B B (15):** LAW14, HR04, MED04, LOG04, EDU04, RE03, K08, K15, K18, K21, K24, K29, K32, K33, K37, all on
  read sub-questions. 12 of the 15 were right as compound questions: the small model misreads at least one of 4-6
  reading questions often enough that the AND of them fails.
- **Jev 1.13 B:** none.
- **Variant A** errors are almost all arithmetic sub-questions (deadlines, thresholds, months of experience): see
  `analysis_out.txt` for the per-item list with the failed sub-question.

## Caveats

- **The decompositions are expert prompt engineering.** They were written for these rules by the experimenter's side
  and checked against true answers. A customer would have to do the same work for each of their rules (identify the
  atomic conditions, write the combiner, write and test the date and amount code). The result says the method works
  when that work is done well, not that the models handle compound rules on their own.
- **Variant B's values were copied from the state by the experimenter**, i.e. a perfect extractor of dates and amounts.
  In production they would come from structured form fields or from a separate extraction step, which can fail. On
  15 items B makes no model call at all.
- **Small n.** 60 + 39 items; intervals are wide (e.g. 59/60 has a 95% interval of 91-100%). Block 2 has only 7 rule
  templates, so its sub-questions repeat across items.
- **Same items as the baselines, different runs.** The compound baselines are the experiment 03/04 runs (Jev on
  2026-09-30, basal on the same machine); the decomposed runs are from 2026-10-01. basal is deterministic; Jev is a
  snapshot of an alpha endpoint.
- The independence assumption in the item confidence ignores correlated errors between sub-questions about one state.
- All checking passes (authoring and the blind truth check) were done by Claude agents, not by a human.

## Files

`items.jsonl` (the 99 items), `decompositions.jsonl`, `AUTHORING_BRIEF.txt`, `truth_check.jsonl` (blind true
sub-answers), `decomp.py` (combiner, calc helpers, confidence), `check_decomp.py`, `run_basal.py`, `run_jev.py`,
`analyze.py`, `raw_*.jsonl` + `.meta.json`, `log_*.txt`, `analysis_out.txt`, `results.csv` (one row per system,
condition and item), `costs.jsonl`, `smoke/`.

```bash
python build_items.py
python check_decomp.py --truth truth_check.jsonl
../../.venv/bin/python run_basal.py --model Remek/basal-1.0-4.5B --out raw_basal-4.5B.jsonl
../../.venv/bin/python run_basal.py --model Remek/basal-1.0-1.5B --out raw_basal-1.5B.jsonl
python run_jev.py --out raw_jev-1.13.jsonl
python analyze.py > analysis_out.txt
```

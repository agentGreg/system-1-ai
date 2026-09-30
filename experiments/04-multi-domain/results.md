# Experiment 04: 204 Polish business decisions across 12 domains

> Independent evaluation; not affiliated with or endorsed by any model provider. Jev results are a snapshot of the
> alpha endpoint on 2026-09-30. Raw model outputs are published for evaluation only; do not use them to train,
> fine-tune or distill models.

Date: 2026-09-30. Goal: experiment 03 has 200 items, but almost all of them are customer service. This set asks
the same systems the same kind of typed questions across 12 domains (public administration, law firm intake, HR,
clinic administration, insurance claims, banking/AML, logistics, IT helpdesk and security, manufacturing quality,
university administration, housing community, marketplace moderation), with three question types (yes/no, choice,
ordinal score) and a larger share of explicit rules with dates and thresholds.

## Setup

Protocol, file formats, scoring, annotators and reference systems are those of experiment 03 (same model ids,
revisions and settings). The runs took place on 2026-09-30 between 20:50 and 21:14 UTC (smoke tests from 20:20).

**Hardware (local systems).** Apple M5 Max, 128 GB unified memory, macOS 26.6.2, Python 3.12.8, PyTorch 2.14.0
(MPS), transformers 5.17.0, mlx-lm 0.31.3. **Network (API systems).** Client in Poland, residential connection,
calls to OpenRouter, sequential (one call in flight per system), non-streaming, Python 3.12.2 standard library.
API latency is wall clock on the client and includes the network and provider queueing.

**Systems**

| system | exact id | settings |
|---|---|---|
| basal-1.0-4.5B | `Remek/basal-1.0-4.5B` rev `b952880` | local, bf16 on MPS, both option orders averaged, CALIBRATION.json v1.0.1 temperatures (noul 1.477, choice 1.075, score 1.106) |
| basal-1.0-1.5B | `Remek/basal-1.0-1.5B` rev `81a74ac` | same (noul 1.335, choice 0.958, score 0.958) |
| Jev 1.13 raw | requested `typesafe/jev-1.13`, served `typesafe/jev-1.13-20260917` (all 408 calls) | System One endpoint `/api/alpha/decisions`, one question per call, options sent in canonical and reversed order; single-order (order 1) and two-order average reported |
| Gemini 3.8 Flash | requested and served `google/gemini-3.8-flash` (providers Google, Google AI Studio) | reasoning `{"effort": "medium"}` (median 182 output tokens, almost all reasoning) |
| Mistral Medium 3.1 | requested and served `mistralai/mistral-medium-3.1` (provider Mistral) | no reasoning parameter, answers with one letter |
| Qwen3-14B thinking | `Qwen/Qwen3-14B` rev `40c0698`, MLX 4-bit (same conversion as experiments 01 and 03) | local, thinking on, T=0.6, top_p=0.95, top_k=20, seed 0 (median 290 output tokens) |

**Annotators** (not scored as systems): `anthropic/claude-opus-5.5` and `openai/gpt-6.1-sol`, both with reasoning
effort `high`, both served as requested.

**What changed against experiment 03 (and nothing else did).**
- *Score questions.* basal reads them like any other question (letter readout, both orders, CALIBRATION.json's
  `score` temperature), as `basal-serve` does. The Jev endpoint accepts score criteria only as a list (a keyed
  object returns HTTP 400, see `smoke/jev_score_smoke.json`) and answers with probabilities by list position; order 2
  sends the reversed list and the positions are mapped back. Score prediction = argmax for every system; we also
  report the expected level `sum(i * p_i)` for basal and Jev.
- *Choice keys.* Each choice/score item carries ASCII keys (`keys` in `decisions.jsonl`) used as Jev criteria keys.
- *Prompts.* The chat-LLM and annotator system prompts of experiment 03 said "customer service department". They now
  say "an assistant working in a company or institution" and "operational teams of companies and institutions". The
  user template (state, question, lettered options, "answer only with the letter") and the parsing are unchanged.

## Dataset

`decisions.jsonl` (204 items), built by `build_dataset.py` from `dataset_src/<domain>.py`. The author labels were
committed (`84629b2`) before any annotator or system saw the set.

**How the items were written.** The items were drafted for this experiment with Claude-based coding agents
following `dataset_src/SPEC.txt` (one agent per four domains), then checked by three separate reviewer agents that
answered each item before looking at the label and recomputed every date, weekday, deadline, sum and threshold in
Python. The review found no wrong label; it led to six wording fixes (a Sunday visit date, a debt-register-like
prefix, real top-level domains in e-mail addresses replaced by `.example` / `.test`, a spelled-out phone number, a
missing "today", one scale definition). All people, firms, addresses and identifiers are fictional (PESEL
`00000000000`, accounts `00 0000 ...`, names such as "Jan Testowy", towns such as "Testowo").

| domain | n | noul (yes/no) | choice | score | rule-based | tricky |
|---|---|---|---|---|---|---|
| administracja (public administration) | 17 | 8 (4/4) | 6 | 3 | 5 | 5 |
| kancelaria (law firm intake) | 17 | 8 (4/4) | 6 | 3 | 5 | 5 |
| hr (HR / recruitment) | 17 | 8 (4/4) | 6 | 3 | 5 | 5 |
| przychodnia (clinic administration) | 17 | 8 (4/4) | 6 | 3 | 5 | 5 |
| ubezpieczenia (insurance claims) | 17 | 8 (4/4) | 5 | 4 | 5 | 5 |
| bank_aml (banking, credit, AML) | 17 | 8 (4/4) | 5 | 4 | 5 | 5 |
| logistyka (logistics) | 17 | 8 (4/4) | 5 | 4 | 5 | 5 |
| it_security (IT helpdesk, security) | 17 | 8 (4/4) | 5 | 4 | 5 | 5 |
| produkcja (manufacturing quality) | 17 | 8 (4/4) | 5 | 4 | 5 | 5 |
| uczelnia (university administration) | 17 | 8 (4/4) | 5 | 4 | 5 | 5 |
| wspolnota (housing community) | 17 | 8 (4/4) | 5 | 4 | 5 | 5 |
| moderacja (marketplace moderation) | 17 | 8 (4/4) | 6 | 3 | 5 | 5 |
| **total** | **204** | **96 (48/48)** | **65** | **43** | **60 (29.4%)** | **60 (29.4%)** |

- *Choice* items have 3 to 6 options (mostly 5 or 6); the correct option is spread over all positions (e.g. on
  6-option items 4 or 5 times per position).
- *Score* items have 4 anchored levels, listed from lowest to highest (IT priority as P4 ... P1); gold levels
  9 / 12 / 11 / 11 from lowest to highest. Examples: clinic registration urgency by protocol (the top level means
  "tell the caller to dial 112"; administrative only, no medical advice), incident priority, housing fault urgency,
  severity of a marketplace violation, AML risk.
- *Rule-based* items (56 yes/no, 4 choice) state a rule with 2 to 5 conditions in the question: deadlines counted
  from a stated "today" with explicit counting conventions (including the 2026-11-01 and 2026-11-11 holidays),
  amounts and thresholds ("co najmniej", "nie przekracza", "powyżej"), "chyba że" exceptions and re-test clauses. Many
  sit exactly on a boundary or one day past it. Their yes/no labels are balanced 28 / 28.
- *Tricky* items: surface cues pointing the wrong way (sarcasm, "PILNE!!!" on a trivial request, a harmless use of
  an alarming word, a banned item framed as a keepsake, politeness masking a demand), colloquial and Silesian
  phrasing. States are 119 to 571 characters (median 229).

## Annotation

Each annotator saw only the state, the question (with the rule or scale) and the lettered options, and returned
the letter plus a one-line justification (`annotate.py`, raw output in `ann_*.jsonl`). They did not see the author
label, the flags or each other.

| pair | agreement | Cohen's kappa |
|---|---|---|
| author vs Claude Opus 5.5 | 204/204 (100.0%) | 1.000 |
| author vs GPT-6.1 Sol | 204/204 (100.0%) | 1.000 |
| Claude Opus 5.5 vs GPT-6.1 Sol | 204/204 (100.0%) | 1.000 |
| **all three agree (clean set)** | **204/204 (100.0%)** | |

Kappa is on pooled labels (domain + type + option). Agreement is 100% in every domain, type, rule-based and tricky
slice (`analysis_out.txt`). **Disputed items: 0** (`disputed.md` is empty). Opus 5.5 returned reasoning tokens on
86 items, GPT-6.1 Sol on 76 (median 0 for both).

**How to read 100%.** It says the labels follow from the stated definitions for two frontier models and for the
item authors. It is weaker evidence than in experiment 03: the items were drafted by Claude-based agents and one
annotator is a Claude model, so the author and one annotator share a vendor (the other annotator and all scored
reference models are from other vendors). It is not human verification; a human pass over at least the rule-based
items would be the next step.

## Main results (clean set = all 204 items)

Accuracy with Wilson 95% intervals; cells are correct/n [95% CI in %]. Latency per decision (median, p90). For Jev
two-order the latency is the sum of the two sequential calls (the median of the slower of the two was 319 ms, which
is roughly what parallel calls would take). $ per 1,000 decisions from `usage.cost`.

| system | overall | noul | choice | score | rule-based | not rule-based | tricky | median | p90 | $ / 1,000 |
|---|---|---|---|---|---|---|---|---|---|---|
| Gemini 3.8 Flash, thinking | **100.0%** (204/204) [98.2-100.0] | 96/96 [96-100] | 65/65 [94-100] | 43/43 [92-100] | 60/60 [94-100] | 144/144 [97-100] | 60/60 [94-100] | 2,969 ms | 4,663 ms | 0.983 |
| Qwen3-14B thinking (local) | 96.1% (196/204) [92.5-98.0] | 91/96 [88-98] | 64/65 [92-100] | 41/43 [85-99] | 56/60 [84-97] | 140/144 [93-99] | 57/60 [86-98] | 5,159 ms | 9,615 ms | local |
| Jev 1.13, 2 orders | 94.6% (193/204) [90.6-97.0] | 85/96 [81-93] | 65/65 [94-100] | 43/43 [92-100] | 49/60 [70-89] | 144/144 [97-100] | 56/60 [84-97] | 603 ms | 702 ms | 0.047 |
| Jev 1.13, order 1 only | 94.6% (193/204) [90.6-97.0] | 86/96 [82-94] | 65/65 [94-100] | 42/43 [88-100] | 50/60 [72-91] | 143/144 [96-100] | 57/60 [86-98] | 295 ms | 365 ms | 0.024 |
| Mistral Medium 3.1 | 91.2% (186/204) [86.5-94.3] | 82/96 [77-91] | 63/65 [89-99] | 41/43 [85-99] | 44/60 [61-83] | 142/144 [95-100] | 53/60 [78-94] | 401 ms | 591 ms | 0.139 |
| basal-1.0-4.5B (local) | 81.9% (167/204) [76.0-86.5] | 71/96 [64-82] | 60/65 [83-97] | 36/43 [70-92] | 38/60 [51-74] | 129/144 [84-94] | 49/60 [70-89] | 142 ms | 173 ms | local |
| basal-1.0-1.5B (local) | 77.5% (158/204) [71.2-82.6] | 67/96 [60-78] | 59/65 [81-96] | 32/43 [60-85] | 38/60 [51-74] | 120/144 [76-89] | 42/60 [57-80] | 57 ms | 65 ms | local |

"local" = no API cost; the Mac's hardware and electricity are not counted. For scale, the annotators cost $5.02
(Opus 5.5) and $1.41 (GPT-6.1 Sol) per 1,000 decisions.

**Reading the table.**
- Gemini's interval (98.2-100) does not overlap Jev's (90.6-97.0). This is new against experiment 03, where the
  two were indistinguishable. Qwen and Mistral overlap Jev. basal-4.5B's interval (76.0-86.5) is below Jev, Qwen
  and Mistral and does not overlap them. The intervals are per system, not a paired test.
- **The whole gap is in the rules.** On the 144 items without an explicit rule, Jev gets every item right, Gemini
  too, Mistral 142 and Qwen 140. On the 60 rule-based items: Gemini 60, Qwen 56, Jev 49, Mistral 44, basal-4.5B 38.
  basal-4.5B still has 15 errors outside the rules (90%, [84-94]).
- Against experiment 03: basal-4.5B drops from 86.9% to 81.9%, Jev from 98.5% to 94.6%, Mistral from 96.0% to
  91.2%; Qwen rises from 94.4% to 96.1%; Gemini stays at 100%. The share of items with an explicit rule went up from
  20% (the 40 completeness items) to 29%.
- Jev costs 21 times less than Gemini per decision with two orders (41 times less with one) and is 5 to 10 times
  faster. basal is the only system that answers in about 0.15 s without a network.

## Per-domain accuracy (clean set)

correct/17 per domain [Wilson 95% CI in %].

| domain | basal-4.5B | basal-1.5B | Jev 2-ord | Jev 1-ord | Gemini | Mistral | Qwen3-14B |
|---|---|---|---|---|---|---|---|
| administracja | 15 [66-97] | 15 [66-97] | 16 [73-99] | 16 [73-99] | 17 [82-100] | 16 [73-99] | 15 [66-97] |
| kancelaria | 14 [59-94] | 15 [66-97] | 16 [73-99] | 16 [73-99] | 17 [82-100] | 13 [53-90] | 16 [73-99] |
| hr | 15 [66-97] | 13 [53-90] | 17 [82-100] | 17 [82-100] | 17 [82-100] | 15 [66-97] | 17 [82-100] |
| przychodnia | 14 [59-94] | 15 [66-97] | 16 [73-99] | 16 [73-99] | 17 [82-100] | 17 [82-100] | 16 [73-99] |
| ubezpieczenia | 15 [66-97] | 14 [59-94] | 16 [73-99] | 16 [73-99] | 17 [82-100] | 16 [73-99] | 17 [82-100] |
| bank_aml | 14 [59-94] | 13 [53-90] | 15 [66-97] | 15 [66-97] | 17 [82-100] | 16 [73-99] | 17 [82-100] |
| logistyka | 14 [59-94] | 13 [53-90] | 16 [73-99] | 16 [73-99] | 17 [82-100] | 15 [66-97] | 16 [73-99] |
| it_security | **11** [41-83] | 10 [36-78] | 17 [82-100] | 17 [82-100] | 17 [82-100] | 14 [59-94] | 17 [82-100] |
| produkcja | 15 [66-97] | 13 [53-90] | 16 [73-99] | 17 [82-100] | 17 [82-100] | 16 [73-99] | 16 [73-99] |
| uczelnia | 13 [53-90] | 13 [53-90] | 15 [66-97] | 15 [66-97] | 17 [82-100] | 17 [82-100] | 17 [82-100] |
| wspolnota | 15 [66-97] | 14 [59-94] | 17 [82-100] | 17 [82-100] | 17 [82-100] | 16 [73-99] | 16 [73-99] |
| moderacja | **12** [47-87] | 10 [36-78] | 16 [73-99] | 15 [66-97] | 17 [82-100] | 15 [66-97] | 16 [73-99] |

- With 17 items per domain every interval is wide; no single domain difference is significant. The patterns below
  are descriptive.
- **Jev** is between 15 and 17 in every domain (17/17 in HR, IT security and housing). All 11 of its errors are
  rule-based yes/no items, spread over 9 domains; it misses two each in banking and university administration.
- **basal-4.5B** is weakest in IT security (11/17: three rule items, namely two access requests and an inactive
  account; a polite payment-fraud e-mail from a lookalike domain; two priority levels) and marketplace moderation
  (12/17: a banned item framed as a keepsake, a counterfeit, spelled-out contact data, price bait, a dispute filed on
  day 31). It does not beat Jev in any domain; it beats Mistral only in law intake (14 vs 13) and ties it in HR.
- **Mistral** is weakest in law intake (13/17: all four errors are rule-based deadlines, thresholds and income
  limits) and IT security (14/17).
- Gemini is 17/17 everywhere; Qwen is 15 to 17 everywhere.

## Per type and rule-based (clean set)

| slice | n | basal-4.5B | basal-1.5B | Jev 2-ord | Jev 1-ord | Gemini | Mistral | Qwen3-14B |
|---|---|---|---|---|---|---|---|---|
| noul, rule-based | 56 | 37 [53-77] | 35 [49-74] | 45 [68-89] | 46 [70-90] | 56 [94-100] | 42 [62-84] | 52 [83-97] |
| noul, no rule | 40 | 34 [71-93] | 32 [65-90] | 40 [91-100] | 40 [91-100] | 40 [91-100] | 40 [91-100] | 39 [87-100] |
| choice, rule-based | 4 | 1 | 3 | 4 | 4 | 4 | 2 | 4 |
| choice, no rule | 61 | 59 [89-99] | 56 [82-96] | 61 [94-100] | 61 [94-100] | 61 [94-100] | 61 [94-100] | 60 [91-100] |
| score (none rule-based) | 43 | 36 [70-92] | 32 [60-85] | 43 [92-100] | 42 [88-100] | 43 [92-100] | 41 [85-99] | 41 [85-99] |

**Direction of the rule errors.** On the 56 rule-based yes/no items (28 "Tak" / 28 "Nie"), 10 of Jev's 11 errors
answer "Tak" where the rule gives "Nie"; basal-4.5B makes 13 of its 19 rule errors in the same direction, Mistral 9
of 14. Qwen errs the other way (3 of 4 "Nie"). In 8 of Jev's 10 cases "Tak" means "the rule is satisfied" (in time,
meets the criteria, may be released, covered) while one condition fails; in the other two (LAW02, INS06) "Tak" is a
flag (time-barred, send to fraud review) that the rule does not trigger. So this is a lean towards "Tak" more than
towards leniency.

**Score items: exact accuracy and mean absolute error (levels)**

| system | exact | MAE (argmax) | MAE (expected level) | off by 2+ levels |
|---|---|---|---|---|
| Gemini 3.8 Flash | 43/43 | 0.000 | - | 0 |
| Jev 1.13, 2 orders | 43/43 | 0.000 | 0.050 | 0 |
| Jev 1.13, order 1 | 42/43 | 0.047 | - | 1 |
| Qwen3-14B thinking | 41/43 | 0.047 | - | 0 |
| Mistral Medium 3.1 | 41/43 | 0.093 | - | 1 |
| basal-1.0-4.5B | 36/43 | 0.209 | 0.260 | 1 |
| basal-1.0-1.5B | 32/43 | 0.419 | 0.460 | 4 |

basal-4.5B's score errors are mostly one level off; its one larger miss is MED17, three levels off (see errors).

## Confidence: coverage at the frozen thresholds

basal-4.5B's `CALIBRATION.json` thresholds (fixed on basal's own calibration data): confidence >= 0.913 (target 1%
error) and >= 0.744 (target 5%), applied as in experiment 03 to all basal and Jev variants (**not fitted for Jev,
nor for basal-1.5B**, whose own thresholds differ). basal's confidence is the calibrated two-order probability;
Jev two-order uses the top probability of the averaged distribution; Jev order 1 uses the `confidence` field where
the endpoint returns one (choice, score) and the top probability for noul.

| system | threshold | decided alone | error among decided [95% CI] | sent to a human | of the system's errors, caught |
|---|---|---|---|---|---|
| basal-1.0-4.5B | 0.913 | 118/204 (57.8%) | 4 (3.4%) [1.3-8.4] | 86 | 33 of 37 |
| basal-1.0-4.5B | 0.744 | 158/204 (77.5%) | 19 (12.0%) [7.8-18.0] | 46 | 18 of 37 |
| basal-1.0-1.5B | 0.913 | 89/204 (43.6%) | 5 (5.6%) [2.4-12.5] | 115 | 41 of 46 |
| basal-1.0-1.5B | 0.744 | 125/204 (61.3%) | 17 (13.6%) [8.7-20.7] | 79 | 29 of 46 |
| Jev 1.13, 2 orders | 0.913 | 157/204 (77.0%) | 0 (0.0%) [0.0-2.4] | 47 | 11 of 11 |
| Jev 1.13, 2 orders | 0.744 | 183/204 (89.7%) | 2 (1.1%) [0.3-3.9] | 21 | 9 of 11 |
| Jev 1.13, order 1 | 0.913 | 155/204 (76.0%) | 0 (0.0%) [0.0-2.4] | 49 | 11 of 11 |
| Jev 1.13, order 1 | 0.744 | 183/204 (89.7%) | 3 (1.6%) [0.6-4.7] | 21 | 8 of 11 |

- basal-4.5B at the strict threshold decides 57.8% alone (in line with its published 58.6%), but at 3.4% observed
  error, above the 1% target (in experiment 03 it was 1.5%). The four confident errors are HR04, ITS14, EDU15 and
  ECM07 (see below). At 0.744 its error among automatic decisions is 12.0%, far above the 5% target.
- **On rule-based items basal knows that it does not know:** at 0.913 it decides only 5 of the 60 alone (1 wrong,
  HR04) and sends 55 to a person. Jev decides 24 of the 60 alone, all correct, and 133 of the 144 others, all
  correct.
- Jev's 11 errors all sit at 0.52 to 0.81 (two-order), so the strict threshold catches every one of them.

## Calibration (clean set)

Top-option probability vs observed accuracy (all bins in `analysis_out.txt`):

| system | mean confidence | accuracy | ECE | Brier (top option) | pattern |
|---|---|---|---|---|---|
| basal-1.0-4.5B | 0.869 | 0.819 | 0.078 | 0.125 | overconfident between 0.8 and 0.95 (0.8-0.9: conf 0.849, acc 0.609; 0.9-0.95: conf 0.929, acc 0.737); well calibrated above 0.95 (101 items, 100 correct) |
| basal-1.0-1.5B | 0.800 | 0.775 | 0.054 | 0.148 | overconfident at 0.8-0.9 (conf 0.839, acc 0.571), close elsewhere |
| Jev 1.13, 2 orders | 0.927 | 0.946 | 0.033 | 0.035 | underconfident above 0.8 (0.8-0.9: conf 0.847, acc 0.944; every one of the 161 items at >= 0.9 correct); slightly overconfident below 0.8 (25 items) |
| Jev 1.13, order 1 | 0.923 | 0.946 | 0.029 | 0.036 | same |

The pattern of experiment 03 holds on a different set: basal-4.5B is overconfident in the 0.8 to 0.95 band, which
is what lets errors through its thresholds; Jev is underconfident at the top, which costs only extra human work.
Bins have 8 to 92 items; the lower bins are coarse.

**Order sensitivity (all 204).** The two option orders disagree on 11 items for basal-4.5B, 17 for basal-1.5B, 2
for Jev (MFG02, ECM16). Averaging the orders changed clean accuracy by 0 items for basal-4.5B (167 either way), -1
for basal-1.5B (159 order 1 only, 158 averaged) and 0 for Jev (193).

## The 10 most informative errors (clean set)

1. **ADM03** (administration, deadline) Discharged from hospital on Monday 2026-10-05, 7 days counted from the next
   day, so the last day was Monday 10-12; the request came on Tuesday 10-13, one day late. Missed by 5 of the 7
   systems (both basal, Jev at 0.77, Mistral, Qwen). Only Gemini (and both annotators) counted it right.
2. **The lean towards "Tak" on rules.** Jev's errors ADM03, LAW02, MED03, INS06, BNK04, BNK05, LOG01, EDU01, EDU03 and
   ECM04 all answer "Tak" where one condition decides "Nie": a request one day late (ADM03, EDU01), a limitation
   period that runs to the end of the year (LAW02), a son who turned 18 in March (MED03), one fraud signal where two
   are needed (INS06), a chargeback filed 28 days after the purchase where 30 are required (BNK05), a parcel on time
   because 11 November is a holiday (LOG01), 1,537.50 zł per person against a 1,500 zł limit (EDU03), a dispute on day
   31 (ECM04). The same lean accounts for most of basal's and Mistral's rule errors. Below the strict threshold, a
   fast system's "Tak" on a rule question is the answer to double-check.
3. **BNK04** (credit criteria) Self-employed since 2025-12-01, applying on 2026-10-20: less than the required 12
   months of business. Five earlier years on a salaried job are the distractor. basal-4.5B, basal-1.5B and Jev (0.60)
   said the criteria are met; Mistral and Qwen caught it.
4. **HR04** (escalation policy) A leave-balance question that mentions, in passing, a sprained ankle on a wet
   warehouse floor "but it's fine now". The policy escalates any injury at work. basal-4.5B said "no" at p=0.95,
   basal-1.5B at 0.93, both above the strict threshold. Jev, Mistral, Qwen and Gemini escalated.
5. **ITS14** (IT priority) "PILNE!!!" for a second monitor while the current setup works: P4 by the anchors.
   basal-4.5B chose P3 at 0.96 (a confident error) and Mistral P3; Jev chose P4 but only at 0.53.
6. **ECM07** (moderation) 9 mm ammunition listed as "a keepsake from grandpa, collector's box". Banned by the stated
   rule. basal-4.5B said allowed at 0.93; every other system flagged it.
7. **EDU15** (student request urgency) Deadline in 3 days: level 3 of 4 by the anchors ("2 to 7 days"). basal-4.5B
   and basal-1.5B chose level 4 ("today or tomorrow"), 4.5B at 0.94. Counting days inside a scale definition.
8. **MED17** (clinic registration protocol) A calm caller asks for a same-day GP slot for her husband, who has been
   slurring his speech and cannot lift his right arm for 20 minutes. The protocol's alarm list makes it level 4
   ("tell the caller to dial 112"). basal-4.5B chose level 1, "administrative" (p=0.47), basal-1.5B level 3. The low
   confidence would have sent it to a person at either threshold; Jev (1.00), Mistral, Qwen and Gemini chose level 4.
   The calm tone is the trap, and this is the kind of item where a confident error would be costly.
9. **MFG02** (quality hold) The technologist suggests releasing the batch after a CMM re-measure, but piece 14 is
   still 25.055 mm against a 25.05 limit, so two pieces remain out of tolerance and the batch must be held. Jev (0.54,
   the orders disagree) and Mistral released it; both basal models and Qwen held it. Jev's only error in the "no"
   direction.
10. **RE07** (housing, sarcasm) "Congratulations, the intercom has worked brilliantly for a week: nobody can reach me
    and the courier left with my parcel for the third time." A fault report. basal-4.5B (0.80), basal-1.5B (0.97,
    above the strict threshold) and Qwen said it is not one; Jev (0.81), Mistral and Gemini read the sarcasm.

Other errors worth a look in `analysis_out.txt`: LOG15 (15 stuck parcels of one sender = "more than 10", level 3;
basal-4.5B level 2 at 0.91, Qwen level 2), ECM14 ("1:1 quality with the original" = counterfeit; basal-4.5B and Qwen
"no violation"), ITS02 (a contractor with an active NDA meets condition 3, but the access expires 35 days out;
both basal models and Mistral approved it). Gemini made no error. Qwen's 8 errors: ADM01, ADM03, LAW01, MFG04
(deadline arithmetic, three of them around a Saturday or the 11 November holiday), MED15, LOG15, RE07, ECM14.

## Spend

Total `usage.cost` for everything in this experiment, smoke tests included: **$1.57** of the $15 cap (annotators
$1.31, Gemini $0.20, Mistral $0.03, Jev $0.010 for 442 calls including a 17-item smoke run, other smoke tests
$0.02). Per-call log: `costs.jsonl`.

## Caveats

- **Circularity, stronger than in experiment 03.** The items were drafted and reviewed by Claude-based agents, one
  annotator is Claude Opus 5.5, and the 100% three-way agreement means the labels are consistent with the stated
  definitions for frontier LLMs, not that humans checked them. No author label was changed after any model output
  was seen. A human review, starting with the 60 rule-based items, is the most useful next step.
- **Easy for frontier models.** Gemini is at 100% and all annotators agree on everything. Like experiment 03, this set
  separates small and fast systems better than frontier ones; it says nothing about differences between Gemini and
  larger models.
- **17 items per domain.** Per-domain numbers are descriptive; intervals span 30 to 40 points. Per-type and
  rule-based slices are larger (43 to 144) but the choice rule-based slice has only 4 items.
- **Written items, not traffic.** States are short (median 229 characters) and each has one clear answer by
  construction. Real documents are longer and messier.
- **Thresholds.** basal-4.5B's thresholds were fitted for basal-4.5B on its own data; for basal-1.5B and Jev they are
  only a common yardstick. Jev's probabilities come rounded to two decimals, and for score and choice its reported
  `confidence` is not always the top probability (5 of 108 order-1 answers differ by more than 0.05, e.g. ECM16:
  confidence 0 with a top probability of 0.49), which affects only the "order 1" coverage and calibration rows.
- **Score in reversed order.** Reversing a score scale for the second order is how basal-serve averages; for Jev it
  means the level list arrives high-to-low in order 2. The two Jev orders disagreed on one score item (ECM16).
- **Prompts.** One system-prompt word change against experiment 03 (see Setup). Chat LLMs got one prompt in the
  original option order, provider-default temperature, one run each.
- **Latency is not like for like.** basal and Qwen run on a laptop (basal as eager PyTorch bf16); API numbers include
  the Poland to OpenRouter network. Jev two-order latency is two sequential calls. Batch size 1 everywhere. The API
  systems ran concurrently with each other; basal-4.5B overlapped with the API runs (network only), and Qwen
  overlapped with the end of the Gemini run.
- **Jev endpoint is alpha.** Results are a snapshot of `typesafe/jev-1.13-20260917` on 2026-09-30.
- **One run per system**, no repeats.

## Files

- `decisions.jsonl` (204 items: id, domain, type, rule_based, tricky, state, question, options, keys, gold =
  author label, author_gold); `build_dataset.py` builds it from `dataset_src/<domain>.py`; `dataset_src/SPEC.txt` is
  the authoring spec
- `annotate.py`, `ann_opus-5.5.jsonl`, `ann_gpt-6.1-sol.jsonl` (+ `.meta.json`): annotations with justifications and
  reasoning text where returned
- `disputed.md`: disputed items for adjudication (none in this run)
- `run_basal.py`, `basal_prompt.py`, `run_llm.py`, `run_jev.py`, `run_cloud.py`, `common.py`, `analyze.py`
- `raw_*.jsonl` + `raw_*.meta.json`: per-item raw outputs per system (basal and Jev: both per-order distributions;
  Jev: full API responses; chat LLMs: full text and reasoning where returned)
- `results.csv`: one row per system (and annotator) and item, with domain, type, rule_based, tricky and `clean`
- `analysis_out.txt`: full output of `analyze.py`; `costs.jsonl`: every paid call's cost; `log_*.txt`: console logs;
  `smoke/`: smoke-test outputs (including the Jev score-format check)

Run: `python3 build_dataset.py`; API scripts with the system Python 3 (standard library only; the keychain entry
`openrouter-api-key`), e.g. `python3 run_jev.py --out raw_jev-1.13.jsonl`; local scripts with the repo venv, e.g.
`../../.venv/bin/python run_basal.py --model Remek/basal-1.0-4.5B --out raw_basal-4.5B.jsonl`; then
`python3 analyze.py > analysis_out.txt`.

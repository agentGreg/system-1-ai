# Experiment 03: an extended, independently checked set of 200 Polish business decisions

> Jev results come from the alpha endpoint https://openrouter.ai/api/alpha/decisions (`typesafe/jev-1.13`) and are a
> snapshot as of 2026-09-30; this repo is independent and not affiliated with or endorsed by TypeSafe AI, OpenRouter
> or any other model provider. Raw model outputs are published for evaluation only; do not use them to train,
> fine-tune or distill models.

Date: 2026-09-30. Goal: turn the 30-item demo of experiment 01 into a benchmark a business reader can trust: 200
Polish customer-service / back-office decisions, labels checked by two independent annotators, several systems.

## Setup

**Hardware (local systems).** Apple M5 Max, 128 GB unified memory, macOS 26.6.2, Python 3.12.8, PyTorch 2.14.0
(MPS), transformers 5.17.0, mlx-lm 0.31.3. **Network (API systems).** Client in Poland, residential connection, calls
to OpenRouter, sequential (one call in flight per system), non-streaming. API latency is wall clock on the client
and includes the network and provider queueing. Runs took place between 19:45 and 20:15 UTC.

**Systems**

| system | exact id | settings |
|---|---|---|
| basal-1.0-4.5B | `Remek/basal-1.0-4.5B` rev `b952880` | local, bf16 on MPS, both option orders averaged, CALIBRATION.json v1.0.1 temperatures (noul 1.477, choice 1.075). `run_basal.py` is experiment 01's script unchanged |
| basal-1.0-1.5B | `Remek/basal-1.0-1.5B` rev `81a74ac` | same (noul 1.335, choice 0.958) |
| Jev 1.13 raw | requested `typesafe/jev-1.13`, served `typesafe/jev-1.13-20260917` (all 400 calls) | System One endpoint `/api/alpha/decisions`, one question per call, criteria sent in canonical and reversed order; reported both single-order (order 1) and the two-order average |
| Gemini 3.8 Flash | requested and served `google/gemini-3.8-flash` (providers Google, Google AI Studio) | reasoning `{"effort": "medium"}` (median 181 output tokens, almost all reasoning) |
| Mistral Medium 3.1 | requested and served `mistralai/mistral-medium-3.1` (provider Mistral) | no reasoning parameter, answers with one letter |
| Qwen3-14B thinking | `Qwen/Qwen3-14B` rev `40c0698`, MLX 4-bit (same conversion as experiment 01) | local, thinking on, experiment 01's `run_llm.py` unchanged (T=0.6, top_p=0.95, top_k=20, seed 0) |

The chat LLMs (Gemini, Mistral, Qwen) get experiment 01's prompt verbatim (state, question, lettered options in the
original order, "answer only with the letter"). Temperature was not sent to the API models (provider default).
Every generation finished normally and every answer was parsable. No API call failed or needed a retry.

**Annotators** (not scored as systems): `anthropic/claude-opus-5.5` with reasoning effort `high` and
`openai/gpt-6.1-sol` with reasoning effort `high`, both served as requested. The reference LLMs above were chosen
from other vendors (Google, Mistral, Alibaba) to limit circularity.

## Dataset

`decisions.jsonl`, built by `build_dataset.py`. The 30 items of experiment 01 are included unchanged (same ids,
text and labels); 170 items are new. All were written by us; the new company and brand names are fictional. The
author labels were committed (`4a0d08b`) before any annotator or system saw the full set.

| category | type | n | new | label balance | tricky |
|---|---|---|---|---|---|
| reklamacja: is it a complaint? | noul | 40 | 30 | 20 yes / 20 no | 13 |
| routing to 5 departments (same options as exp 01) | choice | 40 | 30 | 8 per department | 11 |
| eskalacja: hand over to a human now? | noul | 40 | 35 | 20 / 20 | 10 |
| kompletnosc: complete under a stated rule | noul | 40 | 35 | 19 complete / 21 not | 15 |
| irytacja: calm / slightly / very irritated (new) | choice | 20 | 20 | 7 / 7 / 6 | 6 |
| phishing: scam or phishing aimed at the company or its customer? (new) | noul | 20 | 20 | 10 / 10 | 8 |
| **total** | | **200** | **170** | | **63 (31.5%)** |

The completeness items use seven different rules (2 to 5 conditions, most with a conditional requirement:
account number only for a refund, other driver's plate only if another driver caused the damage, proof of NIP only
if the NIP is wrong, error text only if an error was shown, no account number if paid by card). The texts include
typos, missing diacritics, sarcasm, politeness masking a complaint, mixed intents, Silesian and colloquial
phrasing, and English-Polish code-switching. Messages are 1 to 5 sentences.

## Annotation

Each annotator saw only the message, the question (with the rule) and the lettered options, and returned the
letter plus a one-line justification (`annotate.py`, raw output in `ann_*.jsonl`). They did not see the author
label, the `tricky` flag or each other.

| pair | agreement | Cohen's kappa |
|---|---|---|
| author vs Claude Opus 5.5 | 199/200 (99.5%) | 0.995 |
| author vs GPT-6.1 Sol | 198/200 (99.0%) | 0.989 |
| Claude Opus 5.5 vs GPT-6.1 Sol | 199/200 (99.5%) | 0.995 |
| **all three agree (clean set)** | **198/200 (99.0%)** | |

Kappa is computed on the pooled labels (category + option). Per category, all three agree on every item except one
completeness item and one irritation item. All 63 tricky items and all 30 original items are in the clean set.

**Disputed (2 items, `disputed.md`, awaiting Greg's adjudication; author labels unchanged):**
- **K39**: rule requires "the name of the system or application"; the message says "program pocztowy" (e-mail
  program). Author: complete. Both annotators: incomplete, because a generic "e-mail program" is not a name. This is
  most likely our mistake: the draft said "Outlook" and we replaced it with a generic term when removing brand names.
- **S14**: "Czekam na odpowiedź od tygodnia. Czy ktoś w ogóle czyta te maile?" Author and Opus: slightly irritated.
  GPT-6.1 Sol: very irritated. A real boundary case of a 3-level scale.

**What the agreement does and does not show.** It says the labels are unambiguous to two frontier LLMs and to us.
It does not replace human annotators: the annotators are LLMs too, so a system that "thinks like an LLM" can look
better than it is (circularity). That is why the clean set also requires the author label, why the two annotator
models are not among the scored systems, and why the two disputed items wait for a human. It also shows that for
frontier models most of these items are easy (see below), so this set separates small and fast systems better than
it separates frontier ones.

## Main results (clean set, n = 198)

Accuracy with Wilson 95% intervals; per-category cells are correct/n [95% CI in %]. Latency per decision (median,
p90). For Jev two-order the latency is the sum of the two sequential calls (sending them in parallel would be close
to one call: median of the slower of the two was 306 ms). $ per 1,000 decisions from `usage.cost` on all 200 items.

| system | overall | reklamacja | routing | eskalacja | kompletnosc | irytacja | phishing | tricky | median | p90 | $ / 1,000 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Gemini 3.8 Flash, thinking | **100.0%** (198/198) [98.1-100] | 40/40 [91-100] | 40/40 [91-100] | 40/40 [91-100] | 39/39 [91-100] | 19/19 [83-100] | 20/20 [84-100] | 63/63 | 4,225 ms | 11,958 ms | 0.909 |
| Jev 1.13, 2 orders | **98.5%** (195/198) [95.6-99.5] | 40/40 [91-100] | 39/40 [87-100] | 40/40 [91-100] | 38/39 [87-100] | 19/19 [83-100] | 19/20 [76-99] | 60/63 | 584 ms | 677 ms | 0.038 |
| Jev 1.13, order 1 only | 98.0% (194/198) [94.9-99.2] | 40/40 [91-100] | 39/40 [87-100] | 40/40 [91-100] | 38/39 [87-100] | 19/19 [83-100] | 18/20 [70-97] | 59/63 | 288 ms | 362 ms | 0.019 |
| Mistral Medium 3.1 | 96.0% (190/198) [92.2-97.9] | 40/40 [91-100] | 40/40 [91-100] | 37/40 [80-97] | 35/39 [76-96] | 19/19 [83-100] | 19/20 [76-99] | 58/63 | 396 ms | 563 ms | 0.099 |
| Qwen3-14B thinking (local) | 94.4% (187/198) [90.3-96.9] | 40/40 [91-100] | 38/40 [83-99] | 39/40 [87-100] | 39/39 [91-100] | 16/19 [62-94] | 15/20 [53-89] | 56/63 | 4,136 ms | 6,365 ms | local |
| basal-1.0-4.5B (local) | 86.9% (172/198) [81.5-90.9] | 39/40 [87-100] | 36/40 [77-96] | 37/40 [80-97] | 33/39 [70-93] | 13/19 [46-85] | 14/20 [48-85] | 44/63 | 116 ms | 131 ms | local |
| basal-1.0-1.5B (local) | 79.3% (157/198) [73.1-84.4] | 32/40 [65-90] | 38/40 [83-99] | 38/40 [83-99] | 23/39 [43-73] | 12/19 [41-81] | 14/20 [48-85] | 41/63 | 46 ms | 52 ms | local |

"local" = no API cost; the Mac's hardware and electricity are not counted. For scale, the two annotators cost
$4.12 (Opus 5.5) and $1.20 (GPT-6.1 Sol) per 1,000 decisions.

On all 200 items (clean + disputed) the order is the same: Gemini 99.0%, Jev 2-order 98.0%, Jev order-1 97.5%,
Mistral 95.5%, Qwen 94.0%, basal-4.5B 86.5%, basal-1.5B 79.0% (full table in `analysis_out.txt`).

**Reading the table.** Gemini, Jev and Mistral are statistically indistinguishable from each other on this set
(overlapping intervals). Jev costs 24 times less than Gemini per decision with two orders (48 times less with one)
and is 7 to 15 times faster (one or two short calls vs thinking). basal-4.5B is below Gemini, Jev and Mistral with
non-overlapping intervals (its upper bound is 90.9%, Mistral's lower bound 92.2%, Jev's 95.6%); against Qwen the
intervals touch (Qwen's lower bound 90.3%). basal is the only system here that answers in about 0.1 s without a
network. basal's weak spots
are the two new categories and the completeness rules, not the classic complaint and escalation questions.

## Original 30 items (continuity with experiment 01)

| system | exp 01 result | exp 03 run |
|---|---|---|
| basal-1.0-4.5B | 27/30 | 27/30 (same 3 errors: D07, K02, K03) |
| basal-1.0-1.5B | 27/30 | 27/30 |
| Qwen3-14B thinking | 29/30 | 29/30 |
| Jev 1.13 (both variants) | not run | 30/30 |
| Gemini 3.8 Flash thinking | not run | 30/30 |
| Mistral Medium 3.1 | not run | 29/30 |

All 30 original items are in the clean set, including **D07** (router Wi-Fi 7 question), which experiment 01 called
debatable: both annotators chose Sales, like our label, with the justification "a pre-purchase question about an
offered product". So D07 now counts as a real error for basal-4.5B and Qwen, but it remains the kind of item a
second human might label differently.

## Confidence: coverage at the frozen thresholds

basal ships two thresholds in `CALIBRATION.json` (fixed on basal's calibration data): confidence >= 0.913 (target
1% error) and >= 0.744 (target 5%). Decisions above the threshold are taken automatically, the rest go to a person.
We apply the same numbers to Jev for comparison, although **they were not fitted for Jev**. basal's confidence is
the calibrated two-order probability; Jev's is the top probability of the two-order average (Jev reports noul as
P(yes) with two decimals; for choice questions it also reports a `confidence` field, which we use for order 1).

| system | threshold | decided alone | error among decided [95% CI] | sent to a human | of the system's errors, caught |
|---|---|---|---|---|---|
| basal-1.0-4.5B | 0.913 | 133/198 (67.2%) | 2 (1.5%) [0.4-5.3] | 65 | 24 of 26 |
| basal-1.0-4.5B | 0.744 | 177/198 (89.4%) | 16 (9.0%) [5.6-14.2] | 21 | 10 of 26 |
| basal-1.0-1.5B | 0.913 | 67/198 (33.8%) | 2 (3.0%) [0.8-10.2] | 131 | 39 of 41 |
| basal-1.0-1.5B | 0.744 | 127/198 (64.1%) | 8 (6.3%) [3.2-11.9] | 71 | 33 of 41 |
| Jev 1.13, 2 orders | 0.913 | 159/198 (80.3%) | 0 (0.0%) [0.0-2.4] | 39 | 3 of 3 |
| Jev 1.13, 2 orders | 0.744 | 187/198 (94.4%) | 0 (0.0%) [0.0-2.0] | 11 | 3 of 3 |
| Jev 1.13, order 1 | 0.913 | 154/198 (77.8%) | 0 (0.0%) [0.0-2.4] | 44 | 4 of 4 |
| Jev 1.13, order 1 | 0.744 | 186/198 (93.9%) | 0 (0.0%) [0.0-2.0] | 12 | 4 of 4 |

At the strict threshold basal-4.5B handles two thirds of the set alone at 1.5% observed error, which is in line with
its published figures (58.6% at 1.2% on its own test data). The two confident errors are **S13** (polite but
irritated, predicted "very irritated", p=0.93) and **P18** (a customer asking whether an SMS is really from us,
predicted phishing, p=0.94). At 0.744 basal-4.5B's error among automatic decisions is 9.0%, above the 5% target.
Jev decides more items alone and none of its automatic decisions is wrong; all of its errors sit near 0.5.

## Calibration (clean set)

Top-option probability vs observed accuracy (`analysis_out.txt` has all bins):

| system | mean confidence | accuracy | ECE | Brier (top option) | pattern |
|---|---|---|---|---|---|
| basal-1.0-4.5B | 0.907 | 0.869 | 0.052 | 0.088 | overconfident in the 0.5-0.9 range (e.g. bin 0.8-0.9: conf 0.855, acc 0.679); well calibrated above 0.9 (0.9-0.95: 0.931 vs 0.930; >= 0.95: 97 items, all correct) |
| basal-1.0-1.5B | 0.803 | 0.793 | 0.088 | 0.122 | overconfident at 0.5-0.6 (conf 0.558, acc 0.333), mixed above |
| Jev 1.13, 2 orders | 0.934 | 0.985 | 0.051 | 0.015 | underconfident: every item above 0.7 (178) is correct, bins 0.8-0.95 have conf 0.87-0.93 and acc 1.00 |
| Jev 1.13, order 1 | 0.932 | 0.980 | 0.055 | 0.016 | same |

Similar ECE, opposite direction: basal-4.5B says 85% when it is right about 68% of the time in that range, Jev says
87-93% when it is right every time. For routing to a human, underconfidence costs only extra human work;
overconfidence in the middle range is what lets errors through at the 0.744 threshold. With 198 items and few errors,
these bins are coarse (several bins have fewer than 15 items).

**Order sensitivity (all 200).** The two option orders disagree on 6 items for basal-4.5B, 19 for basal-1.5B, 2 for
Jev. Averaging the orders changed accuracy on the clean set by 0 items for basal-4.5B (172 either way), +1 for
basal-1.5B and +1 for Jev.

## The 10 most informative errors (clean set)

1. **D22** "halo, płace blikiem i ciągle wywala błąd transakcji, kasa się blokuje a zamówienie nie przechodzi". Label
   and both annotators: invoices and payments. Tech support from basal-4.5B, basal-1.5B, Jev (0.60/0.40 in one order,
   0.49/0.51 in the other) and Qwen. The most-missed item: an error message about a payment pulls systems toward
   "technical".
2. **P18** A customer asks whether a "pay the shortfall" SMS is really from us and says they did not click. Not a scam
   (the message itself is an honest question). Flagged as phishing by basal-4.5B (p=0.94, above the strict
   threshold), Qwen, Mistral and Jev order 1 (0.50). Systems react to the topic of the message, not to what the
   message does.
3. **K22** Car damage report where the driver hit a post himself. The rule asks for the other driver's plate only if
   another driver caused the damage, so the report is complete. Jev (P(complete)=0.37), basal-4.5B and Mistral said
   incomplete. Conditional requirements are where fast systems fail.
4. **K02 / K03 / K07** Refund requested but no bank account (or no order number). basal-4.5B still says "complete"
   (0.63 to 0.84), exactly as in experiment 01; basal-1.5B says "complete" for 16 of the 21 incomplete forms. basal
   does not check the conditions of a rule one by one.
5. **S13** "Rozumiem, że każdemu zdarzają się pomyłki, ale to już druga źle skompletowana paczka..." Label: slightly
   irritated. basal-4.5B: very irritated at p=0.93. basal-4.5B put all five "slightly irritated" errors (S08, S09,
   S11, S12, S13) in "very irritated": it has no middle level on this scale.
6. **P13** A customer, from the e-mail registered on the account, asks to change the refund account number. Label:
   not phishing. Jev (0.58) and Qwen flagged it. Arguably the more cautious answer for a real business: account
   changes are a known fraud vector, even though the question as written describes a legitimate sender.
7. **E34** A pregnant customer asks whether her policy covers perinatal care. Label: no escalation needed. basal-4.5B
   (0.87) and Mistral escalated: the word "ciąża" (health) triggers the "vulnerable person" rule without any
   difficulty in the situation.
8. **P04 / P09** Supplier bank-account change from a gmail address, and a fake "business register" invoice. Both
   scams. basal-1.5B missed P04 at p=0.93 (above the strict threshold) and both basal models missed P09. Qwen,
   Mistral, Jev and Gemini caught both.
9. **R31** "Czy byłaby możliwość obniżenia ceny sofy? Przyszła z przetarciem..." A price-reduction demand phrased as
   a polite question. basal-4.5B (0.58) and basal-1.5B (0.93, above threshold) said it is not a complaint.
10. **Qwen and phishing**: Qwen3-14B flagged five legitimate messages as scams (P13, P15, P17, P18, P19), including a
    password-reset code the customer had just requested and a customer asking to block a lost card. With thinking on,
    it errs on the side of suspicion, which on this category cost it more than basal-4.5B.

Gemini 3.8 Flash made no error on the clean set. Mistral's 8 errors: E28, E34, E36 (over-escalation), K01, K06,
K22, K37 (conditional rules, all "incomplete" where the form was complete) and P18.

## Spend

Total `usage.cost` for everything in this experiment, smoke tests included: **$1.31** of the $10 cap
(annotators $1.07, Gemini $0.18, Mistral $0.02, Jev $0.008 for 400 calls, smoke tests $0.03). Per-call log:
`costs.jsonl`.

## Caveats

- **Circularity.** The annotators are LLMs. High agreement means the labels are clear to two frontier models and to
  us, not that they are human-verified. The two disputed items are waiting for a human decision; no author label was
  changed after seeing any model output.
- **We wrote every item.** The set reflects our idea of Polish customer service. Real traffic is longer, messier and
  has more genuinely ambiguous cases. The near-perfect agreement and Gemini's 100% suggest the set is easier than
  real traffic for frontier models; it discriminates small and fast systems better than large ones.
- **n = 198 clean.** Differences of 1 to 3 items between Gemini, Jev and Mistral are not meaningful. Per-category
  intervals (n = 19 to 40) are wide. The gap between basal-4.5B and the API systems is outside the intervals.
- **Thresholds.** basal's thresholds were fitted for basal on its own data; for Jev they are only a common yardstick.
  Jev's noul probabilities come rounded to two decimals.
- **Jev endpoint is alpha.** Results are a snapshot of `typesafe/jev-1.13-20260917` on 2026-09-30.
- **Latency is not like for like.** basal and Qwen run on a laptop (basal as eager PyTorch bf16, see experiment 01);
  API numbers include the Poland to OpenRouter network. Jev two-order latency is two sequential calls. Batch size 1
  everywhere. The basal runs overlapped with the annotator API calls (network only, no local GPU work), and Qwen
  overlapped with the Gemini and Mistral API calls.
- **Prompts.** Chat LLMs got one prompt in the original option order, no averaging, provider-default temperature, one
  run each. Reasoning in the annotators was light: Opus 5.5 produced reasoning tokens on 108 of 200 items (median
  14), GPT-6.1 Sol on 70 (median 0); at effort "medium" both returned no reasoning tokens in smoke tests, which is
  why we used "high".
- **One run per system**, no repeats in this experiment.

## Files

- `decisions.jsonl` (200 items: id, type, category via id prefix, state, question, options, gold = author label,
  author_gold, tricky, subset `exp01`/`new`, rule for completeness items); `build_dataset.py` builds it
- `annotate.py`, `ann_opus-5.5.jsonl`, `ann_gpt-6.1-sol.jsonl` (+ `.meta.json`): annotations with justifications
  and reasoning text where returned
- `disputed.md`: disputed items for adjudication
- `run_basal.py`, `basal_prompt.py`, `run_llm.py` (from experiment 01, unchanged), `run_jev.py`, `run_cloud.py`,
  `common.py`, `analyze.py`
- `raw_*.jsonl` + `raw_*.meta.json`: per-item raw outputs per system (basal and Jev: both per-order distributions;
  Jev: full API responses; chat LLMs: full text and reasoning where returned)
- `results.csv`: one row per system (and annotator) and item, with a `clean` flag
- `analysis_out.txt`: full output of `analyze.py`; `costs.jsonl`: every paid call's cost; `log_*.txt`: console logs;
  `smoke/`: smoke-test outputs

# Experiment 02: Jev Router and cloud "thinking" models on the same 30 decisions

Date: 2026-09-30. Same 30 Polish customer-service / back-office decisions as experiment 01, now sent to cloud models
through OpenRouter. Total spend for this experiment (all runs and smoke tests, from `usage.cost`): **$0.135**.

**Status: raw Jev (`typesafe/jev-1.13` on OpenRouter's `/api/alpha/decisions` endpoint) is not in this version.**
The call was blocked by the permission settings of the session that ran the experiment. `run_jev.py` is prepared
for a follow-up run and is not committed yet. What is here is Jev *Router* (`typesafe/jev-router`), which is a
different product (see below).

## Setup

**Test set and prompt.** `../01-basal-vs-thinking/decisions.jsonl`, unchanged (gold labels fixed before experiment 01).
`run_cloud.py` copies the system prompt, the user prompt, the option lettering (A, B, C... in the original order)
and the answer parser verbatim from experiment 01's `run_llm.py` (the Qwen runs). One decision per call, single pass,
original option order only, no averaging. The answer is the first option letter in the reply content.

**Network.** Client on a residential connection in Poland calling
`https://openrouter.ai/api/v1/chat/completions`, non-streaming, one call in flight at a time. Latency is wall clock
from just before the HTTPS request to the full response on the client, so it includes network, OpenRouter routing,
provider queueing and generation. No warm-up calls were excluded (the smoke tests ran a few minutes earlier).

**Parameters.** Temperature not sent (provider default). `max_tokens` 8192. `"usage": {"include": true}` for exact
tokens and cost per call. Reasoning is set through OpenRouter's `reasoning` field. Retries were allowed only for
transport, 429 and 5xx errors; none were needed.

| system | model ID requested | reasoning setting | served by (provider, count) |
|---|---|---|---|
| Jev Router | `typesafe/jev-router` | chosen by the router | `openai/gpt-6-luna` (OpenAI) 20, `deepseek/deepseek-v4.1-flash` (Together) 10 |
| GPT-6 Luna direct | `openai/gpt-6-luna` | not sent (model default) | OpenAI 30 |
| DeepSeek V4.1 Flash direct | `deepseek/deepseek-v4.1-flash` | not sent (model default) | Wafer 18, Together 9, Relace 2, AtlasCloud 1 |
| Claude Sonnet 5.5, medium | `anthropic/claude-sonnet-5.5` | `{"effort": "medium"}` | Claude Platform on AWS 30 |
| Claude Sonnet 5.5, minimal | `anthropic/claude-sonnet-5.5` | `{"effort": "minimal"}` | Claude Platform on AWS 29, Azure 1 |
| GPT-6.1 Sol, medium | `openai/gpt-6.1-sol` | `{"effort": "medium"}` | OpenAI 30 |
| GPT-6.1 Sol, minimal | `openai/gpt-6.1-sol` | `{"effort": "minimal"}` | OpenAI 29, Azure 1 |
| GPT-6.1 Sol, high | `openai/gpt-6.1-sol` | `{"effort": "high"}` | OpenAI 30 |
| Gemini 3.8 Flash, medium | `google/gemini-3.8-flash` | `{"effort": "medium"}` | Google 18, Google AI Studio 12 |

Model choice: the two models Jev Router picked, called directly, plus the current mid tier of each big vendor on
OpenRouter on the run date (Sonnet 5.5 below Opus 5.5 and Fable 5.1; GPT-6.1 Sol below GPT-6 Astra; Gemini 3.8 Flash,
the newest Gemini text model listed; the newest Gemini Pro listed was 3.1 Pro Preview). Price per million tokens
(input / output): Luna $0.10 / $0.50, DeepSeek V4.1 Flash $0.02 / $0.40 (cheapest listed provider), Sonnet 5.5
$2 / $10, Sol $2 / $10, Gemini 3.8 Flash $0.75 / $3.75.

**Reasoning OFF is not available.** `{"enabled": false}` for Sonnet 5.5 and `{"effort": "none"}` for GPT-6.1 Sol both
returned HTTP 400 "Reasoning is mandatory for this endpoint and cannot be disabled." `minimal` was used as the lowest
setting instead.

**Claude did not reason at any setting.** Sonnet 5.5 reported 0 reasoning tokens and exactly 3 output tokens on every
call at `medium` and `minimal` (full runs), and also at `low`, `high`, `xhigh` and `{"max_tokens": 2048}` (2-item smoke
tests, in `smoke/`). Its adaptive thinking apparently decides that "answer only with the letter" needs none. So the
two Sonnet rows are effectively the same no-think run (identical cost to the cent). GPT-6.1 Sol also mostly skipped
reasoning: at `medium` it reasoned on 2 items (D07, K05), at `high` on 13 items (12 to 26 tokens). Because of this a
GPT-6.1 Sol `high` run was added after the others.

## Results

| system | accuracy | reklamacja | routing | eskalacja | kompletnosc | tricky | median latency | p90 latency | median output tok | median reasoning tok | max reasoning tok | $ for 30 | $ per 1,000 decisions |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jev Router | **30/30** | 10/10 | 10/10 | 5/5 | 5/5 | 8/8 | 1,606 ms | 2,397 ms | 5 | 0 | 86 | 0.00197 | 0.066 |
| GPT-6 Luna direct | **30/30** | 10/10 | 10/10 | 5/5 | 5/5 | 8/8 | 1,333 ms | 2,444 ms | 20 | 14 | 23 | 0.00094 | 0.031 |
| DeepSeek V4.1 Flash direct | **30/30** | 10/10 | 10/10 | 5/5 | 5/5 | 8/8 | 1,155 ms | 1,724 ms | 50 | 48 | 108 | 0.00236 | 0.079 |
| Claude Sonnet 5.5, medium | **30/30** | 10/10 | 10/10 | 5/5 | 5/5 | 8/8 | 1,529 ms | 2,012 ms | 3 | 0 | 0 | 0.02202 | 0.734 |
| Claude Sonnet 5.5, minimal | **30/30** | 10/10 | 10/10 | 5/5 | 5/5 | 8/8 | 1,491 ms | 1,765 ms | 3 | 0 | 0 | 0.02202 | 0.734 |
| GPT-6.1 Sol, medium | **30/30** | 10/10 | 10/10 | 5/5 | 5/5 | 8/8 | 1,960 ms | 2,521 ms | 5 | 0 | 26 | 0.01555 | 0.518 |
| GPT-6.1 Sol, minimal | **30/30** | 10/10 | 10/10 | 5/5 | 5/5 | 8/8 | 2,418 ms | 2,880 ms | 5 | 0 | 0 | 0.01515 | 0.505 |
| GPT-6.1 Sol, high | **30/30** | 10/10 | 10/10 | 5/5 | 5/5 | 8/8 | 2,019 ms | 3,407 ms | 5 | 0 | 26 | 0.01788 | 0.596 |
| Gemini 3.8 Flash, medium | **30/30** | 10/10 | 10/10 | 5/5 | 5/5 | 8/8 | 6,907 ms | 11,847 ms | 176 | 174 | 317 | 0.02395 | 0.798 |

Input was 183 to 306 tokens per call for OpenAI, DeepSeek and Gemini and 306 to 424 for Claude (different tokenizers).
No API errors, no retries, no unparsable answers in any full run.

**Errors per system: none.** Every system answered all 30 decisions correctly, including every item that basal or
Qwen got wrong in experiment 01 (D07, K01, K02, K03, R03).

**Latency notes.** Gemini's latency is bimodal and follows the provider: all 12 calls served by "Google AI Studio"
took 11.4 to 13.9 s, the 18 served by "Google" took 1.3 to 8.2 s (median 3.1 s). The one Sonnet call served by Azure
(K04, minimal) took 11.9 s; the other 29 were 1.4 to 2.7 s.

### Jev Router: what it routed where

| served model | calls | categories | reasoning tokens | correct | median latency | cost |
|---|---|---|---|---|---|---|
| `openai/gpt-6-luna` (OpenAI) | 20 | reklamacja 6, routing 10, eskalacja 3, kompletnosc 1 | 0 on 17 calls; 11 to 23 on D07, D10, K01 | 20/20 | 1,830 ms | $0.00052 |
| `deepseek/deepseek-v4.1-flash` (Together) | 10 | reklamacja 4, eskalacja 2, kompletnosc 4 | 24 to 86 on all 10 | 10/10 | 1,182 ms | $0.00145 |

All 10 routing (department) questions went to Luna. DeepSeek got R05, R07, R09, R10, E02, E03, K02 to K05; 8 of those
10 have gold answer "no" (option B). The router does not say why, and the response carries no routing metadata besides
the served `model` and `provider` (the only extra top-level field was `service_tier`).

**What the router adds on this set, compared with calling its picks directly:**

- Accuracy: nothing measurable. Luna and DeepSeek alone both score 30/30.
- Effort: on the items it sent to Luna, Luna mostly used no reasoning (reasoning tokens on 3 of 20), while Luna called
  directly with default settings reasoned on 18 of 30. So the router lowered Luna's per-call cost
  (median $0.0000253 vs $0.0000328).
- Cost: its DeepSeek calls cost about 3x a direct DeepSeek call (median $0.000142 vs $0.000048), probably because they
  were all served by Together, while direct calls mostly went to other providers (we did not isolate this). Overall the router cost $0.066 per 1,000
  decisions, 2.1x Luna direct ($0.031) and a little below DeepSeek direct ($0.079).
- Latency: on the 20 Luna items, router median 1,830 ms vs 1,272 ms for the same items called directly (about
  +0.56 s, which includes the routing decision). On the 10 DeepSeek items, 1,182 ms vs 1,379 ms direct (different
  providers). One run each, so these are single measurements, not stable differences.

## Comparison with experiment 01

| system | where it ran | accuracy | median latency | p90 latency | $ per 1,000 decisions |
|---|---|---|---|---|---|
| basal-1.0-4.5B (2 orders averaged) | **local**, Apple M5 Max, PyTorch MPS | 27/30 | 118 ms | 139 ms | local hardware |
| basal-1.0-1.5B (2 orders averaged) | **local**, same Mac | 27/30 | 50 ms | 53 ms | local hardware |
| Qwen3-14B thinking ON (MLX 4-bit) | **local**, same Mac | 29/30 | 3,939 ms | 5,152 ms | local hardware |
| Qwen3-14B thinking OFF (MLX 4-bit) | **local**, same Mac | 28/30 | 289 ms | 481 ms | local hardware |
| Jev raw (`typesafe/jev-1.13`) | cloud | not run in this version (see Status) | | | |
| Jev Router | **cloud**, Poland → OpenRouter | 30/30 | 1,606 ms | 2,397 ms | $0.066 |
| GPT-6 Luna direct | **cloud** | 30/30 | 1,333 ms | 2,444 ms | $0.031 |
| DeepSeek V4.1 Flash direct | **cloud** | 30/30 | 1,155 ms | 1,724 ms | $0.079 |
| Claude Sonnet 5.5 (medium; did not reason) | **cloud** | 30/30 | 1,529 ms | 2,012 ms | $0.734 |
| GPT-6.1 Sol, medium | **cloud** | 30/30 | 1,960 ms | 2,521 ms | $0.518 |
| GPT-6.1 Sol, high | **cloud** | 30/30 | 2,019 ms | 3,407 ms | $0.596 |
| Gemini 3.8 Flash, medium | **cloud** | 30/30 | 6,907 ms | 11,847 ms | $0.798 |

Local and cloud latencies measure different things: local numbers are pure compute on one Mac with the model already
loaded; cloud numbers are end to end over the internet from Poland and include queueing at a shared provider.

## Interesting cases

- **D07** ("does the 299 zł router support Wi-Fi 7? I'm thinking of buying two", gold: Sales). In experiment 01
  basal-4.5B and both Qwen runs chose Tech support, and we called our own label debatable. Every cloud system chose
  Sales. DeepSeek's reasoning: "asking about product features before purchase. Sales." Gemini's thinking summary:
  "a pre-sale inquiry focused on offer details and potential acquisition." It is also the item GPT-6.1 Sol reasoned
  longest on at medium (26 tokens) and one of the three items where the router asked Luna to reason.
- **K03** (refund requested, no bank account, gold: incomplete). basal-4.5B and 1.5B called it complete in experiment
  01. Every cloud model got it right; DeepSeek (through the router) wrote out the rule check: "requests refund, no bank
  account provided. So incomplete."
- **Reasoning budgets were mostly ignored.** On one-letter answers, Claude never reasoned, Sol reasoned on 2/30 at
  medium and 13/30 at high, and only Gemini reasoned on every item (62 to 317 tokens), which made it the slowest and
  most expensive system here without any accuracy difference.

## Caveats

- **Ceiling effect.** Every cloud system scored 30/30, so this set cannot rank them. It was built as a small
  sanity-check set, not a benchmark. Harder or larger sets are needed to separate these models.
- **n=30, our own labels**, no second annotator; D07 in particular is debatable (see experiment 01).
- **Single run per system**, original option order only, provider-default temperature. Some systems may give a
  different answer on a rerun; we did not measure that.
- **Cloud latency includes network and queueing** from a home connection in Poland at one time of day, and OpenRouter
  picked different upstream providers per call (see the served-by table). It is not the models' compute time.
- **Costs are OpenRouter's `usage.cost`** at the run date's prices and for these short prompts (183 to 424
  input tokens, 3 to 318 output tokens).
- **Reasoning settings are requests, not guarantees.** The reasoning token counts above are what the providers
  reported; for Claude, 0 reasoning tokens and 3 output tokens means no thinking was billed.
- **Jev Router is not Jev.** The router uses Jev to pick another model and effort; the answers come from GPT-6 Luna or
  DeepSeek V4.1 Flash. The System One comparison with basal needs raw Jev, which is not in this version.

## Files

- `run_cloud.py`: runner for OpenRouter chat/completions (prompt and parser copied from experiment 01)
- `run_all_chat.sh`: the full-run commands, in the order they were run
- `analyze.py`: builds `results.csv` and the tables above
- `raw_*.jsonl` + `raw_*.meta.json`: per-item raw responses (served model, provider, usage with tokens and cost,
  answer text, reasoning text where the provider returned it, latency)
- `log_*.txt`: console logs of the full runs
- `costs.jsonl`: per-call cost ledger for everything run in this experiment, including smoke tests
- `smoke/`: 2-item smoke tests, including the failed reasoning-off attempts (HTTP 400)


## Raw Jev (added 2026-09-30, run from the main session)

`typesafe/jev-1.13` on `POST https://openrouter.ai/api/alpha/decisions` (served as `typesafe/jev-1.13-20260917`,
provider TypeSafe), System One request format, one question per call. Yes/no items sent as `noul` with
`criteria {true, false}`; choice items with keys A-E. Script: `run_jev.py`. Snapshot of the alpha endpoint on this date.

| run | accuracy | median latency | p90 latency | $ per 1,000 decisions |
|---|---|---|---|---|
| original option order | 30/30 | 290 ms | 330 ms | 0.0194 |
| reversed option order | 30/30 | 311 ms | 375 ms | 0.0194 |
| yes/no sent as 2-option choice | 30/30 | 289 ms | 330 ms | 0.0199 |
| two-order average | 30/30 | | | |

Latency is end to end from Poland (residential connection), so it includes the network round trip.
No prediction changed between option orders.

**Coverage at basal's shipped thresholds** (two-order average; Jev's confidences are the vendor's own, not recalibrated):

| system | threshold | decided alone | wrong among those |
|---|---|---|---|
| Jev 1.13 | >= 0.913 | 28/30 | 0 |
| Jev 1.13 | >= 0.744 | 30/30 | 0 |
| basal-4.5B (exp 01) | >= 0.913 | 23/30 | 0 |
| basal-4.5B (exp 01) | >= 0.744 | 28/30 | 2 (K02, K03) |

The two items below Jev's 0.913 are completeness-rule items (K02 0.905, K05 0.905); K03 is at 0.915. Jev got K02 and
K03 right, the two completeness items both basal models missed, and D07 (the debatable Wi-Fi router label), which
basal-4.5B and both Qwen3 runs missed.

**basal vs Jev on these 30 items.** Jev 30/30 against 27/30 for both basal models, and it decides more items alone at
the strict threshold (28 against 23) with no errors in either case. basal's advantage here is that it runs locally
(118 ms for 4.5B, 50 ms for 1.5B on an M5 Max; 12.5 ms on an H100 per its report) with no data leaving the machine,
and it is open (Apache-2.0). This contrasts with basal's own report, where basal-4.5B leads Jev 0.884 to 0.780 on the
author's unpublished Polish set; n=30 with our own labels is far too small to settle that, which is what experiment 03
(about 200 items, independently checked labels) is for.

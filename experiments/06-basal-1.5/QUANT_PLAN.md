# Plan (v2, not run yet): what MLX quantization costs basal-1.5-mini on experiments 03 and 04

Status: DRAFT v2, after an independent review (Fable 5.1, 2026-10-05) of v1. Nothing below has been run except the
smoke checks under "Already known". Changes from v1 are listed at the end.

## Question

basal reads its decision from the letter logits, averages two option orders and applies per-type temperatures and
confidence thresholds fitted on the bf16 model. A quantized port can keep the top option and still move the
probabilities. Question: for each MLX port of basal-1.5-mini, how far are its decisions and probabilities from the
bf16 model on our own Polish sets, on which tasks does it break, and does it need its own temperatures
(`CALIBRATION.mlx.json`, which `basal-serve --mode mlx` loads when a repo ships it, `basal/server.py:263`)?

Not asked: whether the shipped thresholds hold on our sets. They already do not for the reference (e04 noul: 15 of 57
covered errors at the 5 % tier), so thresholds are compared port vs reference only.

## Already known (smoke, 2026-10-05)

- A plain `mlx_lm.convert` of basal-1.5 is silently wrong: the base config has transformers-5 `rope_parameters`,
  mlx_lm 0.31.3 falls back to `rope_theta` 10000 (|dp| up to 0.32). Fixed in `convert_mlx.py`.
- e03 (200), `basal-serve --mode mlx`, vs PyTorch bf16 (acc 0.880): MLX-bf16 agreement 1.000 / acc 0.880 (bit-identical
  to the raw MLX readout); MLX-6bit 0.980 / 0.880 (4 flips, all with reference margin ≤ 0.10); MLX-4bit 0.850 / 0.800
  (30 flips, 26 with margin > 0.2, 19 of them in `kompletnosc`, 5 in `phishing`; weak link to input length, r = 0.11).
- The first 40 e03 items alone suggested 4bit was fine: small samples mislead here.

## Systems (all basal-1.5-mini)

| tag | weights | role |
|---|---|---|
| `torch-bf16` | PyTorch MPS bf16, `Remek/basal-1.5-mini` (existing runs) | reference |
| `torch-fp32` | PyTorch MPS fp32, same weights | dtype floor (calibration `eval_dtype` is float32) |
| `mlx-bf16` | `agentGreg/basal-1.5-mini-MLX-bf16` | engine floor; baseline for quantization cost |
| `mlx-8bit` | `Remek/basal-1.5-mini-MLX-8bit` | official port |
| `mlx-fp4` | `Remek/basal-1.5-mini-MLX-fp4` (ships `CALIBRATION.mlx.json`) | official port |
| `mlx-6bit` | `agentGreg/...-MLX-6bit`, affine g64 | ours |
| `mlx-4bit` | `agentGreg/...-MLX-4bit`, affine g64 | ours |
| `mlx-4bit-g32` | affine 4-bit, group 32 (local) | candidate 4-bit |
| `mlx-mixed-4-6` | `mlx_lm` recipe `mixed_4_6`, embeddings/head bf16 (local) | candidate 4-bit |

Three distances are reported separately: dtype floor (fp32 vs bf16), engine floor (mlx-bf16 vs torch-bf16) and
quantization cost (each port vs mlx-bf16, and vs torch-bf16 for the card). Runs record local path and hub revision.

## Sets

- e03: `../03-extended-set/decisions.jsonl`, 200 items; results on the full set and on experiment 03's clean set
  (`results.csv` `clean`, 198/200).
- e04: `../04-multi-domain/decisions.jsonl`, 204 items, 12 domains, all clean.
- Extra paired readouts for the label-free metrics only (agreement, |dp|, temperature fit): rules99 with `facts auto`
  and with `rule-in-state`, the 40 rule-change items. Correlated with the base items; reported separately.

## Script fixes before any run

1. `run_mlx.py`: load `CALIBRATION.mlx.json` when present (as the server does), record the file used in meta.
2. `run_mlx.py`: write `thresholds` to meta as `run_basal.py` does (otherwise `analyze` drops coverage silently).
3. `run_mlx.py`: support `common.variant` (facts auto, rule-in-state) for the extra readouts.
4. `convert_mlx.py`: `--group-size` and `--recipe mixed_4_6` options.

## Runs

1. Raw readout (`run_mlx.py`, `run_basal.py --dtype float32`), both orders, every system, e03 + e04 (+ extras).
2. Served path (`run_serve.sh`, PORT ≠ 8000) only for ports that pass the raw gate; served vs raw max |dp| ≤ 0.03
   (the server batches both orders, the raw readout does not).
3. Latency: two passes with `run_latency_pass.sh`'s GPU watcher, report the minimum of the per-pass medians, and p90.

## Metrics

- Decisions: agreement; flips listed with the reference margin (p_top − p_second); discordant split (port right /
  reference right); per category and per type (noul/choice/score); accuracy with Wilson 95 % CI, descriptive only.
- Probabilities: mean and max |dp|; for `score`, the shift of the expected level; paired per-item log-loss difference
  vs the reference with a bootstrap CI.
- Temperature: Remek's label-free paired fit (`port_relative_temperature` in his fp4 `CALIBRATION.mlx.json`): the factor
  t per type that minimises KL(reference ‖ port ∘ t) on the same items, with a bootstrap CI; `score` not refit
  separately (43 items). A port with t outside its CI of 1.00 gets a `CALIBRATION.mlx.json` with those factors.
- Thresholds: covered counts and covered errors at the shipped 0.01 and 0.05 tiers, port vs reference.
- Cost: weights on disk, peak memory, latency.

## Decision rule (fixed before running)

A port is "equivalent on these sets" if agreement ≥ 0.98 pooled (e03 + e04) and no flip on an item where the
reference margin ≥ 0.2. Otherwise "measurably different": the card says so with the per-category flip table.
(On the smoke data this separates 6bit from 4bit; it is applied unchanged to the full runs.)

## Outputs

`raw_mlx-<tag>_mini_<set>.jsonl` (+ meta), `analyze_quant.py`, `quant_results.md`; updated cards of the agentGreg
repos (e03 + e04 numbers, flip table) and a `CALIBRATION.mlx.json` where the fit calls for it; a 4-bit candidate is
published only if it passes the rule.

## Limits

- 404 labelled items: accuracy differences of ±2 points are noise; agreement and margin-aware flips are the signal.
  Not a replacement for basal's 8,560-item test set.
- basal-1.5-mini only; 4.5B and max can follow with the same scripts. Apple M5 Max only.

## Changes from v1 (review)

Added: CALIBRATION.mlx.json handling, thresholds in meta, label-free paired temperature fit (replaces refit on gold),
relative threshold framing, margin-aware decision rule, per-category flips, three named floors, two candidate 4-bit
recipes, two-pass latency, extra paired readouts. Cut: McNemar as criterion, ECE across ports, Jensen-Shannon,
order-sensitivity metric, served runs for failing ports.

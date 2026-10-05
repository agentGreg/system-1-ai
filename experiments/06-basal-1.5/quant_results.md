Independent evaluation; not affiliated with or endorsed by the basal authors. Plan: `QUANT_PLAN.md` v2 (fixed before
the runs, after an independent review). Full tables: `quant_results_tables.md` (`python analyze_quant.py`).

# What MLX quantization costs basal-1.5-mini on experiments 03 and 04

**Short answer.** 8-bit and 6-bit MLX ports are equivalent to the bf16 model on our 404 Polish decisions (agreement
0.998 and 0.985, no flip on an item where the bf16 model was confident). Every 4-bit variant tried is measurably
different: agreement 0.84-0.92 and 25-53 flips on items the bf16 model answered with a margin of at least 0.2.
Remek's fp4 is the best 4-bit port (0.916); a smaller group (g32) or a llama.cpp-style mixed 4/6-bit recipe does not
rescue affine 4-bit. The damage is task-specific: rule-based completeness checks (`kompletnosc`) lose the most.

## Setup

- **Reference.** `Remek/basal-1.5-mini` in PyTorch MPS bf16 (`run_basal.py`), the existing runs of experiment 06.
- **Ports.** `convert_mlx.py` (decoder layers quantized, embeddings and output head kept in bf16, like Remek's ports):
  MLX bf16, affine 6-bit g64, affine 4-bit g64, affine 4-bit g32, mixed 4/6-bit (mlx_lm `mixed_4_6` rule with the head
  in bf16); Remek's `-MLX-8bit` and `-MLX-fp4` (the latter ships `CALIBRATION.mlx.json`, which is used).
- **Readout.** `run_mlx.py`: the same prompt and letter readout as `run_basal.py` (both option orders, float32
  softmax over the option letters, per-type temperature). Served path: `basal-serve --mode mlx` (basal v1.5.0).
- **Items.** e03 (200, experiment 03; clean set 198) and e04 (204, experiment 04), same gold labels as before.
  All 404 items are used here (agreement does not need a clean label); `results.md` reports accuracy on the 402
  clean items, so its 85.1% for mini and the 0.847 here are the same runs on different denominators.
  Label-free extras, paired with the reference: rules99 with facts auto and with the rule in the state, and the 20
  rule-change items under the original and under the changed rule.
- **Hardware.** Apple M5 Max, 128 GB, sequential runs, nothing else on the GPU (watcher log
  `log_gpu_watch_quant.txt`). Mac setup and conversion bug: see "Conversion" below.
- **Decision rule (fixed in the plan):** equivalent if pooled agreement ≥ 0.98 and no flip on an item where the
  reference margin (top probability minus the second) is at least 0.2.

## Floors

| comparison | agreement e03 / e04 | mean abs dp | max abs dp |
|---|---|---|---|
| PyTorch fp32 vs bf16 (dtype) | 1.000 / 1.000 | 0.003-0.004 | 0.065 |
| MLX bf16 vs PyTorch bf16 (engine) | 1.000 / 1.000 | 0.004 | 0.038 |

MLX itself costs nothing: the MLX bf16 copy gives the same decision as PyTorch on all 404 items, and a repeated MLX
run is bit-identical (204/204).

## Ports vs the bf16 reference (e03 + e04, 404 items)

| port | weights | agreement | flips | flips at ref margin ≥ 0.2 | accuracy (95% CI) | log-loss vs ref (95% CI) | verdict |
|---|---|---|---|---|---|---|---|
| PyTorch bf16 (reference) | 3.2 GB | - | - | - | 0.847 (0.808-0.878) | - | - |
| MLX bf16 (agentGreg) | 3.19 GB | 1.000 | 0 | 0 | 0.847 | +0.000 (-0.002, +0.002) | equivalent |
| MLX 8-bit (Remek) | 1.79 GB | 0.998 | 1 | 0 | 0.844 | +0.001 (-0.003, +0.004) | equivalent |
| MLX 6-bit (agentGreg) | 1.41 GB | 0.985 | 6 | 0 | 0.842 | +0.000 (-0.009, +0.009) | equivalent |
| MLX fp4 (Remek) | 1.04 GB | 0.916 | 34 | 25 | 0.827 | +0.072 (+0.042, +0.102) | measurably different |
| MLX 4-bit g32 | 1.13 GB | 0.866 | 54 | 41 | 0.782 | +0.123 (+0.070, +0.175) | measurably different |
| MLX mixed 4/6-bit | 1.10 GB | 0.854 | 59 | 47 | 0.775 | +0.140 (+0.092, +0.186) | measurably different |
| MLX 4-bit g64 (agentGreg) | 1.04 GB | 0.842 | 64 | 53 | 0.765 (0.721-0.804) | +0.188 (+0.133, +0.252) | measurably different |

When an affine 4-bit port disagrees with the reference it is wrong about three times as often as it is right
(4-bit g64: 14 port right / 47 reference right). The 6-bit flips are all near-ties (reference margin < 0.2) and split
2 / 4. Accuracy differences of 2 points or less are within noise at 404 items; agreement and flips are the signal.

## Where 4-bit breaks

Flips per category (e03 + e04), in brackets those at reference margin ≥ 0.2; categories with no flips left out:

| set | category | n | ref acc | 6-bit | fp4 | mixed 4/6 | 4-bit g32 | 4-bit g64 |
|---|---|---|---|---|---|---|---|---|
| e03 | kompletnosc | 40 | 0.68 | 2 (0) | 9 (6) | 19 (16) | 16 (13) | 19 (16) |
| e03 | eskalacja | 40 | 0.93 | 1 (0) | 6 (5) | 0 | 3 (2) | 1 (1) |
| e03 | irytacja | 20 | 0.85 | 0 | 2 (2) | 4 (4) | 5 (5) | 4 (4) |
| e03 | phishing | 20 | 0.90 | 0 | 2 (2) | 2 (2) | 2 (2) | 5 (5) |
| e03 | reklamacja / routing | 80 | 0.96 | 1 (0) | 1 (0) | 2 (1) | 1 (0) | 1 (0) |
| e04 | 12 domains | 204 | 0.81 | 2 (0) | 14 (10) | 32 (24) | 27 (19) | 34 (27) |

The rule-based completeness checks of experiment 03 (a compound rule applied to a form) lose almost half their
decisions under affine 4-bit; simple routing and complaint detection barely move. By type, `score` questions shift
most (mean shift of the expected level 0.04 for 6-bit, 0.22-0.39 for 4-bit). The label-free extras agree: on rules99
with facts the 4-bit ports keep 0.64-0.72 of the reference decisions (fp4 0.88, 6-bit 0.97, 8-bit 0.99).

## Calibration

- **Temperatures.** Remek's label-free paired fit (factor t on the bf16 temperature minimising KL to the reference),
  on e03 + e04 + extras: MLX bf16, 8-bit and 6-bit need no change (t = 1.000-1.015, all intervals include or touch
  1.00). For fp4 our fit (noul 0.90, choice 0.92) is consistent with Remek's shipped factors (0.84, 0.944). For affine
  4-bit, noul t = 1.20 (1.08-1.34): the port has become overconfident on yes/no questions. Refitting removes only 2 %
  of its KL to the reference (0.166 to 0.163): a temperature cannot repair flipped decisions.
- **Confidence thresholds** (bf16 tiers, covered items / covered errors on 404): reference 184 / 2 at the 1 % tier
  and 311 / 29 at the 5 % tier; 8-bit 184 / 2 and 309 / 28; 6-bit 184 / 2 and 307 / 29; fp4 163 / 3 and 277 / 31;
  4-bit g64 85 / 6 and 232 / 28. Ports at 6 bits or more keep the reference's coverage; 4-bit ports cover far fewer
  items at the strict tier and make more errors there. (On these sets the 5 % tier is not met even by the reference:
  29 / 311 = 9 %. The thresholds were certified on basal's own distribution, not ours.)

## Served path and latency (basal-serve --mode mlx, e03 + e04, two passes)

| port | agreement with ref (served) | served vs raw max abs dp | median latency per decision e03 / e04 | p90 |
|---|---|---|---|---|
| MLX bf16 | 1.000 | 0.000 | 42 / 45 ms | 43 / 52 ms |
| MLX 8-bit (Remek) | 1.000 | 0.043 | 52 / 58 ms | 55 / 64 ms |
| MLX 6-bit | 0.985 | 0.048 | 52 / 56 ms | 56 / 62 ms |

The plan's served-vs-raw gate (max abs dp ≤ 0.03) is not met by the quantized ports (0.043 and 0.048); decisions are
the same except one item for 8-bit on e04. The server scores both option orders in one padded batch, the raw readout
one sequence at a time, and quantized kernels are not shape-invariant; bf16 is identical. On this Mac and this model
size quantization does not make decisions faster: bf16 is the fastest, at twice the memory.

## Conversion

A plain `mlx_lm.convert` of basal-1.5 is silently wrong (mlx-lm 0.31.3, and the same code in 0.32.0): the base config stores `rope_theta` (1e6) in the
transformers-5 `rope_parameters` field, mlx_lm reads only a top-level `rope_theta` and falls back to 10000. The model
still loads and answers; on the first 40 e03 items it agreed with PyTorch 0.975 with |dp| up to 0.32.
`convert_mlx.py` writes the top-level value. Remek's own MLX ports have it.

## Published

- `agentGreg/basal-1.5-mini-MLX-bf16`, `-MLX-6bit` (equivalent), `-MLX-4bit` (measurably different, card says so,
  ships a `CALIBRATION.mlx.json` with noul t = 1.20). The 4-bit g32 and mixed 4/6-bit candidates were not published.

## Limits

- 404 labelled items from two of our own sets; not basal's 8,560-item test set. basal-1.5-mini only.
- One machine (M5 Max); latency on smaller Macs will differ, the ranking of agreement should not.

# Generation-5 Context-Reset Probe

Date: 2026-05-27

Label: structural policy improvement

## Protocol

This was a development-only follow-up to the teacher-serve macro probe. It
tested whether fixed reset macros become less brittle when gated by the previous
point context. The candidates were transient wrappers around
`SlimeVolleyNetPressurePolicy`; no maintained policy, config, test, ledger, or
holdout artifact was changed.

Seeds used exactly:

`12000, 12001, 12002, 12003, 12004, 12005, 12006, 12007, 12008, 12009, 12010, 12011, 12012, 12013, 12014, 12015`

No holdout or audit seeds were used. In particular, generation-5 holdout seeds
`13000..13049` and audit seeds `14000..14049` were not used.

Artifacts:

- `heuristic_learning/experiments/slimevolley/probes/g5_context_reset_probe.py`
- `heuristic_learning/experiments/slimevolley/results/generation_5_context_reset_probe.json`

Observed environment steps: `2,051,128`.

## Results

All rows use seeds `12000..12015`.

| Candidate | builtin | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Macro starts/frames |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `net_pressure_reference` | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | `0/0` |
| `baseline_rnn` | `0.2500` | `4.1875` | `3.7500` | `2.5625` | `2.5625` | `0/0` |
| `ctx_own_low_110_10` | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | `0/0` |
| `ctx_own_low_110_6` | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | `0/0` |
| `ctx_own_low_110_14` | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | `0/0` |
| `ctx_own_low_110_6_101_4` | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | `0/0` |
| `ctx_opponent_low_110_10` | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | `0/0` |
| `ctx_any_low_110_10` | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | `0/0` |
| `ctx_rear_wall_110_10` | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | `0/0` |

## Failure Analysis

The context gate did not activate any macro. On the built-in row, each
context-gated candidate observed reset-like events, but every context was
classified as `non_terminal_high`, so none matched the low/rear-wall triggers.
For example, `ctx_own_low_110_10` recorded `20` reset events and `0` macro
starts.

Because no macro fired, every context-gated candidate exactly reproduced the
`net_pressure_reference` score matrix. This is useful negative evidence: the
previous-point detector is too strict or stores the wrong pre-reset state for
the intended low/rear-wall context split.

## Promotion Recommendation

Do not promote any context-reset candidate.

No full-pool, holdout, or audit evaluation was opened. A future version would
need a better point-transition detector before it is worth another score probe.

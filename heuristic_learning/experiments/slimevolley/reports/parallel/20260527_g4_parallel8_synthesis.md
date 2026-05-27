# SlimeVolley Generation-4 Parallel8 Synthesis

Date: 2026-05-27

Type: development-only parallel worker synthesis

## Protocol

Five independent workers ran generation-4 development-only probes or diagnostics.
Short screens used fixed seeds `9000..9015`; full checks used fixed seeds
`9000..9049`. No generation-4 holdout seeds `10000..10049`, audit seeds
`11000..11049`, or final-evaluation commands were used.

Before worker launch, the coordinator checked for active SlimeVolley processes
and found none. During execution, visible SlimeVolley processes were generation-4
worker screens/full checks on `9000..9015` or `9000..9049`.

## Comparison Table

| Worker | Family | Type | Seeds | Best candidate | Key score evidence | Fixed-pool outcome | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | `attack` scalar/config search | scalar/config | screen `9000..9015`; full built-in `9000..9049` | `attack_rally_shape_low_x52` | full built-in `0.0600`, W-L-D `10-10-30`, `150000` steps | not run because it did not beat `baseline-rnn` built-in `0.1200` | no promotion |
| B | stacked `grounded_low_receive` | structural/history | screen `9000..9015`; full pool `9000..9049` | `stacked_low_101_wide` | full built-in `0.0400`, W-L-D from JSON artifact, `150000` built-in steps | only `+0.04` on `improved-v5/v6`; built-in regressed by `-0.10`; still below `baseline-rnn` on hard rows | no promotion |
| C | `rear_wall_press` / rear-wall losses | structural branch | screen `9000..9015` | `rw_press_slow_low_vertical_jump` | `improved-v4` screen improved to `2.8750`, W-L-D `16-0-0`, but built-in unchanged | regressed `improved-v5/v6` to `9-4-3`; no full check warranted | no promotion |
| D | `attack` vs `baseline-rnn` trace | diagnostic only | trace `9000..9015` | diagnostic only | `attack` mean `-0.1250`, W-L-D `2-4-10`; `baseline-rnn` mean `0.1250`, W-L-D `6-4-6` | not promotion evidence; points to low own-side recovery and missing `110/111` brace behavior | no promotion |
| E | archived-opponent robustness | robustness check | fixed pool `9000..9049` | `rally-serve-low-x52` scalar reference; `post-contact` structural reference | `rally-serve-low-x52` built-in `0.1800`; `post-contact` built-in `0.1400` | both trail `baseline-rnn` on every archived heuristic opponent in the fixed pool | no promotion |

## Decision

Do not make a maintained policy, config, or regression-test edit from this
parallel8 pass. The evidence does not meet the promotion criteria.

No candidate should be promoted based only on built-in opponent score. The only
new scalar/config candidate expanded to full built-in validation,
`attack_rally_shape_low_x52`, failed to beat the `baseline-rnn` built-in mean.
The only new structural candidate expanded to a full fixed-pool check,
`stacked_low_101_wide`, traded a built-in regression for tiny hard-tail gains.
The rear-wall screen found a narrow `improved-v4` gain that created extra
losses against `improved-v5` and `improved-v6`.

## Failure Analysis

The attack scalar search shows that local threshold and config motion around
the late-contact attack branch is not enough. The best attack-family full
built-in row reached `0.0600`, still below both `baseline-rnn` and the existing
`rally-serve` and `post-contact` references.

The stacked low-receive branch remains the clearest structural lead, but the
current wide `101` conversion is too broad. It preserves most archived rows,
adds only `+0.04` on `improved-v5/v6`, and loses `-0.10` on the built-in row.
That is not a robust improvement.

The rear-wall probes show that single-frame substitutions inside
`rear_wall_press` and `rear_wall_low_jump` are not sufficient. Active changes
either trade one archived opponent for another or leave scores unchanged.

Trace diagnostics still identify the same gap: `attack` never emits `110` or
`111`, while `baseline-rnn` uses `101+110` heavily and converts more low
left/net events. This is a useful hypothesis source, but it is not evidence for
promotion without a new audited candidate.

## Next Single Edit

No maintained policy/config/test edit is supported by this pass.

The next experiment should remain development-only: design a narrower
post-contact low-receive branch that separates low-left/net conversion from
low-mid-right and rear-wall recovery, and require full fixed-pool validation on
`9000..9049` before any maintained edit or holdout use.

# Generation-4 Joint Attack Scalar Search Attempt

Date: 2026-05-27

This note records a development-only scalar/config search around the existing
`attack` candidate. The search did not add a new detector, phase, state
machine, or macro-action. It only varied thresholds and gains inside the
already defined `improved-tuned` plus late-contact attack logic.

Generation-4 holdout seeds `10000..10049` and audit seeds `11000..11049` were
not opened.

## Search Budget

The throwaway search used development seeds only:

- short-screen seeds: `9000..9015`
- full validation seeds: `9000..9049`
- candidate configs screened: `140`
- full validations: `16`
- full-validation episodes: `800`
- full-validation environment steps: `2,400,000`
- wall-clock time reported by the search script: `574.0` seconds

The short-screen step count was not captured, which is a cost-accounting
weakness. At the SlimeVolley `3000` step cap, the short-screen upper bound is
`6,720,000` environment steps. These probes were run before formal promotion
and were not appended row-by-row to `generation_4_trials.jsonl`.

## Best Built-In Candidates

The best full-development built-in candidates were:

| Rank | Built-in mean | W/L/D | Mutated fields relative to `attack` |
| ---: | ---: | --- | --- |
| 1 | -0.10 | 11/13/26 | `high_arc_horizon=0.95`, `overcommit_guard_x=0.20`, `grounded_low_receive_airborne_margin=0.16`, `late_attack_vx=-0.45` |
| 2 | -0.10 | 11/14/25 | `high_arc_horizon=0.95`, `low_ball_rescue_x_window=0.64`, `grounded_low_receive_airborne_margin=0.20`, `late_attack_vx=-0.45`, `late_attack_dx_max=0.42` |
| 3 | -0.16 | 11/17/22 | `late_attack_vx=-0.55`, `late_attack_vy=-0.30`, `late_attack_dx_min=-0.02`, `late_attack_dx_max=0.34` |

The best candidate narrowed the same-seed built-in gap to the packaged
`baseline-rnn` comparator from `0.42` score points for `attack` to `0.22`, but
it still did not reach the comparator mean of `0.12`.

## Opponent-Pool Check For Rank-1 Candidate

A no-ledger development-only opponent-pool check was run for the rank-1
candidate before any promotion decision.

| Opponent | Attack mean | Rank-1 scalar candidate mean | Delta |
| --- | ---: | ---: | ---: |
| builtin | -0.30 | -0.10 | +0.20 |
| random | 4.80 | 4.74 | -0.06 |
| initial | 4.70 | 4.66 | -0.04 |
| improved-v0 | 4.74 | 4.70 | -0.04 |
| improved-v2 | 4.36 | 4.30 | -0.06 |
| improved-v3 | 2.62 | 2.62 | +0.00 |
| improved-v4 | 2.16 | 2.06 | -0.10 |
| improved-v5 | 1.08 | 1.00 | -0.08 |
| improved-v6 | 1.06 | 1.02 | -0.04 |

## Interpretation

The search found a built-in-specific scalar improvement, but it did not produce
a robust policy improvement. The candidate is worse or tied against the
non-built-in opponent pool and still below `baseline-rnn` against the built-in
opponent. Promoting it would mainly optimize the single opponent that the
experiment already warns against overfitting.

Decision: do not add a new policy version and do not open generation-4 holdout.
Keep the result as a visible failed/partial scalar/config search. The next
structural direction should collect contact-placement diagnostics for wins and
losses, then add an interpretable return-placement rule only if it improves the
fixed opponent pool rather than only the built-in opponent.

# Generation-4 Scalar-Tuned Structural Attempt

Date: 2026-05-26

This note records development-only scalar/config tuning attempts for the current SlimeVolley structural heuristic. These attempts do not add a new policy mode, detector, guard, macro-action, or state-machine transition. The policy is exposed separately as `improved-tuned` so reports can distinguish scalar tuning from genuine structural heuristic maintenance.

## Tuned Configuration

The current selected development-seed configuration is `g4-scalar-tuned-v2`:

- `x_margin = 0.04`
- `contact_x_window = 0.14`
- `high_arc_horizon = 0.85`
- `overcommit_guard_x = 0.18`
- `low_ball_rescue_x_window = 0.72`
- `low_ball_rescue_horizon = 0.06`
- `grounded_low_receive_airborne_margin = 0.12`

The prior `g4-scalar-tuned-v1` configuration used `overcommit_guard_x = 0.20`, `x_margin = 0.04`, and `low_ball_rescue_horizon = 0.06`. V2 was selected after bounded generation-4 development probes and a fixed opponent-pool comparison on seeds `9000..9049`. Generation-4 holdout seeds `10000..10049` and audit seeds `11000..11049` were not opened.

## Development Results

Fixed development evaluation used 50 episodes per opponent on seeds `9000..9049`.

| Opponent | V1 mean | V2 mean | V2 W/L/D | V2 environment steps |
| --- | ---: | ---: | --- | ---: |
| builtin | -1.10 | -0.44 | 6/23/21 | 150000 |
| random | 4.76 | 4.66 | 50/0/0 | 39838 |
| initial | 4.70 | 4.56 | 50/0/0 | 45426 |
| improved-v0 | 4.70 | 4.60 | 50/0/0 | 44549 |
| improved-v2 | 4.40 | 4.38 | 49/1/0 | 71170 |
| improved-v3 | 1.76 | 2.38 | 42/1/7 | 142137 |
| improved-v4 | 1.50 | 2.08 | 40/1/9 | 144565 |
| improved-v5 | 0.88 | 1.22 | 31/5/14 | 147554 |
| improved-v6 | 0.84 | 1.20 | 31/5/14 | 147554 |

## Interpretation

V2 improves the same-seed built-in result from current structural `improved` mean `-2.24` and scalar-tuned v1 mean `-1.10` to `-0.44`, closing part of the gap to `baseline-rnn` mean `0.12`. The remaining same-seed gap to the neural/RNN comparator is `0.56` score points.

This result is useful as a stronger scalar-search baseline, but it still does not support a claim that the coding agent found a new structural heuristic or beat the neural comparator. Future structural changes should beat both `improved` and `improved-tuned` v2 across the fixed development opponent pool before any generation-4 holdout evaluation is run.

## Failed Or Partial Directions Kept Visible

Before this scalar result, broad and narrowed `front_net_low_scoop` structural attempts scored `-2.72` and `-2.36` against the built-in opponent on the same development range, both worse than the current `improved` score of `-2.24`; those edits were rolled back and remain recorded in the generation-4 ledger and front-net note. Naive front-net jump probes were also worse or tied in throwaway development scripts and were not promoted. A later low left-moving receive structural probe tied or slightly worsened the v1 scalar baseline and was not promoted.

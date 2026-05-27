# Scalar Attack Search Worker

Date: 2026-05-27

## Exact Seeds Used

- Short screen: generation-4 development seeds `9000..9015`, 16 episodes per candidate, opponent `builtin`.
- Full validation: generation-4 development seeds `9000..9049`, 50 episodes per selected candidate, opponent `builtin`.
- No holdout seeds `10000..10049` and no audit seeds `11000..11049` were used.
- Runs were no-ledger development probes. They did not append trial rows.

## Candidate Definition

This worker reused the broader scalar/config search that was already running from the interrupted turn. The base candidate was the prior best scalar attack configuration:

- starts from `improved-tuned` v2 plus the `attack` structural rule,
- `high_arc_horizon = 0.95`,
- `overcommit_guard_x = 0.20`,
- `grounded_low_receive_airborne_margin = 0.16`,
- `late_attack_vx = -0.45`.

The search varied scalar/config fields only: contact margins, horizons, guards, rear-wall thresholds, and late-attack thresholds. It did not add a new structural branch, detector, state machine, or macro-action.

## Search Budget

- Candidate configs screened: `420`.
- Full validations: `24`.
- Full-validation episodes: `1200`.
- Full-validation environment steps: `3,600,000`.
- Search wall-clock time reported by the script: `1621.3` seconds.
- Short-screen step count was not fully persisted; at the 3000-step cap, the upper bound is `20,160,000` environment steps.

## Score Mean/W-L-D/Steps

Top full-validation candidates on seeds `9000..9049` vs `builtin`:

| Rank | Mean | W-L-D | Steps | Candidate mutation relative to prior scalar attack base |
| ---: | ---: | --- | ---: | --- |
| 1 | -0.02 | 9-12-29 | 150000 | `low_ball_rescue_x_window=0.48` |
| 2 | -0.02 | 9-12-29 | 150000 | `late_attack_dx_max=0.48`, `low_ball_rescue_x_window=0.48`, `rear_wall_press_agent_x=1.70` |
| 3 | -0.02 | 9-12-29 | 150000 | `grounded_low_receive_airborne_margin=0.20`, `low_ball_rescue_x_window=0.48`, `rear_wall_low_jump_agent_x=1.85` |
| 4 | -0.06 | 8-13-29 | 150000 | `rear_wall_low_jump_x=2.10`, `late_attack_dx_max=0.28`, `low_ball_rescue_x_window=0.48`, `grounded_low_receive_airborne_margin=0.28`, `late_attack_dx_min=0.04`, `late_attack_vx=-0.35` |
| 5 | -0.06 | 8-13-29 | 150000 | `floor_intercept_time_max=0.32`, `late_attack_dx_max=0.64`, `rear_wall_low_jump_vy=-0.60`, `rear_wall_press_agent_x=1.95`, `rear_wall_low_jump_y=0.24`, `low_ball_rescue_x_window=0.48`, `rear_wall_low_jump_vx=-0.05` |
| 6 | -0.06 | 8-13-29 | 150000 | `rear_wall_low_jump_x=2.00`, `rear_wall_press_agent_x=1.95`, `rear_wall_press_y=0.65`, `low_ball_rescue_x_window=0.48` |
| Reference | -0.10 | 11-13-26 | 150000 | prior scalar attack base, no additional mutation |
| Comparator | 0.12 | 18-12-20 | 150000 | packaged `baseline-rnn` comparator from recorded generation-4 dev rows |

## Structural Vs Scalar/Config Label

All candidates in this worker are `scalar/config tuning`. The best mutation `low_ball_rescue_x_window=0.48` changes only a scalar threshold in the existing `low_ball_rescue` branch.

## Failure Analysis

The search improved built-in development mean from the prior scalar attack base `-0.10` to `-0.02`, narrowing the same-seed gap to `baseline-rnn` from `0.22` to `0.14`. It still did not beat the neural/RNN comparator mean `0.12`.

The best full-validation candidate also had fewer wins than the prior scalar attack base (`9` vs `11`) while reducing losses (`12` vs `13`) and increasing draws (`29` vs `26`). This looks like a stall/robustness shift rather than a clear return-placement improvement.

Because the gain came from scalar/config search and only against the built-in opponent, it cannot support a structural heuristic-learning claim. It also has not been checked against the archived opponent pool. Per protocol, no holdout use is allowed from this result.

## Promotion Recommendation

Do not promote this scalar candidate. It does not beat `baseline-rnn` on built-in development seeds and is built-in-only evidence. If future work considers it anyway, it must first run the fixed generation-4 development opponent pool (`builtin`, `random`, `initial`, `improved-v0`, `improved-v2`, `improved-v3`, `improved-v4`, `improved-v5`, `improved-v6`) before any holdout discussion.

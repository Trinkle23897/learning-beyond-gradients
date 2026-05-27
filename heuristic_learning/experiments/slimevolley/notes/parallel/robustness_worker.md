# SlimeVolley Archived-Opponent Robustness Check

Date: 2026-05-27

Worker: D

## Scope

All checks use generation-4 development seeds only: `9000..9049` (`--split dev --seed-start 9000 --episodes 50`). No holdout seeds (`10000..10049`) or audit seeds (`11000..11049`) were used.

Fixed development opponent pool:

`builtin`, `random`, `initial`, `improved-v0`, `improved-v2`, `improved-v3`, `improved-v4`, `improved-v5`, `improved-v6`

Evidence sources:

- `improved-tuned` and `attack`: recorded `generation_4_summary.csv` rows on the exact fixed pool and seeds.
- Prior rank-1 scalar attack candidate: fresh no-ledger checks with `.venv/bin/python -m hl_benchmark.slimevolley.evaluate --policy attack --split dev --seed-start 9000 --episodes 50 --no-ledger --config-json ...`.

## Candidate Definitions

`improved-tuned` is a scalar/config baseline, not a structural improvement. It uses `g4-scalar-tuned-v2`:

- `x_margin = 0.04`
- `contact_x_window = 0.14`
- `high_arc_horizon = 0.85`
- `overcommit_guard_x = 0.18`
- `low_ball_rescue_x_window = 0.72`
- `low_ball_rescue_horizon = 0.06`
- `grounded_low_receive_airborne_margin = 0.12`

`attack` is a structural candidate. It starts from `improved-tuned` v2 and adds the late-contact attack rule:

- Fires when `ball_x > 0.05`
- `0.28 <= ball_y <= 0.65`
- `ball_vx < -0.35`
- `ball_vy < -0.10`
- `0.04 <= agent_x - ball_x <= 0.28`
- Action: `101` (`forward + jump`)

The prior best built-in scalar attack candidate is scalar/config tuning around `attack`, not a new structural rule. It starts from the full `improved-tuned` v2 plus `attack` definition and mutates:

- `high_arc_horizon = 0.95`
- `overcommit_guard_x = 0.20`
- `grounded_low_receive_airborne_margin = 0.16`
- `late_attack_vx = -0.45`

The no-ledger built-in reproduction matched the recorded rank-1 candidate: mean `-0.10`, W/L/D `11/13/26`, steps `150000`.

## Robustness Results

| Opponent | improved-tuned scalar/config mean W-L-D steps | attack structural mean W-L-D steps | prior scalar attack mean W-L-D steps |
| --- | ---: | ---: | ---: |
| builtin | -0.44 6/23/21 150000 | -0.30 7/18/25 150000 | -0.10 11/13/26 150000 |
| random | 4.66 50/0/0 39838 | 4.80 50/0/0 37905 | 4.74 50/0/0 38050 |
| initial | 4.56 50/0/0 45426 | 4.70 50/0/0 44007 | 4.66 50/0/0 44650 |
| improved-v0 | 4.60 50/0/0 44549 | 4.74 50/0/0 44346 | 4.70 50/0/0 44452 |
| improved-v2 | 4.38 49/1/0 71170 | 4.36 49/1/0 74158 | 4.30 49/1/0 73734 |
| improved-v3 | 2.38 42/1/7 142137 | 2.62 46/1/3 138953 | 2.62 46/0/4 137892 |
| improved-v4 | 2.08 40/1/9 144565 | 2.16 40/3/7 143423 | 2.06 40/0/10 142412 |
| improved-v5 | 1.22 31/5/14 147554 | 1.08 30/8/12 148079 | 1.00 30/9/11 148311 |
| improved-v6 | 1.20 31/5/14 147554 | 1.06 30/8/12 148079 | 1.02 31/9/10 148311 |

## Failure Analysis

`improved-tuned` is the strongest scalar/config baseline currently visible in the recorded generation-4 summary, but it is not structural evidence and still trails the same-seed packaged `baseline-rnn` built-in mean `0.12` by `0.56`.

`attack` is genuine structural progress on several opponents, including built-in (`+0.14` over `improved-tuned`), random (`+0.14`), initial (`+0.14`), improved-v0 (`+0.14`), improved-v3 (`+0.24`), and improved-v4 (`+0.08`). The failure is robustness: it regresses improved-v2 (`-0.02`) and the nearest archived opponents improved-v5/improved-v6 (`-0.14` each). It also still trails `baseline-rnn` on built-in by `0.42`.

The prior rank-1 scalar attack candidate is built-in-specific. It improves built-in versus `attack` by `+0.20`, but against every non-built-in opponent it is worse or tied on mean: random `-0.06`, initial `-0.04`, improved-v0 `-0.04`, improved-v2 `-0.06`, improved-v3 `+0.00`, improved-v4 `-0.10`, improved-v5 `-0.08`, improved-v6 `-0.04`. The built-in gain does not generalize to the archived opponent pool and still remains below `baseline-rnn` by `0.22`.

Long step counts and many draws against built-in and the later archived opponents show that these candidates mostly alter marginal contacts and stalls rather than producing a robust return-placement solution.

## Promotion Recommendation

Do not promote any candidate from this check.

Keep `improved-tuned` as a scalar/config baseline only. Keep `attack` as an auditable partial structural candidate, not a promoted policy. Keep the prior rank-1 scalar attack candidate as failed/partial scalar-search evidence because it overfits the built-in opponent and regresses or ties the non-built-in fixed pool. Do not open generation-4 holdout or audit seeds from these results.

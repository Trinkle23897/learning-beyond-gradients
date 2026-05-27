# Generation-4 Parallel3 Attack/Rally-Serve Scalar Search

Date: 2026-05-27

Worker: 1

## Protocol

This was a development-only scalar/config search around the existing
`attack`/`rally-serve` family. No policy source, test, opponent-pool, or
canonical ledger file was edited. Runs used no-ledger direct harness calls via:

`heuristic_learning/.venv/bin/python /tmp/g4_parallel3_attack_scalar_search.py`

The first attempted system-Python run failed because Anaconda Python did not
have `gym`; the valid rows below are from the repo-local
`heuristic_learning/.venv` runtime with `gym==0.20.0` and `slimevolleygym`
available.

No holdout seeds, audit seeds, or `slimevolley-final-eval` were used.

Short-screen seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full-check seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

All candidates used policy `rally-serve` with full `RALLY_SERVE_CONFIG` plus
only the listed delta. `scalar` means one numeric field changed. `config` means
multiple numeric fields changed. The references are controls, not candidates.

Full-check selection rule: run the top four short-screen candidate rows by
mean, wins, fewer losses, and descending label tie-break, plus the three
references.

## Candidate Definitions

| Candidate | Kind | Policy | Delta from `RALLY_SERVE_CONFIG` |
| --- | --- | --- | --- |
| `low_rescue_x_0.50` | scalar | `rally-serve` | `low_ball_rescue_x_window=0.50` |
| `low_rescue_x_0.58` | scalar | `rally-serve` | `low_ball_rescue_x_window=0.58` |
| `ground_air_0.12` | scalar | `rally-serve` | `grounded_low_receive_airborne_margin=0.12` |
| `ground_air_0.20` | scalar | `rally-serve` | `grounded_low_receive_airborne_margin=0.20` |
| `late_vx_-0.50` | scalar | `rally-serve` | `late_attack_vx=-0.50` |
| `late_vy_-0.30` | scalar | `rally-serve` | `late_attack_vy=-0.30` |
| `late_dx_max_0.34` | scalar | `rally-serve` | `late_attack_dx_max=0.34` |
| `late_dx_wide_0.00_0.34` | config | `rally-serve` | `late_attack_dx_min=0.00`, `late_attack_dx_max=0.34` |
| `rear_wall_press_early` | config | `rally-serve` | `rear_wall_press_x=2.00`, `rear_wall_press_y=0.70` |
| `rescue50_ground12_latevy30` | config | `rally-serve` | `low_ball_rescue_x_window=0.50`, `grounded_low_receive_airborne_margin=0.12`, `late_attack_vy=-0.30` |

## Short Built-In Screen

Opponent: `builtin`. Seeds: `9000..9015`.

| Row | Kind | Mean | W-L-D | Environment steps |
| --- | --- | ---: | --- | ---: |
| `rally_serve_reference` | reference | `0.3125` | `4-0-12` | `48000` |
| `attack_reference` | reference | `-0.1250` | `2-4-10` | `48000` |
| `baseline_rnn_reference` | reference | `0.1250` | `6-4-6` | `48000` |
| `low_rescue_x_0.50` | scalar | `0.3125` | `4-0-12` | `48000` |
| `low_rescue_x_0.58` | scalar | `0.2500` | `4-1-11` | `48000` |
| `ground_air_0.12` | scalar | `0.3125` | `4-0-12` | `48000` |
| `ground_air_0.20` | scalar | `0.3125` | `4-0-12` | `48000` |
| `late_vx_-0.50` | scalar | `0.3125` | `4-0-12` | `48000` |
| `late_vy_-0.30` | scalar | `0.3125` | `4-0-12` | `48000` |
| `late_dx_max_0.34` | scalar | `0.3125` | `4-0-12` | `48000` |
| `late_dx_wide_0.00_0.34` | config | `0.3750` | `5-0-11` | `48000` |
| `rear_wall_press_early` | config | `0.0000` | `2-2-12` | `48000` |
| `rescue50_ground12_latevy30` | config | `0.3125` | `4-0-12` | `48000` |

## Full Built-In Check

Opponent: `builtin`. Seeds: `9000..9049`.

| Row | Kind | Mean | W-L-D | Environment steps |
| --- | --- | ---: | --- | ---: |
| `rally_serve_reference` | reference | `0.1400` | `13-8-29` | `150000` |
| `attack_reference` | reference | `-0.3000` | `7-18-25` | `150000` |
| `baseline_rnn_reference` | reference | `0.1200` | `18-12-20` | `150000` |
| `low_rescue_x_0.50` | scalar | `0.1600` | `13-8-29` | `150000` |
| `late_vy_-0.30` | scalar | `0.1400` | `13-8-29` | `150000` |
| `late_dx_wide_0.00_0.34` | config | `0.1000` | `12-8-30` | `150000` |
| `rescue50_ground12_latevy30` | config | `0.1600` | `13-8-29` | `150000` |

Top full built-in result: `low_rescue_x_0.50` and
`rescue50_ground12_latevy30` tied at mean `0.1600`, `13-8-29`, `150000`
environment steps. The scalar `low_rescue_x_0.50` is the parsimonious top
candidate because the config tie adds two extra field changes without improving
the observed row.

## Failure Analysis

The short-screen leader, `late_dx_wide_0.00_0.34`, did not survive the full
check. It moved from `0.3750`, `5-0-11` on `9000..9015` to `0.1000`,
`12-8-30` on `9000..9049`, below both `rally-serve` and `baseline-rnn` built-in
full-development means.

The best full rows, `low_rescue_x_0.50` and `rescue50_ground12_latevy30`,
improved built-in mean from `0.1400` to `0.1600` but did not change W-L-D versus
`rally-serve` (`13-8-29`). This means the apparent gain is within same-outcome
score/life-difference details rather than a cleaner conversion of draws or
losses into wins. The config version offers no measurable advantage over the
single scalar change.

The wider low-rescue window `0.58` introduced a screen loss. The early
rear-wall press config regressed immediately on the screen. Grounded-low-receive
airborne-margin and late-attack threshold variants were mostly inert on the
short screen, except for the wide late-dx config that overfit the subset and
then regressed on the full check.

This is built-in-only development evidence. It does not establish robustness
against the generation-4 fixed development opponent pool and must not be used
to justify holdout or audit evaluation.

## Promotion Recommendation

Do not promote a new scalar/config candidate from this worker run.

If follow-up is desired, the only candidate worth a development-pool check is
`low_rescue_x_0.50` because it is the simplest full-check leader. It should
remain a development-only hypothesis unless it improves the fixed generation-4
development opponent pool without opening holdout or audit seeds.

# Generation-4 Attack/Rally-Serve Scalar Config Subagent V2

Date: 2026-05-27

Worker: 1

## Protocol

This was a development-only scalar/config tuning probe around the existing
`attack` plus `rally-serve` candidate. No policy source files were edited.
No ledger rows were appended. No holdout or audit seeds were used.

Short-screen seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full-check seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

All candidate configs started from `RALLY_SERVE_CONFIG` and changed only the
listed scalar/config deltas. This preserves the existing attack/rally-serve
structure and avoids accidentally resetting omitted fields to raw
`SlimeVolleyConfig` defaults.

Base fields relevant to this probe:

- `x_margin=0.04`, `contact_x_window=0.14`, `high_arc_horizon=0.95`
- `overcommit_guard_x=0.18`, `low_ball_rescue_x_window=0.54`, `low_ball_rescue_horizon=0.06`
- `grounded_low_receive_airborne_margin=0.16`, `landing_horizon=0.38`
- `late_attack_y_min=0.24`, `late_attack_y_max=0.65`, `late_attack_vx=-0.45`, `late_attack_vy=-0.35`
- `late_attack_dx_min=0.04`, `late_attack_dx_max=0.28`
- `rally_serve_detect_y=1.45`, `rally_serve_x_window=0.28`, `rally_serve_vx_window=0.50`
- `rally_serve_steps=8`, `rally_serve_cooldown_steps=12`

Label: scalar/config tuning only. This run did not claim a structural
improvement.

## Short Built-In Screen

Opponent: `builtin`. Policy: `rally-serve`. Seeds: `9000..9015`.

| Candidate | Kind | Delta from base | Mean | W/L/D | Steps |
| --- | --- | --- | ---: | --- | ---: |
| `rally_current` | reference | none | `0.3125` | `4/0/12` | `48000` |
| `rs_steps_5` | scalar | `rally_serve_steps=5` | `0.3125` | `4/0/12` | `48000` |
| `rs_steps_6` | scalar | `rally_serve_steps=6` | `0.3125` | `4/0/12` | `48000` |
| `rs_steps_10` | scalar | `rally_serve_steps=10` | `0.3125` | `4/0/12` | `48000` |
| `rs_steps_12` | scalar | `rally_serve_steps=12` | `0.3125` | `4/0/12` | `48000` |
| `rs_cooldown_8` | scalar | `rally_serve_cooldown_steps=8` | `0.3125` | `4/0/12` | `48000` |
| `rs_cooldown_16` | scalar | `rally_serve_cooldown_steps=16` | `0.3125` | `4/0/12` | `48000` |
| `rs_x_0.22` | scalar | `rally_serve_x_window=0.22` | `0.1875` | `3/1/12` | `48000` |
| `rs_x_0.34` | scalar | `rally_serve_x_window=0.34` | `0.3125` | `4/0/12` | `48000` |
| `rs_vx_0.35` | scalar | `rally_serve_vx_window=0.35` | `0.3125` | `4/0/12` | `48000` |
| `rs_vx_0.65` | scalar | `rally_serve_vx_window=0.65` | `0.3125` | `5/1/10` | `48000` |
| `rs_y_1.35` | scalar | `rally_serve_detect_y=1.35` | `0.2500` | `4/1/11` | `48000` |
| `rs_y_1.55` | scalar | `rally_serve_detect_y=1.55` | `0.3125` | `4/1/11` | `48000` |
| `higharc_0.90` | scalar | `high_arc_horizon=0.90` | `0.1875` | `4/1/11` | `48000` |
| `higharc_1.00` | scalar | `high_arc_horizon=1.00` | `0.1250` | `3/2/11` | `48000` |
| `low_rescue_0.60` | scalar | `low_ball_rescue_x_window=0.60` | `0.1250` | `4/2/10` | `48000` |
| `late_vx_-0.35` | scalar | `late_attack_vx=-0.35` | `0.3125` | `4/0/12` | `48000` |
| `late_vx_-0.55` | scalar | `late_attack_vx=-0.55` | `0.3125` | `5/1/10` | `48000` |
| `late_vy_-0.25` | scalar | `late_attack_vy=-0.25` | `0.3125` | `4/0/12` | `48000` |
| `late_vy_-0.45` | scalar | `late_attack_vy=-0.45` | `0.3125` | `4/0/12` | `48000` |
| `steps10_x34_vx65` | config | `rally_serve_steps=10`, `rally_serve_x_window=0.34`, `rally_serve_vx_window=0.65` | `0.3125` | `5/1/10` | `48000` |
| `steps6_x22_vx35` | config | `rally_serve_steps=6`, `rally_serve_x_window=0.22`, `rally_serve_vx_window=0.35` | `0.1875` | `3/1/12` | `48000` |
| `steps10_y135_cd16` | config | `rally_serve_steps=10`, `rally_serve_detect_y=1.35`, `rally_serve_cooldown_steps=16` | `0.2500` | `4/1/11` | `48000` |

## Full Built-In Check

Opponent: `builtin`. Seeds: `9000..9049`.

| Candidate | Kind | Delta from base | Mean | W/L/D | Steps |
| --- | --- | --- | ---: | --- | ---: |
| `baseline_rnn` | reference | policy `baseline-rnn` | `0.1200` | `18/12/20` | `150000` |
| `rally_current` | reference | none | `0.1400` | `13/8/29` | `150000` |
| `rs_steps_5` | scalar | `rally_serve_steps=5` | `0.1400` | `13/8/29` | `150000` |
| `rs_x_0.34` | scalar | `rally_serve_x_window=0.34` | `0.1000` | `12/8/30` | `150000` |
| `rs_vx_0.65` | scalar | `rally_serve_vx_window=0.65` | `0.1400` | `14/10/26` | `150000` |
| `late_vx_-0.55` | scalar | `late_attack_vx=-0.55` | `0.1400` | `14/9/27` | `150000` |
| `steps10_x34_vx65` | config | `rally_serve_steps=10`, `rally_serve_x_window=0.34`, `rally_serve_vx_window=0.65` | `0.1000` | `13/10/27` | `150000` |

The only full-check variants that tied the current built-in mean were
`rs_steps_5`, `rs_vx_0.65`, and `late_vx_-0.55`. None improved the current
`rally_current` mean. The two variants with one extra built-in win also added
extra losses.

## Fixed Development Opponent Pool

Target pool: `builtin`, `random`, `initial`, `improved-v3`, `improved-v4`,
`improved-v5`, `improved-v6`. Seeds: `9000..9049`.

The pool run was stopped after the leader status request. Completed/captured
rows are below. The `rs_vx_0.65` vs `improved-v5` row was not captured before
process termination, and `late_vx_-0.55` rows after `improved-v4` were not run
to completion in this worker.

| Candidate | Opponent | Mean | W/L/D | Steps |
| --- | --- | ---: | --- | ---: |
| `rally_current` | `builtin` | `0.1400` | `13/8/29` | `150000` |
| `rally_current` | `random` | `4.7400` | `50/0/0` | `38217` |
| `rally_current` | `initial` | `4.6800` | `50/0/0` | `44634` |
| `rally_current` | `improved-v3` | `2.9800` | `48/0/2` | `138122` |
| `rally_current` | `improved-v4` | `2.3400` | `44/0/6` | `143814` |
| `rally_current` | `improved-v5` | `1.1600` | `32/7/11` | `149716` |
| `rally_current` | `improved-v6` | `1.2200` | `32/7/11` | `149716` |
| `rs_vx_0.65` | `builtin` | `0.1400` | `14/10/26` | `150000` |
| `rs_vx_0.65` | `random` | `4.7800` | `50/0/0` | `37759` |
| `rs_vx_0.65` | `initial` | `4.7200` | `50/0/0` | `43996` |
| `rs_vx_0.65` | `improved-v3` | `2.9800` | `48/0/2` | `136545` |
| `rs_vx_0.65` | `improved-v4` | `2.3800` | `44/0/6` | `141802` |
| `rs_vx_0.65` | `improved-v6` | `1.0600` | `30/8/12` | `150000` |
| `late_vx_-0.55` | `builtin` | `0.1400` | `14/9/27` | `150000` |
| `late_vx_-0.55` | `random` | `4.7400` | `50/0/0` | `38566` |
| `late_vx_-0.55` | `initial` | `4.6800` | `50/0/0` | `44936` |
| `late_vx_-0.55` | `improved-v3` | `3.0400` | `49/0/1` | `138122` |
| `late_vx_-0.55` | `improved-v4` | `2.3400` | `44/1/5` | `143814` |

## Failure Analysis

The modest v2 search did not find a scalar/config candidate that improved the
current `rally-serve` full-development built-in mean. Short-screen ties were
mostly inert macro/detector changes. Narrowing the serve x-window, lowering the
serve-y detector, increasing high-arc horizon to `1.00`, and widening low-ball
rescue all regressed on the short subset.

The two most tempting built-in variants, `rs_vx_0.65` and `late_vx_-0.55`, tied
the full built-in mean at `0.14` but converted some draws into both wins and
losses. That is not a robust improvement. The partial fixed-pool check also
shows robustness concerns: `rs_vx_0.65` regressed `improved-v6` from `1.22` to
`1.06`, and `late_vx_-0.55` introduced a loss against `improved-v4` while only
matching the current mean there.

Because the leader status request interrupted the pool run, this note should be
treated as partial evidence for the fixed-pool section. The completed evidence
is already sufficient to avoid promotion: no full built-in mean gain was found,
and the pool rows that completed do not show a clean robustness improvement.

## Promotion Recommendation

Do not promote a new scalar/config candidate from this worker run.

Best candidate, if a label is needed for follow-up: `late_vx_-0.55`
(`late_attack_vx=-0.55`). It tied `rally_current` on built-in full dev
(`0.1400`, `14/9/27`, `150000` steps) and had one favorable partial-pool row
against `improved-v3` (`3.0400`, `49/0/1`), but it did not improve the built-in
mean and the fixed-pool evidence is incomplete and mixed. Keep it as a
development note only.

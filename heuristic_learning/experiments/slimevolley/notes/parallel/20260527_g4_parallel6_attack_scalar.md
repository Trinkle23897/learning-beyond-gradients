# Generation-4 Parallel6 Attack/Rally-Serve Scalar Search

Date: 2026-05-27

Worker: A

Label: scalar/config tuning around `rally-serve`

## Protocol

This was a development-only scalar/config search around the existing
`rally-serve` candidate. It did not edit maintained source, policy, opponent,
test, ledger, summary, or result files. Runs used an inline no-ledger Python
orchestration from `heuristic_learning` with `PYTHONPATH=.` and the repo-local
`.venv`.

No holdout or audit seeds were used. The only seeds used were generation-4
development seeds.

Short-screen seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full-development seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

Fixed development opponent pool:

`builtin`, `random`, `initial`, `improved-v0`, `improved-v2`,
`improved-v3`, `improved-v4`, `improved-v5`, `improved-v6`.

All candidates used policy `rally-serve` with a full config cloned from
`RALLY_SERVE_CONFIG`, then only the listed delta was applied. This avoids
accidentally replacing omitted tuned fields with raw `SlimeVolleyConfig`
defaults.

Relevant base fields:

- `x_margin=0.04`, `contact_x_window=0.14`, `high_arc_horizon=0.95`
- `overcommit_guard_x=0.18`, `low_ball_rescue_x_window=0.54`, `low_ball_rescue_horizon=0.06`
- `grounded_low_receive_airborne_margin=0.16`, `landing_horizon=0.38`
- `late_attack_y_min=0.24`, `late_attack_vx=-0.45`, `late_attack_vy=-0.35`
- `rally_serve_detect_y=1.45`, `rally_serve_x_window=0.28`, `rally_serve_vx_window=0.50`
- `rally_serve_steps=8`, `rally_serve_cooldown_steps=12`

## Candidate Definitions

| Candidate | Kind | Policy | Delta from `RALLY_SERVE_CONFIG` |
| --- | --- | --- | --- |
| `rally_current` | reference | `rally-serve` | none |
| `low_x_0.46` | scalar | `rally-serve` | `low_ball_rescue_x_window=0.46` |
| `low_x_0.48` | scalar | `rally-serve` | `low_ball_rescue_x_window=0.48` |
| `low_x_0.50` | scalar | `rally-serve` | `low_ball_rescue_x_window=0.50` |
| `low_x_0.52` | scalar | `rally-serve` | `low_ball_rescue_x_window=0.52` |
| `low_x_0.56` | scalar | `rally-serve` | `low_ball_rescue_x_window=0.56` |
| `horizon_0.04` | scalar | `rally-serve` | `low_ball_rescue_horizon=0.04` |
| `horizon_0.08` | scalar | `rally-serve` | `low_ball_rescue_horizon=0.08` |
| `low_x_0.50_horizon_0.04` | config | `rally-serve` | `low_ball_rescue_x_window=0.50`, `low_ball_rescue_horizon=0.04` |
| `low_x_0.50_horizon_0.08` | config | `rally-serve` | `low_ball_rescue_x_window=0.50`, `low_ball_rescue_horizon=0.08` |
| `low_x_0.48_ground_0.14` | config | `rally-serve` | `low_ball_rescue_x_window=0.48`, `grounded_low_receive_airborne_margin=0.14` |
| `low_x_0.50_ground_0.14` | config | `rally-serve` | `low_ball_rescue_x_window=0.50`, `grounded_low_receive_airborne_margin=0.14` |

## Short Built-In Screen

Opponent: `builtin`. Seeds: `9000..9015`.

| Candidate | Kind | Mean | W-L-D | Steps |
| --- | --- | ---: | --- | ---: |
| `baseline_rnn` | reference | `0.1250` | `6-4-6` | `48000` |
| `rally_current` | reference | `0.3125` | `4-0-12` | `48000` |
| `low_x_0.46` | scalar | `0.2500` | `6-3-7` | `48000` |
| `low_x_0.48` | scalar | `0.3750` | `6-1-9` | `48000` |
| `low_x_0.50` | scalar | `0.3125` | `4-0-12` | `48000` |
| `low_x_0.52` | scalar | `0.3125` | `4-0-12` | `48000` |
| `low_x_0.56` | scalar | `0.1250` | `4-1-11` | `48000` |
| `horizon_0.04` | scalar | `-1.0000` | `2-9-5` | `48000` |
| `horizon_0.08` | scalar | `-0.6875` | `1-9-6` | `48000` |
| `low_x_0.50_horizon_0.04` | config | `-0.8750` | `3-8-5` | `48000` |
| `low_x_0.50_horizon_0.08` | config | `-0.6250` | `1-8-7` | `48000` |
| `low_x_0.48_ground_0.14` | config | `0.3750` | `6-1-9` | `48000` |
| `low_x_0.50_ground_0.14` | config | `0.3125` | `4-0-12` | `48000` |

## Full Built-In Check

Opponent: `builtin`. Seeds: `9000..9049`.

| Candidate | Kind | Mean | W-L-D | Steps |
| --- | --- | ---: | --- | ---: |
| `baseline_rnn` | reference | `0.1200` | `18-12-20` | `150000` |
| `rally_current` | reference | `0.1400` | `13-8-29` | `150000` |
| `low_x_0.48` | scalar | `0.0600` | `13-13-24` | `150000` |
| `low_x_0.50` | scalar | `0.1600` | `13-8-29` | `150000` |
| `low_x_0.52` | scalar | `0.1800` | `14-8-28` | `150000` |
| `low_x_0.50_horizon_0.04` | config | `-0.6600` | `7-25-18` | `150000` |
| `low_x_0.50_ground_0.14` | config | `0.1600` | `13-8-29` | `150000` |

Rows that beat the `baseline_rnn` built-in full-development mean of `0.1200`
were checked against the fixed development opponent pool before making any
recommendation.

## Fixed Development Opponent Pool

Seeds: `9000..9049`.

### `low_x_0.50`

Scalar delta: `low_ball_rescue_x_window=0.50`.

| Opponent | Mean | W-L-D | Steps |
| --- | ---: | --- | ---: |
| `builtin` | `0.1600` | `13-8-29` | `150000` |
| `random` | `4.7400` | `50-0-0` | `38164` |
| `initial` | `4.6800` | `50-0-0` | `44662` |
| `improved-v0` | `4.7000` | `50-0-0` | `43444` |
| `improved-v2` | `4.4400` | `50-0-0` | `73608` |
| `improved-v3` | `2.9400` | `48-1-1` | `139323` |
| `improved-v4` | `2.4800` | `46-1-3` | `143928` |
| `improved-v5` | `1.2400` | `34-6-10` | `149716` |
| `improved-v6` | `1.3000` | `34-6-10` | `149716` |

### `low_x_0.52`

Scalar delta: `low_ball_rescue_x_window=0.52`.

| Opponent | Mean | W-L-D | Steps |
| --- | ---: | --- | ---: |
| `builtin` | `0.1800` | `14-8-28` | `150000` |
| `random` | `4.7400` | `50-0-0` | `38217` |
| `initial` | `4.6800` | `50-0-0` | `44635` |
| `improved-v0` | `4.7000` | `50-0-0` | `43455` |
| `improved-v2` | `4.3800` | `49-1-0` | `75222` |
| `improved-v3` | `3.0600` | `49-0-1` | `136376` |
| `improved-v4` | `2.4800` | `45-0-5` | `143646` |
| `improved-v5` | `1.2000` | `32-7-11` | `149716` |
| `improved-v6` | `1.2600` | `32-7-11` | `149716` |

### `low_x_0.50_ground_0.14`

Config delta: `low_ball_rescue_x_window=0.50`,
`grounded_low_receive_airborne_margin=0.14`.

| Opponent | Mean | W-L-D | Steps |
| --- | ---: | --- | ---: |
| `builtin` | `0.1600` | `13-8-29` | `150000` |
| `random` | `4.7400` | `50-0-0` | `38164` |
| `initial` | `4.6800` | `50-0-0` | `44662` |
| `improved-v0` | `4.7000` | `50-0-0` | `43444` |
| `improved-v2` | `4.4400` | `50-0-0` | `73608` |
| `improved-v3` | `2.9400` | `48-1-1` | `139323` |
| `improved-v4` | `2.4800` | `46-1-3` | `143928` |
| `improved-v5` | `1.2400` | `34-6-10` | `149716` |
| `improved-v6` | `1.3000` | `34-6-10` | `149716` |

## Failure Analysis

The short-screen leader did not survive full-development validation:
`low_x_0.48` reached `0.3750` on `9000..9015`, but fell to `0.0600` with
`13` losses on `9000..9049`. This is a clear short-subset overfit and is not a
promotion candidate.

`low_ball_rescue_horizon` was highly fragile. Both single-scalar horizon edits
regressed badly on the short screen, and the full `low_x_0.50_horizon_0.04`
check fell to `-0.6600`, `7-25-18`. The rescue horizon should not be moved
based on this pass.

`low_x_0.50_ground_0.14` exactly matched `low_x_0.50` in every fixed-pool row
captured here, so the extra grounded margin change has no observed value in
this seed range. The simpler scalar dominates the config tie.

`low_x_0.50` improved several archived-opponent rows but introduced losses
against `improved-v3` and `improved-v4`. It is useful as a diagnostic, but its
extra fixed-pool losses make it less clean than `low_x_0.52`.

`low_x_0.52` was the best row from this worker run. It improved the built-in
full-development mean from `0.1400` to `0.1800` versus current `rally-serve`,
converted one draw to a win, and did not show an obvious fixed-pool regression
against the current `rally-serve` reference rows recorded in
`notes/generation_4_rally_serve_candidate.md`. It improved or matched the
known current reference on `random`, `initial`, `improved-v0`, `improved-v2`,
`improved-v3`, `improved-v4`, `improved-v5`, and `improved-v6`.

This is still development-only evidence. Generation-4 holdout and audit ranges
remain unavailable for tuning, and this worker did not open or use them.

## Promotion Recommendation

Do not make a maintained-source promotion or final-generalization claim from
this worker run.

Best dev-only candidate: `low_x_0.52`, a scalar-only `rally-serve` config with
`low_ball_rescue_x_window=0.52`. It beat `baseline_rnn` and current
`rally-serve` on built-in full-development seeds and passed the required fixed
development opponent-pool check without an obvious archived-opponent
regression. Because this is post-hoc generation-4 development evidence and no
reserved seed can be opened here, the appropriate handoff is coordinator review
as a development-only candidate, not promotion to a final result.

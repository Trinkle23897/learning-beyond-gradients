# Parallel Scalar Rally/Attack Worker

Date: 2026-05-27

Worker: A

## Protocol

No holdout or audit seeds were used. I did not run `slimevolley-final-eval`.
All probes were no-ledger direct in-memory calls to
`evaluate_slimevolley(..., ledger_path=None, summary_path=None)`.

Short-screen seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full-check seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

Reference was current `rally-serve` config:

- `rally_serve_steps=8`
- `rally_serve_x_window=0.28`
- `rally_serve_vx_window=0.50`
- `late_attack_y_min=0.24`
- `late_attack_vy=-0.35`
- `low_ball_rescue_x_window=0.54`
- `contact_x_window=0.14`
- `landing_horizon=0.38`
- `high_arc_horizon=0.95`
- `overcommit_guard_x=0.18`

Each candidate used the full `RALLY_SERVE_CONFIG` plus only the listed scalar/config delta. `scalar` means one numeric field changed. `config` means multiple numeric fields changed. No policy/source/test files were edited.

## Short Screen

Opponent: `builtin`. Policy: `rally-serve`. Episodes: `16`.

| Candidate | Kind | Delta from reference | Mean | W/L/D | Steps |
| --- | --- | --- | ---: | --- | ---: |
| `reference_rally_serve` | reference | none | `0.3125` | `4/0/12` | `48000` |
| `steps_4` | scalar | `rally_serve_steps=4` | `0.3125` | `4/0/12` | `48000` |
| `steps_6` | scalar | `rally_serve_steps=6` | `0.3125` | `4/0/12` | `48000` |
| `steps_10` | scalar | `rally_serve_steps=10` | `0.3125` | `4/0/12` | `48000` |
| `steps_12` | scalar | `rally_serve_steps=12` | `0.3125` | `4/0/12` | `48000` |
| `steps_16` | scalar | `rally_serve_steps=16` | `0.0000` | `2/2/12` | `48000` |
| `serve_x_0.20` | scalar | `rally_serve_x_window=0.20` | `0.1875` | `3/1/12` | `48000` |
| `serve_x_0.24` | scalar | `rally_serve_x_window=0.24` | `0.1875` | `3/1/12` | `48000` |
| `serve_x_0.32` | scalar | `rally_serve_x_window=0.32` | `0.3125` | `4/0/12` | `48000` |
| `serve_x_0.36` | scalar | `rally_serve_x_window=0.36` | `0.3125` | `4/0/12` | `48000` |
| `serve_vx_0.35` | scalar | `rally_serve_vx_window=0.35` | `0.3125` | `4/0/12` | `48000` |
| `serve_vx_0.65` | scalar | `rally_serve_vx_window=0.65` | `0.3125` | `5/1/10` | `48000` |
| `serve_vx_0.80` | scalar | `rally_serve_vx_window=0.80` | `0.1250` | `5/4/7` | `48000` |
| `late_ymin_0.20` | scalar | `late_attack_y_min=0.20` | `0.3125` | `4/0/12` | `48000` |
| `late_ymin_0.28` | scalar | `late_attack_y_min=0.28` | `0.3125` | `4/0/12` | `48000` |
| `late_ymin_0.32` | scalar | `late_attack_y_min=0.32` | `0.3125` | `4/0/12` | `48000` |
| `late_vy_-0.25` | scalar | `late_attack_vy=-0.25` | `0.3125` | `4/0/12` | `48000` |
| `late_vy_-0.45` | scalar | `late_attack_vy=-0.45` | `0.3125` | `4/0/12` | `48000` |
| `late_vy_-0.55` | scalar | `late_attack_vy=-0.55` | `0.3125` | `4/0/12` | `48000` |
| `rescue_x_0.42` | scalar | `low_ball_rescue_x_window=0.42` | `-0.0625` | `4/4/8` | `48000` |
| `rescue_x_0.48` | scalar | `low_ball_rescue_x_window=0.48` | `0.3750` | `6/1/9` | `48000` |
| `rescue_x_0.60` | scalar | `low_ball_rescue_x_window=0.60` | `0.1250` | `4/2/10` | `48000` |
| `rescue_x_0.66` | scalar | `low_ball_rescue_x_window=0.66` | `0.0625` | `4/3/9` | `48000` |
| `rescue_x_0.72` | scalar | `low_ball_rescue_x_window=0.72` | `0.1250` | `4/2/10` | `48000` |
| `contact_x_0.12` | scalar | `contact_x_window=0.12` | `-0.5000` | `2/7/7` | `48000` |
| `contact_x_0.16` | scalar | `contact_x_window=0.16` | `-0.3125` | `2/6/8` | `48000` |
| `contact_x_0.18` | scalar | `contact_x_window=0.18` | `-0.6250` | `1/7/8` | `48000` |
| `contact_x_0.20` | scalar | `contact_x_window=0.20` | `-1.0625` | `1/11/4` | `48000` |
| `landing_0.30` | scalar | `landing_horizon=0.30` | `-0.8750` | `2/10/4` | `48000` |
| `landing_0.34` | scalar | `landing_horizon=0.34` | `-0.6250` | `2/8/6` | `48000` |
| `landing_0.44` | scalar | `landing_horizon=0.44` | `-0.1875` | `1/4/11` | `48000` |
| `landing_0.50` | scalar | `landing_horizon=0.50` | `-0.1250` | `2/6/8` | `48000` |
| `higharc_0.85` | scalar | `high_arc_horizon=0.85` | `-0.0625` | `2/3/11` | `48000` |
| `higharc_0.90` | scalar | `high_arc_horizon=0.90` | `0.1875` | `4/1/11` | `48000` |
| `higharc_1.05` | scalar | `high_arc_horizon=1.05` | `0.1875` | `4/2/10` | `48000` |
| `higharc_1.15` | scalar | `high_arc_horizon=1.15` | `0.0000` | `4/5/7` | `48000` |
| `guard_0.14` | scalar | `overcommit_guard_x=0.14` | `0.0625` | `2/2/12` | `48000` |
| `guard_0.16` | scalar | `overcommit_guard_x=0.16` | `0.0625` | `2/2/12` | `48000` |
| `guard_0.22` | scalar | `overcommit_guard_x=0.22` | `-0.3750` | `2/7/7` | `48000` |
| `guard_0.28` | scalar | `overcommit_guard_x=0.28` | `-0.9375` | `1/10/5` | `48000` |
| `combo_rescue48_latevy45` | config | `low_ball_rescue_x_window=0.48`, `late_attack_vy=-0.45` | `0.3750` | `6/1/9` | `48000` |
| `combo_rescue48_latevy25` | config | `low_ball_rescue_x_window=0.48`, `late_attack_vy=-0.25` | `0.3750` | `6/1/9` | `48000` |
| `combo_rescue60_contact16` | config | `low_ball_rescue_x_window=0.60`, `contact_x_window=0.16` | `-0.5625` | `1/8/7` | `48000` |
| `combo_rescue48_contact16` | config | `low_ball_rescue_x_window=0.48`, `contact_x_window=0.16` | `-0.1250` | `4/5/7` | `48000` |
| `combo_contact16_guard16` | config | `contact_x_window=0.16`, `overcommit_guard_x=0.16` | `-0.9375` | `1/9/6` | `48000` |
| `combo_contact18_guard14` | config | `contact_x_window=0.18`, `overcommit_guard_x=0.14` | `-1.1875` | `1/13/2` | `48000` |
| `combo_landing34_high90` | config | `landing_horizon=0.34`, `high_arc_horizon=0.90` | `-0.6250` | `2/7/7` | `48000` |
| `combo_landing44_high105` | config | `landing_horizon=0.44`, `high_arc_horizon=1.05` | `-0.3750` | `1/7/8` | `48000` |
| `combo_steps6_vx65` | config | `rally_serve_steps=6`, `rally_serve_vx_window=0.65` | `0.3125` | `5/1/10` | `48000` |
| `combo_steps10_vx65` | config | `rally_serve_steps=10`, `rally_serve_vx_window=0.65` | `0.3125` | `5/1/10` | `48000` |
| `combo_steps6_x32` | config | `rally_serve_steps=6`, `rally_serve_x_window=0.32` | `0.3125` | `4/0/12` | `48000` |
| `combo_steps10_x24` | config | `rally_serve_steps=10`, `rally_serve_x_window=0.24` | `0.1875` | `3/1/12` | `48000` |
| `combo_late_y20_vy45` | config | `late_attack_y_min=0.20`, `late_attack_vy=-0.45` | `0.3125` | `4/0/12` | `48000` |
| `combo_late_y28_vy25` | config | `late_attack_y_min=0.28`, `late_attack_vy=-0.25` | `0.3125` | `4/0/12` | `48000` |

## Full Checks

Top short-screen candidates plus the reference were checked on all generation-4 built-in dev seeds `9000..9049`.

| Candidate | Kind | Delta from reference | Mean | W/L/D | Steps | Beats `baseline-rnn` built-in dev mean `0.12`? |
| --- | --- | --- | ---: | --- | ---: | --- |
| `reference_rally_serve` | reference | none | `0.14` | `13/8/29` | `150000` | yes |
| `serve_vx_0.65` | scalar | `rally_serve_vx_window=0.65` | `0.14` | `14/10/26` | `150000` | yes |
| `combo_steps6_vx65` | config | `rally_serve_steps=6`, `rally_serve_vx_window=0.65` | `0.14` | `14/10/26` | `150000` | yes |
| `combo_steps10_vx65` | config | `rally_serve_steps=10`, `rally_serve_vx_window=0.65` | `0.14` | `14/10/26` | `150000` | yes |
| `steps_4` | scalar | `rally_serve_steps=4` | `0.14` | `13/8/29` | `150000` | yes |
| `combo_rescue48_latevy45` | config | `low_ball_rescue_x_window=0.48`, `late_attack_vy=-0.45` | `0.12` | `13/10/27` | `150000` | no, tied |
| `rescue_x_0.48` | scalar | `low_ball_rescue_x_window=0.48` | `0.06` | `13/13/24` | `150000` | no |
| `combo_rescue48_latevy25` | config | `low_ball_rescue_x_window=0.48`, `late_attack_vy=-0.25` | `0.06` | `13/13/24` | `150000` | no |

No full-checked scalar/config candidate exceeded the current `rally-serve` reference mean. The only candidates above the `baseline-rnn` built-in dev mean of `0.12` tied the reference at `0.14`.

## Failure Analysis

The short leader, `low_ball_rescue_x_window=0.48`, looked promising because it raised short-screen wins from `4` to `6`, but it also introduced a loss on only sixteen seeds. On the full dev built-in range, that volatility became loss inflation: `13/13/24`, mean `0.06`, compared with reference `13/8/29`, mean `0.14`.

The wider rally-serve velocity detector, `rally_serve_vx_window=0.65`, and the two step-count combinations tied the reference mean at `0.14`. They did not reduce losses. They converted some draws into both wins and losses: `14/10/26` versus reference `13/8/29`. That is not a clear improvement, even though the mean still beats the built-in dev `baseline-rnn` comparator.

Contact-window, landing-horizon, and overcommit-guard probes were mostly harmful on the short subset. Wider `contact_x_window` variants and lower `landing_horizon` variants especially converted draws into losses. This suggests the current reference is already near a narrow timing balance for the built-in opponent.

This is built-in-only evidence. It does not establish robustness against the fixed development opponent pool, and it does not justify opening holdout or audit seeds.

## Recommendation

Do not promote a new scalar/config candidate from this worker run. Keep current `rally-serve` as the reference.

If the team wants to consider `serve_vx_0.65`, `combo_steps6_vx65`, or `combo_steps10_vx65` despite the tied mean, each requires a fixed generation-4 development opponent-pool check before any holdout discussion. I do not recommend that as the next promotion path because all three add losses against `builtin` without improving mean score over the current reference.

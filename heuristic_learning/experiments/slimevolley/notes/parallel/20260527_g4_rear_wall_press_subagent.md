# Generation-4 Rear-Wall Press Subagent Probe

Date: 2026-05-27

Worker: C

## Protocol

No policy, source, test, ledger, summary, holdout, or audit files were edited or
written. Probes were direct no-ledger in-memory evaluations from
`heuristic_learning/` with `PYTHONPATH=.` and `.venv/bin/python`.

Exact short-screen seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Exact full-dev and fixed-pool seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

No holdout or audit seeds were used. Specifically, no `10000`, `11000`,
`13000`, or `14000` seed ranges were run.

## Candidate Definitions

All structural probes wrap current `rally-serve` unless noted. `rear_wall_press`
means the current press condition: far-right low descending ball, agent near
rear wall, excluding inherited `rear_wall_low_jump` for the final-action press
overrides. `rear_wall_low_jump` action probes only replace the action returned
when that inherited branch fires.

| Candidate | Type | Definition |
| --- | --- | --- |
| `baseline_rnn_reference` | neural comparator reference | Shipped SlimeVolley RNN wrapper vs built-in opponent. |
| `attack_reference` | structural reference | Current `attack` candidate. |
| `rally_serve_reference` | structural plus scalar/config reference | Current `rally-serve` candidate. |
| `scalar_disable_rear_wall_press` | scalar/config ablation | `rally-serve` with `rear_wall_press_x=9.0`, effectively disabling `rear_wall_press`. |
| `struct_press_forward_nojump` | structural branch probe | Force action `100` on `rear_wall_press`. |
| `struct_press_forward_jump` | structural branch probe | Force action `101` on `rear_wall_press`. |
| `struct_press_backward_jump` | structural branch probe | Force action `011` on `rear_wall_press`. |
| `struct_press_backward_nojump` | structural branch probe | Force action `010` on `rear_wall_press`. |
| `struct_press_noop_nojump` | structural branch probe | Force action `000` on `rear_wall_press`. |
| `struct_press_lower_only_forward_jump` | structural branch probe | Force action `101` only when `rear_wall_press` is active and `ball_y <= 0.45`. |
| `struct_press_confirm2_backward_jump` | structural stacked-frame probe | Force action `011` only after two consecutive `rear_wall_press` frames. |
| `struct_lowjump_forward_nojump` | structural branch action probe | When `rear_wall_low_jump` fires, force action `100`. |
| `struct_lowjump_backward_jump` | structural branch action probe | When `rear_wall_low_jump` fires, force action `011`. |
| `struct_lowjump_backward_nojump` | structural branch action probe | When `rear_wall_low_jump` fires, force action `010`. |
| `struct_lowjump_noop_nojump` | structural branch action probe | When `rear_wall_low_jump` fires, force action `000`. |

## Short Screen

Opponent: `builtin`. Seeds: `9000..9015`.

| Candidate | Mean | W-L-D | Steps |
| --- | ---: | --- | ---: |
| `baseline_rnn_reference` | `0.1250` | `6-4-6` | `48000` |
| `attack_reference` | `-0.1250` | `2-4-10` | `48000` |
| `rally_serve_reference` | `0.3125` | `4-0-12` | `48000` |
| `scalar_disable_rear_wall_press` | `-0.5000` | `1-6-9` | `48000` |
| `struct_press_forward_nojump` | `-0.5000` | `1-6-9` | `47052` |
| `struct_press_forward_jump` | `-0.5000` | `1-6-9` | `47052` |
| `struct_press_backward_jump` | `0.3125` | `4-0-12` | `48000` |
| `struct_press_backward_nojump` | `0.2500` | `4-1-11` | `48000` |
| `struct_press_noop_nojump` | `-0.5000` | `1-6-9` | `48000` |
| `struct_press_lower_only_forward_jump` | `0.3125` | `4-0-12` | `48000` |
| `struct_press_confirm2_backward_jump` | `0.3125` | `4-0-12` | `48000` |
| `struct_lowjump_forward_nojump` | `0.3125` | `4-0-12` | `48000` |
| `struct_lowjump_backward_jump` | `0.3125` | `4-0-12` | `48000` |
| `struct_lowjump_backward_nojump` | `0.3125` | `4-0-12` | `48000` |
| `struct_lowjump_noop_nojump` | `0.3125` | `4-0-12` | `48000` |

## Full Built-In Checks

Full checks were run for the references and probes that tied the short-screen
`rally-serve` mean. Opponent: `builtin`. Seeds: `9000..9049`.

| Candidate | Mean | W-L-D | Steps |
| --- | ---: | --- | ---: |
| `baseline_rnn_reference` | `0.12` | `18-12-20` | `150000` |
| `attack_reference` | `-0.30` | `7-18-25` | `150000` |
| `rally_serve_reference` | `0.14` | `13-8-29` | `150000` |
| `struct_press_backward_jump` | `0.16` | `13-8-29` | `150000` |
| `struct_press_lower_only_forward_jump` | `0.14` | `13-8-29` | `150000` |
| `struct_press_confirm2_backward_jump` | `0.14` | `12-8-30` | `150000` |
| `struct_lowjump_forward_nojump` | `0.14` | `13-8-29` | `150000` |
| `struct_lowjump_backward_jump` | `0.14` | `13-8-29` | `150000` |
| `struct_lowjump_backward_nojump` | `0.14` | `13-8-29` | `150000` |
| `struct_lowjump_noop_nojump` | `0.14` | `13-8-29` | `150000` |

`struct_press_backward_jump` was the only new probe to beat
`baseline_rnn_reference` on built-in full dev, so it received the fixed
development opponent-pool check before any recommendation.

## Fixed Opponent-Pool Check

Candidate: `struct_press_backward_jump`. Seeds: `9000..9049`.

| Opponent | Mean | W-L-D | Steps | Override frames |
| --- | ---: | --- | ---: | ---: |
| `builtin` | `0.16` | `13-8-29` | `150000` | `140` |
| `random` | `4.72` | `50-0-0` | `38672` | `137` |
| `initial` | `4.66` | `50-0-0` | `44847` | `149` |
| `improved-v0` | `4.68` | `50-0-0` | `43451` | `142` |
| `improved-v2` | `4.44` | `49-1-0` | `76129` | `170` |
| `improved-v3` | `2.86` | `47-1-2` | `137840` | `155` |
| `improved-v4` | `2.24` | `42-1-7` | `143705` | `148` |
| `improved-v5` | `1.14` | `32-7-11` | `150000` | `166` |
| `improved-v6` | `1.20` | `32-7-11` | `150000` | `164` |

Reference `rally-serve` fixed-pool rows from the existing generation-4
development note were: `builtin 0.14`, `random 4.74`, `initial 4.68`,
`improved-v0 4.70`, `improved-v2 4.38`, `improved-v3 2.98`,
`improved-v4 2.34`, `improved-v5 1.16`, `improved-v6 1.22`.

Against that reference, `struct_press_backward_jump` improved `builtin` by
`+0.02` and `improved-v2` by `+0.06`, but regressed `random`, `initial`,
`improved-v0`, `improved-v3`, `improved-v4`, `improved-v5`, and `improved-v6`.

## Failure Analysis

Disabling `rear_wall_press` was harmful on the short screen. Low-far-right point
losses rose sharply, and mean fell from `0.3125` for `rally_serve_reference` to
`-0.5000`. The press branch is still doing useful work and should not be
removed.

Forward/no-jump, forward/jump, and no-op press overrides were also harmful. They
converted the short-screen no-loss reference into `1-6-9` W-L-D and clustered
losses at low far-right states. That argues against treating rear-wall press as
a forward contest or passive stall branch.

The only positive built-in full-dev probe, `struct_press_backward_jump`, is a
very narrow perturbation. It forced `011` on 140 frames across 150000 built-in
steps and raised the mean from `0.14` to `0.16` without changing W-L-D. The loss
bucket improvement was one fewer low-mid-right loss, not a direct large
reduction in rear-wall losses.

The fixed-pool check exposed the weakness of the built-in-only signal. The same
candidate regressed most archived-opponent cells, especially `improved-v3`
(`2.86` vs `2.98`) and `improved-v4` (`2.24` vs `2.34`), and added losses where
the reference had none. This looks like a tiny built-in-specific trajectory
shift rather than a robust structural improvement.

Rear-wall-low-jump action swaps were neutral on full built-in dev. They matched
`rally_serve_reference` exactly at mean `0.14`, W-L-D `13-8-29`, and `150000`
steps, so changing only that action is not enough to resolve remaining losses.

## Promotion Recommendation

Do not promote any rear-wall press or rear-wall-low-jump variant from this run.

`struct_press_backward_jump` is the best built-in candidate, but the fixed
development opponent-pool check fails the robustness bar. Keep current
`rally-serve` as the generation-4 reference unless a later development-only
candidate improves built-in performance without the archived-opponent
regressions shown here.

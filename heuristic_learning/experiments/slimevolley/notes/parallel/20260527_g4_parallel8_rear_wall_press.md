# Generation-4 Parallel8 Rear-Wall Press Probe

Date: 2026-05-27

Worker: C

## Protocol

Development-only structural branch probe for `rear_wall_press`,
`rear_wall_low_jump`, and rear-wall terminal losses. No maintained policy,
ledger, summary, report, holdout, or audit file was edited.

Repository result artifact:

- `heuristic_learning/experiments/slimevolley/results/generation_4_parallel8_rear_wall_press_probe.json`

Transient probe code:

- `/tmp/g4_parallel8_rear_wall_press_probe.py`

Command run from `heuristic_learning/`:

- `PYTHONPATH=. .venv/bin/python /tmp/g4_parallel8_rear_wall_press_probe.py --phase screen`

Short-screen seeds used exactly:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

No full development follow-up was run because no candidate cleared the short
screen. No holdout seeds `10000..10049` or audit seeds `11000..11049` were
used.

## Candidate Definitions

All branch candidates inherit `SlimeVolleyPostContactPolicy` and alter only
frames where the inherited branch diagnostics report `rear_wall_press` or
`rear_wall_low_jump`.

| Candidate | Structural label | Definition |
| --- | --- | --- |
| `rally_reference` | reference | Current `SlimeVolleyRallyServePolicy`. |
| `post_contact_reference` | reference | Current `SlimeVolleyPostContactPolicy`; this is the direct base for branch probes. |
| `baseline_rnn` | neural comparator | Packaged built-in RNN policy wrapper. |
| `rw_press_slow_low_vertical_jump` | structural branch action | In `rear_wall_press`, if `0.20 <= ball_y <= 0.38`, `ball_vy < -0.45`, `ball_vx <= 0.08`, `abs(ball_x - agent_x) <= 0.22`, and `agent_x >= 1.88`, replace the base action with `001`. |
| `rw_press_slow_low_forward_jump` | structural branch action | Same slow-low `rear_wall_press` gate, but replace the base action with `101`. |
| `rw_press_narrow_backjump` | structural branch action | In `rear_wall_press`, if `0.24 <= ball_y <= 0.44`, `ball_vy < -0.50`, `-0.08 <= ball_vx <= 0.12`, `abs(ball_x - agent_x) <= 0.28`, and `agent_x >= 1.86`, replace the base action with `011`. |
| `rw_press_low_release_nojump` | structural branch action | In `rear_wall_press`, if `ball_y <= 0.34`, `ball_vx < -0.04`, `ball_vy < -0.34`, `ball_x >= 2.02`, and `agent_x >= 1.88`, replace the base action with `100`. |
| `rw_low_jump_vertical` | structural branch action | In `rear_wall_low_jump`, replace current `101` with `001`. |
| `rw_low_jump_backjump` | structural branch action | In `rear_wall_low_jump`, replace current `101` with `011`. |
| `rw_low_jump_high_gate` | structural branch action | In `rear_wall_low_jump`, suppress jump below `ball_y < 0.26`, replacing `101` with `100`. |

## Short-Screen Results

Seeds: `9000..9015`. Opponents: `builtin`, `improved-v4`, `improved-v5`,
`improved-v6`.

| Candidate | Opponent | Mean | W-L-D | Steps | Triggers | Action changes |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| `rally_reference` | `builtin` | `0.3125` | `4-0-12` | `48000` | `0` | `0` |
| `rally_reference` | `improved-v4` | `2.5625` | `15-0-1` | `44632` | `0` | `0` |
| `rally_reference` | `improved-v5` | `1.1250` | `9-3-4` | `48000` | `0` | `0` |
| `rally_reference` | `improved-v6` | `1.1875` | `9-3-4` | `48000` | `0` | `0` |
| `post_contact_reference` | `builtin` | `0.3125` | `4-0-12` | `48000` | `0` | `0` |
| `post_contact_reference` | `improved-v4` | `2.7500` | `15-0-1` | `44527` | `0` | `0` |
| `post_contact_reference` | `improved-v5` | `1.3125` | `9-3-4` | `47686` | `0` | `0` |
| `post_contact_reference` | `improved-v6` | `1.3750` | `9-3-4` | `47686` | `0` | `0` |
| `baseline_rnn` | `builtin` | `0.1250` | `6-4-6` | `48000` | `0` | `0` |
| `baseline_rnn` | `improved-v4` | `3.2500` | `16-0-0` | `40985` | `0` | `0` |
| `baseline_rnn` | `improved-v5` | `2.3125` | `14-1-1` | `46353` | `0` | `0` |
| `baseline_rnn` | `improved-v6` | `2.5625` | `14-1-1` | `45819` | `0` | `0` |
| `rw_press_slow_low_vertical_jump` | `builtin` | `0.3125` | `4-0-12` | `48000` | `1` | `1` |
| `rw_press_slow_low_vertical_jump` | `improved-v4` | `2.8750` | `16-0-0` | `44527` | `3` | `3` |
| `rw_press_slow_low_vertical_jump` | `improved-v5` | `1.2500` | `9-4-3` | `47686` | `4` | `4` |
| `rw_press_slow_low_vertical_jump` | `improved-v6` | `1.3125` | `9-4-3` | `47686` | `4` | `4` |
| `rw_press_slow_low_forward_jump` | `builtin` | `0.3125` | `4-0-12` | `48000` | `1` | `1` |
| `rw_press_slow_low_forward_jump` | `improved-v4` | `2.7500` | `16-0-0` | `44527` | `3` | `3` |
| `rw_press_slow_low_forward_jump` | `improved-v5` | `1.2500` | `9-4-3` | `47686` | `4` | `4` |
| `rw_press_slow_low_forward_jump` | `improved-v6` | `1.3125` | `9-4-3` | `47686` | `4` | `4` |
| `rw_press_narrow_backjump` | `builtin` | `0.3125` | `4-0-12` | `48000` | `0` | `0` |
| `rw_press_narrow_backjump` | `improved-v4` | `2.7500` | `15-0-1` | `44527` | `0` | `0` |
| `rw_press_narrow_backjump` | `improved-v5` | `1.3125` | `9-3-4` | `47686` | `0` | `0` |
| `rw_press_narrow_backjump` | `improved-v6` | `1.3750` | `9-3-4` | `47686` | `0` | `0` |
| `rw_press_low_release_nojump` | `builtin` | `0.3125` | `4-0-12` | `48000` | `0` | `0` |
| `rw_press_low_release_nojump` | `improved-v4` | `2.7500` | `15-0-1` | `44527` | `0` | `0` |
| `rw_press_low_release_nojump` | `improved-v5` | `1.2500` | `9-4-3` | `47686` | `2` | `2` |
| `rw_press_low_release_nojump` | `improved-v6` | `1.3125` | `9-4-3` | `47686` | `2` | `2` |
| `rw_low_jump_vertical` | `builtin` | `0.3125` | `4-0-12` | `48000` | `6` | `6` |
| `rw_low_jump_vertical` | `improved-v4` | `2.7500` | `15-0-1` | `44527` | `2` | `2` |
| `rw_low_jump_vertical` | `improved-v5` | `1.3125` | `9-3-4` | `47686` | `9` | `9` |
| `rw_low_jump_vertical` | `improved-v6` | `1.3750` | `9-3-4` | `47686` | `9` | `9` |
| `rw_low_jump_backjump` | `builtin` | `0.3125` | `4-0-12` | `48000` | `5` | `5` |
| `rw_low_jump_backjump` | `improved-v4` | `2.7500` | `15-0-1` | `44527` | `2` | `2` |
| `rw_low_jump_backjump` | `improved-v5` | `1.3125` | `9-3-4` | `47686` | `9` | `9` |
| `rw_low_jump_backjump` | `improved-v6` | `1.3750` | `9-3-4` | `47686` | `9` | `9` |
| `rw_low_jump_high_gate` | `builtin` | `0.3125` | `4-0-12` | `48000` | `3` | `3` |
| `rw_low_jump_high_gate` | `improved-v4` | `2.7500` | `15-0-1` | `44527` | `2` | `2` |
| `rw_low_jump_high_gate` | `improved-v5` | `1.3125` | `9-3-4` | `47686` | `6` | `6` |
| `rw_low_jump_high_gate` | `improved-v6` | `1.3750` | `9-3-4` | `47686` | `6` | `6` |

## Failure Analysis

`rw_press_slow_low_vertical_jump` was the only branch with a visible short-row
gain: it changed one built-in frame without changing score and improved
`improved-v4` from `2.7500`, W-L-D `15-0-1`, to `2.8750`, W-L-D `16-0-0`.
However, the same gate regressed both harder archived rows from W-L-D `9-3-4`
to `9-4-3`, with terminal rear-wall losses attributed to the override mode.
That is a structural tradeoff, not a promotion candidate.

`rw_press_slow_low_forward_jump` changed the same narrow geometry to `101`
instead of `001`. It did not improve mean over `post_contact_reference` on
`improved-v4` and also added the same extra loss on `improved-v5` and
`improved-v6`.

`rw_press_narrow_backjump` was behaviorally inert on this screen; its stricter
gate never fired. `rw_press_low_release_nojump` fired only on `improved-v5` and
`improved-v6`, where it added a loss in each row.

The `rear_wall_low_jump` action variants were active but score-inert.
`rw_low_jump_vertical`, `rw_low_jump_backjump`, and `rw_low_jump_high_gate`
changed `101` into `001`, `011`, or `100` on several frames, but every short
row matched `post_contact_reference` exactly. They relabeled the same terminal
rear-wall loss bucket without reducing it.

The useful negative signal is that the remaining rear-wall failures are not
fixed by single-frame action substitutions in the current branches. Narrow jump
injections can recover one `improved-v4` draw, but they also create hard-row
losses; direct `rear_wall_low_jump` action swaps are too local to move score.

## Promotion Recommendation

Do not promote any candidate from this run.

No candidate cleared the short-screen gate across `builtin`, `improved-v4`,
`improved-v5`, and `improved-v6`, so no full `9000..9049` development pool,
holdout, or audit evaluation was warranted. The best-scoring branch,
`rw_press_slow_low_vertical_jump`, fails on archived hard-opponent robustness
despite a narrow `improved-v4` gain.

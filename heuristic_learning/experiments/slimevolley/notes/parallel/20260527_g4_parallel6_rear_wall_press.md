# Generation-4 Parallel6 Rear-Wall Press Probe

Date: 2026-05-27

Worker: C

## Protocol

This was a development-only structural branch probe for `rear_wall_press` and
rear-wall low-ball losses. No maintained source, policy, test, ledger, summary,
report, holdout, or audit file was edited. The only repository artifact written
by this run is this note.

Transient code and JSON stayed in `/tmp`:

- `/tmp/g4_parallel6_rear_wall_press.py`
- `/tmp/g4_parallel6_rear_wall_press_screen.json`
- `/tmp/g4_parallel6_rear_wall_press_full_builtins.json`
- `/tmp/g4_parallel6_rear_wall_press_fixed_pool.json`

Short-screen seeds used exactly:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full development and fixed-pool seeds used exactly:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

No holdout or audit seeds were used. In particular, generation-4 holdout seeds
`10000..10049` and audit seeds `11000..11049` were not run.

## Candidate Definitions

| Candidate | Type | Definition |
| --- | --- | --- |
| `rally_reference` | reference structural plus scalar/config | Current `SlimeVolleyRallyServePolicy`, including scalar-tuned baseline, late-contact attack, and rally-serve detector. |
| `baseline_rnn` | neural comparator | Shipped SlimeVolley RNN wrapper. |
| `rw_order_floor_preempt` | structural branch-order | When inherited `rear_wall_press` overlaps `falling_floor_intercept`, use the floor-intercept action instead of the rear-wall press action. |
| `rw_order_low_rescue_preempt` | structural branch-order | When inherited `rear_wall_press` overlaps `low_ball_rescue`, use the low-rescue action instead of the rear-wall press action. |
| `rw_order_floor_then_low` | structural branch-order | Combined reorder: floor intercept first, then low rescue, both before `rear_wall_press`. |
| `rw_press_grounded_bypass_jump_suppress` | structural branch action | If `rear_wall_press` wanted a jump before front-hit suppression and the agent is grounded, close, and the ball is descending fast, force `010 -> 011`. |
| `rw_press_very_late_backjump` | structural branch action | Very narrow low rear-wall gate: `0.22 <= ball_y <= 0.38`, `ball_vy < -0.55`, `ball_vx <= 0.10`, `abs(ball_x - agent_x) <= 0.34`; force `010 -> 011`. |
| `rw_press_high_nojump` | structural branch action | For upper `rear_wall_press` states with `ball_y >= 0.54`, force backward/no-jump `010`. |
| `rw_press_bothdir_jump` | structural branch action | For close rear-wall contact states, force RNN-like both-directions+jump `111`. |
| `rw_press_rear_low_noop_brace` | structural branch action | For already-aligned very low clearing rear-wall states, force no-op/no-jump `000`. |

## Short Screen Results

Seeds: `9000..9015`. Opponents: `builtin`, `improved-v3`, `improved-v5`,
`improved-v6`.

| Candidate | Opponent | Mean | W-L-D | Steps | Overrides | Action changes |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| `rally_reference` | `builtin` | `0.3125` | `4-0-12` | `48000` | `0` | `0` |
| `rally_reference` | `improved-v3` | `3.0000` | `16-0-0` | `41298` | `0` | `0` |
| `rally_reference` | `improved-v5` | `1.1250` | `9-3-4` | `48000` | `0` | `0` |
| `rally_reference` | `improved-v6` | `1.1875` | `9-3-4` | `48000` | `0` | `0` |
| `baseline_rnn` | `builtin` | `0.1250` | `6-4-6` | `48000` | `0` | `0` |
| `baseline_rnn` | `improved-v3` | `3.9375` | `16-0-0` | `37225` | `0` | `0` |
| `baseline_rnn` | `improved-v5` | `2.3125` | `14-1-1` | `46353` | `0` | `0` |
| `baseline_rnn` | `improved-v6` | `2.5625` | `14-1-1` | `45819` | `0` | `0` |
| `rw_order_floor_preempt` | `builtin` | `-0.3125` | `1-5-10` | `48000` | `32` | `32` |
| `rw_order_floor_preempt` | `improved-v3` | `2.1250` | `12-2-2` | `39712` | `49` | `48` |
| `rw_order_floor_preempt` | `improved-v5` | `0.5000` | `6-3-7` | `46041` | `41` | `41` |
| `rw_order_floor_preempt` | `improved-v6` | `0.5000` | `6-3-7` | `46041` | `41` | `41` |
| `rw_order_low_rescue_preempt` | `builtin` | `0.1250` | `3-1-12` | `48000` | `10` | `10` |
| `rw_order_low_rescue_preempt` | `improved-v3` | `2.8750` | `15-0-1` | `42803` | `25` | `24` |
| `rw_order_low_rescue_preempt` | `improved-v5` | `1.0625` | `8-4-4` | `47823` | `36` | `36` |
| `rw_order_low_rescue_preempt` | `improved-v6` | `1.1250` | `8-4-4` | `47823` | `36` | `36` |
| `rw_order_floor_then_low` | `builtin` | `-0.5000` | `1-6-9` | `48000` | `85` | `85` |
| `rw_order_floor_then_low` | `improved-v3` | `2.1875` | `12-1-3` | `39914` | `97` | `94` |
| `rw_order_floor_then_low` | `improved-v5` | `0.4375` | `6-4-6` | `46040` | `97` | `97` |
| `rw_order_floor_then_low` | `improved-v6` | `0.4375` | `6-4-6` | `46040` | `97` | `97` |
| `rw_press_grounded_bypass_jump_suppress` | `builtin` | `0.3125` | `4-0-12` | `48000` | `3` | `0` |
| `rw_press_grounded_bypass_jump_suppress` | `improved-v3` | `2.8750` | `16-0-0` | `41098` | `8` | `7` |
| `rw_press_grounded_bypass_jump_suppress` | `improved-v5` | `1.1250` | `9-3-4` | `48000` | `3` | `2` |
| `rw_press_grounded_bypass_jump_suppress` | `improved-v6` | `1.1875` | `9-3-4` | `48000` | `3` | `2` |
| `rw_press_very_late_backjump` | `builtin` | `0.3125` | `4-0-12` | `48000` | `1` | `1` |
| `rw_press_very_late_backjump` | `improved-v3` | `3.0000` | `16-0-0` | `41298` | `3` | `1` |
| `rw_press_very_late_backjump` | `improved-v5` | `1.1250` | `9-3-4` | `48000` | `4` | `3` |
| `rw_press_very_late_backjump` | `improved-v6` | `1.1875` | `9-3-4` | `48000` | `4` | `3` |
| `rw_press_high_nojump` | `builtin` | `0.2500` | `4-1-11` | `48000` | `31` | `17` |
| `rw_press_high_nojump` | `improved-v3` | `3.0000` | `16-0-0` | `41298` | `38` | `28` |
| `rw_press_high_nojump` | `improved-v5` | `1.1250` | `9-3-4` | `48000` | `34` | `25` |
| `rw_press_high_nojump` | `improved-v6` | `1.1875` | `9-3-4` | `48000` | `34` | `25` |
| `rw_press_bothdir_jump` | `builtin` | `0.2500` | `4-1-11` | `48000` | `9` | `9` |
| `rw_press_bothdir_jump` | `improved-v3` | `2.8125` | `15-0-1` | `41019` | `18` | `18` |
| `rw_press_bothdir_jump` | `improved-v5` | `0.8125` | `8-5-3` | `48000` | `20` | `20` |
| `rw_press_bothdir_jump` | `improved-v6` | `0.8750` | `8-5-3` | `48000` | `20` | `20` |
| `rw_press_rear_low_noop_brace` | `builtin` | `0.1875` | `3-1-12` | `48000` | `1` | `1` |
| `rw_press_rear_low_noop_brace` | `improved-v3` | `2.8125` | `15-0-1` | `41104` | `5` | `5` |
| `rw_press_rear_low_noop_brace` | `improved-v5` | `1.0000` | `8-3-5` | `48000` | `3` | `3` |
| `rw_press_rear_low_noop_brace` | `improved-v6` | `1.0625` | `8-3-5` | `48000` | `3` | `3` |

## Full Built-In Check

Seeds: `9000..9049`. Opponent: `builtin`.

| Candidate | Mean | W-L-D | Steps | Overrides | Action changes |
| --- | ---: | --- | ---: | ---: | ---: |
| `rally_reference` | `0.1400` | `13-8-29` | `150000` | `0` | `0` |
| `baseline_rnn` | `0.1200` | `18-12-20` | `150000` | `0` | `0` |
| `rw_press_grounded_bypass_jump_suppress` | `0.1600` | `13-8-29` | `150000` | `16` | `13` |
| `rw_press_very_late_backjump` | `0.1400` | `13-8-29` | `150000` | `5` | `4` |

Built-in action-change patterns:

| Candidate | Action-change pattern | Count |
| --- | --- | ---: |
| `rw_press_grounded_bypass_jump_suppress` | `010 -> 011` | `13` |
| `rw_press_very_late_backjump` | `010 -> 011` | `4` |

The full built-in check made `rw_press_grounded_bypass_jump_suppress` the only
promising candidate by score, so it received the fixed development opponent-pool
check below before any promotion recommendation.

## Fixed Development Opponent-Pool Check

Seeds: `9000..9049`. Opponents: `builtin`, `random`, `initial`,
`improved-v0`, `improved-v2`, `improved-v3`, `improved-v4`, `improved-v5`,
`improved-v6`.

| Opponent | `rally_reference` mean/W-L-D/steps | `rw_press_grounded_bypass_jump_suppress` mean/W-L-D/steps | Delta | Candidate overrides / changes |
| --- | --- | --- | ---: | ---: |
| `builtin` | `0.1400` / `13-8-29` / `150000` | `0.1600` / `13-8-29` / `150000` | `+0.0200` | `16 / 13` |
| `random` | `4.7400` / `50-0-0` / `38217` | `4.7200` / `50-0-0` / `38814` | `-0.0200` | `12 / 11` |
| `initial` | `4.6800` / `50-0-0` / `44634` | `4.6600` / `50-0-0` / `45025` | `-0.0200` | `14 / 13` |
| `improved-v0` | `4.7000` / `50-0-0` / `43242` | `4.6800` / `50-0-0` / `43629` | `-0.0200` | `12 / 11` |
| `improved-v2` | `4.3800` / `49-1-0` / `76391` | `4.4600` / `49-1-0` / `75883` | `+0.0800` | `16 / 15` |
| `improved-v3` | `2.9800` / `48-0-2` / `138122` | `2.8800` / `47-1-2` / `137642` | `-0.1000` | `15 / 14` |
| `improved-v4` | `2.3400` / `44-0-6` / `143814` | `2.3000` / `43-1-6` / `143603` | `-0.0400` | `14 / 13` |
| `improved-v5` | `1.1600` / `32-7-11` / `149716` | `1.1400` / `32-7-11` / `150000` | `-0.0200` | `12 / 11` |
| `improved-v6` | `1.2200` / `32-7-11` / `149716` | `1.2000` / `32-7-11` / `150000` | `-0.0200` | `12 / 11` |

Candidate fixed-pool action-change pattern was consistently `010 -> 011`
across all changed frames.

## Failure Analysis

Branch-order probes failed quickly. Letting `falling_floor_intercept` or
`low_ball_rescue` preempt `rear_wall_press` introduced built-in losses and
regressed the archived hard opponents. The combined reorder was worst:
`rw_order_floor_then_low` fell to `-0.5000`, W-L-D `1-6-9` against built-in on
the short screen and also hurt `improved-v5` and `improved-v6`. This suggests
the current branch order is important: once the ball is in far-right low
geometry, the generic low-rescue/floor-intercept actions are too passive or too
misaligned.

Broad or unusual action substitutions were also negative. `rw_press_high_nojump`
and `rw_press_bothdir_jump` each added a built-in loss on the short screen.
`rw_press_bothdir_jump` also regressed both hard archived rows to `8-5-3`.
`rw_press_rear_low_noop_brace` changed only a few frames but still added a
built-in loss and reduced the hard archived means.

The sparse jump probes were the only non-collapsing variants. `rw_press_very_late_backjump`
tied the full built-in reference exactly at `0.1400`, W-L-D `13-8-29`, with
only four changed frames, so it is behaviorally too small to justify promotion.

`rw_press_grounded_bypass_jump_suppress` improved full built-in mean to
`0.1600` and reduced built-in terminal `grounded_low_receive` losses from `10`
to `9`, but the fixed-pool check repeats the known rear-wall pattern: a small
built-in gain plus an `improved-v2` gain, offset by regressions to `random`,
`initial`, `improved-v0`, `improved-v3`, `improved-v4`, `improved-v5`, and
`improved-v6`. The `improved-v3` and `improved-v4` rows are the decisive
failures because each adds a loss where `rally_reference` had none.

## Promotion Recommendation

Do not promote any candidate from this run.

Best built-in result: `rw_press_grounded_bypass_jump_suppress`, mean `0.1600`,
W-L-D `13-8-29`, `150000` steps on seeds `9000..9049` against `builtin`.
Despite beating `rally_reference` and the built-in-seed `baseline_rnn` mean, it
fails the fixed generation-4 development opponent-pool check. The result should
remain a diagnostic clue: narrowly bypassing front-hit jump suppression can save
one built-in trajectory, but it is not robust enough for maintained policy code
or holdout evaluation.

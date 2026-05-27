# Generation-4 Attack Vs Baseline-RNN Trace Diagnostics

Date: 2026-05-27

## Exact Seeds Used

Generation-4 development subset only: `9000..9015`.

Exact list: `9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`.

No holdout seeds, audit seeds, `slimevolley-final-eval`, or reserved seed ranges were used. No ledger rows were appended.

## Candidate Definitions

Comparison: current workspace `attack` and `baseline-rnn`, each against opponent `builtin`.

Execution mode: no-ledger development diagnostics with `seed_start=9000`, `episodes=16`, and `trace_window=24`.

- `attack`: structural heuristic candidate `slimevolley_attack_candidate`, `candidate_status=partial_not_promoted`. It inherits `improved-tuned` scalar revision `g4-scalar-tuned-v2` and adds the `late_contact_attack` rule: `ball_x > 0.05`, `0.28 <= ball_y <= 0.65`, `ball_vx < -0.35`, `ball_vy < -0.10`, `0.04 <= agent_x - ball_x <= 0.28`, action `101`.
- `baseline-rnn`: neural comparator `slimevolley_builtin_rnn`, the shipped `slimevolleygym.slimevolley.BaselinePolicy` wrapper with `parameter_count=120`.

This artifact is diagnostic only. It is not promotion evidence and does not justify opening holdout or audit seeds.

## Commands

Sanity runs:

```bash
PYTHONPATH=. .venv/bin/python -m hl_benchmark.custom_envs.slimevolley.evaluate --policy attack --opponent builtin --split dev --seed-start 9000 --episodes 16 --trace-window 24 --no-ledger
PYTHONPATH=. .venv/bin/python -m hl_benchmark.custom_envs.slimevolley.evaluate --policy baseline-rnn --opponent builtin --split dev --seed-start 9000 --episodes 16 --trace-window 24 --no-ledger
```

Both were followed by equivalent no-ledger in-memory aggregation calls to inspect `per_episode` point events and trace windows.

## Headline Metrics

| Policy | Score mean | W/L/D | Environment steps | Point won/lost | Score range |
| --- | ---: | --- | ---: | ---: | --- |
| `attack` | `-0.125` | `2/4/10` | `48000` | `5/7` | `-1..1` |
| `baseline-rnn` | `0.125` | `6/4/6` | `48000` | `10/8` | `-2..2` |

Same-seed comparison: `baseline-rnn - attack = +0.25` mean score. Baseline was better on `7` seeds, attack was better on `3`, and `6` tied.

Outcome conversions from `attack` to `baseline-rnn`: `draw->draw=4`, `draw->loss=3`, `draw->win=3`, `loss->draw=2`, `loss->loss=1`, `loss->win=1`, `win->win=2`.

## Per-Seed Scores

| Seed | `attack` | `baseline-rnn` | Delta RNN-attack |
| ---: | --- | --- | ---: |
| `9000` | `0 draw` | `0 draw` | `0` |
| `9001` | `-1 loss` | `0 draw` | `+1` |
| `9002` | `0 draw` | `0 draw` | `0` |
| `9003` | `0 draw` | `1 win` | `+1` |
| `9004` | `0 draw` | `1 win` | `+1` |
| `9005` | `0 draw` | `-2 loss` | `-2` |
| `9006` | `-1 loss` | `0 draw` | `+1` |
| `9007` | `0 draw` | `-1 loss` | `-1` |
| `9008` | `0 draw` | `1 win` | `+1` |
| `9009` | `1 win` | `2 win` | `+1` |
| `9010` | `0 draw` | `-1 loss` | `-1` |
| `9011` | `-1 loss` | `-1 loss` | `0` |
| `9012` | `-1 loss` | `1 win` | `+2` |
| `9013` | `0 draw` | `0 draw` | `0` |
| `9014` | `1 win` | `1 win` | `0` |
| `9015` | `0 draw` | `0 draw` | `0` |

## Action Frequencies

| Policy | `000` | `001` | `010` | `011` | `100` | `101` | `110` | `111` | Jump-bit rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `attack` | `21446` | `3088` | `11206` | `425` | `10843` | `992` | `0` | `0` | `9.4%` |
| `baseline-rnn` | `962` | `4079` | `7646` | `374` | `2875` | `17208` | `13946` | `910` | `47.0%` |

`attack` is dominated by no-op and single-direction movement. It almost never uses forward+jump compared with the neural comparator and never emits `110` or `111` in this subset. `baseline-rnn` spends most of its terminal wins on `101`, while also using substantial `110` in nonterminal trace windows.

## Point Buckets

Terminal bucket definition: `high_or_mid_terminal` if `ball_y > 0.65`; otherwise `low_left_or_net` if `ball_x <= 0.35`, `low_far_right` if `ball_x >= 1.85`, `low_mid_right` if `ball_x >= 1.00`, and `low_other_own_side` otherwise.

| Bucket | `attack` losses | `baseline-rnn` losses |
| --- | ---: | ---: |
| `low_left_or_net` | `3` | `1` |
| `low_far_right` | `2` | `5` |
| `low_mid_right` | `1` | `2` |
| `low_other_own_side` | `1` | `0` |

All terminal wins for both policies landed in `low_left_or_net`: `attack=5`, `baseline-rnn=10`.

## Terminal Modes And Actions

| Policy/outcome | Terminal modes | Terminal actions |
| --- | --- | --- |
| `attack` lost | `grounded_low_receive=3`, `low_ball_rescue=2`, `rear_wall_low_jump=1`, `rear_wall_press=1` | `101=3`, `100=2`, `010=1`, `000=1` |
| `attack` won | `intercept=3`, `recovery=2` | `100=3`, `010=1`, `000=1` |
| `baseline-rnn` lost | `neural_or_unlabeled=8` | `001=5`, `101=2`, `010=1` |
| `baseline-rnn` won | `neural_or_unlabeled=10` | `101=9`, `110=1` |

The clearest mode split is that `attack` wins from ordinary `intercept`/`recovery` terminal states but loses when the low-ball special modes own the last decision. Its `late_contact_attack` branch does not appear as the terminal mode for a loss here, but it appears in `4/7` loss trace windows shortly before lower-level low receive modes take over.

## Trace-Window Signals

Trace-window counts are over the last `24` frames before each point. They are diagnostic, not causal proof.

| Policy/outcome | Contact-like window | Front/net low window | Rear low window | Low own-side window | `vx` flip | `vy` upward flip |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `attack` lost | `7/7` | `3/7` | `4/7` | `7/7` | `5/7` | `3/7` |
| `attack` won | `0/5` | `5/5` | `0/5` | `0/5` | `4/5` | `1/5` |
| `baseline-rnn` lost | `8/8` | `1/8` | `5/8` | `8/8` | `5/8` | `1/8` |
| `baseline-rnn` won | `1/10` | `10/10` | `0/10` | `0/10` | `7/10` | `5/10` |

`attack` losses always had contact-like, low own-side geometry in the 24-frame window, and most had a recent ball `vx` sign flip. That makes the remaining issue look less like missing ball tracking and more like a post-contact/recovery timing problem.

## Attack Loss Trace Rows

| Seed | Step | Terminal mode/action | Bucket | Ball `(x,y,vx,vy)` | Agent `(x,y,vy)` | Last 6 modes |
| ---: | ---: | --- | --- | --- | --- | --- |
| `9001` | `522` | `rear_wall_press / 010` | `low_far_right` | `(2.350, 0.240, 0.442, -3.330)` | `(2.250, 0.409, -0.610)` | `falling_floor_intercept > rear_wall_press > rear_wall_press > rear_wall_press > rear_wall_press > rear_wall_press` |
| `9006` | `71` | `low_ball_rescue / 101` | `low_left_or_net` | `(0.323, 0.233, -1.375, -3.266)` | `(0.500, 0.342, 0.958)` | `low_ball_rescue > low_ball_rescue > low_ball_rescue > low_ball_rescue > low_ball_rescue > low_ball_rescue` |
| `9006` | `2617` | `grounded_low_receive / 000` | `low_left_or_net` | `(0.170, 0.227, 2.104, -0.798)` | `(0.258, 0.409, -0.610)` | `late_contact_attack > late_contact_attack > late_contact_attack > late_contact_attack > grounded_low_receive > grounded_low_receive` |
| `9011` | `845` | `low_ball_rescue / 101` | `low_mid_right` | `(1.381, 0.216, -2.141, -0.693)` | `(1.600, 0.275, 1.154)` | `late_contact_attack > late_contact_attack > late_contact_attack > low_ball_rescue > low_ball_rescue > low_ball_rescue` |
| `9012` | `986` | `rear_wall_low_jump / 101` | `low_far_right` | `(2.318, 0.230, -0.753, -0.960)` | `(2.125, 0.150, 0.000)` | `rear_wall_press > rear_wall_press > rear_wall_press > rear_wall_press > rear_wall_low_jump > rear_wall_low_jump` |
| `9013` | `225` | `grounded_low_receive / 100` | `low_other_own_side` | `(0.732, 0.222, -2.055, -0.917)` | `(1.083, 0.419, 0.664)` | `low_ball_rescue > low_ball_rescue > low_ball_rescue > low_ball_rescue > grounded_low_receive > grounded_low_receive` |
| `9014` | `1444` | `grounded_low_receive / 100` | `low_left_or_net` | `(0.107, 0.226, -1.627, -1.554)` | `(0.317, 0.453, 0.468)` | `late_contact_attack > late_contact_attack > late_contact_attack > late_contact_attack > grounded_low_receive > grounded_low_receive` |

## Baseline-RNN Loss Trace Rows

| Seed | Step | Terminal action | Bucket | Ball `(x,y,vx,vy)` | Agent `(x,y,vy)` | Last 6 actions |
| ---: | ---: | --- | --- | --- | --- | --- |
| `9001` | `2742` | `001` | `low_far_right` | `(2.161, 0.208, 0.714, -0.776)` | `(1.892, 0.342, 0.958)` | `101 001 001 001 001 001` |
| `9002` | `224` | `001` | `low_mid_right` | `(1.716, 0.226, 1.337, -1.810)` | `(1.250, 0.478, -0.120)` | `001 001 001 001 001 001` |
| `9005` | `468` | `001` | `low_mid_right` | `(1.363, 0.236, 1.667, -1.511)` | `(1.075, 0.310, 1.056)` | `001 001 001 001 001 001` |
| `9005` | `2412` | `001` | `low_far_right` | `(2.327, 0.247, -0.308, -1.965)` | `(2.075, 0.342, 0.958)` | `011 101 101 001 101 001` |
| `9007` | `1449` | `010` | `low_far_right` | `(1.901, 0.222, 1.895, -1.212)` | `(1.542, 0.409, -0.610)` | `010 010 010 010 010 010` |
| `9010` | `2585` | `001` | `low_far_right` | `(2.350, 0.241, 1.274, -2.000)` | `(2.192, 0.275, 1.154)` | `010 010 111 101 001 001` |
| `9011` | `2527` | `101` | `low_far_right` | `(2.181, 0.239, -1.268, -1.191)` | `(1.900, 0.465, 0.370)` | `001 101 001 101 101 101` |
| `9015` | `2682` | `101` | `low_left_or_net` | `(0.290, 0.211, 1.803, -1.346)` | `(0.325, 0.482, -0.022)` | `101 101 001 001 001 101` |

## Failure Analysis

On this fixed development subset, `baseline-rnn` is ahead by `+0.25` mean score and converts more episodes into wins (`6` vs `2`), even though both policies have `4` losses. The extra RNN value comes from more point wins (`10` vs `5`) rather than fewer point losses.

The `attack` heuristic's failure shape is specific. Terminal losses are not random: `3/7` end in `grounded_low_receive`, `2/7` in `low_ball_rescue`, and the remaining `2/7` in rear-wall modes. In the trace windows, `late_contact_attack` appears before several losses, then control falls through to `grounded_low_receive` or `low_ball_rescue`. This suggests the late attack rule can create or enter awkward post-contact states that the downstream low receive logic cannot resolve reliably.

The neural comparator has a different profile. It wins almost exclusively with terminal `101` actions in front/net low buckets (`10/10` wins), but its losses are mostly far-right or mid-right low balls (`7/8`). In other words, the RNN is better at converting front/net terminal opportunities into points, while still vulnerable to low balls deep on the right.

Candidate next structural ideas:

- Add short-history post-contact state to distinguish a newly redirected ball from an untouched incoming ball before choosing `grounded_low_receive` versus a jump-combo contact.
- Add a trajectory-history low receive rule keyed on recent `vx` flip, agent airborne state, and predicted floor intercept, not just the current `ball_y`/`ball_vy`.
- Split rear-wall recovery from rear-wall attack: the `rear_wall_press` and `rear_wall_low_jump` losses show low balls near `x >= 2.1` where repeated mode commitment still misses.
- Explore a narrow front/net conversion rule inspired by the RNN terminal wins, but only as a transparent rule with development-seed evaluation against the fixed dev pool.

## Promotion Recommendation

Do not promote from this artifact. This is development-only trace evidence on `9000..9015`.

`attack` remains weaker than `baseline-rnn` on this subset (`-0.125` vs `0.125` mean, `2/4/10` vs `6/4/6` W/L/D). A later candidate would need fixed generation-4 development evaluation before any promotion discussion, and no holdout or audit seeds should be opened for this diagnostic branch.

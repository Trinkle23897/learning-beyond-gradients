# Generation-4 Parallel 3 Trace Diagnostics: Attack, Rally-Serve, Net-Pressure, Baseline-RNN

Date: 2026-05-27

## Exact Seeds Used

Generation-4 development seeds only: `9000..9049`.

Exact list: `9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`.

No holdout seeds, audit seeds, or `slimevolley-final-eval` runs were used. No canonical ledger or summary was appended; the diagnostic harness called `evaluate_slimevolley` with `ledger_path=None`, `summary_path=None`, opponent `builtin`, `seed_start=9000`, `episodes=50`, and `trace_window=24`.

## Policies Compared

- `attack`: generation-4 late-contact attack candidate, current-frame structural rules plus scalar/config tuning.
- `rally-serve`: generation-4 rally-reset serve detector on top of `attack`; finite serve macro/cooldown state, but no stacked observation history for low receive.
- `net-pressure`: present in the current policy registry; generation-5 front-court pressure probe on top of `rally-serve`.
- `baseline-rnn`: packaged `slimevolleygym.slimevolley.BaselinePolicy` RNN comparator.

This artifact is diagnostics only. It is not benchmark promotion evidence.

## Headline Metrics

| Policy | Score mean | W/L/D | Environment steps | Point won/lost |
| --- | ---: | --- | ---: | ---: |
| `attack` | `-0.3000` | `7/18/25` | `150000` | `17/32` |
| `rally-serve` | `0.1400` | `13/8/29` | `150000` | `25/18` |
| `net-pressure` | `-0.2200` | `7/14/29` | `150000` | `19/30` |
| `baseline-rnn` | `0.1200` | `18/12/20` | `150000` | `31/25` |

Same-seed deltas:

| Comparison | Mean delta | Improved / worse / same seeds |
| --- | ---: | --- |
| `rally-serve - attack` | `+0.44` | `19 / 5 / 26` |
| `rally-serve - baseline-rnn` | `+0.02` | `17 / 16 / 17` |
| `net-pressure - rally-serve` | `-0.36` | `8 / 21 / 21` |
| `net-pressure - baseline-rnn` | `-0.34` | `13 / 25 / 12` |

## Action Frequencies

| Policy | `000` | `001` | `010` | `011` | `100` | `101` | `110` | `111` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `attack` | `67891` | `10569` | `34068` | `1363` | `32965` | `3144` | `0` | `0` |
| `rally-serve` | `68654` | `10661` | `33496` | `1391` | `32347` | `3451` | `0` | `0` |
| `net-pressure` | `66716` | `9702` | `33469` | `1334` | `32046` | `6733` | `0` | `0` |
| `baseline-rnn` | `2891` | `12644` | `23751` | `1184` | `9288` | `53725` | `43727` | `2790` |

`net-pressure` nearly doubles `101` usage versus `rally-serve` (`6733` vs `3451`) but loses score, wins, and point conversion. The issue is not simply that the heuristics need more forward+jump. The RNN has a very different full-action distribution, while the heuristic family still never emits `110` or `111`.

## Point Event Buckets

Terminal bucket definition: `high_or_mid_terminal` if `ball_y > 0.65`; otherwise `low_left_or_net` if `ball_x <= 0.35`, `low_far_right` if `ball_x >= 1.85`, `low_mid_right` if `ball_x >= 1.00`, and `low_other_own_side` otherwise.

| Bucket | `attack` losses | `rally-serve` losses | `net-pressure` losses | `baseline-rnn` losses |
| --- | ---: | ---: | ---: | ---: |
| `low_left_or_net` | `17` | `11` | `13` | `7` |
| `low_far_right` | `8` | `4` | `4` | `16` |
| `low_mid_right` | `2` | `1` | `4` | `2` |
| `low_other_own_side` | `5` | `2` | `9` | `0` |

All terminal point wins for all policies were `low_left_or_net`: `attack=17`, `rally-serve=25`, `net-pressure=19`, `baseline-rnn=31`. The comparator wins more front/net terminals; `net-pressure` adds pressure but also reopens low own-side failures.

## Terminal Modes And Actions

| Policy | Terminal loss modes | Terminal loss actions |
| --- | --- | --- |
| `attack` | `grounded_low_receive=16`, `low_ball_rescue=8`, `rear_wall_low_jump=4`, `rear_wall_press=4` | `101=12`, `100=11`, `010=5`, `000=4` |
| `rally-serve` | `grounded_low_receive=10`, `rear_wall_low_jump=4`, `low_ball_rescue=2`, `late_contact_attack=1`, `late_low_ball_guard=1` | `100=8`, `101=7`, `000=3` |
| `net-pressure` | `grounded_low_receive=13`, `low_ball_rescue=9`, `late_low_ball_guard=3`, `rear_wall_low_jump=3`, `late_contact_attack=1`, `rear_wall_press=1` | `101=13`, `100=10`, `000=4`, `010=3` |
| `baseline-rnn` | `neural=25` | `101=12`, `001=9`, `010=2`, `011=1`, `110=1` |

| Policy | Terminal win modes | Terminal win actions |
| --- | --- | --- |
| `attack` | `recovery=9`, `intercept=8` | `100=7`, `010=5`, `000=5` |
| `rally-serve` | `recovery=13`, `intercept=11`, `grounded_low_receive=1` | `100=11`, `010=7`, `000=7` |
| `net-pressure` | `intercept=11`, `recovery=8` | `100=9`, `000=7`, `010=3` |
| `baseline-rnn` | `neural=31` | `101=28`, `110=2`, `001=1` |

The heuristic policies win terminal points with movement-only recovery/intercept actions, while the RNN converts most terminal wins with `101`. That is the clearest behavioral gap in the traces.

## Trace-Window Signals

Counts are event-level diagnostics over each 24-frame pre-point trace. Contact-like means a low-height abrupt ball-velocity change or sign flip was observed inside the trace; this is an inferred signal, not an engine contact callback.

| Policy/outcome | Contact-like | Front/net low | Rear low | Low own-side | `vx` flip | `vy` upward flip |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `attack` lost | `30/32` | `18/32` | `10/32` | `32/32` | `28/32` | `14/32` |
| `attack` won | `15/17` | `17/17` | `0/17` | `0/17` | `10/17` | `8/17` |
| `rally-serve` lost | `16/18` | `11/18` | `6/18` | `18/18` | `14/18` | `7/18` |
| `rally-serve` won | `23/25` | `25/25` | `0/25` | `1/25` | `16/25` | `8/25` |
| `net-pressure` lost | `29/30` | `13/30` | `6/30` | `30/30` | `26/30` | `16/30` |
| `net-pressure` won | `16/19` | `19/19` | `0/19` | `1/19` | `14/19` | `4/19` |
| `baseline-rnn` lost | `21/25` | `7/25` | `16/25` | `25/25` | `13/25` | `6/25` |
| `baseline-rnn` won | `28/31` | `31/31` | `0/31` | `0/31` | `16/31` | `10/31` |

The heuristic losses are still contact-like, low, own-side events with recent velocity flips. `net-pressure` makes this worse than `rally-serve`: terminal losses rise from `18` to `30`, `grounded_low_receive` losses rise from `10` to `13`, `low_ball_rescue` losses rise from `2` to `9`, and `low_other_own_side` losses rise from `2` to `9`.

## History And Failure Analysis

`attack`, `rally-serve`, and `net-pressure` mostly react to the current observation. `rally-serve` and `net-pressure` have finite serve macro state and cooldown counters, but their low-receive, rear-wall, late-contact, and pressure rules do not use stacked frames to decide whether a low ball has just been contacted, whether the velocity flip is reliable, or whether the agent is recovering from an earlier jump.

`baseline-rnn` is opaque, but its behavior is clearly different: it wins more front/net terminals (`31` vs `25` for `rally-serve` and `19` for `net-pressure`) and its terminal wins are dominated by `101`. The heuristic family can reach similar front/net terminal positions, but it usually converts them with movement-only actions or loses after current-frame low-receive decisions.

`net-pressure` is not the next useful branch family. It adds `101` pressure frames, including `net_pressure=18` frames in loss traces and `net_pressure=24` frames in win traces, but its terminal failures are still assigned to `grounded_low_receive`, `low_ball_rescue`, and late low-ball modes. The pressure rule appears to perturb the rally into more unresolved low own-side states rather than solving the conversion gap.

The next structural edit should target the history-aware low-receive/post-contact family: a narrow stacked-frame gate around `grounded_low_receive` and `low_ball_rescue` that distinguishes recent own-contact or upward/vx flips before choosing movement-only recovery versus `101`. The evidence favors this over broader scalar tuning, wider serve macros, or broader front-court pressure.

## Promotion Recommendation

No benchmark promotion from this artifact. Keep it as development-only diagnostics.

Do not promote `attack`; it remains below both `rally-serve` and `baseline-rnn`. Do not promote `net-pressure` for generation-4 diagnostics; it regresses the current `rally-serve` reference by `-0.36` mean and reintroduces low own-side losses. `rally-serve` remains the best heuristic reference in this comparison, but this artifact is not promotion evidence and did not use holdout or audit seeds.

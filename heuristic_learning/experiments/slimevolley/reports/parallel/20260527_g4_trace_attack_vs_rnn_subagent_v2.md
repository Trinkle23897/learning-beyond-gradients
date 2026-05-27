# Generation-4 Attack/Rally-Serve Vs Baseline-RNN Trace Diagnostics

Date: 2026-05-27

## Exact Seeds Used

Generation-4 development subset only: `9000..9015`.

Exact list: `9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`.

No holdout seeds, audit seeds, or `slimevolley-final-eval` runs were used. No ledger rows were appended.

## Diagnostic Definition

Comparison: the current heuristic family in `slimevolley.py` (`attack` as the ancestor candidate and `rally-serve` as the current candidate) versus `baseline-rnn`, each against opponent `builtin`.

Execution mode: no-ledger, in-memory diagnostics with `seed_start=9000`, `episodes=16`, and `trace_window=24`.

Policy labels:

- `attack`: `slimevolley_attack_candidate`, `candidate_status=partial_not_promoted`. It inherits the `g4-scalar-tuned-v2` scalar revision and adds `late_contact_attack` with `101` on low descending balls in the near-contact band.
- `rally-serve`: `slimevolley_rally_serve_candidate`, the current generation-4 heuristic candidate. It keeps the attack family and adds the point-reset serve detector plus the same low-receive and rear-wall recovery family.
- `baseline-rnn`: the shipped `slimevolleygym.slimevolley.BaselinePolicy` comparator with `parameter_count=120`.

This artifact is diagnostics only. It is not promotion evidence and does not justify opening holdout or audit seeds.

## Headline Metrics

| Policy | Score mean | W/L/D | Environment steps | Point won/lost |
| --- | ---: | --- | ---: | ---: |
| `attack` | `-0.1250` | `2/4/10` | `48000` | `5/7` |
| `rally-serve` | `0.3125` | `4/0/12` | `48000` | `9/4` |
| `baseline-rnn` | `0.1250` | `6/4/6` | `48000` | `10/8` |

Same-seed deltas:

| Comparison | Mean delta | Improved / worse / same seeds |
| --- | ---: | --- |
| `rally-serve - attack` | `+0.4375` | `7 / 1 / 8` |
| `rally-serve - baseline-rnn` | `+0.1875` | `6 / 5 / 5` |

The current candidate wins the short-screen mean comparison, but it does so by converting the `attack` losses into draws and a few wins rather than adopting the baseline's jump-heavy terminal behavior.

## Per-Seed Scores

| Seed | `attack` | `rally-serve` | `baseline-rnn` |
| ---: | --- | --- | --- |
| `9000` | `0 draw` | `0 draw` | `0 draw` |
| `9001` | `-1 loss` | `0 draw` | `0 draw` |
| `9002` | `0 draw` | `0 draw` | `0 draw` |
| `9003` | `0 draw` | `0 draw` | `1 win` |
| `9004` | `0 draw` | `0 draw` | `1 win` |
| `9005` | `0 draw` | `0 draw` | `-2 loss` |
| `9006` | `-1 loss` | `0 draw` | `0 draw` |
| `9007` | `0 draw` | `1 win` | `-1 loss` |
| `9008` | `0 draw` | `0 draw` | `1 win` |
| `9009` | `1 win` | `0 draw` | `2 win` |
| `9010` | `0 draw` | `0 draw` | `-1 loss` |
| `9011` | `-1 loss` | `1 win` | `-1 loss` |
| `9012` | `-1 loss` | `0 draw` | `1 win` |
| `9013` | `0 draw` | `1 win` | `0 draw` |
| `9014` | `1 win` | `2 win` | `1 win` |
| `9015` | `0 draw` | `0 draw` | `0 draw` |

## Action Frequencies

| Policy | `000` | `001` | `010` | `011` | `100` | `101` | `110` | `111` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `attack` | `21446` | `3088` | `11206` | `425` | `10843` | `992` | `0` | `0` |
| `rally-serve` | `21749` | `3458` | `10839` | `436` | `10497` | `1021` | `0` | `0` |
| `baseline-rnn` | `962` | `4079` | `7646` | `374` | `2875` | `17208` | `13946` | `910` |

`rally-serve` adds only `29` total `101` actions over `attack`, and it still never emits `110` or `111`. The RNN remains jump-heavy, with jump-inclusive actions dominating its trace window usage.

## Point Buckets

Bucket definition for terminal point events: `high_or_mid_terminal` if `ball_y > 1.25`; otherwise `low_far_right` if `ball_y < 0.35 and ball_x > 1.8`, `low_mid_right` if `ball_y < 0.35 and ball_x > 1.0`, `low_left_or_net` if `ball_y < 0.35 and ball_x < 0.2`, and `other` otherwise.

| Bucket | `attack` point losses | `rally-serve` point losses | `baseline-rnn` point losses |
| --- | ---: | ---: | ---: |
| `low_left_or_net` | `2` | `2` | `0` |
| `low_far_right` | `2` | `1` | `5` |
| `low_mid_right` | `1` | `0` | `2` |
| `other` | `2` | `1` | `1` |

`rally-serve` removes the `attack` low-mid-right tail on this subset, but its remaining point-loss events are still clustered near the net and the far-right low ball lanes.

## Terminal Modes And Actions

| Policy/outcome | Terminal modes | Terminal actions |
| --- | --- | --- |
| `attack` lost | `grounded_low_receive=3`, `low_ball_rescue=2`, `rear_wall_low_jump=1`, `rear_wall_press=1` | `101=3`, `100=2`, `010=1`, `000=1` |
| `attack` won | `intercept=3`, `recovery=2` | `100=3`, `010=1`, `000=1` |
| `rally-serve` lost | `grounded_low_receive=2`, `late_low_ball_guard=1`, `rear_wall_low_jump=1` | `100=3`, `101=1` |
| `rally-serve` won | `grounded_low_receive=1`, `intercept=4`, `recovery=4` | `100=4`, `010=2`, `000=3` |
| `baseline-rnn` lost | `unknown=8` | `001=5`, `010=1`, `101=2` |
| `baseline-rnn` won | `unknown=10` | `101=9`, `110=1` |

The current heuristic family is still using transparent movement-only recovery on most terminal wins, while the comparator's wins are overwhelmingly jump-based. That gap is visible even on this short screen.

## Trace-Window Signals

Trace-window counts are over the last `24` frames before each point event. These are diagnostic, not causal proof.

| Policy | Contact-like window | Front/net low window | Rear low window | Low own-side window | `vx` flip | `vy` upward flip |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `attack` | `6/12` | `8/12` | `3/12` | `2/12` | `9/12` | `9/12` |
| `rally-serve` | `5/13` | `11/13` | `2/13` | `1/13` | `10/13` | `9/13` |
| `baseline-rnn` | `11/18` | `11/18` | `5/18` | `3/18` | `10/18` | `14/18` |

`rally-serve` still sees frequent front/net low geometry and recent horizontal velocity flips, but unlike `attack` it no longer turns those windows into episode losses on this subset. The remaining work is post-contact timing and conversion, not a missing serve macro.

## Contact And Post-Contact

Inferred contact candidates on the same 24-frame traces:

| Policy | Candidate count | Point lost / won | X bucket concentration |
| --- | ---: | --- | --- |
| `attack` | `21` | `21/0` | `rear_wall=11`, `near_net=5`, `front_half=3`, `back_half=2` |
| `rally-serve` | `14` | `11/3` | `near_net=6`, `rear_wall=6`, `front_half=2` |
| `baseline-rnn` | `22` | `13/9` | `near_net=10`, `rear_wall=9`, `front_half=3` |

`attack` puts every inferred contact candidate inside a point-loss window. `rally-serve` starts to convert contact windows into wins, but the candidates are still concentrated at near-net and rear-wall geometry, which is exactly where short-history low-receive and post-contact rules matter.

## Failure Analysis

`attack` is still the brittle ancestor. Its losses are dominated by `grounded_low_receive`, `low_ball_rescue`, and rear-wall modes, and the inferred contact windows are almost all losses. That shape matches the earlier diagnosis: the current current-frame rules are not enough once the ball has already been redirected or is entering a low recovery window.

`rally-serve` is the current candidate and it does improve the short-screen result. It eliminates episode losses on `9000..9015`, but that improvement is mostly draw conversion. The trace still shows frequent front/net low windows, recent `vx` flips, and contact candidates concentrated near the net and rear wall. In other words, the remaining gap is not the serve detector itself; it is short-history post-contact recovery and low-receive conversion.

`baseline-rnn` still has the most jump-heavy terminal behavior, and it remains better than the heuristic family at turning near-net opportunities into wins. Its losses are mostly far-right low balls, which is a different failure shape than the heuristic family.

The best next idea is therefore history-aware, not broader scalar tuning and not a wider serve macro. The evidence points to a short-frame post-contact gate around `grounded_low_receive` and rear-wall low recovery.

## Promotion Recommendation

Do not promote from this artifact. This is development-only trace evidence on `9000..9015`.

Recommended next experiment: add a 2-frame post-contact history gate to `rally-serve`'s low-receive branch, so it only suppresses jump after repeated low-ball contact geometry; then rerun the same no-ledger `builtin` trace on `9000..9015` with `trace_window=24`. That is the single next policy/config/test edit that is most directly supported by the traces here.

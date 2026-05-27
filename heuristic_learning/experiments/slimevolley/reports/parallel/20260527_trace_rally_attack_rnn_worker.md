# Rally-Serve Vs Attack Vs RNN Trace Diagnostics

Date: 2026-05-27

## Exact Seeds Used

Generation-4 development seeds only: `9000..9049`.

Exact list: `9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`.

No holdout seeds, audit seeds, or `slimevolley-final-eval` runs were used.

## Diagnostic Definition

Comparison: current workspace policies `rally-serve`, `attack`, and `baseline-rnn`, each against opponent `builtin`.

Execution mode: no-ledger, in-memory diagnostics with `seed_start=9000`, `episodes=50`, and `trace_window=24`. The second recount used the standard evaluator with `ledger_path=None` and `summary_path=None` to verify terminal bucket totals. No ledger rows were appended.

Policy labels:

- `attack`: `slimevolley_attack_candidate`, scalar/config revision `g4-scalar-tuned-v2`, structural rule `late_contact_attack`.
- `rally-serve`: `slimevolley_rally_serve_candidate`, same late-contact family plus a point-reset serve detector: `abs(ball_x) <= 0.28`, `ball_y >= 1.45`, `abs(ball_vx) <= 0.50`, `8` steps, `12`-step cooldown, action `101`.
- `baseline-rnn`: shipped `slimevolleygym.slimevolley.BaselinePolicy`, pretrained 120-parameter neural/RNN comparator.

This report is diagnostics only. It is not structural promotion evidence, scalar promotion evidence, holdout evidence, or audit evidence.

## Headline Metrics

| Policy | Score mean | W/L/D | Environment steps | Point won/lost |
| --- | ---: | --- | ---: | --- |
| `attack` | `-0.30` | `7/18/25` | `150000` | `17/32` |
| `rally-serve` | `0.14` | `13/8/29` | `150000` | `25/18` |
| `baseline-rnn` | `0.12` | `18/12/20` | `150000` | `31/25` |

Same-seed deltas:

| Comparison | Mean delta | Improved / worse / same seeds | Main outcome conversions |
| --- | ---: | --- | --- |
| `rally-serve - attack` | `+0.44` | `19 / 5 / 26` | `loss->draw`: `9`, `loss->win`: `3`, `draw->win`: `6`, regressions to loss: `2` |
| `rally-serve - baseline-rnn` | `+0.02` | `17 / 16 / 17` | `loss->draw`: `7`, `loss->win`: `3`, but `win->draw`: `10`, `win->loss`: `3` |

Largest `rally-serve` gains over `attack`: seed `9039` `-4 -> 0`, seed `9030` `-3 -> 0`, and seeds `9011`, `9023`, `9034` `-1 -> 1`.

## Action Frequencies

| Policy | `000` | `001` | `010` | `011` | `100` | `101` | `110` | `111` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `attack` | `67891` | `10569` | `34068` | `1363` | `32965` | `3144` | `0` | `0` |
| `rally-serve` | `68654` | `10661` | `33496` | `1391` | `32347` | `3451` | `0` | `0` |
| `baseline-rnn` | `2891` | `12644` | `23751` | `1184` | `9288` | `53725` | `43727` | `2790` |

The rally detector adds only `+307` total `101` actions over `attack`; it does not make the heuristic action distribution RNN-like. The RNN lives on jump-heavy `101` and `110`, while the transparent heuristics mostly use no-op and one-direction movement without jump.

## Loss Buckets

Bucket definition for terminal point events: `high_or_mid_terminal` if `ball_y > 0.65`; otherwise `low_left_or_net` if `ball_x <= 0.35`, `low_far_right` if `ball_x >= 1.85`, `low_mid_right` if `ball_x >= 1.00`, and `low_other_own_side` otherwise.

| Bucket | `attack` losses | `rally-serve` losses | `baseline-rnn` losses |
| --- | ---: | ---: | ---: |
| `low_left_or_net` | `17` | `11` | `7` |
| `low_far_right` | `8` | `4` | `16` |
| `low_mid_right` | `2` | `1` | `2` |
| `low_other_own_side` | `5` | `2` | `0` |

All terminal point wins for all three policies fell into `low_left_or_net`: `attack=17`, `rally-serve=25`, `baseline-rnn=31`. The difference is conversion rate, not terminal region diversity.

## Terminal Modes And Actions

Terminal loss modes:

| Policy | Terminal loss modes |
| --- | --- |
| `attack` | `grounded_low_receive=16`, `low_ball_rescue=8`, `rear_wall_low_jump=4`, `rear_wall_press=4` |
| `rally-serve` | `grounded_low_receive=10`, `rear_wall_low_jump=4`, `low_ball_rescue=2`, `late_contact_attack=1`, `late_low_ball_guard=1` |
| `baseline-rnn` | `neural=25` |

Terminal loss actions:

| Policy | Terminal loss actions |
| --- | --- |
| `attack` | `101=12`, `100=11`, `010=5`, `000=4` |
| `rally-serve` | `100=8`, `101=7`, `000=3` |
| `baseline-rnn` | `101=12`, `001=9`, `010=2`, `011=1`, `110=1` |

Terminal win modes/actions:

| Policy | Terminal win modes | Terminal win actions |
| --- | --- | --- |
| `attack` | `recovery=9`, `intercept=8` | `100=7`, `010=5`, `000=5` |
| `rally-serve` | `recovery=13`, `intercept=11`, `grounded_low_receive=1` | `100=11`, `010=7`, `000=7` |
| `baseline-rnn` | `neural=31` | `101=28`, `110=2`, `001=1` |

`rally-serve` improves the same transparent modes rather than discovering an RNN-like terminal action family. It halves `grounded_low_receive` losses relative to `attack` (`16 -> 10`) and cuts `low_ball_rescue` losses (`8 -> 2`), but its terminal wins are still mostly movement-only returns. The RNN's terminal wins are almost always jump-combo contacts.

## Serve And Reset Diagnostics

Observed reset-like geometry used for diagnostics only: `abs(ball_x) <= 0.28`, `ball_y >= 1.45`, `abs(ball_vx) <= 0.50`.

| Policy | Reset-like starts / frames | Serve-mode starts | Serve-mode calls |
| --- | ---: | ---: | ---: |
| `attack` | `25 / 476` | `0` | `0` |
| `rally-serve` | `28 / 518` | `rally_serve=53` | `rally_serve=424` |
| `baseline-rnn` | `37 / 641` | `0` | `0` |

The change from `attack` to `rally-serve` is visible: explicit reset-serve macro calls appear (`424` frames, `53` mode starts), and total point losses drop from `32` to `18`. Only a small number of point events occurred soon after a rally-serve start in the 24-frame terminal windows; most terminal events were long after the serve macro. This suggests the serve detector improves rally initialization and state distribution, but the remaining gap is not a direct serve-action problem.

## Trace-Window Signals

Trace-window counts are event-level diagnostics over the last `24` frames before each point. They are not causal proof.

| Policy/outcome | Contact-like window | Front/net low window | Rear low window | `vx` flip | `vy` upward flip |
| --- | ---: | ---: | ---: | ---: | ---: |
| `attack` lost | `32/32` | `18/32` | `10/32` | `28/32` | `13/32` |
| `attack` won | `3/17` | `17/17` | `0/17` | `10/17` | `7/17` |
| `rally-serve` lost | `18/18` | `11/18` | `6/18` | `14/18` | `6/18` |
| `rally-serve` won | `4/25` | `25/25` | `0/25` | `16/25` | `7/25` |
| `baseline-rnn` lost | `25/25` | `5/25` | `16/25` | `12/25` | `4/25` |
| `baseline-rnn` won | `2/31` | `31/31` | `0/31` | `17/31` | `9/31` |

The transparent policies still show many losses with recent contact-like geometry and velocity flips. A single current-frame rule cannot tell whether the ball has just been redirected, whether the agent is recovering from an airborne contact, or whether the next low state is reachable. That is the strongest evidence here for stacked-frame or trajectory-history rules.

## Failure Analysis

`rally-serve` closes the `attack` gap mostly by reducing avoidable low-ball losses: `low_left_or_net` drops `17 -> 11`, `low_far_right` drops `8 -> 4`, `low_other_own_side` drops `5 -> 2`, and point losses drop `32 -> 18`. It also converts several same-seed `attack` losses into draws or wins.

What remains differs from the RNN. `rally-serve` is slightly ahead on mean score on this development range, but it wins fewer matches than the RNN (`13` vs `18`) and relies more on draws (`29` vs `20`). Its remaining losses are still mostly grounded low receive or late low-ball timing failures near the front/net and own-side floor. The RNN loses more far-right points, but it converts many front/net terminals with jump-heavy `101` actions that the heuristic almost never uses at terminal wins.

Stacked-frame or trajectory history looks promising for the next experiment family. The target should not be another broad scalar search or a wider serve macro. The useful branch family is a history-aware low receive / post-contact recovery rule that can distinguish recent contact, velocity flip direction, agent airborne state, and expected floor intercept before choosing between movement-only recovery and jump-combo contact.

## Promotion Recommendation

No direct promotion recommendation from this artifact. Treat it as development diagnostics only.

Recommended next experiment family: stacked-frame or short-trajectory low-receive rules focused on post-contact recovery and terminal jump-combo timing, evaluated only on generation-4 development seeds until a separate predeclared promotion protocol exists.

# Generation-4 Parallel6 Trace Diagnostic: `attack`, `rally-serve`, `baseline-rnn`

Date: 2026-05-27

Candidate type: diagnostics-only no-ledger trace comparison. This is not benchmark evidence, not promotion evidence, and not a reason to open holdout or audit seeds.

## Scope

- Split: generation-4 development seeds only.
- Trace focus: `9000..9015` inclusive, a short trace window inside the predeclared generation-4 development range `9000..9049`.
- Exact seeds: `9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`.
- Policies compared: `attack`, `rally-serve`, `baseline-rnn`.
- Opponent: `builtin`.
- Evaluation mode: no-ledger, `trace_window=24`, `episodes=16`.
- No maintained source, policy, result, or test files were edited.
- No holdout or audit seeds were used.

## Headline Metrics

All policies ran for the full 3000-step cap on every seed, so the score differences are not caused by early termination.

| Policy | Score mean | W-L-D | Environment steps | Point won/lost |
| --- | ---: | ---: | ---: | ---: |
| `attack` | `-0.1250` | `2/4/10` | `48000` | `5/7` |
| `rally-serve` | `0.3125` | `4/0/12` | `48000` | `9/4` |
| `baseline-rnn` | `0.1250` | `6/4/6` | `48000` | `10/8` |

Same-seed deltas:

| Comparison | Mean delta | Improved / worse / same seeds |
| --- | ---: | ---: |
| `rally-serve - attack` | `+0.4375` | `7 / 1 / 8` |
| `rally-serve - baseline-rnn` | `+0.1875` | `6 / 5 / 5` |

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

## Action Totals

Counts are over 48,000 environment steps per policy.

| Policy | `000` | `001` | `010` | `011` | `100` | `101` | `110` | `111` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `attack` | `21446` | `3088` | `11206` | `425` | `10843` | `992` | `0` | `0` |
| `rally-serve` | `21749` | `3458` | `10839` | `436` | `10497` | `1021` | `0` | `0` |
| `baseline-rnn` | `962` | `4079` | `7646` | `374` | `2875` | `17208` | `13946` | `910` |

The heuristic policies are still movement-heavy and never emit `110` or `111`. `rally-serve` emits only 29 more `101` actions than `attack` over the whole slice. `baseline-rnn` is much more jump-heavy: `101` plus `110` accounts for 31,154 of 48,000 actions.

## Terminal Modes And Actions

`baseline-rnn` does not expose heuristic diagnostic modes, so its mode is listed as `unknown`; terminal actions and geometry buckets are still available.

| Policy/event | Terminal modes | Terminal actions | Geometry / failure buckets |
| --- | --- | --- | --- |
| `attack` point lost | `grounded_low_receive=3`, `low_ball_rescue=2`, `rear_wall_low_jump=1`, `rear_wall_press=1` | `101=3`, `100=2`, `010=1`, `000=1` | `low_far_right=2`, `low_left_or_net=2`, `low_mid_right=1`, `other=2` |
| `attack` point won | `intercept=3`, `recovery=2` | `100=3`, `010=1`, `000=1` | `low_left_or_net=5` |
| `rally-serve` point lost | `grounded_low_receive=2`, `late_low_ball_guard=1`, `rear_wall_low_jump=1` | `100=3`, `101=1` | `low_far_right=1`, `low_left_or_net=2`, `other=1` |
| `rally-serve` point won | `grounded_low_receive=1`, `intercept=4`, `recovery=4` | `100=4`, `010=2`, `000=3` | `low_left_or_net=9` |
| `baseline-rnn` point lost | `unknown=8` | `001=5`, `010=1`, `101=2` | `low_far_right=5`, `low_mid_right=2`, `other=1` |
| `baseline-rnn` point won | `unknown=10` | `101=9`, `110=1` | `low_left_or_net=10` |

## Failure Analysis

`attack` is the brittle ancestor on this trace slice. Its episode losses are not primarily tagged as `late_contact_attack`; they are concentrated in low-receive and rear-wall recovery modes. The aggregate action profile is also passive relative to the neural comparator: `attack` spends 44.7% of steps on `000` and only 2.1% on `101`.

`rally-serve` improves the same-seed score by removing `attack` episode losses on `9000..9015`, but the trace still shows point losses in `grounded_low_receive`, `late_low_ball_guard`, and `rear_wall_low_jump`. The improvement looks like loss-to-draw and occasional draw-to-win conversion, not a solved conversion policy. Its terminal wins are still mostly transparent movement-only modes, not the jump-heavy behavior seen in `baseline-rnn`.

`baseline-rnn` wins more often than `attack` but also loses four episodes. Its failures cluster around low far-right or mid-right balls, while its wins are mostly low-left/net opportunities finished with `101` or `110`. That is a different failure shape from the heuristic family and suggests the RNN is better at converting near-net opportunities while accepting more jump-heavy exposure elsewhere.

## Recommendation

Do not promote from this artifact. Keep the next hypothesis development-only and dev-seed-only.

The most supported next hypothesis is a short-history post-contact / low-receive gate on top of `rally-serve`, focused on `grounded_low_receive` and rear-wall low recovery after recent contact-like ball velocity flips. This is more directly supported than wider scalar tuning or a broader serve macro. Recheck first with the same no-ledger trace window on `9000..9015`; if it improves without changing the failure shape adversely, expand only to the remaining generation-4 development seeds in `9000..9049`.

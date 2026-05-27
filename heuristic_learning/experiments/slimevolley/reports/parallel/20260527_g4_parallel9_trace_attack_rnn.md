# Generation-4 Parallel9 Trace Diagnostic: `attack` vs `baseline-rnn`

Date: 2026-05-27

Kind: development-seed diagnostic evidence only. This is not benchmark or
promotion evidence beyond the exact seeds listed below. No holdout seeds
`10000..10049` and no audit seeds `11000..11049` were used.

## Scope

- Split: generation-4 development seeds only.
- Exact seeds: `9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`.
- Opponent: `builtin`, the environment's built-in SlimeVolley RNN policy.
- Policies compared as agents: `attack`, `baseline-rnn`.
- Trace window: `24`.
- Evaluation mode: no ledger and no summary writes (`ledger_path=None`, `summary_path=None`).
- Runtime: repository virtual environment, `.venv/bin/python`.

## Commands Run

- `.venv/bin/python -m hl_benchmark.custom_envs.slimevolley.doctor`
- `.venv/bin/python - <<'PY' ... evaluate_slimevolley(policy_name in ["attack", "baseline-rnn"], opponent_name="builtin", split="dev", seed_start=9000, episodes=16, trace_window=24, ledger_path=None, summary_path=None) ... PY`

## Headline Metrics

All episodes reached the 3000-step cap, so the score gap is not caused by
early termination.

| Policy | Score mean | W-L-D | Environment steps | Points won/lost | Life diff mean |
| --- | ---: | ---: | ---: | ---: | ---: |
| `attack` | `-0.1250` | `2/4/10` | `48000` | `5/7` | `-0.1250` |
| `baseline-rnn` | `0.1250` | `6/4/6` | `48000` | `10/8` | `0.1250` |

Same-seed comparison:

| Comparison | Mean delta | Better / worse / same seeds |
| --- | ---: | --- |
| `attack - baseline-rnn` | `-0.2500` | `3 / 7 / 6` |

`attack` was better on seeds `9005, 9007, 9010`, worse on
`9001, 9003, 9004, 9006, 9008, 9009, 9012`, and tied on
`9000, 9002, 9011, 9013, 9014, 9015`.

## Per-Seed Scores

| Seed | `attack` | `baseline-rnn` | Delta |
| ---: | ---: | ---: | ---: |
| `9000` | `0` | `0` | `0` |
| `9001` | `-1` | `0` | `-1` |
| `9002` | `0` | `0` | `0` |
| `9003` | `0` | `1` | `-1` |
| `9004` | `0` | `1` | `-1` |
| `9005` | `0` | `-2` | `2` |
| `9006` | `-1` | `0` | `-1` |
| `9007` | `0` | `-1` | `1` |
| `9008` | `0` | `1` | `-1` |
| `9009` | `1` | `2` | `-1` |
| `9010` | `0` | `-1` | `1` |
| `9011` | `-1` | `-1` | `0` |
| `9012` | `-1` | `1` | `-2` |
| `9013` | `0` | `0` | `0` |
| `9014` | `1` | `1` | `0` |
| `9015` | `0` | `0` | `0` |

## Action Frequencies

Counts are over 48,000 environment steps per policy.

| Policy | `000` | `001` | `010` | `011` | `100` | `101` | `110` | `111` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `attack` | `21446` | `3088` | `11206` | `425` | `10843` | `992` | `0` | `0` |
| `baseline-rnn` | `962` | `4079` | `7646` | `374` | `2875` | `17208` | `13946` | `910` |

`attack` remains movement-heavy and never emits `110` or `111`.
`baseline-rnn` is jump-heavy: `101` plus `110` accounts for `31154/48000`
steps, versus `992/48000` `101` steps and no `110` for `attack`.

## Terminal Modes And Point-Loss Diagnostics

| Policy/event | Terminal modes | Terminal actions | Terminal geometry buckets |
| --- | --- | --- | --- |
| `attack` point lost | `grounded_low_receive=3`, `low_ball_rescue=2`, `rear_wall_low_jump=1`, `rear_wall_press=1` | `101=3`, `100=2`, `010=1`, `000=1` | `low_left_or_net=3`, `low_far_right=2`, `low_mid_right=1`, `low_other_own_side=1` |
| `attack` point won | `intercept=3`, `recovery=2` | `100=3`, `010=1`, `000=1` | `low_left_or_net=5` |
| `baseline-rnn` point lost | `unknown=8` | `001=5`, `101=2`, `010=1` | `low_far_right=5`, `low_mid_right=2`, `low_left_or_net=1` |
| `baseline-rnn` point won | `unknown=10` | `101=9`, `110=1` | `low_left_or_net=10` |

For `attack`, traced loss windows were dominated by
`intercept=64`, `late_contact_attack=27`, `low_ball_rescue=21`,
`rear_wall_press=16`, `recovery=14`, `falling_floor_intercept=13`,
`grounded_low_receive=6`, and `high_arc=5` frame-level mode counts.

`late_contact_attack` appeared only in point-loss windows on this slice, with
traced seeds `9006, 9011, 9013, 9014`. Other recurring `attack` loss-window
modes were `grounded_low_receive` on `9006, 9013, 9014`,
`low_ball_rescue` on `9006, 9011, 9012, 9013`, and `rear_wall_press` on
`9001, 9011, 9012, 9013`.

Trace-window action counts also show the behavioral gap:

| Policy/event | Main traced actions |
| --- | --- |
| `attack` point lost | `101=45`, `100=42`, `000=32`, `010=29`, `011=11`, `001=9` |
| `attack` point won | `000=79`, `010=23`, `100=18` |
| `baseline-rnn` point lost | `010=83`, `001=59`, `101=35`, `110=6`, `111=4`, `000=3`, `100=1`, `011=1` |
| `baseline-rnn` point won | `101=226`, `110=5`, `111=5`, `001=2`, `010=2` |

## Failure Analysis

`attack` does not close the same-seed gap to `baseline-rnn` on this fixed
trace subset. It trails by `0.25` mean score, has fewer wins (`2` vs `6`), and
wins fewer points (`5` vs `10`) despite both policies reaching the same step
cap.

The added `late_contact_attack` branch is active, but it is not converting the
dominant failures. It appears in traced point-loss windows, while terminal
losses remain tagged as `grounded_low_receive`, `low_ball_rescue`,
`rear_wall_low_jump`, and `rear_wall_press`. The failure shape is still low
own-side recovery after contact-like state changes, not a missing trigger for
the late-contact branch itself.

`baseline-rnn` converts the same low-left-or-net terminal region with a very
different action family. Its wins are almost all `101` or `110`, while
`attack` wins the same region with movement-only terminal actions. That keeps
the heuristic behind on near-net conversion timing even when it reaches similar
states.

## Promotion Recommendation

No promotion.

Keep `attack` as a generation-4 development-only diagnostic candidate. This
artifact is useful for low-receive and post-contact failure tracing, but it is
not benchmark evidence and should not be used as promotion evidence or to open
holdout or audit seeds.

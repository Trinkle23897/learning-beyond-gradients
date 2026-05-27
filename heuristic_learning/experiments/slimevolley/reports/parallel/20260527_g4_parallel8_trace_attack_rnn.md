# Generation-4 Parallel8 Trace Diagnostic: `attack` vs `baseline-rnn`

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
- Dependency versions reported by the harness: `gym=0.20.0`, `numpy=1.26.4`, `opencv-python=4.11.0.86`, `slimevolleygym=0.1.0`.

## Commands Run

- `.venv/bin/python -m hl_benchmark.custom_envs.slimevolley.doctor`
- `.venv/bin/python - <<'PY' ... evaluate_slimevolley(policy_name in ["attack", "baseline-rnn"], opponent_name="builtin", split="dev", seed_start=9000, episodes=16, trace_window=24, ledger_path=None, summary_path=None) ... PY`

## Candidate Definitions

`attack` is `SlimeVolleyAttackPolicy`, a generation-4 structural candidate on
top of `improved-tuned` scalar fields. Its added rule is
`late_contact_attack`: if `ball_x > 0.05`, `0.28 <= ball_y <= 0.65`,
`ball_vx < -0.35`, `ball_vy < -0.10`, and `0.04 <= agent_x - ball_x <= 0.28`,
emit action `101` (`forward+jump`). The policy config reports
`candidate_status=partial_not_promoted`.

`baseline-rnn` is `SlimeVolleyBuiltInRnnPolicy`, a wrapper around
`slimevolleygym.slimevolley.BaselinePolicy`. The harness reports it as a
pretrained neural/RNN comparator with `parameter_count=120`.

## Headline Metrics

All episodes reached the 3000-step cap, so score differences are not due to
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
steps, versus `992/48000` for `attack`.

## Terminal And Life-Loss Modes

The harness records point events as life won/lost events. `attack` exposes
transparent heuristic modes; `baseline-rnn` does not, so its terminal mode is
`unknown`.

| Policy/event | Terminal modes | Terminal actions | Terminal geometry buckets |
| --- | --- | --- | --- |
| `attack` point lost | `grounded_low_receive=3`, `low_ball_rescue=2`, `rear_wall_low_jump=1`, `rear_wall_press=1` | `101=3`, `100=2`, `010=1`, `000=1` | `low_far_right=2`, `low_left_or_net=2`, `low_mid_right=1`, `other=2` |
| `attack` point won | `intercept=3`, `recovery=2` | `100=3`, `010=1`, `000=1` | `low_left_or_net=5` |
| `baseline-rnn` point lost | `unknown=8` | `001=5`, `101=2`, `010=1` | `low_far_right=5`, `low_mid_right=2`, `other=1` |
| `baseline-rnn` point won | `unknown=10` | `101=9`, `110=1` | `low_left_or_net=10` |

The terminal contrast is sharp: `baseline-rnn` wins near-net/left events mostly
with jump actions, while `attack` wins the same bucket with movement-only
terminal actions.

## Trace-Window Diagnostics

Trace-window flags count whether a point-event window contained a feature at
least once.

| Policy/event | Contact-like | Low own-side | Low front/net | Low rear | `vx` flip | Upward flip |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `attack` point lost | `6/7` | `7/7` | `3/7` | `4/7` | `5/7` | `2/7` |
| `attack` point won | `5/5` | `0/5` | `5/5` | `0/5` | `4/5` | `1/5` |
| `baseline-rnn` point lost | `6/8` | `8/8` | `1/8` | `6/8` | `4/8` | `1/8` |
| `baseline-rnn` point won | `10/10` | `0/10` | `10/10` | `0/10` | `6/10` | `5/10` |

For `attack` point-loss windows, mode counts across traced frames were:
`intercept=64`, `late_contact_attack=27`, `low_ball_rescue=23`,
`rear_wall_press=17`, `recovery=14`, `falling_floor_intercept=13`,
`grounded_low_receive=9`, `high_arc=5`, `rear_wall_low_jump=3`.

`late_contact_attack` appeared only in point-loss windows on this slice, with
traced seeds `9006, 9011, 9013, 9014`. Other recurrent point-loss trace modes:
`grounded_low_receive` on `9006, 9013, 9014`, `low_ball_rescue` on
`9006, 9011, 9012, 9013`, and `rear_wall_low_jump` on `9012`.

Trace-window action counts also show the behavioral gap:

| Policy/event | Main traced actions |
| --- | --- |
| `attack` point lost | `101=48`, `100=44`, `000=33`, `010=30`, `011=11`, `001=9` |
| `attack` point won | `000=80`, `010=24`, `100=21` |
| `baseline-rnn` point lost | `010=84`, `001=64`, `101=37`, `110=6`, `111=4`, `000=3`, `100=1`, `011=1` |
| `baseline-rnn` point won | `101=235`, `110=6`, `111=5`, `001=2`, `010=2` |

## Failure Analysis

`attack` does not close the same-seed gap to `baseline-rnn` on this fixed trace
subset. It trails by `0.25` mean score, has fewer wins (`2` vs `6`), and wins
fewer points (`5` vs `10`) despite both policies reaching the same step cap.

The added `late_contact_attack` branch is active, but it is not converting the
dominant failures. It appears in traced point-loss windows, while terminal
losses are tagged as `grounded_low_receive`, `low_ball_rescue`,
`rear_wall_low_jump`, and `rear_wall_press`. The failure shape is therefore
low own-side recovery after contact-like velocity changes, not an absent
late-contact trigger.

`baseline-rnn` has a different tradeoff. Its losses cluster more at low
far-right or low mid-right balls, but its wins are concentrated at low
left/net events and are finished with `101` or `110`. `attack` reaches some of
those near-net events, but the terminal action mix remains movement-only in
its wins, which suggests the current heuristic branch is not matching the RNN's
near-net conversion timing.

## Recommendation

No promotion.

Keep `attack` as a partial generation-4 diagnostic candidate only. This
artifact supports a development-only follow-up around short-history
post-contact/low-receive gating, especially deciding when `grounded_low_receive`
should recover, suppress jump, or attempt a near-net `101` conversion after
recent velocity flips. It does not support opening holdout or audit seeds.

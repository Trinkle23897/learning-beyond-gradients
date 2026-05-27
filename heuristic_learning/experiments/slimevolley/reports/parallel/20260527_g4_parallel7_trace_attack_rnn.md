# Generation-4 Parallel7 Trace Diagnostic: `attack`, `rally-serve`, `post-contact`, `baseline-rnn`

Date: 2026-05-27

Kind: `diagnostic analysis only`

This is no-ledger development-seed evidence. It is not promotion evidence and it does not open holdout or audit seeds.

## Scope

- Split: generation-4 development seeds only.
- Exact seeds: `9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`.
- Opponent: `builtin`.
- Trace window: `12`.
- Policies compared: `improved-tuned` as the current scalar baseline, `attack`, `rally-serve`, `post-contact`, `baseline-rnn`, and `improved-v6` as a hard archived contrast.
- Runtime: repository virtual environment with `source .venv/bin/activate` and `PYTHONPATH=.`.
- Temporary outputs used for this note: `/tmp/slimevolley_g4_parallel7_trace_attack_rnn_summary.json` and `/tmp/slimevolley_g4_parallel7_trace_attack_rnn_raw.json`.
- No shared policy, eval, or report code was edited.

## Headline Metrics

All policies except `improved-v6` ran the full 3000-step cap on every seed. `improved-v6` ended early on 2 seeds, so its step total is lower.

| Policy | Score mean | W-L-D | Environment steps | Notes |
| --- | ---: | --- | ---: | --- |
| `improved-tuned` | `-0.4375` | `2/8/6` | `48000` | current scalar baseline |
| `attack` | `-0.1250` | `2/4/10` | `48000` | partial structural candidate |
| `rally-serve` | `0.3125` | `4/0/12` | `48000` | structural-plus-scalar candidate |
| `post-contact` | `0.3125` | `4/0/12` | `48000` | same score curve as `rally-serve` |
| `baseline-rnn` | `0.1250` | `6/4/6` | `48000` | pretrained neural comparator |
| `improved-v6` | `-2.3750` | `0/14/2` | `45867` | archived contrast; early stop on seeds `9005` and `9015` |

## Same-Seed Comparison Against `baseline-rnn`

| Policy | Mean delta vs `baseline-rnn` | Better / worse / same seeds |
| --- | ---: | --- |
| `improved-tuned` | `-0.5625` | `5 / 10 / 1` |
| `attack` | `-0.2500` | `3 / 7 / 6` |
| `rally-serve` | `+0.1875` | `6 / 5 / 5` |
| `post-contact` | `+0.1875` | `6 / 5 / 5` |
| `improved-v6` | `-2.5000` | `2 / 14 / 0` |

`post-contact` is score-identical to `rally-serve` on all 16 seeds. The only visible change here is action mix, not episode score.

## Action Frequencies

Counts are over 48,000 environment steps for the 3000-step policies. `improved-v6` is lower because two episodes terminated early.

| Policy | `000` | `001` | `010` | `011` | `100` | `101` | `110` | `111` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `improved-tuned` | `22082` | `3493` | `10772` | `408` | `10322` | `923` | `0` | `0` |
| `attack` | `21446` | `3088` | `11206` | `425` | `10843` | `992` | `0` | `0` |
| `rally-serve` | `21749` | `3458` | `10839` | `436` | `10497` | `1021` | `0` | `0` |
| `post-contact` | `21602` | `3392` | `10930` | `456` | `10550` | `1070` | `0` | `0` |
| `baseline-rnn` | `962` | `4079` | `7646` | `374` | `2875` | `17208` | `13946` | `910` |
| `improved-v6` | `18794` | `3874` | `10865` | `703` | `10591` | `1040` | `0` | `0` |

The heuristic policies stay movement-heavy and never emit `110` or `111`. `baseline-rnn` is the only policy with a heavy jump/both-direction profile.

## Trace Modes And Failure Buckets

The point-event trace windows were the main diagnostic signal. The counts below are terminal modes on point events unless otherwise noted.

| Policy | Point-loss terminal modes | Point-win terminal modes | Loss buckets / trace note |
| --- | --- | --- | --- |
| `attack` | `grounded_low_receive=3`, `low_ball_rescue=2`, `rear_wall_low_jump=1`, `rear_wall_press=1` | `intercept=3`, `recovery=2` | Loss buckets: `low_far_right=2`, `low_left_or_net=2`, `low_mid_right=1`, `other=2`. The late-contact branch appeared in `23` traced frames, all in loss windows; its traced seeds were `9006, 9011, 9013, 9014`. |
| `rally-serve` | `grounded_low_receive=2`, `late_low_ball_guard=1`, `rear_wall_low_jump=1` | `intercept=4`, `grounded_low_receive=1`, `recovery=4` | Loss buckets: `low_far_right=1`, `low_left_or_net=2`, `other=1`. The late-contact branch appeared in `8` traced frames, mostly loss windows. The point-window traces did not surface terminal `rally_serve`; the visible wins still came from intercept/recovery. |
| `post-contact` | `grounded_low_receive=2`, `late_low_ball_guard=1`, `rear_wall_low_jump=1` | `intercept=4`, `grounded_low_receive=1`, `recovery=4` | Loss buckets: `low_far_right=1`, `low_left_or_net=2`, `other=1`. `post_contact_front_conversion` appeared in `4` traced frames on seed `9006` only: `3` in loss windows and `1` in a win window. It changed the action mix, not the episode scores. |
| `baseline-rnn` | `unknown=8` | `unknown=10` | Loss buckets: `low_far_right=5`, `low_mid_right=2`, `other=1`. There are no heuristic mode labels for this comparator. |
| `improved-tuned` | `grounded_low_receive=7`, `low_ball_rescue=3`, `rear_wall_low_jump=3`, `rear_wall_press=1` | `intercept=1`, `recovery=6` | Loss buckets: `low_far_right=4`, `low_left_or_net=4`, `other=6`. This baseline is still dominated by low-receive failure modes. |
| `improved-v6` | `grounded_low_receive=29`, `low_ball_rescue=8`, `rear_wall_low_jump=6`, `rear_wall_press=1` | `intercept=1`, `recovery=5` | Loss buckets: `low_far_right=8`, `low_left_or_net=19`, `low_mid_right=1`, `other=16`. The trace windows are flooded with `low_ball_rescue=180` and `grounded_low_receive=137`, and 2 episodes terminated early. |

## Failure Readout

`attack` is still the brittle branch. It improves over `improved-tuned`, but it remains below `baseline-rnn` by `0.25` mean score and its losses are concentrated in `grounded_low_receive` plus rear-wall recovery. The late-contact rule is visible in the trace windows, but it mostly appears inside loss windows rather than converting them into wins.

`rally-serve` and `post-contact` are the strongest heuristic candidates on this slice. Both beat `baseline-rnn` by `0.1875` mean score and avoid any episode losses, but the point-event traces show that their remaining failures are still `grounded_low_receive`, `late_low_ball_guard`, and `rear_wall_low_jump`. The `post_contact_front_conversion` branch fired once on seed `9006` and changed the action distribution, but it did not change any episode scores relative to `rally-serve`.

`baseline-rnn` remains qualitatively different. It is much more jump-heavy and its remaining losses are low far-right or low mid-right balls rather than the left/net and grounded low-receive failures that still hit the heuristic family.

`improved-v6` is useful only as a contrast. It overcommits to low-receive and rear-wall behavior and still loses heavily, so adding more low-receive or rear-wall coverage without tightening the geometry is not enough.

## Next Edit Worth One Try

The next structural edit worth trying is a narrower `grounded_low_receive` split, especially separating low-left/net from low-mid-right recovery, with rear-wall rescue kept separate. That is the branch family that still appears in the remaining losses for `attack`, `rally-serve`, and `post-contact`.

`post_contact_front_conversion` is not the next edit on this slice: it changed actions on one seed but did not change any episode scores. `late_contact_attack` is also not the next edit: on `attack` it showed up mostly inside loss windows.

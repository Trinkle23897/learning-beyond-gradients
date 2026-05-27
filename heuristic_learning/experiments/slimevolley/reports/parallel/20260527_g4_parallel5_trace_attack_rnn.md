# SlimeVolley Generation-4 Trace Diagnostic: `attack` vs `baseline-rnn`

Type: diagnostic-only (`logging/diagnostics change`)

## Scope

This report compares `attack` against `baseline-rnn` on the exact generation-4 development slice `9000..9015` inclusive.

- Policies compared: `attack`, `baseline-rnn`, `rally-serve`, `post-contact`
- Opponent: `builtin`
- Exact seeds used: `9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`
- No holdout or audit seeds were used
- No seeds from `10000..10049` or `11000..11049` were used

Trace capture came from the SlimeVolley adapter diagnostics path, which records per-step action/state frames and point events when `trace_window > 0` is enabled. The relevant generation-4 seed split is declared in the protocol, and the policy implementations are the handwritten candidates under comparison.

## Summary

All four policies ran for the full 3000-step time limit on every seed in this slice, so the difference is not episode length.

| Policy | Mean score | W-L-D | Mean steps | Terminal modes |
| --- | ---: | ---: | ---: | --- |
| `attack` | -0.125 | 2/4/10 | 3000.0 | `falling_floor_intercept` 4, `high_arc` 1, `intercept` 9, `low_ball_rescue` 2 |
| `baseline-rnn` | 0.125 | 6/4/6 | 3000.0 | not exposed by the packaged RNN baseline |
| `rally-serve` | 0.3125 | 4/0/12 | 3000.0 | `falling_floor_intercept` 2, `intercept` 10, `recovery` 4 |
| `post-contact` | 0.3125 | 4/0/12 | 3000.0 | `falling_floor_intercept` 2, `intercept` 10, `recovery` 4 |

Action totals are over 48,000 steps per policy.

### Action Frequencies

`attack`

- `000`: 21446
- `001`: 3088
- `010`: 11206
- `011`: 425
- `100`: 10843
- `101`: 992

`baseline-rnn`

- `000`: 962
- `001`: 4079
- `010`: 7646
- `011`: 374
- `100`: 2875
- `101`: 17208
- `110`: 13946
- `111`: 910

`rally-serve`

- `000`: 21749
- `001`: 3458
- `010`: 10839
- `011`: 436
- `100`: 10497
- `101`: 1021

`post-contact`

- `000`: 21602
- `001`: 3392
- `010`: 10930
- `011`: 456
- `100`: 10550
- `101`: 1070

## Failure Analysis

The gap is not driven by catastrophic `attack` overcommit on this slice. The negative point events on `attack` were concentrated in defensive recovery states:

- 5 `low_receive` losses
- 2 `rear_wall_contact` losses
- 0 losses classified as `late_contact_attack`

Representative `attack` loss traces:

- Seed `9001`, step `522`: `rear_wall_press`, action `010`, with `ball_x=2.35`, `ball_y=0.24`, `ball_vx=0.44`, `ball_vy=-3.33`, `agent_x=2.25`, `agent_y=0.41`
- Seed `9006`, step `71`: `low_ball_rescue`, action `101`, with `ball_x=0.32`, `ball_y=0.23`, `ball_vx=-1.38`, `ball_vy=-3.27`, `agent_x=0.50`, `agent_y=0.34`
- Seed `9006`, step `2617`: `grounded_low_receive`, action `000`, following a prior `late_contact_attack` step
- Seed `9011`, step `845`: `low_ball_rescue`, action `101`, with `ball_x=1.38`, `ball_y=0.22`, `ball_vx=-2.14`, `ball_vy=-0.69`, `agent_x=1.60`, `agent_y=0.28`
- Seed `9012`, step `986`: `rear_wall_low_jump`, action `101`, with `ball_x=2.32`, `ball_y=0.23`, `ball_vx=-0.75`, `ball_vy=-0.96`, `agent_x=2.12`, `agent_y=0.15`

Compared with `baseline-rnn`, `attack` is much more passive in the aggregate:

- `attack` spends 44.7% of steps on `000` and only 2.1% on `101`
- `baseline-rnn` spends 35.9% on `101`, 29.1% on `110`, and only 2.0% on `000`

On this seed slice, `baseline-rnn` wins more often because it converts more rallies into wins, not because it avoids all losses:

- `attack`: 2 wins, 4 losses, 10 draws
- `baseline-rnn`: 6 wins, 4 losses, 6 draws

The `baseline-rnn` losses on the same seeds are different in shape:

- 3 `late_jump_on_low_ball`
- 4 `rear_wall_contact`
- 1 `other`

That makes the gap look like a mix of:

1. `attack` still getting stuck in low-receive and rear-wall states.
2. `attack` not converting enough neutral/draw rallies into wins.
3. `baseline-rnn` being more aggressive and more varied in action selection, which appears to help it convert points even though it also has some late-jump and rear-wall losses.

## What `rally-serve` and `post-contact` Add

Both optional comparators remove losses on this slice:

- `rally-serve`: 4 wins, 0 losses, 12 draws, mean score 0.3125
- `post-contact`: 4 wins, 0 losses, 12 draws, mean score 0.3125

They do not separate from each other here, but they do show the likely missing ingredient for `attack`:

- explicit point-reset serve detection
- post-contact conversion after a recent ball/agent flip

That is consistent with the `attack` losses being defensive follow-through failures rather than a simple late-contact overcommit bug.

## Next Hypotheses

1. Add or widen serve-reset detection and post-contact conversion behavior, then rerun only `9000..9049` dev seeds.
2. Strengthen low-receive and rear-wall recovery, especially the `low_ball_rescue`, `grounded_low_receive`, and `rear_wall_low_jump` branches.
3. If continuing trace work, compare which states trigger `baseline-rnn`'s high-rate `101`/`110` actions and whether those transitions convert more draw states into wins than `attack`.

## Recommendation

No promotion recommendation from this trace slice. This is diagnostic evidence only.

## Source Anchors

- Generation-4 seed split: `heuristic_learning/hl_benchmark/slimevolley/protocol.py:61-65`
- Trace frame and point-event capture: `heuristic_learning/hl_benchmark/slimevolley/adapter.py:138-180`
- `attack` / `rally-serve` / `post-contact` definitions: `heuristic_learning/hl_benchmark/policies/slimevolley.py:1055-1290`
- Packaged baseline-RNN wrapper: `heuristic_learning/hl_benchmark/policies/slimevolley.py:1994-2020`

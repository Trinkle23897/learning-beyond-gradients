# Generation-4 Grounded Low Receive Subagent Probe

Date: 2026-05-27

## Protocol

- Role: Worker B, development-only structural branch probes for `grounded_low_receive`.
- Harness: temporary no-ledger script at `/tmp/g4_grounded_low_receive_probe.py`; no source, policy, or test files were edited.
- Short screen: generation-4 development seeds `9000..9015` inclusive, 16 episodes, opponent `builtin`.
- Full check: generation-4 development seeds `9000..9049` inclusive, 50 episodes, opponent `builtin`.
- Fixed pool gate: generation-4 development seeds `9000..9049` inclusive, 50 episodes per opponent.
- No holdout or audit seeds were used. In particular, no `10000`, `11000`, `13000`, or `14000` seed ranges were run.

Commands used from `heuristic_learning/`:

```bash
PYTHONPATH=. .venv/bin/python /tmp/g4_grounded_low_receive_probe.py --mode short
PYTHONPATH=. .venv/bin/python /tmp/g4_grounded_low_receive_probe.py --mode full --candidates attack rally-serve baseline-rnn glr_restore_low_rescue glr_prev_frame_gate glr_near_net_drive glr_force_jump_unsafe
PYTHONPATH=. .venv/bin/python /tmp/g4_grounded_low_receive_probe.py --mode pool --candidates glr_restore_low_rescue
```

## Candidate Definitions

All GLR probes are structural branch probes layered on current `rally-serve`; no scalar/config thresholds were changed.

| Candidate | Label | Definition |
| --- | --- | --- |
| `attack` | reference | Current `attack` policy unchanged. |
| `rally-serve` | reference | Current `rally-serve` policy unchanged. |
| `baseline-rnn` | reference | Packaged SlimeVolley 120-parameter RNN comparator. |
| `glr_restore_low_rescue` | structural | When `grounded_low_receive` fires, replace no-jump suppression with ordinary `low_ball_rescue` jump-window behavior. |
| `glr_force_jump_unsafe` | structural | When GLR fires, force jump bit on the existing movement action without front-hit suppression. |
| `glr_force_jump_safe` | structural | When GLR fires, force jump bit, then reapply front-hit suppression. |
| `glr_forward_nojump` | structural | When GLR fires, force forward/no-jump (`100`). |
| `glr_back_nojump` | structural | When GLR fires, force back/no-jump (`010`). |
| `glr_noop_nojump` | structural | When GLR fires, force no-op/no-jump (`000`). |
| `glr_split_low_jump_high_suppress` | structural | Separate low/high GLR: if `ball_y <= 0.34`, defer to low-rescue jump; otherwise keep base suppression. |
| `glr_split_high_jump_low_suppress` | structural | Separate low/high GLR: if `ball_y > 0.34`, defer to low-rescue jump; otherwise keep base suppression. |
| `glr_prev_frame_gate` | structural/history | Suppress only when the previous frame was also GLR-like; otherwise defer to low-rescue jump. |
| `glr_recent_jump_gate` | structural/history | Suppress only after a jump in the previous four actions; otherwise defer to low-rescue jump. |
| `glr_agent_descending_jump` | structural | If agent vertical velocity is descending/nonpositive, defer to low-rescue jump; otherwise keep base suppression. |
| `glr_near_net_drive` | structural | On near-net leftward GLR (`ball_x <= 0.45`, `ball_vx < -0.35`), force forward+jump (`101`). |
| `glr_rear_side_backstop` | structural | On rear-side GLR (`ball_x >= 1.20`), force back/no-jump. |
| `glr_recent_own_contact_restore` | structural/history | If recent modes include own low contact/attack, defer GLR to low-rescue jump. |

## Short Screen Results

Seeds `9000..9015`, opponent `builtin`.

| Candidate | Mean | W-L-D | Steps | GLR frames | Changed actions |
| --- | ---: | --- | ---: | ---: | ---: |
| `attack` | -0.1250 | 2/4/10 | 48,000 | n/a | n/a |
| `rally-serve` | 0.3125 | 4/0/12 | 48,000 | n/a | n/a |
| `baseline-rnn` | 0.1250 | 6/4/6 | 48,000 | n/a | n/a |
| `glr_restore_low_rescue` | 0.3125 | 4/0/12 | 48,000 | 6 | 6 |
| `glr_force_jump_unsafe` | 0.3125 | 4/0/12 | 48,000 | 6 | 6 |
| `glr_force_jump_safe` | 0.3125 | 4/0/12 | 48,000 | 6 | 6 |
| `glr_forward_nojump` | 0.3125 | 4/0/12 | 48,000 | 6 | 2 |
| `glr_back_nojump` | 0.2500 | 4/1/11 | 48,000 | 4 | 4 |
| `glr_noop_nojump` | 0.2500 | 4/1/11 | 48,000 | 4 | 4 |
| `glr_split_low_jump_high_suppress` | 0.3125 | 4/0/12 | 48,000 | 6 | 6 |
| `glr_split_high_jump_low_suppress` | 0.3125 | 4/0/12 | 48,000 | 6 | 0 |
| `glr_prev_frame_gate` | 0.3125 | 4/0/12 | 48,000 | 6 | 3 |
| `glr_recent_jump_gate` | 0.3125 | 4/0/12 | 48,000 | 6 | 0 |
| `glr_agent_descending_jump` | 0.3125 | 4/0/12 | 48,000 | 6 | 0 |
| `glr_near_net_drive` | 0.3125 | 4/0/12 | 48,000 | 6 | 2 |
| `glr_rear_side_backstop` | 0.3125 | 4/0/12 | 48,000 | 6 | 0 |
| `glr_recent_own_contact_restore` | 0.3125 | 4/0/12 | 48,000 | 6 | 6 |

Short-screen interpretation: no probe beat `rally-serve`; `glr_back_nojump` and `glr_noop_nojump` introduced one loss. The best probes tied the current reference while changing only 0 to 6 actions across 48,000 steps.

## Full Built-In Check

Seeds `9000..9049`, opponent `builtin`.

| Candidate | Mean | W-L-D | Steps | GLR frames | Changed actions |
| --- | ---: | --- | ---: | ---: | ---: |
| `attack` | -0.30 | 7/18/25 | 150,000 | n/a | n/a |
| `rally-serve` | 0.14 | 13/8/29 | 150,000 | n/a | n/a |
| `baseline-rnn` | 0.12 | 18/12/20 | 150,000 | n/a | n/a |
| `glr_restore_low_rescue` | 0.14 | 13/8/29 | 150,000 | 30 | 30 |
| `glr_prev_frame_gate` | 0.14 | 13/8/29 | 150,000 | 30 | 10 |
| `glr_near_net_drive` | 0.14 | 13/8/29 | 150,000 | 30 | 6 |
| `glr_force_jump_unsafe` | 0.14 | 13/8/29 | 150,000 | 30 | 30 |

All full-checked GLR variants exactly matched the `rally-serve` per-seed score vector. They are not improvements over the current generation-4 candidate even though they inherit its small built-in development edge over `baseline-rnn`.

## Fixed Development Opponent Pool

Because `glr_restore_low_rescue` tied `rally-serve` at `0.14` and therefore exceeded the same-seed `baseline-rnn` built-in mean `0.12`, I ran the fixed generation-4 development opponent pool before making any recommendation. Seeds were `9000..9049`.

| Candidate | Opponent | Mean | W-L-D | Steps | GLR frames | Changed actions |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| `glr_restore_low_rescue` | `builtin` | 0.14 | 13/8/29 | 150,000 | 30 | 30 |
| `glr_restore_low_rescue` | `random` | 4.74 | 50/0/0 | 38,217 | 13 | 13 |
| `glr_restore_low_rescue` | `initial` | 4.68 | 50/0/0 | 44,634 | 13 | 13 |
| `glr_restore_low_rescue` | `improved-v0` | 4.70 | 50/0/0 | 43,242 | 15 | 15 |
| `glr_restore_low_rescue` | `improved-v2` | 4.38 | 49/1/0 | 76,391 | 21 | 21 |
| `glr_restore_low_rescue` | `improved-v3` | 2.98 | 48/0/2 | 138,122 | 18 | 18 |
| `glr_restore_low_rescue` | `improved-v4` | 2.34 | 44/0/6 | 143,814 | 16 | 16 |
| `glr_restore_low_rescue` | `improved-v5` | 1.16 | 32/7/11 | 149,716 | 19 | 19 |
| `glr_restore_low_rescue` | `improved-v6` | 1.22 | 32/7/11 | 149,716 | 17 | 17 |

These rows match the recorded `rally-serve` development matrix, so the fixed-pool check does not add evidence for a new branch promotion.

## Failure Analysis

The current `grounded_low_receive` branch is too sparse on the generation-4 built-in development range to support a useful local edit. It fired only 6 times on `9000..9015` and 30 times on `9000..9049`. Even direct branch ablations that changed every GLR action (`glr_restore_low_rescue`, `glr_force_jump_unsafe`) left every full-dev episode score unchanged.

The action-change pattern also suggests the branch is not the live failure point. Restoring the jump window changed `000->001` 9 times and `100->101` 21 times on full built-in dev, but did not convert any draw or loss. The previous-frame and near-net variants made smaller, targeted changes and also produced identical scores.

Forcing back/no-jump or no-op/no-jump was actively worse on the short screen: both added a loss on the same 16-seed subset, falling from `0.3125` to `0.2500`. That makes "more passive grounded receive" a bad direction.

The fixed-pool result shows the best tied branch variant inherits `rally-serve` robustness rather than improving it. It does not repair the known concern that `rally-serve` relies on draws versus `builtin` and has fewer wins than `baseline-rnn` (`13` vs `18`) despite a slightly higher mean.

## Promotion Recommendation

Do not promote any `grounded_low_receive` branch candidate.

Best candidate by cleanliness is `glr_restore_low_rescue`, but it is only a tie with current `rally-serve`: `0.14`, `13/8/29`, `150,000` steps on full built-in dev. The fixed development opponent-pool check also matches the existing `rally-serve` matrix instead of showing a new gain. Keep `rally-serve` as the archived generation-4 candidate and do not tune or promote from these GLR probes.

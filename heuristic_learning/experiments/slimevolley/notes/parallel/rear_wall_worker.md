# Rear Wall Worker B Probe

## exact seeds used

- Short screening used only generation-4 development seeds `9000..9015` against the built-in opponent, 16 episodes per candidate, no ledger writes.
- Full checks used only generation-4 development seeds `9000..9049` against the built-in opponent, 50 episodes per candidate, no ledger writes.
- No holdout or audit seeds were used.

## candidate definitions

| Candidate | Definition |
| --- | --- |
| `attack_current` | Current `attack` policy reference: `improved-tuned` v2 plus late-contact attack. |
| `scalar_disable_rear_wall_press` | `attack` with `rear_wall_press_x=9.0`, effectively disabling `rear_wall_press`; late-contact attack unchanged. |
| `scalar_low_jump_y045_vx010` | `attack` with `rear_wall_low_jump_y=0.45` and `rear_wall_low_jump_vx=0.10`. |
| `scalar_low_jump_broad` | `attack` with `rear_wall_low_jump_y=0.50`, `rear_wall_low_jump_vx=0.20`, `rear_wall_low_jump_vy=0.0`, and `rear_wall_low_jump_agent_x=1.70`. |
| `scalar_press_jump_margin025` | `attack` with `rear_wall_press_jump_margin=0.25`. |
| `struct_press_forward_nojump` | In the `rear_wall_press` branch, replace current action with `100` and no jump. |
| `struct_press_forward_jump_raw` | In the `rear_wall_press` branch, force `101` with no front-hit jump suppression. |
| `struct_press_backward_jump_raw` | In the `rear_wall_press` branch, force `011` with no front-hit jump suppression. |
| `struct_press_low_forward_jump_raw` | In the `rear_wall_press` branch, force `101` only when `ball_y <= 0.45`; otherwise keep current branch behavior. |
| `struct_press_jump_no_suppress` | Keep current `rear_wall_press` jump criterion, but remove front-hit jump suppression inside that branch. |

## score mean/W-L-D/steps for each candidate

Short screen on `9000..9015`:

| Candidate | Mean | W-L-D | Steps |
| --- | ---: | --- | ---: |
| `attack_current` | -0.1250 | 2-4-10 | 48000 |
| `scalar_disable_rear_wall_press` | -0.5625 | 0-6-10 | 48000 |
| `scalar_low_jump_y045_vx010` | -0.3125 | 1-5-10 | 48000 |
| `scalar_low_jump_broad` | -0.2500 | 1-4-11 | 48000 |
| `scalar_press_jump_margin025` | -0.1250 | 2-4-10 | 48000 |
| `struct_press_forward_nojump` | -0.7500 | 0-7-9 | 48000 |
| `struct_press_forward_jump_raw` | -0.8125 | 0-8-8 | 48000 |
| `struct_press_backward_jump_raw` | -0.1250 | 2-4-10 | 48000 |
| `struct_press_low_forward_jump_raw` | -0.2500 | 1-4-11 | 48000 |
| `struct_press_jump_no_suppress` | -0.1250 | 2-4-10 | 48000 |

Full checks on `9000..9049` for tied short-screen probes:

| Candidate | Mean | W-L-D | Steps |
| --- | ---: | --- | ---: |
| `attack_current` | -0.3000 | 7-18-25 | 150000 |
| `scalar_press_jump_margin025` | -0.3000 | 7-18-25 | 150000 |
| `struct_press_backward_jump_raw` | -0.3000 | 7-19-24 | 150000 |
| `struct_press_jump_no_suppress` | -0.3000 | 7-19-24 | 150000 |

## structural vs scalar/config label

| Candidate | Label |
| --- | --- |
| `attack_current` | structural/current reference |
| `scalar_disable_rear_wall_press` | scalar/config ablation |
| `scalar_low_jump_y045_vx010` | scalar/config |
| `scalar_low_jump_broad` | scalar/config |
| `scalar_press_jump_margin025` | scalar/config |
| `struct_press_forward_nojump` | structural branch probe |
| `struct_press_forward_jump_raw` | structural branch probe |
| `struct_press_backward_jump_raw` | structural branch probe |
| `struct_press_low_forward_jump_raw` | structural branch probe |
| `struct_press_jump_no_suppress` | structural branch probe |

## failure analysis

The rear-wall branch is not the limiting scalar in these probes. On the full dev check, `attack_current` had loss buckets `low_far_right=8`, `low_left_or_net=14`, `low_mid_right=2`, and `other=8`, with only four point-loss events recorded under `rear_wall_press` and four under `rear_wall_low_jump`. Widening `rear_wall_press_jump_margin` was behaviorally identical to current attack.

The structural rear-wall action changes did not help. Forcing rear-wall press to move forward, with or without jump, made short-screen low-far-right losses much worse (`14` or `15` versus `2` for current attack). Forcing backward+jump or removing suppression matched the full-seed mean but changed W-L-D from `7-18-25` to `7-19-24`, so the apparent short-screen tie did not become an improvement.

Disabling `rear_wall_press` was actively harmful on the short screen, increasing low-far-right losses to `10`. Broadening `rear_wall_low_jump` also trailed current attack, suggesting the current rear-wall low-jump guard is already near the useful range for this branch family.

No candidate beat the baseline-rnn built-in dev mean `0.12`; the best full-check mean remained `-0.30`.

## promotion recommendation

Do not promote any rear-wall branch candidate from this worker run. The current `attack` policy remains the best reference among these probes, but it is still below the baseline-rnn built-in development mean and already has known opponent-pool regressions. Any future rear-wall candidate that beats `0.12` on built-in dev still requires fixed generation-4 development opponent-pool checks before any holdout consideration.

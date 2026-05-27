# Grounded Low Receive Worker Probe

## Exact Seeds Used

- Short screening only: generation-4 development seeds `9000..9015` inclusive, 16 episodes per candidate.
- Opponent: `builtin`.
- No holdout or audit seeds were used.
- No full `9000..9049` check was run because no candidate improved on the short-screen `attack` reference or beat the `baseline-rnn` built-in dev mean `0.12`.
- Runs were no-ledger, runtime-only probes using the existing `heuristic_learning/.venv`.

## Candidate Definitions

| Candidate | Structural vs scalar/config label | Definition |
| --- | --- | --- |
| `attack_current` | baseline | Current `attack` policy unchanged. |
| `glr_disable_branch` | structural branch ablation | When `attack` reports `grounded_low_receive`, bypass that suppression: preserve the `late_low_ball_guard` subset, otherwise use ordinary `low_ball_rescue` jump if within `low_ball_rescue_x_window`. |
| `glr_force_jump` | structural branch action change | When `grounded_low_receive` fires, force the jump bit while preserving the branch movement action. |
| `glr_forward_nojump` | structural branch action change | When `grounded_low_receive` fires, force forward/no-jump. |
| `glr_back_nojump` | structural branch action change | When `grounded_low_receive` fires, force backward/no-jump. |
| `glr_noop_nojump` | structural branch action change | When `grounded_low_receive` fires, force no-op/no-jump. |
| `glr_forward_jump_wide` | structural branch action change | When `grounded_low_receive` fires with `ball_x > 0` and `ball_y <= 0.60`, force forward+jump. |
| `attack_glr_margin_0p16` | scalar/config | Current `attack` with `grounded_low_receive_airborne_margin = 0.16`. |
| `attack_glr_margin_0p20` | scalar/config | Current `attack` with `grounded_low_receive_airborne_margin = 0.20`. |
| `glr_wide_y_vy` | scalar/config | Current `attack` with broader trigger: `grounded_low_receive_y = 0.65`, `grounded_low_receive_vy = -0.35`, margin `0.12`. |
| `glr_narrow_late` | scalar/config | Current `attack` with narrower/later trigger: `grounded_low_receive_y = 0.42`, `grounded_low_receive_vy = -0.65`, margin `0.12`. |
| `glr_margin_0p00` | scalar/config | Current `attack` with `grounded_low_receive_airborne_margin = 0.00`. |
| `glr_margin_0p28` | scalar/config | Current `attack` with `grounded_low_receive_airborne_margin = 0.28`. |
| `glr_pre_low_delay` | structural branch expansion | After `attack` chooses `low_ball_rescue`, suppress jump for early grounded/near-ground low receive: `0.30 <= ball_y <= 0.55`, `ball_vy < -0.45`, `agent_y <= ball_y + 0.12`. |
| `glr_pre_low_forward_delay` | structural branch expansion | Same early receive detector as `glr_pre_low_delay`, but force forward/no-jump. |
| `glr_pre_low_forward_jump` | structural branch expansion | After `attack` chooses `low_ball_rescue`, force forward+jump when `ball_vx < -0.25` and `0.28 < agent_x - ball_x <= 0.65`. |
| `glr_pre_low_nojump_all` | structural branch expansion | After `attack` chooses `low_ball_rescue`, clear jump for any descending low receive with `0.26 <= ball_y <= 0.60`, regardless of `agent_y`. |

## Score Mean/W-L-D/Steps For Each Candidate

All rows use seeds `9000..9015` vs `builtin`.

| Candidate | Mean | W-L-D | Steps |
| --- | ---: | --- | ---: |
| `attack_current` | -0.125 | 2-4-10 | 48,000 |
| `glr_disable_branch` | -0.125 | 2-4-10 | 48,000 |
| `glr_force_jump` | -0.125 | 2-4-10 | 48,000 |
| `glr_forward_nojump` | -0.125 | 2-4-10 | 48,000 |
| `glr_back_nojump` | -0.125 | 2-4-10 | 48,000 |
| `glr_noop_nojump` | -0.125 | 2-4-10 | 48,000 |
| `glr_forward_jump_wide` | -0.125 | 2-4-10 | 48,000 |
| `attack_glr_margin_0p16` | -0.125 | 2-4-10 | 48,000 |
| `attack_glr_margin_0p20` | -0.125 | 2-4-10 | 48,000 |
| `glr_wide_y_vy` | -0.125 | 2-4-10 | 48,000 |
| `glr_narrow_late` | -0.125 | 2-4-10 | 48,000 |
| `glr_margin_0p00` | -0.125 | 2-4-10 | 48,000 |
| `glr_margin_0p28` | -0.125 | 2-4-10 | 48,000 |
| `glr_pre_low_delay` | -0.750 | 1-10-5 | 48,000 |
| `glr_pre_low_forward_delay` | -4.8125 | 0-16-0 | 15,088 |
| `glr_pre_low_forward_jump` | -0.125 | 2-4-10 | 48,000 |
| `glr_pre_low_nojump_all` | -0.6875 | 1-9-6 | 48,000 |

## Structural Vs Scalar/Config Label

- Structural branch action/ablation probes: `glr_disable_branch`, `glr_force_jump`, `glr_forward_nojump`, `glr_back_nojump`, `glr_noop_nojump`, `glr_forward_jump_wide`.
- Structural branch expansion probes: `glr_pre_low_delay`, `glr_pre_low_forward_delay`, `glr_pre_low_forward_jump`, `glr_pre_low_nojump_all`.
- Scalar/config probes: `attack_glr_margin_0p16`, `attack_glr_margin_0p20`, `glr_wide_y_vy`, `glr_narrow_late`, `glr_margin_0p00`, `glr_margin_0p28`.

## Failure Analysis

The maintained `grounded_low_receive` branch is sparse on this short built-in subset: counted `attack` fired it only 9 frames across 48,000 environment steps. Directly changing the action taken inside the current branch did not move any episode outcome.

Scalar trigger changes also failed to move score. Even `grounded_low_receive_airborne_margin = 0.28`, which shifted several current-branch frames into `late_low_ball_guard`, preserved the same 2-4-10 result.

Broadening the branch into ordinary `low_ball_rescue` states was harmful. `glr_pre_low_delay` overrode 1,727 low-rescue actions and fell to mean `-0.750`; `glr_pre_low_nojump_all` overrode 1,873 actions and fell to `-0.6875`; forcing forward/no-jump collapsed to `-4.8125`. This repeats the earlier lesson that broad jump suppression removes useful contacts rather than solving built-in return timing.

`glr_pre_low_forward_jump` made only 14 overrides and tied the reference, so widening the late-contact attack from this branch did not expose a useful short-screen signal.

## Promotion Recommendation

Do not promote any candidate. No probe beat the short-screen `attack_current` mean `-0.125`, and no probe beat the `baseline-rnn` built-in dev mean `0.12`; therefore none requires fixed dev opponent-pool checks before holdout.

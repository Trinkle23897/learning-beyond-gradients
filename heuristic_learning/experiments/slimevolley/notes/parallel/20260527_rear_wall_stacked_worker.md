# Rear-Wall Stacked Worker Probe

Date: 2026-05-27

Worker: C

## Protocol

- Short screening used only generation-4 development seeds `9000..9015` against `builtin`, 16 episodes per candidate, no ledger writes.
- Full checks used only generation-4 development seeds `9000..9049` against `builtin`, 50 episodes per candidate, no ledger writes.
- No holdout seeds `10000..10049` were used.
- No audit seeds `11000..11049` were used.
- `slimevolley-final-eval` was not run.
- Temporary policy subclasses were defined in `/tmp` or directly in memory; no policy, source, or test files were edited.

## Candidate Definitions

All structural probes wrap current `rally-serve` unless labeled as a reference. Stacked features used an 8-frame observation history and distinguished:

- `approach_wall`: low far-right ball still moving/integrating toward the rear wall.
- `already_bounced`: low far-right ball with negative current/stacked ball dx, recent rear-wall vx flip, or a recent max-x turn near the rear wall.
- `recent_wall_contact`: a high-x vx flip or x-turn signal near the rear wall.

| Candidate | Label | Definition |
| --- | --- | --- |
| `attack_reference` | reference structural candidate | Current `attack` policy. |
| `rally_serve_reference` | reference structural+scalar candidate | Current `rally-serve` policy. |
| `baseline_rnn_reference` | neural comparator | Shipped SlimeVolley RNN wrapper. |
| `rw_stack_bounced_forward_jump` | structural stacked-history branch probe | On already-bounced low rear-wall states, force `101`. |
| `rw_stack_bounced_backward_jump` | structural stacked-history branch probe | On already-bounced low rear-wall states, force `011`. |
| `rw_stack_bounced_forward_nojump` | structural stacked-history branch probe | On already-bounced low rear-wall states, force `100`. |
| `rw_stack_approach_backward_nojump` | structural stacked-history branch probe | On wall-approach low rear-wall states, force `010`. |
| `rw_stack_approach_backward_jump` | structural stacked-history branch probe | On wall-approach low rear-wall states, force `011`. |
| `rw_wall_contact_hold_forward` | structural stacked-history branch probe | After rear-wall contact signal, hold forward/no-jump up to 4 steps while the ball remains low right. |
| `rw_wall_contact_hold_jump_close` | structural stacked-history branch probe | After rear-wall contact signal, recover forward and jump only when close enough for low contact. |
| `rw_two_phase_approach_then_bounce` | structural stacked-history branch probe | `010` on approach-wall states, then `101` on already-bounced states. |
| `rw_stack_bounced_noop_nojump` | structural stacked-history branch probe | On already-bounced very-low rear-wall states, force `000`. |
| `rw_lowjump_forward_nojump` | structural branch action probe | When inherited `rear_wall_low_jump` fires, force `100`. |
| `rw_lowjump_backward_jump` | structural branch action probe | When inherited `rear_wall_low_jump` fires, force `011`. |
| `rw_lowjump_backward_nojump` | structural branch action probe | When inherited `rear_wall_low_jump` fires, force `010`. |
| `rw_lowjump_noop_nojump` | structural branch action probe | When inherited `rear_wall_low_jump` fires, force `000`. |

## Short Screen Results

Seeds: `9000..9015`. Opponent: `builtin`.

| Candidate | Mean | W/L/D | Steps | Override frames |
| --- | ---: | --- | ---: | ---: |
| `attack_reference` | `-0.1250` | `2/4/10` | `48000` | `0` |
| `rally_serve_reference` | `0.3125` | `4/0/12` | `48000` | `0` |
| `baseline_rnn_reference` | `0.1250` | `6/4/6` | `48000` | `0` |
| `rw_stack_bounced_forward_jump` | `-0.2500` | `2/5/9` | `48000` | `83` |
| `rw_stack_bounced_backward_jump` | `-0.3125` | `1/5/10` | `48000` | `55` |
| `rw_stack_bounced_forward_nojump` | `-0.1250` | `2/4/10` | `48000` | `85` |
| `rw_stack_approach_backward_nojump` | `0.0000` | `3/3/10` | `48000` | `40` |
| `rw_stack_approach_backward_jump` | `0.0000` | `3/3/10` | `48000` | `36` |
| `rw_wall_contact_hold_forward` | `-0.1875` | `2/6/8` | `48000` | `159` |
| `rw_wall_contact_hold_jump_close` | `-0.4375` | `1/7/8` | `48000` | `189` |
| `rw_two_phase_approach_then_bounce` | `-0.6250` | `1/8/7` | `48000` | `107` |
| `rw_stack_bounced_noop_nojump` | `0.3125` | `3/0/13` | `48000` | `23` |
| `rw_lowjump_forward_nojump` | `0.3125` | `4/0/12` | `48000` | `6` |
| `rw_lowjump_backward_jump` | `0.3125` | `4/0/12` | `48000` | `5` |
| `rw_lowjump_backward_nojump` | `0.3125` | `4/0/12` | `48000` | `5` |
| `rw_lowjump_noop_nojump` | `0.3125` | `4/0/12` | `48000` | `6` |

## Full Development Checks

Full `9000..9049` checks were run only for the non-regressing short-screen probes that tied `rally-serve` and cleared the `0.12` built-in comparator threshold. Other stacked rear-wall candidates were not run full because they trailed `rally-serve` on the fixed short subset and did not materially improve.

Seeds: `9000..9049`. Opponent: `builtin`.

| Candidate | Mean | W/L/D | Steps | Override frames |
| --- | ---: | --- | ---: | ---: |
| `rally_serve_reference` | `0.1400` | `13/8/29` | `150000` | `0` |
| `rw_stack_bounced_noop_nojump` | `0.0800` | `10/9/31` | `150000` | `91` |
| `rw_lowjump_forward_nojump` | `0.1400` | `13/8/29` | `150000` | `15` |
| `rw_lowjump_backward_jump` | `0.1400` | `13/8/29` | `150000` | `14` |
| `rw_lowjump_backward_nojump` | `0.1400` | `13/8/29` | `150000` | `14` |
| `rw_lowjump_noop_nojump` | `0.1400` | `13/8/29` | `150000` | `15` |

## Failure Analysis

On full `rally-serve`, point-loss buckets from trace windows were `low_left_or_net=10`, `low_mid_right=4`, and `rear_wall_mode_loss=4`. The rear-wall losses that reached diagnostics were all `rear_wall_low_jump` events; `rear_wall_press` did not appear in the full-reference loss modes.

Broad stacked rear-wall overrides were harmful. The contact-hold and two-phase probes overrode 107-189 frames on the short screen and created more rear-wall-mode losses, suggesting the hold/recover interpretation keeps intervening after the useful wall-contact instant. Forcing post-bounce forward+jump or backward+jump also regressed immediately.

The only broad stacked candidate that tied the short screen, `rw_stack_bounced_noop_nojump`, failed the full check: mean dropped to `0.08`, W/L/D moved to `10/9/31`, and rear-wall-mode losses rose from `4` to `7`. Treating already-bounced very-low rear-wall states as passive/no-op is brittle outside the short subset.

Exact `rear_wall_low_jump` action swaps were behaviorally neutral on full dev. They changed only 14-15 frames across 150000 steps and exactly matched `rally-serve` score, W/L/D, and loss buckets. This implies the branch is too sparse or too outcome-insensitive for action-only edits to solve the remaining low far-right losses.

The low-far-right interpretation is therefore narrower than expected: with the trace classifier, full `rally-serve` losses were mostly left/net or mid-right low balls, and the far-right losses that were visible were already inside `rear_wall_low_jump`, not unhandled `rear_wall_press` states.

## Promotion Recommendation

Do not promote any candidate from this worker run.

The best full-development result was a tie with current `rally-serve` at mean `0.14`, W/L/D `13/8/29`; no structural probe improved built-in development score or robustness evidence. Because built-in-only score is not sufficient for promotion, even a future rear-wall variant that beats the `0.12` comparator must first pass the fixed generation-4 development opponent-pool check before any holdout consideration.

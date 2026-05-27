# Generation-4 Low Receive Teacher/Scalar Follow-up

Date: 2026-05-27

## Protocol

This follow-up used only generation-4 development seeds:

- Short screening seeds: `9000..9015`.
- Full validation seeds: `9000..9049`.
- No generation-4 holdout seeds `10000..10049` were used.
- No generation-4 audit seeds `11000..11049` were used.
- Runs were no-ledger development probes. No candidate was promoted.

## Motivation

The prior parallel trace diagnostic showed that the `attack` candidate trails
the packaged neural/RNN comparator on built-in development seeds:

| Policy | Opponent | Seeds | Mean | W/L/D | Steps |
| --- | --- | --- | ---: | --- | ---: |
| `attack` | `builtin` | `9000..9049` | `-0.30` | `7/18/25` | `150000` |
| `baseline-rnn` | `builtin` | `9000..9049` | `0.12` | `18/12/20` | `150000` |

The same diagnostic pointed at low-left/net and low own-side floor-height
losses, especially around `grounded_low_receive`, `low_ball_rescue`, and
rear-wall branches.

## Teacher-Action Diagnostic

A no-ledger diagnostic replayed `attack` against `builtin` on seeds
`9000..9049` with a 36-frame pre-point trace window. On each lost-point trace
frame, the packaged `baseline-rnn` policy was queried on the same observation
as a teacher signal. The RNN was used only for diagnosis, not as runtime policy.

Headline reproduction:

| Policy | Mean | W/L/D | Steps | Point events | Lost point events |
| --- | ---: | --- | ---: | ---: | ---: |
| `attack` | `-0.30` | `7/18/25` | `150000` | `49` | `32` |

Loss-window buckets from the final eight frames before each lost point:

| Bucket | Frames | Dominant attack modes | Teacher-action pattern |
| --- | ---: | --- | --- |
| `low_left_or_net` | `61` | `grounded_low_receive`, `late_contact_attack`, `low_ball_rescue` | mostly `101`, with many `001` |
| `near_net_nonlow` | `58` | `low_ball_rescue`, `late_contact_attack` | mixed `101`, `001`, and lateral actions |
| `far_right_nonlow` | `46` | `rear_wall_press`, `falling_floor_intercept` | mostly `001` and `101` |
| `low_other_own_side` | `34` | `grounded_low_receive`, `low_ball_rescue` | `101` on all sampled frames |
| `low_far_right` | `22` | `rear_wall_press`, `rear_wall_low_jump` | mostly `101` |

Interpretation: the current heuristic often suppresses jump in
`grounded_low_receive` exactly where the RNN teacher would still jump, but
teacher actions were not uniform enough to justify blindly copying a broad
rule.

## Structural Probe

Candidate family:

- `LowDriveFinish`: if the ball is low, descending, moving toward the net or
  opponent, and the agent is behind/right of the ball, override to
  forward+jump (`101`).
- `NetVerticalBlock`: if a low near-net ball is moving rightward into the
  agent side, override to jump-only (`001`).
- `Combined`: apply both overrides.

These are structural branch probes because they add explicit state detectors
and macro-actions. They were screened against `builtin` on seeds `9000..9015`.

| Candidate family | Best short-screen mean | W/L/D | Steps | Promotion recommendation |
| --- | ---: | --- | ---: | --- |
| Reference `attack` | `-0.125` | `2/4/10` | `48000` | Reference only |
| `LowDriveFinish` variants | `-0.125` | `2/4/10` | `48000` | Do not promote; tied reference |
| Narrow `NetVerticalBlock` variants | `-0.125` | `2/4/10` | `48000` | Do not promote; tied reference |
| Broader `NetVerticalBlock` variants | `-0.25` | `2/4/10` | `48000` | Do not promote; worse score |
| `Combined` variants | `-0.25` | `2/4/10` | `48000` | Do not promote; worse score |

Failure analysis: the teacher-action diagnostic was too coarse for a simple
one-step override. The tested jump/drive rules changed only a small number of
actions in the short screen, and broader near-net vertical blocking converted
some favorable active contacts into weaker returns.

## Scalar/Config Follow-up Search

Because the structural probe failed, a bounded scalar/config search was run
around the prior scalar `attack` base as a search-baseline check, not as
structural evidence.

Base config for the search:

- `high_arc_horizon = 0.95`
- `overcommit_guard_x = 0.20`
- `grounded_low_receive_airborne_margin = 0.16`
- `late_attack_vx = -0.45`
- `low_ball_rescue_x_window = 0.48`

Search budget:

- Short-screen configs: `98`.
- Short-screen seeds: `9000..9015`.
- Full-validated configs: `10`.
- Full-validation seeds: `9000..9049`.
- Full-validation environment steps: `1,500,000`.
- Total wall-clock time reported by the script: `80.6` seconds.

Top short-screen results:

| Candidate | Short mean | W/L/D | Seeds |
| --- | ---: | --- | --- |
| Known scalar top: `low_ball_rescue_x_window=0.48` | `0.3125` | `4/0/12` | `9000..9015` |
| Base prior scalar config | `0.3125` | `4/0/12` | `9000..9015` |
| Random candidate with late-attack/overcommit tweaks | `0.3125` | `4/0/12` | `9000..9015` |

Top full-validation results:

| Candidate | Full mean | W/L/D | Steps | Notes |
| --- | ---: | --- | ---: | --- |
| Known scalar top: `low_ball_rescue_x_window=0.48` | `-0.02` | `9/12/29` | `150000` | Best tied full result |
| `late_attack_dx_max=0.36`, `late_attack_y_min=0.24`, `overcommit_guard_x=0.18` | `-0.02` | `9/12/29` | `150000` | Tied best |
| Base prior scalar config | `-0.02` | `9/12/29` | `150000` | Tied best |
| Best non-tied alternative | `-0.04` | `9/12/29` | `150000` | Worse |

Failure analysis: the short subset overestimated the scalar candidates. Full
development validation again saturated at mean `-0.02`, which remains below
the `baseline-rnn` mean `0.12` on the same built-in development range. The
gain remains scalar/config-only and mostly increases draws rather than wins.

## Decision

Do not promote any candidate from this follow-up.

No candidate beat `baseline-rnn` on built-in development seeds, so the fixed
development opponent-pool gate was not triggered. The remaining same-seed gap
for the best scalar candidate is `0.14` score points (`0.12 - -0.02`). Future
structural work should diagnose contact outcomes and return placement over
multi-frame windows rather than adding another broad one-step low-ball action
override.

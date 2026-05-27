# Grounded Low Receive Stacked-History Worker Probe

## Protocol

- Role: Worker B, structural branch probes for `grounded_low_receive`.
- Opponent: `builtin` SlimeVolley baseline.
- Screening seeds: generation-4 development seeds `9000..9015` inclusive, 16 episodes per candidate.
- Full check seeds: generation-4 development seeds `9000..9049` inclusive for one screened candidate only.
- No holdout or audit seeds were used.
- `slimevolley-final-eval` was not run.
- Runs were no-ledger direct evaluations from a temporary `/tmp` harness; no source, policy, or test files were edited.

## Candidate Definitions

| Candidate | Structural/scalar label | Definition |
| --- | --- | --- |
| `attack_ref` | reference | Current `attack` policy unchanged. |
| `rally_serve_ref` | reference | Current maintained `rally-serve` policy unchanged. |
| `glr_conflict_suppress_only` | structural/history | Over `rally-serve`, restore normal low-rescue jump when base `grounded_low_receive` fires without reported-vs-stacked vertical velocity conflict; suppress only on conflict. |
| `glr_conflict_force_jump` | structural/history | Over `rally-serve`, force jump only when base `grounded_low_receive` overlaps reported-vs-stacked vertical velocity conflict. |
| `glr_any_low_conflict_force_jump` | structural/history | Over `rally-serve`, force jump in any low-rescue state when stacked delta conflicts with reported `vx` or `vy`. |
| `glr_recent_own_restore` | structural/history | Over `rally-serve`, restore normal low-rescue jump when base `grounded_low_receive` occurs within an 8-frame inferred own-contact hold. |
| `glr_recent_own_or_conflict_restore` | structural/history | Restore normal low-rescue jump after inferred own contact or vertical velocity conflict. |
| `glr_stacked_floor_0p32` | structural/history | Gate grounded-low suppression by stacked estimated time-to-floor `<= 0.32` instead of raw `ball_vy`. |
| `glr_stacked_floor_0p45` | structural/history | Same stacked time-to-floor gate with threshold `<= 0.45`. |
| `glr_stacked_floor_0p45_no_own` | structural/history | Stacked time-to-floor `<= 0.45`, disabled during the 8-frame own-contact hold. |
| `glr_stacked_vy_replace_raw` | structural/history | Replace the raw `ball_vy < grounded_low_receive_vy` branch gate with stacked vertical displacement `< -0.08`. |

All probes used temporary in-memory subclasses/wrappers only; no scalar tuning of maintained policy constants was used.

## Short-Screen Results

All rows use seeds `9000..9015` vs `builtin`.

| Candidate | Mean | W-L-D | Steps | Action changes | Base GLR frames |
| --- | ---: | --- | ---: | ---: | ---: |
| `attack_ref` | -0.125 | 2-4-10 | 48,000 | 0 | n/a |
| `rally_serve_ref` | 0.3125 | 4-0-12 | 48,000 | 0 | n/a |
| `glr_conflict_suppress_only` | 0.3125 | 4-0-12 | 48,000 | 6 | 6 |
| `glr_conflict_force_jump` | 0.3125 | 4-0-12 | 48,000 | 0 | 6 |
| `glr_any_low_conflict_force_jump` | 0.2500 | 5-1-10 | 48,000 | 15 | 9 |
| `glr_recent_own_restore` | 0.3125 | 4-0-12 | 48,000 | 4 | 6 |
| `glr_recent_own_or_conflict_restore` | 0.3125 | 4-0-12 | 48,000 | 4 | 6 |
| `glr_stacked_floor_0p32` | 0.3125 | 4-0-12 | 48,000 | 1 | 6 |
| `glr_stacked_floor_0p45` | 0.3125 | 4-0-12 | 48,000 | 1 | 6 |
| `glr_stacked_floor_0p45_no_own` | 0.3125 | 4-0-12 | 48,000 | 4 | 6 |
| `glr_stacked_vy_replace_raw` | 0.3125 | 4-0-12 | 48,000 | 6 | 6 |

## Full Dev Check

`glr_conflict_suppress_only` was the selected full-check candidate because it tied `rally_serve_ref` on the short screen while modifying all current GLR frames, and its inherited `rally-serve` score exceeded the built-in `baseline-rnn` mean threshold `0.12`.

| Candidate | Seeds | Mean | W-L-D | Steps | Action changes | Base GLR frames |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| `glr_conflict_suppress_only` | `9000..9049` | 0.1400 | 13-8-29 | 150,000 | 30 | 30 |

This matches the maintained `rally-serve` built-in full-dev result recorded in the current candidate metadata (`mean=0.14`, `13-8-29`), so it is not an improvement.

The other probes did not receive full `9000..9049` runs because none improved over `rally_serve_ref` on `9000..9015`; the only outcome-changing broader low-rescue conflict probe regressed mean score from `0.3125` to `0.2500`.

## Failure Analysis

Stacked/history signals are available but poorly aligned with this branch. On the short screen, the rally-serve-backed probes saw `3,598` vertical-conflict frames, `1,899` horizontal-conflict frames, `2,909` recent-own-contact frames, and `2,603` recent-opponent-contact frames, but only `6` base `grounded_low_receive` frames out of `48,000` total steps.

Because the branch is this sparse, branch-local history logic mostly changed no outcomes. Restoring jump on all non-conflict GLR frames changed 6 actions and tied the reference. Avoiding suppression after inferred own contact changed 4 actions and tied. Replacing raw `ball_vy` with stacked vertical displacement changed 6 actions and tied. Stacked time-to-floor gates changed only 1 to 4 action keys and tied.

The broader `glr_any_low_conflict_force_jump` probe did alter behavior outside the current branch: it attempted 26 low-rescue conflict jumps, changed 15 action keys, and produced more wins but introduced a `-2` loss on seed `9001`, reducing mean to `0.25`. This suggests the history signal can affect low-rescue behavior, but the effect is not stable enough and is not specific evidence that `grounded_low_receive` should be expanded.

On the full `9000..9049` check, `glr_conflict_suppress_only` changed all 30 GLR frames but still matched the maintained `rally-serve` full-dev score. The stacked conflict condition never identified the existing GLR frames as useful suppression cases; it simply restored jumps on sparse frames without moving the scoreboard.

## Promotion Recommendation

Do not promote any candidate.

Best short-screen result was a tie with `rally_serve_ref` at `0.3125`, `4-0-12`, and the one full dev check tied the maintained `rally-serve` full-dev result at `0.14`, `13-8-29`. No candidate shows material branch-specific improvement.

Any future candidate that beats `0.12` on built-in should first pass a fixed generation-4 development opponent-pool check before any holdout consideration.

# Generation-4 Parallel9 Rear-Wall Press Probe

Date: 2026-05-27

Worker: C

Kind: `structural branch action/recovery probe`

## Protocol

This was a development-only rear-wall branch probe around the current
`post-contact` policy family. It used transient code at
`/tmp/g4_parallel9_rear_wall_press_probe.py` and wrote the repository artifact
`results/generation_4_parallel9_rear_wall_press_probe.json`. No maintained
policy, ledger, summary, holdout, or audit artifact was edited by the probe.

Only generation-4 development seeds were used. Short screens used `9000..9015`;
full built-in and fixed-pool follow-ups used `9000..9049`. No generation-4
holdout seeds `10000..10049` or audit seeds `11000..11049` were used.

## Candidate Families

All branch candidates inherit `SlimeVolleyPostContactPolicy` and alter only
frames diagnosed as `rear_wall_press` or `rear_wall_low_jump`.

| Candidate | Structural idea |
| --- | --- |
| `rw_press_brace_110_close` | Replace close low rear-wall press with a `110` no-jump brace. |
| `rw_press_delay_110_then_011` | Use a one-frame `110` brace, then a delayed `011` back-jump. |
| `rw_press_release_home` | Release rear-wall press back toward home when the ball is already leaving the wall. |
| `rw_low_jump_brace_110` | Replace very low rear-wall low-jump rescue with `110`. |
| `rw_low_jump_delay_110_then_001` | Use one `110` brace frame before a delayed vertical jump. |
| `rw_low_jump_release_home` | Release very low rear-wall low-jump states back toward home. |

## Short Screen

Rows use seeds `9000..9015`.

| Candidate | Built-in | improved-v4 | improved-v5 | improved-v6 | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| `post_contact_reference` | `0.3125` | `2.7500` | `1.3125` | `1.3750` | reference |
| `baseline_rnn` | `0.1250` | `3.2500` | `2.3125` | `2.5625` | neural comparator |
| `rw_press_brace_110_close` | `0.3125` | `2.7500` | `1.3125` | `1.3750` | full built-in check |
| `rw_press_delay_110_then_011` | `0.3125` | `2.7500` | `1.3125` | `1.3750` | full built-in check |
| `rw_press_release_home` | `0.3125` | `2.8125` | `1.3125` | `1.3750` | full built-in check |
| `rw_low_jump_brace_110` | `0.3125` | `2.7500` | `1.3125` | `1.3750` | full built-in check |
| `rw_low_jump_delay_110_then_001` | `0.3125` | `2.7500` | `1.3125` | `1.3750` | full built-in check |
| `rw_low_jump_release_home` | `0.3125` | `2.7500` | `1.3125` | `1.3750` | full built-in check |

The screen did not show a robust hard-tail improvement. `rw_press_release_home`
was the only row with a visible short-screen nudge, improving `improved-v4` by
`+0.0625`, while all other rows tied the `post_contact_reference` score matrix.

## Full Built-In Check

Rows use seeds `9000..9049`, opponent `builtin`.

| Candidate | Mean | W/L/D | Trigger frames | Action changes |
| --- | ---: | --- | ---: | ---: |
| `post_contact_reference` | `0.14` | `13/8/29` | `0` | `0` |
| `baseline_rnn` | `0.12` | `18/12/20` | `0` | `0` |
| `rw_press_brace_110_close` | `0.14` | `13/8/29` | `0` | `0` |
| `rw_press_delay_110_then_011` | `0.14` | `13/8/29` | `0` | `0` |
| `rw_press_release_home` | `0.12` | `13/8/29` | `7` | `7` |
| `rw_low_jump_brace_110` | `0.14` | `13/8/29` | `12` | `12` |
| `rw_low_jump_delay_110_then_001` | `0.14` | `13/8/29` | `15` | `15` |
| `rw_low_jump_release_home` | `0.14` | `13/8/29` | `11` | `11` |

The only active full-built-in regression was `rw_press_release_home`, which
fell to the neural comparator mean and below `post_contact_reference`. The other
full-built-in rows tied the reference and were expanded only as development
diagnostics, not promotion candidates.

## Fixed Development Pool

Rows use seeds `9000..9049`. All fixed-pool follow-ups either tied
`post_contact_reference` exactly on the archived rows or were behaviorally
inert on the relevant modes. Representative hard-tail means:

| Candidate | improved-v3 | improved-v4 | improved-v5 | improved-v6 |
| --- | ---: | ---: | ---: | ---: |
| `post_contact_reference` | `3.04` | `2.40` | `1.22` | `1.28` |
| `baseline_rnn` | `3.84` | `3.26` | `2.10` | `2.18` |
| `rw_low_jump_brace_110` | `3.04` | `2.40` | `1.22` | `1.28` |
| `rw_low_jump_delay_110_then_001` | `3.04` | `2.40` | `1.22` | `1.28` |
| `rw_low_jump_release_home` | `3.04` | `2.40` | `1.22` | `1.28` |
| `rw_press_brace_110_close` | `3.04` | `2.40` | `1.22` | `1.28` |
| `rw_press_delay_110_then_011` | `3.04` | `2.40` | `1.22` | `1.28` |

## Failure Analysis

The run confirms that the remaining rear-wall branch errors are not fixed by
local `110`, delayed-jump, or release-home substitutions. The active low-jump
variants changed `11..21` frames on fixed-pool rows but did not move score. The
press-brace variants were inert on the full pool.

`rw_press_release_home` is a negative result: it produced the only short-screen
visible nudge but regressed built-in on full development seeds. None of the
rows closes the large `baseline_rnn` gap on archived hard opponents.

## Decision

Do not promote any candidate from this parallel9 rear-wall pass. Do not open
holdout or audit seeds.

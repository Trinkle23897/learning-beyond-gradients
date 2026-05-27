# Generation-4 Parallel5 Grounded-Low-Receive Probe

Date: 2026-05-27

Worker: B

Label: structural policy improvement

## Protocol

This was a development-only short-screen probe for stacked/history-aware
`grounded_low_receive` variants. No maintained policy code, ledger, holdout,
audit, or final report claim was modified during the probe. Transient code ran
from `/tmp/g4_parallel5_grounded_low_receive_probe.py`.

Seeds used exactly:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

No holdout or audit seeds were used. In particular, generation-4 holdout seeds
`10000..10049` and audit seeds `11000..11049` were not used.

Screen opponents were `builtin`, `improved-v4`, `improved-v5`, and
`improved-v6`.

JSON result artifact:

`heuristic_learning/experiments/slimevolley/results/generation_4_parallel5_grounded_low_receive_screen.json`

## Candidate Definitions

| Candidate | Type | Definition |
| --- | --- | --- |
| `rally_serve_reference` | reference | Current `SlimeVolleyRallyServePolicy`. |
| `post_contact_reference` | reference | Development-only `post-contact` candidate. |
| `baseline_rnn` | neural comparator | Packaged SlimeVolley `baseline-rnn` comparator. |
| `glr_stacked_target_jump` | structural/history | Use stacked finite-difference low-ball evidence and restore jump. |
| `glr_own_flip_jump_only` | structural/history | Jump only when recent own-contact flip evidence is present. |
| `glr_no_flip_jump_else_keep` | structural/history | Keep current action unless the low receive lacks flip evidence. |
| `glr_finite_diff_direction_check` | structural/history | Keep GLR only when raw and stacked vertical descent agree. |
| `glr_mode_rewrite_backward_brace` | structural | Rewrite rear-drifting GLR to backward no-jump brace. |
| `glr_mode_rewrite_noop_brace` | structural | Rewrite converged GLR to no-op no-jump brace. |

## Screen Results

All rows use seeds `9000..9015`.

| Candidate | builtin | improved-v4 | improved-v5 | improved-v6 | Overrides | Changes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `rally_serve_reference` | `0.3125` | `2.5625` | `1.1250` | `1.1875` | `0` | `0` |
| `post_contact_reference` | `0.3125` | `2.7500` | `1.3125` | `1.3750` | `0` | `0` |
| `baseline_rnn` | `0.1250` | `3.2500` | `2.3125` | `2.5625` | `0` | `0` |
| `glr_stacked_target_jump` | `0.3125` | `2.5625` | `1.1250` | `1.1875` | `31` | `31` |
| `glr_own_flip_jump_only` | `0.3125` | `2.5625` | `1.1250` | `1.1875` | `10` | `10` |
| `glr_no_flip_jump_else_keep` | `0.3125` | `2.5625` | `1.1250` | `1.1875` | `21` | `21` |
| `glr_finite_diff_direction_check` | `0.3125` | `2.5625` | `1.1250` | `1.1875` | `6` | `6` |
| `glr_mode_rewrite_backward_brace` | `0.3125` | `2.5625` | `1.1250` | `1.1875` | `0` | `0` |
| `glr_mode_rewrite_noop_brace` | `0.2500` | `2.5625` | `1.1250` | `1.1875` | `16` | `10` |

## Failure Analysis

The structural/history candidates changed actions in several cases, but none
improved any screened opponent over the `rally_serve_reference`. Most variants
exactly tied the reference across all four opponents, which means the added
state detectors did not move the score distribution on this slice.

`glr_mode_rewrite_noop_brace` is negative evidence: it regressed the built-in
row from `0.3125` to `0.2500` by adding one loss while leaving the archived rows
unchanged. This suggests that bracing in converged low-receive states suppresses
useful recovery movement rather than cleaning up a failure mode.

`post_contact_reference` remains the strongest transparent heuristic comparator
on the archived rows in this short screen, but it is already documented as a
development-only candidate and still trails `baseline_rnn` on every hard
archived opponent.

## Promotion Recommendation

Do not promote any `grounded_low_receive` variant from this run.

The best structural variants only tie `rally_serve_reference` on every screened
row. Because no candidate improves the reference and one variant regresses the
built-in row, there is no basis for full-pool expansion or maintained policy
edits from this evidence.

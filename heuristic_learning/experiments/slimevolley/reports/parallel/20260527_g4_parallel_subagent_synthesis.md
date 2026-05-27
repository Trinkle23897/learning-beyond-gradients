# Generation-4 Parallel Subagent Synthesis

Date: 2026-05-27

## Scope

This synthesis combines five independent subagent artifacts from the
generation-4 SlimeVolley development-only pass. All workers were constrained to
development seeds `9000..9049`; short screens used the fixed subset
`9000..9015`. No worker used holdout seeds `10000..10049`, audit seeds
`11000..11049`, generation-5 holdout seeds, or generation-5 audit seeds. No
candidate below is final evidence.

## Worker Artifacts

| Worker | Artifact | Family | Seeds | Best candidate | Mean / W-L-D / steps | Type | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | `notes/parallel/20260527_g4_attack_scalar_subagent.md` | scalar/config search around `attack` | short `9000..9015`, full `9000..9049` | `old_attack_scalar_base` / `old_base_dx48` | `-0.10`, `11-13-26`, `150000` | scalar/config | Do not promote; improves `attack` but remains below `baseline-rnn` built-in dev mean `0.12`. |
| B | `notes/parallel/20260527_g4_grounded_low_receive_subagent.md` | `grounded_low_receive` branch probes | short `9000..9015`, full/pool `9000..9049` | `glr_restore_low_rescue` | `0.14`, `13-8-29`, `150000` | structural | Do not promote; exactly tied `rally-serve` and matched its fixed-pool matrix. |
| C | `notes/parallel/20260527_g4_rear_wall_press_subagent.md` | `rear_wall_press` / rear-wall branch probes | short `9000..9015`, full/pool `9000..9049` | `struct_press_backward_jump` | `0.16`, `13-8-29`, `150000` | structural | Do not promote; built-in gain failed fixed opponent-pool robustness. |
| D | `reports/parallel/20260527_g4_trace_attack_vs_rnn_subagent.md` | trace diagnostics, `attack` vs `baseline-rnn` | short `9000..9015` | diagnostic only | `attack -0.125` vs `baseline-rnn 0.125`, both `48000` steps | diagnostics | Use traces to guide future work; no promotion evidence. |
| E | `notes/parallel/20260527_g4_archived_robustness_subagent.md` | archived-opponent robustness | full `9000..9049` | `rally-serve` as existing reference | `0.14`, `13-8-29`, `150000` vs built-in | structural plus scalar/config | Keep as frozen dev candidate only; no new promotion. |

## Promotion Gate

The promotion rule was:

1. A candidate may not be promoted from built-in opponent score alone.
2. Any candidate that beats `baseline-rnn` on built-in development seeds must be
   checked against the fixed development opponent pool before any holdout use.

Only `struct_press_backward_jump` produced a new built-in score above the
same-seed `baseline-rnn` comparator: `0.16` versus `0.12`. Worker C then ran
the fixed development opponent pool on `9000..9049`. The candidate regressed
`random`, `initial`, `improved-v0`, `improved-v3`, `improved-v4`,
`improved-v5`, and `improved-v6` versus the `rally-serve` reference. That fails
the robustness gate.

`glr_restore_low_rescue` tied `rally-serve` at `0.14` and therefore also passed
the built-in comparator threshold, but its fixed-pool rows matched
`rally-serve` rather than improving it. That is not a new policy improvement.

## Failure Analysis

The parallel pass mainly produced negative evidence.

Scalar/config search around `attack` can improve built-in development score
from `-0.30` to `-0.10`, but still trails the neural comparator and does not
count as structural learning. The best scalar variants were also already close
to prior attack-search evidence, so this does not justify another config
promotion.

`grounded_low_receive` is not a productive single-branch edit on this seed
range. Even variants that changed every detected GLR action left the full
built-in score vector unchanged. The branch fires too sparsely, and the losses
appear to depend on preceding contact and recovery context rather than the
terminal GLR action alone.

Rear-wall probing found the only new built-in improvement, but the gain was a
small trajectory shift without a W-L-D improvement. It added regressions across
the archived pool, which is exactly the adversarial brittleness the protocol is
designed to catch.

Trace diagnostics show the likely remaining mechanism gap: `baseline-rnn`
converts more front/net low opportunities into wins, while `attack` and
`rally-serve` still rely heavily on draws. The heuristic losses cluster after
contact-like low own-side windows, especially where `late_contact_attack` hands
off into low receive or rear-wall recovery.

## Decision

No policy, config, or test edit is supported by this parallel generation-4
pass. The correct single edit for this iteration is this append-only synthesis
artifact. It records that the candidate with the best built-in development
score failed the fixed-pool robustness gate, so the maintained heuristic should
not be changed from these results.

The next development-only direction, if the experiment continues under a fresh
predeclared protocol, should be structural and trace-driven: a short-history
post-contact/front-net conversion mode that distinguishes a newly redirected
ball from an untouched incoming low ball before selecting low-receive or
rear-wall behavior. That idea still needs its own fixed development screen and
opponent-pool check before any holdout use.

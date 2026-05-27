# Generation-4 Parallel Subagent Synthesis v2

Date: 2026-05-27

## Scope

This synthesis combines the second parallel development-only pass for the
SlimeVolley heuristic-learning experiment. Workers were constrained to
generation-4 development seeds `9000..9049`; short screens used the fixed
subset `9000..9015`. No holdout seeds, audit seeds, or final-evaluation commands
were used.

Before launch, an obsolete interrupted generation-5 probe using `12000..12015`
was found and stopped because it conflicted with this pass. A follow-up process
scan found no active SlimeVolley experiment processes before synthesis.

## Worker Artifacts

| Worker | Artifact | Family | Seeds | Best candidate | Mean / W-L-D / steps | Type | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `notes/parallel/20260527_g4_attack_scalar_subagent_v2.md` | scalar/config search around `attack` and `rally-serve` | short `9000..9015`, full `9000..9049` | `late_vx_-0.55` | built-in full dev `0.1400`, `14-9-27`, `150000` | scalar/config | Do not promote; tied current built-in mean and partial pool evidence was mixed. |
| 2 | `notes/parallel/20260527_g4_grounded_low_receive_subagent_v2.md` | stacked-frame `grounded_low_receive` probes | short `9000..9015`, full/pool `9000..9049` | `glr_temporal_confidence_gate` | built-in full dev `0.14`, `13-8-29`, `150000` | structural | Do not promote; exactly matched the current fixed-pool matrix. |
| 3 | `notes/parallel/20260527_g4_rear_wall_press_subagent_v2.md` | `rear_wall_press` / rear-wall branch probes | short `9000..9015`, full/pool `9000..9049` | `rw_airborne_recovery` | built-in full dev `0.1400`, `13-8-29`, `150000` | structural | Do not promote; tied current behavior and did not improve completed pool rows. |
| 4 | `reports/parallel/20260527_g4_trace_attack_vs_rnn_subagent_v2.md` | trace diagnostics, `attack` / `rally-serve` vs `baseline-rnn` | short `9000..9015` | diagnostic only | `rally-serve 0.3125`, `4-0-12`, `48000`; `baseline-rnn 0.1250`, `6-4-6` | diagnostics | Use as hypothesis source only; no promotion evidence. |
| 5 | `notes/parallel/20260527_g4_archived_robustness_subagent_v2.md` | archived-opponent robustness | full `9000..9049` canonical rows | `rally-serve` reference | built-in `0.14`, `13-8-29`, `150000`; archived rows trail RNN | robustness diagnostics | Do not promote from built-in score alone; archived-pool gap remains. |

## Promotion Gate

The gate for this pass was:

1. Do not promote a candidate from built-in opponent score alone.
2. Any candidate that beats `baseline-rnn` on built-in development seeds must be
   checked against the fixed development opponent pool before holdout use.
3. Treat scalar/config search separately from structural policy changes.

No v2 candidate cleared this gate. The scalar `late_vx_-0.55` variant tied the
current built-in mean but did not improve it. The grounded-low-receive and
rear-wall structural variants also tied or regressed current behavior. The
robustness artifact records the key failure: the current `rally-serve`
reference has a narrow built-in edge over `baseline-rnn` (`0.14` vs `0.12`) but
trails `baseline-rnn` on every archived opponent row in the fixed development
pool.

## Failure Analysis

The second scalar pass mostly moved draws into both wins and losses. It found
no built-in mean improvement over current `rally-serve`, and the partial
opponent-pool rows were mixed. That is not enough to justify another config
promotion, especially because it would still be scalar tuning rather than a
new transparent mechanism.

The stacked-frame grounded-low probes were selective enough to be auditable but
too sparse to move outcomes. The best gate changed `17` actions on full
built-in development seeds and exactly matched the existing fixed-pool scores.
The broader low-incoming-fast detector fired hundreds of times and collapsed
the short built-in screen, which is useful negative evidence: stacked-frame
signals need a contact-quality discriminator before they should control action
selection.

The rear-wall pass found a similar pattern. Broad timing edits were harmful,
while narrow guards were neutral or traded built-in score for small archived
opponent gains. None improved both the built-in comparator row and the archived
pool.

The trace worker produced the most useful next hypothesis. On `9000..9015`,
`rally-serve` beat `baseline-rnn` on mean but did so with many draws, while the
RNN remained much more jump-heavy and converted more near-net contact windows.
This supports a future short-history post-contact experiment, not an immediate
promotion.

## Decision

No policy, config, or test behavior edit is supported by this parallel pass.
The single auditable edit for this iteration is this append-only synthesis
artifact.

Next development-only experiment, if continued: implement a temporary
two-frame post-contact history gate around `rally-serve` low-receive/rear-wall
handoff behavior, then screen it on `9000..9015` and expand to the fixed
development opponent pool only if it improves more than built-in score. That
idea remains a hypothesis, not current benchmark evidence.

# Parallel Rally-Serve Development Synthesis

Date: 2026-05-27

## Protocol

This synthesis covers the parallel generation-4 development iteration requested for SlimeVolley heuristic learning. All workers used only generation-4 development seeds:

- Short screening subset: `9000..9015`.
- Full development range: `9000..9049`.
- No holdout seeds `10000..10049` were used.
- No audit seeds `11000..11049` were used.
- No `slimevolley-final-eval` command was run.
- Worker probes were no-ledger runs or summaries of existing generation-4 development rows.

Before launching the workers, a targeted process check found no still-running SlimeVolley evaluation process from prior turns.

## Worker Comparison

| Worker | Artifact | Family | Best built-in development result | Label | Recommendation |
| --- | --- | --- | --- | --- | --- |
| A | `notes/parallel/20260527_scalar_rally_attack_worker.md` | Scalar/config search around `rally-serve` and `attack` | Tied current `rally-serve`: mean `0.14`, W/L/D `13/8/29`, `150000` steps. Several tied variants had worse W/L/D `14/10/26`. | scalar/config | Do not promote; keep current `rally-serve`. |
| B | `notes/parallel/20260527_grounded_low_receive_stacked_worker.md` | Stacked-history `grounded_low_receive` probes | Full checked `glr_conflict_suppress_only`: mean `0.14`, W/L/D `13/8/29`, `150000` steps, matching current `rally-serve`. | structural/history | Do not promote; branch-local history changes were sparse and outcome-neutral. |
| C | `notes/parallel/20260527_rear_wall_stacked_worker.md` | Stacked-history rear-wall and `rear_wall_low_jump` probes | Exact low-jump action swaps tied current `rally-serve`: mean `0.14`, W/L/D `13/8/29`; broad stacked post-bounce no-op fell to `0.08`. | structural/history | Do not promote; rear-wall edits were neutral or harmful. |
| D | `reports/parallel/20260527_trace_rally_attack_rnn_worker.md` | Trace diagnostics comparing `rally-serve`, `attack`, and `baseline-rnn` | Diagnostics: `rally-serve` mean `0.14`, `attack` `-0.30`, `baseline-rnn` `0.12`, each over `150000` steps. | diagnostics only | No direct promotion; suggests future low-receive/post-contact history probes. |
| E | `notes/parallel/20260527_robustness_rallyserve_worker.md` | Archived-opponent robustness from existing dev rows | Fixed dev pool acceptable for freezing, with `improved-v5` caveat: `rally-serve` `1.16` vs `improved-tuned` `1.22`. | robustness check | Freeze for possible future sealed final eval; do not claim final success. |

## Quantitative Decision Table

| Candidate or family | Built-in dev mean | Built-in W/L/D | Fixed-pool status | Beats `baseline-rnn` built-in mean `0.12`? | Decision |
| --- | ---: | --- | --- | --- | --- |
| Current `rally-serve` | `0.14` | `13/8/29` | Mostly acceptable; one `improved-v5` regression versus scalar baseline | Yes, by `+0.02` | Keep frozen as current dev candidate. |
| Best scalar/config variants | `0.14` | Best tied variants often `14/10/26` | Not checked because they did not improve built-in mean and added losses | Yes, but tied current candidate | Do not promote. |
| Best stacked `grounded_low_receive` variant | `0.14` | `13/8/29` | Not checked further; no built-in improvement | Yes, but tied current candidate | Do not promote. |
| Best rear-wall variants | `0.14` | `13/8/29` | Not checked further; no built-in improvement | Yes, but tied current candidate | Do not promote. |
| `rw_stack_bounced_noop_nojump` | `0.08` | `10/9/31` | Regressed on full dev | No | Reject. |
| `attack` reference | `-0.30` | `7/18/25` | Known archived-opponent regressions | No | Keep only as diagnostic ancestor. |
| `baseline-rnn` comparator | `0.12` | `18/12/20` | Built-in comparator only | n/a | Comparator, not a heuristic candidate. |

## Failure Analysis

The parallel pass did not find a policy/config/test edit that should replace the current candidate. Scalar search around `rally-serve` found no mean improvement. The only scalar/config variants above the neural comparator tied `rally-serve` while adding losses, so they are weaker on the anti-overfitting criterion.

Stacked-frame probes were informative but not promotable. `grounded_low_receive` was too sparse for branch-local history gates to affect outcomes; the full checked variant changed all current GLR frames but still exactly matched `rally-serve`. Rear-wall stacked probes were either neutral in narrow inherited `rear_wall_low_jump` states or harmful when broadened into post-bounce/hold modes.

The trace diagnostic clarifies the remaining gap. `rally-serve` improves substantially over `attack` by cutting point losses from `32` to `18`, but it is not behaviorally similar to the RNN. The heuristic still wins fewer matches than `baseline-rnn` (`13` vs `18`) and relies more on draws (`29` vs `20`). The RNN's terminal wins are mostly jump-heavy `101`/`110` contacts, while `rally-serve` terminal wins remain mostly movement-only `100`, `010`, and `000` actions. This points toward a future history-aware low-receive/post-contact rule, not another scalar sweep or serve macro expansion.

## Cost Accounting

Known new development-only environment steps from worker artifacts:

| Worker | Step accounting |
| --- | ---: |
| Scalar/config search | `3,792,000` steps: `54` short rows at `48000` plus `8` full rows at `150000`. |
| Grounded-low stacked probes | `678,000` steps: `11` short rows at `48000` plus `1` full row at `150000`. |
| Rear-wall stacked probes | `1,620,000` steps: `15` short rows at `48000` plus `6` full rows at `150000`. |
| Trace diagnostics | At least `450,000` headline evaluation steps: `3` policies at `150000`; any internal recount overhead was not separately persisted. |
| Robustness check | `0` new steps; reused existing generation-4 development summary rows. |

Minimum known new environment-step cost: `6,540,000` development steps. This excludes subagent/LLM token cost, which is not available from the local harness.

## Decision

No policy/config/test promotion is evidence-supported by this parallel pass. The next single edit is therefore no code edit: keep the current `rally-serve` implementation frozen as the development candidate, record these negative worker results, and do not open holdout or audit seeds as part of tuning.

If the experiment continues on development seeds, the next predeclared experiment family should be a structural history-aware low-receive/post-contact recovery probe focused on front/net low terminal states and jump-combo timing. That would be a new development iteration, not a promotion from this one.

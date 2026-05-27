# Generation-4 Parallel4 Synthesis

Date: 2026-05-27

## Scope

This report synthesizes the fourth parallel development-only worker pass for
the SlimeVolley heuristic-learning experiment. The pass followed the
generation-4 development protocol:

- Development seeds only: `9000..9049`.
- Short screens were allowed only on the fixed subset `9000..9015`.
- No generation-4 holdout seeds `10000..10049` were used.
- No generation-4 audit seeds `11000..11049` were used.
- No `slimevolley-final-eval` command was used.
- Worker probes were no-ledger/transient except for append-only markdown
  artifacts.

A carryover no-ledger generation-5 screen from a prior turn was allowed to
finish before this pass and was excluded from all generation-4 promotion
decisions. A process check after that screen found no active SlimeVolley,
pytest, or evaluation processes other than the check itself.

## Worker Comparison

| Worker | Artifact | Family | Best candidate | Seeds | Best score summary | Type | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | `notes/parallel/g4_attack_scalar_worker_a_20260527.md` | Scalar/config around `attack` and `net-pressure` | `np_low_rescue_050` | screen `9000..9015`; fixed pool `9000..9049` | fixed-pool mean `3.0022`, but built-in `-0.18` / `9-15-26` / `150000`; below `baseline-rnn` pool mean `3.4089` | scalar/config | Do not promote; mixed scalar gain and built-in regression. |
| B | `notes/parallel/g4_grounded_low_receive_worker_b_screen.md` | `grounded_low_receive` structural probes | `glr_brace_no_jump` | screen `9000..9015` | `improved-v6` `1.5000` / `11-2-3` / `48000`, but built-in regressed to `0.2500` / `4-1-11` / `48000` | structural | Do not promote; one archived-opponent gain with built-in and W-L-D regressions. |
| C | `notes/parallel/g4_rear_wall_press_worker_c_20260527.md` | rear-wall branch probes | `rw_press_always_jump` | screen `9000..9015`; fixed pool `9000..9049` | built-in `0.1600` / `13-8-29` / `150000`, but fixed pool regressed most archived rows | structural | Do not promote; built-in-only signal failed fixed-pool robustness. |
| D | `reports/parallel/g4_trace_attack_vs_baseline_rnn_worker_d_20260527.md` | trace diagnostics | diagnostic only | `9000..9049` | `attack -0.3000`, `net-pressure -0.2200`, `baseline-rnn 0.1200` vs built-in | diagnostics | Do not promote `attack` or `net-pressure`; use stacked-frame low-receive hypothesis only. |
| E | `notes/parallel/g4_archived_opponent_robustness_post_contact_worker_e.md` | archived-opponent robustness | `post-contact` | fixed pool `9000..9049` | built-in `0.14` / `13-8-29`; hard tail `improved-v5 1.22`, `improved-v6 1.28`, both `32-7-11` | structural/history | Keep as development reference; do not promote to final/production claim. |

## Promotion Gate

The gate for this pass was:

1. Do not use holdout or audit seeds.
2. Do not promote a candidate from built-in opponent score alone.
3. Any candidate that beats `baseline-rnn` on built-in development seeds must
   pass the fixed development opponent pool before any holdout use.
4. Separate scalar/config gains from structural heuristic changes.
5. Make at most one maintained policy/config/test edit if evidence supports it.

No candidate clears the gate.

`rw_press_always_jump` beats both `rally_reference` and `baseline-rnn` on the
built-in development mean, but its fixed-pool check regresses `random`,
`initial`, `improved-v0`, `improved-v3`, `improved-v4`, `improved-v5`, and
`improved-v6`. It is therefore a diagnostic clue only.

`np_low_rescue_050` is the best scalar/config row in Worker A, but it keeps a
negative built-in score and remains below the neural comparator across the
fixed pool. It is not structural evidence.

`post-contact` remains the best current development reference among the
transparent history-aware candidates because it preserves the built-in row and
has small hard-tail archived gains over older `rally-serve` evidence. It still
does not close the hard archived-opponent gap to `baseline-rnn`, so it should
not be promoted as a final result or exposed to holdout/audit seeds from this
pass.

## Failure Analysis

The parallel pass repeats a consistent pattern: local current-frame action
changes can move one row, but they are not robust against the fixed opponent
pool.

The trace worker provides the clearest next diagnosis. `attack` and
`net-pressure` terminal losses are dominated by low own-side, contact-like
states. Recent velocity flips appear in most heuristic loss traces, but the
current attack/net-pressure family reacts mostly to the current frame. The RNN
wins many low left/net terminal states with `101` or `110`; the heuristic often
ends with movement-only actions. The missing rule is not "jump more" or
"pressure more." It is a selective stacked-frame classifier for post-contact
low-receive states.

Grounded-low and rear-wall workers show why the next branch must be narrow.
Aggressive low receive rewrites changed hundreds of actions and collapsed
screen rows. Rear-wall force-jump helped a narrow built-in trajectory but hurt
most archived opponents. The next useful edit should distinguish contact-like
history before choosing between suppression, recovery, and conversion.

## Decision

No maintained policy, config, or regression-test edit is evidence-supported by
this pass.

The next single edit, if a future pass pursues it, should be a new development
candidate rather than a promotion: a narrow stacked-frame post-contact
low-receive branch layered near `post-contact`, gated by recent `vx` sign flips,
`vy` upward flips, low own-side geometry, and agent posture. It should be
screened first on `9000..9015`, then checked against the fixed development
opponent pool on `9000..9049` before any holdout/audit use.

## Cost Accounting

Fresh environment-step cost was recorded in the worker artifacts rather than a
canonical ledger. Known high-level costs:

- Worker A ran 13 short built-in rows and six full fixed-pool candidates.
- Worker B ran five candidate/reference rows across three short-screen
  opponents.
- Worker C ran a short rear-wall screen, a full built-in check, and a fixed-pool
  check for the only built-in-improving branch.
- Worker D ran three full built-in trace rows with `trace_window=24`.
- Worker E ran nine full fixed-pool `post-contact` rows.

LLM/subagent token cost is not available from the local harness. All worker
outputs are preserved as auditable markdown artifacts.

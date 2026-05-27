# Generation-4 Parallel3 Synthesis

Date: 2026-05-27

## Scope

This report synthesizes the third parallel development-only worker pass for the SlimeVolley heuristic-learning experiment. Process check before launch found no active stale SlimeVolley, pytest, or evaluation processes from prior turns. Workers used only generation-4 development seeds: short screening subset `9000..9015` and full development range `9000..9049`.

No holdout seeds, audit seeds, or `slimevolley-final-eval` commands were used. No canonical ledger row was appended by the worker probes. The coordinator ran one extra no-ledger fixed-pool check for the scalar top candidate because it beat the built-in `baseline-rnn` comparator row.

## Worker Comparison

| Worker | Artifact | Family | Best candidate | Built-in full-dev mean / W-L-D / steps | Type | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `notes/parallel/20260527_g4_parallel3_attack_scalar.md` | Scalar/config search around `attack` and `rally-serve` | `low_rescue_x_0.50` | `0.1600` / `13-8-29` / `150000` | scalar/config | Do not promote as structural evidence; fixed-pool check required and now recorded below. |
| 2 | `notes/parallel/20260527_g4_parallel3_grounded_low_receive.md` | Stacked/history `grounded_low_receive` probes | several action-changing gates | `0.1400` / `13-8-29` / `150000` | structural/history | Do not promote; all checked candidates matched `rally-serve` across the fixed pool. |
| 3 | `notes/parallel/20260527_g4_parallel3_rear_wall_press.md` | Rear-wall branch probes | `rw_press_forcejump` | `0.1600` / `13-8-29` / `150000` | structural/history | Do not promote; fixed-pool rows regressed most archived opponents. |
| 4 | `reports/parallel/20260527_g4_parallel3_trace_attack_rnn.md` | Trace diagnostics | diagnostic only | `rally-serve 0.1400`, `baseline-rnn 0.1200`, `net-pressure -0.2200` | diagnostics | Use as hypothesis source only; broader net pressure is rejected. |
| 5 | `notes/parallel/20260527_g4_parallel3_archived_robustness.md` | Archived-opponent robustness | `post-contact` / `net-pressure` diagnostics | built-in edge does not survive fixed-pool neural comparison | robustness | Do not promote; every heuristic candidate trails `baseline-rnn` on archived opponents. |

## Coordinator Scalar Fixed-Pool Check

Worker 1 found a scalar-only built-in improvement: `low_ball_rescue_x_window=0.50` on top of `RALLY_SERVE_CONFIG`. Because this candidate beat `baseline-rnn` on the built-in development row, the coordinator ran a no-ledger fixed-pool check on the same full development seed range before making any recommendation.

Candidate definition:

- Policy family: `rally-serve`.
- Change type: scalar/config tuning.
- Delta: `low_ball_rescue_x_window=0.50` instead of the current `0.54`.
- Seeds: exactly `9000..9049`.
- No holdout/audit/final-eval use.

| Opponent | `low_rescue_x_0.50` mean | W-L-D | Steps | `rally-serve` mean | `baseline-rnn` mean |
| --- | ---: | --- | ---: | ---: | ---: |
| `builtin` | `0.16` | `13-8-29` | `150000` | `0.14` | `0.12` |
| `random` | `4.74` | `50-0-0` | `38164` | `4.74` | `4.80` |
| `initial` | `4.68` | `50-0-0` | `44662` | `4.68` | `4.76` |
| `improved-v0` | `4.70` | `50-0-0` | `43444` | `4.70` | `4.82` |
| `improved-v2` | `4.44` | `50-0-0` | `73608` | `4.38` | `4.80` |
| `improved-v3` | `2.94` | `48-1-1` | `139323` | `2.98` | `3.84` |
| `improved-v4` | `2.48` | `46-1-3` | `143928` | `2.34` | `3.26` |
| `improved-v5` | `1.24` | `34-6-10` | `149716` | `1.16` | `2.10` |
| `improved-v6` | `1.30` | `34-6-10` | `149716` | `1.22` | `2.18` |

This check used `932561` additional no-ledger development environment steps.

Interpretation:

- The scalar candidate improves mean score versus `rally-serve` on `builtin`, `improved-v2`, `improved-v4`, `improved-v5`, and `improved-v6`.
- It regresses `improved-v3` and adds one loss each on `improved-v3` and `improved-v4`.
- It remains below `baseline-rnn` on every archived opponent row.
- The improvement is entirely scalar/config tuning, not a structural heuristic learning result.

## Promotion Gate

The gate for this pass was:

1. Do not use holdout or audit seeds.
2. Do not promote a candidate from built-in opponent score alone.
3. Any candidate that beats `baseline-rnn` on built-in development seeds must be checked against the fixed development opponent pool before holdout use.
4. Separate scalar/config search from structural policy improvement.
5. Prefer one auditable edit only if the evidence supports it.

No candidate clears the gate as a maintained policy/config/test edit.

The scalar `low_rescue_x_0.50` candidate is the best numerical follow-up, but it is not promoted because it is scalar-only, still trails `baseline-rnn` across the archived pool, and introduces loss regressions on `improved-v3` and `improved-v4`. The structural `rw_press_forcejump` candidate is also rejected: it reaches the same built-in mean but regresses most archived-opponent rows. The grounded-low-receive history probes are rejected as outcome-neutral.

## Failure Analysis

The workers found several local signals but no robust structural improvement.

The scalar search shows that the low-ball rescue window is still a sensitive parameter. Narrowing it from `0.54` to `0.50` can slightly improve point differentials, especially against late archived heuristics, but the behavior does not close the neural-comparator gap. It also does not create a new interpretable state detector or controller.

The grounded-low-receive probes changed actions but did not move any fixed-pool score row. This is negative evidence for branch-local GLR edits: on these seeds, GLR frames are too sparse and too late to fix the main loss modes by themselves.

The rear-wall probes show that forcing jump inside `rear_wall_press` rescues a narrow built-in pattern, but the same intervention harms the archived pool. Broad post-bounce or approach-state replacements are too ambiguous and collapse quickly.

The trace worker explains why broader pressure is not enough. `net-pressure` nearly doubled `101` usage versus `rally-serve`, but it reopened low own-side failures and dropped built-in mean from `0.14` to `-0.22`. The gap to `baseline-rnn` is not simply jump more; it is deciding when a low/contact-like state should be converted with `101` versus recovered with movement.

## Cost Accounting

Known development-only environment-step cost from this pass:

| Source | Step accounting |
| --- | ---: |
| Worker 1 scalar/config search | `1,674,000` steps from 13 short built-in rows and 7 full built-in rows. |
| Worker 2 grounded-low-receive probes | `9,699,093` steps, reported by the worker artifact. |
| Worker 3 rear-wall probes | At least `1,782,000` screening/full-check steps plus fixed-pool rows reported in the artifact. |
| Worker 4 trace diagnostics | `600,000` steps from 4 full built-in rows. |
| Worker 5 robustness | Fresh `net-pressure` no-ledger rows plus existing generation-4 dev artifacts; exact fresh step total is in the worker note. |
| Coordinator scalar fixed-pool check | `932,561` steps. |

LLM/subagent token cost is not available from the local harness. All worker artifacts were written as auditable markdown notes or reports.

## Decision

No maintained policy, config, or test edit is evidence-supported by this pass. The single repository edit from synthesis is this append-only report plus the README manifest entry.

The next development-only direction, if continued, should be a structural history-aware low-contact classifier that acts before the final `grounded_low_receive` branch, not another broad net-pressure rule. It should explicitly distinguish:

- recent own-contact versus opponent-contact velocity flips,
- low own-side recovery versus front/net conversion,
- whether the agent is grounded or recovering from a jump,
- and whether `101` would produce a conversion or a second-touch/self-side loss.

That next idea remains a hypothesis. It is not current benchmark evidence, and it must use a fresh predeclared development protocol before any future holdout or audit use.

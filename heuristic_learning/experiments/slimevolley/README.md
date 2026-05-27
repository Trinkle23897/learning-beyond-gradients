# SlimeVolley Experiment

Environment ID: `SlimeVolley-v0`; artifact root: `experiments/slimevolley/`.

SlimeVolley is the first `custom_active` competitive-control environment for
the expanded heuristic-learning benchmark layout. The package registration lives
in `hl_benchmark/environments/slimevolley.py`; it is excluded from aggregate
`make eval-all` because it uses legacy Gym APIs plus a custom opponent protocol,
not because it is merely planned.

## Current Code Paths

- Policy code: `hl_benchmark/policies/slimevolley.py`
- Registered custom harness bridge: `hl_benchmark/custom_envs/slimevolley/`
- Implementation and compatibility package: `hl_benchmark/slimevolley/`
- Opponent protocol: `hl_benchmark/slimevolley/opponents.py`
- Legacy Gym adapter: `hl_benchmark/slimevolley/adapter.py`
- Environment diagnostics: `python -m hl_benchmark.custom_envs.slimevolley.doctor`
- Evaluation CLI: `python -m hl_benchmark.custom_envs.slimevolley.evaluate`
- Scalar-search CLI: `python -m hl_benchmark.custom_envs.slimevolley.search`
- Round-robin CLI: `python -m hl_benchmark.custom_envs.slimevolley.tournament`
- Final holdout CLI: `python -m hl_benchmark.custom_envs.slimevolley.final_eval`
- Artifacts: `experiments/slimevolley/results/`, `reports/`, `notes/`

## Upstream API Assumptions To Verify

The implementation follows the upstream `hardmaru/slimevolleygym` API shape:

- environment id: `SlimeVolley-v0`
- observation: 12 normalized floats for agent, ball, and opponent state
- action: `MultiBinary(3)` for forward, backward, and jump
- old Gym step API: `obs, reward, done, info`
- policy-vs-policy step API: `env.step(action, otherAction)`
- built-in baseline opponent: omit `otherAction`

Run `make slimevolley-doctor` after installing the optional dependencies to
record the exact local package versions and observed spaces. `make slimevolley-audit`
requires this `environment_diagnostics.json` artifact, validates its core
package/API fields, compares `summary.csv` content against the append-only
ledger, checks SlimeVolley rows for opponent, win/loss/draw, and
life-difference fields, and fails if scalar/config tuning appears on reserved
holdout or audit splits.

## Dependency Note

`slimevolleygym` depends on the legacy Gym stack. Modern pip/build isolation can
reject `gym==0.20.0` metadata, so use the setup sequence documented in the root
benchmark README before running real evaluations.

## Current Reproduction Commands

```bash
make slimevolley-doctor
make slimevolley-summary
make slimevolley-audit
make slimevolley-verify
make slimevolley-eval POLICY=improved OPPONENT=builtin SPLIT=dev
make slimevolley-search MAX_CANDIDATES=8
make slimevolley-tournament SPLIT=dev
make slimevolley-report
make slimevolley-performance-report
make slimevolley-generation-report
make slimevolley-generation3-report
make slimevolley-protocol
make slimevolley-generation3-protocol
make slimevolley-generation4-protocol
make slimevolley-critic ARGS="--dry-run"
# Final holdout commands are reproduction/audit only after holdout evidence exists.
make slimevolley-final-eval
```

For new ledger-producing runs, include test provenance when it is known:

```bash
make slimevolley-eval POLICY=improved OPPONENT=builtin SPLIT=dev ARGS="--tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass"
```

Use `--tests-pass-fail not_recorded` only when test status is genuinely
unavailable. Historical rows in this experiment predate explicit
`tests_pass_fail`; `results/trial_amendments.jsonl` records append-only
`tests_pass_fail=not_recorded` amendments keyed by row index and SHA256 hash.

`make slimevolley-verify` writes the latest machine-readable audit snapshot to
`results/audit_latest.json` with artifact/source SHA256 hashes, parsed `requirements_audit_rows`, `requirements_audit_status_counts`, `requirements_audit_partial_rows`, `requirements_audit_completion_state`, `requirements_audit_completion_recommendation`, `requirements_audit_partial_row_details`, and `requirements_audit_partial_row_classifications`.

## Artifact Manifest

| Artifact | Role | Produced or refreshed by | Verified by |
| --- | --- | --- | --- |
| `hl_benchmark/custom_envs/slimevolley/` | Registry-facing custom harness bridge that delegates to `hl_benchmark/slimevolley/`. | registration and Makefile targets | `make check-env ENV=SlimeVolley-v0` custom-harness import and entrypoint checks |
| `results/trials.jsonl` | Append-only SlimeVolley trial ledger, including failed rows. | evaluation/search/tournament/holdout commands | `make slimevolley-audit` |
| `results/trial_amendments.jsonl` | Append-only metadata amendments for historical generation-1 ledger rows. | `python -m hl_benchmark.slimevolley.amendments --ledger results/trials.jsonl` | `make slimevolley-audit` row-index, row-hash, and amended-field checks |
| `results/summary.csv` | Regenerated CSV projection of the amendment-aware effective ledger. | `make slimevolley-summary` or `make slimevolley-verify` | `make slimevolley-audit` field-by-field summary check |
| `results/environment_diagnostics.json` | Recorded package/API/runtime diagnostics for the legacy SlimeVolley stack. | `make slimevolley-doctor` | `make slimevolley-audit` diagnostics schema check |
| `results/search_best_dev.json` | Scalar/config-search selection artifact from development seeds only. | `make slimevolley-search` | `make slimevolley-audit` presence/hash check |
| `results/round_robin_dev.json` | Development-seed opponent-pool tournament artifact. | `make slimevolley-tournament SPLIT=dev` | `make slimevolley-audit` presence/hash check |
| `results/holdout_final.json` | Generation-1 final-only holdout matrix over frozen policies and opponents. | `make slimevolley-final-eval` once per experiment generation | `make slimevolley-audit` seed/matrix/anti-tuning checks |
| `configs/generation_2_protocol.json` | Predeclared generation-2 seed, ledger, opponent, and anti-tuning protocol. | `make slimevolley-protocol` or `make slimevolley-verify` | `make slimevolley-audit` seed-overlap, command, and guardrail checks |
| `results/generation_2_trials.jsonl` | Append-only generation-2 ledger for fresh development, scalar-search, tournament, and final-only holdout rows. | generation-2 evaluation/search/tournament/holdout commands in `generation_2_protocol.md` | `make slimevolley-audit` generation-2 ledger schema and seed-range checks |
| `results/generation_2_summary.csv` | Regenerated CSV projection of the generation-2 ledger. | generation-2 ledger-producing commands | `make slimevolley-audit` row-count/content checks |
| `results/search_best_g2_dev.json` | Generation-2 scalar/config-search selection artifact from development seeds only. | generation-2 scalar-search command in `generation_2_protocol.md` | `make slimevolley-audit` generation-2 search artifact checks |
| `results/round_robin_g2_dev.json` | Generation-2 development-seed opponent-pool tournament artifact. | generation-2 tournament command in `generation_2_protocol.md` | `make slimevolley-audit` generation-2 tournament checks |
| `results/holdout_g2_final.json` | Generation-2 final-only holdout matrix over frozen policies and opponents. | generation-2 final-holdout command in `generation_2_protocol.md` | `make slimevolley-audit` generation-2 anti-tuning and matrix checks |
| `results/audit_latest.json` | Latest machine-readable artifact audit snapshot, including artifact/source SHA256 hashes plus parsed requirement status rows. | `make slimevolley-verify` | inspect `pass_fail`, `issues`, `artifact_hashes`, `source_hashes`, `requirements_audit_status_counts`, `requirements_audit_partial_rows`, `requirements_audit_completion_state`, `requirements_audit_completion_recommendation`, `requirements_audit_partial_row_details`, and `requirements_audit_partial_row_classifications` |
| `reports/final_report.md` | Generated final report and conclusion, with generation-2 and generation-3 evidence when present. | `make slimevolley-report` or `make slimevolley-verify` | `make slimevolley-audit` required-section/hash checks |
| `reports/performance_deepdive.md` | Generated score-focused explanation using the latest final-only holdout generation as primary final evidence. | `make slimevolley-performance-report` or `make slimevolley-verify` | `make slimevolley-audit` required-section/snippet/hash checks |
| `reports/generation_2_diagnosis.md` | Generated diagnosis of generation-2 trial rows, failures, dependency state, costs, and holdout lock. | `make slimevolley-generation-report` or `make slimevolley-verify` | `make slimevolley-audit` required-section/snippet/hash checks |
| `reports/generation_2_protocol.md` | Human-readable generation-2 protocol for reviewer inspection. | `make slimevolley-protocol` or `make slimevolley-verify` | `make slimevolley-audit` required-section/snippet/hash checks |
| `configs/generation_3_protocol.json` | Predeclared generation-3 seed, ledger, opponent, and anti-tuning protocol. | `make slimevolley-generation3-protocol` | targeted protocol tests and reviewer inspection |
| `results/generation_3_trials.jsonl` | Append-only generation-3 ledger for development, scalar-search, tournament, and final-only holdout rows. | generation-3 commands in `generation_3_protocol.md` | `make slimevolley-audit` generation-3 ledger and seed-range checks |
| `results/generation_3_summary.csv` | Regenerated CSV projection of the generation-3 ledger. | generation-3 ledger-producing commands or `make slimevolley-verify` | `make slimevolley-audit` row-count/content checks |
| `results/search_best_g3_dev.json` | Generation-3 scalar/config-search selection artifact from development seeds only. | generation-3 scalar-search command in `generation_3_protocol.md` | `make slimevolley-audit` generation-3 search artifact checks |
| `results/round_robin_g3_dev.json` | Generation-3 development-seed opponent-pool tournament artifact. | generation-3 tournament command in `generation_3_protocol.md` | `make slimevolley-audit` generation-3 tournament checks |
| `results/holdout_g3_final.json` | Generation-3 final-only holdout matrix over frozen policies and opponents. | generation-3 final-holdout command in `generation_3_protocol.md` | `make slimevolley-audit` generation-3 anti-tuning and matrix checks |
| `reports/generation_3_diagnosis.md` | Generated diagnosis of generation-3 trial rows, dependency failures, costs, and final-only holdout status. | `make slimevolley-generation3-report` or `make slimevolley-verify` | targeted report tests and reviewer inspection |
| `reports/generation_3_protocol.md` | Human-readable generation-3 protocol for reviewer inspection and holdout guardrails. | `make slimevolley-generation3-protocol` | targeted protocol tests and reviewer inspection |
| `configs/generation_4_protocol.json` | Predeclared generation-4 seed, ledger, opponent, and anti-tuning protocol for any future SlimeVolley policy work. | `make slimevolley-generation4-protocol` or `make slimevolley-verify` | `make slimevolley-audit` seed-overlap, command, and guardrail checks |
| `reports/generation_4_protocol.md` | Human-readable generation-4 protocol for reviewer inspection before any future SlimeVolley tuning. | `make slimevolley-generation4-protocol` or `make slimevolley-verify` | `make slimevolley-audit` required-section/snippet/hash checks |
| `configs/generation_5_protocol.json` | Predeclared generation-5 seed, ledger, opponent, and anti-tuning protocol for post-generation-4 SlimeVolley work. | `make slimevolley-generation5-protocol` or `make slimevolley-verify` | targeted protocol tests and reviewer inspection |
| `reports/generation_5_protocol.md` | Human-readable generation-5 protocol for reviewer inspection before fresh post-generation-4 tuning. | `make slimevolley-generation5-protocol` or `make slimevolley-verify` | targeted protocol tests and reviewer inspection |
| `notes/generation_5_net_pressure_attempt.md` | Development-only note for the `net-pressure` structural probe, fixed seed results, and no-holdout promotion recommendation. | maintained with generation-5 dev-only evidence | reviewer inspection; no generation-5 holdout or audit opened |
| `notes/generation_5_fixed_pool_comparator.md` | Development-only fixed-pool comparator note for `net-pressure`, `baseline-rnn`, and `rally-serve` on generation-5 dev seeds. | maintained after generation-5 fixed-pool comparator rows | reviewer inspection; no generation-5 holdout or audit opened |
| `notes/generation_5_hard_opponent_trace_and_probe.md` | Development-only hard-opponent trace and failed/mixed front-net, brace-action, and contact-quality probe note for generation-5. | maintained after generation-5 hard-opponent diagnostics | reviewer inspection; no generation-5 holdout or audit opened |
| `notes/generation_5_post_contact_comparison.md` | Development-only post-contact transfer and net-post-contact combination note for generation-5; records ledgered fixed-pool rows and no-promotion decision. | maintained after generation-5 post-contact comparison rows | reviewer inspection; no generation-5 holdout or audit opened |
| `notes/generation_5_aggressive_pressure_and_brace_probe.md` | Development-only aggressive pressure, brace-serve, and conditional brace probe note for generation-5; records rejected broad jump/brace directions. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |
| `results/generation_4_trials.jsonl` | Append-only generation-4 ledger for development rows and final-only holdout rows. | generation-4 development and final-holdout commands | reviewer inspection, `reports/generation_4_temporal_history_attempt.md`, and `results/holdout_g4_final.json` |
| `results/generation_4_summary.csv` | CSV projection of the generation-4 ledger, including final-only holdout rows. | generation-4 ledger-producing commands | reviewer inspection |
| `results/holdout_g4_final.json` | Generation-4 final-only holdout matrix over frozen policies, including `rally-serve` and `baseline-rnn`. | `make slimevolley-final-eval` after policy/config/opponent/test freeze | reviewer inspection and `make slimevolley-audit` seed/matrix/anti-tuning checks |
| `reports/generation_4_temporal_history_attempt.md` | Development-only report for the stacked-history temporal candidate, failed sub-hypotheses, and paired controls. | maintained with generation-4 temporal evaluations | reviewer inspection; development-seed evidence only |
| `notes/generation_4_front_hit_suppression_attempt.md` | Development-only note for front-hit suppression, failed probes, and remaining neural comparator gap. | maintained with generation-4 development evidence | reviewer inspection; development-seed evidence only |
| `notes/generation_4_rear_wall_low_jump_attempt.md` | Development-only note for rear-wall low-jump rescue, failed/partial probes, and remaining neural comparator gap. | maintained with generation-4 development evidence | reviewer inspection; development-seed evidence only |
| `notes/generation_4_front_net_low_scoop_attempt.md` | Development-only note for the failed broad/narrow front-net scoop edits and rollback. | maintained with generation-4 development evidence | reviewer inspection; development-seed evidence only |
| `notes/generation_4_scalar_tuned_structural_attempt.md` | Development-only note for the `improved-tuned` scalar/config baseline and remaining neural comparator gap. | maintained with generation-4 scalar/config evidence | reviewer inspection; development-seed evidence only |
| `notes/generation_4_late_contact_attack_attempt.md` | Development-only note for the `attack` structural candidate, archived-opponent regressions, and remaining neural comparator gap. | maintained with generation-4 attack candidate evidence | reviewer inspection; development-seed evidence only |
| `notes/generation_4_joint_attack_scalar_search_attempt.md` | Development-only note for the failed/partial scalar search around `attack`; records the built-in-specific `-0.10` candidate and archived-opponent regressions. | maintained with generation-4 throwaway search evidence | reviewer inspection; development-seed evidence only |
| `notes/generation_4_low_receive_teacher_scalar_followup.md` | Development-only note for the failed teacher-action low-receive structural probes and bounded scalar/config follow-up search. | maintained with generation-4 dev-only follow-up evidence | reviewer inspection; development-seed evidence only |
| `notes/generation_4_rally_serve_candidate.md` | Development-only note for the rally-serve structural candidate that beat baseline-rnn on built-in development seeds before failing to beat it on final-only holdout. | maintained with generation-4 dev-only candidate evidence | reviewer inspection plus `results/holdout_g4_final.json` |
| `notes/parallel/` | Development-only parallel worker notes for scalar search, grounded-low-receive probes, rear-wall probes, and robustness checks. | parallel worker runs on generation-4 dev seeds only | reviewer inspection; development-seed evidence only |
| `reports/parallel/parallel_synthesis.md` | Synthesis report comparing parallel worker results and recording the no-promotion decision. | maintained after parallel worker completion | reviewer inspection; development-seed evidence only |
| `reports/parallel/20260527_parallel_synthesis_rallyserve.md` | Dated synthesis of the rally-serve parallel worker pass; records tied/regressed candidates and the no-promotion decision. | maintained after 2026-05-27 parallel worker completion | reviewer inspection; development-seed evidence only |
| `reports/parallel/20260527_trace_rally_attack_rnn_worker.md` | Dated development-only trace comparison for `rally-serve`, `attack`, and `baseline-rnn`. | parallel trace diagnostics worker on generation-4 dev seeds | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_attack_scalar_subagent_v2.md` | Development-only v2 scalar/config probe around `rally-serve`; records tied built-in variants, incomplete/mixed fixed-pool rows, and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_grounded_low_receive_subagent_v2.md` | Development-only v2 stacked-frame grounded-low-receive probe; records a tie with `rally-serve` and rejects broad low-incoming modes. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_rear_wall_press_subagent_v2.md` | Development-only v2 rear-wall press probe; records harmful/tied wall-clear variants and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_archived_robustness_subagent_v2.md` | Development-only v2 archived-opponent robustness note; records interrupted rerun and canonical fixed-pool regression versus `baseline-rnn`. | no-ledger generation-4 dev diagnostics plus existing summary rows | reviewer inspection; development-seed evidence only |
| `reports/parallel/20260527_g4_trace_attack_vs_rnn_subagent_v2.md` | Development-only v2 attack/rally-serve/RNN trace report on `9000..9015`. | no-ledger generation-4 trace diagnostics | reviewer inspection; development-seed evidence only |
| `reports/parallel/20260527_g4_parallel_subagent_synthesis_v2.md` | Development-only v2 synthesis of scalar, structural, trace, and robustness subagent artifacts; records no promotion decision. | maintained after 2026-05-27 v2 parallel worker completion | reviewer inspection; development-seed evidence only |
| `probes/g4_post_contact_gate_probe.py` | Development-only post-contact gate probe script for temporary structural/history candidates around `rally-serve`. | manual no-ledger generation-4 dev probe | reviewer inspection; development-seed evidence only |
| `results/generation_4_post_contact_gate_probe.json` | JSON results for the development-only post-contact gate probe; records screen and full fixed-pool rows with no promotion. | `python experiments/slimevolley/probes/g4_post_contact_gate_probe.py --phase screen/full` | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_post_contact_gate_probe.md` | Development-only post-contact gate probe note; records short-screen and fixed-pool results plus the no-promotion decision. | maintained after 2026-05-27 post-contact probe completion | reviewer inspection; development-seed evidence only |
| `notes/generation_4_post_contact_front_conversion_attempt.md` | Development-only structural candidate note for registered `post-contact`; records the explicit code/test edit, small archived gains, remaining RNN gap, and no final claim. | maintained after 2026-05-27 post-contact candidate registration | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_parallel3_attack_scalar.md` | Development-only parallel3 scalar/config search around `rally-serve`; records built-in-only ties/small same-W-L-D gains and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_parallel3_grounded_low_receive.md` | Development-only parallel3 grounded-low-receive history probe; records action-changing ties, fixed-pool no-gain results, and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_parallel3_rear_wall_press.md` | Development-only parallel3 rear-wall structural probe; records narrow built-in gain, fixed-pool regressions, and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `reports/parallel/20260527_g4_parallel3_trace_attack_rnn.md` | Development-only parallel3 trace diagnostics comparing `attack`, `rally-serve`, `net-pressure`, and `baseline-rnn` on generation-4 dev seeds. | no-ledger generation-4 trace diagnostics | reviewer inspection; development-seed evidence only |
| `results/generation_4_net_pressure_noledger_probe.json` | JSON rows for the development-only generation-4 `net-pressure` fixed-pool no-ledger probe. | no-ledger generation-4 dev robustness probe | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_net_pressure_fixed_pool_noledger.md` | Development-only generation-4 `net-pressure` fixed-pool note; records built-in regression and no promotion. | maintained after no-ledger generation-4 dev robustness probe | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_parallel3_archived_robustness.md` | Development-only parallel3 archived-opponent robustness note; compares `rally-serve`, `post-contact`, `net-pressure`, and `baseline-rnn` and records no promotion. | maintained after no-ledger generation-4 dev robustness probe | reviewer inspection; development-seed evidence only |
| `reports/parallel/20260527_g4_parallel3_synthesis.md` | Development-only parallel3 synthesis of scalar, structural, trace, robustness, and coordinator fixed-pool checks; records the no-promotion decision. | maintained after 2026-05-27 parallel3 worker completion | reviewer inspection; development-seed evidence only |
| `reports/critic/` and `.omx/artifacts/` | Optional Claude Code CLI critic artifacts containing prompt, raw output, metadata, source hashes, and advisory next-step suggestions. | `make slimevolley-critic ARGS="--allow-external-claude"` or offline mock/dry-run commands | reviewer inspection; advisory only, not benchmark evidence |
| `reports/requirements_audit.md` | Requirement-by-requirement coverage matrix for reviewer traceability. | maintained with SlimeVolley experiment changes | `make slimevolley-audit` required-section/snippet/hash checks |
| `notes/generation_3_start.md` | Human-readable note for the first generation-3 dependency failure and corrected development diagnostic. | maintained with generation-3 setup changes | reviewer inspection |
| `notes/generation_3_rear_wall_recovery_attempt.md` | Failure note for the rolled-back rear-wall recovery structural attempt. | maintained with generation-3 policy iterations | reviewer inspection |
| `notes/generation_3_delayed_low_receive_attempt.md` | Failure note for the rolled-back delayed low receive structural attempt. | maintained with generation-3 policy iterations | reviewer inspection |
| `notes/generation_3_rally_restart_serve_attempt.md` | Failure note for the rolled-back rally restart serve structural attempt. | maintained with generation-3 policy iterations | reviewer inspection |
| `notes/generation_3_rear_wall_press_attempt.md` | Note for the kept rear-wall press structural improvement. | maintained with generation-3 policy iterations | reviewer inspection |
| `notes/generation_3_freeze_before_holdout.md` | Freeze note declaring policy/config/opponent/test state before generation-3 final holdout. | maintained before generation-3 final holdout | reviewer inspection |

## Current Guardrails

1. Holdout seeds `1000..1049`, generation-2 holdout seeds `4000..4049`, generation-3 holdout seeds `7000..7049`, and generation-4 holdout seeds `10000..10049` have already been evaluated as final-only evidence.
2. Do not tune SlimeVolley policies, scalar configs, tests, or opponent pools against any consumed holdout range.
3. Generation-3 audit seeds `8000..8049` and generation-4 audit seeds `11000..11049` remain reserved. Generation-5 is predeclared for future work with development seeds `12000..12049`, holdout seeds `13000..13049`, and audit seeds `14000..14049`; do not use generation-5 holdout or audit before a new policy/config/opponent/test freeze.
4. Keep `status="custom_active"` unless SlimeVolley is migrated into a generic Gymnasium-compatible evaluator.
5. Preserve archived opponents before adding future structural policy versions.

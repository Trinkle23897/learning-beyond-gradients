# SlimeVolley Heuristic Learning Report

## Status

- Environment id: `SlimeVolley-v0`
- Environment availability: `available`
- Ledger: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/trials.jsonl`
- Summary CSV: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/summary.csv`
- Registration status: `custom_active`; custom SlimeVolley commands are active, while aggregate `eval-all` remains limited to generic Gymnasium-style environments.
- Custom module root: `hl_benchmark.custom_envs.slimevolley`; this bridge delegates to `hl_benchmark.slimevolley` for implementation compatibility.

## Dependency Versions

Versions prefer the latest ledger `runtime_metadata.packages` snapshot, with `environment_diagnostics.json` overriding the SlimeVolley-specific package probes when available. This avoids rewriting the recorded environment stack when the report is regenerated with a different Python interpreter.

- Box2D: `2.3.10`
- box2d-py: `not_installed`
- gym: `0.20.0`
- gymnasium: `1.3.0`
- numpy: `1.26.4`
- opencv-python: `4.11.0.86`
- pandas: `2.3.3`
- pygame: `not_installed`
- pygame-ce: `2.5.7`
- pytest: `9.0.3`
- slimevolleygym: `0.1.0`
- stable-baselines3: `not_installed`
- swig: `4.4.1`
- torch: `not_installed`

## Runtime Metadata

Runtime metadata is taken from the latest ledger row, not from the current report-generation process.

- Python: `3.10.20 (main, Mar  3 2026, 14:59:16) [Clang 21.1.4 ]`
- Platform: `Linux-6.11.0-25-generic-x86_64-with-glibc2.39`
- Package snapshot: recorded in the dependency table above.

## Environment Diagnostics

- Message: available
- Observation space: `Box([-3.403e+38 -3.403e+38 -3.403e+38 -3.403e+38 -3.403e+38 -3.403e+38 -3.403e+38 -3.403e+38 -3.403e+38 -3.403e+38 -3.403e+38 -3.403e+38], [3.403e+38 3.403e+38 3.403e+38 3.403e+38 3.403e+38 3.403e+38 3.403e+38 3.403e+38 3.403e+38 3.403e+38 3.403e+38 3.403e+38], (12,), float32)`
- Action space: `MultiBinary(3)`
- Step API: `legacy Gym: obs, reward, done, info; multi-agent step(action, otherAction)`
- Observed step API: `legacy-4-tuple`
- Observed multi-agent step API: `legacy-4-tuple`
- Seed API behavior: env.seed(seed) before reset; reset(seed=seed) if accepted, otherwise reset()
- Same-seed reset observation match: `True`
- Reward semantics: +1 when opponent loses a life, -1 when agent loses a life, episode ends at 5 lives or 3000 steps.

## Reproduction Commands

Run commands from `heuristic_learning/`. The holdout command is listed for reproduction/audit only; do not rerun it for policy tuning after holdout evidence exists.

```bash
make check-env ENV=SlimeVolley-v0
make check-promotion ENV=SlimeVolley-v0
make check-promotions
make check-envs
make check-env-layout
make custom-run ENV=SlimeVolley-v0
make custom-verify ENV=SlimeVolley-v0
make slimevolley-doctor
make slimevolley-summary
make slimevolley-contact-diagnostics
make slimevolley-critic ARGS="--dry-run"
make slimevolley-audit
make slimevolley-verify
make slimevolley-report
make slimevolley-performance-report
make slimevolley-generation-report
make slimevolley-generation3-report
make slimevolley-protocol
make slimevolley-generation3-protocol
make slimevolley-generation4-protocol
make slimevolley-eval POLICY=improved OPPONENT=builtin SPLIT=dev
make slimevolley-search MAX_CANDIDATES=8
make slimevolley-tournament SPLIT=dev
make slimevolley-final-eval
```

For new ledger-producing SlimeVolley runs, include test provenance when it is known:

```bash
make slimevolley-eval POLICY=improved OPPONENT=builtin SPLIT=dev ARGS="--tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass"
```

Use `--tests-pass-fail not_recorded` only when test status is genuinely unavailable. Historical rows in this experiment predate explicit `tests_pass_fail`; `results/trial_amendments.jsonl` preserves append-only amendments keyed by row index and SHA256 hash instead of rewriting those trial rows.

For machine-readable checks, use `make check-env ENV=SlimeVolley-v0 ARGS="--format json"`, `make check-promotion ENV=SlimeVolley-v0 ARGS="--format json"`, `make check-promotions ARGS="--format json"`, `make check-envs ARGS="--format json"`, `make custom-run ENV=SlimeVolley-v0 ARGS="--format json"`, `make slimevolley-audit ARGS="--format json"`, and `make slimevolley-summary ARGS="--format json"`. `make slimevolley-verify` also writes `results/audit_latest.json` with artifact/source SHA256 hashes, parsed `requirements_audit_rows`, `requirements_audit_status_counts`, `requirements_audit_partial_rows`, `requirements_audit_completion_state`, `requirements_audit_completion_recommendation`, `requirements_audit_partial_row_details`, and `requirements_audit_partial_row_classifications`.

## Artifact Integrity Checks

`make slimevolley-audit` is the canonical artifact-integrity gate for this custom environment.

It checks:

- ledger schema plus SlimeVolley-specific opponent, win/loss/draw, life-difference, action-frequency, numeric-cost, and failed-row failure-analysis fields,
- `summary.csv` row count and field-by-field content against the append-only ledger,
- `environment_diagnostics.json` package/API fields plus seed-reset and native step-API probes,
- diagnostics availability remains consistent with successful development or holdout evidence,
- scalar/config tuning rows never use reserved `holdout` or `audit` splits,
- `search_best_dev.json` uses the development split and contains environment, config, opponent mean, selection-score, known-opponent, and one-based candidate-budget fields,
- `round_robin_dev.json` uses the development split and contains a complete known-policy participant matrix, standings table, and win/loss/draw episode totals,
- holdout rows, when present, use exactly `1000..1049` and one episode per seed,
- holdout ledger rows are marked as final SlimeVolley holdout matchups with an explicit anti-tuning next hypothesis,
- ledger rows at or after `2026-05-25T00:00:00+00:00` include explicit `tests_pass_fail`; older generation-1 rows are covered by append-only metadata amendments that record `tests_pass_fail=not_recorded`,
- the holdout artifact policy/opponent matrix matches the holdout ledger rows,
- `configs/generation_2_protocol.json` predeclares fresh generation-2 development, holdout, and audit seeds that do not overlap generation-1 seeds,
- `reports/generation_2_protocol.md` exposes the same guardrails and commands for reviewer inspection,
- `reports/generation_2_diagnosis.md` exposes generation-2 trial-row status, failures, dependency state, costs, and the holdout lock,
- generation-2 ledger rows use only predeclared generation-2 split seeds and are checked independently from generation-1 rows,
- `search_best_g2_dev.json` and `round_robin_g2_dev.json` are cross-checked against the generation-2 ledger timestamps and cell contents,
- `holdout_g2_final.json`, when present, is checked as final-only generation-2 holdout evidence with anti-tuning metadata,
- `configs/generation_3_protocol.json` and `reports/generation_3_protocol.md` predeclare generation-3 development, holdout, and audit seeds,
- `reports/generation_3_diagnosis.md` exposes generation-3 trial-row status, dependency failures, costs, and final-only holdout status,
- `configs/generation_4_protocol.json` and `reports/generation_4_protocol.md` are the predeclared generation-4 protocol artifacts: development seeds `9000..9049`, holdout seeds `10000..10049`, and audit seeds `11000..11049` for any future SlimeVolley policy work,
- the persisted audit snapshot records SHA256 hashes for checked artifacts and SlimeVolley source files.

Audit seeds `2000..2049` remain reserved for future independent checks.
Holdout rows are already present, so future policy edits must use a fresh predeclared experiment generation instead of reusing these final seeds.

## Artifact Manifest

| Artifact | Role | Produced or refreshed by | Verified by |
| --- | --- | --- | --- |
| `hl_benchmark/custom_envs/slimevolley/` | Registry-facing custom harness bridge; delegates to `hl_benchmark/slimevolley/` for the established implementation. | registration and Makefile targets | `make check-env ENV=SlimeVolley-v0` custom-harness import and entrypoint checks |
| `results/trials.jsonl` | Append-only SlimeVolley trial ledger, including failed rows. | evaluation/search/tournament/holdout commands | `make slimevolley-audit` |
| `results/trial_amendments.jsonl` | Append-only metadata amendments for historical generation-1 ledger rows. | `python -m hl_benchmark.slimevolley.amendments --ledger results/trials.jsonl` | audit checks row indexes, entry SHA256 hashes, and amended `tests_pass_fail` values |
| `results/summary.csv` | Regenerated CSV projection of the ledger. | `make slimevolley-summary` or `make slimevolley-verify` | `make slimevolley-audit` field-by-field summary check |
| `results/environment_diagnostics.json` | Recorded package/API/runtime diagnostics for the legacy SlimeVolley stack. | `make slimevolley-doctor` | `make slimevolley-audit` diagnostics schema check |
| `results/search_best_dev.json` | Scalar/config-search selection artifact from development seeds only. | `make slimevolley-search` | `make slimevolley-audit` schema, split, presence, and hash check |
| `results/round_robin_dev.json` | Development-seed opponent-pool tournament artifact. | `make slimevolley-tournament SPLIT=dev` | `make slimevolley-audit` schema, split, matrix, standings, and hash check |
| `results/holdout_final.json` | Final-only holdout matrix over frozen policies and opponents. | `make slimevolley-final-eval` once per experiment generation | `make slimevolley-audit` seed/matrix/anti-tuning checks |
| `results/audit_latest.json` | Latest machine-readable artifact audit snapshot, including artifact/source SHA256 hashes plus parsed requirement status rows. | `make slimevolley-verify` | inspect `pass_fail`, `issues`, `artifact_hashes`, `source_hashes`, `requirements_audit_status_counts`, `requirements_audit_partial_rows`, `requirements_audit_completion_state`, `requirements_audit_completion_recommendation`, `requirements_audit_partial_row_details`, and `requirements_audit_partial_row_classifications` |
| `configs/generation_2_protocol.json` | Predeclared fresh SlimeVolley generation-2 seed, ledger, opponent, and anti-tuning protocol. | `make slimevolley-protocol` or `make slimevolley-verify` | `make slimevolley-audit` seed-overlap, command, guardrail, and hash checks |
| `results/generation_2_trials.jsonl` | Append-only generation-2 ledger for fresh development, scalar-search, tournament, and final-only holdout rows. | generation-2 evaluation/search/tournament/holdout commands | `make slimevolley-audit` generation-2 ledger schema, seed-range, and hash checks |
| `results/generation_2_summary.csv` | Regenerated CSV projection of the generation-2 ledger. | generation-2 ledger-producing commands | `make slimevolley-audit` generation-2 summary row-count/content/hash checks |
| `results/search_best_g2_dev.json` | Generation-2 scalar/config-search selection artifact from development seeds only. | generation-2 scalar-search command in `generation_2_protocol.md` | `make slimevolley-audit` generation-2 search artifact checks |
| `results/round_robin_g2_dev.json` | Generation-2 development-seed opponent-pool tournament artifact. | generation-2 tournament command in `generation_2_protocol.md` | `make slimevolley-audit` generation-2 tournament matrix/content/hash checks |
| `results/holdout_g2_final.json` | Generation-2 final-only holdout matrix once policy/config/opponent pool are frozen. | generation-2 final holdout command in `generation_2_protocol.md` | `make slimevolley-audit` generation-2 holdout anti-tuning and matrix checks when present |
| `reports/final_report.md` | Generated final report and conclusion. | `make slimevolley-report` or `make slimevolley-verify` | `make slimevolley-audit` required-section/hash checks |
| `reports/performance_deepdive.md` | Generated performance-focused explanation of current SlimeVolley scores. | `make slimevolley-performance-report` or `make slimevolley-verify` | `make slimevolley-audit` required-section/hash checks |
| `reports/generation_2_diagnosis.md` | Generated diagnosis of generation-2 trial rows, failures, dependency state, costs, and holdout lock. | `make slimevolley-generation-report` or `make slimevolley-verify` | `make slimevolley-audit` required-section/snippet/hash checks |
| `reports/generation_2_protocol.md` | Human-readable generation-2 protocol for reviewers. | `make slimevolley-protocol` or `make slimevolley-verify` | `make slimevolley-audit` required-section/snippet/hash checks |
| `configs/generation_3_protocol.json` | Predeclared generation-3 seed, ledger, opponent, and anti-tuning protocol. | `make slimevolley-generation3-protocol` or `make slimevolley-verify` | targeted protocol tests and reviewer inspection |
| `results/generation_3_trials.jsonl` | Append-only generation-3 ledger for fresh development rows after generation-2 holdout consumption. | generation-3 development/search/tournament/holdout commands in `generation_3_protocol.md` | targeted report tests and reviewer inspection |
| `results/generation_3_summary.csv` | Regenerated CSV projection of the generation-3 ledger. | generation-3 ledger-producing commands | targeted report tests and reviewer inspection |
| `results/contact_diagnostics_g3_dev.json` | Machine-readable contact/return diagnostic summary from generation-3 development traces only. | `make slimevolley-contact-diagnostics` or `make slimevolley-verify` | report/audit manifest checks and reviewer inspection |
| `reports/contact_diagnostics_g3_dev.md` | Markdown contact/return diagnostic report for generation-3 development traces. | `make slimevolley-contact-diagnostics` or `make slimevolley-verify` | report/audit manifest checks and reviewer inspection |
| `reports/generation_3_diagnosis.md` | Generated diagnosis of generation-3 trial rows, dependency failures, costs, and holdout lock. | `make slimevolley-generation3-report` or `make slimevolley-verify` | targeted report tests and reviewer inspection |
| `reports/generation_3_protocol.md` | Human-readable generation-3 protocol for reviewers and final-only holdout guardrails. | `make slimevolley-generation3-protocol` or `make slimevolley-verify` | targeted protocol tests and reviewer inspection |
| `configs/generation_4_protocol.json` | Predeclared generation-4 seed, ledger, opponent, and anti-tuning protocol for any future SlimeVolley policy work. | `make slimevolley-generation4-protocol` or `make slimevolley-verify` | `make slimevolley-audit` seed-overlap, command, guardrail, and hash checks |
| `reports/generation_4_protocol.md` | Human-readable generation-4 protocol for reviewers before any future SlimeVolley tuning. | `make slimevolley-generation4-protocol` or `make slimevolley-verify` | `make slimevolley-audit` required-section/snippet/hash checks |
| `configs/generation_5_protocol.json` | Predeclared generation-5 seed, ledger, opponent, and anti-tuning protocol for post-generation-4 SlimeVolley work. | `make slimevolley-generation5-protocol` or `make slimevolley-verify` | targeted protocol tests and reviewer inspection |
| `reports/generation_5_protocol.md` | Human-readable generation-5 protocol for reviewers before fresh post-generation-4 tuning. | `make slimevolley-generation5-protocol` or `make slimevolley-verify` | targeted protocol tests and reviewer inspection |
| `notes/generation_5_net_pressure_attempt.md` | Development-only note for the `net-pressure` structural probe, fixed seed results, and no-holdout promotion recommendation. | maintained with generation-5 dev-only evidence | reviewer inspection; no generation-5 holdout or audit opened |
| `notes/generation_5_fixed_pool_comparator.md` | Development-only fixed-pool comparator note for `net-pressure`, `baseline-rnn`, and `rally-serve` on generation-5 dev seeds. | maintained after generation-5 fixed-pool comparator rows | reviewer inspection; no generation-5 holdout or audit opened |
| `notes/generation_5_hard_opponent_trace_and_probe.md` | Development-only hard-opponent trace and failed/mixed front-net, brace-action, and contact-quality probe note for generation-5. | maintained after generation-5 hard-opponent diagnostics | reviewer inspection; no generation-5 holdout or audit opened |
| `notes/generation_5_post_contact_comparison.md` | Development-only post-contact transfer and net-post-contact combination note for generation-5; records ledgered fixed-pool rows and no-promotion decision. | maintained after generation-5 post-contact comparison rows | reviewer inspection; no generation-5 holdout or audit opened |
| `notes/generation_5_aggressive_pressure_and_brace_probe.md` | Development-only aggressive pressure, brace-serve, and conditional brace probe note for generation-5; records rejected broad jump/brace directions. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |
| `notes/generation_5_stacked_followthrough_and_posture_probe.md` | Development-only stacked followthrough, front-low recovery, and opponent-posture gated pressure note for generation-5; records mixed/rejected no-ledger probes. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |
| `notes/generation_5_phase_pressure_probe.md` | Development-only phase-pressure note for generation-5; records mixed two-frame opponent-side pressure probes and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |
| `probes/g5_phase_pressure_probe.py` | Development-only phase-pressure probe script for temporary generation-5 structural/history candidates around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |
| `results/generation_5_phase_pressure_probe.json` | JSON results for the development-only phase-pressure probe; records screen and full fixed-pool rows with no promotion. | `python experiments/slimevolley/probes/g5_phase_pressure_probe.py --phase screen/full` | reviewer inspection; development-seed evidence only |
| `notes/generation_5_teacher_serve_probe.md` | Development-only teacher-serve macro note for generation-5; records archived short-screen gains, built-in regression, and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |
| `probes/g5_teacher_serve_probe.py` | Development-only teacher-serve macro probe script for fixed reset/serve candidates around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |
| `results/generation_5_teacher_serve_probe.json` | JSON results for the development-only teacher-serve macro probe; records short-screen rows and a full fixed-pool check for `serve_110_10`. | `python experiments/slimevolley/probes/g5_teacher_serve_probe.py --phase screen/full` | reviewer inspection; development-seed evidence only |
| `notes/generation_5_context_reset_probe.md` | Development-only context-reset macro note for generation-5; records an initially inert detector, corrected active previous-point reset classifier, mixed fixed-pool results, and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |
| `probes/g5_context_reset_probe.py` | Development-only context-conditioned reset macro probe script for previous-point reset macro candidates around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |
| `results/generation_5_context_reset_probe.json` | JSON results for the development-only context-reset probe; records failed no-op classifier screen, corrected screen, and full fixed-pool checks. | `python experiments/slimevolley/probes/g5_context_reset_probe.py --phase screen/full` | reviewer inspection; development-seed evidence only |
| `notes/generation_5_rally_setup_probe.md` | Development-only rally-setup note for generation-5; records failed post-contact front-anchor structural/history probes and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |
| `probes/g5_rally_setup_probe.py` | Development-only rally-setup probe script for post-own-contact front-anchor candidates around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |
| `results/generation_5_rally_setup_probe.json` | JSON results for the development-only rally-setup probe; records fixed short-screen rows on `12000..12015`. | `python experiments/slimevolley/probes/g5_rally_setup_probe.py --phase screen` | reviewer inspection; development-seed evidence only |
| `notes/generation_5_contact_timing_probe.md` | Development-only contact-timing note for generation-5; records low front-court trace diagnostics, no-op/tied jump override probes, and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |
| `probes/g5_contact_timing_probe.py` | Development-only contact-timing diagnostic/probe script for low front-court jump/contact candidates around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |
| `results/generation_5_contact_timing_probe.json` | JSON results for the development-only contact-timing diagnostic and short screen on `12000..12015`. | `python experiments/slimevolley/probes/g5_contact_timing_probe.py --phase diagnose/screen` | reviewer inspection; development-seed evidence only |
| `notes/generation_5_approach_quality_probe.md` | Development-only approach-quality note for generation-5; records pre-contact trace diagnostics, harmful early-jump probes, mixed/no-op approach probes, and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |
| `probes/g5_approach_quality_probe.py` | Development-only approach-quality diagnostic/probe script for pre-contact movement and early jump candidates around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |
| `results/generation_5_approach_quality_probe.json` | JSON results for the development-only approach-quality diagnostic and short screen on `12000..12015`. | `python experiments/slimevolley/probes/g5_approach_quality_probe.py --phase diagnose/screen` | reviewer inspection; development-seed evidence only |
| `notes/generation_5_contact_quality_probe.md` | Development-only contact-quality note for generation-5; records recent-contact/descent/brace probes, hard-tail nudges with built-in regressions, and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |
| `probes/g5_contact_quality_probe.py` | Development-only contact-quality probe script for short-history pressure gates and RNN-like brace action candidates around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |
| `results/generation_5_contact_quality_probe.json` | JSON results for the development-only contact-quality short screen on `12000..12015`. | `python experiments/slimevolley/probes/g5_contact_quality_probe.py --phase screen` | reviewer inspection; development-seed evidence only |
| `notes/generation_5_position_posture_probe.md` | Development-only position/posture scalar-config note for generation-5; records front-shifted home-anchor probes, archived-row tradeoffs, and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |
| `probes/g5_position_posture_probe.py` | Development-only front-posture scalar/config probe script around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |
| `results/generation_5_position_posture_probe.json` | JSON results for the development-only position/posture short screen on `12000..12015`. | `python experiments/slimevolley/probes/g5_position_posture_probe.py --phase screen` | reviewer inspection; development-seed evidence only |
| `notes/generation_5_planner_takeover_probe.md` | Development-only planner-takeover structural note for generation-5; records harmful/inert transient planner delegation probes and no-promotion decision. | maintained after no-ledger generation-5 dev diagnostics | reviewer inspection; no generation-5 holdout or audit opened |
| `probes/g5_planner_takeover_probe.py` | Development-only transient planner-takeover probe script around `net-pressure`. | manual no-ledger generation-5 dev probe | reviewer inspection; development-seed evidence only |
| `results/generation_5_planner_takeover_probe.json` | JSON results for the development-only planner-takeover short screen on `12000..12015`. | `python experiments/slimevolley/probes/g5_planner_takeover_probe.py --phase screen` | reviewer inspection; development-seed evidence only |
| `results/generation_4_trials.jsonl` | Append-only generation-4 ledger for development rows and final-only holdout rows. | generation-4 development and final holdout commands | reviewer inspection, `reports/generation_4_temporal_history_attempt.md`, and `results/holdout_g4_final.json` |
| `results/generation_4_summary.csv` | CSV projection of the generation-4 ledger, including final-only holdout rows when present. | generation-4 ledger-producing commands | reviewer inspection |
| `results/holdout_g4_final.json` | Generation-4 final-only holdout matrix over frozen policies, including `rally-serve` and `baseline-rnn`. | `make slimevolley-final-eval` after policy/config/opponent/test freeze | reviewer inspection and `make slimevolley-audit` seed/matrix/anti-tuning checks |
| `reports/generation_4_temporal_history_attempt.md` | Development-only report for the stacked-history temporal candidate, including failed sub-hypotheses and paired controls. | maintained with generation-4 temporal evaluations | reviewer inspection; development-seed evidence only |
| `notes/generation_4_scalar_tuned_structural_attempt.md` | Development-only note for the `improved-tuned` scalar/config baseline and remaining neural comparator gap. | maintained with generation-4 scalar/config evidence | reviewer inspection; development-seed evidence only |
| `notes/generation_4_late_contact_attack_attempt.md` | Development-only note for the `attack` structural candidate, archived-opponent regressions, and remaining neural comparator gap. | maintained with generation-4 attack candidate evidence | reviewer inspection; development-seed evidence only |
| `notes/generation_4_joint_attack_scalar_search_attempt.md` | Development-only note for the failed/partial scalar search around `attack`; records the built-in-specific `-0.10` candidate and archived-opponent regressions. | maintained with generation-4 throwaway search evidence | reviewer inspection; development-seed evidence only |
| `notes/generation_4_low_receive_teacher_scalar_followup.md` | Development-only note for the failed teacher-action low-receive structural probes and bounded scalar/config follow-up search. | maintained with generation-4 dev-only follow-up evidence | reviewer inspection; development-seed evidence only |
| `notes/generation_4_rally_serve_candidate.md` | Development-only note for the rally-serve structural candidate that beat baseline-rnn on built-in development seeds before failing to beat it on final-only holdout. | maintained with generation-4 dev-only candidate evidence | reviewer inspection plus `results/holdout_g4_final.json` |
| `notes/parallel/` | Development-only parallel worker notes for scalar search, grounded-low-receive probes, rear-wall probes, and robustness checks. | parallel worker runs on generation-4 dev seeds only | reviewer inspection; development-seed evidence only |
| `reports/parallel/parallel_synthesis.md` | Synthesis report comparing parallel worker results and recording the no-promotion decision. | maintained after parallel worker completion | reviewer inspection; development-seed evidence only |
| `reports/parallel/20260527_parallel_synthesis_rallyserve.md` | Dated synthesis of the rally-serve parallel worker pass; records that scalar/config, stacked low-receive, and rear-wall probes tied or regressed and no new candidate was promoted. | maintained after 2026-05-27 parallel worker completion | reviewer inspection; development-seed evidence only |
| `reports/parallel/20260527_trace_rally_attack_rnn_worker.md` | Dated development-only trace comparison of `rally-serve`, `attack`, and `baseline-rnn` against the built-in opponent. | parallel trace diagnostics worker on generation-4 dev seeds | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_attack_scalar_subagent_v2.md` | Development-only v2 scalar/config probe around `rally-serve`; records tied built-in variants, incomplete/mixed fixed-pool rows, and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `notes/parallel/g4_attack_scalar_worker_a_20260527.md` | Development-only Worker A scalar/config search around `attack`/`net-pressure`; records mixed fixed-pool scalar results and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_grounded_low_receive_subagent_v2.md` | Development-only v2 stacked-frame grounded-low-receive probe; records a tie with `rally-serve` and rejects broad low-incoming modes. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `notes/parallel/g4_grounded_low_receive_worker_b_screen.md` | Development-only Worker B grounded-low-receive short-screen note; records harmful/tied structural branch probes and no full-pool expansion. | no-ledger generation-4 short-screen diagnostics | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_rear_wall_press_subagent_v2.md` | Development-only v2 rear-wall press probe; records harmful/tied wall-clear variants and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `notes/parallel/g4_rear_wall_press_worker_c_20260527.md` | Development-only Worker C rear-wall press probe; records narrow built-in gain, fixed-pool regressions, and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_archived_robustness_subagent_v2.md` | Development-only v2 archived-opponent robustness note; records interrupted rerun and canonical fixed-pool regression versus `baseline-rnn`. | no-ledger generation-4 dev diagnostics plus existing summary rows | reviewer inspection; development-seed evidence only |
| `reports/parallel/20260527_g4_trace_attack_vs_rnn_subagent_v2.md` | Development-only v2 attack/rally-serve/RNN trace report on `9000..9015`. | no-ledger generation-4 trace diagnostics | reviewer inspection; development-seed evidence only |
| `reports/parallel/g4_trace_attack_vs_baseline_rnn_worker_d_20260527.md` | Development-only Worker D trace report comparing `attack`, `net-pressure`, and `baseline-rnn` on generation-4 dev seeds; records no promotion. | no-ledger generation-4 trace diagnostics | reviewer inspection; development-seed evidence only |
| `reports/parallel/20260527_g4_parallel4_synthesis.md` | Development-only Worker A-E synthesis report for generation-4 parallel4 diagnostics; records no maintained edit and no promotion. | maintained after 2026-05-27 parallel4 worker completion | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_parallel5_attack_scalar.md` | Development-only parallel5 attack scalar/config search; records a partial `attack` improvement that remained below `baseline-rnn` and `rally-serve`, with no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_parallel5_grounded_low_receive.md` | Development-only parallel5 grounded-low-receive screen; records action-changing ties and one built-in regression, with no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `results/generation_4_parallel5_grounded_low_receive_screen.json` | JSON rows for the development-only parallel5 grounded-low-receive screen on seeds `9000..9015`. | no-ledger generation-4 dev screen | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_parallel5_rear_wall_press.md` | Development-only parallel5 rear-wall press screen; records a narrow built-in tie, archived regressions, and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `results/generation_4_parallel5_rear_wall_press_probe.json` | JSON rows for the development-only parallel5 rear-wall press screen on seeds `9000..9015`. | no-ledger generation-4 dev screen | reviewer inspection; development-seed evidence only |
| `reports/parallel/20260527_g4_parallel5_trace_attack_rnn.md` | Development-only parallel5 trace diagnostic comparing `attack`, `rally-serve`, `post-contact`, and `baseline-rnn` on generation-4 dev seeds. | no-ledger generation-4 trace diagnostics | reviewer inspection; development-seed evidence only |
| `reports/parallel/20260527_g4_parallel5_synthesis.md` | Development-only parallel5 synthesis for grounded-low-receive, rear-wall, and trace diagnostics; records no maintained edit. | maintained after 2026-05-27 parallel5 worker completion | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_parallel6_attack_scalar.md` | Development-only parallel6 scalar/config search around `rally-serve`; records `low_x_0.52` as a fixed-pool-checked scalar candidate. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_parallel6_grounded_low_receive.md` | Development-only parallel6 grounded-low-receive structural/history probe; records fixed-pool ties and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_parallel6_rear_wall_press.md` | Development-only parallel6 rear-wall press probe; records small built-in gains, archived-opponent regressions, and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_parallel6_archived_robustness.md` | Development-only parallel6 archived-opponent robustness note comparing `rally-serve`, `post-contact`, `net-pressure`, `rw_press_forcejump`, and `baseline-rnn`. | no-ledger generation-4 dev robustness review | reviewer inspection; development-seed evidence only |
| `reports/parallel/20260527_g4_parallel6_trace_attack_rnn.md` | Development-only parallel6 trace diagnostic comparing `attack`, `rally-serve`, and `baseline-rnn` on generation-4 dev seeds. | no-ledger generation-4 trace diagnostics | reviewer inspection; development-seed evidence only |
| `reports/parallel/20260527_g4_parallel6_synthesis.md` | Development-only parallel6 synthesis; records the single supported edit as a named scalar/config candidate, not structural progress. | maintained after 2026-05-27 parallel6 worker completion | reviewer inspection; development-seed evidence only |
| `reports/parallel/20260527_g4_parallel_subagent_synthesis_v2.md` | Development-only v2 synthesis of scalar, structural, trace, and robustness subagent artifacts; records no promotion decision. | maintained after 2026-05-27 v2 parallel worker completion | reviewer inspection; development-seed evidence only |
| `probes/g4_post_contact_gate_probe.py` | Development-only post-contact gate probe script for temporary structural/history candidates around `rally-serve`. | manual no-ledger generation-4 dev probe | reviewer inspection; development-seed evidence only |
| `results/generation_4_post_contact_gate_probe.json` | JSON results for the development-only post-contact gate probe; records screen and full fixed-pool rows with no promotion. | `python experiments/slimevolley/probes/g4_post_contact_gate_probe.py --phase screen/full` | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_post_contact_gate_probe.md` | Development-only post-contact gate probe note; records short-screen and fixed-pool results plus the no-promotion decision. | maintained after 2026-05-27 post-contact probe completion | reviewer inspection; development-seed evidence only |
| `probes/g4_stacked_low_receive_probe.py` | Development-only stacked low-receive probe script for temporary structural/history candidates around `post-contact`. | manual no-ledger generation-4 dev probe | reviewer inspection; development-seed evidence only |
| `results/generation_4_stacked_low_receive_probe.json` | JSON results for the development-only stacked low-receive probe; records screen and full fixed-pool rows with no promotion. | `python experiments/slimevolley/probes/g4_stacked_low_receive_probe.py --phase screen/full` | reviewer inspection; development-seed evidence only |
| `notes/generation_4_stacked_low_receive_probe.md` | Development-only stacked low-receive probe note; records short-screen hard-tail gains, full-pool built-in regression, and no-promotion decision. | maintained after 2026-05-27 stacked low-receive probe completion | reviewer inspection; development-seed evidence only |
| `notes/parallel/g4_archived_opponent_robustness_post_contact_worker_e.md` | Development-only Worker E archived-opponent robustness note for `post-contact`; records fixed-pool rows and no final promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `notes/generation_4_post_contact_front_conversion_attempt.md` | Development-only post-contact front-conversion note; records small archived-opponent gains, registered development-only candidate, and no final claim. | maintained after 2026-05-27 post-contact probe and code registration | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_parallel3_attack_scalar.md` | Development-only parallel3 scalar/config search around `rally-serve`; records built-in-only ties/small same-W-L-D gains and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_parallel3_grounded_low_receive.md` | Development-only parallel3 grounded-low-receive history probe; records action-changing ties, fixed-pool no-gain results, and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_parallel3_rear_wall_press.md` | Development-only parallel3 rear-wall structural probe; records narrow built-in gain, fixed-pool regressions, and no promotion. | no-ledger generation-4 dev diagnostics | reviewer inspection; development-seed evidence only |
| `reports/parallel/20260527_g4_parallel3_trace_attack_rnn.md` | Development-only parallel3 trace diagnostics comparing `attack`, `rally-serve`, `net-pressure`, and `baseline-rnn` on generation-4 dev seeds. | no-ledger generation-4 trace diagnostics | reviewer inspection; development-seed evidence only |
| `results/generation_4_net_pressure_noledger_probe.json` | JSON rows for the development-only generation-4 `net-pressure` fixed-pool no-ledger probe. | no-ledger generation-4 dev robustness probe | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_net_pressure_fixed_pool_noledger.md` | Development-only generation-4 `net-pressure` fixed-pool note; records built-in regression and no promotion. | maintained after no-ledger generation-4 dev robustness probe | reviewer inspection; development-seed evidence only |
| `notes/parallel/20260527_g4_parallel3_archived_robustness.md` | Development-only parallel3 archived-opponent robustness note; compares `rally-serve`, `post-contact`, `net-pressure`, and `baseline-rnn` and records no promotion. | maintained after no-ledger generation-4 dev robustness probe | reviewer inspection; development-seed evidence only |
| `reports/critic/` and `.omx/artifacts/` | Optional Claude Code CLI critic artifacts, each containing prompt, raw output, hashes, and advisory next-step suggestions. | `make slimevolley-critic ARGS="--allow-external-claude"` or offline `--mock-output` runs | reviewer inspection; labeled external advisory context only |
| `notes/generation_3_start.md` | Human-readable note for the first generation-3 dependency failure and corrected development diagnostic. | maintained with generation-3 setup changes | reviewer inspection |
| `notes/generation_3_rear_wall_recovery_attempt.md` | Human-readable failure note for the rolled-back rear-wall recovery structural attempt. | maintained with generation-3 policy iterations | reviewer inspection |
| `notes/generation_3_delayed_low_receive_attempt.md` | Human-readable failure note for the rolled-back delayed low receive structural attempt. | maintained with generation-3 policy iterations | reviewer inspection |
| `notes/generation_3_rally_restart_serve_attempt.md` | Human-readable failure note for the rolled-back rally restart serve structural attempt. | maintained with generation-3 policy iterations | reviewer inspection |
| `notes/generation_3_rear_wall_press_attempt.md` | Human-readable note for the kept rear-wall press structural improvement. | maintained with generation-3 policy iterations | reviewer inspection |
| `notes/generation_3_freeze_before_holdout.md` | Human-readable freeze note declaring the generation-3 policy/config/opponent/test state before final holdout. | maintained before generation-3 final holdout | reviewer inspection |
| `reports/requirements_audit.md` | Requirement-by-requirement coverage matrix for reviewer traceability. | maintained with SlimeVolley experiment changes | `make slimevolley-audit` required-section/snippet/hash checks |

## Opponent Protocol

| Name | Version | Kind | Description |
| --- | --- | --- | --- |
| builtin | slimevolleygym-baseline-rnn | built-in baseline | Use the environment's default 120-parameter RNN baseline by omitting otherAction. |
| random | v0 | random policy | Seeded MultiBinary(3) random opponent. |
| initial | v0 | frozen heuristic | Frozen copy of the intentionally modest initial SlimeVolley heuristic. |
| improved-v0 | v0 | archived heuristic | Frozen first structural heuristic archive before low-ball-rescue was added. |
| improved-v1 | v1 | archived heuristic | Frozen structural heuristic archive before late-low-ball guard was added. |
| improved-v2 | v2 | archived heuristic | Frozen structural heuristic archive before grounded-low-receive was added. |
| improved-v3 | v3 | archived heuristic | Frozen structural heuristic archive before rear-wall recovery was added. |
| improved-v4 | v4 | archived heuristic | Frozen structural heuristic archive before front-hit jump suppression was added. |
| improved-v5 | v5 | archived heuristic | Frozen structural heuristic archive before rear-wall low-jump rescue was added. |
| improved-v6 | v6 | archived heuristic | Frozen structural heuristic archive before front-net low-scoop rescue was added. |
| improved | current | current heuristic | Current structural heuristic; useful for self-play and round-robin diagnostics, not a frozen archive. |
| improved-tuned | g4-scalar-tuned-v2 | scalar-tuned structural heuristic | Generation-4 scalar/config-tuned v2 of the current structural heuristic; not a structural archive. |
| attack | g4-late-contact-attack-candidate | structural heuristic candidate | Generation-4 late-contact attack candidate; partial evidence only and not promoted over improved-tuned v2. |
| rally-serve | g4-rally-serve-candidate | structural-plus-scalar heuristic candidate | Generation-4 rally-serve detector plus scalar-tuned attack candidate; beat baseline-rnn on built-in development seeds but failed to beat it on generation-4 built-in holdout. |
| post-contact | g4-post-contact-front-conversion-candidate | structural heuristic candidate | Generation-4 post-contact front-conversion candidate; development-only structural probe, not final evidence. |
| net-pressure | g5-net-pressure-candidate | structural heuristic candidate | Generation-5 front-court pressure candidate; development probe only, not promoted. |
| temporal | g4-candidate | temporal stacked-history heuristic | Generation-4 candidate heuristic using a short observation/action history for contact and trajectory features. |
| planner | g4-planner-candidate | physics-feature heuristic | Generation-4 pure planner candidate using time-to-floor, net-clearance, wall-bounce, and opponent-commitment features. |
| teacher-assisted | g4-teacher-assisted-candidate | teacher-assisted transparent heuristic | Generation-4 planner variant reserved for hand-audited rules suggested by baseline-rnn development traces; no RNN runtime calls. |
| baseline-rnn | slimevolleygym-baseline-rnn-wrapper | pretrained neural/RNN comparator | Use slimevolleygym's shipped 120-parameter RNN policy as an explicit comparator opponent. |

## Ledger Summary

Recorded SlimeVolley trials: 186

| Timestamp | Policy | Opponent | Split | Episodes | Mean | Wins | Losses | Draws | Win rate | Steps | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2026-05-24T18:29:25+00:00 | initial | builtin | smoke | 2 |  | 0 | 0 | 0 |  | 0 | fail |
| 2026-05-24T18:35:40+00:00 | initial | builtin | smoke | 2 | -5 | 0 | 2 | 0 | 0 | 1327 | pass |
| 2026-05-24T18:35:40+00:00 | initial | random | smoke | 2 | 2 | 1 | 1 | 0 | 0.5 | 1200 | pass |
| 2026-05-24T18:35:40+00:00 | initial | initial | smoke | 2 | 0 | 1 | 1 | 0 | 0.5 | 1605 | pass |
| 2026-05-24T18:35:40+00:00 | initial | improved-v0 | smoke | 2 | -0.5 | 1 | 1 | 0 | 0.5 | 1655 | pass |
| 2026-05-24T18:35:40+00:00 | improved | builtin | smoke | 2 | -5 | 0 | 2 | 0 | 0 | 1287 | pass |
| 2026-05-24T18:35:40+00:00 | improved | random | smoke | 2 | 2 | 1 | 1 | 0 | 0.5 | 1186 | pass |
| 2026-05-24T18:35:41+00:00 | improved | initial | smoke | 2 | 0 | 1 | 1 | 0 | 0.5 | 1612 | pass |
| 2026-05-24T18:35:41+00:00 | improved | improved-v0 | smoke | 2 | -0.5 | 1 | 1 | 0 | 0.5 | 1659 | pass |
| 2026-05-24T18:36:43+00:00 | random | builtin | dev | 20 | -4.9 | 0 | 20 | 0 | 0 | 11423 | pass |
| 2026-05-24T18:36:44+00:00 | random | random | dev | 20 | -0.15 | 10 | 10 | 0 | 0.5 | 12947 | pass |
| 2026-05-24T18:36:45+00:00 | random | initial | dev | 20 | -2.25 | 2 | 18 | 0 | 0.1 | 13848 | pass |
| 2026-05-24T18:36:46+00:00 | random | improved-v0 | dev | 20 | -2.5 | 1 | 19 | 0 | 0.05 | 13949 | pass |
| 2026-05-24T18:36:46+00:00 | initial | builtin | dev | 20 | -4.95 | 0 | 20 | 0 | 0 | 12914 | pass |
| 2026-05-24T18:36:47+00:00 | initial | random | dev | 20 | 1.9 | 16 | 4 | 0 | 0.8 | 13432 | pass |
| 2026-05-24T18:36:48+00:00 | initial | initial | dev | 20 | 0.25 | 11 | 9 | 0 | 0.55 | 16067 | pass |
| 2026-05-24T18:36:49+00:00 | initial | improved-v0 | dev | 20 | -0.15 | 8 | 12 | 0 | 0.4 | 16379 | pass |
| 2026-05-24T18:36:49+00:00 | improved | builtin | dev | 20 | -5 | 0 | 20 | 0 | 0 | 12799 | pass |
| 2026-05-24T18:36:50+00:00 | improved | random | dev | 20 | 1.6 | 13 | 7 | 0 | 0.65 | 13098 | pass |
| 2026-05-24T18:36:51+00:00 | improved | initial | dev | 20 | 0.4 | 11 | 9 | 0 | 0.55 | 15396 | pass |
| 2026-05-24T18:36:52+00:00 | improved | improved-v0 | dev | 20 | 0.25 | 10 | 10 | 0 | 0.5 | 15625 | pass |
| 2026-05-24T18:41:35+00:00 | random | builtin | dev | 20 | -4.85 | 0 | 20 | 0 | 0 | 11582 | pass |
| 2026-05-24T18:41:35+00:00 | initial | builtin | dev | 20 | -4.95 | 0 | 20 | 0 | 0 | 13159 | pass |
| 2026-05-24T18:41:36+00:00 | improved | builtin | dev | 20 | -5 | 0 | 20 | 0 | 0 | 13136 | pass |
| 2026-05-24T18:45:18+00:00 | tuned | builtin | dev | 20 | -4.95 | 0 | 20 | 0 | 0 | 14344 | pass |
| 2026-05-24T18:45:19+00:00 | tuned | random | dev | 20 | 2.75 | 19 | 1 | 0 | 0.95 | 13712 | pass |
| 2026-05-24T18:45:19+00:00 | tuned | initial | dev | 20 | 1.35 | 16 | 4 | 0 | 0.8 | 16289 | pass |
| 2026-05-24T18:45:20+00:00 | tuned | improved-v0 | dev | 20 | 1.2 | 15 | 5 | 0 | 0.75 | 17453 | pass |
| 2026-05-24T18:45:21+00:00 | tuned | builtin | dev | 20 | -4.95 | 0 | 20 | 0 | 0 | 13712 | pass |
| 2026-05-24T18:45:22+00:00 | tuned | random | dev | 20 | 2.35 | 18 | 2 | 0 | 0.9 | 13029 | pass |
| 2026-05-24T18:45:22+00:00 | tuned | initial | dev | 20 | 0.8 | 13 | 7 | 0 | 0.65 | 15344 | pass |
| 2026-05-24T18:45:23+00:00 | tuned | improved-v0 | dev | 20 | 0.8 | 13 | 7 | 0 | 0.65 | 16112 | pass |
| 2026-05-24T18:45:24+00:00 | tuned | builtin | dev | 20 | -4.95 | 0 | 20 | 0 | 0 | 13370 | pass |
| 2026-05-24T18:45:25+00:00 | tuned | random | dev | 20 | 1.65 | 16 | 4 | 0 | 0.8 | 14079 | pass |
| 2026-05-24T18:45:26+00:00 | tuned | initial | dev | 20 | 0.25 | 11 | 9 | 0 | 0.55 | 15777 | pass |
| 2026-05-24T18:45:26+00:00 | tuned | improved-v0 | dev | 20 | -0.25 | 8 | 12 | 0 | 0.4 | 16189 | pass |
| 2026-05-24T18:45:27+00:00 | tuned | builtin | dev | 20 | -4.95 | 0 | 20 | 0 | 0 | 14097 | pass |
| 2026-05-24T18:45:28+00:00 | tuned | random | dev | 20 | 2.45 | 17 | 3 | 0 | 0.85 | 13732 | pass |
| 2026-05-24T18:45:29+00:00 | tuned | initial | dev | 20 | 0.9 | 13 | 7 | 0 | 0.65 | 16389 | pass |
| 2026-05-24T18:45:29+00:00 | tuned | improved-v0 | dev | 20 | 0.7 | 12 | 8 | 0 | 0.6 | 17430 | pass |
| 2026-05-24T18:45:30+00:00 | tuned | builtin | dev | 20 | -4.95 | 0 | 20 | 0 | 0 | 13159 | pass |
| 2026-05-24T18:45:31+00:00 | tuned | random | dev | 20 | 1.9 | 16 | 4 | 0 | 0.8 | 13432 | pass |
| 2026-05-24T18:45:32+00:00 | tuned | initial | dev | 20 | 0.25 | 11 | 9 | 0 | 0.55 | 16067 | pass |
| 2026-05-24T18:45:32+00:00 | tuned | improved-v0 | dev | 20 | -0.15 | 8 | 12 | 0 | 0.4 | 16379 | pass |
| 2026-05-24T18:45:33+00:00 | tuned | builtin | dev | 20 | -4.95 | 0 | 20 | 0 | 0 | 12989 | pass |
| 2026-05-24T18:45:34+00:00 | tuned | random | dev | 20 | 1.55 | 15 | 5 | 0 | 0.75 | 13686 | pass |
| 2026-05-24T18:45:35+00:00 | tuned | initial | dev | 20 | 0 | 10 | 10 | 0 | 0.5 | 15709 | pass |
| 2026-05-24T18:45:35+00:00 | tuned | improved-v0 | dev | 20 | -0.7 | 6 | 14 | 0 | 0.3 | 16235 | pass |
| 2026-05-24T18:45:36+00:00 | tuned | builtin | dev | 20 | -4.95 | 0 | 20 | 0 | 0 | 14130 | pass |
| 2026-05-24T18:45:37+00:00 | tuned | random | dev | 20 | 2.45 | 17 | 3 | 0 | 0.85 | 13487 | pass |
| 2026-05-24T18:45:38+00:00 | tuned | initial | dev | 20 | 0.85 | 13 | 7 | 0 | 0.65 | 16057 | pass |
| 2026-05-24T18:45:38+00:00 | tuned | improved-v0 | dev | 20 | 0.6 | 12 | 8 | 0 | 0.6 | 17164 | pass |
| 2026-05-24T18:45:39+00:00 | tuned | builtin | dev | 20 | -4.9 | 0 | 20 | 0 | 0 | 13436 | pass |
| 2026-05-24T18:45:40+00:00 | tuned | random | dev | 20 | 2 | 16 | 4 | 0 | 0.8 | 13202 | pass |
| 2026-05-24T18:45:41+00:00 | tuned | initial | dev | 20 | 0.3 | 11 | 9 | 0 | 0.55 | 15831 | pass |
| 2026-05-24T18:45:41+00:00 | tuned | improved-v0 | dev | 20 | -0.15 | 8 | 12 | 0 | 0.4 | 16341 | pass |
| 2026-05-24T18:50:36+00:00 | improved | builtin | dev | 20 | -5 | 0 | 20 | 0 | 0 | 21625 | pass |
| 2026-05-24T18:50:37+00:00 | improved | random | dev | 20 | 3.1 | 18 | 2 | 0 | 0.9 | 13785 | pass |
| 2026-05-24T18:50:37+00:00 | improved | initial | dev | 20 | 2.7 | 18 | 2 | 0 | 0.9 | 15859 | pass |
| 2026-05-24T18:50:39+00:00 | improved | improved-v0 | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T18:51:49+00:00 | improved | improved-v0 | dev | 20 | 2.65 | 18 | 2 | 0 | 0.9 | 16270 | pass |
| 2026-05-24T18:51:50+00:00 | tuned | improved-v0 | dev | 20 | 1.2 | 15 | 5 | 0 | 0.75 | 17453 | pass |
| 2026-05-24T18:56:10+00:00 | improved | builtin | dev | 20 | -5 | 0 | 20 | 0 | 0 | 21625 | pass |
| 2026-05-24T18:58:54+00:00 | baseline-rnn | builtin | dev | 20 | -0.2 | 2 | 6 | 12 | 0.1 | 60000 | pass |
| 2026-05-24T18:58:55+00:00 | baseline-rnn | random | dev | 20 | 4.9 | 20 | 0 | 0 | 1 | 10717 | pass |
| 2026-05-24T18:58:55+00:00 | baseline-rnn | initial | dev | 20 | 4.85 | 20 | 0 | 0 | 1 | 12169 | pass |
| 2026-05-24T18:58:56+00:00 | baseline-rnn | improved-v0 | dev | 20 | 4.9 | 20 | 0 | 0 | 1 | 12761 | pass |
| 2026-05-24T19:15:16+00:00 | random | random | dev | 20 | -0.15 | 10 | 10 | 0 | 0.5 | 12947 | pass |
| 2026-05-24T19:15:16+00:00 | random | initial | dev | 20 | -2.25 | 2 | 18 | 0 | 0.1 | 13848 | pass |
| 2026-05-24T19:15:17+00:00 | random | improved-v0 | dev | 20 | -2.5 | 1 | 19 | 0 | 0.05 | 13949 | pass |
| 2026-05-24T19:15:18+00:00 | random | improved | dev | 20 | -2.9 | 1 | 19 | 0 | 0.05 | 14488 | pass |
| 2026-05-24T19:15:19+00:00 | initial | random | dev | 20 | 1.9 | 16 | 4 | 0 | 0.8 | 13432 | pass |
| 2026-05-24T19:15:20+00:00 | initial | initial | dev | 20 | 0.25 | 11 | 9 | 0 | 0.55 | 16067 | pass |
| 2026-05-24T19:15:21+00:00 | initial | improved-v0 | dev | 20 | -0.15 | 8 | 12 | 0 | 0.4 | 16379 | pass |
| 2026-05-24T19:15:22+00:00 | initial | improved | dev | 20 | -2.5 | 3 | 17 | 0 | 0.15 | 16544 | pass |
| 2026-05-24T19:15:22+00:00 | improved-v0 | random | dev | 20 | 1.6 | 13 | 7 | 0 | 0.65 | 13098 | pass |
| 2026-05-24T19:15:23+00:00 | improved-v0 | initial | dev | 20 | 0.4 | 11 | 9 | 0 | 0.55 | 15396 | pass |
| 2026-05-24T19:15:24+00:00 | improved-v0 | improved-v0 | dev | 20 | 0.25 | 10 | 10 | 0 | 0.5 | 15625 | pass |
| 2026-05-24T19:15:25+00:00 | improved-v0 | improved | dev | 20 | -2.35 | 2 | 18 | 0 | 0.1 | 16865 | pass |
| 2026-05-24T19:15:26+00:00 | improved | random | dev | 20 | 3.1 | 18 | 2 | 0 | 0.9 | 13785 | pass |
| 2026-05-24T19:15:27+00:00 | improved | initial | dev | 20 | 2.7 | 18 | 2 | 0 | 0.9 | 15859 | pass |
| 2026-05-24T19:15:28+00:00 | improved | improved-v0 | dev | 20 | 2.65 | 18 | 2 | 0 | 0.9 | 16270 | pass |
| 2026-05-24T19:15:29+00:00 | improved | improved | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:23:11+00:00 | improved | builtin | dev | 20 | -5 | 0 | 20 | 0 | 0 | 21625 | pass |
| 2026-05-24T19:23:11+00:00 | improved | random | dev | 20 | 3.1 | 18 | 2 | 0 | 0.9 | 13785 | pass |
| 2026-05-24T19:23:12+00:00 | improved | initial | dev | 20 | 2.7 | 18 | 2 | 0 | 0.9 | 15859 | pass |
| 2026-05-24T19:23:13+00:00 | improved | improved-v0 | dev | 20 | 2.65 | 18 | 2 | 0 | 0.9 | 16270 | pass |
| 2026-05-24T19:23:14+00:00 | improved | improved-v1 | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:23:16+00:00 | improved | improved | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:23:34+00:00 | random | random | dev | 20 | -0.15 | 10 | 10 | 0 | 0.5 | 12947 | pass |
| 2026-05-24T19:23:35+00:00 | random | initial | dev | 20 | -2.25 | 2 | 18 | 0 | 0.1 | 13848 | pass |
| 2026-05-24T19:23:36+00:00 | random | improved-v0 | dev | 20 | -2.5 | 1 | 19 | 0 | 0.05 | 13949 | pass |
| 2026-05-24T19:23:37+00:00 | random | improved-v1 | dev | 20 | -2.9 | 1 | 19 | 0 | 0.05 | 14488 | pass |
| 2026-05-24T19:23:38+00:00 | random | improved | dev | 20 | -2.9 | 1 | 19 | 0 | 0.05 | 14488 | pass |
| 2026-05-24T19:23:39+00:00 | initial | random | dev | 20 | 1.9 | 16 | 4 | 0 | 0.8 | 13432 | pass |
| 2026-05-24T19:23:39+00:00 | initial | initial | dev | 20 | 0.25 | 11 | 9 | 0 | 0.55 | 16067 | pass |
| 2026-05-24T19:23:40+00:00 | initial | improved-v0 | dev | 20 | -0.15 | 8 | 12 | 0 | 0.4 | 16379 | pass |
| 2026-05-24T19:23:41+00:00 | initial | improved-v1 | dev | 20 | -2.5 | 3 | 17 | 0 | 0.15 | 16544 | pass |
| 2026-05-24T19:23:42+00:00 | initial | improved | dev | 20 | -2.5 | 3 | 17 | 0 | 0.15 | 16544 | pass |
| 2026-05-24T19:23:43+00:00 | improved-v0 | random | dev | 20 | 1.6 | 13 | 7 | 0 | 0.65 | 13098 | pass |
| 2026-05-24T19:23:44+00:00 | improved-v0 | initial | dev | 20 | 0.4 | 11 | 9 | 0 | 0.55 | 15396 | pass |
| 2026-05-24T19:23:45+00:00 | improved-v0 | improved-v0 | dev | 20 | 0.25 | 10 | 10 | 0 | 0.5 | 15625 | pass |
| 2026-05-24T19:23:46+00:00 | improved-v0 | improved-v1 | dev | 20 | -2.35 | 2 | 18 | 0 | 0.1 | 16865 | pass |
| 2026-05-24T19:23:46+00:00 | improved-v0 | improved | dev | 20 | -2.35 | 2 | 18 | 0 | 0.1 | 16865 | pass |
| 2026-05-24T19:23:47+00:00 | improved-v1 | random | dev | 20 | 3.1 | 18 | 2 | 0 | 0.9 | 13785 | pass |
| 2026-05-24T19:23:48+00:00 | improved-v1 | initial | dev | 20 | 2.7 | 18 | 2 | 0 | 0.9 | 15859 | pass |
| 2026-05-24T19:23:49+00:00 | improved-v1 | improved-v0 | dev | 20 | 2.65 | 18 | 2 | 0 | 0.9 | 16270 | pass |
| 2026-05-24T19:23:50+00:00 | improved-v1 | improved-v1 | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:23:52+00:00 | improved-v1 | improved | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:23:52+00:00 | improved | random | dev | 20 | 3.1 | 18 | 2 | 0 | 0.9 | 13785 | pass |
| 2026-05-24T19:23:53+00:00 | improved | initial | dev | 20 | 2.7 | 18 | 2 | 0 | 0.9 | 15859 | pass |
| 2026-05-24T19:23:54+00:00 | improved | improved-v0 | dev | 20 | 2.65 | 18 | 2 | 0 | 0.9 | 16270 | pass |
| 2026-05-24T19:23:55+00:00 | improved | improved-v1 | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:23:57+00:00 | improved | improved | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:24:24+00:00 | improved-v1 | builtin | dev | 20 | -5 | 0 | 20 | 0 | 0 | 21625 | pass |
| 2026-05-24T19:29:06+00:00 | improved | builtin | dev | 20 | -5 | 0 | 20 | 0 | 0 | 21625 | pass |
| 2026-05-24T19:31:44+00:00 | improved | builtin | dev | 20 | -5 | 0 | 20 | 0 | 0 | 21625 | pass |
| 2026-05-24T19:36:24+00:00 | improved | builtin | dev | 20 | -5 | 0 | 20 | 0 | 0 | 21625 | pass |
| 2026-05-24T19:36:24+00:00 | improved | random | dev | 20 | 3.1 | 18 | 2 | 0 | 0.9 | 13785 | pass |
| 2026-05-24T19:36:25+00:00 | improved | initial | dev | 20 | 2.7 | 18 | 2 | 0 | 0.9 | 15859 | pass |
| 2026-05-24T19:36:26+00:00 | improved | improved-v0 | dev | 20 | 2.65 | 18 | 2 | 0 | 0.9 | 16270 | pass |
| 2026-05-24T19:36:28+00:00 | improved | improved-v1 | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:36:29+00:00 | improved | improved-v2 | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:36:30+00:00 | improved | improved | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:36:31+00:00 | improved-v2 | builtin | dev | 20 | -5 | 0 | 20 | 0 | 0 | 21625 | pass |
| 2026-05-24T19:36:47+00:00 | random | random | dev | 20 | -0.15 | 10 | 10 | 0 | 0.5 | 12947 | pass |
| 2026-05-24T19:36:48+00:00 | random | initial | dev | 20 | -2.25 | 2 | 18 | 0 | 0.1 | 13848 | pass |
| 2026-05-24T19:36:49+00:00 | random | improved-v0 | dev | 20 | -2.5 | 1 | 19 | 0 | 0.05 | 13949 | pass |
| 2026-05-24T19:36:49+00:00 | random | improved-v1 | dev | 20 | -2.9 | 1 | 19 | 0 | 0.05 | 14488 | pass |
| 2026-05-24T19:36:50+00:00 | random | improved-v2 | dev | 20 | -2.9 | 1 | 19 | 0 | 0.05 | 14488 | pass |
| 2026-05-24T19:36:51+00:00 | random | improved | dev | 20 | -2.9 | 1 | 19 | 0 | 0.05 | 14488 | pass |
| 2026-05-24T19:36:52+00:00 | initial | random | dev | 20 | 1.9 | 16 | 4 | 0 | 0.8 | 13432 | pass |
| 2026-05-24T19:36:53+00:00 | initial | initial | dev | 20 | 0.25 | 11 | 9 | 0 | 0.55 | 16067 | pass |
| 2026-05-24T19:36:54+00:00 | initial | improved-v0 | dev | 20 | -0.15 | 8 | 12 | 0 | 0.4 | 16379 | pass |
| 2026-05-24T19:36:55+00:00 | initial | improved-v1 | dev | 20 | -2.5 | 3 | 17 | 0 | 0.15 | 16544 | pass |
| 2026-05-24T19:36:56+00:00 | initial | improved-v2 | dev | 20 | -2.5 | 3 | 17 | 0 | 0.15 | 16544 | pass |
| 2026-05-24T19:36:57+00:00 | initial | improved | dev | 20 | -2.5 | 3 | 17 | 0 | 0.15 | 16544 | pass |
| 2026-05-24T19:36:58+00:00 | improved-v0 | random | dev | 20 | 1.6 | 13 | 7 | 0 | 0.65 | 13098 | pass |
| 2026-05-24T19:36:59+00:00 | improved-v0 | initial | dev | 20 | 0.4 | 11 | 9 | 0 | 0.55 | 15396 | pass |
| 2026-05-24T19:37:00+00:00 | improved-v0 | improved-v0 | dev | 20 | 0.25 | 10 | 10 | 0 | 0.5 | 15625 | pass |
| 2026-05-24T19:37:01+00:00 | improved-v0 | improved-v1 | dev | 20 | -2.35 | 2 | 18 | 0 | 0.1 | 16865 | pass |
| 2026-05-24T19:37:01+00:00 | improved-v0 | improved-v2 | dev | 20 | -2.35 | 2 | 18 | 0 | 0.1 | 16865 | pass |
| 2026-05-24T19:37:02+00:00 | improved-v0 | improved | dev | 20 | -2.35 | 2 | 18 | 0 | 0.1 | 16865 | pass |
| 2026-05-24T19:37:03+00:00 | improved-v1 | random | dev | 20 | 3.1 | 18 | 2 | 0 | 0.9 | 13785 | pass |
| 2026-05-24T19:37:04+00:00 | improved-v1 | initial | dev | 20 | 2.7 | 18 | 2 | 0 | 0.9 | 15859 | pass |
| 2026-05-24T19:37:05+00:00 | improved-v1 | improved-v0 | dev | 20 | 2.65 | 18 | 2 | 0 | 0.9 | 16270 | pass |
| 2026-05-24T19:37:07+00:00 | improved-v1 | improved-v1 | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:37:08+00:00 | improved-v1 | improved-v2 | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:37:09+00:00 | improved-v1 | improved | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:37:10+00:00 | improved-v2 | random | dev | 20 | 3.1 | 18 | 2 | 0 | 0.9 | 13785 | pass |
| 2026-05-24T19:37:11+00:00 | improved-v2 | initial | dev | 20 | 2.7 | 18 | 2 | 0 | 0.9 | 15859 | pass |
| 2026-05-24T19:37:12+00:00 | improved-v2 | improved-v0 | dev | 20 | 2.65 | 18 | 2 | 0 | 0.9 | 16270 | pass |
| 2026-05-24T19:37:13+00:00 | improved-v2 | improved-v1 | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:37:15+00:00 | improved-v2 | improved-v2 | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:37:16+00:00 | improved-v2 | improved | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:37:17+00:00 | improved | random | dev | 20 | 3.1 | 18 | 2 | 0 | 0.9 | 13785 | pass |
| 2026-05-24T19:37:18+00:00 | improved | initial | dev | 20 | 2.7 | 18 | 2 | 0 | 0.9 | 15859 | pass |
| 2026-05-24T19:37:19+00:00 | improved | improved-v0 | dev | 20 | 2.65 | 18 | 2 | 0 | 0.9 | 16270 | pass |
| 2026-05-24T19:37:20+00:00 | improved | improved-v1 | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:37:22+00:00 | improved | improved-v2 | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:37:23+00:00 | improved | improved | dev | 20 | 0.35 | 9 | 11 | 0 | 0.45 | 23401 | pass |
| 2026-05-24T19:44:47+00:00 | random | builtin | holdout | 50 | -4.84 | 0 | 50 | 0 | 0 | 30360 | pass |
| 2026-05-24T19:44:48+00:00 | random | random | holdout | 50 | 0.28 | 26 | 24 | 0 | 0.52 | 31361 | pass |
| 2026-05-24T19:44:50+00:00 | random | initial | holdout | 50 | -1.62 | 14 | 36 | 0 | 0.28 | 32595 | pass |
| 2026-05-24T19:44:52+00:00 | random | improved-v0 | holdout | 50 | -1.48 | 14 | 36 | 0 | 0.28 | 33649 | pass |
| 2026-05-24T19:44:55+00:00 | random | improved-v2 | holdout | 50 | -2.82 | 5 | 45 | 0 | 0.1 | 35313 | pass |
| 2026-05-24T19:44:56+00:00 | initial | builtin | holdout | 50 | -4.88 | 0 | 50 | 0 | 0 | 31491 | pass |
| 2026-05-24T19:44:58+00:00 | initial | random | holdout | 50 | 1.76 | 37 | 13 | 0 | 0.74 | 33080 | pass |
| 2026-05-24T19:45:00+00:00 | initial | initial | holdout | 50 | 0.02 | 25 | 25 | 0 | 0.5 | 37308 | pass |
| 2026-05-24T19:45:02+00:00 | initial | improved-v0 | holdout | 50 | 0.2 | 26 | 24 | 0 | 0.52 | 37638 | pass |
| 2026-05-24T19:45:04+00:00 | initial | improved-v2 | holdout | 50 | -2.3 | 6 | 44 | 0 | 0.12 | 40023 | pass |
| 2026-05-24T19:45:06+00:00 | tuned | builtin | holdout | 50 | -4.8 | 0 | 50 | 0 | 0 | 33089 | pass |
| 2026-05-24T19:45:08+00:00 | tuned | random | holdout | 50 | 2.38 | 42 | 8 | 0 | 0.84 | 33717 | pass |
| 2026-05-24T19:45:10+00:00 | tuned | initial | holdout | 50 | 0.86 | 32 | 18 | 0 | 0.64 | 38875 | pass |
| 2026-05-24T19:45:12+00:00 | tuned | improved-v0 | holdout | 50 | 1.06 | 33 | 17 | 0 | 0.66 | 38516 | pass |
| 2026-05-24T19:45:14+00:00 | tuned | improved-v2 | holdout | 50 | -2.04 | 10 | 40 | 0 | 0.2 | 43803 | pass |
| 2026-05-24T19:45:17+00:00 | improved | builtin | holdout | 50 | -4.78 | 0 | 50 | 0 | 0 | 49147 | pass |
| 2026-05-24T19:45:19+00:00 | improved | random | holdout | 50 | 3 | 46 | 4 | 0 | 0.92 | 33664 | pass |
| 2026-05-24T19:45:21+00:00 | improved | initial | holdout | 50 | 2.22 | 43 | 7 | 0 | 0.86 | 40509 | pass |
| 2026-05-24T19:45:23+00:00 | improved | improved-v0 | holdout | 50 | 2.36 | 44 | 6 | 0 | 0.88 | 41046 | pass |
| 2026-05-24T19:45:27+00:00 | improved | improved-v2 | holdout | 50 | 0.8 | 33 | 17 | 0 | 0.66 | 55511 | pass |
| 2026-05-24T19:45:34+00:00 | baseline-rnn | builtin | holdout | 50 | 0.06 | 17 | 14 | 19 | 0.34 | 150000 | pass |
| 2026-05-24T19:45:36+00:00 | baseline-rnn | random | holdout | 50 | 4.88 | 50 | 0 | 0 | 1 | 28405 | pass |
| 2026-05-24T19:45:38+00:00 | baseline-rnn | initial | holdout | 50 | 4.86 | 50 | 0 | 0 | 1 | 32952 | pass |
| 2026-05-24T19:45:40+00:00 | baseline-rnn | improved-v0 | holdout | 50 | 4.86 | 50 | 0 | 0 | 1 | 33335 | pass |
| 2026-05-24T19:45:43+00:00 | baseline-rnn | improved-v2 | holdout | 50 | 4.84 | 50 | 0 | 0 | 1 | 51143 | pass |

## Failure Notes

- `2026-05-24T18:29:25+00:00` `initial` vs `builtin`: SlimeVolleyDependencyError: SlimeVolley requires optional legacy dependencies: gym and slimevolleygym. Current status: ModuleNotFoundError: No module named 'gym'

## Seed Ranges

Fixed seed ranges are declared centrally in `hl_benchmark.envs.SEED_SPLITS`.

| Split | Seeds | Intended use | Recorded rows | Recorded episodes | Recorded steps |
| --- | --- | --- | ---: | ---: | ---: |
| dev | `0..19` | diagnosis, policy iteration, and scalar search | 152 | 3040 | 2531067 |
| holdout | `1000..1049` | final-only evaluation after policies are frozen | 25 | 1250 | 1046530 |
| audit | `2000..2049` | reserved future audit seeds; not used in this SlimeVolley run | 0 | 0 | 0 |
| smoke | `0..1` | dependency and harness smoke checks | 9 | 18 | 11531 |

Holdout rows are already present, so future policy changes must use a new, predeclared experiment generation rather than reusing these final seeds.

## Policy Evolution Timeline

Policy code lives in `hl_benchmark/policies/slimevolley.py`; construction is routed through `hl_benchmark/policies/factory.py`.
Timeline rows aggregate generation-1, generation-2, and generation-3 ledgers when those artifacts are present, plus generation-4 development rows when present.

| Version | Classification | Interpretable change | Ledger rows | First seen | Last seen |
| --- | --- | --- | ---: | --- | --- |
| random | random baseline | Seeded MultiBinary(3) actions; not an interpretable controller. | 78 | 2026-05-24T18:36:43+00:00 | 2026-05-27T03:06:52+00:00 |
| initial | initial handwritten heuristic | Tracks the ball, predicts a short landing x position, jumps near descending contact, and returns home otherwise. | 84 | 2026-05-24T18:29:25+00:00 | 2026-05-27T03:07:24+00:00 |
| improved-v0 | structural archive | Adds serve, recovery, and high-arc handling. Frozen before low_ball_rescue. | 48 | 2026-05-24T19:15:22+00:00 | 2026-05-25T21:01:47+00:00 |
| improved-v1 | structural archive | Adds low_ball_rescue for fast low balls on the agent side. Frozen before late_low_ball_guard. | 46 | 2026-05-24T19:23:47+00:00 | 2026-05-25T21:02:18+00:00 |
| improved-v2 | structural archive | Adds late_low_ball_guard to avoid jumping when already above a late low ball. Frozen before grounded_low_receive. | 41 | 2026-05-24T19:36:31+00:00 | 2026-05-25T21:02:48+00:00 |
| improved-v3 | structural archive | Adds grounded_low_receive and is frozen before the kept generation-3 rear_wall_press branch. | 21 | 2026-05-25T20:19:16+00:00 | 2026-05-25T21:03:27+00:00 |
| improved-v4 | structural archive | Adds generation-3 rear_wall_press and is frozen before generation-4 front_hit_suppression. | 0 |  |  |
| improved-v5 | structural archive | Adds generation-4 front_hit_suppression and is frozen before rear_wall_low_jump. | 0 |  |  |
| improved-v6 | structural archive | Adds rear_wall_low_jump and is frozen before front_net_low_scoop. | 0 |  |  |
| improved | current structural heuristic | Retains rear_wall_low_jump after the front_net_low_scoop attempt was rolled back for weaker development performance. | 154 | 2026-05-24T18:35:40+00:00 | 2026-05-27T03:08:38+00:00 |
| improved-tuned | generation-4 scalar/config tuned heuristic | Keeps the current structural rules but tunes contact_x_window, high_arc_horizon, overcommit_guard_x, low_ball_rescue_x_window, grounded_low_receive_airborne_margin, x_margin, and low_ball_rescue_horizon on development seeds; counted separately from structural improvements. | 29 | 2026-05-26T23:05:38+00:00 | 2026-05-27T03:38:41+00:00 |
| attack | generation-4 structural attack candidate | Adds a narrow late_contact_attack forward+jump rule to improved-tuned v2; partial evidence only because it improves built-in score but regresses nearest archived opponents and remains below baseline-rnn. | 20 | 2026-05-27T00:12:13+00:00 | 2026-05-27T03:38:16+00:00 |
| temporal | generation-4 temporal candidate | Adds short stacked-history contact/phase features as a development-only candidate; not promoted over improved because evidence is mixed. | 15 | 2026-05-26T06:33:11+00:00 | 2026-05-26T06:41:08+00:00 |
| planner | generation-4 physics planner candidate | Adds time-to-floor, net-clearance, one-wall-bounce, opponent-commitment, and jump-budget features as a pure structural heuristic candidate. | 2 | 2026-05-26T19:38:54+00:00 | 2026-05-26T19:41:18+00:00 |
| teacher-assisted | generation-4 teacher-assisted planner candidate | Keeps the planner transparent while reserving labeled margins/rules for hand-audited baseline-rnn development-trace suggestions; no RNN runtime calls. | 2 | 2026-05-26T19:39:25+00:00 | 2026-05-26T19:42:02+00:00 |
| tuned | scalar/config search baseline | Uses scalar changes to the initial heuristic; it is not counted as structural policy improvement. | 169 | 2026-05-24T18:45:18+00:00 | 2026-05-25T21:20:24+00:00 |
| baseline-rnn | pretrained neural/RNN comparator | Wraps slimevolleygym's shipped 120-parameter BaselinePolicy; included only as a labeled neural comparator. | 42 | 2026-05-24T18:58:54+00:00 | 2026-05-27T04:16:23+00:00 |

## Development Diagnosis

- `random` vs `builtin`: mean `-4.85`, wins `0`, losses `20`.
- `initial` vs `builtin`: mean `-4.95`, wins `0`, losses `20`.
- `improved` vs `builtin`: mean `-5`, wins `0`, losses `20`.
- Structural `improved` regressed vs `initial` against `builtin` (-5 vs -4.95).
- Structural `improved` beat `initial` against `improved` (0.35 vs -2.5).
- Structural `improved` beat `initial` against `improved-v0` (2.65 vs -0.15).
- Structural `improved` beat `initial` against `improved-v1` (0.35 vs -2.5).
- Structural `improved` beat `initial` against `improved-v2` (0.35 vs -2.5).
- Structural `improved` beat `initial` against `initial` (2.7 vs 0.25).
- Structural `improved` beat `initial` against `random` (3.1 vs 1.9).
- Diagnosis: low-ball rescue improves the non-built-in opponent pool, but the current structural modes still do not solve the built-in opponent.

## Diagnostic Coverage

- Passing rows with per-episode diagnostics: `185/185`.
- Per-episode records: `4306`; records with seed, score, steps, outcome, and action counts: `4306`.
- Point events recorded: `21691` total, `11020` won, `10671` lost; events with compact pre-event traces: `200`.
- Rows with agent action frequencies: `185/185`; rows with opponent action frequencies: `155/185`.
- Rows with explicit opponent name, kind, and version: `185/185`.
- Minimum logged fields covered: per-episode score, timesteps, life-loss/life-win point events, final outcome, opponent type/name, seed, policy version, and action frequencies.
- Optional replay artifacts are compact JSON traces around selected point events rather than rendered video files.

## Trace Diagnostics

- Latest traced row: `2026-05-24T19:31:44+00:00` with trace window `6`.
- Lost point traces: `100`; score mean `-5`.
- Contact/return diagnostic artifacts: `results/contact_diagnostics_g3_dev.json` and `reports/contact_diagnostics_g3_dev.md` summarize inferred contact candidates from the same development traces.
- Scoring-step actions: `{'100': 44, '101': 22, '000': 18, '010': 8, '001': 5, '011': 3}`.
- First trace-frame actions: `{'101': 57, '100': 12, '010': 11, '011': 10, '000': 5, '001': 5}`; last trace-frame actions: `{'100': 44, '101': 22, '000': 18, '010': 8, '001': 5, '011': 3}`.
- Mean ball-minus-agent x moved from `-0.195698` to `-0.142336`; mean absolute x-distance improvement was `0.0651726`.
- Mean final traced agent y `0.389655` versus ball y `0.220602`, with mean ball vy `-1.32567`.
- Trace diagnosis: losses are usually not pure x-position misses; the agent is near the ball horizontally but remains above a fast-descending low ball. This motivated `grounded_low_receive`; paired evidence below shows jump suppression alone tied its predecessor, so the next structural hypothesis should move earlier into receive positioning or contact timing.

## Failed Or Partial Directions

- `late_low_ball_guard`: tied frozen `improved-v1` against `builtin` (both mean `-5`), so it did not solve the built-in failure.
- `improved-v2` and frozen `improved-v1` tied each other in round-robin cross-play (means `0.35` and `0.35`).
- `grounded_low_receive`: tied frozen `improved-v2` against `builtin` (both mean `-5`), so it did not solve the built-in failure.
- `improved` and frozen `improved-v2` tied each other in round-robin cross-play (means `0.35` and `0.35`).

## Round-Robin Tournament

- Artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/round_robin_dev.json`
- Split: `dev`
- Participants: `random, initial, improved-v0, improved-v1, improved-v2, improved`
- Matchups: `36`
- Status: `pass`

| Rank | Policy | Mean score across opponents | Win rate | Wins | Losses | Draws | Steps |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | improved-v1 | 1.58333 | 0.675 | 81 | 39 | 0 | 116117 |
| 2 | improved-v2 | 1.58333 | 0.675 | 81 | 39 | 0 | 116117 |
| 3 | improved | 1.58333 | 0.675 | 81 | 39 | 0 | 116117 |
| 4 | improved-v0 | -0.8 | 0.333333 | 40 | 80 | 0 | 94714 |
| 5 | initial | -0.916667 | 0.366667 | 44 | 76 | 0 | 95510 |
| 6 | random | -2.26667 | 0.133333 | 16 | 104 | 0 | 84208 |

## Holdout Evaluation

Holdout rows are final evidence and must not be used for further policy tuning.
- Recorded holdout rows: `25`
- Artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_final.json`
- Policies: `random, initial, tuned, improved, baseline-rnn`
- Opponents: `builtin, random, initial, improved-v0, improved-v2`
- Matchups: `25`
- Episodes per matchup: `50`

| Policy | Opponent | Episodes | Mean | Wins | Losses | Draws | Win rate | Steps |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline-rnn | builtin | 50 | 0.06 | 17 | 14 | 19 | 0.34 | 150000 |
| baseline-rnn | improved-v0 | 50 | 4.86 | 50 | 0 | 0 | 1 | 33335 |
| baseline-rnn | improved-v2 | 50 | 4.84 | 50 | 0 | 0 | 1 | 51143 |
| baseline-rnn | initial | 50 | 4.86 | 50 | 0 | 0 | 1 | 32952 |
| baseline-rnn | random | 50 | 4.88 | 50 | 0 | 0 | 1 | 28405 |
| improved | builtin | 50 | -4.78 | 0 | 50 | 0 | 0 | 49147 |
| improved | improved-v0 | 50 | 2.36 | 44 | 6 | 0 | 0.88 | 41046 |
| improved | improved-v2 | 50 | 0.8 | 33 | 17 | 0 | 0.66 | 55511 |
| improved | initial | 50 | 2.22 | 43 | 7 | 0 | 0.86 | 40509 |
| improved | random | 50 | 3 | 46 | 4 | 0 | 0.92 | 33664 |
| initial | builtin | 50 | -4.88 | 0 | 50 | 0 | 0 | 31491 |
| initial | improved-v0 | 50 | 0.2 | 26 | 24 | 0 | 0.52 | 37638 |
| initial | improved-v2 | 50 | -2.3 | 6 | 44 | 0 | 0.12 | 40023 |
| initial | initial | 50 | 0.02 | 25 | 25 | 0 | 0.5 | 37308 |
| initial | random | 50 | 1.76 | 37 | 13 | 0 | 0.74 | 33080 |
| random | builtin | 50 | -4.84 | 0 | 50 | 0 | 0 | 30360 |
| random | improved-v0 | 50 | -1.48 | 14 | 36 | 0 | 0.28 | 33649 |
| random | improved-v2 | 50 | -2.82 | 5 | 45 | 0 | 0.1 | 35313 |
| random | initial | 50 | -1.62 | 14 | 36 | 0 | 0.28 | 32595 |
| random | random | 50 | 0.28 | 26 | 24 | 0 | 0.52 | 31361 |
| tuned | builtin | 50 | -4.8 | 0 | 50 | 0 | 0 | 33089 |
| tuned | improved-v0 | 50 | 1.06 | 33 | 17 | 0 | 0.66 | 38516 |
| tuned | improved-v2 | 50 | -2.04 | 10 | 40 | 0 | 0.2 | 43803 |
| tuned | initial | 50 | 0.86 | 32 | 18 | 0 | 0.64 | 38875 |
| tuned | random | 50 | 2.38 | 42 | 8 | 0 | 0.84 | 33717 |

## Generation-2 Evidence

Generation-2 evidence uses fresh predeclared seeds and a separate ledger from the original SlimeVolley run.
Generation-2 holdout rows are final-only evidence and must not be used for further policy, scalar-config, or opponent-pool tuning.
- Generation-2 ledger: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_2_trials.jsonl`
- Generation-2 summary: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_2_summary.csv`
- Generation-2 ledger rows: `114`
- Generation-2 split counts: `{'dev': 89, 'holdout': 25}`
- Generation-2 scalar-search artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/search_best_g2_dev.json`
- Generation-2 round-robin artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/round_robin_g2_dev.json`
- Generation-2 holdout artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_g2_final.json`
- Generation-2 holdout seeds: `4000..4049`
- Matchups: `25`
- Episodes per matchup: `50`
- Policies: `random, initial, tuned, improved, baseline-rnn`
- Opponents: `builtin, random, initial, improved-v0, improved-v2`

| Policy | Opponent | Episodes | Mean | Wins | Losses | Draws | Win rate | Steps |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline-rnn | builtin | 50 | -0.04 | 16 | 14 | 20 | 0.32 | 150000 |
| baseline-rnn | improved-v0 | 50 | 4.9 | 50 | 0 | 0 | 1 | 32749 |
| baseline-rnn | improved-v2 | 50 | 4.82 | 50 | 0 | 0 | 1 | 50943 |
| baseline-rnn | initial | 50 | 4.92 | 50 | 0 | 0 | 1 | 33037 |
| baseline-rnn | random | 50 | 4.9 | 50 | 0 | 0 | 1 | 30209 |
| improved | builtin | 50 | -4.28 | 0 | 49 | 1 | 0 | 109720 |
| improved | improved-v0 | 50 | 3.3 | 49 | 1 | 0 | 0.98 | 42270 |
| improved | improved-v2 | 50 | 2.7 | 47 | 3 | 0 | 0.94 | 59614 |
| improved | initial | 50 | 3.46 | 49 | 1 | 0 | 0.98 | 41954 |
| improved | random | 50 | 3.44 | 49 | 1 | 0 | 0.98 | 38386 |
| initial | builtin | 50 | -4.68 | 0 | 50 | 0 | 0 | 33876 |
| initial | improved-v0 | 50 | -0.16 | 26 | 24 | 0 | 0.52 | 37355 |
| initial | improved-v2 | 50 | -2.24 | 9 | 41 | 0 | 0.18 | 39535 |
| initial | initial | 50 | -0.46 | 24 | 26 | 0 | 0.48 | 35270 |
| initial | random | 50 | 1 | 36 | 14 | 0 | 0.72 | 34722 |
| random | builtin | 50 | -4.72 | 0 | 50 | 0 | 0 | 28889 |
| random | improved-v0 | 50 | -1.68 | 14 | 36 | 0 | 0.28 | 33993 |
| random | improved-v2 | 50 | -3.36 | 0 | 50 | 0 | 0 | 33082 |
| random | initial | 50 | -1.9 | 13 | 37 | 0 | 0.26 | 32598 |
| random | random | 50 | -0.66 | 21 | 29 | 0 | 0.42 | 32340 |
| tuned | builtin | 50 | -4.78 | 0 | 50 | 0 | 0 | 34808 |
| tuned | improved-v0 | 50 | 0.7 | 33 | 17 | 0 | 0.66 | 38383 |
| tuned | improved-v2 | 50 | -1.9 | 12 | 38 | 0 | 0.24 | 43044 |
| tuned | initial | 50 | 0.38 | 29 | 21 | 0 | 0.58 | 36453 |
| tuned | random | 50 | 1.52 | 38 | 12 | 0 | 0.76 | 34823 |

Generation-2 headline: the current structural heuristic improved over the initial and scalar-tuned heuristic on the non-built-in opponent pool, but it still failed to solve the built-in opponent and remained far behind `baseline-rnn`.
Any additional SlimeVolley policy work now requires following the predeclared generation-4 protocol with development seeds `9000..9049`, sealed holdout seeds `10000..10049`, and reserved audit seeds `11000..11049`.

## Generation-3 Evidence

Generation-3 now includes final-only holdout evidence after the frozen policy/config/opponent/test state was evaluated. It must not be used for subsequent tuning.
- Generation-3 protocol JSON: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/configs/generation_3_protocol.json`
- Generation-3 protocol report: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/reports/generation_3_protocol.md`
- Generation-3 diagnosis report: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/reports/generation_3_diagnosis.md`
- Generation-3 ledger: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_3_trials.jsonl`
- Generation-3 summary: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_3_summary.csv`
- Generation-3 ledger rows: `303`
- Generation-3 split counts: `{'dev': 273, 'holdout': 30}`
- Generation-3 pass/fail counts: `{'fail': 1, 'pass': 302}`
- Generation-3 holdout artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_g3_final.json` is present and must be treated as final-only evidence.

Latest generation-3 development diagnostic:

| Policy | Opponent | Seeds | Episodes | Mean | Wins | Losses | Draws | Steps |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| improved | builtin | `6000..6049` | 50 | -3.8 | 0 | 48 | 2 | 129391 |

Generation-3 final holdout built-in row:

| Policy | Opponent | Seeds | Episodes | Mean | Wins | Losses | Draws | Steps |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| improved | builtin | `7000..7049` | 50 | -3.68 | 0 | 48 | 2 | 126972 |

Generation-3 failed rows remain visible:
- `2026-05-25T19:23:07+00:00` `improved` vs `builtin`: SlimeVolleyDependencyError: SlimeVolley requires optional legacy dependencies: gym and slimevolleygym. Current status: ModuleNotFoundError: No module named 'gym'
Generation-3 holdout evidence confirms the built-in opponent gap remains and is final-only; further tuning requires fresh seeds.

## Generation-4 Development Attempt

Generation-4 now includes final-only holdout evidence. It records temporal/planner candidates, kept structural edits through rear_wall_low_jump, a separate scalar/config-tuned improved-tuned baseline, the partial late-contact attack structural candidate, failed/partial scalar and structural probes, the rally-serve candidate, a post-contact front-conversion development candidate, and a final-only holdout comparison against `baseline-rnn`.
- Generation-4 protocol JSON: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/configs/generation_4_protocol.json`
- Generation-4 protocol report: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/reports/generation_4_protocol.md`
- Generation-4 temporal attempt report: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/reports/generation_4_temporal_history_attempt.md`
- Generation-4 front-hit suppression note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_4_front_hit_suppression_attempt.md`
- Generation-4 rear-wall low-jump note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_4_rear_wall_low_jump_attempt.md`
- Generation-4 front-net low-scoop rollback note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_4_front_net_low_scoop_attempt.md`
- Generation-4 scalar-tuned baseline note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_4_scalar_tuned_structural_attempt.md`
- Generation-4 late-contact attack note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_4_late_contact_attack_attempt.md`
- Generation-4 joint attack scalar-search note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_4_joint_attack_scalar_search_attempt.md`
- Generation-4 low-receive teacher/scalar follow-up note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_4_low_receive_teacher_scalar_followup.md`
- Generation-4 rally-serve candidate note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_4_rally_serve_candidate.md`
- Generation-4 parallel scalar rally/attack worker note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_scalar_rally_attack_worker.md`
- Generation-4 parallel grounded-low-receive stacked worker note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_grounded_low_receive_stacked_worker.md`
- Generation-4 parallel rear-wall stacked worker note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_rear_wall_stacked_worker.md`
- Generation-4 parallel rally-serve robustness worker note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_robustness_rallyserve_worker.md`
- Generation-4 parallel rally/attack/RNN trace report: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/reports/parallel/20260527_trace_rally_attack_rnn_worker.md`
- Generation-4 parallel rally-serve synthesis report: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/reports/parallel/20260527_parallel_synthesis_rallyserve.md`
- Generation-4 subagent attack scalar note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_g4_attack_scalar_subagent.md`
- Generation-4 subagent grounded-low-receive note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_g4_grounded_low_receive_subagent.md`
- Generation-4 subagent rear-wall press note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_g4_rear_wall_press_subagent.md`
- Generation-4 subagent archived-opponent robustness note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_g4_archived_robustness_subagent.md`
- Generation-4 subagent attack/RNN trace report: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/reports/parallel/20260527_g4_trace_attack_vs_rnn_subagent.md`
- Generation-4 subagent synthesis report: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/reports/parallel/20260527_g4_parallel_subagent_synthesis.md`
- Generation-4 subagent scalar/config v2 note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_g4_attack_scalar_subagent_v2.md`
- Generation-4 Worker A attack/net-pressure scalar note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/g4_attack_scalar_worker_a_20260527.md`
- Generation-4 subagent grounded-low-receive v2 note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_g4_grounded_low_receive_subagent_v2.md`
- Generation-4 Worker B grounded-low-receive screen note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/g4_grounded_low_receive_worker_b_screen.md`
- Generation-4 subagent rear-wall press v2 note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_g4_rear_wall_press_subagent_v2.md`
- Generation-4 Worker C rear-wall press note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/g4_rear_wall_press_worker_c_20260527.md`
- Generation-4 subagent archived-opponent robustness v2 note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_g4_archived_robustness_subagent_v2.md`
- Generation-4 subagent attack/rally-serve/RNN trace v2 report: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/reports/parallel/20260527_g4_trace_attack_vs_rnn_subagent_v2.md`
- Generation-4 Worker D attack/net-pressure/RNN trace report: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/reports/parallel/g4_trace_attack_vs_baseline_rnn_worker_d_20260527.md`
- Generation-4 parallel4 synthesis report: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/reports/parallel/20260527_g4_parallel4_synthesis.md`
- Generation-4 parallel6 scalar/config note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_g4_parallel6_attack_scalar.md`
- Generation-4 parallel6 grounded-low-receive note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_g4_parallel6_grounded_low_receive.md`
- Generation-4 parallel6 rear-wall press note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_g4_parallel6_rear_wall_press.md`
- Generation-4 parallel6 archived-opponent robustness note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_g4_parallel6_archived_robustness.md`
- Generation-4 parallel6 attack/rally-serve/RNN trace report: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/reports/parallel/20260527_g4_parallel6_trace_attack_rnn.md`
- Generation-4 parallel6 synthesis report: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/reports/parallel/20260527_g4_parallel6_synthesis.md`
- Generation-4 subagent synthesis v2 report: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/reports/parallel/20260527_g4_parallel_subagent_synthesis_v2.md`
- Generation-4 post-contact front-conversion candidate note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_4_post_contact_front_conversion_attempt.md`
- Generation-4 post-contact Worker E archived-opponent robustness note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/g4_archived_opponent_robustness_post_contact_worker_e.md`
- Generation-4 post-contact gate probe script: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/probes/g4_post_contact_gate_probe.py`
- Generation-4 post-contact gate probe results: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_4_post_contact_gate_probe.json`
- Generation-4 stacked low-receive probe note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_4_stacked_low_receive_probe.md`
- Generation-4 stacked low-receive probe script: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/probes/g4_stacked_low_receive_probe.py`
- Generation-4 stacked low-receive probe results: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_4_stacked_low_receive_probe.json`
- Generation-4 parallel3 scalar/config note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_g4_parallel3_attack_scalar.md`
- Generation-4 parallel3 grounded-low-receive history note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_g4_parallel3_grounded_low_receive.md`
- Generation-4 parallel3 rear-wall press note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_g4_parallel3_rear_wall_press.md`
- Generation-4 parallel3 attack/rally-serve/net-pressure/RNN trace report: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/reports/parallel/20260527_g4_parallel3_trace_attack_rnn.md`
- Generation-4 net-pressure fixed-pool no-ledger results: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_4_net_pressure_noledger_probe.json`
- Generation-4 net-pressure fixed-pool no-ledger note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_g4_net_pressure_fixed_pool_noledger.md`
- Generation-4 parallel3 archived-opponent robustness note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/parallel/20260527_g4_parallel3_archived_robustness.md`
- Generation-4 ledger: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_4_trials.jsonl`
- Generation-4 summary: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_4_summary.csv`
- Generation-4 final holdout artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_g4_final.json` is present and is final-only evidence.
- Generation-4 ledger rows: `155`
- Generation-4 split counts: `{'dev': 92, 'holdout': 63}`
- Generation-4 pass/fail counts: `{'pass': 155}`
- Warning: generation-4 holdout rows are present. Treat them as final-only evidence and do not tune against them.

Generation-4 final-only holdout summary (`10000..10049`):

| Policy | Opponent | Mean | W/L/D | Steps |
| --- | --- | ---: | --- | ---: |
| random | builtin | -4.84 | 0/50/0 | 28961 |
| initial | builtin | -4.8 | 0/50/0 | 33267 |
| improved | builtin | -2.66 | 1/47/2 | 146843 |
| improved-tuned | builtin | -0.56 | 6/23/21 | 150000 |
| attack | builtin | -0.1 | 12/19/19 | 150000 |
| rally-serve | builtin | -0.22 | 6/14/30 | 150000 |
| baseline-rnn | builtin | -0.12 | 10/15/25 | 150000 |
| rally-serve | improved-v5 | 1.4 | 38/2/10 | 148463 |
| baseline-rnn | improved-v5 | 2.1 | 43/2/5 | 148427 |
| rally-serve | improved-v6 | 1.44 | 38/2/10 | 147298 |
| baseline-rnn | improved-v6 | 2.1 | 43/2/5 | 147118 |
- Final-only built-in holdout result: `rally-serve` mean `-0.22` versus `baseline-rnn` mean `-0.12`; holdout delta `-0.1`.
- Final-only archived-opponent result versus `improved-v5`: `rally-serve` mean `1.4` versus `baseline-rnn` mean `2.1`; delta `-0.7`.
- Final-only archived-opponent result versus `improved-v6`: `rally-serve` mean `1.44` versus `baseline-rnn` mean `2.1`; delta `-0.66`.
- Generation-4 holdout conclusion: `rally-serve` did not beat `baseline-rnn` on sealed built-in holdout; no generation-4 heuristic policy is promoted from this final evidence.

Latest 50-seed development comparison (`9000..9049`):

| Opponent | Improved mean | Temporal mean | Delta | Improved W/L/D | Temporal W/L/D |
| --- | ---: | ---: | ---: | --- | --- |
| builtin | -2.24 | -3.8 | -1.56 | 1/43/6 | 0/50/0 |
| random | 4.5 | 4.06 | -0.44 | 50/0/0 | 49/1/0 |
| initial | 4.5 | 3.88 | -0.62 | 50/0/0 | 49/1/0 |
| improved-v0 | 4.48 | 4.04 | -0.44 | 50/0/0 | 49/1/0 |
| improved-v2 | 4.16 | 3.54 | -0.62 | 50/0/0 | 48/2/0 |
| improved-v3 | 1.94 | 0.3 | -1.64 | 35/7/8 | 25/21/4 |

Temporal score deltas across paired development opponents: `0` better, `6` worse, `0` tied.
Decision: keep `temporal` as an auditable generation-4 candidate and opponent, but do not promote it over `improved` because the full development evidence is mixed and built-in performance is slightly worse.

Latest scalar/config tuned baseline versus current `improved` (`9000..9049`):

| Opponent | Improved mean | Improved-tuned mean | Delta | Improved W/L/D | Tuned W/L/D |
| --- | ---: | ---: | ---: | --- | --- |
| builtin | -2.24 | -0.44 | +1.8 | 1/43/6 | 6/23/21 |
| random | 4.5 | 4.66 | +0.16 | 50/0/0 | 50/0/0 |
| initial | 4.5 | 4.56 | +0.06 | 50/0/0 | 50/0/0 |
| improved-v0 | 4.48 | 4.6 | +0.12 | 50/0/0 | 50/0/0 |
| improved-v2 | 4.16 | 4.38 | +0.22 | 50/0/0 | 49/1/0 |
| improved-v3 | 1.94 | 2.38 | +0.44 | 35/7/8 | 42/1/7 |
| improved-v4 | 1.32 | 2.08 | +0.76 | 30/13/7 | 40/1/9 |
| improved-v5 | 0.16 | 1.22 | +1.06 | 17/19/14 | 31/5/14 |
| improved-v6 | 0.18 | 1.2 | +1.02 | 18/19/13 | 31/5/14 |

Scalar-tuned deltas across paired development opponents: `9` better, `0` worse, `0` tied.
Decision: keep `improved-tuned` as a scalar/config baseline only. It is not counted as a structural policy improvement and future structural edits must beat it before holdout.

Latest structural attack candidate versus scalar/config baseline (`9000..9049`):

| Opponent | Improved-tuned mean | Attack mean | Delta | Tuned W/L/D | Attack W/L/D |
| --- | ---: | ---: | ---: | --- | --- |
| builtin | -0.44 | -0.3 | +0.14 | 6/23/21 | 7/18/25 |
| random | 4.66 | 4.8 | +0.14 | 50/0/0 | 50/0/0 |
| initial | 4.56 | 4.7 | +0.14 | 50/0/0 | 50/0/0 |
| improved-v0 | 4.6 | 4.74 | +0.14 | 50/0/0 | 50/0/0 |
| improved-v2 | 4.38 | 4.36 | -0.02 | 49/1/0 | 49/1/0 |
| improved-v3 | 2.38 | 2.62 | +0.24 | 42/1/7 | 46/1/3 |
| improved-v4 | 2.08 | 2.16 | +0.08 | 40/1/9 | 40/3/7 |
| improved-v5 | 1.22 | 1.08 | -0.14 | 31/5/14 | 30/8/12 |
| improved-v6 | 1.2 | 1.06 | -0.14 | 31/5/14 | 30/8/12 |

Attack candidate deltas across paired development opponents: `6` better, `3` worse, `0` tied.
Decision: keep `attack` as a partial structural candidate only. It is not promoted over `improved-tuned` because it remains below `baseline-rnn` on built-in development seeds and regresses nearest archived opponents.

Joint attack scalar search (`9000..9049`, development only): a follow-up threshold/gain search found a built-in-specific candidate at mean `-0.10` with W/L/D `11/13/26`, narrowing the same-seed `baseline-rnn` gap to `0.22`, but the no-ledger opponent-pool check was worse or tied against every non-built-in opponent. It is documented as a failed/partial scalar search and is not promoted.

Low-receive teacher/scalar follow-up (`9000..9049`, development only): a teacher-action diagnostic found many low own-side and near-net loss windows where the RNN would jump, but targeted `LowDriveFinish` and `NetVerticalBlock` structural probes tied or worsened the fixed short screen. A bounded 98-config scalar follow-up again topped out at mean `-0.02`, W/L/D `9/12/29`, leaving a `0.14` built-in gap to `baseline-rnn`; no candidate was promoted.

Latest rally-serve candidate development matrix (`9000..9049`):

| Opponent | Rally-serve mean | W/L/D | Steps |
| --- | ---: | --- | ---: |
| builtin | 0.14 | 13/8/29 | 150000 |
| random | 4.74 | 50/0/0 | 38217 |
| initial | 4.68 | 50/0/0 | 44634 |
| improved-v0 | 4.7 | 50/0/0 | 43242 |
| improved-v2 | 4.38 | 49/1/0 | 76391 |
| improved-v3 | 2.98 | 48/0/2 | 138122 |
| improved-v4 | 2.34 | 44/0/6 | 143814 |
| improved-v5 | 1.16 | 32/7/11 | 149716 |
| improved-v6 | 1.22 | 32/7/11 | 149716 |
- Same-seed built-in comparator result: `rally-serve` mean `0.14` versus `baseline-rnn` mean `0.12`; development delta `0.02`.
- Recorded archive-pool caveat: `rally-serve` versus `improved-v5` mean `1.16` compared with `improved-tuned` versus `improved-v5` mean `1.22`; delta `-0.06`.
Final-only holdout decision: `rally-serve` remains an archived structural-plus-scalar candidate, but it is not promoted because it failed to beat `baseline-rnn` on generation-4 built-in holdout.

Latest parallel rally-serve development pass (`9000..9049`, no holdout/audit):
- Scalar/config search around `rally-serve` screened 53 candidates on `9000..9015` and full-checked the reference plus top candidates on `9000..9049`; no candidate beat the current `0.14` built-in mean, and tied variants added losses.
- Stacked-history `grounded_low_receive` probes tied the current built-in result at best; the branch remained sparse and outcome-neutral.
- Stacked rear-wall probes tied or regressed; broad post-bounce/hold modes were harmful, and exact `rear_wall_low_jump` action swaps were neutral.
- Trace diagnostics show `rally-serve` cuts `attack` point losses from `32` to `18`, but it still wins fewer built-in matches than `baseline-rnn` (`13` versus `18`) and relies more on draws (`29` versus `20`).
- Pre-holdout robustness evidence supported freezing `rally-serve`, with the recorded caveat that it regressed versus `improved-tuned` on `improved-v5` by `-0.06` mean.
- Decision from the parallel pass: no new policy/config/test promotion; keep `rally-serve` frozen and do not tune on holdout or audit seeds.
- Minimum known new development-only cost from that pass: `6,540,000` environment steps, excluding unreported LLM token cost.
- Final-only holdout now supersedes the pre-holdout freeze recommendation: `rally-serve` failed to beat `baseline-rnn` on built-in holdout, so no generation-4 policy is promoted.
- Additional stacked low-receive probe: `stacked_low_101_wide` improved `improved-v5/v6` by `+0.04` on full generation-4 development seeds, but regressed built-in from `0.14` to `0.04` and fell below `baseline-rnn` (`0.12`), so no policy edit was promoted.
- Additional parallel5 diagnostics on generation-4 development seeds: scalar/config tuning improved `attack` to `-0.06` built-in full-dev mean but stayed below `baseline-rnn` and `rally-serve`; grounded-low-receive variants tied at best, the rear-wall low-close jump tied built-in while regressing `improved-v5/v6`, and the trace pass again pointed to low own-side/rear-wall recovery as the gap. No maintained edit was promoted.
- Additional parallel6 diagnostics on generation-4 development seeds: scalar/config tuning found `low_x_0.52` as a fixed-pool-checked `rally-serve` variant with built-in mean `0.18`; it is now exposed as `rally-serve-low-x52` for auditability, but it is scalar/config evidence rather than structural progress. Grounded-low-receive history probes tied the fixed pool without closing the hard-opponent RNN gap; rear-wall press probes repeated the small built-in-gain plus archived-regression pattern; the robustness note kept the fixed-pool gap to `baseline-rnn` explicit, and trace diagnostics again showed `rally-serve` improving `attack` mostly through loss-to-draw conversion. No holdout or audit seeds were opened.

Latest current `improved` development matrix after rear_wall_low_jump:

| Opponent | Mean | W/L/D | Steps |
| --- | ---: | --- | ---: |
| builtin | -2.24 | 1/43/6 | 145800 |
| random | 4.5 | 50/0/0 | 34145 |
| initial | 4.5 | 50/0/0 | 38308 |
| improved-v0 | 4.48 | 50/0/0 | 36877 |
| improved-v2 | 4.16 | 50/0/0 | 58942 |
| improved-v3 | 1.94 | 35/7/8 | 134546 |
| improved-v4 | 1.32 | 30/13/7 | 141875 |
| improved-v5 | 0.16 | 17/19/14 | 146970 |
| improved-v6 | 0.18 | 18/19/13 | 146402 |
- Same-seed built-in neural gap after rear_wall_low_jump: `baseline-rnn` mean `0.12` versus `improved` mean `-2.24`; remaining gap `2.36`.
- Same-seed scalar-tuned built-in gap: `baseline-rnn` mean `0.12` versus `improved-tuned` mean `-0.44`; remaining gap `0.56`.
- Archive regression check: current `improved` versus frozen `improved-v4` mean `1.32` on development seeds; this preserves the pre-edit policy as an opponent.

Planner and teacher-assisted built-in development checks (`9000..9049`):

| Policy | Mean | W/L/D | Steps | Decision |
| --- | ---: | --- | ---: | --- |
| planner | -4.74 | 0/50/0 | 33811 | do not promote; below paired improved baseline |
| teacher-assisted | -4.78 | 0/50/0 | 30248 | do not promote; below paired improved baseline |

## Generation-5 Development Attempt

Generation-5 is fresh post-generation-4 development evidence only. It predeclares new development, holdout, and audit seeds after the generation-4 holdout failure and starts with the `net-pressure` structural probe.
- Generation-5 protocol JSON: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/configs/generation_5_protocol.json`
- Generation-5 protocol report: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/reports/generation_5_protocol.md`
- Generation-5 net-pressure note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_5_net_pressure_attempt.md`
- Generation-5 fixed-pool comparator note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_5_fixed_pool_comparator.md`
- Generation-5 hard-opponent trace/probe note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_5_hard_opponent_trace_and_probe.md`
- Generation-5 post-contact comparison note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_5_post_contact_comparison.md`
- Generation-5 aggressive pressure and brace probe note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_5_aggressive_pressure_and_brace_probe.md`
- Generation-5 stacked followthrough and posture probe note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_5_stacked_followthrough_and_posture_probe.md`
- Generation-5 phase-pressure probe note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_5_phase_pressure_probe.md`
- Generation-5 teacher-serve probe note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_5_teacher_serve_probe.md`
- Generation-5 context-reset probe note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_5_context_reset_probe.md`
- Generation-5 rally-setup probe note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_5_rally_setup_probe.md`
- Generation-5 contact-timing probe note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_5_contact_timing_probe.md`
- Generation-5 approach-quality probe note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_5_approach_quality_probe.md`
- Generation-5 contact-quality probe note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_5_contact_quality_probe.md`
- Generation-5 position/posture probe note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_5_position_posture_probe.md`
- Generation-5 planner-takeover probe note: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/notes/generation_5_planner_takeover_probe.md`
- Generation-5 ledger: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_5_trials.jsonl`
- Generation-5 summary: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_5_summary.csv`
- Generation-5 final holdout artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_g5_final.json` is not present.
- Generation-5 ledger rows: `40`
- Generation-5 split counts: `{'dev': 40}`
- Generation-5 pass/fail counts: `{'pass': 40}`
- Generation-5 holdout rows are absent; holdout seeds `13000..13049` remain sealed, and audit seeds `14000..14049` remain unused.

Generation-5 built-in development comparison (`12000..12049` unless noted):

| Policy | Episodes | Mean | W/L/D | Steps |
| --- | ---: | ---: | --- | ---: |
| improved-tuned | 50 | -0.74 | 6/28/16 | 150000 |
| attack | 50 | -0.4 | 6/20/24 | 150000 |
| rally-serve | 50 | -0.28 | 7/20/23 | 150000 |
| post-contact | 50 | -0.32 | 6/21/23 | 150000 |
| baseline-rnn | 50 | -0.18 | 18/19/13 | 149774 |
| net-pressure | 50 | -0.06 | 11/14/25 | 150000 |
- Built-in development comparator result: `net-pressure` mean `-0.06` versus `baseline-rnn` mean `-0.18`; development delta `0.12`.
- Built-in development heuristic delta: `net-pressure` mean `-0.06` versus `rally-serve` mean `-0.28`; development delta `0.22`.
- Additional teacher-serve macro probe on generation-5 development seeds: `serve_110_10` improved several hard archived short-screen rows, but the full `12000..12049` fixed-pool check regressed built-in from `-0.06` to `-0.12`, regressed `improved-v2/v3`, and remained far below `baseline-rnn` on hard archived opponents. No maintained edit was promoted and holdout/audit stayed sealed.
- Additional context-reset macro probe on generation-5 development seeds: after fixing an initially inert single-frame context detector, `ctx_any_low_110_10` reached the best built-in development mean so far (`-0.02`) but regressed most fixed-pool archived opponents versus `net-pressure` and remained far below `baseline-rnn` on hard rows. No maintained edit was promoted and holdout/audit stayed sealed.
- Additional rally-setup structural/history probe on generation-5 development seeds: post-own-contact front-anchor phases fired on the fixed short screen, but preserved only the built-in row, regressed `improved-v3/v4`, left `improved-v5/v6` unchanged, and remained far below `baseline-rnn`. No maintained edit was promoted and holdout/audit stayed sealed.
- Additional contact-timing diagnostic/probe on generation-5 development seeds: low front-court traces showed `net-pressure` already jumps on most terminal low-contact frames, while narrow `001`/back-jump/base-jump overrides fired only four frames and tied the reference table. No maintained edit was promoted and holdout/audit stayed sealed.
- Additional approach-quality diagnostic/probe on generation-5 development seeds: eight-frame pre-contact traces showed `net-pressure` farther behind the ball than `baseline-rnn`, but early-jump copies collapsed performance, broad no-jump approach rules were mixed or harmful, and a far-behind follow-up only nudged `improved-v5/v6` while regressing built-in and `improved-v3/v4`. No maintained edit was promoted and holdout/audit stayed sealed.
- Additional contact-quality structural/history probe on generation-5 development seeds: recent-contact gates and `110`/`111` brace substitutions were active, but hard-tail nudges came with built-in or `improved-v3/v4` regressions and remained far below `baseline-rnn`. No full-pool expansion, maintained edit, holdout, or audit run was promoted.
- Additional position/posture scalar-config probe on generation-5 development seeds: front-shifted home anchors preserved or nudged some early archived rows, but the harder-tail gains came with built-in or `improved-v3/v4` regressions and remained far below `baseline-rnn`. No full-pool expansion, maintained config, holdout, or audit run was promoted.
- Additional planner-takeover structural probe on generation-5 development seeds: safe/grounded/wide transient planner delegation fired on the short screen but sharply regressed built-in and hard archived rows, while strict/net-clear variants were inert ties. No full-pool expansion, maintained edit, holdout, or audit run was promoted.

Generation-5 fixed development opponent-pool comparison:

| Opponent | net-pressure | baseline-rnn | rally-serve | post-contact | net-pressure minus baseline-rnn | net-pressure minus rally-serve | post-contact minus baseline-rnn |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| builtin | -0.06 11/14/25 150000 | -0.18 18/19/13 149774 | -0.28 7/20/23 150000 | -0.32 6/21/23 150000 | 0.12 | 0.22 | -0.14 |
| random | 4.9 50/0/0 38968 | 4.88 50/0/0 29345 | 4.9 50/0/0 38374 | 4.9 50/0/0 38374 | 0.02 | 0 | 0.02 |
| initial | 4.86 50/0/0 46151 | 4.86 50/0/0 32337 | 4.88 50/0/0 45420 | 4.88 50/0/0 45420 | 0 | -0.02 | 0.02 |
| improved-v0 | 4.84 50/0/0 45461 | 4.86 50/0/0 32042 | 4.88 50/0/0 44740 | 4.88 50/0/0 44740 | -0.02 | -0.04 | 0.02 |
| improved-v2 | 4.68 50/0/0 69296 | 4.8 50/0/0 53053 | 4.66 50/0/0 69999 | 4.66 50/0/0 69690 | -0.12 | 0.02 | -0.14 |
| improved-v3 | 3.08 48/1/1 140453 | 4.24 49/0/1 116019 | 2.84 46/1/3 137950 | 2.84 46/1/3 137950 | -1.16 | 0.24 | -1.4 |
| improved-v4 | 2.56 45/2/3 142939 | 3.7 48/0/2 132117 | 2.38 44/3/3 143145 | 2.38 44/3/3 143145 | -1.14 | 0.18 | -1.32 |
| improved-v5 | 1.2 34/7/9 149883 | 2.38 43/1/6 142995 | 1.32 35/5/10 149883 | 1.32 35/5/10 149883 | -1.18 | -0.12 | -1.06 |
| improved-v6 | 1.22 34/7/9 149011 | 2.4 43/1/6 142777 | 1.28 35/5/10 150000 | 1.28 35/5/10 150000 | -1.18 | -0.06 | -1.12 |
- Fixed-pool neural comparison: `net-pressure` is better than `baseline-rnn` on `2` opponents, tied on `1`, and worse on `6` across the recorded fixed pool.
- Fixed-pool heuristic comparison: `net-pressure` is better than `rally-serve` on `4` opponents, tied on `1`, and worse on `4` across the recorded fixed pool.
- Fixed-pool post-contact neural comparison: `post-contact` is better than `baseline-rnn` on `3` opponents, tied on `0`, and worse on `6` across the recorded fixed pool.
- Promotion recommendation: do not open generation-5 holdout. The fixed-pool comparator rows are now present, and neither `net-pressure` nor `post-contact` beats the neural comparator across the harder archived opponents.
- Additional generation-5 failed direction: aggressive low-contact jump/brace rules and brace-serve macros were screened on `12000..12015`; broad pressure collapsed, brace variants either regressed built-in or became no-ops, and no candidate justified a maintained policy edit.
- Additional generation-5 mixed/failed direction: front-low recovery, stacked followthrough, and opponent-posture gated low-pressure probes were screened on development seeds; the best full-dev posture gate only nudged `improved-v5/v6` while regressing other fixed-pool rows, so no maintained policy edit was promoted.
- Additional generation-5 mixed direction: phase-gated opponent-side low pressure improved some hard archived rows, with `phase_two_frame` moving built-in by `+0.04` and `improved-v5/v6` by `+0.10/+0.12`, but it regressed `improved-v2/v3` and stayed far below `baseline-rnn`; no maintained policy edit was promoted.

## External Critic

Claude Code CLI critic artifacts are external advisory context. They can propose next directions, but they are not benchmark evidence and do not change promotion status unless followed by ledgered code/config/test edits.
The critic also writes a reusable OMX copy under `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/.omx/artifacts` unless `--no-omx-artifact` is supplied.

No Claude critic artifacts recorded yet in `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/reports/critic`.
Use `make slimevolley-critic ARGS="--dry-run"` to preview the prompt without sending data externally.
Use `make slimevolley-critic ARGS="--allow-external-claude"` only when external Claude review is intentional.

## Scalar Search Baseline

Recorded scalar-search evaluation rows: 32
- Best config artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/search_best_dev.json`
- Selection score: `0.0875`
- Opponents: `builtin, random, initial, improved-v0`
- Config: `{"contact_x_window": 0.18, "home_x": 1.05, "landing_horizon": 0.3}`
- Opponent means: `builtin=-4.95, improved-v0=1.2, initial=1.35, random=2.75`

## Neural/RL Comparator

The `baseline-rnn` policy is slimevolleygym's shipped 120-parameter RNN policy. It is included as a labeled neural comparator, not as an interpretable heuristic improvement.
- `baseline-rnn` vs `builtin`: mean `-0.2`, wins `2`, losses `6`, draws `12`, steps `60000`.
- `baseline-rnn` vs `builtin`: mean `0.34`, wins `19`, losses `11`, draws `20`, steps `150000`.
- `baseline-rnn` vs `builtin`: mean `0.12`, wins `18`, losses `12`, draws `20`, steps `150000`.
- `baseline-rnn` vs `builtin`: mean `0.12`, wins `18`, losses `12`, draws `20`, steps `150000`.
- `baseline-rnn` vs `builtin`: mean `0.12`, wins `18`, losses `12`, draws `20`, steps `150000`.
- `baseline-rnn` vs `builtin`: mean `-0.18`, wins `18`, losses `19`, draws `13`, steps `149774`.
- `baseline-rnn` vs `improved-v0`: mean `4.9`, wins `20`, losses `0`, draws `0`, steps `12761`.
- `baseline-rnn` vs `improved-v0`: mean `4.86`, wins `50`, losses `0`, draws `0`, steps `32042`.
- `baseline-rnn` vs `improved-v2`: mean `4.8`, wins `50`, losses `0`, draws `0`, steps `53053`.
- `baseline-rnn` vs `improved-v3`: mean `4.24`, wins `49`, losses `0`, draws `1`, steps `116019`.
- `baseline-rnn` vs `improved-v4`: mean `3.7`, wins `48`, losses `0`, draws `2`, steps `132117`.
- `baseline-rnn` vs `improved-v5`: mean `2.38`, wins `43`, losses `1`, draws `6`, steps `142995`.
- `baseline-rnn` vs `improved-v6`: mean `2.4`, wins `43`, losses `1`, draws `6`, steps `142777`.
- `baseline-rnn` vs `initial`: mean `4.85`, wins `20`, losses `0`, draws `0`, steps `12169`.
- `baseline-rnn` vs `initial`: mean `4.86`, wins `50`, losses `0`, draws `0`, steps `32337`.
- `baseline-rnn` vs `random`: mean `4.9`, wins `20`, losses `0`, draws `0`, steps `10717`.
- `baseline-rnn` vs `random`: mean `4.88`, wins `50`, losses `0`, draws `0`, steps `29345`.
- Built-in-opponent gap on dev seeds: `baseline-rnn` mean `-0.18` versus structural heuristic mean `-2.24`.

## Cost Accounting

Environment-interaction cost is reported separately from research/agent maintenance cost. Episodes and environment steps measure sample use; ledger rows, code edits, agent iterations, tests, and wall time measure the surrounding coding-agent process. This table includes generation-2, generation-3, generation-4, and generation-5 rows when separate generation ledgers are present.

| Metric | Value |
| --- | ---: |
| Generation-1 ledger rows / evaluation records | 186 |
| Generation-2 ledger rows / evaluation records | 114 |
| Generation-3 ledger rows / evaluation records | 303 |
| Generation-4 ledger rows / evaluation records | 155 |
| Generation-5 ledger rows / evaluation records | 40 |
| Total ledger rows / evaluation records | 798 |
| Passing rows | 795 |
| Failed or partial rows | 3 |
| Episodes recorded | 34274 |
| Environment steps recorded | 40335878 |
| Wall-clock seconds recorded | 2797.97 |
| Max recorded agent iterations | 17 |
| Sum of recorded code-edit counts | 7831 |
| Scalar-search rows | 171 |
| Scalar-search episodes | 7590 |
| Scalar-search environment steps | 6986933 |

Sample cost by evidence split:

| Ledger | Split | Rows | Episodes | Environment steps | Wall-clock seconds |
| --- | --- | ---: | ---: | ---: | ---: |
| generation-1 | dev | 152 | 3040 | 2531067 | 132.091 |
| generation-1 | holdout | 25 | 1250 | 1046530 | 53.7986 |
| generation-1 | smoke | 9 | 18 | 11531 | 0.73495 |
| generation-2 | dev | 89 | 4450 | 3882971 | 252.83 |
| generation-2 | holdout | 25 | 1250 | 1118053 | 71.5945 |
| generation-3 | dev | 273 | 13650 | 13161072 | 885.559 |
| generation-3 | holdout | 30 | 1500 | 1531989 | 102.474 |
| generation-4 | dev | 92 | 4000 | 7774257 | 550.389 |
| generation-4 | holdout | 63 | 3150 | 5159074 | 398.012 |
| generation-5 | dev | 40 | 1966 | 4119334 | 350.483 |

Mutually exclusive cost by comparison group:

| Group | Rows | Episodes | Environment steps | Wall-clock seconds | Code-edit count sum |
| --- | ---: | ---: | ---: | ---: | ---: |
| random baseline | 78 | 3300 | 2214892 | 156.061 | 1026 |
| initial handwritten heuristic | 84 | 3360 | 2609668 | 167.201 | 1055 |
| agent-maintained structural heuristics | 416 | 17724 | 25573018 | 1815.51 | 4515 |
| scalar/config search baseline | 169 | 7460 | 5625043 | 353.243 | 826 |
| packaged RNN comparator | 42 | 1980 | 3384055 | 225.548 | 409 |
| harness, diagnostics, and other rows | 9 | 450 | 929202 | 80.4007 | 0 |

The packaged RNN comparator is evaluated here, but its original training sample cost is external to this ledger and is therefore not comparable to the local heuristic-maintenance sample budget.

- Generation-1 rows by split: `{'dev': 152, 'holdout': 25, 'smoke': 9}`
- Generation-2 rows by split: `{'dev': 89, 'holdout': 25}`
- Generation-3 rows by split: `{'dev': 273, 'holdout': 30}`
- Generation-4 rows by split: `{'dev': 92, 'holdout': 63}`
- Generation-5 rows by split: `{'dev': 40}`
- Rows by change type across all ledgers: `{'bug fix': 5, 'evaluation-harness change': 469, 'invalid/rolled back': 4, 'logging/diagnostics': 2, 'logging/diagnostics change': 25, 'neural/RL baseline': 15, 'scalar/config tuning': 171, 'structural policy improvement': 107}`
- Tests recorded in ledger rows: `.venv/bin/python -m pytest tests/test_slimevolley_optional.py, PYTHONPATH=. .venv/bin/python -m pytest tests, PYTHONPATH=. .venv/bin/python -m pytest tests/test_slimevolley_optional.py, PYTHONPATH=. .venv/bin/python -m pytest tests/test_slimevolley_optional.py -q, PYTHONPATH=. .venv/bin/python -m pytest tests/test_slimevolley_optional.py tests/test_policies.py, PYTHONPATH=. .venv/bin/python -m pytest tests/test_slimevolley_optional.py::test_slimevolley_policy_factory_actions_are_multibinary tests/test_slimevolley_optional.py::test_slimevolley_attack_candidate_golden_behavior tests/test_slimevolley_optional.py::test_slimevolley_opponent_pool_has_required_baselines -q, PYTHONPATH=. python3 -m pytest tests, PYTHONPATH=. python3 -m pytest tests/test_slimevolley_optional.py, PYTHONPATH=. python3 -m pytest tests/test_slimevolley_optional.py tests/test_policies.py, make custom-verify ENV=SlimeVolley-v0, make verify, pytest, python3 -m hl_benchmark.slimevolley.audit --format json, python3 -m pytest tests/test_slimevolley_optional.py, python3 -m pytest tests/test_slimevolley_optional.py -q, python3 -m pytest tests/test_slimevolley_optional.py::test_slimevolley_golden_behavior tests/test_slimevolley_optional.py::test_slimevolley_archives_stay_frozen, python3-m-pytest-tests/test_slimevolley_optional.py`
- Explicit test pass/fail statuses: `{'not_recorded': 186, 'pass': 612}`
- LLM token/call accounting: `not exposed by local runtime`
- Code-edit counts are recorded per ledger row and may overcount one shared edit evaluated across multiple opponents.
- Hardware was not separately exposed by the local runtime; package and platform metadata are preserved in each ledger row.

## Hypothesis Evidence Verdict

Primary evidence source for this verdict: `generation-4 holdout` (final-only; not available for further tuning).
- `improved` versus `initial` across common `generation-4 holdout` opponents: 9 better, 0 worse, 0 tied; mean score delta `4.57778`.
- Excluding the built-in opponent, `improved` beat `initial` on 8/8 common `generation-4 holdout` opponents.
- Built-in opponent remains unsolved: `initial` mean `-4.8`, `improved` mean `-2.66`.
- Neural comparator gap on built-in opponent: `baseline-rnn` mean `-0.12` versus `improved` mean `-2.66`.
- Current generation-4 candidate gap on built-in opponent: `rally-serve` mean `-0.22` versus `baseline-rnn` mean `-0.12`; delta `-0.1`.
- Supports the hypothesis: the agent-maintained heuristic produced interpretable structural archives and improved robustness against random, initial, and archived heuristic opponents.
- Weakens the hypothesis: the maintained heuristic failed to beat the packaged RNN on the built-in final holdout, development gains did not generalize cleanly, and some late structural changes tied their predecessors.
- Overall verdict for this SlimeVolley run: weak or mixed support, not a deep-RL-comparable result.

## Anti-Cheating And Limitations

- The ledger is append-only; failed and partial rows remain visible rather than being deleted.
- Scalar/config search is labeled separately from structural policy edits.
- Archived heuristic opponents are preserved as `improved-v0`, `improved-v1`, `improved-v2`, `improved-v3`, `improved-v4`, `improved-v5`, and `improved-v6`.
- Duplicate development rows appear because diagnostics and paired comparisons were intentionally logged; the ledger is an audit trail, not a set of independent benchmark replicas.
- LLM call and token counts were unavailable from the local runtime and are explicitly recorded that way.
- The neural comparator is the packaged SlimeVolley RNN baseline, not a locally trained deep RL agent.
- holdout seeds `1000..1049`, generation-2 holdout seeds `4000..4049`, generation-3 holdout seeds `7000..7049`, generation-4 holdout seeds `10000..10049` have been evaluated once. This report can interpret those results, but policy tuning on any consumed range would invalidate the evidence.
- Generation-4 audit seeds `11000..11049` remain reserved; because generation-4 holdout is consumed, further policy research should predeclare a fresh generation instead of tuning from generation-4 final evidence.
- Noncanonical legacy change_type values are still present append-only: `logging/diagnostics, neural/RL baseline`.

## Current Conclusion

Generation-4 holdout evidence exists and is final-only: do not use seeds `1000..1049`, `4000..4049`, `7000..7049`, or `10000..10049` for further policy tuning, and keep generation-4 audit seeds `11000..11049` reserved. The rally-serve candidate beat the packaged RNN on built-in development seeds but failed to beat it on sealed built-in holdout. On built-in holdout, `rally-serve` mean `-0.22` versus `baseline-rnn` mean `-0.12`, delta `-0.1`. A later generation-5 development-only structural probe, `net-pressure`, reached built-in mean `-0.06`; this is not holdout evidence and must stay on fresh development protocol rails. This SlimeVolley run therefore weakens the final generalization claim, though generation-5 has reopened a clean development path toward a better heuristic.

## Next Steps

1. Treat consumed holdout seeds `1000..1049`, `4000..4049`, `7000..7049`, and `10000..10049` as frozen final evidence; do not tune against any consumed holdout range.
2. Continue generation-5 only on development seeds `12000..12049`; keep generation-5 holdout `13000..13049` and audit `14000..14049` unopened.
3. Do not promote `net-pressure`: the fixed development pool shows it beats `baseline-rnn` on built-in mean but trails the neural comparator on the harder archived opponents.
4. Hard-opponent trace/probe diagnostics are now recorded; the tested front-net, brace-action, and contact-quality rules were mixed or harmful. The next generation-5 development edit should require a more specific multi-frame contact-quality detector before rerunning the fixed development pool.

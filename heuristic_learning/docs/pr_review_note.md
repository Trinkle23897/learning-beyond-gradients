# PR Reviewer Note: Environment Registry and SlimeVolley Expansion

This note is for reviewing the current heuristic-learning benchmark expansion without reading every source file first.

## Scope

This work adds a scalable structure for adding more RL environments while keeping SlimeVolley as the first custom environment.

Main surfaces:

- `hl_benchmark/environments/`: auto-discovered environment registrations with `active`, `custom_active`, and `planned` statuses.
- `hl_benchmark/policies/`: per-environment transparent policy modules plus local `SUPPORTED_POLICY_NAMES`, `make_policy()` builders, and `candidate_configs()` scalar-search grids.
- `hl_benchmark/custom_envs/`: preferred package root for custom harnesses; SlimeVolley now has the first registered bridge at `hl_benchmark/custom_envs/slimevolley/`.
- `hl_benchmark/slimevolley/`: implementation and compatibility root for the first custom active environment.
- `experiments/<env_slug>/`: per-environment artifact roots for configs, results, reports, and notes.

SlimeVolley is registered through `hl_benchmark.custom_envs.slimevolley`, which delegates to `hl_benchmark.slimevolley` for compatibility. New custom environments should scaffold under `hl_benchmark.custom_envs.<env_slug>`.

## Review Order

1. Registry model: `hl_benchmark/environments/base.py`, `hl_benchmark/environments/__init__.py`, and `hl_benchmark/registry.py`.
2. Scaffold helpers and gates: `hl_benchmark/artifacts.py`, `hl_benchmark/custom.py`, `Makefile`.
3. SlimeVolley custom harness: `hl_benchmark/slimevolley/` and `hl_benchmark/policies/slimevolley.py`.
4. Evidence artifacts: `experiments/slimevolley/results/`, `experiments/slimevolley/reports/final_report.md`, and `experiments/slimevolley/reports/requirements_audit.md`.
5. Regression tests: `tests/test_environment_registry.py` and `tests/test_slimevolley_optional.py`.

## Verification Commands

From `heuristic_learning/`:

```bash
make verify
make slimevolley-verify
make list-envs
make check-planned-envs ARGS="--format json"
make check-promotion ENV=SlimeVolley-v0 ARGS="--format json"
make check-promotions ARGS="--format json"
make check-env ENV=SlimeVolley-v0 ARGS="--format json"
```

Last local verification in this working tree:

- `make verify`: pass, including 148 pytest tests and the registry/artifact gates.
- `make custom-run ENV=SlimeVolley-v0 ARGS="--format json"`: pass; generic custom dispatcher lists SlimeVolley commands including `verify`.
- `make custom-run ENV=SlimeVolley-v0 CUSTOM_COMMAND=summary ARGS="--format json"`: pass; generic custom dispatcher routes SlimeVolley summary and reports 186 rows.
- `make custom-verify ENV=SlimeVolley-v0`: pass; shared custom verifier runs readiness, artifact-layout, summary, SlimeVolley-declared contact diagnostics, generation-3 and generation-4 protocol refreshes, report, performance-report, generation-2 diagnosis, and audit gates.
- `make slimevolley-verify`: pass, with 186 generation-1 SlimeVolley ledger rows, 186 append-only test-status amendment rows, 186 summary rows, 25 generation-1 holdout rows, 114 generation-2 ledger rows, 25 generation-2 holdout rows, 303 generation-3 ledger rows, 30 generation-3 holdout rows, contact diagnostics, artifact/source hashes, and machine-readable requirement status counts (`requirements_audit_status_counts`), partial-row names (`requirements_audit_partial_rows`), completion state (`requirements_audit_completion_state`), recommendation (`requirements_audit_completion_recommendation`), partial-row details (`requirements_audit_partial_row_details`), partial-row classifications (`requirements_audit_partial_row_classifications`), and ledger-amendment counts (`ledger_amendment_counts`).

## Important Guardrails

- `make verify` is intentionally non-evaluative. It must not run evaluations, searches, report regeneration, SlimeVolley commands, or holdout logic.
- `make slimevolley-verify` refreshes SlimeVolley summary/report/audit artifacts plus contact diagnostics and generation protocol/report artifacts, but does not run new holdout evaluation.
- Planned environments are visible through `planned_env_ids()` and `make check-envs`, but strict planned scaffold CI should use `make check-planned-envs`; promotion review should use `make check-promotion ENV=<EnvId>` or aggregate `make check-promotions`.
- Planned env readiness validates artifact scaffolds, skipped pytest scaffold files with matching ENV_ID/MODULE_SLUG and promotion commands, and policy imports. Planned custom envs additionally require importable scaffold harness modules and callable custom command entrypoints, while completed EnvSpec metadata and real harness implementation remain promotion-time gates. Runnable readiness fails if the generated skipped test scaffold was not replaced before promotion; JSON separates `planned_test_scaffold_issues` from `runnable_test_scaffold_issues` while retaining combined `test_scaffold_issues`, and exposes `promotion_ready` plus `promotion_blockers` so scaffold-ready planned envs are not mistaken for promotion-ready envs.
- Holdout rows already exist for SlimeVolley generation-1, generation-2, and generation-3. Future policy work should not tune on seeds `1000..1049`, `4000..4049`, or `7000..7049`; use a fresh predeclared generation-4 protocol if policy behavior changes.

## Known Caveats

- Current registry has no planned envs; planned behavior is covered by temporary-scaffold regression tests.
- SlimeVolley audit warns about append-only noncanonical historical change types: `logging/diagnostics` and `neural/RL baseline`.
- The broader five-environment aggregate benchmark review remains in `results/independent_codex_progress_review.md`; this note focuses on the custom-environment/SlimeVolley expansion.

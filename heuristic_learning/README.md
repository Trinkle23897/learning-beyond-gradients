# Heuristic Learning Benchmark

This subproject implements a minimal, auditable experiment for the
Learning Beyond Gradients / Heuristic Learning hypothesis:

> Can an autonomous coding agent maintain and improve a transparent heuristic
> control system across multiple control environments, while preserving prior
> successes through tests and reporting costs and failures honestly?

The benchmark is intentionally small. It favors reproducibility, fixed seed
ranges, append-only trial records, and readable policy code over impressive
scores.

## Setup

From this directory:

```bash
python3 -m pip install -e .
```

Box2D environments require the `gymnasium[box2d]` extra listed in
`pyproject.toml`. If the local platform cannot install Box2D, the evaluation
commands fail explicitly and record the failure instead of silently dropping the
Box2D tasks.

Optional SlimeVolley dependencies use the legacy Gym API. The upstream
package was developed for Gym 0.19/0.20, so modern pip may need the older build
frontend before installing this extra:

```bash
python3 -m pip install 'pip<24.1' 'setuptools==65.5.0' 'wheel==0.38.4'
python3 -m pip install --no-build-isolation -e '.[slimevolley]'
```

Optional neural/RL baseline dependencies are separate:

```bash
python3 -m pip install -e '.[rl]'
```

The primary pass/fail criterion is the fixed benchmark success target recorded for
each environment. Neural/RL runs are optional secondary comparators and are not
required for the default benchmark.

Optional pretrained SB3 comparators can be evaluated through Hugging Face Hub
when the `.[rl]` extra is installed. These runs are recorded separately from
local training runs in the ledger, for example as `rl-sac-hf`.

## Commands

```bash
make test
make verify
make list-envs
make check-env-layout
make check-env-layout ARGS="--format json"
make check-env ENV=CartPole-v1
make check-promotion ENV=SlimeVolley-v0 ARGS="--format json"
make check-promotions
make check-envs
make check-planned-envs
make check-env ENV=SlimeVolley-v0 ARGS="--format json"
make scaffold-env ENV=NewEnv-v0
make scaffold-env-code ENV=NewEnv-v0
make scaffold-env-tests ENV=NewEnv-v0
make scaffold-generic-env ENV=NewEnv-v0
make scaffold-custom-env ENV=NewAdversarialEnv-v0
make custom-run ENV=SlimeVolley-v0 CUSTOM_COMMAND=summary ARGS="--format json"
make custom-verify ENV=SlimeVolley-v0
make eval-env ENV=CartPole-v1 POLICY=initial SPLIT=dev
make eval-env ENV=CartPole-v1 POLICY=initial SPLIT=smoke ARGS="--env-artifacts"
make eval-all SPLIT=dev
make search MAX_CANDIDATES=32
make search-env ENV=CartPole-v1 MAX_CANDIDATES=8 ARGS="--env-artifacts"
make rl-baseline ENV=CartPole-v1 SPLIT=smoke TRAIN_STEPS=100 ARGS="--env-artifacts"
make summary-env ENV=CartPole-v1
make report-env ENV=CartPole-v1
make audit-env ENV=CartPole-v1
make final-eval
make report
make deepdive-report
make slimevolley-doctor
make slimevolley-audit
make slimevolley-verify
make slimevolley-eval POLICY=initial OPPONENT=builtin SPLIT=smoke
make slimevolley-report
make slimevolley-performance-report
make slimevolley-generation-report
make slimevolley-generation3-report
make slimevolley-protocol
make slimevolley-generation3-protocol
make slimevolley-generation4-protocol
make slimevolley-summary
make slimevolley-search MAX_CANDIDATES=8
make slimevolley-tournament SPLIT=dev
make slimevolley-final-eval
```

`make slimevolley-verify` first runs the SlimeVolley readiness gate, all-runnable-env
readiness gate, and artifact-layout validation. It then regenerates SlimeVolley
derived artifacts and writes `experiments/slimevolley/results/audit_latest.json`
with artifact and source SHA256 hashes.

`make verify` is the default non-evaluation, non-regeneration gate for local review and CI: it
runs runnable readiness, planned-scaffold readiness, artifact-layout checks, and
the pytest suite. Custom environment summary/report/audit and declared
diagnostics/protocol regeneration remains in `make custom-verify ENV=<EnvId>`
or the environment-specific verify target, such as `make slimevolley-verify`,
through `CUSTOM_VERIFY_EXTRA_COMMANDS`. The Makefile sets
`PYTHONPATH=.` so the package can run directly from the subproject checkout.

For a compact PR review map, see `docs/pr_review_note.md`.

## Outputs

The legacy aggregate benchmark writes article-level artifacts to `results/` by default:

- `trials.jsonl`: append-only ledger of every evaluation/search trial.
- `summary.csv`: regenerated table summarizing all ledger entries.
- `final_report.md`: Markdown report generated from the ledger and environment
  registry.
- `agent_deepdive_report.md`: generated audit of how the agent iterated,
  including failures, cost accounting, structural/scalar separation, and caveats.
- `heuristic_policy_explainer.md`: high-level visual explanation of how each
  transparent environment policy works.

Every runnable environment has a reserved artifact root under
`experiments/<env_slug>/`. Use `make eval-env ... ARGS="--env-artifacts"`,
`make search-env ... ARGS="--env-artifacts"`, or
`make rl-baseline ... ARGS="--env-artifacts"` when a generic single-environment
run should write `trials.jsonl` and `summary.csv` under that per-environment root
instead of the legacy aggregate ledger. Use `make summary-env ENV=<EnvId>` to
regenerate a generic env summary from that per-environment ledger,
`make report-env ENV=<EnvId>` to write a report scoped to that environment at
`experiments/<env_slug>/reports/final_report.md`, and
`make audit-env ENV=<EnvId>` to write a non-evaluation artifact audit at
`experiments/<env_slug>/results/audit_latest.json`. The generic audit expects the
per-environment ledger, summary, and scoped report to exist first; on scaffold-only
roots it fails with explicit missing-artifact issues. New standalone environments should keep their own artifacts there:

```text
experiments/<env_slug>/
  README.md
  configs/.gitkeep
  results/.gitkeep
  reports/.gitkeep
  notes/.gitkeep
```

Generated after evaluation/report commands:

```text
experiments/<env_slug>/
  results/trials.jsonl
  results/summary.csv
  results/audit_latest.json     # generic per-env artifact audit when generated
  results/round_robin_dev.json   # for adversarial/tournament envs
  reports/final_report.md
  configs/generation_2_protocol.json # predeclared generation-2 seed/opponent protocol when maintained
  results/generation_2_trials.jsonl # append-only generation-2 ledger when maintained
  results/generation_2_summary.csv # summary of the generation-2 ledger when maintained
  results/search_best_g2_dev.json # generation-2 scalar-search artifact when maintained
  results/round_robin_g2_dev.json # generation-2 tournament artifact when maintained
  results/holdout_g2_final.json # generation-2 final-only holdout artifact when generated
  reports/performance_deepdive.md # generated score-focused SlimeVolley explanation when maintained
  reports/generation_2_diagnosis.md # generated generation-2 trial/failure diagnosis when maintained
  reports/generation_2_protocol.md # human-readable generation-2 protocol when maintained
  configs/generation_3_protocol.json # predeclared generation-3 seed/opponent protocol when maintained
  results/generation_3_trials.jsonl # append-only generation-3 ledger when maintained
  results/generation_3_summary.csv # summary of the generation-3 ledger when maintained
  results/search_best_g3_dev.json # generation-3 scalar-search artifact when maintained
  results/round_robin_g3_dev.json # generation-3 tournament artifact when maintained
  results/holdout_g3_final.json # generation-3 final-only holdout artifact when generated
  reports/contact_diagnostics_g3_dev.md # generated generation-3 dev trace diagnostic when maintained
  reports/generation_3_diagnosis.md # generated generation-3 trial/failure/holdout diagnosis when maintained
  reports/generation_3_protocol.md # human-readable generation-3 protocol when maintained
  reports/requirements_audit.md  # requirement-by-requirement reviewer traceability when maintained
```

The artifact README must identify the exact environment ID and artifact root;
`make check-env-layout` validates this to catch copied or stale folders.
The JSON form exposes `required_dirs`, `required_files`, and
`required_placeholder_files` for automated review. Required subdirectories keep
`.gitkeep` placeholders so empty artifact roots remain tracked before
evaluations generate files.

Do not delete failed entries from any `trials.jsonl`. If a run is invalid,
append a new entry explaining why.

## Benchmark Suite

Fixed seed splits:

- Development seeds: `0..19`
- Holdout seeds: `1000..1049`
- Audit seeds: `2000..2049`

SlimeVolley also records a separate generation-2 protocol after the original
holdout was consumed:

- Generation-2 development seeds: `3000..3049`
- Generation-2 holdout seeds: `4000..4049`
- Generation-2 audit seeds: `5000..5049`

SlimeVolley holdout ranges `1000..1049`, `4000..4049`, and `7000..7049` are
final-only consumed evidence. The generation-3 audit seeds `8000..8049` remain
reserved for independent checks. Any further SlimeVolley policy-selection work
requires a fresh later-generation protocol with new development, holdout, and
audit seeds.

Primary environments:

- `CartPole-v1`
- `MountainCar-v0`
- `Acrobot-v1`
- `LunarLander-v3`
- `BipedalWalker-v3`

Custom and planned environments use the same registry shape but do not
automatically run in `make eval-all`. `SlimeVolley-v0` is registered as the
first `custom_active` competitive-control environment: it has its own legacy Gym
adapter, opponent protocol, fixed-seed ledger, and report under
`experiments/slimevolley/`, while the aggregate evaluator stays limited to
generic Gymnasium-style environments.

If `BipedalWalker-v3` is unavailable but another Box2D task such as
`CarRacing-v3` is available, document the substitution in the ledger and final
report. If Box2D is unavailable entirely, install the required dependency or
record the failure.

## Policies And Baselines

Each promoted runnable environment has:

- `random`: random action baseline supplied by the shared factory.
- `initial`: simple handwritten heuristic.
- `improved`: structural heuristic revision with explicit detectors, guards,
  modes, or state-machine behavior.
- `tuned`: scalar/config variant used by the search baseline.

`make check-env` enforces that runnable policy modules expose `initial`,
`improved`, and `tuned` so standard eval/search commands do not fail after
promotion.

Scalar search is intentionally separated from structural policy improvement.
`search.py` rejects holdout and audit splits so reserved comparison seeds cannot be used for tuning. Use `make search-env ... ARGS="--env-artifacts"` when a generic scalar-search baseline should keep its ledger, summary, and `search_best_dev.json` under `experiments/<env_slug>/results/`.

## Audit Rules

- Never cherry-pick seeds.
- Never optimize on holdout seeds.
- Record failed or partial trials.
- Keep initial policies callable for comparison.
- Keep policy changes interpretable.
- Report environment steps, wall time, package versions, git hash/diff hash,
  code-edit counts, agent iterations, and unavailable LLM-token fields.

## Adding Another Environment

The repository is split so small Gymnasium-style environments can use the shared
evaluator, while larger or adversarial environments can own custom harness code.
Standard custom harness modules can be run through `make custom-run` and
verified through `make custom-verify`, so each new custom env does not need a
new Makefile target family. `custom-verify` also runs optional `generation_report` and harness-declared `CUSTOM_VERIFY_EXTRA_COMMANDS` before audit when a custom harness provides them. SlimeVolley uses those extra commands to refresh contact diagnostics, generation-3 diagnosis, and generation-2, generation-3, and generation-4 protocol artifacts. SlimeVolley is the first example of the custom path and is registered through `hl_benchmark.custom_envs.slimevolley`; that bridge delegates to the existing `hl_benchmark.slimevolley` implementation so old reproduction commands and imports keep working. New custom scaffolds use `hl_benchmark.custom_envs.<env_slug>`.
The decision guide lives in
`docs/adding_environment.md`; the custom-harness checklist lives in
`docs/custom_environment_template.md`. Keep new environments `planned` until
policy, tests, ledger/report/audit, metadata, and command entrypoints are real;
`make custom-run` and `make custom-verify` are promotion gates for
`custom_active` environments, not scaffold checks.

1. Start from scaffolds unless the environment already has a complete local
   implementation:
   - Generic Gymnasium path: `make scaffold-generic-env ENV=<EnvId>`; this creates the artifact tree, planned registration/policy files, and skipped test scaffold while leaving `REGISTRATION.custom_module` unset. Use `make scaffold-env ENV=<EnvId>`, `make scaffold-env-code ENV=<EnvId>`, or `make scaffold-env-tests ENV=<EnvId>` only when you intentionally want one piece.
   - Custom harness path: `make scaffold-custom-env ENV=<EnvId>`; this sets `REGISTRATION.custom_module` to `hl_benchmark.custom_envs.<env_slug>`.
2. Keep one auto-discovered `REGISTRATION` object in
   `hl_benchmark/environments/<env_slug>.py`. Do not edit
   `hl_benchmark/environments/__init__.py` for normal additions. Use
   `suite_order` for stable listing order, and keep environment IDs, registry
   keys, artifact slugs unique, and custom module roots unique.
3. Add transparent policies under `hl_benchmark/policies/<env_slug>.py`, or reuse
   a generic policy only when the behavior is genuinely environment-independent.
   Each promoted runnable policy module must expose `initial`, `improved`, and `tuned`
   in `SUPPORTED_POLICY_NAMES`; each policy module owns its local
   `make_policy()` builder and `candidate_configs()` scalar-search grid; the shared factory and
   search dispatcher discover them through the environment registration, so normal
   additions should not edit `hl_benchmark/policies/factory.py` or
   `hl_benchmark/search.py`.
4. If the generic evaluator is insufficient, replace the custom-harness
   placeholders with environment-specific `adapter.py`, `evaluate.py`,
   `search.py`, `summarize.py`, `report.py`, `performance_report.py`, and `audit.py` logic. Optional
   modules such as `doctor.py`, `opponents.py`, `tournament.py`, and
   `final_eval.py` can be added when the environment needs them.
5. Add tests for registry metadata, policy action validity, determinism, ledger
   schema, summary/report generation, holdout guardrails, and any
   environment-specific golden behavior.
6. Choose the registration status deliberately:
   - `planned`: metadata and artifact paths exist, but the environment is not runnable yet; scaffold TODO metadata is allowed and reported as not checked until promotion.
   - `custom_active`: runnable through the module root in `REGISTRATION.custom_module`, normally `hl_benchmark.custom_envs.<env_slug>`, excluded from generic `eval-all`, and covered by tests requiring `experiments/<env_slug>/{configs,results,reports,notes}` plus custom `adapter.py`, `evaluate.py`, `search.py`, `summarize.py`, `report.py`, `performance_report.py`, and `audit.py` modules.
   - `active`: included in generic aggregate evaluator commands.
7. Use `benchmark_env_ids()` for generic aggregate envs, `custom_env_ids()` for custom harness envs, `planned_env_ids()` for scaffolded registrations that must not run yet, and `registration_for(<EnvId>)` when tooling needs the artifact slug, policy module, or custom module root.
8. Run `make list-envs` to audit the generic/custom/planned registry split after adding a new environment; `make check-envs` reports both runnable checked environments and the count of planned registry entries. Use `make check-planned-envs` when CI should fail on incomplete planned scaffolds, including missing skipped pytest scaffold files or mismatched scaffold identity markers.
9. Run `make check-env ENV=<EnvId>`,
    `make check-env ENV=<EnvId> ARGS="--format json"`, and
    `make check-promotion ENV=<EnvId>`, and `make check-promotions` before promoting an
    environment. These checks validate imports, artifacts, completed EnvSpec
    metadata, custom-harness modules, callable custom command entrypoints, and
    generated scaffold/TODO markers and unreplaced skipped test scaffolds without running evaluation; the JSON output
    exposes `runnable`, `artifact_issues`, `test_scaffold_issues`,
    `planned_test_scaffold_issues`, `runnable_test_scaffold_issues`,
    `promotion_ready`, `promotion_blockers`, `metadata_issues`,
    `missing_required_policy_names`, and import/entrypoint/scaffold gates for
    automation. Planned envs must have the
    artifact scaffold and same-environment test scaffold markers, and planned custom envs with `REGISTRATION.custom_module`
    must have importable placeholder harness modules with callable command
    entrypoints; EnvSpec metadata is reported as not checked until promotion, while `promotion_blockers` lists what must change before flipping the status.
10. For `custom_active` envs, run `make custom-run ENV=<EnvId>` to list
    implemented standard commands and `make custom-verify ENV=<EnvId>` to run
    readiness, layout, summary, report, performance-report, optional
    `CUSTOM_VERIFY_EXTRA_COMMANDS`, and audit gates. The standard verify chain
    expects `summarize`, `report`, `performance_report`, and `audit` modules
    with callable `main()` functions; `audit` must accept `--output <path>` so
    the latest audit JSON can be written under
    `experiments/<env_slug>/results/audit_latest.json`.
11. Run `make check-env-layout` to validate artifact directories and files for
    every runnable environment, then run `make test`.

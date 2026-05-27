# Adding Benchmark Environments

Use this guide before adding another RL environment to keep the benchmark
auditable as the suite grows.

## Choose The Execution Path

Use the shared generic evaluator when the environment is a normal
Gymnasium-style single-agent task:

```text
hl_benchmark/environments/<env_slug>.py
hl_benchmark/policies/<env_slug>.py
experiments/<env_slug>/
```

The one-shot generic scaffold target is `make scaffold-generic-env ENV=<EnvId>`. It leaves `REGISTRATION.custom_module` unset. Register the environment with status `active` only after it can run through:

```bash
make eval-env ENV=<EnvId> POLICY=initial SPLIT=smoke
make eval-env ENV=<EnvId> POLICY=initial SPLIT=smoke ARGS="--env-artifacts"
make eval-all SPLIT=dev
make search-env ENV=<EnvId> MAX_CANDIDATES=8 ARGS="--env-artifacts"
make rl-baseline ENV=<EnvId> SPLIT=smoke TRAIN_STEPS=100 ARGS="--env-artifacts"
make summary-env ENV=<EnvId>
make report-env ENV=<EnvId>
make audit-env ENV=<EnvId>
```

Use a custom harness when the environment needs legacy Gym compatibility,
multiple agents, opponent pools, tournaments, replay diagnostics, or special
holdout controls:

```text
hl_benchmark/environments/<env_slug>.py
hl_benchmark/policies/<env_slug>.py
hl_benchmark/custom_envs/<env_slug>/adapter.py
hl_benchmark/custom_envs/<env_slug>/evaluate.py
hl_benchmark/custom_envs/<env_slug>/search.py
hl_benchmark/custom_envs/<env_slug>/summarize.py
hl_benchmark/custom_envs/<env_slug>/report.py
hl_benchmark/custom_envs/<env_slug>/performance_report.py
hl_benchmark/custom_envs/<env_slug>/audit.py
experiments/<env_slug>/
```

For a new custom environment, start with `make scaffold-custom-env ENV=<EnvId>` to create the standard artifact tree, planned registration/policy files with `REGISTRATION.custom_module`, skipped test scaffolds, and placeholder `hl_benchmark/custom_envs/<env_slug>/` modules.

Register it with status `custom_active` only after its custom smoke evaluation,
ledger summary, report generator, and audit command are covered by tests.
`make check-env` verifies the required custom adapter/evaluate/search/summarize/report/audit modules import successfully, verifies required custom command modules expose callable `main()` entrypoints, and rejects runnable registrations whose EnvSpec metadata, policy/harness sources, or generated skipped test scaffold still contain scaffold/TODO markers.
`make custom-run ENV=<EnvId>` dispatches standard custom modules without adding a new Makefile target family, and `make custom-verify ENV=<EnvId>` runs readiness, artifact-layout, summary, report, performance-report, optional generation-report, harness-declared extra non-evaluation commands, and audit gates when those modules follow the standard names. The standard verify chain calls `summarize`, any package-root `CUSTOM_VERIFY_EXTRA_COMMANDS`, `report`, `performance_report`, optional `generation_report`, and `audit`; `audit` must accept `--output <path>` so `audit_latest.json` can be regenerated in the environment's results directory.
SlimeVolley is the reference custom environment and is registered through `hl_benchmark.custom_envs.slimevolley`, which delegates to the existing `hl_benchmark.slimevolley` implementation for compatibility; new custom scaffolds use `hl_benchmark.custom_envs.<env_slug>` through `REGISTRATION.custom_module`.

Use status `planned` for metadata-only placeholders. Planned environments may
have artifact directories, notes, scaffold TODO metadata, and scaffold policy
sources, but they must not be included in generic or custom runnable commands.
`make check-env` validates the planned artifact scaffold but reports planned
metadata as not checked until promotion; metadata completion is enforced only
after status becomes `active` or `custom_active`. `make check-envs` keeps its
pass/fail gate focused on runnable environments while also reporting the count
and names of planned registry entries for review. `make check-planned-envs` is
the strict planned-scaffold gate for CI; it fails if any planned registration is
missing required artifact scaffold files, missing the skipped pytest scaffold,
contains mismatched scaffold identity markers, cannot import its policy scaffold,
or sets `REGISTRATION.custom_module` without
importable placeholder harness modules and callable custom command entrypoints.

The registry auto-discovers every `hl_benchmark/environments/<env_slug>.py`
module that exposes a `REGISTRATION` object, so adding a new environment should
not require editing `hl_benchmark/environments/__init__.py`. For custom envs,
`REGISTRATION.custom_module` names the harness import root, which lets new
harnesses live under `hl_benchmark.custom_envs.<env_slug>` without changing the
shared dispatcher. The shared policy
factory imports the registration's `policy_module`; each promoted runnable
policy module must expose `initial`, `improved`, and `tuned` in
`SUPPORTED_POLICY_NAMES`, plus a local `make_policy()` builder and a local
`candidate_configs()` scalar-search grid, so normal additions should not edit
`hl_benchmark/policies/factory.py` or `hl_benchmark/search.py` either. Use
`planned_env_ids()` to list scaffolded registrations that must not run yet,
`custom_env_ids()` for promoted custom harnesses, and `benchmark_env_ids()` for
generic aggregate environments. Use `registration_for(<EnvId>)` when tooling needs
the artifact slug, policy module, or custom module root without importing private
registry internals. Use `REGISTRATION.suite_order` to keep benchmark
output stable; scaffolded environments start at `suite_order=1000` and existing
benchmark environments use lower explicit values. Environment IDs, registry
keys, and artifact slugs must be unique because artifact slugs define the
`experiments/<env_slug>/` evidence root.

## Required Artifact Layout

Each new environment should keep evidence under its own artifact root. Create
the standard tree with:

```bash
make scaffold-generic-env ENV=<EnvId>
# or, for custom harnesses:
make scaffold-custom-env ENV=<EnvId>

# Use these only when intentionally creating one generic scaffold piece:
make scaffold-env ENV=<EnvId>
make scaffold-env-code ENV=<EnvId>
make scaffold-env-tests ENV=<EnvId>
```

The scaffold-created shape is:

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
  results/audit_latest.json  # generated by generic or custom artifact audit
  reports/final_report.md
  reports/requirements_audit.md  # optional coverage matrix for mature custom environments
```

The README must identify the exact environment ID and artifact root so copied or
stale folders are caught by `make check-env-layout`. Required subdirectories keep
`.gitkeep` placeholders so empty artifact roots remain tracked before
evaluations generate files.

The root `results/` directory is kept for legacy aggregate artifacts. Generic
single-environment evaluations, scalar-search baselines, and optional RL
baselines can opt into the per-environment root with `ARGS="--env-artifacts"`;
`make summary-env ENV=<EnvId>` regenerates the CSV projection from that generic
per-environment ledger, `make report-env ENV=<EnvId>` writes the matching
generic report scoped to that environment under `experiments/<env_slug>/reports/`,
and `make audit-env ENV=<EnvId>` writes a non-evaluation generic artifact audit
to `experiments/<env_slug>/results/audit_latest.json`. The generic audit expects
that ledger, summary, and scoped report artifacts have already been generated;
scaffold-only roots fail with explicit missing-artifact diagnostics. Custom harnesses should use their
per-environment root by default. Every runnable registration still needs a reserved
`experiments/<env_slug>/` root so new ledgers, reports, diagnostics, traces,
and tournament outputs have a stable home as the suite grows.

## Minimum Guardrails

Before promoting a new environment to `active` or `custom_active`, add tests for:

- registry metadata and `make list-envs` visibility,
- importable policy module with runnable `initial`, `improved`, and `tuned` policy names, `make_policy()`, and `candidate_configs()`,
- action validity for representative observations,
- deterministic fixed-seed smoke evaluation,
- ledger schema and summary generation,
- report generation,
- holdout guardrails for tuning/search commands,
- golden behavior checks for important policy states or short traces.

Do not optimize or debug on holdout seeds. If a run is invalid, record the
invalidation as a new ledger entry instead of deleting evidence.

## Promotion Checks

After scaffolding a planned environment, run only the registry and artifact
checks first. These checks are allowed to pass while scaffold metadata is still
marked TODO because planned environments are not runnable, but planned custom
registrations still need their placeholder harness modules to import:

```bash
make list-envs
make check-env-layout
make check-env-layout ARGS="--format json"
make check-env ENV=<EnvId>
make check-env ENV=<EnvId> ARGS="--format json"
make check-promotion ENV=<EnvId>
make check-promotions
make check-planned-envs
make verify
```

Before promoting a generic Gymnasium environment to `active`, replace the
scaffold policy/tests, complete the EnvSpec metadata, implement the policy-local
`candidate_configs()` scalar-search grid, then run:

```bash
make eval-env ENV=<EnvId> POLICY=initial SPLIT=smoke
make check-env ENV=<EnvId>
make check-promotion ENV=<EnvId>
make check-promotions
make check-envs
make verify
```

Before promoting a custom environment to `custom_active`, replace the custom
harness placeholders, complete the EnvSpec metadata, and make sure the standard
custom modules expose callable `main()` entrypoints. Only then run custom
commands:

```bash
make custom-run ENV=<EnvId>
make custom-run ENV=<EnvId> CUSTOM_COMMAND=summary
make custom-run ENV=<EnvId> CUSTOM_COMMAND=report
make custom-run ENV=<EnvId> CUSTOM_COMMAND=audit
make custom-verify ENV=<EnvId>
make check-env ENV=<EnvId>
make check-envs
make verify
```

`make custom-verify` is intentionally separate from `make verify` because it
regenerates custom summary, report, and audit artifacts. Harnesses may also
declare optional diagnostics or protocol refreshes through
`CUSTOM_VERIFY_EXTRA_COMMANDS`. Keep generated-artifact updates in explicit
environment-specific commands so default CI remains a non-regeneration gate.

Scaffolding commands such as `make scaffold-env-code`, `make scaffold-env-tests`,
and `make scaffold-custom-env` create files; use them when starting the new
environment, not as a no-op verification step on an already reviewed change
unless you intentionally want to check that all scaffolded files already exist.

`make check-env ENV=<EnvId>` validates one registry entry, artifact layout,
policy import, custom-harness imports, completed EnvSpec metadata, and absence
of generated scaffold/TODO markers in runnable sources or unreplaced
skipped test scaffolds without running evaluation. The JSON form exposes `runnable`, `metadata_issues`, `artifact_issues`,
`test_scaffold_issues`, `planned_test_scaffold_issues`,
`runnable_test_scaffold_issues`, `promotion_ready`, `promotion_blockers`,
`missing_required_policy_names`, policy import status, custom-harness import
status, custom command entrypoints, and scaffold-source checks for automated
review. `make check-promotion ENV=<EnvId>` uses the same readiness record but fails unless `promotion_ready` is true. `make check-promotions` aggregates that status across all registered environments for promotion review.

`make check-env-layout` validates the required artifact directories and files
for every runnable `active` and `custom_active` environment. The JSON output
exposes `required_dirs`, `required_files`, and `required_placeholder_files` for
automated review. For custom
environments, also run the environment-specific audit target if one exists, such
as
`make slimevolley-audit`.

# Experiment Artifacts

Each runnable environment gets its own artifact directory under `experiments/<env_slug>/`.
Core benchmark code should stay in `hl_benchmark/`; environment-specific configs,
ledgers, reports, notes, traces, and replay metadata belong here.

Scaffold-created per-environment shape:

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
  results/audit_latest.json
  results/episode_diagnostics.jsonl
  results/round_robin_dev.json
  reports/final_report.md
  reports/requirements_audit.md
```

The legacy aggregate benchmark still writes to `results/` so existing article
artifacts remain reproducible. New competitive or large environments should
prefer the per-environment tree, and generic-active environments keep reserved
roots here even while legacy aggregate outputs are still written to `results/`.
When the shared evaluator is not expressive enough, new custom executable code
should live under `hl_benchmark/custom_envs/<env_slug>/` and be referenced by
`REGISTRATION.custom_module`. SlimeVolley is registered through `hl_benchmark/custom_envs/slimevolley/`,
which delegates to `hl_benchmark/slimevolley/` as the implementation and compatibility root.

# LunarLander-v3 Artifacts

Environment ID: `LunarLander-v3`
Artifact root: `experiments/lunar_lander/`

This directory is reserved for benchmark evidence: configs, append-only ledgers, generated summaries, reports, notes, traces, and replay metadata. Keep scaffold files separate from generated evidence so review can tell what was created by setup versus what came from evaluation or audit runs.

Scaffold-created layout:

```text
experiments/lunar_lander/
  README.md
  configs/.gitkeep
  results/.gitkeep
  reports/.gitkeep
  notes/.gitkeep
```

Generated after evaluation/report/audit commands:

```text
experiments/lunar_lander/
  results/trials.jsonl
  results/summary.csv
  results/audit_latest.json
  reports/final_report.md
```

Keep new environments registered as `planned` until real policies, smoke evaluation, ledger/summary/report generation, audit checks, and regression tests exist. Do not delete failed ledger rows once generated.

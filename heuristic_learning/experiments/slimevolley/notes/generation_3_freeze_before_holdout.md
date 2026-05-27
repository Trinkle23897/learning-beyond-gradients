# Generation-3 Freeze Before Holdout

Status: frozen before consuming generation-3 holdout seeds `7000..7049`.

## Frozen State

- Current policy: `improved` with the kept `rear_wall_press` structural branch.
- Archived previous-best opponent: `improved-v3` remains frozen and is included in the generation-3 holdout opponent pool.
- Scalar-search artifact: `experiments/slimevolley/results/search_best_g3_dev.json` from development seeds only.
- Development tournament artifact: `experiments/slimevolley/results/round_robin_g3_dev.json` from development seeds only.
- Contact diagnostics: `experiments/slimevolley/results/contact_diagnostics_g3_dev.json` and `reports/contact_diagnostics_g3_dev.md`, generated from development traces only.

## Verification Before Holdout

Before this freeze note, validation passed with:

- `.venv/bin/python -m py_compile hl_benchmark/slimevolley/audit.py tests/test_slimevolley_optional.py`
- `.venv/bin/python -m pytest tests/test_slimevolley_optional.py`
- `make PYTHON=.venv/bin/python slimevolley-verify`
- `make PYTHON=.venv/bin/python verify`
- `make PYTHON=.venv/bin/python custom-verify ENV=SlimeVolley-v0`
- `.venv/bin/python -m hl_benchmark.slimevolley.audit --format json`
- Current registered bridge equivalent: `.venv/bin/python -m hl_benchmark.custom_envs.slimevolley.audit --format json`

## Holdout Rule

The generation-3 holdout may now be run once with the predeclared `generation_3_protocol.md` command. The resulting rows are final evidence only and must not be used for further policy, scalar-config, opponent-pool, or test changes in this generation.

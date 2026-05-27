# SlimeVolley Generation-3 Start Note

Generation-3 was predeclared before any new SlimeVolley tuning after the generation-2 holdout was consumed.

## Seed Lock

- Prior final-only holdouts remain locked: `1000..1049` and `4000..4049`.
- Generation-3 development seeds: `6000..6049`.
- Generation-3 holdout seeds: `7000..7049`, not inspected or used for tuning.
- Generation-3 audit seeds: `8000..8049`, reserved.

## First Development Diagnostic

Two append-only rows were recorded in `results/generation_3_trials.jsonl`:

1. Default `python3` failure: `gym` and `slimevolleygym` were not installed in the Anaconda Python 3.12 runtime. This row has `pass_fail=fail`, zero environment steps, and is kept as dependency/setup failure evidence.
2. Compatible venv rerun: `.venv/bin/python` with `gym==0.20.0` and `slimevolleygym==0.1.0` completed `improved` vs `builtin` on seeds `6000..6049`. Result: mean `-4.24`, wins/losses/draws `0/49/1`, environment steps `113541`.

## Immediate Diagnosis

The generation-3 development result is consistent with generation-2: the maintained heuristic still does not beat the built-in/RNN opponent. Future policy changes should use only generation-3 development traces until code, scalar config, opponent pool, and tests are frozen.

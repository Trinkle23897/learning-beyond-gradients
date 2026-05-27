# SlimeVolley Generation-3 Protocol

Protocol ID: `slimevolley-g3`
Status: `predeclared-not-run`

This artifact predeclares the next SlimeVolley experiment generation. It is generated without running evaluation, search, tournaments, or holdout evaluation.

## Prior Holdout Locks

Generation-1 holdout is already opened; do not tune, debug, or select policies on those seeds.
- slimevolley-g1 holdout artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_final.json`
- slimevolley-g1 holdout seeds: `1000..1049`

Generation-2 holdout is already opened; do not tune, debug, or select policies on those seeds.
- slimevolley-g2 holdout artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_g2_final.json`
- slimevolley-g2 holdout seeds: `4000..4049`

## Generation-3 Seed Ranges

| split | label | episodes | purpose |
| --- | --- | --- | --- |
| smoke | 6000..6001 | 2 | dependency and command smoke checks only |
| dev | 6000..6049 | 50 | diagnosis, structural policy iteration, scalar search, and tournament development evidence |
| holdout | 7000..7049 | 50 | final-only generation-3 evaluation after policies and scalar configs are frozen |
| audit | 8000..8049 | 50 | reserved independent audit seeds, not available for tuning |

## Opponent Protocol

- Policies: `random, initial, tuned, improved, baseline-rnn`
- Development opponents: `builtin, random, initial, improved-v0, improved-v1, improved-v2, improved`
- Scalar-search opponents: `builtin, random, initial, improved-v0, improved-v2`
- Holdout opponents: `builtin, random, initial, improved-v0, improved-v2, improved-v3`

## Guardrails

- Use the generation-3 ledger and summary paths for all generation-3 evidence; do not append generation-3 rows to generation-1 or generation-2 ledgers.
- Use generation-3 development seeds for diagnosis, structural edits, scalar search, and tournaments.
- Do not inspect generation-3 holdout seeds until the policy code, scalar config, opponent pool, and tests are frozen.
- Do not use generation-1 or generation-2 holdout results as tuning feedback; treat them only as historical final evidence.
- Record tests_run, tests_pass_fail, agent_iterations, code_edits, and failure_analysis on every generation-3 ledger-producing run.
- If generation-3 policy work starts, archive the current `improved` policy as a frozen opponent before changing current behavior.

## Diagnosis Targets

- built-in opponent serve and return timing without using generation-2 holdout outcomes for tuning
- high-arc defense before the ball drops below reachable height
- low-ball contact timing without late jump overcommit
- recovery to defensive home position after contact
- exploitability against archived heuristic opponents

## Commands

| name | command |
| --- | --- |
| regenerate_protocol | make slimevolley-generation3-protocol |
| verification_before_edits | make slimevolley-verify |
| dev_builtin_trace | make slimevolley-eval POLICY=improved OPPONENT=builtin SPLIT=dev ARGS="--ledger experiments/slimevolley/results/generation_3_trials.jsonl --summary experiments/slimevolley/results/generation_3_summary.csv --seed-start 6000 --episodes 50 --trace-window 8 --tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass" |
| scalar_search | make slimevolley-search MAX_CANDIDATES=16 ARGS="--ledger experiments/slimevolley/results/generation_3_trials.jsonl --summary experiments/slimevolley/results/generation_3_summary.csv --output experiments/slimevolley/results/search_best_g3_dev.json --seed-start 6000 --episodes 50 --opponents builtin random initial improved-v0 improved-v2" |
| development_tournament | make slimevolley-tournament SPLIT=dev ARGS="--ledger experiments/slimevolley/results/generation_3_trials.jsonl --summary experiments/slimevolley/results/generation_3_summary.csv --output experiments/slimevolley/results/round_robin_g3_dev.json --seed-start 6000 --episodes 50" |
| final_holdout_once | make slimevolley-final-eval ARGS="--ledger experiments/slimevolley/results/generation_3_trials.jsonl --summary experiments/slimevolley/results/generation_3_summary.csv --output experiments/slimevolley/results/holdout_g3_final.json --best-config experiments/slimevolley/results/search_best_g3_dev.json --seed-start 7000 --episodes 50 --tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass" |

## Promotion Checks

- `make verify`
- `make slimevolley-verify`
- `python3 -m hl_benchmark.custom_envs.slimevolley.audit --format json`

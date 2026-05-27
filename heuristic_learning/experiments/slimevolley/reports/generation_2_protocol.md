# SlimeVolley Generation-2 Protocol

Protocol ID: `slimevolley-g2`
Status: `predeclared-not-run`

This artifact predeclares the next SlimeVolley experiment generation. It is generated without running evaluation, search, tournaments, or holdout evaluation.

## Prior Holdout Lock

Generation-1 holdout is already opened; do not tune, debug, or select policies on those seeds.

- Generation-1 holdout artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_final.json`
- Generation-1 holdout seeds: `1000..1049`

## Generation-2 Seed Ranges

| split | label | episodes | purpose |
| --- | --- | --- | --- |
| smoke | 3000..3001 | 2 | dependency and command smoke checks only |
| dev | 3000..3049 | 50 | diagnosis, structural policy iteration, scalar search, and tournament development evidence |
| holdout | 4000..4049 | 50 | final-only generation-2 evaluation after policies and scalar configs are frozen |
| audit | 5000..5049 | 50 | reserved independent audit seeds, not available for tuning |

## Opponent Protocol

- Policies: `random, initial, tuned, improved, baseline-rnn`
- Development opponents: `builtin, random, initial, improved-v0, improved-v1, improved-v2, improved`
- Scalar-search opponents: `builtin, random, initial, improved-v0, improved-v2`
- Holdout opponents: `builtin, random, initial, improved-v0, improved-v2`

## Guardrails

- Use the generation-2 ledger and summary paths for all generation-2 evidence; do not append generation-2 rows to the generation-1 ledger until audit support is explicitly extended.
- Use generation-2 development seeds for diagnosis, structural edits, scalar search, and tournaments.
- Do not inspect generation-2 holdout seeds until the policy code, scalar config, opponent pool, and tests are frozen.
- Do not use generation-1 holdout results as tuning feedback; treat them only as historical final evidence.
- Record tests_run, tests_pass_fail, agent_iterations, code_edits, and failure_analysis on every generation-2 ledger-producing run.

## Diagnosis Targets

- built-in opponent serve and return timing
- high-arc defense before the ball drops below reachable height
- low-ball contact timing without late jump overcommit
- recovery to defensive home position after contact
- exploitability against archived heuristic opponents

## Commands

| name | command |
| --- | --- |
| regenerate_protocol | make slimevolley-protocol |
| verification_before_edits | make slimevolley-verify |
| dev_builtin_trace | make slimevolley-eval POLICY=improved OPPONENT=builtin SPLIT=dev ARGS="--ledger experiments/slimevolley/results/generation_2_trials.jsonl --summary experiments/slimevolley/results/generation_2_summary.csv --seed-start 3000 --episodes 50 --trace-window 8 --tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass" |
| scalar_search | make slimevolley-search MAX_CANDIDATES=16 ARGS="--ledger experiments/slimevolley/results/generation_2_trials.jsonl --summary experiments/slimevolley/results/generation_2_summary.csv --output experiments/slimevolley/results/search_best_g2_dev.json --seed-start 3000 --episodes 50 --opponents builtin random initial improved-v0 improved-v2" |
| development_tournament | make slimevolley-tournament SPLIT=dev ARGS="--ledger experiments/slimevolley/results/generation_2_trials.jsonl --summary experiments/slimevolley/results/generation_2_summary.csv --output experiments/slimevolley/results/round_robin_g2_dev.json --seed-start 3000 --episodes 50" |
| final_holdout_once | make slimevolley-final-eval ARGS="--ledger experiments/slimevolley/results/generation_2_trials.jsonl --summary experiments/slimevolley/results/generation_2_summary.csv --output experiments/slimevolley/results/holdout_g2_final.json --best-config experiments/slimevolley/results/search_best_g2_dev.json --seed-start 4000 --episodes 50 --tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass" |

## Promotion Checks

- `make verify`
- `make slimevolley-verify`
- `python3 -m hl_benchmark.custom_envs.slimevolley.audit --format json`

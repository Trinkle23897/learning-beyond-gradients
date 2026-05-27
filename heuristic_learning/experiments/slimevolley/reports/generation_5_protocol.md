# SlimeVolley Generation-5 Protocol

Protocol ID: `slimevolley-g5`
Status: `predeclared-not-run`

This artifact predeclares the next SlimeVolley experiment generation after generation-4 holdout was consumed. It is generated without running evaluation, search, tournaments, or holdout evaluation.

## Prior Holdout Locks

Generation-1 holdout is already opened; do not tune, debug, or select policies on those seeds.
- slimevolley-g1 holdout artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_final.json`
- slimevolley-g1 holdout seeds: `1000..1049`

Generation-2 holdout is already opened; do not tune, debug, or select policies on those seeds.
- slimevolley-g2 holdout artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_g2_final.json`
- slimevolley-g2 holdout seeds: `4000..4049`

Generation-3 holdout is already opened; do not tune, debug, or select policies on those seeds.
- slimevolley-g3 holdout artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_g3_final.json`
- slimevolley-g3 holdout seeds: `7000..7049`

Generation-4 holdout is already opened; do not tune, debug, or select policies on those seeds. Generation-4 audit seeds remain reserved and unavailable for tuning.
- slimevolley-g4 holdout artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_g4_final.json`
- slimevolley-g4 holdout seeds: `10000..10049`

## Generation-5 Seed Ranges

| split | label | episodes | purpose |
| --- | --- | --- | --- |
| smoke | 12000..12001 | 2 | dependency and command smoke checks only |
| dev | 12000..12049 | 50 | fresh post-generation-4 diagnosis, structural policy iteration, scalar search, and tournament development evidence |
| holdout | 13000..13049 | 50 | final-only generation-5 evaluation after policies and scalar configs are frozen |
| audit | 14000..14049 | 50 | reserved independent audit seeds, not available for tuning |

## Opponent Protocol

- Policies: `random, initial, tuned, improved, baseline-rnn, improved-v4, improved-v5, improved-v6, improved-tuned, attack, rally-serve, temporal, planner, teacher-assisted, net-pressure`
- Development opponents: `builtin, random, initial, improved-v0, improved-v1, improved-v2, improved, improved-v3, improved-v4, improved-v5, improved-v6, improved-tuned, attack, rally-serve, temporal, planner, teacher-assisted, net-pressure`
- Scalar-search opponents: `builtin, random, initial, improved-v0, improved-v2, improved-v3, improved-v4, improved-v5, improved-v6`
- Holdout opponents: `builtin, random, initial, improved-v0, improved-v2, improved-v3, improved-v4, improved-v5, improved-v6`

## Guardrails

- Use the generation-5 ledger and summary paths for all generation-5 evidence; do not append generation-5 rows to earlier ledgers.
- Use generation-5 development seeds for diagnosis, structural edits, scalar search, and tournaments.
- Do not inspect generation-5 holdout seeds until the policy code, scalar config, opponent pool, and tests are frozen.
- Do not use generation-1, generation-2, generation-3, or generation-4 holdout results as tuning feedback; treat them only as historical final evidence.
- Do not use generation-4 audit seeds for tuning; they remain reserved even though generation-4 holdout has been consumed.
- Record tests_run, tests_pass_fail, agent_iterations, code_edits, and failure_analysis on every generation-5 ledger-producing run.
- Any candidate that beats `baseline-rnn` on built-in development seeds must also pass the fixed development opponent pool before any generation-5 holdout use.

## Diagnosis Targets

- fresh post-generation-4 built-in opponent gap on development seeds without using consumed holdout outcomes for tuning
- whether `rally-serve` relies on draws rather than wins under new development seeds
- serve/return timing, high-arc defense, and low-ball contact timing from generation-5 traces
- robustness against archived heuristic opponents including improved-v4, improved-v5, improved-v6, attack, and rally-serve
- candidate exploitability versus the packaged `baseline-rnn` comparator before any holdout use

## Commands

| name | command |
| --- | --- |
| regenerate_protocol | make slimevolley-generation5-protocol |
| verification_before_edits | make slimevolley-verify |
| dev_builtin_trace | make slimevolley-eval POLICY=rally-serve OPPONENT=builtin SPLIT=dev ARGS="--ledger experiments/slimevolley/results/generation_5_trials.jsonl --summary experiments/slimevolley/results/generation_5_summary.csv --seed-start 12000 --episodes 50 --trace-window 8 --tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass" |
| development_rnn_comparator | make slimevolley-eval POLICY=baseline-rnn OPPONENT=builtin SPLIT=dev ARGS="--ledger experiments/slimevolley/results/generation_5_trials.jsonl --summary experiments/slimevolley/results/generation_5_summary.csv --seed-start 12000 --episodes 50 --trace-window 8 --tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass" |
| scalar_search | make slimevolley-search MAX_CANDIDATES=16 ARGS="--ledger experiments/slimevolley/results/generation_5_trials.jsonl --summary experiments/slimevolley/results/generation_5_summary.csv --output experiments/slimevolley/results/search_best_g5_dev.json --seed-start 12000 --episodes 50 --opponents builtin random initial improved-v0 improved-v2 improved-v3 improved-v5 improved-v6" |
| development_tournament | make slimevolley-tournament SPLIT=dev ARGS="--ledger experiments/slimevolley/results/generation_5_trials.jsonl --summary experiments/slimevolley/results/generation_5_summary.csv --output experiments/slimevolley/results/round_robin_g5_dev.json --seed-start 12000 --episodes 50" |
| final_holdout_once | make slimevolley-final-eval ARGS="--policies random initial improved improved-tuned attack rally-serve net-pressure baseline-rnn --ledger experiments/slimevolley/results/generation_5_trials.jsonl --summary experiments/slimevolley/results/generation_5_summary.csv --output experiments/slimevolley/results/holdout_g5_final.json --best-config experiments/slimevolley/results/search_best_g5_dev.json --seed-start 13000 --episodes 50 --tests-run 'python3 -m pytest tests/test_slimevolley_optional.py' --tests-pass-fail pass" |

## Promotion Checks

- `make verify`
- `make slimevolley-verify`
- `python3 -m hl_benchmark.custom_envs.slimevolley.audit --format json`

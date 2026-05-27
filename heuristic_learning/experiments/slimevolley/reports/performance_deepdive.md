# SlimeVolley Performance Deep Dive

A reviewer-oriented explanation of what the current SlimeVolley scores do and do not show.

## Status

This report is generated from existing artifacts only. It does not run evaluation, scalar search, tournaments, or holdout evaluation.

Holdout evidence in `holdout_final.json`, `holdout_g2_final.json`, and `holdout_g3_final.json` is final-only when present; do not use it for policy tuning.

## Evidence Sources

- Ledger: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/trials.jsonl`
- Original holdout matrix: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_final.json`
- Generation-2 holdout matrix: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_g2_final.json`
- Development round-robin: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/round_robin_dev.json`
- Generation-2 round-robin: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/round_robin_g2_dev.json`
- Scalar-search selection: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/search_best_dev.json`
- Generation-2 scalar-search selection: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/search_best_g2_dev.json`
- Generation-3 ledger: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_3_trials.jsonl`
- Generation-3 holdout matrix: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_g3_final.json`
- Generation-3 round-robin: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/round_robin_g3_dev.json`
- Generation-3 scalar-search selection: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/search_best_g3_dev.json`
- Compared policy labels include `initial`, `tuned`, `improved`, and `baseline-rnn`.

## Holdout Matrix

Artifact: `holdout_g3_final.json`. Split: `holdout`. Matchups: `30`. Episodes per matchup: `50`.

| Policy | Opponent | Mean | Win rate | Wins | Losses | Draws | Episodes | Steps | Score bar |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| random | builtin | -4.88 | 0 | 0 | 50 | 0 | 50 | 29184 | `----------|.........` |
| random | random | -0.22 | 0.46 | 23 | 27 | 0 | 50 | 32492 | `..........|.........` |
| random | initial | -2.22 | 0.14 | 7 | 43 | 0 | 50 | 33767 | `......----|.........` |
| random | improved-v0 | -1.82 | 0.22 | 11 | 39 | 0 | 50 | 34883 | `......----|.........` |
| random | improved-v2 | -3.22 | 0.04 | 2 | 48 | 0 | 50 | 34189 | `....------|.........` |
| random | improved-v3 | -3.68 | 0.02 | 1 | 49 | 0 | 50 | 34432 | `...-------|.........` |
| initial | builtin | -4.88 | 0 | 0 | 50 | 0 | 50 | 32827 | `----------|.........` |
| initial | random | 1.88 | 0.78 | 39 | 11 | 0 | 50 | 35174 | `..........|++++.....` |
| initial | initial | -0.1 | 0.54 | 27 | 23 | 0 | 50 | 38318 | `..........|.........` |
| initial | improved-v0 | -0.06 | 0.52 | 26 | 24 | 0 | 50 | 38658 | `..........|.........` |
| initial | improved-v2 | -2.48 | 0.14 | 7 | 43 | 0 | 50 | 40612 | `.....-----|.........` |
| initial | improved-v3 | -3.64 | 0.02 | 1 | 49 | 0 | 50 | 38622 | `...-------|.........` |
| tuned | builtin | -4.84 | 0 | 0 | 50 | 0 | 50 | 34518 | `----------|.........` |
| tuned | random | 1.98 | 0.78 | 39 | 11 | 0 | 50 | 35198 | `..........|++++.....` |
| tuned | initial | 0.46 | 0.58 | 29 | 21 | 0 | 50 | 40256 | `..........|+........` |
| tuned | improved-v0 | 0.72 | 0.64 | 32 | 18 | 0 | 50 | 40210 | `..........|+........` |
| tuned | improved-v2 | -2.22 | 0.14 | 7 | 43 | 0 | 50 | 44291 | `......----|.........` |
| tuned | improved-v3 | -3.56 | 0.02 | 1 | 49 | 0 | 50 | 41748 | `...-------|.........` |
| improved | builtin | -3.68 | 0 | 0 | 48 | 2 | 50 | 126972 | `...-------|.........` |
| improved | random | 4 | 1 | 50 | 0 | 0 | 50 | 38764 | `..........|++++++++.` |
| improved | initial | 3.72 | 1 | 50 | 0 | 0 | 50 | 46539 | `..........|+++++++..` |
| improved | improved-v0 | 3.78 | 1 | 50 | 0 | 0 | 50 | 46212 | `..........|++++++++.` |
| improved | improved-v2 | 3.34 | 0.98 | 49 | 1 | 0 | 50 | 63630 | `..........|+++++++..` |
| improved | improved-v3 | 0.24 | 0.5 | 25 | 20 | 5 | 50 | 129016 | `..........|.........` |
| baseline-rnn | builtin | -0.26 | 0.24 | 12 | 18 | 20 | 50 | 150000 | `.........-|.........` |
| baseline-rnn | random | 4.88 | 1 | 50 | 0 | 0 | 50 | 29828 | `..........|+++++++++` |
| baseline-rnn | initial | 4.84 | 1 | 50 | 0 | 0 | 50 | 34393 | `..........|+++++++++` |
| baseline-rnn | improved-v0 | 4.86 | 1 | 50 | 0 | 0 | 50 | 34306 | `..........|+++++++++` |
| baseline-rnn | improved-v2 | 4.82 | 1 | 50 | 0 | 0 | 50 | 51186 | `..........|+++++++++` |
| baseline-rnn | improved-v3 | 4.18 | 1 | 50 | 0 | 0 | 50 | 121764 | `..........|++++++++.` |

## Generation-2 Final Evidence

Generation-2 is the fresh-seed follow-up after the original holdout was consumed.
Generation-2 holdout, when present, is final-only and must not be used for further policy, scalar-config, or opponent-pool tuning.
- Generation-2 ledger: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_2_trials.jsonl`
- Generation-2 holdout: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_g2_final.json`
- Generation-2 tournament: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/round_robin_g2_dev.json`
- Generation-2 scalar search: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/search_best_g2_dev.json`
- Generation-2 ledger rows: `114`
- Generation-2 split counts: `{'dev': 89, 'holdout': 25}`
- Generation-2 holdout seeds: `4000..4049`

Artifact: `holdout_g2_final.json`. Split: `holdout`. Matchups: `25`. Episodes per matchup: `50`.

| Policy | Opponent | Mean | Win rate | Wins | Losses | Draws | Episodes | Steps | Score bar |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| random | builtin | -4.72 | 0 | 0 | 50 | 0 | 50 | 28889 | `.---------|.........` |
| random | random | -0.66 | 0.42 | 21 | 29 | 0 | 50 | 32340 | `.........-|.........` |
| random | initial | -1.9 | 0.26 | 13 | 37 | 0 | 50 | 32598 | `......----|.........` |
| random | improved-v0 | -1.68 | 0.28 | 14 | 36 | 0 | 50 | 33993 | `.......---|.........` |
| random | improved-v2 | -3.36 | 0 | 0 | 50 | 0 | 50 | 33082 | `...-------|.........` |
| initial | builtin | -4.68 | 0 | 0 | 50 | 0 | 50 | 33876 | `.---------|.........` |
| initial | random | 1 | 0.72 | 36 | 14 | 0 | 50 | 34722 | `..........|++.......` |
| initial | initial | -0.46 | 0.48 | 24 | 26 | 0 | 50 | 35270 | `.........-|.........` |
| initial | improved-v0 | -0.16 | 0.52 | 26 | 24 | 0 | 50 | 37355 | `..........|.........` |
| initial | improved-v2 | -2.24 | 0.18 | 9 | 41 | 0 | 50 | 39535 | `......----|.........` |
| tuned | builtin | -4.78 | 0 | 0 | 50 | 0 | 50 | 34808 | `----------|.........` |
| tuned | random | 1.52 | 0.76 | 38 | 12 | 0 | 50 | 34823 | `..........|+++......` |
| tuned | initial | 0.38 | 0.58 | 29 | 21 | 0 | 50 | 36453 | `..........|+........` |
| tuned | improved-v0 | 0.7 | 0.66 | 33 | 17 | 0 | 50 | 38383 | `..........|+........` |
| tuned | improved-v2 | -1.9 | 0.24 | 12 | 38 | 0 | 50 | 43044 | `......----|.........` |
| improved | builtin | -4.28 | 0 | 0 | 49 | 1 | 50 | 109720 | `.---------|.........` |
| improved | random | 3.44 | 0.98 | 49 | 1 | 0 | 50 | 38386 | `..........|+++++++..` |
| improved | initial | 3.46 | 0.98 | 49 | 1 | 0 | 50 | 41954 | `..........|+++++++..` |
| improved | improved-v0 | 3.3 | 0.98 | 49 | 1 | 0 | 50 | 42270 | `..........|+++++++..` |
| improved | improved-v2 | 2.7 | 0.94 | 47 | 3 | 0 | 50 | 59614 | `..........|+++++....` |
| baseline-rnn | builtin | -0.04 | 0.32 | 16 | 14 | 20 | 50 | 150000 | `..........|.........` |
| baseline-rnn | random | 4.9 | 1 | 50 | 0 | 0 | 50 | 30209 | `..........|+++++++++` |
| baseline-rnn | initial | 4.92 | 1 | 50 | 0 | 0 | 50 | 33037 | `..........|+++++++++` |
| baseline-rnn | improved-v0 | 4.9 | 1 | 50 | 0 | 0 | 50 | 32749 | `..........|+++++++++` |
| baseline-rnn | improved-v2 | 4.82 | 1 | 50 | 0 | 0 | 50 | 50943 | `..........|+++++++++` |

Generation-2 built-in-opponent headline: `improved` mean `-4.28` with `0` wins, while `baseline-rnn` mean `-0.04` with `16` wins and `20` draws.

## Generation-3 Evidence

Generation-3 now includes final-only holdout evidence from the frozen policy/config/opponent/test state. It must not be used for subsequent tuning.
- Generation-3 ledger: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_3_trials.jsonl`
- Generation-3 scalar search: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/search_best_g3_dev.json`
- Generation-3 tournament: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/round_robin_g3_dev.json`
- Generation-3 holdout: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_g3_final.json`
- Generation-3 ledger rows: `303`
- Generation-3 split counts: `{'dev': 273, 'holdout': 30}`
- Generation-3 pass/fail counts: `{'fail': 1, 'pass': 302}`
- Generation-3 holdout rows: `30`

| Timestamp | Split | Seeds | Policy | Opponent | Pass/fail | Episodes | Steps | Mean | W/L/D |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| 2026-05-25T21:20:50+00:00 | holdout | 7000..7049 | improved | improved-v2 | pass | 50 | 63630 | 3.34 | 49/1/0 |
| 2026-05-25T21:21:00+00:00 | holdout | 7000..7049 | improved | improved-v3 | pass | 50 | 129016 | 0.24 | 25/20/5 |
| 2026-05-25T21:21:09+00:00 | holdout | 7000..7049 | baseline-rnn | builtin | pass | 50 | 150000 | -0.26 | 12/18/20 |
| 2026-05-25T21:21:12+00:00 | holdout | 7000..7049 | baseline-rnn | random | pass | 50 | 29828 | 4.88 | 50/0/0 |
| 2026-05-25T21:21:16+00:00 | holdout | 7000..7049 | baseline-rnn | initial | pass | 50 | 34393 | 4.84 | 50/0/0 |
| 2026-05-25T21:21:19+00:00 | holdout | 7000..7049 | baseline-rnn | improved-v0 | pass | 50 | 34306 | 4.86 | 50/0/0 |
| 2026-05-25T21:21:24+00:00 | holdout | 7000..7049 | baseline-rnn | improved-v2 | pass | 50 | 51186 | 4.82 | 50/0/0 |
| 2026-05-25T21:21:34+00:00 | holdout | 7000..7049 | baseline-rnn | improved-v3 | pass | 50 | 121764 | 4.18 | 50/0/0 |
- Generation-3 scalar-search artifact is present.
- Generation-3 round-robin tournament artifact is present.
- Generation-3 holdout artifact is present and final-only; do not use it for subsequent tuning.

## Headline Comparisons

- `improved vs initial`: 6 better, 0 worse, 0 tied over 6 common holdout opponents; mean delta `3.44667`.

| Opponent | Candidate mean | Reference mean | Delta |
| --- | ---: | ---: | ---: |
| builtin | -3.68 | -4.88 | 1.2 |
| random | 4 | 1.88 | 2.12 |
| initial | 3.72 | -0.1 | 3.82 |
| improved-v0 | 3.78 | -0.06 | 3.84 |
| improved-v2 | 3.34 | -2.48 | 5.82 |
| improved-v3 | 0.24 | -3.64 | 3.88 |

- `improved vs tuned scalar baseline`: 6 better, 0 worse, 0 tied over 6 common holdout opponents; mean delta `3.14333`.

| Opponent | Candidate mean | Reference mean | Delta |
| --- | ---: | ---: | ---: |
| builtin | -3.68 | -4.84 | 1.16 |
| random | 4 | 1.98 | 2.02 |
| initial | 3.72 | 0.46 | 3.26 |
| improved-v0 | 3.78 | 0.72 | 3.06 |
| improved-v2 | 3.34 | -2.22 | 5.56 |
| improved-v3 | 0.24 | -3.56 | 3.8 |

- `baseline-rnn` vs `improved` on built-in holdout: mean gap `3.42` in favor of the packaged RNN comparator.

## Built-In Opponent Gap

The built-in opponent is the hardest recorded opponent and is the clearest place where the heuristic system is not deep-RL comparable.

| Policy | Mean | Wins | Losses | Draws | Win rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| random | -4.88 | 0 | 50 | 0 | 0 |
| initial | -4.88 | 0 | 50 | 0 | 0 |
| tuned | -4.84 | 0 | 50 | 0 | 0 |
| improved | -3.68 | 0 | 48 | 2 | 0 |
| baseline-rnn | -0.26 | 12 | 18 | 20 | 0.24 |

`improved` recorded `0` wins in `50` holdout built-in episodes; `baseline-rnn` recorded `12` wins and `20` draws.

## Opponent-Pool Robustness

This view excludes the built-in opponent and asks whether the maintained heuristic became broadly stronger against random and archived heuristic opponents.

- `non-built-in improved vs initial`: 5 better, 0 worse, 0 tied over 5 common holdout opponents; mean delta `3.896`.

| Opponent | Candidate mean | Reference mean | Delta |
| --- | ---: | ---: | ---: |
| random | 4 | 1.88 | 2.12 |
| initial | 3.72 | -0.1 | 3.82 |
| improved-v0 | 3.78 | -0.06 | 3.84 |
| improved-v2 | 3.34 | -2.48 | 5.82 |
| improved-v3 | 0.24 | -3.64 | 3.88 |

- `non-built-in improved vs tuned`: 5 better, 0 worse, 0 tied over 5 common holdout opponents; mean delta `3.54`.

| Opponent | Candidate mean | Reference mean | Delta |
| --- | ---: | ---: | ---: |
| random | 4 | 1.98 | 2.02 |
| initial | 3.72 | 0.46 | 3.26 |
| improved-v0 | 3.78 | 0.72 | 3.06 |
| improved-v2 | 3.34 | -2.22 | 5.56 |
| improved-v3 | 0.24 | -3.56 | 3.8 |

## Development Round-Robin

Development tournament split: `dev`. Participants: `random, initial, improved-v0, improved-v1, improved-v2, improved`. Matchups: `36`.

| Rank | Policy | Mean score across opponents | Win rate | Wins | Losses | Draws | Steps |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | improved-v1 | 1.58333 | 0.675 | 81 | 39 | 0 | 116117 |
| 2 | improved-v2 | 1.58333 | 0.675 | 81 | 39 | 0 | 116117 |
| 3 | improved | 1.58333 | 0.675 | 81 | 39 | 0 | 116117 |
| 4 | improved-v0 | -0.8 | 0.333333 | 40 | 80 | 0 | 94714 |
| 5 | initial | -0.916667 | 0.366667 | 44 | 76 | 0 | 95510 |
| 6 | random | -2.26667 | 0.133333 | 16 | 104 | 0 | 84208 |

The tournament is development evidence only; it is useful for diagnosing exploitability against archived policies, not for final holdout tuning.

## Scalar Search Context

Scalar/config search is a separate baseline, not a structural heuristic-improvement claim.

- Split: `dev`
- Candidate budget: `8`
- Selected candidate index: `1`
- Selection score: `0.0875`
- Opponents: `builtin, random, initial, improved-v0`
- Config: `{"contact_x_window": 0.18, "home_x": 1.05, "landing_horizon": 0.3}`
- Opponent means: `builtin=-4.95, improved-v0=1.2, initial=1.35, random=2.75`

## Cost Context

This cost context distinguishes environment samples from the coding-agent maintenance process and includes generation-2 and generation-3 rows when present.

| Metric | Value |
| --- | ---: |
| Generation-1 ledger rows | 186 |
| Generation-2 ledger rows | 114 |
| Generation-3 ledger rows | 303 |
| Total ledger rows | 603 |
| Total episodes | 25158 |
| Total environment steps | 23283213 |
| Total wall-clock seconds | 1499.08 |
| Structural-improvement rows | 33 |
| Scalar-search rows | 152 |
| Scalar-search episodes | 6640 |

- Generation-1 rows by split: `{'dev': 152, 'holdout': 25, 'smoke': 9}`
- Generation-2 rows by split: `{'dev': 89, 'holdout': 25}`
- Generation-3 rows by split: `{'dev': 273, 'holdout': 30}`
- Rows by change type across all performance ledgers: `{'bug fix': 5, 'evaluation-harness change': 393, 'invalid/rolled back': 3, 'logging/diagnostics': 1, 'logging/diagnostics change': 11, 'neural/RL baseline': 5, 'scalar/config tuning': 152, 'structural policy improvement': 33}`
- LLM call/token accounting remains limited to what the ledger captured; unavailable values are preserved rather than inferred.

## Interpretation

The current SlimeVolley evidence is weak or mixed support for the Learning Beyond Gradients hypothesis.

Short verdict: not deep-RL comparable.

Supported: the agent-maintained heuristic improved over the initial handwritten policy and scalar-tuned baseline across the non-built-in holdout opponent pool while preserving archived policies for regression and opponent-pool checks.

Weakened: the same heuristic still failed the built-in opponent and remains far behind the packaged `baseline-rnn` comparator, so it should not be described as performing similarly to deep RL on this testbed.

Concrete built-in evidence: `improved` mean `-3.68` with `0` wins; `baseline-rnn` mean `-0.26` with `12` wins and `20` draws.

## Next Performance Step

Do not tune on the already-used holdout seeds in `holdout_final.json`, `holdout_g2_final.json`, or `holdout_g3_final.json`.

Recommended next performance step: treat the current SlimeVolley generation as closed for policy selection. Further SlimeVolley work needs a fresh generation-4 protocol with new development, holdout, and audit seeds, or a move to another environment adapter.

# SlimeVolley Generation-2 Diagnosis

This report is generated from persisted generation-2 artifacts only. It does not run evaluation and must not be used as holdout feedback.

## Status

Generation-2 has `114` recorded trial row(s): `113` pass and `1` fail.

- Split counts: `{'dev': 89, 'holdout': 25}`
- Pass/fail counts: `{'fail': 1, 'pass': 113}`

## Evidence Sources

- Ledger: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_2_trials.jsonl` (present)
- Summary CSV: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_2_summary.csv` (present)
- Generation-2 holdout artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_g2_final.json` (present)
- Generation-2 holdout evidence is present and is final-only; it must not be used for policy tuning.

## Trial Rows

| Timestamp | Split | Seeds | Policy | Opponent | Pass/fail | Episodes | Steps | Mean | W/L/D | Failure note |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 2026-05-25T17:49:30+00:00 | dev | 3000..3049 | improved | builtin | fail | 50 | 0 |  | 0/0/0 | SlimeVolleyDependencyError: SlimeVolley requires optional legacy dependencies: gym and slimevolleygym. Current status... |
| 2026-05-25T18:10:29+00:00 | dev | 3000..3049 | improved | builtin | pass | 50 | 53821 | -4.86 | 0/50/0 | No failure observed. |
| 2026-05-25T18:12:00+00:00 | dev | 3000..3049 | improved-v2 | builtin | pass | 50 | 53821 | -4.86 | 0/50/0 | No failure observed. |
| 2026-05-25T18:12:19+00:00 | dev | 3000..3049 | improved-v1 | builtin | pass | 50 | 53821 | -4.86 | 0/50/0 | No failure observed. |
| 2026-05-25T18:12:34+00:00 | dev | 3000..3049 | initial | builtin | pass | 50 | 32359 | -4.88 | 0/50/0 | No failure observed. |
| 2026-05-25T18:12:56+00:00 | dev | 3000..3049 | baseline-rnn | builtin | pass | 50 | 150000 | 0.34 | 19/11/20 | No failure observed. |
| 2026-05-25T18:15:14+00:00 | dev | 3000..3049 | improved | builtin | pass | 50 | 118089 | -4.3 | 0/50/0 | No failure observed. |
| 2026-05-25T18:15:39+00:00 | dev | 3000..3049 | improved | random | pass | 50 | 34877 | 3.8 | 50/0/0 | No failure observed. |
| 2026-05-25T18:15:42+00:00 | dev | 3000..3049 | improved | initial | pass | 50 | 40744 | 3.4 | 46/4/0 | No failure observed. |
| 2026-05-25T18:15:44+00:00 | dev | 3000..3049 | improved | improved-v0 | pass | 50 | 40794 | 3.54 | 48/2/0 | No failure observed. |
| 2026-05-25T18:15:48+00:00 | dev | 3000..3049 | improved | improved-v1 | pass | 50 | 59027 | 2.92 | 45/5/0 | No failure observed. |
| 2026-05-25T18:15:52+00:00 | dev | 3000..3049 | improved | improved-v2 | pass | 50 | 59027 | 2.92 | 45/5/0 | No failure observed. |
| 2026-05-25T18:15:59+00:00 | dev | 3000..3049 | improved | improved | pass | 50 | 115251 | 0.34 | 28/19/3 | No failure observed. |
| 2026-05-25T18:17:49+00:00 | dev | 3000..3049 | tuned | builtin | pass | 50 | 32834 | -4.94 | 0/50/0 | No failure observed. |
| 2026-05-25T18:17:51+00:00 | dev | 3000..3049 | tuned | random | pass | 50 | 34155 | 2.14 | 42/8/0 | No failure observed. |
| 2026-05-25T18:17:54+00:00 | dev | 3000..3049 | tuned | initial | pass | 50 | 40306 | 0.48 | 30/20/0 | No failure observed. |
| 2026-05-25T18:17:56+00:00 | dev | 3000..3049 | tuned | improved-v0 | pass | 50 | 39844 | 0.94 | 35/15/0 | No failure observed. |
| 2026-05-25T18:17:59+00:00 | dev | 3000..3049 | tuned | improved-v2 | pass | 50 | 43067 | -1.5 | 13/37/0 | No failure observed. |
| 2026-05-25T18:18:01+00:00 | dev | 3000..3049 | tuned | builtin | pass | 50 | 32256 | -4.88 | 0/50/0 | No failure observed. |
| 2026-05-25T18:18:04+00:00 | dev | 3000..3049 | tuned | random | pass | 50 | 33797 | 1.68 | 38/12/0 | No failure observed. |
| 2026-05-25T18:18:06+00:00 | dev | 3000..3049 | tuned | initial | pass | 50 | 38043 | -0.4 | 22/28/0 | No failure observed. |
| 2026-05-25T18:18:09+00:00 | dev | 3000..3049 | tuned | improved-v0 | pass | 50 | 38894 | 0.14 | 27/23/0 | No failure observed. |
| 2026-05-25T18:18:12+00:00 | dev | 3000..3049 | tuned | improved-v2 | pass | 50 | 39238 | -1.98 | 11/39/0 | No failure observed. |
| 2026-05-25T18:18:14+00:00 | dev | 3000..3049 | tuned | builtin | pass | 50 | 31208 | -4.9 | 0/50/0 | No failure observed. |
| 2026-05-25T18:18:16+00:00 | dev | 3000..3049 | tuned | random | pass | 50 | 33716 | 1.24 | 35/15/0 | No failure observed. |
| 2026-05-25T18:18:19+00:00 | dev | 3000..3049 | tuned | initial | pass | 50 | 36907 | -0.66 | 20/30/0 | No failure observed. |
| 2026-05-25T18:18:21+00:00 | dev | 3000..3049 | tuned | improved-v0 | pass | 50 | 37938 | -0.26 | 24/26/0 | No failure observed. |
| 2026-05-25T18:18:24+00:00 | dev | 3000..3049 | tuned | improved-v2 | pass | 50 | 37795 | -2.3 | 8/42/0 | No failure observed. |
| 2026-05-25T18:18:26+00:00 | dev | 3000..3049 | tuned | builtin | pass | 50 | 33172 | -4.94 | 0/50/0 | No failure observed. |
| 2026-05-25T18:18:28+00:00 | dev | 3000..3049 | tuned | random | pass | 50 | 34554 | 2.26 | 42/8/0 | No failure observed. |
| 2026-05-25T18:18:31+00:00 | dev | 3000..3049 | tuned | initial | pass | 50 | 41110 | 0.48 | 29/21/0 | No failure observed. |
| 2026-05-25T18:18:34+00:00 | dev | 3000..3049 | tuned | improved-v0 | pass | 50 | 40337 | 0.92 | 35/15/0 | No failure observed. |
| 2026-05-25T18:18:37+00:00 | dev | 3000..3049 | tuned | improved-v2 | pass | 50 | 43073 | -1.5 | 12/38/0 | No failure observed. |
| 2026-05-25T18:18:39+00:00 | dev | 3000..3049 | tuned | builtin | pass | 50 | 32359 | -4.88 | 0/50/0 | No failure observed. |
| 2026-05-25T18:18:41+00:00 | dev | 3000..3049 | tuned | random | pass | 50 | 33963 | 1.58 | 37/13/0 | No failure observed. |
| 2026-05-25T18:18:44+00:00 | dev | 3000..3049 | tuned | initial | pass | 50 | 38196 | -0.34 | 23/27/0 | No failure observed. |
| 2026-05-25T18:18:47+00:00 | dev | 3000..3049 | tuned | improved-v0 | pass | 50 | 38982 | 0.1 | 26/24/0 | No failure observed. |
| 2026-05-25T18:18:49+00:00 | dev | 3000..3049 | tuned | improved-v2 | pass | 50 | 40409 | -1.96 | 10/40/0 | No failure observed. |
| 2026-05-25T18:18:51+00:00 | dev | 3000..3049 | tuned | builtin | pass | 50 | 30714 | -4.92 | 0/50/0 | No failure observed. |
| 2026-05-25T18:18:54+00:00 | dev | 3000..3049 | tuned | random | pass | 50 | 34157 | 1.24 | 35/15/0 | No failure observed. |
| 2026-05-25T18:18:56+00:00 | dev | 3000..3049 | tuned | initial | pass | 50 | 37324 | -0.7 | 19/31/0 | No failure observed. |
| 2026-05-25T18:18:59+00:00 | dev | 3000..3049 | tuned | improved-v0 | pass | 50 | 38249 | -0.36 | 22/28/0 | No failure observed. |
| 2026-05-25T18:19:02+00:00 | dev | 3000..3049 | tuned | improved-v2 | pass | 50 | 37409 | -2.3 | 8/42/0 | No failure observed. |
| 2026-05-25T18:19:04+00:00 | dev | 3000..3049 | tuned | builtin | pass | 50 | 32899 | -4.94 | 0/50/0 | No failure observed. |
| 2026-05-25T18:19:06+00:00 | dev | 3000..3049 | tuned | random | pass | 50 | 33802 | 2.36 | 42/8/0 | No failure observed. |
| 2026-05-25T18:19:09+00:00 | dev | 3000..3049 | tuned | initial | pass | 50 | 40444 | 0.64 | 31/19/0 | No failure observed. |
| 2026-05-25T18:19:12+00:00 | dev | 3000..3049 | tuned | improved-v0 | pass | 50 | 39512 | 1 | 35/15/0 | No failure observed. |
| 2026-05-25T18:19:15+00:00 | dev | 3000..3049 | tuned | improved-v2 | pass | 50 | 43701 | -1.4 | 12/38/0 | No failure observed. |
| 2026-05-25T18:19:17+00:00 | dev | 3000..3049 | tuned | builtin | pass | 50 | 31967 | -4.88 | 0/50/0 | No failure observed. |
| 2026-05-25T18:19:20+00:00 | dev | 3000..3049 | tuned | random | pass | 50 | 33997 | 1.82 | 39/11/0 | No failure observed. |
| 2026-05-25T18:19:22+00:00 | dev | 3000..3049 | tuned | initial | pass | 50 | 38150 | -0.28 | 23/27/0 | No failure observed. |
| 2026-05-25T18:19:25+00:00 | dev | 3000..3049 | tuned | improved-v0 | pass | 50 | 38667 | 0.28 | 28/22/0 | No failure observed. |
| 2026-05-25T18:19:28+00:00 | dev | 3000..3049 | tuned | improved-v2 | pass | 50 | 41092 | -1.86 | 11/39/0 | No failure observed. |
| 2026-05-25T18:19:46+00:00 | dev | 3000..3049 | random | random | pass | 50 | 32791 | -0.12 | 22/28/0 | No failure observed. |
| 2026-05-25T18:19:49+00:00 | dev | 3000..3049 | random | initial | pass | 50 | 34306 | -1.82 | 9/41/0 | No failure observed. |
| 2026-05-25T18:19:51+00:00 | dev | 3000..3049 | random | improved-v0 | pass | 50 | 34852 | -1.66 | 10/40/0 | No failure observed. |
| 2026-05-25T18:19:54+00:00 | dev | 3000..3049 | random | improved-v1 | pass | 50 | 35825 | -2.54 | 7/43/0 | No failure observed. |
| 2026-05-25T18:19:57+00:00 | dev | 3000..3049 | random | improved-v2 | pass | 50 | 35825 | -2.54 | 7/43/0 | No failure observed. |
| 2026-05-25T18:20:00+00:00 | dev | 3000..3049 | random | improved | pass | 50 | 34805 | -3.64 | 0/50/0 | No failure observed. |
| 2026-05-25T18:20:02+00:00 | dev | 3000..3049 | initial | random | pass | 50 | 33963 | 1.58 | 37/13/0 | No failure observed. |
| 2026-05-25T18:20:05+00:00 | dev | 3000..3049 | initial | initial | pass | 50 | 38196 | -0.34 | 23/27/0 | No failure observed. |
| 2026-05-25T18:20:08+00:00 | dev | 3000..3049 | initial | improved-v0 | pass | 50 | 38980 | 0.1 | 26/24/0 | No failure observed. |
| 2026-05-25T18:20:10+00:00 | dev | 3000..3049 | initial | improved-v1 | pass | 50 | 40407 | -1.96 | 10/40/0 | No failure observed. |
| 2026-05-25T18:20:13+00:00 | dev | 3000..3049 | initial | improved-v2 | pass | 50 | 40407 | -1.96 | 10/40/0 | No failure observed. |
| 2026-05-25T18:20:16+00:00 | dev | 3000..3049 | initial | improved | pass | 50 | 39664 | -3.48 | 1/49/0 | No failure observed. |
| 2026-05-25T18:20:19+00:00 | dev | 3000..3049 | improved-v0 | random | pass | 50 | 33848 | 1.74 | 40/10/0 | No failure observed. |
| 2026-05-25T18:20:22+00:00 | dev | 3000..3049 | improved-v0 | initial | pass | 50 | 39099 | -0.4 | 22/28/0 | No failure observed. |
| 2026-05-25T18:20:24+00:00 | dev | 3000..3049 | improved-v0 | improved-v0 | pass | 50 | 39556 | 0.02 | 27/23/0 | No failure observed. |
| 2026-05-25T18:20:27+00:00 | dev | 3000..3049 | improved-v0 | improved-v1 | pass | 50 | 40575 | -2.32 | 6/44/0 | No failure observed. |
| 2026-05-25T18:20:30+00:00 | dev | 3000..3049 | improved-v0 | improved-v2 | pass | 50 | 40575 | -2.32 | 6/44/0 | No failure observed. |
| 2026-05-25T18:20:33+00:00 | dev | 3000..3049 | improved-v0 | improved | pass | 50 | 39271 | -3.42 | 2/48/0 | No failure observed. |
| 2026-05-25T18:20:36+00:00 | dev | 3000..3049 | improved-v1 | random | pass | 50 | 34609 | 2.98 | 47/3/0 | No failure observed. |
| 2026-05-25T18:20:39+00:00 | dev | 3000..3049 | improved-v1 | initial | pass | 50 | 41430 | 2.38 | 43/7/0 | No failure observed. |
| 2026-05-25T18:20:42+00:00 | dev | 3000..3049 | improved-v1 | improved-v0 | pass | 50 | 41468 | 2.74 | 47/3/0 | No failure observed. |
| 2026-05-25T18:20:45+00:00 | dev | 3000..3049 | improved-v1 | improved-v1 | pass | 50 | 54364 | -0.04 | 24/26/0 | No failure observed. |
| 2026-05-25T18:20:49+00:00 | dev | 3000..3049 | improved-v1 | improved-v2 | pass | 50 | 54364 | -0.04 | 24/26/0 | No failure observed. |
| 2026-05-25T18:20:53+00:00 | dev | 3000..3049 | improved-v1 | improved | pass | 50 | 58984 | -2.86 | 3/47/0 | No failure observed. |
| 2026-05-25T18:20:56+00:00 | dev | 3000..3049 | improved-v2 | random | pass | 50 | 34609 | 2.98 | 47/3/0 | No failure observed. |
| 2026-05-25T18:20:59+00:00 | dev | 3000..3049 | improved-v2 | initial | pass | 50 | 41430 | 2.38 | 43/7/0 | No failure observed. |
| 2026-05-25T18:21:02+00:00 | dev | 3000..3049 | improved-v2 | improved-v0 | pass | 50 | 41468 | 2.74 | 47/3/0 | No failure observed. |
| 2026-05-25T18:21:06+00:00 | dev | 3000..3049 | improved-v2 | improved-v1 | pass | 50 | 54364 | -0.04 | 24/26/0 | No failure observed. |
| 2026-05-25T18:21:10+00:00 | dev | 3000..3049 | improved-v2 | improved-v2 | pass | 50 | 54364 | -0.04 | 24/26/0 | No failure observed. |
| 2026-05-25T18:21:14+00:00 | dev | 3000..3049 | improved-v2 | improved | pass | 50 | 58984 | -2.86 | 3/47/0 | No failure observed. |
| 2026-05-25T18:21:17+00:00 | dev | 3000..3049 | improved | random | pass | 50 | 34877 | 3.8 | 50/0/0 | No failure observed. |
| 2026-05-25T18:21:19+00:00 | dev | 3000..3049 | improved | initial | pass | 50 | 40744 | 3.4 | 46/4/0 | No failure observed. |
| 2026-05-25T18:21:22+00:00 | dev | 3000..3049 | improved | improved-v0 | pass | 50 | 40794 | 3.54 | 48/2/0 | No failure observed. |
| 2026-05-25T18:21:27+00:00 | dev | 3000..3049 | improved | improved-v1 | pass | 50 | 59027 | 2.92 | 45/5/0 | No failure observed. |
| 2026-05-25T18:21:31+00:00 | dev | 3000..3049 | improved | improved-v2 | pass | 50 | 59027 | 2.92 | 45/5/0 | No failure observed. |
| 2026-05-25T18:21:39+00:00 | dev | 3000..3049 | improved | improved | pass | 50 | 115251 | 0.34 | 28/19/3 | No failure observed. |
| 2026-05-25T18:32:58+00:00 | holdout | 4000..4049 | random | builtin | pass | 50 | 28889 | -4.72 | 0/50/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:00+00:00 | holdout | 4000..4049 | random | random | pass | 50 | 32340 | -0.66 | 21/29/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:03+00:00 | holdout | 4000..4049 | random | initial | pass | 50 | 32598 | -1.9 | 13/37/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:06+00:00 | holdout | 4000..4049 | random | improved-v0 | pass | 50 | 33993 | -1.68 | 14/36/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:09+00:00 | holdout | 4000..4049 | random | improved-v2 | pass | 50 | 33082 | -3.36 | 0/50/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:11+00:00 | holdout | 4000..4049 | initial | builtin | pass | 50 | 33876 | -4.68 | 0/50/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:14+00:00 | holdout | 4000..4049 | initial | random | pass | 50 | 34722 | 1 | 36/14/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:16+00:00 | holdout | 4000..4049 | initial | initial | pass | 50 | 35270 | -0.46 | 24/26/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:19+00:00 | holdout | 4000..4049 | initial | improved-v0 | pass | 50 | 37355 | -0.16 | 26/24/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:22+00:00 | holdout | 4000..4049 | initial | improved-v2 | pass | 50 | 39535 | -2.24 | 9/41/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:24+00:00 | holdout | 4000..4049 | tuned | builtin | pass | 50 | 34808 | -4.78 | 0/50/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:27+00:00 | holdout | 4000..4049 | tuned | random | pass | 50 | 34823 | 1.52 | 38/12/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:29+00:00 | holdout | 4000..4049 | tuned | initial | pass | 50 | 36453 | 0.38 | 29/21/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:32+00:00 | holdout | 4000..4049 | tuned | improved-v0 | pass | 50 | 38383 | 0.7 | 33/17/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:35+00:00 | holdout | 4000..4049 | tuned | improved-v2 | pass | 50 | 43044 | -1.9 | 12/38/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:42+00:00 | holdout | 4000..4049 | improved | builtin | pass | 50 | 109720 | -4.28 | 0/49/1 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:45+00:00 | holdout | 4000..4049 | improved | random | pass | 50 | 38386 | 3.44 | 49/1/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:48+00:00 | holdout | 4000..4049 | improved | initial | pass | 50 | 41954 | 3.46 | 49/1/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:51+00:00 | holdout | 4000..4049 | improved | improved-v0 | pass | 50 | 42270 | 3.3 | 49/1/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:33:56+00:00 | holdout | 4000..4049 | improved | improved-v2 | pass | 50 | 59614 | 2.7 | 47/3/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:34:04+00:00 | holdout | 4000..4049 | baseline-rnn | builtin | pass | 50 | 150000 | -0.04 | 16/14/20 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:34:07+00:00 | holdout | 4000..4049 | baseline-rnn | random | pass | 50 | 30209 | 4.9 | 50/0/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:34:09+00:00 | holdout | 4000..4049 | baseline-rnn | initial | pass | 50 | 33037 | 4.92 | 50/0/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:34:12+00:00 | holdout | 4000..4049 | baseline-rnn | improved-v0 | pass | 50 | 32749 | 4.9 | 50/0/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T18:34:16+00:00 | holdout | 4000..4049 | baseline-rnn | improved-v2 | pass | 50 | 50943 | 4.82 | 50/0/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |

## Failure Analysis

Failed rows remain append-only evidence. They should be fixed by later rows, not deleted.

- Failure 1: `improved` vs `builtin` on split `dev` recorded `0` environment steps. Failure analysis: SlimeVolleyDependencyError: SlimeVolley requires optional legacy dependencies: gym and slimevolleygym. Current status: ModuleNotFoundError: No module named 'gym'

## Dependency Status

Report-generator runtime dependency snapshot:

| Package | Version |
| --- | --- |
| gym | `not_installed` |
| numpy | `1.26.4` |
| opencv-python | `4.13.0.92` |
| slimevolleygym | `not_installed` |

Latest generation-2 evaluation runtime dependency snapshot:

| Package | Ledger version |
| --- | --- |
| gym | `0.20.0` |
| numpy | `1.26.4` |
| opencv-python | `4.11.0.86` |
| slimevolleygym | `0.1.0` |

## Cost So Far

- Trial rows: `114`
- Episodes requested/recorded: `5700`
- Environment steps: `5001024`
- Wall-clock seconds: `324.425`
- Agent iterations recorded: `1`
- Code edits recorded as max cumulative count: `1`
- Code-edit row sum, which can double-count one edit evaluated across opponents: `72`
- Test status counts: `{'pass': 114}`
- LLM token accounting: unavailable from the local Codex runtime unless entered manually in ledger rows.

## Holdout Lock

Generation-2 holdout evidence is now present in `holdout_g2_final.json` and the generation-2 ledger. It is final-only evidence; no generation-2 holdout evidence may be used for further tuning of the current policy, scalar config, or opponent pool.
Further policy work requires a fresh predeclared experiment generation with new seeds.

## Next Action

1. Treat generation-2 holdout rows as final evidence only; do not tune current policy/config/opponents on them.
2. Use this diagnosis, `holdout_g2_final.json`, and audit hashes to write conclusions and limitations.
3. If more policy work is needed, predeclare a fresh generation with new seeds before any further tuning.
4. Preserve all failed, dev, scalar-search, tournament, and holdout rows append-only.

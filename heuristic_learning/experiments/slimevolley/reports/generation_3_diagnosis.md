# SlimeVolley Generation-3 Diagnosis

This report is generated from persisted generation-3 artifacts only. It does not run evaluation and must not be used as holdout feedback.

## Status

Generation-3 has `303` recorded trial row(s): `302` pass and `1` fail.

- Split counts: `{'dev': 273, 'holdout': 30}`
- Pass/fail counts: `{'fail': 1, 'pass': 302}`

## Evidence Sources

- Ledger: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_3_trials.jsonl` (present)
- Summary CSV: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/generation_3_summary.csv` (present)
- Generation-3 holdout artifact: `/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/experiments/slimevolley/results/holdout_g3_final.json` (present)
- Generation-3 holdout evidence is present and is final-only; it must not be used for policy tuning.

## Trial Rows

| Timestamp | Split | Seeds | Policy | Opponent | Pass/fail | Episodes | Steps | Mean | W/L/D | Failure note |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 2026-05-25T19:23:07+00:00 | dev | 6000..6049 | improved | builtin | fail | 50 | 0 |  | 0/0/0 | SlimeVolleyDependencyError: SlimeVolley requires optional legacy dependencies: gym and slimevolleygym. Current status... |
| 2026-05-25T19:24:38+00:00 | dev | 6000..6049 | improved | builtin | pass | 50 | 113541 | -4.24 | 0/49/1 | No failure observed. |
| 2026-05-25T20:01:53+00:00 | dev | 6000..6049 | tuned | builtin | pass | 50 | 35129 | -4.88 | 0/50/0 | No failure observed. |
| 2026-05-25T20:01:56+00:00 | dev | 6000..6049 | tuned | random | pass | 50 | 34284 | 2.44 | 43/7/0 | No failure observed. |
| 2026-05-25T20:01:58+00:00 | dev | 6000..6049 | tuned | initial | pass | 50 | 39853 | 0.72 | 32/18/0 | No failure observed. |
| 2026-05-25T20:02:01+00:00 | dev | 6000..6049 | tuned | improved-v0 | pass | 50 | 39952 | 0.84 | 32/18/0 | No failure observed. |
| 2026-05-25T20:02:04+00:00 | dev | 6000..6049 | tuned | improved-v2 | pass | 50 | 45578 | -1.84 | 10/40/0 | No failure observed. |
| 2026-05-25T20:02:06+00:00 | dev | 6000..6049 | tuned | builtin | pass | 50 | 33512 | -4.9 | 0/50/0 | No failure observed. |
| 2026-05-25T20:02:09+00:00 | dev | 6000..6049 | tuned | random | pass | 50 | 35440 | 1.6 | 37/13/0 | No failure observed. |
| 2026-05-25T20:02:11+00:00 | dev | 6000..6049 | tuned | initial | pass | 50 | 39272 | -0.1 | 25/25/0 | No failure observed. |
| 2026-05-25T20:02:14+00:00 | dev | 6000..6049 | tuned | improved-v0 | pass | 50 | 40126 | 0.16 | 29/21/0 | No failure observed. |
| 2026-05-25T20:02:17+00:00 | dev | 6000..6049 | tuned | improved-v2 | pass | 50 | 43280 | -2.2 | 7/43/0 | No failure observed. |
| 2026-05-25T20:02:19+00:00 | dev | 6000..6049 | tuned | builtin | pass | 50 | 32236 | -4.9 | 0/50/0 | No failure observed. |
| 2026-05-25T20:02:21+00:00 | dev | 6000..6049 | tuned | random | pass | 50 | 33960 | 1.5 | 38/12/0 | No failure observed. |
| 2026-05-25T20:02:24+00:00 | dev | 6000..6049 | tuned | initial | pass | 50 | 37890 | -0.44 | 22/28/0 | No failure observed. |
| 2026-05-25T20:02:26+00:00 | dev | 6000..6049 | tuned | improved-v0 | pass | 50 | 38201 | -0.4 | 23/27/0 | No failure observed. |
| 2026-05-25T20:02:29+00:00 | dev | 6000..6049 | tuned | improved-v2 | pass | 50 | 39831 | -2.72 | 4/46/0 | No failure observed. |
| 2026-05-25T20:02:31+00:00 | dev | 6000..6049 | tuned | builtin | pass | 50 | 35588 | -4.86 | 0/50/0 | No failure observed. |
| 2026-05-25T20:02:34+00:00 | dev | 6000..6049 | tuned | random | pass | 50 | 34298 | 2.42 | 44/6/0 | No failure observed. |
| 2026-05-25T20:02:36+00:00 | dev | 6000..6049 | tuned | initial | pass | 50 | 40458 | 0.82 | 32/18/0 | No failure observed. |
| 2026-05-25T20:02:39+00:00 | dev | 6000..6049 | tuned | improved-v0 | pass | 50 | 40479 | 1.1 | 35/15/0 | No failure observed. |
| 2026-05-25T20:02:42+00:00 | dev | 6000..6049 | tuned | improved-v2 | pass | 50 | 46271 | -1.86 | 8/42/0 | No failure observed. |
| 2026-05-25T20:02:44+00:00 | dev | 6000..6049 | tuned | builtin | pass | 50 | 33666 | -4.9 | 0/50/0 | No failure observed. |
| 2026-05-25T20:02:47+00:00 | dev | 6000..6049 | tuned | random | pass | 50 | 35055 | 1.68 | 37/13/0 | No failure observed. |
| 2026-05-25T20:02:49+00:00 | dev | 6000..6049 | tuned | initial | pass | 50 | 39036 | 0.06 | 26/24/0 | No failure observed. |
| 2026-05-25T20:02:52+00:00 | dev | 6000..6049 | tuned | improved-v0 | pass | 50 | 39676 | 0.26 | 29/21/0 | No failure observed. |
| 2026-05-25T20:02:55+00:00 | dev | 6000..6049 | tuned | improved-v2 | pass | 50 | 43228 | -2.1 | 8/42/0 | No failure observed. |
| 2026-05-25T20:02:57+00:00 | dev | 6000..6049 | tuned | builtin | pass | 50 | 32838 | -4.9 | 0/50/0 | No failure observed. |
| 2026-05-25T20:03:00+00:00 | dev | 6000..6049 | tuned | random | pass | 50 | 34184 | 1.38 | 36/14/0 | No failure observed. |
| 2026-05-25T20:03:02+00:00 | dev | 6000..6049 | tuned | initial | pass | 50 | 37922 | -0.3 | 22/28/0 | No failure observed. |
| 2026-05-25T20:03:05+00:00 | dev | 6000..6049 | tuned | improved-v0 | pass | 50 | 38489 | -0.18 | 24/26/0 | No failure observed. |
| 2026-05-25T20:03:08+00:00 | dev | 6000..6049 | tuned | improved-v2 | pass | 50 | 40632 | -2.48 | 6/44/0 | No failure observed. |
| 2026-05-25T20:03:10+00:00 | dev | 6000..6049 | tuned | builtin | pass | 50 | 35117 | -4.9 | 0/50/0 | No failure observed. |
| 2026-05-25T20:03:12+00:00 | dev | 6000..6049 | tuned | random | pass | 50 | 33836 | 2.58 | 45/5/0 | No failure observed. |
| 2026-05-25T20:03:15+00:00 | dev | 6000..6049 | tuned | initial | pass | 50 | 39694 | 0.76 | 32/18/0 | No failure observed. |
| 2026-05-25T20:03:18+00:00 | dev | 6000..6049 | tuned | improved-v0 | pass | 50 | 39720 | 0.92 | 33/17/0 | No failure observed. |
| 2026-05-25T20:03:21+00:00 | dev | 6000..6049 | tuned | improved-v2 | pass | 50 | 45087 | -1.96 | 7/43/0 | No failure observed. |
| 2026-05-25T20:03:23+00:00 | dev | 6000..6049 | tuned | builtin | pass | 50 | 33276 | -4.9 | 0/50/0 | No failure observed. |
| 2026-05-25T20:03:25+00:00 | dev | 6000..6049 | tuned | random | pass | 50 | 34431 | 1.62 | 38/12/0 | No failure observed. |
| 2026-05-25T20:03:28+00:00 | dev | 6000..6049 | tuned | initial | pass | 50 | 39021 | -0.1 | 25/25/0 | No failure observed. |
| 2026-05-25T20:03:31+00:00 | dev | 6000..6049 | tuned | improved-v0 | pass | 50 | 39757 | 0.08 | 28/22/0 | No failure observed. |
| 2026-05-25T20:03:34+00:00 | dev | 6000..6049 | tuned | improved-v2 | pass | 50 | 42892 | -2.2 | 7/43/0 | No failure observed. |
| 2026-05-25T20:03:36+00:00 | dev | 6000..6049 | tuned | builtin | pass | 50 | 32171 | -4.9 | 0/50/0 | No failure observed. |
| 2026-05-25T20:03:38+00:00 | dev | 6000..6049 | tuned | random | pass | 50 | 33748 | 1.5 | 38/12/0 | No failure observed. |
| 2026-05-25T20:03:41+00:00 | dev | 6000..6049 | tuned | initial | pass | 50 | 37475 | -0.32 | 22/28/0 | No failure observed. |
| 2026-05-25T20:03:44+00:00 | dev | 6000..6049 | tuned | improved-v0 | pass | 50 | 38545 | -0.14 | 25/25/0 | No failure observed. |
| 2026-05-25T20:03:46+00:00 | dev | 6000..6049 | tuned | improved-v2 | pass | 50 | 39807 | -2.68 | 5/45/0 | No failure observed. |
| 2026-05-25T20:03:48+00:00 | dev | 6000..6049 | tuned | builtin | pass | 50 | 35129 | -4.88 | 0/50/0 | No failure observed. |
| 2026-05-25T20:03:51+00:00 | dev | 6000..6049 | tuned | random | pass | 50 | 34284 | 2.44 | 43/7/0 | No failure observed. |
| 2026-05-25T20:03:54+00:00 | dev | 6000..6049 | tuned | initial | pass | 50 | 39903 | 0.72 | 32/18/0 | No failure observed. |
| 2026-05-25T20:03:57+00:00 | dev | 6000..6049 | tuned | improved-v0 | pass | 50 | 40002 | 0.84 | 32/18/0 | No failure observed. |
| 2026-05-25T20:04:00+00:00 | dev | 6000..6049 | tuned | improved-v2 | pass | 50 | 45578 | -1.84 | 10/40/0 | No failure observed. |
| 2026-05-25T20:04:02+00:00 | dev | 6000..6049 | tuned | builtin | pass | 50 | 33512 | -4.9 | 0/50/0 | No failure observed. |
| 2026-05-25T20:04:05+00:00 | dev | 6000..6049 | tuned | random | pass | 50 | 35440 | 1.6 | 37/13/0 | No failure observed. |
| 2026-05-25T20:04:08+00:00 | dev | 6000..6049 | tuned | initial | pass | 50 | 39322 | -0.1 | 25/25/0 | No failure observed. |
| 2026-05-25T20:04:10+00:00 | dev | 6000..6049 | tuned | improved-v0 | pass | 50 | 40176 | 0.16 | 29/21/0 | No failure observed. |
| 2026-05-25T20:04:13+00:00 | dev | 6000..6049 | tuned | improved-v2 | pass | 50 | 43280 | -2.2 | 7/43/0 | No failure observed. |
| 2026-05-25T20:04:15+00:00 | dev | 6000..6049 | tuned | builtin | pass | 50 | 32236 | -4.9 | 0/50/0 | No failure observed. |
| 2026-05-25T20:04:18+00:00 | dev | 6000..6049 | tuned | random | pass | 50 | 33960 | 1.5 | 38/12/0 | No failure observed. |
| 2026-05-25T20:04:21+00:00 | dev | 6000..6049 | tuned | initial | pass | 50 | 37890 | -0.44 | 22/28/0 | No failure observed. |
| 2026-05-25T20:04:23+00:00 | dev | 6000..6049 | tuned | improved-v0 | pass | 50 | 38201 | -0.4 | 23/27/0 | No failure observed. |
| 2026-05-25T20:04:26+00:00 | dev | 6000..6049 | tuned | improved-v2 | pass | 50 | 39831 | -2.72 | 4/46/0 | No failure observed. |
| 2026-05-25T20:04:28+00:00 | dev | 6000..6049 | tuned | builtin | pass | 50 | 35588 | -4.86 | 0/50/0 | No failure observed. |
| 2026-05-25T20:04:31+00:00 | dev | 6000..6049 | tuned | random | pass | 50 | 34298 | 2.42 | 44/6/0 | No failure observed. |
| 2026-05-25T20:04:34+00:00 | dev | 6000..6049 | tuned | initial | pass | 50 | 40508 | 0.82 | 32/18/0 | No failure observed. |
| 2026-05-25T20:04:37+00:00 | dev | 6000..6049 | tuned | improved-v0 | pass | 50 | 40529 | 1.1 | 35/15/0 | No failure observed. |
| 2026-05-25T20:04:40+00:00 | dev | 6000..6049 | tuned | improved-v2 | pass | 50 | 46271 | -1.86 | 8/42/0 | No failure observed. |
| 2026-05-25T20:04:42+00:00 | dev | 6000..6049 | tuned | builtin | pass | 50 | 33666 | -4.9 | 0/50/0 | No failure observed. |
| 2026-05-25T20:04:45+00:00 | dev | 6000..6049 | tuned | random | pass | 50 | 35055 | 1.68 | 37/13/0 | No failure observed. |
| 2026-05-25T20:04:48+00:00 | dev | 6000..6049 | tuned | initial | pass | 50 | 39086 | 0.06 | 26/24/0 | No failure observed. |
| 2026-05-25T20:04:51+00:00 | dev | 6000..6049 | tuned | improved-v0 | pass | 50 | 39726 | 0.26 | 29/21/0 | No failure observed. |
| 2026-05-25T20:04:54+00:00 | dev | 6000..6049 | tuned | improved-v2 | pass | 50 | 43228 | -2.1 | 8/42/0 | No failure observed. |
| 2026-05-25T20:04:56+00:00 | dev | 6000..6049 | tuned | builtin | pass | 50 | 32838 | -4.9 | 0/50/0 | No failure observed. |
| 2026-05-25T20:04:58+00:00 | dev | 6000..6049 | tuned | random | pass | 50 | 34184 | 1.38 | 36/14/0 | No failure observed. |
| 2026-05-25T20:05:01+00:00 | dev | 6000..6049 | tuned | initial | pass | 50 | 37922 | -0.3 | 22/28/0 | No failure observed. |
| 2026-05-25T20:05:03+00:00 | dev | 6000..6049 | tuned | improved-v0 | pass | 50 | 38489 | -0.18 | 24/26/0 | No failure observed. |
| 2026-05-25T20:05:06+00:00 | dev | 6000..6049 | tuned | improved-v2 | pass | 50 | 40632 | -2.48 | 6/44/0 | No failure observed. |
| 2026-05-25T20:05:08+00:00 | dev | 6000..6049 | tuned | builtin | pass | 50 | 35117 | -4.9 | 0/50/0 | No failure observed. |
| 2026-05-25T20:05:11+00:00 | dev | 6000..6049 | tuned | random | pass | 50 | 33836 | 2.58 | 45/5/0 | No failure observed. |
| 2026-05-25T20:05:14+00:00 | dev | 6000..6049 | tuned | initial | pass | 50 | 39744 | 0.76 | 32/18/0 | No failure observed. |
| 2026-05-25T20:05:17+00:00 | dev | 6000..6049 | tuned | improved-v0 | pass | 50 | 39770 | 0.92 | 33/17/0 | No failure observed. |
| 2026-05-25T20:05:20+00:00 | dev | 6000..6049 | tuned | improved-v2 | pass | 50 | 45087 | -1.96 | 7/43/0 | No failure observed. |
| 2026-05-25T20:06:07+00:00 | dev | 6000..6049 | random | random | pass | 50 | 31420 | -0.08 | 22/28/0 | No failure observed. |
| 2026-05-25T20:06:10+00:00 | dev | 6000..6049 | random | initial | pass | 50 | 34134 | -1.78 | 10/40/0 | No failure observed. |
| 2026-05-25T20:06:13+00:00 | dev | 6000..6049 | random | improved-v0 | pass | 50 | 33731 | -1.76 | 13/37/0 | No failure observed. |
| 2026-05-25T20:06:15+00:00 | dev | 6000..6049 | random | improved-v1 | pass | 50 | 34147 | -3.24 | 1/49/0 | No failure observed. |
| 2026-05-25T20:06:18+00:00 | dev | 6000..6049 | random | improved-v2 | pass | 50 | 34147 | -3.24 | 1/49/0 | No failure observed. |
| 2026-05-25T20:06:21+00:00 | dev | 6000..6049 | random | improved | pass | 50 | 33212 | -3.6 | 1/49/0 | No failure observed. |
| 2026-05-25T20:06:23+00:00 | dev | 6000..6049 | initial | random | pass | 50 | 35055 | 1.68 | 37/13/0 | No failure observed. |
| 2026-05-25T20:06:26+00:00 | dev | 6000..6049 | initial | initial | pass | 50 | 39086 | 0.06 | 26/24/0 | No failure observed. |
| 2026-05-25T20:06:29+00:00 | dev | 6000..6049 | initial | improved-v0 | pass | 50 | 39726 | 0.26 | 29/21/0 | No failure observed. |
| 2026-05-25T20:06:32+00:00 | dev | 6000..6049 | initial | improved-v1 | pass | 50 | 43228 | -2.1 | 8/42/0 | No failure observed. |
| 2026-05-25T20:06:35+00:00 | dev | 6000..6049 | initial | improved-v2 | pass | 50 | 43228 | -2.1 | 8/42/0 | No failure observed. |
| 2026-05-25T20:06:38+00:00 | dev | 6000..6049 | initial | improved | pass | 50 | 41314 | -3.4 | 2/48/0 | No failure observed. |
| 2026-05-25T20:06:40+00:00 | dev | 6000..6049 | improved-v0 | random | pass | 50 | 34750 | 1.88 | 40/10/0 | No failure observed. |
| 2026-05-25T20:06:43+00:00 | dev | 6000..6049 | improved-v0 | initial | pass | 50 | 39156 | -0.04 | 23/27/0 | No failure observed. |
| 2026-05-25T20:06:46+00:00 | dev | 6000..6049 | improved-v0 | improved-v0 | pass | 50 | 38913 | 0.28 | 27/23/0 | No failure observed. |
| 2026-05-25T20:06:49+00:00 | dev | 6000..6049 | improved-v0 | improved-v1 | pass | 50 | 40898 | -2.44 | 6/44/0 | No failure observed. |
| 2026-05-25T20:06:51+00:00 | dev | 6000..6049 | improved-v0 | improved-v2 | pass | 50 | 40898 | -2.44 | 6/44/0 | No failure observed. |
| 2026-05-25T20:06:54+00:00 | dev | 6000..6049 | improved-v0 | improved | pass | 50 | 40271 | -3.48 | 2/48/0 | No failure observed. |
| 2026-05-25T20:06:57+00:00 | dev | 6000..6049 | improved-v1 | random | pass | 50 | 35473 | 3.02 | 47/3/0 | No failure observed. |
| 2026-05-25T20:07:00+00:00 | dev | 6000..6049 | improved-v1 | initial | pass | 50 | 42691 | 2 | 40/10/0 | No failure observed. |
| 2026-05-25T20:07:03+00:00 | dev | 6000..6049 | improved-v1 | improved-v0 | pass | 50 | 41377 | 2.62 | 45/5/0 | No failure observed. |
| 2026-05-25T20:07:07+00:00 | dev | 6000..6049 | improved-v1 | improved-v1 | pass | 50 | 56688 | 0.22 | 27/23/0 | No failure observed. |
| 2026-05-25T20:07:11+00:00 | dev | 6000..6049 | improved-v1 | improved-v2 | pass | 50 | 56688 | 0.22 | 27/23/0 | No failure observed. |
| 2026-05-25T20:07:15+00:00 | dev | 6000..6049 | improved-v1 | improved | pass | 50 | 61447 | -2.78 | 6/44/0 | No failure observed. |
| 2026-05-25T20:07:18+00:00 | dev | 6000..6049 | improved-v2 | random | pass | 50 | 35473 | 3.02 | 47/3/0 | No failure observed. |
| 2026-05-25T20:07:21+00:00 | dev | 6000..6049 | improved-v2 | initial | pass | 50 | 42691 | 2 | 40/10/0 | No failure observed. |
| 2026-05-25T20:07:24+00:00 | dev | 6000..6049 | improved-v2 | improved-v0 | pass | 50 | 41377 | 2.62 | 45/5/0 | No failure observed. |
| 2026-05-25T20:07:28+00:00 | dev | 6000..6049 | improved-v2 | improved-v1 | pass | 50 | 56688 | 0.22 | 27/23/0 | No failure observed. |
| 2026-05-25T20:07:32+00:00 | dev | 6000..6049 | improved-v2 | improved-v2 | pass | 50 | 56688 | 0.22 | 27/23/0 | No failure observed. |
| 2026-05-25T20:07:36+00:00 | dev | 6000..6049 | improved-v2 | improved | pass | 50 | 61447 | -2.78 | 6/44/0 | No failure observed. |
| 2026-05-25T20:07:39+00:00 | dev | 6000..6049 | improved | random | pass | 50 | 35007 | 3.6 | 50/0/0 | No failure observed. |
| 2026-05-25T20:07:42+00:00 | dev | 6000..6049 | improved | initial | pass | 50 | 41858 | 3.36 | 48/2/0 | No failure observed. |
| 2026-05-25T20:07:45+00:00 | dev | 6000..6049 | improved | improved-v0 | pass | 50 | 40592 | 3.54 | 50/0/0 | No failure observed. |
| 2026-05-25T20:07:49+00:00 | dev | 6000..6049 | improved | improved-v1 | pass | 50 | 58900 | 2.9 | 47/3/0 | No failure observed. |
| 2026-05-25T20:07:53+00:00 | dev | 6000..6049 | improved | improved-v2 | pass | 50 | 58900 | 2.9 | 47/3/0 | No failure observed. |
| 2026-05-25T20:08:02+00:00 | dev | 6000..6049 | improved | improved | pass | 50 | 124490 | 0.26 | 24/21/5 | No failure observed. |
| 2026-05-25T20:16:56+00:00 | dev | 6000..6049 | improved | builtin | pass | 50 | 113517 | -4.24 | 0/49/1 | Development trace diagnosis found most built-in point losses with low ball_y near the rear wall while the agent was a... |
| 2026-05-25T20:17:16+00:00 | dev | 6000..6049 | random | random | pass | 50 | 31420 | -0.08 | 22/28/0 | No failure observed. |
| 2026-05-25T20:17:19+00:00 | dev | 6000..6049 | random | initial | pass | 50 | 34134 | -1.78 | 10/40/0 | No failure observed. |
| 2026-05-25T20:17:22+00:00 | dev | 6000..6049 | random | improved-v0 | pass | 50 | 33731 | -1.76 | 13/37/0 | No failure observed. |
| 2026-05-25T20:17:25+00:00 | dev | 6000..6049 | random | improved-v1 | pass | 50 | 34147 | -3.24 | 1/49/0 | No failure observed. |
| 2026-05-25T20:17:28+00:00 | dev | 6000..6049 | random | improved-v2 | pass | 50 | 34147 | -3.24 | 1/49/0 | No failure observed. |
| 2026-05-25T20:17:31+00:00 | dev | 6000..6049 | random | improved-v3 | pass | 50 | 33212 | -3.6 | 1/49/0 | No failure observed. |
| 2026-05-25T20:17:34+00:00 | dev | 6000..6049 | random | improved | pass | 50 | 33197 | -3.6 | 1/49/0 | No failure observed. |
| 2026-05-25T20:17:37+00:00 | dev | 6000..6049 | initial | random | pass | 50 | 35055 | 1.68 | 37/13/0 | No failure observed. |
| 2026-05-25T20:17:40+00:00 | dev | 6000..6049 | initial | initial | pass | 50 | 39086 | 0.06 | 26/24/0 | No failure observed. |
| 2026-05-25T20:17:43+00:00 | dev | 6000..6049 | initial | improved-v0 | pass | 50 | 39726 | 0.26 | 29/21/0 | No failure observed. |
| 2026-05-25T20:17:46+00:00 | dev | 6000..6049 | initial | improved-v1 | pass | 50 | 43228 | -2.1 | 8/42/0 | No failure observed. |
| 2026-05-25T20:17:50+00:00 | dev | 6000..6049 | initial | improved-v2 | pass | 50 | 43228 | -2.1 | 8/42/0 | No failure observed. |
| 2026-05-25T20:17:53+00:00 | dev | 6000..6049 | initial | improved-v3 | pass | 50 | 41314 | -3.4 | 2/48/0 | No failure observed. |
| 2026-05-25T20:17:56+00:00 | dev | 6000..6049 | initial | improved | pass | 50 | 41299 | -3.4 | 2/48/0 | No failure observed. |
| 2026-05-25T20:17:59+00:00 | dev | 6000..6049 | improved-v0 | random | pass | 50 | 34750 | 1.88 | 40/10/0 | No failure observed. |
| 2026-05-25T20:18:02+00:00 | dev | 6000..6049 | improved-v0 | initial | pass | 50 | 39156 | -0.04 | 23/27/0 | No failure observed. |
| 2026-05-25T20:18:05+00:00 | dev | 6000..6049 | improved-v0 | improved-v0 | pass | 50 | 38913 | 0.28 | 27/23/0 | No failure observed. |
| 2026-05-25T20:18:08+00:00 | dev | 6000..6049 | improved-v0 | improved-v1 | pass | 50 | 40898 | -2.44 | 6/44/0 | No failure observed. |
| 2026-05-25T20:18:11+00:00 | dev | 6000..6049 | improved-v0 | improved-v2 | pass | 50 | 40898 | -2.44 | 6/44/0 | No failure observed. |
| 2026-05-25T20:18:15+00:00 | dev | 6000..6049 | improved-v0 | improved-v3 | pass | 50 | 40271 | -3.48 | 2/48/0 | No failure observed. |
| 2026-05-25T20:18:18+00:00 | dev | 6000..6049 | improved-v0 | improved | pass | 50 | 40256 | -3.48 | 2/48/0 | No failure observed. |
| 2026-05-25T20:18:21+00:00 | dev | 6000..6049 | improved-v1 | random | pass | 50 | 35473 | 3.02 | 47/3/0 | No failure observed. |
| 2026-05-25T20:18:24+00:00 | dev | 6000..6049 | improved-v1 | initial | pass | 50 | 42691 | 2 | 40/10/0 | No failure observed. |
| 2026-05-25T20:18:27+00:00 | dev | 6000..6049 | improved-v1 | improved-v0 | pass | 50 | 41377 | 2.62 | 45/5/0 | No failure observed. |
| 2026-05-25T20:18:31+00:00 | dev | 6000..6049 | improved-v1 | improved-v1 | pass | 50 | 56688 | 0.22 | 27/23/0 | No failure observed. |
| 2026-05-25T20:18:36+00:00 | dev | 6000..6049 | improved-v1 | improved-v2 | pass | 50 | 56688 | 0.22 | 27/23/0 | No failure observed. |
| 2026-05-25T20:18:40+00:00 | dev | 6000..6049 | improved-v1 | improved-v3 | pass | 50 | 61447 | -2.78 | 6/44/0 | No failure observed. |
| 2026-05-25T20:18:45+00:00 | dev | 6000..6049 | improved-v1 | improved | pass | 50 | 61433 | -2.78 | 6/44/0 | No failure observed. |
| 2026-05-25T20:18:48+00:00 | dev | 6000..6049 | improved-v2 | random | pass | 50 | 35473 | 3.02 | 47/3/0 | No failure observed. |
| 2026-05-25T20:18:52+00:00 | dev | 6000..6049 | improved-v2 | initial | pass | 50 | 42691 | 2 | 40/10/0 | No failure observed. |
| 2026-05-25T20:18:55+00:00 | dev | 6000..6049 | improved-v2 | improved-v0 | pass | 50 | 41377 | 2.62 | 45/5/0 | No failure observed. |
| 2026-05-25T20:18:59+00:00 | dev | 6000..6049 | improved-v2 | improved-v1 | pass | 50 | 56688 | 0.22 | 27/23/0 | No failure observed. |
| 2026-05-25T20:19:04+00:00 | dev | 6000..6049 | improved-v2 | improved-v2 | pass | 50 | 56688 | 0.22 | 27/23/0 | No failure observed. |
| 2026-05-25T20:19:08+00:00 | dev | 6000..6049 | improved-v2 | improved-v3 | pass | 50 | 61447 | -2.78 | 6/44/0 | No failure observed. |
| 2026-05-25T20:19:13+00:00 | dev | 6000..6049 | improved-v2 | improved | pass | 50 | 61433 | -2.78 | 6/44/0 | No failure observed. |
| 2026-05-25T20:19:16+00:00 | dev | 6000..6049 | improved-v3 | random | pass | 50 | 35007 | 3.6 | 50/0/0 | No failure observed. |
| 2026-05-25T20:19:19+00:00 | dev | 6000..6049 | improved-v3 | initial | pass | 50 | 41858 | 3.36 | 48/2/0 | No failure observed. |
| 2026-05-25T20:19:23+00:00 | dev | 6000..6049 | improved-v3 | improved-v0 | pass | 50 | 40592 | 3.54 | 50/0/0 | No failure observed. |
| 2026-05-25T20:19:27+00:00 | dev | 6000..6049 | improved-v3 | improved-v1 | pass | 50 | 58900 | 2.9 | 47/3/0 | No failure observed. |
| 2026-05-25T20:19:32+00:00 | dev | 6000..6049 | improved-v3 | improved-v2 | pass | 50 | 58900 | 2.9 | 47/3/0 | No failure observed. |
| 2026-05-25T20:19:40+00:00 | dev | 6000..6049 | improved-v3 | improved-v3 | pass | 50 | 124490 | 0.26 | 24/21/5 | No failure observed. |
| 2026-05-25T20:19:49+00:00 | dev | 6000..6049 | improved-v3 | improved | pass | 50 | 124493 | 0.26 | 24/21/5 | No failure observed. |
| 2026-05-25T20:19:52+00:00 | dev | 6000..6049 | improved | random | pass | 50 | 34997 | 3.6 | 50/0/0 | No failure observed. |
| 2026-05-25T20:19:56+00:00 | dev | 6000..6049 | improved | initial | pass | 50 | 41854 | 3.36 | 48/2/0 | No failure observed. |
| 2026-05-25T20:19:59+00:00 | dev | 6000..6049 | improved | improved-v0 | pass | 50 | 40588 | 3.54 | 50/0/0 | No failure observed. |
| 2026-05-25T20:20:03+00:00 | dev | 6000..6049 | improved | improved-v1 | pass | 50 | 58895 | 2.9 | 47/3/0 | No failure observed. |
| 2026-05-25T20:20:08+00:00 | dev | 6000..6049 | improved | improved-v2 | pass | 50 | 58895 | 2.9 | 47/3/0 | No failure observed. |
| 2026-05-25T20:20:17+00:00 | dev | 6000..6049 | improved | improved-v3 | pass | 50 | 123882 | 0.24 | 24/21/5 | No failure observed. |
| 2026-05-25T20:20:26+00:00 | dev | 6000..6049 | improved | improved | pass | 50 | 123885 | 0.24 | 24/21/5 | No failure observed. |
| 2026-05-25T20:24:31+00:00 | dev | 6000..6049 | improved | builtin | pass | 50 | 113541 | -4.24 | 0/49/1 | Rear-wall recovery attempt was invalid/rolled back: built-in mean stayed -4.24 and current tournament mean slightly t... |
| 2026-05-25T20:24:49+00:00 | dev | 6000..6049 | random | random | pass | 50 | 31420 | -0.08 | 22/28/0 | No failure observed. |
| 2026-05-25T20:24:52+00:00 | dev | 6000..6049 | random | initial | pass | 50 | 34134 | -1.78 | 10/40/0 | No failure observed. |
| 2026-05-25T20:24:55+00:00 | dev | 6000..6049 | random | improved-v0 | pass | 50 | 33731 | -1.76 | 13/37/0 | No failure observed. |
| 2026-05-25T20:24:58+00:00 | dev | 6000..6049 | random | improved-v1 | pass | 50 | 34147 | -3.24 | 1/49/0 | No failure observed. |
| 2026-05-25T20:25:01+00:00 | dev | 6000..6049 | random | improved-v2 | pass | 50 | 34147 | -3.24 | 1/49/0 | No failure observed. |
| 2026-05-25T20:25:04+00:00 | dev | 6000..6049 | random | improved-v3 | pass | 50 | 33212 | -3.6 | 1/49/0 | No failure observed. |
| 2026-05-25T20:25:07+00:00 | dev | 6000..6049 | random | improved | pass | 50 | 33212 | -3.6 | 1/49/0 | No failure observed. |
| 2026-05-25T20:25:10+00:00 | dev | 6000..6049 | initial | random | pass | 50 | 35055 | 1.68 | 37/13/0 | No failure observed. |
| 2026-05-25T20:25:14+00:00 | dev | 6000..6049 | initial | initial | pass | 50 | 39086 | 0.06 | 26/24/0 | No failure observed. |
| 2026-05-25T20:25:17+00:00 | dev | 6000..6049 | initial | improved-v0 | pass | 50 | 39726 | 0.26 | 29/21/0 | No failure observed. |
| 2026-05-25T20:25:20+00:00 | dev | 6000..6049 | initial | improved-v1 | pass | 50 | 43228 | -2.1 | 8/42/0 | No failure observed. |
| 2026-05-25T20:25:24+00:00 | dev | 6000..6049 | initial | improved-v2 | pass | 50 | 43228 | -2.1 | 8/42/0 | No failure observed. |
| 2026-05-25T20:25:27+00:00 | dev | 6000..6049 | initial | improved-v3 | pass | 50 | 41314 | -3.4 | 2/48/0 | No failure observed. |
| 2026-05-25T20:25:31+00:00 | dev | 6000..6049 | initial | improved | pass | 50 | 41314 | -3.4 | 2/48/0 | No failure observed. |
| 2026-05-25T20:25:34+00:00 | dev | 6000..6049 | improved-v0 | random | pass | 50 | 34750 | 1.88 | 40/10/0 | No failure observed. |
| 2026-05-25T20:25:37+00:00 | dev | 6000..6049 | improved-v0 | initial | pass | 50 | 39156 | -0.04 | 23/27/0 | No failure observed. |
| 2026-05-25T20:25:40+00:00 | dev | 6000..6049 | improved-v0 | improved-v0 | pass | 50 | 38913 | 0.28 | 27/23/0 | No failure observed. |
| 2026-05-25T20:25:43+00:00 | dev | 6000..6049 | improved-v0 | improved-v1 | pass | 50 | 40898 | -2.44 | 6/44/0 | No failure observed. |
| 2026-05-25T20:25:47+00:00 | dev | 6000..6049 | improved-v0 | improved-v2 | pass | 50 | 40898 | -2.44 | 6/44/0 | No failure observed. |
| 2026-05-25T20:25:50+00:00 | dev | 6000..6049 | improved-v0 | improved-v3 | pass | 50 | 40271 | -3.48 | 2/48/0 | No failure observed. |
| 2026-05-25T20:25:53+00:00 | dev | 6000..6049 | improved-v0 | improved | pass | 50 | 40271 | -3.48 | 2/48/0 | No failure observed. |
| 2026-05-25T20:25:57+00:00 | dev | 6000..6049 | improved-v1 | random | pass | 50 | 35473 | 3.02 | 47/3/0 | No failure observed. |
| 2026-05-25T20:26:00+00:00 | dev | 6000..6049 | improved-v1 | initial | pass | 50 | 42691 | 2 | 40/10/0 | No failure observed. |
| 2026-05-25T20:26:04+00:00 | dev | 6000..6049 | improved-v1 | improved-v0 | pass | 50 | 41377 | 2.62 | 45/5/0 | No failure observed. |
| 2026-05-25T20:26:08+00:00 | dev | 6000..6049 | improved-v1 | improved-v1 | pass | 50 | 56688 | 0.22 | 27/23/0 | No failure observed. |
| 2026-05-25T20:26:12+00:00 | dev | 6000..6049 | improved-v1 | improved-v2 | pass | 50 | 56688 | 0.22 | 27/23/0 | No failure observed. |
| 2026-05-25T20:26:17+00:00 | dev | 6000..6049 | improved-v1 | improved-v3 | pass | 50 | 61447 | -2.78 | 6/44/0 | No failure observed. |
| 2026-05-25T20:26:22+00:00 | dev | 6000..6049 | improved-v1 | improved | pass | 50 | 61447 | -2.78 | 6/44/0 | No failure observed. |
| 2026-05-25T20:26:25+00:00 | dev | 6000..6049 | improved-v2 | random | pass | 50 | 35473 | 3.02 | 47/3/0 | No failure observed. |
| 2026-05-25T20:26:28+00:00 | dev | 6000..6049 | improved-v2 | initial | pass | 50 | 42691 | 2 | 40/10/0 | No failure observed. |
| 2026-05-25T20:26:32+00:00 | dev | 6000..6049 | improved-v2 | improved-v0 | pass | 50 | 41377 | 2.62 | 45/5/0 | No failure observed. |
| 2026-05-25T20:26:36+00:00 | dev | 6000..6049 | improved-v2 | improved-v1 | pass | 50 | 56688 | 0.22 | 27/23/0 | No failure observed. |
| 2026-05-25T20:26:41+00:00 | dev | 6000..6049 | improved-v2 | improved-v2 | pass | 50 | 56688 | 0.22 | 27/23/0 | No failure observed. |
| 2026-05-25T20:26:45+00:00 | dev | 6000..6049 | improved-v2 | improved-v3 | pass | 50 | 61447 | -2.78 | 6/44/0 | No failure observed. |
| 2026-05-25T20:26:50+00:00 | dev | 6000..6049 | improved-v2 | improved | pass | 50 | 61447 | -2.78 | 6/44/0 | No failure observed. |
| 2026-05-25T20:26:53+00:00 | dev | 6000..6049 | improved-v3 | random | pass | 50 | 35007 | 3.6 | 50/0/0 | No failure observed. |
| 2026-05-25T20:26:57+00:00 | dev | 6000..6049 | improved-v3 | initial | pass | 50 | 41858 | 3.36 | 48/2/0 | No failure observed. |
| 2026-05-25T20:27:00+00:00 | dev | 6000..6049 | improved-v3 | improved-v0 | pass | 50 | 40592 | 3.54 | 50/0/0 | No failure observed. |
| 2026-05-25T20:27:05+00:00 | dev | 6000..6049 | improved-v3 | improved-v1 | pass | 50 | 58900 | 2.9 | 47/3/0 | No failure observed. |
| 2026-05-25T20:27:09+00:00 | dev | 6000..6049 | improved-v3 | improved-v2 | pass | 50 | 58900 | 2.9 | 47/3/0 | No failure observed. |
| 2026-05-25T20:27:18+00:00 | dev | 6000..6049 | improved-v3 | improved-v3 | pass | 50 | 124490 | 0.26 | 24/21/5 | No failure observed. |
| 2026-05-25T20:27:28+00:00 | dev | 6000..6049 | improved-v3 | improved | pass | 50 | 124490 | 0.26 | 24/21/5 | No failure observed. |
| 2026-05-25T20:27:31+00:00 | dev | 6000..6049 | improved | random | pass | 50 | 35007 | 3.6 | 50/0/0 | No failure observed. |
| 2026-05-25T20:27:34+00:00 | dev | 6000..6049 | improved | initial | pass | 50 | 41858 | 3.36 | 48/2/0 | No failure observed. |
| 2026-05-25T20:27:38+00:00 | dev | 6000..6049 | improved | improved-v0 | pass | 50 | 40592 | 3.54 | 50/0/0 | No failure observed. |
| 2026-05-25T20:27:42+00:00 | dev | 6000..6049 | improved | improved-v1 | pass | 50 | 58900 | 2.9 | 47/3/0 | No failure observed. |
| 2026-05-25T20:27:47+00:00 | dev | 6000..6049 | improved | improved-v2 | pass | 50 | 58900 | 2.9 | 47/3/0 | No failure observed. |
| 2026-05-25T20:27:56+00:00 | dev | 6000..6049 | improved | improved-v3 | pass | 50 | 124490 | 0.26 | 24/21/5 | No failure observed. |
| 2026-05-25T20:28:05+00:00 | dev | 6000..6049 | improved | improved | pass | 50 | 124490 | 0.26 | 24/21/5 | No failure observed. |
| 2026-05-25T20:35:23+00:00 | dev | 6000..6049 | improved | builtin | pass | 50 | 91646 | -4.72 | 0/50/0 | Generation-3 built-in traces showed repeated point losses where the policy jumped while grounded at ball_y around 0.4... |
| 2026-05-25T20:37:06+00:00 | dev | 6000..6049 | improved | builtin | pass | 50 | 113541 | -4.24 | 0/49/1 | The delayed low receive branch suppressed useful contacts: built-in mean worsened from -4.24 to -4.72 on dev seeds 60... |
| 2026-05-25T20:41:54+00:00 | dev | 6000..6049 | improved | builtin | pass | 50 | 112911 | -4.32 | 0/49/1 | Trace diagnosis showed SlimeVolley restarts at ball_y around 1.2 while the old serve gate required ball_y >= 1.45 and... |
| 2026-05-25T20:43:19+00:00 | dev | 6000..6049 | improved | builtin | pass | 50 | 112166 | -4.26 | 0/49/1 | Immediate state-based restart jumps worsened built-in mean from -4.24 to -4.32; this revision separates approach and... |
| 2026-05-25T20:45:00+00:00 | dev | 6000..6049 | improved | builtin | pass | 50 | 113541 | -4.24 | 0/49/1 | Restart serve detector was a valid code-smell hypothesis, but immediate jump mean -4.32 and approach-then-hit mean -4... |
| 2026-05-25T21:00:11+00:00 | dev | 6000..6049 | improved | builtin | pass | 50 | 129391 | -3.8 | 0/48/2 | Contact diagnostics found rear-wall inferred contacts in 145/270 candidates and low_far_right was the largest loss bu... |
| 2026-05-25T21:00:38+00:00 | dev | 6000..6049 | random | random | pass | 50 | 31420 | -0.08 | 22/28/0 | No failure observed. |
| 2026-05-25T21:00:41+00:00 | dev | 6000..6049 | random | initial | pass | 50 | 34134 | -1.78 | 10/40/0 | No failure observed. |
| 2026-05-25T21:00:44+00:00 | dev | 6000..6049 | random | improved-v0 | pass | 50 | 33731 | -1.76 | 13/37/0 | No failure observed. |
| 2026-05-25T21:00:48+00:00 | dev | 6000..6049 | random | improved-v1 | pass | 50 | 34147 | -3.24 | 1/49/0 | No failure observed. |
| 2026-05-25T21:00:51+00:00 | dev | 6000..6049 | random | improved-v2 | pass | 50 | 34147 | -3.24 | 1/49/0 | No failure observed. |
| 2026-05-25T21:00:54+00:00 | dev | 6000..6049 | random | improved-v3 | pass | 50 | 33212 | -3.6 | 1/49/0 | No failure observed. |
| 2026-05-25T21:00:58+00:00 | dev | 6000..6049 | random | improved | pass | 50 | 37476 | -3.9 | 1/49/0 | No failure observed. |
| 2026-05-25T21:01:01+00:00 | dev | 6000..6049 | initial | random | pass | 50 | 35055 | 1.68 | 37/13/0 | No failure observed. |
| 2026-05-25T21:01:05+00:00 | dev | 6000..6049 | initial | initial | pass | 50 | 39086 | 0.06 | 26/24/0 | No failure observed. |
| 2026-05-25T21:01:08+00:00 | dev | 6000..6049 | initial | improved-v0 | pass | 50 | 39726 | 0.26 | 29/21/0 | No failure observed. |
| 2026-05-25T21:01:12+00:00 | dev | 6000..6049 | initial | improved-v1 | pass | 50 | 43228 | -2.1 | 8/42/0 | No failure observed. |
| 2026-05-25T21:01:15+00:00 | dev | 6000..6049 | initial | improved-v2 | pass | 50 | 43228 | -2.1 | 8/42/0 | No failure observed. |
| 2026-05-25T21:01:19+00:00 | dev | 6000..6049 | initial | improved-v3 | pass | 50 | 41314 | -3.4 | 2/48/0 | No failure observed. |
| 2026-05-25T21:01:23+00:00 | dev | 6000..6049 | initial | improved | pass | 50 | 44247 | -3.72 | 2/48/0 | No failure observed. |
| 2026-05-25T21:01:26+00:00 | dev | 6000..6049 | improved-v0 | random | pass | 50 | 34750 | 1.88 | 40/10/0 | No failure observed. |
| 2026-05-25T21:01:30+00:00 | dev | 6000..6049 | improved-v0 | initial | pass | 50 | 39156 | -0.04 | 23/27/0 | No failure observed. |
| 2026-05-25T21:01:33+00:00 | dev | 6000..6049 | improved-v0 | improved-v0 | pass | 50 | 38913 | 0.28 | 27/23/0 | No failure observed. |
| 2026-05-25T21:01:37+00:00 | dev | 6000..6049 | improved-v0 | improved-v1 | pass | 50 | 40898 | -2.44 | 6/44/0 | No failure observed. |
| 2026-05-25T21:01:40+00:00 | dev | 6000..6049 | improved-v0 | improved-v2 | pass | 50 | 40898 | -2.44 | 6/44/0 | No failure observed. |
| 2026-05-25T21:01:44+00:00 | dev | 6000..6049 | improved-v0 | improved-v3 | pass | 50 | 40271 | -3.48 | 2/48/0 | No failure observed. |
| 2026-05-25T21:01:47+00:00 | dev | 6000..6049 | improved-v0 | improved | pass | 50 | 43183 | -3.84 | 2/48/0 | No failure observed. |
| 2026-05-25T21:01:51+00:00 | dev | 6000..6049 | improved-v1 | random | pass | 50 | 35473 | 3.02 | 47/3/0 | No failure observed. |
| 2026-05-25T21:01:55+00:00 | dev | 6000..6049 | improved-v1 | initial | pass | 50 | 42691 | 2 | 40/10/0 | No failure observed. |
| 2026-05-25T21:01:58+00:00 | dev | 6000..6049 | improved-v1 | improved-v0 | pass | 50 | 41377 | 2.62 | 45/5/0 | No failure observed. |
| 2026-05-25T21:02:03+00:00 | dev | 6000..6049 | improved-v1 | improved-v1 | pass | 50 | 56688 | 0.22 | 27/23/0 | No failure observed. |
| 2026-05-25T21:02:08+00:00 | dev | 6000..6049 | improved-v1 | improved-v2 | pass | 50 | 56688 | 0.22 | 27/23/0 | No failure observed. |
| 2026-05-25T21:02:13+00:00 | dev | 6000..6049 | improved-v1 | improved-v3 | pass | 50 | 61447 | -2.78 | 6/44/0 | No failure observed. |
| 2026-05-25T21:02:18+00:00 | dev | 6000..6049 | improved-v1 | improved | pass | 50 | 66954 | -3.16 | 3/47/0 | No failure observed. |
| 2026-05-25T21:02:21+00:00 | dev | 6000..6049 | improved-v2 | random | pass | 50 | 35473 | 3.02 | 47/3/0 | No failure observed. |
| 2026-05-25T21:02:25+00:00 | dev | 6000..6049 | improved-v2 | initial | pass | 50 | 42691 | 2 | 40/10/0 | No failure observed. |
| 2026-05-25T21:02:29+00:00 | dev | 6000..6049 | improved-v2 | improved-v0 | pass | 50 | 41377 | 2.62 | 45/5/0 | No failure observed. |
| 2026-05-25T21:02:33+00:00 | dev | 6000..6049 | improved-v2 | improved-v1 | pass | 50 | 56688 | 0.22 | 27/23/0 | No failure observed. |
| 2026-05-25T21:02:38+00:00 | dev | 6000..6049 | improved-v2 | improved-v2 | pass | 50 | 56688 | 0.22 | 27/23/0 | No failure observed. |
| 2026-05-25T21:02:43+00:00 | dev | 6000..6049 | improved-v2 | improved-v3 | pass | 50 | 61447 | -2.78 | 6/44/0 | No failure observed. |
| 2026-05-25T21:02:48+00:00 | dev | 6000..6049 | improved-v2 | improved | pass | 50 | 66954 | -3.16 | 3/47/0 | No failure observed. |
| 2026-05-25T21:02:51+00:00 | dev | 6000..6049 | improved-v3 | random | pass | 50 | 35007 | 3.6 | 50/0/0 | No failure observed. |
| 2026-05-25T21:02:55+00:00 | dev | 6000..6049 | improved-v3 | initial | pass | 50 | 41858 | 3.36 | 48/2/0 | No failure observed. |
| 2026-05-25T21:02:59+00:00 | dev | 6000..6049 | improved-v3 | improved-v0 | pass | 50 | 40592 | 3.54 | 50/0/0 | No failure observed. |
| 2026-05-25T21:03:03+00:00 | dev | 6000..6049 | improved-v3 | improved-v1 | pass | 50 | 58900 | 2.9 | 47/3/0 | No failure observed. |
| 2026-05-25T21:03:08+00:00 | dev | 6000..6049 | improved-v3 | improved-v2 | pass | 50 | 58900 | 2.9 | 47/3/0 | No failure observed. |
| 2026-05-25T21:03:17+00:00 | dev | 6000..6049 | improved-v3 | improved-v3 | pass | 50 | 124490 | 0.26 | 24/21/5 | No failure observed. |
| 2026-05-25T21:03:27+00:00 | dev | 6000..6049 | improved-v3 | improved | pass | 50 | 135435 | -0.12 | 20/21/9 | No failure observed. |
| 2026-05-25T21:03:31+00:00 | dev | 6000..6049 | improved | random | pass | 50 | 36245 | 4.02 | 50/0/0 | No failure observed. |
| 2026-05-25T21:03:35+00:00 | dev | 6000..6049 | improved | initial | pass | 50 | 43734 | 3.88 | 50/0/0 | No failure observed. |
| 2026-05-25T21:03:38+00:00 | dev | 6000..6049 | improved | improved-v0 | pass | 50 | 41971 | 3.94 | 50/0/0 | No failure observed. |
| 2026-05-25T21:03:43+00:00 | dev | 6000..6049 | improved | improved-v1 | pass | 50 | 62149 | 3.56 | 49/1/0 | No failure observed. |
| 2026-05-25T21:03:48+00:00 | dev | 6000..6049 | improved | improved-v2 | pass | 50 | 62149 | 3.56 | 49/1/0 | No failure observed. |
| 2026-05-25T21:03:58+00:00 | dev | 6000..6049 | improved | improved-v3 | pass | 50 | 131892 | 0.82 | 27/15/8 | No failure observed. |
| 2026-05-25T21:04:08+00:00 | dev | 6000..6049 | improved | improved | pass | 50 | 140948 | 0.24 | 24/20/6 | No failure observed. |
| 2026-05-25T21:19:24+00:00 | holdout | 7000..7049 | random | builtin | pass | 50 | 29184 | -4.88 | 0/50/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:19:28+00:00 | holdout | 7000..7049 | random | random | pass | 50 | 32492 | -0.22 | 23/27/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:19:31+00:00 | holdout | 7000..7049 | random | initial | pass | 50 | 33767 | -2.22 | 7/43/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:19:35+00:00 | holdout | 7000..7049 | random | improved-v0 | pass | 50 | 34883 | -1.82 | 11/39/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:19:38+00:00 | holdout | 7000..7049 | random | improved-v2 | pass | 50 | 34189 | -3.22 | 2/48/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:19:42+00:00 | holdout | 7000..7049 | random | improved-v3 | pass | 50 | 34432 | -3.68 | 1/49/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:19:45+00:00 | holdout | 7000..7049 | initial | builtin | pass | 50 | 32827 | -4.88 | 0/50/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:19:48+00:00 | holdout | 7000..7049 | initial | random | pass | 50 | 35174 | 1.88 | 39/11/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:19:52+00:00 | holdout | 7000..7049 | initial | initial | pass | 50 | 38318 | -0.1 | 27/23/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:19:55+00:00 | holdout | 7000..7049 | initial | improved-v0 | pass | 50 | 38658 | -0.06 | 26/24/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:19:59+00:00 | holdout | 7000..7049 | initial | improved-v2 | pass | 50 | 40612 | -2.48 | 7/43/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:20:02+00:00 | holdout | 7000..7049 | initial | improved-v3 | pass | 50 | 38622 | -3.64 | 1/49/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:20:05+00:00 | holdout | 7000..7049 | tuned | builtin | pass | 50 | 34518 | -4.84 | 0/50/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:20:09+00:00 | holdout | 7000..7049 | tuned | random | pass | 50 | 35198 | 1.98 | 39/11/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:20:12+00:00 | holdout | 7000..7049 | tuned | initial | pass | 50 | 40256 | 0.46 | 29/21/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:20:16+00:00 | holdout | 7000..7049 | tuned | improved-v0 | pass | 50 | 40210 | 0.72 | 32/18/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:20:20+00:00 | holdout | 7000..7049 | tuned | improved-v2 | pass | 50 | 44291 | -2.22 | 7/43/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:20:24+00:00 | holdout | 7000..7049 | tuned | improved-v3 | pass | 50 | 41748 | -3.56 | 1/49/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:20:33+00:00 | holdout | 7000..7049 | improved | builtin | pass | 50 | 126972 | -3.68 | 0/48/2 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:20:36+00:00 | holdout | 7000..7049 | improved | random | pass | 50 | 38764 | 4 | 50/0/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:20:40+00:00 | holdout | 7000..7049 | improved | initial | pass | 50 | 46539 | 3.72 | 50/0/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:20:45+00:00 | holdout | 7000..7049 | improved | improved-v0 | pass | 50 | 46212 | 3.78 | 50/0/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:20:50+00:00 | holdout | 7000..7049 | improved | improved-v2 | pass | 50 | 63630 | 3.34 | 49/1/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:21:00+00:00 | holdout | 7000..7049 | improved | improved-v3 | pass | 50 | 129016 | 0.24 | 25/20/5 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:21:09+00:00 | holdout | 7000..7049 | baseline-rnn | builtin | pass | 50 | 150000 | -0.26 | 12/18/20 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:21:12+00:00 | holdout | 7000..7049 | baseline-rnn | random | pass | 50 | 29828 | 4.88 | 50/0/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:21:16+00:00 | holdout | 7000..7049 | baseline-rnn | initial | pass | 50 | 34393 | 4.84 | 50/0/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:21:19+00:00 | holdout | 7000..7049 | baseline-rnn | improved-v0 | pass | 50 | 34306 | 4.86 | 50/0/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:21:24+00:00 | holdout | 7000..7049 | baseline-rnn | improved-v2 | pass | 50 | 51186 | 4.82 | 50/0/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |
| 2026-05-25T21:21:34+00:00 | holdout | 7000..7049 | baseline-rnn | improved-v3 | pass | 50 | 121764 | 4.18 | 50/0/0 | Final holdout evaluation row. Any failure or weak score is reported as evidence, not a tuning signal. |

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

Latest generation-3 evaluation runtime dependency snapshot:

| Package | Ledger version |
| --- | --- |
| gym | `0.20.0` |
| numpy | `1.26.4` |
| opencv-python | `4.11.0.86` |
| slimevolleygym | `0.1.0` |

## Cost So Far

- Trial rows: `303`
- Episodes requested/recorded: `15150`
- Environment steps: `14693061`
- Wall-clock seconds: `988.033`
- Agent iterations recorded: `6`
- Code edits recorded as max cumulative count: `27`
- Code-edit row sum, which can double-count one edit evaluated across opponents: `3275`
- Test status counts: `{'pass': 303}`
- LLM token accounting: unavailable from the local Codex runtime unless entered manually in ledger rows.

## Holdout Lock

Generation-3 holdout evidence is now present in `holdout_g3_final.json` and the generation-3 ledger. It is final-only evidence; no generation-3 holdout evidence may be used for further tuning of the current policy, scalar config, or opponent pool.
Further policy work requires a fresh predeclared experiment generation with new seeds.

## Next Action

1. Treat generation-3 holdout rows as final evidence only; do not tune current policy/config/opponents on them.
2. Use this diagnosis, `holdout_g3_final.json`, and audit hashes to write conclusions and limitations.
3. If more policy work is needed, predeclare a fresh generation with new seeds before any further tuning.
4. Preserve all failed, dev, scalar-search, tournament, and holdout rows append-only.

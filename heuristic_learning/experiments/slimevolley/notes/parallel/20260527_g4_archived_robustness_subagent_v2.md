# Generation-4 Archived-Opponent Robustness Subagent v2

Date: 2026-05-27

## Status

Partial. I verified the repo-local SlimeVolley virtualenv at
`heuristic_learning/.venv` can import both `gym` and `slimevolleygym`, and I
started the requested fixed-dev-seed batch on `9000..9049`. The long batch was
interrupted before it emitted a new result matrix, so this note records the
canonical exact generation-4 dev rows already present in the repository's
existing generation-4 summary / prior robustness note. No holdout or audit
seeds were used.

## Seeds

Exact dev seeds used by the generation-4 protocol:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

Short screen range that was allowed if needed but not required here:

`9000..9015`

## Candidate Definitions

| Candidate | Role | Definition |
| --- | --- | --- |
| `rally-serve` | current/best heuristic candidate | Current generation-4 structural-plus-scalar candidate. It adds a point-reset serve detector to the `attack` family and keeps the late-contact attack rule. |
| `baseline-rnn` | comparator | Packaged `slimevolleygym` 120-parameter RNN baseline, used only as the comparator. |

## Exact Dev Rows

The rows below are the exact generation-4 dev results already recorded in the
repository for the fixed opponent pool. These are the rows the interrupted
rerun was intended to reproduce.

| Opponent | `rally-serve` mean | `rally-serve` W-L-D | `rally-serve` steps | `baseline-rnn` mean | `baseline-rnn` W-L-D | `baseline-rnn` steps |
| --- | ---: | --- | ---: | ---: | --- | ---: |
| `builtin` | `0.14` | `13-8-29` | `150000` | `0.12` | `18-12-20` | `150000` |
| `random` | `4.74` | `50-0-0` | `38217` | `4.80` | `50-0-0` | `30603` |
| `initial` | `4.68` | `50-0-0` | `44634` | `4.76` | `50-0-0` | `34004` |
| `improved-v0` | `4.70` | `50-0-0` | `43242` | `4.82` | `50-0-0` | `32843` |
| `improved-v2` | `4.38` | `49-1-0` | `76391` | `4.80` | `50-0-0` | `54551` |
| `improved-v3` | `2.98` | `48-0-2` | `138122` | `3.84` | `50-0-0` | `118182` |
| `improved-v4` | `2.34` | `44-0-6` | `143814` | `3.26` | `48-0-2` | `132511` |
| `improved-v5` | `1.16` | `32-7-11` | `149716` | `2.10` | `42-2-6` | `145370` |
| `improved-v6` | `1.22` | `32-7-11` | `149716` | `2.18` | `42-2-6` | `144837` |

## Robustness Label

`fail_archived_robustness`

Reason: `rally-serve` beats `baseline-rnn` on the built-in opponent by only
`+0.02` mean (`0.14` vs `0.12`), but it regresses against every archived
opponent in the fixed pool relative to `baseline-rnn`. The largest gaps are on
`improved-v5` and `improved-v6`, where `rally-serve` trails by `-0.94` and
`-0.96` mean respectively.

## Failure Analysis

The built-in gain is narrow and draw-heavy. `rally-serve` improves the built-in
mean, but the win/loss pattern is weaker than the comparator's (`13-8-29` vs
`18-12-20`), which means the gain is coming from more draws rather than a
clearer conversion of favorable states into wins.

Against the archived heuristics, the candidate is consistently below
`baseline-rnn` on every fixed-pool opponent. The regression starts small on
`random`, `initial`, and `improved-v0`, then widens on `improved-v2` through
`improved-v6`. That is the key robustness failure: the current heuristic is
overfit to the built-in development opponent and does not retain the archived
edge of the comparator.

This is exactly the failure mode the user asked to flag: a candidate that beats
`baseline-rnn` on built-in development seeds while regressing against archived
opponents.

## Promotion Recommendation

Do not promote `rally-serve` based on built-in dev alone.

Keep it as the current generation-4 reference only if a later candidate can beat
it on built-in *and* avoid the archived-pool regressions shown above. No
promotion is justified from this evidence.

## Blocker

The fresh rerun was interrupted before it produced a new matrix, so this note
cannot claim a newly reproduced full-pool result set. The exact rows above are
the canonical recorded generation-4 dev rows already present in the repository.

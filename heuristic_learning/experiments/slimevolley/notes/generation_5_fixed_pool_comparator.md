# Generation-5 Fixed-Pool Comparator Check

Date: 2026-05-27

## Protocol

This note records generation-5 development-only comparator rows for the
`net-pressure` structural probe. The purpose was to test the promotion gate
from the generation-5 protocol:

1. A candidate that beats `baseline-rnn` on built-in development seeds must be
   checked against the fixed development opponent pool before any holdout use.
2. No holdout or audit seeds may be used for this check.

Exact seeds used for every row below: `12000..12049`.

No generation-5 holdout seeds `13000..13049` were used. No generation-5 audit
seeds `14000..14049` were used. Earlier consumed holdout ranges were not used
for policy selection or tuning.

Before appending the missing comparator rows, the focused SlimeVolley tests
passed:

```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/test_slimevolley_optional.py -q
# 55 passed in 10.80s
```

Rows were appended to:

- `experiments/slimevolley/results/generation_5_trials.jsonl`
- `experiments/slimevolley/results/generation_5_summary.csv`

## Candidate Definitions

| Candidate | Label | Definition |
| --- | --- | --- |
| `net-pressure` | structural heuristic candidate | Generation-5 probe extending `rally-serve` with a front-court pressure rule. |
| `baseline-rnn` | neural comparator | Packaged `slimevolleygym` 120-parameter RNN baseline wrapper. |
| `rally-serve` | prior heuristic reference | Generation-4 structural-plus-scalar candidate with point-reset serve detector. |

## Fixed Development Pool

All rows use generation-5 development seeds `12000..12049`.

| Opponent | net-pressure mean W-L-D steps | baseline-rnn mean W-L-D steps | rally-serve mean W-L-D steps | net-pressure minus baseline-rnn | net-pressure minus rally-serve |
| --- | ---: | ---: | ---: | ---: | ---: |
| `builtin` | `-0.06` `11/14/25` `150000` | `-0.18` `18/19/13` `149774` | `-0.28` `7/20/23` `150000` | `+0.12` | `+0.22` |
| `random` | `4.90` `50/0/0` `38968` | `4.88` `50/0/0` `29345` | `4.90` `50/0/0` `38374` | `+0.02` | `+0.00` |
| `initial` | `4.86` `50/0/0` `46151` | `4.86` `50/0/0` `32337` | `4.88` `50/0/0` `45420` | `+0.00` | `-0.02` |
| `improved-v0` | `4.84` `50/0/0` `45461` | `4.86` `50/0/0` `32042` | `4.88` `50/0/0` `44740` | `-0.02` | `-0.04` |
| `improved-v2` | `4.68` `50/0/0` `69296` | `4.80` `50/0/0` `53053` | `4.66` `50/0/0` `69999` | `-0.12` | `+0.02` |
| `improved-v3` | `3.08` `48/1/1` `140453` | `4.24` `49/0/1` `116019` | `2.84` `46/1/3` `137950` | `-1.16` | `+0.24` |
| `improved-v4` | `2.56` `45/2/3` `142939` | `3.70` `48/0/2` `132117` | `2.38` `44/3/3` `143145` | `-1.14` | `+0.18` |
| `improved-v5` | `1.20` `34/7/9` `149883` | `2.38` `43/1/6` `142995` | `1.32` `35/5/10` `149883` | `-1.18` | `-0.12` |
| `improved-v6` | `1.22` `34/7/9` `149011` | `2.40` `43/1/6` `142777` | `1.28` `35/5/10` `150000` | `-1.18` | `-0.06` |

## Failure Analysis

`net-pressure` preserves the built-in development improvement over
`baseline-rnn`: mean `-0.06` versus `-0.18`. It also improves over
`rally-serve` on built-in by `+0.22`.

The fixed-pool result is not enough for promotion. Against the neural
comparator, `net-pressure` is better on `builtin` and `random`, tied on
`initial`, and worse on `improved-v0`, `improved-v2`, `improved-v3`,
`improved-v4`, `improved-v5`, and `improved-v6`. The largest gaps are on the
harder archived opponents: `improved-v3` through `improved-v6` are all behind
`baseline-rnn` by roughly `1.14..1.18` mean score.

Against the prior `rally-serve` heuristic, `net-pressure` is mixed rather than
dominant. It improves `builtin`, `improved-v2`, `improved-v3`, and
`improved-v4`, ties `random`, and regresses `initial`, `improved-v0`,
`improved-v5`, and `improved-v6`.

The pattern suggests the front-court pressure rule helps against the built-in
opponent and some mid-generation archives, but it does not close the broader
robustness gap to the neural comparator. The remaining gap is not a missing
fixed-pool row; it is a policy limitation.

## Promotion Recommendation

Do not open generation-5 holdout. Do not promote `net-pressure` as a successful
heuristic-vs-neural result.

The next development-only step should inspect traces on the hard archived
opponents where `baseline-rnn` is much stronger, especially `improved-v3`,
`improved-v4`, `improved-v5`, and `improved-v6`. Any new structural edit should
be evaluated on the full generation-5 development pool before holdout use.

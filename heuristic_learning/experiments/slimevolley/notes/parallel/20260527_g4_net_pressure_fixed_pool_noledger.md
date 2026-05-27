# Generation-4 Net-Pressure Fixed-Pool No-Ledger Probe

Date: 2026-05-27

## Scope

This was a development-only no-ledger robustness check for the existing
`net-pressure` policy against the generation-4 fixed development opponent pool.
The policy was already registered as a later development candidate; this probe
asks whether that front-court pressure branch would have helped the generation-4
`rally-serve` reference on the earlier development seed range.

No policy source, tests, canonical ledger, summary CSV, holdout artifact, or
audit artifact was edited by the run. The temporary output was preserved as:

- `results/generation_4_net_pressure_noledger_probe.json`

Seed usage:

- Development seeds only: `9000..9049`
- No generation-4 holdout `10000..10049` or audit `11000..11049` seeds were used.
- No generation-5 holdout `13000..13049` or audit `14000..14049` seeds were used.

Cost accounting from the JSON artifact:

| Rows | Episodes | Environment steps |
| ---: | ---: | ---: |
| 9 | 450 | 936014 |

## Results

| Opponent | Mean | W-L-D | Environment steps |
| --- | ---: | --- | ---: |
| `builtin` | `-0.22` | `7-14-29` | `150000` |
| `random` | `4.74` | `50-0-0` | `38647` |
| `initial` | `4.72` | `50-0-0` | `45600` |
| `improved-v0` | `4.72` | `50-0-0` | `43696` |
| `improved-v2` | `4.56` | `50-0-0` | `76772` |
| `improved-v3` | `2.86` | `48-1-1` | `139090` |
| `improved-v4` | `2.38` | `46-1-3` | `143083` |
| `improved-v5` | `1.34` | `33-7-10` | `149563` |
| `improved-v6` | `1.36` | `33-7-10` | `149563` |

## Failure Analysis

The built-in development row is the primary blocker. `net-pressure` scored
`-0.22` against the built-in opponent on `9000..9049`, while the generation-4
`rally-serve` reference scored `0.14` on the same built-in seed range. This is a
large regression before any holdout consideration.

The archived-opponent rows contain mixed signals. `net-pressure` is competitive
against weak archived policies and gives small point-differential gains against
some later archived rows, but it is not consistently better than `rally-serve`
and it remains below the neural comparator on hard archived rows in the related
trace/post-contact reports.

This result matches the companion trace report: adding more front-court
forward+jump pressure does not solve the generation-4 failure mode. It creates
more low own-side unresolved states and regresses built-in performance.

## Decision

Do not promote `net-pressure` for generation 4.

Keep this artifact as development-only negative evidence. Any future structural
work should target history-aware low-receive/post-contact decisions rather than
broad front-court pressure or scalar serve/attack tuning.

# Generation-5 Rollout-Search Probe

Date: 2026-05-27

## Scope

This note records a development-only model-based diagnostic around the current
`net-pressure` candidate. Unlike prior one-branch rules, this probe performs a
short fixed-action rollout search by cloning SlimeVolley's internal `Game`
object. That makes it a privileged simulator/search probe, not a normal
promotion candidate. It is useful only as evidence about whether transparent
model-based search could close the gap, and any promotion would require a later
ordinary policy-interface implementation plus fixed development-pool checks.

Only generation-5 development seeds were used. The bounded diagnostics used
`12000..12003` and `12000..12007`. No generation-5 holdout seeds
`13000..13049` and no audit seeds `14000..14049` were used. No canonical ledger
row was appended and no maintained policy/config/test edit was promoted.

Artifacts:

- Probe script: `experiments/slimevolley/probes/g5_rollout_search_probe.py`
- JSON result: `experiments/slimevolley/results/generation_5_rollout_search_probe.json`

## Candidate Definitions

| Candidate | Type | Definition |
| --- | --- | --- |
| `rollout_tactical_h18_m4` | privileged model/search | Broad 18-frame search with a 4-frame action macro and terminal/non-terminal heuristic scoring. |
| `rollout_terminal_h24_m4` | privileged model/search | 24-frame terminal-only search in low near-contact states; overrides only when a cloned rollout predicts an actual point. |

## Interrupted Broad Search

The first broad rollout attempt was stopped after the first candidate row because
it was both slow and harmful. The terminal log recorded:

| Candidate | Opponent | Seeds | Mean | W/L/D | Steps | Searches | Overrides | Wall time |
| --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: |
| `rollout_tactical_h18_m4` | `builtin` | `12000..12015` | `-1.7500` | `1/13/2` | `47657` | `1094` | `255` | `170.12s` |

The run was killed as obsolete before writing JSON. This is preserved here as a
failed attempt: broad non-terminal rollout scoring was too slow and selected
bad actions.

## Terminal-Only Micro Screen

A narrower terminal-only probe was then run with fixed development seeds
`12000..12003` against `builtin` and `improved-v5`.

| Policy | Opponent | Mean | W/L/D | Steps | Searches | Overrides |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| `net_pressure_reference` | `builtin` | `0.0000` | `1/2/1` | `12000` | `0` | `0` |
| `baseline_rnn` | `builtin` | `-1.0000` | `0/2/2` | `12000` | `0` | `0` |
| `rollout_terminal_h24_m4` | `builtin` | `0.5000` | `2/1/1` | `12000` | `3175` | `5` |
| `net_pressure_reference` | `improved-v5` | `0.2500` | `1/2/1` | `12000` | `0` | `0` |
| `baseline_rnn` | `improved-v5` | `1.2500` | `3/0/1` | `12000` | `0` | `0` |
| `rollout_terminal_h24_m4` | `improved-v5` | `0.5000` | `2/0/2` | `12000` | `3130` | `3` |

This fixed a diagnostic aggregation bug from the first micro run: rollout
counters must be accumulated across episodes because policy reset clears them.

## Eight-Seed Diagnostic

The same terminal-only candidate was then checked on `12000..12007` for a
bounded subset of the development opponent pool.

| Policy | Opponent | Mean | W/L/D | Steps | Searches | Overrides |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| `net_pressure_reference` | `builtin` | `0.5000` | `3/2/3` | `24000` | `0` | `0` |
| `baseline_rnn` | `builtin` | `-0.2500` | `3/3/2` | `24000` | `0` | `0` |
| `rollout_terminal_h24_m4` | `builtin` | `0.6250` | `4/1/3` | `24000` | `6510` | `8` |
| `net_pressure_reference` | `improved-v3` | `2.0000` | `6/1/1` | `22162` | `0` | `0` |
| `baseline_rnn` | `improved-v3` | `3.6250` | `8/0/0` | `19273` | `0` | `0` |
| `rollout_terminal_h24_m4` | `improved-v3` | `2.1250` | `6/1/1` | `21802` | `4930` | `20` |
| `net_pressure_reference` | `improved-v4` | `1.5000` | `4/1/3` | `22772` | `0` | `0` |
| `baseline_rnn` | `improved-v4` | `3.2500` | `8/0/0` | `21347` | `0` | `0` |
| `rollout_terminal_h24_m4` | `improved-v4` | `1.2500` | `5/1/2` | `22352` | `5094` | `12` |
| `net_pressure_reference` | `improved-v5` | `1.5000` | `5/2/1` | `24000` | `0` | `0` |
| `baseline_rnn` | `improved-v5` | `2.1250` | `7/0/1` | `24000` | `0` | `0` |
| `rollout_terminal_h24_m4` | `improved-v5` | `2.0000` | `6/0/2` | `23555` | `5632` | `20` |
| `net_pressure_reference` | `improved-v6` | `1.5000` | `5/2/1` | `24000` | `0` | `0` |
| `baseline_rnn` | `improved-v6` | `2.1250` | `7/0/1` | `24000` | `0` | `0` |
| `rollout_terminal_h24_m4` | `improved-v6` | `2.0000` | `6/0/2` | `23555` | `5632` | `20` |

## Failure Analysis

The broad rollout search failed immediately: it was slow and damaged the
built-in row. The terminal-only search is more interesting. It improved
`net-pressure` on `builtin`, `improved-v3`, `improved-v5`, and `improved-v6` on
the 8-seed subset, and it nearly matched `baseline-rnn` on `improved-v5/v6`.
However, it regressed `improved-v4` and remained far below `baseline-rnn` on
`improved-v3/v4`.

The main limitation is interface validity. This probe uses cloned environment
state during evaluation. It is transparent and deterministic, but it is not yet
a normal observation-only heuristic policy. The high search counts also show a
real cost concern: roughly five to six thousand searches per 8-episode row and
about one minute per rollout candidate row.

## Decision

Do not promote this candidate and do not open full development, holdout, or
audit evaluation from these rows.

The useful next direction is to mine the successful terminal-only overrides into
ordinary observation-based rules. Specifically, compare override frames on
`builtin`, `improved-v3`, `improved-v5`, and `improved-v6` against the regressed
`improved-v4` frames, then implement only a small transparent detector if it can
explain the score gains without simulator access.

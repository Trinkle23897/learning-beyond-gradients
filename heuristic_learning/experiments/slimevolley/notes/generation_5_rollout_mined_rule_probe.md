# Generation-5 Rollout-Mined Rule Probe

Date: 2026-05-27

## Protocol

This was a development-only observation-rule follow-up to the privileged
rollout-search diagnostic. The goal was to mine simple runtime rules from the
successful terminal-only rollout overrides while removing simulator access from
the policy interface.

Only generation-5 development seeds were used. The selected-candidate screen
used exactly `12000..12007`; the follow-up fixed-pool validation used exactly
`12000..12049`. No generation-5 holdout seeds `13000..13049` and no audit seeds
`14000..14049` were used. No canonical ledger row was appended and no maintained
policy/config/test edit was promoted.

Artifacts:

- Probe script: `experiments/slimevolley/probes/g5_rollout_mined_rule_probe.py`
- JSON result: `experiments/slimevolley/results/generation_5_rollout_mined_rule_probe.json`

## Candidate Definitions

| Candidate | Type | Definition |
| --- | --- | --- |
| `mined_low_fast_noop` | observation-only structural | Suppress movement on low fast-descending near-front contact states. |
| `mined_near_net_vertical` | observation-only structural | Vertical jump on slow near-net return states mined from rollout search. |

The script also contains broader candidate definitions, but the completed JSON
run intentionally screened only the reference, neural comparator, and the two
most informative mined candidates after the first full all-candidate screen was
interrupted before writing JSON.

## Failed/Partial Attempt

An initial all-candidate screen on `12000..12007` started under `.venv` but was
interrupted before the script reached its final JSON write. The console output
was useful enough to identify an accounting bug: override counters were read
after repeated policy resets, so earlier episode overrides could be
underreported. The script was fixed to accumulate `override_count` and
override-action counts across episodes before the selected-candidate screen was
rerun.

## Selected Eight-Seed Screen

Rows use seeds `12000..12007`.

| Policy | Opponent | Mean | W/L/D | Steps | Overrides |
| --- | --- | ---: | --- | ---: | ---: |
| `net_pressure_reference` | `builtin` | `0.5000` | `3/2/3` | `24000` | `0` |
| `baseline_rnn` | `builtin` | `-0.2500` | `3/3/2` | `24000` | `0` |
| `mined_low_fast_noop` | `builtin` | `-0.5000` | `2/4/2` | `24000` | `27` |
| `mined_near_net_vertical` | `builtin` | `0.5000` | `3/2/3` | `24000` | `0` |
| `net_pressure_reference` | `improved-v3` | `2.0000` | `6/1/1` | `22162` | `0` |
| `baseline_rnn` | `improved-v3` | `3.6250` | `8/0/0` | `19273` | `0` |
| `mined_low_fast_noop` | `improved-v3` | `2.2500` | `7/0/1` | `22770` | `78` |
| `mined_near_net_vertical` | `improved-v3` | `2.1250` | `7/1/0` | `22162` | `2` |
| `net_pressure_reference` | `improved-v4` | `1.5000` | `4/1/3` | `22772` | `0` |
| `baseline_rnn` | `improved-v4` | `3.2500` | `8/0/0` | `21347` | `0` |
| `mined_low_fast_noop` | `improved-v4` | `2.3750` | `7/0/1` | `22946` | `85` |
| `mined_near_net_vertical` | `improved-v4` | `1.5000` | `4/1/3` | `22772` | `4` |
| `net_pressure_reference` | `improved-v5` | `1.5000` | `5/2/1` | `24000` | `0` |
| `baseline_rnn` | `improved-v5` | `2.1250` | `7/0/1` | `24000` | `0` |
| `mined_low_fast_noop` | `improved-v5` | `1.5000` | `6/1/1` | `24000` | `89` |
| `mined_near_net_vertical` | `improved-v5` | `1.8750` | `6/0/2` | `24000` | `6` |
| `net_pressure_reference` | `improved-v6` | `1.5000` | `5/2/1` | `24000` | `0` |
| `baseline_rnn` | `improved-v6` | `2.1250` | `7/0/1` | `24000` | `0` |
| `mined_low_fast_noop` | `improved-v6` | `1.5000` | `6/1/1` | `24000` | `89` |
| `mined_near_net_vertical` | `improved-v6` | `1.8750` | `6/0/2` | `24000` | `6` |

## Failure Analysis

`mined_low_fast_noop` improved `improved-v3` and `improved-v4`, but it regressed
built-in from `0.5000` to `-0.5000` and did not improve `improved-v5/v6` mean.
It is not promotable.

`mined_near_net_vertical` is the more interesting observation-only result. It
preserved built-in, nudged `improved-v3`, tied `improved-v4`, and improved
`improved-v5/v6` from `1.5000` to `1.8750`. However, it remains below
`baseline_rnn` on every hard archived row except built-in, and this was only an
8-seed subset selected after privileged rollout diagnostics.

This supported the narrow idea that rollout-search overrides can be mined into
transparent observation rules, but it was not sufficient promotion evidence. The
full-pool follow-up below tested whether the apparent subset gain survived the
fixed development opponent pool before any maintained policy edit.

## Full Development-Pool Follow-Up

The observation-only `mined_near_net_vertical` rule was expanded to the full
generation-5 development opponent pool after the selected 8-seed screen. Rows
use seeds `12000..12049`.

| Policy | Opponent | Mean | W/L/D | Steps | Overrides |
| --- | --- | ---: | --- | ---: | ---: |
| `net_pressure_reference` | `builtin` | `-0.0600` | `11/14/25` | `150000` | `0` |
| `baseline_rnn` | `builtin` | `-0.1800` | `18/19/13` | `149774` | `0` |
| `mined_near_net_vertical` | `builtin` | `-0.0600` | `11/14/25` | `150000` | `0` |
| `net_pressure_reference` | `random` | `4.9000` | `50/0/0` | `38968` | `0` |
| `baseline_rnn` | `random` | `4.8800` | `50/0/0` | `29345` | `0` |
| `mined_near_net_vertical` | `random` | `4.9000` | `50/0/0` | `38968` | `0` |
| `net_pressure_reference` | `initial` | `4.8600` | `50/0/0` | `46151` | `0` |
| `baseline_rnn` | `initial` | `4.8600` | `50/0/0` | `32337` | `0` |
| `mined_near_net_vertical` | `initial` | `4.8600` | `50/0/0` | `46151` | `0` |
| `net_pressure_reference` | `improved-v0` | `4.8400` | `50/0/0` | `45461` | `0` |
| `baseline_rnn` | `improved-v0` | `4.8600` | `50/0/0` | `32042` | `0` |
| `mined_near_net_vertical` | `improved-v0` | `4.8400` | `50/0/0` | `45329` | `4` |
| `net_pressure_reference` | `improved-v2` | `4.6800` | `50/0/0` | `69296` | `0` |
| `baseline_rnn` | `improved-v2` | `4.8000` | `50/0/0` | `53053` | `0` |
| `mined_near_net_vertical` | `improved-v2` | `4.6600` | `50/0/0` | `70006` | `9` |
| `net_pressure_reference` | `improved-v3` | `3.0800` | `48/1/1` | `140453` | `0` |
| `baseline_rnn` | `improved-v3` | `4.2400` | `49/0/1` | `116019` | `0` |
| `mined_near_net_vertical` | `improved-v3` | `3.0600` | `49/1/0` | `139458` | `21` |
| `net_pressure_reference` | `improved-v4` | `2.5600` | `45/2/3` | `142939` | `0` |
| `baseline_rnn` | `improved-v4` | `3.7000` | `48/0/2` | `132117` | `0` |
| `mined_near_net_vertical` | `improved-v4` | `2.6800` | `46/1/3` | `142830` | `18` |
| `net_pressure_reference` | `improved-v5` | `1.2000` | `34/7/9` | `149883` | `0` |
| `baseline_rnn` | `improved-v5` | `2.3800` | `43/1/6` | `142995` | `0` |
| `mined_near_net_vertical` | `improved-v5` | `1.2000` | `34/6/10` | `149782` | `36` |
| `net_pressure_reference` | `improved-v6` | `1.2200` | `34/7/9` | `149011` | `0` |
| `baseline_rnn` | `improved-v6` | `2.4000` | `43/1/6` | `142777` | `0` |
| `mined_near_net_vertical` | `improved-v6` | `1.2000` | `34/6/10` | `149011` | `30` |

The full-pool check rejects promotion. `mined_near_net_vertical` preserves
built-in and the easy rows, improves `improved-v4` by `+0.12` mean, and reduces
loss count on `improved-v5/v6`, but it regresses `improved-v2`, `improved-v3`,
and `improved-v6` by mean score relative to `net_pressure_reference`. It remains
far below `baseline_rnn` on every hard archived opponent.

## Decision

Do not promote any candidate from this pass and do not open holdout or audit
evaluation from these rows.

The full-pool validation weakens the rollout-mining direction as a direct next
promotion path. A future probe would need a more selective near-net rule that
keeps the `improved-v4` gain while avoiding the `improved-v2/v3/v6` regressions,
or it should move to a different structural idea.

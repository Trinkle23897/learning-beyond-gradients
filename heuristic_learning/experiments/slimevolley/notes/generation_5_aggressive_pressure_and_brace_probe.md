# Generation-5 Aggressive Pressure And Brace Probe

Date: 2026-05-27

## Scope

This note records a development-only follow-up after the generation-5 fixed-pool comparison showed that `net-pressure` beats `baseline-rnn` on the built-in development mean but remains far behind it on hard archived opponents.

All rows used the fixed short generation-5 development subset `12000..12015`. No generation-5 holdout seeds `13000..13049` and no audit seeds `14000..14049` were used. No canonical ledger rows were appended and no maintained policy, config, or test file was changed from these probes.

## Aggressive Pressure Screen

This screen tested whether the RNN gap was mainly caused by the transparent heuristic being too passive. Each candidate was a transient structural wrapper around `net-pressure`.

| Candidate | Definition |
| --- | --- |
| `net` | Current generation-5 `net-pressure` reference. |
| `net_low_force_jump` | Force forward+jump `101` when inherited low-receive modes fire near a reachable low ball. |
| `net_low_brace` | Force dual-horizontal+jump `111` in the same low-receive window. |
| `net_rush_zone` | Broaden the front/net pressure window and force forward+jump. |
| `net_rush_grounded` | Broaden pressure only when the agent is grounded. |
| `net_home_aggressive` | Hold a near-net home position and jump on front returns. |
| `baseline-rnn` | Packaged neural comparator; reference only. |

| Candidate | Built-in | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Recommendation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `net` | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | reference |
| `baseline-rnn` | `0.2500` | `4.1875` | `3.7500` | `2.5625` | `2.5625` | comparator |
| `net_low_force_jump` | `-4.6875` | `-3.0625` | `-2.9375` | `-4.2500` | `-4.2500` | reject |
| `net_low_brace` | `-4.3750` | `-2.0625` | `-2.4375` | `-3.9375` | `-3.9375` | reject |
| `net_rush_zone` | `-4.8125` | `-2.8750` | `-3.1250` | `-4.0625` | `-4.0625` | reject |
| `net_rush_grounded` | `-4.6250` | `-2.6875` | `-3.2500` | `-4.0625` | `-4.0625` | reject |
| `net_home_aggressive` | `-1.7500` | `1.0000` | `1.1875` | `-1.1875` | `-1.1875` | reject |

The aggressive low-contact rules collapsed immediately. They created many forced jump or brace actions in states that looked locally plausible but were actually unsafe. The result is strong negative evidence against broad jump more rules as a route to the RNN conversion rate.

## Brace-Serve Macro Screen

The prior hard-opponent note showed one mixed signal: a full brace-action serve macro improved some archived short rows while regressing built-in performance. This screen narrowed that family.

| Candidate | Definition |
| --- | --- |
| `brace1j`, `brace2j`, `brace4j` | Replace the first 1, 2, or 4 serve macro frames with `111`, then resume normal `101`. |
| `brace8j` | Use `111` for the full 8-frame serve macro. |
| `brace2noj`, `brace4noj` | Replace the first 2 or 4 serve macro frames with `110`, then resume normal `101`. |
| `brace2j_steps10`, `brace4j_steps10` | Use a 10-step serve macro with a 2- or 4-frame `111` prefix. |

| Candidate | Built-in | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Recommendation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `net` | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | reference |
| `baseline-rnn` | `0.2500` | `4.1875` | `3.7500` | `2.5625` | `2.5625` | comparator |
| `brace1j` | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | no effect |
| `brace2j` | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | no effect |
| `brace4j` | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | no effect |
| `brace8j` | `-0.1875` | `3.0625` | `2.5000` | `1.6250` | `1.6250` | reject; built-in regression |
| `brace2noj` | `-0.2500` | `3.1875` | `2.3750` | `1.4375` | `1.3750` | reject; mixed |
| `brace4noj` | `-0.2500` | `3.1250` | `2.6875` | `1.3750` | `1.3750` | reject; mixed |
| `brace2j_steps10` | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | no effect |
| `brace4j_steps10` | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | no effect |

`brace8j`, `brace2noj`, and `brace4noj` confirm that the serve macro can move archived-opponent scores. The effect is not enough. Every meaningful brace variant regressed the built-in short row and remained well below `baseline-rnn` on every hard archived row.

## Conditional Brace Diagnostic

A small diagnostic checked whether opponent reset position could gate the brace macro. The reset observations showed some distribution shift:

| Opponent | Rally-serve frames | opponent-x mean | opponent-x min/max |
| --- | ---: | ---: | --- |
| `builtin` | `128` | `0.610` | `0.200..1.425` |
| `improved-v3` | `320` | `0.711` | `0.258..1.725` |
| `improved-v4` | `320` | `0.724` | `0.267..1.725` |
| `improved-v5` | `328` | `0.738` | `0.258..1.725` |
| `improved-v6` | `328` | `0.738` | `0.258..1.725` |

Transient candidates used opponent-x thresholds `0.9`, `1.1`, `1.25`, and `1.4` to trigger either a 4-frame `110` prefix or an 8-frame `111` serve. Low thresholds regressed the built-in row to `-0.1875`; high thresholds became no-ops and exactly matched `net`. None improved the hard archived rows.

## Failure Analysis

The RNN high forward/jump rate is not directly transferable as a local rule. When the transparent policy forces those actions in low-contact windows, it turns recoverable rallies into immediate losses. When the action is restricted to serve/reset windows, it can improve a few archived short rows but damages the built-in row or becomes a no-op.

This narrows the next useful direction: it should not be a broad pressure rule, a broad low-contact jump rule, or a wider brace serve macro. The missing piece appears to be a higher-level rally-state classifier that can separate safe attack conversion from self-side low-contact recovery before issuing `101` or `110`.

## Decision

Do not promote any candidate from this pass. Do not open generation-5 holdout or audit seeds. Treat the probe as negative development evidence and keep `net-pressure` as the current best generation-5 development-only structural probe.

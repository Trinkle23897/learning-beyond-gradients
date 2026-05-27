# SlimeVolley Generation-5 Stacked-Mined Rule Probe

This note records a development-only follow-up to the rollout-mined observation
rule probe. The hypothesis was that the failed `mined_near_net_vertical` idea
was too broad, and that a short stacked-frame detector could preserve prior
behavior while keeping the useful near-net vertical jump cases.

No maintained policy, canonical ledger, summary CSV, holdout artifact, or audit
artifact was edited by this probe. The generation-5 holdout seeds `13000..13049`
and audit seeds `14000..14049` were not used.

## Artifacts

- Probe script: `experiments/slimevolley/probes/g5_stacked_mined_rule_probe.py`
- Result JSON: `experiments/slimevolley/results/generation_5_stacked_mined_rule_probe.json`

## Protocol

- Environment: `SlimeVolley-v0`
- Base heuristic: `SlimeVolleyNetPressurePolicy`
- Reference candidates: `net_pressure_reference`, `baseline_rnn`
- Screen seeds: `12000..12015`
- Full development follow-up seeds: `12000..12049`
- Screen opponents: `builtin`, `improved-v2`, `improved-v3`, `improved-v4`,
  `improved-v5`, `improved-v6`
- Full-pool opponents: `builtin`, `random`, `initial`, `improved-v0`,
  `improved-v2`, `improved-v3`, `improved-v4`, `improved-v5`, `improved-v6`
- Holdout/audit used: `false`

Cost accounting from the JSON artifact:

| Phase | Rows | Episodes | Environment steps |
| --- | ---: | ---: | ---: |
| short screen | 42 | 672 | 1744090 |
| full dev follow-up | 27 | 1350 | 2694426 |
| total | 69 | 2022 | 4438516 |

## Candidate Rules

All structural/history candidates wrap `SlimeVolleyNetPressurePolicy` and use
only current observation plus a short observation stack. They do not call the
packaged RNN or clone simulator state at runtime.

| Candidate | Intended rule |
| --- | --- |
| `stacked_near_net_tight_vertical` | Tight near-net vertical jump only when stacked frames confirm slow rightward descent. |
| `stacked_near_net_mode_vertical` | Verticalize near-net returns only when the inherited mode is `intercept`. |
| `stacked_near_net_base_jump_vertical` | Replace inherited forward-jump/back-jump with vertical near-net contact. |
| `stacked_near_net_forward_jump` | Keep forward pressure direction on slow near-net descending returns. |
| `stacked_near_net_back_jump` | Yield space with backward+jump on slow near-net descending returns. |

## Short Screen

The short screen selected `stacked_near_net_mode_vertical` for full development
follow-up because it preserved built-in and improved-v2, while nudging
improved-v3, improved-v4, improved-v5, and improved-v6.

| Candidate | Opponent | Mean | W/L/D | Overrides |
| --- | --- | ---: | --- | ---: |
| `net_pressure_reference` | `builtin` | `0.0625` | `3/4/9` | `0` |
| `net_pressure_reference` | `improved-v2` | `4.8125` | `16/0/0` | `0` |
| `net_pressure_reference` | `improved-v3` | `2.8750` | `14/1/1` | `0` |
| `net_pressure_reference` | `improved-v4` | `2.4375` | `12/1/3` | `0` |
| `net_pressure_reference` | `improved-v5` | `1.5625` | `12/3/1` | `0` |
| `net_pressure_reference` | `improved-v6` | `1.5625` | `12/3/1` | `0` |
| `baseline_rnn` | `builtin` | `0.2500` | `7/3/6` | `0` |
| `baseline_rnn` | `improved-v2` | `4.7500` | `16/0/0` | `0` |
| `baseline_rnn` | `improved-v3` | `4.1875` | `16/0/0` | `0` |
| `baseline_rnn` | `improved-v4` | `3.7500` | `16/0/0` | `0` |
| `baseline_rnn` | `improved-v5` | `2.5625` | `14/0/2` | `0` |
| `baseline_rnn` | `improved-v6` | `2.5625` | `14/0/2` | `0` |
| `stacked_near_net_mode_vertical` | `builtin` | `0.0625` | `3/4/9` | `0` |
| `stacked_near_net_mode_vertical` | `improved-v2` | `4.8125` | `16/0/0` | `1` |
| `stacked_near_net_mode_vertical` | `improved-v3` | `2.9375` | `15/1/0` | `2` |
| `stacked_near_net_mode_vertical` | `improved-v4` | `2.5625` | `12/1/3` | `3` |
| `stacked_near_net_mode_vertical` | `improved-v5` | `1.7500` | `13/1/2` | `6` |
| `stacked_near_net_mode_vertical` | `improved-v6` | `1.7500` | `13/1/2` | `6` |

Other screened variants were rejected without full follow-up: `forward_jump`
regressed improved-v3 on the short screen, `base_jump_vertical` was effectively
inert, and the tight/back-jump variants made only small local changes.

## Full Development Follow-Up

`stacked_near_net_mode_vertical` did not clear the fixed full development pool.
It preserved built-in, random, initial, and improved-v0, nudged improved-v4 by
`+0.12`, improved-v5 by `+0.06`, and improved-v6 by `+0.04`, but regressed
improved-v2 by `-0.02`, tied improved-v3 mean, and stayed far below
`baseline_rnn` on every hard archived opponent.

| Opponent | Candidate | Mean | W/L/D | Overrides |
| --- | --- | ---: | --- | ---: |
| `builtin` | `net_pressure_reference` | `-0.0600` | `11/14/25` | `0` |
| `builtin` | `baseline_rnn` | `-0.1800` | `18/19/13` | `0` |
| `builtin` | `stacked_near_net_mode_vertical` | `-0.0600` | `11/14/25` | `0` |
| `improved-v2` | `net_pressure_reference` | `4.6800` | `50/0/0` | `0` |
| `improved-v2` | `baseline_rnn` | `4.8000` | `50/0/0` | `0` |
| `improved-v2` | `stacked_near_net_mode_vertical` | `4.6600` | `50/0/0` | `4` |
| `improved-v3` | `net_pressure_reference` | `3.0800` | `48/1/1` | `0` |
| `improved-v3` | `baseline_rnn` | `4.2400` | `49/0/1` | `0` |
| `improved-v3` | `stacked_near_net_mode_vertical` | `3.0800` | `49/1/0` | `9` |
| `improved-v4` | `net_pressure_reference` | `2.5600` | `45/2/3` | `0` |
| `improved-v4` | `baseline_rnn` | `3.7000` | `48/0/2` | `0` |
| `improved-v4` | `stacked_near_net_mode_vertical` | `2.6800` | `46/1/3` | `10` |
| `improved-v5` | `net_pressure_reference` | `1.2000` | `34/7/9` | `0` |
| `improved-v5` | `baseline_rnn` | `2.3800` | `43/1/6` | `0` |
| `improved-v5` | `stacked_near_net_mode_vertical` | `1.2600` | `35/5/10` | `19` |
| `improved-v6` | `net_pressure_reference` | `1.2200` | `34/7/9` | `0` |
| `improved-v6` | `baseline_rnn` | `2.4000` | `43/1/6` | `0` |
| `improved-v6` | `stacked_near_net_mode_vertical` | `1.2600` | `35/5/10` | `16` |

## Failure Analysis

The stacked detector made the rollout-mined rule less harmful, but it did not
solve the core robustness problem. The useful overrides were sparse and
concentrated on hard-tail archived opponents. They reduced some losses on
improved-v4/v5/v6 but did not move the policy toward the RNN comparator's
broader advantage. The improved-v2 regression is small in mean score but still
violates the preservation requirement for a maintained policy edit.

The result weakens the hypothesis that the rollout-search signal can be copied
into a narrow local observation rule. It may still be useful as a diagnostic:
near-net verticalization has some real hard-tail value, but promotion likely
requires a higher-level rally phase or contact-quality detector rather than one
more terminal-frame action override.

## Decision

Do not promote `stacked_near_net_mode_vertical`. Do not open generation-5
holdout or audit seeds. Keep this as development-only negative/mixed evidence.

Next hypothesis: separate draw-reduction and hard-opponent robustness goals, or
derive a multi-frame rally-phase detector that changes setup before the
near-net terminal frame instead of overriding only the final contact action.

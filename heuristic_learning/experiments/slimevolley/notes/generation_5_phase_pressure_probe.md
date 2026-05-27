# Generation-5 Phase-Pressure Probe

Date: 2026-05-27

## Scope

This note records development-only probes for a higher-level rally phase rule
after earlier generation-5 diagnostics showed that local low-contact and
front-net action overrides were too coarse. The tested idea was to add
opponent-side low pressure only when the ball had already spent time across the
net and the opponent posture suggested a safe conversion opportunity.

No maintained policy/config/test edit was promoted. No canonical ledger row was
appended. No generation-5 holdout seeds `13000..13049` and no audit seeds
`14000..14049` were used.

Artifacts:

- Probe script: `experiments/slimevolley/probes/g5_phase_pressure_probe.py`
- JSON result: `experiments/slimevolley/results/generation_5_phase_pressure_probe.json`

Seed use:

- Short screen: `12000..12015`
- Full fixed-pool checks: `12000..12049`

## Candidate Families

All candidates were transient structural/history wrappers around
`net-pressure`. They forced `101` only for low balls on the opponent side under
additional phase/posture gates:

- `phase_posture_back`: pressure when the opponent is low and deeper.
- `phase_two_frame`: pressure after two consecutive opponent-side frames.
- `phase_grounded`: pressure only while the agent is grounded.
- `phase_two_frame_back`, `phase_two_frame_midback`, and
  `phase_two_frame_strict`: narrower combinations of the above gates.

The first full checks were run before the override-frame counter was fixed to
accumulate across episodes, so their score/W-L-D values are valid but their
override counts should be treated as diagnostic-only. The later narrowed short
screen used the corrected cumulative counter.

## Short Screen

Seeds: `12000..12015`.

| Candidate | Built-in | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `net-pressure` reference | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | reference |
| `baseline-rnn` | `0.2500` | `4.1875` | `3.7500` | `2.5625` | `2.5625` | comparator |
| `phase_posture_back` | `0.0625` | `2.7500` | `2.5000` | `1.8125` | `1.8125` | full check |
| `phase_two_frame` | `0.0625` | `2.6250` | `2.6875` | `1.7500` | `1.7500` | full check |
| `phase_grounded` | `0.0625` | `2.7500` | `2.5000` | `1.7500` | `1.7500` | full check |
| `phase_two_frame_back` | `0.0625` | `2.7500` | `2.5000` | `1.8125` | `1.8125` | no better than checked candidates |
| `phase_two_frame_midback` | `0.0625` | `2.7500` | `2.5625` | `1.6875` | `1.6875` | reject |
| `phase_two_frame_strict` | `0.0625` | `2.6875` | `2.5000` | `1.5625` | `1.5625` | reject |

## Full Development Checks

Seeds: `12000..12049`. The table shows mean score deltas versus the
`net-pressure` reference on the same fixed development pool.

| Opponent | `phase_posture_back` | `phase_two_frame` | `phase_grounded` |
| --- | ---: | ---: | ---: |
| `builtin` | `-0.02` | `+0.04` | `-0.02` |
| `random` | `0.00` | `0.00` | `0.00` |
| `initial` | `0.00` | `0.00` | `0.00` |
| `improved-v0` | `0.00` | `0.00` | `0.00` |
| `improved-v2` | `0.00` | `-0.10` | `-0.06` |
| `improved-v3` | `0.00` | `-0.06` | `-0.04` |
| `improved-v4` | `+0.06` | `+0.08` | `+0.04` |
| `improved-v5` | `+0.08` | `+0.10` | `+0.08` |
| `improved-v6` | `+0.08` | `+0.12` | `+0.08` |

Full checked absolute rows:

| Candidate | Built-in | improved-v2 | improved-v3 | improved-v4 | improved-v5 | improved-v6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `net-pressure` | `-0.06`, `11/14/25` | `4.68`, `50/0/0` | `3.08`, `48/1/1` | `2.56`, `45/2/3` | `1.20`, `34/7/9` | `1.22`, `34/7/9` |
| `baseline-rnn` | `-0.18`, `18/19/13` | `4.80`, `50/0/0` | `4.24`, `49/0/1` | `3.70`, `48/0/2` | `2.38`, `43/1/6` | `2.40`, `43/1/6` |
| `phase_posture_back` | `-0.08`, `11/15/24` | `4.68`, `50/0/0` | `3.08`, `47/1/2` | `2.62`, `45/2/3` | `1.28`, `34/6/10` | `1.30`, `34/6/10` |
| `phase_two_frame` | `-0.02`, `11/14/25` | `4.58`, `50/0/0` | `3.02`, `47/1/2` | `2.64`, `45/3/2` | `1.30`, `34/4/12` | `1.34`, `34/4/12` |
| `phase_grounded` | `-0.08`, `11/15/24` | `4.62`, `50/0/0` | `3.04`, `48/1/1` | `2.60`, `46/2/2` | `1.28`, `34/5/11` | `1.30`, `34/5/11` |

## Selective Follow-Up

A later development-only selective pass used the corrected cumulative override
counter and wrote `results/generation_5_phase_pressure_selective_probe.json`. No
holdout or audit seeds were used. The pass screened narrower descending/depth
variants on `12000..12015`, then expanded only `phase_two_frame_descending` to
the full `12000..12049` development pool.

Short-screen means:

| Candidate | Built-in | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `net-pressure` reference | `0.0625` | `2.8750` | `2.4375` | `1.5625` | `1.5625` | reference |
| `baseline-rnn` | `0.2500` | `4.1875` | `3.7500` | `2.5625` | `2.5625` | comparator |
| `phase_two_frame_descending` | `0.0625` | `2.8750` | `2.6250` | `1.7500` | `1.7500` | full check |
| `phase_two_frame_back_grounded` | `0.0625` | `2.8125` | `2.4375` | `1.7500` | `1.7500` | reject |
| `phase_two_frame_back_low` | `0.0625` | `2.8125` | `2.4375` | `1.5625` | `1.5625` | reject |
| `phase_two_frame_mid_desc` | `0.0625` | `2.8125` | `2.5000` | `1.7500` | `1.7500` | reject |
| `phase_two_frame_back_desc` | `0.0625` | `2.7500` | `2.5000` | `1.8125` | `1.8125` | short-screen only |
| `phase_two_frame_back_low_desc` | `0.0625` | `2.8125` | `2.4375` | `1.5625` | `1.5625` | short-screen only |

Full-pool deltas for `phase_two_frame_descending` versus `net-pressure`:

| Opponent | Delta | Absolute mean | W/L/D | Overrides |
| --- | ---: | ---: | --- | ---: |
| `builtin` | `+0.04` | `-0.02` | `11/14/25` | `6091` |
| `random` | `0.00` | `4.90` | `50/0/0` | `2540` |
| `initial` | `0.00` | `4.86` | `50/0/0` | `11963` |
| `improved-v0` | `0.00` | `4.84` | `50/0/0` | `12472` |
| `improved-v2` | `-0.10` | `4.58` | `50/0/0` | `13387` |
| `improved-v3` | `+0.02` | `3.10` | `47/1/2` | `20505` |
| `improved-v4` | `+0.06` | `2.62` | `45/3/2` | `20465` |
| `improved-v5` | `+0.08` | `1.28` | `34/5/11` | `23775` |
| `improved-v6` | `+0.10` | `1.32` | `34/5/11` | `23735` |

This selective pass is still a no-promotion result. The best variant preserves
the built-in row better than `phase_posture_back`, but it regresses
`improved-v2`, remains far below `baseline-rnn` on every hard archived row, and
uses many override frames.

## Failure Analysis

The phase gates confirm that opponent-side low pressure is a real lever, but
not yet a solution. `phase_two_frame` is the best numerical variant in this
pass: it improves built-in, `improved-v4`, `improved-v5`, and `improved-v6`.
However, it regresses `improved-v2` and `improved-v3`, and it still remains far
below `baseline-rnn` on the hard archived rows.

`phase_posture_back` and `phase_grounded` are cleaner on `improved-v2/v3`, but
they regress built-in and provide smaller hard-tail gains. The narrowed
two-frame/depth screens did not produce a better candidate than the already
full-checked variants.

This weakens the idea that a single opponent-side pressure gate will close the
gap. The remaining RNN advantage likely involves earlier rally setup and return
placement across several frames, not just deciding when to add one final `101`
action.

## Decision

Do not promote a maintained policy/config/test edit from this pass. Do not open
generation-5 holdout or audit seeds.

Keep the result as mixed development evidence: `phase_two_frame` is a useful
diagnostic direction, but it is not robust enough to claim heuristic learning
has beaten the neural comparator.

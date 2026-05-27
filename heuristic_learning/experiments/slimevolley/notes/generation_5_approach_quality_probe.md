# Generation-5 Approach-Quality Probe

Date: 2026-05-27

## Scope

This note records a development-only pre-contact approach diagnostic and
structural probe. The prior contact-timing screen showed that final-frame jump
overrides tied the reference because `net-pressure` was already jumping in most
low front-court terminal windows. This pass moved several frames earlier and
asked whether the gap to `baseline-rnn` is caused by approach quality before
contact.

No maintained policy/config/test edit was promoted. No canonical ledger row was
appended. No generation-5 holdout seeds `13000..13049` and no generation-5
audit seeds `14000..14049` were used.

Artifacts:

- Probe script: `experiments/slimevolley/probes/g5_approach_quality_probe.py`
- JSON result: `experiments/slimevolley/results/generation_5_approach_quality_probe.json`

Seed use:

- Diagnostics: `12000..12015`
- Short screen: `12000..12015`
- Full fixed-pool check: not run, because no candidate improved the fixed
  short-screen opponent set.

## Trace Diagnostic

The diagnostic found the last low front-court contact frame before a point
event, then summarized approach frames before that point. Offset `8` was the
clearest signal.

| Policy | Opponent | Events | Offset-8 dx/ball_y/ball_vy | Offset-8 jump/forward |
| --- | --- | --- | ---: | ---: |
| `net_pressure_reference` | `improved-v3` | `{'point_lost': 6}` | `0.590/0.472/-0.805` | `0.167/0.833` |
| `net_pressure_reference` | `improved-v4` | `{'point_lost': 6}` | `0.610/0.519/-0.887` | `0.000/0.500` |
| `net_pressure_reference` | `improved-v5` | `{'point_lost': 4, 'point_won': 2}` | `0.459/0.563/-0.955` | `0.000/0.500` |
| `net_pressure_reference` | `improved-v6` | `{'point_lost': 4, 'point_won': 2}` | `0.459/0.563/-0.955` | `0.000/0.500` |
| `baseline_rnn` | `improved-v3` | `{'point_lost': 4}` | `0.267/0.592/-1.221` | `1.000/0.750` |
| `baseline_rnn` | `improved-v4` | `{'point_lost': 4}` | `0.267/0.592/-1.221` | `1.000/0.750` |
| `baseline_rnn` | `improved-v5` | `{'point_lost': 2}` | `0.311/0.644/-1.537` | `1.000/0.500` |
| `baseline_rnn` | `improved-v6` | `{'point_lost': 2}` | `0.311/0.644/-1.537` | `1.000/0.500` |

Diagnostic interpretation: on this short subset, `net-pressure` is farther
behind the ball eight frames before low-contact terminal events, while
`baseline-rnn` is closer and already jumping. That made earlier approach jump
timing look plausible enough to screen, even though prior final-frame jump
overrides had failed.

## Short Screen

The structural candidates were transient wrappers around `net-pressure`:

- `approach_drive_jump`: earlier forward+jump while behind a descending
  front-low ball.
- `approach_vertical_jump`: earlier vertical jump when moderately aligned.
- `approach_drive_nojump`: close the approach gap with forward/no-jump.
- `approach_preserve_nojump`: suppress premature jump while preserving base
  movement.
- `approach_vertical_set`: stop horizontal drift before contact.
- `approach_rear_brake`: move rearward/no-jump when close to low front-court
  contact.

Seeds: `12000..12015`.

| Candidate | Built-in | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Overrides |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `net_pressure_reference` | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `0` |
| `baseline_rnn` | `0.2500`, `7/3/6` | `4.1875`, `16/0/0` | `3.7500`, `16/0/0` | `2.5625`, `14/0/2` | `2.5625`, `14/0/2` | `0` |
| `approach_drive_jump` | `-1.8750`, `1/14/1` | `1.6875`, `11/2/3` | `1.1250`, `11/4/1` | `-1.0625`, `4/11/1` | `-1.0625`, `4/11/1` | `66` |
| `approach_vertical_jump` | `-0.5625`, `4/8/4` | `2.3125`, `12/2/2` | `1.3750`, `10/2/4` | `-0.8750`, `4/8/4` | `-0.8750`, `4/8/4` | `134` |
| `approach_drive_nojump` | `-0.1875`, `4/6/6` | `2.8750`, `14/0/2` | `2.5625`, `13/0/3` | `0.8125`, `10/5/1` | `0.8750`, `10/4/2` | `101` |
| `approach_preserve_nojump` | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `178` |
| `approach_vertical_set` | `-0.1875`, `4/7/5` | `2.8750`, `14/0/2` | `2.4375`, `13/0/3` | `1.3750`, `11/2/3` | `1.3750`, `11/2/3` | `73` |
| `approach_rear_brake` | `-0.0625`, `4/5/7` | `2.3125`, `14/2/0` | `1.8125`, `13/3/0` | `0.9375`, `8/3/5` | `0.9375`, `8/3/5` | `50` |

## Far-Behind Follow-Up

The initial screen showed one mixed signal: `approach_drive_nojump` preserved
`improved-v3` and improved `improved-v4`, but regressed built-in and
`improved-v5/v6`. A narrower follow-up gated only far-behind approach states
(`dx >= 0.54`) to test whether it could keep the hard `v5/v6` gains while
avoiding broad damage. It used the same fixed short screen, `12000..12015`, and
was appended to `generation_5_approach_quality_probe.json`.

| Candidate | Built-in | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Overrides |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `net_pressure_reference` | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `0` |
| `baseline_rnn` | `0.2500`, `7/3/6` | `4.1875`, `16/0/0` | `3.7500`, `16/0/0` | `2.5625`, `14/0/2` | `2.5625`, `14/0/2` | `0` |
| `approach_far_drive_nojump` | `-0.1250`, `2/4/10` | `2.7500`, `13/1/2` | `2.3750`, `12/1/3` | `1.6250`, `13/2/1` | `1.6250`, `13/2/1` | `9` |
| `approach_far_preserve_nojump` | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | `33` |
| `approach_far_vertical_set` | `-0.0625`, `2/3/11` | `2.2500`, `13/1/2` | `2.1875`, `12/1/3` | `1.3750`, `11/3/2` | `1.5625`, `11/3/2` | `19` |

The far-behind gate was not promotable. `approach_far_drive_nojump` slightly
improved `improved-v5/v6`, but regressed built-in, `improved-v3`, and
`improved-v4`. `approach_far_preserve_nojump` tied the reference despite many
overrides. `approach_far_vertical_set` regressed nearly every row.

## Failure Analysis

The diagnostic signal was real but not directly actionable. Earlier jump
policies were harmful: `approach_drive_jump` collapsed built-in and hard
archived rows, and `approach_vertical_jump` also regressed every target row.
This suggests that the RNN's early jumping works because of a continuous
controller state, not because a static early-jump predicate can be copied.

The no-jump approach variants were safer but still not promotable.
`approach_drive_nojump` preserved `improved-v3` and improved the short
`improved-v4` row, but it regressed built-in and badly regressed
`improved-v5/v6`. `approach_preserve_nojump` tied the reference despite many
overrides. `approach_vertical_set` reduced hard `v5/v6` less severely than
drive/no-jump but still regressed built-in and did not beat the reference.

This weakens the idea that a single pre-contact movement override can reproduce
the neural comparator. The remaining gap likely requires a phase controller
that coordinates approach, jump start, and post-jump contact over a longer
window, or a deliberately simpler metric such as reducing draws against the
built-in opponent without claiming hard-opponent robustness.

## Decision

Do not promote any approach-quality candidate. Do not run full fixed-pool or
holdout checks for this family.

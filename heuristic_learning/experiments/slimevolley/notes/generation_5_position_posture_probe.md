# Generation-5 Position/Posture Probe

Date: 2026-05-27

## Scope

This note records a development-only scalar/config probe around the current
`net-pressure` structural candidate. Earlier probes changed terminal low-contact
actions, reset macros, post-contact setup, and short-history pressure gates.
This pass tested a more global possibility: the packaged `baseline-rnn` may win
more archived-opponent points because it defaults to a more forward court
posture before the low-contact window arrives.

Only generation-5 development seeds were used. The screen used exactly
`12000..12015`. No generation-5 holdout seeds `13000..13049` and no audit seeds
`14000..14049` were used. No maintained policy/config/test edit was promoted.

Artifacts:

- Probe script: `experiments/slimevolley/probes/g5_position_posture_probe.py`
- JSON result: `experiments/slimevolley/results/generation_5_position_posture_probe.json`

## Candidate Definitions

All candidates wrap `SlimeVolleyNetPressurePolicy` and change only scalar
posture/home constants.

| Candidate | Type | Definition |
| --- | --- | --- |
| `front_home_110` | scalar/config | `home_x=1.05`, `defensive_home_x=1.10`, `attack_home_x=0.72`. |
| `front_home_095` | scalar/config | `home_x=0.92`, `defensive_home_x=1.00`, `attack_home_x=0.66`. |
| `front_home_080` | scalar/config | `home_x=0.80`, `defensive_home_x=0.90`, `attack_home_x=0.58`. |
| `front_home_095_low_guard` | scalar/config | `front_home_095` plus `low_ball_rescue_x_window=0.60`. |
| `front_home_095_fast_land` | scalar/config | `front_home_095` plus `landing_horizon=0.30`. |

## Short Screen Results

Rows use seeds `12000..12015`.

| Candidate | Built-in | improved-v3 | improved-v4 | improved-v5 | improved-v6 | Recommendation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `net_pressure_reference` | `0.0625`, `3/4/9` | `2.8750`, `14/1/1` | `2.4375`, `12/1/3` | `1.5625`, `12/3/1` | `1.5625`, `12/3/1` | reference |
| `baseline_rnn` | `0.2500`, `7/3/6` | `4.1875`, `16/0/0` | `3.7500`, `16/0/0` | `2.5625`, `14/0/2` | `2.5625`, `14/0/2` | comparator |
| `front_home_110` | `0.0625`, `3/4/9` | `3.0000`, `15/0/1` | `2.4375`, `14/0/2` | `1.3750`, `12/3/1` | `1.3750`, `12/3/1` | reject; hard-tail regression |
| `front_home_095` | `0.0625`, `3/4/9` | `3.0000`, `15/0/1` | `2.5625`, `14/0/2` | `1.1250`, `11/4/1` | `1.1250`, `11/4/1` | reject; large hard-tail regression |
| `front_home_080` | `-0.1875`, `2/4/10` | `2.6250`, `14/0/2` | `2.3750`, `13/0/3` | `1.7500`, `14/2/0` | `1.7500`, `14/2/0` | reject; built-in and v3/v4 regression |
| `front_home_095_low_guard` | `-0.1250`, `2/3/11` | `2.5625`, `14/0/2` | `2.4375`, `15/0/1` | `1.3125`, `11/3/2` | `1.3125`, `11/3/2` | reject |
| `front_home_095_fast_land` | `-0.5000`, `1/8/7` | `2.5625`, `13/0/3` | `2.0000`, `12/1/3` | `1.0000`, `8/3/5` | `1.0000`, `8/3/5` | reject |

## Failure Analysis

Front-court posture is a real lever, but only as a tradeoff. The modest
front-shifted candidates improved `improved-v3` and sometimes `improved-v4`,
but they regressed `improved-v5/v6`. The aggressive `front_home_080` candidate
improved `improved-v5/v6` by `+0.1875` on the short screen, but it regressed
built-in by `-0.2500` and also regressed `improved-v3/v4`.

This weakens the idea that the hard archived gap can be closed by scalar
front-posture tuning alone. The useful signal is directional: earlier posture
changes can move hard-tail results, but the correct controller likely needs
context-dependent phase switching rather than one fixed home position.

## Decision

Do not run a full development pool, holdout, or audit evaluation from this
screen. Do not promote a maintained policy/config/test edit.

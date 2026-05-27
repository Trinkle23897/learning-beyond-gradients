# Generation-4 Parallel5 Attack Scalar/Config Tuning

Date: 2026-05-27

Worker: A

Label: scalar/config tuning

## Protocol

This was a development-only scalar/config search around the registered
`attack` policy only. The policy source, report generator, README, final
report, ledgers, and existing result files were not edited. Runs used no-ledger
direct harness calls from `heuristic_learning` with `PYTHONPATH=.`.

Scratch scripts used:

- `/tmp/g4_parallel5_attack_scalar_search.py`
- `/tmp/g4_parallel5_attack_rally_like_followup.py`

No scratch data files were written under `results/parallel`.

No holdout seeds, audit seeds, generation-5 holdout, or generation-5 audit were
used. The only seeds used were generation-4 development seeds.

Short-screen seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full-development seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

The evaluation harness accepts `--config-json`, but a partial config would be
rebuilt from `SlimeVolleyConfig()` defaults rather than from
`IMPROVED_TUNED_CONFIG`. To keep this search around the registered `attack`
policy, each candidate passed a full config cloned from `IMPROVED_TUNED_CONFIG`
plus the listed delta. The policy name remained `attack` for every candidate;
no `rally-serve` detector or macro was enabled.

Base registered-attack config deltas from `SlimeVolleyConfig()`:

`x_margin=0.04`, `contact_x_window=0.14`, `high_arc_horizon=0.85`,
`overcommit_guard_x=0.18`, `low_ball_rescue_x_window=0.72`,
`low_ball_rescue_horizon=0.06`,
`grounded_low_receive_airborne_margin=0.12`.

Existing full-dev comparators supplied to this worker:

| Comparator | Opponent | Seeds | Mean | W-L-D |
| --- | --- | --- | ---: | --- |
| `baseline-rnn` | `builtin` | `9000..9049` | `0.12` | `18-12-20` |
| `attack` | `builtin` | `9000..9049` | `-0.30` | `7-18-25` |
| `rally-serve` | `builtin` | `9000..9049` | `0.14` | `13-8-29` |

## Candidate Definitions

All deltas are relative to the base registered-attack config above.

| Candidate | Kind | Delta |
| --- | --- | --- |
| `attack_reference` | reference | none |
| `home_0.76` | scalar | `attack_home_x=0.76` |
| `home_0.88` | scalar | `attack_home_x=0.88` |
| `late_y_min_0.24` | scalar | `late_attack_y_min=0.24` |
| `late_y_max_0.75` | scalar | `late_attack_y_max=0.75` |
| `late_vx_-0.45` | scalar | `late_attack_vx=-0.45` |
| `late_vx_-0.25` | scalar | `late_attack_vx=-0.25` |
| `late_vy_-0.30` | scalar | `late_attack_vy=-0.30` |
| `late_vy_0.00` | scalar | `late_attack_vy=0.00` |
| `late_dx_min_0.00` | scalar | `late_attack_dx_min=0.00` |
| `late_dx_max_0.34` | scalar | `late_attack_dx_max=0.34` |
| `late_dx_max_0.42` | scalar | `late_attack_dx_max=0.42` |
| `contact_0.16` | scalar | `contact_x_window=0.16` |
| `contact_0.12` | scalar | `contact_x_window=0.12` |
| `low_rescue_x_0.64` | scalar | `low_ball_rescue_x_window=0.64` |
| `low_rescue_x_0.80` | scalar | `low_ball_rescue_x_window=0.80` |
| `rally_attack_like` | config | `high_arc_horizon=0.95`, `low_ball_rescue_x_window=0.54`, `grounded_low_receive_airborne_margin=0.16`, `late_attack_y_min=0.24`, `late_attack_vx=-0.45`, `late_attack_vy=-0.35` |
| `late_window_wide` | config | `late_attack_y_min=0.24`, `late_attack_y_max=0.75`, `late_attack_dx_min=0.00`, `late_attack_dx_max=0.34` |
| `late_fast_down` | config | `late_attack_vx=-0.45`, `late_attack_vy=-0.30`, `late_attack_dx_max=0.34` |

## Short Screen

Seeds: `9000..9015`. Opponents: `builtin`, `improved-v4`, `improved-v6`.

| Candidate | Kind | `builtin` mean / W-L-D / steps | `improved-v4` mean / W-L-D / steps | `improved-v6` mean / W-L-D / steps |
| --- | --- | ---: | ---: | ---: |
| `attack_reference` | reference | `-0.1250 / 2-4-10 / 48000` | `2.1250 / 13-0-3 / 46910` | `1.0000 / 8-3-5 / 47768` |
| `home_0.76` | scalar | `-0.1250 / 2-4-10 / 48000` | `2.1250 / 13-0-3 / 46910` | `1.0000 / 8-3-5 / 47768` |
| `home_0.88` | scalar | `-0.1250 / 2-4-10 / 48000` | `2.1250 / 13-0-3 / 46910` | `1.0000 / 8-3-5 / 47768` |
| `late_y_min_0.24` | scalar | `-0.1250 / 2-4-10 / 48000` | `2.1250 / 13-0-3 / 46910` | `1.0000 / 8-3-5 / 47768` |
| `late_y_max_0.75` | scalar | `-0.4375 / 2-8-6 / 48000` | `2.1875 / 14-0-2 / 46665` | `1.0000 / 9-4-3 / 47768` |
| `late_vx_-0.45` | scalar | `-0.1250 / 2-4-10 / 48000` | `1.9375 / 12-0-4 / 46910` | `1.2500 / 10-3-3 / 47768` |
| `late_vx_-0.25` | scalar | `-0.1250 / 2-4-10 / 48000` | `2.1250 / 13-0-3 / 46910` | `0.8750 / 8-4-4 / 47768` |
| `late_vy_-0.30` | scalar | `-0.2500 / 1-5-10 / 48000` | `2.0625 / 13-0-3 / 46811` | `1.1875 / 9-3-4 / 47768` |
| `late_vy_0.00` | scalar | `-0.1250 / 2-4-10 / 48000` | `2.1875 / 14-0-2 / 46910` | `1.0625 / 8-2-6 / 47768` |
| `late_dx_min_0.00` | scalar | `-0.1875 / 1-4-11 / 48000` | `1.9375 / 12-1-3 / 46240` | `1.3750 / 8-2-6 / 46602` |
| `late_dx_max_0.34` | scalar | `-0.1250 / 2-4-10 / 48000` | `2.1250 / 13-0-3 / 46910` | `1.0000 / 8-3-5 / 47768` |
| `late_dx_max_0.42` | scalar | `-0.1250 / 2-4-10 / 48000` | `2.1250 / 13-0-3 / 46910` | `1.0000 / 8-3-5 / 47768` |
| `contact_0.16` | scalar | `-0.7500 / 0-8-8 / 48000` | `2.4375 / 16-0-0 / 47203` | `1.5625 / 10-2-4 / 48000` |
| `contact_0.12` | scalar | `-0.5000 / 2-7-7 / 48000` | `1.7500 / 13-1-2 / 48000` | `1.3125 / 12-2-2 / 47121` |
| `low_rescue_x_0.64` | scalar | `-0.2500 / 2-4-10 / 48000` | `2.1250 / 13-0-3 / 46910` | `0.7500 / 7-3-6 / 48000` |
| `low_rescue_x_0.80` | scalar | `-0.1250 / 2-4-10 / 48000` | `2.1250 / 13-0-3 / 46910` | `1.0000 / 8-3-5 / 47768` |
| `rally_attack_like` | config | `0.3125 / 4-1-11 / 48000` | `2.3750 / 15-0-1 / 46835` | `0.8750 / 8-3-5 / 48000` |
| `late_window_wide` | config | `-0.2500 / 1-6-9 / 48000` | `1.9375 / 12-0-4 / 45886` | `1.2500 / 8-3-5 / 46602` |
| `late_fast_down` | config | `-0.2500 / 1-5-10 / 48000` | `2.0625 / 13-0-3 / 46811` | `1.3125 / 10-3-3 / 47768` |

## Full Built-In Checks

Seeds: `9000..9049`. Opponent: `builtin`.

| Candidate | Kind | Mean | W-L-D | Steps |
| --- | --- | ---: | --- | ---: |
| `attack_reference` | reference | `-0.3000` | `7-18-25` | `150000` |
| `late_vx_-0.25` | scalar | `-0.3400` | `7-19-24` | `150000` |
| `late_vy_0.00` | scalar | `-0.3400` | `7-19-24` | `150000` |
| `late_dx_max_0.42` | scalar | `-0.3000` | `7-18-25` | `150000` |
| `contact_0.16` | scalar | `-0.4400` | `3-20-27` | `150000` |
| `rally_attack_like` | config | `-0.0600` | `10-13-27` | `150000` |

No scalar-only candidate beat the `baseline-rnn` full-development built-in
mean of `0.12`. The best full-development built-in result was the config
candidate `rally_attack_like`, which improved over `attack_reference` by `0.24`
score points but remained below both `baseline-rnn` (`0.12`) and `rally-serve`
(`0.14`).

## Fixed-Pool Follow-Up: `rally_attack_like`

This was the short-screen built-in leader and the best full built-in result, so
it was checked on the fixed development opponent pool even though it did not
beat `baseline-rnn` on full-development built-in seeds.

Seeds: `9000..9049`.

| Opponent | Mean | W-L-D | Steps |
| --- | ---: | --- | ---: |
| `builtin` | `-0.0600` | `10-13-27` | `150000` |
| `random` | `4.7600` | `50-0-0` | `37576` |
| `initial` | `4.7200` | `50-0-0` | `44924` |
| `improved-v0` | `4.7400` | `50-0-0` | `43623` |
| `improved-v2` | `4.4400` | `50-0-0` | `71584` |
| `improved-v3` | `2.7800` | `47-1-2` | `139360` |
| `improved-v4` | `2.2000` | `43-2-5` | `143731` |
| `improved-v5` | `1.1600` | `31-7-12` | `148027` |
| `improved-v6` | `1.2200` | `31-7-12` | `148027` |

## Fixed-Pool Follow-Up: `contact_0.16`

This scalar row was the strongest short-screen archived-opponent result but a
clear built-in regression. It was still evaluated on the fixed pool as a
diagnostic for the trade-off.

Seeds: `9000..9049`.

| Opponent | Mean | W-L-D | Steps |
| --- | ---: | --- | ---: |
| `builtin` | `-0.4400` | `3-20-27` | `150000` |
| `random` | `4.7000` | `50-0-0` | `38469` |
| `initial` | `4.6200` | `50-0-0` | `43784` |
| `improved-v0` | `4.6200` | `50-0-0` | `43155` |
| `improved-v2` | `4.3000` | `49-1-0` | `73185` |
| `improved-v3` | `2.9400` | `49-1-0` | `138755` |
| `improved-v4` | `2.5200` | `49-0-1` | `144988` |
| `improved-v5` | `1.3200` | `32-8-10` | `147688` |
| `improved-v6` | `1.3600` | `32-8-10` | `147688` |

## Failure Analysis

Most attack-rule scalar changes were inert on the built-in short screen.
`attack_home_x`, `late_attack_y_min`, `late_attack_dx_max`, and the wider
low-rescue window often reproduced the attack reference exactly on
`9000..9015`.

The candidates that helped archived heuristic opponents generally hurt the
built-in opponent. `contact_0.16` is the clearest example: it improved the
full-development archived rows through `improved-v6`, but dropped the built-in
full-development score to `-0.44` with only `3` wins. This is not a robust
promotion candidate because it worsens the neural comparator target that the
generation-4 candidate still needs to close.

`rally_attack_like` was the only row with a meaningful built-in improvement. It
raised full-development built-in mean from `-0.30` to `-0.06` and improved or
roughly held most fixed-pool archived rows. However, it is still below
`baseline-rnn` on the built-in full-development seeds and also below the
existing `rally-serve` built-in mean. Compared with the archived rally-serve
means supplied to this worker, it is also below `rally-serve` on `improved-v3`
(`2.78` vs `2.98`) and `improved-v4` (`2.20` vs `2.34`), tied on
`improved-v5` (`1.16`), and tied on `improved-v6` (`1.22`).

The full-config harness avoided a possible false result from partial
`--config-json` use. A partial JSON would have silently dropped the registered
`attack` tuned base fields and evaluated a different policy family.

## Promotion Recommendation

Do not promote any candidate from this scalar/config tuning run.

Best result: `rally_attack_like` as an `attack` config diagnostic, with
full-development built-in mean `-0.06`, W-L-D `10-13-27`, `150000` steps. This
is a development-only partial improvement over `attack_reference`, but it does
not beat `baseline-rnn` and does not beat the already archived `rally-serve`
candidate. It should remain a diagnostic note only.

# Generation-4 Parallel3 Rear-Wall Press Probe

Date: 2026-05-27

Worker: 3

## Protocol

This was a development-only structural branch probe for `rear_wall_press` and
rear-wall low-ball losses. No maintained policy code, tests, canonical ledger,
summary, holdout artifact, or audit artifact was edited or written. Transient
subclasses were defined in `/tmp/g4_parallel3_rear_wall_press.py`, and transient
JSON output was written to `/tmp/g4_parallel3_rear_wall_press.json`.

Short screen seeds used exactly:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full development seeds and fixed-pool seeds used exactly:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

No holdout seeds, audit seeds, or `slimevolley-final-eval` were used.

## Candidate Definitions

References:

| Name | Role |
| --- | --- |
| `rally_serve_reference` | Current `rally-serve` structural+scalar/config reference. |
| `baseline_rnn_reference` | Shipped SlimeVolley RNN comparator. |

Candidate probes:

| Candidate | Label | Definition |
| --- | --- | --- |
| `rw_press_nojump` | structural | When inherited `rear_wall_press` fires, force backward/no-jump action `010`. |
| `rw_press_forcejump` | structural | When inherited `rear_wall_press` fires, force backward+jump action `011`. |
| `rw_post_bounce_retreat` | structural/history | Use 8-frame rear-wall bounce direction checks; after a low rear-wall bounce, retreat toward `min(ball_x - 0.34, defensive_home_x)` with no forced jump. |
| `rw_lowjump_gate_close` | structural/history | When inherited `rear_wall_low_jump` fires farther than `0.28` x-units from the ball, suppress jump and keep forward recovery `100`. |
| `rw_lowjump_direction_gate` | structural/history | When inherited `rear_wall_low_jump` fires before stacked direction confirms a bounce/return, suppress jump and keep forward recovery `100`. |
| `rw_approach_hold_back` | structural/history | If stacked direction says a low far-right ball is still approaching the rear wall and has not bounced, force backward/no-jump `010`. |
| `rw_post_bounce_forward_nojump` | structural/history | If a very low post-bounce rear-wall state is detected, force forward/no-jump `100`. |

## Short Built-In Screen

Seeds: `9000..9015`. Opponent: `builtin`.

| Candidate | Mean | W/L/D | Environment steps | Override frames |
| --- | ---: | --- | ---: | ---: |
| `rally_serve_reference` | `0.3125` | `4/0/12` | `48000` | `0` |
| `baseline_rnn_reference` | `0.1250` | `6/4/6` | `48000` | `0` |
| `rw_press_nojump` | `0.2500` | `4/1/11` | `48000` | `51` |
| `rw_press_forcejump` | `0.3125` | `4/0/12` | `48000` | `41` |
| `rw_post_bounce_retreat` | `0.0625` | `3/3/10` | `48000` | `104` |
| `rw_lowjump_gate_close` | `0.3125` | `4/0/12` | `48000` | `0` |
| `rw_lowjump_direction_gate` | `0.3125` | `4/0/12` | `48000` | `0` |
| `rw_approach_hold_back` | `-0.8125` | `2/7/7` | `46257` | `91` |
| `rw_post_bounce_forward_nojump` | `0.3125` | `4/0/12` | `48000` | `7` |

## Full Built-In Check

Seeds: `9000..9049`. Opponent: `builtin`.

| Candidate | Mean | W/L/D | Environment steps | Override frames |
| --- | ---: | --- | ---: | ---: |
| `rally_serve_reference` | `0.1400` | `13/8/29` | `150000` | `0` |
| `baseline_rnn_reference` | `0.1200` | `18/12/20` | `150000` | `0` |
| `rw_press_nojump` | `0.1200` | `13/9/28` | `150000` | `156` |
| `rw_press_forcejump` | `0.1600` | `13/8/29` | `150000` | `140` |
| `rw_post_bounce_retreat` | `-0.2000` | `9/14/27` | `150000` | `357` |
| `rw_lowjump_gate_close` | `0.1400` | `13/8/29` | `150000` | `0` |
| `rw_lowjump_direction_gate` | `0.1400` | `13/8/29` | `150000` | `0` |
| `rw_approach_hold_back` | `-0.9600` | `5/25/20` | `148170` | `473` |
| `rw_post_bounce_forward_nojump` | `0.1200` | `13/9/28` | `150000` | `20` |

`rw_press_forcejump` beat the built-in-seed `baseline_rnn_reference` mean
(`0.1600` vs `0.1200`), so it was checked against the fixed generation-4
development opponent pool before any promotion recommendation. The two low-jump
gates also scored above the RNN comparator on the built-in row, but they had
zero overrides and matched `rally_serve_reference` exactly on all checked rows.

## Fixed Development Pool Check

Seeds: `9000..9049`. Opponents: `builtin`, `random`, `initial`,
`improved-v0`, `improved-v2`, `improved-v3`, `improved-v4`, `improved-v5`,
`improved-v6`.

| Candidate | Opponent | Mean | W/L/D | Environment steps | Override frames |
| --- | --- | ---: | --- | ---: | ---: |
| `rally_serve_reference` | `builtin` | `0.1400` | `13/8/29` | `150000` | `0` |
| `rally_serve_reference` | `random` | `4.7400` | `50/0/0` | `38217` | `0` |
| `rally_serve_reference` | `initial` | `4.6800` | `50/0/0` | `44634` | `0` |
| `rally_serve_reference` | `improved-v0` | `4.7000` | `50/0/0` | `43242` | `0` |
| `rally_serve_reference` | `improved-v2` | `4.3800` | `49/1/0` | `76391` | `0` |
| `rally_serve_reference` | `improved-v3` | `2.9800` | `48/0/2` | `138122` | `0` |
| `rally_serve_reference` | `improved-v4` | `2.3400` | `44/0/6` | `143814` | `0` |
| `rally_serve_reference` | `improved-v5` | `1.1600` | `32/7/11` | `149716` | `0` |
| `rally_serve_reference` | `improved-v6` | `1.2200` | `32/7/11` | `149716` | `0` |
| `rw_press_forcejump` | `builtin` | `0.1600` | `13/8/29` | `150000` | `140` |
| `rw_press_forcejump` | `random` | `4.7200` | `50/0/0` | `38814` | `133` |
| `rw_press_forcejump` | `initial` | `4.6600` | `50/0/0` | `45025` | `147` |
| `rw_press_forcejump` | `improved-v0` | `4.6800` | `50/0/0` | `43629` | `140` |
| `rw_press_forcejump` | `improved-v2` | `4.4600` | `49/1/0` | `75883` | `168` |
| `rw_press_forcejump` | `improved-v3` | `2.8800` | `47/1/2` | `137642` | `155` |
| `rw_press_forcejump` | `improved-v4` | `2.3000` | `43/1/6` | `143603` | `146` |
| `rw_press_forcejump` | `improved-v5` | `1.1400` | `32/7/11` | `150000` | `166` |
| `rw_press_forcejump` | `improved-v6` | `1.2000` | `32/7/11` | `150000` | `164` |
| `rw_lowjump_gate_close` | `builtin` | `0.1400` | `13/8/29` | `150000` | `0` |
| `rw_lowjump_gate_close` | `random` | `4.7400` | `50/0/0` | `38217` | `0` |
| `rw_lowjump_gate_close` | `initial` | `4.6800` | `50/0/0` | `44634` | `0` |
| `rw_lowjump_gate_close` | `improved-v0` | `4.7000` | `50/0/0` | `43242` | `0` |
| `rw_lowjump_gate_close` | `improved-v2` | `4.3800` | `49/1/0` | `76391` | `0` |
| `rw_lowjump_gate_close` | `improved-v3` | `2.9800` | `48/0/2` | `138122` | `0` |
| `rw_lowjump_gate_close` | `improved-v4` | `2.3400` | `44/0/6` | `143814` | `0` |
| `rw_lowjump_gate_close` | `improved-v5` | `1.1600` | `32/7/11` | `149716` | `0` |
| `rw_lowjump_gate_close` | `improved-v6` | `1.2200` | `32/7/11` | `149716` | `0` |
| `rw_lowjump_direction_gate` | `builtin` | `0.1400` | `13/8/29` | `150000` | `0` |
| `rw_lowjump_direction_gate` | `random` | `4.7400` | `50/0/0` | `38217` | `0` |
| `rw_lowjump_direction_gate` | `initial` | `4.6800` | `50/0/0` | `44634` | `0` |
| `rw_lowjump_direction_gate` | `improved-v0` | `4.7000` | `50/0/0` | `43242` | `0` |
| `rw_lowjump_direction_gate` | `improved-v2` | `4.3800` | `49/1/0` | `76391` | `0` |
| `rw_lowjump_direction_gate` | `improved-v3` | `2.9800` | `48/0/2` | `138122` | `0` |
| `rw_lowjump_direction_gate` | `improved-v4` | `2.3400` | `44/0/6` | `143814` | `0` |
| `rw_lowjump_direction_gate` | `improved-v5` | `1.1600` | `32/7/11` | `149716` | `0` |
| `rw_lowjump_direction_gate` | `improved-v6` | `1.2200` | `32/7/11` | `149716` | `0` |

## Failure Analysis

`rw_press_forcejump` is the only real positive built-in signal: it improves the
full built-in mean from `0.1400` to `0.1600` while preserving W/L/D at
`13/8/29`. The fixed-pool check does not support promotion, though. It regresses
`random`, `initial`, `improved-v0`, `improved-v3`, `improved-v4`, `improved-v5`,
and `improved-v6`; the `improved-v3` and `improved-v4` rows each add one loss.
Only `improved-v2` improves materially (`4.3800` to `4.4600`).

`rw_press_nojump` is not viable. It matches the RNN comparator mean on full
built-in seeds but loses one extra episode relative to the reference
(`13/9/28` vs `13/8/29`) after 156 overrides.

The broad stacked-history direction branches were harmful. `rw_post_bounce_retreat`
and `rw_approach_hold_back` produced many overrides and collapsed both short and
full checks, which suggests that rear-wall post-bounce/approach state is too
brief or too ambiguous for a broad replacement action. `rw_post_bounce_forward_nojump`
was narrower but still dropped to the RNN comparator mean on the full check.

The low-jump gates are behaviorally neutral in this dev run. They produced zero
overrides on built-in and all checked fixed-pool rows, exactly matching
`rally_serve_reference`. These gates are not evidence of a structural fix.

## Promotion Recommendation

Do not promote any candidate from this run.

Top built-in result: `rw_press_forcejump`, mean `0.1600`, W/L/D `13/8/29`,
`150000` environment steps on seeds `9000..9049` against `builtin`. It beats the
built-in-seed RNN comparator (`0.1200`) but fails the fixed-pool robustness
check because most archived-opponent rows regress. The result is useful as a
narrow diagnostic signal: forcing jump inside `rear_wall_press` may rescue one
built-in development point pattern, but it is not robust enough for maintained
policy code.

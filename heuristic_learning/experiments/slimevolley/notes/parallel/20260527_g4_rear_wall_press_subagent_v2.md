# Generation-4 Rear-Wall Press Subagent V2

Date: 2026-05-27

Worker: 3

## Protocol

This was a development-only structural probe run. No main policy, source, test,
ledger, summary, holdout, or audit files were edited or written. The only
repository artifact from this worker is this append-only note. Transient policy
classes were defined in `/tmp/g4_rear_wall_v2_probe.py` and run from
`heuristic_learning/` with `PYTHONPATH=. .venv/bin/python`.

Short-screen seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full development seeds, where expanded:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

No holdout or audit seeds were used.

## Candidate Definitions

All probes wrapped the current `rally-serve` candidate and changed only local
transient action branches.

| Candidate | Structural label | Definition |
| --- | --- | --- |
| `rally_serve_reference` | reference structural+scalar/config | Current `rally-serve` behavior. |
| `rw_timing_backjump` | rear-wall press timing | Earlier rear-wall trigger at `ball_x >= 1.92`, `agent_x >= 1.62`, `0.30 <= ball_y <= 0.78`, `ball_vy < -0.22`, `ball_vx >= -0.55`; action `010` or `011`, with a two-frame hold. |
| `rw_clear_forward_guard` | wall-clear detector | Six-frame detector for high-x vx flip or x-turn near the rear wall; for low balls moving left, recover with `100`, jumping only on close contact. |
| `rw_airborne_recovery` | backward+jump recovery / airborne guard | If agent is already above a late low rear-wall ball, suppress jump and use `100` when the ball has cleared left, else `010`. |
| `rw_stacked_chase_guard` | stacked-frame bad-wall guard | Five-frame detector for low rear-wall balls not clearing left while the agent is already above the ball; force `000`. |

## Short Screen

Seeds: `9000..9015`. Opponents: `builtin`, `improved-v3`, `improved-v6`.

| Candidate | Opponent | Mean | W/L/D | Steps | Override frames |
| --- | --- | ---: | --- | ---: | ---: |
| `rally_serve_reference` | `builtin` | `0.3125` | `4/0/12` | `48000` | `0` |
| `rally_serve_reference` | `improved-v3` | `3.0000` | `16/0/0` | `41298` | `0` |
| `rally_serve_reference` | `improved-v6` | `1.1875` | `9/3/4` | `48000` | `0` |
| `rw_timing_backjump` | `builtin` | `-0.8750` | `1/9/6` | `48000` | `173` |
| `rw_timing_backjump` | `improved-v3` | `2.2500` | `13/1/2` | `40599` | `179` |
| `rw_timing_backjump` | `improved-v6` | `0.3750` | `7/3/6` | `46064` | `214` |
| `rw_clear_forward_guard` | `builtin` | `0.2500` | `3/0/13` | `48000` | `16` |
| `rw_clear_forward_guard` | `improved-v3` | `3.1250` | `16/0/0` | `41918` | `15` |
| `rw_clear_forward_guard` | `improved-v6` | `1.2500` | `8/3/5` | `48000` | `15` |
| `rw_airborne_recovery` | `builtin` | `0.3125` | `4/0/12` | `48000` | `1` |
| `rw_airborne_recovery` | `improved-v3` | `3.0000` | `16/0/0` | `41298` | `0` |
| `rw_airborne_recovery` | `improved-v6` | `1.1875` | `9/3/4` | `48000` | `0` |
| `rw_stacked_chase_guard` | `builtin` | `0.3125` | `4/0/12` | `48000` | `1` |
| `rw_stacked_chase_guard` | `improved-v3` | `3.0000` | `16/0/0` | `41298` | `3` |
| `rw_stacked_chase_guard` | `improved-v6` | `1.0625` | `9/4/3` | `48000` | `10` |

`rw_timing_backjump` collapsed immediately and was not expanded.
`rw_stacked_chase_guard` tied built-in but regressed `improved-v6`, so it was
not expanded. `rw_clear_forward_guard` and `rw_airborne_recovery` were the only
non-collapsing variants expanded.

## Full Development Checks

Seeds: `9000..9049`. `rw_airborne_recovery` full-pool expansion was interrupted
by the leader status request and stopped after `improved-v2`; rows below are the
completed rows only.

| Candidate | Opponent | Mean | W/L/D | Steps | Override frames |
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
| `rw_clear_forward_guard` | `builtin` | `0.0800` | `10/8/32` | `150000` | `35` |
| `rw_clear_forward_guard` | `random` | `4.7600` | `50/0/0` | `38351` | `23` |
| `rw_clear_forward_guard` | `initial` | `4.7000` | `50/0/0` | `44686` | `32` |
| `rw_clear_forward_guard` | `improved-v0` | `4.7200` | `50/0/0` | `43295` | `28` |
| `rw_clear_forward_guard` | `improved-v2` | `4.4000` | `49/1/0` | `77520` | `31` |
| `rw_clear_forward_guard` | `improved-v3` | `2.9800` | `48/0/2` | `138742` | `35` |
| `rw_clear_forward_guard` | `improved-v4` | `2.4000` | `45/0/5` | `143857` | `32` |
| `rw_clear_forward_guard` | `improved-v5` | `1.1600` | `31/8/11` | `149716` | `51` |
| `rw_clear_forward_guard` | `improved-v6` | `1.1800` | `31/8/11` | `149716` | `41` |
| `rw_airborne_recovery` | `builtin` | `0.1400` | `13/8/29` | `150000` | `1` |
| `rw_airborne_recovery` | `random` | `4.7400` | `50/0/0` | `38217` | `6` |
| `rw_airborne_recovery` | `initial` | `4.6800` | `50/0/0` | `44634` | `6` |
| `rw_airborne_recovery` | `improved-v0` | `4.7000` | `50/0/0` | `43242` | `6` |
| `rw_airborne_recovery` | `improved-v2` | `4.3800` | `49/1/0` | `76391` | `6` |

## Failure Analysis

`rw_timing_backjump` was too broad. On the short screen it overrode 173 built-in
frames and moved the built-in row from `4/0/12` to `1/9/6`. The failure mode is
not just bad jump timing; holding a rear-wall press for extra frames keeps the
agent in a losing low-right chase.

`rw_clear_forward_guard` found a real but bad tradeoff. It improved several
archived cells slightly, including `random`, `initial`, `improved-v0`,
`improved-v2`, and `improved-v4`, but full built-in fell from `0.1400` to
`0.0800` and W/L/D fell from `13/8/29` to `10/8/32`. It also regressed the
harder archived tail: `improved-v5` added one loss and `improved-v6` dropped
from `1.2200` to `1.1800`. This looks like a wall-clear rule that is useful in
some self-play geometries but steals too many built-in contacts.

`rw_airborne_recovery` was effectively neutral in completed full rows. It tied
`rally_serve_reference` on built-in, random, initial, `improved-v0`, and
`improved-v2`, with only one built-in override and six overrides in each
completed archived row. It is too sparse to claim a structural improvement, and
the full fixed-pool expansion did not complete after the leader requested an
immediate artifact.

`rw_stacked_chase_guard` tied built-in on the short subset but regressed the
hard archived short check against `improved-v6` from `1.1875` to `1.0625`.
Forcing no-op on stacked bad-wall states is therefore not robust enough to
expand.

## Promotion Recommendation

Do not promote any v2 rear-wall press candidate.

Best completed built-in result: `rw_airborne_recovery`, tied with
`rally_serve_reference` at mean `0.1400`, W/L/D `13/8/29`, but did not improve
any completed full row.

Best archived tradeoff probe: `rw_clear_forward_guard`, but it regressed
built-in full development score and the harder archived tail. It should not be
recommended based on archived gains alone.

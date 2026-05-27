# Generation-4 Trace: Attack/Net-Pressure vs Baseline-RNN

Date: 2026-05-27

## Scope

Worker D ran development-only trace diagnostics. No policy edits were made. No
holdout, audit, or final-eval seeds were used. The successful diagnostic used
`ledger_path=None`, `summary_path=None`, and `trace_window=24`.

Exact seeds: `9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009,
9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021,
9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033,
9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045,
9046, 9047, 9048, 9049`.

Policies compared as agents: `attack`, `net-pressure`, `baseline-rnn`.
Opponent for all rows: `builtin` (`slimevolleygym` built-in baseline RNN).

## Commands

- `python3 - <<'PY' ... evaluate_slimevolley(... seed_start=9000, episodes=50, trace_window=24, ledger_path=None, summary_path=None) ... PY`
  failed under system Python because SlimeVolley dependencies were unavailable.
- `python3 -m hl_benchmark.custom_envs.slimevolley.doctor` returned
  `status=unavailable` for system Python.
- `.venv/bin/python -m hl_benchmark.custom_envs.slimevolley.doctor` returned
  `status=available`.
- `.venv/bin/python - <<'PY' ... evaluate_slimevolley(... seed_start=9000, episodes=50, trace_window=24, ledger_path=None, summary_path=None) ... PY`
  produced the metrics below.

## Results

| Policy | Opponent | Mean | W-L-D | Steps | Points won-lost |
| --- | --- | ---: | --- | ---: | ---: |
| `attack` | `builtin` | `-0.3000` | `7-18-25` | `150000` | `17-32` |
| `net-pressure` | `builtin` | `-0.2200` | `7-14-29` | `150000` | `19-30` |
| `baseline-rnn` | `builtin` | `0.1200` | `18-12-20` | `150000` | `31-25` |

Same-seed deltas vs `baseline-rnn`:

| Policy | Mean delta | Better / worse / same seeds |
| --- | ---: | --- |
| `attack` | `-0.4200` | `9 / 24 / 17` |
| `net-pressure` | `-0.3400` | `13 / 25 / 12` |

Action frequencies:

| Policy | `000` | `001` | `010` | `011` | `100` | `101` | `110` | `111` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `attack` | `67891` | `10569` | `34068` | `1363` | `32965` | `3144` | `0` | `0` |
| `net-pressure` | `66716` | `9702` | `33469` | `1334` | `32046` | `6733` | `0` | `0` |
| `baseline-rnn` | `2891` | `12644` | `23751` | `1184` | `9288` | `53725` | `43727` | `2790` |

`net-pressure` more than doubles `101` use versus `attack`, but still uses no
`110`/`111` and remains far from the RNN's jump-heavy distribution.

## Trace Observations

Terminal loss buckets:

| Policy | low left/net | low other own-side | low mid-right | low far-right |
| --- | ---: | ---: | ---: | ---: |
| `attack` | `17` | `5` | `2` | `8` |
| `net-pressure` | `13` | `9` | `4` | `4` |
| `baseline-rnn` | `7` | `0` | `2` | `16` |

Terminal win buckets were all low left/net: `attack=17`, `net-pressure=19`,
`baseline-rnn=31`.

Terminal heuristic loss modes were concentrated in current-frame low-receive
branches:

| Policy | Main terminal loss modes |
| --- | --- |
| `attack` | `grounded_low_receive=16`, `low_ball_rescue=8`, `rear_wall_low_jump=4`, `rear_wall_press=4` |
| `net-pressure` | `grounded_low_receive=13`, `low_ball_rescue=9`, `late_low_ball_guard=3`, `rear_wall_low_jump=3` |

Terminal win actions show the main behavioral gap:

| Policy | Terminal win actions |
| --- | --- |
| `attack` | `100=7`, `010=5`, `000=5` |
| `net-pressure` | `100=9`, `000=7`, `010=3` |
| `baseline-rnn` | `101=28`, `110=2`, `001=1` |

Loss trace windows were contact-like and low own-side for the heuristics:

| Policy | Contact-like losses | Low own-side losses | Front/net low losses | Rear low losses |
| --- | ---: | ---: | ---: | ---: |
| `attack` | `30/32` | `32/32` | `19/32` | `11/32` |
| `net-pressure` | `29/30` | `30/30` | `14/30` | `13/30` |
| `baseline-rnn` | `21/25` | `25/25` | `7/25` | `16/25` |

Velocity-history signals are strong: `attack` loss traces had `vx` flips in
`30/32` point losses, and `net-pressure` had `vx` flips in `29/30` point losses.
The current attack/net-pressure family does not use stacked observation history
in these low-receive decisions; it mostly reacts to the current frame after a
contact-like velocity change has already happened.

## Failure Analysis

`attack` lags because its late-contact rule does not repair the dominant
failure mode: low own-side post-contact recovery. Its losses are mostly
`grounded_low_receive` and `low_ball_rescue`, with point-loss traces showing
recent velocity flips and low own-side geometry.

`net-pressure` helps slightly but is not the right branch by itself. It reduces
episode losses from `18` to `14` and raises points won from `17` to `19`, but
it still trails `baseline-rnn` by `-0.34` mean. It also shifts some failures
into `low_other_own_side` and leaves `grounded_low_receive`/`low_ball_rescue`
as the dominant terminal loss modes. The pressure rule appeared in only `3`
winning and `2` losing point-event windows, so broader front-court pressure is
not directly addressing the common loss path.

The RNN's advantage is not just "more jumping." Its terminal wins are mostly
`101`/`110` at low left/net states, while heuristic terminal wins are
movement-only. The useful signal is when to convert after contact-like velocity
flips, not a scalar increase in unconditional pressure.

## Recommendation

Do not promote `attack` or `net-pressure` from this artifact. Keep this as
development-only diagnosis.

Next research branch: a narrow stacked-frame post-contact/low-receive branch.
Track 2-4 recent observations for own-contact and upward-flip features
(`vx` sign flip, `vy` upward flip, and low own-side geometry). Use that gate to
decide whether `grounded_low_receive` should suppress jump, recover, or attempt
`101` conversion near the net. This is better supported than widening
`net_pressure`, adding a longer serve macro, or scalar tuning the current-frame
thresholds.

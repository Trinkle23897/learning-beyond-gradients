# G4 Rear-Wall Press Worker C Probe

Date: 2026-05-27

## Protocol

Development-only, no-ledger structural branch probe. Maintained policy code,
canonical ledgers, summaries, holdout artifacts, and audit artifacts were not
edited or written. Transient probe code and JSON output stayed in `/tmp`:

- `/tmp/g4_rear_wall_press_worker_c_probe.py`
- `/tmp/g4_rear_wall_press_worker_c_results_v2.json`

Short-screen seeds used exactly: `9000, 9001, 9002, 9003, 9004, 9005, 9006,
9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`.

Full development seeds used exactly: `9000, 9001, 9002, 9003, 9004, 9005,
9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017,
9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029,
9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041,
9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`.

No holdout seeds `10000..10049`, audit seeds `11000..11049`, or final-eval
commands were used.

## Candidate Definitions

`rally_reference` is the current `rally-serve` reference and must be labeled
structural plus scalar/config because it includes the rally-serve detector on a
scalar-tuned baseline. `baseline_rnn` is the neural comparator. All other
candidates are transient structural probes wrapping `rally_reference`:

- `rw_press_always_jump`: when inherited `rear_wall_press` fires, force
  backward+jump `011`.
- `rw_press_return_forward`: when `rear_wall_press` sees `ball_vx < -0.12`,
  recover forward instead of pressing the wall.
- `rw_press_close_only`: suppress far/clearing `rear_wall_press` and recover to
  defensive home.
- `rw_exit_recover_four`: after `rear_wall_press` or `rear_wall_low_jump`, hold
  up to four frames of forward recovery while the low ball exits the rear wall.
- `rw_wall_turn_jump_close`: use an 8-frame rear-wall turn detector, recover
  forward, and jump only on close contact.
- `rw_airborne_rear_recover`: if the agent is above a late rear-wall ball,
  recover instead of pressing.
- `rw_lowjump_nojump_recover`: replace inherited `rear_wall_low_jump` with
  forward/no-jump recovery.

## Results

Short screen, seeds `9000..9015`, opponents `builtin`, `improved-v3`,
`improved-v6`:

| Candidate | Builtin mean W/L/D steps | v3 mean W/L/D steps | v6 mean W/L/D steps |
| --- | --- | --- | --- |
| `rally_reference` | `0.3125` `4/0/12` `48000` | `3.0000` `16/0/0` `41298` | `1.1875` `9/3/4` `48000` |
| `baseline_rnn` | `0.1250` `6/4/6` `48000` | `3.9375` `16/0/0` `37225` | `2.5625` `14/1/1` `45819` |
| `rw_press_always_jump` | `0.3125` `4/0/12` `48000` | `2.8750` `16/0/0` `41098` | `1.1875` `9/3/4` `48000` |
| `rw_press_return_forward` | `-0.3125` `1/5/10` `48000` | `2.4375` `14/0/2` `41248` | `0.6250` `8/5/3` `48000` |
| `rw_press_close_only` | `-0.1875` `2/4/10` `48000` | `2.6250` `14/0/2` `41248` | `0.6250` `8/5/3` `48000` |
| `rw_exit_recover_four` | `0.3125` `4/0/12` `48000` | `3.0000` `16/0/0` `41298` | `1.1875` `9/3/4` `48000` |
| `rw_wall_turn_jump_close` | `-0.3125` `1/5/10` `48000` | `2.7500` `15/0/1` `41277` | `0.8750` `8/4/4` `48000` |
| `rw_airborne_rear_recover` | `0.3125` `4/0/12` `48000` | `3.0000` `16/0/0` `41298` | `1.1250` `9/4/3` `48000` |
| `rw_lowjump_nojump_recover` | `0.3125` `4/0/12` `48000` | `3.0000` `16/0/0` `41298` | `1.1875` `9/3/4` `48000` |

Full built-in check, seeds `9000..9049`:

| Candidate | Mean | W/L/D | Steps | Override frames |
| --- | ---: | --- | ---: | ---: |
| `rally_reference` | `0.1400` | `13/8/29` | `150000` | `0` |
| `baseline_rnn` | `0.1200` | `18/12/20` | `150000` | `0` |
| `rw_press_always_jump` | `0.1600` | `13/8/29` | `150000` | `140` |
| `rw_exit_recover_four` | `0.1200` | `13/8/29` | `150000` | `121` |
| `rw_lowjump_nojump_recover` | `0.1400` | `13/8/29` | `150000` | `15` |

Fixed development pool for the only built-in-improving probe,
`rw_press_always_jump`, seeds `9000..9049`:

| Opponent | Reference mean W/L/D steps | `rw_press_always_jump` mean W/L/D steps |
| --- | --- | --- |
| `builtin` | `0.1400` `13/8/29` `150000` | `0.1600` `13/8/29` `150000` |
| `random` | `4.7400` `50/0/0` `38217` | `4.7200` `50/0/0` `38814` |
| `initial` | `4.6800` `50/0/0` `44634` | `4.6600` `50/0/0` `45025` |
| `improved-v0` | `4.7000` `50/0/0` `43242` | `4.6800` `50/0/0` `43629` |
| `improved-v2` | `4.3800` `49/1/0` `76391` | `4.4600` `49/1/0` `75883` |
| `improved-v3` | `2.9800` `48/0/2` `138122` | `2.8800` `47/1/2` `137642` |
| `improved-v4` | `2.3400` `44/0/6` `143814` | `2.3000` `43/1/6` `143603` |
| `improved-v5` | `1.1600` `32/7/11` `149716` | `1.1400` `32/7/11` `150000` |
| `improved-v6` | `1.2200` `32/7/11` `149716` | `1.2000` `32/7/11` `150000` |

## Failure Analysis

The broad recovery interpretations were harmful. `rw_press_return_forward`,
`rw_press_close_only`, and `rw_wall_turn_jump_close` converted short-screen
rear-wall states into immediate rear-low losses and collapsed against the
built-in opponent. `rw_exit_recover_four` survived the short screen but dropped
from `0.1400` to `0.1200` on full built-in seeds after `121` overrides.

`rw_lowjump_nojump_recover` was effectively neutral on full built-in seeds:
same mean and W/L/D as reference with only `15` override frames. That is not
evidence for a structural fix.

`rw_press_always_jump` is the only positive built-in signal: it raises built-in
mean from `0.1400` to `0.1600` without changing W/L/D. The fixed-pool check
does not support promotion. It regresses `random`, `initial`, `improved-v0`,
`improved-v3`, `improved-v4`, `improved-v5`, and `improved-v6`; only
`improved-v2` improves. The added jump appears to rescue a narrow built-in
trajectory while making archived-opponent rear-wall exchanges less robust.

## Promotion Recommendation

Do not promote any candidate.

`rw_press_always_jump` should remain a diagnostic clue, not maintained policy:
it beats the built-in dev mean and the built-in-seed RNN comparator, but fails
the fixed generation-4 development-pool robustness check. No holdout or audit
evaluation is warranted from this run.

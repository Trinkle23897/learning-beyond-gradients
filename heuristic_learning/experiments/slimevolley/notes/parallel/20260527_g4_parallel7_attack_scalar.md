# Generation-4 Parallel7 Attack Scalar/Config Search

Date: 2026-05-27

Worker: A

Label: `kind=scalar/config`

## Protocol

This was a development-only scalar/config search around the registered
`attack` policy. No shared policy, evaluation, report, ledger, summary, or
result code was edited. The only repository artifact created by this worker is
this note.

Runs were executed from `heuristic_learning` with `PYTHONPATH=.` and the
repo-local virtualenv. Temporary artifacts:

- `/tmp/g4_parallel7_attack_scalar.py`
- `/tmp/g4_parallel7_attack_scalar_results.json`

Commands:

```bash
cd /home/alpha/dev/research/learning-beyond-gradients/heuristic_learning
PYTHONPATH=. .venv/bin/python /tmp/g4_parallel7_attack_scalar.py
python3 -m py_compile /tmp/g4_parallel7_attack_scalar.py
```

No holdout or audit seeds were used. The only seeds used were the allowed
generation-4 development seeds.

Short-screen seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full built-in validation seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

All attack candidates used policy `attack` with a full config cloned from
`IMPROVED_TUNED_CONFIG`, then only the listed delta was applied. This avoids
partial-JSON fallback to raw `SlimeVolleyConfig()` defaults.

Base registered-attack tuned fields relative to `SlimeVolleyConfig()`:

- `x_margin=0.04`
- `contact_x_window=0.14`
- `high_arc_horizon=0.85`
- `overcommit_guard_x=0.18`
- `low_ball_rescue_x_window=0.72`
- `low_ball_rescue_horizon=0.06`
- `grounded_low_receive_airborne_margin=0.12`

## Candidate Definitions

Reference policies:

- `baseline_rnn`: policy `baseline-rnn`
- `rally_serve_reference`: policy `rally-serve`
- `attack_reference`: policy `attack`, no config delta

Attack search candidates:

| Candidate | Kind | Policy | Delta from registered `attack` config |
| --- | --- | --- | --- |
| `home_0.78` | scalar | `attack` | `attack_home_x=0.78` |
| `late_y_min_0.24` | scalar | `attack` | `late_attack_y_min=0.24` |
| `late_y_max_0.70` | scalar | `attack` | `late_attack_y_max=0.70` |
| `late_vx_m0.40` | scalar | `attack` | `late_attack_vx=-0.40` |
| `late_vy_m0.20` | scalar | `attack` | `late_attack_vy=-0.20` |
| `late_dx_min_0.00` | scalar | `attack` | `late_attack_dx_min=0.00` |
| `late_dx_max_0.32` | scalar | `attack` | `late_attack_dx_max=0.32` |
| `late_rule_relaxed` | config | `attack` | `late_attack_y_min=0.24`, `late_attack_y_max=0.70`, `late_attack_vx=-0.40`, `late_attack_vy=-0.20`, `late_attack_dx_min=0.00`, `late_attack_dx_max=0.32` |
| `late_rule_strict` | config | `attack` | `attack_home_x=0.78`, `late_attack_vx=-0.45`, `late_attack_vy=-0.30`, `late_attack_dx_max=0.34` |

## Short Built-In Screen

Opponent: `builtin`. Seeds: `9000..9015`.

| Candidate | Kind | Mean | W-L-D | Steps |
| --- | --- | ---: | --- | ---: |
| `baseline_rnn` | reference | `0.1250` | `6-4-6` | `48000` |
| `rally_serve_reference` | reference | `0.3125` | `4-0-12` | `48000` |
| `attack_reference` | reference | `-0.1250` | `2-4-10` | `48000` |
| `home_0.78` | scalar | `-0.1250` | `2-4-10` | `48000` |
| `late_y_min_0.24` | scalar | `-0.1250` | `2-4-10` | `48000` |
| `late_y_max_0.70` | scalar | `-0.3750` | `2-8-6` | `48000` |
| `late_vx_m0.40` | scalar | `-0.0625` | `2-3-11` | `48000` |
| `late_vy_m0.20` | scalar | `-0.2500` | `1-5-10` | `48000` |
| `late_dx_min_0.00` | scalar | `-0.1875` | `1-4-11` | `48000` |
| `late_dx_max_0.32` | scalar | `-0.1250` | `2-4-10` | `48000` |
| `late_rule_relaxed` | config | `-0.5000` | `1-8-7` | `48000` |
| `late_rule_strict` | config | `-0.2500` | `1-5-10` | `48000` |

Full-validation budget rule: advance the top four attack-family rows from the
short built-in screen by mean, then wins, then fewer losses. That yielded
`late_vx_m0.40`, `attack_reference`, `home_0.78`, and `late_y_min_0.24`.

## Full Built-In Validation

Opponent: `builtin`. Seeds: `9000..9049`.

| Candidate | Kind | Mean | W-L-D | Steps |
| --- | --- | ---: | --- | ---: |
| `baseline_rnn` | reference | `0.1200` | `18-12-20` | `150000` |
| `rally_serve_reference` | reference | `0.1400` | `13-8-29` | `150000` |
| `attack_reference` | reference | `-0.3000` | `7-18-25` | `150000` |
| `home_0.78` | scalar | `-0.3000` | `7-18-25` | `150000` |
| `late_y_min_0.24` | scalar | `-0.3000` | `7-18-25` | `150000` |
| `late_vx_m0.40` | scalar | `-0.2800` | `7-17-26` | `150000` |

No attack-family candidate beat the `baseline_rnn` full built-in mean of
`0.1200`. Because the promotion gate was not met, no fixed development
opponent-pool check was run.

## Failure Analysis

Most local attack-only scalar moves were inert. `home_0.78`,
`late_y_min_0.24`, and `late_dx_max_0.32` exactly matched the registered
`attack` row on the short screen, and the two advanced tied rows also matched
`attack_reference` on full built-in validation.

The only variant that changed the full built-in row at all was `late_vx_m0.40`.
It improved the short built-in mean from `-0.1250` to `-0.0625` and the full
built-in mean from `-0.3000` to `-0.2800`, converting one loss into a draw.
That is too small to matter for promotion. It remains `0.4000` behind
`baseline_rnn` and `0.4200` behind `rally-serve` on the same full dev seeds.

Broadening the late-attack window was actively harmful. `late_y_max_0.70`
regressed to `-0.3750` on the short screen, and the broad combo
`late_rule_relaxed` fell further to `-0.5000`, `1-8-7`. Tightening the rule in
`late_rule_strict` also regressed to `-0.2500`, `1-5-10`. That pattern matches
earlier generation-4 evidence: local threshold motion around the `attack`
trigger can move a few draws and losses, but it does not close the built-in gap
and often makes the low-contact branch less stable.

This worker therefore found no candidate worth escalating to fixed-pool
validation. Under the stated rules, built-in-only evidence is not enough, and
here even the built-in gate was not passed.

## Promotion Recommendation

Do not promote any candidate from this worker run.

Best dev-only row: `late_vx_m0.40` with `late_attack_vx=-0.40`. Its full
built-in result was `-0.2800`, `7-17-26`, `150000` steps, which is only a
small improvement over `attack_reference` and still materially below both
`baseline_rnn` and `rally-serve`. Because no candidate beat `baseline_rnn` on
full built-in dev seeds `9000..9049`, no fixed dev opponent-pool check was
required and no promotion is recommended.

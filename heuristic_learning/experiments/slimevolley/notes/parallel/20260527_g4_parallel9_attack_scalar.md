# Generation-4 Parallel9 Attack Scalar/Config Search

Date: 2026-05-27

Worker: A

Label: `scalar/config` around policy `attack`

## Protocol

This was a development-only no-ledger scalar/config probe around the maintained
`attack` policy family. No maintained policy code, tests, ledger, summary CSV,
holdout artifact, or audit artifact was edited. The only repo artifacts from
this worker run are:

- `experiments/slimevolley/results/generation_4_parallel9_attack_scalar_probe.json`
- `experiments/slimevolley/notes/parallel/20260527_g4_parallel9_attack_scalar.md`

Commands:

```bash
cd /home/alpha/dev/research/learning-beyond-gradients/heuristic_learning
.venv/bin/python -m py_compile /tmp/g4_parallel9_attack_scalar_probe.py
PYTHONPATH=. .venv/bin/python /tmp/g4_parallel9_attack_scalar_probe.py
```

Scratch files:

- `/tmp/g4_parallel9_attack_scalar_probe.py`
- `/tmp/g4_parallel9_attack_scalar_probe_summary.json`

No holdout or audit seeds were used. No `10000..10049` or `11000..11049`
episode was opened.

Short-screen seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full built-in validation seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

Fixed development opponent pool, only available if an attack-family candidate
beat `baseline-rnn` on full built-in development seeds:

`builtin, random, initial, improved-v0, improved-v2, improved-v3, improved-v4, improved-v5, improved-v6`

All attack-family rows used policy `attack` with a full config cloned from
`IMPROVED_TUNED_CONFIG`, then only the listed delta was applied. This keeps the
attack structure fixed and avoids partial-config fallback to raw
`SlimeVolleyConfig()` defaults.

## Candidate Definitions

| Label | Kind | Policy | Delta |
| --- | --- | --- | --- |
| `attack_reference` | reference | `attack` | none |
| `baseline_rnn` | neural comparator | `baseline-rnn` | none |
| `low_x_0.48` | scalar | `attack` | `low_ball_rescue_x_window=0.48` |
| `low_x_0.52` | scalar | `attack` | `low_ball_rescue_x_window=0.52` |
| `low_x_0.64` | scalar | `attack` | `low_ball_rescue_x_window=0.64` |
| `low_horizon_0.04` | scalar | `attack` | `low_ball_rescue_horizon=0.04` |
| `low_horizon_0.08` | scalar | `attack` | `low_ball_rescue_horizon=0.08` |
| `late_vx_m0.45` | scalar | `attack` | `late_attack_vx=-0.45` |
| `late_vx_m0.55` | scalar | `attack` | `late_attack_vx=-0.55` |
| `late_vy_m0.30` | scalar | `attack` | `late_attack_vy=-0.30` |
| `late_dx_wide` | config | `attack` | `late_attack_dx_min=-0.02`, `late_attack_dx_max=0.34` |
| `rank1_builtin_combo` | config | `attack` | `high_arc_horizon=0.95`, `overcommit_guard_x=0.20`, `grounded_low_receive_airborne_margin=0.16`, `late_attack_vx=-0.45` |
| `rank2_lowx64_combo` | config | `attack` | `high_arc_horizon=0.95`, `low_ball_rescue_x_window=0.64`, `grounded_low_receive_airborne_margin=0.20`, `late_attack_vx=-0.45`, `late_attack_dx_max=0.42` |
| `fast_contact_combo` | config | `attack` | `late_attack_vx=-0.55`, `late_attack_vy=-0.30`, `late_attack_dx_min=-0.02`, `late_attack_dx_max=0.34` |

## Short Built-In Screen

Opponent: `builtin`. Seeds: `9000..9015`.

| Label | Kind | Mean | W-L-D | Steps |
| --- | --- | ---: | --- | ---: |
| `attack_reference` | reference | `-0.1250` | `2-4-10` | `48000` |
| `baseline_rnn` | neural comparator | `0.1250` | `6-4-6` | `48000` |
| `low_x_0.48` | scalar | `0.0625` | `3-2-11` | `48000` |
| `low_x_0.52` | scalar | `-0.0625` | `2-3-11` | `48000` |
| `low_x_0.64` | scalar | `-0.2500` | `2-4-10` | `48000` |
| `low_horizon_0.04` | scalar | `-0.6250` | `2-8-6` | `48000` |
| `low_horizon_0.08` | scalar | `-1.1875` | `1-11-4` | `48000` |
| `late_vx_m0.45` | scalar | `-0.1250` | `2-4-10` | `48000` |
| `late_vx_m0.55` | scalar | `-0.1875` | `2-5-9` | `48000` |
| `late_vy_m0.30` | scalar | `-0.2500` | `1-5-10` | `48000` |
| `late_dx_wide` | config | `-0.2500` | `4-6-6` | `48000` |
| `rank1_builtin_combo` | config | `0.1875` | `4-1-11` | `48000` |
| `rank2_lowx64_combo` | config | `0.1250` | `4-2-10` | `48000` |
| `fast_contact_combo` | config | `0.0625` | `7-5-4` | `48000` |

Full-validation selection rule: advance attack-family rows that met or exceeded
the `baseline_rnn` short-screen mean; if fewer than four did, fill to four
with the best rows that at least matched `attack_reference`, ordered by mean,
wins, fewer losses, then label. That advanced:

- `rank1_builtin_combo`
- `rank2_lowx64_combo`
- `fast_contact_combo`
- `low_x_0.48`

## Full Built-In Validation

Opponent: `builtin`. Seeds: `9000..9049`.

| Label | Kind | Mean | W-L-D | Steps |
| --- | --- | ---: | --- | ---: |
| `baseline_rnn` | neural comparator | `0.1200` | `18-12-20` | `150000` |
| `attack_reference` | reference | `-0.3000` | `7-18-25` | `150000` |
| `rank1_builtin_combo` | config | `-0.1000` | `11-13-26` | `150000` |
| `rank2_lowx64_combo` | config | `-0.1000` | `11-14-25` | `150000` |
| `fast_contact_combo` | config | `-0.1600` | `11-17-22` | `150000` |
| `low_x_0.48` | scalar | `-0.1200` | `7-14-29` | `150000` |

No attack-family candidate beat the `baseline_rnn` full built-in mean of
`0.1200`. Therefore no fixed development opponent-pool check was run.

## Failure Analysis

The short built-in screen again overstated the attack-family upside. The best
screen row, `rank1_builtin_combo`, rose from `attack_reference` `-0.1250` to
`0.1875` on `9000..9015`, but fell back to `-0.1000` on `9000..9049`. The
closely related `rank2_lowx64_combo` behaved the same way, also landing at
`-0.1000`. Both rows reproduce the earlier joint-search pattern: they narrow
the built-in gap versus `attack_reference` but still miss the `baseline_rnn`
dev comparator by `0.2200`.

Pure low-ball rescue edits remain bounded. `low_x_0.48` was the best scalar-only
row in this pass, improving `attack_reference` from `-0.3000` to `-0.1200` on
full built-in seeds, but it still stayed `0.2400` below `baseline_rnn`. The
broader `low_x_0.64` scalar regressed on the short screen, and the rescue
horizon edits were clearly harmful: `low_horizon_0.04` fell to `-0.6250` and
`low_horizon_0.08` to `-1.1875` even before full validation.

Late-attack threshold moves were mostly inert or harmful in isolation.
`late_vx_m0.45` exactly matched `attack_reference` on the short screen,
`late_vx_m0.55` and `late_vy_m0.30` both regressed, and the widened
`late_dx_wide` contact band produced extra losses without improving mean. The
best late-attack-heavy combo, `fast_contact_combo`, looked lively on the short
screen because it traded draws for wins, but the full built-in row still landed
at `-0.1600` with `17` losses.

The broader pattern is unchanged: scalar/config movement can recover part of
the built-in gap for `attack`, but it does not produce a candidate that clears
the packaged neural comparator on full development seeds. Because the built-in
promotion gate was not met, a fixed-pool check would have been extra probing
rather than required evidence.

## Promotion Recommendation

Do not promote any candidate from this worker run.

Best dev-only row: `rank1_builtin_combo`, a config-only `attack` variant with
`high_arc_horizon=0.95`, `overcommit_guard_x=0.20`,
`grounded_low_receive_airborne_margin=0.16`, and `late_attack_vx=-0.45`. Its
full built-in result was `-0.1000`, `11-13-26`, `150000` steps. It improves
`attack_reference` but does not beat `baseline_rnn`, so no fixed-pool
promotion check was triggered and no promotion is recommended.

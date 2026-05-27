# Generation-4 Parallel8 Attack Scalar/Config Search

Date: 2026-05-27

Worker: A

Label: `scalar/config` around policy `attack`

## Protocol

This was a development-only no-ledger scalar/config screen around the registered
`attack` policy. No policy module, report, README, ledger, summary, or existing
result file was edited. The only repository artifact from this worker is this
note.

Commands:

```bash
cd /home/alpha/dev/research/learning-beyond-gradients/heuristic_learning
.venv/bin/python -m py_compile /tmp/g4_parallel8_attack_scalar.py
.venv/bin/python /tmp/g4_parallel8_attack_scalar.py
```

Scratch files:

- `/tmp/g4_parallel8_attack_scalar.py`
- `/tmp/g4_parallel8_attack_scalar_results.json`

No holdout or audit seeds were used. No `10000..10049` or `11000..11049`
episode was opened.

Short-screen seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full built-in validation seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

Fixed development opponent pool, available only if a candidate beat
`baseline-rnn` on full built-in development seeds:

`builtin, random, initial, improved-v0, improved-v2, improved-v3, improved-v4, improved-v5, improved-v6`

All attack candidates used policy `attack`. Unless noted otherwise, scalar and
config rows used a full config cloned from `IMPROVED_TUNED_CONFIG`, then only
the listed delta was applied. This avoids partial-config fallback to raw
`SlimeVolleyConfig()` defaults.

## Candidate Definitions

Reference rows:

| Label | Kind | Policy | Delta |
| --- | --- | --- | --- |
| `baseline_rnn` | reference | `baseline-rnn` | none |
| `rally_serve_reference` | reference | `rally-serve` | none |
| `post_contact_reference` | reference | `post-contact` | none |
| `attack_reference` | reference | `attack` | none |

Attack search rows:

| Label | Kind | Policy | Delta |
| --- | --- | --- | --- |
| `home_0.74` | scalar | `attack` | `attack_home_x=0.74` |
| `home_0.90` | scalar | `attack` | `attack_home_x=0.90` |
| `late_y_band_0.22_0.60` | config | `attack` | `late_attack_y_min=0.22`, `late_attack_y_max=0.60` |
| `late_y_band_0.30_0.72` | config | `attack` | `late_attack_y_min=0.30`, `late_attack_y_max=0.72` |
| `late_vx_m0.30` | scalar | `attack` | `late_attack_vx=-0.30` |
| `late_vx_m0.50` | scalar | `attack` | `late_attack_vx=-0.50` |
| `late_vy_m0.05` | scalar | `attack` | `late_attack_vy=-0.05` |
| `late_vy_m0.25` | scalar | `attack` | `late_attack_vy=-0.25` |
| `dx_tight_0.08_0.24` | config | `attack` | `late_attack_dx_min=0.08`, `late_attack_dx_max=0.24` |
| `dx_wide_0.00_0.36` | config | `attack` | `late_attack_dx_min=0.00`, `late_attack_dx_max=0.36` |
| `trigger_relaxed_mid` | config | `attack` | `late_attack_y_min=0.22`, `late_attack_y_max=0.70`, `late_attack_vx=-0.30`, `late_attack_vy=-0.05`, `late_attack_dx_min=0.00`, `late_attack_dx_max=0.36` |
| `trigger_fast_down` | config | `attack` | `late_attack_vx=-0.50`, `late_attack_vy=-0.30`, `late_attack_dx_max=0.34` |
| `attack_rally_shape_low_x52` | config | `attack` | `RALLY_SERVE_CONFIG` shape without the rally-serve detector, plus `low_ball_rescue_x_window=0.52` |
| `attack_rally_shape_low_x54` | config | `attack` | `RALLY_SERVE_CONFIG` shape without the rally-serve detector |

## Short Built-In Screen

Opponent: `builtin`. Seeds: `9000..9015`.

| Label | Kind | Mean | W-L-D | Steps |
| --- | --- | ---: | --- | ---: |
| `baseline_rnn` | reference | `0.1250` | `6-4-6` | `48000` |
| `rally_serve_reference` | reference | `0.3125` | `4-0-12` | `48000` |
| `post_contact_reference` | reference | `0.3125` | `4-0-12` | `48000` |
| `attack_reference` | reference | `-0.1250` | `2-4-10` | `48000` |
| `home_0.74` | scalar | `-0.1250` | `2-4-10` | `48000` |
| `home_0.90` | scalar | `-0.1250` | `2-4-10` | `48000` |
| `late_y_band_0.22_0.60` | config | `-0.4375` | `0-6-10` | `48000` |
| `late_y_band_0.30_0.72` | config | `-0.3750` | `2-8-6` | `48000` |
| `late_vx_m0.30` | scalar | `-0.1250` | `2-4-10` | `48000` |
| `late_vx_m0.50` | scalar | `-0.1250` | `2-4-10` | `48000` |
| `late_vy_m0.05` | scalar | `-0.1250` | `2-4-10` | `48000` |
| `late_vy_m0.25` | scalar | `-0.2500` | `1-5-10` | `48000` |
| `dx_tight_0.08_0.24` | config | `-0.3750` | `1-6-9` | `48000` |
| `dx_wide_0.00_0.36` | config | `-0.1250` | `2-4-10` | `48000` |
| `trigger_relaxed_mid` | config | `-0.5625` | `1-9-6` | `48000` |
| `trigger_fast_down` | config | `-0.1875` | `1-4-11` | `48000` |
| `attack_rally_shape_low_x52` | config | `0.3750` | `4-0-12` | `48000` |
| `attack_rally_shape_low_x54` | config | `0.3125` | `4-1-11` | `48000` |

Full-validation selection rule: advance the top five attack-family rows by
mean, then wins, then fewer losses, then label, plus `attack_reference`. That
yielded `attack_rally_shape_low_x52`, `attack_rally_shape_low_x54`,
`late_vx_m0.30`, `late_vx_m0.50`, and `late_vy_m0.05`.

## Full Built-In Validation

Opponent: `builtin`. Seeds: `9000..9049`.

| Label | Kind | Mean | W-L-D | Steps |
| --- | --- | ---: | --- | ---: |
| `baseline_rnn` | reference | `0.1200` | `18-12-20` | `150000` |
| `rally_serve_reference` | reference | `0.1400` | `13-8-29` | `150000` |
| `post_contact_reference` | reference | `0.1400` | `13-8-29` | `150000` |
| `attack_reference` | reference | `-0.3000` | `7-18-25` | `150000` |
| `late_vx_m0.30` | scalar | `-0.3400` | `7-19-24` | `150000` |
| `late_vx_m0.50` | scalar | `-0.2600` | `8-18-24` | `150000` |
| `late_vy_m0.05` | scalar | `-0.3400` | `7-19-24` | `150000` |
| `attack_rally_shape_low_x52` | config | `0.0600` | `10-10-30` | `150000` |
| `attack_rally_shape_low_x54` | config | `-0.0600` | `10-13-27` | `150000` |

No attack-family candidate beat the `baseline_rnn` full built-in mean of
`0.1200`. Therefore no fixed development opponent-pool check was run.

## Failure Analysis

Pure late-contact trigger scalar movement did not solve the built-in gap.
`late_vx_m0.50` was the best pure attack-rule scalar on full built-in seeds,
but it only improved `attack_reference` from `-0.3000` to `-0.2600`, still far
below `baseline_rnn` and the `rally-serve`/`post-contact` references. The
opposite velocity move, `late_vx_m0.30`, and the lighter downward-velocity gate,
`late_vy_m0.05`, both regressed to `-0.3400`.

Several narrow or broad contact windows were harmful even on the short screen.
The y-band and dx-tight rows created extra losses, and the broad
`trigger_relaxed_mid` combo fell to `-0.5625`, `1-9-6`, on the short subset.
`attack_home_x` movement was inert on the short screen, matching
`attack_reference` exactly for both tested values.

The only row that looked promising on the short screen was
`attack_rally_shape_low_x52`, but it did not survive the full built-in check.
It reached `0.0600`, `10-10-30`, which is a meaningful improvement over
`attack_reference` but remains `0.0600` below `baseline_rnn` and `0.0800` below
the `rally-serve` and `post-contact` references on the same development seeds.
The adjacent `attack_rally_shape_low_x54` row dropped to `-0.0600`, so the
shape is not robust enough to recommend without the rally-serve detector.

Because the built-in promotion gate was not met, any fixed-pool run would have
been extra development probing rather than required promotion evidence. Under
the stated rule, built-in-only evidence is not sufficient; here the best
candidate also failed to beat the built-in comparator.

## Promotion Recommendation

Do not promote any candidate from this worker run.

Best dev-only row: `attack_rally_shape_low_x52` as an `attack` config diagnostic
with `RALLY_SERVE_CONFIG`-shaped constants and
`low_ball_rescue_x_window=0.52`, but no rally-serve detector. Its full built-in
result was `0.0600`, `10-10-30`, `150000` steps. It does not beat
`baseline_rnn`, so no fixed-pool promotion check was triggered and no
promotion is recommended.

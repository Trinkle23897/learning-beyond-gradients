# Generation-4 Attack/Net-Pressure Scalar Search

Date: 2026-05-27

Worker: A

## Scope

Development-only scalar/config search around the existing `attack` /
`net-pressure` policy family. No policy source, tests, canonical ledger,
summary CSV, holdout artifact, or audit artifact was edited. Rows were run
through a transient no-ledger script at `/tmp/g4_attack_scalar_worker_a.py`
using the repo-local virtualenv.

No holdout or audit seeds were used. No promotion decision below relies only on
the built-in opponent score.

Command:

`/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/.venv/bin/python /tmp/g4_attack_scalar_worker_a.py`

## Seeds

Short-screen seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full fixed-pool seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

Full fixed-pool opponents:

`builtin, random, initial, improved-v0, improved-v2, improved-v3, improved-v4, improved-v5, improved-v6`

## Candidate Definitions

All `np_*` candidates used policy `net-pressure` with full
`RALLY_SERVE_CONFIG` plus only the listed delta. `scalar` means one numeric
field changed. `config` means multiple numeric fields changed. References are
controls, not search candidates.

| Candidate | Kind | Policy | Delta |
| --- | --- | --- | --- |
| `np_current` | reference | `net-pressure` | current `net-pressure` on `RALLY_SERVE_CONFIG` |
| `attack_current` | reference | `attack` | current `attack` default config |
| `rally_current` | reference | `rally-serve` | current `rally-serve` reference |
| `np_late_vx_m055` | scalar | `net-pressure` | `late_attack_vx=-0.55` |
| `np_late_vx_m035` | scalar | `net-pressure` | `late_attack_vx=-0.35` |
| `np_late_vy_m025` | scalar | `net-pressure` | `late_attack_vy=-0.25` |
| `np_late_ymax_075` | scalar | `net-pressure` | `late_attack_y_max=0.75` |
| `np_late_dx_wide` | config | `net-pressure` | `late_attack_dx_min=0.00`, `late_attack_dx_max=0.38` |
| `np_late_dx_tight` | config | `net-pressure` | `late_attack_dx_min=0.08`, `late_attack_dx_max=0.24` |
| `np_low_rescue_050` | scalar | `net-pressure` | `low_ball_rescue_x_window=0.50` |
| `np_contact_016` | scalar | `net-pressure` | `contact_x_window=0.16` |
| `np_guard_022` | scalar | `net-pressure` | `overcommit_guard_x=0.22` |
| `np_pressure_tempered` | config | `net-pressure` | `late_attack_vx=-0.55`, `late_attack_dx_min=0.08`, `late_attack_dx_max=0.24`, `low_ball_rescue_x_window=0.50` |

## Short Built-In Screen

Opponent: `builtin`. Seeds: `9000..9015`.

| Candidate | Kind | Mean | W-L-D | Steps |
| --- | --- | ---: | --- | ---: |
| `np_current` | reference | `-0.3750` | `2-6-8` | `48000` |
| `attack_current` | reference | `-0.1250` | `2-4-10` | `48000` |
| `rally_current` | reference | `0.3125` | `4-0-12` | `48000` |
| `np_late_vx_m055` | scalar | `-0.5625` | `2-9-5` | `48000` |
| `np_late_vx_m035` | scalar | `-0.5000` | `2-6-8` | `48000` |
| `np_late_vy_m025` | scalar | `-0.3750` | `2-6-8` | `48000` |
| `np_late_ymax_075` | scalar | `-0.3750` | `2-6-8` | `48000` |
| `np_late_dx_wide` | config | `-0.5000` | `1-6-9` | `48000` |
| `np_late_dx_tight` | config | `-0.6250` | `1-9-6` | `48000` |
| `np_low_rescue_050` | scalar | `-0.3750` | `2-6-8` | `48000` |
| `np_contact_016` | scalar | `-0.2500` | `2-7-7` | `48000` |
| `np_guard_022` | scalar | `-0.6875` | `4-9-3` | `48000` |
| `np_pressure_tempered` | config | `-0.6250` | `1-9-6` | `48000` |

Full-pool selection rule: top three scalar/config screen rows by mean, then
wins, then fewer losses, plus `np_current`, `rally_current`, and
`baseline_rnn`.

## Full Fixed-Pool Results

Score cells are `mean; W-L-D; steps`. Seeds: `9000..9049`.

| Opponent | `baseline_rnn` | `rally_current` | `np_current` | `np_late_ymax_075` | `np_low_rescue_050` | `np_contact_016` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `builtin` | `0.12; 18-12-20; 150000` | `0.14; 13-8-29; 150000` | `-0.22; 7-14-29; 150000` | `-0.24; 6-14-30; 150000` | `-0.18; 9-15-26; 150000` | `-0.52; 6-24-20; 150000` |
| `random` | `4.80; 50-0-0; 30603` | `4.74; 50-0-0; 38217` | `4.74; 50-0-0; 38647` | `4.74; 50-0-0; 38647` | `4.74; 50-0-0; 38594` | `4.80; 50-0-0; 37738` |
| `initial` | `4.76; 50-0-0; 34004` | `4.68; 50-0-0; 44634` | `4.72; 50-0-0; 45600` | `4.72; 50-0-0; 45600` | `4.72; 50-0-0; 45628` | `4.76; 50-0-0; 44580` |
| `improved-v0` | `4.82; 50-0-0; 32843` | `4.70; 50-0-0; 43242` | `4.72; 50-0-0; 43696` | `4.72; 50-0-0; 43696` | `4.72; 50-0-0; 43889` | `4.78; 50-0-0; 43386` |
| `improved-v2` | `4.80; 50-0-0; 54551` | `4.38; 49-1-0; 76391` | `4.56; 50-0-0; 76772` | `4.56; 50-0-0; 76772` | `4.58; 50-0-0; 73453` | `4.56; 50-0-0; 69374` |
| `improved-v3` | `3.84; 50-0-0; 118182` | `2.98; 48-0-2; 138122` | `2.86; 48-1-1; 139090` | `2.86; 48-1-1; 139090` | `2.94; 47-1-2; 138612` | `2.74; 47-1-2; 139929` |
| `improved-v4` | `3.26; 48-0-2; 132511` | `2.34; 44-0-6; 143814` | `2.38; 46-1-3; 143083` | `2.38; 46-1-3; 143083` | `2.52; 46-1-3; 143089` | `2.26; 44-2-4; 145670` |
| `improved-v5` | `2.10; 42-2-6; 145370` | `1.16; 32-7-11; 149716` | `1.34; 33-7-10; 149563` | `1.38; 33-7-10; 149077` | `1.48; 35-6-9; 149563` | `1.30; 35-8-7; 149562` |
| `improved-v6` | `2.18; 42-2-6; 144837` | `1.22; 32-7-11; 149716` | `1.36; 33-7-10; 149563` | `1.40; 33-7-10; 149077` | `1.50; 35-6-9; 149563` | `1.30; 35-8-7; 149562` |

Mean across the nine fixed-pool opponents:

| Candidate | Kind | Fixed-pool mean |
| --- | --- | ---: |
| `baseline_rnn` | reference | `3.4089` |
| `np_low_rescue_050` | scalar | `3.0022` |
| `np_late_ymax_075` | scalar | `2.9467` |
| `np_current` | reference | `2.9400` |
| `rally_current` | reference | `2.9267` |
| `np_contact_016` | scalar | `2.8867` |

## Failure Analysis

The short built-in screen was not reliable enough to select a candidate. The
screen leader, `np_contact_016`, improved the short built-in mean from
`-0.3750` to `-0.2500`, but collapsed on the full built-in row to `-0.52`,
`6-24-20`.

`np_low_rescue_050` is the best scalar/config row from this run. It raises the
fixed-pool mean over current `net-pressure` (`3.0022` vs `2.9400`) and improves
the hard archived tail, especially `improved-v5` and `improved-v6` (`1.48` and
`1.50`, both `35-6-9`). The tradeoff is still not acceptable: its built-in row
remains negative at `-0.18`, worse than `rally_current` (`0.14`) and
`baseline_rnn` (`0.12`), and it increases built-in losses versus
`np_current` (`15` losses vs `14`).

`np_late_ymax_075` is almost inert relative to current `net-pressure`; it only
adds small hard-tail mean gains while slightly worsening built-in mean. Broad
late-attack dx changes, stricter late-vx changes, and the tempered config all
regressed or failed to screen.

The broader pattern is unchanged from prior net-pressure evidence: front-court
pressure can convert some nearby heuristic archive cases, but it does not solve
the built-in regression and remains well behind the neural comparator across
the fixed development pool.

## Promotion Recommendation

Do not promote any scalar/config candidate from this Worker A run. Do not open
holdout or audit seeds.

Keep `np_low_rescue_050` only as development-only negative/mixed evidence. It
is the best scalar variant in this batch, but the built-in regression and
remaining fixed-pool gap to `baseline_rnn` make it unsuitable for promotion.

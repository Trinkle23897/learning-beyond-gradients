# Generation-4 Archived-Opponent Robustness Subagent

Worker: E
Date: 2026-05-27

## Scope

This is a development-only robustness check for current generation-4
SlimeVolley candidates against the fixed archived-opponent pool:

`builtin`, `random`, `initial`, `improved-v0`, `improved-v2`, `improved-v3`,
`improved-v4`, `improved-v5`, `improved-v6`.

Exact seeds used for every valid row: `9000, 9001, 9002, 9003, 9004, 9005,
9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017,
9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029,
9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041,
9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`
(`seed_start=9000`, `seed_stop_exclusive=9050`, `episodes=50`).

No holdout or audit seeds were used. I did not run seed starts `10000`,
`11000`, `13000`, or `14000`, and I did not run `slimevolley-final-eval`.

## Run Provenance

Existing rows reused from
`experiments/slimevolley/results/generation_4_summary.csv` only when they
matched `split=dev`, `seed_start=9000`, and `episodes=50`:

- `improved-tuned` g4 scalar-tuned-v2 fixed-pool rows.
- `attack` fixed-pool rows.
- `rally-serve` fixed-pool rows.
- `baseline-rnn` versus `builtin`.

Fresh no-ledger reproductions used the project virtualenv and wrote no ledger or
summary rows:

```bash
.venv/bin/python -m hl_benchmark.custom_envs.slimevolley.evaluate \
  --policy attack --opponent <opponent> --split dev \
  --seed-start 9000 --episodes 50 \
  --config-json '{"x_margin":0.04,"contact_x_window":0.14,"high_arc_horizon":0.95,"overcommit_guard_x":0.20,"low_ball_rescue_x_window":0.48,"low_ball_rescue_horizon":0.06,"grounded_low_receive_airborne_margin":0.16,"late_attack_vx":-0.45}' \
  --no-ledger
```

The command above was run for all nine fixed-pool opponents. It reproduced the
documented scalar-top built-in row exactly: mean `-0.02`, W-L-D `9/12/29`,
`150000` steps.

```bash
.venv/bin/python -m hl_benchmark.custom_envs.slimevolley.evaluate \
  --policy baseline-rnn --opponent <opponent> --split dev \
  --seed-start 9000 --episodes 50 --no-ledger
```

The baseline command above was run for `random`, `initial`, `improved-v0`,
`improved-v2`, `improved-v3`, `improved-v4`, `improved-v5`, and `improved-v6`.
The `baseline-rnn` versus `builtin` row came from the existing exact summary row.

One initial system-Python no-ledger attempt for scalar-top versus `builtin`
failed before evaluation because that interpreter lacked optional
SlimeVolley/Gym dependencies (`ModuleNotFoundError: No module named 'gym'`);
it produced no score, no episodes, and no environment steps. The valid
reproduction used `heuristic_learning/.venv/bin/python`.

## Candidate Definitions

| Candidate | Label | Definition |
| --- | --- | --- |
| `improved-tuned` | scalar/config | Maintained structural heuristic with g4 scalar-tuned-v2 fields: `x_margin=0.04`, `contact_x_window=0.14`, `high_arc_horizon=0.85`, `overcommit_guard_x=0.18`, `low_ball_rescue_x_window=0.72`, `low_ball_rescue_horizon=0.06`, `grounded_low_receive_airborne_margin=0.12`. |
| `attack` | structural plus scalar/config base | `improved-tuned` plus late-contact attack: if `ball_x > 0.05`, `0.28 <= ball_y <= 0.65`, `ball_vx < -0.35`, `ball_vy < -0.10`, and `0.04 <= agent_x - ball_x <= 0.28`, return `101`. |
| `attack-scalar-top` | scalar/config over structural `attack` | No new detector or branch. Uses `attack` with `high_arc_horizon=0.95`, `overcommit_guard_x=0.20`, `grounded_low_receive_airborne_margin=0.16`, `late_attack_vx=-0.45`, `low_ball_rescue_x_window=0.48`, plus the g4 tuned base fields listed above. |
| `rally-serve` | structural plus scalar/config | `attack` family plus point-reset serve detector: if `abs(ball_x) <= 0.28`, `ball_y >= 1.45`, `abs(ball_vx) <= 0.50`, and the last detection was more than `12` policy steps ago, run `8` steps of forward+jump `101`. Uses `high_arc_horizon=0.95`, `overcommit_guard_x=0.18`, `low_ball_rescue_x_window=0.54`, `grounded_low_receive_airborne_margin=0.16`, `landing_horizon=0.38`, `late_attack_y_min=0.24`, `late_attack_vx=-0.45`, `late_attack_vy=-0.35`. |
| `baseline-rnn` | neural comparator | Shipped `slimevolleygym` RNN baseline wrapper. Included for comparison only; not a transparent heuristic candidate. |

## `improved-tuned` Results

Source: existing exact generation-4 summary rows.

| Opponent | Mean | W-L-D | Steps |
| --- | ---: | --- | ---: |
| `builtin` | `-0.44` | `6/23/21` | `150000` |
| `random` | `4.66` | `50/0/0` | `39838` |
| `initial` | `4.56` | `50/0/0` | `45426` |
| `improved-v0` | `4.60` | `50/0/0` | `44549` |
| `improved-v2` | `4.38` | `49/1/0` | `71170` |
| `improved-v3` | `2.38` | `42/1/7` | `142137` |
| `improved-v4` | `2.08` | `40/1/9` | `144565` |
| `improved-v5` | `1.22` | `31/5/14` | `147554` |
| `improved-v6` | `1.20` | `31/5/14` | `147554` |

## `attack` Results

Source: existing exact generation-4 summary rows.

| Opponent | Mean | W-L-D | Steps |
| --- | ---: | --- | ---: |
| `builtin` | `-0.30` | `7/18/25` | `150000` |
| `random` | `4.80` | `50/0/0` | `37905` |
| `initial` | `4.70` | `50/0/0` | `44007` |
| `improved-v0` | `4.74` | `50/0/0` | `44346` |
| `improved-v2` | `4.36` | `49/1/0` | `74158` |
| `improved-v3` | `2.62` | `46/1/3` | `138953` |
| `improved-v4` | `2.16` | `40/3/7` | `143423` |
| `improved-v5` | `1.08` | `30/8/12` | `148079` |
| `improved-v6` | `1.06` | `30/8/12` | `148079` |

## `attack-scalar-top` Results

Source: fresh no-ledger reproduction with the config recorded above.

| Opponent | Mean | W-L-D | Steps |
| --- | ---: | --- | ---: |
| `builtin` | `-0.02` | `9/12/29` | `150000` |
| `random` | `4.76` | `50/0/0` | `37773` |
| `initial` | `4.72` | `50/0/0` | `44727` |
| `improved-v0` | `4.74` | `50/0/0` | `43345` |
| `improved-v2` | `4.56` | `50/0/0` | `70125` |
| `improved-v3` | `3.00` | `48/0/2` | `140591` |
| `improved-v4` | `2.42` | `44/0/6` | `143390` |
| `improved-v5` | `1.14` | `31/7/12` | `148311` |
| `improved-v6` | `1.18` | `31/7/12` | `148311` |

## `rally-serve` Results

Source: existing exact generation-4 summary rows.

| Opponent | Mean | W-L-D | Steps |
| --- | ---: | --- | ---: |
| `builtin` | `0.14` | `13/8/29` | `150000` |
| `random` | `4.74` | `50/0/0` | `38217` |
| `initial` | `4.68` | `50/0/0` | `44634` |
| `improved-v0` | `4.70` | `50/0/0` | `43242` |
| `improved-v2` | `4.38` | `49/1/0` | `76391` |
| `improved-v3` | `2.98` | `48/0/2` | `138122` |
| `improved-v4` | `2.34` | `44/0/6` | `143814` |
| `improved-v5` | `1.16` | `32/7/11` | `149716` |
| `improved-v6` | `1.22` | `32/7/11` | `149716` |

## `baseline-rnn` Comparator Results

Source: existing exact summary row for `builtin`; fresh no-ledger reproduction
for the other eight opponents.

| Opponent | Mean | W-L-D | Steps |
| --- | ---: | --- | ---: |
| `builtin` | `0.12` | `18/12/20` | `150000` |
| `random` | `4.80` | `50/0/0` | `30603` |
| `initial` | `4.76` | `50/0/0` | `34004` |
| `improved-v0` | `4.82` | `50/0/0` | `32843` |
| `improved-v2` | `4.80` | `50/0/0` | `54551` |
| `improved-v3` | `3.84` | `50/0/0` | `118182` |
| `improved-v4` | `3.26` | `48/0/2` | `132511` |
| `improved-v5` | `2.10` | `42/2/6` | `145370` |
| `improved-v6` | `2.18` | `42/2/6` | `144837` |

## Failure Analysis

`improved-tuned` is a useful scalar/config baseline but fails the built-in
neural-comparator gate: mean `-0.44` versus `baseline-rnn` mean `0.12`. It is
still a relevant archived-opponent yardstick because it remains strongest among
the non-rally maintained heuristics on `improved-v5` (`1.22`) and close on
`improved-v6` (`1.20`).

`attack` is not robust enough for promotion. It improves the built-in row over
`improved-tuned` by `+0.14`, but remains far below `baseline-rnn` by `0.42`.
It also regresses nearest archived opponents versus `improved-tuned`:
`improved-v5` drops `1.22 -> 1.08` and `improved-v6` drops `1.20 -> 1.06`.
The late-contact structural rule helps mid archives but adds exploitability
against the closest archived heuristics.

`attack-scalar-top` is the strongest scalar/config-only attack variant checked
here. It raises built-in to `-0.02` and improves most archived rows, including
`improved-v2` (`4.56`), `improved-v3` (`3.00`), and `improved-v4` (`2.42`).
However, it is still below `baseline-rnn` on built-in by `0.14` and still
regresses `improved-v5` and `improved-v6` versus `improved-tuned`
(`1.14` versus `1.22`, `1.18` versus `1.20`). Because this is scalar/config
tuning over an existing structural rule, not a new transparent mechanism, it
does not justify promotion.

`rally-serve` is the only heuristic candidate in this check that beats the
built-in `baseline-rnn` mean on generation-4 development seeds, but only by
`+0.02` (`0.14` versus `0.12`). Its W-L-D is less convincing than the mean:
`13/8/29` versus the RNN's `18/12/20`, so it wins fewer matches and relies more
on draws. Against archived heuristics it is mostly acceptable, but it has a
recorded `improved-v5` regression versus `improved-tuned` (`1.16` versus
`1.22`). It also trails the scalar-top attack config on several archived rows
(`improved-v2`, `improved-v3`, `improved-v4`) while preserving the best built-in
score.

The `baseline-rnn` comparator remains stronger across the harder archived pool:
`improved-v3` through `improved-v6` are all materially ahead of the heuristic
candidates. This does not make it a transparent candidate, but it keeps the
remaining heuristic gap visible and argues against broad final claims from the
small `rally-serve` built-in development edge.

## Promotion Recommendation

Do not promote `improved-tuned`, `attack`, or `attack-scalar-top`.

`rally-serve` is the only candidate that survives this development robustness
check as a frozen generation-4 heuristic candidate, with the explicit caveat
that it regresses `improved-v5` versus the scalar baseline and only narrowly
beats `baseline-rnn` on built-in development mean. This is development evidence
only. It does not justify further tuning on sealed seeds and does not prove
final generalization.

Other parallel-worker variants (`serve_vx_0.65`, `combo_steps6_vx65`,
`combo_steps10_vx65`, grounded-low stacked variants, and rear-wall stacked
variants) either tied current `rally-serve` on built-in development score,
added losses, or were neutral/harmful. They were not included as promotion
candidates here; if reconsidered later, they need their own fixed-pool
development robustness check before any holdout discussion.

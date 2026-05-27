# Generation-4 Parallel3 Archived-Opponent Robustness

Worker: 5
Date: 2026-05-27

## Scope

This is a development-only robustness check on generation-4 development seeds.
It uses only seeds `9000..9049`, does not use holdout or audit seeds, does not
run `slimevolley-final-eval`, and does not append to the canonical ledger.

Sources:

- Existing generation-4 dev rows in `experiments/slimevolley/results/generation_4_summary.csv`
  for `rally-serve`.
- Existing no-ledger post-contact probe rows in
  `experiments/slimevolley/results/generation_4_post_contact_gate_probe.json`
  for `baseline_rnn`, `rally_reference`, and `pc_front_conversion`.
- Fresh Worker 5 no-ledger direct harness run for `net-pressure`, written only
  to temporary file `/tmp/slimevolley_g4_net_pressure_noledger_20260527.json`.

No holdout seeds, audit seeds, or final-evaluation harness calls were used.

## Exact Seeds

All full-pool rows used exactly these 50 development seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

## Candidate Definitions

| Candidate | Label | Definition |
| --- | --- | --- |
| `rally-serve` | structural plus scalar/config | Generation-4 candidate that keeps the late-contact attack rule and adds a point-reset serve detector: when `abs(ball_x) <= 0.28`, `ball_y >= 1.45`, `abs(ball_vx) <= 0.50`, and cooldown permits, run an 8-step forward+jump `101` serve macro. Uses the generation-4 `RALLY_SERVE_CONFIG` scalar settings. |
| `post-contact` / `pc_front_conversion` | structural/history on scalar/config baseline | Registered development-only post-contact candidate. It wraps `rally-serve` and, after a recent contact-like velocity flip, forces forward+jump `101` in a low front-court conversion window. The full-pool probe row name is `pc_front_conversion`. |
| `net-pressure` | structural on scalar/config baseline | Current available structural probe extending `rally-serve`; if a controllable front-court ball is moving toward the opponent, drive forward+jump `101` from behind the contact point. Worker 5 evaluated it no-ledger on generation-4 dev seeds for this note. |
| `baseline-rnn` | neural comparator, not a promotable heuristic candidate | Packaged `slimevolleygym.slimevolley.BaselinePolicy` wrapper with 120 parameters. |

## Opponent Definitions

| Opponent | Definition |
| --- | --- |
| `builtin` | Environment default built-in 120-parameter RNN opponent, by omitting `otherAction`. |
| `random` | Seeded random `MultiBinary(3)` opponent. |
| `initial` | Frozen copy of the initial handwritten heuristic. |
| `improved-v0` | Frozen first structural archive before low-ball rescue. |
| `improved-v2` | Frozen structural archive before grounded-low-receive. |
| `improved-v3` | Frozen structural archive before rear-wall recovery. |
| `improved-v4` | Frozen structural archive before front-hit jump suppression. |
| `improved-v5` | Frozen structural archive before rear-wall low-jump rescue. |
| `improved-v6` | Frozen structural archive before front-net low-scoop rescue. |

## Fixed Development Pool Matrix

Score cells are `mean; W-L-D; environment steps`.

| Opponent | `baseline-rnn` | `rally-serve` | `post-contact` | `net-pressure` |
| --- | ---: | ---: | ---: | ---: |
| `builtin` | `0.12; 18-12-20; 150000` | `0.14; 13-8-29; 150000` | `0.14; 13-8-29; 150000` | `-0.22; 7-14-29; 150000` |
| `random` | `4.80; 50-0-0; 30603` | `4.74; 50-0-0; 38217` | `4.74; 50-0-0; 38217` | `4.74; 50-0-0; 38647` |
| `initial` | `4.76; 50-0-0; 34004` | `4.68; 50-0-0; 44634` | `4.68; 50-0-0; 44634` | `4.72; 50-0-0; 45600` |
| `improved-v0` | `4.82; 50-0-0; 32843` | `4.70; 50-0-0; 43242` | `4.70; 50-0-0; 43242` | `4.72; 50-0-0; 43696` |
| `improved-v2` | `4.80; 50-0-0; 54551` | `4.38; 49-1-0; 76391` | `4.38; 49-1-0; 76391` | `4.56; 50-0-0; 76772` |
| `improved-v3` | `3.84; 50-0-0; 118182` | `2.98; 48-0-2; 138122` | `3.04; 48-0-2; 137816` | `2.86; 48-1-1; 139090` |
| `improved-v4` | `3.26; 48-0-2; 132511` | `2.34; 44-0-6; 143814` | `2.40; 44-0-6; 143709` | `2.38; 46-1-3; 143083` |
| `improved-v5` | `2.10; 42-2-6; 145370` | `1.16; 32-7-11; 149716` | `1.22; 32-7-11; 149402` | `1.34; 33-7-10; 149563` |
| `improved-v6` | `2.18; 42-2-6; 144837` | `1.22; 32-7-11; 149716` | `1.28; 32-7-11; 149402` | `1.36; 33-7-10; 149563` |

## Robustness Failure Analysis

The built-in row alone is misleading. `rally-serve` and `post-contact` edge the
RNN comparator by only `+0.02` mean on `builtin`, but both have fewer wins and
more draws than `baseline-rnn`: `13-8-29` versus `18-12-20`. That is not a
strong conversion profile.

The archived-opponent pool rejects a built-in-only promotion. Against the nine
fixed opponents, `rally-serve` is better than `baseline-rnn` on only `builtin`
and worse on the other eight. `post-contact` has the same built-in result and
small hard-tail improvements over `rally-serve`, but it is still worse than
`baseline-rnn` on every archived opponent.

`net-pressure` improves some heuristic-vs-heuristic archive rows, especially
`improved-v5` and `improved-v6`, but the tradeoff is not acceptable. It regresses
the built-in row to `-0.22`, loses to `baseline-rnn` on every fixed-pool
opponent, and also falls below `post-contact` on `improved-v3` and
`improved-v4`. Its hard-tail gain does not compensate for the primary built-in
regression and broad neural-comparator gap.

The common failure shape is that the transparent candidates can add narrow
point-differential gains against nearby heuristic archives, but they do not
match the RNN's robust win conversion across the archived pool. Promotion from
built-in score alone would overfit to one opponent.

## Promotion Recommendation

Do not promote any checked candidate from this robustness pass.

`post-contact` is the best archived-tail heuristic among the generation-4
candidate rows already present, and `net-pressure` improves the last two archive
means further, but neither clears the robustness bar because both remain behind
`baseline-rnn` across the archived pool. Keep these as development-only
diagnostics. Do not open holdout or audit seeds for these candidates based on
this evidence.

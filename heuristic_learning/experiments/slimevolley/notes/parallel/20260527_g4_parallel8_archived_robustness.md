# Generation-4 Parallel8 Archived-Opponent Robustness

Worker: E
Date: 2026-05-27
Kind: `archived-opponent robustness check`

## Scope

This is a generation-4 development-only fixed-pool robustness note. It uses
only development seeds `9000..9049`. It does not use holdout seeds
`10000..10049` or audit seeds `11000..11049`.

The local SlimeVolley runtime is unavailable in this shell:
`PYTHONPATH=. python3 -m hl_benchmark.custom_envs.slimevolley.doctor` reports
`ModuleNotFoundError: No module named 'gym'`, with `gym` and `slimevolleygym`
not installed. A one-episode no-ledger smoke on seed `9000` therefore returned
`pass_fail=fail` before producing any episode metric. This note does not use
that failed smoke as score evidence.

Source rows are existing development-only fixed-pool artifacts:

- `results/generation_4_summary.csv`, filtered to `split=dev`,
  `seed_start=9000`, `seed_stop_exclusive=9050`, and `episodes=50`, for
  `attack` and `rally-serve`.
- `results/generation_4_post_contact_gate_probe.json` for full-pool
  `baseline-rnn`, `rally-serve`, and `post-contact` rows.
- `results/generation_4_net_pressure_noledger_probe.json` for full-pool
  `net-pressure` rows.
- `notes/parallel/20260527_g4_parallel6_attack_scalar.md` for full-pool
  `rally-serve-low-x52` rows.

## Exact Seeds

All score rows below use exactly these 50 generation-4 development seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012,
9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025,
9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038,
9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

No short-screen score is used for the promotion recommendation.

## Candidates

| Candidate | Role | Definition |
| --- | --- | --- |
| `baseline-rnn` | neural comparator | Packaged `slimevolleygym` 120-parameter RNN wrapper. It is not a promotable heuristic. |
| `rally-serve` | registered heuristic reference | Generation-4 late-contact attack plus point-reset rally-serve detector and rally scalar/config baseline. |
| `rally-serve-low-x52` | scalar/config reference | `rally-serve` with `low_ball_rescue_x_window=0.52`; recorded as `low_x_0.52` in the parallel6 scalar search. |
| `post-contact` | registered structural/history reference | `rally-serve` plus two-frame near-net post-contact front conversion. Source row name: `pc_front_conversion`. |
| `net-pressure` | registered structural pressure probe | Front-court pressure rule layered on `rally-serve`; available as a registered policy but recorded as a probe, not a promotion. |
| `attack` | registered structural reference | Generation-4 late-contact attack candidate before the rally-serve detector was added. |

## Fixed Development Pool Matrix

Cells are `score mean; W-L-D; environment steps`.

| Opponent | `baseline-rnn` | `rally-serve` | `rally-serve-low-x52` | `post-contact` | `net-pressure` | `attack` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `builtin` | `0.12; 18-12-20; 150000` | `0.14; 13-8-29; 150000` | `0.18; 14-8-28; 150000` | `0.14; 13-8-29; 150000` | `-0.22; 7-14-29; 150000` | `-0.30; 7-18-25; 150000` |
| `random` | `4.80; 50-0-0; 30603` | `4.74; 50-0-0; 38217` | `4.74; 50-0-0; 38217` | `4.74; 50-0-0; 38217` | `4.74; 50-0-0; 38647` | `4.80; 50-0-0; 37905` |
| `initial` | `4.76; 50-0-0; 34004` | `4.68; 50-0-0; 44634` | `4.68; 50-0-0; 44635` | `4.68; 50-0-0; 44634` | `4.72; 50-0-0; 45600` | `4.70; 50-0-0; 44007` |
| `improved-v0` | `4.82; 50-0-0; 32843` | `4.70; 50-0-0; 43242` | `4.70; 50-0-0; 43455` | `4.70; 50-0-0; 43242` | `4.72; 50-0-0; 43696` | `4.74; 50-0-0; 44346` |
| `improved-v2` | `4.80; 50-0-0; 54551` | `4.38; 49-1-0; 76391` | `4.38; 49-1-0; 75222` | `4.38; 49-1-0; 76391` | `4.56; 50-0-0; 76772` | `4.36; 49-1-0; 74158` |
| `improved-v3` | `3.84; 50-0-0; 118182` | `2.98; 48-0-2; 138122` | `3.06; 49-0-1; 136376` | `3.04; 48-0-2; 137816` | `2.86; 48-1-1; 139090` | `2.62; 46-1-3; 138953` |
| `improved-v4` | `3.26; 48-0-2; 132511` | `2.34; 44-0-6; 143814` | `2.48; 45-0-5; 143646` | `2.40; 44-0-6; 143709` | `2.38; 46-1-3; 143083` | `2.16; 40-3-7; 143423` |
| `improved-v5` | `2.10; 42-2-6; 145370` | `1.16; 32-7-11; 149716` | `1.20; 32-7-11; 149716` | `1.22; 32-7-11; 149402` | `1.34; 33-7-10; 149563` | `1.08; 30-8-12; 148079` |
| `improved-v6` | `2.18; 42-2-6; 144837` | `1.22; 32-7-11; 149716` | `1.26; 32-7-11; 149716` | `1.28; 32-7-11; 149402` | `1.36; 33-7-10; 149563` | `1.06; 30-8-12; 148079` |

## Robustness Labels

| Candidate | Robustness label | Basis |
| --- | --- | --- |
| `baseline-rnn` | comparator only | Strongest fixed-pool row on every archived heuristic opponent; not a transparent heuristic candidate. |
| `rally-serve-low-x52` | best scalar reference, not promotable | Best built-in mean in this set and no easy-pool collapse, but still behind `baseline-rnn` on every archived heuristic opponent. |
| `post-contact` | best structural reference, not promotable | Preserves `rally-serve` built-in and nudges the hard tail, but keeps a large neural-comparator gap. |
| `rally-serve` | stable reference, not promotable | Built-in mean narrowly exceeds `baseline-rnn`, but W-L-D is weaker and hard archived rows trail the comparator. |
| `net-pressure` | mixed/rejected | Improves `improved-v2` and the hardest tail versus `rally-serve`, but regresses built-in to `-0.22` and still trails `baseline-rnn`. |
| `attack` | rejected/exploitable | Regresses built-in and is worse than the stronger heuristic references on hard archived opponents. |

## Failure Analysis

Built-in score remains a weak promotion signal. `rally-serve-low-x52` has the
best built-in mean at `0.18`, and `rally-serve`/`post-contact` both edge
`baseline-rnn` on built-in mean at `0.14` versus `0.12`. The W-L-D profile is
less convincing: `baseline-rnn` is `18-12-20`, while `rally-serve` and
`post-contact` are `13-8-29`; the heuristic rows rely more on draws and point
differential than on win conversion.

The hard archived opponents expose the main regression risk. Against
`improved-v3` through `improved-v6`, `baseline-rnn` posts means
`3.84, 3.26, 2.10, 2.18`. The strongest transparent rows are still materially
lower: `rally-serve-low-x52` reaches `3.06, 2.48, 1.20, 1.26`, and
`post-contact` reaches `3.04, 2.40, 1.22, 1.28`.

`post-contact` is the cleanest structural follow-up to `rally-serve`: it keeps
the same built-in score and improves `improved-v3` through `improved-v6` by
`+0.06` mean versus `rally-serve`. That improvement is too small to change the
promotion decision because it leaves hard-tail gaps of `0.80`, `0.86`, `0.88`,
and `0.90` mean versus `baseline-rnn`.

`net-pressure` is useful as a failure case for archived-opponent balancing. It
helps `improved-v2`, `improved-v5`, and `improved-v6` relative to
`rally-serve`, but it damages the built-in row from `0.14` to `-0.22` and adds
losses on `improved-v3` and `improved-v4`. It should not replace
`post-contact` or `rally-serve-low-x52` as the generation-4 fixed-pool
reference.

`attack` is no longer competitive with the current references. Its built-in
row is negative and it has the weakest hard-tail W-L-D profile among the
registered candidates checked here.

## Promotion Recommendation

Do not promote any candidate from this archived-opponent robustness pass.

Keep `rally-serve-low-x52` as the strongest scalar/config development
reference and `post-contact` as the strongest structural development
reference. Neither deserves fixed-pool promotion over the comparator because
both remain behind `baseline-rnn` on every archived heuristic opponent in the
fixed pool.

Reject `net-pressure` and `attack` for generation-4 fixed-pool promotion. Do
not open or use generation-4 holdout or audit seeds for any candidate based on
this evidence.

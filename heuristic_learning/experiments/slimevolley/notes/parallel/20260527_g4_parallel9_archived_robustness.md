# Generation-4 Parallel9 Archived-Opponent Robustness

Worker: E
Date: 2026-05-27
Kind: `archived-opponent robustness check`

## Scope

This is a generation-4 development-only fixed-pool robustness note for the
current promising `rally-serve` family context. It uses only development seeds
`9000..9049`. It does not use holdout seeds `10000..10049` or audit seeds
`11000..11049`.

No maintained source, policy, evaluator, ledger, or summary artifact was
edited. The numbers below are synthesized from existing development-only
fixed-pool artifacts so the family can be judged before any holdout discussion.

Source artifacts used:

- `results/generation_4_summary.csv` for `rally-serve` and `attack` rows.
- `notes/parallel/20260527_g4_parallel6_attack_scalar.md` for
  `rally-serve-low-x52` / `low_x_0.52`.
- `notes/parallel/g4_archived_opponent_robustness_post_contact_worker_e.md`
  for `post-contact`.
- `results/generation_4_net_pressure_noledger_probe.json` for `net-pressure`.
- `notes/parallel/20260527_g4_post_contact_gate_probe.md` and
  `notes/parallel/20260527_g4_parallel8_archived_robustness.md` for the
  existing dev-only fixed-pool comparator rows needed to keep the matrix
  aligned.

## Exact Seeds

All rows below use exactly these 50 generation-4 development seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012,
9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025,
9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038,
9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

No short smoke or short screen is used for the recommendation.

## Candidate Definitions

| Candidate | Kind | Definition |
| --- | --- | --- |
| `baseline-rnn` | neural comparator | Packaged `slimevolleygym` 120-parameter RNN wrapper. Comparator only; not a promotable transparent heuristic. |
| `rally-serve` | registered heuristic reference | Generation-4 late-contact attack plus point-reset rally-serve detector and rally scalar/config baseline. |
| `rally-serve-low-x52` | scalar/config reference | `rally-serve` with `low_ball_rescue_x_window=0.52`; recorded as `low_x_0.52` in the parallel6 scalar search. |
| `post-contact` | structural/history reference | `rally-serve` plus a two-frame near-net `post_contact_front_conversion` after recent contact-like velocity flips. |
| `net-pressure` | structural pressure probe | Front-court pressure rule layered on `rally-serve`; preserved as a development no-ledger probe, not a promoted policy. |
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
| `baseline-rnn` | comparator only | Strongest fixed-pool row on every archived heuristic opponent checked here; included only as the neural comparator. |
| `rally-serve-low-x52` | best scalar reference, not promotable | Best built-in mean in this family and no easy-pool collapse, but still behind `baseline-rnn` across the hard archived tail. |
| `post-contact` | best structural reference, not promotable | Preserves the `rally-serve` built-in row and slightly improves `improved-v3..v6`, but does not close the comparator gap. |
| `rally-serve` | stable reference, not promotable | Useful family baseline and slightly better than `baseline-rnn` on built-in mean, but materially weaker on hard archived opponents. |
| `net-pressure` | mixed/rejected | Helps some archived rows but regresses built-in to `-0.22` and still trails `baseline-rnn`. |
| `attack` | rejected/exploitable | Negative built-in row and weakest hard-tail profile among the references checked here. |

## Failure Analysis

Built-in improvement alone is not enough to justify a promotion path. The best
built-in row in this family is `rally-serve-low-x52` at `0.18`, but the hard
archived tail still trails `baseline-rnn` by `0.78`, `0.78`, `0.90`, and
`0.92` on `improved-v3`, `improved-v4`, `improved-v5`, and `improved-v6`.

`post-contact` is the cleanest structural follow-up. It preserves the
`rally-serve` built-in row and nudges the hard tail by `+0.06` mean on each of
`improved-v3..v6` versus `rally-serve`. That is still far short of the neural
comparator: the remaining `baseline-rnn` gaps are `0.80`, `0.86`, `0.88`, and
`0.90`.

`net-pressure` is useful as negative robustness evidence. It slightly improves
`improved-v2`, `improved-v5`, and `improved-v6` versus `rally-serve`, but it
collapses the built-in row from `0.14` to `-0.22`. That trade is not
acceptable for this family.

`attack` is dominated by the later `rally-serve` family references. Its
built-in row is negative, and its `improved-v3..v6` rows are worse than
`rally-serve-low-x52` and `post-contact`.

If another worker reports a candidate that beats `baseline-rnn` on built-in
development seeds, it still needs this same fixed-pool archived-opponent check
before any holdout discussion. The generation-4 development evidence here shows
that built-in wins can coexist with hard-tail robustness gaps.

## Promotion Recommendation

Do not promote any candidate from this archived-opponent robustness pass.

Keep `rally-serve-low-x52` as the best scalar/config development reference and
`post-contact` as the best structural development reference for the current
family context. Reject `net-pressure` and `attack` for generation-4 fixed-pool
promotion.

Do not open or use generation-4 holdout or audit seeds for this family based
on the evidence above.

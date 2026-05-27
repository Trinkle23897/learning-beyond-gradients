# Generation-4 Parallel7 Archived-Opponent Robustness Check

Worker: E
Date: 2026-05-27
Kind: `archived-opponent robustness check`

## Scope

This is a generation-4 development-only fixed-pool robustness note. It uses
only dev seeds `9000..9049`, does not use holdout seeds `10000..10049`, and
does not use audit seeds `11000..11049`.

All rows in this note are read from existing append-only artifacts. No source,
policy, eval, summary, ledger, or report code was edited, and no new reruns
were required for this note.

Source artifacts used:

- `results/generation_4_summary.csv` for `baseline-rnn`, `rally-serve`, and
  `attack`.
- `notes/parallel/20260527_g4_parallel6_attack_scalar.md` for
  `rally-serve-low-x52` / `low_x_0.52`.
- `notes/parallel/g4_archived_opponent_robustness_post_contact_worker_e.md`
  for `post-contact`.

## Exact Seeds

All full-pool rows use exactly these 50 generation-4 development seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011,
9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023,
9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035,
9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047,
9048, 9049`

## Candidate Definitions

| Candidate | Kind | Definition | Source freshness |
| --- | --- | --- | --- |
| `baseline-rnn` | neural comparator | Packaged `slimevolleygym` baseline RNN wrapper. Included as the fixed-pool comparator only; not a promotable heuristic. | read existing |
| `rally-serve` | structural plus scalar/config | Generation-4 `rally-serve` candidate: late-contact attack plus point-reset serve detector and the rally scalar/config fields used in the generation-4 dev rows. | read existing |
| `rally-serve-low-x52` | scalar/config | `rally-serve` with `low_ball_rescue_x_window=0.52`. This is the `low_x_0.52` row from the parallel6 scalar/config search. | read existing |
| `post-contact` | structural/history | `rally-serve` plus `post_contact_front_conversion` after a recent contact-like velocity flip. The source row name in the probe artifact is `pc_front_conversion`. | read existing |
| `attack` | structural plus scalar/config | Generation-4 `attack` candidate: `improved-tuned` plus a narrow late-contact forward+jump rule for low descending balls moving toward the opponent. | read existing |

## Fixed Development Pool Matrix

Cells are `mean; W-L-D; environment steps`.

| Opponent | `baseline-rnn` | `rally-serve` | `rally-serve-low-x52` | `post-contact` | `attack` |
| --- | ---: | ---: | ---: | ---: | ---: |
| `builtin` | `0.12; 18-12-20; 150000` | `0.14; 13-8-29; 150000` | `0.18; 14-8-28; 150000` | `0.14; 13-8-29; 150000` | `-0.30; 7-18-25; 150000` |
| `random` | `4.80; 50-0-0; 30603` | `4.74; 50-0-0; 38217` | `4.74; 50-0-0; 38217` | `4.74; 50-0-0; 38217` | `4.80; 50-0-0; 37905` |
| `initial` | `4.76; 50-0-0; 34004` | `4.68; 50-0-0; 44634` | `4.68; 50-0-0; 44635` | `4.68; 50-0-0; 44634` | `4.70; 50-0-0; 44007` |
| `improved-v0` | `4.82; 50-0-0; 32843` | `4.70; 50-0-0; 43242` | `4.70; 50-0-0; 43455` | `4.70; 50-0-0; 43242` | `4.74; 50-0-0; 44346` |
| `improved-v2` | `4.80; 50-0-0; 54551` | `4.38; 49-1-0; 76391` | `4.38; 49-1-0; 75222` | `4.38; 49-1-0; 76391` | `4.36; 49-1-0; 74158` |
| `improved-v3` | `3.84; 50-0-0; 118182` | `2.98; 48-0-2; 138122` | `3.06; 49-0-1; 136376` | `3.04; 48-0-2; 137816` | `2.62; 46-1-3; 138953` |
| `improved-v4` | `3.26; 48-0-2; 132511` | `2.34; 44-0-6; 143814` | `2.48; 45-0-5; 143646` | `2.40; 44-0-6; 143709` | `2.16; 40-3-7; 143423` |
| `improved-v5` | `2.10; 42-2-6; 145370` | `1.16; 32-7-11; 149716` | `1.20; 32-7-11; 149716` | `1.22; 32-7-11; 149402` | `1.08; 30-8-12; 148079` |
| `improved-v6` | `2.18; 42-2-6; 144837` | `1.22; 32-7-11; 149716` | `1.26; 32-7-11; 149716` | `1.28; 32-7-11; 149402` | `1.06; 30-8-12; 148079` |

## Failure Analysis

`rally-serve-low-x52` is the strongest candidate in this set by built-in
development mean. It improves `rally-serve` from `0.14` to `0.18` and does not
harm the easy fixed-pool rows, but it still trails `baseline-rnn` on every
archived heuristic opponent in the fixed pool. The hard-tail gaps against
`baseline-rnn` are still material: `-0.78` on `improved-v3`, `-0.78` on
`improved-v4`, `-0.90` on `improved-v5`, and `-0.92` on `improved-v6`.

`post-contact` is the best structural follow-up to `rally-serve`. It preserves
the built-in row, and it improves the hardest heuristic tail slightly versus
`rally-serve` on `improved-v3` through `improved-v6`. That is still not enough
to close the comparator gap. Against `baseline-rnn`, it remains behind by
`-0.80` on `improved-v3`, `-0.86` on `improved-v4`, `-0.88` on `improved-v5`,
and `-0.90` on `improved-v6`.

`attack` is a negative control for this pass. Its built-in mean is `-0.30`, far
below `baseline-rnn`, and its fixed-pool archived rows are worse than the
comparator across the hard tail. The candidate does not support a promotion
claim.

`rally-serve` itself is still useful as the base reference for the family, but
the fixed-pool check shows that built-in improvement alone is not the right
promotion criterion. The family can move the scoreboard on the easier rows
without matching the neural comparator on archived opponents.

## Promotion Recommendation

Do not promote any candidate from this robustness pass.

Keep `rally-serve-low-x52` as the best scalar/config development reference and
keep `post-contact` as the best structural follow-up, but treat both as
development-only diagnostics. Neither candidate closes the archived-opponent
gap to `baseline-rnn`, and `attack` is clearly not promotable.

Do not open holdout or audit seeds for any of these candidates based on this
evidence.

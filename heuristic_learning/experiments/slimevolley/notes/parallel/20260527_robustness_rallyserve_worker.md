# Rally-Serve Archived-Opponent Robustness Check

Worker: E
Date: 2026-05-27

## Scope

This check used only existing generation-4 development evidence from
`experiments/slimevolley/results/generation_4_summary.csv`. I did not rerun
probes because the summary already contains full fixed-pool `rally-serve` rows
for every requested opponent. I did not append ledger rows, did not use holdout
or audit seeds, and did not run `slimevolley-final-eval`.

Exact seeds used by the summarized rows: generation-4 dev seeds `9000..9049`
inclusive (`seed_start=9000`, `seed_stop_exclusive=9050`, `episodes=50`).

## Candidate Definition

Policy: `rally-serve`.

Definition: structural plus scalar/config candidate built on the late-contact
attack policy.

- Late-contact attack: for low descending balls moving toward the opponent,
  when `ball_x > 0.05`, `0.24 <= ball_y <= 0.65`, `ball_vx < -0.45`,
  `ball_vy < -0.35`, and `0.04 <= agent_x - ball_x <= 0.28`, return
  forward+jump action `101`.
- Rally-serve detector: after point resets, if `abs(ball_x) <= 0.28`,
  `ball_y >= 1.45`, `abs(ball_vx) <= 0.50`, and the last detection was more
  than `12` policy steps ago, run an `8` step forward+jump `101` serve macro.
- Scalar/config fields: `x_margin=0.04`, `contact_x_window=0.14`,
  `high_arc_horizon=0.95`, `overcommit_guard_x=0.18`,
  `low_ball_rescue_x_window=0.54`, `low_ball_rescue_horizon=0.06`,
  `grounded_low_receive_airborne_margin=0.16`, `landing_horizon=0.38`,
  `late_attack_y_min=0.24`, `late_attack_vx=-0.45`,
  `late_attack_vy=-0.35`.

## Fixed Dev Pool Results

Comparison baselines are the latest full-dev fixed-pool rows available in
`generation_4_summary.csv`: `improved-tuned` g4 scalar-tuned-v2 rows and
`attack` fixed-pool structural rows. Deltas are `rally-serve mean - comparator
mean`.

| Opponent | Rally mean | Rally W-L-D | Rally steps | Tuned mean | Delta vs tuned | Attack mean | Delta vs attack |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `builtin` | `0.14` | `13-8-29` | `150000` | `-0.44` | `+0.58` | `-0.30` | `+0.44` |
| `random` | `4.74` | `50-0-0` | `38217` | `4.66` | `+0.08` | `4.80` | `-0.06` |
| `initial` | `4.68` | `50-0-0` | `44634` | `4.56` | `+0.12` | `4.70` | `-0.02` |
| `improved-v0` | `4.70` | `50-0-0` | `43242` | `4.60` | `+0.10` | `4.74` | `-0.04` |
| `improved-v2` | `4.38` | `49-1-0` | `76391` | `4.38` | `+0.00` | `4.36` | `+0.02` |
| `improved-v3` | `2.98` | `48-0-2` | `138122` | `2.38` | `+0.60` | `2.62` | `+0.36` |
| `improved-v4` | `2.34` | `44-0-6` | `143814` | `2.08` | `+0.26` | `2.16` | `+0.18` |
| `improved-v5` | `1.16` | `32-7-11` | `149716` | `1.22` | `-0.06` | `1.08` | `+0.08` |
| `improved-v6` | `1.22` | `32-7-11` | `149716` | `1.20` | `+0.02` | `1.06` | `+0.16` |

Built-in comparator context from the same generation-4 dev range:
`baseline-rnn` vs `builtin` has mean `0.12`, W-L-D `18-12-20`, steps `150000`.
`rally-serve` is ahead by only `+0.02`, so the built-in result remains a narrow
development signal, not final evidence.

## Failure Analysis

The built-in gain does generalize to several archived opponents: compared with
latest `improved-tuned`, `rally-serve` is better on `builtin`, `random`,
`initial`, `improved-v0`, `improved-v3`, `improved-v4`, and `improved-v6`, and
ties mean score on `improved-v2`. It is also better than the fixed-pool `attack`
rows on the stronger archived opponents from `improved-v2` through
`improved-v6`.

The important archive regression is `improved-v5`: `rally-serve` mean `1.16`
versus latest `improved-tuned` mean `1.22`, a `-0.06` delta. Its W-L-D changes
from the tuned row's `31-5-14` to `32-7-11`, so the candidate gains one win but
also adds two losses and gives up three draws. `improved-v6` does not regress by
mean score (`1.22` versus tuned `1.20`), but it has the same more volatile
`32-7-11` W-L-D pattern. These rows suggest the serve/attack changes help
against the built-in opponent and mid archives, while nearest archive matchups
remain sensitive and should be treated as a caveat.

The small shortfall versus `attack` on `random`, `initial`, and `improved-v0`
does not look promotion-blocking because all three are still clean `50-0-0`
wins with high mean scores. The only material fixed-pool caveat is the
`improved-v5` regression versus the scalar baseline.

## Recommendation

The fixed development pool looks acceptable for freezing `rally-serve` for a
future sealed holdout/audit evaluation, with the `improved-v5` regression
recorded as the main risk. Do not claim final success from these rows. Do not
tune further on holdout or audit seeds; the next evidence step, if approved,
should be a predeclared sealed evaluation of the frozen candidate.

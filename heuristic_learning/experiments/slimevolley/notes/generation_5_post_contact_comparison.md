# Generation-5 Post-Contact Comparison

Date: 2026-05-27

## Scope

This is a generation-5 development-only check of the registered
`post-contact` candidate and a transient `net-pressure + post-contact` probe.
It uses only generation-5 development seeds `12000..12049`.

No generation-5 holdout seeds `13000..13049` and no audit seeds
`14000..14049` were used.

## Rows Added To Ledger

The registered `post-contact` policy was evaluated through the normal
SlimeVolley harness and appended to:

- `results/generation_5_trials.jsonl`
- `results/generation_5_summary.csv`

All rows used `seed_start=12000`, `episodes=50`, split `dev`, and recorded
`tests_pass_fail=pass`.

| Policy | Opponent | Mean | W-L-D | Steps |
| --- | --- | ---: | --- | ---: |
| `post-contact` | `builtin` | `-0.32` | `6/21/23` | `150000` |
| `post-contact` | `random` | `4.90` | `50/0/0` | `38374` |
| `post-contact` | `initial` | `4.88` | `50/0/0` | `45420` |
| `post-contact` | `improved-v0` | `4.88` | `50/0/0` | `44740` |
| `post-contact` | `improved-v2` | `4.66` | `50/0/0` | `69690` |
| `post-contact` | `improved-v3` | `2.84` | `46/1/3` | `137950` |
| `post-contact` | `improved-v4` | `2.38` | `44/3/3` | `143145` |
| `post-contact` | `improved-v5` | `1.32` | `35/5/10` | `149883` |
| `post-contact` | `improved-v6` | `1.28` | `35/5/10` | `150000` |

## Transient Combined Probe

A transient `net_post_contact` policy was evaluated without ledger writes and
saved to `results/generation_5_net_post_contact_probe.json`. It extends
`net-pressure` with the same two-frame front-conversion detector used by
`post-contact`.

| Policy | Opponent | Mean | W-L-D | Steps | Override frames |
| --- | --- | ---: | --- | ---: | ---: |
| `net_post_contact` | `builtin` | `-0.06` | `11/14/25` | `150000` | `1` |
| `net_post_contact` | `random` | `4.90` | `50/0/0` | `38968` | `0` |
| `net_post_contact` | `initial` | `4.86` | `50/0/0` | `46151` | `0` |
| `net_post_contact` | `improved-v0` | `4.84` | `50/0/0` | `45461` | `0` |
| `net_post_contact` | `improved-v2` | `4.68` | `50/0/0` | `69296` | `0` |
| `net_post_contact` | `improved-v3` | `3.08` | `48/1/1` | `140453` | `1` |
| `net_post_contact` | `improved-v4` | `2.56` | `45/2/3` | `142939` | `3` |
| `net_post_contact` | `improved-v5` | `1.20` | `34/7/9` | `149883` | `2` |
| `net_post_contact` | `improved-v6` | `1.22` | `34/7/9` | `149011` | `2` |

## Comparison

`post-contact` does not support a generation-5 promotion. It improves the
hardest archived tail slightly over `rally-serve` on `improved-v5` and ties on
`improved-v6`, but it regresses the built-in development row from
`rally-serve -0.28` to `-0.32` and is far worse than `net-pressure -0.06`.

The combined `net_post_contact` probe preserves `net-pressure` on the built-in
row but does not improve it. On the hard archived rows it is effectively the
same as `net-pressure`: `improved-v3 3.08`, `improved-v4 2.56`,
`improved-v5 1.20`, and `improved-v6 1.22`.

The neural comparator remains materially stronger on the harder archived
opponents:

| Opponent | Best heuristic in this note | Baseline RNN | Gap |
| --- | ---: | ---: | ---: |
| `improved-v3` | `3.08` | `4.24` | `-1.16` |
| `improved-v4` | `2.56` | `3.70` | `-1.14` |
| `improved-v5` | `1.32` | `2.38` | `-1.06` |
| `improved-v6` | `1.28` | `2.40` | `-1.12` |

## Failure Analysis

The generation-4 post-contact rule does not transfer cleanly to generation-5
built-in seeds. It likely optimizes a narrow near-net contact pattern that
helped archived rows in generation 4 but creates more losses against the
built-in opponent on the fresh generation-5 seed range.

Combining post-contact with `net-pressure` is also not useful. `net-pressure`
already captures the front-court pressure situations that the post-contact
detector can influence, so the added detector fires only a handful of times and
does not move score.

## Decision

Do not promote `post-contact` or `net_post_contact` for generation 5.

The next structural direction should not be another near-net conversion rule.
The remaining gap is now concentrated in hard archived-opponent robustness,
especially `improved-v3..improved-v6`, where the packaged RNN still wins far
more reliably. A useful next probe needs diagnostics on lost points against
those archived opponents, not more built-in-only front-court tuning.

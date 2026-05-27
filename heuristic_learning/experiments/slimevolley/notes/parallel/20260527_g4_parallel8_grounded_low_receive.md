# Generation-4 Parallel8 Grounded Low Receive Probe

Date: 2026-05-27

Kind: `structural policy improvement`

## Protocol

This development-only pass persisted a grounded-low-receive rerun that followed
the parallel7 result. It used the existing auditable probe script
`experiments/slimevolley/probes/g4_stacked_low_receive_probe.py` and wrote
`results/generation_4_parallel8_grounded_low_receive_probe.json`.

Commands observed:

```bash
cd /home/alpha/dev/research/learning-beyond-gradients/heuristic_learning
.venv/bin/python experiments/slimevolley/probes/g4_stacked_low_receive_probe.py --phase screen --candidate post_contact_reference --candidate baseline_rnn --candidate stacked_mode_rewrite_101 --candidate stacked_front_101_tight --candidate stacked_low_101_wide --candidate stacked_front_110_tight --output experiments/slimevolley/results/generation_4_parallel8_grounded_low_receive_probe.json
.venv/bin/python experiments/slimevolley/probes/g4_stacked_low_receive_probe.py --phase full --candidate post_contact_reference --candidate baseline_rnn --candidate stacked_low_101_wide --output experiments/slimevolley/results/generation_4_parallel8_grounded_low_receive_probe.json
```

Only generation-4 development seeds were used. The short screen used
`9000..9015`; the full follow-up used `9000..9049`. No generation-4 holdout
`10000..10049` or audit `11000..11049` seeds were used. No maintained policy,
config, or test edit was promoted.

## Short Screen

Rows use seeds `9000..9015`.

| Candidate | Built-in | improved-v4 | improved-v5 | improved-v6 | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| `post_contact_reference` | `0.3125` | `2.7500` | `1.3125` | `1.3750` | reference |
| `baseline_rnn` | `0.1250` | `3.2500` | `2.3125` | `2.5625` | neural comparator |
| `stacked_mode_rewrite_101` | `0.3125` | `2.7500` | `1.3125` | `1.3750` | exact tie with reference |
| `stacked_front_101_tight` | `0.3125` | `2.7500` | `1.3125` | `1.3750` | exact tie with reference |
| `stacked_low_101_wide` | `0.3125` | `2.7500` | `1.4375` | `1.5000` | full check |
| `stacked_front_110_tight` | `0.2500` | `2.5625` | `1.1250` | `1.1875` | reject |

`stacked_low_101_wide` was the only candidate expanded because it preserved the
built-in and `improved-v4` screen rows while improving `improved-v5/v6` by
`+0.1250`.

## Full Dev Follow-Up

Rows use seeds `9000..9049`.

| Opponent | `post_contact_reference` | `baseline_rnn` | `stacked_low_101_wide` | Delta vs reference |
| --- | ---: | ---: | ---: | ---: |
| `builtin` | `0.14` | `0.12` | `0.04` | `-0.10` |
| `random` | `4.74` | `4.80` | `4.74` | `0.00` |
| `initial` | `4.68` | `4.76` | `4.68` | `0.00` |
| `improved-v0` | `4.70` | `4.82` | `4.70` | `0.00` |
| `improved-v2` | `4.38` | `4.80` | `4.38` | `0.00` |
| `improved-v3` | `3.04` | `3.84` | `3.04` | `0.00` |
| `improved-v4` | `2.40` | `3.26` | `2.40` | `0.00` |
| `improved-v5` | `1.22` | `2.10` | `1.26` | `+0.04` |
| `improved-v6` | `1.28` | `2.18` | `1.32` | `+0.04` |

## Failure Analysis

The full-pool result repeats the parallel7 conclusion. `stacked_low_101_wide`
keeps only tiny `+0.04` hard-tail gains on `improved-v5/v6`, ties the middle
archived opponents, and regresses built-in by `-0.10`. It remains well below
`baseline_rnn` on all hard archived rows.

The branch is therefore active but not robust enough to promote. This pass adds
a persisted JSON audit trail for the rerun, not new policy evidence.

## Decision

Do not promote any candidate. Do not open holdout or audit seeds.

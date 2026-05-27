# Generation-4 Parallel7 Grounded Low Receive Probe

Date: 2026-05-27

Worker: B

Kind: `structural policy improvement`

## Protocol

This pass used the existing auditable probe script
`experiments/slimevolley/probes/g4_stacked_low_receive_probe.py` to test
stacked-frame grounded-low-receive structural branches against generation-4
development seeds only. No shared policy, eval, report, holdout, or audit code
was edited.

Commands run:

```bash
cd /home/alpha/dev/research/learning-beyond-gradients/heuristic_learning
.venv/bin/python experiments/slimevolley/probes/g4_stacked_low_receive_probe.py --phase screen --candidate post_contact_reference --candidate baseline_rnn --candidate stacked_mode_rewrite_101 --candidate stacked_split_front_rear --candidate stacked_low_101_wide --candidate stacked_front_110_tight --output /tmp/generation_4_parallel7_grounded_low_receive_screen.json
.venv/bin/python experiments/slimevolley/probes/g4_stacked_low_receive_probe.py --phase full --candidate post_contact_reference --candidate baseline_rnn --candidate stacked_low_101_wide --output /tmp/generation_4_parallel7_grounded_low_receive_full.json
```

Temporary artifacts:

- No temporary scripts were created.
- Temporary JSON outputs were written to
  `/tmp/generation_4_parallel7_grounded_low_receive_screen.json` and
  `/tmp/generation_4_parallel7_grounded_low_receive_full.json` and were not
  copied into the repository.

No holdout or audit seeds were used. In particular, generation-4 holdout
`10000..10049` and audit `11000..11049` remained untouched.

Short-screen seeds used exactly:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full follow-up seeds used exactly:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

Screen opponents: `builtin`, `improved-v4`, `improved-v5`, `improved-v6`

Fixed development opponent pool used for the one expanded candidate:
`builtin`, `random`, `initial`, `improved-v0`, `improved-v2`, `improved-v3`,
`improved-v4`, `improved-v5`, `improved-v6`

## Candidate Definitions

| Candidate | Type | Structural rule summary |
| --- | --- | --- |
| `post_contact_reference` | reference | Development-only `SlimeVolleyPostContactPolicy` comparator with no added stacked receive rewrite. |
| `baseline_rnn` | neural comparator | Packaged SlimeVolley baseline RNN comparator; context only, not a promotion target. |
| `stacked_mode_rewrite_101` | structural/history | When the inherited mode is `grounded_low_receive`, `low_ball_rescue`, or `late_low_ball_guard`, and recent own-contact history plus low/forward geometry agree, rewrite the action to forward+jump `101`. |
| `stacked_split_front_rear` | structural/history | Split the low receive region into a front-half `101` conversion and a rear-wall low-state `110` brace with no extra jump. |
| `stacked_low_101_wide` | structural/history | Use a wider own-side low receive window with recent own-contact history and rewrite to forward+jump `101`. |
| `stacked_front_110_tight` | structural/history | In a tight front low-contact window, replace the inherited action with the RNN-observed both-directions brace `110`. |

## Short Screen

Rows below use seeds `9000..9015`.

| Candidate | Builtin mean W-L-D steps overrides | `improved-v4` mean W-L-D steps overrides | `improved-v5` mean W-L-D steps overrides | `improved-v6` mean W-L-D steps overrides | Decision |
| --- | --- | --- | --- | --- | --- |
| `post_contact_reference` | `0.3125 4/0/12 48000 0` | `2.7500 15/0/1 44527 0` | `1.3125 9/3/4 47686 0` | `1.3750 9/3/4 47686 0` | comparator |
| `baseline_rnn` | `0.1250 6/4/6 48000 0` | `3.2500 16/0/0 40985 0` | `2.3125 14/1/1 46353 0` | `2.5625 14/1/1 45819 0` | neural comparator |
| `stacked_mode_rewrite_101` | `0.3125 4/0/12 48000 5` | `2.7500 15/0/1 44527 6` | `1.3125 9/3/4 47686 14` | `1.3750 9/3/4 47686 8` | reject: exact row-for-row tie with `post_contact_reference` |
| `stacked_split_front_rear` | `0.1250 3/2/11 48000 41` | `2.5000 13/0/3 44644 32` | `1.0625 8/4/4 47686 51` | `1.1250 8/4/4 47686 47` | reject: broad regression |
| `stacked_low_101_wide` | `0.3125 4/0/12 48000 29` | `2.7500 15/0/1 44527 16` | `1.4375 10/3/3 47686 25` | `1.5000 10/3/3 47686 17` | expand to full dev fixed-pool check |
| `stacked_front_110_tight` | `0.2500 4/1/11 48000 22` | `2.5625 15/0/1 44633 18` | `1.1250 9/3/4 48000 23` | `1.1875 9/3/4 48000 17` | reject: built-in regression |

Why `stacked_low_101_wide` was expanded:

- It preserved the `builtin` and `improved-v4` screen rows relative to
  `post_contact_reference`.
- It improved `improved-v5` from `1.3125` to `1.4375` and `improved-v6` from
  `1.3750` to `1.5000`, each with a `+1` win shift and `-1` draw shift.
- It still beat `baseline_rnn` on the 16-seed built-in screen row, so it was
  the only structural candidate that plausibly warranted a 50-seed check.

## Full Dev Follow-Up

Only `stacked_low_101_wide` was expanded to the full generation-4 development
pool.

### Full built-in row

Seeds `9000..9049`, opponent `builtin`.

| Candidate | Mean | W-L-D | Steps | Override frames |
| --- | ---: | --- | ---: | ---: |
| `post_contact_reference` | `0.14` | `13/8/29` | `150000` | `0` |
| `baseline_rnn` | `0.12` | `18/12/20` | `150000` | `0` |
| `stacked_low_101_wide` | `0.04` | `12/10/28` | `150000` | `120` |

The screen advantage did not survive the 50-seed built-in check. The candidate
fell below both `post_contact_reference` and `baseline_rnn`, so it is not a
promotion path.

### Fixed development opponent pool

Seeds `9000..9049`.

| Opponent | `post_contact_reference` mean W-L-D steps | `baseline_rnn` mean W-L-D steps | `stacked_low_101_wide` mean W-L-D steps overrides |
| --- | --- | --- | --- |
| `builtin` | `0.14 13/8/29 150000` | `0.12 18/12/20 150000` | `0.04 12/10/28 150000 120` |
| `random` | `4.74 50/0/0 38217` | `4.80 50/0/0 30603` | `4.74 50/0/0 38217 14` |
| `initial` | `4.68 50/0/0 44634` | `4.76 50/0/0 34004` | `4.68 50/0/0 44634 27` |
| `improved-v0` | `4.70 50/0/0 43242` | `4.82 50/0/0 32843` | `4.70 50/0/0 43242 23` |
| `improved-v2` | `4.38 49/1/0 76391` | `4.80 50/0/0 54551` | `4.38 49/1/0 76391 52` |
| `improved-v3` | `3.04 48/0/2 137816` | `3.84 50/0/0 118182` | `3.04 48/0/2 137816 41` |
| `improved-v4` | `2.40 44/0/6 143709` | `3.26 48/0/2 132511` | `2.40 44/0/6 143709 51` |
| `improved-v5` | `1.22 32/7/11 149402` | `2.10 42/2/6 145370` | `1.26 33/7/10 149402 64` |
| `improved-v6` | `1.28 32/7/11 149402` | `2.18 42/2/6 144837` | `1.32 33/7/10 149402 56` |

## Failure Analysis

The short-screen tail gains were real but too local. `stacked_low_101_wide`
kept only a `+0.04` mean gain against `improved-v5` and `improved-v6` on the
50-seed pool while giving back `-0.10` mean on `builtin`. That trade is not
acceptable for promotion.

The structural edits were active but not outcome-efficient. On the full pool,
`stacked_low_101_wide` spent `120` override frames on `builtin`, `64` on
`improved-v5`, and `56` on `improved-v6`, yet the only durable score movement
was the negative built-in shift. The branch is therefore changing behavior more
often than it is improving outcomes.

The other screen candidates do not justify expansion:

- `stacked_mode_rewrite_101` changed a small number of frames but reproduced
  `post_contact_reference` exactly on every screen row.
- `stacked_split_front_rear` was the clearest negative branch. Its front `101`
  plus rear `110` split produced `32..51` overrides per opponent and regressed
  every screened row.
- `stacked_front_110_tight` added brace behavior, but that brace cost built-in
  mean immediately and did not improve the hard rows.

The candidate also remains far behind `baseline_rnn` on the hard fixed-pool
opponents. Even where it improved the post-contact reference, it still trailed
the neural comparator by `0.86` on `improved-v5` and `0.86` on `improved-v6`.
This is not enough evidence for a grounded-low-receive structural rewrite.

## Promotion Recommendation

Do not promote any candidate from this parallel7 grounded-low-receive pass.

`stacked_low_101_wide` was the only structural/history branch that earned a
full dev follow-up, and the full built-in row rejected it before promotion was
even plausible. The fixed-pool results confirm the same conclusion: minor hard
row gains do not offset the built-in regression, and no candidate closes the
gap to `baseline_rnn`.

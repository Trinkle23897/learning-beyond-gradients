# Generation-4 Parallel9 Grounded Low Receive Probe

Date: 2026-05-27

Worker: B

Kind: `structural policy improvement`

## Protocol

This pass tested development-only stacked-frame receive branches for
`grounded_low_receive` and adjacent low own-side receive modes. It reused the
maintained helper logic from
`experiments/slimevolley/probes/g4_stacked_low_receive_probe.py` through a
transient `/tmp/g4_parallel9_grounded_low_receive_probe.py` runner. No
maintained policy, evaluation, or report code was edited.

Command run:

```bash
cd /home/alpha/dev/research/learning-beyond-gradients/heuristic_learning
PYTHONPATH=/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning ./.venv/bin/python /tmp/g4_parallel9_grounded_low_receive_probe.py --phase screen --candidate post_contact_reference --candidate baseline_rnn --candidate parallel9_narrow_low_net_101 --candidate parallel9_narrow_low_net_110 --candidate parallel9_split_front_rear_mode_gated --output experiments/slimevolley/results/generation_4_parallel9_grounded_low_receive_probe.json
```

Short-screen seeds used exactly:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Screen opponents: `builtin`, `improved-v4`, `improved-v5`, `improved-v6`

No holdout or audit seeds were used. In particular, generation-4 holdout
`10000..10049` and audit `11000..11049` remained untouched. No `9000..9049`
full dev follow-up was run because none of the structural/history candidates
improved any screen row over `post_contact_reference`.

## Candidate Definitions

| Candidate | Label | Definition |
| --- | --- | --- |
| `post_contact_reference` | `reference` | Development-only `SlimeVolleyPostContactPolicy` comparator with no added stacked receive rewrite. |
| `baseline_rnn` | `neural comparator` | Packaged baseline RNN comparator; context only, not a promotion target. |
| `parallel9_narrow_low_net_101` | `structural/history: narrow low-net 101 rewrite` | In `grounded_low_receive`, `late_low_ball_guard`, or `low_ball_rescue`, require recent own-contact history plus a narrow low-net own-side window and rewrite to forward+jump `101`. |
| `parallel9_narrow_low_net_110` | `structural/history: narrow low-net 110 brace` | Use the same narrow low-net receive idea, but replace the inherited action with a no-jump brace `110`. |
| `parallel9_split_front_rear_mode_gated` | `structural/history: mode-gated front 101, rear 110 split` | In grounded front-half low receive, convert to `101`; in rear low-rescue or rear-wall states, brace with `110`. |

## Short Screen Results

Rows below use seeds `9000..9015`.

| Candidate | Builtin mean W-L-D steps | `improved-v4` mean W-L-D steps | `improved-v5` mean W-L-D steps | `improved-v6` mean W-L-D steps | Decision |
| --- | --- | --- | --- | --- | --- |
| `post_contact_reference` | `0.3125 4/0/12 48000` | `2.7500 15/0/1 44527` | `1.3125 9/3/4 47686` | `1.3750 9/3/4 47686` | comparator |
| `baseline_rnn` | `0.1250 6/4/6 48000` | `3.2500 16/0/0 40985` | `2.3125 14/1/1 46353` | `2.5625 14/1/1 45819` | neural comparator |
| `parallel9_narrow_low_net_101` | `0.3125 4/0/12 48000` | `2.7500 15/0/1 44527` | `1.3125 9/3/4 47686` | `1.3750 9/3/4 47686` | reject: exact tie to reference on every row |
| `parallel9_narrow_low_net_110` | `0.3125 4/0/12 48000` | `2.7500 15/0/1 44528` | `1.3125 9/3/4 47686` | `1.3750 9/3/4 47686` | reject: exact tie to reference on every row |
| `parallel9_split_front_rear_mode_gated` | `0.3125 4/0/12 48000` | `2.7500 15/0/1 44527` | `1.3125 9/3/4 47686` | `1.3750 9/3/4 47686` | reject: exact tie to reference on every row |

Override activity from the generated JSON:

| Candidate | Builtin overrides | `improved-v4` overrides | `improved-v5` overrides | `improved-v6` overrides |
| --- | ---: | ---: | ---: | ---: |
| `parallel9_narrow_low_net_101` | 2 | 6 | 11 | 7 |
| `parallel9_narrow_low_net_110` | 2 | 5 | 10 | 7 |
| `parallel9_split_front_rear_mode_gated` | 4 | 6 | 11 | 7 |

## Failure Analysis

The mode-gated stacked-history receive rules were too inert to move outcomes.
All three candidates beat `baseline_rnn` on the built-in screen row only
because the inherited post-contact policy is already stronger than the neural
comparator there; each structural branch reproduced the reference scores
exactly on all four screened opponents.

The narrow gates did activate, but not in outcome-changing places. The `101`
rewrite changed only `2..11` frames per opponent, and the `110` brace changed
the same order of magnitude while inserting small amounts of `110` action mass
without moving wins, losses, draws, or total score.

The split front/rear candidate produced the same screen outcomes as the narrow
`101` rewrite and did not surface distinct rear-brace evidence in terminal
mode accounting. In practice this branch behaved like another sparse front-side
rewrite, not a robust front/rear action split.

Because none of the custom candidates improved any screened archived row over
`post_contact_reference`, there was no promising branch to justify a full
`9000..9049` fixed development pool check. Promoting a candidate that only ties
the reference while remaining well below `baseline_rnn` on `improved-v4/v5/v6`
would not meet the generation-4 bar.

## Promotion Recommendation

Do not promote any candidate from this parallel9 grounded-low-receive pass.

Keep the result JSON as an audit artifact only. The tested stacked-frame
grounded low-receive branches were interpretable and low-risk, but they did
not create any screen-row improvement worth expanding or carrying forward.

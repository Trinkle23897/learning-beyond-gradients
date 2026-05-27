# Generation-4 Parallel3 Grounded Low Receive History Probe

Date: 2026-05-27

Worker: 2

## Protocol

This was a development-only structural/history probe pass for
`grounded_low_receive`, focused on stacked-frame and short-history evidence.
The maintained policy code was not edited. The probe used transient subclasses
in `/tmp/g4_parallel3_grounded_low_receive_probe.py` and wrote the raw JSON
artifact to `/tmp/g4_parallel3_grounded_low_receive_probe.json`.

No canonical ledger, summary, policy, test, holdout, audit, or
`slimevolley-final-eval` artifact was written. No holdout or audit seeds were
used.

Command:

```bash
cd /home/alpha/dev/research/learning-beyond-gradients/heuristic_learning
.venv/bin/python /tmp/g4_parallel3_grounded_low_receive_probe.py --output /tmp/g4_parallel3_grounded_low_receive_probe.json
```

Short screen seeds, exactly:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full check seeds, exactly:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

Explicitly not used: generation-4 holdout `10000..10049`, generation-4 audit
`11000..11049`, generation-5 holdout `13000..13049`, generation-5 audit
`14000..14049`, and `slimevolley-final-eval`.

Cost accounting:

| Phase | Rows | Episodes | Environment steps |
| --- | ---: | ---: | ---: |
| Short screen | 24 | 384 | 1,119,228 |
| Full built-in | 8 | 400 | 1,200,000 |
| Fixed dev opponent pool | 72 | 3,600 | 7,379,865 |
| Total | 104 | 4,384 | 9,699,093 |

## Candidate Definitions

All six probes below are structural/history candidates. `rally_reference` and
`baseline_rnn` are references only.

| Candidate | Label | Definition |
| --- | --- | --- |
| `rally_reference` | reference | Current `SlimeVolleyRallyServePolicy` unchanged. |
| `baseline_rnn` | neural comparator reference | Packaged SlimeVolley baseline RNN wrapper. |
| `glr_history_quorum_gate` | structural/history: stacked low-descent quorum gate | When base `grounded_low_receive` fires, keep no-jump suppression only if at least 5 history frames, 3 low frames, 3 descending transitions, stacked `vy <= -0.015`, reachable predicted floor x, and no recent upward flip are present. Otherwise restore the normal low-rescue jump gate using stacked horizontal motion. |
| `glr_contact_flip_restore` | structural/history: contact-flip restore gate | When base `grounded_low_receive` fires within 4 frames of an inferred contact flip or within 3 frames of an upward velocity flip, restore the low-rescue jump gate. Otherwise keep suppression. |
| `glr_consecutive_low_gate` | structural/history: suppress only after consecutive low frames | Keep no-jump suppression only after at least 3 consecutive low falling frames. Otherwise restore the normal low-rescue jump gate. |
| `glr_consecutive_low_force_jump` | structural/history: force jump after repeated low frames | When base `grounded_low_receive` fires after at least 2 consecutive low falling frames and the ball is horizontally reachable, force a low-rescue jump. |
| `glr_post_contact_keep_else_restore` | structural/history: keep suppression only after contact-low evidence | Keep no-jump suppression only when recent contact evidence, repeated low frames, and stacked downward motion agree. Otherwise restore the low-rescue jump gate. |
| `glr_narrow_early_low_receive` | structural/history: narrow stacked early low-receive expansion | Outside base GLR, when base mode is `low_ball_rescue`, use a narrow stacked low-descent detector to suppress early jump before base GLR would fire. |

## Short Screen

Opponents: `builtin`, `improved-v4`, `improved-v6`. Seeds: `9000..9015`.

| Candidate | Opponent | Mean | W-L-D | Steps | GLR frames | Changed actions | Overrides | Kept suppression |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `rally_reference` | `builtin` | 0.3125 | 4/0/12 | 48,000 | 0 | 0 | 0 | 0 |
| `rally_reference` | `improved-v4` | 2.5625 | 15/0/1 | 44,632 | 0 | 0 | 0 | 0 |
| `rally_reference` | `improved-v6` | 1.1875 | 9/3/4 | 48,000 | 0 | 0 | 0 | 0 |
| `baseline_rnn` | `builtin` | 0.1250 | 6/4/6 | 48,000 | 0 | 0 | 0 | 0 |
| `baseline_rnn` | `improved-v4` | 3.2500 | 16/0/0 | 40,985 | 0 | 0 | 0 | 0 |
| `baseline_rnn` | `improved-v6` | 2.5625 | 14/1/1 | 45,819 | 0 | 0 | 0 | 0 |
| `glr_history_quorum_gate` | `builtin` | 0.3125 | 4/0/12 | 48,000 | 6 | 4 | 4 | 2 |
| `glr_history_quorum_gate` | `improved-v4` | 2.5625 | 15/0/1 | 44,632 | 7 | 3 | 3 | 4 |
| `glr_history_quorum_gate` | `improved-v6` | 1.1875 | 9/3/4 | 48,000 | 8 | 4 | 4 | 4 |
| `glr_contact_flip_restore` | `builtin` | 0.3125 | 4/0/12 | 48,000 | 6 | 4 | 4 | 2 |
| `glr_contact_flip_restore` | `improved-v4` | 2.5625 | 15/0/1 | 44,632 | 7 | 0 | 0 | 7 |
| `glr_contact_flip_restore` | `improved-v6` | 1.1875 | 9/3/4 | 48,000 | 8 | 6 | 6 | 2 |
| `glr_consecutive_low_gate` | `builtin` | 0.3125 | 4/0/12 | 48,000 | 6 | 0 | 0 | 6 |
| `glr_consecutive_low_gate` | `improved-v4` | 2.5625 | 15/0/1 | 44,632 | 7 | 0 | 0 | 7 |
| `glr_consecutive_low_gate` | `improved-v6` | 1.1875 | 9/3/4 | 48,000 | 8 | 0 | 0 | 8 |
| `glr_consecutive_low_force_jump` | `builtin` | 0.3125 | 4/0/12 | 48,000 | 6 | 6 | 6 | 0 |
| `glr_consecutive_low_force_jump` | `improved-v4` | 2.5625 | 15/0/1 | 44,632 | 7 | 7 | 7 | 0 |
| `glr_consecutive_low_force_jump` | `improved-v6` | 1.1875 | 9/3/4 | 48,000 | 8 | 8 | 8 | 0 |
| `glr_post_contact_keep_else_restore` | `builtin` | 0.3125 | 4/0/12 | 48,000 | 6 | 2 | 2 | 4 |
| `glr_post_contact_keep_else_restore` | `improved-v4` | 2.5625 | 15/0/1 | 44,632 | 7 | 7 | 7 | 0 |
| `glr_post_contact_keep_else_restore` | `improved-v6` | 1.1875 | 9/3/4 | 48,000 | 8 | 3 | 3 | 5 |
| `glr_narrow_early_low_receive` | `builtin` | 0.3125 | 4/0/12 | 48,000 | 6 | 0 | 0 | 6 |
| `glr_narrow_early_low_receive` | `improved-v4` | 2.5625 | 15/0/1 | 44,632 | 7 | 0 | 0 | 7 |
| `glr_narrow_early_low_receive` | `improved-v6` | 1.1875 | 9/3/4 | 48,000 | 8 | 0 | 0 | 8 |

Short-screen interpretation: every structural/history candidate tied
`rally_reference` on all screen opponents. The screen built-in row exceeded
`baseline_rnn` by point mean, so all candidates were full-checked on built-in
development seeds before any recommendation.

## Full Built-In Check

Opponent: `builtin`. Seeds: `9000..9049`.

| Candidate | Mean | W-L-D | Steps | GLR frames | Changed actions | Overrides | Kept suppression |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `rally_reference` | 0.14 | 13/8/29 | 150,000 | 0 | 0 | 0 | 0 |
| `baseline_rnn` | 0.12 | 18/12/20 | 150,000 | 0 | 0 | 0 | 0 |
| `glr_history_quorum_gate` | 0.14 | 13/8/29 | 150,000 | 30 | 17 | 17 | 13 |
| `glr_contact_flip_restore` | 0.14 | 13/8/29 | 150,000 | 30 | 15 | 15 | 15 |
| `glr_consecutive_low_gate` | 0.14 | 13/8/29 | 150,000 | 30 | 0 | 0 | 30 |
| `glr_consecutive_low_force_jump` | 0.14 | 13/8/29 | 150,000 | 30 | 30 | 30 | 0 |
| `glr_post_contact_keep_else_restore` | 0.14 | 13/8/29 | 150,000 | 30 | 16 | 16 | 14 |
| `glr_narrow_early_low_receive` | 0.14 | 13/8/29 | 150,000 | 30 | 0 | 0 | 30 |

All six structural/history candidates beat `baseline_rnn` on full built-in
point mean only by tying `rally_reference` at `0.14` versus `baseline_rnn`
`0.12`. Per the promotion rule, all six were checked against the fixed
development opponent pool before recommendation.

## Fixed Dev Opponent Pool

Opponents: `builtin`, `random`, `initial`, `improved-v0`, `improved-v2`,
`improved-v3`, `improved-v4`, `improved-v5`, `improved-v6`. Seeds:
`9000..9049`.

Every structural/history candidate exactly matched `rally_reference` on score
mean and W-L-D for every fixed-pool opponent. The table includes per-row GLR
and changed-action counts to show that several candidates did change behavior
without moving outcomes.

| Candidate | Opponent | Mean | W-L-D | Steps | GLR frames | Changed actions |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| `rally_reference` | `builtin` | 0.14 | 13/8/29 | 150,000 | 0 | 0 |
| `rally_reference` | `random` | 4.74 | 50/0/0 | 38,217 | 0 | 0 |
| `rally_reference` | `initial` | 4.68 | 50/0/0 | 44,634 | 0 | 0 |
| `rally_reference` | `improved-v0` | 4.70 | 50/0/0 | 43,242 | 0 | 0 |
| `rally_reference` | `improved-v2` | 4.38 | 49/1/0 | 76,391 | 0 | 0 |
| `rally_reference` | `improved-v3` | 2.98 | 48/0/2 | 138,122 | 0 | 0 |
| `rally_reference` | `improved-v4` | 2.34 | 44/0/6 | 143,814 | 0 | 0 |
| `rally_reference` | `improved-v5` | 1.16 | 32/7/11 | 149,716 | 0 | 0 |
| `rally_reference` | `improved-v6` | 1.22 | 32/7/11 | 149,716 | 0 | 0 |
| `baseline_rnn` | `builtin` | 0.12 | 18/12/20 | 150,000 | 0 | 0 |
| `baseline_rnn` | `random` | 4.80 | 50/0/0 | 30,603 | 0 | 0 |
| `baseline_rnn` | `initial` | 4.76 | 50/0/0 | 34,004 | 0 | 0 |
| `baseline_rnn` | `improved-v0` | 4.82 | 50/0/0 | 32,843 | 0 | 0 |
| `baseline_rnn` | `improved-v2` | 4.80 | 50/0/0 | 54,551 | 0 | 0 |
| `baseline_rnn` | `improved-v3` | 3.84 | 50/0/0 | 118,182 | 0 | 0 |
| `baseline_rnn` | `improved-v4` | 3.26 | 48/0/2 | 132,511 | 0 | 0 |
| `baseline_rnn` | `improved-v5` | 2.10 | 42/2/6 | 145,370 | 0 | 0 |
| `baseline_rnn` | `improved-v6` | 2.18 | 42/2/6 | 144,837 | 0 | 0 |
| `glr_history_quorum_gate` | `builtin` | 0.14 | 13/8/29 | 150,000 | 30 | 17 |
| `glr_history_quorum_gate` | `random` | 4.74 | 50/0/0 | 38,217 | 13 | 1 |
| `glr_history_quorum_gate` | `initial` | 4.68 | 50/0/0 | 44,634 | 13 | 1 |
| `glr_history_quorum_gate` | `improved-v0` | 4.70 | 50/0/0 | 43,242 | 15 | 3 |
| `glr_history_quorum_gate` | `improved-v2` | 4.38 | 49/1/0 | 76,391 | 21 | 4 |
| `glr_history_quorum_gate` | `improved-v3` | 2.98 | 48/0/2 | 138,122 | 18 | 6 |
| `glr_history_quorum_gate` | `improved-v4` | 2.34 | 44/0/6 | 143,814 | 16 | 4 |
| `glr_history_quorum_gate` | `improved-v5` | 1.16 | 32/7/11 | 149,716 | 19 | 7 |
| `glr_history_quorum_gate` | `improved-v6` | 1.22 | 32/7/11 | 149,716 | 17 | 5 |
| `glr_contact_flip_restore` | `builtin` | 0.14 | 13/8/29 | 150,000 | 30 | 15 |
| `glr_contact_flip_restore` | `random` | 4.74 | 50/0/0 | 38,217 | 13 | 0 |
| `glr_contact_flip_restore` | `initial` | 4.68 | 50/0/0 | 44,634 | 13 | 0 |
| `glr_contact_flip_restore` | `improved-v0` | 4.70 | 50/0/0 | 43,242 | 15 | 2 |
| `glr_contact_flip_restore` | `improved-v2` | 4.38 | 49/1/0 | 76,391 | 21 | 5 |
| `glr_contact_flip_restore` | `improved-v3` | 2.98 | 48/0/2 | 138,122 | 18 | 2 |
| `glr_contact_flip_restore` | `improved-v4` | 2.34 | 44/0/6 | 143,814 | 16 | 0 |
| `glr_contact_flip_restore` | `improved-v5` | 1.16 | 32/7/11 | 149,716 | 19 | 8 |
| `glr_contact_flip_restore` | `improved-v6` | 1.22 | 32/7/11 | 149,716 | 17 | 6 |
| `glr_consecutive_low_gate` | `builtin` | 0.14 | 13/8/29 | 150,000 | 30 | 0 |
| `glr_consecutive_low_gate` | `random` | 4.74 | 50/0/0 | 38,217 | 13 | 0 |
| `glr_consecutive_low_gate` | `initial` | 4.68 | 50/0/0 | 44,634 | 13 | 0 |
| `glr_consecutive_low_gate` | `improved-v0` | 4.70 | 50/0/0 | 43,242 | 15 | 0 |
| `glr_consecutive_low_gate` | `improved-v2` | 4.38 | 49/1/0 | 76,391 | 21 | 0 |
| `glr_consecutive_low_gate` | `improved-v3` | 2.98 | 48/0/2 | 138,122 | 18 | 0 |
| `glr_consecutive_low_gate` | `improved-v4` | 2.34 | 44/0/6 | 143,814 | 16 | 0 |
| `glr_consecutive_low_gate` | `improved-v5` | 1.16 | 32/7/11 | 149,716 | 19 | 0 |
| `glr_consecutive_low_gate` | `improved-v6` | 1.22 | 32/7/11 | 149,716 | 17 | 0 |
| `glr_consecutive_low_force_jump` | `builtin` | 0.14 | 13/8/29 | 150,000 | 30 | 30 |
| `glr_consecutive_low_force_jump` | `random` | 4.74 | 50/0/0 | 38,217 | 13 | 13 |
| `glr_consecutive_low_force_jump` | `initial` | 4.68 | 50/0/0 | 44,634 | 13 | 13 |
| `glr_consecutive_low_force_jump` | `improved-v0` | 4.70 | 50/0/0 | 43,242 | 15 | 15 |
| `glr_consecutive_low_force_jump` | `improved-v2` | 4.38 | 49/1/0 | 76,391 | 21 | 21 |
| `glr_consecutive_low_force_jump` | `improved-v3` | 2.98 | 48/0/2 | 138,122 | 18 | 18 |
| `glr_consecutive_low_force_jump` | `improved-v4` | 2.34 | 44/0/6 | 143,814 | 16 | 16 |
| `glr_consecutive_low_force_jump` | `improved-v5` | 1.16 | 32/7/11 | 149,716 | 19 | 19 |
| `glr_consecutive_low_force_jump` | `improved-v6` | 1.22 | 32/7/11 | 149,716 | 17 | 17 |
| `glr_post_contact_keep_else_restore` | `builtin` | 0.14 | 13/8/29 | 150,000 | 30 | 16 |
| `glr_post_contact_keep_else_restore` | `random` | 4.74 | 50/0/0 | 38,217 | 13 | 13 |
| `glr_post_contact_keep_else_restore` | `initial` | 4.68 | 50/0/0 | 44,634 | 13 | 13 |
| `glr_post_contact_keep_else_restore` | `improved-v0` | 4.70 | 50/0/0 | 43,242 | 15 | 13 |
| `glr_post_contact_keep_else_restore` | `improved-v2` | 4.38 | 49/1/0 | 76,391 | 21 | 16 |
| `glr_post_contact_keep_else_restore` | `improved-v3` | 2.98 | 48/0/2 | 138,122 | 18 | 16 |
| `glr_post_contact_keep_else_restore` | `improved-v4` | 2.34 | 44/0/6 | 143,814 | 16 | 16 |
| `glr_post_contact_keep_else_restore` | `improved-v5` | 1.16 | 32/7/11 | 149,716 | 19 | 12 |
| `glr_post_contact_keep_else_restore` | `improved-v6` | 1.22 | 32/7/11 | 149,716 | 17 | 12 |
| `glr_narrow_early_low_receive` | `builtin` | 0.14 | 13/8/29 | 150,000 | 30 | 0 |
| `glr_narrow_early_low_receive` | `random` | 4.74 | 50/0/0 | 38,217 | 13 | 0 |
| `glr_narrow_early_low_receive` | `initial` | 4.68 | 50/0/0 | 44,634 | 13 | 0 |
| `glr_narrow_early_low_receive` | `improved-v0` | 4.70 | 50/0/0 | 43,242 | 15 | 0 |
| `glr_narrow_early_low_receive` | `improved-v2` | 4.38 | 49/1/0 | 76,391 | 21 | 0 |
| `glr_narrow_early_low_receive` | `improved-v3` | 2.98 | 48/0/2 | 138,122 | 18 | 0 |
| `glr_narrow_early_low_receive` | `improved-v4` | 2.34 | 44/0/6 | 143,814 | 16 | 0 |
| `glr_narrow_early_low_receive` | `improved-v5` | 1.16 | 32/7/11 | 149,716 | 19 | 0 |
| `glr_narrow_early_low_receive` | `improved-v6` | 1.22 | 32/7/11 | 149,716 | 17 | 0 |

## Failure Analysis

The current `grounded_low_receive` branch is still too sparse to produce useful
branch-local improvement. On full built-in development seeds it fired only 30
frames out of 150,000 environment steps. The screen had only 6 built-in GLR
frames out of 48,000 steps.

The history signals are present but not selective enough to move outcomes. On
full built-in rows, the harness observed 9,636 stacked low frames, 2,951 inferred
own-contact flips, 2,765 inferred opponent-contact flips, and 3,956 upward
flips, but only 30 base GLR frames. Rules that used those signals inside GLR
changed actions without changing any score row.

The most aggressive branch-local ablation was
`glr_consecutive_low_force_jump`: it changed every full built-in GLR action
(`30/30`) and every fixed-pool GLR action for each opponent, yet matched
`rally_reference` exactly on every score and W-L-D row. That is strong evidence
that current GLR frames are low-leverage in this dev slice.

The consecutive-low gate and narrow early expansion were effectively diagnostic
no-ops. All observed GLR frames already satisfied the consecutive-low condition,
and the narrow early expansion never changed an action on these seeds. The
more selective history-quorum, contact-flip, and post-contact gates did change
some actions, but those changes were behavior churn without measured benefit.

The fixed-pool check also keeps the neural-comparator gap unchanged. Although
all structural/history candidates beat `baseline_rnn` on built-in point mean by
tying `rally_reference`, they remain far below `baseline_rnn` on harder archived
opponents such as `improved-v4`, `improved-v5`, and `improved-v6`.

## Promotion Recommendation

Do not promote any `grounded_low_receive` structural/history candidate from
this pass.

Best result: `glr_history_quorum_gate`, `glr_contact_flip_restore`,
`glr_consecutive_low_force_jump`, and `glr_post_contact_keep_else_restore` all
demonstrated actual GLR action changes while tying the full built-in
`rally_reference` row at mean `0.14`, W-L-D `13/8/29`, and `150,000` steps.
After the required fixed-pool check, all matched `rally_reference` exactly
across every fixed-pool opponent. This is negative evidence for further
branch-local `grounded_low_receive` history gates unless a future candidate
changes earlier receive positioning or a broader low-ball mode with a stronger
contact-quality discriminator.

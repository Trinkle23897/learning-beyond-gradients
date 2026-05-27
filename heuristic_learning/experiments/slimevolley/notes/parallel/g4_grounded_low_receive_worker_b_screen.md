# G4 Grounded Low Receive Worker B Screen

Date: 2026-05-27

This was a development-only structural branch probe for `grounded_low_receive`
or equivalent grounded low-ball receiving behavior. The probe used transient
subclasses in `/tmp/g4_grounded_low_receive_worker_b_probe.py`; no production
policy, test, ledger, summary, holdout, or audit file was modified or written.

Command:

```bash
cd /home/alpha/dev/research/learning-beyond-gradients/heuristic_learning
.venv/bin/python /tmp/g4_grounded_low_receive_worker_b_probe.py
```

Seeds used exactly:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

No holdout or audit seeds were used. In particular, no generation-4 holdout
`10000..10049` or audit `11000..11049` seeds were run.

## Candidate Definitions

All probe candidates are structural branch edits layered transiently on current
`rally-serve`; there was no scalar/config tuning.

| Candidate | Label | Definition |
| --- | --- | --- |
| `rally_reference` | reference | Current generation-4 `rally-serve` policy unchanged. |
| `baseline_rnn_reference` | neural comparator reference | Packaged SlimeVolley baseline RNN wrapper; context only, not a promotion target. |
| `glr_floor_intercept_jump` | structural branch probe | On grounded low-ball receive context, recompute a floor-intercept target and jump only inside a narrow predicted-contact window. |
| `glr_front_scoop_jump` | structural branch probe | On grounded low-ball receive context with the ball in front/near-net, force forward+jump as a scoop attempt. |
| `glr_brace_no_jump` | structural branch probe | On late grounded low-ball receive when the body is already ahead of the ball, suppress jump and brace with base horizontal movement. |
| `glr_contact_flip_scoop` | structural/history branch probe | On grounded low-ball receive with a recent low contact/upward velocity flip, jump toward a short-horizon ball target. |

## Short Screen Results

Opponents: `builtin`, `improved-v4`, `improved-v6`. Seeds: `9000..9015`.

| Candidate | Opponent | Mean | W-L-D | Steps | Probe activity |
| --- | --- | ---: | --- | ---: | --- |
| `rally_reference` | `builtin` | 0.312500 | 4/0/12 | 48000 | reference |
| `rally_reference` | `improved-v4` | 2.562500 | 15/0/1 | 44632 | reference |
| `rally_reference` | `improved-v6` | 1.187500 | 9/3/4 | 48000 | reference |
| `baseline_rnn_reference` | `builtin` | 0.125000 | 6/4/6 | 48000 | reference |
| `baseline_rnn_reference` | `improved-v4` | 3.250000 | 16/0/0 | 40985 | reference |
| `baseline_rnn_reference` | `improved-v6` | 2.562500 | 14/1/1 | 45819 | reference |
| `glr_floor_intercept_jump` | `builtin` | -4.750000 | 0/16/0 | 20606 | grounded context 815, overrides 815, changed actions 618 |
| `glr_floor_intercept_jump` | `improved-v4` | -1.625000 | 3/12/1 | 31796 | grounded context 864, overrides 864, changed actions 631 |
| `glr_floor_intercept_jump` | `improved-v6` | -3.500000 | 0/16/0 | 31858 | grounded context 993, overrides 993, changed actions 701 |
| `glr_front_scoop_jump` | `builtin` | -4.312500 | 0/16/0 | 39673 | grounded context 1260, overrides 312, changed actions 298 |
| `glr_front_scoop_jump` | `improved-v4` | -0.812500 | 5/9/2 | 40946 | grounded context 1024, overrides 244, changed actions 218 |
| `glr_front_scoop_jump` | `improved-v6` | -2.125000 | 2/11/3 | 41974 | grounded context 1111, overrides 236, changed actions 209 |
| `glr_brace_no_jump` | `builtin` | 0.250000 | 4/1/11 | 48000 | grounded context 1308, overrides 38, changed actions 6 |
| `glr_brace_no_jump` | `improved-v4` | 2.562500 | 14/0/2 | 44632 | grounded context 901, overrides 23, changed actions 7 |
| `glr_brace_no_jump` | `improved-v6` | 1.500000 | 11/2/3 | 48000 | grounded context 1040, overrides 26, changed actions 8 |
| `glr_contact_flip_scoop` | `builtin` | 0.187500 | 3/1/12 | 48000 | grounded context 1308, overrides 13, changed actions 5 |
| `glr_contact_flip_scoop` | `improved-v4` | 2.562500 | 15/0/1 | 43689 | grounded context 885, overrides 8, changed actions 2 |
| `glr_contact_flip_scoop` | `improved-v6` | 1.187500 | 9/3/4 | 48000 | grounded context 1050, overrides 14, changed actions 4 |

## Failure Analysis

The broader grounded low-ball context is much less sparse than the original
`grounded_low_receive` branch, but the aggressive receive rewrites are not
selective. `glr_floor_intercept_jump` and `glr_front_scoop_jump` changed
hundreds of actions and collapsed every screened opponent row, including the
built-in row.

`glr_brace_no_jump` is the only probe with an apparent archived-opponent gain:
`improved-v6` improved from `1.187500` and `9/3/4` to `1.500000` and `11/2/3`.
That gain is not promotable because the same branch regressed built-in from
`0.312500`, `4/0/12` to `0.250000`, `4/1/11`, and degraded the `improved-v4`
win/draw split from `15/0/1` to `14/0/2` despite the same point mean.

`glr_contact_flip_scoop` was more conservative, but it still regressed built-in
to `0.187500`, `3/1/12` and only tied `rally_reference` on the archived rows.
The branch activity counts show that grounded receive contexts are plentiful,
but the tested local action changes either hurt immediately or move too few
outcomes to justify expansion.

## Promotion Recommendation

Do not promote any Worker B `grounded_low_receive` or grounded low-ball receive
candidate from this pass. The only positive-looking row was
`glr_brace_no_jump` versus `improved-v6`, and promotion cannot be based on one
opponent while the same branch regresses built-in and worsens the `improved-v4`
win/draw profile. No full `9000..9049` expansion is recommended from this
screen.

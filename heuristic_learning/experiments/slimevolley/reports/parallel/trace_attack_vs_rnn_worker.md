# Trace Attack Vs RNN Worker C

## Exact seeds used

Generation-4 development seeds only: `9000..9049`.

Exact list: `9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`.

No holdout seeds (`10000..10049`) or audit seeds (`11000..11049`) were used.

## Candidate/diagnostic definition

Comparison: current `attack` policy vs `baseline-rnn`, both against opponent `builtin`.

Primary headline metrics were confirmed from existing generation-4 trace ledger rows:

- `attack` vs `builtin`: row 82, timestamp `2026-05-27T00:45:08+00:00`, trace window `12`.
- `baseline-rnn` vs `builtin`: row 83, timestamp `2026-05-27T00:45:37+00:00`, trace window `12`.

Because those persisted rows did not include branch-label diagnostics in trace frames, a no-ledger in-memory diagnostic probe was run with the same policy/opponent pairs, `split=dev`, `seed_start=9000`, `episodes=50`, and `trace_window=12`. The no-ledger probe reproduced the existing headline scores exactly and did not write ledger rows.

## Score mean/W-L-D/steps for attack and baseline-rnn

| Policy | Score mean | W/L/D | Environment steps | Episode step range |
| --- | ---: | --- | ---: | --- |
| `attack` | `-0.30` | `7/18/25` | `150000` | `3000..3000` |
| `baseline-rnn` | `0.12` | `18/12/20` | `150000` | `3000..3000` |

Same-seed built-in gap: `baseline-rnn` is ahead by `0.42` score points.

## Structural/scalar label as diagnostics only

These labels are diagnostic annotations only. They are not promotion evidence and were not used to select a candidate.

`attack` is labeled `slimevolley_attack_candidate` with `candidate_status=partial_not_promoted`. It is a structural `late_contact_attack` rule layered on the scalar/config tuned revision `g4-scalar-tuned-v2`. The late-contact rule fires `101` when `ball_x > 0.05`, `0.28 <= ball_y <= 0.65`, `ball_vx < -0.35`, `ball_vy < -0.10`, and `0.04 <= agent_x - ball_x <= 0.28`.

The inherited scalar-tuned fields are `x_margin=0.04`, `contact_x_window=0.14`, `high_arc_horizon=0.85`, `overcommit_guard_x=0.18`, `low_ball_rescue_x_window=0.72`, `low_ball_rescue_horizon=0.06`, and `grounded_low_receive_airborne_margin=0.12`.

`baseline-rnn` is labeled `slimevolley_builtin_rnn`, a pretrained neural/RNN comparator with `parameter_count=120` from `slimevolleygym.slimevolley.BaselinePolicy`. It has no structural/scalar branch labels in policy diagnostics.

No-ledger trace-window branch counts for `attack`: `intercept=165`, `recovery=116`, `low_ball_rescue=91`, `late_contact_attack=85`, `falling_floor_intercept=48`, `grounded_low_receive=39`, `rear_wall_press=36`, `rear_wall_low_jump=8`.

## Key failure buckets

Point-event totals:

| Policy | Point won | Point lost |
| --- | ---: | ---: |
| `attack` | `17` | `32` |
| `baseline-rnn` | `31` | `25` |

Loss buckets:

| Bucket | `attack` losses | `baseline-rnn` losses |
| --- | ---: | ---: |
| `low_left_or_net` | `14` | `4` |
| `low_far_right` | `8` | `16` |
| `low_other_own_side` | `8` | `3` |
| `low_mid_right` | `2` | `2` |

`attack` terminal loss modes: `grounded_low_receive=16`, `low_ball_rescue=8`, `rear_wall_low_jump=4`, `rear_wall_press=4`.

`attack` terminal loss actions: `101=12`, `100=11`, `010=5`, `000=4`. `baseline-rnn` terminal loss actions: `101=12`, `001=9`, `010=2`, `011=1`, `110=1`.

Inferred contact candidates appeared in `25/32` `attack` point-loss windows and `16/25` `baseline-rnn` point-loss windows. For `attack`, those contact-loss windows were mostly `low_left_or_net=11`, `low_far_right=8`, and `low_other_own_side=5`.

## Failure analysis

`attack` still loses more points and matches than the RNN comparator on the exact same dev seeds. The loss distribution is broader than `baseline-rnn`: the RNN's remaining failures are mostly far-right low balls, while `attack` adds many low-left/net and low own-side failures.

The `late_contact_attack` branch is active in the trace windows, but it does not convert enough low-ball situations into wins. It appeared `80` times in point-loss trace windows and only `5` times in point-win trace windows. Because trace-window labels are short-horizon diagnostics, this is not proof of direct causality, but it is a strong warning that the active-return rule is often present near failed points.

The terminal `attack` loss labels point to receive/recovery timing rather than a single missing branch. `grounded_low_receive` dominates terminal losses, often with the agent above a low ball near the net or own side. `low_ball_rescue`, `rear_wall_low_jump`, and `rear_wall_press` still fail on low descending balls near the rear wall or mid-right. The scalar-tuned contact window and late attack rule help some situations, but they leave floor-height returns undercontrolled.

## Promotion recommendation

Do not promote `attack`. It remains below `baseline-rnn` by `0.42` mean score on generation-4 development seeds, has worse W/L/D (`7/18/25` vs `18/12/20`), loses more points (`32` vs `25`), and has unresolved low-left/net plus low own-side failure buckets.

Keep this as development-only diagnostic evidence. Do not open holdout or audit seeds, and do not write generation-4 ledger rows for this diagnostic.

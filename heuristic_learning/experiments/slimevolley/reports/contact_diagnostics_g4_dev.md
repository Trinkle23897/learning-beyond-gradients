# SlimeVolley Generation-3 Contact/Return Diagnostics

This report is generated from persisted development traces only. It does not run evaluation and does not inspect generation-3 holdout seeds.

## Selection

- Status: `pass`
- Environment: `SlimeVolley-v0`
- Policy/opponent/split: `improved` vs `builtin` on `dev`
- Selected row: `2026-05-26T22:21:59+00:00`
- Change type: `logging/diagnostics change`
- Seeds: `9000..9049`
- Trace window: `16`
- Score mean: `-2.240`
- W/L/D: `1/43/6`

## Point Outcomes

| Outcome | Count |
| --- | ---: |
| point_lost | 132 |
| point_won | 20 |

## Loss Buckets

| Bucket | Count |
| --- | ---: |
| low_left_or_net | 60 |
| other | 41 |
| low_far_right | 18 |
| low_mid_right | 13 |

## Inferred Contact Candidates

- Candidate count: `313`
- By event outcome: `{'point_lost': 306, 'point_won': 7}`
- By action: `{'101': 77, '010': 61, '000': 54, '100': 53, '001': 48, '011': 20}`
- By x bucket: `{'near_net': 152, 'rear_wall': 71, 'front_half': 51, 'back_half': 39}`

| Seed | Event step | Candidate step | Outcome | Action | X bucket | Ball x/y | Ball vx delta |
| ---: | ---: | ---: | --- | --- | --- | --- | ---: |
| 9006 | 76 | 71 | point_lost | 100 | front_half | 0.361/0.301 | -8.060 |
| 9006 | 76 | 72 | point_lost | 100 | front_half | 0.287/0.316 | 3.945 |
| 9006 | 76 | 75 | point_lost | 101 | near_net | 0.106/0.336 | 4.371 |
| 9006 | 76 | 76 | point_lost | 000 | near_net | 0.111/0.258 | -3.057 |
| 9032 | 102 | 101 | point_lost | 100 | near_net | 0.100/0.291 | 2.384 |
| 9020 | 143 | 136 | point_lost | 101 | front_half | 0.585/0.437 | -5.741 |
| 9020 | 143 | 137 | point_lost | 101 | front_half | 0.512/0.417 | 2.392 |
| 9020 | 143 | 143 | point_lost | 100 | near_net | 0.100/0.240 | 3.984 |
| 9019 | 150 | 147 | point_lost | 010 | rear_wall | 2.350/0.413 | -4.308 |
| 9019 | 150 | 149 | point_lost | 010 | rear_wall | 2.252/0.310 | 2.122 |
| 9019 | 150 | 150 | point_lost | 010 | rear_wall | 2.252/0.235 | 0.013 |
| 9027 | 169 | 162 | point_lost | 101 | front_half | 0.839/0.473 | -2.533 |

## Limitations

- Contacts are inferred from compact pre-event trace velocity changes, not from engine contact callbacks.
- The default artifact reads development rows only and does not inspect generation-3 holdout seeds.
- Trace windows are short, so absence of a candidate does not prove absence of contact earlier in a rally.

## Next Hypotheses

- Target return placement after inferred contact instead of restarting serve behavior.
- Separate front-net and rear-wall low-loss buckets; they may need different recovery modes.
- Before a new policy edit, run this diagnostic on the current dev row and compare contact candidate locations against failed attempts.

## Anti-Tuning Note

This artifact is generated from development traces only. Generation-3 holdout remains final-only and must not be inspected for policy design.

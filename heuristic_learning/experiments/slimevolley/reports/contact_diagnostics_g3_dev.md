# SlimeVolley Generation-3 Contact/Return Diagnostics

This report is generated from persisted development traces only. It does not run evaluation and does not inspect generation-3 holdout seeds.

## Selection

- Status: `pass`
- Environment: `SlimeVolley-v0`
- Policy/opponent/split: `improved` vs `builtin` on `dev`
- Selected row: `2026-05-25T21:00:11+00:00`
- Change type: `structural policy improvement`
- Seeds: `6000..6049`
- Trace window: `8`
- Score mean: `-3.800`
- W/L/D: `0/48/2`

## Point Outcomes

| Outcome | Count |
| --- | ---: |
| point_lost | 206 |
| point_won | 16 |

## Loss Buckets

| Bucket | Count |
| --- | ---: |
| low_far_right | 75 |
| low_left_or_net | 50 |
| other | 48 |
| low_mid_right | 33 |

## Inferred Contact Candidates

- Candidate count: `281`
- By event outcome: `{'point_lost': 281}`
- By action: `{'011': 78, '010': 62, '100': 58, '001': 35, '000': 27, '101': 21}`
- By x bucket: `{'rear_wall': 132, 'near_net': 97, 'front_half': 36, 'back_half': 16}`

| Seed | Event step | Candidate step | Outcome | Action | X bucket | Ball x/y | Ball vx delta |
| ---: | ---: | ---: | --- | --- | --- | --- | ---: |
| 6014 | 110 | 110 | point_lost | 101 | near_net | 0.100/0.223 | 3.622 |
| 6009 | 138 | 134 | point_lost | 001 | near_net | 0.143/0.385 | -0.965 |
| 6009 | 138 | 136 | point_lost | 001 | near_net | 0.100/0.303 | 1.351 |
| 6009 | 138 | 137 | point_lost | 001 | near_net | 0.100/0.263 | 1.769 |
| 6010 | 167 | 161 | point_lost | 101 | back_half | 1.523/0.527 | -2.526 |
| 6043 | 171 | 166 | point_lost | 001 | near_net | 0.008/0.475 | 2.506 |
| 6043 | 171 | 167 | point_lost | 001 | near_net | 0.066/0.437 | 0.934 |
| 6035 | 177 | 176 | point_lost | 001 | near_net | 0.090/0.292 | -1.619 |
| 6044 | 179 | 177 | point_lost | 010 | rear_wall | 1.957/0.345 | 3.220 |
| 6044 | 179 | 178 | point_lost | 010 | rear_wall | 1.987/0.277 | -0.814 |
| 6008 | 187 | 186 | point_lost | 100 | near_net | 0.100/0.259 | 3.966 |
| 6040 | 304 | 301 | point_lost | 011 | rear_wall | 2.102/0.458 | 1.039 |

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

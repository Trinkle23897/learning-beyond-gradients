# G4 Archived-Opponent Robustness: Post-Contact

Date: 2026-05-27

## Scope

Worker E ran a generation-4 development-only no-ledger robustness check for the
existing `post-contact` heuristic candidate. No source, ledger, summary,
holdout, or audit artifact was edited by the run.

Exact seeds used:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

No short subset was used. No holdout seeds `10000..10049` and no audit seeds
`11000..11049` were used.

Command pattern:

`make -s PYTHON=.venv/bin/python slimevolley-eval POLICY=post-contact OPPONENT=<opponent> SPLIT=dev ARGS="--seed-start 9000 --episodes 50 --no-ledger"`

Opponents: `builtin`, `random`, `initial`, `improved-v0`, `improved-v2`,
`improved-v3`, `improved-v4`, `improved-v5`, `improved-v6`.

## Candidate Definition

Candidate: `post-contact`.

Type: structural/history candidate layered on the `rally-serve` scalar/config
baseline. It inherits the `late_contact_attack` and `rally_serve_detector`
rules, then adds `post_contact_front_conversion`: when a recent contact-like
velocity flip is detected within 2 policy steps, force action `101` in the
front-court window `ball_x in [-0.08, 0.48]`, `ball_y in [0.24, 0.82]`,
`ball_vx < -0.04`, `ball_vy <= 0.12`, and `agent_x - ball_x in [-0.05, 0.70]`.

This is not a scalar-only change. The scalar/config fields are inherited from
the existing `rally-serve` candidate; the tested change is structural.

## Results

| Opponent | Mean | W-L-D | Steps |
| --- | ---: | --- | ---: |
| `builtin` | `0.14` | `13-8-29` | `150000` |
| `random` | `4.74` | `50-0-0` | `38217` |
| `initial` | `4.68` | `50-0-0` | `44634` |
| `improved-v0` | `4.70` | `50-0-0` | `43242` |
| `improved-v2` | `4.38` | `49-1-0` | `76391` |
| `improved-v3` | `3.04` | `48-0-2` | `137816` |
| `improved-v4` | `2.40` | `44-0-6` | `143709` |
| `improved-v5` | `1.22` | `32-7-11` | `149402` |
| `improved-v6` | `1.28` | `32-7-11` | `149402` |

## Failure Analysis

The candidate is not just a built-in-only artifact: it was checked against the
fixed archived opponent pool on the same development seeds. It preserves the
`builtin` row while keeping clean wins on the weak archived opponents and
slightly improving the hard archived tail versus the older `rally-serve`
reference recorded in prior notes.

The remaining weakness is concentrated in `improved-v5` and `improved-v6`.
Those rows still have `7` losses and `11` draws each, so the structural detector
does not solve late-generation archived-opponent robustness. The hard-tail
means are positive, but not strong enough to justify a final claim.

## Promotion Recommendation

Keep `post-contact` as the current development reference over `rally-serve` for
archived-opponent robustness. Do not promote it to a production/final result
from this evidence: the run is development-only, uses no holdout/audit seeds,
and the hard archived rows remain brittle.

# Generation-4 Post-Contact Front-Conversion Attempt

Date: 2026-05-27

## Scope

This is a development-only structural probe following the parallel v2 trace
diagnosis. It uses only generation-4 development seeds. No holdout, audit, or
final-evaluation seeds were used.

Important limitation: generation-4 holdout has already been consumed in prior
work, so this candidate cannot support a new generation-4 final claim. It is a
named development candidate for future protocol work, not evidence that the
heuristic system now beats the neural comparator on final evaluation.

## Seeds

Short screen: `9000..9015`.

Full development fixed-pool check: `9000..9049`.

No `10000..10049`, `11000..11049`, generation-5 holdout, or generation-5 audit
seeds were used.

## Candidate Definitions

All candidates wrapped the current `rally-serve` candidate. The maintained
policy edit adds only the best structural rule as `post-contact`.

| Candidate | Type | Definition |
| --- | --- | --- |
| `pc_gate_grounded_low_receive` | structural/history | Restore low-rescue jump behavior when `grounded_low_receive` fires without a two-frame post-contact low-ball signal. |
| `pc_gate_low_receive_and_late_guard` | structural/history | Same as above, also applied to `late_low_ball_guard`. |
| `pc_front_conversion` | structural/history | After a two-frame contact-like flip near the net, force forward+jump `101` when the ball is in a narrow low/front conversion window. |
| `pc_outbound_recover` | structural/history | After own contact on an outbound low ball, avoid risky second touch and recover home. |
| `pc_conservative_combined` | structural/history | Combine the grounded-low gate with a narrower front-conversion window. |

## Full Development Results

Seeds: `9000..9049`. Rows below are no-ledger probe rows from
`results/generation_4_post_contact_gate_probe.json`.

| Policy | Opponent | Mean | W-L-D | Steps | Override frames |
| --- | --- | ---: | --- | ---: | ---: |
| `rally_reference` | `builtin` | `0.14` | `13/8/29` | `150000` | `0` |
| `baseline_rnn` | `builtin` | `0.12` | `18/12/20` | `150000` | `0` |
| `pc_front_conversion` | `builtin` | `0.14` | `13/8/29` | `150000` | `65` |
| `pc_front_conversion` | `random` | `4.74` | `50/0/0` | `38217` | `8` |
| `pc_front_conversion` | `initial` | `4.68` | `50/0/0` | `44634` | `19` |
| `pc_front_conversion` | `improved-v0` | `4.70` | `50/0/0` | `43242` | `14` |
| `pc_front_conversion` | `improved-v2` | `4.38` | `49/1/0` | `76391` | `22` |
| `pc_front_conversion` | `improved-v3` | `3.04` | `48/0/2` | `137816` | `28` |
| `pc_front_conversion` | `improved-v4` | `2.40` | `44/0/6` | `143709` | `37` |
| `pc_front_conversion` | `improved-v5` | `1.22` | `32/7/11` | `149402` | `28` |
| `pc_front_conversion` | `improved-v6` | `1.28` | `32/7/11` | `149402` | `26` |

The registered `post-contact` policy was also verified through the normal
evaluation CLI with `--no-ledger`:

| Policy | Opponent | Mean | W-L-D | Steps |
| --- | --- | ---: | --- | ---: |
| `post-contact` | `builtin` | `0.14` | `13/8/29` | `150000` |
| `post-contact` | `improved-v3` | `3.04` | `48/0/2` | `137816` |
| `post-contact` | `improved-v6` | `1.28` | `32/7/11` | `149402` |

## Comparison

`pc_front_conversion` preserves the `rally-serve` built-in development mean
(`0.14`) and improves the hard archived tail:

| Opponent | Rally-serve | Post-contact | Delta |
| --- | ---: | ---: | ---: |
| `improved-v3` | `2.98` | `3.04` | `+0.06` |
| `improved-v4` | `2.34` | `2.40` | `+0.06` |
| `improved-v5` | `1.16` | `1.22` | `+0.06` |
| `improved-v6` | `1.22` | `1.28` | `+0.06` |

It still trails `baseline-rnn` on every archived hard row:

| Opponent | Post-contact | Baseline RNN | Delta |
| --- | ---: | ---: | ---: |
| `improved-v3` | `3.04` | `3.84` | `-0.80` |
| `improved-v4` | `2.40` | `3.26` | `-0.86` |
| `improved-v5` | `1.22` | `2.10` | `-0.88` |
| `improved-v6` | `1.28` | `2.18` | `-0.90` |

## Failure Analysis

The useful signal is narrow. Branch-local grounded-low receive gates changed
actions but exactly matched `rally-serve` outcomes, so that branch remains too
sparse for a meaningful score move. The outbound recovery idea regressed
built-in mean from `0.14` to `0.12` without hard-opponent gains, so it is not
promoted.

The front-conversion detector is the only candidate that improved archived
robustness without losing the built-in row. It works by detecting a recent
contact-like velocity flip and forcing a forward+jump conversion in a low
front-court window. The score gain is small but interpretable and structural.

The remaining gap to the neural comparator is still large on archived hard
opponents. This attempt improves the maintained heuristic frontier but does not
make the heuristic competitive with `baseline-rnn` overall.

## Code/Test Edit

Kept edit:

- Added `SlimeVolleyPostContactPolicy` in `hl_benchmark/policies/slimevolley.py`.
- Registered policy name `post-contact` in the SlimeVolley policy factory and
  evaluation CLI.
- Added a golden behavior test for the contact-flip front-conversion branch.

## Promotion Recommendation

Keep `post-contact` as a development-only structural candidate. Do not claim a
new final result, and do not open sealed holdout or audit seeds from this
generation. A future final claim needs a fresh predeclared protocol or an
already reserved clean seed range.

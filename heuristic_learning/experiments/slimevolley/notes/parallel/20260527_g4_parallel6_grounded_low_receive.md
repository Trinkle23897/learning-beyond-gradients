# Generation-4 Parallel6 Grounded Low Receive Probe

Date: 2026-05-27

Worker: B

## Protocol

This was a development-only structural branch probe for
`grounded_low_receive`, emphasizing stacked-frame and short-history evidence.
The probe used a transient inline Python harness from `heuristic_learning/`;
no maintained source, policy, test, ledger, summary, holdout, audit, or result
artifact was edited or written.

No holdout or audit seeds were used. Generation-4 holdout `10000..10049` and
generation-4 audit `11000..11049` were not run.

Short-screen seeds used exactly:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full-check seeds used exactly:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

Screen opponents: `builtin`, `improved-v4`, `improved-v5`, `improved-v6`.

Fixed development opponent pool:
`builtin`, `random`, `initial`, `improved-v0`, `improved-v2`,
`improved-v3`, `improved-v4`, `improved-v5`, `improved-v6`.

## Candidate Definitions

All probe candidates were structural/history changes layered on the current
`SlimeVolleyRallyServePolicy`. No candidate changed scalar/config constants.
The rally-serve reference itself carries prior generation-4 scalar/config
choices, but this pass did not tune them.

| Candidate | Type | Definition |
| --- | --- | --- |
| `rally_serve_reference` | reference | Current `SlimeVolleyRallyServePolicy` unchanged. |
| `post_contact_reference` | reference | Development-only `SlimeVolleyPostContactPolicy` comparator. |
| `baseline_rnn` | neural reference | Packaged SlimeVolley baseline RNN comparator. |
| `glr_stack_floor_retarget_nojump` | structural/history | When base `grounded_low_receive` fires, keep jump suppressed but retarget movement to a stacked floor-intercept estimate. |
| `glr_contact_flip_jump_restore` | structural/history | When base GLR fires and recent own-contact/upward-flip plus stacked reachability agree, restore the low-rescue jump. |
| `glr_descent_quorum_else_jump` | structural/history | Keep GLR no-jump suppression only with a stacked low-descent quorum; otherwise restore the low-rescue jump. |
| `glr_airborne_phase_gate` | structural/history | Keep GLR no-jump suppression only after agent descent/apex evidence; otherwise restore the low-rescue jump. |
| `glr_near_stacked_suppression` | structural/history | Expand GLR-like no-jump suppression to nearby low-rescue states only when stacked low descent and recent opponent-contact evidence agree. |

## Short Screen

Rows use seeds `9000..9015`. `GLR/Near` and `Changed/Overrides` are aggregate
probe counters across all four screen opponents.

| Candidate | Builtin mean W-L-D steps | v4 mean W-L-D steps | v5 mean W-L-D steps | v6 mean W-L-D steps | GLR/Near | Changed/Overrides | Decision |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| `rally_serve_reference` | `0.3125 4/0/12 48000` | `2.5625 15/0/1 44632` | `1.1250 9/3/4 48000` | `1.1875 9/3/4 48000` | `0/0` | `0/0` | reference |
| `post_contact_reference` | `0.3125 4/0/12 48000` | `2.7500 15/0/1 44527` | `1.3125 9/3/4 47686` | `1.3750 9/3/4 47686` | `0/0` | `0/0` | comparator only |
| `baseline_rnn` | `0.1250 6/4/6 48000` | `3.2500 16/0/0 40985` | `2.3125 14/1/1 46353` | `2.5625 14/1/1 45819` | `0/0` | `0/0` | neural comparator |
| `glr_stack_floor_retarget_nojump` | `0.3125 4/0/12 48000` | `2.5625 15/0/1 44632` | `1.1250 9/3/4 48000` | `1.1875 9/3/4 48000` | `31/4333` | `6/31` | reject screen-only: no built-in action change |
| `glr_contact_flip_jump_restore` | `0.3125 4/0/12 48000` | `2.5625 15/0/1 44632` | `1.1250 9/3/4 48000` | `1.1875 9/3/4 48000` | `31/4333` | `9/9` | full check |
| `glr_descent_quorum_else_jump` | `0.3125 4/0/12 48000` | `2.5625 15/0/1 44632` | `1.1250 9/3/4 48000` | `1.1875 9/3/4 48000` | `31/4333` | `4/4` | reject screen-only: no built-in action change |
| `glr_airborne_phase_gate` | `0.3125 4/0/12 48000` | `2.5625 15/0/1 44632` | `1.1250 9/3/4 48000` | `1.1875 9/3/4 48000` | `31/4333` | `23/23` | full check |
| `glr_near_stacked_suppression` | `0.3125 4/0/12 48000` | `2.5625 15/0/1 44632` | `1.1250 9/3/4 48000` | `1.1875 9/3/4 48000` | `31/4333` | `5/9` | full check |

The three expanded candidates tied the rally-serve reference on every screen
row while changing built-in actions. Because they beat `baseline_rnn` on
built-in development score in the full built-in check below, they were checked
against the fixed development opponent pool before any recommendation.

## Full Built-In Check

Rows use seeds `9000..9049` against `builtin`.

| Candidate | Mean | W-L-D | Steps | GLR/Near | Changed/Overrides | Decision |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| `rally_serve_reference` | `0.14` | `13/8/29` | `150000` | `0/0` | `0/0` | reference |
| `baseline_rnn` | `0.12` | `18/12/20` | `150000` | `0/0` | `0/0` | neural comparator |
| `glr_contact_flip_jump_restore` | `0.14` | `13/8/29` | `150000` | `30/4085` | `8/8` | fixed-pool check |
| `glr_airborne_phase_gate` | `0.14` | `13/8/29` | `150000` | `30/4085` | `16/16` | fixed-pool check |
| `glr_near_stacked_suppression` | `0.14` | `13/8/29` | `150000` | `30/4085` | `2/4` | fixed-pool check |

## Fixed Development Pool

Rows use seeds `9000..9049`. `glr_contact_flip_jump_restore`,
`glr_airborne_phase_gate`, and `glr_near_stacked_suppression` all exactly
matched the `rally_serve_reference` score, W-L-D, and step matrix below.

| Opponent | Rally and selected GLR probes mean W-L-D steps | `baseline_rnn` mean W-L-D steps |
| --- | --- | --- |
| `builtin` | `0.14 13/8/29 150000` | `0.12 18/12/20 150000` |
| `random` | `4.74 50/0/0 38217` | `4.80 50/0/0 30603` |
| `initial` | `4.68 50/0/0 44634` | `4.76 50/0/0 34004` |
| `improved-v0` | `4.70 50/0/0 43242` | `4.82 50/0/0 32843` |
| `improved-v2` | `4.38 49/1/0 76391` | `4.80 50/0/0 54551` |
| `improved-v3` | `2.98 48/0/2 138122` | `3.84 50/0/0 118182` |
| `improved-v4` | `2.34 44/0/6 143814` | `3.26 48/0/2 132511` |
| `improved-v5` | `1.16 32/7/11 149716` | `2.10 42/2/6 145370` |
| `improved-v6` | `1.22 32/7/11 149716` | `2.18 42/2/6 144837` |

Structural counters for the selected candidates on the same fixed pool:

| Opponent | `contact_flip` GLR/Near Changed/Overrides | `airborne_phase` GLR/Near Changed/Overrides | `near_stacked` GLR/Near Changed/Overrides |
| --- | --- | --- | --- |
| `builtin` | `30/4085 8/8` | `30/4085 16/16` | `30/4085 2/4` |
| `random` | `13/556 0/0` | `13/556 6/6` | `13/556 0/0` |
| `initial` | `13/777 0/0` | `13/777 6/6` | `13/777 2/2` |
| `improved-v0` | `15/727 2/2` | `15/727 8/8` | `15/727 0/0` |
| `improved-v2` | `21/1701 5/5` | `21/1701 8/8` | `21/1701 0/2` |
| `improved-v3` | `18/3034 2/2` | `18/3034 11/11` | `18/3034 2/4` |
| `improved-v4` | `16/3036 0/0` | `16/3036 9/9` | `16/3036 6/6` |
| `improved-v5` | `19/3433 4/4` | `19/3433 8/8` | `19/3433 5/9` |
| `improved-v6` | `17/3420 2/2` | `17/3420 6/6` | `17/3420 5/7` |

## Failure Analysis

The branch-local signal remains too sparse. On full built-in development seeds,
base `grounded_low_receive` occurred only `30` times in `150000` environment
steps. The broader near-GLR region was much larger (`4085` frames), but the
narrow stacked/history gates changed only `2..16` built-in actions depending
on candidate.

The stacked/history evidence itself was abundant but not decisive. In the full
built-in `glr_contact_flip_jump_restore` row, the harness counted
`13316` stacked low-descent frames, `17629` recent own-contact frames,
`23722` recent upward-flip frames, `7187` recent opponent-contact frames, and
`40454` agent-descending-history frames. Those signals rarely intersected the
actual GLR branch in a way that changed episode outcomes.

The fixed-pool result is negative despite behavior changes. The selected
candidates all preserved the built-in row and therefore satisfied the
fixed-pool guard, but they exactly matched `rally_serve_reference` on every
fixed-pool opponent. They also remained well below `baseline_rnn` on the hard
archived rows: `improved-v4` `2.34` versus `3.26`, `improved-v5` `1.16` versus
`2.10`, and `improved-v6` `1.22` versus `2.18`.

The two screen-only rejects did not provide a promotion path. `glr_stack_floor`
retargeting fired on GLR frames but changed no built-in actions, and the
descent-quorum rule also changed no built-in actions. Their hard-opponent
changes did not produce any score gain over the current reference.

## Promotion Recommendation

Do not promote any `grounded_low_receive` candidate from this pass.

This is structural/history negative evidence, not scalar/config evidence.
The best candidates only tie the current rally-serve reference after the
required fixed-pool check, and the known gap to `baseline_rnn` on hard archived
opponents remains unchanged. Further progress is more likely to come from a
higher-level rally setup or contact-quality discriminator than another local
GLR action rewrite.

# SlimeVolley Generation-4 Parallel5 Synthesis

Date: 2026-05-27

Type: development-only parallel worker synthesis

## Protocol

This synthesis combines four independent worker artifacts from the generation-4
development seed protocol. No holdout or audit seeds were used. The only seeds
used were generation-4 development seeds `9000..9049`, with short screens on
the fixed subset `9000..9015`.

Reserved seeds were not used:

- generation-4 holdout `10000..10049`
- generation-4 audit `11000..11049`
- generation-5 holdout `13000..13049`
- generation-5 audit `14000..14049`

No maintained policy, config, opponent pool, ledger, README, report generator,
or final report was changed by the workers. The worker outputs are append-only
notes/reports:

- `notes/parallel/20260527_g4_parallel5_attack_scalar.md`
- `notes/parallel/20260527_g4_parallel5_grounded_low_receive.md`
- `notes/parallel/20260527_g4_parallel5_rear_wall_press.md`
- `reports/parallel/20260527_g4_parallel5_trace_attack_rnn.md`

## Comparison Table

| Worker | Family | Type | Seeds | Best candidate | Key score evidence | Fixed-pool / robustness outcome | Recommendation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | attack scalar/config search | scalar/config tuning | screen `9000..9015`; full `9000..9049` for selected rows | `rally_attack_like` config under `attack` | full built-in dev mean `-0.06`, W-L-D `10-13-27`, `150000` steps | below `baseline-rnn` built-in mean `0.12` and below `rally-serve` mean `0.14`; tied or below `rally-serve` on hard archived rows | no promotion |
| B | grounded-low-receive stacked-history probes | structural policy improvement | screen `9000..9015` | `glr_stacked_target_jump` | built-in mean `0.3125`, W-L-D `4/0/12`, `48000` steps, tied reference | tied `rally-serve` on `improved-v4/v5/v6`; below `post-contact`; GLR fired only a few frames | no promotion |
| C | rear-wall press probes | structural policy improvement | screen `9000..9015` | `rw_press_low_close_jump` | built-in mean `0.3125`, W-L-D `4-0-12`, `48000` steps; improved `improved-v4` to `2.6875` | regressed `improved-v5` and `improved-v6`; no full-pool expansion | no promotion |
| D | attack vs baseline-rnn traces | logging/diagnostics | screen `9000..9015` | diagnostic only | `attack` mean `-0.125`, W-L-D `2/4/10`; `baseline-rnn` mean `0.125`, W-L-D `6/4/6`; `rally-serve` and `post-contact` mean `0.3125`, W-L-D `4/0/12` | losses concentrated in low receive and rear-wall recovery, not late-contact attack overcommit | no promotion |

## Synthesis

The parallel pass did not find a promotable candidate.

The scalar search around `attack` produced a real development improvement over
the registered `attack` policy, but the best row was still below both the
neural comparator and the already-known `rally-serve` candidate on the built-in
full development seeds. Because it is scalar/config tuning only and does not
beat the existing structural-plus-scalar candidate, it should stay diagnostic.

The grounded-low-receive branch probes showed that stacked-frame features are
available and can change actions, but the branch is too sparse in the short
screen to move outcomes. The safest interventions tied the reference. The only
movement was negative when a no-op brace rewrite introduced a built-in loss.

The rear-wall pass found one narrow structural rule that tied built-in and
improved `improved-v4`, but it regressed the harder `improved-v5` and
`improved-v6` rows. This is exactly the brittleness the opponent-pool protocol
is meant to catch, so it should not be promoted.

The trace worker explains why branch-local patches are stalling: on `9000..9015`
the `attack` gap is not mainly a late-contact attack bug. The remaining gap is
split between low-receive/rear-wall defensive recovery and failure to convert
drawn rallies into wins. `baseline-rnn` is much more active with `101` and `110`
actions, while the transparent heuristics remain comparatively passive outside
their narrow branches.

## Cost Accounting

Upper-bound scheduled step budget from preserved parallel5 artifacts:

- Attack scalar/config screen and follow-ups: `6,336,000` scheduled steps (`19 * 3 * 16 * 3000` short-screen steps, `6 * 50 * 3000` built-in full-dev steps, and `2 * 9 * 50 * 3000` fixed-pool follow-up steps).
- Grounded-low-receive screen: `1,728,000` scheduled steps (`9 * 4 * 16 * 3000`).
- Rear-wall press screen: `1,344,000` scheduled steps (`7 * 4 * 16 * 3000`).
- Trace diagnostic: `192,000` scheduled steps (`4 * 16 * 3000`).

Total upper-bound scheduled budget: `9,600,000` environment steps. Actual
observed steps are lower for rows where episodes ended before the 3000-step
limit, but the unledgered workers did not emit one combined machine-readable
cost file. LLM token cost remains unavailable.

## Decision

Do not make a maintained policy/config/test edit from this batch.

The evidence supports the following next experiment direction, but not an
immediate promotion:

1. Design a new structural phase classifier that acts earlier than isolated
   `grounded_low_receive` and `rear_wall_press` branches.
2. Treat it as a fresh development-only probe using `9000..9015` first.
3. Require fixed-pool generation-4 development checks on `9000..9049` before
   any future holdout use.
4. Keep the candidate interpretable: named phases such as `neutral_rally`,
   `pressure_convert`, `low_defense`, `rear_wall_recover`, and `reset_serve`.

This batch weakens the idea that another local threshold tweak around `attack`,
`grounded_low_receive`, or `rear_wall_press` is enough to close the
`baseline-rnn` gap. It does not weaken the broader heuristic-learning program:
the run preserved auditability, separated scalar and structural evidence, and
prevented built-in-only improvements from being promoted.

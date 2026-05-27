# Generation-4 Attack Scalar/Config Subagent

Date: 2026-05-27

Worker: A

## Protocol

No holdout or audit seeds were run or used. I did not run `slimevolley-final-eval`.
All probes were no-ledger development calls to `evaluate_slimevolley(..., ledger_path=None, summary_path=None)`.

Short-screen seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015`

Full-check seeds:

`9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007, 9008, 9009, 9010, 9011, 9012, 9013, 9014, 9015, 9016, 9017, 9018, 9019, 9020, 9021, 9022, 9023, 9024, 9025, 9026, 9027, 9028, 9029, 9030, 9031, 9032, 9033, 9034, 9035, 9036, 9037, 9038, 9039, 9040, 9041, 9042, 9043, 9044, 9045, 9046, 9047, 9048, 9049`

All evaluated candidates used policy `attack` against opponent `builtin`. Candidate configs were full config dictionaries preserving current `attack`/`improved-tuned` scalars, plus only the listed scalar/config deltas. This matters because a partial `config-json` for `attack` would otherwise reset unspecified fields to raw `SlimeVolleyConfig` defaults.

Base preserved config:

- `x_margin=0.04`
- `contact_x_window=0.14`
- `high_arc_horizon=0.85`
- `overcommit_guard_x=0.18`
- `low_ball_rescue_x_window=0.72`
- `low_ball_rescue_horizon=0.06`
- `grounded_low_receive_airborne_margin=0.12`
- `late_attack_y_min=0.28`
- `late_attack_y_max=0.65`
- `late_attack_vx=-0.35`
- `late_attack_vy=-0.10`
- `late_attack_dx_min=0.04`
- `late_attack_dx_max=0.28`

`scalar` means one numeric field changed from the base. `config` means multiple numeric fields changed. No policy, source, or test files were edited.

## References

| Seeds | Policy | Opponent | Mean | W-L-D | Steps |
| --- | --- | --- | ---: | --- | ---: |
| `9000..9015` | `attack_current` | `builtin` | `-0.1250` | `2-4-10` | `48000` |
| `9000..9015` | `baseline-rnn` | `builtin` | `0.1250` | `6-4-6` | `48000` |
| `9000..9049` | `attack_current` | `builtin` | `-0.30` | `7-18-25` | `150000` |
| `9000..9049` | `baseline-rnn` | `builtin` | `0.12` | `18-12-20` | `150000` |

## Short Screen

Opponent: `builtin`. Policy: `attack`. Episodes: `16`.

| Candidate | Kind | Delta from base | Mean | W-L-D | Steps |
| --- | --- | --- | ---: | --- | ---: |
| `higharc_0.75` | scalar | `high_arc_horizon=0.75` | `-0.1875` | `2-6-8` | `48000` |
| `higharc_0.80` | scalar | `high_arc_horizon=0.80` | `-0.3125` | `2-6-8` | `48000` |
| `higharc_0.90` | scalar | `high_arc_horizon=0.90` | `0.1250` | `4-3-9` | `48000` |
| `higharc_0.95` | scalar | `high_arc_horizon=0.95` | `0.1250` | `4-2-10` | `48000` |
| `higharc_1.05` | scalar | `high_arc_horizon=1.05` | `0.0000` | `4-4-8` | `48000` |
| `higharc_1.15` | scalar | `high_arc_horizon=1.15` | `-0.0625` | `4-5-7` | `48000` |
| `guard_0.12` | scalar | `overcommit_guard_x=0.12` | `-0.3125` | `1-6-9` | `48000` |
| `guard_0.14` | scalar | `overcommit_guard_x=0.14` | `-0.3125` | `1-6-9` | `48000` |
| `guard_0.16` | scalar | `overcommit_guard_x=0.16` | `-0.3125` | `1-6-9` | `48000` |
| `guard_0.20` | scalar | `overcommit_guard_x=0.20` | `-0.1250` | `2-4-10` | `48000` |
| `guard_0.22` | scalar | `overcommit_guard_x=0.22` | `-0.5000` | `1-6-9` | `48000` |
| `guard_0.24` | scalar | `overcommit_guard_x=0.24` | `-0.5000` | `2-9-5` | `48000` |
| `guard_0.28` | scalar | `overcommit_guard_x=0.28` | `-1.2500` | `0-9-7` | `46979` |
| `grounded_margin_0.05` | scalar | `grounded_low_receive_airborne_margin=0.05` | `-0.1250` | `2-4-10` | `48000` |
| `grounded_margin_0.08` | scalar | `grounded_low_receive_airborne_margin=0.08` | `-0.1250` | `2-4-10` | `48000` |
| `grounded_margin_0.10` | scalar | `grounded_low_receive_airborne_margin=0.10` | `-0.1250` | `2-4-10` | `48000` |
| `grounded_margin_0.14` | scalar | `grounded_low_receive_airborne_margin=0.14` | `-0.1250` | `2-4-10` | `48000` |
| `grounded_margin_0.16` | scalar | `grounded_low_receive_airborne_margin=0.16` | `-0.1250` | `2-4-10` | `48000` |
| `grounded_margin_0.20` | scalar | `grounded_low_receive_airborne_margin=0.20` | `-0.1250` | `2-4-10` | `48000` |
| `grounded_margin_0.24` | scalar | `grounded_low_receive_airborne_margin=0.24` | `-0.1250` | `2-4-10` | `48000` |
| `grounded_margin_0.28` | scalar | `grounded_low_receive_airborne_margin=0.28` | `-0.1250` | `2-4-10` | `48000` |
| `late_vx_-0.20` | scalar | `late_attack_vx=-0.20` | `-0.1250` | `2-4-10` | `48000` |
| `late_vx_-0.25` | scalar | `late_attack_vx=-0.25` | `-0.1250` | `2-4-10` | `48000` |
| `late_vx_-0.30` | scalar | `late_attack_vx=-0.30` | `-0.1250` | `2-4-10` | `48000` |
| `late_vx_-0.40` | scalar | `late_attack_vx=-0.40` | `-0.0625` | `2-3-11` | `48000` |
| `late_vx_-0.45` | scalar | `late_attack_vx=-0.45` | `-0.1250` | `2-4-10` | `48000` |
| `late_vx_-0.50` | scalar | `late_attack_vx=-0.50` | `-0.1250` | `2-4-10` | `48000` |
| `late_vx_-0.60` | scalar | `late_attack_vx=-0.60` | `-0.1250` | `2-4-10` | `48000` |
| `late_vy_-0.02` | scalar | `late_attack_vy=-0.02` | `-0.1250` | `2-4-10` | `48000` |
| `late_vy_-0.05` | scalar | `late_attack_vy=-0.05` | `-0.1250` | `2-4-10` | `48000` |
| `late_vy_-0.15` | scalar | `late_attack_vy=-0.15` | `-0.1875` | `2-5-9` | `48000` |
| `late_vy_-0.20` | scalar | `late_attack_vy=-0.20` | `-0.2500` | `1-5-10` | `48000` |
| `late_vy_-0.25` | scalar | `late_attack_vy=-0.25` | `-0.2500` | `1-5-10` | `48000` |
| `late_vy_-0.35` | scalar | `late_attack_vy=-0.35` | `-0.2500` | `1-5-10` | `48000` |
| `late_vy_-0.45` | scalar | `late_attack_vy=-0.45` | `-0.2500` | `1-5-10` | `48000` |
| `late_dx_min_0.00` | scalar | `late_attack_dx_min=0.00` | `-0.1875` | `1-4-11` | `48000` |
| `late_dx_min_0.02` | scalar | `late_attack_dx_min=0.02` | `-0.1250` | `2-4-10` | `48000` |
| `late_dx_min_0.06` | scalar | `late_attack_dx_min=0.06` | `-0.1875` | `2-5-9` | `48000` |
| `late_dx_min_0.08` | scalar | `late_attack_dx_min=0.08` | `-0.4375` | `1-7-8` | `48000` |
| `late_dx_min_0.10` | scalar | `late_attack_dx_min=0.10` | `-0.6250` | `0-9-7` | `48000` |
| `late_dx_min_0.14` | scalar | `late_attack_dx_min=0.14` | `-0.3125` | `1-6-9` | `48000` |
| `late_dx_max_0.20` | scalar | `late_attack_dx_max=0.20` | `-0.0625` | `2-3-11` | `48000` |
| `late_dx_max_0.24` | scalar | `late_attack_dx_max=0.24` | `-0.0625` | `2-3-11` | `48000` |
| `late_dx_max_0.32` | scalar | `late_attack_dx_max=0.32` | `-0.1250` | `2-4-10` | `48000` |
| `late_dx_max_0.36` | scalar | `late_attack_dx_max=0.36` | `-0.1250` | `2-4-10` | `48000` |
| `late_dx_max_0.42` | scalar | `late_attack_dx_max=0.42` | `-0.1250` | `2-4-10` | `48000` |
| `late_dx_max_0.48` | scalar | `late_attack_dx_max=0.48` | `-0.1250` | `2-4-10` | `48000` |
| `late_dx_max_0.56` | scalar | `late_attack_dx_max=0.56` | `-0.1250` | `2-4-10` | `48000` |
| `late_dx_max_0.64` | scalar | `late_attack_dx_max=0.64` | `-0.1250` | `2-4-10` | `48000` |
| `late_y_min_0.20` | scalar | `late_attack_y_min=0.20` | `-0.1250` | `2-4-10` | `48000` |
| `late_y_min_0.24` | scalar | `late_attack_y_min=0.24` | `-0.1250` | `2-4-10` | `48000` |
| `late_y_min_0.32` | scalar | `late_attack_y_min=0.32` | `-0.1250` | `2-4-10` | `48000` |
| `late_y_min_0.36` | scalar | `late_attack_y_min=0.36` | `-0.1250` | `2-4-10` | `48000` |
| `late_y_min_0.40` | scalar | `late_attack_y_min=0.40` | `-0.1250` | `2-4-10` | `48000` |
| `late_y_max_0.55` | scalar | `late_attack_y_max=0.55` | `-0.3125` | `0-4-12` | `48000` |
| `late_y_max_0.60` | scalar | `late_attack_y_max=0.60` | `-0.4375` | `0-6-10` | `48000` |
| `late_y_max_0.70` | scalar | `late_attack_y_max=0.70` | `-0.3750` | `2-8-6` | `48000` |
| `late_y_max_0.75` | scalar | `late_attack_y_max=0.75` | `-0.4375` | `2-8-6` | `48000` |
| `late_y_max_0.85` | scalar | `late_attack_y_max=0.85` | `-0.2500` | `4-6-6` | `48000` |
| `old_attack_scalar_base` | config | `high_arc_horizon=0.95`, `overcommit_guard_x=0.20`, `grounded_low_receive_airborne_margin=0.16`, `late_attack_vx=-0.45` | `0.1875` | `4-1-11` | `48000` |
| `old_base_dx48` | config | `high_arc_horizon=0.95`, `overcommit_guard_x=0.20`, `grounded_low_receive_airborne_margin=0.16`, `late_attack_vx=-0.45`, `late_attack_dx_max=0.48` | `0.1875` | `4-1-11` | `48000` |
| `wider_attack_window` | config | `late_attack_y_min=0.24`, `late_attack_y_max=0.75`, `late_attack_vx=-0.25`, `late_attack_vy=-0.05`, `late_attack_dx_min=0.02`, `late_attack_dx_max=0.42` | `-0.3125` | `2-7-7` | `48000` |
| `strict_fast_contact` | config | `late_attack_vx=-0.45`, `late_attack_vy=-0.20`, `late_attack_dx_min=0.06`, `late_attack_dx_max=0.24` | `-0.2500` | `1-5-10` | `48000` |
| `fast_wide_dx` | config | `late_attack_vx=-0.45`, `late_attack_vy=-0.10`, `late_attack_dx_min=0.02`, `late_attack_dx_max=0.48` | `-0.1250` | `2-4-10` | `48000` |
| `low_early_contact` | config | `late_attack_y_min=0.20`, `late_attack_y_max=0.55`, `late_attack_vx=-0.35`, `late_attack_vy=-0.05`, `late_attack_dx_max=0.36` | `-0.5000` | `0-5-11` | `48000` |
| `high_guard_margin` | config | `high_arc_horizon=0.95`, `overcommit_guard_x=0.22`, `grounded_low_receive_airborne_margin=0.16`, `late_attack_vx=-0.45` | `-0.4375` | `1-6-9` | `48000` |
| `front_guard_fast` | config | `overcommit_guard_x=0.14`, `late_attack_vx=-0.45`, `late_attack_vy=-0.20`, `late_attack_dx_max=0.36` | `-0.3125` | `1-6-9` | `48000` |
| `defensive_margin_wide_dx` | config | `overcommit_guard_x=0.20`, `grounded_low_receive_airborne_margin=0.16`, `late_attack_dx_min=0.02`, `late_attack_dx_max=0.42` | `-0.1250` | `2-4-10` | `48000` |
| `loose_vx_tight_dx` | config | `late_attack_vx=-0.25`, `late_attack_vy=-0.05`, `late_attack_dx_min=0.08`, `late_attack_dx_max=0.24` | `-0.3750` | `1-6-9` | `48000` |
| `strict_vy_wide_y` | config | `late_attack_y_min=0.20`, `late_attack_y_max=0.75`, `late_attack_vy=-0.25`, `late_attack_dx_max=0.42` | `-0.3125` | `2-7-7` | `48000` |

## Full Checks

Top short-screen candidates plus near-miss scalar controls were checked on all generation-4 built-in dev seeds `9000..9049`.

| Candidate | Kind | Delta from base | Mean | W-L-D | Steps | Beats `baseline-rnn` full built-in dev mean `0.12`? |
| --- | --- | --- | ---: | --- | ---: | --- |
| `attack_current` | reference | none | `-0.30` | `7-18-25` | `150000` | no |
| `baseline-rnn` | reference | none | `0.12` | `18-12-20` | `150000` | comparator |
| `higharc_0.90` | scalar | `high_arc_horizon=0.90` | `-0.22` | `10-18-22` | `150000` | no |
| `higharc_0.95` | scalar | `high_arc_horizon=0.95` | `-0.16` | `10-14-26` | `150000` | no |
| `late_vx_-0.40` | scalar | `late_attack_vx=-0.40` | `-0.28` | `7-17-26` | `150000` | no |
| `late_dx_max_0.20` | scalar | `late_attack_dx_max=0.20` | `-0.28` | `7-17-26` | `150000` | no |
| `late_dx_max_0.24` | scalar | `late_attack_dx_max=0.24` | `-0.28` | `7-17-26` | `150000` | no |
| `higharc_1.05` | scalar | `high_arc_horizon=1.05` | `-0.20` | `10-15-25` | `150000` | no |
| `old_attack_scalar_base` | config | `high_arc_horizon=0.95`, `overcommit_guard_x=0.20`, `grounded_low_receive_airborne_margin=0.16`, `late_attack_vx=-0.45` | `-0.10` | `11-13-26` | `150000` | no |
| `old_base_dx48` | config | `high_arc_horizon=0.95`, `overcommit_guard_x=0.20`, `grounded_low_receive_airborne_margin=0.16`, `late_attack_vx=-0.45`, `late_attack_dx_max=0.48` | `-0.10` | `11-13-26` | `150000` | no |

No scalar or config candidate beat `baseline-rnn` on built-in full dev. Therefore I did not run the fixed development opponent-pool promotion check.

## Failure Analysis

The short screen was optimistic. The best short candidates, `old_attack_scalar_base` and `old_base_dx48`, reached `0.1875` on seeds `9000..9015`, mostly by reducing early losses. On the full dev set they fell to `-0.10`, improving over `attack_current` by `+0.20` but remaining `0.22` below `baseline-rnn`.

The strongest single scalar was `high_arc_horizon=0.95`, which improved full dev from `-0.30` to `-0.16`. This is a real built-in dev improvement, but it still has `14` losses and only `10` wins across `50` seeds. It does not solve the late-return placement gap.

Most direct late-attack threshold changes were neutral or harmful. Tightening `late_attack_dx_max` or `late_attack_vx` reduced a few short-screen losses but did not hold up on full dev. Wider/taller late-attack windows, especially larger `late_attack_y_max`, added losses. This suggests the late-contact attack rule is already narrow for a reason: broadening it often fires into bad contact geometry.

`grounded_low_receive_airborne_margin` was effectively inert on the short subset across `0.05..0.28`, producing identical results to `attack_current`. `overcommit_guard_x` above `0.20` was clearly harmful, and lower guards did not help.

This remains built-in-only development evidence. Since no full-dev candidate exceeded the neural comparator, a fixed opponent-pool check was not triggered, and no holdout or audit use is justified.

## Promotion Recommendation

Do not promote a new `attack` scalar/config candidate from this worker run.

Best built-in full-dev candidate: tie between `old_attack_scalar_base` and `old_base_dx48`, both `-0.10`, `11-13-26`, `150000` steps on seeds `9000..9049`. They improve over `attack_current` but do not beat `baseline-rnn` on the same built-in dev seeds. Keep them as development notes only, not promotion candidates.

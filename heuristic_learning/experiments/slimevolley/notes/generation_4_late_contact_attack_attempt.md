# Generation-4 Late-Contact Attack Attempt

Date: 2026-05-26

This note records a structural SlimeVolley candidate named `attack`. It extends `improved-tuned` v2 with one narrow rule: when a low descending ball is already moving toward the opponent and the agent is slightly behind the contact point, drive forward+jump (`101`) to attempt an active return.

## Rule

The candidate fires when all conditions are true:

- `ball_x > 0.05`
- `0.28 <= ball_y <= 0.65`
- `ball_vx < -0.35`
- `ball_vy < -0.10`
- `0.04 <= agent_x - ball_x <= 0.28`

The action is `101` (`forward + jump`). No neural policy is called at runtime.

## Development Results

Fixed development evaluation used seeds `9000..9049`, 50 episodes per opponent.

| Opponent | Improved-tuned v2 mean | Attack mean | Delta | Attack W/L/D |
| --- | ---: | ---: | ---: | --- |
| builtin | -0.44 | -0.30 | +0.14 | 7/18/25 |
| random | 4.66 | 4.80 | +0.14 | 50/0/0 |
| initial | 4.56 | 4.70 | +0.14 | 50/0/0 |
| improved-v0 | 4.60 | 4.74 | +0.14 | 50/0/0 |
| improved-v2 | 4.38 | 4.36 | -0.02 | 49/1/0 |
| improved-v3 | 2.38 | 2.62 | +0.24 | 46/1/3 |
| improved-v4 | 2.08 | 2.16 | +0.08 | 40/3/7 |
| improved-v5 | 1.22 | 1.08 | -0.14 | 30/8/12 |
| improved-v6 | 1.20 | 1.06 | -0.14 | 30/8/12 |

## Interpretation

The rule is real structural progress against the built-in opponent and several archived opponents, but it is not sufficient for the goal. Built-in mean is still below `baseline-rnn` mean `0.12`, with a remaining gap of `0.42`. The candidate also regresses the nearest archived opponents `improved-v5` and `improved-v6` compared with `improved-tuned` v2.

Decision: keep `attack` as an auditable partial structural candidate. Do not promote it over `improved-tuned` v2 and do not open generation-4 holdout. The next structural direction should target active return placement without sacrificing the closest archived-policy regression checks.

## Cost And Failed Probe Notes

Before this candidate was added, dev-only throwaway low-left receive probes tested eight fixed 50-seed variants and did not improve over scalar v1; those probes consumed 400 episodes and 1,198,176 environment steps. Additional scalar refinement searched 121 short-subset candidates plus 12 full validations, then 132 full-seed refined candidates. Those exploratory search costs were not persisted row-by-row in the ledger, which is a cost-accounting weakness; the promoted v2 and `attack` fixed-pool evaluations are ledgered explicitly.

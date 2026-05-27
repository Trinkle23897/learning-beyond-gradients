# SlimeVolley Generation-4 Temporal History Attempt

Development-only report for the stacked-frame/short-history SlimeVolley heuristic attempt. No generation-4 holdout or audit seeds were inspected.

## What Changed

- Added policy name `temporal` in `hl_benchmark/policies/slimevolley.py`.
- The policy keeps a rolling observation/action history of up to 8 frames.
- It derives explicit features: finite-difference ball motion, velocity-flip contact detectors, upward-flip detection, and trajectory reliability.
- The final simplified controller uses history for opponent/self contact detection and post-contact/intercept phases, while preserving urgent single-frame low-ball, floor-intercept, and rear-wall guards.
- The current `improved` policy was not replaced. `temporal` remains a generation-4 candidate because evidence is mixed.

## Failed / Revised Sub-Hypotheses

| Timestamp | Built-in mean | W/L/D | Change | Failure analysis |
| --- | ---: | --- | --- | --- |
| 2026-05-26T06:33:11+00:00 | -4.80 | 0/10/0 | Generation-4 temporal stacked-history candidate: contact-flip features, finite-difference trajectory signals, and jump cooldown. | Initial pre-diagnosis row; later comparison showed this version underperformed the same-seed current-improved control. |
| 2026-05-26T06:34:58+00:00 | -4.80 | 0/10/0 | Revise temporal stacked-history candidate: disable cooldown suppression after first dev trace showed lost reachable contacts; keep contact-flip and finite-difference history features. | Prior temporal trial underperformed current improved on builtin dev seeds because jump actions were much rarer; cooldown guard was over-constraining contact attempts. |
| 2026-05-26T06:37:01+00:00 | -4.00 | 0/10/0 | Revise temporal stacked-history candidate: urgent low-ball/floor/rear-wall guards now take priority over contact-flip intercept mode. | Previous temporal revision still underperformed builtin dev control; trace showed opponent-contact intercept overriding low-ball rescue on reachable low balls. |
| 2026-05-26T06:38:54+00:00 | -3.90 | 0/10/0 | Simplify temporal stacked-history candidate: remove broad uncertain-trajectory and upward-flip recovery overrides; keep contact-flip intercept and urgent safety guards. | Safety-priority temporal policy nearly matched but did not beat current improved on builtin dev seeds; broad recovery modes were not clearly tied to losses and added mode complexity. |

Interpretation: the first cooldown version reduced reachable contact attempts and performed poorly. Disabling cooldown alone did not fix the issue. Trace inspection then showed temporal intercept overriding low-ball rescue; putting urgent guards first restored most of the gap. Removing broad trajectory-recovery overrides simplified the policy and tied the same 10-seed built-in control.

## Full Development-Seed Comparison

Seeds: `9000..9049`. Episodes: 50 per policy/opponent cell. Split: generation-4 development only.

| Opponent | Improved mean | Temporal mean | Delta | Improved W/L/D | Temporal W/L/D |
| --- | ---: | ---: | ---: | --- | --- |
| builtin | -3.72 | -3.80 | -0.08 | 0/50/0 | 0/50/0 |
| random | 4.06 | 4.06 | +0.00 | 49/1/0 | 49/1/0 |
| initial | 3.94 | 3.88 | -0.06 | 49/1/0 | 49/1/0 |
| improved-v0 | 4.04 | 4.04 | +0.00 | 49/1/0 | 49/1/0 |
| improved-v2 | 3.50 | 3.54 | +0.04 | 47/3/0 | 48/2/0 |
| improved-v3 | 0.22 | 0.30 | +0.08 | 23/23/4 | 25/21/4 |

## Aggregate Cost And Outcome

| Policy | Cells | Mean across opponents | Wins | Losses | Draws | Env steps | Wall-clock seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| improved | 6 | 2.007 | 217 | 79 | 4 | 452189 | 27.57 |
| temporal | 6 | 2.003 | 220 | 76 | 4 | 444980 | 36.10 |

Temporal did not produce a clean score improvement over `improved`: mean across the six development opponents is effectively tied and slightly lower by score. It did produce a small win/loss improvement across the full opponent pool: `220/76/4` versus `217/79/4`, mainly from archived heuristic opponents. Built-in performance remains worse (`-3.80` versus `-3.72`).

## Decision

- Keep `temporal` as an auditable candidate policy and opponent for further development-seed analysis.
- Do not promote it to replace `improved` yet.
- Do not open generation-4 holdout for this candidate unless a future development-only protocol shows a clear promotion criterion.

## Reproduction Commands

```bash
python3 -m pytest tests/test_slimevolley_optional.py
make PYTHON=.venv/bin/python verify
.venv/bin/python -m hl_benchmark.custom_envs.slimevolley.evaluate --policy temporal --opponent builtin --split dev --seed-start 9000 --episodes 50 --ledger experiments/slimevolley/results/generation_4_trials.jsonl --summary experiments/slimevolley/results/generation_4_summary.csv
```

## Conclusion

Stacked history helped express interpretable contact/phase logic, but the current implementation is only neutral-to-mixed on development evidence. The result supports adding temporal memory as a promising heuristic-maintenance direction, not as a proven improvement over the current SlimeVolley heuristic.

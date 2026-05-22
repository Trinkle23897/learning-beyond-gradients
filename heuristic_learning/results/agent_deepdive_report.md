# Agent Deep-Dive Report

## Executive Verdict

This generated report explains how the coding-agent experiment progressed, what evidence it produced, and where the evidence remains weak.

- Strict benchmark targets met: 4/5 (CartPole-v1, MountainCar-v0, Acrobot-v1, LunarLander-v3)
- Strict benchmark targets missed: 1/5 (BipedalWalker-v3)
- 5% tolerance targets met: 5/5 (CartPole-v1, MountainCar-v0, Acrobot-v1, LunarLander-v3, BipedalWalker-v3)
- 5% tolerance targets missed: 0/5 (none)
- Missing holdout evidence: 0/5 (none)
- Deep-RL comparisons are secondary comparators; benchmark solved-score targets are the primary cutoff.

## Benchmark Outcome

| Environment | Best transparent holdout policy | Mean | Strict target | Strict pass? | 5% cutoff | 5% pass? |
| --- | --- | ---: | ---: | --- | ---: | --- |
| CartPole-v1 | initial | 500 | 475 | yes | 451.25 | yes |
| MountainCar-v0 | improved | -107.64 | -110 | yes | -115.5 | yes |
| Acrobot-v1 | tree | -87.74 | -100 | yes | -105 | yes |
| LunarLander-v3 | tuned | 274.877 | 200 | yes | 190 | yes |
| BipedalWalker-v3 | improved | 294.426 | 300 | no | 285 | yes |

## How The Agent Worked

Each meaningful trial is represented as a ledger row with a change type, diagnosis, next hypothesis, cost fields, and fixed seed range. The practical loop was: evaluate, inspect reward summaries and failures, edit policy/config/tests, run checks, re-evaluate, and preserve unsuccessful attempts as non-pass or diagnostic rows.

### Process By Environment

| Environment | Trials | Dev | Holdout | Audit | Structural | Scalar | RL | Partial/non-pass | First trial | Last trial |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| CartPole-v1 | 19 | 13 | 6 | 0 | 5 | 9 | 2 | 1 | 2026-05-20T06:12:15+00:00 | 2026-05-21T03:49:09+00:00 |
| MountainCar-v0 | 22 | 14 | 8 | 0 | 7 | 9 | 3 | 1 | 2026-05-20T06:12:16+00:00 | 2026-05-21T06:04:10+00:00 |
| Acrobot-v1 | 622 | 611 | 11 | 0 | 10 | 604 | 2 | 2 | 2026-05-20T06:12:18+00:00 | 2026-05-21T04:54:26+00:00 |
| LunarLander-v3 | 23 | 13 | 10 | 0 | 5 | 9 | 6 | 1 | 2026-05-20T06:12:20+00:00 | 2026-05-21T06:55:07+00:00 |
| BipedalWalker-v3 | 42 | 29 | 12 | 1 | 14 | 21 | 4 | 4 | 2026-05-20T06:12:38+00:00 | 2026-05-21T07:20:45+00:00 |

### Change-Type Counts

- bug fix: 1
- invalid/rolled back: 6
- logging/diagnostics change: 11
- rl/deep learning baseline: 17
- scalar/config tuning: 652
- structural policy improvement: 41

## Structural, Scalar, Teacher-Distilled, And RL Evidence

This table separates result families so scalar tuning and teacher distillation are not misreported as purely hand-written structural policy improvement.

| Environment | Initial | Structural improved | Scalar tuned | Teacher-distilled tree | Best recorded RL |
| --- | ---: | ---: | ---: | ---: | ---: |
| CartPole-v1 | initial 500 | improved 500 | tuned 500 |  | rl-ppo 500 |
| MountainCar-v0 | initial -117.98 | improved -107.64 | tuned -117.98 |  | rl-dqn -104.34 |
| Acrobot-v1 | initial -141.6 | improved -123.58 | tuned -106.16 | tree -87.74 | rl-ppo -84.68 |
| LunarLander-v3 | initial 199.131 | improved 148.788 | tuned 274.877 |  | rl-dqn 276.883 |
| BipedalWalker-v3 | initial -129.216 | improved 294.426 | tuned -120.945 |  | rl-sac-hf 300.773 |

## Deep-RL Secondary Comparator

This section is intentionally secondary. It answers whether the best transparent result looked similar to the best recorded RL comparator, not whether the benchmark was solved.

| Environment | Best transparent | Transparent mean | Best recorded RL | RL mean | Strict gap | Comparator status |
| --- | --- | ---: | --- | ---: | ---: | --- |
| CartPole-v1 | initial | 500 | rl-ppo | 500 | 0.00% | within 5% |
| MountainCar-v0 | improved | -107.64 | rl-dqn | -104.34 | 3.16% | within 5% |
| Acrobot-v1 | tree | -87.74 | rl-ppo | -84.68 | 3.61% | within 5% |
| LunarLander-v3 | tuned | 274.877 | rl-dqn | 276.883 | 0.72% | within 5% |
| BipedalWalker-v3 | improved | 294.426 | rl-sac-hf | 300.773 | 2.11% | within 5% |

## Environment Deep Dives

### CartPole-v1

- Best transparent holdout result: `initial` mean `500` against strict target `475` and 5% cutoff `451.25`.
- Structural improved policy tied the initial policy.
- Notable non-pass iterations:
  - `2026-05-20T16:04:20+00:00` `improved-v0-rejected` `partial` mean `257.3`: Rejected first structural improved policy on development seeds: mean 257.300 was below initial heuristic mean 500.000. The guard/mode changes were too aggressive and were revised conservatively before holdout evaluation.

### MountainCar-v0

- Best transparent holdout result: `improved` mean `-107.64` against strict target `-110` and 5% cutoff `-115.5`.
- Structural improved policy beat initial by `10.34` mean reward.
- Notable non-pass iterations:
  - `2026-05-20T16:04:20+00:00` `improved-v0-rejected` `partial` mean `-144.3`: Rejected first structural improved policy on development seeds: mean -144.300 was below initial heuristic mean -120.150. The guard/mode changes were too aggressive and were revised conservatively before holdout evaluation.

### Acrobot-v1

- Best transparent holdout result: `tree` mean `-87.74` against strict target `-100` and 5% cutoff `-105`.
- Structural improved policy beat initial by `18.02` mean reward.
- Best result came from an explicit decision tree distilled from a PPO teacher.
- Notable non-pass iterations:
  - `2026-05-20T16:04:20+00:00` `improved-v0-rejected` `partial` mean `-154.6`: Rejected first structural improved policy on development seeds: mean -154.600 was below initial heuristic mean -144.950. The guard/mode changes were too aggressive and were revised conservatively before holdout evaluation.
  - `2026-05-21T04:34:21+00:00` `mpc-diagnostic-rejected` `partial` mean `-100.3`: Best quick lookahead diagnostic reached only about -104 mean on 20 dev seeds, below the structural/scalar dev result and far from the PPO comparator.

### LunarLander-v3

- Best transparent holdout result: `tuned` mean `274.877` against strict target `200` and 5% cutoff `190`.
- Structural improved policy regressed versus initial by `50.343` mean reward.
- Best result came from scalar/config tuning, not a structural policy edit.
- Notable non-pass iterations:
  - `2026-05-20T16:04:20+00:00` `improved-v0-rejected` `partial` mean `164.398`: Rejected first structural improved policy on development seeds: mean 164.398 was below initial heuristic mean 210.007. The guard/mode changes were too aggressive and were revised conservatively before holdout evaluation.

### BipedalWalker-v3

- Best transparent holdout result: `improved` mean `294.426` against strict target `300` and 5% cutoff `285`.
- Structural improved policy beat initial by `423.642` mean reward.
- Strict benchmark target is not met; only tolerance or comparator claims are justified.
- Notable non-pass iterations:
  - `2026-05-20T16:04:20+00:00` `improved-v0-rejected` `partial` mean `-138.384`: Rejected first structural improved policy on development seeds: mean -138.384 was below initial heuristic mean -129.395. The guard/mode changes were too aggressive and were revised conservatively before holdout evaluation.
  - `2026-05-21T05:36:27+00:00` `bipedal-state-machine-search` `partial` mean `280.321`: Search improved BipedalWalker dramatically, but the scratch diagnostic did not record aggregate environment steps, so this ledger row is marked partial and the selected controller is re-evaluated through the normal harness in adjacent rows.
  - `2026-05-21T05:52:58+00:00` `bipedal-speed-scale-prescreen` `partial` mean `310.097`: The five-seed top config averaged above 300 but failed on the full development range, showing that short dev prescreens can overfit; aggregate environment steps were not captured by the scratch diagnostic.
  - `2026-05-21T07:08:01+00:00` `bipedal-robustness-sweep` `partial` mean `295.414`: The scratch sweep found prior fast settings were brittle and did not capture aggregate environment steps, so this row is partial; selected constants were re-evaluated through the normal harness on dev and audit splits.

## Non-Pass And Partial Iterations

| Timestamp | Environment | Policy | Status | Mean | Steps | Failure analysis |
| --- | --- | --- | --- | ---: | ---: | --- |
| 2026-05-20T16:04:20+00:00 | CartPole-v1 | improved-v0-rejected | partial | 257.3 | 5146 | Rejected first structural improved policy on development seeds: mean 257.300 was below initial heuristic mean 500.000. The guard/mode changes were too aggressive and were revised conservatively before holdout evaluation. |
| 2026-05-20T16:04:20+00:00 | MountainCar-v0 | improved-v0-rejected | partial | -144.3 | 2886 | Rejected first structural improved policy on development seeds: mean -144.300 was below initial heuristic mean -120.150. The guard/mode changes were too aggressive and were revised conservatively before holdout evaluation. |
| 2026-05-20T16:04:20+00:00 | Acrobot-v1 | improved-v0-rejected | partial | -154.6 | 3112 | Rejected first structural improved policy on development seeds: mean -154.600 was below initial heuristic mean -144.950. The guard/mode changes were too aggressive and were revised conservatively before holdout evaluation. |
| 2026-05-20T16:04:20+00:00 | LunarLander-v3 | improved-v0-rejected | partial | 164.398 | 9425 | Rejected first structural improved policy on development seeds: mean 164.398 was below initial heuristic mean 210.007. The guard/mode changes were too aggressive and were revised conservatively before holdout evaluation. |
| 2026-05-20T16:04:20+00:00 | BipedalWalker-v3 | improved-v0-rejected | partial | -138.384 | 2418 | Rejected first structural improved policy on development seeds: mean -138.384 was below initial heuristic mean -129.395. The guard/mode changes were too aggressive and were revised conservatively before holdout evaluation. |
| 2026-05-21T04:34:21+00:00 | Acrobot-v1 | mpc-diagnostic-rejected | partial | -100.3 | 2026 | Best quick lookahead diagnostic reached only about -104 mean on 20 dev seeds, below the structural/scalar dev result and far from the PPO comparator. |
| 2026-05-21T05:36:27+00:00 | BipedalWalker-v3 | bipedal-state-machine-search | partial | 280.321 | 0 | Search improved BipedalWalker dramatically, but the scratch diagnostic did not record aggregate environment steps, so this ledger row is marked partial and the selected controller is re-evaluated through the normal harness in adjacent rows. |
| 2026-05-21T05:52:58+00:00 | BipedalWalker-v3 | bipedal-speed-scale-prescreen | partial | 310.097 | 0 | The five-seed top config averaged above 300 but failed on the full development range, showing that short dev prescreens can overfit; aggregate environment steps were not captured by the scratch diagnostic. |
| 2026-05-21T07:08:01+00:00 | BipedalWalker-v3 | bipedal-robustness-sweep | partial | 295.414 | 0 | The scratch sweep found prior fast settings were brittle and did not capture aggregate environment steps, so this row is partial; selected constants were re-evaluated through the normal harness on dev and audit splits. |

## Cost And Audit Accounting

- Trials: 728
- Status counts: partial: 9, pass: 719
- Split counts: audit: 1, dev: 680, holdout: 47
- Change-type counts: bug fix: 1, invalid/rolled back: 6, logging/diagnostics change: 11, rl/deep learning baseline: 17, scalar/config tuning: 652, structural policy improvement: 41
- Episodes: 42460
- Recorded environment steps: 9502225
- Wall-clock seconds: 6295.445
- Max agent iterations recorded: 16
- Max code edits recorded: 19
- Rows with tests recorded: 54/728
- Rows with unavailable LLM token totals: 728/728
- Runs with episodes but zero recorded environment steps: 3
- Ledger git commits: d3c6593: 728
- Ledger diff identifiers: clean: 721, ae5d509d6d05: 7
- Current git status for benchmark path: `?? ./`

## Interpretation

- The strongest support is auditability: the ledger preserves successes, regressions, partial trials, and costs.
- Structural improvement is mixed: MountainCar and BipedalWalker improved clearly, CartPole was already solved, and LunarLander regressed structurally.
- The best Acrobot result is transparent at inference time but teacher-distilled, so it should be reported separately from hand-written heuristic learning.
- BipedalWalker is the strict benchmark miss: it is within 5% of the target but below the official solved-score threshold.
- Holdout reuse and limited audit coverage weaken claims of final generalization; fresh audit evaluations should be the next evidence step.


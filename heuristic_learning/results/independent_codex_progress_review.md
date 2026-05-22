**Heuristic Learning Benchmark Audit**

**Executive Verdict**

Partial pass. The benchmark is implemented and auditable, but the core hypothesis is only partly supported. Best transparent holdout results meet strict benchmark targets on 4/5 environments; `BipedalWalker-v3` misses the strict `300.0` target with `294.426`, though it is within the 5% cutoff `285.0`. Deep-RL parity is secondary, not primary.

No files were edited.

**What Was Implemented**

Implemented in [hl_benchmark](/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/hl_benchmark):

- Fixed environment registry and seed splits: dev `0..19`, holdout `1000..1049`, audit `2000..2049`.
- Transparent policies: `random`, `initial`, `improved`, `tuned`, plus Acrobot `tree`.
- Evaluation harness, append-only JSONL ledger, CSV summary, generated Markdown report.
- Scalar/config search with holdout/audit rejection.
- Optional Stable-Baselines3 / Hugging Face RL baselines.
- Tests for policy outputs, ledger/report schema, search split protection, RL helper surface, and small deterministic evals.

Artifacts inspected: [README.md](/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/README.md), [pyproject.toml](/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/pyproject.toml), [results/trials.jsonl](/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/results/trials.jsonl), [results/summary.csv](/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/results/summary.csv), [results/final_report.md](/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/results/final_report.md).

**Evidence For / Against Hypothesis**

For:

- Best transparent holdout results meet strict targets on `4/5`: CartPole `500 >= 475`, MountainCar `-107.64 >= -110`, Acrobot `-87.74 >= -100`, LunarLander `274.877 >= 200`.
- Within 5% cutoff is `5/5`, including BipedalWalker `294.426 >= 285`.
- Structural `improved` beats `initial` on holdout for `3/5`: MountainCar `+10.34`, Acrobot `+18.02`, BipedalWalker `+423.642`; CartPole ties at `500`.

Against / partial:

- LunarLander structural policy regresses: `improved 148.788` vs `initial 199.131`; the best result is scalar `tuned 274.877`.
- Acrobot’s best transparent result is `tree -87.74`, distilled from a PPO teacher, not a pure hand-written heuristic.
- BipedalWalker strict target fails on holdout and audit: holdout `294.426 < 300`, audit `287.239 < 300`.

**Failed Benchmark Target**

`BipedalWalker-v3` is the strict failed target: success target `300.0`, best transparent holdout `294.426`, audit `287.239`. It passes only the 5% tolerance cutoff.

**Deep-RL Comparison**

Secondary comparator. [README.md](/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/README.md) and [final_report.md](/home/alpha/dev/research/learning-beyond-gradients/heuristic_learning/results/final_report.md:169) both frame benchmark success targets as primary.

Recorded best transparent vs best RL holdout:

- CartPole: `500` vs `500`, gap `0.00%`.
- MountainCar: `-107.64` vs `-104.34`, gap `3.16%`.
- Acrobot: `-87.74` vs `-84.68`, gap `3.61%`.
- LunarLander: `274.877` vs `276.883`, gap `0.72%`.
- BipedalWalker: `294.426` vs pretrained `rl-sac-hf 300.773`, gap `2.11%`.

**Reproducibility / Tests**

Current verification: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 -m pytest -p no:cacheprovider tests` passed `15/15` with `11` warnings.

Ledger and summary are consistent: `728` JSONL entries and `728` CSV rows. No reserved-seed violations found. Caveat: current `git status --short` reports the benchmark directory as untracked (`?? ./` from this subdir), while all ledger rows cite commit `d3c6593`; `721/728` rows say `diff_identifier=clean`, so git provenance is weaker than the ledger suggests.

**Ledger / Cost Accounting**

From `results/trials.jsonl` and `results/final_report.md`:

- Trials: `728`
- Status: `719 pass`, `9 partial`, `0 fail`, `0 error`
- Episodes: `42,460`
- Recorded environment steps: `9,502,225`
- Wall-clock seconds: `6,295.445`
- Agent iterations max: `16`
- Code edits max: `19`
- LLM token/call fields: unavailable in all `728` rows
- `tests_run=["pytest"]` appears in `54/728` rows; `674` rows have no recorded tests.

Cost caveat: three Bipedal scratch sweeps record `3,880` episodes with `environment_steps=0`, so total environment-step accounting is an undercount.

**Major Risks / Caveats**

- Holdout has been used repeatedly: `47` holdout rows total; BipedalWalker has `12` holdout rows. Final Bipedal claims should lean on audit/new holdout, not the reused holdout.
- Audit coverage is only `1/5` environments; CartPole, MountainCar, Acrobot, and LunarLander have no audit-split evidence.
- Runtime metadata is mixed: `85` rows used Gymnasium `1.3.0` with SB3 unavailable; `643` rows used Gymnasium `1.2.3` with SB3 `2.8.0`.
- Acrobot `tree` is transparent at inference but PPO-distilled, so it should be reported separately from hand-written heuristic learning.
- The report labels `9` “failed trials,” but the raw ledger statuses are `partial`, not `fail`.

**Next Recommendations**

1. Freeze provenance first: track/commit this benchmark directory, then regenerate summary/report from a clean checkout.
2. Treat BipedalWalker strict target as failed unless the stated success criterion is explicitly changed to the 5% tolerance cutoff.
3. Run fresh audit evaluations for all five environments, preferably as the main final claim set.
4. Separate result tables into pure structural, scalar-tuned, and teacher-distilled policies.
5. Fix cost accounting for scratch sweeps and add real LLM token/call accounting when available.
6. Add regression tests for best-policy smoke/audit thresholds beyond CartPole and MountainCar.
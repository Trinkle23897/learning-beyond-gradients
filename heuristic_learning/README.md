# Heuristic Learning Benchmark

This subproject implements a minimal, auditable experiment for the
Learning Beyond Gradients / Heuristic Learning hypothesis:

> Can an autonomous coding agent maintain and improve a transparent heuristic
> control system across multiple control environments, while preserving prior
> successes through tests and reporting costs and failures honestly?

The benchmark is intentionally small. It favors reproducibility, fixed seed
ranges, append-only trial records, and readable policy code over impressive
scores.

## Setup

From this directory:

```bash
python3 -m pip install -e .
```

Box2D environments require the `gymnasium[box2d]` extra listed in
`pyproject.toml`. If the local platform cannot install Box2D, the evaluation
commands fail explicitly and record the failure instead of silently dropping the
Box2D tasks.

Optional neural/RL baseline dependencies are separate:

```bash
python3 -m pip install -e '.[rl]'
```

The primary pass/fail criterion is the fixed benchmark success target recorded for
each environment. Neural/RL runs are optional secondary comparators and are not
required for the default benchmark.

Optional pretrained SB3 comparators can be evaluated through Hugging Face Hub
when the `.[rl]` extra is installed. These runs are recorded separately from
local training runs in the ledger, for example as `rl-sac-hf`.

## Commands

```bash
make test
make eval-env ENV=CartPole-v1 POLICY=initial SPLIT=dev
make eval-all SPLIT=dev
make search MAX_CANDIDATES=32
make final-eval
make report
make deepdive-report
```

The Makefile sets `PYTHONPATH=.` so the package can run directly from the
subproject checkout.

## Outputs

Generated artifacts are written to `results/`:

- `trials.jsonl`: append-only ledger of every evaluation/search trial.
- `summary.csv`: regenerated table summarizing all ledger entries.
- `final_report.md`: Markdown report generated from the ledger and environment
  registry.
- `agent_deepdive_report.md`: generated audit of how the agent iterated,
  including failures, cost accounting, structural/scalar separation, and caveats.
- `heuristic_policy_explainer.md`: high-level visual explanation of how each
  transparent environment policy works.

Do not delete failed entries from `trials.jsonl`. If a run is invalid, append a
new entry explaining why.

## Benchmark Suite

Fixed seed splits:

- Development seeds: `0..19`
- Holdout seeds: `1000..1049`
- Audit seeds: `2000..2049`

Primary environments:

- `CartPole-v1`
- `MountainCar-v0`
- `Acrobot-v1`
- `LunarLander-v3`
- `BipedalWalker-v3`

If `BipedalWalker-v3` is unavailable but another Box2D task such as
`CarRacing-v3` is available, document the substitution in the ledger and final
report. If Box2D is unavailable entirely, install the required dependency or
record the failure.

## Policies And Baselines

Each environment has:

- `random`: random action baseline.
- `initial`: simple handwritten heuristic.
- `improved`: structural heuristic revision with explicit detectors, guards,
  modes, or state-machine behavior.
- `tuned`: scalar/config variant used by the search baseline.

Scalar search is intentionally separated from structural policy improvement.
`search.py` rejects holdout and audit splits so reserved comparison seeds cannot be used for tuning.

## Audit Rules

- Never cherry-pick seeds.
- Never optimize on holdout seeds.
- Record failed or partial trials.
- Keep initial policies callable for comparison.
- Keep policy changes interpretable.
- Report environment steps, wall time, package versions, git hash/diff hash,
  code-edit counts, agent iterations, and unavailable LLM-token fields.


# SlimeVolley Requirement Coverage Audit

This matrix maps the requested SlimeVolley heuristic-learning experiment requirements to current repository evidence. It is intentionally conservative: partially satisfied items stay marked partial rather than being treated as complete by implication.

## Verdict

Current status: runnable and auditable for the minimal SlimeVolley experiment, with mixed scientific evidence. The agent-maintained structural heuristic improves strongly over the initial handwritten heuristic and scalar-tuned baseline against random, initial, and archived heuristic opponents on generation-3 holdout seeds, including a narrow win over `improved-v3`. It remains far below the packaged RNN comparator against the built-in opponent. Holdout seeds `1000..1049`, generation-2 holdout seeds `4000..4049`, and generation-3 holdout seeds `7000..7049` are final-only evidence and must not be used for further tuning.

## Completion Checkpoint

Current completion gate for this SlimeVolley testbed is the passing artifact audit plus local verification commands, not a high-score claim. The current repo state is complete enough to review the minimal experiment because the wrapper, policies, opponent protocol, ledgers, summaries, reports, diagnostics, regression tests, and generation-3 final holdout are all present and audited.

Accepted historical caveats:

- Append-only generation-1 ledger rows predate explicit `tests_pass_fail`; `results/trial_amendments.jsonl` now records `tests_pass_fail=not_recorded` amendments keyed by row index and SHA256 hash rather than rewriting those historical trial rows.
- The neural/RL comparison requirement is satisfied by the packaged documented `baseline-rnn` comparator; no local PPO/DQN/self-play training run was performed, so local neural training remains outside this ledger.
- The maintained heuristic is not deep-RL comparable on the built-in opponent.

Do not mark the durable goal complete if future work requires a stronger SlimeVolley score, a locally trained neural baseline, video/plot replays, or a fresh generation-4 policy iteration. Those are new research extensions; the current completion gate is auditability and reproducibility of the finished generation-3 experiment.

## Machine-Readable Completion State

`experiments/slimevolley/results/audit_latest.json` currently reports the requirements audit as machine-readable status fields rather than requiring reviewers to infer completion from prose:

- `requirements_audit_completion_state`: `satisfied`
- `requirements_audit_completion_recommendation`: `eligible_for_completion_audit`
- `requirements_audit_status_counts`: `{"Satisfied": 25}`
- `requirements_audit_completion_blockers`: `[]`

There are currently no partial rows in the SlimeVolley requirement matrix. Historical caveats remain visible through raw and effective test-status counts in `audit_latest.json`.

A passing artifact audit means the evidence is internally consistent. It does not by itself claim high SlimeVolley performance or deep-RL comparability.

## Coverage Matrix

| Requirement | Current evidence | Status |
| --- | --- | --- |
| Working repository | `make verify` passes registry, artifact-layout, planned-env, and pytest gates. `make slimevolley-verify` and `make custom-verify ENV=SlimeVolley-v0` pass SlimeVolley summary/report/audit regeneration plus contact diagnostics and generation protocol refreshes. `make check-promotions` remains the documented promotion gate for all registered environments. | Satisfied |
| Reproduction instructions | `README.md`, `experiments/slimevolley/README.md`, and `experiments/slimevolley/reports/final_report.md` list setup, optional legacy Gym install, exact commands, and final-only holdout guardrails. | Satisfied |
| SlimeVolley environment wrapper or compatibility layer | `hl_benchmark/slimevolley/adapter.py` handles legacy Gym step/reset/seed behavior; `hl_benchmark/slimevolley/doctor.py` records environment diagnostics. | Satisfied |
| Exact package and runtime metadata | `experiments/slimevolley/results/environment_diagnostics.json`, ledger `runtime_metadata`, and final report dependency/runtime sections record package versions and API observations. | Satisfied |
| Initial handwritten heuristic | `hl_benchmark/policies/slimevolley.py` exposes `initial`; final report describes it as a modest landing/home/jump heuristic. | Satisfied |
| Agent-maintained heuristic policy versions | `hl_benchmark/policies/slimevolley.py` keeps `improved-v0`, `improved-v1`, `improved-v2`, `improved-v3`, and current `improved` as interpretable structural archives. | Satisfied |
| Opponent protocol | `hl_benchmark/slimevolley/opponents.py` defines `builtin`, `random`, frozen heuristic opponents, current heuristic, and `baseline-rnn`; final report contains the opponent table. | Satisfied |
| Fixed development and holdout seed ranges | `hl_benchmark.envs.SEED_SPLITS` defines generation-1 dev `0..19`, holdout `1000..1049`, and audit `2000..2049`; generation-2 protocol predeclares dev `3000..3049`, holdout `4000..4049`, and audit `5000..5049`; generation-3 protocol predeclares dev `6000..6049`, holdout `7000..7049`, and audit `8000..8049`; generation-4 protocol predeclares dev `9000..9049`, holdout `10000..10049`, and audit `11000..11049` for future work. SlimeVolley audit checks the generation seed protocols. | Satisfied |
| Append-only trial ledger | `experiments/slimevolley/results/trials.jsonl` contains 186 generation-1 rows including the initial dependency failure; `results/trial_amendments.jsonl` contains 186 append-only `tests_pass_fail=not_recorded` metadata amendments keyed to historical row indexes and SHA256 hashes; `generation_2_trials.jsonl` contains 114 rows including 25 final-only holdout rows; `generation_3_trials.jsonl` contains 303 rows including 30 final-only holdout rows. `generation_4_trials.jsonl` is intentionally absent until future generation-4 work begins under the predeclared protocol. Generation-2 and generation-3 rows record explicit test status directly. | Satisfied |
| Evaluation harness | `hl_benchmark/slimevolley/evaluate.py` records policy/opponent fixed-seed evaluations with win/loss/draw, life difference, per-episode scores, steps, action frequencies, trace windows, and costs. | Satisfied |
| Scalar/config search baseline | `hl_benchmark/slimevolley/search.py` records development-only scalar search; `search_best_dev.json`, `search_best_g2_dev.json`, and `search_best_g3_dev.json` store selected configs. | Satisfied |
| Round-robin or opponent-pool robustness check | `hl_benchmark/slimevolley/tournament.py`, `round_robin_dev.json`, `round_robin_g2_dev.json`, and `round_robin_g3_dev.json` record development opponent-pool tournaments. | Satisfied |
| Final holdout evaluation | `hl_benchmark/slimevolley/final_eval.py` produced `holdout_final.json`, `holdout_g2_final.json`, and `holdout_g3_final.json`; audit enforces final-only holdout labeling and seed matrix consistency. | Satisfied |
| Required command surface | `Makefile`, `README.md`, and `experiments/slimevolley/README.md` document commands for tests, one policy/opponent evaluation, development evaluation, final-only holdout reproduction, scalar search, round-robin tournament, summary regeneration, report regeneration, audit, and custom verification. | Satisfied |
| Heuristic-system improvement loop | Generation ledgers and diagnosis reports record evaluation rows, failure analysis, next hypotheses, change types, code/config/test edit labels, tests run, re-evaluation outcomes, and kept or rolled-back attempts including generation-3 failed structural directions. | Satisfied |
| Replay and diagnostics | `evaluate.py` ledger rows and `contact_diagnostics.py` artifacts record per-episode scores, timesteps, final outcome, policy/opponent/seed, action frequencies, life-loss summaries, compact trace windows, and selected contact/loss diagnostics. | Satisfied |
| Baseline comparison set | Final and performance reports compare random, built-in, initial handwritten, scalar-tuned, agent-maintained, archived heuristic, and packaged `baseline-rnn` opponents/policies across fixed development and holdout protocols. | Satisfied |
| Regression and golden tests | `tests/test_slimevolley_optional.py` covers environment creation, action validity, deterministic evaluation, report generation, audit validation, holdout guardrails, archived-policy checks, contact diagnostics, and fixed-state/golden SlimeVolley policy behavior. | Satisfied |
| Failure-analysis notes | Ledger rows include `failure_analysis` and `next_hypothesis`; final report, generation diagnosis reports, and `experiments/slimevolley/notes/` list dependency failures, rolled-back attempts, kept structural changes, and the generation-3 pre-holdout freeze note. | Satisfied |
| Separation of structural improvement from scalar tuning | Ledger `change_type`, policy version names, final report, and audit checks distinguish structural policies from `scalar/config tuning`. | Satisfied |
| Packaged RNN comparator | `baseline-rnn` wraps slimevolleygym's packaged 120-parameter RNN baseline and is reported separately as a documented pretrained neural/RNN comparator. No local PPO/DQN/self-play training baseline was run. | Satisfied |
| Cost accounting | Final report separates episodes/steps from ledger rows, wall time, code edits, agent iterations, scalar-search budget, generation-2 and generation-3 costs, and unavailable LLM token accounting. | Satisfied |
| Anti-cheating guardrails | Search rejects reserved splits, holdout rows are marked final-only, audit checks holdout seeds and summaries, failed rows remain visible, and all consumed holdout artifacts are treated as final-only evidence. | Satisfied |
| Extensible multi-environment structure | `hl_benchmark/environments/`, `hl_benchmark/policies/`, `hl_benchmark/custom_envs/`, `experiments/<env_slug>/`, and docs support future generic and custom RL envs. SlimeVolley is registered through `hl_benchmark/custom_envs/slimevolley/`, which delegates to the existing `hl_benchmark/slimevolley/` implementation for compatibility. `make check-promotion ENV=<EnvId>` and `make check-promotions` gate promotion readiness. | Satisfied |
| Final Markdown report | `experiments/slimevolley/reports/final_report.md` contains setup, seed ranges, opponent protocol, timeline, generation-2 evidence, generation-3 holdout evidence, results, costs, limitations, and conclusion. | Satisfied |

## Verification Commands

Latest local verification for this working tree:

```bash
make verify
make slimevolley-verify
make custom-verify ENV=SlimeVolley-v0
make check-promotions
python3 -m pytest tests/test_slimevolley_optional.py
```

Expected current outcomes:

- `make verify`: pass, with 148 pytest tests and 3 known optional Gym/SWIG deprecation warnings.
- `make slimevolley-verify`: pass, with 186 generation-1 rows, 114 generation-2 rows, 303 generation-3 rows, 30 generation-3 holdout rows, and audited generation-4 protocol artifacts.
- `make custom-verify ENV=SlimeVolley-v0`: pass through the custom-environment verification entrypoint, including contact diagnostics and generation protocol refreshes declared by the SlimeVolley harness.
- `make check-promotions`: pass, with all 6 registered environments promotion-ready.
- SlimeVolley audit warnings remain for append-only legacy noncanonical change types: `logging/diagnostics` and `neural/RL baseline`; raw generation-1 rows still predate `tests_pass_fail`, but `trial_amendments.jsonl` covers those 186 rows without rewriting them.

## Known Limitations

- The maintained heuristic is not deep-RL comparable: it wins non-built-in generation-3 holdout matchups but wins zero generation-3 holdout episodes against the built-in opponent, while the packaged RNN comparator is much stronger.
- The neural/RL comparator is a packaged RNN baseline, not a locally trained DQN/PPO/self-play agent. Its original training sample cost is external to this ledger.
- Holdout seeds `1000..1049`, generation-2 holdout seeds `4000..4049`, and generation-3 holdout seeds `7000..7049` are already consumed for final evidence. The predeclared generation-4 protocol is the next valid policy-work path: further SlimeVolley policy tuning must use generation-4 development seeds `9000..9049`; generation-4 holdout seeds `10000..10049` must remain sealed until the next freeze.
- LLM calls and token counts were not exposed by the local runtime and are recorded as unavailable rather than estimated.
- SlimeVolley is registered through `hl_benchmark/custom_envs/slimevolley/`, which delegates to `hl_benchmark/slimevolley/` for implementation compatibility; new custom environments should use `hl_benchmark/custom_envs/<env_slug>/` directly.
- No video replay or plot artifact is required by the current audit gate; diagnostics are textual/JSON plus compact trace summaries.

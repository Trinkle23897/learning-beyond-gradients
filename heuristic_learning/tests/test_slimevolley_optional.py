from __future__ import annotations

import json

import numpy as np
import pytest

from hl_benchmark.policies import make_policy
from hl_benchmark.policies.slimevolley import (
    SlimeVolleyImprovedV0Policy,
    SlimeVolleyImprovedV1Policy,
    SlimeVolleyImprovedV2Policy,
    SlimeVolleyImprovedV3Policy,
    SlimeVolleyImprovedV4Policy,
    SlimeVolleyImprovedV5Policy,
    SlimeVolleyImprovedV6Policy,
    SlimeVolleyImprovedTunedPolicy,
    SlimeVolleyAttackPolicy,
    SlimeVolleyPlannerPolicy,
    SlimeVolleyRallyServePolicy,
    SlimeVolleyNetPressurePolicy,
    SlimeVolleyPostContactPolicy,
    SlimeVolleyRandomPolicy,
    SlimeVolleyTeacherAssistedPolicy,
    SlimeVolleyTemporalPolicy,
)
from hl_benchmark.ledger import read_entries, write_summary_csv
from hl_benchmark.search import candidate_configs
from hl_benchmark.slimevolley.adapter import check_slimevolley_available, run_slimevolley_episode
from hl_benchmark.slimevolley.amendments import (
    append_missing_legacy_tests_pass_fail_amendments,
    apply_ledger_amendments,
    canonical_entry_hash,
    read_ledger_amendments,
)
from hl_benchmark.slimevolley.audit import (
    audit_slimevolley_artifacts,
    main as slimevolley_audit_main,
    render_audit_text,
)
from hl_benchmark.slimevolley.contact_diagnostics import (
    build_contact_diagnostics,
    write_contact_diagnostics,
)
from hl_benchmark.slimevolley.critic import (
    build_critic_prompt,
    invoke_claude,
    run_claude_critic,
)
from hl_benchmark.slimevolley.doctor import collect_slimevolley_metadata
from hl_benchmark.slimevolley.evaluate import evaluate_slimevolley
from hl_benchmark.slimevolley.final_eval import run_slimevolley_holdout
from hl_benchmark.slimevolley.opponents import OPPONENT_POOL, make_slimevolley_opponent
from hl_benchmark.slimevolley.performance_report import (
    PERFORMANCE_REPORT_SECTIONS,
    render_slimevolley_performance_report,
    write_slimevolley_performance_report,
)
from hl_benchmark.slimevolley.generation_report import (
    GENERATION_REPORT_SECTIONS,
    render_generation_2_diagnosis_report,
    render_generation_3_diagnosis_report,
    write_generation_2_diagnosis_report,
    write_generation_3_diagnosis_report,
)
from hl_benchmark.slimevolley.protocol import (
    GENERATION_2_SEED_SPLITS,
    GENERATION_3_SEED_SPLITS,
    GENERATION_4_SEED_SPLITS,
    GENERATION_5_SEED_SPLITS,
    generation_2_protocol_payload,
    generation_3_protocol_payload,
    generation_4_protocol_payload,
    generation_5_protocol_payload,
    render_generation_2_protocol_markdown,
    render_generation_3_protocol_markdown,
    render_generation_4_protocol_markdown,
    render_generation_5_protocol_markdown,
    write_generation_2_protocol,
    write_generation_3_protocol,
    write_generation_4_protocol,
    write_generation_5_protocol,
)
from hl_benchmark.slimevolley.report import render_slimevolley_report
from hl_benchmark.slimevolley.schema import (
    CANONICAL_CHANGE_TYPES,
    LEGACY_NONCANONICAL_CHANGE_TYPES,
    NEURAL_BASELINE_CHANGE_TYPE,
    validate_slimevolley_ledger_entry,
)
from hl_benchmark.slimevolley.search import search_slimevolley_configs
from hl_benchmark.slimevolley.summarize import (
    render_summary_text,
    summarize_slimevolley_ledger,
)
from hl_benchmark.slimevolley.tournament import run_slimevolley_tournament


TESTS_RUN_FIXTURE = ["python3 -m pytest tests/test_slimevolley_optional.py"]


def write_requirements_audit_fixture(path) -> None:
    path.write_text(
        """# SlimeVolley Requirement Coverage Audit

## Verdict

Holdout seeds `1000..1049`, generation-2 holdout seeds `4000..4049`, and generation-3 holdout seeds `7000..7049` are final-only; this fixture covers audit validation.

## Completion Checkpoint

Current completion gate is fixture audit validation. Accepted historical caveats: append-only legacy ledger rows use amendments instead of rewrites, and packaged RNN comparison satisfies the documented-pretrained-baseline comparator requirement while local neural training remains outside this ledger. Do not mark the durable goal complete for stronger SlimeVolley performance claims.

## Machine-Readable Completion State

The fixture mirrors the machine-readable completion fields required by the artifact audit:

- `requirements_audit_completion_state`: `satisfied`
- `requirements_audit_completion_recommendation`: `eligible_for_completion_audit`
- `requirements_audit_status_counts`: `{"Satisfied": 25}`
- `requirements_audit_completion_blockers`: `[]`

There are currently no partial rows in the SlimeVolley requirement matrix. Historical caveats remain visible through raw and effective test-status counts in `audit_latest.json`.

A passing artifact audit means the evidence is internally consistent. It does not by itself claim high SlimeVolley performance or deep-RL comparability.

## Coverage Matrix

| Requirement | Current evidence | Status |
| --- | --- | --- |
| Working repository | `make slimevolley-verify`; `make check-promotions`; contact diagnostics and generation protocol refreshes | Satisfied |
| Reproduction instructions | README and report commands | Satisfied |
| SlimeVolley environment wrapper or compatibility layer | adapter and doctor modules | Satisfied |
| Exact package and runtime metadata | diagnostics and runtime metadata | Satisfied |
| Initial handwritten heuristic | `hl_benchmark/policies/slimevolley.py` | Satisfied |
| Agent-maintained heuristic policy versions | `improved-v0`, `improved-v1`, `improved-v2`, `improved-v3`, `improved-v4`, `improved-v5`, `improved-v6`, `improved` | Satisfied |
| Opponent protocol | builtin, random, archived heuristics, and baseline-rnn | Satisfied |
| Fixed development and holdout seed ranges | dev, holdout, generation-2, and generation-3 splits | Satisfied |
| Append-only trial ledger | `experiments/slimevolley/results/trials.jsonl`; `experiments/slimevolley/results/trial_amendments.jsonl` records append-only `tests_pass_fail=not_recorded` amendments for historical rows | Satisfied |
| Evaluation harness | fixed-seed policy/opponent evaluation | Satisfied |
| Scalar/config search baseline | `search_best_dev.json` | Satisfied |
| Round-robin or opponent-pool robustness check | round_robin_dev.json | Satisfied |
| Final holdout evaluation | holdout_final.json, holdout_g2_final.json, and holdout_g3_final.json | Satisfied |
| Required command surface | test, one-eval, development-eval, holdout, search, tournament, summary, report, and audit commands are documented | Satisfied |
| Heuristic-system improvement loop | generation ledgers and diagnosis reports record evaluation, diagnosis, code/config/test change, tests, re-evaluation, and keep/rollback status | Satisfied |
| Replay and diagnostics | ledger rows and contact diagnostics record per-episode scores, steps, outcomes, policy/opponent/seed, action frequencies, life-loss summaries, and trace windows | Satisfied |
| Baseline comparison set | random, built-in, initial, tuned, improved, archived heuristics, and baseline-rnn are compared | Satisfied |
| Regression and golden tests | pytest SlimeVolley coverage | Satisfied |
| Failure-analysis notes | ledger failure_analysis and next_hypothesis | Satisfied |
| Separation of structural improvement from scalar tuning | ledger change_type and policy archives | Satisfied |
| Packaged RNN comparator | `baseline-rnn` wraps slimevolleygym's packaged RNN baseline as a documented pretrained neural/RNN comparator. No local PPO/DQN/self-play training baseline was run. | Satisfied |
| Cost accounting | final report cost accounting | Satisfied |
| Anti-cheating guardrails | reserved split and holdout checks | Satisfied |
| Extensible multi-environment structure | registry, policies, custom_envs, experiments, and `hl_benchmark/custom_envs/slimevolley/` bridge | Satisfied |
| Final Markdown report | final_report.md | Satisfied |

## Verification Commands

```bash
make slimevolley-verify
make check-promotions
```

## Known Limitations

The fixture records that the current policy is not deep-RL comparable. Further SlimeVolley policy tuning requires the predeclared generation-4 protocol.
""",
        encoding="utf-8",
    )


class FakeSlimeVolleyActionSpace:
    def seed(self, seed: int) -> None:
        self.seed_value = seed


class FakeBuiltInPolicy:
    def __init__(self) -> None:
        self.reset_count = 0

    def reset(self) -> None:
        self.reset_count += 1


class FakeSlimeVolleyEnv:
    action_space = FakeSlimeVolleyActionSpace()
    observation_space = "FakeBox(12)"

    def __init__(self) -> None:
        self.steps = 0
        self.received_builtin = False
        self.seed_value = None
        self.policy = FakeBuiltInPolicy()

    def seed(self, seed: int) -> None:
        self.seed_value = seed

    def reset(self):
        self.steps = 0
        obs = np.asarray([1.2, 0.0, 0.0, 0.0, 0.7, 0.8, 0.05, -0.03, -1.2, 0.0, 0.0, 0.0])
        return obs

    def step(self, action, other_action=None):
        if other_action is None:
            self.received_builtin = True
        self.steps += 1
        obs = np.asarray([1.1, 0.0, 0.0, 0.0, 0.9, 0.7, 0.04, -0.04, -1.1, 0.0, 0.0, 0.0])
        reward = 1.0 if self.steps == 3 else 0.0
        done = self.steps >= 3
        info = {"otherObs": obs * -1, "ale.lives": 5, "ale.otherLives": 4}
        return obs, reward, done, info

    def close(self) -> None:
        pass


def test_slimevolley_critic_prompt_uses_dev_rows_and_excludes_holdout_context(tmp_path) -> None:
    ledger_path = tmp_path / "generation_4_trials.jsonl"
    summary_path = tmp_path / "generation_4_summary.csv"
    report_path = tmp_path / "final_report.md"
    def fixture_entry(**overrides):
        score_mean = overrides.get("score_stats", {}).get("mean", 0.0)
        seed_range = overrides.get("seed_range", {"split": "dev", "start": 9000, "stop_exclusive": 9001})
        seeds = list(range(seed_range["start"], seed_range["stop_exclusive"]))
        entry = {
            "timestamp": "2026-05-26T00:00:00+00:00",
            "environment": "SlimeVolley-v0",
            "policy_version": "planner",
            "opponent_name": "builtin",
            "git_commit": "test",
            "diff_identifier": "test",
            "config": {},
            "seed_range": {**seed_range, "seeds": seeds},
            "episodes": len(seeds),
            "score_stats": {"mean": score_mean, "std": 0.0, "median": score_mean, "min": score_mean, "max": score_mean},
            "environment_steps": 1,
            "wall_clock_seconds": 0.1,
            "tests_run": TESTS_RUN_FIXTURE,
            "pass_fail": "pass",
            "change_summary": "critic fixture",
            "failure_analysis": "fixture",
            "next_hypothesis": "fixture",
            "change_type": "structural policy improvement",
            "agent_iterations": 0,
            "code_edits": 0,
            "llm_cost": {"source": "test"},
            "runtime_metadata": {"python": "test"},
            "win_loss_draw": {"wins": 0, "losses": len(seeds), "draws": 0},
        }
        entry.update(overrides)
        return entry

    dev_entry = fixture_entry(
        policy_version="planner",
        score_stats={"mean": -4.5, "std": 0.0, "median": -4.5, "min": -4.5, "max": -4.5},
        seed_range={"split": "dev", "start": 9000, "stop_exclusive": 9002, "seeds": [9000, 9001]},
        win_loss_draw={"wins": 0, "losses": 2, "draws": 0},
        environment_steps=123,
        failure_analysis="planner dev row",
        per_episode=[
            {
                "point_events": [
                    {
                        "policy_diagnostics": {"mode": "planner_floor_intercept"},
                        "pre_event_trace": [
                            {"policy_diagnostics": {"mode": "planner_intercept"}},
                        ],
                    }
                ]
            }
        ],
    )
    improved_tuned_entry = fixture_entry(
        policy_version="improved-tuned",
        score_stats={"mean": -1.1, "std": 0.0, "median": -1.1, "min": -1.1, "max": -1.1},
        seed_range={"split": "dev", "start": 9000, "stop_exclusive": 9002, "seeds": [9000, 9001]},
        win_loss_draw={"wins": 1, "losses": 1, "draws": 0},
        environment_steps=456,
        failure_analysis="scalar tuned row",
        change_type="scalar/config tuning",
    )
    holdout_entry = fixture_entry(
        policy_version="secret-holdout-policy",
        score_stats={"mean": 5.0, "std": 0.0, "median": 5.0, "min": 5.0, "max": 5.0},
        seed_range={"split": "holdout", "start": 10000, "stop_exclusive": 10001, "seeds": [10000]},
        win_loss_draw={"wins": 1, "losses": 0, "draws": 0},
        environment_steps=1,
        failure_analysis="must not enter prompt",
    )
    ledger_path.write_text(
        json.dumps(dev_entry) + "\n" + json.dumps(improved_tuned_entry) + "\n" + json.dumps(holdout_entry) + "\n",
        encoding="utf-8",
    )
    summary_path.write_text("header\n", encoding="utf-8")
    report_path.write_text("## Generation-4 Development Attempt\nreport text\n", encoding="utf-8")

    prompt = build_critic_prompt(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        context="sanitized",
    )

    assert "planner dev row" in prompt
    assert "improved-tuned" in prompt
    assert "scalar tuned row" in prompt
    assert "secret-holdout-policy" not in prompt
    assert "must not enter prompt" not in prompt
    assert "Sealed holdout/audit rows" in prompt
    assert "planner_floor_intercept" in prompt


def test_slimevolley_critic_mock_run_writes_auditable_artifacts(tmp_path) -> None:
    ledger_path = tmp_path / "generation_4_trials.jsonl"
    summary_path = tmp_path / "generation_4_summary.csv"
    report_path = tmp_path / "final_report.md"
    ledger_path.write_text("", encoding="utf-8")
    summary_path.write_text("", encoding="utf-8")
    report_path.write_text("", encoding="utf-8")

    result = run_claude_critic(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        mock_output="Collect return-placement diagnostics next.",
        report_artifact_dir=tmp_path / "reports" / "critic",
        omx_artifact_dir=tmp_path / ".omx" / "artifacts",
    )

    assert result.report_artifact_path is not None
    assert result.omx_artifact_path is not None
    artifact_text = result.report_artifact_path.read_text(encoding="utf-8")
    assert "## Final Prompt Sent To Claude CLI" in artifact_text
    assert "## Claude Output Raw" in artifact_text
    assert "Collect return-placement diagnostics next." in artifact_text
    assert result.metadata["mock_output_used"] is True


def test_slimevolley_critic_dry_run_does_not_write_artifacts(tmp_path) -> None:
    result = run_claude_critic(
        ledger_path=tmp_path / "missing.jsonl",
        summary_path=tmp_path / "missing.csv",
        report_path=tmp_path / "missing.md",
        dry_run=True,
        report_artifact_dir=tmp_path / "reports" / "critic",
        omx_artifact_dir=tmp_path / ".omx" / "artifacts",
    )

    assert "external critic" in result.prompt.lower()
    assert result.report_artifact_path is None
    assert result.omx_artifact_path is None
    assert not (tmp_path / "reports" / "critic").exists()


def test_slimevolley_critic_refuses_external_call_without_gate() -> None:
    with pytest.raises(ValueError, match="allow-external-claude"):
        invoke_claude("prompt", allow_external_claude=False, runner=lambda command: "unused")



def test_slimevolley_policy_factory_actions_are_multibinary() -> None:
    obs = np.asarray([1.2, 0.0, 0.0, 0.0, 0.8, 0.8, 0.05, -0.04, -1.2, 0.0, 0.0, 0.0])
    for policy_name in ["initial", "improved", "improved-tuned", "attack", "rally-serve", "post-contact", "net-pressure", "temporal", "planner", "teacher-assisted", "tuned", "improved-v0", "improved-v1", "improved-v2", "improved-v3", "improved-v4", "improved-v5", "improved-v6"]:
        policy = make_policy("SlimeVolley-v0", policy_name)
        action = policy.act(obs)
        assert action.shape == (3,)
        assert action.dtype == np.int8
        assert set(action.tolist()) <= {0, 1}


def test_slimevolley_improved_tuned_is_labeled_scalar_tuning() -> None:
    for policy in [SlimeVolleyImprovedTunedPolicy(), make_policy("SlimeVolley-v0", "improved-tuned")]:
        config = policy.config()
        assert config["policy_type"] == "slimevolley_improved_tuned"
        assert config["tuning_label"] == "scalar/config tuning"
        assert config["tuned_from"] == "improved-v6/current-rear_wall_low_jump"
        assert config["tuned_revision"] == "g4-scalar-tuned-v2"
        assert config["tuned_fields"] == {
            "x_margin": 0.04,
            "contact_x_window": 0.14,
            "high_arc_horizon": 0.85,
            "overcommit_guard_x": 0.18,
            "low_ball_rescue_x_window": 0.72,
            "low_ball_rescue_horizon": 0.06,
            "grounded_low_receive_airborne_margin": 0.12,
        }



def test_slimevolley_attack_candidate_golden_behavior() -> None:
    policy = SlimeVolleyAttackPolicy()
    state = np.asarray([0.62, 0.20, 0.0, 0.0, 0.42, 0.50, -0.70, -0.30, -1.2, 0.0, 0.0, 0.0])
    assert policy.act(state).tolist() == [1, 0, 1]
    config = policy.config()
    assert config["policy_type"] == "slimevolley_attack_candidate"
    assert config["candidate_status"] == "partial_not_promoted"
    assert config["structural_change"] == "late_contact_attack"


def test_slimevolley_attack_records_branch_diagnostics() -> None:
    policy = SlimeVolleyAttackPolicy()
    state = np.asarray([0.62, 0.20, 0.0, 0.0, 0.42, 0.50, -0.70, -0.30, -1.2, 0.0, 0.0, 0.0])
    action = policy.act(state)
    diagnostics = policy.diagnostics()
    assert action.tolist() == [1, 0, 1]
    assert diagnostics["mode"] == "late_contact_attack"
    assert diagnostics["action"] == "101"
    assert diagnostics["target_x"] == pytest.approx(0.42)
    assert "drive forward+jump" in diagnostics["reason"]


def test_slimevolley_rally_serve_candidate_golden_behavior() -> None:
    policy = SlimeVolleyRallyServePolicy()
    serve_state = np.asarray([1.20, 0.15, 0.0, 0.0, 0.04, 1.55, 0.02, 0.0, -1.2, 0.0, 0.0, 0.0])
    action = policy.act(serve_state)
    diagnostics = policy.diagnostics()
    assert action.tolist() == [1, 0, 1]
    assert diagnostics["mode"] == "rally_serve"
    assert diagnostics["action"] == "101"
    assert diagnostics["target_x"] == pytest.approx(0.0)
    config = policy.config()
    assert config["policy_type"] == "slimevolley_rally_serve_candidate"
    assert config["candidate_status"] == "dev_beat_baseline_rnn_failed_generation_4_holdout"
    assert config["structural_changes"] == ["late_contact_attack", "rally_serve_detector"]
    assert config["development_result"]["mean"] == pytest.approx(0.14)
    assert config["development_result"]["holdout_status"] == "generation_4_failed_to_beat_baseline_rnn"


def test_slimevolley_post_contact_candidate_golden_behavior() -> None:
    policy = SlimeVolleyPostContactPolicy()
    previous = np.asarray([0.55, 0.20, 0.0, 0.0, 0.30, 0.52, 0.12, -0.02, -1.2, 0.0, 0.0, 0.0])
    current = np.asarray([0.55, 0.20, 0.0, 0.0, 0.30, 0.52, -0.12, -0.02, -1.2, 0.0, 0.0, 0.0])
    assert policy.act(previous).shape == (3,)
    action = policy.act(current)
    diagnostics = policy.diagnostics()
    assert action.tolist() == [1, 0, 1]
    assert diagnostics["mode"] == "post_contact_front_conversion"
    assert diagnostics["action"] == "101"
    assert diagnostics["target_x"] == pytest.approx(0.30)
    config = policy.config()
    assert config["policy_type"] == "slimevolley_post_contact_candidate"
    assert config["candidate_status"] == "development_only_not_holdout_validated"
    assert "post_contact_front_conversion" in config["structural_changes"]
    assert config["development_result"]["holdout_status"] == "not_evaluated_do_not_tune_on_generation_4_holdout"


def test_slimevolley_golden_behavior() -> None:
    initial = make_policy("SlimeVolley-v0", "initial")
    improved = make_policy("SlimeVolley-v0", "improved")

    descending_contact = np.asarray([1.0, 0.0, 0.0, 0.0, 1.05, 0.8, 0.0, -0.08, -1.2, 0.0, 0.0, 0.0])
    assert initial.act(descending_contact).tolist() == [0, 0, 1]

    serve_state = np.asarray([1.2, 0.0, 0.0, 0.0, 0.05, 1.6, 0.0, 0.0, -1.2, 0.0, 0.0, 0.0])
    improved.reset(0)
    assert improved.act(serve_state)[2] == 1

    front_hit_state = np.asarray([0.675, 0.419, 0.0, 0.66, 0.882, 0.586, -0.93, -0.84, -1.2, 0.0, 0.0, 0.0])
    improved.reset(464)
    assert improved.act(front_hit_state).tolist() == [1, 0, 0]
    archived_v4 = make_policy("SlimeVolley-v0", "improved-v4")
    archived_v4.reset(464)
    assert archived_v4.act(front_hit_state).tolist() == [1, 0, 1]

    low_ball_state = np.asarray([1.08, 0.0, 0.0, 0.0, 0.72, 0.32, 1.40, -1.70, -1.2, 0.0, 0.0, 0.0])
    improved.reset(40)
    assert improved.act(low_ball_state).tolist() == [1, 0, 1]
    temporal = make_policy("SlimeVolley-v0", "temporal")
    temporal.reset(40)
    temporal.act(np.asarray([1.2, 0.0, 0.0, 0.0, -0.18, 0.92, -0.22, -0.10, -1.2, 0.0, 0.0, 0.0]))
    assert temporal.act(low_ball_state).tolist() == [1, 0, 1]

    late_low_ball_state = np.asarray([
        1.6083333333333336,
        0.4089999999999998,
        -1.75,
        -0.6100000000000005,
        1.394555527532018,
        0.20936784794911595,
        -1.6793619058381766,
        -1.4974122976720763,
        0.2,
        0.4707333333333331,
        0.0,
        -0.21800000000000042,
    ])
    improved.reset(40)
    assert improved.act(late_low_ball_state).tolist() == [1, 0, 0]

    grounded_receive_state = np.asarray([
        1.8416666666666663,
        0.4707333333333331,
        -1.75,
        -0.21800000000000042,
        1.6279485985910003,
        0.3975218855190726,
        -1.8663318444602972,
        -1.2567042000221953,
        0.2,
        0.4801999999999998,
        0.0,
        0.17399999999999963,
    ])
    improved.reset(40)
    assert improved.act(grounded_receive_state).tolist() == [1, 0, 0]

    falling_floor_intercept_state = np.asarray([
        1.02,
        0.15,
        0.0,
        0.0,
        0.57,
        0.51,
        1.47,
        -1.70,
        -1.2,
        0.0,
        0.0,
        0.0,
    ])
    improved.reset(440)
    assert improved.act(falling_floor_intercept_state).tolist() == [1, 0, 0]


def test_slimevolley_temporal_policy_uses_stacked_history_features() -> None:
    policy = SlimeVolleyTemporalPolicy()
    policy.reset(0)
    before_contact = np.asarray([1.2, 0.0, 0.0, 0.0, -0.18, 0.92, -0.22, -0.10, -1.2, 0.0, 0.0, 0.0])
    after_contact = np.asarray([1.18, 0.0, 0.0, 0.0, -0.12, 0.88, 0.42, -0.12, -1.1, 0.0, 0.0, 0.0])

    assert policy.act(before_contact).shape == (3,)
    features = policy._temporal_features(after_contact)
    assert features.frames == 2
    assert features.recent_opponent_contact is True
    assert features.ball_ax > 0.0
    assert features.stacked_ball_vx > 0.0


def test_slimevolley_temporal_policy_reset_clears_stacked_history() -> None:
    policy = SlimeVolleyTemporalPolicy()
    before_contact = np.asarray([1.2, 0.0, 0.0, 0.0, -0.18, 0.92, -0.22, -0.10, -1.2, 0.0, 0.0, 0.0])
    after_contact = np.asarray([1.18, 0.0, 0.0, 0.0, -0.12, 0.88, 0.42, -0.12, -1.1, 0.0, 0.0, 0.0])

    policy.reset(0)
    policy.act(before_contact)
    assert policy._temporal_features(after_contact).recent_opponent_contact is True

    policy.reset(0)
    assert policy._temporal_features(after_contact).recent_opponent_contact is False


def test_slimevolley_planner_features_use_physics_meaningful_history() -> None:
    policy = SlimeVolleyPlannerPolicy()
    policy.reset(0)
    policy.act(np.asarray([1.0, 0.0, 0.0, 0.0, 1.70, 0.80, 0.38, -0.45, -1.2, 0.0, -0.04, 0.0]))
    state = np.asarray([1.1, 0.0, 0.0, 0.0, 1.95, 0.58, 0.60, -0.60, -1.24, 0.0, -0.04, 0.0])

    features = policy._planner_features(state)

    assert features.wall_bounce_imminent is True
    assert features.predicted_intercept_x < 2.12
    assert features.time_to_floor > 0.0
    assert features.stacked_ball_vx > 0.0
    assert features.ball_returning is True


def test_slimevolley_planner_policy_records_interpretable_diagnostics() -> None:
    policy = SlimeVolleyPlannerPolicy()
    policy.reset(0)
    action = policy.act(np.asarray([1.90, 0.0, 0.0, 0.0, 2.02, 0.48, 0.75, -0.80, -1.2, 0.0, 0.0, 0.0]))
    diagnostics = policy.diagnostics()

    assert action.shape == (3,)
    assert diagnostics["mode"] in {
        "planner_rear_wall",
        "planner_floor_intercept",
        "planner_intercept",
        "planner_net_clearance_guard",
    }
    assert "planner" in diagnostics
    assert "time_to_floor" in diagnostics["planner"]
    assert "predicted_intercept_x" in diagnostics["planner"]


def test_slimevolley_teacher_assisted_policy_is_labeled_but_transparent() -> None:
    policy = SlimeVolleyTeacherAssistedPolicy()
    policy.reset(0)
    action = policy.act(np.asarray([1.0, 0.0, 0.0, 0.0, 0.82, 0.74, 0.15, -0.08, -0.7, 0.0, 0.0, 0.0]))
    config = policy.config()
    diagnostics = policy.diagnostics()

    assert action.shape == (3,)
    assert config["teacher_assisted"] is True
    assert "baseline-rnn" in config["teacher_source"]
    assert diagnostics["teacher_assisted"] is True


def test_slimevolley_contact_diagnostics_from_trace(tmp_path) -> None:
    entry = {
        "timestamp": "2026-05-25T20:45:00+00:00",
        "environment": "SlimeVolley-v0",
        "policy_version": "improved",
        "opponent_name": "builtin",
        "pass_fail": "pass",
        "change_type": "invalid/rolled back",
        "change_summary": "Synthetic traced row for contact diagnostics.",
        "seed_range": {"split": "dev", "start": 6000, "stop_exclusive": 6001, "seeds": [6000]},
        "git_commit": "test",
        "diff_identifier": "test",
        "config": {"trace_window": 3},
        "score_stats": {"mean": -1.0, "std": 0.0, "median": -1.0, "min": -1.0, "max": -1.0},
        "environment_steps": 12,
        "wall_clock_seconds": 0.1,
        "episodes": 1,
        "tests_run": TESTS_RUN_FIXTURE,
        "failure_analysis": "Synthetic fixture.",
        "next_hypothesis": "Synthetic next hypothesis.",
        "agent_iterations": 0,
        "code_edits": 0,
        "llm_cost": {"source": "test"},
        "runtime_metadata": {"python": "test"},
        "win_loss_draw": {"wins": 0, "losses": 1, "draws": 0},
        "per_episode": [
            {
                "seed": 6000,
                "point_events": [
                    {
                        "step": 12,
                        "outcome": "point_lost",
                        "action": "010",
                        "state_before_step": {
                            "agent_x": 1.10,
                            "agent_y": 0.40,
                            "ball_x": 1.30,
                            "ball_y": 0.22,
                            "ball_vx": 1.20,
                            "ball_vy": -1.50,
                        },
                        "pre_event_trace": [
                            {
                                "step": 10,
                                "action": "100",
                                "state": {
                                    "agent_x": 1.05,
                                    "agent_y": 0.35,
                                    "ball_x": 1.08,
                                    "ball_y": 0.42,
                                    "ball_vx": -1.10,
                                    "ball_vy": -0.80,
                                },
                            },
                            {
                                "step": 11,
                                "action": "010",
                                "state": {
                                    "agent_x": 1.08,
                                    "agent_y": 0.37,
                                    "ball_x": 1.12,
                                    "ball_y": 0.38,
                                    "ball_vx": 1.15,
                                    "ball_vy": -1.10,
                                },
                            },
                        ],
                    }
                ],
            }
        ],
    }
    payload = build_contact_diagnostics([entry])
    assert payload["status"] == "pass"
    assert payload["selected_entry"]["timestamp"] == entry["timestamp"]
    assert payload["loss_state_buckets"] == {"low_mid_right": 1}
    assert payload["contact_candidate_summary"]["count"] == 1
    assert payload["contact_candidate_summary"]["by_event_outcome"] == {"point_lost": 1}

    ledger_path = tmp_path / "generation_3_trials.jsonl"
    json_path = tmp_path / "contact_diagnostics_g3_dev.json"
    markdown_path = tmp_path / "contact_diagnostics_g3_dev.md"
    ledger_path.write_text(json.dumps(entry) + "\n", encoding="utf-8")
    written = write_contact_diagnostics(
        ledger_path=ledger_path,
        json_path=json_path,
        markdown_path=markdown_path,
    )
    assert written["status"] == "pass"
    assert json.loads(json_path.read_text(encoding="utf-8"))["contact_candidate_summary"]["count"] == 1
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "SlimeVolley Generation-3 Contact/Return Diagnostics" in markdown
    assert "does not inspect generation-3 holdout seeds" in markdown


def test_slimevolley_contact_diagnostics_no_data() -> None:
    payload = build_contact_diagnostics([])
    assert payload["status"] == "no_data"
    assert "holdout" in payload["anti_tuning_note"]

def test_slimevolley_random_policy_is_seed_deterministic() -> None:
    policy = SlimeVolleyRandomPolicy()
    obs = np.zeros(12)
    policy.reset(123)
    first = [policy.act(obs).tolist() for _ in range(5)]
    policy.reset(123)
    second = [policy.act(obs).tolist() for _ in range(5)]
    assert first == second


def test_slimevolley_opponent_pool_has_required_baselines() -> None:
    assert {"builtin", "random", "initial", "improved-v0", "improved-v1", "improved-v2", "improved-v3", "improved-v4", "improved-v5", "improved-v6", "improved", "improved-tuned", "attack", "rally-serve", "post-contact", "net-pressure", "temporal", "planner", "teacher-assisted", "baseline-rnn"}.issubset(OPPONENT_POOL)
    assert getattr(make_slimevolley_opponent("builtin"), "uses_env_builtin") is True
    assert getattr(make_slimevolley_opponent("initial"), "uses_env_builtin") is False


def test_slimevolley_episode_runner_supports_fake_legacy_env_and_builtin_opponent() -> None:
    env = FakeSlimeVolleyEnv()
    result = run_slimevolley_episode(
        env=env,
        policy=make_policy("SlimeVolley-v0", "initial"),
        opponent=make_slimevolley_opponent("builtin"),
        seed=7,
    )
    assert env.seed_value == 7
    assert env.received_builtin is True
    assert result.score == 1.0
    assert result.steps == 3
    assert result.outcome == "win"
    assert result.life_difference == 1
    assert sum(result.action_counts.values()) == 3
    assert len(result.point_events) == 1
    assert result.point_events[0]["outcome"] == "point_won"
    assert result.point_events[0]["state_before_step"]["ball_x"] == 0.9
    assert env.policy.reset_count == 1


def test_slimevolley_episode_runner_can_attach_pre_point_trace() -> None:
    env = FakeSlimeVolleyEnv()
    result = run_slimevolley_episode(
        env=env,
        policy=make_policy("SlimeVolley-v0", "initial"),
        opponent=make_slimevolley_opponent("builtin"),
        seed=7,
        trace_window=2,
    )
    event = result.point_events[0]
    assert [frame["step"] for frame in event["pre_event_trace"]] == [1, 2]
    assert event["pre_event_trace"][-1]["action"] == event["action"]
    assert event["pre_event_trace"][-1]["state"]["ball_x"] == event["state_before_step"]["ball_x"]


def test_slimevolley_episode_runner_can_attach_policy_diagnostics_to_trace() -> None:
    env = FakeSlimeVolleyEnv()
    result = run_slimevolley_episode(
        env=env,
        policy=make_policy("SlimeVolley-v0", "planner"),
        opponent=make_slimevolley_opponent("builtin"),
        seed=7,
        trace_window=2,
    )
    event = result.point_events[0]

    assert "policy_diagnostics" in event
    assert "policy_diagnostics" in event["pre_event_trace"][-1]
    assert "planner" in event["policy_diagnostics"]


def test_slimevolley_evaluator_records_trace_window_config_with_fake_env(tmp_path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    entry = evaluate_slimevolley(
        policy_name="initial",
        opponent_name="builtin",
        split="smoke",
        ledger_path=ledger_path,
        summary_path=summary_path,
        env_factory=FakeSlimeVolleyEnv,
        trace_window=2,
        tests_run=TESTS_RUN_FIXTURE,
    )
    assert entry["config"]["trace_window"] == 2
    assert "pre_event_trace" in entry["per_episode"][0]["point_events"][0]
    assert len(entry["per_episode"][0]["point_events"][0]["pre_event_trace"]) == 2
    assert len(read_entries(ledger_path)) == 1


def test_slimevolley_doctor_reports_dependency_status_without_install() -> None:
    available, message = check_slimevolley_available()
    metadata = collect_slimevolley_metadata()
    assert metadata["status"] in {"available", "unavailable"}
    assert metadata["packages"]["slimevolleygym"]
    assert metadata["runtime_metadata"]["python"]
    assert metadata["runtime_metadata"]["platform"]
    assert metadata["runtime_metadata"]["packages"]["slimevolleygym"]
    assert "seed_api_behavior" in metadata
    assert "same_seed_reset_observation_equal" in metadata
    assert "observed_step_api" in metadata
    assert "multiagent_step_api_observed" in metadata
    if available:
        assert metadata["same_seed_reset_observation_equal"] is True
        assert metadata["observed_step_api"] in {"legacy-4-tuple", "gymnasium-5-tuple"}
        assert metadata["multiagent_step_api_observed"] in {"legacy-4-tuple", "gymnasium-5-tuple"}
    else:
        assert metadata["status"] == "unavailable"
        assert message in metadata["message"]


def test_slimevolley_scalar_search_space_is_registered() -> None:
    configs = candidate_configs("SlimeVolley-v0", max_candidates=4)
    assert len(configs) == 4
    assert {"home_x", "contact_x_window", "landing_horizon"}.issubset(configs[0])


def test_slimevolley_evaluator_records_opponent_metrics_with_fake_env(tmp_path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    entry = evaluate_slimevolley(
        policy_name="initial",
        opponent_name="builtin",
        split="smoke",
        ledger_path=ledger_path,
        summary_path=summary_path,
        env_factory=FakeSlimeVolleyEnv,
        tests_run=TESTS_RUN_FIXTURE,
    )
    assert entry["pass_fail"] == "pass"
    assert entry["opponent_name"] == "builtin"
    assert entry["win_loss_draw"] == {"wins": 2, "losses": 0, "draws": 0, "win_rate": 1.0}
    assert entry["life_difference_stats"]["mean"] == 1.0
    assert entry["environment_steps"] == 6
    assert len(read_entries(ledger_path)) == 1
    summary = summary_path.read_text(encoding="utf-8")
    assert "opponent_name" in summary
    assert "builtin" in summary
    assert "win_rate" in summary


def test_slimevolley_evaluator_no_ledger_does_not_write(tmp_path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    entry = evaluate_slimevolley(
        policy_name="initial",
        opponent_name="initial",
        split="smoke",
        ledger_path=None,
        summary_path=None,
        env_factory=FakeSlimeVolleyEnv,
        tests_run=TESTS_RUN_FIXTURE,
    )
    assert entry["pass_fail"] == "pass"
    assert entry["opponent_name"] == "initial"
    assert not ledger_path.exists()


def test_slimevolley_evaluator_records_missing_dependency_failure(tmp_path) -> None:
    available, _message = check_slimevolley_available()
    if available:
        return
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    entry = evaluate_slimevolley(
        policy_name="initial",
        opponent_name="builtin",
        split="smoke",
        ledger_path=ledger_path,
        summary_path=summary_path,
        tests_run=TESTS_RUN_FIXTURE,
    )
    assert entry["pass_fail"] == "fail"
    assert "SlimeVolley requires optional legacy dependencies" in entry["failure_analysis"]
    assert entry["opponent_name"] == "builtin"
    assert len(read_entries(ledger_path)) == 1


def test_slimevolley_direct_evaluation_rejects_reserved_splits(tmp_path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    for split in ("holdout", "audit"):
        with pytest.raises(ValueError, match="direct SlimeVolley evaluation may not use holdout or audit"):
            evaluate_slimevolley(
                policy_name="initial",
                opponent_name="builtin",
                split=split,
                ledger_path=ledger_path,
                summary_path=tmp_path / "summary.csv",
                env_factory=FakeSlimeVolleyEnv,
                tests_run=TESTS_RUN_FIXTURE,
            )
    assert not ledger_path.exists()


def test_slimevolley_tournament_rejects_reserved_splits(tmp_path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    for split in ("holdout", "audit"):
        with pytest.raises(ValueError, match="direct SlimeVolley evaluation may not use holdout or audit"):
            run_slimevolley_tournament(
                split=split,
                participants=("initial",),
                ledger_path=ledger_path,
                summary_path=tmp_path / "summary.csv",
                output_path=tmp_path / "round_robin.json",
                env_factory=FakeSlimeVolleyEnv,
            )
    assert not ledger_path.exists()


def test_slimevolley_report_generation(tmp_path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    report_path = tmp_path / "final_report.md"
    diagnostics_path = tmp_path / "environment_diagnostics.json"
    diagnostics_path.write_text(
        '{"status":"unavailable","message":"missing deps","packages":{"slimevolleygym":"not_installed"},"expected_observation_space":"Box(12)","expected_action_space":"MultiBinary(3)","expected_step_api":"legacy","reward_semantics":"point reward","seed_api_behavior":"not probed; unavailable","same_seed_reset_observation_equal":false,"observed_step_api":"unavailable","multiagent_step_api_observed":"unavailable","runtime_metadata":{"python":"test-python","platform":"test-platform","packages":{"slimevolleygym":"not_installed"}}}',
        encoding="utf-8",
    )
    evaluate_slimevolley(
        policy_name="initial",
        opponent_name="builtin",
        split="smoke",
        ledger_path=ledger_path,
        summary_path=summary_path,
        env_factory=FakeSlimeVolleyEnv,
        tests_run=TESTS_RUN_FIXTURE,
    )
    report = render_slimevolley_report(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
    )
    assert "SlimeVolley Heuristic Learning Report" in report
    assert "Registration status: `custom_active`" in report
    assert "Custom module root: `hl_benchmark.custom_envs.slimevolley`" in report
    assert "hl_benchmark/custom_envs/slimevolley/" in report
    assert "Reproduction Commands" in report
    assert "Runtime Metadata" in report
    assert "Environment Diagnostics" in report
    assert "Observed step API" in report
    assert "Observed multi-agent step API" in report
    assert "Same-seed reset observation match" in report
    assert "Reward semantics" in report
    assert "stable-baselines3" in report
    assert "Platform:" in report
    assert "make check-env ENV=SlimeVolley-v0" in report
    assert "make check-promotion ENV=SlimeVolley-v0" in report
    assert "make check-promotions" in report
    assert "make check-envs" in report
    assert "make check-env-layout" in report
    assert "make custom-run ENV=SlimeVolley-v0" in report
    assert "make custom-verify ENV=SlimeVolley-v0" in report
    assert "make slimevolley-summary" in report
    assert "make slimevolley-contact-diagnostics" in report
    assert "make slimevolley-audit" in report
    assert "make slimevolley-verify" in report
    assert "make slimevolley-performance-report" in report
    assert "make slimevolley-generation-report" in report
    assert "make slimevolley-protocol" in report
    assert "make slimevolley-generation3-protocol" in report
    assert "make slimevolley-generation4-protocol" in report
    assert "reports/performance_deepdive.md" in report
    assert "reports/generation_2_diagnosis.md" in report
    assert "reports/generation_2_protocol.md" in report
    assert "configs/generation_2_protocol.json" in report
    assert "results/generation_2_trials.jsonl" in report
    assert "results/generation_2_summary.csv" in report
    assert "results/search_best_g2_dev.json" in report
    assert "results/round_robin_g2_dev.json" in report
    assert "results/holdout_g2_final.json" in report
    assert "--tests-pass-fail pass" in report
    assert "`tests_pass_fail`" in report
    assert "trial_amendments.jsonl" in report
    assert "results/audit_latest.json" in report
    assert "artifact/source SHA256 hashes" in report
    assert "requirements_audit_status_counts" in report
    assert "requirements_audit_partial_rows" in report
    assert "requirements_audit_completion_state" in report
    assert "requirements_audit_completion_recommendation" in report
    assert "requirements_audit_partial_row_details" in report
    assert "requirements_audit_partial_row_classifications" in report
    assert "generation-2 ledger rows use only predeclared generation-2 split seeds" in report
    assert "search_best_g2_dev.json" in report
    assert "round_robin_g2_dev.json" in report
    assert "holdout_g2_final.json" in report
    assert "Artifact Integrity Checks" in report
    assert "Artifact Manifest" in report
    assert "results/trials.jsonl" in report
    assert "results/audit_latest.json" in report
    assert "results/contact_diagnostics_g3_dev.json" in report
    assert "reports/contact_diagnostics_g3_dev.md" in report
    assert "configs/generation_4_protocol.json" in report
    assert "reports/generation_4_protocol.md" in report
    assert "9000..9049" in report
    assert "10000..10049" in report
    assert "11000..11049" in report
    assert "field-by-field content against the append-only ledger" in report
    assert "seed-reset and native step-API probes" in report
    assert "diagnostics availability remains consistent with successful development or holdout evidence" in report
    assert "known-opponent" in report
    assert "known-policy participant matrix" in report
    assert "failed-row failure-analysis fields" in report
    assert "scalar/config tuning rows never use reserved `holdout` or `audit` splits" in report
    assert "Opponent Protocol" in report
    assert "Diagnostic Coverage" in report
    assert "Minimum logged fields covered" in report
    assert "life-loss/life-win point events" in report
    assert "Trace Diagnostics" in report
    assert "No traced `improved` vs `builtin` development-seed diagnostic row has been recorded yet." in report
    assert "Failed Or Partial Directions" in report
    assert "No failed or partial structural direction has enough paired evidence yet." in report
    assert "predeclared generation-4 protocol" in report
    assert "Seed Ranges" in report
    assert "| smoke | `0..1`" in report
    assert "Policy Evolution Timeline" in report
    assert "initial handwritten heuristic" in report
    assert "Cost Accounting" in report
    assert "Environment-interaction cost is reported separately from research/agent maintenance cost" in report
    assert "Explicit test pass/fail statuses" in report
    assert "Sample cost by evidence split" in report
    assert "Mutually exclusive cost by comparison group" in report
    assert "packaged RNN comparator" in report
    assert "original training sample cost is external to this ledger" in report
    assert "Hypothesis Evidence Verdict" in report
    assert "No successful development or holdout evidence exists yet." in report
    assert "Anti-Cheating And Limitations" in report
    assert "Holdout seeds are not present in the ledger yet." in report
    assert "Round-Robin Tournament" in report
    assert "No SlimeVolley round-robin artifact recorded yet." in report
    assert "Holdout Evaluation" in report
    assert "No SlimeVolley holdout rows recorded yet; reserved seeds remain untouched." in report
    assert "Neural/RL Comparator" in report
    assert "No neural/RL comparator has been recorded yet." in report
    assert "initial | builtin" in report
    assert report_path.exists()




def test_slimevolley_generation_2_protocol_generation(tmp_path) -> None:
    payload = generation_2_protocol_payload()
    assert payload["protocol_id"] == "slimevolley-g2"
    assert payload["status"] == "predeclared-not-run"
    assert payload["created_by"] == "hl_benchmark.custom_envs.slimevolley.protocol"
    assert payload["generation_2"]["ledger"].endswith("generation_2_trials.jsonl")
    assert payload["generation_2"]["summary"].endswith("generation_2_summary.csv")
    assert payload["generation_2"]["seed_splits"]["dev"]["label"] == "3000..3049"
    assert payload["generation_2"]["seed_splits"]["holdout"]["label"] == "4000..4049"
    assert payload["generation_2"]["seed_splits"]["audit"]["label"] == "5000..5049"
    assert "Do not inspect generation-2 holdout" in " ".join(payload["guardrails"])
    assert "generation_2_trials.jsonl" in payload["commands"]["dev_builtin_trace"]
    assert "--seed-start 4000" in payload["commands"]["final_holdout_once"]
    assert "python3 -m hl_benchmark.custom_envs.slimevolley.audit --format json" in payload["promotion_checks"]

    generation_one_ranges = [range(0, 20), range(1000, 1050), range(2000, 2050)]
    for spec in GENERATION_2_SEED_SPLITS.values():
        current = range(int(spec["start"]), int(spec["stop_exclusive"]))
        assert all(current.start >= prior.stop or prior.start >= current.stop for prior in generation_one_ranges)

    markdown = render_generation_2_protocol_markdown(payload)
    assert "SlimeVolley Generation-2 Protocol" in markdown
    assert "Generation-1 holdout is already opened" in markdown
    assert "3000..3049" in markdown
    assert "4000..4049" in markdown
    assert "holdout_g2_final.json" in markdown
    assert "hl_benchmark.custom_envs.slimevolley.audit" in markdown

    paths = write_generation_2_protocol(
        json_path=tmp_path / "generation_2_protocol.json",
        markdown_path=tmp_path / "generation_2_protocol.md",
    )
    assert paths["json"].exists()
    assert paths["markdown"].exists()




def test_slimevolley_generation_3_protocol_generation(tmp_path) -> None:
    payload = generation_3_protocol_payload()
    assert payload["protocol_id"] == "slimevolley-g3"
    assert payload["status"] == "predeclared-not-run"
    assert payload["created_by"] == "hl_benchmark.custom_envs.slimevolley.protocol"
    assert payload["generation_3"]["ledger"].endswith("generation_3_trials.jsonl")
    assert payload["generation_3"]["summary"].endswith("generation_3_summary.csv")
    assert payload["generation_3"]["seed_splits"]["dev"]["label"] == "6000..6049"
    assert payload["generation_3"]["seed_splits"]["holdout"]["label"] == "7000..7049"
    assert payload["generation_3"]["seed_splits"]["audit"]["label"] == "8000..8049"
    assert "improved-v3" in payload["generation_3"]["holdout_opponents"]
    assert "Do not inspect generation-3 holdout" in " ".join(payload["guardrails"])
    assert "generation_3_trials.jsonl" in payload["commands"]["dev_builtin_trace"]
    assert "--seed-start 7000" in payload["commands"]["final_holdout_once"]
    assert "python3 -m hl_benchmark.custom_envs.slimevolley.audit --format json" in payload["promotion_checks"]

    prior_ranges = [
        range(0, 20),
        range(1000, 1050),
        range(2000, 2050),
    ]
    prior_ranges.extend(
        range(int(spec["start"]), int(spec["stop_exclusive"]))
        for spec in GENERATION_2_SEED_SPLITS.values()
    )
    for spec in GENERATION_3_SEED_SPLITS.values():
        current = range(int(spec["start"]), int(spec["stop_exclusive"]))
        assert all(current.start >= prior.stop or prior.start >= current.stop for prior in prior_ranges)

    markdown = render_generation_3_protocol_markdown(payload)
    assert "SlimeVolley Generation-3 Protocol" in markdown
    assert "Generation-1 holdout is already opened" in markdown
    assert "Generation-2 holdout is already opened" in markdown
    assert "6000..6049" in markdown
    assert "7000..7049" in markdown
    assert "holdout_g3_final.json" in markdown
    assert "hl_benchmark.custom_envs.slimevolley.audit" in markdown

    paths = write_generation_3_protocol(
        json_path=tmp_path / "generation_3_protocol.json",
        markdown_path=tmp_path / "generation_3_protocol.md",
    )
    assert paths["json"].exists()
    assert paths["markdown"].exists()


def test_slimevolley_generation_4_protocol_generation(tmp_path) -> None:
    payload = generation_4_protocol_payload()
    assert payload["protocol_id"] == "slimevolley-g4"
    assert payload["status"] == "predeclared-not-run"
    assert payload["created_by"] == "hl_benchmark.custom_envs.slimevolley.protocol"
    assert payload["generation_4"]["ledger"].endswith("generation_4_trials.jsonl")
    assert payload["generation_4"]["summary"].endswith("generation_4_summary.csv")
    assert payload["generation_4"]["seed_splits"]["dev"]["label"] == "9000..9049"
    assert payload["generation_4"]["seed_splits"]["holdout"]["label"] == "10000..10049"
    assert payload["generation_4"]["seed_splits"]["audit"]["label"] == "11000..11049"
    assert "improved-v3" in payload["generation_4"]["development_opponents"]
    assert "improved-v4" in payload["generation_4"]["development_opponents"]
    assert "improved-v5" in payload["generation_4"]["development_opponents"]
    assert "improved-v6" in payload["generation_4"]["development_opponents"]
    assert "rally-serve" in payload["generation_4"]["policies"]
    assert "rally-serve" in payload["generation_4"]["development_opponents"]
    assert "Do not inspect generation-4 holdout" in " ".join(payload["guardrails"])
    assert "generation_4_trials.jsonl" in payload["commands"]["dev_builtin_trace"]
    assert "--policies random initial improved improved-tuned attack rally-serve baseline-rnn" in payload["commands"]["final_holdout_once"]
    assert "--seed-start 10000" in payload["commands"]["final_holdout_once"]
    assert "python3 -m hl_benchmark.custom_envs.slimevolley.audit --format json" in payload["promotion_checks"]

    prior_ranges = [
        range(0, 20),
        range(1000, 1050),
        range(2000, 2050),
    ]
    prior_ranges.extend(
        range(int(spec["start"]), int(spec["stop_exclusive"]))
        for spec in GENERATION_2_SEED_SPLITS.values()
    )
    prior_ranges.extend(
        range(int(spec["start"]), int(spec["stop_exclusive"]))
        for spec in GENERATION_3_SEED_SPLITS.values()
    )
    for spec in GENERATION_4_SEED_SPLITS.values():
        current = range(int(spec["start"]), int(spec["stop_exclusive"]))
        assert all(current.start >= prior.stop or prior.start >= current.stop for prior in prior_ranges)

    markdown = render_generation_4_protocol_markdown(payload)
    assert "SlimeVolley Generation-4 Protocol" in markdown
    assert "Generation-1 holdout is already opened" in markdown
    assert "Generation-2 holdout is already opened" in markdown
    assert "Generation-3 holdout is already opened" in markdown
    assert "9000..9049" in markdown
    assert "10000..10049" in markdown
    assert "holdout_g4_final.json" in markdown
    assert "rally-serve" in markdown
    assert "hl_benchmark.custom_envs.slimevolley.audit" in markdown

    paths = write_generation_4_protocol(
        json_path=tmp_path / "generation_4_protocol.json",
        markdown_path=tmp_path / "generation_4_protocol.md",
    )
    assert paths["json"].exists()
    assert paths["markdown"].exists()



def test_slimevolley_generation_5_protocol_generation(tmp_path) -> None:
    payload = generation_5_protocol_payload()
    assert payload["protocol_id"] == "slimevolley-g5"
    assert payload["status"] == "predeclared-not-run"
    assert payload["created_by"] == "hl_benchmark.custom_envs.slimevolley.protocol"
    assert payload["generation_5"]["ledger"].endswith("generation_5_trials.jsonl")
    assert payload["generation_5"]["summary"].endswith("generation_5_summary.csv")
    assert payload["generation_5"]["seed_splits"]["dev"]["label"] == "12000..12049"
    assert payload["generation_5"]["seed_splits"]["holdout"]["label"] == "13000..13049"
    assert payload["generation_5"]["seed_splits"]["audit"]["label"] == "14000..14049"
    assert payload["generation_5"]["policy_start"] == "rally-serve"
    assert "rally-serve" in payload["generation_5"]["policies"]
    assert "baseline-rnn" in payload["generation_5"]["policies"]
    assert "net-pressure" in payload["generation_5"]["policies"]
    assert "net-pressure" in payload["generation_5"]["development_opponents"]
    assert "Do not use generation-4 audit seeds" in " ".join(payload["guardrails"])
    assert "Do not inspect generation-5 holdout" in " ".join(payload["guardrails"])
    assert "generation_5_trials.jsonl" in payload["commands"]["dev_builtin_trace"]
    assert "generation_5_trials.jsonl" in payload["commands"]["development_rnn_comparator"]
    assert "--seed-start 12000" in payload["commands"]["dev_builtin_trace"]
    assert "--policies random initial improved improved-tuned attack rally-serve net-pressure baseline-rnn" in payload["commands"]["final_holdout_once"]
    assert "--seed-start 13000" in payload["commands"]["final_holdout_once"]

    prior_ranges = [
        range(0, 20),
        range(1000, 1050),
        range(2000, 2050),
    ]
    for split_group in (GENERATION_2_SEED_SPLITS, GENERATION_3_SEED_SPLITS, GENERATION_4_SEED_SPLITS):
        prior_ranges.extend(
            range(int(spec["start"]), int(spec["stop_exclusive"]))
            for spec in split_group.values()
        )
    for spec in GENERATION_5_SEED_SPLITS.values():
        current = range(int(spec["start"]), int(spec["stop_exclusive"]))
        assert all(current.start >= prior.stop or prior.start >= current.stop for prior in prior_ranges)

    markdown = render_generation_5_protocol_markdown(payload)
    assert "SlimeVolley Generation-5 Protocol" in markdown
    assert "Generation-4 holdout is already opened" in markdown
    assert "12000..12049" in markdown
    assert "13000..13049" in markdown
    assert "14000..14049" in markdown
    assert "holdout_g5_final.json" in markdown
    assert "rally-serve" in markdown
    assert "baseline-rnn" in markdown
    assert "net-pressure" in markdown

    paths = write_generation_5_protocol(
        json_path=tmp_path / "generation_5_protocol.json",
        markdown_path=tmp_path / "generation_5_protocol.md",
    )
    assert paths["json"].exists()
    assert paths["markdown"].exists()



def test_slimevolley_generation_2_diagnosis_report_generation(tmp_path) -> None:
    ledger_path = tmp_path / "generation_2_trials.jsonl"
    summary_path = tmp_path / "generation_2_summary.csv"
    holdout_path = tmp_path / "holdout_g2_final.json"
    output_path = tmp_path / "generation_2_diagnosis.md"
    ledger_path.write_text(
        json.dumps(
            {
                "timestamp": "2026-05-25T17:49:30+00:00",
                "seed_range": {
                    "split": "dev",
                    "start": 3000,
                    "stop_exclusive": 3050,
                    "seeds": list(range(3000, 3050)),
                },
                "environment": "SlimeVolley-v0",
                "policy_version": "improved",
                "opponent_name": "builtin",
                "pass_fail": "fail",
                "episodes": 50,
                "environment_steps": 0,
                "wall_clock_seconds": 0.01,
                "score_stats": {"mean": None, "std": None, "median": None, "min": None, "max": None},
                "win_loss_draw": {"wins": 0, "losses": 0, "draws": 0},
                "git_commit": "test",
                "diff_identifier": "test",
                "tests_run": TESTS_RUN_FIXTURE,
                "change_summary": "Generation-2 dependency failure fixture.",
                "failure_analysis": "SlimeVolleyDependencyError: SlimeVolley requires optional legacy dependencies: gym and slimevolleygym.",
                "next_hypothesis": "Install optional dependencies before rerunning development traces.",
                "change_type": "logging/diagnostics change",
                "tests_pass_fail": "pass",
                "agent_iterations": 0,
                "code_edits": 0,
                "llm_cost": {
                    "calls": "unavailable",
                    "prompt_tokens": "unavailable",
                    "completion_tokens": "unavailable",
                    "total_tokens": "unavailable",
                    "source": "test fixture",
                },
                "runtime_metadata": {
                    "python": "test-python",
                    "platform": "test-platform",
                    "packages": {"gym": "not_installed", "slimevolleygym": "not_installed"},
                },
                "config": {
                    "dependency_versions": {
                        "gym": "not_installed",
                        "slimevolleygym": "not_installed",
                    }
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    summary_path.write_text("timestamp,pass_fail\n2026-05-25T17:49:30+00:00,fail\n", encoding="utf-8")

    report = render_generation_2_diagnosis_report(
        ledger_path=ledger_path,
        summary_path=summary_path,
        holdout_path=holdout_path,
    )
    assert "SlimeVolley Generation-2 Diagnosis" in report
    for section in GENERATION_REPORT_SECTIONS:
        assert section in report
    assert "generated from persisted generation-2 artifacts only" in report
    assert "generation_2_trials.jsonl" in report
    assert "generation_2_summary.csv" in report
    assert "holdout_g2_final.json" in report
    assert "No generation-2 holdout evidence" in report
    assert "do not inspect generation-2 holdout" in report
    assert "SlimeVolleyDependencyError" in report
    assert "not policy-performance evidence" in report
    assert "Install or activate the optional legacy SlimeVolley stack" in report

    written = write_generation_2_diagnosis_report(
        output_path=output_path,
        ledger_path=ledger_path,
        summary_path=summary_path,
        holdout_path=holdout_path,
    )
    assert written == output_path
    assert output_path.exists()





def test_slimevolley_generation_3_diagnosis_report_generation(tmp_path) -> None:
    ledger_path = tmp_path / "generation_3_trials.jsonl"
    summary_path = tmp_path / "generation_3_summary.csv"
    holdout_path = tmp_path / "holdout_g3_final.json"
    output_path = tmp_path / "generation_3_diagnosis.md"
    ledger_path.write_text(
        json.dumps(
            {
                "timestamp": "2026-05-25T19:24:38+00:00",
                "seed_range": {
                    "split": "dev",
                    "start": 6000,
                    "stop_exclusive": 6050,
                    "seeds": list(range(6000, 6050)),
                },
                "environment": "SlimeVolley-v0",
                "policy_version": "improved",
                "opponent_name": "builtin",
                "pass_fail": "pass",
                "episodes": 50,
                "environment_steps": 113541,
                "wall_clock_seconds": 7.2,
                "score_stats": {"mean": -4.24, "std": 1.0, "median": -5.0, "min": -5.0, "max": 0.0},
                "win_loss_draw": {"wins": 0, "losses": 49, "draws": 1},
                "git_commit": "test",
                "diff_identifier": "test",
                "tests_run": TESTS_RUN_FIXTURE,
                "change_summary": "Generation-3 development diagnostic fixture.",
                "failure_analysis": "No failure observed.",
                "next_hypothesis": "Inspect development traces before any structural edit.",
                "change_type": "structural policy improvement",
                "tests_pass_fail": "pass",
                "agent_iterations": 0,
                "code_edits": 0,
                "llm_cost": {
                    "calls": "unavailable",
                    "prompt_tokens": "unavailable",
                    "completion_tokens": "unavailable",
                    "total_tokens": "unavailable",
                    "source": "test fixture",
                },
                "runtime_metadata": {
                    "python": "test-python",
                    "platform": "test-platform",
                    "packages": {"gym": "0.20.0", "slimevolleygym": "0.1.0"},
                },
                "config": {
                    "dependency_versions": {
                        "gym": "0.20.0",
                        "slimevolleygym": "0.1.0",
                    }
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    summary_path.write_text("timestamp,pass_fail\n2026-05-25T19:24:38+00:00,pass\n", encoding="utf-8")

    report = render_generation_3_diagnosis_report(
        ledger_path=ledger_path,
        summary_path=summary_path,
        holdout_path=holdout_path,
    )
    assert "SlimeVolley Generation-3 Diagnosis" in report
    for section in GENERATION_REPORT_SECTIONS:
        assert section in report
    assert "persisted generation-3 artifacts only" in report
    assert "generation_3_trials.jsonl" in report
    assert "generation_3_summary.csv" in report
    assert "holdout_g3_final.json" in report
    assert "No generation-3 holdout evidence" in report
    assert "do not inspect generation-3 holdout" in report
    assert "6000" in report
    assert "113541" in report

    written = write_generation_3_diagnosis_report(
        output_path=output_path,
        ledger_path=ledger_path,
        summary_path=summary_path,
        holdout_path=holdout_path,
    )
    assert written == output_path
    assert output_path.exists()


def test_slimevolley_performance_report_generation(tmp_path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    holdout_path = tmp_path / "holdout_final.json"
    tournament_path = tmp_path / "round_robin_dev.json"
    search_path = tmp_path / "search_best_dev.json"
    output_path = tmp_path / "performance_deepdive.md"

    evaluate_slimevolley(
        policy_name="initial",
        opponent_name="builtin",
        split="smoke",
        ledger_path=ledger_path,
        summary_path=summary_path,
        env_factory=FakeSlimeVolleyEnv,
        tests_run=TESTS_RUN_FIXTURE,
    )
    holdout_path.write_text(
        json.dumps(
            {
                "split": "holdout",
                "matchup_count": 6,
                "episodes_per_matchup": 50,
                "cells": [
                    {"policy": "initial", "opponent": "builtin", "mean": -4.88, "win_rate": 0.0, "wins": 0, "losses": 50, "draws": 0, "episodes": 50, "environment_steps": 10},
                    {"policy": "tuned", "opponent": "builtin", "mean": -4.8, "win_rate": 0.0, "wins": 0, "losses": 50, "draws": 0, "episodes": 50, "environment_steps": 10},
                    {"policy": "improved", "opponent": "builtin", "mean": -4.78, "win_rate": 0.0, "wins": 0, "losses": 50, "draws": 0, "episodes": 50, "environment_steps": 10},
                    {"policy": "baseline-rnn", "opponent": "builtin", "mean": 0.06, "win_rate": 0.34, "wins": 17, "losses": 14, "draws": 19, "episodes": 50, "environment_steps": 10},
                    {"policy": "initial", "opponent": "random", "mean": 1.76, "win_rate": 0.74, "wins": 37, "losses": 13, "draws": 0, "episodes": 50, "environment_steps": 10},
                    {"policy": "improved", "opponent": "random", "mean": 3.0, "win_rate": 0.92, "wins": 46, "losses": 4, "draws": 0, "episodes": 50, "environment_steps": 10},
                ],
            }
        ),
        encoding="utf-8",
    )
    tournament_path.write_text(
        json.dumps(
            {
                "split": "dev",
                "participants": ["initial", "improved"],
                "matchup_count": 4,
                "standings": [
                    {"policy": "improved", "mean_score_across_opponents": 1.5, "win_rate": 0.7, "wins": 28, "losses": 12, "draws": 0, "environment_steps": 100},
                    {"policy": "initial", "mean_score_across_opponents": -0.5, "win_rate": 0.4, "wins": 16, "losses": 24, "draws": 0, "environment_steps": 100},
                ],
            }
        ),
        encoding="utf-8",
    )
    search_path.write_text(
        json.dumps(
            {
                "split": "dev",
                "candidate_count": 8,
                "candidate_index": 1,
                "selection_score": 0.0875,
                "opponents": ["builtin", "random"],
                "config": {"home_x": 1.05, "contact_x_window": 0.18, "landing_horizon": 0.3},
                "opponent_means": {"builtin": -4.95, "random": 2.75},
            }
        ),
        encoding="utf-8",
    )

    report = render_slimevolley_performance_report(
        ledger_path=ledger_path,
        holdout_path=holdout_path,
        tournament_path=tournament_path,
        search_best_path=search_path,
    )
    assert "SlimeVolley Performance Deep Dive" in report
    for section in PERFORMANCE_REPORT_SECTIONS:
        assert section in report
    assert "generated from existing artifacts only" in report
    assert "do not use it for policy tuning" in report
    assert "holdout_final.json" in report
    assert "round_robin_dev.json" in report
    assert "search_best_dev.json" in report
    assert "improved vs initial" in report
    assert "improved vs tuned scalar baseline" in report
    assert "baseline-rnn" in report
    assert "not deep-RL comparable" in report
    assert "Score bar" in report

    written = write_slimevolley_performance_report(
        output_path=output_path,
        ledger_path=ledger_path,
        holdout_path=holdout_path,
        tournament_path=tournament_path,
        search_best_path=search_path,
    )
    assert written == output_path
    assert output_path.exists()





def test_slimevolley_canonical_change_types_are_shared_for_audit_and_report() -> None:
    assert "structural policy improvement" in CANONICAL_CHANGE_TYPES
    assert "scalar/config tuning" in CANONICAL_CHANGE_TYPES
    assert "evaluation-harness change" in CANONICAL_CHANGE_TYPES
    assert "neural/RL baseline" not in CANONICAL_CHANGE_TYPES
    assert NEURAL_BASELINE_CHANGE_TYPE in LEGACY_NONCANONICAL_CHANGE_TYPES
    assert "logging/diagnostics" in LEGACY_NONCANONICAL_CHANGE_TYPES


def test_slimevolley_summary_command_regenerates_csv_from_ledger(tmp_path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    evaluate_slimevolley(
        policy_name="initial",
        opponent_name="builtin",
        split="smoke",
        ledger_path=ledger_path,
        summary_path=summary_path,
        env_factory=FakeSlimeVolleyEnv,
        tests_run=TESTS_RUN_FIXTURE,
    )
    summary_path.unlink()
    result = summarize_slimevolley_ledger(
        ledger_path=ledger_path,
        summary_path=summary_path,
    )
    assert result["pass_fail"] == "pass"
    assert result["ledger_rows"] == 1
    assert result["summary_rows"] == 1
    summary_text = summary_path.read_text(encoding="utf-8")
    assert "builtin" in summary_text
    assert "tests_pass_fail" in summary_text.splitlines()[0]
    assert "not_recorded" in summary_text
    rendered = render_summary_text(result)
    assert "SlimeVolley summary regeneration: pass" in rendered

    with pytest.raises(FileNotFoundError):
        summarize_slimevolley_ledger(
            ledger_path=tmp_path / "missing.jsonl",
            summary_path=tmp_path / "missing.csv",
        )


def test_slimevolley_specific_ledger_schema_validates_opponent_fields(tmp_path) -> None:
    entry = evaluate_slimevolley(
        policy_name="initial",
        opponent_name="builtin",
        split="smoke",
        ledger_path=tmp_path / "trials.jsonl",
        summary_path=tmp_path / "summary.csv",
        env_factory=FakeSlimeVolleyEnv,
        tests_run=TESTS_RUN_FIXTURE,
    )
    assert validate_slimevolley_ledger_entry(entry) == []

    missing_opponent = dict(entry)
    del missing_opponent["opponent_name"]
    assert "missing SlimeVolley ledger field: opponent_name" in (
        validate_slimevolley_ledger_entry(missing_opponent)
    )

    bad_wld = dict(entry)
    bad_wld["win_loss_draw"] = dict(entry["win_loss_draw"], wins=0, losses=0, draws=0)
    assert "win/loss/draw total does not match episodes" in (
        validate_slimevolley_ledger_entry(bad_wld)
    )

    bad_wld_count = dict(entry)
    bad_wld_count["win_loss_draw"] = dict(entry["win_loss_draw"], wins=-1)
    assert "win_loss_draw.wins is not a non-negative integer" in (
        validate_slimevolley_ledger_entry(bad_wld_count)
    )

    mismatched_win_rate = dict(entry)
    expected_wrong_rate = 0.0 if entry["win_loss_draw"]["win_rate"] != 0.0 else 1.0
    mismatched_win_rate["win_loss_draw"] = dict(
        entry["win_loss_draw"],
        win_rate=expected_wrong_rate,
    )
    assert "win_loss_draw.win_rate does not match wins/episodes" in (
        validate_slimevolley_ledger_entry(mismatched_win_rate)
    )

    bad_score_stats = dict(entry)
    bad_score_stats["score_stats"] = dict(entry["score_stats"], mean="high")
    assert "score_stats.mean is not numeric or null" in (
        validate_slimevolley_ledger_entry(bad_score_stats)
    )

    bad_life_stats = dict(entry)
    bad_life_stats["life_difference_stats"] = dict(
        entry["life_difference_stats"],
        mean="ahead",
    )
    assert "life_difference_stats.mean is not numeric or null" in (
        validate_slimevolley_ledger_entry(bad_life_stats)
    )

    bad_actions = dict(entry)
    bad_actions["action_frequencies"] = {"001": -1}
    assert "action_frequencies count for '001' is not a non-negative integer" in (
        validate_slimevolley_ledger_entry(bad_actions)
    )

    bad_per_episode_type = dict(entry)
    bad_per_episode_type["per_episode"] = "missing"
    assert "passing row per_episode is missing or not a list" in (
        validate_slimevolley_ledger_entry(bad_per_episode_type)
    )

    bad_episode_fields = dict(entry)
    bad_episode_fields["per_episode"] = [dict(episode) for episode in entry["per_episode"]]
    bad_episode_fields["per_episode"][0] = dict(
        bad_episode_fields["per_episode"][0],
        seed=True,
        score="high",
        life_difference="wide",
        steps=-1,
        outcome="maybe",
        action_counts={"001": -1},
        point_events=[{"step": -1, "reward": "one", "outcome": "maybe", "action": ""}],
    )
    bad_episode_issues = " ".join(validate_slimevolley_ledger_entry(bad_episode_fields))
    assert "per_episode[1].seed is not an integer" in bad_episode_issues
    assert "per_episode[1].score is not numeric" in bad_episode_issues
    assert "per_episode[1].life_difference is not numeric" in bad_episode_issues
    assert "per_episode[1].steps is not a non-negative integer" in bad_episode_issues
    assert "per_episode[1].outcome is not one of" in bad_episode_issues
    assert "per_episode[1].action_counts count for '001' is not a non-negative integer" in bad_episode_issues
    assert "per_episode[1].point_events[1].step is not a non-negative integer" in bad_episode_issues
    assert "per_episode[1].point_events[1].reward is not numeric" in bad_episode_issues
    assert "per_episode[1].point_events[1].outcome is not one of" in bad_episode_issues
    assert "per_episode[1].point_events[1].action is missing or empty" in bad_episode_issues

    bad_point_event_step = json.loads(json.dumps(entry))
    bad_point_event_step["per_episode"][0]["point_events"][0]["step"] = (
        bad_point_event_step["per_episode"][0]["steps"]
    )
    assert "per_episode[1].point_events[1].step is outside episode step range" in (
        validate_slimevolley_ledger_entry(bad_point_event_step)
    )

    bad_point_event_reward_sign = json.loads(json.dumps(entry))
    bad_point_event_reward_sign["per_episode"][0]["point_events"][0]["reward"] = -1.0
    assert "per_episode[1].point_events[1].outcome does not match negative reward" in (
        validate_slimevolley_ledger_entry(bad_point_event_reward_sign)
    )

    zero_point_event_reward = json.loads(json.dumps(entry))
    zero_point_event_reward["per_episode"][0]["point_events"][0]["reward"] = 0.0
    assert "per_episode[1].point_events[1].reward is zero despite point event" in (
        validate_slimevolley_ledger_entry(zero_point_event_reward)
    )

    mismatched_episode_actions = dict(entry)
    mismatched_episode_actions["per_episode"] = [dict(episode) for episode in entry["per_episode"]]
    mismatched_episode_actions["per_episode"][0] = dict(
        mismatched_episode_actions["per_episode"][0],
        action_counts={"001": 0},
    )
    assert "per_episode[1].action_counts total does not match environment steps" in (
        validate_slimevolley_ledger_entry(mismatched_episode_actions)
    )

    mismatched_top_level_actions = dict(entry)
    mismatched_top_level_actions["action_frequencies"] = {"001": 0}
    assert "action_frequencies total does not match environment steps" in (
        validate_slimevolley_ledger_entry(mismatched_top_level_actions)
    )

    mismatched_top_level_opponent_actions = dict(entry)
    mismatched_top_level_opponent_actions["opponent_action_frequencies"] = {"000": 0}
    assert "opponent_action_frequencies total does not match environment steps" in (
        validate_slimevolley_ledger_entry(mismatched_top_level_opponent_actions)
    )

    mismatched_episode_opponent_actions = dict(entry)
    mismatched_episode_opponent_actions["per_episode"] = [
        dict(episode) for episode in entry["per_episode"]
    ]
    mismatched_episode_opponent_actions["per_episode"][0] = dict(
        mismatched_episode_opponent_actions["per_episode"][0],
        opponent_action_counts={"000": 0},
    )
    assert "per_episode[1].opponent_action_counts total does not match environment steps" in (
        validate_slimevolley_ledger_entry(mismatched_episode_opponent_actions)
    )

    missing_episode_opponent_actions = dict(entry)
    missing_episode_opponent_actions["per_episode"] = [
        dict(episode) for episode in entry["per_episode"]
    ]
    del missing_episode_opponent_actions["per_episode"][0]["opponent_action_counts"]
    assert "per_episode[1].opponent_action_counts is missing or not an object" in (
        validate_slimevolley_ledger_entry(missing_episode_opponent_actions)
    )

    explicit_opponent_without_actions = dict(entry)
    explicit_opponent_without_actions["opponent_name"] = "random"
    explicit_opponent_without_actions["opponent_action_frequencies"] = {}
    explicit_opponent_without_actions["per_episode"] = [
        dict(episode) for episode in entry["per_episode"]
    ]
    explicit_opponent_issues = " ".join(
        validate_slimevolley_ledger_entry(explicit_opponent_without_actions)
    )
    assert (
        "opponent_action_frequencies is empty for explicit opponent policy"
        in explicit_opponent_issues
    )
    assert (
        "per_episode[1].opponent_action_counts is empty for explicit opponent policy"
        in explicit_opponent_issues
    )

    mismatched_per_episode_seeds = dict(entry)
    mismatched_per_episode_seeds["per_episode"] = [
        dict(episode) for episode in entry["per_episode"]
    ]
    mismatched_per_episode_seeds["per_episode"][0]["seed"] = 999
    assert "per_episode seeds do not match seed_range.seeds" in (
        validate_slimevolley_ledger_entry(mismatched_per_episode_seeds)
    )

    mismatched_per_episode_steps_total = dict(entry)
    mismatched_per_episode_steps_total["environment_steps"] = entry["environment_steps"] + 1
    adjusted_actions = dict(entry["action_frequencies"])
    first_action = next(iter(adjusted_actions))
    adjusted_actions[first_action] += 1
    mismatched_per_episode_steps_total["action_frequencies"] = adjusted_actions
    assert "per_episode steps total does not match environment_steps" in (
        validate_slimevolley_ledger_entry(mismatched_per_episode_steps_total)
    )

    mismatched_per_episode_outcomes = dict(entry)
    mismatched_per_episode_outcomes["per_episode"] = [
        dict(episode) for episode in entry["per_episode"]
    ]
    original_outcome = mismatched_per_episode_outcomes["per_episode"][0]["outcome"]
    mismatched_per_episode_outcomes["per_episode"][0]["outcome"] = (
        "loss" if original_outcome != "loss" else "win"
    )
    assert "per_episode outcomes do not match win_loss_draw" in (
        validate_slimevolley_ledger_entry(mismatched_per_episode_outcomes)
    )

    mismatched_score_stats_from_episodes = dict(entry)
    mismatched_score_stats_from_episodes["score_stats"] = dict(
        entry["score_stats"],
        mean=entry["score_stats"]["mean"] + 1.0,
    )
    assert "score_stats.mean does not match per_episode scores" in (
        validate_slimevolley_ledger_entry(mismatched_score_stats_from_episodes)
    )

    mismatched_life_stats_from_episodes = dict(entry)
    mismatched_life_stats_from_episodes["life_difference_stats"] = dict(
        entry["life_difference_stats"],
        max=entry["life_difference_stats"]["max"] + 1.0,
    )
    assert "life_difference_stats.max does not match per_episode life_difference values" in (
        validate_slimevolley_ledger_entry(mismatched_life_stats_from_episodes)
    )

    missing_cost = dict(entry)
    del missing_cost["llm_cost"]
    assert "llm_cost is missing or not an object" in (
        validate_slimevolley_ledger_entry(missing_cost)
    )

    bad_cost = dict(entry)
    bad_cost["llm_cost"] = dict(entry["llm_cost"], total_tokens=-1, source="")
    bad_cost_issues = " ".join(validate_slimevolley_ledger_entry(bad_cost))
    assert "llm_cost.total_tokens is not a non-negative integer or 'unavailable'" in bad_cost_issues
    assert "llm_cost.source is missing or empty" in bad_cost_issues

    numeric_cost = dict(entry)
    numeric_cost["llm_cost"] = {
        "calls": 2,
        "prompt_tokens": 100,
        "completion_tokens": 25,
        "total_tokens": 125,
        "source": "test fixture",
    }
    assert validate_slimevolley_ledger_entry(numeric_cost) == []

    mismatched_token_total = dict(numeric_cost)
    mismatched_token_total["llm_cost"] = dict(
        numeric_cost["llm_cost"],
        total_tokens=126,
    )
    assert "llm_cost.total_tokens does not match prompt_tokens + completion_tokens" in (
        validate_slimevolley_ledger_entry(mismatched_token_total)
    )

    missing_numeric_total = dict(numeric_cost)
    missing_numeric_total["llm_cost"] = dict(
        numeric_cost["llm_cost"],
        total_tokens="unavailable",
    )
    assert "llm_cost.total_tokens is unavailable despite numeric prompt/completion tokens" in (
        validate_slimevolley_ledger_entry(missing_numeric_total)
    )

    total_only_cost = dict(entry)
    total_only_cost["llm_cost"] = {
        "calls": 1,
        "prompt_tokens": "unavailable",
        "completion_tokens": "unavailable",
        "total_tokens": 200,
        "source": "total-only provider",
    }
    assert validate_slimevolley_ledger_entry(total_only_cost) == []

    bad_agent_cost = dict(entry)
    bad_agent_cost["agent_iterations"] = -1
    bad_agent_cost["code_edits"] = True
    bad_agent_cost_issues = " ".join(validate_slimevolley_ledger_entry(bad_agent_cost))
    assert "agent_iterations is not a non-negative integer" in bad_agent_cost_issues
    assert "code_edits is not a non-negative integer" in bad_agent_cost_issues

    bad_provenance = dict(entry)
    bad_provenance["git_commit"] = ""
    bad_provenance["diff_identifier"] = None
    bad_provenance["tests_run"] = ["pytest", ""]
    bad_provenance_issues = " ".join(validate_slimevolley_ledger_entry(bad_provenance))
    assert "git_commit is missing or empty" in bad_provenance_issues
    assert "diff_identifier is missing or empty" in bad_provenance_issues
    assert "tests_run contains a non-string or empty command" in bad_provenance_issues

    bad_core = dict(entry)
    bad_core["timestamp"] = ""
    bad_core["policy_version"] = ""
    bad_core["config"] = []
    bad_core["pass_fail"] = "maybe"
    bad_core["change_summary"] = ""
    bad_core["failure_analysis"] = ""
    bad_core["next_hypothesis"] = ""
    bad_core["change_type"] = ""
    bad_core_issues = " ".join(validate_slimevolley_ledger_entry(bad_core))
    assert "timestamp is missing or empty" in bad_core_issues
    assert "policy_version is missing or empty" in bad_core_issues
    assert "config is missing or not an object" in bad_core_issues
    assert "pass_fail is not 'pass' or 'fail'" in bad_core_issues
    assert "change_summary is missing or empty" in bad_core_issues
    assert "failure_analysis is missing or empty" in bad_core_issues
    assert "next_hypothesis is missing or empty" in bad_core_issues
    assert "change_type is missing or empty" in bad_core_issues

    unknown_change_type = dict(entry)
    unknown_change_type["change_type"] = "legacy typo"
    assert "change_type 'legacy typo' is not a recognized SlimeVolley change type" in (
        validate_slimevolley_ledger_entry(unknown_change_type)
    )

    legacy_change_type = dict(entry)
    legacy_change_type["change_type"] = NEURAL_BASELINE_CHANGE_TYPE
    assert validate_slimevolley_ledger_entry(legacy_change_type) == []

    bad_seed_range = dict(entry)
    bad_seed_range["seed_range"] = {
        "split": "",
        "start": 99,
        "stop_exclusive": 100,
        "seeds": [0, True],
    }
    bad_seed_range_issues = " ".join(validate_slimevolley_ledger_entry(bad_seed_range))
    assert "seed_range.split is missing or empty" in bad_seed_range_issues
    assert "seed_range.seeds is missing or not a list of integers" in bad_seed_range_issues

    inconsistent_seed_bounds = dict(entry)
    inconsistent_seed_bounds["seed_range"] = {
        "split": "smoke",
        "start": 99,
        "stop_exclusive": 100,
        "seeds": [0, 1],
    }
    inconsistent_seed_bound_issues = " ".join(
        validate_slimevolley_ledger_entry(inconsistent_seed_bounds)
    )
    assert "seed_range.start does not match the minimum seed" in inconsistent_seed_bound_issues
    assert "seed_range.stop_exclusive does not match the maximum seed plus one" in inconsistent_seed_bound_issues

    missing_config_versions = dict(entry)
    missing_config_versions["config"] = dict(entry["config"], dependency_versions={})
    assert "config.dependency_versions is missing or empty" in (
        validate_slimevolley_ledger_entry(missing_config_versions)
    )

    missing_config_required_package = dict(entry)
    config_versions = dict(entry["config"]["dependency_versions"])
    config_versions.pop("slimevolleygym", None)
    missing_config_required_package["config"] = dict(
        entry["config"],
        dependency_versions=config_versions,
    )
    assert "config.dependency_versions missing required package: slimevolleygym" in (
        validate_slimevolley_ledger_entry(missing_config_required_package)
    )

    bad_runtime_metadata = dict(entry)
    bad_runtime_metadata["runtime_metadata"] = {"python": "", "platform": "", "packages": {}}
    bad_runtime_metadata_issues = " ".join(validate_slimevolley_ledger_entry(bad_runtime_metadata))
    assert "runtime_metadata.python is missing or empty" in bad_runtime_metadata_issues
    assert "runtime_metadata.platform is missing or empty" in bad_runtime_metadata_issues
    assert "runtime_metadata.packages is missing or empty" in bad_runtime_metadata_issues

    missing_runtime_required_package = dict(entry)
    runtime_metadata = dict(entry["runtime_metadata"])
    runtime_packages = dict(runtime_metadata["packages"])
    runtime_packages.pop("numpy", None)
    runtime_metadata["packages"] = runtime_packages
    missing_runtime_required_package["runtime_metadata"] = runtime_metadata
    assert "runtime_metadata.packages missing required package: numpy" in (
        validate_slimevolley_ledger_entry(missing_runtime_required_package)
    )

    bad_runtime_package_value = dict(entry)
    runtime_metadata = dict(entry["runtime_metadata"])
    runtime_metadata["packages"] = dict(runtime_metadata["packages"], numpy="")
    bad_runtime_package_value["runtime_metadata"] = runtime_metadata
    assert "runtime_metadata.packages.'numpy' is missing or not a string" in (
        validate_slimevolley_ledger_entry(bad_runtime_package_value)
    )

    missing_runtime_metadata = dict(entry)
    del missing_runtime_metadata["runtime_metadata"]
    assert "runtime_metadata is missing or not an object" in (
        validate_slimevolley_ledger_entry(missing_runtime_metadata)
    )

    assert entry["tests_pass_fail"] == "not_recorded"

    bad_tests_pass_fail = dict(entry)
    bad_tests_pass_fail["tests_pass_fail"] = "maybe"
    assert "tests_pass_fail is not one of pass, fail, or not_recorded" in (
        validate_slimevolley_ledger_entry(bad_tests_pass_fail)
    )

    recorded_tests_passed = dict(entry)
    recorded_tests_passed["tests_pass_fail"] = "pass"
    assert validate_slimevolley_ledger_entry(recorded_tests_passed) == []

    missing_tests = dict(entry)
    missing_tests["tests_run"] = []
    assert "tests_run is missing or empty" in (
        validate_slimevolley_ledger_entry(missing_tests)
    )

    missing_tests_with_status = dict(missing_tests)
    missing_tests_with_status["tests_pass_fail"] = "pass"
    assert "tests_pass_fail records a status but tests_run is empty" in (
        validate_slimevolley_ledger_entry(missing_tests_with_status)
    )

    legacy_missing_tests_status = dict(entry)
    del legacy_missing_tests_status["tests_pass_fail"]
    assert validate_slimevolley_ledger_entry(legacy_missing_tests_status) == []

    failed_without_analysis = dict(entry)
    failed_without_analysis["pass_fail"] = "fail"
    failed_without_analysis["failure_analysis"] = "No failure observed."
    failed_without_analysis["next_hypothesis"] = ""
    joined = " ".join(validate_slimevolley_ledger_entry(failed_without_analysis))
    assert "failed row is missing specific failure_analysis" in joined
    assert "failed row is missing next_hypothesis" in joined


def test_slimevolley_artifact_audit_validates_ledger_summary_and_report(tmp_path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    report_path = tmp_path / "final_report.md"
    diagnostics_path = tmp_path / "environment_diagnostics.json"
    diagnostics_path.write_text(
        '{"status":"unavailable","message":"missing deps","packages":{"slimevolleygym":"not_installed"},"expected_observation_space":"Box(12)","expected_action_space":"MultiBinary(3)","expected_step_api":"legacy","reward_semantics":"point reward","seed_api_behavior":"not probed; unavailable","same_seed_reset_observation_equal":false,"observed_step_api":"unavailable","multiagent_step_api_observed":"unavailable","runtime_metadata":{"python":"test-python","platform":"test-platform","packages":{"slimevolleygym":"not_installed"}}}',
        encoding="utf-8",
    )
    evaluate_slimevolley(
        policy_name="initial",
        opponent_name="builtin",
        split="smoke",
        ledger_path=ledger_path,
        summary_path=summary_path,
        env_factory=FakeSlimeVolleyEnv,
        tests_run=TESTS_RUN_FIXTURE,
    )
    render_slimevolley_report(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
        holdout_path=tmp_path / "missing_holdout.json",
    )
    write_requirements_audit_fixture(report_path.with_name("requirements_audit.md"))
    experiment_readme_path = report_path.with_name("README.md")
    experiment_readme_path.write_text(
        "# SlimeVolley Experiment\n\n"
        "## Current Code Paths\n\n"
        "- Registered custom harness bridge: `hl_benchmark/custom_envs/slimevolley/`.\n"
        "- Registry-facing custom harness bridge delegates to `hl_benchmark/slimevolley/`.\n"
        "- Evaluation CLI: `python -m hl_benchmark.custom_envs.slimevolley.evaluate`.\n\n"
        "## Current Reproduction Commands\n\n"
        "- `make slimevolley-verify` writes `results/audit_latest.json` with "
        "`requirements_audit_status_counts`, `requirements_audit_partial_rows`, "
        "`requirements_audit_completion_state`, `requirements_audit_completion_recommendation`, "
        "`requirements_audit_partial_row_details`, and `requirements_audit_partial_row_classifications`.\n\n"
        "## Artifact Manifest\n\n"
        "| Artifact | Purpose |\n"
        "| --- | --- |\n"
        "| `hl_benchmark/custom_envs/slimevolley/` | Registry-facing custom harness bridge |\n"
        "| `results/audit_latest.json` | Machine-readable audit snapshot with `requirements_audit_status_counts`, `requirements_audit_partial_rows`, `requirements_audit_completion_state`, `requirements_audit_completion_recommendation`, `requirements_audit_partial_row_details`, and `requirements_audit_partial_row_classifications` |\n\n"
        "## Current Guardrails\n\n"
        "- Holdout seeds `1000..1049` remain final-only.\n"
        "- Ledger rows preserve explicit `tests_pass_fail` statuses.\n"
        "- Historical missing status is covered by `results/trial_amendments.jsonl`.\n",
        encoding="utf-8",
    )
    performance_path = report_path.with_name("performance_deepdive.md")
    generation_report_path = report_path.with_name("generation_2_diagnosis.md")
    generation_ledger_path = tmp_path / "generation_2_trials.jsonl"
    generation_summary_path = tmp_path / "generation_2_summary.csv"
    generation_search_path = tmp_path / "search_best_g2_dev.json"
    generation_tournament_path = tmp_path / "round_robin_g2_dev.json"
    generation_holdout_path = tmp_path / "holdout_g2_final.json"
    protocol_path = tmp_path / "generation_2_protocol.json"
    protocol_report_path = report_path.with_name("generation_2_protocol.md")
    generation3_report_path = report_path.with_name("generation_3_diagnosis.md")
    generation3_ledger_path = tmp_path / "generation_3_trials.jsonl"
    generation3_summary_path = tmp_path / "generation_3_summary.csv"
    generation3_search_path = tmp_path / "search_best_g3_dev.json"
    generation3_tournament_path = tmp_path / "round_robin_g3_dev.json"
    generation3_holdout_path = tmp_path / "holdout_g3_final.json"
    generation3_protocol_path = tmp_path / "generation_3_protocol.json"
    generation3_protocol_report_path = report_path.with_name("generation_3_protocol.md")
    generation4_protocol_path = tmp_path / "generation_4_protocol.json"
    generation4_protocol_report_path = report_path.with_name("generation_4_protocol.md")
    contact_diagnostics_json_path = tmp_path / "contact_diagnostics_g3_dev.json"
    contact_diagnostics_report_path = report_path.with_name("contact_diagnostics_g3_dev.md")
    write_slimevolley_performance_report(
        output_path=performance_path,
        ledger_path=ledger_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
    )
    evaluate_slimevolley(
        policy_name="improved",
        opponent_name="builtin",
        split="dev",
        seed_start=3000,
        episodes=50,
        ledger_path=generation_ledger_path,
        summary_path=generation_summary_path,
        env_factory=FakeSlimeVolleyEnv,
        tests_run=TESTS_RUN_FIXTURE,
        tests_pass_fail="pass",
    )
    search_slimevolley_configs(
        split="dev",
        opponents=("builtin",),
        max_candidates=1,
        episodes=50,
        seed_start=3000,
        ledger_path=generation_ledger_path,
        summary_path=generation_summary_path,
        output_path=generation_search_path,
        tests_run=TESTS_RUN_FIXTURE,
        tests_pass_fail="pass",
        env_factory=FakeSlimeVolleyEnv,
    )
    run_slimevolley_tournament(
        split="dev",
        participants=("initial",),
        episodes=50,
        seed_start=3000,
        ledger_path=generation_ledger_path,
        summary_path=generation_summary_path,
        output_path=generation_tournament_path,
        tests_run=TESTS_RUN_FIXTURE,
        tests_pass_fail="pass",
        env_factory=FakeSlimeVolleyEnv,
    )
    write_generation_2_diagnosis_report(
        output_path=generation_report_path,
        ledger_path=generation_ledger_path,
        summary_path=generation_summary_path,
        holdout_path=generation_holdout_path,
    )
    write_generation_2_protocol(
        json_path=protocol_path,
        markdown_path=protocol_report_path,
    )
    evaluate_slimevolley(
        policy_name="improved",
        opponent_name="builtin",
        split="dev",
        seed_start=6000,
        episodes=50,
        ledger_path=generation3_ledger_path,
        summary_path=generation3_summary_path,
        env_factory=FakeSlimeVolleyEnv,
        tests_run=TESTS_RUN_FIXTURE,
        tests_pass_fail="pass",
    )
    search_slimevolley_configs(
        split="dev",
        opponents=("builtin",),
        max_candidates=1,
        episodes=50,
        seed_start=6000,
        ledger_path=generation3_ledger_path,
        summary_path=generation3_summary_path,
        output_path=generation3_search_path,
        tests_run=TESTS_RUN_FIXTURE,
        tests_pass_fail="pass",
        env_factory=FakeSlimeVolleyEnv,
    )
    run_slimevolley_tournament(
        split="dev",
        participants=("initial",),
        episodes=50,
        seed_start=6000,
        ledger_path=generation3_ledger_path,
        summary_path=generation3_summary_path,
        output_path=generation3_tournament_path,
        tests_run=TESTS_RUN_FIXTURE,
        tests_pass_fail="pass",
        env_factory=FakeSlimeVolleyEnv,
    )
    write_generation_3_diagnosis_report(
        output_path=generation3_report_path,
        ledger_path=generation3_ledger_path,
        summary_path=generation3_summary_path,
        holdout_path=generation3_holdout_path,
    )
    write_generation_3_protocol(
        json_path=generation3_protocol_path,
        markdown_path=generation3_protocol_report_path,
    )
    write_generation_4_protocol(
        json_path=generation4_protocol_path,
        markdown_path=generation4_protocol_report_path,
    )
    contact_diagnostics_json_path.write_text(json.dumps({"status": "pass"}) + "\n", encoding="utf-8")
    contact_diagnostics_report_path.write_text("# SlimeVolley Generation-3 Contact/Return Diagnostics\n", encoding="utf-8")
    result = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
        experiment_readme_path=experiment_readme_path,
        performance_report_path=performance_path,
        generation_report_path=generation_report_path,
        generation_ledger_path=generation_ledger_path,
        generation_summary_path=generation_summary_path,
        generation_search_best_path=generation_search_path,
        generation_tournament_path=generation_tournament_path,
        generation_holdout_path=generation_holdout_path,
        generation_protocol_path=protocol_path,
        generation_protocol_report_path=protocol_report_path,
        generation3_report_path=generation3_report_path,
        generation3_ledger_path=generation3_ledger_path,
        generation3_summary_path=generation3_summary_path,
        generation3_search_best_path=generation3_search_path,
        generation3_tournament_path=generation3_tournament_path,
        generation3_holdout_path=generation3_holdout_path,
        generation3_protocol_path=generation3_protocol_path,
        generation3_protocol_report_path=generation3_protocol_report_path,
        generation4_protocol_path=generation4_protocol_path,
        generation4_protocol_report_path=generation4_protocol_report_path,
        contact_diagnostics_json_path=contact_diagnostics_json_path,
        contact_diagnostics_report_path=contact_diagnostics_report_path,
    )
    assert result["pass_fail"] == "pass"
    assert result["ledger_rows"] == 1
    assert result["summary_rows"] == 1
    assert result["tests_pass_fail_counts"] == {"not_recorded": 1}
    assert result["explicit_tests_pass_fail_required_after"] == "2026-05-25T00:00:00+00:00"
    assert result["diagnostics_status"] == "unavailable"
    assert result["artifact_hashes"]["ledger"] != "missing"
    assert result["artifact_hashes"]["summary"] != "missing"
    assert result["artifact_hashes"]["requirements_audit"] != "missing"
    assert result["artifact_hashes"]["experiment_readme"] != "missing"
    assert result["artifact_hashes"]["performance_report"] != "missing"
    assert result["artifact_hashes"]["generation_report"] != "missing"
    assert result["artifact_hashes"]["generation_ledger"] != "missing"
    assert result["artifact_hashes"]["generation_summary"] != "missing"
    assert result["artifact_hashes"]["generation_search_best"] != "missing"
    assert result["artifact_hashes"]["generation_tournament"] != "missing"
    assert result["artifact_hashes"]["generation_holdout"] == "missing"
    assert result["artifact_hashes"]["generation_protocol"] != "missing"
    assert result["artifact_hashes"]["generation_protocol_report"] != "missing"
    assert result["artifact_hashes"]["generation3_report"] != "missing"
    assert result["artifact_hashes"]["generation3_ledger"] != "missing"
    assert result["artifact_hashes"]["generation3_summary"] != "missing"
    assert result["artifact_hashes"]["generation3_search_best"] != "missing"
    assert result["artifact_hashes"]["generation3_tournament"] != "missing"
    assert result["artifact_hashes"]["generation3_holdout"] == "missing"
    assert result["artifact_hashes"]["generation3_protocol"] != "missing"
    assert result["artifact_hashes"]["generation3_protocol_report"] != "missing"
    assert result["artifact_hashes"]["generation4_protocol"] != "missing"
    assert result["artifact_hashes"]["generation4_protocol_report"] != "missing"
    assert result["artifact_hashes"]["contact_diagnostics_json"] != "missing"
    assert result["artifact_hashes"]["contact_diagnostics_report"] != "missing"
    assert result["requirements_audit_path"] == str(report_path.with_name("requirements_audit.md"))
    assert result["requirements_audit_row_count"] == 25
    assert result["requirements_audit_required_row_count"] == 25
    assert result["requirements_audit_status_counts"] == {"Satisfied": 25}
    assert result["requirements_audit_partial_rows"] == []
    assert result["requirements_audit_completion_state"] == "satisfied"
    assert result["requirements_audit_completion_recommendation"] == "eligible_for_completion_audit"
    assert result["requirements_audit_completion_blockers"] == []
    assert result["requirements_audit_partial_row_classifications"] == {}
    assert result["requirements_audit_partial_row_details"] == []
    assert any(
        row["requirement"] == "Replay and diagnostics"
        and row["status"] == "Satisfied"
        for row in result["requirements_audit_rows"]
    )
    assert result["experiment_readme_path"] == str(experiment_readme_path)
    assert result["performance_report_path"] == str(performance_path)
    assert result["generation_report_path"] == str(generation_report_path)
    assert result["generation_ledger_path"] == str(generation_ledger_path)
    assert result["generation_summary_path"] == str(generation_summary_path)
    assert result["generation_search_best_path"] == str(generation_search_path)
    assert result["generation_tournament_path"] == str(generation_tournament_path)
    assert result["generation_holdout_path"] == str(generation_holdout_path)
    assert result["generation_ledger_rows"] == 3
    assert result["generation_summary_rows"] == 3
    assert result["generation_summary_content_checked"] is True
    assert result["generation_split_counts"] == {"dev": 3}
    assert result["generation_holdout_rows"] == 0
    assert result["generation_protocol_path"] == str(protocol_path)
    assert result["generation_protocol_report_path"] == str(protocol_report_path)
    assert result["generation3_report_path"] == str(generation3_report_path)
    assert result["generation3_ledger_path"] == str(generation3_ledger_path)
    assert result["generation3_summary_path"] == str(generation3_summary_path)
    assert result["generation3_search_best_path"] == str(generation3_search_path)
    assert result["generation3_tournament_path"] == str(generation3_tournament_path)
    assert result["generation3_holdout_path"] == str(generation3_holdout_path)
    assert result["generation3_ledger_rows"] == 3
    assert result["generation3_summary_rows"] == 3
    assert result["generation3_summary_content_checked"] is True
    assert result["generation3_split_counts"] == {"dev": 3}
    assert result["generation3_holdout_rows"] == 0
    assert result["generation3_protocol_path"] == str(generation3_protocol_path)
    assert result["generation3_protocol_report_path"] == str(generation3_protocol_report_path)
    assert result["generation4_protocol_path"] == str(generation4_protocol_path)
    assert result["generation4_protocol_report_path"] == str(generation4_protocol_report_path)
    assert result["generation4_protocol_status"] == "predeclared-not-run"
    assert result["generation4_seed_ranges"] == {
        "audit": "11000..11049",
        "dev": "9000..9049",
        "holdout": "10000..10049",
        "smoke": "9000..9001",
    }
    assert result["contact_diagnostics_json_path"] == str(contact_diagnostics_json_path)
    assert result["contact_diagnostics_report_path"] == str(contact_diagnostics_report_path)
    assert result["source_hashes"]["hl_benchmark/artifacts.py"] != "missing"
    assert result["source_hashes"]["hl_benchmark/registry.py"] != "missing"
    assert result["source_hashes"]["hl_benchmark/custom_envs/slimevolley/__init__.py"] != "missing"
    assert result["source_hashes"]["hl_benchmark/policies/base.py"] != "missing"
    assert result["source_hashes"]["hl_benchmark/policies/slimevolley.py"] != "missing"
    assert result["source_hashes"]["hl_benchmark/slimevolley/contact_diagnostics.py"] != "missing"
    assert result["split_counts"] == {"smoke": 1}
    assert "missing scalar-search artifact" in " ".join(result["warnings"])
    text = render_audit_text(result)
    assert "SlimeVolley artifact audit: pass" in text
    assert "Generation-4 protocol status: predeclared-not-run" in text
    assert "'holdout': '10000..10049'" in text
    assert "Requirements audit statuses: {'Satisfied': 25}" in text
    assert "Requirements audit completion state: satisfied" in text
    assert "Requirements audit completion recommendation: eligible_for_completion_audit" in text

    original_experiment_readme = experiment_readme_path.read_text(encoding="utf-8")
    experiment_readme_path.write_text(
        original_experiment_readme.replace(
            "Registry-facing custom harness bridge",
            "Registry-facing custom harness removed",
        ),
        encoding="utf-8",
    )
    missing_readme_snippet = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
        experiment_readme_path=experiment_readme_path,
    )
    assert missing_readme_snippet["pass_fail"] == "fail"
    assert "experiment README missing required snippet" in " ".join(
        missing_readme_snippet["issues"]
    )
    experiment_readme_path.write_text(original_experiment_readme, encoding="utf-8")

    original_performance_report = performance_path.read_text(encoding="utf-8")
    performance_path.write_text(
        original_performance_report.replace("baseline-rnn", "packaged-rnn"),
        encoding="utf-8",
    )
    missing_performance_snippet = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
        performance_report_path=performance_path,
    )
    assert missing_performance_snippet["pass_fail"] == "fail"
    assert "performance report missing required snippet" in " ".join(
        missing_performance_snippet["issues"]
    )
    performance_path.write_text(original_performance_report, encoding="utf-8")

    original_generation_report = generation_report_path.read_text(encoding="utf-8")
    generation_report_path.write_text(
        original_generation_report.replace("generation-2 holdout", "generation-two holdout"),
        encoding="utf-8",
    )
    missing_generation_report_snippet = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
        performance_report_path=performance_path,
        generation_report_path=generation_report_path,
    )
    assert missing_generation_report_snippet["pass_fail"] == "fail"
    assert "generation-2 diagnosis report missing required snippet" in " ".join(
        missing_generation_report_snippet["issues"]
    )
    generation_report_path.write_text(original_generation_report, encoding="utf-8")

    original_protocol_report = protocol_report_path.read_text(encoding="utf-8")
    protocol_report_path.write_text(
        original_protocol_report.replace("4000..4049", "4000..4048"),
        encoding="utf-8",
    )
    missing_protocol_snippet = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
        performance_report_path=performance_path,
        generation_protocol_path=protocol_path,
        generation_protocol_report_path=protocol_report_path,
    )
    assert missing_protocol_snippet["pass_fail"] == "fail"
    assert "generation-2 protocol report missing required snippet" in " ".join(
        missing_protocol_snippet["issues"]
    )
    protocol_report_path.write_text(original_protocol_report, encoding="utf-8")

    original_generation3_report = generation3_report_path.read_text(encoding="utf-8")
    generation3_report_path.write_text(
        original_generation3_report.replace("generation-3 holdout", "generation-three holdout"),
        encoding="utf-8",
    )
    missing_generation3_report_snippet = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
        performance_report_path=performance_path,
        generation3_report_path=generation3_report_path,
    )
    assert missing_generation3_report_snippet["pass_fail"] == "fail"
    assert "generation-3 diagnosis report missing required snippet" in " ".join(
        missing_generation3_report_snippet["issues"]
    )
    generation3_report_path.write_text(original_generation3_report, encoding="utf-8")

    original_generation3_protocol_report = generation3_protocol_report_path.read_text(encoding="utf-8")
    generation3_protocol_report_path.write_text(
        original_generation3_protocol_report.replace("7000..7049", "7000..7048"),
        encoding="utf-8",
    )
    missing_generation3_protocol_snippet = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
        performance_report_path=performance_path,
        generation3_protocol_path=generation3_protocol_path,
        generation3_protocol_report_path=generation3_protocol_report_path,
    )
    assert missing_generation3_protocol_snippet["pass_fail"] == "fail"
    assert "generation-3 protocol report missing required snippet" in " ".join(
        missing_generation3_protocol_snippet["issues"]
    )
    generation3_protocol_report_path.write_text(original_generation3_protocol_report, encoding="utf-8")

    original_generation4_protocol_report = generation4_protocol_report_path.read_text(encoding="utf-8")
    generation4_protocol_report_path.write_text(
        original_generation4_protocol_report.replace("10000..10049", "10000..10048"),
        encoding="utf-8",
    )
    missing_generation4_protocol_snippet = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
        performance_report_path=performance_path,
        generation4_protocol_path=generation4_protocol_path,
        generation4_protocol_report_path=generation4_protocol_report_path,
    )
    assert missing_generation4_protocol_snippet["pass_fail"] == "fail"
    assert "generation-4 protocol report missing required snippet" in " ".join(
        missing_generation4_protocol_snippet["issues"]
    )
    generation4_protocol_report_path.write_text(original_generation4_protocol_report, encoding="utf-8")

    requirements_path = report_path.with_name("requirements_audit.md")
    original_requirements_audit = requirements_path.read_text(encoding="utf-8")
    requirements_path.write_text(
        original_requirements_audit.replace("Working repository", ""),
        encoding="utf-8",
    )
    missing_requirements_snippet = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
    )
    assert missing_requirements_snippet["pass_fail"] == "fail"
    assert "requirements audit missing required snippet" in " ".join(
        missing_requirements_snippet["issues"]
    )

    requirements_path.write_text(
        original_requirements_audit.replace("| Opponent protocol |", "| Opponent protocol removed |"),
        encoding="utf-8",
    )
    missing_opponent_protocol_row = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
    )
    assert missing_opponent_protocol_row["pass_fail"] == "fail"
    assert "requirements audit missing coverage row: Opponent protocol" in " ".join(
        missing_opponent_protocol_row["issues"]
    )

    requirements_path.write_text(
        original_requirements_audit.replace(
            "documented pretrained neural/RNN comparator. No local PPO/DQN/self-play training baseline was run. | Satisfied |",
            "documented pretrained neural/RNN comparator. No local PPO/DQN/self-play training baseline was run. | Partial |",
        ),
        encoding="utf-8",
    )
    overclaimed_neural_baseline = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
    )
    assert overclaimed_neural_baseline["pass_fail"] == "fail"
    joined_overclaim_issues = " ".join(overclaimed_neural_baseline["issues"])
    assert "documented pretrained neural/RNN comparator. No local PPO/DQN/self-play training baseline was run. | Satisfied |" in joined_overclaim_issues
    assert "Packaged RNN comparator" in joined_overclaim_issues
    assert "expected 'Satisfied'" in joined_overclaim_issues
    requirements_path.write_text(original_requirements_audit, encoding="utf-8")

    original_report = report_path.read_text(encoding="utf-8")
    report_path.write_text(
        original_report.replace("## Environment Diagnostics", "## Environment Diagnostics Removed"),
        encoding="utf-8",
    )
    missing_environment_diagnostics = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
    )
    assert missing_environment_diagnostics["pass_fail"] == "fail"
    assert "report missing section: ## Environment Diagnostics" in " ".join(
        missing_environment_diagnostics["issues"]
    )

    report_path.write_text(
        original_report.replace("make slimevolley-final-eval", ""),
        encoding="utf-8",
    )
    missing_reproduction_command = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
    )
    assert missing_reproduction_command["pass_fail"] == "fail"
    assert "report missing required reproduction snippet" in " ".join(
        missing_reproduction_command["issues"]
    )
    report_path.write_text(
        original_report.replace("results/search_best_dev.json", ""),
        encoding="utf-8",
    )
    missing_manifest_artifact = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
    )
    assert missing_manifest_artifact["pass_fail"] == "fail"
    assert "results/search_best_dev.json" in " ".join(missing_manifest_artifact["issues"])
    report_path.write_text(
        original_report.replace(
            "| baseline-rnn | slimevolleygym-baseline-rnn-wrapper | pretrained neural/RNN comparator |",
            "| baseline-rnn | omitted | omitted |",
        ),
        encoding="utf-8",
    )
    missing_opponent_protocol = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
    )
    assert missing_opponent_protocol["pass_fail"] == "fail"
    assert "baseline-rnn" in " ".join(missing_opponent_protocol["issues"])
    report_path.write_text(original_report, encoding="utf-8")

    original_summary = summary_path.read_text(encoding="utf-8")
    assert "tests_pass_fail" in original_summary.splitlines()[0]
    assert "not_recorded" in original_summary
    summary_path.write_text(
        original_summary.replace("initial", "corrupted-policy", 1),
        encoding="utf-8",
    )
    corrupted_summary = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
    )
    assert corrupted_summary["pass_fail"] == "fail"
    assert "summary row 1 column" in " ".join(corrupted_summary["issues"])
    summary_path.write_text(original_summary, encoding="utf-8")

    ledger_entry = json.loads(ledger_path.read_text(encoding="utf-8"))
    future_missing_tests_status = dict(ledger_entry)
    future_missing_tests_status["timestamp"] = "2026-05-25T00:00:00+00:00"
    future_missing_tests_status.pop("tests_pass_fail", None)
    ledger_path.write_text(json.dumps(future_missing_tests_status) + "\n", encoding="utf-8")
    write_summary_csv(ledger_path, summary_path)
    missing_future_test_status = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
    )
    assert missing_future_test_status["pass_fail"] == "fail"
    assert "missing tests_pass_fail for row at or after 2026-05-25T00:00:00+00:00" in " ".join(
        missing_future_test_status["issues"]
    )

    legacy_missing_tests_status = dict(ledger_entry)
    legacy_missing_tests_status["timestamp"] = "2026-05-24T23:59:59+00:00"
    legacy_missing_tests_status.pop("tests_pass_fail", None)
    ledger_path.write_text(json.dumps(legacy_missing_tests_status) + "\n", encoding="utf-8")
    write_summary_csv(ledger_path, summary_path)
    uncovered_legacy_missing_status = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
    )
    assert uncovered_legacy_missing_status["pass_fail"] == "fail"
    assert "not fully covered by append-only amendments" in " ".join(
        uncovered_legacy_missing_status["issues"]
    )

    amendments_path = tmp_path / "legacy_trial_amendments.jsonl"
    append_missing_legacy_tests_pass_fail_amendments(
        ledger_path=ledger_path,
        amendments_path=amendments_path,
        timestamp="2026-05-26T00:00:00+00:00",
    )
    amended_entries, amendment_issues, amendment_counts = apply_ledger_amendments(
        [legacy_missing_tests_status],
        read_ledger_amendments(amendments_path),
        target_ledger=ledger_path.name,
    )
    assert amendment_issues == []
    assert amendment_counts["tests_pass_fail_amended"] == 1
    assert amended_entries[0]["tests_pass_fail"] == "not_recorded"
    assert read_ledger_amendments(amendments_path)[0]["ledger_entry_sha256"] == canonical_entry_hash(
        legacy_missing_tests_status
    )
    write_summary_csv(ledger_path, summary_path, entries=amended_entries)
    accepted_legacy_missing_status = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
        ledger_amendments_path=amendments_path,
    )
    assert accepted_legacy_missing_status["pass_fail"] == "pass"
    assert accepted_legacy_missing_status["tests_pass_fail_counts"] == {"not_recorded": 1}
    assert accepted_legacy_missing_status["raw_tests_pass_fail_counts"] == {"legacy_missing": 1}
    assert accepted_legacy_missing_status["ledger_amendment_counts"]["tests_pass_fail_amended"] == 1

    ledger_entry["change_type"] = NEURAL_BASELINE_CHANGE_TYPE
    ledger_path.write_text(json.dumps(ledger_entry) + "\n", encoding="utf-8")
    write_summary_csv(ledger_path, summary_path)
    warned = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
    )
    assert warned["pass_fail"] == "pass"
    assert warned["noncanonical_change_types"] == [NEURAL_BASELINE_CHANGE_TYPE]
    assert "noncanonical change_type" in " ".join(warned["warnings"])

    unknown_change_type_entry = dict(ledger_entry)
    unknown_change_type_entry["change_type"] = "legacy typo"
    ledger_path.write_text(json.dumps(unknown_change_type_entry) + "\n", encoding="utf-8")
    write_summary_csv(ledger_path, summary_path)
    invalid_change_type = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
    )
    assert invalid_change_type["pass_fail"] == "fail"
    assert "not a recognized SlimeVolley change type" in " ".join(
        invalid_change_type["issues"]
    )

    dev_entry = dict(ledger_entry)
    dev_entry["seed_range"] = {
        "split": "dev",
        "start": 0,
        "stop_exclusive": 2,
        "seeds": [0, 1],
    }
    dev_entry["pass_fail"] = "pass"
    ledger_path.write_text(json.dumps(dev_entry) + "\n", encoding="utf-8")
    write_summary_csv(ledger_path, summary_path)
    unavailable_with_dev_evidence = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
    )
    assert unavailable_with_dev_evidence["pass_fail"] == "fail"
    assert "unavailable but successful dev/holdout SlimeVolley evidence exists" in " ".join(
        unavailable_with_dev_evidence["issues"]
    )

    ledger_path.write_text(json.dumps(ledger_entry) + "\n", encoding="utf-8")
    write_summary_csv(ledger_path, summary_path)

    failed = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        require_holdout=True,
    )
    assert failed["pass_fail"] == "fail"
    assert "holdout rows are required but absent" in failed["issues"]

    missing_diagnostics = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=tmp_path / "missing_diagnostics.json",
        holdout_path=tmp_path / "missing_holdout.json",
    )
    assert missing_diagnostics["pass_fail"] == "fail"
    assert "missing environment diagnostics" in " ".join(missing_diagnostics["issues"])

    malformed_diagnostics = tmp_path / "malformed_diagnostics.json"
    malformed_diagnostics.write_text(
        '{"status":"maybe","packages":{}}',
        encoding="utf-8",
    )
    malformed = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=malformed_diagnostics,
        holdout_path=tmp_path / "missing_holdout.json",
    )
    assert malformed["pass_fail"] == "fail"
    joined_issues = " ".join(malformed["issues"])
    assert "environment diagnostics missing field" in joined_issues
    assert "runtime_metadata is missing or not an object" in joined_issues
    assert "is not available/unavailable" in joined_issues

    mismatched_diagnostics = tmp_path / "mismatched_diagnostics.json"
    mismatched_payload = json.loads(diagnostics_path.read_text(encoding="utf-8"))
    mismatched_payload["packages"] = {"slimevolleygym": "0.1.0"}
    mismatched_payload["runtime_metadata"] = {
        "python": "test-python",
        "platform": "test-platform",
        "packages": {"slimevolleygym": "9.9.9"},
    }
    mismatched_diagnostics.write_text(json.dumps(mismatched_payload), encoding="utf-8")
    mismatched = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=mismatched_diagnostics,
        holdout_path=tmp_path / "missing_holdout.json",
    )
    assert mismatched["pass_fail"] == "fail"
    assert "environment diagnostics package mismatch" in " ".join(mismatched["issues"])

    missing_runtime_package_path = tmp_path / "missing_runtime_package_diagnostics.json"
    mismatched_payload["runtime_metadata"]["packages"] = {}
    missing_runtime_package_path.write_text(json.dumps(mismatched_payload), encoding="utf-8")
    missing_runtime_package = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=missing_runtime_package_path,
        holdout_path=tmp_path / "missing_holdout.json",
    )
    assert missing_runtime_package["pass_fail"] == "fail"
    assert "runtime_metadata.packages is missing or empty" in " ".join(
        missing_runtime_package["issues"]
    )

    reserved_tuning_entry = dict(ledger_entry)
    reserved_tuning_entry["change_type"] = "scalar/config tuning"
    reserved_tuning_entry["seed_range"] = {
        "split": "holdout",
        "start": 1000,
        "stop_exclusive": 1050,
        "seeds": list(range(1000, 1050)),
    }
    reserved_tuning_entry["episodes"] = 50
    reserved_tuning_entry["pass_fail"] = "fail"
    ledger_path.write_text(json.dumps(reserved_tuning_entry) + "\n", encoding="utf-8")
    write_summary_csv(ledger_path, summary_path)
    reserved_tuning = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
    )
    assert reserved_tuning["pass_fail"] == "fail"
    assert "uses reserved 'holdout' split" in " ".join(reserved_tuning["issues"])

    malformed_holdout_entry = dict(reserved_tuning_entry)
    malformed_holdout_entry["change_type"] = "evaluation-harness change"
    malformed_holdout_entry["seed_range"] = {
        "split": "holdout",
        "start": 1000,
        "stop_exclusive": 1001,
        "seeds": [1000],
    }
    malformed_holdout_entry["episodes"] = 1
    ledger_path.write_text(json.dumps(malformed_holdout_entry) + "\n", encoding="utf-8")
    write_summary_csv(ledger_path, summary_path)
    malformed_holdout = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
    )
    assert malformed_holdout["pass_fail"] == "fail"
    assert "holdout seeds do not match predeclared" in " ".join(malformed_holdout["issues"])


def test_slimevolley_audit_cross_checks_holdout_artifact_cells(tmp_path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    report_path = tmp_path / "final_report.md"
    diagnostics_path = tmp_path / "environment_diagnostics.json"
    holdout_path = tmp_path / "holdout_final.json"
    diagnostics_path.write_text(
        json.dumps(
            {
                "status": "available",
                "message": "available",
                "environment_id": "SlimeVolley-v0",
                "packages": {"slimevolleygym": "0.1.0"},
                "runtime_metadata": {
                    "python": "test-python",
                    "platform": "test-platform",
                    "packages": {"slimevolleygym": "0.1.0"},
                },
                "expected_observation_space": "Box(12)",
                "expected_action_space": "MultiBinary(3)",
                "expected_step_api": "legacy",
                "reward_semantics": "point reward",
                "seed_api_behavior": "env.seed(seed) before reset",
                "same_seed_reset_observation_equal": True,
                "observed_step_api": "legacy-4-tuple",
                "multiagent_step_api_observed": "legacy-4-tuple",
                "has_seed_method": True,
                "max_episode_steps": 3000,
            }
        ),
        encoding="utf-8",
    )
    run_slimevolley_holdout(
        policies=("initial",),
        opponents=("builtin",),
        ledger_path=ledger_path,
        summary_path=summary_path,
        output_path=holdout_path,
        tests_run=TESTS_RUN_FIXTURE,
        env_factory=FakeSlimeVolleyEnv,
    )
    render_slimevolley_report(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=holdout_path,
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
    )
    write_requirements_audit_fixture(report_path.with_name("requirements_audit.md"))

    valid = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=holdout_path,
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
    )
    assert valid["pass_fail"] == "pass"

    payload = json.loads(holdout_path.read_text(encoding="utf-8"))
    payload["cells"][0]["mean"] = 999.0
    holdout_path.write_text(json.dumps(payload), encoding="utf-8")
    corrupted = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=holdout_path,
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
    )
    assert corrupted["pass_fail"] == "fail"
    assert "holdout artifact cell initial vs builtin field 'mean' does not match ledger" in " ".join(
        corrupted["issues"]
    )


def test_slimevolley_audit_cross_checks_search_best_artifact_entries(tmp_path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    report_path = tmp_path / "final_report.md"
    diagnostics_path = tmp_path / "environment_diagnostics.json"
    search_path = tmp_path / "search_best_dev.json"
    diagnostics_path.write_text(
        json.dumps(
            {
                "status": "available",
                "message": "available",
                "environment_id": "SlimeVolley-v0",
                "packages": {"slimevolleygym": "0.1.0"},
                "runtime_metadata": {
                    "python": "test-python",
                    "platform": "test-platform",
                    "packages": {"slimevolleygym": "0.1.0"},
                },
                "expected_observation_space": "Box(12)",
                "expected_action_space": "MultiBinary(3)",
                "expected_step_api": "legacy",
                "reward_semantics": "point reward",
                "seed_api_behavior": "env.seed(seed) before reset",
                "same_seed_reset_observation_equal": True,
                "observed_step_api": "legacy-4-tuple",
                "multiagent_step_api_observed": "legacy-4-tuple",
                "has_seed_method": True,
                "max_episode_steps": 3000,
            }
        ),
        encoding="utf-8",
    )
    search_slimevolley_configs(
        opponents=("builtin",),
        max_candidates=1,
        episodes=2,
        ledger_path=ledger_path,
        summary_path=summary_path,
        output_path=search_path,
        tests_run=TESTS_RUN_FIXTURE,
        env_factory=FakeSlimeVolleyEnv,
    )
    render_slimevolley_report(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=search_path,
        tournament_path=tmp_path / "missing_tournament.json",
    )
    write_requirements_audit_fixture(report_path.with_name("requirements_audit.md"))

    valid = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=search_path,
        tournament_path=tmp_path / "missing_tournament.json",
    )
    assert valid["pass_fail"] == "pass"

    payload = json.loads(search_path.read_text(encoding="utf-8"))
    bad_config = dict(payload)
    bad_config["config"] = dict(payload["config"], home_x=9.99)
    search_path.write_text(json.dumps(bad_config), encoding="utf-8")
    mismatched_config = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=search_path,
        tournament_path=tmp_path / "missing_tournament.json",
    )
    assert mismatched_config["pass_fail"] == "fail"
    assert "scalar-search artifact config does not match candidate_index" in " ".join(
        mismatched_config["issues"]
    )

    payload["opponent_means"]["builtin"] = 999.0
    search_path.write_text(json.dumps(payload), encoding="utf-8")
    corrupted = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=search_path,
        tournament_path=tmp_path / "missing_tournament.json",
    )
    assert corrupted["pass_fail"] == "fail"
    assert "scalar-search artifact opponent mean for builtin does not match ledger" in " ".join(
        corrupted["issues"]
    )


def test_slimevolley_audit_cross_checks_tournament_artifact_cells(tmp_path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    report_path = tmp_path / "final_report.md"
    diagnostics_path = tmp_path / "environment_diagnostics.json"
    tournament_path = tmp_path / "round_robin_dev.json"
    diagnostics_path.write_text(
        json.dumps(
            {
                "status": "available",
                "message": "available",
                "environment_id": "SlimeVolley-v0",
                "packages": {"slimevolleygym": "0.1.0"},
                "runtime_metadata": {
                    "python": "test-python",
                    "platform": "test-platform",
                    "packages": {"slimevolleygym": "0.1.0"},
                },
                "expected_observation_space": "Box(12)",
                "expected_action_space": "MultiBinary(3)",
                "expected_step_api": "legacy",
                "reward_semantics": "point reward",
                "seed_api_behavior": "env.seed(seed) before reset",
                "same_seed_reset_observation_equal": True,
                "observed_step_api": "legacy-4-tuple",
                "multiagent_step_api_observed": "legacy-4-tuple",
                "has_seed_method": True,
                "max_episode_steps": 3000,
            }
        ),
        encoding="utf-8",
    )
    run_slimevolley_tournament(
        split="dev",
        participants=("initial",),
        episodes=2,
        ledger_path=ledger_path,
        summary_path=summary_path,
        output_path=tournament_path,
        tests_run=TESTS_RUN_FIXTURE,
        env_factory=FakeSlimeVolleyEnv,
    )
    render_slimevolley_report(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tournament_path,
    )
    write_requirements_audit_fixture(report_path.with_name("requirements_audit.md"))

    valid = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tournament_path,
    )
    assert valid["pass_fail"] == "pass"

    payload = json.loads(tournament_path.read_text(encoding="utf-8"))
    payload["cells"][0]["mean"] = 999.0
    tournament_path.write_text(json.dumps(payload), encoding="utf-8")
    corrupted = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tournament_path,
    )
    assert corrupted["pass_fail"] == "fail"
    assert "tournament artifact cell initial vs initial field 'mean' does not match ledger" in " ".join(
        corrupted["issues"]
    )


def test_slimevolley_audit_validates_search_and_tournament_artifacts(tmp_path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    report_path = tmp_path / "final_report.md"
    diagnostics_path = tmp_path / "environment_diagnostics.json"
    search_path = tmp_path / "search_best_dev.json"
    tournament_path = tmp_path / "round_robin_dev.json"
    diagnostics_path.write_text(
        '{"status":"unavailable","message":"missing deps","packages":{"slimevolleygym":"not_installed"},"expected_observation_space":"Box(12)","expected_action_space":"MultiBinary(3)","expected_step_api":"legacy","reward_semantics":"point reward","seed_api_behavior":"not probed; unavailable","same_seed_reset_observation_equal":false,"observed_step_api":"unavailable","multiagent_step_api_observed":"unavailable","runtime_metadata":{"python":"test-python","platform":"test-platform","packages":{"slimevolleygym":"not_installed"}}}',
        encoding="utf-8",
    )
    evaluate_slimevolley(
        policy_name="initial",
        opponent_name="builtin",
        split="smoke",
        ledger_path=ledger_path,
        summary_path=summary_path,
        env_factory=FakeSlimeVolleyEnv,
        tests_run=TESTS_RUN_FIXTURE,
    )
    render_slimevolley_report(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        search_best_path=search_path,
        tournament_path=tournament_path,
        holdout_path=tmp_path / "missing_holdout.json",
    )
    write_requirements_audit_fixture(report_path.with_name("requirements_audit.md"))

    search_payload = {
        "candidate_count": 1,
        "candidate_index": 1,
        "config": {"home_x": 1.05, "contact_x_window": 0.18, "landing_horizon": 0.3},
        "environment": "SlimeVolley-v0",
        "opponent_means": {"builtin": -5.0},
        "opponents": ["builtin"],
        "selection_score": -5.0,
        "split": "dev",
    }
    tournament_payload = {
        "cells": [
            {
                "draws": 0,
                "episodes": 2,
                "losses": 1,
                "opponent": "initial",
                "policy": "initial",
                "split": "dev",
                "wins": 1,
            }
        ],
        "environment": "SlimeVolley-v0",
        "matchup_count": 1,
        "participants": ["initial"],
        "pass_fail": "pass",
        "split": "dev",
        "standings": [{"policy": "initial"}],
    }
    search_path.write_text(json.dumps(search_payload), encoding="utf-8")
    tournament_path.write_text(json.dumps(tournament_payload), encoding="utf-8")

    result = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=search_path,
        tournament_path=tournament_path,
    )

    assert result["pass_fail"] == "pass"
    assert result["search_best_artifact"] == str(search_path)
    assert result["tournament_artifact"] == str(tournament_path)
    assert "missing scalar-search artifact" not in " ".join(result["warnings"])
    assert "missing tournament artifact" not in " ".join(result["warnings"])

    bad_search = dict(search_payload, split="holdout")
    search_path.write_text(json.dumps(bad_search), encoding="utf-8")
    bad_search_result = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=search_path,
        tournament_path=tournament_path,
    )
    assert bad_search_result["pass_fail"] == "fail"
    assert "scalar-search artifact uses reserved 'holdout' split" in " ".join(
        bad_search_result["issues"]
    )

    bad_search_opponent = dict(search_payload, opponents=["ghost"], opponent_means={"ghost": 0.0})
    search_path.write_text(json.dumps(bad_search_opponent), encoding="utf-8")
    bad_search_opponent_result = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=search_path,
        tournament_path=tournament_path,
    )
    assert bad_search_opponent_result["pass_fail"] == "fail"
    assert "scalar-search artifact references unknown opponents" in " ".join(
        bad_search_opponent_result["issues"]
    )

    search_path.write_text(json.dumps(search_payload), encoding="utf-8")
    bad_tournament = dict(
        tournament_payload,
        participants=["initial", "ghost"],
        matchup_count=1,
    )
    tournament_path.write_text(json.dumps(bad_tournament), encoding="utf-8")
    bad_tournament_result = audit_slimevolley_artifacts(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=search_path,
        tournament_path=tournament_path,
    )
    assert bad_tournament_result["pass_fail"] == "fail"
    assert "tournament artifact cells do not cover the full participant matrix" in " ".join(
        bad_tournament_result["issues"]
    )


def test_slimevolley_audit_cli_writes_json_output(tmp_path, monkeypatch) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    report_path = tmp_path / "final_report.md"
    diagnostics_path = tmp_path / "environment_diagnostics.json"
    output_path = tmp_path / "audit_latest.json"
    performance_path = tmp_path / "performance_deepdive.md"
    generation_report_path = tmp_path / "generation_2_diagnosis.md"
    protocol_path = tmp_path / "generation_2_protocol.json"
    protocol_report_path = tmp_path / "generation_2_protocol.md"
    generation3_report_path = tmp_path / "generation_3_diagnosis.md"
    generation3_ledger_path = tmp_path / "generation_3_trials.jsonl"
    generation3_summary_path = tmp_path / "generation_3_summary.csv"
    generation3_protocol_path = tmp_path / "generation_3_protocol.json"
    generation3_protocol_report_path = tmp_path / "generation_3_protocol.md"
    generation4_protocol_path = tmp_path / "generation_4_protocol.json"
    generation4_protocol_report_path = tmp_path / "generation_4_protocol.md"
    contact_diagnostics_json_path = tmp_path / "contact_diagnostics_g3_dev.json"
    contact_diagnostics_report_path = tmp_path / "contact_diagnostics_g3_dev.md"
    diagnostics_path.write_text(
        '{"status":"unavailable","message":"missing deps","packages":{"slimevolleygym":"not_installed"},"expected_observation_space":"Box(12)","expected_action_space":"MultiBinary(3)","expected_step_api":"legacy","reward_semantics":"point reward","seed_api_behavior":"not probed; unavailable","same_seed_reset_observation_equal":false,"observed_step_api":"unavailable","multiagent_step_api_observed":"unavailable","runtime_metadata":{"python":"test-python","platform":"test-platform","packages":{"slimevolleygym":"not_installed"}}}',
        encoding="utf-8",
    )
    evaluate_slimevolley(
        policy_name="initial",
        opponent_name="builtin",
        split="smoke",
        ledger_path=ledger_path,
        summary_path=summary_path,
        env_factory=FakeSlimeVolleyEnv,
        tests_run=TESTS_RUN_FIXTURE,
    )
    render_slimevolley_report(
        ledger_path=ledger_path,
        summary_path=summary_path,
        report_path=report_path,
        diagnostics_path=diagnostics_path,
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
        holdout_path=tmp_path / "missing_holdout.json",
    )
    write_requirements_audit_fixture(report_path.with_name("requirements_audit.md"))
    write_slimevolley_performance_report(
        output_path=performance_path,
        ledger_path=ledger_path,
        holdout_path=tmp_path / "missing_holdout.json",
        search_best_path=tmp_path / "missing_search.json",
        tournament_path=tmp_path / "missing_tournament.json",
    )
    write_generation_2_diagnosis_report(
        output_path=generation_report_path,
        ledger_path=tmp_path / "generation_2_trials.jsonl",
        summary_path=tmp_path / "generation_2_summary.csv",
        holdout_path=tmp_path / "holdout_g2_final.json",
    )
    write_generation_2_protocol(
        json_path=protocol_path,
        markdown_path=protocol_report_path,
    )
    evaluate_slimevolley(
        policy_name="improved",
        opponent_name="builtin",
        split="dev",
        seed_start=6000,
        episodes=50,
        ledger_path=generation3_ledger_path,
        summary_path=generation3_summary_path,
        env_factory=FakeSlimeVolleyEnv,
        tests_run=TESTS_RUN_FIXTURE,
        tests_pass_fail="pass",
    )
    write_generation_3_diagnosis_report(
        output_path=generation3_report_path,
        ledger_path=generation3_ledger_path,
        summary_path=generation3_summary_path,
        holdout_path=tmp_path / "holdout_g3_final.json",
    )
    write_generation_3_protocol(
        json_path=generation3_protocol_path,
        markdown_path=generation3_protocol_report_path,
    )
    write_generation_4_protocol(
        json_path=generation4_protocol_path,
        markdown_path=generation4_protocol_report_path,
    )
    contact_diagnostics_json_path.write_text(json.dumps({"status": "pass"}) + "\n", encoding="utf-8")
    contact_diagnostics_report_path.write_text("# SlimeVolley Generation-3 Contact/Return Diagnostics\n", encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        [
            "slimevolley-audit",
            "--ledger",
            str(ledger_path),
            "--summary",
            str(summary_path),
            "--report",
            str(report_path),
            "--diagnostics",
            str(diagnostics_path),
            "--holdout",
            str(tmp_path / "missing_holdout.json"),
            "--search-best",
            str(tmp_path / "missing_search.json"),
            "--tournament",
            str(tmp_path / "missing_tournament.json"),
            "--performance-report",
            str(performance_path),
            "--generation-report",
            str(generation_report_path),
            "--generation-protocol",
            str(protocol_path),
            "--generation-protocol-report",
            str(protocol_report_path),
            "--generation3-report",
            str(generation3_report_path),
            "--generation3-protocol",
            str(generation3_protocol_path),
            "--generation3-protocol-report",
            str(generation3_protocol_report_path),
            "--generation4-protocol",
            str(generation4_protocol_path),
            "--generation4-protocol-report",
            str(generation4_protocol_report_path),
            "--contact-diagnostics-json",
            str(contact_diagnostics_json_path),
            "--contact-diagnostics-report",
            str(contact_diagnostics_report_path),
            "--output",
            str(output_path),
        ],
    )
    slimevolley_audit_main()
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["pass_fail"] == "pass"
    assert payload["summary_content_checked"] is True
    assert payload["diagnostics_status"] == "unavailable"
    assert payload["artifact_hashes"]["ledger"] != "missing"
    assert payload["artifact_hashes"]["holdout"] == "missing"
    assert payload["artifact_hashes"]["performance_report"] != "missing"
    assert payload["artifact_hashes"]["generation_report"] != "missing"
    assert payload["artifact_hashes"]["generation_protocol"] != "missing"
    assert payload["artifact_hashes"]["generation_protocol_report"] != "missing"
    assert payload["artifact_hashes"]["generation3_report"] != "missing"
    assert payload["artifact_hashes"]["generation3_protocol"] != "missing"
    assert payload["artifact_hashes"]["generation3_protocol_report"] != "missing"
    assert payload["artifact_hashes"]["generation4_protocol"] != "missing"
    assert payload["artifact_hashes"]["generation4_protocol_report"] != "missing"
    assert payload["generation4_protocol_status"] == "predeclared-not-run"
    assert payload["generation4_seed_ranges"]["holdout"] == "10000..10049"
    assert payload["requirements_audit_row_count"] == 25
    assert payload["requirements_audit_status_counts"] == {"Satisfied": 25}
    assert payload["requirements_audit_partial_rows"] == []
    assert payload["requirements_audit_completion_state"] == "satisfied"
    assert payload["requirements_audit_completion_recommendation"] == "eligible_for_completion_audit"
    assert payload["requirements_audit_completion_blockers"] == []
    assert payload["requirements_audit_partial_row_classifications"] == {}
    assert payload["requirements_audit_partial_row_details"] == []
    assert payload["artifact_hashes"]["contact_diagnostics_json"] != "missing"
    assert payload["artifact_hashes"]["contact_diagnostics_report"] != "missing"
    assert payload["source_hashes"]["hl_benchmark/artifacts.py"] != "missing"
    assert payload["source_hashes"]["hl_benchmark/policies/base.py"] != "missing"
    assert payload["source_hashes"]["hl_benchmark/slimevolley/audit.py"] != "missing"


def test_slimevolley_holdout_runner_records_artifact_and_refuses_repeat(tmp_path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    output_path = tmp_path / "holdout_final.json"
    payload = run_slimevolley_holdout(
        policies=("initial",),
        opponents=("builtin",),
        episodes=1,
        ledger_path=ledger_path,
        summary_path=summary_path,
        output_path=output_path,
        env_factory=FakeSlimeVolleyEnv,
    )
    entries = read_entries(ledger_path)
    assert payload["pass_fail"] == "pass"
    assert payload["split"] == "holdout"
    assert payload["matchup_count"] == 1
    assert payload["anti_tuning_note"]
    assert output_path.exists()
    assert len(entries) == 1
    assert entries[0]["seed_range"]["split"] == "holdout"
    assert entries[0]["seed_range"]["seeds"] == [1000]
    assert "must not be used for tuning" in entries[0]["change_summary"]
    with pytest.raises(ValueError, match="holdout ledger already contains"):
        run_slimevolley_holdout(
            policies=("initial",),
            opponents=("builtin",),
            episodes=1,
            ledger_path=ledger_path,
            summary_path=summary_path,
            output_path=output_path,
            env_factory=FakeSlimeVolleyEnv,
        )


def test_slimevolley_holdout_runner_accepts_rally_serve_policy(tmp_path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    output_path = tmp_path / "holdout_final.json"
    payload = run_slimevolley_holdout(
        policies=("rally-serve",),
        opponents=("builtin",),
        episodes=1,
        ledger_path=ledger_path,
        summary_path=summary_path,
        output_path=output_path,
        env_factory=FakeSlimeVolleyEnv,
    )
    entries = read_entries(ledger_path)
    assert payload["pass_fail"] == "pass"
    assert payload["policies"] == ["rally-serve"]
    assert entries[0]["policy_version"] == "rally-serve"
    assert entries[0]["seed_range"]["split"] == "holdout"


def test_slimevolley_tournament_records_round_robin_artifact(tmp_path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    output_path = tmp_path / "round_robin_smoke.json"
    payload = run_slimevolley_tournament(
        split="smoke",
        participants=("initial", "improved-v0"),
        ledger_path=ledger_path,
        summary_path=summary_path,
        output_path=output_path,
        env_factory=FakeSlimeVolleyEnv,
    )
    entries = read_entries(ledger_path)
    assert payload["pass_fail"] == "pass"
    assert payload["matchup_count"] == 4
    assert [row["policy"] for row in payload["standings"]] == ["initial", "improved-v0"]
    assert output_path.exists()
    assert len(entries) == 4
    assert {entry["change_type"] for entry in entries} == {"evaluation-harness change"}
    assert {entry["opponent_name"] for entry in entries} == {"initial", "improved-v0"}
    assert "round-robin" in entries[0]["change_summary"]


def test_slimevolley_scalar_search_rejects_holdout(tmp_path) -> None:
    with pytest.raises(ValueError, match="holdout"):
        search_slimevolley_configs(
            split="holdout",
            max_candidates=1,
            ledger_path=tmp_path / "trials.jsonl",
            summary_path=tmp_path / "summary.csv",
            output_path=tmp_path / "best.json",
            env_factory=FakeSlimeVolleyEnv,
        )


def test_slimevolley_scalar_search_records_opponent_rows_and_best_config(tmp_path) -> None:
    ledger_path = tmp_path / "trials.jsonl"
    summary_path = tmp_path / "summary.csv"
    output_path = tmp_path / "best.json"
    best = search_slimevolley_configs(
        split="smoke",
        opponents=("builtin", "random"),
        max_candidates=2,
        ledger_path=ledger_path,
        summary_path=summary_path,
        output_path=output_path,
        env_factory=FakeSlimeVolleyEnv,
    )
    entries = read_entries(ledger_path)
    assert best is not None
    assert best["candidate_count"] == 2
    assert output_path.exists()
    assert len(entries) == 4
    assert {entry["opponent_name"] for entry in entries} == {"builtin", "random"}
    assert {entry["change_type"] for entry in entries} == {"scalar/config tuning"}
    assert "selection_score" in output_path.read_text(encoding="utf-8")


def test_slimevolley_archives_stay_frozen() -> None:
    low_ball_state = np.asarray([1.08, 0.0, 0.0, 0.0, 0.72, 0.32, 1.40, -1.70, -1.2, 0.0, 0.0, 0.0])
    late_low_ball_state = np.asarray([
        1.6083333333333336,
        0.4089999999999998,
        -1.75,
        -0.6100000000000005,
        1.394555527532018,
        0.20936784794911595,
        -1.6793619058381766,
        -1.4974122976720763,
        0.2,
        0.4707333333333331,
        0.0,
        -0.21800000000000042,
    ])
    current = make_policy("SlimeVolley-v0", "improved")
    grounded_receive_state = np.asarray([
        1.8416666666666663,
        0.4707333333333331,
        -1.75,
        -0.21800000000000042,
        1.6279485985910003,
        0.3975218855190726,
        -1.8663318444602972,
        -1.2567042000221953,
        0.2,
        0.4801999999999998,
        0.0,
        0.17399999999999963,
    ])
    rear_wall_recovery_state = np.asarray([
        2.016666666666666,
        0.4089999999999998,
        0.0,
        -0.21800000000000042,
        2.229,
        0.256,
        -0.854,
        -2.082,
        0.2,
        0.23673333333333332,
        0.0,
        1.252,
    ])
    rear_wall_press_state = np.asarray([
        2.016666666666666,
        0.4743999999999998,
        0.0,
        -0.12000000000000041,
        2.349666666666667,
        0.298312956665069,
        -1.0334420895830876,
        -1.998623888448785,
        0.2,
        0.15,
        0.0,
        0.0,
    ])
    archived_v0 = SlimeVolleyImprovedV0Policy()
    archived_v1 = SlimeVolleyImprovedV1Policy()
    archived_v2 = SlimeVolleyImprovedV2Policy()
    archived_v3 = SlimeVolleyImprovedV3Policy()
    archived_v4 = SlimeVolleyImprovedV4Policy()
    archived_v5 = SlimeVolleyImprovedV5Policy()
    archived_v6 = SlimeVolleyImprovedV6Policy()
    current.reset(40)
    archived_v0.reset(40)
    archived_v1.reset(40)
    archived_v2.reset(40)
    archived_v3.reset(40)
    archived_v4.reset(40)
    archived_v5.reset(40)
    assert current.act(low_ball_state).tolist() == [1, 0, 1]
    assert archived_v0.act(low_ball_state).tolist() == [0, 1, 0]
    assert archived_v1.act(low_ball_state).tolist() == [1, 0, 1]
    assert archived_v2.act(low_ball_state).tolist() == [1, 0, 1]

    current.reset(40)
    archived_v1.reset(40)
    archived_v2.reset(40)
    assert current.act(late_low_ball_state).tolist() == [1, 0, 0]
    assert archived_v1.act(late_low_ball_state).tolist() == [1, 0, 1]
    assert archived_v2.act(late_low_ball_state).tolist() == [1, 0, 0]

    current.reset(40)
    archived_v2.reset(40)
    assert current.act(grounded_receive_state).tolist() == [1, 0, 0]
    assert archived_v2.act(grounded_receive_state).tolist() == [1, 0, 1]

    current.reset(6040)
    archived_v3.reset(6040)
    archived_v5.reset(6040)
    archived_v6.reset(6040)
    assert current.act(rear_wall_recovery_state).tolist() == [1, 0, 1]
    assert archived_v3.act(rear_wall_recovery_state).tolist() == [0, 0, 0]
    assert archived_v5.act(rear_wall_recovery_state).tolist() == [0, 1, 0]
    assert archived_v6.act(rear_wall_recovery_state).tolist() == [1, 0, 1]

    current.reset(6037)
    archived_v3.reset(6037)
    archived_v4.reset(6037)
    archived_v5.reset(6037)
    archived_v6.reset(6037)
    assert current.act(rear_wall_press_state).tolist() == [1, 0, 1]
    assert archived_v3.act(rear_wall_press_state).tolist() == [0, 0, 0]
    assert archived_v4.act(rear_wall_press_state).tolist() == [0, 1, 0]
    assert archived_v5.act(rear_wall_press_state).tolist() == [0, 1, 0]
    assert archived_v6.act(rear_wall_press_state).tolist() == [1, 0, 1]

    front_hit_state = np.asarray([0.675, 0.419, 0.0, 0.66, 0.882, 0.586, -0.93, -0.84, -1.2, 0.0, 0.0, 0.0])
    current.reset(464)
    archived_v4.reset(464)
    assert current.act(front_hit_state).tolist() == [1, 0, 0]
    assert archived_v4.act(front_hit_state).tolist() == [1, 0, 1]

    front_net_low_scoop_state = np.asarray([0.267, 0.371, 0.0, 0.86, 0.10, 0.247, 1.77, -1.47, 0.2, 0.218, 0.0, -1.20])
    current.reset(9005)
    archived_v6.reset(9005)
    assert current.act(front_net_low_scoop_state).tolist() == [0, 0, 0]
    assert archived_v6.act(front_net_low_scoop_state).tolist() == [0, 0, 0]

    assert "low_ball_rescue" not in archived_v0.config()["structural_modes"]
    assert "late_low_ball_guard" not in archived_v1.config()["structural_modes"]
    assert "grounded_low_receive" not in archived_v2.config()["structural_modes"]
    assert "falling_floor_intercept" not in archived_v2.config()["structural_modes"]
    assert "rear_wall_recovery" not in archived_v3.config()["structural_modes"]
    assert "rear_wall_press" not in archived_v3.config()["structural_modes"]
    assert "delayed_low_receive" not in archived_v3.config()["structural_modes"]
    assert "front_hit_suppression" not in archived_v4.config()["structural_modes"]
    assert "front_hit_suppression" in archived_v5.config()["structural_modes"]
    assert "rear_wall_low_jump" not in archived_v5.config()["structural_modes"]
    assert "rear_wall_low_jump" in archived_v6.config()["structural_modes"]
    assert "front_hit_suppression" in current.config()["structural_modes"]
    assert "rear_wall_low_jump" in current.config()["structural_modes"]
    assert "front_net_low_scoop" not in current.config()["structural_modes"]
    assert "grounded_low_receive" in current.config()["structural_modes"]
    assert "falling_floor_intercept" in current.config()["structural_modes"]
    assert "rear_wall_press" in current.config()["structural_modes"]
    assert "delayed_low_receive" not in current.config()["structural_modes"]
    assert "rear_wall_recovery" not in current.config()["structural_modes"]


def test_slimevolley_archived_opponents_use_frozen_policies() -> None:
    opponent_v0 = make_slimevolley_opponent("improved-v0")
    opponent_v1 = make_slimevolley_opponent("improved-v1")
    opponent_v2 = make_slimevolley_opponent("improved-v2")
    opponent_v3 = make_slimevolley_opponent("improved-v3")
    opponent_v4 = make_slimevolley_opponent("improved-v4")
    opponent_v5 = make_slimevolley_opponent("improved-v5")
    opponent_v6 = make_slimevolley_opponent("improved-v6")
    assert opponent_v0.config()["policy_config"]["policy_type"] == "slimevolley_improved_v0_archive"
    assert opponent_v1.config()["policy_config"]["policy_type"] == "slimevolley_improved_v1_archive"
    assert opponent_v2.config()["policy_config"]["policy_type"] == "slimevolley_improved_v2_archive"
    assert opponent_v3.config()["policy_config"]["policy_type"] == "slimevolley_improved_v3_archive"
    assert opponent_v4.config()["policy_config"]["policy_type"] == "slimevolley_improved_v4_archive"
    assert opponent_v5.config()["policy_config"]["policy_type"] == "slimevolley_improved_v5_archive"
    assert opponent_v6.config()["policy_config"]["policy_type"] == "slimevolley_improved_v6_archive"


def test_slimevolley_baseline_rnn_policy_when_available() -> None:
    available, _message = check_slimevolley_available()
    if not available:
        return
    policy = make_policy("SlimeVolley-v0", "baseline-rnn")
    obs = np.asarray([1.2, 0.0, 0.0, 0.0, 0.8, 0.8, 0.05, -0.04, -1.2, 0.0, 0.0, 0.0])
    action = policy.act(obs)
    assert action.shape == (3,)
    assert set(action.tolist()) <= {0, 1}
    assert policy.config()["baseline_type"] == "pretrained neural/RNN comparator"

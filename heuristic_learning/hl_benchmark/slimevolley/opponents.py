"""Named SlimeVolley opponent protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hl_benchmark.policies.base import BasePolicy
from hl_benchmark.policies.slimevolley import (
    SlimeVolleyBuiltInRnnPolicy,
    SlimeVolleyHeuristicPolicy,
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
    SlimeVolleyRandomPolicy,
    SlimeVolleyRallyServePolicy,
    SlimeVolleyNetPressurePolicy,
    SlimeVolleyPostContactPolicy,
    SlimeVolleyTeacherAssistedPolicy,
    SlimeVolleyTemporalPolicy,
)


@dataclass(frozen=True)
class OpponentSpec:
    """Auditable opponent identity used by SlimeVolley evaluations."""

    name: str
    version: str
    kind: str
    description: str


OPPONENT_POOL: dict[str, OpponentSpec] = {
    "builtin": OpponentSpec(
        name="builtin",
        version="slimevolleygym-baseline-rnn",
        kind="built-in baseline",
        description="Use the environment's default 120-parameter RNN baseline by omitting otherAction.",
    ),
    "random": OpponentSpec(
        name="random",
        version="v0",
        kind="random policy",
        description="Seeded MultiBinary(3) random opponent.",
    ),
    "initial": OpponentSpec(
        name="initial",
        version="v0",
        kind="frozen heuristic",
        description="Frozen copy of the intentionally modest initial SlimeVolley heuristic.",
    ),
    "improved-v0": OpponentSpec(
        name="improved-v0",
        version="v0",
        kind="archived heuristic",
        description="Frozen first structural heuristic archive before low-ball-rescue was added.",
    ),
    "improved-v1": OpponentSpec(
        name="improved-v1",
        version="v1",
        kind="archived heuristic",
        description="Frozen structural heuristic archive before late-low-ball guard was added.",
    ),
    "improved-v2": OpponentSpec(
        name="improved-v2",
        version="v2",
        kind="archived heuristic",
        description="Frozen structural heuristic archive before grounded-low-receive was added.",
    ),
    "improved-v3": OpponentSpec(
        name="improved-v3",
        version="v3",
        kind="archived heuristic",
        description="Frozen structural heuristic archive before rear-wall recovery was added.",
    ),
    "improved-v4": OpponentSpec(
        name="improved-v4",
        version="v4",
        kind="archived heuristic",
        description="Frozen structural heuristic archive before front-hit jump suppression was added.",
    ),
    "improved-v5": OpponentSpec(
        name="improved-v5",
        version="v5",
        kind="archived heuristic",
        description="Frozen structural heuristic archive before rear-wall low-jump rescue was added.",
    ),
    "improved-v6": OpponentSpec(
        name="improved-v6",
        version="v6",
        kind="archived heuristic",
        description="Frozen structural heuristic archive before front-net low-scoop rescue was added.",
    ),
    "improved": OpponentSpec(
        name="improved",
        version="current",
        kind="current heuristic",
        description="Current structural heuristic; useful for self-play and round-robin diagnostics, not a frozen archive.",
    ),
    "improved-tuned": OpponentSpec(
        name="improved-tuned",
        version="g4-scalar-tuned-v2",
        kind="scalar-tuned structural heuristic",
        description="Generation-4 scalar/config-tuned v2 of the current structural heuristic; not a structural archive.",
    ),
    "attack": OpponentSpec(
        name="attack",
        version="g4-late-contact-attack-candidate",
        kind="structural heuristic candidate",
        description="Generation-4 late-contact attack candidate; partial evidence only and not promoted over improved-tuned v2.",
    ),
    "rally-serve": OpponentSpec(
        name="rally-serve",
        version="g4-rally-serve-candidate",
        kind="structural-plus-scalar heuristic candidate",
        description="Generation-4 rally-serve detector plus scalar-tuned attack candidate; beat baseline-rnn on built-in development seeds but failed to beat it on generation-4 built-in holdout.",
    ),
    "post-contact": OpponentSpec(
        name="post-contact",
        version="g4-post-contact-front-conversion-candidate",
        kind="structural heuristic candidate",
        description="Generation-4 post-contact front-conversion candidate; development-only structural probe, not final evidence.",
    ),
    "net-pressure": OpponentSpec(
        name="net-pressure",
        version="g5-net-pressure-candidate",
        kind="structural heuristic candidate",
        description="Generation-5 front-court pressure candidate; development probe only, not promoted.",
    ),
    "temporal": OpponentSpec(
        name="temporal",
        version="g4-candidate",
        kind="temporal stacked-history heuristic",
        description="Generation-4 candidate heuristic using a short observation/action history for contact and trajectory features.",
    ),
    "planner": OpponentSpec(
        name="planner",
        version="g4-planner-candidate",
        kind="physics-feature heuristic",
        description="Generation-4 pure planner candidate using time-to-floor, net-clearance, wall-bounce, and opponent-commitment features.",
    ),
    "teacher-assisted": OpponentSpec(
        name="teacher-assisted",
        version="g4-teacher-assisted-candidate",
        kind="teacher-assisted transparent heuristic",
        description="Generation-4 planner variant reserved for hand-audited rules suggested by baseline-rnn development traces; no RNN runtime calls.",
    ),
    "baseline-rnn": OpponentSpec(
        name="baseline-rnn",
        version="slimevolleygym-baseline-rnn-wrapper",
        kind="pretrained neural/RNN comparator",
        description="Use slimevolleygym's shipped 120-parameter RNN policy as an explicit comparator opponent.",
    ),
}


class BuiltInBaselineOpponent(BasePolicy):
    """Sentinel opponent that asks SlimeVolleyEnv to use its built-in policy."""

    policy_name = "slimevolley_builtin_baseline"
    uses_env_builtin = True

    def act(self, obs: Any) -> None:
        del obs
        return None

    def config(self) -> dict[str, Any]:
        return {"opponent_type": "built_in_baseline", "uses_env_builtin": True}


class PolicyOpponent(BasePolicy):
    """Wrap a regular policy with opponent metadata."""

    uses_env_builtin = False

    def __init__(self, spec: OpponentSpec, policy: BasePolicy) -> None:
        self.spec = spec
        self.policy = policy
        self.policy_name = f"slimevolley_opponent_{spec.name}"

    def reset(self, seed: int | None = None) -> None:
        self.policy.reset(seed)

    def act(self, obs: Any) -> Any:
        return self.policy.act(obs)

    def config(self) -> dict[str, Any]:
        return {"opponent": self.spec.__dict__, "policy_config": self.policy.config()}


def make_slimevolley_opponent(name: str) -> BasePolicy:
    """Build a named frozen opponent for SlimeVolley evaluation."""

    if name not in OPPONENT_POOL:
        raise ValueError(f"unknown SlimeVolley opponent {name!r}; expected one of {sorted(OPPONENT_POOL)}")
    spec = OPPONENT_POOL[name]
    if name == "builtin":
        return BuiltInBaselineOpponent()
    if name == "random":
        return PolicyOpponent(spec, SlimeVolleyRandomPolicy())
    if name == "initial":
        return PolicyOpponent(spec, SlimeVolleyHeuristicPolicy(structural=False))
    if name == "improved-v0":
        return PolicyOpponent(spec, SlimeVolleyImprovedV0Policy())
    if name == "improved-v1":
        return PolicyOpponent(spec, SlimeVolleyImprovedV1Policy())
    if name == "improved-v2":
        return PolicyOpponent(spec, SlimeVolleyImprovedV2Policy())
    if name == "improved-v3":
        return PolicyOpponent(spec, SlimeVolleyImprovedV3Policy())
    if name == "improved-v4":
        return PolicyOpponent(spec, SlimeVolleyImprovedV4Policy())
    if name == "improved-v5":
        return PolicyOpponent(spec, SlimeVolleyImprovedV5Policy())
    if name == "improved-v6":
        return PolicyOpponent(spec, SlimeVolleyImprovedV6Policy())
    if name == "improved":
        return PolicyOpponent(spec, SlimeVolleyHeuristicPolicy(structural=True))
    if name == "improved-tuned":
        return PolicyOpponent(spec, SlimeVolleyImprovedTunedPolicy())
    if name == "attack":
        return PolicyOpponent(spec, SlimeVolleyAttackPolicy())
    if name == "rally-serve":
        return PolicyOpponent(spec, SlimeVolleyRallyServePolicy())
    if name == "post-contact":
        return PolicyOpponent(spec, SlimeVolleyPostContactPolicy())
    if name == "net-pressure":
        return PolicyOpponent(spec, SlimeVolleyNetPressurePolicy())
    if name == "temporal":
        return PolicyOpponent(spec, SlimeVolleyTemporalPolicy())
    if name == "planner":
        return PolicyOpponent(spec, SlimeVolleyPlannerPolicy())
    if name == "teacher-assisted":
        return PolicyOpponent(spec, SlimeVolleyTeacherAssistedPolicy())
    if name == "baseline-rnn":
        return PolicyOpponent(spec, SlimeVolleyBuiltInRnnPolicy())
    raise AssertionError(f"unhandled opponent {name!r}")

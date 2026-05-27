"""Transparent SlimeVolley heuristic policies.

The state-space SlimeVolley observation is agent-relative and ordered as:
agent x/y/vx/vy, ball x/y/vx/vy, opponent x/y/vx/vy. The upstream
environment scales these values by 10, so the constants below are expressed in
that normalized observation space.
"""

from __future__ import annotations

import itertools
from collections import deque
from dataclasses import asdict, dataclass, replace
from typing import Any

import numpy as np

from .base import BasePolicy, config_from_dict


ACTION_NOOP = np.asarray([0, 0, 0], dtype=np.int8)
ACTION_FORWARD = np.asarray([1, 0, 0], dtype=np.int8)
ACTION_BACKWARD = np.asarray([0, 1, 0], dtype=np.int8)
ACTION_JUMP = np.asarray([0, 0, 1], dtype=np.int8)


@dataclass(frozen=True)
class SlimeVolleyConfig:
    """Scalar controls for the readable SlimeVolley controller."""

    home_x: float = 1.20
    defensive_home_x: float = 1.35
    attack_home_x: float = 0.82
    x_margin: float = 0.08
    contact_x_window: float = 0.22
    jump_y_min: float = 0.30
    jump_y_max: float = 1.25
    descending_vy: float = -0.015
    landing_horizon: float = 0.38
    high_arc_horizon: float = 0.62
    overcommit_guard_x: float = 0.24
    rear_guard_x: float = 2.05
    serve_steps: int = 24
    serve_ball_x_window: float = 0.20
    serve_ball_y_min: float = 1.45
    rally_serve_detect_y: float = 1.45
    rally_serve_x_window: float = 0.28
    rally_serve_vx_window: float = 0.50
    rally_serve_steps: int = 8
    rally_serve_cooldown_steps: int = 12
    low_ball_rescue_y: float = 0.50
    low_ball_rescue_vy: float = -0.20
    low_ball_rescue_x_window: float = 0.48
    low_ball_rescue_horizon: float = 0.05
    late_low_ball_y: float = 0.26
    late_low_ball_vy: float = -0.50
    late_low_ball_airborne_margin: float = 0.12
    grounded_low_receive_y: float = 0.55
    grounded_low_receive_vy: float = -0.45
    grounded_low_receive_airborne_margin: float = 0.05
    floor_intercept_y: float = 0.78
    floor_intercept_vy: float = -0.60
    floor_intercept_floor_y: float = 0.22
    floor_intercept_time_max: float = 0.32
    rear_wall_press_x: float = 2.05
    rear_wall_press_agent_x: float = 1.70
    rear_wall_press_y: float = 0.65
    rear_wall_press_vy: float = -0.35
    rear_wall_press_jump_margin: float = 0.08
    front_hit_suppression_y_max: float = 1.25
    front_hit_suppression_vx: float = -0.05
    front_hit_suppression_x_margin: float = 0.0
    rear_wall_low_jump_x: float = 2.0
    rear_wall_low_jump_agent_x: float = 1.90
    rear_wall_low_jump_y: float = 0.32
    rear_wall_low_jump_vx: float = -0.20
    rear_wall_low_jump_vy: float = -0.30
    late_attack_y_min: float = 0.28
    late_attack_y_max: float = 0.65
    late_attack_vx: float = -0.35
    late_attack_vy: float = -0.10
    late_attack_dx_min: float = 0.04
    late_attack_dx_max: float = 0.28
    temporal_history_frames: int = 8
    temporal_flip_threshold: float = 0.05
    temporal_jump_cooldown_steps: int = 0
    temporal_contact_hold_steps: int = 9
    temporal_intercept_margin: float = 0.06
    temporal_reliable_vx_delta: float = 0.55
    planner_floor_y: float = 0.22
    planner_net_x: float = 0.0
    planner_net_clearance_y: float = 0.58
    planner_rear_wall_x: float = 2.12
    planner_wall_bounce_decay: float = 0.82
    planner_max_horizon: float = 0.72
    planner_low_time_threshold: float = 0.20
    planner_jump_cooldown_steps: int = 5
    planner_mode_dwell_steps: int = 3
    planner_front_net_guard_x: float = 0.34
    planner_front_net_guard_y: float = 0.42
    planner_aim_offset: float = 0.07
    planner_teacher_contact_extra: float = 0.06
    planner_teacher_low_time_extra: float = 0.05
    planner_teacher_net_margin: float = 0.05



IMPROVED_TUNED_CONFIG = SlimeVolleyConfig(
    x_margin=0.04,
    contact_x_window=0.14,
    high_arc_horizon=0.85,
    overcommit_guard_x=0.18,
    low_ball_rescue_x_window=0.72,
    low_ball_rescue_horizon=0.06,
    grounded_low_receive_airborne_margin=0.12,
)


RALLY_SERVE_CONFIG = SlimeVolleyConfig(
    x_margin=0.04,
    contact_x_window=0.14,
    high_arc_horizon=0.95,
    overcommit_guard_x=0.18,
    low_ball_rescue_x_window=0.54,
    low_ball_rescue_horizon=0.06,
    grounded_low_receive_airborne_margin=0.16,
    landing_horizon=0.38,
    late_attack_y_min=0.24,
    late_attack_vx=-0.45,
    late_attack_vy=-0.35,
    rally_serve_detect_y=1.45,
    rally_serve_x_window=0.28,
    rally_serve_vx_window=0.50,
    rally_serve_steps=8,
    rally_serve_cooldown_steps=12,
)


RALLY_SERVE_LOW_X52_CONFIG = replace(
    RALLY_SERVE_CONFIG,
    low_ball_rescue_x_window=0.52,
)


@dataclass(frozen=True)
class SlimeVolleyTemporalFeatures:
    """Derived short-history features for the transparent temporal controller."""

    frames: int
    ball_ax: float
    ball_ay: float
    stacked_ball_vx: float
    stacked_ball_vy: float
    recent_opponent_contact: bool
    recent_own_contact: bool
    recent_upward_flip: bool
    trajectory_reliable: bool


@dataclass(frozen=True)
class SlimeVolleyPlannerFeatures:
    """Physics-meaningful features derived from current and stacked observations."""

    frames: int
    stacked_ball_vx: float
    stacked_ball_vy: float
    stacked_opponent_vx: float
    opponent_committed_direction: int
    time_to_floor: float
    time_to_net_cross: float | None
    predicted_intercept_x: float
    predicted_net_y: float | None
    net_clearance: float | None
    wall_bounce_imminent: bool
    recent_jump_count: int
    convergence_rate: float
    ball_returning: bool


@dataclass(frozen=True)
class SlimeVolleyModeProposal:
    """Interpretable candidate action from one planner mode."""

    mode: str
    target_x: float
    jump: bool
    score: float
    reason: str


def _state(obs: Any) -> np.ndarray:
    values = np.asarray(obs, dtype=float).reshape(-1)
    if values.size < 12:
        raise ValueError(f"SlimeVolley policy expected at least 12 observation values, got {values.size}")
    return values[:12]


def _clip(value: float, low: float, high: float) -> float:
    return float(min(high, max(low, value)))


def _move_toward(x: float, target_x: float, margin: float) -> np.ndarray:
    if x > target_x + margin:
        return ACTION_FORWARD.copy()
    if x < target_x - margin:
        return ACTION_BACKWARD.copy()
    return ACTION_NOOP.copy()


def _action_key_for_policy(action: Any) -> str:
    values = np.asarray(action if action is not None else [0, 0, 0], dtype=int).reshape(-1)[:3]
    return "".join(str(int(value > 0)) for value in values)


def _with_jump(action: np.ndarray, jump: bool) -> np.ndarray:
    if jump:
        action[2] = 1
    return action.astype(np.int8, copy=False)


class SlimeVolleyHeuristicPolicy(BasePolicy):
    """Readable state-based controller for `SlimeVolley-v0`.

    `initial` mode is intentionally modest: predict where the ball will be soon,
    move toward that x position on our side, and jump only near contact. The
    structural `improved` mode adds serve, recovery, and high-arc modes without
    changing the action interface or hiding behavior in learned weights.
    """

    policy_name = "slimevolley_heuristic"

    def __init__(self, config: SlimeVolleyConfig | None = None, *, structural: bool = False) -> None:
        self._config = config or SlimeVolleyConfig()
        self._structural = structural
        self._steps = 0
        self._last_diagnostics: dict[str, Any] = {}

    def reset(self, seed: int | None = None) -> None:
        del seed
        self._steps = 0
        self._last_diagnostics = {}

    def act(self, obs: Any) -> np.ndarray:
        self._steps += 1
        values = _state(obs)
        x, y, vx, vy, ball_x, ball_y, ball_vx, ball_vy, opp_x, opp_y, opp_vx, opp_vy = values
        del vx, opp_y, opp_vx, opp_vy

        if self._structural:
            return self._act_structural(
                agent_y=y,
                agent_vy=vy,
                x=x,
                ball_x=ball_x,
                ball_y=ball_y,
                ball_vx=ball_vx,
                ball_vy=ball_vy,
                opp_x=opp_x,
            )
        action = self._act_initial(x=x, ball_x=ball_x, ball_y=ball_y, ball_vx=ball_vx, ball_vy=ball_vy)
        return self._record_diagnostics(
            mode="initial",
            action=action,
            target_x=None,
            reason="initial short-horizon ball tracking",
        )

    def diagnostics(self) -> dict[str, Any]:
        """Return the latest transparent branch decision for traces."""

        return dict(self._last_diagnostics)

    def _record_diagnostics(
        self,
        *,
        mode: str,
        action: np.ndarray,
        target_x: float | None,
        reason: str,
    ) -> np.ndarray:
        self._last_diagnostics = {
            "mode": mode,
            "action": _action_key_for_policy(action),
            "target_x": target_x,
            "reason": reason,
        }
        return action

    def _act_initial(self, *, x: float, ball_x: float, ball_y: float, ball_vx: float, ball_vy: float) -> np.ndarray:
        cfg = self._config
        ball_on_our_side = ball_x > 0.0 or ball_vx > 0.0
        if ball_on_our_side:
            target_x = _clip(ball_x + cfg.landing_horizon * ball_vx, cfg.overcommit_guard_x, cfg.rear_guard_x)
        else:
            target_x = cfg.home_x
        action = _move_toward(x, target_x, cfg.x_margin)
        should_jump = (
            abs(ball_x - x) <= cfg.contact_x_window
            and cfg.jump_y_min <= ball_y <= cfg.jump_y_max
            and ball_vy <= cfg.descending_vy
        )
        return _with_jump(action, should_jump)

    def _act_structural(
        self,
        *,
        agent_y: float,
        agent_vy: float,
        x: float,
        ball_x: float,
        ball_y: float,
        ball_vx: float,
        ball_vy: float,
        opp_x: float,
    ) -> np.ndarray:
        cfg = self._config
        serving_window = (
            self._steps <= cfg.serve_steps
            and abs(ball_x) <= cfg.serve_ball_x_window
            and ball_y >= cfg.serve_ball_y_min
        )
        if serving_window:
            action = _move_toward(x, cfg.attack_home_x, cfg.x_margin)
            action = self._suppress_front_hit_jump(
                _with_jump(action, True),
                x=x,
                ball_x=ball_x,
                ball_y=ball_y,
                ball_vx=ball_vx,
            )
            return self._record_diagnostics(
                mode="serve",
                action=action,
                target_x=cfg.attack_home_x,
                reason="serve window attack-home jump",
            )

        rear_wall_low_jump = self._rear_wall_low_jump_action(
            x=x,
            ball_x=ball_x,
            ball_y=ball_y,
            ball_vx=ball_vx,
            ball_vy=ball_vy,
        )
        if rear_wall_low_jump is not None:
            return self._record_diagnostics(
                mode="rear_wall_low_jump",
                action=rear_wall_low_jump,
                target_x=cfg.rear_guard_x,
                reason="low descending ball at rear wall; jump while moving forward",
            )

        rear_wall_press = (
            ball_x >= cfg.rear_wall_press_x
            and x >= cfg.rear_wall_press_agent_x
            and ball_y <= cfg.rear_wall_press_y
            and ball_vy < cfg.rear_wall_press_vy
        )
        if rear_wall_press:
            should_jump = (
                agent_y <= ball_y + cfg.rear_wall_press_jump_margin
                and cfg.jump_y_min <= ball_y <= cfg.jump_y_max
            )
            action = self._suppress_front_hit_jump(
                _with_jump(ACTION_BACKWARD.copy(), should_jump),
                x=x,
                ball_x=ball_x,
                ball_y=ball_y,
                ball_vx=ball_vx,
            )
            return self._record_diagnostics(
                mode="rear_wall_press",
                action=action,
                target_x=cfg.rear_guard_x,
                reason="press rear wall low ball while preserving jump timing",
            )

        falling_floor_intercept = (
            ball_x > -0.05
            and cfg.low_ball_rescue_y < ball_y <= cfg.floor_intercept_y
            and ball_vy < cfg.floor_intercept_vy
        )
        if falling_floor_intercept:
            time_to_floor = (ball_y - cfg.floor_intercept_floor_y) / max(abs(ball_vy), 1e-6)
            horizon = _clip(time_to_floor, 0.0, cfg.floor_intercept_time_max)
            target_x = _clip(
                ball_x + horizon * ball_vx,
                cfg.overcommit_guard_x,
                cfg.rear_guard_x,
            )
            action = _move_toward(x, target_x, cfg.x_margin)
            should_jump = (
                abs(ball_x - x) <= cfg.contact_x_window
                and cfg.jump_y_min <= ball_y <= cfg.jump_y_max
                and ball_vy <= cfg.descending_vy
            )
            action = self._suppress_front_hit_jump(
                _with_jump(action, should_jump),
                x=x,
                ball_x=ball_x,
                ball_y=ball_y,
                ball_vx=ball_vx,
            )
            return self._record_diagnostics(
                mode="falling_floor_intercept",
                action=action,
                target_x=target_x,
                reason="falling ball above low-rescue range; move to clipped floor intercept",
            )

        low_ball_rescue = (
            ball_x > 0.0
            and ball_y <= cfg.low_ball_rescue_y
            and ball_vy < cfg.low_ball_rescue_vy
        )
        if low_ball_rescue:
            target_x = _clip(
                ball_x + cfg.low_ball_rescue_horizon * ball_vx,
                cfg.overcommit_guard_x,
                cfg.rear_guard_x,
            )
            action = _move_toward(x, target_x, cfg.x_margin)
            grounded_low_receive = (
                ball_y <= cfg.grounded_low_receive_y
                and ball_vy < cfg.grounded_low_receive_vy
                and agent_y > ball_y + cfg.grounded_low_receive_airborne_margin
            )
            if grounded_low_receive:
                action = self._suppress_front_hit_jump(
                    _with_jump(action, False),
                    x=x,
                    ball_x=ball_x,
                    ball_y=ball_y,
                    ball_vx=ball_vx,
                )
                return self._record_diagnostics(
                    mode="grounded_low_receive",
                    action=action,
                    target_x=target_x,
                    reason="agent already above late low ball; suppress jump and recover position",
                )
            late_low_ball_guard = (
                ball_y <= cfg.late_low_ball_y
                and ball_vy < cfg.late_low_ball_vy
                and agent_y > ball_y + cfg.late_low_ball_airborne_margin
            )
            if late_low_ball_guard:
                action = self._suppress_front_hit_jump(
                    _with_jump(action, False),
                    x=x,
                    ball_x=ball_x,
                    ball_y=ball_y,
                    ball_vx=ball_vx,
                )
                return self._record_diagnostics(
                    mode="late_low_ball_guard",
                    action=action,
                    target_x=target_x,
                    reason="late low ball guard suppresses mistimed jump",
                )
            action = self._suppress_front_hit_jump(
                _with_jump(action, abs(ball_x - x) <= cfg.low_ball_rescue_x_window),
                x=x,
                ball_x=ball_x,
                ball_y=ball_y,
                ball_vx=ball_vx,
            )
            return self._record_diagnostics(
                mode="low_ball_rescue",
                action=action,
                target_x=target_x,
                reason="fast low ball on agent side; jump if within rescue window",
            )

        ball_returning = ball_x > -0.10 or ball_vx > 0.02
        high_arc = ball_y > cfg.jump_y_max and ball_vy < 0.0
        if high_arc:
            target_x = _clip(ball_x + cfg.high_arc_horizon * ball_vx, cfg.overcommit_guard_x, cfg.rear_guard_x)
        elif ball_returning:
            target_x = _clip(ball_x + cfg.landing_horizon * ball_vx, cfg.overcommit_guard_x, cfg.rear_guard_x)
        else:
            target_x = cfg.defensive_home_x if opp_x < 0.8 else cfg.home_x

        if x < cfg.overcommit_guard_x and not ball_returning:
            target_x = cfg.defensive_home_x
        action = _move_toward(x, target_x, cfg.x_margin)
        low_contact = cfg.jump_y_min <= ball_y <= cfg.jump_y_max
        high_contact = high_arc and abs(ball_x - x) <= cfg.contact_x_window * 1.25 and ball_y <= cfg.jump_y_max + 0.35
        should_jump = (
            abs(ball_x - x) <= cfg.contact_x_window
            and low_contact
            and ball_vy <= cfg.descending_vy
        ) or high_contact
        action = self._suppress_front_hit_jump(
            _with_jump(action, should_jump),
            x=x,
            ball_x=ball_x,
            ball_y=ball_y,
            ball_vx=ball_vx,
        )
        mode = "high_arc" if high_arc else "intercept" if ball_returning else "recovery"
        reason = (
            "descending high arc; move toward longer-horizon landing point"
            if high_arc
            else "ball returning; move toward short-horizon intercept"
            if ball_returning
            else "ball away from agent; recover to defensive home"
        )
        return self._record_diagnostics(
            mode=mode,
            action=action,
            target_x=target_x,
            reason=reason,
        )

    def _rear_wall_low_jump_action(
        self,
        *,
        x: float,
        ball_x: float,
        ball_y: float,
        ball_vx: float,
        ball_vy: float,
    ) -> np.ndarray | None:
        cfg = self._config
        rear_wall_low_jump = (
            ball_x >= cfg.rear_wall_low_jump_x
            and ball_y <= cfg.rear_wall_low_jump_y
            and ball_vx <= cfg.rear_wall_low_jump_vx
            and ball_vy < cfg.rear_wall_low_jump_vy
            and x >= cfg.rear_wall_low_jump_agent_x
        )
        if rear_wall_low_jump:
            return _with_jump(ACTION_FORWARD.copy(), True)
        return None

    def _suppress_front_hit_jump(
        self,
        action: np.ndarray,
        *,
        x: float,
        ball_x: float,
        ball_y: float,
        ball_vx: float,
    ) -> np.ndarray:
        """Avoid jumping into own-side balls from the front side of contact."""

        cfg = self._config
        bad_front_hit = (
            action[2] > 0
            and ball_x > 0.0
            and ball_vx < cfg.front_hit_suppression_vx
            and ball_y < cfg.front_hit_suppression_y_max
            and x < ball_x - cfg.front_hit_suppression_x_margin
        )
        if bad_front_hit:
            action = action.copy()
            action[2] = 0
        return action.astype(np.int8, copy=False)

    def config(self) -> dict[str, Any]:
        values = asdict(self._config)
        values["policy_type"] = "slimevolley_structural" if self._structural else "slimevolley_initial"
        values["structural_modes"] = [
            "serve",
            "recovery",
            "high_arc",
            "rear_wall_press",
            "falling_floor_intercept",
            "low_ball_rescue",
            "late_low_ball_guard",
            "grounded_low_receive",
            "front_hit_suppression",
            "rear_wall_low_jump",
        ] if self._structural else []
        return values


class SlimeVolleyImprovedV0Policy(SlimeVolleyHeuristicPolicy):
    """Frozen structural policy archive before the low-ball-rescue mode."""

    policy_name = "slimevolley_improved_v0_archive"

    def __init__(self, config: SlimeVolleyConfig | None = None) -> None:
        super().__init__(config, structural=True)

    def _act_structural(
        self,
        *,
        agent_y: float,
        agent_vy: float,
        x: float,
        ball_x: float,
        ball_y: float,
        ball_vx: float,
        ball_vy: float,
        opp_x: float,
    ) -> np.ndarray:
        cfg = self._config
        serving_window = (
            self._steps <= cfg.serve_steps
            and abs(ball_x) <= cfg.serve_ball_x_window
            and ball_y >= cfg.serve_ball_y_min
        )
        if serving_window:
            action = _move_toward(x, cfg.attack_home_x, cfg.x_margin)
            return _with_jump(action, True)

        ball_returning = ball_x > -0.10 or ball_vx > 0.02
        high_arc = ball_y > cfg.jump_y_max and ball_vy < 0.0
        if high_arc:
            target_x = _clip(ball_x + cfg.high_arc_horizon * ball_vx, cfg.overcommit_guard_x, cfg.rear_guard_x)
        elif ball_returning:
            target_x = _clip(ball_x + cfg.landing_horizon * ball_vx, cfg.overcommit_guard_x, cfg.rear_guard_x)
        else:
            target_x = cfg.defensive_home_x if opp_x < 0.8 else cfg.home_x

        if x < cfg.overcommit_guard_x and not ball_returning:
            target_x = cfg.defensive_home_x
        action = _move_toward(x, target_x, cfg.x_margin)
        low_contact = cfg.jump_y_min <= ball_y <= cfg.jump_y_max
        high_contact = high_arc and abs(ball_x - x) <= cfg.contact_x_window * 1.25 and ball_y <= cfg.jump_y_max + 0.35
        should_jump = (
            abs(ball_x - x) <= cfg.contact_x_window
            and low_contact
            and ball_vy <= cfg.descending_vy
        ) or high_contact
        return _with_jump(action, should_jump)

    def config(self) -> dict[str, Any]:
        values = asdict(self._config)
        values["policy_type"] = "slimevolley_improved_v0_archive"
        values["structural_modes"] = ["serve", "recovery", "high_arc"]
        values["archive_note"] = "Frozen before low_ball_rescue was added."
        return values


class SlimeVolleyImprovedV1Policy(SlimeVolleyHeuristicPolicy):
    """Frozen structural policy archive before the late-low-ball guard."""

    policy_name = "slimevolley_improved_v1_archive"

    def __init__(self, config: SlimeVolleyConfig | None = None) -> None:
        super().__init__(config, structural=True)

    def _act_structural(
        self,
        *,
        agent_y: float,
        agent_vy: float,
        x: float,
        ball_x: float,
        ball_y: float,
        ball_vx: float,
        ball_vy: float,
        opp_x: float,
    ) -> np.ndarray:
        del agent_y, agent_vy
        cfg = self._config
        serving_window = (
            self._steps <= cfg.serve_steps
            and abs(ball_x) <= cfg.serve_ball_x_window
            and ball_y >= cfg.serve_ball_y_min
        )
        if serving_window:
            action = _move_toward(x, cfg.attack_home_x, cfg.x_margin)
            return _with_jump(action, True)

        low_ball_rescue = (
            ball_x > 0.0
            and ball_y <= cfg.low_ball_rescue_y
            and ball_vy < cfg.low_ball_rescue_vy
        )
        if low_ball_rescue:
            target_x = _clip(
                ball_x + cfg.low_ball_rescue_horizon * ball_vx,
                cfg.overcommit_guard_x,
                cfg.rear_guard_x,
            )
            action = _move_toward(x, target_x, cfg.x_margin)
            return _with_jump(action, abs(ball_x - x) <= cfg.low_ball_rescue_x_window)

        ball_returning = ball_x > -0.10 or ball_vx > 0.02
        high_arc = ball_y > cfg.jump_y_max and ball_vy < 0.0
        if high_arc:
            target_x = _clip(ball_x + cfg.high_arc_horizon * ball_vx, cfg.overcommit_guard_x, cfg.rear_guard_x)
        elif ball_returning:
            target_x = _clip(ball_x + cfg.landing_horizon * ball_vx, cfg.overcommit_guard_x, cfg.rear_guard_x)
        else:
            target_x = cfg.defensive_home_x if opp_x < 0.8 else cfg.home_x

        if x < cfg.overcommit_guard_x and not ball_returning:
            target_x = cfg.defensive_home_x
        action = _move_toward(x, target_x, cfg.x_margin)
        low_contact = cfg.jump_y_min <= ball_y <= cfg.jump_y_max
        high_contact = high_arc and abs(ball_x - x) <= cfg.contact_x_window * 1.25 and ball_y <= cfg.jump_y_max + 0.35
        should_jump = (
            abs(ball_x - x) <= cfg.contact_x_window
            and low_contact
            and ball_vy <= cfg.descending_vy
        ) or high_contact
        return _with_jump(action, should_jump)

    def config(self) -> dict[str, Any]:
        values = asdict(self._config)
        values["policy_type"] = "slimevolley_improved_v1_archive"
        values["structural_modes"] = ["serve", "recovery", "high_arc", "low_ball_rescue"]
        values["archive_note"] = "Frozen before late_low_ball_guard was added."
        return values


class SlimeVolleyImprovedV2Policy(SlimeVolleyHeuristicPolicy):
    """Frozen structural policy archive before grounded low receive."""

    policy_name = "slimevolley_improved_v2_archive"

    def __init__(self, config: SlimeVolleyConfig | None = None) -> None:
        super().__init__(config, structural=True)

    def _act_structural(
        self,
        *,
        agent_y: float,
        agent_vy: float,
        x: float,
        ball_x: float,
        ball_y: float,
        ball_vx: float,
        ball_vy: float,
        opp_x: float,
    ) -> np.ndarray:
        del agent_vy
        cfg = self._config
        serving_window = (
            self._steps <= cfg.serve_steps
            and abs(ball_x) <= cfg.serve_ball_x_window
            and ball_y >= cfg.serve_ball_y_min
        )
        if serving_window:
            action = _move_toward(x, cfg.attack_home_x, cfg.x_margin)
            return _with_jump(action, True)

        low_ball_rescue = (
            ball_x > 0.0
            and ball_y <= cfg.low_ball_rescue_y
            and ball_vy < cfg.low_ball_rescue_vy
        )
        if low_ball_rescue:
            target_x = _clip(
                ball_x + cfg.low_ball_rescue_horizon * ball_vx,
                cfg.overcommit_guard_x,
                cfg.rear_guard_x,
            )
            action = _move_toward(x, target_x, cfg.x_margin)
            late_low_ball_guard = (
                ball_y <= cfg.late_low_ball_y
                and ball_vy < cfg.late_low_ball_vy
                and agent_y > ball_y + cfg.late_low_ball_airborne_margin
            )
            if late_low_ball_guard:
                return _with_jump(action, False)
            return _with_jump(action, abs(ball_x - x) <= cfg.low_ball_rescue_x_window)

        ball_returning = ball_x > -0.10 or ball_vx > 0.02
        high_arc = ball_y > cfg.jump_y_max and ball_vy < 0.0
        if high_arc:
            target_x = _clip(ball_x + cfg.high_arc_horizon * ball_vx, cfg.overcommit_guard_x, cfg.rear_guard_x)
        elif ball_returning:
            target_x = _clip(ball_x + cfg.landing_horizon * ball_vx, cfg.overcommit_guard_x, cfg.rear_guard_x)
        else:
            target_x = cfg.defensive_home_x if opp_x < 0.8 else cfg.home_x

        if x < cfg.overcommit_guard_x and not ball_returning:
            target_x = cfg.defensive_home_x
        action = _move_toward(x, target_x, cfg.x_margin)
        low_contact = cfg.jump_y_min <= ball_y <= cfg.jump_y_max
        high_contact = high_arc and abs(ball_x - x) <= cfg.contact_x_window * 1.25 and ball_y <= cfg.jump_y_max + 0.35
        should_jump = (
            abs(ball_x - x) <= cfg.contact_x_window
            and low_contact
            and ball_vy <= cfg.descending_vy
        ) or high_contact
        return _with_jump(action, should_jump)

    def config(self) -> dict[str, Any]:
        values = asdict(self._config)
        values["policy_type"] = "slimevolley_improved_v2_archive"
        values["structural_modes"] = [
            "serve",
            "recovery",
            "high_arc",
            "low_ball_rescue",
            "late_low_ball_guard",
        ]
        values["archive_note"] = "Frozen before grounded_low_receive was added."
        return values


class SlimeVolleyImprovedV3Policy(SlimeVolleyHeuristicPolicy):
    """Frozen structural policy archive before rear-wall recovery was added."""

    policy_name = "slimevolley_improved_v3_archive"

    def __init__(self, config: SlimeVolleyConfig | None = None) -> None:
        super().__init__(config, structural=True)

    def _act_structural(
        self,
        *,
        agent_y: float,
        agent_vy: float,
        x: float,
        ball_x: float,
        ball_y: float,
        ball_vx: float,
        ball_vy: float,
        opp_x: float,
    ) -> np.ndarray:
        del agent_vy
        cfg = self._config
        serving_window = (
            self._steps <= cfg.serve_steps
            and abs(ball_x) <= cfg.serve_ball_x_window
            and ball_y >= cfg.serve_ball_y_min
        )
        if serving_window:
            action = _move_toward(x, cfg.attack_home_x, cfg.x_margin)
            return _with_jump(action, True)

        falling_floor_intercept = (
            ball_x > -0.05
            and cfg.low_ball_rescue_y < ball_y <= cfg.floor_intercept_y
            and ball_vy < cfg.floor_intercept_vy
        )
        if falling_floor_intercept:
            time_to_floor = (ball_y - cfg.floor_intercept_floor_y) / max(abs(ball_vy), 1e-6)
            horizon = _clip(time_to_floor, 0.0, cfg.floor_intercept_time_max)
            target_x = _clip(
                ball_x + horizon * ball_vx,
                cfg.overcommit_guard_x,
                cfg.rear_guard_x,
            )
            action = _move_toward(x, target_x, cfg.x_margin)
            should_jump = (
                abs(ball_x - x) <= cfg.contact_x_window
                and cfg.jump_y_min <= ball_y <= cfg.jump_y_max
                and ball_vy <= cfg.descending_vy
            )
            return _with_jump(action, should_jump)

        low_ball_rescue = (
            ball_x > 0.0
            and ball_y <= cfg.low_ball_rescue_y
            and ball_vy < cfg.low_ball_rescue_vy
        )
        if low_ball_rescue:
            target_x = _clip(
                ball_x + cfg.low_ball_rescue_horizon * ball_vx,
                cfg.overcommit_guard_x,
                cfg.rear_guard_x,
            )
            action = _move_toward(x, target_x, cfg.x_margin)
            grounded_low_receive = (
                ball_y <= cfg.grounded_low_receive_y
                and ball_vy < cfg.grounded_low_receive_vy
                and agent_y > ball_y + cfg.grounded_low_receive_airborne_margin
            )
            if grounded_low_receive:
                return _with_jump(action, False)
            late_low_ball_guard = (
                ball_y <= cfg.late_low_ball_y
                and ball_vy < cfg.late_low_ball_vy
                and agent_y > ball_y + cfg.late_low_ball_airborne_margin
            )
            if late_low_ball_guard:
                return _with_jump(action, False)
            return _with_jump(action, abs(ball_x - x) <= cfg.low_ball_rescue_x_window)

        ball_returning = ball_x > -0.10 or ball_vx > 0.02
        high_arc = ball_y > cfg.jump_y_max and ball_vy < 0.0
        if high_arc:
            target_x = _clip(ball_x + cfg.high_arc_horizon * ball_vx, cfg.overcommit_guard_x, cfg.rear_guard_x)
        elif ball_returning:
            target_x = _clip(ball_x + cfg.landing_horizon * ball_vx, cfg.overcommit_guard_x, cfg.rear_guard_x)
        else:
            target_x = cfg.defensive_home_x if opp_x < 0.8 else cfg.home_x

        if x < cfg.overcommit_guard_x and not ball_returning:
            target_x = cfg.defensive_home_x
        action = _move_toward(x, target_x, cfg.x_margin)
        low_contact = cfg.jump_y_min <= ball_y <= cfg.jump_y_max
        high_contact = high_arc and abs(ball_x - x) <= cfg.contact_x_window * 1.25 and ball_y <= cfg.jump_y_max + 0.35
        should_jump = (
            abs(ball_x - x) <= cfg.contact_x_window
            and low_contact
            and ball_vy <= cfg.descending_vy
        ) or high_contact
        return _with_jump(action, should_jump)

    def config(self) -> dict[str, Any]:
        values = asdict(self._config)
        values["policy_type"] = "slimevolley_improved_v3_archive"
        values["structural_modes"] = [
            "serve",
            "recovery",
            "high_arc",
            "falling_floor_intercept",
            "low_ball_rescue",
            "late_low_ball_guard",
            "grounded_low_receive",
        ]
        values["archive_note"] = "Frozen before generation-3 rear_wall_press was added."
        return values


class SlimeVolleyImprovedV4Policy(SlimeVolleyHeuristicPolicy):
    """Frozen structural policy archive before front-hit jump suppression."""

    policy_name = "slimevolley_improved_v4_archive"

    def __init__(self, config: SlimeVolleyConfig | None = None) -> None:
        super().__init__(config, structural=True)

    def _suppress_front_hit_jump(
        self,
        action: np.ndarray,
        *,
        x: float,
        ball_x: float,
        ball_y: float,
        ball_vx: float,
    ) -> np.ndarray:
        del x, ball_x, ball_y, ball_vx
        return action.astype(np.int8, copy=False)

    def _rear_wall_low_jump_action(
        self,
        *,
        x: float,
        ball_x: float,
        ball_y: float,
        ball_vx: float,
        ball_vy: float,
    ) -> np.ndarray | None:
        del x, ball_x, ball_y, ball_vx, ball_vy
        return None

    def config(self) -> dict[str, Any]:
        values = asdict(self._config)
        values["policy_type"] = "slimevolley_improved_v4_archive"
        values["structural_modes"] = [
            "serve",
            "recovery",
            "high_arc",
            "rear_wall_press",
            "falling_floor_intercept",
            "low_ball_rescue",
            "late_low_ball_guard",
            "grounded_low_receive",
        ]
        values["archive_note"] = "Frozen before generation-4 front_hit_suppression was added."
        return values


class SlimeVolleyImprovedV5Policy(SlimeVolleyHeuristicPolicy):
    """Frozen structural policy archive before rear-wall low-jump rescue."""

    policy_name = "slimevolley_improved_v5_archive"

    def __init__(self, config: SlimeVolleyConfig | None = None) -> None:
        super().__init__(config, structural=True)

    def _rear_wall_low_jump_action(
        self,
        *,
        x: float,
        ball_x: float,
        ball_y: float,
        ball_vx: float,
        ball_vy: float,
    ) -> np.ndarray | None:
        del x, ball_x, ball_y, ball_vx, ball_vy
        return None

    def config(self) -> dict[str, Any]:
        values = asdict(self._config)
        values["policy_type"] = "slimevolley_improved_v5_archive"
        values["structural_modes"] = [
            "serve",
            "recovery",
            "high_arc",
            "rear_wall_press",
            "falling_floor_intercept",
            "low_ball_rescue",
            "late_low_ball_guard",
            "grounded_low_receive",
            "front_hit_suppression",
        ]
        values["archive_note"] = "Frozen before generation-4 rear_wall_low_jump was added."
        return values


class SlimeVolleyImprovedV6Policy(SlimeVolleyHeuristicPolicy):
    """Frozen structural policy archive before front-net low-scoop rescue."""

    policy_name = "slimevolley_improved_v6_archive"

    def __init__(self, config: SlimeVolleyConfig | None = None) -> None:
        super().__init__(config, structural=True)

    def config(self) -> dict[str, Any]:
        values = asdict(self._config)
        values["policy_type"] = "slimevolley_improved_v6_archive"
        values["structural_modes"] = [
            "serve",
            "recovery",
            "high_arc",
            "rear_wall_press",
            "falling_floor_intercept",
            "low_ball_rescue",
            "late_low_ball_guard",
            "grounded_low_receive",
            "front_hit_suppression",
            "rear_wall_low_jump",
        ]
        values["archive_note"] = "Frozen before generation-4 front_net_low_scoop was added."
        return values


class SlimeVolleyImprovedTunedPolicy(SlimeVolleyHeuristicPolicy):
    """Scalar-tuned version of the maintained structural heuristic.

    This is intentionally not a structural archive. The tuned constants were
    selected on generation-4 development seeds and must be compared separately
    from code-level heuristic improvements.
    """

    policy_name = "slimevolley_improved_tuned"

    def __init__(self, config: SlimeVolleyConfig | None = None) -> None:
        super().__init__(config or IMPROVED_TUNED_CONFIG, structural=True)

    def config(self) -> dict[str, Any]:
        values = super().config()
        values["policy_type"] = "slimevolley_improved_tuned"
        values["tuned_from"] = "improved-v6/current-rear_wall_low_jump"
        values["tuning_label"] = "scalar/config tuning"
        values["tuned_revision"] = "g4-scalar-tuned-v2"
        values["tuned_fields"] = {
            "x_margin": self._config.x_margin,
            "contact_x_window": self._config.contact_x_window,
            "high_arc_horizon": self._config.high_arc_horizon,
            "overcommit_guard_x": self._config.overcommit_guard_x,
            "low_ball_rescue_x_window": self._config.low_ball_rescue_x_window,
            "low_ball_rescue_horizon": self._config.low_ball_rescue_horizon,
            "grounded_low_receive_airborne_margin": self._config.grounded_low_receive_airborne_margin,
        }
        return values


class SlimeVolleyAttackPolicy(SlimeVolleyImprovedTunedPolicy):
    """Generation-4 structural late-contact attack candidate.

    The rule is intentionally narrow: when a low, descending ball is already
    moving toward the opponent and the agent is slightly behind the contact
    point, drive forward+jump to attempt an active return. Development evidence
    improved the built-in score but regressed the nearest archived opponents, so
    this candidate is not promoted over ``improved-tuned``.
    """

    policy_name = "slimevolley_attack_candidate"

    def act(self, obs: Any) -> np.ndarray:
        action = super().act(obs)
        values = _state(obs)
        x, _y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy = values[:8]
        cfg = self._config
        dx = x - ball_x
        late_contact_attack = (
            ball_x > 0.05
            and cfg.late_attack_y_min <= ball_y <= cfg.late_attack_y_max
            and ball_vx < cfg.late_attack_vx
            and ball_vy < cfg.late_attack_vy
            and cfg.late_attack_dx_min <= dx <= cfg.late_attack_dx_max
        )
        if late_contact_attack:
            action = _with_jump(ACTION_FORWARD.copy(), True)
            return self._record_diagnostics(
                mode="late_contact_attack",
                action=action,
                target_x=ball_x,
                reason="low descending ball moving toward opponent; drive forward+jump from behind contact",
            )
        return action

    def config(self) -> dict[str, Any]:
        values = super().config()
        values["policy_type"] = "slimevolley_attack_candidate"
        values["candidate_status"] = "partial_not_promoted"
        values["structural_change"] = "late_contact_attack"
        values["structural_rule"] = {
            "ball_x_min": 0.05,
            "late_attack_y_min": self._config.late_attack_y_min,
            "late_attack_y_max": self._config.late_attack_y_max,
            "late_attack_vx": self._config.late_attack_vx,
            "late_attack_vy": self._config.late_attack_vy,
            "late_attack_dx_min": self._config.late_attack_dx_min,
            "late_attack_dx_max": self._config.late_attack_dx_max,
            "action": "101",
        }
        return values




class SlimeVolleyRallyServePolicy(SlimeVolleyAttackPolicy):
    """Generation-4 rally-serve structural candidate.

    SlimeVolley resets the ball after each point, but earlier heuristic policies
    only ran their serve macro during the first few episode steps. This candidate
    detects later point-reset serve states directly from observation geometry and
    repeats a short forward+jump macro. It keeps the late-contact attack rule and
    uses scalar fields selected on generation-4 development seeds, so reports
    must label it as structural plus scalar/config tuning rather than a pure
    structural improvement.
    """

    policy_name = "slimevolley_rally_serve_candidate"

    def __init__(self, config: SlimeVolleyConfig | None = None) -> None:
        super().__init__(config or RALLY_SERVE_CONFIG)
        self._rally_serve_left = 0
        self._last_rally_serve_detect_step = -10_000

    def reset(self, seed: int | None = None) -> None:
        super().reset(seed)
        self._rally_serve_left = 0
        self._last_rally_serve_detect_step = -10_000

    def act(self, obs: Any) -> np.ndarray:
        values = _state(obs)
        ball_x, ball_y, ball_vx = values[4], values[5], values[6]
        cfg = self._config
        next_step = self._steps + 1
        serve_reset_detected = (
            abs(ball_x) <= cfg.rally_serve_x_window
            and ball_y >= cfg.rally_serve_detect_y
            and abs(ball_vx) <= cfg.rally_serve_vx_window
            and next_step - self._last_rally_serve_detect_step > cfg.rally_serve_cooldown_steps
        )
        if serve_reset_detected:
            self._rally_serve_left = cfg.rally_serve_steps
            self._last_rally_serve_detect_step = next_step

        if self._rally_serve_left > 0:
            self._steps = next_step
            self._rally_serve_left -= 1
            action = _with_jump(ACTION_FORWARD.copy(), True)
            return self._record_diagnostics(
                mode="rally_serve",
                action=action,
                target_x=0.0,
                reason="point-reset serve detector; forward+jump macro",
            )
        return super().act(obs)

    def config(self) -> dict[str, Any]:
        values = super().config()
        values["policy_type"] = "slimevolley_rally_serve_candidate"
        values["candidate_status"] = "dev_beat_baseline_rnn_failed_generation_4_holdout"
        values["tuning_label"] = "structural rally-serve detector plus scalar/config tuning"
        values["structural_changes"] = ["late_contact_attack", "rally_serve_detector"]
        values["rally_serve_rule"] = {
            "ball_abs_x_max": self._config.rally_serve_x_window,
            "ball_y_min": self._config.rally_serve_detect_y,
            "ball_abs_vx_max": self._config.rally_serve_vx_window,
            "steps": self._config.rally_serve_steps,
            "cooldown_steps": self._config.rally_serve_cooldown_steps,
            "action": "101",
        }
        values["development_result"] = {
            "seeds": "9000..9049",
            "opponent": "builtin",
            "mean": 0.14,
            "wld": "13/8/29",
            "baseline_rnn_mean": 0.12,
            "holdout_status": "generation_4_failed_to_beat_baseline_rnn",
        }
        return values


class SlimeVolleyPostContactPolicy(SlimeVolleyRallyServePolicy):
    """Generation-4 post-contact front-conversion candidate.

    A development-only probe found that a narrow two-frame contact detector
    preserved the `rally-serve` built-in development score while improving the
    harder archived-opponent rows. This class keeps the rule transparent and
    separate from the frozen `rally-serve` candidate. It has not been validated
    on sealed holdout or audit seeds.
    """

    policy_name = "slimevolley_post_contact_candidate"

    def __init__(self, config: SlimeVolleyConfig | None = None) -> None:
        super().__init__(config)
        self._previous_values: np.ndarray | None = None
        self._recent_own_contact = 999
        self._recent_upward_flip = 999

    def reset(self, seed: int | None = None) -> None:
        super().reset(seed)
        self._previous_values = None
        self._recent_own_contact = 999
        self._recent_upward_flip = 999

    def _update_post_contact_features(self, values: np.ndarray) -> None:
        if self._previous_values is None:
            self._recent_own_contact += 1
            self._recent_upward_flip += 1
            self._previous_values = values.copy()
            return

        previous = self._previous_values
        own_vx_flip = previous[6] > 0.08 and values[6] < -0.08 and values[4] > -0.05
        own_vy_flip = previous[7] < -0.10 and values[7] > 0.04 and values[4] > -0.05 and values[5] < 1.05
        if own_vx_flip or own_vy_flip:
            self._recent_own_contact = 0
        else:
            self._recent_own_contact += 1
        if own_vy_flip:
            self._recent_upward_flip = 0
        else:
            self._recent_upward_flip += 1
        self._previous_values = values.copy()

    def act(self, obs: Any) -> np.ndarray:
        values = _state(obs)
        self._update_post_contact_features(values)
        action = super().act(obs)
        if self._last_diagnostics.get("mode") == "rally_serve":
            return action

        x, _y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy = values[:8]
        dx = x - ball_x
        front_post_contact = (
            min(self._recent_own_contact, self._recent_upward_flip) <= 2
            and -0.08 <= ball_x <= 0.48
            and 0.24 <= ball_y <= 0.82
            and ball_vx < -0.04
            and ball_vy <= 0.12
            and -0.05 <= dx <= 0.70
        )
        if front_post_contact:
            conversion_action = _with_jump(ACTION_FORWARD.copy(), True)
            return self._record_diagnostics(
                mode="post_contact_front_conversion",
                action=conversion_action,
                target_x=ball_x,
                reason="recent contact-like flip near net; forward+jump conversion attempt",
            )
        return action

    def config(self) -> dict[str, Any]:
        values = super().config()
        values["policy_type"] = "slimevolley_post_contact_candidate"
        values["candidate_status"] = "development_only_not_holdout_validated"
        values["tuning_label"] = "structural post-contact detector plus rally-serve scalar/config baseline"
        values["structural_changes"] = [
            "late_contact_attack",
            "rally_serve_detector",
            "post_contact_front_conversion",
        ]
        values["post_contact_front_conversion_rule"] = {
            "recent_contact_window_steps": 2,
            "ball_x_range": [-0.08, 0.48],
            "ball_y_range": [0.24, 0.82],
            "ball_vx_max": -0.04,
            "ball_vy_max": 0.12,
            "agent_minus_ball_x_range": [-0.05, 0.70],
            "action": "101",
        }
        values["development_result"] = {
            "seeds": "9000..9049",
            "opponent_pool": "builtin, random, initial, improved-v0, improved-v2, improved-v3, improved-v4, improved-v5, improved-v6",
            "built_in_mean": 0.14,
            "built_in_wld": "13/8/29",
            "baseline_rnn_builtin_mean": 0.12,
            "archived_mean_deltas_vs_rally_serve": {
                "improved-v3": 0.06,
                "improved-v4": 0.06,
                "improved-v5": 0.06,
                "improved-v6": 0.06,
            },
            "holdout_status": "not_evaluated_do_not_tune_on_generation_4_holdout",
        }
        return values


class SlimeVolleyRallyServeLowX52Policy(SlimeVolleyRallyServePolicy):
    """Development-only scalar/config candidate from generation-4 parallel6.

    This preserves the historical ``rally-serve`` policy and exposes the single
    scalar change that passed a development fixed-pool check. It is not a
    structural heuristic improvement and must not be treated as holdout evidence.
    """

    policy_name = "slimevolley_rally_serve_low_x52_candidate"

    def __init__(self, config: SlimeVolleyConfig | None = None) -> None:
        super().__init__(config or RALLY_SERVE_LOW_X52_CONFIG)

    def config(self) -> dict[str, Any]:
        values = super().config()
        values["policy_type"] = "slimevolley_rally_serve_low_x52_candidate"
        values["candidate_status"] = "generation_4_development_only_scalar_config_candidate"
        values["tuning_label"] = "scalar/config tuning over rally-serve"
        values["structural_changes"] = ["late_contact_attack", "rally_serve_detector"]
        values["scalar_change"] = {
            "base_policy": "rally-serve",
            "low_ball_rescue_x_window": self._config.low_ball_rescue_x_window,
            "previous_rally_serve_value": RALLY_SERVE_CONFIG.low_ball_rescue_x_window,
        }
        values["development_result"] = {
            "seeds": "9000..9049",
            "opponent_pool": "builtin, random, initial, improved-v0, improved-v2, improved-v3, improved-v4, improved-v5, improved-v6",
            "built_in_mean": 0.18,
            "built_in_wld": "14/8/28",
            "baseline_rnn_builtin_mean": 0.12,
            "rally_serve_builtin_mean": 0.14,
            "evidence_note": "Passed fixed development opponent-pool check in parallel6, but remains scalar-only development evidence.",
            "holdout_status": "not_evaluated_do_not_tune_on_generation_4_holdout_or_audit",
        }
        return values


class SlimeVolleyNetPressurePolicy(SlimeVolleyRallyServePolicy):
    """Generation-5 structural front-court pressure probe.

    Generation-5 development diagnostics showed `rally-serve` drawing far more
    often than the packaged RNN while using far fewer forward+jump actions. This
    candidate adds one readable pressure rule: if a controllable ball is near
    the front court and moving toward the opponent, drive forward+jump from
    behind the contact point. It is a probe, not a promoted policy.
    """

    policy_name = "slimevolley_net_pressure_candidate"

    def act(self, obs: Any) -> np.ndarray:
        action = super().act(obs)
        if self._last_diagnostics.get("mode") == "rally_serve":
            return action

        values = _state(obs)
        x, _y, _vx, _vy, ball_x, ball_y, ball_vx, ball_vy = values[:8]
        front_pressure = (
            -0.08 <= ball_x <= 0.55
            and 0.58 <= ball_y <= 1.30
            and ball_vx <= -0.02
            and ball_vy <= 0.08
            and 0.08 <= x - ball_x <= 0.72
        )
        if front_pressure:
            pressure_action = _with_jump(ACTION_FORWARD.copy(), True)
            return self._record_diagnostics(
                mode="net_pressure",
                action=pressure_action,
                target_x=ball_x,
                reason="front-court ball moving toward opponent; drive forward+jump to convert draws into points",
            )
        return action

    def config(self) -> dict[str, Any]:
        values = super().config()
        values["policy_type"] = "slimevolley_net_pressure_candidate"
        values["candidate_status"] = "generation_5_structural_probe"
        values["structural_changes"] = [
            "late_contact_attack",
            "rally_serve_detector",
            "net_pressure",
        ]
        values["net_pressure_rule"] = {
            "ball_x_range": [-0.08, 0.55],
            "ball_y_range": [0.58, 1.30],
            "ball_vx_max": -0.02,
            "ball_vy_max": 0.08,
            "agent_minus_ball_x_range": [0.08, 0.72],
            "action": "101",
        }
        return values


class SlimeVolleyTemporalPolicy(SlimeVolleyHeuristicPolicy):
    """Structural heuristic with a short stacked-observation memory.

    This remains a transparent controller: history is used only to derive named
    event features such as recent velocity flips and simple finite-difference
    ball motion. The jump guard is optional and disabled by default after the
    first development trial showed that cooldown suppression cost too many
    reachable contacts. It is intentionally separate from
    ``improved`` until development-seed evidence justifies promotion.
    """

    policy_name = "slimevolley_temporal"

    def __init__(self, config: SlimeVolleyConfig | None = None) -> None:
        super().__init__(config, structural=True)
        self._obs_history: deque[np.ndarray] = deque(maxlen=self._config.temporal_history_frames)
        self._action_history: deque[np.ndarray] = deque(maxlen=self._config.temporal_history_frames)
        self._last_jump_step = -10_000
        self._last_contact_step = -10_000
        self._last_contact_side = "none"
        self._phase = "recover"

    def reset(self, seed: int | None = None) -> None:
        super().reset(seed)
        self._obs_history.clear()
        self._action_history.clear()
        self._last_jump_step = -10_000
        self._last_contact_step = -10_000
        self._last_contact_side = "none"
        self._phase = "recover"

    def act(self, obs: Any) -> np.ndarray:
        self._steps += 1
        values = _state(obs)
        x, y, vx, vy, ball_x, ball_y, ball_vx, ball_vy, opp_x, opp_y, opp_vx, opp_vy = values
        del vx, opp_y, opp_vx, opp_vy
        features = self._temporal_features(values)
        if features.recent_opponent_contact:
            self._last_contact_step = self._steps
            self._last_contact_side = "opponent"
        elif features.recent_own_contact:
            self._last_contact_step = self._steps
            self._last_contact_side = "self"

        action = self._act_temporal(
            agent_y=y,
            agent_vy=vy,
            x=x,
            ball_x=ball_x,
            ball_y=ball_y,
            ball_vx=ball_vx,
            ball_vy=ball_vy,
            opp_x=opp_x,
            features=features,
        )
        if action[2] > 0:
            self._last_jump_step = self._steps
        self._obs_history.append(values.copy())
        self._action_history.append(action.copy())
        return action

    def _temporal_features(self, values: np.ndarray) -> SlimeVolleyTemporalFeatures:
        cfg = self._config
        history = list(self._obs_history)
        frames = len(history) + 1
        if not history:
            return SlimeVolleyTemporalFeatures(
                frames=frames,
                ball_ax=0.0,
                ball_ay=0.0,
                stacked_ball_vx=float(values[6]),
                stacked_ball_vy=float(values[7]),
                recent_opponent_contact=False,
                recent_own_contact=False,
                recent_upward_flip=False,
                trajectory_reliable=True,
            )

        prev = history[-1]
        window = [*history[-(cfg.temporal_history_frames - 1):], values]
        span = max(1, len(window) - 1)
        stacked_ball_vx = float((window[-1][4] - window[0][4]) / span)
        stacked_ball_vy = float((window[-1][5] - window[0][5]) / span)
        threshold = cfg.temporal_flip_threshold
        recent_opponent_contact = False
        recent_own_contact = False
        recent_upward_flip = False
        for before, after in zip(window, window[1:]):
            before_vx = float(before[6])
            after_vx = float(after[6])
            after_x = float(after[4])
            before_vy = float(before[7])
            after_vy = float(after[7])
            if before_vx < -threshold and after_vx > threshold and after_x < 0.55:
                recent_opponent_contact = True
            if before_vx > threshold and after_vx < -threshold and after_x > 0.05:
                recent_own_contact = True
            if before_vy < -threshold and after_vy > threshold:
                recent_upward_flip = True

        reported_vx = float(values[6])
        stacked_direction_conflict = (
            abs(reported_vx) > threshold
            and abs(stacked_ball_vx) > 0.01
            and reported_vx * stacked_ball_vx < 0.0
        )
        abrupt_vx_change = abs(float(values[6]) - float(prev[6])) > cfg.temporal_reliable_vx_delta
        trajectory_reliable = not (stacked_direction_conflict or (abrupt_vx_change and not recent_opponent_contact))
        return SlimeVolleyTemporalFeatures(
            frames=frames,
            ball_ax=float(values[6] - prev[6]),
            ball_ay=float(values[7] - prev[7]),
            stacked_ball_vx=stacked_ball_vx,
            stacked_ball_vy=stacked_ball_vy,
            recent_opponent_contact=recent_opponent_contact,
            recent_own_contact=recent_own_contact,
            recent_upward_flip=recent_upward_flip,
            trajectory_reliable=trajectory_reliable,
        )

    def _act_temporal(
        self,
        *,
        agent_y: float,
        agent_vy: float,
        x: float,
        ball_x: float,
        ball_y: float,
        ball_vx: float,
        ball_vy: float,
        opp_x: float,
        features: SlimeVolleyTemporalFeatures,
    ) -> np.ndarray:
        cfg = self._config
        base_action = self._act_structural(
            agent_y=agent_y,
            agent_vy=agent_vy,
            x=x,
            ball_x=ball_x,
            ball_y=ball_y,
            ball_vx=ball_vx,
            ball_vy=ball_vy,
            opp_x=opp_x,
        )

        serving_window = (
            self._steps <= cfg.serve_steps
            and abs(ball_x) <= cfg.serve_ball_x_window
            and ball_y >= cfg.serve_ball_y_min
        )
        if serving_window:
            self._phase = "serve"
            return base_action

        urgent_low_rescue = ball_x > 0.0 and ball_y <= cfg.low_ball_rescue_y and ball_vy < cfg.low_ball_rescue_vy
        urgent_floor_intercept = (
            ball_x > -0.05
            and cfg.low_ball_rescue_y < ball_y <= cfg.floor_intercept_y
            and ball_vy < cfg.floor_intercept_vy
        )
        urgent_rear_wall = (
            ball_x >= cfg.rear_wall_press_x
            and x >= cfg.rear_wall_press_agent_x
            and ball_y <= cfg.rear_wall_press_y
            and ball_vy < cfg.rear_wall_press_vy
        )
        if urgent_low_rescue or urgent_floor_intercept or urgent_rear_wall:
            self._phase = "urgent_single_frame_guard"
            return base_action

        ball_returning = ball_x > -0.10 or ball_vx > 0.02
        frames_since_contact = self._steps - self._last_contact_step
        if (
            self._last_contact_side == "self"
            and frames_since_contact <= cfg.temporal_contact_hold_steps
            and not ball_returning
        ):
            self._phase = "post_contact_recover"
            action = _move_toward(x, cfg.defensive_home_x, cfg.x_margin)
            return _with_jump(action, False)

        if features.recent_opponent_contact and ball_returning:
            self._phase = "opponent_contact_intercept"
            blended_vx = ball_vx if abs(ball_vx) >= abs(features.stacked_ball_vx) else features.stacked_ball_vx
            target_x = _clip(
                ball_x + (cfg.landing_horizon + 0.12) * blended_vx + cfg.temporal_intercept_margin,
                cfg.overcommit_guard_x,
                cfg.rear_guard_x,
            )
            action = _move_toward(x, target_x, cfg.x_margin)
            low_contact = cfg.jump_y_min <= ball_y <= cfg.jump_y_max
            should_jump = (
                abs(ball_x - x) <= cfg.contact_x_window
                and low_contact
                and ball_vy <= cfg.descending_vy
            )
            return self._with_temporal_jump_guard(action, should_jump, emergency=False)

        self._phase = "single_frame_fallback"
        emergency = ball_x > 0.0 and ball_y <= cfg.low_ball_rescue_y and ball_vy < cfg.low_ball_rescue_vy
        return self._with_temporal_jump_guard(base_action.copy(), bool(base_action[2]), emergency=emergency)

    def _with_temporal_jump_guard(self, action: np.ndarray, jump: bool, *, emergency: bool) -> np.ndarray:
        cfg = self._config
        if jump and not emergency and self._steps - self._last_jump_step <= cfg.temporal_jump_cooldown_steps:
            jump = False
        guarded = action.copy()
        guarded[2] = 0
        return _with_jump(guarded, jump)

    def config(self) -> dict[str, Any]:
        values = asdict(self._config)
        values["policy_type"] = "slimevolley_temporal_stacked_history"
        values["history_features"] = [
            "stacked_ball_vx",
            "stacked_ball_vy",
            "ball_ax",
            "ball_ay",
            "recent_opponent_contact",
            "recent_own_contact",
            "recent_upward_flip",
            "trajectory_reliable",
        ]
        values["structural_modes"] = [
            "serve",
            "urgent_single_frame_guard",
            "post_contact_recover",
            "opponent_contact_intercept",
            "single_frame_fallback",
        ]
        values["archive_note"] = "Generation-4 candidate; not promoted unless development evidence improves over current improved."
        return values


class SlimeVolleyPlannerPolicy(SlimeVolleyTemporalPolicy):
    """Physics-feature planner for generation-4 SlimeVolley experiments.

    The planner keeps the controller transparent: stacked frames are reduced to
    named quantities such as time-to-floor, net clearance, one-wall-bounce
    intercepts, opponent commitment, and recent jump count. It does not learn
    weights and it does not call the RNN comparator at runtime.
    """

    policy_name = "slimevolley_planner"

    def __init__(self, config: SlimeVolleyConfig | None = None, *, teacher_assisted: bool = False) -> None:
        super().__init__(config)
        self._teacher_assisted = teacher_assisted
        self._last_mode_step = -10_000
        self._last_diagnostics: dict[str, Any] = {}

    def reset(self, seed: int | None = None) -> None:
        super().reset(seed)
        self._last_mode_step = -10_000
        self._last_diagnostics = {}

    def act(self, obs: Any) -> np.ndarray:
        self._steps += 1
        values = _state(obs)
        x, y, vx, vy, ball_x, ball_y, ball_vx, ball_vy, opp_x, opp_y, opp_vx, opp_vy = values
        del vx, opp_y, opp_vx, opp_vy
        features = self._planner_features(values)
        base_action = self._act_structural(
            agent_y=y,
            agent_vy=vy,
            x=x,
            ball_x=ball_x,
            ball_y=ball_y,
            ball_vx=ball_vx,
            ball_vy=ball_vy,
            opp_x=opp_x,
        )
        proposals = self._planner_proposals(
            agent_y=y,
            agent_vy=vy,
            x=x,
            ball_x=ball_x,
            ball_y=ball_y,
            ball_vx=ball_vx,
            ball_vy=ball_vy,
            opp_x=opp_x,
            features=features,
        )
        proposal = self._choose_planner_proposal(proposals)
        action = self._planner_action(x=x, proposal=proposal, features=features)
        safety_action = self._structural_safety_action(
            base_action=base_action,
            planner_action=action,
            ball_x=ball_x,
            ball_y=ball_y,
            ball_vy=ball_vy,
            features=features,
        )
        if safety_action is not None:
            action = safety_action
            proposal = SlimeVolleyModeProposal(
                mode="planner_structural_safety",
                target_x=features.predicted_intercept_x,
                jump=bool(action[2]),
                score=proposal.score + 0.25,
                reason="preserve archived structural low-ball/rear-wall contact guard",
            )
        if action[2] > 0:
            self._last_jump_step = self._steps
        if proposal.mode != self._phase:
            self._last_mode_step = self._steps
        self._phase = proposal.mode
        self._last_diagnostics = self._diagnostics_payload(features, proposal, action)
        self._obs_history.append(values.copy())
        self._action_history.append(action.copy())
        return action

    def diagnostics(self) -> dict[str, Any]:
        """Return the latest transparent planner decision for traces."""

        return dict(self._last_diagnostics)

    def _planner_features(self, values: np.ndarray) -> SlimeVolleyPlannerFeatures:
        cfg = self._config
        history = list(self._obs_history)
        window = [*history[-(cfg.temporal_history_frames - 1):], values]
        frames = len(window)
        span = max(1, frames - 1)
        x = float(values[0])
        ball_x = float(values[4])
        ball_y = float(values[5])
        ball_vx = float(values[6])
        ball_vy = float(values[7])
        stacked_ball_vx = float((window[-1][4] - window[0][4]) / span)
        stacked_ball_vy = float((window[-1][5] - window[0][5]) / span)
        stacked_opponent_vx = float((window[-1][8] - window[0][8]) / span)

        opponent_deltas = [float(after[8] - before[8]) for before, after in zip(window, window[1:])]
        nonzero_opponent_signs = [1 if delta > 0.002 else -1 for delta in opponent_deltas if abs(delta) > 0.002]
        opponent_committed_direction = 0
        if nonzero_opponent_signs and all(sign == nonzero_opponent_signs[0] for sign in nonzero_opponent_signs):
            opponent_committed_direction = nonzero_opponent_signs[0]

        if ball_vy < -1e-6 and ball_y > cfg.planner_floor_y:
            time_to_floor = (ball_y - cfg.planner_floor_y) / abs(ball_vy)
        else:
            time_to_floor = cfg.planner_max_horizon
        time_to_floor = _clip(time_to_floor, 0.0, cfg.planner_max_horizon)

        raw_intercept_x = ball_x + time_to_floor * ball_vx
        wall_bounce_imminent = raw_intercept_x > cfg.planner_rear_wall_x
        predicted_intercept_x = raw_intercept_x
        if wall_bounce_imminent:
            overshoot = raw_intercept_x - cfg.planner_rear_wall_x
            predicted_intercept_x = cfg.planner_rear_wall_x - overshoot * cfg.planner_wall_bounce_decay
        predicted_intercept_x = _clip(predicted_intercept_x, cfg.overcommit_guard_x, cfg.rear_guard_x)

        time_to_net_cross: float | None = None
        predicted_net_y: float | None = None
        net_clearance: float | None = None
        if abs(ball_vx) > 1e-6:
            candidate_time = (cfg.planner_net_x - ball_x) / ball_vx
            if 0.0 <= candidate_time <= cfg.planner_max_horizon:
                time_to_net_cross = float(candidate_time)
                predicted_net_y = float(ball_y + candidate_time * ball_vy)
                net_clearance = float(predicted_net_y - cfg.planner_net_clearance_y)

        recent_jump_count = sum(
            1 for action in self._action_history
            if np.asarray(action, dtype=int).reshape(-1).size >= 3 and int(np.asarray(action, dtype=int).reshape(-1)[2] > 0)
        )
        if history:
            previous = history[-1]
            previous_distance = abs(float(previous[4]) - float(previous[0]))
            current_distance = abs(ball_x - x)
            convergence_rate = previous_distance - current_distance
        else:
            convergence_rate = 0.0
        ball_returning = ball_x > -0.10 or max(ball_vx, stacked_ball_vx) > 0.02
        return SlimeVolleyPlannerFeatures(
            frames=frames,
            stacked_ball_vx=stacked_ball_vx,
            stacked_ball_vy=stacked_ball_vy,
            stacked_opponent_vx=stacked_opponent_vx,
            opponent_committed_direction=opponent_committed_direction,
            time_to_floor=time_to_floor,
            time_to_net_cross=time_to_net_cross,
            predicted_intercept_x=predicted_intercept_x,
            predicted_net_y=predicted_net_y,
            net_clearance=net_clearance,
            wall_bounce_imminent=wall_bounce_imminent,
            recent_jump_count=recent_jump_count,
            convergence_rate=convergence_rate,
            ball_returning=ball_returning,
        )

    def _planner_proposals(
        self,
        *,
        agent_y: float,
        agent_vy: float,
        x: float,
        ball_x: float,
        ball_y: float,
        ball_vx: float,
        ball_vy: float,
        opp_x: float,
        features: SlimeVolleyPlannerFeatures,
    ) -> list[SlimeVolleyModeProposal]:
        del agent_vy
        cfg = self._config
        proposals: list[SlimeVolleyModeProposal] = []
        serving_window = (
            self._steps <= cfg.serve_steps
            and abs(ball_x) <= cfg.serve_ball_x_window
            and ball_y >= cfg.serve_ball_y_min
        )
        if serving_window:
            serve_offset = cfg.planner_aim_offset if self._teacher_assisted and (self._steps // 4) % 2 == 0 else 0.0
            proposals.append(
                SlimeVolleyModeProposal(
                    mode="planner_serve",
                    target_x=_clip(cfg.attack_home_x + serve_offset, cfg.overcommit_guard_x, cfg.rear_guard_x),
                    jump=True,
                    score=12.0,
                    reason="opening serve window",
                )
            )

        contact_extra = cfg.planner_teacher_contact_extra if self._teacher_assisted else 0.0
        low_time_extra = cfg.planner_teacher_low_time_extra if self._teacher_assisted else 0.0
        contact_window = cfg.contact_x_window + contact_extra
        target_x = _clip(
            features.predicted_intercept_x + self._planner_aim_offset(opp_x=opp_x, features=features),
            cfg.overcommit_guard_x,
            cfg.rear_guard_x,
        )
        near_contact = abs(ball_x - x) <= contact_window
        jumpable_height = cfg.jump_y_min <= ball_y <= cfg.jump_y_max + 0.25
        contact_jump = near_contact and jumpable_height and (ball_vy <= cfg.descending_vy or features.convergence_rate > 0.02)

        if features.wall_bounce_imminent or ball_x >= cfg.rear_wall_press_x - 0.05:
            proposals.append(
                SlimeVolleyModeProposal(
                    mode="planner_rear_wall",
                    target_x=features.predicted_intercept_x,
                    jump=contact_jump and agent_y <= ball_y + cfg.rear_wall_press_jump_margin,
                    score=9.0,
                    reason="one-wall-bounce intercept",
                )
            )

        if features.time_to_floor <= cfg.planner_low_time_threshold + low_time_extra:
            grounded_late = (
                ball_y <= cfg.grounded_low_receive_y
                and ball_vy < cfg.grounded_low_receive_vy
                and agent_y > ball_y + cfg.grounded_low_receive_airborne_margin
            )
            low_contact_window = max(contact_window, cfg.low_ball_rescue_x_window)
            proposals.append(
                SlimeVolleyModeProposal(
                    mode="planner_floor_intercept",
                    target_x=target_x,
                    jump=False if grounded_late else abs(ball_x - x) <= low_contact_window and ball_y >= cfg.jump_y_min,
                    score=8.5,
                    reason="low time-to-floor intercept",
                )
            )

        net_margin = cfg.planner_teacher_net_margin if self._teacher_assisted else 0.0
        if (
            features.net_clearance is not None
            and features.net_clearance < net_margin
            and -0.18 <= ball_x <= 0.62
            and ball_vy <= 0.05
        ):
            proposals.append(
                SlimeVolleyModeProposal(
                    mode="planner_net_clearance_guard",
                    target_x=max(target_x, cfg.planner_front_net_guard_x),
                    jump=abs(ball_x - x) <= max(contact_window, cfg.low_ball_rescue_x_window) and ball_y >= cfg.planner_front_net_guard_y,
                    score=8.0,
                    reason="predicted return is too low at the net",
                )
            )

        if features.ball_returning:
            proposals.append(
                SlimeVolleyModeProposal(
                    mode="planner_intercept",
                    target_x=target_x,
                    jump=contact_jump,
                    score=5.5,
                    reason="ball returning to agent side",
                )
            )
        else:
            recover_x = cfg.defensive_home_x if opp_x < 0.8 else cfg.home_x
            if features.opponent_committed_direction > 0:
                recover_x = min(cfg.rear_guard_x, recover_x + 0.10)
            proposals.append(
                SlimeVolleyModeProposal(
                    mode="planner_recover",
                    target_x=recover_x,
                    jump=False,
                    score=3.0,
                    reason="ball not currently returning",
                )
            )
        return proposals

    def _planner_aim_offset(self, *, opp_x: float, features: SlimeVolleyPlannerFeatures) -> float:
        if not features.ball_returning:
            return 0.0
        cfg = self._config
        offset = cfg.planner_aim_offset
        if self._teacher_assisted:
            offset += cfg.planner_teacher_contact_extra * 0.5
        if opp_x > -0.85:
            return offset
        if opp_x < -1.35:
            return -offset * 0.5
        if features.opponent_committed_direction > 0:
            return -offset * 0.25
        if features.opponent_committed_direction < 0:
            return offset * 0.25
        return 0.0

    def _choose_planner_proposal(self, proposals: list[SlimeVolleyModeProposal]) -> SlimeVolleyModeProposal:
        chosen = max(proposals, key=lambda proposal: proposal.score)
        if self._steps - self._last_mode_step <= self._config.planner_mode_dwell_steps:
            previous = [proposal for proposal in proposals if proposal.mode == self._phase]
            if previous and previous[0].score >= chosen.score - 0.35:
                return previous[0]
        return chosen

    def _structural_safety_action(
        self,
        *,
        base_action: np.ndarray,
        planner_action: np.ndarray,
        ball_x: float,
        ball_y: float,
        ball_vy: float,
        features: SlimeVolleyPlannerFeatures,
    ) -> np.ndarray | None:
        cfg = self._config
        urgent_low_or_wall = (
            features.time_to_floor <= cfg.planner_low_time_threshold + cfg.planner_teacher_low_time_extra
            or features.wall_bounce_imminent
            or (ball_x >= cfg.rear_wall_press_x and ball_y <= cfg.rear_wall_press_y)
        )
        low_ball = ball_x > 0.0 and ball_y <= cfg.low_ball_rescue_y and ball_vy < cfg.low_ball_rescue_vy
        if (urgent_low_or_wall or low_ball) and base_action[2] > planner_action[2]:
            return base_action.copy()
        return None

    def _planner_action(
        self,
        *,
        x: float,
        proposal: SlimeVolleyModeProposal,
        features: SlimeVolleyPlannerFeatures,
    ) -> np.ndarray:
        cfg = self._config
        action = _move_toward(x, proposal.target_x, cfg.x_margin)
        jump = proposal.jump
        emergency = proposal.mode in {"planner_floor_intercept", "planner_rear_wall"} and (
            features.time_to_floor <= cfg.planner_low_time_threshold + cfg.planner_teacher_low_time_extra
        )
        if jump and not emergency and self._steps - self._last_jump_step <= cfg.planner_jump_cooldown_steps:
            jump = False
        return _with_jump(action, jump)

    def _diagnostics_payload(
        self,
        features: SlimeVolleyPlannerFeatures,
        proposal: SlimeVolleyModeProposal,
        action: np.ndarray,
    ) -> dict[str, Any]:
        return {
            "mode": proposal.mode,
            "reason": proposal.reason,
            "target_x": proposal.target_x,
            "score": proposal.score,
            "action": _action_key_for_policy(action),
            "teacher_assisted": self._teacher_assisted,
            "planner": {
                "frames": features.frames,
                "stacked_ball_vx": features.stacked_ball_vx,
                "stacked_ball_vy": features.stacked_ball_vy,
                "stacked_opponent_vx": features.stacked_opponent_vx,
                "opponent_committed_direction": features.opponent_committed_direction,
                "time_to_floor": features.time_to_floor,
                "time_to_net_cross": features.time_to_net_cross,
                "predicted_intercept_x": features.predicted_intercept_x,
                "predicted_net_y": features.predicted_net_y,
                "net_clearance": features.net_clearance,
                "wall_bounce_imminent": features.wall_bounce_imminent,
                "recent_jump_count": features.recent_jump_count,
                "convergence_rate": features.convergence_rate,
                "ball_returning": features.ball_returning,
            },
        }

    def config(self) -> dict[str, Any]:
        values = asdict(self._config)
        values["policy_type"] = "slimevolley_teacher_assisted_planner" if self._teacher_assisted else "slimevolley_planner"
        values["teacher_assisted"] = self._teacher_assisted
        values["teacher_source"] = (
            "baseline-rnn development traces may be used for rule discovery; the runtime policy is hand-coded."
            if self._teacher_assisted else None
        )
        values["history_features"] = [
            "time_to_floor",
            "time_to_net_cross",
            "net_clearance",
            "one_wall_bounce_intercept",
            "stacked_ball_velocity",
            "stacked_opponent_commitment",
            "recent_jump_count",
            "convergence_rate",
        ]
        values["structural_modes"] = [
            "planner_serve",
            "planner_rear_wall",
            "planner_floor_intercept",
            "planner_net_clearance_guard",
            "planner_structural_safety",
            "planner_intercept",
            "planner_recover",
        ]
        values["archive_note"] = "Generation-4 hybrid candidate; evaluate on development seeds before any holdout use."
        return values


class SlimeVolleyTeacherAssistedPolicy(SlimeVolleyPlannerPolicy):
    """Transparent planner variant reserved for RNN-teacher-derived rules.

    The policy stores the teacher-assisted label and slightly wider contact/net
    margins that should be justified by dev-seed teacher traces before promotion.
    It remains a handwritten controller and never queries the teacher at runtime.
    """

    policy_name = "slimevolley_teacher_assisted_planner"

    def __init__(self, config: SlimeVolleyConfig | None = None) -> None:
        super().__init__(config, teacher_assisted=True)


class SlimeVolleyBuiltInRnnPolicy(BasePolicy):
    """Wrapper for slimevolleygym's shipped 120-parameter RNN baseline."""

    policy_name = "slimevolley_builtin_rnn"

    def __init__(self) -> None:
        try:
            from slimevolleygym.slimevolley import BaselinePolicy
        except Exception as exc:  # pragma: no cover - depends on optional package
            raise RuntimeError(
                "SlimeVolley baseline-rnn requires optional slimevolleygym dependencies."
            ) from exc
        self._policy = BaselinePolicy()

    def reset(self, seed: int | None = None) -> None:
        del seed
        self._policy.reset()

    def act(self, obs: Any) -> np.ndarray:
        return np.asarray(self._policy.predict(obs), dtype=np.int8)

    def config(self) -> dict[str, Any]:
        return {
            "policy_type": "slimevolley_builtin_rnn",
            "baseline_type": "pretrained neural/RNN comparator",
            "parameter_count": 120,
            "source": "slimevolleygym.slimevolley.BaselinePolicy",
        }


class SlimeVolleyRandomPolicy(BasePolicy):
    """Deterministic-seed random MultiBinary(3) SlimeVolley baseline."""

    policy_name = "slimevolley_random"

    def __init__(self) -> None:
        self._rng = np.random.default_rng(0)

    def reset(self, seed: int | None = None) -> None:
        self._rng = np.random.default_rng(seed)

    def act(self, obs: Any) -> np.ndarray:
        del obs
        return self._rng.integers(0, 2, size=3, dtype=np.int8)

    def config(self) -> dict[str, Any]:
        return {"policy_type": "slimevolley_random"}


def candidate_configs(*, max_candidates: int = 32) -> list[dict[str, Any]]:
    """Return scalar-only SlimeVolley configs for the search baseline."""

    candidates: list[dict[str, Any]] = []
    for home_x, contact_x_window, landing_horizon in itertools.product(
        [1.05, 1.20, 1.35],
        [0.18, 0.22, 0.28],
        [0.30, 0.38, 0.48],
    ):
        candidates.append(
            {
                "home_x": home_x,
                "contact_x_window": contact_x_window,
                "landing_horizon": landing_horizon,
            }
        )
    return candidates[:max_candidates]


SUPPORTED_POLICY_NAMES = (
    "initial",
    "improved",
    "tuned",
    "improved-tuned",
    "attack",
    "rally-serve",
    "rally-serve-low-x52",
    "post-contact",
    "net-pressure",
    "baseline-rnn",
    "improved-v0",
    "improved-v1",
    "improved-v2",
    "improved-v3",
    "improved-v4",
    "improved-v5",
    "improved-v6",
    "temporal",
    "planner",
    "teacher-assisted",
)


def make_policy(
    policy_name: str,
    *,
    config: dict[str, Any] | None = None,
) -> BasePolicy:
    """Build a SlimeVolley policy from this environment-local policy registry."""

    if policy_name not in SUPPORTED_POLICY_NAMES:
        raise ValueError(f"unsupported slimevolley policy {policy_name!r}")
    if policy_name == "baseline-rnn":
        return SlimeVolleyBuiltInRnnPolicy()
    if policy_name == "improved-tuned":
        tuned_config = config_from_dict(SlimeVolleyConfig, config) if config is not None else None
        return SlimeVolleyImprovedTunedPolicy(tuned_config)
    if policy_name == "attack":
        attack_config = config_from_dict(SlimeVolleyConfig, config) if config is not None else None
        return SlimeVolleyAttackPolicy(attack_config)
    if policy_name == "rally-serve":
        rally_config = config_from_dict(SlimeVolleyConfig, config) if config is not None else None
        return SlimeVolleyRallyServePolicy(rally_config)
    if policy_name == "rally-serve-low-x52":
        low_x52_config = config_from_dict(SlimeVolleyConfig, config) if config is not None else None
        return SlimeVolleyRallyServeLowX52Policy(low_x52_config)
    if policy_name == "post-contact":
        post_contact_config = config_from_dict(SlimeVolleyConfig, config) if config is not None else None
        return SlimeVolleyPostContactPolicy(post_contact_config)
    if policy_name == "net-pressure":
        pressure_config = config_from_dict(SlimeVolleyConfig, config) if config is not None else None
        return SlimeVolleyNetPressurePolicy(pressure_config)
    if policy_name == "improved-v0":
        return SlimeVolleyImprovedV0Policy()
    if policy_name == "improved-v1":
        return SlimeVolleyImprovedV1Policy()
    if policy_name == "improved-v2":
        return SlimeVolleyImprovedV2Policy()
    if policy_name == "improved-v3":
        return SlimeVolleyImprovedV3Policy()
    if policy_name == "improved-v4":
        return SlimeVolleyImprovedV4Policy()
    if policy_name == "improved-v5":
        return SlimeVolleyImprovedV5Policy()
    if policy_name == "improved-v6":
        return SlimeVolleyImprovedV6Policy()
    if policy_name == "temporal":
        return SlimeVolleyTemporalPolicy(config_from_dict(SlimeVolleyConfig, config))
    if policy_name == "planner":
        return SlimeVolleyPlannerPolicy(config_from_dict(SlimeVolleyConfig, config))
    if policy_name == "teacher-assisted":
        return SlimeVolleyTeacherAssistedPolicy(config_from_dict(SlimeVolleyConfig, config))
    return SlimeVolleyHeuristicPolicy(
        config_from_dict(SlimeVolleyConfig, config),
        structural=policy_name == "improved",
    )

"""Transparent handwritten policies used by the benchmark."""

from __future__ import annotations

from .acrobot import AcrobotConfig, AcrobotDecisionTreePolicy, AcrobotPolicy
from .base import BasePolicy, RandomPolicy
from .bipedal_walker import BipedalWalkerConfig, BipedalWalkerPolicy
from .cartpole import CartPoleConfig, CartPolePolicy
from .factory import make_policy
from .lunar_lander import LunarLanderConfig, LunarLanderPolicy
from .mountain_car import MountainCarConfig, MountainCarPolicy
from .slimevolley import (
    SlimeVolleyBuiltInRnnPolicy,
    SlimeVolleyConfig,
    SlimeVolleyHeuristicPolicy,
    SlimeVolleyImprovedV0Policy,
    SlimeVolleyImprovedV1Policy,
    SlimeVolleyImprovedV2Policy,
    SlimeVolleyRallyServePolicy,
    SlimeVolleyRallyServeLowX52Policy,
    SlimeVolleyPostContactPolicy,
    SlimeVolleyRandomPolicy,
)

__all__ = [
    "AcrobotConfig",
    "AcrobotDecisionTreePolicy",
    "AcrobotPolicy",
    "BasePolicy",
    "BipedalWalkerConfig",
    "BipedalWalkerPolicy",
    "CartPoleConfig",
    "CartPolePolicy",
    "LunarLanderConfig",
    "LunarLanderPolicy",
    "MountainCarConfig",
    "MountainCarPolicy",
    "RandomPolicy",
    "SlimeVolleyBuiltInRnnPolicy",
    "SlimeVolleyConfig",
    "SlimeVolleyHeuristicPolicy",
    "SlimeVolleyImprovedV0Policy",
    "SlimeVolleyImprovedV1Policy",
    "SlimeVolleyImprovedV2Policy",
    "SlimeVolleyRallyServePolicy",
    "SlimeVolleyRallyServeLowX52Policy",
    "SlimeVolleyPostContactPolicy",
    "SlimeVolleyRandomPolicy",
    "make_policy",
]

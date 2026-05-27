"""Registry-facing custom-env bridge for the SlimeVolley harness.

The full implementation remains in :mod:`hl_benchmark.slimevolley` so existing
scripts, tests, and reports keep working. This package makes SlimeVolley the
first concrete harness under the preferred ``hl_benchmark.custom_envs`` layout.
"""

from __future__ import annotations

from hl_benchmark.slimevolley import CUSTOM_VERIFY_EXTRA_COMMANDS

__all__ = ("CUSTOM_VERIFY_EXTRA_COMMANDS",)

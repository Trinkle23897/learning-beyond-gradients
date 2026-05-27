"""Optional SlimeVolley experiment support."""

from .adapter import SlimeVolleyEpisodeResult, check_slimevolley_available, run_slimevolley_episode
from .opponents import OPPONENT_POOL, make_slimevolley_opponent

CUSTOM_VERIFY_EXTRA_COMMANDS = (
    ("contact-diagnostics", ()),
    ("generation-report", ("--generation", "3")),
    ("protocol", ()),
    ("protocol", ("--generation", "3")),
    ("protocol", ("--generation", "4")),
)

__all__ = [
    "CUSTOM_VERIFY_EXTRA_COMMANDS",
    "OPPONENT_POOL",
    "SlimeVolleyEpisodeResult",
    "check_slimevolley_available",
    "make_slimevolley_opponent",
    "run_slimevolley_episode",
]

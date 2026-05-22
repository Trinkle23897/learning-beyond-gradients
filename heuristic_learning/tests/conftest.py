from __future__ import annotations

import sys
from pathlib import Path


SUBPROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(SUBPROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(SUBPROJECT_ROOT))


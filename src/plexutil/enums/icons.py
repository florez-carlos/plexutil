from __future__ import annotations

import sys
from enum import Enum


class Icons(Enum):
    WARNING = (
        "⚠️ " if sys.stdout.encoding.lower().startswith("utf") else "[WARNING] "
    )

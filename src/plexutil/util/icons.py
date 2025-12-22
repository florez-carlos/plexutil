from __future__ import annotations

import sys

from plexutil.static import Static


class Icons(Static):
    WARNING = (
        "⚠️ " if sys.stdout.encoding.lower().startswith("utf") else "[WARNING] "
    )

from __future__ import annotations

import sys

from plexutil.static import Static


class Icons(Static):
    WARNING = (
        "⚠️ " if sys.stdout.encoding.lower().startswith("utf") else "[WARNING] "
    )
    BANNER_LEFT = (
        "══════════ "
        if sys.stdout.encoding.lower().startswith("utf")
        else "========== "
    )
    BANNER_RIGHT = (
        " ══════════"
        if sys.stdout.encoding.lower().startswith("utf")
        else " =========="
    )
    CHEVRON_RIGHT = (
        "► " if sys.stdout.encoding.lower().startswith("utf") else "> "
    )
    STAR = "●" if sys.stdout.encoding.lower().startswith("utf") else "*"
    SUCCESS = (
        "🟢" if sys.stdout.encoding.lower().startswith("utf") else "SUCCESS"
    )
    FAILURE = "🔴" if sys.stdout.encoding.lower().startswith("utf") else "FAIL"
    PASS = (
        "🎟" if sys.stdout.encoding.lower().startswith("utf") else "*PlexPass*"
    )

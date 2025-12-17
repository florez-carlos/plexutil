from __future__ import annotations

from enum import Enum

from src.plexutil.plex_util_logger import PlexUtilLogger


# Evaluates file name/folder structure to identify media
# https://support.plex.tv/articles/200241548-scanners/
class Scanner(Enum):
    MUSIC = "Plex Music"
    TV = "Plex TV Series"
    MOVIE = "Plex Movie"
    MOVIE_VIDEO = "Plex Video Files Scanner"  # Most appropriate for Home Video
    MOVIE_LEGACY = "Plex Movie Scanner"
    TV_LEGACY = "Plex Series Scanner"

    @staticmethod
    def get_all() -> list[Scanner]:
        return list(Scanner)

    @staticmethod
    def get_from_str(candidate: str) -> Scanner:
        for scanner in Scanner.get_all():
            if candidate.lower() == scanner.value.lower():
                if (
                    scanner is Scanner.MOVIE_LEGACY
                    or scanner is Scanner.TV_LEGACY
                ):
                    description = (
                        f"WARNING: Chosen a deprecated Scanner "
                        f"({scanner.value})"
                    )
                    PlexUtilLogger.get_logger().warning(description)

                return scanner

        description = f"Scanner not supported: {candidate}"
        raise ValueError(description)

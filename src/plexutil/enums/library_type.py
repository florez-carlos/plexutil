from __future__ import annotations

from enum import Enum

from plexapi.library import (
    LibrarySection,
    MovieSection,
    MusicSection,
    ShowSection,
)


class LibraryType(Enum):
    MUSIC = "track"  # track 10
    TV = "show"
    MOVIE = "movie"
    MUSIC_PLAYLIST = "audio"

    @staticmethod
    def is_eq(
        library_type: LibraryType, library_section: LibrarySection
    ) -> bool:
        if (
            isinstance(library_section, MovieSection)
            and library_type is LibraryType.MOVIE
            or isinstance(library_section, MusicSection)
            and library_type is LibraryType.MUSIC
            or isinstance(library_section, ShowSection)
            and library_type is LibraryType.TV
        ):
            return True
        return False

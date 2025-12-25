from __future__ import annotations

from enum import Enum

from plexutil.enums.library_type import LibraryType
from plexutil.exception.library_unsupported_error import (
    LibraryUnsupportedError,
)


class LibraryName(Enum):
    MUSIC = "Music"
    TV = "TV Shows"
    MOVIE = "Movies"

    @staticmethod
    def get_default(library_type: LibraryType) -> LibraryName:
        match library_type:
            case LibraryType.MOVIE:
                return LibraryName.MOVIE
            case LibraryType.TV:
                return LibraryName.TV
            case LibraryType.MUSIC:
                return LibraryName.MUSIC

        op_type = "Get Default Library Name"
        raise LibraryUnsupportedError(op_type, library_type)

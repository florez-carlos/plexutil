from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class LibraryPreferencesDTO:
    music: Dict
    movie: Dict
    tv: Dict
    plex_server_settings: Dict


def __eq__(self, other):
    if not isinstance(other, LibraryPreferencesDTO):
        return NotImplemented

    return (
        self.music == other.music
        and self.movie == other.movie
        and self.tv == other.tv
        and self.plex_server_settings == other.plex_server_settings
    )


def __hash__(self):
    return hash((self.music, self.movie, self.tv, self.plex_server_settings))

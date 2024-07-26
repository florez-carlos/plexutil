from dataclasses import dataclass


@dataclass(frozen=True)
class LibraryPreferencesDTO:
    music: dict
    movie: dict
    tv: dict
    plex_server_settings: dict

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LibraryPreferencesDTO):
            return False

        return (
            self.music == other.music
            and self.movie == other.movie
            and self.tv == other.tv
            and self.plex_server_settings == other.plex_server_settings
        )

    def __hash__(self) -> int:
        return hash(
            (self.music, self.movie, self.tv, self.plex_server_settings)
        )

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LibraryPreferencesDTO:
    music: dict = field(default_factory=dict)
    movie: dict = field(default_factory=dict)
    tv: dict = field(default_factory=dict)
    plex_server_settings: dict = field(default_factory=dict)

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

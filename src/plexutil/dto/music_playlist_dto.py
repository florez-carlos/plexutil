from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plexutil.dto.song_dto import SongDTO


@dataclass(frozen=True)
class MusicPlaylistDTO:
    name: str = ""
    songs: list[SongDTO] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MusicPlaylistDTO):
            return False

        return self.name == other.name and self.songs == other.songs

    def __hash__(self) -> int:
        return hash((self.name, self.songs))

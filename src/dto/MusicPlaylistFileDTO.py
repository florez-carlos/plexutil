from dataclasses import dataclass, field
from typing import List

from src.dto.MusicPlaylistDTO import MusicPlaylistDTO
from src.serializer.Serializable import Serializable


@dataclass(frozen=True)
class MusicPlaylistFileDTO(Serializable):
    track_count: int = 0
    playlists: List[MusicPlaylistDTO] = field(default_factory=list)

    def __eq__(self, other):
        if not isinstance(other, MusicPlaylistFileDTO):
            return NotImplemented

        return (
            self.track_count == other.track_count
            and self.playlists == other.playlists
        )

    def __hash__(self):
        return hash((self.track_count, self.playlists))

from dataclasses import dataclass, field
from typing import List
from src.serializer.Serializable import Serializable
from src.dto.MusicPlaylistDTO import MusicPlaylistDTO


@dataclass(frozen=True)
class MusicPlaylistFileDTO(Serializable):
    track_count: int = 0
    playlists: List[MusicPlaylistDTO] = field(default_factory=lambda: [])


def __eq__(self, other):
    if not isinstance(other, MusicPlaylistFileDTO):
        return NotImplemented

    return (
        self.track_count == other.track_count
        and self.playlists == other.playlists
    )


def __hash__(self):
    return hash((self.location, self.track_count, self.playlists))

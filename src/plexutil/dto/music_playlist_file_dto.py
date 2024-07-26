from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plexutil.dto.music_playlist_dto import MusicPlaylistDTO

from plexutil.serializer.serializable import Serializable


@dataclass(frozen=True)
class MusicPlaylistFileDTO(Serializable):
    track_count: int = 0
    playlists: list[MusicPlaylistDTO] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MusicPlaylistFileDTO):
            return False

        return (
            self.track_count == other.track_count
            and self.playlists == other.playlists
        )

    def __hash__(self) -> int:
        return hash((self.track_count, self.playlists))

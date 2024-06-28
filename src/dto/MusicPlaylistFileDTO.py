from dataclasses import dataclass, field
from pathlib import Path
from typing import List
from src.dto.MusicPlaylistDTO import MusicPlaylistDTO

@dataclass(frozen=True)
class MusicPlaylistFileDTO():

    location: Path = Path()
    track_count: int = 0
    playlists: List[MusicPlaylistDTO] = field(default_factory=lambda: [])


def __eq__(self, other):

    if not isinstance(other, MusicPlaylistFileDTO):
        return NotImplemented

    return self.location == other.location and self.track_count == other.track_count and self.playlists == other.playlists

def __hash__(self):
    return hash((self.location, self.track_count,self.playlists))




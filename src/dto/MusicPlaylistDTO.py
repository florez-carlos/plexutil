from dataclasses import dataclass, field
from typing import List
from src.dto.SongDTO import SongDTO

@dataclass(frozen=True)
class MusicPlaylistDTO():

    name: str = ""
    songs: List[SongDTO] = field(default_factory=lambda: [])

def __eq__(self, other):

    if not isinstance(other, MusicPlaylistDTO):
        return NotImplemented

    return self.name == other.name and self.songs == other.songs

def __hash__(self):
    return hash((self.name, self.songs))



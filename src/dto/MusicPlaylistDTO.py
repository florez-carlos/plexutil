from dataclasses import dataclass
from typing import List
from SongDTO import SongDTO

@dataclass(frozen=True)
class MusicPlaylistDTO():

    name: str = ""
    songs: List[SongDTO] = []

def __eq__(self, other):

    if not isinstance(other, MusicPlaylistDTO):
        return NotImplemented

    return self.name == other.name and self.songs == other.songs

def __hash__(self):
    return hash((self.name, self.songs))



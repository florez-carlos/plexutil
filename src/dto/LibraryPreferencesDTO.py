from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class LibraryPreferencesDTO():

    music: Dict
    movie: Dict
    tv: Dict

def __eq__(self, other):

    if not isinstance(other, LibraryPreferencesDTO):
        return NotImplemented

    return self.music == other.music and self.movie == other.movie and self.tv == other.tv 
    
def __hash__(self):
    return hash((self.prefs))

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class LibraryPreferencesDTO():

    prefs: Dict

def __eq__(self, other):

    if not isinstance(other, LibraryPreferencesDTO):
        return NotImplemented

    return self.prefs == other.prefs 
    
def __hash__(self):
    return hash((self.prefs))

from dataclasses import dataclass
from typing import List

from pathlib import Path
from enum.LibraryType import LibraryType

@dataclass(frozen=True)
class LibraryDTO():

    library_type: LibraryType
    library_location: Path
    library_name: str = ""

def __eq__(self, other):

    if not isinstance(other, LibraryDTO):
        return NotImplemented

    return self.library_type == other.library_type and self.library_location == other.library_location and self.library_name == other.library_name

def __hash__(self):
    return hash((self.library_type, self.library_location, self.library_name))

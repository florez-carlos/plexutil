from dataclasses import dataclass

from enum.FileType import FileType

@dataclass(frozen=True)
class SongDTO():

    name: str = ""
    extension: FileType = FileType.UNKNOWN 

def __eq__(self, other):

    if not isinstance(other, SongDTO):
        return NotImplemented

    return self.name == other.name and self.extension == other.extension

def __hash__(self):
    return hash((self.name, self.extension))

from dataclasses import dataclass

from plexutil.enums.file_type import FileType


# Frozen=True creates an implicit hash method, eq is created by default
@dataclass(frozen=True)
class SongDTO:
    name: str = ""
    extension: FileType = FileType.UNKNOWN

    def __str__(self) -> str:
        return self.name + "." + self.extension.value

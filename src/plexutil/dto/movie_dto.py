from dataclasses import dataclass

from plexutil.enums.file_type import FileType


# Frozen=True creates an implicit hash method, eq is created by default
@dataclass(frozen=True)
class MovieDTO:
    name: str = ""
    extension: FileType = FileType.UNKNOWN
    year: int = 0

    def __str__(self) -> str:
        return f"{self.name} ({self.year}) "

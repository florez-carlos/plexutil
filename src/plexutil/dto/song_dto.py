from dataclasses import dataclass

from plexutil.enums.file_type import FileType


@dataclass(frozen=True)
class SongDTO:
    name: str = ""
    extension: FileType = FileType.UNKNOWN

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SongDTO):
            return False

        return self.name == other.name and self.extension == other.extension

    def __hash__(self) -> int:
        return hash((self.name, self.extension))

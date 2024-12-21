from dataclasses import dataclass

from plexutil.enums.file_type import FileType


@dataclass(frozen=True)
class MovieDTO:
    name: str = ""
    extension: FileType = FileType.UNKNOWN
    year: int = 0

    def __str__(self) -> str:
        return f"{self.name} ({self.year}) "

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MovieDTO):
            return False

        return (
            self.name == other.name
            and self.extension == other.extension
            and self.year == other.year
        )

    def __hash__(self) -> int:
        return hash((self.name, self.extension, self.year))

from dataclasses import dataclass, field
from pathlib import Path


# Frozen=True creates an implicit hash method, eq is created by default
@dataclass(frozen=True)
class SongDTO:
    name: str = ""
    locations: list[Path] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.name}"

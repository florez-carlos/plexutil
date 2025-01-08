from dataclasses import dataclass
from pathlib import Path


# Frozen=True creates an implicit hash method, eq is created by default
@dataclass(frozen=True)
class TVSeriesDTO:
    name: str = ""
    year: int = 0
    location: Path = Path()

    def __str__(self) -> str:
        return f"{self.name} ({int(self.year)})"

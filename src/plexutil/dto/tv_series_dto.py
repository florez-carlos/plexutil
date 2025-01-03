from dataclasses import dataclass


# Frozen=True creates an implicit hash method, eq is created by default
@dataclass(frozen=True)
class TVSeriesDTO:
    name: str = ""
    year: int = 0

    def __str__(self) -> str:
        return f"{self.name} ({int(self.year)})"

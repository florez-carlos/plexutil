from dataclasses import dataclass


@dataclass(frozen=True)
class TVEpisodeDTO:
    name: str = ""
    first_aired_year: int = 0
    season: int = 0
    episode: int = 0

    def __str__(self) -> str:
        return (
            self.name + " "
            f"({self.first_aired_year}): "
            f"S{self.season:02}E{self.episode:02}"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TVEpisodeDTO):
            return False

        return (
            self.name == other.name
            and self.first_aired_year == other.first_aired_year
            and self.season == other.season
            and self.episode == other.episode
        )

    def __hash__(self) -> int:
        return hash(
            (self.name, self.first_aired_year, self.season, self.episode)
        )

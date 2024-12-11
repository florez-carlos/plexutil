from __future__ import annotations
from enum import Enum


class Scanner(Enum):
    MUSIC = "Plex Music"
    TV = "Plex TV Series"
    MOVIE = "Plex Movie"

    @staticmethod
    def get_all() -> list[Scanner]:
        return [Scanner.MUSIC, Scanner.TV, Scanner.MOVIE]

    @staticmethod
    def get_from_str(candidate: str) -> Scanner:


        for agent in Scanner.get_all():
            if candidate.lower() == agent.value:
                return agent

        description = f"Scanner not supported: {candidate}"
        raise ValueError(description)

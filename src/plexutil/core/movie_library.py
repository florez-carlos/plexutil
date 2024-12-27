from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from plexapi.server import PlexServer
    from plexapi.video import Video

    from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO

from plexutil.core.library import Library
from plexutil.enums.agent import Agent
from plexutil.enums.language import Language
from plexutil.enums.library_name import LibraryName
from plexutil.enums.library_type import LibraryType
from plexutil.enums.scanner import Scanner


class MovieLibrary(Library):
    def __init__(
        self,
        plex_server: PlexServer,
        locations: list[Path],
        preferences: LibraryPreferencesDTO,
        language: Language = Language.ENGLISH_US,
        name: str = LibraryName.MOVIE.value,
    ) -> None:
        super().__init__(
            plex_server,
            name,
            LibraryType.MOVIE,
            Agent.MOVIE,
            Scanner.MOVIE,
            locations,
            language,
            preferences,
        )

    def create(self) -> None:
        library = self.plex_server.library

        library.add(
            name=self.name,
            type=self.library_type.value,
            agent=self.agent.value,
            scanner=self.scanner.value,
            location=[str(x) for x in self.locations],  # pyright: ignore [reportArgumentType]
            language=self.language.value,
        )

        section = self.get_section()
        section.editAdvanced(**self.preferences.movie)

    def query(self) -> list[Video]:
        return self.get_section().searchMovies()

    def delete(self) -> None:
        return super().delete()

    def exists(self) -> bool:
        return super().exists()

from __future__ import annotations

from typing import TYPE_CHECKING

from plexapi.exceptions import NotFound

from plexutil.plex_util_logger import PlexUtilLogger

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

        for key, value in self.preferences.movie.items():
            try:
                section = self.get_section()
                section.editAdvanced(**{key: value})
            except NotFound:  # noqa: PERF203
                description = (
                    f"Preference not accepted by the server: {key}\n"
                    f"Skipping -> {key}:{value}\n"
                )
                PlexUtilLogger.get_logger().warning(description)
                continue

    def query(self) -> list[Video]:
        return self.get_section().searchMovies()

    def delete(self) -> None:
        return super().delete()

    def exists(self) -> bool:
        return super().exists()

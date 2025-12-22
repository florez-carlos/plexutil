from __future__ import annotations

from typing import TYPE_CHECKING, cast

from plexutil.dto.library_setting_dto import LibrarySettingDTO
from plexutil.enums.library_setting import LibrarySetting
from plexutil.exception.library_op_error import LibraryOpError
from plexutil.plex_util_logger import PlexUtilLogger

if TYPE_CHECKING:
    from pathlib import Path

    from plexapi.server import PlexServer
    from plexapi.video import Movie


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
        language: Language = Language.get_default(),  # noqa: B008
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
        )

    def create(self) -> None:
        """
        Creates a Movie Library
        Logs a warning if a specific movie preference is rejected by the server
        Logs a warning if no Movie Preferences available

        Returns:
            None: This method does not return a value

        Raises:
            LibraryOpError: If Library already exists
        """
        op_type = "CREATE"

        self.log_library(operation=op_type, is_info=False, is_debug=True)

        if self.exists():
            description = f"Movie Library '{self.name}' already exists"
            raise LibraryOpError(
                op_type=op_type,
                library_type=LibraryType.MOVIE,
                description=description,
            )

        self.plex_server.library.add(
            name=self.name,
            type=self.library_type.get_value(),
            agent=self.agent.get_value(),
            scanner=self.scanner.get_value(),
            location=[str(x) for x in self.locations],  # pyright: ignore [reportArgumentType]
            language=self.language.get_value(),
        )

        description = f"Successfully created: {self.name}"
        PlexUtilLogger.get_logger().debug(description)

        settings = LibrarySetting.get_all(LibraryType.MOVIE)

        library_settings = []

        for setting in settings:
            library_settings.append(  # noqa: PERF401
                LibrarySettingDTO(
                    name=setting.get_name(),
                    display_name=setting.get_display_name(),
                    description=setting.get_description(),
                    user_response=setting.get_default_selection(),
                    is_toggle=setting.is_toggle(),
                    is_value=setting.is_value(),
                    is_dropdown=setting.is_dropdown(),
                    dropdown=setting.get_dropdown(),
                    is_from_server=False,
                )
            )

        self.set_settings(settings=library_settings)
        self.get_section().refresh()

    def query(self) -> list[Movie]:
        """
        Returns all movies for the current LibrarySection

        Returns:
            list[plexapi.video.Movie]: Movies from the current Section
        """
        op_type = "QUERY"
        if not self.exists():
            description = f"Movie Library '{self.name}' does not exist"
            raise LibraryOpError(
                op_type=op_type,
                library_type=LibraryType.MOVIE,
                description=description,
            )
        return cast("list[Movie]", self.get_section().searchMovies())

    def delete(self) -> None:
        return super().delete()

    def exists(self) -> bool:
        return super().exists()

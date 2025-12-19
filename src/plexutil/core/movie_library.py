from __future__ import annotations

from typing import TYPE_CHECKING, cast

from plexutil.core.prompt import Prompt
from plexutil.dto.library_setting_dropdown_item_dto import (
    LibrarySettingDropdownItemDTO,
)
from plexutil.dto.library_setting_dto import LibrarySettingDTO
from plexutil.exception.library_op_error import LibraryOpError
from plexutil.plex_util_logger import PlexUtilLogger

if TYPE_CHECKING:
    from pathlib import Path

    from plexapi.server import PlexServer
    from plexapi.video import Movie

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
            type=self.library_type.value,
            agent=self.agent.value,
            scanner=self.scanner.value,
            location=[str(x) for x in self.locations],  # pyright: ignore [reportArgumentType]
            language=self.language.value,
        )

        description = f"Successfully created: {self.name}"
        PlexUtilLogger.get_logger().debug(description)

        tuples = []

        name = "enableCinemaTrailers"
        display_name = "Enable Cinema Trailers"
        description = (
            f"(Play Trailers automatically prior to the selected movie)\n"
            f"{Prompt.WARNING} Also needs to be enabled in the client app\n"
        )
        user_response = 0
        tuples.append(
            (
                name,
                display_name,
                description,
                user_response,
                True,
                False,
                False,
            )
        )

        name = "originalTitles"
        display_name = "Original Titles"
        description = (
            "Use the original titles for all items "
            "regardless of the library language\n"
        )
        user_response = 1
        tuples.append(
            (
                name,
                display_name,
                description,
                user_response,
                True,
                False,
                False,
            )
        )

        name = "localizedArtwork"
        display_name = "Prefer artwork based on library language"
        description = "Use localized posters when available\n"
        user_response = 1
        tuples.append(
            (
                name,
                display_name,
                description,
                user_response,
                True,
                False,
                False,
            )
        )

        name = "useLocalAssets"
        display_name = "Use local assets"
        description = (
            "When scanning this library, "
            "use local posters and artwork if present\n"
        )
        user_response = 1
        tuples.append(
            (
                name,
                display_name,
                description,
                user_response,
                True,
                False,
                False,
            )
        )

        name = "respectTags"
        display_name = "Prefer local metadata"
        description = (
            "When scanning this library, prefer "
            "embedded tags and local files if present."
        )
        user_response = 0
        tuples.append(
            (
                name,
                display_name,
                description,
                user_response,
                True,
                False,
                False,
            )
        )

        name = "enableBIFGeneration"
        display_name = "Enable video preview thumbnails"
        description = (
            "Generate video preview thumbnails for items in this library "
            "when enabled in server settings"
        )
        user_response = 1
        tuples.append(
            (
                name,
                display_name,
                description,
                user_response,
                True,
                False,
                False,
            )
        )

        name = "ratingsSource"
        display_name = "Ratings Source"
        description = "Select a primary source for ratings."
        user_response = 0
        dropdown = [
            LibrarySettingDropdownItemDTO(
                display_name="Rotten Tomatoes", value="rottentomatoes"
            ),
            LibrarySettingDropdownItemDTO(display_name="IMDb", value="imdb"),
            LibrarySettingDropdownItemDTO(
                display_name="The Movie Database", value="themoviedb"
            ),
        ]
        tuples.append(
            (
                name,
                display_name,
                description,
                user_response,
                False,
                False,
                True,
                dropdown,
            )
        )

        library_settings = []

        for a_tuple in tuples:
            library_settings.append( # noqa: PERF401
                LibrarySettingDTO(
                    name=a_tuple[0],
                    display_name=a_tuple[1],
                    description=a_tuple[2],
                    user_response=a_tuple[3],
                    is_toggle=a_tuple[4],
                    is_value=a_tuple[5],
                    is_dropdown=a_tuple[6],
                    dropdown=a_tuple[7],
                )
            )

        self.set_settings(settings=library_settings)

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

from pathlib import Path

from plexapi.server import PlexServer

from plexutil.core.library import Library
from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO
from plexutil.enums.agent import Agent
from plexutil.enums.language import Language
from plexutil.enums.library_name import LibraryName
from plexutil.enums.library_type import LibraryType
from plexutil.enums.scanner import Scanner
from plexutil.plex_util_logger import PlexUtilLogger


class MovieLibrary(Library):
    def __init__(
        self,
        plex_server: PlexServer,
        location: Path,
        language: Language,
        preferences: LibraryPreferencesDTO,
    ) -> None:
        super().__init__(
            plex_server,
            LibraryName.MOVIE,
            LibraryType.MOVIE,
            Agent.MOVIE,
            Scanner.MOVIE,
            location,
            language,
            preferences,
        )

    def create(self) -> None:
        info = (
            "Creating movie library: \n"
            f"Name: {self.name.value}\n"
            f"Type: {self.library_type.value}\n"
            f"Agent: {self.agent.value}\n"
            f"Scanner: {self.scanner.value}\n"
            f"Location: {self.location!s}\n"
            f"Language: {self.language.value}\n"
            f"Preferences: {self.preferences.movie}\n"
        )

        PlexUtilLogger.get_logger().info(info)

        self.plex_server.library.add(
            name=self.name.value,
            type=self.library_type.value,
            agent=self.agent.value,
            scanner=self.scanner.value,
            location=str(self.location),
            language=self.language.value,
        )

        # This line triggers a refresh of the library
        self.plex_server.library.sections()

        self.plex_server.library.section(self.name.value).editAdvanced(
            **self.preferences.movie,
        )

    def delete(self) -> None:
        return super().delete()

    def exists(self) -> bool:
        return super().exists()

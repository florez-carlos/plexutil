from pathlib import Path

from plexapi.server import PlexServer
from throws import throws

from src.core.Library import Library
from src.dto.LibraryPreferencesDTO import LibraryPreferencesDTO
from src.enum.Agent import Agent
from src.enum.Language import Language
from src.enum.LibraryName import LibraryName
from src.enum.LibraryType import LibraryType
from src.enum.Scanner import Scanner
from src.exception.LibraryOpException import LibraryOpException


class MovieLibrary(Library):
    def __init__(
        self,
        plex_server: PlexServer,
        location: Path,
        language: Language,
        preferences: LibraryPreferencesDTO,
    ):
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

    @throws(LibraryOpException)
    def create(self) -> None:
        try:
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

        except LibraryOpException as e:
            raise e
        except Exception as e:
            raise LibraryOpException("CREATE", original_exception=e)

    @throws(LibraryOpException)
    def delete(self) -> None:
        return super().delete()

    @throws(LibraryOpException)
    def exists(self) -> bool:
        return super().exists()

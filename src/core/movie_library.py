from pathlib import Path

from plexapi.server import PlexServer
from throws import throws

from src.core.library import Library
from src.dto.library_preferences_dto import LibraryPreferencesDTO
from src.enum.agent import Agent
from src.enum.language import Language
from src.enum.library_name import LibraryName
from src.enum.library_type import LibraryType
from src.enum.scanner import Scanner
from src.exception.library_op_error import LibraryOpError


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

    @throws(LibraryOpError)
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

        except LibraryOpError as e:
            raise e
        except Exception as e:
            raise LibraryOpError("CREATE", original_exception=e)

    @throws(LibraryOpError)
    def delete(self) -> None:
        return super().delete()

    @throws(LibraryOpError)
    def exists(self) -> bool:
        return super().exists()

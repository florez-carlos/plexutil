from pathlib import Path

from plexapi.server import PlexServer
from throws import throws

from src.core.Library import Library
from src.dto.LibraryPreferencesDTO import LibraryPreferencesDTO
from src.dto.TVLanguageManifestFileDTO import TVLanguageManifestFileDTO
from src.enum.Agent import Agent
from src.enum.Language import Language
from src.enum.LibraryName import LibraryName
from src.enum.LibraryType import LibraryType
from src.enum.Scanner import Scanner
from src.exception.LibraryOpException import LibraryOpException


class TVLibrary(Library):
    def __init__(
        self,
        plex_server: PlexServer,
        location: Path,
        language: Language,
        preferences: LibraryPreferencesDTO,
        tv_language_manifest_file_dto: TVLanguageManifestFileDTO,
    ):
        super().__init__(
            plex_server,
            LibraryName.TV,
            LibraryType.TV,
            Agent.TV,
            Scanner.TV,
            location,
            language,
            preferences,
        )
        self.tv_language_manifest_file_dto = tv_language_manifest_file_dto

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
                **self.preferences.tv,
            )

            manifests_dto = self.tv_language_manifest_file_dto.manifests_dto

            for manifest_dto in manifests_dto:
                language = manifest_dto.language
                ids = manifest_dto.ids

                print("\n")
                print(
                    "Checking server tv "
                    + language.value
                    + " language meets expected count: "
                    + str(len(ids)),
                )
                self.poll(100, len(ids), 10, ids)

                shows = []

                for show in shows:
                    show.editAdvanced(languageOverride=language.value)

                self.plex_server.library.section(self.name.value).refresh()

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

from pathlib import Path

from plexapi.server import PlexServer

from plexutil.core.library import Library
from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO
from plexutil.dto.tv_language_manifest_file_dto import TVLanguageManifestFileDTO
from plexutil.enums.agent import Agent
from plexutil.enums.language import Language
from plexutil.enums.library_name import LibraryName
from plexutil.enums.library_type import LibraryType
from plexutil.enums.scanner import Scanner
from plexutil.plex_util_logger import PlexUtilLogger


class TVLibrary(Library):
    def __init__(
        self,
        plex_server: PlexServer,
        location: Path,
        language: Language,
        preferences: LibraryPreferencesDTO,
        tv_language_manifest_file_dto: TVLanguageManifestFileDTO,
    ) -> None:
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

    def create(self) -> None:
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

        info = (
            "Creating tv library: \n"
            f"Name: {self.name.value}\n"
            f"Type: {self.library_type.value}\n"
            f"Agent: {self.agent.value}\n"
            f"Scanner: {self.scanner.value}\n"
            f"Location: {self.location!s}\n"
            f"Language: {self.language.value}\n"
            f"Preferences: {self.preferences.tv}\n"
            f"Manifests: {manifests_dto}\n"
        )

        PlexUtilLogger.get_logger().info(info)

        for manifest_dto in manifests_dto:
            language = manifest_dto.language
            ids = manifest_dto.ids

            info = (
                f"Checking server tv {language.value} language meets "
                f"expected count {len(ids)!s}\n"
            )
            PlexUtilLogger.get_logger().info(info)
            self.poll(100, len(ids), 10, ids)

            shows = []

            for show in shows:
                show.editAdvanced(languageOverride=language.value)

            self.plex_server.library.section(self.name.value).refresh()

    def delete(self) -> None:
        return super().delete()

    def exists(self) -> bool:
        return super().exists()

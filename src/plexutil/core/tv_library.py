from pathlib import Path

from plexapi.server import PlexServer

from plexutil.core.library import Library
from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO
from plexutil.dto.tv_language_manifest_file_dto import (
    TVLanguageManifestFileDTO,
)
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
        locations: list[Path],
        preferences: LibraryPreferencesDTO,
        tv_language_manifest_file_dto: TVLanguageManifestFileDTO,
        name: str = LibraryName.TV.value,
        language: Language = Language.ENGLISH_US,
    ) -> None:
        super().__init__(
            plex_server,
            name,
            LibraryType.TV,
            Agent.TV,
            Scanner.TV,
            locations,
            language,
            preferences,
        )
        self.tv_language_manifest_file_dto = tv_language_manifest_file_dto

    def create(self) -> None:

        super().create()

        manifests_dto = self.tv_language_manifest_file_dto.manifests_dto

        info = (f"Manifests: {manifests_dto}\n")

        PlexUtilLogger.get_logger().info(info)
        PlexUtilLogger.get_logger().debug(info)

        self.plex_server.library.add(
            name=self.name,
            type=self.library_type.value,
            agent=self.agent.value,
            scanner=self.scanner.value,
            location=self.locations, #pyright: ignore
            language=self.language.value,
        )

        # This line triggers a refresh of the library
        self.plex_server.library.sections()

        self.plex_server.library.section(self.name).editAdvanced(
            **self.preferences.tv,
        )

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

            self.plex_server.library.section(self.name).refresh()

    def delete(self) -> None:
        return super().delete()

    def exists(self) -> bool:
        return super().exists()

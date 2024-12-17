from __future__ import annotations

from typing import TYPE_CHECKING

from plexapi.video import Video

from plexutil.exception.library_op_error import LibraryOpError

if TYPE_CHECKING:
    from pathlib import Path

    from plexapi.server import PlexServer

    from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO
    from plexutil.dto.tv_language_manifest_dto import TVLanguageManifestDTO

from plexutil.core.library import Library
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
        tvdb_ids: list[int],
        tv_language_manifest_dto: list[TVLanguageManifestDTO],
        agent: Agent = Agent.TV,
        scanner: Scanner = Scanner.TV,
        name: str = LibraryName.TV.value,
        language: Language = Language.ENGLISH_US,
    ) -> None:
        super().__init__(
            plex_server,
            name,
            LibraryType.TV,
            agent,
            scanner,
            locations,
            language,
            preferences,
        )
        self.tv_language_manifest_dto = tv_language_manifest_dto
        self.tvdb_ids = tvdb_ids

    def create(self) -> None:
        op_type = "CREATE"

        if self.exists():
            description = f"TV Library '{self.name}' already exists"
            raise LibraryOpError(
                op_type=op_type,
                library_type=LibraryType.TV,
                description=description,
            )

        self.__log_library(operation=op_type, is_info=False, is_debug=True)

        self.get_library().add(
            name=self.name,
            type=self.library_type.value,
            agent=self.agent.value,
            scanner=self.scanner.value,
            location=self.locations,  # pyright: ignore [reportArgumentType]
            language=self.language.value,
        )

        if self.preferences.tv:
            self.get_library().editAdvanced(**self.preferences.tv)

        manifests_dto = self.tv_language_manifest_dto
        debug = f"Manifests: {manifests_dto}\n"
        PlexUtilLogger.get_logger().debug(debug)

        self.probe_library()

        for manifest_dto in manifests_dto:
            language = manifest_dto.language
            ids = manifest_dto.ids
            if not ids:
                continue

            info = (
                f"Checking server tv {language.value} language meets "
                f"expected count {len(ids)!s}\n"
            )
            PlexUtilLogger.get_logger().info(info)

            for show in self.get_filtered_shows():
                show.editAdvanced(languageOverride=language.value)

    def query(self) -> list[Video]:
        if self.tvdb_ids:
            return self.get_filtered_shows()
        else:
            return self.get_shows()

    def get_shows(self) -> list[Video]:
        library = self.get_library()
        shows = library.all()
        return shows

    def get_filtered_shows(self) -> list[Video]:
        shows = self.get_shows()

        tvdb_prefix = "tvdb://"

        if not self.tvdb_ids:
            return []

        id_shows = {}
        shows_filtered = []

        for show in shows:
            for guid in show.guids:
                id = guid.id
                if tvdb_prefix in id:
                    tvdb = id.replace(tvdb_prefix, "")
                    id_shows[int(tvdb)] = show

        for tvdb_id in self.tvdb_ids:
            if tvdb_id in id_shows:
                shows_filtered.append(id_shows[tvdb_id])
            else:
                description = f"No show in server matches the supplied TVDB ID: {tvdb_id!s}"
                PlexUtilLogger.get_logger().debug(description)

        return shows_filtered

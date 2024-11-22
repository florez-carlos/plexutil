from pathlib import Path
from typing import List

from plexapi.library import MusicSection
from plexapi.server import PlexServer

from plexutil.core.library import Library
from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO
from plexutil.enums.agent import Agent
from plexutil.enums.language import Language
from plexutil.enums.library_name import LibraryName
from plexutil.enums.library_type import LibraryType
from plexutil.enums.scanner import Scanner
from plexutil.exception.library_op_error import LibraryOpError
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.util.path_ops import PathOps
from plexutil.util.query_builder import QueryBuilder


class MusicLibrary(Library):
    def __init__(
        self,
        plex_server: PlexServer,
        locations: list[Path],
        preferences: LibraryPreferencesDTO,
        name: str = LibraryName.MUSIC.value,
        language: Language = Language.ENGLISH_US,
    ) -> None:
        section = plex_server.library.section(name)
        plex_locations = []        
        if isinstance(section, MusicSection):
            plex_locations = section.locations
        super().__init__(
            plex_server,
            name,
            LibraryType.MUSIC,
            Agent.MUSIC,
            Scanner.MUSIC,
            plex_locations or locations,
            language,
            preferences,
        )

    def create(self) -> None:

        super().create()
            
        part = ""

        query_builder = QueryBuilder(
            "/library/sections",
            name=self.name,
            the_type=LibraryType.MUSIC.value,
            agent=Agent.MUSIC.value,
            scanner=Scanner.MUSIC.value,
            language=self.language.value,
            importFromiTunes="",
            enableAutoPhotoTags="",
            location=self.locations,
            prefs=self.preferences.music,
        )

        part = query_builder.build()

        debug = f"Query: {part}\n"

        PlexUtilLogger.get_logger().debug(debug)

        # This posts a music library
        if part:
            self.plex_server.query(
                part,
                method=self.plex_server._session.post,
            )
        else:
            description = "Query Builder has not built a part!"
            raise LibraryOpError(
                op_type="CREATE",
                library_type=self.library_type,
                description=description,
            )

        # This triggers a refresh of the library
        self.plex_server.library.sections()

        local_files = PathOps.get_local_files(self.locations)

        info = (
            "Checking server music "
            "meets expected "
            f"count: {len(local_files)!s}\n"
        )
        PlexUtilLogger.get_logger().info(info)

        self.poll(200, len(local_files), 10)

    def delete(self) -> None:
        return super().delete()

    def exists(self) -> bool:
        return super().exists()

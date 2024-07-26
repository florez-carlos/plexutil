from pathlib import Path

from plexapi.server import PlexServer

from plexutil.core.library import Library
from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO
from plexutil.dto.music_playlist_file_dto import MusicPlaylistFileDTO
from plexutil.enums.agent import Agent
from plexutil.enums.language import Language
from plexutil.enums.library_name import LibraryName
from plexutil.enums.library_type import LibraryType
from plexutil.enums.scanner import Scanner
from plexutil.exception.library_op_error import LibraryOpError
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.util.query_builder import QueryBuilder


class MusicLibrary(Library):
    def __init__(
        self,
        plex_server: PlexServer,
        location: Path,
        language: Language,
        preferences: LibraryPreferencesDTO,
        music_playlist_file_dto: MusicPlaylistFileDTO,
    ) -> None:
        super().__init__(
            plex_server,
            LibraryName.MUSIC,
            LibraryType.MUSIC,
            Agent.MUSIC,
            Scanner.MUSIC,
            location,
            language,
            preferences,
        )
        self.music_playlist_file_dto = music_playlist_file_dto

    def create(self) -> None:
        op_type = "CREATE"

        part = ""

        query_builder = QueryBuilder(
            "/library/sections",
            name=LibraryName.MUSIC.value,
            the_type=LibraryType.MUSIC.value,
            agent=Agent.MUSIC.value,
            scanner=Scanner.MUSIC.value,
            language=Language.ENGLISH_US.value,
            importFromiTunes="",
            enableAutoPhotoTags="",
            location=str(self.location),
            prefs=self.preferences.music,
        )

        part = query_builder.build()

        info = (
            "Creating music library: \n"
            f"Name: {self.name.value}\n"
            f"Type: {self.library_type.value}\n"
            f"Agent: {self.agent.value}\n"
            f"Scanner: {self.scanner.value}\n"
            f"Location: {self.location!s}\n"
            f"Language: {self.language.value}\n"
            f"Preferences: {self.preferences.music}\n"
        )

        debug = f"Query: {part}\n"

        PlexUtilLogger.get_logger().info(info)
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
                op_type=op_type,
                library_type=self.library_type,
                description=description,
            )

        # This triggers a refresh of the library
        self.plex_server.library.sections()

        info = (
            "Checking server music "
            "meets expected "
            f"count: {self.music_playlist_file_dto.track_count!s}\n"
        )
        PlexUtilLogger.get_logger().info(info)

        self.poll(200, self.music_playlist_file_dto.track_count, 10)

    def delete(self) -> None:
        return super().delete()

    def exists(self) -> bool:
        return super().exists()

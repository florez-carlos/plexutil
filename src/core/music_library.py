from pathlib import Path

from plexapi.server import PlexServer
from throws import throws

from src.core.library import Library
from src.dto.library_preferences_dto import LibraryPreferencesDTO
from src.dto.music_playlist_file_dto import MusicPlaylistFileDTO
from src.enum.agent import Agent
from src.enum.language import Language
from src.enum.library_name import LibraryName
from src.enum.library_type import LibraryType
from src.enum.scanner import Scanner
from src.exception.library_op_error import LibraryOpError
from src.exception.library_poll_timeout_error import LibraryPollTimeoutError
from src.exception.library_unsupported_error import LibraryUnsupportedError
from src.util.query_builder import QueryBuilder


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

    @throws(LibraryPollTimeoutError, LibraryOpError, LibraryUnsupportedError)
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

        print("\n")
        print(
            "Checking server music meets expected count: "
            + str(self.music_playlist_file_dto.track_count),
        )
        self.poll(200, self.music_playlist_file_dto.track_count, 10)

    @throws(LibraryOpError)
    def delete(self) -> None:
        return super().delete()

    def exists(self) -> bool:
        return super().exists()

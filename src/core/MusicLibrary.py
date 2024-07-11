from pathlib import Path
from plexapi.server import PlexServer
from throws import throws
from src.dto.LibraryPreferencesDTO import LibraryPreferencesDTO
from src.exception.LibraryOpException import LibraryOpException
from src.enum.Agent import Agent
from src.enum.Language import Language
from src.enum.LibraryName import LibraryName
from src.enum.LibraryType import LibraryType
from src.enum.Scanner import Scanner
from src.dto.MusicPlaylistFileDTO import MusicPlaylistFileDTO
from src.core.Library import Library
from src.util.QueryBuilder import QueryBuilder


class MusicLibrary(Library):
    def __init__(
        self,
        plex_server: PlexServer,
        location: Path,
        language: Language,
        preferences: LibraryPreferencesDTO,
        music_playlist_file_dto: MusicPlaylistFileDTO,
    ):
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

    @throws(LibraryOpException)
    def create(self) -> None:
        try:
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
                    part, method=self.plex_server._session.post
                )
            else:
                raise LibraryOpException(
                    "CREATE", "Query Builder has not built a part!"
                )

            print("\n")
            print(
                "Checking server music meets expected count: "
                + str(self.music_playlist_file_dto.track_count)
            )
            self.poll(200, self.music_playlist_file_dto.track_count, 10)

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

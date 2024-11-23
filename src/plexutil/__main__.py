from pathlib import Path
import sys

from peewee import SqliteDatabase
from plexapi.server import PlexServer

from plexutil.core.movie_library import MovieLibrary
from plexutil.core.music_library import MusicLibrary
from plexutil.core.playlist import Playlist
from plexutil.core.prompt import Prompt
from plexutil.core.server_config import ServerConfig
from plexutil.core.tv_library import TVLibrary
from plexutil.dto import user_instructions_dto
from plexutil.enums.language import Language
from plexutil.enums.library_type import LibraryType
from plexutil.enums.user_request import UserRequest
from plexutil.exception.bootstrap_error import BootstrapError
from plexutil.exception.invalid_schema_error import InvalidSchemaError
from plexutil.model.music_playlist_entity import MusicPlaylistEntity
from plexutil.model.song_entity import SongEntity
from plexutil.model.song_music_playlist_entity import SongMusicPlaylistEntity
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.service.plexutil_library_config_service import PlexUtilLibraryConfigService
from plexutil.util.file_importer import FileImporter
from plexutil.util.plex_ops import PlexOps


def main() -> None:
    try:
        #TODO:
        # https://docs.peewee-orm.com/en/latest/peewee/relationships.html
        # # Ensure foreign-key constraints are enforced.
        # db = SqliteDatabase('my_app.db', pragmas={'foreign_keys': 1})
        
        bootstrap_paths_dto = FileImporter.bootstrap()

        config_dir = bootstrap_paths_dto.config_dir

        instructions_dto = Prompt.get_user_instructions_dto()

        request = instructions_dto.request
        items = instructions_dto.items
        server_config_dto = instructions_dto.server_config_dto

        if request == UserRequest.CONFIG:
            config = ServerConfig(bootstrap_paths_dto,server_config_dto)
            server_config_dto = config.setup()
            sys.exit(0)

        preferences_dto = FileImporter.get_library_preferences_dto(
            config_dir,
        )

        tv_language_manifest_file_dto = (
            FileImporter.get_tv_language_manifest(
                config_dir,
            )
        )

        host = server_config_dto.host
        port = server_config_dto.port
        token = server_config_dto.token

        baseurl = f"http://{host}:{port}"
        plex_server = PlexServer(baseurl, token)
        library = None
        language = instructions_dto.language

        match instructions_dto.library_type:
            case LibraryType.MUSIC:
                library = MusicLibrary(
                    plex_server,
                    language
                    preferences_dto,
                    music_playlist_file_dto,
                )
            case LibraryType.PLAYLIST:
                library = Playlist(
                    plex_server,
                    language
                    music_playlist_file_dto_filtered,
                )
            case LibraryType.MOVIE:
                library = MovieLibrary(
                    plex_server,
                    language
                    preferences_dto,
                )
            case LibraryType.TV:
                library = TVLibrary(
                    plex_server,
                    language
                    preferences_dto,
                    tv_language_manifest_file_dto,
                )
            case _:
                #TODO:
                sys.exit(1)


        match request:

            case UserRequest.CREATE_MUSIC_PLAYLIST:
                playlist_library.create()

            case UserRequest.CREATE_MUSIC_LIBRARY:
                #TODO: PlexOPS.create_library()
                #TODO: Simplify naming
                library.create()

            case UserRequest.CREATE_MOVIE_LIBRARY:
                movie_library.create()

            case (
                UserRequest.DELETE_MOVIE_LIBRARY |
                UserRequest.DELETE_TV_LIBRARY |
                UserRequest.DELETE_MUSIC_LIBRARY |
                UserRequest.DELETE_MUSIC_PLAYLIST
            ):
                if library.exists():
                    library.delete()

            case UserRequest.CREATE_TV_LIBRARY:
                tv_library.create()


            case UserRequest.SET_SERVER_SETTINGS:
                PlexOps.set_server_settings(plex_server, preferences_dto)

            case UserRequest.EXPORT_MUSIC_PLAYLIST:

                with SqliteDatabase(
                    bootstrap_paths_dto.config_dir / "playlists.db"
                ) as db:
                    db.bind([SongEntity, SongMusicPlaylistEntity, MusicPlaylistEntity])

                    db.create_tables(
                        [SongEntity, SongMusicPlaylistEntity, MusicPlaylistEntity],
                        safe=True,
                    )
                    playlist_library = Playlist(
                        plex_server,
                        music_location,
                        Language.ENGLISH_US,
                        music_playlist_file_dto,
                    )
                    playlist_library.export_music_playlists()

    except SystemExit as e:
        if e.code == 0:
            description = "Successful System Exit"
            PlexUtilLogger.get_logger().debug(description)
        else:
            description = "Unexpected error:"
            PlexUtilLogger.get_logger().exception(description)
            raise

    except PlexUtilConfigError:
        description = "Plexutil configuration error"
        PlexUtilLogger.get_logger().exception(description)

    except InvalidSchemaError as e:
        description = "\n\n=====Invalid schema error=====\n\n" f"{e!s}"
        PlexUtilLogger.get_logger().exception(description)

    # No regular logger can be expected to be initialized
    except BootstrapError as e:
        description = "\n\n=====Program initialization error=====\n\n" f"{e!s}"
        e.args = (description,)
        raise

    except Exception:  # noqa: BLE001
        description = "Unexpected error:"
        PlexUtilLogger.get_logger().exception(description)


if __name__ == "__main__":
    main()

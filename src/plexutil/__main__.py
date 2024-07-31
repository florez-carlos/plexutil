import sys

from plexapi.server import PlexServer

from plexutil.core.movie_library import MovieLibrary
from plexutil.core.music_library import MusicLibrary
from plexutil.core.playlist import Playlist
from plexutil.core.prompt import Prompt
from plexutil.core.tv_library import TVLibrary
from plexutil.dto.music_playlist_file_dto import MusicPlaylistFileDTO
from plexutil.enums.language import Language
from plexutil.enums.user_request import UserRequest
from plexutil.exception.bootstrap_error import BootstrapError
from plexutil.exception.plex_util_config_error import PlexUtilConfigError
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.util.file_importer import FileImporter
from plexutil.util.plex_ops import PlexOps


def main() -> None:
    try:
        bootstrap_paths_dto = FileImporter.bootstrap()

        config_dir = bootstrap_paths_dto.config_dir
        plexutil_config_file = bootstrap_paths_dto.plexutil_config_file

        instructions_dto = Prompt.get_user_instructions_dto(
            plexutil_config_file
        )

        request = instructions_dto.request
        items = instructions_dto.items
        plex_config_dto = instructions_dto.plex_config_dto

        if request == UserRequest.CONFIG:
            sys.exit(0)

        music_location = instructions_dto.plex_config_dto.music_folder_path
        movie_location = instructions_dto.plex_config_dto.movie_folder_path
        tv_location = instructions_dto.plex_config_dto.tv_folder_path

        preferences_dto = FileImporter.get_library_preferences_dto(
            config_dir,
        )
        music_playlist_file_dto = FileImporter.get_music_playlist_file_dto(
            config_dir,
        )
        tv_language_manifest_file_dto = FileImporter.get_tv_language_manifest(
            config_dir,
        )

        playlists = []
        music_playlist_file_dto_filtered = MusicPlaylistFileDTO()

        if items:
            playlists = [
                playlist
                for playlist in music_playlist_file_dto.playlists
                if playlist.name in items
            ]

            music_playlist_file_dto_filtered = MusicPlaylistFileDTO(
                music_playlist_file_dto.track_count,
                playlists,
            )

        if instructions_dto.is_all_items:
            music_playlist_file_dto_filtered = music_playlist_file_dto

        host = plex_config_dto.host
        port = int(plex_config_dto.port)
        token = plex_config_dto.token

        baseurl = f"http://{host}:{port}"
        plex_server = PlexServer(baseurl, token)

        match request:
            # If config, we should already be done by now
            case UserRequest.CONFIG:
                return
            case UserRequest.INIT:
                PlexOps.set_server_settings(plex_server, preferences_dto)

                music_library = MusicLibrary(
                    plex_server,
                    music_location,
                    Language.ENGLISH_US,
                    preferences_dto,
                    music_playlist_file_dto,
                )
                tv_library = TVLibrary(
                    plex_server,
                    tv_location,
                    Language.ENGLISH_US,
                    preferences_dto,
                    tv_language_manifest_file_dto,
                )
                movie_library = MovieLibrary(
                    plex_server,
                    movie_location,
                    Language.ENGLISH_US,
                    preferences_dto,
                )
                playlist_library = Playlist(
                    plex_server,
                    music_location,
                    Language.ENGLISH_US,
                    music_playlist_file_dto,
                )

                if music_library.exists():
                    music_library.delete()
                if tv_library.exists():
                    tv_library.delete()
                if movie_library.exists():
                    movie_library.delete()

                music_library.create()
                tv_library.create()
                movie_library.create()
                playlist_library.create()

            case UserRequest.DELETE_MUSIC_PLAYLIST:
                playlist_library = Playlist(
                    plex_server,
                    music_location,
                    Language.ENGLISH_US,
                    music_playlist_file_dto_filtered,
                )
                if playlist_library.exists():
                    playlist_library.delete()

            case UserRequest.CREATE_MUSIC_PLAYLIST:
                playlist_library = Playlist(
                    plex_server,
                    music_location,
                    Language.ENGLISH_US,
                    music_playlist_file_dto_filtered,
                )
                playlist_library.create()

            case UserRequest.DELETE_MUSIC_LIBRARY:
                music_library = MusicLibrary(
                    plex_server,
                    music_location,
                    Language.ENGLISH_US,
                    preferences_dto,
                    music_playlist_file_dto,
                )
                if music_library.exists():
                    music_library.delete()

            case UserRequest.CREATE_MUSIC_LIBRARY:
                music_library = MusicLibrary(
                    plex_server,
                    music_location,
                    Language.ENGLISH_US,
                    preferences_dto,
                    music_playlist_file_dto,
                )
                music_library.create()

            case UserRequest.CREATE_MOVIE_LIBRARY:
                movie_library = MovieLibrary(
                    plex_server,
                    movie_location,
                    Language.ENGLISH_US,
                    preferences_dto,
                )
                movie_library.create()

            case UserRequest.DELETE_MOVIE_LIBRARY:
                movie_library = MovieLibrary(
                    plex_server,
                    movie_location,
                    Language.ENGLISH_US,
                    preferences_dto,
                )
                if movie_library.exists():
                    movie_library.delete()

            case UserRequest.CREATE_TV_LIBRARY:
                tv_library = TVLibrary(
                    plex_server,
                    tv_location,
                    Language.ENGLISH_US,
                    preferences_dto,
                    tv_language_manifest_file_dto,
                )
                tv_library.create()

            case UserRequest.DELETE_TV_LIBRARY:
                tv_library = TVLibrary(
                    plex_server,
                    tv_location,
                    Language.ENGLISH_US,
                    preferences_dto,
                    tv_language_manifest_file_dto,
                )
                if tv_library.exists():
                    tv_library.delete()

            case UserRequest.SET_SERVER_SETTINGS:
                PlexOps.set_server_settings(plex_server, preferences_dto)
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

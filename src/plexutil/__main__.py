import sys
from typing import cast

from peewee import DoesNotExist
from plexapi.server import PlexServer

from plexutil.core.movie_library import MovieLibrary
from plexutil.core.music_library import MusicLibrary
from plexutil.core.playlist import Playlist
from plexutil.core.prompt import Prompt
from plexutil.core.server_config import ServerConfig
from plexutil.core.tv_library import TVLibrary
from plexutil.dto.music_playlist_dto import MusicPlaylistDTO
from plexutil.enums.library_type import LibraryType
from plexutil.enums.user_request import UserRequest
from plexutil.exception.bootstrap_error import BootstrapError
from plexutil.exception.invalid_schema_error import InvalidSchemaError
from plexutil.exception.library_illegal_state_error import (
    LibraryIllegalStateError,
)
from plexutil.exception.server_config_error import ServerConfigError
from plexutil.exception.unexpected_argument_error import (
    UnexpectedArgumentError,
)
from plexutil.exception.user_error import UserError
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.util.file_importer import FileImporter
from plexutil.util.path_ops import PathOps
from plexutil.util.plex_ops import PlexOps


def main() -> None:
    try:
        bootstrap_paths_dto = FileImporter.bootstrap()
        FileImporter.populate_sample(bootstrap_paths_dto)

        config_dir = bootstrap_paths_dto.config_dir

        instructions_dto = Prompt.get_user_instructions_dto()

        request = instructions_dto.request
        songs = instructions_dto.songs
        playlist_name = instructions_dto.playlist_name
        language = instructions_dto.language
        library_name = instructions_dto.library_name
        locations = instructions_dto.locations
        library_type = instructions_dto.library_type
        server_config_dto = instructions_dto.server_config_dto

        config = ServerConfig(bootstrap_paths_dto, server_config_dto)

        song_paths = [PathOps.get_path_from_str(x) for x in songs]
        local_files = PathOps.get_local_files(song_paths)
        songs_dto = [PlexOps.local_file_to_song_dto(x) for x in local_files]

        music_playlist_dto = MusicPlaylistDTO(
            name=playlist_name,
            songs=songs_dto,
        )

        if request == UserRequest.CONFIG:
            server_config_dto = config.save()
            sys.exit(0)
        else:
            try:
                server_config_dto = config.get()
            except DoesNotExist:
                description = "No Server Config found"
                PlexUtilLogger.get_logger().debug(description)

        host = server_config_dto.host
        port = server_config_dto.port
        token = server_config_dto.token

        if (
            instructions_dto.is_show_configuration
            | instructions_dto.is_show_configuration_token
        ):
            if request:
                description = (
                    f"Received a request: '{request.value}' but also a call "
                    f"to show configuration?\n"
                    f"plexutil -sc OR plexutil -sct to show the token\n"
                )

                raise UserError(description)

            description = (
                "\n=====Server Configuration=====\n"
                "To update the configuration: plexutil config -token ...\n\n"
                f"Host: {host}\n"
                f"Port: {port}\n"
                f"Token: "
            )
            if instructions_dto.is_show_configuration_token:
                description = (
                    description + f"{token if token else 'NOT SUPPLIED'}\n"
                )
            else:
                description = (
                    description + "\n\nINFO: To show token use"
                    "--show_configuration_token\n"
                )

            PlexUtilLogger.get_console_logger().info(description)

            sys.exit(0)

        if not token:
            description = (
                "Plex Token has not been supplied, cannot continue\n"
                "Set a token -> plexutil config -token ..."
            )
            raise ServerConfigError(description)

        preferences_dto = FileImporter.get_library_preferences_dto(
            config_dir,
        )

        tv_language_manifest_dto = FileImporter.get_tv_language_manifest(
            config_dir,
        )

        baseurl = f"http://{host}:{port}"
        plex_server = PlexServer(baseurl, token)
        library = None

        match library_type:
            case LibraryType.MUSIC:
                library = MusicLibrary(
                    plex_server=plex_server,
                    language=language,
                    preferences=preferences_dto,
                    name=library_name,
                    locations=locations,
                )
            case LibraryType.MUSIC_PLAYLIST:
                library = Playlist(
                    plex_server=plex_server,
                    language=language,
                    music_playlists_dto=[music_playlist_dto],
                    library_type=LibraryType.MUSIC,
                    name=library_name,
                    playlist_name=playlist_name,
                    locations=locations,
                )
            case LibraryType.MOVIE:
                library = MovieLibrary(
                    plex_server=plex_server,
                    language=language,
                    preferences=preferences_dto,
                    name=library_name,
                    locations=locations,
                )
            case LibraryType.TV:
                library = TVLibrary(
                    plex_server=plex_server,
                    language=language,
                    preferences=preferences_dto,
                    tv_language_manifest_dto=tv_language_manifest_dto,
                    locations=locations,
                )
            case _:
                description = "Didn't receive a request"
                PlexUtilLogger.get_logger().error(description)
                sys.exit(1)

        match request:
            case (
                UserRequest.CREATE_MUSIC_LIBRARY
                | UserRequest.CREATE_MOVIE_LIBRARY
                | UserRequest.CREATE_TV_LIBRARY
            ):
                library.create()

            case (
                UserRequest.DELETE_MOVIE_LIBRARY
                | UserRequest.DELETE_TV_LIBRARY
                | UserRequest.DELETE_MUSIC_LIBRARY
                | UserRequest.DELETE_MUSIC_PLAYLIST
            ):
                if library.exists():
                    library.delete()

            case UserRequest.SET_SERVER_SETTINGS:
                PlexOps.set_server_settings(plex_server, preferences_dto)

            case UserRequest.EXPORT_MUSIC_PLAYLIST:
                cast(Playlist, library).export_music_playlists(
                    bootstrap_paths_dto
                )

            case UserRequest.IMPORT_MUSIC_PLAYLIST:
                cast(Playlist, library).import_music_playlists(
                    bootstrap_paths_dto
                )

            case UserRequest.ADD_SONGS_TO_MUSIC_PLAYLIST:
                cast(Playlist, library).add_songs(songs_dto)

            case UserRequest.DELETE_SONGS_FROM_MUSIC_PLAYLIST:
                cast(Playlist, library).delete_songs(songs_dto)

    except SystemExit as e:
        if e.code == 0:
            description = "Successful System Exit"
            PlexUtilLogger.get_logger().debug(description)
        else:
            description = "\n=====Unexpected error=====\n" f"{e!s}"
            PlexUtilLogger.get_logger().exception(description)
            raise

    except ServerConfigError as e:
        sys.tracebacklimit = 0
        description = "\n=====Server Config Error=====\n" f"{e!s}"
        PlexUtilLogger.get_logger().error(description)
        sys.exit(1)

    except UserError as e:
        sys.tracebacklimit = 0
        description = "\n=====User Error=====\n" f"{e!s}"
        PlexUtilLogger.get_logger().error(description)
        sys.exit(1)

    except LibraryIllegalStateError as e:
        sys.tracebacklimit = 0
        description = "\n=====Local Library Illegal State=====\n" f"{e!s}"
        PlexUtilLogger.get_logger().error(description)
        sys.exit(1)

    except UnexpectedArgumentError as e:
        sys.tracebacklimit = 0
        description = (
            "\n=====User Argument Error=====\n"
            "These arguments are unrecognized: \n"
        )
        for argument in e.args[0]:
            description += "-> " + argument + "\n"
        PlexUtilLogger.get_logger().error(description)
        sys.exit(1)

    except InvalidSchemaError as e:
        sys.tracebacklimit = 0
        description = "\n=====Invalid schema error=====\n" f"{e!s}"
        PlexUtilLogger.get_logger().error(description)

    # No regular logger can be expected to be initialized
    except BootstrapError as e:
        description = "\n=====Program initialization error=====\n" f"{e!s}"
        e.args = (description,)
        raise

    except Exception as e:  # noqa: BLE001
        description = "\n=====Unexpected error=====\n" f"{e!s}"
        PlexUtilLogger.get_logger().exception(description)


if __name__ == "__main__":
    main()

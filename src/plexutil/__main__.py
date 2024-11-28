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
from plexutil.dto.server_config_dto import ServerConfigDTO
from plexutil.enums.library_type import LibraryType
from plexutil.enums.user_request import UserRequest
from plexutil.exception.bootstrap_error import BootstrapError
from plexutil.exception.invalid_schema_error import InvalidSchemaError
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.service.server_config_service import ServerConfigService
from plexutil.util.file_importer import FileImporter
from plexutil.util.plex_ops import PlexOps


def main() -> None:
    try:
        bootstrap_paths_dto = FileImporter.bootstrap()

        config_dir = bootstrap_paths_dto.config_dir

        instructions_dto = Prompt.get_user_instructions_dto()

        request = instructions_dto.request
        items = instructions_dto.items
        server_config_dto = instructions_dto.server_config_dto

        if request == UserRequest.CONFIG:
            config = ServerConfig(bootstrap_paths_dto, server_config_dto)
            server_config_dto = config.setup()
            sys.exit(0)

        if instructions_dto.is_show_configuration:
            try:
                service = ServerConfigService(bootstrap_paths_dto.config_dir / "config.db")
                server_config_dto = service.get_id()
                print(server_config_dto)
            except DoesNotExist:
                dto = ServerConfigDTO()
                description = (
                    "\n=====Server Configuration=====\n"
                    "To update the configuration: plexutil config --token ...\n\n"
                    f"Host: {dto.host}\n"
                    f"Port: {dto.port}\n"
                    f"Token: None supplied\n"
                )
                PlexUtilLogger.get_logger().info(description)
                description = "WARNING: Token has not been supplied"
                PlexUtilLogger.get_logger().warning(description)

            sys.exit(0)

        preferences_dto = FileImporter.get_library_preferences_dto(
            config_dir,
        )

        tv_language_manifest_dto = FileImporter.get_tv_language_manifest(
            config_dir,
        )

        host = server_config_dto.host
        port = server_config_dto.port
        token = server_config_dto.token

        baseurl = f"http://{host}:{port}"
        plex_server = PlexServer(baseurl, token)
        library = None
        language = instructions_dto.language
        library_name = instructions_dto.library_name
        locations = instructions_dto.locations
        library_type = instructions_dto.library_type

        match instructions_dto.library_type:
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
                    playlist_names=items,
                    library_type=library_type,
                    name=library_name,
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
                # TODO:
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

            case UserRequest.EXPORT_MUSIC_PLAYLIST:
                cast(Playlist, library).import_music_playlists(
                    bootstrap_paths_dto
                )

    except SystemExit as e:
        if e.code == 0:
            description = "Successful System Exit"
            PlexUtilLogger.get_logger().debug(description)
        else:
            description = "Unexpected error:"
            PlexUtilLogger.get_logger().exception(description)
            raise

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

from datetime import datetime, timezone
import logging.config
import ctypes.wintypes
import os
import platform
from pathlib import Path

from plexapi.server import PlexServer

from src.core.movie_library import MovieLibrary
from src.core.music_library import MusicLibrary
from src.core.playlist import Playlist
from src.core.prompt import Prompt
from src.core.tv_library import TVLibrary
from src.dto.music_playlist_file_dto import MusicPlaylistFileDTO
from src.enum.language import Language
from src.enum.user_request import UserRequest
from src.plex_util_logger import PlexUtilLogger
from src.util.file_importer import FileImporter
from src.util.plex_ops import PlexOps

logger = None


def main() -> None:
    home_folder = Path()
    plex_util_dir = Path()
    config_dir = Path()
    log_dir = Path()
    system = platform.system()
    if system == "Windows":
        CSIDL_PERSONAL = 5
        SHGFP_TYPE_CURRENT = 0

        buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(  # pyright: ignore
            None,
            CSIDL_PERSONAL,
            None,
            SHGFP_TYPE_CURRENT,
            buf
        )        
        home_folder = buf.value or ""
        if not home_folder:
            description = "Could not locate Documents folder"
            raise FileNotFoundError(description)
    elif system == "Linux":
        home_folder = os.getenv("HOME") or ""
    else:
        description = f"Unsupported OS: {system}"
        raise OSError(description)

    plex_util_dir = Path(home_folder) / "plexutil"
    config_dir = plex_util_dir / "config"
    log_dir = plex_util_dir / "log"

    plex_util_dir.mkdir(exist_ok=True)
    config_dir.mkdir(exist_ok=True)
    log_dir.mkdir(exist_ok=True)
    
    logger = PlexUtilLogger(log_dir)

    try:

        config_file_path = config_dir / "config.json"
        instructions_dto = Prompt.get_user_instructions_dto(config_file_path)

        request = instructions_dto.request
        items = instructions_dto.items
        plex_config_dto = instructions_dto.plex_config_dto

        host = plex_config_dto.host
        port = int(plex_config_dto.port)
        token = plex_config_dto.token

        baseurl = f"http://{host}:{port}"
        plex_server = PlexServer(baseurl, token)

        music_location = instructions_dto.plex_config_dto.music_folder_path
        movie_location = instructions_dto.plex_config_dto.movie_folder_path
        tv_location = instructions_dto.plex_config_dto.tv_folder_path

        music_prefs_file_location = config_dir / "music_library_preferences.json"
        movie_prefs_file_location = config_dir / "movie_library_preferences.json"
        tv_prefs_file_location = config_dir / "tv_library_preferences.json"
        plex_server_setting_prefs_file_location = (
            config_dir / "plex_server_setting_preferences.json"
        )
        music_playlist_file_location = config_dir / "music_playlists.json"
        tv_language_manifest_file_location = (
            config_dir / "tv_language_manifest.json"
        )

        preferences_dto = FileImporter.get_library_preferences_dto(
            music_prefs_file_location,
            movie_prefs_file_location,
            tv_prefs_file_location,
            plex_server_setting_prefs_file_location,
        )
        music_playlist_file_dto = FileImporter.get_music_playlist_file_dto(
            music_playlist_file_location,
        )
        tv_language_manifest_file_dto = FileImporter.get_tv_language_manifest(
            tv_language_manifest_file_location,
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
    except:

        raise

if __name__ == "__main__":
    main()

import ctypes.wintypes
import json
import os
import platform
import syslog
import time
from pathlib import Path

from plexutil.exception.bootstrap_error import BootstrapError

if platform.system() == "Windows":
    import win32evtlog  # pyright: ignore # noqa: PGH003
    import win32evtlogutil  # pyright: ignore # noqa: PGH003

import yaml

from plexutil.dto.bootstrap_paths_dto import BootstrapPathsDTO
from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO
from plexutil.dto.music_playlist_file_dto import MusicPlaylistFileDTO
from plexutil.dto.plex_config_dto import PlexConfigDTO
from plexutil.dto.tv_language_manifest_file_dto import (
    TVLanguageManifestFileDTO,
)
from plexutil.exception.plex_util_config_error import PlexUtilConfigError
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.serializer.music_playlist_file_serializer import (
    MusicPlaylistFileSerializer,
)
from plexutil.serializer.plex_config_serializer import PlexConfigSerializer
from plexutil.serializer.tv_language_manifest_serializer import (
    TVLanguageManifestSerializer,
)
from plexutil.static import Static
from plexutil.util.path_ops import PathOps


class FileImporter(Static):
    encoding = "utf-8"

    @staticmethod
    def get_library_preferences_dto(
        config_dir: Path,
    ) -> LibraryPreferencesDTO:
        music_preferences_file_location = (
            config_dir / "music_library_preferences.json"
        )
        movie_preferences_file_location = (
            config_dir / "movie_library_preferences.json"
        )
        tv_preferences_file_location = (
            config_dir / "tv_library_preferences.json"
        )
        plex_server_setting_prefs_file_location = (
            config_dir / "plex_server_setting_preferences.json"
        )
        music_prefs = {}
        movie_prefs = {}
        tv_prefs = {}
        plex_server_setting_prefs = {}

        try:
            with music_preferences_file_location.open(
                encoding=FileImporter.encoding,
            ) as file:
                music_prefs = json.load(file)
        except FileNotFoundError:
            description = (
                "Music Library Preferences not found. "
                "Proceeding with no music preferences\n"
            )
            PlexUtilLogger.get_logger().info(description)
            time.sleep(2)
            music_prefs = {}

        try:
            with movie_preferences_file_location.open(
                encoding=FileImporter.encoding,
            ) as file:
                movie_prefs = json.load(file)
        except FileNotFoundError:
            description = (
                "Movie Library Preferences not found. "
                "Proceeding with no movie preferences\n"
            )
            PlexUtilLogger.get_logger().info(description)
            time.sleep(2)
            movie_prefs = {}

        try:
            with tv_preferences_file_location.open(
                encoding=FileImporter.encoding
            ) as file:
                tv_prefs = json.load(file)
        except FileNotFoundError:
            description = (
                "TV Library Preferences not found. "
                "Proceeding with no tv preferences\n"
            )
            PlexUtilLogger.get_logger().info(description)
            time.sleep(2)
            tv_prefs = {}

        try:
            with plex_server_setting_prefs_file_location.open(
                encoding=FileImporter.encoding,
            ) as file:
                plex_server_setting_prefs = json.load(file)
        except FileNotFoundError:
            description = (
                "Plex Server Setting Preferences not found. "
                "Proceeding with no plex server setting preferences\n"
            )
            PlexUtilLogger.get_logger().info(description)
            time.sleep(2)
            plex_server_setting_prefs = {}

        return LibraryPreferencesDTO(
            music_prefs,
            movie_prefs,
            tv_prefs,
            plex_server_setting_prefs,
        )

    @staticmethod
    def get_plex_config_dto(plex_config_file_location: Path) -> PlexConfigDTO:
        serializer = PlexConfigSerializer()

        try:
            with plex_config_file_location.open(
                encoding=FileImporter.encoding
            ) as file:
                file_dict = json.load(file)
                return serializer.to_dto(file_dict)
        except FileNotFoundError:
            description = (
                "\n\n=====plexutil config file not found=====\n\n"
                "A plexutil configuration file must exist prior to use.\n"
                "\nplexutil config  \\\n"
                "-music <path/to/music/folder> \\\n"
                "-movie <path/to/movie/folder> \\\n"
                "-tv <path/to/tv/folder> \\\n"
                "-host <plex server host> \\\n"
                "-port <plex server port> \\\n"
                "-token <plex server token>\n\n"
                "*Replace placeholder brackets with the appropriate values"
            )
            raise PlexUtilConfigError(description) from FileNotFoundError

    @staticmethod
    def save_plex_config_dto(
        plex_config_file_location: Path,
        plex_config_dto: PlexConfigDTO,
        is_overwrite: bool = True,
    ) -> None:
        mode = "w" if is_overwrite else "x"

        with plex_config_file_location.open(
            encoding=FileImporter.encoding,
            mode=mode,
        ) as f:
            serializer = PlexConfigSerializer()
            json.dump(serializer.to_json(plex_config_dto), f, indent=4)

    @staticmethod
    def get_music_playlist_file_dto(
        config_dir: Path,
    ) -> MusicPlaylistFileDTO:
        serializer = MusicPlaylistFileSerializer()

        music_playlist_file_location = config_dir / "music_playlists.json"

        try:
            with music_playlist_file_location.open(
                encoding=FileImporter.encoding
            ) as file:
                file_dict = json.load(file)
                return serializer.to_dto(file_dict)
        except FileNotFoundError:
            description = (
                "Music Playlists File not found. "
                "Proceeding with no music playlists file\n"
            )
            PlexUtilLogger.get_logger().info(description)
            description = f"Supplied location: {music_playlist_file_location}"
            PlexUtilLogger.get_logger().debug(description)
            time.sleep(2)

        return MusicPlaylistFileDTO()

    @staticmethod
    def get_tv_language_manifest(
        config_dir: Path,
    ) -> TVLanguageManifestFileDTO:
        serializer = TVLanguageManifestSerializer()

        tv_language_manifest_file_location = (
            config_dir / "tv_language_manifest.json"
        )

        try:
            with tv_language_manifest_file_location.open(
                encoding=FileImporter.encoding
            ) as file:
                file_dict = json.load(file)
                return serializer.to_dto(file_dict)
        except FileNotFoundError:
            description = (
                "TV Language Manifest File not found. "
                "Proceeding with no tv language manifest file\n"
            )
            PlexUtilLogger.get_logger().info(description)
            description = (
                "Supplied location: " f"{tv_language_manifest_file_location}"
            )
            PlexUtilLogger.get_logger().debug(description)
            time.sleep(2)

        return TVLanguageManifestFileDTO()

    @staticmethod
    def get_logging_config(logging_config_path: Path) -> dict:
        with logging_config_path.open(
            "r", errors="strict", encoding=FileImporter.encoding
        ) as file:
            return yaml.safe_load(file)

    @staticmethod
    def bootstrap() -> BootstrapPathsDTO:
        try:
            home_folder = Path()
            system = platform.system()
            system = "Darwin"

            if system == "Windows":
                csidl_personal = 5
                shgfp_type_current = 0

                buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
                ctypes.windll.shell32.SHGetFolderPathW(  # pyright: ignore # noqa: PGH003
                    None, csidl_personal, None, shgfp_type_current, buf
                )
                home_folder = buf.value or ""
                if not home_folder:
                    description = "Could not locate Documents folder"
                    raise FileNotFoundError(description)  # noqa: TRY301

            elif system == "Linux":
                home_folder = os.getenv("HOME") or ""
            else:
                description = f"Unsupported OS: {system}"
                raise OSError(description)  # noqa: TRY301

            plexutil_dir = Path(home_folder) / "plexutil"
            config_dir = plexutil_dir / "config"
            log_dir = plexutil_dir / "log"
            plexutil_config_file = config_dir / "config.json"

            plexutil_dir.mkdir(exist_ok=True)
            config_dir.mkdir(exist_ok=True)
            log_dir.mkdir(exist_ok=True)

            log_config_file_path = (
                PathOps.get_project_root()
                / "plexutil"
                / "config"
                / "log_config.yaml"
            )

            log_config = FileImporter.get_logging_config(log_config_file_path)

            PlexUtilLogger(log_dir, log_config)

            return BootstrapPathsDTO(
                config_dir=config_dir,
                log_dir=log_dir,
                plexutil_config_file=plexutil_config_file,
            )

        except Exception as e:
            if platform.system == "Windows":
                win32evtlogutil.ReportEvent(  # pyright: ignore # noqa: PGH003
                    "plexutil",
                    eventID=1,
                    eventType=win32evtlog.EVENTLOG_ERROR_TYPE,  # pyright: ignore # noqa: PGH003
                    strings=[""],
                )
            elif platform.system == "Linux":
                syslog.syslog(syslog.LOG_ERR, "")
            if e.args and len(e.args) >= 0:
                raise BootstrapError(e.args[0]) from e

            raise BootstrapError from e

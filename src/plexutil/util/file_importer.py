import json
from pathlib import Path

import yaml

from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO
from plexutil.dto.music_playlist_file_dto import MusicPlaylistFileDTO
from plexutil.dto.plex_config_dto import PlexConfigDTO
from plexutil.dto.tv_language_manifest_file_dto import (
    TVLanguageManifestFileDTO,
)
from plexutil.serializer.music_playlist_file_serializer import (
    MusicPlaylistFileSerializer,
)
from plexutil.serializer.plex_config_serializer import PlexConfigSerializer
from plexutil.serializer.tv_language_manifest_serializer import (
    TVLanguageManifestSerializer,
)
from plexutil.static import Static


class FileImporter(Static):
    encoding = "utf-8"

    @staticmethod
    def get_library_preferences_dto(
        music_preferences_file_location: Path,
        movie_preferences_file_location: Path,
        tv_preferences_file_location: Path,
        plex_server_setting_prefs_file_location: Path,
    ) -> LibraryPreferencesDTO:
        music_prefs = {}
        movie_prefs = {}
        tv_prefs = {}
        plex_server_setting_prefs = {}

        with music_preferences_file_location.open(
            encoding=FileImporter.encoding,
        ) as file:
            music_prefs = json.load(file)

        with movie_preferences_file_location.open(
            encoding=FileImporter.encoding,
        ) as file:
            movie_prefs = json.load(file)

        with tv_preferences_file_location.open(
            encoding=FileImporter.encoding
        ) as file:
            tv_prefs = json.load(file)

        with plex_server_setting_prefs_file_location.open(
            encoding=FileImporter.encoding,
        ) as file:
            plex_server_setting_prefs = json.load(file)

        return LibraryPreferencesDTO(
            music_prefs,
            movie_prefs,
            tv_prefs,
            plex_server_setting_prefs,
        )

    @staticmethod
    def get_plex_config_dto(plex_config_file_location: Path) -> PlexConfigDTO:
        serializer = PlexConfigSerializer()

        with plex_config_file_location.open(
            encoding=FileImporter.encoding
        ) as file:
            file_dict = json.load(file)
            return serializer.to_dto(file_dict)

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
        music_playlist_file_location: Path,
    ) -> MusicPlaylistFileDTO:
        serializer = MusicPlaylistFileSerializer()

        with music_playlist_file_location.open(
            encoding=FileImporter.encoding
        ) as file:
            file_dict = json.load(file)
            return serializer.to_dto(file_dict)

    @staticmethod
    def get_tv_language_manifest(
        tv_language_manifest_location: Path,
    ) -> TVLanguageManifestFileDTO:
        serializer = TVLanguageManifestSerializer()

        with tv_language_manifest_location.open(
            encoding=FileImporter.encoding
        ) as file:
            file_dict = json.load(file)
            return serializer.to_dto(file_dict)

    @staticmethod
    def get_logging_config(logging_config_path: Path) -> dict:
        with logging_config_path.open(
            "r", errors="strict", encoding=FileImporter.encoding
        ) as file:
            return yaml.safe_load(file)

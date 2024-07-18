from pathlib import Path

from plexapi.utils import json

from src.dto.library_preferences_dto import LibraryPreferencesDTO
from src.dto.music_playlist_file_dto import MusicPlaylistFileDTO
from src.dto.plex_config_dto import PlexConfigDTO
from src.dto.tv_language_manifest_file_dto import TVLanguageManifestFileDTO
from src.serializer.music_playlist_file_serializer import (
    MusicPlaylistFileSerializer,
)
from src.serializer.plex_config_serializer import PlexConfigSerializer
from src.serializer.tv_language_manifest_serializer import (
    TVLanguageManifestSerializer,
)
from src.static import Static


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
            file_dict = json.load(file)
            music_prefs = file_dict.get("prefs")

        with movie_preferences_file_location.open(
            encoding=FileImporter.encoding,
        ) as file:
            file_dict = json.load(file)
            movie_prefs = file_dict.get("prefs")

        with tv_preferences_file_location.open(
            encoding=FileImporter.encoding
        ) as file:
            file_dict = json.load(file)
            tv_prefs = file_dict.get("prefs")

        with plex_server_setting_prefs_file_location.open(
            encoding="utf-8",
        ) as file:
            file_dict = json.load(file)
            plex_server_setting_prefs = file_dict.get("prefs")

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

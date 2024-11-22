from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, List

from plexapi.audio import Track
from plexapi.server import Playlist

from plexutil.enums.file_type import FileType
from plexutil.model.music_playlist_entity import MusicPlaylistEntity
from plexutil.model.song_entity import SongEntity
from plexutil.static import Static
from plexutil.util.path_ops import PathOps

if TYPE_CHECKING:
    from plexapi.server import PlexServer

    from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO


class PlexOps(Static):
    @staticmethod
    def set_server_settings(
        plex_server: PlexServer,
        library_preferences_dto: LibraryPreferencesDTO,
    ) -> None:
        server_settings = library_preferences_dto.plex_server_settings
        for setting_id, setting_value in server_settings.items():
            plex_server.settings.get(setting_id).set(setting_value)
        plex_server.settings.save()

    @staticmethod
    def get_music_playlist_entity(playlist: Playlist) -> MusicPlaylistEntity:
        return MusicPlaylistEntity(name=playlist.title)

    # @staticmethod
    # def get_entity(plexutil_config_dto: PlexConfigDTO) -> PlexUtilConfigEntity:
    #     return PlexUtilConfigEntity(
    #         host=plexutil_config_dto.host,
    #         port=plexutil_config_dto.port,
    #         token=plexutil_config_dto.token,
    #     )
    #
    # @staticmethod
    # def get_dto(plexutil_config_entity: PlexUtilConfigEntity) -> PlexConfigDTO:
    #     return PlexConfigDTO(
    #         host=str(plexutil_config_entity.host),
    #         port=int(plexutil_config_entity.port),
    #         token=str(plexutil_config_entity.token),
    #     )

    @staticmethod
    def get_song_entity(track: Track) -> SongEntity:
        plex_track_absolute_location = track.locations[0]
        plex_track_path = PathOps.get_path_from_str(
            plex_track_absolute_location,
        )
        plex_track_full_name = plex_track_path.name
        plex_track_name = plex_track_full_name.rsplit(".", 1)[0]
        plex_track_ext = FileType.get_file_type_from_str(
            plex_track_full_name.rsplit(".", 1)[1],
        )
        return SongEntity(name=plex_track_name, extension=plex_track_ext.value)

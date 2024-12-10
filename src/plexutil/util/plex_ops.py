from __future__ import annotations

from typing import TYPE_CHECKING

from plexutil.dto.song_dto import SongDTO
from plexutil.enums.file_type import FileType
from plexutil.exception.library_illegal_state_error import (
    LibraryIllegalStateError,
)
from plexutil.mapper.song_mapper import SongMapper
from plexutil.model.music_playlist_entity import MusicPlaylistEntity
from plexutil.model.song_entity import SongEntity
from plexutil.static import Static
from plexutil.util.path_ops import PathOps

if TYPE_CHECKING:
    from pathlib import Path

    from plexapi.audio import Track
    from plexapi.server import Playlist, PlexServer

    from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO
    from plexutil.dto.local_file_dto import LocalFileDTO


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

    @staticmethod
    def filter_tracks(
        tracks: list[Track],
        songs: list[SongDTO],
    ) -> tuple[list[Track], list[SongDTO]]:
        """
        Filters the provided tracks with the provided songs,
        return as 1st element in tuple the filtered tracks,
        2nd element is songs that do not match any tracks

        Args:
            tracks ([plexapi.audio.Track]): plexapi tracks.
            songs ([SongDTO]): SongDTOs.

        Returns:
        A tuple of:
        1) Tracks that match the provided songs
        2) Songs that did not match to any tracks
        """

        filtered_tracks = []
        unknown_songs = []
        mapper = SongMapper()
        track_song = {}
        for track in tracks:
            song_dto = mapper.get_dto(PlexOps.get_song_entity(track))
            track_song[song_dto] = track

        for song in songs:
            if song in track_song:
                filtered_tracks.append(track_song[song])
            else:
                unknown_songs.append(song)

        return filtered_tracks, unknown_songs

    @staticmethod
    def validate_local_files(
        tracks: list[Track],
        locations: list[Path],
    ) -> None:
        """
        Verifies that all local files match the provided plex tracks
        in the locations indicated

        Args:
            tracks ([plexapi.audio.Track]): plexapi tracks.
            locations ([Path]): local file locations.

        Returns:
            None, raises error if local files do not match tracks
        """

        local_files = PathOps.get_local_files(locations)
        songs = []
        for local_file in local_files:
            song_dto = PlexOps.local_file_to_song_dto(local_file)
            songs.append(song_dto)

        _, unknown = PlexOps.filter_tracks(tracks, songs)
        if unknown:
            description = "These local songs are unknown to the plex server:\n"
            for u in unknown:
                description = (
                    description + f"-> {u.name}.{u.extension.value}\n"
                )

            raise LibraryIllegalStateError(description)

    @staticmethod
    def local_file_to_song_dto(local_file: LocalFileDTO) -> SongDTO:
        return SongDTO(
            name=local_file.name,
            extension=local_file.extension,
        )

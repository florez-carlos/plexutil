from __future__ import annotations

from typing import TYPE_CHECKING, cast

from plexapi.audio import Track
from plexapi.video import Movie, Show

from plexutil.dto.tv_series_dto import TVSeriesDTO
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

    from plexapi.server import Playlist, PlexServer

    from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO
    from plexutil.dto.movie_dto import MovieDTO
    from plexutil.dto.song_dto import SongDTO


class PlexOps(Static):
    @staticmethod
    def set_server_settings(
        plex_server: PlexServer,
        library_preferences_dto: LibraryPreferencesDTO,
    ) -> None:
        """
        Sets Plex Server Settings

        Args:
            plex_server (plexapi.server.PlexServer): A Plex Server instance
            library_preferences_dto (LibraryPreferencesDTO): Library Preference


        Returns:
            None: This method does not return a value

        """
        server_settings = library_preferences_dto.plex_server_settings
        for setting_id, setting_value in server_settings.items():
            plex_server.settings.get(setting_id).set(setting_value)
        plex_server.settings.save()

    @staticmethod
    def get_music_playlist_entity(playlist: Playlist) -> MusicPlaylistEntity:
        """
        Maps a plexapi.server.Playlist to a MusicPlaylsitEntity

        Args:
            playlist (plexapi.server.Playlist): A plex playlist

        Returns:
            MusicPlaylistEntity: Mapped from playlist
        """
        return MusicPlaylistEntity(name=playlist.title)

    @staticmethod
    def get_song_entity(track: Track) -> SongEntity:
        """
        Maps a plexapi.server.Track to a SongEntity

        Args:
            track (plexapi.server.Track): A plex track

        Returns:
            MusicPlaylistEntity
        """
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
    def validate_local_files(
        plex_files: list[Track] | list[Show] | list[Movie],
        locations: list[Path],
    ) -> None:
        """
        Verifies that all local files match the provided plex tracks
        in the locations indicated

        Args:
            tracks ([plexapi.audio.Track]): plexapi tracks.
            locations ([Path]): local file locations.

        Returns:
            None: This method does not return a value

        Raises:
            LibraryIllegalStateError: if local files do not match plex files
            LibraryOpError: If plex_file type is not supported
        """
        if all(isinstance(plex_file, Track) for plex_file in plex_files):
            songs = PathOps.get_local_songs(locations)
            _, unknown = PlexOps.filter_tracks(
                cast(list[Track], plex_files), songs
            )
        elif all(isinstance(plex_file, Show) for plex_file in plex_files):
            tv = PathOps.get_local_tv(locations)
            _, unknown = PlexOps.filter_series(
                cast(list[Show], plex_files), tv
            )
        elif all(isinstance(plex_file, Movie) for plex_file in plex_files):
            movies = PathOps.get_local_movies(locations)
            _, unknown = PlexOps.filter_movies(
                cast(list[Movie], plex_files), movies
            )
        else:
            description = "Expected to find Tracks, Movies or Shows"
            raise ValueError(description)

        if unknown:
            description = "These local files are unknown to the plex server:\n"
            for u in unknown:
                description = description + f"-> {u!s}\n"

            raise LibraryIllegalStateError(description)

    @staticmethod
    def filter_tracks(
        tracks: list[Track],
        songs: list[SongDTO],
    ) -> tuple[list[Track], list[SongDTO]]:
        """
        Filters the provided tracks with the provided songs

        Args:
            tracks ([plexapi.audio.Track]): plexapi tracks
            songs ([SongDTO]): SongDTOs to match against tracks

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
    def filter_series(
        shows: list[Show],
        series: list[TVSeriesDTO],
    ) -> tuple[list[Show], list[TVSeriesDTO]]:
        """
        Filters the provided Shows with the provided episodes

        Args:
            shows ([plexapi.video.Show]): plexapi shows
            episodes ([TVSeriesDTO]): TVSeriesDTOs to match against shows

        Returns:
            A tuple of:
            1) Shows that match the provided series
            2) Series that did not match to any Shows
        """
        plex_shows = []
        filtered_series = []
        unknown_series = []

        for show in shows:
            plex_show = TVSeriesDTO(name=show.title, year=cast(int, show.year))

            plex_shows.append(plex_show)

        for a_series in series:
            if a_series not in plex_shows:
                unknown_series.append(a_series)
            else:
                filtered_series.append(a_series)

        return filtered_series, unknown_series

    @staticmethod
    def filter_movies(
        plex_movies: list[Movie], movies: list[MovieDTO]
    ) -> tuple[list[Movie], list[MovieDTO]]:
        """
        Filters the provided Plex Movies with the provided Movies

        Args:
            plex_movies ([plexapi.video.Movie]): plexapi movies
            movies ([MovieDTO]): MovieDTOs to match against plex movies

        Returns:
            A tuple of:
            1) Plex movies that match the provided movies
            2) Movies that did not match to any Plex Movies
        """
        filtered_movies = []
        unknown_movies = []

        for movie in movies:
            found = [x for x in plex_movies if movie.name == x.title]
            if found:
                found = found[0]
                filtered_movies.append(found)
            else:
                unknown_movies.append(movie)

        return filtered_movies, unknown_movies

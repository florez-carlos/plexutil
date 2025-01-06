from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from plexapi.audio import Audio
    from plexapi.server import PlexServer

    from plexutil.dto.bootstrap_paths_dto import BootstrapPathsDTO
    from plexutil.dto.music_playlist_dto import MusicPlaylistDTO
    from plexutil.dto.song_dto import SongDTO

from plexutil.core.library import Library
from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO
from plexutil.enums.agent import Agent
from plexutil.enums.language import Language
from plexutil.enums.library_name import LibraryName
from plexutil.enums.library_type import LibraryType
from plexutil.enums.scanner import Scanner
from plexutil.exception.library_op_error import LibraryOpError
from plexutil.mapper.music_playlist_mapper import MusicPlaylistMapper
from plexutil.mapper.song_mapper import SongMapper
from plexutil.model.music_playlist_entity import MusicPlaylistEntity
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.service.song_music_playlist_composite_service import (
    SongMusicPlaylistCompositeService,
)
from plexutil.util.plex_ops import PlexOps


class Playlist(Library):
    def __init__(
        self,
        plex_server: PlexServer,
        locations: list[Path],
        playlist_name: str,
        music_playlists_dto: list[MusicPlaylistDTO],
        name: str = LibraryName.MUSIC.value,
        library_type: LibraryType = LibraryType.MUSIC_PLAYLIST,
        language: Language = Language.ENGLISH_US,
    ) -> None:
        super().__init__(
            plex_server,
            name,
            library_type,
            Agent.MUSIC,
            Scanner.MUSIC,
            locations,
            language,
            LibraryPreferencesDTO(),
        )
        self.playlist_name = playlist_name
        self.music_playlists_dto = music_playlists_dto

    def create(self) -> None:
        self.probe_library()

        tracks = self.get_section().searchTracks()

        for music_playlist_dto in self.music_playlists_dto:
            songs = music_playlist_dto.songs
            playlist_name = music_playlist_dto.name

            debug = (
                f"Creating a Playlist: \n"
                f"Playlist Name: {playlist_name} \n"
                f"Library Name: {self.name}\n"
                f"Song Count: {len(songs)}\n"
                f"Type: {self.library_type.value}\n"
                f"Agent: {self.agent.value}\n"
                f"Scanner: {self.scanner.value}\n"
                f"Locations: {self.locations!s}\n"
                f"Language: {self.language.value}\n"
            )
            PlexUtilLogger.get_logger().debug(debug)

            if self.exists():
                info = (
                    f"Playlist {playlist_name} for "
                    f"Library {self.name} of "
                    f"type {self.library_type} already exists\n"
                    f"Skipping...\n"
                )
                PlexUtilLogger.get_logger().info(info)
                continue

            self.get_section().createPlaylist(
                title=playlist_name,
                items=tracks,
            )

    def query(self) -> list[Audio]:
        return self.get_section().playlist(self.playlist_name).items()

    def delete(self) -> None:
        plex_playlists = self.get_section().playlists()

        playlist_names = [x.name for x in self.music_playlists_dto]
        debug = (
            "Deleting music playlists: \n"
            f"Playlists: {playlist_names!s}\n"
            f"Location: {self.locations!s}\n"
            f"Playlists available in server: {plex_playlists}"
        )
        PlexUtilLogger.get_logger().debug(debug)

        for plex_playlist in plex_playlists:
            if plex_playlist.title in playlist_names:
                plex_playlist.delete()

    def exists(self) -> bool:
        plex_playlists = self.get_section().playlists()

        debug = (
            f"Checking playlists exist\n"
            f"Requested: {self.music_playlists_dto!s}\n"
            f"In server: {plex_playlists}\n"
        )
        PlexUtilLogger.get_logger().debug(debug)

        if not plex_playlists or not self.music_playlists_dto:
            return False

        all_exist = True
        for playlist_dto in self.music_playlists_dto:
            playlist_name = playlist_dto.name
            if playlist_name in [x.title for x in plex_playlists]:
                continue
            all_exist = False
            break

        debug = f"All exist: {all_exist}"
        PlexUtilLogger.get_logger().debug(debug)

        return all_exist

    def export_music_playlists(
        self,
        bootstrap_paths_dto: BootstrapPathsDTO,
    ) -> None:
        service = SongMusicPlaylistCompositeService(
            bootstrap_paths_dto.plexutil_playlists_db_dir
        )
        song_mapper = SongMapper()
        music_playlist_mapper = MusicPlaylistMapper()

        section = self.get_section()
        plex_playlists = section.playlists()

        to_save = []
        for plex_playlist in plex_playlists:
            music_playlist_dto = music_playlist_mapper.get_dto(
                PlexOps.get_music_playlist_entity(plex_playlist)
            )

            for track in plex_playlist.items():
                song_dto = PlexOps.get_song_dto(track)
                music_playlist_dto.songs.append(song_dto)

            to_save.append(music_playlist_dto)

        service.add_many(to_save)

    def import_music_playlists(
        self,
        bootstrap_paths_dto: BootstrapPathsDTO,
    ) -> None:
        op_type = "IMPORT"
        playlist_names = [x.name for x in self.music_playlists_dto]

        self.probe_library()

        tracks = self.get_section().searchTracks()
        plex_track_dict = {}
        plex_playlist = []

        info = (
            "Creating playlist library: \n",
            f"Playlists: {playlist_names}\n",
        )

        PlexUtilLogger.get_logger().info(info)

        entities = [MusicPlaylistEntity(name=x) for x in playlist_names]
        service = SongMusicPlaylistCompositeService(
            bootstrap_paths_dto.plexutil_playlists_db_dir
        )
        playlists = service.get(entities)

        for track in tracks:
            song_dto = PlexOps.get_song_dto(track)
            plex_track_dict[song_dto.name] = track

        for playlist in playlists:
            playlist_name = playlist.name
            songs = playlist.songs

            for song in songs:
                song_name = song.name

                if plex_track_dict.get(song_name) is None:
                    description = (
                        f"File in music playlist: '{song_name}' "
                        "does not exist in server"
                    )
                    raise LibraryOpError(
                        op_type=op_type,
                        library_type=self.library_type,
                        description=description,
                    )

                plex_playlist.append(plex_track_dict.get(song_name))

            self.get_section().createPlaylist(
                title=playlist_name,
                items=plex_playlist,
            )
            plex_playlist = []

    def delete_songs(self, songs: list[SongDTO]) -> None:
        """
        Matches provided Songs to Plex Tracks in the playlist and deletes
        the tracks from the playlist

        Args:
            songs ([SongDTO]): Songs to be removed, these songs are first
            matched to existing Tracks in the Plex library

        Returns:
            None: This method does not return a value
        """
        playlist = self.get_section().playlist(self.playlist_name)
        playlist_tracks = playlist.items()
        known, _ = PlexOps.filter_tracks(playlist_tracks, songs)
        playlist.removeItems(known)

    def add_songs(self, songs: list[SongDTO]) -> None:
        """
        Matches provided Songs to Plex Tracks in the library and adds
        the tracks to the plex playlist

        Args:
            songs ([SongDTO]): Songs to be added, these songs are first
            matched to existing Tracks in the Plex library

        Returns:
            None: This method does not return a value
        """
        playlist = self.get_section().playlist(self.playlist_name)
        library_tracks = self.get_section().searchTracks()
        known, _ = PlexOps.filter_tracks(library_tracks, songs)
        playlist.addItems(known)

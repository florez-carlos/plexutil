from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

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

        library = self.get_library()
        tracks = library.searchTracks()

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

            library.createPlaylist(
                title=playlist_name,
                items=tracks,
            )

    def delete(self) -> None:
        library = self.get_library()
        plex_playlists = library.playlists()

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
        library = self.get_library()
        plex_playlists = library.playlists()

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
        library = self.get_library()
        service = SongMusicPlaylistCompositeService(
            bootstrap_paths_dto.config_dir / "playlists.db"
        )
        song_mapper = SongMapper()
        music_playlist_mapper = MusicPlaylistMapper()

        plex_playlists = library.playlists()

        to_save = []
        for plex_playlist in plex_playlists:
            music_playlist_dto = music_playlist_mapper.get_dto(
                PlexOps.get_music_playlist_entity(plex_playlist)
            )

            for track in plex_playlist.items():
                song_dto = song_mapper.get_dto(PlexOps.get_song_entity(track))
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

        library = self.get_library()
        tracks = library.searchTracks()
        plex_track_dict = {}
        plex_playlist = []

        info = (
            "Creating playlist library: \n",
            f"Playlists: {playlist_names}\n",
        )

        PlexUtilLogger.get_logger().info(info)

        entities = [MusicPlaylistEntity(name=x) for x in playlist_names]
        service = SongMusicPlaylistCompositeService(
            bootstrap_paths_dto.config_dir / "playlists.db"
        )
        playlists = service.get(entities)

        for track in tracks:
            song_entity = PlexOps.get_song_entity(track)
            plex_track_dict[str(song_entity.name)] = track

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

            library.createPlaylist(
                title=playlist_name,
                items=plex_playlist,
            )
            plex_playlist = []

    def delete_songs(self, songs: list[SongDTO]) -> None:
        library = self.get_library()
        playlist = library.playlist(self.name)
        tracks = playlist.items()
        known, _ = PlexOps.filter_tracks(tracks, songs)
        playlist.removeItems(known)

    def add_songs(self, songs: list[SongDTO]) -> None:
        library = self.get_library()
        library_tracks = library.searchTracks()
        known, _ = PlexOps.filter_tracks(library_tracks, songs)
        playlist = library.playlist(self.playlist_name)
        playlist.addItems(known)

from pathlib import Path

from plexapi.server import PlexServer

from plexutil.core.library import Library
from plexutil.dto.bootstrap_paths_dto import BootstrapPathsDTO
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
from plexutil.util.path_ops import PathOps
from plexutil.util.plex_ops import PlexOps


class Playlist(Library):
    def __init__(
        self,
        plex_server: PlexServer,
        locations: list[Path],
        name: str = LibraryName.MUSIC.value,
        library_type: LibraryType = LibraryType.MUSIC_PLAYLIST,
        playlist_names: list[str] = [],
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
        self.playlist_names = playlist_names

    def delete(self) -> None:
        info = (
            "Deleting music playlists: \n"
            f"Playlists: {self.playlist_names}\n"
            f"Location: {self.locations!s}\n"
        )
        PlexUtilLogger.get_logger().info(info)

        playlist_type = LibraryType.MUSIC_PLAYLIST

        if self.library_type is LibraryType.MOVIE:
            pass

        playlists = self.plex_server.playlists(playlistType=playlist_type)

        debug = f"Playlists available in server: {playlists}"
        PlexUtilLogger.get_logger().debug(debug)

        for playlist in playlists:
            if playlist.title in self.playlist_names:
                playlist.delete()

    def exists(self) -> bool:
        playlist_type = LibraryType.MUSIC_PLAYLIST

        if self.library_type is LibraryType.MOVIE:
            pass

        playlists = self.plex_server.playlists(playlistType=playlist_type)

        debug = (
            f"Checking playlists exist\n"
            f"Requested: {self.playlist_names}\n"
            f"In server: {playlists}\n"
        )
        PlexUtilLogger.get_logger().debug(debug)

        if not playlists or not self.playlist_names:
            return False

        all_exist = True
        for playlist_name in self.playlist_names:
            if playlist_name in [x.title for x in playlists]:
                continue
            all_exist = False

        debug = f"All exist: {all_exist}"
        PlexUtilLogger.get_logger().debug(debug)

        return all_exist

    def export_music_playlists(
        self,
        bootstrap_paths_dto: BootstrapPathsDTO,
    ) -> None:
        service = SongMusicPlaylistCompositeService(
            bootstrap_paths_dto.config_dir / "playlists.db"
        )
        song_mapper = SongMapper()
        music_playlist_mapper = MusicPlaylistMapper()

        plex_playlists = self.plex_server.playlists(
            LibraryType.MUSIC_PLAYLIST,
        )

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
        op_type = "CREATE"
        self.plex_server.library.section(self.name).update()

        local_track_count = len(PathOps.get_local_files(self.locations))

        info = (
            "Checking server track count "
            f"meets expected "
            f"count: {local_track_count!s}\n"
        )
        PlexUtilLogger.get_logger().info(info)
        self.poll(10, local_track_count, 10)

        tracks = self.plex_server.library.section(
            self.name,
        ).searchTracks()
        plex_track_dict = {}
        plex_playlist = []

        info = (
            "Creating playlist library: \n",
            f"Playlists: {self.playlist_names}\n",
        )

        PlexUtilLogger.get_logger().info(info)

        entities = [MusicPlaylistEntity(name=x) for x in self.playlist_names]
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

            self.plex_server.createPlaylist(
                title=playlist_name,
                items=plex_playlist,
            )
            plex_playlist = []

    def create(self) -> None:
        raise NotImplementedError

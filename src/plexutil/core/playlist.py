from pathlib import Path

from plexapi.server import PlexServer

from plexutil.core.library import Library
from plexutil.dto.library_preferences_dto import LibraryPreferencesDTO
from plexutil.dto.music_playlist_file_dto import MusicPlaylistFileDTO
from plexutil.enums.agent import Agent
from plexutil.enums.language import Language
from plexutil.enums.library_name import LibraryName
from plexutil.enums.library_type import LibraryType
from plexutil.enums.scanner import Scanner
from plexutil.exception.library_op_error import LibraryOpError
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.util.path_ops import PathOps


class Playlist(Library):
    def __init__(
        self,
        plex_server: PlexServer,
        location: Path,
        language: Language,
        music_playlist_file_dto: MusicPlaylistFileDTO,
    ) -> None:
        super().__init__(
            plex_server,
            LibraryName.MUSIC,
            LibraryType.MUSIC,
            Agent.MUSIC,
            Scanner.MUSIC,
            location,
            language,
            LibraryPreferencesDTO({}, {}, {}, {}),
        )
        self.music_playlist_file_dto = music_playlist_file_dto

    def create(self) -> None:
        op_type = "CREATE"
        tracks = self.plex_server.library.section(
            self.name.value,
        ).searchTracks()
        plex_track_dict = {}
        plex_playlist = []

        playlist_names = [
            x.name for x in self.music_playlist_file_dto.playlists
        ]

        info = "Creating playlist library: \n" f"Playlists: {playlist_names}\n"

        PlexUtilLogger.get_logger().info(info)

        info = (
            "Checking server track count "
            f"meets expected "
            f"count: {self.music_playlist_file_dto.track_count!s}\n"
        )
        PlexUtilLogger.get_logger().info(info)
        self.poll(10, self.music_playlist_file_dto.track_count, 10)

        playlists = self.music_playlist_file_dto.playlists

        for track in tracks:
            plex_track_absolute_location = track.locations[0]
            plex_track_path = PathOps.get_path_from_str(
                plex_track_absolute_location,
            )
            plex_track_full_name = plex_track_path.name
            plex_track_name = plex_track_full_name.rsplit(".", 1)[0]
            plex_track_dict[plex_track_name] = track

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

    def delete(self) -> None:
        playlist_names = [
            x.name for x in self.music_playlist_file_dto.playlists
        ]

        info = (
            "Deleting music playlists: \n"
            f"Playlists: {playlist_names}\n"
            f"Location: {self.location!s}\n"
        )
        PlexUtilLogger.get_logger().info(info)

        server_playlists = self.plex_server.playlists(playlistType="audio")

        debug = f"Playlists available in server: {server_playlists}"
        PlexUtilLogger.get_logger().debug(debug)

        for playlist in server_playlists:
            if playlist.title in playlist_names:
                playlist.delete()

    def exists(self) -> bool:
        playlist_names = [
            x.name for x in self.music_playlist_file_dto.playlists
        ]
        playlists = self.plex_server.playlists(playlistType="audio")

        debug = (
            f"Checking playlists exist\n"
            f"Requested: {playlist_names}\n"
            f"In server: {playlists}\n"
        )
        PlexUtilLogger.get_logger().debug(debug)

        if not playlists or not playlist_names:
            return False

        all_exist = True
        for playlist_name in playlist_names:
            if playlist_name in [x.title for x in playlists]:
                continue
            all_exist = False

        debug = f"All exist: {all_exist}"
        PlexUtilLogger.get_logger().debug(debug)

        return all_exist

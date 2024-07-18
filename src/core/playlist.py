from pathlib import Path

from plexapi.server import PlexServer
from throws import throws

from src.core.library import Library
from src.dto.library_preferences_dto import LibraryPreferencesDTO
from src.dto.music_playlist_file_dto import MusicPlaylistFileDTO
from src.enum.agent import Agent
from src.enum.language import Language
from src.enum.library_name import LibraryName
from src.enum.library_type import LibraryType
from src.enum.scanner import Scanner
from src.exception.library_op_error import LibraryOpError
from src.exception.library_poll_timeout_error import LibraryPollTimeoutError
from src.exception.library_unsupported_error import LibraryUnsupportedError
from src.util.path_ops import PathOps


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

    @throws(LibraryPollTimeoutError, LibraryOpError, LibraryUnsupportedError)
    def create(self) -> None:
        op_type = "CREATE"
        tracks = self.plex_server.library.section(
            self.name.value,
        ).searchTracks()
        plex_track_dict = {}
        plex_playlist = []

        print(
            "Checking server track count meets expected count: "
            + str(self.music_playlist_file_dto.track_count),
        )
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
                        "File in music playlist: '"
                        + song_name
                        + "' does not exist in server"
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

        for playlist in self.plex_server.playlists(playlistType="audio"):
            if playlist.title in playlist_names:
                playlist.delete()

    def exists(self) -> bool:
        playlist_names = [
            x.name for x in self.music_playlist_file_dto.playlists
        ]
        playlists = self.plex_server.playlists(playlistType="audio")

        if not playlists or not playlist_names:
            return False

        return all(playlist.title in playlist_names for playlist in playlists)

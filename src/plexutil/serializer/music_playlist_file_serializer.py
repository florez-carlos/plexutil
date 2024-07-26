from typing import cast

from plexutil.dto.music_playlist_dto import MusicPlaylistDTO
from plexutil.dto.music_playlist_file_dto import MusicPlaylistFileDTO
from plexutil.dto.song_dto import SongDTO
from plexutil.enums.file_type import FileType
from plexutil.serializer.serializable import Serializable
from plexutil.serializer.serializer import Serializer


class MusicPlaylistFileSerializer(Serializer):
    def to_json(self, serializable: Serializable) -> dict:
        if not isinstance(serializable, MusicPlaylistFileDTO):
            description = "Expected MusicPlaylistFileDTO"
            raise TypeError(description)
        music_playlist_file_dto = cast(MusicPlaylistFileDTO, serializable)
        music_playlist_file = {
            "trackCount": music_playlist_file_dto.track_count,
            "playlists": [],
        }

        playlists_dict = []
        songs_dict = []
        playlists = music_playlist_file_dto.playlists

        for playlist in playlists:
            name = playlist.name
            songs = playlist.songs
            for song in songs:
                songs_dict.append(  # noqa: PERF401
                    {"fileName": song.name + "." + song.extension.value},
                )

            playlists_dict.append({"playlistName": name, "songs": songs_dict})

        music_playlist_file["playlists"] = playlists_dict

        return music_playlist_file

    def to_dto(self, json_dict: dict) -> MusicPlaylistFileDTO:
        track_count = json_dict["trackCount"]
        playlists = json_dict["playlists"]
        playlists_dto = []

        for playlist in playlists:
            playlist_name = playlist["playlistName"]
            playlist_songs = []
            songs = playlist["songs"]
            for song in songs:
                file_name = song["fileName"]

                dot_position = file_name.rfind(".")
                song_name = file_name[:dot_position]
                song_extension = file_name[dot_position + 1 :]

                song_dto = SongDTO(
                    song_name,
                    FileType.get_file_type_from_str(song_extension),
                )
                playlist_songs.append(song_dto)

            playlist_dto = MusicPlaylistDTO(playlist_name, playlist_songs)
            playlists_dto.append(playlist_dto)

        return MusicPlaylistFileDTO(track_count, playlists_dto)

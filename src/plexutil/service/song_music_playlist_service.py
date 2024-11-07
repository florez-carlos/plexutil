from __future__ import annotations


from plexutil.model.song_music_playlist_entity import SongMusicPlaylistEntity
from plexutil.static import Static



class SongMusicPlaylistService(Static):

    @staticmethod
    def add_many_song_playlist(
        song_playlists: list[SongMusicPlaylistEntity],
    ) -> None:
        bulk = [
            (song_playlist.playlist, song_playlist.song)
            for song_playlist in song_playlists
        ]

        SongMusicPlaylistEntity.insert_many(
            bulk,
            fields=[
                SongMusicPlaylistEntity.playlist,
                SongMusicPlaylistEntity.song,
            ],
        ).execute()

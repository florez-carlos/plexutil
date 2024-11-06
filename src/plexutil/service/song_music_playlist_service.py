from __future__ import annotations

from typing import TYPE_CHECKING

from plexutil.model.song_music_playlist_entity import SongMusicPlaylistEntity

if TYPE_CHECKING:
    from plexutil.util.database_manager import DatabaseManager


class SongMusicPlaylistService:
    def __init__(self, database_manager: DatabaseManager) -> None:
        self.database_manager = database_manager

    def add_many_song_playlist(
        self, song_playlists: list[SongMusicPlaylistEntity]
    ) -> None:
        bulk = [
            (song_playlist.playlist, song_playlist.song)
            for song_playlist in song_playlists
        ]

        with self.database_manager:
            SongMusicPlaylistEntity.insert_many(
                bulk,
                fields=[
                    SongMusicPlaylistEntity.playlist,
                    SongMusicPlaylistEntity.song,
                ],
            ).execute()

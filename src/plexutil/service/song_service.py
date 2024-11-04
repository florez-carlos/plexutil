from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plexutil.dto.song_dto import SongDTO
    from plexutil.util.database_manager import DatabaseManager

from plexutil.model.song_entity import SongEntity


class SongService:
    def __init__(self, database_manager: DatabaseManager) -> None:
        self.database_manager = database_manager

    def add_many_song(self, songs: list[SongDTO]) -> None:
        bulk = [(song.name, song.extension.value) for song in songs]

        with self.database_manager:
            SongEntity.insert_many(
                bulk,
                fields=[SongEntity.name, SongEntity.extension],
            ).execute()

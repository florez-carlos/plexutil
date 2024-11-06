from __future__ import annotations

from typing import TYPE_CHECKING

from plexutil.model.song_entity import SongEntity

if TYPE_CHECKING:
    from uuid import UUID

    from plexutil.util.database_manager import DatabaseManager


class SongService:
    def __init__(self, database_manager: DatabaseManager) -> None:
        self.database_manager = database_manager

    def get_id(self, song: SongEntity) -> UUID:
        return (
            SongEntity.select()
            .where(
                (SongEntity.name == song.name)
                & (SongEntity.extension == song.extension)
            )
            .get()
        )

    def get_song(self, uuid: UUID) -> SongEntity:
        return SongEntity.select().where(SongEntity.id == uuid).get()

    def add_song(self, song: SongEntity) -> None:
        song.save(force_insert=True)

    def add_many_song(self, songs: list[SongEntity]) -> None:
        bulk = [(song.name, song.extension) for song in songs]

        with self.database_manager:
            SongEntity.insert_many(
                bulk,
                fields=[SongEntity.name, SongEntity.extension],
            ).execute()

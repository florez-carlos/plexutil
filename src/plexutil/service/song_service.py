from __future__ import annotations

from typing import TYPE_CHECKING

from plexutil.model.song_entity import SongEntity
from plexutil.static import Static

if TYPE_CHECKING:
    from uuid import UUID


class SongService(Static):
    @staticmethod
    def get_id(song: SongEntity) -> UUID:
        return (
            SongEntity.select()
            .where(
                (SongEntity.name == song.name)
                & (SongEntity.extension == song.extension)
            )
            .get()
        )

    @staticmethod
    def get_song(uuid: UUID) -> SongEntity:
        return SongEntity.select().where(SongEntity.id == uuid).get()

    @staticmethod
    def add_song(song: SongEntity) -> None:
        song.save(force_insert=True)

    @staticmethod
    def add_many_song(songs: list[SongEntity]) -> None:
        bulk = [(song.name, song.extension) for song in songs]

        SongEntity.insert_many(
            bulk,
            fields=[SongEntity.name, SongEntity.extension],
        ).execute()

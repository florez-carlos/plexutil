from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from plexutil.model.song_entity import SongEntity
from plexutil.service.db_manager import db_manager

if TYPE_CHECKING:
    from uuid import UUID


class SongService:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def get_id(self, entity: SongEntity) -> UUID:
        with db_manager(self.db_path, [SongEntity]):
            return (
                SongEntity.select()
                .where(
                    (SongEntity.name == entity.name)
                    & (SongEntity.extension == entity.extension)
                )
                .get()
            )

    def get(self, uuid: UUID) -> SongEntity:
        with db_manager(self.db_path, [SongEntity]):
            return SongEntity.select().where(SongEntity.id == uuid).get()

    def get_many(self, entities: list[SongEntity]) -> list[SongEntity]:
        with db_manager(self.db_path, [SongEntity]):
            names = [x.name for x in entities]
            extensions = [x.extension for x in entities]
            return (
                SongEntity.select()
                .where(
                    (SongEntity.name.in_(names))
                    & (SongEntity.extension.in_(extensions))
                )
                .get()
            )

    def add(self, entity: SongEntity) -> int:
        with db_manager(self.db_path, [SongEntity]):
            return entity.save(force_insert=True)

    def add_many(self, entities: list[SongEntity]) -> int:
        with db_manager(self.db_path, [SongEntity]):
            bulk = [(song.name, song.extension) for song in entities]

            return SongEntity.insert_many(
                bulk,
                fields=[SongEntity.name, SongEntity.extension],
            ).execute()

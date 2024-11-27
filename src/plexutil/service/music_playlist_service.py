from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from plexutil.model.music_playlist_entity import MusicPlaylistEntity
from plexutil.service.db_manager import db_manager

if TYPE_CHECKING:
    from uuid import UUID


class MusicPlaylistService:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def get_id(self, entity: MusicPlaylistEntity) -> UUID:
        with db_manager(self.db_path, [MusicPlaylistEntity]):
            return (
                MusicPlaylistEntity.select()
                .where(
                    MusicPlaylistEntity.name == entity.name,
                )
                .get()
            )

    def get(self, uuid: UUID) -> MusicPlaylistEntity:
        with db_manager(self.db_path, [MusicPlaylistEntity]):
            return (
                MusicPlaylistEntity.select()
                .where(MusicPlaylistEntity.id == uuid)
                .get()
            )

    def get_many(
        self, entities: list[MusicPlaylistEntity]
    ) -> list[MusicPlaylistEntity]:
        with db_manager(self.db_path, [MusicPlaylistEntity]):
            names = [x.name for x in entities]
            return (
                MusicPlaylistEntity.select()
                .where(MusicPlaylistEntity.name.in_(names))
                .get()
            )

    def add(self, entity: MusicPlaylistEntity) -> int:
        with db_manager(self.db_path, [MusicPlaylistEntity]):
            return entity.save(force_insert=True)

    def add_many(self, entities: list[MusicPlaylistEntity]) -> int:
        with db_manager(self.db_path, [MusicPlaylistEntity]):
            bulk = [(entity.name,) for entity in entities]

            return MusicPlaylistEntity.insert_many(
                bulk,
                fields=[MusicPlaylistEntity.name],
            ).execute()

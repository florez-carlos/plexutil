from __future__ import annotations

from pathlib import Path

from plexutil.model.music_playlist_entity import MusicPlaylistEntity
from plexutil.service.db_manager import db_manager


class MusicPlaylistService:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def get(self, entity: MusicPlaylistEntity) -> MusicPlaylistEntity:
        with db_manager(self.db_path, [MusicPlaylistEntity]):
            return (
                MusicPlaylistEntity.select()
                .where(
                    MusicPlaylistEntity.name == entity.name,
                )
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

    def save(self, entity: MusicPlaylistEntity) -> MusicPlaylistEntity:
        force_insert = False if self.exists() else True

        with db_manager(self.db_path, [MusicPlaylistEntity]):
            entity.save(force_insert=force_insert)
            return entity

    def exists(self) -> bool:
        with db_manager(self.db_path, [MusicPlaylistEntity]):
            return MusicPlaylistEntity.select().exists()

    def add_many(self, entities: list[MusicPlaylistEntity]) -> None:
        with db_manager(self.db_path, [MusicPlaylistEntity], is_atomic=True):
            bulk = [(entity.name,) for entity in entities]
            for idx in range(0, len(bulk), 100):
                MusicPlaylistEntity.insert_many(
                    bulk[idx : idx + 100],
                    fields=[MusicPlaylistEntity.name],
                ).execute()

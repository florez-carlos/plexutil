from __future__ import annotations

from typing import TYPE_CHECKING

from plexutil.model.music_playlist_entity import MusicPlaylistEntity

if TYPE_CHECKING:
    from uuid import UUID

    from plexutil.util.database_manager import DatabaseManager


class MusicPlaylistService:
    def __init__(self, database_manager: DatabaseManager) -> None:
        self.database_manager = database_manager

    def get_id(self, playlist: MusicPlaylistEntity) -> UUID:
        return (
            MusicPlaylistEntity.select()
            .where(
                MusicPlaylistEntity.name == playlist.name,
            )
            .get()
        )

    def get_playlist(self, uuid: UUID) -> MusicPlaylistEntity:
        return (
            MusicPlaylistEntity.select()
            .where(MusicPlaylistEntity.id == uuid)
            .get()
        )

    def add_playlist(self, playlist: MusicPlaylistEntity) -> None:
        playlist.save(force_insert=True)

    def add_many_playlist(self, playlists: list[MusicPlaylistEntity]) -> None:
        bulk = [(playlist.name) for playlist in playlists]

        with self.database_manager:
            MusicPlaylistEntity.insert_many(
                bulk,
                fields=[MusicPlaylistEntity.name],
            ).execute()

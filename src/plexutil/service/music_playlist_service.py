from __future__ import annotations

from typing import TYPE_CHECKING

from plexutil.model.music_playlist_entity import MusicPlaylistEntity
from plexutil.static import Static

if TYPE_CHECKING:
    from uuid import UUID


class MusicPlaylistService(Static):
    @staticmethod
    def get_id(playlist: MusicPlaylistEntity) -> UUID:
        return (
            MusicPlaylistEntity.select()
            .where(
                MusicPlaylistEntity.name == playlist.name,
            )
            .get()
        )

    @staticmethod
    def get_playlist(uuid: UUID) -> MusicPlaylistEntity:
        return (
            MusicPlaylistEntity.select()
            .where(MusicPlaylistEntity.id == uuid)
            .get()
        )

    @staticmethod
    def add_playlist(playlist: MusicPlaylistEntity) -> None:
        playlist.save(force_insert=True)

    @staticmethod
    def add_many_playlist(playlists: list[MusicPlaylistEntity]) -> None:
        bulk = [(playlist.name,) for playlist in playlists]

        MusicPlaylistEntity.insert_many(
            bulk,
            fields=[MusicPlaylistEntity.name],
        ).execute()

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import TracebackType

    from dto.bootstrap_paths_dto import BootstrapPathsDTO

from model.music_playlist_entity import MusicPlaylistEntity
from model.song_entity import SongEntity
from model.song_music_playlist_entity import SongMusicPlaylistEntity
from peewee import SqliteDatabase

from plexutil.exception.database_connection_error import (
    DatabaseConnectionError,
)


class DatabaseManager:
    def __init__(self, bootstrap_paths_dto: BootstrapPathsDTO) -> None:
        self.db = SqliteDatabase(
            bootstrap_paths_dto.config_dir / "plexutil.db"
        )

    def __enter__(self) -> SqliteDatabase:
        self.db.connect()
        return self.db

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.db.close()
        if exc_type is not None:
            raise DatabaseConnectionError(exc_val)

    def initialize_db(self) -> None:
        with self as db:  # Use the context manager
            db.create_tables(
                [SongEntity, SongMusicPlaylistEntity, MusicPlaylistEntity],
                safe=True,
            )  # Create tables if they don't exist

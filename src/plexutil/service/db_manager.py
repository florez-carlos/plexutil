from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from peewee import SqliteDatabase


@contextmanager
def db_manager(
    db_path: Path, entities: list, is_atomic: bool = False
) -> Generator[SqliteDatabase, None, None]:
    if is_atomic:
        with SqliteDatabase(
            db_path, pragmas={"foreign_keys": 1}
        ).atomic() as db:
            db.bind(entities)
            db.create_tables(entities)
            yield db
    else:
        with SqliteDatabase(db_path, pragmas={"foreign_keys": 1}) as db:
            db.bind(entities)
            db.create_tables(entities)
            yield db

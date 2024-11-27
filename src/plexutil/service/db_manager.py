from contextlib import contextmanager
from pathlib import Path
from peewee import Model, SqliteDatabase

@contextmanager
def db_manager(db_path: Path, entities: list):
    with SqliteDatabase(
        db_path, 
        pragmas={"foreign_keys": 1}
    ) as db:
        db.bind(entities)
        db.create_tables(entities)
        yield db

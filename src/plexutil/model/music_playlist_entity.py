import uuid

from peewee import Model, SqliteDatabase, TextField, UUIDField

db = SqliteDatabase("plexutil.db")


class MusicPlaylistEntity(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = TextField(null=False)

    class Meta:
        table_name = "music_playlist"
        database = db
        indexes = ((("name",), True),)

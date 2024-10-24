import uuid

from peewee import Model, SqliteDatabase, TextField, UUIDField

db = SqliteDatabase("plexutil.db")


class SongEntity(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = TextField(null=False)
    extension = TextField(null=False)

    class Meta:
        table_name = "music_song"
        database = db
        indexes = ((("name", "extension"), True),)

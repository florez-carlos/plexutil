import uuid

from peewee import Model, TextField, UUIDField


class SongEntity(Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = TextField(null=False)
    extension = TextField(null=False)

    class Meta:
        table_name = "music_song"
        indexes = ((("name", "extension"), True),)

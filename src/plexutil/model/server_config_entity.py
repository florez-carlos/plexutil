from peewee import IntegerField, Model, TextField


class ServerConfigEntity(Model):
    id = IntegerField(primary_key=True, default=1)
    host = TextField(null=False, default="localhost")
    port = IntegerField(null=False, default=32400)
    token = TextField(null=False)

    class Meta:
        table_name = "server_config"

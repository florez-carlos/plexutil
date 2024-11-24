from plexutil.model.server_config_entity import ServerConfigEntity
from plexutil.static import Static


class ServerConfigService(Static):
    @staticmethod
    def get() -> ServerConfigEntity:
        return ServerConfigEntity.select().get()

    @staticmethod
    def add(entity: ServerConfigEntity) -> int:
        return entity.save(force_insert=True)

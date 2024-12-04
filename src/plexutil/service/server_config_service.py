from pathlib import Path

from plexutil.model.server_config_entity import ServerConfigEntity
from plexutil.service.db_manager import db_manager


class ServerConfigService:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def get(self) -> ServerConfigEntity:
        with db_manager(self.db_path, [ServerConfigEntity]):
            return ServerConfigEntity.select().get()

    def get_many(
        self, entities: list[ServerConfigEntity]
    ) -> list[ServerConfigEntity]:
        with db_manager(self.db_path, [ServerConfigEntity]):
            hosts = [x.host for x in entities]
            ports = [x.port for x in entities]
            tokens = [x.token for x in entities]
            return (
                ServerConfigEntity.select()
                .where(
                    (ServerConfigEntity.host.in_(hosts))
                    & (ServerConfigEntity.port.in_(ports))
                    & (ServerConfigEntity.token.in_(tokens))
                )
                .get()
            )

    def save(self, entity: ServerConfigEntity) -> int:
        force_insert = False if self.exists() else True

        with db_manager(self.db_path, [ServerConfigEntity]):
            saved = entity.save(force_insert=force_insert)
            return saved

    def exists(self) -> bool:
        with db_manager(self.db_path, [ServerConfigEntity]):
            return ServerConfigEntity.select().exists()

    def add_many(self, entity: list[ServerConfigEntity]) -> int:
        raise NotImplementedError

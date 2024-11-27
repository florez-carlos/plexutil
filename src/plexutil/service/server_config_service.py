from pathlib import Path
from uuid import UUID

from plexutil.model.server_config_entity import ServerConfigEntity
from plexutil.service.db_manager import db_manager


class ServerConfigService:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def get_id(self) -> UUID:
        with db_manager(self.db_path, [ServerConfigEntity]):
            return ServerConfigEntity.select().get()

    def get(self, uuid: UUID) -> ServerConfigEntity:
        with db_manager(self.db_path, [ServerConfigEntity]):
            return (
                ServerConfigEntity.select()
                .where(ServerConfigEntity.id == uuid)
                .get()
            )

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

    def add(self, entity: ServerConfigEntity) -> int:
        with db_manager(self.db_path, [ServerConfigEntity]):
            return entity.save(force_insert=True)

    def add_many(self, entity: list[ServerConfigEntity]) -> int:
        raise NotImplementedError

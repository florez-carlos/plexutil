from plexutil.dto.server_config_dto import ServerConfigDTO
from plexutil.model.server_config_entity import ServerConfigEntity
from plexutil.static import Static


class ServerConfigMapper(Static):
    @staticmethod
    def get_dto(entity: ServerConfigEntity) -> ServerConfigDTO:
        return ServerConfigDTO(
            host=str(entity.host),
            port=int(entity.port),  # pyright: ignore
            token=str(entity.token),
        )

    @staticmethod
    def get_entity(dto: ServerConfigDTO) -> ServerConfigEntity:
        return ServerConfigEntity(
            host=dto.host, port=dto.port, token=dto.token
        )

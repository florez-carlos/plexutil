from plexutil.dto.server_config_dto import ServerConfigDTO
from plexutil.model.server_config_entity import ServerConfigEntity


class ServerConfigMapper:
    def get_dto(self, entity: ServerConfigEntity) -> ServerConfigDTO:
        return ServerConfigDTO(
            host=str(entity.host),
            port=int(entity.port),  # pyright: ignore
            token=str(entity.token),
        )

    def get_entity(self, dto: ServerConfigDTO) -> ServerConfigEntity:
        return ServerConfigEntity(
            host=dto.host, port=dto.port, token=dto.token
        )

from peewee import DoesNotExist, SqliteDatabase

from plexutil.dto.bootstrap_paths_dto import BootstrapPathsDTO
from plexutil.dto.server_config_dto import ServerConfigDTO
from plexutil.exception.server_config_error import ServerConfigError
from plexutil.mapper.server_config_mapper import ServerConfigMapper
from plexutil.model.server_config_entity import ServerConfigEntity
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.service.server_config_service import ServerConfigService


class ServerConfig:
    def __init__(
        self,
        bootstrap_paths_dto: BootstrapPathsDTO,
        server_config_dto: ServerConfigDTO,
    ):
        self.bootstrap_paths_dto = bootstrap_paths_dto
        self.server_config_dto = server_config_dto

    def setup(self) -> ServerConfigDTO:
        with SqliteDatabase(
            self.bootstrap_paths_dto.config_dir / "plexutil.db"
        ) as db:
            db.bind([ServerConfigEntity])

            db.create_tables(
                [ServerConfigEntity],
                safe=True,
            )
            try:
                return ServerConfigMapper.get_dto(ServerConfigService.get())
            except DoesNotExist:
                if not self.server_config_dto.token:
                    description = "No Plex Token has been supplied"
                    PlexUtilLogger.get_logger().error(description)
                    raise ServerConfigError(description)

                server_config_entity = ServerConfigMapper.get_entity(
                    self.server_config_dto,
                )

                description = (
                    "Plexutil Config does not exist. Creating:\n"
                    f"Host: {server_config_entity.host}"
                    f"Port: {server_config_entity.port}"
                    f"Token: {server_config_entity.token}"
                )
                PlexUtilLogger.get_logger().debug(description)
                ServerConfigService.add(server_config_entity)
                return ServerConfigMapper.get_dto(ServerConfigService.get())

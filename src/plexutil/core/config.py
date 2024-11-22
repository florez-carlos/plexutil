from peewee import DoesNotExist, SqliteDatabase

from plexutil.dto.bootstrap_paths_dto import BootstrapPathsDTO
from plexutil.dto.plex_config_dto import PlexConfigDTO
from plexutil.exception.plex_util_config_error import PlexUtilConfigError
from plexutil.mapper.plexutil_config_entity_mapper import PlexutilConfigEntityMapper
from plexutil.model.plexutil_config_entity import PlexUtilConfigEntity
from plexutil.plex_util_logger import PlexUtilLogger
from plexutil.service.plexutil_config_service import PlexUtilConfigService


class Config:

    def __init__(
        self,
        bootstrap_paths_dto: BootstrapPathsDTO,
        plex_config_dto: PlexConfigDTO,
    ):
        self.bootstrap_paths_dto = bootstrap_paths_dto
        self.plex_config_dto = plex_config_dto

    def setup(self) -> PlexConfigDTO:

        with SqliteDatabase(
            self.bootstrap_paths_dto.config_dir / "plexutil.db"
        ) as db:
            db.bind([PlexUtilConfigEntity])

            db.create_tables(
                [PlexUtilConfigEntity],
                safe=True,
            )
            try:
                return PlexutilConfigEntityMapper.get_dto(
                    PlexUtilConfigService.get_plexutil_config()
                )
            except DoesNotExist:
        
                if not self.plex_config_dto.token:
                    description = "No Plex Token has been supplied"
                    PlexUtilLogger.get_logger().error(description)
                    raise PlexUtilConfigError(description)

                plexutil_config_entity = PlexUtilConfigEntity(
                    host=self.plex_config_dto.host,
                    port=self.plex_config_dto.port,
                    token=self.plex_config_dto.token
                )
                description = (
                    "Plexutil Config does not exist. Creating:\n"
                    f"Host: {plexutil_config_entity.host}"
                    f"Port: {plexutil_config_entity.port}"
                    f"Token: {plexutil_config_entity.token}"
                )
                PlexUtilLogger.get_logger().debug(description)
                PlexUtilConfigService.add_plexutil_config(plexutil_config_entity)
                return PlexutilConfigEntityMapper.get_dto(
                        PlexUtilConfigService.get_plexutil_config()
                )


from plexutil.exception.entity_not_found_error import EntityNotFoundError
from plexutil.model.plexutil_config_entity import PlexUtilConfigEntity
from plexutil.static import Static


class PlexUtilConfigService(Static):
    @staticmethod
    def get_id() -> int:
        if PlexUtilConfigEntity.select().exists():
            return 1
        raise EntityNotFoundError(PlexUtilConfigEntity(id=1))

    @staticmethod
    def get_plexutil_config() -> PlexUtilConfigEntity:
        return PlexUtilConfigEntity.select().get()

    @staticmethod
    def add_plexutil_config(plexutil_config_entity: PlexUtilConfigEntity) -> None:
        # plexutil_config_entity.save(force_insert=True)
        plexutil_config_entity.save(force_insert=True)

from plexutil.enums.library_type import LibraryType
from plexutil.model.plexutil_config_entity import PlexUtilConfigEntity
from plexutil.model.plexutil_library_config import PlexUtilLibraryConfigEntity
from plexutil.static import Static


class PlexUtilLibraryConfigService(Static):
    @staticmethod
    def get_id() -> int:
        return 0

    @staticmethod
    def get_plexutil_library_config(
        library_type: LibraryType, library_name: str
    ) -> PlexUtilConfigEntity:
        return (
            PlexUtilLibraryConfigEntity.select()
            .where(
                (PlexUtilLibraryConfigEntity.name == library_type)
                & (PlexUtilLibraryConfigEntity.library_type == library_name)
            )
            .get()
        )

    @staticmethod
    def add_plexutil_library_config(
        plexutil_config_entity: PlexUtilConfigEntity,
    ) -> None:
        plexutil_config_entity.save(force_insert=True)
